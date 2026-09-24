"""FAISS vector indexing module for exact dense semantic retrieval.

Features:
- Uses faiss.IndexFlatIP for exact inner product / cosine similarity evaluation.
- Maintains document ID mappings to decouple search engine from internal integer offsets.
- Persists index binary, doc IDs, and embedding manifest to disk.
- Verifies manifest consistency on reload to avoid dimensional or model mismatch errors.
"""

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from src.embeddings.embedder import EmbeddingManifest


@dataclass
class IndexManifest:
    index_type: str = "IndexFlatIP"
    dimension: int = 384
    num_vectors: int = 0
    embedding_manifest: dict[str, Any] | None = None
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


class FaissVectorIndex:
    """Vector index wrapper around FAISS IndexFlatIP for exact similarity search."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(self.dimension)
        self.doc_ids: list[str] = []

    @property
    def total_vectors(self) -> int:
        return self.index.ntotal

    def add_vectors(
        self,
        vectors: np.ndarray,
        doc_ids: Sequence[str],
    ) -> None:
        """Add dense vectors and corresponding document IDs to the index."""
        if len(vectors) != len(doc_ids):
            raise ValueError(
                f"Number of vectors ({len(vectors)}) must match doc_ids ({len(doc_ids)})"
            )
        if len(vectors) == 0:
            return

        vecs = np.asarray(vectors, dtype=np.float32)
        if vecs.ndim == 1:
            vecs = vecs.reshape(1, -1)

        if vecs.shape[1] != self.dimension:
            raise ValueError(
                f"Vector dimension {vecs.shape[1]} does not match index dimension {self.dimension}"
            )

        self.index.add(vecs)
        self.doc_ids.extend([str(d) for d in doc_ids])

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """Search nearest neighbors for a single query vector, returning ranked (doc_id, score)."""
        q = np.asarray(query_vector, dtype=np.float32)
        if q.ndim == 1:
            q = q.reshape(1, -1)

        if q.shape[1] != self.dimension:
            raise ValueError(
                f"Query vector dimension {q.shape[1]} does not match index dimension {self.dimension}"
            )

        if self.index.ntotal == 0 or not self.doc_ids:
            return []

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q, k)

        results: list[tuple[str, float]] = []
        for score, idx in zip(scores[0], indices[0], strict=True):
            if idx != -1 and idx < len(self.doc_ids):
                results.append((self.doc_ids[idx], float(score)))

        return results

    def save(
        self,
        output_dir: str | Path,
        embedding_manifest: EmbeddingManifest | None = None,
    ) -> None:
        """Save FAISS index binary, doc_ids mapping, and manifest metadata."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        # Write FAISS binary
        faiss.write_index(self.index, str(out / "index.faiss"))

        # Write document IDs
        with open(out / "doc_ids.json", "w", encoding="utf-8") as f:
            json.dump(self.doc_ids, f, indent=2)

        # Write index manifest
        emb_dict = embedding_manifest.to_dict() if embedding_manifest else None
        manifest = IndexManifest(
            index_type="IndexFlatIP",
            dimension=self.dimension,
            num_vectors=self.index.ntotal,
            embedding_manifest=emb_dict,
        )
        with open(out / "index_manifest.json", "w", encoding="utf-8") as f:
            json.dump(asdict(manifest), f, indent=2)

    @classmethod
    def load(cls, index_dir: str | Path) -> "FaissVectorIndex":
        """Load vector index, doc_ids, and manifest from disk."""
        inp = Path(index_dir)
        index_file = inp / "index.faiss"
        ids_file = inp / "doc_ids.json"
        manifest_file = inp / "index_manifest.json"

        if not index_file.exists() or not ids_file.exists():
            raise FileNotFoundError(f"Missing required index files in {inp}")

        index = faiss.read_index(str(index_file))
        with open(ids_file, encoding="utf-8") as f:
            doc_ids = json.load(f)

        instance = cls(dimension=index.d)
        instance.index = index
        instance.doc_ids = [str(d) for d in doc_ids]

        if manifest_file.exists():
            with open(manifest_file, encoding="utf-8") as f:
                manifest_data = json.load(f)
                if manifest_data.get("dimension") != instance.dimension:
                    raise ValueError(
                        f"Manifest dimension mismatch: {manifest_data.get('dimension')} vs {instance.dimension}"
                    )

        return instance
