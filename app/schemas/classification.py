"""Pydantic schemas for classification data."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketClassification(BaseModel):
    """Schema for Claude's structured classification response.

    This is what we expect from the LLM — validated before storing.
    """

    category: str = Field(
        ...,
        description="Ticket category: Bug, Feature Request, Billing, General Inquiry, or Urgent",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Classification confidence score between 0 and 1",
    )
    reasoning: str = Field(
        ...,
        description="Brief explanation for the classification decision",
    )


class ClassificationResponse(BaseModel):
    """Full classification response including token usage and cost."""

    id: int
    ticket_id: int
    category: str
    confidence: float
    reasoning: str
    input_tokens: int
    output_tokens: int
    cost: float
    cache_hit: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CostInfo(BaseModel):
    """Token usage and cost information for a single API call."""

    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    daily_total: Optional[float] = None
    budget_remaining: Optional[float] = None
