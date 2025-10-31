#!/usr/bin/env python3
"""
🎭 STEGANOGRAPHY CODE INJECTOR
==============================
Versteckt Code in Kommentaren, Strings und Whitespace
"""
import ast
import base64
import zlib


class SteganographyInjector:

    def hide_code_in_comments(self, source_file, hidden_code):
        """Versteckt Code in Kommentaren mittels Unicode-Steganographie"""

        # Konvertiere hidden_code zu Binär
        hidden_binary = ''.join(format(ord(char), '08b')
                                for char in hidden_code)

        # Unicode Zero-Width Characters für Steganographie
        zero_width_chars = {
            '0': '\u200B',  # Zero Width Space
            '1': '\u200C',  # Zero Width Non-Joiner
        }

        # Verstecke Binär-Code in unsichtbaren Unicode-Zeichen
        hidden_unicode = ''.join(
            zero_width_chars[bit] for bit in hidden_binary)

        with open(source_file, encoding='utf-8') as f:
            content = f.read()

        # Füge versteckten Code in ersten Kommentar ein
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                lines[i] = line + hidden_unicode
                break

        modified_content = '\n'.join(lines)

        with open(f"{source_file}.steganified", 'w', encoding='utf-8') as f:
            f.write(modified_content)

        print(f"🎭 Code versteckt in {source_file}.steganified")
        return f"{source_file}.steganified"

    def extract_hidden_code(self, steganified_file):
        """Extrahiert versteckten Code aus steganifizierten Dateien"""

        zero_width_chars = {
            '\u200B': '0',  # Zero Width Space
            '\u200C': '1',  # Zero Width Non-Joiner
        }

        with open(steganified_file, encoding='utf-8') as f:
            content = f.read()

        # Extrahiere alle Zero-Width Characters
        hidden_binary = ''
        for char in content:
            if char in zero_width_chars:
                hidden_binary += zero_width_chars[char]

        if len(hidden_binary) % 8 != 0:
            print("❌ Kein versteckter Code gefunden")
            return None

        # Konvertiere Binär zurück zu Text
        hidden_code = ''
        for i in range(0, len(hidden_binary), 8):
            byte = hidden_binary[i:i + 8]
            if len(byte) == 8:
                hidden_code += chr(int(byte, 2))

        print(f"🔓 Versteckter Code extrahiert: {len(hidden_code)} Zeichen")
        return hidden_code

    def inject_payload_in_docstrings(self, target_file, payload):
        """Versteckt Payload in Docstrings mittels Base64 + Compression"""

        # Komprimiere und encode Payload
        compressed = zlib.compress(payload.encode('utf-8'))
        encoded = base64.b64encode(compressed).decode('ascii')

        # Aufteilen in kleinere Chunks für Docstrings
        chunk_size = 60
        chunks = [encoded[i:i + chunk_size]
                  for i in range(0, len(encoded), chunk_size)]

        with open(target_file) as f:
            tree = ast.parse(f.read())

        # Modifiziere AST - füge Docstrings hinzu
        class DocstringInjector(ast.NodeTransformer):
            def __init__(self):
                self.chunk_index = 0

            def visit_FunctionDef(self, node):
                if self.chunk_index < len(chunks):
                    # Erstelle Docstring mit verstecktem Payload
                    fake_docstring = f'"""\n    Internal optimization data: {
                        chunks[
                            self.chunk_index]}\n    """'

                    # Füge als ersten Statement hinzu wenn kein Docstring
                    # existiert
                    if not (node.body and isinstance(node.body[0], ast.Expr)
                            and isinstance(node.body[0].value, ast.Str)):
                        doc_node = ast.Expr(value=ast.Str(
                            s=f"Internal optimization data: {chunks[self.chunk_index]}"))
                        node.body.insert(0, doc_node)

                    self.chunk_index += 1

                return self.generic_visit(node)

        injector = DocstringInjector()
        modified_tree = injector.visit(tree)

        # Konvertiere zurück zu Code
        import astor
        modified_code = astor.to_source(modified_tree)

        with open(f"{target_file}.injected", 'w') as f:
            f.write(modified_code)

        print(f"💉 Payload in Docstrings versteckt: {target_file}.injected")
        return f"{target_file}.injected"


# Elite-Level Usage
if __name__ == "__main__":
    injector = SteganographyInjector()

    # Beispiel: Verstecke Admin-Password in harmlosem Code
    secret_payload = """
    ADMIN_PASSWORD = "ultra_secret_2024!"
    API_KEY = "sk-proj-abc123xyz789"
    DATABASE_URL = "postgresql://admin:secret@hidden-server.com/db"
    """

    injector.hide_code_in_comments("innocent_file.py", secret_payload)
    extracted = injector.extract_hidden_code("innocent_file.py.steganified")
    print(f"🔓 Extrahiert: {extracted}")
