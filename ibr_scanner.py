"""
ibr_scanner.py — IBR (Integrity, Build, Reference) project health audit.
Writes data/ibr_report_{timestamp}.json + data/ibr_latest.txt
"""
import datetime
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"
SESSION_LOGS = HERE / "session_logs"
STATUS_FILE  = HERE / "STATUS.md"
HISTORY_FILE = HERE / "HISTORY.md"
ACCA_FILE    = HERE / "ACCA.md"
INDEX_FILE   = HERE / "INDEX.md"
ALP_FILE     = HERE / "ALP_Database.md"
STATUS_LC    = DATA / "status_linecount.json"
SEVEN_DAYS   = datetime.timedelta(days=7)


def _now(): return datetime.datetime.now()
def _iso(): return _now().isoformat()[:19]
def _ts():  return _now().strftime("%Y%m%d_%H%M%S")


def check1_file_integrity():
    """Check STATUS.md, INDEX.md, HISTORY.md, ACCA.md exist and STATUS is healthy."""
    results = []
    baseline = 0
    current  = 0

    for name, path in [("STATUS.md", STATUS_FILE), ("INDEX.md", INDEX_FILE),
                        ("HISTORY.md", HISTORY_FILE), ("ACCA.md", ACCA_FILE)]:
        if path.exists():
            results.append({"check": name + " exists", "status": "PASS", "detail": f"{path.stat().st_size} bytes"})
        else:
            results.append({"check": name + " exists", "status": "FAIL", "detail": "File not found"})

    if STATUS_FILE.exists():
        current = len(STATUS_FILE.read_text(encoding="utf-8", errors="replace").splitlines())
        if STATUS_LC.exists():
            try:
                baseline = int(json.loads(STATUS_LC.read_text(encoding="utf-8")).get("baseline", current))
            except Exception:
                baseline = current
        else:
            baseline = current
        ratio = current / baseline if baseline else 1.0
        if ratio >= 0.90:
            status = "PASS"
        elif ratio >= 0.85:
            status = "WARN"
        else:
            status = "FAIL"
        results.append({"check": "STATUS.md line count", "status": status,
                         "detail": f"{current} lines (baseline {baseline}, {ratio:.0%})"})

        # Scan "BUILT AND WORKING" table for file references
        text = STATUS_FILE.read_text(encoding="utf-8", errors="replace")
        missing = []
        for line in text.splitlines():
            if not line.strip().startswith("|"): continue
            # Look for .py / .html / .json filenames in table cells
            for m in re.finditer(r'`([^`]+\.(py|html|json|md|txt))`', line):
                fname = m.group(1).strip()
                if "/" not in fname and "\\" not in fname:
                    if not (HERE / fname).exists():
                        missing.append(fname)
        missing = list(set(missing))
        if missing:
            results.append({"check": "Files in STATUS built list", "status": "WARN",
                             "detail": f"{len(missing)} referenced files missing: {', '.join(missing[:10])}"})
        else:
            results.append({"check": "Files in STATUS built list", "status": "PASS",
                             "detail": "All referenced files found"})

    return {"name": "Check 1 — File Integrity", "items": results,
            "overall": "FAIL" if any(r["status"]=="FAIL" for r in results)
                       else "WARN" if any(r["status"]=="WARN" for r in results) else "PASS"}


