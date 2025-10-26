import ast

import astor


class TraceInjector(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        name = node.name
        args = [a.arg for a in node.args.args]
        before = ast.parse(f'print("CALL: {name}, args={args}")').body
        node.body = before + node.body
        return node


def inject_tracing(filename):
    with open(filename, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    tree = TraceInjector().visit(tree)
    new_code = astor.to_source(tree)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_code)
    print("Trace-Logging injected!")
