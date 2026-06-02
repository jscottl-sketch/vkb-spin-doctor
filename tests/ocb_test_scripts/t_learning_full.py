"""t_learning_full — Full learning machine integration test: reindex → query → scan → report."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

results = {}

# Step 1: reindex
try:
    from learning_machine.rag_engine import reindex_all
    stats = reindex_all()
    print(f"[t_learning_full] RAG reindex: {stats['doc_count']} docs, {stats['chunk_count']} chunks")
    results["rag_reindex"] = "PASS"
except Exception as exc:
    print(f"[t_learning_full] RAG reindex FAIL: {exc}")
    results["rag_reindex"] = "FAIL"

# Step 2: query
try:
    from learning_machine.rag_engine import query
    qr = query("spin doctor joystick fix", n_results=3)
    print(f"[t_learning_full] RAG query: {len(qr)} result(s)")
    results["rag_query"] = "PASS"
except Exception as exc:
    print(f"[t_learning_full] RAG query FAIL: {exc}")
    results["rag_query"] = "FAIL"

# Step 3: training scan
try:
    from learning_machine.training_prep import scan_results
    ts = scan_results()
    print(f"[t_learning_full] Training scan: {ts['pair_count']} pairs from {ts['total_runs']} runs")
    results["training_scan"] = "PASS"
except Exception as exc:
    print(f"[t_learning_full] Training scan FAIL: {exc}")
    results["training_scan"] = "FAIL"

# Step 4: feedback report
try:
    from learning_machine.feedback_loop import get_report
    report = get_report()
    print(f"[t_learning_full] Feedback report: {'exists' if report else 'empty (ok — no runs yet)'}")
    results["feedback_report"] = "PASS"
except Exception as exc:
    print(f"[t_learning_full] Feedback report FAIL: {exc}")
    results["feedback_report"] = "FAIL"

# Summary
passed = sum(1 for v in results.values() if v == "PASS")
total = len(results)
print(f"\n[t_learning_full] {'PASS' if passed == total else 'PARTIAL'} — {passed}/{total} steps passed")
for k, v in results.items():
    print(f"  {v}  {k}")

sys.exit(0 if passed == total else 1)
