"""
aafl_core.py — AAFL (AI Agent Feedback Loop) Core Spine
Uses LiteLLM for unified provider routing. python-dotenv for .env loading.
Cheapest-first routing: local LM Studio → free online → paid fallback.
Skips any provider whose API key is missing from .env.
"""
import os
import sys
import subprocess
import time
import datetime
import socket
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

import litellm
litellm.set_verbose = False
litellm.suppress_debug_info = True

# ── Paths ────────────────────────────────────────────────────────────────────
HERE     = Path(__file__).parent
LOG_FILE = HERE / "aafl_log.txt"

# ── Task types ────────────────────────────────────────────────────────────────
TASK_TYPES = ["code", "fast", "reason", "vision", "batch", "embed"]

# ── Provider table ────────────────────────────────────────────────────────────
# Ordered cheapest-first within each tier.
# tier 1 = local (free, unlimited)
# tier 2 = free online (has API key, generous free tier)
# tier 3 = online fallback
# tier 99 = paid — only used when allow_paid=True
PROVIDERS = [
    # ── Tier 1: Local LM Studio ───────────────────────────────────────────
    {
        "id": "lmstudio_coder",
        "label": "LM Studio Coder 32B",
        "model": "openai/qwen2.5-coder-32b-instruct",
        "api_base": "http://127.0.0.1:1234/v1",
        "api_key": "lm-studio",
        "api_key_env": None,
        "task_types": ["code", "reason", "batch"],
        "vision": False,
        "tier": 1,
    },
    {
        "id": "lmstudio_vision",
        "label": "LM Studio VL 32B",
        "model": "openai/qwen2.5-vl-32b-instruct",
        "api_base": "http://127.0.0.1:1234/v1",
        "api_key": "lm-studio",
        "api_key_env": None,
        "task_types": ["vision", "code"],
        "vision": True,
        "tier": 1,
    },
    {
        "id": "lmstudio_reason",
        "label": "LM Studio DeepSeek R1",
        "model": "openai/deepseek-r1-70b",
        "api_base": "http://127.0.0.1:1234/v1",
        "api_key": "lm-studio",
        "api_key_env": None,
        "task_types": ["reason", "batch"],
        "vision": False,
        "tier": 1,
    },
    {
        "id": "lmstudio_fast",
        "label": "LM Studio Phi-4 14B",
        "model": "openai/phi-4-14b",
        "api_base": "http://127.0.0.1:1234/v1",
        "api_key": "lm-studio",
        "api_key_env": None,
        "task_types": ["fast", "code"],
        "vision": False,
        "tier": 1,
    },
    # ── Tier 2: Free online ───────────────────────────────────────────────
    {
        "id": "cerebras",
        "label": "Cerebras GPT-OSS 120B",
        "model": "cerebras/gpt-oss-120b",
        "api_base": None,
        "api_key": None,
        "api_key_env": "CEREBRAS_API_KEY",
        "task_types": ["fast", "reason", "code"],
        "vision": False,
        "tier": 2,
    },
    {
        "id": "groq_70b",
        "label": "Groq Llama 3.3 70B",
        "model": "groq/llama-3.3-70b-versatile",
        "api_base": None,
        "api_key": None,
        "api_key_env": "GROQ_API_KEY",
        "task_types": ["fast", "code", "reason"],
        "vision": False,
        "tier": 2,
    },
    {
        "id": "groq_deepseek",
        "label": "Groq DeepSeek R1",
        "model": "groq/deepseek-r1-distill-llama-70b",
        "api_base": None,
        "api_key": None,
        "api_key_env": "GROQ_API_KEY",
        "task_types": ["reason", "code"],
        "vision": False,
        "tier": 2,
    },
    {
        "id": "gemini_flash",
        "label": "Gemini 2.5 Flash",
        "model": "gemini/gemini-2.5-flash",
        "api_base": None,
        "api_key": None,
        "api_key_env": "GEMINI_API_KEY",
        "task_types": ["vision", "reason", "fast"],
        "vision": True,
        "tier": 2,
    },
    {
        "id": "mistral_code",
        "label": "Mistral Codestral",
        "model": "mistral/codestral-latest",
        "api_base": None,
        "api_key": None,
        "api_key_env": "MISTRAL_API_KEY",
        "task_types": ["code", "batch"],
        "vision": False,
        "tier": 2,
    },
    # ── Tier 3: Online fallback ───────────────────────────────────────────
    {
        "id": "openrouter",
        "label": "OpenRouter Auto",
        "model": "openrouter/openrouter/auto",
        "api_base": None,
        "api_key": None,
        "api_key_env": "OPENROUTER_API_KEY",
        "task_types": ["fast", "code", "reason"],
        "vision": False,
        "tier": 3,
    },
    {
        "id": "huggingface",
        "label": "HuggingFace Mistral-7B",
        "model": "huggingface/mistralai/Mistral-7B-Instruct-v0.3",
        "api_base": None,
        "api_key": None,
        "api_key_env": "HF_API_KEY",
        "task_types": ["fast", "code"],
        "vision": False,
        "tier": 3,
    },
    {
        "id": "cloudflare",
        "label": "Cloudflare Workers AI",
        "model": "cloudflare/@cf/meta/llama-3.1-8b-instruct",
        "api_base": None,
        "api_key": None,
        "api_key_env": "CLOUDFLARE_API_KEY",
        "extra_env":   "CLOUDFLARE_ACCOUNT_ID",
        "task_types": ["fast", "code"],
        "vision": False,
        "tier": 2,
    },
    {
        "id": "cohere_embed",
        "label": "Cohere Embeddings",
        "model": "cohere/embed-english-v3.0",
        "api_base": None,
        "api_key": None,
        "api_key_env": "COHERE_API_KEY",
        "task_types": ["embed"],
        "vision": False,
        "tier": 3,
        "embed_only": True,
    },
    # ── Tier 99: Paid — blocked unless allow_paid=True ────────────────────
    {
        "id": "claude_api",
        "label": "Claude Sonnet (PAID)",
        "model": "claude-sonnet-4-6",
        "api_base": None,
        "api_key": None,
        "api_key_env": "ANTHROPIC_API_KEY",
        "task_types": ["code", "reason", "vision", "fast"],
        "vision": True,
        "tier": 99,
        "paid": True,
        "cost_per_call_usd": 0.01,
    },
]

