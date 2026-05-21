import os


def check_line_length(directory=".", max_len=79):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if len(line) > max_len:
                        print(f"{filename}:{i} ist {len(line)} Zeichen lang.")
