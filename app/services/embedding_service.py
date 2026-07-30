import os
import re
import time
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

MAX_RETRIES = 5
DEFAULT_RETRY_DELAY = 60


def _get_retry_delay(error: Exception) -> float:
    """
    Extract Gemini's suggested retry delay from a 429 error.

    Example:
        "Please retry in 28.922738098s."
    """

    match = re.search(
        r"retry in ([0-9.]+)s",
        str(error),
        re.IGNORECASE,
    )

    if match:
        # Add a small buffer so we don't retry exactly
        # at the quota boundary.
        return float(match.group(1)) + 2

    return DEFAULT_RETRY_DELAY


def _embed_with_retry(contents):
    """
    Call Gemini embeddings and automatically retry
    temporary 429 RESOURCE_EXHAUSTED errors.
    """

    for attempt in range(MAX_RETRIES + 1):

        try:
            return client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=contents,
            )

        except Exception as error:

            error_text = str(error)

            is_rate_limit = (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            )

            if not is_rate_limit:
                raise

            if attempt >= MAX_RETRIES:
                raise

            delay = _get_retry_delay(error)

            print(
                f"\nGemini embedding rate limit reached. "
                f"Retrying in {delay:.1f}s..."
            )

            time.sleep(delay)


def embed_text(text: str) -> list[float]:
    """
    Generate an embedding for a single query.
    """

    response = _embed_with_retry(text)

    return response.embeddings[0].values


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a batch of repository chunks.
    Automatically retries temporary Gemini rate limits.
    """

    if not texts:
        return []

    response = _embed_with_retry(texts)

    return [
        embedding.values
        for embedding in response.embeddings
    ]