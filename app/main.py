"""FastAPI application entry point.

Customer Support Ticket Classifier & Suggester.
Mounts routers, configures middleware (CORS, rate limiting, request logging),
and registers lifecycle events and exception handlers.
"""

import logging
import time
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.database import close_db, init_db
from app.redis_client import close_redis
from app.routers import analytics, health, tickets
from app.utils.exceptions import register_exception_handlers
from app.utils.logging import generate_request_id, logger, request_id_ctx

settings = get_settings()


# --- Rate Limiter ---
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])


# --- Lifespan (startup/shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: initialize DB tables on startup, clean up on shutdown."""
    logger.info("Starting application", extra={"version": settings.app_version})

    # Startup
    await init_db()
    logger.info("Database tables created/verified")

    yield

    # Shutdown
    await close_db()
    await close_redis()
    logger.info("Application shutdown complete")


# --- FastAPI App ---
app = FastAPI(
    title="Customer Support Ticket Classifier & Suggester",
    description=(
        "A production-ready FastAPI service that automatically classifies "
        "support tickets using Anthropic Claude, generates suggested responses "
        "via SSE streaming, and tracks API costs."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Middleware ---

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Request logging middleware (structured JSON with request_id and duration)
@app.middleware("http")
async def logging_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Log every request with request_id, method, path, status, and duration_ms."""
    rid = generate_request_id()
    request_id_ctx.set(rid)

    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    logger.info(
        "Request completed",
        extra={
            "request_id": rid,
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )

    # Add request_id to response headers for tracing
    response.headers["X-Request-ID"] = rid

    return response


# --- Exception Handlers ---
register_exception_handlers(app)

# --- Routers ---
app.include_router(health.router)
app.include_router(tickets.router)
app.include_router(analytics.router)


# --- Root ---
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint — welcome message and API info."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
