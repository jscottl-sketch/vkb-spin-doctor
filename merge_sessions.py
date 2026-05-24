"""
merge_sessions.py — Merges session_logs/*.md into HISTORY.md, then archives them.
Stdlib only. Never deletes files.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
SESSION_DIR = ROOT / "session_logs"
HISTORY_FILE = ROOT / "HISTORY.md"
ARCHIVE_DIR = ROOT / "archive_dead" / "session_logs"


def main():
    if not SESSION_DIR.exists():
        print("[SKIP] session_logs/ folder not found")
        return

    md_files = sorted(SESSION_DIR.glob("*.md"))

    if not md_files:
        print("[SKIP] nothing to merge — session_logs/ is empty")
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    merged = 0
    with HISTORY_FILE.open("a", encoding="utf-8") as history:
        for f in md_files:
            content = f.read_text(encoding="utf-8")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            history.write(f"\n\n---\n<!-- merged from session_logs/{f.name} on {timestamp} -->\n\n")
            history.write(content)

            dest = ARCHIVE_DIR / f.name
            if dest.exists():
                dest = ARCHIVE_DIR / f"{f.stem}_dup_{timestamp.replace(':', '-').replace(' ', '_')}{f.suffix}"
            shutil.move(str(f), str(dest))
            print(f"  [OK] {f.name} -> archive_dead/session_logs/{dest.name}")
            merged += 1

    print(f"[DONE] {merged} session file(s) merged into HISTORY.md and archived")


if __name__ == "__main__":
    main()
