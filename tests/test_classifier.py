"""Tests for the classifier service logic."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.classification import TicketClassification
from app.services.cost_tracker import calculate_cost
from tests.conftest import create_mock_anthropic_response


class TestTicketClassification:
    """Test the Pydantic TicketClassification schema validation."""

    def test_valid_classification(self):
        """Test valid classification data parses correctly."""
        data = {
            "category": "Bug",
            "confidence": 0.95,
            "reasoning": "The ticket describes a software crash.",
        }
        classification = TicketClassification(**data)
        assert classification.category == "Bug"
        assert classification.confidence == 0.95

    def test_confidence_bounds(self):
        """Test that confidence must be between 0 and 1."""
        with pytest.raises(ValueError):
            TicketClassification(
                category="Bug",
                confidence=1.5,  # Out of bounds
                reasoning="Test",
            )

        with pytest.raises(ValueError):
            TicketClassification(
                category="Bug",
                confidence=-0.1,  # Out of bounds
                reasoning="Test",
            )

    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValueError):
            TicketClassification(category="Bug")  # Missing confidence and reasoning


class TestCostCalculation:
    """Test the cost calculation logic."""

    def test_zero_tokens(self):
        """Test cost with zero tokens."""
        cost = calculate_cost(0, 0)
        assert cost == 0.0

    def test_known_cost(self):
        """Test cost calculation with known values.

        With default pricing:
        - Input: $3.00 per 1M tokens → 1000 tokens = $0.003
        - Output: $15.00 per 1M tokens → 500 tokens = $0.0075
        - Total: $0.0105
        """
        cost = calculate_cost(1000, 500)
        assert cost == 0.0105

    def test_large_token_count(self):
        """Test cost with larger realistic token counts."""
        # 10K input + 2K output
        cost = calculate_cost(10_000, 2_000)
        # Input: 10000/1M * 3.00 = 0.03
        # Output: 2000/1M * 15.00 = 0.03
        # Total: 0.06
        assert cost == 0.06


class TestClassificationParsing:
    """Test parsing of Claude's classification responses."""

    def test_parse_valid_json(self):
        """Test parsing a well-formed JSON response."""
        raw = '{"category": "Feature Request", "confidence": 0.88, "reasoning": "User is asking for a new capability."}'
        parsed = json.loads(raw)
        classification = TicketClassification(**parsed)
        assert classification.category == "Feature Request"
        assert classification.confidence == 0.88

    def test_parse_invalid_json(self):
        """Test that invalid JSON raises an error."""
        raw = "This is not JSON at all"
        with pytest.raises(json.JSONDecodeError):
            json.loads(raw)

    def test_parse_missing_fields(self):
        """Test that JSON missing required fields raises validation error."""
        raw = '{"category": "Bug"}'
        parsed = json.loads(raw)
        with pytest.raises(ValueError):
            TicketClassification(**parsed)
