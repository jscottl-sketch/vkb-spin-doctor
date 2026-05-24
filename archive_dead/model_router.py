# model_router.py
# VKB Spin Doctor — Model Router
#
# Picks the cheapest free model for any task.
# If it fails, escalates to the next model automatically.
# Logs every result to task_db.json — gets smarter over time.
#
# Usage — standalone test:
#   python model_router.py
#
# Usage — from another script:
#   from model_router import ModelRouter
#   router = ModelRouter()
#   response = router.run("Write a Python function that reads a .blk file")

import os
import json
import time
import datetime
from pathlib import Path

# --- OPTIONAL IMPORTS (graceful fallback if not installed) --------------------
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("[Router] WARNING: 'requests' not installed. Online APIs unavailable.")
    print("         Fix: pip install requests --break-system-packages")

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# --- PATHS --------------------------------------------------------------------
PROJECT_DIR = Path(r"C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor")
DB_PATH     = PROJECT_DIR / "task_db.json"
ENV_FILE    = PROJECT_DIR / ".env"

# --- API ENDPOINTS ------------------------------------------------------------
LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL   = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


# --- MODEL ROUTER CLASS -------------------------------------------------------

class ModelRouter:
    """
    Routes tasks to the cheapest model that can handle them.
    Escalates automatically if a model fails.
    Logs every call to task_db.json.
    """

    def __init__(self, db_path: Path = DB_PATH, verbose: bool = True):
        self.verbose    = verbose
        self.db_path    = db_path
        self.db         = self._load_db()
        self.env        = self._load_env()
        self.allow_paid = False   # ← PAID API OFF by default. Use toggle_paid() to enable.

    def toggle_paid(self, on: bool = None):
        """
        Toggle paid API access (Anthropic Claude).
        toggle_paid()        — flips current state
        toggle_paid(True)    — force ON
        toggle_paid(False)   — force OFF
        """
        if on is None:
            self.allow_paid = not self.allow_paid
        else:
            self.allow_paid = on
        state = "ON  ⚠️  (costs money)" if self.allow_paid else "OFF ✓ (free only)"
        print(f"[Router] Paid API: {state}")

    # -- LOAD / SAVE ----------------------------------------------------------

    def _load_db(self) -> dict:
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"task_db.json not found at {self.db_path}\n"
                "Run setup_router.py first."
            )
        return json.loads(self.db_path.read_text())

    def _save_db(self):
        self.db_path.write_text(json.dumps(self.db, indent=2))

    def _load_env(self) -> dict:
        env = {}
        # From .env file
        if ENV_FILE.exists():
            for line in ENV_FILE.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
        # From Windows environment variables (overrides .env)
        for key in ("GROQ_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"):
            if os.environ.get(key):
                env[key] = os.environ[key]
        return env

    # -- TASK CLASSIFICATION --------------------------------------------------

    def classify_task(self, task_text: str) -> str:
        """
        Classify task type using keyword matching.
        FREE — no API call needed.
        Returns: 'vision' | 'code' | 'plan' | 'fast'
        """
        task_lower = task_text.lower()
        scores = {}

        for task_type, config in self.db["task_types"].items():
            score = sum(1 for kw in config["keywords"] if kw in task_lower)
            scores[task_type] = score

        best_type  = max(scores, key=scores.get)
        best_score = scores[best_type]

        # If no keywords matched, default to "fast"
        return best_type if best_score > 0 else "fast"

    # -- API CALLERS -----------------------------------------------------------

    def _call_lmstudio(self, model_name: str, messages: list) -> str:
        """Call LM Studio local server (OpenAI-compatible API, port 1234)."""
        if not HAS_REQUESTS:
            raise RuntimeError("requests not installed")

        resp = requests.post(
            LMSTUDIO_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model":       model_name,
                "messages":    messages,
                "max_tokens":  2000,
                "temperature": 0.7,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _call_groq(self, model_name: str, messages: list) -> str:
        """Call Groq free API (Llama 3.3 70B at ~500 tokens/sec)."""
        if not HAS_REQUESTS:
            raise RuntimeError("requests not installed")

        api_key = self.env.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set. Run setup_router.py to add it.")

        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            json={
                "model":      model_name,
                "messages":   messages,
                "max_tokens": 2000,
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _call_gemini(self, model_name: str, messages: list) -> str:
        """Call Google Gemini free tier (strong vision capability)."""
        if not HAS_REQUESTS:
            raise RuntimeError("requests not installed")

        api_key = self.env.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set. Run setup_router.py to add it.")

        resp = requests.post(
            f"{GEMINI_URL}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "model":      model_name,
                "messages":   messages,
                "max_tokens": 2000,
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _call_anthropic(self, model_name: str, messages: list) -> str:
        """Call Anthropic Claude API — PAID, last resort only."""
        if not HAS_ANTHROPIC:
            raise RuntimeError("anthropic package not installed")

        client = anthropic.Anthropic()

        # Split system message out (Anthropic format is different)
        system_msg = next(
            (m["content"] for m in messages if m["role"] == "system"), None
        )
        user_messages = [m for m in messages if m["role"] != "system"]

        kwargs = {
            "model":      model_name,
            "max_tokens": 2000,
            "messages":   user_messages,
        }
        if system_msg:
            kwargs["system"] = system_msg

        resp = client.messages.create(**kwargs)
        return resp.content[0].text

    # -- DISPATCHER -----------------------------------------------------------

    def _dispatch(self, model_cfg: dict, messages: list) -> str:
        """Send messages to the correct provider."""
        provider = model_cfg["provider"]
        name     = model_cfg["name"]

        if provider == "lmstudio":
            return self._call_lmstudio(name, messages)
        elif provider == "groq":
            return self._call_groq(name, messages)
        elif provider == "gemini":
            return self._call_gemini(name, messages)
        elif provider == "anthropic":
            return self._call_anthropic(name, messages)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    # -- LOGGING --------------------------------------------------------------

    def _log(self, task_type: str, model_name: str, success: bool, elapsed: float):
        """Update success stats and append to log. Saves to task_db.json."""
        # Update per-model stats
        for m in self.db["task_types"][task_type]["models"]:
            if m["name"] == model_name:
                m["attempts"] += 1
                if success:
                    m["successes"] += 1

        # Append to logs (cap at 500 entries)
        self.db["logs"].append({
            "ts":          datetime.datetime.now().isoformat(timespec="seconds"),
            "task_type":   task_type,
            "model":       model_name,
            "success":     success,
            "elapsed_s":   round(elapsed, 2),
        })
        if len(self.db["logs"]) > 500:
            self.db["logs"] = self.db["logs"][-500:]

        self._save_db()

    # -- PUBLIC: run -----------------------------------------------------------

    def run(
        self,
        task_text:     str,
        system_prompt: str  = None,
        image_b64:     str  = None,   # Optional base64 image (for vision tasks)
        image_type:    str  = "image/png",
    ) -> str:
        """
        Main entry point.

        1. Classifies the task (free keyword match)
        2. Tries models cheapest-first
        3. Escalates automatically on failure
        4. Logs every attempt to task_db.json
        5. Returns the first successful response

        Args:
            task_text:     The task or question as a string.
            system_prompt: Optional system-level instructions.
            image_b64:     Optional base64-encoded image string (vision tasks).
            image_type:    MIME type of image e.g. "image/png", "image/jpeg"

        Returns:
            Response string, or an error message if all models fail.
        """
        task_type = self.classify_task(task_text)
        models    = self.db["task_types"][task_type]["models"]

        if self.verbose:
            print(f"[Router] Task type  : {task_type}")
            print(f"[Router] Model chain: {[m['name'] for m in models]}")

        # Build messages list
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # User content — plain text or text + image
        if image_b64:
            user_content = [
                {"type": "text", "text": task_text},
                {"type": "image_url", "image_url": {"url": f"data:{image_type};base64,{image_b64}"}},
            ]
        else:
            user_content = task_text

        messages.append({"role": "user", "content": user_content})

        # Try each model in order
        for model_cfg in models:
            name     = model_cfg["name"]
            provider = model_cfg["provider"]
            cost     = model_cfg["cost_per_call"]
            cost_str = "FREE" if cost == 0 else f"~£{cost:.4f}"

            # Skip paid models unless allow_paid is ON
            if cost > 0 and not self.allow_paid:
                if self.verbose:
                    print(f"[Router] Skipped : {name}  ({provider})  {cost_str}  — paid API is OFF")
                continue

            if self.verbose:
                print(f"[Router] Trying  : {name}  ({provider})  {cost_str}")

            t0 = time.time()
            try:
                response = self._dispatch(model_cfg, messages)
                elapsed  = time.time() - t0
                self._log(task_type, name, True, elapsed)

                if self.verbose:
                    print(f"[Router] ✓ {name} responded in {elapsed:.1f}s")

                return response

            except Exception as e:
                elapsed = time.time() - t0
                self._log(task_type, name, False, elapsed)

                if self.verbose:
                    print(f"[Router] ✗ {name} failed: {e}")
                    print(f"[Router] Escalating to next model...")

        # All models failed
        paid_note = "" if self.allow_paid else "\n  Note: Paid API is OFF. Run toggle_paid(True) to enable Claude as fallback."
        return (
            "ERROR: All free models in the chain failed." + paid_note + "\n"
            "Check:\n"
            "  1. LM Studio is running (port 1234)\n"
            "  2. GROQ_API_KEY is set in .env\n"
            "  3. GEMINI_API_KEY is set in .env"
        )

    # -- PUBLIC: add_task_type -------------------------------------------------

    def add_task_type(self, name: str, description: str, keywords: list, models: list):
        """
        Add a new task type to the database.
        Call this as you discover new categories of task.

        Example:
            router.add_task_type(
                name        = "game_config",
                description = "Read or edit game config files (.blk, .binds, .xml)",
                keywords    = [".blk", ".binds", "config", "keybind", "axis"],
                models      = [
                    {"name": "qwen2.5-coder-32b-instruct", "provider": "lmstudio",  "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "llama-3.3-70b-versatile",    "provider": "groq",      "cost_per_call": 0,    "attempts": 0, "successes": 0},
                    {"name": "claude-sonnet-4-6",           "provider": "anthropic", "cost_per_call": 0.01, "attempts": 0, "successes": 0},
                ]
            )
        """
        if name in self.db["task_types"]:
            print(f"[Router] Task type '{name}' already exists — not overwriting.")
            return

        self.db["task_types"][name] = {
            "description": description,
            "keywords":    keywords,
            "models":      models,
        }
        self._save_db()
        print(f"[Router] ✓ Added task type: {name}")

    # -- PUBLIC: stats ---------------------------------------------------------

    def stats(self):
        """Print a table of success rates for every model in the database."""
        print("\n" + "=" * 60)
        print("  MODEL ROUTER STATS")
        print("=" * 60)

        for task_type, config in self.db["task_types"].items():
            print(f"\n  {task_type.upper()}  — {config['description']}")
            for m in config["models"]:
                attempts  = m["attempts"]
                successes = m["successes"]
                cost      = "FREE" if m["cost_per_call"] == 0 else f"${m['cost_per_call']}"

                if attempts > 0:
                    rate = successes / attempts * 100
                    bar  = "█" * int(rate / 10)
                    print(f"    {m['name']:<40} {rate:5.0f}%  ({successes}/{attempts})  {cost}")
                else:
                    print(f"    {m['name']:<40}   n/a  (no data yet)  {cost}")

        total_logs = len(self.db.get("logs", []))
        print(f"\n  Total calls logged: {total_logs}")
        print("=" * 60 + "\n")

    # -- PUBLIC: cost_report ---------------------------------------------------

    def cost_report(self):
        """Show how much has been spent vs saved by using free models."""
        logs = self.db.get("logs", [])
        if not logs:
            print("[Router] No logs yet.")
            return

        total_cost   = 0.0
        money_saved  = 0.0
        free_calls   = 0
        paid_calls   = 0

        for log in logs:
            if not log["success"]:
                continue
            task_type = log["task_type"]
            model_name = log["model"]

            # Find cost for this model
            cost = 0.0
            for m in self.db["task_types"].get(task_type, {}).get("models", []):
                if m["name"] == model_name:
                    cost = m["cost_per_call"]
                    break

            if cost == 0:
                free_calls += 1
                # What would Anthropic have cost?
                money_saved += 0.01
            else:
                paid_calls  += 1
                total_cost  += cost

        print("\n" + "=" * 60)
        print("  COST REPORT")
        print("=" * 60)
        print(f"  Free calls  : {free_calls}")
        print(f"  Paid calls  : {paid_calls}")
        print(f"  Total spent : £{total_cost:.4f}")
        print(f"  Est. saved  : £{money_saved:.2f}  (vs. always using Claude API)")
        print("=" * 60 + "\n")


# --- STANDALONE TEST ----------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  MODEL ROUTER — Standalone Test")
    print("=" * 60)

    router = ModelRouter(verbose=True)

    # 1. Test task classification (free — no API calls)
    print("\n-- CLASSIFICATION TEST (no API calls) --")
    test_tasks = [
        "What do you see on this screenshot of the War Thunder controls screen?",
        "Write a Python function to parse a War Thunder .blk config file",
        "What is the best approach to building the Big SFL router?",
        "Summarise this log file in one sentence",
        "Fix the bug in spin_fix.py where the axis name is wrong",
    ]
    for task in test_tasks:
        t = router.classify_task(task)
        print(f"  [{t:<8}]  {task[:65]}")

    # 2. Live test — uses cheapest FREE model (paid is OFF by default)
    print("\n-- LIVE TEST --")
    print(f"Paid API: {'ON' if router.allow_paid else 'OFF (free models only)'}")
    print("Sending a simple test message — cheapest model wins...\n")

    response = router.run(
        task_text     = "Reply with exactly: ROUTER WORKING. Nothing else.",
        system_prompt = "You are a test assistant. Follow instructions exactly."
    )
    print(f"\nResponse: {response}")

    # To enable paid fallback: router.toggle_paid(True)
    # To disable again:        router.toggle_paid(False)
    # To flip current state:   router.toggle_paid()

    # 3. Stats
    router.stats()
    router.cost_report()

