"""
feedback_loop.py — Self-Improving Feedback Loop.
Called after every AAFL run. Routes results to RAG + training data.
Tracks failure patterns and emits a learning report every 10 runs.
"""
import json
import datetime
from pathlib import Path

HERE = Path(__file__).parent.parent
FAILURE_PATTERNS_FILE = HERE / "data" / "failure_patterns.jsonl"
FEEDBACK_COUNTER_FILE = HERE / "data" / "feedback_counter.json"
LEARNING_REPORT_FILE  = HERE / "data" / "learning_report.json"

HIGH_SCORE = 7.0
LOW_SCORE  = 4.0
REPORT_EVERY = 10


def _load_counter() -> dict:
    if FEEDBACK_COUNTER_FILE.exists():
        try:
            return json.loads(FEEDBACK_COUNTER_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"total_runs": 0, "high_count": 0, "low_count": 0, "score_sum": 0.0,
            "provider_scores": {}, "failure_types": {}}


def _save_counter(counter: dict):
    FEEDBACK_COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_COUNTER_FILE.write_text(json.dumps(counter, indent=2), encoding="utf-8")


def _log_failure(goal: str, error: str, provider: str):
    entry = {
        "goal": goal[:200],
        "error": error[:300],
        "provider": provider,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    FAILURE_PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with FAILURE_PATTERNS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _generate_report(counter: dict) -> dict:
    total = counter["total_runs"]
    avg_score = round(counter["score_sum"] / total, 2) if total else 0.0

    provider_scores = counter.get("provider_scores", {})
    best_provider = max(provider_scores, key=lambda k: provider_scores[k].get("avg", 0)) \
        if provider_scores else "unknown"

    failure_types = counter.get("failure_types", {})
    most_common_failure = max(failure_types, key=failure_types.get) \
        if failure_types else "none"

    report = {
        "total_runs": total,
        "high_quality_runs": counter["high_count"],
        "low_quality_runs": counter["low_count"],
        "avg_score": avg_score,
        "best_provider_by_score": best_provider,
        "most_common_failure": most_common_failure,
        "failure_counts": failure_types,
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    LEARNING_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    LEARNING_REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def get_report() -> dict:
    """Return latest cached learning report."""
    if LEARNING_REPORT_FILE.exists():
        try:
            return json.loads(LEARNING_REPORT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def get_failures(limit: int = 50) -> list:
    """Return last N failure pattern entries."""
    if not FAILURE_PATTERNS_FILE.exists():
        return []
    try:
        lines = FAILURE_PATTERNS_FILE.read_text(encoding="utf-8").strip().splitlines()
        entries = []
        for line in lines:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
        return entries[-limit:]
    except Exception:
        return []


def update_rag_live():
    """Index the latest session log and any new result files into RAG."""
    try:
        from learning_machine.rag_engine import index_file
        session_dir = HERE / "session_logs"
        if session_dir.exists():
            logs = sorted(session_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
            if logs:
                index_file(logs[0])
    except Exception as exc:
        print(f"[FEEDBACK] update_rag_live error: {exc}")


def after_run(goal: str, result: dict, score: float, provider: str = "unknown"):
    """
    Called after every AAFL loop run.
    result dict should contain at least: goal, plan, work/output, score.
    """
    counter = _load_counter()
    counter["total_runs"] = counter.get("total_runs", 0) + 1
    counter["score_sum"]  = counter.get("score_sum", 0.0) + score

    # Track provider scores
    ps = counter.setdefault("provider_scores", {})
    if provider not in ps:
        ps[provider] = {"sum": 0.0, "count": 0, "avg": 0.0}
    ps[provider]["sum"] += score
    ps[provider]["count"] += 1
    ps[provider]["avg"] = round(ps[provider]["sum"] / ps[provider]["count"], 2)

    if score >= HIGH_SCORE:
        counter["high_count"] = counter.get("high_count", 0) + 1
        # Add to training data
        try:
            from learning_machine.training_prep import scan_results
            scan_results()
        except Exception as exc:
            print(f"[FEEDBACK] training_prep error: {exc}")
        # Add to RAG
        update_rag_live()

    elif score < LOW_SCORE:
        counter["low_count"] = counter.get("low_count", 0) + 1
        error = result.get("error") or result.get("failure_reason") or f"score={score}"
        _log_failure(goal, str(error), provider)
        # Track failure type
        error_key = str(error)[:60].lower().replace(" ", "_")
        ft = counter.setdefault("failure_types", {})
        ft[error_key] = ft.get(error_key, 0) + 1

    _save_counter(counter)

    # Every 10 runs — print learning report
    if counter["total_runs"] % REPORT_EVERY == 0:
        report = _generate_report(counter)
        print(f"\n[FEEDBACK] === Learning Report (run #{counter['total_runs']}) ===")
        print(f"[FEEDBACK] Avg score trend  : {report['avg_score']}/10")
        print(f"[FEEDBACK] High quality runs: {report['high_quality_runs']}/{report['total_runs']}")
        print(f"[FEEDBACK] Most common fail : {report['most_common_failure']}")
        print(f"[FEEDBACK] Best provider    : {report['best_provider_by_score']}")
        print(f"[FEEDBACK] ===")
    else:
        _generate_report(counter)


if __name__ == "__main__":
    report = get_report()
    if report:
        print(f"[FEEDBACK] Total runs       : {report.get('total_runs', 0)}")
        print(f"[FEEDBACK] Avg score        : {report.get('avg_score', 0)}")
        print(f"[FEEDBACK] Best provider    : {report.get('best_provider_by_score', 'unknown')}")
        print(f"[FEEDBACK] Most common fail : {report.get('most_common_failure', 'none')}")
    else:
        print("[FEEDBACK] No report yet — no runs recorded.")
