# setup_router.py
# VKB Spin Doctor — Model Router Setup
# Run ONCE from Admin terminal to download all models and set up API keys
#
# Usage:
#   C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe setup_router.py

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

# ─── PATHS ────────────────────────────────────────────────────────────────────
PROJECT_DIR = Path(r"C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor")
MODELS_DIR  = Path(r"D:\lm-models")
ENV_FILE    = PROJECT_DIR / ".env"
DB_PATH     = PROJECT_DIR / "task_db.json"

# ─── MODELS TO DOWNLOAD ───────────────────────────────────────────────────────
# DeepSeek R1 70B is already downloaded — not in this list
MODELS = [
    {
        "label":    "Qwen2.5-VL 32B  (Vision — reads game UIs)",
        "lms_id":   "lmstudio-community/Qwen2.5-VL-32B-Instruct-GGUF",
        "folder":   "Qwen2.5-VL-32B-Instruct-GGUF",
        "task":     "vision",
        "vram_gb":  20,
        "disk_gb":  20,
    },
    {
        "label":    "Qwen2.5-Coder 32B  (Code — writes Python)",
        "lms_id":   "lmstudio-community/Qwen2.5-Coder-32B-Instruct-GGUF",
        "folder":   "Qwen2.5-Coder-32B-Instruct-GGUF",
        "task":     "code",
        "vram_gb":  20,
        "disk_gb":  20,
    },
    {
        "label":    "Phi-4 14B  (Fast — quick tasks)",
        "lms_id":   "microsoft/phi-4-GGUF",
        "folder":   "phi-4-GGUF",
        "task":     "fast",
        "vram_gb":  9,
        "disk_gb":  8,
    },
]

TOTAL_DISK_GB = sum(m["disk_gb"] for m in MODELS)


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def banner(text):
    print(f"\n{'─' * 60}")
    print(f"  {text}")
    print(f"{'─' * 60}")


def find_lms_cli():
    """Try to locate the LM Studio CLI (lms / lms.exe)."""
    # 1. Already in PATH
    found = shutil.which("lms")
    if found:
        return found

    # 2. Common install locations on Windows
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "LM-Studio" / "lms.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "LM-Studio"              / "lms.exe",
        Path(r"C:\Program Files\LM-Studio\lms.exe"),
        Path(r"C:\Program Files (x86)\LM-Studio\lms.exe"),
    ]
    for path in candidates:
        if path.exists():
            return str(path)

    return None  # Not found


def existing_model_folders():
    """Return list of folder names already inside MODELS_DIR."""
    if not MODELS_DIR.exists():
        return []
    return [p.name for p in MODELS_DIR.iterdir() if p.is_dir()]


def download_via_lms(lms_path, model):
    """Attempt download using LM Studio CLI. Tries 'get' then 'download'."""
    for verb in ("get", "download"):
        print(f"  Running: lms {verb} {model['lms_id']}")
        result = subprocess.run(
            [lms_path, verb, model["lms_id"]],
            cwd=str(MODELS_DIR),
        )
        if result.returncode == 0:
            return True
    return False


def load_env():
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    # Also pull from Windows environment
    for key in ("GROQ_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"):
        if key not in env and os.environ.get(key):
            env[key] = os.environ[key]
    return env


def save_env(env: dict):
    lines = [f"{k}={v}" for k, v in env.items()]
    ENV_FILE.write_text("\n".join(lines) + "\n")


# ─── STEP 1 — DISK SPACE WARNING ─────────────────────────────────────────────

def step_disk_warning():
    banner("STEP 1 — Disk space check")
    print(f"  Models to download: {len(MODELS)}")
    print(f"  Total disk needed:  ~{TOTAL_DISK_GB} GB  (on D:\\)")
    print(f"  Destination:        {MODELS_DIR}")
    print()
    print("  Models already downloaded (DeepSeek R1 70B) are skipped.")
    print()
    answer = input("  Continue? (y / n): ").strip().lower()
    if answer != "y":
        print("  Aborted.")
        sys.exit(0)


# ─── STEP 2 — CREATE MODELS DIR ──────────────────────────────────────────────

def step_create_dirs():
    banner("STEP 2 — Create directories")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECT_DIR / "sfl_logs").mkdir(exist_ok=True)
    (PROJECT_DIR / "backups").mkdir(exist_ok=True)
    print(f"  ✓ {MODELS_DIR}")
    print(f"  ✓ {PROJECT_DIR / 'sfl_logs'}")
    print(f"  ✓ {PROJECT_DIR / 'backups'}")


# ─── STEP 3 — FIND LMS CLI ───────────────────────────────────────────────────

def step_find_lms():
    banner("STEP 3 — Locate LM Studio CLI")
    lms = find_lms_cli()
    if lms:
        print(f"  ✓ Found: {lms}")
    else:
        print("  ✗ LM Studio CLI not found.")
        print()
        print("  Option A — add LM Studio to PATH then re-run this script.")
        print("  Option B — open LM Studio and download these models manually:")
        for m in MODELS:
            print(f"    Search: {m['lms_id'].split('/')[-1]}")
        print()
        print("  Continuing — API keys and task_db.json will still be set up.")
    return lms


# ─── STEP 4 — DOWNLOAD MODELS ────────────────────────────────────────────────

