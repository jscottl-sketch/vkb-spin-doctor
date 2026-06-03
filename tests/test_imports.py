"""
tests/test_imports.py — Verify every .py in project root can be imported without crash.
Catches "silent broken import" issues. Exits 0 if all pass, 1 if any fail.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PASS = 0
FAIL = 0

# Files to skip (they have side-effects on import or are scripts)
SKIP = {
    "mcc_server.py",         # starts HTTP server
    "spin_doctor.py",        # starts tkinter GUI
    "merge_sessions.py",     # interactive
    "mcc_full_mot.py",       # runs MOT suite
    "reality_check.py",      # runs report on import in __main__ only (safe, but slow)
    "HOW_TO_INTEGRATE_DIAGNOSTIC.py",
}


def check(label: str, ok: bool, detail: str = "") -> bool:
    global PASS, FAIL
    status = "PASS" if ok else "FAIL"
    suffix = f": {detail}" if detail else ""
    print(f"{status}: {label}{suffix}")
    if ok:
        PASS += 1
    else:
        FAIL += 1
    return ok


def main():
    print("=== test_imports.py ===")
    py_files = sorted(p for p in HERE.glob("*.py") if p.name not in SKIP)

    for pyf in py_files:
        mod = pyf.stem
        result = subprocess.run(
            [sys.executable, "-c", f"import sys; sys.path.insert(0, r'{HERE}'); import {mod}"],
            capture_output=True, text=True, timeout=15
        )
        ok = result.returncode == 0
        detail = ""
        if not ok:
            # Extract just the last error line
            lines = (result.stderr or "").strip().splitlines()
            detail = lines[-1][:80] if lines else "unknown error"
        check(f"import {mod}", ok, detail)

    total = PASS + FAIL
    print(f"\nRESULT: {PASS}/{total} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
