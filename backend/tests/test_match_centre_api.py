"""Tests for Match Centre API Endpoints:
- GET /api/v1/matches (with filters: status, is_home, matchweek, start_date, end_date, search)
- GET /api/v1/matches/{match_id}
- GET /api/v1/matches/upcoming
- GET /api/v1/matches/completed
- GET /api/v1/matches/{match_id}/statistics
- GET /api/v1/matches/{match_id}/players
- GET /api/v1/analytics/season
- GET /api/v1/analytics/form
"""

import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.common import (
    EventType,
    LineupRole,
    MatchPeriod,
    MatchStatus,
    PlayerPosition,
    ProviderType,
    VerificationStatus,
)
from marina.models.competition import Competition, Season
from marina.models.match import Lineup, Match, MatchEvent, MatchLineup, MatchSubstitute
from marina.models.player import Player
from marina.models.provenance import DataSource
from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
from marina.models.team import Team, Venue


@pytest.fixture
async def setup_match_centre_fixtures(db_session: AsyncSession):
    ds = DataSource(
        code="OFFICIAL_ISL_FEED",
        name="Official ISL Match Centre",
        provider_type=ProviderType.OFFICIAL_LEAGUE,
    )
    db_session.add(ds)
    await db_session.flush()

    comp = Competition(code="ISL", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(
        competition_id=comp.id,
        name="2026–27",
        slug="2026-27",
        is_current=True,
    )
    db_session.add(season)
    await db_session.flush()

    venue_home = Venue(
        name="Jawaharlal Nehru Stadium",
        city="Chennai",
        state="Tamil Nadu",
        capacity=40000,
    )
    venue_away = Venue(
        name="Fatorda Stadium",
        city="Margao",
        state="Goa",
        capacity=19000,
    )
    db_session.add_all([venue_home, venue_away])
    await db_session.flush()

    cfc = Team(
        name="Chennaiyin FC",
        short_name="CFC",
        slug="chennaiyin-fc",
        primary_venue_id=venue_home.id,
    )
    fcg = Team(
        name="FC Goa",
        short_name="FCG",
        slug="fc-goa",
        primary_venue_id=venue_away.id,
    )
    kbfc = Team(
        name="Kerala Blasters FC",
        short_name="KBFC",
        slug="kerala-blasters",
    )
    db_session.add_all([cfc, fcg, kbfc])
    await db_session.flush()

    # Players
    p1 = Player(
        first_name="Mohammad",
        last_name="Nawaz",
        known_name="Mohammad Nawaz",
        slug="mohammad-nawaz",
        primary_position=PlayerPosition.GK,
    )
    p2 = Player(
        first_name="Ramon",
        last_name="Tanque",
        known_name="Ramon Tanque",
        slug="ramon-tanque",
        primary_position=PlayerPosition.CF,
    )
    p3 = Player(
        first_name="Lalhriatpuia",
        last_name="Chawngthu",
        known_name="Lalhriatpuia Chawngthu",
        slug="lalhriatpuia-chawngthu",
        primary_position=PlayerPosition.CM,
    )
    db_session.add_all([p1, p2, p3])
    await db_session.flush()

    # Match 1: Finished away match (FC Goa 1-1 Chennaiyin FC)
    m1 = Match(
        season_id=season.id,
        home_team_id=fcg.id,
        away_team_id=cfc.id,
        venue_id=venue_away.id,
        match_number=1,
        match_status=MatchStatus.FINISHED,
        scheduled_kickoff=datetime(2026, 10, 10, 19, 30, tzinfo=timezone.utc),
        home_score=1,
        away_score=1,
        referee="Crystal John",
        attendance=12400,
        verification_status="VERIFIED",
    )
    # Match 2: Scheduled upcoming home match (Chennaiyin FC vs Kerala Blasters FC)
    m2 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=kbfc.id,
        venue_id=venue_home.id,
        match_number=4,
        match_status=MatchStatus.SCHEDULED,
        scheduled_kickoff=datetime(2026, 11, 20, 19, 30, tzinfo=timezone.utc),
        home_score=None,
        away_score=None,
        referee="Tejas Nagvenkar",
        attendance=None,
        verification_status="PROVISIONAL",
    )
    db_session.add_all([m1, m2])
    await db_session.flush()

    # Team Stats for Match 1
    ts_cfc = TeamMatchStatistic(
        match_id=m1.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        verification_status=VerificationStatus.VERIFIED,
        is_verified=True,
        possession_pct=46.5,
        shots_total=11,
        shots_on_target=4,
        passes_total=380,
        passes_completed=310,
        corners=5,
        fouls_committed=10,
        yellow_cards=2,
    )
    ts_fcg = TeamMatchStatistic(
        match_id=m1.id,
        team_id=fcg.id,
        data_source_id=ds.id,
        verification_status=VerificationStatus.VERIFIED,
        is_verified=True,
        possession_pct=53.5,
        shots_total=14,
        shots_on_target=5,
        passes_total=440,
        passes_completed=370,
        corners=6,
        fouls_committed=12,
        yellow_cards=1,
    )
    db_session.add_all([ts_cfc, ts_fcg])

    # Player stats for Match 1
    ps_p1 = PlayerMatchStatistic(
        match_id=m1.id,
        player_id=p1.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        verification_status=VerificationStatus.VERIFIED,
        is_verified=True,
        minutes_played=90,
        saves=4,
        goals_conceded=1,
        clean_sheet=False,
    )
    ps_p2 = PlayerMatchStatistic(
        match_id=m1.id,
        player_id=p2.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        verification_status=VerificationStatus.VERIFIED,
        is_verified=True,
        minutes_played=90,
        goals=1,
        shots_total=3,
        shots_on_target=2,
    )
    db_session.add_all([ps_p1, ps_p2])

    # MatchLineup for Starter
    ml = MatchLineup(
        match_id=m1.id,
        team_id=cfc.id,
        player_id=p2.id,
        lineup_role=LineupRole.STARTER,
        position=PlayerPosition.CF,
        tactical_formation="4-3-3",
        jersey_number=7,
        is_captain=False,
        minutes_played=90,
        is_verified=True,
    )
    # MatchSubstitute
    ms = MatchSubstitute(
        match_id=m1.id,
        team_id=cfc.id,
        player_id=p3.id,
        jersey_number=17,
        position=PlayerPosition.CM,
        is_used=True,
        sub_in_minute=65,
        replaced_player_id=p2.id,
        minutes_played=25,
        is_verified=True,
    )
    db_session.add_all([ml, ms])

    # Goal event
    evt = MatchEvent(
        match_id=m1.id,
        team_id=cfc.id,
        primary_player_id=p2.id,
        event_type=EventType.GOAL,
        period=MatchPeriod.SECOND_HALF,
        minute=72,
        description="Goal scored by Ramon Tanque",
        verification_status=VerificationStatus.VERIFIED,
        is_verified=True,
    )
    db_session.add(evt)
    await db_session.commit()

    return {
        "season_id": season.id,
        "m1_id": m1.id,
        "m2_id": m2.id,
        "cfc_id": cfc.id,
        "fcg_id": fcg.id,
    }


