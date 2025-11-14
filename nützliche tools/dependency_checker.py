#!/usr/bin/env python3
"""
Überprüft und aktualisiert Python-Dependencies
"""
import json
import subprocess
import sys


def check_outdated_packages():
    """Prüft veraltete Pakete"""

    result = subprocess.run([sys.executable,
                             '-m',
                             'pip',
                             'list',
                             '--outdated',
                             '--format=json'],
                            capture_output=True,
                            text=True)

    if result.returncode == 0:
        outdated = json.loads(result.stdout)

        if outdated:
            print(f"[PACKAGE] VERALTETE PAKETE ({len(outdated)}):")
            for package in outdated:
                print(
                    f"  📌 {
                        package['name']}: {
                        package['version']} → {
                        package['latest_version']}")

            update_all = input("\n🔄 Alle Pakete aktualisieren? (y/n): ")
            if update_all.lower() == 'y':
                for package in outdated:
                    print(f"⬆️ Aktualisiere {package['name']}...")
                    subprocess.run([sys.executable, '-m', 'pip',
                                   'install', '--upgrade', package['name']])
                print("[OK] Alle Pakete aktualisiert!")
        else:
            print("[OK] Alle Pakete sind aktuell!")
    else:
        print("[ERROR] Fehler beim Prüfen der Pakete")


def check_security_vulnerabilities():
    """Prüft Sicherheitslücken in Dependencies"""

    print("\n🔒 SICHERHEITS-CHECK:")

    try:
        # Installiere safety wenn nicht vorhanden
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'safety'],
                       capture_output=True)

        # Führe Sicherheits-Check aus
        result = subprocess.run([sys.executable, '-m', 'safety', 'check'],
                                capture_output=True, text=True)

        if "No known security vulnerabilities found" in result.stdout:
            print("[OK] Keine Sicherheitslücken gefunden!")
        else:
            print("[WARNING] SICHERHEITSLÜCKEN GEFUNDEN:")
            print(result.stdout)
    except BaseException:
        print("[ERROR] Safety-Check nicht verfügbar")


if __name__ == "__main__":
    check_outdated_packages()
    check_security_vulnerabilities()
