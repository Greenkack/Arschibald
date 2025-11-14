# crm/utils/test_notification_manager.py
"""
Unit Tests für Notification Manager
Testet Regel-Engine, automatische Erinnerungs-Erstellung und Snooze-Funktion

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
"""

import sys
import os
from datetime import date, timedelta

# Füge Projekt-Root zum Path hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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
        is_reminder_overdue,
        format_reminder_for_display,
        REMINDER_RULES
    )
    from database import get_db_connection, create_crm_enhancement_tables
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"FEHLER: Konnte Module nicht importieren: {e}")
    IMPORTS_SUCCESSFUL = False


def setup_test_database():
    """Initialisiert Test-Datenbank mit CRM-Tabellen."""
    if not IMPORTS_SUCCESSFUL:
        return False
    
    try:
        conn = get_db_connection()
        if not conn:
            print("FEHLER: Keine Datenbankverbindung")
            return False
        
        # Erstelle CRM-Tabellen
        create_crm_enhancement_tables(conn)
        conn.close()
        
        print("[OK] Test-Datenbank initialisiert")
        return True
    except Exception as e:
        print(f"FEHLER beim Setup: {e}")
        return False


def test_reminder_rules():
    """Test 1: Regel-Definitionen prüfen"""
    print("\n" + "="*60)
    print("TEST 1: Regel-Definitionen")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("[ERROR] ÜBERSPRUNGEN: Imports fehlgeschlagen")
        return False
    
    try:
        # Prüfe ob alle erwarteten Regeln existieren
        expected_rules = ['lead_created', 'offer_sent', 'appointment_completed']
        
        for rule_name in expected_rules:
            assert rule_name in REMINDER_RULES, f"Regel '{rule_name}' fehlt"
            
            rule = REMINDER_RULES[rule_name]
            assert 'days_offset' in rule, f"Regel '{rule_name}' hat kein 'days_offset'"
            assert 'message_template' in rule, f"Regel '{rule_name}' hat kein 'message_template'"
            assert 'description' in rule, f"Regel '{rule_name}' hat keine 'description'"
            
            print(f"[OK] Regel '{rule_name}': {rule['description']}")
            print(f"   → Follow-up nach {rule['days_offset']} Tagen")
        
        # Prüfe spezifische Werte
        assert REMINDER_RULES['lead_created']['days_offset'] == 3, "Lead Follow-up sollte nach 3 Tagen sein"
        assert REMINDER_RULES['offer_sent']['days_offset'] == 7, "Angebots Follow-up sollte nach 7 Tagen sein"
        assert REMINDER_RULES['appointment_completed']['days_offset'] == 1, "Termin Follow-up sollte nach 1 Tag sein"
        
        print("\n[OK] TEST 1 BESTANDEN: Alle Regeln korrekt definiert")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST 1 FEHLGESCHLAGEN: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] TEST 1 FEHLER: {e}")
        return False


def test_create_reminder():
    """Test 2: Erinnerung erstellen"""
    print("\n" + "="*60)
    print("TEST 2: Erinnerung erstellen")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("[ERROR] ÜBERSPRUNGEN: Imports fehlgeschlagen")
        return False
    
    try:
        # Test: Manuelle Erinnerung erstellen
        test_date = date.today() + timedelta(days=5)
        reminder_id = create_reminder(
            reminder_type='manual',
            related_id=1,
            related_type='customer',
            due_date=test_date,
            message='Test-Erinnerung',
            auto_calculate_date=False
        )
        
        assert reminder_id is not None, "Erinnerung konnte nicht erstellt werden"
        assert isinstance(reminder_id, int), "Reminder-ID sollte Integer sein"
        
        print(f"[OK] Erinnerung #{reminder_id} erstellt")
        
        # Test: Erinnerung laden
        reminder = get_reminder(reminder_id)
        assert reminder is not None, "Erinnerung konnte nicht geladen werden"
        assert reminder['id'] == reminder_id, "Falsche Erinnerungs-ID"
        assert reminder['reminder_type'] == 'manual', "Falscher Typ"
        assert reminder['related_id'] == 1, "Falsche related_id"
        assert reminder['related_type'] == 'customer', "Falscher related_type"
        assert reminder['message'] == 'Test-Erinnerung', "Falsche Nachricht"
        assert reminder['status'] == 'pending', "Falscher Status"
        
        print(f"[OK] Erinnerung korrekt geladen: {reminder['message']}")
        
        # Cleanup
        delete_reminder(reminder_id)
        
        print("\n[OK] TEST 2 BESTANDEN: Erinnerung erstellen und laden funktioniert")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST 2 FEHLGESCHLAGEN: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] TEST 2 FEHLER: {e}")
        return False


