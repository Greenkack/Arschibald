#!/usr/bin/env python3
"""
Intelligenter Code-Auskommentierer
"""
import re


def comment_out_functions(file_path, functions_to_comment):
    """Kommentiert spezifische Funktionen aus"""

    with open(file_path, encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    inside_function = False
    current_function = None
    indent_level = 0

    for line in lines:
        # Prüfe ob Funktionsdefinition
        func_match = re.match(r'^(\s*)def\s+(\w+)', line)
        if func_match:
            indent_level = len(func_match.group(1))
            current_function = func_match.group(2)
            inside_function = current_function in functions_to_comment

        # Prüfe ob wir noch in der Funktion sind
        if inside_function and line.strip():
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and not line.startswith(
                    ' ' * indent_level):
                inside_function = False

        # Kommentiere aus wenn nötig
        if inside_function:
            new_lines.append(f"# {line}")
        else:
            new_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"✅ Funktionen {functions_to_comment} in {file_path} auskommentiert")


# Verwendung:
comment_out_functions(
    "pdf_generator.py", [
        "generate_pdf", "create_pdf_content"])
