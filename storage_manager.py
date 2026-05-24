"""
storage_manager.py — Feature 10: Storage Manager Agent
Checks disk usage per slot, enforces quotas by moving to overflow.
Standalone: python storage_manager.py report
"""
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE           = Path(__file__).parent
STORAGE_CFG    = HERE / "storage_config.json"
BASE_PATH_D    = Path("D:/")

# Files never moved or deleted by enforce_quota
_PROTECTED = {"STATUS.md", "INDEX.md", "HISTORY.md", "ACCA.md"}


def _load_config() -> dict:
    if STORAGE_CFG.exists():
        try:
            return json.loads(STORAGE_CFG.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"base_path": "D:/", "total_allocated_gb": 1000, "slots": []}


def _resolve_folder(slot: dict) -> Path:
    """Resolve the folder path for a slot."""
    folder = slot["folder"]
    if os.path.isabs(folder) or folder.startswith("D:/") or folder.startswith("D:\\"):
        return Path(folder)
    base = Path(_load_config().get("base_path", "D:/"))
    return base / folder


def _dir_size_gb(path: Path) -> float:
    """Return directory size in GB. Returns 0.0 if path missing."""
    if not path.exists():
        return 0.0
    try:
        total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        return round(total / (1024 ** 3), 4)
    except Exception:
        return 0.0


def check_slot_usage(slot_name: str) -> dict:
    """Check actual disk usage of a named slot."""
    cfg   = _load_config()
    slot  = next((s for s in cfg.get("slots", []) if s["name"] == slot_name), None)
    if slot is None:
        return {"error": f"Slot not found: {slot_name}"}

    folder   = _resolve_folder(slot)
    used_gb  = _dir_size_gb(folder)
    quota_gb = slot.get("quota_gb", 0)
    pct      = round(used_gb / quota_gb * 100, 1) if quota_gb else 0.0

    if pct >= 95:
        status = "critical"
    elif pct >= 80:
        status = "warning"
    else:
        status = "ok"

    return {
        "name":       slot_name,
        "folder":     str(folder),
        "used_gb":    used_gb,
        "quota_gb":   quota_gb,
        "percent_used": pct,
        "status":     status,
        "component":  slot.get("component", "?"),
    }


def check_all_slots() -> dict:
    """Run check_slot_usage for all configured slots."""
    cfg     = _load_config()
    results = {}
    for slot in cfg.get("slots", []):
        name = slot["name"]
        results[name] = check_slot_usage(name)
    total_alloc = cfg.get("total_allocated_gb", 0)
    total_used  = round(sum(r.get("used_gb", 0) for r in results.values()), 4)
    return {
        "slots":           results,
        "total_allocated_gb": total_alloc,
        "total_used_gb":   total_used,
        "generated_at":    datetime.now().isoformat(),
    }


def enforce_quota(slot_name: str) -> dict:
    """
    If slot over quota, move oldest files to overflow folder.
    Never touches protected files (_PROTECTED set).
    """
    usage = check_slot_usage(slot_name)
    if "error" in usage:
        return usage
    if usage["status"] not in ("warning", "critical"):
        return {**usage, "action": "none"}

    cfg      = _load_config()
    overflow = next((s for s in cfg.get("slots", []) if s.get("component") == "overflow"), None)
    if not overflow:
        return {**usage, "action": "no_overflow_slot"}

    src_folder  = Path(usage["folder"])
    over_folder = _resolve_folder(overflow)
    over_folder.mkdir(parents=True, exist_ok=True)

    moved = []
    files = sorted(
        (f for f in src_folder.rglob("*") if f.is_file() and f.name not in _PROTECTED
         and not any(f.name.endswith(f"_v{i}.md") for i in range(100))),
        key=lambda f: f.stat().st_mtime,
    )
    for f in files:
        if check_slot_usage(slot_name).get("status") == "ok":
            break
        dest = over_folder / f.name
        try:
            shutil.move(str(f), str(dest))
            moved.append(f.name)
        except Exception:
            pass

    return {**usage, "action": "moved_to_overflow", "moved_files": moved}


def generate_weekly_report() -> dict:
    """Return full usage report with growth estimates and recommendations."""
    all_slots = check_all_slots()
    recommendations = []
    for name, info in all_slots["slots"].items():
        if info.get("status") == "critical":
            recommendations.append(f"CRITICAL: {name} is at {info.get('percent_used')}% — run enforce_quota immediately")
        elif info.get("status") == "warning":
            recommendations.append(f"WARNING: {name} is at {info.get('percent_used')}% — approaching quota")

    if not recommendations:
        recommendations.append("All slots healthy — no action needed")

    return {
        "generated_at":    datetime.now().isoformat(),
        "total_used_gb":   all_slots["total_used_gb"],
        "total_alloc_gb":  all_slots["total_allocated_gb"],
        "slots":           all_slots["slots"],
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report":
        report = generate_weekly_report()
        print("=" * 60)
        print("  STORAGE MANAGER — WEEKLY REPORT")
        print(f"  Generated: {report['generated_at']}")
        print("=" * 60)
        print(f"  Total used: {report['total_used_gb']:.2f} GB / {report['total_alloc_gb']} GB")
        print()
        for name, info in report["slots"].items():
            bar = "#" * int(info.get("percent_used", 0) / 5)
            print(f"  [{info.get('status','?').upper():<8}] {name:<30} {info.get('used_gb',0):.2f}/{info.get('quota_gb',0)} GB  [{bar:<20}] {info.get('percent_used',0):.1f}%")
        print()
        print("  Recommendations:")
        for r in report["recommendations"]:
            print(f"    - {r}")
        print("=" * 60)
