"""
Hilfsskript zum Löschen des Streamlit Session State Cache
Nützlich nach Datenbank- oder Model-Änderungen
"""
import shutil
from pathlib import Path

def clear_streamlit_cache():
    """Löscht Streamlit Cache und Session State Dateien"""
    cache_dirs = [
        Path.home() / ".streamlit" / "cache",
        Path.home() / ".streamlit" / "sessions",
        Path(".streamlit_cache"),
    ]
    
    deleted = 0
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir)
                print(f"✓ Gelöscht: {cache_dir}")
                deleted += 1
            except Exception as e:
                print(f"✗ Fehler bei {cache_dir}: {e}")
    
    if deleted == 0:
        print("Keine Cache-Dateien gefunden")
    else:
        print(f"\n✓ {deleted} Cache-Verzeichnis(se) gelöscht")
    
    print("\nBitte starten Sie die Streamlit-App neu:")
    print("  streamlit run gui.py")

if __name__ == "__main__":
    print("=== Streamlit Session State & Cache Bereinigung ===\n")
    clear_streamlit_cache()
