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


if __name__ == "__main__":
    cli()
