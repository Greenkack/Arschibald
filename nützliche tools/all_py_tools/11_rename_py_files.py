import os


def rename_py_files(directory=".", prefix="mod_"):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            newname = prefix + filename
            os.rename(
                os.path.join(
                    directory, filename), os.path.join(
                    directory, newname))
    print("✅ Dateien umbenannt.")
