"""
source_library_manager.py — Feature 8: Source Discovery Mode
Manages sources_library.json — discovered URLs, domains, tags, usage tracking.
Standalone: python source_library_manager.py list
"""
import json
import sys
from datetime import datetime
from pathlib import Path

HERE     = Path(__file__).parent
SOURCES  = HERE / "sources_library.json"


def _load() -> list:
    if SOURCES.exists():
        try:
            return json.loads(SOURCES.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _save(items: list):
    SOURCES.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def add_source(url: str, domain: str, description: str, tags: list) -> bool:
    """Append a new source. Deduplicates by URL. Returns True if added."""
    items = _load()
    for item in items:
        if item.get("url") == url:
            return False  # already exists
    items.append({
        "url":             url,
        "domain":          domain,
        "description":     description,
        "topic_tags":      tags if isinstance(tags, list) else [tags],
        "date_found":      datetime.now().strftime("%Y-%m-%d"),
        "times_referenced": 0,
    })
    _save(items)
    return True


def get_sources(topic_filter: str = None) -> list:
    """Return all sources, optionally filtered by topic tag."""
    items = _load()
    if not topic_filter:
        return items
    tf = topic_filter.lower()
    return [i for i in items if any(tf in t.lower() for t in i.get("topic_tags", []))]


def mark_used(url: str) -> None:
    """Increment times_referenced for a source URL."""
    items = _load()
    for item in items:
        if item.get("url") == url:
            item["times_referenced"] = item.get("times_referenced", 0) + 1
            break
    _save(items)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        items = get_sources()
        print(f"Sources library — {len(items)} entries")
        for item in items:
            print(f"  {item['domain']:<30} {item['description'][:50]}")
    elif cmd == "add" and len(sys.argv) >= 4:
        ok = add_source(sys.argv[2], sys.argv[3], "Manual add", [])
        print("Added" if ok else "Already exists")
