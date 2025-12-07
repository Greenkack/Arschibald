#!/usr/bin/env python3
"""
Analysiert Code-Statistiken
"""
import ast
import glob
import os


def analyze_code_stats(directory="."):
    """Erstellt umfassende Code-Statistiken"""

    stats = {
        'total_files': 0,
        'total_lines': 0,
        'total_functions': 0,
        'total_classes': 0,
        'files_with_errors': 0,
        'largest_files': [],
        'function_count_by_file': {},
        'complexity_warnings': []
    }

    for file_path in glob.glob(os.path.join(directory, "*.py")):
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            stats['total_files'] += 1
            stats['total_lines'] += len(lines)

            # Parse AST für Funktionen/Klassen
            try:
                tree = ast.parse(content)
                functions = [
                    node for node in ast.walk(tree) if isinstance(
                        node, ast.FunctionDef)]
                classes = [
                    node for node in ast.walk(tree) if isinstance(
                        node, ast.ClassDef)]

                stats['total_functions'] += len(functions)
                stats['total_classes'] += len(classes)
                stats['function_count_by_file'][file_path] = len(functions)

                # Komplexitäts-Warnung für große Dateien
                if len(lines) > 500:
                    stats['complexity_warnings'].append(
                        f"{file_path}: {len(lines)} Zeilen")

                # Größte Dateien merken
                stats['largest_files'].append((file_path, len(lines)))

            except SyntaxError:
                stats['files_with_errors'] += 1

        except Exception as e:
            print(f"Fehler bei {file_path}: {e}")

    # Sortiere größte Dateien
    stats['largest_files'] = sorted(
        stats['largest_files'],
        key=lambda x: x[1],
        reverse=True)[
        :10]

    # Ausgabe
    print("CODE-STATISTIKEN:")
    print(f"Dateien: {stats['total_files']}")
    print(f"Zeilen: {stats['total_lines']:,}")
    print(f"Funktionen: {stats['total_functions']}")
    print(f" Klassen: {stats['total_classes']}")
    print(f"Dateien mit Fehlern: {stats['files_with_errors']}")

    print("\n GRÖßTE DATEIEN:")
    for file_path, line_count in stats['largest_files']:
        print(f"  {line_count:4d} Zeilen - {os.path.basename(file_path)}")

    if stats['complexity_warnings']:
        print("\nKOMPLEXITÄTS-WARNUNGEN:")
        for warning in stats['complexity_warnings']:
            print(f"  {warning}")

    return stats


if __name__ == "__main__":
    analyze_code_stats()
