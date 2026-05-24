"""
test_tier3.py — Tier 3 tests for provider_health.py + mcc_server.py
Features 9-10: Cost Logger, MCC Status Panel
"""
import csv
import json
import datetime
import http.client
import subprocess
import sys
import time
import traceback
from pathlib import Path

import provider_health as ph

HEALTH_DIR   = ph.HEALTH_DIR
COST_LOG     = ph.COST_LOG
LATEST_JSON  = ph.LATEST_JSON
RESULTS_FILE = HEALTH_DIR / "tier3_results.json"
HERE         = Path(__file__).parent


# ── Feature 9: Cost Logger ────────────────────────────────────────────────────

def test_f9_cost_logger():
    print("\n[F9] Cost Logger — cost_log.csv write")

    # Ensure health dir exists
    HEALTH_DIR.mkdir(exist_ok=True)

    # Log a test entry
    test_provider = "_tier3_test_provider"
    ph._log_cost(test_provider, 2.345, 0.00012, True)
    ph._log_cost(test_provider, 0.0,   0.0,     False)

    # Verify file exists
    assert COST_LOG.exists(), f"cost_log.csv not created at {COST_LOG}"

    # Verify headers
    with open(COST_LOG, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected_headers = {"timestamp", "provider_name", "response_time_seconds",
                             "estimated_cost_usd", "success"}
        assert expected_headers.issubset(set(reader.fieldnames or [])), \
            f"Missing headers. Got: {reader.fieldnames}"
        rows = list(reader)

    # Find our test rows
    test_rows = [r for r in rows if r["provider_name"] == test_provider]
    assert len(test_rows) >= 2, f"Expected 2+ rows for {test_provider}, got {len(test_rows)}"

    ok_rows   = [r for r in test_rows if r["success"] == "true"]
    fail_rows = [r for r in test_rows if r["success"] == "false"]
    assert ok_rows,   "No successful row logged"
    assert fail_rows, "No failed row logged"

    # Verify append (not overwrite) — size must grow
    size_before = COST_LOG.stat().st_size
    ph._log_cost(test_provider, 1.0, 0.0, True)
    size_after = COST_LOG.stat().st_size
    assert size_after > size_before, "cost_log.csv was overwritten instead of appended"

    print(f"  cost_log.csv exists: YES")
    print(f"  Headers correct: YES")
    print(f"  Rows logged for test provider: {len(test_rows)}")
    print(f"  Append verified: size {size_before} -> {size_after}")
    print("  F9: PASS")
    return "PASS"


# ── Feature 9 + 10: Full health run writes cost_log + latest_health.json ──────

def test_f9_f10_full_run():
    print("\n[F9+F10] Full health run — verify both files written")

    # Run a health check (uses cached results from tier1 if fast, else re-runs)
    results = ph.run_health_checks()

    # cost_log.csv must exist
    assert COST_LOG.exists(), "cost_log.csv missing after health check run"

    # latest_health.json must exist
    assert LATEST_JSON.exists(), f"latest_health.json missing at {LATEST_JSON}"

    # Validate JSON structure
    with open(LATEST_JSON, encoding="utf-8") as f:
        data = json.load(f)

    assert "generated_at" in data, "latest_health.json missing generated_at"
    assert "providers" in data, "latest_health.json missing providers"
    assert isinstance(data["providers"], list), "providers must be a list"

    for p in data["providers"]:
        for key in ("id", "label", "status", "score", "response_time", "quality_pass"):
            assert key in p, f"provider entry missing key: {key}"

    print(f"  cost_log.csv:        OK ({COST_LOG.stat().st_size} bytes)")
    print(f"  latest_health.json:  OK ({LATEST_JSON.stat().st_size} bytes)")
    print(f"  providers in JSON:   {len(data['providers'])}")
    print(f"  generated_at:        {data['generated_at']}")
    return "PASS"


# ── Feature 10: /health-status endpoint ───────────────────────────────────────

def test_f10_endpoint():
    print("\n[F10] /health-status endpoint — start server, hit endpoint")

    # Start mcc_server.py in background
    server_proc = None
    try:
        server_proc = subprocess.Popen(
            [sys.executable, str(HERE / "mcc_server.py")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd=str(HERE),
        )
        # Give server 3 seconds to start
        time.sleep(3)

        # Check process is still running
        if server_proc.poll() is not None:
            out, err = server_proc.communicate(timeout=2)
            raise RuntimeError(f"Server exited early: {err[:200]}")

        # Hit the endpoint
        conn = http.client.HTTPConnection("localhost", 8080, timeout=10)
        conn.request("GET", "/health-status")
        resp = conn.getresponse()
        body = resp.read().decode("utf-8")
        conn.close()

        assert resp.status == 200, f"Expected HTTP 200, got {resp.status}"

        data = json.loads(body)
        assert "providers" in data, "Response missing 'providers' key"

        print(f"  HTTP status: {resp.status}")
        print(f"  providers in response: {len(data['providers'])}")
        print(f"  generated_at: {data.get('generated_at', 'N/A')}")
        print("  F10: PASS")
        return "PASS"

    except Exception as exc:
        print(f"  F10: FAIL — {exc}")
        traceback.print_exc()
        return "FAIL"
    finally:
        if server_proc and server_proc.poll() is None:
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()


# ── Main ──────────────────────────────────────────────────────────────────────

def run_tests():
    HEALTH_DIR.mkdir(exist_ok=True)
    print()
    print("=" * 60)
    print("  TIER 3 TESTS")
    print("=" * 60)

    test_results = {}
    all_pass = True

    for name, fn in [("F9_cost_logger",    test_f9_cost_logger),
                     ("F9F10_full_run",    test_f9_f10_full_run),
                     ("F10_endpoint",      test_f10_endpoint)]:
        try:
            r = fn()
            test_results[name] = r
            if r != "PASS":
                all_pass = False
        except Exception as exc:
            print(f"  {name}: FAIL — {exc}")
            traceback.print_exc()
            test_results[name] = "FAIL"
            all_pass = False

    print()
    print("=" * 60)
    tier_result = "TIER 3 PASS" if all_pass else "TIER 3 FAIL"
    print(f"  {tier_result}")
    if not all_pass:
        failed = [k for k, v in test_results.items() if v != "PASS"]
        print(f"  Failed: {failed}")
    print("=" * 60)
    print()

    output = {
        "timestamp":   datetime.datetime.now().isoformat(),
        "tier_result": tier_result,
        "tests":       test_results,
    }
    RESULTS_FILE.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"  Results saved to {RESULTS_FILE}")
    print()

    return tier_result


if __name__ == "__main__":
    result = run_tests()
    if "FAIL" in result:
        sys.exit(1)
