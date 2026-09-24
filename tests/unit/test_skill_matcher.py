"""Unit tests for skill matching with exact, hierarchical parent, and related skill credits."""

from pathlib import Path

from src.skill_normalization.skill_matcher import SkillMatcher
from src.skill_normalization.taxonomy import SkillTaxonomy


def test_skill_matcher_evaluation(project_root: Path):
    """Verify exact match, hierarchical discount, related skill credit, and missing skills."""
    tax = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")
    matcher = SkillMatcher(
        tax,
        parent_discount=0.60,
        related_discount=0.40,
        required_weight=1.0,
        preferred_weight=0.5,
    )

    # Candidate has: Python, PyTorch, PostgreSQL
    candidate_skills = ["sk_python", "sk_pytorch", "sk_postgresql"]

    # Job asks for:
    # 1. Python (required) -> Exact match (1.0)
    # 2. Machine Learning (required) -> Hierarchical parent match through PyTorch (0.60)
    # 3. MySQL (preferred) -> Related match through PostgreSQL (0.40 * 0.5)
    # 4. Docker (required) -> Missing
    job_skills = [
        {"skill_id": "sk_python", "name": "Python", "importance": "required"},
        {
            "skill_id": "sk_machine_learning",
            "name": "Machine Learning",
            "importance": "required",
        },
        {"skill_id": "sk_mysql", "name": "MySQL", "importance": "preferred"},
        {"skill_id": "sk_docker", "name": "Docker", "importance": "required"},
    ]

    result = matcher.match(candidate_skills, job_skills)

    # Matched skills
    matched_ids = [m.job_skill_id for m in result.matched_skills]
    assert "sk_python" in matched_ids
    assert result.matched_count == 1

    # Related / Hierarchical skills
    related_ids = [m.job_skill_id for m in result.related_skills]
    assert "sk_machine_learning" in related_ids
    assert "sk_mysql" in related_ids

    # Missing skills
    missing_ids = [m.skill_id for m in result.missing_skills]
    assert "sk_docker" in missing_ids

    # Score calculation check:
    # Total possible weight = 1.0 (python) + 1.0 (ML) + 0.5 (mysql) + 1.0 (docker) = 3.5
    # Earned weight = 1.0*1.0 (python) + 0.6*1.0 (ML) + 0.4*0.5 (mysql) + 0 (docker) = 1.0 + 0.6 + 0.2 = 1.8
    # Score = 1.8 / 3.5 = ~0.5143
    assert abs(result.skill_score - (1.8 / 3.5)) < 1e-3
