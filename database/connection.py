"""Database connection engine and session management.

Provides SQLAlchemy engine, session maker, and FastAPI get_db dependency.
"""

import os
from collections.abc import Generator
from pathlib import Path

from database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Environment-driven database connection URL with default fallback
DEFAULT_DATABASE_URL = (
    "postgresql://app:change_this_in_production_password@localhost:5432/jobs"
)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Configure connection engine
# Use pool_pre_ping to automatically reconnect on stale connections
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(engine_instance=None) -> None:
    """Create all database tables using declarative Base metadata."""
    target_engine = engine_instance or engine
    Base.metadata.create_all(bind=target_engine)


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
