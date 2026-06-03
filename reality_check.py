"""
reality_check.py — Standalone Reality Report generator (OCB-R+).
Produces docs/REALITY_REPORT.md + archives to docs/reality_history/.
Runs with or without mcc_server. All sections wrapped in try/except.
No new pip dependencies (psutil optional, skipped gracefully if absent).
"""
import datetime
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

HERE     = Path(__file__).parent
DOCS     = HERE / "docs"
OUT_FILE = DOCS / "REALITY_REPORT.md"
HIST_DIR = DOCS / "reality_history"
DATA_DIR = HERE / "data"

DOCS.mkdir(exist_ok=True)
HIST_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _stamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d_%H%M")


def _short(p: Path) -> str:
    try:
        return p.relative_to(HERE).as_posix()
    except Exception:
        return str(p)


def _ok(b: bool) -> str:
    return "YES" if b else "NO"


def _age(mtime: float) -> str:
    secs = datetime.datetime.now().timestamp() - mtime
    if secs < 3600:
        return f"{int(secs//60)}m ago"
    if secs < 86400:
        return f"{int(secs//3600)}h ago"
    return f"{int(secs//86400)}d ago"


# ── Parse STATUS.md for BUILT file names ─────────────────────────────────────

def _status_built_files() -> list:
    status = HERE / "STATUS.md"
    if not status.exists():
        return []
    text = status.read_text(encoding="utf-8", errors="replace")
    in_built = False
    files = []
    for line in text.splitlines():
        if re.search(r"CURRENT STATUS.+BUILT", line):
            in_built = True
        elif re.match(r"^##\s", line) and in_built:
            in_built = False
        if not in_built:
            continue
        # Match table cells that look like a .py filename
        m = re.search(r'`?([a-zA-Z_][a-zA-Z0-9_./-]*\.py)`?', line)
        if m:
            files.append(m.group(1))
    return list(dict.fromkeys(files))  # deduplicate, preserve order


# ── Section generators ────────────────────────────────────────────────────────

def sec_a() -> str:
    lines = ["## A. FILE EXISTENCE\n"]
    py_files = _status_built_files()
    if not py_files:
        return "".join(lines) + "_No .py files found in STATUS.md BUILT table._\n"
    lines.append("| File | Exists | Size | Last Modified |")
    lines.append("|---|---|---|---|")
    for name in py_files:
        p = HERE / name
        exists = p.exists()
        size   = f"{p.stat().st_size:,}B" if exists else "—"
        mtime  = _age(p.stat().st_mtime) if exists else "—"
        flag   = "" if (exists and p.stat().st_size > 0) else " ⚠️"
        lines.append(f"| {name}{flag} | {_ok(exists)} | {size} | {mtime} |")
    return "\n".join(lines) + "\n"


def sec_b() -> str:
    lines = ["## B. ENDPOINT HEALTH\n"]
    try:
        import http.client
        import urllib.parse
        # Grab all /api/* paths from mcc_server.py via grep
        srv = HERE / "mcc_server.py"
        endpoints = []
        if srv.exists():
            for line in srv.read_text(encoding="utf-8", errors="replace").splitlines():
                m = re.search(r'path\s*==\s*"(/api/[^"]+)"', line)
                if m:
                    endpoints.append(m.group(1))
        endpoints = list(dict.fromkeys(endpoints))[:30]  # cap at 30
        # Quick check if server is up
        try:
            conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=2)
            conn.request("GET", "/api/health")
            r = conn.getresponse()
            r.read()
            server_up = True
        except Exception:
            server_up = False

        if not server_up:
            lines.append("_mcc_server not running — endpoint ping skipped._\n")
            return "\n".join(lines)

        lines.append("| Endpoint | Code | ms |")
        lines.append("|---|---|---|")
        for ep in endpoints:
            try:
                import time
                conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=3)
                t0 = time.time()
                conn.request("GET", ep)
                resp = conn.getresponse()
                resp.read()
                ms = int((time.time() - t0) * 1000)
                flag = "" if resp.status == 200 else " ⚠️"
                lines.append(f"| {ep}{flag} | {resp.status} | {ms}ms |")
            except Exception as e:
                lines.append(f"| {ep} | ERR | {str(e)[:40]} |")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_c() -> str:
    lines = ["## C. DATABASE INTEGRITY\n"]
    lines.append("| File | Valid JSON | Size | Entries | Last Modified |")
    lines.append("|---|---|---|---|---|")
    json_files = sorted(DATA_DIR.glob("*.json")) if DATA_DIR.exists() else []
    if not json_files:
        return "\n".join(lines) + "\n_No JSON files in data/_\n"
    for p in json_files:
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
            obj = json.loads(raw)
            valid = "YES"
            count = len(obj) if isinstance(obj, (list, dict)) else "—"
        except Exception:
            valid = "NO ⚠️"
            count = "—"
        size  = f"{p.stat().st_size:,}B"
        mtime = _age(p.stat().st_mtime)
        lines.append(f"| {p.name} | {valid} | {size} | {count} | {mtime} |")
    return "\n".join(lines) + "\n"


