"""
Löscht alle Python Cache-Dateien (.pyc, __pycache__) im Projekt.
"""

import os
import shutil
from pathlib import Path

def clear_cache(root_dir: str) -> tuple:
    """Löscht alle Python Cache-Dateien."""
    deleted_dirs = 0
    deleted_files = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Lösche __pycache__ Verzeichnisse
        if '__pycache__' in dirnames:
            pycache_path = os.path.join(dirpath, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                deleted_dirs += 1
                print(f"Gelöscht: {pycache_path}")
            except Exception as e:
                print(f"Fehler: {pycache_path} - {e}")
        
        # Lösche .pyc Dateien
        for filename in filenames:
            if filename.endswith('.pyc'):
                pyc_path = os.path.join(dirpath, filename)
                try:
                    os.remove(pyc_path)
                    deleted_files += 1
                    print(f"Gelöscht: {pyc_path}")
                except Exception as e:
                    print(f"Fehler: {pyc_path} - {e}")
    
    return deleted_dirs, deleted_files


def main():
    print("=" * 80)
    print("🧹 Python Cache Cleaner")
    print("=" * 80)
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\nArbeitsverzeichnis: {root_dir}")
    print("\n⏳ Lösche Cache-Dateien...\n")
    
    dirs, files = clear_cache(root_dir)
    
    print("\n" + "=" * 80)
    print(f"Fertig!")
    print(f"Statistik:")
    print(f"   - Gelöschte __pycache__ Verzeichnisse: {dirs}")
    print(f"   - Gelöschte .pyc Dateien: {files}")
    print("=" * 80)
    print("\nBitte Streamlit-App neu starten!")


if __name__ == "__main__":
    main()
