"""Automated Tests for Ingestion Data Extractors."""

import json
from pathlib import Path
import pytest

from marina.ingestion.extractors.aiff import AIFFExtractor
from marina.ingestion.extractors.chennaiyin_fc import ChennaiyinFCOfficialExtractor
from marina.ingestion.extractors.isl_official import ISLOfficialExtractor
from marina.ingestion.extractors.manual_files import ManualFileExtractor
from marina.ingestion.extractors.statsbomb import StatsBombOpenDataAdapter


@pytest.mark.asyncio
async def test_isl_official_extractor():
    """Verify ISL official extractor extracts fixtures, results, and standings."""
    extractor = ISLOfficialExtractor(mock_mode=True)

    # 1. Fixtures
    fixtures_data = await extractor.extract_fixtures(season_code="2026-27")
    assert fixtures_data["source_code"] == "ISL_OFFICIAL"
    assert len(fixtures_data["fixtures"]) >= 3
    for f in fixtures_data["fixtures"]:
        assert f["match_status"] == "SCHEDULED"
        assert f["home_score"] is None
        assert f["away_score"] is None

    # 2. Results (includes Chennaiyin FC 5–3 East Bengal on 7 Nov 2026)
    results_data = await extractor.extract_results(season_code="2026-27")
    assert results_data["source_code"] == "ISL_OFFICIAL"
    res_list = results_data["results"]
    assert len(res_list) >= 1
    cfc_match = next((m for m in res_list if m["home_team"] == "Chennaiyin FC" and m["away_team"] == "East Bengal FC"), None)
    assert cfc_match is not None
    assert cfc_match["home_score"] == 5
    assert cfc_match["away_score"] == 3
    assert len(cfc_match["events"]) == 8  # 8 goals scored

    # 3. Standings
    standings_data = await extractor.extract_standings(season_code="2026-27")
    assert len(standings_data["standings"]) >= 5


@pytest.mark.asyncio
async def test_chennaiyin_fc_extractor():
    """Verify Chennaiyin FC official extractor extracts squad and match reports."""
    extractor = ChennaiyinFCOfficialExtractor(mock_mode=True)

    squad_data = await extractor.extract_squad(season_code="2026-27")
    assert squad_data["source_code"] == "CHENNAIYIN_FC_OFFICIAL"
    assert squad_data["club_name"] == "Chennaiyin FC"
    players = squad_data["players"]
    assert len(players) >= 10

    # Verify key first-team players exist with valid squad status
    mitra = next((p for p in players if p["known_name"] == "Samik Mitra"), None)
    assert mitra is not None
    assert mitra["jersey_number"] == 1
    assert mitra["position"] == "GOALKEEPER"

    farukh = next((p for p in players if p["known_name"] == "Farukh Choudhary"), None)
    assert farukh is not None
    assert farukh["jersey_number"] == 11


@pytest.mark.asyncio
async def test_aiff_extractor():
    """Verify AIFF extractor provides registered fixtures and match commissioner results."""
    extractor = AIFFExtractor(mock_mode=True)
    res = await extractor.extract_results(season_code="2026-27")
    assert res["source_code"] == "AIFF_OFFICIAL"
    assert len(res["results"]) >= 1


def test_manual_file_extractor(tmp_path: Path):
    """Verify ManualFileExtractor parses CSV and JSON uploads."""
    extractor = ManualFileExtractor()

    # 1. Test CSV
    csv_file = tmp_path / "test_squad.csv"
    csv_file.write_text(
        "first_name,last_name,jersey_number,position,nationality\n"
        "Rafael,Crivellaro,10,ATTACKING_MIDFIELDER,Brazil\n"
        "Bikash,Yumnam,3,CENTRE_BACK,India\n",
        encoding="utf-8",
    )
    csv_res = extractor.parse_file(csv_file, entity_type="SQUAD")
    assert csv_res["source_code"] == "MANUAL_CURATION"
    assert len(csv_res["payload"]) == 2
    assert csv_res["payload"][0]["first_name"] == "Rafael"

    # 2. Test JSON
    json_file = tmp_path / "test_fixtures.json"
    json_data = [{"match_number": 1, "home_team": "Chennaiyin FC", "away_team": "FC Goa"}]
    json_file.write_text(json.dumps(json_data), encoding="utf-8")
    json_res = extractor.parse_file(json_file, entity_type="FIXTURES")
    assert len(json_res["payload"]) == 1


@pytest.mark.asyncio
async def test_statsbomb_open_data_adapter_isolation():
    """CRITICAL RULE: Verify StatsBomb Open Data adapter is strictly used as test benchmark,
    never mixed or claimed as Chennaiyin FC or ISL data.
    """
    adapter = StatsBombOpenDataAdapter()
    lineup_res = await adapter.fetch_benchmark_lineup(match_id=3788741)

    assert lineup_res["source_code"] == "STATSBOMB_OPEN_DATA"
    assert lineup_res["source_type"] == "BENCHMARK_ONLY_NEVER_CFC"
    assert "Chennaiyin" not in str(lineup_res)

    events_res = await adapter.fetch_benchmark_events(match_id=3788741)
    assert events_res["source_type"] == "BENCHMARK_ONLY_NEVER_CFC"
    assert events_res["events_count"] > 0
