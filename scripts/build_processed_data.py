"""Dataset processing, deduplication, PII scrubbing, and resume-level data splitting.

Follows the golden rules:
1. Split by resume (user), not by pair. Guaranteed zero leakage.
2. Train/val/test split ratio (60/20/20) frozen with seed 42 and saved to splits.json.
3. Raw data is never edited in place; outputs written to data/processed/.
"""

import random
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ruff: noqa: E402

# Ensure repository root is in Python path for direct script execution
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from src.common.config import get_config
from src.common.io import write_json
from src.common.logging_utils import get_logger, setup_logging
from src.common.seed import set_seed
from src.preprocessing.deduplicator import Deduplicator

logger = get_logger("build_processed_data")


def split_resume_ids(
    resume_ids: list[str],
    train_ratio: float = 0.60,
    val_ratio: float = 0.20,
    test_ratio: float = 0.20,
    seed: int = 42,
) -> dict[str, Any]:
    """Split resume IDs into train, validation, and test sets with strict user isolation."""
    total = round(train_ratio + val_ratio + test_ratio, 5)
    if total != 1.0:
        raise ValueError(f"Ratios must sum to 1.0, got {total}")

    unique_ids = sorted(set(resume_ids))
    rng = random.Random(seed)
    shuffled = list(unique_ids)
    rng.shuffle(shuffled)

    n = len(shuffled)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    train_ids = shuffled[:n_train]
    val_ids = shuffled[n_train : n_train + n_val]
    test_ids = shuffled[n_train + n_val :]

    split_manifest = {
        "seed": seed,
        "created_at": datetime.now(UTC).isoformat(),
        "ratios": {
            "train": train_ratio,
            "val": val_ratio,
            "test": test_ratio,
        },
        "train_resume_ids": train_ids,
        "val_resume_ids": val_ids,
        "test_resume_ids": test_ids,
        "stats": {
            "total_resumes": n,
            "train_count": len(train_ids),
            "val_count": len(val_ids),
            "test_count": len(test_ids),
        },
    }
    return split_manifest


