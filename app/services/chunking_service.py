from pathlib import Path

from app.services.parser_service import parse_repository_file


def chunk_repository(repo_path: Path) -> list[dict]:

    chunks = []

    for file_path in repo_path.rglob("*.py"):

        parsed = parse_repository_file(file_path)

        if parsed is None:
            continue

        # -----------------------------------------
        # TOP-LEVEL FUNCTIONS
        # -----------------------------------------

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

        # -----------------------------------------
        # TOP-LEVEL ASYNC FUNCTIONS
        # -----------------------------------------

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

        # -----------------------------------------
        # CLASSES + METHODS
        # -----------------------------------------

        for cls in parsed["classes"]:

            # Class header
            if cls["code"].strip():

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

            # Individual methods
            for method in cls["methods"]:

                chunks.append({
                    "content": method["code"],
                    "metadata": {
                        "file": parsed["file"],
                        "type": (
                            "async_method"
                            if method["is_async"]
                            else "method"
                        ),
                        "name": method["name"],
                        "class_name": method["class_name"],
                        "method_name": method["method_name"],
                        "start_line": method["start_line"],
                        "end_line": method["end_line"],
                    },
                })

    return chunks