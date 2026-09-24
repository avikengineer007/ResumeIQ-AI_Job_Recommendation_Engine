"""Unit tests for exact and near-duplicate MinHash deduplication."""

from src.preprocessing.deduplicator import (
    Deduplicator,
    MinHash,
    compute_exact_hash,
)


def test_exact_hash_consistency():
    """Verify exact hash is identical across differing whitespaces and casings."""
    t1 = "Senior Machine Learning Engineer at Acme Corp"
    t2 = "  senior   machine learning engineer at acme corp \n"
    assert compute_exact_hash(t1) == compute_exact_hash(t2)


def test_minhash_jaccard_similarity():
    """Verify MinHash Jaccard similarity between identical, similar, and dissimilar texts."""
    mh = MinHash(num_perm=128, seed=42, shingle_size=2)

    text_base = "We are seeking a senior machine learning engineer experienced in PyTorch and transformers"
    text_near = "We are seeking a lead machine learning engineer experienced in PyTorch and transformers"
    text_diff = (
        "Frontend developer needed for React, TypeScript, Tailwind, and CSS animations"
    )

    sig_base = mh.compute_signature(text_base)
    sig_near = mh.compute_signature(text_near)
    sig_diff = mh.compute_signature(text_diff)

    sim_same = MinHash.jaccard_similarity(sig_base, sig_base)
    sim_near = MinHash.jaccard_similarity(sig_base, sig_near)
    sim_diff = MinHash.jaccard_similarity(sig_base, sig_diff)

    assert sim_same == 1.0
    assert sim_near > 0.60
    assert sim_diff < 0.20


def test_deduplicator_pipeline():
    """Verify full deduplication clusters exact duplicates and near duplicates."""
    records = [
        {
            "job_id": "j1",
            "title": "ML Engineer",
            "company": "Acme",
            "description": "Python, PyTorch, Docker, deep learning models in production.",
        },
        # Exact duplicate
        {
            "job_id": "j2",
            "title": "ml engineer",
            "company": "acme",
            "description": "python, pytorch, docker, deep learning models in production.",
        },
        # Near duplicate (small wording change)
        {
            "job_id": "j3",
            "title": "ML Engineer",
            "company": "Acme",
            "description": "Python, PyTorch, Docker, deep learning models in production. Apply today!",
        },
        # Completely distinct
        {
            "job_id": "j4",
            "title": "Marketing Manager",
            "company": "Beta",
            "description": "Lead digital marketing campaigns, SEO, Google Ads, and brand strategy.",
        },
    ]

    dedup = Deduplicator(near_duplicate_threshold=0.70, seed=42)
    unique_recs, clusters = dedup.deduplicate(records, id_key="job_id")

    unique_ids = {r["job_id"] for r in unique_recs}
    assert "j1" in unique_ids
    assert "j4" in unique_ids
    # j2 and j3 should be clustered into j1
    assert "j2" not in unique_ids
    assert "j3" not in unique_ids
    assert "j2" in clusters["j1"]
    assert "j3" in clusters["j1"]
