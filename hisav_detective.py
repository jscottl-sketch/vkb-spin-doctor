"""
hisav_detective.py — 6-strategy live validator for VKB-SpinDoctor / AAFL project.

Runs: python hisav_detective.py --once   (single scan, write report, exit)
      python hisav_detective.py --watch  (loop every 5 minutes)

Writes: data/detective_report.json
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

REPORT_PATH = DATA / "detective_report.json"
STATUS_FILE = HERE / "STATUS.md"
MCC_SERVER  = HERE / "mcc_server.py"
MCC_HTML    = HERE / "mission_control.html"
SESSION_DIR = HERE / "session_logs"
MCC_MOT     = HERE / "mcc_full_mot.py"
BASE_URL    = "http://127.0.0.1:8080"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _now():
    return datetime.now(timezone.utc).isoformat()


def _load_report():
    if REPORT_PATH.exists():
        try:
            return json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_run": None, "run_count": 0, "findings": []}


def _save_report(report):
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def _make_finding(ftype, severity, description, evidence, suggested_fix, node_id=None):
    return {
        "id": f"det_{ftype.lower()}_{int(time.time()*1000) % 1000000}",
        "type": ftype,
        "severity": severity,
        "description": description,
        "evidence": evidence,
        "suggested_fix": suggested_fix,
        "status": "open",
        "found_at": _now(),
        "node_id": node_id,
    }


# ─────────────────────────────────────────────────────────────────────────────
# STRATEGY 1 — File Exists Checker
# ─────────────────────────────────────────────────────────────────────────────

def strategy_1_file_exists():
    findings = []
    if not STATUS_FILE.exists():
        findings.append(_make_finding(
            "GHOST_FILE", "high",
            "STATUS.md not found on disk",
            "File path: " + str(STATUS_FILE),
            "Restore STATUS.md from archive_dead/ or git history"
        ))
        return findings

    text = STATUS_FILE.read_text(encoding="utf-8", errors="ignore")

    # Extract filenames from BUILT section
    built_match = re.search(r'## CURRENT STATUS.*?BUILT(.*?)## CURRENT STATUS.*?PENDING', text, re.DOTALL)
    if not built_match:
        # Try simpler match
        built_match = re.search(r'## CURRENT STATUS.*?BUILT(.*?)---', text, re.DOTALL)

    section_text = built_match.group(1) if built_match else text

    # Find all filenames: *.py, *.json, *.html, *.md, *.bat, *.txt
    pattern = r'\b([\w_\-/]+\.(?:py|json|html|md|bat|txt|sh|csv|db))\b'
    raw_files = re.findall(pattern, section_text)

    # Deduplicate and filter junk
    seen = set()
    candidate_files = []
    for f in raw_files:
        if f in seen or f.startswith("2026") or len(f) < 5:
            continue
        seen.add(f)
        candidate_files.append(f)

    for fname in candidate_files:
        # Check project root, data/, session_logs/, health_results/
        candidates = [
            HERE / fname,
            HERE / "data" / fname,
            HERE / "session_logs" / fname,
        ]
        # Also check with path as-is relative to project root
        if any(c.exists() for c in candidates):
            continue
        # Check if it's a known dynamic/generated file that doesn't need to exist
        skip_patterns = ['*.log', 'morning_report', 'queue_log', 'loop_output', 'backup']
        skip = any(p.replace('*', '') in fname for p in skip_patterns)
        if skip:
            continue
        # Only flag if it looks like a real module file mentioned prominently
        if fname.endswith('.py') or fname.endswith('.html'):
            findings.append(_make_finding(
                "GHOST_FILE", "medium",
                f"File '{fname}' mentioned in STATUS.md but not found on disk",
                f"Searched: {HERE}/{fname}",
                f"Check if '{fname}' was renamed, archived, or never created"
            ))

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# STRATEGY 2 — Endpoint Health Checker
# ─────────────────────────────────────────────────────────────────────────────

def strategy_2_endpoint_health():
    findings = []
    if not MCC_SERVER.exists():
        return findings

    text = MCC_SERVER.read_text(encoding="utf-8", errors="ignore")

    # Extract route paths from @app.route style or path == "/api/..." patterns
    routes = set()
    # Pattern: path == "/api/..."
    for m in re.finditer(r'path\s*==\s*["\'](/api/[^"\'?{]+)["\']', text):
        routes.add(m.group(1))
    # Pattern: elif path.startswith("/api/...")
    for m in re.finditer(r'path\.startswith\s*\(["\'](/api/[^"\']{4,})["\']', text):
        routes.add(m.group(1))

    # Test a sample of routes (up to 20 GET endpoints)
    test_routes = sorted(routes)[:20]

    for route in test_routes:
        try:
            url = BASE_URL + route
            req = urllib.request.Request(url, method="GET")
            req.add_header("Accept", "application/json")
            with urllib.request.urlopen(req, timeout=3) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                status = resp.status
                if status == 404:
                    findings.append(_make_finding(
                        "DEAD_ENDPOINT", "high",
                        f"Endpoint {route} returns 404 — route registered but handler not found",
                        f"GET {url} → 404",
                        f"Check handler for {route} in mcc_server.py"
                    ))
                elif status >= 500:
                    findings.append(_make_finding(
                        "BROKEN_ENDPOINT", "high",
                        f"Endpoint {route} returns 5xx error",
                        f"GET {url} → {status}",
                        f"Check Python traceback for {route} handler"
                    ))
                elif body.strip() in ('{}', '[]', ''):
                    findings.append(_make_finding(
                        "HOLLOW_ENDPOINT", "low",
                        f"Endpoint {route} returns empty/empty object response",
                        f"GET {url} → empty body",
                        f"Verify {route} data source exists and has content"
                    ))
        except urllib.error.HTTPError as e:
            if e.code >= 500:
                findings.append(_make_finding(
                    "BROKEN_ENDPOINT", "high",
                    f"Endpoint {route} returned HTTP {e.code}",
                    f"GET {BASE_URL + route} → {e.code}",
                    f"Fix handler for {route}"
                ))
        except Exception:
            pass  # Server not running — skip silently

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# STRATEGY 3 — STATUS vs Reality Cross-Check
# ─────────────────────────────────────────────────────────────────────────────

def strategy_3_status_cross_check():
    findings = []
    if not STATUS_FILE.exists():
        return findings

    text = STATUS_FILE.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    built_items = set()
    pending_items = set()
    in_built = False
    in_pending = False

    for line in lines:
        if "BUILT AND WORKING" in line or (line.strip().startswith("|") and "CURRENT STATUS" in text[:text.find(line)] and in_built is False and "---" not in line):
            pass
        if "BUILT AND WORKING" in line:
            in_built = True
            in_pending = False
        elif "PENDING" in line and "##" in line:
            in_built = False
            in_pending = True
        elif line.strip().startswith("## ") and "BUILT" not in line and "PENDING" not in line:
            in_built = False
            in_pending = False

        if line.strip().startswith("|") and "|" in line[1:]:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and parts[1] and parts[1] != "Component" and "---" not in parts[1]:
                label = parts[1].lower()
                if in_built:
                    built_items.add(label)
                elif in_pending:
                    pending_items.add(label)

    # Check for items in both BUILT and PENDING
    duplicates = built_items & pending_items
    for dup in sorted(duplicates):
        findings.append(_make_finding(
            "STATUS_CONTRADICTION", "medium",
            f"Item '{dup}' appears in both BUILT and PENDING sections",
            f"Found in both STATUS.md BUILT and PENDING",
            "Remove from PENDING if truly built, or from BUILT if still incomplete"
        ))

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# STRATEGY 4 — MOT Freshness Check
# ─────────────────────────────────────────────────────────────────────────────

def strategy_4_mot_freshness():
    findings = []

    # Check last MOT run from mcc_full_mot.py modification time
    if MCC_MOT.exists():
        mtime = MCC_MOT.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        if age_hours > 48:
            findings.append(_make_finding(
                "STALE_MOT", "medium",
                f"mcc_full_mot.py has not been modified in {age_hours:.0f} hours",
                f"Last modified: {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')}",
                "Run: python mcc_full_mot.py to get a fresh MOT result"
            ))

    # Check for MOT result in data/
    mot_results = sorted(HERE.glob("health_results/*/mot_report*.json")) + sorted(HERE.glob("data/mot_report*.json"))
    if mot_results:
        latest = mot_results[-1]
        try:
            mot = json.loads(latest.read_text(encoding="utf-8"))
            score = mot.get("score", mot.get("passed", None))
            total = mot.get("total", 108)
            if score is not None and score != total:
                findings.append(_make_finding(
                    "MOT_FAILURE", "high",
                    f"Last MOT run had failures: {score}/{total}",
                    f"Report: {latest.name}",
                    "Run python mcc_full_mot.py and fix all failing checks"
                ))
        except Exception:
            pass

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# STRATEGY 5 — Session Log Cross-Check
# ─────────────────────────────────────────────────────────────────────────────

def strategy_5_session_log_cross_check():
    findings = []
    if not SESSION_DIR.exists():
        return findings

    if not STATUS_FILE.exists():
        return findings

    status_text = STATUS_FILE.read_text(encoding="utf-8", errors="ignore").lower()

    # Keywords that signal "this was built" in session logs
    built_signals = [
        r'✅\s*(.{10,80})',        # checkmark lines
        r'completed?:\s*(.{10,80})',
        r'built?:\s*(.{10,80})',
        r'added?:\s*(.{10,80})',
        r'created?:\s*(.{10,80})',
        r'phase \d+.*?(?:complete|done|pass)',
    ]

    # Only check recent session logs (last 10)
    session_files = sorted(SESSION_DIR.glob("*.md"))[-10:]
    mentioned_built = {}  # label -> session file

    for sf in session_files:
        try:
            content = sf.read_text(encoding="utf-8", errors="ignore")
            for pat in built_signals:
                for m in re.finditer(pat, content, re.IGNORECASE):
                    label = m.group(0)[:60].strip().lower()
                    label = re.sub(r'[^\w\s/.-]', '', label)[:40].strip()
                    if len(label) > 8:
                        mentioned_built[label] = sf.name
        except Exception:
            pass

    missing_count = 0
    for label, session in mentioned_built.items():
        # Check if any significant keyword from the label appears in STATUS.md
        words = [w for w in label.split() if len(w) > 5]
        if not words:
            continue
        if not any(w in status_text for w in words[:2]):
            missing_count += 1
            if missing_count <= 5:  # Limit to 5 findings
                findings.append(_make_finding(
                    "MISSING_FROM_STATUS", "low",
                    f"Session log '{session}' mentions built work not found in STATUS.md",
                    f"Label: '{label}'",
                    f"Check session log {session} and add the item to STATUS.md BUILT section"
                ))

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# STRATEGY 6 — DOM Element Verifier
# ─────────────────────────────────────────────────────────────────────────────

def strategy_6_dom_verifier():
    findings = []
    if not MCC_HTML.exists() or not STATUS_FILE.exists():
        return findings

    html_text = MCC_HTML.read_text(encoding="utf-8", errors="ignore")
    status_text = STATUS_FILE.read_text(encoding="utf-8", errors="ignore")

    # Tab IDs claimed in STATUS.md vs what exists in HTML
    # Known tab IDs from the HTML
    html_tab_ids = set(re.findall(r'id="tab-([\w-]+)"', html_text))

    # Key component element IDs that should exist
    required_elements = [
        "hisav-accordion",      # HISAV tab
        "hisav-tl",             # Vehicle History timeline
        "ocb-input",            # OCB Runner
        "ai-status-bar",        # AI Status Bar
        "llow-canvas",          # LLOW canvas
        "hs-pane-selfdiag",     # Health Suite self-diagnosis
        "acca-ticker-bar",      # ACCA ticker
        "hisav-body-s1",        # HISAV section 1
        "hisav-body-s3",        # HISAV section 3 (timeline)
    ]

    for elem_id in required_elements:
        if f'id="{elem_id}"' not in html_text and f"id='{elem_id}'" not in html_text:
            findings.append(_make_finding(
                "PHANTOM_UI", "medium",
                f"Expected element id='{elem_id}' not found in mission_control.html",
                f"Searched mission_control.html for id=\"{elem_id}\"",
                f"Check if element was removed or ID was renamed in a recent OCB"
            ))

    # Check that all HISAV sections 1-9 have their body divs
    for i in range(1, 10):
        sid = f"hisav-body-s{i}"
        if f'id="{sid}"' not in html_text:
            findings.append(_make_finding(
                "PHANTOM_UI", "medium",
                f"HISAV section {i} body (id='{sid}') missing from HTML",
                f"id='{sid}' not found",
                f"Add Section {i} to HISAV accordion"
            ))

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────────

def run_all_strategies():
    print("[Detective] Starting 6-strategy scan…", flush=True)
    report = _load_report()

    # Preserve dismissed findings
    dismissed = {f["id"]: f for f in report.get("findings", []) if f.get("status") == "dismissed"}
    fixed     = {f["id"]: f for f in report.get("findings", []) if f.get("status") == "fixed"}

    new_findings = []
    for i, fn in enumerate([
        strategy_1_file_exists,
        strategy_2_endpoint_health,
        strategy_3_status_cross_check,
        strategy_4_mot_freshness,
        strategy_5_session_log_cross_check,
        strategy_6_dom_verifier,
    ], 1):
        try:
            print(f"[Detective] Strategy {i}…", flush=True)
            results = fn()
            new_findings.extend(results)
            print(f"[Detective] Strategy {i} → {len(results)} finding(s)", flush=True)
        except Exception as exc:
            print(f"[Detective] Strategy {i} ERROR: {exc}", flush=True)

    # Merge: keep dismissed/fixed, add new open findings
    all_findings = list(dismissed.values()) + list(fixed.values()) + new_findings

    summary = {
        "total_findings": len(all_findings),
        "high": sum(1 for f in all_findings if f.get("severity") == "high"),
        "medium": sum(1 for f in all_findings if f.get("severity") == "medium"),
        "low": sum(1 for f in all_findings if f.get("severity") == "low"),
        "ghosts": sum(1 for f in all_findings if f.get("type") == "GHOST_FILE"),
        "dead_endpoints": sum(1 for f in all_findings if f.get("type") == "DEAD_ENDPOINT"),
    }

    report = {
        "last_run": _now(),
        "run_count": report.get("run_count", 0) + 1,
        "findings": all_findings,
        "summary": summary,
    }
    _save_report(report)
    print(f"[Detective] Done. {summary['total_findings']} findings ({summary['high']} high). Report: {REPORT_PATH}", flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description="HISAV Detective — 6-strategy project validator")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--watch", action="store_true", help="Run every 5 minutes continuously")
    args = parser.parse_args()

    if args.watch:
        print("[Detective] Watch mode — running every 5 minutes. Ctrl+C to stop.", flush=True)
        while True:
            run_all_strategies()
            time.sleep(300)
    else:
        # Default: run once
        run_all_strategies()


if __name__ == "__main__":
    main()
