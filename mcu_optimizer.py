"""
mcu_optimizer.py — Mission Control Optimizer
Reads latest handover + last 3 session logs + mission_control_tasks.json,
sends context to AAFLCore (cheapest free provider), asks it to reorganise
tasks for the optimal path forward, writes updated JSON back, prints diff.

Usage:
    python mcu_optimizer.py
"""

import json
import re
import datetime
from pathlib import Path

from aafl_core import AAFLCore

HERE         = Path(__file__).parent
SESSION_LOGS = HERE / "session_logs"

# Desktop location — try standard first, OneDrive fallback
_DESKTOP_STD    = Path.home() / "Desktop"
_DESKTOP_OD     = Path.home() / "OneDrive" / "Desktop"
MCU_JSON = (
    _DESKTOP_STD / "mission_control_tasks.json"
    if (_DESKTOP_STD / "mission_control_tasks.json").exists()
    else _DESKTOP_OD / "mission_control_tasks.json"
)

AGENT_SYSTEM = (
    "You are an autonomous AI agent. "
    "Complete every task fully in a single response. "
    "Never ask follow-up questions. Never ask for clarification. "
    "Produce your complete answer and stop."
)

VALID_COLUMNS = {"Up Next", "In Progress", "Blocked", "Backlog", "Done"}


# ── Context readers ───────────────────────────────────────────────────────────

def find_latest_handover() -> Path | None:
    """Return path of highest-numbered VKB_SpinDoctor_Handover_vNN.md."""
    files = list(HERE.glob("VKB_SpinDoctor_Handover_v*.md"))
    if not files:
        return None
    def _ver(p):
        m = re.search(r"_v(\d+)\.md$", p.name)
        return int(m.group(1)) if m else 0
    return max(files, key=_ver)


def read_handover_context(path: Path) -> str:
    """Extract Status line + Next Priorities section from handover."""
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\*\*Status:\*\*(.+)", text)
    status = m.group(1).strip() if m else "(unknown)"
    m2 = re.search(r"## NEXT PRIORITIES\n(.*?)(?=\n---|\n##)", text, re.DOTALL)
    priorities = m2.group(1).strip() if m2 else "(not found)"
    return (
        f"### Handover: {path.name}\n"
        f"**Status:** {status}\n\n"
        f"**Next Priorities:**\n{priorities}"
    )


def read_session_logs(n: int = 3) -> str:
    """Return last N session log texts (capped at 40 lines each)."""
    if not SESSION_LOGS.exists():
        return "(no session logs found)"
    logs = sorted(
        SESSION_LOGS.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:n]
    if not logs:
        return "(no session logs found)"
    parts = []
    for log in logs:
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()[:40]
        parts.append(f"#### {log.name}\n" + "\n".join(lines))
    return "### Recent Session Logs\n\n" + "\n\n".join(parts)


def load_tasks() -> dict:
    if not MCU_JSON.exists():
        raise FileNotFoundError(f"mission_control_tasks.json not found at {MCU_JSON}")
    return json.loads(MCU_JSON.read_text(encoding="utf-8"))


def board_summary(tasks: list) -> str:
    """Format non-Done tasks as a detailed summary for the LLM."""
    done_count = sum(1 for t in tasks if t.get("column") == "Done")
    active = [t for t in tasks if t.get("column") != "Done"]

    lines = [
        f"### Current Mission Control Board ({len(tasks)} tasks total, {done_count} Done — Done tasks excluded below)",
        "",
    ]
    for col in ("Up Next", "In Progress", "Blocked", "Backlog"):
        col_tasks = [t for t in active if t.get("column") == col]
        if not col_tasks:
            continue
        lines.append(f"**{col}** ({len(col_tasks)})")
        for t in col_tasks:
            notes = (t.get("notes") or "")[:80].replace("\n", " ")
            lines.append(
                f"  [{t['id']}] [{t.get('priority','?')}] {t['title']}\n"
                f"    notes: {notes}"
            )
        lines.append("")
    return "\n".join(lines)


# ── Prompt ────────────────────────────────────────────────────────────────────

def build_prompt(handover_ctx: str, session_ctx: str, board_ctx: str,
                 active_ids: list[str]) -> str:
    ids_str = ", ".join(active_ids)
    return f"""You are optimising a software project's Mission Control task board.

Reorganise the active (non-Done) tasks for the optimal path forward based on the project's current status and priorities.

RULES:
- "Up Next"     = max 4 tasks — the most critical things to do RIGHT NOW, in order
- "In Progress" = tasks being actively worked on now (only if clearly active)
- "Blocked"     = tasks with a concrete external blocker; leave as-is unless clearly unblocked
- "Backlog"     = everything else not yet started; order by priority (high → medium → low)
- "Done"        = NEVER touch — do not include Done tasks in your output
- You may update column, priority, and notes (keep notes ≤ 100 chars)
- Do NOT invent new tasks. Do NOT delete tasks. Only reorganise existing ones.
- Active task IDs to include: {ids_str}

Return ONLY a valid JSON array. No explanation. No markdown fences. Start with [ end with ].

Each object must have exactly these keys:
  id, title, column, notes, priority, tool, created, updated

Set updated to today's date: {datetime.date.today().isoformat()}

--- CONTEXT ---

{handover_ctx}

{session_ctx}

{board_ctx}

--- OUTPUT (JSON array only) ---
"""


