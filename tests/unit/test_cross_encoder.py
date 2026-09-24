"""Unit tests for CrossEncoderReranker with mocked transformer model."""

from unittest.mock import MagicMock, patch

from src.reranking.cache import RerankCache
from src.reranking.cross_encoder import CrossEncoderReranker
from src.retrieval.hybrid_search import HybridSearchResult


def test_cross_encoder_rerank_and_truncation() -> None:
    mock_model = MagicMock()
    # Mock scores for 3 missing candidate pairs: job_2=5.0, job_1=2.0, job_3=8.0
    mock_model.predict.return_value = [2.0, 5.0, 8.0]

    with patch("src.reranking.cross_encoder.CrossEncoder", return_value=mock_model):
        cache = RerankCache()
        reranker = CrossEncoderReranker(cache=cache)

        candidates = [
            HybridSearchResult(job_id="job_1", final_score=0.8, rank=1),
            HybridSearchResult(job_id="job_2", final_score=0.7, rank=2),
            HybridSearchResult(job_id="job_3", final_score=0.6, rank=3),
        ]
        job_texts = {
            "job_1": "Python developer role",
            "job_2": "FastAPI engineer",
            "job_3": "Machine learning lead",
        }

        # Truncate top 3 to top 2
        results = reranker.rerank(
            query_text="Experienced ML lead with Python",
            candidates=candidates,
            job_texts_lookup=job_texts,
            top_k=2,
        )

        assert len(results) == 2

        # Order must be sorted descending by rerank score: job_3 (8.0), job_2 (5.0)
        assert results[0].job_id == "job_3"
        assert results[0].rerank_score == 8.0
        assert results[0].rank == 1
        assert results[0].prior_rank == 3
        assert results[0].cached is False

        assert results[1].job_id == "job_2"
        assert results[1].rerank_score == 5.0
        assert results[1].rank == 2
        assert results[1].prior_rank == 2

        # Second call with the same input must hit the cache!
        mock_model.predict.reset_mock()
        cached_results = reranker.rerank(
            query_text="Experienced ML lead with Python",
            candidates=candidates,
            job_texts_lookup=job_texts,
            top_k=2,
        )
        assert len(cached_results) == 2
        assert cached_results[0].cached is True
        assert cached_results[1].cached is True
        # Model predict should NOT have been called on cache hit
        mock_model.predict.assert_not_called()


def test_cross_encoder_empty_candidates() -> None:
    with patch("src.reranking.cross_encoder.CrossEncoder"):
        reranker = CrossEncoderReranker()
        res = reranker.rerank("query", [], {})
        assert res == []
