"""Unit tests for text cleaning and boilerplate filtering."""

from src.preprocessing.text_cleaner import (
    clean_text,
    normalize_unicode,
    remove_boilerplate,
    strip_html,
)


def test_strip_html_tags_and_entities():
    """Verify HTML tags and HTML entities are stripped properly."""
    html_input = "<p>Join our team &amp; build great software! <br><strong>Apply now</strong></p>"
    cleaned = strip_html(html_input)
    assert "<p>" not in cleaned
    assert "<strong>" not in cleaned
    assert "&amp;" not in cleaned
    assert "&" in cleaned
    assert "Join our team & build great software!" in cleaned


def test_normalize_unicode():
    """Verify Unicode punctuation, smart quotes, and dashes are normalized."""
    unicode_input = "“Antigravity” – the AI\u00a0engine… \u2018fast\u2019"
    normalized = normalize_unicode(unicode_input)
    assert '"Antigravity"' in normalized
    assert "-" in normalized
    assert "..." in normalized
    assert "'fast'" in normalized
    assert "\u00a0" not in normalized


def test_remove_boilerplate():
    """Verify standard recruitment compliance boilerplate clauses are stripped."""
    text = (
        "We need a Python engineer. We are an equal opportunity employer and do not discriminate. "
        "All qualified applicants will receive consideration for employment without regard to race. "
        "Great benefits included."
    )
    cleaned = remove_boilerplate(text)
    assert "equal opportunity employer" not in cleaned.lower()
    assert "without regard to race" not in cleaned.lower()
    assert "We need a Python engineer." in cleaned
    assert "Great benefits included." in cleaned


def test_clean_text_whitespace_normalization():
    """Verify consecutive whitespace and newlines are collapsed cleanly."""
    messy_text = "  First line   with   spaces.  \n\n\n\n\nSecond line.   "
    cleaned = clean_text(messy_text)
    assert cleaned == "First line with spaces.\n\nSecond line."