# Routing table: task_type → provider IDs in cheapest-first order
ROUTING = {
    "code":   ["lmstudio_coder",  "lmstudio_fast",   "cerebras",    "groq_70b",
               "cloudflare",      "mistral_code",     "openrouter",  "claude_api"],
    "fast":   ["lmstudio_fast",   "cerebras",         "groq_70b",    "cloudflare",
               "gemini_flash",    "openrouter"],
    "reason": ["lmstudio_reason", "groq_deepseek",    "gemini_flash","cerebras",
               "openrouter",      "claude_api"],
    "vision": ["lmstudio_vision", "gemini_flash",     "claude_api"],
    "batch":  ["mistral_code",    "lmstudio_coder",   "gemini_flash","openrouter"],
    "embed":  ["cohere_embed",    "lmstudio_coder"],
}


# ── Result object ─────────────────────────────────────────────────────────────

class CallResult:
    def __init__(self, ok: bool, provider_id: str, model: str, response: str,
                 task_type: str, elapsed_sec: float, cost_usd: float = 0.0,
                 dry_run: bool = False, error: Optional[str] = None):
        self.ok          = ok
        self.provider_id = provider_id
        self.model       = model
        self.response    = response
        self.task_type   = task_type
        self.elapsed_sec = elapsed_sec
        self.cost_usd    = cost_usd
        self.dry_run     = dry_run
        self.error       = error

    def __repr__(self):
        tag = "DRY" if self.dry_run else ("OK" if self.ok else "ERR")
        return (f"CallResult({tag} | {self.provider_id} | {self.task_type} | "
                f"{self.elapsed_sec}s | ${self.cost_usd:.5f})")


