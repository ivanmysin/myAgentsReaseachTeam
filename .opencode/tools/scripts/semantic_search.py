#!/usr/bin/env python3
"""
Семантический поиск по статьям через ChromaDB.
Поддерживает две коллекции:
- abstracts: поиск по абстрактам статей (коллекция LITBASE_CHROMA_COLLECTION)
- chunks: поиск по чанкам полных текстов (~500 токенов) (коллекция CHUNK_CHROMA_COLLECTION)
"""

import argparse
import csv
import os
import sqlite3
import sys
from pathlib import Path


def load_env():
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def get_embedding_function():
    """Get embedding function using sentence-transformers with SPECTER2."""
    try:
        from sentence_transformers import SentenceTransformer
        # Use SPECTER2 - specialized for scientific papers
        # Model: allenai/specter2_base produces 768-dim embeddings
        model = SentenceTransformer('allenai/specter2_base')
        print("Using model: allenai/specter2_base (768-dim, SPECTER2)")
        return model, 768
    except ImportError:
        print(
            "WARNING: sentence-transformers not installed. Using ChromaDB default.",
            file=sys.stderr
        )
        return None, None


def main():
    parser = argparse.ArgumentParser(
        description="Semantic search via ChromaDB"
    )
    parser.add_argument("query", help="Search query in natural language")
    parser.add_argument("--top", type=int, default=20, help="Number of results")
    parser.add_argument(
        "--threshold", type=float, default=-1.0,
        help="Minimum similarity threshold (default: -1.0, no filter)"
    )
    parser.add_argument(
        "--cluster", type=int, default=None,
        help="Restrict to cluster N"
    )
    parser.add_argument(
        "--collection", "-c",
        choices=["abstracts", "chunks", "all"],
        default="abstracts",
        help="Which collection to search: 'abstracts' (default), 'chunks' (full-text chunks), or 'all' (both)"
    )
    args = parser.parse_args()

    load_env()

    chroma_path = os.environ.get("LITBASE_CHROMA_PATH")
    abstract_collection_name = os.environ.get(
        "LITBASE_CHROMA_COLLECTION", "research_papers"
    )
    chunk_collection_name = os.environ.get(
        "CHUNK_CHROMA_COLLECTION", "fulltext_chunks"
    )
    db_path = os.environ.get("LITBASE_SQLITE_PATH")
    clusters_csv = os.environ.get("LITBASE_CLUSTERS_CSV")

    if not chroma_path:
        print("ERROR: LITBASE_CHROMA_PATH not set", file=sys.stderr)
        sys.exit(1)

    try:
        import chromadb
    except ImportError:
        print(
            "ERROR: chromadb not installed. Run: pip install chromadb",
            file=sys.stderr,
        )
        sys.exit(1)

    # Get embedding model
    embed_model, embed_dim = get_embedding_function()

    # Generate query embedding
    if embed_model:
        query_embedding = embed_model.encode(args.query).tolist()
    else:
        query_embedding = None

    client = chromadb.PersistentClient(path=chroma_path)

    # Determine which collections to search
    collections_to_search = []
    if args.collection in ("abstracts", "all"):
        collections_to_search.append(("abstracts", abstract_collection_name))
    if args.collection in ("chunks", "all"):
        collections_to_search.append(("chunks", chunk_collection_name))

    where_filter = None
    if args.cluster is not None and clusters_csv:
        cluster_ids = []
        with open(clusters_csv, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row["cluster"]) == args.cluster:
                    cluster_ids.append(str(row["id"]))
        if cluster_ids:
            where_filter = {"id": {"$in": cluster_ids}}
        else:
            print(f"No articles found in cluster {args.cluster}")
            return

    conn = None
    if db_path and Path(db_path).exists():
        conn = sqlite3.connect(db_path)

    print(f"Semantic search for: \"{args.query}\"")
    print(f"Collection(s): {', '.join(c[0] for c in collections_to_search)}\n")

    all_results = []

    for coll_type, coll_name in collections_to_search:
        try:
            collection = client.get_collection(name=coll_name)
        except Exception as e:
            print(f"Warning: Could not access collection '{coll_name}': {e}")
            continue

        # Use pre-computed embedding if available, otherwise fallback to text
        if query_embedding:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=args.top,
                where=where_filter,
                include=["documents", "distances", "metadatas"],
            )
        else:
            results = collection.query(
                query_texts=[args.query],
                n_results=args.top,
                where=where_filter,
                include=["documents", "distances", "metadatas"],
            )

        if not results["ids"][0]:
            continue

        for i, (doc_id, distance) in enumerate(
            zip(results["ids"][0], results["distances"][0])
        ):
            # ChromaDB uses L2 distance - convert to similarity
            # Lower distance = more similar
            # For better readability, use negative distance as "raw similarity"
            similarity = -distance  # This is not normalized, but preserves ordering

            if args.threshold > 0 and similarity < args.threshold:
                continue

            metadata = {}
            if results["metadatas"] and results["metadatas"][0]:
                metadata = results["metadatas"][0][i]

            # Extract article_id from chunk metadata (chunks store article_id separately)
            article_id = doc_id
            if coll_type == "chunks":
                article_id = metadata.get("article_id", doc_id)

            all_results.append({
                "doc_id": doc_id,
                "article_id": article_id,
                "similarity": similarity,
                "collection": coll_type,
                "document": results["documents"][0][i] if results["documents"] and results["documents"][0] else "",
                "metadata": metadata,
            })

    if not all_results:
        print("No results found.")
        if conn:
            conn.close()
        return

    # Sort by similarity and display
    all_results.sort(key=lambda x: x["similarity"], reverse=True)
    print(f"Found {len(all_results)} results:\n")

    result_num = 0
    for res in all_results:
        result_num += 1
        # Show raw similarity score (negative distance - higher is better)
        print(f"--- Result {result_num} (score: {res['similarity']:.2f}, source: {res['collection']}) ---")

        # Get article info from SQLite
        if conn:
            try:
                cursor = conn.execute(
                    "SELECT title, authors, date, journal, doi "
                    "FROM Articles WHERE id = ?",
                    [res["article_id"]],
                )
                row = cursor.fetchone()
                if row:
                    print(f"  Article ID: {res['article_id']}")
                    print(f"  Title: {row[0]}")
                    print(f"  Authors: {row[1]}")
                    print(f"  Date: {row[2]}")
                    print(f"  Journal: {row[3]}")
                    print(f"  DOI: {row[4]}")
            except Exception:
                pass

        # Show document snippet
        doc_text = res["document"]
        if doc_text and len(doc_text) > 500:
            doc_text = doc_text[:500] + "..."
        if doc_text:
            if res["collection"] == "chunks":
                chunk_idx = res["metadata"].get("chunk_index", "?")
                print(f"  Chunk #{chunk_idx}: {doc_text}")
            else:
                print(f"  Abstract: {doc_text}")

        print()

    if conn:
        conn.close()


if __name__ == "__main__":
    main()
