"""
ocb_runner.py — OCB (Operation Code Build) Runner
Parses an OCB block and executes each phase/task using free AI providers.
Called by mcc_server.py via POST /api/ocb/run.
"""

import argparse
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

import clacker_safety
import clacker_validator

HERE = Path(__file__).parent

_SESSION_STATE = HERE / "data" / "session_state.json"
_SS_DEFAULTS = {
    "session_id": "", "started_at": "",
    "current_task": {"type": "", "description": "", "subsystem": "", "status": "idle", "started_at": ""},
    "last_result": {"task": "", "status": "", "mot_score": "", "files_changed": [], "completed_at": ""},
    "provider_health": {"healthy_count": 0, "total": 14, "last_checked": ""},
    "watchdog_status": "OFF",
    "last_save": {"type": "", "timestamp": "", "file": ""},
    "aafl_score": None, "cost_7d": None, "active_ocb_run_id": "", "next_priority": "",
}


def _update_ss(patch: dict):
    """Merge patch into data/session_state.json (atomic, non-blocking)."""
    try:
        state = json.loads(_SESSION_STATE.read_text(encoding="utf-8")) if _SESSION_STATE.exists() else dict(_SS_DEFAULTS)
        state.update(patch)
        fd, tmp = tempfile.mkstemp(dir=str(_SESSION_STATE.parent), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        shutil.move(tmp, str(_SESSION_STATE))
    except Exception:
        pass

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

# Lifeguard Protocol paths
STATUS_FILE      = HERE / "STATUS.md"
STATUS_MASTER    = HERE / "STATUS_MASTER.md"
WAL_LOG          = HERE / "ocb_wal.log"
OCB_QUEUE        = HERE / "data" / "ocb_queue.json"
STUCK_INBOX      = HERE / "data" / "stuck_inbox.json"
SNAPSHOTS_DIR    = HERE / "status_snapshots"
SESSION_LOGS_DIR = HERE / "session_logs"

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
                ok, err = clacker_safety.check_py(tmp)
                if not ok:
                    os.unlink(tmp)
                    return False

            if filepath.suffix == ".html":
                ok, err = clacker_safety.check_html(tmp)
                if not ok:
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


# ── Git safety helpers ────────────────────────────────────────────────────────

def _git_stash_save(status: dict) -> bool:
    """Run git stash before any edits. Returns True if changes were actually stashed."""
    print("🔒 Stashing current state before edit...")
    _log_entry(status, 0, 0, "🔒 Stashing current state before edit...")
    _write_status(status)
    try:
        result = subprocess.run(
            ["git", "stash"],
            capture_output=True, text=True, cwd=str(HERE), timeout=30,
        )
        output = (result.stdout + result.stderr).strip()
        stashed = "saved working directory" in output.lower()
        _log_entry(status, 0, 0, f"git stash: {output[:120]}" if output else "git stash: (no output)")
        _write_status(status)
        return stashed
    except Exception as exc:
        _log_entry(status, 0, 0, f"git stash error: {str(exc)[:80]}")
        _write_status(status)
        return False


def _git_stash_drop(status: dict):
    """Drop the top stash after MOT pass — changes are good, discard the safety copy."""
    print("✅ MOT passed — stash dropped, changes kept")
    _log_entry(status, 0, 0, "✅ MOT passed — stash dropped, changes kept")
    try:
        result = subprocess.run(
            ["git", "stash", "drop"],
            capture_output=True, text=True, cwd=str(HERE), timeout=30,
        )
        output = (result.stdout + result.stderr).strip()
        _log_entry(status, 0, 0, f"git stash drop: {output[:120]}")
    except Exception as exc:
        _log_entry(status, 0, 0, f"git stash drop error: {str(exc)[:80]}")
    _write_status(status)


def _git_stash_pop(status: dict):
    """Pop the top stash after MOT fail — auto-rollback to the pre-edit state."""
    print("🔴 MOT failed — rolling back to safe state automatically")
    _log_entry(status, 0, 0, "🔴 MOT failed — rolling back to safe state automatically")
    try:
        result = subprocess.run(
            ["git", "stash", "pop"],
            capture_output=True, text=True, cwd=str(HERE), timeout=30,
        )
        output = (result.stdout + result.stderr).strip()
        _log_entry(status, 0, 0, f"git stash pop: {output[:120]}")
    except Exception as exc:
        _log_entry(status, 0, 0, f"git stash pop error: {str(exc)[:80]}")
    _write_status(status)


# ── Per-file HTML safety ──────────────────────────────────────────────────────

def git_stash_html() -> bool:
    """Stash mission_control.html before any edit."""
    result = subprocess.run(
        ["git", "stash", "push", "-m", "ocb-pre-edit", "mission_control.html"],
        capture_output=True, text=True, cwd=str(HERE),
    )
    return result.returncode == 0


def check_html_syntax(html_path: str) -> tuple:
    """Basic HTML syntax check — detect missing panes and unbalanced script tags."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        required = [
            'id="tab-wccs"', 'id="tab-aafl-control"',
            'id="tab-health-suite"', 'id="tab-kanban"', 'id="tab-scout"',
        ]
        missing = [r for r in required if r not in content]
        if missing:
            return False, f"Missing tab panes: {missing}"
        opens  = content.count("<script")
        closes = content.count("</script>")
        if opens != closes:
            return False, f"Unbalanced script tags: {opens} open, {closes} close"
        return True, "OK"
    except Exception as exc:
        return False, str(exc)


def auto_rollback_html() -> bool:
    """Restore mission_control.html from git stash."""
    result = subprocess.run(
        ["git", "stash", "pop"],
        capture_output=True, text=True, cwd=str(HERE),
    )
    return result.returncode == 0


# ── Orchestrator ──────────────────────────────────────────────────────────────

def run_all(ocb_text: str, run_id: str, max_retries: int = 3,
            provider: str = "auto", acceptance_criteria: list = None) -> dict:
    """
    Parse and execute an entire OCB block.
    Writes progress to data/ocb_status.json throughout.
    Returns the final status dict.
    """
    if acceptance_criteria is None:
        acceptance_criteria = []
    phases = parse_ocb_block(ocb_text)
    now    = datetime.now().isoformat(timespec="seconds")

    # ── NEEDS_OPUS check ──────────────────────────────────────────────────────
    try:
        from clacker_router import classify_all as _classify_all
        ca = _classify_all(phases)
        if ca.get("has_opus_tasks"):
            needs_opus_status = {
                "run_id":         run_id,
                "status":         "NEEDS_OPUS",
                "started_at":     now,
                "opus_task_list": ca["opus_task_list"],
                "phases":         [{"phase_num": p["phase_num"], "phase_name": p["phase_name"],
                                    "status": "PENDING",
                                    "tasks": [{"num": t["num"], "text": t["text"][:80],
                                               "status": "PENDING"} for t in p["tasks"]]}
                                   for p in phases],
                "log": [f"[{datetime.now().strftime('%H:%M:%S')}] [SYS] NEEDS_OPUS — "
                        f"{len(ca['opus_task_list'])} task(s) require Claude Opus"],
                "mot_score": "", "cancelled": False, "files_changed": [], "completed_at": "",
            }
            _write_status(needs_opus_status)
            return needs_opus_status
    except Exception:
        pass

    # Update session_state: current task = OCB run
    _update_ss({"current_task": {
        "type": "CODE", "description": f"OCB run {run_id}",
        "subsystem": "ocb_runner", "status": "running",
        "started_at": now,
    }, "active_ocb_run_id": run_id})

    status = {
        "run_id":               run_id,
        "started_at":           now,
        "provider":             provider,
        "max_retries":          max_retries,
        "acceptance_criteria":  acceptance_criteria,
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

    stash_ref = clacker_safety.pre_run(run_id, str(HERE))
    _log_entry(status, 0, 0, f"🔒 git stash push pre-ocb-{run_id}: {stash_ref[:80] if stash_ref else '(nothing stashed)'}")
    _write_status(status)

    files_changed = set()
    phases_done   = []
    phases_failed = []

    try:
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

            # Stash HTML before any edit attempt
            html_stashed = False
            if filepath.suffix == ".html":
                html_stashed = git_stash_html()
                if html_stashed:
                    _log_entry(status, phase["phase_num"], task["num"],
                               "Stashed HTML backup")
                _write_status(status)

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
                        if filepath.suffix == ".html":
                            html_ok, html_reason = check_html_syntax(str(filepath))
                            if not html_ok:
                                auto_rollback_html()
                                html_stashed = False
                                _log_entry(status, phase["phase_num"], task["num"],
                                           f"❌ ROLLBACK: HTML check failed — {html_reason}")
                                phase_ok = False
                                break
                            else:
                                _log_entry(status, phase["phase_num"], task["num"],
                                           "✅ HTML check passed")
                                subprocess.run(
                                    ["git", "stash", "drop"],
                                    capture_output=True, text=True, cwd=str(HERE),
                                )
                                html_stashed = False
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

            # Drop orphaned HTML stash if all attempts failed without explicit cleanup
            if html_stashed:
                subprocess.run(
                    ["git", "stash", "drop"],
                    capture_output=True, text=True, cwd=str(HERE),
                )
                html_stashed = False

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

    except Exception as exc:
        status["status"] = "ROLLED_BACK"
        _log_entry(status, 0, 0, f"ROLLED_BACK: unhandled exception — {str(exc)[:120]}")
        _write_status(status)
        clacker_safety.post_run_failure(run_id, str(HERE), stash_ref)
        raise

    # Run MOT test suite
    mot_score      = ""
    mot_returncode = -1
    if not _is_cancelled(run_id):
        _log_entry(status, 0, 0, "Running MOT test suite…")
        _write_status(status)
        try:
            result = subprocess.run(
                [sys.executable, str(MOT_SCRIPT)],
                capture_output=True, text=True, timeout=180, cwd=str(HERE),
            )
            mot_returncode = result.returncode
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

    # Run acceptance criteria validator
    validator_result = {}
    if not _is_cancelled(run_id):
        try:
            validator_result = clacker_validator.validate(
                acceptance_criteria,
                sorted(files_changed),
                mot_score,
                str(HERE),
            )
            _log_entry(status, 0, 0,
                       f"Validator: {validator_result.get('status','?')} — {validator_result.get('notes','')}")
        except Exception as exc:
            _log_entry(status, 0, 0, f"Validator error: {str(exc)[:80]}")

    # CLACKER stash safety: drop on MOT pass, pop (rollback) on MOT fail
    if not _is_cancelled(run_id):
        mot_passed = mot_returncode == 0 or "all clear" in mot_score.lower()
        if mot_passed:
            clacker_safety.post_run_success(run_id, str(HERE))
            _log_entry(status, 0, 0, "✅ MOT passed — stash dropped, changes kept")
        else:
            clacker_safety.post_run_failure(run_id, str(HERE), stash_ref)
            _log_entry(status, 0, 0, "🔴 MOT failed — rolled back to pre-OCB state")
    _write_status(status)

    status["mot_score"]   = mot_score
    completed_at          = datetime.now().isoformat(timespec="seconds")
    status["completed_at"] = completed_at

    if not _is_cancelled(run_id):
        status["status"] = "DONE" if not phases_failed else "PARTIAL"

    _write_status(status)

    # Write CLACHR response for the CLACHR panel auto-poll
    clachr = {
        "session_id":         run_id,
        "status":             status["status"],
        "phases_done":        phases_done,
        "phases_failed":      phases_failed,
        "files_changed":      sorted(files_changed),
        "mot_score":          mot_score,
        "completed_at":       completed_at,
        "acceptance_criteria": acceptance_criteria,
        "validator":          validator_result,
        "notes":              validator_result.get("notes", ""),
        "ocb_text":           ocb_text,
    }
    try:
        tmp = str(CLACHR_RESPONSE) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(clachr, f, indent=2)
        shutil.move(tmp, str(CLACHR_RESPONSE))
    except Exception:
        pass

    # Update session_state last_result + clear current_task
    _update_ss({
        "last_result": {
            "task": f"OCB run {run_id}",
            "status": status["status"],
            "mot_score": mot_score,
            "files_changed": sorted(files_changed),
            "completed_at": completed_at,
        },
        "current_task": {
            "type": "", "description": "", "subsystem": "",
            "status": "idle", "started_at": "",
        },
        "active_ocb_run_id": "",
    })

    return status


# ── Lifeguard Protocol helpers ────────────────────────────────────────────────

def _lp_now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _lp_now_file():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def _lp_now_date():
    return datetime.now().strftime("%Y-%m-%d")


# ── 1. WAL LOG ─────────────────────────────────────────────────────────────────

def wal_log(ocb_id, phase, intent, status="INTENT"):
    """Append one line to ocb_wal.log — append only, never delete."""
    line = f"[{_lp_now_ts()}] {status}: {ocb_id} Phase {phase} — {intent}\n"
    with open(WAL_LOG, "a", encoding="utf-8") as f:
        f.write(line)


# ── 2. PRE-MISSION SNAPSHOT ────────────────────────────────────────────────────

def pre_mission_snapshot(ocb_id):
    """Copy STATUS.md to status_snapshots/STATUS_pre_{ocb_id}_{timestamp}.md"""
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    if not STATUS_FILE.exists():
        print("  WARNING: STATUS.md not found — snapshot skipped")
        return None
    ts = _lp_now_file()
    filename = f"STATUS_pre_{ocb_id}_{ts}.md"
    dest = SNAPSHOTS_DIR / filename
    shutil.copy2(STATUS_FILE, dest)
    wal_log(ocb_id, "SNAPSHOT", f"Pre-mission snapshot saved: {filename}")
    print(f"  Pre-mission snapshot saved: {filename}")
    return dest


# ── 3. POST-PHASE BEACON ──────────────────────────────────────────────────────

def post_phase_beacon(ocb_id, phase, summary):
    """Write a 5-line beacon file and log COMPLETE to WAL."""
    SESSION_LOGS_DIR.mkdir(exist_ok=True)
    date = _lp_now_date()
    filename = f"ocb_beacon_{ocb_id}_{phase}_{date}.md"
    dest = SESSION_LOGS_DIR / filename
    content = (
        f"date: {_lp_now_ts()}\n"
        f"ocb_id: {ocb_id}\n"
        f"phase: {phase}\n"
        f"summary: {summary}\n"
        f"status: COMPLETE\n"
    )
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)
    wal_log(ocb_id, phase, summary, status="COMPLETE")
    print(f"  Post-phase beacon saved: {filename}")


# ── 4. DISTRESS SAVE ──────────────────────────────────────────────────────────

def distress_save(ocb_id, phase, error_msg):
    """Snapshot STATUS.md with FAIL prefix, flag stuck inbox, log FAILURE to WAL."""
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    ts = _lp_now_file()
    filename = f"STATUS_FAIL_{ocb_id}_{phase}_{ts}.md"
    dest = SNAPSHOTS_DIR / filename
    if STATUS_FILE.exists():
        shutil.copy2(STATUS_FILE, dest)

    wal_log(ocb_id, phase, error_msg, status="FAILURE")

    if STUCK_INBOX.exists():
        try:
            with open(STUCK_INBOX, "r", encoding="utf-8") as f:
                inbox = json.load(f)
            if not isinstance(inbox, list):
                inbox = [inbox]
        except (json.JSONDecodeError, ValueError):
            inbox = []
        inbox.append({
            "source": "OCBR",
            "ocb_id": ocb_id,
            "phase": phase,
            "error": error_msg,
            "timestamp": _lp_now_ts(),
            "severity": "high"
        })
        with open(STUCK_INBOX, "w", encoding="utf-8") as f:
            json.dump(inbox, f, indent=2)

    print("  DISTRESS SAVE triggered — snapshot + stuck inbox flagged")
    print(f"  Snapshot: {filename}")


# ── 5. SYNC MASTER COPY ───────────────────────────────────────────────────────

def sync_master_copy():
    """Overwrite STATUS_MASTER.md with current STATUS.md + updated header."""
    if not STATUS_FILE.exists():
        print("  ERROR: STATUS.md not found — sync aborted")
        return
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        status_content = f.read()
    header = (
        "# STATUS MASTER COPY — Golden backup. Only rewritten after MOT all-clear (108/108). Do not edit manually.\n"
        f"Last synced: {_lp_now_date()} | Source: STATUS.md\n\n"
    )
    with open(STATUS_MASTER, "w", encoding="utf-8") as f:
        f.write(header + status_content)
    wal_log("MASTER", "SYNC", "STATUS_MASTER updated after MOT all-clear", status="COMPLETE")
    print("  STATUS_MASTER.md synced — golden copy updated")


# ── 6. RECOVER ────────────────────────────────────────────────────────────────

def recover(ocb_id=None):
    """List snapshots and WAL entries since chosen snapshot. Print recovery plan."""
    if not SNAPSHOTS_DIR.exists():
        print("  No status_snapshots/ directory found.")
        return
    snapshots = sorted(SNAPSHOTS_DIR.glob("STATUS_pre_*.md"))
    if not snapshots:
        print("  No pre-mission snapshots found.")
        return
    if ocb_id:
        candidates = [s for s in snapshots if f"STATUS_pre_{ocb_id}_" in s.name]
        if not candidates:
            print(f"  No snapshots found for OCB ID: {ocb_id}")
            return
        chosen = candidates[-1]
    else:
        chosen = snapshots[-1]

    parts = chosen.stem.split("_")
    try:
        snap_ts_str = f"{parts[-2]}_{parts[-1]}"
        snap_dt = datetime.strptime(snap_ts_str, "%Y%m%d_%H%M%S")
        snap_ts_readable = snap_dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, IndexError):
        snap_ts_readable = "unknown"
        snap_dt = None

    print(f"\n  === RECOVERY PLAN ===")
    print(f"  Restore from: {chosen.name}")
    print(f"  Snapshot timestamp: {snap_ts_readable}")

    wal_entries = []
    if WAL_LOG.exists():
        with open(WAL_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if snap_dt is not None:
                    try:
                        entry_dt = datetime.strptime(line[1:20], "%Y-%m-%d %H:%M:%S")
                        if entry_dt > snap_dt:
                            wal_entries.append(line)
                    except ValueError:
                        pass
                else:
                    wal_entries.append(line)

    print(f"  WAL entries after snapshot: {len(wal_entries)}")
    if wal_entries:
        print("\n  WAL entries to replay:")
        for e in wal_entries:
            print(f"    {e}")

    print(f"\n  To restore manually:")
    print(f"    copy status_snapshots\\{chosen.name} STATUS.md")
    print(f"  Then review the {len(wal_entries)} WAL entries above and re-apply any completed work.")
    print(f"  === END RECOVERY PLAN ===\n")


# ── 7. GENERATE CLAC BLOCK ────────────────────────────────────────────────────

def generate_clac_block(ocb_id, description):
    """Print a formatted CLAC instruction block stub."""
    border = "=" * 64
    print(f"\n  {border}")
    print(f"  CLAC BLOCK -- {ocb_id}")
    print(f"  {border}")
    print(f"  DSP? (claude --dangerously-skip-permissions)")
    print(f"  {border}")
    print(f"\n  Read STATUS.md and INDEX.md.")
    print(f"  Build: {description}")
    print(f"  Run MOT after: python mcc_full_mot.py")
    print(f"  Report pass/fail. WCCS triggered automatically.\n")


# ── 8. RUN OCB ────────────────────────────────────────────────────────────────

def run_ocb(ocb_id, description):
    """Step 1: snapshot, Step 2: WAL log, Step 3: CLAC block."""
    print(f"\n  === OCB RUNNER: {ocb_id} ===")
    pre_mission_snapshot(ocb_id)
    wal_log(ocb_id, "START", description)
    generate_clac_block(ocb_id, description)
    print(f"  Ready. Run the CLAC block above.")
    print(f"  When done, call: python ocb_runner.py --complete {ocb_id}\n")


# ── QUEUE HELPERS ─────────────────────────────────────────────────────────────

def _load_queue():
    if not OCB_QUEUE.exists():
        return {"queue": [], "completed": [], "last_ocb": "", "last_mot": ""}
    with open(OCB_QUEUE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_queue(data):
    with open(OCB_QUEUE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _find_in_queue(ocb_id):
    q = _load_queue()
    for item in q.get("queue", []):
        if item["id"] == ocb_id:
            return item
    return None


# ── CLI COMMANDS ───────────────────────────────────────────────────────────────

def _cli_list():
    q = _load_queue()
    pending = [i for i in q.get("queue", []) if i.get("status") == "pending"]
    print(f"\n  === OCB QUEUE — PENDING ({len(pending)}) ===")
    for item in pending:
        print(f"  [{item['id']}] {item['description']}")
    completed = q.get("completed", [])
    if completed:
        print(f"\n  Completed: {', '.join(completed)}")
    print(f"  Last OCB: {q.get('last_ocb', 'none')}")
    print(f"  Last MOT: {q.get('last_mot', 'none')}\n")


def _cli_run(ocb_id):
    item = _find_in_queue(ocb_id)
    if not item:
        print(f"  ERROR: {ocb_id} not found in ocb_queue.json")
        print("  Use --list to see available OCBs")
        sys.exit(1)
    run_ocb(ocb_id, item["description"])


def _cli_complete(ocb_id):
    print(f"\n  === COMPLETE: {ocb_id} ===")
    try:
        summary = input("  Enter phase summary (or press Enter to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        summary = ""
    if not summary:
        summary = f"{ocb_id} phase completed"
    post_phase_beacon(ocb_id, "COMPLETE", summary)

    try:
        mot_result = input("  MOT result (e.g. 108/108 ALL CLEAR, or skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        mot_result = ""
    if mot_result:
        wal_log(ocb_id, "MOT", mot_result, status="MOT")
        if "ALL CLEAR" in mot_result or "108/108" in mot_result:
            print("\n  MOT all-clear detected — syncing master copy...")
            sync_master_copy()
            q = _load_queue()
            q["queue"] = [i for i in q.get("queue", []) if i["id"] != ocb_id]
            if ocb_id not in q.get("completed", []):
                q.setdefault("completed", []).append(ocb_id)
            q["last_ocb"] = ocb_id
            q["last_mot"] = f"{mot_result} {_lp_now_date()}"
            _save_queue(q)
    print("  Done.\n")


def _cli_sync_master():
    print("\n  === SYNC MASTER COPY ===")
    sync_master_copy()


def _cli_recover(ocb_id=None):
    recover(ocb_id)


def _cli_status():
    print("\n  === OCBR STATUS ===")
    if SNAPSHOTS_DIR.exists():
        snaps = sorted(SNAPSHOTS_DIR.glob("STATUS_pre_*.md"))
        if snaps:
            print(f"  Last snapshot:   {snaps[-1].name}")
        else:
            print("  Last snapshot:   none")
    else:
        print("  Snapshots dir:   not found")

    if STATUS_MASTER.exists():
        mtime = datetime.fromtimestamp(STATUS_MASTER.stat().st_mtime)
        print(f"  STATUS_MASTER:   last written {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("  STATUS_MASTER:   not found")

    if WAL_LOG.exists():
        with open(WAL_LOG, "r", encoding="utf-8") as f:
            lines = [l.rstrip() for l in f if l.strip() and not l.startswith("#")]
        recent = lines[-10:]
        print(f"\n  Last {len(recent)} WAL entries:")
        for line in recent:
            print(f"    {line}")
    else:
        print("  WAL log:         not found")
    print()


# ── MAIN ──────────────────────────────────────────────────────────────────────

def _lifeguard_cli():
    parser = argparse.ArgumentParser(
        description="OCBR — OCB Runner Lifeguard Protocol v0.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--run", metavar="OCB_ID", help="Start an OCB from the queue")
    parser.add_argument("--complete", metavar="OCB_ID", help="Mark an OCB phase complete")
    parser.add_argument("--sync-master", action="store_true", help="Sync STATUS_MASTER.md from STATUS.md")
    parser.add_argument("--recover", metavar="OCB_ID", nargs="?", const="__all__",
                        help="Show recovery plan (optional: filter by OCB ID)")
    parser.add_argument("--list", action="store_true", help="List pending OCBs in queue")
    parser.add_argument("--status", action="store_true", help="Show WAL entries + snapshot + master age")
    return parser


# ── Self-test / CLI entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    parser = _lifeguard_cli()
    args, _unknown = parser.parse_known_args()

    if args.run:
        _cli_run(args.run)
    elif args.complete:
        _cli_complete(args.complete)
    elif args.sync_master:
        _cli_sync_master()
    elif args.recover is not None:
        ocb_id_arg = None if args.recover == "__all__" else args.recover
        _cli_recover(ocb_id_arg)
    elif args.list:
        _cli_list()
    elif args.status:
        _cli_status()
    else:
        # Legacy self-test when no args given
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
        print("\nLifeguard Protocol v0.1 — use: python ocb_runner.py --status | --list | --run <ID>")
