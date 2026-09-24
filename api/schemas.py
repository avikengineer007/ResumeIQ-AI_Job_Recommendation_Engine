"""Pydantic v2 data transfer schemas for FastAPI endpoints.

Strict request/response validation matching Section 28 specifications.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# --- Health Schemas ---
class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "0.1.0"
    environment: str = "development"
    database_connected: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- Auth & User Schemas ---
class UserCreate(BaseModel):
    email: str = Field(
        ...,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        description="Valid email address",
    )
    password: str = Field(min_length=8, description="Argon2id secured password")
    full_name: str | None = None


class UserLogin(BaseModel):
    email: str = Field(
        ...,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        description="Valid email address",
    )
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str | None = None
    is_active: bool
    is_superuser: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: str | None = None
    email: str | None = None


# --- Resume Schemas ---
class ResumeCreate(BaseModel):
    raw_text: str = Field(description="Raw text content of the candidate resume")
    is_primary: bool = True


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    total_years_experience: float
    sections_json: dict[str, Any]
    is_primary: bool
    created_at: datetime


# --- Job Schemas ---
class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    company: str
    location: str | None = None
    work_mode: str = "remote"
    required_years_experience: float = 0.0
    description: str | None = None
    is_active: bool = True
    created_at: datetime


class JobSearchRequest(BaseModel):
    query: str = Field(default="", description="Search query string")
    location: str | None = None
    work_mode: str | None = None  # remote, hybrid, onsite
    min_years_experience: float | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# --- Recommendation Schemas ---
class RecommendationRequest(BaseModel):
    resume_id: uuid.UUID | None = None
    target_role: str | None = None
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_work_modes: list[str] = Field(default_factory=list)
    require_location: bool = False
    require_work_mode: bool = False
    top_k: int = Field(default=10, ge=1, le=50)


class RecommendationItemResponse(BaseModel):
    job_id: str
    title: str
    company: str
    location: str | None
    work_mode: str
    rank: int
    score: float
    calibrated_probability: float | None = None
    model_version: str = "hybrid-rerank-0.4"
    explanation: dict[str, Any] | None = None
    score_breakdown: dict[str, float] | None = None


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItemResponse]
    count: int
    model_version: str = "hybrid-rerank-0.4"
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# --- Feedback Schemas ---
class FeedbackCreate(BaseModel):
    job_id: str
    action: str = Field(
        description="User interaction: clicked, applied, dismissed, saved, thumbs_up, thumbs_down"
    )
    recommendation_id: int | None = None
    feedback_text: str | None = None


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: uuid.UUID
    job_id: str
    action: str
    feedback_text: str | None = None
    created_at: datetime
