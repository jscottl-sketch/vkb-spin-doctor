"""
error_logger.py — FFUEM (Fluid Flexible Upgradeable Editable Modular) drop-in error logger.
Writes to data/errors_db.json. File-locked, atomic writes, rotation at 1000 entries.
No external dependencies.
"""
import datetime
import json
import os
import threading
import traceback as _tb
from pathlib import Path

HERE = Path(__file__).parent
_DB_FILE    = HERE / "data" / "errors_db.json"
_ARCH_DIR   = HERE / "data" / "errors_archive"
_DB_MAX     = 1000
_LOCK       = threading.Lock()


def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _month() -> str:
    return datetime.datetime.now().strftime("%Y-%m")


def _load() -> list:
    try:
        if _DB_FILE.exists():
            raw = _DB_FILE.read_text(encoding="utf-8")
            data = json.loads(raw)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def _save(entries: list) -> None:
    _DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = _DB_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(_DB_FILE)


def _rotate_if_needed(entries: list) -> list:
    if len(entries) <= _DB_MAX:
        return entries
    overflow = entries[: len(entries) - _DB_MAX]
    keep     = entries[len(entries) - _DB_MAX :]
    _ARCH_DIR.mkdir(parents=True, exist_ok=True)
    arch_file = _ARCH_DIR / f"{_month()}.json"
    existing: list = []
    if arch_file.exists():
        try:
            existing = json.loads(arch_file.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    tmp = arch_file.with_suffix(".tmp")
    tmp.write_text(json.dumps(existing + overflow, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(arch_file)
    return keep


def log_error(component: str, severity: str, message: str, traceback_str: str = None) -> None:
    """Append an error entry to errors_db.json."""
    entry = {
        "ts":        _now(),
        "type":      "error",
        "component": component,
        "severity":  severity,
        "message":   message,
    }
    if traceback_str:
        entry["traceback"] = traceback_str[:2000]
    with _LOCK:
        entries = _load()
        entries.append(entry)
        entries = _rotate_if_needed(entries)
        _save(entries)


def log_event(component: str, message: str) -> None:
    """Append an info/event entry to errors_db.json."""
    entry = {
        "ts":        _now(),
        "type":      "event",
        "component": component,
        "severity":  "INFO",
        "message":   message,
    }
    with _LOCK:
        entries = _load()
        entries.append(entry)
        entries = _rotate_if_needed(entries)
        _save(entries)


def get_recent_errors(n: int = 50, component: str = None) -> list:
    """Return last N entries, optionally filtered by component."""
    with _LOCK:
        entries = _load()
    if component:
        entries = [e for e in entries if e.get("component") == component]
    return list(reversed(entries))[:n]


def get_errors_by_component(component: str) -> list:
    return get_recent_errors(n=1000, component=component)


def clear_old_entries(keep_last_n: int = 1000) -> int:
    """Trim to keep_last_n most recent entries. Returns number removed."""
    with _LOCK:
        entries = _load()
        removed = max(0, len(entries) - keep_last_n)
        if removed > 0:
            entries = entries[-keep_last_n:]
            _save(entries)
    return removed
