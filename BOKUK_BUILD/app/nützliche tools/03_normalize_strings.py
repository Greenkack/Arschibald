import os
import unicodedata


def normalize_strings(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, encoding="utf-8") as f:
                content = f.read()
            content = unicodedata.normalize("NFKC", content)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
    print("✅ Alle Strings unicode-normalisiert.")
