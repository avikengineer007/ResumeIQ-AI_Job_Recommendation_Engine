"""Dictionary and PhraseMatcher skill extraction with context-aware disambiguation."""

import re
from dataclasses import dataclass

from src.skill_normalization.taxonomy import SkillTaxonomy

# Ambiguous tokens requiring surrounding context validation
AMBIGUOUS_TOKENS = {"go", "r", "c", "spring", "swift", "rust", "word", "excel"}

# Context keywords that confirm technical skill usage
CONTEXT_SIGNALS: dict[str, list[str]] = {
    "go": [
        "golang",
        "concurrency",
        "goroutines",
        "backend",
        "microservices",
        "docker",
        "kubernetes",
        "developer",
        "engineer",
        "programming",
        "python",
    ],
    "r": [
        "r-lang",
        "statistics",
        "data analysis",
        "biostatistics",
        "ggplot",
        "rstudio",
        "python",
        "statistical",
        "machine learning",
    ],
    "c": [
        "c++",
        "embedded",
        "c/c++",
        "linux",
        "systems",
        "kernel",
        "compilers",
        "c programming",
        "c language",
    ],
    "spring": [
        "spring boot",
        "springboot",
        "java",
        "hibernate",
        "microservices",
        "jvm",
        "backend",
        "jpa",
        "rest api",
    ],
    "swift": [
        "ios",
        "apple",
        "xcode",
        "mobile",
        "uikit",
        "swiftui",
        "macos",
        "objective-c",
    ],
    "rust": [
        "systems programming",
        "memory safety",
        "cargo",
        "webassembly",
        "concurrency",
        "c++",
        "developer",
        "backend",
    ],
}

# Context phrases indicating non-technical usage
NEGATIVE_SIGNALS: dict[str, list[str]] = {
    "spring": [
        r"\bspring\s+(?:20\d{2}|19\d{2})\b",
        r"\bspring\s+semester\b",
        r"\bspring\s+break\b",
        r"\bspring\s+(?:internship|intern)\b",
    ],
    "go": [
        r"\bgo\s+to\b",
        r"\bgo\s+ahead\b",
        r"\bgo\s+through\b",
        r"\bgo\s+live\b",
        r"\bon\s+the\s+go\b",
        r"\bgo[- ]to[- ]market\b",
    ],
    "swift": [
        r"\bswift\s+action\b",
        r"\bswift\s+response\b",
        r"\bswift\s+resolution\b",
    ],
}


@dataclass
class ExtractedSkillMention:
    raw_mention: str
    canonical_skill_id: str | None
    start_char: int
    end_char: int
    confidence: float
    method: str  # exact, phrase, disambiguated


class DictionaryMatcher:
    """Extracts skill mentions from text using taxonomy patterns with ambiguity guards."""

    def __init__(self, taxonomy: SkillTaxonomy) -> None:
        self.taxonomy = taxonomy
        self._build_patterns()

    def _build_patterns(self) -> None:
        """Compile regex patterns from taxonomy aliases."""
        # Sort by length descending to prioritize longer multi-word phrases over single tokens
        sorted_aliases = sorted(self.taxonomy.alias_to_id.keys(), key=len, reverse=True)
        self.exact_patterns: list[tuple[str, str, re.Pattern[str]]] = []

        for alias in sorted_aliases:
            if not alias.strip():
                continue
            cid = self.taxonomy.alias_to_id[alias]

            # Short tokens (<= 2 chars like 'c', 'r', 'go', 'js', 'ts')
            if len(alias) <= 2:
                cap_form = (
                    alias.capitalize()
                    if alias.lower() in ("go", "r", "c")
                    else alias.upper()
                )
                pattern = re.compile(
                    rf"\b(?:{re.escape(cap_form)}|{re.escape(alias.upper())})\b"
                )
            else:
                words = [re.escape(w) for w in alias.split()]
                if not words:
                    continue
                pattern_body = r"[-_/\s.]+".join(words)
                prefix_bound = r"\b" if alias[0].isalnum() else r"(?:(?<=[\s,./])|^)"
                suffix_bound = r"\b" if alias[-1].isalnum() else r"(?:(?=[\s,./])|$)"
                pattern = re.compile(
                    rf"{prefix_bound}{pattern_body}{suffix_bound}", re.IGNORECASE
                )

            self.exact_patterns.append((alias, cid, pattern))

    def _is_ambiguous_valid(
        self, token: str, match_text: str, context_window: str
    ) -> bool:
        """Validate whether an ambiguous token mention is genuinely a technical skill."""
        lower_token = token.lower()
        lower_ctx = context_window.lower()

        # Check negative signals first
        if lower_token in NEGATIVE_SIGNALS:
            for neg_pat in NEGATIVE_SIGNALS[lower_token]:
                if re.search(neg_pat, lower_ctx, re.IGNORECASE):
                    return False

        # Short tokens (C, R, Go) must be capitalized
        if len(token) <= 2 and not match_text.isupper() and match_text != "Go":
            return False

        # Check positive context signals
        if lower_token in CONTEXT_SIGNALS:
            signals = CONTEXT_SIGNALS[lower_token]
            for sig in signals:
                if sig in lower_ctx:
                    return True
            # If no positive signals found within window, reject ambiguous match
            return False

        return True

    def extract_skills(
        self, text: str, section_name: str = "all"
    ) -> list[ExtractedSkillMention]:
        """Extract all skill mentions from text with source character offsets."""
        if not text:
            return []

        raw_matches: list[tuple[int, int, str, str]] = []

        # Find all phrase occurrences
        for alias, cid, regex in self.exact_patterns:
            for m in regex.finditer(text):
                start, end = m.start(), m.end()
                match_str = m.group(0)

                # Context window (+/- 80 characters)
                ctx_start = max(0, start - 80)
                ctx_end = min(len(text), end + 80)
                ctx_window = text[ctx_start:ctx_end]

                # Ambiguity resolution
                if alias.lower() in AMBIGUOUS_TOKENS:
                    if not self._is_ambiguous_valid(alias, match_str, ctx_window):
                        continue

                raw_matches.append((start, end, match_str, cid))

        # Longest match wins / non-overlapping deduplication
        raw_matches.sort(key=lambda x: (x[0], -(x[1] - x[0])))
        deduped: list[ExtractedSkillMention] = []
        last_end = -1

        for start, end, match_str, cid in raw_matches:
            if start >= last_end:
                deduped.append(
                    ExtractedSkillMention(
                        raw_mention=match_str,
                        canonical_skill_id=cid,
                        start_char=start,
                        end_char=end,
                        confidence=1.0 if len(match_str) > 2 else 0.90,
                        method="dictionary_phrase",
                    )
                )
                last_end = end

        return deduped
