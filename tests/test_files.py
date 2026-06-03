"""
tests/test_files.py — Verify STATUS.md BUILT files exist on disk + data/*.json validity.
Standalone. Exits 0 if all pass, 1 if any fail.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PASS = 0
FAIL = 0


def check(label: str, ok: bool, detail: str = "") -> bool:
    global PASS, FAIL
    status = "PASS" if ok else "FAIL"
    suffix = f": {detail}" if detail else ""
    print(f"{status}: {label}{suffix}")
    if ok:
        PASS += 1
    else:
        FAIL += 1
    return ok


def status_built_files() -> list:
    status = HERE / "STATUS.md"
    if not status.exists():
        return []
    text = status.read_text(encoding="utf-8", errors="replace")
    in_built = False
    files = []
    for line in text.splitlines():
        if re.search(r"CURRENT STATUS.+BUILT", line):
            in_built = True
        elif re.match(r"^##\s", line) and in_built:
            in_built = False
        if not in_built:
            continue
        m = re.search(r'`?([a-zA-Z_][a-zA-Z0-9_./-]*\.py)`?', line)
        if m:
            files.append(m.group(1))
    return list(dict.fromkeys(files))


def main():
    print("=== test_files.py ===")

    # Check STATUS.md exists
    check("STATUS.md exists", (HERE / "STATUS.md").exists())

    # Check every BUILT .py file
    py_files = status_built_files()
    check(f"STATUS.md parsed ({len(py_files)} .py files found)", len(py_files) > 0)

    for name in py_files:
        p = HERE / name
        check(f"{name} exists", p.exists())
        if p.exists():
            check(f"{name} non-empty", p.stat().st_size > 0)

    # Check data/*.json files validity
    data_dir = HERE / "data"
    if data_dir.exists():
        for jf in sorted(data_dir.glob("*.json")):
            try:
                json.loads(jf.read_text(encoding="utf-8", errors="replace"))
                check(f"data/{jf.name} valid JSON", True)
            except json.JSONDecodeError as e:
                check(f"data/{jf.name} valid JSON", False, str(e)[:60])
    else:
        check("data/ directory exists", False)

    total = PASS + FAIL
    print(f"\nRESULT: {PASS}/{total} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
