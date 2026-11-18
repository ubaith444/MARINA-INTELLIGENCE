"""Automated Verification of MARINA INTELLIGENCE Core Data Integrity Rules.

Verifies:
1. Rejection of fabricated match scores for SCHEDULED fixtures.
2. Rejection of statistics for unplayed / upcoming fixtures.
3. Retention of NULL for unmeasured metrics (NEVER converting to 0).
4. Provenance and verification requirement.
"""

import uuid
from datetime import date, datetime, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import (
    FabricatedDataViolationError,
    IntegrityConstraintViolationError,
)
from marina.models.common import (
    MatchStatus,
    PlayerPosition,
    ProviderType,
    VerificationStatus,
)
from marina.models.competition import Competition, Season
from marina.models.match import Match
from marina.models.player import Player
from marina.models.provenance import DataSource
from marina.models.team import Team
from marina.schemas.match import MatchCreate
from marina.schemas.statistics import (
    PlayerMatchStatisticCreate,
    TeamMatchStatisticCreate,
)
from marina.services.match_service import MatchService
from marina.services.statistics_service import StatisticsService


@pytest.fixture
async def setup_isl_entities(db_session: AsyncSession):
    comp = Competition(code="ISL", name="Indian Super League")
    db_session.add(comp)
    await db_session.flush()

    season = Season(
        competition_id=comp.id,
        name="2026–27",
        slug="isl-2026-27",
        is_current=True,
    )
    db_session.add(season)
    await db_session.flush()

    cfc = Team(name="Chennaiyin FC", short_name="CFC", slug="chennaiyin-fc")
    mbsg = Team(name="Mohun Bagan SG", short_name="MBSG", slug="mohun-bagan-sg")
    db_session.add_all([cfc, mbsg])
    await db_session.flush()

    player = Player(
        slug="farukh-choudhary",
        first_name="Farukh",
        last_name="Choudhary",
        nationality="India",
        primary_position=PlayerPosition.LW,
    )
    db_session.add(player)
    await db_session.flush()

    source = DataSource(
        code="ISL_OFFICIAL",
        name="ISL Official Data",
        provider_type=ProviderType.OFFICIAL_LEAGUE,
    )
    db_session.add(source)
    await db_session.flush()

    return {
        "season": season,
        "cfc": cfc,
        "mbsg": mbsg,
        "player": player,
        "source": source,
    }


@pytest.mark.asyncio
async def test_forbid_fabricated_score_on_scheduled_match(
    db_session: AsyncSession, setup_isl_entities
):
    """Rule: A scheduled future fixture must NOT have pre-populated scores."""
    data = setup_isl_entities
    service = MatchService(db_session)

    # Attempting to schedule a match with fabricated scores must fail
    with pytest.raises(FabricatedDataViolationError):
        await service.schedule_match(
            MatchCreate(
                season_id=data["season"].id,
                home_team_id=data["cfc"].id,
                away_team_id=data["mbsg"].id,
                scheduled_kickoff=datetime(2026, 11, 20, 19, 30, tzinfo=timezone.utc),
                match_status=MatchStatus.SCHEDULED,
                home_score=2,  # Fabricated score!
                away_score=1,
            )
        )


@pytest.mark.asyncio
async def test_forbid_statistics_for_scheduled_unplayed_fixture(
    db_session: AsyncSession, setup_isl_entities
):
    """Rule: Cannot record player or team statistics for a SCHEDULED match."""
    data = setup_isl_entities
    match_service = MatchService(db_session)
    stats_service = StatisticsService(db_session)

    # Legitimate scheduled match with null scores
    match = await match_service.schedule_match(
        MatchCreate(
            season_id=data["season"].id,
            home_team_id=data["cfc"].id,
            away_team_id=data["mbsg"].id,
            scheduled_kickoff=datetime(2026, 11, 25, 19, 30, tzinfo=timezone.utc),
            match_status=MatchStatus.SCHEDULED,
            home_score=None,
            away_score=None,
        )
    )

    # Attempting to record team statistics for this scheduled match must be rejected
    with pytest.raises(FabricatedDataViolationError):
        await stats_service.record_team_statistics(
            TeamMatchStatisticCreate(
                match_id=match.id,
                team_id=data["cfc"].id,
                data_source_id=data["source"].id,
                possession_pct=54.2,
            )
        )

    # Attempting to record player statistics for this scheduled match must also be rejected
    with pytest.raises(FabricatedDataViolationError):
        await stats_service.record_player_statistics(
            PlayerMatchStatisticCreate(
                match_id=match.id,
                player_id=data["player"].id,
                team_id=data["cfc"].id,
                data_source_id=data["source"].id,
                goals=1,
            )
        )


@pytest.mark.asyncio
async def test_unavailable_statistics_remain_null_not_zero(
    db_session: AsyncSession, setup_isl_entities
):
    """Rule: Unavailable statistics MUST remain None / NULL, never default to 0."""
    data = setup_isl_entities
    stats_service = StatisticsService(db_session)

    # Create a finished match fixture
    finished_match = Match(
        season_id=data["season"].id,
        home_team_id=data["cfc"].id,
        away_team_id=data["mbsg"].id,
        scheduled_kickoff=datetime(2026, 9, 20, 19, 30, tzinfo=timezone.utc),
        actual_kickoff=datetime(2026, 9, 20, 19, 30, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=1,
        away_score=0,
    )
    db_session.add(finished_match)
    await db_session.flush()

    # Record player statistics where only minutes_played and goals are known;
    # advanced tracking (xG, distance_covered_km, sprints) are unavailable
    player_stat = await stats_service.record_player_statistics(
        PlayerMatchStatisticCreate(
            match_id=finished_match.id,
            player_id=data["player"].id,
            team_id=data["cfc"].id,
            data_source_id=data["source"].id,
            verification_status=VerificationStatus.OFFICIAL,
            is_verified=True,
            minutes_played=90,
            goals=1,
            # expected_goals, distance_covered_km, sprints_count, top_speed_kmh are omitted
        )
    )

    # CRITICAL ASSERTIONS: Unmeasured metrics MUST be None, NEVER 0!
    assert player_stat.expected_goals is None
    assert player_stat.expected_assists is None
    assert player_stat.distance_covered_km is None
    assert player_stat.sprints_count is None
    assert player_stat.top_speed_kmh is None
    assert player_stat.tackles_won is None

    # Observed values are recorded accurately
    assert player_stat.minutes_played == 90
    assert player_stat.goals == 1
    assert player_stat.verification_status == VerificationStatus.OFFICIAL


@pytest.mark.asyncio
async def test_provenance_requirement(db_session: AsyncSession, setup_isl_entities):
    """Rule: Statistics cannot be recorded without an authoritative, existing DataSource."""
    data = setup_isl_entities
    stats_service = StatisticsService(db_session)

    finished_match = Match(
        season_id=data["season"].id,
        home_team_id=data["cfc"].id,
        away_team_id=data["mbsg"].id,
        scheduled_kickoff=datetime(2026, 9, 20, 19, 30, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=0,
        away_score=0,
    )
    db_session.add(finished_match)
    await db_session.flush()

    fake_source_id = uuid.uuid4()
    with pytest.raises(IntegrityConstraintViolationError):
        await stats_service.record_team_statistics(
            TeamMatchStatisticCreate(
                match_id=finished_match.id,
                team_id=data["cfc"].id,
                data_source_id=fake_source_id,  # Non-existent source
                possession_pct=50.0,
            )
        )
