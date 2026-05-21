#!/usr/bin/env python
"""
Verification Script für Import/Export-System

Prüft, ob alle Komponenten korrekt installiert und funktionsfähig sind.

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import sys
import os
from typing import List, Tuple


def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """Prüft, ob eine Datei existiert."""
    if os.path.exists(filepath):
        return True, f"{filepath}"
    else:
        return False, f"{filepath} - FEHLT"


def check_import(module_name: str) -> Tuple[bool, str]:
    """Prüft, ob ein Modul importiert werden kann."""
    try:
        __import__(module_name)
        return True, f"{module_name}"
    except ImportError as e:
        return False, f"{module_name} - FEHLER: {str(e)}"


def check_function_exists(module_name: str, function_name: str) -> Tuple[bool, str]:
    """Prüft, ob eine Funktion in einem Modul existiert."""
    try:
        module = __import__(module_name, fromlist=[function_name])
        if hasattr(module, function_name):
            return True, f"{module_name}.{function_name}"
        else:
            return False, f"{module_name}.{function_name} - FEHLT"
    except Exception as e:
        return False, f"{module_name}.{function_name} - FEHLER: {str(e)}"


def run_verification():
    """Führt vollständige Verifikation durch."""
    
    print("=" * 70)
    print("Import/Export-System Verifikation")
    print("=" * 70)
    print()
    
    all_checks_passed = True
    
    # 1. Datei-Existenz prüfen
    print("1. Datei-Existenz prüfen")
    print("-" * 70)
    
    files_to_check = [
        "crm/utils/import_export_manager.py",
        "crm/utils/import_export_ui.py",
        "crm/utils/test_import_export_manager.py",
        "crm/utils/IMPORT_EXPORT_REFERENCE.md",
        "crm/utils/IMPORT_EXPORT_INTEGRATION_GUIDE.md",
        "docs/IMPORT_EXPORT_QUICK_REFERENCE.md",
        "TASK_13_IMPORT_EXPORT_COMPLETE.md",
    ]
    
    for filepath in files_to_check:
        success, message = check_file_exists(filepath)
        print(message)
        if not success:
            all_checks_passed = False
    
    print()
    
    # 2. Abhängigkeiten prüfen
    print("2. Abhängigkeiten prüfen")
    print("-" * 70)
    
    dependencies = [
        "csv",
        "io",
        "sqlite3",
        "datetime",
        "typing",
        "pandas",
        "openpyxl",
        "streamlit",
    ]
    
    for dep in dependencies:
        success, message = check_import(dep)
        print(message)
        if not success:
            all_checks_passed = False
    
    print()
    
    # 3. Module prüfen
    print("3. Module prüfen")
    print("-" * 70)
    
    modules = [
        "crm.utils.import_export_manager",
        "crm.utils.import_export_ui",
    ]
    
    for module in modules:
        success, message = check_import(module)
        print(message)
        if not success:
            all_checks_passed = False
    
    print()
    
    # 4. Funktionen prüfen
    print("4. Funktionen prüfen")
    print("-" * 70)
    
    functions_to_check = [
        ("crm.utils.import_export_manager", "export_customers_to_csv"),
        ("crm.utils.import_export_manager", "export_customers_to_excel"),
        ("crm.utils.import_export_manager", "get_export_statistics"),
        ("crm.utils.import_export_manager", "parse_csv_for_import"),
        ("crm.utils.import_export_manager", "parse_excel_for_import"),
        ("crm.utils.import_export_manager", "map_import_fields"),
        ("crm.utils.import_export_manager", "check_duplicate_customer"),
        ("crm.utils.import_export_manager", "validate_customer_data"),
        ("crm.utils.import_export_manager", "import_customer"),
        ("crm.utils.import_export_manager", "import_customers_batch"),
        ("crm.utils.import_export_ui", "render_import_export_ui"),
    ]
    
    for module_name, function_name in functions_to_check:
        success, message = check_function_exists(module_name, function_name)
        print(message)
        if not success:
            all_checks_passed = False
    
    print()
    
    # 5. Tests prüfen
    print("5. Tests prüfen")
    print("-" * 70)
    
    try:
        import pytest
        print("pytest installiert")
        
        # Versuche Tests zu laden
        test_file = "crm/utils/test_import_export_manager.py"
        if os.path.exists(test_file):
            print(f"Test-Datei gefunden: {test_file}")
            print("   Führen Sie Tests aus mit: pytest crm/utils/test_import_export_manager.py -v")
        else:
            print(f"Test-Datei nicht gefunden: {test_file}")
            all_checks_passed = False
    except ImportError:
        print("pytest nicht installiert")
        print("   Installieren Sie mit: pip install pytest")
        all_checks_passed = False
    
    print()
    
    # 6. Datenbank-Verbindung prüfen
    print("6. Datenbank-Verbindung prüfen")
    print("-" * 70)
    
    try:
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            print("Datenbankverbindung erfolgreich")
            
            # Prüfe customers-Tabelle
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
            if cursor.fetchone():
                print("customers-Tabelle existiert")
            else:
                print("customers-Tabelle existiert nicht")
                all_checks_passed = False
            
            conn.close()
        else:
            print("Datenbankverbindung fehlgeschlagen")
            all_checks_passed = False
    except Exception as e:
        print(f"Fehler bei Datenbankverbindung: {str(e)}")
        all_checks_passed = False
    
    print()
    
    # Zusammenfassung
    print("=" * 70)
    if all_checks_passed:
        print("ALLE PRÜFUNGEN BESTANDEN")
        print()
        print("Das Import/Export-System ist vollständig installiert und einsatzbereit!")
        print()
        print("Nächste Schritte:")
        print("1. Tests ausführen: pytest crm/utils/test_import_export_manager.py -v")
        print("2. Integration in Admin-Panel (siehe IMPORT_EXPORT_INTEGRATION_GUIDE.md)")
        print("3. Dokumentation lesen (siehe IMPORT_EXPORT_QUICK_REFERENCE.md)")
        return 0
    else:
        print("EINIGE PRÜFUNGEN FEHLGESCHLAGEN")
        print()
        print("Bitte beheben Sie die oben genannten Fehler.")
        return 1


if __name__ == "__main__":
    sys.exit(run_verification())
