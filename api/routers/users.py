"""User preferences and saved jobs endpoints matching Phase 10 API specifications."""

from datetime import UTC, datetime

from database.connection import get_db
from database.models import Job, SavedJob, User, UserPreference
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from api.schemas import (
    SavedJobCreate,
    SavedJobResponse,
    UserPreferenceResponse,
    UserPreferenceUpdate,
)

router = APIRouter(tags=["User & Preferences"])


# --- User Preferences Endpoints ---
@router.get("/user/preferences", response_model=UserPreferenceResponse)
def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPreferenceResponse:
    """Retrieve personal career preferences for the authenticated candidate."""
    pref = db.scalar(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    if not pref:
        # Return default preferences if not yet configured
        return UserPreferenceResponse(
            user_id=current_user.id,
            target_role=None,
            preferred_locations=[],
            preferred_work_modes=[],
            min_salary=None,
            require_work_mode=False,
            require_location=False,
            updated_at=datetime.now(UTC),
        )
    return UserPreferenceResponse.model_validate(pref)


@router.put("/user/preferences", response_model=UserPreferenceResponse)
@router.post("/user/preferences", response_model=UserPreferenceResponse)
def update_user_preferences(
    pref_in: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPreferenceResponse:
    """Create or update career preferences and strict recommendation filters."""
    pref = db.scalar(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    now = datetime.now(UTC)
    if pref:
        pref.target_role = pref_in.target_role
        pref.preferred_locations = pref_in.preferred_locations
        pref.preferred_work_modes = pref_in.preferred_work_modes
        pref.min_salary = pref_in.min_salary
        pref.require_work_mode = pref_in.require_work_mode
        pref.require_location = pref_in.require_location
        pref.updated_at = now
    else:
        pref = UserPreference(
            user_id=current_user.id,
            target_role=pref_in.target_role,
            preferred_locations=pref_in.preferred_locations,
            preferred_work_modes=pref_in.preferred_work_modes,
            min_salary=pref_in.min_salary,
            require_work_mode=pref_in.require_work_mode,
            require_location=pref_in.require_location,
            created_at=now,
            updated_at=now,
        )
        db.add(pref)

    db.commit()
    db.refresh(pref)
    return UserPreferenceResponse.model_validate(pref)


# --- Saved Jobs Endpoints ---
@router.post(
    "/save-job", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED
)
def save_job(
    payload: SavedJobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedJobResponse:
    """Bookmark or save a job posting for the authenticated candidate."""
    # Verify job existence
    job = db.scalar(select(Job).where(Job.id == payload.job_id))
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{payload.job_id}' not found.",
        )

    saved = db.scalar(
        select(SavedJob).where(
            SavedJob.user_id == current_user.id, SavedJob.job_id == payload.job_id
        )
    )
    if saved:
        saved.notes = payload.notes
    else:
        saved = SavedJob(
            user_id=current_user.id,
            job_id=payload.job_id,
            notes=payload.notes,
            created_at=datetime.now(UTC),
        )
        db.add(saved)

    db.commit()
    db.refresh(saved)
    return SavedJobResponse.model_validate(saved)


@router.get("/saved-jobs", response_model=list[SavedJobResponse])
def list_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SavedJob]:
    """Retrieve all bookmarked jobs for the current user."""
    stmt = (
        select(SavedJob)
        .where(SavedJob.user_id == current_user.id)
        .order_by(SavedJob.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.delete("/save-job/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_saved_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Remove a previously bookmarked job."""
    saved = db.scalar(
        select(SavedJob).where(
            SavedJob.user_id == current_user.id, SavedJob.job_id == job_id
        )
    )
    if saved:
        db.delete(saved)
        db.commit()
