"""
loop_manager.py — Minimum Viable Loop Engine.
Reads goal from goal.txt, loops plan → work → verify → store → cost check.
Phases B+C+D: DB cache, scout agent, source reputation, tag taxonomy.
Writes morning_report.md when done.
"""
import re
import sys
import datetime
from pathlib import Path

try:
    import winsound
    import ctypes
    _NOTIFY_OK = True
except ImportError:
    _NOTIFY_OK = False


def _notify_done(stop_reason: str, iterations: int, total_cost: float) -> None:
    """Windows beep + message box notification at end of an overnight run. stdlib only."""
    if not _NOTIFY_OK:
        return
    try:
        winsound.Beep(880, 200)
        winsound.Beep(1100, 350)
    except Exception:
        pass
    try:
        msg = (f"Stop reason: {stop_reason}\n"
               f"Iterations: {iterations}\n"
               f"Cost: £{total_cost:.6f}")
        ctypes.windll.user32.MessageBoxW(None, msg, "AAFL Run Complete", 0x40)
    except Exception:
        pass

from aafl_core import AAFLCore
from memory_bank import (
    store, search_solution, search_failures, store_solution,
    update_source, TAGS, infer_tags_from_keywords,
)
from researcher import scout
USE_CHIEF_SCOUT = True
try: from chief_scout import chief_scout as _chief_scout
except ImportError: _chief_scout = None
from cost_guard import CostGuard, CostGuardError
from evaluator import evaluate

# Injected into every LLM call so models behave as agents, not chatbots.
AGENT_SYSTEM = (
    "You are an autonomous AI agent operating inside an automated feedback loop. "
    "You have internet access — web search results are provided in the prompt when available. "
    "Complete every task fully and definitively in a single response. "
    "Never ask follow-up questions. Never ask for clarification. "
    "Never end with phrases like 'Would you like more details?', "
    "'Let me know if you need anything else', or any similar invitation. "
    "Produce your complete answer and stop."
)

HERE = Path(__file__).parent


def load_goal() -> str:
    goal_path = HERE / "goal.txt"
    if not goal_path.exists():
        raise FileNotFoundError(
            "goal.txt not found — create it with your goal on the first line"
        )
    return goal_path.read_text(encoding="utf-8-sig").strip()


def _detect_game(goal: str) -> str:
    text = goal.lower()
    if "war thunder" in text:
        return "war_thunder"
    if "elite dangerous" in text or "elite: dangerous" in text:
        return "elite_dangerous"
    if "star citizen" in text:
        return "star_citizen"
    if "dcs" in text:
        return "dcs"
    return "unknown"


def _goal_slug(goal: str) -> str:
    words = re.sub(r"[^\w\s]", "", goal).split()[:4]
    return "_".join(w.lower() for w in words)


def _write_report(goal: str, iterations: int, best: dict | None,
                  total_cost: float, stop_reason: str):
    out_dir  = HERE / "loop_output"
    out_dir.mkdir(exist_ok=True)
    stamp    = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    slug     = _goal_slug(goal)
    out_path = out_dir / f"{stamp}_{slug}.md"
    n = 2
    while out_path.exists():
        out_path = out_dir / f"{stamp}_{slug}_{n}.md"
        n += 1

    now   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Morning Report — {now}",
        "",
        f"**Goal:** {goal}",
        f"**Stop reason:** {stop_reason}",
        f"**Iterations completed:** {iterations}",
        f"**Total cost:** £{total_cost:.6f}",
        "",
    ]
    if best:
        lines += [
            "## Best Attempt",
            "",
            f"**ID:** {best.get('id', 'n/a')}",
            f"**Score:** {best.get('quality_score', 'n/a')}",
            "",
            "### Plan",
            "",
            best.get("plan", "(none)"),
            "",
            "### Work",
            "",
            best.get("work", "(none)"),
            "",
        ]
    else:
        lines.append("_No successful attempt recorded._")

    text = "\n".join(lines)
    out_path.write_text(text, encoding="utf-8")
    (HERE / "morning_report.md").write_text(text, encoding="utf-8")


