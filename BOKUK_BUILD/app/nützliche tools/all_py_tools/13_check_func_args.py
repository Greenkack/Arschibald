import ast


def check_func_args(filename, max_args=5):
    with open(filename, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if len(node.args.args) > max_args:
                print(
                    f"Funktion {node.name} hat zu viele Argumente: {len(node.args.args)}")
