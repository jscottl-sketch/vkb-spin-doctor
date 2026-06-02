"""
tests/ocb_runner_tests.py — HTTP-level OCB Runner test suite.
Uses POST /api/ocb/run + GET /api/ocb/status against a live mcc_server.py.
Run: python tests/ocb_runner_tests.py   (server must be up on port 8080)
"""

import requests
import os
import json
import time

BASE_URL = "http://127.0.0.1:8080"

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "ocb_test_scripts")
TEMP_OUTPUT = os.path.join(SCRIPTS, "temp_output.txt")

TERMINAL = {"DONE", "FAILED", "ROLLED_BACK", "CANCELLED", "BLOCKED", "DRY_RUN", "PARTIAL"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ocb(phase_name, script_rel):
    """Minimal single-phase OCB block that runs one script (path relative to project root)."""
    return (
        f"═══ Phase 1 — {phase_name} ═══\n"
        f"1. Run script: {script_rel}\n"
    )


def run_ocb_and_wait(ocb_text, timeout=240, poll=3):
    """POST to /api/ocb/run, poll /api/ocb/status until terminal. Returns final status dict."""
    resp = requests.post(
        f"{BASE_URL}/api/ocb/run",
        json={"ocb_text": ocb_text},
        timeout=10,
    )
    resp.raise_for_status()
    run_id = resp.json().get("run_id", "")

    time.sleep(2)  # allow background thread to write initial status
    deadline = time.time() + timeout
    last = {}
    while time.time() < deadline:
        r = requests.get(f"{BASE_URL}/api/ocb/status", timeout=10)
        last = r.json()
        if last.get("run_id") == run_id and last.get("status", "").upper() in TERMINAL:
            return last
        time.sleep(poll)
    return last


def live_output(data):
    """Join live_output (or log) lines into one searchable string."""
    lines = data.get("live_output") or data.get("log") or []
    return "\n".join(str(ln) for ln in lines)


def run_test(name, fn):
    """Run fn(), print PASS/FAIL, return bool."""
    try:
        ok = bool(fn())
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
        return ok
    except Exception as exc:
        print(f"  FAIL  {name}  [{type(exc).__name__}: {exc}]")
        return False


# ── Test functions ─────────────────────────────────────────────────────────────

def test_01_echo():
    """POST run with t01_echo.py — expect status DONE (exit 0)."""
    data = run_ocb_and_wait(_ocb("Echo Test", "tests/ocb_test_scripts/t01_echo.py"))
    return data.get("status", "").upper() == "DONE"


def test_02_readonly():
    """POST run with t02_readonly.py — expect 'Lines:' in live output."""
    data = run_ocb_and_wait(_ocb("Read-Only", "tests/ocb_test_scripts/t02_readonly.py"))
    return "Lines:" in live_output(data)


def test_04_mot():
    """POST run with t04_mot.py — expect status DONE (MOT passes inside script + post-run)."""
    data = run_ocb_and_wait(
        _ocb("MOT Run", "tests/ocb_test_scripts/t04_mot.py"),
        timeout=480,
    )
    return data.get("status", "").upper() == "DONE"


def test_05_gitstash():
    """POST run with t05_gitstash.py — expect status DONE (stash list can be empty)."""
    data = run_ocb_and_wait(_ocb("Git Stash", "tests/ocb_test_scripts/t05_gitstash.py"))
    return data.get("status", "").upper() == "DONE"


def test_06_html_clean():
    """POST run with t06_html_clean.py — expect 'HTML sample read OK' in output."""
    data = run_ocb_and_wait(_ocb("HTML Clean", "tests/ocb_test_scripts/t06_html_clean.py"))
    return "HTML sample read OK" in live_output(data)


def test_07_rollback():
    """POST run with t07_html_bad.py — expect FAILED or ROLLED_BACK (error indicator)."""
    data = run_ocb_and_wait(_ocb("HTML Bad Rollback", "tests/ocb_test_scripts/t07_html_bad.py"))
    return data.get("status", "").upper() in {"FAILED", "ROLLED_BACK", "PARTIAL"}


def test_08_multistep():
    """POST run with t08_multistep.py — expect 'All 3 steps done' AND temp_output.txt created."""
    if os.path.exists(TEMP_OUTPUT):
        os.remove(TEMP_OUTPUT)
    data = run_ocb_and_wait(_ocb("Multistep", "tests/ocb_test_scripts/t08_multistep.py"))
    output_ok = "All 3 steps done" in live_output(data)
    file_ok = os.path.exists(TEMP_OUTPUT)
    return output_ok and file_ok


def test_10_fail():
    """POST run with t10_fail.py — expect exit_code != 0 and 'fail' in output."""
    data = run_ocb_and_wait(_ocb("Deliberate Fail", "tests/ocb_test_scripts/t10_fail.py"))
    status_fail = data.get("status", "").upper() != "DONE"
    has_fail_word = "fail" in live_output(data).lower()
    return status_fail and has_fail_word


def test_11_aafl():
    """POST run with t11_aafl.py (one-liner: import aafl_core) — expect 'aafl_core import OK'."""
    data = run_ocb_and_wait(_ocb("AAFL Import", "tests/ocb_test_scripts/t11_aafl.py"))
    return "aafl_core import OK" in live_output(data)


def test_12_dryrun():
    """POST run with t12_dryrun.py — expect 'TEST COMMENT READ:' in output, no writes."""
    data = run_ocb_and_wait(_ocb("Dry Run Read", "tests/ocb_test_scripts/t12_dryrun.py"))
    return "TEST COMMENT READ:" in live_output(data)


# ── Runner ────────────────────────────────────────────────────────────────────

TESTS = [
    ("test_01_echo",       test_01_echo),
    ("test_02_readonly",   test_02_readonly),
    ("test_04_mot",        test_04_mot),
    ("test_05_gitstash",   test_05_gitstash),
    ("test_06_html_clean", test_06_html_clean),
    ("test_07_rollback",   test_07_rollback),
    ("test_08_multistep",  test_08_multistep),
    ("test_10_fail",       test_10_fail),
    ("test_11_aafl",       test_11_aafl),
    ("test_12_dryrun",     test_12_dryrun),
]

if __name__ == "__main__":
    print(f"\n=== OCB Runner Test Suite ===")
    print(f"    Server: {BASE_URL}")
    print(f"    Tests:  {len(TESTS)}\n")

    results = []
    for name, fn in TESTS:
        passed = run_test(name, fn)
        results.append((name, passed))

    passed_count = sum(1 for _, p in results if p)
    total = len(results)

    print(f"\n{'=' * 42}")
    print(f"  {'Test':<26} {'Result'}")
    print(f"  {'-' * 38}")
    for name, passed in results:
        label = "PASS" if passed else "FAIL"
        print(f"  {name:<26} {label}")
    print(f"  {'-' * 38}")
    print(f"  Score: {passed_count}/{total}")
    print(f"{'=' * 42}\n")
