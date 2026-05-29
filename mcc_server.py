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
HOST         = "127.0.0.1"
HERE         = Path(__file__).parent
CHAT         = HERE / "chat_latest.txt"
SCOUT_OUTPUT = HERE / "scout_output"
SCOUT_LATEST = SCOUT_OUTPUT / "latest.txt"
SCOUT_CONFIG = HERE / "chief_scout_config.json"
PYTHON       = sys.executable
from config import PYTHON_EXE as FULL_PYTHON  # noqa: E402
ARCHIVE_DIR  = HERE / "archive_dead"
STATUS_FILE  = HERE / "STATUS.md"
HISTORY_FILE = HERE / "HISTORY.md"
ACCA_FILE    = HERE / "ACCA.md"
WCCS_ERROR_LOG = HERE / "wccs_errors.log"
STATUS_SANITY_THRESHOLD = 0.90
STATUS_LINECOUNT_JSON    = HERE / "data" / "status_linecount.json"

def _log_status_error(msg):
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    with open(WCCS_ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {msg}\n")

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
MEDICAL_SCRIPT   = HERE / "mcc_medical.py"
MEDICAL_DIR      = HERE / "health_results" / "mcc_medical"
MEDICAL_HISTORY  = MEDICAL_DIR / "mcc_medical_history.json"

# ── Feature paths ──────────────────────────────────────────────────────────────
MODULE_REGISTRY  = HERE / "modules" / "module_registry.json"
PRESETS_DIR      = HERE / "presets"
AAFL_SETTINGS    = HERE / "aafl_config.json"
RETRY_LOG        = HEALTH_RESULTS / "retry_log.json"
CHAIN_LOG        = HEALTH_RESULTS / "chain_log.json"
SOURCES_LIBRARY  = HERE / "sources_library.json"
STORAGE_CFG      = HERE / "storage_config.json"
SCOUT_TIMER_STOP = HERE / "scout_timer_stop.flag"
WCCS_LOG_MD        = HERE / "wccs_log.md"
SESSION_LOGS_DIR   = HERE / "session_logs"
WORKFLOW_PRESETS   = HERE / "aafl_workflow_presets.json"
LOOP_PRESETS       = HERE / "aafl_loop_presets.json"

# ── LLOW paths (OCB-D) ───────────────────────────────────────────────────────
LLOW_ELEMENTS_FILE  = HERE / "data" / "llow_elements.json"
LLOW_ARROWS_FILE    = HERE / "data" / "llow_arrows.json"
LLOW_WORKFLOWS_DIR  = HERE / "data" / "llow_workflows"
# ── OCB-N paths ───────────────────────────────────────────────────────────────
TIMELINE_FILE       = HERE / "data" / "project_timeline.json"
SCOUT_SWARM_STATE   = HERE / "data" / "scout_swarm_state.json"
# ── OCB-O: OCB Runner paths ──────────────────────────────────────────────────
OCB_STATUS_FILE     = HERE / "data" / "ocb_status.json"
CLACHR_RESPONSE     = HERE / "data" / "clachr_response.json"
# ── OCB-P: Unified session state ─────────────────────────────────────────────
SESSION_STATE_FILE  = HERE / "data" / "session_state.json"
PROVIDER_DIAG_FILE  = HERE / "data" / "provider_diagnosis.json"
_SS_DEFAULTS = {
    "session_id": "", "started_at": "",
    "current_task": {"type": "", "description": "", "subsystem": "", "status": "idle", "started_at": ""},
    "last_result": {"task": "", "status": "", "mot_score": "", "files_changed": [], "completed_at": ""},
    "provider_health": {"healthy_count": 0, "total": 14, "last_checked": ""},
    "watchdog_status": "OFF",
    "last_save": {"type": "", "timestamp": "", "file": ""},
    "aafl_score": None, "cost_7d": None, "active_ocb_run_id": "", "next_priority": "",
}

# ── Self-Health paths (OCB-A / OCB-B) ────────────────────────────────────────
SH_REGISTRY     = HERE / "data" / "element_registry.json"
SH_HEALTH_DB    = HERE / "data" / "health.db"
SH_CONFIG       = HERE / "data" / "self_health_config.json"
SH_SOLUTIONS    = HERE / "data" / "solution_database.json"
AF_PROPOSALS    = HERE / "data" / "fix_proposals.json"
AF_HISTORY_FILE = HERE / "data" / "fix_history.json"

# ── B2 paths ──────────────────────────────────────────────────────────────────
KANBAN_JSON       = HERE / "kanban_board.json"
ACTIVITY_LOG      = HERE / "activity_log.json"
MCC_PREFS         = HERE / "mcc_prefs.json"
BUDGET_CAPS       = HERE / "budget_caps.json"
BENCHMARK_RESULTS = HERE / "benchmark_results.json"
KEYBIND_PROFILES  = HERE / "keybind_profiles"
SCOUT_BRIEFINGS   = HERE / "scout_briefings"
SCOUT_CFG_EXTRA   = HERE / "scout_config.json"
B2_CHAIN_FILE     = HERE / "b2_chain.json"
B2_STEP_FILE      = HERE / "b2_step_state.json"
B2_BLOCKED        = HERE / "b2_blocked_sources.json"
COST_LOG          = HERE / "data" / "cost_log.txt"
WORK_REPORT       = HERE / "data" / "work_report.json"
WORK_CHECKER      = HERE / "work_checker.py"

_state_lock  = threading.Lock()
_wccs_lock   = threading.Lock()
_scout_lock  = threading.Lock()
_aafl_lock   = threading.Lock()

_last_wccs: dict = {"result": None, "time": None, "stdout": ""}
_last_capture: datetime.datetime | None = None
_scout_running: bool = False
_scout_proc          = None  # subprocess.Popen handle (killable)
_scout_start_time    = None  # datetime when scout started (for 120s auto-clear)
_aafl_running: bool  = False
_aafl_proc           = None  # subprocess.Popen handle

# ── OCB-N: Scout Swarm LLOW LEL state ────────────────────────────────────────
_swarm_sessions: dict = {}   # session_id → {status, results_count, params, time_limit, proc, started}
_swarm_lock = threading.Lock()

# ── Auto-WCCS state ───────────────────────────────────────────────────────────
_auto_wccs_timer     = None
_auto_wccs_interval  = 30        # minutes
_auto_wccs_active    = False
_auto_wccs_last_save = None
_auto_wccs_next_fire = None      # datetime
_auto_wccs_log       = []        # last 5 entries
_auto_wccs_lock      = threading.Lock()


def _run_scout_bg(goal: str):
    global _scout_running, _scout_proc, _scout_start_time
    SCOUT_OUTPUT.mkdir(exist_ok=True)
    try:
        with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
            f.write(f"[RUNNING] Goal: {goal}\n[STARTED] {_now_iso()}\n")
        cmd = [PYTHON, str(HERE / "chief_scout.py")]
        if goal:
            cmd.append(goal)
        _scout_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(HERE))
        stdout, stderr = _scout_proc.communicate(timeout=120)
        output = (stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")).strip()
        with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
            f.write(output if output else "[DONE] No output received")
    except subprocess.TimeoutExpired:
        if _scout_proc:
            _scout_proc.kill()
        with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
            f.write("[ERROR] Scout timed out after 120s")
    except Exception as exc:
        with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
            f.write(f"[ERROR] {exc}")
    finally:
        _scout_proc = None
        _scout_start_time = None
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

    def address_string(self):
        # Override to skip reverse-DNS lookup (which adds ~2s per request on some systems)
        return self.client_address[0]

    def log_message(self, fmt, *args):
        print(f"[MCC] {self.address_string()} -- {fmt % args}")

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
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
            # ── Feature 10 + OCB-C storage ─────────────────────────────────────
            elif path == "/storage":
                self._handle_storage_get()
            elif path == "/storage/report":
                self._handle_storage_report()
            elif path == "/api/storage/stats":
                self._handle_storage_stats()
            elif path == "/api/storage/largest":
                self._handle_storage_largest()
            elif path == "/api/storage/detailed":
                self._handle_storage_detailed()
            elif path == "/api/storage/forecast":
                self._handle_storage_forecast()
            elif path == "/api/storage/treemap":
                self._handle_storage_treemap()
            elif path == "/api/storage/archive-history":
                self._handle_storage_archive_history()
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
            elif path == "/api/acca":
                self._handle_api_acca_md()
            elif path == "/api/health":
                self._handle_api_health()
            # ── Fix: AAFL live + bridge + workflow GET ──────────────────────────
            elif path == "/aafl/last-result":
                self._handle_aafl_last_result()
            elif path == "/aafl/live":
                self._handle_aafl_live()
            elif path == "/aafl/bridge-result":
                self._handle_aafl_bridge_result()
            elif path == "/aafl/workflow-presets":
                self._handle_workflow_presets_get()
            # ── B2 GET endpoints ───────────────────────────────────────────────
            elif path == "/b2/kanban":
                self._handle_b2_kanban_get()
            elif path == "/b2/activity":
                self._handle_b2_activity_get()
            elif path == "/b2/aafl-runs":
                self._handle_b2_aafl_runs()
            elif path == "/b2/prefs":
                self._handle_b2_prefs_get()
            elif path == "/b2/budget-caps":
                self._handle_b2_budget_caps_get()
            elif path == "/b2/costs":
                self._handle_b2_costs_get()
            elif path == "/b2/keybind-profiles":
                self._handle_b2_kbp_get()
            elif path == "/b2/source-health":
                self._handle_b2_source_health()
            # ── Task 3: Scout Results + Task Inbox ─────────────────────────────
            elif path == "/scout/results":
                self._handle_scout_results_json()
            elif path == "/api/task-inbox":
                self._handle_api_task_inbox_get()
            elif path == "/api/processes":
                self._handle_api_processes()
            elif path == "/api/medical-report":
                self._handle_api_medical_report()
            elif path == "/api/medical-history":
                self._handle_api_medical_history()
            # ── Build 3 GET endpoints ──────────────────────────────────────────
            elif path == "/health/system":
                self._handle_b3_system_health()
            elif path == "/b3/urgency":
                self._handle_b3_urgency_get()
            elif path == "/b3/design-presets":
                self._handle_b3_design_presets_get()
            elif path == "/b3/scout-ai-summary":
                self._handle_b3_scout_ai_summary()
            elif path == "/b2/loop-presets":
                self._handle_b2_loop_presets_get()
            elif path.startswith("/b2/loop-preset/"):
                name = path[len("/b2/loop-preset/"):]
                self._handle_b2_loop_preset_get(name)
            elif path == "/api/statuscheck":
                self._handle_api_statuscheck()
            elif path == "/api/old-saves-report":
                self._handle_api_old_saves_report()
            elif path == "/api/ibr-scan":
                self._handle_api_ibr_scan()
            elif path == "/api/ibr-latest":
                self._handle_api_ibr_latest()
            elif path == "/api/missions":
                self._handle_api_missions_get()
            # ── Work Checker GET endpoints ─────────────────────────────────────
            elif path == "/api/work-checker/report":
                self._handle_wc_report()
            elif path == "/api/work-checker/requeue":
                self._handle_wc_requeue()
            elif path == "/api/work-checker/orphaned":
                self._handle_wc_orphaned()
            # ── OCB-A / OCB-B: Self-Health endpoints ──────────────────────────
            elif path == "/api/self-health/registry":
                self._handle_sh_registry()
            elif path == "/api/self-health/last-run":
                self._handle_sh_last_run()
            elif path == "/api/self-health/config":
                self._handle_sh_config_get()
            elif path == "/api/self-health/solutions":
                self._handle_sh_solutions()
            elif path == "/api/self-health/history":
                self._handle_sh_history()
            elif path == "/api/self-health/results":
                self._handle_sh_results()
            elif path == "/api/self-health/element-history":
                self._handle_sh_element_history()
            # ── OCB-B: Auto-Fix endpoints ──────────────────────────────────────
            elif path == "/api/auto-fix/proposals":
                self._handle_af_proposals()
            elif path == "/api/auto-fix/history":
                self._handle_af_history()
            # ── OCB-C: Storage + System endpoints ─────────────────────────────
            elif path == "/api/storage/stats":
                self._handle_storage_stats()
            elif path == "/api/storage/largest":
                self._handle_storage_largest()
            elif path == "/api/system/snapshot":
                self._handle_system_snapshot()
            elif path == "/api/system/cpu":
                self._handle_system_cpu()
            elif path == "/api/system/ram":
                self._handle_system_ram()
            elif path == "/api/system/gpu":
                self._handle_system_gpu()
            elif path == "/api/system/ai-allocation":
                self._handle_system_ai_allocation()
            elif path == "/api/health/latest":
                self._handle_health_latest()
            # ── OCB-D: LLOW ─────────────────────────────────────────────────────
            elif path == "/api/llow/elements":
                self._handle_llow_elements()
            elif path == "/api/llow/arrows":
                self._handle_llow_arrows()
            elif path == "/api/llow/workflows":
                self._handle_llow_list_workflows()
            elif path.startswith("/api/llow/workflow/"):
                name = urllib.parse.unquote(path[len("/api/llow/workflow/"):])
                self._handle_llow_get_workflow(name)
            # ── OCB-N: Scout Swarm + Timeline ────────────────────────────────
            elif path == "/api/llow/scout-swarm":
                self._handle_scout_swarm_get()
            elif path == "/api/timeline-data":
                self._handle_api_timeline_data()
            # ── OCB-N: Work Checker new panels ───────────────────────────────
            elif path == "/api/work-checker/timeline":
                self._handle_wc_timeline()
            elif path == "/api/work-checker/checklist":
                self._handle_wc_checklist()
            elif path == "/api/work-checker/action-plan":
                self._handle_wc_action_plan()
            # ── Instructions keeper ────────────────────────────────────────────
            elif path == "/api/instructions":
                self._handle_api_instructions()
            elif path.startswith("/api/instructions/"):
                element_id = path[len("/api/instructions/"):]
                self._handle_api_instructions_element(element_id)
            # ── OCB-J: Safety Status + CLACHR + AFNA ──────────────────────────
            elif path == "/api/safety-status":
                self._handle_safety_status()
            elif path == "/api/clachr/queue":
                self._handle_clachr_queue()
            elif path == "/api/clachr/results":
                self._handle_clachr_results()
            elif path == "/api/stuck/afna-suggestions":
                self._handle_stuck_afna_suggestions()
            # ── OCB-K: MOT live SSE + project endpoints ─────────────────────
            elif path == "/api/mot/live":
                self._handle_mot_live_sse()
            elif path == "/api/project-vision":
                self._handle_project_vision()
            elif path == "/api/project-awareness":
                self._handle_project_awareness()
            elif path == "/api/resources/snapshot":
                self._handle_resources_snapshot()
            elif path == "/api/aafl/errors":
                self._handle_aafl_errors()
            # ── OCB-L: Phase 3 — Provider health (enriched) ──────────────────
            elif path == "/api/provider-health":
                self._handle_provider_health_enriched()
            # ── OCB-L: Phase 4 — Resource drill-downs ────────────────────────
            elif path == "/api/resources/cpu-detail":
                self._handle_resources_cpu_detail()
            elif path == "/api/resources/ram-detail":
                self._handle_resources_ram_detail()
            elif path == "/api/resources/disk-detail":
                self._handle_resources_disk_detail()
            elif path == "/api/resources/gpu-detail":
                self._handle_resources_gpu_detail()
            elif path == "/api/resources/lmstudio-detail":
                self._handle_resources_lmstudio_detail()
            # ── OCB-L: Phase 5 — Help tab ─────────────────────────────────────
            elif path == "/api/help/history":
                self._handle_help_history()
            # ── OCB-O: Health run history from health.db ───────────────────────
            elif path == "/api/health/history":
                self._handle_health_run_history()
            # ── OCB-L: Phase 6 — Settings persistence ─────────────────────────
            elif path == "/api/settings":
                self._handle_settings_get()
            # ── OCB-O: Watchdog status ─────────────────────────────────────────
            elif path == "/api/watchdog/status":
                self._handle_watchdog_status()
            # ── OCB-O: Code Editor ────────────────────────────────────────────
            elif path == "/api/code/files":
                self._handle_code_files()
            elif path == "/api/code/read":
                self._handle_code_read()
            # ── OCB-O: OCB Runner ─────────────────────────────────────────────
            elif path.startswith("/api/ocb/status/"):
                run_id = path[len("/api/ocb/status/"):]
                self._handle_ocb_status(run_id)
            # ── MCCM / Chief Detective ─────────────────────────────────────────
            elif path == "/api/mccm/status":
                self._handle_mccm_status()
            elif path == "/api/mccm/detective":
                self._handle_mccm_detective()
            elif path == "/api/mccm/alerts":
                self._handle_mccm_alerts()
            # ── OCB-P: Unified session state ───────────────────────────────────
            elif path == "/api/session-state":
                self._handle_session_state_get()
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
            # ── Fix: AAFL run-goal + scout strategy + bridge + workflow POST ────
            elif path == "/aafl/run-goal":
                self._handle_aafl_run_goal()
            elif path == "/scout/strategy":
                self._handle_scout_strategy()
            elif path == "/scout/force-stop":
                self._handle_scout_force_stop()
            elif path == "/scout/stop":
                self._handle_scout_force_stop()     # alias for force-stop
            elif path == "/aafl/stop":
                self._handle_stop_aafl()            # alias for stop-aafl
            elif path == "/aafl/scout-bridge":
                self._handle_aafl_scout_bridge()
            elif path == "/aafl/workflow":
                self._handle_workflow_save()
            # ── B2 POST endpoints ──────────────────────────────────────────────
            elif path == "/b2/kanban":
                self._handle_b2_kanban_post()
            elif path == "/b2/activity":
                self._handle_b2_activity_post()
            elif path == "/b2/activity/summarise":
                self._handle_b2_activity_summarise()
            elif path == "/b2/run-tag":
                self._handle_b2_run_tag()
            elif path == "/b2/run-notes":
                self._handle_b2_run_notes()
            elif path == "/b2/prefs":
                self._handle_b2_prefs_post()
            elif path == "/b2/budget-caps":
                self._handle_b2_budget_caps_post()
            elif path == "/b2/benchmark":
                self._handle_b2_benchmark()
            elif path == "/b2/second-opinion":
                self._handle_b2_second_opinion()
            elif path == "/b2/step-mode":
                self._handle_b2_step_mode()
            elif path == "/b2/step-next":
                self._handle_b2_step_next()
            elif path == "/b2/pause-aafl":
                self._handle_b2_pause_aafl()
            elif path == "/b2/resume-aafl":
                self._handle_b2_resume_aafl()
            elif path == "/b2/chain-save":
                self._handle_b2_chain_save()
            elif path == "/b2/chain-run":
                self._handle_b2_chain_run()
            elif path == "/b2/keybind-profiles":
                self._handle_b2_kbp_post()
            elif path == "/b2/keybind-profiles/rate":
                self._handle_b2_kbp_rate()
            elif path == "/b2/keybind-profiles/delete":
                self._handle_b2_kbp_delete()
            elif path == "/b2/strategy-overrides":
                self._handle_b2_strategy_overrides()
            elif path == "/b2/workers":
                self._handle_b2_workers()
            elif path == "/b2/block-source":
                self._handle_b2_block_source()
            elif path == "/b2/unblock-source":
                self._handle_b2_unblock_source()
            elif path == "/b2/export-briefing":
                self._handle_b2_export_briefing()
            elif path == "/b2/scout-compare":
                self._handle_b2_scout_compare()
            # ── Task 3: Scout Results + Task Inbox ─────────────────────────────
            elif path == "/api/task-inbox":
                self._handle_api_task_inbox_post()
            elif path == "/api/run-queue":
                self._handle_api_run_queue()
            elif path == "/api/run-medical":
                self._handle_api_run_medical()
            # ── Build 3 POST endpoints ─────────────────────────────────────────
            elif path == "/b3/urgency":
                self._handle_b3_urgency_post()
            elif path == "/b3/design-presets":
                self._handle_b3_design_presets_post()
            elif path == "/b3/delegate":
                self._handle_b3_delegate()
            elif path == "/quick-ask":
                self._handle_quick_ask()
            elif path == "/scout/search":
                self._handle_scout_search()
            elif path == "/b2/save-loop-preset":
                self._handle_b2_save_loop_preset()
            elif path == "/api/chat-to-sesum":
                self._handle_api_chat_to_sesum()
            elif path == "/api/missions":
                self._handle_api_missions_post()
            # ── Work Checker POST endpoints ────────────────────────────────────
            elif path == "/api/work-checker/refresh":
                self._handle_wc_refresh()
            # ── OCB-A / OCB-B: Self-Health POST endpoints ─────────────────────
            elif path == "/api/self-health/run":
                self._handle_sh_run_all()
            elif path == "/api/self-health/run-tab":
                self._handle_sh_run_tab()
            elif path == "/api/self-health/config":
                self._handle_sh_config_post()
            # ── OCB-B: Auto-Fix POST endpoints ────────────────────────────────
            elif path == "/api/auto-fix/approve":
                self._handle_af_approve()
            elif path == "/api/auto-fix/reject":
                self._handle_af_reject()
            # ── OCB-C: Storage reallocation ───────────────────────────────────
            elif path == "/api/storage/reallocate":
                self._handle_storage_reallocate()
            # ── OCB-C: System monitor ─────────────────────────────────────────
            elif path == "/api/launch-spindoctor":
                self._handle_launch_spindoctor()
            elif path == "/api/system/kill":
                self._handle_system_kill()
            # ── OCB-D: LLOW ─────────────────────────────────────────────────────
            elif path == "/api/llow/workflow":
                self._handle_llow_save_workflow()
            elif path == "/api/llow/validate":
                self._handle_llow_validate()
            elif path == "/api/llow/export-clacr":
                self._handle_llow_export_clacr()
            elif path == "/api/llow/run":
                self._handle_llow_run()
            elif path == "/api/llow/dry-run":
                self._handle_llow_dry_run()
            # ── OCB-N: Scout Swarm launch + Work Checker ─────────────────────
            elif path == "/api/llow/scout-swarm":
                self._handle_scout_swarm_post()
            elif path == "/api/work-checker/check-item":
                self._handle_wc_check_item()
            elif path == "/api/work-checker/delegate":
                self._handle_wc_delegate()
            elif path == "/api/clachr/dispatch":
                self._handle_clachr_dispatch()
            # ── OCB-K: Project awareness update ─────────────────────────────
            elif path == "/api/project-awareness/update":
                self._handle_project_awareness_update()
            # ── OCB-L: Phase 5 — Help tab ask (SSE) ─────────────────────────
            elif path == "/api/help/ask":
                self._handle_help_ask()
            # ── OCB-L: Phase 6 — Settings persistence ────────────────────────
            elif path == "/api/settings":
                self._handle_settings_post()
            # ── OCB-O: Code Editor ────────────────────────────────────────────
            elif path == "/api/code/save":
                self._handle_code_save()
            elif path == "/api/code/run":
                self._handle_code_run()
            # ── OCB-O: OCB Runner ─────────────────────────────────────────────
            elif path == "/api/ocb/parse":
                self._handle_ocb_parse()
            elif path == "/api/ocb/run":
                self._handle_ocb_run()
            elif path.startswith("/api/ocb/cancel/"):
                run_id = path[len("/api/ocb/cancel/"):]
                self._handle_ocb_cancel(run_id)
            elif path.startswith("/api/ocb/archive/"):
                run_id = path[len("/api/ocb/archive/"):]
                self._handle_ocb_archive(run_id)
            elif path == "/api/rrclach/save":
                self._handle_rrclach_save()
            # ── OCB-P: Unified session state POST ─────────────────────────────
            elif path == "/api/session-state":
                self._handle_session_state_post()
            # ── OCB-P: Provider diagnosis ─────────────────────────────────────
            elif path == "/api/provider-health/diagnose":
                self._handle_provider_health_diagnose()
            # ── OCB-P: Command bar ────────────────────────────────────────────
            elif path == "/api/command-bar":
                self._handle_command_bar()
            # ── OCB-P: Watchdog start ─────────────────────────────────────────
            elif path == "/api/watchdog/start":
                self._handle_watchdog_start()
            else:
                self._send_json({"error": "Not found"}, 404)
        except Exception as exc:
            try:
                self._send_json({"error": f"Server error: {exc}"}, 500)
            except Exception:
                pass

    def do_PUT(self):
        path = self.path.split("?")[0]
        try:
            if path.startswith("/api/missions/"):
                mission_id = path[len("/api/missions/"):]
                self._handle_api_missions_put(mission_id)
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
        elif path.startswith("/api/missions/"):
            mission_id = path[len("/api/missions/"):]
            self._handle_api_missions_delete(mission_id)
        elif path.startswith("/api/llow/workflow/"):
            name = urllib.parse.unquote(path[len("/api/llow/workflow/"):])
            self._handle_llow_delete_workflow(name)
        elif path == "/api/clachr/clear":
            self._handle_clachr_clear()
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

        # Bug fix: do NOT persist merged config on every run — that overwrites
        # chief_scout_config.json from the Scout results panel on each poll/run.
        # Config persistence is handled exclusively by POST /scout-config.
        SCOUT_OUTPUT.mkdir(exist_ok=True)

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
            if ok and STATUS_FILE.exists():
                try:
                    cnt = len(STATUS_FILE.read_text(encoding="utf-8", errors="replace").splitlines())
                    self._update_statuscheck_baseline(cnt)
                except Exception:
                    pass
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
        old_lines = len(STATUS_FILE.read_text(encoding="utf-8", errors="replace").splitlines()) if STATUS_FILE.exists() else 0
        if STATUS_FILE.exists():
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(STATUS_FILE, ARCHIVE_DIR / f"STATUS_{stamp}.md")
        text = override if override is not None else src.read_text(encoding="utf-8", errors="replace")
        STATUS_FILE.write_text(text, encoding="utf-8")
        new_lines = len(STATUS_FILE.read_text(encoding="utf-8", errors="replace").splitlines())
        if old_lines > 0 and new_lines < old_lines * STATUS_SANITY_THRESHOLD:
            bak = ARCHIVE_DIR / f"STATUS_{stamp}.md"
            if bak.exists():
                shutil.copy2(bak, STATUS_FILE)
            err = f"POST /api/restore sanity check failed: {new_lines} lines < 90% of {old_lines}"
            _log_status_error(err)
            self._send_json({"ok": False, "error": "STATUS.md sanity check failed — write aborted"}, 500)
            return
        self._send_json({"ok": True, "restored_from": fname,
                         "line_count": new_lines})

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
        old_lines = len(STATUS_FILE.read_text(encoding="utf-8", errors="replace").splitlines()) if STATUS_FILE.exists() else 0
        if STATUS_FILE.exists():
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(STATUS_FILE, ARCHIVE_DIR / f"STATUS_{stamp}.md")
        text = content if content is not None else src.read_text(encoding="utf-8", errors="replace")
        STATUS_FILE.write_text(text, encoding="utf-8")
        new_lines = len(STATUS_FILE.read_text(encoding="utf-8", errors="replace").splitlines())
        if old_lines > 0 and new_lines < old_lines * STATUS_SANITY_THRESHOLD:
            bak = ARCHIVE_DIR / f"STATUS_{stamp}.md"
            if bak.exists():
                shutil.copy2(bak, STATUS_FILE)
            err = f"POST /wccs/restore sanity check failed: {new_lines} lines < 90% of {old_lines}"
            _log_status_error(err)
            self._send_json({"ok": False, "error": "STATUS.md sanity check failed — write aborted"}, 500)
            return
        self._send_json({"ok": True, "restored_from": fname, "line_count": new_lines})

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

    # ── MCP: GET /api/acca ───────────────────────────────────────────────────────

    def _handle_api_acca_md(self):
        content = ""
        if ACCA_FILE.exists():
            try:
                content = ACCA_FILE.read_text(encoding="utf-8", errors="replace")
            except Exception as exc:
                self._send_json({"error": str(exc)}, 500)
                return
        self._send_json({"content": content, "file": str(ACCA_FILE), "exists": ACCA_FILE.exists()})

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


    # ── POST /aafl/run-goal ───────────────────────────────────────────────────

    def _handle_aafl_run_goal(self):
        global _aafl_running
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
        if not _aafl_lock.acquire(blocking=False):
            self._send_json({"ok": False, "status": "already_running", "goal": goal})
            return
        _aafl_running = True
        AAFL_OUTPUT.mkdir(exist_ok=True)
        t = threading.Thread(target=_run_aafl_bg, args=(cfg,), daemon=True)
        t.start()
        self._send_json({"ok": True, "status": "running", "goal": goal})

    # ── GET /aafl/live ────────────────────────────────────────────────────────

    def _handle_aafl_last_result(self):
        """GET /aafl/last-result — scan aafl_output/ for most recent file, return structured JSON."""
        import re as _re
        result: dict = {
            "running":   _aafl_running,
            "status":    "running" if _aafl_running else "idle",
            "goal":      "",
            "provider":  "—",
            "result":    "",
            "score":     None,
            "timestamp": "",
        }
        # Find the most recently modified file in aafl_output/
        best_path = None
        if AAFL_OUTPUT.exists():
            candidates = [f for f in AAFL_OUTPUT.iterdir()
                          if f.is_file() and f.suffix in (".txt", ".json", ".md")]
            if candidates:
                best_path = max(candidates, key=lambda f: f.stat().st_mtime)
        if not best_path:
            self._send_json(result)
            return
        try:
            text  = best_path.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            content_parts: list = []
            for ln in lines:
                if ln.startswith("[RUNNING] Goal:"):
                    result["goal"] = ln[len("[RUNNING] Goal:"):].strip()
                elif ln.startswith("[RUNNING] Strategy:"):
                    # e.g. "[RUNNING] Strategy: ddg | Goal: ..."
                    if "Goal:" in ln:
                        result["goal"] = ln.split("Goal:")[-1].strip()
                elif ln.startswith("[STARTED]"):
                    result["timestamp"] = ln[len("[STARTED]"):].strip()
                elif ln.startswith("[FINISHED]"):
                    result["timestamp"] = ln[len("[FINISHED]"):].strip()
                    result["status"]    = "complete"
                elif ln.startswith("[DONE]"):
                    result["status"] = "complete"
                elif ln.startswith("[ERROR]"):
                    result["status"] = "error"
                    content_parts.append(ln)
                elif "[AAFL] ->" in ln:
                    result["provider"] = ln.split("[AAFL] ->")[-1].strip().split()[0]
                else:
                    content_parts.append(ln)
                m = _re.search(r'[Ss]core[:\s=]+([0-9]+(?:\.[0-9]+)?)', ln)
                if m:
                    try:
                        result["score"] = float(m.group(1))
                    except ValueError:
                        pass
            result["result"] = "\n".join(content_parts).strip()
            if _aafl_running:
                result["status"] = "running"
        except Exception as exc:
            result["error"] = str(exc)
        self._send_json(result)

    def _handle_aafl_live(self):
        lines = []
        if AAFL_LATEST.exists():
            try:
                raw = AAFL_LATEST.read_text(encoding="utf-8", errors="replace")
                lines = raw.splitlines()[-100:]
            except Exception:
                pass
        phase = "idle"
        provider = ""
        for ln in lines:
            if "[LOOP] Planning" in ln or "Phase: plan" in ln:
                phase = "plan"
            elif "[LOOP] Working" in ln or "Phase: work" in ln:
                phase = "work"
            elif "[LOOP] Score" in ln or "Phase: verify" in ln or "[EVAL]" in ln:
                phase = "verify"
            elif "[DB] Stored" in ln or "Phase: store" in ln:
                phase = "store"
            elif "[DONE]" in ln or "[FINISHED]" in ln:
                phase = "done"
            if "[AAFL] ->" in ln:
                provider = ln.split("[AAFL] ->")[-1].strip().split()[0]
        self._send_json({
            "lines": lines,
            "phase": phase,
            "provider": provider,
            "running": _aafl_running,
        })

    # ── POST /scout/strategy ──────────────────────────────────────────────────

    def _handle_scout_strategy(self):
        global _scout_running, _scout_proc, _scout_start_time
        body = self._read_body().strip()
        try:
            data = json.loads(body) if body else {}
            goal = data.get("goal", "").strip()
            strategy = data.get("strategy", "ddg").strip()
        except Exception:
            self._send_json({"ok": False, "error": "Bad request"}, 400)
            return
        if not goal:
            self._send_json({"ok": False, "error": "Empty goal"}, 400)
            return
        # Auto-clear stale lock if scout has been running for more than 120s
        if _scout_start_time and (datetime.datetime.now() - _scout_start_time).total_seconds() > 120:
            if _scout_proc:
                try:
                    _scout_proc.kill()
                except Exception:
                    pass
            _scout_proc = None
            _scout_start_time = None
            _scout_running = False
            try:
                _scout_lock.release()
            except RuntimeError:
                pass
        if not _scout_lock.acquire(blocking=False):
            self._send_json({"ok": False, "status": "already_running",
                             "message": "A search is still running — click Force Stop to cancel it"})
            return
        _scout_running = True
        _scout_start_time = datetime.datetime.now()
        SCOUT_OUTPUT.mkdir(exist_ok=True)

        def _bg():
            global _scout_running, _scout_proc, _scout_start_time
            try:
                with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
                    f.write(f"[RUNNING] Strategy: {strategy} | Goal: {goal}\n[STARTED] {_now_iso()}\n")
                if strategy == "all":
                    cmd = [PYTHON, str(HERE / "chief_scout.py"), goal]
                else:
                    cmd = [PYTHON, str(HERE / "chief_scout.py"), goal, "--strategy", strategy]
                _scout_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(HERE))
                stdout, stderr = _scout_proc.communicate(timeout=120)
                output = (stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")).strip()
                with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
                    f.write(output if output else "[DONE] No output received")
            except subprocess.TimeoutExpired:
                if _scout_proc:
                    _scout_proc.kill()
                with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
                    f.write("[ERROR] Scout timed out after 120s")
            except Exception as exc:
                with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
                    f.write(f"[ERROR] {exc}")
            finally:
                _scout_proc = None
                _scout_start_time = None
                _scout_running = False
                try:
                    _scout_lock.release()
                except RuntimeError:
                    pass

        t = threading.Thread(target=_bg, daemon=True)
        t.start()
        self._send_json({"ok": True, "status": "running", "strategy": strategy, "goal": goal})

    # ── POST /scout/force-stop ────────────────────────────────────────────────

    def _handle_scout_force_stop(self):
        global _scout_running, _scout_proc, _scout_start_time
        killed = False
        if _scout_proc:
            try:
                _scout_proc.kill()
                killed = True
            except Exception:
                pass
        _scout_proc = None
        _scout_start_time = None
        _scout_running = False
        try:
            _scout_lock.release()
        except RuntimeError:
            pass
        try:
            with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
                f.write(f"[STOPPED] Force-stopped by user at {_now_iso()}")
        except Exception:
            pass
        self._send_json({"ok": True, "killed": killed})

    # ── POST /aafl/scout-bridge ───────────────────────────────────────────────

    def _handle_aafl_scout_bridge(self):
        body = self._read_body().strip()
        try:
            data = json.loads(body) if body else {}
            goal = data.get("goal", "").strip()
        except Exception:
            goal = ""
        if not goal and GOAL_TXT.exists():
            goal = GOAL_TXT.read_text(encoding="utf-8", errors="replace").strip()
        if not goal:
            self._send_json({"ok": False, "error": "No goal"}, 400)
            return
        bridge_out = AAFL_OUTPUT / "bridge_result.json"
        AAFL_OUTPUT.mkdir(exist_ok=True)

        def _bg():
            try:
                cmd = [PYTHON, str(HERE / "chief_scout.py"), goal]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(HERE))
                result = {"goal": goal, "output": (res.stdout + res.stderr).strip(),
                          "timestamp": _now_iso(), "ok": res.returncode == 0}
                with open(bridge_out, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            except Exception as exc:
                try:
                    with open(bridge_out, "w", encoding="utf-8") as f:
                        json.dump({"goal": goal, "error": str(exc), "timestamp": _now_iso(), "ok": False}, f)
                except Exception:
                    pass

        t = threading.Thread(target=_bg, daemon=True)
        t.start()
        self._send_json({"ok": True, "status": "running", "goal": goal})

    # ── GET /aafl/bridge-result ───────────────────────────────────────────────

    def _handle_aafl_bridge_result(self):
        bridge_out = AAFL_OUTPUT / "bridge_result.json"
        if bridge_out.exists():
            try:
                with open(bridge_out, encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json(data)
                return
            except Exception:
                pass
        self._send_json({"ok": False, "error": "No bridge result yet"})

    # ── GET /aafl/workflow-presets ────────────────────────────────────────────

    def _handle_workflow_presets_get(self):
        if WORKFLOW_PRESETS.exists():
            try:
                with open(WORKFLOW_PRESETS, encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json({"presets": data if isinstance(data, list) else []})
                return
            except Exception:
                pass
        self._send_json({"presets": []})

    # ── POST /aafl/workflow ───────────────────────────────────────────────────

    def _handle_workflow_save(self):
        body = self._read_body().strip()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        name = data.get("name", "").strip()
        steps = data.get("steps", [])
        if not name:
            self._send_json({"ok": False, "error": "No name"}, 400)
            return
        presets = []
        if WORKFLOW_PRESETS.exists():
            try:
                with open(WORKFLOW_PRESETS, encoding="utf-8") as f:
                    presets = json.load(f)
                if not isinstance(presets, list):
                    presets = []
            except Exception:
                presets = []
        presets = [p for p in presets if p.get("name") != name]
        presets.append({"name": name, "steps": steps})
        try:
            with open(WORKFLOW_PRESETS, "w", encoding="utf-8") as f:
                json.dump(presets, f, indent=2, ensure_ascii=False)
            self._send_json({"ok": True, "name": name, "count": len(presets)})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)


    # ═══════════════════════════════════════════════════════════════════════════
    # B2 HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════

    def _b2_load_json(self, path, default):
        try:
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return default

    def _b2_save_json(self, path, data):
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(path)

    # ── B2-01/02: Kanban ──────────────────────────────────────────────────────

    def _handle_b2_kanban_get(self):
        board = self._b2_load_json(KANBAN_JSON, {"todo": [], "doing": [], "done": []})
        self._send_json(board)

    def _handle_b2_kanban_post(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        action = data.get("action", "")
        board  = self._b2_load_json(KANBAN_JSON, {"todo": [], "doing": [], "done": []})
        if action == "add":
            col  = data.get("col", "todo")
            card = {
                "id":      data.get("id", _now_iso()),
                "title":   data.get("title", "New Card"),
                "tags":    data.get("tags", []),
                "deps":    data.get("deps", []),
                "created": _now_iso(),
            }
            board.setdefault(col, []).append(card)
        elif action == "move":
            card_id = data.get("id")
            to_col  = data.get("col", "todo")
            for col in ("todo", "doing", "done"):
                for c in board.get(col, []):
                    if c.get("id") == card_id:
                        board[col].remove(c)
                        board.setdefault(to_col, []).append(c)
                        break
        elif action == "delete":
            card_id = data.get("id")
            for col in ("todo", "doing", "done"):
                board[col] = [c for c in board.get(col, []) if c.get("id") != card_id]
        elif action == "save":
            for k in ("todo", "doing", "done"):
                if k in data:
                    board[k] = data[k]
        self._b2_save_json(KANBAN_JSON, board)
        self._send_json({"ok": True, "board": board})

    # ── B2-03: Activity ───────────────────────────────────────────────────────

    def _handle_b2_activity_get(self):
        log = self._b2_load_json(ACTIVITY_LOG, [])
        qs  = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        cat = qs.get("cat", [None])[0]
        if cat and cat != "all":
            log = [e for e in log if e.get("cat") == cat]
        self._send_json({"entries": log[-200:]})

    def _handle_b2_activity_post(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        entry = {
            "ts":      _now_iso(),
            "cat":     data.get("cat", "general"),
            "msg":     data.get("msg", ""),
            "trigger": data.get("trigger", "manual"),
        }
        log = self._b2_load_json(ACTIVITY_LOG, [])
        log.append(entry)
        if len(log) > 1000:
            log = log[-1000:]
        self._b2_save_json(ACTIVITY_LOG, log)
        self._send_json({"ok": True})

    def _handle_b2_activity_summarise(self):
        log = self._b2_load_json(ACTIVITY_LOG, [])
        if not log:
            self._send_json({"summary": "No activity to summarise."})
            return
        recent = log[-50:]
        text   = "\n".join(
            f"[{e.get('ts','')}] [{e.get('cat','')}] {e.get('msg','')}" for e in recent
        )
        prompt = f"Summarise this MCC activity log in 3-5 bullet points:\n{text}"
        try:
            sys.path.insert(0, str(HERE))
            import importlib
            core    = importlib.import_module("aafl_core")
            summary = core.call_llm(
                prompt=prompt, provider="mistral",
                model="codestral-latest", max_tokens=400,
            )
        except Exception as exc:
            summary = f"AI summarise unavailable: {exc}"
        self._send_json({"summary": summary})

    # ── B2-04/05: AAFL Runs ───────────────────────────────────────────────────

    def _handle_b2_aafl_runs(self):
        import sqlite3
        rows = []
        try:
            if DB_PATH.exists():
                conn = sqlite3.connect(str(DB_PATH))
                cur  = conn.cursor()
                # add optional columns if missing
                for col in ("tags", "notes"):
                    try:
                        conn.execute(f"ALTER TABLE solution_log ADD COLUMN {col} TEXT")
                        conn.commit()
                    except Exception:
                        pass
                cur.execute(
                    "SELECT id, goal, provider, score, timestamp, result, tags, notes "
                    "FROM solution_log ORDER BY timestamp DESC LIMIT 100"
                )
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    rows.append(dict(zip(cols, row)))
                conn.close()
        except Exception as exc:
            rows = [{"error": str(exc)}]
        self._send_json({"runs": rows})

    def _handle_b2_run_tag(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        import sqlite3
        try:
            conn = sqlite3.connect(str(DB_PATH))
            try:
                conn.execute("ALTER TABLE solution_log ADD COLUMN tags TEXT")
                conn.commit()
            except Exception:
                pass
            conn.execute("UPDATE solution_log SET tags=? WHERE id=?", (data.get("tags", ""), data.get("id")))
            conn.commit()
            conn.close()
            self._send_json({"ok": True})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    def _handle_b2_run_notes(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        import sqlite3
        try:
            conn = sqlite3.connect(str(DB_PATH))
            try:
                conn.execute("ALTER TABLE solution_log ADD COLUMN notes TEXT")
                conn.commit()
            except Exception:
                pass
            conn.execute("UPDATE solution_log SET notes=? WHERE id=?", (data.get("notes", ""), data.get("id")))
            conn.commit()
            conn.close()
            self._send_json({"ok": True})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── B2 Prefs ──────────────────────────────────────────────────────────────

    def _handle_b2_prefs_get(self):
        prefs = self._b2_load_json(MCC_PREFS, {"theme": "dark", "tutorial": False, "first_run": True})
        self._send_json(prefs)

    def _handle_b2_prefs_post(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        prefs = self._b2_load_json(MCC_PREFS, {"theme": "dark", "tutorial": False, "first_run": True})
        prefs.update(data)
        self._b2_save_json(MCC_PREFS, prefs)
        self._send_json({"ok": True})

    # ── B2-10/11: Budget Caps + Costs ─────────────────────────────────────────

    def _handle_b2_budget_caps_get(self):
        caps = self._b2_load_json(BUDGET_CAPS, {"daily": 0.50, "weekly": 2.00, "monthly": 8.00, "roi_value": 10.00})
        self._send_json(caps)

    def _handle_b2_budget_caps_post(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        caps = self._b2_load_json(BUDGET_CAPS, {})
        caps.update(data)
        self._b2_save_json(BUDGET_CAPS, caps)
        self._send_json({"ok": True})

    def _handle_b2_costs_get(self):
        import re
        daily: dict   = {}
        by_prov: dict = {}
        total         = 0.0
        pattern       = re.compile(
            r"\[(\d{4}-\d{2}-\d{2})[^\]]*\] CALL #\d+\s+cost=£([\d.]+)\s+running=£[\d.]+(?:\s+iter=\S+)?(?:\s+provider=(\S+))?"
        )
        try:
            if COST_LOG.exists():
                with open(COST_LOG, encoding="utf-8") as f:
                    for line in f:
                        m = pattern.search(line)
                        if m:
                            day          = m.group(1)
                            cost         = float(m.group(2))
                            prov         = m.group(3) or "unknown"
                            daily[day]   = daily.get(day, 0.0) + cost
                            by_prov[prov] = by_prov.get(prov, 0.0) + cost
                            total        += cost
        except Exception as exc:
            self._send_json({"error": str(exc), "daily": {}, "by_provider": {}, "total": 0.0})
            return
        self._send_json({"daily": daily, "by_provider": by_prov, "total": round(total, 6)})

    # ── B2-08: Benchmark ──────────────────────────────────────────────────────

    def _handle_b2_benchmark(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        goal      = data.get("goal", "benchmark test").strip()
        providers = data.get("providers", ["mistral", "cerebras", "openrouter"])
        runs      = int(data.get("runs", 3))
        py        = str(FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable))

        def _bg():
            results = []
            for prov in providers:
                for i in range(runs):
                    try:
                        env = dict(os.environ)
                        env["AAFL_GOAL"] = goal
                        res = subprocess.run(
                            [py, str(HERE / "loop_manager.py"), "--once", f"--provider={prov}"],
                            capture_output=True, text=True, timeout=180, cwd=str(HERE), env=env,
                        )
                        results.append({"provider": prov, "run": i + 1, "ok": res.returncode == 0,
                                        "output": (res.stdout + res.stderr)[-500:]})
                    except Exception as exc:
                        results.append({"provider": prov, "run": i + 1, "ok": False, "output": str(exc)})
            self._b2_save_json(BENCHMARK_RESULTS, {"goal": goal, "ts": _now_iso(), "results": results})

        threading.Thread(target=_bg, daemon=True).start()
        self._send_json({"ok": True, "status": "running", "goal": goal})

    # ── B2-09: Second Opinion ─────────────────────────────────────────────────

    def _handle_b2_second_opinion(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        goal     = data.get("goal", "").strip()
        provider = data.get("provider", "mistral").strip()
        if not goal:
            try:
                if GOAL_TXT.exists():
                    goal = GOAL_TXT.read_text(encoding="utf-8").strip()
            except Exception:
                pass
        if not goal:
            self._send_json({"ok": False, "error": "No goal"}, 400)
            return
        py = str(FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable))

        def _bg():
            env = dict(os.environ)
            env["AAFL_GOAL"] = goal
            try:
                res = subprocess.run(
                    [py, str(HERE / "loop_manager.py"), "--once", f"--provider={provider}"],
                    capture_output=True, text=True, timeout=180, cwd=str(HERE), env=env,
                )
                out = (res.stdout + res.stderr).strip()
            except Exception as exc:
                out = f"[ERROR] {exc}"
            AAFL_OUTPUT.mkdir(exist_ok=True)
            (AAFL_OUTPUT / "second_opinion.txt").write_text(
                f"[SECOND OPINION] Provider: {provider}\nGoal: {goal}\n\n{out}", encoding="utf-8"
            )

        threading.Thread(target=_bg, daemon=True).start()
        self._send_json({"ok": True, "status": "running", "provider": provider})

    # ── B2-06: Step / Pause ───────────────────────────────────────────────────

    def _handle_b2_step_mode(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}
        state = self._b2_load_json(B2_STEP_FILE, {"step_mode": False, "current_phase": "plan"})
        state["step_mode"] = bool(data.get("enabled", False))
        self._b2_save_json(B2_STEP_FILE, state)
        self._send_json({"ok": True, "step_mode": state["step_mode"]})

    def _handle_b2_step_next(self):
        phases = ["plan", "work", "verify", "store"]
        state  = self._b2_load_json(B2_STEP_FILE, {"step_mode": True, "current_phase": "plan"})
        cur    = state.get("current_phase", "plan")
        idx    = phases.index(cur) if cur in phases else -1
        nxt    = phases[min(idx + 1, len(phases) - 1)]
        state["current_phase"] = nxt
        self._b2_save_json(B2_STEP_FILE, state)
        self._send_json({"ok": True, "phase": nxt})

    def _handle_b2_pause_aafl(self):
        (HERE / "aafl_pause.flag").write_text("paused", encoding="utf-8")
        self._send_json({"ok": True, "status": "paused"})

    def _handle_b2_resume_aafl(self):
        flag = HERE / "aafl_pause.flag"
        try:
            if flag.exists():
                flag.unlink()
        except Exception:
            pass
        self._send_json({"ok": True, "status": "resumed"})

    # ── B2-07: Chain Builder ──────────────────────────────────────────────────

    def _handle_b2_chain_save(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        self._b2_save_json(B2_CHAIN_FILE, data)
        self._send_json({"ok": True})

    def _handle_b2_chain_run(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        # Support both {goals:[str,...]} (from chain builder) and {chain:[{goal,provider},...]}
        raw_goals = data.get("goals", [])
        chain     = data.get("chain", [])
        if raw_goals and not chain:
            chain = [{"goal": g, "provider": ""} for g in raw_goals if isinstance(g, str) and g.strip()]
        loop_count    = int(data.get("loop_count", 1))
        loop_infinite = bool(data.get("loop_infinite", False))
        end_condition = data.get("end_condition", "after_n")
        loop_actions  = data.get("loop_actions", [])
        if loop_infinite:
            loop_count = 0  # 0 means unlimited
        if not chain:
            chain_data = self._b2_load_json(B2_CHAIN_FILE, {"chain": []})
            chain      = chain_data.get("chain", [])
        if not chain:
            self._send_json({"ok": False, "error": "Empty chain"}, 400)
            return
        py = str(FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable))

        def _bg():
            iteration = 0
            while True:
                results = []
                for item in chain:
                    goal     = item.get("goal", "").strip()
                    provider = item.get("provider", "")
                    if not goal:
                        continue
                    try:
                        env = dict(os.environ)
                        env["AAFL_GOAL"] = goal
                        env["AAFL_LOOP_ACTIONS"] = ",".join(loop_actions)
                        cmd = [py, str(HERE / "loop_manager.py"), "--once"]
                        if provider:
                            cmd.append(f"--provider={provider}")
                        res = subprocess.run(cmd, capture_output=True, text=True,
                                             timeout=300, cwd=str(HERE), env=env)
                        results.append({"goal": goal, "provider": provider,
                                        "ok": res.returncode == 0,
                                        "output": (res.stdout + res.stderr)[-300:]})
                    except Exception as exc:
                        results.append({"goal": goal, "provider": provider,
                                        "ok": False, "output": str(exc)})
                iteration += 1
                self._b2_save_json(HERE / "b2_chain_results.json",
                                   {"ts": _now_iso(), "results": results,
                                    "iteration": iteration, "loop_actions": loop_actions})
                # Check WCCS action
                if "WCCS" in loop_actions:
                    try:
                        wccs_script = HERE / "aafl_wccs.py"
                        if wccs_script.exists():
                            subprocess.run([py, str(wccs_script)],
                                           capture_output=True, text=True,
                                           timeout=120, cwd=str(HERE))
                    except Exception:
                        pass
                # Check loop end condition (loop_count==0 means infinite)
                if end_condition == "after_n" and loop_count > 0 and iteration >= loop_count:
                    break
                if end_condition == "manual_stop":
                    stop_flag = HERE / "chain_stop.flag"
                    if stop_flag.exists():
                        try:
                            stop_flag.unlink()
                        except Exception:
                            pass
                        break

        threading.Thread(target=_bg, daemon=True).start()
        self._send_json({"ok": True, "status": "running", "count": len(chain),
                         "loop_count": loop_count, "end_condition": end_condition,
                         "loop_actions": loop_actions})

    # ── B2-22: Keybinding Profiles ────────────────────────────────────────────

    def _handle_b2_kbp_get(self):
        KEYBIND_PROFILES.mkdir(exist_ok=True)
        profiles = []
        for fp in sorted(KEYBIND_PROFILES.glob("*.json")):
            try:
                with open(fp, encoding="utf-8") as f:
                    p = json.load(f)
                p.setdefault("filename", fp.name)
                profiles.append(p)
            except Exception:
                pass
        self._send_json({"profiles": profiles})

    def _handle_b2_kbp_post(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        name = data.get("name", "").strip()
        if not name:
            self._send_json({"ok": False, "error": "No name"}, 400)
            return
        KEYBIND_PROFILES.mkdir(exist_ok=True)
        safe = "".join(c for c in name if c.isalnum() or c in " -_").strip().replace(" ", "_")
        fp   = KEYBIND_PROFILES / f"{safe}.json"
        data.setdefault("created", _now_iso())
        data.setdefault("stars", 0)
        self._b2_save_json(fp, data)
        self._send_json({"ok": True, "filename": fp.name})

    def _handle_b2_kbp_rate(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        fp = KEYBIND_PROFILES / data.get("filename", "")
        if not fp.exists():
            self._send_json({"ok": False, "error": "Not found"}, 404)
            return
        try:
            with open(fp, encoding="utf-8") as f:
                p = json.load(f)
            p["stars"] = max(0, min(5, int(data.get("stars", 0))))
            self._b2_save_json(fp, p)
            self._send_json({"ok": True})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    def _handle_b2_kbp_delete(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        fp = KEYBIND_PROFILES / data.get("filename", "")
        if not fp.exists():
            self._send_json({"ok": False, "error": "Not found"}, 404)
            return
        try:
            fp.unlink()
            self._send_json({"ok": True})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── B2-14/15: Strategy Overrides + Workers ────────────────────────────────

    def _handle_b2_strategy_overrides(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        cfg = self._b2_load_json(SCOUT_CFG_EXTRA, {})
        cfg["strategy_overrides"] = data.get("overrides", {})
        self._b2_save_json(SCOUT_CFG_EXTRA, cfg)
        self._send_json({"ok": True})

    def _handle_b2_workers(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        cfg = self._b2_load_json(SCOUT_CFG_EXTRA, {})
        cfg["parallel_workers"] = max(1, min(10, int(data.get("workers", 3))))
        self._b2_save_json(SCOUT_CFG_EXTRA, cfg)
        self._send_json({"ok": True, "workers": cfg["parallel_workers"]})

    # ── B2-16: Source Health + Block/Unblock ──────────────────────────────────

    def _handle_b2_source_health(self):
        blocked = self._b2_load_json(B2_BLOCKED, [])
        health  = []
        try:
            lib     = self._b2_load_json(SOURCES_LIBRARY, {})
            sources = lib.get("sources", lib) if isinstance(lib, dict) else []
            if isinstance(sources, dict):
                sources = list(sources.values())
            for s in (sources if isinstance(sources, list) else []):
                name = s.get("name", s.get("url", "?"))
                health.append({
                    "source":       name,
                    "status":       "blocked" if name in blocked else "ok",
                    "queries":      s.get("query_count", 0),
                    "success_rate": s.get("success_rate", 1.0),
                })
        except Exception:
            pass
        self._send_json({"health": health, "blocked": blocked})

    def _handle_b2_block_source(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        source  = data.get("source", "").strip()
        blocked = self._b2_load_json(B2_BLOCKED, [])
        if source and source not in blocked:
            blocked.append(source)
            self._b2_save_json(B2_BLOCKED, blocked)
        self._send_json({"ok": True, "blocked": blocked})

    def _handle_b2_unblock_source(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        source  = data.get("source", "").strip()
        blocked = self._b2_load_json(B2_BLOCKED, [])
        blocked = [b for b in blocked if b != source]
        self._b2_save_json(B2_BLOCKED, blocked)
        self._send_json({"ok": True, "blocked": blocked})

    # ── B2-17: Export Briefing ────────────────────────────────────────────────

    def _handle_b2_export_briefing(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        goal  = data.get("goal", "briefing").strip() or "briefing"
        lines = [f"# Scout Briefing — {goal}", f"Generated: {_now_iso()}", ""]
        try:
            if SCOUT_LATEST.exists():
                lines += ["## Scout Result", SCOUT_LATEST.read_text(encoding="utf-8")]
        except Exception:
            pass
        SCOUT_BRIEFINGS.mkdir(exist_ok=True)
        safe = "".join(c for c in goal if c.isalnum() or c in " -_")[:40].strip().replace(" ", "_")
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out  = SCOUT_BRIEFINGS / f"briefing_{ts}_{safe}.md"
        out.write_text("\n".join(lines), encoding="utf-8")
        self._send_json({"ok": True, "file": str(out), "name": out.name})

    # ── B2-13: Scout Compare ──────────────────────────────────────────────────

    def _handle_b2_scout_compare(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        goal      = data.get("goal", "").strip()
        providers = data.get("providers", ["mistral", "gemini"])
        py        = str(FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable))

        def _bg():
            results = {}
            for prov in providers:
                env = dict(os.environ)
                if goal:
                    env["AAFL_GOAL"] = goal
                try:
                    res = subprocess.run(
                        [py, str(HERE / "loop_manager.py"), "--once", f"--provider={prov}"],
                        capture_output=True, text=True, timeout=180, cwd=str(HERE), env=env,
                    )
                    results[prov] = {"ok": res.returncode == 0,
                                     "output": (res.stdout + res.stderr)[-800:]}
                except Exception as exc:
                    results[prov] = {"ok": False, "output": str(exc)}
            AAFL_OUTPUT.mkdir(exist_ok=True)
            self._b2_save_json(
                AAFL_OUTPUT / "scout_compare.json",
                {"goal": goal, "ts": _now_iso(), "results": results},
            )

        threading.Thread(target=_bg, daemon=True).start()
        self._send_json({"ok": True, "status": "running", "providers": providers})


    # ── Task 3: GET /scout/results ────────────────────────────────────────────

    def _handle_scout_results_json(self):
        """Returns latest scout output as JSON. Polls every 10s from the MCC front-end."""
        content = ""
        mtime   = None
        if SCOUT_LATEST.exists():
            try:
                content = SCOUT_LATEST.read_text(encoding="utf-8", errors="replace")
                mtime   = SCOUT_LATEST.stat().st_mtime
            except Exception:
                content = "[ERROR] Could not read scout output"
        else:
            content = "No scout results yet — run a scout first."

        # Try to parse as structured JSON if the scout wrote it
        data = None
        try:
            data = json.loads(content)
        except Exception:
            data = None

        self._send_json({
            "content": content,
            "data":    data,
            "running": _scout_running,
            "ts":      mtime,
        })

    # ── Task 3: GET /api/task-inbox ───────────────────────────────────────────

    def _handle_api_task_inbox_get(self):
        """Return current active goals from goal_queue.txt."""
        goals = []
        if GOAL_QUEUE.exists():
            try:
                lines = GOAL_QUEUE.read_text(encoding="utf-8", errors="replace").splitlines()
                goals = [l.strip() for l in lines
                         if l.strip() and not l.strip().startswith("#")]
            except Exception:
                pass
        self._send_json({"goals": goals, "count": len(goals)})

    # ── Task 3: POST /api/task-inbox ──────────────────────────────────────────

    def _handle_api_task_inbox_post(self):
        """Append a goal to goal_queue.txt and return updated queue."""
        body = self._read_body().strip()
        try:
            data = json.loads(body) if body else {}
            goal = data.get("goal", "").strip() if isinstance(data, dict) else body.strip()
        except Exception:
            goal = body.strip()
        if not goal:
            self._send_json({"ok": False, "error": "Empty goal"}, 400)
            return
        try:
            with open(GOAL_QUEUE, "a", encoding="utf-8") as f:
                f.write(goal + "\n")
            goals = []
            if GOAL_QUEUE.exists():
                lines = GOAL_QUEUE.read_text(encoding="utf-8", errors="replace").splitlines()
                goals = [l.strip() for l in lines
                         if l.strip() and not l.strip().startswith("#")]
            self._send_json({"ok": True, "queue": goals, "count": len(goals)})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Task 3: POST /api/run-queue ───────────────────────────────────────────

    def _handle_api_run_queue(self):
        """Launch queue_runner.py in the background."""
        runner = HERE / "queue_runner.py"
        if not runner.exists():
            self._send_json({"ok": False, "error": "queue_runner.py not found"}, 404)
            return
        try:
            subprocess.Popen(
                [PYTHON, str(runner)],
                cwd=str(HERE),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._send_json({"ok": True, "status": "queue_runner started"})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)


    # ── GET /api/processes ────────────────────────────────────────────────────

    def _handle_api_processes(self):
        """Returns JSON list of tracked processes with name, status, pid."""
        procs = []
        # MCC server — always running (we are it)
        procs.append({"name": "mcc_server", "status": "running", "pid": os.getpid()})
        # AAFL loop
        aafl_live = _aafl_proc is not None and _aafl_proc.poll() is None
        procs.append({
            "name":   "aafl_loop",
            "status": "running" if aafl_live else "stopped",
            "pid":    _aafl_proc.pid if aafl_live else None,
        })
        # Scout
        scout_live = _scout_proc is not None and _scout_proc.poll() is None
        procs.append({
            "name":   "scout",
            "status": "running" if scout_live else "stopped",
            "pid":    _scout_proc.pid if scout_live else None,
        })
        # queue_runner — check via tasklist (Windows)
        qr_status = "unknown"
        try:
            res = subprocess.run(
                ["tasklist", "/fo", "csv", "/nh"],
                capture_output=True, text=True, timeout=5,
            )
            qr_status = "running" if "queue_runner" in res.stdout.lower() else "stopped"
        except Exception:
            try:
                import psutil
                qr_status = "running" if any(
                    "queue_runner" in " ".join(p.info.get("cmdline") or [])
                    for p in psutil.process_iter(["cmdline"])
                ) else "stopped"
            except Exception:
                pass
        procs.append({"name": "queue_runner", "status": qr_status, "pid": None})
        self._send_json({"processes": procs, "ts": _now_iso()})


    # ── GET /api/medical-report ───────────────────────────────────────────────

    def _handle_api_medical_report(self):
        MEDICAL_DIR.mkdir(parents=True, exist_ok=True)
        reports = sorted(MEDICAL_DIR.glob("mcc_medical_report_*.md"), reverse=True)
        if not reports:
            self._send_json({"ok": False, "report": None, "score": None,
                             "message": "No medical run yet. Click Run Medical."})
            return
        latest = reports[0]
        try:
            content = latest.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)
            return
        score = None
        try:
            import re as _re
            m = _re.search(r"\*\*Score:\*\* (\d+)/100", content)
            if m:
                score = int(m.group(1))
        except Exception:
            pass
        self._send_json({
            "ok": True,
            "filename": latest.name,
            "content": content,
            "score": score,
            "generated_at": _now_iso(),
        })

    # ── GET /api/medical-history ──────────────────────────────────────────────

    def _handle_api_medical_history(self):
        MEDICAL_DIR.mkdir(parents=True, exist_ok=True)
        if not MEDICAL_HISTORY.exists():
            self._send_json({"ok": True, "history": [],
                             "message": "No history yet — run Medical first."})
            return
        try:
            history = json.loads(MEDICAL_HISTORY.read_text(encoding="utf-8"))
        except Exception:
            history = []
        self._send_json({"ok": True, "history": history})

    # ── POST /api/run-medical ─────────────────────────────────────────────────

    def _handle_api_run_medical(self):
        if not MEDICAL_SCRIPT.exists():
            self._send_json({"ok": False, "error": "mcc_medical.py not found"}, 500)
            return
        py = FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable)
        body = self._read_body()
        try:
            opts = json.loads(body) if body.strip() else {}
        except Exception:
            opts = {}
        cmd = [str(py), str(MEDICAL_SCRIPT)]
        if opts.get("quick"):
            cmd.append("--quick")
        elif opts.get("category"):
            cmd += ["--category", opts["category"]]

        # Stream output via chunked plain-text
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        def _send_chunk(text: str):
            try:
                encoded = text.encode("utf-8", errors="replace")
                chunk_hdr = f"{len(encoded):X}\r\n".encode()
                self.wfile.write(chunk_hdr)
                self.wfile.write(encoded)
                self.wfile.write(b"\r\n")
                self.wfile.flush()
            except Exception:
                pass

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(HERE),
            )
            for line in proc.stdout:
                _send_chunk(line)
            proc.wait()
            _send_chunk(f"\n[EXIT] code={proc.returncode}\n")
        except Exception as exc:
            _send_chunk(f"[ERROR] {exc}\n")
        finally:
            # Chunked terminator
            try:
                self.wfile.write(b"0\r\n\r\n")
                self.wfile.flush()
            except Exception:
                pass


    # ── Build 3: GET /health/system ───────────────────────────────────────────

    def _handle_b3_system_health(self):
        try:
            import psutil
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "psutil", "-q"],
                           capture_output=True)
            try:
                import psutil
            except ImportError:
                self._send_json({"ok": False, "error": "psutil not available"})
                return

        info = {
            "ok": True,
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "cpu_count": psutil.cpu_count(),
            "ram_percent": psutil.virtual_memory().percent,
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 1),
            "disk_percent": psutil.disk_usage(str(HERE)).percent,
            "gpu": [],
        }
        # Optional GPU info via GPUtil or nvidia-smi
        try:
            import GPUtil
            for g in GPUtil.getGPUs():
                info["gpu"].append({
                    "name": g.name,
                    "load_percent": round(g.load * 100, 1),
                    "mem_used_mb": round(g.memoryUsed, 0),
                    "mem_total_mb": round(g.memoryTotal, 0),
                    "temp_c": g.temperature,
                })
        except Exception:
            try:
                res = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                     "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=5
                )
                if res.returncode == 0:
                    for line in res.stdout.strip().splitlines():
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) >= 5:
                            info["gpu"].append({
                                "name": parts[0],
                                "load_percent": float(parts[1]),
                                "mem_used_mb": float(parts[2]),
                                "mem_total_mb": float(parts[3]),
                                "temp_c": float(parts[4]),
                            })
            except Exception:
                pass
        self._send_json(info)

    # ── Build 3: GET/POST /b3/urgency ─────────────────────────────────────────

    def _handle_b3_urgency_get(self):
        prefs = self._b2_load_json(MCC_PREFS, {})
        self._send_json({"urgency": prefs.get("urgency", {})})

    def _handle_b3_urgency_post(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        prefs = self._b2_load_json(MCC_PREFS, {})
        if "urgency" not in prefs:
            prefs["urgency"] = {}
        prefs["urgency"].update(data.get("urgency", {}))
        try:
            with open(MCC_PREFS, "w", encoding="utf-8") as f:
                json.dump(prefs, f, indent=2)
            self._send_json({"ok": True})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Build 3: GET/POST /b3/design-presets ─────────────────────────────────

    DESIGN_PRESETS = HERE / "design_presets.json"

    def _handle_b3_design_presets_get(self):
        try:
            if self.DESIGN_PRESETS.exists():
                data = json.loads(self.DESIGN_PRESETS.read_text(encoding="utf-8"))
                self._send_json(data)
                return
        except Exception:
            pass
        self._send_json({"presets": []})

    def _handle_b3_design_presets_post(self):
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        existing = {"presets": []}
        if self.DESIGN_PRESETS.exists():
            try:
                existing = json.loads(self.DESIGN_PRESETS.read_text(encoding="utf-8"))
            except Exception:
                pass
        if "preset" in data:
            existing.setdefault("presets", [])
            existing["presets"] = [p for p in existing["presets"] if p.get("name") != data["preset"].get("name")]
            existing["presets"].append(data["preset"])
        elif "delete" in data:
            existing["presets"] = [p for p in existing.get("presets", []) if p.get("name") != data["delete"]]
        try:
            self.DESIGN_PRESETS.write_text(json.dumps(existing, indent=2), encoding="utf-8")
            self._send_json({"ok": True, "presets": existing["presets"]})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Build 3: GET /b3/scout-ai-summary ────────────────────────────────────

    def _handle_b3_scout_ai_summary(self):
        """Read latest scout output, pass through Mistral to get plain-English summary."""
        content = ""
        if SCOUT_LATEST.exists():
            try:
                content = SCOUT_LATEST.read_text(encoding="utf-8", errors="replace").strip()
            except Exception:
                pass
        if not content or content.startswith("[RUNNING]") or content.startswith("[ERROR]"):
            self._send_json({"ok": False, "summary": "", "reason": "No complete results available"})
            return

        try:
            sys.path.insert(0, str(HERE))
            from aafl_core import call_llm
            prompt = (
                "You are a research assistant. Below is raw output from a web scout search. "
                "Write ONE plain-English paragraph (3-5 sentences) summarising the most important "
                "findings, key web links found, and what the user should do next. "
                "Do NOT include technical warnings, tracebacks, or log noise. "
                "Focus on actionable insights for the user.\n\n"
                f"RAW SCOUT OUTPUT:\n{content[:4000]}"
            )
            result = call_llm(
                provider="mistral",
                model="mistral/mistral-small-latest",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
            )
            summary = result.get("content", "").strip() if isinstance(result, dict) else str(result).strip()
            self._send_json({"ok": True, "summary": summary})
        except Exception as exc:
            self._send_json({"ok": False, "summary": "", "reason": str(exc)})

    # ── POST /quick-ask ───────────────────────────────────────────────────────

    def _handle_quick_ask(self):
        """Instant AI call — tries Cerebras then Mistral then Gemini, 15s timeout each."""
        import time as _time
        try:
            data = json.loads(self._read_body() or "{}")
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        question = data.get("question", "").strip()
        provider = data.get("provider", "auto").strip()
        if not question:
            self._send_json({"ok": False, "error": "Empty question"}, 400)
            return

        t0 = _time.time()
        try:
            sys.path.insert(0, str(HERE))
            import litellm as _ll
            from aafl_core import PROVIDERS
            pmap = {p["id"]: p for p in PROVIDERS}

            alias = {
                "gemini": "gemini_flash", "gemini_flash": "gemini_flash",
                "mistral": "mistral_code", "mistral_code": "mistral_code",
                "cerebras": "cerebras",
            }
            FALLBACK_ORDER = ["cerebras", "mistral_code", "gemini_flash"]
            if provider != "auto":
                pid = alias.get(provider, provider)
                trial_order = [pid] + [x for x in FALLBACK_ORDER if x != pid]
            else:
                trial_order = list(FALLBACK_ORDER)

            errors = {}
            for pid in trial_order:
                p = pmap.get(pid)
                if not p:
                    errors[pid] = "Unknown provider ID"
                    continue
                api_key = (p.get("api_key") or
                           os.environ.get(p.get("api_key_env") or "", "") or "")
                if p.get("api_key_env") and not api_key:
                    errors[pid] = "No API key configured"
                    continue
                try:
                    kwargs = dict(
                        model=p["model"],
                        messages=[{"role": "user", "content": question}],
                        max_tokens=1024,
                        timeout=15,
                    )
                    if p.get("api_base"):
                        kwargs["api_base"] = p["api_base"]
                    if api_key:
                        kwargs["api_key"] = api_key
                    resp = _ll.completion(**kwargs)
                    text = (resp.choices[0].message.content or "").strip()
                    if text:
                        elapsed = round(_time.time() - t0, 2)
                        self._send_json({
                            "ok": True,
                            "provider_used": pid,
                            "response": text,
                            "time_seconds": elapsed,
                        })
                        return
                    errors[pid] = "Empty response from provider"
                except Exception as exc:
                    errors[pid] = str(exc)[:200]

            elapsed = round(_time.time() - t0, 2)
            detail = "; ".join(f"{k}: {v}" for k, v in errors.items())
            self._send_json({
                "ok": False,
                "error": "All providers failed",
                "detail": detail,
                "time_seconds": elapsed,
            })
        except Exception as exc:
            elapsed = round(_time.time() - t0, 2)
            self._send_json({
                "ok": False,
                "error": f"Quick Ask setup error: {exc}",
                "time_seconds": elapsed,
            })

    # ── POST /scout/search ────────────────────────────────────────────────────

    def _handle_scout_search(self):
        """Launch chief_scout.py with a user query, write results to scout_output/."""
        global _scout_running, _scout_proc, _scout_start_time
        body = self._read_body().strip()
        try:
            data  = json.loads(body) if body else {}
            query = data.get("query", "").strip()
        except Exception:
            self._send_json({"ok": False, "error": "Bad request"}, 400)
            return
        if not query:
            self._send_json({"ok": False, "error": "Empty query"}, 400)
            return
        # Auto-clear stale lock
        if _scout_start_time and (datetime.datetime.now() - _scout_start_time).total_seconds() > 120:
            if _scout_proc:
                try:
                    _scout_proc.kill()
                except Exception:
                    pass
            _scout_proc = None
            _scout_start_time = None
            _scout_running = False
            try:
                _scout_lock.release()
            except RuntimeError:
                pass
        if not _scout_lock.acquire(blocking=False):
            self._send_json({"ok": False, "status": "already_running",
                             "message": "A search is still running — click Force Stop to cancel it"})
            return
        _scout_running = True
        _scout_start_time = datetime.datetime.now()
        SCOUT_OUTPUT.mkdir(exist_ok=True)

        def _bg():
            global _scout_running, _scout_proc, _scout_start_time
            try:
                with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
                    f.write(f"[RUNNING] Query: {query}\n[STARTED] {_now_iso()}\n")
                cmd = [PYTHON, str(HERE / "chief_scout.py"), query]
                _scout_proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(HERE)
                )
                stdout, stderr = _scout_proc.communicate(timeout=120)
                output = (
                    stdout.decode("utf-8", errors="replace") +
                    stderr.decode("utf-8", errors="replace")
                ).strip()
                with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
                    f.write(output if output else "[DONE] No output received")
            except subprocess.TimeoutExpired:
                if _scout_proc:
                    _scout_proc.kill()
                with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
                    f.write("[ERROR] Scout timed out after 120s")
            except Exception as exc:
                with open(SCOUT_LATEST, "w", encoding="utf-8") as f:
                    f.write(f"[ERROR] {exc}")
            finally:
                _scout_proc = None
                _scout_start_time = None
                _scout_running = False
                try:
                    _scout_lock.release()
                except RuntimeError:
                    pass

        threading.Thread(target=_bg, daemon=True).start()
        self._send_json({"ok": True, "status": "running", "query": query})

    # ── Build 3: POST /b3/delegate ────────────────────────────────────────────

    def _handle_b3_delegate(self):
        """Trigger the highest-urgency tab's default action."""
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}
        tab = data.get("tab", "")
        action_map = {
            "scout":    ("/run-scout", {}),
            "aafl":     ("/run-aafl", {}),
            "wccs":     ("/wccs", {}),
            "health":   ("/run-health-check", {}),
            "medical":  ("/api/run-medical", {}),
        }
        if tab not in action_map:
            self._send_json({"ok": False, "error": f"No delegate action for tab '{tab}'"})
            return
        endpoint, payload = action_map[tab]
        try:
            import urllib.request as ulr
            req = ulr.Request(
                f"http://127.0.0.1:{PORT}{endpoint}",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with ulr.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read())
            self._send_json({"ok": True, "tab": tab, "result": result})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)})

    # ── Loop Preset endpoints ─────────────────────────────────────────────────

    def _handle_b2_save_loop_preset(self):
        """POST /b2/save-loop-preset — save a named loop configuration."""
        body = self._read_body()
        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"ok": False, "error": "Bad JSON"}, 400)
            return
        name = (data.get("name") or "").strip()
        if not name:
            self._send_json({"ok": False, "error": "name required"}, 400)
            return
        presets: dict = {}
        if LOOP_PRESETS.exists():
            try:
                with open(LOOP_PRESETS, encoding="utf-8") as f:
                    presets = json.load(f)
            except Exception:
                presets = {}
        presets[name] = data
        with open(LOOP_PRESETS, "w", encoding="utf-8") as f:
            json.dump(presets, f, indent=2)
        self._send_json({"ok": True, "name": name})

    def _handle_b2_loop_presets_get(self):
        """GET /b2/loop-presets — list saved loop preset names."""
        presets: dict = {}
        if LOOP_PRESETS.exists():
            try:
                with open(LOOP_PRESETS, encoding="utf-8") as f:
                    presets = json.load(f)
            except Exception:
                pass
        self._send_json({"presets": list(presets.keys())})

    def _handle_b2_loop_preset_get(self, name: str):
        """GET /b2/loop-preset/<name> — load a specific loop preset."""
        import urllib.parse as _up
        name = _up.unquote(name)
        presets: dict = {}
        if LOOP_PRESETS.exists():
            try:
                with open(LOOP_PRESETS, encoding="utf-8") as f:
                    presets = json.load(f)
            except Exception:
                pass
        if name not in presets:
            self._send_json({"ok": False, "error": "Preset not found"}, 404)
            return
        self._send_json({"ok": True, "preset": presets[name]})


    # ── Task 1: GET /api/statuscheck ─────────────────────────────────────────────

    def _handle_api_statuscheck(self):
        current = 0
        if STATUS_FILE.exists():
            try:
                current = len(STATUS_FILE.read_text(encoding="utf-8", errors="replace").splitlines())
            except Exception:
                pass
        baseline = current
        if STATUS_LINECOUNT_JSON.exists():
            try:
                data = json.loads(STATUS_LINECOUNT_JSON.read_text(encoding="utf-8"))
                baseline = int(data.get("baseline", current))
            except Exception:
                pass
        else:
            (HERE / "data").mkdir(exist_ok=True)
            STATUS_LINECOUNT_JSON.write_text(
                json.dumps({"baseline": current, "updated": _now_iso()}, indent=2),
                encoding="utf-8",
            )
        if baseline == 0:
            health = "ok"
        else:
            ratio = current / baseline
            if ratio >= 0.90:
                health = "ok"
            elif ratio >= 0.85:
                health = "warning"
            else:
                health = "critical"
        self._send_json({"current": current, "baseline": baseline, "health": health})

    def _update_statuscheck_baseline(self, new_count: int):
        """Call after a successful WCCS save — update baseline if count rose."""
        try:
            (HERE / "data").mkdir(exist_ok=True)
            baseline = 0
            if STATUS_LINECOUNT_JSON.exists():
                baseline = int(json.loads(
                    STATUS_LINECOUNT_JSON.read_text(encoding="utf-8")
                ).get("baseline", 0))
            if new_count > baseline:
                STATUS_LINECOUNT_JSON.write_text(
                    json.dumps({"baseline": new_count, "updated": _now_iso()}, indent=2),
                    encoding="utf-8",
                )
        except Exception:
            pass

    # ── Task 2: GET /api/old-saves-report ────────────────────────────────────────

    def _handle_api_old_saves_report(self):
        report_file = HERE / "data" / "old_saves_report.txt"
        if not report_file.exists():
            self._send_json({"ok": False, "error": "No report yet — run scan_old_saves.py first"})
            return
        try:
            content = report_file.read_text(encoding="utf-8", errors="replace")
            self._send_json({"ok": True, "report": content})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Task 3: POST /api/chat-to-sesum ──────────────────────────────────────────

    def _handle_api_chat_to_sesum(self):
        body = self._read_body().strip()
        if not body:
            self._send_json({"ok": False, "error": "No chat text provided"}, 400)
            return
        try:
            import litellm as _ll
            from aafl_core import PROVIDERS
            pmap = {p["id"]: p for p in PROVIDERS}
            p = pmap.get("mistral_code") or next(
                (x for x in PROVIDERS if "mistral" in x.get("model", "").lower()), None
            )
            if not p:
                self._send_json({"ok": False, "error": "Mistral provider not found"}, 500)
                return
            api_key = (p.get("api_key") or
                       os.environ.get(p.get("api_key_env") or "", "") or "")
            system_prompt = (
                "You are a SESUM (Session Summary) generator for a software project called VKB Spin Doctor / AAFL.\n"
                "A SESUM must contain:\n"
                "- Date and session number\n"
                "- What was built or decided (bullet points, max 15)\n"
                "- What was NOT completed (bullet points, max 5)\n"
                "- Next priorities (numbered, max 5)\n"
                "- Any new ACCA codes mentioned\n"
                "- Any ALP savings found\n"
                "Keep it under 40 lines total. Be specific, not vague."
            )
            kwargs = dict(
                model=p["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate a SESUM from this chat export:\n\n{body[:8000]}"},
                ],
                max_tokens=1200,
                timeout=60,
            )
            if api_key:
                kwargs["api_key"] = api_key
            resp = _ll.completion(**kwargs)
            sesum_text = (resp.choices[0].message.content or "").strip()
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = SESSION_LOGS_DIR / f"sesum_imported_{ts}.md"
            SESSION_LOGS_DIR.mkdir(exist_ok=True)
            out_path.write_text(sesum_text, encoding="utf-8")
            self._send_json({"ok": True, "sesum": sesum_text, "saved_to": str(out_path)})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    # ── Task 4: Missions endpoints ────────────────────────────────────────────────

    MISSIONS_FILE = None  # set after class def

    def _missions_path(self):
        return HERE / "data" / "missions.json"

    def _load_missions(self):
        p = self._missions_path()
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"missions": [], "archived": []}

    def _save_missions(self, data: dict):
        p = self._missions_path()
        p.parent.mkdir(exist_ok=True)
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _handle_api_missions_get(self):
        self._send_json(self._load_missions())

    def _handle_api_missions_post(self):
        try:
            data = json.loads(self._read_body() or "{}")
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        import uuid as _uuid
        data["id"] = data.get("id") or str(_uuid.uuid4())[:8]
        db = self._load_missions()
        db["missions"].append(data)
        self._save_missions(db)
        self._send_json({"ok": True, "mission": data})

    def _handle_api_missions_put(self, mission_id: str):
        try:
            updates = json.loads(self._read_body() or "{}")
        except Exception:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return
        db = self._load_missions()
        found = False
        for m in db["missions"]:
            if m.get("id") == mission_id:
                m.update(updates)
                found = True
                break
        if found:
            self._save_missions(db)
            self._send_json({"ok": True})
        else:
            self._send_json({"ok": False, "error": "Mission not found"}, 404)

    def _handle_api_missions_delete(self, mission_id: str):
        db = self._load_missions()
        to_archive = None
        db["missions"] = [m for m in db["missions"]
                          if not (m.get("id") == mission_id and (to_archive := m) or False)]
        if to_archive is None:
            self._send_json({"ok": False, "error": "Mission not found"}, 404)
            return
        archived = db.get("archived", [])
        to_archive["status"] = "archived"
        archived.append(to_archive)
        db["archived"] = archived
        self._save_missions(db)
        self._send_json({"ok": True, "archived": to_archive})

    # ── Task 7: IBR endpoints ─────────────────────────────────────────────────────

    def _handle_api_ibr_scan(self):
        ibr_script = HERE / "ibr_scanner.py"
        if not ibr_script.exists():
            self._send_json({"ok": False, "error": "ibr_scanner.py not found"}, 500)
            return
        py = FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable)
        try:
            res = subprocess.run(
                [str(py), str(ibr_script)],
                capture_output=True, text=True, timeout=120, cwd=str(HERE),
            )
            ok = res.returncode == 0
            latest_file = HERE / "data" / "ibr_latest.txt"
            report = {}
            if latest_file.exists():
                try:
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_file = HERE / "data" / f"ibr_report_{ts}.json"
                    # ibr_scanner writes its own JSON; load it
                    for jf in sorted((HERE / "data").glob("ibr_report_*.json"), reverse=True):
                        try:
                            report = json.loads(jf.read_text(encoding="utf-8"))
                            break
                        except Exception:
                            pass
                except Exception:
                    pass
            self._send_json({"ok": ok, "stdout": (res.stdout + res.stderr)[-3000:], "report": report})
        except subprocess.TimeoutExpired:
            self._send_json({"ok": False, "error": "Timed out after 120s"})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)

    def _handle_api_ibr_latest(self):
        latest_file = HERE / "data" / "ibr_latest.txt"
        if not latest_file.exists():
            self._send_json({"ok": False, "error": "No IBR report yet — run a scan first"})
            return
        try:
            content = latest_file.read_text(encoding="utf-8", errors="replace")
            self._send_json({"ok": True, "report": content})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, 500)


