"""Automated Tests for Ingestion CLI Commands."""

from click.testing import CliRunner
from marina.cli import cli


def test_cli_help():
    """Verify that CLI help displays all commands."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "import-fixtures" in result.output
    assert "import-results" in result.output
    assert "import-squad" in result.output
    assert "import-file" in result.output
    assert "ingest-all" in result.output
    assert "quality-report" in result.output


def test_cli_import_file_csv(tmp_path):
    """Verify that import-file CLI command parses CSV file properly."""
    csv_file = tmp_path / "fixtures_test.csv"
    csv_file.write_text(
        "home_team,away_team,scheduled_kickoff\n"
        "Chennaiyin FC,Kerala Blasters FC,2026-11-28 19:30:00\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["import-file", "--file", str(csv_file), "--entity", "FIXTURES"])
    assert result.exit_code == 0
    assert "Loaded file" in result.output
