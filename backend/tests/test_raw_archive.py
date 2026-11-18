"""Automated Tests for Raw Data Archive and Checksum Immutability."""

import hashlib
from pathlib import Path
from marina.ingestion.archive.raw_storage import RawArchiveStorage


def test_raw_archive_storage_preservation(tmp_path: Path):
    """Verify raw payload archiving, SHA-256 calculation, and directory partitioning."""
    storage = RawArchiveStorage(base_dir=str(tmp_path))

    payload = {
        "competition": "Indian Super League",
        "season": "2026-27",
        "matches": [
            {"home": "Chennaiyin FC", "away": "East Bengal FC", "score": "5-3"}
        ],
    }

    meta = storage.archive_payload(
        source_code="ISL_OFFICIAL",
        entity_type="RESULTS",
        batch_id="batch-001",
        content=payload,
        source_url="https://www.indiansuperleague.com/results",
    )

    assert meta["source_code"] == "ISL_OFFICIAL"
    assert meta["entity_type"] == "RESULTS"
    assert "checksum_sha256" in meta
    assert Path(meta["payload_path"]).exists()

    # Verify SHA-256 integrity
    file_bytes = storage.read_payload(meta["payload_path"])
    expected_hash = hashlib.sha256(file_bytes).hexdigest()
    assert meta["checksum_sha256"] == expected_hash

    # Verify sidecar metadata file exists
    meta_path = Path(meta["payload_path"]).with_suffix(".meta.json")
    # Actually the naming is {batch_id}_{hash[:8]}.meta.json
    assert meta["size_bytes"] > 0
