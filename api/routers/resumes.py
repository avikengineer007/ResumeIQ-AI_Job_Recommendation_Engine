"""Resume ingestion, parsing, and management router."""

import uuid

from database.connection import get_db
from database.models import Resume, User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from api.schemas import ResumeCreate, ResumeResponse
from src.pii.anonymizer import PIIAnonymizer
from src.preprocessing.section_detector import SectionDetector

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def create_resume(
    resume_in: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    """Ingest resume text, redact PII, detect sections, and persist record."""
    if not resume_in.raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text cannot be empty.",
        )

    # 1. PII Scrubbing
    anonymizer = PIIAnonymizer()
    cleaned_text, _ = anonymizer.anonymize(resume_in.raw_text)

    # 2. Section Detection
    detector = SectionDetector()
    detected_sections = detector.detect_sections(cleaned_text)
    sections_dict = {sec.section_type.value: sec.text for sec in detected_sections}

    # If this resume is set as primary, unmark existing primary resumes for user
    if resume_in.is_primary:
        existing_resumes = db.scalars(
            select(Resume).where(Resume.user_id == current_user.id)
        ).all()
        for r in existing_resumes:
            r.is_primary = False

    resume = Resume(
        id=uuid.uuid4(),
        user_id=current_user.id,
        raw_text=resume_in.raw_text,
        cleaned_text=cleaned_text,
        sections_json=sections_dict,
        total_years_experience=0.0,
        is_primary=resume_in.is_primary,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=list[ResumeResponse])
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Resume]:
    """Retrieve all resumes owned by the authenticated user."""
    return list(
        db.scalars(
            select(Resume)
            .where(Resume.user_id == current_user.id)
            .order_by(Resume.created_at.desc())
        ).all()
    )


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    """Retrieve a specific resume by ID."""
    resume = db.scalar(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )
    return resume
