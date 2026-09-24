"""Unit tests for pair-score cross-encoder caching."""

from pathlib import Path

from src.reranking.cache import RerankCache, compute_text_hash


def test_text_hash_stability() -> None:
    t1 = "  Senior Python   Engineer  "
    t2 = "Senior Python Engineer"
    t3 = "Junior Python Engineer"

    # Whitespace invariance
    assert compute_text_hash(t1) == compute_text_hash(t2)
    # Content sensitivity
    assert compute_text_hash(t1) != compute_text_hash(t3)


def test_cache_put_get_single() -> None:
    cache = RerankCache()
    r_hash = "abc123hash"
    m_ver = "test_model@v1"

    assert cache.get(r_hash, "job_1", m_ver) is None

    cache.put(r_hash, "job_1", m_ver, 4.25)
    assert cache.get(r_hash, "job_1", m_ver) == 4.25


def test_cache_batch_operations() -> None:
    cache = RerankCache()
    r_hash = "resume_hash_xyz"
    m_ver = "cross_encoder@main"

    # Insert some items
    pairs = [("job_a", 2.5), ("job_b", -1.2)]
    cache.put_batch(r_hash, pairs, m_ver)

    # Query 3 jobs (2 cached, 1 missing)
    cached, missing = cache.get_batch(r_hash, ["job_a", "job_b", "job_c"], m_ver)

    assert cached["job_a"] == 2.5
    assert cached["job_b"] == -1.2
    assert missing == ["job_c"]


def test_cache_disk_persistence(tmp_path: Path) -> None:
    db_file = tmp_path / "rerank_cache.db"
    cache1 = RerankCache(db_path=db_file)
    cache1.put("hash1", "job_99", "v1", 3.14)

    # Re-open from disk
    cache2 = RerankCache(db_path=db_file)
    assert cache2.get("hash1", "job_99", "v1") == 3.14
    assert cache2.count() == 1

    cache2.clear()
    assert cache2.count() == 0
