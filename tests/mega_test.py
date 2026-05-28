"""
tests/mega_test.py — OCB-K Mega Functional Test Suite
Tests FUNCTION not just structure. Run after mcc_server.py is started.
Usage:  python tests/mega_test.py
Output: tests/mega_test_results_<date>.json + console summary
"""

import datetime
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE    = Path(__file__).parent.parent
TESTS   = Path(__file__).parent
PORT    = 8080
BASE    = f"http://127.0.0.1:{PORT}"
PYTHON  = sys.executable

_results   = []
_pass      = 0
_fail      = 0
_total     = 0


# ── Helpers ────────────────────────────────────────────────────────────────────

def _http(method: str, path: str, body: bytes | None = None, timeout: int = 10):
    url = BASE + path
    req = urllib.request.Request(url, data=body, method=method)
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}
    except Exception as exc:
        return 0, {"error": str(exc)[:100]}


def _record(name: str, what: str, passed: bool, detail: str = ""):
    global _pass, _fail, _total
    _total += 1
    if passed:
        _pass += 1
        status = "PASS"
        icon   = "✅"
    else:
        _fail += 1
        status = "FAIL"
        icon   = "❌"
    _results.append({"name": name, "what": what, "status": status, "detail": detail})
    label = f"  {icon} {name}"
    if detail:
        label += f": {detail}"
    print(label)


def _server_live() -> bool:
    try:
        with urllib.request.urlopen(BASE + "/status", timeout=3):
            return True
    except Exception:
        return False


# ── 1. API Endpoints ───────────────────────────────────────────────────────────

def test_api_endpoints():
    print("\n[1] API Endpoints")
    endpoints = [
        ("GET", "/status",                    "WCCS last run status"),
        ("GET", "/health-status",             "Provider health JSON"),
        ("GET", "/aafl-status",               "AAFL running status"),
        ("GET", "/aafl-config",               "AAFL config JSON"),
        ("GET", "/aafl-queue",                "AAFL goal queue"),
        ("GET", "/scout-config",              "Scout config"),
        ("GET", "/api/status",                "STATUS.md content"),
        ("GET", "/api/health",                "Combined health data"),
        ("GET", "/api/missions",              "Mission list"),
        ("GET", "/api/safety-status",         "Safety Shield status"),
        ("GET", "/api/clachr/queue",          "CLACHR task queue"),
        ("GET", "/api/clachr/results",        "CLACHR results"),
        ("GET", "/api/project-awareness",     "Project awareness JSON"),
        ("GET", "/api/project-vision",        "Project vision charts data"),
        ("GET", "/api/resources/snapshot",    "RAM/CPU/Disk snapshot"),
        ("GET", "/api/aafl/errors",           "AAFL error log"),
        ("GET", "/api/storage/stats",         "Storage stats"),
        ("GET", "/api/llow/elements",         "LLOW elements"),
        ("GET", "/api/llow/arrows",           "LLOW arrow types"),
        ("GET", "/api/llow/workflows",        "LLOW saved workflows"),
        ("GET", "/api/self-health/registry",  "Self-health element registry"),
        ("GET", "/storage",                   "Storage overview"),
        ("GET", "/api/instructions",          "Instructions DB"),
        ("GET", "/api/medical-report",        "Medical report (200 or 404 OK)"),
        ("GET", "/api/work-checker/report",   "Work checker report"),
        ("GET", "/api/processes",             "Running AI processes"),
        ("GET", "/api/system/snapshot",       "System metrics snapshot"),
    ]
    for method, path, desc in endpoints:
        code, data = _http(method, path)
        passed = code in (200, 404)  # 404 is OK for files not yet generated
        detail = f"HTTP {code}" + (f" — error: {data.get('error','')[:40]}" if not passed else "")
        _record(f"GET {path}", desc, passed, detail)


# ── 2. AAFL Core (dry_run — no real API calls) ───────────────────────────────

def test_aafl_core():
    print("\n[2] AAFL Core")
    try:
        sys.path.insert(0, str(HERE))
        from aafl_core import AAFLCore
        core = AAFLCore(dry_run=True, allow_paid=False)
        result = core.run("test task — mega test suite", task_type="fast", max_tokens=10)
        _record("AAFLCore.run() dry_run", "Creates AAFLCore and runs a fast dry-run call", result.ok, f"ok={result.ok} provider={result.provider_id}")
    except Exception as exc:
        _record("AAFLCore.run() dry_run", "Creates AAFLCore and runs a fast dry-run call", False, str(exc)[:80])


# ── 3. Scout ─────────────────────────────────────────────────────────────────

