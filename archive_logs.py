import shutil
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = Path("session_logs")
ARCHIVE_DIR = LOG_DIR / "archive"
CUTOFF_DAYS = 30


def main():
    if not LOG_DIR.exists():
        print("session_logs/ not found — nothing to archive.")
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now() - timedelta(days=CUTOFF_DAYS)
    moved = 0
    errors = 0

    for item in LOG_DIR.iterdir():
        if item == ARCHIVE_DIR or item.is_dir():
            continue
        try:
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff:
                dest = ARCHIVE_DIR / item.name
                if dest.exists():
                    dest = ARCHIVE_DIR / f"{item.stem}_{int(mtime.timestamp())}{item.suffix}"
                shutil.move(str(item), str(dest))
                print(f"  Archived: {item.name}  (modified {mtime.strftime('%Y-%m-%d')})")
                moved += 1
        except Exception as e:
            print(f"  ERROR moving {item.name}: {e}")
            errors += 1

    print(f"\n  Done — {moved} file(s) archived, {errors} error(s).")


if __name__ == "__main__":
    print(f"\n=== archive_logs  cutoff={CUTOFF_DAYS} days  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    main()
