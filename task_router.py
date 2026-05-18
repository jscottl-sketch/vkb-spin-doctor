import sys

TIERS = {
    "AAFL": {
        "keywords": [
            "research", "search", "scrape", "gather", "collect", "fetch", "download",
            "crawl", "find", "lookup", "repeat", "automate", "batch", "monitor",
            "watch", "poll", "aggregate", "scan", "list", "data", "web",
        ],
        "estimated_cost": "low (~$0.001-0.01)",
        "recommended_action": "Route to AAFL agent for automated execution.",
    },
    "CLAC": {
        "keywords": [
            "code", "debug", "fix", "build", "implement", "write", "develop",
            "refactor", "function", "class", "bug", "error", "feature", "test",
            "deploy", "script", "program", "module", "api", "endpoint", "syntax",
        ],
        "estimated_cost": "low-medium (~$0.01-0.05)",
        "recommended_action": "Route to CLAC for code generation or debugging.",
    },
    "SONNET": {
        "keywords": [
            "plan", "explain", "describe", "summarize", "decide", "compare",
            "review", "analyze", "design", "draft", "outline", "recommend",
            "assess", "evaluate", "understand", "clarify", "document", "medium",
        ],
        "estimated_cost": "medium (~$0.05-0.20)",
        "recommended_action": "Use Sonnet for reasoning, planning, or explanation tasks.",
    },
    "OPUS": {
        "keywords": [
            "architecture", "strategy", "complex", "advanced", "system design",
            "trade-off", "tradeoff", "optimize", "scalability", "migration",
            "overhaul", "redesign", "enterprise", "critical", "fundamental",
            "paradigm", "deep", "intricate", "sophisticated", "comprehensive",
        ],
        "estimated_cost": "high (~$0.20-1.00+)",
        "recommended_action": "Escalate to Opus only after Scott approves. High-cost task.",
    },
}


def classify(task_text: str) -> dict:
    text = task_text.lower()
    scores = {}

    for tier, data in TIERS.items():
        hit_words = [kw for kw in data["keywords"] if kw in text]
        scores[tier] = hit_words

    ranked = sorted(scores, key=lambda t: len(scores[t]), reverse=True)
    winner = ranked[0]

    # Fallback: no keywords matched at all — default to SONNET
    if not scores[winner]:
        winner = "SONNET"
        reason = "No strong keyword signals found. Defaulting to Sonnet."
    else:
        hits = scores[winner]
        reason = f"Matched {len(hits)} keyword(s): {', '.join(hits[:5])}"

    if winner == "OPUS":
        print("\n⚠️  OPUS-LEVEL TASK DETECTED — advise Scott before proceeding\n")

    return {
        "tier": winner,
        "reason": reason,
        "estimated_cost": TIERS[winner]["estimated_cost"],
        "recommended_action": TIERS[winner]["recommended_action"],
    }


def _print_result(result: dict) -> None:
    print("=" * 50)
    print(f"  TIER:    {result['tier']}")
    print(f"  REASON:  {result['reason']}")
    print(f"  COST:    {result['estimated_cost']}")
    print(f"  ACTION:  {result['recommended_action']}")
    print("=" * 50)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python task_router.py \"your task description here\"")
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    result = classify(task)
    _print_result(result)
