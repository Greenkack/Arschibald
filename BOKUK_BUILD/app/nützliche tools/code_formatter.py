#!/usr/bin/env python3
"""
Automatischer Code-Formatter (Black + isort)
"""
import glob
import subprocess
import sys


def format_code():
    """Formatiert allen Python-Code automatisch"""

    python_files = glob.glob("**/*.py", recursive=True)

    print("🎨 CODE-FORMATIERUNG:")
    print(f"📁 Gefundene Python-Dateien: {len(python_files)}")

    # Installiere Formatter falls nötig
    formatters = ['black', 'isort', 'autopep8']
    for formatter in formatters:
        try:
            subprocess.run([sys.executable, '-m', formatter, '--version'],
                           capture_output=True, check=True)
        except BaseException:
            print(f"📦 Installiere {formatter}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', formatter])

    # Black Formatierung
    print("🖤 Führe Black-Formatierung aus...")
    result = subprocess.run([sys.executable,
                             '-m',
                             'black',
                             '.',
                             '--line-length=100'],
                            capture_output=True,
                            text=True)
    print(f"  {result.stdout.count('reformatted')} Dateien reformatiert")

    # isort Import-Sortierung
    print("📋 Sortiere Imports mit isort...")
    subprocess.run([sys.executable, '-m', 'isort', '.'])

    # AutoPEP8 für PEP8-Konformität
    print("📏 PEP8-Korrekturen mit autopep8...")
    for py_file in python_files:
        subprocess.run([sys.executable, '-m', 'autopep8',
                       '--in-place', '--aggressive', py_file])

    print("✅ Code-Formatierung abgeschlossen!")


def check_code_quality():
    """Prüft Code-Qualität mit flake8"""

    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'flake8'],
                       capture_output=True)

        print("\n🔍 CODE-QUALITÄTS-CHECK:")
        result = subprocess.run([sys.executable,
                                 '-m',
                                 'flake8',
                                 '.',
                                 '--max-line-length=100'],
                                capture_output=True,
                                text=True)

        if result.stdout:
            print("⚠️ Code-Qualitäts-Probleme gefunden:")
            print(result.stdout)
        else:
            print("✅ Code-Qualität ist gut!")
    except BaseException:
        print("❌ flake8 nicht verfügbar")


if __name__ == "__main__":
    format_code()
    check_code_quality()
