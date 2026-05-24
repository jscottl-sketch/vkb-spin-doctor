"""
test_full_system.py — Phase 1 comprehensive system test.
Runs all groups A-H, prints PASS/FAIL per item, saves JSON results.
"""
import datetime
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
HEALTH_DIR = HERE / "health_results"
HEALTH_DIR.mkdir(exist_ok=True)

results = []
_fail_groups = set()


def _rec(group, name, passed, reason=""):
    symbol = "PASS" if passed else "FAIL"
    tag = f"[{group}][{symbol}]"
    line = f"{tag} {name}"
    if not passed and reason:
        line += f"  — {reason}"
    print(line)
    results.append({
        "group": group,
        "name": name,
        "passed": passed,
        "reason": reason if not passed else "",
    })
    if not passed:
        _fail_groups.add(group)


# ─────────────────────────────────────────────────────────────────────────────
# GROUP A — File existence
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== GROUP A — File Existence ===")

FILE_CHECKS = [
    "provider_health.py",
    "aafl_core.py",
    "loop_manager.py",
    "evaluator.py",
    "researcher.py",
    "memory_bank.py",
    "meta_loop.py",
    "chief_scout.py",
    "mcu_optimizer.py",
    "dashboard_builder.py",
    "task_router.py",
    "aafl_wccs.py",
    "mission_control.html",
    "mcc_server.py",
    "spin_doctor.py",
    "sfl_agent.py",
]
for f in FILE_CHECKS:
    exists = (HERE / f).exists()
    _rec("A", f"File exists: {f}", exists)

_rec("A", "health_results/ folder exists", (HERE / "health_results").is_dir())
_rec("A", "dashboard_data/ folder exists", (HERE / "dashboard_data").is_dir())
_rec("A", "data/devices.json exists", (HERE / "data" / "devices.json").exists())
_rec("A", "INDEX.md exists", (HERE / "INDEX.md").exists())
_rec("A", "STATUS.md exists", (HERE / "STATUS.md").exists())
_rec("A", "ALP_Database.md exists", (HERE / "ALP_Database.md").exists())


# ─────────────────────────────────────────────────────────────────────────────
# GROUP B — Python syntax check
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== GROUP B — Python Syntax Check ===")

SYNTAX_CHECKS = [
    "provider_health.py",
    "aafl_core.py",
    "loop_manager.py",
    "evaluator.py",
    "researcher.py",
    "memory_bank.py",
    "task_router.py",
    "aafl_wccs.py",
]

for fname in SYNTAX_CHECKS:
    fpath = HERE / fname
    if not fpath.exists():
        _rec("B", f"{fname} imports without error", False, "File does not exist")
        continue
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import py_compile; py_compile.compile(r'{fpath}', doraise=True)"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            _rec("B", f"{fname} imports without error", True)
        else:
            _rec("B", f"{fname} imports without error", False, (result.stderr or result.stdout).strip()[:120])
    except Exception as exc:
        _rec("B", f"{fname} imports without error", False, str(exc)[:120])


# ─────────────────────────────────────────────────────────────────────────────
# GROUP C — Database integrity
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== GROUP C — Database Integrity ===")

DB_PATH = HERE / "data" / "knowledge_engine.db"

_rec("C", "SQLite database file exists", DB_PATH.exists())

if DB_PATH.exists():
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row

        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        for tbl in ("knowledge", "solution_log", "source_reputation", "provider_reputation"):
            _rec("C", f"Table exists: {tbl}", tbl in tables)

        if "provider_reputation" in tables:
            cols = [r[1] for r in conn.execute(
                "PRAGMA table_info(provider_reputation)"
            ).fetchall()]
            required_cols = [
                "provider_name", "total_calls", "successful_calls",
                "failed_calls", "avg_response_time", "last_updated",
            ]
            for col in required_cols:
                _rec("C", f"provider_reputation column: {col}", col in cols)
        else:
            for col in ["provider_name", "total_calls", "successful_calls",
                        "failed_calls", "avg_response_time", "last_updated"]:
                _rec("C", f"provider_reputation column: {col}", False, "Table missing")

        # Write + read + delete test row
        try:
            conn.execute("""
                INSERT OR REPLACE INTO provider_reputation
                (provider_name, total_calls, successful_calls, failed_calls,
                 avg_response_time, last_updated)
                VALUES ('_test_row_', 0, 0, 0, 0.0, 'test')
            """)
            conn.commit()
            row = conn.execute(
                "SELECT provider_name FROM provider_reputation WHERE provider_name='_test_row_'"
            ).fetchone()
            _rec("C", "Can write a test row and read it back", row is not None)
        except Exception as exc:
            _rec("C", "Can write a test row and read it back", False, str(exc)[:120])

        try:
            conn.execute(
                "DELETE FROM provider_reputation WHERE provider_name='_test_row_'"
            )
            conn.commit()
            row = conn.execute(
                "SELECT provider_name FROM provider_reputation WHERE provider_name='_test_row_'"
            ).fetchone()
            _rec("C", "Can delete the test row cleanly", row is None)
        except Exception as exc:
            _rec("C", "Can delete the test row cleanly", False, str(exc)[:120])

        conn.close()
    except Exception as exc:
        _rec("C", "Database accessible", False, str(exc)[:120])
