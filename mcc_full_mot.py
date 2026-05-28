"""
mcc_full_mot.py — Full System MOT (Ministry of Transport test)
Tests all groups: file existence, imports, HTML structure, server endpoints,
home cards, provider health, AAFL core, data integrity.
Writes report to health_results/full_mot_report.json
Run: python mcc_full_mot.py
"""

import importlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

HERE       = Path(__file__).parent
HEALTH_DIR = HERE / "health_results"

_results   = []
_total     = 0
_passed    = 0
_failed    = 0
_LIVE_MODE = False   # set True by --live flag


def _pre(name: str, desc: str):
    """Print the 'Checking...' line before a test runs (--live mode only)."""
    if _LIVE_MODE:
        print(f"Checking {name}: {desc}...", flush=True)


def _record(group, name, passed, detail=""):
    global _total, _passed, _failed
    _total += 1
    if passed:
        _passed += 1
        status = "PASS"
    else:
        _failed += 1
        status = "FAIL"
    _results.append({"group": group, "name": name, "status": status, "detail": detail})
    if _LIVE_MODE:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {status}: {detail or 'OK'}", flush=True)
    else:
        icon = "OK" if passed else "XX"
        msg  = f"  [{icon}] {name}"
        if detail:
            msg += f": {detail}"
        print(msg)


def _hdr(name):
    if not _LIVE_MODE:
        print(f"\n{'='*62}")
        print(f"  {name}")
    print("="*62)


# ── GROUP A — File existence ─────────────────────────────────────────────────

def test_group_a():
    _hdr("GROUP A — File Existence")

    # .py files listed in STATUS.md BUILT AND WORKING
    py_files = [
        "spin_doctor.py", "sfl_agent.py", "aafl_core.py", "loop_manager.py",
        "evaluator.py", "researcher.py", "memory_bank.py", "meta_loop.py",
        "chief_scout.py", "mcu_optimizer.py", "dashboard_builder.py",
        "task_router.py", "aafl_wccs.py", "aafl_watchdog.py", "cost_guard.py",
        "merge_sessions.py", "queue_runner.py", "mcc_server.py",
        "problems/conductor.py", "problems/win_hardener.py",
        "problems/ed_bind_reset.py",
    ]
    for f in py_files:
        path = HERE / f
        _pre(f"File: {f}", f"Tests that {f} exists on disk")
        _record("A", f"File: {f}", path.exists(),
                "exists" if path.exists() else "MISSING")

    # Docs
    for doc in ["INDEX.md", "STATUS.md", "HISTORY.md", "ACCA.md", "ALP_Database.md"]:
        path = HERE / doc
        _pre(f"Doc: {doc}", f"Tests that {doc} exists in the project root")
        _record("A", f"Doc: {doc}", path.exists(),
                "exists" if path.exists() else "MISSING")

    # Folders
    for folder in ["health_results", "dashboard_data", "session_logs", "archive_dead"]:
        path = HERE / folder
        _pre(f"Folder: {folder}/", f"Tests that {folder}/ directory exists")
        _record("A", f"Folder: {folder}/", path.is_dir(),
                "exists" if path.is_dir() else "MISSING")


# ── GROUP B — Python imports ─────────────────────────────────────────────────

def _import_test(mod_name):
    """Test import by spawning subprocess — avoids polluting current process."""
    try:
        res = subprocess.run(
            [sys.executable, "-c", f"import sys; sys.path.insert(0,r'{HERE}'); import {mod_name}"],
            capture_output=True, text=True, timeout=15, cwd=str(HERE),
        )
        if res.returncode == 0:
            return True, "OK"
        err = (res.stderr or "").strip().split("\n")[-1][:100]
        return False, err
    except subprocess.TimeoutExpired:
        return False, "Timed out after 15s"
    except Exception as e:
        return False, str(e)[:80]


def test_group_b():
    _hdr("GROUP B — Python Imports")
    modules = [
        "aafl_core", "loop_manager", "evaluator", "researcher",
        "memory_bank", "meta_loop", "chief_scout", "mcu_optimizer",
        "dashboard_builder", "task_router", "provider_health",
        "spin_doctor", "sfl_agent",
    ]
    for mod in modules:
        _pre(f"import {mod}", f"Verifies {mod}.py loads in Python without import errors")
        ok, detail = _import_test(mod)
        _record("B", f"import {mod}", ok, detail)


# ── GROUP C — MCC HTML Structure ─────────────────────────────────────────────

