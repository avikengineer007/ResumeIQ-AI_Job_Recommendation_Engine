# Contributing to ResumeIQ

First off, thank you for considering contributing to **ResumeIQ**! It is people like you that make open-source AI tools such a fantastic ecosystem.

---

## 📜 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 🛠️ Getting Started

### 1. Fork and Clone
```bash
git clone https://github.com/avikengineer007/ResumeIQ-AI_Job_Recommendation_Engine.git
cd ResumeIQ-AI_Job_Recommendation_Engine
```

### 2. Set Up Your Environment
Ensure you have **Python 3.11+** installed.
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 3. Verify Existing Tests
```bash
pytest tests/
ruff check src api tests
black --check src api tests
```

---

## 🌿 Branching Strategy & Git Workflow

- **`main`**: Production-ready, fully tested code.
- Feature branches: `feat/<feature-name>`
- Bug fixes: `fix/<bug-name>`
- Documentation: `docs/<doc-update>`
- Experiments: `exp/<experiment-name>`

### Commit Message Guidelines
We adhere to **Conventional Commits**:
- `feat: add hybrid score thresholding to FAISS retriever`
- `fix: resolve PII regex masking for international phone numbers`
- `docs: update architecture diagram with layer descriptions`
- `test: add unit tests for cross-encoder reranking cache`
- `refactor: optimize token batching in dense embedder`

---

## 🧪 Testing Guidelines

Any contribution that introduces new features or alters pipeline scoring must include appropriate test coverage:
1. **Unit tests**: Fast tests covering individual methods and modules located in `tests/unit/`.
2. **Integration tests**: Multi-component tests in `tests/integration/`.
3. **Reproducibility**: Ensure seeds (`configs/seed.yaml` or global random state) are respected so test runs are deterministic.

To run tests with coverage reporting:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

---

## 🎨 Code Style and Quality

We enforce strict formatting and linting via:
- **Ruff**: Modern, ultra-fast Python linter
- **Black**: Deterministic code formatter

Before opening a pull request, run:
```bash
ruff check src api tests --fix
black src api tests
```

---

## 📬 Submitting a Pull Request (PR)

1. Ensure all tests and linters pass locally.
2. Push your branch to your fork.
3. Open a Pull Request targeting the `main` branch.
4. Fill out the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md) completely with a summary of changes and testing evidence.
5. The core maintainers (**Avik Ghosh** & **Sumouna Ghosh**) will review your submission promptly!
