"""Generate initial validation benchmark relevance labels (qrels_val.json).

PROVISIONAL / PLACEHOLDER SCRIPT:
Note: This script generates synthetic qrels via deterministic Jaccard skill overlap.
Because the downstream ranking pipeline also heavily weights skill overlap, using these
labels creates circular evaluation leakage (mechanically yielding near-perfect NDCG/MRR).
TODO(Phase 17): Replace these synthetic labels with real multi-annotator judgements
collected via pooling + blind annotation across an expanded validation set (50-100 resumes)
before running formal research benchmarks.
"""

import json
from pathlib import Path

import pandas as pd


def _extract_skill_ids(skills_obj) -> set[str]:
    if skills_obj is None:
        return set()
    if hasattr(skills_obj, "tolist"):
        skills_obj = skills_obj.tolist()
    if isinstance(skills_obj, str):
        skills_obj = [s.strip() for s in skills_obj.split(",")]
    s_ids = set()
    for item in skills_obj:
        if isinstance(item, dict):
            s_id = item.get("skill_id") or item.get("name", "")
            if s_id:
                s_ids.add(str(s_id))
        elif hasattr(item, "skill_id"):
            s_ids.add(str(item.skill_id))
        elif isinstance(item, str) and item.strip():
            s_ids.add(item.strip())
    return s_ids


def generate_validation_qrels(
    data_dir: str | Path = "data/processed",
) -> dict[str, dict[str, float]]:
    data_path = Path(data_dir)
    splits_file = data_path / "splits.json"
    resumes_file = data_path / "resumes.parquet"
    jobs_file = data_path / "jobs.parquet"

    with open(splits_file, encoding="utf-8") as f:
        splits = json.load(f)
    val_resume_ids = set(splits["val_resume_ids"])

    resumes_df = pd.read_parquet(resumes_file)
    jobs_df = pd.read_parquet(jobs_file)

    val_resumes = resumes_df[resumes_df["resume_id"].isin(val_resume_ids)]

    qrels: dict[str, dict[str, float]] = {}

    for _, r in val_resumes.iterrows():
        r_id = str(r["resume_id"])
        r_skills = _extract_skill_ids(r["skills"])

        qrels[r_id] = {}

        for _, j in jobs_df.iterrows():
            j_id = str(j["job_id"])
            j_skills = _extract_skill_ids(j["skills"])

            if not j_skills or not r_skills:
                continue

            overlap = len(r_skills.intersection(j_skills))
            jaccard = overlap / float(len(j_skills))

            if jaccard >= 0.50:
                qrels[r_id][j_id] = 3.0
            elif jaccard >= 0.30:
                qrels[r_id][j_id] = 2.0
            elif jaccard >= 0.15:
                qrels[r_id][j_id] = 1.0

    out_file = Path("data/evaluation/qrels_val.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(qrels, f, indent=2)

    print(
        f"Generated validation qrels for {len(qrels)} validation resumes -> {out_file}"
    )
    return qrels


if __name__ == "__main__":
    generate_validation_qrels()
