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
OCB_ABORT_FILE   = HERE / "data" / "ocb_abort.json"
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
    r'[═=─\-]{3,}\s*PHASE\s+(\d+)\s*[—\-—]+\s*(.+?)\s*[═=─\-]{3,}',
    re.IGNORECASE,
)
# Fallback: match lines like "Phase 3 — Title" or "PHASE 3: Title"
_PHASE_FALLBACK = re.compile(
    r'^\s*(?:Phase|PHASE|STEP|TASK)\s+(\d+)\s*[—:\-]+\s*(.+)$',
    re.IGNORECASE | re.MULTILINE,
)
_TASK_LINE = re.compile(r'^\s*(\d+)\.\s+(.+)$')

_STOPWORDS = {
    "phase", "section", "lines", "add", "update", "create", "button", "panel",
    "function", "method", "class", "style", "color", "colour", "width", "height",
    "display", "return", "should", "using", "with", "that", "this", "from",
    "into", "each", "every", "show", "hide", "when", "after", "before",
}


# ── Parse ─────────────────────────────────────────────────────────────────────

_SEP_CHARS   = frozenset('═=─-')
_PH_NUM_RE   = re.compile(r'(?:Phase|STEP|TASK)\s+(\d+)', re.IGNORECASE)
_PH_NAME_RE  = re.compile(r'(?:Phase|STEP|TASK)\s+\d+\s*[—–:\-]+\s*(.+)', re.IGNORECASE)


def _is_sep_line(s: str) -> bool:
    """True if line starts with 3+ separator chars AND contains 'Phase/STEP/TASK N'."""
    if len(s) < 6 or s[0] not in _SEP_CHARS:
        return False
    n = 0
    for c in s[:8]:
        if c in _SEP_CHARS:
            n += 1
        else:
            break
    return n >= 3 and bool(_PH_NUM_RE.search(s))


def _body_tasks(body_lines: list) -> list:
    tasks = []
    for bl in body_lines[:1000]:
        m = _TASK_LINE.match(bl)
        if m:
            tasks.append({"num": int(m.group(1)), "text": m.group(2).strip()})
    return tasks


def _parse_ocb_block_inner(text: str) -> list:
    """
    O(n) line-scan parser. Four passes:
    1) Lines starting with 3+ sep chars + 'Phase N' (═══ Phase 1 — Title ═══)
    2) Bare 'Phase N — Title' lines
    3) Forgiving: any line starting with a number+dot or === is a new phase
    4) Fallback: entire text as one phase
    Hard cap: 10 000 lines, 1 000 body lines per phase.
    """
    lines = text.splitlines()
    phases: list = []
    cur_num  = None
    cur_name = None
    cur_body: list = []

    for raw in lines[:10000]:
        s = raw.strip()
        if _is_sep_line(s):
            if cur_num is not None:
                phases.append({"phase_num": cur_num, "phase_name": cur_name, "tasks": _body_tasks(cur_body)})
            nm = _PH_NUM_RE.search(s)
            try:
                cur_num = int(nm.group(1))
            except (ValueError, AttributeError):
                continue
            nm2 = _PH_NAME_RE.search(s)
            raw_name = nm2.group(1) if nm2 else ""
            cur_name = raw_name.rstrip('═=─- ').strip() or f"Phase {cur_num}"
            cur_body = []
        elif cur_num is not None:
            cur_body.append(raw)

    if cur_num is not None:
        phases.append({"phase_num": cur_num, "phase_name": cur_name, "tasks": _body_tasks(cur_body)})

    if phases:
        return phases

    # Pass 2: bare "Phase N — Title" lines (no leading separator chars)
    cur_num = cur_name = None
    cur_body = []
    _bare = re.compile(r'^\s*(?:Phase|STEP|TASK)\s+(\d+)\s*[—–:\-]+\s*(.+)$', re.IGNORECASE)
    for raw in lines[:10000]:
        m = _bare.match(raw)
        if m:
            if cur_num is not None:
                phases.append({"phase_num": cur_num, "phase_name": cur_name, "tasks": _body_tasks(cur_body)})
            try:
                cur_num = int(m.group(1))
                cur_name = m.group(2).strip()
                cur_body = []
            except ValueError:
                pass
        elif cur_num is not None:
            cur_body.append(raw)
    if cur_num is not None:
        phases.append({"phase_num": cur_num, "phase_name": cur_name, "tasks": _body_tasks(cur_body)})

    if phases:
        return phases

    # Pass 3: forgiving fallback — every line starting with N. or === is a new phase
    _forgiving_sep = re.compile(r'^\s*(?:(\d+)\s*[.):]\s+(.+)|={3,}\s*(.+?)\s*={0,})\s*$')
    cur_num = 0
    cur_name = None
    cur_body = []
    for raw in lines[:10000]:
        m = _forgiving_sep.match(raw)
        if m:
            if cur_num > 0 and cur_body:
                phases.append({"phase_num": cur_num, "phase_name": cur_name or f"Phase {cur_num}", "tasks": _body_tasks(cur_body)})
            cur_num += 1
            # Use the matched text as both phase name and first task
            label = m.group(2) or m.group(3) or raw.strip()
            cur_name = label[:60].strip()
            cur_body = [raw]
        elif cur_num > 0:
            cur_body.append(raw)

    if cur_num > 0 and cur_body:
        phases.append({"phase_num": cur_num, "phase_name": cur_name or f"Phase {cur_num}", "tasks": _body_tasks(cur_body)})

    if phases:
        return phases

    # Pass 4: treat entire text as one phase
    return [{"phase_num": 1, "phase_name": "Task Block", "tasks": _body_tasks(lines)}]


