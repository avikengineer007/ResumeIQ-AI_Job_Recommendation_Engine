"""Unit tests for JobLoader, ResumeLoader, and resume-level split isolation."""

import json
from pathlib import Path

from scripts.build_processed_data import split_resume_ids

from src.ingestion.job_loader import JobLoader
from src.ingestion.resume_loader import ResumeLoader


def test_resume_level_split_isolation():
    """Verify resume-level 60/20/20 splitting guarantees zero leakage across splits."""
    ids = [f"resume_{i:03d}" for i in range(100)]
    manifest = split_resume_ids(
        ids, train_ratio=0.60, val_ratio=0.20, test_ratio=0.20, seed=42
    )

    train_set = set(manifest["train_resume_ids"])
    val_set = set(manifest["val_resume_ids"])
    test_set = set(manifest["test_resume_ids"])

    # Strict partition check: zero overlap
    assert len(train_set.intersection(val_set)) == 0
    assert len(train_set.intersection(test_set)) == 0
    assert len(val_set.intersection(test_set)) == 0

    # Counts match ratios
    assert len(train_set) == 60
    assert len(val_set) == 20
    assert len(test_set) == 20
    assert manifest["seed"] == 42


def test_resume_split_reproducibility():
    """Verify split with identical seed generates identical sets."""
    ids = [f"resume_{i:03d}" for i in range(50)]
    split_a = split_resume_ids(ids, seed=42)
    split_b = split_resume_ids(ids, seed=42)
    assert split_a["train_resume_ids"] == split_b["train_resume_ids"]
    assert split_a["val_resume_ids"] == split_b["val_resume_ids"]
    assert split_a["test_resume_ids"] == split_b["test_resume_ids"]


def test_job_loader_with_json(tmp_path: Path):
    """Verify JobLoader loads, validates, and generates missingness profile."""
    jobs_file = tmp_path / "jobs.json"
    data = [
        {
            "job_id": "job_1",
            "title": "Backend Python Engineer",
            "company": "DataCorp",
            "description": "Building FastAPI services with PostgreSQL and Redis.",
            "location": "Remote",
            "work_mode": "remote",
            "min_years": 2.0,
        },
        {
            "job_id": "job_2",
            "title": "   ",  # Invalid empty title
            "company": "DataCorp",
            "description": "Short",
        },
    ]
    with open(jobs_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    loader = JobLoader()
    valid_jobs, report = loader.load_and_validate(jobs_file)

    assert len(valid_jobs) == 1
    assert valid_jobs[0].job_id == "job_1"
    assert report.total_records == 2
    assert report.valid_records == 1
    assert report.invalid_records == 1


def test_resume_loader_with_pii_scrubbing(tmp_path: Path):
    """Verify ResumeLoader masks PII in raw text and validates schemas."""
    resumes_file = tmp_path / "resumes.jsonl"
    record = {
        "resume_id": "res_100",
        "raw_text": "Alex Smith, reachable at alex@smith.org or 555-123-4567. 4 years of Python experience.",
        "skills": [{"skill_id": "sk_python", "name": "Python"}],
        "education": [{"degree": "B.Tech Computer Science"}],
        "total_years": 4.0,
    }
    with open(resumes_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    loader = ResumeLoader()
    valid_resumes, report = loader.load_and_validate(resumes_file, mask_pii=True)

    assert len(valid_resumes) == 1
    assert valid_resumes[0].resume_id == "res_100"
    assert valid_resumes[0].pii_removed is True
    assert report.pii_redacted_count >= 2
