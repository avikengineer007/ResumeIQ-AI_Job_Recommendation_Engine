"""Recommendation engine router providing personalized job matching and explainability."""

from database.connection import get_db
from database.models import Job, Recommendation, Resume, User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from api.schemas import (
    RecommendationItemResponse,
    RecommendationRequest,
    RecommendationResponse,
)
from src.explainability.evidence import EvidenceBuilder
from src.explainability.templates import TemplateExplainer
from src.recommendation.personalization import (
    CandidatePreferences,
    PersonalizedScorer,
)

router = APIRouter(prefix="/recommend", tags=["Recommendations"])


@router.post("", response_model=RecommendationResponse)
def get_recommendations(
    req: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    """Generate personalized job recommendations with evidence-grounded explanations."""
    # 1. Resolve candidate resume
    resume: Resume | None = None
    if req.resume_id:
        resume = db.scalar(
            select(Resume).where(
                Resume.id == req.resume_id, Resume.user_id == current_user.id
            )
        )
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specified resume not found.",
            )
    else:
        # Fallback to primary resume or most recent
        resume = db.scalar(
            select(Resume)
            .where(Resume.user_id == current_user.id, Resume.is_primary.is_(True))
            .order_by(Resume.created_at.desc())
        )
        if not resume:
            resume = db.scalar(
                select(Resume)
                .where(Resume.user_id == current_user.id)
                .order_by(Resume.created_at.desc())
            )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no uploaded resumes. Please upload a resume before requesting recommendations.",
        )

    # 2. Fetch candidate jobs from DB
    jobs = list(db.scalars(select(Job).where(Job.is_active.is_(True))).all())
    if not jobs:
        return RecommendationResponse(recommendations=[], count=0)

    # Convert to candidate dictionaries for scorer
    candidates_data = []
    job_map = {}
    for j in jobs:
        j_skills = (
            [s.skill_id for s in j.skills] if hasattr(j, "skills") and j.skills else []
        )
        j_dict = {
            "job_id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location or "Remote",
            "work_mode": j.work_mode,
            "required_years": float(j.required_years_experience or 0.0),
            "skills": j_skills,
            "rerank_score": 0.80,  # Baseline score for direct DB candidates
            "vector_score": 0.75,
            "skill_score": 0.70,
        }
        candidates_data.append(j_dict)
        job_map[j.id] = j

    # 3. Apply Personalized Scoring & Hard Constraints
    preferences = CandidatePreferences(
        target_role=req.target_role or "",
        years_of_experience=float(resume.total_years_experience or 0.0),
        candidate_skills=[s.skill_id for s in resume.skills] if resume.skills else [],
        preferred_locations=req.preferred_locations,
        preferred_work_modes=req.preferred_work_modes,
        require_location=req.require_location,
        require_work_mode=req.require_work_mode,
    )

    scorer = PersonalizedScorer()
    scored_results = scorer.score_candidates(
        candidates_data, preferences, top_k=req.top_k
    )

    # 4. Generate Explanations & Persist Recommendations
    evidence_builder = EvidenceBuilder()
    explainer = TemplateExplainer()

    items: list[RecommendationItemResponse] = []
    candidate_resume_dict = {
        "resume_id": str(resume.id),
        "total_years": float(resume.total_years_experience or 0.0),
        "skills": preferences.candidate_skills,
        "preferences": {
            "role": preferences.target_role,
            "locations": preferences.preferred_locations,
            "work_modes": preferences.preferred_work_modes,
        },
    }

    for ranked_item in scored_results:
        raw_job = job_map[ranked_item.job_id]
        job_dict = {
            "job_id": raw_job.id,
            "title": raw_job.title,
            "company": raw_job.company,
            "location": raw_job.location or "Remote",
            "work_mode": raw_job.work_mode,
            "required_years": float(raw_job.required_years_experience or 0.0),
            "skills": [s.skill_id for s in raw_job.skills] if raw_job.skills else [],
        }

        # Build verifiable evidence
        evidence = evidence_builder.build_evidence(
            candidate_resume=candidate_resume_dict,
            job_posting=job_dict,
            score_info=ranked_item,
            preferences=preferences,
            calibrated_probability=0.75,  # Provisional placeholder confidence
        )

        # Generate verified explanation
        explanation = explainer.explain(evidence, auto_verify=True, strict=False)

        score_breakdown = {
            "rerank_score": ranked_item.s_rerank,
            "semantic_score": ranked_item.s_sem,
            "skill_score": ranked_item.s_skill,
            "experience_score": ranked_item.s_exp,
            "role_score": ranked_item.s_role,
            "location_score": ranked_item.s_loc,
            "work_mode_score": ranked_item.s_mode,
        }

        # Persist Recommendation row
        rec_row = Recommendation(
            user_id=current_user.id,
            resume_id=resume.id,
            job_id=raw_job.id,
            model_version="hybrid-rerank-0.4",
            rank=ranked_item.rank,
            score=round(ranked_item.final_score, 4),
            calibrated_probability=0.75,
            explanation_json=explanation.to_dict(),
            scores_breakdown_json=score_breakdown,
        )
        db.add(rec_row)

        items.append(
            RecommendationItemResponse(
                job_id=raw_job.id,
                title=raw_job.title,
                company=raw_job.company,
                location=raw_job.location,
                work_mode=raw_job.work_mode,
                rank=ranked_item.rank,
                score=round(ranked_item.final_score, 4),
                calibrated_probability=0.75,
                model_version="hybrid-rerank-0.4",
                explanation=explanation.to_dict(),
                score_breakdown=score_breakdown,
            )
        )

    db.commit()

    return RecommendationResponse(
        recommendations=items,
        count=len(items),
        model_version="hybrid-rerank-0.4",
    )


@router.get("/history", response_model=list[RecommendationItemResponse])
def get_recommendation_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RecommendationItemResponse]:
    """Retrieve historical recommendations generated for the authenticated user."""
    recs = list(
        db.scalars(
            select(Recommendation)
            .where(Recommendation.user_id == current_user.id)
            .order_by(Recommendation.created_at.desc())
            .limit(limit)
        ).all()
    )

    items = []
    for r in recs:
        j = r.job
        items.append(
            RecommendationItemResponse(
                job_id=r.job_id,
                title=j.title if j else "Job Position",
                company=j.company if j else "Company",
                location=j.location if j else None,
                work_mode=j.work_mode if j else "remote",
                rank=r.rank,
                score=float(r.score),
                calibrated_probability=(
                    float(r.calibrated_probability)
                    if r.calibrated_probability is not None
                    else None
                ),
                model_version=r.model_version,
                explanation=r.explanation_json,
                score_breakdown=r.scores_breakdown_json,
            )
        )
    return items
