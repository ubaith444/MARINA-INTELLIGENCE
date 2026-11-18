"""Automated Tests for Module 1: Team Performance and Form Engine."""

import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from marina.analytics.team_performance import TeamPerformanceEngine
from marina.models.common import MatchStatus
from marina.models.competition import Competition, Season
from marina.models.match import Match
from marina.models.team import Team


@pytest.fixture
async def setup_season_matches(db_session: AsyncSession):
    comp = Competition(code="ISL", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2026–27", slug="isl-2026-27", is_current=True)
    db_session.add(season)
    await db_session.flush()

    cfc = Team(name="Chennaiyin FC", short_name="CFC", slug="chennaiyin-fc")
    ebfc = Team(name="East Bengal FC", short_name="EBFC", slug="east-bengal-fc")
    kbfc = Team(name="Kerala Blasters FC", short_name="KBFC", slug="kerala-blasters-fc")
    mcfc = Team(name="Mumbai City FC", short_name="MCFC", slug="mumbai-city-fc")
    db_session.add_all([cfc, ebfc, kbfc, mcfc])
    await db_session.flush()

    # Match 1: CFC 5–3 EBFC (Home Win)
    m1 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=ebfc.id,
        scheduled_kickoff=datetime(2026, 11, 7, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=5,
        away_score=3,
        match_number=1,
    )
    # Match 2: KBFC 1–1 CFC (Away Draw)
    m2 = Match(
        season_id=season.id,
        home_team_id=kbfc.id,
        away_team_id=cfc.id,
        scheduled_kickoff=datetime(2026, 11, 14, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=1,
        away_score=1,
        match_number=2,
    )
    # Match 3: CFC 2–0 MCFC (Home Win + Clean Sheet)
    m3 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=mcfc.id,
        scheduled_kickoff=datetime(2026, 11, 21, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=2,
        away_score=0,
        match_number=3,
    )
    # Match 4: Upcoming Scheduled fixture (must be ignored in performance calculations)
    m4 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=kbfc.id,
        scheduled_kickoff=datetime(2026, 11, 28, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.SCHEDULED,
        home_score=None,
        away_score=None,
        match_number=4,
    )

    db_session.add_all([m1, m2, m3, m4])
    await db_session.flush()

    return {"season": season, "cfc": cfc, "ebfc": ebfc}


@pytest.mark.asyncio
async def test_team_season_performance_calculations(db_session: AsyncSession, setup_season_matches):
    """Verify team seasonal points, goals, clean sheets, and form sequences."""
    data = setup_season_matches
    engine = TeamPerformanceEngine(db_session)

    perf = await engine.calculate_team_season_performance(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
    )

    # 3 finished matches (m4 is SCHEDULED and excluded)
    assert perf["matches_played"] == 3
    assert perf["wins"] == 2
    assert perf["draws"] == 1
    assert perf["losses"] == 0
    assert perf["points"] == 7  # (2*3) + 1

    # Goals & Clean sheets
    assert perf["goals_for"] == 8       # 5 + 1 + 2
    assert perf["goals_against"] == 4   # 3 + 1 + 0
    assert perf["goal_difference"] == 4
    assert perf["clean_sheets"] == 1
    assert perf["clean_sheet_percentage"] == round((1 / 3) * 100, 2)
    assert perf["points_per_match"] == round(7 / 3, 2)
    assert perf["win_percentage"] == round((2 / 3) * 100, 2)

    # Home / Away splits
    assert perf["home_record"]["matches_played"] == 2
    assert perf["home_record"]["wins"] == 2
    assert perf["home_record"]["points"] == 6
    assert perf["home_record"]["clean_sheets"] == 1

    assert perf["away_record"]["matches_played"] == 1
    assert perf["away_record"]["wins"] == 0
    assert perf["away_record"]["draws"] == 1
    assert perf["away_record"]["points"] == 1

    # Form sequence
    assert perf["recent_form"]["sequence"] == ["W", "D", "W"]
    assert perf["recent_form"]["form_points"] == 7


@pytest.mark.asyncio
async def test_team_empty_season_handling(db_session: AsyncSession):
    """Verify graceful handling when a team has 0 finished matches (e.g. before season kickoff)."""
    comp = Competition(code="ISL_EMPTY", name="ISL Empty")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2027–28", slug="isl-2027-28")
    team = Team(name="Future FC", short_name="FFC", slug="future-fc")
    db_session.add_all([season, team])
    await db_session.flush()

    engine = TeamPerformanceEngine(db_session)
    perf = await engine.calculate_team_season_performance(team_id=team.id, season_id=season.id)

    assert perf["matches_played"] == 0
    assert perf["points"] == 0
    assert perf["win_percentage"] is None  # Safe divide prevented ZeroDivisionError!
    assert perf["points_per_match"] is None
    assert perf["recent_form"]["sequence"] == []
