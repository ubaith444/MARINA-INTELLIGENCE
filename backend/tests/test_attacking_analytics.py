"""Automated Tests for Module 2: Attacking Performance & Shot Quality Analytics Engine."""

import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from marina.analytics.attacking import AttackingAnalyticsEngine
from marina.models.common import EventType, MatchPeriod, MatchStatus, PlayerPosition, ProviderType
from marina.models.competition import Competition, Season
from marina.models.match import Match, MatchEvent
from marina.models.player import Player
from marina.models.provenance import DataSource
from marina.models.statistics import TeamMatchStatistic
from marina.models.team import Team


@pytest.fixture
async def setup_attacking_fixtures(db_session: AsyncSession):
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
    db_session.add_all([cfc, ebfc])
    await db_session.flush()

    # Players
    p1 = Player(first_name="Wilmar", last_name="Jordan Gil", known_name="Wilmar Jordan Gil", slug="wilmar-jordan-gil", primary_position=PlayerPosition.CF)
    p2 = Player(first_name="Farukh", last_name="Choudhary", known_name="Farukh Choudhary", slug="farukh-choudhary", primary_position=PlayerPosition.CF)
    p3 = Player(first_name="Lukas", last_name="Brambilla", known_name="Lukas Brambilla", slug="lukas-brambilla", primary_position=PlayerPosition.AM)
    db_session.add_all([p1, p2, p3])
    await db_session.flush()

    # Match 1: CFC 5–3 EBFC
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
    db_session.add(m1)
    await db_session.flush()

    # Team Match Statistics for CFC in Match 1 (With recorded xG)
    stat1 = TeamMatchStatistic(
        match_id=m1.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        possession_pct=52.0,
        shots_total=16,
        shots_on_target=8,
        shots_off_target=5,
        blocked_shots=3,
        expected_goals=2.85,
        big_chances_created=4,
        big_chances_missed=1,
    )
    db_session.add(stat1)

    # Goal Events for CFC in Match 1
    # Goal 1: 12th min (1st half) - Farukh Choudhary (assist Brambilla)
    e1 = MatchEvent(
        match_id=m1.id,
        team_id=cfc.id,
        period=MatchPeriod.FIRST_HALF,
        minute=12,
        event_type=EventType.GOAL,
        primary_player_id=p2.id,
        secondary_player_id=p3.id,
    )
    # Goal 2: 24th min (1st half) - Wilmar Jordan Gil
    e2 = MatchEvent(
        match_id=m1.id,
        team_id=cfc.id,
        period=MatchPeriod.FIRST_HALF,
        minute=24,
        event_type=EventType.GOAL,
        primary_player_id=p1.id,
        secondary_player_id=None,
    )
    # Goal 3: 55th min (2nd half) - Lukas Brambilla (Penalty)
    e3 = MatchEvent(
        match_id=m1.id,
        team_id=cfc.id,
        period=MatchPeriod.SECOND_HALF,
        minute=55,
        event_type=EventType.PENALTY_GOAL,
        primary_player_id=p3.id,
        secondary_player_id=None,
    )
    # Goal 4: 68th min (2nd half) - Wilmar Jordan Gil (assist Brambilla)
    e4 = MatchEvent(
        match_id=m1.id,
        team_id=cfc.id,
        period=MatchPeriod.SECOND_HALF,
        minute=68,
        event_type=EventType.GOAL,
        primary_player_id=p1.id,
        secondary_player_id=p3.id,
    )
    # Goal 5: 88th min (2nd half) - Farukh Choudhary (assist Wilmar)
    e5 = MatchEvent(
        match_id=m1.id,
        team_id=cfc.id,
        period=MatchPeriod.SECOND_HALF,
        minute=88,
        event_type=EventType.GOAL,
        primary_player_id=p2.id,
        secondary_player_id=p1.id,
    )
    db_session.add_all([e1, e2, e3, e4, e5])
    await db_session.flush()

    return {
        "season": season,
        "cfc": cfc,
        "ebfc": ebfc,
        "players": [p1, p2, p3],
        "match": m1,
        "ds": ds,
    }


