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
    관리자 로그인/세션 관련 비즈니스 로직을 모아 둔 서비스 클래스.
    역할:
    - 비밀번호 해시/검증 (bcrypt 사용)
    - 관리자 계정 인증 (DB 조회 + 비밀번호 비교)
    - 세션 생성 + 쿠키 세팅 (create_admin_session 호출)
    """
    @staticmethod
    def hash_password(plain: str) -> str:
        """
        평문 비밀번호를 bcrypt로 해시하여 문자열로 반환.

        관리자 계정을 미리 생성할 때(초기 데이터), 이 함수를 사용해서
        password_hash 컬럼에 저장한다.
        """
        hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """
        평문 비밀번호와 해시 비밀번호를 비교.

        - 로그인 시 클라이언트에서 넘어온 password(plain)를
          DB에 저장된 password_hash(hashed)와 비교한다.
        """
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

    @staticmethod
    def authenticate(db: Session, login_id: str, password: str) -> AdminUser:
        """
        관리자 계정 인증 로직.
        [동작]
        1) DB에서 login_id 로 AdminUser 를 조회.
        2) 계정이 없으면 400 에러(관리자 계정 없음).
        3) 비밀번호가 일치하지 않으면 400 에러(비밀번호 불일치).
        4) 모두 통과하면 AdminUser 엔티티를 반환한다.
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
        로그인 전체 플로우를 처리하는 메서드.
        [플로우]
        1) authenticate(...) 를 통해
           - 관리자 계정 존재 여부
           - 비밀번호 일치 여부를 검증한다.
        2) 인증에 성공하면 create_admin_session(...) 을 호출하여
           - Redis 에 세션을 생성하고
           - 응답에 admin_session 쿠키를 세팅한다.
        3) 최종적으로 AdminUser 엔티티를 반환한다.

        이 메서드는 실제 라우터(/admin/login)에서 호출되고,
        세션 + 쿠키 처리를 한 곳에서 관리한다는 점이 핵심이다.
        """
        admin = AdminAuthService.authenticate(db, login_id, password)
        await create_admin_session(login_id=admin.login_id, response=response, redis=redis)
        return admin

    @staticmethod
    def get_admin_info_from_session(session_data: Dict[str, str]) -> Dict[str, str]:
        """
        Redis 세션 데이터에서 필요한 정보만 추출.

        현재는 세션에 {"loginId": "..."} 만 저장하기 때문에
        해당 값만 꺼내서 반환한다.
        나중에 세션에 role, 권한 정보 등을 추가하면
        여기서 함께 꺼내서 반환하도록 확장할 수 있다.
        """
        return {
            "loginId": session_data.get("loginId"),
        }
