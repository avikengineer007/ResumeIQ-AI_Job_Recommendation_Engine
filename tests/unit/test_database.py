"""Unit tests for Database Schema, SQLAlchemy ORM models, and migration integrity.

Verifies:
1. database/schema.sql integrity (all 11 tables, ON DELETE CASCADE, GIN indexes).
2. All 11 canonical tables exist in Base.metadata (when SQLAlchemy is available).
3. Strict ON DELETE CASCADE enforcement across all child relationships.
4. ON DELETE SET NULL on nullable self-referential / soft references.
5. Unique constraints on junction and account tables.
"""

import re
from pathlib import Path

import pytest

EXPECTED_TABLES = {
    "users",
    "resumes",
    "skills",
    "jobs",
    "job_skills",
    "resume_skills",
    "user_preferences",
    "search_history",
    "recommendations",
    "feedback",
    "saved_jobs",
}


def test_schema_sql_file_integrity() -> None:
    """Validate canonical schema.sql contains all 11 tables, foreign keys, and indexes."""
    schema_path = Path("database/schema.sql")
    assert schema_path.exists(), "database/schema.sql must exist"

    sql = schema_path.read_text(encoding="utf-8")

    # Check that all 11 CREATE TABLE statements exist
    for table in EXPECTED_TABLES:
        pattern = rf"CREATE TABLE IF NOT EXISTS {table}\b"
        assert re.search(
            pattern, sql, re.IGNORECASE
        ), f"CREATE TABLE {table} missing from schema.sql"

    # Check CASCADE count across all foreign keys
    cascade_matches = re.findall(r"ON DELETE CASCADE", sql, re.IGNORECASE)
    assert (
        len(cascade_matches) >= 14
    ), f"Found only {len(cascade_matches)} ON DELETE CASCADE in schema.sql"

    # Check SET NULL on optional foreign keys
    set_null_matches = re.findall(r"ON DELETE SET NULL", sql, re.IGNORECASE)
    assert (
        len(set_null_matches) >= 2
    ), "Expected ON DELETE SET NULL for parent_skill_id and recommendation_id"

    # Check GIN indexes for JSONB columns
    gin_matches = re.findall(r"USING gin", sql, re.IGNORECASE)
    assert (
        len(gin_matches) >= 4
    ), f"Found only {len(gin_matches)} GIN indexes in schema.sql"

    # Check Unique Constraints
    assert "uq_job_skill" in sql
    assert "uq_resume_skill" in sql
    assert "uq_user_saved_job" in sql


def test_all_11_tables_registered_in_metadata() -> None:
    pytest.importorskip(
        "sqlalchemy", reason="SQLAlchemy not installed in current environment"
    )
    from database.models import Base

    registered_tables = set(Base.metadata.tables.keys())
    assert EXPECTED_TABLES.issubset(registered_tables)
    assert len(EXPECTED_TABLES) == 11


def test_foreign_key_cascade_delete_rules() -> None:
    """Every child table referencing user, resume, or job MUST specify ON DELETE CASCADE."""
    pytest.importorskip(
        "sqlalchemy", reason="SQLAlchemy not installed in current environment"
    )
    from database.models import Base

    cascade_targets = [
        ("resumes", "users.id"),
        ("job_skills", "jobs.id"),
        ("job_skills", "skills.id"),
        ("resume_skills", "resumes.id"),
        ("resume_skills", "skills.id"),
        ("user_preferences", "users.id"),
        ("search_history", "users.id"),
        ("recommendations", "users.id"),
        ("recommendations", "resumes.id"),
        ("recommendations", "jobs.id"),
        ("feedback", "users.id"),
        ("feedback", "jobs.id"),
        ("saved_jobs", "users.id"),
        ("saved_jobs", "jobs.id"),
    ]

    for table_name, target in cascade_targets:
        table = Base.metadata.tables[table_name]
        matching_fks = [
            fk
            for fk in table.foreign_keys
            if f"{fk.column.table.name}.{fk.column.name}" == target
        ]
        assert (
            len(matching_fks) > 0
        ), f"Missing foreign key from {table_name} to {target}"
        for fk in matching_fks:
            assert fk.ondelete == "CASCADE", (
                f"Foreign key {table_name} -> {target} has ondelete='{fk.ondelete}', "
                f"expected 'CASCADE'"
            )


def test_nullable_foreign_key_set_null_rules() -> None:
    """Self-referential or optional foreign keys must use SET NULL."""
    pytest.importorskip(
        "sqlalchemy", reason="SQLAlchemy not installed in current environment"
    )
    from database.models import Base

    # skills.parent_skill_id -> skills.id
    skills_table = Base.metadata.tables["skills"]
    parent_fk = [
        fk for fk in skills_table.foreign_keys if fk.column.table.name == "skills"
    ][0]
    assert parent_fk.ondelete == "SET NULL"

    # feedback.recommendation_id -> recommendations.id
    feedback_table = Base.metadata.tables["feedback"]
    rec_fk = [
        fk
        for fk in feedback_table.foreign_keys
        if fk.column.table.name == "recommendations"
    ][0]
    assert rec_fk.ondelete == "SET NULL"


def test_unique_constraints() -> None:
    pytest.importorskip(
        "sqlalchemy", reason="SQLAlchemy not installed in current environment"
    )
    from database.models import Base
    from sqlalchemy import UniqueConstraint

    # 1. job_skills (job_id, skill_id)
    js_table = Base.metadata.tables["job_skills"]
    js_uqs = [c for c in js_table.constraints if isinstance(c, UniqueConstraint)]
    assert any(
        {"job_id", "skill_id"} == {col.name for col in uq.columns} for uq in js_uqs
    )

    # 2. resume_skills (resume_id, skill_id)
    rs_table = Base.metadata.tables["resume_skills"]
    rs_uqs = [c for c in rs_table.constraints if isinstance(c, UniqueConstraint)]
    assert any(
        {"resume_id", "skill_id"} == {col.name for col in uq.columns} for uq in rs_uqs
    )

    # 3. saved_jobs (user_id, job_id)
    sj_table = Base.metadata.tables["saved_jobs"]
    sj_uqs = [c for c in sj_table.constraints if isinstance(c, UniqueConstraint)]
    assert any(
        {"user_id", "job_id"} == {col.name for col in uq.columns} for uq in sj_uqs
    )


def test_indexes_present_on_foreign_keys_and_filters() -> None:
    pytest.importorskip(
        "sqlalchemy", reason="SQLAlchemy not installed in current environment"
    )
    from database.models import Base

    for table_name in EXPECTED_TABLES:
        table = Base.metadata.tables[table_name]
        indexed_cols = set()
        for idx in table.indexes:
            for col in idx.columns:
                indexed_cols.add(col.name)

        if "user_id" in table.c:
            assert "user_id" in indexed_cols or table.c.user_id.index is True
