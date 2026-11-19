"""Pytest Automated Test Suite for Football Data Provider Coverage."""

import pytest
from marina.ingestion.providers.coverage_tester import ProviderCoverageTester
from marina.ingestion.providers.base import ValidationStatus


@pytest.mark.asyncio
async def test_provider_coverage_suite_execution():
    """Validates that all 4 providers are tested across 5 matches and enforce non-fabrication rules."""
    tester = ProviderCoverageTester()
    report = await tester.execute_full_coverage_suite()

    assert report["fixture_count"] == 5
    assert len(report["providers_evaluated"]) == 4

    # 1. FBref Ground Truth Baseline
    fbref_res = report["provider_results"]["FBREF_VERIFIED"]
    assert fbref_res["effective_coverage_pct"] == 100.0
    assert fbref_res["failed_validations"] == 0
    assert fbref_res["unsupported_metrics"] == 15  # 3 unsupported per match * 5 matches

    # 2. API-Football
    api_res = report["provider_results"]["API_FOOTBALL"]
    assert api_res["effective_coverage_pct"] == 100.0
    assert api_res["failed_validations"] == 0

    # 3. Sportmonks
    sm_res = report["provider_results"]["SPORTMONKS"]
    assert sm_res["effective_coverage_pct"] >= 90.0

    # 4. Critical Non-Fabrication Rule: Spatial Coordinates & xG MUST be NULL
    for prov_code, res in report["provider_results"].items():
        for match in res["matches"]:
            shot_xy = match.metrics["shot_coordinates_xy"]
            pass_xy = match.metrics["pass_coordinates_xy"]
            xg = match.metrics["expected_goals_xg"]

            assert shot_xy.normalized_value is None
            assert pass_xy.normalized_value is None
            assert xg.normalized_value is None
            assert shot_xy.validation_status == ValidationStatus.NOT_SUPPORTED
            assert pass_xy.validation_status == ValidationStatus.NOT_SUPPORTED
            assert xg.validation_status == ValidationStatus.NOT_SUPPORTED
