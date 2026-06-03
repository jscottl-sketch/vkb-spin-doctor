"""
tests/test_wccs.py — Verify WCCS prerequisites without triggering an actual save.
Checks: STATUS.md readable, HISTORY.md readable, .env provider creds, tmp write.
Exits 0 if all pass, 1 if any fail.
"""
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

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


def main():
    print("=== test_wccs.py ===")

    # 1. aafl_wccs.py exists
    wccs = HERE / "aafl_wccs.py"
    check("aafl_wccs.py exists", wccs.exists())

    # 2. STATUS.md readable + non-empty
    status = HERE / "STATUS.md"
    if check("STATUS.md exists", status.exists()):
        text = status.read_text(encoding="utf-8", errors="replace")
        check("STATUS.md non-empty", len(text) > 100)
        check("STATUS.md has BUILT section",
              "CURRENT STATUS" in text and "BUILT" in text)

    # 3. HISTORY.md readable + non-empty
    history = HERE / "HISTORY.md"
    if check("HISTORY.md exists", history.exists()):
        h = history.read_text(encoding="utf-8", errors="replace")
        check("HISTORY.md non-empty", len(h) > 10)

    # 4. .env has at least one provider key
    env_file = HERE / ".env"
    if check(".env exists", env_file.exists()):
        env_text = env_file.read_text(encoding="utf-8", errors="replace")
        has_key = any(k in env_text for k in [
            "MISTRAL_API_KEY", "GEMINI_API_KEY", "CEREBRAS_API_KEY",
            "GROQ_API_KEY", "OPENROUTER_API_KEY"
        ])
        check(".env has at least one provider API key", has_key)

    # 5. Can write a temp file to archive_dead/
    archive = HERE / "archive_dead"
    archive.mkdir(exist_ok=True)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=str(archive), suffix=".tmp")
        os.close(fd)
        Path(tmp_path).unlink()
        check("Can write to archive_dead/", True)
    except Exception as e:
        check("Can write to archive_dead/", False, str(e)[:60])

    # 6. chat_latest.txt readable (or absent — that's fine)
    chat = HERE / "chat_latest.txt"
    if chat.exists():
        try:
            _ = chat.read_text(encoding="utf-8", errors="replace")
            check("chat_latest.txt readable", True)
        except Exception as e:
            check("chat_latest.txt readable", False, str(e)[:60])
    else:
        check("chat_latest.txt present (optional)", False,
              "missing — WCCS will create it on first run")
        # Don't fail the suite for this — it's optional
        global FAIL
        FAIL -= 1  # undo the FAIL since this is non-fatal

    total = PASS + FAIL
    print(f"\nRESULT: {PASS}/{total} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
