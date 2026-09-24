# AI-Powered Skill-Aware Semantic Job Search and Personalized Recommendation System

[![CI](https://github.com/organization/ai-job-recommendation-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/organization/ai-job-recommendation-engine/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A reproducible, research-grade, and production-ready job recommendation platform. Given a candidate's resume (PDF/DOCX), the system parses sections, extracts and normalizes skills against a curated taxonomy, retrieves candidates via hybrid search (BM25 + Dense FAISS index), reranks through a cross-encoder, applies personalization criteria, and delivers faithful, evidence-grounded explanations.

---

## Architecture Overview (10 Layers)

```
[ L1: React UI ] ──> [ L2: FastAPI Gateway ] ──> [ L3: Data Ingestion & PII Scrubbing ]
                                                      │
[ L6: Hybrid Search (BM25 + FAISS) ] <── [ L5: Repr ] <── [ L4: Parsing & Skill Normalization ]
         │
         ▼
[ L7: Cross-Encoder Reranking ]
         │
         ▼
[ L8: Personalization & Preferences ]
         │
         ▼
[ L9: Explainable AI (Evidence-Grounded) ]
         ▲
         │ (Unified Pipeline Code in src/)
[ L10: Evaluation & Benchmark Harness ]
```

---

## Directory Structure

```
ai-job-recommendation-engine/
├── .github/workflows/ci.yml      # Continuous integration (Ruff, Black, Pytest)
├── configs/                      # Central YAML configurations (no hardcoding)
├── data/                         # Data tier (raw, interim, processed, evaluation)
├── src/                          # Unified core pipeline code
│   ├── common/                   # Config loader, deterministic seed, structured logger, IO
│   ├── ingestion/                # Document and job loaders, schema validators
│   ├── preprocessing/            # Text cleaning, MinHash deduplication, section parsing
│   ├── pii/                      # PII detection and redaction with typed placeholders
│   ├── skill_extraction/         # PhraseMatcher & NER models
│   ├── skill_normalization/      # Taxonomy management, fuzzy/embedding mapping
│   ├── embeddings/               # Model wrappers, template builders, batch encoding
│   ├── retrieval/                # BM25, FAISS index, RRF / weighted fusion, filters
│   ├── reranking/                # Cross-encoder pair scoring, cache
│   ├── recommendation/           # Scoring engine, skill gap analysis, preference matching
│   ├── explainability/           # Evidence object builder, template explanations, verifier
│   └── evaluation/               # Ranking metrics (P@K, NDCG@K, MRR), statistical tests
├── api/                          # FastAPI routers, schemas, security, and dependencies
├── frontend/                     # React + TypeScript + Tailwind (Vite)
├── database/                     # PostgreSQL schemas, migrations, seeds
├── scripts/                      # Reproducible CLI runners
├── tests/                        # Unit, integration, model, e2e, security test suites
├── experiments/                  # Experiment configs, evaluation logs, ablation results
├── docs/                         # Architecture, methodology, research notes
└── deployment/                   # Dockerfiles, docker-compose, platform manifests
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Node.js LTS (for frontend)

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/organization/ai-job-recommendation-engine.git
cd ai-job-recommendation-engine

# Copy configuration template
cp .env.example .env

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start PostgreSQL via Docker Compose
```bash
docker compose up -d db
```

### 3. Run Automated Tests & Quality Checks
```bash
# Run linters and format checks
ruff check src api tests
black --check src api tests

# Run unit tests
pytest tests/unit
```

---

## Research Protocol Integrity
- **Frozen Protocol**: Dataset splits (60/20/20 by resume), evaluation metrics, and seeds are frozen prior to tuning.
- **Leakage Prevention**: All judged resume-job pairs reside in the same split as the candidate resume.
- **Zero Fabrication**: All results tables are marked TBD until populated by real reproducible benchmark runs.
- **Privacy First**: Sensitive attributes (gender, age, ethnicity, photo, religion) are strictly prohibited from extraction and recommendation logic.
