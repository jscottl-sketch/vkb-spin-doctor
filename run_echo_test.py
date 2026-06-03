"""
run_echo_test.py -- Drives OCB Runner echo test end to end.
Calls parse_ocb + run_safe synchronously; prints live log.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import ocb_runner

OCB_TEXT = """
═══ PHASE 1 — ECHO TEST ═══

1. Run Script: echo_test.py
"""

def main():
    print("[ECHO TEST] Parsing OCB block...", flush=True)
    parsed = ocb_runner.parse_ocb(OCB_TEXT)
    print(f"[ECHO TEST] Phases: {len(parsed)}", flush=True)
    for p in parsed:
        print(f"  Phase {p['phase']}: {p['phase_name']} -- {len(p['tasks'])} tasks", flush=True)
        for t in p["tasks"]:
            print(f"    {t['num']}. {t['text']}", flush=True)

    if not parsed or not parsed[0]["tasks"]:
        print("[ECHO TEST] FAIL -- no phases/tasks parsed", flush=True)
        sys.exit(1)

    run_id = "echo_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"\n[ECHO TEST] Calling run_safe(run_id={run_id}, skip_mot=False)...", flush=True)
    print("[ECHO TEST] Safety layer: git stash will fire if tree is dirty", flush=True)

    result = ocb_runner.run_safe(parsed, run_id=run_id, skip_mot=False)

    print(f"\n[ECHO TEST] --- RESULT ---", flush=True)
    print(f"[ECHO TEST] Status:      {result.get('status')}", flush=True)
    print(f"[ECHO TEST] MOT score:   {result.get('mot_score', '?')}", flush=True)
    print(f"[ECHO TEST] Files changed: {result.get('files_changed', [])}", flush=True)
    print(f"[ECHO TEST] Guard results: {result.get('guard_results', {})}", flush=True)

    print(f"\n[ECHO TEST] --- LIVE LOG ---", flush=True)
    for line in result.get("live_output", []):
        print(f"  {line}", flush=True)

    # Verify "OCB Runner alive" appears in the captured script output
    live_text = "\n".join(str(l) for l in result.get("live_output", []))
    echo_found = "OCB Runner alive" in live_text
    stash_fired = any("stash" in str(l).lower() for l in result.get("live_output", []))
    status_ok = result.get("status") in ("DONE", "PARTIAL")

    print(f"\n[ECHO TEST] --- VERDICT ---", flush=True)
    print(f"[ECHO TEST] 'OCB Runner alive' captured: {echo_found}", flush=True)
    print(f"[ECHO TEST] Safety layer (stash) fired: {stash_fired}", flush=True)
    print(f"[ECHO TEST] Status DONE/PARTIAL: {status_ok}", flush=True)

    overall = echo_found and status_ok
    print(f"[ECHO TEST] FINAL: {'PASS' if overall else 'FAIL'}", flush=True)
    sys.exit(0 if overall else 1)

if __name__ == "__main__":
    main()
