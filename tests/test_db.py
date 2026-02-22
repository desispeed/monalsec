import sqlite3
import tempfile
import os
import pytest
from aptsec.db import get_connection, init_db


@pytest.fixture
def tmp_db(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = get_connection(db_path)
    init_db(conn)
    yield conn
    conn.close()


def test_init_creates_engagements_table(tmp_db):
    cursor = tmp_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='engagements'"
    )
    assert cursor.fetchone() is not None


def test_init_creates_findings_table(tmp_db):
    cursor = tmp_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='findings'"
    )
    assert cursor.fetchone() is not None


def test_init_creates_targets_table(tmp_db):
    cursor = tmp_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='targets'"
    )
    assert cursor.fetchone() is not None


def test_init_is_idempotent(tmp_db):
    # Running init_db twice should not raise
    init_db(tmp_db)
