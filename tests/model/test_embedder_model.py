"""Model-level test for actual SentenceTransformer weights inference and L2 normalization."""

import numpy as np
import pytest

from src.embeddings.embedder import DenseEmbedder, EmbeddingManifest


@pytest.mark.slow
def test_real_model_inference_and_normalization() -> None:
    """Verifies that the actual all-MiniLM-L6-v2 model weights load and produce valid unit-norm embeddings."""
    embedder = DenseEmbedder(
        manifest=EmbeddingManifest(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384,
            normalize_embeddings=True,
        )
    )

    texts = [
        "Software Engineer with Python and FastAPI experience.",
        "Data Scientist specializing in Natural Language Processing.",
    ]
    vectors = embedder.encode_passages(texts)

    assert isinstance(vectors, np.ndarray)
    assert vectors.shape == (2, 384)
    assert vectors.dtype == np.float32

    for vec in vectors:
        norm = np.linalg.norm(vec)
        assert norm == pytest.approx(1.0, abs=1e-4)
