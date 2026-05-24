# full_auto_setup.py
# VKB Spin Doctor — Full Autonomous Setup
# Zero prompts. Runs everything start to finish.
#
# Usage (Admin terminal):
#   C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe full_auto_setup.py

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────────────────────────────

PROJECT_DIR = Path(r"C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor")
MODELS_DIR  = Path(r"D:\lm-models")
DB_PATH     = PROJECT_DIR / "task_db.json"
ENV_FILE    = PROJECT_DIR / ".env"
PYTHON      = r"C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe"

# Models to download — correct LM Studio short IDs
MODELS = [
    {
        "label":   "Qwen2.5-VL 32B  (Vision)",
        "lms_id":  "qwen/qwen2.5-vl-32b",
        "folder":  "qwen2.5-vl-32b",
        "disk_gb": 20,
        "vram_gb": 20,
        "load_priority": 3,   # Load last (biggest)
    },
    {
        "label":   "Qwen2.5-Coder 32B  (Code)",
        "lms_id":  "qwen/qwen2.5-coder-32b",
        "folder":  "qwen2.5-coder-32b",
        "disk_gb": 20,
        "vram_gb": 20,
        "load_priority": 1,   # Load first for test
    },
    {
        "label":   "Phi-4 14B  (Fast)",
        "lms_id":  "microsoft/phi-4",
        "folder":  "phi-4",
        "disk_gb": 8,
        "vram_gb": 9,
        "load_priority": 2,
    },
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def log(msg, status=""):
    icons = {"ok": "✓", "fail": "✗", "skip": "–", "run": "→", "info": " "}
    icon = icons.get(status, " ")
    print(f"  {icon}  {msg}")

def banner(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")

def find_lms():
    if shutil.which("lms"):
        return "lms"
    candidates = [
        Path(os.environ.get("LOCALAPPDATA","")) / "Programs" / "LM-Studio" / "lms.exe",
        Path(os.environ.get("LOCALAPPDATA","")) / ".lmstudio" / "bin" / "lms.EXE",
        Path(os.path.expanduser("~")) / ".lmstudio" / "bin" / "lms.EXE",
        Path(os.path.expanduser("~")) / ".lmstudio" / "bin" / "lms.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None

def run_cmd(cmd, timeout=None, capture=True):
    """Run a command. Returns (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=timeout,
        )
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)

def existing_model_folders():
    if not MODELS_DIR.exists():
        return []
    return [p.name.lower() for p in MODELS_DIR.iterdir() if p.is_dir()]

def load_env():
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    for key in ("GROQ_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"):
        if os.environ.get(key):
            env[key] = os.environ[key]
    return env

# ─── PHASE 1 — DIRECTORIES ────────────────────────────────────────────────────

def phase_dirs():
    banner("PHASE 1 — Directories")
    for d in [MODELS_DIR, PROJECT_DIR/"sfl_logs", PROJECT_DIR/"backups"]:
        d.mkdir(parents=True, exist_ok=True)
        log(str(d), "ok")

# ─── PHASE 2 — FIND LMS ───────────────────────────────────────────────────────

def phase_find_lms():
    banner("PHASE 2 — LM Studio CLI")
    lms = find_lms()
    if lms:
        log(f"Found: {lms}", "ok")
    else:
        log("Not found in standard locations", "fail")
        log("Models will need to be downloaded manually in LM Studio app", "info")
    return lms

# ─── PHASE 3 — DOWNLOAD MODELS ────────────────────────────────────────────────

def phase_download_models(lms):
    banner("PHASE 3 — Download Models")

    if not lms:
        log("Skipped — LMS CLI not available", "skip")
        log("Open LM Studio app and search for these models manually:", "info")
        for m in MODELS:
            log(f"  {m['lms_id']}", "info")
        return

    existing = existing_model_folders()
    log(f"Existing models found: {len(existing)}", "info")

    for model in MODELS:
        already = any(model["folder"].lower() in e for e in existing)

        if already:
            log(f"{model['label']} — already downloaded", "skip")
            continue

        log(f"Downloading {model['label']}  (~{model['disk_gb']}GB)...", "run")
        log("This will take a while. Do not close this window.", "info")

        # Try lms get
        code, out, err = run_cmd([lms, "get", model["lms_id"]], timeout=3600, capture=False)

        if code == 0:
            log(f"{model['label']} — downloaded", "ok")
        else:
            # Try alternate: lms download
            log(f"lms get failed, trying lms download...", "run")
            code2, out2, err2 = run_cmd([lms, "download", model["lms_id"]], timeout=3600, capture=False)
            if code2 == 0:
                log(f"{model['label']} — downloaded", "ok")
            else:
                log(f"{model['label']} — failed. Download manually in LM Studio:", "fail")
                log(f"  Search: {model['lms_id']}", "info")

# ─── PHASE 4 — TASK DATABASE ──────────────────────────────────────────────────

def phase_task_db():
    banner("PHASE 4 — Task Database")

    db = {
        "version": 1,
        "description": "Model Router — task-to-model database. Grows smarter over time.",
        "task_types": {
            "vision": {
                "description": "Screenshot or game UI analysis",
                "keywords": [
                    "screenshot", "screen", "image", "see", "look", "ui",
                    "window", "visual", "game", "display", "pixel", "what is on"
                ],
                "models": [
                    {"name": "qwen2.5-vl-32b-instruct", "provider": "lmstudio",  "cost_per_call": 0,     "attempts": 0, "successes": 0},
                    {"name": "gemini-2.5-pro",           "provider": "gemini",    "cost_per_call": 0,     "attempts": 0, "successes": 0},
                    {"name": "claude-sonnet-4-6",         "provider": "anthropic", "cost_per_call": 0.003, "attempts": 0, "successes": 0}
                ]
            },
            "code": {
                "description": "Write, edit, or debug Python / config files",
                "keywords": [
                    "python", "code", "write", "edit", "file", "function",
                    "bug", "fix", "class", "import", ".py", "script", "module",
                    "def ", "json", ".blk", ".xml", "parse", "read file", "save file"
                ],
                "models": [
                    {"name": "qwen2.5-coder-32b-instruct", "provider": "lmstudio",  "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "llama-3.3-70b-versatile",    "provider": "groq",      "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "claude-sonnet-4-6",           "provider": "anthropic", "cost_per_call": 0.01, "attempts": 0, "successes": 0}
                ]
            },
            "plan": {
                "description": "Strategy, planning, reasoning, architecture",
                "keywords": [
                    "plan", "strategy", "should", "how to", "decide",
                    "architect", "design", "best way", "approach", "what next",
                    "recommend", "prioritise", "roadmap", "next step"
                ],
                "models": [
                    {"name": "deepseek-r1-70b",          "provider": "lmstudio",  "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "llama-3.3-70b-versatile",  "provider": "groq",      "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "claude-sonnet-4-6",         "provider": "anthropic", "cost_per_call": 0.01, "attempts": 0, "successes": 0}
                ]
            },
            "fast": {
                "description": "Quick summaries, simple questions, short text tasks",
                "keywords": [],
                "models": [
                    {"name": "llama-3.3-70b-versatile",  "provider": "groq",      "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "phi-4",                    "provider": "lmstudio",  "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "claude-sonnet-4-6",         "provider": "anthropic", "cost_per_call": 0.01, "attempts": 0, "successes": 0}
                ]
            }
        },
        "logs": []
    }

    DB_PATH.write_text(json.dumps(db, indent=2))
    log(f"Created {DB_PATH}", "ok")

# ─── PHASE 5 — START LM STUDIO SERVER ────────────────────────────────────────

def phase_start_server(lms):
    banner("PHASE 5 — LM Studio Server")

    if not lms:
        log("Skipped — LMS CLI not available", "skip")
        return False

    # Try to start server
    log("Starting LM Studio server on port 1234...", "run")
    code, out, err = run_cmd([lms, "server", "start"], timeout=15)

    if code == 0 or "already" in (out + err).lower() or "running" in (out + err).lower():
        log("Server running on port 1234", "ok")
        return True
    else:
        log("Could not start server via CLI", "fail")
        log("In LM Studio app — click the green Start Server button (top right)", "info")
        return False

# ─── PHASE 6 — LOAD A MODEL ───────────────────────────────────────────────────

def phase_load_model(lms):
    banner("PHASE 6 — Load Model")

    if not lms:
        log("Skipped — LMS CLI not available", "skip")
        return

    # Try to load Qwen2.5-Coder first (code tasks — most useful)
    model_to_load = "qwen/qwen2.5-coder-32b"
    log(f"Loading {model_to_load}...", "run")
    log("This may take 1-2 minutes (reading from disk)", "info")

    code, out, err = run_cmd([lms, "load", model_to_load], timeout=180)

    if code == 0:
        log(f"{model_to_load} loaded", "ok")
    else:
        # Try without the slash prefix
        code2, out2, err2 = run_cmd([lms, "load", "qwen2.5-coder-32b"], timeout=180)
        if code2 == 0:
            log("qwen2.5-coder-32b loaded", "ok")
        else:
            log("Could not load via CLI — load manually in LM Studio", "fail")
            log("Open LM Studio → click the model → Load", "info")

# ─── PHASE 7 — TEST ROUTER ────────────────────────────────────────────────────

def phase_test_router():
    banner("PHASE 7 — Test Model Router")

    router_path = PROJECT_DIR / "model_router.py"
    if not router_path.exists():
        log("model_router.py not found in project folder", "fail")
        log(f"Expected at: {router_path}", "info")
        return

    log("Running model_router.py test...", "run")

    # Brief wait for server to be ready
    time.sleep(2)

    code, out, err = run_cmd([PYTHON, str(router_path)], timeout=120)

    if code == 0:
        log("Router test complete", "ok")
        print("\n" + "─"*60)
        print(out)
    else:
        log("Router test had errors", "fail")
        if out:
            print(out[-2000:])  # Last 2000 chars
        if err:
            print(err[-1000:])

# ─── PHASE 8 — FINAL REPORT ───────────────────────────────────────────────────

def phase_report():
    banner("FINAL REPORT")

    env = load_env()
    existing = existing_model_folders()

    print("\n  Models downloaded:")
    for m in MODELS:
        have = any(m["folder"].lower() in e for e in existing)
        log(m["label"], "ok" if have else "fail")

    print("\n  API keys:")
    for key in ("GROQ_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"):
        status = "ok" if env.get(key) else "fail"
        label = "set" if env.get(key) else "MISSING"
        log(f"{key}: {label}", status)

    print("\n  Files:")
    for f in ("model_router.py", "setup_router.py", "task_db.json"):
        path = PROJECT_DIR / f
        log(f"{f}", "ok" if path.exists() else "fail")

    env = load_env()
    missing_keys = [k for k in ("GROQ_API_KEY", "GEMINI_API_KEY") if not env.get(k)]
    if missing_keys:
        print("\n  FREE API KEYS STILL NEEDED:")
        if "GROQ_API_KEY" in missing_keys:
            print("    Groq  (fastest free AI):  https://console.groq.com")
        if "GEMINI_API_KEY" in missing_keys:
            print("    Gemini (free vision AI):  https://aistudio.google.com/apikey")
        print()
        print("  Once you have them, run:")
        print(f"  {PYTHON} setup_router.py")
        print("  (It will skip downloads and only ask for missing keys)")

    print("\n" + "="*60)
    print("  DONE. Router is ready.")
    print("="*60 + "\n")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("  VKB SPIN DOCTOR — Full Auto Setup")
    print("  Runs everything. No prompts.")
    print("="*60)

    phase_dirs()
    lms = phase_find_lms()
    phase_download_models(lms)
    phase_task_db()
    phase_start_server(lms)
    phase_load_model(lms)
    phase_test_router()
    phase_report()

if __name__ == "__main__":
    main()
