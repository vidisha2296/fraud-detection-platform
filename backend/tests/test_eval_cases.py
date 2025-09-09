# # import json
# # import os
# # import pytest
# # from httpx import AsyncClient
# # from fastapi import FastAPI
# # from app.api.fraud_router import router

# # # -------------------------
# # # Setup FastAPI app
# # # -------------------------
# # app = FastAPI()
# # app.include_router(router)

# # # -------------------------
# # # Load eval cases
# # # -------------------------
# # eval_file_path = os.path.join(
# #     os.path.dirname(__file__), "../fixtures/evals/eval_cases.json"
# # )
# # with open(eval_file_path, "r") as f:
# #     eval_cases = json.load(f)

# # # -------------------------
# # # Async test runner
# # # -------------------------
# # @pytest.mark.asyncio
# # async def test_eval_cases():
# #     async with AsyncClient(app=app, base_url="http://test") as client:
# #         for case in eval_cases:
# #             customer_id = case["customerId"]
# #             transaction = case["transaction"]
# #             expected = case["expected_action"]

# #             # Call assess endpoint
# #             response = await client.post("/assess", json=transaction)
# #             assert response.status_code == 200, f"Failed case: {case['name']}"
# #             result = response.json()

# #             # Determine actual action
# #             actual_action = None
# #             if "action" in result.get("action", {}):
# #                 actual_action = result["action"]["action"]
# #             elif result.get("status") == "success":
# #                 actual_action = result["action"]["action"]
# #             else:
# #                 actual_action = result.get("partial_results", {}).get("final_action", {}).get("action")

# #             # Compare expected vs actual
# #             assert actual_action == expected["action"], (
# #                 f"Case '{case['name']}' failed. "
# #                 f"Expected: {expected['action']}, Got: {actual_action}"
# #             )

# #             # Optional: check reason/fallback/redaction
# #             if "reason" in expected:
# #                 reason_in_result = (
# #                     result.get("action", {}).get("reason")
# #                     or result.get("partial_results", {}).get("reason")
# #                 )
# #                 assert reason_in_result and expected["reason"] in reason_in_result, (
# #                     f"Case '{case['name']}' reason mismatch. "
# #                     f"Expected to include: {expected['reason']}, Got: {reason_in_result}"
# #                 )

# #     print(f"✅ All {len(eval_cases)} eval cases passed successfully.")

# import json
# import os
# import pytest

# # Load eval cases from fixtures
# eval_file_path = os.path.join(
#     os.path.dirname(__file__), "../fixtures/evals/eval_cases.json"
# )
# with open(eval_file_path, "r") as f:
#     eval_cases = json.load(f)

# @pytest.mark.asyncio
# async def test_eval_cases(async_client):
#     client = async_client  # already a TestClient instance

#     for case in eval_cases:
#         transaction = case["transaction"]
#         expected = case["expected_action"]

#         response = client.post("/assess", json=transaction)
#         assert response.status_code == 200, f"Failed case: {case['name']}"
#         result = response.json()

#         # Determine actual action from response
#         actual_action = None
#         if "action" in result.get("action", {}):
#             actual_action = result["action"]["action"]
#         elif result.get("status") == "success":
#             actual_action = result["action"]["action"]
#         else:
#             actual_action = result.get("partial_results", {}).get("final_action", {}).get("action")

#         assert actual_action == expected["action"], (
#             f"Case '{case['name']}' failed. "
#             f"Expected: {expected['action']}, Got: {actual_action}"
#         )

#         if "reason" in expected:
#             reason_in_result = (
#                 result.get("action", {}).get("reason")
#                 or result.get("partial_results", {}).get("reason")
#             )
#             assert reason_in_result and expected["reason"] in reason_in_result, (
#                 f"Case '{case['name']}' reason mismatch. "
#                 f"Expected to include: {expected['reason']}, Got: {reason_in_result}"
#             )

#     print(f"✅ All {len(eval_cases)} eval cases passed successfully.")















# # # tests/test_eval_cases.py
# # import pytest
# # from httpx import AsyncClient
# # from app.main import app  # replace with the path to your FastAPI app

