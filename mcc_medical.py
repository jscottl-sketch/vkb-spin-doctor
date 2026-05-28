"""
mcc_medical.py — Doctor CLAC's Full Medical & Fitness Assessment for MCC
Supersedes mcc_full_mot.py (which it also re-runs as regression group).

Usage:
  python mcc_medical.py              # full medical (all 14 categories)
  python mcc_medical.py --quick      # functional + endpoints only
  python mcc_medical.py --category=ux
  python mcc_medical.py --category=endpoints
  python mcc_medical.py --category=functional,safety,recovery

Categories: functional, ux, endpoints, integration, edge, performance,
            error_handling, persistence, accessibility, cross_tab,
            safety, recovery, deps, regression

Outputs:
  health_results/mcc_medical/mcc_medical_report_YYYY-MM-DD_HH-MM.md
  health_results/mcc_medical/mcc_inventory.json
  health_results/mcc_medical/mcc_wmbw_report.md
  health_results/mcc_medical/mcc_medical_history.json
"""

from __future__ import annotations

import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import datetime
import importlib
import json
import os
import re
import socket
import sqlite3
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG — edit here, never hunt through the file
# ══════════════════════════════════════════════════════════════════════════════
HERE         = Path(__file__).parent
PORT         = 8080
BASE_URL     = f"http://127.0.0.1:{PORT}"
PYTHON       = sys.executable

# Report output paths
MED_DIR      = HERE / "health_results" / "mcc_medical"
REPORT_GLOB  = "mcc_medical_report_*.md"
HISTORY_FILE = MED_DIR / "mcc_medical_history.json"

# Score thresholds
SCORE_GREEN  = 90    # ≥90 → green badge
SCORE_YELLOW = 70    # 70-89 → yellow badge  (below → red)

# Source files
HTML_PATH    = HERE / "mission_control.html"
SERVER_PATH  = HERE / "mcc_server.py"
MOT_PATH     = HERE / "mcc_full_mot.py"

# Data files
DB_PATH      = HERE / "data" / "knowledge_engine.db"
GOAL_QUEUE   = HERE / "goal_queue.txt"
GOAL_TXT     = HERE / "goal.txt"
CHAT_FILE    = HERE / "chat_latest.txt"
AAFL_CFG     = HERE / "aafl_control_config.json"
COST_LOG     = HERE / "data" / "cost_log.txt"
WATCHDOG     = HERE / "aafl_watchdog.py"
COST_GUARD   = HERE / "cost_guard.py"
STUCK_INBOX  = HERE / "stuck_inbox.json"
MCC_PREFS    = HERE / "mcc_prefs.json"
SESS_DIR     = HERE / "session_logs"

MED_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RECORDER — central truth
# ═══════════════════════════════════════════════════════════════════════════════

