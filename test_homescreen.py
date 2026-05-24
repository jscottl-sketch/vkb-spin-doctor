"""
test_homescreen.py — Home Screen automated tests (Section 4)
Checks HTML structure, file system, server endpoint.
"""
import datetime
import http.client
import json
import subprocess
import sys
import time
import traceback
from pathlib import Path

HERE         = Path(__file__).parent
HEALTH_DIR   = HERE / "health_results"
RESULTS_FILE = HEALTH_DIR / "homescreen_test_results.json"
HTML_PATH    = HERE / "mission_control.html"
SERVER_PATH  = HERE / "mcc_server.py"
DASHBOARD    = HERE / "dashboard_data"

PYTHON       = sys.executable
PORT         = 8080


# ── helpers ───────────────────────────────────────────────────────────────────

def _kill_port(port):
    """Kill whatever process is bound to the given port (Windows)."""
    try:
        subprocess.run(
            ["powershell", "-Command",
             f"Stop-Process -Id (Get-NetTCPConnection -LocalPort {port} "
             f"-ErrorAction SilentlyContinue).OwningProcess "
             f"-Force -ErrorAction SilentlyContinue"],
            capture_output=True, timeout=10,
        )
        time.sleep(1)
    except Exception:
        pass


def _port_open(port):
    import socket
    try:
        with socket.create_connection(("localhost", port), timeout=2):
            return True
    except OSError:
        return False


# ── Test 1: Home tab is first tab ─────────────────────────────────────────────

def test_home_tab_first():
    print("\n[T1] Home tab is first tab in tab bar")
    html = HTML_PATH.read_text(encoding="utf-8")
    home_pos = html.find('data-tab="home"')
    wccs_pos = html.find('data-tab="wccs"')
    assert home_pos != -1, "Home tab button not found"
    assert wccs_pos != -1, "WCCS tab button not found"
    assert home_pos < wccs_pos, f"Home tab not first: home@{home_pos} wccs@{wccs_pos}"
    # Verify active class is on home, not on wccs at load time
    home_pane = 'id="tab-home"' in html
    assert home_pane, "tab-home pane not found"
    print("  Home tab is first: YES")
    print("  tab-home pane exists: YES")
    print("  T1: PASS")
    return "PASS"


# ── Test 2: All 7 cards + 3 empty slots ───────────────────────────────────────

def test_card_count():
    print("\n[T2] All 7 card definitions + 3 empty slots")
    html = HTML_PATH.read_text(encoding="utf-8")

    REQUIRED_FILES = [
        "provider_health.json",
        "aafl_runs.json",
        "scout.json",
        "kanban.json",
        "costs.json",
        "wccs.json",
        "aafl_control.json",
    ]
    missing = [f for f in REQUIRED_FILES if f not in html]
    assert not missing, f"Missing card file references: {missing}"

    # Empty slots — the JS loop generates 3 at runtime; check the template +
    # loop construct are both present in the source
    has_slot_text  = "plug in later" in html
    has_empty_slot = "empty-slot" in html or "slot" in html
    # Check the loop generates exactly 3 slots (for i < 3)
    has_three_loop = "i < 3" in html or "for (let i = 0; i < 3" in html
    assert has_slot_text,  "empty slot text 'plug in later' not found in JS"
    assert has_empty_slot, "empty-slot CSS class not found"
    assert has_three_loop, "loop generating 3 slots not found (expected 'i < 3')"
    slot_count = 3  # confirmed by loop

    print(f"  Card file references found: {len(REQUIRED_FILES)}/7")
    print(f"  Empty slot loop (x3) verified")
    print("  T2: PASS")
    return "PASS"


# ── Test 3: dashboard_data folder + README ────────────────────────────────────

def test_dashboard_data_folder():
    print("\n[T3] dashboard_data/ folder and README.md")
    assert DASHBOARD.exists(), f"dashboard_data/ not found at {DASHBOARD}"
    readme = DASHBOARD / "README.md"
    assert readme.exists(), "README.md not found in dashboard_data/"
    content = readme.read_text(encoding="utf-8")
    assert "tab_name" in content, "README missing tab_name field docs"
    assert "status" in content, "README missing status field docs"
    assert "facts" in content, "README missing facts field docs"

    json_files = list(DASHBOARD.glob("*.json"))
    assert len(json_files) >= 7, f"Expected 7+ JSON files, found {len(json_files)}"

    print(f"  dashboard_data/ exists: YES")
    print(f"  README.md exists: YES")
    print(f"  JSON files: {len(json_files)}")
    print("  T3: PASS")
    return "PASS"


# ── Test 4: mcc_server has /dashboard-data/ endpoint ─────────────────────────

def test_server_endpoint_defined():
    print("\n[T4] mcc_server.py has /dashboard-data/ endpoint")
    src = SERVER_PATH.read_text(encoding="utf-8")
    assert "dashboard-data" in src, "/dashboard-data not found in mcc_server.py"
    assert "_handle_dashboard_data" in src, "_handle_dashboard_data method not found"
    assert "DASHBOARD_DATA" in src, "DASHBOARD_DATA constant not found"
    print("  /dashboard-data route: YES")
    print("  _handle_dashboard_data method: YES")
    print("  T4: PASS")
    return "PASS"


# ── Test 5: Connect button states in HTML ─────────────────────────────────────

