"""
sfl_agent.py — Screenshot Feedback Loop Agent v3
VKB Spin Doctor
================================================
v2 IMPROVEMENTS (still active):
  1. Project folder path injected into every Claude message
  2. Running memory — Claude sees all previous commands + outputs
  3. Iteration limit is configurable + asks Y/N to continue at the limit
  4. Agent can ask Scott a question mid-task via "ask_user"
  5. Full log saved automatically to sfl_logs/ folder
  6. Expanded safe command list — fewer unnecessary Y/N prompts
  7. Context flags — pass --folder and --note at task prompt
  8. Handover injection — PROJECT_HANDOVER.md prepended to prompt

v3 AUTONOMY CONTROL PANEL v1 (handover v13 — 4 features):
  A. Heartbeats — every 30 s the agent prints one status line (iter,
     phase, elapsed, tokens). Watch it scroll. Ctrl+C anytime to stop.
     Replaces per-step approvals for safe ops.
  B. Safe-op allow-list — reads, syntax checks, --help, --dry-run auto-
     run. Commands touching more than 5 files OR matching the delete
     blacklist are forced to ask, overriding the safe list
     (the "watcher is theatre" WMBW fix from v13).
  C. Auto-snapshot — before any approved non-safe command, editable
     project files are copied to backups/auto_YYYYMMDD_HHMMSS/. Last 20
     kept; older pruned. No git required.
  D. Token budget — optional --budget flag. Soft cap (80 %) = finish
     current iteration, stop before next Claude call. Hard cap (100 %) =
     stop immediately at the next natural breakpoint.

HOW TO RUN:
  Run as Admin: Windows key + X -> Terminal (Admin)

  C:\\Users\\jscot\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe "C:\\Users\\jscot\\OneDrive\\Desktop\\VKB-SpinDoctor\\sfl_agent.py"

  Optional flags you can add to your task:
    --folder C:\\path\\to\\folder   (overrides default project folder)
    --note "extra context"          (adds a note Claude sees every loop)
    --budget 50k                    (token cap — e.g. 50k, 100000, 1m)

  Example task:
    Read spin_doctor.py and add Elite Dangerous support --note "binds file in AppData" --budget 80k

STOP: Ctrl + C
"""

import os
import base64
import json
import re
import shutil
import threading
import time
import mss
import subprocess
from aafl_core import AAFLCore
from PIL import Image
import io
from collections import Counter
from datetime import datetime
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────
from config import PROJECT_ROOT
DEFAULT_WORK_FOLDER = str(PROJECT_ROOT)
MAX_TOKENS          = 2048
DEFAULT_MAX_ITER    = 50
MEMORY_MAX_CHARS    = 6000
LOG_FOLDER          = Path(DEFAULT_WORK_FOLDER) / "sfl_logs"

# ── Autonomy Control Panel v1 settings (handover v13) ────────────────────────
HEARTBEAT_INTERVAL_SEC = 30          # (A) one status line every N seconds
SOFT_CAP_PCT           = 80          # (D) finish current iter, no new Claude calls
HARD_CAP_PCT           = 100         # (D) stop immediately
AUTO_SNAPSHOT_KEEP     = 20          # (C) retain this many recent snapshots
AUTO_SNAPSHOT_PREFIX   = "auto_"     # legacy prefix (still pruned for back-compat)
SESSION_SNAPSHOT_RE    = re.compile(r"^v\d{2}_")  # FEATURE 1: vNN_<slug>/
SNAPSHOT_EXTENSIONS    = {".py", ".json", ".xml", ".blk", ".binds",
                          ".md", ".bat", ".txt", ".cfg", ".ini", ".csv"}
SNAPSHOT_EXCLUDE_DIRS  = {"backups", "sfl_logs", "__pycache__",
                          ".git", ".venv", "venv", "env", ".idea", ".vscode"}
TOUCH_FILES_ASK_THRESH = 5           # (B) >N file args forces an ask (overrides safe)

# Dead-end detector: stop and ask Scott if the same error appears
# DEAD_END_THRESHOLD or more times in the last DEAD_END_WINDOW outputs.
DEAD_END_WINDOW    = 5
DEAD_END_THRESHOLD = 3

BLACKLIST = ["del ", "rm ", "format ", "rmdir", "shutdown", "remove-item"]

