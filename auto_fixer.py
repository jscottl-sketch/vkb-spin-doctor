"""
auto_fixer.py — OCB-B Auto-Fix Engine
Matches self-health failures against solution_database.json and proposes or
executes fixes.  Writes proposals to data/fix_proposals.json and logs results
to data/fix_history.json and data/health.db.
"""

import datetime
import json
import re
import sqlite3
import subprocess
import uuid
from pathlib import Path

HERE             = Path(__file__).parent
SOLUTION_DB      = HERE / "data" / "solution_database.json"
HEALTH_DB        = HERE / "data" / "health.db"
PROPOSALS_FILE   = HERE / "data" / "fix_proposals.json"
HISTORY_FILE     = HERE / "data" / "fix_history.json"
STUCK_INBOX_FILE = HERE / "stuck_inbox.json"


def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class AutoFixer:

    def __init__(self):
        raw = _load_json(SOLUTION_DB, {"solutions": []})
        self.solutions: list = raw.get("solutions", [])
        self.db = self._init_db()

    # ── DB ────────────────────────────────────────────────────────────────────

    def _init_db(self):
        if not HEALTH_DB.parent.exists():
            HEALTH_DB.parent.mkdir(parents=True, exist_ok=True)
        if not HEALTH_DB.exists():
            return None
        try:
            conn = sqlite3.connect(str(HEALTH_DB), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception:
            return None

    def _log_to_db(self, element_id: str, fix_id: str, success: bool):
        if not self.db:
            return
        try:
            self.db.execute(
                """UPDATE health_results SET auto_fix_attempted=1, auto_fix_id=?, auto_fix_success=?
                   WHERE element_id=?
                   AND id=(SELECT MAX(id) FROM health_results WHERE element_id=?)""",
                (fix_id, int(success), element_id, element_id)
            )
            self.db.commit()
        except Exception:
            pass

    # ── Solution matching ─────────────────────────────────────────────────────

    def match_solution(self, error_message: str) -> dict | None:
        """Return the first solution whose match_pattern matches error_message."""
        if not error_message:
            return None
        best = None
        for sol in self.solutions:
            pattern = sol.get("match_pattern", "")
            if not pattern:
                continue
            try:
                if re.search(pattern, error_message, re.IGNORECASE):
                    if best is None or sol.get("success_rate", 0) > best.get("success_rate", 0):
                        best = sol
            except re.error:
                pass
        return best

    # ── Proposal + execution ──────────────────────────────────────────────────

    def propose_fix(self, element_id: str, error_message: str) -> dict:
        """
        Match a solution and either:
          - queue a proposal for user approval (user_approval_required=True)
          - auto-execute the fix (user_approval_required=False)
          - escalate to Stuck Inbox (no match found)
        """
        solution = self.match_solution(error_message)

        if solution is None:
            self._escalate(element_id, error_message)
            return {"action": "escalated_to_stuck_inbox"}

        fix_id = str(uuid.uuid4())[:8]
        proposal = {
            "fix_id":               fix_id,
            "element_id":           element_id,
            "error":                error_message,
            "proposed_fix":         solution.get("name", solution["id"]),
            "solution_id":          solution["id"],
            "proposed_at":          _now(),
            "status":               "awaiting_approval",
            "user_approval_required": solution.get("user_approval_required", True),
        }

        if solution.get("user_approval_required", True):
            proposals = _load_json(PROPOSALS_FILE, [])
            proposals.append(proposal)
            _save_json(PROPOSALS_FILE, proposals)
            return {"action": "awaiting_approval", "fix": solution, "fix_id": fix_id}

        # Auto-execute
        success = self.execute_fix(fix_id, solution=solution)
        return {"action": "auto_fixed", "fix": solution, "success": success, "fix_id": fix_id}

    def execute_fix(self, fix_id: str, solution: dict | None = None) -> bool:
        """Run all fix_steps for a solution; log result to history and DB."""
        if solution is None:
            proposals = _load_json(PROPOSALS_FILE, [])
            proposal  = next((p for p in proposals if p.get("fix_id") == fix_id), None)
            if not proposal:
                return False
            sol_id   = proposal.get("solution_id", "")
            solution = next((s for s in self.solutions if s.get("id") == sol_id), None)
            if not solution:
                return False
            element_id = proposal.get("element_id", "")
        else:
            element_id = ""

        stdout_acc = ""
        stderr_acc = ""
        success    = False
        try:
            for step in solution.get("fix_steps", []):
                result = subprocess.run(
                    step, shell=True, capture_output=True, text=True,
                    cwd=str(HERE), timeout=60
                )
                stdout_acc += result.stdout
                stderr_acc += result.stderr
            success = True
        except subprocess.TimeoutExpired as exc:
            stderr_acc += f"\n[TIMEOUT] {exc}"
        except Exception as exc:
            stderr_acc += f"\n[ERROR] {exc}"

        # Update proposal status
        proposals = _load_json(PROPOSALS_FILE, [])
        for p in proposals:
            if p.get("fix_id") == fix_id:
                p["status"]     = "applied" if success else "failed"
                p["applied_at"] = _now()
                break
        _save_json(PROPOSALS_FILE, proposals)

        # Write history
        history = _load_json(HISTORY_FILE, [])
        history.insert(0, {
            "fix_id":     fix_id,
            "element_id": element_id,
            "fix_name":   solution.get("name", fix_id),
            "success":    success,
            "applied_at": _now(),
            "stdout":     stdout_acc[:500],
            "stderr":     stderr_acc[:500],
        })
        _save_json(HISTORY_FILE, history[:200])

        if element_id:
            self._log_to_db(element_id, fix_id, success)

        return success

    def get_pending_proposals(self) -> list:
        proposals = _load_json(PROPOSALS_FILE, [])
        return [p for p in proposals if p.get("status") == "awaiting_approval"]

    # ── Escalation ────────────────────────────────────────────────────────────

    def _escalate(self, element_id: str, error_message: str):
        try:
            inbox = _load_json(STUCK_INBOX_FILE, [])
            if not isinstance(inbox, list):
                inbox = []
            entry_id = f"af_{element_id}_{_now()[:10]}"
            if not any(i.get("id") == entry_id for i in inbox):
                inbox.append({
                    "id":        entry_id,
                    "goal":      f"Auto-Fix: No solution found for element '{element_id}'",
                    "error":     error_message[:300],
                    "timestamp": _now(),
                    "severity":  "medium",
                    "source":    "auto_fixer",
                    "resolved":  False,
                })
                _save_json(STUCK_INBOX_FILE, inbox)
        except Exception:
            pass


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    af = AutoFixer()
    if len(sys.argv) >= 3 and sys.argv[1] == "test":
        el_id = sys.argv[2]
        err   = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "ConnectionRefusedError: port 8080"
        result = af.propose_fix(el_id, err)
        print(json.dumps(result, indent=2))
    else:
        pending = af.get_pending_proposals()
        print(f"[AutoFixer] Solutions loaded: {len(af.solutions)}")
        print(f"[AutoFixer] Pending proposals: {len(pending)}")
        for p in pending:
            print(f"  [{p['fix_id']}] {p['element_id']} — {p['proposed_fix']}")