@pytest.mark.asyncio
async def test_list_matches_with_filters(client: AsyncClient, setup_match_centre_fixtures):
    data = setup_match_centre_fixtures

    # All matches
    res = await client.get("/api/v1/matches")
    assert res.status_code == 200
    all_matches = res.json()
    assert len(all_matches) >= 2

    # Filter by FINISHED
    res_finished = await client.get("/api/v1/matches?status=FINISHED")
    assert res_finished.status_code == 200
    finished = res_finished.json()
    assert all(m["match_status"] == "FINISHED" for m in finished)
    assert any(m["id"] == str(data["m1_id"]) for m in finished)

    # Filter by COMPLETED (alias for FINISHED)
    res_completed = await client.get("/api/v1/matches?status=COMPLETED")
    assert res_completed.status_code == 200
    assert len(res_completed.json()) == len(finished)

    # Filter by SCHEDULED
    res_scheduled = await client.get("/api/v1/matches?status=SCHEDULED")
    assert res_scheduled.status_code == 200
    scheduled = res_scheduled.json()
    assert all(m["match_status"] == "SCHEDULED" for m in scheduled)
    assert any(m["id"] == str(data["m2_id"]) for m in scheduled)

    # Filter by matchweek
    res_mw1 = await client.get("/api/v1/matches?matchweek=1")
    assert res_mw1.status_code == 200
    mw1 = res_mw1.json()
    assert len(mw1) >= 1
    assert mw1[0]["match_number"] == 1

    # Filter by search term
    res_search = await client.get("/api/v1/matches?search=Goa")
    assert res_search.status_code == 200
    search_res = res_search.json()
    assert len(search_res) >= 1
    assert "Goa" in (search_res[0]["home_team"]["name"] or "") or "Goa" in (search_res[0]["away_team"]["name"] or "")