def check2_session_logs():
    """Count session logs, find gaps, truncated files, newest/oldest."""
    results = []
    if not SESSION_LOGS.exists():
        return {"name": "Check 2 — Session Log Health", "overall": "WARN",
                "items": [{"check": "session_logs/ exists", "status": "WARN", "detail": "Directory not found"}]}

    logs = sorted(SESSION_LOGS.glob("*.md"), key=lambda f: f.stat().st_mtime)
    results.append({"check": "Session log count", "status": "PASS" if logs else "WARN",
                    "detail": f"{len(logs)} .md files in session_logs/"})

    if logs:
        oldest = datetime.datetime.fromtimestamp(logs[0].stat().st_mtime)
        newest = datetime.datetime.fromtimestamp(logs[-1].stat().st_mtime)
        results.append({"check": "Date range", "status": "PASS",
                        "detail": f"Oldest: {oldest:%Y-%m-%d}  Newest: {newest:%Y-%m-%d}"})

        truncated = []
        for f in logs:
            try:
                lines = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
                if lines < 10:
                    truncated.append(f"{f.name} ({lines} lines)")
            except Exception:
                pass
        if truncated:
            results.append({"check": "Truncated session logs (<10 lines)", "status": "WARN",
                            "detail": ", ".join(truncated[:5])})
        else:
            results.append({"check": "Truncated session logs", "status": "PASS",
                            "detail": "All session logs have ≥10 lines"})

    return {"name": "Check 2 — Session Log Health",
            "overall": "WARN" if any(r["status"]=="WARN" for r in results) else "PASS",
            "items": results}


def check3_acca_consistency():
    """Find ACCA codes used in STATUS/HISTORY/INDEX that are not in ACCA.md."""
    results = []
    if not ACCA_FILE.exists():
        return {"name": "Check 3 — ACCA Code Consistency", "overall": "WARN",
                "items": [{"check": "ACCA.md exists", "status": "WARN", "detail": "ACCA.md not found"}]}

    acca_text = ACCA_FILE.read_text(encoding="utf-8", errors="replace")
    registered = set(re.findall(r'\b([A-Z]{2,6}-\d{2,4})\b', acca_text))

    found_codes = set()
    for fpath in [STATUS_FILE, HISTORY_FILE, INDEX_FILE]:
        if fpath.exists():
            txt = fpath.read_text(encoding="utf-8", errors="replace")
            found_codes.update(re.findall(r'\b([A-Z]{2,6}-\d{2,4})\b', txt))

    unregistered = sorted(found_codes - registered)
    results.append({"check": "Registered ACCA codes", "status": "PASS",
                    "detail": f"{len(registered)} codes in ACCA.md"})
    if unregistered:
        results.append({"check": "Unregistered codes found", "status": "WARN",
                        "detail": ", ".join(unregistered[:20])})
    else:
        results.append({"check": "Unregistered codes found", "status": "PASS",
                        "detail": "All codes in project files are registered in ACCA.md"})

    return {"name": "Check 3 — ACCA Code Consistency",
            "overall": "WARN" if unregistered else "PASS",
            "items": results}


def check4_dead_files():
    """Find files in project root that are not in STATUS.md built list and not in archive_dead/."""
    results = []
    if not STATUS_FILE.exists():
        return {"name": "Check 4 — Dead File Check", "overall": "WARN",
                "items": [{"check": "STATUS.md readable", "status": "WARN", "detail": "Not found"}]}

    status_text = STATUS_FILE.read_text(encoding="utf-8", errors="replace")
    mentioned = set(re.findall(r'`([^`]+)`', status_text))

    archive = HERE / "archive_dead"
    orphans = []
    IGNORE_EXTS = {".pyc", ".pyo", ".db", ".log"}
    IGNORE_NAMES = {"__pycache__", ".git", ".claude", "node_modules", "electron"}
    for p in HERE.iterdir():
        if p.name in IGNORE_NAMES: continue
        if not p.is_file(): continue
        if p.suffix in IGNORE_EXTS: continue
        if p.name.startswith("."): continue
        if p.name not in mentioned:
            orphans.append(p.name)

    results.append({"check": "Orphan files in root", "status": "WARN" if orphans else "PASS",
                    "detail": f"{len(orphans)} files not mentioned in STATUS.md: {', '.join(sorted(orphans)[:15])}" if orphans else "None — all root files are referenced in STATUS.md"})

    return {"name": "Check 4 — Dead File Check",
            "overall": "WARN" if orphans else "PASS",
            "items": results}


