"""
meta_loop.py — AAFL Self-Improving Meta-Loop

Reads recent loop reports, picks the next goal from meta_queue.txt,
runs it through scout → plan → work → score, gets a second opinion,
and writes a proposal markdown. Dry-run by default — no code changes
unless --apply is passed.

Usage:
  python meta_loop.py           # dry-run, process next goal in queue
  python meta_loop.py --once    # explicit single-goal (same as default)
  python meta_loop.py --apply   # write code changes after snapshot + regression

Hard cap: 3 meta-goals max per invocation.
"""

import sys
import re
import json
import sqlite3
import datetime
import shutil
import subprocess
import statistics
from collections import Counter
from pathlib import Path

from aafl_core import AAFLCore
from evaluator import evaluate

HERE            = Path(__file__).parent
LOOP_OUTPUT     = HERE / "loop_output"
META_QUEUE      = HERE / "meta_queue.txt"
META_PROPOSALS  = HERE / "meta_proposals"
BACKUPS_DIR     = HERE / "backups"
AAFL_LOG        = HERE / "aafl_log.txt"
DB_PATH         = HERE / "data" / "knowledge_engine.db"

AGENT_SYSTEM = (
    "You are an autonomous AI agent operating inside an automated feedback loop. "
    "You have internet access — web search results are provided in the prompt when available. "
    "Complete every task fully and definitively in a single response. "
    "Never ask follow-up questions. Never ask for clarification. "
    "Never end with phrases like 'Would you like more details?', "
    "'Let me know if you need anything else', or any similar invitation. "
    "Produce your complete answer and stop."
)

MAX_META_GOALS      = 3
APPROVAL_THRESHOLD  = 8.5


# ── Report parsing ────────────────────────────────────────────────────────────

def read_loop_reports(n: int = 10) -> list:
    """Parse last N .md reports from loop_output/. Returns list of dicts."""
    if not LOOP_OUTPUT.exists():
        return []

    md_files = sorted(
        LOOP_OUTPUT.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:n]

    reports = []
    for f in md_files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
            report = {"file": f.name}

            m = re.search(r"\*\*Score:\*\*\s*([\d.]+)", text)
            report["score"] = float(m.group(1)) if m else None

            m = re.search(r"\*\*Total cost:\*\*\s*[£$]?([\d.]+)", text)
            report["cost"] = float(m.group(1)) if m else None

            m = re.search(r"\*\*Stop reason:\*\*\s*(.+)", text)
            report["stop_reason"] = m.group(1).strip() if m else "unknown"

            m = re.search(r"\*\*Goal:\*\*\s*(.+)", text)
            report["goal"] = m.group(1).strip() if m else ""

            reports.append(report)
        except Exception:
            continue
    return reports


def compute_stats(reports: list) -> dict:
    """Calculate avg score, common failures, avg cost, slowest provider."""
    stats = {
        "report_count":    len(reports),
        "avg_score":       None,
        "common_failures": [],
        "avg_cost":        None,
        "slowest_provider": "unknown",
    }

    scores = [r["score"] for r in reports if r.get("score") is not None]
    costs  = [r["cost"]  for r in reports if r.get("cost")  is not None]

    if scores:
        stats["avg_score"] = round(statistics.mean(scores), 2)
    if costs:
        stats["avg_cost"] = round(statistics.mean(costs), 6)

    reasons = [r["stop_reason"] for r in reports if r.get("stop_reason")]
    if reasons:
        top = Counter(reasons).most_common(3)
        stats["common_failures"] = [r for r, _ in top]

    # Parse aafl_log.txt for slowest provider
    if AAFL_LOG.exists():
        try:
            provider_times: dict = {}
            log_lines = AAFL_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
            for line in log_lines[-500:]:   # last 500 log lines
                m = re.search(r"\] (OK|DRY)\s+\S+\s+(\S+)\s+\$\S+\s+([\d.]+)s", line)
                if m:
                    pid     = m.group(2)
                    elapsed = float(m.group(3))
                    provider_times.setdefault(pid, []).append(elapsed)
            if provider_times:
                avg_times = {p: statistics.mean(ts) for p, ts in provider_times.items()}
                stats["slowest_provider"] = max(avg_times, key=avg_times.get)
        except Exception:
            pass

    return stats


# ── Queue management ──────────────────────────────────────────────────────────

