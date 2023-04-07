from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import timedelta
from ..database import models, schemas
from ..libraries import auth

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_HOURS = 24

async def create_member(db: Session, member: schemas.MemberCreate):
    # 아이디가 중복되는 계정이 있는지 확인
    stmt = select(models.Members.member_id).filter(models.Members.member_id == member.member_id)
    result = db.execute(stmt)

    list = result.fetchall()
    if len(list) > 0:
        raise Exception("아이디가 이미 사용 중입니다")

    # 패스워드 해싱 처리
    password_hash = auth.get_password_hash(member.member_pw)

    # DB 저장
    db_member = models.Members(**member.dict(exclude={"member_pw"}), member_pw=password_hash)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)

    return db_member

async def login_proc(db: Session, member_id: str, member_pw: str):
    # 해당 아이디가 있는지 찾는다/
    stmt = select(models.Members).filter(models.Members.member_id == member_id, models.Members.is_deleted == 'F')
    result = db.execute(stmt)

    db_member = result.fetchone()
    if db_member is None:
        raise Exception("해당하는 아이디를 찾을 수 없습니다")

    if auth.verify_password(member_pw, db_member.Members.member_pw) == False:
        raise Exception("패스워드가 일치하지 않습니다.")

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

async def member_modify(db: Session, member: schemas.MemberModify, payload: schemas.JWTPayload):
    # 회원이 존재하는 아이디인지 확인
    db_member = db.query(models.Members).filter_by(member_no = payload['member_no'], is_deleted = 'F').first()

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

    db.commit()
    return db_member

async def member_delete(db: Session, payload: schemas.JWTPayload):
    # 회원이 존재하는 아이디인지 확인
    db_member = db.query(models.Members).filter_by(member_no = payload['member_no'], is_deleted = 'F').first()

    if db_member is None:
        raise Exception("해당하는 회원 정보를 찾을 수 없습니다.")

    setattr(db_member, 'is_deleted', 'T')
    setattr(db_member, 'del_dt', func.now())

    db.commit()
    return db_member
