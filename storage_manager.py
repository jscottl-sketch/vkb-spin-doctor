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


def get_health_db_info() -> dict:
    """Return size + last archive date for the self-health DB."""
    health_db = HERE / "data" / "health.db"
    archive_dir = HERE / "data" / "archives"

    size_mb = 0.0
    if health_db.exists():
        try:
            size_mb = round(health_db.stat().st_size / (1024 * 1024), 3)
        except Exception:
            pass

    last_archive = None
    if archive_dir.exists():
        archives = sorted(archive_dir.glob("health_*.db"), key=lambda f: f.stat().st_mtime, reverse=True)
        if archives:
            last_archive = archives[0].name

    return {
        "health_db_size_mb": size_mb,
        "health_db_path":    str(health_db),
        "last_archive_name": last_archive,
        "archive_dir":       str(archive_dir),
    }


def archive_health_db(days: int = 90) -> dict:
    """Delegate to self_health.py to archive results older than N days."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("self_health", HERE / "self_health.py")
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            runner = mod.SelfHealthRunner()
            return runner.archive_old_results(days=days)
    except Exception as exc:
        return {"error": str(exc)}
    return {"error": "self_health.py not found"}


# ── STORM: Deduplication methods ─────────────────────────────────────────────

def deduplicate_status() -> dict:
    """Read STATUS.md BUILT section and find/remove duplicate component entries."""
    status_path = HERE / "STATUS.md"
    if not status_path.exists():
        return {"error": "STATUS.md not found"}

    lines = status_path.read_text(encoding="utf-8").splitlines()
    in_built = False
    built_rows = []
    other_lines = []
    duplicates = []

    for line in lines:
        if "## CURRENT STATUS — BUILT" in line:
            in_built = True
            other_lines.append(line)
            continue
        if in_built and line.startswith("## "):
            in_built = False

        if in_built and line.startswith("|") and not line.startswith("|---|"):
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if cols and cols[0] != "Component":
                key = cols[0].lower().replace("-", " ").replace("_", " ").strip()
                if key in {r["key"] for r in built_rows}:
                    duplicates.append(cols[0])
                    continue
                built_rows.append({"key": key, "line": line})
                other_lines.append(line)
            else:
                other_lines.append(line)
        else:
            other_lines.append(line)

    if duplicates:
        status_path.write_text("\n".join(other_lines), encoding="utf-8")

    return {
        "duplicates_found": len(duplicates),
        "duplicates": duplicates,
        "action": "removed" if duplicates else "none",
    }


def deduplicate_sesums() -> dict:
    """Check session_logs/sesum_*.md files for overlapping content."""
    logs_dir = HERE / "session_logs"
    if not logs_dir.exists():
        return {"error": "session_logs/ not found"}

    sesum_files = sorted(logs_dir.glob("sesum_*.md"))
    if not sesum_files:
        return {"overlapping": [], "note": "No sesum files found"}

    contents = {}
    for f in sesum_files:
        try:
            contents[f.name] = f.read_text(encoding="utf-8").lower()
        except Exception:
            pass

    overlaps = []
    names = list(contents.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            # Sample 3 key lines from a and check if they appear in b
            lines_a = [l.strip() for l in contents[a].splitlines() if len(l.strip()) > 30][:10]
            shared = sum(1 for l in lines_a if l in contents[b])
            if shared >= 3:
                overlaps.append(f"{a} ↔ {b} ({shared} matching lines)")

    return {
        "sesum_files_checked": len(sesum_files),
        "overlapping": overlaps,
        "note": "No files deleted — report only",
    }


def deduplicate_history() -> dict:
    """Check HISTORY.md for repeated date entries."""
    history_path = HERE / "HISTORY.md"
    if not history_path.exists():
        return {"error": "HISTORY.md not found"}

    import re
    lines = history_path.read_text(encoding="utf-8").splitlines()
    date_pat = re.compile(r"#+\s+\d{4}-\d{2}-\d{2}")
    seen_dates: dict[str, int] = {}
    repeated = []

    for line in lines:
        m = date_pat.match(line)
        if m:
            key = line.strip()
            seen_dates[key] = seen_dates.get(key, 0) + 1
            if seen_dates[key] == 2:
                repeated.append(key)

    return {
        "repeated_entries": repeated,
        "count": len(repeated),
        "note": "No deletions — report only. Manual review required.",
    }


def run_all_dedup() -> dict:
    """Run all 3 STORM deduplication checks and print combined report."""
    status_result  = deduplicate_status()
    sesum_result   = deduplicate_sesums()
    history_result = deduplicate_history()
    return {
        "status_dedup":  status_result,
        "sesum_dedup":   sesum_result,
        "history_dedup": history_result,
    }


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "dedup":
        result = run_all_dedup()
        print("=" * 60)
        print("  STORM — DEDUPLICATION REPORT")
        print("=" * 60)
        s = result["status_dedup"]
        print(f"  STATUS.md:  {s.get('duplicates_found', 0)} duplicates {'removed' if s.get('action') == 'removed' else 'found (none)'}")
        if s.get("duplicates"):
            for d in s["duplicates"]:
                print(f"    - {d}")
        se = result["sesum_dedup"]
        print(f"  SESUMs:     {len(se.get('overlapping', []))} overlapping pairs")
        for o in se.get("overlapping", []):
            print(f"    - {o}")
        h = result["history_dedup"]
        print(f"  HISTORY.md: {h.get('count', 0)} repeated date entries (manual review needed)")
        for r in h.get("repeated_entries", []):
            print(f"    - {r}")
        print("=" * 60)
    elif cmd == "report":
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
