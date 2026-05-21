import os


def pack_py_files(directory=".", output="packed.py"):
    with open(output, "w", encoding="utf-8") as out:
        for fn in os.listdir(directory):
            if fn.endswith(".py") and fn != output:
                with open(fn, encoding="utf-8") as f:
                    out.write(f"# --- {fn} ---\n")
                    out.write(f.read() + "\n")
    print("Alle Codes gepackt!")
