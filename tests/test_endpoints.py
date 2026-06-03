"""
tests/test_endpoints.py — Test MCC server endpoints.
Requires mcc_server.py running on localhost:8080.
Exits 0 if all pass, 1 if any fail.
"""
import http.client
import json
import sys
import time

PASS = 0
FAIL = 0

ENDPOINTS = [
    ("GET", "/api/health",             200),
    ("GET", "/api/status",             200),
    ("GET", "/api/history",            200),
    ("GET", "/api/acca",               200),
    ("GET", "/api/reality/export",     200),
    ("GET", "/api/errors/recent",      200),
    ("GET", "/api/detective/report",   200),
    ("GET", "/api/timeline/full",      200),
    ("GET", "/api/llow/elements",      200),
    ("GET", "/api/instructions",       200),
    ("GET", "/api/status-pip",         200),
    ("GET", "/api/ocb/test-status",    200),
]


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


def server_up() -> bool:
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=3)
        conn.request("GET", "/api/health")
        r = conn.getresponse()
        r.read()
        return r.status < 500
    except Exception:
        return False


def hit(method: str, path: str, expect: int) -> tuple:
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=10)
        t0 = time.time()
        conn.request(method, path)
        resp = conn.getresponse()
        body = resp.read()
        ms   = int((time.time() - t0) * 1000)
        return resp.status, body, ms
    except Exception as e:
        return 0, b"", 0


def main():
    print("=== test_endpoints.py ===")

    if not server_up():
        print("FAIL: mcc_server not running on port 8080 — all endpoint tests skipped")
        print(f"\nRESULT: 0/{len(ENDPOINTS)} PASS")
        sys.exit(1)

    check("mcc_server reachable on port 8080", True)

    for method, path, expect in ENDPOINTS:
        code, body, ms = hit(method, path, expect)
        ok = (code == expect)
        check(f"{method} {path} → {expect}", ok, f"got {code} in {ms}ms")

    total = PASS + FAIL
    print(f"\nRESULT: {PASS}/{total} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