class ThreadingServer(http.server.ThreadingHTTPServer):
    pass


def _qa_startup_test():
    """Fire-and-forget: test Quick Ask on startup, print result to terminal."""
    import time as _time
    try:
        sys.path.insert(0, str(HERE))
        import litellm as _ll
        from aafl_core import PROVIDERS
        pmap = {p["id"]: p for p in PROVIDERS}
        for pid in ["cerebras", "mistral_code", "gemini_flash"]:
            p = pmap.get(pid)
            if not p:
                continue
            api_key = (p.get("api_key") or
                       os.environ.get(p.get("api_key_env") or "", "") or "")
            if p.get("api_key_env") and not api_key:
                print(f"[MCC] Quick Ask test [{pid}]: SKIP (no API key)", flush=True)
                continue
            try:
                t0 = _time.time()
                kwargs = dict(
                    model=p["model"],
                    messages=[{"role": "user", "content": "1+1="}],
                    max_tokens=16,
                    timeout=15,
                )
                if api_key:
                    kwargs["api_key"] = api_key
                resp = _ll.completion(**kwargs)
                text = (resp.choices[0].message.content or "").strip()
                elapsed = round(_time.time() - t0, 2)
                print(f"[MCC] Quick Ask test [{pid}]: OK ({elapsed}s) -> {text[:40]!r}", flush=True)
                return
            except Exception as exc:
                print(f"[MCC] Quick Ask test [{pid}]: FAILED -> {exc}", flush=True)
        print("[MCC] Quick Ask test: ALL PROVIDERS FAILED", flush=True)
    except Exception as exc:
        print(f"[MCC] Quick Ask test: SETUP ERROR -> {exc}", flush=True)


    # ── Work Checker endpoints ────────────────────────────────────────────────

    def _wc_run_checker(self):
        py = FULL_PYTHON if FULL_PYTHON.exists() else Path(sys.executable)
        if not WORK_CHECKER.exists():
            return None, "work_checker.py not found"
        try:
            res = subprocess.run(
                [str(py), str(WORK_CHECKER)],
                capture_output=True, text=True, timeout=60, cwd=str(HERE),
            )
            if res.returncode != 0:
                return None, (res.stderr or res.stdout).strip()
            if WORK_REPORT.exists():
                return json.loads(WORK_REPORT.read_text(encoding="utf-8")), None
            return None, "work_report.json not written"
        except Exception as exc:
            return None, str(exc)

    def _handle_wc_report(self):
        if WORK_REPORT.exists():
            age = datetime.datetime.now().timestamp() - WORK_REPORT.stat().st_mtime
            if age < 300:
                try:
                    self._send_json(json.loads(WORK_REPORT.read_text(encoding="utf-8")))
                    return
                except Exception:
                    pass
        report, err = self._wc_run_checker()
        if report:
            self._send_json(report)
        else:
            self._send_json({"error": err or "Unknown error"}, 500)

    def _handle_wc_refresh(self):
        report, err = self._wc_run_checker()
        if report:
            self._send_json(report)
        else:
            self._send_json({"ok": False, "error": err or "Unknown error"}, 500)

    def _handle_wc_requeue(self):
        report = None
        if WORK_REPORT.exists():
            try:
                report = json.loads(WORK_REPORT.read_text(encoding="utf-8"))
            except Exception:
                pass
        if not report:
            report, _ = self._wc_run_checker()
        if not report:
            body = b"work_report.json not found"
            self.send_response(500)
            self._cors()
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        text = report.get("requeue_block", "No requeue block found.")
        body = text.encode("utf-8")
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_wc_orphaned(self):
        report = None
        if WORK_REPORT.exists():
            try:
                report = json.loads(WORK_REPORT.read_text(encoding="utf-8"))
            except Exception:
                pass
        if not report:
            report, _ = self._wc_run_checker()
        if not report:
            self._send_json({"error": "work_report.json not found"}, 500)
            return
        self._send_json(report.get("orphaned_plans", []))


