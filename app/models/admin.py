from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, func

from app.core.database import Base


class AdminUser(Base):
    """
    관리자 계정 테이블
    - 로그인 ID, 비밀번호 해시, 생성일시만 관리
    """
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 로그인용 ID (이메일 형태든 그냥 아이디든 상관없음)
    login_id = Column(String(100), nullable=False, unique=True, index=True)
    # 비밀번호 해시 (bcrypt 등으로 암호화된 값)
    password_hash = Column(String(255), nullable=False)

    # 생성 일시
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    # 수정 일시
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<AdminUser(id={self.id}, login_id={self.login_id})>"
