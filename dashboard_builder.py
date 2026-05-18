#!/usr/bin/env python3
"""
dashboard_builder.py  —  VKB Spin Doctor MCC data builder

Reads:  data/knowledge_engine.db (solution_log)
        Desktop/mission_control_tasks.json
        data/cost_log.txt
        loop_output/  (last 10 files)
        session_logs/ (last 5 files)

Writes: data/dashboard_data.json  (atomic via .tmp + rename)
        data/dashboard_data_backup.json  (copy of previous output)

Flags:  --dry-run   Print what would change, no write.
"""

import argparse
import json
import re
import shutil
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

BASE         = Path(__file__).parent
DATA_DIR     = BASE / "data"
DB_PATH      = DATA_DIR / "knowledge_engine.db"
COST_LOG     = DATA_DIR / "cost_log.txt"
LOOP_OUT     = BASE / "loop_output"
SESSION_LOGS = BASE / "session_logs"
OUT_PATH     = DATA_DIR / "dashboard_data.json"
BACKUP_PATH  = DATA_DIR / "dashboard_data_backup.json"
CAP          = 50

# Desktop path — mission_control_tasks.json lives here
_DESKTOP     = Path.home() / "Desktop"
TASKS_JSON   = _DESKTOP / "mission_control_tasks.json"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ── Section builders ───────────────────────────────────────────────────────────

def build_tasks() -> dict:
    try:
        raw = json.loads(TASKS_JSON.read_text(encoding="utf-8"))
        return {"last_updated": _now(), "data": raw.get("tasks", []), "meta": raw.get("meta", {})}
    except FileNotFoundError:
        return {"last_updated": _now(), "data": [], "error": f"Not found: {TASKS_JSON}"}
    except Exception as exc:
        return {"last_updated": _now(), "data": [], "error": str(exc)}


def build_activity_feed() -> dict:
    events = []

    # loop_output/ — last 10 files, sorted newest first
    if LOOP_OUT.exists():
        files = sorted(LOOP_OUT.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:10]
        for f in files:
            m = re.match(r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})_(.+)\.md", f.name)
            if m:
                ts = f"{m.group(1)}T{m.group(2).replace('-', ':')}:00"
            else:
                ts = datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds")
            goal, score = f.stem, None
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
                for line in lines[:15]:
                    if line.startswith("**Goal:**"):
                        goal = line.replace("**Goal:**", "").strip()
                    sm = re.search(r"\*\*Score:\*\*\s*([\d.]+)", line)
                    if sm:
                        score = float(sm.group(1))
            except Exception:
                pass
            events.append({
                "timestamp": ts,
                "type": "loop_run",
                "title": goal[:80],
                "detail": f"Score: {score:.2f}" if score is not None else "Loop run",
                "file": f.name,
            })

    # session_logs/ — last 5 files
    if SESSION_LOGS.exists():
        files = sorted(SESSION_LOGS.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:5]
        for f in files:
            ts = datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds")
            title = f.stem
            try:
                first = f.read_text(encoding="utf-8", errors="replace").splitlines()[0]
                title = first.lstrip("# ").strip() or f.stem
            except Exception:
                pass
            events.append({
                "timestamp": ts,
                "type": "session_log",
                "title": title[:80],
                "detail": f.name,
                "file": f.name,
            })

    events.sort(key=lambda e: e["timestamp"], reverse=True)
    return {"last_updated": _now(), "data": events[:CAP]}


