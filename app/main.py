from fastapi import FastAPI

from app.api.ask import router as ask_router
from app.api.ingest import router as ingest_router


app = FastAPI(
    title="Codebase RAG API",
    description=(
        "Chat with a GitHub codebase using "
        "hybrid retrieval and local LLM generation."
    ),
    version="1.0.0",
)


app.include_router(
    ingest_router,
    tags=["Ingestion"],
)

app.include_router(
    ask_router,
    tags=["Questions"],
)


@app.get("/")
def root():
    return {
        "message": "Codebase RAG API is running."
    }