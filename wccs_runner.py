"""
wccs_runner.py — WCCS (Write Claude Code Save) Legacy Runner
Writes session log + wccs_log.md, runs mcu_optimizer + dashboard_builder.
NEVER creates VKB_SpinDoctor_Handover_vXX.md — STATUS.md is the handover now.
Use aafl_wccs.py for full WCCS saves (STATUS.md rewrite + HISTORY.md + ACCA.md).

Usage:
    python wccs_runner.py
"""

import datetime
import re
import subprocess
import sys
from pathlib import Path

from aafl_core import AAFLCore

HERE         = Path(__file__).parent
SESSION_LOGS = HERE / "session_logs"
PYTHON       = sys.executable

AGENT_SYSTEM = (
    "You are an autonomous AI agent. "
    "Complete every task fully in a single response. "
    "Never ask follow-up questions. Never ask for clarification. "
    "Produce your complete answer and stop."
)


# ── Row counter ────────────────────────────────────────────────────────────────

def next_wccs_row_number():
    log_path = HERE / "wccs_log.md"
    if not log_path.exists():
        return 1
    content = log_path.read_text(encoding="utf-8", errors="replace")
    rows = re.findall(r"^\|\s*(\d+)\s*\|", content, re.MULTILINE)
    return max((int(r) for r in rows), default=0) + 1


# ── Subprocess runner ─────────────────────────────────────────────────────────

def run_script(script_name):
    script_path = HERE / script_name
    if not script_path.exists():
        return False, f"{script_name} not found"
    try:
        result = subprocess.run(
            [PYTHON, str(script_path)],
            capture_output=True, text=True, timeout=120,
            cwd=str(HERE),
        )
        ok = result.returncode == 0
        out = (result.stdout + result.stderr).strip()
        return ok, out[:500]
    except subprocess.TimeoutExpired:
        return False, f"{script_name} timed out after 120s"
    except Exception as e:
        return False, str(e)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    today = datetime.date.today().isoformat()
    results = {}
    print("[WCCS] Starting WCCS automation (legacy runner — STATUS/HISTORY/ACCA mode)...")

    # 1. Read chat_latest.txt
    chat_path = HERE / "chat_latest.txt"
    if not chat_path.exists():
        print("[WCCS] No chat_latest.txt — skipping session log. Running mcu/dashboard only.")
        chat_summary = ""
    else:
        chat_summary = chat_path.read_text(encoding="utf-8", errors="replace").strip()
    print(f"[WCCS] Chat summary: {len(chat_summary)} chars")

    # NOTE: Handover file creation is REMOVED (Phase 5 — OCB-N).
    # STATUS.md / HISTORY.md / ACCA.md are the source of truth.
    # Use aafl_wccs.py for full WCCS saves. This runner is legacy support only.

    # 2. Determine session label
    existing_cc = list(SESSION_LOGS.glob(f"{today}-cc*.md")) if SESSION_LOGS.exists() else []
    max_cc = 0
    for f in existing_cc:
        m = re.search(r"-cc(\d+)\.md$", f.name)
        if m:
            max_cc = max(max_cc, int(m.group(1)))
    session_n = max_cc + 1
    session_label = f"Claude Code session {session_n}"
    session_log_path = SESSION_LOGS / f"{today}-cc{session_n}.md"

    chat_entry = (
        f"### {today} ({session_label})\n"
        f"**Key decisions:** WCCS legacy runner (no AI call).\n"
        f"**New ACCA codes:** None\n"
        f"**Ideas discussed:** None\n"
        f"**Next priorities:** See STATUS.md NEXT PRIORITIES.\n"
    )

    # 3. Write session log
    SESSION_LOGS.mkdir(exist_ok=True)
    try:
        content = (
            f"# Session Log -- {session_log_path.stem}\n\n"
            f"**Mode:** Legacy wccs_runner (no handover created)\n\n"
            f"## Chat Summary\n\n{chat_summary[:2000]}\n\n"
            f"## Session Entry\n\n{chat_entry}\n"
        )
        session_log_path.write_text(content, encoding="utf-8")
        print(f"[WCCS] Session log: {session_log_path.name}")
        results["session_log"] = "PASS"
    except Exception as e:
        print(f"[WCCS] WARN: Session log failed: {e}")
        results["session_log"] = "FAIL"

    # 4. Append wccs_log.md
    try:
        row_num = next_wccs_row_number()
        log_path = HERE / "wccs_log.md"
        focus = (chat_summary[:80].replace("\n", " ").replace("|", "/")).strip() or "legacy runner"
        row = f"| {row_num} | {today} | legacy | {focus} | None |\n"
        if not log_path.exists():
            header = (
                "# WCCS Run Log\n\n"
                "**WCCS = Write Claude Code Save.**\n\n"
                "---\n\n"
                "| # | Date | Handover | Session Focus | ALP Rules Added |\n"
                "|---|---|---|---|---|\n"
            )
            log_path.write_text(header + row, encoding="utf-8")
        else:
            with log_path.open("a", encoding="utf-8") as f:
                f.write(row)
        print(f"[WCCS] wccs_log.md: row {row_num} appended")
        results["wccs_log"] = "PASS"
    except Exception as e:
        print(f"[WCCS] WARN: wccs_log failed: {e}")
        results["wccs_log"] = "FAIL"

    # 5. Run mcu_optimizer.py
    print("[WCCS] Running mcu_optimizer.py...")
    ok, out = run_script("mcu_optimizer.py")
    results["mcu_optimizer"] = "PASS" if ok else "FAIL"
    if not ok:
        print(f"[WCCS] WARN: mcu_optimizer failed:\n{out}")
    else:
        print("[WCCS] mcu_optimizer: OK")

    # 6. Run dashboard_builder.py
    print("[WCCS] Running dashboard_builder.py...")
    ok, out = run_script("dashboard_builder.py")
    results["dashboard_builder"] = "PASS" if ok else "FAIL"
    if not ok:
        print(f"[WCCS] WARN: dashboard_builder failed:\n{out}")
    else:
        print("[WCCS] dashboard_builder: OK")

    # 7. Summary
    fails = [k for k, v in results.items() if v.startswith("FAIL")]
    print("\n" + "=" * 50)
    print("[WCCS] SUMMARY:")
    for k, v in results.items():
        icon = "OK" if v == "PASS" else "!!"
        print(f"  [{icon}] {k}: {v}")
    if fails:
        print(f"\n[WCCS] RESULT: WARN ({len(fails)} issue(s)) — non-fatal")
    else:
        print(f"\n[WCCS] RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
