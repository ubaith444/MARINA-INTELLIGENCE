"""Integration and Unit Tests for Chennaiyin FC 2026–27 Fixture Management."""

import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.common import MatchStatus
from marina.models.competition import Competition, Season
from marina.models.match import Match
from marina.models.team import Team, Venue
from marina.services.fixture_service import FixtureService


@pytest.fixture
async def setup_fixture_season(db_session: AsyncSession) -> Season:
    """Prepares clean test season and clubs."""
    comp = Competition(code="ISL_TEST", name="Indian Super League", country="India", federation="AIFF")
    db_session.add(comp)
    await db_session.flush()

    season = Season(
        competition_id=comp.id,
        name="2026–27",
        slug="isl-2026-27-test",
        is_current=True,
    )
    db_session.add(season)

    cfc = Team(name="Chennaiyin FC", short_name="CFC", slug="chennaiyin-fc")
    db_session.add(cfc)
    await db_session.flush()

    return season


@pytest.mark.asyncio
async def test_import_24_fixtures_and_idempotency(db_session: AsyncSession, setup_fixture_season: Season):
    """Verifies that 24 fixtures are imported, correctly partitioned into 12 first-leg and 12 second-leg, and idempotent."""
    service = FixtureService(db_session)

    # 1. First import from bundled data
    cur_dir = os_dir = __file__
    import os
    data_path = os.path.join(os.path.dirname(os.path.dirname(os_dir)), "src", "marina", "data", "chennaiyin_fc_2026_27_fixtures.json")
    with open(data_path, "r", encoding="utf-8") as f:
        records = service.parse_raw_fixtures(f.read())

    res1 = await service.import_fixtures(records, season_id=setup_fixture_season.id)
    await db_session.flush()

    assert res1["total_processed"] == 24
    assert res1["published_count"] == 12
    assert res1["provisional_count"] == 12
    assert res1["discrepancies_flagged"] == 1
    assert res1["new_created"] == 24

    # Verify count in database
    stmt = select(Match).where(Match.season_id == setup_fixture_season.id)
    matches = (await db_session.execute(stmt)).scalars().all()
    assert len(matches) == 24

    # 2. Idempotent Second Run (0 new created, 24 updated)
    res2 = await service.import_fixtures(records, season_id=setup_fixture_season.id)
    await db_session.flush()

    assert res2["total_processed"] == 24
    assert res2["new_created"] == 0
    assert res2["updated"] == 24

    matches_after = (await db_session.execute(stmt)).scalars().all()
    assert len(matches_after) == 24


@pytest.mark.asyncio
async def test_match_24_null_preservation(db_session: AsyncSession, setup_fixture_season: Season):
    """Verifies Requirement 5: Missing dates, venues and kickoff times for #24 remain strictly NULL."""
    service = FixtureService(db_session)
    import os
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "marina", "data", "chennaiyin_fc_2026_27_fixtures.json")
    with open(data_path, "r", encoding="utf-8") as f:
        records = service.parse_raw_fixtures(f.read())

    await service.import_fixtures(records, season_id=setup_fixture_season.id)
    await db_session.flush()

    stmt = select(Match).where(
        Match.season_id == setup_fixture_season.id,
        Match.match_number == 24,
    )
    m24 = (await db_session.execute(stmt)).scalars().first()

    assert m24 is not None
    assert m24.scheduled_kickoff is None
    assert m24.venue_id is None
    assert m24.kickoff_time_ist is None
    assert m24.publication_status == "PROVISIONAL"
    assert m24.verification_status == "PENDING"
    assert m24.venue_verification_status == "TBC"
    assert m24.home_score is None
    assert m24.away_score is None


@pytest.mark.asyncio
async def test_match_7_discrepancy_flag(db_session: AsyncSession, setup_fixture_season: Season):
    """Verifies Schedule Discrepancy requirement for Mumbai City FC fixture #7."""
    service = FixtureService(db_session)
    import os
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "marina", "data", "chennaiyin_fc_2026_27_fixtures.json")
    with open(data_path, "r", encoding="utf-8") as f:
        records = service.parse_raw_fixtures(f.read())

    await service.import_fixtures(records, season_id=setup_fixture_season.id)
    await db_session.flush()

    stmt = select(Match).where(
        Match.season_id == setup_fixture_season.id,
        Match.match_number == 7,
    )
    m7 = (await db_session.execute(stmt)).scalars().first()

    assert m7 is not None
    assert m7.has_discrepancy is True
    assert m7.verification_status == "DISCREPANCY_FLAGGED"
    assert "Mumbai City" in (m7.discrepancy_notes or "")


