import json
import time
from datetime import datetime
import litellm

litellm.suppress_debug_info = True

PROVIDERS = [
    {"name": "Gemini",     "model": "gemini/gemini-1.5-flash",         "env": "GEMINI_API_KEY"},
    {"name": "Mistral",    "model": "mistral/mistral-small-latest",     "env": "MISTRAL_API_KEY"},
    {"name": "OpenRouter", "model": "openrouter/openai/gpt-3.5-turbo",  "env": "OPENROUTER_API_KEY"},
    {"name": "Cerebras",   "model": "cerebras/llama3.1-8b",             "env": "CEREBRAS_API_KEY"},
]

PING_MSG = [{"role": "user", "content": "ping"}]


def ping(provider: dict) -> dict:
    start = time.time()
    try:
        litellm.completion(
            model=provider["model"],
            messages=PING_MSG,
            max_tokens=5,
            timeout=15,
        )
        elapsed = round(time.time() - start, 2)
        return {"name": provider["name"], "status": "alive", "latency_s": elapsed, "error": None}
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        return {"name": provider["name"], "status": "dead", "latency_s": elapsed, "error": str(e)[:200]}


def main():
    print(f"\n=== AAFL Provider Health Check  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    results = []
    for p in PROVIDERS:
        print(f"  Pinging {p['name']}...", end=" ", flush=True)
        result = ping(p)
        results.append(result)
        tag = "OK  " if result["status"] == "alive" else "DEAD"
        print(f"[{tag}]  {result['latency_s']}s")
        if result["error"]:
            print(f"         {result['error']}")

    log_path = "health_log.json"
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append({"timestamp": datetime.now().isoformat(), "results": results})
    history = history[-500:]

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    alive = sum(1 for r in results if r["status"] == "alive")
    print(f"\n  {alive}/{len(results)} providers alive  —  log saved to {log_path}\n")
    return alive


if __name__ == "__main__":
    main()
