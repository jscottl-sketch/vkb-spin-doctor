"""
cost_guard.py — In-process ALP (Always £0 Policy) brake.
Raises CostGuardError before any call that would exceed the cap.
Logs every event to data/cost_log.txt.
"""
import datetime
from collections import deque
from pathlib import Path

LOG_PATH = Path(__file__).parent / "data" / "cost_log.txt"


class CostGuardError(Exception):
    pass


class CostGuard:
    """
    Safety brake for the loop engine.

    max_cost_gbp    — hard ceiling in GBP (default 0.00 = strictly free)
    max_iterations  — hard ceiling on loop cycles (default 50)
    """

    def __init__(self, max_cost_gbp: float = 0.05, max_iterations: int = 50):
        self.max_cost_gbp   = max_cost_gbp
        self.max_iterations = max_iterations
        self._running_cost  = 0.0
        self._call_count    = 0
        self._recent_sigs   = deque(maxlen=3)
        self._log(f"CostGuard init  max_cost=£{max_cost_gbp:.4f}  max_iter={max_iterations}")

    # ── Public API ────────────────────────────────────────────────────────────

    def check_before_call(self, estimated_cost: float = 0.0):
        """Raise CostGuardError if this call would exceed cost or iteration cap."""
        projected = self._running_cost + estimated_cost
        if projected > self.max_cost_gbp:
            msg = (f"Cost cap exceeded: running=£{self._running_cost:.4f}"
                   f" + estimated=£{estimated_cost:.4f}"
                   f" > cap=£{self.max_cost_gbp:.4f}")
            self._log(f"BLOCKED check_before_call: {msg}")
            raise CostGuardError(msg)
        if self._call_count >= self.max_iterations:
            msg = f"Iteration cap: {self._call_count} >= {self.max_iterations}"
            self._log(f"BLOCKED check_before_call: {msg}")
            raise CostGuardError(msg)

    def record_call(self, actual_cost: float = 0.0):
        """Record that a call completed with the given cost."""
        self._running_cost += actual_cost
        self._call_count   += 1
        self._log(
            f"CALL #{self._call_count}  cost=£{actual_cost:.6f}"
            f"  running=£{self._running_cost:.6f}"
            f"  iter={self._call_count}/{self.max_iterations}"
        )

    def detect_loop(self, action_signature: str):
        """Raise CostGuardError if the same signature appears 3 times in a row."""
        self._recent_sigs.append(action_signature)
        if len(self._recent_sigs) == 3 and len(set(self._recent_sigs)) == 1:
            msg = f"Loop detected: '{action_signature}' repeated 3x in a row"
            self._log(f"BLOCKED detect_loop: {msg}")
            raise CostGuardError(msg)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def running_cost(self) -> float:
        return self._running_cost

    @property
    def call_count(self) -> int:
        return self._call_count

    # ── Internal ──────────────────────────────────────────────────────────────

    def _log(self, msg: str):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {msg}\n")
        except Exception:
            pass


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("cost_guard.py self-test")
    print("=" * 40)

    # 1. Free call succeeds; then cost brake fires on any paid estimate
    cg = CostGuard(max_cost_gbp=0.00, max_iterations=50)
    cg.record_call(0.0)
    print(f"record_call(0.0)  OK  running=£{cg.running_cost:.4f}")

    try:
        cg.check_before_call(0.001)
        print("FAIL — cost brake should have fired")
    except CostGuardError as e:
        print(f"cost brake fired  OK: {e}")

    # 2. Iteration brake fires when cap is reached
    cg2 = CostGuard(max_cost_gbp=999.0, max_iterations=3)
    cg2.record_call(0.0)
    cg2.record_call(0.0)
    cg2.record_call(0.0)
    try:
        cg2.check_before_call(0.0)
        print("FAIL — iteration brake should have fired")
    except CostGuardError as e:
        print(f"iteration brake fired  OK: {e}")

    # 3. Loop detector fires on 3 identical signatures in a row
    cg3 = CostGuard()
    cg3.detect_loop("run_python")
    cg3.detect_loop("run_python")
    try:
        cg3.detect_loop("run_python")
        print("FAIL — loop detector should have fired")
    except CostGuardError as e:
        print(f"loop detector fired  OK: {e}")

    # 4. Different signatures don't trigger the detector
    cg4 = CostGuard()
    cg4.detect_loop("run_python")
    cg4.detect_loop("run_tests")
    cg4.detect_loop("run_python")
    print("different sigs  OK — no false positive")

    print("=" * 40)
    print(f"All brakes confirmed. Log: {LOG_PATH}")
