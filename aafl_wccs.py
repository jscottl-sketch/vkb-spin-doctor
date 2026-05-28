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
STATUS_BAK = ROOT / "STATUS.md.bak"   # pre-write safety copy (same folder)
HISTORY = ROOT / "HISTORY.md"
ACCA = ROOT / "ACCA.md"
CHAT_LATEST = ROOT / "chat_latest.txt"
BACKUP_DIR = ROOT / "archive_dead"
EOF_MARKER = "<!-- END_OF_FILE -->"
LINE_COUNT_THRESHOLD = 0.90   # hard reject — no warn path, no proceeding
REJECTION_LOG = ROOT / "wccs_rejections.log"
WCCS_ERROR_LOG = ROOT / "wccs_errors.log"

# Section headers Mistral must include; if any missing → truncation detected → reject
REQUIRED_SECTION_PATTERNS = [
    (r"^##\s+WHO IS SCOTT",            "## WHO IS SCOTT — READ THIS FIRST"),
    (r"^##\s+CURRENT STATUS.+BUILT",   "## CURRENT STATUS — BUILT AND WORKING"),
    (r"^##\s+CURRENT STATUS.+PENDING", "## CURRENT STATUS — PENDING"),
]

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
        raise RuntimeError(f"line count {new_n} vs prev {old_n} ({ratio:.1%} < 90%)")

def verify_sections(content):
    for pattern, label in REQUIRED_SECTION_PATTERNS:
        if not re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            raise RuntimeError(f"missing required section '{label}' — Mistral output truncated")

def log_rejection(reason, old_n, new_n, ratio, restore_method="unknown"):
    stamp = dt.datetime.now().isoformat(timespec="seconds")
    pct = f"{ratio:.1%}" if ratio is not None else "N/A"
    entry = (f"[{stamp}] REJECTED — {reason} | old={old_n} lines, new={new_n} lines, "
             f"ratio={pct} | restore={restore_method}\n")
    with open(REJECTION_LOG, "a", encoding="utf-8") as f:
        f.write(entry)