# ── OCB-A: Self-Health handlers — monkey-patched onto MCCHandler ──────────────

def _sh_import_runner():
    """Import SelfHealthRunner lazily to avoid circular startup cost."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("self_health", HERE / "self_health.py")
    if not spec or not spec.loader:
        raise ImportError("self_health.py not found")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SelfHealthRunner


def _sh_handle_registry(self):
    if SH_REGISTRY.exists():
        try:
            self._send_json(json.loads(SH_REGISTRY.read_text(encoding="utf-8")))
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)
            return
    self._send_json({"error": "registry not found"}, 404)


def _sh_handle_last_run(self):
    try:
        runner = _sh_import_runner()()
        last = runner.get_last_run()
        self._send_json(last or {})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _sh_handle_run_all(self):
    try:
        runner = _sh_import_runner()()
        summary = runner.run_all(trigger_source="manual")
        self._send_json(summary)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _sh_handle_run_tab(self):
    body = self._read_body()
    try:
        data = json.loads(body) if body else {}
    except Exception:
        data = {}
    tab = data.get("tab", "")
    if not tab:
        self._send_json({"error": "tab required"}, 400)
        return
    try:
        runner = _sh_import_runner()()
        summary = runner.run_by_tab(tab)
        self._send_json(summary)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _sh_handle_config_get(self):
    if SH_CONFIG.exists():
        try:
            self._send_json(json.loads(SH_CONFIG.read_text(encoding="utf-8")))
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)
            return
    self._send_json({"error": "config not found"}, 404)


def _sh_handle_config_post(self):
    body = self._read_body()
    try:
        new_cfg = json.loads(body) if body else {}
    except Exception as exc:
        self._send_json({"error": f"Invalid JSON: {exc}"}, 400)
        return
    try:
        existing = {}
        if SH_CONFIG.exists():
            try:
                existing = json.loads(SH_CONFIG.read_text(encoding="utf-8"))
            except Exception:
                pass
        existing.update(new_cfg)
        tmp = SH_CONFIG.with_suffix(".tmp")
        tmp.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        tmp.replace(SH_CONFIG)
        self._send_json({"ok": True})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _sh_handle_solutions(self):
    if SH_SOLUTIONS.exists():
        try:
            self._send_json(json.loads(SH_SOLUTIONS.read_text(encoding="utf-8")))
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)
            return
    self._send_json({"error": "solution_database.json not found"}, 404)


def _sh_handle_history(self):
    try:
        runner = _sh_import_runner()()
        history = runner.get_history(limit=50)
        self._send_json(history)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_sh_registry   = _sh_handle_registry    # type: ignore[attr-defined]
MCCHandler._handle_sh_last_run   = _sh_handle_last_run    # type: ignore[attr-defined]
MCCHandler._handle_sh_run_all    = _sh_handle_run_all     # type: ignore[attr-defined]
MCCHandler._handle_sh_run_tab    = _sh_handle_run_tab     # type: ignore[attr-defined]
MCCHandler._handle_sh_config_get = _sh_handle_config_get  # type: ignore[attr-defined]
MCCHandler._handle_sh_config_post= _sh_handle_config_post # type: ignore[attr-defined]
MCCHandler._handle_sh_solutions  = _sh_handle_solutions   # type: ignore[attr-defined]
MCCHandler._handle_sh_history    = _sh_handle_history     # type: ignore[attr-defined]


# ── OCB-B: Results + Element History endpoints ────────────────────────────────

def _sh_handle_results(self):
    """GET /api/self-health/results?run_id=xxx — results for one run."""
    import sqlite3
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
    run_id = (qs.get("run_id") or [None])[0]
    if not run_id:
        self._send_json({"error": "run_id required"}, 400)
        return
    try:
        if not SH_HEALTH_DB.exists():
            self._send_json([])
            return
        conn = sqlite3.connect(str(SH_HEALTH_DB))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM health_results WHERE test_run_id=? ORDER BY id",
            (run_id,)
        ).fetchall()
        conn.close()
        self._send_json([dict(r) for r in rows])
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _sh_handle_element_history(self):
    """GET /api/self-health/element-history?element_id=xxx — last 50 results for element."""
    import sqlite3
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
    element_id = (qs.get("element_id") or [None])[0]
    if not element_id:
        self._send_json({"error": "element_id required"}, 400)
        return
    try:
        if not SH_HEALTH_DB.exists():
            self._send_json([])
            return
        conn = sqlite3.connect(str(SH_HEALTH_DB))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM health_results WHERE element_id=? ORDER BY id DESC LIMIT 50",
            (element_id,)
        ).fetchall()
        conn.close()
        self._send_json([dict(r) for r in rows])
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_sh_results        = _sh_handle_results        # type: ignore[attr-defined]
MCCHandler._handle_sh_element_history = _sh_handle_element_history # type: ignore[attr-defined]


# ── OCB-B: Auto-Fix Engine endpoints ─────────────────────────────────────────

def _af_load_proposals() -> list:
    if AF_PROPOSALS.exists():
        try:
            data = json.loads(AF_PROPOSALS.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            pass
    return []


def _af_save_proposals(proposals: list):
    AF_PROPOSALS.parent.mkdir(parents=True, exist_ok=True)
    AF_PROPOSALS.write_text(json.dumps(proposals, indent=2, ensure_ascii=False), encoding="utf-8")


def _af_load_history() -> list:
    if AF_HISTORY_FILE.exists():
        try:
            data = json.loads(AF_HISTORY_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            pass
    return []


def _af_save_history(history: list):
    AF_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    AF_HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def _af_handle_proposals(self):
    """GET /api/auto-fix/proposals — pending proposals awaiting approval."""
    proposals = _af_load_proposals()
    pending = [p for p in proposals if p.get("status") == "awaiting_approval"]
    self._send_json(pending)


def _af_handle_history(self):
    """GET /api/auto-fix/history — all applied/rejected fixes."""
    self._send_json(_af_load_history())


def _af_handle_approve(self):
    """POST /api/auto-fix/approve — body: {fix_id} — executes the fix."""
    import subprocess as _sp
    try:
        body = json.loads(self._read_body() or "{}")
    except Exception:
        self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
        return
    fix_id = body.get("fix_id", "").strip()
    if not fix_id:
        self._send_json({"ok": False, "error": "fix_id required"}, 400)
        return

    proposals = _af_load_proposals()
    proposal  = next((p for p in proposals if p.get("fix_id") == fix_id), None)
    if not proposal:
        self._send_json({"ok": False, "error": "Proposal not found"}, 404)
        return

    # Load solution
    solutions = []
    try:
        solutions = json.loads(SH_SOLUTIONS.read_text(encoding="utf-8")).get("solutions", [])
    except Exception:
        pass
    solution = next((s for s in solutions if s.get("id") == proposal.get("solution_id")), None)

    success = False
    stdout_log = ""
    stderr_log = ""
    if solution:
        try:
            for step in solution.get("fix_steps", []):
                result = _sp.run(step, shell=True, capture_output=True, text=True, cwd=str(HERE), timeout=30)
                stdout_log += result.stdout
                stderr_log += result.stderr
            success = True
        except Exception as exc:
            stderr_log += str(exc)

    # Update proposal status
    for p in proposals:
        if p.get("fix_id") == fix_id:
            p["status"] = "applied" if success else "failed"
            p["applied_at"] = datetime.datetime.now().isoformat(timespec="seconds")
            break
    _af_save_proposals(proposals)

    # Log to history
    history = _af_load_history()
    history.insert(0, {
        "fix_id":     fix_id,
        "element_id": proposal.get("element_id", ""),
        "fix_name":   solution.get("name", fix_id) if solution else fix_id,
        "success":    success,
        "applied_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "stdout":     stdout_log[:500],
        "stderr":     stderr_log[:500],
    })
    _af_save_history(history[:200])

    self._send_json({"ok": True, "success": success, "stdout": stdout_log[:200], "stderr": stderr_log[:200]})


def _af_handle_reject(self):
    """POST /api/auto-fix/reject — body: {fix_id} — marks proposal rejected."""
    try:
        body = json.loads(self._read_body() or "{}")
    except Exception:
        self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
        return
    fix_id = body.get("fix_id", "").strip()
    if not fix_id:
        self._send_json({"ok": False, "error": "fix_id required"}, 400)
        return
    proposals = _af_load_proposals()
    for p in proposals:
        if p.get("fix_id") == fix_id:
            p["status"] = "rejected"
            p["rejected_at"] = datetime.datetime.now().isoformat(timespec="seconds")
            break
    _af_save_proposals(proposals)
    self._send_json({"ok": True})


MCCHandler._handle_af_proposals = _af_handle_proposals  # type: ignore[attr-defined]
MCCHandler._handle_af_history   = _af_handle_history    # type: ignore[attr-defined]
MCCHandler._handle_af_approve   = _af_handle_approve    # type: ignore[attr-defined]
MCCHandler._handle_af_reject    = _af_handle_reject     # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-C: Storage stats, largest files, quota reallocation
# ═══════════════════════════════════════════════════════════════════════════════

def _handle_storage_stats(self):
    """GET /api/storage/stats — slot sizes, totals, growth trends."""
    try:
        from storage_manager import check_all_slots
        data = check_all_slots()
        slots_list = list(data.get("slots", {}).values())
        # Build growth map (stub — would need historical data in a real impl)
        growth = {s["name"]: 0.0 for s in slots_list}
        self._send_json({
            "ok": True,
            "slots": slots_list,
            "total_allocated_gb": data.get("total_allocated_gb", 1000),
            "total_used_gb": data.get("total_used_gb", 0.0),
            "growth_gb_per_day": growth,
            "trend": [],
            "archive_log": [],
        })
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


def _handle_storage_largest(self):
    """GET /api/storage/largest — top 10 biggest files across all slots."""
    try:
        from storage_manager import _load_config, _resolve_folder
        cfg = _load_config()
        all_files = []
        for slot in cfg.get("slots", []):
            folder = _resolve_folder(slot)
            if not folder.exists():
                continue
            for f in folder.rglob("*"):
                if not f.is_file():
                    continue
                try:
                    stat   = f.stat()
                    age    = int((datetime.datetime.now().timestamp() - stat.st_mtime) / 86400)
                    all_files.append({
                        "name":     f.name,
                        "path":     str(f),
                        "size_gb":  round(stat.st_size / (1024**3), 6),
                        "slot":     slot["name"],
                        "age_days": age,
                    })
                except Exception:
                    pass
        all_files.sort(key=lambda x: x["size_gb"], reverse=True)
        self._send_json({"ok": True, "files": all_files[:10]})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


def _handle_storage_reallocate(self):
    """POST /api/storage/reallocate — body: {quotas: {slot_name: gb}} — update quotas in storage_config.json."""
    try:
        body = json.loads(self._read_body() or "{}")
        quotas = body.get("quotas", {})
        cfg = json.loads(STORAGE_CFG.read_text(encoding="utf-8")) if STORAGE_CFG.exists() else {}
        changed = 0
        for slot in cfg.get("slots", []):
            name = slot.get("name", "")
            if name in quotas:
                slot["quota_gb"] = float(quotas[name])
                changed += 1
        STORAGE_CFG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
        self._send_json({"ok": True, "changed": changed})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


def _handle_storage_detailed(self):
    """GET /api/storage/detailed — per-slot breakdown with top 20 files each."""
    try:
        from storage_manager import _load_config, _resolve_folder
        cfg = _load_config()
        result = []
        for slot in cfg.get("slots", []):
            folder = _resolve_folder(slot)
            files = []
            if folder.exists():
                for f in folder.rglob("*"):
                    if not f.is_file():
                        continue
                    try:
                        st = f.stat()
                        files.append({
                            "name": f.name,
                            "path": str(f.relative_to(folder)),
                            "size_kb": round(st.st_size / 1024, 1),
                            "age_days": int((datetime.datetime.now().timestamp() - st.st_mtime) / 86400),
                        })
                    except Exception:
                        pass
            files.sort(key=lambda x: x["size_kb"], reverse=True)
            total_size = sum(f["size_kb"] for f in files)
            result.append({
                "name": slot.get("name", ""),
                "quota_gb": slot.get("quota_gb", 0),
                "used_kb": round(total_size, 1),
                "used_gb": round(total_size / (1024 * 1024), 4),
                "file_count": len(files),
                "top_files": files[:20],
            })
        self._send_json({"ok": True, "slots": result})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


def _handle_storage_forecast(self):
    """GET /api/storage/forecast — growth prediction per slot."""
    try:
        from storage_manager import _load_config, _resolve_folder
        cfg = _load_config()
        forecasts = []
        for slot in cfg.get("slots", []):
            folder = _resolve_folder(slot)
            if not folder.exists():
                continue
            files = list(folder.rglob("*"))
            files = [f for f in files if f.is_file()]
            if not files:
                continue
            total_bytes = sum(f.stat().st_size for f in files if f.exists())
            quota_bytes = slot.get("quota_gb", 1) * 1024**3
            used_pct = (total_bytes / quota_bytes * 100) if quota_bytes > 0 else 0
            # Simple linear growth: estimate based on files added in last 7 days
            now = datetime.datetime.now().timestamp()
            week_ago = now - 7 * 86400
            recent_bytes = sum(f.stat().st_size for f in files if f.stat().st_mtime > week_ago)
            daily_growth = recent_bytes / 7 if recent_bytes > 0 else total_bytes * 0.01
            remaining = quota_bytes - total_bytes
            days_to_full = int(remaining / daily_growth) if daily_growth > 0 else 9999
            forecasts.append({
                "name": slot.get("name", ""),
                "used_pct": round(used_pct, 1),
                "daily_growth_kb": round(daily_growth / 1024, 1),
                "days_to_full": min(days_to_full, 9999),
                "status": "red" if days_to_full < 30 else "amber" if days_to_full < 90 else "green",
            })
        self._send_json({"ok": True, "forecasts": forecasts})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


def _handle_storage_treemap(self):
    """GET /api/storage/treemap — file type breakdown across all slots."""
    try:
        from storage_manager import _load_config, _resolve_folder
        cfg = _load_config()
        ext_map: dict = {}
        for slot in cfg.get("slots", []):
            folder = _resolve_folder(slot)
            if not folder.exists():
                continue
            for f in folder.rglob("*"):
                if not f.is_file():
                    continue
                try:
                    ext = f.suffix.lower() or ".other"
                    size = f.stat().st_size
                    if ext not in ext_map:
                        ext_map[ext] = {"count": 0, "size_bytes": 0}
                    ext_map[ext]["count"] += 1
                    ext_map[ext]["size_bytes"] += size
                except Exception:
                    pass
        colours = {".py": "#4A90D9", ".json": "#50C878", ".html": "#FF6B6B",
                   ".md": "#8B5CF6", ".txt": "#FFD700", ".db": "#FF9500",
                   ".bat": "#EC4899", ".csv": "#10B981"}
        items = sorted([
            {"ext": ext, "count": v["count"],
             "size_kb": round(v["size_bytes"] / 1024, 1),
             "colour": colours.get(ext, "#555555")}
            for ext, v in ext_map.items()
        ], key=lambda x: x["size_kb"], reverse=True)
        self._send_json({"ok": True, "items": items[:30]})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


def _handle_storage_archive_history(self):
    """GET /api/storage/archive-history — archive timeline data (last 90 days)."""
    try:
        archive_log_path = HERE / "archive_logs.json"
        history: dict = {}
        if archive_log_path.exists():
            log = json.loads(archive_log_path.read_text(encoding="utf-8"))
            for entry in (log if isinstance(log, list) else log.get("entries", [])):
                day = str(entry.get("date", ""))[:10]
                if day:
                    history[day] = history.get(day, 0) + 1
        # Also scan archive_dead folder
        dead_dir = HERE / "archive_dead"
        if dead_dir.exists():
            for f in dead_dir.iterdir():
                if f.is_file():
                    try:
                        day = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
                        history[day] = history.get(day, 0) + 1
                    except Exception:
                        pass
        self._send_json({"ok": True, "history": history})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


def _handle_launch_spindoctor(self):
    """POST /api/launch-spindoctor — launch spin_doctor.py GUI."""
    try:
        subprocess.Popen(
            [sys.executable, str(HERE / "spin_doctor.py")],
            cwd=str(HERE),
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )
        self._send_json({"ok": True})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


def _handle_health_latest(self):
    """GET /api/health/latest — return last MOT / medical score."""
    try:
        result = {}
        if LATEST_HEALTH.exists():
            result = json.loads(LATEST_HEALTH.read_text(encoding="utf-8"))
        mot_file = HEALTH_RESULTS / "full_mot_report.json"
        if mot_file.exists():
            mot = json.loads(mot_file.read_text(encoding="utf-8"))
            result["mot_score"] = f"{mot.get('passed',0)}/{mot.get('total',0)}"
        result["ok"] = True
        self._send_json(result)
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


MCCHandler._handle_storage_stats          = _handle_storage_stats           # type: ignore[attr-defined]
MCCHandler._handle_storage_largest        = _handle_storage_largest          # type: ignore[attr-defined]
MCCHandler._handle_storage_reallocate     = _handle_storage_reallocate       # type: ignore[attr-defined]
MCCHandler._handle_storage_detailed       = _handle_storage_detailed         # type: ignore[attr-defined]
MCCHandler._handle_storage_forecast       = _handle_storage_forecast         # type: ignore[attr-defined]
MCCHandler._handle_storage_treemap        = _handle_storage_treemap          # type: ignore[attr-defined]
MCCHandler._handle_storage_archive_history= _handle_storage_archive_history  # type: ignore[attr-defined]
MCCHandler._handle_launch_spindoctor  = _handle_launch_spindoctor    # type: ignore[attr-defined]
MCCHandler._handle_health_latest      = _handle_health_latest        # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-C: System monitor endpoints (delegates to system_monitor.py)
# ═══════════════════════════════════════════════════════════════════════════════

def _handle_system_snapshot(self):
    """GET /api/system/snapshot — full system state."""
    try:
        from system_monitor import SystemMonitor
        sm = SystemMonitor()
        self._send_json(sm.get_full_snapshot())
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)

def _handle_system_cpu(self):
    """GET /api/system/cpu — CPU only."""
    try:
        from system_monitor import SystemMonitor
        self._send_json(SystemMonitor().get_cpu())
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)

def _handle_system_ram(self):
    """GET /api/system/ram — RAM only."""
    try:
        from system_monitor import SystemMonitor
        self._send_json(SystemMonitor().get_ram())
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)

def _handle_system_gpu(self):
    """GET /api/system/gpu — GPU only."""
    try:
        from system_monitor import SystemMonitor
        self._send_json(SystemMonitor().get_gpu())
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)

def _handle_system_ai_allocation(self):
    """GET /api/system/ai-allocation — AI process breakdown."""
    try:
        from system_monitor import SystemMonitor
        self._send_json(SystemMonitor().get_ai_allocation())
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


def _handle_system_kill(self):
    """POST /api/system/kill — terminate a process by PID (AI processes only)."""
    try:
        import psutil
        body = json.loads(self._read_body())
        pid = int(body.get("pid", 0))
        if not pid:
            self._send_json({"ok": False, "error": "pid required"}, 400)
            return
        proc = psutil.Process(pid)
        name = proc.name().lower()
        _ai_safe = {"python", "node", "lm studio", "mcc_server", "loop_manager", "aafl"}
        if not any(k in name for k in _ai_safe):
            self._send_json({"ok": False, "error": f"Process '{name}' not in AI-safe list"}, 403)
            return
        proc.terminate()
        self._send_json({"ok": True, "killed_pid": pid, "name": name})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


# ── OCB-D: LLOW handlers ─────────────────────────────────────────────────────

def _handle_llow_elements(self):
    """GET /api/llow/elements — return llow_elements.json."""
    try:
        data = json.loads(LLOW_ELEMENTS_FILE.read_text(encoding="utf-8"))
        self._send_json(data)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_llow_arrows(self):
    """GET /api/llow/arrows — return llow_arrows.json."""
    try:
        data = json.loads(LLOW_ARROWS_FILE.read_text(encoding="utf-8"))
        self._send_json(data)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_llow_list_workflows(self):
    """GET /api/llow/workflows — list saved workflows."""
    try:
        from llow_engine import LLOWEngine
        engine = LLOWEngine()
        self._send_json(engine.list_workflows())
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_llow_get_workflow(self, name: str):
    """GET /api/llow/workflow/<name> — load a specific workflow."""
    try:
        from llow_engine import LLOWEngine
        engine = LLOWEngine()
        wf = engine.load_workflow(name)
        self._send_json(wf)
    except FileNotFoundError:
        self._send_json({"error": f"Workflow not found: {name}"}, 404)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_llow_save_workflow(self):
    """POST /api/llow/workflow — save workflow JSON."""
    try:
        wf = json.loads(self._read_body())
        from llow_engine import LLOWEngine
        engine = LLOWEngine()
        filename = wf.get("name", "unnamed").replace(" ", "_").lower()
        import re as _re
        filename = _re.sub(r"[^\w\-]", "_", filename)
        path = engine.save_workflow(wf, filename)
        self._send_json({"ok": True, "filename": path.name})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_llow_delete_workflow(self, name: str):
    """DELETE /api/llow/workflow/<name> — delete a workflow."""
    try:
        from llow_engine import LLOWEngine
        engine = LLOWEngine()
        deleted = engine.delete_workflow(name)
        self._send_json({"ok": deleted})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_llow_validate(self):
    """POST /api/llow/validate — validate workflow, return errors/warnings."""
    try:
        wf = json.loads(self._read_body())
        from llow_engine import LLOWEngine
        engine = LLOWEngine()
        valid, warnings = engine.validate_workflow(wf)
        self._send_json({"valid": valid, "warnings": warnings})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_llow_export_clacr(self):
    """POST /api/llow/export-clacr — convert workflow to CLACR text."""
    try:
        wf = json.loads(self._read_body())
        from llow_engine import LLOWEngine
        engine = LLOWEngine()
        clacr = engine.export_as_clacr(wf)
        self._send_json({"clacr": clacr})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_llow_run(self):
    """POST /api/llow/run — execute workflow via loop_manager."""
    try:
        wf = json.loads(self._read_body())
        from loop_manager import run_llow_workflow
        import threading as _threading
        t = _threading.Thread(target=run_llow_workflow, args=(wf,), daemon=True)
        t.start()
        self._send_json({"ok": True, "message": "LLOW run started"})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_llow_dry_run(self):
    """POST /api/llow/dry-run — validate + simulate without executing."""
    try:
        wf = json.loads(self._read_body())
        from llow_engine import LLOWEngine
        engine = LLOWEngine()
        valid, warnings = engine.validate_workflow(wf)
        # Simulate step order
        steps = wf.get("steps", [])
        arrows = wf.get("arrows", [])
        out: dict = {}
        for a in arrows:
            out.setdefault(a["from"], []).append(a["to"])
        ordered = []
        visited: set = set()
        queue = [steps[0]["id"]] if steps else []
        step_map = {s["id"]: s for s in steps}
        while queue:
            sid = queue.pop(0)
            if sid in visited:
                continue
            visited.add(sid)
            ordered.append(step_map.get(sid, {}).get("element_id", sid))
            for nxt in out.get(sid, []):
                if nxt not in visited:
                    queue.append(nxt)
        self._send_json({
            "valid": valid,
            "warnings": warnings,
            "simulated_order": ordered,
            "step_count": len(steps),
            "arrow_count": len(arrows),
        })
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_llow_elements       = _handle_llow_elements        # type: ignore[attr-defined]
MCCHandler._handle_llow_arrows         = _handle_llow_arrows          # type: ignore[attr-defined]
MCCHandler._handle_llow_list_workflows = _handle_llow_list_workflows  # type: ignore[attr-defined]
MCCHandler._handle_llow_get_workflow   = _handle_llow_get_workflow    # type: ignore[attr-defined]
MCCHandler._handle_llow_save_workflow  = _handle_llow_save_workflow   # type: ignore[attr-defined]
MCCHandler._handle_llow_delete_workflow= _handle_llow_delete_workflow # type: ignore[attr-defined]
MCCHandler._handle_llow_validate       = _handle_llow_validate        # type: ignore[attr-defined]
MCCHandler._handle_llow_export_clacr   = _handle_llow_export_clacr   # type: ignore[attr-defined]
MCCHandler._handle_llow_run            = _handle_llow_run             # type: ignore[attr-defined]
MCCHandler._handle_llow_dry_run        = _handle_llow_dry_run         # type: ignore[attr-defined]


MCCHandler._handle_system_kill          = _handle_system_kill           # type: ignore[attr-defined]
MCCHandler._handle_system_snapshot      = _handle_system_snapshot       # type: ignore[attr-defined]
MCCHandler._handle_system_cpu           = _handle_system_cpu            # type: ignore[attr-defined]
MCCHandler._handle_system_ram           = _handle_system_ram            # type: ignore[attr-defined]
MCCHandler._handle_system_gpu           = _handle_system_gpu            # type: ignore[attr-defined]
MCCHandler._handle_system_ai_allocation = _handle_system_ai_allocation  # type: ignore[attr-defined]


INSTRUCTIONS_DB = HERE / "data" / "instructions_db.json"


def _handle_api_instructions(self):
    """GET /api/instructions — return full instructions_db.json."""
    try:
        if not INSTRUCTIONS_DB.exists():
            self._send_json({"error": "instructions_db.json not found"}, 404)
            return
        data = json.loads(INSTRUCTIONS_DB.read_text(encoding="utf-8"))
        self._send_json(data)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_api_instructions_element(self, element_id: str):
    """GET /api/instructions/<element_id> — return one element entry."""
    try:
        if not INSTRUCTIONS_DB.exists():
            self._send_json({"error": "instructions_db.json not found"}, 404)
            return
        data = json.loads(INSTRUCTIONS_DB.read_text(encoding="utf-8"))
        elements = data.get("elements", {})
        if element_id not in elements:
            self._send_json({"error": "not found", "element_id": element_id}, 404)
            return
        self._send_json(elements[element_id])
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_api_instructions         = _handle_api_instructions          # type: ignore[attr-defined]
MCCHandler._handle_api_instructions_element = _handle_api_instructions_element  # type: ignore[attr-defined]


# ── OCB-J: Safety Shield endpoint ────────────────────────────────────────────

def _handle_safety_status(self):
    """GET /api/safety-status — runs HC-02, HC-09, HC-10, HC-03 + allow_paid check."""
    import re as _re
    checks = []

    # HC-02: API Keys (never log values)
    api_keys = ["ANTHROPIC_API_KEY", "GROQ_API_KEY", "CLOUDFLARE_API_KEY", "CLOUDFLARE_ACCOUNT_ID"]
    present = [k for k in api_keys if os.environ.get(k)]
    missing = [k for k in api_keys if not os.environ.get(k)]
    checks.append({
        "name":   "API Keys",
        "status": "PASS" if not missing else "WARN",
        "detail": (f"Present: {len(present)}/{len(api_keys)}" +
                   (f" — Missing: {', '.join(missing)}" if missing else "")),
    })

    # HC-09: Cost Cap
    try:
        cfg_data = json.loads(AAFL_SETTINGS.read_text(encoding="utf-8")) if AAFL_SETTINGS.exists() else {}
        cap_found = None
        for key in ("cost_cap", "cost_cap_per_goal_usd", "cost_cap_per_goal_gbp"):
            val = cfg_data.get(key)
            if val is not None and float(val) > 0:
                cap_found = (key, val)
                break
        if cap_found:
            checks.append({"name": "Cost Cap", "status": "PASS",
                           "detail": f"{cap_found[0]} = {cap_found[1]}"})
        else:
            checks.append({"name": "Cost Cap", "status": "FAIL",
                           "detail": "No cost_cap key found or value is 0"})
    except Exception as exc:
        checks.append({"name": "Cost Cap", "status": "FAIL", "detail": str(exc)})

    # HC-10: Watchdog Wiring (split into Watchdog + Cost Guard pills)
    lm_path = HERE / "loop_manager.py"
    if lm_path.exists():
        lm_text = lm_path.read_text(encoding="utf-8", errors="replace")
        wd_import = bool(_re.search(r'from\s+aafl_watchdog\b|import\s+aafl_watchdog\b', lm_text))
        wd_call   = bool(_re.search(r'_watchdog_run_cycle|_watchdog_check', lm_text))
        cg_import = bool(_re.search(r'from\s+cost_guard\b|import\s+cost_guard\b', lm_text))
        cg_call   = bool(_re.search(r'CostGuard\s*\(|guard\.check|guard\.record', lm_text))

        if wd_import and wd_call:
            checks.append({"name": "Watchdog", "status": "PASS",
                           "detail": "aafl_watchdog imported and called"})
        else:
            miss = []
            if not wd_import: miss.append("import missing")
            if not wd_call:   miss.append("call missing")
            checks.append({"name": "Watchdog", "status": "FAIL",
                           "detail": f"aafl_watchdog: {', '.join(miss)}"})

        if cg_import and cg_call:
            checks.append({"name": "Cost Guard", "status": "PASS",
                           "detail": "cost_guard imported and called"})
        else:
            miss = []
            if not cg_import: miss.append("import missing")
            if not cg_call:   miss.append("call missing")
            checks.append({"name": "Cost Guard", "status": "FAIL",
                           "detail": f"cost_guard: {', '.join(miss)}"})
    else:
        checks.append({"name": "Watchdog",   "status": "FAIL", "detail": "loop_manager.py not found"})
        checks.append({"name": "Cost Guard", "status": "FAIL", "detail": "loop_manager.py not found"})

    # HC-03: Disk Space
    disk_results = []
    disk_status = "PASS"
    for drive in ("C:\\", "D:\\"):
        try:
            free_gb = round(shutil.disk_usage(drive).free / 1024 ** 3, 1)
            label = f"{drive} {free_gb}GB"
            if free_gb < 10:
                label += " ⚠"
                disk_status = "WARN"
            disk_results.append(label)
        except Exception:
            disk_results.append(f"{drive} N/A")
    checks.append({"name": "Disk Space", "status": disk_status,
                   "detail": " | ".join(disk_results)})

    # allow_paid check
    try:
        cfg_data = json.loads(AAFL_SETTINGS.read_text(encoding="utf-8")) if AAFL_SETTINGS.exists() else {}
        allow_paid = cfg_data.get("allow_paid", False)
        if allow_paid:
            checks.append({"name": "Claude Blocked", "status": "WARN",
                           "detail": "allow_paid = True — paid API can run"})
        else:
            checks.append({"name": "Claude Blocked", "status": "PASS",
                           "detail": "allow_paid = False — Claude blocked (safe)"})
    except Exception as exc:
        checks.append({"name": "Claude Blocked", "status": "FAIL", "detail": str(exc)})

    overall = "SAFE" if not any(c["status"] == "FAIL" for c in checks) else "DANGER"
    self._send_json({"overall": overall, "checks": checks})


MCCHandler._handle_safety_status = _handle_safety_status  # type: ignore[attr-defined]


# ── OCB-O: Watchdog status ────────────────────────────────────────────────────

def _handle_watchdog_status(self):
    """GET /api/watchdog/status — checks if aafl_watchdog.py is running via psutil."""
    running = False
    pid = None
    try:
        import psutil as _psutil
        for p in _psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmd = " ".join(p.info.get("cmdline") or [])
                if "aafl_watchdog" in cmd:
                    running = True
                    pid = p.info["pid"]
                    break
            except Exception:
                continue
    except Exception:
        pass
    self._send_json({"running": running, "pid": pid})


MCCHandler._handle_watchdog_status = _handle_watchdog_status  # type: ignore[attr-defined]


# ── OCB-O: Health run history ─────────────────────────────────────────────────

def _handle_health_run_history(self):
    """GET /api/health/history — last 10+ runs from health.db health_runs table."""
    import sqlite3 as _sq
    rows = []
    try:
        if SH_HEALTH_DB.exists():
            conn = _sq.connect(str(SH_HEALTH_DB))
            conn.row_factory = _sq.Row
            for r in conn.execute(
                "SELECT * FROM health_runs ORDER BY started_at DESC LIMIT 20"
            ):
                d = dict(r)
                total = (d.get("passed") or 0) + (d.get("failed") or 0) + (d.get("warned") or 0)
                score = round(((d.get("passed") or 0) / max(total, 1)) * 100) if total else 0
                rows.append({
                    "fitness_score": score,
                    "run_at":        d.get("finished_at") or d.get("started_at", ""),
                    "verdict":       f"Self-health: {d.get('passed',0)} passed, {d.get('failed',0)} failed",
                    "passed":        d.get("passed") or 0,
                    "failed":        d.get("failed") or 0,
                    "warned":        d.get("warned") or 0,
                    "source":        "health.db",
                })
            conn.close()
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc), "history": []})
        return
    self._send_json({"ok": True, "history": rows[::-1]})  # oldest first


MCCHandler._handle_health_run_history = _handle_health_run_history  # type: ignore[attr-defined]


# ── OCB-J: CLACHR Relay endpoints ─────────────────────────────────────────────

def _handle_clachr_queue(self):
    """GET /api/clachr/queue — returns goal_queue.txt as JSON array."""
    tasks = []
    if GOAL_QUEUE.exists():
        try:
            for line in GOAL_QUEUE.read_text(encoding="utf-8", errors="replace").splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    tasks.append(stripped)
        except Exception:
            pass
    self._send_json(tasks)


def _handle_clachr_results(self):
    """GET /api/clachr/results — latest 20 files from aafl_output/."""
    results = []
    if AAFL_OUTPUT.exists():
        files = sorted(
            [f for f in AAFL_OUTPUT.iterdir() if f.is_file()],
            key=lambda f: f.stat().st_mtime, reverse=True,
        )[:20]
        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                ts = datetime.datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds")
                status = "DONE"
                if "[ERROR]" in content or "[FAIL]" in content.upper():
                    status = "FAILED"
                elif "[RUNNING]" in content:
                    status = "RUNNING"
                results.append({
                    "goal":      f.stem,
                    "result":    content[:500],
                    "timestamp": ts,
                    "status":    status,
                })
            except Exception:
                continue
    self._send_json(results)


def _handle_clachr_dispatch(self):
    """POST /api/clachr/dispatch — runs queue_runner.py as non-blocking subprocess."""
    runner = HERE / "queue_runner.py"
    if not runner.exists():
        self._send_json({"status": "error", "detail": "queue_runner.py not found"}, 404)
        return
    task_count = 0
    if GOAL_QUEUE.exists():
        try:
            lines = [l.strip() for l in GOAL_QUEUE.read_text(encoding="utf-8").splitlines()
                     if l.strip() and not l.strip().startswith("#")]
            task_count = len(lines)
        except Exception:
            pass
    try:
        subprocess.Popen(
            [PYTHON, str(runner)],
            cwd=str(HERE),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._send_json({"status": "dispatched", "task_count": task_count})
    except Exception as exc:
        self._send_json({"status": "error", "detail": str(exc)}, 500)


def _handle_clachr_clear(self):
    """DELETE /api/clachr/clear — empties goal_queue.txt."""
    try:
        GOAL_QUEUE.write_text("", encoding="utf-8")
        self._send_json({"status": "cleared"})
    except Exception as exc:
        self._send_json({"status": "error", "detail": str(exc)}, 500)


MCCHandler._handle_clachr_queue    = _handle_clachr_queue     # type: ignore[attr-defined]
MCCHandler._handle_clachr_results  = _handle_clachr_results   # type: ignore[attr-defined]
MCCHandler._handle_clachr_dispatch = _handle_clachr_dispatch  # type: ignore[attr-defined]
MCCHandler._handle_clachr_clear    = _handle_clachr_clear     # type: ignore[attr-defined]


# ── OCB-J: AFNA Suggestions endpoint ─────────────────────────────────────────

AFNA_STRATEGIES_FILE = HERE / "afna_strategies.json"


def _handle_stuck_afna_suggestions(self):
    """GET /api/stuck/afna-suggestions — returns full strategies array from afna_strategies.json."""
    try:
        if not AFNA_STRATEGIES_FILE.exists():
            self._send_json({"error": "afna_strategies.json not found"}, 404)
            return
        data = json.loads(AFNA_STRATEGIES_FILE.read_text(encoding="utf-8"))
        strategies = data.get("strategies", data) if isinstance(data, dict) else data
        self._send_json(strategies)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_stuck_afna_suggestions = _handle_stuck_afna_suggestions  # type: ignore[attr-defined]


# ── OCB-K: MOT Live SSE endpoint ─────────────────────────────────────────────

def _handle_mot_live_sse(self):
    """GET /api/mot/live — streams mcc_full_mot.py --live output as Server-Sent Events."""
    try:
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        proc = subprocess.Popen(
            [PYTHON, str(MOT_SCRIPT), "--live"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, cwd=str(HERE), bufsize=1,
        )
        try:
            for line in proc.stdout:
                line = line.rstrip()
                if not line:
                    continue
                msg = json.dumps({"line": line})
                self.wfile.write(f"data: {msg}\n\n".encode("utf-8"))
                self.wfile.flush()
            proc.wait(timeout=300)
        except Exception:
            pass
        finally:
            try:
                proc.terminate()
            except Exception:
                pass
        self.wfile.write(b"data: {\"done\": true}\n\n")
        self.wfile.flush()
    except Exception as exc:
        try:
            msg = json.dumps({"error": str(exc)})
            self.wfile.write(f"data: {msg}\n\n".encode("utf-8"))
            self.wfile.flush()
        except Exception:
            pass


MCCHandler._handle_mot_live_sse = _handle_mot_live_sse  # type: ignore[attr-defined]


# ── OCB-K: Project Vision endpoint ───────────────────────────────────────────

_PROJECT_VISION = {
    "aafl_engine":     {"label": "AAFL Engine",     "score": 85, "done": ["14 providers", "cheapest-first routing", "DB cache", "evaluator", "cost guard", "watchdog"], "next": ["LiteLLM router class", "more providers", "overnight autonomous runs"]},
    "mcc_cockpit":     {"label": "MCC Cockpit",     "score": 80, "done": ["19+ tabs", "108/108 MOT", "SSE live feed", "Health Suite", "LLOW canvas"], "next": ["B2 parking lot features", "Electron wrapper"]},
    "spin_doctor":     {"label": "Spin Doctor",     "score": 60, "done": ["War Thunder fix confirmed", "benchmark framework"], "next": ["Star Citizen v0.2 benchmark", "Elite Dangerous support"]},
    "scout_swarm":     {"label": "Scout Swarm",     "score": 70, "done": ["5 parallel strategies", "source reputation", "chief_scout", "AI synthesis"], "next": ["multi-browser sources", "per-strategy AI override"]},
    "safety_systems":  {"label": "Safety Systems",  "score": 75, "done": ["Safety Shield HC-01–HC-10", "CLACHR relay", "cost guard", "watchdog", "stuck inbox"], "next": ["aafl_watchdog wiring confirm", "cost_guard wiring confirm"]},
    "alp_efficiency":  {"label": "ALP Efficiency",  "score": 90, "done": ["17 ALP entries", "WCCS auto-save", "cost guard", "ALP gate in LLOW"], "next": ["Chrome extension stage 3"]},
}

_OCB_HISTORY = [
    {"label": "A", "date": "2026-05-23", "features": 5},
    {"label": "B", "date": "2026-05-24", "features": 4},
    {"label": "C", "date": "2026-05-25", "features": 6},
    {"label": "D", "date": "2026-05-25", "features": 5},
    {"label": "E", "date": "2026-05-26", "features": 6},
    {"label": "F", "date": "2026-05-27", "features": 4},
    {"label": "G", "date": "2026-05-27", "features": 5},
    {"label": "H", "date": "2026-05-28", "features": 11},
    {"label": "I", "date": "2026-05-28", "features": 10},
    {"label": "J", "date": "2026-05-28", "features": 6},
    {"label": "K", "date": "2026-05-28", "features": 8},
]

_MILESTONES_PAST = [
    "AAFL first run (Apr 2026)", "War Thunder fix confirmed", "108/108 MOT ALL CLEAR",
    "Build 1 complete (13/13 modules)", "Build 4 MCC overhaul", "Build 4b Health Suite",
    "OCB-A Self-Health", "OCB-B Body Map + Auto-Fix", "OCB-C Missions + Storage",
    "OCB-D LLOW Canvas", "OCB-E Visual overhaul", "OCB-F Arrow drag-drop",
    "OCB-G Junction Boxes + Presets", "OCB-H MCC Full Revamp", "OCB-I LLOW deep fix",
    "OCB-J HC checks + Safety Shield", "OCB-K MOT live + Project Brain",
]
_MILESTONES_FUTURE = [
    "Star Citizen benchmark v0.2", "r/LocalLLaMA post", "B2-23 Electron wrapper", "Commercial launch"
]


def _handle_project_vision(self):
    """GET /api/project-vision — returns all data for the Project Vision charts."""
    mot_report = HERE / "health_results" / "full_mot_report.json"
    mot_score = 100
    try:
        if mot_report.exists():
            d = json.loads(mot_report.read_text(encoding="utf-8"))
            mot_score = round(d.get("pass_rate", 100))
    except Exception:
        pass
    avg_radar = round(sum(v["score"] for v in _PROJECT_VISION.values()) / len(_PROJECT_VISION))
    health_score = round((mot_score + avg_radar) / 2)
    self._send_json({
        "radar": _PROJECT_VISION,
        "milestones_past": _MILESTONES_PAST,
        "milestones_future": _MILESTONES_FUTURE,
        "build_history": _OCB_HISTORY,
        "health_score": health_score,
        "mot_score": mot_score,
    })


MCCHandler._handle_project_vision = _handle_project_vision  # type: ignore[attr-defined]


# ── OCB-K: Project Awareness endpoints ───────────────────────────────────────

PROJECT_AWARENESS_FILE = HERE / "data" / "project_awareness.json"


def _build_project_awareness() -> dict:
    """Build project_awareness.json from STATUS.md content."""
    what_is_built = [
        {"name": "AAFL Engine", "desc": "14-provider AI routing loop with cost guard, evaluator, DB cache", "status": "ACTIVE"},
        {"name": "MCC Cockpit", "desc": "Mission Control Center — 19+ tabs, 108/108 MOT", "status": "ACTIVE"},
        {"name": "Spin Doctor", "desc": "Joystick mouse-spin fix for War Thunder / Elite Dangerous / Star Citizen", "status": "ACTIVE"},
        {"name": "Scout Swarm", "desc": "5-strategy parallel web researcher with AI synthesis", "status": "ACTIVE"},
        {"name": "LLOW Canvas", "desc": "Visual workflow builder — 35+ elements, 15 arrow types, junction boxes", "status": "ACTIVE"},
        {"name": "Safety Shield", "desc": "HC-01–HC-10 health checks + CLACHR relay", "status": "ACTIVE"},
        {"name": "WCCS Protocol", "desc": "Write Claude Code Save — 3-step auto-save system", "status": "ACTIVE"},
        {"name": "self_health.py", "desc": "Element registry test runner — 109 elements", "status": "ACTIVE"},
        {"name": "mcc_full_mot.py", "desc": "108-check Ministry of Transport test suite", "status": "ACTIVE"},
        {"name": "provider_health.py", "desc": "3-tier 29-test provider health system", "status": "ACTIVE"},
    ]
    what_is_next = [
        {"item": "Star Citizen full support", "status": "NOT STARTED"},
        {"item": "Add GROQ_API_KEY to .env", "status": "NOT STARTED"},
        {"item": "Add Cloudflare keys to .env", "status": "NOT STARTED"},
        {"item": "Build 2 parking lot (23 features)", "status": "NOT STARTED"},
        {"item": "5-project split after Star Citizen benchmark", "status": "NOT STARTED"},
        {"item": "aafl_watchdog.py wiring confirm", "status": "BLOCKED"},
        {"item": "LiteLLM full Router integration", "status": "NOT STARTED"},
        {"item": "Electron wrapper B2-23", "status": "NOT STARTED"},
        {"item": "Ko-fi + Itch.io monetisation setup", "status": "NOT STARTED"},
        {"item": "r/LocalLLaMA post after SC benchmark", "status": "NOT STARTED"},
    ]
    action_plan = [
        "1. Star Citizen v0.2 benchmark via AAFL autonomous run",
        "2. Add GROQ + Cloudflare keys to .env (manual — security rule)",
        "3. Polish AASKC for ship — README, demo video, r/LocalLLaMA post",
        "4. Build 2 CLAC block (23 parking lot features)",
        "5. LiteLLM full integration — replace direct provider calls",
        "6. Electron wrapper for packaging",
        "7. Ko-fi + Itch.io setup (fastest monetisation path)",
    ]
    evolution_log = [
        "Started as VKB SpinDoctor joystick fix → grew into full AAFL framework",
        "sfl_agent.py (simple loop) → aafl_core.py (14 providers, LiteLLM routing)",
        "Single Python script → MCC Mission Control Center with 19+ tabs",
        "Manual WCCS → aafl_wccs.py (automatic save on every OCB)",
        "LLOW as simple workflow idea → full visual canvas with junction boxes",
        "AASKC brand name created: Autonomous AI Simultaneous Knowledge Connection",
    ]
    forks_taken = [
        {"decision": "SFL → AAFL", "chosen": "Full AAFL framework", "alternative": "Keep sfl_agent.py simple"},
        {"decision": "SpinDoctor → benchmark", "chosen": "Use as AAFL proof of concept", "alternative": "Build standalone tool"},
        {"decision": "Raw API → LiteLLM", "chosen": "LiteLLM unified routing", "alternative": "Direct HTTP requests per provider"},
        {"decision": "B2-07 + OCB-C", "chosen": "Merged chain builder into Workflow Builder", "alternative": "Separate tab"},
    ]
    return {
        "what_is_built": what_is_built,
        "what_is_next": what_is_next,
        "action_plan": action_plan,
        "evolution_log": evolution_log,
        "forks_taken": forks_taken,
        "jobs_remaining": [x["item"] for x in what_is_next],
        "last_updated": _now_iso(),
    }


def _handle_project_awareness(self):
    """GET /api/project-awareness — returns project_awareness.json."""
    if not PROJECT_AWARENESS_FILE.exists():
        data = _build_project_awareness()
        try:
            PROJECT_AWARENESS_FILE.parent.mkdir(parents=True, exist_ok=True)
            PROJECT_AWARENESS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        self._send_json(data)
        return
    try:
        self._send_json(json.loads(PROJECT_AWARENESS_FILE.read_text(encoding="utf-8")))
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_project_awareness_update(self):
    """POST /api/project-awareness/update — rebuilds project_awareness.json from STATUS.md."""
    try:
        data = _build_project_awareness()
        PROJECT_AWARENESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROJECT_AWARENESS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        self._send_json({"ok": True, "updated_at": data["last_updated"]})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


MCCHandler._handle_project_awareness = _handle_project_awareness  # type: ignore[attr-defined]
MCCHandler._handle_project_awareness_update = _handle_project_awareness_update  # type: ignore[attr-defined]


# ── OCB-K/L: Resource Snapshot endpoint ─────────────────────────────────────

def _handle_resources_snapshot(self):
    """GET /api/resources/snapshot — full resource data incl GPU via nvidia-smi."""
    import socket as _sock
    import urllib.request as _ur
    result = {
        "cpu_percent": 0.0,
        "ram_used_gb": 0.0,
        "ram_total_gb": 0.0,
        "ram_percent": 0.0,
        "disk_c_free_gb": 0.0,
        "disk_c_percent": 0.0,
        "gpu_name": "Unknown",
        "gpu_vram_used_mb": None,
        "gpu_vram_total_mb": None,
        "gpu_utilization_percent": None,
        "lm_studio_running": False,
        "lm_studio_models_loaded": [],
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        # backwards-compat fields
        "ram_pct": 0.0,
        "cpu_pct": 0.0,
        "disk_pct": 0.0,
        "lm_studio": "UNKNOWN",
        "error": None,
    }
    try:
        import psutil as _ps
        result["cpu_percent"] = round(_ps.cpu_percent(interval=0.1), 1)
        result["cpu_pct"] = result["cpu_percent"]
        vm = _ps.virtual_memory()
        result["ram_used_gb"]  = round(vm.used  / 1024**3, 2)
        result["ram_total_gb"] = round(vm.total / 1024**3, 2)
        result["ram_percent"]  = round(vm.percent, 1)
        result["ram_pct"]      = result["ram_percent"]
        try:
            du = _ps.disk_usage("C:\\")
            result["disk_c_free_gb"] = round(du.free / 1024**3, 1)
            result["disk_c_percent"] = round(du.percent, 1)
            result["disk_pct"]       = result["disk_c_percent"]
        except Exception:
            pass
    except ImportError:
        result["error"] = "psutil not installed"
    except Exception as exc:
        result["error"] = str(exc)
    # GPU via nvidia-smi
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            parts = [p.strip() for p in out.stdout.strip().split(",")]
            if len(parts) >= 4:
                result["gpu_name"] = parts[0]
                try:
                    result["gpu_vram_used_mb"]        = int(parts[1])
                    result["gpu_vram_total_mb"]        = int(parts[2])
                    result["gpu_utilization_percent"]  = int(parts[3])
                except ValueError:
                    pass
    except Exception:
        pass
    # LM Studio
    try:
        with _sock.create_connection(("127.0.0.1", 1234), timeout=1):
            result["lm_studio_running"] = True
            result["lm_studio"] = "UP"
    except Exception:
        result["lm_studio"] = "DOWN"
    if result["lm_studio_running"]:
        try:
            req = _ur.urlopen("http://127.0.0.1:1234/v1/models", timeout=2)
            mdata = json.loads(req.read().decode())
            result["lm_studio_models_loaded"] = [m.get("id", "") for m in mdata.get("data", [])]
        except Exception:
            pass
    self._send_json(result)


MCCHandler._handle_resources_snapshot = _handle_resources_snapshot  # type: ignore[attr-defined]


# ── OCB-K: AAFL Error Log endpoint ───────────────────────────────────────────

AAFL_ERROR_DB = HERE / "data" / "aafl_error_db.json"


def _handle_aafl_errors(self):
    """GET /api/aafl/errors — returns last 20 error entries from aafl_error_db.json."""
    if not AAFL_ERROR_DB.exists():
        self._send_json({"errors": []})
        return
    try:
        data = json.loads(AAFL_ERROR_DB.read_text(encoding="utf-8"))
        if isinstance(data, list):
            self._send_json({"errors": data[-20:]})
        else:
            self._send_json({"errors": []})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_aafl_errors = _handle_aafl_errors  # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-L Phase 3 — Provider Health Enriched
# ═══════════════════════════════════════════════════════════════════════════════

def _handle_provider_health_enriched(self):
    """GET /api/provider-health — enriched provider data with location, model, VRAM."""
    import urllib.request as _ur
    import socket as _sock

    # Read last health check results
    providers_raw = []
    if LATEST_HEALTH.exists():
        try:
            raw = json.loads(LATEST_HEALTH.read_text(encoding="utf-8"))
            providers_raw = raw.get("providers", [])
        except Exception:
            pass

    # Build a quick latency map from existing results
    latency_map = {}
    status_map  = {}
    for p in providers_raw:
        pid = p.get("id") or p.get("provider_id", "")
        latency_map[pid] = p.get("latency_ms") or p.get("latency") or 0
        status_map[pid]  = p.get("status", "UNKNOWN")

    # Check LM Studio
    lm_running = False
    lm_models  = []
    try:
        with _sock.create_connection(("127.0.0.1", 1234), timeout=1):
            lm_running = True
    except Exception:
        pass
    if lm_running:
        try:
            req = _ur.urlopen("http://127.0.0.1:1234/v1/models", timeout=2)
            mdata = json.loads(req.read().decode())
            lm_models = [m.get("id", "") for m in mdata.get("data", [])]
        except Exception:
            pass

    # GPU VRAM via nvidia-smi
    gpu_vram_used_mb  = None
    gpu_vram_total_mb = None
    gpu_name          = "Unknown"
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            parts = [p.strip() for p in out.stdout.strip().split(",")]
            if len(parts) >= 3:
                gpu_name = parts[0]
                gpu_vram_used_mb  = int(parts[1])
                gpu_vram_total_mb = int(parts[2])
    except Exception:
        pass

    # Load provider table from aafl_core if available
    provider_defs = []
    try:
        import sys as _sys
        if str(HERE) not in _sys.path:
            _sys.path.insert(0, str(HERE))
        from aafl_core import PROVIDERS as _PROV
        provider_defs = _PROV
    except Exception:
        pass

    _LOCATION_MAP = {1: "LOCAL_GPU", 2: "CLOUD_FREE", 3: "CLOUD_FREE", 99: "CLOUD_PAID"}
    enriched = []
    for p in provider_defs:
        pid  = p["id"]
        tier = p.get("tier", 2)
        loc  = _LOCATION_MAP.get(tier, "CLOUD_FREE")

        # Override location for CPU-only local models (phi-4 is likely CPU if small)
        if tier == 1 and "phi" in p.get("id", "").lower():
            loc = "LOCAL_CPU"

        # Determine model name loaded (for LM Studio providers)
        model_name = p.get("model", "")
        vram_mb    = None
        if tier == 1 and lm_running and lm_models:
            # Match by partial model name
            for loaded in lm_models:
                if any(frag in loaded.lower() for frag in [
                    "coder", "vl", "deepseek", "phi", "qwen"
                ]):
                    model_name = loaded
                    break
            vram_mb = gpu_vram_used_mb  # total VRAM shared, not per-model

        # Determine status
        raw_status = status_map.get(pid, "UNKNOWN")
        if tier == 1:
            st = "LIVE" if lm_running else "OFFLINE"
        elif raw_status in ("LIVE", "PASS", "OK"):
            st = "LIVE"
        elif raw_status in ("OFFLINE", "FAIL", "ERROR"):
            st = "OFFLINE"
        else:
            # Check if API key is in env
            env_key = p.get("api_key_env")
            if env_key and not os.environ.get(env_key):
                st = "NO_KEY"
            else:
                st = "UNKNOWN"

        enriched.append({
            "id":           pid,
            "name":         p.get("label", pid),
            "status":       st,
            "latency_ms":   latency_map.get(pid, 0),
            "location":     loc,
            "model_loaded": model_name,
            "vram_mb":      vram_mb,
            "tier":         tier,
            "task_types":   p.get("task_types", []),
        })

    self._send_json({
        "providers":       enriched,
        "lm_studio_running": lm_running,
        "lm_models":       lm_models,
        "gpu_name":        gpu_name,
        "gpu_vram_used_mb":  gpu_vram_used_mb,
        "gpu_vram_total_mb": gpu_vram_total_mb,
        "generated_at":    datetime.datetime.now().isoformat(timespec="seconds"),
    })


MCCHandler._handle_provider_health_enriched = _handle_provider_health_enriched  # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-L Phase 4 — Resource Drill-Down Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

def _handle_resources_cpu_detail(self):
    """GET /api/resources/cpu-detail — per-core usage + top 10 processes."""
    try:
        import psutil as _ps
        per_core = _ps.cpu_percent(interval=0.2, percpu=True)
        freq     = _ps.cpu_freq(percpu=True)
        top10    = sorted(
            [{"pid": p.info["pid"], "name": p.info["name"],
              "cpu": round(p.info["cpu_percent"] or 0, 1)}
             for p in _ps.process_iter(["pid", "name", "cpu_percent"])
             if (p.info["cpu_percent"] or 0) > 0],
            key=lambda x: x["cpu"], reverse=True
        )[:10]
        cores = []
        for i, pct in enumerate(per_core):
            mhz = round(freq[i].current, 0) if freq and i < len(freq) else 0
            cores.append({"core": i, "pct": round(pct, 1), "mhz": mhz})
        self._send_json({"ok": True, "cores": cores, "top_processes": top10})
    except ImportError:
        self._send_json({"ok": False, "error": "psutil not installed"})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)})


def _handle_resources_ram_detail(self):
    """GET /api/resources/ram-detail — top consumers + history."""
    try:
        import psutil as _ps
        vm = _ps.virtual_memory()
        top10 = sorted(
            [{"pid": p.info["pid"], "name": p.info["name"],
              "mb": round(p.info["memory_info"].rss / 1024**2, 1) if p.info["memory_info"] else 0}
             for p in _ps.process_iter(["pid", "name", "memory_info"])
             if p.info["memory_info"]],
            key=lambda x: x["mb"], reverse=True
        )[:10]
        history = []
        mem_log = HERE / "data" / "memory_log.json"
        if mem_log.exists():
            try:
                history = json.loads(mem_log.read_text(encoding="utf-8"))[-60:]
            except Exception:
                pass
        self._send_json({
            "ok": True,
            "used_gb":  round(vm.used / 1024**3, 2),
            "avail_gb": round(vm.available / 1024**3, 2),
            "total_gb": round(vm.total / 1024**3, 2),
            "percent":  vm.percent,
            "top_processes": top10,
            "history":  history,
        })
    except ImportError:
        self._send_json({"ok": False, "error": "psutil not installed"})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)})


def _handle_resources_disk_detail(self):
    """GET /api/resources/disk-detail — C: and D: usage + largest project folders."""
    drives = {}
    for drv in ("C:\\", "D:\\"):
        try:
            import psutil as _ps
            du = _ps.disk_usage(drv)
            drives[drv] = {
                "free_gb":  round(du.free / 1024**3, 1),
                "used_gb":  round(du.used / 1024**3, 1),
                "total_gb": round(du.total / 1024**3, 1),
                "percent":  round(du.percent, 1),
            }
        except Exception as exc:
            drives[drv] = {"error": str(exc)}

    # Top 5 folders in project root by size
    folders = []
    try:
        for entry in sorted(HERE.iterdir(), key=lambda p: p.stat().st_size if p.is_file() else sum(
            f.stat().st_size for f in p.rglob("*") if f.is_file()
        ), reverse=True)[:8]:
            if entry.name.startswith(".") or entry.name in ("backups", "archive_dead"):
                continue
            if entry.is_dir():
                try:
                    sz = sum(f.stat().st_size for f in entry.rglob("*") if f.is_file())
                    folders.append({"name": entry.name, "size_mb": round(sz / 1024**2, 1)})
                except Exception:
                    pass
            if len(folders) >= 5:
                break
    except Exception:
        pass

    # aafl_output stats
    aafl_out = HERE / "aafl_output"
    aafl_count = 0
    aafl_mb    = 0.0
    if aafl_out.exists():
        try:
            files = list(aafl_out.rglob("*"))
            aafl_count = len([f for f in files if f.is_file()])
            aafl_mb    = round(sum(f.stat().st_size for f in files if f.is_file()) / 1024**2, 1)
        except Exception:
            pass

    self._send_json({
        "ok": True,
        "drives": drives,
        "top_folders": folders,
        "aafl_output": {"file_count": aafl_count, "total_mb": aafl_mb},
    })


def _handle_resources_gpu_detail(self):
    """GET /api/resources/gpu-detail — nvidia-smi full output parsed."""
    result = {"ok": True, "gpu_name": "Unknown", "driver": "", "vram_used_mb": None,
              "vram_total_mb": None, "utilization": None, "temperature": None,
              "processes": [], "error": None}
    try:
        out = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=name,driver_version,memory.used,memory.total,utilization.gpu,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            parts = [p.strip() for p in out.stdout.strip().split(",")]
            if len(parts) >= 6:
                result["gpu_name"]     = parts[0]
                result["driver"]       = parts[1]
                result["vram_used_mb"] = int(parts[2]) if parts[2].isdigit() else None
                result["vram_total_mb"]= int(parts[3]) if parts[3].isdigit() else None
                result["utilization"]  = int(parts[4]) if parts[4].isdigit() else None
                result["temperature"]  = int(parts[5]) if parts[5].isdigit() else None
        else:
            result["ok"]    = False
            result["error"] = "nvidia-smi returned no data — GPU may be offline"
    except FileNotFoundError:
        result["ok"]    = False
        result["error"] = "nvidia-smi not found — no NVIDIA GPU or driver not installed"
    except Exception as exc:
        result["ok"]    = False
        result["error"] = str(exc)

    # Per-process VRAM
    try:
        out2 = subprocess.run(
            ["nvidia-smi", "--query-compute-apps=pid,name,used_memory",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        for line in out2.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                result["processes"].append({"pid": parts[0], "name": parts[1], "vram_mb": parts[2]})
    except Exception:
        pass
    self._send_json(result)


def _handle_resources_lmstudio_detail(self):
    """GET /api/resources/lmstudio-detail — loaded models, VRAM, call stats."""
    import urllib.request as _ur
    import socket as _sock
    result = {"ok": True, "running": False, "models": [], "total_vram_used_mb": None,
              "gpu_vram_total_mb": None, "error": None}
    # Check if running
    try:
        with _sock.create_connection(("127.0.0.1", 1234), timeout=1):
            result["running"] = True
    except Exception:
        result["ok"]    = False
        result["error"] = "LM Studio offline"
        self._send_json(result)
        return
    # Loaded models
    try:
        req = _ur.urlopen("http://127.0.0.1:1234/v1/models", timeout=3)
        mdata = json.loads(req.read().decode())
        result["models"] = [{"id": m.get("id", ""), "owned_by": m.get("owned_by", "")}
                            for m in mdata.get("data", [])]
    except Exception as exc:
        result["error"] = f"Could not fetch /v1/models: {exc}"
    # GPU VRAM total
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip().isdigit():
            result["gpu_vram_total_mb"] = int(out.stdout.strip())
    except Exception:
        pass
    # Try LM Studio stats endpoint
    try:
        req2 = _ur.urlopen("http://127.0.0.1:1234/v1/system/stats", timeout=2)
        stats = json.loads(req2.read().decode())
        result["total_vram_used_mb"] = stats.get("vram_used_mb") or stats.get("gpu_memory_used_mb")
    except Exception:
        pass
    self._send_json(result)


MCCHandler._handle_resources_cpu_detail      = _handle_resources_cpu_detail      # type: ignore[attr-defined]
MCCHandler._handle_resources_ram_detail      = _handle_resources_ram_detail      # type: ignore[attr-defined]
MCCHandler._handle_resources_disk_detail     = _handle_resources_disk_detail     # type: ignore[attr-defined]
MCCHandler._handle_resources_gpu_detail      = _handle_resources_gpu_detail      # type: ignore[attr-defined]
MCCHandler._handle_resources_lmstudio_detail = _handle_resources_lmstudio_detail # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-L Phase 5 — Help Tab (Ask + History)
# ═══════════════════════════════════════════════════════════════════════════════

HELP_HISTORY_FILE = HERE / "data" / "help_history.json"
HELP_SYSTEM_PROMPT = (
    "You are a helpful assistant for the VKB Spin Doctor / AAFL / AASKC project. "
    "The project is a self-improving AI agent framework (AAFL) built by a beginner coder "
    "using free local and online AI providers. The Mission Control Center (MCC) is the UI. "
    "LLOW is the visual workflow canvas. Scout Swarm does web research. WCCS saves sessions. "
    "Answer questions about how to use MCC, what components do, how AAFL works, "
    "debugging help, and project status. Be concise and friendly."
)

_HELP_PROVIDER_ORDER = [
    "lmstudio_coder", "mistral_code", "gemini_flash", "cerebras", "openrouter"
]


def _help_try_providers(query: str, provider_prefs: list) -> tuple[str, str]:
    """Try providers in order, return (response_text, provider_label). Fallback to error."""
    try:
        import sys as _sys
        if str(HERE) not in _sys.path:
            _sys.path.insert(0, str(HERE))
        from aafl_core import AAFLCore, PROVIDERS as _PROV
    except Exception as exc:
        return f"[Error loading AAFL core: {exc}]", "error"

    pmap = {p["id"]: p for p in _PROV}
    order = provider_prefs if provider_prefs else _HELP_PROVIDER_ORDER

    for pid in order:
        p = pmap.get(pid)
        if not p:
            continue
        # Skip if needs key and key missing
        env_key = p.get("api_key_env")
        if env_key and not os.environ.get(env_key):
            continue
        try:
            import litellm
            msgs = [
                {"role": "system", "content": HELP_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ]
            kwargs = {"model": p["model"], "messages": msgs, "max_tokens": 800, "timeout": 30}
            if p.get("api_base"):
                kwargs["api_base"] = p["api_base"]
            if p.get("api_key"):
                kwargs["api_key"] = p["api_key"]
            resp = litellm.completion(**kwargs)
            text = resp.choices[0].message.content or ""
            if text.strip():
                return text.strip(), p.get("label", pid)
        except Exception:
            continue
    return "No AI provider responded. Check your .env keys and that LM Studio is running.", "none"


def _handle_help_ask(self):
    """POST /api/help/ask — tries providers in order, streams response as SSE."""
    try:
        body = json.loads(self._read_body() or "{}")
    except Exception:
        self._send_json({"error": "Invalid JSON"}, 400)
        return
    query    = body.get("query", "").strip()
    prefs    = body.get("provider_preference", [])
    if not query:
        self._send_json({"error": "query required"}, 400)
        return

    response_text, provider_label = _help_try_providers(query, prefs)

    # Save to history
    try:
        HELP_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        hist = []
        if HELP_HISTORY_FILE.exists():
            try:
                hist = json.loads(HELP_HISTORY_FILE.read_text(encoding="utf-8"))
            except Exception:
                hist = []
        hist.append({
            "ts":       datetime.datetime.now().isoformat(timespec="seconds"),
            "query":    query,
            "response": response_text,
            "provider": provider_label,
        })
        if len(hist) > 100:
            hist = hist[-100:]
        HELP_HISTORY_FILE.write_text(json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    # Send as SSE — write word by word with small delay, then close
    words = response_text.split(" ")
    try:
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        import time as _time
        for word in words:
            chunk = json.dumps({"word": word + " ", "provider": provider_label})
            self.wfile.write(f"data: {chunk}\n\n".encode("utf-8"))
            self.wfile.flush()
            _time.sleep(0.02)
        # Send done event
        self.wfile.write(b"data: {\"done\": true}\n\n")
        self.wfile.flush()
    except Exception:
        pass


def _handle_help_history(self):
    """GET /api/help/history — returns last 10 Q&A entries."""
    if not HELP_HISTORY_FILE.exists():
        self._send_json({"history": []})
        return
    try:
        hist = json.loads(HELP_HISTORY_FILE.read_text(encoding="utf-8"))
        self._send_json({"history": hist[-10:]})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_help_ask     = _handle_help_ask     # type: ignore[attr-defined]
MCCHandler._handle_help_history = _handle_help_history # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-L Phase 6 — Settings Persistence
# ═══════════════════════════════════════════════════════════════════════════════

MCC_SETTINGS_FILE = HERE / "data" / "mcc_settings.json"

_MCC_SETTINGS_DEFAULT = {
    "theme": "dark",
    "tab_order": [],
    "section_order_per_tab": {},
    "open_sections": {},
    "provider_preference_order": ["lmstudio_coder", "mistral_code", "gemini_flash",
                                  "cerebras", "openrouter"],
    "design_density": "comfortable",
    "animation_speed": 1,
    "tab_bar_style": "default",
    "sidebar_accent": "#0d0d0d",
    "tabbar_accent": "#4af",
    "btn_style": "filled",
    "font": "monospace",
    "font_size": "13",
    "text_color": "#cccccc",
    "bg_color": "#0d0d0d",
    "border_radius": "4",
    "last_active_tab": "home",
}


def _load_mcc_settings() -> dict:
    if not MCC_SETTINGS_FILE.exists():
        return dict(_MCC_SETTINGS_DEFAULT)
    try:
        data = json.loads(MCC_SETTINGS_FILE.read_text(encoding="utf-8"))
        merged = dict(_MCC_SETTINGS_DEFAULT)
        merged.update(data)
        return merged
    except Exception:
        return dict(_MCC_SETTINGS_DEFAULT)


def _save_mcc_settings(data: dict) -> None:
    MCC_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = MCC_SETTINGS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(MCC_SETTINGS_FILE)


def _handle_settings_get(self):
    """GET /api/settings — returns mcc_settings.json."""
    self._send_json(_load_mcc_settings())


def _handle_settings_post(self):
    """POST /api/settings — saves mcc_settings.json (atomic write)."""
    try:
        body = json.loads(self._read_body() or "{}")
    except Exception:
        self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
        return
    current = _load_mcc_settings()
    current.update(body)
    try:
        _save_mcc_settings(current)
        self._send_json({"ok": True, "saved_at": datetime.datetime.now().isoformat(timespec="seconds")})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


MCCHandler._handle_settings_get  = _handle_settings_get  # type: ignore[attr-defined]
MCCHandler._handle_settings_post = _handle_settings_post # type: ignore[attr-defined]


# ── OCB-N: Scout Swarm LLOW LEL handlers ─────────────────────────────────────

def _run_swarm_bg(session_id: str, params: str, time_limit: str):
    global _swarm_sessions
    timeout_map = {"5min": 300, "15min": 900, "30min": 1800, "1hr": 3600, "indefinite": None}
    timeout_secs = timeout_map.get(time_limit)
    SCOUT_OUTPUT.mkdir(exist_ok=True)
    out_file = SCOUT_OUTPUT / f"swarm_{session_id}.txt"
    try:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"[SWARM] session={session_id}\n[PARAMS] {params}\n[STARTED] {_now_iso()}\n")
        cmd = [PYTHON, str(HERE / "chief_scout.py"), params]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, cwd=str(HERE))
        with _swarm_lock:
            _swarm_sessions[session_id]["proc"] = proc
            _swarm_sessions[session_id]["status"] = "running"
        lines = []
        with open(out_file, "a", encoding="utf-8") as f:
            if timeout_secs:
                import signal as _sig
                deadline = datetime.datetime.now().timestamp() + timeout_secs
            for line in proc.stdout:
                lines.append(line)
                f.write(line)
                f.flush()
                with _swarm_lock:
                    _swarm_sessions[session_id]["results_count"] = len(lines)
                if timeout_secs and datetime.datetime.now().timestamp() > deadline:
                    proc.terminate()
                    break
        proc.wait()
        with _swarm_lock:
            _swarm_sessions[session_id]["status"] = "complete"
            _swarm_sessions[session_id]["results_count"] = len(lines)
    except Exception as exc:
        with _swarm_lock:
            _swarm_sessions[session_id]["status"] = "error"
            _swarm_sessions[session_id]["error"] = str(exc)


def _handle_scout_swarm_get(self):
    """GET /api/llow/scout-swarm?session_id=X — poll swarm session status."""
    try:
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        sid = params.get("session_id", "").strip()
        if not sid:
            with _swarm_lock:
                self._send_json({"sessions": list(_swarm_sessions.values())})
            return
        with _swarm_lock:
            s = _swarm_sessions.get(sid)
        if not s:
            self._send_json({"error": "session not found"}, 404)
            return
        out_file = SCOUT_OUTPUT / f"swarm_{sid}.txt"
        output = ""
        if out_file.exists():
            try:
                output = out_file.read_text(encoding="utf-8", errors="replace")[-2000:]
            except Exception:
                pass
        self._send_json({
            "session_id": sid,
            "status": s.get("status", "idle"),
            "results_count": s.get("results_count", 0),
            "params": s.get("params", ""),
            "time_limit": s.get("time_limit", ""),
            "started": s.get("started", ""),
            "output": output,
        })
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_scout_swarm_post(self):
    """POST /api/llow/scout-swarm — launch a new swarm session."""
    try:
        body = json.loads(self._read_body() or "{}")
        params = body.get("parameters", "").strip()
        time_limit = body.get("time_limit", "15min")
        if not params:
            self._send_json({"error": "parameters required"}, 400)
            return
        import uuid as _uuid
        sid = _uuid.uuid4().hex[:12]
        with _swarm_lock:
            _swarm_sessions[sid] = {
                "session_id": sid, "status": "starting",
                "results_count": 0, "params": params,
                "time_limit": time_limit, "started": _now_iso(), "proc": None,
            }
        t = threading.Thread(target=_run_swarm_bg, args=(sid, params, time_limit), daemon=True)
        t.start()
        self._send_json({"ok": True, "session_id": sid, "status": "starting"})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


MCCHandler._handle_scout_swarm_get  = _handle_scout_swarm_get   # type: ignore[attr-defined]
MCCHandler._handle_scout_swarm_post = _handle_scout_swarm_post  # type: ignore[attr-defined]


# ── OCB-N: Project Timeline endpoint ─────────────────────────────────────────

def _handle_api_timeline_data(self):
    """GET /api/timeline-data — return data/project_timeline.json, rebuild if stale."""
    try:
        rebuild = not TIMELINE_FILE.exists()
        if not rebuild and TIMELINE_FILE.exists():
            age = (datetime.datetime.now() - datetime.datetime.fromtimestamp(
                TIMELINE_FILE.stat().st_mtime)).total_seconds()
            rebuild = age > 3600  # rebuild if >1h old
        if rebuild:
            try:
                sys.path.insert(0, str(HERE))
                import importlib
                tl_mod = importlib.import_module("project_timeline_builder")
                tl_mod.build()
            except Exception:
                pass
        if TIMELINE_FILE.exists():
            data = json.loads(TIMELINE_FILE.read_text(encoding="utf-8"))
            self._send_json(data)
        else:
            self._send_json({"error": "Timeline not yet built", "ocb_nodes": [], "milestones": [], "recent_commits": []})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_api_timeline_data = _handle_api_timeline_data  # type: ignore[attr-defined]


# ── OCB-N: Work Checker new panel handlers ────────────────────────────────────

def _handle_wc_timeline(self):
    """GET /api/work-checker/timeline — return timeline panel data."""
    try:
        from work_checker import WorkChecker
        wc = WorkChecker()
        self._send_json(wc.build_timeline_panel())
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_wc_checklist(self):
    """GET /api/work-checker/checklist — return PENDING items as checkboxes."""
    try:
        from work_checker import WorkChecker
        wc = WorkChecker()
        self._send_json({"items": wc.build_checklist()})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_wc_action_plan(self):
    """GET /api/work-checker/action-plan — return top 5 next priorities."""
    try:
        from work_checker import WorkChecker
        wc = WorkChecker()
        self._send_json({"priorities": wc.build_action_plan()})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


def _handle_wc_check_item(self):
    """POST /api/work-checker/check-item — mark item done/undone in STATUS.md."""
    try:
        body = json.loads(self._read_body() or "{}")
        item_id = body.get("item_id", "").strip()
        done = bool(body.get("done", True))
        if not item_id:
            self._send_json({"ok": False, "error": "item_id required"}, 400)
            return
        from work_checker import WorkChecker
        wc = WorkChecker()
        ok = wc.mark_item_done(item_id, done)
        self._send_json({"ok": ok})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


def _handle_wc_delegate(self):
    """POST /api/work-checker/delegate — send priority to stuck inbox as a task."""
    try:
        body = json.loads(self._read_body() or "{}")
        priority = body.get("priority", "").strip()
        if not priority:
            self._send_json({"ok": False, "error": "priority required"}, 400)
            return
        inbox = []
        if STUCK_INBOX_FILE.exists():
            try:
                inbox = json.loads(STUCK_INBOX_FILE.read_text(encoding="utf-8"))
                if not isinstance(inbox, list):
                    inbox = []
            except Exception:
                inbox = []
        import uuid as _uuid2
        inbox.append({
            "item_id": _uuid2.uuid4().hex[:8],
            "content": priority,
            "severity": "medium",
            "source": "action_plan",
            "status": "open",
            "created_at": _now_iso(),
        })
        STUCK_INBOX_FILE.write_text(json.dumps(inbox, indent=2, ensure_ascii=False), encoding="utf-8")
        self._send_json({"ok": True, "delegated": priority})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


MCCHandler._handle_wc_timeline    = _handle_wc_timeline     # type: ignore[attr-defined]
MCCHandler._handle_wc_checklist   = _handle_wc_checklist    # type: ignore[attr-defined]
MCCHandler._handle_wc_action_plan = _handle_wc_action_plan  # type: ignore[attr-defined]
MCCHandler._handle_wc_check_item  = _handle_wc_check_item   # type: ignore[attr-defined]
MCCHandler._handle_wc_delegate    = _handle_wc_delegate     # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-O: Code Editor API endpoints
# ═══════════════════════════════════════════════════════════════════════════════

import tempfile as _tempfile_mod

_CE_SKIP = {"__pycache__", "backups", "archive_dead", ".git", "node_modules", ".claude"}


def _handle_code_files(self):
    """GET /api/code/files?path=X — directory listing as JSON tree."""
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
    rel = qs.get("path", [""])[0].strip().lstrip("/\\")
    target = (HERE / rel).resolve() if rel else HERE.resolve()
    if not str(target).startswith(str(HERE.resolve())):
        self._send_json({"error": "Access denied"}, 403)
        return
    if not target.exists():
        self._send_json({"error": "Not found"}, 404)
        return

    def _entry(p):
        try:
            st = p.stat()
            return {
                "name": p.name,
                "path": str(p.relative_to(HERE)).replace("\\", "/"),
                "type": "dir" if p.is_dir() else "file",
                "size": st.st_size if p.is_file() else None,
                "mtime": int(st.st_mtime),
                "ext":  p.suffix.lstrip(".").lower() if p.is_file() else None,
            }
        except Exception:
            return {"name": p.name, "type": "file",
                    "path": str(p.relative_to(HERE)).replace("\\", "/")}

    if target.is_file():
        self._send_json(_entry(target))
        return

    entries = []
    try:
        for child in sorted(target.iterdir(),
                            key=lambda p: (0 if p.is_dir() else 1, p.name.lower())):
            if child.name.startswith(".") or child.name in _CE_SKIP:
                continue
            e = _entry(child)
            if child.is_dir():
                e["children"] = []
            entries.append(e)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)
        return
    self._send_json({
        "path": str(target.relative_to(HERE)).replace("\\", "/") if target != HERE else "",
        "entries": entries,
    })


MCCHandler._handle_code_files = _handle_code_files  # type: ignore[attr-defined]


def _handle_code_read(self):
    """GET /api/code/read?file=X — reads file content (max 2 MB)."""
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
    rel = qs.get("file", [""])[0].strip().lstrip("/\\")
    if not rel:
        self._send_json({"error": "No file specified"}, 400)
        return
    target = (HERE / rel).resolve()
    if not str(target).startswith(str(HERE.resolve())):
        self._send_json({"error": "Access denied"}, 403)
        return
    if not target.is_file():
        self._send_json({"error": "File not found"}, 404)
        return
    size = target.stat().st_size
    if size > 2 * 1024 * 1024:
        self._send_json({"error": f"File too large ({size//1024}KB) to open in editor", "size": size}, 400)
        return
    try:
        content = target.read_text(encoding="utf-8", errors="replace")
        self._send_json({"file": rel, "content": content, "size": size,
                         "ext": target.suffix.lstrip(".").lower()})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_code_read = _handle_code_read  # type: ignore[attr-defined]


def _handle_code_save(self):
    """POST /api/code/save — atomic file write. Body: {file, content}."""
    try:
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        rel = (body.get("file") or "").strip().lstrip("/\\")
        content = body.get("content", "")
        if not rel:
            self._send_json({"error": "No file specified"}, 400)
            return
        target = (HERE / rel).resolve()
        if not str(target).startswith(str(HERE.resolve())):
            self._send_json({"error": "Access denied"}, 403)
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = _tempfile_mod.mkstemp(dir=str(target.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                f.write(content)
            import shutil as _sh
            _sh.move(tmp_path, str(target))
        except Exception:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            raise
        self._send_json({"ok": True, "file": rel, "size": len(content.encode("utf-8"))})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_code_save = _handle_code_save  # type: ignore[attr-defined]


def _handle_code_run(self):
    """POST /api/code/run — runs a .py file, returns stdout/stderr."""
    try:
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        rel = (body.get("file") or "").strip().lstrip("/\\")
        if not rel:
            self._send_json({"error": "No file specified"}, 400)
            return
        target = (HERE / rel).resolve()
        if not str(target).startswith(str(HERE.resolve())):
            self._send_json({"error": "Access denied"}, 403)
            return
        if not target.is_file():
            self._send_json({"error": "File not found"}, 404)
            return
        if target.suffix.lower() != ".py":
            self._send_json({"error": "Only .py files can be run here"}, 400)
            return
        result = subprocess.run(
            [PYTHON, str(target)],
            capture_output=True, text=True, timeout=30, cwd=str(HERE),
        )
        self._send_json({
            "ok":         result.returncode == 0,
            "returncode": result.returncode,
            "stdout":     result.stdout[-8000:]   if result.stdout else "",
            "stderr":     result.stderr[-4000:]   if result.stderr else "",
        })
    except subprocess.TimeoutExpired:
        self._send_json({"ok": False, "error": "Script timed out after 30s",
                         "stdout": "", "stderr": ""})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_code_run = _handle_code_run  # type: ignore[attr-defined]


# ── OCB-O: OCB Runner endpoints ────────────────────────────────────────────────

def _handle_ocb_parse(self):
    """POST /api/ocb/parse — parse OCB block, return phase list."""
    try:
        body = json.loads(self._read_body() or "{}")
        ocb_text = (body.get("ocb_text") or "").strip()
        if not ocb_text:
            self._send_json({"error": "ocb_text is required"}, 400)
            return
        from ocb_runner import parse_ocb_block
        phases = parse_ocb_block(ocb_text)
        self._send_json({"phases": phases, "phase_count": len(phases)})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_ocb_parse = _handle_ocb_parse  # type: ignore[attr-defined]


def _handle_ocb_run(self):
    """POST /api/ocb/run — launch OCB run in background thread. Supports failed_phases_only flag."""
    try:
        body                = json.loads(self._read_body() or "{}")
        provider            = (body.get("provider") or "auto").strip()
        max_retries         = int(body.get("max_retries", 3))
        acceptance_criteria = body.get("acceptance_criteria", [])
        failed_phases_only  = bool(body.get("failed_phases_only", False))
        original_run_id     = (body.get("run_id") or "").strip()
        if not isinstance(acceptance_criteria, list):
            acceptance_criteria = []

        if failed_phases_only and original_run_id:
            # Rebuild OCB text from failed phases only
            import ocb_runner as _ocbr
            ocb_text = ""
            try:
                if CLACHR_RESPONSE.exists():
                    cr = json.loads(CLACHR_RESPONSE.read_text(encoding="utf-8"))
                    orig_text = cr.get("ocb_text", "")
                    failed_names = set(cr.get("phases_failed", []))
                    if orig_text and failed_names:
                        all_phases = _ocbr.parse_ocb_block(orig_text)
                        filtered = [p for p in all_phases if p["phase_name"] in failed_names]
                        if filtered:
                            lines = []
                            for p in filtered:
                                lines.append(f"═══ PHASE {p['phase_num']} — {p['phase_name']} ═══")
                                lines.append("")
                                for t in p["tasks"]:
                                    lines.append(f"{t['num']}. {t['text']}")
                                lines.append("")
                            ocb_text = "\n".join(lines)
                if not ocb_text:
                    ocb_text = (body.get("ocb_text") or "").strip()
            except Exception:
                ocb_text = (body.get("ocb_text") or "").strip()
        else:
            ocb_text = (body.get("ocb_text") or "").strip()

        if not ocb_text:
            self._send_json({"error": "ocb_text is required"}, 400)
            return

        run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        import ocb_runner
        t = threading.Thread(
            target=ocb_runner.run_all,
            args=(ocb_text, run_id),
            kwargs={"max_retries": max_retries, "provider": provider,
                    "acceptance_criteria": acceptance_criteria},
            daemon=True,
        )
        t.start()
        self._send_json({"run_id": run_id, "status": "started"})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_ocb_run = _handle_ocb_run  # type: ignore[attr-defined]


def _handle_ocb_status(self, run_id: str):
    """GET /api/ocb/status/<run_id> — return current run status from ocb_status.json."""
    try:
        if not OCB_STATUS_FILE.exists():
            self._send_json({"status": "idle", "run_id": "", "phases": [], "log": []})
            return
        data = json.loads(OCB_STATUS_FILE.read_text(encoding="utf-8"))
        # If run_id is given and doesn't match, still return (client may poll stale id)
        self._send_json(data)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_ocb_status = _handle_ocb_status  # type: ignore[attr-defined]


def _handle_ocb_cancel(self, run_id: str):
    """POST /api/ocb/cancel/<run_id> — set cancelled flag in ocb_status.json."""
    try:
        if OCB_STATUS_FILE.exists():
            data = json.loads(OCB_STATUS_FILE.read_text(encoding="utf-8"))
            data["cancelled"] = True
            data["status"]    = "CANCELLED"
            import tempfile as _tf
            fd, tmp = _tf.mkstemp(dir=str(OCB_STATUS_FILE.parent), suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            import shutil as _sh
            _sh.move(tmp, str(OCB_STATUS_FILE))
        self._send_json({"cancelled": True, "run_id": run_id})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_ocb_cancel = _handle_ocb_cancel  # type: ignore[attr-defined]


def _handle_ocb_archive(self, run_id: str):
    """POST /api/ocb/archive/<run_id> — copy ocb_status.json to archive_dead/."""
    try:
        if not OCB_STATUS_FILE.exists():
            self._send_json({"ok": False, "error": "No status file to archive"}, 404)
            return
        ARCHIVE_DIR.mkdir(exist_ok=True)
        dest = ARCHIVE_DIR / f"ocb_run_{run_id}.json"
        import shutil as _sh
        _sh.copy2(str(OCB_STATUS_FILE), str(dest))
        self._send_json({"ok": True, "archived_to": str(dest)})
    except Exception as exc:
        self._send_json({"ok": False, "error": str(exc)}, 500)


MCCHandler._handle_ocb_archive = _handle_ocb_archive  # type: ignore[attr-defined]


def _handle_rrclach_save(self):
    """POST /api/rrclach/save — write rrclach_request.json with ocb_text + acceptance_criteria + classification."""
    try:
        body                = json.loads(self._read_body() or "{}")
        ocb_text            = (body.get("ocb_text") or "").strip()
        acceptance_criteria = body.get("acceptance_criteria", [])
        if not isinstance(acceptance_criteria, list):
            acceptance_criteria = []
        if not ocb_text:
            self._send_json({"error": "ocb_text is required"}, 400)
            return
        # Classify the OCB block
        classification = {}
        try:
            import sys as _sys
            if str(HERE) not in _sys.path:
                _sys.path.insert(0, str(HERE))
            from clacker_router import classify as _classify
            classification = _classify(ocb_text)
        except Exception:
            pass
        payload = {
            "ocb_text":            ocb_text,
            "acceptance_criteria": acceptance_criteria,
            "saved_at":            datetime.datetime.now().isoformat(timespec="seconds"),
            "classification":      classification,
        }
        rrclach_file = HERE / "data" / "rrclach_request.json"
        import shutil as _sh
        import tempfile as _tf
        fd, tmp = _tf.mkstemp(dir=str(rrclach_file.parent), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        _sh.move(tmp, str(rrclach_file))
        self._send_json({"ok": True, "saved_to": "data/rrclach_request.json",
                         "criteria_count": len(acceptance_criteria),
                         "classification": classification})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_rrclach_save = _handle_rrclach_save  # type: ignore[attr-defined]


# ── MCCM / Chief Detective endpoints ─────────────────────────────────────────

MCCM_PERMS_FILE = HERE / "data" / "mccm_permissions.json"


def _handle_mccm_status(self):
    """GET /api/mccm/status — run mccm_agent.py --overview and return JSON."""
    try:
        proc = subprocess.run(
            [FULL_PYTHON, str(HERE / "mccm_agent.py"), "--overview"],
            capture_output=True, text=True, timeout=30, cwd=str(HERE),
        )
        power = 1
        try:
            if MCCM_PERMS_FILE.exists():
                data = json.loads(MCCM_PERMS_FILE.read_text(encoding="utf-8"))
                power = data.get("mccm_power_level", 1)
        except Exception:
            pass
        self._send_json({"status": proc.stdout, "power_level": power})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_mccm_status = _handle_mccm_status  # type: ignore[attr-defined]


def _handle_mccm_detective(self):
    """GET /api/mccm/detective — return latest detective_report_{date}.json."""
    try:
        data_dir = HERE / "data"
        reports  = sorted(data_dir.glob("detective_report_*.json"), reverse=True)
        if not reports:
            self._send_json({"error": "No detective report found. Run wccs_detective.py --investigate first."}, 404)
            return
        report = json.loads(reports[0].read_text(encoding="utf-8"))
        self._send_json(report)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_mccm_detective = _handle_mccm_detective  # type: ignore[attr-defined]


def _handle_mccm_alerts(self):
    """GET /api/mccm/alerts — return pending Scott interrupts."""
    try:
        if not MCCM_PERMS_FILE.exists():
            self._send_json([])
            return
        data = json.loads(MCCM_PERMS_FILE.read_text(encoding="utf-8"))
        pending = [i for i in data.get("scott_interrupts", []) if i.get("status") == "PENDING_SCOTT"]
        self._send_json(pending)
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_mccm_alerts = _handle_mccm_alerts  # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-P: Unified Session State
# ═══════════════════════════════════════════════════════════════════════════════

def _session_state_read() -> dict:
    """Read session_state.json or return defaults."""
    try:
        if SESSION_STATE_FILE.exists():
            return json.loads(SESSION_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return dict(_SS_DEFAULTS)


def _session_state_write(state: dict):
    """Atomic write of session_state.json."""
    import tempfile as _tf
    import shutil as _sh
    SESSION_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = _tf.mkstemp(dir=str(SESSION_STATE_FILE.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    _sh.move(tmp, str(SESSION_STATE_FILE))


def _handle_session_state_get(self):
    """GET /api/session-state — returns session_state.json (never 404)."""
    self._send_json(_session_state_read())


MCCHandler._handle_session_state_get = _handle_session_state_get  # type: ignore[attr-defined]


def _handle_session_state_post(self):
    """POST /api/session-state — merges partial update (dict.update), atomic write."""
    try:
        patch = json.loads(self._read_body() or "{}")
        state = _session_state_read()
        state.update(patch)
        _session_state_write(state)
        self._send_json({"ok": True})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_session_state_post = _handle_session_state_post  # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-P: Provider Health Diagnosis
# ═══════════════════════════════════════════════════════════════════════════════

def _handle_provider_health_diagnose(self):
    """POST /api/provider-health/diagnose — live-test all providers, write provider_diagnosis.json."""
    try:
        import sys as _sys
        if str(HERE) not in _sys.path:
            _sys.path.insert(0, str(HERE))
        import provider_health as _ph
        result = _ph.run_diagnosis()
        self._send_json({
            "healthy": result["healthy"],
            "total": result["total"],
            "failures": result["failures"],
        })
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_provider_health_diagnose = _handle_provider_health_diagnose  # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-P: Command Bar
# ═══════════════════════════════════════════════════════════════════════════════

_HINT_MAP = {
    "CODE":        "Go to WCCS tab → OCB Runner to execute",
    "RESEARCH":    "Go to Scout tab to run web research",
    "AAFL":        "Go to AAFL Runs tab → set goal and run",
    "MAINTENANCE": "Go to WCCS tab → click Save WCCS",
    "OPUS":        "Paste into Claude Chat for big-brain analysis",
}

def _handle_command_bar(self):
    """POST /api/command-bar — classify instructions, update session_state current_task."""
    try:
        body = json.loads(self._read_body() or "{}")
        instructions = (body.get("instructions") or "").strip()
        if not instructions:
            self._send_json({"error": "instructions required"}, 400)
            return
        import sys as _sys
        if str(HERE) not in _sys.path:
            _sys.path.insert(0, str(HERE))
        from clacker_router import classify as _classify
        cls = _classify(instructions)
        task_type = cls.get("type", "OPUS")
        hint = _HINT_MAP.get(task_type, "")
        now = datetime.datetime.now().isoformat(timespec="seconds")
        state = _session_state_read()
        state["current_task"] = {
            "type": task_type,
            "description": instructions[:120],
            "subsystem": cls.get("subsystem", ""),
            "status": "routed",
            "started_at": now,
        }
        _session_state_write(state)
        self._send_json({
            "classification": task_type,
            "subsystem": cls.get("subsystem", ""),
            "provider": cls.get("provider", ""),
            "confidence": cls.get("confidence", 0.5),
            "hint": hint,
        })
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_command_bar = _handle_command_bar  # type: ignore[attr-defined]


# ═══════════════════════════════════════════════════════════════════════════════
# OCB-P: Watchdog Start
# ═══════════════════════════════════════════════════════════════════════════════

def _handle_watchdog_start(self):
    """POST /api/watchdog/start — launch aafl_watchdog.py as a background process."""
    try:
        watchdog_script = HERE / "aafl_watchdog.py"
        if not watchdog_script.exists():
            self._send_json({"ok": False, "error": "aafl_watchdog.py not found"})
            return
        import subprocess as _sp
        _sp.Popen([FULL_PYTHON, str(watchdog_script)],
                  cwd=str(HERE), creationflags=0x00000008)  # DETACHED_PROCESS on Windows
        state = _session_state_read()
        state["watchdog_status"] = "ON"
        _session_state_write(state)
        self._send_json({"ok": True, "status": "started"})
    except Exception as exc:
        self._send_json({"error": str(exc)}, 500)


MCCHandler._handle_watchdog_start = _handle_watchdog_start  # type: ignore[attr-defined]


def main():
    threading.Thread(target=_qa_startup_test, daemon=True).start()
    server = ThreadingServer((HOST, PORT), MCCHandler)
    print(f"[MCC] MCC Server running at http://{HOST}:{PORT}", flush=True)
    print(f"[MCC] Project folder: {HERE}", flush=True)
    print(f"[MCC] chat_latest.txt: {CHAT}", flush=True)
    print(f"[MCC] Ctrl+C to stop", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[MCC] Stopped.")


if __name__ == "__main__":
    main()
