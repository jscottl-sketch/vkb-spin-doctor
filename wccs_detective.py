"""
wccs_detective.py — WCCS Chief Detective
Reads every data source in the project and builds a case file of what is
confirmed, uncertain, and unknown about project state.
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"

# Data source paths
STATUS_MD          = HERE / "STATUS.md"
HISTORY_MD         = HERE / "HISTORY.md"
ACCA_MD            = HERE / "ACCA.md"
SESSION_LOGS_DIR   = HERE / "session_logs"
WAL_LOG            = HERE / "ocb_wal.log"
OCB_QUEUE          = DATA_DIR / "ocb_queue.json"
KANBAN_BOARD       = DATA_DIR / "kanban_board.json"
HEALTH_DB          = DATA_DIR / "health.db"
SNAPSHOTS_DIR      = HERE / "status_snapshots"
MCCM_PERMS         = DATA_DIR / "mccm_permissions.json"
INVESTIGATIONS_DIR = DATA_DIR / "mccm_investigations"

# Patterns for extracting facts
_TS_PATTERN  = re.compile(r'\b(20\d{2}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?)?)\b')
_OCB_PATTERN = re.compile(r'\bOCB[-–—]([A-Z0-9]+)\b')
_STATUS_PATTERN = re.compile(r'\b(COMPLETE|DONE|PENDING|IN[- ]PROGRESS|BUILT|ACTIVE|PASS|FAIL)\b', re.IGNORECASE)


def _read_safe(path: Path, max_lines: int = None) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if max_lines:
            lines = text.splitlines()[:max_lines]
            return "\n".join(lines)
        return text
    except Exception:
        return ""


def _extract_facts(text: str, source_name: str) -> dict:
    timestamps = list(dict.fromkeys(_TS_PATTERN.findall(text)))
    ocb_names  = list(dict.fromkeys(f"OCB-{m}" for m in _OCB_PATTERN.findall(text)))
    markers    = list(dict.fromkeys(m.upper() for m in _STATUS_PATTERN.findall(text)))
    # Extract table rows from STATUS.md BUILT table
    table_rows = []
    for line in text.splitlines():
        if line.strip().startswith("|") and "|" in line[1:]:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and cells[0] not in ("Component", "---", ":---"):
                table_rows.append(cells[0])
    return {
        "timestamps": timestamps,
        "ocb_names": ocb_names,
        "status_markers": markers,
        "key_facts": table_rows[:60] if table_rows else ocb_names[:30],
    }


def scan_all_sources() -> dict:
    """Returns dict: {source_name: {last_modified, key_facts, timestamps}}"""
    results = {}

    def _add(name: str, path: Path, text: str):
        mtime = ""
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
        facts = _extract_facts(text, name)
        results[name] = {
            "last_modified": mtime,
            "key_facts":     facts["key_facts"],
            "timestamps":    facts["timestamps"],
            "ocb_names":     facts["ocb_names"],
            "status_markers": facts["status_markers"],
        }

    # STATUS.md
    if STATUS_MD.exists():
        _add("STATUS.md", STATUS_MD, _read_safe(STATUS_MD))

    # HISTORY.md
    if HISTORY_MD.exists():
        _add("HISTORY.md", HISTORY_MD, _read_safe(HISTORY_MD))

    # ACCA.md
    if ACCA_MD.exists():
        _add("ACCA.md", ACCA_MD, _read_safe(ACCA_MD))

    # Session logs — newest first
    if SESSION_LOGS_DIR.exists():
        logs = sorted(SESSION_LOGS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        for i, log in enumerate(logs[:10]):
            _add(f"session_log/{log.name}", log, _read_safe(log, max_lines=50))

    # ocb_wal.log
    if WAL_LOG.exists():
        _add("ocb_wal.log", WAL_LOG, _read_safe(WAL_LOG))

    # data/ocb_queue.json
    if OCB_QUEUE.exists():
        _add("ocb_queue.json", OCB_QUEUE, _read_safe(OCB_QUEUE))

    # data/kanban_board.json
    if KANBAN_BOARD.exists():
        _add("kanban_board.json", KANBAN_BOARD, _read_safe(KANBAN_BOARD))

    # health.db — last 20 rows from each table
    if HEALTH_DB.exists():
        try:
            conn = sqlite3.connect(str(HEALTH_DB))
            cur  = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            texts  = []
            for tbl in tables:
                try:
                    rows = conn.execute(f"SELECT * FROM [{tbl}] ORDER BY rowid DESC LIMIT 20").fetchall()
                    for row in rows:
                        texts.append(" ".join(str(c) for c in row))
                except Exception:
                    pass
            conn.close()
            _add("health.db", HEALTH_DB, "\n".join(texts))
        except Exception:
            pass

    # status_snapshots/ — filenames only
    if SNAPSHOTS_DIR.exists():
        names = sorted(p.name for p in SNAPSHOTS_DIR.iterdir())
        _add("status_snapshots/", SNAPSHOTS_DIR, "\n".join(names))

    # git log --oneline -30
    try:
        proc = subprocess.run(
            ["git", "log", "--oneline", "-30"],
            capture_output=True, text=True, cwd=str(HERE), timeout=15
        )
        _add("git_log", HERE / ".git" / "COMMIT_EDITMSG", proc.stdout)
    except Exception:
        pass

    return results


def cross_reference_dates() -> list:
    """Compare timestamps across sources, return inconsistencies."""
    sources = scan_all_sources()
    inconsistencies = []

    status_ts  = set(sources.get("STATUS.md",  {}).get("timestamps", []))
    history_ts = set(sources.get("HISTORY.md", {}).get("timestamps", []))
    wal_ts     = set(sources.get("ocb_wal.log",{}).get("timestamps", []))
    status_ocb = set(sources.get("STATUS.md",  {}).get("ocb_names", []))
    history_ocb= set(sources.get("HISTORY.md", {}).get("ocb_names", []))

    # Session logs with no matching STATUS.md timestamp
    for key, val in sources.items():
        if not key.startswith("session_log/"):
            continue
        for ts in val.get("timestamps", []):
            date = ts[:10]
            if not any(date in s for s in status_ts):
                inconsistencies.append({
                    "source_a": key,
                    "source_b": "STATUS.md",
                    "description": f"Session log timestamp {ts} not reflected in STATUS.md",
                })

    # WAL entries without STATUS.md mention
    for ts in wal_ts:
        date = ts[:10]
        if not any(date in s for s in status_ts):
            inconsistencies.append({
                "source_a": "ocb_wal.log",
                "source_b": "STATUS.md",
                "description": f"WAL log entry {ts} has no matching STATUS.md date",
            })

    # OCBs in HISTORY but not in STATUS BUILT table
    for ocb in history_ocb:
        if ocb not in status_ocb:
            inconsistencies.append({
                "source_a": "HISTORY.md",
                "source_b": "STATUS.md",
                "description": f"{ocb} found in HISTORY.md but not confirmed in STATUS.md BUILT table",
            })

    return inconsistencies


def find_gaps() -> list:
    """
    Returns list of dicts: {gap_id, description, sources_checked,
    confidence: HIGH/MEDIUM/LOW, suggested_fix}
    A gap is anything mentioned in one source but missing from STATUS.md.
    """
    sources   = scan_all_sources()
    status_text = _read_safe(STATUS_MD)
    gaps = []
    gap_id = 1

    def _in_status(term: str) -> bool:
        return term.lower() in status_text.lower()

    # OCB names in non-STATUS sources but absent from STATUS
    all_ocb = set()
    for key, val in sources.items():
        if key != "STATUS.md":
            for ocb in val.get("ocb_names", []):
                all_ocb.add(ocb)

    for ocb in sorted(all_ocb):
        if not _in_status(ocb):
            gaps.append({
                "gap_id":         f"GAP-{gap_id:03d}",
                "description":    f"{ocb} mentioned in non-STATUS sources but absent from STATUS.md",
                "sources_checked": [k for k, v in sources.items() if ocb in v.get("ocb_names", [])],
                "confidence":     "MEDIUM",
                "suggested_fix":  f"Add {ocb} entry to STATUS.md BUILT table if build is complete",
            })
            gap_id += 1

    # Session log facts not in STATUS
    for key, val in sources.items():
        if not key.startswith("session_log/"):
            continue
        for fact in val.get("key_facts", [])[:10]:
            if len(fact) > 8 and not _in_status(fact[:20]):
                gaps.append({
                    "gap_id":         f"GAP-{gap_id:03d}",
                    "description":    f"Session log entry '{fact[:60]}' not found in STATUS.md",
                    "sources_checked": [key],
                    "confidence":     "LOW",
                    "suggested_fix":  f"Verify if '{fact[:40]}' should be in STATUS.md BUILT table",
                })
                gap_id += 1
                if gap_id > 50:
                    break

    return gaps


def build_case_file() -> dict:
    """
    Returns dict:
      CONFIRMED: facts with 2+ source agreement
      UNCERTAIN: facts with 1 source only
      UNKNOWN:   things referenced but not found anywhere
      PROPOSED_UPDATES: text blocks ready to add to STATUS.md BUILT table
    """
    sources   = scan_all_sources()
    gaps      = find_gaps()
    incon     = cross_reference_dates()
    status_text = _read_safe(STATUS_MD)

    # Build fact frequency map
    fact_count: dict = {}
    for key, val in sources.items():
        for ocb in val.get("ocb_names", []):
            fact_count[ocb] = fact_count.get(ocb, 0) + 1

    confirmed  = {k: v for k, v in fact_count.items() if v >= 2}
    uncertain  = {k: v for k, v in fact_count.items() if v == 1}
    unknown    = [g["description"] for g in gaps if g["confidence"] == "LOW"]

    # Proposed STATUS.md rows — CONFIRMED items not already in STATUS
    proposed = []
    for ocb in sorted(confirmed.keys()):
        if ocb.lower() not in status_text.lower():
            today = datetime.now().strftime("%Y-%m-%d")
            proposed.append(f"| {ocb} | Confirmed by detective {today} — verify details |")

    return {
        "CONFIRMED":          confirmed,
        "UNCERTAIN":          uncertain,
        "UNKNOWN":            unknown,
        "PROPOSED_UPDATES":   proposed,
        "INCONSISTENCIES":    incon,
        "GAPS":               gaps,
        "sources_scanned":    list(sources.keys()),
        "generated_at":       datetime.now().isoformat(timespec="seconds"),
    }


def propose_status_updates():
    """Print all proposed STATUS.md table rows — does NOT auto-write."""
    case_file = build_case_file()
    print("\n=== PROPOSED STATUS.md ADDITIONS ===")
    rows = case_file.get("PROPOSED_UPDATES", [])
    if not rows:
        print("  (none — STATUS.md appears up to date)")
    else:
        for row in rows:
            print(row)
    print()


def request_ai_investigation(gap_id: str, gap_description: str):
    """Flag a low-confidence gap to MCCM for AI investigation."""
    perms_path = MCCM_PERMS
    try:
        if perms_path.exists():
            perms = json.loads(perms_path.read_text(encoding="utf-8"))
        else:
            perms = {"mccm_power_level": 1, "pending": [], "approved": [],
                     "rejected": [], "scott_interrupts": [], "last_cycle": None}

        request_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}-{gap_id}"
        perms.setdefault("pending", []).append({
            "request_id":    request_id,
            "gap_id":        gap_id,
            "description":   gap_description,
            "requested_by":  "WCCS_DETECTIVE",
            "timestamp":     datetime.now().isoformat(timespec="seconds"),
            "level_required": 2,
        })
        fd, tmp = tempfile.mkstemp(dir=str(perms_path.parent), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(perms, f, indent=2)
        os.replace(tmp, str(perms_path))
        print(f"🔍 Gap flagged to MCCM: {gap_description[:80]}")
    except Exception as exc:
        print(f"[DETECTIVE] Failed to write MCCM request: {exc}")


def main():
    today      = datetime.now().strftime("%Y%m%d")
    report_path = DATA_DIR / f"detective_report_{today}.json"

    print("[DETECTIVE] Scanning all sources…")
    case_file = build_case_file()

    # Atomic write
    DATA_DIR.mkdir(exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(DATA_DIR), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(case_file, f, indent=2)
    os.replace(tmp, str(report_path))

    # Flag LOW confidence gaps to MCCM
    mccm_count = 0
    for gap in case_file.get("GAPS", []):
        if gap.get("confidence") == "LOW":
            request_ai_investigation(gap["gap_id"], gap["description"])
            mccm_count += 1

    print()
    print("=== WCCS CHIEF DETECTIVE REPORT ===")
    print(f"CONFIRMED: {len(case_file['CONFIRMED'])} facts")
    print(f"UNCERTAIN: {len(case_file['UNCERTAIN'])} items")
    print(f"UNKNOWN: {len(case_file['UNKNOWN'])} gaps")
    print(f"Proposed STATUS.md additions: {len(case_file['PROPOSED_UPDATES'])} rows")
    print(f"MCCM requests raised: {mccm_count}")
    print(f"Full report: {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WCCS Chief Detective")
    parser.add_argument("--investigate", action="store_true", help="Full investigation run")
    parser.add_argument("--propose",     action="store_true", help="Print proposed STATUS.md updates only")
    parser.add_argument("--gaps",        action="store_true", help="Print gaps only")
    args = parser.parse_args()

    if args.propose:
        propose_status_updates()
    elif args.gaps:
        gaps = find_gaps()
        print(f"\n=== GAPS ({len(gaps)}) ===")
        for g in gaps:
            print(f"[{g['confidence']}] {g['gap_id']}: {g['description']}")
            print(f"  Fix: {g['suggested_fix']}")
        print()
    else:
        main()
