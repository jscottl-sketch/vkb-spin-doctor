"""
mccm_agent.py — Mission Control Center Master (MCCM)
Overseer agent. Reads pending requests from wccs_detective.py, approves
AI dispatches, or escalates to Scott.

Power levels:
  1 (default)  — Read, deduce, propose
  2            — Unlocked: memory_bank.db + health.db + 10+ session logs
  3            — Unlocked: AAFL has 10+ autonomous run records
  4 (future)   — Full autonomy with post-action reporting
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE      = Path(__file__).parent
DATA_DIR  = HERE / "data"

MCCM_PERMS         = DATA_DIR / "mccm_permissions.json"
INVESTIGATIONS_DIR = DATA_DIR / "mccm_investigations"
SESSION_LOGS_DIR   = HERE / "session_logs"
MEMORY_BANK_DB     = DATA_DIR / "memory_bank.db"
HEALTH_DB          = DATA_DIR / "health.db"
MORNING_REPORT     = HERE / "morning_report.md"
LOOP_OUTPUT_DIR    = HERE / "loop_output"

PYTHON = sys.executable


def _load_perms() -> dict:
    if MCCM_PERMS.exists():
        try:
            return json.loads(MCCM_PERMS.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "mccm_power_level": 1,
        "pending":          [],
        "approved":         [],
        "rejected":         [],
        "scott_interrupts": [],
        "last_cycle":       None,
    }


def _save_perms(perms: dict):
    DATA_DIR.mkdir(exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(DATA_DIR), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(perms, f, indent=2)
    os.replace(tmp, str(MCCM_PERMS))


def assess_power_level() -> int:
    """Calculate current MCCM power level 1-4."""
    level = 1

    has_memory = MEMORY_BANK_DB.exists()
    has_health = HEALTH_DB.exists()
    session_count = 0
    if SESSION_LOGS_DIR.exists():
        session_count = sum(1 for _ in SESSION_LOGS_DIR.iterdir())

    if has_memory and has_health and session_count >= 10:
        level = 2

    # Count AAFL autonomous run records
    aafl_runs = 0
    if MORNING_REPORT.exists():
        try:
            txt = MORNING_REPORT.read_text(encoding="utf-8", errors="replace")
            aafl_runs += txt.lower().count("score:")
        except Exception:
            pass
    if LOOP_OUTPUT_DIR.exists():
        aafl_runs += sum(1 for p in LOOP_OUTPUT_DIR.iterdir()
                        if p.suffix in (".txt", ".md") and "result" in p.name.lower())

    if level >= 2 and aafl_runs >= 10:
        level = 3

    # Level 4 is future — not unlocked yet
    perms = _load_perms()
    perms["mccm_power_level"] = level
    _save_perms(perms)
    return level


def check_pending_requests() -> tuple:
    """
    Returns (approvable list, escalation_needed list).
    Approvable = level_required <= current power level.
    """
    perms = _load_perms()
    power = perms.get("mccm_power_level", 1)
    approvable  = []
    escalations = []
    for req in perms.get("pending", []):
        if req.get("level_required", 2) <= power:
            approvable.append(req)
        else:
            escalations.append(req)
    return approvable, escalations


def approve_ai_dispatch(request_id: str) -> bool:
    """Move request from pending→approved and trigger chief_scout.py."""
    perms = _load_perms()
    pending = perms.get("pending", [])
    target  = next((r for r in pending if r.get("request_id") == request_id), None)
    if not target:
        print(f"[MCCM] Request {request_id} not found in pending list")
        return False

    # Move to approved
    perms["pending"]  = [r for r in pending if r.get("request_id") != request_id]
    target["approved_at"] = datetime.now().isoformat(timespec="seconds")
    perms.setdefault("approved", []).append(target)
    _save_perms(perms)

    # Dispatch to chief_scout.py
    INVESTIGATIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = INVESTIGATIONS_DIR / f"{request_id}.txt"
    desc     = target.get("description", "unknown gap")
    try:
        result = subprocess.run(
            [PYTHON, str(HERE / "chief_scout.py"), desc],
            capture_output=True, text=True, timeout=120, cwd=str(HERE),
        )
        out_file.write_text(
            result.stdout + ("\n[STDERR]\n" + result.stderr if result.stderr else ""),
            encoding="utf-8",
        )
        print(f"✅ MCCM approved dispatch for request {request_id}")
        return True
    except Exception as exc:
        out_file.write_text(f"[ERROR] chief_scout dispatch failed: {exc}", encoding="utf-8")
        print(f"[MCCM] Dispatch error for {request_id}: {exc}")
        return False


def raise_scott_interrupt(reason: str, urgency: str = "normal"):
    """Raise a Scott interrupt — log to permissions file + try Stuck Inbox API."""
    perms = _load_perms()
    entry = {
        "reason":    reason,
        "urgency":   urgency,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "status":    "PENDING_SCOTT",
    }
    perms.setdefault("scott_interrupts", []).append(entry)
    _save_perms(perms)

    # Try to POST to Stuck Inbox endpoint
    try:
        import urllib.request
        payload = json.dumps({
            "severity":    "high",
            "description": "MCCM ALERT: " + reason,
        }).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:5000/api/stuck/add",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass  # Server may not be running

    print(f"🚨 MCCM has raised a Scott interrupt: {reason}")
    print("Check MCC Stuck Inbox or run: python mccm_agent.py --alerts")


def get_overview():
    """Print a formatted summary of project state from MCCM perspective."""
    perms = _load_perms()
    power = perms.get("mccm_power_level", 1)

    print("=== MCCM OVERVIEW ===")
    print(f"Power Level: {power}/4")
    print()

    # STATUS.md first 30 lines
    status_path = HERE / "STATUS.md"
    if status_path.exists():
        lines = status_path.read_text(encoding="utf-8", errors="replace").splitlines()[:30]
        print("--- STATUS.md (first 30 lines) ---")
        for line in lines:
            print(line)
        print()

    # Latest detective report
    today = datetime.now().strftime("%Y%m%d")
    report_path = DATA_DIR / f"detective_report_{today}.json"
    if not report_path.exists():
        # Find any recent one
        reports = sorted(DATA_DIR.glob("detective_report_*.json"), reverse=True)
        report_path = reports[0] if reports else None

    if report_path and report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            print("--- Latest Detective Report ---")
            print(f"CONFIRMED: {len(report.get('CONFIRMED', {}))}")
            print(f"UNCERTAIN: {len(report.get('UNCERTAIN', {}))}")
            print(f"UNKNOWN gaps: {len(report.get('UNKNOWN', []))}")
            print(f"Generated: {report.get('generated_at', '?')}")
            print()
        except Exception:
            pass

    # Pending requests
    pending = perms.get("pending", [])
    approved = perms.get("approved", [])
    interrupts = [i for i in perms.get("scott_interrupts", []) if i.get("status") == "PENDING_SCOTT"]
    print(f"Pending requests: {len(pending)}")
    print(f"Approved this session: {len(approved)}")
    print(f"Scott interrupts pending: {len(interrupts)}")


def main():
    power = assess_power_level()
    print(f"MCCM Power Level: {power}/4")

    approvable, escalations = check_pending_requests()

    approved_count  = 0
    escalated_count = 0
    scott_count     = 0

    for req in approvable:
        if approve_ai_dispatch(req["request_id"]):
            approved_count += 1

    for req in escalations:
        escalated_count += 1
        if req.get("urgency") == "high":
            raise_scott_interrupt(req.get("description", "Unknown gap"), urgency="high")
            scott_count += 1

    # Update last_cycle
    perms = _load_perms()
    perms["last_cycle"] = datetime.now().isoformat(timespec="seconds")
    _save_perms(perms)

    print(f"MCCM cycle complete. Approved: {approved_count}. Escalated: {escalated_count}. Scott alerts: {scott_count}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCCM Agent")
    parser.add_argument("--run",      action="store_true", help="Full MCCM cycle")
    parser.add_argument("--overview", action="store_true", help="Show project overview")
    parser.add_argument("--alerts",   action="store_true", help="Show pending Scott interrupts")
    parser.add_argument("--power",    action="store_true", help="Print power level only")
    args = parser.parse_args()

    if args.power:
        lvl = assess_power_level()
        print(f"MCCM Power Level: {lvl}/4")
    elif args.overview:
        assess_power_level()
        get_overview()
    elif args.alerts:
        perms = _load_perms()
        interrupts = [i for i in perms.get("scott_interrupts", []) if i.get("status") == "PENDING_SCOTT"]
        print(f"=== SCOTT INTERRUPTS ({len(interrupts)} pending) ===")
        for i in interrupts:
            print(f"[{i.get('urgency','?').upper()}] {i.get('timestamp','?')} — {i.get('reason','?')}")
    else:
        main()
