import os


def find_fixme(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if "FIXME" in line:
                        print(f"{filename}:{i}: {line.strip()}")
