"""Tests for the health check endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test that /health returns ok status with DB and Redis info."""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["db"] == "connected"
    assert data["redis"] == "connected"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test that root / returns service info."""
    response = await client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "service" in data
    assert "version" in data
    assert data["docs"] == "/docs"
