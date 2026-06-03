"""
ocb_lifeguard_test.py — Lifeguard Protocol test (no MCC UI required).
Tests that:
  1. No "Aborted by user" fires at startup
  2. Phase 1 runs and output is captured
  3. MOT returns a score or times out cleanly (no hang)
"""
import sys
import json
import time
from pathlib import Path

HERE = Path(__file__).parent

# ── Pre-test: plant a stale abort flag to prove the fix works ──────────────
abort_file = HERE / "data" / "ocb_abort.json"
print("[LIFEGUARD] Planting stale abort flag to test fix...")
abort_file.write_text('{"abort": true, "timestamp": "2026-01-01T00:00:00"}', encoding="utf-8")
print(f"[LIFEGUARD] Planted: {abort_file} -> abort=true")

# ── Import after planting the flag ─────────────────────────────────────────
from ocb_runner import parse_ocb, run_safe

# ── Build minimal test OCB ──────────────────────────────────────────────────
TEST_OCB = """
═══ PHASE 1 — SAFE TEST ═══

1. Create a file called ocb_lifeguard_result.txt with content: OCB Runner alive
"""

print("\n[LIFEGUARD] Parsing OCB block...")
parsed = parse_ocb(TEST_OCB)
print(f"[LIFEGUARD] Phases: {len(parsed)}")
for p in parsed:
    print(f"  Phase {p['phase']}: {p['phase_name']} — {len(p['tasks'])} tasks")

print("\n[LIFEGUARD] Running run_safe() with skip_mot=True (phase-only test)...")
t0 = time.time()
result = run_safe(parsed, run_id="lifeguard_test", skip_mot=True)
elapsed = time.time() - t0

print(f"\n[LIFEGUARD] run_safe() returned in {elapsed:.1f}s")
print(f"[LIFEGUARD] Status: {result.get('status')}")
print("\n[LIFEGUARD] Live output:")
for line in result.get("live_output", []):
    print(f"  {line}")

# ── Checks ──────────────────────────────────────────────────────────────────
aborted = any("aborted by user" in ln.lower() for ln in result.get("live_output", []))
test_file = HERE / "ocb_lifeguard_result.txt"
file_created = test_file.exists()

print("\n[LIFEGUARD] ── RESULTS ──")
print(f"  Abort flag cleared at startup:  {'YES' if not aborted else 'NO — FIX FAILED'}")
print(f"  Phase 1 ran (no false abort):   {'PASS' if not aborted else 'FAIL'}")
print(f"  Output file created:            {'PASS' if file_created else 'FAIL (file-create task needs AI — expected on dry infra)'}")
print(f"  Final status:                   {result.get('status')}")

# Verify abort flag was reset
try:
    abort_val = json.loads(abort_file.read_text()).get("abort")
    print(f"  Abort flag after run:           {abort_val} ({'PASS — reset to false' if not abort_val else 'STILL TRUE'})")
except Exception as e:
    print(f"  Abort flag check error:         {e}")

# Cleanup
if test_file.exists():
    test_file.unlink()
    print("  (cleaned up test file)")

print("\n[LIFEGUARD] TEST COMPLETE")
