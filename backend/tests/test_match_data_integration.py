"""Tests for Complete Match Statistics Import, Analytics Engine, and Provenance Tracking."""

import os
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.common import MatchStatus
from marina.models.competition import Competition, Season
from marina.models.match import Match, MatchEvent, MatchPass, MatchShot
from marina.models.provenance import DataMetricVerification, DataSyncLog
from marina.models.team import Team
from marina.services.fixture_service import FixtureService
from marina.services.match_ingestion_service import MatchIngestionService
from marina.services.squad_sync_service import SquadSyncService


@pytest.fixture(autouse=True)
async def seed_integration_test_db(db_session: AsyncSession):
    """Seeds in-memory test database with competitions, season 2026-27, teams, official fixtures and squad."""
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

    # 6. Run Match Ingestion for the 5 matches
    ingestion_service = MatchIngestionService(db_session)
    await ingestion_service.ingest_completed_matches()


@pytest.mark.asyncio
async def test_completed_matches_record_and_scorelines(db_session: AsyncSession):
    matches = (
        await db_session.execute(
            select(Match).where(Match.match_number.in_([1, 2, 3, 4, 5])).order_by(Match.match_number)
        )
    ).scalars().all()

    assert len(matches) == 5
    for m in matches:
        assert m.match_status == MatchStatus.FINISHED
        assert m.home_score is not None
        assert m.away_score is not None
        assert m.referee is not None
        assert m.attendance is not None and m.attendance > 10000

    # Specific scores
    # Match 1: Goa 1-1 CFC
    assert matches[0].home_score == 1 and matches[0].away_score == 1
    # Match 2: Bengaluru 2-0 CFC
    assert matches[1].home_score == 2 and matches[1].away_score == 0
    # Match 3: MBSG 1-0 CFC
    assert matches[2].home_score == 1 and matches[2].away_score == 0
    # Match 4: CFC 0-0 KBFC
    assert matches[3].home_score == 0 and matches[3].away_score == 0
    # Match 5: CFC 5-3 EBFC
    assert matches[4].home_score == 5 and matches[4].away_score == 3


@pytest.mark.asyncio
async def test_season_overview_aggregate_kpis(client: AsyncClient):
    res = await client.get("/api/v1/season/overview")
    assert res.status_code == 200
    data = res.json()

    assert data["matches_played"] == 5
    assert data["matches_remaining"] == 19
    assert data["wins"] == 1
    assert data["draws"] == 2
    assert data["losses"] == 2
    assert data["points"] == 5
    assert data["goals_scored"] == 6
    assert data["goals_conceded"] == 7
    assert data["goal_difference"] == -1
    assert data["recent_form"] == ["D", "L", "L", "D", "W"]
    assert data["clean_sheets"] == 1


@pytest.mark.asyncio
async def test_top_scorers_calculation(client: AsyncClient):
    res = await client.get("/api/v1/season/top-scorers")
    assert res.status_code == 200
    scorers = res.json()

    assert len(scorers) >= 3
    # Irfan Yadwad: 3 goals (1 vs Goa, 2 vs East Bengal), 1 assist
    yadwad = next((s for s in scorers if "Yadwad" in s["name"]), None)
    assert yadwad is not None
    assert yadwad["goals"] == 3
    assert yadwad["assists"] == 1

    # Brison Fernandes: 2 goals (both vs East Bengal)
    brison = next((s for s in scorers if "Brison" in s["name"]), None)
    assert brison is not None
    assert brison["goals"] == 2

    # Ramon Tanque: 1 goal (penalty vs East Bengal), 1 assist
    tanque = next((s for s in scorers if "Tanque" in s["name"]), None)
    assert tanque is not None
    assert tanque["goals"] == 1
    assert tanque["assists"] == 1


@pytest.mark.asyncio
async def test_east_bengal_match_events(client: AsyncClient, db_session: AsyncSession):
    match_5 = (
        await db_session.execute(select(Match).where(Match.match_number == 5))
    ).scalars().first()
    assert match_5 is not None

    res = await client.get(f"/api/v1/matches/{match_5.id}/events")
    assert res.status_code == 200
    events = res.json()

    goal_events = [e for e in events if "GOAL" in e["event_type"]]
    assert len(goal_events) == 8  # 5 CFC + 3 EBFC

    # Check key goal minutes
    minutes = [g["minute"] for g in goal_events]
    assert 4 in minutes
    assert 18 in minutes
    assert 29 in minutes
    assert 41 in minutes
    assert 47 in minutes
    assert 59 in minutes
    assert 67 in minutes
    assert 91 in minutes


@pytest.mark.asyncio
async def test_disciplinary_totals(db_session: AsyncSession):
    events = (
        await db_session.execute(
            select(MatchEvent).where(
                MatchEvent.event_type.in_(["YELLOW_CARD", "SECOND_YELLOW", "RED_CARD"])
            )
        )
    ).scalars().all()

    cfc = (await db_session.execute(select(Team).where(Team.short_name == "CFC"))).scalars().first()
    cfc_cards = [e for e in events if e.team_id == cfc.id]

    yellow_and_second_yellows = [e for e in cfc_cards if e.event_type.value in ["YELLOW_CARD", "SECOND_YELLOW"]]
    reds = [e for e in cfc_cards if e.event_type.value == "RED_CARD"]

    assert len(yellow_and_second_yellows) == 5
    assert len(reds) == 1


@pytest.mark.asyncio
async def test_spatial_coordinates_non_fabrication(db_session: AsyncSession):
    shots = (await db_session.execute(select(MatchShot))).scalars().all()
    assert len(shots) > 0
    for shot in shots:
        assert shot.x_coord is None
        assert shot.y_coord is None

    passes = (await db_session.execute(select(MatchPass))).scalars().all()
    assert len(passes) > 0
    for p in passes:
        assert p.start_x is None
        assert p.start_y is None
        assert p.end_x is None
        assert p.end_y is None


@pytest.mark.asyncio
async def test_sync_endpoints(client: AsyncClient):
    # Logs
    res_logs = await client.get("/api/v1/sync/logs")
    assert res_logs.status_code == 200
    logs = res_logs.json()
    assert len(logs) >= 1
    assert logs[0]["status"] == "SUCCESS"
    assert logs[0]["matches_synced"] == 5

    # Discrepancies
    res_disc = await client.get("/api/v1/sync/discrepancies?disputed_only=true")
    assert res_disc.status_code == 200
    discrepancies = res_disc.json()
    assert len(discrepancies) >= 3
    metric_names = [d["metric_name"] for d in discrepancies]
    assert "possession_pct" in metric_names
    assert "shots_total" in metric_names
    assert "shots_on_target" in metric_names
