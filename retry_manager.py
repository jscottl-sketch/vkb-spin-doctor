"""
retry_manager.py — Feature 4: Auto-Retry on Failure
Decides whether to retry a goal, picks next provider, logs retries.
Standalone: python retry_manager.py test
"""
import json
import sys
from datetime import datetime
from pathlib import Path

HERE          = Path(__file__).parent
AAFL_CFG      = HERE / "aafl_config.json"
HEALTH_DIR    = HERE / "health_results"
LATEST_HEALTH = HEALTH_DIR / "latest_health.json"
RETRY_LOG     = HEALTH_DIR / "retry_log.json"


def _load_aafl_config() -> dict:
    if AAFL_CFG.exists():
        try:
            return json.loads(AAFL_CFG.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"confidence_threshold": 7.0, "max_retries": 3, "retry_on_score_below": 6.0}


def _load_health() -> list:
    if LATEST_HEALTH.exists():
        try:
            data = json.loads(LATEST_HEALTH.read_text(encoding="utf-8"))
            return data.get("providers", [])
        except Exception:
            pass
    return []


def should_retry(score: float, attempts: int, max_attempts: int = None) -> bool:
    """Return True if the goal should be retried based on score and attempt count."""
    cfg = _load_aafl_config()
    threshold = cfg.get("retry_on_score_below", 6.0)
    max_tries  = max_attempts if max_attempts is not None else cfg.get("max_retries", 3)
    return score < threshold and attempts < max_tries


def get_next_provider(failed_providers: list, health_data: list = None) -> str | None:
    """Return next GREEN provider not already in failed list."""
    if health_data is None:
        health_data = _load_health()
    green = [
        p["id"] for p in health_data
        if p.get("status") in ("GREEN", "YELLOW")
        and p.get("id") not in failed_providers
    ]
    if green:
        # Prefer GREEN over YELLOW — health data is already sorted by score
        for p in health_data:
            if p.get("id") in green and p.get("status") == "GREEN":
                return p["id"]
        return green[0]
    return None


def log_retry(goal: str, attempt_number: int, failed_provider: str,
              next_provider: str, reason: str) -> None:
    """Append a retry event to retry_log.json."""
    HEALTH_DIR.mkdir(exist_ok=True)
    entries = []
    if RETRY_LOG.exists():
        try:
            entries = json.loads(RETRY_LOG.read_text(encoding="utf-8"))
        except Exception:
            entries = []
    entries.append({
        "goal":            goal[:80],
        "attempt":         attempt_number,
        "failed_provider": failed_provider,
        "next_provider":   next_provider,
        "reason":          reason,
        "timestamp":       datetime.now().isoformat(),
        "final_score":     None,
        "outcome":         "pending",
    })
    # Keep last 200 entries
    entries = entries[-200:]
    RETRY_LOG.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def update_retry_outcome(goal: str, attempt_number: int, final_score: float,
                          outcome: str) -> None:
    """Update the latest matching retry entry with final score and outcome."""
    if not RETRY_LOG.exists():
        return
    try:
        entries = json.loads(RETRY_LOG.read_text(encoding="utf-8"))
        for entry in reversed(entries):
            if entry["goal"] == goal[:80] and entry["attempt"] == attempt_number:
                entry["final_score"] = final_score
                entry["outcome"]     = outcome
                break
        RETRY_LOG.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


if __name__ == "__main__":
    print("retry_manager.py — self-test")
    print("=" * 50)
    cfg = _load_aafl_config()
    print(f"Config: threshold={cfg.get('retry_on_score_below')} max_retries={cfg.get('max_retries')}")
    print()
    cases = [(5.0, 0), (5.0, 3), (8.0, 0), (6.5, 1)]
    for score, attempt in cases:
        result = should_retry(score, attempt)
        print(f"  should_retry(score={score}, attempts={attempt}) -> {result}")
    print()
    print("Writing mock retry log entry...")
    log_retry("test goal", 1, "gemini", "mistral", "score below threshold")
    log_retry("test goal", 2, "mistral", "cerebras", "empty response")
    entries = json.loads(RETRY_LOG.read_text(encoding="utf-8")) if RETRY_LOG.exists() else []
    print(f"  retry_log.json has {len(entries)} entries")
    print("=" * 50)
    print("PASS")
