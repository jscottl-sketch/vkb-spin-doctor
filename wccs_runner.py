"""
wccs_runner.py — WCCS (Write Claude Code Save) Automation
Reads chat_latest.txt + current handover, sends to AAFLCore (free LLM) to
generate updated handover sections, writes vNN+1 handover, session log,
wccs_log, runs mcu_optimizer + dashboard_builder, updates sfl_agent.py, cleans up.

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


# ── File finders ──────────────────────────────────────────────────────────────

def find_latest_handover():
    files = list(HERE.glob("VKB_SpinDoctor_Handover_v*.md"))
    if not files:
        return None
    def _ver(p):
        m = re.search(r"_v(\d+)\.md$", p.name)
        return int(m.group(1)) if m else 0
    return max(files, key=_ver)


def handover_version(path):
    m = re.search(r"_v(\d+)\.md$", path.name)
    return int(m.group(1)) if m else 0


def next_wccs_row_number():
    log_path = HERE / "wccs_log.md"
    if not log_path.exists():
        return 1
    content = log_path.read_text(encoding="utf-8", errors="replace")
    rows = re.findall(r"^\|\s*(\d+)\s*\|", content, re.MULTILINE)
    return max((int(r) for r in rows), default=0) + 1


# ── LLM prompt ────────────────────────────────────────────────────────────────

def _handover_excerpt(text):
    parts = []
    m = re.search(r"\*\*Status:\*\*(.+)", text)
    if m:
        parts.append(f"**Status:**{m.group(1).strip()}")
    m2 = re.search(r"## NEXT PRIORITIES\n(.*?)(?=\n---|\n##)", text, re.DOTALL)
    if m2:
        parts.append(f"## NEXT PRIORITIES\n{m2.group(1).strip()}")
    entries = list(re.finditer(r"### 20\d\d-\d\d-\d\d", text))
    if entries:
        last_start = entries[-1].start()
        parts.append("## CHAT LOG (last entry)\n" + text[last_start:last_start + 600])
    return "\n\n".join(parts)


def build_llm_prompt(chat_summary, handover_text, today, session_label):
    return f"""You are updating a project handover document after a Claude Code session.

Given the CHAT SUMMARY and CURRENT HANDOVER, generate two sections.

SECTION 1 - New CHAT LOG entry to APPEND at the bottom of ## CHAT LOG.
Use EXACTLY this format:

===CHAT_LOG_ENTRY===
### {today} ({session_label})
**Key decisions:** <one or two sentences>
**New ACCA codes:** <list or None>
**Ideas discussed:** <brief bullet or sentence>
**Bugs fixed:** <list or omit if none>
**Next priorities:** <numbered list, max 5>
===END_CHAT_LOG===

SECTION 2 - Updated NEXT PRIORITIES to REPLACE the current ## NEXT PRIORITIES section.
Use EXACTLY this format:

===NEXT_PRIORITIES===
1. <most urgent>
2. <second>
3. <third>
4. <fourth (optional)>
5. <fifth (optional)>
===END_PRIORITIES===

Rules:
- Use plain ASCII only. No unicode arrows or dashes.
- Be concise. No padding or filler.
- Next priorities must reflect what actually needs doing next based on the chat summary.

--- CHAT SUMMARY ---
{chat_summary[:3000]}

--- CURRENT HANDOVER EXCERPT ---
{_handover_excerpt(handover_text)}

