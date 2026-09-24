"""Text cleaning and normalization pipeline.

Cleans raw HTML, normalizes Unicode (NFKC), strips whitespace,
and removes recruitment boilerplate for embedding generation while
preserving original descriptions for auditing.
"""

import html
import re
import unicodedata

# Common hiring boilerplates to filter out from embedding texts
BOILERPLATE_PATTERNS = [
    r"equal opportunity employer[^.\n]*\.?",
    r"we are proud to be an equal opportunity[^.\n]*\.?",
    r"affirmative action employer[^.\n]*\.?",
    r"all qualified applicants will receive consideration for employment without regard to[^.\n]*\.?",
    r"we do not discriminate (on the basis of|based on)[^.\n]*\.?",
    r"reasonable accommodation[^.\n]*\.?",
    r"eoe/m/f/d/v[^.\n]*\.?",
]

_COMPILED_BOILERPLATE = [
    re.compile(pattern, re.IGNORECASE) for pattern in BOILERPLATE_PATTERNS
]

HTML_TAG_REGEX = re.compile(r"<[^>]+>")
MULTIPLE_WHITESPACE_REGEX = re.compile(r"[ \t]+")
MULTIPLE_NEWLINES_REGEX = re.compile(r"\n{3,}")


def strip_html(text: str) -> str:
    """Unescape HTML entities and strip all HTML tags."""
    if not text:
        return ""
    unescaped = html.unescape(text)
    return HTML_TAG_REGEX.sub(" ", unescaped)


def normalize_unicode(text: str) -> str:
    """Normalize Unicode characters using NFKC and replace smart punctuation."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKC", text)
    # Replace non-breaking spaces and smart quotes/dashes
    replacements = {
        "\u00a0": " ",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\ufeff": "",
    }
    for orig, repl in replacements.items():
        normalized = normalized.replace(orig, repl)
    return normalized


def remove_boilerplate(text: str) -> str:
    """Strip common boilerplate clauses (equal opportunity, compliance notices)."""
    cleaned = text
    for pat in _COMPILED_BOILERPLATE:
        cleaned = pat.sub(" ", cleaned)
    return cleaned


def clean_text(
    text: str,
    strip_tags: bool = True,
    normalize_uni: bool = True,
    strip_boilerplate: bool = False,
) -> str:
    """Unified text cleaner function.

    Args:
        text: Raw input string.
        strip_tags: Whether to strip HTML markup.
        normalize_uni: Whether to normalize Unicode NFKC.
        strip_boilerplate: Whether to remove boilerplate clauses.

    Returns:
        Cleaned, normalized text.
    """
    if not text:
        return ""

    result = text
    if strip_tags:
        result = strip_html(result)

    if normalize_uni:
        result = normalize_unicode(result)

    if strip_boilerplate:
        result = remove_boilerplate(result)

    # Normalize whitespace
    lines = [
        MULTIPLE_WHITESPACE_REGEX.sub(" ", line).strip() for line in result.splitlines()
    ]
    result = "\n".join(lines)
    result = MULTIPLE_NEWLINES_REGEX.sub("\n\n", result).strip()

    return result
