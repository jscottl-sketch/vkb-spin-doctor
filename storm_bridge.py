"""
storm_bridge.py — STORM (Selective Targeted Output Remove Merge) bridge.
Reads from local data files and writes unified storm_feed.json.
Functions: ingest_detective(), ingest_sesum(), ingest_screenshot(), get_feed(), clear_feed()
Also provides StormBridge class (HTTP-based) for backward compat with older callers.
"""

import datetime
import json
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORM_FEED = HERE / "data" / "storm_feed.json"
HEALTH_DB  = HERE / "data" / "health.db"
SESSION_LOGS = HERE / "session_logs"
SCREENSHOT_LOG = HERE / "data" / "screenshot_log.json"
MASTER_CHECKLIST = HERE / "data" / "master_checklist.json"

_MAX_ENTRIES = 500


def _now_iso() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _load_feed() -> dict:
    """Load storm_feed.json or return empty structure."""
    try:
        if STORM_FEED.exists():
            return json.loads(STORM_FEED.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"entries": [], "last_ingested": ""}


def _save_feed(data: dict) -> bool:
    """Atomic write + read-back verify."""
    try:
        STORM_FEED.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(STORM_FEED.parent), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        shutil.move(tmp, str(STORM_FEED))
        # Read-back verify
        verify = json.loads(STORM_FEED.read_text(encoding="utf-8"))
        return isinstance(verify.get("entries"), list)
    except Exception:
        return False


def _append(entries: list, new: list):
    """Append new entries, deduplicate by (source+description), cap at _MAX_ENTRIES."""
    seen = {(e.get("source", ""), e.get("description", "")) for e in entries}
    for item in new:
        key = (item.get("source", ""), item.get("description", ""))
        if key not in seen:
            entries.append(item)
            seen.add(key)
    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    del entries[_MAX_ENTRIES:]


def ingest_detective() -> int:
    """Read detective findings from data/health.db and append to storm_feed.json."""
    data = _load_feed()
    new_items = []
    try:
        if HEALTH_DB.exists():
            conn = sqlite3.connect(str(HEALTH_DB))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM findings WHERE status='open' ORDER BY found_at DESC LIMIT 100")
            rows = cur.fetchall()
            conn.close()
            for row in rows:
                new_items.append({
                    "source": "detective",
                    "category": "finding",
                    "timestamp": row["found_at"] if "found_at" in row.keys() else _now_iso(),
                    "description": row["description"] if "description" in row.keys() else str(dict(row)),
                    "severity": row["severity"] if "severity" in row.keys() else "info",
                    "resolved": False,
                })
    except Exception:
        pass
    _append(data.setdefault("entries", []), new_items)
    data["last_ingested"] = _now_iso()
    _save_feed(data)
    return len(new_items)


def ingest_sesum() -> int:
    """Read session log .md files from session_logs/ and append to storm_feed.json."""
    data = _load_feed()
    new_items = []
    try:
        if SESSION_LOGS.exists():
            for md_file in sorted(SESSION_LOGS.glob("*.md"))[-20:]:
                try:
                    text = md_file.read_text(encoding="utf-8", errors="replace")
                    new_items.append({
                        "source": "sesum",
                        "category": "session_log",
                        "timestamp": datetime.datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%Y-%m-%dT%H:%M:%S"),
                        "description": md_file.name + ": " + text[:120].replace("\n", " "),
                        "severity": "info",
                        "resolved": False,
                    })
                except Exception:
                    continue
    except Exception:
        pass
    _append(data.setdefault("entries", []), new_items)
    data["last_ingested"] = _now_iso()
    _save_feed(data)
    return len(new_items)


def ingest_screenshot() -> int:
    """Read screenshot_log.json and append entries to storm_feed.json."""
    data = _load_feed()
    new_items = []
    try:
        if SCREENSHOT_LOG.exists():
            sc_data = json.loads(SCREENSHOT_LOG.read_text(encoding="utf-8"))
            for sc in (sc_data if isinstance(sc_data, list) else sc_data.get("screenshots", []))[-20:]:
                new_items.append({
                    "source": "screenshot",
                    "category": "screenshot",
                    "timestamp": sc.get("uploaded_at") or sc.get("ts") or _now_iso(),
                    "description": sc.get("description") or sc.get("filename") or "screenshot",
                    "severity": "info",
                    "resolved": False,
                })
    except Exception:
        pass
    _append(data.setdefault("entries", []), new_items)
    data["last_ingested"] = _now_iso()
    _save_feed(data)
    return len(new_items)


def get_feed(severity: str = None, limit: int = 50) -> list:
    """Return entries from storm_feed.json, optionally filtered by severity."""
    data = _load_feed()
    entries = data.get("entries", [])
    if severity:
        entries = [e for e in entries if e.get("severity") == severity]
    return entries[:limit]


def clear_feed() -> bool:
    """Clear all entries from storm_feed.json."""
    return _save_feed({"entries": [], "last_ingested": _now_iso()})


def full_ingest() -> dict:
    """Run all ingest functions and return summary."""
    d = ingest_detective()
    s = ingest_sesum()
    sc = ingest_screenshot()
    return {"detective": d, "sesum": s, "screenshot": sc, "total": d + s + sc}


# ── Backward-compat HTTP-based class ──────────────────────────────────────────

import urllib.request
import urllib.parse

MCC_HOST = "http://127.0.0.1:8080"


class StormBridge:
    """HTTP-based bridge — used when mcc_server.py is running."""

    def ingest(self, source: str, category: str, data_dict: dict) -> bool:
        payload = {
            "source": source,
            "category": category,
            "timestamp": _now_iso(),
            "resolved": False,
            **data_dict,
        }
        try:
            body = json.dumps(payload).encode()
            req = urllib.request.Request(
                f"{MCC_HOST}/api/storm/ingest",
                data=body,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception:
            return False

    def get_feed(self, severity: str = None, limit: int = 50) -> list:
        try:
            params = {"limit": str(limit)}
            if severity:
                params["severity"] = severity
            qs = urllib.parse.urlencode(params)
            resp = urllib.request.urlopen(f"{MCC_HOST}/api/storm/feed?{qs}", timeout=5)
            data = json.loads(resp.read())
            return data.get("entries", [])
        except Exception:
            return []

    def get_summary(self) -> dict:
        try:
            resp = urllib.request.urlopen(f"{MCC_HOST}/api/storm/summary", timeout=5)
            return json.loads(resp.read())
        except Exception:
            return {}


if __name__ == "__main__":
    print("storm_bridge.py — full ingest run")
    result = full_ingest()
    print(f"  detective: {result['detective']} | sesum: {result['sesum']} | screenshot: {result['screenshot']}")
    feed = get_feed(limit=5)
    print(f"  Latest {len(feed)} entries:")
    for e in feed:
        print(f"    [{e.get('source','')}] {e.get('description','')[:60]}")
