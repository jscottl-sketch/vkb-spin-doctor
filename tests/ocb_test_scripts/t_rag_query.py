"""t_rag_query — RAG query test. Queries 'spin doctor joystick fix' and prints top 3."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from learning_machine.rag_engine import query
    results = query("spin doctor joystick fix", n_results=3)
    if results:
        print(f"[t_rag_query] PASS — {len(results)} result(s) returned")
        for r in results:
            print(f"  [{r['rank']}] {r['source']} (dist={r['distance']}) — {r['text'][:80]}...")
        sys.exit(0)
    else:
        print("[t_rag_query] WARN — 0 results returned (collection may be empty, run t_rag_index first)")
        sys.exit(0)
except Exception as exc:
    print(f"[t_rag_query] FAIL — {exc}")
    sys.exit(1)
