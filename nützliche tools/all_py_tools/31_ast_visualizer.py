import ast

import astpretty


def visualize_ast(filename):
    with open(filename) as f:
        tree = ast.parse(f.read())
    astpretty.pprint(tree)