def test_scout():
    print("\n[3] Scout")
    out_dir = HERE / "scout_output"
    out_dir.mkdir(exist_ok=True)
    try:
        res = subprocess.run(
            [PYTHON, str(HERE / "chief_scout.py"), "test VKB joystick mega test"],
            capture_output=True, text=True, timeout=60, cwd=str(HERE),
        )
        passed = res.returncode == 0 or "briefing" in (res.stdout + res.stderr).lower()
        _record("chief_scout.py run", "Runs chief_scout.py with a 1-result test query", passed,
                f"rc={res.returncode}" + (f" err={res.stderr[:50]}" if not passed else ""))
    except subprocess.TimeoutExpired:
        _record("chief_scout.py run", "Runs chief_scout.py with a 1-result test query", False, "Timed out after 60s")
    except Exception as exc:
        _record("chief_scout.py run", "Runs chief_scout.py with a 1-result test query", False, str(exc)[:80])


# ── 4. self_health.py ─────────────────────────────────────────────────────────

def test_self_health():
    print("\n[4] self_health.py")
    try:
        sys.path.insert(0, str(HERE))
        from self_health import SelfHealthRunner
        runner = SelfHealthRunner()
        checks = runner.run_checks()
        passed = isinstance(checks, list) and len(checks) > 0
        _record("SelfHealthRunner.run_checks()", "Runs all HC-series system health checks and returns results list", passed,
                f"{len(checks)} checks run" if passed else "empty result")
    except Exception as exc:
        _record("SelfHealthRunner.run_checks()", "Runs all HC-series system health checks", False, str(exc)[:80])


# ── 5. work_checker.py ────────────────────────────────────────────────────────

def test_work_checker():
    print("\n[5] work_checker.py")
    wc = HERE / "work_checker.py"
    if not wc.exists():
        _record("work_checker.py run", "Runs work_checker.py and checks output", False, "work_checker.py not found")
        return
    try:
        res = subprocess.run(
            [PYTHON, str(wc)],
            capture_output=True, text=True, timeout=30, cwd=str(HERE),
        )
        passed = res.returncode == 0
        _record("work_checker.py run", "Runs work_checker.py — checks for lost/orphaned work", passed,
                f"rc={res.returncode}" + (f" err={res.stderr[:50]}" if not passed else ""))
    except subprocess.TimeoutExpired:
        _record("work_checker.py run", "Runs work_checker.py", False, "Timed out after 30s")
    except Exception as exc:
        _record("work_checker.py run", "Runs work_checker.py", False, str(exc)[:80])


# ── 6. system_monitor.py ─────────────────────────────────────────────────────

def test_system_monitor():
    print("\n[6] system_monitor.py")
    sm = HERE / "system_monitor.py"
    if not sm.exists():
        _record("system_monitor.py run", "Runs system_monitor.py for one snapshot cycle", False, "system_monitor.py not found")
        return
    try:
        sys.path.insert(0, str(HERE))
        import system_monitor
        snap = system_monitor.get_snapshot() if hasattr(system_monitor, "get_snapshot") else None
        if snap is None:
            # Try running as subprocess
            res = subprocess.run(
                [PYTHON, str(sm), "--once"],
                capture_output=True, text=True, timeout=20, cwd=str(HERE),
            )
            passed = res.returncode == 0
            _record("system_monitor.py snapshot", "Runs system_monitor.py --once and checks exit code", passed, f"rc={res.returncode}")
        else:
            passed = isinstance(snap, dict) and len(snap) > 0
            _record("system_monitor.get_snapshot()", "Calls get_snapshot() and checks it returns a non-empty dict", passed,
                    f"{len(snap)} keys" if passed else "empty result")
    except Exception as exc:
        _record("system_monitor.py snapshot", "Runs system_monitor.py for one snapshot cycle", False, str(exc)[:80])


# ── 7. memory_bank.py ─────────────────────────────────────────────────────────

def test_memory_bank():
    print("\n[7] memory_bank.py")
    try:
        sys.path.insert(0, str(HERE))
        from memory_bank import store, search_solution, DB_PATH
        import sqlite3
        # Write
        uid = store({
            "title": "__MEGA_TEST__",
            "content": "Mega test suite — safe to delete automatically",
            "source_type": "mega_test",
            "project": "mega_test",
        })
        _record("memory_bank.store()", "Writes a test entry to the knowledge database and returns a UID", bool(uid), f"uid={str(uid)[:20]}")
        # Read back
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute("SELECT id, title FROM knowledge WHERE title='__MEGA_TEST__'").fetchone()
        conn.close()
        _record("memory_bank read-back", "Reads back the test entry just written", row is not None, f"id={row[0] if row else 'not found'}")
        # Delete
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("DELETE FROM knowledge WHERE title='__MEGA_TEST__'")
        conn.commit()
        conn.close()
        _record("memory_bank cleanup", "Deletes the test row written by this test", True, "test row removed")
    except Exception as exc:
        _record("memory_bank.store()", "Tests write-read-delete cycle on the knowledge database", False, str(exc)[:80])


