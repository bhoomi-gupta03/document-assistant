"""All SQL lives here. Every query is parameterized (the ? placeholders),
so user input can never be executed as SQL."""
import sqlite3
from typing import Any

_METADATA_COLUMNS = "id, filename, size_bytes, word_count, sentence_count, uploaded_at"


def create_document(
    conn: sqlite3.Connection,
    *,
    filename: str,
    size_bytes: int,
    content: str,
    word_count: int,
    sentence_count: int,
) -> dict[str, Any]:
    cursor = conn.execute(
        "INSERT INTO documents (filename, size_bytes, word_count, sentence_count, content) "
        "VALUES (?, ?, ?, ?, ?)",
        (filename, size_bytes, word_count, sentence_count, content),
    )
    conn.commit()
    created = get_document(conn, cursor.lastrowid)
    assert created is not None
    return created


def get_document(conn: sqlite3.Connection, document_id: int) -> dict[str, Any] | None:
    row = conn.execute(
        f"SELECT {_METADATA_COLUMNS}, content FROM documents WHERE id = ?", (document_id,)
    ).fetchone()
    return dict(row) if row else None


def list_documents(conn: sqlite3.Connection, limit: int, offset: int) -> list[dict[str, Any]]:
    """Metadata only (no content), newest first."""
    rows = conn.execute(
        f"SELECT {_METADATA_COLUMNS} FROM documents ORDER BY id DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    return [dict(r) for r in rows]


def count_documents(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]


def get_all_documents(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """id, filename and content of every document (used by search and ask)."""
    rows = conn.execute("SELECT id, filename, content FROM documents ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def delete_document(conn: sqlite3.Connection, document_id: int) -> bool:
    cursor = conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    return cursor.rowcount > 0
