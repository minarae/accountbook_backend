from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import func
from ..database import schemas, models
from .category_service import get_all_category_nos_list

# 지출입내역 기록
async def create_account(
    db: AsyncSession,
    member_no: int,
    account_info: schemas.AccountUpsert,
):
    # category를 검사하기 위해서 먼저 데이터를 가지고 있는다.
    category_list = await get_all_category_nos_list(db, member_no)

    # 먼저 대표 정보를 저장하고 세부 내역을 루프로 돌면서 저장
    db_account_info = models.AccountLog(**account_info.dict(exclude={"detail_list"}), member_no=member_no)
    db.add(db_account_info)
    # 세션을 플러시하여 변경 사항을 데이터베이스에 반영합니다.
    await db.flush()
    await db.refresh(db_account_info)

    # 세부내역을 루프를 돌면서 저장
    for item in account_info.detail_list:
        if item.category_no is not None and item.category_no not in (category_list):
            raise Exception("사용할 수 없는 카테고리 번호")

        db_item = models.LogDefault(**item.dict(), account_log_no=db_account_info.account_log_no)
        db.add(db_item)

    await db.commit()
    await db.refresh(db_account_info)

    return db_account_info

# 지출입내역 수정
async def modify_account(
    db: AsyncSession,
    member_no: int,
    account_no: int,
    account_info: schemas.AccountUpsert,
):
    # 지출입 기록이 존재하는지 확인
    result = await db.execute(
        select(models.AccountLog).filter(
            models.AccountLog.account_log_no == account_no,
            models.AccountLog.is_deleted == 'F',
        )
    )
    db_account_info = result.scalars().first()

    if db_account_info is None:
        raise Exception('지출입 내역을 찾을 수 없습니다.')

    if db_account_info.member_no != member_no:
        raise Exception('지출입 내역을 찾을 수 없습니다.')

    # 지출입 기록 기본 정보 수정
    account_info_dict =  account_info.dict()
    account = {k: v for k, v in account_info_dict.items()}
    for key, value in account.items():
        if key == "detail_list" or value is None:
            continue

        setattr(db_account_info, key, value)

    # category를 검사하기 위해서 먼저 데이터를 가지고 있는다.
    category_list = await get_all_category_nos_list(db, member_no)

    # 상세정보 추가/수정
    log_detail_nos = []
    for item in account_info.detail_list:
        if item.category_no is not None and item.category_no not in (category_list):
            raise Exception("사용할 수 없는 카테고리 번호")

        if item.log_detail_no is None:
            # 사용내역 번호가 없으면 추가
            db_item = models.LogDefault(**item.dict(), account_log_no=account_no)
            db.add(db_item)
            await db.flush()
            await db.refresh(db_item)
            log_detail_nos.append(db_item.log_detail_no)
        else:
            # 사용내역 번호가 있으면 수정
            log_detail_nos.append(item.log_detail_no)

    await db.commit()
    return db_account_info

# 지출입내역 삭제
async def delete_account(
    db: AsyncSession,
    member_no: int,
    account_no: int,
):
    # 지출입 기록이 존재하는지 확인
    result = await db.execute(
        select(models.AccountLog).filter(
            models.AccountLog.account_log_no == account_no,
            models.AccountLog.is_deleted == 'F',
        )
    )
    db_account_info = result.scalars().first()

    if db_account_info is None:
        raise Exception('지출입 내역을 찾을 수 없습니다.')

    if db_account_info.member_no != member_no:
        raise Exception('지출입 내역을 찾을 수 없습니다.')

    setattr(db_account_info, 'is_deleted', 'T')
    setattr(db_account_info, 'del_dt', func.now())

    stmt = update(models.LogDefault).where(models.LogDefault.account_log_no == account_no).values(is_deleted = 'T', del_dt = func.now())
    await db.execute(stmt)
    # 쿼리가 실패나는 경우를 대비해서 commit은 마지막에 한 번만 호출
    await db.commit()
    return db_account_info
