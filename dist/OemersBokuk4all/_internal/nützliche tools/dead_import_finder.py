import os


def find_unused_imports(filename):
    # Nutzt isort und autoflake (pip install isort autoflake)
    os.system(f"autoflake --remove-all-unused-imports --in-place {filename}")
    print("Unbenutzte Imports entfernt.")
