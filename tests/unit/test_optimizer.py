"""Unit tests for JointPipelineTuner and hyperparameter optimization."""

from unittest.mock import MagicMock

import numpy as np

from src.evaluation.optimizer import JointPipelineTuner, TunedPipelineConfig


def test_joint_tuner_optimization_and_calibration() -> None:
    # 1. Mock components
    mock_bm25 = MagicMock()
    mock_bm25.search.return_value = [("job_1", 10.0), ("job_2", 5.0)]

    mock_vector = MagicMock()
    mock_vector.search.return_value = [("job_1", 0.9), ("job_2", 0.6)]

    mock_embedder = MagicMock()
    mock_embedder.encode_queries.return_value = np.zeros((1, 384), dtype=np.float32)

    mock_matcher = MagicMock()

    mock_reranker = MagicMock()
    mock_res_1 = MagicMock()
    mock_res_1.job_id = "job_1"
    mock_res_1.rerank_score = 4.0
    mock_res_2 = MagicMock()
    mock_res_2.job_id = "job_2"
    mock_res_2.rerank_score = 1.0
    mock_reranker.rerank.return_value = [mock_res_1, mock_res_2]

    tuner = JointPipelineTuner(
        bm25_retriever=mock_bm25,
        vector_index=mock_vector,
        embedder=mock_embedder,
        skill_matcher=mock_matcher,
        reranker=mock_reranker,
    )

    val_resumes = [
        {
            "resume_id": "val_res_01",
            "experience": "Senior Python developer",
            "skills": ["Python"],
            "total_years": 5.0,
            "preferences": {"role": "Python Developer"},
        }
    ]
    jobs = [
        {"job_id": "job_1", "title": "Python Developer", "required_years": 4.0},
        {"job_id": "job_2", "title": "Frontend Engineer", "required_years": 2.0},
    ]
    val_qrels = {"val_res_01": {"job_1": 3.0, "job_2": 0.0}}

    fusion_candidates = [
        {"mode": "rrf", "rrf_k": 40, "weights": None},
        {"mode": "rrf", "rrf_k": 60, "weights": None},
    ]
    personalization_candidates = [
        {
            "lambda_exp": 0.35,
            "weights": {
                "s_rerank": 0.40,
                "s_sem": 0.20,
                "s_skill": 0.20,
                "s_exp": 0.10,
                "s_role": 0.05,
                "s_loc": 0.025,
                "s_mode": 0.025,
            },
        }
    ]

    tuned_cfg, calibrator = tuner.tune(
        val_resumes=val_resumes,
        jobs=jobs,
        val_qrels=val_qrels,
        fusion_candidates=fusion_candidates,
        personalization_candidates=personalization_candidates,
        top_candidates_pool=2,
    )

    assert isinstance(tuned_cfg, TunedPipelineConfig)
    assert tuned_cfg.best_ndcg_at_10 >= 0.0
    assert tuned_cfg.rrf_k in [40, 60]
    assert calibrator.is_fit is True
