"""
tools/knowledge_harvester.py — Import project knowledge into knowledge_archive.

Sources harvested:
  a) HISTORY.md        — each dated session entry  -> tagged "session_history"
  b) session_logs/     — each .md/.txt file        -> tagged "session_log"
  c) ACCA.md           — each table row            -> tagged "acca_code"
  d) ALP_Database.md   — each numbered saving      -> tagged "alp_saving"
  e) meta_proposals/   — each .md file             -> tagged "meta_proposal"

Dedup: skip if first 100 chars already exist in knowledge_archive.

Usage:
  python tools/knowledge_harvester.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from memory_bank import store_knowledge, search_knowledge, _connect, _init_db


# ── Dedup helper ──────────────────────────────────────────────────────────────

def _already_stored(fingerprint: str) -> bool:
    """True if any row in knowledge_archive starts with the same first 100 chars."""
    fp = fingerprint[:100]
    conn = _connect()
    _init_db(conn)
    row = conn.execute(
        "SELECT id FROM knowledge_archive WHERE substr(content, 1, ?) = ? LIMIT 1",
        (len(fp), fp),
    ).fetchone()
    conn.close()
    return row is not None


def _store_if_new(source_file: str, content: str, tags: str, category: str) -> bool:
    content = content.strip()
    if not content or len(content) < 10:
        return False
    if _already_stored(content):
        return False
    store_knowledge(source_file, content, tags, category)
    return True


# ── Source parsers ────────────────────────────────────────────────────────────

def harvest_history(path: Path) -> int:
    """Split HISTORY.md on --- or ### date headings, store each block."""
    if not path.exists():
        print(f"  [SKIP] {path.name} not found")
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    # Split on horizontal rules (with optional surrounding blank lines) or ### headings
    blocks = re.split(r"\n\s*---\s*\n|\n(?=###\s)", text)
    count = 0
    for block in blocks:
        block = block.strip()
        # Skip header lines with no real content
        if len(block) < 30 or block.startswith("# HISTORY") or block.startswith("*Append-only"):
            continue
        if _store_if_new(path.name, block, "session_history", "session_history"):
            count += 1
    print(f"  HISTORY.md       -> {count} new records")
    return count


def harvest_session_logs(logs_dir: Path) -> int:
    """Each file in session_logs/ becomes one record."""
    if not logs_dir.exists():
        print(f"  [SKIP] {logs_dir} not found")
        return 0
    count = 0
    for f in sorted(logs_dir.iterdir()):
        if f.is_file() and f.suffix in (".md", ".txt"):
            content = f.read_text(encoding="utf-8", errors="replace").strip()
            if _store_if_new(f.name, content, "session_log", "session_log"):
                count += 1
    print(f"  session_logs/    -> {count} new records")
    return count


def harvest_acca(path: Path) -> int:
    """Each non-header pipe-table row in ACCA.md = one record."""
    if not path.exists():
        print(f"  [SKIP] {path.name} not found")
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("|") or "|---|" in line or line.startswith("| Code"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2 or not parts[0]:
            continue
        code    = parts[0]
        meaning = parts[1] if len(parts) > 1 else ""
        added   = parts[2] if len(parts) > 2 else ""
        content = f"ACCA code: {code} = {meaning} (added: {added})"
        if _store_if_new(path.name, content, "acca_code", "acca_code"):
            count += 1
    print(f"  ACCA.md          -> {count} new records")
    return count


def harvest_alp(path: Path) -> int:
    """Each numbered | # | Saving | ... | row in ALP_Database.md = one record."""
    if not path.exists():
        print(f"  [SKIP] {path.name} not found")
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("|") or "|---|" in line or "| # |" in line:
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2 or not parts[0]:
            continue
        content = " | ".join(p for p in parts if p)
        if _store_if_new(path.name, content, "alp_saving", "alp_saving"):
            count += 1
    print(f"  ALP_Database.md  -> {count} new records")
    return count


def harvest_meta_proposals(proposals_dir: Path) -> int:
    """Each .md file in meta_proposals/ = one record."""
    if not proposals_dir.exists():
        print(f"  [SKIP] {proposals_dir} not found")
        return 0
    count = 0
    for f in sorted(proposals_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8", errors="replace").strip()
        if _store_if_new(f.name, content, "meta_proposal", "meta_proposal"):
            count += 1
    print(f"  meta_proposals/  -> {count} new records")
    return count


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    print("[HARVESTER] Starting knowledge harvest...")
    total = 0
    total += harvest_history(ROOT / "HISTORY.md")
    total += harvest_session_logs(ROOT / "session_logs")
    total += harvest_acca(ROOT / "ACCA.md")
    total += harvest_alp(ROOT / "ALP_Database.md")
    total += harvest_meta_proposals(ROOT / "meta_proposals")
    print(f"\n[HARVESTER] Done. Total new records imported: {total}")
    return total


if __name__ == "__main__":
    run()
