"""Skill NER model wrapper using spaCy and taxonomy integration."""

from typing import Any

import spacy

from src.skill_extraction.dictionary_matcher import ExtractedSkillMention
from src.skill_normalization.taxonomy import SkillTaxonomy


class SkillNER:
    """Named Entity Recognition model wrapper for extracting skill spans."""

    def __init__(
        self, taxonomy: SkillTaxonomy, model_name: str = "en_core_web_sm"
    ) -> None:
        self.taxonomy = taxonomy
        try:
            self.nlp = spacy.load(model_name)
        except Exception:
            self.nlp = spacy.blank("en")

        self._configure_entity_ruler()

    def _configure_entity_ruler(self) -> None:
        """Inject taxonomy patterns into spaCy pipeline via EntityRuler."""
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe(
                "entity_ruler", before="ner" if "ner" in self.nlp.pipe_names else None
            )
        else:
            ruler = self.nlp.get_pipe("entity_ruler")

        patterns: list[dict[str, Any]] = []
        for alias, cid in self.taxonomy.alias_to_id.items():
            if (
                len(alias) > 2
            ):  # Skip single/double letter tokens to avoid spaCy over-matching
                patterns.append({"label": "SKILL", "pattern": alias, "id": cid})

        ruler.add_patterns(patterns)

    def extract_entities(self, text: str) -> list[ExtractedSkillMention]:
        """Extract skill entities using spaCy pipeline with offsets."""
        if not text:
            return []

        doc = self.nlp(text)
        results: list[ExtractedSkillMention] = []

        for ent in doc.ents:
            if ent.label_ == "SKILL":
                cid = (
                    ent.ent_id_
                    if ent.ent_id_
                    else self.taxonomy.alias_to_id.get(ent.text.lower())
                )
                results.append(
                    ExtractedSkillMention(
                        raw_mention=ent.text,
                        canonical_skill_id=cid,
                        start_char=ent.start_char,
                        end_char=ent.end_char,
                        confidence=0.92,
                        method="spacy_ner_ruler",
                    )
                )

        return results
