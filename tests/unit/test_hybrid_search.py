"""Unit tests for hybrid search and score fusion module."""

from unittest.mock import MagicMock

import numpy as np
import pytest

from src.retrieval.hybrid_search import (
    HybridSearchEngine,
    linear_score_fusion,
    min_max_normalize,
    reciprocal_rank_fusion,
)


def test_rrf_golden_calculation() -> None:
    rankings = {
        "bm25": ["doc_1", "doc_2", "doc_3"],
        "vector": ["doc_2", "doc_1", "doc_4"],
    }
    k = 60
    results = reciprocal_rank_fusion(rankings, k=k)

    res_dict = dict(results)

    # doc_1: 1/(60+1) + 1/(60+2) = 1/61 + 1/62
    expected_doc1 = (1.0 / 61.0) + (1.0 / 62.0)
    assert res_dict["doc_1"] == pytest.approx(expected_doc1)

    # doc_2: 1/(60+2) + 1/(60+1) = 1/62 + 1/61
    expected_doc2 = (1.0 / 62.0) + (1.0 / 61.0)
    assert res_dict["doc_2"] == pytest.approx(expected_doc2)

    # doc_3: 1/(60+3) = 1/63
    assert res_dict["doc_3"] == pytest.approx(1.0 / 63.0)

    # doc_4: 1/(60+3) = 1/63
    assert res_dict["doc_4"] == pytest.approx(1.0 / 63.0)

    # doc_1 and doc_2 must be ranked above doc_3 and doc_4
    assert res_dict["doc_1"] > res_dict["doc_3"]
    assert res_dict["doc_2"] > res_dict["doc_4"]


def test_min_max_normalize() -> None:
    raw = {"a": 10.0, "b": 20.0, "c": 30.0}
    norm = min_max_normalize(raw)
    assert norm["a"] == pytest.approx(0.0)
    assert norm["b"] == pytest.approx(0.5)
    assert norm["c"] == pytest.approx(1.0)

    # Single or constant score
    const_scores = {"x": 5.0, "y": 5.0}
    norm_const = min_max_normalize(const_scores)
    assert norm_const["x"] == pytest.approx(1.0)
    assert norm_const["y"] == pytest.approx(1.0)


def test_linear_score_fusion_golden() -> None:
    score_maps = {
        "bm25": {"doc_1": 10.0, "doc_2": 2.0},  # norm: doc_1=1.0, doc_2=0.0
        "vector": {"doc_1": 0.5, "doc_2": 0.9},  # norm: doc_1=0.0, doc_2=1.0
    }
    weights = {"bm25": 0.40, "vector": 0.60}

    fused = linear_score_fusion(score_maps, weights=weights)
    fused_dict = dict(fused)

    # doc_1: 0.40 * 1.0 + 0.60 * 0.0 = 0.40
    assert fused_dict["doc_1"] == pytest.approx(0.40)
    # doc_2: 0.40 * 0.0 + 0.60 * 1.0 = 0.60
    assert fused_dict["doc_2"] == pytest.approx(0.60)
    assert fused[0][0] == "doc_2"


def test_hybrid_search_engine_rrf_and_metadata() -> None:
    mock_bm25 = MagicMock()
    mock_bm25.search.return_value = [("job_a", 15.0), ("job_b", 8.0)]

    mock_vector_index = MagicMock()
    mock_vector_index.search.return_value = [("job_b", 0.95), ("job_a", 0.75)]

    mock_embedder = MagicMock()
    mock_embedder.encode_queries.return_value = np.zeros((1, 384), dtype=np.float32)

    engine = HybridSearchEngine(
        bm25_retriever=mock_bm25,
        vector_index=mock_vector_index,
        embedder=mock_embedder,
        rrf_k=60,
    )

    results = engine.search("python developer", top_k=2, mode="rrf")

    assert len(results) == 2
    # Verify metadata fields are populated
    for r in results:
        assert r.fusion_mode == "rrf"
        assert r.bm25_rank is not None
        assert r.vector_rank is not None
        assert r.bm25_score > 0.0
        assert r.vector_score > 0.0

    # Top result should be tied or highest RRF
    assert results[0].final_score >= results[1].final_score


def test_hybrid_search_engine_weighted_with_skills() -> None:
    mock_bm25 = MagicMock()
    mock_bm25.search.return_value = [("job_1", 10.0)]

    mock_vector_index = MagicMock()
    mock_vector_index.search.return_value = [("job_1", 0.88)]

    mock_embedder = MagicMock()
    mock_embedder.encode_queries.return_value = np.zeros((1, 384), dtype=np.float32)

    mock_skill_matcher = MagicMock()
    match_res = MagicMock()
    match_res.skill_score = 0.90
    mock_skill_matcher.match.return_value = match_res

    engine = HybridSearchEngine(
        bm25_retriever=mock_bm25,
        vector_index=mock_vector_index,
        embedder=mock_embedder,
        linear_weights={"bm25": 0.35, "vector": 0.45, "skill": 0.20},
        job_skills_lookup={"job_1": [{"skill_id": "sk_python", "required": True}]},
        skill_matcher=mock_skill_matcher,
    )

    results = engine.search(
        "python developer",
        candidate_skill_ids=["sk_python"],
        top_k=1,
        mode="weighted",
    )

    assert len(results) == 1
    res = results[0]
    assert res.fusion_mode == "weighted"
    assert res.skill_score == pytest.approx(0.90)
    assert res.job_id == "job_1"


def test_hybrid_search_engine_invalid_inputs() -> None:
    engine = HybridSearchEngine(
        bm25_retriever=MagicMock(),
        vector_index=MagicMock(),
        embedder=MagicMock(),
    )
    with pytest.raises(ValueError, match="Unsupported fusion mode"):
        engine.search("test", mode="invalid_mode")

    with pytest.raises(ValueError, match="k must be positive"):
        reciprocal_rank_fusion({}, k=0)
