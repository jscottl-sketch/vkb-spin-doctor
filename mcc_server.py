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
import http.server
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

PORT         = 8080
HOST         = "localhost"
HERE         = Path(__file__).parent
CHAT         = HERE / "chat_latest.txt"
SCOUT_OUTPUT = HERE / "scout_output"
SCOUT_LATEST = SCOUT_OUTPUT / "latest.txt"
SCOUT_CONFIG = HERE / "chief_scout_config.json"
PYTHON       = sys.executable

# ── AAFL Control paths ────────────────────────────────────────────────────────
AAFL_CONFIG  = HERE / "aafl_control_config.json"
AAFL_OUTPUT  = HERE / "aafl_output"
AAFL_LATEST  = AAFL_OUTPUT / "latest.txt"
GOAL_TXT     = HERE / "goal.txt"
GOAL_QUEUE   = HERE / "goal_queue.txt"
DB_PATH      = HERE / "data" / "knowledge_engine.db"

_state_lock  = threading.Lock()
_wccs_lock   = threading.Lock()
_scout_lock  = threading.Lock()
_aafl_lock   = threading.Lock()

_last_wccs: dict = {"result": None, "time": None, "stdout": ""}
_last_capture: datetime.datetime | None = None
_scout_running: bool = False
_aafl_running: bool  = False
_aafl_proc           = None  # subprocess.Popen handle


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
        if path == "/status":
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
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]
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
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_DELETE(self):
        path = self.path.split("?")[0]
        if path == "/aafl-queue":
            self._handle_aafl_queue_delete()
        else:
            self._send_json({"error": "Not found"}, 404)

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
