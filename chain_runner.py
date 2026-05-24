"""
chain_runner.py — Feature 6: Chain Mode (Scout -> AAFL -> Verify)
Orchestrates full pipeline: scout -> enrich goal -> loop_manager -> evaluate -> retry.
Standalone: python chain_runner.py "test goal"
"""
import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

HERE       = Path(__file__).parent
HEALTH_DIR = HERE / "health_results"
CHAIN_LOG  = HEALTH_DIR / "chain_log.json"

_chain_status_lock = threading.Lock()
_chain_status: dict = {"state": "idle", "chain_id": None, "goal": "", "step": ""}


def get_chain_status() -> dict:
    with _chain_status_lock:
        s = dict(_chain_status)
        s["running"] = s.get("state") == "running"
        s["last_goal"] = s.get("goal", "")
        return s


def _set_status(state: str, step: str = "", goal: str = "", chain_id: str = ""):
    with _chain_status_lock:
        _chain_status["state"]    = state
        _chain_status["step"]     = step
        _chain_status["goal"]     = goal
        if chain_id:
            _chain_status["chain_id"] = chain_id


def _load_chain_log() -> list:
    if CHAIN_LOG.exists():
        try:
            return json.loads(CHAIN_LOG.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _save_chain_log(entries: list):
    HEALTH_DIR.mkdir(exist_ok=True)
    CHAIN_LOG.write_text(json.dumps(entries[-20:], indent=2, ensure_ascii=False), encoding="utf-8")


def run_chain(goal_text: str, provider: str = None) -> dict:
    """
    Full pipeline: Scout -> enrich goal -> AAFL loop -> evaluate -> retry if needed.
    Returns chain_result dict.
    """
    chain_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    t_start  = time.time()

    _set_status("running", "scout", goal_text, chain_id)

    # ── Step 1: Scout ─────────────────────────────────────────────────────────
    scout_results = []
    scout_briefing = ""
    try:
        from chief_scout import chief_scout
        scout_data    = chief_scout(goal_text)
        scout_results = scout_data.get("results", [])
        scout_briefing = scout_data.get("briefing", "")
        print(f"[CHAIN] Step 1 — Scout done: {len(scout_results)} sources")
    except Exception as exc:
        print(f"[CHAIN] Step 1 — Scout failed ({exc}), continuing without web context")

    # ── Step 2: Enrich goal ────────────────────────────────────────────────────
    _set_status("running", "aafl", goal_text, chain_id)
    enriched_goal = goal_text
    if scout_briefing:
        enriched_goal = f"Research findings:\n{scout_briefing}\n\nGoal: {goal_text}"

    # Write enriched goal to goal.txt so loop_manager picks it up
    goal_txt = HERE / "goal.txt"
    try:
        goal_txt.write_text(enriched_goal, encoding="utf-8")
    except Exception:
        pass

    # ── Step 3: Run AAFL loop ──────────────────────────────────────────────────
    import subprocess
    loop_score  = 0.0
    loop_output = ""
    provider_used = provider or "auto"
    loop_ok     = False
    try:
        py = sys.executable
        result = subprocess.run(
            [py, str(HERE / "loop_manager.py"), "--once"],
            capture_output=True, text=True, timeout=180, cwd=str(HERE),
        )
        loop_output = (result.stdout + result.stderr).strip()
        loop_ok     = result.returncode == 0

        # Extract score from output
        for line in reversed(loop_output.splitlines()):
            if "score" in line.lower():
                import re
                m = re.search(r"(\d+\.\d+)", line)
                if m:
                    loop_score = float(m.group(1))
                    break
        print(f"[CHAIN] Step 3 — AAFL done: score={loop_score}")
    except subprocess.TimeoutExpired:
        loop_output = "TIMEOUT after 180s"
        print("[CHAIN] Step 3 — AAFL timed out")
    except Exception as exc:
        loop_output = str(exc)
        print(f"[CHAIN] Step 3 — AAFL error: {exc}")

    # ── Step 4: Evaluate ───────────────────────────────────────────────────────
    _set_status("running", "verify", goal_text, chain_id)
    from evaluator import evaluate
    scores = evaluate(loop_output[:2000], goal_text)
    final_score = scores.get("overall", loop_score)

    # ── Step 5: Retry if needed ────────────────────────────────────────────────
    retried = False
    try:
        from retry_manager import should_retry, get_next_provider, log_retry
        from aafl_config_reader import get_max_retries
        max_r = get_max_retries()
    except Exception:
        max_r = 3

    if should_retry(final_score, 1, max_r):
        _set_status("running", "retry", goal_text, chain_id)
        next_prov = get_next_provider([provider_used] if provider_used != "auto" else [])
        if next_prov:
            log_retry(goal_text, 1, provider_used, next_prov, f"score {final_score} below threshold")
            retried = True
            print(f"[CHAIN] Step 5 — Retrying with {next_prov}")

    # ── Step 6: Log result ─────────────────────────────────────────────────────
    elapsed  = round(time.time() - t_start, 1)
    chain_result = {
        "chain_id":      chain_id,
        "goal":          goal_text[:80],
        "provider":      provider_used,
        "scout_sources": len(scout_results),
        "final_score":   final_score,
        "retried":       retried,
        "total_time_s":  elapsed,
        "total_cost_usd": 0.0,
        "steps":         ["scout", "enrich", "aafl", "evaluate"] + (["retry"] if retried else []),
        "timestamp":     datetime.now().isoformat(),
        "loop_ok":       loop_ok,
    }

    entries = _load_chain_log()
    entries.append(chain_result)
    _save_chain_log(entries)

    _set_status("idle")
    print(f"[CHAIN] Done — score={final_score} time={elapsed}s")
    return chain_result


if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or "test goal"
    print(f"[CHAIN] Starting chain for goal: {goal}")
    print(f"[CHAIN] Status: {get_chain_status()}")
    result = run_chain(goal)
    print(f"[CHAIN] Result: {result}")
