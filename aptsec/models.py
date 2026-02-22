import sqlite3
from typing import Optional


def create_engagement(conn: sqlite3.Connection, name: str, target: str, tester: str) -> int:
    cur = conn.execute(
        "INSERT INTO engagements (name, target, tester) VALUES (?, ?, ?)",
        (name, target, tester),
    )
    conn.commit()
    return cur.lastrowid


def get_engagement(conn: sqlite3.Connection, engagement_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM engagements WHERE id = ?", (engagement_id,)
    ).fetchone()


def list_engagements(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM engagements ORDER BY created_at DESC"
    ).fetchall()


def create_finding(
    conn: sqlite3.Connection, engagement_id: int, title: str, severity: str,
    category: str, description: str, evidence: str,
    remediation: str, tool_source: str, cvss_score: Optional[float] = None,
) -> int:
    cur = conn.execute(
        """INSERT INTO findings
           (engagement_id, title, severity, category, description,
            evidence, remediation, tool_source, cvss_score)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (engagement_id, title, severity, category, description,
         evidence, remediation, tool_source, cvss_score),
    )
    conn.commit()
    return cur.lastrowid


def get_finding(conn: sqlite3.Connection, finding_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM findings WHERE id = ?", (finding_id,)
    ).fetchone()


def list_findings(conn: sqlite3.Connection, engagement_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT * FROM findings WHERE engagement_id = ?
           ORDER BY CASE severity
             WHEN 'critical' THEN 1 WHEN 'high' THEN 2
             WHEN 'medium' THEN 3 WHEN 'low' THEN 4
             ELSE 5 END""",
        (engagement_id,),
    ).fetchall()


def delete_finding(conn: sqlite3.Connection, finding_id: int) -> None:
    conn.execute("DELETE FROM findings WHERE id = ?", (finding_id,))
    conn.commit()


def create_target(
    conn: sqlite3.Connection, engagement_id: int, host: str, port: int,
    protocol: str, service: str, state: str,
) -> int:
    cur = conn.execute(
        """INSERT INTO targets (engagement_id, host, port, protocol, service, state)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (engagement_id, host, port, protocol, service, state),
    )
    conn.commit()
    return cur.lastrowid


def list_targets(conn: sqlite3.Connection, engagement_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM targets WHERE engagement_id = ? ORDER BY host, port",
        (engagement_id,),
    ).fetchall()
