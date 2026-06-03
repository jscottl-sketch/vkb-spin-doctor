"""
tests/test_providers.py — Send single-token ping to each provider in aafl_core.py.
Logs results to errors_db.json via error_logger. Exits 0 if all pass, 1 if any fail.
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

PASS = 0
FAIL = 0


def check(label: str, ok: bool, detail: str = "") -> bool:
    global PASS, FAIL
    status = "PASS" if ok else "FAIL"
    suffix = f": {detail}" if detail else ""
    print(f"{status}: {label}{suffix}")
    if ok:
        PASS += 1
    else:
        FAIL += 1
    return ok


def main():
    print("=== test_providers.py ===")

    try:
        from error_logger import log_event, log_error
    except ImportError:
        log_event = log_error = lambda *a, **kw: None
        print("WARN: error_logger not found — results won't be logged to errors_db")

    try:
        from aafl_core import PROVIDERS, AAFLCore
    except Exception as e:
        check("aafl_core import", False, str(e)[:80])
        print(f"\nRESULT: 0/1 PASS")
        sys.exit(1)

    check("aafl_core import", True)

    # Try a minimal ping via AAFLCore for each provider
    core = AAFLCore()
    for p in PROVIDERS:
        pid = p["id"]
        t0 = time.time()
        try:
            resp = core.call_provider(p, "ping", max_tokens=3)
            ms = int((time.time() - t0) * 1000)
            ok = bool(resp and len(resp) > 0)
            if ok:
                log_event("test_providers", f"{pid} OK {ms}ms")
                check(f"provider {pid}", True, f"{ms}ms")
            else:
                log_error("test_providers", "PROVIDER_FAIL", f"{pid}: empty response")
                check(f"provider {pid}", False, "empty response")
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            log_error("test_providers", "PROVIDER_FAIL", f"{pid}: {str(e)[:80]}")
            check(f"provider {pid}", False, str(e)[:60])

    total = PASS + FAIL
    print(f"\nRESULT: {PASS}/{total} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
