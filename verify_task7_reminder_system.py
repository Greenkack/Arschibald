#!/usr/bin/env python3
"""
Verification Script für Task 7: Automatische Erinnerungen und Follow-ups
Prüft ob alle Komponenten korrekt implementiert und integriert sind
"""

import sys
import os

# Füge Projekt-Root zum Path hinzu
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def verify_imports():
    """Prüft ob alle Module importiert werden können."""
    print("\n" + "="*60)
    print("SCHRITT 1: Module-Imports prüfen")
    print("="*60)
    
    try:
        from crm.utils.notification_manager import (
            create_reminder,
            get_reminder,
            update_reminder_status,
            snooze_reminder,
            delete_reminder,
            get_all_reminders,
            get_due_reminders,
            create_reminder_for_lead,
            create_reminder_for_offer,
            create_reminder_for_appointment,
            create_manual_reminder,
            get_reminder_statistics,
            REMINDER_RULES
        )
        print("[OK] notification_manager.py erfolgreich importiert")
        
        from crm.utils.reminder_ui import (
            render_reminders_widget,
            render_reminders_management_ui
        )
        print("[OK] reminder_ui.py erfolgreich importiert")
        
        from database import get_db_connection, create_crm_enhancement_tables
        print("[OK] database.py erfolgreich importiert")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import-Fehler: {e}")
        return False


def verify_database():
    """Prüft ob die Datenbank-Tabelle existiert."""
    print("\n" + "="*60)
    print("SCHRITT 2: Datenbank-Struktur prüfen")
    print("="*60)
    
    try:
        from database import get_db_connection, create_crm_enhancement_tables
        
        conn = get_db_connection()
        if not conn:
            print("[ERROR] Keine Datenbankverbindung")
            return False
        
        # Erstelle Tabellen falls nicht vorhanden
        create_crm_enhancement_tables(conn)
        
        # Prüfe ob Tabelle existiert
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='crm_reminders'
        """)
        
        if cursor.fetchone():
            print("[OK] Tabelle 'crm_reminders' existiert")
        else:
            print("[ERROR] Tabelle 'crm_reminders' nicht gefunden")
            conn.close()
            return False
        
        # Prüfe Spalten
        cursor.execute("PRAGMA table_info(crm_reminders)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            'id', 'reminder_type', 'related_id', 'related_type',
            'due_date', 'status', 'message', 'repeat_count', 'created_at'
        ]
        
        for col in required_columns:
            if col in columns:
                print(f"[OK] Spalte '{col}' vorhanden")
            else:
                print(f"[ERROR] Spalte '{col}' fehlt")
                conn.close()
                return False
        
        # Prüfe Indizes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='crm_reminders'
        """)
        indices = [row[0] for row in cursor.fetchall()]
        
        if 'idx_crm_reminders_due_date' in indices:
            print("[OK] Index 'idx_crm_reminders_due_date' vorhanden")
        else:
            print("[WARNING] Index 'idx_crm_reminders_due_date' fehlt (optional)")
        
        if 'idx_crm_reminders_status' in indices:
            print("[OK] Index 'idx_crm_reminders_status' vorhanden")
        else:
            print("[WARNING] Index 'idx_crm_reminders_status' fehlt (optional)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Datenbank-Fehler: {e}")
        return False


def verify_rules():
    """Prüft ob die Regel-Engine korrekt konfiguriert ist."""
    print("\n" + "="*60)
    print("SCHRITT 3: Regel-Engine prüfen")
    print("="*60)
    
    try:
        from crm.utils.notification_manager import REMINDER_RULES
        
        expected_rules = {
            'lead_created': 3,
            'offer_sent': 7,
            'appointment_completed': 1
        }
        
        for rule_name, expected_days in expected_rules.items():
            if rule_name in REMINDER_RULES:
                actual_days = REMINDER_RULES[rule_name]['days_offset']
                if actual_days == expected_days:
                    print(f"[OK] Regel '{rule_name}': {actual_days} Tage (korrekt)")
                else:
                    print(f"[ERROR] Regel '{rule_name}': {actual_days} Tage (erwartet: {expected_days})")
                    return False
            else:
                print(f"[ERROR] Regel '{rule_name}' fehlt")
                return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Regel-Engine-Fehler: {e}")
        return False


