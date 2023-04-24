from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from datetime import timedelta
from ..database import models, schemas
from ..libraries import auth

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_HOURS = 24

async def create_member(db: AsyncSession, member: schemas.MemberCreate):
    # 아이디가 중복되는 계정이 있는지 확인
    stmt = select(models.Members.member_id).filter(models.Members.member_id == member.member_id)
    result = await db.execute(stmt)

    list = result.fetchall()
    if len(list) > 0:
        raise Exception("아이디가 이미 사용 중입니다")

    # 패스워드 해싱 처리
    password_hash = auth.get_password_hash(member.member_pw)

    # DB 저장
    db_member = models.Members(**member.dict(exclude={"member_pw"}), member_pw=password_hash)
    db.add(db_member)
    await db.commit()
    await db.refresh(db_member)

    return db_member

# login 처리
async def login_proc(db: AsyncSession, member_id: str, member_pw: str):
    # 해당 아이디가 있는지 찾는다/
    stmt = select(models.Members).filter(models.Members.member_id == member_id, models.Members.is_deleted == 'F')
    result = await db.execute(stmt)

    db_member = result.fetchone()
    if db_member is None:
        raise Exception("해당하는 아이디를 찾을 수 없습니다")

    if auth.verify_password(member_pw, db_member.Members.member_pw) == False:
        raise Exception("패스워드가 일치하지 않습니다.")

    return make_login_response(db_member)


# refresh token 처리
async def member_refresh(db: AsyncSession, refresh_token: schemas.Refresh):
    # refresh token 검사
    try:
        payload = auth.decode_refresh_token(refresh_token.refresh_token)
    except Exception:
        raise Exception

    # 해당 회원이 있는지 검사
    stmt = select(models.Members).filter(models.Members.member_no == payload['member_no'], models.Members.is_deleted == 'F')
    result = await db.execute(stmt)

    db_member = result.fetchone()
    if db_member is None:
        raise Exception("해당하는 아이디를 찾을 수 없습니다")

    return make_login_response(db_member)


def make_login_response(db_member):
    data = {
        "member_no": db_member.Members.member_no,
        "member_id": db_member.Members.member_id,
        "member_name": db_member.Members.member_name,
        "member_email": db_member.Members.member_email
    }
    data["access_token"] = auth.create_access_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    data["refresh_token"] = auth.create_access_token({
        "member_no": data["member_no"],
        "member_id": data["member_id"]
    }, timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS))

    return data


async def member_modify(db: AsyncSession, member: schemas.MemberModify, payload: schemas.JWTPayload):
    # 회원이 존재하는 아이디인지 확인
    result = await db.execute(select(models.Members).filter_by(member_no = payload['member_no'], is_deleted = 'F'))
    db_member = result.scalars().first()

    if db_member is None:
        raise Exception("해당하는 회원 정보를 찾을 수 없습니다.")

    member_info =  member.dict()
    member = {k: v for k, v in member_info.items()}
    for key, value in member.items():
        if value is None:
            continue

        if key == 'member_pw':
            setattr(db_member, key, auth.get_password_hash(value))
        else:
            setattr(db_member, key, value)

    await db.commit()
    return db_member


async def member_delete(db: AsyncSession, payload: schemas.JWTPayload):
    # 회원이 존재하는 아이디인지 확인
    db_member = await db.query(models.Members).filter_by(member_no = payload['member_no'], is_deleted = 'F').first()

    if db_member is None:
        raise Exception("해당하는 회원 정보를 찾을 수 없습니다.")

    setattr(db_member, 'is_deleted', 'T')
    setattr(db_member, 'del_dt', func.now())

    await db.commit()
    return db_member
