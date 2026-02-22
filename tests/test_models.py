import pytest
from aptsec.db import get_connection, init_db
from aptsec.models import (
    create_engagement, get_engagement, list_engagements,
    create_finding, list_findings, get_finding, delete_finding,
    create_target, list_targets,
)


@pytest.fixture
def db(tmp_path):
    conn = get_connection(str(tmp_path / "test.db"))
    init_db(conn)
    return conn


def test_create_and_get_engagement(db):
    eid = create_engagement(db, name="Acme", target="acme.com", tester="Alice")
    eng = get_engagement(db, eid)
    assert eng["name"] == "Acme"
    assert eng["target"] == "acme.com"
    assert eng["tester"] == "Alice"


def test_list_engagements(db):
    create_engagement(db, name="A", target="a.com", tester="t")
    create_engagement(db, name="B", target="b.com", tester="t")
    results = list_engagements(db)
    assert len(results) == 2


def test_create_and_list_findings(db):
    eid = create_engagement(db, name="X", target="x.com", tester="t")
    fid = create_finding(db, engagement_id=eid, title="SQLi", severity="high",
                         category="Web", description="Found in login",
                         evidence="curl output", remediation="Use parameterized queries",
                         tool_source="manual")
    findings = list_findings(db, eid)
    assert len(findings) == 1
    assert findings[0]["title"] == "SQLi"


def test_delete_finding(db):
    eid = create_engagement(db, name="X", target="x.com", tester="t")
    fid = create_finding(db, engagement_id=eid, title="XSS", severity="medium",
                         category="Web", description="", evidence="",
                         remediation="", tool_source="manual")
    delete_finding(db, fid)
    assert list_findings(db, eid) == []


def test_create_target(db):
    eid = create_engagement(db, name="X", target="x.com", tester="t")
    create_target(db, engagement_id=eid, host="10.0.0.1", port=22,
                  protocol="tcp", service="ssh", state="open")
    targets = list_targets(db, eid)
    assert len(targets) == 1
    assert targets[0]["service"] == "ssh"
