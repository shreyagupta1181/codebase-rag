from app.services.retrieval_service import search as dense_search
from app.services.bm25_store import BM25Store


bm25_store = BM25Store()


def reload_bm25_store():
    bm25_store.load("bm25_store")


def reciprocal_rank_fusion(
    dense_results,
    sparse_results,
    dense_weight=2.0,
    sparse_weight=1.0,
    k=60,
):
    scores = {}
    chunks = {}

    # Dense retrieval (higher weight)
    for rank, result in enumerate(dense_results, start=1):

        metadata = result["chunk"]["metadata"]

        file_path = metadata["file"].replace("\\", "/").lower()

        if (
            "/tests/" in file_path
            or file_path.startswith("tests/")
            or "/test/" in file_path
            or "/docs/" in file_path
            or "/examples/" in file_path
        ):
            continue

        key = (
            metadata["file"],
            metadata["name"],
            metadata["start_line"],
        )

        scores[key] = (
            scores.get(key, 0)
            + dense_weight / (k + rank)
        )

        chunks[key] = result["chunk"]

    # BM25 retrieval
    for rank, result in enumerate(sparse_results, start=1):

        metadata = result["chunk"]["metadata"]

        file_path = metadata["file"].replace("\\", "/").lower()

        if (
            "/tests/" in file_path
            or file_path.startswith("tests/")
            or "/test/" in file_path
            or "/docs/" in file_path
            or "/examples/" in file_path
        ):
            continue

        key = (
            metadata["file"],
            metadata["name"],
            metadata["start_line"],
        )

        scores[key] = (
            scores.get(key, 0)
            + sparse_weight / (k + rank)
        )

        chunks[key] = result["chunk"]

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


def hybrid_search(query: str, k: int = 5):

    # Retrieve many candidates
    candidate_k = 50

    dense_results = dense_search(
        query=query,
        k=candidate_k,
    )

    sparse_results = bm25_store.search(
        query=query,
        k=candidate_k,
    )

    fused = reciprocal_rank_fusion(
        dense_results,
        sparse_results,
        dense_weight=2.0,
        sparse_weight=1.0,
    )

    return fused[:k]