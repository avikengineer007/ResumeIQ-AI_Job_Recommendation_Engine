"""Central configuration loader and schema definitions.

Follows the principle:
No hard-coded paths, seeds, model names, or thresholds.
All tunable settings are managed via YAML files in configs/ with optional environment overrides.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class SystemSettings(BaseModel):
    seed: int = Field(default=42, description="Global random seed for reproducibility")
    app_name: str = Field(default="ai-job-recommendation-engine")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)


class PathSettings(BaseModel):
    data_raw: Path = Field(default=Path("data/raw"))
    data_interim: Path = Field(default=Path("data/interim"))
    data_processed: Path = Field(default=Path("data/processed"))
    data_evaluation: Path = Field(default=Path("data/evaluation"))
    models_dir: Path = Field(default=Path("models"))
    configs_dir: Path = Field(default=Path("configs"))
    experiments_dir: Path = Field(default=Path("experiments"))
    splits_file: Path = Field(default=Path("data/processed/splits.json"))


class DatasetSettings(BaseModel):
    train_ratio: float = Field(default=0.60)
    val_ratio: float = Field(default=0.20)
    test_ratio: float = Field(default=0.20)
    random_state: int = Field(default=42)
    group_by: str = Field(default="resume_id")

    @field_validator("test_ratio")
    @classmethod
    def validate_ratios(cls, v: float, info: Any) -> float:
        data = info.data
        train = data.get("train_ratio", 0.60)
        val = data.get("val_ratio", 0.20)
        total = round(train + val + v, 5)
        if total != 1.0:
            raise ValueError(f"Dataset split ratios must sum to 1.0, got {total}")
        return v


class PIISettings(BaseModel):
    mask_names: bool = Field(default=True)
    mask_emails: bool = Field(default=True)
    mask_phones: bool = Field(default=True)
    mask_addresses: bool = Field(default=True)
    mask_urls: bool = Field(default=True)
    replacement_strategy: str = Field(default="typed_placeholder")


class DatabaseSettings(BaseModel):
    echo_sql: bool = Field(default=False)
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    url: str | None = Field(default=None)


class EmbeddingCandidate(BaseModel):
    name: str
    dimension: int
    max_seq_length: int
    revision: str = "main"
    prefix_query: str = ""
    prefix_passage: str = ""


class EmbeddingSettings(BaseModel):
    default_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    normalize: bool = Field(default=True)
    batch_size: int = Field(default=64)
    candidates: list[EmbeddingCandidate] = Field(default_factory=list)


class RerankerCandidate(BaseModel):
    name: str
    revision: str = "main"


class RerankerSettings(BaseModel):
    default_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
    max_length: int = Field(default=512)
    batch_size: int = Field(default=32)
    candidates: list[RerankerCandidate] = Field(default_factory=list)


class SpacySettings(BaseModel):
    model_name: str = Field(default="en_core_web_sm")
    ner_labels: list[str] = Field(
        default_factory=lambda: ["SKILL", "DEGREE", "EXPERIENCE", "ORGANIZATION"]
    )


class BM25Settings(BaseModel):
    k1: float = Field(default=1.5)
    b: float = Field(default=0.75)
    title_boost: float = Field(default=2.0)
    skills_boost: float = Field(default=1.5)
    description_boost: float = Field(default=1.0)


class VectorSearchSettings(BaseModel):
    index_type: str = Field(default="IndexFlatIP")
    hnsw_m: int = Field(default=32)
    hnsw_ef_construction: int = Field(default=200)
    hnsw_ef_search: int = Field(default=64)


class FusionSettings(BaseModel):
    default_mode: str = Field(default="rrf")
    rrf_k: int = Field(default=60)
    weighted_weights: dict[str, float] = Field(
        default_factory=lambda: {"bm25": 0.35, "vector": 0.45, "skill": 0.20}
    )


class SkillMatchingSettings(BaseModel):
    exact_weight: float = Field(default=1.0)
    parent_discount: float = Field(default=0.60)
    related_discount: float = Field(default=0.40)
    fuzzy_threshold: float = Field(default=92.0)
    embedding_similarity_threshold: float = Field(default=0.82)


class RerankingSettings(BaseModel):
    top_n: int = Field(default=50)
    top_k: int = Field(default=10)


class PersonalizationSettings(BaseModel):
    weights: dict[str, float] = Field(
        default_factory=lambda: {
            "s_rerank": 0.35,
            "s_sem": 0.20,
            "s_skill": 0.25,
            "s_exp": 0.10,
            "s_role": 0.05,
            "s_loc": 0.025,
            "s_mode": 0.025,
            "s_pref": 0.0,
            "s_inter": 0.0,
        }
    )


class AppConfig(BaseModel):
    """Unified application configuration object."""

    system: SystemSettings = Field(default_factory=SystemSettings)
    paths: PathSettings = Field(default_factory=PathSettings)
    dataset: DatasetSettings = Field(default_factory=DatasetSettings)
    pii: PIISettings = Field(default_factory=PIISettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    embeddings: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    rerankers: RerankerSettings = Field(default_factory=RerankerSettings)
    spacy: SpacySettings = Field(default_factory=SpacySettings)
    bm25: BM25Settings = Field(default_factory=BM25Settings)
    vector_search: VectorSearchSettings = Field(default_factory=VectorSearchSettings)
    fusion: FusionSettings = Field(default_factory=FusionSettings)
    skill_matching: SkillMatchingSettings = Field(default_factory=SkillMatchingSettings)
    reranking: RerankingSettings = Field(default_factory=RerankingSettings)
    personalization: PersonalizationSettings = Field(
        default_factory=PersonalizationSettings
    )


def _load_yaml(file_path: Path) -> dict[str, Any]:
    if not file_path.exists():
        return {}
    with open(file_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def load_config(config_dir: str | Path | None = None) -> AppConfig:
    """Load configuration from YAML files in config_dir, applying environment overrides."""
    if config_dir is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
        configs_path = base_dir / "configs"
    else:
        configs_path = Path(config_dir)

    main_yaml = _load_yaml(configs_path / "config.yaml")
    model_yaml = _load_yaml(configs_path / "model_config.yaml")
    retrieval_yaml = _load_yaml(configs_path / "retrieval_config.yaml")

    merged: dict[str, Any] = {}
    merged.update(main_yaml)
    merged.update(model_yaml)
    merged.update(retrieval_yaml)

    # Optional Environment variable overrides
    if os.getenv("APP_SEED"):
        merged.setdefault("system", {})["seed"] = int(os.environ["APP_SEED"])
    if os.getenv("ENVIRONMENT"):
        merged.setdefault("system", {})["environment"] = os.environ["ENVIRONMENT"]
    if os.getenv("DATABASE_URL"):
        merged.setdefault("database", {})["url"] = os.environ["DATABASE_URL"]

    return AppConfig.model_validate(merged)


@lru_cache
def get_config() -> AppConfig:
    """Get cached singleton configuration instance."""
    return load_config()
