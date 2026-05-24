"""
chief_scout.py — Parallel scout orchestrator.
Reads afna_strategies.json, fires all active strategies simultaneously,
synthesises results via free LLM. Drop-in compatible with researcher.scout().
"""
import json
import sys
from pathlib import Path

CHIEF_SCOUT_MODEL = "mistral"  # swap to claude-opus-4-7 when funded

HERE = Path(__file__).parent


def _load_strategies() -> list:
    try:
        with open(HERE / "afna_strategies.json", encoding="utf-8") as f:
            return [s for s in json.load(f).get("strategies", [])
                    if not s.get("disabled", False)]
    except Exception as exc:
        print(f"[CHIEF_SCOUT] Load strategies failed: {exc}")
        return []


_CONFIG_DEFAULTS = {
    "active_strategies":    {"ddg": True, "reddit": True, "github": True, "youtube": True, "forum": True},
    "goal":                 "",
    "game_filter":          "all",
    "hardware_filter":      "any",
    "search_type":          "keybinds",
    "max_results_per_scout": 5,
    "timeout_seconds":      30,
    "synthesis_model":      "mistral",
    "reputation_floor":     3.0,
    "date_filter":          "all",
}


def load_config() -> dict:
    """Read chief_scout_config.json if present, fall back to _CONFIG_DEFAULTS."""
    cfg_path = HERE / "chief_scout_config.json"
    if cfg_path.exists():
        try:
            with open(cfg_path, encoding="utf-8") as f:
                user = json.load(f)
            return {**_CONFIG_DEFAULTS, **user}
        except Exception as exc:
            print(f"[CHIEF_SCOUT] Config read error ({exc}) — using defaults")
    return dict(_CONFIG_DEFAULTS)


def chief_scout(goal: str = None, mode: str = "goal") -> dict:
    """
    Parallel multi-strategy scout. Returns same format as researcher.scout().
    mode="goal"      — existing behaviour, uses goal text as query.
    mode="discovery" — auto-generates query to find sources/communities. Results
                       go to sources_library.json via source_library_manager.
    """
    from researcher import run_parallel_scouts, scout as _fallback

    cfg  = load_config()
    goal = goal or cfg.get("goal") or ""

    if mode == "discovery":
        return _run_discovery_mode(goal, cfg)


    # Filter strategies by active_strategies in config
    active = cfg.get("active_strategies", {})
    all_strats = _load_strategies()
    strategies = [s for s in all_strats if active.get(s["name"], True)]

    if not strategies:
        print("[CHIEF_SCOUT] No active strategies — falling back to basic scout")
        return _fallback(goal)

    try:
        data = run_parallel_scouts(
            goal, strategies,
            max_results_per_scout=cfg.get("max_results_per_scout", 5),
            timeout_seconds=cfg.get("timeout_seconds", 30),
            reputation_floor=cfg.get("reputation_floor", 3.0),
        )
    except Exception as exc:
        print(f"[CHIEF_SCOUT] Parallel scouts error ({exc}) — falling back")
        return _fallback(goal)

    if not data["results"]:
        print("[CHIEF_SCOUT] No results — falling back to basic scout")
        return _fallback(goal)

    model = cfg.get("synthesis_model") or CHIEF_SCOUT_MODEL
    briefing = _synthesise(goal, data, model=model)
    return {"results": data["results"], "briefing": briefing}


def _run_discovery_mode(goal: str, cfg: dict) -> dict:
    """
    Feature 8 — discovery mode: find source communities related to project topic.
    Auto-generates query from recent memory_bank entries if goal is empty.
    Results saved to sources_library.json.
    """
    from researcher import run_parallel_scouts, scout as _fallback

    # Auto-generate discovery query
    topic_hint = goal or "VKB joystick Star Citizen War Thunder input device"
    query = (f"Find websites forums subreddits YouTube channels Discord servers "
             f"related to {topic_hint}")

    active      = cfg.get("active_strategies", {})
    all_strats  = _load_strategies()
    strategies  = [s for s in all_strats if active.get(s["name"], True)]

    try:
        data = run_parallel_scouts(
            query, strategies,
            max_results_per_scout=cfg.get("max_results_per_scout", 5),
            timeout_seconds=cfg.get("timeout_seconds", 30),
        )
    except Exception:
        data = _fallback(query)

    # Save results to sources_library.json
    try:
        from source_library_manager import add_source
        for r in data.get("results", []):
            add_source(
                url=r.get("url", ""),
                domain=r.get("domain", ""),
                description=r.get("snippet", r.get("title", ""))[:120],
                tags=["discovery"],
            )
    except Exception:
        pass

    return data


def _synthesise(goal: str, data: dict, model: str = None) -> str:
    """Synthesise parallel results into one ranked briefing via free LLM."""
    effective_model = model or CHIEF_SCOUT_MODEL
    try:
        from aafl_core import AAFLCore
        aafl = AAFLCore(dry_run=False, allow_paid=False)

        sources = ""
        for i, r in enumerate(data["results"][:6], 1):
            sources += (f"{i}. [{r.get('strategy','?')}] {r.get('title','')}: "
                        f"{r.get('snippet','')}\n   URL: {r.get('url','')}\n")

        task_type = "batch" if "mistral" in effective_model else "reason"
        prompt = (
            f"Goal: {goal}\n\nSources found by parallel scouts:\n{sources}\n"
            f"Write a ranked briefing of the top 3 most relevant sources, "
            f"2 sentences each. Most relevant first. No preamble. No commentary."
        )
        result = aafl.run(task=prompt, task_type=task_type, max_tokens=400)
        if result.ok and result.response.strip():
            return f"Chief Scout briefing:\n{result.response.strip()}"
    except Exception as exc:
        print(f"[CHIEF_SCOUT] Synthesis failed ({exc}) — using raw briefing")

    return data["briefing"]


if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or "Star Citizen joystick axis spinning fix"
    print(f"[CHIEF_SCOUT] Smoke test")
    print(f"[CHIEF_SCOUT] Goal: {goal}")
    print("=" * 60)
    result = chief_scout(goal)
    print(f"\nSources found: {len(result['results'])}")
    print()
    print(result["briefing"])
    print("=" * 60)
    print("[CHIEF_SCOUT] Smoke test complete — no crashes.")
