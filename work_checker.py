"""
work_checker.py — Scans SESUM files and STATUS.md to detect lost/stuck work.
Run: python work_checker.py
Output: data/work_report.json
"""

import hashlib
import json
import os
import re
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SESSION_LOGS = ROOT / "session_logs"
STATUS_FILE  = ROOT / "STATUS.md"
HISTORY_FILE = ROOT / "HISTORY.md"
WORK_REPORT  = ROOT / "data" / "work_report.json"

_ORPHAN_KWDS = re.compile(
    r'\b(discussed|brainstorm|planned|idea|RIBS|to\s+explore)\b', re.IGNORECASE
)
_HIST_KWDS = re.compile(r'\b(RIBS|brainstorm)\b', re.IGNORECASE)


class WorkChecker:

    def scan_sesum_files(self):
        sessions = []
        if not SESSION_LOGS.exists():
            return sessions
        for f in sorted(SESSION_LOGS.glob("sesum_*.md"), reverse=True):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
                session = {
                    "filename": f.name,
                    "date": self._extract_field(text, "DATE"),
                    "session_type": self._extract_field(text, "SESSION_TYPE"),
                    "clac_completed": self._extract_list(text, "CLAC_COMPLETED"),
                    "incomplete": self._extract_list(text, "INCOMPLETE_FROM_LAST"),
                    "new_this_session": self._extract_list(text, "NEW_THIS_SESSION"),
                    "bugs_found": self._extract_list(text, "BUGS_FOUND"),
                    "next": self._extract_list(text, "NEXT"),
                    "new_acca": self._extract_field(text, "NEW_ACCA"),
                }
                sessions.append(session)
            except Exception:
                continue
        return sessions

    def _extract_field(self, text, key):
        m = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
        return m.group(1).strip() if m else ""

    def _extract_list(self, text, key):
        m = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
        if not m:
            return []
        val = m.group(1).strip()
        if val.startswith("["):
            try:
                return json.loads(val)
            except Exception:
                pass
        return [item.strip() for item in val.split(",") if item.strip()]

    def _read_status_section(self, section_key):
        items = []
        if not STATUS_FILE.exists():
            return items
        text = STATUS_FILE.read_text(encoding="utf-8", errors="replace")
        in_section = False
        for line in text.splitlines():
            if re.match(r"^##\s+" + re.escape(section_key), line, re.IGNORECASE):
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

    def compare_to_status(self):
        sessions = self.scan_sesum_files()
        built_items = self._read_status_section("CURRENT STATUS.+BUILT")
        built_lower = {i.lower() for i in built_items}

        item_session_count = {}
        for s in sessions:
            for item in s["incomplete"]:
                item_lower = item.lower()
                item_session_count[item_lower] = item_session_count.get(item_lower, 0) + 1

        completed_items = []
        lost_items = []
        stuck_items = []

        for item_lower, count in item_session_count.items():
            if any(item_lower in built.lower() or built.lower() in item_lower for built in built_lower):
                completed_items.append(item_lower)
            else:
                lost_items.append(item_lower)
                if count >= 3:
                    stuck_items.append({"item": item_lower, "sessions": count})

        return completed_items, lost_items, stuck_items

    def completion_score(self, session):
        completed = len(session.get("clac_completed", []))
        incomplete = len(session.get("incomplete", []))
        total = completed + incomplete
        if total == 0:
            return 100.0
        return round((completed / total) * 100, 1)

    def detect_orphaned_plans(self):
        sessions = self.scan_sesum_files()
        today = datetime.date.today()

        # Build completed text blob for cross-referencing
        completed_parts = []
        for s in sessions:
            for item in s.get("clac_completed", []):
                completed_parts.append(item.lower())
        for item in self._read_status_section("CURRENT STATUS.+BUILT"):
            completed_parts.append(item.lower())
        completed_text = " | ".join(completed_parts)

        def is_covered(plan_text):
            plan_lower = plan_text.lower().strip()
            if not plan_lower:
                return True
            if plan_lower in completed_text:
                return True
            words = [w for w in re.findall(r'\b\w{5,}\b', plan_lower)]
            if words:
                hits = sum(1 for w in words if w in completed_text)
                if hits >= max(2, len(words) // 2):
                    return True
            return False

        candidates = {}

        def add_candidate(text, date_str):
            text = text.strip()
            if len(text) < 5:
                return
            key = text.lower()[:120]
            if key not in candidates:
                candidates[key] = {"text": text[:200], "date_first": date_str, "count": 0}
            candidates[key]["count"] += 1

        for s in sessions:
            filename = s["filename"]
            date_str = s.get("date", "")
            if not date_str:
                m = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
                date_str = m.group(1) if m else "unknown"

            # NEXT: items are explicitly planned but may never have been completed
            for item in s.get("next", []):
                if item.strip():
                    add_candidate(item, date_str)

            # Lines with orphan keywords in raw SESUM body text
            f = SESSION_LOGS / filename
            if f.exists():
                raw = f.read_text(encoding="utf-8", errors="replace")
                for line in raw.splitlines():
                    if _ORPHAN_KWDS.search(line):
                        clean = re.sub(r'^[A-Z_]+:\s*', '', line).strip()
                        for part in re.split(r'[,;]', clean):
                            part = part.strip()
                            if len(part) > 8 and _ORPHAN_KWDS.search(part):
                                add_candidate(part, date_str)

        # Scan HISTORY.md for RIBS/brainstorm lines
        if HISTORY_FILE.exists():
            hist_date = "history"
            for line in HISTORY_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
                dm = re.match(r'^###\s+(\d{4}-\d{2}-\d{2})', line)
                if dm:
                    hist_date = dm.group(1)
                    continue
                if _HIST_KWDS.search(line) and len(line.strip()) > 15:
                    add_candidate(line.strip()[:200], hist_date)

        orphaned = []
        for key, val in candidates.items():
            if not is_covered(val["text"]):
                days_since = 0
                try:
                    days_since = (today - datetime.date.fromisoformat(val["date_first"])).days
                except Exception:
                    pass
                orphaned.append({
                    "text": val["text"],
                    "date_first": val["date_first"],
                    "days_since": days_since,
                })
        return orphaned

    def generate_requeue_block(self, lost_items, stuck_items):
        lines = [
            "Read STATUS.md and INDEX.md. This is a CLACR (CLAC Request) — re-run incomplete work.",
            "",
        ]
        combined = list(lost_items)
        for s in stuck_items:
            if s["item"] not in combined:
                combined.append(s["item"])
        if not combined:
            lines.append("No lost or stuck items found. All clear.")
        else:
            for i, item in enumerate(combined, 1):
                lines.append(f"{i}. {item}")
        return "\n".join(lines)

    def check_file_integrity(self) -> dict:
        """HC-05: SHA-256 baseline for loop_manager.py and aafl_core.py."""
        targets = [ROOT / "loop_manager.py", ROOT / "aafl_core.py"]
        hashes_file = ROOT / "data" / "file_hashes.json"
        current = {}
        for f in targets:
            current[f.name] = hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None

        if not hashes_file.exists():
            hashes_file.parent.mkdir(exist_ok=True)
            hashes_file.write_text(json.dumps(current, indent=2), encoding="utf-8")
            return {"name": "HC-05 File Integrity", "status": "PASS",
                    "detail": f"Baseline written for: {list(current.keys())}"}

        try:
            baseline = json.loads(hashes_file.read_text(encoding="utf-8"))
        except Exception as exc:
            return {"name": "HC-05 File Integrity", "status": "FAIL",
                    "detail": f"Could not read baseline: {exc}"}

        mismatches = [f for f, h in current.items() if baseline.get(f) != h]
        if mismatches:
            return {"name": "HC-05 File Integrity", "status": "WARN",
                    "detail": f"Hash mismatch (changed): {', '.join(mismatches)}"}
        return {"name": "HC-05 File Integrity", "status": "PASS",
                "detail": "All hashes match baseline"}

    def check_loop_output_cap(self) -> dict:
        """HC-07: If aafl_output/ > 50 files, move oldest 10 to aafl_output/archive/."""
        out_dir = ROOT / "aafl_output"
        if not out_dir.exists():
            return {"name": "HC-07 Loop Output Cap", "status": "PASS",
                    "detail": "aafl_output/ does not exist"}
        files = sorted(
            [f for f in out_dir.iterdir() if f.is_file()],
            key=lambda f: f.stat().st_mtime,
        )
        count = len(files)
        if count <= 50:
            return {"name": "HC-07 Loop Output Cap", "status": "PASS",
                    "detail": f"{count} files — under cap"}
        archive = out_dir / "archive"
        archive.mkdir(exist_ok=True)
        archived = 0
        for f in files[:10]:
            try:
                f.rename(archive / f.name)
                archived += 1
            except Exception:
                pass
        return {"name": "HC-07 Loop Output Cap", "status": "PASS",
                "detail": f"Archived {archived} oldest files to aafl_output/archive/ ({count} total before)"}

    def check_watchdog_wiring(self) -> dict:
        """HC-10: Confirm aafl_watchdog and cost_guard are both imported and called in loop_manager.py."""
        lm = ROOT / "loop_manager.py"
        if not lm.exists():
            return {"name": "HC-10 Watchdog Wiring", "status": "FAIL",
                    "detail": "loop_manager.py not found"}
        text = lm.read_text(encoding="utf-8", errors="replace")
        checks = {
            "aafl_watchdog import": bool(re.search(r'from\s+aafl_watchdog\b|import\s+aafl_watchdog\b', text)),
            "aafl_watchdog call":   bool(re.search(r'_watchdog_run_cycle|_watchdog_check', text)),
            "cost_guard import":    bool(re.search(r'from\s+cost_guard\b|import\s+cost_guard\b', text)),
            "cost_guard call":      bool(re.search(r'CostGuard\s*\(|guard\.check|guard\.record', text)),
        }
        missing = [k for k, v in checks.items() if not v]
        if missing:
            return {"name": "HC-10 Watchdog Wiring", "status": "FAIL",
                    "detail": f"Missing: {', '.join(missing)}"}
        return {"name": "HC-10 Watchdog Wiring", "status": "PASS",
                "detail": "aafl_watchdog and cost_guard both imported and called"}

    def generate_report(self):
        sessions = self.scan_sesum_files()
        completed_items, lost_items, stuck_items = self.compare_to_status()
        orphaned_plans = self.detect_orphaned_plans()

        last_score = 0.0
        last_incomplete = []
        if sessions:
            last_score = self.completion_score(sessions[0])
            last_incomplete = sessions[0].get("incomplete", [])

        total_completed = sum(len(s.get("clac_completed", [])) for s in sessions)
        total_incomplete = sum(len(s.get("incomplete", [])) for s in sessions)
        total_tasks = total_completed + total_incomplete
        overall_pct = round((total_completed / total_tasks) * 100, 1) if total_tasks > 0 else 100.0

        requeue = self.generate_requeue_block(lost_items, [s["item"] for s in stuck_items])

        # ALP waste estimate
        total_incomplete_count = len(lost_items) + len(stuck_items) + len(orphaned_plans)
        estimated_pct = min(total_incomplete_count * 5.0, 90.0)
        sessions_below_80 = sum(1 for s in sessions if self.completion_score(s) < 80.0)
        if estimated_pct == 0:
            alp_msg = "No incomplete work detected — ALP preserved"
        else:
            alp_msg = (
                f"~{estimated_pct:.0f}% allowance estimated lost to incomplete work "
                f"across {sessions_below_80} session(s)"
            )
        alp_waste = {
            "incomplete_item_count": total_incomplete_count,
            "estimated_alp_wasted_pct": estimated_pct,
            "sessions_below_80pct": sessions_below_80,
            "alp_message": alp_msg,
        }

        system_checks = {
            "file_integrity":   self.check_file_integrity(),
            "loop_output_cap":  self.check_loop_output_cap(),
            "watchdog_wiring":  self.check_watchdog_wiring(),
        }
        for c in system_checks.values():
            icon = "✓" if c["status"] == "PASS" else ("⚠" if c["status"] == "WARN" else "✗")
            print(f"[WC] {icon} {c['name']}: {c['status']} — {c['detail']}")

        report = {
            "report_date": datetime.date.today().isoformat(),
            "sessions_scanned": len(sessions),
            "overall_completion_pct": overall_pct,
            "lost_work": lost_items,
            "stuck_items": stuck_items,
            "orphaned_plans": orphaned_plans,
            "alp_waste_estimate": alp_waste,
            "last_session_score": last_score,
            "last_session_incomplete": last_incomplete,
            "requeue_block": requeue,
            "system_checks": system_checks,
            "sessions": [
                {
                    "date": s.get("date", s["filename"]),
                    "filename": s["filename"],
                    "planned": len(s.get("clac_completed", [])) + len(s.get("incomplete", [])),
                    "completed": len(s.get("clac_completed", [])),
                    "score": self.completion_score(s),
                }
                for s in sessions
            ],
            "manual_findings": [],
        }

        WORK_REPORT.parent.mkdir(exist_ok=True)
        tmp = WORK_REPORT.with_suffix(".tmp")
        tmp.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(WORK_REPORT)
        return report


if __name__ == "__main__":
    wc = WorkChecker()
    report = wc.generate_report()
    print(json.dumps(report, indent=2))
