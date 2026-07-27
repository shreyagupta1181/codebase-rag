from fastapi import APIRouter
from pydantic import BaseModel

from app.services.generation_service import GenerationService


router = APIRouter()

generation_service = GenerationService()


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):

    result = generation_service.generate(request.question)

    return result