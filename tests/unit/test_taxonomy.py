"""Unit tests for SkillTaxonomy loader, aliases, and relationship graphs."""

from pathlib import Path

from src.skill_normalization.taxonomy import SkillTaxonomy


def test_taxonomy_loading(project_root: Path):
    """Verify loading taxonomy, aliases, and relations from data/processed/."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")

    assert len(tax.skills) >= 20
    assert "sk_python" in tax.skills
    assert "sk_machine_learning" in tax.skills

    py_skill = tax.get_skill("sk_python")
    assert py_skill is not None
    assert py_skill.canonical_name == "Python"
    assert py_skill.skill_type == "technical"


def test_alias_lookup(project_root: Path):
    """Verify alias mapping to canonical skill IDs."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")

    assert tax.alias_to_id.get("reactjs") == "sk_react"
    assert tax.alias_to_id.get("react js") == "sk_react"
    assert tax.alias_to_id.get("postgres") == "sk_postgresql"
    assert tax.alias_to_id.get("sklearn") == "sk_scikit_learn"
    assert tax.alias_to_id.get("golang") == "sk_golang"


def test_hierarchy_ancestor_resolution(project_root: Path):
    """Verify recursive parent traversal: PyTorch -> Deep Learning -> Machine Learning."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")

    parents = tax.get_all_parents("sk_pytorch")
    assert "sk_deep_learning" in parents
    assert "sk_machine_learning" in parents


def test_related_skills_resolution(project_root: Path):
    """Verify non-hierarchical related skills lookup."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")

    related = tax.get_related_skills("sk_postgresql")
    target_ids = [r[0] for r in related]
    assert "sk_mysql" in target_ids
