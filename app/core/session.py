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
    관리자 로그인 성공 후 세션을 생성하고, 브라우저에 세션 쿠키를 심는 함수.

    [동작 개요]
    1. 서버에서 무작위 session_id(UUID hex)를 생성한다.
    2. Redis에 "admin_session:{session_id}" 라는 키로 세션 정보를 저장한다.
       - Hash 구조로 {"loginId": <관리자 ID>} 형태로 저장.
       - TTL은 settings.session_expire_seconds 로 설정한다.
    3. 응답 헤더에 Set-Cookie 를 추가해서 브라우저에 session_id 를 내려준다.
       - 쿠키 이름: SESSION_COOKIE_NAME (예: "admin_session")
       - 쿠키 값: session_id
       - HttpOnly, SameSite=Lax 등의 보안 옵션을 함께 적용한다.

    이후 클라이언트는 매 요청마다 이 쿠키를 자동으로 보내고,
    서버는 쿠키에 있는 session_id를 기준으로 Redis에서 세션을 조회한다.
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
        httponly=True,        # JS에서 접근 불가 → XSS에 의한 탈취 위험 줄이기
        samesite="lax",       # CSRF에 대한 기본적인 보호 (필요 시 "strict" 나 "none" 으로 조정)
        secure=False,         # HTTPS 환경(prod)에서는 True 로 변경하는 것을 권장
        path="/",             # 전체 경로에서 쿠키를 전송하도록 설정
        max_age=settings.session_expire_seconds,  # 브라우저 쿠키 만료 시간
    )

    return session_id


async def delete_admin_session(
    request: Request,
    response: Response,
    redis: Redis,
) -> None:
    """
    로그아웃 시 세션 삭제 + 쿠키 제거를 담당하는 함수.

    [동작 개요]
    1. 요청 쿠키에서 session_id를 읽어온다.
    2. Redis에서 "admin_session:{session_id}" 키를 삭제한다.
    3. 응답에 delete_cookie 를 호출해서 브라우저 쿠키도 제거한다.
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
    현재 요청의 관리자 세션 정보를 조회하는 Depends 함수.
    [동작 개요]
    1. 요청 쿠키에서 session_id 를 읽는다.
       - 없으면 401 UNAUTHORIZED.
    2. Redis에서 "admin_session:{session_id}" 키를 조회한다.
       - 세션 정보가 없거나 TTL로 만료된 경우 401 UNAUTHORIZED.
    3. 세션 Hash에서 loginId 등 필요한 값을 반환한다.
    이 함수는 FastAPI Depends 로 주입하여,
    관리자 전용 API에서 인증/인가 미들웨어 역할처럼 사용할 수 있다.
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
