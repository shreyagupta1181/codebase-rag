from app.services.indexing_service import build_embedding_index
from app.services.vector_store import VectorStore

repo = r"C:\codebase-rag\repositories\fastapi"

indexed_chunks = build_embedding_index(repo)

store = VectorStore()

store.build(indexed_chunks)

store.save("vector_store")

print()

print("FAISS vectors:", store.index.ntotal)

print("Metadata:", len(store.metadata))

print()

print("Saved successfully!")