def parse_ocb_block(text: str) -> list:
    """
    Parse an OCB block with a 30-second hard timeout.
    Falls back to a single-phase block if parsing exceeds the limit.
    """
    import concurrent.futures as _cf
    try:
        with _cf.ThreadPoolExecutor(max_workers=1) as _ex:
            future = _ex.submit(_parse_ocb_block_inner, text)
            return future.result(timeout=30)
    except _cf.TimeoutError:
        # Hard fallback: return a single phase so the runner can continue
        lines = text.splitlines()[:10000]
        return [{"phase_num": 1, "phase_name": "Task Block (timeout fallback)", "tasks": _body_tasks(lines)}]
    except Exception:
        return [{"phase_num": 1, "phase_name": "Task Block (error fallback)", "tasks": []}]


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

    # Score each line using a ±50-line sliding window.
    # Capped at 2000 lines to prevent O(n²) blocking on large files.
    best_idx   = 0
    best_score = -1
    half_win   = 50
    scan_cap   = min(total, 2000)
    for i in range(scan_cap):
        chunk = " ".join(raw_lines[max(0, i - half_win): i + half_win + 1]).lower()
        score = sum(1 for kw in keywords if kw in chunk)
        if score > best_score:
            best_score = score
            best_idx   = i
        if best_score >= len(keywords):
            break  # All keywords found — stop scanning

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
    # Write compact progress file for MCC progress bar polling
    ph_list = status_obj.get("phases", [])
    if ph_list:
        try:
            ph_total = len(ph_list)
            ph_done = sum(1 for p in ph_list if (p.get("status") or "").upper() in ("DONE","FAILED","SKIPPED"))
            ph_cur = status_obj.get("current_phase", 0)
            ph_cur_name = next((p.get("phase_name","") for p in ph_list if p.get("phase_num") == ph_cur), "")
            prog = {
                "phases": [{"phase_num": p.get("phase_num"), "phase_name": p.get("phase_name",""),
                            "status": (p.get("status") or "PENDING").upper(),
                            "tasks_done": sum(1 for t in p.get("tasks",[]) if (t.get("status") or "").upper() in ("DONE","FAILED","SKIPPED")),
                            "tasks_total": len(p.get("tasks",[]))} for p in ph_list],
                "phase_current": ph_cur, "phase_name": ph_cur_name, "phase_total": ph_total,
                "percent": round(ph_done / ph_total * 100) if ph_total else 0,
                "status": status_obj.get("status", "RUNNING"),
                "current_stage": status_obj.get("current_stage", ""),
                "mot_score": status_obj.get("mot_score", ""),
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
            pf = OCB_STATUS_FILE.parent / "ocb_progress.json"
            ptmp = str(pf) + ".tmp"
            with open(ptmp, "w", encoding="utf-8") as pf_:
                json.dump(prog, pf_, indent=2)
            shutil.move(ptmp, str(pf))
        except Exception:
            pass


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


def _is_aborted() -> bool:
    """Check if user clicked ABORT via MCC (data/ocb_abort.json)."""
    try:
        if not OCB_ABORT_FILE.exists():
            return False
        return bool(json.loads(OCB_ABORT_FILE.read_text(encoding="utf-8")).get("abort"))
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
        ["git", "stash", "push", "-m", "pre-ocb-backup", "mission_control.html"],
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

            # Run Script task type: "run script: foo.py" or "execute foo.bat"
            task_lower = task["text"].lower()
            if task_lower.startswith("run script:") or task_lower.startswith("execute "):
                script_name = task["text"].split(":", 1)[-1].strip() if ":" in task["text"] else task["text"].split(None, 1)[-1].strip()
                script_path = HERE / script_name
                _log_entry(status, phase["phase_num"], task["num"], f"Run Script: {script_name}")
                _write_status(status)
                try:
                    cmd = [sys.executable, str(script_path)] if script_path.suffix == ".py" else [str(script_path)]
                    res = subprocess.run(cmd, capture_output=True, text=True,
                                        encoding="utf-8", errors="replace",
                                        timeout=120, cwd=str(HERE))
                    _log_entry(status, phase["phase_num"], task["num"],
                               f"exit={res.returncode} | {((res.stdout or '')+(res.stderr or '')).strip()[:200]}")
                    status["phases"][pi]["tasks"][ti]["status"] = "DONE" if res.returncode == 0 else "FAILED"
                    if res.returncode != 0:
                        phase_ok = False
                except Exception as exc:
                    _log_entry(status, phase["phase_num"], task["num"], f"Script error: {str(exc)[:80]}")
                    status["phases"][pi]["tasks"][ti]["status"] = "FAILED"
                    phase_ok = False
                _write_status(status)
                continue

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
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=180, cwd=str(HERE),
            )
            mot_returncode = result.returncode
            output = (result.stdout or "") + (result.stderr or "")
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


