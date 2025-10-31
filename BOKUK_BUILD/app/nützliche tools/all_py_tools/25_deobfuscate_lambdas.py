import re


def deobfuscate_lambdas(filename):
    with open(filename, encoding="utf-8") as f:
        code = f.read()
    matches = re.findall(r'(lambda\s.*?:\s.*?)(?=[,\)\n])', code)
    for match in matches:
        print(f"Lambda gefunden: {match}")
