#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SESSION CLEANER: Entfernt alte Daikin-Daten aus Session-Files
"""

import os
import json
from pathlib import Path

def clean_session_files():
    """Bereinigt alle Streamlit Session-Dateien von ungültigen Herstellern"""
    
    print("=" * 80)
    print("SESSION CLEANER - Entferne ungültige Hersteller")
    print("=" * 80)
    
    allowed_manufacturers = ['Viessmann', 'Buderus', 'Vaillant']
    forbidden = ['Daikin', 'Mitsubishi', 'LG', 'Samsung', 'Panasonic']
    
    # Finde alle Session-Verzeichnisse
    session_dirs = []
    
    # Streamlit Session-Cache Verzeichnisse
    possible_locations = [
        Path.home() / '.streamlit' / 'sessions',
        Path('.streamlit') / 'sessions',
        Path('sessions'),
        Path('.') / '.streamlit',
    ]
    
    for loc in possible_locations:
        if loc.exists():
            session_dirs.append(loc)
            print(f"[OK] Gefunden: {loc}")
    
    if not session_dirs:
        print("\n[WARNING] Keine Session-Verzeichnisse gefunden")
        print("\n[INFO] LÖSUNG: Session wird beim nächsten App-Start automatisch bereinigt!")
        print("   Die Validierung in heatpump_ui.py filtert ungültige Hersteller.")
        return
    
    cleaned_count = 0
    
    for session_dir in session_dirs:
        print(f"\nPrüfe: {session_dir}")
        
        # Suche nach JSON/pickle Dateien
        for file in session_dir.rglob("*"):
            if file.is_file():
                try:
                    if file.suffix == '.json':
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Prüfe auf ungültige Hersteller
                        needs_cleaning = False
                        
                        if isinstance(data, dict):
                            if 'heatpump_data' in data:
                                hp = data['heatpump_data'].get('selected_heatpump', {})
                                mfr = hp.get('manufacturer', '')
                                if mfr in forbidden:
                                    print(f"  [ERROR] UNGÜLTIG: {mfr} in {file.name}")
                                    needs_cleaning = True
                        
                        if needs_cleaning:
                            # Lösche die Datei
                            file.unlink()
                            cleaned_count += 1
                            print(f"  [DELETE]  GELÖSCHT: {file.name}")
                
                except Exception as e:
                    # Ignoriere Fehler beim Lesen
                    pass
    
    print("\n" + "=" * 80)
    print(f"[OK] BEREINIGT: {cleaned_count} Session-Dateien gelöscht")
    print("=" * 80)
    
    if cleaned_count == 0:
        print("\n[OK] Keine ungültigen Session-Daten gefunden!")
        print("\n[INFO] Falls Daikin noch angezeigt wird:")
        print("   1. App neu starten (Strg+C, dann neu starten)")
        print("   2. Browser-Cache leeren (Strg+Shift+R)")
        print("   3. Session-State wird automatisch validiert!")

if __name__ == "__main__":
    clean_session_files()
