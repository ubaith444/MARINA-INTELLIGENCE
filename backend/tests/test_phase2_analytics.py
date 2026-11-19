"""Tests for Phase 2 Advanced Analytics Endpoints."""

import uuid
from datetime import datetime, timezone
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.common import MatchStatus, PlayerPosition, ProviderType
from marina.models.competition import Competition, Season
from marina.models.match import Match
from marina.models.player import Player, SquadRegistration
from marina.models.provenance import DataSource
from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
from marina.models.team import Team


@pytest.fixture(autouse=True)
async def seed_phase2_data(db_session: AsyncSession):
    """Seed comprehensive fixture and player records for Phase 2 tests."""
    ds = DataSource(code="ISL_OFFICIAL", name="ISL Official Data", provider_type=ProviderType.OFFICIAL_LEAGUE)
    db_session.add(ds)
    await db_session.flush()

    comp = Competition(code="ISL", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2026–27", slug="2026-27", is_current=True)
    db_session.add(season)
    await db_session.flush()

    cfc = Team(name="Chennaiyin FC", short_name="CFC", slug="chennaiyin-fc")
    fcg = Team(name="FC Goa", short_name="FCG", slug="fc-goa")
    ebfc = Team(name="East Bengal FC", short_name="EBFC", slug="east-bengal-fc")
    db_session.add_all([cfc, fcg, ebfc])
    await db_session.flush()

    p_irfan = Player(
        first_name="Irfan",
        last_name="Yadwad",
        known_name="Irfan Yadwad",
        slug="irfan-yadwad",
        squad_number=24,
        primary_position=PlayerPosition.CF,
        nationality="India",
        is_active=True,
    )
    p_brison = Player(
        first_name="Brison",
        last_name="Fernandes",
        known_name="Brison Fernandes",
        slug="brison-fernandes",
        squad_number=42,
        primary_position=PlayerPosition.LW,
        nationality="India",
        is_active=True,
    )
    p_nawaz = Player(
        first_name="Mohammad",
        last_name="Nawaz",
        known_name="Mohammad Nawaz",
        slug="mohammad-nawaz",
        squad_number=13,
        primary_position=PlayerPosition.GK,
        nationality="India",
        is_active=True,
    )
    db_session.add_all([p_irfan, p_brison, p_nawaz])
    await db_session.flush()

    reg1 = SquadRegistration(team_id=cfc.id, player_id=p_irfan.id, season_id=season.id)
    reg2 = SquadRegistration(team_id=cfc.id, player_id=p_brison.id, season_id=season.id)
    reg3 = SquadRegistration(team_id=cfc.id, player_id=p_nawaz.id, season_id=season.id)
    db_session.add_all([reg1, reg2, reg3])
    await db_session.flush()

    # Match 1: FC Goa 1-1 CFC
    m1 = Match(
        season_id=season.id,
        home_team_id=fcg.id,
        away_team_id=cfc.id,
        match_number=1,
        match_status=MatchStatus.FINISHED,
        scheduled_kickoff=datetime(2026, 9, 20, 14, 0, tzinfo=timezone.utc),
        home_score=1,
        away_score=1,
    )
    # Match 5: CFC 5-3 EBFC
    m5 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=ebfc.id,
        match_number=5,
        match_status=MatchStatus.FINISHED,
        scheduled_kickoff=datetime(2026, 10, 24, 14, 0, tzinfo=timezone.utc),
        home_score=5,
        away_score=3,
    )
    db_session.add_all([m1, m5])
    await db_session.flush()

    # Team Match Statistics
    ts1 = TeamMatchStatistic(
        match_id=m1.id, team_id=cfc.id, data_source_id=ds.id,
        possession_pct=48.0, passes_total=420, passes_completed=340, pass_accuracy_pct=81.0,
        shots_total=10, shots_on_target=4, tackles_total=18, tackles_won=14, yellow_cards=2, red_cards=0
    )
    ts5 = TeamMatchStatistic(
        match_id=m5.id, team_id=cfc.id, data_source_id=ds.id,
        possession_pct=54.0, passes_total=480, passes_completed=410, pass_accuracy_pct=85.4,
        shots_total=14, shots_on_target=8, tackles_total=16, tackles_won=12, yellow_cards=1, red_cards=0
    )
    db_session.add_all([ts1, ts5])

    # Player Match Statistics for Irfan
    ps_irfan_1 = PlayerMatchStatistic(
        match_id=m1.id, player_id=p_irfan.id, team_id=cfc.id, data_source_id=ds.id,
        minutes_played=90, goals=1, assists=0, shots_total=3, shots_on_target=2, passes_completed=12
    )
    ps_irfan_5 = PlayerMatchStatistic(
        match_id=m5.id, player_id=p_irfan.id, team_id=cfc.id, data_source_id=ds.id,
        minutes_played=90, goals=2, assists=1, shots_total=5, shots_on_target=3, passes_completed=18
    )
    # Player Match Statistics for Brison
    ps_brison_5 = PlayerMatchStatistic(
        match_id=m5.id, player_id=p_brison.id, team_id=cfc.id, data_source_id=ds.id,
        minutes_played=75, goals=2, assists=0, shots_total=3, shots_on_target=2, passes_completed=15
    )
    # Player Match Statistics for Nawaz
    ps_nawaz_1 = PlayerMatchStatistic(
        match_id=m1.id, player_id=p_nawaz.id, team_id=cfc.id, data_source_id=ds.id,
        minutes_played=90, goals=0, assists=0, saves=3, goals_conceded=1, clean_sheet=False, passes_completed=24
    )
    ps_nawaz_5 = PlayerMatchStatistic(
        match_id=m5.id, player_id=p_nawaz.id, team_id=cfc.id, data_source_id=ds.id,
        minutes_played=90, goals=0, assists=0, saves=2, goals_conceded=3, clean_sheet=False, passes_completed=28
    )
    db_session.add_all([ps_irfan_1, ps_irfan_5, ps_brison_5, ps_nawaz_1, ps_nawaz_5])
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_all_players_analytics(client: AsyncClient):
    """Test GET /api/v1/analytics/players returns full squad analytics table with per-90 metrics."""
    response = await client.get("/api/v1/analytics/players")
    assert response.status_code == 200
    data = response.json()
    assert data["total_players"] >= 3
    assert data["active_players"] >= 3
    assert len(data["players"]) >= 3

    # Verify Irfan Yadwad profile
    irfan = next((p for p in data["players"] if "irfan" in p["name"].lower()), None)
    assert irfan is not None
    assert irfan["goals"] == 3
    assert irfan["minutes_played"] == 180
    # True per-90: (3 / 180) * 90 = 1.5
    assert irfan["goals_per_90"] == 1.5