def build_aafl_runs() -> dict:
    if not DB_PATH.exists():
        return {"last_updated": _now(), "data": [], "error": f"DB not found: {DB_PATH}"}
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute("PRAGMA table_info(solution_log)")
        cols = [r[1] for r in c.fetchall()]
        if not cols:
            conn.close()
            return {"last_updated": _now(), "data": [], "error": "solution_log table empty or missing"}
        c.execute(f"SELECT * FROM solution_log ORDER BY rowid DESC LIMIT {CAP}")
        rows = c.fetchall()
        conn.close()
        runs = []
        for row in rows:
            r = dict(zip(cols, row))
            score = r.get("ai_score")
            passed = bool(r.get("worked", 0)) or (score is not None and score >= 7.0)
            runs.append({
                "id":         r.get("id"),
                "goal":       str(r.get("problem", ""))[:100],
                "score":      score,
                "tags":       r.get("tags", ""),
                "cost":       None,
                "passed":     passed,
                "iterations": r.get("iterations"),
                "game":       r.get("game"),
                "hardware":   r.get("hardware"),
                "created_at": r.get("created_at", ""),
            })
        return {"last_updated": _now(), "data": runs}
    except Exception as exc:
        return {"last_updated": _now(), "data": [], "error": str(exc)}


def build_cost_tracker() -> dict:
    if not COST_LOG.exists():
        return {"last_updated": _now(), "data": {
            "total_spent": 0.0, "avg_per_run": 0.0,
            "runs_today": 0, "runs_total": 0
        }, "error": f"Not found: {COST_LOG}"}
    total = 0.0
    runs_total = 0
    runs_today = 0
    today_str = date.today().strftime("%Y-%m-%d")
    try:
        text = COST_LOG.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if "] CALL #" not in line:
                continue
            dm = re.match(r"\[(\d{4}-\d{2}-\d{2})", line)
            line_date = dm.group(1) if dm else ""
            cm = re.search(r"cost=[^\d]*(\d+\.\d+)", line)
            if cm:
                total += float(cm.group(1))
                runs_total += 1
                if line_date == today_str:
                    runs_today += 1
    except Exception:
        pass
    avg = total / runs_total if runs_total else 0.0
    return {
        "last_updated": _now(),
        "data": {
            "total_spent":  round(total, 6),
            "avg_per_run":  round(avg, 6),
            "runs_today":   runs_today,
            "runs_total":   runs_total,
        }
    }


# ── Diff summary ───────────────────────────────────────────────────────────────

def _count(section: dict) -> int:
    d = section.get("data")
    return len(d) if isinstance(d, list) else (1 if d else 0)


def print_diff(new_data: dict, old_data: dict | None) -> None:
    for key in ("tasks", "activity_feed", "aafl_runs", "cost_tracker"):
        new_sec = new_data.get(key, {})
        old_sec = (old_data or {}).get(key, {})
        nc, oc = _count(new_sec), _count(old_sec)
        err = f"  [ERROR: {new_sec['error']}]" if "error" in new_sec else ""
        print(f"  {key}: {oc} -> {nc} items{err}")
    ct = new_data.get("cost_tracker", {}).get("data", {})
    if ct:
        print(f"    total_spent={ct.get('total_spent',0):.4f}  "
              f"avg={ct.get('avg_per_run',0):.4f}  "
              f"runs_today={ct.get('runs_today',0)}  "
              f"runs_total={ct.get('runs_total',0)}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="VKB MCC dashboard data builder")
    ap.add_argument("--dry-run", action="store_true", help="Print what would change, no write")
    args = ap.parse_args()

    print("[dashboard_builder] Building dashboard data...")
    new_data = {
        "meta": {"generated": _now(), "generator": "dashboard_builder.py"},
        "tasks":         build_tasks(),
        "activity_feed": build_activity_feed(),
        "aafl_runs":     build_aafl_runs(),
        "cost_tracker":  build_cost_tracker(),
    }

    old_data = None
    if OUT_PATH.exists():
        try:
            old_data = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    print_diff(new_data, old_data)

    if args.dry_run:
        print("[dashboard_builder] --dry-run: no files written.")
        return

    # Backup
    if OUT_PATH.exists():
        shutil.copy2(OUT_PATH, BACKUP_PATH)
        print(f"[dashboard_builder] Backup -> {BACKUP_PATH.name}")

    # Atomic write
    DATA_DIR.mkdir(exist_ok=True)
    tmp = OUT_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(new_data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(OUT_PATH)
    print(f"[dashboard_builder] Done -> {OUT_PATH}")


if __name__ == "__main__":
    main()
