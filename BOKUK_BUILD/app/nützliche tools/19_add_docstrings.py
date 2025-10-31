import ast


def add_docstrings(filename):
    with open(filename, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and ast.get_docstring(
                node) is None:
            print(f"Funktion {node.name} ohne Docstring.")
