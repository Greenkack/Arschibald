import ast


def find_dead_functions(filename):
    with open(filename, encoding="utf-8") as f:
        code = f.read()
    tree = ast.parse(code)
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    used = set()
    for name in funcs:
        if name in code.split("def " + name)[1]:
            used.add(name)
    print("Nicht genutzte Funktionen:", set(funcs) - used)
