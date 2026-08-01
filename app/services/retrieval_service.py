import faiss
import numpy as np

from app.services.embedding_service import embed_text
from app.services.vector_store import VectorStore

vector_store = VectorStore()


def reload_vector_store():
    vector_store.load("vector_store")


def search(query: str, k: int = 5):

    if vector_store.index is None:
        vector_store.load("vector_store")

    query_embedding = np.array(
        embed_text(query),
        dtype=np.float32,
    ).reshape(1, -1)

    faiss.normalize_L2(query_embedding)

    distances, indices = vector_store.index.search(
        query_embedding,
        k,
    )

    results = []

    for score, idx in zip(distances[0], indices[0]):

        if idx == -1:
            continue

        results.append(
            {
                "score": float(score),
                "chunk": vector_store.metadata[idx],
            }
        )

    return results