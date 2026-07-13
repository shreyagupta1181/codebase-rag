from app.services.git_service import clone_repository

path = clone_repository("https://github.com/fastapi/fastapi")

print(path)