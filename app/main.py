from fastapi import FastAPI

from app.api.ingest import router as ingest_router

from app.api.ask import router as ask_router

app = FastAPI(title="Codebase RAG API")



app.include_router(ask_router)

app.include_router(ingest_router)


@app.get("/")
def root():
    return {"message": "Codebase RAG API"}