# Fix 6 + v3 (B): safe allow-list. Substring match on lowercased command.
SAFE_PATTERNS = [
    # v2 list — read-only verbs and pip introspection
    "get-childitem", "dir ", "ls ", "echo ", "type ", "cat ",
    "get-content", "select-object", "where-object", "format-table",
    "write-output", "get-item", "test-path", "resolve-path",
    "python ", "pip show", "pip list", "pip freeze",
    "where python", "where pip",
    "get-process", "get-service", "get-variable", "get-location",
    "get-command", "get-alias", "get-date", "hostname",
    "-recurse", "-filter", "select-string", "findstr",
    "split-path", "join-path",
    # v3 additions — help, version, dry-run, syntax-check, read-only git
    " --help", " /help", " /?", " --version", " -h ",
    " --dry-run", " --check", " -whatif",
    "py_compile", "python -m ast", "python -m json.tool",
    "node --check", "git status", "git diff", "git log",
]


# ── Fix 7: Parse flags from task string ──────────────────────────────────────

def parse_task(raw_task):
    """Extract --folder, --note, and --budget flags.
    Returns (clean_task, work_folder, extra_note, budget_tokens_or_None)."""
    work_folder = DEFAULT_WORK_FOLDER
    extra_note  = ""
    budget      = None

    folder_match = re.search(r'--folder\s+"([^"]+)"', raw_task)
    if not folder_match:
        folder_match = re.search(r'--folder\s+(\S+)', raw_task)
    if folder_match:
        work_folder = folder_match.group(1)
        raw_task = raw_task[:folder_match.start()] + raw_task[folder_match.end():]

    note_match = re.search(r'--note\s+"([^"]+)"', raw_task)
    if not note_match:
        note_match = re.search(r'--note\s+(.+?)(?:--|$)', raw_task)
    if note_match:
        extra_note = note_match.group(1).strip()
        raw_task = raw_task[:note_match.start()] + raw_task[note_match.end():]

    budget_match = re.search(r'--budget\s+(\S+)', raw_task)
    if budget_match:
        budget = parse_budget(budget_match.group(1))
        raw_task = raw_task[:budget_match.start()] + raw_task[budget_match.end():]

    return raw_task.strip(), work_folder, extra_note, budget


def parse_budget(text):
    """Parse '50k', '1.5m', '100000' into integer token count.
    Returns None on invalid input (treated as no cap)."""
    text = text.strip().lower().replace(",", "").replace("_", "")
    mult = 1
    if text.endswith("k"):
        mult, text = 1_000, text[:-1]
    elif text.endswith("m"):
        mult, text = 1_000_000, text[:-1]
    try:
        return int(float(text) * mult)
    except (ValueError, TypeError):
        return None


# ── Fix 5: Logger ─────────────────────────────────────────────────────────────

class Logger:
    def __init__(self, task):
        LOG_FOLDER.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        safe_task = re.sub(r'[^a-zA-Z0-9_]', '_', task[:40])
        self.path = LOG_FOLDER / f"{timestamp}_{safe_task}.txt"
        self._write(f"SFL Agent v2 Log\nStarted: {datetime.now()}\nTask: {task}\n{'='*60}\n")
        print(f"[LOG] Saving to: {self.path}")

    def _write(self, text):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def log(self, text):
        self._write(text)


# ── Fix 2: Running memory ────────────────────────────────────────────────────

class Memory:
    """Keeps a rolling log of commands + outputs. Sent to Claude each loop."""
    def __init__(self):
        self.entries = []

    def add(self, iteration, command, output, thought):
        self.entries.append({
            "i":       iteration,
            "cmd":     command,
            "out":     output[:500] if output else "",
            "thought": thought[:300] if thought else ""
        })

    def to_text(self):
        if not self.entries:
            return ""
        lines = ["--- HISTORY OF PREVIOUS STEPS ---"]
        for e in self.entries:
            lines.append(f"Step {e['i']}: RAN: {e['cmd']}")
            if e["out"]:
                lines.append(f"  Output: {e['out']}")
        result = "\n".join(lines)
        if len(result) > MEMORY_MAX_CHARS:
            result = "[...earlier history trimmed...]\n" + result[-MEMORY_MAX_CHARS:]
        return result


# ── Dead-end detector ────────────────────────────────────────────────────────