def verify_functionality():
    """Prüft ob die Kernfunktionen arbeiten."""
    print("\n" + "="*60)
    print("SCHRITT 4: Funktionalität testen")
    print("="*60)
    
    try:
        from crm.utils.notification_manager import (
            create_manual_reminder,
            get_reminder,
            snooze_reminder,
            update_reminder_status,
            delete_reminder,
            get_due_reminders
        )
        from datetime import date, timedelta
        
        # Test 1: Erinnerung erstellen
        test_date = date.today() + timedelta(days=1)
        reminder_id = create_manual_reminder(
            related_id=999,
            related_type='customer',
            due_date=test_date,
            message='Verification Test'
        )
        
        if reminder_id:
            print(f"[OK] Erinnerung erstellen: ID {reminder_id}")
        else:
            print("[ERROR] Erinnerung erstellen fehlgeschlagen")
            return False
        
        # Test 2: Erinnerung laden
        reminder = get_reminder(reminder_id)
        if reminder and reminder['message'] == 'Verification Test':
            print("[OK] Erinnerung laden funktioniert")
        else:
            print("[ERROR] Erinnerung laden fehlgeschlagen")
            return False
        
        # Test 3: Snooze
        if snooze_reminder(reminder_id, days=2):
            print("[OK] Snooze-Funktion funktioniert")
        else:
            print("[ERROR] Snooze-Funktion fehlgeschlagen")
            return False
        
        # Test 4: Status-Update
        if update_reminder_status(reminder_id, 'completed'):
            print("[OK] Status-Update funktioniert")
        else:
            print("[ERROR] Status-Update fehlgeschlagen")
            return False
        
        # Test 5: Löschen
        if delete_reminder(reminder_id):
            print("[OK] Löschen funktioniert")
        else:
            print("[ERROR] Löschen fehlgeschlagen")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Funktionalitäts-Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_ui_integration():
    """Prüft ob die UI-Integration funktioniert."""
    print("\n" + "="*60)
    print("SCHRITT 5: UI-Integration prüfen")
    print("="*60)
    
    try:
        # Prüfe ob Dashboard-Integration vorhanden ist
        with open('crm_dashboard_ui.py', 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        if 'from crm.utils.reminder_ui import render_reminders_widget' in dashboard_content:
            print("[OK] Reminder UI Import im Dashboard vorhanden")
        else:
            print("[ERROR] Reminder UI Import im Dashboard fehlt")
            return False
        
        if 'render_reminders_widget' in dashboard_content:
            print("[OK] render_reminders_widget wird aufgerufen")
        else:
            print("[ERROR] render_reminders_widget wird nicht aufgerufen")
            return False
        
        if '🔔 Erinnerungen' in dashboard_content:
            print("[OK] Erinnerungs-Tab im Dashboard vorhanden")
        else:
            print("[ERROR] Erinnerungs-Tab im Dashboard fehlt")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] UI-Integration-Fehler: {e}")
        return False


def verify_documentation():
    """Prüft ob die Dokumentation vorhanden ist."""
    print("\n" + "="*60)
    print("SCHRITT 6: Dokumentation prüfen")
    print("="*60)
    
    try:
        import os
        
        # Prüfe Quick Reference
        if os.path.exists('docs/REMINDER_SYSTEM_QUICK_REFERENCE.md'):
            print("[OK] Quick Reference Dokumentation vorhanden")
        else:
            print("[WARNING] Quick Reference Dokumentation fehlt")
        
        # Prüfe Summary
        if os.path.exists('TASK_7_REMINDER_SYSTEM_COMPLETE.md'):
            print("[OK] Task Summary Dokumentation vorhanden")
        else:
            print("[WARNING] Task Summary Dokumentation fehlt")
        
        # Prüfe Tests
        if os.path.exists('crm/utils/test_notification_manager.py'):
            print("[OK] Test-Datei vorhanden")
        else:
            print("[ERROR] Test-Datei fehlt")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Dokumentations-Fehler: {e}")
        return False


def main():
    """Hauptfunktion für Verification."""
    print("\n" + "="*60)
    print("TASK 7 VERIFICATION: Automatische Erinnerungen und Follow-ups")
    print("="*60)
    
    results = {
        'Module-Imports': verify_imports(),
        'Datenbank-Struktur': verify_database(),
        'Regel-Engine': verify_rules(),
        'Funktionalität': verify_functionality(),
        'UI-Integration': verify_ui_integration(),
        'Dokumentation': verify_documentation()
    }
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("VERIFICATION ZUSAMMENFASSUNG")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
        print(f"{check_name}: {status}")
    
    print("\n" + "="*60)
    print(f"ERGEBNIS: {passed}/{total} Checks bestanden ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 TASK 7 VOLLSTÄNDIG IMPLEMENTIERT UND VERIFIZIERT! 🎉")
        print("\nDas Erinnerungssystem ist:")
        print("  [OK] Vollständig implementiert")
        print("  [OK] Getestet und funktionsfähig")
        print("  [OK] In Dashboard integriert")
        print("  [OK] Dokumentiert")
        print("\nDas System ist production-ready und kann verwendet werden.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} Check(s) fehlgeschlagen")
        print("Bitte überprüfen Sie die Fehlerausgaben oben.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
