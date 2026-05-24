"""
stuck_inbox.py — Track goals that are stuck in a loop with no progress.
Writes to stuck_inbox.json in the project root.
Integrates with afna_strategies.json to suggest research strategies for each stuck goal.
"""
import datetime
import json
import uuid
from pathlib import Path

HERE = Path(__file__).parent
INBOX_FILE = HERE / "stuck_inbox.json"
STRATEGIES_FILE = HERE / "afna_strategies.json"

# Keyword hints that map goal text to useful strategies
_STRATEGY_HINTS = {
    "reddit":  ["reddit", "forum", "community", "war thunder", "elite dangerous", "star citizen",
                 "dcs", "vkb", "joystick", "hotas", "binds", "keybind", "setup", "config"],
    "github":  ["error", "bug", "fix", "crash", "exception", "code", "script", "python",
                 "install", "dependency", "import", "traceback"],
    "youtube": ["tutorial", "guide", "how to", "setup", "walkthrough", "video", "calibrate",
                 "configure", "install", "show", "demo"],
    "forum":   ["war thunder", "elite dangerous", "star citizen", "dcs", "spectrum", "hoggit",
                 "binds", "profile", "axis", "deadzone", "sensitivity"],
    "ddg":     [],   # always suggested as fallback
}


def _load_strategies() -> list:
    if STRATEGIES_FILE.exists():
        try:
            data = json.loads(STRATEGIES_FILE.read_text(encoding="utf-8"))
            return [s for s in data.get("strategies", []) if not s.get("disabled")]
        except Exception:
            return []
    return []


def suggest_strategies(goal: str) -> list:
    """Return strategy names from afna_strategies.json relevant to the given goal."""
    strategies = _load_strategies()
    if not strategies:
        return []
    goal_lower = goal.lower()
    available  = {s["name"] for s in strategies}
    suggested  = []
    for name, keywords in _STRATEGY_HINTS.items():
        if name not in available:
            continue
        if not keywords or any(k in goal_lower for k in keywords):
            suggested.append(name)
    # ddg is always included as a fallback
    if "ddg" in available and "ddg" not in suggested:
        suggested.append("ddg")
    return suggested


def get_strategies() -> list:
    """Return all enabled strategies from afna_strategies.json."""
    return _load_strategies()


def _load() -> list:
    if INBOX_FILE.exists():
        try:
            return json.loads(INBOX_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(items: list):
    INBOX_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def add_stuck_item(goal: str, reason: str, attempts: int, last_error: str,
                   severity: str = "medium") -> str:
    """Add a stuck goal to the inbox. Returns the new item_id."""
    items = _load()
    item_id    = str(uuid.uuid4())[:8]
    strategies = suggest_strategies(goal)

    # Feature 9 — AFNA suggestion via smart_suggester
    afna_suggestion = None
    try:
        from smart_suggester import suggest_provider
        sug = suggest_provider(goal)
        afna_suggestion = sug.get("suggested_provider")
    except Exception:
        pass

    items.append({
        "item_id":              item_id,
        "goal":                 goal,
        "reason":               reason,
        "attempts":             attempts,
        "last_error":           last_error,
        "status":               "unresolved",
        "severity":             severity if severity in ("low", "medium", "high") else "medium",
        "suggested_strategies": strategies,
        "afna_suggestion":      afna_suggestion,
        "created_at":           datetime.datetime.now().isoformat(),
        "resolved_at":          None,
    })
    _save(items)
    return item_id


def get_stuck_items() -> list:
    """Return all unresolved stuck items."""
    return [i for i in _load() if i.get("status") != "resolved"]


def resolve_stuck_item(item_id: str) -> bool:
    """Mark item as resolved. Returns True if found and updated."""
    items = _load()
    found = False
    for item in items:
        if item.get("item_id") == item_id:
            item["status"] = "resolved"
            item["resolved_at"] = datetime.datetime.now().isoformat()
            found = True
            break
    if found:
        _save(items)
    return found


def get_all_items() -> list:
    """Return all items (resolved and unresolved)."""
    return _load()


def stuck_count() -> int:
    """Return count of unresolved stuck items."""
    return len(get_stuck_items())


# ── Feature 9 additions ───────────────────────────────────────────────────────

def get_stuck_by_severity(severity: str) -> list:
    """Return unresolved items filtered by severity."""
    return [i for i in get_stuck_items() if i.get("severity") == severity]


def bulk_resolve(item_ids: list) -> int:
    """Resolve multiple items by id list. Returns count resolved."""
    items = _load()
    resolved = 0
    now = datetime.datetime.now().isoformat()
    for item in items:
        if item.get("item_id") in item_ids and item.get("status") != "resolved":
            item["status"]      = "resolved"
            item["resolved_at"] = now
            resolved += 1
    _save(items)
    return resolved


def get_stuck_summary() -> dict:
    """Return counts by severity for unresolved items."""
    items = get_stuck_items()
    return {
        "total":  len(items),
        "high":   sum(1 for i in items if i.get("severity") == "high"),
        "medium": sum(1 for i in items if i.get("severity") == "medium"),
        "low":    sum(1 for i in items if i.get("severity") == "low"),
    }


def _auto_escalate():
    """Escalate items unresolved > 24h to severity=high."""
    items = _load()
    now = datetime.datetime.now()
    changed = False
    for item in items:
        if item.get("status") == "resolved":
            continue
        try:
            created = datetime.datetime.fromisoformat(item["created_at"])
            age_h   = (now - created).total_seconds() / 3600
            if age_h > 24 and item.get("severity") != "high":
                item["severity"] = "high"
                changed = True
        except Exception:
            pass
    if changed:
        _save(items)
