# core/rate_limiter.py
from fastapi import HTTPException, Request
from functools import wraps
from app.core.redis import get_redis_client

def rate_limit(max_requests: int, window_seconds: int, key: str | None = None):
    """
    Rate limiter decorator using Redis.
    :param max_requests: maximum allowed requests in the window
    :param window_seconds: time window in seconds
    :param key: optional custom key for rate limiting (default: client_ip:path)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if not request:
                raise HTTPException(status_code=500, detail="Request not found in kwargs")

            # Use custom key if provided, else client IP + path
            rate_key = key if key else f"rate:{request.client.host}:{request.url.path}"

            redis_client = await get_redis_client()

            # Increment counter atomically
            current = await redis_client.incr(rate_key)
            if current == 1:
                # Set TTL for first request
                await redis_client.expire(rate_key, window_seconds)

            if current > max_requests:
                ttl = await redis_client.ttl(rate_key)
                retry_after_sec = ttl if ttl > 0 else window_seconds
                retry_after_ms = retry_after_sec * 1000

                # Raise 429 with Retry-After header and retryAfterMs in JSON body
                raise HTTPException(
                    status_code=429,
                    detail={
                        "message": "Rate limit exceeded",
                        "retryAfterMs": retry_after_ms
                    },
                    headers={"Retry-After": str(retry_after_sec)}
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
