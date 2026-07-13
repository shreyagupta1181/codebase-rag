from fastapi import FastAPI

from app.api.ingest import router as ingest_router

app = FastAPI(title="Codebase RAG API")

app.include_router(ingest_router)


@app.get("/")
def root():
    return {"message": "Codebase RAG API"}