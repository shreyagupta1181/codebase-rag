from fastapi import APIRouter, HTTPException
from git import GitCommandError

from app.schemas.ingest import IngestRequest, IngestResponse
from app.services.git_service import clone_repository

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest_repository(request: IngestRequest):
    try:
        path = clone_repository(str(request.repo_url))

    except GitCommandError:
        raise HTTPException(
            status_code=400,
            detail="Failed to clone repository. Please check the repository URL."
        )

    return IngestResponse(
        status="success",
        repository=path.name,
        message="Repository cloned successfully."
    )