--- OUTPUT ---
"""


# ── LLM response parsing ──────────────────────────────────────────────────────

def parse_llm_response(response):
    chat_m = re.search(r"===CHAT_LOG_ENTRY===\s*(.*?)\s*===END_CHAT_LOG===", response, re.DOTALL)
    prio_m = re.search(r"===NEXT_PRIORITIES===\s*(.*?)\s*===END_PRIORITIES===", response, re.DOTALL)
    chat_entry = chat_m.group(1).strip() if chat_m else None
    priorities = prio_m.group(1).strip() if prio_m else None
    return chat_entry, priorities


# ── Handover builder ──────────────────────────────────────────────────────────

def build_new_handover(old_text, old_ver, new_ver, chat_entry, priorities, today):
    text = old_text

    # Update version in title
    text = re.sub(
        r"(# VKB Spin Doctor[^\n]*?Handover v)\d+",
        lambda m: m.group(1) + str(new_ver),
        text, count=1,
    )

    # Update Last updated
    text = re.sub(
        r"\*\*Last updated:\*\*[^\n]+",
        f"**Last updated:** {today} (WCCS automation)",
        text, count=1,
    )

    # Update Consolidates
    text = re.sub(
        r"\*\*Consolidates:\*\*[^\n]+",
        f"**Consolidates:** v{old_ver}",
        text, count=1,
    )

    # Update all handover filename references
    text = re.sub(
        r"VKB_SpinDoctor_Handover_v\d+\.md",
        f"VKB_SpinDoctor_Handover_v{new_ver}.md",
        text,
    )

    # Replace NEXT PRIORITIES if LLM provided one
    if priorities:
        text = re.sub(
            r"(## NEXT PRIORITIES\n).*?(?=\n---|\n##)",
            lambda m: m.group(1) + "\n" + priorities + "\n",
            text, count=1, flags=re.DOTALL,
        )

    # Append new chat log entry at end
    text = text.rstrip("\n")
    text += f"\n\n---\n\n{chat_entry}\n"

    return text


# ── sfl_agent.py updater ──────────────────────────────────────────────────────

def update_sfl_agent(new_ver):
    sfl_path = HERE / "sfl_agent.py"
    if not sfl_path.exists():
        return False
    text = sfl_path.read_text(encoding="utf-8", errors="replace")
    new_text = re.sub(
        r'(HANDOVER_FILENAME\s*=\s*")VKB_SpinDoctor_Handover_v\d+\.md(")',
        lambda m: m.group(1) + f"VKB_SpinDoctor_Handover_v{new_ver}.md" + m.group(2),
        text, count=1,
    )
    if new_text == text:
        return False
    sfl_path.write_text(new_text, encoding="utf-8")
    return True


# ── Session log writer ────────────────────────────────────────────────────────

def write_session_log(log_path, old_ver, new_ver, chat_summary, chat_entry):
    SESSION_LOGS.mkdir(exist_ok=True)
    name = log_path.stem
    content = (
        f"# Session Log -- {name}\n\n"
        f"**Handover:** v{old_ver} -> v{new_ver}\n"
        f"**Focus:** WCCS automation run\n\n"
        f"## Chat Summary (from chat_latest.txt)\n\n"
        f"{chat_summary[:2000]}\n\n"
        f"## Generated Chat Log Entry\n\n"
        f"{chat_entry}\n\n"
        f"## Files written (WCCS)\n"
        f"- VKB_SpinDoctor_Handover_v{new_ver}.md\n"
        f"- wccs_log.md (row appended)\n"
        f"- {log_path.name} (this file)\n"
        f"- sfl_agent.py HANDOVER_FILENAME updated to v{new_ver}\n"
        f"- mcu_optimizer.py run\n"
        f"- dashboard_builder.py run\n"
    )
    log_path.write_text(content, encoding="utf-8")


# ── wccs_log.md appender ──────────────────────────────────────────────────────

def append_wccs_log(row_num, old_ver, new_ver, chat_summary, today):
    log_path = HERE / "wccs_log.md"
    focus = (chat_summary[:80].replace("\n", " ").replace("|", "/")).strip()
    row = f"| {row_num} | {today} | v{old_ver} -> v{new_ver} | {focus} | None |\n"
    if not log_path.exists():
        header = (
            "# WCCS Run Log\n\n"
            "**WCCS = Write Claude Code Save.** Each entry is one end-of-session save run.\n\n"
            "---\n\n"
            "| # | Date | Handover | Session Focus | ALP Rules Added |\n"
            "|---|---|---|---|---|\n"
        )
        log_path.write_text(header + row, encoding="utf-8")
    else:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(row)


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
