"""BM25 keyword search baseline module for job retrieval.

Implements BM25Okapi retrieval over job postings with:
- Configurable field boosting (title, skills, description)
- Tokenization, lowercasing, and stopword filtering
- Document ID indexing and score extraction
- Serialization and loading for reproducible benchmark evaluation
"""

import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi

STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "aren't",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can't",
    "cannot",
    "could",
    "couldn't",
    "did",
    "didn't",
    "do",
    "does",
    "doesn't",
    "doing",
    "don't",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "hadn't",
    "has",
    "hasn't",
    "have",
    "haven't",
    "having",
    "he",
    "he'd",
    "he'll",
    "he's",
    "her",
    "here",
    "here's",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "how's",
    "i",
    "i'd",
    "i'll",
    "i'm",
    "i've",
    "if",
    "in",
    "into",
    "is",
    "isn't",
    "it",
    "it's",
    "its",
    "itself",
    "let's",
    "me",
    "more",
    "most",
    "mustn't",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "ought",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "shan't",
    "she",
    "she'd",
    "she'll",
    "she's",
    "should",
    "shouldn't",
    "so",
    "some",
    "such",
    "than",
    "that",
    "that's",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "there's",
    "these",
    "they",
    "they'd",
    "they'll",
    "they're",
    "they've",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "wasn't",
    "we",
    "we'd",
    "we'll",
    "we're",
    "we've",
    "were",
    "weren't",
    "what",
    "what's",
    "when",
    "when's",
    "where",
    "where's",
    "which",
    "while",
    "who",
    "who's",
    "whom",
    "why",
    "why's",
    "with",
    "won't",
    "would",
    "wouldn't",
    "you",
    "you'd",
    "you'll",
    "you're",
    "you've",
    "your",
    "yours",
    "yourself",
    "yourselves",
}


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric words, filtering stopwords."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9_+#.-]+\b", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


class BM25Retriever:
    """BM25Okapi keyword retriever with field-boosted indexing."""

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        title_boost: float = 2.0,
        skills_boost: float = 1.5,
        description_boost: float = 1.0,
    ) -> None:
        self.k1 = k1
        self.b = b
        self.title_boost = title_boost
        self.skills_boost = skills_boost
        self.description_boost = description_boost

        self.doc_ids: list[str] = []
        self.corpus_tokens: list[list[str]] = []
        self.bm25: BM25Okapi | None = None

    def _build_document_tokens(self, doc: dict[str, Any]) -> list[str]:
        """Tokenize a document applying repetition multipliers for field boosts."""
        tokens: list[str] = []

        title_toks = tokenize(str(doc.get("title", "")))
        tokens.extend(title_toks * int(round(self.title_boost)))

        # Skills field can be list or string
        skills_val = doc.get("skills", [])
        if isinstance(skills_val, list):
            skills_text = " ".join(str(s) for s in skills_val)
        else:
            skills_text = str(skills_val)
        skills_toks = tokenize(skills_text)
        tokens.extend(skills_toks * int(round(self.skills_boost)))

        desc_toks = tokenize(str(doc.get("description", "")))
        tokens.extend(desc_toks * int(round(self.description_boost)))

        return tokens

    def index_documents(self, documents: Sequence[dict[str, Any]]) -> None:
        """Index a collection of documents."""
        self.doc_ids = []
        self.corpus_tokens = []

        for doc in documents:
            doc_id = str(doc.get("id", doc.get("job_id", len(self.doc_ids))))
            toks = self._build_document_tokens(doc)
            self.doc_ids.append(doc_id)
            self.corpus_tokens.append(toks)

        if self.corpus_tokens:
            self.bm25 = BM25Okapi(self.corpus_tokens, k1=self.k1, b=self.b)
        else:
            self.bm25 = None

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Search indexed documents by query string, returning ranked (doc_id, score)."""
        if self.bm25 is None or not self.doc_ids:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)
        scored_pairs = [
            (self.doc_ids[idx], float(score))
            for idx, score in enumerate(scores)
            if score > 0.0
        ]
        scored_pairs.sort(key=lambda x: x[1], reverse=True)
        return scored_pairs[:top_k]

    def save(self, output_dir: str | Path) -> None:
        """Persist BM25 index corpus and configuration to disk."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        data = {
            "k1": self.k1,
            "b": self.b,
            "title_boost": self.title_boost,
            "skills_boost": self.skills_boost,
            "description_boost": self.description_boost,
            "doc_ids": self.doc_ids,
            "corpus_tokens": self.corpus_tokens,
        }
        with open(out / "bm25_index.json", "w", encoding="utf-8") as f:
            json.dump(data, f)

    @classmethod
    def load(cls, index_dir: str | Path) -> "BM25Retriever":
        """Load BM25 retriever from saved index directory."""
        inp = Path(index_dir)
        with open(inp / "bm25_index.json", encoding="utf-8") as f:
            data = json.load(f)

        retriever = cls(
            k1=data.get("k1", 1.5),
            b=data.get("b", 0.75),
            title_boost=data.get("title_boost", 2.0),
            skills_boost=data.get("skills_boost", 1.5),
            description_boost=data.get("description_boost", 1.0),
        )
        retriever.doc_ids = data.get("doc_ids", [])
        retriever.corpus_tokens = data.get("corpus_tokens", [])
        if retriever.corpus_tokens:
            retriever.bm25 = BM25Okapi(
                retriever.corpus_tokens, k1=retriever.k1, b=retriever.b
            )
        return retriever
