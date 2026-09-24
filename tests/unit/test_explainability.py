"""Unit tests for Phase 11 Evidence-Grounded Explainability Layer.

Tests:
1. EvidenceBuilder: skill overlap, gap analysis, experience alignment, score drivers.
2. TemplateExplainer: multi-facet explanation generation, markdown formatting, honest gaps,
   active verification wiring.
3. ExplanationVerifier: faithfulness validation, hallucination detection, numerical fidelity,
   percentage / calibrated probability fidelity, work arrangement consistency.
4. Adversarial tests: ungrounded skill citations, percentage tampering, malformed inputs,
   and strict verification rejection.
"""

from unittest.mock import MagicMock

import pytest

from src.explainability.evidence import EvidenceBuilder, ExplanationEvidence
from src.explainability.templates import GeneratedExplanation, TemplateExplainer
from src.explainability.verifier import (
    ExplanationVerifier,
    UnfaithfulExplanationError,
)
from src.recommendation.personalization import (
    CandidatePreferences,
    PersonalizedJobScore,
)


def test_evidence_builder_complete() -> None:
    mock_taxonomy = MagicMock()
    mock_taxonomy.get_parents.side_effect = lambda s_id: (
        ["pytorch"] if "torch" in s_id else []
    )
    mock_taxonomy.get_related.side_effect = lambda s_id: []

    builder = EvidenceBuilder(skill_taxonomy=mock_taxonomy)

    candidate = {
        "resume_id": "res_01",
        "total_years": 5.0,
        "skills": ["Python", "PyTorch", "SQL"],
        "preferences": {
            "role": "Senior Machine Learning Engineer",
            "work_modes": ["remote"],
        },
        "summary": "Experienced ML engineer specializing in deep learning and NLP.",
    }

    job = {
        "job_id": "job_101",
        "title": "Machine Learning Engineer",
        "company": "DeepTech AI",
        "skills": ["Python", "PyTorch", "TorchVision", "Docker"],
        "required_skills": ["Python", "PyTorch"],
        "required_years": 4.0,
        "location": "San Francisco, CA",
        "work_mode": "remote",
        "description": "Looking for an ML engineer to build scalable PyTorch inference pipelines.",
    }

    score_info = PersonalizedJobScore(
        job_id="job_101",
        final_score=0.88,
        rank=1,
        s_rerank=1.0,
        s_sem=0.85,
        s_skill=0.80,
        s_exp=0.90,
        s_role=0.75,
        s_loc=0.80,
        s_mode=0.80,
    )

    prefs = CandidatePreferences(
        target_role="Machine Learning Engineer",
        years_of_experience=5.0,
        candidate_skills=["Python", "PyTorch", "SQL"],
        preferred_work_modes=["remote"],
    )

    evidence = builder.build_evidence(
        candidate_resume=candidate,
        job_posting=job,
        score_info=score_info,
        preferences=prefs,
        calibrated_probability=0.89,
    )

    assert isinstance(evidence, ExplanationEvidence)
    assert evidence.job_id == "job_101"
    assert evidence.job_title == "Machine Learning Engineer"
    assert evidence.company == "DeepTech AI"

    # Skills: Python and PyTorch are exact matches; TorchVision has parent PyTorch; Docker is missing
    matched_names = {s.skill_name for s in evidence.matched_skills}
    assert "Python" in matched_names
    assert "PyTorch" in matched_names

    missing_names = {s.skill_name for s in evidence.missing_skills}
    assert "Docker" in missing_names

    # Experience
    assert evidence.experience.candidate_years == 5.0
    assert evidence.experience.required_years == 4.0
    assert evidence.experience.meets_requirement is True
    assert evidence.experience.seniority_alignment == "matched"

    # Role
    assert (
        "machine" in evidence.role.matched_keywords
        or "learning" in evidence.role.matched_keywords
    )

    # Location & Mode
    assert evidence.location.is_match is True
    assert evidence.location.job_work_mode == "remote"

    # Scores
    assert evidence.scores.final_score == 0.88
    assert evidence.scores.rank == 1
    assert evidence.scores.calibrated_probability == 0.89
    assert evidence.scores.primary_driver == "Cross-Encoder Relevance"


