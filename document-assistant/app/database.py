"""SQLite connection handling using Python's built-in sqlite3 module."""
import sqlite3
from collections.abc import Iterator
from contextlib import closing

from app.config import get_database_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    filename       TEXT    NOT NULL,
    size_bytes     INTEGER NOT NULL,
    word_count     INTEGER NOT NULL,
    sentence_count INTEGER NOT NULL,
    content        TEXT    NOT NULL,
    uploaded_at    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
"""


def connect(path: str) -> sqlite3.Connection:
    # check_same_thread=False: FastAPI may use different worker threads for
    # one request. Each request still gets its own connection, so this is safe.
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # rows behave like dicts: row["filename"]
    return conn


def init_db(path: str) -> None:
    """Create the table if it does not exist. Never drops existing data."""
    with closing(connect(path)) as conn:
        conn.executescript(SCHEMA)


def get_db() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency: one connection per request, always closed."""
    conn = connect(get_database_path())
    try:
        yield conn
    finally:
        conn.close()
