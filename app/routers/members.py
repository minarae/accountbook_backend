from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from typing import Optional
from ..database.connection import get_db
from ..database import schemas
from ..services import members_service
from ..libraries import auth

router = APIRouter(
    prefix="/members",
    tags=["member"],
    responses={
        404: {"description": "Not Found"},
    }
)


# 회원 가입
@router.post("/create", description="회원 가입", response_class=Response, responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def create(
    member: schemas.MemberCreate = Body(
        title="회원정보",
        example={
            "member_id": "foo",
            "member_pw": "1234567890",
            "member_name": "홍길동",
            "member_email": "test@example.com",
        }
    ),
    db: Session = Depends(get_db)
):
    try:
        result = await members_service.create_member(db, member)

        return Response(status_code=HTTP_201_CREATED)
    except Exception as e:
        return JSONResponse(content={"detail": e.args[0]}, status_code=HTTP_400_BAD_REQUEST)


# 로그인
@router.post("/login", description="로그인", response_model=schemas.LoginResponse, responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def login(
    member_id: str = Body(title="사용자 아이디"),
    member_pw: str = Body(title="사용자 패스워드"),
    db: Session = Depends(get_db)
):
    try:
        result = await members_service.login_proc(db, member_id, member_pw)

        return result
    except Exception as e:
        return JSONResponse(content={"detail": e.args[0]}, status_code=HTTP_400_BAD_REQUEST)


# 회원 정보 수정
@router.put("/modify", description="회원 정보 수정", response_class=Response, responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def modify(
    payload: schemas.JWTPayload = Depends(auth.decode_access_token),
    member: schemas.MemberModify = Body(
        title="수정할 회원정보",
        example={
            "member_pw": "1234567890",
            "member_name": "홍길동",
            "member_email": "test@example.com",
        }
    ),
    db: Session = Depends(get_db)
):
    try:
        result = await members_service.member_modify(db, member, payload)

        return Response(status_code=HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"detail": e.args[0]}, status_code=HTTP_400_BAD_REQUEST)


#refresh token을 이용한 access token 재발급
@router.post("/refresh", description="token 갱신", response_model=schemas.LoginResponse, responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def refresh(
    refresh_token: schemas.Refresh,
    db: Session = Depends(get_db)
):
    try:
        result = await members_service.member_refresh(db, refresh_token)

        return result
    except Exception as e:
        return JSONResponse(content={"detail": e.args[0]}, status_code=HTTP_400_BAD_REQUEST)


# 회원탈퇴
@router.post("/unsubscribing", description="회원탈퇴", response_class=Response, responses={
    HTTP_400_BAD_REQUEST: {
        "model": schemas.Message
    }
})
async def unsubscribing(
    payload: schemas.JWTPayload = Depends(auth.decode_access_token),
    db: Session = Depends(get_db)
):
    print(payload)
    try:
        result = await members_service.member_delete(db, payload)

        return Response(status_code=HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"detail": e.args[0]}, status_code=HTTP_400_BAD_REQUEST)
