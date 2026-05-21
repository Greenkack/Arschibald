# crm/features/test_note_manager.py
"""
Unit Tests für das Notizen- und Kommunikationshistorie-Management.

Testet alle CRUD-Funktionen, Suche, Filterung und Timeline-Funktionalität.
"""

import pytest
import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from crm.features.note_manager import (
    create_activity,
    get_activity,
    get_customer_activities,
    update_activity,
    delete_activity,
    toggle_important,
    search_activities,
    auto_archive_old_activities,
    get_activity_statistics,
    add_note,
    add_email_activity,
    add_call_activity,
    add_appointment_activity,
    ACTIVITY_TYPES
)
from database import get_db_connection


# Test-Datenbank Setup
TEST_DB_PATH = "test_note_manager.db"


@pytest.fixture(scope="function")
def test_db():
    """Erstellt eine Test-Datenbank für jeden Test."""
    # Setze Test-DB-Pfad
    import database
    original_db_path = database.DB_PATH
    database.DB_PATH = TEST_DB_PATH
    
    # Erstelle Test-DB
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    
    # Erstelle Tabellen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crm_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_important BOOLEAN DEFAULT 0,
            archived BOOLEAN DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
    """)
    
    # Füge Test-Kunden hinzu
    cursor.execute("INSERT INTO customers (name, email) VALUES (?, ?)", ("Test Kunde", "test@example.com"))
    conn.commit()
    conn.close()
    
    yield TEST_DB_PATH
    
    # Cleanup
    database.DB_PATH = original_db_path
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


class TestActivityCreation:
    """Tests für das Erstellen von Aktivitäten."""
    
    def test_create_activity_success(self, test_db):
        """Test: Aktivität erfolgreich erstellen."""
        activity_id = create_activity(
            customer_id=1,
            activity_type="note",
            title="Test Notiz",
            content="Dies ist eine Test-Notiz",
            created_by="Test User",
            is_important=False
        )
        
        assert activity_id is not None
        assert activity_id > 0
    
    def test_create_activity_with_all_types(self, test_db):
        """Test: Aktivitäten mit allen Typen erstellen."""
        for activity_type in ACTIVITY_TYPES.keys():
            activity_id = create_activity(
                customer_id=1,
                activity_type=activity_type,
                title=f"Test {activity_type}",
                content=f"Test content for {activity_type}"
            )
            assert activity_id is not None
    
    def test_create_activity_invalid_type(self, test_db):
        """Test: Aktivität mit ungültigem Typ."""
        activity_id = create_activity(
            customer_id=1,
            activity_type="invalid_type",
            title="Test",
            content="Test"
        )
        
        assert activity_id is None
    
    def test_create_activity_important(self, test_db):
        """Test: Wichtige Aktivität erstellen."""
        activity_id = create_activity(
            customer_id=1,
            activity_type="note",
            title="Wichtige Notiz",
            content="Dies ist wichtig",
            is_important=True
        )
        
        assert activity_id is not None
        
        # Prüfe, ob wichtig-Flag gesetzt ist
        activity = get_activity(activity_id)
        assert activity is not None
        assert activity["is_important"] is True
    
    def test_add_note_helper(self, test_db):
        """Test: Notiz mit Helper-Funktion hinzufügen."""
        note_id = add_note(
            customer_id=1,
            title="Test Note",
            content="Note content",
            created_by="Test User"
        )
        
        assert note_id is not None
        
        note = get_activity(note_id)
        assert note["activity_type"] == "note"
    
    def test_add_email_helper(self, test_db):
        """Test: E-Mail mit Helper-Funktion hinzufügen."""
        email_id = add_email_activity(
            customer_id=1,
            subject="Test Email",
            body="Email body"
        )
        
        assert email_id is not None
        
        email = get_activity(email_id)
        assert email["activity_type"] == "email"
    
    def test_add_call_helper(self, test_db):
        """Test: Anruf mit Helper-Funktion hinzufügen."""
        call_id = add_call_activity(
            customer_id=1,
            title="Test Call",
            notes="Call notes"
        )
        
        assert call_id is not None
        
        call = get_activity(call_id)
        assert call["activity_type"] == "call"
    
    def test_add_appointment_helper(self, test_db):
        """Test: Termin mit Helper-Funktion hinzufügen."""
        appointment_id = add_appointment_activity(
            customer_id=1,
            title="Test Appointment",
            details="Appointment details"
        )
        
        assert appointment_id is not None
        
        appointment = get_activity(appointment_id)
        assert appointment["activity_type"] == "appointment"


class TestActivityRetrieval:
    """Tests für das Abrufen von Aktivitäten."""
    
    def test_get_activity_success(self, test_db):
        """Test: Einzelne Aktivität abrufen."""
        # Erstelle Aktivität
        activity_id = create_activity(
            customer_id=1,
            activity_type="note",
            title="Test Notiz",
            content="Test Inhalt"
        )
        
        # Rufe ab
        activity = get_activity(activity_id)
        
        assert activity is not None
        assert activity["id"] == activity_id
        assert activity["title"] == "Test Notiz"
        assert activity["content"] == "Test Inhalt"
        assert activity["activity_type"] == "note"
    
    def test_get_activity_not_found(self, test_db):
        """Test: Nicht existierende Aktivität."""
        activity = get_activity(99999)
        assert activity is None
    
    def test_get_customer_activities(self, test_db):
        """Test: Alle Aktivitäten eines Kunden abrufen."""
        # Erstelle mehrere Aktivitäten
        for i in range(5):
            create_activity(
                customer_id=1,
                activity_type="note",
                title=f"Notiz {i}",
                content=f"Inhalt {i}"
            )
        
        # Rufe ab
        activities = get_customer_activities(customer_id=1)
        
        assert len(activities) == 5
        # Prüfe, dass alle Aktivitäten vorhanden sind
        titles = [a["title"] for a in activities]
        assert "Notiz 0" in titles
        assert "Notiz 4" in titles
    
    def test_get_customer_activities_filtered_by_type(self, test_db):
        """Test: Aktivitäten nach Typ filtern."""
        # Erstelle verschiedene Typen
        create_activity(customer_id=1, activity_type="note", title="Notiz 1")
        create_activity(customer_id=1, activity_type="email", title="Email 1")
        create_activity(customer_id=1, activity_type="call", title="Anruf 1")
        create_activity(customer_id=1, activity_type="note", title="Notiz 2")
        
        # Filtere nach Notizen
        notes = get_customer_activities(customer_id=1, activity_type="note")
        
        assert len(notes) == 2
        assert all(a["activity_type"] == "note" for a in notes)
    
    def test_get_customer_activities_exclude_archived(self, test_db):
        """Test: Archivierte Aktivitäten ausschließen."""
        # Erstelle Aktivitäten
        id1 = create_activity(customer_id=1, activity_type="note", title="Aktiv")
        id2 = create_activity(customer_id=1, activity_type="note", title="Archiviert")
        
        # Archiviere eine
        update_activity(id2, archived=True)
        
        # Rufe ohne archivierte ab
        activities = get_customer_activities(customer_id=1, include_archived=False)
        
        assert len(activities) == 1
        assert activities[0]["title"] == "Aktiv"
    
    def test_get_customer_activities_include_archived(self, test_db):
        """Test: Archivierte Aktivitäten einschließen."""
        # Erstelle Aktivitäten
        id1 = create_activity(customer_id=1, activity_type="note", title="Aktiv")
        id2 = create_activity(customer_id=1, activity_type="note", title="Archiviert")
        
        # Archiviere eine
        update_activity(id2, archived=True)
        
        # Rufe mit archivierten ab
        activities = get_customer_activities(customer_id=1, include_archived=True)
        
        assert len(activities) == 2
    
    def test_get_customer_activities_limit(self, test_db):
        """Test: Limit für Aktivitäten."""
        # Erstelle 10 Aktivitäten
        for i in range(10):
            create_activity(customer_id=1, activity_type="note", title=f"Notiz {i}")
        
        # Rufe mit Limit ab
        activities = get_customer_activities(customer_id=1, limit=5)
        
        assert len(activities) == 5


class TestActivityUpdate:
    """Tests für das Aktualisieren von Aktivitäten."""
    
    def test_update_activity_title(self, test_db):
        """Test: Titel aktualisieren."""
        activity_id = create_activity(
            customer_id=1,
            activity_type="note",
            title="Alter Titel"
        )
        
        success = update_activity(activity_id, title="Neuer Titel")
        
        assert success is True
        
        activity = get_activity(activity_id)
        assert activity["title"] == "Neuer Titel"
    
    def test_update_activity_content(self, test_db):
        """Test: Inhalt aktualisieren."""
        activity_id = create_activity(
            customer_id=1,
            activity_type="note",
            title="Test",
            content="Alter Inhalt"
        )
        
        success = update_activity(activity_id, content="Neuer Inhalt")
        
        assert success is True
        
        activity = get_activity(activity_id)
        assert activity["content"] == "Neuer Inhalt"
    
    def test_update_activity_important(self, test_db):
        """Test: Wichtig-Status aktualisieren."""
        activity_id = create_activity(
            customer_id=1,
            activity_type="note",
            title="Test",
            is_important=False
        )
        
        success = update_activity(activity_id, is_important=True)
        
        assert success is True
        
        activity = get_activity(activity_id)
        assert activity["is_important"] is True
    
    def test_update_activity_archived(self, test_db):
        """Test: Archiviert-Status aktualisieren."""
        activity_id = create_activity(
            customer_id=1,
            activity_type="note",
            title="Test"
        )
        
        success = update_activity(activity_id, archived=True)
        
        assert success is True
        
        activity = get_activity(activity_id)
        assert activity["archived"] is True
    
    def test_update_activity_multiple_fields(self, test_db):
        """Test: Mehrere Felder gleichzeitig aktualisieren."""
        activity_id = create_activity(
            customer_id=1,
            activity_type="note",
            title="Alter Titel",
            content="Alter Inhalt"
        )
        
        success = update_activity(
            activity_id,
            title="Neuer Titel",
            content="Neuer Inhalt",
            is_important=True
        )
        
        assert success is True
        
        activity = get_activity(activity_id)
        assert activity["title"] == "Neuer Titel"
        assert activity["content"] == "Neuer Inhalt"
        assert activity["is_important"] is True
    
    def test_update_activity_not_found(self, test_db):
        """Test: Nicht existierende Aktivität aktualisieren."""
        success = update_activity(99999, title="Test")
        assert success is False
    
    def test_toggle_important(self, test_db):
        """Test: Wichtig-Status umschalten."""
        activity_id = create_activity(
            customer_id=1,
            activity_type="note",
            title="Test",
            is_important=False
        )
        
        # Umschalten auf True
        success = toggle_important(activity_id)
        assert success is True
        
        activity = get_activity(activity_id)
        assert activity["is_important"] is True
        
        # Umschalten auf False
        success = toggle_important(activity_id)
        assert success is True
        
        activity = get_activity(activity_id)
        assert activity["is_important"] is False


class TestActivityDeletion:
    """Tests für das Löschen von Aktivitäten."""
    
    def test_delete_activity_success(self, test_db):
        """Test: Aktivität erfolgreich löschen."""
        activity_id = create_activity(
            customer_id=1,
            activity_type="note",
            title="Test"
        )
        
        success = delete_activity(activity_id)
        
        assert success is True
        
        # Prüfe, ob gelöscht
        activity = get_activity(activity_id)
        assert activity is None
    
    def test_delete_activity_not_found(self, test_db):
        """Test: Nicht existierende Aktivität löschen."""
        success = delete_activity(99999)
        assert success is False


class TestActivitySearch:
    """Tests für die Volltextsuche."""
    
    def test_search_activities_in_title(self, test_db):
        """Test: Suche im Titel."""
        create_activity(customer_id=1, activity_type="note", title="Wichtige Besprechung")
        create_activity(customer_id=1, activity_type="note", title="Unwichtige Notiz")
        create_activity(customer_id=1, activity_type="note", title="Termin vereinbaren")
        
        results = search_activities("Wichtige", customer_id=1)
        
        # LIKE-Suche findet sowohl "Wichtige" als auch "Unwichtige"
        assert len(results) >= 1
        assert any("Wichtige" in r["title"] for r in results)
    
    def test_search_activities_in_content(self, test_db):
        """Test: Suche im Inhalt."""
        create_activity(
            customer_id=1,
            activity_type="note",
            title="Notiz 1",
            content="Dies ist ein wichtiger Punkt"
        )
        create_activity(
            customer_id=1,
            activity_type="note",
            title="Notiz 2",
            content="Dies ist unwichtig"
        )
        
        results = search_activities("wichtiger Punkt", customer_id=1)
        
        assert len(results) >= 1
        assert any("wichtiger Punkt" in r["content"] for r in results)
    
    def test_search_activities_case_insensitive(self, test_db):
        """Test: Suche ist case-insensitive."""
        create_activity(customer_id=1, activity_type="note", title="WICHTIG")
        
        results = search_activities("wichtig", customer_id=1)
        
        assert len(results) == 1
    
    def test_search_activities_with_type_filter(self, test_db):
        """Test: Suche mit Typ-Filter."""
        create_activity(customer_id=1, activity_type="note", title="Test Notiz")
        create_activity(customer_id=1, activity_type="email", title="Test Email")
        
        results = search_activities("Test", customer_id=1, activity_type="note")
        
        assert len(results) == 1
        assert results[0]["activity_type"] == "note"
    
    def test_search_activities_no_results(self, test_db):
        """Test: Suche ohne Ergebnisse."""
        create_activity(customer_id=1, activity_type="note", title="Test")
        
        results = search_activities("Nicht vorhanden", customer_id=1)
        
        assert len(results) == 0


class TestActivityArchiving:
    """Tests für die Auto-Archivierung."""
    
    def test_auto_archive_old_activities(self, test_db):
        """Test: Alte Aktivitäten automatisch archivieren."""
        # Erstelle alte Aktivität (manuell in DB)
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        
        old_date = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO crm_activities 
            (customer_id, activity_type, title, created_at, is_important, archived)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (1, "note", "Alte Notiz", old_date, 0, 0)
        )
        conn.commit()
        conn.close()
        
        # Archiviere alte Aktivitäten
        count = auto_archive_old_activities(days_threshold=30)
        
        assert count == 1
    
    def test_auto_archive_keeps_important(self, test_db):
        """Test: Wichtige Aktivitäten werden nicht archiviert."""
        # Erstelle alte wichtige Aktivität
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        
        old_date = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO crm_activities 
            (customer_id, activity_type, title, created_at, is_important, archived)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (1, "note", "Wichtige alte Notiz", old_date, 1, 0)
        )
        conn.commit()
        conn.close()
        
        # Archiviere alte Aktivitäten
        count = auto_archive_old_activities(days_threshold=30)
        
        assert count == 0


class TestActivityStatistics:
    """Tests für Aktivitäts-Statistiken."""
    
    def test_get_activity_statistics(self, test_db):
        """Test: Statistiken abrufen."""
        # Erstelle verschiedene Aktivitäten
        create_activity(customer_id=1, activity_type="note", title="Notiz 1")
        create_activity(customer_id=1, activity_type="note", title="Notiz 2")
        create_activity(customer_id=1, activity_type="email", title="Email 1")
        create_activity(customer_id=1, activity_type="note", title="Wichtig", is_important=True)
        
        stats = get_activity_statistics(customer_id=1)
        
        assert stats["total"] == 4
        assert stats["by_type"]["note"] == 3
        assert stats["by_type"]["email"] == 1
        assert stats["important"] == 1
        assert stats["last_activity"] is not None
    
    def test_get_activity_statistics_empty(self, test_db):
        """Test: Statistiken für Kunde ohne Aktivitäten."""
        stats = get_activity_statistics(customer_id=1)
        
        assert stats["total"] == 0
        assert stats["important"] == 0
        assert stats["last_activity"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