def test_template_explainer_rendering_and_auto_verification() -> None:
    builder = EvidenceBuilder()
    candidate = {
        "resume_id": "res_02",
        "total_years": 2.0,
        "skills": ["JavaScript", "React"],
        "preferences": {"role": "Frontend Developer"},
    }
    job = {
        "job_id": "job_202",
        "title": "Senior Frontend Engineer",
        "company": "WebCorp",
        "skills": ["React", "TypeScript", "GraphQL"],
        "required_skills": ["React", "TypeScript"],
        "required_years": 5.0,
        "location": "New York, NY",
        "work_mode": "hybrid",
    }

    score_info = {
        "final_score": 0.65,
        "rank": 2,
        "rerank_score": 0.60,
        "semantic_score": 0.70,
        "skill_score": 0.50,
    }

    evidence = builder.build_evidence(
        candidate_resume=candidate,
        job_posting=job,
        score_info=score_info,
        calibrated_probability=0.62,
    )

    explainer = TemplateExplainer()
    explanation = explainer.explain(evidence)

    assert isinstance(explanation, GeneratedExplanation)
    assert explanation.job_id == "job_202"
    assert explanation.rank == 2
    assert "React" in " ".join(explanation.skill_bullets)
    assert "TypeScript" in explanation.missing_skills_bullet
    assert "gap" in explanation.experience_statement.lower()

    # Active verification check
    assert explanation.is_verified is True
    assert explanation.verification_report is not None
    assert explanation.verification_report.is_faithful is True

    # Markdown export
    md = explanation.to_markdown()
    assert "### #2 Senior Frontend Engineer at WebCorp" in md
    assert "Skill Alignment" in md
    assert "Estimated Match Confidence: ~62% (provisional)" in md


def test_explanation_verifier_faithful_and_unfaithful() -> None:
    builder = EvidenceBuilder()
    candidate = {
        "resume_id": "res_03",
        "total_years": 4.0,
        "skills": ["Python", "FastAPI"],
        "preferences": {"role": "Backend Engineer"},
    }
    job = {
        "job_id": "job_303",
        "title": "Backend Engineer",
        "company": "SaaS Co",
        "skills": ["Python", "FastAPI", "Kubernetes"],
        "required_skills": ["Python", "FastAPI", "Kubernetes"],
        "required_years": 3.0,
        "location": "Remote",
        "work_mode": "remote",
    }

    evidence = builder.build_evidence(
        candidate_resume=candidate,
        job_posting=job,
        score_info={"final_score": 0.90, "rank": 1},
        calibrated_probability=0.91,
    )

    explainer = TemplateExplainer()
    explanation = explainer.explain(evidence)

    verifier = ExplanationVerifier()
    # 1. Faithfully generated explanation must pass
    report = verifier.verify(explanation, evidence)
    assert report.is_faithful is True
    assert len(report.violations) == 0
    assert "Python" in report.verified_skills

    # 2. Altered explanation with hallucinated skill and fake 100% coverage claim
    hallucinated_explanation = GeneratedExplanation(
        job_id="job_303",
        job_title="Backend Engineer",
        company="SaaS Co",
        rank=1,
        headline="100% skill overlap guaranteed!",
        summary="Candidate knows Rust and C++ which is great.",
        skill_bullets=["Candidate has Python, FastAPI, and Rust expertise."],
        experience_statement="Candidate has 10 years of experience (requires 3.0 years).",
        role_statement="Matches role.",
        logistics_statement="Fully remote.",
        missing_skills_bullet="full skill coverage",
        transparency_statement="Score 0.90",
    )

    bad_report = verifier.verify(hallucinated_explanation, evidence)
    assert bad_report.is_faithful is False
    assert len(bad_report.violations) >= 2
    # Should catch experience number contradiction (10y vs 4y)
    assert any("experience" in v.lower() for v in bad_report.violations)
    # Should catch dishonest claim of full skill coverage when Kubernetes is missing
    assert any("full skill coverage" in v.lower() for v in bad_report.violations)


