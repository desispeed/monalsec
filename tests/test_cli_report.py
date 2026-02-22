import os
import pytest
from click.testing import CliRunner
from aptsec.cli import cli

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "nmap_sample.xml")


@pytest.fixture
def runner_with_data(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("APTSEC_DB", db_path)
    runner = CliRunner()
    result = runner.invoke(cli, [
        "engagement", "create",
        "--name", "Acme", "--target", "acme.com", "--tester", "Alice",
    ])
    assert result.exit_code == 0, f"Fixture setup failed: {result.output}"
    result = runner.invoke(cli, ["import", "nmap", "--file", FIXTURE, "--engagement", "1"])
    assert result.exit_code == 0, f"Nmap import failed: {result.output}"
    return runner, tmp_path


def test_report_generates_pdf(runner_with_data):
    runner, tmp_path = runner_with_data
    output = str(tmp_path / "report.pdf")
    result = runner.invoke(cli, [
        "report", "generate", "--engagement", "1", "--output", output,
    ])
    assert result.exit_code == 0
    assert os.path.exists(output)
    assert "report.pdf" in result.output


def test_report_nonexistent_engagement(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("APTSEC_DB", db_path)
    runner = CliRunner()
    output = str(tmp_path / "report.pdf")
    result = runner.invoke(cli, [
        "report", "generate", "--engagement", "99", "--output", output,
    ])
    assert result.exit_code != 0
    assert not os.path.exists(output)