def extract_error_signature(output):
    """Pull a normalized error 'signature' from a command output so equivalent
    errors collapse to the same string. Strips numbers and Windows paths.
    Returns '' if no error-like line is found."""
    if not output:
        return ""
    keywords = ("error", "exception", "traceback", "is not recognized",
                "denied", "fatal", "cannot find", "syntaxerror", "failed")
    for line in output.splitlines():
        low = line.lower()
        if any(k in low for k in keywords):
            sig = re.sub(r"\d+", "#", line)
            sig = re.sub(r"[A-Za-z]:\\[^\s\"']+", "PATH", sig)
            sig = re.sub(r"\s+", " ", sig).strip()
            return sig[:200]
    return ""


def detect_dead_end(entries, window=DEAD_END_WINDOW, threshold=DEAD_END_THRESHOLD):
    """If the same error signature appears `threshold` or more times in the
    last `window` memory entries, return (True, signature). Else (False, '')."""
    if len(entries) < threshold:
        return False, ""
    recent = entries[-window:]
    sigs = [s for s in (extract_error_signature(e.get("out", "")) for e in recent) if s]
    if not sigs:
        return False, ""
    top_sig, count = Counter(sigs).most_common(1)[0]
    if count >= threshold:
        return True, top_sig
    return False, ""


# ── PowerShell file-write bypass ─────────────────────────────────────────────

