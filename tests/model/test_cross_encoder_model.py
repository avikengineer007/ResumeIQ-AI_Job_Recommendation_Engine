"""Model-level test for real CrossEncoder model inference and caching."""

import pytest

from src.reranking.cache import RerankCache
from src.reranking.cross_encoder import CrossEncoderReranker


@pytest.mark.slow
def test_real_cross_encoder_inference_and_caching() -> None:
    """Verifies that the actual cross-encoder/ms-marco-MiniLM-L-6-v2 weights run inference and populate cache."""
    cache = RerankCache()
    reranker = CrossEncoderReranker(
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
        cache=cache,
    )

    query = "Senior Python developer with FastAPI and microservices"
    candidates = ["job_backend", "job_gardener"]
    job_texts = {
        "job_backend": "Senior Python Backend Engineer building FastAPI microservices.",
        "job_gardener": "Professional landscape gardener specializing in lawn maintenance.",
    }

    results = reranker.rerank(
        query_text=query,
        candidates=candidates,
        job_texts_lookup=job_texts,
        top_k=2,
    )

    assert len(results) == 2
    # The relevant backend job must score significantly higher than the irrelevant gardener job
    assert results[0].job_id == "job_backend"
    assert results[1].job_id == "job_gardener"
    assert results[0].rerank_score > results[1].rerank_score

    # Check cache count
    assert cache.count() == 2

    # Second pass must hit cache
    cached_results = reranker.rerank(
        query_text=query,
        candidates=candidates,
        job_texts_lookup=job_texts,
        top_k=2,
    )
    assert cached_results[0].cached is True
    assert cached_results[1].cached is True
