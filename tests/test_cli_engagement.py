import pytest
from click.testing import CliRunner
from aptsec.cli import cli


@pytest.fixture
def runner(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("APTSEC_DB", db_path)
    return CliRunner()


def test_engagement_create(runner):
    result = runner.invoke(cli, [
        "engagement", "create",
        "--name", "Acme Corp",
        "--target", "acme.com",
        "--tester", "Alice",
    ])
    assert result.exit_code == 0
    assert "Created engagement" in result.output


def test_engagement_list_empty(runner):
    result = runner.invoke(cli, ["engagement", "list"])
    assert result.exit_code == 0
    assert "No engagements" in result.output


def test_engagement_list_shows_created(runner):
    runner.invoke(cli, [
        "engagement", "create",
        "--name", "Test Co", "--target", "test.co", "--tester", "Bob",
    ])
    result = runner.invoke(cli, ["engagement", "list"])
    assert "Test Co" in result.output
