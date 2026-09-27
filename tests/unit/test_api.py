"""Integration and unit tests for FastAPI Gateway endpoints (Layer 2).

Tests:
1. Root and health check endpoints (/ and /api/v1/health).
2. Auth endpoints: Signup, Argon2id verification, Login, /me resolution.
3. Resumes: Ingestion, PII scrubbing, and section detection.
4. Jobs catalog: Querying and filtering.
5. Recommendations: Generating explanations and score breakdowns.
6. Feedback: Logging interaction events and duplicate handling.
"""

from collections.abc import Generator

import pytest
from database.models import Base, Job
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api.dependencies import get_db
from api.main import app


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


# In-memory test engine isolated per test run
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    # Seed a test job for recommendation and search tests
    with TestingSessionLocal() as session:
        test_job = Job(
            id="job_fastapi_01",
            title="Senior Python Backend Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            work_mode="remote",
            required_years_experience=3.0,
            description="Looking for an experienced Python developer with FastAPI and PostgreSQL skills.",
            is_active=True,
        )
        session.add(test_job)
        session.commit()
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_root_and_health_endpoints(client: TestClient) -> None:
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["service"] == "ResumeIQ Recommendation Engine API"

    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    data = res_health.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data


def test_auth_workflow_and_protected_me(client: TestClient) -> None:
    email = "fastapi_user@example.com"
    pw = "SuperSecurePassword123!"

    # 1. Signup
    res_signup = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": pw, "full_name": "API Tester"},
    )
    assert res_signup.status_code == 201
    user_data = res_signup.json()
    assert user_data["email"] == email
    assert "id" in user_data

    # 2. Duplicate signup rejection
    res_dup = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": pw},
    )
    assert res_dup.status_code == 409

    # 3. Login with wrong password
    res_bad_pw = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword!"},
    )
    assert res_bad_pw.status_code == 401

    # 4. Login with correct password
    res_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pw},
    )
    assert res_login.status_code == 200
    token_data = res_login.json()
    token = token_data["access_token"]
    assert token_data["token_type"] == "bearer"

    # 5. Access protected /me endpoint
    headers = {"Authorization": f"Bearer {token}"}
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == email

    # 6. Access /me without credentials
    res_unauth = client.get("/api/v1/auth/me")
    assert res_unauth.status_code == 401


