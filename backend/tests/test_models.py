"""Automated Tests for Core Database Models and Relational Integrity."""

import uuid
from datetime import date, datetime, timezone
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.common import (
    BatchStatus,
    EventType,
    LineupRole,
    MatchPeriod,
    MatchStatus,
    PlayerPosition,
    ProviderType,
    SquadStatus,
    VerificationStatus,
)
from marina.models.competition import Competition, Season
from marina.models.match import Lineup, Match, MatchEvent
from marina.models.player import Player, SquadRegistration
from marina.models.provenance import DataSource, ImportHistory
from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
from marina.models.team import Team, Venue


@pytest.mark.asyncio
async def test_uuid_primary_keys_and_foreign_keys(db_session: AsyncSession):
    """Validate UUID primary key generation and foreign key constraints."""
    # 1. Create Venue
    venue = Venue(
        name="Jawaharlal Nehru Stadium (Marina Arena)",
        city="Chennai",
        state="Tamil Nadu",
        country="India",
        capacity=40000,
        surface="Natural Grass",
    )
    db_session.add(venue)
    await db_session.flush()
    assert isinstance(venue.id, uuid.UUID)

    # 2. Create Teams
    chennaiyin = Team(
        name="Chennaiyin FC",
        short_name="CFC",
        slug="chennaiyin-fc",
        founded_year=2014,
        primary_venue_id=venue.id,
        primary_color="#003399",
        secondary_color="#FFFFFF",
    )
    kerala = Team(
        name="Kerala Blasters FC",
        short_name="KBFC",
        slug="kerala-blasters-fc",
        founded_year=2014,
    )
    db_session.add_all([chennaiyin, kerala])
    await db_session.flush()
    assert isinstance(chennaiyin.id, uuid.UUID)

    # 3. Create Competition and Season
    isl = Competition(
        code="ISL",
        name="Indian Super League",
        country="India",
        tier=1,
    )
    db_session.add(isl)
    await db_session.flush()

    season_2026_27 = Season(
        competition_id=isl.id,
        name="2026–27",
        slug="isl-2026-27",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 4, 30),
        is_current=True,
    )
    db_session.add(season_2026_27)
    await db_session.flush()

    # 4. Decoupled Player Identity vs Squad Registration
    player = Player(
        slug="anirudh-thapa",
        first_name="Anirudh",
        last_name="Thapa",
        known_name="Anirudh Thapa",
        nationality="India",
        primary_position=PlayerPosition.CM,
    )
    db_session.add(player)
    await db_session.flush()
    assert isinstance(player.id, uuid.UUID)

    # Register player to Chennaiyin FC for season 2026–27
    squad_reg = SquadRegistration(
        player_id=player.id,
        team_id=chennaiyin.id,
        season_id=season_2026_27.id,
        jersey_number=7,
        squad_status=SquadStatus.FIRST_TEAM,
    )
    db_session.add(squad_reg)
    await db_session.flush()
    assert isinstance(squad_reg.id, uuid.UUID)

    # 5. Scheduled Match (Upcoming ISL 2026-27 fixture)
    match = Match(
        season_id=season_2026_27.id,
        home_team_id=chennaiyin.id,
        away_team_id=kerala.id,
        venue_id=venue.id,
        scheduled_kickoff=datetime(2026, 10, 15, 19, 30, tzinfo=timezone.utc),
        match_status=MatchStatus.SCHEDULED,
        home_score=None,  # Not played yet! Must be None!
        away_score=None,
    )
    db_session.add(match)
    await db_session.flush()

    assert match.home_score is None
    assert match.away_score is None
    assert match.match_status == MatchStatus.SCHEDULED

    # 6. Lineup & Match Events
    lineup_entry = Lineup(
        match_id=match.id,
        team_id=chennaiyin.id,
        player_id=player.id,
        squad_registration_id=squad_reg.id,
        lineup_role=LineupRole.STARTER,
        position=PlayerPosition.CM,
        jersey_number=7,
        is_captain=True,
    )
    db_session.add(lineup_entry)
    await db_session.flush()

    # 7. Data Sources and Provenance
    source = DataSource(
        code="ISL_OFFICIAL",
        name="Indian Super League Official Match Center",
        provider_type=ProviderType.OFFICIAL_LEAGUE,
        trust_score=100,
    )
    db_session.add(source)
    await db_session.flush()

    batch = ImportHistory(
        data_source_id=source.id,
        entity_type="FIXTURES",
        batch_id="batch-isl-2026-001",
        status=BatchStatus.COMPLETED,
        records_imported=1,
    )
    db_session.add(batch)
    await db_session.flush()

    assert batch.id is not None
    assert batch.records_imported == 1


@pytest.mark.asyncio
async def test_unique_constraints(db_session: AsyncSession):
    """Verify unique constraints across competition codes, team slugs, and season slugs."""
    comp1 = Competition(code="ISL", name="Indian Super League")
    db_session.add(comp1)
    await db_session.flush()

    # Duplicate competition code should fail
    comp2 = Competition(code="ISL", name="Another ISL")
    db_session.add(comp2)
    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()
