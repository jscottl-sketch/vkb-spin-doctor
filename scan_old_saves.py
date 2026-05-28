"""
scan_old_saves.py — One-time scan for lost session/chat data.
Writes data/old_saves_scan.json and data/old_saves_report.txt
"""
import datetime
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).parent
FLAG_WORDS = {"session", "summary", "sesum", "wccs", "scott", "chat", "export"}

SCAN_LOCATIONS = [
    HERE / "session_logs",
    HERE / "archive_dead",
    HERE / "aafl_output",
]
SEVEN_DAYS_AGO = datetime.datetime.now() - datetime.timedelta(days=7)


def first_lines(path: Path, n=3) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return [ln[:200] for ln in lines[:n]]
    except Exception:
        return []


def is_flagged(path: Path) -> bool:
    name_lower = path.name.lower()
    if any(w in name_lower for w in FLAG_WORDS):
        return True
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:2000].lower()
        if any(w in head for w in FLAG_WORDS):
            return True
    except Exception:
        pass
    return False


def scan_file(path: Path) -> dict:
    try:
        stat = path.stat()
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
        return {
            "filename":  path.name,
            "path":      str(path),
            "size_bytes": stat.st_size,
            "modified":  mtime.isoformat()[:19],
            "first_lines": first_lines(path),
            "flagged":   is_flagged(path),
        }
    except Exception as exc:
        return {"path": str(path), "error": str(exc)}


def scan_root_old_md() -> list[Path]:
    results = []
    for p in HERE.glob("*.md"):
        try:
            mtime = datetime.datetime.fromtimestamp(p.stat().st_mtime)
            if mtime < SEVEN_DAYS_AGO:
                results.append(p)
        except Exception:
            pass
    return results


def find_chat_and_log_files() -> list[Path]:
    results = []
    for pattern in ["chat_*.txt", "*_log*.txt", "*sesum*"]:
        results.extend(HERE.rglob(pattern))
    return list(set(results))


def main():
    all_files: list[dict] = []

    # Scan directories
    for loc in SCAN_LOCATIONS:
        if not loc.exists():
            continue
        for p in sorted(loc.rglob("*")):
            if p.is_file() and p.suffix in (".txt", ".md", ".log", ".json", ".csv"):
                all_files.append(scan_file(p))

    # Scan old root .md files
    for p in scan_root_old_md():
        all_files.append(scan_file(p))

    # Scan chat/log/sesum name patterns
    for p in find_chat_and_log_files():
        entry = scan_file(p)
        if not any(f["path"] == entry["path"] for f in all_files):
            all_files.append(entry)

    flagged = [f for f in all_files if f.get("flagged")]

    # Write JSON
    out_json = HERE / "data" / "old_saves_scan.json"
    out_json.parent.mkdir(exist_ok=True)
    out_json.write_text(
        json.dumps({"scanned": len(all_files), "flagged": len(flagged), "files": all_files},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Write human-readable
    lines = [
        "OLD SAVES SCAN REPORT",
        f"Generated: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
        f"Total files scanned: {len(all_files)}",
        f"Flagged (possible chat/session data): {len(flagged)}",
        "",
        "=" * 60,
        "FLAGGED FILES",
        "=" * 60,
    ]
    if flagged:
        for f in flagged:
            lines.append(f"\n[FLAGGED] {f['path']}")
            lines.append(f"  Size: {f.get('size_bytes', '?')} bytes  |  Modified: {f.get('modified', '?')}")
            for ln in f.get("first_lines", []):
                lines.append(f"  > {ln}")
    else:
        lines.append("  (none found)")

    lines += [
        "",
        "=" * 60,
        "ALL FILES SCANNED",
        "=" * 60,
    ]
    for f in all_files:
        marker = "[FLAG] " if f.get("flagged") else "       "
        lines.append(f"{marker}{f.get('path', '?')}  ({f.get('size_bytes', '?')}b  {f.get('modified', '?')})")

    report_text = "\n".join(lines)
    out_txt = HERE / "data" / "old_saves_report.txt"
    out_txt.write_text(report_text, encoding="utf-8")

    sys.stdout.buffer.write(report_text.encode("utf-8", errors="replace"))
    sys.stdout.buffer.write(f"\n[DONE] Scan complete. JSON: {out_json}  Report: {out_txt}\n".encode("utf-8", errors="replace"))
    sys.stdout.flush()
    return flagged


if __name__ == "__main__":
    main()