def test_automatic_reminder_creation():
    """Test 3: Automatische Erinnerungs-Erstellung mit Regeln"""
    print("\n" + "="*60)
    print("TEST 3: Automatische Erinnerungs-Erstellung")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("[ERROR] ÜBERSPRUNGEN: Imports fehlgeschlagen")
        return False
    
    try:
        # Test: Lead Follow-up (3 Tage)
        lead_id = create_reminder_for_lead(lead_id=1, lead_name="Test Lead")
        assert lead_id is not None, "Lead-Erinnerung konnte nicht erstellt werden"
        
        lead_reminder = get_reminder(lead_id)
        assert lead_reminder is not None, "Lead-Erinnerung konnte nicht geladen werden"
        
        # Prüfe Datum (sollte heute + 3 Tage sein)
        expected_date = (date.today() + timedelta(days=3)).isoformat()
        assert lead_reminder['due_date'] == expected_date, f"Falsches Datum: {lead_reminder['due_date']} != {expected_date}"
        assert lead_reminder['reminder_type'] == 'lead_created', "Falscher Typ"
        
        print(f"[OK] Lead Follow-up erstellt: Fällig am {lead_reminder['due_date']}")
        
        # Test: Angebots Follow-up (7 Tage)
        offer_id = create_reminder_for_offer(project_id=1, project_name="Test Projekt")
        assert offer_id is not None, "Angebots-Erinnerung konnte nicht erstellt werden"
        
        offer_reminder = get_reminder(offer_id)
        assert offer_reminder is not None, "Angebots-Erinnerung konnte nicht geladen werden"
        
        # Prüfe Datum (sollte heute + 7 Tage sein)
        expected_date = (date.today() + timedelta(days=7)).isoformat()
        assert offer_reminder['due_date'] == expected_date, f"Falsches Datum: {offer_reminder['due_date']} != {expected_date}"
        assert offer_reminder['reminder_type'] == 'offer_sent', "Falscher Typ"
        
        print(f"[OK] Angebots Follow-up erstellt: Fällig am {offer_reminder['due_date']}")
        
        # Test: Termin Follow-up (1 Tag)
        appointment_id = create_reminder_for_appointment(appointment_id=1, appointment_title="Test Termin")
        assert appointment_id is not None, "Termin-Erinnerung konnte nicht erstellt werden"
        
        appointment_reminder = get_reminder(appointment_id)
        assert appointment_reminder is not None, "Termin-Erinnerung konnte nicht geladen werden"
        
        # Prüfe Datum (sollte heute + 1 Tag sein)
        expected_date = (date.today() + timedelta(days=1)).isoformat()
        assert appointment_reminder['due_date'] == expected_date, f"Falsches Datum: {appointment_reminder['due_date']} != {expected_date}"
        assert appointment_reminder['reminder_type'] == 'appointment_completed', "Falscher Typ"
        
        print(f"[OK] Termin Follow-up erstellt: Fällig am {appointment_reminder['due_date']}")
        
        # Cleanup
        delete_reminder(lead_id)
        delete_reminder(offer_id)
        delete_reminder(appointment_id)
        
        print("\n[OK] TEST 3 BESTANDEN: Automatische Erinnerungs-Erstellung funktioniert")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST 3 FEHLGESCHLAGEN: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] TEST 3 FEHLER: {e}")
        return False


