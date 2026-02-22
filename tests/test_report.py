import os
import pytest
from aptsec.db import get_connection, init_db
from aptsec.models import create_engagement, create_finding, create_target
from aptsec.report.generator import generate_pdf


@pytest.fixture
def engagement_db(tmp_path):
    conn = get_connection(str(tmp_path / "test.db"))
    init_db(conn)
    eid = create_engagement(conn, name="Acme Corp", target="acme.com", tester="Alice")
    create_finding(conn, engagement_id=eid, title="Open SSH", severity="info",
                   category="Network", description="SSH open on 22",
                   evidence="nmap output", remediation="Restrict to known IPs",
                   tool_source="nmap")
    create_finding(conn, engagement_id=eid, title="SQLi in login", severity="critical",
                   category="Web", description="Union-based injection",
                   evidence="payload: ' OR 1=1--", remediation="Use parameterized queries",
                   tool_source="manual", cvss_score=9.8)
    create_target(conn, engagement_id=eid, host="10.0.0.1", port=22,
                  protocol="tcp", service="ssh", state="open")
    return conn, eid


def test_generate_pdf_creates_file(engagement_db, tmp_path):
    conn, eid = engagement_db
    output = str(tmp_path / "report.pdf")
    generate_pdf(conn, engagement_id=eid, output_path=output)
    assert os.path.exists(output)
    assert os.path.getsize(output) > 1000  # not empty


def test_generate_pdf_nonexistent_engagement(tmp_path):
    conn = get_connection(str(tmp_path / "empty.db"))
    init_db(conn)
    with pytest.raises(ValueError, match="Engagement"):
        generate_pdf(conn, engagement_id=999, output_path="/tmp/x.pdf")
