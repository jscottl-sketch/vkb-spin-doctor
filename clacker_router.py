"""
clacker_router.py — CLACKER task classifier.
Classifies a task description into CODE / RESEARCH / AAFL / MAINTENANCE / OPUS.
"""

_CODE_KEYWORDS = [
    "mission_control.html", ".html", "css", "tab", "button", "panel", "style",
    "colour", "color", ".py", "def ", "import ", "endpoint", "mcc_server",
    "loop_manager", "aafl_core", "ocb_runner", ".json",
]
_RESEARCH_KEYWORDS = [
    "search", "find online", "look up", "research", "keybind", "competitor",
    "reddit", "github", "youtube", "forum",
]
_AAFL_KEYWORDS = [
    "run loop", "aafl goal", "overnight", "benchmark", "autonomous run",
]
_MAINTENANCE_KEYWORDS = [
    "save", "wccs", "status.md", "session log", "sesum", "git commit",
    "health check", "mot", "diagnose",
]
_OPUS_KEYWORDS = [
    "architecture", "debug why", "design the", "strategy", "brainstorm",
    "what should", "is this right",
]


def classify(task_text: str) -> dict:
    """
    Classify a task text.  Returns:
    {type, subsystem, provider, confidence, reason}
    Priority order: OPUS wins if matched or confidence < 0.7.
    """
    t = task_text.lower()

    # OPUS always wins when matched
    for kw in _OPUS_KEYWORDS:
        if kw in t:
            return {"type": "OPUS", "subsystem": "claude_chat",
                    "provider": "opus", "confidence": 1.0,
                    "reason": "Needs big brain"}

    # CODE
    code_hits = sum(1 for kw in _CODE_KEYWORDS if kw in t)
    if code_hits > 0:
        return {"type": "CODE", "subsystem": "ocb_runner",
                "provider": "codestral", "confidence": 0.9,
                "reason": f"{code_hits} code keyword(s) matched"}

    # RESEARCH
    for kw in _RESEARCH_KEYWORDS:
        if kw in t:
            return {"type": "RESEARCH", "subsystem": "scout_swarm",
                    "provider": "mistral", "confidence": 0.9,
                    "reason": f"research keyword: {kw!r}"}

    # AAFL
    for kw in _AAFL_KEYWORDS:
        if kw in t:
            return {"type": "AAFL", "subsystem": "loop_manager",
                    "provider": "any_free", "confidence": 0.9,
                    "reason": f"aafl keyword: {kw!r}"}

    # MAINTENANCE
    for kw in _MAINTENANCE_KEYWORDS:
        if kw in t:
            return {"type": "MAINTENANCE", "subsystem": "aafl_wccs",
                    "provider": "mistral", "confidence": 0.85,
                    "reason": f"maintenance keyword: {kw!r}"}

    # Low confidence → OPUS
    return {"type": "OPUS", "subsystem": "claude_chat",
            "provider": "opus", "confidence": 0.5,
            "reason": "No clear match — escalate to big brain"}


def classify_all(phases: list) -> dict:
    """
    Classify every task in every phase.
    Returns {results, has_opus_tasks, opus_task_list}.
    """
    results = []
    opus_tasks = []
    for phase in phases:
        for task in phase.get("tasks", []):
            cls = classify(task["text"])
            results.append({
                "phase": phase["phase_num"],
                "task": task["num"],
                "text": task["text"][:80],
                "classification": cls,
            })
            if cls["type"] == "OPUS":
                opus_tasks.append({
                    "phase": phase["phase_num"],
                    "task": task["num"],
                    "text": task["text"][:80],
                    "reason": cls.get("reason", ""),
                })
    return {
        "results": results,
        "has_opus_tasks": len(opus_tasks) > 0,
        "opus_task_list": opus_tasks,
    }
