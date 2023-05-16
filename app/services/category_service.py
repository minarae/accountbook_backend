from typing import Optional, List, Literal
from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import schemas, models
import json
import asyncio

# 회원 가입시 기본 카테고리 구성 추가
async def insert_default_categories(
    db: AsyncSession,
    member_no: int,
):
    # 우선 카테고리 내용을 정의한 파일을 읽어들인다.
    with open("./categories.json", "r") as f:
        categories = json.load(f)

    # 메인 카테고리 리스트를 처리한다.
    for category in categories:
        new_category = {k: v for k, v in category.items() if k != 'children'}
        if len(category['children']) == 0:
            new_category['has_children'] = 'F'
        else:
            new_category['has_children'] = 'T'

        # 카테고리 정보를 DB에 저장한다.
        db_category = models.Category(**new_category, member_no=member_no)
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        insert_coros = []

        # 서브카테고리도 DB에 입력한다. 이 때 처리는 비동기로 한다.
        insert_coros = [db.execute(models.Category.__table__.insert().values(**{
                "member_no": member_no,
                "category_name": child,
                "has_children": "F",
                "inout_type": category["inout_type"],
                "parent_no": db_category.category_no,
                "sort_order": index + 1
            })) for index, child in enumerate(category['children'])]

        # 모든 데이터 추가 코루틴을 동시에 실행
        await asyncio.gather(*insert_coros)
        await db.commit()


# 카테고리 생성
async def create_category(
    db: AsyncSession,
    member_no: int,
    category: schemas.CategoryUpsert,
):
    db_category = models.Category(**category.dict(), member_no=member_no, has_children='F')
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)

    return db_category

# 카테고리 수정
async def modify_category(
    db: AsyncSession,
    member_no: int,
    category_no: int,
    category: schemas.CategoryUpsert,
):
    result = await db.execute(
        select(models.Category).filter(
            models.Category.category_no == category_no,
            models.Category.is_deleted == 'F',
        )
    )
    db_category = result.scalars().first()

    if db_category is None:
        raise Exception('카테고리 정보를 찾을 수 없습니다.')

    if db_category.member_no != member_no:
        raise Exception('카테고리 수정에 대한 권한이 없습니다')

    category_info =  category.dict()
    category = {k: v for k, v in category_info.items()}
    for key, value in category.items():
        if value is None:
            continue

        setattr(db_category, key, value)

    await db.commit()
    return db_category


# 카테고리 삭제
async def delete_category(
    db: AsyncSession,
    member_no: int,
    category_no: int,
):
    # 카테고리가 존재하는지 확인
    result = await db.execute(
        select(models.Category).filter(
            models.Category.category_no == category_no,
            models.Category.is_deleted == 'F',
        )
    )
    db_category = result.scalars().first()

    if db_category is None:
        raise Exception("카테고리 정보를 찾을 수 없습니다.")

    if db_category.member_no != member_no:
        raise Exception('카테고리 수정에 대한 권한이 없습니다')

    setattr(db_category, 'is_deleted', 'T')
    setattr(db_category, 'del_dt', func.now())

    await db.commit()
    return db_category

# 카테고리 리스트 조회
async def get_category_list(
    db: AsyncSession,
    member_no: int,
    inout_type: Literal['I', 'O'],
    parent_category_no: Optional[int]
) -> List[schemas.CategoryInfo]:
    stmt = select(models.Category).filter(
        models.Category.member_no == member_no,
        models.Category.inout_type == inout_type,
        models.Category.is_deleted == 'F'
    ).order_by(models.Category.sort_order.asc(), models.Category.category_no.asc())
    if parent_category_no is None:
        stmt = stmt.filter(models.Category.parent_no.is_(None))
    else:
        stmt = stmt.filter(models.Category.parent_no == parent_category_no)

    results = await db.execute(stmt)
    return results.scalars().all()
