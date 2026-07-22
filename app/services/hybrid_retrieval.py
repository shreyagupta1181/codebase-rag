from app.services.retrieval_service import search as dense_search
from app.services.bm25_store import BM25Store


bm25_store = BM25Store()
bm25_store.load("bm25_store")


def reciprocal_rank_fusion(result_lists, k=60):

    scores = {}

    chunks = {}

    for results in result_lists:

        for rank, result in enumerate(results, start=1):

            chunk = result["chunk"]

            key = (
                chunk["metadata"]["file"],
                chunk["metadata"]["start_line"],
                chunk["metadata"]["end_line"],
            )

            chunks[key] = chunk

            scores[key] = scores.get(key, 0) + 1 / (k + rank)

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    fused = []

    for key, score in ranked:

        fused.append(
            {
                "score": score,
                "chunk": chunks[key],
            }
        )

    return fused


def hybrid_search(query, k=5):

    dense_results = dense_search(query, k=10)

    sparse_results = bm25_store.search(query, k=10)

    fused = reciprocal_rank_fusion(
        [dense_results, sparse_results]
    )

    return fused[:k]