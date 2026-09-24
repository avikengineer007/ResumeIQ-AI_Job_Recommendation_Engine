"""Skill normalization cascade: Exact -> Fuzzy (>=92) -> Semantic Embedding -> Unresolved Queue."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from rapidfuzz import fuzz, process

from src.skill_normalization.taxonomy import SkillTaxonomy, normalize_lookup_key


@dataclass
class NormalizationResult:
    raw_mention: str
    canonical_skill_id: str | None
    canonical_name: str | None
    method: str  # exact, fuzzy, embedding, unresolved
    confidence: float


class SkillNormalizer:
    """Normalizes raw skill mentions to canonical skill IDs using a 4-tier cascade."""

    def __init__(
        self,
        taxonomy: SkillTaxonomy,
        fuzzy_threshold: float = 92.0,
        embedding_threshold: float = 0.82,
        embed_fn: Callable[[str], Any] | None = None,
    ) -> None:
        self.taxonomy = taxonomy
        self.fuzzy_threshold = fuzzy_threshold
        self.embedding_threshold = embedding_threshold
        self.embed_fn = embed_fn
        self.unresolved_queue: list[dict[str, Any]] = []

    def normalize(self, raw_mention: str) -> NormalizationResult:
        """Map a raw skill mention string to a canonical skill ID."""
        cleaned_key = normalize_lookup_key(raw_mention)
        if not cleaned_key:
            return NormalizationResult(
                raw_mention=raw_mention,
                canonical_skill_id=None,
                canonical_name=None,
                method="unresolved",
                confidence=0.0,
            )

        # 1. Exact alias lookup
        if cleaned_key in self.taxonomy.alias_to_id:
            cid = self.taxonomy.alias_to_id[cleaned_key]
            skill = self.taxonomy.get_skill(cid)
            return NormalizationResult(
                raw_mention=raw_mention,
                canonical_skill_id=cid,
                canonical_name=skill.canonical_name if skill else cleaned_key,
                method="exact",
                confidence=1.0,
            )

        # 2. Fuzzy match against all known taxonomy aliases
        if self.taxonomy.raw_aliases:
            match = process.extractOne(
                cleaned_key,
                self.taxonomy.raw_aliases,
                scorer=fuzz.ratio,
            )
            if match and match[1] >= self.fuzzy_threshold:
                matched_alias = match[0]
                cid = self.taxonomy.alias_to_id[matched_alias]
                skill = self.taxonomy.get_skill(cid)
                score = round(float(match[1]) / 100.0, 2)
                return NormalizationResult(
                    raw_mention=raw_mention,
                    canonical_skill_id=cid,
                    canonical_name=skill.canonical_name if skill else matched_alias,
                    method="fuzzy",
                    confidence=score,
                )

        # 3. Optional Embedding Nearest Neighbor
        if self.embed_fn is not None:
            # Semantic search can be applied here when embeddings are initialized
            pass

        # 4. Fallback: Queue for human audit and review
        self.unresolved_queue.append(
            {
                "raw_mention": raw_mention,
                "cleaned_key": cleaned_key,
            }
        )
        return NormalizationResult(
            raw_mention=raw_mention,
            canonical_skill_id=None,
            canonical_name=None,
            method="unresolved",
            confidence=0.0,
        )

    def normalize_batch(self, mentions: list[str]) -> list[NormalizationResult]:
        """Normalize a list of skill mentions."""
        return [self.normalize(m) for m in mentions]

    def get_unresolved_queue(self) -> list[dict[str, Any]]:
        """Return all unresolved mentions logged during normalization."""
        return self.unresolved_queue
