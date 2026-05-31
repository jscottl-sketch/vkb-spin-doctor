"""
clacr_protocol.py — CLACR (MCC↔CLACH) Language Protocol
Parses CLACH shorthand messages into MCC task objects and formats results back.

TASK TYPES: BUILD, FIX, CHECK, RESEARCH, SAVE, REVIEW
PRIORITY:   1 (low) → 5 (critical)
"""

import re
import uuid
import datetime
from typing import Optional


_TASK_TYPES = {"BUILD", "FIX", "CHECK", "RESEARCH", "SAVE", "REVIEW"}

_PRIORITY_KEYWORDS = {
    "critical": 5, "urgent": 5, "asap": 5,
    "high": 4, "important": 4,
    "medium": 3, "normal": 3,
    "low": 2, "minor": 2,
    "backlog": 1, "later": 1,
}

_COMPONENT_PATTERNS = [
    (r'\b(mission_control\.html|mcc\.html)\b', "mission_control.html"),
    (r'\b(mcc_server\.py)\b', "mcc_server.py"),
    (r'\b(aafl_core\.py)\b', "aafl_core.py"),
    (r'\b(loop_manager\.py)\b', "loop_manager.py"),
    (r'\b(aafl_wccs\.py)\b', "aafl_wccs.py"),
    (r'\b(ocb_runner\.py)\b', "ocb_runner.py"),
    (r'\b(hitsav|wccs)\b', "HITSAV tab"),
    (r'\b(ocb.runner)\b', "OCB Runner"),
    (r'\b(health.suite)\b', "Health Suite"),
    (r'\b(llow)\b', "LLOW"),
    (r'\b(kanban)\b', "Kanban"),
    (r'\b(aafl.control)\b', "AAFL Control"),
]

_SAFE_TARGETS = {
    "mission_control.html", "mcc_server.py", "aafl_core.py",
    "loop_manager.py", "aafl_wccs.py", "ocb_runner.py",
    "STATUS.md", "HISTORY.md", "ACCA.md",
    "HITSAV tab", "OCB Runner", "Health Suite", "LLOW",
    "Kanban", "AAFL Control",
}


class CLACRProtocol:

    def parse_clach_message(self, text: str) -> dict:
        """Extract task type, priority, target component from CLACH shorthand."""
        text = text.strip()
        task_type = "CHECK"
        for tt in _TASK_TYPES:
            if tt in text.upper():
                task_type = tt
                break

        priority = 3
        lower = text.lower()
        for kw, p in _PRIORITY_KEYWORDS.items():
            if kw in lower:
                priority = p
                break
        # Priority can also be stated as P1-P5
        pm = re.search(r'\bP([1-5])\b', text, re.IGNORECASE)
        if pm:
            priority = int(pm.group(1))

        target = "MCC"
        for pattern, name in _COMPONENT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                target = name
                break

        description = re.sub(
            r'\b(BUILD|FIX|CHECK|RESEARCH|SAVE|REVIEW|P[1-5]|critical|urgent|high|medium|low)\b',
            '', text, flags=re.IGNORECASE,
        ).strip()
        description = re.sub(r'\s{2,}', ' ', description).strip()

        return {
            "task_type":   task_type,
            "priority":    priority,
            "target":      target,
            "description": description or text,
            "raw":         text,
        }

    def format_for_mcc(self, parsed: dict) -> dict:
        """Convert parsed CLACH dict into an MCC task object."""
        return {
            "id":          str(uuid.uuid4())[:8],
            "type":        parsed["task_type"],
            "priority":    parsed["priority"],
            "target":      parsed["target"],
            "description": parsed["description"],
            "status":      "queued",
            "created_at":  datetime.datetime.now().isoformat(timespec="seconds"),
            "result":      None,
        }

    def format_response_for_clach(self, result: dict) -> str:
        """Convert MCC task result back to CLACH-readable format."""
        tid   = result.get("id", "?")
        ttype = result.get("type", "?")
        stat  = result.get("status", "?").upper()
        desc  = result.get("description", "")[:60]
        res   = result.get("result") or ""
        ts    = result.get("completed_at", result.get("created_at", ""))[:16]
        return (
            f"[CLACR|{tid}|{ttype}|{stat}] {desc}"
            + (f" → {str(res)[:80]}" if res else "")
            + (f" [{ts}]" if ts else "")
        )

    def validate_task(self, task: dict) -> tuple:
        """
        Check task is safe and within scope.
        Returns (ok: bool, reason: str).
        """
        ttype = task.get("type", "")
        if ttype not in _TASK_TYPES:
            return False, f"Unknown task type: {ttype}"
        priority = task.get("priority", 3)
        if not isinstance(priority, int) or not 1 <= priority <= 5:
            return False, f"Priority must be 1-5, got: {priority}"
        target = task.get("target", "")
        desc   = task.get("description", "")
        danger = ["rm -rf", "drop table", "delete from", "format c:", "shutdown"]
        for d in danger:
            if d in desc.lower():
                return False, f"Dangerous keyword detected: {d}"
        return True, "ok"
