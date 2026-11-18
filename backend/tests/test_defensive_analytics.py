"""Automated Tests for Module 3: Defensive Resilience & Disciplinary Analytics Engine."""

import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from marina.analytics.defensive import DefensiveAnalyticsEngine
from marina.models.common import MatchStatus, ProviderType
from marina.models.competition import Competition, Season
from marina.models.match import Match
from marina.models.provenance import DataSource
from marina.models.statistics import TeamMatchStatistic
from marina.models.team import Team


@pytest.fixture
async def setup_defensive_fixtures(db_session: AsyncSession):
    ds = DataSource(
        code="ISL_OFFICIAL_DEF",
        name="ISL Official Defensive Stats",
        provider_type=ProviderType.OFFICIAL_LEAGUE,
    )
    db_session.add(ds)
    await db_session.flush()

    comp = Competition(code="ISL_DEF", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2026–27", slug="isl-2026-27-def", is_current=True)
    db_session.add(season)
    await db_session.flush()

    cfc = Team(name="Chennaiyin FC", short_name="CFC", slug="chennaiyin-fc-def")
    mcfc = Team(name="Mumbai City FC", short_name="MCFC", slug="mumbai-city-fc-def")
    kbfc = Team(name="Kerala Blasters FC", short_name="KBFC", slug="kerala-blasters-fc-def")
    db_session.add_all([cfc, mcfc, kbfc])
    await db_session.flush()

    # Match 1: CFC 2–0 MCFC (Home Clean Sheet)
    m1 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=mcfc.id,
        scheduled_kickoff=datetime(2026, 11, 7, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=2,
        away_score=0,
        match_number=1,
    )
    # Match 2: KBFC 2–1 CFC (Away Match, Conceded 2)
    m2 = Match(
        season_id=season.id,
        home_team_id=kbfc.id,
        away_team_id=cfc.id,
        scheduled_kickoff=datetime(2026, 11, 14, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=2,
        away_score=1,
        match_number=2,
    )
    db_session.add_all([m1, m2])
    await db_session.flush()

    # TeamMatchStatistic for CFC in Match 1
    stat1 = TeamMatchStatistic(
        match_id=m1.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        tackles_total=18,
        tackles_won=14,
        interceptions=12,
        clearances=22,
        saves=4,
        blocked_shots=3,
        fouls_committed=10,
        yellow_cards=2,
        red_cards=0,
        expected_goals_conceded=0.65,
    )
    # TeamMatchStatistic for CFC in Match 2
    stat2 = TeamMatchStatistic(
        match_id=m2.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        tackles_total=14,
        tackles_won=10,
        interceptions=9,
        clearances=16,
        saves=2,
        blocked_shots=2,
        fouls_committed=14,
        yellow_cards=3,
        red_cards=1,
        expected_goals_conceded=1.45,
    )
    db_session.add_all([stat1, stat2])
    await db_session.flush()

    return {
        "season": season,
        "cfc": cfc,
        "mcfc": mcfc,
        "kbfc": kbfc,
        "ds": ds,
    }


@pytest.mark.asyncio
async def test_calculate_defensive_metrics(db_session: AsyncSession, setup_defensive_fixtures):
    """Verify clean sheets, duel efficiency, defensive actions, and disciplinary index."""
    data = setup_defensive_fixtures
    engine = DefensiveAnalyticsEngine(db_session)

    res = await engine.calculate_team_defensive_metrics(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
    )

    assert res["matches_analyzed"] == 2
    # Conceded 0 in match 1, 2 in match 2 -> total 2
    assert res["goals_conceded"] == 2
    assert res["goals_conceded_per_match"] == 1.0
    # 1 clean sheet out of 2 matches -> 50%
    assert res["clean_sheets"] == 1
    assert res["clean_sheet_percentage"] == 50.0

    # Tackles: 18 + 14 = 32 total; 14 + 10 = 24 won -> 75%
    assert res["tackles_total"] == 32
    assert res["tackles_won"] == 24
    assert res["tackle_success_pct"] == 75.0

    # Actions
    assert res["interceptions"] == 21
    assert res["clearances"] == 38
    assert res["saves"] == 6
    assert res["blocked_shots"] == 5
    # Total defensive actions: 32 tackles + 21 int + 38 clear + 5 blocked = 96
    assert res["total_defensive_actions"] == 96
    assert res["defensive_actions_per_match"] == 48.0

    # Disciplinary: Yellows = 2 + 3 = 5; Reds = 0 + 1 = 1
    # Discipline index = 5 + (3 * 1) = 8
    assert res["yellow_cards"] == 5
    assert res["red_cards"] == 1
    assert res["discipline_index"] == 8

    # xGA: 0.65 + 1.45 = 2.10
    assert res["expected_goals_conceded"] == 2.10
    assert res["expected_goals_conceded_per_match"] == 1.05


@pytest.mark.asyncio
async def test_calculate_defensive_metrics_without_xga(db_session: AsyncSession, setup_defensive_fixtures):
    """Verify that when xGA is missing, it remains None without fabrication."""
    data = setup_defensive_fixtures

    # Add a match for MCFC with NO expected goals conceded
    m3 = Match(
        season_id=data["season"].id,
        home_team_id=data["mcfc"].id,
        away_team_id=data["kbfc"].id,
        scheduled_kickoff=datetime(2026, 11, 21, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=1,
        away_score=1,
        match_number=3,
    )
    db_session.add(m3)
    await db_session.flush()

    stat_mcfc = TeamMatchStatistic(
        match_id=m3.id,
        team_id=data["mcfc"].id,
        data_source_id=data["ds"].id,
        tackles_total=12,
        tackles_won=8,
        interceptions=7,
        clearances=10,
        yellow_cards=1,
        red_cards=0,
        expected_goals_conceded=None,  # missing
    )
    db_session.add(stat_mcfc)
    await db_session.flush()

    engine = DefensiveAnalyticsEngine(db_session)
    res = await engine.calculate_team_defensive_metrics(
        team_id=data["mcfc"].id,
        season_id=data["season"].id,
    )

    assert res["expected_goals_conceded"] is None
    assert res["expected_goals_conceded_per_match"] is None


@pytest.mark.asyncio
async def test_calculate_defensive_metrics_empty(db_session: AsyncSession):
    """Verify empty matches handling does not trigger ZeroDivisionError."""
    comp = Competition(code="ISL_EMPTY", name="ISL Empty")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2026–27", slug="isl-empty", is_current=True)
    team = Team(name="Odisha FC", short_name="OFC", slug="odisha-fc-empty")
    db_session.add_all([season, team])
    await db_session.flush()

    engine = DefensiveAnalyticsEngine(db_session)
    res = await engine.calculate_team_defensive_metrics(team_id=team.id, season_id=season.id)

    assert res["matches_analyzed"] == 0
    assert res["goals_conceded"] == 0
    assert res["goals_conceded_per_match"] is None
    assert res["clean_sheets"] == 0
    assert res["clean_sheet_percentage"] is None
    assert res["expected_goals_conceded"] is None
    assert res["tackle_success_pct"] is None
    assert res["discipline_index"] == 0