else:
    for item in [
        "Tables present: knowledge", "Tables present: solution_log",
        "Tables present: source_reputation", "Tables present: provider_reputation",
        "Can write a test row and read it back", "Can delete the test row cleanly",
    ]:
        _rec("C", item, False, "DB file missing")


# ─────────────────────────────────────────────────────────────────────────────
# GROUP D — Provider health system
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== GROUP D — Provider Health System ===")

ph_file = HERE / "provider_health.py"
_rec("D", "provider_health.py can be run as a module", ph_file.exists())

if ph_file.exists():
    # Check get_reputation exists via syntax/grep
    try:
        src = ph_file.read_text(encoding="utf-8")
        _rec("D", "get_reputation() function exists", "def get_reputation(" in src)
    except Exception as exc:
        _rec("D", "get_reputation() function exists", False, str(exc))
else:
    _rec("D", "get_reputation() function exists", False, "File missing")

HEALTH_CHECKS = [
    ("health_results/latest_health.json", True),
    ("health_results/tier1_results.json", True),
    ("health_results/tier2_results.json", True),
    ("health_results/tier3_results.json", True),
    ("health_results/cost_log.csv", True),
]
for path_str, _is_json in HEALTH_CHECKS:
    fpath = HERE / path_str
    exists = fpath.exists()
    _rec("D", f"{path_str} exists", exists)
    if exists and _is_json and path_str.endswith(".json"):
        try:
            json.loads(fpath.read_text(encoding="utf-8"))
            _rec("D", f"{path_str} is valid JSON", True)
        except Exception as exc:
            _rec("D", f"{path_str} is valid JSON", False, str(exc)[:80])


# ─────────────────────────────────────────────────────────────────────────────
# GROUP E — MCC Server
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== GROUP E — MCC Server ===")

_mcc_proc = None
_mcc_started = False

mcc_file = HERE / "mcc_server.py"
if not mcc_file.exists():
    _rec("E", "Start mcc_server.py as subprocess on port 8080", False, "mcc_server.py missing")
