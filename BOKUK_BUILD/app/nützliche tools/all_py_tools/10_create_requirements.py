import ast
import os


def create_requirements(directory="."):
    imports = set()
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        imports.add(n.name.split('.')[0])
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
    with open("requirements_auto.txt", "w") as f:
        for i in sorted(imports):
            f.write(i + "\n")
    print("✅ requirements_auto.txt erstellt!")
