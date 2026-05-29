"""
provider_health.py — AAFL Provider Health Monitor
Features 1-10 across Tier 1, Tier 2, Tier 3.

Run standalone: python provider_health.py
"""
import csv
import json
import os
import shutil
import sqlite3
import tempfile
import time
import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

import litellm
litellm.set_verbose = False
litellm.suppress_debug_info = True

from aafl_core import PROVIDERS, _check_lmstudio

HERE          = Path(__file__).parent
HEALTH_DIR    = HERE / "health_results"
COST_LOG      = HEALTH_DIR / "cost_log.csv"
LATEST_JSON   = HEALTH_DIR / "latest_health.json"
DB_PATH       = HERE / "data" / "knowledge_engine.db"

ALIVE_TIMEOUT    = 15   # seconds
SPEED_GREEN      = 10   # seconds
SPEED_YELLOW     = 30   # seconds
COOLING_MINUTES  = 60   # minutes

# ── Module-level cooling registry ─────────────────────────────────────────────
_cooling_registry: dict[str, datetime.datetime] = {}


# ── DB helpers ─────────────────────────────────────────────────────────────────

def _db_connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_reputation_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS provider_reputation (
            provider_name      TEXT PRIMARY KEY,
            total_calls        INTEGER NOT NULL DEFAULT 0,
            successful_calls   INTEGER NOT NULL DEFAULT 0,
            failed_calls       INTEGER NOT NULL DEFAULT 0,
            avg_response_time  REAL    NOT NULL DEFAULT 0.0,
            last_updated       TEXT    NOT NULL DEFAULT ''
        )
    """)
    conn.commit()


# ── Key check (mirrors aafl_core) ──────────────────────────────────────────────

def _has_key(p: dict) -> bool:
    if p.get("api_key_env") is None:
        return True
    if not os.environ.get(p["api_key_env"], "").strip():
        return False
    extra = p.get("extra_env")
    if extra and not os.environ.get(extra, "").strip():
        return False
    return True


# ── Low-level call ─────────────────────────────────────────────────────────────

def _raw_call(p: dict, prompt: str, timeout: int = ALIVE_TIMEOUT) -> tuple[str, float]:
    """Returns (response_text, cost_usd). Raises on error."""
    api_key = (p.get("api_key")
               or os.environ.get(p.get("api_key_env") or "", "")
               or "")

    if p.get("id") == "huggingface" and api_key:
        os.environ.setdefault("HUGGINGFACE_API_KEY", api_key)

    if p.get("embed_only"):
        raise ValueError("embed-only provider — skipped in health checks")

    messages = [{"role": "user", "content": prompt}]
    kwargs = dict(
        model=p["model"],
        messages=messages,
        max_tokens=32,
        timeout=timeout,
    )
    if p.get("api_base"):
        kwargs["api_base"] = p["api_base"]
    if api_key:
        kwargs["api_key"] = api_key

    resp = litellm.completion(**kwargs)
    text = (resp.choices[0].message.content or "").strip()
    try:
        cost = litellm.completion_cost(completion_response=resp)
    except Exception:
        cost = p.get("cost_per_call_usd", 0.0)
    return text, cost


# ── Feature 1 + 2: Alive Check + Speed Test ───────────────────────────────────

def check_alive(p: dict) -> dict:
    """
    Returns dict with keys: alive (bool), response_time (float),
    speed_color (GREEN/YELLOW/RED), error (str|None), response (str).
    """
    t0 = time.time()
    try:
        text, _ = _raw_call(p, "Respond with the single word OK and nothing else", ALIVE_TIMEOUT)
        elapsed = round(time.time() - t0, 2)
        if elapsed <= SPEED_GREEN:
            color = "GREEN"
        elif elapsed <= SPEED_YELLOW:
            color = "YELLOW"
        else:
            color = "RED"
        return {
            "alive": True,
            "response_time": elapsed,
            "speed_color": color,
            "error": None,
            "response": text,
        }
    except Exception as exc:
        elapsed = round(time.time() - t0, 2)
        msg = str(exc)
        return {
            "alive": False,
            "response_time": elapsed,
            "speed_color": "RED",
            "error": msg,
            "response": "",
        }


# ── Feature 3: Quality Test ────────────────────────────────────────────────────

def check_quality(p: dict) -> dict:
    """Returns dict with keys: quality_pass (bool), quality_response (str), error (str|None)."""
    try:
        text, _ = _raw_call(p, "What is 2+2? Reply with the number only.", ALIVE_TIMEOUT)
        passed = "4" in text
        return {"quality_pass": passed, "quality_response": text, "error": None}
    except Exception as exc:
        return {"quality_pass": False, "quality_response": "", "error": str(exc)}


# ── Feature 4: Rate Limit Detector ────────────────────────────────────────────

def _is_rate_limit_error(msg: str) -> bool:
    low = msg.lower()
    return ("429" in msg or "rate limit" in low or "ratelimit" in low
            or "too many requests" in low or "rateLimitError" in msg)


def mark_cooling(provider_id: str):
    _cooling_registry[provider_id] = datetime.datetime.now()


def is_cooling(provider_id: str) -> bool:
    ts = _cooling_registry.get(provider_id)
    if ts is None:
        return False
    elapsed = (datetime.datetime.now() - ts).total_seconds() / 60
    return elapsed < COOLING_MINUTES


def check_with_rate_limit_detection(p: dict) -> dict:
    """
    Wraps check_alive. Detects 429/rate-limit and marks provider COOLING.
    Returns merged result dict with 'cooling' key.
    """
    result = check_alive(p)
    if result["error"] and _is_rate_limit_error(result["error"]):
        mark_cooling(p["id"])
        result["cooling"] = True
    else:
        result["cooling"] = is_cooling(p["id"])
    return result


# ── Feature 5: Pre-Run Report ─────────────────────────────────────────────────

def run_health_checks(providers=None, skip_paid=True) -> list[dict]:
    """
    Run health checks on all testable providers.
    Returns list of result dicts, one per provider.
    """
    HEALTH_DIR.mkdir(exist_ok=True)
    lm_up = _check_lmstudio()
    results = []

    targets = providers or PROVIDERS
    for p in targets:
        pid = p["id"]

        if p.get("embed_only"):
            results.append({
                "id": pid, "label": p["label"], "tier": p["tier"],
                "alive": False, "response_time": 0.0,
                "speed_color": "DEAD", "cooling": False,
                "quality_pass": False, "quality_response": "",
                "status": "SKIP", "error": "embed-only provider",
                "score": 0, "cost_usd": 0.0,
            })
            continue

        if skip_paid and p.get("paid"):
            results.append({
                "id": pid, "label": p["label"], "tier": p["tier"],
                "alive": False, "response_time": 0.0,
                "speed_color": "DEAD", "cooling": False,
                "quality_pass": False, "quality_response": "",
                "status": "SKIP", "error": "paid provider blocked",
                "score": 0, "cost_usd": 0.0,
            })
            continue

        if not _has_key(p):
            results.append({
                "id": pid, "label": p["label"], "tier": p["tier"],
                "alive": False, "response_time": 0.0,
                "speed_color": "DEAD", "cooling": False,
                "quality_pass": False, "quality_response": "",
                "status": "NO_KEY", "error": "no API key",
                "score": 0, "cost_usd": 0.0,
            })
            continue

        is_local = "127.0.0.1" in (p.get("api_base") or "")
        if is_local and not lm_up:
            results.append({
                "id": pid, "label": p["label"], "tier": p["tier"],
                "alive": False, "response_time": 0.0,
                "speed_color": "DEAD", "cooling": False,
                "quality_pass": False, "quality_response": "",
                "status": "DEAD", "error": "LM Studio not running",
                "score": 0, "cost_usd": 0.0,
            })
            continue

        if is_cooling(pid):
            results.append({
                "id": pid, "label": p["label"], "tier": p["tier"],
                "alive": False, "response_time": 0.0,
                "speed_color": "COOLING", "cooling": True,
                "quality_pass": False, "quality_response": "",
                "status": "COOLING", "error": "rate-limited",
                "score": 0, "cost_usd": 0.0,
            })
            continue

        print(f"  Checking {p['label']} ... ", end="", flush=True)
        alive_result = check_with_rate_limit_detection(p)

        if alive_result["cooling"]:
            print("COOLING (rate limited)")
            row = {**alive_result, "id": pid, "label": p["label"], "tier": p["tier"],
                   "quality_pass": False, "quality_response": "",
                   "status": "COOLING", "score": 0, "cost_usd": 0.0}
            results.append(row)
            _log_cost(pid, alive_result["response_time"], 0.0, False)
            continue

        if not alive_result["alive"]:
            print(f"DEAD ({alive_result['error'][:50] if alive_result['error'] else ''})")
            row = {**alive_result, "id": pid, "label": p["label"], "tier": p["tier"],
                   "quality_pass": False, "quality_response": "",
                   "status": "DEAD", "score": 0, "cost_usd": 0.0}
            results.append(row)
            _log_cost(pid, alive_result["response_time"], 0.0, False)
            continue

        quality_result = check_quality(p)
        color = alive_result["speed_color"]
        speed_pts   = 40 if color == "GREEN" else (20 if color == "YELLOW" else 5)
        quality_pts = 40 if quality_result["quality_pass"] else 0
        alive_pts   = 20
        score = speed_pts + quality_pts + alive_pts

        status = color  # GREEN / YELLOW / RED

        cost_usd = p.get("cost_per_call_usd", 0.0) * 2  # two calls (alive + quality)

        print(f"{color} | quality={'PASS' if quality_result['quality_pass'] else 'FAIL'} | score={score}")

        row = {
            "id": pid,
            "label": p["label"],
            "tier": p["tier"],
            "alive": True,
            "response_time": alive_result["response_time"],
            "speed_color": color,
            "cooling": False,
            "quality_pass": quality_result["quality_pass"],
            "quality_response": quality_result["quality_response"],
            "status": status,
            "error": None,
            "score": score,
            "cost_usd": cost_usd,
        }
        results.append(row)

        # Log cost for each of the 2 calls made
        _log_cost(pid, alive_result["response_time"], cost_usd / 2, True)
        _log_cost(pid, 0.0, 0.0, quality_result["quality_pass"])

    # Update reputation after every run
    _update_reputation(results)

    # Write latest_health.json
    _write_latest_json(results)

    # Update session_state provider_health
    healthy_n = sum(1 for r in results if r.get("alive"))
    _update_session_state({"provider_health": {
        "healthy_count": healthy_n,
        "total": len(results),
        "last_checked": datetime.datetime.now().isoformat(timespec="seconds"),
    }})

    return results


def print_pre_run_report(results: list[dict]):
    """Feature 5 — formatted summary after all checks complete."""
    total      = len([r for r in results if r["status"] not in ("SKIP",)])
    green      = [r for r in results if r["status"] == "GREEN"]
    yellow     = [r for r in results if r["status"] == "YELLOW"]
    red        = [r for r in results if r["status"] == "RED"]
    cooling    = [r for r in results if r["status"] == "COOLING"]
    dead       = [r for r in results if r["status"] in ("DEAD", "NO_KEY")]
    available  = green + yellow

    est_cost = sum(p.get("cost_per_call_usd", 0.0)
                   for p in PROVIDERS
                   if any(r["id"] == p["id"] for r in available))

    print()
    print("=" * 64)
    print("  PROVIDER HEALTH — PRE-RUN REPORT")
    print("=" * 64)
    print(f"  Total checked : {total}")
    print(f"  GREEN         : {len(green)}")
    print(f"  YELLOW        : {len(yellow)}")
    print(f"  RED           : {len(red)}")
    print(f"  COOLING       : {len(cooling)}")
    print(f"  DEAD/NO_KEY   : {len(dead)}")
    print()
    print("  Available for work (GREEN + YELLOW):")
    if available:
        for r in sorted(available, key=lambda x: -x["score"]):
            rep = get_reputation(r["id"])
            print(f"    [{r['status']:<6}] {r['label']:<35} score={r['score']}  rep={rep:.0f}%  {r['response_time']}s")
    else:
        print("    (none)")
    print()
    print(f"  Estimated cost if all available do 1 small task: ${est_cost:.5f}")
    if cooling:
        print()
        print("  COOLING providers (skipped — rate limited):")
        for r in cooling:
            print(f"    {r['label']}")
    if dead:
        print()
        print("  DEAD / NO_KEY providers:")
        for r in dead:
            print(f"    {r['label']}  ({r['error'] or ''})")
    print("=" * 64)
    print()


# ── Feature 6: Best Worker Picker ─────────────────────────────────────────────

def rank_providers(results: list[dict]) -> list[dict]:
    """Sort available providers by score descending. Returns only ALIVE, non-COOLING."""
    available = [r for r in results if r["alive"] and not r["cooling"]]
    return sorted(available, key=lambda r: -r["score"])


# ── Feature 7: Reputation Score ───────────────────────────────────────────────

def _update_reputation(results: list[dict]):
    try:
        conn = _db_connect()
        _ensure_reputation_table(conn)
        now = datetime.datetime.utcnow().isoformat()
        for r in results:
            if r["status"] in ("SKIP", "NO_KEY"):
                continue
            pid   = r["id"]
            ok    = 1 if r["alive"] else 0
            fail  = 0 if r["alive"] else 1
            rt    = r["response_time"]
            row = conn.execute(
                "SELECT * FROM provider_reputation WHERE provider_name=?", (pid,)
            ).fetchone()
            if row:
                tc   = row["total_calls"] + 1
                sc   = row["successful_calls"] + ok
                fc   = row["failed_calls"] + fail
                # rolling average of response time
                avg_rt = round(
                    (row["avg_response_time"] * row["total_calls"] + rt) / tc, 3
                )
                conn.execute(
                    """UPDATE provider_reputation
                       SET total_calls=?, successful_calls=?, failed_calls=?,
                           avg_response_time=?, last_updated=?
                       WHERE provider_name=?""",
                    (tc, sc, fc, avg_rt, now, pid),
                )
            else:
                conn.execute(
                    """INSERT INTO provider_reputation
                       (provider_name, total_calls, successful_calls, failed_calls,
                        avg_response_time, last_updated)
                       VALUES (?,?,?,?,?,?)""",
                    (pid, 1, ok, fail, rt, now),
                )
        conn.commit()
        conn.close()
    except Exception as exc:
        print(f"[health] reputation update failed: {exc}")


def get_reputation(provider_name: str) -> float:
    """Returns success rate as a percentage (0.0 – 100.0). Returns 0 if unknown."""
    try:
        conn = _db_connect()
        _ensure_reputation_table(conn)
        row = conn.execute(
            "SELECT total_calls, successful_calls FROM provider_reputation WHERE provider_name=?",
            (provider_name,),
        ).fetchone()
        conn.close()
        if row and row["total_calls"] > 0:
            return round(row["successful_calls"] / row["total_calls"] * 100, 1)
        return 0.0
    except Exception:
        return 0.0


# ── Feature 8: Auto Retry ─────────────────────────────────────────────────────

def run_with_retry(prompt: str, max_attempts: int = 3,
                   results: Optional[list] = None) -> Optional[dict]:
    """
    Try providers in score order. Skip DEAD and COOLING.
    Returns first successful response as dict, or None if all fail.
    """
    if results is None:
        print("[health] Running health checks for auto-retry ...")
        results = run_health_checks()

    ranked = rank_providers(results)
    if not ranked:
        print("[health] No available providers for retry.")
        return None

    attempts = 0
    for r in ranked:
        if attempts >= max_attempts:
            break
        p = next((x for x in PROVIDERS if x["id"] == r["id"]), None)
        if p is None:
            continue
        attempts += 1
        print(f"[health] Attempt {attempts}/{max_attempts} -> {p['label']}")
        try:
            t0   = time.time()
            text, cost = _raw_call(p, prompt)
            elapsed = round(time.time() - t0, 2)
            if text and text.strip():
                print(f"[health] Success on attempt {attempts} ({p['label']}, {elapsed}s)")
                _log_cost(p["id"], elapsed, cost, True)
                return {"provider": p["id"], "label": p["label"],
                        "response": text, "elapsed": elapsed,
                        "cost_usd": cost, "attempt": attempts}
            else:
                raise ValueError("empty response")
        except Exception as exc:
            msg = str(exc)
            print(f"[health] Attempt {attempts} FAILED ({p['label']}): {msg[:80]}")
            if _is_rate_limit_error(msg):
                mark_cooling(p["id"])
            _log_cost(p["id"], 0.0, 0.0, False)
            continue

    print("[health] All retry attempts exhausted.")
    return None


# ── Feature 9: Cost Logger ────────────────────────────────────────────────────

def _log_cost(provider_name: str, response_time: float,
              cost_usd: float, success: bool):
    HEALTH_DIR.mkdir(exist_ok=True)
    write_header = not COST_LOG.exists()
    try:
        with open(COST_LOG, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow([
                    "timestamp", "provider_name", "response_time_seconds",
                    "estimated_cost_usd", "success"
                ])
            writer.writerow([
                datetime.datetime.now().isoformat(),
                provider_name,
                round(response_time, 3),
                round(cost_usd, 6),
                str(success).lower(),
            ])
    except Exception as exc:
        print(f"[health] cost log write failed: {exc}")


# ── Feature 10: Write latest_health.json ─────────────────────────────────────

def _write_latest_json(results: list[dict]):
    HEALTH_DIR.mkdir(exist_ok=True)
    payload = {
        "generated_at": datetime.datetime.now().isoformat(),
        "providers": [],
    }
    for r in results:
        rep = get_reputation(r["id"])
        conn = None
        total_calls = 0
        try:
            conn = _db_connect()
            _ensure_reputation_table(conn)
            row = conn.execute(
                "SELECT total_calls FROM provider_reputation WHERE provider_name=?",
                (r["id"],),
            ).fetchone()
            if row:
                total_calls = row["total_calls"]
        except Exception:
            pass
        finally:
            if conn:
                conn.close()

        payload["providers"].append({
            "id":             r["id"],
            "label":          r["label"],
            "tier":           r["tier"],
            "status":         r["status"],
            "response_time":  r["response_time"],
            "quality_pass":   r["quality_pass"],
            "score":          r["score"],
            "reputation_pct": rep,
            "total_calls":    total_calls,
            "error":          r.get("error"),
        })
    try:
        LATEST_JSON.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as exc:
        print(f"[health] latest_health.json write failed: {exc}")


# ── Session State helper ──────────────────────────────────────────────────────

_SESSION_STATE = HERE / "data" / "session_state.json"
_SS_DEFAULTS = {
    "session_id": "", "started_at": "",
    "current_task": {"type": "", "description": "", "subsystem": "", "status": "idle", "started_at": ""},
    "last_result": {"task": "", "status": "", "mot_score": "", "files_changed": [], "completed_at": ""},
    "provider_health": {"healthy_count": 0, "total": 14, "last_checked": ""},
    "watchdog_status": "OFF",
    "last_save": {"type": "", "timestamp": "", "file": ""},
    "aafl_score": None, "cost_7d": None, "active_ocb_run_id": "", "next_priority": "",
}


def _update_session_state(patch: dict):
    """Merge patch into data/session_state.json (atomic write, never full overwrite)."""
    try:
        state = json.loads(_SESSION_STATE.read_text(encoding="utf-8")) if _SESSION_STATE.exists() else dict(_SS_DEFAULTS)
        state.update(patch)
        fd, tmp = tempfile.mkstemp(dir=str(_SESSION_STATE.parent), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        shutil.move(tmp, str(_SESSION_STATE))
    except Exception:
        pass


# ── Diagnosis ─────────────────────────────────────────────────────────────────

def run_diagnosis(providers=None) -> dict:
    """
    Minimal live test of each provider with prompt 'reply OK'.
    Writes result to data/provider_diagnosis.json (atomic).
    Returns {healthy, total, failures, providers}.
    """
    targets = providers or PROVIDERS
    lm_up = _check_lmstudio()
    results = {}
    healthy_count = 0
    failures = []

    for p in targets:
        pid = p["id"]
        tier = p.get("tier", 2)
        model = p["model"]

        if p.get("embed_only"):
            results[pid] = {"status": "SKIP", "latency_ms": 0, "error": "embed-only",
                            "model_used": model, "tier": tier}
            continue
        if p.get("paid"):
            results[pid] = {"status": "SKIP", "latency_ms": 0, "error": "paid provider blocked",
                            "model_used": model, "tier": tier}
            continue
        if not _has_key(p):
            results[pid] = {"status": "NO_KEY", "latency_ms": 0, "error": "no API key",
                            "model_used": model, "tier": tier}
            continue
        is_local = "127.0.0.1" in (p.get("api_base") or "")
        if is_local and not lm_up:
            results[pid] = {"status": "OFFLINE", "latency_ms": 0, "error": "LM Studio not running",
                            "model_used": model, "tier": tier}
            continue

        t0 = time.time()
        try:
            text, _ = _raw_call(p, "reply OK", timeout=15)
            latency = round((time.time() - t0) * 1000)
            results[pid] = {"status": "OK", "latency_ms": latency, "error": None,
                            "model_used": model, "tier": tier}
            healthy_count += 1
        except Exception as exc:
            latency = round((time.time() - t0) * 1000)
            err = str(exc)[:120]
            results[pid] = {"status": "FAIL", "latency_ms": latency, "error": err,
                            "model_used": model, "tier": tier}
            failures.append({"id": pid, "label": p.get("label", pid), "error": err})

    diagnosis = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "healthy": healthy_count,
        "total": len(targets),
        "failures": failures,
        "providers": results,
    }
    out = HERE / "data" / "provider_diagnosis.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(out.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(diagnosis, f, indent=2)
    shutil.move(tmp, str(out))
    return diagnosis


# ── Main CLI entry point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("=" * 64)
    print("  PROVIDER HEALTH CHECK")
    print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 64)
    print()
    results = run_health_checks()
    print_pre_run_report(results)