def test_verifier_work_mode_fidelity() -> None:
    builder = EvidenceBuilder()
    candidate = {"resume_id": "res_04", "total_years": 3.0, "skills": ["Go"]}
    job = {
        "job_id": "job_404",
        "title": "Systems Engineer",
        "company": "InfraCorp",
        "skills": ["Go"],
        "required_years": 2.0,
        "location": "Austin, TX",
        "work_mode": "onsite",
    }

    evidence = builder.build_evidence(
        candidate_resume=candidate,
        job_posting=job,
        score_info={"final_score": 0.85, "rank": 1},
    )

    # Hallucinate that this onsite job is fully remote
    fake_explanation = GeneratedExplanation(
        job_id="job_404",
        job_title="Systems Engineer",
        company="InfraCorp",
        rank=1,
        headline="Systems Role",
        summary="Good match.",
        skill_bullets=["Direct skill matches: Go"],
        experience_statement="Candidate meets requirement with 3.0 years of experience (requires 2.0 years).",
        role_statement="Aligned.",
        logistics_statement="Fully remote position with flexible hours.",
        missing_skills_bullet="None",
        transparency_statement="Score 0.85",
    )

    verifier = ExplanationVerifier()
    report = verifier.verify(fake_explanation, evidence)
    assert report.is_faithful is False
    assert any(
        "remote" in v.lower() and "onsite" in v.lower() for v in report.violations
    )


def test_edge_cases_overqualified_and_full_skill_match() -> None:
    builder = EvidenceBuilder()
    candidate = {
        "resume_id": "res_05",
        "total_years": 8.0,
        "skills": ["Python", "Django"],
    }
    job = {
        "job_id": "job_505",
        "title": "Junior Python Dev",
        "company": "StartUp",
        "skills": ["Python", "Django"],
        "required_skills": ["Python"],
        "required_years": 2.0,
        "location": "Remote",
        "work_mode": "remote",
    }

    evidence = builder.build_evidence(
        candidate_resume=candidate,
        job_posting=job,
        score_info={"final_score": 0.95, "rank": 1},
    )

    assert evidence.experience.seniority_alignment == "overqualified"
    assert len(evidence.missing_skills) == 0

    explainer = TemplateExplainer()
    explanation = explainer.explain(evidence)

    assert "Complete Skill Match" in explanation.headline
    assert "exceeding" in explanation.experience_statement.lower()

    verifier = ExplanationVerifier()
    report = verifier.verify(explanation, evidence)
    assert report.is_faithful is True


def test_verifier_mismatched_metadata() -> None:
    builder = EvidenceBuilder()
    evidence = builder.build_evidence(
        candidate_resume={"resume_id": "res_06", "total_years": 1.0, "skills": ["SQL"]},
        job_posting={"job_id": "job_606", "title": "Data Analyst", "skills": ["SQL"]},
        score_info={"final_score": 0.80, "rank": 1},
    )

    bad_id_explanation = GeneratedExplanation(
        job_id="wrong_id",
        job_title="Data Analyst",
        company="Company",
        rank=5,  # Mismatched rank
        headline="Analyst role",
        summary="Match summary",
        experience_statement="Candidate meets requirement with 1.0 years of experience (requires 0.0 years).",
    )

    verifier = ExplanationVerifier()
    report = verifier.verify(bad_id_explanation, evidence)
    assert report.is_faithful is False
    assert any("job_id" in v for v in report.violations)
    assert any("rank" in v for v in report.violations)

    rep_dict = report.to_dict()
    assert rep_dict["is_faithful"] is False


