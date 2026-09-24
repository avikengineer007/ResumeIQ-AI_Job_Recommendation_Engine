"""Evaluation metrics module for information retrieval and recommendation benchmarks.

Implements standard, reproducible IR metrics with a frozen evaluation protocol:
- Precision@K
- Recall@K
- F1@K
- HitRate@K (Success@K)
- Mean Reciprocal Rank (MRR)
- Normalized Discounted Cumulative Gain (NDCG@K) with exponential gain (2^rel - 1)

Guarantees:
- Handles zero divisions gracefully (empty retrieval, empty ground truth).
- Protocol freeze: All retrieval and reranking models must evaluate on the exact
  same split and metrics implementations.
"""

import math
from collections.abc import Sequence


def _normalize_relevance(
    relevance_data: set[str] | Sequence[str] | dict[str, float],
) -> dict[str, float]:
    """Convert sets, lists, or score mappings into a unified {item_id: score} dict."""
    if isinstance(relevance_data, dict):
        return {k: float(v) for k, v in relevance_data.items()}
    if isinstance(relevance_data, (set, list, tuple)):
        return {str(item): 1.0 for item in relevance_data}
    raise TypeError(
        f"relevance_data must be dict, set, or sequence, got {type(relevance_data)}"
    )


def precision_at_k(
    retrieved: Sequence[str],
    relevant: set[str] | Sequence[str] | dict[str, float],
    k: int,
) -> float:
    """Compute Precision@K.

    Precision@K = |Retrieved[:K] ∩ Relevant| / K
    """
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")
    if not retrieved or not relevant:
        return 0.0

    rel_map = _normalize_relevance(relevant)
    top_k = retrieved[:k]
    hits = sum(1 for item in top_k if rel_map.get(item, 0.0) > 0.0)
    return hits / float(k)


def recall_at_k(
    retrieved: Sequence[str],
    relevant: set[str] | Sequence[str] | dict[str, float],
    k: int,
) -> float:
    """Compute Recall@K.

    Recall@K = |Retrieved[:K] ∩ Relevant| / |Relevant|
    """
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")
    if not retrieved or not relevant:
        return 0.0

    rel_map = _normalize_relevance(relevant)
    total_relevant = sum(1 for score in rel_map.values() if score > 0.0)
    if total_relevant == 0:
        return 0.0

    top_k = retrieved[:k]
    hits = sum(1 for item in top_k if rel_map.get(item, 0.0) > 0.0)
    return hits / float(total_relevant)


def f1_at_k(
    retrieved: Sequence[str],
    relevant: set[str] | Sequence[str] | dict[str, float],
    k: int,
) -> float:
    """Compute harmonic mean of Precision@K and Recall@K."""
    p = precision_at_k(retrieved, relevant, k)
    r = recall_at_k(retrieved, relevant, k)
    if p + r == 0.0:
        return 0.0
    return (2.0 * p * r) / (p + r)


def hit_rate_at_k(
    retrieved: Sequence[str],
    relevant: set[str] | Sequence[str] | dict[str, float],
    k: int,
) -> float:
    """Compute HitRate@K (1.0 if at least one relevant item appears in top K, else 0.0)."""
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")
    if not retrieved or not relevant:
        return 0.0

    rel_map = _normalize_relevance(relevant)
    top_k = retrieved[:k]
    for item in top_k:
        if rel_map.get(item, 0.0) > 0.0:
            return 1.0
    return 0.0


def mrr(
    retrieved: Sequence[str],
    relevant: set[str] | Sequence[str] | dict[str, float],
    k: int | None = None,
) -> float:
    """Compute Mean Reciprocal Rank (RR for a single ranking).

    RR = 1 / rank of first relevant item (1-indexed).
    If no relevant item is found in top K (or whole list), returns 0.0.
    """
    if k is not None and k <= 0:
        raise ValueError(f"k must be positive, got {k}")
    if not retrieved or not relevant:
        return 0.0

    rel_map = _normalize_relevance(relevant)
    candidates = retrieved[:k] if k is not None else retrieved

    for idx, item in enumerate(candidates, start=1):
        if rel_map.get(item, 0.0) > 0.0:
            return 1.0 / float(idx)

    return 0.0


