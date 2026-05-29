"""
ocb_runner.py — OCB (Operation Code Build) Runner
Parses an OCB block and executes each phase/task using free AI providers.
Called by mcc_server.py via POST /api/ocb/run.
"""

import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent

KNOWN_FILES = [
    "mission_control.html",
    "mcc_server.py",
    "loop_manager.py",
    "aafl_core.py",
    "aafl_wccs.py",
    "memory_bank.py",
    "evaluator.py",
    "chief_scout.py",
    "ocb_runner.py",
    "system_monitor.py",
    "provider_health.py",
    "mcc_full_mot.py",
    "mcc_medical.py",
    "work_checker.py",
    "auto_fixer.py",
]

OCB_STATUS_FILE  = HERE / "data" / "ocb_status.json"
CLACHR_RESPONSE  = HERE / "data" / "clachr_response.json"
MOT_SCRIPT       = HERE / "mcc_full_mot.py"

_PHASE_SEP = re.compile(
    r'[═=═]{3,}\s*PHASE\s+(\d+)\s*[—\-—]+\s*(.+?)\s*[═=═]{3,}',
    re.IGNORECASE,
)
_TASK_LINE = re.compile(r'^\s*(\d+)\.\s+(.+)$')

_STOPWORDS = {
    "phase", "section", "lines", "add", "update", "create", "button", "panel",
    "function", "method", "class", "style", "color", "colour", "width", "height",
    "display", "return", "should", "using", "with", "that", "this", "from",
    "into", "each", "every", "show", "hide", "when", "after", "before",
}


# ── Parse ─────────────────────────────────────────────────────────────────────

def parse_ocb_block(text: str) -> list:
    """Split OCB text into structured phases with tasks. Returns list of phase dicts."""
    phases = []
    parts  = _PHASE_SEP.split(text)
    # split() with 2 capturing groups → [pre, num, name, body, num, name, body, ...]
    i = 1
    while i + 2 < len(parts):
        try:
            phase_num  = int(parts[i])
        except ValueError:
            i += 3
            continue
        phase_name = parts[i + 1].strip()
        body       = parts[i + 2]
        tasks = []
        for line in body.splitlines():
            m = _TASK_LINE.match(line)
            if m:
                tasks.append({
                    "num":  int(m.group(1)),
                    "text": m.group(2).strip(),
                })
        phases.append({
            "phase_num":  phase_num,
            "phase_name": phase_name,
            "tasks":      tasks,
        })
        i += 3
    return phases


# ── File identification ───────────────────────────────────────────────────────

def identify_affected_file(task_text: str) -> Path:
    """Return the first known filename found in task_text, else mission_control.html."""
    lower = task_text.lower()
    for fname in KNOWN_FILES:
        if fname.lower() in lower:
            return HERE / fname
    return HERE / "mission_control.html"


# ── Section extraction ────────────────────────────────────────────────────────

def extract_relevant_section(filepath: Path, task_text: str) -> dict:
    """
    Return ±150 lines around the best-scoring keyword match in the file.
    Falls back to whole file if < 600 lines total.
    """
    try:
        raw_lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return {"section_text": "", "start_line": 1, "end_line": 0}

    total = len(raw_lines)
    if total <= 600:
        return {
            "section_text": "\n".join(raw_lines),
            "start_line":   1,
            "end_line":     total,
        }

    # Build keyword set from task_text
    keywords = set()
    for m in re.finditer(r'(\w+)\s*\(', task_text):          # func(
        keywords.add(m.group(1).lower())
    for m in re.finditer(r'\.([a-zA-Z][\w-]{2,})', task_text):  # .className
        keywords.add(m.group(1).lower())
    for m in re.finditer(r'#([a-zA-Z][\w-]{2,})', task_text):   # #id
        keywords.add(m.group(1).lower())
    for m in re.finditer(r'"([^"]{3,30})"', task_text):          # "quoted"
        keywords.add(m.group(1).lower())
    for w in re.findall(r'\b[a-zA-Z]\w{4,}\b', task_text):       # long words
        lw = w.lower()
        if lw not in _STOPWORDS:
            keywords.add(lw)

    keywords.discard("")

    if not keywords:
        end = min(300, total)
        return {"section_text": "\n".join(raw_lines[:end]),
                "start_line": 1, "end_line": end}

    # Score each line using a ±50-line sliding window
    best_idx   = 0
    best_score = -1
    half_win   = 50
    for i in range(total):
        chunk = " ".join(raw_lines[max(0, i - half_win): i + half_win + 1]).lower()
        score = sum(1 for kw in keywords if kw in chunk)
        if score > best_score:
            best_score = score
            best_idx   = i

    start = max(0, best_idx - 150)
    end   = min(total, best_idx + 150)
    return {
        "section_text": "\n".join(raw_lines[start:end]),
        "start_line":   start + 1,   # 1-indexed
        "end_line":     end,
    }


