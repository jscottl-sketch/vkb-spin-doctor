"""
project_timeline_builder.py — Live Project Timeline Generator
Scans git log, session_logs/, STATUS.md, HISTORY.md, ACCA.md, OCB entries.
Saves data/project_timeline.json. Called automatically on every WCCS run.

Run standalone: python project_timeline_builder.py
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, date
from pathlib import Path

ROOT        = Path(__file__).resolve().parent
STATUS_FILE = ROOT / "STATUS.md"
HISTORY_FILE= ROOT / "HISTORY.md"
ACCA_FILE   = ROOT / "ACCA.md"
SESSION_LOGS= ROOT / "session_logs"
HEALTH_DIR  = ROOT / "health_results"
OUTPUT_FILE = ROOT / "data" / "project_timeline.json"


def _git_log():
    """Return list of {hash, date, message} from git log."""
    try:
        res = subprocess.run(
            ["git", "log", "--oneline", "--format=%H|%ai|%s", "--max-count=200"],
            capture_output=True, text=True, timeout=15, cwd=str(ROOT),
        )
        entries = []
        for line in res.stdout.splitlines():
            parts = line.split("|", 2)
            if len(parts) == 3:
                entries.append({"hash": parts[0][:8], "date": parts[1][:10], "message": parts[2].strip()})
        return entries
    except Exception:
        return []


def _parse_status_built():
    """Return list of component names from BUILT AND WORKING section."""
    if not STATUS_FILE.exists():
        return []
    text = STATUS_FILE.read_text(encoding="utf-8", errors="replace")
    items = []
    in_section = False
    for line in text.splitlines():
        if re.match(r"^##\s+CURRENT STATUS.+BUILT", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            m = re.match(r"^\|\s*(.+?)\s*\|", line)
            if m:
                val = m.group(1).strip()
                if val and not val.startswith("---") and val.lower() not in ("component", "#"):
                    items.append(val)
    return items


def _parse_status_pending():
    """Return list of (component, notes) from PENDING section."""
    if not STATUS_FILE.exists():
        return []
    text = STATUS_FILE.read_text(encoding="utf-8", errors="replace")
    items = []
    in_section = False
    for line in text.splitlines():
        if re.match(r"^##\s+CURRENT STATUS.+PENDING", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            m = re.match(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|", line)
            if m:
                comp = m.group(1).strip()
                notes = m.group(2).strip()
                if comp and not comp.startswith("---") and comp.lower() not in ("component", "#"):
                    items.append({"component": comp, "notes": notes})
    return items


def _parse_next_priorities():
    """Return top-5 priorities from NEXT PRIORITIES section."""
    if not STATUS_FILE.exists():
        return []
    text = STATUS_FILE.read_text(encoding="utf-8", errors="replace")
    in_section = False
    items = []
    for line in text.splitlines():
        if re.match(r"^##\s+NEXT PRIORITIES", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if line.startswith("## ") or line.startswith("---"):
                break
            m = re.match(r"^\d+\.\s+(.+)", line.strip())
            if m:
                items.append(m.group(1).strip())
    return items[:5]


def _extract_ocb_nodes():
    """Parse STATUS.md BUILT section for OCB-X entries with phase breakdown."""
    if not STATUS_FILE.exists():
        return []
    text = STATUS_FILE.read_text(encoding="utf-8", errors="replace")
    nodes = {}
    in_built = False
    for line in text.splitlines():
        if re.match(r"^##\s+CURRENT STATUS.+BUILT", line, re.IGNORECASE):
            in_built = True
            continue
        if in_built:
            if line.startswith("## "):
                break
            m = re.match(r"^\|\s*(OCB-[A-Z]+)\s+Phase\s+(\d+)\s*\((.+?)\)\s*\|\s*(.+?)\s*\|", line)
            if m:
                ocb = m.group(1)
                phase = int(m.group(2))
                phase_name = m.group(3).strip()
                notes = m.group(4).strip()
                if ocb not in nodes:
                    nodes[ocb] = {"id": ocb, "phases": [], "mot_score": None, "date": None}
                passed = "108/108" in notes or "PASS" in notes.upper() or "CLEAR" in notes.upper()
                nodes[ocb]["phases"].append({
                    "phase": phase,
                    "name": phase_name,
                    "notes": notes,
                    "status": "PASS" if passed else "COMPLETE"
                })
                # Extract date from notes
                dm = re.search(r"(\d{4}-\d{2}-\d{2})", notes)
                if dm and nodes[ocb]["date"] is None:
                    nodes[ocb]["date"] = dm.group(1)
                # MOT score
                sm = re.search(r"(\d+)/(\d+)\s+(?:MOT|ALL CLEAR)", notes)
                if sm:
                    nodes[ocb]["mot_score"] = f"{sm.group(1)}/{sm.group(2)}"
    return list(nodes.values())


def _git_files_per_commit(commits):
    """Add files_changed count to each commit entry."""
    for c in commits[:30]:  # Only enrich recent 30 to avoid slowness
        try:
            res = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", c["hash"]],
                capture_output=True, text=True, timeout=8, cwd=str(ROOT),
            )
            c["files_changed"] = len(res.stdout.strip().splitlines())
        except Exception:
            c["files_changed"] = 0
    return commits


def _mot_scores_from_history():
    """Scan health_results/ for MOT scores over time."""
    scores = []
    mot_dir = HEALTH_DIR
    if mot_dir.exists():
        for f in sorted(mot_dir.glob("full_mot_report*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                scores.append({
                    "date": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"),
                    "passed": data.get("passed", 0),
                    "total": data.get("total", 0),
                    "score": f"{data.get('passed',0)}/{data.get('total',0)}"
                })
            except Exception:
                pass
    # Also read current latest
    latest = HEALTH_DIR / "full_mot_report.json"
    if latest.exists():
        try:
            data = json.loads(latest.read_text(encoding="utf-8"))
            scores.append({
                "date": datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d"),
                "passed": data.get("passed", 0),
                "total": data.get("total", 0),
                "score": f"{data.get('passed',0)}/{data.get('total',0)}"
            })
        except Exception:
            pass
    # Deduplicate by date (keep last)
    seen = {}
    for s in scores:
        seen[s["date"]] = s
    return list(seen.values())


def _velocity(commits):
    """Work velocity: builds per day and per week."""
    if len(commits) < 2:
        return {"per_day": 0, "per_week": 0, "total_commits": len(commits)}
    try:
        dates = [datetime.strptime(c["date"], "%Y-%m-%d") for c in commits if c.get("date")]
        if len(dates) < 2:
            return {"per_day": 0, "per_week": 0, "total_commits": len(commits)}
        span_days = (dates[0] - dates[-1]).days
        if span_days <= 0:
            return {"per_day": len(commits), "per_week": len(commits) * 7, "total_commits": len(commits)}
        per_day = round(len(commits) / span_days, 2)
        per_week = round(per_day * 7, 1)
        return {"per_day": per_day, "per_week": per_week, "total_commits": len(commits), "span_days": span_days}
    except Exception:
        return {"per_day": 0, "per_week": 0, "total_commits": len(commits)}


def _milestones(commits, built_items):
    """Detect milestone events from commits and built items."""
    milestones = []
    for c in commits:
        msg = c.get("message", "")
        if re.search(r"108/108|ALL CLEAR|MOT PASS", msg, re.IGNORECASE):
            milestones.append({"date": c["date"], "label": "108/108 MOT", "type": "mot", "detail": msg[:80]})
        elif re.search(r"^v\d+:", msg):
            ver = re.match(r"^(v\d+):", msg).group(1)
            milestones.append({"date": c["date"], "label": ver, "type": "version", "detail": msg[:80]})
        elif re.search(r"first.*(benchmark|proof|confirmed)", msg, re.IGNORECASE):
            milestones.append({"date": c["date"], "label": "Benchmark", "type": "benchmark", "detail": msg[:80]})

    # Static milestones from known history
    static = [
        {"date": "2026-05-20", "label": "Handover Split", "type": "architecture", "detail": "STATUS/HISTORY/ACCA/INDEX created"},
        {"date": "2026-05-23", "label": "First 108/108", "type": "mot", "detail": "First perfect MOT score"},
        {"date": "2026-05-28", "label": "LLOW Launched", "type": "feature", "detail": "Loop Law Organiser Window launched"},
    ]
    all_ms = milestones + static
    seen = set()
    unique = []
    for m in all_ms:
        key = m["label"]
        if key not in seen:
            seen.add(key)
            unique.append(m)
    return sorted(unique, key=lambda x: x.get("date", ""))


def _acca_codes_count():
    """Count entries in ACCA.md."""
    if not ACCA_FILE.exists():
        return 0
    text = ACCA_FILE.read_text(encoding="utf-8", errors="replace")
    rows = [l for l in text.splitlines() if l.strip().startswith("|") and "---" not in l and "Code" not in l]
    return len(rows)


def _scout_findings_timeline():
    """Summarise scout output files over time."""
    scout_dir = ROOT / "scout_output"
    findings = []
    if scout_dir.exists():
        for f in sorted(scout_dir.glob("*.txt")):
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
                findings.append({
                    "date": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"),
                    "file": f.name,
                    "lines": len(lines),
                })
            except Exception:
                pass
    return findings[-20:]  # last 20


def build():
    commits = _git_log()
    commits = _git_files_per_commit(commits)
    built_items = _parse_status_built()
    pending_items = _parse_status_pending()
    next_priorities = _parse_next_priorities()
    ocb_nodes = _extract_ocb_nodes()
    mot_scores = _mot_scores_from_history()
    vel = _velocity(commits)
    ms = _milestones(commits, built_items)
    scout_findings = _scout_findings_timeline()

    pending_count = len(pending_items)
    built_count = len(built_items)
    total_items = pending_count + built_count
    completion_ratio = round(built_count / total_items * 100, 1) if total_items > 0 else 0

    timeline = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "total_commits": vel.get("total_commits", 0),
            "built_items": built_count,
            "pending_items": pending_count,
            "completion_ratio_pct": completion_ratio,
            "acca_codes": _acca_codes_count(),
            "ocb_count": len(ocb_nodes),
        },
        "velocity": vel,
        "milestones": ms,
        "ocb_nodes": ocb_nodes,
        "mot_scores": mot_scores,
        "recent_commits": commits[:50],
        "pending_items": pending_items,
        "next_priorities": next_priorities,
        "scout_findings": scout_findings,
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    tmp = OUTPUT_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(timeline, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(OUTPUT_FILE)
    print(f"[TIMELINE] Built — {built_count} built, {pending_count} pending, {vel.get('total_commits',0)} commits, {len(ocb_nodes)} OCBs")
    return timeline


if __name__ == "__main__":
    build()
