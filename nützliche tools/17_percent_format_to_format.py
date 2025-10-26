import os
import re


def convert_percent_format(directory="."):
    pattern = re.compile(r'(["\'].*?["\'])\s*%\s*\(?.*?\)?')
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            with open(filename, encoding="utf-8") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if "%" in line and ".format(" not in line:
                    line = pattern.sub(
                        lambda m: f"{
                            m.group(1)}.format()", line)
                new_lines.append(line)
            with open(filename, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
    print("✅ Prozent-Formatierung umgestellt.")
