import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from google import genai
from ollama import chat


load_dotenv()


class LLMService(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class OllamaLLM(LLMService):

    def __init__(self, model="qwen2.5-coder:3b"):
        self.model = model

    def generate(self, prompt: str) -> str:
        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.message.content


class GeminiLLM(LLMService):

    def __init__(self, model="gemini-3.6-flash"):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text


def get_llm() -> LLMService:

    provider = os.getenv(
        "LLM_PROVIDER",
        "ollama",
    ).lower()

    if provider == "gemini":
        return GeminiLLM()

    if provider == "ollama":
        return OllamaLLM()

    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )