# crm/features/test_call_manager.py
"""
Unit Tests für Anruf-Protokollierung (call_manager.py).

Testet:
- Anruf-Erstellung
- Timer-Funktion (Dauer-Formatierung)
- Timeline-Integration
- Anruf-Statistiken
"""

import unittest
import sqlite3
import os
import sys
from datetime import datetime

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from crm.features.call_manager import (
    create_call, get_call, get_customer_calls, update_call, delete_call,
    get_call_statistics, format_duration, parse_duration, ensure_call_fields,
    CALL_DIRECTIONS
)


class TestCallManager(unittest.TestCase):
    """Test-Suite für call_manager.py"""
    
    def setUp(self):
        """Erstellt eine Test-Datenbank vor jedem Test."""
        self.test_db = "test_call_manager.db"
        self.conn = sqlite3.connect(self.test_db)
        self.conn.row_factory = sqlite3.Row
        
        # Erstelle Tabellen
        cursor = self.conn.cursor()
        
        # customers Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                mobile TEXT
            )
        """)
        
        # crm_activities Tabelle (Basis)
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
        
        self.conn.commit()
        
        # Füge Anruf-Felder hinzu
        self._add_call_fields()
        
        # Erstelle Test-Kunden
        cursor.execute(
            "INSERT INTO customers (name, email, phone, mobile) VALUES (?, ?, ?, ?)",
            ("Test Kunde", "test@example.com", "+43 123 456789", "+43 987 654321")
        )
        self.conn.commit()
        self.test_customer_id = cursor.lastrowid
        
        # Mock get_db_connection
        import crm.features.call_manager as call_manager_module
        self.original_get_db_connection = call_manager_module.get_db_connection
        call_manager_module.get_db_connection = lambda: sqlite3.connect(self.test_db)
        
        # Setze row_factory für neue Verbindungen
        def get_test_connection():
            conn = sqlite3.connect(self.test_db)
            conn.row_factory = sqlite3.Row
            return conn
        call_manager_module.get_db_connection = get_test_connection
    
    def _add_call_fields(self):
        """Fügt Anruf-spezifische Felder zur crm_activities Tabelle hinzu."""
        cursor = self.conn.cursor()
        
        # Prüfe, welche Spalten bereits existieren
        cursor.execute("PRAGMA table_info(crm_activities)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        # Füge fehlende Spalten hinzu
        columns_to_add = {
            "call_direction": "TEXT",
            "call_phone_number": "TEXT",
            "call_duration_seconds": "INTEGER DEFAULT 0",
            "call_notes": "TEXT"
        }
        
        for column_name, column_type in columns_to_add.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE crm_activities ADD COLUMN {column_name} {column_type}")
                except sqlite3.OperationalError:
                    pass  # Spalte existiert bereits
        
        self.conn.commit()
    
    def tearDown(self):
        """Räumt nach jedem Test auf."""
        # Stelle ursprüngliche Funktion wieder her
        import crm.features.call_manager as call_manager_module
        call_manager_module.get_db_connection = self.original_get_db_connection
        
        self.conn.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    # Test 1: Anruf-Erstellung
    def test_create_call_outgoing(self):
        """Testet das Erstellen eines ausgehenden Anrufs."""
        call_id = create_call(
            customer_id=self.test_customer_id,
            phone_number="+43 123 456789",
            direction="outgoing",
            duration_seconds=300,
            notes="Angebot besprochen",
            created_by="Test User"
        )
        
        self.assertIsNotNone(call_id)
        self.assertIsInstance(call_id, int)
        
        # Prüfe, ob Anruf korrekt gespeichert wurde
        call = get_call(call_id)
        self.assertIsNotNone(call)
        self.assertEqual(call["customer_id"], self.test_customer_id)
        self.assertEqual(call["call_direction"], "outgoing")
        self.assertEqual(call["call_phone_number"], "+43 123 456789")
        self.assertEqual(call["call_duration_seconds"], 300)
        self.assertEqual(call["call_notes"], "Angebot besprochen")
        self.assertEqual(call["created_by"], "Test User")
        self.assertEqual(call["activity_type"], "call")
    
    def test_create_call_incoming(self):
        """Testet das Erstellen eines eingehenden Anrufs."""
        call_id = create_call(
            customer_id=self.test_customer_id,
            phone_number="+43 987 654321",
            direction="incoming",
            duration_seconds=180,
            notes="Kunde hat Fragen",
            created_by="Test User"
        )
        
        self.assertIsNotNone(call_id)
        
        call = get_call(call_id)
        self.assertEqual(call["call_direction"], "incoming")
        self.assertEqual(call["call_direction_display"], "Eingehend")
    
    def test_create_call_invalid_direction(self):
        """Testet das Erstellen eines Anrufs mit ungültiger Richtung."""
        call_id = create_call(
            customer_id=self.test_customer_id,
            phone_number="+43 123 456789",
            direction="invalid",
            duration_seconds=100
        )
        
        self.assertIsNone(call_id)
    
    # Test 2: Timer-Funktion (Dauer-Formatierung)
    def test_format_duration_seconds_only(self):
        """Testet Formatierung von Sekunden."""
        self.assertEqual(format_duration(45), "0:45")
        self.assertEqual(format_duration(5), "0:05")
    
    def test_format_duration_minutes_seconds(self):
        """Testet Formatierung von Minuten und Sekunden."""
        self.assertEqual(format_duration(300), "5:00")
        self.assertEqual(format_duration(323), "5:23")
        self.assertEqual(format_duration(65), "1:05")
    
    def test_format_duration_hours(self):
        """Testet Formatierung mit Stunden."""
        self.assertEqual(format_duration(3600), "1:00:00")
        self.assertEqual(format_duration(3665), "1:01:05")
        self.assertEqual(format_duration(7323), "2:02:03")
    
    def test_format_duration_zero(self):
        """Testet Formatierung von 0 Sekunden."""
        self.assertEqual(format_duration(0), "0:00")
    
    def test_format_duration_negative(self):
        """Testet Formatierung von negativen Werten."""
        self.assertEqual(format_duration(-100), "0:00")
    
    def test_parse_duration_minutes_seconds(self):
        """Testet Parsen von MM:SS Format."""
        self.assertEqual(parse_duration("5:30"), 330)
        self.assertEqual(parse_duration("0:45"), 45)
        self.assertEqual(parse_duration("12:05"), 725)
    
    def test_parse_duration_hours(self):
        """Testet Parsen von HH:MM:SS Format."""
        self.assertEqual(parse_duration("1:30:00"), 5400)
        self.assertEqual(parse_duration("2:15:30"), 8130)
    
    def test_parse_duration_invalid(self):
        """Testet Parsen von ungültigen Formaten."""
        self.assertEqual(parse_duration("invalid"), 0)
        self.assertEqual(parse_duration(""), 0)
        self.assertEqual(parse_duration("5"), 0)
    
    # Test 3: Timeline-Integration (Abrufen von Anrufen)
    def test_get_customer_calls_empty(self):
        """Testet Abrufen von Anrufen wenn keine vorhanden sind."""
        calls = get_customer_calls(self.test_customer_id)
        self.assertEqual(len(calls), 0)
    
    def test_get_customer_calls_multiple(self):
        """Testet Abrufen mehrerer Anrufe."""
        # Erstelle mehrere Anrufe
        call_id1 = create_call(self.test_customer_id, "+43 111", "outgoing", 100)
        call_id2 = create_call(self.test_customer_id, "+43 222", "incoming", 200)
        call_id3 = create_call(self.test_customer_id, "+43 333", "outgoing", 300)
        
        calls = get_customer_calls(self.test_customer_id)
        self.assertEqual(len(calls), 3)
        
        # Prüfe, dass alle Telefonnummern vorhanden sind
        phone_numbers = {call["call_phone_number"] for call in calls}
        self.assertEqual(phone_numbers, {"+43 111", "+43 222", "+43 333"})
        
        # Prüfe, dass alle Anrufe die richtigen Felder haben
        for call in calls:
            self.assertIn("call_direction", call)
            self.assertIn("call_phone_number", call)
            self.assertIn("call_duration_seconds", call)
            self.assertIn("call_duration_formatted", call)
    
    def test_get_customer_calls_filter_direction(self):
        """Testet Filtern nach Richtung."""
        create_call(self.test_customer_id, "+43 111", "outgoing", 100)
        create_call(self.test_customer_id, "+43 222", "incoming", 200)
        create_call(self.test_customer_id, "+43 333", "outgoing", 300)
        
        # Nur ausgehende
        outgoing_calls = get_customer_calls(self.test_customer_id, direction="outgoing")
        self.assertEqual(len(outgoing_calls), 2)
        for call in outgoing_calls:
            self.assertEqual(call["call_direction"], "outgoing")
        
        # Nur eingehende
        incoming_calls = get_customer_calls(self.test_customer_id, direction="incoming")
        self.assertEqual(len(incoming_calls), 1)
        self.assertEqual(incoming_calls[0]["call_direction"], "incoming")
    
    def test_get_customer_calls_limit(self):
        """Testet Limit-Parameter."""
        # Erstelle 5 Anrufe
        for i in range(5):
            create_call(self.test_customer_id, f"+43 {i}", "outgoing", 100)
        
        calls = get_customer_calls(self.test_customer_id, limit=3)
        self.assertEqual(len(calls), 3)
    
    # Test 4: Anruf-Aktualisierung
    def test_update_call_duration(self):
        """Testet Aktualisierung der Anrufdauer."""
        call_id = create_call(self.test_customer_id, "+43 123", "outgoing", 100)
        
        success = update_call(call_id, duration_seconds=200)
        self.assertTrue(success)
        
        call = get_call(call_id)
        self.assertEqual(call["call_duration_seconds"], 200)
    
    def test_update_call_notes(self):
        """Testet Aktualisierung der Notizen."""
        call_id = create_call(self.test_customer_id, "+43 123", "outgoing", 100, notes="Alt")
        
        success = update_call(call_id, notes="Neu")
        self.assertTrue(success)
        
        call = get_call(call_id)
        self.assertEqual(call["call_notes"], "Neu")
    
    def test_update_call_phone_number(self):
        """Testet Aktualisierung der Telefonnummer."""
        call_id = create_call(self.test_customer_id, "+43 111", "outgoing", 100)
        
        success = update_call(call_id, phone_number="+43 999")
        self.assertTrue(success)
        
        call = get_call(call_id)
        self.assertEqual(call["call_phone_number"], "+43 999")
    
    # Test 5: Anruf-Löschung
    def test_delete_call(self):
        """Testet Löschen eines Anrufs."""
        call_id = create_call(self.test_customer_id, "+43 123", "outgoing", 100)
        
        success = delete_call(call_id)
        self.assertTrue(success)
        
        call = get_call(call_id)
        self.assertIsNone(call)
    
    def test_delete_nonexistent_call(self):
        """Testet Löschen eines nicht existierenden Anrufs."""
        success = delete_call(99999)
        self.assertFalse(success)
    
    # Test 6: Anruf-Statistiken
    def test_call_statistics_empty(self):
        """Testet Statistiken ohne Anrufe."""
        stats = get_call_statistics(self.test_customer_id)
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["incoming"], 0)
        self.assertEqual(stats["outgoing"], 0)
        self.assertEqual(stats["total_duration_seconds"], 0)
    
    def test_call_statistics_with_calls(self):
        """Testet Statistiken mit mehreren Anrufen."""
        create_call(self.test_customer_id, "+43 111", "outgoing", 300)  # 5 min
        create_call(self.test_customer_id, "+43 222", "incoming", 180)  # 3 min
        create_call(self.test_customer_id, "+43 333", "outgoing", 120)  # 2 min
        
        stats = get_call_statistics(self.test_customer_id)
        
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["incoming"], 1)
        self.assertEqual(stats["outgoing"], 2)
        self.assertEqual(stats["total_duration_seconds"], 600)  # 10 min
        self.assertEqual(stats["average_duration_seconds"], 200)  # 3:20 min
        self.assertIsNotNone(stats["last_call"])
    
    def test_call_statistics_duration_formatting(self):
        """Testet Formatierung der Dauer in Statistiken."""
        create_call(self.test_customer_id, "+43 111", "outgoing", 3665)  # 1:01:05
        
        stats = get_call_statistics(self.test_customer_id)
        
        self.assertEqual(stats["total_duration_formatted"], "1:01:05")
        self.assertEqual(stats["average_duration_formatted"], "1:01:05")
    
    # Test 7: Ensure Call Fields
    def test_ensure_call_fields(self):
        """Testet das Hinzufügen von Anruf-Feldern."""
        # Felder sollten bereits existieren durch setUp
        success = ensure_call_fields()
        self.assertTrue(success)
        
        # Prüfe, ob alle Felder vorhanden sind
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(crm_activities)")
        columns = {row[1] for row in cursor.fetchall()}
        
        self.assertIn("call_direction", columns)
        self.assertIn("call_phone_number", columns)
        self.assertIn("call_duration_seconds", columns)
        self.assertIn("call_notes", columns)


def run_tests():
    """Führt alle Tests aus."""
    # Erstelle Test-Suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCallManager)
    
    # Führe Tests aus
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Gebe Zusammenfassung aus
    print("\n" + "="*70)
    print("TEST ZUSAMMENFASSUNG")
    print("="*70)
    print(f"Tests durchgeführt: {result.testsRun}")
    print(f"Erfolgreich: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fehlgeschlagen: {len(result.failures)}")
    print(f"Fehler: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