def write_file_directly(path, content):
    """Write `content` to `path` using Python — bypasses PowerShell heredocs
    and string encoding that mangle quotes, backticks, and indentation.
    Returns a short status string suitable for the log + memory."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"[OK] Wrote {len(content)} chars to {path}"
    except Exception as e:
        return f"[ERROR] Could not write {path}: {e}"


# ── v3 (A) Heartbeat — background status thread ──────────────────────────────

class Heartbeat:
    """Prints one status line every HEARTBEAT_INTERVAL_SEC on a daemon thread.
    State is updated via update(); silence() suppresses prints during input()
    prompts so the [y/n] line doesn't get garbled by a heartbeat firing."""

    def __init__(self, interval=HEARTBEAT_INTERVAL_SEC):
        self.interval    = interval
        self.start_time  = time.time()
        self.budget      = None
        self._state      = {"phase": "starting", "iter": 0,
                            "max_iter": 0, "last_cmd": ""}
        self._silenced   = False
        self._lock       = threading.Lock()
        self._stop_event = threading.Event()
        self._thread     = None

    def set_budget(self, budget):
        self.budget = budget

    def update(self, **kwargs):
        with self._lock:
            self._state.update(kwargs)

    def silence(self, value=True):
        with self._lock:
            self._silenced = value

    def start(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _loop(self):
        # Skip the first interval — main thread is still printing the banner
        while not self._stop_event.wait(self.interval):
            with self._lock:
                if self._silenced:
                    continue
                state = dict(self._state)
            elapsed = int(time.time() - self.start_time)
            line = (f"[HEARTBEAT {elapsed // 60}m{elapsed % 60:02d}s]  "
                    f"iter {state['iter']}/{state['max_iter']}  "
                    f"phase: {state['phase']}")
            if self.budget is not None:
                line += f"  |  {self.budget.status_line()}"
            if state["last_cmd"]:
                line += f"\n             last cmd: {state['last_cmd'][:80]}"
            print(line)


# ── v3 (D) Token budget ──────────────────────────────────────────────────────

class TokenBudget:
    """Cumulative Claude API token tracker against an optional cap.
    Soft cap (80 %) sets soft_capped — main loop should stop asking Claude.
    Hard cap (100 %) sets hard_capped — main loop should break immediately."""

    def __init__(self, cap=None):
        self.cap           = cap
        self.input_tokens  = 0
        self.output_tokens = 0
        self.soft_capped   = False
        self.hard_capped   = False

    @property
    def total(self):
        return self.input_tokens + self.output_tokens

    def add(self, input_tokens, output_tokens):
        self.input_tokens  += input_tokens
        self.output_tokens += output_tokens
        if self.cap:
            pct = self.pct()
            if pct >= HARD_CAP_PCT:
                self.hard_capped = True
            if pct >= SOFT_CAP_PCT:
                self.soft_capped = True

    def pct(self):
        return (self.total / self.cap * 100) if self.cap else 0

    def status_line(self):
        if not self.cap:
            return f"{self.total:,} tokens"
        return f"{self.total:,}/{self.cap:,} tokens ({self.pct():.0f}%)"


# ── v3 (C) Auto-snapshot ─────────────────────────────────────────────────────

def make_task_slug(task):
    """FEATURE 1: First 30 chars of task, lowercased, spaces -> underscores,
    other non-alphanumeric chars dropped. Empty string falls back to 'task'."""
    slug = task[:30].lower().replace(" ", "_")
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    return slug or "task"


def auto_snapshot(work_folder, version_num, task_slug):
    """Copy editable project files to backups/vNN_<task_slug>/.
    Returns the snapshot Path on success, or None if no eligible files were
    found (no empty stub dir is left behind)."""
    work = Path(work_folder)
    if not work.is_dir():
        return None

    dest = work / "backups" / f"v{version_num:02d}_{task_slug}"
    # If a same-named dir survives from a prior session (counter resets), replace it.
    if dest.exists():
        try:
            shutil.rmtree(dest)
        except OSError:
            pass
    dest.mkdir(parents=True, exist_ok=True)

    copied = 0
    for path in work.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SNAPSHOT_EXTENSIONS:
            continue
        rel = path.relative_to(work)
        if any(part in SNAPSHOT_EXCLUDE_DIRS for part in rel.parts):
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(path, target)
            copied += 1
        except (OSError, PermissionError):
            continue

    if copied == 0:
        try:
            shutil.rmtree(dest)
        except OSError:
            pass
        return None
    return dest


def prune_snapshots(work_folder, keep=AUTO_SNAPSHOT_KEEP):
    """Delete oldest snapshot dirs beyond `keep` count.
    Matches both new vNN_<slug>/ and legacy auto_<timestamp>/ names.
    Sorted by mtime since vNN names are no longer chronological."""
    backup_root = Path(work_folder) / "backups"
    if not backup_root.is_dir():
        return
    snaps = [p for p in backup_root.iterdir()
             if p.is_dir() and (
                 SESSION_SNAPSHOT_RE.match(p.name)
                 or p.name.startswith(AUTO_SNAPSHOT_PREFIX)
             )]
    snaps.sort(key=lambda p: p.stat().st_mtime)
    if len(snaps) > keep:
        for old in snaps[:-keep]:
            try:
                shutil.rmtree(old)
            except OSError:
                pass


# ── FEATURE 2 — Rollback ──────────────────────────────────────────────────────

def list_snapshots(work_folder):
    """Return snapshot dirs (vNN_*/ and legacy auto_*/), newest first."""
    backup_root = Path(work_folder) / "backups"
    if not backup_root.is_dir():
        return []
    snaps = [p for p in backup_root.iterdir()
             if p.is_dir() and (
                 SESSION_SNAPSHOT_RE.match(p.name)
                 or p.name.startswith(AUTO_SNAPSHOT_PREFIX)
             )]
    snaps.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return snaps


def rollback(work_folder):
    """List snapshots, prompt user for one, copy it back over live files."""
    snaps = list_snapshots(work_folder)
    if not snaps:
        print("\nNo snapshots found in backups/. Nothing to roll back to.")
        return

    print("\nAvailable snapshots (newest first):")
    for i, p in enumerate(snaps, 1):
        ts = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {i:>2}. {p.name}    ({ts})")

    while True:
        choice = input(
            f"\nPick a snapshot to restore [1-{len(snaps)}] (or 'cancel'): "
        ).strip().lower()
        if choice in ("cancel", "c", ""):
            print("Rollback cancelled.")
            return
        try:
            idx = int(choice)
            if 1 <= idx <= len(snaps):
                break
        except ValueError:
            pass
        print(f"Please enter a number 1-{len(snaps)} or 'cancel'.")

    chosen = snaps[idx - 1]
    print(f"\nRestoring from {chosen.name} ...")
    work     = Path(work_folder)
    restored = []
    failed   = []
    for path in chosen.rglob("*"):
        if not path.is_file():
            continue
        rel    = path.relative_to(chosen)
        target = work / rel
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            restored.append(str(rel))
        except (OSError, PermissionError) as e:
            failed.append(f"{rel}: {e}")

    print(f"\n[ROLLBACK] Restored {len(restored)} file(s) from {chosen.name}:")
    for r in restored[:20]:
        print(f"  - {r}")
    if len(restored) > 20:
        print(f"  ... and {len(restored) - 20} more")
    if failed:
        print(f"\n[ROLLBACK] {len(failed)} file(s) failed:")
        for f in failed[:10]:
            print(f"  - {f}")


# ── v3 (B) Multi-file safeguard — "watcher is theatre" WMBW fix ──────────────

def touches_many_files(cmd):
    """Heuristic: does the command appear to touch more than
    TOUCH_FILES_ASK_THRESH files? If so, force an ask even when the
    command otherwise matches the safe allow-list."""
    tokens    = cmd.split()
    path_like = [t for t in tokens if ("\\" in t or "/" in t)]
    if len(path_like) > TOUCH_FILES_ASK_THRESH:
        return True
    # Pad so a verb at the very start of the cmd still matches with surrounding spaces
    low = " " + cmd.lower() + " "
    write_verbs = (" copy ", " move ", " mv ", " cp ", " ren ", " rename ",
                   "out-file", "set-content", "add-content",
                   "copy-item", "move-item")
    has_wildcard = any(ch in cmd for ch in "*?")
    if has_wildcard and any(v in low for v in write_verbs):
        return True
    return False


# ── Load handover document ────────────────────────────────────────────────────

HANDOVER_FILENAME = "STATUS.md"

def load_handover(work_folder):
    """Read the handover doc from the work folder. Return '' and warn if missing."""
    path = Path(work_folder) / HANDOVER_FILENAME
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"[WARN] Handover file not found at {path}. Continuing without project context.")
        return ""
    except Exception as e:
        print(f"[WARN] Could not read {path}: {e}. Continuing without project context.")
        return ""


