"""SQLAlchemy 2.0 Declarative ORM models for ResumeIQ.

Implements all 11 core tables with strict foreign key constraints (ON DELETE CASCADE),
relationship declarations, and indexing.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

AutoBigInt = BigInteger().with_variant(Integer, "sqlite")


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    # Relationships
    resumes: Mapped[list["Resume"]] = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
    preferences: Mapped["UserPreference | None"] = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    searches: Mapped[list["SearchHistory"]] = relationship(
        "SearchHistory", back_populates="user", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="user", cascade="all, delete-orphan"
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="user", cascade="all, delete-orphan"
    )
    saved_jobs: Mapped[list["SavedJob"]] = relationship(
        "SavedJob", back_populates="user", cascade="all, delete-orphan"
    )


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    cleaned_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    sections_json: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False, server_default="{}"
    )
    total_years_experience: Mapped[float] = mapped_column(
        Numeric(4, 1), default=0.0, nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resumes")
    skills: Mapped[list["ResumeSkill"]] = relationship(
        "ResumeSkill", back_populates="resume", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="resume", cascade="all, delete-orphan"
    )


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    category: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    parent_skill_id: Mapped[str | None] = mapped_column(
        String(128), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )

    # Relationships
    parent_skill: Mapped["Skill | None"] = relationship(
        "Skill", remote_side=[id], backref="child_skills"
    )
    job_skills: Mapped[list["JobSkill"]] = relationship(
        "JobSkill", back_populates="skill", cascade="all, delete-orphan"
    )
    resume_skills: Mapped[list["ResumeSkill"]] = relationship(
        "ResumeSkill", back_populates="skill", cascade="all, delete-orphan"
    )


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    work_mode: Mapped[str] = mapped_column(
        String(32), default="remote", nullable=False
    )  # remote, hybrid, onsite
    required_years_experience: Mapped[float] = mapped_column(
        Numeric(4, 1), default=0.0, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_json: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False, server_default="{}"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    __table_args__ = (Index("idx_jobs_is_active_work_mode", "is_active", "work_mode"),)

    # Relationships
    skills: Mapped[list["JobSkill"]] = relationship(
        "JobSkill", back_populates="job", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="job", cascade="all, delete-orphan"
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="job", cascade="all, delete-orphan"
    )
    saved_by: Mapped[list["SavedJob"]] = relationship(
        "SavedJob", back_populates="job", cascade="all, delete-orphan"
    )


class JobSkill(Base):
    __tablename__ = "job_skills"

    id: Mapped[int] = mapped_column(AutoBigInt, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    importance: Mapped[str] = mapped_column(
        String(32), default="required", nullable=False
    )  # required, preferred, bonus
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )

    __table_args__ = (UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="job_skills")


class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id: Mapped[int] = mapped_column(AutoBigInt, primary_key=True, autoincrement=True)
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    proficiency: Mapped[str | None] = mapped_column(
        String(32), default="intermediate", nullable=True
    )
    source_section: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float] = mapped_column(
        Numeric(4, 3), default=1.000, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("resume_id", "skill_id", name="uq_resume_skill"),
    )

    # Relationships
    resume: Mapped["Resume"] = relationship("Resume", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="resume_skills")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    target_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferred_locations: Mapped[list] = mapped_column(
        JSONB, default=list, nullable=False, server_default="[]"
    )
    preferred_work_modes: Mapped[list] = mapped_column(
        JSONB, default=list, nullable=False, server_default="[]"
    )
    min_salary: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    require_location: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    require_work_mode: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preferences")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(AutoBigInt, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    filters_applied: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False, server_default="{}"
    )
    results_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )

    __table_args__ = (
        Index("idx_search_history_user_created", "user_id", created_at.desc()),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="searches")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(AutoBigInt, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_version: Mapped[str] = mapped_column(
        String(64), default="hybrid-rerank-0.4", nullable=False
    )
    rank: Mapped[int] = mapped_column(nullable=False)
    score: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    calibrated_probability: Mapped[float | None] = mapped_column(
        Numeric(6, 4), nullable=True
    )
    explanation_json: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False, server_default="{}"
    )
    scores_breakdown_json: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )

    __table_args__ = (
        Index("idx_recommendations_user_created", "user_id", created_at.desc()),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="recommendations")
    resume: Mapped["Resume"] = relationship("Resume", back_populates="recommendations")
    job: Mapped["Job"] = relationship("Job", back_populates="recommendations")
    feedback: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="recommendation"
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(AutoBigInt, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recommendation_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("recommendations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # clicked, applied, dismissed, saved, thumbs_up, thumbs_down
    feedback_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )

    __table_args__ = (Index("idx_feedback_user_job", "user_id", "job_id"),)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="feedback")
    job: Mapped["Job"] = relationship("Job", back_populates="feedback")
    recommendation: Mapped["Recommendation | None"] = relationship(
        "Recommendation", back_populates="feedback"
    )


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id: Mapped[int] = mapped_column(AutoBigInt, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_saved_job"),
        Index("idx_saved_jobs_user_id", "user_id"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="saved_jobs")
    job: Mapped["Job"] = relationship("Job", back_populates="saved_by")
