"""Command Line Interface for MARINA INTELLIGENCE Data Ingestion and Quality Auditing."""

import asyncio
import json
import sys
from pathlib import Path
import click

from marina.db.session import AsyncSessionLocal
from marina.ingestion.extractors.manual_files import ManualFileExtractor
from marina.ingestion.pipeline.quality import DataQualityAuditor
from marina.ingestion.pipeline.runner import IngestionPipelineRunner


@click.group()
def cli() -> None:
    """MARINA INTELLIGENCE: Football Data Acquisition and Ingestion CLI."""
    pass


@cli.command("import-fixtures")
@click.option("--season", default="2026–27", help="Target ISL season (default: 2026–27)")
@click.option("--mock/--live", default=False, help="Use mock extraction or live HTTP")
def import_fixtures_cmd(season: str, mock: bool) -> None:
    """Ingests official ISL scheduled match fixtures."""
    async def _run():
        async with AsyncSessionLocal() as session:
            runner = IngestionPipelineRunner(session, mock_mode=mock)
            result = await runner.ingest_fixtures(season_code=season)
            await session.commit()
            click.echo(click.style(f"Fixtures Ingested Successfully: {result['records_imported']} fixtures", fg="green"))
            click.echo(f"Archive: {result['archive_path']}")

    asyncio.run(_run())


@cli.command("import-results")
@click.option("--season", default="2026–27", help="Target ISL season (default: 2026–27)")
@click.option("--mock/--live", default=False, help="Use mock extraction or live HTTP")
def import_results_cmd(season: str, mock: bool) -> None:
    """Ingests completed match results, scorelines, and match events."""
    async def _run():
        async with AsyncSessionLocal() as session:
            runner = IngestionPipelineRunner(session, mock_mode=mock)
            result = await runner.ingest_results(season_code=season)
            await session.commit()
            click.echo(click.style(f"Match Results Ingested: {result['records_imported']} matches", fg="green"))
            click.echo(f"Batch ID: {result['batch_id']}")

    asyncio.run(_run())


@cli.command("import-squad")
@click.option("--season", default="2026–27", help="Target ISL season (default: 2026–27)")
@click.option("--mock/--live", default=False, help="Use mock extraction or live HTTP")
def import_squad_cmd(season: str, mock: bool) -> None:
    """Ingests official Chennaiyin FC squad roster and player profiles."""
    async def _run():
        async with AsyncSessionLocal() as session:
            runner = IngestionPipelineRunner(session, mock_mode=mock)
            result = await runner.ingest_squad(season_code=season)
            await session.commit()
            click.echo(click.style(f"Squad Ingested: {result['records_imported']} players registered", fg="green"))
            click.echo(f"Archive: {result['archive_path']}")

    asyncio.run(_run())


@cli.command("import-file")
@click.option("--file", "file_path", required=True, type=click.Path(exists=True), help="Path to CSV or JSON file")
@click.option("--entity", "entity_type", required=True, type=click.Choice(["FIXTURES", "SQUAD", "STATISTICS"]), help="Data entity type")
def import_file_cmd(file_path: str, entity_type: str) -> None:
    """Ingests manually uploaded CSV or JSON football data."""
    extractor = ManualFileExtractor()
    parsed = extractor.parse_file(file_path, entity_type)
    click.echo(click.style(f"Loaded file {file_path} with {len(parsed['payload'])} items.", fg="cyan"))


@cli.command("ingest-all")
@click.option("--season", default="2026–27", help="Target ISL season (default: 2026–27)")
@click.option("--mock/--live", default=False, help="Use mock extraction or live HTTP")
def ingest_all_cmd(season: str, mock: bool) -> None:
    """Executes the complete multi-source ingestion pipeline."""
    async def _run():
        async with AsyncSessionLocal() as session:
            runner = IngestionPipelineRunner(session, mock_mode=mock)
            click.echo(click.style(f"Starting Full Ingestion for Season {season}...", fg="yellow"))

            squad_res = await runner.ingest_squad(season_code=season)
            click.echo(f"Squad: {squad_res['records_imported']} players")

            fixtures_res = await runner.ingest_fixtures(season_code=season)
            click.echo(f"Fixtures: {fixtures_res['records_imported']} fixtures")

            results_res = await runner.ingest_results(season_code=season)
            click.echo(f"Results: {results_res['records_imported']} completed matches")

            await session.commit()
            click.echo(click.style("Full Ingestion Pipeline Completed Successfully!", fg="green", bold=True))

    asyncio.run(_run())


@cli.command("quality-report")
@click.option("--output", "output_path", default=None, help="Optional output path for markdown report")
def quality_report_cmd(output_path: str | None) -> None:
    """Generates an automated data quality and integrity report."""
    async def _run():
        async with AsyncSessionLocal() as session:
            auditor = DataQualityAuditor(session)
            report = await auditor.generate_quality_report()
            md = auditor.format_markdown_report(report)

            click.echo(md)
            if output_path:
                Path(output_path).write_text(md, encoding="utf-8")
                click.echo(click.style(f"\nReport written to {output_path}", fg="green"))

    asyncio.run(_run())


