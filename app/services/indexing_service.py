from pathlib import Path

from app.services.chunking_service import chunk_repository
from app.services.embedding_service import embed_text


def build_embedding_index(repo_path: str):

    chunks = chunk_repository(Path(repo_path))

    indexed_chunks = []

    print(f"Found {len(chunks)} chunks.")
    print("Generating embeddings...\n")

    for i, chunk in enumerate(chunks, start=1):

        embedding = embed_text(chunk["content"])

        indexed_chunks.append({
            "content": chunk["content"],
            "metadata": chunk["metadata"],
            "embedding": embedding,
        })

        print(f"{i}/{len(chunks)}")

    print("\nRepository indexed successfully!")

    return indexed_chunks