"""Tests for Historical Match Lineups, Formations, and Substitutions Ingestion."""

import os
import json
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.common import EventType, LineupRole, MatchStatus, VerificationStatus
from marina.models.competition import Competition, Season
from marina.models.match import Lineup, Match, MatchEvent, MatchLineup, MatchSubstitute
from marina.models.player import Player
from marina.models.statistics import PlayerMatchStatistic
from marina.models.team import Team
from marina.services.fixture_service import FixtureService
from marina.services.match_ingestion_service import MatchIngestionService
from marina.services.squad_sync_service import SquadSyncService
from marina.services.lineup_import_service import LineupImportService, HISTORICAL_LINEUP_SPECS


@pytest.fixture(autouse=True)
async def seed_lineup_test_db(db_session: AsyncSession):
    """Ensures base competitions, season, teams, fixtures, and squad players exist in test database."""
    # 1. Competition
    comp = Competition(
        code="ISL",
        name="Indian Super League",
        country="India",
        federation="AIFF",
    )
    db_session.add(comp)
    await db_session.flush()

    # 2. Season 2026-27
    season = Season(
        competition_id=comp.id,
        name="2026–27",
        slug="isl-2026-27",
        is_current=True,
        is_completed=False,
    )
    db_session.add(season)
    await db_session.flush()

    # 3. Teams
    teams_data = [
        ("Chennaiyin FC", "CFC", "chennaiyin-fc"),
        ("FC Goa", "FCG", "fc-goa"),
        ("Bengaluru FC", "BFC", "bengaluru-fc"),
        ("Mohun Bagan SG", "MBSG", "mohun-bagan-sg"),
        ("Kerala Blasters FC", "KBFC", "kerala-blasters-fc"),
        ("East Bengal FC", "EBFC", "east-bengal-fc"),
        ("Mumbai City FC", "MCFC", "mumbai-city-fc"),
        ("Punjab FC", "PFC", "punjab-fc"),
        ("NorthEast United FC", "NEUFC", "northeast-united-fc"),
        ("Odisha FC", "OFC", "odisha-fc"),
        ("Churchill Brothers", "CBFC", "churchill-brothers"),
        ("Inter Kashi", "IKFC", "inter-kashi"),
        ("Sporting Club Delhi", "SCD", "sporting-club-delhi"),
    ]
    for name, short, slug in teams_data:
        db_session.add(Team(name=name, short_name=short, slug=slug))
    await db_session.flush()

    # 4. Import official 24 fixtures
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src",
        "marina",
        "data",
    )
    fix_service = FixtureService(db_session)
    fix_path = os.path.join(data_dir, "chennaiyin_fc_2026_27_fixtures.json")
    with open(fix_path, "r", encoding="utf-8") as f:
        fix_records = fix_service.parse_raw_fixtures(f.read())
    await fix_service.import_fixtures(fix_records, season_id=season.id)

    # 5. Import official 26-player squad
    cfc = (await db_session.execute(select(Team).where(Team.short_name == "CFC"))).scalars().first()
    squad_service = SquadSyncService(db_session)
    squad_path = os.path.join(data_dir, "chennaiyin_fc_2026_27_squad.json")
    with open(squad_path, "r", encoding="utf-8") as f:
        squad_records = squad_service.parse_raw_records(f.read(), format_hint="json")
    await squad_service.synchronize_squad(
        team_id=cfc.id,
        season_id=season.id,
        incoming_records=squad_records,
    )
    await db_session.commit()

    # 6. Ingest base completed matches
    ingestion_service = MatchIngestionService(db_session)
    await ingestion_service.ingest_completed_matches()
    await db_session.commit()


@pytest.mark.asyncio
async def test_historical_lineup_import_execution(db_session: AsyncSession):
    """Validates transactional import of historical lineups for all 5 matches."""
    service = LineupImportService(db_session)
    result = await service.import_historical_lineups()

    assert result["status"] == "SUCCESS"
    assert len(result["imported_match_ids"]) == 5
    assert result["duplicate_records_detected"] == 0
    assert len(result["player_id_matching_failures"]) == 0

    # Verify exactly 11 starters for each match in match_lineups
    for mw, count in result["starting_xi_counts"].items():
        assert count == 11

    # Verify substitutions counts
    assert result["substitution_counts"]["Match #1"] == 5
    assert result["substitution_counts"]["Match #2"] == 5
    assert result["substitution_counts"]["Match #3"] == 5
    assert result["substitution_counts"]["Match #4"] == 4
    assert result["substitution_counts"]["Match #5"] == 5

    # Check match_lineups table count: exactly 55
    ml_stmt = select(MatchLineup)
    mls = (await db_session.execute(ml_stmt)).scalars().all()
    assert len(mls) == 55

    # Check match_substitutes table count: exactly 24
    ms_stmt = select(MatchSubstitute)
    mss = (await db_session.execute(ms_stmt)).scalars().all()
    assert len(mss) == 24
    assert all(sub.is_used is True for sub in mss)

    # Check lineups table: exactly 55 starters + 24 substitutes = 79
    lp_stmt = select(Lineup)
    lps = (await db_session.execute(lp_stmt)).scalars().all()
    starters = [l for l in lps if l.lineup_role == LineupRole.STARTER]
    substitutes = [l for l in lps if l.lineup_role == LineupRole.BENCH and l.is_substitute_in]
    assert len(starters) == 55
    assert len(substitutes) == 24


