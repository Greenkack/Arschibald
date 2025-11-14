#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Installiere fehlende Dependencies aus Mariana-Graben Analyse
"""

import subprocess
import sys

# Liste der 10 fehlenden Packages
MISSING_PACKAGES = [
    'annotated-types',
    'APScheduler',
    'beautifulsoup4',
    'bleach',
    'geopy',
    'jinja2',
    'markdown',
    'PyMuPDF',
    'weasyprint',
    'yaml',
]

def install_packages():
    print("=" * 80)
    print("[PACKAGE] INSTALLATION FEHLENDER DEPENDENCIES")
    print("=" * 80)
    print(f"\nInstalliere {len(MISSING_PACKAGES)} Packages...\n")
    
    failed = []
    
    for i, package in enumerate(MISSING_PACKAGES, 1):
        print(f"[{i}/{len(MISSING_PACKAGES)}] Installiere {package}...")
        
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"   [OK] {package} erfolgreich installiert")
            else:
                print(f"   [ERROR] {package} Installation fehlgeschlagen")
                failed.append((package, result.stderr[:100]))
        
        except Exception as e:
            print(f"   [ERROR] {package} Fehler: {str(e)[:50]}")
            failed.append((package, str(e)))
    
    print("\n" + "=" * 80)
    print("INSTALLATION ABGESCHLOSSEN")
    print("=" * 80)
    
    if failed:
        print(f"\n[WARNING]  {len(failed)} Fehler:")
        for pkg, err in failed:
            print(f"   • {pkg}: {err}")
    else:
        print("\n🎉 ALLE PACKAGES ERFOLGREICH INSTALLIERT!")
    
    return len(failed) == 0

if __name__ == "__main__":
    success = install_packages()
    sys.exit(0 if success else 1)
