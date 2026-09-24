"""Unit tests for JobPostingSchema and ResumeSchema validators."""

import pytest
from pydantic import ValidationError

from src.ingestion.validators import (
    EmploymentType,
    ExperienceLevel,
    JobPostingSchema,
    ResumeSchema,
    SalaryInfo,
    WorkMode,
)


def test_valid_job_posting():
    """Verify that a well-formed job posting passes validation."""
    job = JobPostingSchema(
        job_id="job_001",
        title="Machine Learning Engineer",
        company="Tech Corp",
        description="We need an ML engineer with Python and PyTorch experience.",
        location="Remote",
        work_mode=WorkMode.REMOTE,
        min_years=2.0,
        max_years=5.0,
        level=ExperienceLevel.MID,
        employment_type=EmploymentType.FULL_TIME,
    )
    assert job.job_id == "job_001"
    assert job.min_years == 2.0
    assert job.max_years == 5.0


def test_job_posting_rejects_empty_whitespace():
    """Verify that empty strings or whitespace-only fields are rejected."""
    with pytest.raises(ValidationError):
        JobPostingSchema(
            job_id="job_002",
            title="   ",
            company="Tech Corp",
            description="Valid description here",
        )

    with pytest.raises(ValidationError):
        JobPostingSchema(
            job_id="job_003",
            title="Valid Title",
            company="   ",
            description="Valid description here",
        )


def test_job_posting_invalid_experience_range():
    """Verify min_years > max_years triggers validation error."""
    with pytest.raises(ValidationError):
        JobPostingSchema(
            job_id="job_004",
            title="Staff Engineer",
            company="Tech Corp",
            description="Engineering role with deep systems experience.",
            min_years=8.0,
            max_years=4.0,  # min > max should fail
        )


def test_salary_info_validation():
    """Verify salary range validation."""
    valid_salary = SalaryInfo(min_salary=100000, max_salary=150000)
    assert valid_salary.min_salary == 100000

    with pytest.raises(ValidationError):
        SalaryInfo(min_salary=200000, max_salary=150000)


def test_valid_resume_schema():
    """Verify standard resume schema parsing."""
    resume = ResumeSchema(
        resume_id="res_001",
        education=[{"degree": "B.S. Computer Science", "year": 2021}],
        experience=[{"title": "Software Engineer", "months": 24}],
        total_years=2.0,
        consent_flag=True,
    )
    assert resume.resume_id == "res_001"
    assert len(resume.education) == 1
    assert resume.total_years == 2.0


def test_resume_rejects_blank_id():
    """Verify resume_id cannot be blank."""
    with pytest.raises(ValidationError):
        ResumeSchema(resume_id="  ")
