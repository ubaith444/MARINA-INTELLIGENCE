"""Raw Data Archive Storage Service.

Preserves immutable raw payloads (JSON/HTML/CSV) with SHA-256 checksums,
source URLs, timestamps, and batch tracking.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union


class RawArchiveStorage:
    """Manages immutable raw data archiving partitioned by source and date."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            # Default to backend/data/raw_archive
            backend_root = Path(__file__).resolve().parent.parent.parent.parent
            self.base_dir = backend_root / "data" / "raw_archive"

        self.base_dir.mkdir(parents=True, exist_ok=True)

    def archive_payload(
        self,
        source_code: str,
        entity_type: str,
        batch_id: str,
        content: Union[str, bytes, Dict[str, Any], list],
        source_url: Optional[str] = None,
        extension: str = "json",
    ) -> Dict[str, Any]:
        """Saves a raw payload to the immutable archive.

        Returns metadata dictionary containing sha256, path, timestamp, and size.
        """
        now = datetime.now(timezone.utc)
        date_partition = now.strftime("%Y%m%d")

        # Normalize content to bytes
        if isinstance(content, (dict, list)):
            content_bytes = json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")
            if not extension:
                extension = "json"
        elif isinstance(content, str):
            content_bytes = content.encode("utf-8")
        elif isinstance(content, bytes):
            content_bytes = content
        else:
            content_bytes = str(content).encode("utf-8")

        # Compute SHA-256 checksum
        sha256_hash = hashlib.sha256(content_bytes).hexdigest()

        # Destination directory
        target_dir = self.base_dir / source_code.lower() / entity_type.lower() / date_partition
        target_dir.mkdir(parents=True, exist_ok=True)

        # File naming: {batch_id}_{sha256_prefix}.{extension}
        filename = f"{batch_id}_{sha256_hash[:8]}.{extension.lstrip('.')}"
        file_path = target_dir / filename

        # Write immutable file (if already exists with same checksum, do not overwrite)
        if not file_path.exists():
            with open(file_path, "wb") as f:
                f.write(content_bytes)

        metadata = {
            "source_code": source_code,
            "entity_type": entity_type,
            "batch_id": batch_id,
            "source_url": source_url,
            "checksum_sha256": sha256_hash,
            "payload_path": str(file_path.resolve()),
            "size_bytes": len(content_bytes),
            "archived_at": now.isoformat(),
        }

        # Also store sidecar metadata JSON
        meta_filename = f"{batch_id}_{sha256_hash[:8]}.meta.json"
        meta_path = target_dir / meta_filename
        if not meta_path.exists():
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

        return metadata

    def read_payload(self, file_path: str) -> bytes:
        """Reads stored payload from archive, verifying file existence."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Archive file not found: {file_path}")
        with open(path, "rb") as f:
            return f.read()
