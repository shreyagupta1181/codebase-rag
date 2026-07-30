import os
import time
from pathlib import Path

from dotenv import load_dotenv
import voyageai


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("VOYAGE_API_KEY")

if not API_KEY:
    raise ValueError(
        "VOYAGE_API_KEY environment variable is not set."
    )

client = voyageai.Client(
    api_key=API_KEY,
    max_retries=2,
    timeout=60,
)

EMBEDDING_MODEL = "voyage-code-3"
EMBEDDING_DIMENSION = 1024


def embed_text(text: str) -> list[float]:
    """
    Generate an embedding for a user query.
    """

    response = client.embed(
        [text],
        model=EMBEDDING_MODEL,
        input_type="query",
        output_dimension=EMBEDDING_DIMENSION,
    )

    return response.embeddings[0]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate document embeddings for repository chunks.
    """

    if not texts:
        return []

    response = client.embed(
        texts,
        model=EMBEDDING_MODEL,
        input_type="document",
        output_dimension=EMBEDDING_DIMENSION,
    )

    return response.embeddings