def run_loop(max_loop_iters: int = 50, max_llm_calls: int = 200):
    goal  = load_goal()
    aafl  = AAFLCore(dry_run=False, allow_paid=False)
    guard = CostGuard(max_cost_gbp=0.05, max_iterations=max_llm_calls)

    print(f"[LOOP] Goal: {goal}")
    print(f"[LOOP] Max iterations: {max_loop_iters}")

    # ── Phase B — check DB for past solution ──────────────────────────────────
    past = search_solution(goal)
    if past:
        print(f"[DB] Past solution found (score {past['ai_score']}) — using it")
        _write_report(
            goal,
            iterations=0,
            best={
                "id":            past.get("id", "n/a"),
                "quality_score": past["ai_score"],
                "plan":          "(from DB cache)",
                "work":          past.get("approach", ""),
            },
            total_cost=0.0,
            stop_reason="db_cache_hit",
        )
        print(f"[LOOP] Done (DB cache hit).")
        return

    iterations    = 0
    best_attempt  = None
    stop_reason   = "max_iterations"
    prev_feedback = ""

    while iterations < max_loop_iters:
        if (HERE / "STOP").exists():
            stop_reason = "STOP file found"
            break

        iterations += 1
        print(f"\n[LOOP] === Iteration {iterations}/{max_loop_iters} ===")

        # ── Phase C — scout ───────────────────────────────────────────────────
        try:
            briefing_data = (_chief_scout(goal) if USE_CHIEF_SCOUT and _chief_scout else scout(goal))
            n_sources     = len(briefing_data["results"])
            print(f"[SCOUT] Briefing ready — {n_sources} source(s) found")
            briefing_text = briefing_data["briefing"]
        except Exception as exc:
            print(f"[SCOUT] Failed ({exc}) — continuing without web context")
            briefing_data = {"results": []}
            briefing_text = ""

        # ── Phase B — failure injection ───────────────────────────────────────
        past_failures = search_failures(goal)
        failure_note  = ""
        if past_failures:
            failure_note = "Approaches that failed previously:\n" + "\n".join(
                f"- {f}" for f in past_failures
            )

        # ── Plan ──────────────────────────────────────────────────────────────
        try:
            guard.check_before_call(0.0)
        except CostGuardError as e:
            stop_reason = f"cost_guard: {e}"
            break

        print("[LOOP] Planning...")
        plan_prompt = f"Plan how to achieve this goal step by step: {goal}"
        if briefing_data["results"]:          # only inject when search actually returned content
            plan_prompt += f"\n\n{briefing_text}"
        if failure_note:
            plan_prompt += f"\n\n{failure_note}"

        plan_result = aafl.run(
            task=plan_prompt,
            task_type="reason",
            max_tokens=1024,
            system=AGENT_SYSTEM,
        )
        guard.record_call(plan_result.cost_usd)

        if not plan_result.ok:
            print("[LOOP] Plan step: no provider available — skipping")
            continue

        plan_text = plan_result.response

        # ── Loop detection ────────────────────────────────────────────────────
        try:
            guard.detect_loop(plan_text[:60])
        except CostGuardError as e:
            stop_reason = f"cost_guard: {e}"
            break

        # ── Work ──────────────────────────────────────────────────────────────
        try:
            guard.check_before_call(0.0)
        except CostGuardError as e:
            stop_reason = f"cost_guard: {e}"
            break

        print("[LOOP] Working...")
        work_task = f"Execute this plan to achieve the goal.\n\nGoal: {goal}\n\nPlan:\n{plan_text}"
        if briefing_data["results"]:          # give the work step the same web context as the plan
            work_task += f"\n\n{briefing_text}"
        if prev_feedback:
            work_task += f"\n\nNote from previous attempt: {prev_feedback}"
        work_result = aafl.run(
            task=work_task,
            task_type="code",
            max_tokens=1024,
            system=AGENT_SYSTEM,
        )
        guard.record_call(work_result.cost_usd)

        if not work_result.ok:
            print("[LOOP] Work step: no provider available — skipping")
            continue

        work_text = work_result.response

        # Guard: evaluator must never receive empty content — verify() can pass
        # for reasoning-model responses that contain only whitespace after
        # stripping think tags, so check explicitly before scoring.
        if not work_text.strip():
            print("[LOOP] Verify: empty content after provider response — skipping")
            continue

        # ── Evaluate ──────────────────────────────────────────────────────────
        scores   = evaluate(work_text, goal)
        score    = scores["overall"]
        weak     = [k for k, v in scores.items() if k != "overall" and v < 7.0]
        print(f"[LOOP] Score: {score}/10  "
              f"(completeness={scores['completeness']}  "
              f"clarity={scores['clarity']}  "
              f"accuracy={scores['accuracy']})")

        goal_met = score >= 7.0
        if not goal_met:
            weak_str      = ", ".join(weak) if weak else "overall quality"
            prev_feedback = f"Previous score was {score}/10. Weak areas: {weak_str}. Improve these."
            print(f"[LOOP] Score below 7 — weak: {weak_str}. Looping again.")
        else:
            prev_feedback = ""
            print(f"[LOOP] Score >= 7 — goal met.")

        # ── Phase D — tag inference ───────────────────────────────────────────
        tags_str  = ""
        try:
            guard.check_before_call(0.0)
            tag_prompt = (
                f"From this list: {TAGS}\n"
                f"Pick up to 5 tags that best describe this goal: {goal}\n"
                f"Reply with ONLY the tag names separated by commas. No explanation."
            )
            tag_result = aafl.run(task=tag_prompt, task_type="fast", max_tokens=200, system=AGENT_SYSTEM)
            guard.record_call(tag_result.cost_usd)
            if tag_result.ok:
                raw_tags  = [t.strip().lower() for t in tag_result.response.split(",")]
                valid_tags = [t for t in raw_tags if t in TAGS][:5]
                tags_str   = ",".join(valid_tags)
        except CostGuardError as e:
            stop_reason = f"cost_guard: {e}"
            break
        except Exception:
            pass

        if not tags_str:
            tags_str = infer_tags_from_keywords(goal)

        game = _detect_game(goal)

        # ── Phase B — store solution ──────────────────────────────────────────
        failure_reason = prev_feedback if not goal_met else None
        store_solution(
            problem=goal,
            approach=work_text[:200],
            worked=goal_met,
            failure_reason=failure_reason,
            ai_score=score,
            tags=tags_str,
            cost_tokens=0,
            iterations=iterations,
            game=game,
            hardware="vkb_nxt_evo",
        )

        # ── Phase C — update source reputation ───────────────────────────────
        for src in briefing_data["results"]:
            domain = src.get("domain", "")
            if domain:
                update_source(domain, score)

        # ── Store to knowledge table ──────────────────────────────────────────
        entry_id = store({
            "title":         f"Loop attempt #{iterations}",
            "content":       work_text,
            "project":       "loop_manager",
            "source_type":   "loop_attempt",
            "quality_score": score,
            "tags":          ["loop_attempt"] + (tags_str.split(",") if tags_str else []),
            "metadata":      {
                "plan":              plan_text,
                "goal_met":          goal_met,
                "iteration":         iterations,
                "plan_provider":     plan_result.provider_id,
                "work_provider":     work_result.provider_id,
                "eval_completeness": scores["completeness"],
                "eval_clarity":      scores["clarity"],
                "eval_accuracy":     scores["accuracy"],
                "eval_overall":      score,
                "tags":              tags_str,
                "game":              game,
            },
        })

        tag_display = tags_str if tags_str else "(none)"
        print(f"[DB] Stored — score: {score} | tags: [{tag_display}] | iterations: {iterations}")

        out_dir = HERE / "loop_output"; out_dir.mkdir(exist_ok=True)
        (out_dir / f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}_result.txt").write_text(work_text, encoding="utf-8")

        attempt = {
            "id":            entry_id,
            "quality_score": score,
            "plan":          plan_text,
            "work":          work_text,
        }
        if best_attempt is None or score > best_attempt.get("quality_score", 0):
            best_attempt = attempt

        if goal_met:
            stop_reason = "goal_met"
            break

        # ── End-of-iteration cost guard ───────────────────────────────────────
        try:
            guard.check_before_call(0.0)
        except CostGuardError as e:
            stop_reason = f"cost_guard: {e}"
            break
    else:
        stop_reason = "max_iterations"

    total_cost = guard.running_cost
    _write_report(goal, iterations, best_attempt, total_cost, stop_reason)

    print(f"\n[LOOP] Done.")
    print(f"[LOOP] Stop reason : {stop_reason}")
    print(f"[LOOP] Iterations  : {iterations}")
    print(f"[LOOP] Total cost  : £{total_cost:.6f}")
    print(f"[LOOP] Report      : {HERE / 'morning_report.md'}")
    _notify_done(stop_reason, iterations, total_cost)


if __name__ == "__main__":
    _once = "--once" in sys.argv
    if _once:
        run_loop(max_loop_iters=1, max_llm_calls=10)
    else:
        run_loop()
