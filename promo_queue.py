"""
promo_queue.py — Promotion queue for high-scoring results (score >= 9.0).
Items awaiting manual review before being promoted to a knowledge base or published.
"""
import datetime
import json
import uuid
from pathlib import Path

HERE = Path(__file__).parent
PROMO_FILE = HERE / "promo_queue.json"


def _load() -> list:
    if PROMO_FILE.exists():
        try:
            return json.loads(PROMO_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(items: list):
    PROMO_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def add_to_promo(content: str, source: str, reason: str) -> str:
    """Add an item to the promotion queue. Returns item_id."""
    items = _load()
    item_id = str(uuid.uuid4())[:8]
    items.append({
        "item_id":    item_id,
        "content":    content,
        "source":     source,
        "reason":     reason,
        "status":     "pending",
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": None,
    })
    _save(items)
    return item_id


def get_promo_items() -> list:
    """Return all items with status pending/approved/rejected."""
    return _load()


def get_pending_items() -> list:
    """Return only pending items."""
    return [i for i in _load() if i.get("status") == "pending"]


def update_promo_status(item_id: str, status: str) -> bool:
    """Approve or reject an item. status must be 'approved' or 'rejected'."""
    if status not in ("approved", "rejected"):
        return False
    items = _load()
    found = False
    for item in items:
        if item.get("item_id") == item_id:
            item["status"] = status
            item["updated_at"] = datetime.datetime.now().isoformat()
            found = True
            break
    if found:
        _save(items)
    return found


def pending_count() -> int:
    """Return count of pending promo items."""
    return len(get_pending_items())
