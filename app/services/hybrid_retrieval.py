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
            metadata = chunk["metadata"]

            key = (
                metadata["file"],
                metadata["name"],
                metadata["start_line"],
            )

            score = 1 / (k + rank)

            file_path = metadata["file"].replace("\\", "/").lower()

            # Slightly penalise test chunks so implementation
            # code wins when relevance is otherwise similar.
            if "/tests/" in file_path or file_path.startswith("tests/"):
                score *= 0.75

            scores[key] = scores.get(key, 0) + score
            chunks[key] = chunk

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    return [
        {
            "score": score,
            "chunk": chunks[key],
        }
        for key, score in ranked
    ]


def hybrid_search(query, k=5):

    candidate_k = max(k * 4, 20)

    dense_results = dense_search(
        query,
        k=candidate_k,
    )

    sparse_results = bm25_store.search(
        query,
        k=candidate_k,
    )

    fused = reciprocal_rank_fusion(
        [dense_results, sparse_results]
    )

    return fused[:k]