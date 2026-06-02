"""t_training_scan — Training data pipeline test. Scans loop_output and prints pair count."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from learning_machine.training_prep import scan_results
    stats = scan_results()
    print(f"[t_training_scan] PASS — {stats['pair_count']} pairs from {stats['total_runs']} runs "
          f"(avg score {stats['avg_score']})")
    sys.exit(0)
except Exception as exc:
    print(f"[t_training_scan] FAIL — {exc}")
    sys.exit(1)
