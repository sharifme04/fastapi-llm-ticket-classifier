"""Pydantic schemas for ticket API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    """Request schema for creating a new support ticket."""

    subject: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Brief summary of the support issue",
        examples=["Cannot login to my account"],
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Detailed description of the issue",
        examples=["I've been trying to login for 2 hours. I keep getting an 'invalid credentials' error even though I reset my password."],
    )
    priority: Optional[str] = Field(
        default="medium",
        description="Ticket priority: low, medium, high, critical",
        examples=["high"],
    )


class ClassificationDetail(BaseModel):
    """Embedded classification info in ticket response."""

    category: str
    confidence: float
    reasoning: str
    cache_hit: bool
    created_at: datetime


class TicketResponse(BaseModel):
    """Response schema for a single ticket with classification."""

    id: int
    subject: str
    description: str
    priority: str
    created_at: datetime
    updated_at: datetime
    classification: Optional[ClassificationDetail] = None

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    """Response schema for listing multiple tickets."""

    tickets: list[TicketResponse]
    total: int
    page: int
    page_size: int


class TicketFeedback(BaseModel):
    """Request schema for submitting feedback on a suggestion."""

    helpful: bool = Field(..., description="Whether the suggestion was helpful")
    comment: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional feedback comment",
    )
