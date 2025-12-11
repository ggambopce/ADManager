from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, func

from app.core.database import Base


class AdminUser(Base):
    """
    관리자 계정 테이블
    - 관리자 로그인에 사용되는 계정 정보를 저장한다.
    - 실제 인증(로그인) 시에는 login_id + password_hash 를 사용하고,
      인증에 성공하면 Redis 세션 + 브라우저 쿠키를 통해 상태를 유지한다.
    이 테이블 자체에는 세션 정보는 저장하지 않고
    순수하게 관리자 계정 정보만 보관한다.
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
