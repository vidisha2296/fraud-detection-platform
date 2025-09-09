import asyncio
from httpx import AsyncClient
from app.main import app

async def run_test():
    async with AsyncClient(app=app, base_url="http://test") as client:
        print("Sending 5 requests quickly...")
        for i in range(1, 6):
            response = await client.get("/test")
            print(f"Request {i}: status {response.status_code}, body: {response.json()}")

if __name__ == "__main__":
    asyncio.run(run_test())
