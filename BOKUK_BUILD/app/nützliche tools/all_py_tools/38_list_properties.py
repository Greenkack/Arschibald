import ast


def list_properties(filename):
    with open(filename) as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(
                node,
                ast.FunctionDef) and any(
                'property' in d.id for d in node.decorator_list if hasattr(
                d,
                'id')):
            print(node.name)
