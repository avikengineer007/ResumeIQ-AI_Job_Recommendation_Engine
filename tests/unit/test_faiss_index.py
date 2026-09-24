"""Unit tests for FAISS vector index (IndexFlatIP) and persistence."""

from pathlib import Path

import numpy as np
import pytest

from src.embeddings.embedder import EmbeddingManifest
from src.embeddings.faiss_index import FaissVectorIndex


def test_faiss_index_add_and_search() -> None:
    dim = 4
    index = FaissVectorIndex(dimension=dim)

    # 3 mock normalized vectors
    v1 = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    v2 = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)
    v3 = np.array([0.7071, 0.7071, 0.0, 0.0], dtype=np.float32)

    vectors = np.stack([v1, v2, v3])
    doc_ids = ["doc_1", "doc_2", "doc_3"]

    index.add_vectors(vectors, doc_ids)
    assert index.total_vectors == 3

    # Query matching v1 exactly
    query = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    results = index.search(query, top_k=2)

    assert len(results) == 2
    top_doc_id, top_score = results[0]
    assert top_doc_id == "doc_1"
    assert top_score == pytest.approx(1.0, abs=1e-5)

    # Second result should be doc_3 (dot product ~0.7071)
    second_doc_id, second_score = results[1]
    assert second_doc_id == "doc_3"
    assert second_score == pytest.approx(0.7071, abs=1e-3)


def test_dimension_mismatch_error() -> None:
    index = FaissVectorIndex(dimension=4)
    invalid_vectors = np.ones((2, 8), dtype=np.float32)

    with pytest.raises(ValueError, match="does not match index dimension"):
        index.add_vectors(invalid_vectors, ["doc_a", "doc_b"])

    with pytest.raises(ValueError, match="does not match index dimension"):
        index.search(np.ones((8,), dtype=np.float32), top_k=1)


def test_faiss_save_and_load(tmp_path: Path) -> None:
    dim = 8
    index = FaissVectorIndex(dimension=dim)
    vectors = np.random.randn(5, dim).astype(np.float32)
    # L2 normalize
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    doc_ids = [f"job_{i}" for i in range(5)]

    index.add_vectors(vectors, doc_ids)

    manifest = EmbeddingManifest(dimension=dim, model_name="test-model")
    save_dir = tmp_path / "faiss_test_index"
    index.save(save_dir, embedding_manifest=manifest)

    # Load back
    loaded = FaissVectorIndex.load(save_dir)
    assert loaded.dimension == dim
    assert loaded.total_vectors == 5
    assert loaded.doc_ids == doc_ids

    # Query with vector 0
    res = loaded.search(vectors[0], top_k=1)
    assert res[0][0] == "job_0"
    assert res[0][1] == pytest.approx(1.0, abs=1e-4)
