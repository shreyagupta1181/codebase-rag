from app.services.hybrid_retrieval import hybrid_search
from app.services.symbol_retrieval import (
    find_symbol_in_query,
    search_symbol,
)


def should_use_symbol_lookup(
    query: str,
    symbol: str | None,
) -> bool:

    if symbol is None:
        return False

    query_clean = query.strip().rstrip("?.!").lower()
    symbol_clean = symbol.lower()

    # -----------------------------------------
    # CASE 1: User typed the symbol itself
    #
    # APIRouter
    # HTTPException
    # -----------------------------------------

    if query_clean == symbol_clean:
        return True

    # -----------------------------------------
    # CASE 2: Qualified symbol
    #
    # APIRouter.include_router
    # FastAPI.openapi
    #
    # These are strong structural references.
    # -----------------------------------------

    if "." in symbol:
        return True

    # -----------------------------------------
    # Otherwise use normal hybrid retrieval.
    #
    # Example:
    # "How does FastAPI generate OpenAPI?"
    #
    # FastAPI occurs in the question, but that
    # doesn't mean the user wants the FastAPI
    # class definition.
    # -----------------------------------------

    return False


def retrieve(query: str, k: int = 5) -> list[dict]:

    symbol = find_symbol_in_query(query)

    if not should_use_symbol_lookup(query, symbol):

        return hybrid_search(
            query,
            k=k,
        )

    symbol_results = search_symbol(
        symbol,
        k=k,
    )

    hybrid_results = hybrid_search(
        query,
        k=k,
    )

    return merge_results(
        symbol_results,
        hybrid_results,
        k=k,
    )


def merge_results(
    symbol_results: list[dict],
    hybrid_results: list[dict],
    k: int,
) -> list[dict]:

    merged = []
    seen = set()

    for result in symbol_results:

        chunk = result["chunk"]
        metadata = chunk["metadata"]

        key = (
            metadata["file"],
            metadata["name"],
            metadata["start_line"],
        )

        if key in seen:
            continue

        seen.add(key)
        merged.append(result)

    for result in hybrid_results:

        chunk = result["chunk"]
        metadata = chunk["metadata"]

        key = (
            metadata["file"],
            metadata["name"],
            metadata["start_line"],
        )

        if key in seen:
            continue

        seen.add(key)
        merged.append(result)

        if len(merged) >= k:
            break

    return merged[:k]