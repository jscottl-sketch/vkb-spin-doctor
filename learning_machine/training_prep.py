"""
training_prep.py — Training Data Pipeline.
Scans loop_output/*.json results, extracts high-quality pairs, saves alpaca-format JSONL.
"""
import json
import datetime
from pathlib import Path

HERE = Path(__file__).parent.parent
LOOP_OUTPUT_DIR = HERE / "loop_output"
TRAINING_DATA_FILE = HERE / "data" / "training_data.jsonl"
TRAINING_STATS_FILE = HERE / "data" / "training_stats.json"
MIN_SCORE = 7.0


def _load_result_file(path: Path) -> dict | None:
    """Parse a loop_output JSON file. Returns dict or None."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return None


def scan_results() -> dict:
    """
    Scan loop_output/*.json, extract pairs scored >= MIN_SCORE.
    Saves to data/training_data.jsonl in alpaca format.
    Returns stats dict.
    """
    LOOP_OUTPUT_DIR.mkdir(exist_ok=True)

    json_files = sorted(LOOP_OUTPUT_DIR.glob("*.json"))
    total_runs = len(json_files)
    pairs = []

    for fpath in json_files:
        result = _load_result_file(fpath)
        if not result:
            continue
        score = result.get("quality_score") or result.get("score") or result.get("eval_overall")
        try:
            score = float(score)
        except (TypeError, ValueError):
            continue
        if score < MIN_SCORE:
            continue

        goal = result.get("goal") or result.get("instruction") or result.get("task", "")
        plan = result.get("plan") or ""
        work = result.get("work") or result.get("output") or result.get("response", "")
        context = plan.strip()
        response = work.strip()

        if not goal or not response:
            continue

        pairs.append({
            "instruction": goal,
            "input": context,
            "output": response,
            "score": score,
            "source_file": fpath.name,
        })

    TRAINING_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with TRAINING_DATA_FILE.open("w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    avg_score = round(sum(p["score"] for p in pairs) / len(pairs), 2) if pairs else 0.0

    stats = {
        "pair_count": len(pairs),
        "total_runs": total_runs,
        "avg_score": avg_score,
        "min_score_threshold": MIN_SCORE,
        "last_updated": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    TRAINING_STATS_FILE.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print(f"[TRAINING] {len(pairs)} high-quality training pairs extracted from {total_runs} total runs")
    return stats


def get_stats() -> dict:
    """Return cached training stats."""
    if TRAINING_STATS_FILE.exists():
        try:
            return json.loads(TRAINING_STATS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"pair_count": 0, "total_runs": 0, "avg_score": 0.0, "last_updated": None}


if __name__ == "__main__":
    stats = scan_results()
    print(f"[TRAINING] Pair count : {stats['pair_count']}")
    print(f"[TRAINING] Total runs : {stats['total_runs']}")
    print(f"[TRAINING] Avg score  : {stats['avg_score']}")
