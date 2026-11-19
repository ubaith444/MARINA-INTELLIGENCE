"""Automated Test Suite for Season Performance Overview Rework and Dynamic Analytics."""

import os
import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.common import MatchStatus
from marina.models.competition import Competition, Season
from marina.models.match import Match
from marina.models.team import Team
from marina.services.fixture_service import FixtureService
from marina.services.season_cleanup_service import SeasonCleanupService
from marina.services.squad_sync_service import SquadSyncService


@pytest.fixture(autouse=True)
async def seed_test_database(db_session: AsyncSession):
    """Seeds test in-memory database with official 2026-27 fixtures, 2026-27 squad,

    and isolated 2025-26 historical mock match.
    """
    # 1. Competitions
    comp = Competition(
        code="ISL",
        name="Indian Super League",
        country="India",
        federation="AIFF",
    )
    db_session.add(comp)
    await db_session.flush()

    # 2. Seasons: 2025-26 (historical) and 2026-27 (active)
    s25 = Season(
        competition_id=comp.id,
        name="2025–26",
        slug="isl-2025-26",
        is_current=False,
        is_completed=True,
    )
    s26 = Season(
        competition_id=comp.id,
        name="2026–27",
        slug="isl-2026-27",
        is_current=True,
        is_completed=False,
    )
    db_session.add_all([s25, s26])
    await db_session.flush()

    # 3. Teams
    cfc = Team(name="Chennaiyin FC", short_name="CFC", slug="chennaiyin-fc")
    ebfc = Team(name="East Bengal FC", short_name="EBFC", slug="east-bengal-fc")
    db_session.add_all([cfc, ebfc])
    await db_session.flush()

    # 4. Import official fixtures into 2026-27
    fix_service = FixtureService(db_session)
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src",
        "marina",
        "data",
    )
    fix_path = os.path.join(data_dir, "chennaiyin_fc_2026_27_fixtures.json")
    with open(fix_path, "r", encoding="utf-8") as f:
        fix_records = fix_service.parse_raw_fixtures(f.read())
    await fix_service.import_fixtures(fix_records, season_id=s26.id)

    # 5. Import official squad into 2026-27
    squad_service = SquadSyncService(db_session)
    squad_path = os.path.join(data_dir, "chennaiyin_fc_2026_27_squad.json")
    with open(squad_path, "r", encoding="utf-8") as f:
        squad_records = squad_service.parse_raw_records(f.read(), format_hint="json")
    await squad_service.synchronize_squad(
        team_id=cfc.id,
        season_id=s26.id,
        incoming_records=squad_records,
    )

    # 6. Isolated historical match in 2025-26 season
    mock_id = uuid.UUID("8054b142-9fae-4351-bd72-e5bb5ecb1000")
    hist_match = Match(
        id=mock_id,
        season_id=s25.id,
        home_team_id=cfc.id,
        away_team_id=ebfc.id,
        match_number=7,
        match_status=MatchStatus.FINISHED,
        home_score=5,
        away_score=3,
        scheduled_kickoff=datetime(2025, 11, 7, 14, 0, tzinfo=timezone.utc),
        actual_kickoff=datetime(2025, 11, 7, 14, 0, tzinfo=timezone.utc),
        has_discrepancy=False,
    )
    db_session.add(hist_match)
    await db_session.commit()


@pytest.mark.asyncio
async def test_season_overview_kpis(client: AsyncClient):
    """Verify that Season Overview returns strictly dynamic, non-fabricated metrics."""
    response = await client.get("/api/v1/season/overview")
    assert response.status_code == 200
    data = response.json()

    assert data["season_name"] == "2026–27"
    assert data["team_name"] == "Chennaiyin FC"
    assert data["matches_played"] == 0
    assert data["matches_remaining"] == 24
    assert data["total_fixtures"] == 24
    assert data["wins"] == 0
    assert data["draws"] == 0
    assert data["losses"] == 0
    assert data["points"] == 0
    assert data["goals_scored"] == 0
    assert data["goals_conceded"] == 0
    assert data["goal_difference"] == 0
    assert data["win_percentage"] == 0.0
    assert data["points_per_match"] == 0.0
    assert data["clean_sheets"] == 0
    assert data["recent_form"] == []
    assert data["is_season_active"] is True


@pytest.mark.asyncio
async def test_season_form_endpoint(client: AsyncClient):
    """Verify recent form returns empty sequence when no matches are completed."""
    response = await client.get("/api/v1/season/form")
    assert response.status_code == 200
    data = response.json()

    assert data["sequence"] == []
    assert data["form_points"] == 0
    assert data["form_ppm"] == 0.0
    assert data["matches"] == []