def read_next_goal() -> tuple:
    """Return (goal_text, line_index) of next uncommented goal, or (None, None)."""
    if not META_QUEUE.exists():
        return None, None

    lines = META_QUEUE.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped, idx
    return None, None


def comment_out_goal(line_idx: int) -> None:
    """Prefix the goal line with '# DONE ' to mark it processed."""
    lines = META_QUEUE.read_text(encoding="utf-8").splitlines()
    if 0 <= line_idx < len(lines):
        lines[line_idx] = "# DONE " + lines[line_idx]
    META_QUEUE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _goal_slug(goal: str) -> str:
    words = re.sub(r"[^\w\s]", "", goal).split()[:5]
    return "_".join(w.lower() for w in words)[:50]


# ── Context injection ─────────────────────────────────────────────────────────

def _inject_file_context(goal: str) -> str:
    """If goal mentions a source file, read and return its full content (capped at 600 lines)."""
    goal_lower = goal.lower()
    targets = []

    if "loop_manager" in goal_lower:
        targets.append(HERE / "loop_manager.py")
    if "aafl_core" in goal_lower:
        targets.append(HERE / "aafl_core.py")
    if "evaluator" in goal_lower:
        targets.append(HERE / "evaluator.py")
    if "researcher" in goal_lower:
        targets.append(HERE / "researcher.py")

    if not targets:
        return ""

    LINE_CAP = 600
    parts = []
    for p in targets:
        if p.exists():
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            total = len(lines)
            truncated = total > LINE_CAP
            lines = lines[:LINE_CAP]
            note = f"first {LINE_CAP} of {total} lines — truncated" if truncated else f"{total} lines — full file"
            parts.append(f"### {p.name} ({note})\n```python\n" + "\n".join(lines) + "\n```")
    return "\n\n".join(parts)


