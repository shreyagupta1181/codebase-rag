from app.services.query_router import retrieve


queries = [
    "APIRouter",
    "What does APIRouter.include_router do?",
    "How does FastAPI include routers?",
    "How does FastAPI generate the OpenAPI schema?",
    "How does FastAPI prevent circular router inclusion?",
]


for query in queries:

    print("\n")
    print("=" * 100)
    print(f"QUERY: {query}")
    print("=" * 100)

    results = retrieve(
        query,
        k=5,
    )

    for rank, result in enumerate(results, start=1):

        metadata = result["chunk"]["metadata"]

        print(f"\nRank {rank}")
        print(f"Type : {metadata['type']}")
        print(f"Name : {metadata['name']}")
        print(f"File : {metadata['file']}")
        print(
            f"Lines: "
            f"{metadata['start_line']}-"
            f"{metadata['end_line']}"
        )