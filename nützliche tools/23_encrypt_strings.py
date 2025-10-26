import ast

import astor
from cryptography.fernet import Fernet

key = Fernet.generate_key()
fernet = Fernet(key)


class EncryptStrings(ast.NodeTransformer):
    def visit_Str(self, node):
        encrypted = fernet.encrypt(node.s.encode()).decode()
        return ast.copy_location(
            ast.Call(func=ast.Name(id='fernet.decrypt', ctx=ast.Load()),
                     args=[ast.Str(s=encrypted)],
                     keywords=[]), node)


def encrypt_strings_in_file(filename):
    with open(filename, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    tree = EncryptStrings().visit(tree)
    code = astor.to_source(tree)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    print("Alle Strings sind jetzt verschlüsselt (nur lauffähig mit passendem Schlüssel).")