@pytest.mark.asyncio
async def test_season_results_endpoint(client: AsyncClient):
    """Verify results list returns empty list when no matches are completed."""
    response = await client.get("/api/v1/season/results")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_season_home_away_splits(client: AsyncClient):
    """Verify home vs away record splits with 12 home and 12 away scheduled fixtures."""
    response = await client.get("/api/v1/season/home-away")
    assert response.status_code == 200
    data = response.json()

    home = data["home"]
    away = data["away"]

    assert home["matches_played"] == 0
    assert home["matches_scheduled"] == 12
    assert home["points"] == 0
    assert home["wins"] == 0
    assert home["goals_scored"] == 0
    assert home["goals_conceded"] == 0
    assert home["win_percentage"] == 0.0

    assert away["matches_played"] == 0
    assert away["matches_scheduled"] == 12
    assert away["points"] == 0
    assert away["wins"] == 0
    assert away["goals_scored"] == 0
    assert away["goals_conceded"] == 0
    assert away["win_percentage"] == 0.0


@pytest.mark.asyncio
async def test_season_scoring_endpoint(client: AsyncClient):
    """Verify scoring metrics are properly formatted and report false for available records."""
    response = await client.get("/api/v1/season/scoring")
    assert response.status_code == 200
    data = response.json()

    assert data["total_goals_scored"] == 0
    assert data["total_goals_conceded"] == 0
    assert data["goals_per_match"] == 0.0
    assert data["goals_conceded_per_match"] == 0.0
    assert data["clean_sheets"] == 0
    assert data["scoring_records_available"] is False


@pytest.mark.asyncio
async def test_player_statistics_strict_non_fabrication(client: AsyncClient):
    """Verify player statistics are derived strictly from match records and not fabricated."""
    response = await client.get("/api/v1/players/statistics")
    assert response.status_code == 200
    players = response.json()

    assert len(players) >= 26
    for p in players:
        assert p["appearances"] == 0
        assert p["starts"] == 0
        assert p["minutes_played"] == 0
        assert p["goals"] == 0
        assert p["assists"] == 0
        assert p["yellow_cards"] == 0
        assert p["red_cards"] == 0


@pytest.mark.asyncio
async def test_player_top_scorers_empty_when_no_goals(client: AsyncClient):
    """Verify top scorers endpoint returns empty list when zero goals are recorded."""
    response = await client.get("/api/v1/players/top-scorers")
    assert response.status_code == 200
    scorers = response.json()
    assert isinstance(scorers, list)
    assert len(scorers) == 0


@pytest.mark.asyncio
async def test_data_quality_report(client: AsyncClient):
    """Verify comprehensive data quality and integrity report."""
    response = await client.get("/api/v1/data-quality")
    assert response.status_code == 200
    report = response.json()

    assert report["total_players"] >= 26
    assert report["duplicate_players_count"] == 0
    assert report["total_fixtures"] == 24
    assert report["duplicate_fixtures_count"] == 0
    assert report["scheduled_matches_count"] == 24
    assert report["completed_matches_count"] == 0
    assert report["discrepant_matches_count"] == 1  # Match #7
    assert report["unplayed_matches_with_scores"] == 0
    assert report["finished_matches_without_scores"] == 0
    assert report["orphan_events_count"] == 0
    assert report["season_contamination_detected"] is False
    assert report["data_integrity_score_pct"] == 100.0

    check_names = [c["name"] for c in report["checks"]]
    assert "Squad Duplicate Check" in check_names
    assert "Fixture Uniqueness Check" in check_names
    assert "Unplayed Matches Score Integrity" in check_names
    assert "Season Isolation Check" in check_names
    assert "Orphan Event Integrity" in check_names


@pytest.mark.asyncio
async def test_historical_mock_match_isolation(db_session: AsyncSession):
    """Verify mock match 8054b142-9fae-4351-bd72-e5bb5ecb1000 is isolated in 2025-26 season."""
    mock_id = uuid.UUID("8054b142-9fae-4351-bd72-e5bb5ecb1000")
    match = (await db_session.execute(select(Match).where(Match.id == mock_id))).scalars().first()

    assert match is not None
    assert match.home_score == 5
    assert match.away_score == 3
    assert match.match_status == MatchStatus.FINISHED

    season = (await db_session.execute(select(Season).where(Season.id == match.season_id))).scalars().first()
    assert season is not None
    assert season.name == "2025–26"
    assert season.slug == "isl-2025-26"


