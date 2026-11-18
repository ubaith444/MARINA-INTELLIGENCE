"""Step 5: Season Analytics Calculation Engine Comprehensive Test Suite.

Validates:
1. Season Overview calculations (W/D/L, Points, Goal Difference, PPM, Clean Sheets, Average Possession).
2. Strict completed fixture filtering (scheduled/postponed matches excluded).
3. Home and Away splits and comparative advantage indices.
4. Passing analytics (total passes, completed, failed, accuracy %, average possession %, per-match breakdown).
5. Performance trends (last 5 fixtures, chronological history, monthly aggregations, points progression, rolling trends).
6. Attacking analytics extensions (assists, goals by match, goals by player, competition phase breakdown).
7. Defensive analytics extensions (match-by-match defending, tackles, clean sheets, discipline).
8. Zero division protection and graceful handling of empty seasons.
9. Strict missing data preservation (NULLs remain None, never coerced to 0).
10. End-to-end REST API verification for all Step 5 endpoints.
"""

import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from marina.analytics.attacking import AttackingAnalyticsEngine
from marina.analytics.defensive import DefensiveAnalyticsEngine
from marina.analytics.passing import PassingAnalyticsEngine
from marina.analytics.team_performance import TeamPerformanceEngine
from marina.analytics.trends import PerformanceTrendsEngine
from marina.models.common import EventType, MatchPeriod, MatchStatus, PlayerPosition, ProviderType
from marina.models.competition import Competition, Season
from marina.models.match import Match, MatchEvent
from marina.models.player import Player
from marina.models.provenance import DataSource
from marina.models.statistics import TeamMatchStatistic
from marina.models.team import Team