# ── Fix 1: System prompt with injected path ───────────────────────────────────

def build_system_prompt(work_folder, extra_note, handover_text=""):
    note_block = f"\nExtra context from user: {extra_note}" if extra_note else ""
    context_block = ""
    if handover_text:
        context_block = f"## PROJECT CONTEXT\n\n{handover_text}\n\n---\n\n"
    return context_block + f"""You are an autonomous PC assistant helping Scott build and fix software on Windows.

IMPORTANT FACTS — use these every time, never guess paths:
- Project folder: {work_folder}
- Python executable: C:\\Users\\jscot\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe{note_block}

CRITICAL: Your entire response must be ONLY a single JSON object. Nothing before it. Nothing after it.

You have FOUR possible response types:

1. Run a command:
{{"thought": "what you see and plan", "action": "run", "command": "powershell.exe -Command ...", "done": false}}

2. Ask Scott a question (only when genuinely stuck):
{{"thought": "why I need to ask", "action": "ask_user", "question": "your question here", "done": false}}

3. Write a file directly with Python (PREFERRED for any file/script writing):
{{"thought": "what you're writing and why", "action": "write_file", "path": "C:\\full\\path\\to\\file.ext", "content": "full file contents exactly as they should appear on disk", "done": false}}

4. Task complete:
{{"thought": "summary of what was done", "action": "run", "command": "", "done": true}}

Rules:
- done must be false unless the task is fully complete
- Always use the exact project folder path above — never guess
- Always prefix PowerShell cmdlets with: powershell.exe -Command
- ALWAYS use action "write_file" to create or overwrite any file. NEVER use PowerShell Out-File, Set-Content, Add-Content, echo redirects, or heredocs to write file content — they mangle quotes, backticks, and indentation. write_file writes the raw "content" string straight to disk via Python.
- Never wrap in code fences. Never add text outside the JSON."""


# ── Screenshot ────────────────────────────────────────────────────────────────

def take_screenshot():
    with mss.MSS() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.thumbnail((1280, 720))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=70)
        return base64.b64encode(buf.getvalue()).decode("utf-8")


# ── AAFL convenience wrapper ──────────────────────────────────────────────────

def call_aafl(prompt: str, task_type: str = "fast", max_tokens: int = 512) -> str:
    """Route a prompt through AAFLCore and return the response string."""
    _aafl = AAFLCore(dry_run=False, allow_paid=False)
    result = _aafl.run(task=prompt, task_type=task_type, max_tokens=max_tokens)
    return result.response if result.ok else ""


# ── Ask Claude ────────────────────────────────────────────────────────────────

