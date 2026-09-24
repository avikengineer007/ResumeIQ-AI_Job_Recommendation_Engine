"""Unit tests for PII detection, typed placeholders, and zero-PII audit verification."""

from src.pii.anonymizer import PIIAnonymizer
from src.pii.pii_detector import PIIDetector


def test_pii_detection():
    """Verify detection of emails, phone numbers, and URLs."""
    text = (
        "Contact Jane Doe at jane.doe@example.com or reach out via +1 (555) 987-6543. "
        "Portfolio: https://github.com/janedoe and linkedin.com/in/janedoe"
    )
    detector = PIIDetector()
    spans = detector.detect(text)

    types = {s.entity_type for s in spans}
    assert "EMAIL" in types
    assert "PHONE" in types
    assert "URL" in types


def test_pii_anonymization_and_zero_pii_verification():
    """Verify typed placeholder replacement and post-anonymization zero-PII check."""
    raw_text = (
        "Candidate contact: test.candidate@domain.org, telephone 212-555-0199. "
        "Web link: https://myresume.dev"
    )
    anonymizer = PIIAnonymizer()
    cleaned_text, report = anonymizer.anonymize(raw_text)

    # Check typed placeholders exist
    assert "[EMAIL]" in cleaned_text
    assert "[PHONE]" in cleaned_text
    assert "[URL]" in cleaned_text

    # Ensure raw PII is absent
    assert "test.candidate@domain.org" not in cleaned_text
    assert "212-555-0199" not in cleaned_text
    assert "https://myresume.dev" not in cleaned_text

    # Verify report counts
    assert report.total_spans_redacted >= 3
    assert report.counts_by_type["EMAIL"] == 1
    assert report.counts_by_type["PHONE"] == 1
    assert report.counts_by_type["URL"] == 1

    # Verify audit verification passes with 0 unmasked PII
    is_clean, remaining = anonymizer.verify_zero_pii(cleaned_text)
    assert is_clean is True
    assert len(remaining) == 0
