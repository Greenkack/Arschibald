#!/usr/bin/env python3
"""
Automatischer Requirements.txt Generator
"""
import ast
import glob
import subprocess
import sys


def generate_requirements():
    """Erstellt requirements.txt basierend auf tatsächlichen Imports"""

    # Sammle alle Imports
    all_imports = set()

    for file_path in glob.glob("**/*.py", recursive=True):
        try:
            with open(file_path, encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        all_imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        all_imports.add(node.module.split('.')[0])
        except BaseException:
            continue

    # Standard-Module ausschließen
    stdlib_modules = {
        'os', 'sys', 'json', 're', 'datetime', 'time', 'math', 'random',
        'collections', 'itertools', 'functools', 'operator', 'pathlib',
        'typing', 'dataclasses', 'enum', 'abc', 'contextlib', 'warnings'
    }

    external_imports = all_imports - stdlib_modules

    # Hole installierte Versionen
    requirements = []
    for module in sorted(external_imports):
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', module],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':')[1].strip()
                        requirements.append(f"{module}=={version}")
                        break
            else:
                requirements.append(module)  # Ohne Version
        except BaseException:
            requirements.append(module)

    # Schreibe requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))

    print(f"📦 Requirements.txt erstellt mit {len(requirements)} Paketen:")
    for req in requirements:
        print(f"  - {req}")


if __name__ == "__main__":
    generate_requirements()