def ask_claude(screenshot_b64, task, memory, system_prompt, aafl):
    """Returns (raw_text, usage_dict). Routes all AI calls through AAFLCore."""
    history_text = memory.to_text()
    msg = f"Task: {task}"
    if history_text:
        msg += f"\n\n{history_text}"

    result = aafl.run(
        task=msg,
        task_type="vision",
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        image_b64=screenshot_b64,
    )
    usage = {"input": 0, "output": 0}
    return result.response, usage


# ── Parse response ────────────────────────────────────────────────────────────

def parse_response(raw):
    cleaned = re.sub(r"```[a-z]*\n?", "", raw).strip()
    start = cleaned.find("{")
    end   = cleaned.rfind("}") + 1
    if start == -1 or end == 0:
        print(f"No JSON found. Raw:\n{raw}")
        return "", "run", "", False, "", ""
    try:
        data     = json.loads(cleaned[start:end])
        thought  = data.get("thought", "")
        action   = data.get("action", "run")
        command  = data.get("command", "")
        question = data.get("question", "")
        path     = data.get("path", "")
        content  = data.get("content", "")
        done     = data.get("done", False)
        # payload preserves prior behaviour for run/ask_user;
        # write_file uses `content` so a single-field caller still sees it.
        if action == "write_file":
            payload = content
        else:
            payload = command or question
        return thought, action, payload, done, path, content
    except json.JSONDecodeError:
        print(f"Could not parse JSON. Raw:\n{raw}")
        return "", "run", "", False, "", ""


# ── Safety ────────────────────────────────────────────────────────────────────

def is_blacklisted(cmd):
    return any(kw in cmd.lower() for kw in BLACKLIST)

def is_safe(cmd):
    return any(p in cmd.lower() for p in SAFE_PATTERNS)

def ask_yn(prompt, heartbeat=None):
    """v3: pass `heartbeat` to silence its prints while waiting for input."""
    if heartbeat is not None:
        heartbeat.silence(True)
    try:
        while True:
            ans = input(f"\n{prompt} [y/n]: ").strip().lower()
            if ans in ("y", "n"):
                return ans == "y"
    finally:
        if heartbeat is not None:
            heartbeat.silence(False)