# ── AI task call ──────────────────────────────────────────────────────────────

def run_task(filepath: Path, section_data: dict, task_text: str) -> str:
    """
    Send a section + task to the AI. Returns the modified section text, or "" on failure.
    Provider priority: Codestral → any 'code' provider via aafl_core routing.
    """
    from aafl_core import AAFLCore  # import here so ocb_runner can be imported cheaply

    filename = filepath.name
    start    = section_data["start_line"]
    end      = section_data["end_line"]
    section  = section_data["section_text"]

    prompt = (
        f"You are a precise code editor. Edit the following section of {filename}.\n\n"
        f"SECTION (lines {start}–{end}):\n"
        f"```\n{section}\n```\n\n"
        f"TASK: {task_text}\n\n"
        f"RULES:\n"
        f"- Return ONLY the modified section — no other text.\n"
        f"- Keep every unchanged line completely identical.\n"
        f"- Do not add markdown fences, explanations, or commentary.\n"
        f"- Match the indentation style of the original exactly.\n"
        f"- Output raw code only."
    )

    core   = AAFLCore(dry_run=False, allow_paid=False)
    result = core.run(prompt, task_type="code", max_tokens=4096)
    if not result.ok or not result.response:
        return ""

    text = result.response.strip()
    # Strip accidental markdown fences
    if text.startswith("```"):
        lines = text.splitlines()
        end_fence = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        text = "\n".join(lines[1:end_fence])
    return text


# ── Apply result ──────────────────────────────────────────────────────────────

