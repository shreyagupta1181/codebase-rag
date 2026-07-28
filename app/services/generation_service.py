import json

from app.services.query_router import retrieve
from app.services.llm_service import get_llm

class GenerationService:

    def __init__(self):
        self.llm = get_llm()

    def build_prompt(
        self,
        question: str,
        chunks: list[dict],
    ) -> str:

        context_parts = []

        for i, result in enumerate(chunks, start=1):

            chunk = result["chunk"]
            metadata = chunk["metadata"]

            source = (
                f"[Source {i}]\n"
                f"File: {metadata['file']}\n"
                f"Symbol: {metadata['name']}\n"
                f"Type: {metadata['type']}\n"
                f"Lines: {metadata['start_line']}-{metadata['end_line']}\n"
                f"Code:\n{chunk['content']}"
            )

            context_parts.append(source)

        context = "\n\n".join(context_parts)

        return f"""
You are an expert software engineering assistant answering questions
about a specific code repository.

Answer using ONLY the repository context provided below.

GROUNDING RULES:

1. Do not use outside knowledge.
2. Do not invent functions, classes, files, behaviour, or implementation details.
3. Every factual claim must be supported by the provided repository context.
4. Determine whether the context contains enough information to answer the question.
5. If the context is insufficient, set "answerable" to false.
6. If the context is sufficient, set "answerable" to true.
7. "used_sources" must contain ONLY the source numbers that actually support the answer.
8. Do not include irrelevant sources.
9. If only part of the question can be answered, answer only the supported part.
10. Return ONLY valid JSON.
11. Do not include markdown.
12. Do not include ```json fences.
13. Do not include text before or after the JSON object.

Your response MUST have exactly this structure:

{{
    "answerable": true,
    "answer": "Your answer here.",
    "used_sources": [1, 2]
}}

If the repository context is insufficient, return:

{{
    "answerable": false,
    "answer": "I couldn't find enough information in the repository.",
    "used_sources": []
}}

Repository Context
==================

{context}

==================

Question:
{question}
"""

    def parse_llm_response(
        self,
        raw_response: str,
    ) -> dict | None:

        if not raw_response:
            return None

        text = raw_response.strip()

        # -----------------------------------------
        # Remove Markdown code fences
        #
        # ```json
        # {...}
        # ```
        # -----------------------------------------

        if text.startswith("```json"):
            text = text[7:]

        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # -----------------------------------------
        # Attempt 1:
        # Entire response is valid JSON
        # -----------------------------------------

        try:
            result = json.loads(text)

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            pass

        # -----------------------------------------
        # Attempt 2:
        # Model added text around the JSON
        #
        # Example:
        #
        # Here is the result:
        # {
        #     ...
        # }
        # -----------------------------------------

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            return None

        if end <= start:
            return None

        json_text = text[start:end + 1]

        try:
            result = json.loads(json_text)

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            return None

        return None

    def generate(self, question: str):

        # -----------------------------------------
        # 1. Retrieve repository context
        # -----------------------------------------

        retrieved_chunks = retrieve(
            question,
            k=5,
        )

        if not retrieved_chunks:

            return {
                "answer": (
                    "I couldn't find enough information "
                    "in the repository."
                ),
                "sources": [],
            }

        # -----------------------------------------
        # 2. Build grounded prompt
        # -----------------------------------------

        prompt = self.build_prompt(
            question,
            retrieved_chunks,
        )

        # -----------------------------------------
        # 3. Generate answer with Ollama
        # -----------------------------------------

        try:
            raw_response = self.llm.generate(prompt)

        except Exception as error:

            print("\n===== LLM ERROR =====")
            print(error)
            print("=====================\n")

            return {
                "answer": (
                    "I couldn't reliably generate "
                    "a grounded answer."
                ),
                "sources": [],
            }

        # Useful while we're debugging Qwen
        print("\n===== RAW LLM RESPONSE =====")
        print(raw_response)
        print("============================\n")

        # -----------------------------------------
        # 4. Parse LLM JSON
        # -----------------------------------------

        result = self.parse_llm_response(
            raw_response
        )

        if result is None:

            print("\n===== INVALID LLM RESPONSE =====")
            print(raw_response)
            print("================================\n")

            return {
                "answer": (
                    "I couldn't reliably generate "
                    "a grounded answer."
                ),
                "sources": [],
            }

        # -----------------------------------------
        # 5. Validate response fields
        # -----------------------------------------

        answerable = result.get(
            "answerable",
            False,
        )

        answer = result.get(
            "answer",
            "",
        )

        used_source_ids = result.get(
            "used_sources",
            [],
        )

        if not isinstance(answerable, bool):
            answerable = False

        if not isinstance(answer, str):
            answer = str(answer)

        if not isinstance(used_source_ids, list):
            used_source_ids = []

        # -----------------------------------------
        # 6. Model says context is insufficient
        # -----------------------------------------

        if not answerable:

            return {
                "answer": (
                    "I couldn't find enough information "
                    "in the repository."
                ),
                "sources": [],
            }

        # -----------------------------------------
        # 7. Validate and construct citations
        # -----------------------------------------

        sources = []
        seen_source_ids = set()

        for source_id in used_source_ids:

            # Ignore anything that isn't an integer
            if not isinstance(source_id, int):
                continue

            # Avoid duplicate citations
            if source_id in seen_source_ids:
                continue

            index = source_id - 1

            # Prevent invalid/hallucinated source IDs
            if index < 0 or index >= len(retrieved_chunks):
                continue

            seen_source_ids.add(source_id)

            metadata = (
                retrieved_chunks[index]
                ["chunk"]
                ["metadata"]
            )

            sources.append({
                "id": source_id,
                "file": metadata["file"],
                "type": metadata["type"],
                "name": metadata["name"],
                "start_line": metadata["start_line"],
                "end_line": metadata["end_line"],
            })

        # -----------------------------------------
        # 8. Extra grounding safeguard
        #
        # If model claims it answered but cites
        # absolutely nothing, don't trust it.
        # -----------------------------------------

        if not sources:

            return {
                "answer": (
                    "I couldn't reliably generate "
                    "a grounded answer."
                ),
                "sources": [],
            }

        # -----------------------------------------
        # 9. Final grounded response
        # -----------------------------------------

        return {
            "answer": answer,
            "sources": sources,
        }