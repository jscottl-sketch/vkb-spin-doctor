"""OCB Runner self-test — file creation + progress file check."""
import json, sys
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import ocb_runner as ocbr

test_ocb = """
Phase 1 --- Create Brain Test File

1. create a file ocb_brain_test.txt content: OCB Runner AI brain wired 2026-06-02
"""

print("[TEST] Parsing OCB block...")
parsed = ocbr.parse_ocb(test_ocb)
print(f"[TEST] Phases found: {len(parsed)}")
for p in parsed:
    print(f"  Phase {p['phase']}: {p['phase_name']} -- {len(p['tasks'])} task(s)")
    for t in p["tasks"]:
        print(f"    {t['num']}. {t['text']}")

tf = HERE / "ocb_brain_test.txt"
if tf.exists():
    tf.unlink()
    print("[TEST] Cleaned up pre-existing test file")

print("[TEST] Running run_safe(skip_mot=True)...")
run_id = "test_brain_" + datetime.now().strftime("%H%M%S")
result = ocbr.run_safe(parsed, run_id=run_id, skip_mot=True)
print(f"[TEST] Status: {result.get('status')}")
for line in (result.get("live_output") or [])[-15:]:
    print(" ", line)

pf = HERE / "data" / "ocb_progress.json"
if pf.exists():
    prog = json.loads(pf.read_text(encoding="utf-8"))
    print(f"[TEST] ocb_progress.json: {prog.get('percent')}% | status={prog.get('status')} | phases={len(prog.get('phases', []))}")
    print(f"[TEST] Phase list: {[(p['phase_name'], p['status']) for p in prog.get('phases', [])]}")
else:
    print("[TEST] FAIL -- ocb_progress.json NOT found")

if tf.exists():
    print(f"[TEST] PASS -- ocb_brain_test.txt created: {tf.read_text(encoding='utf-8').strip()!r}")
else:
    print("[TEST] FAIL -- ocb_brain_test.txt was NOT created")

print("[TEST] COMPLETE")
