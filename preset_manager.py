"""
preset_manager.py — Feature 2: Preset System
Save, load, list, delete MCC state presets.
Standalone: python preset_manager.py list
"""
import json
import sys
from datetime import datetime
from pathlib import Path

HERE        = Path(__file__).parent
PRESETS_DIR = HERE / "presets"


def _preset_path(name: str) -> Path:
    safe = name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    return PRESETS_DIR / f"{safe}.json"


def save_preset(name: str, state_dict: dict) -> bool:
    """Write preset to presets/<name>.json. Returns True on success."""
    PRESETS_DIR.mkdir(exist_ok=True)
    payload = {
        "name":    name,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "state":   state_dict,
    }
    try:
        _preset_path(name).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return True
    except Exception as exc:
        print(f"[preset] save failed: {exc}")
        return False


def load_preset(name: str) -> dict | None:
    """Read and return preset dict, or None if not found."""
    p = _preset_path(name)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def list_presets() -> list:
    """Return list of dicts: {name, created, file}."""
    PRESETS_DIR.mkdir(exist_ok=True)
    results = []
    for f in sorted(PRESETS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results.append({
                "name":    data.get("name", f.stem),
                "created": data.get("created", ""),
                "file":    f.name,
            })
        except Exception:
            results.append({"name": f.stem, "created": "", "file": f.name})
    return results


def delete_preset(name: str) -> bool:
    """Delete a preset file. Never deletes the last preset. Returns True if deleted."""
    all_presets = list_presets()
    if len(all_presets) <= 1:
        print("[preset] Cannot delete last preset.")
        return False
    p = _preset_path(name)
    if not p.exists():
        return False
    try:
        p.unlink()
        return True
    except Exception as exc:
        print(f"[preset] delete failed: {exc}")
        return False


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        presets = list_presets()
        print(f"Presets ({len(presets)} found):")
        for p in presets:
            print(f"  {p['name']:<30} created: {p['created']}")
    elif cmd == "save" and len(sys.argv) >= 3:
        n = sys.argv[2]
        save_preset(n, {"test": True})
        print(f"Saved preset: {n}")
    elif cmd == "load" and len(sys.argv) >= 3:
        n = sys.argv[2]
        data = load_preset(n)
        print(data if data else f"Not found: {n}")
    elif cmd == "delete" and len(sys.argv) >= 3:
        n = sys.argv[2]
        ok = delete_preset(n)
        print("Deleted" if ok else "Failed / not found")
