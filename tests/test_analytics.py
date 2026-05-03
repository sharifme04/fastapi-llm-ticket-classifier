"""Tests for the analytics endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import create_mock_anthropic_response


@pytest.mark.asyncio
async def test_analytics_empty(client: AsyncClient):
    """Test analytics summary with no tickets returns zeros."""
    response = await client.get("/analytics/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["total_tickets"] == 0
    assert data["categories"] == []
    assert data["avg_classification_confidence"] == 0.0
    assert data["cost_summary"]["total_cost"] == 0.0


@pytest.mark.asyncio
async def test_analytics_with_tickets(client: AsyncClient):
    """Test analytics after creating some tickets."""
    mock_response = create_mock_anthropic_response()

    with patch("app.services.classifier.anthropic.AsyncAnthropic") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        # Create a few tickets
        for i in range(3):
            await client.post(
                "/tickets",
                json={
                    "subject": f"Test ticket number {i + 1}",
                    "description": f"This is test ticket description number {i + 1} with sufficient length.",
                    "priority": "medium",
                },
            )

    response = await client.get("/analytics/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["total_tickets"] == 3
    assert len(data["categories"]) >= 1
    assert data["avg_classification_confidence"] > 0
