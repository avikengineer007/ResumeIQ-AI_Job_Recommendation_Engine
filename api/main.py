"""FastAPI Application Entrypoint for ResumeIQ Recommendation Engine (Layer 2).

Integrates all API routers, CORS middleware, OpenAPI documentation, and lifecycle events.
"""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from database.connection import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import (
    auth,
    feedback,
    health,
    jobs,
    recommendations,
    resumes,
)

# Allowed CORS origins
allowed_origins_raw = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
)
origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifespan context."""
    # Attempt graceful metadata initialization if not running in production migration mode
    try:
        init_db()
    except Exception:
        pass
    yield


app = FastAPI(
    title="ResumeIQ Recommendation Engine API",
    description="Skill-Aware Semantic Job Search and Personalized Recommendation System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root_endpoint() -> dict[str, str]:
    """API root endpoint returning system overview and documentation link."""
    return {
        "service": "ResumeIQ Recommendation Engine API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
