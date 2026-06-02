"""
rag_engine.py — RAG (Retrieval Augmented Generation) engine.
Indexes project files into ChromaDB; query() returns top-N relevant chunks.
Stored locally at data/rag_db/ — no cloud.
"""
import json
import datetime
from pathlib import Path

HERE = Path(__file__).parent.parent
RAG_DB_PATH = str(HERE / "data" / "rag_db")
COLLECTION_NAME = "aafl_knowledge"

_SOURCE_FILES = [
    HERE / "STATUS.md",
    HERE / "INDEX.md",
    HERE / "HISTORY.md",
    HERE / "ACCA.md",
    HERE / "data" / "solution_database.json",
    HERE / "data" / "instructions_db.json",
    HERE / "data" / "storm_feed.json",
    HERE / "data" / "wento_queue.json",
]

_STATS_FILE = HERE / "data" / "rag_stats.json"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def _chunk_text(text: str, source: str) -> list[dict]:
    """Split text into overlapping chunks. Returns list of {id, text, source}."""
    chunks = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    for i, start in enumerate(range(0, max(1, len(text)), step)):
        chunk = text[start:start + CHUNK_SIZE]
        if not chunk.strip():
            continue
        chunks.append({
            "id": f"{source}::{i}",
            "text": chunk,
            "source": source,
        })
    return chunks


def _load_file(path: Path) -> str:
    """Load a file as text. JSON files are pretty-printed."""
    if not path.exists():
        return ""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".json":
            try:
                data = json.loads(raw)
                return json.dumps(data, indent=2, ensure_ascii=False)[:50000]
            except Exception:
                return raw[:50000]
        return raw[:100000]
    except Exception:
        return ""


def _get_client():
    import chromadb
    client = chromadb.PersistentClient(path=RAG_DB_PATH)
    return client


def _save_stats(doc_count: int, chunk_count: int):
    _STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _STATS_FILE.write_text(json.dumps({
        "doc_count": doc_count,
        "chunk_count": chunk_count,
        "last_indexed": datetime.datetime.now().isoformat(timespec="seconds"),
    }, indent=2), encoding="utf-8")


def get_stats() -> dict:
    """Return current RAG stats from disk cache."""
    if _STATS_FILE.exists():
        try:
            return json.loads(_STATS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"doc_count": 0, "chunk_count": 0, "last_indexed": None}


def reindex_all() -> dict:
    """Full reindex: scans session_logs/*.md + source files. Returns stats dict."""
    client = _get_client()

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    all_chunks = []

    # Session logs
    session_dir = HERE / "session_logs"
    if session_dir.exists():
        for md_file in sorted(session_dir.glob("*.md")):
            text = _load_file(md_file)
            if text:
                all_chunks.extend(_chunk_text(text, str(md_file.name)))

    # Source files
    for src_path in _SOURCE_FILES:
        text = _load_file(src_path)
        if text:
            all_chunks.extend(_chunk_text(text, src_path.name))

    if not all_chunks:
        print("[RAG] No content to index.")
        _save_stats(0, 0)
        return {"doc_count": 0, "chunk_count": 0}

    # Deduplicate IDs
    seen_ids = set()
    unique_chunks = []
    for c in all_chunks:
        if c["id"] not in seen_ids:
            seen_ids.add(c["id"])
            unique_chunks.append(c)

    ids = [c["id"] for c in unique_chunks]
    docs = [c["text"] for c in unique_chunks]
    metas = [{"source": c["source"]} for c in unique_chunks]

    batch_size = 500
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i + batch_size],
            documents=docs[i:i + batch_size],
            metadatas=metas[i:i + batch_size],
        )

    doc_count = len(set(c["source"] for c in unique_chunks))
    chunk_count = len(unique_chunks)
    _save_stats(doc_count, chunk_count)

    print(f"[RAG] Reindex complete — {doc_count} documents, {chunk_count} chunks")
    return {"doc_count": doc_count, "chunk_count": chunk_count}


def index_file(path: str | Path) -> dict:
    """Add or update a single file in the collection."""
    path = Path(path)
    text = _load_file(path)
    if not text:
        return {"ok": False, "reason": "empty or missing"}

    client = _get_client()
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        reindex_all()
        return {"ok": True, "note": "collection missing — triggered full reindex"}

    chunks = _chunk_text(text, path.name)
    if not chunks:
        return {"ok": False, "reason": "no chunks produced"}

    ids = [c["id"] for c in chunks]
    docs = [c["text"] for c in chunks]
    metas = [{"source": c["source"]} for c in chunks]

    try:
        collection.upsert(ids=ids, documents=docs, metadatas=metas)
    except Exception as exc:
        return {"ok": False, "reason": str(exc)}

    stats = get_stats()
    stats["chunk_count"] = stats.get("chunk_count", 0) + len(chunks)
    stats["last_indexed"] = datetime.datetime.now().isoformat(timespec="seconds")
    _save_stats(stats.get("doc_count", 0), stats["chunk_count"])

    return {"ok": True, "chunks_added": len(chunks)}


def query(text: str, n_results: int = 5) -> list[dict]:
    """Search the collection. Returns top n_results chunks with source and text."""
    if not text or not text.strip():
        return []
    client = _get_client()
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        return []

    try:
        count = collection.count()
        if count == 0:
            return []
        n = min(n_results, count)
        results = collection.query(query_texts=[text], n_results=n)
        out = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            dist = results["distances"][0][i] if results.get("distances") else None
            out.append({
                "source": meta.get("source", "unknown"),
                "text": doc,
                "distance": round(dist, 4) if dist is not None else None,
                "rank": i + 1,
            })
        return out
    except Exception as exc:
        print(f"[RAG] query error: {exc}")
        return []


if __name__ == "__main__":
    stats = reindex_all()
    print(f"[RAG] Total documents : {stats['doc_count']}")
    print(f"[RAG] Total chunks    : {stats['chunk_count']}")
