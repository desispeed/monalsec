import os
import pytest
from click.testing import CliRunner
from aptsec.cli import cli

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "nmap_sample.xml")


@pytest.fixture
def runner_with_engagement(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("APTSEC_DB", db_path)
    runner = CliRunner()
    result = runner.invoke(cli, [
        "engagement", "create",
        "--name", "Test", "--target", "10.0.0.0/24", "--tester", "t",
    ])
    assert result.exit_code == 0, f"Fixture setup failed: {result.output}"
    return runner


def test_import_nmap(runner_with_engagement):
    result = runner_with_engagement.invoke(cli, [
        "import", "nmap", "--file", FIXTURE, "--engagement", "1",
    ])
    assert result.exit_code == 0
    assert "Imported" in result.output


def test_import_nmap_populates_findings(runner_with_engagement):
    import_result = runner_with_engagement.invoke(cli, [
        "import", "nmap", "--file", FIXTURE, "--engagement", "1",
    ])
    assert import_result.exit_code == 0, f"Import failed: {import_result.output}"
    result = runner_with_engagement.invoke(cli, ["finding", "list", "--engagement", "1"])
    assert "nmap" in result.output


def test_import_nmap_bad_file(runner_with_engagement):
    # click.Path(exists=True) rejects the non-existent file before the command body runs
    result = runner_with_engagement.invoke(cli, [
        "import", "nmap", "--file", "/nonexistent.xml", "--engagement", "1",
    ])
    assert result.exit_code != 0