def sec_d() -> str:
    lines = ["## D. PROVIDER STATUS\n"]
    try:
        ph = HERE / "health_results" / "latest_health.json"
        if not ph.exists():
            return "\n".join(lines) + "_No provider health data found._\n"
        data = json.loads(ph.read_text(encoding="utf-8"))
        lines.append("| Provider | Status | ms |")
        lines.append("|---|---|---|")
        results = data if isinstance(data, list) else data.get("results", [])
        for r in results:
            label  = r.get("label", r.get("id", "?"))
            ok     = r.get("ok", r.get("success", False))
            ms     = r.get("ms", "—")
            status = "🟢 GREEN" if ok else "🔴 RED"
            lines.append(f"| {label} | {status} | {ms} |")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_e() -> str:
    lines = ["## E. RECENT ERRORS (last 50)\n"]
    try:
        from error_logger import get_recent_errors
        errors = get_recent_errors(50)
        if not errors:
            return "\n".join(lines) + "_No errors logged yet._\n"
        by_comp: dict = {}
        for e in errors:
            comp = e.get("component", "unknown")
            by_comp.setdefault(comp, []).append(e)
        for comp, entries in by_comp.items():
            lines.append(f"\n**{comp}** ({len(entries)} entries)")
            lines.append("| Time | Severity | Message |")
            lines.append("|---|---|---|")
            for e in entries[:10]:
                msg = str(e.get("message",""))[:80].replace("|","¦")
                lines.append(f"| {e.get('ts','?')} | {e.get('severity','?')} | {msg} |")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_f() -> str:
    lines = ["## F. BEST/WORST AI (last 7 days)\n"]
    try:
        mr = HERE / "morning_report.md"
        if mr.exists():
            lines.append("**morning_report.md**")
            lines.append("```")
            lines.append(mr.read_text(encoding="utf-8", errors="replace")[:800])
            lines.append("```")
        mp_dir = HERE / "meta_proposals"
        if mp_dir.exists():
            proposals = sorted(mp_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
            if proposals:
                lines.append(f"\nLatest {len(proposals)} meta proposals:")
                for p in proposals:
                    lines.append(f"- {p.name} ({_age(p.stat().st_mtime)})")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_g() -> str:
    lines = ["## G. MOT FRESHNESS\n"]
    try:
        mot = HERE / "mcc_full_mot.py"
        if not mot.exists():
            return "\n".join(lines) + "_mcc_full_mot.py not found._\n"
        mtime = mot.stat().st_mtime
        age_h = (datetime.datetime.now().timestamp() - mtime) / 3600
        stale = age_h > 48
        lines.append(f"- Script last modified: {_age(mtime)}")
        lines.append(f"- Stale flag (>48h): {'⚠️ YES' if stale else 'NO'}")
        # Check if there's a recent MOT result stored
        ocb_prog = HERE / "data" / "ocb_progress.json"
        if ocb_prog.exists():
            try:
                prog = json.loads(ocb_prog.read_text(encoding="utf-8"))
                lines.append(f"- Last OCB progress: {prog.get('phase','?')} / score: {prog.get('mot_score','?')}")
            except Exception:
                pass
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_h() -> str:
    lines = ["## H. WCCS HEALTH\n"]
    try:
        wccs = HERE / "aafl_wccs.py"
        if not wccs.exists():
            return "\n".join(lines) + "_aafl_wccs.py not found._\n"
        lines.append(f"- aafl_wccs.py size: {wccs.stat().st_size:,}B, modified {_age(wccs.stat().st_mtime)}")
        err_log = HERE / "wccs_errors.log"
        if err_log.exists():
            lines.append(f"- wccs_errors.log: {err_log.stat().st_size:,}B ({_age(err_log.stat().st_mtime)})")
            tail = err_log.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-5:]
            if tail:
                lines.append("- Last 5 error lines:")
                for l in tail:
                    lines.append(f"  `{l[:100]}`")
        wccs_log = HERE / "wccs_log.md"
        if wccs_log.exists():
            lines.append(f"- wccs_log.md: {wccs_log.stat().st_size:,}B ({_age(wccs_log.stat().st_mtime)})")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_i() -> str:
    lines = ["## I. STATUS vs DISK CONTRADICTIONS\n"]
    try:
        py_files = _status_built_files()
        missing = [f for f in py_files if not (HERE / f).exists()]
        if not missing:
            lines.append("_No contradictions found — all BUILT files exist on disk._")
        else:
            lines.append("| File | Status says | Disk |")
            lines.append("|---|---|---|")
            for f in missing:
                lines.append(f"| {f} | BUILT | ⚠️ MISSING |")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_j(top5: list) -> str:
    lines = ["## J. TOP 5 ACTIONS\n"]
    if not top5:
        lines.append("_Nothing critical detected. All clear._")
    else:
        for i, item in enumerate(top5[:5], 1):
            lines.append(f"{i}. {item}")
    return "\n".join(lines) + "\n"


