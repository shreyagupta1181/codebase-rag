from fastembed import TextEmbedding


EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

model = TextEmbedding(
    model_name=EMBEDDING_MODEL,
)


def embed_text(text: str) -> list[float]:
    """
    Generate an embedding for a single query.
    """

    embeddings = list(
        model.embed([text])
    )

    return embeddings[0].tolist()


def embed_texts(
    texts: list[str],
) -> list[list[float]]:
    """
    Generate embeddings for repository chunks
    locally using FastEmbed.
    """

    if not texts:
        return []

    embeddings = model.embed(texts)

    return [
        embedding.tolist()
        for embedding in embeddings
    ]