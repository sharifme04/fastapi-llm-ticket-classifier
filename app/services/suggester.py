"""Response suggestion service using Anthropic Claude with SSE streaming.

Generates suggested responses for classified support tickets.
Streams the response token-by-token via Server-Sent Events (SSE).
"""

import logging
from collections.abc import AsyncGenerator

import anthropic

from app.config import get_settings
from app.utils.exceptions import ClassificationError

logger = logging.getLogger("ticket_classifier")
settings = get_settings()

# Suggestion system prompt
SUGGESTION_SYSTEM_PROMPT = """You are a helpful, professional customer support agent. Based on the ticket category and description provided, craft a warm, empathetic initial response to the customer.

Guidelines:
1. Acknowledge the customer's issue in the first sentence.
2. Show empathy — use phrases like "I understand how frustrating this must be" where appropriate.
3. Provide a clear next step or action you're taking.
4. Keep the response 2-4 sentences long.
5. Be professional but friendly — not robotic.
6. If the issue is urgent, convey urgency and reassurance.
7. If it's a billing issue, be extra careful and reassuring about their account.
8. End with a question or next step so the customer knows what to expect.

Category-specific notes:
- Bug: Acknowledge the issue, mention you're investigating, ask for reproduction steps if not provided.
- Feature Request: Thank them for the suggestion, explain how feedback is reviewed.
- Billing: Reassure about account security, offer to investigate immediately.
- General Inquiry: Be helpful and direct, provide links/docs if possible.
- Urgent: Express urgency, mention escalation to priority team.
"""


async def generate_suggestion_stream(
    subject: str,
    description: str,
    category: str,
) -> AsyncGenerator[str, None]:
    """Stream a suggested response for a support ticket via SSE.

    Calls Claude's streaming API and yields each text chunk as it arrives.
    The caller wraps these in SSE events for the client.

    Args:
        subject: Ticket subject line.
        description: Ticket description text.
        category: Classification category (Bug, Feature Request, etc.).

    Yields:
        Text chunks from Claude's streaming response.

    Raises:
        ClassificationError: If the Claude API call fails.
    """
    user_message = (
        f"Ticket Category: {category}\n"
        f"Subject: {subject}\n"
        f"Description: {description}\n\n"
        "Please generate a suggested response for this support ticket."
    )

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        async with client.messages.stream(
            model=settings.anthropic_model,
            max_tokens=500,
            system=SUGGESTION_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message},
            ],
        ) as stream:
            async for text in stream.text_stream:
                yield text

        logger.info(
            "Suggestion stream completed",
            extra={"subject": subject[:50], "category": category},
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error during suggestion streaming: %s", str(e))
        raise ClassificationError(
            message=f"Failed to generate suggestion: {e.message}",
            detail={"api_error": str(e)},
        )
