import math
from pathlib import Path


def chunk_id(chunk: dict) -> tuple:
    """
    Convert a retrieved chunk into a stable identity.
    """
    metadata = chunk["metadata"]

    return (
        Path(metadata["file"]).name,
        metadata["name"],
        metadata["start_line"],
    )


def relevant_id(relevant_chunk: dict) -> tuple:
    """
    Convert a ground-truth chunk from queries.json
    into the same identity format.
    """
    return (
        relevant_chunk["file"],
        relevant_chunk["name"],
        relevant_chunk["start_line"],
    )


def recall_at_k(results: list, relevant_chunks: list, k: int) -> float:

    relevant = {
        relevant_id(chunk)
        for chunk in relevant_chunks
    }

    retrieved = {
        chunk_id(result["chunk"])
        for result in results[:k]
    }

    if not relevant:
        return 0.0

    return len(relevant & retrieved) / len(relevant)


def reciprocal_rank(results: list, relevant_chunks: list) -> float:

    relevant = {
        relevant_id(chunk)
        for chunk in relevant_chunks
    }

    for rank, result in enumerate(results, start=1):

        if chunk_id(result["chunk"]) in relevant:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(results: list, relevant_chunks: list, k: int) -> float:

    relevant = {
        relevant_id(chunk)
        for chunk in relevant_chunks
    }

    # Actual DCG
    dcg = 0.0

    for rank, result in enumerate(results[:k], start=1):

        if chunk_id(result["chunk"]) in relevant:
            dcg += 1.0 / math.log2(rank + 1)

    # Ideal DCG
    ideal_hits = min(len(relevant), k)

    idcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, ideal_hits + 1)
    )

    if idcg == 0:
        return 0.0

    return dcg / idcg