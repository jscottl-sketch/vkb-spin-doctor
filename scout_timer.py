"""
scout_timer.py — Feature 7: Timed Scout Runs
Runs chief_scout repeatedly for a set duration or until a result target is met.
Stop flag: scout_timer_stop.flag in project root.
Standalone: python scout_timer.py --hours 1 --goal "Star Citizen joystick setup"
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

HERE       = Path(__file__).parent
HEALTH_DIR = HERE / "health_results"
TIMER_LOG  = HEALTH_DIR / "scout_timer_log.json"
STOP_FLAG  = HERE / "scout_timer_stop.flag"

_running = False
_start_time: datetime | None = None
_runs_done = 0
_results_found = 0


def _check_stop() -> bool:
    """Return True and delete flag if stop flag exists."""
    if STOP_FLAG.exists():
        try:
            STOP_FLAG.unlink()
        except Exception:
            pass
        return True
    return False


def _run_one_scout(goal_text: str) -> int:
    """Run one chief_scout cycle. Returns count of results found."""
    try:
        from chief_scout import chief_scout
        data = chief_scout(goal_text)
        return len(data.get("results", []))
    except Exception as exc:
        print(f"[SCOUT_TIMER] Scout error: {exc}")
        return 0


def _log_run(goal_text: str, runs: int, results: int, reason: str,
             t_start: datetime, t_end: datetime):
    HEALTH_DIR.mkdir(exist_ok=True)
    entries = []
    if TIMER_LOG.exists():
        try:
            entries = json.loads(TIMER_LOG.read_text(encoding="utf-8"))
        except Exception:
            pass
    entries.append({
        "goal":            goal_text[:80],
        "start_time":      t_start.isoformat(),
        "end_time":        t_end.isoformat(),
        "runs_completed":  runs,
        "results_found":   results,
        "reason_stopped":  reason,
    })
    entries = entries[-50:]
    TIMER_LOG.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def run_for_hours(hours: float, goal_text: str, interval_minutes: int = 30) -> dict:
    """Run scout repeatedly for `hours` hours."""
    global _running, _start_time, _runs_done, _results_found
    _running = True
    _start_time = datetime.now()
    _runs_done = 0
    _results_found = 0
    deadline = time.time() + hours * 3600
    reason = "time_expired"

    while time.time() < deadline:
        if _check_stop():
            reason = "stop_flag"
            break
        n = _run_one_scout(goal_text)
        _runs_done += 1
        _results_found += n
        print(f"[SCOUT_TIMER] Run {_runs_done}: {n} results. Total: {_results_found}")
        wait = interval_minutes * 60
        waited = 0
        while waited < wait:
            if _check_stop():
                reason = "stop_flag"
                _running = False
                _log_run(goal_text, _runs_done, _results_found, reason, _start_time, datetime.now())
                return {"runs": _runs_done, "results": _results_found, "reason": reason}
            time.sleep(min(10, wait - waited))
            waited += 10
            if time.time() >= deadline:
                break

    _running = False
    _log_run(goal_text, _runs_done, _results_found, reason, _start_time, datetime.now())
    return {"runs": _runs_done, "results": _results_found, "reason": reason}


def run_indefinitely(goal_text: str, interval_minutes: int = 30) -> dict:
    """Run scout forever until stop flag."""
    global _running, _start_time, _runs_done, _results_found
    _running = True
    _start_time = datetime.now()
    _runs_done = 0
    _results_found = 0
    reason = "stop_flag"

    while True:
        if _check_stop():
            break
        n = _run_one_scout(goal_text)
        _runs_done += 1
        _results_found += n
        print(f"[SCOUT_TIMER] Run {_runs_done}: {n} results. Total: {_results_found}")
        wait = interval_minutes * 60
        waited = 0
        while waited < wait:
            if _check_stop():
                break
            time.sleep(min(10, wait - waited))
            waited += 10

    _running = False
    _log_run(goal_text, _runs_done, _results_found, reason, _start_time, datetime.now())
    return {"runs": _runs_done, "results": _results_found, "reason": reason}


def run_until_results(target_count: int, goal_text: str) -> dict:
    """Run scout until knowledge_bank has target_count entries on topic."""
    global _running, _start_time, _runs_done, _results_found
    _running = True
    _start_time = datetime.now()
    _runs_done = 0
    _results_found = 0
    reason = "target_reached"

    while _results_found < target_count:
        if _check_stop():
            reason = "stop_flag"
            break
        n = _run_one_scout(goal_text)
        _runs_done += 1
        _results_found += n
        print(f"[SCOUT_TIMER] Run {_runs_done}: {n} results. Total: {_results_found}/{target_count}")

    _running = False
    _log_run(goal_text, _runs_done, _results_found, reason, _start_time, datetime.now())
    return {"runs": _runs_done, "results": _results_found, "reason": reason}


def get_status() -> dict:
    return {
        "running":      _running,
        "start_time":   _start_time.isoformat() if _start_time else None,
        "runs_done":    _runs_done,
        "results_found": _results_found,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=float, default=0)
    parser.add_argument("--goal", default="Star Citizen joystick setup")
    parser.add_argument("--interval", type=int, default=30)
    args = parser.parse_args()

    print(f"[SCOUT_TIMER] Import OK")
    print(f"[SCOUT_TIMER] Args: hours={args.hours} goal={args.goal!r} interval={args.interval}")
    print(f"[SCOUT_TIMER] Status: {get_status()}")

    # Write stop flag test
    STOP_FLAG.write_text("stop", encoding="utf-8")
    assert _check_stop(), "Stop flag check failed"
    print("[SCOUT_TIMER] Stop flag mechanism: OK")
    print("PASS")
