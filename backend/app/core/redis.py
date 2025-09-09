# app/core/redis.py
import redis.asyncio as redis
from app.core.config import settings

_redis_client = None

async def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url, decode_responses=True
        )
    return _redis_client
