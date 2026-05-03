"""Pydantic schemas for analytics responses."""

from pydantic import BaseModel, Field


class CategoryStat(BaseModel):
    """Statistics for a single ticket category."""

    category: str
    count: int
    avg_confidence: float = Field(..., description="Average classification confidence")
    total_cost: float = Field(..., description="Total LLM cost for this category")


class CostSummary(BaseModel):
    """Cost summary for the current month."""

    total_cost: float
    total_requests: int
    total_cache_hits: int
    cache_hit_rate: float = Field(..., description="Percentage of requests served from cache")
    avg_cost_per_request: float


class AnalyticsSummary(BaseModel):
    """Full analytics summary response."""

    total_tickets: int
    categories: list[CategoryStat]
    cost_summary: CostSummary
    avg_classification_confidence: float
