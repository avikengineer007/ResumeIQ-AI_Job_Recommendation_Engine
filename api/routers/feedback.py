"""User interaction and feedback router for implicit/explicit signal collection."""

from database.connection import get_db
from database.models import Feedback, Job, User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from api.schemas import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["Feedback"])

VALID_ACTIONS = {
    "clicked",
    "applied",
    "dismissed",
    "saved",
    "thumbs_up",
    "thumbs_down",
}


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def record_feedback(
    feedback_in: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Feedback:
    """Record an interaction or explicit feedback action on a job recommendation."""
    action_norm = feedback_in.action.lower().strip()
    if action_norm not in VALID_ACTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{feedback_in.action}'. Must be one of: {', '.join(sorted(VALID_ACTIONS))}",
        )

    # Verify job exists
    job = db.scalar(select(Job).where(Job.id == feedback_in.job_id))
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{feedback_in.job_id}' not found.",
        )

    feedback = Feedback(
        user_id=current_user.id,
        job_id=feedback_in.job_id,
        recommendation_id=feedback_in.recommendation_id,
        action=action_norm,
        feedback_text=feedback_in.feedback_text,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("", response_model=list[FeedbackResponse])
def get_user_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Feedback]:
    """Retrieve all interaction events logged by the authenticated user."""
    return list(
        db.scalars(
            select(Feedback)
            .where(Feedback.user_id == current_user.id)
            .order_by(Feedback.created_at.desc())
        ).all()
    )
