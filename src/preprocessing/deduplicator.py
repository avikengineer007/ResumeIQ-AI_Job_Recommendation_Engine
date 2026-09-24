"""Exact and near-duplicate deduplication using SHA-256 and MinHash.

Supports:
1. Exact deduplication on normalized text hash (SHA-256).
2. Near-duplicate detection using MinHash shingling and Jaccard similarity.
3. Cluster management: preserves the earliest or most complete document.
"""

import hashlib
import re
from collections import defaultdict
from collections.abc import Callable
from typing import Any


def compute_exact_hash(text: str) -> str:
    """Compute SHA-256 hexadecimal digest of normalized text."""
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class MinHash:
    """MinHash signature generator using Carter-Wegman universal hashing."""

    def __init__(self, num_perm: int = 128, seed: int = 42, shingle_size: int = 3):
        self.num_perm = num_perm
        self.shingle_size = shingle_size
        self.prime = 2147483647  # Mersenne prime (2^31 - 1)

        # Deterministically initialize hash coefficients (a*x + b) % prime
        # Using a fixed seed for complete reproducibility
        import random

        rng = random.Random(seed)
        self.a_coeffs = [rng.randint(1, self.prime - 1) for _ in range(num_perm)]
        self.b_coeffs = [rng.randint(0, self.prime - 1) for _ in range(num_perm)]

    def create_shingles(self, text: str) -> set[str]:
        """Generate word n-gram shingles from text."""
        tokens = re.findall(r"\b\w+\b", text.lower())
        if len(tokens) < self.shingle_size:
            return set(tokens) if tokens else {"__empty__"}
        return {
            " ".join(tokens[i : i + self.shingle_size])
            for i in range(len(tokens) - self.shingle_size + 1)
        }

    def compute_signature(self, text: str) -> list[int]:
        """Compute the MinHash signature array for the given text."""
        shingles = self.create_shingles(text)
        signature = [self.prime] * self.num_perm

        for shingle in shingles:
            # 32-bit hash of shingle string
            h = int(hashlib.md5(shingle.encode("utf-8")).hexdigest()[:8], 16)
            for i in range(self.num_perm):
                val = (self.a_coeffs[i] * h + self.b_coeffs[i]) % self.prime
                if val < signature[i]:
                    signature[i] = val

        return signature

    @staticmethod
    def jaccard_similarity(sig1: list[int], sig2: list[int]) -> float:
        """Estimate Jaccard similarity by comparing fraction of matching signature slots."""
        if not sig1 or not sig2 or len(sig1) != len(sig2):
            return 0.0
        matches = sum(1 for a, b in zip(sig1, sig2, strict=True) if a == b)
        return matches / len(sig1)


def _default_extract_text(record: dict[str, Any]) -> str:
    return f"{record.get('title', '')} {record.get('company', '')} {record.get('description', '')}"


class Deduplicator:
    """End-to-end deduplication engine for job postings or resumes."""

    def __init__(
        self,
        near_duplicate_threshold: float = 0.85,
        num_perm: int = 128,
        shingle_size: int = 3,
        seed: int = 42,
    ):
        self.threshold = near_duplicate_threshold
        self.minhash = MinHash(num_perm=num_perm, seed=seed, shingle_size=shingle_size)

    def deduplicate(
        self,
        records: list[dict[str, Any]],
        id_key: str = "job_id",
        text_fn: Callable[[dict[str, Any]], str] | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
        """Deduplicate records by exact hash and near-duplicate MinHash similarity.

        Returns:
            Tuple of (unique_records, duplicate_clusters) where duplicate_clusters
            maps retained_id -> [list of duplicate discarded ids].
        """
        if text_fn is None:
            text_fn = _default_extract_text

        exact_seen: dict[str, dict[str, Any]] = {}
        exact_clusters: dict[str, list[str]] = defaultdict(list)

        # 1. Exact Deduplication
        for record in records:
            rec_id = str(record[id_key])
            t = text_fn(record)
            h = compute_exact_hash(t)
            if h in exact_seen:
                retained_id = str(exact_seen[h][id_key])
                exact_clusters[retained_id].append(rec_id)
            else:
                exact_seen[h] = record

        first_pass_records = list(exact_seen.values())

        # 2. Near-duplicate detection using MinHash signatures
        signatures: list[tuple[dict[str, Any], list[int]]] = [
            (rec, self.minhash.compute_signature(text_fn(rec)))
            for rec in first_pass_records
        ]

        unique_records: list[dict[str, Any]] = []
        discarded_ids: set[str] = set()
        final_clusters: dict[str, list[str]] = defaultdict(list)

        # Merge exact clusters into final clusters
        for rep_id, dups in exact_clusters.items():
            final_clusters[rep_id].extend(dups)

        for i, (rec_a, sig_a) in enumerate(signatures):
            id_a = str(rec_a[id_key])
            if id_a in discarded_ids:
                continue

            unique_records.append(rec_a)

            # Compare against remaining candidates
            for j in range(i + 1, len(signatures)):
                rec_b, sig_b = signatures[j]
                id_b = str(rec_b[id_key])
                if id_b in discarded_ids:
                    continue

                sim = MinHash.jaccard_similarity(sig_a, sig_b)
                if sim >= self.threshold:
                    discarded_ids.add(id_b)
                    final_clusters[id_a].append(id_b)

        return unique_records, dict(final_clusters)
