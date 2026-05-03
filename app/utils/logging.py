"""Structured JSON logging configuration.

Uses python-json-logger to emit JSON logs with request_id, duration_ms, and level.
Never use print() — always use the configured logger.
"""

import logging
import sys
import uuid
from contextvars import ContextVar

from pythonjsonlogger import jsonlogger

# Context variable for request-scoped request_id
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that injects request_id from context."""

    def add_fields(
        self,
        log_record: dict,
        record: logging.LogRecord,
        message_dict: dict,
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["level"] = record.levelname.upper()
        log_record["logger"] = record.name
        log_record["timestamp"] = self.formatTime(record)

        # Inject request_id from context variable
        rid = request_id_ctx.get("")
        if rid:
            log_record["request_id"] = rid


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured JSON logging for the application.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Configured root logger.
    """
    logger = logging.getLogger("ticket_classifier")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    logger.handlers.clear()

    # JSON handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())[:8]


# Module-level logger
logger = setup_logging()
