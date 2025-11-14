"""
Verifikations-Script für Geo-Mapping Implementation

Prüft, ob alle Komponenten korrekt implementiert sind.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Prüft, ob eine Datei existiert"""
    if os.path.exists(filepath):
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[ERROR] {description} fehlt: {filepath}")
        return False


def check_imports():
    """Prüft, ob alle Module importiert werden können"""
    print("\n" + "="*70)
    print("MODUL-IMPORTS PRÜFEN")
    print("="*70)
    
    all_ok = True
    
    # Hauptmodul
    try:
        from crm.features.geo_mapper import GeoMapper, ensure_geo_columns
        print("[OK] geo_mapper.py kann importiert werden")
    except ImportError as e:
        print(f"[ERROR] geo_mapper.py Import-Fehler: {e}")
        all_ok = False
    
    # UI-Modul
    try:
        from crm.features.geo_ui import show_geo_mapping_ui
        print("[OK] geo_ui.py kann importiert werden")
    except ImportError as e:
        print(f"[ERROR] geo_ui.py Import-Fehler: {e}")
        all_ok = False
    
    return all_ok


def check_dependencies():
    """Prüft, ob erforderliche Pakete installiert sind"""
    print("\n" + "="*70)
    print("ABHÄNGIGKEITEN PRÜFEN")
    print("="*70)
    
    dependencies = {
        'geopy': 'Geocoding',
        'folium': 'Kartenvisualisierung',
        'streamlit_folium': 'Streamlit-Integration'
    }
    
    all_ok = True
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            print(f"[OK] {package} installiert ({description})")
        except ImportError:
            print(f"[WARNING] {package} nicht installiert ({description})")
            print(f"   Installieren Sie mit: pip install {package.replace('_', '-')}")
            all_ok = False
    
    return all_ok


def check_functions():
    """Prüft, ob alle Hauptfunktionen verfügbar sind"""
    print("\n" + "="*70)
    print("FUNKTIONEN PRÜFEN")
    print("="*70)
    
    try:
        from crm.features.geo_mapper import GeoMapper
        
        # Erforderliche Methoden
        required_methods = [
            'geocode_address',
            'update_customer_coordinates',
            'geocode_all_customers',
            'get_customers_with_coordinates',
            'create_map',
            'calculate_distance',
            'optimize_route',
            'create_route_map',
            'export_route_to_calendar',
            'save_appointments_to_db'
        ]
        
        all_ok = True
        
        for method in required_methods:
            if hasattr(GeoMapper, method):
                print(f"[OK] GeoMapper.{method}() vorhanden")
            else:
                print(f"[ERROR] GeoMapper.{method}() fehlt")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"[ERROR] Fehler beim Prüfen der Funktionen: {e}")
        return False


def check_tests():
    """Prüft, ob Tests vorhanden sind"""
    print("\n" + "="*70)
    print("TESTS PRÜFEN")
    print("="*70)
    
    test_file = "crm/features/test_geo_mapper.py"
    
    if not os.path.exists(test_file):
        print(f"[ERROR] Test-Datei fehlt: {test_file}")
        return False
    
    print(f"[OK] Test-Datei vorhanden: {test_file}")
    
    # Tests ausführen
    print("\nTests ausführen...")
    import subprocess
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("[OK] Alle Tests bestanden")
            return True
        else:
            print("[ERROR] Einige Tests fehlgeschlagen")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("[WARNING] Tests dauern zu lange (Timeout)")
        return False
    except Exception as e:
        print(f"[ERROR] Fehler beim Ausführen der Tests: {e}")
        return False


def check_documentation():
    """Prüft, ob Dokumentation vorhanden ist"""
    print("\n" + "="*70)
    print("DOKUMENTATION PRÜFEN")
    print("="*70)
    
    docs = {
        'docs/GEO_MAPPING_QUICK_REFERENCE.md': 'Quick Reference',
        'crm/features/GEO_MAPPER_REFERENCE.md': 'API-Referenz',
        'crm/features/GEO_INTEGRATION_GUIDE.md': 'Integration Guide',
        'crm/features/geo_integration_example.py': 'Beispiele',
        'crm/features/geo_requirements.txt': 'Requirements',
        'TASK_21_GEO_MAPPING_COMPLETE.md': 'Abschluss-Dokumentation'
    }
    
    all_ok = True
    
    for filepath, description in docs.items():
        if check_file_exists(filepath, description):
            # Dateigröße prüfen
            size = os.path.getsize(filepath)
            print(f"   Größe: {size:,} Bytes")
        else:
            all_ok = False
    
    return all_ok


def check_database_schema():
    """Prüft, ob Datenbank-Schema korrekt ist"""
    print("\n" + "="*70)
    print("DATENBANK-SCHEMA PRÜFEN")
    print("="*70)
    
    try:
        from crm.features.geo_mapper import ensure_geo_columns
        
        # Geo-Spalten sicherstellen
        result = ensure_geo_columns()
        
        if result:
            print("[OK] Geo-Spalten vorhanden oder erfolgreich hinzugefügt")
            return True
        else:
            print("[ERROR] Fehler beim Hinzufügen der Geo-Spalten")
            return False
            
    except Exception as e:
        print(f"[ERROR] Fehler beim Prüfen des Schemas: {e}")
        return False


def run_verification():
    """Führt alle Verifikations-Checks durch"""
    print("\n" + "="*70)
    print("GEO-MAPPING VERIFIKATION")
    print("="*70)
    print("\nPrüft, ob alle Komponenten korrekt implementiert sind.\n")
    
    results = {
        'Dateien': check_documentation(),
        'Imports': check_imports(),
        'Abhängigkeiten': check_dependencies(),
        'Funktionen': check_functions(),
        'Datenbank': check_database_schema(),
        'Tests': check_tests()
    }
    
    # Zusammenfassung
    print("\n" + "="*70)
    print("ZUSAMMENFASSUNG")
    print("="*70)
    
    for check, result in results.items():
        status = "[OK] OK" if result else "[ERROR] FEHLER"
        print(f"{check}: {status}")
    
    all_ok = all(results.values())
    
    print("\n" + "="*70)
    if all_ok:
        print("[OK] ALLE CHECKS ERFOLGREICH - IMPLEMENTATION VOLLSTÄNDIG")
    else:
        print("[ERROR] EINIGE CHECKS FEHLGESCHLAGEN - BITTE PRÜFEN")
    print("="*70)
    
    return all_ok


if __name__ == '__main__':
    success = run_verification()
    sys.exit(0 if success else 1)
