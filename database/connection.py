"""Database connection engine and session management.

Provides SQLAlchemy engine, session maker, and FastAPI get_db dependency.
"""

import os
from collections.abc import Generator
from pathlib import Path

import pandas as pd
from database.models import Base, Job
from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


# Environment-driven database connection URL with default fallback
DEFAULT_DATABASE_URL = (
    "postgresql://app:change_this_in_production_password@localhost:5432/jobs"
)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def _create_engine_instance(url: str):
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


try:
    engine = _create_engine_instance(DATABASE_URL)
    if DATABASE_URL.startswith("postgresql"):
        with engine.connect() as conn:
            pass
except Exception:
    # Gracefully fall back to local sqlite when PostgreSQL daemon is not running locally
    DATABASE_URL = "sqlite:///./resumeiq.db"
    engine = _create_engine_instance(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(engine_instance=None) -> None:
    """Create all database tables using declarative Base metadata and seed initial jobs if empty."""
    target_engine = engine_instance or engine
    Base.metadata.create_all(bind=target_engine)

    # Seed baseline jobs if jobs table is empty and processed parquet exists
    try:
        local_session = sessionmaker(bind=target_engine)()
        job_count = local_session.scalar(select(func.count(Job.id)))
        if job_count == 0 and os.path.exists("data/processed/jobs.parquet"):
            df = pd.read_parquet("data/processed/jobs.parquet")
            for _, row in df.iterrows():
                skills_list = (
                    row["skills"]
                    if isinstance(row["skills"], list)
                    else list(row["skills"])
                )
                job = Job(
                    id=str(row["job_id"]),
                    title=str(row["title"]),
                    company=str(row["company"]),
                    location=(
                        str(row["location"]) if pd.notna(row["location"]) else "Remote"
                    ),
                    work_mode=str(row.get("work_mode", "remote")).lower(),
                    required_years_experience=float(row.get("min_years", 2.0) or 2.0),
                    description=str(row.get("description", "")),
                    raw_json={
                        "skills": skills_list,
                        "employment_type": str(row.get("employment_type", "full-time")),
                    },
                    is_active=True,
                )
                local_session.add(job)
            local_session.commit()
        local_session.close()
    except Exception:
        pass


def execute_schema_sql(
    schema_path: str | Path = "database/schema.sql", engine_instance=None
) -> None:
    """Execute raw schema.sql script directly on the database engine."""
    from sqlalchemy import text

    target_engine = engine_instance or engine
    with open(schema_path, encoding="utf-8") as f:
        sql = f.read()

    with target_engine.connect() as conn:
        with conn.begin():
            conn.execute(text(sql))
