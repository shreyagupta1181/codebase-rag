from app.services.generation_service import GenerationService


def main():

    service = GenerationService()

    question = "What is APIRouter?"

    response = service.generate(question)

    print("=" * 120)
    print(response["answer"])

    print("\nSources:\n")

    for source in response["sources"]:
        print(source)


if __name__ == "__main__":
    main()