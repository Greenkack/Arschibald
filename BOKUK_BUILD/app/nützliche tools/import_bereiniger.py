#!/usr/bin/env python3
"""
Entfernt ungenutzte Imports aus Python-Dateien
"""
import ast
import glob


def clean_unused_imports(file_path):
    """Entfernt ungenutzte Imports"""

    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except BaseException:
        print(f"❌ Syntax-Fehler in {file_path}")
        return

    # Sammle alle Imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append(alias.name)

    # Sammle alle verwendeten Namen
    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)

    # Finde ungenutzte Imports
    unused_imports = [imp for imp in imports if imp not in used_names]

    if unused_imports:
        print(f"🧹 Ungenutzte Imports in {file_path}: {unused_imports}")
        # Hier könnte man sie automatisch entfernen
    else:
        print(f"✅ {file_path} hat keine ungenutzten Imports")


# Alle Python-Dateien prüfen
for file_path in glob.glob("*.py"):
    clean_unused_imports(file_path)
