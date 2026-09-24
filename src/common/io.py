"""Safe file I/O utilities supporting JSON, YAML, and atomic file writes."""

import json
import tempfile
from pathlib import Path
from typing import Any

import yaml


def read_json(file_path: str | Path) -> Any:
    """Read and parse a JSON file."""
    p = Path(file_path)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def write_json(file_path: str | Path, data: Any, indent: int = 2) -> Path:
    """Atomically write data as JSON to prevent partial/corrupt writes."""
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "w", dir=p.parent, delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(data, tmp, indent=indent, default=str)
        tmp_name = tmp.name

    temp_path = Path(tmp_name)
    temp_path.replace(p)
    return p


def read_yaml(file_path: str | Path) -> dict[str, Any]:
    """Read and parse a YAML file."""
    p = Path(file_path)
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(file_path: str | Path, data: dict[str, Any]) -> Path:
    """Atomically write data as YAML."""
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "w", dir=p.parent, delete=False, encoding="utf-8"
    ) as tmp:
        yaml.safe_dump(data, tmp, sort_keys=False)
        tmp_name = tmp.name

    temp_path = Path(tmp_name)
    temp_path.replace(p)
    return p
