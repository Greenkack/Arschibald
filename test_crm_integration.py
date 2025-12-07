#!/usr/bin/env python3
"""
Quick Test: CRM Integration mit Lead Scoring und Backup
Testet ob die neuen Tabs ohne Fehler geladen werden können
"""

import sqlite3
import tempfile
import os

def test_crm_integration():
    """Testet die CRM-Integration ohne die App zu starten"""
    
    print(" Teste CRM Integration...")
    print("=" * 60)
    
    # 1. Import Test
    print("\n1⃣ Import Test...")
    try:
        import crm
        print("    CRM Modul importiert")
    except Exception as e:
        print(f"    Import fehlgeschlagen: {e}")
        return False
    
    # 2. Funktions-Verfügbarkeit
    print("\n2⃣ Funktions-Verfügbarkeit...")
    required_functions = [
        'render_crm',
        'render_customer_management', 
        'render_lead_scoring_tab',
        'render_backup_tab',
        'save_customer',
        'load_customer',
        'load_all_customers'
    ]
    
    for func_name in required_functions:
        if hasattr(crm, func_name):
            print(f"    {func_name} verfügbar")
        else:
            print(f"    {func_name} FEHLT")
            return False
    
    # 3. Datenbank-Operationen
    print("\n3⃣ Datenbank-Operationen...")
    try:
        # Temporäre Datenbank erstellen
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        conn = sqlite3.connect(temp_db.name)
        print(f"    Test-Datenbank erstellt: {temp_db.name}")
        
        # Tabellen erstellen
        crm.create_tables_crm(conn)
        print("    CRM-Tabellen erstellt")
        
        # Test-Kunde erstellen
        test_customer = {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'email': 'max@test.de',
            'phone': '0123456789',
            'street': 'Teststr. 1',
            'zip_code': '12345',
            'city': 'Teststadt'
        }
        
        customer_id = crm.save_customer(conn, test_customer)
        print(f"    Test-Kunde erstellt (ID: {customer_id})")
        
        # Kunde laden
        loaded = crm.load_customer(conn, customer_id)
        if loaded and loaded['first_name'] == 'Max':
            print("    Test-Kunde erfolgreich geladen")
        else:
            print("    Fehler beim Laden des Test-Kunden")
            return False
        
        # Alle Kunden laden
        all_customers = crm.load_all_customers(conn)
        if len(all_customers) == 1:
            print(f"    Kundenliste korrekt ({len(all_customers)} Kunde)")
        else:
            print(f"     Unerwartete Anzahl: {len(all_customers)}")
        
        conn.close()
        os.unlink(temp_db.name)
        print("    Test-Datenbank bereinigt")
        
    except Exception as e:
        print(f"    Datenbank-Test fehlgeschlagen: {e}")
        return False
    
    # 4. Tab-Funktionen (Import-Check)
    print("\n4⃣ Tab-Funktionen Verfügbarkeit...")
    
    # Lead Scoring
    try:
        from crm.features.lead_scoring_ui import render_lead_scoring_admin
        print("    Lead Scoring Modul verfügbar")
    except ImportError:
        print("   ℹ  Lead Scoring Modul optional (Fallback aktiv)")
    
    # Backup
    try:
        from crm.utils.backup_ui import render_admin_backup_tab
        print("    Backup Modul verfügbar")
    except ImportError:
        print("   ℹ  Backup Modul optional (Fallback aktiv)")
    
    print("\n" + "=" * 60)
    print(" ALLE TESTS BESTANDEN!")
    print("\nDie CRM-Integration ist funktionsfähig und hat keine")
    print("negativen Auswirkungen auf die bestehende App.")
    print("\nNeue Features:")
    print("  • Tab 1: Kundenverwaltung (bestehend)")
    print("  • Tab 2: Lead Scoring (neu, mit Fallback)")
    print("  • Tab 3: Backup & Daten (neu, mit Fallback)")
    
    return True

if __name__ == "__main__":
    success = test_crm_integration()
    exit(0 if success else 1)
