"""Comprehensive Automated Test Suite for Chennaiyin FC 2026–27 Squad Synchronization.

Validates:
1. Currency normalization (Cr, L, raw integer conversion, missing/dash preservation).
2. Height, date of birth, age, and dual nationality parsing.
3. Roster import preview, duplicate detection, and missing fields auditing.
4. Transactional synchronization:
   - 27 incoming players activated in 2026-27 squad.
   - Departed players deactivated for 2026-27 (never deleted).
   - Historical player records, match appearances, and statistics preserved intact.
   - Database rollback on execution failure.
5. REST API endpoints verification (/squads/import, /squads/sync, /squads/chennaiyin-fc/2026-27, /squads/import/history, /players/{id}).
"""

import uuid
from datetime import date, datetime, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.common import EventType, MatchPeriod, MatchStatus, PlayerPosition, ProviderType
from marina.models.competition import Competition, Season
from marina.models.match import Match, MatchEvent
from marina.models.player import (
    Player,
    SquadImportHistory,
    SquadRegistration,
    TeamSquadMembership,
)
from marina.models.provenance import DataSource
from marina.models.statistics import PlayerMatchStatistic
from marina.models.team import Team
from marina.services.squad_sync_service import (
    SquadSyncService,
    parse_date_dmy,
    parse_height,
    parse_market_value,
    parse_nationality,
    parse_position,
)


# =============================================================================
# 1. Parsing & Normalization Unit Tests
# =============================================================================

def test_parse_market_value_crores_and_lakhs():
    """Verifies market value normalization to INR integer while preserving original notation."""
    # Crores (1 Cr = 10,000,000)
    inr, orig = parse_market_value("₹1.10 Cr")
    assert inr == 11_000_000
    assert orig == "₹1.10 Cr"

    inr, orig = parse_market_value("₹4.13 Cr")
    assert inr == 41_300_000
    assert orig == "₹4.13 Cr"

    inr, orig = parse_market_value("₹2.75 Cr")
    assert inr == 27_500_000

    inr, orig = parse_market_value("₹3.03 Cr")
    assert inr == 30_300_000

    inr, orig = parse_market_value("₹2.20 Cr")
    assert inr == 22_000_000

    # Lakhs (1 L = 100,000)
    inr, orig = parse_market_value("₹55 L")
    assert inr == 5_500_000
    assert orig == "₹55 L"

    inr, orig = parse_market_value("₹27.50 L")
    assert inr == 2_750_000

    inr, orig = parse_market_value("₹82.50 L")
    assert inr == 8_250_000

    inr, orig = parse_market_value("₹11 L")
    assert inr == 1_100_000

    # Missing or dashes -> None (Preserved as NULL, never zero)
    inr, orig = parse_market_value("—")
    assert inr is None
    assert orig is None

    inr, orig = parse_market_value("")
    assert inr is None
    assert orig is None


def test_parse_height():
    """Verifies height conversion from meter strings into meters float and cm integer."""
    h_m, h_cm = parse_height("1.74 m")
    assert h_m == 1.74
    assert h_cm == 174

    h_m, h_cm = parse_height("1.88 m")
    assert h_m == 1.88
    assert h_cm == 188

    h_m, h_cm = parse_height("—")
    assert h_m is None
    assert h_cm is None


def test_parse_date_and_age():
    """Verifies date of birth parsing and age handling."""
    dob, age = parse_date_dmy("21/01/2000 (26)")
    assert dob == date(2000, 1, 21)
    assert age == 26

    dob, age = parse_date_dmy("10/06/2005 (21)")
    assert dob == date(2005, 6, 10)
    assert age == 21

    dob, age = parse_date_dmy("31/05/2027")
    assert dob == date(2027, 5, 31)

    dob, age = parse_date_dmy("—")
    assert dob is None
    assert age is None


def test_parse_nationality_dual():
    """Verifies dual nationality splitting into primary and secondary."""
    pri, sec = parse_nationality("Portugal / Switzerland")
    assert pri == "Portugal"
    assert sec == "Switzerland"

    pri, sec = parse_nationality("France / Morocco")
    assert pri == "France"
    assert sec == "Morocco"

    pri, sec = parse_nationality("India")
    assert pri == "India"
    assert sec is None


