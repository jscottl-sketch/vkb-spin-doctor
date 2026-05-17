"""
researcher.py — DuckDuckGo search wrapper.
Takes a query string, returns top 5 results as formatted string.
Fallback: "Search unavailable — proceed with existing knowledge." on any error.
"""
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


if __name__ == "__main__":
    print("researcher.py self-test — searching 'Python asyncio tutorial'")
    print("=" * 60)
    print(research("Python asyncio tutorial"))
    print("=" * 60)