@pytest.mark.asyncio
async def test_get_all_players_filters(client: AsyncClient):
    """Test filtering players by position and minimum minutes threshold."""
    # Filter forwards
    response = await client.get("/api/v1/analytics/players?position=FORWARD")
    assert response.status_code == 200
    data = response.json()
    assert all("FORWARD" in p["primary_position"].upper() for p in data["players"])

    # Filter with min_minutes
    resp_mins = await client.get("/api/v1/analytics/players?min_minutes=100")
    assert resp_mins.status_code == 200
    data_mins = resp_mins.json()
    assert all(p["minutes_played"] >= 100 for p in data_mins["players"])


@pytest.mark.asyncio
async def test_get_player_detailed_performance_and_matches(client: AsyncClient):
    """Test GET /api/v1/analytics/players/{id} and match logs."""
    list_res = await client.get("/api/v1/analytics/players")
    players = list_res.json()["players"]
    irfan = next(p for p in players if "irfan" in p["name"].lower())
    p_id = irfan["player_id"]

    # Test detailed performance
    perf_res = await client.get(f"/api/v1/analytics/players/{p_id}")
    assert perf_res.status_code == 200
    perf_data = perf_res.json()
    assert perf_data["player_id"] == p_id
    assert perf_data["rankings"] is not None
    assert "goals" in perf_data["rankings"]
    assert "last_five_matches" in perf_data

    # Test match history
    matches_res = await client.get(f"/api/v1/analytics/players/{p_id}/matches")
    assert matches_res.status_code == 200
    matches_data = matches_res.json()
    assert matches_data["player_id"] == p_id
    assert matches_data["total_appearances"] == 2
    assert len(matches_data["matches"]) == 2
    assert all("opponent_name" in m for m in matches_data["matches"])