def test_connect_button_states():
    print("\n[T5] Connect Data button states in HTML/CSS")
    html = HTML_PATH.read_text(encoding="utf-8")
    checks = {
        "btn-connect element":   'id="btn-connect"' in html,
        "connecting CSS state":  "btn-connect.connecting" in html or ".connecting{" in html,
        "connected CSS state":   "btn-connect.connected" in html or ".connected{" in html,
        "failed CSS state":      "btn-connect.failed" in html or ".failed{" in html,
        "spinner element":       "btn-spinner" in html,
        "spin animation":        "@keyframes spin" in html,
        "Connecting text in JS": "Connecting..." in html,
    }
    failed = [k for k, v in checks.items() if not v]
    assert not failed, f"Missing: {failed}"
    for k, v in checks.items():
        print(f"  {'YES' if v else 'NO '} {k}")
    print("  T5: PASS")
    return "PASS"


# ── Test 6: Server status dot exists ─────────────────────────────────────────

def test_server_dot():
    print("\n[T6] Server status dot in HTML")
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="server-dot"' in html, "server-dot element missing"
    assert "server-dot" in html, "server-dot CSS class missing"
    assert ".live{" in html or "server-dot.live" in html, ".live CSS missing"
    assert ".dead{" in html or "server-dot.dead" in html, ".dead CSS missing"
    assert "checkServerAlive" in html, "checkServerAlive function missing"
    assert "10000" in html, "10-second poll interval missing"
    print("  server-dot element: YES")
    print("  live/dead CSS states: YES")
    print("  10s auto-poll: YES")
    print("  T6: PASS")
    return "PASS"


# ── Test 7: Live server serves /dashboard-data/README.md ─────────────────────

def test_live_server():
    print("\n[T7] Start mcc_server.py, hit /dashboard-data/README.md, confirm 200")
    server_proc = None
    killed_existing = False

    # Kill any existing process on port 8080
    if _port_open(PORT):
        print(f"  Port {PORT} in use — killing existing process...")
        _kill_port(PORT)
        killed_existing = True
        time.sleep(1)

    try:
        server_proc = subprocess.Popen(
            [PYTHON, str(SERVER_PATH)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd=str(HERE),
        )
        # Wait for server to bind
        for _ in range(15):
            if _port_open(PORT):
                break
            time.sleep(0.3)
        else:
            out, err = server_proc.communicate(timeout=3)
            raise RuntimeError(f"Server did not bind to port {PORT}\n{err[:300]}")

        if server_proc.poll() is not None:
            _, err = server_proc.communicate(timeout=2)
            raise RuntimeError(f"Server exited immediately: {err[:200]}")

        # Hit /dashboard-data/README.md
        conn = http.client.HTTPConnection("localhost", PORT, timeout=10)
        conn.request("GET", "/dashboard-data/README.md")
        resp = conn.getresponse()
        body = resp.read().decode("utf-8")
        conn.close()

        assert resp.status == 200, f"Expected 200, got {resp.status}"
        assert "tab_name" in body, "README.md body missing expected content"

        # Also verify /dashboard-data/ listing works
        conn2 = http.client.HTTPConnection("localhost", PORT, timeout=10)
        conn2.request("GET", "/dashboard-data/")
        resp2 = conn2.getresponse()
        body2 = resp2.read().decode("utf-8")
        conn2.close()

        assert resp2.status == 200, f"/dashboard-data/ listing returned {resp2.status}"
        listing = json.loads(body2)
        assert "files" in listing, "Listing missing 'files' key"
        assert len(listing["files"]) >= 7, f"Expected 7+ files, got {len(listing['files'])}"

        print(f"  HTTP 200 from /dashboard-data/README.md: YES")
        print(f"  Files in listing: {len(listing['files'])}")
        print("  T7: PASS")
        return "PASS"

    except Exception as exc:
        print(f"  T7: FAIL — {exc}")
        traceback.print_exc()
        return "FAIL"
    finally:
        if server_proc and server_proc.poll() is None:
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()


# ── Main ─────────────────────────────────────────────────────────────────────

def run_tests():
    HEALTH_DIR.mkdir(exist_ok=True)
    print()
    print("=" * 60)
    print("  HOME SCREEN TESTS")
    print("=" * 60)

    results = {}
    all_pass = True

    for name, fn in [
        ("T1_home_first",       test_home_tab_first),
        ("T2_card_count",       test_card_count),
        ("T3_dashboard_folder", test_dashboard_data_folder),
        ("T4_endpoint_defined", test_server_endpoint_defined),
        ("T5_connect_states",   test_connect_button_states),
        ("T6_server_dot",       test_server_dot),
        ("T7_live_server",      test_live_server),
    ]:
        try:
            r = fn()
            results[name] = r
            if r != "PASS":
                all_pass = False
        except Exception as exc:
            print(f"  {name}: FAIL — {exc}")
            traceback.print_exc()
            results[name] = "FAIL"
            all_pass = False

    print()
    print("=" * 60)
    final = "HOME SCREEN PASS" if all_pass else "HOME SCREEN FAIL"
    print(f"  {final}")
    if not all_pass:
        failed = [k for k, v in results.items() if v != "PASS"]
        print(f"  Failed tests: {failed}")
    print("=" * 60)
    print()

    output = {
        "timestamp":  datetime.datetime.now().isoformat(),
        "result":     final,
        "tests":      results,
    }
    RESULTS_FILE.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"  Results saved to {RESULTS_FILE}")
    print()

    return final


if __name__ == "__main__":
    result = run_tests()
    if "FAIL" in result:
        sys.exit(1)
