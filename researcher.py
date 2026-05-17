"""
researcher.py — DuckDuckGo search wrapper.
Phase A: research(query) → formatted string, top 5 results.
Phase C: scout(goal) → dict {results, briefing} with source reputation filtering.
"""
from urllib.parse import urlparse

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


def research(query: str, max_results: int = 5) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return f"No results found for: {query}"

        lines = [f"Search results for: {query}\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            body  = r.get("body", "")[:200]
            href  = r.get("href", "")
            lines.append(f"{i}. {title}")
            lines.append(f"   {body}")
            if href:
                lines.append(f"   URL: {href}")
            lines.append("")
        return "\n".join(lines)

    except Exception as exc:
        return f"Search unavailable — proceed with existing knowledge. (Error: {exc})"


def _extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return ""


def scout(goal: str, max_results: int = 5) -> dict:
    """Search for goal, filter by source reputation, return dict {results, briefing}."""
    from memory_bank import get_blocked_sources, get_top_sources

    blocked = set(get_blocked_sources())
    top     = set(get_top_sources())

    raw = []
    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(goal, max_results=max_results * 2))
    except Exception:
        pass

    results = []
    for r in raw:
        url    = r.get("href", "")
        domain = _extract_domain(url)
        if domain and domain in blocked:
            continue
        results.append({
            "title":   r.get("title", ""),
            "url":     url,
            "snippet": r.get("body", "")[:200],
            "domain":  domain,
            "top":     domain in top,
        })
        if len(results) >= max_results:
            break

    top3 = results[:3]
    if top3:
        lines = [f"- [{r['title']}]({r['url']}): {r['snippet']}" for r in top3]
        briefing = "Web context:\n" + "\n".join(lines)
    else:
        briefing = "No web context available — proceed with existing knowledge."

    return {"results": results, "briefing": briefing}


if __name__ == "__main__":
    print("researcher.py self-test — research()")
    print("=" * 60)
    print(research("Python asyncio tutorial"))
    print("=" * 60)
    print("\nscout() test — goal: 'VKB NXT EVO joystick not detected'")
    print("=" * 60)
    s = scout("VKB NXT EVO joystick not detected")
    print(f"Sources found: {len(s['results'])}")
    print(s["briefing"])
    print("=" * 60)