@pytest.mark.asyncio
async def test_get_player_compare_removed(client: AsyncClient):
    """Confirm player comparison endpoint has been removed."""
    res = await client.post("/api/v1/analytics/players/compare", json={"player_a_id": "p1", "player_b_id": "p2"})
    assert res.status_code in (404, 405)


@pytest.mark.asyncio
async def test_get_passing_network_with_networkx_and_periods(client: AsyncClient):
    """Test passing network endpoint calculates NetworkX degree centrality, density, and supports period filters."""
    matches_res = await client.get("/api/v1/matches?status=FINISHED")
    matches = matches_res.json()
    assert len(matches) > 0
    m_id = matches[0]["id"]

    # Full match passing network
    res_full = await client.get(f"/api/v1/analytics/passing-network/{m_id}?period=FULL_MATCH")
    assert res_full.status_code == 200
    data_full = res_full.json()
    assert data_full["nodes_count"] > 0
    assert data_full["edges_count"] > 0
    assert "network_density" in data_full
    assert "degree_centrality" in data_full
    assert data_full["period"] == "FULL_MATCH"

    # Check node NetworkX fields
    node = data_full["nodes"][0]
    assert "in_degree" in node
    assert "out_degree" in node
    assert "weighted_degree" in node
    assert "degree_centrality" in node

    # First half passing network
    res_h1 = await client.get(f"/api/v1/analytics/passing-network/{m_id}?period=FIRST_HALF")
    assert res_h1.status_code == 200
    assert res_h1.json()["period"] == "FIRST_HALF"


@pytest.mark.asyncio
async def test_get_shots_and_xg_overview(client: AsyncClient):
    """Test shot map and xG baseline calculations."""
    # Shots endpoint
    shots_res = await client.get("/api/v1/analytics/shots")
    assert shots_res.status_code == 200
    shots_data = shots_res.json()
    assert shots_data["total_shots"] == 18
    assert shots_data["goals"] == 6

    # Verify shot fields: distance, angle, xG
    shot = shots_data["shots"][0]
    assert "distance_meters" in shot
    assert "angle_degrees" in shot
    assert "expected_goals" in shot

    # xG Overview endpoint
    xg_res = await client.get("/api/v1/analytics/xg")
    assert xg_res.status_code == 200
    xg_data = xg_res.json()
    assert xg_data["total_shots"] == 18
    assert xg_data["total_goals"] == 6
    assert xg_data["total_xg"] > 0
    assert "xg_difference" in xg_data
    assert "conversion_rate_pct" in xg_data
    assert len(xg_data["players_xg"]) > 0
    assert len(xg_data["matches_xg"]) == 5


@pytest.mark.asyncio
async def test_get_opposition_analysis(client: AsyncClient):
    """Test opposition scouting profile and H2H record for an opponent."""
    opp_res = await client.get("/api/v1/analytics/opposition/fc-goa")
    assert opp_res.status_code == 200
    data = opp_res.json()
    assert data["slug"] == "fc-goa"
    assert "head_to_head" in data
    assert "tactical_profile" in data
    assert "formation" in data["tactical_profile"]
    assert "strengths" in data["tactical_profile"]
    assert "vulnerabilities" in data["tactical_profile"]
    assert len(data["completed_fixtures"]) > 0


@pytest.mark.asyncio
async def test_get_match_tactical_and_comparison(client: AsyncClient):
    """Test match tactical breakdown and side-by-side match comparison."""
    matches_res = await client.get("/api/v1/matches?status=FINISHED")
    matches = matches_res.json()
    m1_id = matches[0]["id"]
    m2_id = matches[1]["id"]

    # Tactical breakdown
    tact_res = await client.get(f"/api/v1/analytics/tactical/{m1_id}")
    assert tact_res.status_code == 200
    tact_data = tact_res.json()
    assert "formation" in tact_data
    assert "territorial" in tact_data
    assert "passing_network" in tact_data
    assert "shot_efficiency" in tact_data

    # Match comparison
    comp_res = await client.get(f"/api/v1/analytics/matches/compare?match_a_id={m1_id}&match_b_id={m2_id}")
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert "match_a" in comp_data
    assert "match_b" in comp_data
    assert "comparisons" in comp_data
    assert len(comp_data["comparisons"]) > 0
    assert all("delta" in c for c in comp_data["comparisons"])
