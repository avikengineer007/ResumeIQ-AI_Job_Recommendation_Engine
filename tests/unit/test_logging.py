"""Unit tests for structured JSON logging and PII scrubbing."""

import json
import logging

from src.common.logging_utils import (
    JSONFormatter,
    get_logger,
    request_id_ctx,
    sanitize_value,
)


def test_json_formatter_structure():
    """Verify that JSONFormatter emits valid JSON with standard metadata."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message content",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test_logger"
    assert parsed["message"] == "Test message content"
    assert "timestamp" in parsed


def test_request_id_injection():
    """Verify request_id is automatically appended when set in context."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="api_logger",
        level=logging.INFO,
        pathname="api.py",
        lineno=25,
        msg="Handling search query",
        args=(),
        exc_info=None,
    )

    token = request_id_ctx.set("req-uuid-12345")
    try:
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        assert parsed.get("request_id") == "req-uuid-12345"
    finally:
        request_id_ctx.reset(token)


def test_pii_redaction_in_logs():
    """Ensure sensitive attributes and contact data are sanitized."""
    sensitive_keys = {"password", "token", "resume_text", "email"}

    # Sensitive key redaction
    assert sanitize_value("password", "supersecret123", sensitive_keys) == "[REDACTED]"
    assert (
        sanitize_value("resume_text", "John Doe, Python Engineer", sensitive_keys)
        == "[REDACTED]"
    )

    # Pattern redaction in arbitrary text
    text_with_pii = "Candidate contact: john.doe@example.com or +1 (555) 123-4567"
    sanitized_text = sanitize_value("message", text_with_pii, sensitive_keys)
    assert "john.doe@example.com" not in sanitized_text
    assert "[EMAIL]" in sanitized_text
    assert "[PHONE]" in sanitized_text


def test_get_logger_instance():
    """Verify logger instantiation helper."""
    logger = get_logger("my_test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "my_test_module"