# # # Example eval_cases list for demonstration
# # eval_cases = [
# #     {
# #         "transaction": {"id": 1, "amount": 100},
# #         "expected_action": {"action": "allow"}
# #     },
# #     {
# #         "transaction": {"id": 2, "amount": 1000},
# #         "expected_action": {"action": "review"}
# #     },
# # ]

# # @pytest.mark.asyncio
# # async def test_eval_cases():
# #     async with AsyncClient(app=app, base_url="http://test") as client:
# #         for case in eval_cases:
# #             transaction = case["transaction"]
# #             expected = case["expected_action"]
# #             response = await client.post("/fraud/assess", json=transaction)
# #             assert response.json() == expected



# # import pytest
# # import pytest_asyncio

# # # Sample eval cases
# # eval_cases = [
# #     {
# #         "transaction": {
# #             "id": "txn_test_1",
# #             "customerId": "cust_017",
# #             "amount": 100,
# #             "merchant": "Test Store",
# #             "mcc": "5411",
# #             "deviceId": "dev_45"
# #         },
# #         "expected_action": "approve"
# #     },
# #     {
# #         "transaction": {
# #             "id": "txn_test_2", 
# #             "customerId": "cust_017",
# #             "amount": 10000,
# #             "merchant": "ATM Withdrawal",
# #             "mcc": "6011",
# #             "deviceId": "dev_unknown"
# #         },
# #         "expected_action": "review"
# #     }
# # ]

# # @pytest.mark.asyncio
# # async def test_eval_cases(async_client):
# #     """Test evaluation cases for fraud detection"""
# #     for i, case in enumerate(eval_cases):
# #         transaction = case["transaction"]
# #         expected_action = case["expected_action"]

# #         # Test the fraud assessment endpoint
# #         response = await async_client.post("/fraud/assess", json=transaction)

# #         # Assert status code
# #         assert response.status_code == 200, f"Case {i}: Got {response.status_code} instead of 200. Response: {response.text}"

# #         # Parse response
# #         data = response.json()
        
# #         # Check if assessment was successful
# #         if data["status"] == "success":
# #             assert "action" in data, f"Case {i}: Response missing action field"
# #             action_data = data["action"]
# #             assert action_data["action"] == expected_action, f"Case {i}: Expected {expected_action}, got {action_data['action']}"
# #         else:
# #             # If assessment failed, we might still want to check error handling
# #             pytest.skip(f"Case {i}: Assessment failed with error: {data.get('error', 'Unknown error')}")



# tests/test_eval_cases.py
import pytest
from app.core import rate_limiter

class FakeRedis:
    def __init__(self):
        self.store = {}

    async def incr(self, key):
        self.store[key] = self.store.get(key, 0) + 1
        return self.store[key]

    async def expire(self, key, ttl):
        pass  # No-op for tests

    async def ttl(self, key):
        return 60  # Mock 60 seconds remaining

# Create a single shared FakeRedis instance
fake_redis_instance = FakeRedis()

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """
    Patches get_redis_client to return the shared FakeRedis instance asynchronously.
    """
    async def fake_get_redis_client():
        return fake_redis_instance

    monkeypatch.setattr(rate_limiter, "get_redis_client", fake_get_redis_client)

@pytest.mark.asyncio
async def test_fraud_assessment_rate_limit():
    from app.core.rate_limiter import rate_limit

    call_count = 0

    @rate_limit(max_requests=2, window_seconds=60)
    async def dummy_func(request=None):
        nonlocal call_count
        call_count += 1
        return "ok"

    class DummyRequest:
        client = type("Client", (), {"host": "127.0.0.1"})()
        url = type("URL", (), {"path": "/test"})()

    # First two calls succeed
    assert await dummy_func(request=DummyRequest()) == "ok"
    assert await dummy_func(request=DummyRequest()) == "ok"

    # Third call should raise 429
    with pytest.raises(Exception) as exc:
        await dummy_func(request=DummyRequest())
    assert "Rate limit exceeded" in str(exc.value)