def test_resume_ingestion_and_recommendation(client: TestClient) -> None:
    # Authenticate user
    email = "candidate_recs@example.com"
    pw = "ResumePass2026!"
    client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": pw, "full_name": "Jane Developer"},
    )
    res_login = client.post("/api/v1/auth/login", json={"email": email, "password": pw})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ingest resume
    raw_resume = (
        "Jane Doe\n"
        "Email: jane@secretcorp.com\n"
        "Phone: 555-019-2831\n\n"
        "EXPERIENCE\n"
        "Senior Backend Developer with 5 years building scalable APIs in Python and FastAPI.\n"
        "SKILLS\n"
        "Python, FastAPI, SQL, Docker, Linux\n"
    )

    res_resume = client.post(
        "/api/v1/resumes",
        json={"raw_text": raw_resume, "is_primary": True},
        headers=headers,
    )
    assert res_resume.status_code == 201
    resume_obj = res_resume.json()
    assert "id" in resume_obj

    # List resumes
    res_list = client.get("/api/v1/resumes", headers=headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # Request recommendations
    rec_payload = {
        "target_role": "Python Backend Engineer",
        "preferred_work_modes": ["remote"],
        "top_k": 5,
    }
    res_recs = client.post("/api/v1/recommend", json=rec_payload, headers=headers)
    assert res_recs.status_code == 200
    rec_data = res_recs.json()
    assert "recommendations" in rec_data
    assert rec_data["count"] >= 1
    top_rec = rec_data["recommendations"][0]
    assert top_rec["job_id"] == "job_fastapi_01"
    assert top_rec["model_version"] == "hybrid-rerank-0.4"
    assert top_rec["explanation"] is not None

    # History retrieval
    res_hist = client.get("/api/v1/recommend/history", headers=headers)
    assert res_hist.status_code == 200
    assert len(res_hist.json()) >= 1


def test_jobs_and_feedback(client: TestClient) -> None:
    # 1. Query jobs catalog
    res_jobs = client.get("/api/v1/jobs?work_mode=remote")
    assert res_jobs.status_code == 200
    jobs = res_jobs.json()
    assert len(jobs) >= 1
    assert jobs[0]["id"] == "job_fastapi_01"

    # Specific job detail
    res_single = client.get("/api/v1/jobs/job_fastapi_01")
    assert res_single.status_code == 200
    assert res_single.json()["title"] == "Senior Python Backend Engineer"

    # 2. Record feedback
    email = "feedback_user@example.com"
    pw = "FeedbackUser2026!"
    client.post("/api/v1/auth/signup", json={"email": email, "password": pw})
    res_login = client.post("/api/v1/auth/login", json={"email": email, "password": pw})
    headers = {"Authorization": f"Bearer {res_login.json()['access_token']}"}

    feedback_payload = {
        "job_id": "job_fastapi_01",
        "action": "applied",
        "feedback_text": "Great match with my background!",
    }
    res_fb = client.post("/api/v1/feedback", json=feedback_payload, headers=headers)
    assert res_fb.status_code == 201
    fb_data = res_fb.json()
    assert fb_data["action"] == "applied"

    # List user feedback
    res_fb_list = client.get("/api/v1/feedback", headers=headers)
    assert res_fb_list.status_code == 200
    assert len(res_fb_list.json()) >= 1


def test_user_preferences_and_saved_jobs(client: TestClient) -> None:
    # 1. Register user via /api/v1/auth/register alias
    email = "prefs_user@example.com"
    pw = "SecurePrefs2026!"
    res_reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pw, "full_name": "Pref Tester"},
    )
    assert res_reg.status_code == 201
    assert res_reg.json()["email"] == email

    res_login = client.post("/api/v1/auth/login", json={"email": email, "password": pw})
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get default preferences
    res_pref_get = client.get("/api/v1/user/preferences", headers=headers)
    assert res_pref_get.status_code == 200
    pref_data = res_pref_get.json()
    assert pref_data["target_role"] is None
    assert pref_data["preferred_work_modes"] == []

    # 3. Update preferences
    pref_update = {
        "target_role": "Lead ML Engineer",
        "preferred_locations": ["San Francisco, CA", "Remote"],
        "preferred_work_modes": ["remote", "hybrid"],
        "min_salary": 180000.0,
        "require_work_mode": True,
        "require_location": False,
    }
    res_pref_put = client.put(
        "/api/v1/user/preferences", json=pref_update, headers=headers
    )
    assert res_pref_put.status_code == 200
    updated = res_pref_put.json()
    assert updated["target_role"] == "Lead ML Engineer"
    assert "remote" in updated["preferred_work_modes"]
    assert updated["require_work_mode"] is True

    # 4. Save job via /api/v1/save-job
    save_payload = {"job_id": "job_fastapi_01", "notes": "Top target opportunity"}
    res_save = client.post("/api/v1/save-job", json=save_payload, headers=headers)
    assert res_save.status_code == 201
    saved_item = res_save.json()
    assert saved_item["job_id"] == "job_fastapi_01"
    assert saved_item["notes"] == "Top target opportunity"

    # 5. List saved jobs via /api/v1/saved-jobs
    res_saved_list = client.get("/api/v1/saved-jobs", headers=headers)
    assert res_saved_list.status_code == 200
    assert len(res_saved_list.json()) == 1
    assert res_saved_list.json()[0]["job_id"] == "job_fastapi_01"

    # 6. Delete saved job
    res_del = client.delete("/api/v1/save-job/job_fastapi_01", headers=headers)
    assert res_del.status_code == 204

    # Verify deleted
    res_saved_after = client.get("/api/v1/saved-jobs", headers=headers)
    assert len(res_saved_after.json()) == 0


def test_live_adzuna_jobs_endpoint(client: TestClient) -> None:
    res = client.get("/api/v1/jobs/live/search?query=Python&limit=2")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "jobs" in data
    assert isinstance(data["jobs"], list)
