#!/usr/bin/env python3
"""
Bereinigt Debug-Logs und Print-Statements
"""
import glob
import os
import re


def clean_debug_statements(directory="."):
    """Entfernt Debug-Print-Statements"""

    debug_patterns = [
        r'print\s*\(\s*["\']DEBUG:.*?\).*?\n',
        r'print\s*\(\s*["\']DB DEBUG:.*?\).*?\n',
        r'print\s*\(\s*["\']TRACE:.*?\).*?\n',
        r'print\s*\(\s*f["\']DEBUG:.*?\).*?\n',
        r'# DEBUG:.*?\n',
        r'# TODO:.*?\n',
        r'# FIXME:.*?\n',
    ]

    cleaned_files = 0
    total_removals = 0

    for file_path in glob.glob(os.path.join(directory, "*.py")):
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            original_content = content
            file_removals = 0

            for pattern in debug_patterns:
                matches = len(re.findall(pattern, content, re.MULTILINE))
                if matches > 0:
                    content = re.sub(pattern, '', content, flags=re.MULTILINE)
                    file_removals += matches

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                cleaned_files += 1
                total_removals += file_removals
                print(
                    f"🧹 {
                        os.path.basename(file_path)}: {file_removals} Debug-Statements entfernt")

        except Exception as e:
            print(f"❌ Fehler bei {file_path}: {e}")

    print(
        f"\n🎉 {cleaned_files} Dateien bereinigt, {total_removals} Debug-Statements entfernt!")


if __name__ == "__main__":
    clean_debug_statements()