# ── v2 API: parse_ocb / pre_flight / run_safe / read_results / stream_log ─────

_LOCK_FILE        = HERE / ".ocb_running"
_live_output: list  = []
_check_results: dict = {}
_last_run_result: dict = {}

STATUS_STAGES = [
    "idle", "received", "parsing", "pre_flight",
    "locking", "stashing", "phase_running",
    "html_checking", "js_checking", "registry_checking",
    "mot_running", "committing", "complete", "failed", "rolled_back"
]
_current_stage: str = "idle"


def set_status(stage: str, detail: str = ""):
    """Update _current_stage, log the transition, and persist to OCB_STATUS_FILE."""
    global _current_stage
    _current_stage = stage
    msg = f"[STAGE:{stage}]" + (f" {detail}" if detail else "")
    stream_log(msg)
    try:
        data = json.loads(OCB_STATUS_FILE.read_text(encoding="utf-8")) if OCB_STATUS_FILE.exists() else {}
        data["current_stage"] = stage
        data["stage_detail"] = detail
        _write_status(data)
    except Exception:
        pass

_JS_BUILTINS = {
    "if","for","while","switch","do","try","catch","finally","return","typeof",
    "instanceof","new","delete","void","throw","in","of","let","const","var",
    "parseInt","parseFloat","isNaN","isFinite","encodeURIComponent",
    "decodeURIComponent","encodeURI","decodeURI","eval","atob","btoa",
    "clearInterval","setInterval","setTimeout","clearTimeout","requestAnimationFrame",
    "fetch","JSON","Object","Array","String","Number","Boolean","Math","Date",
    "RegExp","Function","Error","Promise","Map","Set","WeakMap","WeakSet",
    "Symbol","Proxy","Reflect","Uint8Array","Int32Array","Float64Array","ArrayBuffer",
    "console","document","window","event","location","navigator","history","screen",
    "performance","localStorage","sessionStorage","XMLHttpRequest","WebSocket","Worker",
    "Blob","URL","alert","confirm","prompt","open","close","postMessage",
    "addEventListener","removeEventListener","dispatchEvent",
    "querySelector","querySelectorAll","getElementById","getElementsByClassName",
    "getElementsByTagName","createElement","createTextNode","getAttribute",
    "setAttribute","removeAttribute","appendChild","removeChild","insertBefore",
    "replaceChild","scrollIntoView","focus","blur","click","submit",
    "undefined","null","true","false","NaN","Infinity","this","super","arguments",
    "constructor","prototype","hasOwnProperty","toString","valueOf",
    "log","warn","error","info","debug",
}


def stream_log(msg: str):
    """Append timestamped msg to _live_output and update OCB_STATUS_FILE for polling."""
    global _live_output
    ts    = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    _live_output.append(entry)
    if len(_live_output) > 500:
        _live_output[:] = _live_output[-500:]
    try:
        data = json.loads(OCB_STATUS_FILE.read_text(encoding="utf-8")) if OCB_STATUS_FILE.exists() else {}
        data["live_output"] = list(_live_output)
        _write_status(data)
    except Exception:
        pass


def parse_ocb(text: str) -> list:
    """Extended parse: returns [{phase, phase_name, task_type, files_affected, commands, risk_level, tasks}]."""
    result = []
    for p in parse_ocb_block(text):
        files_affected: list = []
        commands: list       = []
        for task in p["tasks"]:
            fname = identify_affected_file(task["text"]).name
            if fname not in files_affected:
                files_affected.append(fname)
            if re.search(r'\b(run|execute|install|python|pip)\b', task["text"], re.I):
                commands.append(task["text"][:80])
        if "mission_control.html" in files_affected:
            risk = "HIGH"
        elif any(f.endswith(".py") for f in files_affected):
            risk = "MEDIUM"
        else:
            risk = "LOW"
        result.append({
            "phase":          p["phase_num"],
            "phase_name":     p["phase_name"],
            "tasks":          p["tasks"],
            "task_type":      "code_edit",
            "files_affected": files_affected,
            "commands":       commands,
            "risk_level":     risk,
        })
    return result


