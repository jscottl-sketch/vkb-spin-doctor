"""
memory_bank.py — SQLite knowledge store.
Implements knowledge + tags tables from Knowledge_Engine_Schema_v1.md.
Phase B: solution_log table — search_solution, search_failures, store_solution.
Phase C: source_reputation table — update_source, get_top_sources, get_blocked_sources.
Phase D: TAGS constant, extended solution_log columns.
DB path: data/knowledge_engine.db
"""
import sqlite3
import uuid
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "knowledge_engine.db"

# Phase D — tag vocabulary
TAGS = [
    "usb", "steam", "config_file", "spin", "bindings",
    "registry", "companion_software", "polling_rate", "axis",
    "overlay", "launch_order", "firmware", "driver", "power",
    "war_thunder", "elite_dangerous", "star_citizen", "dcs",
    "joystick", "wheel", "pedals", "mouse", "keyboard",
]


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

        CREATE TABLE IF NOT EXISTS solution_log (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            problem        TEXT    NOT NULL,
            approach       TEXT    NOT NULL,
            worked         INTEGER NOT NULL DEFAULT 0,
            failure_reason TEXT,
            ai_score       REAL    NOT NULL DEFAULT 0.0,
            created_at     TEXT    NOT NULL,
            tags           TEXT,
            cost_tokens    INTEGER,
            iterations     INTEGER,
            game           TEXT,
            hardware       TEXT,
            verified_at    TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_sol_problem ON solution_log(problem);

        CREATE TABLE IF NOT EXISTS source_reputation (
            domain     TEXT PRIMARY KEY,
            topic_tags TEXT    NOT NULL DEFAULT '',
            times_used INTEGER NOT NULL DEFAULT 0,
            avg_score  REAL    NOT NULL DEFAULT 0.0,
            last_used  TEXT    NOT NULL DEFAULT ''
        );
    """)
    conn.commit()
    _migrate_solution_log(conn)


def _migrate_solution_log(conn):
    """Add Phase D columns to solution_log for DBs created before Phase D."""
    new_cols = [
        ("tags",        "TEXT"),
        ("cost_tokens", "INTEGER"),
        ("iterations",  "INTEGER"),
        ("game",        "TEXT"),
        ("hardware",    "TEXT"),
        ("verified_at", "TEXT"),
    ]
    for col, typ in new_cols:
        try:
            conn.execute(f"ALTER TABLE solution_log ADD COLUMN {col} {typ}")
            conn.commit()
        except Exception:
            pass  # column already exists


# ── Phase B — solution log ────────────────────────────────────────────────────

def search_solution(problem: str) -> dict | None:
    """Return best past solution where worked=True, ordered by ai_score desc."""
    conn = _connect()
    _init_db(conn)
    row = conn.execute(
        """SELECT * FROM solution_log
           WHERE worked=1 AND problem=?
           ORDER BY ai_score DESC LIMIT 1""",
        (problem,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def search_failures(problem: str) -> list[str]:
    """Return all failure_reasons for failed attempts on this problem."""
    conn = _connect()
    _init_db(conn)
    rows = conn.execute(
        """SELECT failure_reason FROM solution_log
           WHERE worked=0 AND problem=? AND failure_reason IS NOT NULL""",
        (problem,),
    ).fetchall()
    conn.close()
    return [r["failure_reason"] for r in rows]


def store_solution(problem: str, approach: str, worked: bool,
                   failure_reason: str | None, ai_score: float,
                   tags: str = "", cost_tokens: int = 0,
                   iterations: int = 1, game: str = "unknown",
                   hardware: str = "vkb_nxt_evo") -> int:
    """Insert a new solution_log row. Returns the new row id."""
    conn = _connect()
    _init_db(conn)
    now = datetime.utcnow().isoformat()
    cur = conn.execute(
        """INSERT INTO solution_log
           (problem, approach, worked, failure_reason, ai_score, created_at,
            tags, cost_tokens, iterations, game, hardware, verified_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (problem, approach, 1 if worked else 0, failure_reason, ai_score, now,
         tags, cost_tokens, iterations, game, hardware, now),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


# ── Phase C — source reputation ───────────────────────────────────────────────

def update_source(domain: str, score: float) -> None:
    """Upsert source reputation: increment times_used, recalculate rolling avg_score."""
    conn = _connect()
    _init_db(conn)
    now = datetime.utcnow().isoformat()
    row = conn.execute(
        "SELECT times_used, avg_score FROM source_reputation WHERE domain=?",
        (domain,),
    ).fetchone()
    if row:
        new_count = row["times_used"] + 1
        new_avg   = round((row["avg_score"] * row["times_used"] + score) / new_count, 2)
        conn.execute(
            """UPDATE source_reputation
               SET times_used=?, avg_score=?, last_used=? WHERE domain=?""",
            (new_count, new_avg, now, domain),
        )
    else:
        conn.execute(
            """INSERT INTO source_reputation
               (domain, topic_tags, times_used, avg_score, last_used)
               VALUES (?, ?, ?, ?, ?)""",
            (domain, "", 1, round(score, 2), now),
        )
    conn.commit()
    conn.close()


def get_top_sources(min_score: float = 7.0) -> list[str]:
    """Return domains with avg_score >= min_score, ordered by avg_score desc."""
    conn = _connect()
    _init_db(conn)
    rows = conn.execute(
        """SELECT domain FROM source_reputation
           WHERE avg_score >= ? ORDER BY avg_score DESC""",
        (min_score,),
    ).fetchall()
    conn.close()
    return [r["domain"] for r in rows]


def get_blocked_sources(max_score: float = 3.0) -> list[str]:
    """Return domains with avg_score <= max_score."""
    conn = _connect()
    _init_db(conn)
    rows = conn.execute(
        "SELECT domain FROM source_reputation WHERE avg_score <= ?",
        (max_score,),
    ).fetchall()
    conn.close()
    return [r["domain"] for r in rows]


def infer_tags_from_keywords(text: str) -> str:
    """Keyword fallback: match text against TAGS list, return comma-separated matches."""
    text_lower = text.lower()
    matched = [tag for tag in TAGS if tag in text_lower][:5]
    return ",".join(matched)


# ── Original functions ────────────────────────────────────────────────────────

def store(entry: dict) -> str:
    """Store a knowledge entry. Returns the entry ID."""
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

    sid = store_solution("_test_problem", "test approach xyz", True, None, 8.5)
    print(f"store_solution()  OK: rowid={sid}")
    found = search_solution("_test_problem")
    assert found and found["ai_score"] == 8.5, "search_solution failed"
    print(f"search_solution()  OK: score={found['ai_score']}")

    update_source("example.com", 7.5)
    update_source("example.com", 8.5)
    top = get_top_sources(7.0)
    assert "example.com" in top, "get_top_sources failed"
    print(f"update_source / get_top_sources  OK: {top}")

    print("=" * 40)
    print(f"All checks passed. DB: {DB_PATH}")