def test_adversarial_skill_hallucination_rejection() -> None:
    builder = EvidenceBuilder()
    candidate = {
        "resume_id": "res_adv1",
        "total_years": 3.0,
        "skills": ["Java", "Spring"],
    }
    job = {
        "job_id": "job_adv1",
        "title": "Backend Developer",
        "skills": ["Java", "Spring"],
        "required_years": 3.0,
    }
    evidence = builder.build_evidence(
        candidate, job, score_info={"final_score": 0.85, "rank": 1}
    )

    # Deliberately inject a hallucinated skill not in candidate resume, job, or taxonomy
    adversarial_explanation = GeneratedExplanation(
        job_id="job_adv1",
        job_title="Backend Developer",
        company="Company",
        rank=1,
        headline="Backend Role",
        summary="Matches well.",
        skill_bullets=["Direct skill matches: Java, Spring, Quantum Computing"],
        experience_statement="Candidate meets requirement with 3.0 years of experience (requires 3.0 years).",
        logistics_statement="Compatible arrangement",
    )

    verifier = ExplanationVerifier()
    report = verifier.verify(adversarial_explanation, evidence)
    assert report.is_faithful is False
    assert any("Quantum Computing" in v for v in report.violations)


def test_adversarial_percentage_tampering_rejection() -> None:
    builder = EvidenceBuilder()
    candidate = {"resume_id": "res_adv2", "total_years": 2.0, "skills": ["HTML"]}
    job = {
        "job_id": "job_adv2",
        "title": "Web Developer",
        "skills": ["HTML", "CSS", "JavaScript", "TypeScript"],
        "required_years": 2.0,
    }
    # 1 out of 4 skills matches -> 25% overlap
    evidence = builder.build_evidence(
        candidate,
        job,
        score_info={"final_score": 0.40, "rank": 3},
        calibrated_probability=0.25,
    )

    # Adversarial explanation falsely boasts 95% match
    tampered_explanation = GeneratedExplanation(
        job_id="job_adv2",
        job_title="Web Developer",
        company="Company",
        rank=3,
        headline="Strong Match (95% skill overlap) driven by Semantic Relevance",
        summary="Summary statement.",
        skill_bullets=["Direct skill matches: HTML"],
        experience_statement="Candidate meets requirement with 2.0 years of experience (requires 2.0 years).",
        logistics_statement="Compatible arrangement",
        transparency_statement="Estimated Match Confidence: ~95% (provisional) | Rank #3 | Key Driver: Semantic Relevance.",
    )

    verifier = ExplanationVerifier()
    report = verifier.verify(tampered_explanation, evidence)
    assert report.is_faithful is False
    assert any("95%" in v for v in report.violations)


def test_strict_verification_raises_error() -> None:
    builder = EvidenceBuilder()
    evidence = builder.build_evidence(
        candidate_resume={
            "resume_id": "res_adv3",
            "total_years": 1.0,
            "skills": ["Python"],
        },
        job_posting={"job_id": "job_adv3", "title": "Developer", "skills": ["Python"]},
        score_info={"final_score": 0.70, "rank": 1},
    )

    mock_verifier = MagicMock()
    mock_verifier.verify.return_value = MagicMock(
        is_faithful=False, violations=["Hallucination detected"]
    )

    explainer = TemplateExplainer(verifier=mock_verifier)
    with pytest.raises(UnfaithfulExplanationError, match="failed strict verification"):
        explainer.explain(evidence, auto_verify=True, strict=True)


def test_evidence_builder_adversarial_malformed_inputs() -> None:
    builder = EvidenceBuilder()

    # Highly malformed input structures: nulls, integers, missing keys, irregular nested data
    candidate_malformed = {
        "resume_id": "res_bad",
        "total_years": None,
        "skills": [None, 123, {"unexpected_field": True}, "ValidSkill"],
        "preferences": None,
    }
    job_malformed = {
        "job_id": "job_bad",
        "title": None,
        "skills": None,
        "required_skills": ["ValidSkill"],
        "required_years": None,
        "location": None,
        "work_mode": None,
    }

    # Must safely build without unhandled exceptions
    evidence = builder.build_evidence(candidate_malformed, job_malformed)
    assert isinstance(evidence, ExplanationEvidence)
    assert evidence.experience.candidate_years == 0.0
    assert evidence.experience.required_years == 0.0
    assert evidence.scores.final_score == 0.0

    explainer = TemplateExplainer()
    explanation = explainer.explain(evidence, strict=True)
    assert isinstance(explanation, GeneratedExplanation)
    assert explanation.is_verified is True