def dcg_at_k(
    retrieved: Sequence[str],
    relevant: set[str] | Sequence[str] | dict[str, float],
    k: int,
) -> float:
    """Compute Discounted Cumulative Gain at K using exponential gain: (2^rel - 1) / log2(i + 1)."""
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")
    if not retrieved or not relevant:
        return 0.0

    rel_map = _normalize_relevance(relevant)
    top_k = retrieved[:k]

    dcg = 0.0
    for idx, item in enumerate(top_k, start=1):
        rel = rel_map.get(item, 0.0)
        if rel > 0.0:
            gain = math.pow(2.0, rel) - 1.0
            discount = math.log2(idx + 1)
            dcg += gain / discount

    return dcg


def ndcg_at_k(
    retrieved: Sequence[str],
    relevant: set[str] | Sequence[str] | dict[str, float],
    k: int,
) -> float:
    """Compute Normalized Discounted Cumulative Gain at K (NDCG@K = DCG@K / IDCG@K)."""
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")
    if not retrieved or not relevant:
        return 0.0

    rel_map = _normalize_relevance(relevant)
    actual_dcg = dcg_at_k(retrieved, rel_map, k)
    if actual_dcg == 0.0:
        return 0.0

    # Ideal ranking: Sort relevant scores descending
    sorted_scores = sorted(
        [score for score in rel_map.values() if score > 0.0], reverse=True
    )
    ideal_scores = sorted_scores[:k]

    idcg = 0.0
    for idx, rel in enumerate(ideal_scores, start=1):
        gain = math.pow(2.0, rel) - 1.0
        discount = math.log2(idx + 1)
        idcg += gain / discount

    if idcg == 0.0:
        return 0.0

    return actual_dcg / idcg


def evaluate_single_query(
    retrieved: Sequence[str],
    relevant: set[str] | Sequence[str] | dict[str, float],
    k_values: Sequence[int] = (5, 10, 20),
) -> dict[str, float]:
    """Compute all evaluation metrics for a single query across multiple cutoffs."""
    results: dict[str, float] = {}
    results["mrr"] = mrr(retrieved, relevant)

    for k in k_values:
        results[f"precision@{k}"] = precision_at_k(retrieved, relevant, k)
        results[f"recall@{k}"] = recall_at_k(retrieved, relevant, k)
        results[f"f1@{k}"] = f1_at_k(retrieved, relevant, k)
        results[f"hit_rate@{k}"] = hit_rate_at_k(retrieved, relevant, k)
        results[f"ndcg@{k}"] = ndcg_at_k(retrieved, relevant, k)

    return results


def evaluate_ranking_dataset(
    all_retrieved: Sequence[Sequence[str]],
    all_relevant: Sequence[set[str] | Sequence[str] | dict[str, float]],
    k_values: Sequence[int] = (5, 10, 20),
) -> dict[str, float]:
    """Compute macro-averaged evaluation metrics across an entire evaluation split."""
    if len(all_retrieved) != len(all_relevant):
        raise ValueError(
            f"Retrieved length ({len(all_retrieved)}) does not match relevant length ({len(all_relevant)})"
        )
    if not all_retrieved:
        return {}

    num_queries = len(all_retrieved)
    aggregated: dict[str, float] = {}

    for ret, rel in zip(all_retrieved, all_relevant, strict=True):
        query_metrics = evaluate_single_query(ret, rel, k_values=k_values)
        for metric, val in query_metrics.items():
            aggregated[metric] = aggregated.get(metric, 0.0) + val

    return {metric: total / float(num_queries) for metric, total in aggregated.items()}
