"""Dense text embedding module with swappable model manifests.

Features:
- EmbeddingManifest tracking model name, revision, dimension, text-template version, and prefixes.
- Supports candidate models: all-MiniLM-L6-v2, all-mpnet-base-v2, bge-base-en-v1.5, e5-base-v2.
- Text template formatters for jobs and resumes.
- L2 normalization for exact cosine similarity via FAISS IndexFlatIP.
"""

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class EmbeddingManifest:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    revision: str = "main"
    dimension: int = 384
    text_template_version: str = "v1_job_title_skills_desc"
    normalize_embeddings: bool = True
    prefix_query: str = ""
    prefix_passage: str = ""
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EmbeddingManifest":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def format_job_text(job: dict[str, Any], template_version: str = "v1") -> str:
    """Format structured job data into an embedding text payload."""
    title = str(job.get("title", "")).strip()
    skills_raw = job.get("skills", [])
    if isinstance(skills_raw, list):
        skills_str = ", ".join(str(s) for s in skills_raw)
    else:
        skills_str = str(skills_raw).strip()
    desc = str(job.get("description", "")).strip()

    if template_version in ("v1", "v1_job_title_skills_desc"):
        parts = []
        if title:
            parts.append(f"Job Title: {title}")
        if skills_str:
            parts.append(f"Required Skills: {skills_str}")
        if desc:
            parts.append(f"Description: {desc}")
        return "\n".join(parts)

    # Fallback raw concatenated text
    return f"{title} {skills_str} {desc}".strip()


def format_resume_text(resume: dict[str, Any], template_version: str = "v1") -> str:
    """Format structured resume data into an embedding text payload."""
    skills_raw = resume.get("skills", [])
    if hasattr(skills_raw, "tolist"):
        skills_raw = skills_raw.tolist()
    if isinstance(skills_raw, list):
        skills_str = ", ".join(
            s.get("name", s.get("skill_id", str(s))) if isinstance(s, dict) else str(s)
            for s in skills_raw
        )
    else:
        skills_str = str(skills_raw).strip()

    summary = str(resume.get("summary", "")).strip()
    exp_raw = resume.get("experience", "")
    if hasattr(exp_raw, "tolist"):
        exp_raw = exp_raw.tolist()
    if isinstance(exp_raw, list):
        exp_str = " ".join(
            str(e.get("description", "")) if isinstance(e, dict) else str(e)
            for e in exp_raw
        )
    else:
        exp_str = str(exp_raw).strip()

    if template_version in ("v1", "v1_resume_summary_skills_exp"):
        parts = []
        if summary:
            parts.append(f"Professional Summary: {summary}")
        if skills_str:
            parts.append(f"Skills: {skills_str}")
        if exp_str:
            parts.append(f"Experience: {exp_str}")
        return "\n".join(parts)

    return f"{summary} {skills_str} {exp_str}".strip()


class DenseEmbedder:
    """SentenceTransformer embedding generator with manifest tracking and query/passage prefixing."""

    def __init__(
        self,
        manifest: EmbeddingManifest | None = None,
        device: str | None = None,
    ) -> None:
        self.manifest = manifest or EmbeddingManifest()
        self.device = device

        self.model = SentenceTransformer(
            self.manifest.model_name,
            revision=self.manifest.revision,
            device=self.device,
        )

        # Confirm and synchronize embedding dimension
        get_dim_fn = getattr(
            self.model,
            "get_embedding_dimension",
            self.model.get_sentence_embedding_dimension,
        )
        detected_dim = get_dim_fn()
        if detected_dim and detected_dim != self.manifest.dimension:
            self.manifest.dimension = detected_dim

    def encode_queries(
        self,
        queries: Sequence[str] | str,
        batch_size: int = 64,
    ) -> np.ndarray:
        """Encode query strings with prefix_query and optional L2 normalization."""
        if isinstance(queries, str):
            queries = [queries]

        prefixed = [f"{self.manifest.prefix_query}{q}" for q in queries]
        embeddings = self.model.encode(
            prefixed,
            batch_size=batch_size,
            normalize_embeddings=self.manifest.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embeddings.astype(np.float32)

    def encode_passages(
        self,
        passages: Sequence[str] | str,
        batch_size: int = 64,
    ) -> np.ndarray:
        """Encode passage/document strings with prefix_passage and optional L2 normalization."""
        if isinstance(passages, str):
            passages = [passages]

        prefixed = [f"{self.manifest.prefix_passage}{p}" for p in passages]
        embeddings = self.model.encode(
            prefixed,
            batch_size=batch_size,
            normalize_embeddings=self.manifest.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embeddings.astype(np.float32)

    def save_manifest(self, output_path: str | Path) -> None:
        """Save embedding manifest JSON."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.manifest.to_dict(), f, indent=2)

    @classmethod
    def from_manifest_file(
        cls, manifest_path: str | Path, device: str | None = None
    ) -> "DenseEmbedder":
        """Instantiate embedder from an existing manifest JSON file."""
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        manifest = EmbeddingManifest.from_dict(data)
        return cls(manifest=manifest, device=device)
