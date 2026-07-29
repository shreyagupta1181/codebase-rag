import os
from abc import ABC, abstractmethod
from pathlib import Path

from dotenv import load_dotenv
from google import genai


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class LLMService(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


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
    return GeminiLLM()