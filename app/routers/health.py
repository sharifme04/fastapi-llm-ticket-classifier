"""Health check endpoint.

Returns application status including DB and Redis connectivity.
Required for Railway/Fly.io deployment health probes.
"""

import logging

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.redis_client import get_redis

logger = logging.getLogger("ticket_classifier")
router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", response_model=dict)
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> dict:
    """Health check endpoint.

    Verifies connectivity to PostgreSQL and Redis.
    Returns status, version, and individual service health.

    Returns:
        JSON with status, version, db status, and redis status.
    """
    health = {
        "status": "ok",
        "version": settings.app_version,
        "service": settings.app_name,
        "db": "disconnected",
        "redis": "disconnected",
    }

    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        health["db"] = "connected"
    except Exception as e:
        logger.error("Database health check failed: %s", str(e))
        health["status"] = "degraded"
        health["db"] = f"error: {str(e)[:100]}"

    # Check Redis
    try:
        await redis.ping()
        health["redis"] = "connected"
    except Exception as e:
        logger.error("Redis health check failed: %s", str(e))
        health["status"] = "degraded"
        health["redis"] = f"error: {str(e)[:100]}"

    return health
