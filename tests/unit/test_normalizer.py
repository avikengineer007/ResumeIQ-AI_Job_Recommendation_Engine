"""Unit tests for the 4-tier skill normalizer cascade."""

from pathlib import Path

from src.skill_normalization.normalizer import SkillNormalizer
from src.skill_normalization.taxonomy import SkillTaxonomy


def test_exact_alias_normalization(project_root: Path):
    """Verify exact alias normalization across punctuation, versions, and abbreviations."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")
    normalizer = SkillNormalizer(tax)

    res_react = normalizer.normalize("ReactJS")
    assert res_react.canonical_skill_id == "sk_react"
    assert res_react.method == "exact"
    assert res_react.confidence == 1.0

    res_py = normalizer.normalize("Python 3.11")
    assert res_py.canonical_skill_id == "sk_python"
    assert res_py.method == "exact"

    res_sklearn = normalizer.normalize("sklearn")
    assert res_sklearn.canonical_skill_id == "sk_scikit_learn"

    res_postgres = normalizer.normalize("psql")
    assert res_postgres.canonical_skill_id == "sk_postgresql"


def test_fuzzy_normalization(project_root: Path):
    """Verify fuzzy matching with RapidFuzz ratio >= 92."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")
    normalizer = SkillNormalizer(tax, fuzzy_threshold=90.0)

    # Slight typo / character variation
    res_k8s = normalizer.normalize("kubernets")
    assert res_k8s.canonical_skill_id == "sk_kubernetes"
    assert res_k8s.method == "fuzzy"
    assert res_k8s.confidence >= 0.90


def test_unresolved_queue_capture(project_root: Path):
    """Verify unknown or unmapped skill mentions enter the unresolved review queue."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")
    normalizer = SkillNormalizer(tax)

    res_unknown = normalizer.normalize("ObscureCustomFrameworkXYZ")
    assert res_unknown.canonical_skill_id is None
    assert res_unknown.method == "unresolved"
    assert res_unknown.confidence == 0.0

    unresolved = normalizer.get_unresolved_queue()
    assert len(unresolved) == 1
    assert unresolved[0]["raw_mention"] == "ObscureCustomFrameworkXYZ"