def _inject_db_context(goal: str) -> str:
    """Query solution_log + knowledge.metadata and inject real rows for analytical goals."""
    goal_lower = goal.lower()
    ANALYSIS_KEYWORDS = (
        "solution_log", "knowledge_engine", "provider", "success rate",
        "bottleneck", "loop_manager", "latency", "tier", "score",
        "performance", "analyse", "analyze", "identify", "improve",
    )
    if not any(k in goal_lower for k in ANALYSIS_KEYWORDS):
        return ""
    if not DB_PATH.exists():
        return "DB not yet populated — no solution_log data available."

    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            """SELECT id, problem, worked, ai_score, failure_reason,
                      tags, iterations, game, hardware, created_at
               FROM solution_log ORDER BY id DESC LIMIT 20"""
        ).fetchall()

        lines = [
            f"### solution_log — real rows ({len(rows)} entries, all columns)",
            "| id | problem (50 chars) | worked | score | tags | iters | game | date |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in rows:
            prob = (r["problem"] or "")[:50].replace("|", "/")
            lines.append(
                f"| {r['id']} | {prob} | {'Y' if r['worked'] else 'N'} | "
                f"{r['ai_score']} | {(r['tags'] or '')[:30]} | "
                f"{r['iterations']} | {r['game'] or ''} | {(r['created_at'] or '')[:10]} |"
            )

        # Provider usage from knowledge.metadata
        meta_rows = conn.execute(
            "SELECT metadata FROM knowledge WHERE source_type='loop_attempt' LIMIT 50"
        ).fetchall()
        conn.close()

        provider_scores: dict = {}
        for mr in meta_rows:
            try:
                meta = json.loads(mr["metadata"] or "{}")
                for key in ("plan_provider", "work_provider"):
                    pid = meta.get(key)
                    sc  = meta.get("eval_overall")
                    if pid and sc is not None:
                        provider_scores.setdefault(pid, []).append(float(sc))
            except Exception:
                continue

        if provider_scores:
            lines += ["", "### Provider avg scores (from knowledge.metadata)",
                      "| Provider | Calls | Avg score |",
                      "|---|---|---|"]
            for pid, sc_list in sorted(provider_scores.items()):
                lines.append(f"| {pid} | {len(sc_list)} | {statistics.mean(sc_list):.2f} |")
        else:
            lines += ["", "### Provider scores",
                      "No provider metadata stored in knowledge table yet.",
                      "Provider performance data comes from loop_output reports — see below."]

        return "\n".join(lines)

    except Exception as exc:
        return f"DB query failed: {exc}"


def _inject_loop_reports(goal: str, n: int = 3) -> str:
    """Inject recent loop_output report text for bottleneck/performance analysis goals."""
    goal_lower = goal.lower()
    REPORT_KEYWORDS = (
        "bottleneck", "performance", "loop_manager", "provider",
        "latency", "tier", "score", "loop_output",
    )
    if not any(k in goal_lower for k in REPORT_KEYWORDS):
        return ""
    if not LOOP_OUTPUT.exists():
        return ""

    md_files = sorted(
        LOOP_OUTPUT.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:n]

    if not md_files:
        return ""

    parts = [f"### Recent loop_output reports (last {len(md_files)} — real data)"]
    for f in md_files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
            report_lines = text.splitlines()[:80]
            parts.append(f"\n#### {f.name}\n```\n" + "\n".join(report_lines) + "\n```")
        except Exception:
            continue
    return "\n".join(parts)


def _format_stats(stats: dict) -> str:
    """Format the loop stats dict as a small markdown table."""
    if stats["report_count"] == 0:
        return "No loop reports found yet — this is likely the first meta-loop run."

    rows = [
        f"| Reports analysed | {stats['report_count']} |",
        f"| Avg score | {stats['avg_score'] or 'n/a'} / 10 |",
        f"| Common stop reasons | {', '.join(stats['common_failures']) or 'n/a'} |",
        f"| Avg cost per run | £{stats['avg_cost']:.6f} |" if stats["avg_cost"] is not None
            else "| Avg cost per run | n/a |",
        f"| Slowest provider | {stats['slowest_provider']} |",
    ]
    return "| Metric | Value |\n|---|---|\n" + "\n".join(rows)


# ── Core meta-goal runner ─────────────────────────────────────────────────────

def run_meta_goal(goal: str, stats: dict, aafl: AAFLCore, apply: bool) -> dict:
    """
    Run scout → plan → work → score → second-opinion for one meta-goal.
    Returns dict with proposal_path, score1, score2, approved.
    """
    print(f"\n[META] Goal: {goal}")

    # ── Scout (web search — optional) ────────────────────────────────────────
    web_context = ""
    try:
        from researcher import scout
        briefing = scout(goal)
        if briefing.get("results"):
            web_context = briefing["briefing"]
            print(f"[META] Scout: {len(briefing['results'])} source(s) found")
        else:
            print("[META] Scout: no web results — continuing without web context")
    except Exception as exc:
        print(f"[META] Scout failed ({exc}) — continuing without web context")

    stats_ctx  = _format_stats(stats)
    file_ctx   = _inject_file_context(goal)
    db_ctx     = _inject_db_context(goal)
    report_ctx = _inject_loop_reports(goal)

    # ── Plan ─────────────────────────────────────────────────────────────────
    plan_prompt = (
        f"You are analysing an AI feedback loop system called AAFL (AI Agent Feedback Loop). "
        f"Plan how to fully analyse and answer this goal:\n\n{goal}"
    )
    if stats_ctx:
        plan_prompt += f"\n\n## Recent Loop Performance Stats\n{stats_ctx}"
    if web_context:
        plan_prompt += f"\n\n## Web Context\n{web_context}"

    print("[META] Planning...")
    plan_result = aafl.run(plan_prompt, task_type="reason", max_tokens=1024, system=AGENT_SYSTEM)
    if not plan_result.ok:
        print("[META] Plan step failed — no provider available. Skipping goal.")
        return {}

    # ── Work (primary opinion) ────────────────────────────────────────────────
    work_prompt = (
        f"Execute this analysis fully. Produce a complete, specific answer.\n\n"
        f"Goal: {goal}\n\nPlan:\n{plan_result.response}"
    )
    if file_ctx:
        work_prompt += f"\n\n## Relevant Source Code\n{file_ctx}"
    if db_ctx:
        work_prompt += f"\n\n## Database — Real Rows\n{db_ctx}"
    if report_ctx:
        work_prompt += f"\n\n## Loop Output Reports — Real Data\n{report_ctx}"
    if stats_ctx:
        work_prompt += f"\n\n## Loop Performance Stats\n{stats_ctx}"

    print("[META] Working (primary opinion)...")
    work_result = aafl.run(work_prompt, task_type="reason", max_tokens=2048, system=AGENT_SYSTEM)
    if not work_result.ok or not work_result.response.strip():
        print("[META] Work step failed — skipping goal.")
        return {}

    scores1   = evaluate(work_result.response, goal)
    score1    = scores1["overall"]
    provider1 = work_result.provider_id
    print(f"[META] Primary score: {score1}/10  (provider: {provider1})")

    # ── Second opinion ────────────────────────────────────────────────────────
    # Use task_type="batch" which routes to Mistral first — different from
    # "reason" which routes to Cerebras/Groq/Gemini first.
    print("[META] Working (second opinion)...")
    op2_result = aafl.run(work_prompt, task_type="batch", max_tokens=2048, system=AGENT_SYSTEM)
    if op2_result.ok and op2_result.response.strip():
        scores2   = evaluate(op2_result.response, goal)
        score2    = scores2["overall"]
        provider2 = op2_result.provider_id
        # Use whichever opinion scored higher for the proposal body
        final_work = op2_result.response if score2 > score1 else work_result.response
    else:
        print("[META] Second opinion unavailable — using primary score twice")
        score2    = score1
        provider2 = f"{provider1} (repeated)"
        final_work = work_result.response

    print(f"[META] Second opinion: {score2}/10  (provider: {provider2})")

    approved = (score1 >= APPROVAL_THRESHOLD) and (score2 >= APPROVAL_THRESHOLD)
    if approved:
        print(f"[META] APPROVED — both scores >= {APPROVAL_THRESHOLD}")
    else:
        print(f"[META] FLAGGED — one or both scores below {APPROVAL_THRESHOLD}")

    # ── Write proposal ────────────────────────────────────────────────────────
    proposal_path = write_proposal(
        goal      = goal,
        plan      = plan_result.response,
        work      = final_work,
        score1    = score1,
        provider1 = provider1,
        score2    = score2,
        provider2 = provider2,
        stats     = stats,
        approved  = approved,
        apply     = apply,
    )

    # ── Apply (only when --apply passed AND approved) ─────────────────────────
    if apply:
        if not approved:
            print(f"[META] --apply skipped: scores below {APPROVAL_THRESHOLD} threshold")
        else:
            snap = _snapshot_backups()
            print(f"[META] Snapshot saved: {snap}")
            changed = _apply_proposal(proposal_path)
            if changed:
                passed = _run_regression()
                if not passed:
                    print("[META] Regression FAILED — restoring snapshot")
                    _restore_snapshot(snap)
                    print("[META] Snapshot restored. Changes reverted.")
                else:
                    print("[META] Regression PASSED — changes kept.")
            else:
                print("[META] No CHANGE FILE blocks found in proposal — nothing applied.")

    print(f"[META] Proposal written: {proposal_path}")
    return {
        "proposal_path": proposal_path,
        "score1":        score1,
        "score2":        score2,
        "approved":      approved,
    }


# ── Proposal writer ───────────────────────────────────────────────────────────

def write_proposal(goal: str, plan: str, work: str,
                   score1: float, provider1: str,
                   score2: float, provider2: str,
                   stats: dict, approved: bool, apply: bool) -> Path:
    """Write structured proposal markdown. Hard cap: 200 lines."""
    META_PROPOSALS.mkdir(exist_ok=True)

    date_str  = datetime.date.today().isoformat()
    slug      = _goal_slug(goal)
    fname     = f"{date_str}_{slug}.md"
    out_path  = META_PROPOSALS / fname
    n = 2
    while out_path.exists():
        out_path = META_PROPOSALS / f"{date_str}_{slug}_{n}.md"
        n += 1

    ts         = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    status_tag = "APPROVED" if approved else f"FLAGGED (below {APPROVAL_THRESHOLD})"
    mode_tag   = "APPLIED" if (apply and approved) else "DRY-RUN (proposal only)"

    header = [
        f"# Meta-Loop Proposal: {date_str} — {slug}",
        "",
        f"**Goal:** {goal}",
        f"**Generated:** {ts}",
        f"**Status:** {status_tag}",
        f"**Mode:** {mode_tag}",
        f"**Primary score:** {score1} / 10  (provider: {provider1})",
        f"**Second opinion:** {score2} / 10  (provider: {provider2})",
        "",
        "## Loop Stats",
        "",
        _format_stats(stats),
        "",
        "## Analysis",
        "",
    ]

    footer = [
        "",
        "## How to Apply",
        "",
        "If this proposal contains a `CHANGE FILE` block, pass `--apply` to meta_loop.py:",
        "```",
        "python meta_loop.py --apply",
        "```",
        "This snapshots backups/, writes the change, runs regression_test.bat,",
        "and restores from snapshot if the regression score drops.",
        "",
        "---",
        f"*Generated by meta_loop.py — AAFL Self-Improving Meta-Loop*",
    ]

    # Budget: 200 - len(header) - len(footer) lines for analysis
    budget    = 200 - len(header) - len(footer)
    work_lines = work.splitlines()
    if len(work_lines) > budget:
        work_lines = work_lines[:budget - 2] + ["", "*(truncated to fit 200-line budget)*"]

    all_lines = header + work_lines + footer

    out_path.write_text("\n".join(all_lines), encoding="utf-8")
    return out_path


# ── Snapshot + apply + regression ─────────────────────────────────────────────

def _snapshot_backups() -> Path:
    """Copy all .py and .json project files to backups/meta_YYYYMMDD_HHMMSS/."""
    stamp   = datetime.datetime.now().strftime("meta_%Y%m%d_%H%M%S")
    snap_dir = BACKUPS_DIR / stamp
    snap_dir.mkdir(parents=True, exist_ok=True)

    for pattern in ("*.py", "*.json", "*.bat", "*.txt"):
        for src in HERE.glob(pattern):
            shutil.copy2(src, snap_dir / src.name)

    return snap_dir


def _apply_proposal(proposal_path: Path) -> bool:
    """
    Parse CHANGE FILE blocks from the proposal and write them to disk.
    Block format:
      **CHANGE FILE:** `relative/path/to/file.py`
      ```python
      new content here
      ```
    Returns True if at least one file was written.
    """
    text    = proposal_path.read_text(encoding="utf-8")
    pattern = r"\*\*CHANGE FILE:\*\*\s*`([^`]+)`\s*```(?:\w+)?\n([\s\S]*?)```"
    matches = re.findall(pattern, text)
    if not matches:
        return False

    for rel_path, code in matches:
        target = HERE / rel_path.strip()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code, encoding="utf-8")
        print(f"[META] Applied change → {target}")
    return True


