"""Unit tests for dense embedding generator and model manifest tracking."""

from pathlib import Path

import numpy as np
import pytest

from src.embeddings.embedder import (
    DenseEmbedder,
    EmbeddingManifest,
    format_job_text,
    format_resume_text,
)


def test_embedding_manifest_serialization(tmp_path: Path) -> None:
    manifest = EmbeddingManifest(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        revision="main",
        dimension=384,
        text_template_version="v1_job_title_skills_desc",
        normalize_embeddings=True,
        prefix_query="",
        prefix_passage="",
    )

    p = tmp_path / "manifest.json"
    manifest_dict = manifest.to_dict()
    assert manifest_dict["dimension"] == 384
    assert manifest_dict["model_name"] == "sentence-transformers/all-MiniLM-L6-v2"

    import json

    with open(p, "w", encoding="utf-8") as f:
        json.dump(manifest_dict, f)

    reloaded = EmbeddingManifest.from_dict(manifest_dict)
    assert reloaded.dimension == manifest.dimension
    assert reloaded.text_template_version == manifest.text_template_version


def test_text_formatting() -> None:
    job = {
        "title": "Machine Learning Engineer",
        "skills": ["Python", "PyTorch"],
        "description": "Build recommender systems.",
    }
    formatted_job = format_job_text(job, template_version="v1")
    assert "Job Title: Machine Learning Engineer" in formatted_job
    assert "Required Skills: Python, PyTorch" in formatted_job
    assert "Description: Build recommender systems." in formatted_job

    resume = {
        "summary": "Experienced Data Scientist with 5 years in NLP.",
        "skills": ["Python", "Transformers"],
        "experience": "Led search ranking project.",
    }
    formatted_resume = format_resume_text(resume, template_version="v1")
    assert "Professional Summary: Experienced Data Scientist" in formatted_resume
    assert "Skills: Python, Transformers" in formatted_resume


def test_embedder_encoding_and_l2_normalization() -> None:
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

    # Verify L2 normalization: norm of each vector must be ~1.0
    for vec in vectors:
        norm = np.linalg.norm(vec)
        assert norm == pytest.approx(1.0, abs=1e-5)
