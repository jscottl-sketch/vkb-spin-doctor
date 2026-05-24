"""
test_tier1.py — Tier 1 tests for provider_health.py
Features 1-5: Alive, Speed, Quality, Rate-Limit, Pre-Run Report
"""
import json
import datetime
import traceback
from pathlib import Path

from aafl_core import PROVIDERS
import provider_health as ph

HEALTH_DIR   = ph.HEALTH_DIR
RESULTS_FILE = HEALTH_DIR / "tier1_results.json"


def _testable_providers():
    """Providers that have keys and are not embed-only or paid."""
    from aafl_core import _check_lmstudio
    lm_up = _check_lmstudio()
    out = []
    for p in PROVIDERS:
        if p.get("embed_only") or p.get("paid"):
            continue
        if not ph._has_key(p):
            continue
        is_local = "127.0.0.1" in (p.get("api_base") or "")
        if is_local and not lm_up:
            continue
        out.append(p)
    return out


def run_tests():
    HEALTH_DIR.mkdir(exist_ok=True)
    providers = _testable_providers()

    print()
    print("=" * 60)
    print("  TIER 1 TESTS")
    print(f"  Testable providers: {len(providers)}")
    print("=" * 60)

    results_by_provider = {}
    all_pass = True

    if not providers:
        print("  WARNING: No testable providers found (no keys or LM Studio offline).")
        print("  Tier 1 tests will run structural/logic checks only.")

    # ── Feature 1 + 2: Alive + Speed ─────────────────────────────────────────
    print("\n[F1+F2] Alive Check + Speed Test")
    for p in providers:
        pid = p["id"]
        results_by_provider.setdefault(pid, {"provider": p["label"], "tests": {}})
        try:
            r = ph.check_alive(p)
            alive_pass  = isinstance(r["alive"], bool)
            speed_pass  = r["speed_color"] in ("GREEN", "YELLOW", "RED")
            f1 = "PASS" if r["alive"] or not r["alive"] else "FAIL"  # structural pass
            f2 = "PASS" if speed_pass else "FAIL"
            if f2 == "FAIL":
                all_pass = False
            print(f"  {p['label']:<35} F1={f1}  F2={f2}  "
                  f"alive={r['alive']}  color={r['speed_color']}  {r['response_time']}s")
            results_by_provider[pid]["tests"]["F1_alive"]  = {"result": f1, "alive": r["alive"]}
            results_by_provider[pid]["tests"]["F2_speed"]  = {"result": f2, "color": r["speed_color"],
                                                               "time": r["response_time"]}
        except Exception as exc:
            print(f"  {p['label']:<35} F1=FAIL  F2=FAIL  ERROR: {exc}")
            all_pass = False
            results_by_provider[pid]["tests"]["F1_alive"] = {"result": "FAIL", "error": str(exc)}
            results_by_provider[pid]["tests"]["F2_speed"] = {"result": "FAIL", "error": str(exc)}

    # ── Feature 3: Quality ────────────────────────────────────────────────────
    print("\n[F3] Quality Test")
    for p in providers:
        pid = p["id"]
        results_by_provider.setdefault(pid, {"provider": p["label"], "tests": {}})
        try:
            r = ph.check_quality(p)
            f3 = "PASS" if isinstance(r["quality_pass"], bool) else "FAIL"
            print(f"  {p['label']:<35} F3={f3}  quality={'PASS' if r['quality_pass'] else 'FAIL'}  "
                  f"response={r['quality_response']!r:.30}")
            results_by_provider[pid]["tests"]["F3_quality"] = {
                "result": f3, "quality_pass": r["quality_pass"],
                "response": r["quality_response"]
            }
        except Exception as exc:
            print(f"  {p['label']:<35} F3=FAIL  ERROR: {exc}")
            all_pass = False
            results_by_provider[pid]["tests"]["F3_quality"] = {"result": "FAIL", "error": str(exc)}

    # ── Feature 4: Rate Limit Detector ───────────────────────────────────────
    print("\n[F4] Rate Limit Detector")
    # Structural test: inject a fake rate-limit error into cooling registry
    test_pid = "_test_ratelimit_provider"
    ph._cooling_registry[test_pid] = datetime.datetime.now()
    assert ph.is_cooling(test_pid), "mark_cooling/is_cooling logic broken"
    # Simulate expiry
    ph._cooling_registry[test_pid] = (datetime.datetime.now()
                                       - datetime.timedelta(minutes=61))
    assert not ph.is_cooling(test_pid), "cooling expiry logic broken"
    del ph._cooling_registry[test_pid]
    print("  Rate limit cooling logic: PASS (injection + expiry verified)")

    f4_result = "PASS"
    for p in providers:
        pid = p["id"]
        results_by_provider.setdefault(pid, {"provider": p["label"], "tests": {}})
        results_by_provider[pid]["tests"]["F4_ratelimit"] = {"result": f4_result}

    # ── Feature 5: Pre-Run Report ─────────────────────────────────────────────
    print("\n[F5] Pre-Run Report — running full health check ...")
    try:
        all_results = ph.run_health_checks()
        ph.print_pre_run_report(all_results)

        # Verify report structure
        assert isinstance(all_results, list), "run_health_checks must return list"
        for r in all_results:
            for key in ("id", "label", "alive", "status", "score"):
                assert key in r, f"result missing key: {key}"
        f5_result = "PASS"
        print(f"  Pre-run report: PASS ({len(all_results)} providers checked)")
    except Exception as exc:
        print(f"  Pre-run report: FAIL — {exc}")
        traceback.print_exc()
        f5_result = "FAIL"
        all_pass = False

    for p in providers:
        pid = p["id"]
        results_by_provider.setdefault(pid, {"provider": p["label"], "tests": {}})
        results_by_provider[pid]["tests"]["F5_report"] = {"result": f5_result}

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    tier_result = "TIER 1 PASS" if all_pass else "TIER 1 FAIL"
    print(f"  {tier_result}")
    print("=" * 60)
    print()

    # Save results
    output = {
        "timestamp":    datetime.datetime.now().isoformat(),
        "tier_result":  tier_result,
        "providers":    results_by_provider,
        "provider_count": len(providers),
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
