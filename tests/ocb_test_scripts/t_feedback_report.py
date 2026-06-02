"""t_feedback_report — Feedback loop learning report test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from learning_machine.feedback_loop import get_report, get_failures
    report = get_report()
    failures = get_failures(10)
    if report:
        print(f"[t_feedback_report] PASS — report exists")
        print(f"  Total runs    : {report.get('total_runs', 0)}")
        print(f"  Avg score     : {report.get('avg_score', 0)}")
        print(f"  Best provider : {report.get('best_provider_by_score', 'unknown')}")
        print(f"  Common fail   : {report.get('most_common_failure', 'none')}")
        print(f"  Failure log   : {len(failures)} entries")
    else:
        print("[t_feedback_report] PASS — no runs recorded yet (report will appear after first AAFL run)")
    sys.exit(0)
except Exception as exc:
    print(f"[t_feedback_report] FAIL — {exc}")
    sys.exit(1)
