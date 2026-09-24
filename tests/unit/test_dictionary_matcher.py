"""Unit tests for dictionary matcher and context-aware ambiguous token disambiguation."""

from pathlib import Path

from src.skill_extraction.dictionary_matcher import DictionaryMatcher
from src.skill_normalization.taxonomy import SkillTaxonomy


def test_phrase_and_alias_extraction(project_root: Path):
    """Verify multi-token and alias skill extraction with correct offsets."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")
    matcher = DictionaryMatcher(tax)

    text = "Extensive experience in Natural Language Processing, scikit-learn, and React.js."
    mentions = matcher.extract_skills(text)
    cids = {m.canonical_skill_id for m in mentions}

    assert "sk_nlp" in cids
    assert "sk_scikit_learn" in cids
    assert "sk_react" in cids

    # Check offsets
    for m in mentions:
        assert text[m.start_char : m.end_char] == m.raw_mention


def test_ambiguous_token_disambiguation_positive(project_root: Path):
    """Verify ambiguous tokens are extracted when technical context is present."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")
    matcher = DictionaryMatcher(tax)

    # Go programming
    text_go = (
        "Senior Backend Engineer building Go microservices with Docker and Kubernetes."
    )
    cids_go = {m.canonical_skill_id for m in matcher.extract_skills(text_go)}
    assert "sk_golang" in cids_go

    # Swift programming
    text_swift = "iOS developer proficient in Swift and mobile app architecture."
    cids_swift = {m.canonical_skill_id for m in matcher.extract_skills(text_swift)}
    assert "sk_swift" in cids_swift

    # Spring framework
    text_spring = "Backend Java developer working with Spring microservices."
    cids_spring = {m.canonical_skill_id for m in matcher.extract_skills(text_spring)}
    assert "sk_spring" in cids_spring


def test_ambiguous_token_disambiguation_negative(project_root: Path):
    """Verify ambiguous tokens are REJECTED when used as common English words."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")
    matcher = DictionaryMatcher(tax)

    # "go to" verb
    text_go = "Candidates must go to the main office for orientation."
    cids_go = {m.canonical_skill_id for m in matcher.extract_skills(text_go)}
    assert "sk_golang" not in cids_go

    # "swift action" adjective
    text_swift = "The incident response team took swift action to restore service."
    cids_swift = {m.canonical_skill_id for m in matcher.extract_skills(text_swift)}
    assert "sk_swift" not in cids_swift

    # "Spring 2022" calendar term
    text_spring = "Graduated with honors in Spring 2022."
    cids_spring = {m.canonical_skill_id for m in matcher.extract_skills(text_spring)}
    assert "sk_spring" not in cids_spring