class _HtmlScanner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tabs_found   = set()
        self.element_ids  = set()
        self.all_classes  = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get("data-tab"):
            self.tabs_found.add(d["data-tab"])
        if d.get("id"):
            self.element_ids.add(d["id"])
        for cls in (d.get("class") or "").split():
            self.all_classes.add(cls)


def test_group_c():
    _hdr("GROUP C — MCC HTML Structure")
    html_path = HERE / "mission_control.html"
    if not html_path.exists():
        _record("C", "mission_control.html", False, "MISSING"); return

    content = html_path.read_text(encoding="utf-8", errors="replace")
    scanner = _HtmlScanner()
    try:
        scanner.feed(content)
    except Exception:
        pass

    # Required tabs
    tab_checks = {
        "home":          "Home",
        "kanban":        "Kanban",
        # "aafl-runs" tab merged into AAFL Control in Build 5 — no longer a standalone tab
        "costs":         "Costs",
        "scout":         "Scout Control",
        "aafl-control":  "AAFL Control",
        "wccs":          "WCCS",
        "health-suite":  "Health Suite",
        "acca":          "ACCA",
    }
    for tab_id, label in tab_checks.items():
        found = tab_id in scanner.tabs_found
        _pre(f"Tab: {label}", f"Verifies the {label} tab (data-tab={tab_id}) exists in mission_control.html")
        _record("C", f"Tab: {label}", found, "found" if found else "MISSING")

    # 10 features — static IDs where possible, JS search for dynamic elements
    feature_ids = {
        "stuck-inbox-list":  "Stuck Inbox",
        "btn-run-now":       "Run Now button",
        "cost-preview":      "Cost Predictor",
        "tab-memory":        "Memory Inspector",
        "tab-promo":         "Promo Queue",
        "tab-acca":          "ACCA Tab",
        "alp-entry-input":   "ALP Counter (merged into AAFL Control)",
        "kb-overlay":        "Keyboard Shortcuts",
        "hs-pane-provider":  "Provider Health (in Health Suite)",
        "wpanel-activity":   "Activity Feed (in WCCS)",
    }
    for el_id, label in feature_ids.items():
        found = el_id in scanner.element_ids
        _pre(f"Feature: {label}", f"Checks that HTML element id='{el_id}' ({label}) is present")
        _record("C", f"Feature: {label}", found, "found" if found else "MISSING")

    undo_found = "showUndoToast" in content or "undo_stack" in content
    _pre("Feature: Undo system", "Searches for showUndoToast or undo_stack JavaScript function in HTML")
    _record("C", "Feature: Undo system", undo_found, "JS function found" if undo_found else "MISSING")

    sunday_found = any(kw in content for kw in ("sunday-merge", "merge_sessions", "SundayMerge", "runSundayMerge"))
    _pre("Feature: Sunday Merge", "Searches for Sunday auto-merge keyword in HTML")
    _record("C", "Feature: Sunday Merge", sunday_found, "keyword found" if sunday_found else "MISSING")

    save_features = {
        "api/timeline":  "Save Timeline",
        "tab-rewind":    "Rewind panel",
        "tab-diff":      "Diff Viewer",
        "tab-sessions":  "Session Log Browser",
        "tab-search":    "HISTORY Search",
        "auto-toggle":   "Auto-WCCS Toggle",
        "btn-wccs-hub":  "WCCS Save button",
    }
    for key, label in save_features.items():
        found = key in content
        _pre(f"Save Feature: {label}", f"Checks that '{key}' keyword is referenced in the HTML")
        _record("C", f"Save Feature: {label}", found, "found" if found else "MISSING")


# ── GROUP D — MCC Server Endpoints ───────────────────────────────────────────

def _port_busy(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("localhost", port)) == 0


def _get(url, expect_json=True, timeout=6):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            status = r.status
            body   = r.read().decode("utf-8", errors="replace")
            if expect_json:
                data = json.loads(body)
                return status, True, data
            return status, True, body
    except urllib.error.HTTPError as e:
        return e.code, False, f"HTTP {e.code}"
    except Exception as e:
        return 0, False, str(e)[:80]


