"""Automated Tests for Entity Normalization and NULL Retention."""

from datetime import datetime, timezone
import pytest
from marina.ingestion.transformers.normalizer import FootballNormalizer
from marina.models.common import PlayerPosition


def test_team_canonical_resolution():
    """Verify various team representations and aliases resolve to canonical entities."""
    # Chennaiyin FC
    cfc_variants = ["Chennaiyin FC", "CFC", "chennaiyin", "Chennaiyin", "chennaiyinfc"]
    for variant in cfc_variants:
        res = FootballNormalizer.resolve_team(variant)
        assert res["slug"] == "chennaiyin-fc"
        assert res["short_name"] == "CFC"

    # East Bengal
    eb_variants = ["East Bengal FC", "SC East Bengal", "eastbengal", "EBFC"]
    for variant in eb_variants:
        res = FootballNormalizer.resolve_team(variant)
        assert res["slug"] == "east-bengal-fc"

    # Mohun Bagan SG
    mb_variants = ["Mohun Bagan SG", "Mohun Bagan Super Giant", "MBSG"]
    for variant in mb_variants:
        res = FootballNormalizer.resolve_team(variant)
        assert res["slug"] == "mohun-bagan-sg"


def test_position_normalization():
    """Verify free-text positions map to valid domain enums."""
    assert FootballNormalizer.normalize_position("Centre-Back") == PlayerPosition.CB
    assert FootballNormalizer.normalize_position("Goalkeeper") == PlayerPosition.GK
    assert FootballNormalizer.normalize_position("striker") == PlayerPosition.ST
    assert FootballNormalizer.normalize_position("attacking midfielder") == PlayerPosition.AM


def test_datetime_and_timezone_normalization():
    """Verify Indian Standard Time (IST) strings convert accurately to UTC datetime."""
    # 2026-11-07 19:30:00 IST is 14:00:00 UTC
    dt_str = "2026-11-07T19:30:00+05:30"
    utc_dt = FootballNormalizer.normalize_datetime(dt_str)
    assert utc_dt.tzinfo == timezone.utc
    assert utc_dt.hour == 14
    assert utc_dt.minute == 0


def test_strict_null_metric_preservation():
    """CRITICAL RULE: Missing values must remain None, NEVER converted to 0."""
    # Empty string, N/A, dash, null, None
    assert FootballNormalizer.normalize_nullable_metric(None) is None
    assert FootballNormalizer.normalize_nullable_metric("") is None
    assert FootballNormalizer.normalize_nullable_metric("   ") is None
    assert FootballNormalizer.normalize_nullable_metric("N/A") is None
    assert FootballNormalizer.normalize_nullable_metric("-") is None
    assert FootballNormalizer.normalize_nullable_metric("null") is None

    # Observed zero MUST be preserved as 0
    assert FootballNormalizer.normalize_nullable_metric(0, int) == 0
    assert FootballNormalizer.normalize_nullable_metric("0", int) == 0
    assert FootballNormalizer.normalize_nullable_metric(0.0, float) == 0.0

    # Measured positive numbers
    assert FootballNormalizer.normalize_nullable_metric("2.85", float) == 2.85
    assert FootballNormalizer.normalize_nullable_metric("5", int) == 5
