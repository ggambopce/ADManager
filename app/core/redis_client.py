# app/core/redis_client.py
from redis.asyncio import Redis
from app.core.config import settings

# 애플리케이션 전역에서 사용할 Redis 클라이언트 하나를 생성한다.
# - 이 Redis는 주로 관리자 세션 정보를 저장하는 용도로 사용한다.
# - 세션 키 구조: "admin_session:{session_id}"
# - 값 구조: Hash (예: {"loginId": "admin@example.com"})
redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password or None,
    decode_responses=True,  # 문자열 응답 원하면
)

async def get_redis() -> Redis:
    """
    FastAPI Depends 에서 사용할 Redis 의존성.

    각 요청 핸들러에서 Redis를 직접 생성하지 않고,
    이 함수를 통해 동일한 전역 클라이언트를 주입받는 방식으로 사용한다.
    """
    return redis_client
