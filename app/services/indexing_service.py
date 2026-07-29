from pathlib import Path

from app.services.chunking_service import chunk_repository
from app.services.embedding_service import embed_texts
from app.services.vector_store import VectorStore
from app.services.bm25_store import BM25Store


BATCH_SIZE = 50


def build_indexes(repo_path: str):

    chunks = chunk_repository(
        Path(repo_path)
    )

    if not chunks:
        raise ValueError(
            "No supported code chunks were found in the repository."
        )

    print(f"\nFound {len(chunks)} chunks.")
    print("Generating Gemini embeddings...\n")

    indexed_chunks = []

    # --------------------------------
    # Generate embeddings in batches
    # --------------------------------

    for start in range(0, len(chunks), BATCH_SIZE):

        batch = chunks[
            start:start + BATCH_SIZE
        ]

        texts = [
            chunk["content"]
            for chunk in batch
        ]

        embeddings = embed_texts(texts)

        if len(embeddings) != len(batch):
            raise ValueError(
                "Embedding count does not match chunk count."
            )

        for chunk, embedding in zip(
            batch,
            embeddings,
        ):
            indexed_chunks.append({
                "content": chunk["content"],
                "metadata": chunk["metadata"],
                "embedding": embedding,
            })

        completed = min(
            start + BATCH_SIZE,
            len(chunks),
        )

        print(
            f"\rEmbedded {completed}/{len(chunks)}",
            end="",
            flush=True,
        )

    print("\n")

    # --------------------------------
    # FAISS
    # --------------------------------

    vector_store = VectorStore()

    vector_store.build(
        indexed_chunks
    )

    vector_store.save(
        "vector_store"
    )

    print("FAISS index saved.")

    # --------------------------------
    # BM25
    # --------------------------------

    bm25_store = BM25Store()

    bm25_store.build(
        indexed_chunks
    )

    bm25_store.save(
        "bm25_store"
    )

    print("BM25 index saved.")

    # --------------------------------
    # Refresh retrieval state
    # --------------------------------

    # Import here to avoid circular imports
    from app.services.retrieval_service import (
        reload_vector_store,
    )
    from app.services.hybrid_retrieval import (
        reload_bm25_store,
    )

    reload_vector_store()
    reload_bm25_store()

    print("Retrieval stores refreshed.")

    print("\nRepository indexed successfully!")

    return {
        "chunks": len(indexed_chunks),
    }