def test_snooze_function():
    """Test 4: Snooze-Funktion"""
    print("\n" + "="*60)
    print("TEST 4: Snooze-Funktion")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("[ERROR] ÜBERSPRUNGEN: Imports fehlgeschlagen")
        return False
    
    try:
        # Erstelle Test-Erinnerung
        original_date = date.today()
        reminder_id = create_reminder(
            reminder_type='manual',
            related_id=1,
            related_type='customer',
            due_date=original_date,
            message='Snooze Test',
            auto_calculate_date=False
        )
        
        assert reminder_id is not None, "Test-Erinnerung konnte nicht erstellt werden"
        
        # Lade Original
        original_reminder = get_reminder(reminder_id)
        assert original_reminder['due_date'] == original_date.isoformat(), "Falsches Original-Datum"
        assert original_reminder['repeat_count'] == 0, "Repeat-Count sollte 0 sein"
        
        print(f"[OK] Original-Erinnerung: Fällig am {original_reminder['due_date']}")
        
        # Snooze um 2 Tage
        success = snooze_reminder(reminder_id, days=2)
        assert success, "Snooze fehlgeschlagen"
        
        # Lade nach Snooze
        snoozed_reminder = get_reminder(reminder_id)
        expected_date = (original_date + timedelta(days=2)).isoformat()
        
        assert snoozed_reminder['due_date'] == expected_date, f"Falsches Snooze-Datum: {snoozed_reminder['due_date']} != {expected_date}"
        assert snoozed_reminder['status'] == 'snoozed', "Status sollte 'snoozed' sein"
        assert snoozed_reminder['repeat_count'] == 1, "Repeat-Count sollte 1 sein"
        
        print(f"[OK] Nach Snooze: Fällig am {snoozed_reminder['due_date']}, Repeat-Count: {snoozed_reminder['repeat_count']}")
        
        # Snooze nochmal um 3 Tage
        success = snooze_reminder(reminder_id, days=3)
        assert success, "Zweites Snooze fehlgeschlagen"
        
        # Lade nach zweitem Snooze
        snoozed_again = get_reminder(reminder_id)
        expected_date = (original_date + timedelta(days=5)).isoformat()  # 2 + 3 Tage
        
        assert snoozed_again['due_date'] == expected_date, f"Falsches zweites Snooze-Datum"
        assert snoozed_again['repeat_count'] == 2, "Repeat-Count sollte 2 sein"
        
        print(f"[OK] Nach zweitem Snooze: Fällig am {snoozed_again['due_date']}, Repeat-Count: {snoozed_again['repeat_count']}")
        
        # Cleanup
        delete_reminder(reminder_id)
        
        print("\n[OK] TEST 4 BESTANDEN: Snooze-Funktion funktioniert korrekt")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST 4 FEHLGESCHLAGEN: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] TEST 4 FEHLER: {e}")
        return False


def test_status_updates():
    """Test 5: Status-Updates"""
    print("\n" + "="*60)
    print("TEST 5: Status-Updates")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("[ERROR] ÜBERSPRUNGEN: Imports fehlgeschlagen")
        return False
    
    try:
        # Erstelle Test-Erinnerung
        reminder_id = create_reminder(
            reminder_type='manual',
            related_id=1,
            related_type='customer',
            due_date=date.today(),
            message='Status Test',
            auto_calculate_date=False
        )
        
        assert reminder_id is not None, "Test-Erinnerung konnte nicht erstellt werden"
        
        # Test: Status auf 'completed' setzen
        success = update_reminder_status(reminder_id, 'completed')
        assert success, "Status-Update auf 'completed' fehlgeschlagen"
        
        reminder = get_reminder(reminder_id)
        assert reminder['status'] == 'completed', "Status sollte 'completed' sein"
        print("[OK] Status auf 'completed' gesetzt")
        
        # Test: Status auf 'dismissed' setzen
        success = update_reminder_status(reminder_id, 'dismissed')
        assert success, "Status-Update auf 'dismissed' fehlgeschlagen"
        
        reminder = get_reminder(reminder_id)
        assert reminder['status'] == 'dismissed', "Status sollte 'dismissed' sein"
        print("[OK] Status auf 'dismissed' gesetzt")
        
        # Test: Ungültiger Status
        success = update_reminder_status(reminder_id, 'invalid_status')
        assert not success, "Ungültiger Status sollte abgelehnt werden"
        print("[OK] Ungültiger Status korrekt abgelehnt")
        
        # Cleanup
        delete_reminder(reminder_id)
        
        print("\n[OK] TEST 5 BESTANDEN: Status-Updates funktionieren")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST 5 FEHLGESCHLAGEN: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] TEST 5 FEHLER: {e}")
        return False