def step_download_models(lms_path):
    banner("STEP 4 — Download models")

    if not lms_path:
        print("  Skipped — LM Studio CLI not available.")
        print("  Download models manually in LM Studio app, then re-run to set up API keys.")
        return

    existing = existing_model_folders()
    print(f"  Existing folders in {MODELS_DIR}: {len(existing)}")

    for model in MODELS:
        # Rough check — is the folder already there?
        already = any(model["folder"].lower() in e.lower() for e in existing)
        if already:
            print(f"\n  ✓ {model['label']} — already downloaded, skipping")
            continue

        print(f"\n  ↓ {model['label']}")
        print(f"    Size: ~{model['disk_gb']} GB   VRAM when loaded: ~{model['vram_gb']} GB")
        print(f"    This will take a while on a slow connection...")

        ok = download_via_lms(lms_path, model)
        if ok:
            print(f"    ✓ Downloaded")
        else:
            print(f"    ✗ Failed — download manually in LM Studio:")
            print(f"      Search: {model['lms_id']}")


# ─── STEP 5 — API KEYS ───────────────────────────────────────────────────────

def step_api_keys():
    banner("STEP 5 — API keys  (free services)")
    env = load_env()

    services = [
        {
            "key":   "GROQ_API_KEY",
            "label": "Groq  (free, Llama 3.3 70B at 500 tokens/sec)",
            "url":   "https://console.groq.com",
        },
        {
            "key":   "GEMINI_API_KEY",
            "label": "Google Gemini  (free tier, strong vision)",
            "url":   "https://aistudio.google.com/apikey",
        },
    ]

    for svc in services:
        current = env.get(svc["key"], "")
        if current:
            print(f"\n  ✓ {svc['label']} — key already set")
        else:
            print(f"\n  {svc['label']}")
            print(f"  Get your free key at: {svc['url']}")
            val = input("  Paste key here (or Enter to skip): ").strip()
            if val:
                env[svc["key"]] = val
                print(f"  ✓ Saved")
            else:
                print(f"  – Skipped (can add later)")

    # Check Anthropic key (already set as Windows env var)
    if env.get("ANTHROPIC_API_KEY"):
        print(f"\n  ✓ Anthropic API key — already set (Windows env var)")
    else:
        print(f"\n  ⚠  Anthropic API key not found.")
        print(f"     Set it as Windows environment variable ANTHROPIC_API_KEY")

    save_env(env)
    print(f"\n  Keys saved to {ENV_FILE}")


# ─── STEP 6 — CREATE task_db.json ────────────────────────────────────────────

def step_create_task_db():
    banner("STEP 6 — Create task_db.json")

    if DB_PATH.exists():
        print(f"  ✓ Already exists at {DB_PATH} — skipping")
        return

    db = {
        "version": 1,
        "description": "Model Router — task-to-model database. Grows smarter over time.",
        "task_types": {

            "vision": {
                "description": "Screenshot or game UI analysis",
                "keywords": [
                    "screenshot", "screen", "image", "see", "look",
                    "ui", "window", "visual", "game", "display", "pixel", "what is on"
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
                    {"name": "qwen2.5-coder-32b-instruct",   "provider": "lmstudio",  "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "llama-3.3-70b-versatile",       "provider": "groq",      "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "claude-sonnet-4-6",              "provider": "anthropic", "cost_per_call": 0.01, "attempts": 0, "successes": 0}
                ]
            },

            "plan": {
                "description": "Strategy, planning, reasoning, architecture",
                "keywords": [
                    "plan", "strategy", "should i", "how to", "decide",
                    "architect", "design", "best way", "approach", "what next",
                    "recommend", "prioritise", "roadmap", "next step"
                ],
                "models": [
                    {"name": "deepseek-r1-70b",           "provider": "lmstudio",  "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "llama-3.3-70b-versatile",   "provider": "groq",      "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "claude-sonnet-4-6",          "provider": "anthropic", "cost_per_call": 0.01, "attempts": 0, "successes": 0}
                ]
            },

            "fast": {
                "description": "Quick summaries, simple questions, short text tasks",
                "keywords": [],  # Catch-all — no keywords needed
                "models": [
                    {"name": "llama-3.3-70b-versatile",   "provider": "groq",      "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "phi-4",                     "provider": "lmstudio",  "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "claude-sonnet-4-6",          "provider": "anthropic", "cost_per_call": 0.01, "attempts": 0, "successes": 0}
                ]
            }
        },

        "logs": []
    }

    DB_PATH.write_text(json.dumps(db, indent=2))
    print(f"  ✓ Created {DB_PATH}")


# ─── STEP 7 — SUMMARY ────────────────────────────────────────────────────────

def step_summary(lms_found):
    banner("SETUP COMPLETE")

    existing = existing_model_folders()
    print("  Models in D:\\lm-models\\:")
    if existing:
        for f in existing:
            print(f"    ✓ {f}")
    else:
        print("    None — download manually in LM Studio then re-run")

    env = load_env()
    print("\n  API keys:")
    for key in ("GROQ_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"):
        status = "✓ set" if env.get(key) else "✗ missing"
        print(f"    {key}: {status}")

    print(f"\n  task_db.json: {'✓' if DB_PATH.exists() else '✗'}")

    print("""
  NEXT STEPS:
    1. In LM Studio — load a model (start with Qwen2.5-Coder 32B for code tasks)
    2. Start LM Studio server  (green button top-right, port 1234)
    3. Run:  python model_router.py
       — It will route a test task and show you which model responded
""")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  VKB SPIN DOCTOR — Model Router Setup")
    print("=" * 60)

    step_disk_warning()
    step_create_dirs()
    lms = step_find_lms()
    step_download_models(lms)
    step_api_keys()
    step_create_task_db()
    step_summary(lms)


if __name__ == "__main__":
    main()
