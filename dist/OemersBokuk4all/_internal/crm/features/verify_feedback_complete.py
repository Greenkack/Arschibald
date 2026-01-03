# crm/features/verify_feedback_complete.py
"""
Verifiziert die vollständige Implementierung des Feedback-Systems

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import sqlite3
import sys
from pathlib import Path


def verify_modules():
    """Prüft ob alle Module importierbar sind."""
    print(" Prüfe Module...")
    
    try:
        from crm.features import feedback_manager
        print("   feedback_manager importiert")
    except ImportError as e:
        print(f"   feedback_manager Import fehlgeschlagen: {e}")
        return False
    
    try:
        from crm.features import feedback_ui
        print("   feedback_ui importiert")
    except ImportError as e:
        print(f"   feedback_ui Import fehlgeschlagen: {e}")
        return False
    
    return True


def verify_database_tables():
    """Prüft ob Datenbank-Tabellen erstellt werden können."""
    print("\n Prüfe Datenbank-Tabellen...")
    
    try:
        from crm.features import feedback_manager
        
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        
        feedback_manager.create_feedback_tables(conn)
        
        cursor = conn.cursor()
        
        # Prüfe feedback_surveys
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback_surveys'")
        if cursor.fetchone():
            print("   Tabelle 'feedback_surveys' erstellt")
        else:
            print("   Tabelle 'feedback_surveys' fehlt")
            return False
        
        # Prüfe feedback_responses
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback_responses'")
        if cursor.fetchone():
            print("   Tabelle 'feedback_responses' erstellt")
        else:
            print("   Tabelle 'feedback_responses' fehlt")
            return False
        
        # Prüfe feedback_triggers
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback_triggers'")
        if cursor.fetchone():
            print("   Tabelle 'feedback_triggers' erstellt")
        else:
            print("   Tabelle 'feedback_triggers' fehlt")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   Fehler beim Erstellen der Tabellen: {e}")
        return False


def verify_crud_operations():
    """Prüft CRUD-Operationen."""
    print("\n Prüfe CRUD-Operationen...")
    
    try:
        from crm.features import feedback_manager
        
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        
        feedback_manager.create_feedback_tables(conn)
        
        # Mock-Tabellen
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT)")
        cursor.execute("CREATE TABLE projects (id INTEGER PRIMARY KEY, customer_id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO customers VALUES (1, 'Max', 'Mustermann', 'max@example.com')")
        cursor.execute("INSERT INTO projects VALUES (1, 1, 'Test Projekt')")
        conn.commit()
        
        # CREATE
        survey_id = feedback_manager.create_survey(
            conn,
            name="Test Umfrage",
            questions=[{'id': 'q1', 'type': 'rating', 'text': 'Test?', 'required': True}]
        )
        
        if survey_id:
            print("   CREATE: Umfrage erstellt")
        else:
            print("   CREATE: Fehler beim Erstellen")
            return False
        
        # READ
        survey = feedback_manager.get_survey_by_id(conn, survey_id)
        if survey and survey['name'] == "Test Umfrage":
            print("   READ: Umfrage geladen")
        else:
            print("   READ: Fehler beim Laden")
            return False
        
        # UPDATE
        success = feedback_manager.update_survey(conn, survey_id, name="Neue Umfrage")
        if success:
            survey = feedback_manager.get_survey_by_id(conn, survey_id)
            if survey['name'] == "Neue Umfrage":
                print("   UPDATE: Umfrage aktualisiert")
            else:
                print("   UPDATE: Änderung nicht gespeichert")
                return False
        else:
            print("   UPDATE: Fehler beim Aktualisieren")
            return False
        
        # DELETE
        success = feedback_manager.delete_survey(conn, survey_id)
        if success:
            survey = feedback_manager.get_survey_by_id(conn, survey_id)
            if survey is None:
                print("   DELETE: Umfrage gelöscht")
            else:
                print("   DELETE: Umfrage noch vorhanden")
                return False
        else:
            print("   DELETE: Fehler beim Löschen")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   Fehler bei CRUD-Operationen: {e}")
        return False


def verify_trigger_system():
    """Prüft Trigger-System."""
    print("\n Prüfe Trigger-System...")
    
    try:
        from crm.features import feedback_manager
        from datetime import datetime
        
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        
        feedback_manager.create_feedback_tables(conn)
        
        # Mock-Tabellen
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT)")
        cursor.execute("CREATE TABLE projects (id INTEGER PRIMARY KEY, customer_id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO customers VALUES (1, 'Max', 'Mustermann', 'max@example.com')")
        cursor.execute("INSERT INTO projects VALUES (1, 1, 'Test Projekt')")
        conn.commit()
        
        # Erstelle Umfrage mit Trigger
        survey_id = feedback_manager.create_survey(
            conn,
            name="Trigger Test",
            questions=[{'id': 'q1', 'type': 'rating', 'text': 'Test?', 'required': True}],
            trigger_event="project_completed",
            trigger_delay_days=0
        )
        
        # Löse Trigger aus
        trigger_ids = feedback_manager.trigger_survey_on_event(
            conn,
            event_type="project_completed",
            customer_id=1,
            project_id=1
        )
        
        if trigger_ids and len(trigger_ids) > 0:
            print("   Trigger erstellt")
        else:
            print("   Trigger nicht erstellt")
            return False
        
        # Lade ausstehende Trigger
        pending = feedback_manager.get_pending_triggers(conn, datetime.now().strftime('%Y-%m-%d'))
        if len(pending) > 0:
            print("   Ausstehende Trigger geladen")
        else:
            print("   Keine ausstehenden Trigger gefunden")
            return False
        
        # Markiere als versendet
        success = feedback_manager.mark_trigger_sent(conn, trigger_ids[0])
        if success:
            print("   Trigger als versendet markiert")
        else:
            print("   Fehler beim Markieren")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   Fehler im Trigger-System: {e}")
        return False


def verify_analytics():
    """Prüft Analytics-Funktionen."""
    print("\n Prüfe Analytics...")
    
    try:
        from crm.features import feedback_manager
        
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        
        feedback_manager.create_feedback_tables(conn)
        
        # Mock-Tabellen
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT)")
        cursor.execute("CREATE TABLE projects (id INTEGER PRIMARY KEY, customer_id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO customers VALUES (1, 'Max', 'Mustermann', 'max@example.com')")
        cursor.execute("INSERT INTO projects VALUES (1, 1, 'Test Projekt')")
        conn.commit()
        
        # Erstelle Umfrage und Antworten
        survey_id = feedback_manager.create_survey(
            conn,
            name="Analytics Test",
            questions=[{'id': 'q1', 'type': 'rating', 'text': 'Test?', 'required': True}]
        )
        
        # Erstelle Antworten
        feedback_manager.submit_response(conn, survey_id, 1, {'q1': 5}, overall_rating=5)
        feedback_manager.submit_response(conn, survey_id, 1, {'q1': 4}, overall_rating=4)
        feedback_manager.submit_response(conn, survey_id, 1, {'q1': 2}, overall_rating=2)
        
        # Statistiken
        stats = feedback_manager.get_survey_statistics(conn, survey_id)
        if stats['total_responses'] == 3:
            print("   Statistiken berechnet")
        else:
            print(f"   Falsche Anzahl Antworten: {stats['total_responses']}")
            return False
        
        # Negativ-Feedback
        alerts = feedback_manager.get_negative_feedback_alerts(conn, days=7)
        if len(alerts) == 1:
            print("   Negativ-Feedback erkannt")
        else:
            print(f"   Falsche Anzahl Alerts: {len(alerts)}")
            return False
        
        # Fragen-Statistiken
        q_stats = feedback_manager.get_question_statistics(conn, survey_id, 'q1')
        if q_stats['total_answers'] == 3:
            print("   Fragen-Statistiken berechnet")
        else:
            print(f"   Falsche Anzahl Antworten: {q_stats['total_answers']}")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   Fehler bei Analytics: {e}")
        return False


def verify_files():
    """Prüft ob alle Dateien vorhanden sind."""
    print("\n Prüfe Dateien...")
    
    files = [
        "crm/features/feedback_manager.py",
        "crm/features/feedback_ui.py",
        "crm/features/test_feedback_manager.py",
        "crm/features/FEEDBACK_MANAGER_REFERENCE.md",
        "crm/features/feedback_integration_example.py",
        "docs/FEEDBACK_SYSTEM_QUICK_REFERENCE.md"
    ]
    
    all_exist = True
    for file_path in files:
        if Path(file_path).exists():
            print(f"   {file_path}")
        else:
            print(f"   {file_path} fehlt")
            all_exist = False
    
    return all_exist


def main():
    """Hauptfunktion für Verifikation."""
    print("\n" + "=" * 70)
    print("FEEDBACK-SYSTEM VERIFIKATION")
    print("=" * 70 + "\n")
    
    results = []
    
    # Module
    results.append(("Module", verify_modules()))
    
    # Dateien
    results.append(("Dateien", verify_files()))
    
    # Datenbank
    results.append(("Datenbank-Tabellen", verify_database_tables()))
    
    # CRUD
    results.append(("CRUD-Operationen", verify_crud_operations()))
    
    # Trigger
    results.append(("Trigger-System", verify_trigger_system()))
    
    # Analytics
    results.append(("Analytics", verify_analytics()))
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70 + "\n")
    
    all_passed = True
    for name, passed in results:
        status = " BESTANDEN" if passed else " FEHLGESCHLAGEN"
        print(f"{name:.<50} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print(" ALLE TESTS BESTANDEN - IMPLEMENTIERUNG VOLLSTÄNDIG")
        print("=" * 70 + "\n")
        return 0
    else:
        print(" EINIGE TESTS FEHLGESCHLAGEN - BITTE PRÜFEN")
        print("=" * 70 + "\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