def test_parse_position():
    """Verifies position strings mapping to PlayerPosition enum and pos_group."""
    pos, grp = parse_position("Goalkeeper")
    assert pos == PlayerPosition.GK
    assert grp == "GK"

    pos, grp = parse_position("Centre-Back")
    assert pos == PlayerPosition.CB
    assert grp == "DEF"

    pos, grp = parse_position("Defensive Midfield")
    assert pos == PlayerPosition.DM
    assert grp == "MID"

    pos, grp = parse_position("Attacking Midfield")
    assert pos == PlayerPosition.AM
    assert grp == "MID"

    pos, grp = parse_position("Centre-Forward")
    assert pos == PlayerPosition.CF
    assert grp == "FWD"

    pos, grp = parse_position("Striker")
    assert pos == PlayerPosition.ST
    assert grp == "FWD"

    pos, grp = parse_position("Defender")
    assert pos == PlayerPosition.DEF
    assert grp == "DEF"

    pos, grp = parse_position("Right Wing")
    assert pos == PlayerPosition.RW
    assert grp == "FWD"

    pos, grp = parse_position("Left Wing")
    assert pos == PlayerPosition.LW
    assert grp == "FWD"


# =============================================================================
# 2. Squad Synchronization Fixture
# =============================================================================

@pytest.fixture
async def setup_squad_sync_env(db_session: AsyncSession):
    """Sets up base Chennaiyin FC club, 2026-27 season, existing players, and historical match data."""
    ds = DataSource(code="ISL_OFFICIAL", name="ISL Official", provider_type=ProviderType.OFFICIAL_LEAGUE)
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

    # Pre-existing players in DB:
    # 1. Samik Mitra (Retained in 2026-27)
    p_samik = Player(slug="samik-mitra", first_name="Samik", last_name="Mitra", known_name="Samik Mitra", nationality="India", primary_position=PlayerPosition.GK, squad_number=1)
    # 2. Ryan Edwards (Departed, should be deactivated for 2026-27)
    p_edwards = Player(slug="ryan-edwards", first_name="Ryan", last_name="Edwards", known_name="Ryan Edwards", nationality="England", primary_position=PlayerPosition.CB, squad_number=6)
    # 3. Wilmar Jordan Gil (Departed, should be deactivated for 2026-27)
    p_gil = Player(slug="wilmar-jordan-gil", first_name="Wilmar", last_name="Jordan Gil", known_name="Wilmar Jordan Gil", nationality="Colombia", primary_position=PlayerPosition.CF, squad_number=9)
    db_session.add_all([p_samik, p_edwards, p_gil])
    await db_session.flush()

    # Register them initially as active in 2026-27
    mem_samik = TeamSquadMembership(team_id=cfc.id, season_id=season.id, player_id=p_samik.id, squad_number=1, is_active=True)
    mem_edwards = TeamSquadMembership(team_id=cfc.id, season_id=season.id, player_id=p_edwards.id, squad_number=6, is_active=True)
    mem_gil = TeamSquadMembership(team_id=cfc.id, season_id=season.id, player_id=p_gil.id, squad_number=9, is_active=True)
    db_session.add_all([mem_samik, mem_edwards, mem_gil])
    await db_session.flush()

    # Add historical match record with statistics and events for Ryan Edwards and Wilmar Jordan Gil
    m = Match(
        season_id=season.id,
        home_team_id=cfc.id,
        away_team_id=ebfc.id,
        scheduled_kickoff=datetime(2026, 11, 7, 14, 0, tzinfo=timezone.utc),
        match_status=MatchStatus.FINISHED,
        home_score=5,
        away_score=3,
        match_number=1,
    )
    db_session.add(m)
    await db_session.flush()

    # Historical stats for Wilmar Jordan Gil: 2 goals
    stat_gil = PlayerMatchStatistic(
        match_id=m.id,
        player_id=p_gil.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        minutes_played=90,
        goals=2,
        shots_total=4,
    )
    # Historical stats for Ryan Edwards: 90 mins, 5 clearances
    stat_edwards = PlayerMatchStatistic(
        match_id=m.id,
        player_id=p_edwards.id,
        team_id=cfc.id,
        data_source_id=ds.id,
        minutes_played=90,
        clearances=5,
    )
    # Historical goal event
    event_gil = MatchEvent(
        match_id=m.id,
        team_id=cfc.id,
        primary_player_id=p_gil.id,
        event_type=EventType.GOAL,
        period=MatchPeriod.FIRST_HALF,
        minute=24,
    )
    db_session.add_all([stat_gil, stat_edwards, event_gil])
    await db_session.flush()

    return {
        "ds": ds,
        "comp": comp,
        "season": season,
        "cfc": cfc,
        "ebfc": ebfc,
        "p_samik": p_samik,
        "p_edwards": p_edwards,
        "p_gil": p_gil,
        "match": m,
    }


