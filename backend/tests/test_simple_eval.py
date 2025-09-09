# # tests/test_simple_eval.py
# import pytest
# from unittest.mock import AsyncMock, patch
# from httpx import AsyncClient
# from httpx._transports.asgi import ASGITransport
# from app.main import app

# # Async client fixture
# @pytest.fixture
# async def async_client():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
#         yield client

# # Mock Redis globally
# @pytest.fixture(autouse=True)
# def mock_redis():
#     class FakeRedis:
#         async def incr(self, *args, **kwargs):
#             return 1

#     with patch("app.core.rate_limiter.get_redis_client", return_value=FakeRedis()):
#         yield

# @pytest.mark.asyncio
# async def test_fraud_assessment_simple(async_client):
#     transaction = {"customer_id": "cust_001", "amount": 100, "currency": "USD"}

#     # Mock Orchestrator.run
#     with patch(
#         "app.agents.orchestrator.Orchestrator.run",
#         new_callable=AsyncMock,
#         return_value={"success": True, "results": {"fraud": {"risk_score": 10}}}
#     ):
#         response = await async_client.post("/fraud/assess", json=transaction)

#     assert response.status_code == 200
#     data = response.json()
#     assert data["success"] is True
#     assert "fraud" in data["results"]


# @pytest.mark.asyncio
# async def test_fraud_assessment_high_risk(async_client):
#     transaction = {"customer_id": "cust_002", "amount": 10000, "currency": "USD"}

#     with patch(
#         "app.agents.orchestrator.Orchestrator.run",
#         new_callable=AsyncMock,
#         return_value={"success": True, "results": {"fraud": {"risk_score": 95}}}
#     ):
#         response = await async_client.post("/fraud/assess", json=transaction)

#     assert response.status_code == 200
#     data = response.json()
#     assert data["results"]["fraud"]["risk_score"] > 90



# tests/test_simple_eval.py
import pytest

@pytest.mark.asyncio
async def test_fraud_assessment_simple(async_client):
    transaction = {"amount": 100, "currency": "USD"}
    response = await async_client.post("/fraud/assess", json=transaction)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_fraud_assessment_high_risk(async_client):
    transaction = {"amount": 10000, "currency": "USD"}  # High-risk
    response = await async_client.post("/fraud/assess", json=transaction)
    assert response.status_code == 200




