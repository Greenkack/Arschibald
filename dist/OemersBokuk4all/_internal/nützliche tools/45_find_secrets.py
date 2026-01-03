import os
import re


def find_secrets(directory="."):
    pat = re.compile(r"(?i)(api|secret|key)[\s\:_=\-\"]+([a-z0-9\-_]{8,})")
    for root, _, files in os.walk(directory):
        for fn in files:
            if fn.endswith(".py"):
                with open(os.path.join(root, fn)) as f:
                    for line in f:
                        m = pat.search(line)
                        if m:
                            print(f"{fn}: {m.group(0)}")
