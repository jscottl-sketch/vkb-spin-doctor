"""
aafl_wccs.py — AAFL-powered WCCS (Write Claude Code Save)
Zero Claude allowance burn per save. Free Mistral does the work.

USAGE:
    python aafl_wccs.py                  # uses chat_latest.txt
    python aafl_wccs.py --chat path.txt  # custom chat summary
    python aafl_wccs.py --dry-run        # show changes, don't write
"""

import argparse, datetime as dt, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATUS = ROOT / "STATUS.md"
HISTORY = ROOT / "HISTORY.md"
ACCA = ROOT / "ACCA.md"
CHAT_LATEST = ROOT / "chat_latest.txt"
BACKUP_DIR = ROOT / "archive_dead"
EOF_MARKER = "<!-- END_OF_FILE -->"
LINE_COUNT_THRESHOLD = 0.80
LINE_COUNT_WARN      = 0.90

try:
    from aafl_core import AAFLCore
except ImportError:
    print("[FATAL] aafl_core.py not found. Aborting.")
    sys.exit(1)

def read_text(p): return p.read_text(encoding="utf-8") if p.exists() else ""

def backup_file(src):
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = BACKUP_DIR / f"{src.stem}_{stamp}{src.suffix}"
    shutil.copy2(src, dst)
    return dst

def atomic_write(path, content):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    if EOF_MARKER not in tmp.read_text(encoding="utf-8"):
        tmp.unlink()
        raise RuntimeError(f"[FAIL] EOF marker missing — refusing to write {path.name}")
    tmp.replace(path)

def verify_line_count(old, new, name):
    old_n, new_n = len(old.splitlines()), len(new.splitlines())
    if old_n == 0: return
    ratio = new_n / old_n
    if ratio < LINE_COUNT_THRESHOLD:
        raise RuntimeError(f"[FAIL] {name}: {new_n} lines vs prev {old_n} (ratio {ratio:.0%} < 80%). Refusing to write.")
    if ratio < LINE_COUNT_WARN:
        print(f"[WARN] {name}: {new_n} lines vs prev {old_n} (ratio {ratio:.0%}). Writing with caution.")

def append_to_file(path, entry, header=None):
    if not path.exists():
        path.write_text((header or "") + entry + "\n" + EOF_MARKER + "\n", encoding="utf-8")
    else:
        old = read_text(path)
        new = old.replace(EOF_MARKER, entry + "\n" + EOF_MARKER) if EOF_MARKER in old else old + entry + "\n" + EOF_MARKER + "\n"
        path.write_text(new, encoding="utf-8")

def extract_acca_codes(chat_text):
    codes, in_section = [], False
    pattern = re.compile(r"^\s*([A-Z]{2,6})\s*[=:]\s*(.+?)$", re.MULTILINE)
    for line in chat_text.splitlines():
        if re.search(r"acca|new code", line, re.IGNORECASE):
            in_section = True; continue
        if in_section:
            m = pattern.match(line)
            if m: codes.append((m.group(1), m.group(2).strip()))
            elif line.strip() and not line.startswith(("-","*","#")): in_section = False
    return codes

