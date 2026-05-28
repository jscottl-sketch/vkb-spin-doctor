"""
aafl_watchdog.py -- WCCS Auto-Capture + Trigger Watchdog

Captures the current Claude session (CLAC JSONL -> Chrome MCC -> Clipboard),
validates it, runs aafl_wccs.py, and shows a Windows toast on success/fail.

Usage:
  python aafl_watchdog.py          # start daemon, type /wccs to trigger now
  python aafl_watchdog.py --once   # one capture+WCCS cycle then exit
"""

import re
import sys
import json
import time
import ctypes
import datetime
import threading
import subprocess
from pathlib import Path
from urllib import request as urlrequest

from aafl_core import AAFLCore

# ── Paths ──────────────────────────────────────────────────────────────────────
HERE        = Path(__file__).parent
from config import CLAUDE_PROJ  # noqa: E402
CHAT_FILE   = HERE / "chat_latest.txt"
WCCS_LOG    = HERE / "wccs_log.md"
MCC_URL     = "http://localhost:8080/captures"
PYTHON      = sys.executable

CYCLE_MINUTES = 10
ONCE          = "--once" in sys.argv

# ── Windows notification (ctypes, stdlib) ─────────────────────────────────────
try:
    import winsound
    _WINSOUND_OK = True
except ImportError:
    _WINSOUND_OK = False


def toast(title: str, msg: str) -> None:
    """Non-blocking Windows MessageBox. Falls back to print if ctypes unavailable."""
    def _show():
        try:
            ctypes.windll.user32.MessageBoxW(None, msg, title, 0x40)
        except Exception:
            pass
    threading.Thread(target=_show, daemon=True).start()
    print(f"[TOAST] {title}: {msg}")


def _beep_success() -> None:
    if _WINSOUND_OK:
        try:
            winsound.Beep(880, 180)
            winsound.Beep(1100, 280)
        except Exception:
            pass


# ── Clipboard reader (ctypes, Windows stdlib) ─────────────────────────────────
def clipboard_read() -> str:
    """Read current clipboard text. Returns '' on any failure."""
    try:
        u = ctypes.windll.user32
        k = ctypes.windll.kernel32
        if not u.OpenClipboard(None):
            return ""
        CF_UNICODETEXT = 13
        h = u.GetClipboardData(CF_UNICODETEXT)
        if not h:
            u.CloseClipboard()
            return ""
        ptr = k.GlobalLock(h)
        text = ctypes.wstring_at(ptr) if ptr else ""
        k.GlobalUnlock(h)
        u.CloseClipboard()
        return text
    except Exception:
        return ""


# ── JSONL parsing ─────────────────────────────────────────────────────────────
def _content_to_str(val) -> str:
    """Flatten Claude Code content (str or list-of-blocks) to plain text."""
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        parts = []
        for block in val:
            if isinstance(block, dict):
                parts.append(block.get("text") or block.get("content") or "")
            elif isinstance(block, str):
                parts.append(block)
        return " ".join(p for p in parts if p)
    return str(val) if val else ""


def parse_jsonl(path: Path) -> str:
    """
    Extract human+assistant turns from a Claude Code JSONL session file.
    Returns formatted chat text or '' if nothing usable found.
    """
    lines_out = []
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            role    = (obj.get("role") or obj.get("type") or "").lower()
            content = _content_to_str(
                obj.get("content") or obj.get("message") or ""
            ).strip()
            if not content:
                continue
            if role in ("human", "user"):
                lines_out.append(f"Human: {content[:1200]}")
            elif role == "assistant":
                lines_out.append(f"Assistant: {content[:1200]}")
    except Exception as exc:
        print(f"[WATCHDOG]   JSONL parse error: {exc}")
    return "\n\n".join(lines_out)


# ── Chat-likeness heuristic ───────────────────────────────────────────────────
_CHAT_MARKERS = (
    "human:", "assistant:", "user:", "claude:", "you asked",
    "> user", "> claude", "question:", "chatgpt", "gpt-4",
)


def _is_chat_like(text: str) -> bool:
    lower = text.lower()
    return len(text) >= 200 and any(m in lower for m in _CHAT_MARKERS)


