#!/usr/bin/env python3
"""
Python & Streamlit Cache Cleaner
================================
Löscht alle Python- und Streamlit-Caches für bessere Performance
"""
import glob
import os
import shutil


def clear_python_cache():
    """Löscht alle Python __pycache__ Ordner"""

    cache_dirs = []

    # Finde alle __pycache__ Ordner
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_dir = os.path.join(root, "__pycache__")
            cache_dirs.append(cache_dir)

    print("🐍 PYTHON CACHE BEREINIGUNG:")
    print(f"📁 Gefundene __pycache__ Ordner: {len(cache_dirs)}")

    deleted_count = 0
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"  ✅ Gelöscht: {cache_dir}")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Fehler bei {cache_dir}: {e}")

    # Lösche .pyc Dateien
    pyc_files = glob.glob("**/*.pyc", recursive=True)
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            deleted_count += 1
        except BaseException:
            pass

    print(f"✅ {deleted_count} Python-Cache-Einträge gelöscht")
    return deleted_count


def clear_streamlit_cache():
    """Löscht Streamlit Cache-Ordner"""

    streamlit_dirs = [
        os.path.expanduser("~/.streamlit"),
        ".streamlit",
        "streamlit_cache",
    ]

    print("\n🚀 STREAMLIT CACHE BEREINIGUNG:")

    deleted_count = 0
    for streamlit_dir in streamlit_dirs:
        if os.path.exists(streamlit_dir):
            cache_subdir = os.path.join(streamlit_dir, "cache")
            if os.path.exists(cache_subdir):
                try:
                    shutil.rmtree(cache_subdir)
                    print(f"  ✅ Gelöscht: {cache_subdir}")
                    deleted_count += 1
                except Exception as e:
                    print(f"  ❌ Fehler bei {cache_subdir}: {e}")

    # Lösche temporäre Streamlit Dateien
    temp_patterns = [
        "**/streamlit-*.tmp",
        "**/st_*_cache",
        "**/.streamlit_cache",
    ]

    for pattern in temp_patterns:
        for temp_file in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                elif os.path.isdir(temp_file):
                    shutil.rmtree(temp_file)
                deleted_count += 1
            except BaseException:
                pass

    print(f"✅ {deleted_count} Streamlit-Cache-Einträge gelöscht")
    return deleted_count


def clear_all_caches():
    """Löscht alle Caches"""

    print("🧹 KOMPLETTE CACHE-BEREINIGUNG GESTARTET")
    print("=" * 50)

    python_deleted = clear_python_cache()
    streamlit_deleted = clear_streamlit_cache()

    total_deleted = python_deleted + streamlit_deleted

    print("\n🎉 CACHE-BEREINIGUNG ABGESCHLOSSEN!")
    print(f"📊 Insgesamt {total_deleted} Cache-Einträge gelöscht")
    print("💾 Freier Speicherplatz gewonnen!")

    return total_deleted


if __name__ == "__main__":
    clear_all_caches()
