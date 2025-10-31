import os
import re


def convert_print_to_logging(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r'print\((.*)\)', r'logging.info(\1)', content)
            if "import logging" not in content:
                content = "import logging\n" + content
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
    print("✅ Alle print() zu logging.info() konvertiert.")
