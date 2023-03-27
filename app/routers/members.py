from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from starlette.responses import Response
from starlette.status import HTTP_201_CREATED, HTTP_202_ACCEPTED
from typing import Optional
from ..database.connection import get_db
from ..database import schemas

router = APIRouter(
    prefix="/members",
    tags=["member"],
    responses={
        404: {"description": "Not Found"},
    }
)

# 회원 가입
@router.post("/create", description="회원 가입", response_class=Response)
async def create(
    member: schemas.Member,
    db: Session = Depends(get_db)
):
    return Response(status_code=HTTP_201_CREATED)

# 회원 정보 수정
@router.put("/modify", description="회원 정보 수정")
async def modify(
    member_no: int = Body(title="사용자 번호"),
    member_pw: Optional[str] = Body(title="사용자 패스워드"),
    member_name: Optional[str] = Body(title="사용자 이름"),
    member_email: Optional[str] = Body(title="사용자 이메일"),
    db: Session = Depends(get_db)
):
    return Response(HTTP_202_ACCEPTED)

# 로그인
@router.post("/login", description="로그인", response_model=schemas.LoginResponse)
async def login(
    member_id: str = Body(title="사용자 아이디"),
    member_pw: str = Body(title="사용자 패스워드"),
    db: Session = Depends(get_db)
):
    pass

# 회원탈퇴
@router.post("/unsubscribing", description="회원탈퇴", response_class=Response)
async def unsubscribing(
    member_no: int = Body(title="삭제할 사용자의 번호"),
    db: Session = Depends(get_db)
):
    return Response(status_code=HTTP_202_ACCEPTED)
