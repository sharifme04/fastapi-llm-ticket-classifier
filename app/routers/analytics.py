"""Analytics endpoint.

Provides aggregated statistics: tickets by category,
average confidence, and cost summary for the current month.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import Float, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.classification import Classification
from app.models.ticket import Ticket
from app.schemas.analytics import AnalyticsSummary, CategoryStat, CostSummary
from app.services.cost_tracker import get_monthly_cost_summary

logger = logging.getLogger("ticket_classifier")
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
) -> AnalyticsSummary:
    """Get aggregated analytics summary.

    Returns:
    - Total tickets count
    - Tickets grouped by classification category with avg confidence and cost
    - Monthly cost summary (total, requests, cache hits, hit rate, avg cost)
    - Overall average classification confidence

    Args:
        db: Async database session.

    Returns:
        AnalyticsSummary with category stats and cost breakdown.
    """
    # Total tickets
    total_result = await db.execute(select(func.count(Ticket.id)))
    total_tickets = total_result.scalar() or 0

    # Category breakdown with aggregations
    category_query = (
        select(
            Classification.category.cast(String).label("category"),
            func.count(Classification.id).label("count"),
            func.avg(Classification.confidence).cast(Float).label("avg_confidence"),
            func.sum(Classification.cost).cast(Float).label("total_cost"),
        )
        .group_by(Classification.category)
        .order_by(func.count(Classification.id).desc())
    )
    category_result = await db.execute(category_query)
    category_rows = category_result.all()

    categories = [
        CategoryStat(
            category=row.category,
            count=row.count,
            avg_confidence=round(row.avg_confidence or 0.0, 3),
            total_cost=round(row.total_cost or 0.0, 4),
        )
        for row in category_rows
    ]

    # Overall average confidence
    avg_conf_result = await db.execute(
        select(func.avg(Classification.confidence).cast(Float))
    )
    avg_confidence = avg_conf_result.scalar() or 0.0

    # Monthly cost summary
    cost_summary_data = await get_monthly_cost_summary(db)
    cost_summary = CostSummary(**cost_summary_data)

    return AnalyticsSummary(
        total_tickets=total_tickets,
        categories=categories,
        cost_summary=cost_summary,
        avg_classification_confidence=round(avg_confidence, 3),
    )
