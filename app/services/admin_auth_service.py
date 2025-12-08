# app/services/admin_auth_service.py

from typing import Dict

from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session
from redis.asyncio import Redis
import bcrypt

from app.models.admin import AdminUser
from app.core.session import create_admin_session


class AdminAuthService:
    """
    관리자 로그인/세션 관련 서비스.
    - 비밀번호 해시/검증
    - 관리자 계정 인증
    - 세션 생성 + 쿠키 세팅
    """

    @staticmethod
    def hash_password(plain: str) -> str:
        """
        평문 비밀번호를 bcrypt로 해시하여 문자열로 반환.
        """
        hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """
        평문 비밀번호와 해시 비밀번호를 비교.
        """
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

    @staticmethod
    def authenticate(db: Session, login_id: str, password: str) -> AdminUser:
        """
        DB에서 관리자 계정 조회 + 비밀번호 검증.
        실패 시 HTTPException 발생.
        """
        admin = (
            db.query(AdminUser)
            .filter(AdminUser.login_id == login_id)
            .first()
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="관리자 계정이 존재하지 않습니다.",
            )

        if not AdminAuthService.verify_password(password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호가 일치하지 않습니다.",
            )

        return admin

    @staticmethod
    async def login(
        db: Session,
        login_id: str,
        password: str,
        response: Response,
        redis: Redis,
    ) -> AdminUser:
        """
        로그인 전체 플로우:
        1) DB에서 관리자 검증
        2) Redis 세션 생성
        3) admin_session 쿠키 세팅
        """
        admin = AdminAuthService.authenticate(db, login_id, password)
        await create_admin_session(login_id=admin.login_id, response=response, redis=redis)
        return admin

    @staticmethod
    def get_admin_info_from_session(session_data: Dict[str, str]) -> Dict[str, str]:
        """
        Redis 세션 데이터에서 필요한 정보만 추출.
        """
        return {
            "loginId": session_data.get("loginId"),
        }
