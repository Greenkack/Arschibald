import os


def tabs_to_spaces(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, encoding="utf-8") as f:
                content = f.read()
            content = content.replace("\t", "    ")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
    print("✅ Alle Tabs in 4 Spaces konvertiert!")
