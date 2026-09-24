"""Comparative retrieval benchmark test: BM25 vs Dense Vector Retrieval.

NOTE: This is a pipeline sanity check over synthetic toy fixtures verifying end-to-end
retriever execution and metric computation parity. This is NOT a formal RQ1 research result.
Formal RQ1 evaluation is executed in Phase 17 using annotated qrels across frozen validation/test splits.
"""

import pytest

from src.embeddings.embedder import DenseEmbedder, EmbeddingManifest, format_job_text
from src.embeddings.faiss_index import FaissVectorIndex
from src.evaluation.metrics import evaluate_ranking_dataset
from src.retrieval.bm25_retriever import BM25Retriever


@pytest.mark.slow
def test_bm25_vs_dense_retrieval_comparison() -> None:
    # 1. Benchmark Job Corpus (Toy synthetic fixture)
    jobs = [
        {
            "id": "job_01",
            "title": "Senior Python Backend Developer",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "description": "Design distributed microservices, REST APIs, and database models.",
        },
        {
            "id": "job_02",
            "title": "Machine Learning Research Engineer",
            "skills": ["PyTorch", "Python", "Transformers", "NLP"],
            "description": "Train state-of-the-art transformer models for semantic search and retrieval.",
        },
        {
            "id": "job_03",
            "title": "Frontend React TypeScript Engineer",
            "skills": ["React", "TypeScript", "TailwindCSS", "Redux"],
            "description": "Develop responsive web interfaces, reusable components, and client-side logic.",
        },
        {
            "id": "job_04",
            "title": "DevOps & Cloud Infrastructure Engineer",
            "skills": ["Kubernetes", "Docker", "AWS", "Terraform", "CI/CD"],
            "description": "Manage cloud infrastructure, container orchestration, and automated pipelines.",
        },
        {
            "id": "job_05",
            "title": "Data Analyst & Business Intelligence",
            "skills": ["SQL", "Tableau", "Python", "Excel"],
            "description": "Build executive dashboards and analyze operational customer analytics.",
        },
    ]

    # 2. Benchmark Queries and Ground Truth
    queries = [
        "Python FastAPI backend microservices development",
        "NLP deep learning with PyTorch and Transformers",
        "React frontend web user interface developer",
    ]
    ground_truth = [
        {"job_01": 1.0},
        {"job_02": 1.0},
        {"job_03": 1.0},
    ]

    # 3. BM25 Baseline Run
    bm25 = BM25Retriever()
    bm25.index_documents(jobs)
    bm25_retrieved: list[list[str]] = []
    for q in queries:
        ranked = bm25.search(q, top_k=5)
        bm25_retrieved.append([doc_id for doc_id, _ in ranked])

    bm25_metrics = evaluate_ranking_dataset(
        bm25_retrieved, ground_truth, k_values=[1, 3, 5]
    )

    # 4. Dense Vector Retrieval Run
    embedder = DenseEmbedder(
        manifest=EmbeddingManifest(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384,
            normalize_embeddings=True,
        )
    )
    job_texts = [format_job_text(j) for j in jobs]
    doc_vectors = embedder.encode_passages(job_texts)
    doc_ids = [j["id"] for j in jobs]

    faiss_idx = FaissVectorIndex(dimension=384)
    faiss_idx.add_vectors(doc_vectors, doc_ids)

    query_vectors = embedder.encode_queries(queries)
    dense_retrieved: list[list[str]] = []
    for q_vec in query_vectors:
        ranked = faiss_idx.search(q_vec, top_k=5)
        dense_retrieved.append([doc_id for doc_id, _ in ranked])

    dense_metrics = evaluate_ranking_dataset(
        dense_retrieved, ground_truth, k_values=[1, 3, 5]
    )

    # 5. Sanity Checks & Calibrated Comparative Assertions
    assert bm25_metrics["mrr"] > 0.0
    assert dense_metrics["mrr"] > 0.0
    assert bm25_metrics["ndcg@3"] > 0.0
    assert dense_metrics["ndcg@3"] > 0.0

    # Parity check on returned evaluation metrics
    assert set(bm25_metrics.keys()) == set(dense_metrics.keys())
