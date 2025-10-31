import os


def remove_empty_lines(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, encoding="utf-8") as f:
                lines = f.readlines()
            lines = [line for line in lines if line.strip()]
            with open(filename, "w", encoding="utf-8") as f:
                f.writelines(lines)
    print("✅ Leere Zeilen entfernt.")