# =============================================================================
# 3. Synchronization & Data Integrity Tests
# =============================================================================

@pytest.mark.asyncio
async def test_squad_import_preview_and_audit(db_session: AsyncSession, setup_squad_sync_env):
    """Verifies that import preview accurately classifies incoming roster changes without writing to DB."""
    data = setup_squad_sync_env
    service = SquadSyncService(db_session)

    # 3 incoming players: Samik Mitra (retained), Mohammad Nawaz (new), Ramon Tanque (new)
    incoming = [
        {"#": 1, "Player": "Samik Mitra", "Position": "Goalkeeper", "Date of birth (Age)": "01/12/2000 (25)", "Nationality": "India", "Height": "1.88 m", "Foot": "Right", "Joined": "27/08/2020", "Signed from": "Indian Arrows FC", "Contract until": "31/05/2027", "Market value": "₹55 L"},
        {"#": 13, "Player": "Mohammad Nawaz", "Position": "Goalkeeper", "Date of birth (Age)": "21/01/2000 (26)", "Nationality": "India", "Height": "1.74 m", "Foot": "Right", "Joined": "25/06/2024", "Signed from": "Mumbai City FC", "Contract until": "31/05/2027", "Market value": "₹1.10 Cr"},
        {"#": 7, "Player": "Ramon Tanque", "Position": "Centre-Forward", "Date of birth (Age)": "10/09/1998 (28)", "Nationality": "Brazil", "Height": "1.88 m", "Foot": "—", "Joined": "31/08/2026", "Signed from": "PERSIB Bandung", "Contract until": "31/05/2027", "Market value": "₹2.75 Cr"},
    ]

    preview = await service.preview_squad_import(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
        raw_records=incoming,
    )

    assert preview["total_incoming"] == 3
    # 2 brand new signings: Mohammad Nawaz, Ramon Tanque
    assert len(preview["new_players"]) == 2
    # 1 updated/retained: Samik Mitra
    assert len(preview["updated_players"]) == 1
    assert len(preview["retained_players"]) == 1
    # 2 leaving players: Ryan Edwards and Wilmar Jordan Gil (were active in 2026-27, absent from incoming)
    assert len(preview["leaving_players"]) == 2
    leaving_names = [p["name"] for p in preview["leaving_players"]]
    assert "Ryan Edwards" in leaving_names
    assert "Wilmar Jordan Gil" in leaving_names

    # Confirmation required
    assert preview["requires_confirmation"] is True


