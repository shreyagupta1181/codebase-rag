from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.generation_service import GenerationService
from app.services.repository_state import get_active_repository


router = APIRouter()


class AskRequest(BaseModel):
    question: str


class Source(BaseModel):
    id: int
    file: str
    type: str
    name: str
    start_line: int
    end_line: int


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


@router.post(
    "/ask",
    response_model=AskResponse,
)
def ask_question(request: AskRequest):

    # Make sure something has been ingested
    repository = get_active_repository()

    if repository is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "No repository has been indexed yet. "
                "Ingest a repository before asking questions."
            ),
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        generation_service = GenerationService()

        result = generation_service.generate(
            question
        )

        return result

    except Exception as error:

        print("\n===== ASK ERROR =====")
        print(error)
        print("=====================\n")

        raise HTTPException(
            status_code=500,
            detail="Failed to generate answer.",
        )