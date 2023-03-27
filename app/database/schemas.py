from pydantic import BaseModel, Field

class Member(BaseModel):
    member_id: str = Field(title="사용자 아이디", max_length=30)
    member_pw: str = Field(title="사용자 패스워드")
    member_name: str = Field(title="사용자 이름", max_length=20)
    member_email: str = Field(title="사용자 이메일", max_length=50)

    class Config:
        orm_mode = True

class LoginResponse(BaseModel):
    member_no: int = Field(title="사용자 번호")
    memeber_id: str = Field(title="사용자 아이디")
    member_name: str = Field(title="사용자 이름")
    member_email: str = Field(title="사용자 이메일")
    access_token: str = Field(title="Access Token")
    refresh_totke: str = Field(title="Refresh Token")
