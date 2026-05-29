"""
loop_manager.py — Minimum Viable Loop Engine.
Reads goal from goal.txt, loops plan → work → verify → store → cost check.
Phases B+C+D: DB cache, scout agent, source reputation, tag taxonomy.
Writes morning_report.md when done.
"""
import json as _json_lm
import os as _os_lm
import re
import shutil as _shutil_lm
import sys
import datetime
import tempfile as _tempfile_lm
import threading
from pathlib import Path

_LM_HERE = Path(__file__).parent
_LM_SS_FILE = _LM_HERE / "data" / "session_state.json"

def _lm_update_ss(patch: dict):
    """Merge patch into session_state.json (non-fatal)."""
    try:
        ss = _json_lm.loads(_LM_SS_FILE.read_text(encoding="utf-8")) if _LM_SS_FILE.exists() else {}
        ss.update(patch)
        fd, tmp = _tempfile_lm.mkstemp(dir=str(_LM_SS_FILE.parent), suffix=".tmp")
        with _os_lm.fdopen(fd, "w", encoding="utf-8") as f:
            _json_lm.dump(ss, f, indent=2)
        _shutil_lm.move(tmp, str(_LM_SS_FILE))
    except Exception:
        pass

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
try:
    from aafl_watchdog import run_cycle as _watchdog_run_cycle, check_loop_danger as _watchdog_check
    _WATCHDOG_OK = True
except ImportError:
    _watchdog_run_cycle = None
    _watchdog_check = None
    _WATCHDOG_OK = False
from evaluator import evaluate
try:
    from stuck_inbox import add_stuck_item as _add_stuck
except ImportError:
    _add_stuck = None

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


LOOP_OUTPUT_CAP = 50


def _cap_loop_output(out_dir: "Path") -> None:
    files = sorted(out_dir.glob("*"), key=lambda f: f.stat().st_mtime)
    if len(files) < LOOP_OUTPUT_CAP:
        return
    archive = HERE / "archive_dead" / "loop_output_old"
    archive.mkdir(parents=True, exist_ok=True)
    excess = files[: len(files) - LOOP_OUTPUT_CAP + 1]
    for f in excess:
        f.rename(archive / f.name)
    print(f"[CAP] loop_output: archived {len(excess)} oldest file(s) to archive_dead/loop_output_old/")


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
    _cap_loop_output(out_dir)