def rewrite_status(chat_text, current_status, dry):
    if dry:
        print("[DRY] Would call Mistral to rewrite STATUS.md")
        return current_status
    core = AAFLCore()
    today = dt.date.today().isoformat()
    prompt = f"""Update STATUS.md for VKB Spin Doctor project.

CURRENT STATUS.md:
{current_status}

CHAT SUMMARY:
{chat_text}

Rules:
1. Keep same structure (Who Is Scott, Mission Priority, Status tables, Big Vision, Providers, Next Priorities, What Not To Do)
2. Set "Last updated" to {today} and "Updated by" to aafl_wccs.py
3. Move completed pending items to built section
4. Add new items from chat summary
5. Update Next Priorities
6. End with exactly: <!-- END_OF_FILE -->
7. No chat log content (goes to HISTORY.md)
8. No ACCA codes (goes to ACCA.md)
9. Keep under 250 lines

Return the COMPLETE document. Do NOT summarize or shorten. Every section must appear in full.
Return ONLY the new STATUS.md content. No explanation. No code fences."""
    print("[AAFL] Calling free Mistral to rewrite STATUS.md...")
    result = core.run(prompt, task_type="batch", max_tokens=4000)
    new = result.response if result.ok else ""
    new = re.sub(r"^```\w*\n", "", new); new = re.sub(r"\n```$", "", new)
    if EOF_MARKER not in new: new = new.rstrip() + f"\n\n{EOF_MARKER}\n"
    return new

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat", default=str(CHAT_LATEST))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    chat_path = Path(args.chat)
    if not chat_path.exists():
        today_str = dt.date.today().isoformat()
        chat_path.write_text(f"{today_str}\nNo chat summary provided — light save mode\n", encoding="utf-8")
        print("[PRE-FLIGHT] chat_latest.txt missing — created minimal version")
    elif not chat_path.read_text(encoding="utf-8").strip():
        today_str = dt.date.today().isoformat()
        chat_path.write_text(f"{today_str}\nNo chat summary provided — light save mode\n", encoding="utf-8")
        print("[PRE-FLIGHT] chat_latest.txt was empty — created minimal version")
    else:
        print("[PRE-FLIGHT] chat_latest.txt found")
    chat_text = read_text(chat_path)
    current_status = read_text(STATUS)
    if not current_status:
        print("[FATAL] STATUS.md not found. Run handover split first.")
        sys.exit(1)
    print(f"[START] aafl_wccs.py {'(DRY RUN)' if args.dry_run else ''}")
    if not args.dry_run:
        bak = backup_file(STATUS)
        print(f"[OK] Backed up STATUS.md to {bak.name}")
    new_status = rewrite_status(chat_text, current_status, args.dry_run)
    try:
        verify_line_count(current_status, new_status, "STATUS.md")
        if args.dry_run:
            print(f"[DRY] STATUS.md would be {len(new_status.splitlines())} lines (prev {len(current_status.splitlines())})")
        else:
            atomic_write(STATUS, new_status)
            print(f"[OK] STATUS.md written ({len(new_status.splitlines())} lines)")
    except RuntimeError as e:
        print(str(e)); print("[RESTORE] STATUS.md untouched"); sys.exit(1)
    today = dt.date.today().isoformat()
    entry = f"\n---\n\n### {today}\n\n{chat_text.strip()}\n"
    if args.dry_run:
        print(f"[DRY] Would append to HISTORY.md")
    else:
        append_to_file(HISTORY, entry, f"# HISTORY — VKB Spin Doctor\n*Append-only chat log.*\n")
        print(f"[OK] HISTORY.md appended")
    new_codes = extract_acca_codes(chat_text)
    if new_codes:
        existing = read_text(ACCA).upper()
        additions = [f"| {c} | {m} | {today} |" for c,m in new_codes if f"| {c.upper()} " not in existing]
        if additions:
            entry = "\n" + "\n".join(additions) + "\n"
            if args.dry_run:
                print(f"[DRY] Would append {len(additions)} codes to ACCA.md")
            else:
                append_to_file(ACCA, entry, f"# ACCA — VKB Spin Doctor\n*Append-only.*\n\n| Code | Meaning | Added |\n|---|---|---|\n")
                print(f"[OK] ACCA.md appended ({len(additions)} codes)")
    if not args.dry_run:
        try:
            msg = f"WCCS auto-save {today} (aafl_wccs.py)"
            subprocess.run(["git","add","STATUS.md","HISTORY.md","ACCA.md"], cwd=ROOT, check=False, capture_output=True)
            subprocess.run(["git","commit","-m",msg], cwd=ROOT, check=False, capture_output=True)
            print(f"[OK] Git committed")
        except Exception as e:
            print(f"[WARN] Git commit failed (non-fatal): {e}")
        try:
            push_res = subprocess.run(["git", "push"], cwd=ROOT, capture_output=True, text=True)
            if push_res.returncode == 0:
                print("[GIT PUSH] Pushed to remote")
            else:
                print(f"[GIT PUSH] Failed — run manually. Error: {push_res.stderr.strip()}")
        except Exception as e:
            print(f"[GIT PUSH] Failed — run manually. Error: {e}")
    if not args.dry_run:
        _sunday_merge()
    print(f"[DONE] WCCS complete {'(dry run)' if args.dry_run else ''}")


def _sunday_merge():
    import datetime as _dt
    if _dt.date.today().weekday() != 6:  # 6 = Sunday
        print("[SKIP MERGE] Not Sunday")
        return
    print("[AUTO-MERGE] Sunday detected — running weekly merge")
    merge_script = ROOT / "merge_sessions.py"
    if not merge_script.exists():
        print("[AUTO-MERGE] merge_sessions.py not found — skipping. Build it separately.")
        return
    try:
        result = subprocess.run(
            [sys.executable, str(merge_script)],
            capture_output=True, text=True, timeout=60, cwd=str(ROOT),
        )
        out = (result.stdout + result.stderr).strip()
        if out:
            print(out)
        print(f"[AUTO-MERGE] Done (exit code {result.returncode})")
    except Exception as e:
        print(f"[AUTO-MERGE] Error: {e}")

if __name__ == "__main__":
    main()
