"""Tiny helper: read aafl_config.json without circular imports."""
import json
from pathlib import Path

_CFG = Path(__file__).parent / "aafl_config.json"


def _load():
    if _CFG.exists():
        try:
            return json.loads(_CFG.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def get_confidence_threshold() -> float:
    return float(_load().get("confidence_threshold", 7.0))


def get_cost_cap_usd() -> float:
    return float(_load().get("cost_cap_per_goal_usd", 0.05))


def get_max_retries() -> int:
    return int(_load().get("max_retries", 3))


def get_retry_threshold() -> float:
    return float(_load().get("retry_on_score_below", 6.0))
