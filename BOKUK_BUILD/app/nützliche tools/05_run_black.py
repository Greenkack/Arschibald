import os


def run_black(directory="."):
    os.system(f"black {directory}")
    print("✅ Black-Formatierung abgeschlossen.")
