from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ask import router as ask_router
from app.api.ingest import router as ingest_router
import os



app = FastAPI(
    title="Codebase RAG API",
    description=(
        "Chat with a GitHub codebase using "
        "hybrid retrieval and local LLM generation."
    ),
    version="1.0.0",
)


# -------------------------
# CORS
# -------------------------

frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Routers
# -------------------------

app.include_router(
    ingest_router,
    tags=["Ingestion"],
)

app.include_router(
    ask_router,
    tags=["Questions"],
)


# -------------------------
# Root
# -------------------------

@app.get("/")
def root():
    return {
        "message": "Codebase RAG API is running."
    }