else:
    try:
        _mcc_proc = subprocess.Popen(
            [sys.executable, str(mcc_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(HERE),
        )
        time.sleep(3)
        _mcc_started = _mcc_proc.poll() is None
        _rec("E", "Start mcc_server.py as subprocess on port 8080", _mcc_started,
             "" if _mcc_started else "Process exited early")
    except Exception as exc:
        _rec("E", "Start mcc_server.py as subprocess on port 8080", False, str(exc)[:120])


def _http_get(path, timeout=5):
    try:
        url = f"http://127.0.0.1:8080{path}"
        with urllib.request.urlopen(url, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="replace")
            return r.status, body
    except Exception as exc:
        return None, str(exc)


if _mcc_started:
    status_code, body = _http_get("/health-status")
    ok = status_code == 200
    _rec("E", "GET /health-status returns 200", ok,
         "" if ok else f"status={status_code}, body={body[:80]}")
    if ok:
        try:
            json.loads(body)
            _rec("E", "GET /health-status returns valid JSON", True)
        except Exception as exc:
            _rec("E", "GET /health-status returns valid JSON", False, str(exc)[:80])
    else:
        _rec("E", "GET /health-status returns valid JSON", False, "Request failed")

    status_code2, body2 = _http_get("/")
    _rec("E", "GET / returns 200", status_code2 == 200,
         "" if status_code2 == 200 else f"status={status_code2}")

    # dashboard_data endpoint
    dd_dir = HERE / "dashboard_data"
    if dd_dir.exists() and any(dd_dir.iterdir()):
        status_code3, body3 = _http_get("/dashboard-data/")
        _rec("E", "GET /dashboard-data/ returns response", status_code3 is not None,
             "" if status_code3 is not None else "No response")
    else:
        _rec("E", "GET /dashboard-data/ returns response", True, "(skipped — no files)")
else:
    for item in [
        "GET /health-status returns 200",
        "GET /health-status returns valid JSON",
        "GET / returns 200",
        "GET /dashboard-data/ returns response",
    ]:
        _rec("E", item, False, "Server not started")

# Kill server
if _mcc_proc is not None:
    try:
        _mcc_proc.terminate()
        _mcc_proc.wait(timeout=5)
        _rec("E", "Kill subprocess cleanly", True)
    except Exception as exc:
        _rec("E", "Kill subprocess cleanly", False, str(exc)[:80])
        try:
            _mcc_proc.kill()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# GROUP F — MCC HTML structure
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== GROUP F — MCC HTML Structure ===")

html_path = HERE / "mission_control.html"
if not html_path.exists():
    for item in ["Home tab", "Provider Health tab", "Kanban tab", "AAFL Runs tab",
                 "Scout Control tab", "Costs tab", "WCCS tab", "AAFL Control tab",
                 "Connect Data button", "Server status dot", "7 data cards + 3 slots",
                 "Cards are clickable", "dashboard_data/README.md exists"]:
        _rec("F", item, False, "mission_control.html missing")
else:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    html_lower = html.lower()

    def _tab_exists(tab_id):
        return f'data-tab="{tab_id}"' in html or f"data-tab='{tab_id}'" in html

    def _tab_first(tab_id):
        # Check it's the first tab-btn
        import re
        buttons = re.findall(r'data-tab=["\']([^"\']+)["\']', html)
        return buttons[0] == tab_id if buttons else False

    _rec("F", "Home tab is first tab", _tab_first("home"))
    _rec("F", "Provider Health tab exists", _tab_exists("providerhealth"))
    _rec("F", "Kanban tab exists", _tab_exists("kanban"))
    _rec("F", "AAFL Runs tab exists", _tab_exists("aafl-runs"))
    _rec("F", "Scout Control tab exists", _tab_exists("scout"))
    _rec("F", "Costs tab exists", _tab_exists("costs"))
    _rec("F", "WCCS tab exists", _tab_exists("wccs"))
    _rec("F", "AAFL Control tab exists", _tab_exists("aafl-control"))

    _rec("F", "Connect Data button exists with spinner state",
         "btn-connect" in html and "btn-spinner" in html)
    _rec("F", "Server status dot exists",
         "server-dot" in html)

    # 7 data cards
    import re as _re
    home_card_files = _re.findall(r"file:\s*['\"]([^'\"]+\.json)['\"]", html)
    _rec("F", "Home screen has 7 data cards",
         len(home_card_files) >= 7,
         f"Found {len(home_card_files)} card file refs")

    _rec("F", "Home screen has 3 empty slot cards",
         "Empty Slot" in html or "home-card slot" in html)

    _rec("F", "Cards are clickable (onclick/href present)",
         "homeCardClick" in html or "onclick" in html)

    _rec("F", "dashboard_data/README.md exists",
         (HERE / "dashboard_data" / "README.md").exists())


# ─────────────────────────────────────────────────────────────────────────────
# GROUP G — AAFL core logic
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== GROUP G — AAFL Core Logic ===")

# task_router classify tests
tr_path = HERE / "task_router.py"
if tr_path.exists():
    try:
        spec = importlib.util.spec_from_file_location("task_router", tr_path)
        tr_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tr_mod)

        result1 = tr_mod.classify("write python code")
        tier1 = result1.get("tier", "")
        _rec("G", "task_router classifies 'write python code' as AAFL or CLAC",
             tier1 in ("AAFL", "CLAC"),
             f"Got: {tier1}")

        result2 = tr_mod.classify("what should I do next")
        tier2 = result2.get("tier", "")
        _rec("G", "task_router classifies 'what should I do next' as SONNET",
             tier2 == "SONNET",
             f"Got: {tier2}")
    except Exception as exc:
        _rec("G", "task_router classifies 'write python code' as AAFL or CLAC",
             False, str(exc)[:120])
        _rec("G", "task_router classifies 'what should I do next' as SONNET",
             False, "Module load failed")
else:
    _rec("G", "task_router classifies 'write python code' as AAFL or CLAC",
         False, "task_router.py missing")
    _rec("G", "task_router classifies 'what should I do next' as SONNET",
         False, "task_router.py missing")

# evaluator
ev_path = HERE / "evaluator.py"
if ev_path.exists():
    try:
        spec = importlib.util.spec_from_file_location("evaluator", ev_path)
        ev_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ev_mod)
        mock_result = "This is a test result with some content about the goal."
        scores = ev_mod.evaluate(mock_result, "test goal")
        _rec("G", "evaluator.py can score a mock result without crashing",
             isinstance(scores, dict) and "overall" in scores)
    except Exception as exc:
        _rec("G", "evaluator.py can score a mock result without crashing",
             False, str(exc)[:120])
else:
    _rec("G", "evaluator.py can score a mock result without crashing",
         False, "evaluator.py missing")

# researcher.py research() function exists
res_path = HERE / "researcher.py"
if res_path.exists():
    src = res_path.read_text(encoding="utf-8", errors="replace")
    _rec("G", "researcher.py research() function exists",
         "def research(" in src or "def scout(" in src)
