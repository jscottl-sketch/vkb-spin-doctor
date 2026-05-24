"""
cost_predictor.py — Estimate token cost before sending a goal to a provider.
Free providers show $0.00 but estimated time.
"""

PROVIDER_RATES = {
    "mistral":      {"cost_per_1k_tokens": 0.0,   "tokens_per_second": 60,  "free": True,  "label": "Mistral Free"},
    "cerebras":     {"cost_per_1k_tokens": 0.0,   "tokens_per_second": 180, "free": True,  "label": "Cerebras Free"},
    "gemini":       {"cost_per_1k_tokens": 0.0,   "tokens_per_second": 50,  "free": True,  "label": "Gemini Free"},
    "openrouter":   {"cost_per_1k_tokens": 0.0015,"tokens_per_second": 40,  "free": False, "label": "OpenRouter"},
    "cohere":       {"cost_per_1k_tokens": 0.0005,"tokens_per_second": 35,  "free": False, "label": "Cohere"},
    "huggingface":  {"cost_per_1k_tokens": 0.0,   "tokens_per_second": 20,  "free": True,  "label": "HuggingFace Free"},
    "auto":         {"cost_per_1k_tokens": 0.0,   "tokens_per_second": 60,  "free": True,  "label": "Auto (Best Free)"},
}

WORDS_PER_TOKEN = 0.75


def estimate_cost(goal_text: str, provider_name: str = "auto") -> dict:
    """
    Estimate cost for a goal on a given provider.
    Returns: estimated_tokens, estimated_cost_usd, estimated_time_seconds, provider_used
    """
    provider_key = provider_name.lower().strip()
    if provider_key not in PROVIDER_RATES:
        provider_key = "auto"

    rate = PROVIDER_RATES[provider_key]

    word_count = len(goal_text.split())
    input_tokens = int(word_count / WORDS_PER_TOKEN)
    output_tokens = min(int(input_tokens * 2.5), 4000)
    total_tokens = input_tokens + output_tokens

    cost_usd = 0.0 if rate["free"] else (total_tokens / 1000) * rate["cost_per_1k_tokens"]

    tps = rate["tokens_per_second"]
    estimated_time_seconds = round(output_tokens / tps, 1) if tps > 0 else 0

    return {
        "provider_name":           provider_key,
        "provider_label":          rate["label"],
        "estimated_input_tokens":  input_tokens,
        "estimated_output_tokens": output_tokens,
        "estimated_total_tokens":  total_tokens,
        "estimated_cost_usd":      round(cost_usd, 6),
        "estimated_time_seconds":  estimated_time_seconds,
        "is_free":                 rate["free"],
    }


def cheapest_provider() -> dict:
    """Return the free provider with the highest tokens_per_second."""
    free = {k: v for k, v in PROVIDER_RATES.items() if v["free"] and k != "auto"}
    if not free:
        return {"provider_name": "auto", "label": "Auto"}
    best = max(free.items(), key=lambda x: x[1]["tokens_per_second"])
    return {"provider_name": best[0], "label": best[1]["label"],
            "tokens_per_second": best[1]["tokens_per_second"]}


def all_providers() -> list:
    """Return all provider names."""
    return [k for k in PROVIDER_RATES if k != "auto"]
