"""
test_tier2.py — Tier 2 tests for provider_health.py
Features 6-8: Best Worker Picker, Reputation Score, Auto Retry
"""
import json
import datetime
import sqlite3
import traceback
from pathlib import Path

import provider_health as ph
from aafl_core import PROVIDERS

HEALTH_DIR   = ph.HEALTH_DIR
RESULTS_FILE = HEALTH_DIR / "tier2_results.json"

# ── Mock helpers ───────────────────────────────────────────────────────────────

def _mock_results():
    """Three fake provider results to test scoring and retry logic."""
    return [
        {"id": "mock_green",  "label": "Mock Green",  "tier": 2, "alive": True,
         "response_time": 3.0,  "speed_color": "GREEN",  "cooling": False,
         "quality_pass": True,  "quality_response": "4", "status": "GREEN",
         "error": None, "score": 100, "cost_usd": 0.0},
        {"id": "mock_yellow", "label": "Mock Yellow", "tier": 2, "alive": True,
         "response_time": 15.0, "speed_color": "YELLOW", "cooling": False,
         "quality_pass": False, "quality_response": "5", "status": "YELLOW",
         "error": None, "score": 40,  "cost_usd": 0.0},
        {"id": "mock_dead",   "label": "Mock Dead",   "tier": 3, "alive": False,
         "response_time": 0.0,  "speed_color": "DEAD",   "cooling": False,
         "quality_pass": False, "quality_response": "",  "status": "DEAD",
         "error": "timeout",    "score": 0,  "cost_usd": 0.0},
    ]


# ── Feature 6: Scoring ────────────────────────────────────────────────────────

def test_f6_scoring():
    print("\n[F6] Best Worker Picker — scoring logic")
    results = _mock_results()

    ranked = ph.rank_providers(results)

    # Dead provider must not appear
    ids = [r["id"] for r in ranked]
    assert "mock_dead" not in ids, "DEAD provider should not appear in ranking"

    # Order must be descending by score
    scores = [r["score"] for r in ranked]
    assert scores == sorted(scores, reverse=True), f"Not sorted descending: {scores}"

    # Green must be first
    assert ranked[0]["id"] == "mock_green", "Green (score=100) should be first"

    # Scoring formula verification
    green = results[0]
    speed_pts   = 40 if green["speed_color"] == "GREEN" else (20 if green["speed_color"] == "YELLOW" else 5)
    quality_pts = 40 if green["quality_pass"] else 0
    alive_pts   = 20
    expected_score = speed_pts + quality_pts + alive_pts
    assert green["score"] == expected_score, f"Score mismatch: got {green['score']} expected {expected_score}"

    print(f"  Ranked order: {[r['id'] for r in ranked]}")
    print(f"  Scores:       {[r['score'] for r in ranked]}")
    print("  F6: PASS")
    return "PASS"


# ── Feature 7: Reputation Table ───────────────────────────────────────────────

def test_f7_reputation():
    print("\n[F7] Reputation Score — table create + update")

    # Force table creation
    conn = ph._db_connect()
    ph._ensure_reputation_table(conn)
    conn.close()

    # Verify table exists
    conn = ph._db_connect()
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='provider_reputation'"
    ).fetchone()
    assert row is not None, "provider_reputation table not created"
    conn.close()

    # Run _update_reputation with mocks
    test_pid = "_test_ph_mock_green"
    mock = [{"id": test_pid, "label": "Test", "tier": 2, "alive": True,
             "response_time": 2.5, "status": "GREEN", "score": 100, "cost_usd": 0.0,
             "quality_pass": True}]
    ph._update_reputation(mock)

    # Check row was written
    conn = ph._db_connect()
    row = conn.execute(
        "SELECT * FROM provider_reputation WHERE provider_name=?", (test_pid,)
    ).fetchone()
    conn.close()
    assert row is not None, "reputation row not written"
    assert row["total_calls"] >= 1, "total_calls not incremented"

    # Run again — should increment
    ph._update_reputation(mock)
    conn = ph._db_connect()
    row2 = conn.execute(
        "SELECT * FROM provider_reputation WHERE provider_name=?", (test_pid,)
    ).fetchone()
    conn.close()
    assert row2["total_calls"] >= 2, "total_calls not incrementing on repeat"

    # Test get_reputation
    rep = ph.get_reputation(test_pid)
    assert 0.0 <= rep <= 100.0, f"reputation out of range: {rep}"
    assert rep == 100.0, f"Expected 100% reputation (all alive), got {rep}"

    # Test unknown provider returns 0
    rep_unknown = ph.get_reputation("__nonexistent_provider__")
    assert rep_unknown == 0.0, f"Unknown provider should return 0.0, got {rep_unknown}"

    print(f"  provider_reputation table: EXISTS")
    print(f"  total_calls after 2 runs: {row2['total_calls']}")
    print(f"  get_reputation({test_pid}): {rep}%")
    print("  F7: PASS")
    return "PASS"


