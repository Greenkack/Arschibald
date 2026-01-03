import os


def todo_list(directory="."):
    todos = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, encoding="utf-8") as f:
                    for num, line in enumerate(f, 1):
                        if "# TODO" in line:
                            todos.append(f"{path}:{num}: {line.strip()}")
    print("\n".join(todos))
