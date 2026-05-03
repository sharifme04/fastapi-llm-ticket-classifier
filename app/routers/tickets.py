"""Ticket API endpoints.

Handles ticket creation, retrieval, classification triggering,
suggestion streaming (SSE), and feedback collection.
"""

import json
import logging
from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.database import get_db
from app.models.ticket import Priority, Ticket
from app.redis_client import get_redis
from app.schemas.ticket import TicketCreate, TicketFeedback, TicketResponse
from app.services.classifier import classify_ticket
from app.services.suggester import generate_suggestion_stream

logger = logging.getLogger("ticket_classifier")
router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> TicketResponse:
    """Create a new support ticket and trigger automatic classification.

    Accepts ticket details, validates with Pydantic, stores in PostgreSQL,
    and immediately classifies via Claude (with Redis caching).

    Args:
        ticket_data: Validated ticket creation payload.
        db: Async database session.
        redis: Redis client for caching.

    Returns:
        Created ticket with classification details.
    """
    # Validate priority
    priority_value = ticket_data.priority or "medium"
    try:
        priority = Priority(priority_value.lower())
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid priority: {priority_value}. Must be one of: low, medium, high, critical",
        )

    # Create ticket in DB
    ticket = Ticket(
        subject=ticket_data.subject,
        description=ticket_data.description,
        priority=priority,
    )
    db.add(ticket)
    await db.flush()  # Get the ticket ID without committing

    logger.info(
        "Ticket created",
        extra={"ticket_id": ticket.id, "subject": ticket.subject[:50]},
    )

    # Trigger classification
    try:
        classification = await classify_ticket(
            subject=ticket.subject,
            description=ticket.description,
            ticket_id=ticket.id,
            db=db,
            redis=redis,
        )
        logger.info(
            "Ticket classified",
            extra={
                "ticket_id": ticket.id,
                "category": classification.category,
                "confidence": classification.confidence,
                "cache_hit": classification.cache_hit,
            },
        )
    except Exception as e:
        # Classification failure shouldn't block ticket creation
        logger.warning(
            "Classification failed, ticket saved without classification",
            extra={"ticket_id": ticket.id, "error": str(e)},
        )

    # Refresh to get relationships loaded
    await db.refresh(ticket)

    return _ticket_to_response(ticket)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Get a single ticket by ID with its classification.

    Args:
        ticket_id: The ticket ID.
        db: Async database session.

    Returns:
        Ticket details with classification if available.

    Raises:
        HTTPException 404: If ticket not found.
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")

    return _ticket_to_response(ticket)


@router.get("/{ticket_id}/suggest")
async def suggest_response(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
) -> EventSourceResponse:
    """Stream a suggested response for a ticket via Server-Sent Events.

    Uses Claude's streaming API to generate a response suggestion
    in real-time, sent chunk-by-chunk to the client.

    Args:
        ticket_id: The ticket ID.
        db: Async database session.

    Returns:
        SSE stream of suggestion text chunks.

    Raises:
        HTTPException 404: If ticket not found.
        HTTPException 400: If ticket not yet classified.
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")

    if ticket.classification is None:
        raise HTTPException(
            status_code=400,
            detail="Ticket must be classified before generating a suggestion",
        )

    category = ticket.classification.category

    async def event_generator() -> AsyncGenerator[dict, None]:
        """Generate SSE events from Claude's streaming response."""
        try:
            async for chunk in generate_suggestion_stream(
                subject=ticket.subject,
                description=ticket.description,
                category=category,
            ):
                yield {"event": "chunk", "data": json.dumps({"text": chunk})}

            yield {"event": "done", "data": json.dumps({"status": "complete"})}

        except Exception as e:
            logger.error("Suggestion stream error: %s", str(e))
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())


@router.post("/{ticket_id}/feedback", status_code=200)
async def submit_feedback(
    ticket_id: int,
    feedback: TicketFeedback,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Submit feedback on a ticket's suggested response.

    Used for future evaluation tracking — stores whether the
    suggestion was helpful and any user comments.

    Args:
        ticket_id: The ticket ID.
        feedback: Feedback payload (helpful: bool, comment: Optional[str]).
        db: Async database session.

    Returns:
        Confirmation message.

    Raises:
        HTTPException 404: If ticket not found.
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")

    logger.info(
        "Feedback received",
        extra={
            "ticket_id": ticket_id,
            "helpful": feedback.helpful,
            "comment": feedback.comment,
        },
    )

    # TODO: Store feedback in a dedicated feedback table for eval tracking
    return {
        "message": "Feedback received",
        "ticket_id": ticket_id,
        "helpful": feedback.helpful,
    }


def _ticket_to_response(ticket: Ticket) -> TicketResponse:
    """Convert a Ticket model to a TicketResponse schema.

    Handles the nested classification relationship.

    Args:
        ticket: SQLAlchemy Ticket instance.

    Returns:
        Pydantic TicketResponse.
    """
    classification_detail = None
    if ticket.classification:
        from app.schemas.ticket import ClassificationDetail
        classification_detail = ClassificationDetail(
            category=ticket.classification.category,
            confidence=ticket.classification.confidence,
            reasoning=ticket.classification.reasoning,
            cache_hit=ticket.classification.cache_hit,
            created_at=ticket.classification.created_at,
        )

    return TicketResponse(
        id=ticket.id,
        subject=ticket.subject,
        description=ticket.description,
        priority=ticket.priority.value if isinstance(ticket.priority, Priority) else ticket.priority,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        classification=classification_detail,
    )
