import os
import re


def clean_imports(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, encoding="utf-8") as f:
                content = f.readlines()
            imports = set()
            new_lines = []
            for line in content:
                m = re.match(
                    r"^\s*import (\w+)",
                    line) or re.match(
                    r"^\s*from (\w+)",
                    line)
                if m:
                    if m.group(1) not in imports:
                        imports.add(m.group(1))
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            with open(filename, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
    print("✅ Unnötige doppelte Imports entfernt!")
