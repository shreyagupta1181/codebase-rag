from pathlib import Path
import json


STATE_FILE = Path("repository_state.json")


def set_active_repository(
    name: str,
    path: str,
    url: str,
    chunks_indexed: int,
) -> None:

    state = {
        "repository": name,
        "path": path,
        "url": url,
        "chunks_indexed": chunks_indexed,
        "status": "ready",
    }

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            state,
            f,
            indent=4,
        )


def get_active_repository() -> dict | None:

    if not STATE_FILE.exists():
        return None

    try:
        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):
        return None


def clear_active_repository() -> None:

    if STATE_FILE.exists():
        STATE_FILE.unlink()