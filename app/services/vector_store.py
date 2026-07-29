import json
from pathlib import Path

import faiss
import numpy as np


class VectorStore:

    def __init__(self):
        self.index = None
        self.metadata = []

    def build(self, indexed_chunks: list[dict]):

        embeddings = np.array(
            [chunk["embedding"] for chunk in indexed_chunks],
            dtype=np.float32,
        )

        # Normalize stored embeddings.
        # Inner product on normalized vectors = cosine similarity.
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        self.metadata = [
            {
                "content": chunk["content"],
                "metadata": chunk["metadata"],
            }
            for chunk in indexed_chunks
        ]

    def save(self, directory: str):

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        faiss.write_index(
            self.index,
            str(directory / "index.faiss"),
        )

        with open(
            directory / "metadata.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.metadata,
                f,
                indent=4,
                ensure_ascii=False,
            )

    def load(self, directory: str):

        directory = Path(directory)

        self.index = faiss.read_index(
            str(directory / "index.faiss")
        )

        with open(
            directory / "metadata.json",
            encoding="utf-8",
        ) as f:
            self.metadata = json.load(f)