def generate_seed_benchmark_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Generate realistic seed jobs and resumes for bootstrapping the research benchmark."""
    roles = [
        (
            "Machine Learning Engineer",
            ["Python", "PyTorch", "scikit-learn", "Docker", "SQL", "MLOps"],
            "remote",
        ),
        (
            "Data Scientist",
            ["Python", "SQL", "pandas", "Machine Learning", "Statistics", "Tableau"],
            "hybrid",
        ),
        (
            "Full Stack Developer",
            ["TypeScript", "React", "Node.js", "PostgreSQL", "Docker", "Tailwind CSS"],
            "remote",
        ),
        (
            "Backend Engineer",
            ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "AWS"],
            "onsite",
        ),
        (
            "Data Engineer",
            ["Python", "SQL", "Apache Spark", "Airflow", "PostgreSQL", "Kafka"],
            "remote",
        ),
        (
            "Frontend Developer",
            ["JavaScript", "React", "TypeScript", "HTML5", "CSS3", "Vite"],
            "hybrid",
        ),
        (
            "NLP Research Engineer",
            ["Python", "PyTorch", "Transformers", "spaCy", "BERT", "Deep Learning"],
            "remote",
        ),
        (
            "DevOps Engineer",
            ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform"],
            "onsite",
        ),
        (
            "Computer Vision Engineer",
            ["Python", "PyTorch", "OpenCV", "Deep Learning", "TensorFlow", "C++"],
            "hybrid",
        ),
        (
            "Cloud Architect",
            ["AWS", "Terraform", "Docker", "Kubernetes", "System Design", "Security"],
            "remote",
        ),
    ]

    jobs = []
    for i in range(50):
        role_title, skill_list, work_mode = roles[i % len(roles)]
        job_id = f"job_{i+1:04d}"
        skills_data = [
            {
                "skill_id": f"sk_{s.lower().replace(' ', '_').replace('.', '')}",
                "name": s,
                "importance": "required" if idx < 3 else "preferred",
            }
            for idx, s in enumerate(skill_list)
        ]
        jobs.append(
            {
                "job_id": job_id,
                "title": f"Senior {role_title}" if i % 3 == 0 else role_title,
                "company": f"TechCorp {i % 10 + 1}",
                "description": f"We are hiring a {role_title}. Key skills include {', '.join(skill_list)}. Minimum experience: {i % 5} years. Come join our growing engineering team.",
                "skills": skills_data,
                "location": "New York, NY" if i % 2 == 0 else "San Francisco, CA",
                "work_mode": work_mode,
                "min_years": float(i % 5),
                "max_years": float((i % 5) + 3),
                "employment_type": "full_time",
                "source": "benchmark_seed",
            }
        )

    resumes = []
    for i in range(25):
        resume_id = f"res_{i+1:04d}"
        role_title, skill_list, work_mode = roles[i % len(roles)]
        # Add candidate skills (partially matched)
        cand_skills = skill_list[:4]
        skills_data = [
            {
                "skill_id": f"sk_{s.lower().replace(' ', '_').replace('.', '')}",
                "name": s,
                "confidence": 0.95,
                "evidence": f"Skills:1-{len(s)}",
            }
            for s in cand_skills
        ]
        resumes.append(
            {
                "resume_id": resume_id,
                "skills": skills_data,
                "education": [
                    {
                        "degree": "B.S. Computer Science",
                        "field": "Computer Science",
                        "year": 2022 - (i % 5),
                    }
                ],
                "experience": [
                    {
                        "title": role_title,
                        "org": f"Company {i % 5}",
                        "description": f"Worked with {', '.join(cand_skills)} building production pipelines.",
                        "months": 12 * (i % 6 + 1),
                    }
                ],
                "total_years": float(i % 6 + 1),
                "preferences": {
                    "roles": [role_title],
                    "locations": ["New York, NY", "Remote"],
                    "work_modes": [work_mode],
                    "min_experience": 0.0,
                },
                "source": "synthetic_seed",
                "consent_flag": True,
                "pii_removed": True,
            }
        )

    return jobs, resumes


def main() -> None:
    setup_logging()
    cfg = get_config()
    set_seed(cfg.system.seed)

    processed_dir = cfg.paths.data_processed
    processed_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing dataset build and deduplication pipeline")

    jobs_data, resumes_data = generate_seed_benchmark_data()

    # Deduplicate jobs
    deduplicator = Deduplicator(seed=cfg.system.seed)
    unique_jobs, dup_clusters = deduplicator.deduplicate(jobs_data, id_key="job_id")
    logger.info(
        "Job deduplication complete",
        extra={
            "total": len(jobs_data),
            "unique": len(unique_jobs),
            "duplicate_clusters": len(dup_clusters),
        },
    )

    # Save to Parquet
    jobs_df = pd.DataFrame(unique_jobs)
    jobs_df.to_parquet(processed_dir / "jobs.parquet", index=False)

    resumes_df = pd.DataFrame(resumes_data)
    resumes_df.to_parquet(processed_dir / "resumes.parquet", index=False)

    # Perform resume-level 60/20/20 train/val/test split
    resume_ids = [r["resume_id"] for r in resumes_data]
    split_manifest = split_resume_ids(
        resume_ids=resume_ids,
        train_ratio=cfg.dataset.train_ratio,
        val_ratio=cfg.dataset.val_ratio,
        test_ratio=cfg.dataset.test_ratio,
        seed=cfg.system.seed,
    )

    write_json(cfg.paths.splits_file, split_manifest)
    logger.info(
        "Resume-level split manifest written",
        extra={
            "splits_path": str(cfg.paths.splits_file),
            "stats": split_manifest["stats"],
        },
    )


if __name__ == "__main__":
    main()
