"""
evaluator.py — Score a text result 0-10 for quality.
Rubric: completeness (answers the goal?), clarity (readable?), accuracy (no obvious errors?).
Input: result string + optional goal string. Output: dict with scores and overall.
Pure logic — no external APIs.
"""


def evaluate(result: str, goal: str = "") -> dict:
    completeness = _score_completeness(result, goal)
    clarity      = _score_clarity(result)
    accuracy     = _score_accuracy(result)
    overall      = round((completeness + clarity + accuracy) / 3, 2)

    # Feature 3 — read confidence threshold from aafl_config.json
    threshold = 7.0
    try:
        from aafl_config_reader import get_confidence_threshold
        threshold = get_confidence_threshold()
    except Exception:
        pass
    status = "PASS" if overall >= threshold else "RETRY"

    scores = {
        "completeness": completeness,
        "clarity":      clarity,
        "accuracy":     accuracy,
        "overall":      overall,
        "status":       status,
        "threshold":    threshold,
    }
    if overall >= 9.0:
        try:
            from promo_queue import add_to_promo
            add_to_promo(
                content=result[:500],
                source=goal[:200] if goal else "unknown",
                reason=f"Auto-promoted: score {overall}/10",
            )
        except Exception:
            pass
    return scores


def _score_completeness(result: str, goal: str) -> float:
    if not result.strip():
        return 0.0
    if not goal.strip():
        return 5.0 if len(result) > 50 else 2.0

    goal_words   = {w.lower() for w in goal.split() if len(w) > 3}
    result_lower = result.lower()

    if not goal_words:
        return 5.0

    matched = sum(1 for w in goal_words if w in result_lower)
    ratio   = matched / len(goal_words)
    score   = ratio * 8.0
    if len(result) > 200:
        score = min(score + 1.0, 10.0)
    if len(result) > 500:
        score = min(score + 1.0, 10.0)
    return round(score, 1)


def _score_clarity(result: str) -> float:
    if not result.strip():
        return 0.0

    score     = 5.0
    sentences = [s.strip() for s in result.replace("!", ".").replace("?", ".").split(".") if s.strip()]

    if not sentences:
        return 2.0

    avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
    if avg_len < 5:
        score -= 1.0
    elif avg_len > 40:
        score -= 1.0

    if any(c in result for c in (".", ",", ":", "\n")):
        score += 1.5
    if len(result.splitlines()) > 3:
        score += 1.5
    if any(p in result for p in ("```", "def ", "return ")):
        score += 1.0

    return round(min(max(score, 0.0), 10.0), 1)


def _score_accuracy(result: str) -> float:
    if not result.strip():
        return 0.0

    score        = 8.0
    result_lower = result.lower()

    error_patterns = [
        "traceback", "syntaxerror", "nameerror", "typeerror", "valueerror",
        "indentationerror", "undefined", "null pointer", "segfault",
        "i don't know", "i cannot", "i'm unable", "as an ai, i",
        "i apologize", "i'm sorry, but i cannot",
    ]
    for pat in error_patterns:
        if pat in result_lower:
            score -= 2.0

    for pat in ("def ", "return ", "```", "example", "output:", "result:"):
        if pat in result_lower:
            score = min(score + 0.5, 10.0)

    return round(max(score, 0.0), 1)


if __name__ == "__main__":
    test_result = '''def top_three(numbers):
    """Return the three largest numbers from a list."""
    if not numbers:
        raise ValueError("List is empty")
    return sorted(numbers, reverse=True)[:3]

# Example
print(top_three([1, 5, 3, 9, 2]))  # Output: [9, 5, 3]
'''
    test_goal = (
        "Write a Python function that takes a list of numbers and "
        "returns the three largest. Include error handling and a docstring."
    )
    scores = evaluate(test_result, test_goal)
    print("Evaluator self-test")
    print("=" * 40)
    for k, v in scores.items():
        print(f"  {k:15}: {v}")
    print("=" * 40)