# ── Feature 8: Auto Retry ─────────────────────────────────────────────────────

def test_f8_retry():
    print("\n[F8] Auto Retry — switches provider on failure")

    call_log = []

    # Monkey-patch _raw_call: fail on first provider, succeed on second
    original_raw = ph._raw_call

    def mock_raw(p, prompt, timeout=ph.ALIVE_TIMEOUT):
        call_log.append(p["id"])
        if p["id"] == "mock_green":
            raise Exception("Simulated first-call failure")
        if p["id"] == "mock_yellow":
            return "mocked success response", 0.0
        raise Exception("Unknown mock provider")

    ph._raw_call = mock_raw

    # Build PROVIDERS-compatible entries for mocks
    mock_provider_green  = {"id": "mock_green",  "label": "Mock Green",
                            "model": "mock/green", "api_base": None,
                            "api_key": "x", "api_key_env": None, "task_types": ["fast"],
                            "tier": 2}
    mock_provider_yellow = {"id": "mock_yellow", "label": "Mock Yellow",
                            "model": "mock/yellow", "api_base": None,
                            "api_key": "x", "api_key_env": None, "task_types": ["fast"],
                            "tier": 2}

    # Temporarily add mock providers to PROVIDERS list
    original_providers = list(PROVIDERS)
    PROVIDERS.append(mock_provider_green)
    PROVIDERS.append(mock_provider_yellow)

    mock_results = [
        {"id": "mock_green",  "label": "Mock Green",  "alive": True, "cooling": False,
         "score": 100, "status": "GREEN"},
        {"id": "mock_yellow", "label": "Mock Yellow", "alive": True, "cooling": False,
         "score": 40,  "status": "YELLOW"},
    ]

    try:
        result = ph.run_with_retry("test prompt", max_attempts=3, results=mock_results)

        assert result is not None, "run_with_retry returned None — should have succeeded on 2nd provider"
        assert result["provider"] == "mock_yellow", f"Expected mock_yellow, got {result['provider']}"
        assert "mock_green" in call_log, "mock_green should have been tried first"
        assert "mock_yellow" in call_log, "mock_yellow should have been tried second"
        assert result["response"] == "mocked success response"

        print(f"  Call log: {call_log}")
        print(f"  Final provider: {result['provider']}")
        print(f"  Response: {result['response']!r}")
        print("  F8: PASS")
        f8_result = "PASS"
    except AssertionError as exc:
        print(f"  F8: FAIL — {exc}")
        traceback.print_exc()
        f8_result = "FAIL"
    finally:
        ph._raw_call = original_raw
        # Restore PROVIDERS
        while len(PROVIDERS) > len(original_providers):
            PROVIDERS.pop()

    # Verify DEAD/COOLING providers are never retried
    call_log2 = []
    mock_raw2_count = [0]

    def mock_raw2(p, prompt, timeout=ph.ALIVE_TIMEOUT):
        call_log2.append(p["id"])
        mock_raw2_count[0] += 1
        return "ok", 0.0

    ph._raw_call = mock_raw2
    PROVIDERS.append(mock_provider_green)
    PROVIDERS.append(mock_provider_yellow)

    dead_cooling_results = [
        {"id": "mock_green",  "label": "Mock Green",  "alive": False, "cooling": False,
         "score": 0,   "status": "DEAD"},
        {"id": "mock_yellow", "label": "Mock Yellow", "alive": True,  "cooling": True,
         "score": 40,  "status": "COOLING"},
    ]

    try:
        result2 = ph.run_with_retry("test", max_attempts=3, results=dead_cooling_results)
        assert result2 is None, f"Should return None when all providers are dead/cooling, got {result2}"
        assert "mock_green" not in call_log2, "DEAD provider should never be called"
        assert "mock_yellow" not in call_log2, "COOLING provider should never be called"
        print("  DEAD/COOLING exclusion: PASS")
    except AssertionError as exc:
        print(f"  DEAD/COOLING exclusion: FAIL — {exc}")
        if f8_result == "PASS":
            f8_result = "FAIL"
    finally:
        ph._raw_call = original_raw
        while len(PROVIDERS) > len(original_providers):
            PROVIDERS.pop()

    return f8_result


# ── Main ──────────────────────────────────────────────────────────────────────

def run_tests():
    HEALTH_DIR.mkdir(exist_ok=True)
    print()
    print("=" * 60)
    print("  TIER 2 TESTS")
    print("=" * 60)

    test_results = {}
    all_pass = True

    for name, fn in [("F6_scoring", test_f6_scoring),
                     ("F7_reputation", test_f7_reputation),
                     ("F8_retry", test_f8_retry)]:
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
    tier_result = "TIER 2 PASS" if all_pass else "TIER 2 FAIL"
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
        import sys
        sys.exit(1)
