from sqlalchemy import (
    Column,
    VARCHAR,
    DATETIME,
    DATE,
    CHAR,
    PrimaryKeyConstraint,
    UniqueConstraint,
    ForeignKeyConstraint,
)
from sqlalchemy.dialects.mysql import (
    TINYINT,
    SMALLINT,
    INTEGER,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()
class Members(Base):
    __tablename__ = "tb_members"

    member_no = Column(SMALLINT(unsigned=True), nullable=False, autoincrement=True, comment="멤버번호")
    member_id = Column(VARCHAR(length=30), nullable=False, comment="사용자 아이디")
    member_pw = Column(VARCHAR(length=128), nullable=False, comment="사용자 패스워드")
    member_name = Column(VARCHAR(length=20), nullable=False, comment="사용자 이름")
    member_email = Column(VARCHAR(length=50), nullable=False, comment="이메일 주소")
    reg_dt = Column(DATETIME(timezone=False), nullable=False, server_default=func.now(), comment="생성일시")
    upd_dt = Column(DATETIME(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")
    is_deleted = Column(CHAR(length=1), default="F", server_default="F", nullable=False, comment="삭제여부(T|F)")
    del_dt = Column(DATETIME(timezone=False), nullable=True, comment="삭제일시")

    __table_args__ = (
        PrimaryKeyConstraint(member_no, name="pk_members"),
        UniqueConstraint(member_id, name="ixn_members__member_id"),
        {
            "comment": "사용자 정보"
        }
    )

class Category(Base):
    __tablename__ = "tb_category"

    category_no = Column(INTEGER(unsigned=True), nullable=False, autoincrement=True, comment="카테고리 번호")
    member_no = Column(SMALLINT(unsigned=True), nullable=True, comment="카테고리 생성자 번호(기본 카테고리일 경우 null)")
    category_name = Column(VARCHAR(length=50), nullable=False, comment="카테고리 이름")
    has_children = Column(CHAR(length=1), nullable=False, default="F", comment="자식을 가지고 있는지 여부(T|F)")
    parent_no = Column(INTEGER(unsigned=True), nullable=True, comment="부모 카테고리 번호")
    class_name = Column(VARCHAR(length=30), nullable=True, comment="아이콘 클래스")
    is_system = Column(CHAR(length=1), default="F", comment="시스템 기본 카테고리")
    reg_dt = Column(DATETIME(timezone=False), nullable=False, server_default=func.now(), comment="생성일시")
    upd_dt = Column(DATETIME(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")
    is_deleted = Column(CHAR(length=1), default="F", server_default="F", nullable=False, comment="삭제여부(T|F)")
    del_dt = Column(DATETIME(timezone=False), nullable=True, comment="삭제일시")

    __table_args__ = (
        PrimaryKeyConstraint(category_no, name="pk_category"),
        ForeignKeyConstraint(
            ["member_no"],
            ["tb_members.member_no"],
            name="fk_category__member_no",
            onupdate="NO ACTION",
            ondelete="NO ACTION",
        ),
        {
            "comment": "카테고리 정보"
        }
    )


class AccountLog(Base):
    __tablename__ = "tb_account_log"

    account_log_no = Column(INTEGER(unsigned=True), nullable=False, autoincrement=True, comment="내역번호")
    member_no = Column(SMALLINT(unsigned=True), nullable=False, comment="사용자번호")
    std_date = Column(DATE, nullable=False, comment="날짜")
    opponent_name = Column(VARCHAR(length=150), nullable=False, comment="메인거래처")
    reg_dt = Column(DATETIME(timezone=False), nullable=False, server_default=func.now(), comment="생성일시")
    upd_dt = Column(DATETIME(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")
    is_deleted = Column(CHAR(length=1), default="F", server_default="F", nullable=False, comment="삭제여부(T|F)")
    del_dt = Column(DATETIME(timezone=False), nullable=True, comment="삭제일시")

    __table_args__ = (
        PrimaryKeyConstraint(account_log_no, name="pk_account_log"),
        ForeignKeyConstraint(
            ["member_no"],
            ["tb_members.member_no"],
            name="fk_account_log__member_no",
            onupdate="NO ACTION",
            ondelete="NO ACTION",
        ),
        {
            "comment": "가계부 메인 내역"
        }
    )

class LogDefault(Base):
    __tablename__ = "tb_log_detail"

    log_detail_no = Column(INTEGER(unsigned=True), nullable=False, autoincrement=True, comment="사용내역 상세 번호")
    account_log_no = Column(INTEGER(unsigned=True), nullable=False, comment="내역번호")
    detail_contents = Column(VARCHAR(length=300), nullable=False, comment="상세내역정보")
    amounts = Column(INTEGER(unsigned=True), nullable=False, comment="금액")
    io_type = Column(CHAR(length=1), nullable=False, comment="수입/지출 구분(I: 수입, O: 지출)")
    category_no = Column(INTEGER(unsigned=True), nullable=True, comment="카테고리 번호")
    important = Column(TINYINT(unsigned=True), nullable=False, default=1, comment="중요도(지출일 경우만)")
    is_fixed_cost = Column(CHAR(length=1), nullable=False, default="F", comment="고정비여부(지출일 경우만, T|F)")
    reg_dt = Column(DATETIME(timezone=False), nullable=False, server_default=func.now(), comment="생성일시")
    upd_dt = Column(DATETIME(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now(), comment="수정일시")
    is_deleted = Column(CHAR(length=1), default="F", server_default="F", nullable=False, comment="삭제여부(T|F)")
    del_dt = Column(DATETIME(timezone=False), nullable=True, comment="삭제일시")

    __table_args__ = (
        PrimaryKeyConstraint(log_detail_no, name="pk_log_detail"),
        ForeignKeyConstraint(
            ["account_log_no"],
            ["tb_account_log.account_log_no"],
            name="fk_log_detail__account_log_no",
            onupdate="NO ACTION",
            ondelete="NO ACTION",
        ),
        ForeignKeyConstraint(
            ["category_no"],
            ["tb_category.category_no"],
            name="fk_log_detail__category_no",
            onupdate="NO ACTION",
            ondelete="NO ACTION",
        ),
        {
            "comment": "가계부 상세 내역"
        }
    )

#with engine.connect() as conn:
#    Base.metadata.create_all(conn)
