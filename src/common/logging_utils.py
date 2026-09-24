"""Structured JSON logging utility with strict PII scrubbing.

Follows the hard rule:
Never log resume text or PII (emails, phone numbers, auth secrets).
Produces parseable JSON logs for observability and auditability.
"""

from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import re
from typing import Any, Dict, List, Optional

# Context variable for tracing requests across functions and threads
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

# Patterns to sanitize accidental PII in log text
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")

DEFAULT_SENSITIVE_KEYS = {
    "password",
    "token",
    "jwt_secret",
    "secret",
    "authorization",
    "resume_text",
    "raw_text",
    "email",
    "phone",
    "address",
}


def sanitize_value(key: str, value: Any, sensitive_keys: set[str]) -> Any:
    """Recursively scrub sensitive keys and regex patterns from values."""
    if key.lower() in sensitive_keys:
        return "[REDACTED]"

    if isinstance(value, str):
        cleaned = EMAIL_REGEX.sub("[EMAIL]", value)
        cleaned = PHONE_REGEX.sub("[PHONE]", cleaned)
        return cleaned

    if isinstance(value, dict):
        return {
            k: sanitize_value(k, v, sensitive_keys)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [sanitize_value(key, v, sensitive_keys) for v in value]

    return value


class JSONFormatter(logging.Formatter):
    """Custom logging formatter outputting clean, standardized JSON lines."""

    def __init__(self, sensitive_keys: Optional[List[str]] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.sensitive_keys = DEFAULT_SENSITIVE_KEYS.union(set(sensitive_keys or []))

    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Inject active request ID if set in context
        req_id = request_id_ctx.get()
        if req_id:
            log_payload["request_id"] = req_id

        # Attach extra properties passed to logger
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            for k, v in record.extra.items():
                if k not in log_payload:
                    log_payload[k] = v

        # Include exception trace if present
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        # Sanitize entire payload before emitting JSON
        sanitized = {
            k: sanitize_value(k, v, self.sensitive_keys)
            for k, v in log_payload.items()
        }

        return json.dumps(sanitized, default=str)


def setup_logging(level: str = "INFO") -> None:
    """Initialize structured logging across the application."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())

    # Avoid duplicate handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            handler.setFormatter(JSONFormatter())


def get_logger(name: str) -> logging.Logger:
    """Helper to retrieve a named logger configured for JSON output."""
    return logging.getLogger(name)
