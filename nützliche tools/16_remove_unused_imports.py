import os


def find_unused_imports(filename):
    os.system(f"autoflake --remove-all-unused-imports --in-place {filename}")
    print("Unbenutzte Imports entfernt.")
