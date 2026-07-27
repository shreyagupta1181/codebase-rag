from pathlib import Path

from app.services.chunking_service import chunk_repository
from app.services.embedding_service import embed_text
from app.services.vector_store import VectorStore
from app.services.bm25_store import BM25Store


def build_indexes(repo_path: str):

    chunks = chunk_repository(
        Path(repo_path)
    )

    if not chunks:
        raise ValueError(
            "No supported code chunks were found in the repository."
        )

    indexed_chunks = []

    print(f"\nFound {len(chunks)} chunks.")
    print("Generating embeddings...\n")

    for i, chunk in enumerate(chunks, start=1):

        embedding = embed_text(
            chunk["content"]
        )

        indexed_chunks.append({
            "content": chunk["content"],
            "metadata": chunk["metadata"],
            "embedding": embedding,
        })

        print(
            f"\rEmbedding {i}/{len(chunks)}",
            end="",
            flush=True,
        )

    print("\n")

    # ------------------------------
    # FAISS
    # ------------------------------

    vector_store = VectorStore()

    vector_store.build(
        indexed_chunks
    )

    vector_store.save(
        "vector_store"
    )

    print("FAISS index saved.")

    # ------------------------------
    # BM25
    # ------------------------------

    bm25_store = BM25Store()

    bm25_store.build(
        indexed_chunks
    )

    bm25_store.save(
        "bm25_store"
    )

    print("BM25 index saved.")

    print("\nRepository indexed successfully!")

    return {
        "chunks": len(indexed_chunks),
    }