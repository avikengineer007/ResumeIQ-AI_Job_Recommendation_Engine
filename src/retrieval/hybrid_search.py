"""Hybrid search and score fusion module combining BM25, dense vector, and skill scoring.

Features:
- Reciprocal Rank Fusion (RRF) with configurable k (default: 60)
- Convex Linear Score Combination with min-max normalization
- Unified HybridSearchResult tracking individual component scores and ranks
- Robust handling of missing items and non-overlapping candidate sets
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from src.embeddings.embedder import DenseEmbedder
from src.embeddings.faiss_index import FaissVectorIndex
from src.retrieval.bm25_retriever import BM25Retriever
from src.skill_normalization.skill_matcher import SkillMatcher


@dataclass
class HybridSearchResult:
    job_id: str
    final_score: float
    rank: int
    bm25_score: float = 0.0
    bm25_rank: int | None = None
    vector_score: float = 0.0
    vector_rank: int | None = None
    skill_score: float = 0.0
    fusion_mode: str = "rrf"


def reciprocal_rank_fusion(
    rankings: dict[str, Sequence[str]],
    k: int = 60,
    weights: dict[str, float] | None = None,
) -> list[tuple[str, float]]:
    """Compute Reciprocal Rank Fusion (RRF) score for each candidate document.

    RRF(d) = sum_{m in M} ( w_m / (k + rank_m(d)) )
    where rank_m(d) is 1-indexed.
    """
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")

    rrf_scores: dict[str, float] = {}

    for source_name, doc_list in rankings.items():
        w = weights.get(source_name, 1.0) if weights else 1.0
        for rank_idx, doc_id in enumerate(doc_list, start=1):
            contrib = w / float(k + rank_idx)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + contrib

    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results


def min_max_normalize(scores: dict[str, float]) -> dict[str, float]:
    """Normalize score values to [0.0, 1.0] using min-max scaling."""
    if not scores:
        return {}
    vals = list(scores.values())
    min_v = min(vals)
    max_v = max(vals)

    denom = max_v - min_v
    if denom <= 1e-9:
        # If all scores are identical, assign 1.0 if positive else 0.0
        uniform = 1.0 if max_v > 0.0 else 0.0
        return dict.fromkeys(scores, uniform)

    return {doc_id: (val - min_v) / denom for doc_id, val in scores.items()}


def linear_score_fusion(
    score_maps: dict[str, dict[str, float]],
    weights: dict[str, float] | None = None,
) -> list[tuple[str, float]]:
    """Compute convex linear combination of min-max normalized scores across channels.

    S_hybrid(d) = sum_{m in M} alpha_m * norm_score_m(d)
    """
    # Default weights from configs/retrieval_config.yaml
    # TODO(Phase 10): tune fusion weights on validation split rather than keeping heuristic defaults
    default_weights = {
        "bm25": 0.35,
        "vector": 0.45,
        "skill": 0.20,
    }
    active_weights = weights or default_weights

    # Ensure weights are normalized to sum to 1.0
    total_w = sum(active_weights.values())
    if total_w > 0:
        norm_weights = {k: v / total_w for k, v in active_weights.items()}
    else:
        norm_weights = active_weights

    # Normalize each channel's scores
    norm_channels: dict[str, dict[str, float]] = {
        name: min_max_normalize(scores) for name, scores in score_maps.items()
    }

    # Collect union of all document IDs
    all_doc_ids: set[str] = set()
    for scores in score_maps.values():
        all_doc_ids.update(scores.keys())

    fused_scores: dict[str, float] = {}
    for doc_id in all_doc_ids:
        score = 0.0
        for channel_name, channel_scores in norm_channels.items():
            w = norm_weights.get(channel_name, 0.0)
            score += w * channel_scores.get(doc_id, 0.0)
        fused_scores[doc_id] = score

    sorted_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results


class HybridSearchEngine:
    """Orchestrates multi-channel retrieval (BM25, dense vector, skill matching) and score fusion."""

    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        vector_index: FaissVectorIndex,
        embedder: DenseEmbedder,
        # TODO(Phase 10): tune rrf_k on validation split
        rrf_k: int = 60,
        # TODO(Phase 10): tune linear fusion weights on validation split
        linear_weights: dict[str, float] | None = None,
        job_skills_lookup: dict[str, list[dict[str, Any]]] | None = None,
        skill_matcher: SkillMatcher | None = None,
    ) -> None:
        self.bm25 = bm25_retriever
        self.vector_index = vector_index
        self.embedder = embedder
        self.rrf_k = rrf_k
        # TODO(Phase 10): tune fusion weights (0.35/0.45/0.20) on validation split
        self.linear_weights = linear_weights or {
            "bm25": 0.35,
            "vector": 0.45,
            "skill": 0.20,
        }
        self.job_skills_lookup = job_skills_lookup or {}
        self.skill_matcher = skill_matcher

    def search(
        self,
        query: str,
        candidate_skill_ids: list[str] | None = None,
        top_k: int = 50,
        mode: str = "rrf",
    ) -> list[HybridSearchResult]:
        """Perform hybrid search over indexed corpus with specified fusion mode ('rrf' or 'weighted')."""
        if mode not in ("rrf", "weighted", "linear"):
            raise ValueError(
                f"Unsupported fusion mode: {mode}. Must be 'rrf', 'weighted', or 'linear'"
            )

        # 1. Retrieve BM25 candidates
        bm25_raw = self.bm25.search(query, top_k=top_k)
        bm25_scores = dict(bm25_raw)
        bm25_ranking = [doc_id for doc_id, _ in bm25_raw]
        bm25_ranks = {doc_id: idx for idx, doc_id in enumerate(bm25_ranking, start=1)}

        # 2. Retrieve Vector candidates
        query_vec = self.embedder.encode_queries(query)
        if isinstance(query_vec, np.ndarray) and query_vec.ndim > 1:
            query_vec = query_vec[0]
        vector_raw = self.vector_index.search(query_vec, top_k=top_k)
        vector_scores = dict(vector_raw)
        vector_ranking = [doc_id for doc_id, _ in vector_raw]
        vector_ranks = {
            doc_id: idx for idx, doc_id in enumerate(vector_ranking, start=1)
        }

        # 3. Optional Skill matching candidates
        skill_scores: dict[str, float] = {}
        all_candidate_ids = set(bm25_scores.keys()).union(vector_scores.keys())

        if (
            candidate_skill_ids is not None
            and len(candidate_skill_ids) > 0
            and self.skill_matcher
            and self.job_skills_lookup
        ):
            for doc_id in all_candidate_ids:
                job_reqs = self.job_skills_lookup.get(doc_id, [])
                if job_reqs is not None and len(job_reqs) > 0:
                    match_res = self.skill_matcher.match(candidate_skill_ids, job_reqs)
                    skill_scores[doc_id] = match_res.skill_score

        # 4. Perform Fusion
        if mode == "rrf":
            rankings = {
                "bm25": bm25_ranking,
                "vector": vector_ranking,
            }
            fused = reciprocal_rank_fusion(rankings, k=self.rrf_k)
        else:
            score_maps = {
                "bm25": bm25_scores,
                "vector": vector_scores,
            }
            if skill_scores:
                score_maps["skill"] = skill_scores
            fused = linear_score_fusion(score_maps, weights=self.linear_weights)

        # 5. Build structured hybrid results
        results: list[HybridSearchResult] = []
        for rank_idx, (doc_id, fused_score) in enumerate(fused[:top_k], start=1):
            results.append(
                HybridSearchResult(
                    job_id=doc_id,
                    final_score=float(fused_score),
                    rank=rank_idx,
                    bm25_score=bm25_scores.get(doc_id, 0.0),
                    bm25_rank=bm25_ranks.get(doc_id),
                    vector_score=vector_scores.get(doc_id, 0.0),
                    vector_rank=vector_ranks.get(doc_id),
                    skill_score=skill_scores.get(doc_id, 0.0),
                    fusion_mode=mode,
                )
            )

        return results
