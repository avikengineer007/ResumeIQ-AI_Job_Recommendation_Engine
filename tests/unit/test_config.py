"""Unit tests for configuration loading and validation."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from src.common.config import AppConfig, DatasetSettings, load_config


def test_load_config_valid(project_root: Path):
    """Test loading valid configurations from configs/."""
    cfg = load_config(project_root / "configs")
    assert cfg.system.seed == 42
    assert cfg.dataset.train_ratio == 0.60
    assert cfg.dataset.val_ratio == 0.20
    assert cfg.dataset.test_ratio == 0.20
    assert cfg.bm25.k1 == 1.5
    assert cfg.vector_search.index_type == "IndexFlatIP"
    assert cfg.embeddings.default_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert len(cfg.embeddings.candidates) >= 3


def test_dataset_split_ratio_validation():
    """Verify that dataset splits must sum to 1.0."""
    with pytest.raises(ValidationError):
        DatasetSettings(train_ratio=0.7, val_ratio=0.2, test_ratio=0.3)


def test_config_env_overrides(project_root: Path, monkeypatch: pytest.MonkeyPatch):
    """Verify environment variables correctly override file configurations."""
    monkeypatch.setenv("APP_SEED", "999")
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/testdb")

    cfg = load_config(project_root / "configs")
    assert cfg.system.seed == 999
    assert cfg.system.environment == "testing"
    assert cfg.database.url == "postgresql://test:test@localhost:5432/testdb"


def test_missing_config_directory_uses_defaults():
    """Test that a non-existent config path falls back to default values."""
    cfg = load_config(Path("/non/existent/path"))
    assert isinstance(cfg, AppConfig)
    assert cfg.system.seed == 42
