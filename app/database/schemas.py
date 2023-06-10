from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import date

# 회원 가입에 대한 Request Schema
class MemberCreate(BaseModel):
    member_id: str = Field(title="사용자 아이디", max_length=30)
    member_pw: str = Field(title="사용자 패스워드")
    member_name: str = Field(title="사용자 이름", max_length=20)
    member_email: str = Field(title="사용자 이메일", max_length=50)

    class Config:
        orm_mode = True

# 회원 정보 수정에 대한 Request Schema
class MemberModify(BaseModel):
    member_pw: Optional[str] = Field(title="사용자 패스워드")
    member_name: Optional[str] = Field(title="사용자 이름", max_length=20)
    member_email: Optional[str] = Field(title="사용자 이메일", max_length=50)

    class Config:
        orm_mode = True

class CategoryUpsert(BaseModel):
    category_name: str = Field(title="카테고리 이름")
    parent_no: Optional[int] = Field(title="부모 카테고리 번호", default=None)
    class_name: Optional[str] = Field(title="아이콘 정보", default=None)
    inout_type: Literal['I', 'O'] = Field(title="수입/지출구분")

class CategoryInfo(CategoryUpsert):
    category_no: int = Field(title="카테고리 번호")
    member_no: Optional[int] = Field(title="소유자 회원 번호")
    sort_order: int = Field(title="정렬순서")

    class Config:
        orm_mode = True

class LogDetailUpsert(BaseModel):
    log_detail_no: Optional[int] = Field(title="사용재역번호")
    detail_contents: str = Field(title="상세내역정보")
    amounts: int = Field(title="금액")
    io_type: Literal["I", "O"] = Field(title="수입/지출 구분(I: 수입, O: 지출)")
    category_no: Optional[int] = Field(title="카테고리 번호")
    important: Optional[int] = Field(title="중요도")
    is_fixed_cost: Literal["T", "F"] = Field(title="고정비여부(T|F)")

class LogDetail(LogDetailUpsert):
    account_log_no: int = Field(title="내역번호")

    class Config:
        orm_mode = True

class AccountUpsert(BaseModel):
    std_date: date = Field(title="날짜")
    opponent_name: str = Field(title="메인거래처")
    detail_list: List[LogDetailUpsert] = Field(title="세부내역")

class AccountLog(AccountUpsert):
    account_log_no: int = Field(title="내역번호")
    member_no: int = Field(title="사용자번호")

    class Config:
        orm_mode = True

# JWT Decode에 얻어지는 정보에 대한 Schema
class JWTPayload(BaseModel):
    member_no: int = Field(title="사용자 번호")
    member_id: str = Field(title="사용자 아이디")
    member_name: str = Field(title="사용자 이름")
    member_email: str = Field(title="사용자 이메일")

# 로그인 성공시 Response로 전송되는 Schema
class LoginResponse(BaseModel):
    member_no: int = Field(title="사용자 번호")
    member_id: str = Field(title="사용자 아이디")
    member_name: str = Field(title="사용자 이름")
    member_email: str = Field(title="사용자 이메일")
    access_token: str = Field(title="Access Token")
    refresh_token: str = Field(title="Refresh Token")

class Message(BaseModel):
    message: str

# Refresh token을 위한 request 정의
class Refresh(BaseModel):
    refresh_token: str = Field(title="Refresh Token")