# ── Confidence check via AAFLCore ─────────────────────────────────────────────
def confidence_check(text: str) -> bool:
    """
    Send the first 500 chars to AAFLCore (task_type=batch -> Mistral route).
    Returns True if LLM says YES (or if the LLM call itself fails).
    """
    print("[WATCHDOG]   Confidence check (asking LLM) ...")
    sample = text[:500]
    aafl   = AAFLCore(dry_run=False, allow_paid=False)
    result = aafl.run(
        f"Is this a real AI chat session? Reply YES or NO only.\n\n"
        f"--- TEXT SAMPLE ---\n{sample}",
        task_type="batch",
        max_tokens=5,
    )
    if not result.ok:
        print("[WATCHDOG]   LLM failed -- treating as YES (pass-through)")
        return True
    answer = result.response.strip().upper()[:3]
    print(f"[WATCHDOG]   LLM: {answer!r}  ({result.provider_id}, {result.elapsed_sec}s)")
    return answer.startswith("YES")


# ── Capture Method 1: CLAC JSONL ──────────────────────────────────────────────
def capture_clac() -> str | None:
    """Find the most-recently-modified JSONL in .claude/projects/ and parse it."""
    print("[WATCHDOG] [1/3] CLAC CAPTURE: scanning .claude/projects/ ...")
    if not CLAUDE_PROJ.exists():
        print("[WATCHDOG]   .claude/projects not found -- skip")
        return None

    jsonl_files = list(CLAUDE_PROJ.rglob("*.jsonl"))
    if not jsonl_files:
        print("[WATCHDOG]   No JSONL files found -- skip")
        return None

    latest  = max(jsonl_files, key=lambda f: f.stat().st_mtime)
    age_min = (time.time() - latest.stat().st_mtime) / 60
    print(f"[WATCHDOG]   Latest: {latest.name}  ({age_min:.1f} min old)")

    if age_min > 60:
        print(f"[WATCHDOG]   SKIP: file is {age_min:.0f} min old (>60 min -- stale)")
        return None

    text = parse_jsonl(latest)
    if len(text) < 200:
        print(f"[WATCHDOG]   SKIP: parsed text too short ({len(text)} chars)")
        return None

    print(f"[WATCHDOG]   OK: {len(text)} chars extracted from JSONL")
    return text


# ── Capture Method 2: Chrome MCC server ───────────────────────────────────────
def capture_chrome_mcc() -> str | None:
    """
    GET localhost:8080/captures from the MCC server.
    The MCC WCCS tab lets you save chat snippets -- this reads the latest.
    """
    print("[WATCHDOG] [2/3] CHAT CAPTURE: trying MCC server captures endpoint ...")
    try:
        resp = urlrequest.urlopen(MCC_URL, timeout=5)
        raw  = resp.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
            if isinstance(data, list) and data:
                entry = data[-1]
                text  = entry.get("text") or entry.get("content") or str(entry)
            elif isinstance(data, dict):
                text = data.get("text") or data.get("content") or raw
            else:
                text = raw
        except json.JSONDecodeError:
            text = raw
        text = text.strip()
        if len(text) < 200:
            print(f"[WATCHDOG]   SKIP: MCC returned only {len(text)} chars")
            return None
        print(f"[WATCHDOG]   OK: {len(text)} chars from MCC server")
        return text
    except Exception as exc:
        print(f"[WATCHDOG]   SKIP: MCC not reachable ({type(exc).__name__})")
        return None


# ── Capture Method 3: Clipboard watcher ───────────────────────────────────────
def capture_clipboard(watch_secs: int = 30) -> str | None:
    """Poll clipboard for watch_secs seconds. Returns text if 200+ chat-like chars found."""
    print(f"[WATCHDOG] [3/3] CLIPBOARD FALLBACK: watching clipboard for {watch_secs}s ...")
    deadline = time.time() + watch_secs
    seen: set[str] = set()

    while time.time() < deadline:
        text = clipboard_read()
        if text:
            key = text[:64]
            if key not in seen and len(text) >= 200:
                seen.add(key)
                if _is_chat_like(text):
                    print(f"\n[WATCHDOG]   OK: clipboard has {len(text)} chars")
                    return text
        remaining = int(deadline - time.time())
        print(f"[WATCHDOG]   Watching clipboard ... {remaining}s left  ", end="\r", flush=True)
        time.sleep(2)

    print()
    print("[WATCHDOG]   SKIP: no chat-like text found in clipboard")
    return None