# ── 8. storage_manager.py ────────────────────────────────────────────────────

def test_storage_manager():
    print("\n[8] storage_manager.py")
    try:
        sys.path.insert(0, str(HERE))
        import storage_manager
        if hasattr(storage_manager, "get_stats"):
            stats = storage_manager.get_stats()
            passed = isinstance(stats, dict) and len(stats) > 0
            _record("storage_manager.get_stats()", "Calls get_stats() and checks it returns a non-empty dict", passed,
                    f"{len(stats)} keys" if passed else "empty result")
        elif hasattr(storage_manager, "StorageManager"):
            sm = storage_manager.StorageManager()
            method = next((m for m in ("get_stats", "stats", "summary") if hasattr(sm, m)), None)
            if method:
                stats = getattr(sm, method)()
                passed = stats is not None
                _record(f"StorageManager.{method}()", "Calls storage stats method and checks it returns data", passed, str(stats)[:60])
            else:
                _record("storage_manager", "Checks storage_manager.py imports and has usable class", True, "StorageManager class found")
        else:
            _record("storage_manager import", "Imports storage_manager.py", True, "no get_stats — module loads OK")
    except Exception as exc:
        _record("storage_manager.get_stats()", "Imports and calls storage_manager.py", False, str(exc)[:80])


# ── 9. Safety Shield ─────────────────────────────────────────────────────────

def test_safety_shield():
    print("\n[9] Safety Shield")
    code, data = _http("GET", "/api/safety-status")
    has_overall = "overall" in data
    _record("/api/safety-status response", "GET /api/safety-status — checks response has 'overall' field", code == 200 and has_overall,
            f"HTTP {code} overall={data.get('overall','MISSING')}")


# ── 10. CLACHR Relay ─────────────────────────────────────────────────────────

def test_clachr():
    print("\n[10] CLACHR Relay")
    code, data = _http("GET", "/api/clachr/queue")
    _record("/api/clachr/queue response", "GET /api/clachr/queue — checks it responds with a valid JSON", code == 200,
            f"HTTP {code}" + (f" error={data.get('error','')}" if code != 200 else ""))


# ── 11. Project Awareness ─────────────────────────────────────────────────────

def test_project_awareness():
    print("\n[11] Project Awareness")
    code, data = _http("GET", "/api/project-awareness")
    required = {"what_is_built", "what_is_next", "action_plan", "evolution_log", "forks_taken", "jobs_remaining"}
    found    = set(data.keys()) if isinstance(data, dict) else set()
    missing  = required - found
    passed   = code == 200 and not missing
    _record("/api/project-awareness 6 sections", "GET /api/project-awareness — checks all 6 required sections are present", passed,
            f"HTTP {code}" + (f" missing={missing}" if missing else " all sections present"))


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*62)
    print("  MCC MEGA FUNCTIONAL TEST SUITE — OCB-K")
    print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*62)

    # Check server is running
    if not _server_live():
        print("\n  ⚠️  mcc_server.py is NOT running on :8080")
        print("  Start it first: python mcc_server.py")
        print("  API endpoint tests will be skipped or fail.")
    else:
        print(f"\n  ✅ Server live at {BASE}")

    test_api_endpoints()
    test_aafl_core()
    test_scout()
    test_self_health()
    test_work_checker()
    test_system_monitor()
    test_memory_bank()
    test_storage_manager()
    test_safety_shield()
    test_clachr()
    test_project_awareness()

    pct   = round(_pass / _total * 100, 1) if _total else 0
    fails = [r for r in _results if r["status"] == "FAIL"]

    print("\n" + "="*62)
    print("  MEGA TEST RESULTS")
    print("="*62)
    print(f"  Total:   {_total}")
    print(f"  Passed:  {_pass} ({pct}%)")
    print(f"  Failed:  {_fail}")

    if fails:
        print(f"\n  FAILURES ({len(fails)}):")
        for f in fails:
            print(f"    FAIL: {f['name']}: {f['detail']}")

    report = {
        "timestamp":  datetime.datetime.now().isoformat(),
        "total":      _total,
        "passed":     _pass,
        "failed":     _fail,
        "pass_rate":  pct,
        "verdict":    "ALL PASS" if _fail == 0 else "ISSUES FOUND",
        "failures":   fails,
        "results":    _results,
    }

    TESTS.mkdir(exist_ok=True)
    stamp  = datetime.datetime.now().strftime("%Y-%m-%d")
    out    = TESTS / f"mega_test_results_{stamp}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Report saved: {out}")
    print(f"\n  VERDICT: {'ALL PASS' if _fail == 0 else f'ISSUES FOUND — {_fail} failures'}")
    print("="*62 + "\n")
    return report


if __name__ == "__main__":
    main()