def test_due_reminders():
    """Test 6: Fällige Erinnerungen abrufen"""
    print("\n" + "="*60)
    print("TEST 6: Fällige Erinnerungen")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("[ERROR] ÜBERSPRUNGEN: Imports fehlgeschlagen")
        return False
    
    try:
        # Erstelle verschiedene Erinnerungen
        # 1. Überfällig (gestern)
        overdue_id = create_reminder(
            reminder_type='manual',
            related_id=1,
            related_type='customer',
            due_date=date.today() - timedelta(days=1),
            message='Überfällig',
            auto_calculate_date=False
        )
        
        # 2. Heute fällig
        today_id = create_reminder(
            reminder_type='manual',
            related_id=2,
            related_type='customer',
            due_date=date.today(),
            message='Heute fällig',
            auto_calculate_date=False
        )
        
        # 3. Morgen fällig (sollte NICHT in due_reminders sein)
        tomorrow_id = create_reminder(
            reminder_type='manual',
            related_id=3,
            related_type='customer',
            due_date=date.today() + timedelta(days=1),
            message='Morgen fällig',
            auto_calculate_date=False
        )
        
        # 4. Bereits erledigt (sollte NICHT in due_reminders sein)
        completed_id = create_reminder(
            reminder_type='manual',
            related_id=4,
            related_type='customer',
            due_date=date.today(),
            message='Erledigt',
            auto_calculate_date=False
        )
        update_reminder_status(completed_id, 'completed')
        
        # Lade fällige Erinnerungen
        due_reminders = get_due_reminders()
        
        # Prüfe Ergebnisse
        due_ids = [r['id'] for r in due_reminders]
        
        assert overdue_id in due_ids, "Überfällige Erinnerung sollte in due_reminders sein"
        assert today_id in due_ids, "Heute fällige Erinnerung sollte in due_reminders sein"
        assert tomorrow_id not in due_ids, "Morgen fällige Erinnerung sollte NICHT in due_reminders sein"
        assert completed_id not in due_ids, "Erledigte Erinnerung sollte NICHT in due_reminders sein"
        
        print(f"[OK] {len(due_reminders)} fällige Erinnerungen gefunden")
        print(f"   → Überfällig: [OK]")
        print(f"   → Heute: [OK]")
        print(f"   → Morgen: korrekt ausgeschlossen")
        print(f"   → Erledigt: korrekt ausgeschlossen")
        
        # Cleanup
        delete_reminder(overdue_id)
        delete_reminder(today_id)
        delete_reminder(tomorrow_id)
        delete_reminder(completed_id)
        
        print("\n[OK] TEST 6 BESTANDEN: Fällige Erinnerungen werden korrekt gefiltert")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST 6 FEHLGESCHLAGEN: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] TEST 6 FEHLER: {e}")
        return False


def test_statistics():
    """Test 7: Statistiken"""
    print("\n" + "="*60)
    print("TEST 7: Statistiken")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("[ERROR] ÜBERSPRUNGEN: Imports fehlgeschlagen")
        return False
    
    try:
        # Erstelle Test-Erinnerungen
        ids = []
        
        # 2x pending
        ids.append(create_reminder('manual', 1, 'customer', date.today(), 'Test 1', False))
        ids.append(create_reminder('manual', 2, 'customer', date.today(), 'Test 2', False))
        
        # 1x completed
        completed_id = create_reminder('manual', 3, 'customer', date.today(), 'Test 3', False)
        update_reminder_status(completed_id, 'completed')
        ids.append(completed_id)
        
        # 1x snoozed
        snoozed_id = create_reminder('manual', 4, 'customer', date.today(), 'Test 4', False)
        snooze_reminder(snoozed_id)
        ids.append(snoozed_id)
        
        # Lade Statistiken
        stats = get_reminder_statistics()
        
        assert 'total' in stats, "Statistiken sollten 'total' enthalten"
        assert 'by_status' in stats, "Statistiken sollten 'by_status' enthalten"
        assert 'due' in stats, "Statistiken sollten 'due' enthalten"
        
        print(f"[OK] Statistiken geladen:")
        print(f"   → Gesamt: {stats['total']}")
        print(f"   → Nach Status: {stats['by_status']}")
        print(f"   → Fällig: {stats['due']}")
        
        # Cleanup
        for reminder_id in ids:
            if reminder_id:
                delete_reminder(reminder_id)
        
        print("\n[OK] TEST 7 BESTANDEN: Statistiken funktionieren")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST 7 FEHLGESCHLAGEN: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] TEST 7 FEHLER: {e}")
        return False


