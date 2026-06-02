"""
ancoreg_validator.py — Save System Validator for ANCOREG tab.
Runs all save-system checks and returns a dict of results.
"""

import datetime
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"

STATUS_FILE   = HERE / "STATUS.md"
HISTORY_FILE  = HERE / "HISTORY.md"
ACCA_FILE     = HERE / "ACCA.md"
INDEX_FILE    = HERE / "INDEX.md"
SESSION_LOGS  = HERE / "session_logs"
LINECOUNT_JSON = DATA / "status_linecount.json"

END_MARKER    = "END_OF_FILE"


def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def _check(name: str, status: str, detail: str) -> dict:
    return {"check": name, "status": status, "detail": detail, "timestamp": _now()}


def validate_save_system() -> dict:
    results = {}

    # 1. STATUS.md exists + line count >= 90% of previous baseline
    try:
        if not STATUS_FILE.exists():
            results["status_exists"] = _check("STATUS.md exists", "FAIL", "File not found")
        else:
            lines = len(STATUS_FILE.read_text(encoding="utf-8").splitlines())
            baseline = 0
            if LINECOUNT_JSON.exists():
                try:
                    baseline = json.loads(LINECOUNT_JSON.read_text(encoding="utf-8")).get("lines", 0)
                except Exception:
                    pass
            if baseline == 0:
                results["status_exists"] = _check("STATUS.md line count", "PASS", f"{lines} lines (no baseline yet)")
            elif lines >= int(baseline * 0.90):
                results["status_exists"] = _check("STATUS.md line count", "PASS", f"{lines} lines (baseline {baseline}, {int(lines/baseline*100)}%)")
            else:
                results["status_exists"] = _check("STATUS.md line count", "FAIL", f"{lines} lines is below 90% of baseline {baseline}")
    except Exception as exc:
        results["status_exists"] = _check("STATUS.md line count", "ERROR", str(exc))

    # 2. END_OF_FILE marker in all 4 .md files
    for fname, fpath in [("STATUS.md", STATUS_FILE), ("HISTORY.md", HISTORY_FILE),
                          ("ACCA.md", ACCA_FILE), ("INDEX.md", INDEX_FILE)]:
        key = f"eof_marker_{fname.replace('.', '_').lower()}"
        try:
            if not fpath.exists():
                results[key] = _check(f"{fname} END_OF_FILE marker", "FAIL", "File not found")
            else:
                content = fpath.read_text(encoding="utf-8")
                if END_MARKER in content:
                    results[key] = _check(f"{fname} END_OF_FILE marker", "PASS", "Marker present")
                else:
                    results[key] = _check(f"{fname} END_OF_FILE marker", "FAIL", "END_OF_FILE marker missing")
        except Exception as exc:
            results[key] = _check(f"{fname} END_OF_FILE marker", "ERROR", str(exc))

    # 3. Last modified timestamp (flag if >48h stale)
    try:
        if STATUS_FILE.exists():
            mtime = STATUS_FILE.stat().st_mtime
            age_h = (datetime.datetime.now().timestamp() - mtime) / 3600
            if age_h < 48:
                results["status_freshness"] = _check("STATUS.md freshness", "PASS", f"Last modified {age_h:.1f}h ago")
            else:
                results["status_freshness"] = _check("STATUS.md freshness", "AMBER", f"Stale — last modified {age_h:.0f}h ago (>48h)")
        else:
            results["status_freshness"] = _check("STATUS.md freshness", "FAIL", "File missing")
    except Exception as exc:
        results["status_freshness"] = _check("STATUS.md freshness", "ERROR", str(exc))

    # 4. Git status — uncommitted changes?
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(HERE), timeout=10
        )
        if result.returncode == 0:
            changed = result.stdout.strip()
            if changed:
                count = len(changed.splitlines())
                results["git_clean"] = _check("Git uncommitted changes", "AMBER", f"{count} uncommitted change(s)")
            else:
                results["git_clean"] = _check("Git uncommitted changes", "PASS", "Working tree clean")
        else:
            results["git_clean"] = _check("Git uncommitted changes", "ERROR", result.stderr.strip()[:100])
    except Exception as exc:
        results["git_clean"] = _check("Git uncommitted changes", "ERROR", str(exc))

    # 5. Split integrity — all 4 .md files present and non-empty
    split_ok = True
    split_details = []
    for fname, fpath in [("STATUS.md", STATUS_FILE), ("HISTORY.md", HISTORY_FILE),
                          ("ACCA.md", ACCA_FILE), ("INDEX.md", INDEX_FILE)]:
        if not fpath.exists():
            split_ok = False
            split_details.append(f"{fname} MISSING")
        elif fpath.stat().st_size == 0:
            split_ok = False
            split_details.append(f"{fname} EMPTY")
        else:
            split_details.append(f"{fname} OK")
    results["split_integrity"] = _check(
        "Split integrity (4 .md files)",
        "PASS" if split_ok else "FAIL",
        " | ".join(split_details)
    )

    # 6. aafl_wccs.py importable + callable
    try:
        wccs_path = HERE / "aafl_wccs.py"
        if not wccs_path.exists():
            results["wccs_importable"] = _check("aafl_wccs.py importable", "FAIL", "File not found")
        else:
            result = subprocess.run(
                [sys.executable, "-c", "import importlib.util,sys; spec=importlib.util.spec_from_file_location('aafl_wccs','aafl_wccs.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('OK')"],
                capture_output=True, text=True, cwd=str(HERE), timeout=15
            )
            if "OK" in result.stdout:
                results["wccs_importable"] = _check("aafl_wccs.py importable", "PASS", "Importable OK")
            else:
                err = (result.stderr or result.stdout)[:120].strip()
                results["wccs_importable"] = _check("aafl_wccs.py importable", "FAIL", err)
    except Exception as exc:
        results["wccs_importable"] = _check("aafl_wccs.py importable", "ERROR", str(exc))

    # 7. session_logs/ folder exists + recent files present
    try:
        if not SESSION_LOGS.exists():
            results["session_logs"] = _check("session_logs/ folder", "FAIL", "Folder not found")
        else:
            files = sorted(SESSION_LOGS.glob("*.txt"), key=lambda f: f.stat().st_mtime, reverse=True)
            if not files:
                results["session_logs"] = _check("session_logs/ folder", "AMBER", "Folder exists but no .txt files")
            else:
                newest_age_h = (datetime.datetime.now().timestamp() - files[0].stat().st_mtime) / 3600
                results["session_logs"] = _check(
                    "session_logs/ folder",
                    "PASS",
                    f"{len(files)} files, newest {newest_age_h:.0f}h ago"
                )
    except Exception as exc:
        results["session_logs"] = _check("session_logs/ folder", "ERROR", str(exc))

    return results


if __name__ == "__main__":
    r = validate_save_system()
    for k, v in r.items():
        icon = "✅" if v["status"] == "PASS" else ("⚠️" if v["status"] == "AMBER" else "❌")
        print(f"{icon} {v['check']}: {v['detail']}")
