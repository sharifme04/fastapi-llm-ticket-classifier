"""Cost tracking service.

Logs API token usage, calculates costs, aggregates daily totals,
and alerts when daily cost exceeds the configured threshold.
"""

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.api_cost import ApiCost
from app.schemas.classification import CostInfo
from app.utils.exceptions import CostLimitExceededError

logger = logging.getLogger("ticket_classifier")
settings = get_settings()


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate the USD cost for a single API call.

    Uses configurable pricing from settings (not hardcoded).
    Prices are per 1 million tokens.

    Args:
        input_tokens: Number of input tokens used.
        output_tokens: Number of output tokens generated.

    Returns:
        Cost in USD.
    """
    input_cost = (input_tokens / 1_000_000) * settings.anthropic_input_price_per_mtok
    output_cost = (output_tokens / 1_000_000) * settings.anthropic_output_price_per_mtok
    return round(input_cost + output_cost, 6)


async def log_api_cost(
    db: AsyncSession,
    input_tokens: int,
    output_tokens: int,
    cache_hit: bool = False,
) -> CostInfo:
    """Log token usage and cost for a single API call.

    Updates the daily aggregate in api_costs table.
    Returns cost info including daily running total.

    Args:
        db: Async database session.
        input_tokens: Input tokens consumed.
        output_tokens: Output tokens generated.
        cache_hit: Whether this was served from Redis cache.

    Returns:
        CostInfo with per-request and daily cost information.
    """
    cost = calculate_cost(input_tokens, output_tokens) if not cache_hit else 0.0
    today = date.today()

    # Get or create today's cost record
    result = await db.execute(
        select(ApiCost).where(ApiCost.date == today)
    )
    daily_record = result.scalar_one_or_none()

    if daily_record is None:
        daily_record = ApiCost(
            date=today,
            total_cost=cost,
            request_count=1,
            cache_hit_count=1 if cache_hit else 0,
        )
        db.add(daily_record)
    else:
        daily_record.total_cost += cost
        daily_record.request_count += 1
        if cache_hit:
            daily_record.cache_hit_count += 1

    await db.flush()

    logger.info(
        "API cost logged",
        extra={
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "cache_hit": cache_hit,
            "daily_total": daily_record.total_cost,
        },
    )

    return CostInfo(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        daily_total=daily_record.total_cost,
        budget_remaining=settings.daily_cost_limit - daily_record.total_cost,
    )


async def check_cost_limit(db: AsyncSession) -> None:
    """Check if the daily cost limit has been exceeded.

    Raises CostLimitExceededError if the limit is breached.

    Args:
        db: Async database session.

    Raises:
        CostLimitExceededError: If daily cost exceeds configured limit.
    """
    today = date.today()
    result = await db.execute(
        select(ApiCost).where(ApiCost.date == today)
    )
    daily_record = result.scalar_one_or_none()

    if daily_record and daily_record.total_cost >= settings.daily_cost_limit:
        logger.warning(
            "Daily cost limit exceeded!",
            extra={
                "daily_total": daily_record.total_cost,
                "limit": settings.daily_cost_limit,
            },
        )
        raise CostLimitExceededError(
            daily_total=daily_record.total_cost,
            limit=settings.daily_cost_limit,
        )


async def get_monthly_cost_summary(db: AsyncSession) -> dict:
    """Get cost summary for the current month.

    Args:
        db: Async database session.

    Returns:
        Dictionary with total_cost, total_requests, total_cache_hits,
        cache_hit_rate, and avg_cost_per_request.
    """
    today = date.today()
    first_of_month = today.replace(day=1)

    result = await db.execute(
        select(ApiCost).where(ApiCost.date >= first_of_month)
    )
    records = result.scalars().all()

    if not records:
        return {
            "total_cost": 0.0,
            "total_requests": 0,
            "total_cache_hits": 0,
            "cache_hit_rate": 0.0,
            "avg_cost_per_request": 0.0,
        }

    total_cost = sum(r.total_cost for r in records)
    total_requests = sum(r.request_count for r in records)
    total_cache_hits = sum(r.cache_hit_count for r in records)
    cache_hit_rate = (total_cache_hits / total_requests * 100) if total_requests > 0 else 0.0
    avg_cost = total_cost / total_requests if total_requests > 0 else 0.0

    return {
        "total_cost": round(total_cost, 4),
        "total_requests": total_requests,
        "total_cache_hits": total_cache_hits,
        "cache_hit_rate": round(cache_hit_rate, 2),
        "avg_cost_per_request": round(avg_cost, 6),
    }