def test_display_formatting():
    """Test 8: Display-Formatierung"""
    print("\n" + "="*60)
    print("TEST 8: Display-Formatierung")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("[ERROR] ÜBERSPRUNGEN: Imports fehlgeschlagen")
        return False
    
    try:
        # Erstelle Test-Erinnerung
        reminder_id = create_reminder(
            reminder_type='lead_created',
            related_id=1,
            related_type='lead',
            due_date=date.today(),
            message='Test Lead Follow-up',
            auto_calculate_date=False
        )
        
        reminder = get_reminder(reminder_id)
        display_reminder = format_reminder_for_display(reminder)
        
        # Prüfe zusätzliche Felder
        assert 'is_overdue' in display_reminder, "Sollte 'is_overdue' enthalten"
        assert 'display_color' in display_reminder, "Sollte 'display_color' enthalten"
        assert 'status_label' in display_reminder, "Sollte 'status_label' enthalten"
        assert 'type_label' in display_reminder, "Sollte 'type_label' enthalten"
        assert 'due_date_label' in display_reminder, "Sollte 'due_date_label' enthalten"
        
        print(f"[OK] Display-Formatierung:")
        print(f"   → Status: {display_reminder['status_label']}")
        print(f"   → Typ: {display_reminder['type_label']}")
        print(f"   → Fälligkeit: {display_reminder['due_date_label']}")
        print(f"   → Farbe: {display_reminder['display_color']}")
        print(f"   → Überfällig: {display_reminder['is_overdue']}")
        
        # Cleanup
        delete_reminder(reminder_id)
        
        print("\n[OK] TEST 8 BESTANDEN: Display-Formatierung funktioniert")
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST 8 FEHLGESCHLAGEN: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] TEST 8 FEHLER: {e}")
        return False


def run_all_tests():
    """Führt alle Tests aus und gibt Zusammenfassung aus."""
    print("\n" + "="*60)
    print("NOTIFICATION MANAGER - TEST SUITE")
    print("="*60)
    
    if not IMPORTS_SUCCESSFUL:
        print("\n[ERROR] KRITISCHER FEHLER: Module konnten nicht importiert werden")
        print("Bitte stellen Sie sicher, dass alle Abhängigkeiten installiert sind.")
        return
    
    # Setup
    if not setup_test_database():
        print("\n[ERROR] KRITISCHER FEHLER: Datenbank-Setup fehlgeschlagen")
        return
    
    # Führe Tests aus
    results = {
        'Regel-Definitionen': test_reminder_rules(),
        'Erinnerung erstellen': test_create_reminder(),
        'Automatische Erstellung': test_automatic_reminder_creation(),
        'Snooze-Funktion': test_snooze_function(),
        'Status-Updates': test_status_updates(),
        'Fällige Erinnerungen': test_due_reminders(),
        'Statistiken': test_statistics(),
        'Display-Formatierung': test_display_formatting()
    }
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("TEST-ZUSAMMENFASSUNG")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
        print(f"{test_name}: {status}")
    
    print("\n" + "="*60)
    print(f"ERGEBNIS: {passed}/{total} Tests bestanden ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALLE TESTS BESTANDEN! 🎉")
        print("Das Notification Manager Modul funktioniert korrekt.")
    else:
        print(f"\n[WARNING] {total - passed} Test(s) fehlgeschlagen")
        print("Bitte überprüfen Sie die Fehlerausgaben oben.")


if __name__ == "__main__":
    run_all_tests()
