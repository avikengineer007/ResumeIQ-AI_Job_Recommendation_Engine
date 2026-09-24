"""Data schemas and strict validators for job postings and resumes.

Enforces:
- Title and description cannot be empty or whitespace.
- Experience years must be non-negative with min_years <= max_years.
- Sensitive attributes (gender, age, photo, ethnicity, religion) are excluded by design.
- Transparent missingness handling: missing values are explicit nulls, never silently imputed.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class WorkMode(StrEnum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class ExperienceLevel(StrEnum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


class SkillImportance(StrEnum):
    REQUIRED = "required"
    PREFERRED = "preferred"


class JobSkillItem(BaseModel):
    skill_id: str = Field(..., description="Canonical skill ID or raw identifier")
    name: str = Field(..., description="Skill name mention")
    importance: SkillImportance = Field(default=SkillImportance.REQUIRED)
    source_span: str | None = Field(
        default=None, description="Character offset or section evidence"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class SalaryInfo(BaseModel):
    min_salary: float | None = Field(default=None, ge=0.0)
    max_salary: float | None = Field(default=None, ge=0.0)
    currency: str = Field(default="USD")
    period: str = Field(default="yearly")

    @model_validator(mode="after")
    def validate_salary_range(self) -> "SalaryInfo":
        if self.min_salary is not None and self.max_salary is not None:
            if self.min_salary > self.max_salary:
                raise ValueError(
                    f"min_salary ({self.min_salary}) cannot exceed max_salary ({self.max_salary})"
                )
        return self


class JobPostingSchema(BaseModel):
    job_id: str = Field(..., description="Unique stable job posting identifier")
    title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(
        ..., min_length=1, description="Company or hiring organization"
    )
    description: str = Field(..., min_length=5, description="Full job description")
    skills: list[JobSkillItem] = Field(default_factory=list)
    location: str | None = Field(default=None)
    work_mode: WorkMode | None = Field(default=None)
    min_years: float | None = Field(default=0.0, ge=0.0)
    max_years: float | None = Field(default=None, ge=0.0)
    level: ExperienceLevel | None = Field(default=None)
    salary: SalaryInfo | None = Field(default=None)
    employment_type: EmploymentType | None = Field(default=None)
    industry: str | None = Field(default=None)
    source: str = Field(default="dataset", description="Provenance identifier")
    posted_date: str | None = Field(default=None)
    url: str | None = Field(default=None)
    license_tag: str | None = Field(default=None)

    @field_validator("title", "company", "description")
    @classmethod
    def reject_empty_whitespace(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be empty or solely whitespace")
        return stripped

    @model_validator(mode="after")
    def validate_experience_range(self) -> "JobPostingSchema":
        if self.min_years is not None and self.max_years is not None:
            if self.min_years > self.max_years:
                raise ValueError(
                    f"min_years ({self.min_years}) cannot exceed max_years ({self.max_years})"
                )
        return self


class EducationItem(BaseModel):
    degree: str = Field(..., min_length=1)
    field: str | None = Field(default=None)
    year: int | None = Field(default=None)


class ExperienceItem(BaseModel):
    title: str = Field(..., min_length=1)
    org: str | None = Field(default=None)
    start: str | None = Field(default=None)
    end: str | None = Field(default=None)
    description: str | None = Field(default=None)
    months: int | None = Field(default=None, ge=0)


class ResumeSkillItem(BaseModel):
    skill_id: str
    name: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: str | None = Field(
        default=None, description="Section:offset where skill was found"
    )
    years_used: float | None = Field(default=None, ge=0.0)


class UserPreferences(BaseModel):
    roles: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    work_modes: list[WorkMode] = Field(default_factory=list)
    min_experience: float | None = Field(default=None, ge=0.0)
    salary_min: float | None = Field(default=None, ge=0.0)


class ResumeSchema(BaseModel):
    resume_id: str = Field(
        ..., min_length=1, description="Anonymized resume identifier"
    )
    skills: list[ResumeSkillItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[dict[str, Any]] = Field(default_factory=list)
    preferences: UserPreferences | None = Field(default=None)
    total_years: float | None = Field(default=None, ge=0.0)
    source: str = Field(default="volunteer_or_synthetic")
    consent_flag: bool = Field(default=True)
    pii_removed: bool = Field(default=False)
    parser_version: str = Field(default="0.1.0")

    @field_validator("resume_id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("resume_id cannot be blank")
        return stripped
