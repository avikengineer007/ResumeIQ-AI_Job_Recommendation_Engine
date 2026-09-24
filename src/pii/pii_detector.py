"""PII Detection module using regex patterns and spaCy NER.

Detects email addresses, phone numbers, URLs, social links,
physical addresses, and candidate names.
"""

import re
from dataclasses import dataclass

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)
URL_PATTERN = re.compile(
    r"https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_+.~#?&/=]*"
)
LINKEDIN_GITHUB_PATTERN = re.compile(
    r"(?:linkedin\.com/in/|github\.com/)[a-zA-Z0-9_-]+"
)
SSN_OR_ID_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b")
STREET_ADDRESS_PATTERN = re.compile(
    r"\b\d{1,5}\s+[A-Za-z0-9\s.,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way)\b",
    re.IGNORECASE,
)


@dataclass
class PIISpan:
    entity_type: str  # EMAIL, PHONE, URL, NAME, ADDRESS, ID
    start: int
    end: int
    text: str


class PIIDetector:
    """Detects PII occurrences across text strings."""

    def __init__(self, spacy_model: str | None = None):
        self.nlp = None
        if spacy_model:
            try:
                import spacy

                self.nlp = spacy.load(spacy_model)
            except Exception:
                self.nlp = None

    def detect(self, text: str) -> list[PIISpan]:
        """Find all PII occurrences and return non-overlapping spans sorted by start offset."""
        if not text:
            return []

        spans: list[PIISpan] = []

        # 1. Regex Detectors
        for match in EMAIL_PATTERN.finditer(text):
            spans.append(PIISpan("EMAIL", match.start(), match.end(), match.group()))

        for match in PHONE_PATTERN.finditer(text):
            spans.append(PIISpan("PHONE", match.start(), match.end(), match.group()))

        for match in URL_PATTERN.finditer(text):
            spans.append(PIISpan("URL", match.start(), match.end(), match.group()))

        for match in LINKEDIN_GITHUB_PATTERN.finditer(text):
            spans.append(PIISpan("URL", match.start(), match.end(), match.group()))

        for match in SSN_OR_ID_PATTERN.finditer(text):
            spans.append(PIISpan("ID", match.start(), match.end(), match.group()))

        for match in STREET_ADDRESS_PATTERN.finditer(text):
            spans.append(PIISpan("ADDRESS", match.start(), match.end(), match.group()))

        # 2. NER Detectors if model is loaded
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    spans.append(
                        PIISpan("NAME", ent.start_char, ent.end_char, ent.text)
                    )
                elif ent.label_ in ("GPE", "LOC", "FAC"):
                    # Check if not already captured
                    spans.append(
                        PIISpan("ADDRESS", ent.start_char, ent.end_char, ent.text)
                    )

        # 3. Resolve overlaps (longest span wins)
        spans.sort(key=lambda s: (s.start, -(s.end - s.start)))
        filtered: list[PIISpan] = []
        last_end = 0

        for span in spans:
            if span.start >= last_end:
                filtered.append(span)
                last_end = span.end

        return filtered