def sec_k() -> str:
    lines = ["## K. INSTALLED PACKAGES\n"]
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"],
                                capture_output=True, text=True, timeout=30)
        installed = {}
        if result.returncode == 0:
            for pkg in json.loads(result.stdout):
                installed[pkg["name"].lower()] = pkg["version"]
        req = HERE / "requirements.txt"
        if req.exists():
            req_pkgs = [l.strip().split("==")[0].split(">=")[0].lower()
                        for l in req.read_text().splitlines() if l.strip() and not l.startswith("#")]
        else:
            req_pkgs = []
        lines.append(f"- Installed packages: {len(installed)}")
        lines.append(f"- requirements.txt entries: {len(req_pkgs)}")
        if req_pkgs:
            lines.append("\n| Package | In requirements.txt | Installed | Version |")
            lines.append("|---|---|---|---|")
            for pkg in req_pkgs:
                inst = pkg in installed
                ver  = installed.get(pkg, "—")
                flag = "" if inst else " ⚠️ MISSING"
                lines.append(f"| {pkg}{flag} | YES | {_ok(inst)} | {ver} |")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_l() -> str:
    lines = ["## L. HIDDEN OR MISSING IMPORTS\n"]
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"],
                                capture_output=True, text=True, timeout=30)
        installed = set()
        if result.returncode == 0:
            for pkg in json.loads(result.stdout):
                installed.add(pkg["name"].lower())
        # Grep all import statements across project .py files
        import_map: dict = {}
        for pyf in HERE.glob("*.py"):
            try:
                for line in pyf.read_text(encoding="utf-8", errors="replace").splitlines():
                    m = re.match(r'^\s*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_.]*)', line)
                    if m:
                        mod = m.group(1).split(".")[0].lower()
                        import_map.setdefault(mod, set()).add(pyf.name)
            except Exception:
                pass
        stdlib = {
            "os","sys","re","json","time","math","copy","enum","abc","io","csv",
            "random","hashlib","hmac","base64","struct","array","queue","heapq",
            "collections","itertools","functools","operator","datetime","calendar",
            "decimal","fractions","statistics","pathlib","glob","fnmatch","shutil",
            "tempfile","fileinput","stat","filecmp","threading","multiprocessing",
            "concurrent","asyncio","socket","ssl","http","urllib","email","html",
            "xml","sqlite3","logging","unittest","pdb","traceback","inspect","ast",
            "dis","token","tokenize","keyword","types","typing","dataclasses",
            "contextlib","weakref","gc","platform","signal","subprocess","argparse",
            "configparser","getopt","getpass","readline","atexit","faulthandler",
            "ctypes","zipfile","tarfile","gzip","bz2","lzma","zlib","pickle",
            "shelve","dbm","pprint","textwrap","difflib","uuid","secrets","hashlib",
            "warnings","string","struct","builtins","__future__","importlib",
            "pkgutil","site","sysconfig","venv","code","codeop","compileall",
            "winreg","winsound","msvcrt","nt","posix","errno","pwd","grp",
        }
        hidden: list = []
        broken: list = []
        for mod, files in sorted(import_map.items()):
            if mod in stdlib or mod in ("__future__", "problems", "modules", "learning_machine", "tests"):
                continue
            if mod not in installed:
                # Check if it's a local file
                if (HERE / f"{mod}.py").exists() or (HERE / mod).is_dir():
                    continue
                broken.append((mod, sorted(files)))
            # Check if in installed but not requirements.txt
            # (informational — not flagged as broken)
        if broken:
            lines.append("**BROKEN imports** (used in code, not installed):")
            lines.append("| Module | Used in |")
            lines.append("|---|---|")
            for mod, files in broken[:20]:
                lines.append(f"| {mod} | {', '.join(files[:3])} |")
        else:
            lines.append("_No broken imports detected._")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_m() -> str:
    lines = ["## M. WCCS DEEP DIVE (last 10 runs)\n"]
    try:
        session_dir = HERE / "session_logs"
        if not session_dir.exists():
            return "\n".join(lines) + "_No session_logs/ directory found._\n"
        sessions = sorted(session_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
        if not sessions:
            return "\n".join(lines) + "_No session log files found._\n"
        lines.append("| File | Size | Last Modified |")
        lines.append("|---|---|---|")
        for s in sessions:
            lines.append(f"| {s.name} | {s.stat().st_size:,}B | {_age(s.stat().st_mtime)} |")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_n() -> str:
    lines = ["## N. SYSTEM SNAPSHOT (WENTO-1)\n"]
    try:
        import psutil
        lines.append(f"- RAM: {psutil.virtual_memory().percent:.1f}% used")
        lines.append(f"- CPU: {psutil.cpu_percent(interval=0.5):.1f}%")
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                lines.append(f"- Disk {part.mountpoint}: {usage.free / 1e9:.1f}GB free / {usage.total / 1e9:.1f}GB total")
            except Exception:
                pass
        # GPU via nvidia-smi
        try:
            r = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                                 "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                for line in r.stdout.strip().splitlines():
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 3:
                        lines.append(f"- GPU: {parts[0]}% util, {parts[1]}MB/{parts[2]}MB VRAM")
        except Exception:
            lines.append("- GPU: nvidia-smi not available")
    except ImportError:
        lines.append("_psutil not installed — skipping system snapshot._")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_o() -> str:
    lines = ["## O. NETWORK CHECKS (WENTO-2)\n"]
    import urllib.request
    hosts = [
        ("Mistral",      "https://api.mistral.ai"),
        ("Gemini",       "https://generativelanguage.googleapis.com"),
        ("Cerebras",     "https://api.cerebras.ai"),
        ("OpenRouter",   "https://openrouter.ai"),
        ("GitHub API",   "https://api.github.com"),
    ]
    lines.append("| Service | Reachable | ms |")
    lines.append("|---|---|---|")
    import time
    for label, url in hosts:
        try:
            t0 = time.time()
            req = urllib.request.urlopen(url, timeout=3)
            req.read(64)
            ms = int((time.time() - t0) * 1000)
            lines.append(f"| {label} | YES | {ms}ms |")
        except Exception as e:
            lines.append(f"| {label} | NO ⚠️ | {str(e)[:40]} |")
    return "\n".join(lines) + "\n"


def sec_p() -> str:
    lines = ["## P. PORT AND LOCK STATE (WENTO-3)\n"]
    try:
        import psutil
        def port_process(port: int):
            for conn in psutil.net_connections(kind="inet"):
                if conn.laddr.port == port and conn.status == "LISTEN":
                    try:
                        proc = psutil.Process(conn.pid)
                        return f"{proc.name()} (PID {conn.pid})"
                    except Exception:
                        return f"PID {conn.pid}"
            return "free"
        lines.append(f"- Port 8080 (MCC): {port_process(8080)}")
        lines.append(f"- Port 1234 (LM Studio): {port_process(1234)}")
    except ImportError:
        # Fallback: try socket
        for port, label in [(8080, "MCC"), (1234, "LM Studio")]:
            try:
                s = socket.socket()
                s.settimeout(0.5)
                r = s.connect_ex(("127.0.0.1", port))
                s.close()
                lines.append(f"- Port {port} ({label}): {'IN USE' if r == 0 else 'free'}")
            except Exception:
                lines.append(f"- Port {port} ({label}): unknown")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    # Stale lock files
    try:
        threshold = datetime.datetime.now().timestamp() - 86400
        locks = [p for p in HERE.glob("*.lock") if p.stat().st_mtime < threshold]
        if locks:
            lines.append(f"\n⚠️ Stale .lock files (>24h): {[p.name for p in locks]}")
        else:
            lines.append("- No stale .lock files found.")
    except Exception:
        pass
    return "\n".join(lines) + "\n"


def sec_q() -> str:
    lines = ["## Q. GIT STATE (WENTO-4)\n"]
    try:
        def git(*args):
            r = subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=str(HERE), timeout=10)
            return r.stdout.strip()
        branch  = git("rev-parse", "--abbrev-ref", "HEAD")
        status  = git("status", "--short")
        staged  = [l for l in status.splitlines() if l and l[0] in "AMDRC"]
        changed = [l for l in status.splitlines() if l.strip()]
        last_log = git("log", "-1", "--format=%ci %s")
        lines.append(f"- Branch: {branch}")
        lines.append(f"- Uncommitted changes: {len(changed)}")
        lines.append(f"- Staged files: {len(staged)}")
        lines.append(f"- Last commit: {last_log[:100]}")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_r() -> str:
    lines = ["## R. PYTHON ENV (WENTO-5)\n"]
    try:
        lines.append(f"- Python: {sys.version.split()[0]}")
        lines.append(f"- Executable: {sys.executable}")
        venv = os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_DEFAULT_ENV")
        lines.append(f"- Virtualenv: {venv if venv else 'not detected'}")
        import site
        sp = site.getsitepackages() if hasattr(site, "getsitepackages") else []
        lines.append(f"- Site-packages: {sp[0] if sp else 'unknown'}")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_s() -> str:
    lines = ["## S. LM STUDIO STATE (WENTO-6)\n"]
    try:
        import http.client, time
        conn = http.client.HTTPConnection("127.0.0.1", 1234, timeout=3)
        t0 = time.time()
        conn.request("GET", "/v1/models")
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", errors="replace")
        ms   = int((time.time() - t0) * 1000)
        lines.append(f"- LM Studio: RUNNING ({ms}ms)")
        try:
            data = json.loads(body)
            models = [m.get("id","?") for m in data.get("data", [])]
            lines.append(f"- Models loaded: {len(models)}")
            for m in models[:5]:
                lines.append(f"  - {m}")
        except Exception:
            pass
    except Exception:
        lines.append("- LM Studio: NOT RUNNING (port 1234 not responding)")
    return "\n".join(lines) + "\n"