@pytest.fixture
async def season_engine_dataset(db_session: AsyncSession):
    """Seed comprehensive test dataset representing Chennaiyin FC's campaign."""
    ds = DataSource(
        code="ISL_OFFICIAL",
        name="Indian Super League Official",
        provider_type=ProviderType.OFFICIAL_LEAGUE,
    )
    db_session.add(ds)
    await db_session.flush()

    comp = Competition(code="ISL", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2026–27", slug="isl-2026-27", is_current=True)
    db_session.add(season)
    await db_session.flush()

    cfc = Team(name="Chennaiyin FC", short_name="CFC", slug="chennaiyin-fc")
    ebfc = Team(name="East Bengal FC", short_name="EBFC", slug="east-bengal-fc")
    mcfc = Team(name="Mumbai City FC", short_name="MCFC", slug="mumbai-city-fc")
    kbfc = Team(name="Kerala Blasters FC", short_name="KBFC", slug="kerala-blasters-fc")
    db_session.add_all([cfc, ebfc, mcfc, kbfc])
    await db_session.flush()

    # Players
    p1 = Player(first_name="Wilmar", last_name="Jordan Gil", known_name="Wilmar Jordan Gil", slug="wilmar-jordan-gil", primary_position=PlayerPosition.CF)
    p2 = Player(first_name="Farukh", last_name="Choudhary", known_name="Farukh Choudhary", slug="farukh-choudhary", primary_position=PlayerPosition.CF)
    p3 = Player(first_name="Lukas", last_name="Brambilla", known_name="Lukas Brambilla", slug="lukas-brambilla", primary_position=PlayerPosition.AM)
    p4 = Player(first_name="Ryan", last_name="Edwards", known_name="Ryan Edwards", slug="ryan-edwards", primary_position=PlayerPosition.CB)
    db_session.add_all([p1, p2, p3, p4])
    await db_session.flush()

    # Match 1 (Home, Nov 2026): CFC 5-3 EBFC (Win)
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
    # Match 2 (Away, Nov 2026): MCFC 1-1 CFC (Draw)
    m2 = Match(
        season_id=season.id,
        home_team_id=mcfc.id,
        away_team_id=cfc.id,
        scheduled_kickoff=datetime(2026, 11, 20, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=1,
        away_score=1,
        match_number=2,
    )
    # Match 3 (Home, Dec 2026): CFC 2-0 KBFC (Win, Clean Sheet)
    m3 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=kbfc.id,
        scheduled_kickoff=datetime(2026, 12, 5, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=2,
        away_score=0,
        match_number=3,
    )
    # Match 4 (Away, Dec 2026): EBFC 2-1 CFC (Loss)
    m4 = Match(
        season_id=season.id,
        home_team_id=ebfc.id,
        away_team_id=cfc.id,
        scheduled_kickoff=datetime(2026, 12, 18, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=2,
        away_score=1,
        match_number=4,
    )
    # Match 5 (Scheduled fixture, Jan 2027): Unplayed / incomplete match
    m5 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=mcfc.id,
        scheduled_kickoff=datetime(2027, 1, 10, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.SCHEDULED,
        home_score=None,
        away_score=None,
        match_number=5,
    )
    db_session.add_all([m1, m2, m3, m4, m5])
    await db_session.flush()

    # Team Match Statistics for CFC
    # Match 1: CFC vs EBFC
    s1 = TeamMatchStatistic(
        match_id=m1.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        possession_pct=52.0,
        passes_total=450,
        passes_completed=380,
        pass_accuracy_pct=84.4,
        shots_total=16,
        shots_on_target=8,
        shots_off_target=5,
        blocked_shots=3,
        expected_goals=2.85,
        tackles_total=18,
        tackles_won=12,
        interceptions=10,
        clearances=14,
        saves=2,
        fouls_committed=11,
        yellow_cards=2,
        red_cards=0,
    )
    # Match 2: MCFC vs CFC
    s2 = TeamMatchStatistic(
        match_id=m2.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        possession_pct=46.0,
        passes_total=380,
        passes_completed=300,
        pass_accuracy_pct=78.9,
        shots_total=10,
        shots_on_target=4,
        shots_off_target=4,
        blocked_shots=2,
        expected_goals=1.10,
        tackles_total=22,
        tackles_won=15,
        interceptions=14,
        clearances=20,
        saves=4,
        fouls_committed=14,
        yellow_cards=3,
        red_cards=0,
    )
    # Match 3: CFC vs KBFC
    s3 = TeamMatchStatistic(
        match_id=m3.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        possession_pct=58.0,
        passes_total=510,
        passes_completed=440,
        pass_accuracy_pct=86.3,
        shots_total=14,
        shots_on_target=6,
        shots_off_target=5,
        blocked_shots=3,
        expected_goals=1.95,
        tackles_total=15,
        tackles_won=11,
        interceptions=8,
        clearances=12,
        saves=3,
        fouls_committed=9,
        yellow_cards=1,
        red_cards=0,
    )
    # Match 4: EBFC vs CFC (Missing possession_pct to verify None preservation)
    s4 = TeamMatchStatistic(
        match_id=m4.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        possession_pct=None,
        passes_total=400,
        passes_completed=320,
        pass_accuracy_pct=80.0,
        shots_total=12,
        shots_on_target=4,
        shots_off_target=6,
        blocked_shots=2,
        expected_goals=1.20,
        tackles_total=16,
        tackles_won=10,
        interceptions=11,
        clearances=16,
        saves=1,
        fouls_committed=12,
        yellow_cards=2,
        red_cards=1,
    )
    db_session.add_all([s1, s2, s3, s4])

    # Goal Events for CFC
    # Match 1: 5 goals
    e1 = MatchEvent(match_id=m1.id, team_id=cfc.id, period=MatchPeriod.FIRST_HALF, minute=12, event_type=EventType.GOAL, primary_player_id=p2.id, secondary_player_id=p3.id)
    e2 = MatchEvent(match_id=m1.id, team_id=cfc.id, period=MatchPeriod.FIRST_HALF, minute=24, event_type=EventType.GOAL, primary_player_id=p1.id, secondary_player_id=None)
    e3 = MatchEvent(match_id=m1.id, team_id=cfc.id, period=MatchPeriod.SECOND_HALF, minute=55, event_type=EventType.GOAL, primary_player_id=p3.id, secondary_player_id=p1.id)
    e4 = MatchEvent(match_id=m1.id, team_id=cfc.id, period=MatchPeriod.SECOND_HALF, minute=72, event_type=EventType.GOAL, primary_player_id=p1.id, secondary_player_id=p3.id)
    e5 = MatchEvent(match_id=m1.id, team_id=cfc.id, period=MatchPeriod.SECOND_HALF, minute=88, event_type=EventType.GOAL, primary_player_id=p2.id, secondary_player_id=None)
    # Match 2: 1 goal
    e6 = MatchEvent(match_id=m2.id, team_id=cfc.id, period=MatchPeriod.SECOND_HALF, minute=64, event_type=EventType.GOAL, primary_player_id=p1.id, secondary_player_id=p3.id)
    # Match 3: 2 goals
    e7 = MatchEvent(match_id=m3.id, team_id=cfc.id, period=MatchPeriod.FIRST_HALF, minute=30, event_type=EventType.GOAL, primary_player_id=p1.id, secondary_player_id=None)
    e8 = MatchEvent(match_id=m3.id, team_id=cfc.id, period=MatchPeriod.SECOND_HALF, minute=80, event_type=EventType.GOAL, primary_player_id=p3.id, secondary_player_id=p2.id)
    # Match 4: 1 goal
    e9 = MatchEvent(match_id=m4.id, team_id=cfc.id, period=MatchPeriod.FIRST_HALF, minute=40, event_type=EventType.GOAL, primary_player_id=p2.id, secondary_player_id=None)
    db_session.add_all([e1, e2, e3, e4, e5, e6, e7, e8, e9])
    await db_session.flush()

    return {
        "ds": ds,
        "season": season,
        "cfc": cfc,
        "ebfc": ebfc,
        "mcfc": mcfc,
        "kbfc": kbfc,
        "players": [p1, p2, p3, p4],
        "matches": [m1, m2, m3, m4, m5],
    }


# =============================================================================
# 1. Season Overview Tests
# =============================================================================

@pytest.mark.asyncio
async def test_season_overview_calculations(db_session: AsyncSession, season_engine_dataset):
    """Verifies season overview metrics: W/D/L, Points, GD, Win %, Clean Sheets, Avg Possession."""
    data = season_engine_dataset
    engine = TeamPerformanceEngine(db_session)
    res = await engine.calculate_team_season_performance(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
    )

    # 4 finished matches (scheduled Match 5 is strictly excluded)
    assert res["matches_played"] == 4
    # W: m1 (5-3), m3 (2-0) -> 2 wins
    assert res["wins"] == 2
    # D: m2 (1-1) -> 1 draw
    assert res["draws"] == 1
    # L: m4 (1-2) -> 1 loss
    assert res["losses"] == 1

    # Points = (2 * 3) + 1 = 7
    assert res["points"] == 7
    # PPM = 7 / 4 = 1.75
    assert res["points_per_match"] == 1.75

    # Goals For = 5 + 1 + 2 + 1 = 9
    assert res["goals_for"] == 9
    # Goals Against = 3 + 1 + 0 + 2 = 6
    assert res["goals_against"] == 6
    # Goal Difference = 9 - 6 = +3
    assert res["goal_difference"] == 3

    # Win % = 2/4 = 50.0%
    assert res["win_percentage"] == 50.0

    # Clean Sheets = 1 (Match 3: 2-0 vs KBFC)
    assert res["clean_sheets"] == 1
    assert res["clean_sheet_percentage"] == 25.0

    # Average Possession: (52 + 46 + 58) / 3 = 52.0% (m4 was None)
    assert res["average_possession_pct"] == 52.0
    assert "calculated_at" in res


# =============================================================================
# 2. Home and Away Split Tests
# =============================================================================

@pytest.mark.asyncio
async def test_home_away_analysis(db_session: AsyncSession, season_engine_dataset):
    """Verifies dedicated home vs away performance metrics and comparative indices."""
    data = season_engine_dataset
    engine = TeamPerformanceEngine(db_session)
    res = await engine.calculate_home_away_analysis(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
    )

    home = res["home_record"]
    away = res["away_record"]
    comp = res["comparison"]

    # Home: 2 played (m1: 5-3 W, m3: 2-0 W)
    assert home["matches_played"] == 2
    assert home["wins"] == 2
    assert home["draws"] == 0
    assert home["losses"] == 0
    assert home["points"] == 6
    assert home["goals_for"] == 7
    assert home["goals_against"] == 3
    assert home["clean_sheets"] == 1
    assert home["win_percentage"] == 100.0
    assert home["points_per_match"] == 3.0

    # Away: 2 played (m2: 1-1 D, m4: 1-2 L)
    assert away["matches_played"] == 2
    assert away["wins"] == 0
    assert away["draws"] == 1
    assert away["losses"] == 1
    assert away["points"] == 1
    assert away["goals_for"] == 2
    assert away["goals_against"] == 3
    assert away["clean_sheets"] == 0
    assert away["win_percentage"] == 0.0
    assert away["points_per_match"] == 0.5

    # Comparison
    # Point ratio home to away: 6 / 1 = 6.0
    assert comp["point_ratio_home_to_away"] == 6.0
    # Win % delta: 100.0 - 0.0 = 100.0
    assert comp["win_pct_delta"] == 100.0
    # Home advantage index: 6 / (6 + 1) * 100 = 85.71%
    assert round(comp["home_advantage_index"], 2) == 85.71
    assert "calculated_at" in res


# =============================================================================
# 3. Passing Analytics Tests
# =============================================================================

@pytest.mark.asyncio
async def test_passing_analytics_engine(db_session: AsyncSession, season_engine_dataset):
    """Verifies team passing totals, completed, failed, accuracy %, average possession, and match breakdown."""
    data = season_engine_dataset
    engine = PassingAnalyticsEngine(db_session)
    res = await engine.calculate_team_passing_metrics(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
    )

    assert res["matches_analyzed"] == 4
    # Total passes: 450 + 380 + 510 + 400 = 1740
    assert res["total_passes"] == 1740
    # Successful passes: 380 + 300 + 440 + 320 = 1440
    assert res["successful_passes"] == 1440
    # Failed passes: 1740 - 1440 = 300
    assert res["failed_passes"] == 300

    # Accuracy: 1440 * 100 / 1740 = 82.76%
    assert round(res["passing_accuracy_pct"], 2) == 82.76

    # Average possession: (52 + 46 + 58) / 3 = 52.0%
    assert res["average_possession_pct"] == 52.0

    # Match-by-match passing
    p_matches = res["passing_by_match"]
    assert len(p_matches) == 4
    # Match 1: 450 total, 380 comp, 70 failed
    assert p_matches[0]["passes_total"] == 450
    assert p_matches[0]["passes_completed"] == 380
    assert p_matches[0]["failed_passes"] == 70
    assert p_matches[0]["possession_pct"] == 52.0

    # Match 4: possession was None, verify preservation
    assert p_matches[3]["possession_pct"] is None
    assert p_matches[3]["failed_passes"] == 80
    assert "calculated_at" in res


# =============================================================================
# 4. Performance Trends Tests
# =============================================================================

@pytest.mark.asyncio
async def test_performance_trends_engine(db_session: AsyncSession, season_engine_dataset):
    """Verifies chronological progressions, rolling averages, monthly breakdowns, and points progression."""
    data = season_engine_dataset
    engine = PerformanceTrendsEngine(db_session)
    res = await engine.calculate_performance_trends(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
        rolling_window=3,
    )

    assert res["matches_analyzed"] == 4
    # Last 5 matches should contain all 4
    assert len(res["last_five_matches"]) == 4
    # Outcomes: W, D, W, L
    outcomes = [m["outcome"] for m in res["match_by_match_results"]]
    assert outcomes == ["W", "D", "W", "L"]

    # Monthly goals:
    # 2026-11: m1 (5-3), m2 (1-1) -> GF: 6, GA: 4
    # 2026-12: m3 (2-0), m4 (1-2) -> GF: 3, GA: 2
    assert res["monthly_goals_scored"]["2026-11"] == 6
    assert res["monthly_goals_conceded"]["2026-11"] == 4
    assert res["monthly_goals_scored"]["2026-12"] == 3
    assert res["monthly_goals_conceded"]["2026-12"] == 2

    # Points progression: cumulative points: 3 -> 4 -> 7 -> 7
    pts_prog = res["points_progression"]
    assert len(pts_prog) == 4
    assert [p["cumulative_points"] for p in pts_prog] == [3, 4, 7, 7]

    # Rolling trends with window 3:
    # Match 0: [W] -> GF: 5.0, GA: 3.0, PPM: 3.0
    # Match 1: [W, D] -> GF: (5+1)/2=3.0, GA: (3+1)/2=2.0, PPM: (3+1)/2=2.0
    # Match 2: [W, D, W] -> GF: (5+1+2)/3=2.67, GA: (3+1+0)/3=1.33, PPM: (3+1+3)/3=2.33
    # Match 3: [D, W, L] -> GF: (1+2+1)/3=1.33, GA: (1+0+2)/3=1.0, PPM: (1+3+0)/3=1.33
    rolling = res["rolling_trends"]
    assert len(rolling) == 4
    assert rolling[0]["rolling_points_per_match"] == 3.0
    assert rolling[1]["rolling_points_per_match"] == 2.0
    assert round(rolling[2]["rolling_points_per_match"], 2) == 2.33
    assert round(rolling[3]["rolling_points_per_match"], 2) == 1.33
    assert "calculated_at" in res


# =============================================================================
# 5. Attacking Analytics Extensions Tests
# =============================================================================

@pytest.mark.asyncio
async def test_attacking_analytics_extensions(db_session: AsyncSession, season_engine_dataset):
    """Verifies assists, goals by match, goals by player, and phase breakdown."""
    data = season_engine_dataset
    engine = AttackingAnalyticsEngine(db_session)
    res = await engine.calculate_team_attacking_metrics(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
    )

    assert res["matches_analyzed"] == 4
    assert res["goals_scored"] == 9
    assert res["goals_per_match"] == 2.25

    # Total assists recorded in goal events: Brambilla (3), Jordan Gil (1), Farukh (1) = 5
    assert res["total_assists"] == 5

    # Goals by competition phase
    phase = res["goals_by_competition_phase"]
    # 1st half: e1, e2, e7, e9 -> 4 goals
    # 2nd half: e3, e4, e5, e6, e8 -> 5 goals
    assert phase["first_half_goals"] == 4
    assert phase["second_half_goals"] == 5
    assert phase["extra_time_goals"] == 0

    # Goals by match
    gbm = res["goals_by_match"]
    assert len(gbm) == 4
    assert [m["goals"] for m in gbm] == [5, 1, 2, 1]

    # Goals by player
    gbp = res["goals_by_player"]
    # Jordan Gil: 4 goals, 1 assist
    # Farukh: 3 goals, 1 assist
    # Brambilla: 2 goals, 3 assists
    player_map = {p["player_name"]: p for p in gbp}
    assert player_map["Wilmar Jordan Gil"]["goals"] == 4
    assert player_map["Wilmar Jordan Gil"]["assists"] == 1
    assert player_map["Wilmar Jordan Gil"]["goal_contributions"] == 5
    assert player_map["Farukh Choudhary"]["goals"] == 3
    assert player_map["Lukas Brambilla"]["goals"] == 2
    assert player_map["Lukas Brambilla"]["assists"] == 3


# =============================================================================
# 6. Defensive Analytics Extensions Tests
# =============================================================================

@pytest.mark.asyncio
async def test_defensive_analytics_extensions(db_session: AsyncSession, season_engine_dataset):
    """Verifies defensive match breakdowns, clean sheets, tackles, and discipline."""
    data = season_engine_dataset
    engine = DefensiveAnalyticsEngine(db_session)
    res = await engine.calculate_team_defensive_metrics(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
    )

    assert res["matches_analyzed"] == 4
    assert res["goals_conceded"] == 6
    assert res["goals_conceded_per_match"] == 1.5
    assert res["clean_sheets"] == 1

    # Disciplinary: yellows = 2+3+1+2 = 8, reds = 1 -> index = 8 + 3(1) = 11
    assert res["yellow_cards"] == 8
    assert res["red_cards"] == 1
    assert res["discipline_index"] == 11

    # Defensive by match
    dbm = res["defensive_by_match"]
    assert len(dbm) == 4
    assert dbm[0]["goals_conceded"] == 3
    assert dbm[0]["clean_sheet"] is False
    assert dbm[2]["goals_conceded"] == 0
    assert dbm[2]["clean_sheet"] is True
    assert dbm[2]["tackles_won"] == 11
    assert "calculated_at" in res


# =============================================================================
# 7. Empty Season & Zero Division Handling Tests
# =============================================================================

@pytest.mark.asyncio
async def test_empty_season_handling(db_session: AsyncSession):
    """Verifies zero division safety when a team has no completed matches."""
    comp = Competition(code="ISL_EMPTY", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2026–27", slug="isl-empty-2026-27", is_current=True)
    team = Team(name="New Club", short_name="NC", slug="new-club")
    db_session.add_all([season, team])
    await db_session.flush()

    # Team performance
    perf_engine = TeamPerformanceEngine(db_session)
    p_res = await perf_engine.calculate_team_season_performance(team.id, season.id)
    assert p_res["matches_played"] == 0
    assert p_res["points"] == 0
    assert p_res["points_per_match"] is None
    assert p_res["win_percentage"] is None
    assert p_res["average_possession_pct"] is None

    # Home/Away
    ha_res = await perf_engine.calculate_home_away_analysis(team.id, season.id)
    assert ha_res["home_record"]["matches_played"] == 0
    assert ha_res["comparison"]["point_ratio_home_to_away"] is None
    assert ha_res["comparison"]["home_advantage_index"] is None

    # Passing
    pass_engine = PassingAnalyticsEngine(db_session)
    pass_res = await pass_engine.calculate_team_passing_metrics(team.id, season.id)
    assert pass_res["matches_analyzed"] == 0
    assert pass_res["total_passes"] is None
    assert pass_res["passing_accuracy_pct"] is None
    assert pass_res["passing_by_match"] == []

    # Trends
    trend_engine = PerformanceTrendsEngine(db_session)
    trend_res = await trend_engine.calculate_performance_trends(team.id, season.id)
    assert trend_res["matches_analyzed"] == 0
    assert trend_res["last_five_matches"] == []
    assert trend_res["monthly_goals_scored"] == {}


# =============================================================================
# 8. REST API Integration Endpoints Tests
# =============================================================================

@pytest.mark.asyncio
async def test_step5_api_endpoints(client: AsyncClient, season_engine_dataset):
    """Verifies all Step 5 API routes respond with status 200 and schema validation."""
    data = season_engine_dataset
    team_id = str(data["cfc"].id)
    season_id = str(data["season"].id)

    # 1. GET /api/v1/analytics/season
    r = await client.get(f"/api/v1/analytics/season?team_id={team_id}&season_id={season_id}")
    assert r.status_code == 200
    res_json = r.json()
    assert res_json["matches_played"] == 4
    assert res_json["points"] == 7
    assert res_json["average_possession_pct"] == 52.0

    # 2. GET /api/v1/analytics/season/{season_id}
    r = await client.get(f"/api/v1/analytics/season/{season_id}?team_id={team_id}")
    assert r.status_code == 200
    assert r.json()["matches_played"] == 4

    # 3. GET /api/v1/analytics/team/{team_id}
    r = await client.get(f"/api/v1/analytics/team/{team_id}?season_id={season_id}")
    assert r.status_code == 200
    assert r.json()["goals_for"] == 9

    # 4. GET /api/v1/analytics/team/{team_id}/attacking
    r = await client.get(f"/api/v1/analytics/team/{team_id}/attacking?season_id={season_id}")
    assert r.status_code == 200
    att_json = r.json()
    assert att_json["goals_scored"] == 9
    assert att_json["total_assists"] == 5
    assert len(att_json["goals_by_match"]) == 4

    # 5. GET /api/v1/analytics/team/{team_id}/defensive
    r = await client.get(f"/api/v1/analytics/team/{team_id}/defensive?season_id={season_id}")
    assert r.status_code == 200
    def_json = r.json()
    assert def_json["goals_conceded"] == 6
    assert len(def_json["defensive_by_match"]) == 4

    # 6. GET /api/v1/analytics/team/{team_id}/passing
    r = await client.get(f"/api/v1/analytics/team/{team_id}/passing?season_id={season_id}")
    assert r.status_code == 200
    pass_json = r.json()
    assert pass_json["total_passes"] == 1740
    assert pass_json["successful_passes"] == 1440
    assert pass_json["failed_passes"] == 300
    assert len(pass_json["passing_by_match"]) == 4

    # 7. GET /api/v1/analytics/team/{team_id}/home-away
    r = await client.get(f"/api/v1/analytics/team/{team_id}/home-away?season_id={season_id}")
    assert r.status_code == 200
    ha_json = r.json()
    assert ha_json["home_record"]["wins"] == 2
    assert ha_json["away_record"]["wins"] == 0
    assert ha_json["comparison"]["point_ratio_home_to_away"] == 6.0

    # 8. GET /api/v1/analytics/team/{team_id}/trends
    r = await client.get(f"/api/v1/analytics/team/{team_id}/trends?season_id={season_id}&rolling_window=3")
    assert r.status_code == 200
    tr_json = r.json()
    assert len(tr_json["match_by_match_results"]) == 4
    assert len(tr_json["points_progression"]) == 4
    assert len(tr_json["rolling_trends"]) == 4
    assert "2026-11" in tr_json["monthly_goals_scored"]