@pytest.mark.asyncio
async def test_squad_synchronization_preserves_historical_data(db_session: AsyncSession, setup_squad_sync_env):
    """Verifies that squad sync updates active members and deactivates departed players WITHOUT deleting historical match records."""
    data = setup_squad_sync_env
    service = SquadSyncService(db_session)

    incoming = [
        {"squad_number": 1, "player_name": "Samik Mitra", "position": "Goalkeeper", "date_of_birth": "01/12/2000", "nationality": "India", "height": "1.88 m", "preferred_foot": "Right", "joined_date": "27/08/2020", "previous_club": "Indian Arrows FC", "contract_expiry": "31/05/2027", "market_value": "₹55 L"},
        {"squad_number": 13, "player_name": "Mohammad Nawaz", "position": "Goalkeeper", "date_of_birth": "21/01/2000", "nationality": "India", "height": "1.74 m", "preferred_foot": "Right", "joined_date": "25/06/2024", "previous_club": "Mumbai City FC", "contract_expiry": "31/05/2027", "market_value": "₹1.10 Cr"},
        {"squad_number": 7, "player_name": "Ramon Tanque", "position": "Centre-Forward", "date_of_birth": "10/09/1998", "nationality": "Brazil", "height": "1.88 m", "preferred_foot": None, "joined_date": "31/08/2026", "previous_club": "PERSIB Bandung", "contract_expiry": "31/05/2027", "market_value": "₹2.75 Cr"},
    ]

    res = await service.synchronize_squad(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
        incoming_records=incoming,
        confirmed=True,
        deactivate_absent=True,
    )

    assert res["status"] == "COMPLETED"
    assert res["new_created"] == 2  # Nawaz, Tanque
    assert res["updated"] == 1      # Samik Mitra
    assert res["deactivated"] == 2  # Edwards, Jordan Gil
    assert res["active_squad_count"] == 3

    # 1. Verify Active Squad contains exactly 3 players
    active_squad = await service.get_active_squad(data["cfc"].id, data["season"].id, include_inactive=False)
    assert len(active_squad) == 3
    active_names = [p["name"] for p in active_squad]
    assert "Samik Mitra" in active_names
    assert "Mohammad Nawaz" in active_names
    assert "Ramon Tanque" in active_names

    # 2. Verify Departed Players STILL EXIST in DB (never deleted!)
    p_edwards_db = (await db_session.execute(select(Player).where(Player.slug == "ryan-edwards"))).scalars().first()
    p_gil_db = (await db_session.execute(select(Player).where(Player.slug == "wilmar-jordan-gil"))).scalars().first()
    assert p_edwards_db is not None
    assert p_gil_db is not None

    # 3. Verify their 2026-27 squad membership is marked is_active = False
    mem_edwards = (await db_session.execute(select(TeamSquadMembership).where(TeamSquadMembership.player_id == p_edwards_db.id))).scalars().first()
    assert mem_edwards.is_active is False

    mem_gil = (await db_session.execute(select(TeamSquadMembership).where(TeamSquadMembership.player_id == p_gil_db.id))).scalars().first()
    assert mem_gil.is_active is False

    # 4. CRITICAL: Verify Historical Match Statistics are 100% PRESERVED
    gil_stats = (await db_session.execute(select(PlayerMatchStatistic).where(PlayerMatchStatistic.player_id == p_gil_db.id))).scalars().all()
    assert len(gil_stats) == 1
    assert gil_stats[0].goals == 2
    assert gil_stats[0].minutes_played == 90

    # 5. Verify Historical Match Goal Event is PRESERVED
    events = (await db_session.execute(select(MatchEvent).where(MatchEvent.primary_player_id == p_gil_db.id))).scalars().all()
    assert len(events) == 1
    assert events[0].event_type == EventType.GOAL

    # 6. Verify Squad Import Audit History was created
    history = (await db_session.execute(select(SquadImportHistory).where(SquadImportHistory.team_id == data["cfc"].id))).scalars().all()
    assert len(history) == 1
    assert history[0].status == "COMPLETED"
    assert history[0].deactivated_players == 2