@cli.command("sync-squad")
@click.option("--file", "file_path", default=None, help="Optional path to custom CSV/JSON squad file")
@click.option("--confirm/--preview", default=True, help="Execute commit or preview only")
def sync_squad_cmd(file_path: str | None, confirm: bool) -> None:
    """Synchronizes Chennaiyin FC 2026-27 active squad roster with database."""
    async def _run():
        async with AsyncSessionLocal() as session:
            from marina.models.competition import Season
            from marina.models.team import Team
            from marina.services.squad_sync_service import SquadSyncService
            from sqlalchemy import select

            cfc = (await session.execute(select(Team).where(Team.slug == "chennaiyin-fc"))).scalars().first()
            season = (await session.execute(select(Season).where(Season.slug.ilike("%2026-27%")))).scalars().first()
            if not cfc or not season:
                click.echo(click.style("Chennaiyin FC or 2026-27 season not found.", fg="red"))
                return

            service = SquadSyncService(session)
            if file_path:
                content = Path(file_path).read_text(encoding="utf-8")
                records = service.parse_raw_records(content)
            else:
                data_path = Path(__file__).parent / "data" / "chennaiyin_fc_2026_27_squad.csv"
                records = service.parse_raw_records(data_path.read_text(encoding="utf-8"))

            if not confirm:
                preview = await service.preview_squad_import(cfc.id, season.id, records)
                click.echo(click.style(f"Preview: {preview['total_incoming']} incoming, {len(preview['new_players'])} new, {len(preview['leaving_players'])} leaving", fg="yellow"))
            else:
                res = await service.synchronize_squad(cfc.id, season.id, records, confirmed=True)
                click.echo(click.style(res["message"], fg="green", bold=True))

    asyncio.run(_run())


@cli.command("import-fixtures")
@click.option("--file", "file_path", default=None, help="Optional path to custom CSV/JSON fixture file")
def import_fixtures_cmd(file_path: str | None) -> None:
    """Imports or updates the 24 Chennaiyin FC 2026-27 ISL fixtures idempotently."""
    async def _run():
        async with AsyncSessionLocal() as session:
            from marina.services.fixture_service import FixtureService
            service = FixtureService(session)

            if file_path:
                content = Path(file_path).read_text(encoding="utf-8")
                hint = "json" if file_path.endswith(".json") else "csv"
                records = service.parse_raw_fixtures(content, format_hint=hint)
            else:
                data_path = Path(__file__).parent / "data" / "chennaiyin_fc_2026_27_fixtures.json"
                records = service.parse_raw_fixtures(data_path.read_text(encoding="utf-8"), format_hint="json")

            click.echo(click.style(f"Importing {len(records)} fixtures for Chennaiyin FC...", fg="yellow"))
            res = await service.import_fixtures(records)
            await session.commit()
            click.echo(click.style(res["message"], fg="green", bold=True))
            click.echo(f"Published: {res['published_count']} | Provisional: {res['provisional_count']} | Discrepancies: {res['discrepancies_flagged']}")

    asyncio.run(_run())


@cli.command("sync-completed-matches")
def sync_completed_matches_cmd() -> None:
    """Ingests and synchronizes the last 5 completed ISL 2026-27 fixtures for Chennaiyin FC."""
    async def _run():
        async with AsyncSessionLocal() as session:
            from marina.services.match_ingestion_service import MatchIngestionService
            service = MatchIngestionService(session)
            click.echo(click.style("Synchronizing 5 completed matches with ground-truth provider metrics...", fg="yellow"))
            res = await service.ingest_completed_matches()
            click.echo(click.style(f"Successfully synchronized {res['matches_synced']} completed matches!", fg="green", bold=True))
            click.echo(f"Records Updated: {res['records_updated']} | Discrepancies Flagged: {res['discrepancies_flagged']} | Duration: {res['duration_ms']} ms")

    asyncio.run(_run())


@cli.command("import-historical-lineups")
def import_historical_lineups_cmd() -> None:
    """Imports verified historical lineups, formations, and substitutions for the first 5 ISL 2026-27 matches."""
    async def _run():
        async with AsyncSessionLocal() as session:
            from marina.services.lineup_import_service import LineupImportService
            service = LineupImportService(session)
            click.echo(click.style("Importing verified Starting XIs, formations, and substitutions...", fg="yellow"))
            res = await service.import_historical_lineups()
            click.echo(click.style("Lineup Import Completed Successfully!", fg="green", bold=True))
            click.echo(f"Imported Match IDs: {res['imported_match_ids']}")
            click.echo(f"Starting XI Counts: {res['starting_xi_counts']}")
            click.echo(f"Substitution Counts: {res['substitution_counts']}")
            click.echo(f"Duplicate Records: {res['duplicate_records_detected']}")
            click.echo(f"Player Matching Failures: {len(res['player_id_matching_failures'])}")

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
