"""Orchestration script for Phase 10 validation-split tuning & calibration.

Executes joint optimization across:
- Retrieval fusion weights (BM25, vector, skill) & RRF k
- Experience decay lambda & personalization weights
- Fits and serializes probability calibrator (safe JSON) on validation predictions
- Saves tuned parameters to configs/tuned_hyperparameters.json
"""

import json
from pathlib import Path

import pandas as pd

from src.embeddings.embedder import DenseEmbedder, EmbeddingManifest, format_job_text
from src.embeddings.faiss_index import FaissVectorIndex
from src.evaluation.optimizer import JointPipelineTuner
from src.reranking.cross_encoder import CrossEncoderReranker
from src.retrieval.bm25_retriever import BM25Retriever
from src.skill_normalization.skill_matcher import SkillMatcher
from src.skill_normalization.taxonomy import SkillTaxonomy


def run_validation_tuning(
    processed_dir: str | Path = "data/processed",
    eval_dir: str | Path = "data/evaluation",
    output_dir: str | Path = "configs",
    model_dir: str | Path = "models",
) -> None:
    p_dir = Path(processed_dir)
    e_dir = Path(eval_dir)
    out_dir = Path(output_dir)
    m_dir = Path(model_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    m_dir.mkdir(parents=True, exist_ok=True)

    print("Loading datasets and validation split...")
    with open(p_dir / "splits.json", encoding="utf-8") as f:
        splits = json.load(f)
    val_ids = set(splits["val_resume_ids"])

    jobs_df = pd.read_parquet(p_dir / "jobs.parquet")
    resumes_df = pd.read_parquet(p_dir / "resumes.parquet")

    jobs = jobs_df.to_dict(orient="records")
    val_resumes = resumes_df[resumes_df["resume_id"].isin(val_ids)].to_dict(
        orient="records"
    )

    with open(e_dir / "qrels_val.json", encoding="utf-8") as f:
        val_qrels = json.load(f)

    print(
        f"Loaded {len(jobs)} jobs, {len(val_resumes)} validation resumes, {len(val_qrels)} validation qrels."
    )

    # 1. Setup Taxonomy and Matcher
    tax = SkillTaxonomy.load_from_dir(p_dir)
    skill_matcher = SkillMatcher(taxonomy=tax)

    # 2. Setup BM25 Retriever
    bm25 = BM25Retriever()
    bm25.index_documents(jobs)

    # 3. Setup Vector Index with DenseEmbedder
    embedder = DenseEmbedder(
        manifest=EmbeddingManifest(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384,
            normalize_embeddings=True,
        )
    )
    job_texts = [format_job_text(j) for j in jobs]
    doc_vectors = embedder.encode_passages(job_texts)
    doc_ids = [str(j.get("job_id", j.get("id"))) for j in jobs]

    vector_index = FaissVectorIndex(dimension=384)
    vector_index.add_vectors(doc_vectors, doc_ids)

    # 4. Setup CrossEncoder Reranker
    reranker = CrossEncoderReranker(
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
    )

    # 5. Run Joint Pipeline Tuner
    print(
        "Running joint hyperparameter optimization across fusion and personalization spaces..."
    )
    tuner = JointPipelineTuner(
        bm25_retriever=bm25,
        vector_index=vector_index,
        embedder=embedder,
        skill_matcher=skill_matcher,
        reranker=reranker,
    )

    tuned_config, calibrator = tuner.tune(
        val_resumes=val_resumes,
        jobs=jobs,
        val_qrels=val_qrels,
    )

    # 6. Save Artifacts
    calibrator_path = m_dir / "calibrator.json"
    calibrator.save(calibrator_path)
    print(f"Saved calibrated probability model to -> {calibrator_path}")

    config_path = out_dir / "tuned_hyperparameters.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(tuned_config.to_dict(), f, indent=2)
    print(f"Saved tuned hyperparameters to -> {config_path}")

    print("\n=== Phase 10 Validation Tuning Results ===")
    print(f"Best Validation NDCG@10: {tuned_config.best_ndcg_at_10:.4f}")
    print(f"Best Validation MRR:     {tuned_config.best_mrr:.4f}")
    print(f"Optimal RRF k:           {tuned_config.rrf_k}")
    print(f"Optimal Fusion Weights:  {tuned_config.fusion_weights}")
    print(f"Optimal Exp Decay Lambda:{tuned_config.lambda_exp}")
    print(f"Calibrator Method:       {tuned_config.calibrator_method}")
    print(f"Calibrator Brier Score:  {tuned_config.calibrator_brier:.4f}")
    print(f"Calibrator ECE:          {tuned_config.calibrator_ece:.4f}")


if __name__ == "__main__":
    run_validation_tuning()
