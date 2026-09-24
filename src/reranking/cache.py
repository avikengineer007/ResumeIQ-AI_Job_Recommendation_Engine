"""Cross-encoder pair-score caching module.

Caches (resume_hash, job_id, model_version) -> score tuples in SQLite/in-memory storage
to eliminate redundant transformer forward passes across experimental ablation runs
(Ablations A-F in Phase 17/18).
"""

import hashlib
import sqlite3
from collections.abc import Sequence
from pathlib import Path


def compute_text_hash(text: str) -> str:
    """Compute stable SHA-256 hex digest of normalized text."""
    normalized = " ".join(text.strip().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class RerankCache:
    """Persistent SQLite-backed cache for cross-encoder (resume_hash, job_id, model_version) pairs."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is not None:
            p = Path(db_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self.db_path = str(p)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA synchronous=NORMAL;")
        else:
            self.db_path = ":memory:"
            self.conn = sqlite3.connect(":memory:", check_same_thread=False)

        self._init_db()

    def _init_db(self) -> None:
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS rerank_cache (
                    resume_hash TEXT NOT NULL,
                    job_id TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    score REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (resume_hash, job_id, model_version)
                );
            """)

    def get(
        self,
        resume_hash: str,
        job_id: str,
        model_version: str,
    ) -> float | None:
        """Retrieve cached pair score or None if cache miss."""
        cursor = self.conn.execute(
            """
            SELECT score FROM rerank_cache
            WHERE resume_hash = ? AND job_id = ? AND model_version = ?;
            """,
            (resume_hash, job_id, model_version),
        )
        row = cursor.fetchone()
        return float(row[0]) if row else None

    def put(
        self,
        resume_hash: str,
        job_id: str,
        model_version: str,
        score: float,
    ) -> None:
        """Store pair score in cache."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO rerank_cache (resume_hash, job_id, model_version, score)
                VALUES (?, ?, ?, ?);
                """,
                (resume_hash, job_id, model_version, float(score)),
            )

    def get_batch(
        self,
        resume_hash: str,
        job_ids: Sequence[str],
        model_version: str,
    ) -> tuple[dict[str, float], list[str]]:
        """Query cache for a list of job IDs.

        Returns:
            cached_scores: {job_id: score}
            missing_job_ids: [job_id, ...] needing cross-encoder inference
        """
        if not job_ids:
            return {}, []

        cached_scores: dict[str, float] = {}
        missing: list[str] = []

        batch_size = 500
        for i in range(0, len(job_ids), batch_size):
            chunk = list(job_ids[i : i + batch_size])
            placeholders = ",".join("?" for _ in chunk)
            query = f"""
                SELECT job_id, score FROM rerank_cache
                WHERE resume_hash = ? AND model_version = ? AND job_id IN ({placeholders});
            """
            params = [resume_hash, model_version, *chunk]
            cursor = self.conn.execute(query, params)
            for j_id, sc in cursor.fetchall():
                cached_scores[j_id] = float(sc)

        for j_id in job_ids:
            if j_id not in cached_scores:
                missing.append(j_id)

        return cached_scores, missing

    def put_batch(
        self,
        resume_hash: str,
        pairs: Sequence[tuple[str, float]],
        model_version: str,
    ) -> None:
        """Store batch of (job_id, score) pairs into cache."""
        if not pairs:
            return

        records = [
            (resume_hash, str(job_id), model_version, float(score))
            for job_id, score in pairs
        ]
        with self.conn:
            self.conn.executemany(
                """
                INSERT OR REPLACE INTO rerank_cache (resume_hash, job_id, model_version, score)
                VALUES (?, ?, ?, ?);
                """,
                records,
            )

    def count(self) -> int:
        """Return total cached pair entries."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM rerank_cache;")
        return int(cursor.fetchone()[0])

    def clear(self) -> None:
        """Clear all entries in the cache."""
        with self.conn:
            self.conn.execute("DELETE FROM rerank_cache;")

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
