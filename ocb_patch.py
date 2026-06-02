"""
Apply phase-tracking + ocb_progress.json write to ocb_runner.py.
Must be run as a single script to avoid linter revert between steps.
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "ocb_runner.py"
text = TARGET.read_text(encoding="utf-8")

# ── Patch 1: add progress write to _write_status body ─────────────────────────
OLD_WS = '''def _write_status(status_obj: dict):
    OCB_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(OCB_STATUS_FILE) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(status_obj, f, indent=2)
    shutil.move(tmp, str(OCB_STATUS_FILE))'''

NEW_WS = '''def _write_status(status_obj: dict):
    OCB_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(OCB_STATUS_FILE) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(status_obj, f, indent=2)
    shutil.move(tmp, str(OCB_STATUS_FILE))
    # Write compact progress file for MCC progress bar polling
    ph_list = status_obj.get("phases", [])
    if ph_list:
        try:
            ph_total = len(ph_list)
            ph_done = sum(1 for p in ph_list if (p.get("status") or "").upper() in ("DONE","FAILED","SKIPPED"))
            ph_cur = status_obj.get("current_phase", 0)
            ph_cur_name = next((p.get("phase_name","") for p in ph_list if p.get("phase_num") == ph_cur), "")
            prog = {
                "phases": [{"phase_num": p.get("phase_num"), "phase_name": p.get("phase_name",""),
                            "status": (p.get("status") or "PENDING").upper(),
                            "tasks_done": sum(1 for t in p.get("tasks",[]) if (t.get("status") or "").upper() in ("DONE","FAILED","SKIPPED")),
                            "tasks_total": len(p.get("tasks",[]))} for p in ph_list],
                "phase_current": ph_cur, "phase_name": ph_cur_name, "phase_total": ph_total,
                "percent": round(ph_done / ph_total * 100) if ph_total else 0,
                "status": status_obj.get("status", "RUNNING"),
                "current_stage": status_obj.get("current_stage", ""),
                "mot_score": status_obj.get("mot_score", ""),
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
            pf = OCB_STATUS_FILE.parent / "ocb_progress.json"
            ptmp = str(pf) + ".tmp"
            with open(ptmp, "w", encoding="utf-8") as pf_:
                json.dump(prog, pf_, indent=2)
            shutil.move(ptmp, str(pf))
        except Exception:
            pass'''

if OLD_WS in text:
    text = text.replace(OLD_WS, NEW_WS)
    print("[PATCH 1] _write_status: progress write added")
else:
    print("[PATCH 1] WARN: _write_status old string not found — skipping")

# ── Patch 2: add phases + current_phase + mot_score to run_safe obj ───────────
OLD_OBJ = '''        "rollback_available": False, "error": "", "stash_ref": None,
    }
    _write_status(obj)

    def _sl(msg: str):'''

NEW_OBJ = '''        "rollback_available": False, "error": "", "stash_ref": None,
        "current_phase": 0, "mot_score": "",
        "phases": [
            {"phase_num": p2["phase"], "phase_name": p2.get("phase_name",""), "status": "PENDING",
             "tasks": [{"num": t2["num"], "text": t2["text"][:80], "status": "PENDING"} for t2 in p2.get("tasks",[])]}
            for p2 in parsed
        ],
    }
    _write_status(obj)

    def _sl(msg: str):'''

if OLD_OBJ in text:
    text = text.replace(OLD_OBJ, NEW_OBJ)
    print("[PATCH 2] run_safe obj: phases + current_phase added")
else:
    print("[PATCH 2] WARN: old obj string not found — skipping")

# ── Patch 3: change `for phase in parsed:` to enumerate + phase tracking ──────
OLD_LOOP = '''        print(f"[THREAD] About to execute phase 1")
        for phase in parsed:
            if failed_reason:
                break
            if _is_aborted():
                obj["status"] = "CANCELLED"
                _sl(f"\\u26d4 Aborted by user before Phase {phase['phase']}: {phase.get('phase_name','')}")
                _write_status(obj)
                break
            set_status("phase_running", f"Phase {phase['phase']}: {phase.get('phase_name','')}")
            _sl(f"Phase {phase['phase']}: {phase.get('phase_name','')}")'''

NEW_LOOP = '''        print(f"[THREAD] About to execute phase 1")
        for ph_idx, phase in enumerate(parsed):
            if failed_reason:
                if ph_idx < len(obj["phases"]):
                    obj["phases"][ph_idx]["status"] = "SKIPPED"
                break
            if _is_aborted():
                obj["status"] = "CANCELLED"
                _sl(f"\\u26d4 Aborted by user before Phase {phase['phase']}: {phase.get('phase_name','')}")
                _write_status(obj)
                break
            obj["current_phase"] = phase["phase"]
            if ph_idx < len(obj["phases"]):
                obj["phases"][ph_idx]["status"] = "RUNNING"
            set_status("phase_running", f"Phase {phase['phase']}: {phase.get('phase_name','')}")
            _sl(f"Phase {phase['phase']}: {phase.get('phase_name','')}")'''

# Try with actual unicode character
OLD_LOOP2 = '''        print(f"[THREAD] About to execute phase 1")
        for phase in parsed:
            if failed_reason:
                break
            if _is_aborted():
                obj["status"] = "CANCELLED"
                _sl(f"⛔ Aborted by user before Phase {phase['phase']}: {phase.get('phase_name','')}")
                _write_status(obj)
                break
            set_status("phase_running", f"Phase {phase['phase']}: {phase.get('phase_name','')}")
            _sl(f"Phase {phase['phase']}: {phase.get('phase_name','')}")'''

NEW_LOOP2 = '''        print(f"[THREAD] About to execute phase 1")
        for ph_idx, phase in enumerate(parsed):
            if failed_reason:
                if ph_idx < len(obj["phases"]):
                    obj["phases"][ph_idx]["status"] = "SKIPPED"
                break
            if _is_aborted():
                obj["status"] = "CANCELLED"
                _sl(f"⛔ Aborted by user before Phase {phase['phase']}: {phase.get('phase_name','')}")
                _write_status(obj)
                break
            obj["current_phase"] = phase["phase"]
            if ph_idx < len(obj["phases"]):
                obj["phases"][ph_idx]["status"] = "RUNNING"
            set_status("phase_running", f"Phase {phase['phase']}: {phase.get('phase_name','')}")
            _sl(f"Phase {phase['phase']}: {phase.get('phase_name','')}")'''

if OLD_LOOP in text:
    text = text.replace(OLD_LOOP, NEW_LOOP)
    print("[PATCH 3a] for loop: enumerate + phase tracking added")
elif OLD_LOOP2 in text:
    text = text.replace(OLD_LOOP2, NEW_LOOP2)
    print("[PATCH 3b] for loop: enumerate + phase tracking added (unicode variant)")
else:
    print("[PATCH 3] WARN: for phase loop not found — skipping")

# ── Patch 4: add phase done/fail status after phase task loop ─────────────────
OLD_PHASE_END = '''            print(f"[OCB THREAD] Phase {phase.get('phase', '')} complete")

        if not html_was_edited:'''

NEW_PHASE_END = '''            if ph_idx < len(obj["phases"]):
                obj["phases"][ph_idx]["status"] = "FAILED" if failed_reason else "DONE"
            _write_status(obj)
            print(f"[OCB THREAD] Phase {phase.get('phase', '')} complete")

        if not html_was_edited:'''

if OLD_PHASE_END in text:
    text = text.replace(OLD_PHASE_END, NEW_PHASE_END)
    print("[PATCH 4] phase end: status DONE/FAILED added")
else:
    print("[PATCH 4] WARN: phase end marker not found — skipping")

# ── Patch 5: add obj["mot_score"] updates ─────────────────────────────────────
OLD_SKIP = '''                obj["check_results"]["D_mot"] = {"ok": True, "score": mot_score, "skipped": True}
                _sl(f"CHECK D (MOT): SKIPPED'''

NEW_SKIP = '''                obj["check_results"]["D_mot"] = {"ok": True, "score": mot_score, "skipped": True}
                obj["mot_score"] = mot_score
                _sl(f"CHECK D (MOT): SKIPPED'''

OLD_MOT = '''                obj["check_results"]["D_mot"] = {"ok": mot_ok, "score": mot_score}
                _sl(f"CHECK D (MOT):'''

NEW_MOT = '''                obj["check_results"]["D_mot"] = {"ok": mot_ok, "score": mot_score}
                obj["mot_score"] = mot_score
                _sl(f"CHECK D (MOT):'''

if OLD_SKIP in text:
    text = text.replace(OLD_SKIP, NEW_SKIP)
    print("[PATCH 5a] mot_score skip branch: added")
if OLD_MOT in text:
    text = text.replace(OLD_MOT, NEW_MOT)
    print("[PATCH 5b] mot_score run branch: added")

TARGET.write_text(text, encoding="utf-8")
print(f"\n[DONE] {TARGET.name} patched.")

import subprocess, sys
r = subprocess.run(["python", "-c", f"import ast; ast.parse(open(r'{TARGET}', encoding='utf-8').read()); print('syntax OK')"],
                   capture_output=True, text=True, cwd=str(HERE))
print(r.stdout.strip() or r.stderr.strip())