def pre_flight(parsed: list) -> dict:
    """Return preview dict: {files, risk, html_flag, warnings, phase_count}."""
    all_files: list = []
    max_risk        = "LOW"
    _rord           = {"HIGH": 2, "MEDIUM": 1, "LOW": 0}
    warnings: list  = []
    for phase in parsed:
        for f in phase.get("files_affected", []):
            if f not in all_files:
                all_files.append(f)
        r = phase.get("risk_level", "LOW")
        if _rord.get(r, 0) > _rord.get(max_risk, 0):
            max_risk = r
    html_flag = "mission_control.html" in all_files
    if html_flag:
        warnings.append("JS integrity check will run after edit")
    return {
        "files": all_files, "risk": max_risk, "html_flag": html_flag,
        "warnings": warnings, "phase_count": len(parsed),
    }


def _check_js_integrity(html_path: str) -> tuple:
    """CHECK B — JS integrity. Returns (ok, details_dict)."""
    try:
        from bs4 import BeautifulSoup
        with open(html_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        soup = BeautifulSoup(content, "html.parser")

        script_texts = [s.string for s in soup.find_all("script") if s.string]
        all_scripts  = "\n".join(script_texts)

        defined = set(re.findall(r'function\s+(\w+)\s*\(', all_scripts))
        defined.update(re.findall(r'(?:window|this)\.(\w+)\s*=\s*function', all_scripts))
        defined.update(re.findall(r'(?:var|let|const)\s+(\w+)\s*=\s*function', all_scripts))

        ev_attrs = ["onclick","onchange","onsubmit","onkeydown","onkeyup","oninput"]
        called: set = set()
        for tag in soup.find_all(True):
            for attr in ev_attrs:
                val = tag.get(attr) or ""
                if not val:
                    continue
                for m in re.finditer(r'(?<!\.)(\b[a-zA-Z_]\w*)\s*\(', val):
                    fn = m.group(1)
                    if fn not in _JS_BUILTINS:
                        called.add(fn)

        missing_funcs = [fn for fn in called if fn not in defined]

        id_calls = set(re.findall(r"getElementById\(['\"](\w[\w-]*)['\"]", all_scripts))
        dom_ids  = {tag["id"] for tag in soup.find_all(id=True)}
        missing_ids = [iid for iid in id_calls if iid not in dom_ids]

        if missing_funcs or missing_ids:
            det: dict = {}
            if missing_funcs:
                det["missing_functions"] = missing_funcs[:20]
            if missing_ids:
                det["missing_ids"] = missing_ids[:20]
            return False, det
        return True, {"defined": len(defined), "called": len(called), "id_calls": len(id_calls)}
    except Exception as exc:
        return False, {"error": str(exc)[:200]}


def _check_element_registry(html_path: str) -> tuple:
    """CHECK C — Element registry. Returns (ok, details_dict)."""
    reg_path = HERE / "data" / "element_registry.json"
    if not reg_path.exists():
        return True, {"note": "element_registry.json not found — skipped"}
    try:
        elements = json.loads(reg_path.read_text(encoding="utf-8")).get("elements", [])
        with open(html_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        dom_ids = set(re.findall(r'id=["\']([^"\']+)["\']', content))
        missing = [e["id"] for e in elements if e.get("id") and e["id"] not in dom_ids]
        if missing:
            return False, {"missing_registry_ids": missing[:20]}
        return True, {"checked": len(elements)}
    except Exception as exc:
        return False, {"error": str(exc)[:200]}


def _run_mot_check() -> tuple:
    """CHECK D — MOT. Returns (ok, score_str)."""
    try:
        r      = subprocess.run([sys.executable, str(MOT_SCRIPT)],
                                capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=180, cwd=str(HERE))
        output = (r.stdout or "") + (r.stderr or "")
        score  = ""
        for line in output.splitlines():
            if "passed" in line.lower() and ("failed" in line.lower() or "/" in line):
                score = line.strip(); break
        if not score:
            for line in output.splitlines():
                if "verdict" in line.lower() or "all clear" in line.lower():
                    score = line.strip(); break
        if not score:
            score = f"exit {r.returncode}"
        return r.returncode == 0 or "all clear" in score.lower(), score
    except Exception as exc:
        return False, f"MOT error: {str(exc)[:80]}"


def run_safe(parsed: list, run_id: str = "", dry_run: bool = False,
             skip_mot: bool = False) -> dict:
    """Full safe OCB execution: 4 guards + 4 HTML checks (BS4/JS/Registry/MOT)."""
    print("[THREAD] Thread function entered")
    print("[THREAD] run_safe() entered")
    global _live_output, _check_results, _last_run_result
    _live_output = []
    if not run_id:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[OCB THREAD] Started — run_id={run_id} dry_run={dry_run}")

    obj: dict = {
        "run_id": run_id, "started_at": datetime.now().isoformat(timespec="seconds"),
        "status": "RUNNING", "current_stage": "received", "stage_detail": "",
        "live_output": [], "guard_results": {
            "lock": None, "stash": None, "bs4": None, "js": None, "registry": None, "mot": None,
        }, "check_results": {}, "files_changed": [], "git_diff_stat": "",
        "rollback_available": False, "error": "", "stash_ref": None,
        "current_phase": 0, "mot_score": "",
        "phases": [
            {"phase_num": p2["phase"], "phase_name": p2.get("phase_name",""), "status": "PENDING",
             "tasks": [{"num": t2["num"], "text": t2["text"][:80], "status": "PENDING"} for t2 in p2.get("tasks",[])]}
            for p2 in parsed
        ],
    }
    _write_status(obj)

    def _sl(msg: str):
        stream_log(msg)
        obj["live_output"] = list(_live_output)
        _write_status(obj)

    # GUARD 1 — Lock file
    set_status("locking", "checking .ocb_running lock file")
    obj["current_stage"] = "locking"
    obj["live_output"] = list(_live_output)
    _write_status(obj)
    if _LOCK_FILE.exists():
        try:
            lock_age = time.time() - _LOCK_FILE.stat().st_mtime
        except Exception:
            lock_age = 999
        if lock_age > 600:  # stale lock — older than 10 minutes, process is dead
            try:
                _LOCK_FILE.unlink(missing_ok=True)
            except Exception:
                pass
            _sl(f"GUARD 1: stale lock cleared (age {lock_age:.0f}s) — continuing")
        else:
            msg = "Another OCB is running (.ocb_running exists)"
            obj["guard_results"]["lock"] = False
            obj.update({"status": "BLOCKED", "error": msg, "current_stage": "failed"})
            _sl(f"GUARD 1 FAIL: {msg}")
            _write_status(obj)
            _last_run_result = obj
            _check_results   = {}
            return obj

    obj["guard_results"]["lock"] = True
    _sl("GUARD 1 PASS: lock file clear")
    print("[THREAD] Lock check passed")

    if dry_run:
        _sl("DRY RUN: stopping here — no changes made")
        obj["status"] = "DRY_RUN"
        _write_status(obj)
        _last_run_result = obj
        return obj

    _LOCK_FILE.write_text(datetime.now().isoformat(), encoding="utf-8")
    no_stash  = False
    stash_ref = None

    try:
        # GUARD 2 — Clean tree check / stash
        set_status("stashing", "checking git working tree")
        print(f"[OCB THREAD] About to git stash")
        gs = subprocess.run(["git", "status", "--porcelain"],
                            capture_output=True, text=True, cwd=str(HERE), timeout=30)
        print("[THREAD] Git status checked")
        if gs.stdout.strip():
            ts_lbl = f"OCB-Runner-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            sr     = subprocess.run(["git", "stash", "push", "-m", ts_lbl],
                                    capture_output=True, text=True, cwd=str(HERE), timeout=30)
            stash_out = (sr.stdout + sr.stderr).strip()
            stash_ref = ts_lbl if "saved" in stash_out.lower() else None
            obj["stash_ref"] = stash_ref
            obj["guard_results"]["stash"] = True
            _sl(f"GUARD 2: dirty tree stashed ({ts_lbl})")
        else:
            no_stash = True
            obj["guard_results"]["stash"] = True
            _sl("GUARD 2: clean tree — no stash needed")
        print("[THREAD] Git stash done")

        # GUARD 3 — Phase execution (sequential, stop on first fail)
        set_status("phase_running", "starting phase execution")
        files_changed:   set  = set()
        html_was_edited: bool = False
        failed_reason: str    = ""

        print(f"[THREAD] About to execute phase 1")
        for ph_idx, phase in enumerate(parsed):
            if failed_reason:
                if ph_idx < len(obj["phases"]):
                    obj["phases"][ph_idx]["status"] = "SKIPPED"
                break
            if _is_aborted():
                obj["status"] = "CANCELLED"
                _sl(f"⛔ Aborted by user before Phase {phase['phase']}: {phase.get('phase_name','')}")
                _write_status(obj)
                break
            obj["current_phase"] = phase["phase"]
            if ph_idx < len(obj["phases"]):
                obj["phases"][ph_idx]["status"] = "RUNNING"
            set_status("phase_running", f"Phase {phase['phase']}: {phase.get('phase_name','')}")
            _sl(f"Phase {phase['phase']}: {phase.get('phase_name','')}")
            for task in phase.get("tasks", []):
                if failed_reason:
                    break
                if _is_aborted():
                    failed_reason = f"Aborted by user at Phase {phase['phase']} Task {task.get('num','?')}"
                    _sl(f"⛔ {failed_reason}")
                    obj["status"] = "CANCELLED"
                    _write_status(obj)
                    break
                _sl(f"  Task {task['num']}: {task['text'][:70]}")

                # ── Direct: run script ────────────────────────────────────────
                _tl = task["text"].lower().strip()
                if _tl.startswith("run script:") or (_tl.startswith("execute ") and not _tl.startswith("execute the")):
                    _sname = task["text"].split(":", 1)[-1].strip() if ":" in task["text"] else task["text"].split(None, 1)[-1].strip()
                    _spath = HERE / _sname
                    _sl(f"  Run Script: {_sname}")
                    try:
                        _cmd = [sys.executable, str(_spath)] if _spath.suffix == ".py" else [str(_spath)]
                        _sr = subprocess.run(_cmd, capture_output=True, text=True,
                                            encoding="utf-8", errors="replace",
                                            timeout=120, cwd=str(HERE))
                        _sl(f"  exit={_sr.returncode} | {((_sr.stdout or '')+(_sr.stderr or '')).strip()[:200]}")
                        if _sr.returncode != 0:
                            failed_reason = f"Script {_sname} exited {_sr.returncode}"
                            _sl(f"  FAIL: {failed_reason}")
                    except Exception as _se:
                        failed_reason = f"Script error: {str(_se)[:80]}"
                        _sl(f"  FAIL: {failed_reason}")
                    continue

                # ── Direct: create / write file ───────────────────────────────
                _cfm = re.search(
                    r'(?:create|write(?:\s+to)?)\s+(?:a\s+)?(?:new\s+)?file\s+(?:called\s+|named\s+)?["\']?([^\s"\'<>:|?*]+\.[a-zA-Z0-9]+)["\']?',
                    task["text"], re.IGNORECASE,
                )
                if _cfm:
                    _cfname = _cfm.group(1).strip()
                    _cftarget = HERE / _cfname
                    _ccm = re.search(
                        r'(?:content[:\s]+|write(?:\s+this)?(?:\s+exact)?(?:\s+content)?[:\s]+)["\']?(.+?)(?:["\']?\s*$)',
                        task["text"], re.IGNORECASE | re.DOTALL,
                    )
                    _cfcontent = _ccm.group(1).strip() if _ccm else f"# Created by OCB Runner\n# Task: {task['text'][:80]}\n"
                    try:
                        _cftarget.parent.mkdir(parents=True, exist_ok=True)
                        _cftarget.write_text(_cfcontent, encoding="utf-8")
                        files_changed.add(_cfname)
                        _sl(f"  DONE: created {_cfname} ({len(_cfcontent)} chars)")
                    except Exception as _cfe:
                        failed_reason = f"File create failed: {str(_cfe)[:80]}"
                        _sl(f"  FAIL: {failed_reason}")
                    continue

                filepath = identify_affected_file(task["text"])
                ext      = filepath.suffix.lower()
                try:
                    sd = extract_relevant_section(filepath, task["text"])
                    if not sd["section_text"]:
                        _sl(f"  SKIP: cannot read {filepath.name}"); continue
                    new_text = run_task(filepath, sd, task["text"])
                    if not new_text:
                        failed_reason = f"AI returned empty for task: {task['text'][:60]}"
                        _sl(f"  FAIL: {failed_reason}"); break
                    ok = apply_result(filepath, sd["start_line"], sd["end_line"], new_text)
                    if not ok:
                        failed_reason = f"Apply/syntax check failed for {filepath.name}"
                        _sl(f"  FAIL: {failed_reason}"); break
                    files_changed.add(filepath.name)
                    _sl(f"  DONE: {filepath.name} updated")

                    if ext == ".html":
                        html_was_edited  = True
                        hp               = str(filepath)
                        # CHECK A — BS4
                        set_status("html_checking", "BS4 structure check")
                        try:
                            from bs4 import BeautifulSoup
                            with open(hp, "r", encoding="utf-8") as fh:
                                BeautifulSoup(fh.read(), "html.parser")
                            obj["guard_results"]["bs4"] = True
                            obj["check_results"]["A_bs4"] = {"ok": True}
                            _sl("  CHECK A (BS4): PASS")
                        except Exception as e:
                            obj["guard_results"]["bs4"] = False
                            obj["check_results"]["A_bs4"] = {"ok": False, "error": str(e)[:120]}
                            failed_reason = f"CHECK A (BS4) failed: {str(e)[:80]}"
                            _sl(f"  CHECK A (BS4): FAIL"); break
                        # CHECK B — JS integrity
                        set_status("js_checking", "JS function integrity check")
                        js_ok, js_det = _check_js_integrity(hp)
                        obj["guard_results"]["js"] = js_ok
                        obj["check_results"]["B_js"] = {"ok": js_ok, "details": js_det}
                        if js_ok:
                            _sl("  CHECK B (JS): PASS")
                        else:
                            failed_reason = f"CHECK B (JS) failed: {js_det}"
                            _sl(f"  CHECK B (JS): FAIL — {js_det}"); break
                        # CHECK C — Element registry
                        set_status("registry_checking", "element registry cross-check")
                        reg_ok, reg_det = _check_element_registry(hp)
                        obj["guard_results"]["registry"] = reg_ok
                        obj["check_results"]["C_registry"] = {"ok": reg_ok, "details": reg_det}
                        if reg_ok:
                            _sl("  CHECK C (Registry): PASS")
                        else:
                            failed_reason = f"CHECK C (registry) failed: {reg_det}"
                            _sl(f"  CHECK C (Registry): FAIL"); break
                except Exception as exc:
                    failed_reason = f"Exception: {str(exc)[:100]}"
                    _sl(f"  ERROR: {failed_reason}"); break
            if ph_idx < len(obj["phases"]):
                obj["phases"][ph_idx]["status"] = "FAILED" if failed_reason else "DONE"
            _write_status(obj)
            print(f"[OCB THREAD] Phase {phase.get('phase', '')} complete")

        if not html_was_edited:
            for k in ("bs4", "js", "registry"):
                if obj["guard_results"][k] is None:
                    obj["guard_results"][k] = True
            for k, lbl in (("A_bs4","BS4"),("B_js","JS"),("C_registry","Registry")):
                if k not in obj["check_results"]:
                    obj["check_results"][k] = {"ok": True, "note": "no HTML edited"}

        obj["files_changed"] = sorted(files_changed)

        if failed_reason:
            # GUARD 4 — Rollback on failure
            if not no_stash and stash_ref:
                set_status("rolled_back", failed_reason[:80])
                subprocess.run(["git", "stash", "pop"],
                               capture_output=True, text=True, cwd=str(HERE), timeout=30)
                obj["status"] = "ROLLED_BACK"
                _sl(f"ROLLED BACK — {failed_reason}")
            else:
                set_status("failed", failed_reason[:80])
                obj["status"] = "FAILED"
                obj["rollback_available"] = True
                _sl(f"FAILED — {failed_reason}")
            obj["guard_results"]["mot"] = False
            obj["check_results"]["D_mot"] = {"ok": False, "error": failed_reason}
            obj["error"] = failed_reason
        else:
            # CHECK D — MOT (skipped if skip_mot=True)
            if skip_mot:
                mot_score = "SKIPPED (skip_mot=True)"
                obj["guard_results"]["mot"] = True
                obj["check_results"]["D_mot"] = {"ok": True, "score": mot_score, "skipped": True}
                obj["mot_score"] = mot_score
                _sl(f"CHECK D (MOT): SKIPPED — non-HTML task flag set")
                mot_ok = True
            else:
                set_status("mot_running", "running mcc_full_mot.py")
                _sl("Running MOT check…")
                print(f"[OCB THREAD] About to run MOT")
                mot_ok, mot_score = _run_mot_check()
                obj["guard_results"]["mot"] = mot_ok
                obj["check_results"]["D_mot"] = {"ok": mot_ok, "score": mot_score}
                obj["mot_score"] = mot_score
                _sl(f"CHECK D (MOT): {'PASS' if mot_ok else 'FAIL'} — {mot_score}")
            if mot_ok:
                set_status("committing", "MOT passed — committing changes")
                if not no_stash and stash_ref:
                    subprocess.run(["git", "stash", "drop"],
                                   capture_output=True, text=True, cwd=str(HERE), timeout=30)
                summary = "; ".join(t["text"][:40] for p in parsed for t in p.get("tasks",[]))[:120]
                subprocess.run(["git", "add", "-A"],
                               capture_output=True, text=True, cwd=str(HERE), timeout=30)
                subprocess.run(["git", "commit", "-m", f"OCB-Runner: {summary}"],
                               capture_output=True, text=True, cwd=str(HERE), timeout=30)
                dr = subprocess.run(["git", "diff", "--stat", "HEAD~1", "HEAD"],
                                    capture_output=True, text=True, cwd=str(HERE), timeout=30)
                obj["git_diff_stat"] = dr.stdout[:2000]
                obj["status"] = "DONE"
                set_status("complete", f"MOT {mot_score}")
                _sl("All guards passed — changes committed")
            else:
                if not no_stash and stash_ref:
                    set_status("rolled_back", f"MOT failed: {mot_score}")
                    subprocess.run(["git", "stash", "pop"],
                                   capture_output=True, text=True, cwd=str(HERE), timeout=30)
                    obj["status"] = "ROLLED_BACK"
                    _sl(f"ROLLED BACK — MOT failed: {mot_score}")
                else:
                    set_status("failed", f"MOT failed: {mot_score}")
                    obj["status"] = "FAILED"
                    obj["rollback_available"] = True
                    obj["stash_ref"] = "HEAD"
                    _sl(f"MOT FAILED — {mot_score}")
    except Exception as e:
        print(f"[THREAD] TOP-LEVEL EXCEPTION: {e}")
        import traceback; print(traceback.format_exc())
        print(f"[OCB THREAD] EXCEPTION: {e}")
        import traceback as _tb; print(_tb.format_exc())
        obj["status"] = "failed"
        obj["current_stage"] = "failed"
        stream_log(f"THREAD CRASH: {str(e)}")
        stream_log(f"Type: {type(e).__name__}")
        stream_log(_tb.format_exc())
        import os as _eos
        if _eos.path.exists(str(_LOCK_FILE)):
            try:
                _LOCK_FILE.unlink(missing_ok=True)
            except Exception:
                pass
        _write_status(obj)
        _last_run_result = obj
        _check_results = {}
    finally:
        try:
            _LOCK_FILE.unlink(missing_ok=True)
        except Exception:
            pass
        _sl("Lock file released")
        global _current_stage
        if _current_stage not in ("complete", "failed", "rolled_back"):
            _current_stage = "idle"

    obj["completed_at"] = datetime.now().isoformat(timespec="seconds")
    _write_status(obj)
    _last_run_result = obj
    _check_results   = obj["check_results"]
    return obj


def read_results() -> dict:
    """Return enriched last run: file line deltas, check results, git diff stat, pass/fail."""
    global _last_run_result
    out = dict(_last_run_result)
    file_details = []
    for fname in out.get("files_changed", []):
        added = removed = 0
        try:
            dr = subprocess.run(
                ["git", "diff", "--numstat", "HEAD~1", "HEAD", "--", fname],
                capture_output=True, text=True, cwd=str(HERE), timeout=15,
            )
            parts = dr.stdout.strip().split()
            if len(parts) >= 2:
                added   = int(parts[0]) if parts[0] != "-" else 0
                removed = int(parts[1]) if parts[1] != "-" else 0
        except Exception:
            pass
        file_details.append({"name": fname, "lines_added": added, "lines_removed": removed})
    out["file_details"] = file_details
    out["live_output"]  = list(_live_output)
    return out


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


# ── Synchronous test mode ─────────────────────────────────────────────────────

def run_test():
    """Synchronous test run — exercises the full autonomous pipeline."""
    print("[TEST] Starting autonomous OCB test run")

    test_ocb = """
═══ PHASE 1 — CREATE FILE TEST ═══

1. Create a file called ocb_test_output.txt with content: OCB Runner test successful
"""
    print("[TEST] Parsing OCB block...")
    try:
        parsed = parse_ocb(test_ocb)
        print(f"[TEST] Phases found: {len(parsed)}")
        for p in parsed:
            print(f"  Phase {p['phase']}: {p['phase_name']} — {len(p['tasks'])} tasks")
            for t in p["tasks"]:
                print(f"    {t['num']}. {t['text']}")
    except Exception as e:
        print(f"[TEST] PARSE FAILED: {e}")
        import traceback; traceback.print_exc()
        return

    print("[TEST] Running run_safe() — full autonomous pipeline...")
    test_file = HERE / "ocb_test_output.txt"
    if test_file.exists():
        test_file.unlink()
        print("[TEST] Cleaned up pre-existing test file")

    try:
        result = run_safe(parsed, run_id="test_" + datetime.now().strftime("%H%M%S"))
        print(f"\n[TEST] run_safe status: {result.get('status')}")
        print("[TEST] Live output:")
        for line in result.get("live_output", []):
            print(f"  {line}")
    except Exception as e:
        print(f"[TEST] run_safe FAILED: {e}")
        import traceback; traceback.print_exc()

    if test_file.exists():
        content = test_file.read_text(encoding="utf-8").strip()
        print(f"\n[TEST] PASS — ocb_test_output.txt exists with content: {content!r}")
    else:
        print(f"\n[TEST] FAIL — ocb_test_output.txt was NOT created")
    print("[TEST] COMPLETE")


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
    if "--test" in sys.argv:
        run_test()
        sys.exit(0)
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
