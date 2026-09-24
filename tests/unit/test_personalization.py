"""Unit tests for personalization module, hard constraint filters, and soft scoring."""

from src.recommendation.personalization import (
    CandidatePreferences,
    PersonalizedScorer,
    compute_experience_score,
    compute_location_score,
    compute_role_score,
    compute_work_mode_score,
    filter_hard_constraints,
)


def test_hard_constraint_filtering_strict_mode() -> None:
    """Verify that jobs violating required work mode are strictly filtered out regardless of scores."""
    jobs = [
        {
            "id": "job_remote",
            "title": "Backend Dev",
            "work_mode": "remote",
            "location": "Anywhere",
            "rerank_score": 0.5,
        },
        {
            "id": "job_onsite",
            "title": "Backend Dev",
            "work_mode": "onsite",
            "location": "New York",
            "rerank_score": 0.99,
        },
    ]

    prefs = CandidatePreferences(
        preferred_work_modes=["remote"],
        require_work_mode=True,  # STRICT FILTER
    )

    survivors = filter_hard_constraints(jobs, prefs)
    survivor_ids = [j["id"] for j in survivors]

    # job_onsite must be strictly filtered out even though it had a near-perfect rerank score!
    assert survivor_ids == ["job_remote"]
    assert "job_onsite" not in survivor_ids


def test_hard_constraint_filtering_strict_location() -> None:
    """Verify that jobs violating required location are strictly filtered out (unless remote)."""
    jobs = [
        {"id": "job_ny", "location": "New York, NY", "work_mode": "onsite"},
        {"id": "job_sf", "location": "San Francisco, CA", "work_mode": "onsite"},
        {"id": "job_remote", "location": "Remote", "work_mode": "remote"},
    ]

    prefs = CandidatePreferences(
        preferred_locations=["New York"],
        require_location=True,  # STRICT FILTER
    )

    survivors = filter_hard_constraints(jobs, prefs)
    survivor_ids = [j["id"] for j in survivors]

    assert "job_ny" in survivor_ids
    assert "job_remote" in survivor_ids  # Remote is accepted
    assert "job_sf" not in survivor_ids


def test_soft_constraints_allow_all_jobs() -> None:
    """When requirements are soft (require_*=False), all candidates pass filtering."""
    jobs = [
        {"id": "job_1", "work_mode": "onsite", "location": "London"},
        {"id": "job_2", "work_mode": "remote", "location": "Remote"},
    ]
    prefs = CandidatePreferences(
        preferred_work_modes=["remote"],
        preferred_locations=["Berlin"],
        require_work_mode=False,
        require_location=False,
    )
    survivors = filter_hard_constraints(jobs, prefs)
    assert len(survivors) == 2


def test_compute_experience_score() -> None:
    # Meets or exceeds requirement
    assert compute_experience_score(candidate_years=5.0, required_years=3.0) == 1.0
    assert compute_experience_score(candidate_years=3.0, required_years=3.0) == 1.0

    # Under requirement: exponential decay
    score_1yr_gap = compute_experience_score(candidate_years=2.0, required_years=3.0)
    score_2yr_gap = compute_experience_score(candidate_years=1.0, required_years=3.0)
    assert 0.0 < score_2yr_gap < score_1yr_gap < 1.0


def test_compute_role_and_location_scores() -> None:
    # Role alignment
    assert (
        compute_role_score("Machine Learning Engineer", "Senior Machine Learning Lead")
        > 0.0
    )
    assert compute_role_score("Frontend Developer", "Civil Structural Engineer") == 0.0

    # Location alignment
    assert compute_location_score("New York, NY", ["New York"]) == 1.0
    assert compute_location_score("Fully Remote", ["Boston"]) == 0.95
    assert compute_location_score("Chicago, IL", ["Seattle"]) == 0.0

    # Mode alignment
    assert compute_work_mode_score("remote", ["remote", "hybrid"]) == 1.0
    assert compute_work_mode_score("onsite", ["remote"]) == 0.0


def test_personalized_scorer_end_to_end() -> None:
    scorer = PersonalizedScorer()
    jobs = [
        {
            "id": "job_ml_remote",
            "title": "Senior ML Engineer",
            "work_mode": "remote",
            "location": "Remote",
            "required_years": 4.0,
            "rerank_score": 0.85,
            "vector_score": 0.80,
            "skill_score": 0.90,
        },
        {
            "id": "job_civil_onsite",
            "title": "Civil Structural Engineer",
            "work_mode": "onsite",
            "location": "Dallas",
            "required_years": 8.0,
            "rerank_score": 0.95,  # higher raw score but completely wrong role/mode
            "vector_score": 0.20,
            "skill_score": 0.10,
        },
    ]

    prefs = CandidatePreferences(
        target_role="ML Engineer",
        years_of_experience=5.0,
        preferred_work_modes=["remote"],
        preferred_locations=["Remote"],
        require_work_mode=True,  # filters out job_civil_onsite
    )

    ranked = scorer.score_candidates(jobs, prefs, top_k=2)
    assert len(ranked) == 1
    assert ranked[0].job_id == "job_ml_remote"
    assert ranked[0].s_exp == 1.0
    assert ranked[0].s_mode == 1.0
    assert ranked[0].final_score > 0.0
