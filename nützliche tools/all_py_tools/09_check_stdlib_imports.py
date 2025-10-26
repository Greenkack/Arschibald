import ast
import sys


def check_stdlib_imports(filename):
    with open(filename, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    stdlib = sys.stdlib_module_names if hasattr(
        sys, 'stdlib_module_names') else []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name not in stdlib:
                    print(f"Nicht-Stdlib importiert: {n.name}")
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] not in stdlib:
                print(f"Nicht-Stdlib importiert: {node.module}")
