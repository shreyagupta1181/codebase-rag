from pathlib import Path

from app.services.parser_service import parse_repository_file


def chunk_repository(repo_path: Path):

    chunks = []

    for file_path in repo_path.rglob("*.py"):

        parsed = parse_repository_file(file_path)

        if parsed is None:
            continue

        # Function chunks
        for function in parsed["functions"]:

            chunks.append({
                "content": function["code"],
                "metadata": {
                    "file": parsed["file"],
                    "type": "function",
                    "name": function["name"],
                    "start_line": function["start_line"],
                    "end_line": function["end_line"],
                },
            })

        # Async function chunks
        for function in parsed["async_functions"]:

            chunks.append({
                "content": function["code"],
                "metadata": {
                    "file": parsed["file"],
                    "type": "async_function",
                    "name": function["name"],
                    "start_line": function["start_line"],
                    "end_line": function["end_line"],
                },
            })

        # Class chunks
        for cls in parsed["classes"]:

            chunks.append({
                "content": cls["code"],
                "metadata": {
                    "file": parsed["file"],
                    "type": "class",
                    "name": cls["name"],
                    "start_line": cls["start_line"],
                    "end_line": cls["end_line"],
                },
            })

    return chunks