@pytest.mark.asyncio
async def test_completed_match_dynamic_recalculation(db_session: AsyncSession, client: AsyncClient):
    """Verify that when a verified match completes, KPIs dynamically recalculate."""
    # Find match #1 and mark it finished: CFC 2 - 1 Opponent (Away win for CFC)
    s26 = (await db_session.execute(select(Season).where(Season.slug == "isl-2026-27"))).scalars().first()
    m1 = (await db_session.execute(
        select(Match).where(Match.season_id == s26.id, Match.match_number == 1)
    )).scalars().first()

    assert m1 is not None
    m1.match_status = MatchStatus.FINISHED
    m1.home_score = 1  # FC Goa 1
    m1.away_score = 2  # Chennaiyin FC 2
    m1.actual_kickoff = datetime(2026, 10, 10, 19, 30, tzinfo=timezone.utc)
    await db_session.commit()

    # Query overview
    res = await client.get("/api/v1/season/overview")
    assert res.status_code == 200
    data = res.json()

    assert data["matches_played"] == 1
    assert data["matches_remaining"] == 23
    assert data["wins"] == 1
    assert data["draws"] == 0
    assert data["losses"] == 0
    assert data["points"] == 3
    assert data["goals_scored"] == 2
    assert data["goals_conceded"] == 1
    assert data["goal_difference"] == 1
    assert data["win_percentage"] == 100.0
    assert data["points_per_match"] == 3.0
    assert data["recent_form"] == ["W"]

    # Query results
    res_results = await client.get("/api/v1/season/results")
    assert res_results.status_code == 200
    results = res_results.json()
    assert len(results) == 1
    assert results[0]["cfc_score"] == 2
    assert results[0]["opponent_score"] == 1
    assert results[0]["outcome"] == "WIN"
    assert results[0]["is_home"] is False

    # Query home/away splits
    res_ha = await client.get("/api/v1/season/home-away")
    assert res_ha.status_code == 200
    ha = res_ha.json()
    assert ha["away"]["matches_played"] == 1
    assert ha["away"]["wins"] == 1
    assert ha["away"]["points"] == 3
    assert ha["home"]["matches_played"] == 0


@pytest.mark.asyncio
async def test_strict_exclusion_of_scheduled_matches_from_completed_stats(db_session: AsyncSession, client: AsyncClient):
    """Verify scheduled fixtures are strictly excluded from completed match metrics."""
    res = await client.get("/api/v1/season/overview")
    assert res.status_code == 200
    data = res.json()

    assert data["matches_played"] == 0
    assert data["total_fixtures"] == 24
    assert data["matches_remaining"] == 24
    assert data["points"] == 0


@pytest.mark.asyncio
async def test_recent_form_chronological_ordering(db_session: AsyncSession, client: AsyncClient):
    """Verify that multiple completed matches are correctly ordered chronologically in form."""
    s26 = (await db_session.execute(select(Season).where(Season.slug == "isl-2026-27"))).scalars().first()
    matches = (await db_session.execute(
        select(Match).where(Match.season_id == s26.id, Match.match_number.in_([1, 2, 3]))
    )).scalars().all()

    # M1: Away Win (Goa 0 - 2 CFC) on Oct 10
    # M2: Away Draw (Bengaluru 1 - 1 CFC) on Oct 17
    # M3: Away Loss (Mohun Bagan 2 - 1 CFC) on Oct 26
    m_by_num = {m.match_number: m for m in matches}
    m_by_num[1].match_status = MatchStatus.FINISHED
    m_by_num[1].home_score = 0
    m_by_num[1].away_score = 2
    m_by_num[1].actual_kickoff = datetime(2026, 10, 10, 19, 30, tzinfo=timezone.utc)

    m_by_num[2].match_status = MatchStatus.FINISHED
    m_by_num[2].home_score = 1
    m_by_num[2].away_score = 1
    m_by_num[2].actual_kickoff = datetime(2026, 10, 17, 19, 30, tzinfo=timezone.utc)

    m_by_num[3].match_status = MatchStatus.FINISHED
    m_by_num[3].home_score = 2
    m_by_num[3].away_score = 1
    m_by_num[3].actual_kickoff = datetime(2026, 10, 26, 19, 30, tzinfo=timezone.utc)

    await db_session.commit()

    res = await client.get("/api/v1/season/form")
    assert res.status_code == 200
    form_data = res.json()

    assert form_data["sequence"] == ["W", "D", "L"]
    assert form_data["form_points"] == 4
    assert form_data["form_ppm"] == 1.33
    assert len(form_data["matches"]) == 3
    assert form_data["matches"][0]["result"] == "W"
    assert form_data["matches"][1]["result"] == "D"
    assert form_data["matches"][2]["result"] == "L"


@pytest.mark.asyncio
async def test_season_cleanup_service_idempotent(db_session: AsyncSession):
    """Verify that SeasonCleanupService can be executed multiple times safely."""
    service = SeasonCleanupService(db_session)
    result = await service.isolate_historical_data()

    assert result["moved_mock_match"] is True
    assert result["active_season_matches_count"] == 24

    # Run second time
    result2 = await service.isolate_historical_data()
    assert result2["active_season_matches_count"] == 24
