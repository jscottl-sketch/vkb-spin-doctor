"""t_rag_index — RAG reindex test. Runs reindex_all() and prints stats."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from learning_machine.rag_engine import reindex_all, get_stats
    stats = reindex_all()
    print(f"[t_rag_index] PASS — {stats['doc_count']} documents, {stats['chunk_count']} chunks indexed")
    sys.exit(0)
except Exception as exc:
    print(f"[t_rag_index] FAIL — {exc}")
    sys.exit(1)
