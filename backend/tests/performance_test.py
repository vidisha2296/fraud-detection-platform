# tests/performance_test.py
import asyncio
import httpx
import time
import numpy as np

BASE_URL = "http://127.0.0.1:8000"
CUSTOMER_ID = "cust_test_1"
CONCURRENT_REQUESTS = 100
TOTAL_REQUESTS = 1000

latencies = []

async def fetch_transactions(client: httpx.AsyncClient):
    start = time.perf_counter()
    response = await client.get(f"{BASE_URL}/transactions/customer/{CUSTOMER_ID}")
    end = time.perf_counter()
    latency_ms = (end - start) * 1000
    latencies.append(latency_ms)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")

async def run_test():
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = []
        for _ in range(TOTAL_REQUESTS):
            task = asyncio.create_task(fetch_transactions(client))
            tasks.append(task)

            # Limit concurrency
            if len(tasks) >= CONCURRENT_REQUESTS:
                await asyncio.gather(*tasks)
                tasks = []

        # Await remaining tasks
        if tasks:
            await asyncio.gather(*tasks)

    # Compute stats
    latencies_array = np.array(latencies)
    print(f"Total requests: {len(latencies_array)}")
    print(f"Mean latency: {latencies_array.mean():.2f} ms")
    print(f"Median latency: {np.median(latencies_array):.2f} ms")
    print(f"P95 latency: {np.percentile(latencies_array, 95):.2f} ms")
    print(f"Max latency: {latencies_array.max():.2f} ms")

if __name__ == "__main__":
    asyncio.run(run_test())
