"""Automated Tests for Module 5: Match Intelligence and Head-to-Head Tactical Analytics."""

import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from marina.analytics.match_intelligence import MatchIntelligenceEngine
from marina.models.common import EventType, MatchPeriod, MatchStatus, PlayerPosition, ProviderType
from marina.models.competition import Competition, Season
from marina.models.match import Match, MatchEvent
from marina.models.player import Player
from marina.models.provenance import DataSource
from marina.models.statistics import TeamMatchStatistic
from marina.models.team import Team, Venue


@pytest.fixture
async def setup_match_intelligence_fixtures(db_session: AsyncSession):
    ds = DataSource(
        code="ISL_MATCH_INTEL",
        name="ISL Official Match Intelligence",
        provider_type=ProviderType.OFFICIAL_LEAGUE,
    )
    db_session.add(ds)
    await db_session.flush()

    comp = Competition(code="ISL_MI", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(competition_id=comp.id, name="2026–27", slug="isl-2026-27-mi", is_current=True)
    venue = Venue(name="Jawaharlal Nehru Stadium", city="Chennai", state="Tamil Nadu", capacity=40000)
    db_session.add_all([season, venue])
    await db_session.flush()

    cfc = Team(name="Chennaiyin FC", short_name="CFC", slug="chennaiyin-fc-mi", primary_venue_id=venue.id)
    ebfc = Team(name="East Bengal FC", short_name="EBFC", slug="east-bengal-fc-mi")
    db_session.add_all([cfc, ebfc])
    await db_session.flush()

    p1 = Player(first_name="Farukh", last_name="Choudhary", known_name="Farukh Choudhary", slug="farukh-c-mi", primary_position=PlayerPosition.CF)
    p2 = Player(first_name="Lukas", last_name="Brambilla", known_name="Lukas Brambilla", slug="lukas-b-mi", primary_position=PlayerPosition.AM)
    p3 = Player(first_name="Madih", last_name="Talal", known_name="Madih Talal", slug="madih-t-mi", primary_position=PlayerPosition.AM)
    db_session.add_all([p1, p2, p3])
    await db_session.flush()

    # Match 1: CFC 2–1 EBFC
    m1 = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=ebfc.id,
        venue_id=venue.id,
        scheduled_kickoff=datetime(2026, 11, 7, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=2,
        away_score=1,
        match_number=1,
        attendance=18500,
        referee="Tejas Nagvenkar",
    )
    # Match 2: EBFC 0–1 CFC (Reverse fixture for head-to-head)
    m2 = Match(
        season_id=season.id,
        home_team_id=ebfc.id,
        away_team_id=cfc.id,
        scheduled_kickoff=datetime(2026, 12, 12, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=0,
        away_score=1,
        match_number=2,
    )
    db_session.add_all([m1, m2])
    await db_session.flush()

    # Team Match Statistics for Match 1
    stat_cfc = TeamMatchStatistic(
        match_id=m1.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        possession_pct=54.0,
        shots_total=14,
        shots_on_target=6,
        passes_total=420,
        passes_completed=350,
        pass_accuracy_pct=83.3,
        tackles_total=16,
        tackles_won=12,
        corners=6,
        yellow_cards=2,
        red_cards=0,
    )
    stat_ebfc = TeamMatchStatistic(
        match_id=m1.id,
        team_id=ebfc.id,
        data_source_id=ds.id,
        possession_pct=46.0,
        shots_total=10,
        shots_on_target=4,
        passes_total=360,
        passes_completed=280,
        pass_accuracy_pct=77.8,
        tackles_total=18,
        tackles_won=11,
        corners=3,
        yellow_cards=3,
        red_cards=0,
    )
    db_session.add_all([stat_cfc, stat_ebfc])

    # Events in Match 1:
    # 20' CFC Goal: Farukh Choudhary (assist Brambilla) - 1st half
    e1 = MatchEvent(
        match_id=m1.id,
        team_id=cfc.id,
        period=MatchPeriod.FIRST_HALF,
        minute=20,
        event_type=EventType.GOAL,
        primary_player_id=p1.id,
        secondary_player_id=p2.id,
        description="Goal scored by Farukh Choudhary with a right footed shot.",
    )
    # 42' EBFC Yellow Card - 1st half
    e2 = MatchEvent(
        match_id=m1.id,
        team_id=ebfc.id,
        period=MatchPeriod.FIRST_HALF,
        minute=42,
        event_type=EventType.YELLOW_CARD,
        primary_player_id=p3.id,
        description="Yellow card for reckless challenge.",
    )
    # 65' EBFC Goal: Madih Talal - 2nd half
    e3 = MatchEvent(
        match_id=m1.id,
        team_id=ebfc.id,
        period=MatchPeriod.SECOND_HALF,
        minute=65,
        event_type=EventType.GOAL,
        primary_player_id=p3.id,
        description="Equalizer by Madih Talal.",
    )
    # 83' CFC Goal: Lukas Brambilla - 2nd half
    e4 = MatchEvent(
        match_id=m1.id,
        team_id=cfc.id,
        period=MatchPeriod.SECOND_HALF,
        minute=83,
        event_type=EventType.GOAL,
        primary_player_id=p2.id,
        description="Winning goal by Lukas Brambilla from 20 yards.",
    )
    db_session.add_all([e1, e2, e3, e4])
    await db_session.flush()

    return {
        "m1": m1,
        "m2": m2,
        "cfc": cfc,
        "ebfc": ebfc,
        "venue": venue,
        "ds": ds,
    }


@pytest.mark.asyncio
async def test_generate_match_report(db_session: AsyncSession, setup_match_intelligence_fixtures):
    """Verify single match report generation, side-by-side stats, half analysis, and timeline."""
    data = setup_match_intelligence_fixtures
    engine = MatchIntelligenceEngine(db_session)

    report = await engine.generate_match_report(match_id=data["m1"].id)

    assert report["match_id"] == str(data["m1"].id)
    assert report["venue"] == "Jawaharlal Nehru Stadium"
    assert report["attendance"] == 18500
    assert report["referee"] == "Tejas Nagvenkar"

    # Home team (CFC) stats
    home = report["home_team"]
    assert home["name"] == "Chennaiyin FC"
    assert home["score"] == 2
    assert home["statistics"]["possession_pct"] == 54.0
    assert home["statistics"]["shots_total"] == 14
    assert home["statistics"]["shots_on_target"] == 6

    # Away team (EBFC) stats
    away = report["away_team"]
    assert away["name"] == "East Bengal FC"
    assert away["score"] == 1
    assert away["statistics"]["possession_pct"] == 46.0

    # Half by half breakdown
    h_by_h = report["half_by_half"]
    # 1st half: CFC 1 (20'), EBFC 0 -> 1-0
    assert h_by_h["first_half"]["score"] == "1-0"
    assert h_by_h["first_half"]["home_goals"] == 1
    assert h_by_h["first_half"]["away_goals"] == 0
    assert h_by_h["first_half"]["events_count"] == 2  # goal + yellow card

    # 2nd half: CFC 1 (83'), EBFC 1 (65') -> 1-1
    assert h_by_h["second_half"]["score"] == "1-1"
    assert h_by_h["second_half"]["home_goals"] == 1
    assert h_by_h["second_half"]["away_goals"] == 1
    assert h_by_h["second_half"]["events_count"] == 2  # 2 goals

    # Chronological timeline
    timeline = report["timeline"]
    assert len(timeline) == 4
    assert timeline[0]["minute"] == 20
    assert timeline[0]["event_type"] == "GOAL"
    assert timeline[0]["primary_player"] == "Farukh Choudhary"
    assert timeline[0]["secondary_player"] == "Lukas Brambilla"


@pytest.mark.asyncio
async def test_calculate_head_to_head(db_session: AsyncSession, setup_match_intelligence_fixtures):
    """Verify historical head-to-head aggregation between two teams."""
    data = setup_match_intelligence_fixtures
    engine = MatchIntelligenceEngine(db_session)

    h2h = await engine.calculate_head_to_head(
        team_a_id=data["cfc"].id,
        team_b_id=data["ebfc"].id,
    )

    # 2 matches played: CFC won 2-1 (home) and 1-0 (away) -> 2 CFC wins, 0 EBFC wins, 0 draws
    assert h2h["matches_played"] == 2
    assert h2h["team_a_wins"] == 2
    assert h2h["team_b_wins"] == 0
    assert h2h["draws"] == 0
    assert h2h["team_a_goals"] == 3  # 2 + 1
    assert h2h["team_b_goals"] == 1  # 1 + 0


@pytest.mark.asyncio
async def test_match_report_not_found(db_session: AsyncSession):
    """Verify ValueError when match does not exist."""
    engine = MatchIntelligenceEngine(db_session)
    with pytest.raises(ValueError, match="not found"):
        await engine.generate_match_report(match_id=uuid.uuid4())
