"""
module_loader.py — Feature 1: Plugin/Module Architecture
Reads modules/module_registry.json, manages module enable/disable, tab routing.
Standalone: python module_loader.py
"""
import json
import sys
from pathlib import Path

HERE     = Path(__file__).parent
REGISTRY = HERE / "modules" / "module_registry.json"


def _load() -> dict:
    if not REGISTRY.exists():
        return {"modules": []}
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception:
        return {"modules": []}


def _save(data: dict):
    REGISTRY.parent.mkdir(exist_ok=True)
    REGISTRY.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_all_modules() -> list:
    """Return all modules from registry."""
    return _load().get("modules", [])


def get_enabled_modules() -> list:
    """Return only enabled modules."""
    return [m for m in get_all_modules() if m.get("enabled", True)]


def get_modules_for_tab(tab_name: str) -> list:
    """Return enabled modules assigned to the given tab, plus 'all' tab modules."""
    return [m for m in get_enabled_modules()
            if m.get("tab_target") in (tab_name, "all")]


def enable_module(module_id: str) -> bool:
    """Enable a module by id. Returns True if found and updated."""
    data = _load()
    for m in data.get("modules", []):
        if m["id"] == module_id:
            m["enabled"] = True
            _save(data)
            return True
    return False


def disable_module(module_id: str) -> bool:
    """Disable a module by id. Returns True if found and updated."""
    data = _load()
    for m in data.get("modules", []):
        if m["id"] == module_id:
            m["enabled"] = False
            _save(data)
            return True
    return False


def toggle_module(module_id: str, enabled: bool) -> bool:
    """Set module enabled state. Returns True if found."""
    if enabled:
        return enable_module(module_id)
    return disable_module(module_id)


if __name__ == "__main__":
    modules = get_all_modules()
    enabled = get_enabled_modules()
    print(f"Module Registry — {len(modules)} total, {len(enabled)} enabled")
    print("=" * 60)
    for m in modules:
        status = "ON " if m.get("enabled", True) else "OFF"
        lock   = " [personal]" if m.get("personal_only") else ""
        print(f"  [{status}] {m['id']:<24} tab={m.get('tab_target','?'):<18} v{m.get('version','?')}{lock}")
    print("=" * 60)
