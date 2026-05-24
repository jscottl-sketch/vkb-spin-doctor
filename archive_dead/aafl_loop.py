# aafl_loop.py — AI Agent Feedback Loop Manager
# ALP: paid models OFF by default. Call loop.enable_paid() to unlock.
# Usage: from aafl_loop import AAFLLoop
#        loop = AAFLLoop()
#        result = loop.run(task="fix this bug", task_type="code")
#        print(result.response)

import os, json, time, datetime, requests
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

TASK_TYPES = ["code","vision","reason","fast","embed","batch"]

ALL_PROVIDERS = [
    {"id":"lmstudio_coder","label":"LM Studio Coder 32B","base_url":"http://127.0.0.1:1234/v1","model":"qwen2.5-coder-32b-instruct","api_key":"lm-studio","ranked_for":["code","reason","batch"],"vision":False,"online":False,"free_daily":None,"free_rpm":999,"alp_tier":1,"permanent_free":True},
    {"id":"lmstudio_vision","label":"LM Studio VL 32B","base_url":"http://127.0.0.1:1234/v1","model":"qwen2.5-vl-32b-instruct","api_key":"lm-studio","ranked_for":["vision","code"],"vision":True,"online":False,"free_daily":None,"free_rpm":999,"alp_tier":1,"permanent_free":True},
    {"id":"lmstudio_reason","label":"LM Studio DeepSeek R1","base_url":"http://127.0.0.1:1234/v1","model":"deepseek-r1-70b","api_key":"lm-studio","ranked_for":["reason","batch"],"vision":False,"online":False,"free_daily":None,"free_rpm":999,"alp_tier":1,"permanent_free":True},
    {"id":"lmstudio_fast","label":"LM Studio Phi-4 14B","base_url":"http://127.0.0.1:1234/v1","model":"phi-4-14b","api_key":"lm-studio","ranked_for":["fast","code"],"vision":False,"online":False,"free_daily":None,"free_rpm":999,"alp_tier":1,"permanent_free":True},
    {"id":"cerebras","label":"Cerebras Llama 3.3 70B","base_url":"https://api.cerebras.ai/v1","model":"llama-3.3-70b","api_key_env":"CEREBRAS_API_KEY","ranked_for":["fast","reason","code"],"vision":False,"online":True,"free_daily":1000000,"free_rpm":30,"alp_tier":2,"permanent_free":True},
    {"id":"groq_70b","label":"Groq Llama 3.3 70B","base_url":"https://api.groq.com/openai/v1","model":"llama-3.3-70b-versatile","api_key_env":"GROQ_API_KEY","ranked_for":["fast","code","reason"],"vision":False,"online":True,"free_daily":1000,"free_rpm":30,"alp_tier":2,"permanent_free":True},
    {"id":"groq_deepseek","label":"Groq DeepSeek R1","base_url":"https://api.groq.com/openai/v1","model":"deepseek-r1-distill-llama-70b","api_key_env":"GROQ_API_KEY","ranked_for":["reason","code"],"vision":False,"online":True,"free_daily":1000,"free_rpm":30,"alp_tier":2,"permanent_free":True},
    {"id":"gemini_flash","label":"Gemini 2.5 Flash","base_url":"https://generativelanguage.googleapis.com/v1beta/openai","model":"gemini-2.5-flash","api_key_env":"GEMINI_API_KEY","ranked_for":["vision","reason","fast"],"vision":True,"online":True,"free_daily":1500,"free_rpm":15,"alp_tier":2,"permanent_free":True},
    {"id":"mistral_code","label":"Mistral Codestral","base_url":"https://api.mistral.ai/v1","model":"codestral-latest","api_key_env":"MISTRAL_API_KEY","ranked_for":["code","batch"],"vision":False,"online":True,"free_daily":None,"free_rpm":2,"alp_tier":2,"permanent_free":True},
    {"id":"openrouter","label":"OpenRouter Auto","base_url":"https://openrouter.ai/api/v1","model":"openrouter/auto","api_key_env":"OPENROUTER_API_KEY","ranked_for":["fast","code","reason"],"vision":False,"online":True,"free_daily":50,"free_rpm":20,"alp_tier":3,"permanent_free":True},
    {"id":"huggingface","label":"HuggingFace Vision","base_url":"https://api-inference.huggingface.co/models","model":"meta-llama/Llama-3.2-11B-Vision-Instruct","api_key_env":"HF_API_KEY","ranked_for":["vision"],"vision":True,"online":True,"free_daily":None,"free_rpm":5,"alp_tier":3,"permanent_free":True},
    {"id":"cohere","label":"Cohere Embeddings","base_url":"https://api.cohere.com/v1","model":"embed-english-v3.0","api_key_env":"COHERE_API_KEY","ranked_for":["embed"],"vision":False,"online":True,"free_daily":33,"free_rpm":20,"alp_tier":3,"permanent_free":True},
    {"id":"claude_api","label":"Claude Sonnet PAID","base_url":"https://api.anthropic.com","model":"claude-sonnet-4-6","api_key_env":"ANTHROPIC_API_KEY","ranked_for":["code","reason","vision","fast"],"vision":True,"online":True,"free_daily":0,"free_rpm":50,"alp_tier":99,"permanent_free":False,"disabled_by_alp":True,"cost_usd_per_call":0.01},
]

