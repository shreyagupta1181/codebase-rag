import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    text = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', text)   # camelCase -> camel Case
    text = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', ' ', text) # ABCDef -> ABC Def (acronym boundary)
    text = text.lower()
    text = text.replace("_", " ")
    return re.findall(r"\b[a-zA-Z0-9]+\b", text)

class BM25Store:

    def __init__(self):
        self.bm25 = None
        self.corpus = []
        self.metadata = []

    def build(self, indexed_chunks: list[dict]):

        self.corpus = []

        self.metadata = []

        for chunk in indexed_chunks:

            document = (
                f"{chunk['metadata']['name']} "
                f"{chunk['metadata']['type']} "
                f"{Path(chunk['metadata']['file']).name} "
                f"{chunk['content']}"
            )

            self.corpus.append(tokenize(document))

            self.metadata.append(
                {
                    "content": chunk["content"],
                    "metadata": chunk["metadata"],
                }
            )

        self.bm25 = BM25Okapi(self.corpus)

    def save(self, directory: str):

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            directory / "corpus.json",
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                {
                    "corpus": self.corpus,
                    "metadata": self.metadata,
                },
                f,
                indent=4,
                ensure_ascii=False,
            )

    def load(self, directory: str):

        directory = Path(directory)

        with open(
            directory / "corpus.json",
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        self.corpus = data["corpus"]
        self.metadata = data["metadata"]

        self.bm25 = BM25Okapi(self.corpus)

    def search(self, query: str, k: int = 5):

        query_tokens = tokenize(query)

        scores = self.bm25.get_scores(query_tokens)

        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True,
        )[:k]

        results = []

        for idx, score in ranked:

            if score <= 0:
                continue

            results.append(
                {
                    "score": float(score),
                    "chunk": self.metadata[idx],
                }
            )

        return results