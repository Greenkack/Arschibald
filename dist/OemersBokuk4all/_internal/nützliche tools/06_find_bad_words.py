import os


def find_bad_words(directory=".", words=None):
    if words is None:
        words = ["eval", "exec", "pickle.loads"]
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    for w in words:
                        if w in line:
                            print(f"{filename}:{i}: {w}")
