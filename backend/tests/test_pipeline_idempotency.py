"""Automated Tests for Ingestion Pipeline Execution and Upsert Idempotency."""

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from marina.ingestion.archive.raw_storage import RawArchiveStorage
from marina.ingestion.pipeline.runner import IngestionPipelineRunner
from marina.models.match import Match, MatchEvent
from marina.models.player import Player, SquadRegistration
from marina.models.statistics import TeamMatchStatistic
from marina.models.team import Team


@pytest.mark.asyncio
async def test_pipeline_execution_and_idempotent_upsert(
    db_session: AsyncSession, tmp_path
):
    """Verify that running the ingestion pipeline twice results in identical row counts (idempotent)."""
    archive = RawArchiveStorage(base_dir=str(tmp_path / "raw_archive"))
    runner = IngestionPipelineRunner(db_session, archive_storage=archive, mock_mode=True)

    # --------------------------------------------------------------------------
    # FIRST INGESTION RUN
    # --------------------------------------------------------------------------
    squad_res_1 = await runner.ingest_squad(season_code="2026–27")
    assert squad_res_1["status"] == "COMPLETED"
    assert squad_res_1["records_imported"] >= 10

    fixtures_res_1 = await runner.ingest_fixtures(season_code="2026–27")
    assert fixtures_res_1["status"] == "COMPLETED"
    assert fixtures_res_1["records_imported"] >= 3

    results_res_1 = await runner.ingest_results(season_code="2026–27")
    assert results_res_1["status"] == "COMPLETED"
    assert results_res_1["records_imported"] >= 1

    await db_session.flush()

    # Capture initial database counts
    players_count_1 = (await db_session.execute(select(func.count(Player.id)))).scalar_one()
    squad_reg_count_1 = (await db_session.execute(select(func.count(SquadRegistration.id)))).scalar_one()
    matches_count_1 = (await db_session.execute(select(func.count(Match.id)))).scalar_one()
    events_count_1 = (await db_session.execute(select(func.count(MatchEvent.id)))).scalar_one()
    team_stats_count_1 = (await db_session.execute(select(func.count(TeamMatchStatistic.id)))).scalar_one()

    assert players_count_1 >= 10
    assert matches_count_1 >= 4  # 3 fixtures + 1 result
    assert events_count_1 == 8   # 8 goals from CFC 5-3 EBFC
    assert team_stats_count_1 == 2  # CFC and EBFC stats

    # Verify Chennaiyin FC 5-3 East Bengal match properties
    cfc_match_stmt = select(Match).where(Match.home_score == 5, Match.away_score == 3)
    cfc_match = (await db_session.execute(cfc_match_stmt)).scalars().first()
    assert cfc_match is not None
    assert cfc_match.match_status.value == "FINISHED"

    # Verify upcoming scheduled match properties
    sched_match_stmt = select(Match).where(Match.match_status == "SCHEDULED")
    sched_matches = (await db_session.execute(sched_match_stmt)).scalars().all()
    assert len(sched_matches) == 3
    for sm in sched_matches:
        assert sm.home_score is None  # Never fabricated!
        assert sm.away_score is None

    # --------------------------------------------------------------------------
    # SECOND INGESTION RUN (IDEMPOTENCY VERIFICATION)
    # --------------------------------------------------------------------------
    squad_res_2 = await runner.ingest_squad(season_code="2026–27")
    fixtures_res_2 = await runner.ingest_fixtures(season_code="2026–27")
    results_res_2 = await runner.ingest_results(season_code="2026–27")

    await db_session.flush()

    # Capture counts after second run
    players_count_2 = (await db_session.execute(select(func.count(Player.id)))).scalar_one()
    squad_reg_count_2 = (await db_session.execute(select(func.count(SquadRegistration.id)))).scalar_one()
    matches_count_2 = (await db_session.execute(select(func.count(Match.id)))).scalar_one()
    team_stats_count_2 = (await db_session.execute(select(func.count(TeamMatchStatistic.id)))).scalar_one()

    # ASSERT EXACT EQUALITY: No duplicates created!
    assert players_count_1 == players_count_2
    assert squad_reg_count_1 == squad_reg_count_2
    assert matches_count_1 == matches_count_2
    assert team_stats_count_1 == team_stats_count_2