@pytest.mark.asyncio
async def test_substitution_events_and_metadata(db_session: AsyncSession):
    """Validates discrete substitution events and exact required raw_metadata format."""
    service = LineupImportService(db_session)
    await service.import_historical_lineups()

    sub_events_stmt = (
        select(MatchEvent)
        .where(MatchEvent.event_type == EventType.SUBSTITUTION)
        .order_by(MatchEvent.minute.asc())
    )
    events = (await db_session.execute(sub_events_stmt)).scalars().all()
    assert len(events) == 24

    for ev in events:
        assert ev.raw_metadata is not None
        meta = json.loads(ev.raw_metadata)
        assert meta["event_type"] == "substitution"
        assert "minute" in meta
        assert "player_in" in meta
        assert "player_out" in meta
        assert meta["team"] == "Chennaiyin FC"
        assert meta["source_verified"] is True
        assert ev.primary_player_id is not None
        assert ev.secondary_player_id is not None


@pytest.mark.asyncio
async def test_match_4_disciplinary_events(db_session: AsyncSession):
    """Validates yellow card, second yellow, and red card dismissal in Match 4."""
    service = LineupImportService(db_session)
    await service.import_historical_lineups()

    # Find Match 4
    m4_stmt = select(Match).where(Match.match_number == 4, Match.match_status == MatchStatus.FINISHED)
    m4 = (await db_session.execute(m4_stmt)).scalar_one()

    # Find Imanishimwe
    im_stmt = select(Player).where(Player.known_name == "Emmanuel Imanishimwe")
    im = (await db_session.execute(im_stmt)).scalar_one()

    events_stmt = (
        select(MatchEvent)
        .where(MatchEvent.match_id == m4.id, MatchEvent.primary_player_id == im.id)
        .order_by(MatchEvent.minute.asc(), MatchEvent.stoppage_minute.asc())
    )
    events = (await db_session.execute(events_stmt)).scalars().all()

    event_types = [e.event_type for e in events]
    assert EventType.YELLOW_CARD in event_types
    assert EventType.SECOND_YELLOW in event_types
    assert EventType.RED_CARD in event_types

    # Verify player match statistics reflects cards
    pms_stmt = select(PlayerMatchStatistic).where(
        PlayerMatchStatistic.match_id == m4.id,
        PlayerMatchStatistic.player_id == im.id,
    )
    stat = (await db_session.execute(pms_stmt)).scalar_one()
    assert stat.red_cards == 1
    assert stat.yellow_cards == 1


@pytest.mark.asyncio
async def test_lineup_import_idempotency(db_session: AsyncSession):
    """Verifies that re-running lineup import preserves identical record counts without duplication."""
    service = LineupImportService(db_session)
    res1 = await service.import_historical_lineups()
    res2 = await service.import_historical_lineups()

    assert res1["starting_xi_counts"] == res2["starting_xi_counts"]
    assert res1["substitution_counts"] == res2["substitution_counts"]
    assert res2["duplicate_records_detected"] == 0

    ml_count = len((await db_session.execute(select(MatchLineup))).scalars().all())
    ms_count = len((await db_session.execute(select(MatchSubstitute))).scalars().all())
    assert ml_count == 55
    assert ms_count == 24


@pytest.mark.asyncio
async def test_lineup_api_endpoints(client: AsyncClient, db_session: AsyncSession):
    """Validates starting-xi and substitutes REST endpoints."""
    service = LineupImportService(db_session)
    await service.import_historical_lineups()

    m1_stmt = select(Match).where(Match.match_number == 1, Match.match_status == MatchStatus.FINISHED)
    m1 = (await db_session.execute(m1_stmt)).scalar_one()

    # GET Starting XI
    res_xi = await client.get(f"/api/v1/matches/{m1.id}/starting-xi")
    assert res_xi.status_code == 200
    starters = res_xi.json()
    assert len(starters) == 11
    assert any(s["is_captain"] is True for s in starters)

    # GET Substitutes
    res_subs = await client.get(f"/api/v1/matches/{m1.id}/substitutes")
    assert res_subs.status_code == 200
    subs = res_subs.json()
    assert len(subs) == 5
    assert all(s["is_used"] is True for s in subs)
    assert all(s["replaced_player"] is not None for s in subs)
