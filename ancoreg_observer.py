"""
ancoreg_observer.py — Pre/post OCB run observer for ANCOREG Health Suite.
Snapshots MOT score + error count before each run, compares after, writes verdict.
"""

import json
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"
OBSERVER_LOG    = DATA / "ocb_observer_log.json"
TERMINATOR_FEED = DATA / "terminator_feed.json"
HEALTH_DB       = DATA / "health.db"
STATUS_FILE     = HERE / "STATUS.md"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _load_log() -> dict:
    if OBSERVER_LOG.exists():
        try:
            return json.loads(OBSERVER_LOG.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_log(data: dict):
    DATA.mkdir(exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(DATA), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        shutil.move(tmp, str(OBSERVER_LOG))
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass


def _get_mot_score() -> str:
    """Read the last known MOT score from ocb_progress.json or ocb_status.json."""
    for fname in ("ocb_progress.json", "ocb_status.json"):
        p = DATA / fname
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                score = d.get("mot_score", "")
                if score:
                    return str(score)
            except Exception:
                pass
    return "unknown"


def _get_error_count() -> int:
    """Count FAIL rows in data/health.db health_results table (0 if db absent)."""
    if not HEALTH_DB.exists():
        return 0
    try:
        conn = sqlite3.connect(str(HEALTH_DB), timeout=5)
        row = conn.execute(
            "SELECT COUNT(*) FROM health_results WHERE status = ?", ("FAIL",)
        ).fetchone()
        conn.close()
        return int(row[0]) if row else 0
    except Exception:
        return 0


def _get_status_linecount() -> int:
    if STATUS_FILE.exists():
        try:
            return len(STATUS_FILE.read_text(encoding="utf-8").splitlines())
        except Exception:
            pass
    return 0


def pre_run(run_id: str, task_description: str):
    """
    Snapshot current MOT score, error count, and STATUS.md line count.
    Saves to data/ocb_observer_log.json under the run_id key.
    """
    snapshot = {
        "run_id":           run_id,
        "task_description": task_description,
        "pre": {
            "mot_score":        _get_mot_score(),
            "error_count":      _get_error_count(),
            "status_linecount": _get_status_linecount(),
            "timestamp":        _now(),
        },
        "post":    None,
        "verdict": "UNKNOWN",
    }
    log = _load_log()
    log[run_id] = snapshot
    _save_log(log)


def post_run(run_id: str, result: dict, log_output: list):
    """
    Compare post-run state to the pre-run snapshot.
    Flags regressions (new errors introduced, run failed).
    Writes verdict CLEAN / REGRESSION / UNKNOWN to data/ocb_observer_log.json.
    Appends to data/terminator_feed.json only on CLEAN verdict.
    """
    log   = _load_log()
    entry = log.get(run_id, {
        "run_id": run_id, "task_description": "", "pre": {}, "post": None, "verdict": "UNKNOWN",
    })

    new_mot      = str(result.get("mot_score", ""))
    new_errors   = _get_error_count()
    new_linecount = _get_status_linecount()

    pre        = entry.get("pre", {})
    pre_errors = int(pre.get("error_count", 0))

    post = {
        "mot_score":        new_mot,
        "error_count":      new_errors,
        "status_linecount": new_linecount,
        "timestamp":        _now(),
    }
    entry["post"] = post

    # Determine verdict
    run_status = (result.get("status") or "").upper()
    if run_status in ("FAILED", "ROLLED_BACK", "CANCELLED", "BLOCKED"):
        verdict = "REGRESSION"
    elif new_errors > pre_errors:
        verdict = "REGRESSION"
    elif run_status == "DONE" or "all clear" in new_mot.lower():
        verdict = "CLEAN"
    elif run_status == "PARTIAL":
        verdict = "UNKNOWN"
    else:
        verdict = "UNKNOWN"

    entry["verdict"] = verdict
    log[run_id] = entry
    _save_log(log)

    if verdict == "CLEAN":
        _append_terminator(run_id, entry.get("task_description", ""), result, log_output)


def _append_terminator(run_id: str, task: str, result: dict, log_output: list):
    """Append a successful run record to data/terminator_feed.json."""
    if isinstance(log_output, list):
        raw = "\n".join(str(l) for l in log_output)
    else:
        raw = str(log_output)

    entry = {
        "timestamp":   _now(),
        "run_id":      run_id,
        "task":        (task or "")[:120],
        "result":      "pass",
        "log_summary": raw[:200],
    }

    feed: list = []
    if TERMINATOR_FEED.exists():
        try:
            feed = json.loads(TERMINATOR_FEED.read_text(encoding="utf-8"))
            if not isinstance(feed, list):
                feed = []
        except Exception:
            feed = []

    feed.append(entry)
    if len(feed) > 500:
        feed = feed[-500:]

    DATA.mkdir(exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(DATA), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(feed, f, indent=2)
        shutil.move(tmp, str(TERMINATOR_FEED))
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
