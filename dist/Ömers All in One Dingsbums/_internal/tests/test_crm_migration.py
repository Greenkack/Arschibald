#!/usr/bin/env python3
"""
Test-Skript für CRM-Erweiterungs-Migration (Task 1.1)

Testet die Erstellung der neuen Tabellen und Felder.
"""

import sqlite3
import sys
from database import get_db_connection, migrate_crm_enhancements, create_crm_enhancement_tables


def test_table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Prüft ob eine Tabelle existiert."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name))
    return cursor.fetchone() is not None


def test_column_exists(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    """Prüft ob eine Spalte in einer Tabelle existiert."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = {row[1] for row in cursor.fetchall()}
    return column_name in columns


def test_index_exists(conn: sqlite3.Connection, index_name: str) -> bool:
    """Prüft ob ein Index existiert."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND name=?
    """, (index_name))
    return cursor.fetchone() is not None


def run_tests():
    """Führt alle Tests für die CRM-Migration durch."""
    print("=" * 70)
    print("CRM-ERWEITERUNGS-MIGRATION TEST (Task 1.1)")
    print("=" * 70)
    print()
    
    # Test 1: Migration ausführen
    print("Test 1: Migration ausführen...")
    success = migrate_crm_enhancements()
    if not success:
        print("FEHLER: Migration fehlgeschlagen!")
        return False
    print("Migration erfolgreich durchgeführt")
    print()
    
    # Verbindung für Tests herstellen
    conn = get_db_connection()
    if not conn:
        print("FEHLER: Keine Datenbankverbindung!")
        return False
    
    try:
        # Test 2: Neue Tabellen prüfen
        print("Test 2: Neue Tabellen prüfen...")
        tables_to_check = [
            'project_calculations',
            'crm_tasks',
            'crm_activities',
            'crm_reminders'
        ]
        
        all_tables_exist = True
        for table in tables_to_check:
            exists = test_table_exists(conn, table)
            status = "" if exists else ""
            print(f"  {status} Tabelle '{table}': {'existiert' if exists else 'FEHLT'}")
            if not exists:
                all_tables_exist = False
        
        if not all_tables_exist:
            print("FEHLER: Nicht alle Tabellen wurden erstellt!")
            return False
        print()
        
        # Test 3: Neue Spalten in projects Tabelle prüfen
        print("Test 3: Neue Spalten in 'projects' Tabelle prüfen...")
        columns_to_check = [
            'offer_status',
            'offer_sent_date',
            'offer_version',
            'offer_value',
            'offer_accepted_date',
            'rejection_reason'
        ]
        
        all_columns_exist = True
        for column in columns_to_check:
            exists = test_column_exists(conn, 'projects', column)
            status = "" if exists else ""
            print(f"  {status} Spalte '{column}': {'existiert' if exists else 'FEHLT'}")
            if not exists:
                all_columns_exist = False
        
        if not all_columns_exist:
            print("FEHLER: Nicht alle Spalten wurden hinzugefügt!")
            return False
        print()
        
        # Test 4: Indizes prüfen
        print("Test 4: Performance-Indizes prüfen...")
        indices_to_check = [
            'idx_project_calculations_project_id',
            'idx_crm_tasks_customer_id',
            'idx_crm_tasks_status',
            'idx_crm_activities_customer_id',
            'idx_crm_reminders_due_date',
            'idx_projects_offer_status'
        ]
        
        all_indices_exist = True
        for index in indices_to_check:
            exists = test_index_exists(conn, index)
            status = "" if exists else ""
            print(f"  {status} Index '{index}': {'existiert' if exists else 'FEHLT'}")
            if not exists:
                all_indices_exist = False
        
        if not all_indices_exist:
            print("WARNUNG: Nicht alle Indizes wurden erstellt (nicht kritisch)")
        print()
        
        # Test 5: Tabellen-Schema prüfen
        print("Test 5: Tabellen-Schema Details prüfen...")
        
        # project_calculations Schema
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(project_calculations)")
        calc_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_calc_columns = {
            'id': 'INTEGER',
            'project_id': 'INTEGER',
            'version': 'INTEGER',
            'calculation_data': 'TEXT',
            'dynamic_keys': 'TEXT',
            'is_main_offer': 'BOOLEAN',
            'archived': 'BOOLEAN',
            'created_at': 'TIMESTAMP'
        }
        
        schema_ok = True
        for col, expected_type in required_calc_columns.items():
            if col not in calc_columns:
                print(f"  Spalte '{col}' fehlt in project_calculations")
                schema_ok = False
            else:
                print(f"  Spalte '{col}' ({calc_columns[col]}) vorhanden")
        
        if not schema_ok:
            print("FEHLER: Schema von project_calculations ist unvollständig!")
            return False
        print()
        
        # Test 6: Foreign Key Constraints prüfen
        print("Test 6: Foreign Key Constraints prüfen...")
        cursor.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        if fk_enabled:
            print("  Foreign Keys sind aktiviert")
        else:
            print("  WARNUNG: Foreign Keys sind nicht aktiviert")
        print()
        
        # Test 7: Test-Daten einfügen und wieder löschen
        print("Test 7: Test-Daten einfügen und löschen...")
        try:
            # Test-Erinnerung einfügen
            cursor.execute("""
                INSERT INTO crm_reminders (reminder_type, related_id, related_type, due_date, message)
                VALUES ('test', 1, 'test_type', datetime('now'), 'Test-Erinnerung')
            """)
            reminder_id = cursor.lastrowid
            print(f"  Test-Erinnerung eingefügt (ID: {reminder_id})")
            
            # Test-Erinnerung wieder löschen
            cursor.execute("DELETE FROM crm_reminders WHERE id = ?", (reminder_id))
            conn.commit()
            print("  Test-Erinnerung gelöscht")
            
        except Exception as e:
            print(f"  FEHLER beim Einfügen/Löschen von Test-Daten: {e}")
            return False
        print()
        
        # Alle Tests bestanden
        print("=" * 70)
        print("ALLE TESTS BESTANDEN!")
        print("=" * 70)
        print()
        print("Die CRM-Erweiterungstabellen wurden erfolgreich erstellt:")
        print("  • project_calculations (Berechnungsversionierung)")
        print("  • crm_tasks (Aufgabenverwaltung)")
        print("  • crm_activities (Notizen und Historie)")
        print("  • crm_reminders (Automatische Erinnerungen)")
        print("  • projects Tabelle erweitert (Angebots-Felder)")
        print()
        print("Task 1.1 ist abgeschlossen! ")
        print()
        
        return True
        
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nKRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
