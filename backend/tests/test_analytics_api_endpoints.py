"""Automated Integration Tests for Analytics REST API Endpoints."""

import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.common import EventType, MatchPeriod, MatchStatus, PlayerPosition, ProviderType
from marina.models.competition import Competition, Season
from marina.models.match import Lineup, Match, MatchEvent
from marina.models.player import Player
from marina.models.provenance import DataSource
from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
from marina.models.team import Team, Venue


@pytest.fixture
async def setup_api_data(db_session: AsyncSession):
    ds = DataSource(
        code="ISL_API_TEST",
        name="ISL API Ingestion Source",
        provider_type=ProviderType.OFFICIAL_LEAGUE,
    )
    db_session.add(ds)
    await db_session.flush()

    comp = Competition(code="ISL_API", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2026–27", slug="isl-2026-27-api", is_current=True)
    venue = Venue(name="Jawaharlal Nehru Stadium", city="Chennai", state="Tamil Nadu", capacity=40000)
    db_session.add_all([season, venue])
    await db_session.flush()

    cfc = Team(name="Chennaiyin FC", short_name="CFC", slug="chennaiyin-fc-api", primary_venue_id=venue.id)
    kbfc = Team(name="Kerala Blasters FC", short_name="KBFC", slug="kerala-blasters-fc-api")
    db_session.add_all([cfc, kbfc])
    await db_session.flush()

    p1 = Player(first_name="Wilmar", last_name="Jordan Gil", known_name="Wilmar Jordan Gil", slug="wilmar-jordan-gil-api", primary_position=PlayerPosition.CF)
    p2 = Player(first_name="Ryan", last_name="Edwards", known_name="Ryan Edwards", slug="ryan-edwards-api", primary_position=PlayerPosition.CB)
    db_session.add_all([p1, p2])
    await db_session.flush()

    m1 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=kbfc.id,
        venue_id=venue.id,
        scheduled_kickoff=datetime(2026, 11, 7, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=2,
        away_score=0,
        match_number=1,
    )
    db_session.add(m1)
    await db_session.flush()

    # Team Stats
    stat_cfc = TeamMatchStatistic(
        match_id=m1.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        possession_pct=55.0,
        shots_total=14,
        shots_on_target=6,
        tackles_total=16,
        tackles_won=12,
        yellow_cards=1,
        red_cards=0,
    )
    db_session.add(stat_cfc)

    # Lineups and Player Stats
    l1 = Lineup(match_id=m1.id, team_id=cfc.id, player_id=p1.id, minutes_played=90)
    l2 = Lineup(match_id=m1.id, team_id=cfc.id, player_id=p2.id, minutes_played=90)
    db_session.add_all([l1, l2])

    pstat1 = PlayerMatchStatistic(
        match_id=m1.id,
        player_id=p1.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        minutes_played=90,
        goals=2,
        shots_total=5,
        shots_on_target=3,
        expected_goals=1.2,
    )
    pstat2 = PlayerMatchStatistic(
        match_id=m1.id,
        player_id=p2.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        minutes_played=90,
        tackles_total=4,
        tackles_won=3,
        interceptions=5,
        clearances=6,
    )
    db_session.add_all([pstat1, pstat2])

    # Goal event
    e1 = MatchEvent(
        match_id=m1.id,
        team_id=cfc.id,
        period=MatchPeriod.FIRST_HALF,
        minute=35,
        event_type=EventType.GOAL,
        primary_player_id=p1.id,
    )
    db_session.add(e1)
    await db_session.flush()

    return {
        "season": season,
        "venue": venue,
        "cfc": cfc,
        "kbfc": kbfc,
        "p1": p1,
        "p2": p2,
        "match": m1,
    }


@pytest.mark.asyncio
async def test_api_team_season_performance(client: AsyncClient, setup_api_data):
    """GET /api/v1/analytics/teams/{team_id}/season/{season_id}"""
    data = setup_api_data
    url = f"/api/v1/analytics/teams/{data['cfc'].id}/season/{data['season'].id}"
    resp = await client.get(url)
    assert resp.status_code == 200
    res = resp.json()
    assert res["matches_played"] == 1
    assert res["wins"] == 1
    assert res["points"] == 3
    assert res["team_name"] == "Chennaiyin FC"


@pytest.mark.asyncio
async def test_api_team_attacking_analytics(client: AsyncClient, setup_api_data):
    """GET /api/v1/analytics/teams/{team_id}/attacking"""
    data = setup_api_data
    url = f"/api/v1/analytics/teams/{data['cfc'].id}/attacking?season_id={data['season'].id}"
    resp = await client.get(url)
    assert resp.status_code == 200
    res = resp.json()
    assert res["team_name"] == "Chennaiyin FC"
    assert res["shots_total"] == 14
    assert res["goals_scored"] == 1


@pytest.mark.asyncio
async def test_api_team_defensive_analytics(client: AsyncClient, setup_api_data):
    """GET /api/v1/analytics/teams/{team_id}/defensive"""
    data = setup_api_data
    url = f"/api/v1/analytics/teams/{data['cfc'].id}/defensive?season_id={data['season'].id}"
    resp = await client.get(url)
    assert resp.status_code == 200
    res = resp.json()
    assert res["team_name"] == "Chennaiyin FC"
    assert res["goals_conceded"] == 0
    assert res["clean_sheets"] == 1
    assert res["clean_sheet_percentage"] == 100.0


@pytest.mark.asyncio
async def test_api_player_performance(client: AsyncClient, setup_api_data):
    """GET /api/v1/analytics/players/{player_id}/performance"""
    data = setup_api_data
    url = f"/api/v1/analytics/players/{data['p1'].id}/performance?season_id={data['season'].id}&min_minutes=45"
    resp = await client.get(url)
    assert resp.status_code == 200
    res = resp.json()
    assert res["name"] == "Wilmar Jordan Gil"
    assert res["minutes_played"] == 90
    assert res["per_90"]["has_sufficient_minutes"] is True
    assert res["per_90"]["goals_per_90"] == 2.0


@pytest.mark.asyncio
async def test_api_player_compare_removed(client: AsyncClient, setup_api_data):
    """POST /api/v1/analytics/players/compare should return 404 or 405 after feature removal."""
    url = "/api/v1/analytics/players/compare"
    resp = await client.post(url, json={})
    assert resp.status_code in (404, 405)


@pytest.mark.asyncio
async def test_api_match_tactical_report(client: AsyncClient, setup_api_data):
    """GET /api/v1/analytics/matches/{match_id}/report"""
    data = setup_api_data
    url = f"/api/v1/analytics/matches/{data['match'].id}/report"
    resp = await client.get(url)
    assert resp.status_code == 200
    res = resp.json()
    assert res["home_team"]["name"] == "Chennaiyin FC"
    assert res["home_team"]["score"] == 2
    assert "half_by_half" in res
    assert "timeline" in res


@pytest.mark.asyncio
async def test_api_tactical_passing_network(client: AsyncClient, setup_api_data):
    """GET /api/v1/analytics/tactical/passing-network/{match_id}/team/{team_id}"""
    data = setup_api_data
    url = f"/api/v1/analytics/tactical/passing-network/{data['match'].id}/team/{data['cfc'].id}"
    resp = await client.get(url)
    assert resp.status_code == 200
    res = resp.json()
    assert "nodes" in res
    assert "edges" in res
    assert "network_density" in res


@pytest.mark.asyncio
async def test_api_tactical_shot_map(client: AsyncClient, setup_api_data):
    """GET /api/v1/analytics/tactical/shot-map/{match_id}"""
    data = setup_api_data
    url = f"/api/v1/analytics/tactical/shot-map/{data['match'].id}"
    resp = await client.get(url)
    assert resp.status_code == 200
    res = resp.json()
    assert "total_shots" in res
    assert "goals" in res
    assert "shots" in res


@pytest.mark.asyncio
async def test_api_404_handling(client: AsyncClient):
    """Verify 404 for non-existent entities."""
    random_uuid = uuid.uuid4()
    resp = await client.get(f"/api/v1/analytics/matches/{random_uuid}/report")
    assert resp.status_code == 404