TASK_ROUTING = {
    "code":   ["lmstudio_coder","lmstudio_fast","groq_70b","cerebras","mistral_code","openrouter","claude_api"],
    "vision": ["lmstudio_vision","gemini_flash","huggingface","claude_api"],
    "reason": ["lmstudio_reason","groq_deepseek","gemini_flash","cerebras","openrouter","claude_api"],
    "fast":   ["lmstudio_fast","cerebras","groq_70b","gemini_flash","openrouter"],
    "embed":  ["cohere","lmstudio_coder"],
    "batch":  ["mistral_code","lmstudio_coder","gemini_flash","openrouter"],
}

@dataclass
class LoopResult:
    success: bool
    provider_id: str
    model: str
    response: str
    task_type: str
    attempts: int
    elapsed_sec: float
    cost_usd: float = 0.0
    error: Optional[str] = None

class RateLimitTracker:
    def __init__(self):
        self._calls = {}
        self._last_call = {}

    def can_call(self, provider):
        pid = provider["id"]
        today = datetime.date.today().isoformat()
        daily_limit = provider.get("free_daily")
        rpm_limit = provider.get("free_rpm")
        if daily_limit is not None:
            entry = self._calls.get(pid, {"date": today, "count": 0})
            if entry["date"] != today:
                entry = {"date": today, "count": 0}
            if entry["count"] >= daily_limit:
                return False, f"Daily limit reached ({daily_limit})"
            self._calls[pid] = entry
        if rpm_limit is not None and rpm_limit < 100:
            gap = 60.0 / rpm_limit
            last = self._last_call.get(pid, 0)
            waited = time.time() - last
            if waited < gap:
                return False, f"RPM {rpm_limit}/min — wait {gap-waited:.1f}s"
        return True, "ok"

    def record_call(self, pid):
        today = datetime.date.today().isoformat()
        entry = self._calls.get(pid, {"date": today, "count": 0})
        if entry["date"] != today:
            entry = {"date": today, "count": 0}
        entry["count"] += 1
        self._calls[pid] = entry
        self._last_call[pid] = time.time()

    def remaining(self, provider):
        pid = provider["id"]
        daily = provider.get("free_daily")
        if daily is None:
            return "unlimited"
        today = datetime.date.today().isoformat()
        entry = self._calls.get(pid, {"date": today, "count": 0})
        used = entry["count"] if entry["date"] == today else 0
        return f"{daily - used}/{daily} left today"