def _run_regression() -> bool:
    """
    Run regression_test.bat and return True if it exits 0 (PASS).
    Captures stdout/stderr and prints them.
    """
    bat = HERE / "regression_test.bat"
    if not bat.exists():
        print("[META] regression_test.bat not found — assuming PASS")
        return True

    try:
        result = subprocess.run(
            [str(bat)],
            cwd=str(HERE),
            capture_output=True,
            text=True,
            timeout=120,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as exc:
        print(f"[META] Regression test error: {exc}")
        return False


def _restore_snapshot(snap_dir: Path) -> None:
    """Copy all files from snap_dir back to HERE, overwriting current versions."""
    for src in snap_dir.iterdir():
        if src.is_file():
            shutil.copy2(src, HERE / src.name)
            print(f"[META] Restored: {src.name}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    apply    = "--apply" in sys.argv
    once     = "--once" in sys.argv or True   # default is always single-goal
    # Without --once the loop processes up to MAX_META_GOALS sequentially.
    # Add explicit multi-goal support by NOT forcing once when --all is passed.
    if "--all" in sys.argv:
        once = False

    mode_label = "DRY-RUN" if not apply else "APPLY"
    print(f"\n[META] AAFL Meta-Loop — {mode_label}")
    print(f"[META] Max goals this run: {'1 (--once)' if once else MAX_META_GOALS}")

    META_PROPOSALS.mkdir(exist_ok=True)

    aafl    = AAFLCore(dry_run=False, allow_paid=False)
    reports = read_loop_reports(10)
    stats   = compute_stats(reports)

    print(f"[META] Loop reports found: {stats['report_count']}")
    if stats["avg_score"] is not None:
        print(f"[META] Avg score: {stats['avg_score']}/10 | "
              f"Avg cost: £{stats['avg_cost']:.6f} | "
              f"Slowest provider: {stats['slowest_provider']}")

    goals_run = 0
    last_proposal = None

    while goals_run < MAX_META_GOALS:
        goal, line_idx = read_next_goal()
        if goal is None:
            print("[META] Queue empty — no goals to process.")
            break

        result = run_meta_goal(goal, stats, aafl, apply)
        if result and result.get("proposal_path"):
            last_proposal = result["proposal_path"]
            comment_out_goal(line_idx)
        goals_run += 1

        if once:
            break

    print(f"\n[META] Done. {goals_run} meta-goal(s) processed.")
    if last_proposal:
        print(f"[META] Proposal: {last_proposal}")
        # Print full path as required
        print(f"\n{'='*60}")
        print(f"PROPOSAL PATH: {last_proposal.resolve()}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
