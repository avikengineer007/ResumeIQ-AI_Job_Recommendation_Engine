"""Job postings search and catalog router."""

from database.connection import get_db
from database.models import Job
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.schemas import JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=list[JobResponse])
def list_jobs(
    work_mode: str | None = Query(
        None, description="Filter by work mode: remote, hybrid, onsite"
    ),
    location: str | None = Query(None, description="Filter by location keyword"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Job]:
    """List active jobs with optional filtering by work mode and location."""
    stmt = select(Job).where(Job.is_active.is_(True))

    if work_mode:
        stmt = stmt.where(Job.work_mode == work_mode.lower().strip())
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location.strip()}%"))

    stmt = stmt.order_by(Job.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> Job:
    """Retrieve details for a specific job posting."""
    job = db.scalar(select(Job).where(Job.id == job_id))
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
    return job
