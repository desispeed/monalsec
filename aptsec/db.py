import sqlite3
import os

DEFAULT_DB_PATH = os.path.expanduser("~/aptsec.db")


def get_connection(path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS engagements (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            target    TEXT    NOT NULL,
            tester    TEXT    NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS findings (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            engagement_id INTEGER NOT NULL REFERENCES engagements(id),
            title         TEXT    NOT NULL,
            severity      TEXT    NOT NULL CHECK(severity IN ('critical','high','medium','low','info')),
            category      TEXT    NOT NULL DEFAULT 'Network',
            description   TEXT    NOT NULL DEFAULT '',
            evidence      TEXT    NOT NULL DEFAULT '',
            remediation   TEXT    NOT NULL DEFAULT '',
            tool_source   TEXT    NOT NULL DEFAULT 'manual',
            cvss_score    REAL,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS targets (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            engagement_id INTEGER NOT NULL REFERENCES engagements(id),
            host          TEXT    NOT NULL,
            port          INTEGER,
            protocol      TEXT    NOT NULL DEFAULT 'tcp',
            service       TEXT    NOT NULL DEFAULT '',
            state         TEXT    NOT NULL DEFAULT 'open'
        );
    """)
    conn.commit()
