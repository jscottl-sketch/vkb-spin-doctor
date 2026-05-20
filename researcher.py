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


def _scout_ddg(goal: str) -> list:
    raw = []
    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(goal, max_results=5))
    except Exception:
        return []
    return [{"title": r.get("title",""), "url": r.get("href",""),
             "snippet": r.get("body","")[:200], "domain": _extract_domain(r.get("href","")),
             "top": False, "strategy": "ddg"} for r in raw]


def _scout_reddit(goal: str) -> list:
    """Reddit PRAW search. Needs REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET in .env."""
    try:
        import praw, os
        reddit = praw.Reddit(
            client_id=os.environ.get("REDDIT_CLIENT_ID",""),
            client_secret=os.environ.get("REDDIT_CLIENT_SECRET",""),
            user_agent="VKBSpinDoctor/1.0",
        )
        results = []
        for sub in ("hoggit", "starcitizen", "EliteDangerous", "warthunder"):
            try:
                for post in reddit.subreddit(sub).search(goal, limit=2):
                    results.append({"title": post.title, "url": f"https://reddit.com{post.permalink}",
                                    "snippet": (post.selftext or "")[:200], "domain": "reddit.com",
                                    "top": False, "strategy": "reddit"})
            except Exception:
                pass
        return results
    except Exception:
        return []


def _scout_github(goal: str) -> list:
    """GitHub Issues search via public API — no key needed, 60 req/hr."""
    try:
        import urllib.request, urllib.parse, json as _j
        q = urllib.parse.quote(goal + " joystick")
        url = f"https://api.github.com/search/issues?q={q}&per_page=5"
        req = urllib.request.Request(url, headers={"User-Agent": "VKBSpinDoctor/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            items = _j.loads(resp.read()).get("items", [])
        return [{"title": it.get("title",""), "url": it.get("html_url",""),
                 "snippet": (it.get("body") or "")[:200], "domain": "github.com",
                 "top": False, "strategy": "github"} for it in items[:5]]
    except Exception:
        return []


def _scout_youtube(goal: str) -> list:
    """YouTube transcript search. Needs youtube-transcript-api installed."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        video_ids = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(f"site:youtube.com {goal}", max_results=3):
                    href = r.get("href", "")
                    vid = None
                    if "v=" in href:
                        vid = href.split("v=")[1].split("&")[0]
                    elif "youtu.be/" in href:
                        vid = href.split("youtu.be/")[1].split("?")[0]
                    if vid:
                        video_ids.append((r.get("title",""), href, vid))
        except Exception:
            pass
        results = []
        for title, url, vid in video_ids[:2]:
            try:
                tx = YouTubeTranscriptApi.get_transcript(vid)
                text = " ".join(t["text"] for t in tx[:30])[:300]
                results.append({"title": title, "url": url, "snippet": text,
                                 "domain": "youtube.com", "top": False, "strategy": "youtube"})
            except Exception:
                pass
        return results
    except Exception:
        return []


def _scout_forum(goal: str) -> list:
    """Direct HTTP crawler for gaming forums. Needs beautifulsoup4 installed."""
    try:
        from bs4 import BeautifulSoup
        import urllib.request, urllib.parse
        forums = [
            f"https://forum.warthunder.com/search/?q={urllib.parse.quote(goal)}",
            f"https://robertsspaceindustries.com/spectrum/search?query={urllib.parse.quote(goal)}",
        ]
        results = []
        kws = set(goal.lower().split()[:4])
        for base_url in forums:
            try:
                req = urllib.request.Request(base_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    soup = BeautifulSoup(resp.read(), "html.parser")
                for link in soup.find_all("a", href=True)[:15]:
                    text = link.get_text(strip=True)
                    if len(text) > 10 and kws & set(text.lower().split()):
                        href = link["href"]
                        if href.startswith("/"):
                            from urllib.parse import urlparse as _up
                            parsed = _up(base_url)
                            href = f"{parsed.scheme}://{parsed.netloc}{href}"
                        results.append({"title": text[:100], "url": href, "snippet": text[:200],
                                        "domain": _extract_domain(href), "top": False, "strategy": "forum"})
                if len(results) >= 5:
                    break
            except Exception:
                pass
        return results[:5]
    except Exception:
        return []


def run_parallel_scouts(goal: str, strategies: list = None, **kwargs) -> dict:
    """Fire all active AFNA scout strategies in parallel. Returns combined deduped results.
    kwargs: timeout_seconds (int), max_results_per_scout (int), reputation_floor (float)
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as _TE
    import json as _json
    from pathlib import Path as _Path

    timeout_sec   = int(kwargs.get("timeout_seconds", 30))
    max_per_strat = int(kwargs.get("max_results_per_scout", 5))

    _FNS = {"ddg": _scout_ddg, "reddit": _scout_reddit, "github": _scout_github,
            "youtube": _scout_youtube, "forum": _scout_forum}

    if strategies is None:
        try:
            sf = _Path(__file__).parent / "afna_strategies.json"
            with open(sf, encoding="utf-8") as f:
                strategies = [s for s in _json.load(f).get("strategies", [])
                               if not s.get("disabled", False)]
        except Exception:
            strategies = [{"name": "ddg"}]

    all_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_FNS[s["name"]], goal): s["name"]
                   for s in strategies if s.get("name") in _FNS}
        try:
            for future in as_completed(futures, timeout=timeout_sec):
                name = futures[future]
                try:
                    all_results.extend(future.result()[:max_per_strat])
                except Exception as exc:
                    print(f"[PARALLEL_SCOUT] {name} failed: {exc}")
        except _TE:
            print("[PARALLEL_SCOUT] Timeout — using partial results")

    seen, deduped = set(), []
    for r in all_results:
        url = r.get("url", "")
        if url not in seen:
            seen.add(url)
            deduped.append(r)

    try:
        from memory_bank import get_top_sources, get_blocked_sources
        top_d, blocked_d = set(get_top_sources()), set(get_blocked_sources())
        deduped = [r for r in deduped if r.get("domain","") not in blocked_d]
        deduped.sort(key=lambda r: (1 if r.get("domain","") in top_d else 0), reverse=True)
    except Exception:
        pass

    if not deduped:
        return scout(goal)

    top3 = deduped[:3]
    lines = [f"- [{r['title']}]({r['url']}): {r['snippet']}" for r in top3]
    briefing = "Web context (parallel scouts):\n" + "\n".join(lines)
    return {"results": deduped, "briefing": briefing}


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
