import ast
from pathlib import Path


def _start_line_with_decorators(node) -> int:
    """
    Return the first source line belonging to a definition,
    including decorators such as @router.get(...).
    """

    if getattr(node, "decorator_list", None):
        return min(
            decorator.lineno
            for decorator in node.decorator_list
        )

    return node.lineno


def _extract_code(
    lines: list[str],
    node,
    start_line: int | None = None,
    end_line: int | None = None,
) -> str:

    start = start_line or _start_line_with_decorators(node)
    end = end_line or node.end_lineno

    return "\n".join(lines[start - 1:end])


def extract_functions(
    tree: ast.Module,
    source: str,
) -> list[dict]:
    """
    Extract only top-level synchronous functions.

    Methods inside classes are handled by extract_classes().
    """

    functions = []
    lines = source.splitlines()

    for node in tree.body:

        if not isinstance(node, ast.FunctionDef):
            continue

        start_line = _start_line_with_decorators(node)

        functions.append({
            "name": node.name,
            "start_line": start_line,
            "end_line": node.end_lineno,
            "code": _extract_code(
                lines,
                node,
                start_line=start_line,
            ),
        })

    return functions


def extract_async_functions(
    tree: ast.Module,
    source: str,
) -> list[dict]:
    """
    Extract only top-level asynchronous functions.
    """

    functions = []
    lines = source.splitlines()

    for node in tree.body:

        if not isinstance(node, ast.AsyncFunctionDef):
            continue

        start_line = _start_line_with_decorators(node)

        functions.append({
            "name": node.name,
            "start_line": start_line,
            "end_line": node.end_lineno,
            "code": _extract_code(
                lines,
                node,
                start_line=start_line,
            ),
        })

    return functions


def extract_classes(
    tree: ast.Module,
    source: str,
) -> list[dict]:
    """
    Extract top-level classes.

    Each class contains:
    - a class header chunk
    - separate method entries

    The full class body is NOT stored as one giant chunk.
    """

    classes = []
    lines = source.splitlines()

    for node in tree.body:

        if not isinstance(node, ast.ClassDef):
            continue

        class_start = _start_line_with_decorators(node)

        # Direct methods belonging to this class.
        method_nodes = [
            child
            for child in node.body
            if isinstance(
                child,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )
        ]

        if method_nodes:

            first_method_start = min(
                _start_line_with_decorators(method)
                for method in method_nodes
            )

            header_end = first_method_start - 1

        else:
            header_end = node.end_lineno

        header_code = "\n".join(
            lines[class_start - 1:header_end]
        ).rstrip()

        methods = []

        for method in method_nodes:

            method_start = _start_line_with_decorators(method)

            method_code = _extract_code(
                lines,
                method,
                start_line=method_start,
            )

            methods.append({
                "name": f"{node.name}.{method.name}",
                "method_name": method.name,
                "class_name": node.name,
                "start_line": method_start,
                "end_line": method.end_lineno,
                "code": method_code,
                "is_async": isinstance(
                    method,
                    ast.AsyncFunctionDef,
                ),
            })

        classes.append({
            "name": node.name,
            "start_line": class_start,
            "end_line": header_end,
            "code": header_code,
            "methods": methods,
        })

    return classes


def extract_imports(tree: ast.Module) -> list[str]:

    imports = []

    for node in tree.body:

        if isinstance(node, ast.Import):

            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            for alias in node.names:
                imports.append(
                    f"{module}.{alias.name}"
                    if module
                    else alias.name
                )

    return imports


def extract_module_docstring(tree: ast.Module) -> str | None:
    return ast.get_docstring(tree)


def extract_assignments(
    tree: ast.Module,
    source: str,
) -> list[dict]:

    assignments = []
    lines = source.splitlines()

    # Top-level assignments only.
    for node in tree.body:

        if not isinstance(
            node,
            (ast.Assign, ast.AnnAssign),
        ):
            continue

        code = "\n".join(
            lines[node.lineno - 1:node.end_lineno]
        )

        assignments.append({
            "start_line": node.lineno,
            "end_line": node.end_lineno,
            "code": code,
        })

    return assignments


def parse_python_file(file_path: Path) -> dict | None:

    try:
        source = file_path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        return None

    try:
        tree = ast.parse(source)

    except SyntaxError:
        return None

    return {
        "file": str(file_path),
        "functions": extract_functions(
            tree,
            source,
        ),
        "async_functions": extract_async_functions(
            tree,
            source,
        ),
        "classes": extract_classes(
            tree,
            source,
        ),
        "imports": extract_imports(tree),
        "module_docstring": extract_module_docstring(tree),
        "assignments": extract_assignments(
            tree,
            source,
        ),
    }


def parse_repository_file(file_path: Path) -> dict | None:
    return parse_python_file(file_path)