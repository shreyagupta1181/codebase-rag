import re
from pathlib import Path

from app.services.vector_store import VectorStore


vector_store = VectorStore()


def ensure_vector_store_loaded() -> bool:
    """
    Load the vector store lazily.

    Returns False if no repository has been indexed yet.
    """

    if vector_store.index is not None:
        return True

    index_path = Path("vector_store") / "index.faiss"
    metadata_path = Path("vector_store") / "metadata.json"

    if not index_path.exists() or not metadata_path.exists():
        return False

    vector_store.load("vector_store")

    return True


def normalize_symbol(value: str) -> str:
    return value.strip().lower()


def symbol_pattern(name: str) -> re.Pattern:
    """
    Match a symbol as a complete identifier rather than
    as an arbitrary substring.

    Examples:
        APIRouter
        APIRouter.include_router
        include_router
    """

    return re.compile(
        rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])",
        re.IGNORECASE,
    )


def is_candidate_symbol(name: str) -> bool:
    """
    Ignore extremely short/generic names that would cause
    noisy matches such as functions called `a`, `x`, etc.
    """

    if len(name) < 3:
        return False

    return True


def find_symbols_in_query(query: str) -> list[str]:

    if not ensure_vector_store_loaded():
        return []

    matches = []

    for chunk in vector_store.metadata:

        metadata = chunk["metadata"]
        name = metadata.get("name")

        if not name:
            continue

        if not is_candidate_symbol(name):
            continue

        if symbol_pattern(name).search(query):
            matches.append(name)

    # Remove duplicates
    matches = list(set(matches))

    # Most specific symbol first
    matches.sort(key=len, reverse=True)

    return matches


def find_symbol_in_query(query: str) -> str | None:

    matches = find_symbols_in_query(query)

    if not matches:
        return None

    return matches[0]


def search_symbol(
    symbol: str,
    k: int = 5,
) -> list[dict]:

    if not ensure_vector_store_loaded():
        return []

    target = normalize_symbol(symbol)

    results = []

    for chunk in vector_store.metadata:

        metadata = chunk["metadata"]
        name = metadata.get("name")

        if not name:
            continue

        if normalize_symbol(name) == target:

            results.append({
                "score": 1.0,
                "chunk": chunk,
            })

    return results[:k]