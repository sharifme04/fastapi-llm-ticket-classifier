"""Pytest fixtures for the ticket classifier tests.

Provides:
- Async test client (httpx.AsyncClient via FastAPI TestClient)
- In-memory SQLite database for isolated tests
- Mock Redis client
- Mock Anthropic API
"""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.redis_client import get_redis


# --- Async event loop ---
@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for all tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# --- Test Database (SQLite async) ---
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the DB dependency with test database."""
    async with test_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# --- Mock Redis ---
class FakeRedis:
    """In-memory fake Redis for testing."""

    def __init__(self):
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._store[key] = value

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        pass


@pytest_asyncio.fixture
async def fake_redis():
    """Provide a FakeRedis instance."""
    return FakeRedis()


async def override_get_redis() -> AsyncGenerator[FakeRedis, None]:
    """Override the Redis dependency with FakeRedis."""
    yield FakeRedis()


# --- Override dependencies ---
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_redis] = override_get_redis


# --- Async HTTP client ---
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# --- Mock Claude response ---
MOCK_CLASSIFICATION_RESPONSE = {
    "category": "Bug",
    "confidence": 0.92,
    "reasoning": "The ticket describes a software error preventing login.",
}


def create_mock_anthropic_response(
    text: str = '{"category": "Bug", "confidence": 0.92, "reasoning": "The ticket describes a software error preventing login."}',
    input_tokens: int = 150,
    output_tokens: int = 50,
):
    """Create a mock Anthropic API response."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=text)]
    mock_response.usage = MagicMock(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
    return mock_response