def _log_wccs_error(msg):
    stamp = dt.datetime.now().isoformat(timespec="seconds")
    with open(WCCS_ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {msg}\n")

def _parse_by_sections(text):
    """Split text into [(header_line|None, body_text)] ordered pairs."""
    sections = []
    lines = text.splitlines(keepends=True)
    cur_header = None
    cur_body = []
    for line in lines:
        if re.match(r'^## ', line):
            sections.append((cur_header, ''.join(cur_body)))
            cur_header = line.rstrip('\n').rstrip('\r')
            cur_body = []
        else:
            cur_body.append(line)
    sections.append((cur_header, ''.join(cur_body)))
    return sections

def _extract_table_rows(body):
    """
    Parse a markdown table within body text.
    Returns (pre_lines, hdr_line, sep_line, rows_dict, post_lines).
    rows_dict preserves insertion order (Python 3.7+).
    """
    lines = body.splitlines(keepends=True)
    pre, post = [], []
    hdr = sep = None
    rows = {}
    state = 'pre'
    for line in lines:
        s = line.strip()
        if state == 'pre':
            if s.startswith('|'):
                if re.match(r'^\|[\s\-:]+\|', s):
                    sep = line
                    state = 'rows'
                else:
                    hdr = line
                    state = 'hdr_found'
            else:
                pre.append(line)
        elif state == 'hdr_found':
            if s.startswith('|') and re.match(r'^\|[\s\-:]+\|', s):
                sep = line
                state = 'rows'
            else:
                pre.append(hdr)
                hdr = None
                state = 'pre'
                pre.append(line)
        elif state == 'rows':
            if s.startswith('|'):
                cols = [c.strip() for c in s.strip('|').split('|')]
                key = cols[0] if cols else ''
                if key:
                    rows[key] = line
            else:
                post.append(line)
                state = 'post'
        else:
            post.append(line)
    return pre, hdr, sep, rows, post

def _rebuild_section(header, pre, hdr, sep, rows, post):
    body = ''.join(pre) + (hdr or '') + (sep or '') + ''.join(rows.values()) + ''.join(post)
    return f"{header}\n{body}"

def merge_status(old_text, new_text):
    """
    Merge new_text into old_text by ## section.
    BUILT AND WORKING: append new rows only — never remove existing rows.
    PENDING: update existing rows if present, append new, never remove.
    NEXT PRIORITIES: replace entirely from new_text.
    All other sections: preserve exactly from old_text.
    """
    old_secs = _parse_by_sections(old_text)
    new_secs = _parse_by_sections(new_text)

    def nk(h): return re.sub(r'\s+', ' ', (h or '').upper().strip())
    new_map = {nk(h): c for h, c in new_secs}

    result = []
    for old_h, old_c in old_secs:
        key = nk(old_h)

        if old_h is None:
            new_pre = new_map.get('', '')
            result.append(new_pre if new_pre and new_pre.strip() else old_c)
            continue

        if 'BUILT AND WORKING' in key:
            pre, hdr, sep, old_rows, post = _extract_table_rows(old_c)
            new_c = new_map.get(key, '')
            _, _, _, new_rows, _ = _extract_table_rows(new_c) if new_c else ([], None, None, {}, [])
            merged = dict(old_rows)
            for k, v in new_rows.items():
                if k not in merged:
                    merged[k] = v
            result.append(_rebuild_section(old_h, pre, hdr, sep, merged, post))

        elif 'PENDING' in key:
            pre, hdr, sep, old_rows, post = _extract_table_rows(old_c)
            new_c = new_map.get(key, '')
            _, _, _, new_rows, _ = _extract_table_rows(new_c) if new_c else ([], None, None, {}, [])
            merged = dict(old_rows)
            for k, v in new_rows.items():
                merged[k] = v
            result.append(_rebuild_section(old_h, pre, hdr, sep, merged, post))

        elif 'NEXT PRIORITIES' in key:
            new_c = new_map.get(key, old_c)
            result.append(f"{old_h}\n{new_c}")

        else:
            result.append(f"{old_h}\n{old_c}")

    merged_text = ''.join(result)
    if EOF_MARKER not in merged_text:
        merged_text = merged_text.rstrip() + f"\n\n{EOF_MARKER}\n"
    return merged_text

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
    # --- PRE-WRITE BACKUP: copy STATUS.md → STATUS.md.bak BEFORE validation or write ---
    if not args.dry_run and STATUS.exists():
        shutil.copy2(STATUS, STATUS_BAK)
        print(f"[PRE-BAK] STATUS.md.bak created ({STATUS.stat().st_size} bytes)")
    print(f"[START] aafl_wccs.py {'(DRY RUN)' if args.dry_run else ''}")
    new_status = rewrite_status(chat_text, current_status, args.dry_run)

    old_n = len(current_status.splitlines())
    new_n = len(new_status.splitlines())
    ratio = new_n / old_n if old_n > 0 else 1.0

    # Sanity check AI output isn't empty/garbage before merging
    if new_n < 10:
        rejection_reason = f"AI output too short ({new_n} lines) — likely empty or garbled"
        log_rejection(rejection_reason, old_n, new_n, ratio, "preserved (STATUS.md not modified)")
        print(f"WCCS REJECTED: {rejection_reason}. Old file preserved.")
        sys.exit(1)

    # --- Read-merge-write with 90% sanity check ---
    # Merge first — preserves all old sections not explicitly replaced.
    # Then validate required sections against the merged result.
    merged = merge_status(current_status, new_status)
    merged_n = len(merged.splitlines())

    # --- Validate required sections on merged output (not raw AI output) ---
    rejection_reason = None
    try:
        verify_sections(merged)
    except RuntimeError as e:
        rejection_reason = str(e)
    if rejection_reason:
        restore_method = "preserved (STATUS.md not modified)"
        log_rejection(rejection_reason, old_n, merged_n, merged_n / old_n if old_n > 0 else 1.0, restore_method)
        print(f"WCCS REJECTED: {rejection_reason}. Old file preserved.")
        sys.exit(1)
    if args.dry_run:
        print(f"[DRY] STATUS.md would be {merged_n} lines after merge (prev {old_n})")
    else:
        try:
            STATUS_TMP = STATUS.with_name("STATUS_tmp.md")
            STATUS_TMP.write_text(merged, encoding="utf-8")
            tmp_n = len(STATUS_TMP.read_text(encoding="utf-8").splitlines())
            if tmp_n < old_n * LINE_COUNT_THRESHOLD:
                try:
                    STATUS_TMP.unlink()
                except OSError:
                    pass
                err = f"STATUS merge aborted: {tmp_n} lines < 90% of {old_n} ({old_n * LINE_COUNT_THRESHOLD:.0f})"
                _log_wccs_error(err)
                print(f"[ABORT] {err}. STATUS.md untouched.")
            else:
                bak = backup_file(STATUS)
                print(f"[OK] Backed up STATUS.md to {bak.name}")
                STATUS_TMP.replace(STATUS)
                print(f"[OK] STATUS.md written via merge ({tmp_n} lines, was {old_n})")
        except Exception as _write_err:
            _log_wccs_error(f"STATUS write crashed: {_write_err}")
            print(f"[ERROR] STATUS.md write crashed — see wccs_errors.log. {_write_err}")
    today = dt.date.today().isoformat()
    entry = f"\n---\n\n### {today}\n\n{chat_text.strip()}\n"
    if args.dry_run:
        print(f"[DRY] Would append to HISTORY.md")
    else:
        try:
            append_to_file(HISTORY, entry, f"# HISTORY — VKB Spin Doctor\n*Append-only chat log.*\n")
            print(f"[OK] HISTORY.md appended")
        except Exception as _hist_err:
            _log_wccs_error(f"HISTORY append crashed: {_hist_err}")
            print(f"[WARN] HISTORY.md append failed — see wccs_errors.log. {_hist_err}")
    new_codes = extract_acca_codes(chat_text)
    if new_codes:
        existing = read_text(ACCA).upper()
        additions = [f"| {c} | {m} | {today} |" for c,m in new_codes if f"| {c.upper()} " not in existing]
        if additions:
            entry = "\n" + "\n".join(additions) + "\n"
            if args.dry_run:
                print(f"[DRY] Would append {len(additions)} codes to ACCA.md")
            else:
                try:
                    append_to_file(ACCA, entry, f"# ACCA — VKB Spin Doctor\n*Append-only.*\n\n| Code | Meaning | Added |\n|---|---|---|\n")
                    print(f"[OK] ACCA.md appended ({len(additions)} codes)")
                except Exception as _acca_err:
                    _log_wccs_error(f"ACCA append crashed: {_acca_err}")
                    print(f"[WARN] ACCA.md append failed — see wccs_errors.log. {_acca_err}")
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
