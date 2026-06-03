"""
mcc_ocbr_handlers.py — OCB-R+ handler extensions for mcc_server.py.
Imported at the bottom of mcc_server.py to attach new routes to MCCHandler.
"""
import json
import subprocess
import threading
import traceback
import urllib.parse
from pathlib import Path

try:
    from error_logger import log_error as _log_error, log_event as _log_event
    from error_logger import get_recent_errors, clear_old_entries
except Exception:
    def _log_error(*a, **kw): pass
    def _log_event(*a, **kw): pass
    def get_recent_errors(n=50, component=None): return []
    def clear_old_entries(keep_last_n=1000): return 0

HERE = Path(__file__).parent

_OCB_TEST_RESULTS: dict = {}
_OCB_TEST_LOCK = threading.Lock()


def _handle_reality_export_get(self):
    """GET /api/reality/export"""
    import sys as _sys
    try:
        script = HERE / "reality_check.py"
        if not script.exists():
            self._send_json({"error": "reality_check.py not found"}, 404)
            return
        proc = subprocess.run(
            [_sys.executable, str(script)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(HERE), timeout=120
        )
        report_file = HERE / "docs" / "REALITY_REPORT.md"
        if not report_file.exists():
            self._send_json({"error": f"Report not generated. stderr: {proc.stderr[:500]}"}, 500)
            return
        content = report_file.read_text(encoding="utf-8", errors="replace")
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/markdown; charset=utf-8")
        self.send_header("Content-Disposition", "attachment; filename=REALITY_REPORT.md")
        body = content.encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    except subprocess.TimeoutExpired:
        _log_error("mcc_server", "ERROR", "reality_check.py timed out")
        self._send_json({"error": "reality_check.py timed out (120s)"}, 500)
    except Exception as exc:
        _log_error("mcc_server", "ERROR", f"reality/export: {exc}", traceback.format_exc())
        self._send_json({"error": str(exc)}, 500)


def _handle_errors_recent_get(self):
    """GET /api/errors/recent?n=50&component=X"""
    try:
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        n = int(qs.get("n", ["50"])[0])
        comp = qs.get("component", [None])[0]
        errors = get_recent_errors(n=n, component=comp)
        self._send_json({"errors": errors, "count": len(errors)})
    except Exception as exc:
        _log_error("mcc_server", "ERROR", f"errors/recent: {exc}", traceback.format_exc())
        self._send_json({"error": str(exc)}, 500)


def _handle_errors_clear_post(self):
    """POST /api/errors/clear"""
    try:
        body = json.loads(self._read_body() or "{}")
        if not body.get("confirm"):
            self._send_json({"ok": False, "error": "confirm flag required"}, 400)
            return
        removed = clear_old_entries(keep_last_n=0)
        _log_event("mcc_server", f"errors_db cleared ({removed} entries removed)")
        self._send_json({"ok": True, "removed": removed})
    except Exception as exc:
        _log_error("mcc_server", "ERROR", f"errors/clear: {exc}", traceback.format_exc())
        self._send_json({"error": str(exc)}, 500)


def _handle_ocb_test_status_get(self):
    """GET /api/ocb/test-status"""
    with _OCB_TEST_LOCK:
        self._send_json(_OCB_TEST_RESULTS.copy() if _OCB_TEST_RESULTS else {"status": "idle", "results": {}})


def _handle_ocb_run_test_suite_post(self):
    """POST /api/ocb/run-test-suite"""
    import sys as _sys
    import re as _re
    try:
        tests_dir = HERE / "tests"
        if not tests_dir.exists():
            self._send_json({"error": "tests/ directory not found"}, 404)
            return
        scripts = ["test_files.py", "test_endpoints.py", "test_imports.py",
                   "test_providers.py", "test_wccs.py"]
        with _OCB_TEST_LOCK:
            _OCB_TEST_RESULTS.clear()
            _OCB_TEST_RESULTS["status"] = "running"

        import datetime as _dt
        results = {}
        total_pass = 0
        total_fail = 0
        for script in scripts:
            sp = tests_dir / script
            if not sp.exists():
                results[script] = {"status": "MISSING", "output": "Script not found", "pass": 0, "fail": 1}
                total_fail += 1
                continue
            try:
                proc = subprocess.run(
                    [_sys.executable, str(sp)],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    cwd=str(HERE), timeout=60
                )
                output = (proc.stdout or "") + (proc.stderr or "")
                exit_ok = proc.returncode == 0
                m = _re.search(r"RESULT:\s*(\d+)/(\d+)\s*PASS", output)
                p = int(m.group(1)) if m else 0
                total_n = int(m.group(2)) if m else 1
                f = total_n - p
                total_pass += p
                total_fail += f
                results[script] = {
                    "status": "PASS" if exit_ok else "FAIL",
                    "output": output[-2000:],
                    "pass": p, "fail": f,
                    "returncode": proc.returncode,
                }
            except subprocess.TimeoutExpired:
                results[script] = {"status": "TIMEOUT", "output": "Timed out", "pass": 0, "fail": 1}
                total_fail += 1
            except Exception as e:
                results[script] = {"status": "ERROR", "output": str(e), "pass": 0, "fail": 1}
                total_fail += 1

        with _OCB_TEST_LOCK:
            _OCB_TEST_RESULTS.update({
                "status": "done",
                "results": results,
                "total_pass": total_pass,
                "total_fail": total_fail,
                "finished": _dt.datetime.now().isoformat(timespec="seconds"),
            })
        self._send_json(_OCB_TEST_RESULTS.copy())
    except Exception as exc:
        _log_error("mcc_server", "ERROR", f"ocb/run-test-suite: {exc}", traceback.format_exc())
        self._send_json({"error": str(exc)}, 500)


def _handle_status_pip_get(self):
    """GET /api/status-pip"""
    import datetime as _dt
    import time as _time
    try:
        now = _time.time()
        LATEST_HEALTH = HERE / "health_results" / "latest_health.json"

        # Pill 1: Providers
        prov_count = 0
        try:
            if LATEST_HEALTH.exists():
                data = json.loads(LATEST_HEALTH.read_text(encoding="utf-8"))
                results = data if isinstance(data, list) else data.get("results", [])
                prov_count = sum(1 for r in results if r.get("ok", r.get("success", False)))
        except Exception:
            pass
        prov_state = "green" if prov_count > 10 else ("amber" if prov_count >= 5 else "red")

        # Pill 2: MOT
        mot_state = "amber"
        mot_detail = "Unknown"
        try:
            mot_prog = HERE / "data" / "ocb_progress.json"
            if mot_prog.exists():
                prog = json.loads(mot_prog.read_text(encoding="utf-8"))
                score = prog.get("mot_score", "")
                mot_detail = str(score)
                mot_state = "green" if ("109/109" in str(score) or "108/108" in str(score)) else "amber"
        except Exception:
            pass

        # Pill 3: WCCS last save
        wccs_state = "red"
        wccs_detail = "Unknown"
        try:
            ss = HERE / "data" / "session_state.json"
            if ss.exists():
                data = json.loads(ss.read_text(encoding="utf-8"))
                last_save_ts = data.get("last_save", {}).get("timestamp", "")
                if last_save_ts:
                    saved = _dt.datetime.fromisoformat(last_save_ts)
                    age_h = (_dt.datetime.now() - saved).total_seconds() / 3600
                    wccs_detail = f"{int(age_h*60)}m ago" if age_h < 1 else f"{int(age_h)}h ago"
                    wccs_state = "green" if age_h < 1 else ("amber" if age_h < 24 else "red")
        except Exception:
            pass

        # Pill 4: Errors per hour
        err_state = "green"
        err_detail = "0/hr"
        try:
            errors = get_recent_errors(200)
            cutoff = (_dt.datetime.now() - _dt.timedelta(hours=1)).isoformat(timespec="seconds")
            count = sum(1 for e in errors if e.get("type") == "error" and e.get("ts", "") >= cutoff)
            err_detail = f"{count}/hr"
            err_state = "green" if count == 0 else ("amber" if count <= 5 else "red")
        except Exception:
            pass

        # Pill 5: Report freshness
        rep_state = "red"
        rep_detail = "None"
        try:
            rep = HERE / "docs" / "REALITY_REPORT.md"
            if rep.exists():
                age_h = (now - rep.stat().st_mtime) / 3600
                rep_detail = f"{int(age_h*60)}m ago" if age_h < 1 else f"{int(age_h)}h ago"
                rep_state = "green" if age_h < 2 else ("amber" if age_h < 24 else "red")
        except Exception:
            pass

        self._send_json({
            "providers": {"state": prov_state, "value": f"{prov_count}/14", "detail": f"{prov_count} of 14 healthy"},
            "mot":       {"state": mot_state,  "value": "MOT",   "detail": mot_detail},
            "wccs":      {"state": wccs_state, "value": "WCCS",  "detail": wccs_detail},
            "errors":    {"state": err_state,  "value": err_detail, "detail": f"{err_detail} error rate"},
            "report":    {"state": rep_state,  "value": "RPT",   "detail": rep_detail},
        })
    except Exception as exc:
        _log_error("mcc_server", "ERROR", f"status-pip: {exc}", traceback.format_exc())
        self._send_json({"error": str(exc)}, 500)


def attach_to_handler(MCCHandler):
    """Attach all OCB-R+ handlers to MCCHandler."""
    MCCHandler._handle_reality_export_get    = _handle_reality_export_get
    MCCHandler._handle_errors_recent_get     = _handle_errors_recent_get
    MCCHandler._handle_errors_clear_post     = _handle_errors_clear_post
    MCCHandler._handle_ocb_test_status_get   = _handle_ocb_test_status_get
    MCCHandler._handle_ocb_run_test_suite_post = _handle_ocb_run_test_suite_post
    MCCHandler._handle_status_pip_get        = _handle_status_pip_get


def patch_do_get(original_do_get):
    """Wrap do_GET to add new OCB-R+ routes before the 404 fallback."""
    def patched_do_get(self):
        path = self.path.split("?")[0]
        if path == "/api/reality/export":
            self._handle_reality_export_get()
        elif path == "/api/errors/recent":
            self._handle_errors_recent_get()
        elif path == "/api/ocb/test-status":
            self._handle_ocb_test_status_get()
        elif path == "/api/status-pip":
            self._handle_status_pip_get()
        else:
            original_do_get(self)
    return patched_do_get


def patch_do_post(original_do_post):
    """Wrap do_POST to add new OCB-R+ routes before the 404 fallback."""
    def patched_do_post(self):
        path = self.path.split("?")[0]
        if path == "/api/errors/clear":
            self._handle_errors_clear_post()
        elif path == "/api/ocb/run-test-suite":
            self._handle_ocb_run_test_suite_post()
        else:
            original_do_post(self)
    return patched_do_post