@pytest.mark.asyncio
async def test_preserve_verified_completed_score(db_session: AsyncSession, setup_fixture_season: Season):
    """Verifies that an already played/verified score is never overwritten with NULL upon fixture re-sync."""
    service = FixtureService(db_session)

    # Pre-create match 5 with verified score
    cfc = (await db_session.execute(select(Team).where(Team.slug == "chennaiyin-fc"))).scalars().first()
    ebfc = await service.resolve_or_create_team("East Bengal FC")

    m5 = Match(
        season_id=setup_fixture_season.id,
        home_team_id=cfc.id,
        away_team_id=ebfc.id,
        match_number=5,
        scheduled_kickoff=datetime(2026, 11, 7, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=5,
        away_score=3,
        publication_status="PUBLISHED",
        verification_status="VERIFIED",
    )
    db_session.add(m5)
    await db_session.flush()

    # Re-import fixtures
    import os
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "marina", "data", "chennaiyin_fc_2026_27_fixtures.json")
    with open(data_path, "r", encoding="utf-8") as f:
        records = service.parse_raw_fixtures(f.read())

    await service.import_fixtures(records, season_id=setup_fixture_season.id)
    await db_session.flush()

    # Fetch match 5 again
    stmt = select(Match).where(
        Match.season_id == setup_fixture_season.id,
        Match.match_number == 5,
    )
    m5_after = (await db_session.execute(stmt)).scalars().first()

    assert m5_after is not None
    assert m5_after.match_status == MatchStatus.FINISHED
    assert m5_after.home_score == 5
    assert m5_after.away_score == 3


@pytest.mark.asyncio
async def test_fixture_filters(db_session: AsyncSession, setup_fixture_season: Season):
    """Verifies multi-criteria filtering for opponent, home/away, and status."""
    service = FixtureService(db_session)
    import os
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "marina", "data", "chennaiyin_fc_2026_27_fixtures.json")
    with open(data_path, "r", encoding="utf-8") as f:
        records = service.parse_raw_fixtures(f.read())

    await service.import_fixtures(records, season_id=setup_fixture_season.id)
    await db_session.flush()

    # Filter Home matches for Chennaiyin FC
    home_matches = await service.list_fixtures(season_id=setup_fixture_season.id, home_away="HOME")
    assert len(home_matches) == 12

    # Filter Away matches for Chennaiyin FC
    away_matches = await service.list_fixtures(season_id=setup_fixture_season.id, home_away="AWAY")
    assert len(away_matches) == 12

    # Filter Opponent
    kerala_matches = await service.list_fixtures(season_id=setup_fixture_season.id, opponent="Kerala Blasters")
    assert len(kerala_matches) == 2  # Match 4 (Home) and Match 18 (Away)

    # Filter Discrepancy
    discrepancy_matches = await service.list_fixtures(season_id=setup_fixture_season.id, verification_status="DISCREPANCY_FLAGGED")
    assert len(discrepancy_matches) == 1
    assert discrepancy_matches[0].match_number == 7


@pytest.mark.asyncio
async def test_fixture_rest_endpoints(client: AsyncClient, db_session: AsyncSession, setup_fixture_season: Season):
    """Verifies all REST API fixture endpoints."""
    # 1. Import via API
    res = await client.post(f"/api/v1/fixtures/import?season_id={setup_fixture_season.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["total_processed"] == 24
    assert data["published_count"] == 12
    assert data["provisional_count"] == 12

    # 2. GET /fixtures/season/2026-27
    res_season = await client.get("/api/v1/fixtures/season/2026-27")
    assert res_season.status_code == 200
    fixtures = res_season.json()
    assert len(fixtures) == 24
    assert fixtures[0]["match_number"] == 1
    assert fixtures[23]["match_number"] == 24
    assert fixtures[23]["scheduled_kickoff"] is None

    # 3. GET /fixtures with filters
    res_filt = await client.get("/api/v1/fixtures?home_away=HOME&verification_status=PUBLISHED")
    assert res_filt.status_code == 200
    published_home = res_filt.json()
    assert len(published_home) > 0
    for f in published_home:
        assert f["publication_status"] == "PUBLISHED"

    # 4. GET /fixtures/{id}
    m1_id = fixtures[0]["id"]
    res_m1 = await client.get(f"/api/v1/fixtures/{m1_id}")
    assert res_m1.status_code == 200
    m1_data = res_m1.json()
    assert m1_data["match_number"] == 1
    assert m1_data["home_team"]["name"] == "FC Goa"
    assert m1_data["away_team"]["name"] == "Chennaiyin FC"
