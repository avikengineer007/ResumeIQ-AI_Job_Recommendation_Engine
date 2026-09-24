"""Job dataset loader with validation, missingness profiling, and error reporting."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import ValidationError

from src.ingestion.validators import JobPostingSchema
from src.preprocessing.text_cleaner import clean_text


@dataclass
class JobValidationReport:
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    missingness_by_field: dict[str, int] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)


class JobLoader:
    """Reads raw job data from various file formats and applies schema validation."""

    def load_records(self, file_path: str | Path) -> list[dict[str, Any]]:
        """Read records from JSON, JSONL, CSV, or Parquet."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Job file not found: {p}")

        suffix = p.suffix.lower()
        if suffix == ".json":
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        elif suffix == ".jsonl":
            records = []
            with open(p, encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        records.append(json.loads(stripped))
            return records
        elif suffix == ".csv":
            df = pd.read_csv(p)
            return df.where(pd.notnull(df), None).to_dict(orient="records")
        elif suffix in (".parquet", ".pq"):
            df = pd.read_parquet(p)
            return df.where(pd.notnull(df), None).to_dict(orient="records")
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def load_and_validate(
        self,
        file_path: str | Path,
        clean_descriptions: bool = True,
    ) -> tuple[list[JobPostingSchema], JobValidationReport]:
        """Load, clean, and validate job postings, returning validated schemas and a report."""
        raw_records = self.load_records(file_path)
        report = JobValidationReport(total_records=len(raw_records))

        validated_jobs: list[JobPostingSchema] = []

        for idx, raw in enumerate(raw_records):
            # Track field presence for missingness profiling
            for k, v in raw.items():
                if v is None or v == "" or (isinstance(v, list) and len(v) == 0):
                    report.missingness_by_field[k] = (
                        report.missingness_by_field.get(k, 0) + 1
                    )

            # Clean description text if requested
            if (
                clean_descriptions
                and "description" in raw
                and isinstance(raw["description"], str)
            ):
                raw = dict(raw)
                raw["description"] = clean_text(raw["description"])

            try:
                schema = JobPostingSchema.model_validate(raw)
                validated_jobs.append(schema)
                report.valid_records += 1
            except ValidationError as err:
                report.invalid_records += 1
                report.errors.append(
                    {
                        "record_index": idx,
                        "record_id": raw.get("job_id", f"index_{idx}"),
                        "errors": err.errors(),
                    }
                )

        return validated_jobs, report
