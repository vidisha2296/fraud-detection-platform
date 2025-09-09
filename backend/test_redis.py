import asyncio
from app.core.redis import get_redis_client

async def test():
    r = await get_redis_client()
    await r.set("foo", "bar")
    value = await r.get("foo")
    print(value)

asyncio.run(test())
