# # import sys
# # import os

# # # add backend/ to sys.path
# # sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# # # tests/conftest.py
# # import pytest
# # from unittest.mock import AsyncMock, patch

# # @pytest.fixture(autouse=True)
# # def mock_redis_client():
# #     with patch("app.core.rate_limiter.redis_client", new_callable=AsyncMock) as mock_redis:
# #         # You can define default return values if needed
# #         mock_redis.incr.return_value = 1
# #         yield mock_redis


# # # tests/conftest.py
# # from unittest.mock import AsyncMock, patch
# # import pytest

# # @pytest.fixture(autouse=True)
# # def mock_redis():
# #     with patch("redis.asyncio.Redis", new_callable=AsyncMock) as mock_redis:
# #         instance = mock_redis.return_value
# #         instance.incr.return_value = 1
# #         yield instance


# # # tests/conftest.py
# # import pytest
# # from unittest.mock import AsyncMock, patch

# # # Async fixture to mock Redis client globally for all tests
# # @pytest.fixture(autouse=True)
# # async def mock_redis():
# #     # Patch the Redis client used in your code
# #     with patch("redis.asyncio.Redis", new_callable=AsyncMock) as mock_redis_cls:
# #         instance = mock_redis_cls.return_value
# #         # Mock methods you use
# #         instance.incr.return_value = 1
# #         instance.get.return_value = b"1"  # if you use get
# #         yield instance


# # tests/conftest.py
# # import pytest_asyncio
# # from httpx import AsyncClient
# # from app.main import app  # Make sure PYTHONPATH includes backend/

# # @pytest_asyncio.fixture(scope="module")
# # async def async_client():
# #     """
# #     Provides an AsyncClient instance for testing FastAPI endpoints.
# #     """
# #     async with AsyncClient(app=app, base_url="http://test") as client:
# #         yield client


# # import asyncio
# # import pytest
# # import pytest_asyncio
# # from httpx import AsyncClient
# # from app.main import app  # should work if PYTHONPATH is set

# # # Provide a session-scoped event loop
# # @pytest.fixture(scope="session")
# # def event_loop():
# #     loop = asyncio.get_event_loop_policy().new_event_loop()
# #     yield loop
# #     loop.close()

# # # Async client fixture (function-scoped)
# # @pytest_asyncio.fixture
# # async def async_client():
# #     async with AsyncClient(app=app, base_url="http://test") as client:
# #         yield client



# # import pytest
# import pytest
# from fastapi.testclient import TestClient
# import sys
# import os

# # Ensure 'app' module is discoverable
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from app.main import app

# # Sync TestClient fixture
# @pytest.fixture(scope="function")
# def test_client():
#     """Create a synchronous test client for FastAPI app."""
#     with TestClient(app) as client:
#         yield client

# # Async wrapper fixture (for @pytest.mark.asyncio tests)
# @pytest.fixture(scope="function")
# async def async_client(test_client):
#     """Async wrapper for sync TestClient."""
#     yield test_client


# tests/conftest.py
# tests/conftest.py
# tests/conftest.py
# tests/conftest.py
# tests/conftest.py
# import sys
# import os
# import pytest_asyncio
# from httpx import AsyncClient

# # Ensure 'app' package is discoverable
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from app.main import app  # FastAPI app

# @pytest_asyncio.fixture
# async def async_client():
#     """
#     Provides an AsyncClient instance for testing FastAPI endpoints.
#     """
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client


# tests/conftest.py
# import sys
# import os
# import pytest
# import pytest_asyncio
# from httpx import AsyncClient
# from fastapi import FastAPI

# # Make sure the app package is discoverable
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from app.main import app  # import your FastAPI app instance

# @pytest_asyncio.fixture
# async def async_client():
#     """
#     Provides an AsyncClient instance for testing FastAPI endpoints.
#     """
#     # Use 'app' argument (httpx>=0.24) and 'lifespan' context automatically
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client

# Correct import
# tests/conftest.py
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.main import app

# Fake Redis client for async usage
class FakeRedis:
    async def incr(self, key):
        return 1  # always 1 to avoid rate limit
    async def expire(self, key, seconds):
        return True
    async def ttl(self, key):
        return 0

@pytest_asyncio.fixture
async def async_client():
    # Patch rate_limit to be a no-op decorator
    with patch("app.core.rate_limiter.rate_limit", lambda *args, **kwargs: (lambda f: f)):
        # Patch get_redis_client to return FakeRedis
        with patch("app.core.redis.get_redis_client", AsyncMock(return_value=FakeRedis())):
            async with AsyncClient(app=app, base_url="http://test") as client:
                yield client