@pytest.mark.asyncio
async def test_upcoming_matches_endpoint(client: AsyncClient, setup_match_centre_fixtures):
    data = setup_match_centre_fixtures
    res = await client.get("/api/v1/matches/upcoming")
    assert res.status_code == 200
    upcoming = res.json()
    assert len(upcoming) >= 1
    for m in upcoming:
        assert m["match_status"] == "SCHEDULED"
        # Scores must remain strictly null for upcoming matches
        assert m["home_score"] is None
        assert m["away_score"] is None


@pytest.mark.asyncio
async def test_completed_matches_endpoint(client: AsyncClient, setup_match_centre_fixtures):
    data = setup_match_centre_fixtures
    res = await client.get("/api/v1/matches/completed")
    assert res.status_code == 200
    completed = res.json()
    assert len(completed) >= 1
    for m in completed:
        assert m["match_status"] == "FINISHED"
        assert m["home_score"] is not None
        assert m["away_score"] is not None


@pytest.mark.asyncio
async def test_match_detail_endpoint(client: AsyncClient, setup_match_centre_fixtures):
    data = setup_match_centre_fixtures
    res = await client.get(f"/api/v1/matches/{data['m1_id']}")
    assert res.status_code == 200
    match = res.json()
    assert match["id"] == str(data["m1_id"])
    assert match["home_team"]["name"] == "FC Goa"
    assert match["away_team"]["name"] == "Chennaiyin FC"
    assert match["home_score"] == 1
    assert match["away_score"] == 1
    assert match["referee"] == "Crystal John"


@pytest.mark.asyncio
async def test_match_statistics_endpoint(client: AsyncClient, setup_match_centre_fixtures):
    data = setup_match_centre_fixtures
    res = await client.get(f"/api/v1/matches/{data['m1_id']}/statistics")
    assert res.status_code == 200
    body = res.json()
    assert "team_statistics" in body
    assert "player_statistics" in body
    assert len(body["team_statistics"]) >= 2
    assert len(body["player_statistics"]) >= 2


@pytest.mark.asyncio
async def test_match_players_endpoint(client: AsyncClient, setup_match_centre_fixtures):
    data = setup_match_centre_fixtures
    res = await client.get(f"/api/v1/matches/{data['m1_id']}/players")
    assert res.status_code == 200
    body = res.json()
    assert body["match_id"] == str(data["m1_id"])
    assert "starting_xi" in body
    assert "substitutes" in body
    assert len(body["starting_xi"]) >= 1
    starter = body["starting_xi"][0]
    assert starter["name"] == "Ramon Tanque"
    assert starter["jersey_number"] == 7
    assert starter["goals"] == 1

    assert len(body["substitutes"]) >= 1
    sub = body["substitutes"][0]
    assert sub["name"] == "Lalhriatpuia Chawngthu"
    assert sub["sub_in_minute"] == 65
    assert sub["replaced_player_name"] == "Ramon Tanque"


@pytest.mark.asyncio
async def test_analytics_season_and_form(client: AsyncClient, setup_match_centre_fixtures):
    res_season = await client.get("/api/v1/analytics/season")
    assert res_season.status_code == 200
    season_data = res_season.json()
    assert "matches_played" in season_data
    assert "points" in season_data

    res_form = await client.get("/api/v1/analytics/form")
    assert res_form.status_code == 200
    form_data = res_form.json()
    assert "matches" in form_data
    assert "sequence" in form_data