class AAFLLoop:
    def __init__(self, log_dir="sfl_logs"):
        self.tracker = RateLimitTracker()
        self._paid_enabled = False
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(exist_ok=True)
        self._log_file = self._log_dir / f"aafl_{datetime.date.today()}.jsonl"
        self._pmap = {p["id"]: p for p in ALL_PROVIDERS}
        print(f"[AAFL] Ready. Paid API: OFF (ALP). Providers: {len(ALL_PROVIDERS)}")

    def run(self, task, task_type="fast", context="", image_b64=None, max_tokens=1000, system=""):
        if task_type not in TASK_ROUTING:
            task_type = "fast"
        route = TASK_ROUTING[task_type]
        attempts = 0
        t_start = time.time()
        for pid in route:
            p = self._pmap.get(pid)
            if not p:
                continue
            if p.get("disabled_by_alp") and not self._paid_enabled:
                continue
            if image_b64 and not p.get("vision"):
                continue
            can, reason = self.tracker.can_call(p)
            if not can:
                print(f"[AAFL] skip {p['label']}: {reason}")
                continue
            attempts += 1
            print(f"[AAFL] trying {p['label']}...")
            try:
                response = self._call(p, task, context, image_b64, max_tokens, system)
                self.tracker.record_call(pid)
                elapsed = round(time.time() - t_start, 2)
                result = LoopResult(True, pid, p["model"], response, task_type, attempts, elapsed, p.get("cost_usd_per_call", 0.0))
                self._log(result, task)
                print(f"[AAFL] OK via {p['label']} ({elapsed}s)")
                return result
            except Exception as e:
                print(f"[AAFL] fail {p['label']}: {e}")
                continue
        elapsed = round(time.time() - t_start, 2)
        result = LoopResult(False, "none", "none", "", task_type, attempts, elapsed, 0.0, "All providers failed")
        self._log(result, task)
        print("[AAFL] All providers exhausted.")
        return result

    def _call(self, p, task, context, image_b64, max_tokens, system):
        api_key = p.get("api_key") or os.environ.get(p.get("api_key_env") or "", "")
        model = p["model"]
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        content = f"{task}\n\n{context}".strip() if context else task
        if image_b64 and p.get("vision"):
            messages.append({"role": "user", "content": [{"type": "text", "text": content}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}]})
        else:
            messages.append({"role": "user", "content": content})
        if p["id"] == "claude_api":
            hdrs = {"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
            sys_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
            user_msgs = [m for m in messages if m["role"] != "system"]
            body = {"model": model, "max_tokens": max_tokens, "messages": user_msgs}
            if sys_msg:
                body["system"] = sys_msg
            r = requests.post("https://api.anthropic.com/v1/messages", headers=hdrs, json=body, timeout=30)
            r.raise_for_status()
            return r.json()["content"][0]["text"]
        if p["id"] == "huggingface":
            r = requests.post(f"{p['base_url']}/{model}", headers={"Authorization": f"Bearer {api_key}"}, json={"inputs": content}, timeout=60)
            r.raise_for_status()
            data = r.json()
            return data[0].get("generated_text", str(data)) if isinstance(data, list) else str(data)
        hdrs = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        if p["id"] == "openrouter":
            hdrs["HTTP-Referer"] = "https://github.com/VKB-SpinDoctor"
            hdrs["X-Title"] = "VKB-SpinDoctor-AAFL"
        r = requests.post(f"{p['base_url']}/chat/completions", headers=hdrs, json={"model": model, "messages": messages, "max_tokens": max_tokens}, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def enable_paid(self):
        self._paid_enabled = True
        for p in ALL_PROVIDERS:
            if "disabled_by_alp" in p:
                p["disabled_by_alp"] = False
        print("[AAFL] WARNING: Paid API ON. ~$0.01/call.")

    def disable_paid(self):
        self._paid_enabled = False
        for p in ALL_PROVIDERS:
            if p.get("alp_tier", 0) == 99:
                p["disabled_by_alp"] = True
        print("[AAFL] Paid API OFF (ALP).")

    def status(self):
        print("\n" + "="*55)
        print("  AAFL PROVIDER STATUS")
        print("="*55)
        for tier, tid in [("LOCAL (unlimited)", 1), ("ONLINE FREE", 2), ("FALLBACK", 3), ("PAID", 99)]:
            ps = [p for p in ALL_PROVIDERS if p.get("alp_tier") == tid]
            if not ps:
                continue
            print(f"\n  [{tier}]")
            for p in ps:
                if p.get("disabled_by_alp"):
                    st = "OFF (ALP)"
                else:
                    can, reason = self.tracker.can_call(p)
                    st = f"OK  {self.tracker.remaining(p)}" if can else f"WAIT {reason}"
                print(f"    {p['label'][:40]:<40} {','.join(p['ranked_for']):<20} {st}")
        print("="*55 + "\n")

    def cost_report(self):
        total, calls = 0.0, 0
        for lf in sorted(self._log_dir.glob("aafl_*.jsonl")):
            for line in open(lf):
                e = json.loads(line)
                total += e.get("cost_usd", 0.0)
                calls += 1
        print(f"[AAFL] Calls: {calls} | Spend: £{total:.4f} | ALP: {'SPENDING' if total > 0 else 'FREE'}")

    def detect(self, task):
        t = task.lower()
        if any(w in t for w in ["screenshot","screen","image","see","look","ui","window","visual","game"]):
            return "vision"
        if any(w in t for w in ["embed","vector","similarity"]):
            return "embed"
        if any(w in t for w in [".py","python","code","bug","fix","write","edit","function","script",".blk",".xml",".binds"]):
            return "code"
        if any(w in t for w in ["plan","strategy","decide","should","architect","roadmap","analyse","analyze"]):
            return "reason"
        if any(w in t for w in ["batch","all files","process all","convert all"]):
            return "batch"
        return "fast"

    def _log(self, r, task):
        entry = {"ts": datetime.datetime.now().isoformat(), "task": task[:80], "type": r.task_type, "provider": r.provider_id, "ok": r.success, "attempts": r.attempts, "sec": r.elapsed_sec, "cost": r.cost_usd}
        with open(self._log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    loop = AAFLLoop()
    loop.status()
    tests = ["fix this Python bug","read this screenshot","plan the orchestrator build","what is 2+2"]
    for t in tests:
        tt = loop.detect(t)
        print(f"  '{t}' -> {tt} -> {TASK_ROUTING[tt][0]}")
    print("\n[TEST] Quick call...")
    r = loop.run("Reply with exactly: AAFL_OK", task_type="fast", max_tokens=20)
    print(f"  {r.response} | provider={r.provider_id} | time={r.elapsed_sec}s")
    loop.cost_report()