# ── JSON extraction ───────────────────────────────────────────────────────────

def extract_json_array(text: str) -> list | None:
    text = text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    if text.startswith("["):
        try:
            return json.loads(text)
        except Exception:
            pass
    # Find first [...] block spanning multiple lines
    m = re.search(r"\[[\s\S]*\]", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return None


# ── Diff ─────────────────────────────────────────────────────────────────────

def diff_tasks(old_tasks: list, new_tasks: list) -> list[str]:
    old_by_id = {t["id"]: t for t in old_tasks}
    new_by_id = {t["id"]: t for t in new_tasks}
    changes = []
    for tid, new_t in new_by_id.items():
        old_t = old_by_id.get(tid)
        if not old_t:
            continue
        label = f"[{tid}] {new_t.get('title','')[:45]}"
        col_old, col_new = old_t.get("column"), new_t.get("column")
        pri_old, pri_new = old_t.get("priority"), new_t.get("priority")
        if col_old != col_new:
            changes.append(f"  {label}: column  {col_old} -> {col_new}")
        if pri_old != pri_new:
            changes.append(f"  {label}: priority {pri_old} -> {pri_new}")
    return changes


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("[MCU] Mission Control Optimizer")

    # ── Load context ──────────────────────────────────────────────────────────
    handover_path = find_latest_handover()
    if not handover_path:
        print("[MCU] ERROR: No handover file found in project folder.")
        return
    print(f"[MCU] Handover:  {handover_path.name}")

    handover_ctx = read_handover_context(handover_path)
    session_ctx  = read_session_logs(3)
    board_data   = load_tasks()
    all_tasks    = board_data["tasks"]
    done_tasks   = [t for t in all_tasks if t.get("column") == "Done"]
    active_tasks = [t for t in all_tasks if t.get("column") != "Done"]
    active_ids   = [t["id"] for t in active_tasks]
    board_ctx    = board_summary(all_tasks)

    print(f"[MCU] Board:     {len(all_tasks)} tasks ({len(active_tasks)} active, {len(done_tasks)} Done)")
    print(f"[MCU] JSON path: {MCU_JSON}")

    # ── Send to LLM ───────────────────────────────────────────────────────────
    prompt = build_prompt(handover_ctx, session_ctx, board_ctx, active_ids)
    print("[MCU] Sending to AAFLCore (cheapest free provider)...")

    aafl   = AAFLCore(dry_run=False, allow_paid=False)
    result = aafl.run(prompt, task_type="batch", max_tokens=3000, system=AGENT_SYSTEM)

    if not result.ok or not result.response.strip():
        print("[MCU] ERROR: No usable response from provider.")
        return
    print(f"[MCU] Response:  {result.provider_id}  ${result.cost_usd:.5f}")

    # ── Parse ─────────────────────────────────────────────────────────────────
    new_active = extract_json_array(result.response)
    if not new_active or not isinstance(new_active, list):
        print("[MCU] ERROR: Could not parse JSON array from LLM response.")
        print("[MCU] Raw response (first 600 chars):")
        print(result.response[:600])
        return

    # Safety: only keep tasks whose IDs exist in the original active list
    valid_ids  = set(active_ids)
    new_active = [t for t in new_active if isinstance(t, dict) and t.get("id") in valid_ids]

    # Safety: re-add any active tasks the LLM dropped
    returned_ids = {t["id"] for t in new_active}
    for t in active_tasks:
        if t["id"] not in returned_ids:
            new_active.append(t)
            print(f"  [SAFETY] [{t['id']}] preserved — LLM dropped it")

    # Safety: never touch Done tasks
    for t in new_active:
        if t.get("column") == "Done":
            orig = next((o for o in active_tasks if o["id"] == t["id"]), None)
            if orig:
                t["column"] = orig["column"]

    # Safety: validate column values
    for t in new_active:
        if t.get("column") not in VALID_COLUMNS:
            t["column"] = "Backlog"

    # ── Diff + write ─────────────────────────────────────────────────────────
    changes = diff_tasks(active_tasks, new_active)

    board_data["tasks"] = new_active + done_tasks
    board_data["meta"]["updated"]    = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    board_data["meta"]["updated_by"] = "mcu_optimizer"
    MCU_JSON.write_text(
        json.dumps(board_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\n[MCU] {len(changes)} change(s):")
    if changes:
        for c in changes:
            print(c)
    else:
        print("  (no column or priority changes - board already optimal)")
    print(f"[MCU] Written -> {MCU_JSON}")


if __name__ == "__main__":
    main()
