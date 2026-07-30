import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set."
    )

client = genai.Client(api_key=API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"


def embed_text(text: str) -> list[float]:
    """
    Generate an embedding for a single query.
    Used primarily for query embeddings.
    """

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )

    return response.embeddings[0].values


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple repository chunks.
    Used when building the FAISS vector index.
    """

    if not texts:
        return []

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
    )

    return [
        embedding.values
        for embedding in response.embeddings
    ]