"""
ocb_runner_tests.py — 8 tests for parse_ocb_block + run_safe fundamentals.
Writes results to data/ocb_runner_test_results.json.
Run: python ocb_runner_tests.py
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

HERE = Path(__file__).parent

try:
    from ocb_runner import parse_ocb_block, pre_flight, parse_ocb, identify_affected_file
except ImportError as e:
    print(f"[FATAL] Cannot import ocb_runner: {e}")
    sys.exit(1)

_results = []


def _test(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    _results.append({"name": name, "status": status, "detail": detail})
    icon = "OK" if passed else "!!"
    print(f"  [{icon}] {name}: {status}" + (f" — {detail}" if detail else ""))


# ── Test 1: Standard === Phase N === format ───────────────────────────────────
def test_standard_sep_format():
    ocb = """
═══ PHASE 1 — Build the thing ═══

1. Add a button to mission_control.html
2. Wire endpoint in mcc_server.py

═══ PHASE 2 — Test it ═══

3. Run mcc_full_mot.py
"""
    phases = parse_ocb_block(ocb)
    _test("standard_sep_format",
          len(phases) == 2 and phases[0]["phase_num"] == 1 and phases[1]["phase_num"] == 2,
          f"found {len(phases)} phases")


# ── Test 2: Bare "Phase N — Title" format ─────────────────────────────────────
def test_bare_phase_format():
    ocb = """
Phase 1 — Setup
1. Create data directory
2. Write config file

Phase 2 — Run
3. Execute the script
"""
    phases = parse_ocb_block(ocb)
    _test("bare_phase_format",
          len(phases) == 2 and phases[0]["phase_name"] == "Setup",
          f"found {len(phases)} phases, first={phases[0]['phase_name'] if phases else 'N/A'}")


# ── Test 3: Forgiving fallback — lines starting with N. ──────────────────────
def test_forgiving_numbered_lines():
    ocb = """
1. Add timing to aafl_wccs.py
2. Fix the z-index in mission_control.html
3. Write tests
"""
    phases = parse_ocb_block(ocb)
    # Should produce at least 1 phase with tasks
    has_tasks = any(len(p.get("tasks", [])) > 0 for p in phases)
    _test("forgiving_numbered_lines",
          len(phases) >= 1 and has_tasks,
          f"phases={len(phases)}, has_tasks={has_tasks}")


# ── Test 4: Empty input — must not hang ──────────────────────────────────────
def test_empty_input():
    t0 = time.time()
    phases = parse_ocb_block("")
    elapsed = time.time() - t0
    _test("empty_input_no_hang",
          elapsed < 5.0 and isinstance(phases, list),
          f"elapsed={elapsed:.2f}s phases={len(phases)}")


# ── Test 5: Very long input — must not hang (soft timeout) ───────────────────
def test_large_input_timeout():
    big_text = "some random text without any phase markers\n" * 5000
    t0 = time.time()
    phases = parse_ocb_block(big_text)
    elapsed = time.time() - t0
    _test("large_input_timeout",
          elapsed < 35.0 and isinstance(phases, list),
          f"elapsed={elapsed:.2f}s phases={len(phases)}")


# ── Test 6: identify_affected_file routing ────────────────────────────────────
def test_file_identification():
    tests = [
        ("Add a button to mission_control.html", "mission_control.html"),
        ("Fix the handler in mcc_server.py", "mcc_server.py"),
        ("Update aafl_core.py routing table", "aafl_core.py"),
        ("Generic task with no file mention", "mission_control.html"),  # default
    ]
    all_pass = True
    details = []
    for task_text, expected in tests:
        got = identify_affected_file(task_text).name
        ok = got == expected
        if not ok:
            all_pass = False
        details.append(f"{task_text[:30]}->{got}{'OK' if ok else 'FAIL'}")
    _test("file_identification", all_pass, " | ".join(details))


# ── Test 7: parse_ocb extended dict format ────────────────────────────────────
def test_parse_ocb_extended():
    ocb = """
═══ PHASE 1 — HTML edits ═══
1. Add panel to mission_control.html
2. Fix z-index in mission_control.html

═══ PHASE 2 — Python edits ═══
3. Add endpoint to mcc_server.py
"""
    result = parse_ocb(ocb)
    ok = (isinstance(result, list) and len(result) == 2
          and result[0].get("risk_level") == "HIGH"   # HTML = HIGH
          and result[1].get("risk_level") == "MEDIUM"  # .py = MEDIUM
    )
    _test("parse_ocb_extended_format",
          ok,
          f"phases={len(result)}, risk0={result[0].get('risk_level') if result else 'N/A'}")


# ── Test 8: Colour-change test — phase with colour task parsed correctly ──────
def test_colour_change_task():
    ocb = """
═══ PHASE 1 — Change tab bar colour ═══

1. In mission_control.html change tab bar background from #111 to #1a1a2e
2. Update the active tab colour from #4af to #c084fc
3. Fix the button border colour to match
"""
    phases = parse_ocb_block(ocb)
    tasks = phases[0]["tasks"] if phases else []
    has_colour_task = any("colour" in t["text"].lower() or "color" in t["text"].lower()
                          for t in tasks)
    _test("colour_change_task_parsed",
          len(phases) == 1 and len(tasks) == 3 and has_colour_task,
          f"phases={len(phases)} tasks={len(tasks)} colour_task={has_colour_task}")


# ── Run all tests ─────────────────────────────────────────────────────────────
def main():
    print(f"\n[OCB RUNNER TESTS] Starting 8 tests...")
    start = time.time()

    test_standard_sep_format()
    test_bare_phase_format()
    test_forgiving_numbered_lines()
    test_empty_input()
    test_large_input_timeout()
    test_file_identification()
    test_parse_ocb_extended()
    test_colour_change_task()

    elapsed = time.time() - start
    passed = sum(1 for r in _results if r["status"] == "PASS")
    failed = sum(1 for r in _results if r["status"] == "FAIL")
    total = len(_results)

    print(f"\n[RESULT] {passed}/{total} passed in {elapsed:.1f}s")
    if failed:
        print(f"[FAIL] {failed} test(s) failed")
    else:
        print("[ALL CLEAR] All 8 tests passed")

    # Write JSON results
    output = {
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "elapsed_s": round(elapsed, 2),
        "passed": passed,
        "failed": failed,
        "total": total,
        "verdict": "ALL CLEAR" if failed == 0 else f"FAIL — {failed} failed",
        "tests": _results,
    }
    out_path = HERE / "data" / "ocb_runner_test_results.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"[OUT] Results written to {out_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
