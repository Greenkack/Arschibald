import re


def remove_debug_prints(file):
    with open(file) as f:
        lines = f.readlines()
    with open(file, "w") as f:
        for line in lines:
            if not re.match(r"\s*print\(", line):
                f.write(line)
