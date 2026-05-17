"""
memory_bank.py — SQLite knowledge store.
Implements knowledge + tags tables from Knowledge_Engine_Schema_v1.md.
DB path: data/knowledge_engine.db
"""
import sqlite3
import uuid
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "knowledge_engine.db"


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id            TEXT PRIMARY KEY,
            created_at    DATETIME NOT NULL,
            updated_at    DATETIME NOT NULL,
            project       TEXT     NOT NULL DEFAULT '',
            source_type   TEXT     NOT NULL DEFAULT 'manual',
            source_url    TEXT,
            title         TEXT     NOT NULL DEFAULT '',
            content       TEXT     NOT NULL DEFAULT '',
            quality_score REAL,
            status        TEXT     NOT NULL DEFAULT 'active',
            parent_id     TEXT,
            metadata      TEXT     NOT NULL DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS tags (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            knowledge_id TEXT    NOT NULL,
            tag          TEXT    NOT NULL,
            FOREIGN KEY (knowledge_id) REFERENCES knowledge(id)
        );
        CREATE INDEX IF NOT EXISTS idx_tags_kid ON tags(knowledge_id);
        CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
    """)
    conn.commit()


def store(entry: dict) -> str:
    """Store a knowledge entry. Returns the entry ID.

    Recognised keys: id, title, content, project, source_type, source_url,
                     quality_score, status, parent_id, metadata (dict or JSON str),
                     tags (list of str), created_at.
    """
    conn = _connect()
    _init_db(conn)
    now  = datetime.utcnow().isoformat()
    kid  = entry.get("id") or str(uuid.uuid4())
    tags = entry.get("tags") or []
    meta = entry.get("metadata", {})
    if isinstance(meta, dict):
        meta = json.dumps(meta)
    conn.execute(
        """INSERT OR REPLACE INTO knowledge
           (id, created_at, updated_at, project, source_type, source_url,
            title, content, quality_score, status, parent_id, metadata)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            kid,
            entry.get("created_at", now),
            now,
            entry.get("project", ""),
            entry.get("source_type", "manual"),
            entry.get("source_url"),
            entry.get("title", ""),
            entry.get("content", ""),
            entry.get("quality_score"),
            entry.get("status", "active"),
            entry.get("parent_id"),
            meta,
        ),
    )
    if tags:
        conn.execute("DELETE FROM tags WHERE knowledge_id = ?", (kid,))
        conn.executemany(
            "INSERT INTO tags (knowledge_id, tag) VALUES (?, ?)",
            [(kid, t) for t in tags],
        )
    conn.commit()
    conn.close()
    return kid


def get(entry_id: str) -> dict | None:
    """Return a knowledge entry dict (with 'tags' list) or None if not found."""
    conn = _connect()
    _init_db(conn)
    row = conn.execute(
        "SELECT * FROM knowledge WHERE id = ?", (entry_id,)
    ).fetchone()
    if not row:
        conn.close()
        return None
    result = dict(row)
    result["tags"] = [
        r["tag"] for r in conn.execute(
            "SELECT tag FROM tags WHERE knowledge_id = ?", (entry_id,)
        ).fetchall()
    ]
    conn.close()
    return result


def search_by_tag(tag: str) -> list[dict]:
    """Return all active knowledge entries that carry the given tag."""
    conn = _connect()
    _init_db(conn)
    rows = conn.execute(
        """SELECT k.* FROM knowledge k
           JOIN tags t ON t.knowledge_id = k.id
           WHERE t.tag = ?
           ORDER BY k.created_at DESC""",
        (tag,),
    ).fetchall()
    results = []
    for row in rows:
        entry = dict(row)
        entry["tags"] = [
            r["tag"] for r in conn.execute(
                "SELECT tag FROM tags WHERE knowledge_id = ?", (entry["id"],)
            ).fetchall()
        ]
        results.append(entry)
    conn.close()
    return results


def recent(n: int = 10) -> list[dict]:
    """Return the n most recently created knowledge entries."""
    conn = _connect()
    _init_db(conn)
    rows = conn.execute(
        "SELECT * FROM knowledge ORDER BY created_at DESC LIMIT ?", (n,)
    ).fetchall()
    results = []
    for row in rows:
        entry = dict(row)
        entry["tags"] = [
            r["tag"] for r in conn.execute(
                "SELECT tag FROM tags WHERE knowledge_id = ?", (entry["id"],)
            ).fetchall()
        ]
        results.append(entry)
    conn.close()
    return results


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("memory_bank.py self-test")
    print("=" * 40)

    test_id = store({
        "title":       "Self-test entry",
        "content":     "Test content inserted by memory_bank self-test.",
        "project":     "_selftest",
        "source_type": "manual",
        "tags":        ["_selftest", "test"],
    })
    print(f"store()  OK: {test_id}")

    entry = get(test_id)
    assert entry is not None,                    "get() returned None"
    assert entry["title"] == "Self-test entry",  "title mismatch"
    assert "_selftest" in entry["tags"],         "tag missing"
    print(f"get()    OK: {entry['title']!r}  tags={entry['tags']}")

    results = search_by_tag("_selftest")
    assert any(r["id"] == test_id for r in results), "search_by_tag missed the entry"
    print(f"search_by_tag('_selftest')  OK: {len(results)} result(s)")

    r = recent(5)
    assert any(e["id"] == test_id for e in r), "recent() missed the entry"
    print(f"recent(5)  OK: {len(r)} result(s)")

    print("=" * 40)
    print(f"All checks passed. DB: {DB_PATH}")
