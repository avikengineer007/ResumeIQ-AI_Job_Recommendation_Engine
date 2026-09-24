"""Unit tests for the IR & Recommendation evaluation metrics module.

Covers:
- Precision@K
- Recall@K
- F1@K
- HitRate@K
- MRR (Mean Reciprocal Rank)
- NDCG@K (with exponential gain 2^rel - 1)
- Binary and graded relevance
- Perfect rankings, zero overlap, empty inputs, edge cases
- Dataset macro-averaging
"""

import math

import pytest

from src.evaluation.metrics import (
    dcg_at_k,
    evaluate_ranking_dataset,
    evaluate_single_query,
    f1_at_k,
    hit_rate_at_k,
    mrr,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


def test_precision_at_k_golden() -> None:
    retrieved = ["job_1", "job_2", "job_3", "job_4", "job_5"]
    relevant = {"job_2", "job_4", "job_6"}

    # k=1: ["job_1"] -> 0/1 = 0.0
    assert precision_at_k(retrieved, relevant, k=1) == pytest.approx(0.0)

    # k=2: ["job_1", "job_2"] -> 1/2 = 0.5
    assert precision_at_k(retrieved, relevant, k=2) == pytest.approx(0.5)

    # k=5: ["job_1", "job_2", "job_3", "job_4", "job_5"] -> 2/5 = 0.4
    assert precision_at_k(retrieved, relevant, k=5) == pytest.approx(0.4)


def test_recall_at_k_golden() -> None:
    retrieved = ["job_1", "job_2", "job_3", "job_4", "job_5"]
    relevant = {"job_2", "job_4", "job_6"}  # 3 relevant items total

    # k=1: 0 hits / 3 = 0.0
    assert recall_at_k(retrieved, relevant, k=1) == pytest.approx(0.0)

    # k=2: 1 hit / 3 = 1/3
    assert recall_at_k(retrieved, relevant, k=2) == pytest.approx(1.0 / 3.0)

    # k=5: 2 hits / 3 = 2/3
    assert recall_at_k(retrieved, relevant, k=5) == pytest.approx(2.0 / 3.0)


def test_f1_at_k_golden() -> None:
    retrieved = ["job_1", "job_2", "job_3", "job_4", "job_5"]
    relevant = {"job_2", "job_4", "job_6"}

    # At k=2: P=0.5, R=1/3 -> F1 = 2 * (0.5 * (1/3)) / (0.5 + 1/3) = (1/3) / (5/6) = 2/5 = 0.4
    assert f1_at_k(retrieved, relevant, k=2) == pytest.approx(0.4)

    # Zero hits: P=0, R=0 -> F1=0
    assert f1_at_k(retrieved, relevant, k=1) == pytest.approx(0.0)


def test_hit_rate_at_k_golden() -> None:
    retrieved = ["job_1", "job_2", "job_3", "job_4", "job_5"]
    relevant = {"job_2", "job_4", "job_6"}

    # k=1: job_1 not relevant -> 0.0
    assert hit_rate_at_k(retrieved, relevant, k=1) == pytest.approx(0.0)

    # k=2: job_2 is relevant -> 1.0
    assert hit_rate_at_k(retrieved, relevant, k=2) == pytest.approx(1.0)


def test_mrr_golden() -> None:
    retrieved = ["job_1", "job_2", "job_3", "job_4", "job_5"]
    relevant = {"job_2", "job_4", "job_6"}

    # First relevant item is job_2 at position 2 -> 1/2 = 0.5
    assert mrr(retrieved, relevant) == pytest.approx(0.5)

    # With cutoff k=1: first item is not relevant -> 0.0
    assert mrr(retrieved, relevant, k=1) == pytest.approx(0.0)

    # Immediate first hit
    assert mrr(["job_2", "job_1"], relevant) == pytest.approx(1.0)


def test_ndcg_at_k_binary_exponential_gain() -> None:
    """Validate NDCG@K using standard exponential gain (2^rel - 1) / log2(i + 1)."""
    retrieved = ["job_1", "job_2", "job_3", "job_4", "job_5"]
    relevant = {"job_2", "job_4", "job_6"}

    # Calculation for k=5:
    # Actual DCG@5:
    # rank 2: (2^1 - 1) / log2(3) = 1.0 / 1.58496250072 = 0.63092975357
    # rank 4: (2^1 - 1) / log2(5) = 1.0 / 2.32192809489 = 0.43067655807
    # DCG@5 = 0.63092975357 + 0.43067655807 = 1.06160631164
    expected_dcg = (1.0 / math.log2(3)) + (1.0 / math.log2(5))
    assert dcg_at_k(retrieved, relevant, k=5) == pytest.approx(expected_dcg)

    # Ideal IDCG@5: top 3 relevant items at ranks 1, 2, 3:
    # rank 1: 1.0 / log2(2) = 1.0
    # rank 2: 1.0 / log2(3) = 0.63092975357
    # rank 3: 1.0 / log2(4) = 0.50
    # IDCG@5 = 1.0 + (1.0 / log2(3)) + 0.50 = 2.13092975357
    expected_idcg = 1.0 + (1.0 / math.log2(3)) + 0.50

    expected_ndcg = expected_dcg / expected_idcg
    assert ndcg_at_k(retrieved, relevant, k=5) == pytest.approx(expected_ndcg)


def test_ndcg_at_k_graded_relevance() -> None:
    """Validate graded relevance (0, 1, 2, 3) where relevance is passed as a dict."""
    rel_map = {"job_1": 3.0, "job_2": 1.0, "job_3": 2.0}
    retrieved = ["job_2", "job_1", "job_3"]

    # DCG@3:
    # rank 1: (2^1 - 1) / log2(2) = 1.0 / 1.0 = 1.0
    # rank 2: (2^3 - 1) / log2(3) = 7.0 / 1.5849625 = 4.416508
    # rank 3: (2^2 - 1) / log2(4) = 3.0 / 2.0 = 1.5
    # DCG = 1.0 + 4.416508 + 1.5 = 6.916508
    dcg = dcg_at_k(retrieved, rel_map, k=3)
    expected_dcg = 1.0 + (7.0 / math.log2(3)) + (3.0 / math.log2(4))
    assert dcg == pytest.approx(expected_dcg)

    # Ideal IDCG@3: scores sorted [3.0, 2.0, 1.0]
    # rank 1: (2^3 - 1) / log2(2) = 7.0
    # rank 2: (2^2 - 1) / log2(3) = 3.0 / log2(3) = 1.892789
    # rank 3: (2^1 - 1) / log2(4) = 1.0 / 2.0 = 0.5
    expected_idcg = 7.0 + (3.0 / math.log2(3)) + 0.50
    expected_ndcg = expected_dcg / expected_idcg
    assert ndcg_at_k(retrieved, rel_map, k=3) == pytest.approx(expected_ndcg)


def test_perfect_ranking() -> None:
    """When ranking is already ideal, NDCG must be exactly 1.0."""
    relevant = {"job_a", "job_b", "job_c"}
    retrieved = ["job_a", "job_b", "job_c", "job_d", "job_e"]

    assert ndcg_at_k(retrieved, relevant, k=3) == pytest.approx(1.0)
    assert precision_at_k(retrieved, relevant, k=3) == pytest.approx(1.0)
    assert recall_at_k(retrieved, relevant, k=3) == pytest.approx(1.0)
    assert f1_at_k(retrieved, relevant, k=3) == pytest.approx(1.0)
    assert hit_rate_at_k(retrieved, relevant, k=3) == pytest.approx(1.0)
    assert mrr(retrieved, relevant) == pytest.approx(1.0)


def test_empty_and_zero_overlap_edge_cases() -> None:
    # Empty retrieved
    assert precision_at_k([], {"job_1"}, k=5) == 0.0
    assert recall_at_k([], {"job_1"}, k=5) == 0.0
    assert f1_at_k([], {"job_1"}, k=5) == 0.0
    assert hit_rate_at_k([], {"job_1"}, k=5) == 0.0
    assert mrr([], {"job_1"}) == 0.0
    assert ndcg_at_k([], {"job_1"}, k=5) == 0.0

    # Empty relevant
    assert precision_at_k(["job_1"], set(), k=5) == 0.0
    assert recall_at_k(["job_1"], set(), k=5) == 0.0
    assert f1_at_k(["job_1"], set(), k=5) == 0.0
    assert hit_rate_at_k(["job_1"], set(), k=5) == 0.0
    assert mrr(["job_1"], set()) == 0.0
    assert ndcg_at_k(["job_1"], set(), k=5) == 0.0

    # No overlap
    assert precision_at_k(["job_1", "job_2"], {"job_3"}, k=2) == 0.0
    assert recall_at_k(["job_1", "job_2"], {"job_3"}, k=2) == 0.0
    assert mrr(["job_1", "job_2"], {"job_3"}) == 0.0
    assert ndcg_at_k(["job_1", "job_2"], {"job_3"}, k=2) == 0.0

    # Invalid k
    with pytest.raises(ValueError):
        precision_at_k(["job_1"], {"job_1"}, k=0)
    with pytest.raises(ValueError):
        recall_at_k(["job_1"], {"job_1"}, k=-1)
    with pytest.raises(ValueError):
        ndcg_at_k(["job_1"], {"job_1"}, k=0)


def test_single_query_and_dataset_evaluation() -> None:
    # Single query evaluation returns standard metric bundle
    retrieved = ["job_1", "job_2", "job_3"]
    relevant = {"job_2"}

    single_res = evaluate_single_query(retrieved, relevant, k_values=[1, 2, 5])
    assert "precision@1" in single_res
    assert "recall@2" in single_res
    assert "f1@5" in single_res
    assert "hit_rate@1" in single_res
    assert "ndcg@2" in single_res
    assert "mrr" in single_res

    # Dataset macro evaluation across 2 queries
    all_ret = [
        ["job_1", "job_2"],  # hit at pos 2 -> MRR 0.5
        ["job_3", "job_4"],  # hit at pos 1 -> MRR 1.0
    ]
    all_rel = [
        {"job_2"},
        {"job_3"},
    ]

    dataset_res = evaluate_ranking_dataset(all_ret, all_rel, k_values=[1, 2])
    # Average MRR = (0.5 + 1.0) / 2 = 0.75
    assert dataset_res["mrr"] == pytest.approx(0.75)
    # Average HitRate@1 = (0.0 + 1.0) / 2 = 0.5
    assert dataset_res["hit_rate@1"] == pytest.approx(0.5)
    # Average HitRate@2 = (1.0 + 1.0) / 2 = 1.0
    assert dataset_res["hit_rate@2"] == pytest.approx(1.0)
