from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

print(f"Loading reranker: {MODEL_NAME}")

reranker = CrossEncoder(MODEL_NAME)


def rerank(query: str, results: list, top_k: int = 5):

    if not results:
        return []

    pairs = [
        (query, result["chunk"]["content"])
        for result in results
    ]

    scores = reranker.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):
        reranked.append(
            {
                "score": float(score),
                "chunk": result["chunk"],
            }
        )

    reranked.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return reranked[:top_k]