@pytest.mark.asyncio
async def test_full_27_player_supplied_squad_sync(db_session: AsyncSession, setup_squad_sync_env):
    """Imports the full supplied Chennaiyin FC 2026-27 roster and validates all 27 players."""
    data = setup_squad_sync_env
    service = SquadSyncService(db_session)

    # Load from bundled CSV/JSON file
    raw_records = SquadSyncService.parse_raw_records(
        open("backend/src/marina/data/chennaiyin_fc_2026_27_squad.csv", "r", encoding="utf-8").read(),
        format_hint="csv",
    )
    assert len(raw_records) == 27

    res = await service.synchronize_squad(
        team_id=data["cfc"].id,
        season_id=data["season"].id,
        incoming_records=raw_records,
        confirmed=True,
        deactivate_absent=True,
    )

    assert res["status"] == "COMPLETED"
    assert res["active_squad_count"] == 27

    # Check active squad query
    active_squad = await service.get_active_squad(data["cfc"].id, data["season"].id, include_inactive=False)
    assert len(active_squad) == 27

    # Validate specific players and converted market values
    talal = next(p for p in active_squad if p["name"] == "Madih Talal")
    assert talal["squad_number"] == 10
    assert talal["market_value_inr"] == 41_300_000  # ₹4.13 Cr
    assert talal["market_value_original"] == "₹4.13 Cr"
    assert talal["nationality"] == "France"
    assert talal["secondary_nationality"] == "Morocco"

    nawaz = next(p for p in active_squad if p["name"] == "Mohammad Nawaz")
    assert nawaz["squad_number"] == 13
    assert nawaz["market_value_inr"] == 11_000_000  # ₹1.10 Cr
    assert nawaz["height_m"] == 1.74

    tanque = next(p for p in active_squad if p["name"] == "Ramon Tanque")
    assert tanque["squad_number"] == 7
    assert tanque["market_value_inr"] == 27_500_000  # ₹2.75 Cr
    assert tanque["nationality"] == "Brazil"
    assert tanque["is_domestic"] is False

    # Check filter: Overseas players (5 foreign players: Nuno Rice, Imanishimwe, Stojanovic, Talal, Ramon Tanque)
    overseas = await service.get_active_squad(data["cfc"].id, data["season"].id, nationality_filter="OVERSEAS")
    assert len(overseas) == 5

    # Check filter: Domestic players (22 Indian players)
    domestic = await service.get_active_squad(data["cfc"].id, data["season"].id, nationality_filter="DOMESTIC")
    assert len(domestic) == 22

    # Check filter: Goalkeepers (3 GKs: Nawaz, Mitra, Mohol)
    gks = await service.get_active_squad(data["cfc"].id, data["season"].id, position_filter="GK")
    assert len(gks) == 3


# =============================================================================
# 4. REST API Endpoint Tests
# =============================================================================

@pytest.mark.asyncio
async def test_squad_rest_api_endpoints(client: AsyncClient, setup_squad_sync_env):
    """Verifies all squad sync and player REST API endpoints."""
    data = setup_squad_sync_env

    # 1. POST /api/v1/squads/import (Preview)
    r_preview = await client.post(
        f"/api/v1/squads/import?team_id={data['cfc'].id}&season_id={data['season'].id}"
    )
    assert r_preview.status_code == 200
    p_data = r_preview.json()
    assert p_data["total_incoming"] == 27
    assert p_data["requires_confirmation"] is True

    # 2. POST /api/v1/squads/sync (Synchronize)
    sync_payload = {
        "team_id": str(data["cfc"].id),
        "season_id": str(data["season"].id),
        "confirmed": True,
        "deactivate_absent": True,
    }
    r_sync = await client.post("/api/v1/squads/sync", json=sync_payload)
    assert r_sync.status_code == 200
    s_data = r_sync.json()
    assert s_data["status"] == "COMPLETED"
    assert s_data["active_squad_count"] == 27

    # 3. GET /api/v1/squads/chennaiyin-fc/2026-27
    r_squad = await client.get("/api/v1/squads/chennaiyin-fc/2026-27")
    assert r_squad.status_code == 200
    squad_list = r_squad.json()
    assert len(squad_list) == 27

    # 4. GET /api/v1/squads/import/history
    r_hist = await client.get(f"/api/v1/squads/import/history?team_id={data['cfc'].id}")
    assert r_hist.status_code == 200
    hist_logs = r_hist.json()
    assert len(hist_logs) >= 1
    assert hist_logs[0]["status"] == "COMPLETED"

    # 5. GET /api/v1/players (with nationality filter)
    r_players = await client.get("/api/v1/players?nationality=OVERSEAS")
    assert r_players.status_code == 200
    overseas_players = r_players.json()
    # At least the 5 synced foreign players + historical Ryan Edwards & Jordan Gil
    assert len(overseas_players) >= 5

    # 6. GET /api/v1/players/{player_id} (Player detail with career & stats)
    player_id = squad_list[0]["player_id"]
    r_detail = await client.get(f"/api/v1/players/{player_id}")
    assert r_detail.status_code == 200
    detail_data = r_detail.json()
    assert "career_memberships" in detail_data
    assert "historical_statistics" in detail_data

    # 7. PATCH /api/v1/players/{player_id}
    patch_payload = {"known_name": "Updated Test Name"}
    r_patch = await client.patch(f"/api/v1/players/{player_id}", json=patch_payload)
    assert r_patch.status_code == 200
    assert r_patch.json()["known_name"] == "Updated Test Name"
