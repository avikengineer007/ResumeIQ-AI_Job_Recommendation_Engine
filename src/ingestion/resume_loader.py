"""Resume loader supporting structured formats (JSON/JSONL/CSV/Parquet) and document formats (PDF/DOCX)."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import ValidationError

from src.ingestion.validators import ResumeSchema
from src.pii.anonymizer import PIIAnonymizer
from src.preprocessing.text_cleaner import clean_text


@dataclass
class ResumeValidationReport:
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    pii_redacted_count: int = 0
    missingness_by_field: dict[str, int] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)


class ResumeLoader:
    """Loads and validates structured resume records or raw document files."""

    def __init__(self, anonymizer: PIIAnonymizer | None = None):
        self.anonymizer = anonymizer or PIIAnonymizer()

    def extract_text_from_file(self, file_path: str | Path) -> str:
        """Extract raw plain text from PDF or DOCX file."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")

        suffix = p.suffix.lower()
        if suffix == ".pdf":
            import pdfplumber

            pages_text = []
            with pdfplumber.open(p) as pdf:
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    pages_text.append(t)
            return "\n\n".join(pages_text)

        elif suffix in (".docx", ".doc"):
            import docx

            doc = docx.Document(p)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(paragraphs)

        elif suffix in (".txt", ".md"):
            with open(p, encoding="utf-8", errors="ignore") as f:
                return f.read()

        else:
            raise ValueError(f"Unsupported document format: {suffix}")

    def load_structured_records(self, file_path: str | Path) -> list[dict[str, Any]]:
        """Load structured resume data from JSON, JSONL, CSV, or Parquet."""
        p = Path(file_path)
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
            raise ValueError(f"Unsupported structured file format: {suffix}")

    def load_and_validate(
        self,
        file_path: str | Path,
        mask_pii: bool = True,
    ) -> tuple[list[ResumeSchema], ResumeValidationReport]:
        """Load structured resume records, apply PII scrubbing, and validate schemas."""
        raw_records = self.load_structured_records(file_path)
        report = ResumeValidationReport(total_records=len(raw_records))
        validated_resumes: list[ResumeSchema] = []

        for idx, raw in enumerate(raw_records):
            for k, v in raw.items():
                if v is None or v == "" or (isinstance(v, list) and len(v) == 0):
                    report.missingness_by_field[k] = (
                        report.missingness_by_field.get(k, 0) + 1
                    )

            record_copy = dict(raw)
            # If raw_text is present, clean and scrub PII
            if "raw_text" in record_copy and isinstance(record_copy["raw_text"], str):
                cleaned = clean_text(record_copy["raw_text"])
                if mask_pii:
                    anonymized_text, pii_rep = self.anonymizer.anonymize(cleaned)
                    record_copy["raw_text"] = anonymized_text
                    record_copy["pii_removed"] = True
                    report.pii_redacted_count += pii_rep.total_spans_redacted
                else:
                    record_copy["raw_text"] = cleaned

            try:
                schema = ResumeSchema.model_validate(record_copy)
                validated_resumes.append(schema)
                report.valid_records += 1
            except ValidationError as err:
                report.invalid_records += 1
                report.errors.append(
                    {
                        "record_index": idx,
                        "record_id": raw.get("resume_id", f"index_{idx}"),
                        "errors": err.errors(),
                    }
                )

        return validated_resumes, report
