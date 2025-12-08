# app/core/redis_client.py
from redis.asyncio import Redis
from app.core.config import settings


# 애플리케이션 전역에서 쓸 Redis 클라이언트 하나 생성
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
    """
    return redis_client
