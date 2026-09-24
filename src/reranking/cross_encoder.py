"""Cross-encoder reranking module with pair-score caching and candidate reranking.

Features:
- Wraps sentence_transformers CrossEncoder (default: cross-encoder/ms-marco-MiniLM-L-6-v2)
- Pair-score caching by (resume_hash, job_id, model_version) via RerankCache
- Batched inference only on cache misses
- Truncates top-N hybrid candidates to top-K final reranked results
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from sentence_transformers import CrossEncoder

from src.reranking.cache import RerankCache, compute_text_hash
from src.retrieval.hybrid_search import HybridSearchResult


@dataclass
class RerankResult:
    job_id: str
    rerank_score: float
    rank: int
    prior_rank: int | None = None
    cached: bool = False


class CrossEncoderReranker:
    """Reranks top-N candidates using a CrossEncoder transformer with pair-score caching."""

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        revision: str = "main",
        max_length: int = 512,
        batch_size: int = 32,
        cache: RerankCache | None = None,
        device: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.revision = revision
        self.max_length = max_length
        self.batch_size = batch_size
        self.cache = cache or RerankCache()
        self.device = device

        self.model = CrossEncoder(
            self.model_name,
            max_length=self.max_length,
            revision=self.revision,
            device=self.device,
        )

    @property
    def model_version(self) -> str:
        return f"{self.model_name}@{self.revision}"

    def rerank(
        self,
        query_text: str,
        candidates: Sequence[dict[str, Any] | HybridSearchResult | str],
        job_texts_lookup: dict[str, str],
        top_k: int = 10,
        resume_hash: str | None = None,
    ) -> list[RerankResult]:
        """Rerank candidates using cross-encoder scores.

        Args:
            query_text: Resume text or query payload
            candidates: Sequence of job IDs, candidate dicts, or HybridSearchResult objects
            job_texts_lookup: Mapping from job_id to formatted job description text
            top_k: Number of reranked candidates to return (default: 10)
            resume_hash: Optional precomputed resume content hash
        """
        if not candidates:
            return []

        # 1. Normalize candidates into (job_id, prior_rank)
        candidate_items: list[tuple[str, int | None]] = []
        for idx, c in enumerate(candidates, start=1):
            if isinstance(c, HybridSearchResult):
                candidate_items.append((c.job_id, c.rank))
            elif isinstance(c, dict):
                j_id = str(c.get("job_id", c.get("id", "")))
                p_rank = c.get("rank", idx)
                candidate_items.append((j_id, p_rank))
            else:
                candidate_items.append((str(c), idx))

        job_ids = [j_id for j_id, _ in candidate_items]
        prior_ranks = dict(candidate_items)

        r_hash = resume_hash or compute_text_hash(query_text)
        m_version = self.model_version

        # 2. Check cache
        cached_scores, missing_ids = self.cache.get_batch(r_hash, job_ids, m_version)

        # 3. Predict on cache misses
        new_scores: dict[str, float] = {}
        if missing_ids:
            pairs: list[list[str]] = []
            valid_missing_ids: list[str] = []

            for m_id in missing_ids:
                passage_text = job_texts_lookup.get(m_id, "")
                pairs.append([query_text, passage_text])
                valid_missing_ids.append(m_id)

            if pairs:
                predicted = self.model.predict(
                    pairs,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                )
                # Handle single scalar or array output
                if hasattr(predicted, "__iter__"):
                    pred_list = [float(p) for p in predicted]
                else:
                    pred_list = [float(predicted)]

                pairs_to_cache: list[tuple[str, float]] = []
                for m_id, score in zip(valid_missing_ids, pred_list, strict=True):
                    new_scores[m_id] = score
                    pairs_to_cache.append((m_id, score))

                self.cache.put_batch(r_hash, pairs_to_cache, m_version)

        # 4. Assemble all scored candidates
        all_scored: list[tuple[str, float, bool]] = []
        for j_id in job_ids:
            if j_id in cached_scores:
                all_scored.append((j_id, cached_scores[j_id], True))
            elif j_id in new_scores:
                all_scored.append((j_id, new_scores[j_id], False))
            else:
                all_scored.append((j_id, float("-inf"), False))

        # 5. Sort descending by cross-encoder score
        all_scored.sort(key=lambda x: x[1], reverse=True)

        # 6. Truncate to top_k and build RerankResult
        results: list[RerankResult] = []
        for rank_idx, (j_id, score, is_cached) in enumerate(
            all_scored[:top_k], start=1
        ):
            results.append(
                RerankResult(
                    job_id=j_id,
                    rerank_score=score,
                    rank=rank_idx,
                    prior_rank=prior_ranks.get(j_id),
                    cached=is_cached,
                )
            )

        return results
