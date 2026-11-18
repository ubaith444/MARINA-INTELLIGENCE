"""Automated Tests for Module 4: Player Performance, Per-90 Standardizer, and Head-to-Head Engine."""

import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from marina.analytics.player_intelligence import PlayerIntelligenceEngine
from marina.models.common import LineupRole, MatchStatus, PlayerPosition, ProviderType
from marina.models.competition import Competition, Season
from marina.models.match import Lineup, Match
from marina.models.player import Player
from marina.models.provenance import DataSource
from marina.models.statistics import PlayerMatchStatistic
from marina.models.team import Team


@pytest.fixture
async def setup_player_fixtures(db_session: AsyncSession):
    ds = DataSource(
        code="ISL_OFFICIAL_PLY",
        name="ISL Official Player Stats",
        provider_type=ProviderType.OFFICIAL_LEAGUE,
    )
    db_session.add(ds)
    await db_session.flush()

    comp = Competition(code="ISL_PLY", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2026–27", slug="isl-2026-27-ply", is_current=True)
    db_session.add(season)
    await db_session.flush()

    cfc = Team(name="Chennaiyin FC", short_name="CFC", slug="chennaiyin-fc-ply")
    ebfc = Team(name="East Bengal FC", short_name="EBFC", slug="east-bengal-fc-ply")
    db_session.add_all([cfc, ebfc])
    await db_session.flush()

    p1 = Player(
        first_name="Wilmar",
        last_name="Jordan Gil",
        known_name="Wilmar Jordan Gil",
        slug="wilmar-jordan-gil",
        primary_position=PlayerPosition.CF,
        nationality="Colombia",
    )
    p2 = Player(
        first_name="Ryan",
        last_name="Edwards",
        known_name="Ryan Edwards",
        slug="ryan-edwards",
        primary_position=PlayerPosition.CB,
        nationality="England",
    )
    p3 = Player(
        first_name="Vincy",
        last_name="Barretto",
        known_name="Vincy Barretto",
        slug="vincy-barretto",
        primary_position=PlayerPosition.RW,
        nationality="India",
    )
    db_session.add_all([p1, p2, p3])
    await db_session.flush()

    # Match 1: CFC vs EBFC
    m1 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=ebfc.id,
        scheduled_kickoff=datetime(2026, 11, 7, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=3,
        away_score=1,
        match_number=1,
    )
    # Match 2: EBFC vs CFC
    m2 = Match(
        season_id=season.id,
        home_team_id=ebfc.id,
        away_team_id=cfc.id,
        scheduled_kickoff=datetime(2026, 11, 14, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=0,
        away_score=2,
        match_number=2,
    )
    db_session.add_all([m1, m2])
    await db_session.flush()

    # Lineups for m1
    l1_p1 = Lineup(match_id=m1.id, team_id=cfc.id, player_id=p1.id, lineup_role=LineupRole.STARTER, minutes_played=85)
    l1_p2 = Lineup(match_id=m1.id, team_id=cfc.id, player_id=p2.id, lineup_role=LineupRole.STARTER, minutes_played=90)
    l1_p3 = Lineup(match_id=m1.id, team_id=cfc.id, player_id=p3.id, lineup_role=LineupRole.BENCH, is_substitute_in=True, sub_in_minute=75, minutes_played=15)

    # Lineups for m2
    l2_p1 = Lineup(match_id=m2.id, team_id=cfc.id, player_id=p1.id, lineup_role=LineupRole.STARTER, minutes_played=90)
    l2_p2 = Lineup(match_id=m2.id, team_id=cfc.id, player_id=p2.id, lineup_role=LineupRole.STARTER, minutes_played=90)
    l2_p3 = Lineup(match_id=m2.id, team_id=cfc.id, player_id=p3.id, lineup_role=LineupRole.BENCH, is_substitute_in=True, sub_in_minute=80, minutes_played=10)

    db_session.add_all([l1_p1, l1_p2, l1_p3, l2_p1, l2_p2, l2_p3])
    await db_session.flush()

    # Statistics for p1 (Jordan Gil) in m1 and m2: total minutes = 175
    stat_p1_m1 = PlayerMatchStatistic(
        match_id=m1.id,
        player_id=p1.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        minutes_played=85,
        goals=2,
        assists=0,
        shots_total=5,
        shots_on_target=3,
        passes_total=24,
        passes_completed=18,
        expected_goals=1.4,
    )
    stat_p1_m2 = PlayerMatchStatistic(
        match_id=m2.id,
        player_id=p1.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        minutes_played=90,
        goals=1,
        assists=1,
        shots_total=4,
        shots_on_target=2,
        passes_total=20,
        passes_completed=16,
        expected_goals=0.8,
    )

    # Statistics for p2 (Ryan Edwards) in m1 and m2: total minutes = 180 (Defender)
    stat_p2_m1 = PlayerMatchStatistic(
        match_id=m1.id,
        player_id=p2.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        minutes_played=90,
        goals=0,
        assists=0,
        tackles_total=5,
        tackles_won=4,
        interceptions=6,
        clearances=8,
        passes_total=55,
        passes_completed=48,
    )
    stat_p2_m2 = PlayerMatchStatistic(
        match_id=m2.id,
        player_id=p2.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        minutes_played=90,
        goals=0,
        assists=0,
        tackles_total=4,
        tackles_won=3,
        interceptions=5,
        clearances=9,
        passes_total=60,
        passes_completed=54,
    )

    # Statistics for p3 (Vincy Barretto): only 25 minutes total
    stat_p3_m1 = PlayerMatchStatistic(
        match_id=m1.id,
        player_id=p3.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        minutes_played=15,
        goals=0,
        assists=0,
        shots_total=1,
    )
    stat_p3_m2 = PlayerMatchStatistic(
        match_id=m2.id,
        player_id=p3.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        minutes_played=10,
        goals=0,
        assists=0,
    )

    db_session.add_all([stat_p1_m1, stat_p1_m2, stat_p2_m1, stat_p2_m2, stat_p3_m1, stat_p3_m2])
    await db_session.flush()

    return {
        "season": season,
        "cfc": cfc,
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "ds": ds,
    }


@pytest.mark.asyncio
async def test_player_performance_per_90_calculations(db_session: AsyncSession, setup_player_fixtures):
    """Verify player appearances, minutes, totals, and per-90 rates when minutes are sufficient."""
    data = setup_player_fixtures
    engine = PlayerIntelligenceEngine(db_session)

    res = await engine.calculate_player_performance(
        player_id=data["p1"].id,
        season_id=data["season"].id,
        min_minutes_for_per90=45,
    )

    assert res["appearances"] == 2
    assert res["starts"] == 2
    assert res["substitute_appearances"] == 0
    assert res["minutes_played"] == 175  # 85 + 90

    raw = res["raw_totals"]
    assert raw["goals"] == 3
    assert raw["assists"] == 1
    assert raw["goal_contributions"] == 4
    assert raw["shots_total"] == 9
    assert raw["shots_on_target"] == 5
    assert raw["expected_goals"] == 2.20

    # Per-90 calculations: 175 minutes = 1.9444 90s
    p90 = res["per_90"]
    assert p90["has_sufficient_minutes"] is True
    # Goals per 90: (3 / 175) * 90 = 1.54
    assert p90["goals_per_90"] == round((3 / 175) * 90, 2)
    # Assists per 90: (1 / 175) * 90 = 0.51
    assert p90["assists_per_90"] == round((1 / 175) * 90, 2)
    # Expected goals per 90: (2.20 / 175) * 90 = 1.13
    assert p90["expected_goals_per_90"] == round((2.20 / 175) * 90, 2)


@pytest.mark.asyncio
async def test_player_performance_insufficient_sample_size(db_session: AsyncSession, setup_player_fixtures):
    """Verify per-90 metrics are suppressed (None) when minutes are below threshold to prevent noise."""
    data = setup_player_fixtures
    engine = PlayerIntelligenceEngine(db_session)

    # p3 played only 25 minutes, default threshold is 45 min
    res = await engine.calculate_player_performance(
        player_id=data["p3"].id,
        season_id=data["season"].id,
        min_minutes_for_per90=45,
    )

    assert res["appearances"] == 2
    assert res["starts"] == 0
    assert res["substitute_appearances"] == 2
    assert res["minutes_played"] == 25

    p90 = res["per_90"]
    assert p90["has_sufficient_minutes"] is False
    assert p90["goals_per_90"] is None
    assert p90["assists_per_90"] is None
    assert p90["shots_per_90"] is None


@pytest.mark.asyncio
async def test_player_comparison_radar(db_session: AsyncSession, setup_player_fixtures):
    """Verify head-to-head comparison and 5-dimension radar output."""
    data = setup_player_fixtures
    engine = PlayerIntelligenceEngine(db_session)

    comp = await engine.compare_players(
        player_a_id=data["p1"].id,
        player_b_id=data["p2"].id,
        season_id=data["season"].id,
    )

    assert "player_a" in comp
    assert "player_b" in comp
    assert "radar_comparison" in comp

    radar = comp["radar_comparison"]
    dimensions = {r["dimension"]: r for r in radar}

    assert "Scoring Threat" in dimensions
    assert "Shot Volume" in dimensions
    assert "Playmaking / Assists" in dimensions
    assert "Passing Output" in dimensions
    assert "Defensive Ball Winning" in dimensions

    # p1 is a striker with 3 goals: Scoring Threat score should be higher than defender p2
    assert dimensions["Scoring Threat"]["player_a_score"] > dimensions["Scoring Threat"]["player_b_score"]
    # p2 is a center-back with tackles & interceptions: Defensive Ball Winning should be higher than striker p1
    assert dimensions["Defensive Ball Winning"]["player_b_score"] > dimensions["Defensive Ball Winning"]["player_a_score"]

    # All radar scores must be clamped in [0, 100]
    for r in radar:
        assert 0.0 <= r["player_a_score"] <= 100.0
        assert 0.0 <= r["player_b_score"] <= 100.0


@pytest.mark.asyncio
async def test_player_not_found(db_session: AsyncSession):
    """Verify ValueError is raised for non-existent player."""
    engine = PlayerIntelligenceEngine(db_session)
    with pytest.raises(ValueError, match="not found"):
        await engine.calculate_player_performance(player_id=uuid.uuid4())
