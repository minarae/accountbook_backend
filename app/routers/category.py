from fastapi import APIRouter, Depends, Body, Query
from typing import List, Optional, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from ..database import models, schemas
from ..database.connection import get_db
from ..services import category_service
from ..libraries.auth import decode_access_token
from starlette.responses import Response, JSONResponse

router = APIRouter(
    prefix="/category",
    tags=["category"],
    dependencies=[Depends(decode_access_token)],
    responses={
        404: {"description": "Not Found"},
    }
)

# 카테고리 리스트 조회
@router.get('/list', description="카테고리 리스트 조회", response_model=List[schemas.CategoryInfo], responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def get_list(
    user_info: schemas.JWTPayload = Depends(decode_access_token),
    inout_type: Literal['I', 'O'] = Query(title="수입/지출 구분"),
    parent_no: Optional[int] = Query(default=None, title="부모카테고리 이름"),
    db: AsyncSession = Depends(get_db)
):
    result = await category_service.get_category_list(db, user_info['member_no'], inout_type, parent_no)
    response = []
    for item in result:
        response.append(schemas.CategoryInfo.from_orm(item).dict())
    return response


# 카테고리 생성
@router.post("/create", description="카테고리 생성", response_class=Response, responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def create(
    user_info: schemas.JWTPayload = Depends(decode_access_token),
    category: schemas.CategoryUpsert = Body(
        title="카테고리 정보",
        example={
            "category_name": "테스트",
            "parent_no": None,
            "class_name": None,
            "inout_type": "O",
        }
    ),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await category_service.create_category(db, user_info['member_no'], category)

        return Response(status_code=HTTP_201_CREATED)
    except Exception as e:
        return JSONResponse(content={"detail": e.args[0]}, status_code=HTTP_400_BAD_REQUEST)

# 카테고리 항목 수정
@router.put("/modify/{category_no}", description="카테고리 정보 수정", response_class=Response, responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def modify(
    user_info: schemas.JWTPayload = Depends(decode_access_token),
    category_no: int = Query(title="카테고리번호"),
    category: schemas.CategoryUpsert = Body(
        title="카테고리 정보",
        example={
            "category_name": "테스트",
            "parent_no": None,
            "class_name": None,
            "inout_type": "O",
        }
    ),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await category_service.modify_category(db, user_info['member_no'], category_no, category)

        return Response(status_code=HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"detail": e.args[0]}, status_code=HTTP_400_BAD_REQUEST)

# 카테고리 삭제
@router.delete("/delete/{category_no}", description="카테고리 삭제", response_class=Response, responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def delete(
    user_info: schemas.JWTPayload = Depends(decode_access_token),
    category_no: int = Query(title="카테고리 번호"),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await category_service.delete_category(db, user_info['member_no'], category_no)

        return Response(status_code=HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"detail": e.args[0]}, status_code=HTTP_400_BAD_REQUEST)