def test_group_d():
    _hdr("GROUP D — MCC Server Endpoints")
    PORT = 8080
    proc = None
    started = False

    if not _port_busy(PORT):
        print(f"  Starting mcc_server.py on :{PORT}…")
        try:
            proc = subprocess.Popen(
                [sys.executable, str(HERE / "mcc_server.py")],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                cwd=str(HERE),
            )
            time.sleep(3)
            started = True
        except Exception as e:
            _record("D", "Server startup", False, str(e)); return
    else:
        print(f"  Port {PORT} already in use — testing existing server.")

    try:
        base = f"http://localhost:{PORT}"

        # / → HTML
        _pre("GET / (HTML)", "Requests the root URL and checks MCC HTML is returned correctly")
        code, ok, body = _get(base + "/", expect_json=False)
        html_ok = code == 200 and ok and "#!/usr/bin" not in str(body)
        _record("D", "GET / (HTML)", html_ok, f"HTTP {code}")

        # JSON endpoints
        for path in ["/health-status", "/dashboard-data/", "/status"]:
            _pre(f"GET {path} (JSON)", f"Tests that the {path} endpoint returns HTTP 200 with valid JSON")
            code, ok, data = _get(base + path, expect_json=True)
            passed = code == 200 and ok
            _record("D", f"GET {path} (JSON)", passed, f"HTTP {code}")

        # dashboard-data files (200 or 404 both acceptable)
        for fname in ["kanban.json", "costs.json"]:
            _pre(f"GET /dashboard-data/{fname}", f"Checks the dashboard data file {fname} is accessible (200 or 404 both OK)")
            code, ok, _ = _get(base + f"/dashboard-data/{fname}", expect_json=True)
            passed = code in (200, 404)
            _record("D", f"GET /dashboard-data/{fname}", passed, f"HTTP {code}")

    finally:
        if started and proc:
            proc.terminate()
            try:
                proc.wait(timeout=4)
            except Exception:
                proc.kill()
            print("  Server stopped.")


# ── GROUP E — Home Screen Cards ──────────────────────────────────────────────

def test_group_e():
    _hdr("GROUP E — Home Screen Cards")
    html_path = HERE / "mission_control.html"
    if not html_path.exists():
        _record("E", "mission_control.html", False, "MISSING"); return

    content = html_path.read_text(encoding="utf-8", errors="replace")

    card_defs = [
        ("provider_health.json", "providerhealth", "Provider Health"),
        ("aafl_runs.json",       "aafl-runs",      "AAFL Last Run"),
        ("scout.json",           "scout",          "Scout Status"),
        ("kanban.json",          "kanban",         "Kanban Summary"),
        ("costs.json",           "costs",          "Cost Today"),
        ("wccs.json",            "wccs",           "WCCS Last Save"),
        ("aafl_control.json",    "aafl-control",   "AAFL Control"),
    ]
    for fname, tab_id, label in card_defs:
        in_js   = fname in content and tab_id in content
        on_disk = (HERE / "dashboard_data" / fname).exists()
        _pre(f"Card JS ref: {label}", f"Verifies JavaScript references {fname} and tab '{tab_id}' for the {label} home card")
        _record("E", f"Card JS ref: {label}", in_js,
                "referenced" if in_js else "missing from JS")
        _pre(f"Card data file: {fname}", f"Checks that dashboard_data/{fname} exists on disk")
        _record("E", f"Card data file: {fname}", on_disk,
                "exists" if on_disk else "MISSING")

    slot_found = "home-card slot" in content and "for (let i = 0; i < 3" in content
    _pre("3 empty slot cards (JS loop)", "Checks the JS loop that renders 3 empty home card slots exists in HTML")
    _record("E", "3 empty slot cards (JS loop)", slot_found,
            "JS loop found" if slot_found else "MISSING")

    _pre("Cards have onclick navigation", "Checks homeCardClick() JavaScript function is present for card click navigation")
    _record("E", "Cards have onclick navigation", "homeCardClick" in content,
            "found" if "homeCardClick" in content else "MISSING")


# ── GROUP F — Provider Health System ────────────────────────────────────────