def check5_alp_database():
    """Check ALP_Database.md has entries and last entry is recent."""
    results = []
    if not ALP_FILE.exists():
        return {"name": "Check 5 — ALP Database", "overall": "WARN",
                "items": [{"check": "ALP_Database.md exists", "status": "WARN", "detail": "Not found"}]}

    text = ALP_FILE.read_text(encoding="utf-8", errors="replace")
    entries = [l for l in text.splitlines()
               if l.strip().startswith("|") and "Date" not in l and "---" not in l and len(l.strip()) > 3]
    results.append({"check": "ALP entry count", "status": "PASS" if entries else "WARN",
                    "detail": f"{len(entries)} entries found"})

    if entries:
        # Try to parse the most recent date
        last_dates = []
        for e in entries[-3:]:
            parts = [p.strip() for p in e.strip("|").split("|")]
            if parts:
                try:
                    d = datetime.datetime.strptime(parts[0].strip(), "%Y-%m-%d")
                    last_dates.append(d)
                except Exception:
                    pass
        if last_dates:
            most_recent = max(last_dates)
            age = _now() - most_recent
            if age > SEVEN_DAYS:
                results.append({"check": "Last ALP entry age", "status": "WARN",
                                 "detail": f"Last entry: {most_recent:%Y-%m-%d} — {age.days} days ago. New savings may have been missed."})
            else:
                results.append({"check": "Last ALP entry age", "status": "PASS",
                                 "detail": f"Last entry: {most_recent:%Y-%m-%d} — within 7 days"})

    return {"name": "Check 5 — ALP Database",
            "overall": "WARN" if any(r["status"]=="WARN" for r in results) else "PASS",
            "items": results}


def check6_provider_health():
    """Try to call /api/health on the local MCC server."""
    results = []
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8080/health-status", timeout=3)
        data = json.loads(req.read())
        providers = data.get("providers", [])
        green = sum(1 for p in providers if p.get("status") in ("GREEN", "OK"))
        total = len(providers)
        results.append({"check": "MCC server reachable", "status": "PASS", "detail": "Connected to http://127.0.0.1:8080"})
        results.append({"check": "Provider health snapshot", "status": "PASS" if green >= total/2 else "WARN",
                         "detail": f"{green}/{total} providers healthy"})
    except Exception as exc:
        results.append({"check": "MCC server reachable", "status": "WARN",
                         "detail": f"Cannot reach server: {exc}. Start mcc_server.py first for live health."})

    return {"name": "Check 6 — Provider Health Snapshot",
            "overall": "WARN" if any(r["status"] in ("WARN","FAIL") for r in results) else "PASS",
            "items": results}


def main():
    checks = [
        check1_file_integrity(),
        check2_session_logs(),
        check3_acca_consistency(),
        check4_dead_files(),
        check5_alp_database(),
        check6_provider_health(),
    ]

    ts = _ts()
    total = len(checks)
    passed = sum(1 for c in checks if c["overall"] == "PASS")
    warned = sum(1 for c in checks if c["overall"] == "WARN")
    failed = sum(1 for c in checks if c["overall"] == "FAIL")

    report = {
        "generated_at": _iso(),
        "summary": {"total": total, "pass": passed, "warn": warned, "fail": failed},
        "checks": checks,
    }

    DATA.mkdir(exist_ok=True)
    json_file = DATA / f"ibr_report_{ts}.json"
    json_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "=" * 65,
        f"  IBR SCAN REPORT — {_iso()}",
        "=" * 65,
        f"  Result: {passed} PASS  |  {warned} WARN  |  {failed} FAIL",
        "=" * 65,
        "",
    ]
    for c in checks:
        icon = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}.get(c["overall"], "[?]")
        lines.append(f"{icon}  {c['name']}")
        for item in c.get("items", []):
            status = item.get("status", "?")
            detail = item.get("detail", "")
            check  = item.get("check", "?")
            pfx    = {"PASS": "     +", "WARN": "     !", "FAIL": "     X"}.get(status, "     ?")
            lines.append(f"{pfx}  {check}: {detail}")
        lines.append("")

    report_text = "\n".join(lines)
    latest_file = DATA / "ibr_latest.txt"
    latest_file.write_text(report_text, encoding="utf-8")

    sys.stdout.buffer.write(report_text.encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()
    return report


if __name__ == "__main__":
    main()
