from app.services.hybrid_retrieval import hybrid_search
from app.services.llm_service import OllamaLLM


class GenerationService:

    def __init__(self):

        self.llm = OllamaLLM()
    def build_prompt(self, question: str, chunks: list[dict]) -> str:

        context = ""

        for i, chunk in enumerate(chunks, start=1):

            metadata = chunk["chunk"]["metadata"]

            context += (
                f"### Chunk {i}\n"
                f"File: {metadata['file']}\n"
                f"Type: {metadata['type']}\n"
                f"Name: {metadata['name']}\n\n"
                f"{chunk['chunk']['content']}\n\n"
            )

        prompt = f"""
You are an expert software engineering assistant.

Answer the user's question ONLY using the repository context below.

If the answer cannot be found in the provided context, say:
"I couldn't find enough information in the repository."

Repository Context
==================

{context}

==================

Question:
{question}

Answer:
"""

        return prompt

    def generate(self, question: str):

        retrieved_chunks = hybrid_search(question)

        prompt = self.build_prompt(
            question,
            retrieved_chunks,
        )

        answer = self.llm.generate(prompt)

        return {
            "answer": answer,
            "sources": [
                chunk["chunk"]["metadata"]
                for chunk in retrieved_chunks
            ],
        }