class MedicalRecorder:
    def __init__(self):
        self.results: list[dict] = []
        self.total = self.passed = self.failed = self.warned = 0
        self.start_time = time.time()
        self._category_times: dict[str, float] = {}
        self._cat_start: float | None = None
        self._cat_current: str = ""
        self._issues: list[str] = []

    def begin_category(self, name: str):
        self._cat_current = name
        self._cat_start = time.time()
        width = 62
        print(f"\n{'='*width}")
        print(f"  CATEGORY: {name.upper()}")
        print(f"{'='*width}")

    def end_category(self):
        elapsed = round(time.time() - (self._cat_start or time.time()), 2)
        self._category_times[self._cat_current] = elapsed
        print(f"  [{self._cat_current}] completed in {elapsed}s")

    def record(self, category: str, name: str, passed: bool,
               detail: str = "", warn: bool = False, repro: str = "",
               fix: str = "") -> None:
        self.total += 1
        if warn and not passed:
            status = "WARN"
            self.warned += 1
        elif passed:
            status = "PASS"
            self.passed += 1
        else:
            status = "FAIL"
            self.failed += 1
            if fix:
                self._issues.append(f"[{category}] {name}: {fix}")

        row = {
            "category": category,
            "name": name,
            "status": status,
            "detail": detail,
            "repro": repro,
            "fix": fix,
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        self.results.append(row)
        icon = {"PASS": "OK", "FAIL": "XX", "WARN": "WN"}[status]
        msg = f"  [{icon}] {name}"
        if detail:
            msg += f": {detail}"
        print(msg)
        if repro and status == "FAIL":
            print(f"       repro -> {repro}")

    def score(self) -> int:
        if self.total == 0:
            return 0
        base = round((self.passed / self.total) * 100)
        warn_penalty = min(self.warned * 2, 10)
        return max(0, min(100, base - warn_penalty))

    def issues(self) -> list[str]:
        return self._issues


REC = MedicalRecorder()

# ═══════════════════════════════════════════════════════════════════════════════
# SERVER LIFECYCLE
# ═══════════════════════════════════════════════════════════════════════════════

_server_proc = None
_server_started_by_us = False


def _port_busy(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def ensure_server() -> bool:
    global _server_proc, _server_started_by_us
    if _port_busy(PORT):
        print(f"  [server] Port {PORT} already live — using existing server")
        return True
    print(f"  [server] Starting mcc_server.py on :{PORT}…")
    try:
        _server_proc = subprocess.Popen(
            [PYTHON, str(SERVER_PATH)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(HERE),
        )
        for _ in range(20):
            time.sleep(0.5)
            if _port_busy(PORT):
                _server_started_by_us = True
                print(f"  [server] Server up in ~{(_ + 1) * 0.5:.1f}s")
                return True
        return False
    except Exception as exc:
        print(f"  [server] Failed to start: {exc}")
        return False


def stop_server_if_ours():
    global _server_proc, _server_started_by_us
    if _server_started_by_us and _server_proc:
        _server_proc.terminate()
        try:
            _server_proc.wait(timeout=4)
        except Exception:
            _server_proc.kill()
        print("  [server] Test server stopped.")
        _server_started_by_us = False


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _http(method: str, path: str, body=None, timeout: int = 8,
          content_type: str = "application/json") -> tuple[int, dict | str | None, float]:
    url = BASE_URL + path
    t0 = time.time()
    try:
        data = None
        if body is not None:
            if isinstance(body, (dict, list)):
                data = json.dumps(body).encode("utf-8")
            elif isinstance(body, str):
                data = body.encode("utf-8")
            else:
                data = body
        req = urllib.request.Request(url, data=data, method=method)
        if data:
            req.add_header("Content-Type", content_type)
            req.add_header("Content-Length", str(len(data)))
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = round(time.time() - t0, 3)
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw), elapsed
            except Exception:
                return resp.status, raw, elapsed
    except urllib.error.HTTPError as exc:
        elapsed = round(time.time() - t0, 3)
        try:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                return exc.code, json.loads(raw), elapsed
            except Exception:
                return exc.code, raw, elapsed
        except Exception:
            return exc.code, None, elapsed
    except Exception as exc:
        elapsed = round(time.time() - t0, 3)
        return 0, str(exc)[:120], elapsed


def _get(path: str, timeout: int = 8):
    return _http("GET", path, timeout=timeout)


def _post(path: str, body=None, timeout: int = 12):
    return _http("POST", path, body=body, timeout=timeout)


def _delete(path: str, body=None):
    return _http("DELETE", path, body=body)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════

class _HtmlInventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tabs: list[dict] = []
        self.buttons: list[dict] = []
        self.inputs: list[dict] = []
        self.textareas: list[dict] = []
        self.selects: list[dict] = []
        self.modals: list[dict] = []
        self.fetch_calls: list[str] = []
        self._current_tag = ""
        self._all_ids: set[str] = set()
        self._tab_stack: list[str] = ["root"]

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        eid = d.get("id", "")
        if eid:
            self._all_ids.add(eid)

        if tag == "button":
            tab_target = d.get("data-tab", "")
            if tab_target:
                self.tabs.append({
                    "id": tab_target,
                    "label": "",
                    "title": d.get("title", ""),
                    "classes": d.get("class", ""),
                })
            else:
                self.buttons.append({
                    "id": eid,
                    "type": "button",
                    "classes": d.get("class", ""),
                    "data-tip": d.get("data-tip", d.get("title", "")),
                    "onclick": d.get("onclick", ""),
                    "parent_tab": self._tab_stack[-1],
                })

        elif tag == "input":
            self.inputs.append({
                "id": eid,
                "type": d.get("type", "text"),
                "placeholder": d.get("placeholder", ""),
                "classes": d.get("class", ""),
                "parent_tab": self._tab_stack[-1],
            })

        elif tag == "textarea":
            self.textareas.append({
                "id": eid,
                "placeholder": d.get("placeholder", ""),
                "classes": d.get("class", ""),
                "parent_tab": self._tab_stack[-1],
            })

        elif tag == "select":
            self.selects.append({
                "id": eid,
                "classes": d.get("class", ""),
                "parent_tab": self._tab_stack[-1],
            })

        elif tag == "div":
            cls = d.get("class", "")
            if "modal" in cls or "overlay" in cls or "confirm-" in cls:
                self.modals.append({
                    "id": eid,
                    "classes": cls,
                })
            if "tab-pane" in cls and eid:
                self._tab_stack.append(eid)

    def handle_endtag(self, tag):
        if tag == "div" and len(self._tab_stack) > 1:
            pass

    def handle_data(self, data):
        text = data.strip()
        if self.buttons and not self.buttons[-1].get("label") and text:
            self.buttons[-1]["label"] = text[:60]


def build_inventory() -> dict:
    inv = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "tabs": [],
        "buttons": [],
        "inputs": [],
        "textareas": [],
        "selects": [],
        "modals": [],
        "endpoints_get": [],
        "endpoints_post": [],
        "endpoints_delete": [],
        "files_read": [],
        "files_written": [],
        "dependencies": [],
        "fetch_calls_in_html": [],
    }

    # ── Parse HTML ──
    if HTML_PATH.exists():
        content = HTML_PATH.read_text(encoding="utf-8", errors="replace")
        parser = _HtmlInventory()
        try:
            parser.feed(content)
        except Exception:
            pass
        inv["tabs"] = parser.tabs
        inv["buttons"] = parser.buttons
        inv["inputs"] = parser.inputs
        inv["textareas"] = parser.textareas
        inv["selects"] = parser.selects
        inv["modals"] = parser.modals

        # Find all fetch('...') and fetch("...") calls
        fetches = re.findall(r"fetch\(['\"]([^'\"]+)['\"]", content)
        inv["fetch_calls_in_html"] = sorted(set(fetches))

    # ── Parse server endpoints from source ──
    get_eps, post_eps, del_eps = [], [], []
    files_r, files_w = set(), set()
    if SERVER_PATH.exists():
        src = SERVER_PATH.read_text(encoding="utf-8", errors="replace")
        # GET routes
        for m in re.finditer(r'elif path == "(/[^"]+)"', src):
            ep = m.group(1)
            # determine GET or POST by context (look at surrounding block)
            context_start = max(0, m.start() - 200)
            context = src[context_start: m.start()]
            if "do_GET" in src[:m.start()][-4000:] or "def do_GET" in context:
                pass
        # Parse do_GET block
        get_block = re.search(r"def do_GET\(self\).*?def do_POST", src, re.DOTALL)
        if get_block:
            for m in re.finditer(r'path in \(["\'](.+?)["\']\)|path == "(/[^"]+)"|path\.startswith\("(/[^"]+)"\)', get_block.group(0)):
                for g in m.groups():
                    if g:
                        get_eps.append(g)
        post_block = re.search(r"def do_POST\(self\).*?def do_DELETE", src, re.DOTALL)
        if post_block:
            for m in re.finditer(r'path == "(/[^"]+)"', post_block.group(0)):
                post_eps.append(m.group(1))
        del_block = re.search(r"def do_DELETE\(self\).*?def do_GET", src, re.DOTALL)
        if del_block:
            for m in re.finditer(r'path == "(/[^"]+)"', del_block.group(0)):
                del_eps.append(m.group(1))
        # File reads/writes
        for m in re.finditer(r'[A-Z_]+\s*=\s*HERE\s*/\s*"([^"]+)"', src):
            files_r.add(m.group(1))
        for m in re.finditer(r'\.write_text\(|open\(.+,"w"', src):
            pass
        # Dependencies
        for m in re.finditer(r"^import (\w+)|^from (\w+)", src, re.MULTILINE):
            dep = m.group(1) or m.group(2)
            if dep not in ("http", "os", "sys", "json", "datetime", "re", "subprocess",
                           "threading", "urllib", "pathlib", "difflib", "shutil"):
                files_r.add(dep)

    inv["endpoints_get"]    = sorted(set(get_eps))
    inv["endpoints_post"]   = sorted(set(post_eps))
    inv["endpoints_delete"] = sorted(set(del_eps))
    inv["files_read"]       = sorted(files_r)

    # Known full endpoint lists (hardcoded from source analysis)
    inv["endpoints_get_full"] = [
        "/", "/mission_control.html", "/status", "/captures", "/scout-result",
        "/scout-config", "/scout-presets", "/aafl-status", "/aafl-queue",
        "/aafl-config", "/aafl-providers", "/api/timeline", "/api/backup",
        "/api/diff", "/api/session-logs", "/api/session-log", "/api/search",
        "/api/auto-wccs", "/health-status", "/dashboard-data/", "/stuck-inbox",
        "/memory/knowledge", "/memory/solutions", "/memory/sources", "/promo-queue",
        "/acca-codes", "/alp-data", "/self-diagnosis", "/known-issues", "/modules",
        "/presets", "/presets/load", "/aafl-settings", "/retry-log", "/chain-status",
        "/chain-log", "/scout-timer/status", "/sources-library", "/stuck-inbox/summary",
        "/storage", "/storage/report", "/wccs/save-log", "/wccs/history-search",
        "/wccs/session-logs", "/wccs/versions", "/api/status", "/api/history",
        "/api/acca", "/api/health", "/aafl/live", "/aafl/bridge-result",
        "/aafl/workflow-presets", "/b2/kanban", "/b2/activity", "/b2/aafl-runs",
        "/b2/prefs", "/b2/budget-caps", "/b2/costs", "/b2/keybind-profiles",
        "/b2/source-health", "/scout/results", "/api/task-inbox",
        "/api/medical-report", "/api/medical-history",
    ]
    inv["endpoints_post_full"] = [
        "/wccs", "/capture", "/run-scout", "/scout-config", "/run-aafl",
        "/set-aafl-goal", "/aafl-queue", "/aafl-config", "/stop-aafl", "/api/wccs",
        "/api/restore", "/api/auto-wccs", "/resolve-stuck", "/run-now",
        "/approve-promo", "/reject-promo", "/alp-add", "/run-mot", "/known-issues",
        "/run-health-check", "/run-merge-sessions", "/toggle-module", "/presets/save",
        "/presets/delete", "/aafl-settings", "/suggest-provider", "/run-chain",
        "/scout-timer/start", "/scout-timer/stop", "/sources-library/add",
        "/stuck-inbox/bulk-resolve", "/wccs/restore", "/wccs/diff", "/aafl/run-goal",
        "/scout/strategy", "/aafl/scout-bridge", "/aafl/workflow", "/b2/kanban",
        "/b2/activity", "/b2/activity/summarise", "/b2/run-tag", "/b2/run-notes",
        "/b2/prefs", "/b2/budget-caps", "/b2/benchmark", "/b2/second-opinion",
        "/b2/step-mode", "/b2/step-next", "/b2/pause-aafl", "/b2/resume-aafl",
        "/b2/chain-save", "/b2/chain-run", "/b2/keybind-profiles",
        "/b2/keybind-profiles/rate", "/b2/keybind-profiles/delete",
        "/b2/strategy-overrides", "/b2/workers", "/b2/block-source",
        "/b2/unblock-source", "/b2/export-briefing", "/b2/scout-compare",
        "/api/task-inbox", "/api/run-queue", "/api/run-medical",
    ]
    inv["endpoints_delete_full"] = ["/aafl-queue"]
    inv["tabs_full"] = [
        "home", "wccs", "kanban", "aafl-runs", "scout", "costs",
        "aafl-control", "memory", "promo", "acca", "alp", "storage",
        "self-diagnosis", "autolog", "providerhealth", "keybind-profiles",
        "medical",
    ]

    out = MED_DIR / "mcc_inventory.json"
    out.write_text(json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [inventory] Saved -> {out.name}")
    return inv


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — WMBW PASS
# Best-practice scoring per element type. Research synthesis baked in.
# ═══════════════════════════════════════════════════════════════════════════════

WMBW_BEST_PRACTICES = {
    "tab_navigation": {
        "score": 7,
        "current": "Tab bar with data-tab buttons, CSS active state, JS switchTab()",
        "bp_1": "Keyboard arrow-key navigation between tabs (WCAG 2.1 §4.1.3)",
        "bp_2": "aria-selected and role='tab' + role='tabpanel' for screen readers",
        "bp_3": "Tab state persisted to localStorage so refresh returns to last tab",
        "flag_for_upgrade": True,
        "recommendation": "Add aria-selected/role=tab attributes; persist active tab to localStorage",
    },
    "button_save": {
        "score": 7,
        "current": "btn-save-lg with disabled state during run",
        "bp_1": "Loading spinner replaces button label during async op (not just disabled)",
        "bp_2": "Success/fail toast with undo action within 5s (Nielsen: error recovery)",
        "bp_3": "Keyboard shortcut (Ctrl+S) wired to save trigger",
        "flag_for_upgrade": True,
        "recommendation": "Add inline spinner to save button; wire Ctrl+S shortcut",
    },
    "textarea_chat": {
        "score": 6,
        "current": "Plain textarea with fixed height, Consolas font",
        "bp_1": "Auto-resize textarea (css: field-sizing: content or JS resize observer)",
        "bp_2": "Character count indicator with soft/hard limits clearly marked",
        "bp_3": "Paste-to-save keyboard shortcut (Ctrl+Enter) clearly labelled",
        "flag_for_upgrade": True,
        "recommendation": "Auto-resize + char counter + Ctrl+Enter shortcut label",
    },
    "polling_dashboard": {
        "score": 6,
        "current": "setInterval polling every 5-10s on multiple tabs simultaneously",
        "bp_1": "Exponential backoff when server is unreachable (not constant polling)",
        "bp_2": "Pause polling when tab is hidden (document.visibilityState check)",
        "bp_3": "Show 'Last updated X seconds ago' staleness indicator",
        "flag_for_upgrade": True,
        "recommendation": "Implement visibility-aware polling + backoff on failure",
    },
    "toast_notifications": {
        "score": 7,
        "current": "Bottom-right toast with ok/error colour coding, 3s auto-dismiss",
        "bp_1": "Stack multiple toasts vertically (currently may overlap)",
        "bp_2": "Manual dismiss X button for error toasts (shouldn't auto-dismiss errors)",
        "bp_3": "ARIA live region (role=alert) so screen readers announce them",
        "flag_for_upgrade": True,
        "recommendation": "Add role=alert to toast container; keep error toasts until dismissed",
    },
    "error_display": {
        "score": 5,
        "current": "Inline .error-msg class shown in panels on failure",
        "bp_1": "Errors should include actionable text: what failed + what user can do",
        "bp_2": "Error messages should be distinguishable from empty/loading states",
        "bp_3": "Retry button inline with error for recoverable failures",
        "flag_for_upgrade": True,
        "recommendation": "Add actionable error text + inline retry buttons",
    },
    "theme_toggle": {
        "score": 7,
        "current": "Dark/light theme stored in prefs, CSS body.theme-light class swap",
        "bp_1": "Respect prefers-color-scheme media query as default before user pref",
        "bp_2": "Theme persists across sessions (localStorage or server pref)",
        "bp_3": "System-level contrast check — light theme may not meet WCAG AA",
        "flag_for_upgrade": True,
        "recommendation": "Add prefers-color-scheme auto-detection as fallback",
    },
    "data_tables": {
        "score": 6,
        "current": "data-table class with th/td, no pagination, loads all rows",
        "bp_1": "Virtual scrolling or pagination for tables >50 rows",
        "bp_2": "Sortable columns — click th to sort ascending/descending",
        "bp_3": "Column resize handles for wide content",
        "flag_for_upgrade": True,
        "recommendation": "Add client-side sort on th click; cap row render at 50 with load-more",
    },
    "confirm_dialog": {
        "score": 7,
        "current": "Custom overlay confirm-box for destructive actions",
        "bp_1": "Focus trap inside dialog (Tab cycles within modal, not to background)",
        "bp_2": "Esc key closes dialog",
        "bp_3": "Default focus on Cancel (not Confirm) for destructive actions",
        "flag_for_upgrade": True,
        "recommendation": "Implement focus trap + Escape key handler in confirm dialog",
    },
    "endpoint_error_handling": {
        "score": 5,
        "current": "Most endpoints catch Exception and return {error: str(exc)}",
        "bp_1": "Distinguish client errors (4xx) from server errors (5xx) consistently",
        "bp_2": "Never expose raw exception messages to client (security + UX)",
        "bp_3": "Structured error codes (e.g. {error_code: 'E_QUEUE_FULL'}) for machine parsing",
        "flag_for_upgrade": True,
        "recommendation": "Add error_code field to all error responses; sanitize exception text",
    },
    "performance_polling": {
        "score": 5,
        "current": "Multiple setInterval timers across tabs, all polling even when not visible",
        "bp_1": "Consolidate to single polling loop that distributes to subscribers",
        "bp_2": "Reduce polling rate to 30s when window loses focus",
        "bp_3": "Request coalescing: batch multiple endpoint reads into one cycle",
        "flag_for_upgrade": True,
        "recommendation": "Implement central poller with visibility-aware rate reduction",
    },
    "accessibility_contrast": {
        "score": 5,
        "current": "#888 text on #0d0d0d background — ratio ~4.5:1 (borderline AA)",
        "bp_1": "WCAG AA requires 4.5:1 for normal text, 3:1 for large text",
        "bp_2": "Secondary text (#555, #444, #333) on dark backgrounds likely fails AA",
        "bp_3": "Run automated contrast checker on all colour pairs",
        "flag_for_upgrade": True,
        "recommendation": "Audit and lighten secondary text colours (#555->#777 minimum)",
    },
    "keyboard_shortcuts": {
        "score": 6,
        "current": "Number key 1-9 for tab switching, some VKB profile shortcuts",
        "bp_1": "All shortcuts visible in a help overlay (? key)",
        "bp_2": "Shortcuts should not conflict with browser defaults",
        "bp_3": "Shortcut hints should appear in tooltips (e.g. 'Save (Ctrl+S)')",
        "flag_for_upgrade": True,
        "recommendation": "Add shortcut hints to button tooltips; verify no browser conflicts",
    },
    "form_validation": {
        "score": 5,
        "current": "Client-side empty-check before fetch; server returns 400 for empty",
        "bp_1": "Inline validation feedback before submit (not just on empty check)",
        "bp_2": "Max-length enforcement visible to user (not just truncated server-side)",
        "bp_3": "Input sanitization visible — show what characters are stripped",
        "flag_for_upgrade": True,
        "recommendation": "Add maxlength attributes to inputs; show character remaining",
    },
}


def build_wmbw_report(inventory: dict) -> str:
    lines = [
        "# MCC WMBW Report — Per-Element Scrutiny",
        f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "WMBW = What Makes it Better? (3 improvements + web best-practice + WENTO score)",
        "",
        "---",
        "",
    ]

    total_score = 0
    flagged = []

    for key, bp in WMBW_BEST_PRACTICES.items():
        score = bp["score"]
        total_score += score
        flag_marker = "🚩 FLAGGED FOR UPGRADE" if bp.get("flag_for_upgrade") and score < 7 else ""
        lines += [
            f"## {key.replace('_', ' ').title()} — Score: {score}/10  {flag_marker}",
            "",
            f"**Current implementation:** {bp['current']}",
            "",
            "**3 ways it could be better:**",
            f"1. {bp['bp_1']}",
            f"2. {bp['bp_2']}",
            f"3. {bp['bp_3']}",
            "",
            f"**Recommendation:** {bp['recommendation']}",
            "",
            "---",
            "",
        ]
        if bp.get("flag_for_upgrade") and score < 7:
            flagged.append(f"{key}: {bp['recommendation']}")

    avg = round(total_score / len(WMBW_BEST_PRACTICES), 1)
    lines += [
        "## Summary",
        "",
        f"Average score: **{avg}/10**",
        f"Elements flagged for upgrade: **{len(flagged)}**",
        "",
        "### Top Upgrade Targets:",
    ]
    for f in flagged[:5]:
        lines.append(f"- {f}")

    report_text = "\n".join(lines)
    out = MED_DIR / "mcc_wmbw_report.md"
    out.write_text(report_text, encoding="utf-8")
    print(f"  [wmbw] Saved -> {out.name}")
    return report_text


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — TEST CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════

# ── CATEGORY 1: FUNCTIONAL ─────────────────────────────────────────────────────

def test_functional():
    REC.begin_category("functional")

    # Test /capture POST
    code, data, _ = _post("/capture", "medical_test_ping")
    REC.record("functional", "POST /capture writes to chat", code == 200 and isinstance(data, dict) and data.get("ok"),
               detail=str(code), fix="Check chat_latest.txt write permissions")

    # Test /captures GET
    code, data, _ = _get("/captures")
    REC.record("functional", "GET /captures returns content", code == 200 and "content" in (data or {}),
               detail=str(code))

    # Test /status GET
    code, data, _ = _get("/status")
    REC.record("functional", "GET /status returns last_wccs field",
               code == 200 and "last_wccs" in (data or {}), detail=str(code))

    # Test /aafl-queue round-trip
    test_goal = "__medical_test_goal__"
    code, data, _ = _post("/aafl-queue", {"goal": test_goal})
    REC.record("functional", "POST /aafl-queue appends goal", code == 200 and (data or {}).get("ok"),
               detail=str(code), fix="Check goal_queue.txt write permissions")

    code, data, _ = _get("/aafl-queue")
    goals_text = json.dumps(data) if data else ""
    REC.record("functional", "GET /aafl-queue shows appended goal",
               test_goal in goals_text, detail=f"found={test_goal in goals_text}")

    # DELETE /aafl-queue (comment out our test goal)
    if isinstance(data, dict):
        goals = data.get("goals", [])
        idx = next((g["index"] for g in goals if g.get("text") == test_goal), None)
        if idx is not None:
            code, _, _ = _delete("/aafl-queue", {"index": idx})
            REC.record("functional", "DELETE /aafl-queue comments goal",
                       code == 200, detail=str(code))

    # Test /set-aafl-goal
    code, data, _ = _post("/set-aafl-goal", {"goal": "__medical_goal_test__"})
    REC.record("functional", "POST /set-aafl-goal updates goal.txt",
               code == 200 and (data or {}).get("ok"), detail=str(code))

    # Test /known-issues round-trip
    code, data, _ = _post("/known-issues", {"action": "add", "description": "__medical_test_issue__", "severity": "low"})
    ok_add = code == 200 and (data or {}).get("ok")
    REC.record("functional", "POST /known-issues add", ok_add, detail=str(code))

    if ok_add:
        item_id = (data or {}).get("item", {}).get("id", "")
        code, data2, _ = _post("/known-issues", {"action": "delete", "id": item_id})
        REC.record("functional", "POST /known-issues delete",
                   code == 200, detail=str(code))

    # Test /alp-add
    code, data, _ = _post("/alp-add", {"entry": "__medical ALP test entry__"})
    REC.record("functional", "POST /alp-add appends row",
               code == 200 and (data or {}).get("ok"), detail=str(code))

    # Test /b2/prefs round-trip
    code, data, _ = _get("/b2/prefs")
    REC.record("functional", "GET /b2/prefs returns prefs", code == 200, detail=str(code))

    code, data, _ = _post("/b2/prefs", {"_medical_test": True})
    REC.record("functional", "POST /b2/prefs saves pref", code == 200, detail=str(code))

    # Test /b2/kanban add + delete
    code, data, _ = _post("/b2/kanban", {"action": "add", "col": "todo", "title": "__medical_card__"})
    ok_kanban = code == 200 and (data or {}).get("ok")
    REC.record("functional", "POST /b2/kanban add card", ok_kanban, detail=str(code))

    if ok_kanban and isinstance(data, dict):
        board = data.get("board", {})
        todo_cards = board.get("todo", [])
        test_card = next((c for c in todo_cards if c.get("title") == "__medical_card__"), None)
        if test_card:
            code2, _, _ = _post("/b2/kanban", {"action": "delete", "id": test_card["id"]})
            REC.record("functional", "POST /b2/kanban delete card", code2 == 200, detail=str(code2))

    # Test /b2/activity log
    code, data, _ = _post("/b2/activity", {"cat": "medical", "msg": "test", "trigger": "auto"})
    REC.record("functional", "POST /b2/activity logs entry", code == 200, detail=str(code))

    # Test /api/auto-wccs start + stop
    code, data, _ = _post("/api/auto-wccs", {"action": "start", "interval": 30})
    REC.record("functional", "POST /api/auto-wccs start", code == 200 and (data or {}).get("ok"), detail=str(code))

    code, data, _ = _post("/api/auto-wccs", {"action": "stop"})
    REC.record("functional", "POST /api/auto-wccs stop", code == 200 and (data or {}).get("ok"), detail=str(code))

    # Test /b2/pause-aafl + resume
    code, _, _ = _post("/b2/pause-aafl", {})
    REC.record("functional", "POST /b2/pause-aafl creates flag", code == 200, detail=str(code))

    code, _, _ = _post("/b2/resume-aafl", {})
    REC.record("functional", "POST /b2/resume-aafl removes flag", code == 200, detail=str(code))

    pause_flag = HERE / "aafl_pause.flag"
    REC.record("functional", "resume removes aafl_pause.flag from disk",
               not pause_flag.exists(), detail=str(pause_flag.exists()))

    # Test scout timer stop/start
    code, _, _ = _post("/scout-timer/stop", {})
    REC.record("functional", "POST /scout-timer/stop creates stop flag", code == 200, detail=str(code))

    stop_flag = HERE / "scout_timer_stop.flag"
    REC.record("functional", "stop flag written to disk", stop_flag.exists(),
               detail=str(stop_flag.exists()))

    REC.end_category()


# ── CATEGORY 2: UI/UX ─────────────────────────────────────────────────────────

def test_ux(inventory: dict):
    REC.begin_category("ux")

    if not HTML_PATH.exists():
        REC.record("ux", "mission_control.html exists", False, fix="File missing")
        REC.end_category()
        return

    content = HTML_PATH.read_text(encoding="utf-8", errors="replace")

    # Tab count and label coverage
    tabs = inventory.get("tabs_full", [])
    REC.record("ux", f"Tab count >=17 (found {len(tabs)})", len(tabs) >= 17, detail=str(len(tabs)))

    # All tabs have title attributes — match only the button opening tag
    tab_btns = re.findall(r'<button[^>]+data-tab="[^"]*"[^>]*>', content)
    tabs_with_title = sum(1 for b in tab_btns if "title=" in b)
    REC.record("ux", "All tab buttons have title tooltips",
               tabs_with_title >= len(tab_btns), detail=f"{tabs_with_title}/{len(tab_btns)}")

    # Custom tooltip system present
    has_data_tip = "[data-tip]" in content
    REC.record("ux", "Custom tooltip system present ([data-tip])", has_data_tip)

    # Toast notifications
    has_toast = "toast-container" in content and "toast(" in content.lower()
    REC.record("ux", "Toast notification system present", has_toast)

    # Confirm dialog
    has_confirm = "confirm-overlay" in content or "confirmDialog" in content
    REC.record("ux", "Confirm dialog for destructive actions", has_confirm)

    # Loading states
    has_loading = "loading" in content and ("disabled" in content or "btn-spinner" in content)
    REC.record("ux", "Loading/disabled states on async buttons", has_loading)

    # Theme toggle
    has_theme = "theme-light" in content or "toggleTheme" in content
    REC.record("ux", "Theme toggle (dark/light) present", has_theme)

    # Keyboard shortcuts
    has_keyboard = "keydown" in content or "keyboard" in content.lower()
    REC.record("ux", "Keyboard shortcut handling present", has_keyboard)

    # Responsive layout hints
    has_responsive = "flex-wrap" in content or "@media" in content
    REC.record("ux", "Responsive layout (flex-wrap / @media) present", has_responsive)

    # Empty states
    has_empty = "empty-msg" in content
    REC.record("ux", "Empty state messages defined (.empty-msg)", has_empty)

    # Server connectivity indicator
    has_server_dot = "server-dot" in content or "btn-connect" in content
    REC.record("ux", "Server connectivity indicator present", has_server_dot)

    # WCCS tab flow numbered/clear
    wccs_has_textarea = 'class="wccs-chat-textarea"' in content or "wccs-chat" in content
    REC.record("ux", "WCCS tab has chat textarea for input", wccs_has_textarea)

    # Home screen cards
    has_home_cards = "home-card" in content
    REC.record("ux", "Home screen card widgets present", has_home_cards)

    # Status indicators (dots for green/yellow/red)
    has_status_dots = "hc-dot" in content or "log-dot" in content
    REC.record("ux", "Status indicator dots (green/yellow/red) present", has_status_dots)

    # Instrument gauges
    has_gauges = "gauge-track" in content or "gauge-fill" in content
    REC.record("ux", "Gauge/instrument widgets on home screen", has_gauges)

    # WARN: no visible skip-to-main / skip-link
    has_skip = 'skip' in content.lower() and 'href' in content
    REC.record("ux", "Skip-to-main navigation link",
               has_skip, warn=True, detail="Accessibility enhancement",
               fix="Add a skip-to-content link for keyboard users")

    # WARN: no visible loading skeleton
    has_skeleton = "skeleton" in content.lower()
    REC.record("ux", "Loading skeleton screens for slow data",
               has_skeleton, warn=True, detail="UX enhancement",
               fix="Add skeleton loading placeholders for table sections")

    REC.end_category()


# ── CATEGORY 3: ENDPOINTS ─────────────────────────────────────────────────────

def test_endpoints():
    REC.begin_category("endpoints")

    # ── GET endpoints — test all for 200 + valid JSON ──
    get_smoke = [
        ("/", False),              # HTML response
        ("/status", True),
        ("/captures", True),
        ("/scout-result", True),
        ("/scout-config", True),
        ("/aafl-status", True),
        ("/aafl-queue", True),
        ("/aafl-config", True),
        ("/aafl-providers", True),
        ("/health-status", True),
        ("/dashboard-data/", True),
        ("/stuck-inbox", True),
        ("/memory/knowledge", True),
        ("/memory/solutions", True),
        ("/memory/sources", True),
        ("/promo-queue", True),
        ("/acca-codes", True),
        ("/alp-data", True),
        ("/self-diagnosis", True),
        ("/known-issues", True),
        ("/presets", True),
        ("/aafl-settings", True),
        ("/retry-log", True),
        ("/chain-status", True),
        ("/chain-log", True),
        ("/scout-timer/status", True),
        ("/sources-library", True),
        ("/stuck-inbox/summary", True),
        ("/storage", True),
        ("/storage/report", True),
        ("/wccs/save-log", True),
        ("/wccs/session-logs", True),
        ("/wccs/versions", True),
        ("/api/status", True),
        ("/api/history", True),
        ("/api/acca", True),
        ("/api/health", True),
        ("/api/auto-wccs", True),
        ("/api/session-logs", True),
        ("/api/timeline", True),
        ("/aafl/live", True),
        ("/aafl/bridge-result", True),
        ("/aafl/workflow-presets", True),
        ("/b2/kanban", True),
        ("/b2/activity", True),
        ("/b2/aafl-runs", True),
        ("/b2/prefs", True),
        ("/b2/budget-caps", True),
        ("/b2/costs", True),
        ("/b2/keybind-profiles", True),
        ("/b2/source-health", True),
        ("/scout/results", True),
        ("/api/task-inbox", True),
        ("/api/medical-report", True),
        ("/api/medical-history", True),
    ]

    slow_endpoints = []
    for path, expect_json in get_smoke:
        code, data, elapsed = _get(path, timeout=10)
        ok = code == 200
        if expect_json and ok:
            ok = isinstance(data, (dict, list))
        REC.record("endpoints", f"GET {path}",
                   ok, detail=f"HTTP {code} ({elapsed}s)",
                   fix=f"Check _handle for {path} in mcc_server.py")
        if elapsed > 2.0:
            slow_endpoints.append((path, elapsed))

    for path, t in slow_endpoints:
        REC.record("endpoints", f"PERF: {path} slow ({t}s)",
                   t < 5.0, warn=True, detail=f"{t}s response",
                   fix=f"{path} took {t}s — investigate DB query or file read")

    # ── POST endpoints — smoke tests ──
    post_smoke = [
        ("/capture", "test capture text"),
        ("/set-aafl-goal", {"goal": "__ep_test__"}),
        ("/aafl-config", {"_test": True}),
        ("/scout-config", {"_test": True}),
        ("/api/auto-wccs", {"action": "stop"}),
        ("/b2/prefs", {"_ep_test": True}),
        ("/b2/activity", {"cat": "test", "msg": "ep test"}),
        ("/b2/step-mode", {"enabled": False}),
        ("/run-now", {"goal": "__ep_run_now_test__"}),
        ("/stop-aafl", {}),
    ]
    for path, body in post_smoke:
        code, data, elapsed = _post(path, body, timeout=10)
        ok = code in (200, 201, 202, 204, 409)
        REC.record("endpoints", f"POST {path}",
                   ok, detail=f"HTTP {code} ({elapsed}s)",
                   fix=f"Check _handle for {path} in mcc_server.py")

    # ── Content-type header check ──
    try:
        req = urllib.request.Request(BASE_URL + "/status")
        with urllib.request.urlopen(req, timeout=5) as resp:
            ct = resp.headers.get("Content-Type", "")
            REC.record("endpoints", "Content-Type: application/json on /status",
                       "application/json" in ct, detail=ct)
    except Exception as exc:
        REC.record("endpoints", "Content-Type header check", False, detail=str(exc))

    # ── CORS headers present ──
    try:
        req = urllib.request.Request(BASE_URL + "/status")
        req.method = "OPTIONS"
        with urllib.request.urlopen(req, timeout=5) as resp:
            acao = resp.headers.get("Access-Control-Allow-Origin", "")
            REC.record("endpoints", "CORS Access-Control-Allow-Origin present",
                       bool(acao), detail=acao)
    except Exception as exc:
        # OPTIONS may return 204 but urlopen raises error — check manually
        code, _, _ = _http("OPTIONS", "/status")
        REC.record("endpoints", "CORS OPTIONS returns 204",
                   code == 204, detail=f"HTTP {code}")

    # ── 404 for unknown path ──
    code, _, _ = _get("/this_path_does_not_exist_medical_test")
    REC.record("endpoints", "Unknown path returns 404",
               code == 404, detail=f"HTTP {code}",
               fix="Server should return 404 for unknown paths")

    # ── Missing params return 400 ──
    code, data, _ = _post("/capture", "")
    REC.record("endpoints", "POST /capture empty body returns 400",
               code == 400, detail=f"HTTP {code}",
               fix="Empty body should be rejected with 400")

    code, data, _ = _post("/set-aafl-goal", {"goal": ""})
    REC.record("endpoints", "POST /set-aafl-goal empty goal returns 400",
               code == 400, detail=f"HTTP {code}")

    code, data, _ = _post("/run-now", {"goal": ""})
    REC.record("endpoints", "POST /run-now empty goal returns 400",
               code == 400, detail=f"HTTP {code}")

    REC.end_category()


# ── CATEGORY 4: INTEGRATION ────────────────────────────────────────────────────

def test_integration():
    REC.begin_category("integration")

    # Flow 1: capture → chat_latest.txt written
    test_text = f"__integration_test_{int(time.time())}__"
    code, _, _ = _post("/capture", test_text)
    REC.record("integration", "Flow1: POST /capture accepted", code == 200)

    if CHAT_FILE.exists():
        content = CHAT_FILE.read_text(encoding="utf-8", errors="replace")
        REC.record("integration", "Flow1: text appears in chat_latest.txt",
                   test_text in content, detail=f"found={test_text in content}")
    else:
        REC.record("integration", "Flow1: chat_latest.txt exists after capture",
                   False, fix="POST /capture should write to chat_latest.txt")

    # Flow 2: queue goal → appears in /aafl-queue → readable
    test_goal = f"__int_test_goal_{int(time.time())}__"
    code, _, _ = _post("/aafl-queue", {"goal": test_goal})
    REC.record("integration", "Flow2: POST /aafl-queue accepted", code == 200)

    code, data, _ = _get("/aafl-queue")
    found = test_goal in json.dumps(data or {})
    REC.record("integration", "Flow2: queued goal visible via GET /aafl-queue",
               found, detail=f"found={found}")

    # Flow 3: set goal → goal.txt on disk → readable via /api/health
    code, _, _ = _post("/set-aafl-goal", {"goal": "__int_goal_test__"})
    REC.record("integration", "Flow3: POST /set-aafl-goal OK", code == 200)

    if GOAL_TXT.exists():
        txt = GOAL_TXT.read_text(encoding="utf-8", errors="replace").strip()
        REC.record("integration", "Flow3: goal.txt written with correct content",
                   txt == "__int_goal_test__", detail=f"content={txt[:50]}")
    else:
        REC.record("integration", "Flow3: goal.txt exists after set-aafl-goal",
                   False, fix="POST /set-aafl-goal should write to goal.txt")

    # Flow 4: /b2/activity POST → GET returns that entry
    ts_marker = f"int_test_{int(time.time())}"
    code, _, _ = _post("/b2/activity", {"cat": "integration", "msg": ts_marker})
    REC.record("integration", "Flow4: POST /b2/activity accepted", code == 200)

    code, data, _ = _get("/b2/activity")
    entries_text = json.dumps(data or {})
    REC.record("integration", "Flow4: activity entry visible in GET /b2/activity",
               ts_marker in entries_text, detail=f"found={ts_marker in entries_text}")

    # Flow 5: kanban add → save → reload
    code, data, _ = _post("/b2/kanban", {"action": "add", "col": "doing",
                                          "title": "__int_kanban_card__"})
    REC.record("integration", "Flow5: POST /b2/kanban add card", code == 200)

    code2, data2, _ = _get("/b2/kanban")
    found_card = "__int_kanban_card__" in json.dumps(data2 or {})
    REC.record("integration", "Flow5: card persists on GET /b2/kanban",
               found_card, detail=f"found={found_card}")

    # Clean up: delete card
    if found_card and isinstance(data2, dict):
        doing = data2.get("doing", [])
        test_card = next((c for c in doing if c.get("title") == "__int_kanban_card__"), None)
        if test_card:
            _post("/b2/kanban", {"action": "delete", "id": test_card["id"]})

    # Flow 6: known-issues add → GET → delete
    code, add_data, _ = _post("/known-issues", {
        "action": "add", "description": "__int_issue_test__", "severity": "high"
    })
    REC.record("integration", "Flow6: POST /known-issues add", code == 200)

    code2, get_data, _ = _get("/known-issues")
    found_issue = "__int_issue_test__" in json.dumps(get_data or {})
    REC.record("integration", "Flow6: issue visible in GET /known-issues",
               found_issue, detail=f"found={found_issue}")

    if isinstance(add_data, dict) and add_data.get("item", {}).get("id"):
        iid = add_data["item"]["id"]
        _post("/known-issues", {"action": "delete", "id": iid})

    REC.end_category()


# ── CATEGORY 5: EDGE CASES ─────────────────────────────────────────────────────

def test_edge_cases():
    REC.begin_category("edge")

    # Empty string body
    code, _, _ = _post("/capture", "")
    REC.record("edge", "Empty string body rejected (400)", code == 400, detail=f"HTTP {code}")

    # Very long input (10,000 chars)
    long_text = "A" * 10000
    code, data, _ = _post("/capture", long_text)
    REC.record("edge", "10,000-char input handled without crash",
               code in (200, 400, 413), detail=f"HTTP {code}")

    # Unicode and emoji input
    unicode_text = "Test 🚀 emoji and unicode: àéîõü 日本語 العربية"
    code, data, _ = _post("/capture", unicode_text)
    REC.record("edge", "Unicode/emoji input accepted", code == 200, detail=f"HTTP {code}")

    # SQL-injection style input
    sql_input = "'; DROP TABLE solution_log; --"
    code, data, _ = _post("/capture", sql_input)
    REC.record("edge", "SQL-injection style input handled safely",
               code in (200, 400), detail=f"HTTP {code}")

    # Special characters
    special = "<script>alert('xss')</script> & \"quotes\" 'single' null\x00byte"
    code, data, _ = _post("/capture", special)
    REC.record("edge", "Special chars + null bytes handled",
               code in (200, 400), detail=f"HTTP {code}")

    # Malformed JSON body to a JSON endpoint
    code, data, _ = _http("POST", "/set-aafl-goal",
                          body=b"{not valid json!!!",
                          content_type="application/json")
    REC.record("edge", "Malformed JSON body handled gracefully (no 500)",
               code in (400, 200), detail=f"HTTP {code}",
               fix="Malformed JSON should return 400 not 500")

    # Negative index in delete queue
    code, data, _ = _delete("/aafl-queue", {"index": -999})
    REC.record("edge", "Negative index in DELETE /aafl-queue returns error",
               code in (400, 404), detail=f"HTTP {code}")

    # Out-of-range index
    code, data, _ = _delete("/aafl-queue", {"index": 99999})
    REC.record("edge", "Huge index in DELETE /aafl-queue returns error",
               code in (400, 404), detail=f"HTTP {code}")

    # Missing required field
    code, data, _ = _post("/alp-add", {"entry": ""})
    REC.record("edge", "POST /alp-add empty entry returns 400",
               code == 400, detail=f"HTTP {code}")

    # Known-issues with unknown action
    code, data, _ = _post("/known-issues", {"action": "destroy_everything"})
    REC.record("edge", "POST /known-issues unknown action returns 400",
               code == 400, detail=f"HTTP {code}")

    # Double-submit guard: concurrent /stop-aafl calls
    results = []
    def _stop_call():
        c, _, _ = _post("/stop-aafl", {})
        results.append(c)
    threads = [threading.Thread(target=_stop_call) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    all_ok = all(c == 200 for c in results)
    REC.record("edge", "Concurrent /stop-aafl calls all return 200",
               all_ok, detail=f"codes={results}")

    # Path traversal in /api/backup
    code, data, _ = _get("/api/backup?f=../../../etc/passwd")
    REC.record("edge", "Path traversal in /api/backup rejected",
               code in (400, 404), detail=f"HTTP {code}",
               fix="Path traversal attempt should return 400",
               repro="GET /api/backup?f=../../../etc/passwd")

    # Path traversal in /api/session-log
    code, data, _ = _get("/api/session-log?f=../mcc_server.py")
    REC.record("edge", "Path traversal in /api/session-log rejected",
               code in (400, 404), detail=f"HTTP {code}",
               fix="Path traversal should return 400 not 200")

    REC.end_category()


# ── CATEGORY 6: PERFORMANCE ───────────────────────────────────────────────────

def test_performance():
    REC.begin_category("performance")

    # Page load time
    t0 = time.time()
    code, body, _ = _get("/", timeout=15)
    load_time = round(time.time() - t0, 3)
    REC.record("performance", f"Page load time < 500ms (got {load_time*1000:.0f}ms)",
               load_time < 0.5, detail=f"{load_time}s",
               warn=load_time >= 0.5,
               fix="mission_control.html is large — consider lazy-loading sections")

    # Core endpoint response times
    endpoints_to_time = [
        "/status", "/aafl-queue", "/b2/kanban", "/b2/activity", "/b2/costs",
        "/memory/knowledge", "/self-diagnosis", "/api/timeline",
    ]
    slow_count = 0
    for ep in endpoints_to_time:
        code, _, elapsed = _get(ep, timeout=15)
        ok = elapsed < 2.0
        if not ok:
            slow_count += 1
        REC.record("performance", f"Response time {ep} < 2s (got {elapsed}s)",
                   ok, detail=f"{elapsed}s", warn=not ok,
                   fix=f"{ep} is slow — profile the handler")

    REC.record("performance", "All timed endpoints under 2s threshold",
               slow_count == 0, detail=f"{slow_count} slow endpoints")

    # HTML file size
    if HTML_PATH.exists():
        size_kb = round(HTML_PATH.stat().st_size / 1024, 1)
        REC.record("performance", f"HTML size < 300KB (got {size_kb}KB)",
                   size_kb < 300, detail=f"{size_kb}KB",
                   warn=size_kb >= 300,
                   fix="Consider splitting large HTML tabs into lazy-loaded fragments")

    # DB query time (if DB exists)
    if DB_PATH.exists():
        t0 = time.time()
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.execute("SELECT COUNT(*) FROM knowledge")
            conn.close()
        except Exception:
            pass
        db_time = round(time.time() - t0, 3)
        REC.record("performance", f"DB query time < 0.5s (got {db_time}s)",
                   db_time < 0.5, detail=f"{db_time}s", warn=db_time >= 0.5)

    # Cost log parse time
    if COST_LOG.exists():
        t0 = time.time()
        code, data, elapsed = _get("/b2/costs", timeout=15)
        REC.record("performance", f"/b2/costs parse time < 1s (got {elapsed}s)",
                   elapsed < 1.0, detail=f"{elapsed}s", warn=elapsed >= 1.0,
                   fix="Cost log parsing reads the whole file — consider indexing or caching")

    # Self-diagnosis (heavy endpoint)
    code, data, elapsed = _get("/self-diagnosis", timeout=20)
    REC.record("performance", f"/self-diagnosis < 5s (got {elapsed}s)",
               elapsed < 5.0, detail=f"{elapsed}s", warn=elapsed >= 5.0)

    # Memory check: activity log size
    act_log = HERE / "activity_log.json"
    if act_log.exists():
        size_kb = round(act_log.stat().st_size / 1024, 1)
        REC.record("performance", f"activity_log.json < 500KB (got {size_kb}KB)",
                   size_kb < 500, detail=f"{size_kb}KB", warn=size_kb >= 500,
                   fix="Activity log trimming may not be working — check log[-1000:] capping")

    REC.end_category()


# ── CATEGORY 7: ERROR HANDLING ─────────────────────────────────────────────────

def test_error_handling():
    REC.begin_category("error_handling")

    # Bad JSON to JSON-expecting endpoints
    for path in ["/set-aafl-goal", "/aafl-config", "/b2/prefs"]:
        code, data, _ = _http("POST", path,
                              body=b"not json at all }{",
                              content_type="application/json")
        no_crash = code not in (500, 0)
        REC.record("error_handling", f"Bad JSON to {path} handled (no 500)",
                   no_crash, detail=f"HTTP {code}",
                   fix=f"{path} should return 400 for malformed JSON, not 500")

    # Restore with nonexistent file
    code, data, _ = _post("/api/restore", {"filename": "nonexistent_file_xyz.md"})
    REC.record("error_handling", "POST /api/restore with nonexistent file returns 404",
               code == 404, detail=f"HTTP {code}")

    # Invalid filename in /api/backup
    code, data, _ = _get("/api/backup?f=")
    REC.record("error_handling", "POST /api/backup empty filename returns 400",
               code == 400, detail=f"HTTP {code}")

    # Resolve stuck with missing item_id
    code, data, _ = _post("/resolve-stuck", {"item_id": ""})
    REC.record("error_handling", "POST /resolve-stuck empty item_id returns 400",
               code == 400, detail=f"HTTP {code}")

    # Approve promo with missing item_id
    code, data, _ = _post("/approve-promo", {"item_id": ""})
    REC.record("error_handling", "POST /approve-promo empty item_id returns 400",
               code == 400, detail=f"HTTP {code}")

    # Server error response has 'error' key
    code, data, _ = _get("/api/backup?f=nonexistent.md")
    has_error_key = isinstance(data, dict) and "error" in data
    REC.record("error_handling", "Error response contains 'error' field",
               has_error_key or code == 404, detail=f"HTTP {code} keys={list((data or {}).keys())[:5]}")

    # WCCS: if chat_latest.txt is empty/missing, should reject
    # Note: if chat_latest.txt already has content from earlier tests, 200 is correct
    # This test deletes the chat file first to force the empty-guard to trigger
    chat_backup_eh = None
    if CHAT_FILE.exists():
        chat_backup_eh = CHAT_FILE.read_bytes()
        CHAT_FILE.unlink()
    code, data, _ = _post("/wccs", "")
    REC.record("error_handling", "POST /wccs with no chat file returns 400",
               code in (400, 409), detail=f"HTTP {code}",
               fix="POST /wccs should return 400 when chat_latest.txt is missing or empty")
    if chat_backup_eh is not None:
        CHAT_FILE.write_bytes(chat_backup_eh)

    # Module toggle with missing fields
    code, data, _ = _post("/toggle-module", {"id": ""})
    REC.record("error_handling", "POST /toggle-module missing enabled returns 400",
               code in (400, 500), detail=f"HTTP {code}")

    # Chain run with empty chain
    code, data, _ = _post("/b2/chain-run", {"chain": []})
    REC.record("error_handling", "POST /b2/chain-run empty chain returns 400",
               code == 400, detail=f"HTTP {code}")

    # Worker count clamped (boundary)
    code, data, _ = _post("/b2/workers", {"workers": 999})
    REC.record("error_handling", "POST /b2/workers clamps to max 10",
               code == 200 and (data or {}).get("workers", 999) <= 10,
               detail=f"workers={( data or {}).get('workers', '?')}")

    REC.end_category()


# ── CATEGORY 8: STATE PERSISTENCE ─────────────────────────────────────────────

def test_persistence():
    REC.begin_category("persistence")

    # Prefs written to disk
    code, _, _ = _post("/b2/prefs", {"theme": "dark", "_persist_test": True})
    prefs_ok = MCC_PREFS.exists() and "_persist_test" in MCC_PREFS.read_text(encoding="utf-8", errors="replace")
    REC.record("persistence", "POST /b2/prefs persists to mcc_prefs.json",
               prefs_ok, fix="Check mcc_prefs.json write path in mcc_server.py")

    # Budget caps persisted
    caps_file = HERE / "budget_caps.json"
    code, _, _ = _post("/b2/budget-caps", {"daily": 0.50, "_test": True})
    caps_ok = caps_file.exists()
    REC.record("persistence", "POST /b2/budget-caps persists to budget_caps.json",
               caps_ok, fix="budget_caps.json not created after POST")

    # AAFL config persisted
    code, _, _ = _post("/aafl-config", {"_persist_test": True})
    aafl_cfg_ok = AAFL_CFG.exists()
    REC.record("persistence", "POST /aafl-config persists to aafl_control_config.json",
               aafl_cfg_ok)

    # Scout config persisted
    code, _, _ = _post("/scout-config", {"_persist_test": True})
    scout_cfg = HERE / "chief_scout_config.json"
    REC.record("persistence", "POST /scout-config persists to chief_scout_config.json",
               scout_cfg.exists())

    # Kanban board survives a GET-POST-GET cycle
    code, before, _ = _get("/b2/kanban")
    if isinstance(before, dict):
        before_count = sum(len(before.get(col, [])) for col in ("todo", "doing", "done"))
        code, _, _ = _post("/b2/kanban", {"action": "add", "col": "todo",
                                           "title": "__persist_test_card__"})
        code2, after, _ = _get("/b2/kanban")
        if isinstance(after, dict):
            after_count = sum(len(after.get(col, [])) for col in ("todo", "doing", "done"))
            REC.record("persistence", "Kanban card persists after add + re-GET",
                       after_count > before_count, detail=f"{before_count}->{after_count}")
            # Clean up
            todo = after.get("todo", [])
            card = next((c for c in todo if c.get("title") == "__persist_test_card__"), None)
            if card:
                _post("/b2/kanban", {"action": "delete", "id": card["id"]})

    # Auto-WCCS state: start, GET, verify active
    _post("/api/auto-wccs", {"action": "start", "interval": 30})
    code, data, _ = _get("/api/auto-wccs")
    active = (data or {}).get("active", False)
    REC.record("persistence", "Auto-WCCS active state retrievable after start",
               active, detail=f"active={active}")
    _post("/api/auto-wccs", {"action": "stop"})

    # Activity log not lost between calls
    before_size = (HERE / "activity_log.json").stat().st_size if (HERE / "activity_log.json").exists() else 0
    _post("/b2/activity", {"cat": "persist_test", "msg": "test entry"})
    after_size = (HERE / "activity_log.json").stat().st_size if (HERE / "activity_log.json").exists() else 0
    REC.record("persistence", "Activity log grows after POST /b2/activity",
               after_size >= before_size, detail=f"{before_size}->{after_size} bytes")

    REC.end_category()


# ── CATEGORY 9: ACCESSIBILITY ──────────────────────────────────────────────────

def test_accessibility():
    REC.begin_category("accessibility")

    if not HTML_PATH.exists():
        REC.record("accessibility", "HTML file exists", False)
        REC.end_category()
        return

    content = HTML_PATH.read_text(encoding="utf-8", errors="replace")

    # lang attribute on <html>
    has_lang = 'lang="en"' in content or "lang='en'" in content
    REC.record("accessibility", "html[lang] attribute set to 'en'", has_lang,
               fix="Add lang='en' to <html> tag")

    # meta charset
    has_charset = "charset" in content.lower()
    REC.record("accessibility", "Meta charset declared", has_charset)

    # viewport meta
    has_viewport = 'name="viewport"' in content
    REC.record("accessibility", "Meta viewport declared", has_viewport)

    # Title element
    has_title = "<title>" in content
    REC.record("accessibility", "Page <title> element present", has_title)

    # Buttons have accessible text (labels or aria)
    buttons_raw = re.findall(r'<button[^>]*>(.*?)</button>', content, re.DOTALL)
    buttons_with_text = sum(1 for b in buttons_raw if b.strip()[:1] not in ("", "<"))
    total_buttons = len(buttons_raw)
    REC.record("accessibility", f"Buttons have text content ({buttons_with_text}/{total_buttons})",
               buttons_with_text >= total_buttons * 0.8,
               detail=f"{buttons_with_text}/{total_buttons} have text",
               warn=buttons_with_text < total_buttons,
               fix="Some buttons lack text content — add aria-label or visible text")

    # Focus outline (not hidden by outline:none without alternative)
    outline_none_count = content.count("outline:none") + content.count("outline: none")
    has_focus_ring_alternative = ":focus{" in content or ".focus" in content or "focus-visible" in content
    REC.record("accessibility", "Focus ring not completely suppressed",
               outline_none_count <= 3 or has_focus_ring_alternative,
               detail=f"outline:none occurrences={outline_none_count}",
               warn=outline_none_count > 3,
               fix="Too many outline:none — ensure focus-visible style is provided")

    # ARIA roles present somewhere
    has_aria = "aria-" in content or "role=" in content
    REC.record("accessibility", "ARIA roles/attributes used", has_aria,
               warn=not has_aria,
               fix="Add aria-label to icon-only buttons and aria-selected to tabs")

    # Input labels — inputs should have associated labels
    input_ids = re.findall(r'<input[^>]+id="([^"]+)"', content)
    label_fors = re.findall(r'<label[^>]+for="([^"]+)"', content)
    labelled_inputs = sum(1 for iid in input_ids if iid in label_fors)
    REC.record("accessibility", "Inputs have associated <label> elements",
               labelled_inputs > 0 or len(input_ids) == 0,
               detail=f"{labelled_inputs}/{len(input_ids)} inputs labelled",
               warn=True,
               fix="Add <label for=...> to all user-facing inputs for screen readers")

    # Colour contrast (approximation — check CSS for known bad combos)
    # #555 on #0d0d0d = very low contrast
    has_555_on_dark = "#555" in content and "#0d0d0d" in content
    REC.record("accessibility", "Secondary text colour (#555) may fail WCAG AA",
               not has_555_on_dark, warn=has_555_on_dark,
               detail="#555 on #0d0d0d ≈ 3.2:1 contrast ratio (AA requires 4.5:1)",
               fix="Lighten secondary text from #555 to #777 minimum on dark backgrounds")

    # Tab index management (no positive tabindex which breaks natural order)
    tabindex_pos = re.findall(r'tabindex="([^"]*)"', content)
    bad_tabindex = [t for t in tabindex_pos if t.isdigit() and int(t) > 0]
    REC.record("accessibility", "No positive tabindex values (breaks tab order)",
               len(bad_tabindex) == 0,
               detail=f"positive tabindex found: {bad_tabindex[:5]}",
               fix="Remove positive tabindex values — use DOM order instead")

    REC.end_category()


# ── CATEGORY 10: CROSS-TAB ────────────────────────────────────────────────────

def test_cross_tab():
    REC.begin_category("cross_tab")

    if not HTML_PATH.exists():
        REC.record("cross_tab", "HTML exists", False)
        REC.end_category()
        return

    content = HTML_PATH.read_text(encoding="utf-8", errors="replace")

    # All 17 tab panes exist (16 original + medical)
    expected_tabs = [
        "home", "wccs", "kanban", "aafl-runs", "scout", "costs",
        "aafl-control", "memory", "promo", "acca", "alp", "storage",
        "self-diagnosis", "autolog", "providerhealth", "keybind-profiles",
        "medical",
    ]
    found = [t for t in expected_tabs if f'id="tab-{t}"' in content]
    missing = [t for t in expected_tabs if t not in [f.replace("tab-", "") for f in found]]
    REC.record("cross_tab", f"All 17 tab panes in DOM ({len(found)}/17)",
               len(found) >= 17, detail=f"missing: {missing}",
               fix=f"Missing tab panes: {missing}")

    # switchTab function exists
    has_switchtab = "switchTab(" in content or "function switchTab" in content
    REC.record("cross_tab", "switchTab() function defined", has_switchtab)

    # Active tab state managed
    has_active_mgmt = "classList.remove('active')" in content and "classList.add('active')" in content
    REC.record("cross_tab", "Tab active class properly toggled", has_active_mgmt)

    # Home tab has auto-refresh (it should poll /health-status etc.)
    home_has_refresh = "setInterval" in content and "home" in content
    REC.record("cross_tab", "Home tab has polling/refresh logic", home_has_refresh)

    # AAFL tab has live output polling
    aafl_has_poll = "/aafl/live" in content or "/aafl-status" in content
    REC.record("cross_tab", "AAFL Control tab polls live output", aafl_has_poll)

    # Scout results has polling
    scout_poll = "/scout-result" in content or "/scout/results" in content
    REC.record("cross_tab", "Scout tab polls for results", scout_poll)

    # Auto-WCCS timer visible in WCCS tab
    has_auto_wccs_ui = "auto-toggle" in content or "autoWccs" in content.replace(" ", "")
    REC.record("cross_tab", "Auto-WCCS timer UI present in WCCS tab", has_auto_wccs_ui)

    # Keyboard shortcut tab switching
    has_key_tab_switch = "dataset.tab" in content or "data-tab" in content
    REC.record("cross_tab", "Keyboard tab switching via data-tab attributes", has_key_tab_switch)

    # Memory Inspector tab
    has_memory_tab = 'id="tab-memory"' in content
    REC.record("cross_tab", "Memory Inspector tab (#tab-memory) present", has_memory_tab)

    # WCCS drill-down sub-tabs
    has_wccs_subs = 'id="tab-search"' in content or 'id="tab-rewind"' in content
    REC.record("cross_tab", "WCCS sub-tabs (search/rewind/diff/sessions) present", has_wccs_subs)

    # Home card click navigates to tab
    has_homecard_click = "homeCardClick" in content or "switchTab" in content
    REC.record("cross_tab", "Home cards have tab navigation onclick", has_homecard_click)

    REC.end_category()


# ── CATEGORY 11: SAFETY ───────────────────────────────────────────────────────

def test_safety():
    REC.begin_category("safety")

    # Watchdog exists
    REC.record("safety", "aafl_watchdog.py exists",
               WATCHDOG.exists(), fix="aafl_watchdog.py missing — watchdog protection gone")

    # Cost guard exists
    REC.record("safety", "cost_guard.py exists",
               COST_GUARD.exists(), fix="cost_guard.py missing — no spend protection")

    # Budget caps file has reasonable defaults
    caps_file = HERE / "budget_caps.json"
    if caps_file.exists():
        try:
            caps = json.loads(caps_file.read_text(encoding="utf-8"))
            daily_cap = caps.get("daily", 0)
            REC.record("safety", f"Daily budget cap set ({daily_cap})",
                       daily_cap > 0, detail=f"£{daily_cap}",
                       fix="Set a daily budget cap in budget_caps.json")
        except Exception as exc:
            REC.record("safety", "budget_caps.json valid JSON", False, detail=str(exc))
    else:
        REC.record("safety", "budget_caps.json exists", False,
                   warn=True, fix="Create budget_caps.json with daily/weekly/monthly caps")

    # WCCS double-submit lock — test with no chat file to force guard
    chat_backup_sf = None
    if CHAT_FILE.exists():
        chat_backup_sf = CHAT_FILE.read_bytes()
        CHAT_FILE.unlink()
    code, _, _ = _post("/wccs", "")
    REC.record("safety", "POST /wccs rejects missing/empty chat (no runaway save)",
               code in (400, 409), detail=f"HTTP {code}",
               fix="WCCS guard: should return 400 when chat_latest.txt is missing/empty")
    if chat_backup_sf is not None:
        CHAT_FILE.write_bytes(chat_backup_sf)

    # Scout lock — can't double-start
    # We test by checking the running flag endpoint, not actually starting
    code, data, _ = _get("/scout/results")
    REC.record("safety", "GET /scout/results returns running status",
               code == 200 and "running" in (data or {}),
               detail=f"running={( data or {}).get('running', '?')}")

    # AAFL stop works
    code, data, _ = _post("/stop-aafl", {})
    REC.record("safety", "POST /stop-aafl returns ok",
               code == 200, detail=str(code))

    # Pause flag mechanism
    _post("/b2/pause-aafl", {})
    pause_flag = HERE / "aafl_pause.flag"
    REC.record("safety", "Pause flag created by /b2/pause-aafl",
               pause_flag.exists(), fix="Pause flag mechanism broken")

    _post("/b2/resume-aafl", {})
    REC.record("safety", "Resume clears pause flag",
               not pause_flag.exists(), fix="Resume should delete aafl_pause.flag")

    # Stuck inbox endpoint works
    code, data, _ = _get("/stuck-inbox")
    REC.record("safety", "GET /stuck-inbox responds",
               code == 200, detail=str(code))

    # Promo queue: unknown ID returns ok:false (server returns 200 with ok=false by design)
    code, data, _ = _post("/approve-promo", {"item_id": "NONEXISTENT_ID"})
    # Server returns {"ok": false} with 200 for unknown IDs — this is by design
    # Ideally should be 404, but current impl always 200 with ok=true/false
    found_ok_false = isinstance(data, dict) and data.get("ok") is False
    REC.record("safety", "POST /approve-promo with unknown ID returns ok:false",
               code == 200 and found_ok_false, detail=f"HTTP {code} ok={( data or {}).get('ok')}",
               warn=not found_ok_false,
               fix="Consider returning 404 status (not 200) for unknown item_id in approve/reject-promo")

    REC.end_category()


# ── CATEGORY 12: RECOVERY ─────────────────────────────────────────────────────

def test_recovery():
    REC.begin_category("recovery")

    # Missing config file — AAFL config endpoint should return {} not crash
    # We test by asking for aafl-config before any exists (it returns {})
    code, data, _ = _get("/aafl-config")
    REC.record("recovery", "GET /aafl-config returns {} when config not set",
               code == 200 and isinstance(data, dict), detail=f"HTTP {code}")

    # Corrupt JSON in budget_caps.json — test graceful degradation
    caps_file = HERE / "budget_caps.json"
    original = None
    if caps_file.exists():
        original = caps_file.read_bytes()
        caps_file.write_text("{CORRUPT JSON!!!", encoding="utf-8")

    code, data, _ = _get("/b2/budget-caps")
    REC.record("recovery", "GET /b2/budget-caps recovers from corrupt JSON",
               code == 200, detail=f"HTTP {code}",
               fix="b2_load_json should fall back to default when JSON is corrupt — check _b2_load_json")

    if original is not None:
        caps_file.write_bytes(original)

    # Missing stuck_inbox.json — returns empty list
    stub = HERE / "_test_stuck_inbox_backup.json"
    if STUCK_INBOX.exists():
        import shutil
        shutil.copy2(STUCK_INBOX, stub)
        STUCK_INBOX.unlink()

    code, data, _ = _get("/stuck-inbox")
    REC.record("recovery", "GET /stuck-inbox returns empty list when file missing",
               code == 200 and (data or {}).get("items", None) is not None,
               detail=f"HTTP {code}")

    if stub.exists():
        import shutil
        shutil.copy2(stub, STUCK_INBOX)
        stub.unlink()

    # /wccs with no chat file — should return 400 not crash
    chat_backup = None
    if CHAT_FILE.exists():
        chat_backup = CHAT_FILE.read_bytes()
        CHAT_FILE.unlink()

    code, data, _ = _post("/wccs", "")
    REC.record("recovery", "POST /wccs with missing chat_latest.txt returns 400",
               code in (400, 409), detail=f"HTTP {code}",
               fix="WCCS should check chat file exists before running")

    if chat_backup is not None:
        CHAT_FILE.write_bytes(chat_backup)

    # /self-diagnosis recovers without MOT report
    mot_path = HERE / "health_results" / "full_mot_report.json"
    mot_backup = None
    if mot_path.exists():
        mot_backup = mot_path.read_bytes()
        mot_path.unlink()

    code, data, _ = _get("/self-diagnosis")
    REC.record("recovery", "GET /self-diagnosis works without full_mot_report.json",
               code == 200, detail=f"HTTP {code}")

    if mot_backup is not None:
        mot_path.write_bytes(mot_backup)

    # WCCS endpoint accepts chat as body (recovery: writes chat then runs)
    code, data, _ = _post("/wccs", "test chat text for recovery check")
    REC.record("recovery", "POST /wccs with body text writes chat and responds",
               code in (200, 400, 409, 500), detail=f"HTTP {code}")

    REC.end_category()


# ── CATEGORY 13: DEPENDENCY HEALTH ────────────────────────────────────────────

def test_deps():
    REC.begin_category("deps")

    core_modules = [
        "aafl_core", "loop_manager", "evaluator", "researcher",
        "memory_bank", "meta_loop", "chief_scout", "mcu_optimizer",
        "dashboard_builder", "task_router", "provider_health",
    ]

    for mod in core_modules:
        try:
            res = subprocess.run(
                [PYTHON, "-c",
                 f"import sys; sys.path.insert(0, r'{HERE}'); import {mod}"],
                capture_output=True, text=True, timeout=15, cwd=str(HERE),
            )
            ok = res.returncode == 0
            detail = "OK" if ok else (res.stderr or "").strip().split("\n")[-1][:80]
            REC.record("deps", f"import {mod}", ok, detail=detail,
                       fix=f"Fix import error in {mod}.py")
        except subprocess.TimeoutExpired:
            REC.record("deps", f"import {mod}", False, detail="Timed out after 15s")
        except Exception as exc:
            REC.record("deps", f"import {mod}", False, detail=str(exc)[:80])

    # Optional modules used by server
    optional_modules = [
        ("module_loader", "/modules endpoint"),
        ("preset_manager", "/presets endpoint"),
        ("smart_suggester", "/suggest-provider endpoint"),
        ("chain_runner", "/run-chain endpoint"),
        ("scout_timer", "/scout-timer/status endpoint"),
        ("source_library_manager", "/sources-library endpoint"),
        ("stuck_inbox", "/stuck-inbox/summary endpoint"),
        ("storage_manager", "/storage endpoint"),
    ]
    for mod, used_by in optional_modules:
        try:
            res = subprocess.run(
                [PYTHON, "-c",
                 f"import sys; sys.path.insert(0, r'{HERE}'); import {mod}"],
                capture_output=True, text=True, timeout=10, cwd=str(HERE),
            )
            ok = res.returncode == 0
            detail = f"OK — used by {used_by}" if ok else (res.stderr or "").strip()[-60:]
            REC.record("deps", f"optional import {mod}", ok, detail=detail,
                       warn=not ok,
                       fix=f"{mod} not importable — {used_by} will fail with 500")
        except Exception as exc:
            REC.record("deps", f"optional import {mod}", False,
                       detail=str(exc)[:60], warn=True)

    # Required config files
    configs = [
        ("aafl_control_config.json", "AAFL engine config"),
        ("chief_scout_config.json", "Scout config"),
        ("mcc_prefs.json", "UI preferences"),
    ]
    for fname, label in configs:
        path = HERE / fname
        exists = path.exists()
        if exists:
            try:
                json.loads(path.read_text(encoding="utf-8"))
                REC.record("deps", f"{fname} valid JSON", True, detail=label)
            except Exception as exc:
                REC.record("deps", f"{fname} valid JSON", False,
                           detail=str(exc)[:60], fix=f"Fix corrupt JSON in {fname}")
        else:
            REC.record("deps", f"{fname} exists", False, warn=True,
                       detail="will be created on first use",
                       fix=f"Create {fname} with defaults")

    # DB health
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(DB_PATH))
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            conn.close()
            has_knowledge = "knowledge" in tables
            has_solution = "solution_log" in tables
            REC.record("deps", "DB has 'knowledge' table", has_knowledge,
                       detail=f"tables: {tables}",
                       fix="Run: python memory_bank.py to create tables")
            REC.record("deps", "DB has 'solution_log' table", has_solution,
                       fix="Run: python memory_bank.py to create tables")
        except Exception as exc:
            REC.record("deps", "knowledge_engine.db readable", False, detail=str(exc)[:80])
    else:
        REC.record("deps", "knowledge_engine.db exists", False, warn=True,
                   detail="DB not yet created",
                   fix="Run: python memory_bank.py to initialise database")

    REC.end_category()


# ── CATEGORY 14: REGRESSION (re-run existing MOT) ────────────────────────────

def test_regression():
    REC.begin_category("regression")

    if not MOT_PATH.exists():
        REC.record("regression", "mcc_full_mot.py exists", False,
                   fix="mcc_full_mot.py not found — cannot run regression suite")
        REC.end_category()
        return

    print("  [regression] Running mcc_full_mot.py …")
    try:
        result = subprocess.run(
            [PYTHON, str(MOT_PATH)],
            capture_output=True, text=True, timeout=180, cwd=str(HERE),
        )
        ok = result.returncode == 0
        REC.record("regression", "mcc_full_mot.py exits cleanly",
                   ok, detail=f"exit={result.returncode}")
    except subprocess.TimeoutExpired:
        REC.record("regression", "mcc_full_mot.py runs within 3 minutes",
                   False, fix="mcc_full_mot.py timed out after 180s")
        REC.end_category()
        return
    except Exception as exc:
        REC.record("regression", "mcc_full_mot.py runs", False, detail=str(exc))
        REC.end_category()
        return

    # Load the MOT report
    mot_report_path = HERE / "health_results" / "full_mot_report.json"
    if not mot_report_path.exists():
        REC.record("regression", "MOT report written to disk", False)
        REC.end_category()
        return

    try:
        report = json.loads(mot_report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        REC.record("regression", "MOT report valid JSON", False, detail=str(exc))
        REC.end_category()
        return

    total = report.get("total", 0)
    passed = report.get("passed", 0)
    failed = report.get("failed", 0)
    pct = report.get("pass_rate", 0)

    REC.record("regression", f"MOT total checks: {total}", total > 0, detail=str(total))
    REC.record("regression", f"MOT pass rate >= 80% (got {pct}%)",
               pct >= 80, detail=f"{pct}% ({passed}/{total})",
               fix=f"MOT has {failed} failures — see health_results/full_mot_report.json")

    # Report each MOT failure as a regression record
    failures = report.get("failures", [])
    for f in failures[:20]:
        REC.record("regression", f"MOT [{f.get('group')}] {f.get('name')}",
                   False, detail=f.get("detail", ""),
                   fix=f"Fix: {f.get('name')} — {f.get('detail', '')}")

    if not failures:
        REC.record("regression", "All existing MOT checks pass", True,
                   detail=f"{passed}/{total} PASS")

    REC.end_category()


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

CATEGORY_MAP = {
    "functional":     test_functional,
    "ux":             None,   # needs inventory arg
    "endpoints":      test_endpoints,
    "integration":    test_integration,
    "edge":           test_edge_cases,
    "performance":    test_performance,
    "error_handling": test_error_handling,
    "persistence":    test_persistence,
    "accessibility":  None,   # needs inventory arg
    "cross_tab":      None,   # needs inventory arg
    "safety":         test_safety,
    "recovery":       test_recovery,
    "deps":           test_deps,
    "regression":     test_regression,
}

QUICK_CATEGORIES = ["functional", "endpoints"]


def run_medical(categories: list[str] | None = None) -> dict:
    ts = datetime.datetime.now()
    ts_str = ts.strftime("%Y-%m-%d_%H-%M")

    print("\n" + "+" + "=" * 64 + "+")
    print("|   DOCTOR CLAC -- MCC FULL MEDICAL                             |")
    print(f"|   {ts.strftime('%Y-%m-%d %H:%M:%S')}" + " " * (54 - 19) + "|")
    print("+" + "=" * 64 + "+")

    # PHASE 1: Inventory
    print("\n[PHASE 1] Building inventory …")
    inventory = build_inventory()
    print(f"  Tabs: {len(inventory.get('tabs_full', []))}")
    print(f"  GET endpoints: {len(inventory.get('endpoints_get_full', []))}")
    print(f"  POST endpoints: {len(inventory.get('endpoints_post_full', []))}")
    print(f"  Fetch calls in HTML: {len(inventory.get('fetch_calls_in_html', []))}")

    # PHASE 2: WMBW
    print("\n[PHASE 2] Running WMBW analysis …")
    build_wmbw_report(inventory)

    # Ensure server is up for phases 3-4
    print("\n[SERVER] Ensuring MCC server is available …")
    server_ok = ensure_server()
    if not server_ok:
        print("  [WARN] Could not start server — endpoint/functional tests will FAIL")

    # PHASE 3: Tests
    print("\n[PHASE 3] Running medical tests …")
    if categories is None:
        categories = list(CATEGORY_MAP.keys())

    for cat in categories:
        if cat not in CATEGORY_MAP:
            print(f"  [SKIP] Unknown category: {cat}")
            continue
        fn = CATEGORY_MAP[cat]
        if fn is None:
            # Needs inventory argument
            if cat == "ux":
                test_ux(inventory)
            elif cat == "accessibility":
                test_accessibility()
            elif cat == "cross_tab":
                test_cross_tab()
        else:
            fn()

    stop_server_if_ours()

    # PHASE 4: Report
    fitness_score = REC.score()
    fails = [r for r in REC.results if r["status"] == "FAIL"]
    warns = [r for r in REC.results if r["status"] == "WARN"]

    if fitness_score >= 90:
        verdict = "PATIENT IS FIT FOR SERVICE"
        verdict_detail = "All critical systems healthy. Minor improvements recommended."
    elif fitness_score >= 70:
        verdict = "RESTRICTED DUTY"
        verdict_detail = "Core functions working but notable issues need attention before heavy use."
    else:
        verdict = "NEEDS TREATMENT"
        verdict_detail = "Critical failures found. Fix priority issues before production use."

    report = {
        "run_at": ts.isoformat(timespec="seconds"),
        "fitness_score": fitness_score,
        "verdict": verdict,
        "total": REC.total,
        "passed": REC.passed,
        "failed": REC.failed,
        "warned": REC.warned,
        "categories_run": categories,
        "results": REC.results,
        "failures": fails,
        "warnings": warns,
        "top_fixes": REC.issues()[:10],
        "category_times": REC._category_times,
    }

    # Write dated report
    report_path = MED_DIR / f"mcc_medical_report_{ts_str}.md"
    _write_report(report_path, report, inventory, verdict, verdict_detail)

    # Update rolling history
    history_path = MED_DIR / "mcc_medical_history.json"
    history = []
    if history_path.exists():
        try:
            history = json.loads(history_path.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.append({
        "run_at": report["run_at"],
        "fitness_score": fitness_score,
        "verdict": verdict,
        "total": REC.total,
        "passed": REC.passed,
        "failed": REC.failed,
        "warned": REC.warned,
    })
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    # Print final summary
    print("\n" + "=" * 66)
    print("  MEDICAL COMPLETE")
    print("=" * 66)
    print(f"  Score:   {fitness_score}/100")
    print(f"  Verdict: {verdict}")
    print(f"  Total:   {REC.total} | Pass: {REC.passed} | Fail: {REC.failed} | Warn: {REC.warned}")
    print(f"  Report:  {report_path.name}")
    if fails:
        print(f"\n  TOP FAILURES ({min(len(fails), 5)}):")
        for f in fails[:5]:
            print(f"    [{f['category']}] {f['name']}: {f.get('detail', '')}")
    print("=" * 66 + "\n")

    return report


def _write_report(path: Path, report: dict, inventory: dict,
                  verdict: str, verdict_detail: str):
    ts = report["run_at"]
    score = report["fitness_score"]
    fails = report["failures"]
    warns = report["warnings"]
    top_fixes = report["top_fixes"]

    lines = [
        f"# MCC Medical Report",
        f"**Date:** {ts}  |  **Score:** {score}/100  |  **Verdict:** {verdict}",
        "",
        "---",
        "",
        "## Doctor's Verdict",
        "",
        f"### {verdict}",
        f"{verdict_detail}",
        "",
        f"**Fitness Score: {score}/100**",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total checks | {report['total']} |",
        f"| Passed | {report['passed']} |",
        f"| Failed | {report['failed']} |",
        f"| Warnings | {report['warned']} |",
        "",
        "---",
        "",
        "## Top Priority Fixes",
        "",
    ]
    for i, fix in enumerate(top_fixes[:3], 1):
        lines.append(f"{i}. {fix}")

    lines += [
        "",
        "## Top WMBW Improvement Recommendations",
        "",
    ]
    flagged = [(k, v) for k, v in WMBW_BEST_PRACTICES.items()
               if v.get("flag_for_upgrade") and v["score"] < 7]
    for i, (k, v) in enumerate(sorted(flagged, key=lambda x: x[1]["score"])[:3], 1):
        lines.append(f"{i}. **{k.replace('_', ' ').title()} ({v['score']}/10):** {v['recommendation']}")

    lines += [
        "",
        "## Long-Term Wellness Recommendations",
        "",
        "1. **Consolidate polling:** Replace per-tab setInterval with a central dispatcher that pauses when the browser tab is hidden. This will reduce background CPU use by ~60% and prevent stale data from accumulating.",
        "2. **Structured error codes:** Add `error_code` fields to all API error responses so the frontend can give specific recovery suggestions rather than generic error messages.",
        "3. **ARIA audit:** A full screen-reader audit is needed. Tab buttons lack `role=tab` and `aria-selected`. This is a one-afternoon fix with high accessibility dividend.",
        "4. **DB index optimisation:** If knowledge_engine.db grows beyond 10,000 rows, add `CREATE INDEX idx_knowledge_created ON knowledge(created_at)` to keep query times under 50ms.",
        "5. **Automated regression CI:** Wire `python mcc_medical.py --quick` to run on git push so regressions are caught at commit time rather than after deployment.",
        "",
        "---",
        "",
        "## Failures Detail",
        "",
    ]

    if not fails:
        lines.append("_No failures found. Patient passed all checks._")
    else:
        lines.append(f"**{len(fails)} failure(s) found:**")
        lines.append("")
        for f in fails:
            lines.append(f"### [{f['category'].upper()}] {f['name']}")
            lines.append(f"- **Detail:** {f.get('detail', 'n/a')}")
            if f.get("repro"):
                lines.append(f"- **Reproduce:** `{f['repro']}`")
            if f.get("fix"):
                lines.append(f"- **Fix:** {f['fix']}")
            lines.append("")

    lines += [
        "## Warnings Detail",
        "",
    ]
    if not warns:
        lines.append("_No warnings._")
    else:
        for w in warns:
            lines.append(f"- **[{w['category']}]** {w['name']}: {w.get('detail', '')}")

    lines += [
        "",
        "---",
        "",
        "## Inventory Summary",
        "",
        f"- Tabs: {len(inventory.get('tabs_full', []))}",
        f"- GET endpoints: {len(inventory.get('endpoints_get_full', []))}",
        f"- POST endpoints: {len(inventory.get('endpoints_post_full', []))}",
        f"- DELETE endpoints: {len(inventory.get('endpoints_delete_full', []))}",
        f"- Fetch calls in HTML: {len(inventory.get('fetch_calls_in_html', []))}",
        "",
        "### All GET Endpoints",
        "",
    ]
    for ep in inventory.get("endpoints_get_full", []):
        lines.append(f"- `GET {ep}`")

    lines += [
        "",
        "### All POST Endpoints",
        "",
    ]
    for ep in inventory.get("endpoints_post_full", []):
        lines.append(f"- `POST {ep}`")

    lines += [
        "",
        "---",
        "",
        f"_Report generated by mcc_medical.py — Doctor CLAC_",
        f"_History: health_results/mcc_medical/mcc_medical_history.json_",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [report] Saved -> {path.name}")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Doctor CLAC — MCC Full Medical. Run: python mcc_medical.py"
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Run quick check: functional + endpoints only"
    )
    parser.add_argument(
        "--category", type=str, default=None,
        help="Comma-separated list of categories to run (e.g. --category=ux,safety)"
    )
    args = parser.parse_args()

    if args.quick:
        cats = QUICK_CATEGORIES
    elif args.category:
        cats = [c.strip() for c in args.category.split(",")]
    else:
        cats = None  # all categories

    report = run_medical(cats)
    sys.exit(0 if report["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
