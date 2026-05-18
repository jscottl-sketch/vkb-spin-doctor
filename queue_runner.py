"""queue_runner.py — reads goal_queue.txt and runs loop_manager.py --once per goal."""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE  = Path(__file__).parent
QUEUE = HERE / "goal_queue.txt"


def main():
    if not QUEUE.exists():
        print("[QUEUE] goal_queue.txt not found. Create it with one goal per line.")
        sys.exit(1)

    goals = [
        line.strip()
        for line in QUEUE.read_text("utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

    if not goals:
        print("[QUEUE] No goals found in goal_queue.txt (all lines blank or commented).")
        sys.exit(0)

    log_dir  = HERE / "loop_output"
    log_dir.mkdir(exist_ok=True)
    stamp    = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_path = log_dir / f"queue_log_{stamp}.txt"

    print("=" * 60)
    print(f"  AAFL Goal Queue Runner — {len(goals)} goal(s)")
    print("=" * 60)

    passed = failed = 0
    for i, goal in enumerate(goals, 1):
        print(f"\n[QUEUE] === Goal {i}/{len(goals)} ===")
        print(f"[QUEUE] {goal}")
        (HERE / "goal.txt").write_text(goal, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(HERE / "loop_manager.py"), "--once"]
        )
        status = "PASS" if result.returncode == 0 else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1
        print(f"[QUEUE] Result: {status}")
        with open(log_path, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%H:%M:%S")
            f.write(f"[{ts}] {status}: {goal}\n")

    print(f"\n[QUEUE] Done. {passed} passed, {failed} failed.")
    print(f"[QUEUE] Log: {log_path}")


if __name__ == "__main__":
    main()
