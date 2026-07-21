from pathlib import Path

SUPPORTED_EXTENSIONS = {".py", ".md"}


def get_repository_files(repo_path: Path) -> list[Path]:
    """
    Recursively find all supported files inside a repository.

    Args:
        repo_path: Path to the cloned repository.

    Returns:
        List of file paths.
    """

    files = []

    for file in repo_path.rglob("*"):
        if file.is_file() and file.suffix in SUPPORTED_EXTENSIONS:
            files.append(file)

    return sorted(files)