# ── WCCS runner ───────────────────────────────────────────────────────────────
def _detect_version(output: str) -> str:
    m = re.search(r"VKB_SpinDoctor_Handover_v(\d+)\.md", output)
    return f"v{m.group(1)}" if m else "vNN"


def run_wccs() -> tuple[bool, str, str]:
    """
    Run aafl_wccs.py as a subprocess.
    Returns (success, version_string, stdout+stderr).
    """
    print("[WATCHDOG] Running aafl_wccs.py ...")
    wccs_script = HERE / "aafl_wccs.py"
    if not wccs_script.exists():
        return False, "vNN", "aafl_wccs.py not found in project folder"
    try:
        res = subprocess.run(
            [PYTHON, str(wccs_script)],
            cwd=str(HERE),
            capture_output=True,
            text=True,
            timeout=300,
            encoding="utf-8",
            errors="replace",
        )
        output  = res.stdout + res.stderr
        success = res.returncode == 0
        version = _detect_version(output)
        return success, version, output
    except subprocess.TimeoutExpired:
        return False, "vNN", "aafl_wccs.py timed out after 300s"
    except Exception as exc:
        return False, "vNN", str(exc)


# ── Watchdog log ──────────────────────────────────────────────────────────────
def log_cycle(method: str, success: bool) -> None:
    """Append one watchdog row to wccs_log.md."""
    ts     = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    status = "SUCCESS" if success else "FAIL"
    line   = f"| WATCHDOG | {ts} | - | Capture: {method} | {status} |\n"
    try:
        with open(WCCS_LOG, "a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception as exc:
        print(f"[WATCHDOG] Log write failed: {exc}")


# ── Per-iteration loop danger check ──────────────────────────────────────────
_WATCHDOG_LOG = HERE / "aafl_output" / "watchdog_loop_log.txt"


def check_loop_danger(
    iterations: int,
    cost_gbp: float,
    consecutive_provider_fails: int,
) -> tuple[bool, str]:
    """
    Called after each loop iteration to detect dangerous conditions.
    Returns (is_danger, reason). Logs every check to aafl_output/watchdog_loop_log.txt.

    Detects:
    - Runaway provider failures (all providers exhausted repeatedly)
    - Token burn rate too high (cost/iteration > £0.02)
    - Iteration ceiling hit without goal completion
    """
    danger = False
    reason = "ok"

    if consecutive_provider_fails >= 5:
        danger = True
        reason = (
            f"WATCHDOG ABORT: {consecutive_provider_fails} consecutive provider failures "
            "— runaway loop with no output"
        )
    elif cost_gbp > 0 and iterations > 0 and (cost_gbp / iterations) > 0.02:
        burn = cost_gbp / iterations
        danger = True
        reason = (
            f"WATCHDOG ABORT: token burn rate £{burn:.4f}/iter exceeds safety threshold "
            f"(£0.0200/iter) after {iterations} iterations"
        )
    elif iterations >= 45:
        danger = True
        reason = (
            f"WATCHDOG ABORT: iteration ceiling reached ({iterations}/45) "
            "with no goal completion"
        )

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        (HERE / "aafl_output").mkdir(exist_ok=True)
        with open(_WATCHDOG_LOG, "a", encoding="utf-8") as f:
            f.write(
                f"[{ts}] iter={iterations} cost=£{cost_gbp:.4f} "
                f"prov_fails={consecutive_provider_fails} "
                f"danger={danger} reason={reason}\n"
            )
    except Exception:
        pass

    if danger:
        print(f"[WATCHDOG] {reason}")

    return danger, reason


# ── Full cycle ────────────────────────────────────────────────────────────────
_cycle_lock = threading.Lock()


def run_cycle() -> bool:
    """
    Run one full capture -> confidence check -> WCCS cycle.
    Thread-safe: skips if a cycle is already in progress.
    Returns True on success.
    """
    if not _cycle_lock.acquire(blocking=False):
        print("[WATCHDOG] A cycle is already running -- skipping")
        return False

    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*56}")
        print(f"[WATCHDOG] Cycle start: {ts}")
        print(f"{'='*56}")

        captured: str | None = None
        method               = "none"

        # -- Methods 1 and 2 (no waiting) ------------------------------------
        for m_name, m_fn in [("CLAC", capture_clac), ("CHAT_MCC", capture_chrome_mcc)]:
            text = m_fn()
            if text is None:
                continue
            if confidence_check(text):
                captured = text
                method   = m_name
                break
            print(f"[WATCHDOG]   Confidence FAIL for {m_name} -- trying next method")

        # -- Method 3: clipboard (30-second watch) ----------------------------
        if captured is None:
            text = capture_clipboard(30)
            if text is not None:
                if confidence_check(text):
                    captured = text
                    method   = "CLIPBOARD"
                else:
                    print("[WATCHDOG]   Confidence FAIL for CLIPBOARD")

        # -- All methods failed -----------------------------------------------
        if captured is None:
            print("[WATCHDOG] All 3 capture methods failed.")
            toast(
                "AAFL Watchdog",
                "[!] Auto-capture failed -- paste chat into chat_latest.txt manually.",
            )
            log_cycle("none", False)
            return False

        # -- Write chat_latest.txt -------------------------------------------
        print(f"[WATCHDOG] Writing chat_latest.txt ({len(captured)} chars) ...")
        CHAT_FILE.write_text(captured, encoding="utf-8")
        print(f"[WATCHDOG] chat_latest.txt written.")

        # -- Run aafl_wccs.py ------------------------------------------------
        success, version, wccs_out = run_wccs()
        print()
        for line in wccs_out.splitlines()[-25:]:
            print(f"  {line}")
        print()

        log_cycle(method, success)

        if success:
            print(f"[WATCHDOG] WCCS OK -- {version} written via {method}")
            _beep_success()
            toast("AAFL Watchdog", f"WCCS saved -- {version} written")
        else:
            print("[WATCHDOG] WCCS FAILED -- check terminal output")
            toast("AAFL Watchdog", "WCCS run failed -- check terminal output")

        return success

    finally:
        _cycle_lock.release()