def apply_result(filepath: Path, start_line: int, end_line: int, new_section: str) -> bool:
    """
    Atomically replace lines[start_line-1 : end_line] with new_section.
    For .py files: verify syntax before committing. Returns True on success.
    """
    try:
        original = filepath.read_text(encoding="utf-8", errors="replace")
        orig_lines = original.splitlines(keepends=True)

        new_lines = new_section.splitlines(keepends=True)
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] += "\n"

        replaced    = orig_lines[:start_line - 1] + new_lines + orig_lines[end_line:]
        new_content = "".join(replaced)

        fd, tmp = tempfile.mkstemp(dir=str(filepath.parent), suffix=".ocbtmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_content)

            if filepath.suffix == ".py":
                try:
                    py_compile.compile(tmp, doraise=True)
                except py_compile.PyCompileError:
                    os.unlink(tmp)
                    return False

            shutil.move(tmp, str(filepath))
            return True
        except Exception:
            try:
                os.unlink(tmp)
            except Exception:
                pass
            raise
    except Exception:
        return False


# ── Status helpers ────────────────────────────────────────────────────────────

def _write_status(status_obj: dict):
    OCB_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(OCB_STATUS_FILE) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(status_obj, f, indent=2)
    shutil.move(tmp, str(OCB_STATUS_FILE))


def _read_status() -> dict:
    try:
        return json.loads(OCB_STATUS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _is_cancelled(run_id: str) -> bool:
    try:
        s = _read_status()
        return s.get("run_id") == run_id and bool(s.get("cancelled"))
    except Exception:
        return False


def _log_entry(status_obj: dict, phase: int, task: int, message: str):
    ts    = datetime.now().strftime("%H:%M:%S")
    label = f"P{phase}.T{task}" if task > 0 else (f"P{phase}" if phase > 0 else "SYS")
    status_obj.setdefault("log", []).append(f"[{ts}] [{label}] {message}")
    if len(status_obj["log"]) > 300:
        status_obj["log"] = status_obj["log"][-300:]


# ── Orchestrator ──────────────────────────────────────────────────────────────

def run_all(ocb_text: str, run_id: str, max_retries: int = 3,
            provider: str = "auto") -> dict:
    """
    Parse and execute an entire OCB block.
    Writes progress to data/ocb_status.json throughout.
    Returns the final status dict.
    """
    phases = parse_ocb_block(ocb_text)
    now    = datetime.now().isoformat(timespec="seconds")

    status = {
        "run_id":        run_id,
        "started_at":    now,
        "provider":      provider,
        "max_retries":   max_retries,
        "phases": [
            {
                "phase_num":  p["phase_num"],
                "phase_name": p["phase_name"],
                "status":     "PENDING",
                "tasks": [
                    {"num": t["num"], "text": t["text"][:80], "status": "PENDING"}
                    for t in p["tasks"]
                ],
            }
            for p in phases
        ],
        "current_phase":  0,
        "current_task":   0,
        "log":            [],
        "mot_score":      "",
        "status":         "RUNNING",
        "cancelled":      False,
        "files_changed":  [],
        "completed_at":   "",
    }
    _write_status(status)

    files_changed = set()
    phases_done   = []
    phases_failed = []

    for pi, phase in enumerate(phases):
        if _is_cancelled(run_id):
            status["status"] = "CANCELLED"
            _write_status(status)
            break

        status["current_phase"]        = phase["phase_num"]
        status["phases"][pi]["status"] = "RUNNING"
        _log_entry(status, phase["phase_num"], 0,
                   f"Starting: {phase['phase_name']}")
        _write_status(status)

        phase_ok = True

        for ti, task in enumerate(phase["tasks"]):
            if _is_cancelled(run_id):
                status["phases"][pi]["tasks"][ti]["status"] = "SKIPPED"
                break

            status["current_task"] = task["num"]
            status["phases"][pi]["tasks"][ti]["status"] = "RUNNING"
            _log_entry(status, phase["phase_num"], task["num"],
                       f"Task: {task['text'][:70]}")
            _write_status(status)

            filepath = identify_affected_file(task["text"])
            _log_entry(status, phase["phase_num"], task["num"],
                       f"Target: {filepath.name}")

            success = False
            for attempt in range(1, max_retries + 1):
                if _is_cancelled(run_id):
                    break
                try:
                    section_data = extract_relevant_section(filepath, task["text"])
                    if not section_data["section_text"]:
                        _log_entry(status, phase["phase_num"], task["num"],
                                   f"SKIP — could not read {filepath.name}")
                        break

                    _log_entry(status, phase["phase_num"], task["num"],
                               f"Attempt {attempt}: lines {section_data['start_line']}–{section_data['end_line']}")
                    _write_status(status)

                    new_text = run_task(filepath, section_data, task["text"])
                    if not new_text:
                        _log_entry(status, phase["phase_num"], task["num"],
                                   f"Attempt {attempt}: AI returned empty — retry")
                        continue

                    ok = apply_result(
                        filepath,
                        section_data["start_line"],
                        section_data["end_line"],
                        new_text,
                    )
                    if ok:
                        files_changed.add(filepath.name)
                        status["files_changed"] = sorted(files_changed)
                        _log_entry(status, phase["phase_num"], task["num"],
                                   f"DONE — {filepath.name} updated")
                        success = True
                        break
                    else:
                        _log_entry(status, phase["phase_num"], task["num"],
                                   f"Attempt {attempt}: apply failed (syntax?) — retry")
                except Exception as exc:
                    _log_entry(status, phase["phase_num"], task["num"],
                               f"Attempt {attempt}: exception — {str(exc)[:80]}")

            if _is_cancelled(run_id):
                status["phases"][pi]["tasks"][ti]["status"] = "SKIPPED"
            elif success:
                status["phases"][pi]["tasks"][ti]["status"] = "DONE"
            else:
                status["phases"][pi]["tasks"][ti]["status"] = "FAILED"
                phase_ok = False
                _log_entry(status, phase["phase_num"], task["num"],
                           f"FAILED after {max_retries} attempt(s)")

            _write_status(status)

        if _is_cancelled(run_id):
            status["phases"][pi]["status"] = "SKIPPED"
        elif phase_ok:
            status["phases"][pi]["status"] = "DONE"
            phases_done.append(phase["phase_name"])
        else:
            status["phases"][pi]["status"] = "FAILED"
            phases_failed.append(phase["phase_name"])

        _write_status(status)

    # Run MOT test suite
    mot_score = ""
    if not _is_cancelled(run_id):
        _log_entry(status, 0, 0, "Running MOT test suite…")
        _write_status(status)
        try:
            result = subprocess.run(
                [sys.executable, str(MOT_SCRIPT)],
                capture_output=True, text=True, timeout=180, cwd=str(HERE),
            )
            output = result.stdout + result.stderr
            # Try to extract the concise score line
            for line in output.splitlines():
                if "passed" in line.lower() and ("failed" in line.lower() or "/" in line):
                    mot_score = line.strip()
                    break
            if not mot_score:
                for line in output.splitlines():
                    if "verdict" in line.lower() or "clear" in line.lower():
                        mot_score = line.strip()
                        break
            if not mot_score:
                mot_score = f"exit {result.returncode}"
            _log_entry(status, 0, 0, f"MOT: {mot_score}")
        except Exception as exc:
            mot_score = f"MOT error: {str(exc)[:60]}"
            _log_entry(status, 0, 0, mot_score)

    status["mot_score"]   = mot_score
    completed_at          = datetime.now().isoformat(timespec="seconds")
    status["completed_at"] = completed_at

    if not _is_cancelled(run_id):
        status["status"] = "DONE" if not phases_failed else "PARTIAL"

    _write_status(status)

    # Write CLACHR response for the CLACHR panel auto-poll
    clachr = {
        "session_id":    run_id,
        "status":        status["status"],
        "phases_done":   phases_done,
        "phases_failed": phases_failed,
        "files_changed": sorted(files_changed),
        "mot_score":     mot_score,
        "completed_at":  completed_at,
        "notes":         "",
    }
    try:
        tmp = str(CLACHR_RESPONSE) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(clachr, f, indent=2)
        shutil.move(tmp, str(CLACHR_RESPONSE))
    except Exception:
        pass

    return status


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
═══ PHASE 1 — TEST PHASE ═══

1. Add a comment to aafl_core.py saying hello world
2. Update mcc_server.py with a dummy no-op comment

═══ PHASE 2 — SECOND TEST PHASE ═══

3. Check that mission_control.html exists
"""
    print("parse_ocb_block test:")
    phases = parse_ocb_block(sample)
    for p in phases:
        print(f"  Phase {p['phase_num']}: {p['phase_name']} — {len(p['tasks'])} tasks")
        for t in p["tasks"]:
            print(f"    {t['num']}. {t['text']}")
    print(f"\nidentify_affected_file tests:")
    tests = [
        "Add a new button to mission_control.html",
        "Fix the handler in mcc_server.py",
        "Update the routing table in aafl_core.py",
        "Some generic task with no file mentioned",
    ]
    for txt in tests:
        print(f"  '{txt[:50]}' -> {identify_affected_file(txt).name}")
    print("\nocb_runner.py self-test complete.")
