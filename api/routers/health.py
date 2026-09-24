"""Health check router for monitoring and container orchestration."""

from database.connection import get_db
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)) -> HealthResponse:
    """Return health status and verify database connectivity."""
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        version="0.1.0",
        environment="development",
        database_connected=db_ok,
    )
