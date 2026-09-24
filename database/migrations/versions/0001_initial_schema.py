"""Initial schema migration: 11 core tables with CASCADE rules and indexes.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 0. PostgreSQL Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # 1. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("idx_users_email", "users", ["email"])

    # 2. resumes
    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("cleaned_text", sa.Text(), nullable=True),
        sa.Column(
            "sections_json", postgresql.JSONB(), nullable=False, server_default="{}"
        ),
        sa.Column(
            "total_years_experience",
            sa.Numeric(4, 1),
            nullable=False,
            server_default="0.0",
        ),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("idx_resumes_user_id", "resumes", ["user_id"])

    # 3. skills
    op.create_table(
        "skills",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("category", sa.String(128), nullable=True),
        sa.Column(
            "parent_skill_id",
            sa.String(128),
            sa.ForeignKey("skills.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("idx_skills_name", "skills", ["name"])
    op.create_index("idx_skills_category", "skills", ["category"])

    # 4. jobs
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("work_mode", sa.String(32), nullable=False, server_default="remote"),
        sa.Column(
            "required_years_experience",
            sa.Numeric(4, 1),
            nullable=False,
            server_default="0.0",
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("raw_json", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("idx_jobs_title", "jobs", ["title"])
    op.create_index("idx_jobs_is_active_work_mode", "jobs", ["is_active", "work_mode"])

    # 5. job_skills
    op.create_table(
        "job_skills",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "job_id",
            sa.String(128),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "skill_id",
            sa.String(128),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "importance", sa.String(32), nullable=False, server_default="required"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
    )
    op.create_index("idx_job_skills_job_id", "job_skills", ["job_id"])
    op.create_index("idx_job_skills_skill_id", "job_skills", ["skill_id"])

    # 6. resume_skills
    op.create_table(
        "resume_skills",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "resume_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resumes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "skill_id",
            sa.String(128),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "proficiency", sa.String(32), nullable=True, server_default="intermediate"
        ),
        sa.Column("source_section", sa.String(64), nullable=True),
        sa.Column(
            "confidence", sa.Numeric(4, 3), nullable=False, server_default="1.000"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("resume_id", "skill_id", name="uq_resume_skill"),
    )
    op.create_index("idx_resume_skills_resume_id", "resume_skills", ["resume_id"])
    op.create_index("idx_resume_skills_skill_id", "resume_skills", ["skill_id"])

    # 7. user_preferences
    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("target_role", sa.String(255), nullable=True),
        sa.Column(
            "preferred_locations",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "preferred_work_modes",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("min_salary", sa.Numeric(12, 2), nullable=True),
        sa.Column(
            "require_location", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "require_work_mode", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("idx_user_preferences_user_id", "user_preferences", ["user_id"])

    # 8. search_history
    op.create_table(
        "search_history",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("query_text", sa.Text(), nullable=True),
        sa.Column(
            "filters_applied", postgresql.JSONB(), nullable=False, server_default="{}"
        ),
        sa.Column("results_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "idx_search_history_user_created",
        "search_history",
        ["user_id", sa.text("created_at DESC")],
    )

    # 9. recommendations
    op.create_table(
        "recommendations",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "resume_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("resumes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            sa.String(128),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "model_version",
            sa.String(64),
            nullable=False,
            server_default="hybrid-rerank-0.4",
        ),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("score", sa.Numeric(6, 4), nullable=False),
        sa.Column("calibrated_probability", sa.Numeric(6, 4), nullable=True),
        sa.Column(
            "explanation_json", postgresql.JSONB(), nullable=False, server_default="{}"
        ),
        sa.Column(
            "scores_breakdown_json",
            postgresql.JSONB(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "idx_recommendations_user_created",
        "recommendations",
        ["user_id", sa.text("created_at DESC")],
    )
    op.create_index("idx_recommendations_job_id", "recommendations", ["job_id"])

    # 10. feedback
    op.create_table(
        "feedback",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            sa.String(128),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "recommendation_id",
            sa.BigInteger(),
            sa.ForeignKey("recommendations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("idx_feedback_user_job", "feedback", ["user_id", "job_id"])

    # 11. saved_jobs
    op.create_table(
        "saved_jobs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            sa.String(128),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("user_id", "job_id", name="uq_user_saved_job"),
    )
    op.create_index("idx_saved_jobs_user_id", "saved_jobs", ["user_id"])


def downgrade() -> None:
    op.drop_table("saved_jobs")
    op.drop_table("feedback")
    op.drop_table("recommendations")
    op.drop_table("search_history")
    op.drop_table("user_preferences")
    op.drop_table("resume_skills")
    op.drop_table("job_skills")
    op.drop_table("jobs")
    op.drop_table("skills")
    op.drop_table("resumes")
    op.drop_table("users")
