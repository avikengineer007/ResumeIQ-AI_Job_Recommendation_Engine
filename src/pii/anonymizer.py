"""PII Anonymization module with typed placeholder substitution and audit verification.

Replaces identifying attributes with deterministic typed placeholders:
[EMAIL], [PHONE], [URL], [NAME], [ADDRESS], [ID].
"""

from collections import Counter
from dataclasses import dataclass

from src.pii.pii_detector import PIIDetector, PIISpan


@dataclass
class PIIReport:
    total_spans_redacted: int
    counts_by_type: dict[str, int]
    original_length: int
    cleaned_length: int


class PIIAnonymizer:
    """Anonymizer that replaces PII spans with typed bracketed tokens."""

    def __init__(self, detector: PIIDetector | None = None):
        self.detector = detector or PIIDetector()

    def anonymize(self, text: str) -> tuple[str, PIIReport]:
        """Anonymize text by substituting detected PII spans with typed tokens."""
        if not text:
            return "", PIIReport(0, {}, 0, 0)

        spans = self.detector.detect(text)
        if not spans:
            return text, PIIReport(0, {}, len(text), len(text))

        counts: Counter[str] = Counter()
        # Build text backwards by offset to avoid shifting index locations
        sorted_spans = sorted(spans, key=lambda s: s.start, reverse=True)
        chars = list(text)

        for s in sorted_spans:
            placeholder = f"[{s.entity_type}]"
            chars[s.start : s.end] = list(placeholder)
            counts[s.entity_type] += 1

        cleaned_text = "".join(chars)
        report = PIIReport(
            total_spans_redacted=len(spans),
            counts_by_type=dict(counts),
            original_length=len(text),
            cleaned_length=len(cleaned_text),
        )
        return cleaned_text, report

    def verify_zero_pii(self, text: str) -> tuple[bool, list[PIISpan]]:
        """Verify that no unmasked PII entities remain in the text.

        Returns:
            Tuple of (is_clean, remaining_spans).
        """
        remaining = self.detector.detect(text)
        is_clean = len(remaining) == 0
        return is_clean, remaining
