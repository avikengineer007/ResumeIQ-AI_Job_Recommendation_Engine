"""Unit tests for safe file IO utilities."""

from pathlib import Path

from src.common.io import read_json, read_yaml, write_json, write_yaml


def test_json_roundtrip(tmp_path: Path):
    """Verify write_json and read_json preserve data structures."""
    target_file = tmp_path / "test.json"
    data = {"key": "value", "list": [1, 2, 3], "nested": {"a": True}}

    write_json(target_file, data)
    assert target_file.exists()

    loaded = read_json(target_file)
    assert loaded == data


def test_yaml_roundtrip(tmp_path: Path):
    """Verify write_yaml and read_yaml preserve configuration mapping."""
    target_file = tmp_path / "test.yaml"
    data = {"system": {"seed": 42, "debug": True}, "tags": ["search", "nlp"]}

    write_yaml(target_file, data)
    assert target_file.exists()

    loaded = read_yaml(target_file)
    assert loaded == data
