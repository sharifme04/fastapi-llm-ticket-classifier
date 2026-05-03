"""Ticket classification service using Anthropic Claude.

Classifies support tickets into categories with confidence scores.
Uses Redis caching to skip API calls for identical tickets within 1 hour.
"""

import hashlib
import json
import logging

import anthropic
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.classification import Classification
from app.schemas.classification import TicketClassification
from app.services.cost_tracker import calculate_cost, check_cost_limit, log_api_cost
from app.utils.exceptions import ClassificationError

logger = logging.getLogger("ticket_classifier")
settings = get_settings()

# Classification system prompt
CLASSIFICATION_SYSTEM_PROMPT = """You are an expert customer support ticket classifier. Your job is to classify incoming support tickets into exactly one of these categories:

- **Bug**: Software defects, errors, crashes, broken functionality
- **Feature Request**: Requests for new features or improvements  
- **Billing**: Payment issues, subscription questions, refunds, pricing
- **General Inquiry**: General questions, how-to, documentation requests
- **Urgent**: Critical issues requiring immediate attention (data loss, security, service outage)

Analyze the ticket's subject and description carefully. Return your classification as a JSON object with these exact fields:

{
  "category": "Bug|Feature Request|Billing|General Inquiry|Urgent",
  "confidence": 0.0 to 1.0,
  "reasoning": "Brief explanation of why you chose this category"
}

Rules:
1. Always return valid JSON — no markdown, no code fences, just the JSON object.
2. Confidence should reflect how clearly the ticket fits the category.
3. If the ticket mentions security breaches, data loss, or complete service outage, classify as "Urgent" regardless of other signals.
4. Reasoning should be 1-2 sentences maximum.
"""

# Cache TTL: 1 hour
CACHE_TTL = 3600


def _cache_key(subject: str, description: str) -> str:
    """Generate a deterministic cache key from ticket content.

    Args:
        subject: Ticket subject.
        description: Ticket description.

    Returns:
        Redis cache key string.
    """
    content_hash = hashlib.sha256(f"{subject}:{description}".encode()).hexdigest()[:16]
    return f"classification:{content_hash}"


async def classify_ticket(
    subject: str,
    description: str,
    ticket_id: int,
    db: AsyncSession,
    redis: aioredis.Redis,
) -> Classification:
    """Classify a support ticket using Claude with Redis caching.

    Flow:
    1. Check Redis cache for identical ticket content
    2. If cache miss, check cost limit
    3. Call Claude API with classification system prompt
    4. Parse and validate structured JSON response
    5. Store classification in DB and cache in Redis
    6. Log token usage and cost

    Args:
        subject: Ticket subject line.
        description: Ticket description text.
        ticket_id: ID of the ticket to classify.
        db: Async database session.
        redis: Redis client for caching.

    Returns:
        Classification model instance (persisted to DB).

    Raises:
        ClassificationError: If Claude call fails or response is invalid.
        CostLimitExceededError: If daily cost limit is exceeded.
    """
    cache_key = _cache_key(subject, description)

    # Step 1: Check Redis cache
    cached = await redis.get(cache_key)
    if cached:
        logger.info("Cache hit for ticket classification", extra={"ticket_id": ticket_id})
        cached_data = json.loads(cached)
        classification = TicketClassification(**cached_data)

        db_classification = Classification(
            ticket_id=ticket_id,
            category=classification.category,
            confidence=classification.confidence,
            reasoning=classification.reasoning,
            input_tokens=0,
            output_tokens=0,
            cost=0.0,
            cache_hit=True,
        )
        db.add(db_classification)
        await db.flush()

        # Log cost (cache hit — no tokens used)
        await log_api_cost(db, input_tokens=0, output_tokens=0, cache_hit=True)

        return db_classification

    # Step 2: Check cost limit before making API call
    await check_cost_limit(db)

    # Step 3: Call Claude API
    try:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        user_message = f"Subject: {subject}\n\nDescription: {description}"

        response = await client.messages.create(
            model=settings.anthropic_model,
            max_tokens=300,
            system=CLASSIFICATION_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message},
            ],
        )

        # Extract response text
        response_text = response.content[0].text.strip()

        # Extract token usage
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        logger.info(
            "Claude classification response received",
            extra={
                "ticket_id": ticket_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error: %s", str(e), extra={"ticket_id": ticket_id})
        raise ClassificationError(
            message=f"Claude API call failed: {e.message}",
            detail={"ticket_id": ticket_id, "api_error": str(e)},
        )

    # Step 4: Parse and validate response
    try:
        parsed = json.loads(response_text)
        classification = TicketClassification(**parsed)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(
            "Failed to parse classification response",
            extra={"ticket_id": ticket_id, "raw_response": response_text, "error": str(e)},
        )
        raise ClassificationError(
            message="Failed to parse Claude's classification response",
            detail={"raw_response": response_text},
        )

    # Step 5: Calculate cost and store classification
    cost = calculate_cost(input_tokens, output_tokens)

    db_classification = Classification(
        ticket_id=ticket_id,
        category=classification.category,
        confidence=classification.confidence,
        reasoning=classification.reasoning,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        cache_hit=False,
    )
    db.add(db_classification)
    await db.flush()

    # Step 6: Cache the classification result
    await redis.set(
        cache_key,
        json.dumps(classification.model_dump()),
        ex=CACHE_TTL,
    )

    # Log cost
    await log_api_cost(db, input_tokens=input_tokens, output_tokens=output_tokens, cache_hit=False)

    logger.info(
        "Ticket classified successfully",
        extra={
            "ticket_id": ticket_id,
            "category": classification.category,
            "confidence": classification.confidence,
            "cost": cost,
        },
    )

    return db_classification
