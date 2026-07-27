from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from app.services.git_service import clone_repository
from app.services.indexing_service import build_indexes
from app.services.repository_state import (
    set_active_repository,
    get_active_repository,
)


router = APIRouter()


class IngestRequest(BaseModel):
    repo_url: HttpUrl


class IngestResponse(BaseModel):
    message: str
    repository: str
    chunks_indexed: int
    status: str


class RepositoryResponse(BaseModel):
    repository: str
    url: str
    chunks_indexed: int
    status: str


@router.post(
    "/ingest",
    response_model=IngestResponse,
)
def ingest_repository(request: IngestRequest):

    try:
        repo_url = str(request.repo_url)

        # 1. Clone repository
        repo_path = clone_repository(
            repo_url
        )

        # 2. Build FAISS + BM25
        result = build_indexes(
            str(repo_path)
        )

        chunks_indexed = result["chunks"]

        # 3. Only change active repository AFTER
        # indexing succeeds.
        set_active_repository(
            name=repo_path.name,
            path=str(repo_path),
            url=repo_url,
            chunks_indexed=chunks_indexed,
        )

        return {
            "message": "Repository indexed successfully.",
            "repository": repo_path.name,
            "chunks_indexed": chunks_indexed,
            "status": "ready",
        }

    except Exception as error:

        print("\n===== INGEST ERROR =====")
        print(error)
        print("========================\n")

        raise HTTPException(
            status_code=500,
            detail="Failed to ingest repository.",
        )


@router.get(
    "/repository",
    response_model=RepositoryResponse,
)
def get_repository():

    repository = get_active_repository()

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="No repository has been indexed yet.",
        )

    return {
        "repository": repository["repository"],
        "url": repository["url"],
        "chunks_indexed": repository["chunks_indexed"],
        "status": repository["status"],
    }