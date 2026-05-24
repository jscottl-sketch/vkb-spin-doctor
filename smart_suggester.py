"""
smart_suggester.py — Feature 5: Smart Provider Suggester
Keyword-based provider recommendation with health cross-check.
Standalone: python smart_suggester.py "write a python function to parse XML"
"""
import json
import sys
from pathlib import Path

HERE          = Path(__file__).parent
LATEST_HEALTH = HERE / "health_results" / "latest_health.json"

# Keyword → provider mapping (no AI call needed)
_RULES = [
    {
        "keywords": ["code", "python", "script", "function", "bug", "fix", "def ",
                     "class", "import", "syntax", "parse", "implement"],
        "provider": "mistral_code",
        "label":    "Mistral Codestral",
        "reason":   "Goal contains coding keywords — Codestral is optimised for code",
    },
    {
        "keywords": ["search", "find", "research", "what", "who", "when", "where",
                     "latest", "news", "look up", "discover"],
        "provider": "gemini_flash",
        "label":    "Gemini 2.5 Flash",
        "reason":   "Goal is a search/research task — Gemini has strong web awareness",
    },
    {
        "keywords": ["write", "draft", "explain", "describe", "summarise", "summarize",
                     "document", "blog", "post", "copy"],
        "provider": "mistral_code",
        "label":    "Mistral Codestral",
        "reason":   "Goal is a writing/explanation task — Mistral produces clear prose",
    },
    {
        "keywords": ["analyse", "analyze", "compare", "review", "score", "evaluate",
                     "assess", "rank", "judge", "benchmark"],
        "provider": "cerebras",
        "label":    "Cerebras GPT-OSS 120B",
        "reason":   "Goal requires analysis/reasoning — Cerebras is fast and analytical",
    },
]

_DEFAULT_PROVIDER = "openrouter"
_DEFAULT_LABEL    = "OpenRouter Auto"


def _load_health() -> list:
    if LATEST_HEALTH.exists():
        try:
            data = json.loads(LATEST_HEALTH.read_text(encoding="utf-8"))
            return data.get("providers", [])
        except Exception:
            pass
    return []


def _is_green(provider_id: str, health: list) -> bool:
    for p in health:
        if p.get("id") == provider_id:
            return p.get("status") in ("GREEN", "YELLOW")
    return True  # assume OK if no health data


def _next_green(exclude: str, health: list) -> tuple[str, str]:
    for p in health:
        if p.get("id") != exclude and p.get("status") in ("GREEN", "YELLOW"):
            return p["id"], p.get("label", p["id"])
    return _DEFAULT_PROVIDER, _DEFAULT_LABEL


def suggest_provider(goal_text: str) -> dict:
    """
    Returns: {suggested_provider, label, confidence, reason, alternatives}
    No AI calls — pure keyword matching + health cross-check.
    """
    goal_lower = goal_text.lower()
    health     = _load_health()

    matched = None
    for rule in _RULES:
        if any(kw in goal_lower for kw in rule["keywords"]):
            matched = rule
            break

    if matched is None:
        # Default: pick highest-reputation green provider
        for p in health:
            if p.get("status") in ("GREEN", "YELLOW"):
                suggested   = p["id"]
                label       = p.get("label", p["id"])
                confidence  = "low"
                reason      = f"No keyword match — using best available provider: {label}"
                alternatives = [q["id"] for q in health
                                if q.get("status") in ("GREEN","YELLOW") and q["id"] != suggested][:3]
                return {
                    "suggested_provider": suggested,
                    "label":              label,
                    "confidence":         confidence,
                    "reason":             reason,
                    "alternatives":       alternatives,
                }
        return {
            "suggested_provider": _DEFAULT_PROVIDER,
            "label":              _DEFAULT_LABEL,
            "confidence":         "low",
            "reason":             "No keyword match and no health data available",
            "alternatives":       [],
        }

    suggested  = matched["provider"]
    label      = matched["label"]
    confidence = "high"

    # Cross-check against health data — if RED, pick next green
    if health and not _is_green(suggested, health):
        alt_id, alt_label = _next_green(suggested, health)
        reason = (f"{matched['reason']}. However {label} is currently RED — "
                  f"switching to {alt_label}")
        suggested = alt_id
        label     = alt_label
        confidence = "medium"
    else:
        reason = matched["reason"]

    alternatives = [p["id"] for p in health
                    if p.get("status") in ("GREEN","YELLOW")
                    and p["id"] != suggested][:3]

    return {
        "suggested_provider": suggested,
        "label":              label,
        "confidence":         confidence,
        "reason":             reason,
        "alternatives":       alternatives,
    }


if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or "write a python function to parse XML"
    result = suggest_provider(goal)
    print(f"Goal: {goal}")
    print(f"  Suggested : {result['suggested_provider']} ({result['label']})")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Reason    : {result['reason']}")
    print(f"  Alternates: {result['alternatives']}")