# ── Background timer (daemon thread) ─────────────────────────────────────────
def _timer_loop() -> None:
    """Sleep CYCLE_MINUTES then run a cycle, forever."""
    while True:
        time.sleep(CYCLE_MINUTES * 60)
        run_cycle()


# ── stdin /wccs listener (daemon thread) ─────────────────────────────────────
_trigger = threading.Event()


def _stdin_listener() -> None:
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "/wccs":
            print("[WATCHDOG] /wccs received -- triggering capture now ...")
            _trigger.set()


# ── Entry point ────────────────────────────────────────────────────────────────
def main() -> None:
    print()
    print("[WATCHDOG] aafl_watchdog.py -- WCCS Auto-Capture Daemon")
    print(f"[WATCHDOG] Project: {HERE}")
    if ONCE:
        print("[WATCHDOG] --once flag: run one cycle then exit")
    else:
        print(f"[WATCHDOG] Auto-cycle every {CYCLE_MINUTES} min | type /wccs to trigger now")
    print()

    if ONCE:
        run_cycle()
        return

    # Background timer
    threading.Thread(target=_timer_loop, daemon=True, name="WatchdogTimer").start()
    print(f"[WATCHDOG] Background timer started -- next auto-cycle in {CYCLE_MINUTES} min")

    # stdin listener for /wccs
    threading.Thread(target=_stdin_listener, daemon=True, name="StdinListener").start()
    print("[WATCHDOG] Type /wccs to trigger an immediate cycle")
    print("[WATCHDOG] Press Ctrl+C to stop")
    print()

    try:
        while True:
            if _trigger.wait(timeout=0.5):
                _trigger.clear()
                run_cycle()
    except KeyboardInterrupt:
        print("\n[WATCHDOG] Stopped.")


if __name__ == "__main__":
    main()
