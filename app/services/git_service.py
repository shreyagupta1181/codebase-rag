from pathlib import Path

from git import Repo, GitCommandError


REPOSITORIES_DIR = Path("repositories")


def get_repo_name(repo_url: str) -> str:
    name = repo_url.rstrip("/").split("/")[-1]

    if name.endswith(".git"):
        name = name[:-4]

    return name


def clone_repository(repo_url: str) -> Path:

    REPOSITORIES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    repo_name = get_repo_name(repo_url)
    destination = REPOSITORIES_DIR / repo_name

    # -----------------------------------------
    # Repository already exists
    # -----------------------------------------

    if destination.exists():

        git_directory = destination / ".git"

        # Make sure it is actually a Git repo
        if not git_directory.exists():
            raise ValueError(
                f"{destination} already exists but is not a Git repository."
            )

        print(
            f"\nRepository already exists: {destination}"
        )

        try:
            repo = Repo(destination)

            print("Updating existing repository...")

            origin = repo.remotes.origin

            origin.fetch()

            # Reset local copy to remote state
            branch = repo.active_branch.name

            repo.git.reset(
                "--hard",
                f"origin/{branch}",
            )

            print("Repository updated successfully.")

        except GitCommandError as error:
            raise RuntimeError(
                f"Failed to update repository: {error}"
            ) from error

        return destination

    # -----------------------------------------
    # Repository doesn't exist → clone
    # -----------------------------------------

    print(f"\nCloning {repo_url}...")

    try:
        Repo.clone_from(
            repo_url,
            destination,
            depth=1,
        )

    except GitCommandError as error:
        raise RuntimeError(
            f"Failed to clone repository: {error}"
        ) from error

    print(
        f"Repository cloned to {destination}"
    )

    return destination