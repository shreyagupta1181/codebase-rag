from app.services.hybrid_retrieval import hybrid_search
from app.services.reranker import rerank


def hybrid_rerank_search(query: str, k: int = 5):
    """
    Hybrid Retrieval (Dense + BM25 via RRF)
    followed by CrossEncoder reranking.
    """

    # Retrieve more candidates for reranking
    candidates = hybrid_search(
        query=query,
        k=50,
    )

    # CrossEncoder reranks the candidates
    reranked = rerank(
        query=query,
        results=candidates,
        top_k=k,
    )

    return reranked