def sec_t(prev_report: str = "") -> str:
    lines = ["## T. REALITY DIFF (WENTO-7)\n"]
    try:
        prev_files = sorted(HIST_DIR.glob("REALITY_REPORT_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if len(prev_files) < 1:
            return "\n".join(lines) + "_No previous report to diff against._\n"
        prev = prev_files[0]
        prev_text = prev.read_text(encoding="utf-8", errors="replace")
        lines.append(f"- Comparing against: {prev.name}")
        # Simple section-level diff: check which sections changed
        def extract_sections(text: str) -> dict:
            secs = {}
            current = None
            buf = []
            for line in text.splitlines():
                m = re.match(r'^## ([A-Z])\.', line)
                if m:
                    if current:
                        secs[current] = "\n".join(buf)
                    current = m.group(1)
                    buf = [line]
                elif current:
                    buf.append(line)
            if current:
                secs[current] = "\n".join(buf)
            return secs
        if prev_report:
            prev_secs = extract_sections(prev_text)
            cur_secs  = extract_sections(prev_report)
            changed = [s for s in cur_secs if cur_secs.get(s) != prev_secs.get(s, "")]
            new_secs = [s for s in cur_secs if s not in prev_secs]
            if changed:
                lines.append(f"- Changed sections: {', '.join(changed)}")
            if new_secs:
                lines.append(f"- New sections: {', '.join(new_secs)}")
            if not changed and not new_secs:
                lines.append("- No changes detected vs previous report.")
        else:
            lines.append(f"- Previous report exists: {prev.name} ({_age(prev.stat().st_mtime)})")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


def sec_u() -> str:
    lines = ["## U. ONEDRIVE SYNC (WENTO-8)\n"]
    try:
        import subprocess
        # Check OneDrive sync status via attrib command on Windows
        r = subprocess.run(["attrib", str(HERE)], capture_output=True, text=True, timeout=5)
        attrs = r.stdout.strip()
        lines.append(f"- Folder attrib: `{attrs}`")
        # Check if OneDrive process is running
        try:
            import psutil
            od_procs = [p.name() for p in psutil.process_iter(["name"]) if "onedrive" in p.name().lower()]
            if od_procs:
                lines.append(f"- OneDrive process: RUNNING ({od_procs[0]})")
            else:
                lines.append("- OneDrive process: NOT FOUND")
        except ImportError:
            # Try tasklist
            r2 = subprocess.run(["tasklist", "/FI", "IMAGENAME eq OneDrive.exe", "/FO", "CSV"],
                                 capture_output=True, text=True, timeout=5)
            if "OneDrive.exe" in r2.stdout:
                lines.append("- OneDrive process: RUNNING")
            else:
                lines.append("- OneDrive process: not detected")
    except Exception as e:
        lines.append(f"_Error: {e}_\n")
    return "\n".join(lines) + "\n"


# ── WENTO-9: Stale lock cleanup ───────────────────────────────────────────────

def cleanup_stale_locks() -> None:
    try:
        threshold = datetime.datetime.now().timestamp() - 86400
        removed = []
        for lf in HERE.glob("*.lock"):
            if lf.stat().st_mtime < threshold:
                lf.unlink()
                removed.append(lf.name)
        if removed:
            try:
                from error_logger import log_event
                log_event("reality_check", f"Removed stale locks: {removed}")
            except Exception:
                pass
    except Exception:
        pass


# ── Main ──────────────────────────────────────────────────────────────────────

def build_report() -> str:
    stamp = _now()
    parts = [
        f"# REALITY REPORT — {stamp}\n",
        "_Generated by reality_check.py. Standalone — no mcc_server required._\n\n---\n",
    ]

    # Build sections — collect issues for TOP 5 ACTIONS
    top5: list = []

    a = sec_a(); parts.append(a)
    if "⚠️" in a:
        top5.append("Files marked ⚠️ in Section A need attention")

    b = sec_b(); parts.append(b)
    if "ERR" in b or "⚠️" in b:
        top5.append("Endpoint failures detected — see Section B")

    c = sec_c(); parts.append(c)
    if "NO ⚠️" in c:
        top5.append("Invalid JSON files in data/ — see Section C")

    d = sec_d(); parts.append(d)
    if "🔴" in d:
        top5.append("Providers offline — see Section D")

    e = sec_e(); parts.append(e)

    f = sec_f(); parts.append(f)
    g = sec_g(); parts.append(g)
    if "⚠️ YES" in g:
        top5.append("MOT is stale (>48h) — re-run mcc_full_mot.py")

    h = sec_h(); parts.append(h)

    i = sec_i(); parts.append(i)
    if "⚠️ MISSING" in i:
        top5.append("STATUS.md lists files as BUILT that are missing on disk — see Section I")

    parts.append(sec_j(top5))
    parts.append(sec_k())
    parts.append(sec_l())
    parts.append(sec_m())
    parts.append(sec_n())
    parts.append(sec_o())
    parts.append(sec_p())
    parts.append(sec_q())
    parts.append(sec_r())
    parts.append(sec_s())

    full = "\n".join(parts)
    parts.append(sec_t(full))
    parts.append(sec_u())

    return "\n".join(parts)


def main():
    cleanup_stale_locks()
    print(f"[reality_check] Building report at {_now()}...")
    report = build_report()

    # Write main report
    OUT_FILE.write_text(report, encoding="utf-8")
    print(f"[reality_check] Written: {OUT_FILE}")

    # Archive
    arch = HIST_DIR / f"REALITY_REPORT_{_stamp()}.md"
    shutil.copy2(OUT_FILE, arch)
    print(f"[reality_check] Archived: {arch}")

    print("[reality_check] DONE.")


if __name__ == "__main__":
    main()
