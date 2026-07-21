import ast
from pathlib import Path


def parse_python_file(file_path: Path) -> ast.Module | None:
    """
    Parse a Python file into an AST.
    """
    source = file_path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    return tree


def parse_repository_file(file_path: Path) -> dict | None:
    """
    Parse a repository file and extract all useful metadata.
    """
    tree = parse_python_file(file_path)

    if tree is None:
        return None

    source = file_path.read_text(encoding="utf-8")

    return {
        "file": str(file_path),
        "source": source,
        "functions": extract_functions(tree, source),
        "async_functions": extract_async_functions(tree, source),
        "classes": extract_classes(tree, source),
        "imports": extract_imports(tree),
        "module_docstring": extract_module_docstring(tree),
        "function_docstrings": extract_function_docstrings(tree),
        "class_docstrings": extract_class_docstrings(tree),
        "assignments": extract_assignments(tree),
    }


# ---------------------------------------------------------
# Function Extraction
# ---------------------------------------------------------

def extract_functions(tree: ast.Module, source: str) -> list[dict]:
    functions = []
    lines = source.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):

            code = "\n".join(
                lines[node.lineno - 1 : node.end_lineno]
            )

            functions.append(
                {
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                    "code": code,
                }
            )

    return functions


def extract_async_functions(tree: ast.Module, source: str) -> list[dict]:
    functions = []
    lines = source.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):

            code = "\n".join(
                lines[node.lineno - 1 : node.end_lineno]
            )

            functions.append(
                {
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                    "code": code,
                }
            )

    return functions


# ---------------------------------------------------------
# Class Extraction
# ---------------------------------------------------------

def extract_classes(tree: ast.Module, source: str) -> list[dict]:
    classes = []
    lines = source.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):

            code = "\n".join(
                lines[node.lineno - 1 : node.end_lineno]
            )

            classes.append(
                {
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                    "code": code,
                }
            )

    return classes


# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

def extract_imports(tree: ast.Module) -> list[str]:
    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            for alias in node.names:
                imports.append(f"{module}.{alias.name}")

    return imports


# ---------------------------------------------------------
# Docstrings
# ---------------------------------------------------------

def extract_module_docstring(tree: ast.Module) -> str | None:
    return ast.get_docstring(tree)


def extract_function_docstrings(tree: ast.Module) -> list[dict]:
    docs = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docs.append(
                {
                    "function": node.name,
                    "docstring": ast.get_docstring(node),
                }
            )

    return docs


def extract_class_docstrings(tree: ast.Module) -> list[dict]:
    docs = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docs.append(
                {
                    "class": node.name,
                    "docstring": ast.get_docstring(node),
                }
            )

    return docs


# ---------------------------------------------------------
# Assignments
# ---------------------------------------------------------

def extract_assignments(tree: ast.Module) -> list[str]:
    assignments = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):
                    assignments.append(target.id)

    return assignments