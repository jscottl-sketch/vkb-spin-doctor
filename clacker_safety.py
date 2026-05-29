"""
clacker_safety.py — CLACKER Safety Layer for OCB builds.
Provides git stash safety, file validation, and server health check.
"""
import html.parser
import json
import py_compile
import shutil
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
ROLLBACK_LOG = HERE / "data" / "rollback_log.json"


def pre_run(run_id: str, project_root: str) -> str:
    """
    Run git stash push -m pre-ocb-{run_id}.
    Returns the stash output string (use as stash_ref in post_run_failure).
    """
    result = subprocess.run(
        ["git", "stash", "push", "-m", f"pre-ocb-{run_id}"],
        cwd=project_root, capture_output=True, text=True, timeout=30,
    )
    output = (result.stdout + result.stderr).strip()
    return output


def post_run_success(run_id: str, project_root: str):
    """Drop the top stash — changes are good, discard the safety copy."""
    subprocess.run(
        ["git", "stash", "drop"],
        cwd=project_root, capture_output=True, text=True, timeout=30,
    )
    print(f"CLACKER: changes kept — stash dropped for run {run_id}")


def post_run_failure(run_id: str, project_root: str, stash_ref: str):
    """Pop the top stash (rollback) and append to data/rollback_log.json."""
    subprocess.run(
        ["git", "stash", "pop"],
        cwd=project_root, capture_output=True, text=True, timeout=30,
    )
    ROLLBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = json.loads(ROLLBACK_LOG.read_text(encoding="utf-8"))
        if not isinstance(existing, list):
            existing = [existing]
    except Exception:
        existing = []
    existing.append({
        "status": "ROLLED_BACK",
        "run_id": run_id,
        "stash_ref": stash_ref,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    tmp = str(ROLLBACK_LOG) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)
    shutil.move(tmp, str(ROLLBACK_LOG))
    print(f"CLACKER: rolled back to pre-OCB state for run {run_id}")


def check_html(filepath: str) -> tuple:
    """
    Parse HTML file with html.parser.
    Returns (True, "") on success or (False, error_string) on HTMLParseError.
    """
    try:
        text = Path(filepath).read_text(encoding="utf-8", errors="replace")
        parser = html.parser.HTMLParser()
        parser.feed(text)
        parser.close()
        return True, ""
    except html.parser.HTMLParseError as exc:
        return False, str(exc)
    except Exception as exc:
        return False, str(exc)


def check_py(filepath: str) -> tuple:
    """
    Compile-check a Python source file.
    Returns (True, "") on success or (False, error_string) on syntax error.
    """
    try:
        py_compile.compile(str(filepath), doraise=True)
        return True, ""
    except py_compile.PyCompileError as exc:
        return False, str(exc)
    except Exception as exc:
        return False, str(exc)


def check_server() -> bool:
    """
    GET http://127.0.0.1:8080/api/health.
    Returns True if the server responds with HTTP 200.
    """
    try:
        with urllib.request.urlopen("http://127.0.0.1:8080/api/health", timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False