def run_loop(max_loop_iters: int = 50, max_llm_calls: int = 200):
    goal  = load_goal()
    aafl  = AAFLCore(dry_run=False, allow_paid=False)

    # Feature 3 — read cost cap from aafl_config.json
    _cost_cap_usd = 0.05
    try:
        from aafl_config_reader import get_cost_cap_usd
        _cost_cap_usd = get_cost_cap_usd()
    except Exception:
        pass
    _cost_cap_gbp = _cost_cap_usd * 0.79   # approximate conversion

    guard = CostGuard(max_cost_gbp=_cost_cap_gbp, max_iterations=max_llm_calls)

    print(f"[LOOP] Goal: {goal}")
    print(f"[LOOP] Max iterations: {max_loop_iters}")
    print(f"[LOOP] Cost cap: £{_cost_cap_gbp:.4f} (${_cost_cap_usd:.4f})")
    # Update session_state: AAFL run started
    _lm_update_ss({"current_task": {
        "type": "AAFL", "description": goal[:120], "subsystem": "loop_manager",
        "status": "running", "started_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }})

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

    iterations            = 0
    best_attempt          = None
    stop_reason           = "max_iterations"
    prev_feedback         = ""
    _consec_fails         = 0
    _last_best_score      = -1.0
    _provider_fail_streak = 0   # consecutive iterations where all providers failed

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
            _provider_fail_streak += 1
            print("[LOOP] Plan step: no provider available — skipping")
            if _WATCHDOG_OK and _watchdog_check is not None:
                _wd_danger, _wd_reason = _watchdog_check(
                    iterations, guard.running_cost, _provider_fail_streak)
                if _wd_danger:
                    stop_reason = _wd_reason
                    break
            continue

        plan_text = plan_result.response
        _provider_fail_streak = 0   # at least one provider responded

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
            _provider_fail_streak += 1
            print("[LOOP] Work step: no provider available — skipping")
            if _WATCHDOG_OK and _watchdog_check is not None:
                _wd_danger, _wd_reason = _watchdog_check(
                    iterations, guard.running_cost, _provider_fail_streak)
                if _wd_danger:
                    stop_reason = _wd_reason
                    break
            continue

        work_text = work_result.response

        # Guard: evaluator must never receive empty content — verify() can pass
        # for reasoning-model responses that contain only whitespace after
        # stripping think tags, so check explicitly before scoring.
        if not work_text.strip():
            print("[LOOP] Verify: empty content after provider response — skipping")
            continue

        # ── Save generated code to disk ───────────────────────────────────────
        _code_blocks = re.findall(r"```(?:python|py)?\n(.*?)```", work_text, re.DOTALL)
        if _code_blocks:
            _code_dir   = HERE / "loop_output"
            _code_dir.mkdir(exist_ok=True)
            _code_stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            _code_slug  = _goal_slug(goal)
            for _i, _block in enumerate(_code_blocks, 1):
                _suffix = f"_{_i}" if len(_code_blocks) > 1 else ""
                (_code_dir / f"{_code_stamp}_{_code_slug}{_suffix}.py").write_text(
                    _block, encoding="utf-8"
                )
            print(f"[CODE] {len(_code_blocks)} code block(s) saved to loop_output/")

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
            if score > _last_best_score:
                _last_best_score = score
                _consec_fails = 0
            else:
                _consec_fails += 1
            if _consec_fails >= 3 and _add_stuck is not None:
                _add_stuck(
                    goal=goal,
                    reason=f"No score improvement after {_consec_fails} attempts (stuck at {score}/10)",
                    attempts=iterations,
                    last_error=prev_feedback,
                )
                print(f"[STUCK] Goal added to stuck_inbox after {_consec_fails} non-improving iterations")
                stop_reason = "stuck_inbox"
                break
        else:
            prev_feedback  = ""
            _consec_fails  = 0
            _last_best_score = score
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

        # ── Post-iteration watchdog check ─────────────────────────────────────
        if _WATCHDOG_OK and _watchdog_check is not None:
            _wd_danger, _wd_reason = _watchdog_check(
                iterations, guard.running_cost, _provider_fail_streak)
            if _wd_danger:
                stop_reason = _wd_reason
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

    # Feature 3 — log cost_cap_hit to stuck_inbox
    if stop_reason.startswith("cost_guard") and _add_stuck is not None:
        _add_stuck(
            goal=goal,
            reason="COST_CAP_HIT",
            attempts=iterations,
            last_error=f"Cost cap reached: £{total_cost:.5f}. Stop reason: {stop_reason}",
        )
        print("[STUCK] COST_CAP_HIT logged to stuck_inbox")

    _write_report(goal, iterations, best_attempt, total_cost, stop_reason)

    print(f"\n[LOOP] Done.")
    print(f"[LOOP] Stop reason : {stop_reason}")
    print(f"[LOOP] Iterations  : {iterations}")
    print(f"[LOOP] Total cost  : £{total_cost:.6f}")
    print(f"[LOOP] Report      : {HERE / 'morning_report.md'}")
    # Update session_state: AAFL run complete
    _best_score = best_attempt.get("quality_score", "") if best_attempt else ""
    _lm_update_ss({
        "last_result": {
            "task": goal[:120], "status": stop_reason,
            "mot_score": str(_best_score), "files_changed": [],
            "completed_at": datetime.datetime.now().isoformat(timespec="seconds"),
        },
        "current_task": {"type": "", "description": "", "subsystem": "",
                         "status": "idle", "started_at": ""},
        "aafl_score": _best_score if isinstance(_best_score, (int, float)) else None,
    })

    if _WATCHDOG_OK and _watchdog_run_cycle is not None:
        try:
            print("[LOOP] Triggering post-run watchdog WCCS cycle (background)...")
            threading.Thread(target=_watchdog_run_cycle, daemon=True, name="WatchdogPostRun").start()
        except Exception as _we:
            print(f"[LOOP] Watchdog trigger failed (non-fatal): {_we}")

    _notify_done(stop_reason, iterations, total_cost)


def run_llow_workflow(workflow_json: dict) -> list[dict]:
    """
    Execute a LLOW workflow JSON.
    Iterates steps in order defined by arrows, respects branch/gate/stop logic.
    Logs each step result. Returns execution log.
    """
    import json as _json
    steps  = workflow_json.get("steps", [])
    arrows = workflow_json.get("arrows", [])
    name   = workflow_json.get("name", "LLOW Workflow")
    log    = []

    def _log(msg, status="info"):
        entry = {
            "step": msg,
            "status": status,
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        log.append(entry)
        print(f"[LLOW] [{status.upper()}] {msg}", flush=True)

    _log(f"Starting LLOW workflow: {name}", "info")

    if not steps:
        _log("No steps in workflow", "fail")
        return log

    # Build adjacency map
    out_arrows: dict = {}
    for a in arrows:
        out_arrows.setdefault(a["from"], []).append(a)

    step_map = {s["id"]: s for s in steps}
    current_id = steps[0]["id"]
    visited_count: dict = {}
    MAX_VISITS = 10  # guard against infinite loops

    while current_id:
        step = step_map.get(current_id)
        if not step:
            _log(f"Step not found: {current_id}", "fail")
            break

        visits = visited_count.get(current_id, 0)
        if visits >= MAX_VISITS:
            _log(f"Max visits ({MAX_VISITS}) reached at step {current_id} — stopping", "fail")
            break
        visited_count[current_id] = visits + 1

        el_id = step.get("element_id", "?")
        _log(f"Executing: {el_id}", "running")

        # ── Handler dispatch ────────────────────────────────────────────────
        next_id = None
        should_stop = False

        if el_id == "AAFL_RUN":
            try:
                _log("Launching AAFL loop (1 iteration)", "info")
                run_loop(max_loop_iters=1, max_llm_calls=20)
                _log("AAFL run complete", "pass")
            except Exception as exc:
                _log(f"AAFL run error: {exc}", "fail")

        elif el_id in ("WCCS_END", "SESUM_END", "HARD_STOP", "CNP"):
            _log(f"Ending step reached: {el_id}", "pass")
            should_stop = True

        elif el_id == "ALP_GATE":
            params = step.get("params", {})
            min_pct = params.get("min_pct", 20)
            _log(f"ALP Gate: min {min_pct}% — check ALP_Database.md", "info")
            # Non-blocking: just log and continue
            _log("ALP Gate passed (automated run — assuming ALP sufficient)", "pass")

        elif el_id == "SCORE_GATE":
            params = step.get("params", {})
            threshold = params.get("threshold", 7)
            _log(f"Score Gate (threshold {threshold}) — auto-continue", "pass")

        elif el_id in ("YO", "PAUSE"):
            _log(f"Pause gate ({el_id}) — skipping in automated run", "info")

        else:
            _log(f"Step {el_id}: no automation handler — marking pass", "pass")

        if should_stop:
            break

        # ── Arrow resolution ────────────────────────────────────────────────
        out = out_arrows.get(current_id, [])
        if not out:
            _log("No outgoing arrows — workflow complete", "pass")
            break

        # Pick the first non-loop arrow for automated execution
        chosen = None
        for a in out:
            atype = a.get("arrow_type", "continue")
            if atype == "hard_stop":
                _log("Hard stop arrow — ending", "pass")
                should_stop = True
                break
            elif atype == "alp_gate":
                min_pct = a.get("params", {}).get("min_pct", 20)
                _log(f"ALP gate arrow ({min_pct}%) — continuing", "info")
                chosen = a
                break
            elif atype in ("continue", "approval", "trigger", "checkpoint"):
                chosen = a
                break
            elif atype == "branch":
                # In automated mode take the first branch
                chosen = a
                break
            elif atype in ("loop_back", "repeat", "jump_back", "jump_forward"):
                chosen = a
                break
            elif atype in ("timer", "scheduled"):
                secs = a.get("params", {}).get("seconds", 5)
                import time as _time
                _log(f"Timer: waiting {min(secs, 30)}s", "info")
                _time.sleep(min(secs, 30))
                chosen = a
                break
            else:
                chosen = a
                break

        if should_stop:
            break

        if chosen:
            atype = chosen.get("arrow_type", "continue")
            if atype == "loop_back":
                next_id = steps[0]["id"]
                _log(f"Loop back to start: {next_id}", "info")
            elif atype == "jump_back":
                n = chosen.get("params", {}).get("n", 1)
                step_list = list(step_map.keys())
                curr_idx = step_list.index(current_id) if current_id in step_list else 0
                next_idx = max(0, curr_idx - int(n))
                next_id = step_list[next_idx]
                _log(f"Jump back {n} to: {next_id}", "info")
            elif atype == "jump_forward":
                n = chosen.get("params", {}).get("n", 1)
                step_list = list(step_map.keys())
                curr_idx = step_list.index(current_id) if current_id in step_list else 0
                next_idx = min(len(step_list) - 1, curr_idx + int(n))
                next_id = step_list[next_idx]
                _log(f"Jump forward {n} to: {next_id}", "info")
            else:
                next_id = chosen.get("to")
        else:
            _log("No applicable arrow — workflow complete", "pass")
            break

        current_id = next_id

    _log(f"LLOW workflow '{name}' finished. Steps executed: {sum(visited_count.values())}", "pass")

    # Write execution log
    log_path = HERE / "data" / "llow_last_run.json"
    try:
        log_path.write_text(
            __import__("json").dumps({"workflow": name, "log": log}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception:
        pass

    return log


if __name__ == "__main__":
    _once = "--once" in sys.argv
    _goal_idx = next((i for i, a in enumerate(sys.argv) if a == "--goal"), None)
    if _goal_idx is not None and _goal_idx + 1 < len(sys.argv):
        _inline_goal = sys.argv[_goal_idx + 1]
        (HERE / "goal.txt").write_text(_inline_goal, encoding="utf-8")
        print(f"[LOOP] Set goal from --goal flag: {_inline_goal}")
    if _once:
        run_loop(max_loop_iters=1, max_llm_calls=10)
    else:
        run_loop()