def test_group_f():
    _hdr("GROUP F — Provider Health System")
    health_dir = HERE / "health_results"

    _pre("provider_health.py exists", "Tests that the provider health script file is present on disk")
    _record("F", "provider_health.py exists",
            (HERE / "provider_health.py").exists(),
            "exists" if (HERE / "provider_health.py").exists() else "MISSING")

    _pre("health_results/ folder", "Tests that the health_results/ output directory exists")
    _record("F", "health_results/ folder", health_dir.is_dir(),
            "exists" if health_dir.is_dir() else "MISSING")

    latest = health_dir / "latest_health.json"
    if latest.exists():
        try:
            data = json.loads(latest.read_text(encoding="utf-8"))
            n = len(data.get("providers", []))
            _pre("latest_health.json valid JSON", "Parses latest_health.json and counts the provider entries")
            _record("F", "latest_health.json valid JSON", True, f"{n} providers")
        except Exception as e:
            _pre("latest_health.json valid JSON", "Parses latest_health.json — checks it is valid JSON")
            _record("F", "latest_health.json valid JSON", False, str(e)[:60])
    else:
        _pre("latest_health.json exists", "Checks latest_health.json has been generated by running provider_health.py")
        _record("F", "latest_health.json exists", False, "run provider_health.py first")

    for fname in ["tier1_results.json", "tier2_results.json",
                  "tier3_results.json", "cost_log.csv"]:
        path = health_dir / fname
        _pre(fname, f"Checks that health_results/{fname} exists after a provider health run")
        _record("F", fname, path.exists(), "exists" if path.exists() else "MISSING")


# ── GROUP G — AAFL Core ──────────────────────────────────────────────────────

def test_group_g():
    _hdr("GROUP G — AAFL Core")

    _pre("task_router.classify()", "Calls classify() with a test goal and checks it returns a valid routing tier (AAFL/CLAC/SONNET/OPUS)")
    try:
        sys.path.insert(0, str(HERE))
        from task_router import classify
        res = classify("search the web for joystick spin fix information")
        ok  = "tier" in res and res["tier"] in ("AAFL", "CLAC", "SONNET", "OPUS")
        _record("G", "task_router.classify()", ok, f"tier={res.get('tier','?')}")
    except Exception as e:
        _record("G", "task_router.classify()", False, str(e)[:80])

    # evaluator.evaluate
    _pre("evaluator.evaluate()", "Calls evaluate() with a test result string and checks it returns a numeric score")
    try:
        from evaluator import evaluate
        sc = evaluate("This is a test result about joystick spin fix", "joystick spin")
        ok = "overall" in sc and isinstance(sc["overall"], (int, float))
        _record("G", "evaluator.evaluate()", ok, f"score={sc.get('overall','?')}")
    except Exception as e:
        _record("G", "evaluator.evaluate()", False, str(e)[:80])

    _pre("memory_bank.store()", "Writes a test entry to the knowledge database, verifies it gets a UID, then deletes it")
    try:
        from memory_bank import store, DB_PATH as MB_DB
        uid = store({
            "title":       "__MOT_TEST__",
            "content":     "Automated MOT test row -- safe to delete.",
            "source_type": "mot_test",
            "project":     "mot",
        })
        _record("G", "memory_bank.store()", bool(uid), f"uid={str(uid)[:16]}")
        import sqlite3
        conn = sqlite3.connect(str(MB_DB))
        conn.execute("DELETE FROM knowledge WHERE title = '__MOT_TEST__'")
        conn.commit()
        conn.close()
        _pre("memory_bank cleanup", "Deletes the test row written by the store() check above")
        _record("G", "memory_bank cleanup", True, "test row removed")
    except Exception as e:
        _record("G", "memory_bank.store()", False, str(e)[:80])

    _pre("researcher.research() exists", "Checks that researcher.py exports a callable research() function")
    try:
        from researcher import research
        _record("G", "researcher.research() exists", callable(research), "callable")
    except Exception as e:
        _record("G", "researcher.research() exists", False, str(e)[:80])


# ── GROUP H — Data Integrity ─────────────────────────────────────────────────