@pytest.mark.asyncio
async def test_calculate_attacking_metrics_with_xg(db_session: AsyncSession, setup_attacking_fixtures):
    """Verify shooting volume, accuracy, conversion, xG shot efficiency, and player contributions."""
    data = setup_attacking_fixtures
    engine = AttackingAnalyticsEngine(db_session)

    res = await engine.calculate_team_attacking_metrics(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
    )

    assert res["matches_analyzed"] == 1
    assert res["goals_scored"] == 5
    assert res["goals_per_match"] == 5.0
    assert res["shots_total"] == 16
    assert res["shots_on_target"] == 8
    assert res["shots_off_target"] == 5
    assert res["blocked_shots"] == 3

    # Accuracy: 8 on target / 16 total = 50.0%
    assert res["shooting_accuracy_pct"] == 50.0
    # Conversion: 5 goals / 16 total = 31.25%
    assert res["conversion_rate_pct"] == 31.25

    # xG metrics (2.85 recorded)
    assert res["expected_goals"] == 2.85
    assert res["expected_goals_per_match"] == 2.85
    # Shot efficiency = 5 goals - 2.85 xG = +2.15
    assert res["shot_efficiency"] == 2.15

    # Big chances
    assert res["big_chances_created"] == 4
    assert res["big_chances_missed"] == 1

    # Half breakdown
    # 2 goals in 1st half, 3 in 2nd half
    hb = res["half_breakdown"]
    assert hb["first_half_goals"] == 2
    assert hb["second_half_goals"] == 3
    assert hb["first_half_pct"] == 40.0
    assert hb["second_half_pct"] == 60.0

    # Top contributors
    contribs = res["top_contributors"]
    assert len(contribs) == 3
    # Brambilla: 1 goal + 2 assists = 3 contributions
    # Wilmar Jordan Gil: 2 goals + 1 assist = 3 contributions
    # Farukh Choudhary: 2 goals + 0 assists = 2 contributions
    total_contrib_goals = sum(c["goals"] for c in contribs)
    assert total_contrib_goals == 5


@pytest.mark.asyncio
async def test_calculate_attacking_metrics_without_xg(db_session: AsyncSession, setup_attacking_fixtures):
    """Verify that when xG is not tracked, it remains None rather than converting to 0.0."""
    data = setup_attacking_fixtures
    # Match 2 without xG
    m2 = Match(
        season_id=data["season"].id,
        home_team_id=data["ebfc"].id,
        away_team_id=data["cfc"].id,
        scheduled_kickoff=datetime(2026, 11, 14, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=0,
        away_score=1,
        match_number=2,
    )
    db_session.add(m2)
    await db_session.flush()

    # TeamMatchStatistic for ebfc with NO expected goals tracked (None)
    stat_ebfc = TeamMatchStatistic(
        match_id=m2.id,
        team_id=data["ebfc"].id,
        data_source_id=data["ds"].id,
        possession_pct=45.0,
        shots_total=9,
        shots_on_target=3,
        shots_off_target=4,
        blocked_shots=2,
        expected_goals=None,  # Not tracked
    )
    db_session.add(stat_ebfc)
    await db_session.flush()

    engine = AttackingAnalyticsEngine(db_session)
    res = await engine.calculate_team_attacking_metrics(
        team_id=data["ebfc"].id,
        season_id=data["season"].id,
    )

    assert res["matches_analyzed"] == 1
    assert res["shots_total"] == 9
    assert res["expected_goals"] is None
    assert res["expected_goals_per_match"] is None
    assert res["shot_efficiency"] is None


@pytest.mark.asyncio
async def test_calculate_attacking_metrics_empty(db_session: AsyncSession):
    """Verify zero division and empty data handling."""
    comp = Competition(code="ISL_E", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2026–27", slug="isl-2026-27-e", is_current=True)
    team = Team(name="Kerala Blasters FC", short_name="KBFC", slug="kbfc-e")
    db_session.add_all([season, team])
    await db_session.flush()

    engine = AttackingAnalyticsEngine(db_session)
    res = await engine.calculate_team_attacking_metrics(team_id=team.id, season_id=season.id)

    assert res["matches_analyzed"] == 0
    assert res["goals_scored"] == 0
    assert res["goals_per_match"] is None
    assert res["shots_total"] == 0
    assert res["shooting_accuracy_pct"] is None
    assert res["conversion_rate_pct"] is None
    assert res["expected_goals"] is None
    assert res["shot_efficiency"] is None
