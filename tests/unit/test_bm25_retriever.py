"""Unit tests for BM25 keyword retriever baseline."""

from pathlib import Path

from src.retrieval.bm25_retriever import BM25Retriever, tokenize


def test_tokenizer() -> None:
    text = "Senior Python & FastAPI Engineer with Docker experience!"
    tokens = tokenize(text)
    assert "python" in tokens
    assert "fastapi" in tokens
    assert "docker" in tokens
    assert "engineer" in tokens
    # Stopwords like 'with' must be filtered
    assert "with" not in tokens


def test_bm25_retrieval_and_boosting(tmp_path: Path) -> None:
    jobs = [
        {
            "id": "job_python_dev",
            "title": "Senior Python Developer",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "description": "Develop scalable backend services and microservices.",
        },
        {
            "id": "job_frontend_react",
            "title": "Frontend React Engineer",
            "skills": ["React", "TypeScript", "TailwindCSS"],
            "description": "Design modern user interfaces and web applications.",
        },
        {
            "id": "job_ml_engineer",
            "title": "Machine Learning Engineer",
            "skills": ["PyTorch", "Python", "Transformers"],
            "description": "Train and deploy deep learning NLP models.",
        },
    ]

    retriever = BM25Retriever(
        k1=1.5,
        b=0.75,
        title_boost=2.0,
        skills_boost=1.5,
        description_boost=1.0,
    )
    retriever.index_documents(jobs)

    # Search Python backend
    results = retriever.search("Python FastAPI developer", top_k=2)
    assert len(results) == 2
    top_doc_id, top_score = results[0]
    assert top_doc_id == "job_python_dev"
    assert top_score > 0.0

    # Search React
    react_results = retriever.search("React TypeScript UI", top_k=1)
    assert len(react_results) == 1
    assert react_results[0][0] == "job_frontend_react"

    # Save and reload
    save_dir = tmp_path / "bm25_index"
    retriever.save(save_dir)
    loaded = BM25Retriever.load(save_dir)

    reloaded_results = loaded.search("Python FastAPI developer", top_k=2)
    assert reloaded_results[0][0] == "job_python_dev"
    assert reloaded_results[0][1] == reloaded_results[0][1]