def test_group_h():
    _hdr("GROUP H — Data Integrity")

    index = HERE / "INDEX.md"
    if index.exists():
        txt = index.read_text(encoding="utf-8", errors="replace")
        _pre("INDEX.md has RESUME COMMAND", "Searches INDEX.md for the RESUME COMMAND section — required for session restarts")
        _record("H", "INDEX.md has RESUME COMMAND",
                "RESUME COMMAND" in txt,
                "found" if "RESUME COMMAND" in txt else "MISSING")
    else:
        _pre("INDEX.md has RESUME COMMAND", "Checks INDEX.md exists and contains the RESUME COMMAND")
        _record("H", "INDEX.md has RESUME COMMAND", False, "INDEX.md missing")

    status = HERE / "STATUS.md"
    if status.exists():
        txt = status.read_text(encoding="utf-8", errors="replace")
        _pre("STATUS.md has NEXT PRIORITIES", "Searches STATUS.md for NEXT PRIORITIES section — confirms the file is complete")
        _record("H", "STATUS.md has NEXT PRIORITIES",
                "NEXT PRIORITIES" in txt,
                "found" if "NEXT PRIORITIES" in txt else "MISSING")
        _pre("STATUS.md has WHO IS SCOTT", "Searches STATUS.md for WHO IS SCOTT section — confirms BI rules are present")
        _record("H", "STATUS.md has WHO IS SCOTT",
                "WHO IS SCOTT" in txt,
                "found" if "WHO IS SCOTT" in txt else "MISSING")
    else:
        _pre("STATUS.md has NEXT PRIORITIES", "Checks STATUS.md exists and contains NEXT PRIORITIES")
        _record("H", "STATUS.md has NEXT PRIORITIES", False, "STATUS.md missing")
        _pre("STATUS.md has WHO IS SCOTT", "Checks STATUS.md exists and contains WHO IS SCOTT")
        _record("H", "STATUS.md has WHO IS SCOTT", False, "STATUS.md missing")

    alp = HERE / "ALP_Database.md"
    if alp.exists():
        txt  = alp.read_text(encoding="utf-8", errors="replace")
        rows = [
            l for l in txt.splitlines()
            if l.strip().startswith("|")
            and "---" not in l
            and not l.strip().startswith("| #")
            and not l.strip().startswith("| Date")
            and not l.strip().startswith("| Saving")
        ]
        count = len(rows)
        label = "ALP_Database.md >=12 entries (found: " + str(count) + ")"
        _pre(label, "Counts data rows in ALP_Database.md — must have at least 12 Allowance Preservation entries")
        _record("H", label, count >= 12, str(count) + " rows")
    else:
        _pre("ALP_Database.md >=12 entries", "Counts ALP_Database.md entries — file must exist with >=12 rows")
        _record("H", "ALP_Database.md >=12 entries", False, "file missing")


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    global _LIVE_MODE
    import argparse
    parser = argparse.ArgumentParser(description="MCC Full MOT Test Suite")
    parser.add_argument("--live", action="store_true",
                        help="Live mode: print check name+description before each test, then PASS/FAIL after")
    args = parser.parse_args()
    _LIVE_MODE = args.live

    if not _LIVE_MODE:
        print("\n" + "="*62)
        print("  MCC FULL MOT -- Mission Control System Test")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*62)
    else:
        print(f"[LIVE] MCC FULL MOT starting — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print("[LIVE] TOTAL_CHECKS=108", flush=True)

    test_group_a()
    test_group_b()
    test_group_c()
    test_group_d()
    test_group_e()
    test_group_f()
    test_group_g()
    test_group_h()

    pct   = round(_passed / _total * 100, 1) if _total else 0
    fails = [r for r in _results if r["status"] == "FAIL"]

    if _LIVE_MODE:
        print(f"[LIVE] DONE total={_total} passed={_passed} failed={_failed} score={pct}%", flush=True)
        if fails:
            for f in fails:
                hint = f.get("detail", "")
                print(f"[LIVE] FAIL [{f['group']}] {f['name']}: {hint}", flush=True)
        print(f"[LIVE] VERDICT={'ALL CLEAR' if _failed == 0 else 'ISSUES FOUND'}", flush=True)
    else:
        print("\n" + "="*62)
        print("  FINAL MOT REPORT")
        print("="*62)
        print(f"  Total:   {_total}")
        print(f"  Passed:  {_passed} ({pct}%)")
        print(f"  Failed:  {_failed}")

        if fails:
            print(f"\n  FAILURES ({len(fails)}):")
            for f in fails:
                print(f"    [{f['group']}] {f['name']}: {f['detail']}")

    report = {
        "timestamp": datetime.now().isoformat(),
        "total":     _total,
        "passed":    _passed,
        "failed":    _failed,
        "pass_rate": pct,
        "verdict":   "ALL CLEAR" if _failed == 0 else "ISSUES FOUND",
        "failures":  fails,
        "results":   _results,
    }

    HEALTH_DIR.mkdir(exist_ok=True)
    out = HEALTH_DIR / "full_mot_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if not _LIVE_MODE:
        print(f"\n  Report saved: {out}")
        verdict = "ALL CLEAR" if _failed == 0 else f"ISSUES FOUND -- {_failed} failures"
        print(f"\n  VERDICT: {verdict}")
        print("="*62 + "\n")

    return report


if __name__ == "__main__":
    main()
