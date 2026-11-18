"""Automated Tests for Data Quality Reporting and Markdown Generation."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from marina.ingestion.archive.raw_storage import RawArchiveStorage
from marina.ingestion.pipeline.quality import DataQualityAuditor
from marina.ingestion.pipeline.runner import IngestionPipelineRunner


@pytest.mark.asyncio
async def test_data_quality_report_generation(db_session: AsyncSession, tmp_path):
    """Verify that DataQualityAuditor produces a valid report and markdown document."""
    archive = RawArchiveStorage(base_dir=str(tmp_path / "raw_archive"))
    runner = IngestionPipelineRunner(db_session, archive_storage=archive, mock_mode=True)

    # Ingest data
    await runner.ingest_squad(season_code="2026–27")
    await runner.ingest_fixtures(season_code="2026–27")
    await runner.ingest_results(season_code="2026–27")
    await db_session.flush()

    # Generate audit report
    auditor = DataQualityAuditor(db_session)
    report = await auditor.generate_quality_report()

    assert report["overall_health"] == "PASSED"
    assert report["data_integrity"]["scheduled_score_integrity_pass"] is True
    assert report["data_integrity"]["invalid_scheduled_scores"] == 0
    assert report["entity_counts"]["players"] >= 10
    assert report["entity_counts"]["matches"] >= 4

    # Format Markdown
    md_output = auditor.format_markdown_report(report)
    assert "# MARINA INTELLIGENCE: Data Quality & Ingestion Audit Report" in md_output
    assert "**Overall Pipeline Health:** `PASSED`" in md_output
    assert "Chennaiyin FC" in md_output
