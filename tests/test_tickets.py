"""Tests for ticket creation and retrieval endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import create_mock_anthropic_response


@pytest.mark.asyncio
async def test_create_ticket_success(client: AsyncClient):
    """Test creating a ticket with valid data triggers classification."""
    mock_response = create_mock_anthropic_response()

    with patch("app.services.classifier.anthropic.AsyncAnthropic") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        response = await client.post(
            "/tickets",
            json={
                "subject": "Cannot login to my account",
                "description": "I've been trying to login for 2 hours. I keep getting an invalid credentials error even though I reset my password.",
                "priority": "high",
            },
        )

    assert response.status_code == 201
    data = response.json()

    assert data["subject"] == "Cannot login to my account"
    assert data["priority"] == "high"
    assert data["id"] is not None
    assert data["classification"] is not None
    assert data["classification"]["category"] == "Bug"
    assert data["classification"]["confidence"] == 0.92


@pytest.mark.asyncio
async def test_create_ticket_default_priority(client: AsyncClient):
    """Test that tickets default to medium priority."""
    mock_response = create_mock_anthropic_response()

    with patch("app.services.classifier.anthropic.AsyncAnthropic") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        response = await client.post(
            "/tickets",
            json={
                "subject": "How do I export data?",
                "description": "I need to export my data to a CSV file but cannot find the option in the settings.",
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == "medium"


@pytest.mark.asyncio
async def test_create_ticket_validation_error(client: AsyncClient):
    """Test that invalid ticket data returns 422."""
    response = await client.post(
        "/tickets",
        json={
            "subject": "ab",  # Too short (min_length=3)
            "description": "short",  # Too short (min_length=10)
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_ticket_invalid_priority(client: AsyncClient):
    """Test that invalid priority returns 422."""
    response = await client.post(
        "/tickets",
        json={
            "subject": "Valid subject line",
            "description": "This is a valid description with enough characters.",
            "priority": "super_ultra_critical",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_ticket_not_found(client: AsyncClient):
    """Test that requesting a non-existent ticket returns 404."""
    response = await client.get("/tickets/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_ticket_success(client: AsyncClient):
    """Test retrieving a previously created ticket."""
    mock_response = create_mock_anthropic_response()

    with patch("app.services.classifier.anthropic.AsyncAnthropic") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        create_resp = await client.post(
            "/tickets",
            json={
                "subject": "Billing question about my plan",
                "description": "I was charged twice for the same subscription month. Please investigate.",
                "priority": "high",
            },
        )

    ticket_id = create_resp.json()["id"]
    response = await client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ticket_id
    assert data["subject"] == "Billing question about my plan"


@pytest.mark.asyncio
async def test_submit_feedback(client: AsyncClient):
    """Test submitting feedback on a ticket."""
    mock_response = create_mock_anthropic_response()

    with patch("app.services.classifier.anthropic.AsyncAnthropic") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        create_resp = await client.post(
            "/tickets",
            json={
                "subject": "Feature request for dark mode",
                "description": "Would love to have a dark mode option in the dashboard for late night work.",
            },
        )

    ticket_id = create_resp.json()["id"]
    response = await client.post(
        f"/tickets/{ticket_id}/feedback",
        json={"helpful": True, "comment": "Great suggestion!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["helpful"] is True
    assert data["ticket_id"] == ticket_id
