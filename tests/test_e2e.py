import os
import pytest
from click.testing import CliRunner
from aptsec.cli import cli

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "nmap_sample.xml")


def test_full_workflow(tmp_path, monkeypatch):
    """Full engagement workflow: create → import → add manual finding → report."""
    monkeypatch.setenv("APTSEC_DB", str(tmp_path / "e2e.db"))
    runner = CliRunner()
    output_pdf = str(tmp_path / "final_report.pdf")

    # 1. Create engagement
    r = runner.invoke(cli, [
        "engagement", "create",
        "--name", "E2E Corp", "--target", "192.168.1.0/24", "--tester", "Tester",
    ])
    assert r.exit_code == 0

    # 2. Import nmap results
    r = runner.invoke(cli, ["import", "nmap", "--file", FIXTURE, "--engagement", "1"])
    assert r.exit_code == 0

    # 3. Add a manual finding
    r = runner.invoke(cli, [
        "finding", "add",
        "--engagement", "1",
        "--title", "Weak password policy",
        "--severity", "high",
        "--category", "Web",
        "--description", "No lockout after failed attempts",
        "--remediation", "Implement account lockout",
    ])
    assert r.exit_code == 0

    # 4. List findings — should contain both nmap and manual
    r = runner.invoke(cli, ["finding", "list", "--engagement", "1"])
    assert "nmap" in r.output
    assert "manual" in r.output

    # 5. Generate PDF
    r = runner.invoke(cli, [
        "report", "generate", "--engagement", "1", "--output", output_pdf,
    ])
    assert r.exit_code == 0
    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 4000  # confirms non-empty multi-page PDF
