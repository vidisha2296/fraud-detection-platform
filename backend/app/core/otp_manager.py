# app/core/otp_manager.py
import random
from app.core.redis import get_redis_client

OTP_TTL = 300  # 5 minutes

class OTPManager:
    @staticmethod
    async def generate_otp(customer_id: str, action_id: str) -> str:
        otp = f"{random.randint(100000, 999999)}"
        redis_client = await get_redis_client()
        key = f"otp:{customer_id}:{action_id}"
        await redis_client.set(key, otp, ex=OTP_TTL)
        return otp

    @staticmethod
    async def verify_otp(customer_id: str, action_id: str, otp: str) -> bool:
        redis_client = await get_redis_client()
        key = f"otp:{customer_id}:{action_id}"
        stored_otp = await redis_client.get(key)
        if not stored_otp:
            return False
        if stored_otp.decode() == otp:
            await redis_client.delete(key)  # consume OTP
            return True
        return False
