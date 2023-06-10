from fastapi import APIRouter, Depends, Body, Query
from typing import List, Optional, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from ..database import models, schemas
from ..database.connection import get_db
from ..services import account_service
from ..libraries.auth import decode_access_token
from starlette.responses import Response, JSONResponse
from datetime import datetime

router = APIRouter(
    prefix="/account",
    tags=["account"],
    dependencies=[Depends(decode_access_token)],
    responses={
        404: {"description": "Not Found"},
    }
)

# 지출입 기록 생성
@router.post("/create", description="수입/지출 항목 생성", response_class=Response, responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def create(
    user_info: schemas.JWTPayload = Depends(decode_access_token),
    account_log: schemas.AccountUpsert =  Body(
        title="항목생성",
        example={
            "std_date": "2023-05-01",
            "opponent_name": "이마트",
            "detail_list": [
                {
                    "detail_contents": "우유",
                    "amounts": 5500,
                    "io_type": "O",
                    "category_no": None,
                    "important": 4,
                    "is_fixed_cost": "F"
                },
                {
                    "detail_contents": "딸기",
                    "amounts": 15000,
                    "io_type": "O",
                    "category_no": None,
                    "important": 4,
                    "is_fixed_cost": "F"
                },
            ]
        }
    ),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await account_service.create_account(db, user_info['member_no'], account_log)

        return Response(status_code=HTTP_201_CREATED)
    except Exception as e:
        return JSONResponse(content={"detail": e.args[0]}, status_code=HTTP_400_BAD_REQUEST)

# 지출입 기록 삭제
@router.delete('/{account_no}', description="지출입 기록 삭제", response_class=Response, responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def delete(
    user_info: schemas.JWTPayload = Depends(decode_access_token),
    account_no: int = Query(title="지출입 번호"),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await account_service.delete_account(db, user_info['member_no'], account_no)

        return Response(status_code=HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"detail": e.args[0]}, status_code=HTTP_400_BAD_REQUEST)