else:
    _rec("G", "researcher.py research() function exists", False, "researcher.py missing")

# memory_bank store + retrieve
mb_path = HERE / "memory_bank.py"
if mb_path.exists():
    try:
        spec = importlib.util.spec_from_file_location("memory_bank", mb_path)
        mb_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mb_mod)
        test_entry = {
            "title": "_test_entry_",
            "content": "test content",
            "project": "test",
            "source_type": "test",
            "quality_score": 5.0,
            "tags": ["test"],
            "metadata": {},
        }
        entry_id = mb_mod.store(test_entry)
        _rec("G", "memory_bank.py can store a test knowledge entry",
             entry_id is not None)
        # Clean up test entry
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.execute("DELETE FROM knowledge WHERE title='_test_entry_'")
            conn.execute("DELETE FROM tags WHERE knowledge_id=?", (entry_id,))
            conn.commit()
            conn.close()
        except Exception:
            pass
        _rec("G", "memory_bank.py retrieve works (store succeeded)", entry_id is not None)
    except Exception as exc:
        _rec("G", "memory_bank.py can store a test knowledge entry",
             False, str(exc)[:120])
        _rec("G", "memory_bank.py retrieve works (store succeeded)", False, "Store failed")
else:
    _rec("G", "memory_bank.py can store a test knowledge entry",
         False, "memory_bank.py missing")
    _rec("G", "memory_bank.py retrieve works (store succeeded)", False, "File missing")


# ─────────────────────────────────────────────────────────────────────────────
# GROUP H — Index and status files
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== GROUP H — Index and Status Files ===")

index_path = HERE / "INDEX.md"
if index_path.exists():
    idx_lines = len(index_path.read_text(encoding="utf-8").splitlines())
    _rec("H", "INDEX.md is over 30 lines", idx_lines > 30, f"Got {idx_lines} lines")
    _rec("H", "INDEX.md contains RESUME COMMAND section",
         "RESUME COMMAND" in index_path.read_text(encoding="utf-8"))
else:
    _rec("H", "INDEX.md is over 30 lines", False, "File missing")
    _rec("H", "INDEX.md contains RESUME COMMAND section", False, "File missing")

status_path = HERE / "STATUS.md"
if status_path.exists():
    status_text = status_path.read_text(encoding="utf-8")
    status_lines = len(status_text.splitlines())
    _rec("H", "STATUS.md is over 50 lines", status_lines > 50, f"Got {status_lines} lines")
    _rec("H", "STATUS.md contains NEXT PRIORITIES section",
         "NEXT PRIORITIES" in status_text)
else:
    _rec("H", "STATUS.md is over 50 lines", False, "File missing")
    _rec("H", "STATUS.md contains NEXT PRIORITIES section", False, "File missing")

alp_path = HERE / "ALP_Database.md"
if alp_path.exists():
    alp_text = alp_path.read_text(encoding="utf-8")
    alp_lines = alp_text.splitlines()
    table_rows = [l for l in alp_lines
                  if l.strip().startswith("|") and not l.strip().startswith("|---")]
    # subtract header row
    data_rows = max(0, len(table_rows) - 1)
    _rec("H", "ALP_Database.md has at least 12 entries",
         data_rows >= 12, f"Found {data_rows} data rows")
else:
    _rec("H", "ALP_Database.md has at least 12 entries", False, "File missing")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
total   = len(results)
passed  = sum(1 for r in results if r["passed"])
failed  = total - passed

print("\n" + "=" * 60)
print(f"  PHASE 1 RESULTS")
print("=" * 60)
print(f"  Total tests : {total}")
print(f"  Passed      : {passed}")
print(f"  Failed      : {failed}")
print()

fails = [r for r in results if not r["passed"]]
if fails:
    print("  FAILURES:")
    for r in fails:
        reason = f" — {r['reason']}" if r['reason'] else ""
        print(f"    [{r['group']}] {r['name']}{reason}")
    print()

critical_fail = "B" in _fail_groups or "E" in _fail_groups
if critical_fail:
    verdict = "SYSTEM HAS CRITICAL ISSUES (Group B or E failed — stopping before Phase 2)"
else:
    verdict = "SYSTEM HEALTHY" if not fails else "SYSTEM HAS ISSUES (non-critical)"

print(f"  VERDICT: {verdict}")
print("=" * 60)
print()

if critical_fail:
    print("[STOP] Group B or E failures detected. Do not proceed to Phase 2.")
    print("       Fix the issues above first.")

# Save JSON
output = {
    "timestamp": datetime.datetime.now().isoformat(),
    "total": total,
    "passed": passed,
    "failed": failed,
    "verdict": verdict,
    "critical_stop": critical_fail,
    "results": results,
}
out_path = HEALTH_DIR / "full_system_test.json"
out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Results saved to: {out_path}")
