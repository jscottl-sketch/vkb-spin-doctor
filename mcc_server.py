"""
mcc_server.py — MCC (Mission Control Center) HTTP Server
Runs on localhost:8080. Provides endpoints for the WCCS tab in mission_control.html.

Endpoints:
  POST /wccs      body = chat summary text (optional). Writes chat_latest.txt if body
                  provided, then runs wccs_runner.py. Returns JSON result.
  POST /capture   body = text. Appends to chat_latest.txt with timestamp.
  GET  /captures  Returns current chat_latest.txt content as JSON.
  GET  /status    Returns last WCCS result + time since last capture.

Usage:
  python mcc_server.py
"""

import datetime
import difflib
import http.server
import json
import os
import shutil
import subprocess
import sys
import threading
import urllib.parse
from pathlib import Path

PORT         = 8080
HOST         = "localhost"
HERE         = Path(__file__).parent
CHAT         = HERE / "chat_latest.txt"
SCOUT_OUTPUT = HERE / "scout_output"
SCOUT_LATEST = SCOUT_OUTPUT / "latest.txt"
SCOUT_CONFIG = HERE / "chief_scout_config.json"
PYTHON       = sys.executable
FULL_PYTHON  = Path(r"C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe")
ARCHIVE_DIR  = HERE / "archive_dead"
STATUS_FILE  = HERE / "STATUS.md"
HISTORY_FILE = HERE / "HISTORY.md"
ACCA_FILE    = HERE / "ACCA.md"

# ── AAFL Control paths ────────────────────────────────────────────────────────
AAFL_CONFIG  = HERE / "aafl_control_config.json"
AAFL_OUTPUT  = HERE / "aafl_output"
AAFL_LATEST  = AAFL_OUTPUT / "latest.txt"
GOAL_TXT     = HERE / "goal.txt"
GOAL_QUEUE   = HERE / "goal_queue.txt"
DB_PATH          = HERE / "data" / "knowledge_engine.db"
HEALTH_RESULTS   = HERE / "health_results"
LATEST_HEALTH    = HEALTH_RESULTS / "latest_health.json"
DASHBOARD_DATA   = HERE / "dashboard_data"
STUCK_INBOX_FILE = HERE / "stuck_inbox.json"
PROMO_QUEUE_FILE = HERE / "promo_queue.json"
ALP_FILE         = HERE / "ALP_Database.md"
KNOWN_ISSUES     = DASHBOARD_DATA / "known_issues.json"
MOT_SCRIPT       = HERE / "mcc_full_mot.py"

# ── Feature paths ──────────────────────────────────────────────────────────────
MODULE_REGISTRY  = HERE / "modules" / "module_registry.json"
PRESETS_DIR      = HERE / "presets"
AAFL_SETTINGS    = HERE / "aafl_config.json"
RETRY_LOG        = HEALTH_RESULTS / "retry_log.json"
CHAIN_LOG        = HEALTH_RESULTS / "chain_log.json"
SOURCES_LIBRARY  = HERE / "sources_library.json"
STORAGE_CFG      = HERE / "storage_config.json"
SCOUT_TIMER_STOP = HERE / "scout_timer_stop.flag"
WCCS_LOG_MD      = HERE / "wccs_log.md"
SESSION_LOGS_DIR = HERE / "session_logs"

_state_lock  = threading.Lock()
_wccs_lock   = threading.Lock()
_scout_lock  = threading.Lock()
_aafl_lock   = threading.Lock()

_last_wccs: dict = {"result": None, "time": None, "stdout": ""}
_last_capture: datetime.datetime | None = None
_scout_running: bool = False
_aafl_running: bool  = False
_aafl_proc           = None  # subprocess.Popen handle

# ── Auto-WCCS state ───────────────────────────────────────────────────────────
_auto_wccs_timer     = None
_auto_wccs_interval  = 30        # minutes
_auto_wccs_active    = False
_auto_wccs_last_save = None
_auto_wccs_next_fire = None      # datetime
_auto_wccs_log       = []        # last 5 entries
_auto_wccs_lock      = threading.Lock()


def _run_scout_bg(goal: str):
    global _scout_running
    SCOUT_OUTPUT.mkdir(exist_ok=True)
    try:
        with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
            f.write(f"[RUNNING] Goal: {goal}\n[STARTED] {_now_iso()}\n")
        cmd = [PYTHON, str(HERE / "chief_scout.py")]
        if goal:
            cmd.append(goal)
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(HERE))
        output = (res.stdout + res.stderr).strip()
        with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
            f.write(output if output else "[DONE] No output received")
    except subprocess.TimeoutExpired:
        with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
            f.write("[ERROR] Scout timed out after 120s")
    except Exception as exc:
        with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
            f.write(f"[ERROR] {exc}")
    finally:
        global _scout_running
        _scout_running = False
        try:
            _scout_lock.release()
        except RuntimeError:
            pass


def _run_aafl_bg(config: dict):
    global _aafl_running, _aafl_proc
    AAFL_OUTPUT.mkdir(exist_ok=True)
    try:
        goal = config.get("current_goal", "").strip()
        with open(AAFL_LATEST, "w", encoding="utf-8") as f:
            f.write(f"[RUNNING] Goal: {goal}\n[STARTED] {_now_iso()}\n")
        cmd = [PYTHON, str(HERE / "loop_manager.py"), "--once"]
        _aafl_proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, cwd=str(HERE),
        )
        with open(AAFL_LATEST, "a", encoding="utf-8") as f:
            for line in _aafl_proc.stdout:
                f.write(line)
                f.flush()
        _aafl_proc.wait()
        with open(AAFL_LATEST, "a", encoding="utf-8") as f:
            f.write(f"\n[DONE] Exit code: {_aafl_proc.returncode}\n[FINISHED] {_now_iso()}\n")
    except Exception as exc:
        try:
            with open(AAFL_LATEST, "a", encoding="utf-8") as f:
                f.write(f"[ERROR] {exc}\n")
        except Exception:
            pass
    finally:
        _aafl_running = False
        _aafl_proc = None
        try:
            _aafl_lock.release()
        except RuntimeError:
            pass


def _now_iso() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _stamp() -> str:
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def _run_wccs() -> dict:
    runner = HERE / "wccs_runner.py"
    if not runner.exists():
        return {"ok": False, "stdout": "wccs_runner.py not found", "time": _now_iso()}
    try:
        res = subprocess.run(
            [PYTHON, str(runner)],
            capture_output=True, text=True, timeout=300,
            cwd=str(HERE),
        )
        ok  = res.returncode == 0
        out = (res.stdout + res.stderr).strip()
        return {"ok": ok, "stdout": out, "time": _now_iso()}
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "Timed out after 300s", "time": _now_iso()}
    except Exception as e:
        return {"ok": False, "stdout": str(e), "time": _now_iso()}


# ── Auto-WCCS helpers ─────────────────────────────────────────────────────────

def _auto_wccs_record(ok, trigger):
    global _auto_wccs_last_save
    ts = _now_iso()
    entry = {"time": ts, "ok": ok, "trigger": trigger}
    with _auto_wccs_lock:
        _auto_wccs_last_save = ts
        _auto_wccs_log.insert(0, entry)
        del _auto_wccs_log[5:]


def _auto_wccs_fire():
    global _auto_wccs_timer, _auto_wccs_next_fire
    py = FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable)
    script = HERE / "aafl_wccs.py"
    ok = False
    try:
        if script.exists():
            res = subprocess.run(
                [str(py), str(script)],
                capture_output=True, text=True, timeout=300, cwd=str(HERE),
            )
            ok = res.returncode == 0
    except Exception:
        pass
    _auto_wccs_record(ok, "auto")
    with _auto_wccs_lock:
        if _auto_wccs_active:
            _auto_wccs_next_fire = (datetime.datetime.now()
                                    + datetime.timedelta(minutes=_auto_wccs_interval))
            t = threading.Timer(_auto_wccs_interval * 60, _auto_wccs_fire)
            t.daemon = True
            t.start()
            # store ref without holding lock across assignment
    if _auto_wccs_active:
        globals()["_auto_wccs_timer"] = t


def _auto_wccs_set(action, interval=30):
    global _auto_wccs_timer, _auto_wccs_interval, _auto_wccs_active, _auto_wccs_next_fire
    with _auto_wccs_lock:
        if _auto_wccs_timer is not None:
            _auto_wccs_timer.cancel()
            _auto_wccs_timer = None
        if action == "start":
            _auto_wccs_interval = max(15, min(60, int(interval)))
            _auto_wccs_active   = True
            _auto_wccs_next_fire = (datetime.datetime.now()
                                    + datetime.timedelta(minutes=_auto_wccs_interval))
            t = threading.Timer(_auto_wccs_interval * 60, _auto_wccs_fire)
            t.daemon = True
            t.start()
            _auto_wccs_timer = t
        elif action == "stop":
            _auto_wccs_active    = False
            _auto_wccs_next_fire = None


class MCCHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[MCC] {self.address_string()} -- {fmt % args}")

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> str:
        length = int(self.headers.get("Content-Length", 0))
        if length > 0:
            return self.rfile.read(length).decode("utf-8", errors="replace")
        return ""

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        try:
            if path in ("/", "/mission_control.html"):
                self._handle_html()
            elif path == "/status":
                self._handle_status()
            elif path == "/captures":
                self._handle_captures()
            elif path == "/scout-result":
                self._handle_scout_result()
            elif path == "/scout-config":
                self._handle_scout_config_get()
            elif path == "/scout-presets":
                self._handle_scout_presets()
            elif path == "/aafl-status":
                self._handle_aafl_status()
            elif path == "/aafl-queue":
                self._handle_aafl_queue_get()
            elif path == "/aafl-config":
                self._handle_aafl_config_get()
            elif path == "/aafl-providers":
                self._handle_aafl_providers()
            elif path == "/api/timeline":
                self._handle_api_timeline()
            elif path == "/api/backup":
                self._handle_api_backup()
            elif path == "/api/diff":
                self._handle_api_diff()
            elif path == "/api/session-logs":
                self._handle_api_session_logs()
            elif path == "/api/session-log":
                self._handle_api_session_log()
            elif path == "/api/search":
                self._handle_api_search()
            elif path == "/api/auto-wccs":
                self._handle_api_auto_wccs_get()
            elif path == "/health-status":
                self._handle_health_status()
            elif path.startswith("/dashboard-data"):
                self._handle_dashboard_data(path)
            elif path == "/stuck-inbox":
                self._handle_stuck_inbox_get()
            elif path == "/memory/knowledge":
                self._handle_memory_knowledge()
            elif path == "/memory/solutions":
                self._handle_memory_solutions()
            elif path == "/memory/sources":
                self._handle_memory_sources()
            elif path == "/promo-queue":
                self._handle_promo_queue_get()
            elif path == "/acca-codes":
                self._handle_acca_codes()
            elif path == "/alp-data":
                self._handle_alp_data()
            elif path == "/self-diagnosis":
                self._handle_self_diagnosis()
            elif path == "/known-issues":
                self._handle_known_issues_get()
            # ── Feature 1 ──────────────────────────────────────────────────────
            elif path == "/modules":
                self._handle_modules_get()
            # ── Feature 2 ──────────────────────────────────────────────────────
            elif path == "/presets":
                self._handle_presets_get()
            elif path == "/presets/load":
                self._handle_presets_load()
            # ── Feature 3 ──────────────────────────────────────────────────────
            elif path == "/aafl-settings":
                self._handle_aafl_settings_get()
            # ── Feature 4 ──────────────────────────────────────────────────────
            elif path == "/retry-log":
                self._handle_retry_log_get()
            # ── Feature 6 ──────────────────────────────────────────────────────
            elif path == "/chain-status":
                self._handle_chain_status()
            elif path == "/chain-log":
                self._handle_chain_log_get()
            # ── Feature 7 ──────────────────────────────────────────────────────
            elif path == "/scout-timer/status":
                self._handle_scout_timer_status()
            # ── Feature 8 ──────────────────────────────────────────────────────
            elif path == "/sources-library":
                self._handle_sources_library_get()
            # ── Feature 9 ──────────────────────────────────────────────────────
            elif path == "/stuck-inbox/summary":
                self._handle_stuck_summary_get()
            # ── Feature 10 ─────────────────────────────────────────────────────
            elif path == "/storage":
                self._handle_storage_get()
            elif path == "/storage/report":
                self._handle_storage_report()
            # ── Build 1 Step B: WCCS Drill-Down ────────────────────────────────
            elif path == "/wccs/save-log":
                self._handle_wccs_save_log()
            elif path == "/wccs/history-search":
                self._handle_wccs_history_search()
            elif path == "/wccs/session-logs":
                self._handle_wccs_session_logs()
            elif path == "/wccs/versions":
                self._handle_wccs_versions()
            # ── MCP endpoints for Claude Chat web_fetch access ──────────────────
            elif path == "/api/status":
                self._handle_api_status_md()
            elif path == "/api/history":
                self._handle_api_history_md()
            elif path == "/api/health":
                self._handle_api_health()
            else:
                self._send_json({"error": "Not found"}, 404)
        except Exception as exc:
            try:
                self._send_json({"error": f"Server error: {exc}"}, 500)
            except Exception:
                pass

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            if path == "/wccs":
                self._handle_wccs()
            elif path == "/capture":
                self._handle_capture()
            elif path == "/run-scout":
                self._handle_run_scout()
            elif path == "/scout-config":
                self._handle_scout_config_post()
            elif path == "/run-aafl":
                self._handle_run_aafl()
            elif path == "/set-aafl-goal":
                self._handle_set_aafl_goal()
            elif path == "/aafl-queue":
                self._handle_aafl_queue_post()
            elif path == "/aafl-config":
                self._handle_aafl_config_post()
            elif path == "/stop-aafl":
                self._handle_stop_aafl()
            elif path == "/api/wccs":
                self._handle_api_wccs()
            elif path == "/api/restore":
                self._handle_api_restore()
            elif path == "/api/auto-wccs":
                self._handle_api_auto_wccs_post()
            elif path == "/resolve-stuck":
                self._handle_resolve_stuck()
            elif path == "/run-now":
                self._handle_run_now()
            elif path == "/approve-promo":
                self._handle_approve_promo()
            elif path == "/reject-promo":
                self._handle_reject_promo()
            elif path == "/alp-add":
                self._handle_alp_add()
            elif path == "/run-mot":
                self._handle_run_mot()
            elif path == "/known-issues":
                self._handle_known_issues_post()
            elif path == "/run-health-check":
                self._handle_run_health_check()
            elif path == "/run-merge-sessions":
                self._handle_run_merge_sessions()
            # ── Feature 1 ──────────────────────────────────────────────────────
            elif path == "/toggle-module":
                self._handle_toggle_module()
            # ── Feature 2 ──────────────────────────────────────────────────────
            elif path == "/presets/save":
                self._handle_presets_save()
            elif path == "/presets/delete":
                self._handle_presets_delete()
            # ── Feature 3 ──────────────────────────────────────────────────────
            elif path == "/aafl-settings":
                self._handle_aafl_settings_post()
            # ── Feature 5 ──────────────────────────────────────────────────────
            elif path == "/suggest-provider":
                self._handle_suggest_provider()
            # ── Feature 6 ──────────────────────────────────────────────────────
            elif path == "/run-chain":
                self._handle_run_chain()
            # ── Feature 7 ──────────────────────────────────────────────────────
            elif path == "/scout-timer/start":
                self._handle_scout_timer_start()
            elif path == "/scout-timer/stop":
                self._handle_scout_timer_stop()
            # ── Feature 8 ──────────────────────────────────────────────────────
            elif path == "/sources-library/add":
                self._handle_sources_library_add()
            # ── Feature 9 ──────────────────────────────────────────────────────
            elif path == "/stuck-inbox/bulk-resolve":
                self._handle_stuck_bulk_resolve()
            # ── Build 1 Step B: WCCS Drill-Down ────────────────────────────────
            elif path == "/wccs/restore":
                self._handle_wccs_restore()
            elif path == "/wccs/diff":
                self._handle_wccs_diff()
            else:
                self._send_json({"error": "Not found"}, 404)
        except Exception as exc:
            try:
                self._send_json({"error": f"Server error: {exc}"}, 500)
            except Exception:
                pass

    def do_DELETE(self):
        path = self.path.split("?")[0]
        if path == "/aafl-queue":
            self._handle_aafl_queue_delete()
        else:
            self._send_json({"error": "Not found"}, 404)

    # ── GET / and /mission_control.html ──────────────────────────────────────

    def _handle_html(self):
        html_path = HERE / "mission_control.html"
        if not html_path.exists():
            self._send_json({"error": "mission_control.html not found"}, 404)
            return
        body = html_path.read_bytes()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── GET /status ───────────────────────────────────────────────────────────

    def _handle_status(self):
        global _last_capture
        with _state_lock:
            wccs = dict(_last_wccs)
            cap  = _last_capture

        mins_since = None
        if cap:
            delta = datetime.datetime.now() - cap
            mins_since = int(delta.total_seconds() / 60)

        self._send_json({
            "last_wccs":          wccs,
            "last_capture_iso":   cap.isoformat() if cap else None,
            "mins_since_capture": mins_since,
        })

    # ── GET /captures ─────────────────────────────────────────────────────────

    def _handle_captures(self):
        with _state_lock:
            content = CHAT.read_text(encoding="utf-8", errors="replace") if CHAT.exists() else ""
        self._send_json({"content": content, "path": str(CHAT)})

    # ── POST /capture ─────────────────────────────────────────────────────────

    def _handle_capture(self):
        global _last_capture
        body = self._read_body().strip()
        if not body:
            self._send_json({"ok": False, "error": "Empty body"}, 400)
            return
        entry = f"{_stamp()} {body}\n"
        with _state_lock:
            with CHAT.open("a", encoding="utf-8") as f:
                f.write(entry)
            _last_capture = datetime.datetime.now()
        self._send_json({"ok": True, "appended": entry})

    # ── POST /wccs ────────────────────────────────────────────────────────────

    def _handle_wccs(self):
        global _last_capture, _last_wccs

        # Only one WCCS run at a time
        if not _wccs_lock.acquire(blocking=False):
            self._send_json({"ok": False, "error": "WCCS already running"}, 409)
            return

        try:
            body = self._read_body().strip()

            # Write body to chat_latest.txt if provided
            if body:
                with _state_lock:
                    CHAT.write_text(body, encoding="utf-8")
                    _last_capture = datetime.datetime.now()

            # Guard: must have something to process
            if not CHAT.exists() or not CHAT.read_text(encoding="utf-8").strip():
                self._send_json({"ok": False, "error": "chat_latest.txt is empty"}, 400)
                return

            print("[MCC] Running wccs_runner.py ...")
            result = _run_wccs()

            with _state_lock:
                _last_wccs.update(result)

            self._send_json({
                "ok":     result["ok"],
                "result": "PASS" if result["ok"] else "FAIL",
                "stdout": result["stdout"],
                "time":   result["time"],
            })
        finally:
            _wccs_lock.release()


    # ── POST /run-scout ───────────────────────────────────────────────────────

    def _handle_run_scout(self):
        global _scout_running
        body = self._read_body()
        try:
            overrides = json.loads(body) if body.strip() else {}
        except Exception:
            overrides = {}

        # Load existing config, merge overrides
        existing = {}
        if SCOUT_CONFIG.exists():
            try:
                with open(SCOUT_CONFIG, encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass
        merged = {**existing, **overrides}

        # Persist merged config
        SCOUT_OUTPUT.mkdir(exist_ok=True)
        try:
            with open(SCOUT_CONFIG, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        goal = merged.get("goal", "")

        if not _scout_lock.acquire(blocking=False):
            self._send_json({"status": "already_running", "config": merged})
            return

        _scout_running = True
        t = threading.Thread(target=_run_scout_bg, args=(goal,), daemon=True)
        t.start()
        self._send_json({"status": "running", "config": merged})

    # ── GET /scout-result ────────────────────────────────────────────────────

    def _handle_scout_result(self):
        content = ""
        if SCOUT_LATEST.exists():
            try:
                content = SCOUT_LATEST.read_text(encoding="utf-8", errors="replace")
            except Exception:
                content = "[ERROR] Could not read scout output"
        else:
            content = "No scout results yet — run a scout first."
        self._send_json({"content": content, "running": _scout_running})

    # ── GET /scout-config ────────────────────────────────────────────────────

    def _handle_scout_config_get(self):
        if SCOUT_CONFIG.exists():
            try:
                with open(SCOUT_CONFIG, encoding="utf-8") as f:
                    cfg = json.load(f)
                self._send_json(cfg)
                return
            except Exception:
                pass
        self._send_json({})

    # ── POST /scout-config (save without running) ─────────────────────────────

    def _handle_scout_config_post(self):
        body = self._read_body()
        try:
            updates = json.loads(body) if body.strip() else {}
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        existing = {}
        if SCOUT_CONFIG.exists():
            try:
                with open(SCOUT_CONFIG, encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass
        merged = {**existing, **updates}
        try:
            with open(SCOUT_CONFIG, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)
            self._send_json({"ok": True, "config": merged})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── GET /scout-presets ────────────────────────────────────────────────────

    def _handle_scout_presets(self):
        if SCOUT_CONFIG.exists():
            try:
                with open(SCOUT_CONFIG, encoding="utf-8") as f:
                    cfg = json.load(f)
                self._send_json({"presets": cfg.get("presets", [])})
                return
            except Exception:
                pass
        self._send_json({"presets": []})

    # ── POST /run-aafl ────────────────────────────────────────────────────────

    def _handle_run_aafl(self):
        global _aafl_running
        cfg = {}
        if AAFL_CONFIG.exists():
            try:
                with open(AAFL_CONFIG, encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                pass

        goal = cfg.get("current_goal", "").strip()
        if goal:
            try:
                GOAL_TXT.write_text(goal, encoding="utf-8")
            except Exception:
                pass

        if not _aafl_lock.acquire(blocking=False):
            self._send_json({"status": "already_running", "goal": goal})
            return

        _aafl_running = True
        AAFL_OUTPUT.mkdir(exist_ok=True)
        t = threading.Thread(target=_run_aafl_bg, args=(cfg,), daemon=True)
        t.start()
        self._send_json({"status": "running", "goal": goal})

    # ── POST /set-aafl-goal ───────────────────────────────────────────────────

    def _handle_set_aafl_goal(self):
        body = self._read_body().strip()
        try:
            data = json.loads(body) if body else {}
            goal = data.get("goal", "").strip()
        except Exception:
            goal = body.strip()
        if not goal:
            self._send_json({"ok": False, "error": "Empty goal"}, 400)
            return
        try:
            GOAL_TXT.write_text(goal, encoding="utf-8")
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)
            return
        cfg = {}
        if AAFL_CONFIG.exists():
            try:
                with open(AAFL_CONFIG, encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                pass
        cfg["current_goal"] = goal
        try:
            with open(AAFL_CONFIG, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        self._send_json({"ok": True, "goal": goal})

    # ── GET /aafl-status ──────────────────────────────────────────────────────

    def _handle_aafl_status(self):
        lines = []
        if AAFL_LATEST.exists():
            try:
                text = AAFL_LATEST.read_text(encoding="utf-8", errors="replace")
                lines = text.splitlines()[-50:]
            except Exception:
                lines = ["[ERROR] Could not read aafl_output/latest.txt"]

        last_run = {}
        try:
            import sqlite3
            if DB_PATH.exists():
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT * FROM solution_log ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
                if row:
                    last_run = dict(row)
                conn.close()
        except Exception:
            pass

        self._send_json({
            "output":   "\n".join(lines),
            "running":  _aafl_running,
            "last_run": last_run,
        })

    # ── GET /aafl-queue ───────────────────────────────────────────────────────

    def _handle_aafl_queue_get(self):
        goals = []
        if GOAL_QUEUE.exists():
            try:
                lines = GOAL_QUEUE.read_text(encoding="utf-8", errors="replace").splitlines()
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    is_comment = stripped.startswith("#")
                    goals.append({
                        "index":  i,
                        "text":   stripped.lstrip("#").strip(),
                        "raw":    line,
                        "status": "commented" if is_comment else "active",
                    })
            except Exception:
                pass
        self._send_json({"goals": goals})

    # ── POST /aafl-queue ──────────────────────────────────────────────────────

    def _handle_aafl_queue_post(self):
        body = self._read_body().strip()
        try:
            data = json.loads(body) if body else {}
            goal = data.get("goal", "").strip()
        except Exception:
            goal = body.strip()
        if not goal:
            self._send_json({"ok": False, "error": "Empty goal"}, 400)
            return
        try:
            with open(GOAL_QUEUE, "a", encoding="utf-8") as f:
                f.write(goal + "\n")
            self._send_json({"ok": True})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── DELETE /aafl-queue ────────────────────────────────────────────────────

    def _handle_aafl_queue_delete(self):
        body = self._read_body().strip()
        try:
            data = json.loads(body) if body else {}
            idx  = int(data.get("index", -1))
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON or missing index"}, 400)
            return
        if not GOAL_QUEUE.exists():
            self._send_json({"ok": False, "error": "goal_queue.txt not found"}, 404)
            return
        try:
            lines = GOAL_QUEUE.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
            if idx < 0 or idx >= len(lines):
                self._send_json({"ok": False, "error": "Index out of range"}, 400)
                return
            if not lines[idx].lstrip().startswith("#"):
                lines[idx] = "# " + lines[idx]
            GOAL_QUEUE.write_text("".join(lines), encoding="utf-8")
            self._send_json({"ok": True})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── GET /aafl-config ──────────────────────────────────────────────────────

    def _handle_aafl_config_get(self):
        if AAFL_CONFIG.exists():
            try:
                with open(AAFL_CONFIG, encoding="utf-8") as f:
                    cfg = json.load(f)
                self._send_json(cfg)
                return
            except Exception:
                pass
        self._send_json({})

    # ── POST /aafl-config ─────────────────────────────────────────────────────

    def _handle_aafl_config_post(self):
        body = self._read_body().strip()
        try:
            updates = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        existing = {}
        if AAFL_CONFIG.exists():
            try:
                with open(AAFL_CONFIG, encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass
        # Preserve provider_list — never overwritten from UI saves
        if "provider_list" not in updates and "provider_list" in existing:
            updates["provider_list"] = existing["provider_list"]
        merged = {**existing, **updates}
        try:
            with open(AAFL_CONFIG, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)
            self._send_json({"ok": True})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── GET /aafl-providers ───────────────────────────────────────────────────

    def _handle_aafl_providers(self):
        providers = []
        if AAFL_CONFIG.exists():
            try:
                with open(AAFL_CONFIG, encoding="utf-8") as f:
                    cfg = json.load(f)
                providers = cfg.get("provider_list", [])
            except Exception:
                pass
        self._send_json({"providers": providers})

    # ── POST /stop-aafl ───────────────────────────────────────────────────────

    def _handle_stop_aafl(self):
        global _aafl_running, _aafl_proc
        if _aafl_proc is not None:
            try:
                _aafl_proc.terminate()
            except Exception:
                pass
        _aafl_running = False
        self._send_json({"ok": True, "status": "stop_requested"})


    # ── POST /api/wccs ────────────────────────────────────────────────────────

    def _handle_api_wccs(self):
        global _last_capture
        if not _wccs_lock.acquire(blocking=False):
            self._send_json({"ok": False, "error": "WCCS already running"}, 409)
            return
        try:
            # Accept optional JSON body with a "chat" field to write to chat_latest.txt
            try:
                body = json.loads(self._read_body() or "{}")
                chat_text = body.get("chat", "").strip()
                if chat_text:
                    CHAT.write_text(chat_text, encoding="utf-8")
                    with _state_lock:
                        _last_capture = datetime.datetime.now()
            except Exception:
                pass

            py = FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable)
            script = HERE / "aafl_wccs.py"
            if not script.exists():
                self._send_json({"ok": False, "error": "aafl_wccs.py not found"}, 500)
                return
            res = subprocess.run(
                [str(py), str(script)],
                capture_output=True, text=True, timeout=300, cwd=str(HERE),
            )
            ok  = res.returncode == 0
            out = (res.stdout + res.stderr).strip()
            _auto_wccs_record(ok, "manual")
            self._send_json({"ok": ok, "result": "PASS" if ok else "FAIL",
                             "stdout": out, "time": _now_iso()})
        except subprocess.TimeoutExpired:
            self._send_json({"ok": False, "error": "Timed out after 300s"})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)})
        finally:
            _wccs_lock.release()

    # ── GET /api/timeline ─────────────────────────────────────────────────────

    def _handle_api_timeline(self):
        points = []
        if ARCHIVE_DIR.exists():
            for f in sorted(ARCHIVE_DIR.glob("STATUS_*.md")):
                try:
                    parts = f.stem.split("_")
                    if len(parts) >= 3:
                        dt_parsed = datetime.datetime.strptime(
                            parts[1] + parts[2], "%Y%m%d%H%M%S")
                    else:
                        dt_parsed = datetime.datetime.fromtimestamp(f.stat().st_mtime)
                    content = f.read_text(encoding="utf-8", errors="replace")
                    lines   = content.splitlines()
                    source  = "unknown"
                    for ln in lines[:6]:
                        if "Updated by" in ln:
                            source = ln.split("Updated by")[-1].strip(" :|")
                            break
                    snippet = ""
                    date_iso = dt_parsed.strftime("%Y-%m-%d")
                    if HISTORY_FILE.exists():
                        hist = HISTORY_FILE.read_text(encoding="utf-8", errors="replace")
                        idx  = hist.find(date_iso)
                        if idx >= 0:
                            snippet = hist[idx: idx + 300].strip()[:300]
                    points.append({
                        "filename":     f.name,
                        "date_iso":     dt_parsed.isoformat(),
                        "date_display": dt_parsed.strftime("%Y-%m-%d %H:%M"),
                        "line_count":   len(lines),
                        "pass":         "<!-- END_OF_FILE -->" in content,
                        "source":       source,
                        "snippet":      snippet,
                    })
                except Exception:
                    continue
        total = len(points)
        first = points[0]["date_display"]  if points else None
        latest = points[-1]["date_display"] if points else None
        avg_per_day = 0.0
        biggest_gap = 0.0
        if len(points) >= 2:
            dates  = [datetime.datetime.fromisoformat(p["date_iso"]) for p in points]
            gaps   = [(dates[i+1]-dates[i]).total_seconds()/3600 for i in range(len(dates)-1)]
            total_h = (dates[-1]-dates[0]).total_seconds() / 3600
            if total_h > 0:
                avg_per_day = round(total * 24 / total_h, 2)
            biggest_gap = round(max(gaps), 1)
        self._send_json({
            "points": points,
            "stats":  {"total": total, "first": first, "latest": latest,
                       "avg_per_day": avg_per_day, "biggest_gap_hours": biggest_gap},
        })

    # ── GET /api/backup ───────────────────────────────────────────────────────

    def _handle_api_backup(self):
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        fname  = params.get("f", "").strip()
        if not fname or "/" in fname or "\\" in fname or ".." in fname:
            self._send_json({"ok": False, "error": "Invalid filename"}, 400)
            return
        fpath = ARCHIVE_DIR / fname
        if not fpath.exists() or not fpath.is_file():
            self._send_json({"ok": False, "error": "File not found"}, 404)
            return
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
            self._send_json({
                "ok": True, "filename": fname, "content": content,
                "line_count": len(content.splitlines()),
                "size_bytes": fpath.stat().st_size,
            })
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── POST /api/restore ─────────────────────────────────────────────────────

    def _handle_api_restore(self):
        try:
            data = json.loads(self._read_body() or "{}")
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        fname    = data.get("filename", "").strip()
        override = data.get("content", None)
        if not fname or "/" in fname or "\\" in fname:
            self._send_json({"ok": False, "error": "Invalid filename"}, 400)
            return
        src = ARCHIVE_DIR / fname
        if not src.exists():
            self._send_json({"ok": False, "error": "Backup not found"}, 404)
            return
        ARCHIVE_DIR.mkdir(exist_ok=True)
        if STATUS_FILE.exists():
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(STATUS_FILE, ARCHIVE_DIR / f"STATUS_{stamp}.md")
        text = override if override is not None else src.read_text(encoding="utf-8", errors="replace")
        STATUS_FILE.write_text(text, encoding="utf-8")
        self._send_json({"ok": True, "restored_from": fname,
                         "line_count": len(text.splitlines())})

    # ── GET /api/diff ──────────────────────────────────────────────────────────

    def _handle_api_diff(self):
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        a_name = params.get("a", "current").strip()
        b_name = params.get("b", "previous").strip()

        def _resolve(name):
            if name == "current":
                return STATUS_FILE
            if name == "previous":
                baks = sorted(ARCHIVE_DIR.glob("STATUS_*.md")) if ARCHIVE_DIR.exists() else []
                return baks[-1] if baks else STATUS_FILE
            if name and "/" not in name and "\\" not in name:
                p = ARCHIVE_DIR / name
                if p.exists():
                    return p
            return STATUS_FILE

        path_a = _resolve(a_name)
        path_b = _resolve(b_name)
        try:
            text_a = path_a.read_text(encoding="utf-8", errors="replace").splitlines() if path_a.exists() and path_a.is_file() else []
        except Exception:
            text_a = []
        try:
            text_b = path_b.read_text(encoding="utf-8", errors="replace").splitlines() if path_b.exists() and path_b.is_file() else []
        except Exception:
            text_b = []

        hunks   = []
        added = removed = changed = 0
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, text_a, text_b).get_opcodes():
            if tag == "equal":
                for k in range(i2 - i1):
                    hunks.append({"type": "equal", "ln_a": i1+k+1, "ln_b": j1+k+1,
                                  "text_a": text_a[i1+k], "text_b": text_b[j1+k]})
            elif tag == "replace":
                ml = max(i2-i1, j2-j1)
                changed += ml
                for k in range(ml):
                    la = text_a[i1+k] if i1+k < i2 else None
                    lb = text_b[j1+k] if j1+k < j2 else None
                    hunks.append({"type": "changed",
                                  "ln_a": i1+k+1 if la is not None else None,
                                  "ln_b": j1+k+1 if lb is not None else None,
                                  "text_a": la or "", "text_b": lb or ""})
            elif tag == "delete":
                removed += i2 - i1
                for k in range(i1, i2):
                    hunks.append({"type": "removed", "ln_a": k+1, "ln_b": None,
                                  "text_a": text_a[k], "text_b": ""})
            elif tag == "insert":
                added += j2 - j1
                for k in range(j1, j2):
                    hunks.append({"type": "added", "ln_a": None, "ln_b": k+1,
                                  "text_a": "", "text_b": text_b[k]})

        self._send_json({"hunks": hunks,
                         "summary": {"added": added, "removed": removed, "changed": changed},
                         "file_a": a_name, "file_b": b_name})

    # ── GET /api/session-logs ─────────────────────────────────────────────────

    def _handle_api_session_logs(self):
        sdir = ARCHIVE_DIR / "session_logs"
        logs = []
        if sdir.exists():
            for f in sorted(sdir.glob("*.md"), reverse=True):
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                    lines   = content.splitlines()
                    logs.append({
                        "filename":   f.name,
                        "line_count": len(lines),
                        "size_bytes": f.stat().st_size,
                        "preview":    " ".join(lines[:3])[:200],
                        "mtime":      datetime.datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                    })
                except Exception:
                    continue
        self._send_json({"logs": logs})

    # ── GET /api/session-log ──────────────────────────────────────────────────

    def _handle_api_session_log(self):
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        fname  = params.get("f", "").strip()
        if not fname or "/" in fname or "\\" in fname or ".." in fname:
            self._send_json({"ok": False, "error": "Invalid filename"}, 400)
            return
        fpath = ARCHIVE_DIR / "session_logs" / fname
        if not fpath.exists() or not fpath.is_file():
            self._send_json({"ok": False, "error": "Not found"}, 404)
            return
        try:
            self._send_json({"ok": True, "filename": fname,
                             "content": fpath.read_text(encoding="utf-8", errors="replace")})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── GET /api/search ───────────────────────────────────────────────────────

    def _handle_api_search(self):
        params  = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        query   = params.get("q", "").strip().lower()
        section = params.get("section", "").strip().lower()
        if not query:
            self._send_json({"results": [], "count": 0})
            return
        results = []

        def _search(fpath, label):
            if not fpath.exists():
                return
            lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
            for i, line in enumerate(lines):
                if query in line.lower():
                    if section and section not in line.lower():
                        continue
                    results.append({
                        "source":  label,
                        "file":    fpath.name,
                        "line_n":  i + 1,
                        "match":   line,
                        "before":  lines[max(0, i-2): i],
                        "after":   lines[i+1: min(len(lines), i+3)],
                    })

        _search(HISTORY_FILE, "HISTORY.md")
        _search(ACCA_FILE,    "ACCA.md")
        sdir = ARCHIVE_DIR / "session_logs"
        if sdir.exists():
            for f in sorted(sdir.glob("*.md"), reverse=True)[:50]:
                _search(f, f"session:{f.name}")

        self._send_json({"results": results[:100], "count": len(results)})

    # ── GET /api/auto-wccs ────────────────────────────────────────────────────

    def _handle_api_auto_wccs_get(self):
        with _auto_wccs_lock:
            nxt = None
            if _auto_wccs_active and _auto_wccs_next_fire:
                nxt = max(0, int((_auto_wccs_next_fire - datetime.datetime.now()).total_seconds()))
            self._send_json({
                "active":    _auto_wccs_active,
                "interval":  _auto_wccs_interval,
                "last_save": _auto_wccs_last_save,
                "next_in_s": nxt,
                "log":       list(_auto_wccs_log),
            })

    # ── GET /dashboard-data/ and /dashboard-data/<file> ──────────────────────

    def _handle_dashboard_data(self, path: str):
        # Strip prefix
        suffix = path[len("/dashboard-data"):]  # "" or "/" or "/foo.json"
        if suffix in ("", "/"):
            # List all JSON files
            DASHBOARD_DATA.mkdir(exist_ok=True)
            files = sorted(
                f.name for f in DASHBOARD_DATA.iterdir()
                if f.suffix == ".json" and f.is_file()
            )
            self._send_json({"files": files})
            return

        # Serve specific file
        fname = suffix.lstrip("/")
        if not fname or ".." in fname or "/" in fname or "\\" in fname:
            self._send_json({"error": "Invalid filename"}, 400)
            return

        fpath = DASHBOARD_DATA / fname
        if not fpath.exists() or not fpath.is_file():
            self._send_json({"error": "Not found"}, 404)
            return

        try:
            content = fpath.read_text(encoding="utf-8")
            if fname.endswith(".json"):
                self._send_json(json.loads(content))
            else:
                body = content.encode("utf-8")
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)

    # ── GET /health-status ────────────────────────────────────────────────────

    def _handle_health_status(self):
        if LATEST_HEALTH.exists():
            try:
                data = json.loads(LATEST_HEALTH.read_text(encoding="utf-8"))
                self._send_json(data)
                return
            except Exception as exc:
                self._send_json({"error": f"Could not read latest_health.json: {exc}"}, 500)
                return
        self._send_json({
            "generated_at": None,
            "providers": [],
            "message": "No health check run yet. Run: python provider_health.py",
        })

    # ── POST /api/auto-wccs ───────────────────────────────────────────────────

    def _handle_api_auto_wccs_post(self):
        try:
            data = json.loads(self._read_body() or "{}")
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        action   = data.get("action", "").strip()
        interval = int(data.get("interval", 30))
        _auto_wccs_set(action, interval)
        with _auto_wccs_lock:
            self._send_json({"ok": True, "active": _auto_wccs_active,
                             "interval": _auto_wccs_interval})


    # ── GET /stuck-inbox ─────────────────────────────────────────────────────────

    def _handle_stuck_inbox_get(self):
        items = []
        if STUCK_INBOX_FILE.exists():
            try:
                all_items = json.loads(STUCK_INBOX_FILE.read_text(encoding="utf-8"))
                items = [i for i in all_items if i.get("status") != "resolved"]
            except Exception:
                pass
        self._send_json({"items": items, "count": len(items)})

    # ── POST /resolve-stuck ───────────────────────────────────────────────────────

    def _handle_resolve_stuck(self):
        try:
            data = json.loads(self._read_body() or "{}")
            item_id = data.get("item_id", "").strip()
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        if not item_id:
            self._send_json({"ok": False, "error": "Missing item_id"}, 400)
            return
        if not STUCK_INBOX_FILE.exists():
            self._send_json({"ok": False, "error": "stuck_inbox.json not found"}, 404)
            return
        try:
            items = json.loads(STUCK_INBOX_FILE.read_text(encoding="utf-8"))
            found = False
            for item in items:
                if item.get("item_id") == item_id:
                    item["status"] = "resolved"
                    item["resolved_at"] = _now_iso()
                    found = True
                    break
            if found:
                STUCK_INBOX_FILE.write_text(
                    json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
                )
            self._send_json({"ok": found})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── POST /run-now ─────────────────────────────────────────────────────────────

    def _handle_run_now(self):
        try:
            data = json.loads(self._read_body() or "{}")
            goal = data.get("goal", "").strip()
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        if not goal:
            self._send_json({"ok": False, "error": "Empty goal"}, 400)
            return
        try:
            with open(GOAL_QUEUE, "a", encoding="utf-8") as f:
                f.write(goal + "\n")
            self._send_json({"ok": True, "goal": goal, "queued_at": _now_iso()})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── GET /memory/knowledge ─────────────────────────────────────────────────────

    def _handle_memory_knowledge(self):
        rows = []
        try:
            import sqlite3
            if DB_PATH.exists():
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, title, content, source_type, created_at FROM knowledge "
                    "ORDER BY created_at DESC LIMIT 200"
                )
                for r in cur.fetchall():
                    rows.append({
                        "id":          r["id"],
                        "title":       r["title"],
                        "content_preview": (r["content"] or "")[:100],
                        "source":      r["source_type"],
                        "timestamp":   r["created_at"],
                    })
                conn.close()
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)
            return
        self._send_json({"rows": rows, "count": len(rows)})

    # ── GET /memory/solutions ─────────────────────────────────────────────────────

    def _handle_memory_solutions(self):
        rows = []
        try:
            import sqlite3
            if DB_PATH.exists():
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, problem, approach, ai_score, created_at "
                    "FROM solution_log ORDER BY id DESC LIMIT 200"
                )
                for r in cur.fetchall():
                    rows.append({
                        "id":               r["id"],
                        "goal":             r["problem"],
                        "solution_preview": (r["approach"] or "")[:100],
                        "score":            r["ai_score"],
                        "provider":         "—",
                        "timestamp":        r["created_at"],
                    })
                conn.close()
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)
            return
        self._send_json({"rows": rows, "count": len(rows)})

    # ── GET /memory/sources ───────────────────────────────────────────────────────

    def _handle_memory_sources(self):
        rows = []
        try:
            import sqlite3
            if DB_PATH.exists():
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute(
                    "SELECT domain, avg_score, times_used, last_used "
                    "FROM source_reputation ORDER BY avg_score DESC LIMIT 200"
                )
                for r in cur.fetchall():
                    rows.append({
                        "source_url":       r["domain"],
                        "reputation_score": r["avg_score"],
                        "times_used":       r["times_used"],
                        "last_used":        r["last_used"],
                    })
                conn.close()
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)
            return
        self._send_json({"rows": rows, "count": len(rows)})

    # ── GET /promo-queue ──────────────────────────────────────────────────────────

    def _handle_promo_queue_get(self):
        items = []
        if PROMO_QUEUE_FILE.exists():
            try:
                items = json.loads(PROMO_QUEUE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        pending = sum(1 for i in items if i.get("status") == "pending")
        self._send_json({"items": items, "pending_count": pending})

    # ── POST /approve-promo ───────────────────────────────────────────────────────

    def _handle_approve_promo(self):
        self._update_promo_item("approved")

    # ── POST /reject-promo ────────────────────────────────────────────────────────

    def _handle_reject_promo(self):
        self._update_promo_item("rejected")

    def _update_promo_item(self, new_status: str):
        try:
            data = json.loads(self._read_body() or "{}")
            item_id = data.get("item_id", "").strip()
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        if not item_id:
            self._send_json({"ok": False, "error": "Missing item_id"}, 400)
            return
        if not PROMO_QUEUE_FILE.exists():
            self._send_json({"ok": False, "error": "promo_queue.json not found"}, 404)
            return
        try:
            items = json.loads(PROMO_QUEUE_FILE.read_text(encoding="utf-8"))
            found = False
            for item in items:
                if item.get("item_id") == item_id:
                    item["status"] = new_status
                    item["updated_at"] = _now_iso()
                    found = True
                    break
            if found:
                PROMO_QUEUE_FILE.write_text(
                    json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
                )
            self._send_json({"ok": found})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── GET /acca-codes ───────────────────────────────────────────────────────────

    def _handle_acca_codes(self):
        if not ACCA_FILE.exists():
            self._send_json({"codes": [], "count": 0})
            return
        codes = []
        try:
            text = ACCA_FILE.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped.startswith("|"):
                    continue
                parts = [p.strip() for p in stripped.strip("|").split("|")]
                if len(parts) >= 2 and parts[0] and parts[0] != "Code" and not parts[0].startswith("---"):
                    codes.append({
                        "code":     parts[0],
                        "meaning":  parts[1] if len(parts) > 1 else "",
                        "added":    parts[2] if len(parts) > 2 else "",
                    })
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)
            return
        self._send_json({"codes": codes, "count": len(codes)})

    # ── GET /alp-data ─────────────────────────────────────────────────────────────

    def _handle_alp_data(self):
        if not ALP_FILE.exists():
            self._send_json({"entries": [], "count": 0})
            return
        entries = []
        try:
            text = ALP_FILE.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped.startswith("|"):
                    continue
                parts = [p.strip() for p in stripped.strip("|").split("|")]
                if (len(parts) >= 2 and parts[0]
                        and parts[0] not in ("Date", "Saving", "#")
                        and not parts[0].startswith("---")):
                    entries.append({
                        "col1": parts[0],
                        "col2": parts[1] if len(parts) > 1 else "",
                        "col3": parts[2] if len(parts) > 2 else "",
                        "col4": parts[3] if len(parts) > 3 else "",
                    })
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)
            return
        self._send_json({"entries": entries, "count": len(entries)})

    # ── POST /alp-add ─────────────────────────────────────────────────────────────

    def _handle_alp_add(self):
        try:
            data = json.loads(self._read_body() or "{}")
            entry = data.get("entry", "").strip()
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        if not entry:
            self._send_json({"ok": False, "error": "Empty entry"}, 400)
            return
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        new_row = f"| {today} | {entry} |"
        try:
            if ALP_FILE.exists():
                text = ALP_FILE.read_text(encoding="utf-8", errors="replace")
                text = text.rstrip() + "\n" + new_row + "\n"
            else:
                text = "# ALP Database\n\n| Date | Saving |\n|---|---|\n" + new_row + "\n"
            ALP_FILE.write_text(text, encoding="utf-8")
            self._send_json({"ok": True, "row": new_row})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)


    # ── GET /self-diagnosis ───────────────────────────────────────────────────────

    def _handle_self_diagnosis(self):
        import glob as _glob
        import platform

        # Python version
        py_ver = sys.version.split()[0]

        # Count .py files + total lines
        py_files_info = []
        total_lines   = 0
        for fpath in sorted(HERE.glob("*.py")):
            try:
                lines = fpath.read_text(encoding="utf-8", errors="replace").count("\n") + 1
                mtime = datetime.datetime.fromtimestamp(fpath.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                total_lines += lines
                py_files_info.append({
                    "name":     fpath.name,
                    "lines":    lines,
                    "modified": mtime,
                    "size_kb":  round(fpath.stat().st_size / 1024, 1),
                })
            except Exception:
                pass

        # Disk usage (project folder)
        try:
            total_size = sum(f.stat().st_size for f in HERE.rglob("*") if f.is_file())
            disk_mb    = round(total_size / 1024 / 1024, 2)
        except Exception:
            disk_mb = 0

        # Last git commit
        git_info = {}
        try:
            res = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%H|%s|%ai"],
                capture_output=True, text=True, timeout=5, cwd=str(HERE),
            )
            if res.returncode == 0 and res.stdout:
                parts = res.stdout.strip().split("|", 2)
                git_info = {
                    "hash":    parts[0][:10] if parts else "",
                    "message": parts[1] if len(parts) > 1 else "",
                    "date":    parts[2][:19] if len(parts) > 2 else "",
                }
        except Exception:
            pass

        # MOT report if available
        mot_report = {}
        mot_path = HEALTH_RESULTS / "full_mot_report.json"
        if mot_path.exists():
            try:
                mot_report = json.loads(mot_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Import status from MOT report
        import_map = {}
        for row in mot_report.get("results", []):
            if row.get("group") == "B":
                mod = row["name"].replace("import ", "")
                import_map[mod] = row["status"] == "PASS"

        for f in py_files_info:
            mod = f["name"].replace(".py", "")
            if mod in import_map:
                f["import_ok"] = import_map[mod]

        self._send_json({
            "python_version":  py_ver,
            "project_path":    str(HERE),
            "py_file_count":   len(py_files_info),
            "total_lines":     total_lines,
            "disk_mb":         disk_mb,
            "git":             git_info,
            "files":           py_files_info,
            "mot_report":      mot_report,
            "generated_at":    _now_iso(),
        })

    # ── POST /run-mot ─────────────────────────────────────────────────────────────

    def _handle_run_mot(self):
        if not MOT_SCRIPT.exists():
            self._send_json({"ok": False, "error": "mcc_full_mot.py not found"}, 500)
            return
        py = FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable)
        try:
            res = subprocess.run(
                [str(py), str(MOT_SCRIPT)],
                capture_output=True, text=True, timeout=120, cwd=str(HERE),
            )
            ok  = res.returncode == 0
            out = (res.stdout + res.stderr).strip()
            # Try to load the JSON report just written
            report = {}
            rpath  = HEALTH_RESULTS / "full_mot_report.json"
            if rpath.exists():
                try:
                    report = json.loads(rpath.read_text(encoding="utf-8"))
                except Exception:
                    pass
            self._send_json({"ok": ok, "stdout": out[-3000:], "report": report})
        except subprocess.TimeoutExpired:
            self._send_json({"ok": False, "error": "Timed out after 120s"})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── GET /known-issues ─────────────────────────────────────────────────────────

    def _handle_known_issues_get(self):
        DASHBOARD_DATA.mkdir(exist_ok=True)
        items = []
        if KNOWN_ISSUES.exists():
            try:
                items = json.loads(KNOWN_ISSUES.read_text(encoding="utf-8"))
            except Exception:
                pass
        self._send_json({"items": items, "count": len(items)})

    # ── POST /known-issues ────────────────────────────────────────────────────────

    def _handle_known_issues_post(self):
        try:
            data = json.loads(self._read_body() or "{}")
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        action = data.get("action", "").strip()
        DASHBOARD_DATA.mkdir(exist_ok=True)
        items = []
        if KNOWN_ISSUES.exists():
            try:
                items = json.loads(KNOWN_ISSUES.read_text(encoding="utf-8"))
            except Exception:
                pass

        if action == "add":
            desc  = data.get("description", "").strip()
            sev   = data.get("severity", "medium").strip()
            if not desc:
                self._send_json({"ok": False, "error": "Empty description"}, 400)
                return
            import uuid as _uuid
            item = {
                "id":          str(_uuid.uuid4())[:8],
                "description": desc,
                "severity":    sev,
                "date_added":  _now_iso()[:10],
                "status":      "open",
            }
            items.append(item)
            KNOWN_ISSUES.write_text(
                json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            self._send_json({"ok": True, "item": item})

        elif action == "delete":
            item_id = data.get("id", "").strip()
            before  = len(items)
            items   = [i for i in items if i.get("id") != item_id]
            KNOWN_ISSUES.write_text(
                json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            self._send_json({"ok": True, "deleted": before - len(items)})

        elif action == "set_status":
            item_id    = data.get("id", "").strip()
            new_status = data.get("status", "open").strip()
            for item in items:
                if item.get("id") == item_id:
                    item["status"] = new_status
                    break
            KNOWN_ISSUES.write_text(
                json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            self._send_json({"ok": True})

        else:
            self._send_json({"ok": False, "error": "Unknown action"}, 400)

    # ── POST /run-merge-sessions ──────────────────────────────────────────────────

    def _handle_run_merge_sessions(self):
        script = HERE / "merge_sessions.py"
        if not script.exists():
            self._send_json({"ok": False, "error": "merge_sessions.py not found"}, 500)
            return
        py = FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable)
        try:
            t = threading.Thread(
                target=lambda: subprocess.run(
                    [str(py), str(script)],
                    capture_output=True, text=True, timeout=120, cwd=str(HERE),
                ),
                daemon=True,
            )
            t.start()
            self._send_json({"ok": True, "status": "running",
                             "message": "merge_sessions.py started in background"})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── POST /run-health-check ────────────────────────────────────────────────────

    def _handle_run_health_check(self):
        ph_script = HERE / "provider_health.py"
        if not ph_script.exists():
            self._send_json({"ok": False, "error": "provider_health.py not found"}, 500)
            return
        py = FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable)
        try:
            t = threading.Thread(
                target=lambda: subprocess.run(
                    [str(py), str(ph_script)],
                    capture_output=True, text=True, timeout=120, cwd=str(HERE),
                ),
                daemon=True,
            )
            t.start()
            self._send_json({"ok": True, "status": "running",
                             "message": "provider_health.py started in background"})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 1: GET /modules ───────────────────────────────────────────────────

    def _handle_modules_get(self):
        try:
            from module_loader import get_all_modules
            self._send_json({"ok": True, "modules": get_all_modules()})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 1: POST /toggle-module ───────────────────────────────────────────

    def _handle_toggle_module(self):
        try:
            data = json.loads(self._read_body() or "{}")
            module_id = data.get("id", "").strip()
            enabled   = data.get("enabled")
            if not module_id or enabled is None:
                self._send_json({"ok": False, "error": "id and enabled required"}, 400)
                return
            from module_loader import toggle_module
            ok = toggle_module(module_id, bool(enabled))
            self._send_json({"ok": ok})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 2: GET /presets ───────────────────────────────────────────────────

    def _handle_presets_get(self):
        try:
            from preset_manager import list_presets
            self._send_json({"ok": True, "presets": list_presets()})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 2: POST /presets/save ────────────────────────────────────────────

    def _handle_presets_save(self):
        try:
            data  = json.loads(self._read_body() or "{}")
            name  = data.get("name", "").strip()
            state = data.get("state", {})
            if not name:
                self._send_json({"ok": False, "error": "name required"}, 400)
                return
            from preset_manager import save_preset
            ok = save_preset(name, state)
            self._send_json({"ok": ok})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 2: GET /presets/load?name=X ──────────────────────────────────────

    def _handle_presets_load(self):
        try:
            qs   = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            name = (qs.get("name", [""])[0]).strip()
            if not name:
                self._send_json({"ok": False, "error": "name required"}, 400)
                return
            from preset_manager import load_preset
            state = load_preset(name)
            if state is None:
                self._send_json({"ok": False, "error": "Preset not found"}, 404)
            else:
                self._send_json({"ok": True, "name": name, "state": state})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 2: POST /presets/delete ──────────────────────────────────────────

    def _handle_presets_delete(self):
        try:
            data = json.loads(self._read_body() or "{}")
            name = data.get("name", "").strip()
            if not name:
                self._send_json({"ok": False, "error": "name required"}, 400)
                return
            from preset_manager import delete_preset
            ok = delete_preset(name)
            self._send_json({"ok": ok})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 3: GET /aafl-settings ────────────────────────────────────────────

    def _handle_aafl_settings_get(self):
        try:
            if AAFL_SETTINGS.exists():
                cfg = json.loads(AAFL_SETTINGS.read_text(encoding="utf-8"))
            else:
                cfg = {}
            self._send_json({"ok": True, "settings": cfg})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 3: POST /aafl-settings ───────────────────────────────────────────

    def _handle_aafl_settings_post(self):
        try:
            data = json.loads(self._read_body() or "{}")
            if AAFL_SETTINGS.exists():
                existing = json.loads(AAFL_SETTINGS.read_text(encoding="utf-8"))
            else:
                existing = {}
            existing.update(data)
            AAFL_SETTINGS.write_text(json.dumps(existing, indent=2, ensure_ascii=False),
                                     encoding="utf-8")
            self._send_json({"ok": True, "settings": existing})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 4: GET /retry-log ─────────────────────────────────────────────────

    def _handle_retry_log_get(self):
        try:
            if RETRY_LOG.exists():
                entries = json.loads(RETRY_LOG.read_text(encoding="utf-8"))
            else:
                entries = []
            self._send_json({"ok": True, "entries": entries})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 5: POST /suggest-provider ────────────────────────────────────────

    def _handle_suggest_provider(self):
        try:
            data      = json.loads(self._read_body() or "{}")
            goal_text = data.get("goal", "").strip()
            if not goal_text:
                self._send_json({"ok": False, "error": "goal required"}, 400)
                return
            from smart_suggester import suggest_provider
            suggestion = suggest_provider(goal_text)
            self._send_json({"ok": True, **suggestion})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 6: POST /run-chain ────────────────────────────────────────────────

    def _handle_run_chain(self):
        try:
            data     = json.loads(self._read_body() or "{}")
            goal     = data.get("goal", "").strip()
            provider = data.get("provider")
            if not goal:
                self._send_json({"ok": False, "error": "goal required"}, 400)
                return
            py = FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable)
            def _bg():
                subprocess.run(
                    [str(py), str(HERE / "chain_runner.py"), goal],
                    capture_output=True, text=True, timeout=300, cwd=str(HERE),
                )
            threading.Thread(target=_bg, daemon=True).start()
            self._send_json({"ok": True, "status": "running", "goal": goal})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 6: GET /chain-status ─────────────────────────────────────────────

    def _handle_chain_status(self):
        try:
            from chain_runner import get_chain_status
            self._send_json({"ok": True, **get_chain_status()})
        except Exception as exc:
            self._send_json({"ok": True, "running": False, "error": str(exc)})

    # ── Feature 6: GET /chain-log ─────────────────────────────────────────────────

    def _handle_chain_log_get(self):
        try:
            if CHAIN_LOG.exists():
                entries = json.loads(CHAIN_LOG.read_text(encoding="utf-8"))
            else:
                entries = []
            self._send_json({"ok": True, "entries": entries})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 7: POST /scout-timer/start ───────────────────────────────────────

    def _handle_scout_timer_start(self):
        try:
            data     = json.loads(self._read_body() or "{}")
            goal     = data.get("goal", "").strip()
            hours    = float(data.get("hours", 0))
            interval = int(data.get("interval_minutes", 30))
            if not goal:
                self._send_json({"ok": False, "error": "goal required"}, 400)
                return
            # Clear any existing stop flag
            if SCOUT_TIMER_STOP.exists():
                SCOUT_TIMER_STOP.unlink()
            py = FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable)
            args = [str(py), str(HERE / "scout_timer.py"), goal,
                    "--interval", str(interval)]
            if hours > 0:
                args += ["--hours", str(hours)]
            threading.Thread(
                target=lambda: subprocess.run(
                    args, capture_output=True, text=True, cwd=str(HERE),
                ),
                daemon=True,
            ).start()
            self._send_json({"ok": True, "status": "started", "goal": goal,
                             "hours": hours, "interval_minutes": interval})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 7: POST /scout-timer/stop ────────────────────────────────────────

    def _handle_scout_timer_stop(self):
        try:
            SCOUT_TIMER_STOP.write_text("STOP", encoding="utf-8")
            self._send_json({"ok": True, "status": "stop_requested"})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 7: GET /scout-timer/status ───────────────────────────────────────

    def _handle_scout_timer_status(self):
        try:
            from scout_timer import get_status
            self._send_json({"ok": True, **get_status()})
        except Exception as exc:
            self._send_json({"ok": True, "running": False, "error": str(exc)})

    # ── Feature 8: GET /sources-library ──────────────────────────────────────────

    def _handle_sources_library_get(self):
        try:
            from source_library_manager import get_sources
            qs     = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            topic  = (qs.get("topic", [""])[0]).strip() or None
            self._send_json({"ok": True, "sources": get_sources(topic_filter=topic)})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 8: POST /sources-library/add ─────────────────────────────────────

    def _handle_sources_library_add(self):
        try:
            data = json.loads(self._read_body() or "{}")
            url  = data.get("url", "").strip()
            if not url:
                self._send_json({"ok": False, "error": "url required"}, 400)
                return
            from source_library_manager import add_source
            ok = add_source(
                url=url,
                domain=data.get("domain", ""),
                description=data.get("description", ""),
                tags=data.get("tags", []),
            )
            self._send_json({"ok": ok})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 9: GET /stuck-inbox/summary ──────────────────────────────────────

    def _handle_stuck_summary_get(self):
        try:
            from stuck_inbox import get_stuck_summary
            self._send_json({"ok": True, **get_stuck_summary()})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 9: POST /stuck-inbox/bulk-resolve ─────────────────────────────────

    def _handle_stuck_bulk_resolve(self):
        try:
            data     = json.loads(self._read_body() or "{}")
            item_ids = data.get("item_ids", [])
            if not item_ids:
                self._send_json({"ok": False, "error": "item_ids required"}, 400)
                return
            from stuck_inbox import bulk_resolve
            count = bulk_resolve(item_ids)
            self._send_json({"ok": True, "resolved": count})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 10: GET /storage ──────────────────────────────────────────────────

    def _handle_storage_get(self):
        try:
            from storage_manager import check_all_slots
            self._send_json({"ok": True, **check_all_slots()})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Feature 10: GET /storage/report ──────────────────────────────────────────

    def _handle_storage_report(self):
        try:
            from storage_manager import generate_weekly_report
            self._send_json({"ok": True, "report": generate_weekly_report()})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)


    # ── Build 1 Step B: GET /wccs/save-log ───────────────────────────────────

    def _handle_wccs_save_log(self):
        entries = []
        if WCCS_LOG_MD.exists():
            try:
                text  = WCCS_LOG_MD.read_text(encoding="utf-8", errors="replace")
                lines = text.splitlines()
                for line in lines:
                    stripped = line.strip()
                    if not stripped.startswith("|"):
                        continue
                    parts = [p.strip() for p in stripped.strip("|").split("|")]
                    if (len(parts) >= 2
                            and parts[0]
                            and parts[0] not in ("#", "Date", "")
                            and not parts[0].startswith("---")):
                        entries.append({
                            "version": parts[0],
                            "date":    parts[1] if len(parts) > 1 else "",
                            "session": parts[2] if len(parts) > 2 else "",
                            "focus":   parts[3] if len(parts) > 3 else "",
                            "alp":     parts[4] if len(parts) > 4 else "",
                        })
            except Exception as exc:
                self._send_json({"ok": False, "error": str(exc)}, 500)
                return
        last20 = list(reversed(entries))[:20]
        self._send_json({"ok": True, "entries": last20, "total": len(entries)})

    # ── Build 1 Step B: GET /wccs/history-search?q= ──────────────────────────

    def _handle_wccs_history_search(self):
        qs    = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        query = (qs.get("q", [""])[0]).strip().lower()
        if not query:
            self._send_json({"results": [], "count": 0})
            return
        results = []

        def _search(fpath, label):
            if not fpath.exists():
                return
            lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
            for i, line in enumerate(lines):
                if query in line.lower():
                    results.append({
                        "source": label,
                        "line_n": i + 1,
                        "match":  line,
                        "before": lines[max(0, i-2): i],
                        "after":  lines[i+1: min(len(lines), i+3)],
                    })

        _search(HISTORY_FILE, "HISTORY.md")
        _search(ACCA_FILE,    "ACCA.md")
        self._send_json({"results": results[:100], "count": len(results), "query": query})

    # ── Build 1 Step B: GET /wccs/session-logs ───────────────────────────────

    def _handle_wccs_session_logs(self):
        logs  = []
        sdir  = SESSION_LOGS_DIR
        if sdir.exists():
            for f in sorted(sdir.glob("*.md"), reverse=True):
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                    lines   = content.splitlines()
                    logs.append({
                        "filename":   f.name,
                        "line_count": len(lines),
                        "size_bytes": f.stat().st_size,
                        "preview":    " ".join(lines[:3])[:200],
                        "mtime":      datetime.datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                        "content":    content,
                    })
                except Exception:
                    continue
        self._send_json({"ok": True, "logs": logs, "count": len(logs)})

    # ── Build 1 Step B: GET /wccs/versions ───────────────────────────────────

    def _handle_wccs_versions(self):
        versions = []
        if ARCHIVE_DIR.exists():
            for f in sorted(ARCHIVE_DIR.glob("STATUS_*.md"), reverse=True)[:10]:
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                    parts   = f.stem.split("_")
                    if len(parts) >= 3:
                        dt = datetime.datetime.strptime(parts[1] + parts[2], "%Y%m%d%H%M%S")
                        display = dt.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        display = f.name
                    versions.append({
                        "filename":    f.name,
                        "display":     display,
                        "line_count":  len(content.splitlines()),
                        "size_bytes":  f.stat().st_size,
                        "content":     content,
                    })
                except Exception:
                    continue
        self._send_json({"ok": True, "versions": versions})

    # ── Build 1 Step B: POST /wccs/restore ───────────────────────────────────

    def _handle_wccs_restore(self):
        try:
            data    = json.loads(self._read_body() or "{}")
            fname   = data.get("filename", "").strip()
            content = data.get("content", None)
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        if not fname or "/" in fname or "\\" in fname or ".." in fname:
            self._send_json({"ok": False, "error": "Invalid filename"}, 400)
            return
        src = ARCHIVE_DIR / fname
        if not src.exists():
            self._send_json({"ok": False, "error": "Version not found"}, 404)
            return
        if STATUS_FILE.exists():
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(STATUS_FILE, ARCHIVE_DIR / f"STATUS_{stamp}.md")
        text = content if content is not None else src.read_text(encoding="utf-8", errors="replace")
        STATUS_FILE.write_text(text, encoding="utf-8")
        self._send_json({"ok": True, "restored_from": fname, "line_count": len(text.splitlines())})

    # ── Build 1 Step B: POST /wccs/diff ──────────────────────────────────────

    def _handle_wccs_diff(self):
        try:
            data  = json.loads(self._read_body() or "{}")
            a_nm  = data.get("a", "").strip()
            b_nm  = data.get("b", "").strip()
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return

        def _resolve(name):
            if not name or "/" in name or "\\" in name or ".." in name:
                return None
            p = ARCHIVE_DIR / name
            return p if p.exists() else None

        pa = _resolve(a_nm)
        pb = _resolve(b_nm)
        if pa is None or pb is None:
            self._send_json({"ok": False, "error": "One or both files not found"}, 404)
            return

        lines_a = pa.read_text(encoding="utf-8", errors="replace").splitlines()
        lines_b = pb.read_text(encoding="utf-8", errors="replace").splitlines()

        hunks   = []
        added = removed = changed = 0
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, lines_a, lines_b).get_opcodes():
            if tag == "equal":
                for k in range(i2 - i1):
                    hunks.append({"type": "equal",
                                  "ln_a": i1+k+1, "ln_b": j1+k+1,
                                  "text_a": lines_a[i1+k], "text_b": lines_b[j1+k]})
            elif tag == "replace":
                ml = max(i2-i1, j2-j1)
                changed += ml
                for k in range(ml):
                    la = lines_a[i1+k] if i1+k < i2 else None
                    lb = lines_b[j1+k] if j1+k < j2 else None
                    hunks.append({"type": "changed",
                                  "ln_a": i1+k+1 if la is not None else None,
                                  "ln_b": j1+k+1 if lb is not None else None,
                                  "text_a": la or "", "text_b": lb or ""})
            elif tag == "delete":
                removed += i2 - i1
                for k in range(i1, i2):
                    hunks.append({"type": "removed",
                                  "ln_a": k+1, "ln_b": None,
                                  "text_a": lines_a[k], "text_b": ""})
            elif tag == "insert":
                added += j2 - j1
                for k in range(j1, j2):
                    hunks.append({"type": "added",
                                  "ln_a": None, "ln_b": k+1,
                                  "text_a": "", "text_b": lines_b[k]})

        self._send_json({
            "ok": True,
            "hunks": hunks,
            "summary": {"added": added, "removed": removed, "changed": changed},
            "file_a": a_nm, "file_b": b_nm,
        })


    # ── MCP: GET /api/status ─────────────────────────────────────────────────────

    def _handle_api_status_md(self):
        content = ""
        if STATUS_FILE.exists():
            try:
                content = STATUS_FILE.read_text(encoding="utf-8", errors="replace")
            except Exception as exc:
                self._send_json({"error": str(exc)}, 500)
                return
        self._send_json({"content": content, "file": str(STATUS_FILE), "exists": STATUS_FILE.exists()})

    # ── MCP: GET /api/history ─────────────────────────────────────────────────────

    def _handle_api_history_md(self):
        content = ""
        if HISTORY_FILE.exists():
            try:
                content = HISTORY_FILE.read_text(encoding="utf-8", errors="replace")
            except Exception as exc:
                self._send_json({"error": str(exc)}, 500)
                return
        self._send_json({"content": content, "file": str(HISTORY_FILE), "exists": HISTORY_FILE.exists()})

    # ── MCP: GET /api/health ──────────────────────────────────────────────────────

    def _handle_api_health(self):
        last_save = None
        try:
            if SESSION_LOGS_DIR.exists():
                files = [f for f in SESSION_LOGS_DIR.iterdir() if f.is_file()]
                if files:
                    newest = max(files, key=lambda f: f.stat().st_mtime)
                    last_save = datetime.datetime.fromtimestamp(
                        newest.stat().st_mtime
                    ).strftime("%Y-%m-%dT%H:%M:%S")
        except Exception:
            pass

        provider_count = 0
        try:
            env_file = HERE / ".env"
            if env_file.exists():
                lines = env_file.read_text(encoding="utf-8", errors="replace").splitlines()
                provider_count = sum(
                    1 for ln in lines
                    if "=" in ln and not ln.strip().startswith("#") and ln.split("=", 1)[1].strip()
                )
        except Exception:
            pass

        self._send_json({
            "status":    "ok",
            "last_save": last_save,
            "providers": provider_count,
        })


class ThreadingServer(http.server.ThreadingHTTPServer):
    pass


def main():
    server = ThreadingServer((HOST, PORT), MCCHandler)
    print(f"[MCC] MCC Server running at http://{HOST}:{PORT}")
    print(f"[MCC] Project folder: {HERE}")
    print(f"[MCC] chat_latest.txt: {CHAT}")
    print(f"[MCC] Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[MCC] Stopped.")


if __name__ == "__main__":
    main()
