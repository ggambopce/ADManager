# app/core/session.py
import uuid
from fastapi import Request, Response, HTTPException, status, Depends
from redis.asyncio import Redis

from app.core.config import settings
from app.core.redis_client import get_redis

# 쿠키 이름은 설정값을 그대로 사용
SESSION_COOKIE_NAME = settings.session_cookie_name
# Redis 키 prefix는 이 모듈에서 고정으로 관리
SESSION_PREFIX = "admin_session:"


def _session_key(session_id: str) -> str:
    return f"{SESSION_PREFIX}{session_id}"


async def create_admin_session(
    login_id: str,
    response: Response,
    redis: Redis,
) -> str:
    """
    로그인 성공 후 세션을 생성하고 쿠키를 세팅한다.
    """
    session_id = uuid.uuid4().hex
    key = _session_key(session_id)

    # Redis Hash 구조로 세션 저장
    await redis.hset(key, mapping={"loginId": login_id})
    # TTL = settings.session_expire_seconds
    await redis.expire(key, settings.session_expire_seconds)

    # 쿠키 세팅
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False,  # 운영에서 https 쓰면 True로 변경
        path="/",
        max_age=settings.session_expire_seconds,
    )

    return session_id


async def delete_admin_session(
    request: Request,
    response: Response,
    redis: Redis,
) -> None:
    """
    로그아웃 시 세션 삭제 + 쿠키 제거.
    """
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        await redis.delete(_session_key(session_id))

    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


async def get_current_admin(
    request: Request,
    redis: Redis = Depends(get_redis),
) -> dict:
    """
    현재 admin 세션 정보 조회. 없으면 401.
    """
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED",
        )

    key = _session_key(session_id)
    data = await redis.hgetall(key)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED",
        )

    # data: {"loginId": "..."} 형태 (redis가 str dict 반환)
    return data
