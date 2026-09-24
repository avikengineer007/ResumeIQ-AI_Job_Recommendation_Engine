"""Shared fixtures for pytest test suites."""

from pathlib import Path

import pytest

from src.common.config import AppConfig, load_config
from src.common.seed import set_seed


@pytest.fixture(autouse=True)
def reset_seed():
    """Ensure every test starts with deterministic seed 42."""
    set_seed(42)


@pytest.fixture
def project_root() -> Path:
    """Return the absolute path to the repository root."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def sample_config(project_root: Path) -> AppConfig:
    """Load configuration from the project configs directory."""
    return load_config(project_root / "configs")
