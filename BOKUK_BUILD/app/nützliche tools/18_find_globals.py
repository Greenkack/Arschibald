import ast


def find_globals(filename):
    with open(filename, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Global):
            print(f"Globale Variable: {node.names}")
