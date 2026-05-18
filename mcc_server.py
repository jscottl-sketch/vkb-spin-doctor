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
import subprocess
import sys
import threading
from pathlib import Path

PORT   = 8080
HOST   = "localhost"
HERE   = Path(__file__).parent
CHAT   = HERE / "chat_latest.txt"
PYTHON = sys.executable

_state_lock = threading.Lock()
_wccs_lock  = threading.Lock()

_last_wccs: dict = {"result": None, "time": None, "stdout": ""}
_last_capture: datetime.datetime | None = None


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
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
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
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]
        if path == "/wccs":
            self._handle_wccs()
        elif path == "/capture":
            self._handle_capture()
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
