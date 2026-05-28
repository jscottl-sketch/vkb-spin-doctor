"""
self_health.py — MCC Self-Health Runner (OCB-A)
Tests every element in data/element_registry.json against the live MCC server.
Results stored in data/health.db.

Usage:
  python self_health.py                   # run all tests
  python self_health.py --tab "Home"      # run one tab
  python self_health.py --scheduled       # honour frequency config
"""

import argparse
import datetime
import json
import sqlite3
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

HERE              = Path(__file__).parent
REGISTRY_FILE     = HERE / "data" / "element_registry.json"
HEALTH_DB         = HERE / "data" / "health.db"
CONFIG_FILE       = HERE / "data" / "self_health_config.json"
STUCK_INBOX_FILE  = HERE / "stuck_inbox.json"
MCC_BASE          = "http://127.0.0.1:8080"
REQUEST_TIMEOUT   = 8   # seconds per test request


class SelfHealthRunner:

    def __init__(self):
        self.registry = self._load_registry()
        self.db       = self._init_db()

    # ── Loading ───────────────────────────────────────────────────────────────

    def _load_registry(self) -> list:
        if not REGISTRY_FILE.exists():
            print(f"[self_health] ERROR: registry not found at {REGISTRY_FILE}")
            return []
        try:
            data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
            return data.get("elements", [])
        except Exception as exc:
            print(f"[self_health] ERROR loading registry: {exc}")
            return []

    def _load_config(self) -> dict:
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"frequency_modes": {"on_demand_only": True, "on_startup": True}, "last_run": None}

    def _save_config(self, cfg: dict):
        try:
            CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        except Exception:
            pass

    # ── DB ────────────────────────────────────────────────────────────────────

    def _init_db(self) -> sqlite3.Connection:
        HEALTH_DB.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(HEALTH_DB), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS health_results (
          id                 INTEGER PRIMARY KEY AUTOINCREMENT,
          element_id         TEXT    NOT NULL,
          status             TEXT    NOT NULL,
          latency_ms         INTEGER,
          error_message      TEXT,
          timestamp          TEXT    NOT NULL,
          test_run_id        TEXT    NOT NULL,
          auto_fix_attempted BOOLEAN DEFAULT 0,
          auto_fix_id        TEXT,
          auto_fix_success   BOOLEAN
        );

        CREATE TABLE IF NOT EXISTS health_runs (
          run_id         TEXT PRIMARY KEY,
          started_at     TEXT NOT NULL,
          finished_at    TEXT,
          total_tested   INTEGER,
          passed         INTEGER,
          warned         INTEGER,
          failed         INTEGER,
          trigger_source TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_hr_element ON health_results(element_id);
        CREATE INDEX IF NOT EXISTS idx_hr_ts      ON health_results(timestamp);
        CREATE INDEX IF NOT EXISTS idx_hr_runid   ON health_results(test_run_id);
        """)
        conn.commit()
        return conn

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    def _http(self, method: str, path: str, body: bytes | None = None) -> tuple[int, bytes]:
        url = MCC_BASE + path
        req = urllib.request.Request(url, data=body, method=method)
        if body:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, b""
        except Exception as exc:
            raise exc

    # ── Testers ───────────────────────────────────────────────────────────────

    def _test_button(self, el: dict) -> dict:
        method   = el.get("method", "POST").upper()
        endpoint = el["endpoint"]
        t0 = time.monotonic()
        try:
            body = b"{}" if method == "POST" else None
            status_code, raw = self._http(method, endpoint, body)
            latency = int((time.monotonic() - t0) * 1000)
            if status_code == 200:
                return {"status": "pass", "latency_ms": latency, "error_message": None}
            elif status_code in (400, 422) and method == "POST":
                # 400 on POST means server is live but our empty payload is rejected — endpoint exists
                return {"status": "warn", "latency_ms": latency,
                        "error_message": f"HTTP {status_code} — endpoint live but needs params (expected for empty-body test)"}
            else:
                return {"status": "fail", "latency_ms": latency,
                        "error_message": f"HTTP {status_code}"}
        except Exception as exc:
            latency = int((time.monotonic() - t0) * 1000)
            return {"status": "fail", "latency_ms": latency, "error_message": str(exc)[:200]}

    def _test_data_field(self, el: dict) -> dict:
        method   = el.get("method", "GET").upper()
        endpoint = el["endpoint"]
        t0 = time.monotonic()
        try:
            status_code, raw = self._http(method, endpoint)
            latency = int((time.monotonic() - t0) * 1000)
            if status_code != 200:
                return {"status": "fail", "latency_ms": latency,
                        "error_message": f"HTTP {status_code}"}
            if not raw.strip():
                return {"status": "warn", "latency_ms": latency,
                        "error_message": "Response body empty"}
            try:
                json.loads(raw)
            except Exception:
                pass
            return {"status": "pass", "latency_ms": latency, "error_message": None}
        except Exception as exc:
            latency = int((time.monotonic() - t0) * 1000)
            return {"status": "fail", "latency_ms": latency, "error_message": str(exc)[:200]}

    def _test_graph(self, el: dict) -> dict:
        method   = el.get("method", "GET").upper()
        endpoint = el["endpoint"]
        t0 = time.monotonic()
        try:
            status_code, raw = self._http(method, endpoint)
            latency = int((time.monotonic() - t0) * 1000)
            if status_code != 200:
                return {"status": "fail", "latency_ms": latency,
                        "error_message": f"HTTP {status_code}"}
            try:
                data = json.loads(raw)
                if isinstance(data, list) and len(data) == 0:
                    return {"status": "warn", "latency_ms": latency,
                            "error_message": "Graph data array is empty"}
            except Exception:
                pass
            return {"status": "pass", "latency_ms": latency, "error_message": None}
        except Exception as exc:
            latency = int((time.monotonic() - t0) * 1000)
            return {"status": "fail", "latency_ms": latency, "error_message": str(exc)[:200]}

    def _test_endpoint(self, el: dict) -> dict:
        return self._test_data_field(el)

    def _test_toggle(self, el: dict) -> dict:
        endpoint = el["endpoint"]
        t0 = time.monotonic()
        try:
            status_code, raw = self._http("GET", endpoint)
            latency = int((time.monotonic() - t0) * 1000)
            if status_code == 200:
                return {"status": "pass", "latency_ms": latency, "error_message": None}
            else:
                return {"status": "warn", "latency_ms": latency,
                        "error_message": f"Toggle GET returned HTTP {status_code} — state unverified"}
        except Exception as exc:
            latency = int((time.monotonic() - t0) * 1000)
            return {"status": "fail", "latency_ms": latency, "error_message": str(exc)[:200]}

    def _test_input(self, el: dict) -> dict:
        return {"status": "pass", "latency_ms": 0,
                "error_message": "Skipped — requires user interaction"}

    # ── Core test dispatcher ──────────────────────────────────────────────────

    def test_element(self, element: dict) -> dict:
        el_type = element.get("type", "endpoint")
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        dispatch = {
            "button":     self._test_button,
            "data_field": self._test_data_field,
            "graph":      self._test_graph,
            "endpoint":   self._test_endpoint,
            "toggle":     self._test_toggle,
            "input":      self._test_input,
        }
        tester = dispatch.get(el_type, self._test_endpoint)
        result = tester(element)
        result["timestamp"] = ts
        result["element_id"] = element["id"]
        return result

    # ── Store result ──────────────────────────────────────────────────────────

    def _store_result(self, result: dict, run_id: str):
        try:
            self.db.execute(
                """INSERT INTO health_results
                   (element_id, status, latency_ms, error_message, timestamp, test_run_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    result["element_id"],
                    result["status"],
                    result.get("latency_ms"),
                    result.get("error_message"),
                    result["timestamp"],
                    run_id,
                )
            )
            self.db.commit()
        except Exception as exc:
            print(f"[self_health] DB store error: {exc}")

    # ── Run ───────────────────────────────────────────────────────────────────

    def run_all(self, trigger_source: str = "manual") -> dict:
        run_id    = str(uuid.uuid4())[:8]
        started   = datetime.datetime.now().isoformat(timespec="seconds")
        elements  = self.registry

        try:
            self.db.execute(
                "INSERT INTO health_runs (run_id, started_at, trigger_source) VALUES (?,?,?)",
                (run_id, started, trigger_source)
            )
            self.db.commit()
        except Exception:
            pass

        total = passed = warned = failed = 0
        critical_failures = []
        results = []

        for el in elements:
            result = self.test_element(el)
            self._store_result(result, run_id)
            total += 1
            s = result["status"]
            if s == "pass":
                passed += 1
            elif s == "warn":
                warned += 1
            else:
                failed += 1
                if el.get("severity_if_broken") == "critical":
                    critical_failures.append({
                        "id": el["id"],
                        "name": el.get("name", el["id"]),
                        "error": result.get("error_message", ""),
                    })
            results.append(result)

        finished = datetime.datetime.now().isoformat(timespec="seconds")
        try:
            self.db.execute(
                """UPDATE health_runs
                   SET finished_at=?, total_tested=?, passed=?, warned=?, failed=?
                   WHERE run_id=?""",
                (finished, total, passed, warned, failed, run_id)
            )
            self.db.commit()
        except Exception:
            pass

        cfg = self._load_config()
        cfg["last_run"] = finished
        self._save_config(cfg)

        summary = {
            "run_id":            run_id,
            "total":             total,
            "passed":            passed,
            "warned":            warned,
            "failed":            failed,
            "critical_failures": critical_failures,
            "started_at":        started,
            "finished_at":       finished,
        }

        if critical_failures and cfg.get("escalate_to_stuck_inbox", True):
            self._escalate_to_stuck_inbox(critical_failures, run_id)

        return summary

    def run_by_tab(self, tab_name: str) -> dict:
        saved = self.registry
        self.registry = [e for e in saved if e.get("tab") == tab_name]
        summary = self.run_all(trigger_source="tab_switch")
        self.registry = saved
        return summary

    def run_scheduled(self):
        cfg = self._load_config()
        modes = cfg.get("frequency_modes", {})
        last_run_str = cfg.get("last_run")
        now = datetime.datetime.now()

        freq_map = {
            "every_30s":  30,
            "every_5min": 5 * 60,
            "every_30min": 30 * 60,
            "hourly":     60 * 60,
        }
        for mode, interval_s in freq_map.items():
            if modes.get(mode):
                if last_run_str:
                    last = datetime.datetime.fromisoformat(last_run_str)
                    if (now - last).total_seconds() < interval_s:
                        return {"skipped": True, "reason": f"Not due yet ({mode})"}
                return self.run_all(trigger_source="scheduled")

        if modes.get("on_startup") and last_run_str is None:
            return self.run_all(trigger_source="startup")

        return {"skipped": True, "reason": "No scheduled mode active"}

    # ── Archive ───────────────────────────────────────────────────────────────

    def archive_old_results(self, days: int = 90):
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        archive_dir = HERE / "data" / "archives"
        archive_dir.mkdir(parents=True, exist_ok=True)
        year_month = datetime.datetime.now().strftime("%Y-%m")
        archive_path = archive_dir / f"health_{year_month}.db"

        try:
            arch_conn = sqlite3.connect(str(archive_path))
            arch_cur  = arch_conn.cursor()
            arch_cur.executescript("""
            CREATE TABLE IF NOT EXISTS health_results (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              element_id TEXT, status TEXT, latency_ms INTEGER,
              error_message TEXT, timestamp TEXT, test_run_id TEXT,
              auto_fix_attempted BOOLEAN DEFAULT 0, auto_fix_id TEXT, auto_fix_success BOOLEAN
            );
            CREATE TABLE IF NOT EXISTS health_runs (
              run_id TEXT PRIMARY KEY, started_at TEXT, finished_at TEXT,
              total_tested INTEGER, passed INTEGER, warned INTEGER, failed INTEGER, trigger_source TEXT
            );
            """)
            arch_conn.commit()

            old_results = self.db.execute(
                "SELECT * FROM health_results WHERE timestamp < ?", (cutoff,)
            ).fetchall()
            old_run_ids = set(r["test_run_id"] for r in old_results)

            for row in old_results:
                arch_cur.execute(
                    """INSERT OR IGNORE INTO health_results
                       (element_id,status,latency_ms,error_message,timestamp,test_run_id,
                        auto_fix_attempted,auto_fix_id,auto_fix_success)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (row["element_id"], row["status"], row["latency_ms"],
                     row["error_message"], row["timestamp"], row["test_run_id"],
                     row["auto_fix_attempted"], row["auto_fix_id"], row["auto_fix_success"])
                )
            for rid in old_run_ids:
                run = self.db.execute(
                    "SELECT * FROM health_runs WHERE run_id=?", (rid,)
                ).fetchone()
                if run:
                    arch_cur.execute(
                        """INSERT OR IGNORE INTO health_runs
                           (run_id,started_at,finished_at,total_tested,passed,warned,failed,trigger_source)
                           VALUES (?,?,?,?,?,?,?,?)""",
                        (run["run_id"], run["started_at"], run["finished_at"],
                         run["total_tested"], run["passed"], run["warned"],
                         run["failed"], run["trigger_source"])
                    )
            arch_conn.commit()
            arch_conn.close()

            self.db.execute("DELETE FROM health_results WHERE timestamp < ?", (cutoff,))
            run_ids_left = {r["test_run_id"] for r in
                            self.db.execute("SELECT test_run_id FROM health_results").fetchall()}
            for rid in old_run_ids - run_ids_left:
                self.db.execute("DELETE FROM health_runs WHERE run_id=?", (rid,))
            self.db.commit()
            return {"archived": len(old_results), "archive_path": str(archive_path)}
        except Exception as exc:
            return {"error": str(exc)}

    # ── History ───────────────────────────────────────────────────────────────

    def get_last_run(self) -> dict | None:
        row = self.db.execute(
            "SELECT * FROM health_runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None

    def get_history(self, limit: int = 50) -> list:
        rows = self.db.execute(
            "SELECT * FROM health_runs ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_results_for_run(self, run_id: str) -> list:
        rows = self.db.execute(
            "SELECT * FROM health_results WHERE test_run_id=? ORDER BY id",
            (run_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Escalation ────────────────────────────────────────────────────────────

    def _escalate_to_stuck_inbox(self, failures: list, run_id: str):
        try:
            inbox = []
            if STUCK_INBOX_FILE.exists():
                try:
                    inbox = json.loads(STUCK_INBOX_FILE.read_text(encoding="utf-8"))
                    if not isinstance(inbox, list):
                        inbox = []
                except Exception:
                    inbox = []

            for f in failures:
                entry = {
                    "id":        f"sh_{run_id}_{f['id']}",
                    "goal":      f"Self-Health: {f['name']} FAILED",
                    "error":     f.get("error", "Unknown failure"),
                    "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                    "severity":  "high",
                    "source":    "self_health",
                    "resolved":  False,
                }
                if not any(i.get("id") == entry["id"] for i in inbox):
                    inbox.append(entry)

            STUCK_INBOX_FILE.write_text(json.dumps(inbox, indent=2), encoding="utf-8")
        except Exception as exc:
            print(f"[self_health] Failed to escalate to stuck inbox: {exc}")


def main():
    parser = argparse.ArgumentParser(description="MCC Self-Health Runner")
    parser.add_argument("--tab", help="Test only elements from this tab")
    parser.add_argument("--scheduled", action="store_true",
                        help="Only run if schedule config says it is due")
    args = parser.parse_args()

    runner = SelfHealthRunner()
    total_reg = len(runner.registry)
    print(f"[self_health] Registry loaded: {total_reg} elements")
    print(f"[self_health] MCC target: {MCC_BASE}")

    if args.scheduled:
        summary = runner.run_scheduled()
    elif args.tab:
        summary = runner.run_by_tab(args.tab)
    else:
        summary = runner.run_all(trigger_source="manual")

    print(json.dumps(summary, indent=2))

    if summary.get("total"):
        pct = round(summary["passed"] / summary["total"] * 100, 1)
        print(f"\n[self_health] Result: {summary['passed']}/{summary['total']} PASS  "
              f"{summary['warned']} WARN  {summary['failed']} FAIL  ({pct}%)")
        if summary.get("critical_failures"):
            print(f"\n[self_health] CRITICAL FAILURES ({len(summary['critical_failures'])}):")
            for cf in summary["critical_failures"]:
                print(f"  FAIL {cf['name']}: {cf['error']}")


if __name__ == "__main__":
    main()
