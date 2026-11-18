"""Manual File Ingestion Extractor (CSV / JSON)."""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Union


class ManualFileExtractor:
    """Parses and extracts structured football data from manually uploaded CSV or JSON files."""

    def __init__(self, source_code: str = "MANUAL_CURATION") -> None:
        self.source_code = source_code
        self.source_name = "Manually Verified File Ingestion"

    def parse_file(self, file_path: Union[str, Path], entity_type: str) -> Dict[str, Any]:
        """Parses a CSV or JSON file into standard ingestion payload format."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        extracted_at = datetime.now(timezone.utc).isoformat()
        extension = path.suffix.lower()

        if extension == ".json":
            with open(path, "r", encoding="utf-8") as f:
                content = json.load(f)
            return {
                "source_code": self.source_code,
                "source_file": str(path.resolve()),
                "extracted_at": extracted_at,
                "entity_type": entity_type,
                "payload": content,
            }

        elif extension == ".csv":
            rows: List[Dict[str, Any]] = []
            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Clean whitespace from keys and values
                    cleaned_row = {
                        k.strip(): (v.strip() if v is not None and v.strip() != "" else None)
                        for k, v in row.items()
                        if k is not None
                    }
                    rows.append(cleaned_row)

            return {
                "source_code": self.source_code,
                "source_file": str(path.resolve()),
                "extracted_at": extracted_at,
                "entity_type": entity_type,
                "payload": rows,
            }

        else:
            raise ValueError(f"Unsupported file format '{extension}'. Expected .csv or .json.")
