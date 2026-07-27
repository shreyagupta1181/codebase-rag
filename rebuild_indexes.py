from app.services.indexing_service import build_embedding_index


REPO_PATH = "repositories/fastapi"


if __name__ == "__main__":
    print("Rebuilding indexes...\n")

    build_embedding_index(REPO_PATH)

    print("\nFAISS and BM25 indexes rebuilt successfully.")