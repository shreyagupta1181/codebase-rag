from pathlib import Path
from git import Repo

from app.config import REPOSITORIES_DIR


def clone_repository(repo_url: str) -> Path:
    repo_name = repo_url.rstrip("/").split("/")[-1]
    destination = REPOSITORIES_DIR / repo_name

    if destination.exists():
        return destination

    Repo.clone_from(repo_url, destination)

    return destination