def run_command(cmd, work_folder):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=work_folder)
    return (result.stdout + result.stderr).strip()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  SFL Agent v3 — Autonomy Control Panel v1")
    print("="*60)
    print("Optional flags you can add to your task:")
    print("  --folder C:\\your\\path    override project folder")
    print('  --note "extra context"   tell Claude something extra')
    print("  --budget 50k             token cap (k = thousand, m = million)")
    print("="*60 + "\n")

    # FEATURE 2: support `rollback` at the task prompt. Loops until we get a real task.
    while True:
        raw_task = input(
            "What do you want the agent to do?\n"
            "(or type 'rollback' to restore a snapshot)\n> "
        ).strip()
        first_word = raw_task.split()[0].lower() if raw_task else ""
        if first_word == "rollback":
            # Honour --folder if user passed it alongside rollback.
            _, rb_folder, _, _ = parse_task(raw_task)
            rollback(rb_folder)
            continue
        if not raw_task:
            continue
        break

    task, work_folder, extra_note, budget_cap = parse_task(raw_task)

    print(f"\nTask:           {task}")
    print(f"Project folder: {work_folder}")
    if extra_note:
        print(f"Note:           {extra_note}")
    if budget_cap:
        print(f"Token budget:   {budget_cap:,}  "
              f"(soft cap {SOFT_CAP_PCT}%, hard cap {HARD_CAP_PCT}%)")
    else:
        print("Token budget:   unlimited")
    print(f"Heartbeat:      every {HEARTBEAT_INTERVAL_SEC}s. Ctrl+C to stop.\n")

    handover_text = load_handover(work_folder)
    if handover_text:
        print(f"[OK] Loaded {HANDOVER_FILENAME} ({len(handover_text)} chars) into system prompt.")

    aafl          = AAFLCore()
    system_prompt = build_system_prompt(work_folder, extra_note, handover_text)
    logger        = Logger(task)
    memory        = Memory()
    budget        = TokenBudget(cap=budget_cap)
    heartbeat     = Heartbeat()
    heartbeat.set_budget(budget)

    logger.log(f"Task: {task}\nFolder: {work_folder}\nNote: {extra_note}")
    logger.log(f"Handover loaded: {'yes' if handover_text else 'no'}")
    logger.log(f"Token budget: {budget_cap if budget_cap else 'unlimited'}")

    iteration         = 0
    max_iter          = DEFAULT_MAX_ITER
    snapshot_counter  = 0                       # FEATURE 1: resets each session
    task_slug         = make_task_slug(task)    # FEATURE 1: vNN_<task_slug>/
    dead_end_cooldown = 0                       # skip detector for N iters after intervention
    heartbeat.update(max_iter=max_iter)
    heartbeat.start()

    try:
        while iteration < max_iter:
            # v3 (D) Soft cap check BEFORE next Claude call — "stop new ones"
            if budget.hard_capped or budget.soft_capped:
                tag = "HARD" if budget.hard_capped else "SOFT"
                print(f"\n[BUDGET {tag} CAP] {budget.status_line()} — stopping.")
                logger.log(f"BUDGET {tag} CAP HIT: {budget.status_line()}")
                break

            iteration += 1
            print(f"--- Iteration {iteration}/{max_iter} ---")
            logger.log(f"\n--- Iteration {iteration} ---")
            heartbeat.update(iter=iteration, phase="starting", last_cmd="")

            # Dead-end detector: same error in DEAD_END_THRESHOLD of last
            # DEAD_END_WINDOW outputs → pause and ask Scott what to do.
            if dead_end_cooldown > 0:
                dead_end_cooldown -= 1
            else:
                hit, sig = detect_dead_end(memory.entries)
                if hit:
                    print("\n" + "=" * 60)
                    print(f"[DEAD-END] Same error in {DEAD_END_THRESHOLD}+ of last "
                          f"{DEAD_END_WINDOW} outputs:")
                    print(f"  {sig}")
                    print("=" * 60)
                    logger.log(f"DEAD-END DETECTED: {sig}")
                    heartbeat.update(phase="waiting for dead-end guidance")
                    heartbeat.silence(True)
                    try:
                        guidance = input(
                            "What should Claude do? "
                            "(type instructions, or 'stop' to end): "
                        ).strip()
                    finally:
                        heartbeat.silence(False)
                    if not guidance or guidance.lower() in ("stop", "quit", "exit", "n", "no"):
                        print("Stopping at dead-end.")
                        logger.log("STOPPED at dead-end by user.")
                        break
                    logger.log(f"USER GUIDANCE: {guidance}")
                    memory.add(iteration, "[DEAD-END INTERVENTION]",
                               f"Scott says: {guidance}",
                               "user broke the loop with new guidance")
                    dead_end_cooldown = DEAD_END_WINDOW

            heartbeat.update(phase="screenshot")
            print("Taking screenshot...")
            img_data = take_screenshot()

            heartbeat.update(phase="asking Claude")
            print("Asking Claude...")
            raw, usage = ask_claude(img_data, task, memory, system_prompt, aafl)
            budget.add(usage["input"], usage["output"])
            logger.log(f"TOKENS: +{usage['input']}in/+{usage['output']}out  "
                       f"=> {budget.status_line()}")

            thought, action, payload, done, file_path, file_content = parse_response(raw)

            print(f"THOUGHT: {thought}")
            logger.log(f"THOUGHT: {thought}")

            # Fix 4: Agent asks a question
            if action == "ask_user":
                print(f"\nClaude has a question: {payload}")
                logger.log(f"QUESTION: {payload}")
                heartbeat.update(phase="waiting for answer")
                heartbeat.silence(True)
                try:
                    answer = input("Your answer: ").strip()
                finally:
                    heartbeat.silence(False)
                logger.log(f"ANSWER: {answer}")
                memory.add(iteration, f"[asked: {payload}]", f"[answer: {answer}]", thought)
                continue

            # PowerShell file-write bypass: Claude requested a direct Python write.
            if action == "write_file":
                print(f"\nWRITE FILE: {file_path}  ({len(file_content)} chars)")
                logger.log(f"WRITE FILE: {file_path}  ({len(file_content)} chars)")
                heartbeat.update(last_cmd=f"write_file {file_path}")
                if not file_path:
                    print("No path provided; skipping.")
                    logger.log("WRITE FILE: skipped — no path.")
                    memory.add(iteration, "[write_file: no path]", "Skipped.", thought)
                    continue
                if ask_yn(f"Write {len(file_content)} chars to {file_path}?", heartbeat):
                    heartbeat.update(phase="snapshotting")
                    print("[SNAPSHOT] Saving project files...")
                    snapshot_counter += 1
                    snap = auto_snapshot(work_folder, snapshot_counter, task_slug)
                    if snap:
                        print(f"[SNAPSHOT] Saved to: {snap}")
                        logger.log(f"SNAPSHOT: {snap}")
                        prune_snapshots(work_folder)
                    else:
                        print("[SNAPSHOT] (no editable files matched — skipped)")
                        snapshot_counter -= 1
                    heartbeat.update(phase="writing file")
                    result = write_file_directly(file_path, file_content)
                    print(result)
                    logger.log(f"OUTPUT: {result}")
                    memory.add(iteration, f"[write_file {file_path}]", result, thought)
                else:
                    print("Skipped.")
                    logger.log("SKIPPED.")
                    memory.add(iteration, f"[write_file {file_path}]", "User skipped.", thought)
                continue

            command = payload
            print(f"COMMAND: {command}")
            logger.log(f"COMMAND: {command}")
            heartbeat.update(last_cmd=command)

            if done:
                print("\nClaude says task is done.")
                logger.log("STATUS: Done.")
                break

            if not command:
                print("No command. Looping...")
                memory.add(iteration, "", "", thought)
                continue

            if is_blacklisted(command):
                print(f"BLOCKED — blacklisted: {command}")
                logger.log(f"BLOCKED: {command}")
                memory.add(iteration, command, "Blocked by safety filter.", thought)
                continue

            # v3 (B) safe allow-list + multi-file safeguard
            multi_file = touches_many_files(command)
            auto_run   = is_safe(command) and not multi_file

            if auto_run:
                print("AUTO-RUNNING (safe)...")
                heartbeat.update(phase="running (safe)")
                output = run_command(command, work_folder)
                print(f"Output: {output}")
                logger.log(f"OUTPUT: {output}")
                memory.add(iteration, command, output, thought)
            else:
                reason = " (touches multiple files)" if multi_file else ""
                if ask_yn(f"Run{reason}: {command}", heartbeat):
                    # v3 (C) auto-snapshot before approved change
                    # FEATURE 1: named vNN_<slug>/ snapshots, counter per session
                    heartbeat.update(phase="snapshotting")
                    print("[SNAPSHOT] Saving project files...")
                    snapshot_counter += 1
                    snap = auto_snapshot(work_folder, snapshot_counter, task_slug)
                    if snap:
                        print(f"[SNAPSHOT] Saved to: {snap}")
                        logger.log(f"SNAPSHOT: {snap}")
                        prune_snapshots(work_folder)
                    else:
                        print("[SNAPSHOT] (no editable files matched — skipped)")
                        snapshot_counter -= 1   # FEATURE 1: keep numbering contiguous
                    heartbeat.update(phase="running")
                    print("Running...")
                    output = run_command(command, work_folder)
                    print(f"Output: {output}")
                    logger.log(f"OUTPUT: {output}")
                    memory.add(iteration, command, output, thought)
                else:
                    print("Skipped.")
                    logger.log("SKIPPED.")
                    memory.add(iteration, command, "User skipped.", thought)

            # v3 (D) Hard cap check at end-of-iteration natural breakpoint
            if budget.hard_capped:
                print(f"\n[BUDGET HARD CAP] {budget.status_line()} — stopping immediately.")
                logger.log("BUDGET HARD CAP HIT")
                break

            # Fix 3: Ask to continue at iteration limit
            if iteration == max_iter:
                print(f"\nReached {max_iter} iterations.")
                if ask_yn("Keep going for another 50?", heartbeat):
                    max_iter += 50
                    heartbeat.update(max_iter=max_iter)
                    logger.log(f"User extended limit to {max_iter}.")
                else:
                    logger.log("User stopped at limit.")
                    break
    finally:
        heartbeat.stop()

    print("\nLoop ended.")
    if budget_cap:
        print(f"[BUDGET] Final usage: {budget.status_line()}")
    logger.log(f"\nLoop ended. Final budget: {budget.status_line()}")
    print(f"Full log saved to: {logger.path}")