# ── Core class ────────────────────────────────────────────────────────────────

class AAFLCore:
    """
    AAFL spine. Instantiate once, call .run() for every task.

    dry_run=True  — no real API calls, spends nothing, returns "DRY_RUN_OK"
    allow_paid=True — unlocks tier-99 paid providers (Claude Sonnet etc.)
    """

    def __init__(self, dry_run: bool = False, allow_paid: bool = False):
        self.dry_run     = dry_run
        self.allow_paid  = allow_paid
        self._pmap       = {p["id"]: p for p in PROVIDERS}
        self._total_cost = 0.0
        self._call_count = 0
        self._log(f"START  dry_run={dry_run}  allow_paid={allow_paid}")
        mode = "DRY RUN — no real calls" if dry_run else "LIVE"
        print(f"[AAFL] {mode}. Paid={'ON' if allow_paid else 'OFF'}. "
              f"{len(PROVIDERS)} providers registered.")

    # ── Public: run a task ────────────────────────────────────────────────────

    def run(self, task: str, task_type: str = "fast",
            max_tokens: int = 512, system: str = "",
            image_b64: str = "") -> CallResult:
        if task_type not in ROUTING:
            task_type = "fast"

        route = ROUTING[task_type]
        t0    = time.time()

        for pid in route:
            p = self._pmap.get(pid)
            if not p:
                continue
            if p.get("paid") and not self.allow_paid:
                continue
            if not self._has_key(p):
                continue

            print(f"[AAFL] -> {p['label']}", end="", flush=True)
            elapsed = round(time.time() - t0, 2)

            # ── dry_run: skip the real call ───────────────────────────────
            if self.dry_run:
                print("  [dry]")
                result = CallResult(True, pid, p["model"], "DRY_RUN_OK",
                                    task_type, elapsed, 0.0, dry_run=True)
                self._record(result, task)
                return result

            # ── real call ─────────────────────────────────────────────────
            try:
                text, cost = self._call(p, task, system, max_tokens, image_b64)
                elapsed = round(time.time() - t0, 2)
                if not self.verify(text):
                    raise ValueError("verify() failed — empty response")
                print(f"  OK ({elapsed}s, ${cost:.5f})")
                result = CallResult(True, pid, p["model"], text,
                                    task_type, elapsed, cost)
                self._record(result, task)
                return result
            except Exception as exc:
                msg = str(exc)
                if any(t in msg.lower() for t in ("timeout", "timed out", "read timeout")):
                    print("  SKIP (timeout)")
                else:
                    print(f"  FAIL: {msg[:80]}")
                continue

        elapsed = round(time.time() - t0, 2)
        result  = CallResult(False, "none", "none", "", task_type, elapsed, 0.0,
                             error="All providers failed or skipped")
        self._record(result, task)
        print("[AAFL] All providers exhausted for this task.")
        return result

    # ── verify hooks ──────────────────────────────────────────────────────────

    def verify(self, response: str) -> bool:
        """Default verify: delegates to verify_returns_nonempty."""
        return self.verify_returns_nonempty(response)

    def verify_returns_nonempty(self, response: str) -> bool:
        """True if response is a non-empty, non-whitespace string."""
        return bool(response and response.strip())

    def verify_file_exists(self, path: str) -> bool:
        """True if the file at path exists on disk."""
        return Path(path).exists()

    def verify_python_runs(self, path: str) -> bool:
        """True if the file at path is valid Python (AST parse succeeds)."""
        try:
            result = subprocess.run(
                [sys.executable, "-c",
                 f"import ast; ast.parse(open({path!r}).read())"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    # ── Internal: LiteLLM call ────────────────────────────────────────────────

    def _call(self, p: dict, task: str, system: str, max_tokens: int, image_b64: str = ""):
        api_key = p.get("api_key") or os.environ.get(p.get("api_key_env") or "", "") or ""
        model   = p["model"]

        # HuggingFace uses a different env var name than LiteLLM expects
        if p["id"] == "huggingface" and api_key:
            os.environ.setdefault("HUGGINGFACE_API_KEY", api_key)

        # Embedding call (Cohere embed etc.)
        if p.get("embed_only"):
            resp = litellm.embedding(model=model, input=[task], api_key=api_key or None)
            vec  = resp.data[0]["embedding"]
            text = f"[embed:{len(vec)}dims first3={vec[:3]}]"
            return text, 0.0

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        if image_b64:
            messages.append({"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                {"type": "text", "text": task},
            ]})
        else:
            messages.append({"role": "user", "content": task})

        is_local = "127.0.0.1" in (p.get("api_base") or "")
        kwargs = dict(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            timeout=5 if is_local else 30,
        )
        if p.get("api_base"):
            kwargs["api_base"] = p["api_base"]
        if api_key:
            kwargs["api_key"] = api_key

        resp = litellm.completion(**kwargs)
        text = (resp.choices[0].message.content or "").strip()
        if not text:
            # Reasoning models (DeepSeek R1, etc.) put output in reasoning_content
            # when token budget is exhausted. Extract the answer after </think> so
            # the evaluator receives the actual answer, not the thinking chain.
            rc = getattr(resp.choices[0].message, "reasoning_content", None) or ""
            if "</think>" in rc:
                after_think = rc.split("</think>", 1)[-1].strip()
                text = after_think if after_think else rc.strip()
            else:
                text = rc.strip()

        # Cost — LiteLLM calculates this for known providers; falls back to 0
        try:
            cost = litellm.completion_cost(completion_response=resp)
        except Exception:
            cost = p.get("cost_per_call_usd", 0.0)

        return text, cost

    # ── Internal: key check ───────────────────────────────────────────────────

    def _has_key(self, p: dict) -> bool:
        """True if provider is usable (local needs no key; online needs env var set)."""
        if p.get("api_key_env") is None:
            return True   # local LM Studio — no key needed
        if not os.environ.get(p["api_key_env"], "").strip():
            return False
        # Some providers need a second env var (e.g. Cloudflare needs account ID)
        extra = p.get("extra_env")
        if extra and not os.environ.get(extra, "").strip():
            return False
        return True

    # ── Internal: logging ─────────────────────────────────────────────────────

    def _record(self, result: CallResult, task: str):
        self._call_count += 1
        self._total_cost += result.cost_usd
        tag = "DRY" if result.dry_run else ("OK " if result.ok else "ERR")
        self._log(
            f"{tag}  {result.task_type:<8} {result.provider_id:<20} "
            f"${result.cost_usd:.5f}  {result.elapsed_sec}s  {task[:60]!r}"
        )

    def _log(self, msg: str):
        ts   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}\n"
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass   # logging must never crash the caller

    # ── Public: status and reporting ──────────────────────────────────────────

    def status(self) -> List[dict]:
        """Print provider status table. Returns list of status dicts."""
        lm_up = _check_lmstudio()
        rows  = []
        for p in PROVIDERS:
            paid    = p.get("paid", False)
            local   = p.get("api_key_env") is None
            has_key = self._has_key(p)
            if paid and not self.allow_paid:
                st = "BLOCKED (paid off)"
            elif not has_key:
                st = "NO KEY"
            elif local and not lm_up:
                st = "LOCAL - not running"
            else:
                st = "LIVE"
            rows.append({"id": p["id"], "label": p["label"],
                         "tasks": ",".join(p["task_types"]),
                         "tier": p["tier"], "status": st})

        print("\n" + "=" * 68)
        print(f"  AAFL PROVIDER STATUS  (dry_run={self.dry_run})")
        print("=" * 68)
        tier_names = {1: "LOCAL", 2: "FREE ONLINE", 3: "FALLBACK", 99: "PAID"}
        cur_tier   = None
        for r in rows:
            if r["tier"] != cur_tier:
                cur_tier = r["tier"]
                print(f"\n  [{tier_names.get(cur_tier, cur_tier)}]")
            mark = "OK" if r["status"] == "LIVE" else "~~" if "not running" in r["status"] else "--"
            print(f"    {mark} {r['label']:<35} {r['tasks']:<24} {r['status']}")
        print()
        print(f"  Calls: {self._call_count}  |  Total cost: ${self._total_cost:.5f}")
        print("=" * 68 + "\n")
        return rows

    def cost_report(self):
        print(f"[AAFL] Session calls: {self._call_count} | "
              f"Cost: ${self._total_cost:.5f} | "
              f"{'DRY RUN -- $0 spent' if self.dry_run else 'LIVE'}")

    def detect(self, task: str) -> str:
        """Auto-detect the right task_type from a free-text task description."""
        t = task.lower()
        if any(w in t for w in ["screenshot", "image", "see", "look", "visual", "ui"]):
            return "vision"
        if any(w in t for w in ["embed", "vector", "similarity"]):
            return "embed"
        if any(w in t for w in [".py", "code", "bug", "fix", "function", "script"]):
            return "code"
        if any(w in t for w in ["plan", "decide", "should", "architect", "analyse", "analyze"]):
            return "reason"
        if any(w in t for w in ["batch", "all files", "process all"]):
            return "batch"
        return "fast"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _check_lmstudio(host: str = "127.0.0.1", port: int = 1234) -> bool:
    """Quick TCP check — is LM Studio listening on localhost?"""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 68)
    print("  AAFL CORE — DRY-RUN SELF-TEST")
    print("=" * 68)

    core = AAFLCore(dry_run=True)

    # ── Show which providers are live ────────────────────────────────────────
    rows = core.status()

    # ── Run one dry call per task type ───────────────────────────────────────
    print("  ROUTING TEST (dry_run — no real calls, no cost)\n")
    test_tasks = {
        "code":   "fix the off-by-one bug in spin_doctor.py",
        "fast":   "what is 2 + 2",
        "reason": "should I use litellm or raw requests for this project",
        "vision": "read this screenshot of the game UI",
        "batch":  "convert all .blk files in the folder",
        "embed":  "find similar sentences using embeddings",
    }

    results = []
    for tt, task in test_tasks.items():
        r = core.run(task, task_type=tt, max_tokens=20)
        results.append((tt, r))

    # ── Summary table ────────────────────────────────────────────────────────
    print("\n" + "=" * 68)
    print("  SELF-TEST RESULTS")
    print("=" * 68)
    print(f"  {'Task type':<10} {'Routed to':<25} {'Response':<15} {'Cost'}")
    print("  " + "-" * 64)
    for tt, r in results:
        resp_preview = r.response[:12] if r.response else "(none)"
        print(f"  {tt:<10} {r.provider_id:<25} {resp_preview:<15} ${r.cost_usd:.5f}")

    print()
    print("  LIVE PROVIDERS (key present or local):")
    live = [r for r in rows if r["status"] == "LIVE"]
    skip = [r for r in rows if r["status"] != "LIVE"]
    for r in live:
        print(f"    OK  {r['label']}")
    for r in skip:
        print(f"    --  {r['label']}  ({r['status']})")

    # ── Live probe: local providers (5-second timeout) ───────────────────────
    print()
    print("  LIVE PROBE — local LM Studio providers (5 s timeout)")
    print("  " + "-" * 64)
    _lm_up = _check_lmstudio()
    local_providers = [p for p in PROVIDERS if "127.0.0.1" in (p.get("api_base") or "")]
    for p_info in local_providers:
        print(f"  {p_info['label']:<35}", end="", flush=True)
        if not _lm_up:
            print("  SKIP (not running)")
            continue
        try:
            text, _ = core._call(p_info, "reply OK only", "", 5)
            print("  OK")
        except Exception as exc:
            msg = str(exc)
            if "timeout" in msg.lower():
                print("  SKIP (timeout)")
            else:
                print(f"  FAIL: {msg[:40]}")

    print()
    core.cost_report()
    print("=" * 68)
    print("  Self-test complete. aafl_log.txt updated.")
    print("=" * 68 + "\n")
