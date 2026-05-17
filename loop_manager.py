"""
loop_manager.py — Minimum Viable Loop Engine.
Reads goal from goal.txt, loops plan → work → verify → store → cost check.
Writes morning_report.md when done.
"""
import sys
import datetime
from pathlib import Path

from aafl_core import AAFLCore
from memory_bank import store
from cost_guard import CostGuard, CostGuardError

HERE = Path(__file__).parent


def load_goal() -> str:
    goal_path = HERE / "goal.txt"
    if not goal_path.exists():
        raise FileNotFoundError(
            "goal.txt not found — create it with your goal on the first line"
        )
    return goal_path.read_text(encoding="utf-8").strip()


def _write_report(path: Path, iterations: int, best: dict | None,
                  total_cost: float, stop_reason: str):
    now   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Morning Report — {now}",
        "",
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
    path.write_text("\n".join(lines), encoding="utf-8")


def run_loop(max_loop_iters: int = 50, max_llm_calls: int = 200):
    goal  = load_goal()
    aafl  = AAFLCore(dry_run=False, allow_paid=False)
    guard = CostGuard(max_cost_gbp=0.05, max_iterations=max_llm_calls)

    print(f"[LOOP] Goal: {goal}")
    print(f"[LOOP] Max iterations: {max_loop_iters}")

    iterations   = 0
    best_attempt = None
    stop_reason  = "max_iterations"

    while iterations < max_loop_iters:
        # Hard stop — create a file named STOP in the project folder
        if (HERE / "STOP").exists():
            stop_reason = "STOP file found"
            break

        iterations += 1
        print(f"\n[LOOP] === Iteration {iterations}/{max_loop_iters} ===")

        # ── Plan ──────────────────────────────────────────────────────────────
        try:
            guard.check_before_call(0.0)
        except CostGuardError as e:
            stop_reason = f"cost_guard: {e}"
            break

        print("[LOOP] Planning...")
        plan_result = aafl.run(
            task=f"Plan how to achieve this goal step by step: {goal}",
            task_type="reason",
            max_tokens=512,
        )
        guard.record_call(plan_result.cost_usd)

        if not plan_result.ok:
            print("[LOOP] Plan step: no provider available — skipping")
            continue

        plan_text = plan_result.response

        # ── Loop detection ─────────────────────────────────────────────────────
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
        work_result = aafl.run(
            task=(
                f"Execute this plan to achieve the goal.\n\n"
                f"Goal: {goal}\n\nPlan:\n{plan_text}"
            ),
            task_type="code",
            max_tokens=1024,
        )
        guard.record_call(work_result.cost_usd)

        if not work_result.ok:
            print("[LOOP] Work step: no provider available — skipping")
            continue

        work_text = work_result.response

        # ── Verify ────────────────────────────────────────────────────────────
        goal_met = aafl.verify_returns_nonempty(work_text)
        print(f"[LOOP] Verify: goal_met={goal_met}")

        # ── Store ─────────────────────────────────────────────────────────────
        entry_id = store({
            "title":       f"Loop attempt #{iterations}",
            "content":     work_text,
            "project":     "loop_manager",
            "source_type": "loop_attempt",
            "tags":        ["loop_attempt"],
            "metadata":    {
                "plan":           plan_text,
                "goal_met":       goal_met,
                "iteration":      iterations,
                "plan_provider":  plan_result.provider_id,
                "work_provider":  work_result.provider_id,
            },
        })
        print(f"[LOOP] Stored attempt: {entry_id}")
        out_dir = HERE / "loop_output"; out_dir.mkdir(exist_ok=True)
        (out_dir / f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}_result.txt").write_text(work_text, encoding="utf-8")

        score   = 1.0 if goal_met else 0.0
        attempt = {
            "id":           entry_id,
            "quality_score": score,
            "plan":          plan_text,
            "work":          work_text,
        }
        if best_attempt is None or score > best_attempt.get("quality_score", 0):
            best_attempt = attempt

        if goal_met:
            stop_reason = "goal_met"
            break

        # ── End-of-iteration cost guard ────────────────────────────────────────
        try:
            guard.check_before_call(0.0)
        except CostGuardError as e:
            stop_reason = f"cost_guard: {e}"
            break
    else:
        stop_reason = "max_iterations"

    total_cost  = guard.running_cost
    report_path = HERE / "morning_report.md"
    _write_report(report_path, iterations, best_attempt, total_cost, stop_reason)

    print(f"\n[LOOP] Done.")
    print(f"[LOOP] Stop reason : {stop_reason}")
    print(f"[LOOP] Iterations  : {iterations}")
    print(f"[LOOP] Total cost  : £{total_cost:.6f}")
    print(f"[LOOP] Report      : {report_path}")


if __name__ == "__main__":
    _once = "--once" in sys.argv
    if _once:
        run_loop(max_loop_iters=1, max_llm_calls=10)
    else:
        run_loop()
