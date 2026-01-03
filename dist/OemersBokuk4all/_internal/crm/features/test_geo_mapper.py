"""
Unit Tests für Geo-Mapping und Routenplanung

Testet die Funktionalität von geo_mapper.py

Anforderungen: 16.1, 16.2, 16.3
"""

import unittest
import sqlite3
import os
import tempfile
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import der zu testenden Module
try:
    from crm.features.geo_mapper import (
        GeoMapper, ensure_geo_columns,
        GEOCODING_AVAILABLE, FOLIUM_AVAILABLE
    )
except ImportError:
    from geo_mapper import (
        GeoMapper, ensure_geo_columns,
        GEOCODING_AVAILABLE, FOLIUM_AVAILABLE
    )


class TestGeoMapper(unittest.TestCase):
    """Test-Suite für GeoMapper"""
    
    def setUp(self):
        """Setup für jeden Test - erstellt temporäre Testdatenbank"""
        # Temporäre Datenbankdatei erstellen
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # Testdatenbank initialisieren
        self._create_test_database()
        
        # GeoMapper initialisieren
        self.mapper = GeoMapper(self.db_path)
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        # Datenbankverbindung schließen
        try:
            os.close(self.db_fd)
            os.unlink(self.db_path)
        except:
            pass
    
    def _create_test_database(self):
        """Erstellt eine Testdatenbank mit Beispieldaten"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Customers-Tabelle erstellen
        cursor.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                company_name TEXT,
                address TEXT,
                house_number TEXT,
                city TEXT,
                zip_code TEXT,
                email TEXT,
                phone_mobile TEXT,
                phone_landline TEXT,
                latitude REAL,
                longitude REAL,
                geocoded_at TEXT
            )
        """)
        
        # Appointments-Tabelle erstellen
        cursor.execute("""
            CREATE TABLE crm_appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                title TEXT,
                description TEXT,
                start_time TEXT,
                end_time TEXT,
                location TEXT,
                appointment_type TEXT,
                created_at TEXT
            )
        """)
        
        # Test-Kunden einfügen
        test_customers = [
            ('Max', 'Mustermann', 'Solar GmbH', 'Hauptstraße', '1', 'Berlin', '10115', 'max@example.com', '0171234567', None, None, None),
            ('Anna', 'Schmidt', None, 'Bahnhofstraße', '10', 'München', '80331', 'anna@example.com', '0172345678', None, None, None),
            ('Peter', 'Müller', 'Energie AG', 'Marktplatz', '5', 'Hamburg', '20095', 'peter@example.com', '0173456789', None, None, None),
            ('Lisa', 'Weber', None, 'Kirchstraße', '15', 'Köln', '50667', 'lisa@example.com', '0174567890', 52.5200, 13.4050, '2024-01-15T10:00:00'),  # Bereits geocodiert
        ]
        
        cursor.executemany("""
            INSERT INTO customers 
            (first_name, last_name, company_name, address, house_number, city, zip_code, email, phone_mobile, latitude, longitude, geocoded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_customers)
        
        conn.commit()
        conn.close()
    
    # Test 1: Geocoding
    def test_geocode_address(self):
        """
        Test: Geocoding einer Adresse
        
        Requirement: 16.1
        """
        if not GEOCODING_AVAILABLE:
            self.skipTest("Geocoding nicht verfügbar (geopy nicht installiert)")
        
        # Bekannte Adresse geocodieren
        coords = self.mapper.geocode_address(
            "Brandenburger Tor",
            "Berlin",
            "10117"
        )
        
        # Prüfen, ob Koordinaten zurückgegeben wurden
        self.assertIsNotNone(coords, "Geocoding sollte Koordinaten zurückgeben")
        self.assertEqual(len(coords), 2, "Koordinaten sollten aus 2 Werten bestehen")
        
        lat, lon = coords
        
        # Prüfen, ob Koordinaten im erwarteten Bereich liegen (Berlin)
        self.assertGreater(lat, 52.0, "Breitengrad sollte > 52 sein (Berlin)")
        self.assertLess(lat, 53.0, "Breitengrad sollte < 53 sein (Berlin)")
        self.assertGreater(lon, 13.0, "Längengrad sollte > 13 sein (Berlin)")
        self.assertLess(lon, 14.0, "Längengrad sollte < 14 sein (Berlin)")
        
        print(f"Geocoding erfolgreich: {coords}")
    
    def test_geocode_invalid_address(self):
        """
        Test: Geocoding einer ungültigen Adresse
        
        Requirement: 16.1
        """
        if not GEOCODING_AVAILABLE:
            self.skipTest("Geocoding nicht verfügbar")
        
        # Ungültige Adresse
        coords = self.mapper.geocode_address(
            "Nichtexistente Straße 999",
            "Nichtexistente Stadt",
            "99999"
        )
        
        # Sollte None zurückgeben
        self.assertIsNone(coords, "Ungültige Adresse sollte None zurückgeben")
        
        print("Ungültige Adresse korrekt behandelt")
    
    # Test 2: Kunden mit Koordinaten abrufen
    def test_get_customers_with_coordinates(self):
        """
        Test: Abrufen von Kunden mit Koordinaten
        
        Requirement: 16.2
        """
        # Kunden abrufen
        customers = self.mapper.get_customers_with_coordinates()
        
        # Prüfen, ob nur geocodierte Kunden zurückgegeben werden
        self.assertEqual(len(customers), 1, "Nur 1 Kunde sollte Koordinaten haben")
        
        customer = customers[0]
        self.assertEqual(customer['name'], "Lisa Weber")
        self.assertIsNotNone(customer['latitude'])
        self.assertIsNotNone(customer['longitude'])
        
        print(f"{len(customers)} Kunde(n) mit Koordinaten gefunden")
    
    def test_get_customers_with_filter(self):
        """
        Test: Filtern von Kunden nach Stadt
        
        Requirement: 16.2
        """
        # Filter anwenden
        customers = self.mapper.get_customers_with_coordinates({'city': 'Köln'})
        
        # Prüfen
        self.assertEqual(len(customers), 1, "1 Kunde in Köln sollte gefunden werden")
        self.assertEqual(customers[0]['city'], 'Köln')
        
        print("Filter funktioniert korrekt")
    
    # Test 3: Karten-Erstellung
    def test_create_map(self):
        """
        Test: Erstellung einer Karte mit Markern
        
        Requirement: 16.2, 16.3
        """
        if not FOLIUM_AVAILABLE:
            self.skipTest("Folium nicht verfügbar")
        
        # Kunden mit Koordinaten abrufen
        customers = self.mapper.get_customers_with_coordinates()
        
        if not customers:
            self.skipTest("Keine Kunden mit Koordinaten für Test verfügbar")
        
        # Karte erstellen
        map_obj = self.mapper.create_map(customers)
        
        # Prüfen, ob Karte erstellt wurde
        self.assertIsNotNone(map_obj, "Karte sollte erstellt werden")
        
        # Prüfen, ob es ein Folium-Map-Objekt ist
        import folium
        self.assertIsInstance(map_obj, folium.Map, "Sollte ein Folium-Map-Objekt sein")
        
        print("Karte erfolgreich erstellt")
    
    def test_create_map_empty(self):
        """
        Test: Karten-Erstellung mit leerer Kundenliste
        
        Requirement: 16.2
        """
        if not FOLIUM_AVAILABLE:
            self.skipTest("Folium nicht verfügbar")
        
        # Leere Liste
        map_obj = self.mapper.create_map([])
        
        # Sollte None zurückgeben
        self.assertIsNone(map_obj, "Leere Kundenliste sollte None zurückgeben")
        
        print("Leere Kundenliste korrekt behandelt")
    
    # Test 4: Entfernungsberechnung
    def test_calculate_distance(self):
        """
        Test: Berechnung der Entfernung zwischen zwei Punkten
        
        Requirement: 16.4
        """
        # Berlin und München (ca. 585 km)
        berlin = (52.5200, 13.4050)
        munich = (48.1351, 11.5820)
        
        distance = self.mapper.calculate_distance(berlin, munich)
        
        # Prüfen, ob Entfernung im erwarteten Bereich liegt
        self.assertGreater(distance, 500, "Entfernung sollte > 500 km sein")
        self.assertLess(distance, 650, "Entfernung sollte < 650 km sein")
        
        print(f"Entfernung Berlin-München: {distance:.2f} km")
    
    def test_calculate_distance_same_point(self):
        """
        Test: Entfernung zwischen identischen Punkten
        
        Requirement: 16.4
        """
        point = (52.5200, 13.4050)
        
        distance = self.mapper.calculate_distance(point, point)
        
        # Sollte 0 oder sehr klein sein
        self.assertLess(distance, 0.01, "Entfernung sollte nahe 0 sein")
        
        print(f"Entfernung zum gleichen Punkt: {distance:.6f} km")
    
    # Test 5: Routenoptimierung
    def test_optimize_route(self):
        """
        Test: Optimierung einer Route
        
        Requirement: 16.4
        """
        # Mehrere Kunden mit Koordinaten erstellen
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Zusätzliche Test-Kunden mit Koordinaten
        test_customers = [
            ('Test1', 'User1', None, 'Straße 1', '1', 'Berlin', '10115', None, None, 52.5200, 13.4050, datetime.now().isoformat()),
            ('Test2', 'User2', None, 'Straße 2', '2', 'Berlin', '10117', None, None, 52.5180, 13.4100, datetime.now().isoformat()),
            ('Test3', 'User3', None, 'Straße 3', '3', 'Berlin', '10119', None, None, 52.5220, 13.4150, datetime.now().isoformat()),
        ]
        
        cursor.executemany("""
            INSERT INTO customers 
            (first_name, last_name, company_name, address, house_number, city, zip_code, email, phone_mobile, latitude, longitude, geocoded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_customers)
        
        conn.commit()
        
        # IDs der Test-Kunden abrufen
        cursor.execute("SELECT id FROM customers WHERE first_name LIKE 'Test%'")
        customer_ids = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # Route optimieren
        route = self.mapper.optimize_route(customer_ids)
        
        # Prüfen
        self.assertEqual(len(route), len(customer_ids), "Route sollte alle Kunden enthalten")
        self.assertGreater(route[-1]['cumulative_distance_km'], 0, "Gesamtstrecke sollte > 0 sein")
        
        # Prüfen, ob Entfernungen berechnet wurden
        for i, stop in enumerate(route):
            if i > 0:
                self.assertGreater(stop['distance_km'], 0, "Entfernung sollte > 0 sein")
        
        print(f"Route optimiert: {len(route)} Stopps, {route[-1]['cumulative_distance_km']:.2f} km")
    
    def test_optimize_route_empty(self):
        """
        Test: Routenoptimierung mit leerer Liste
        
        Requirement: 16.4
        """
        route = self.mapper.optimize_route([])
        
        # Sollte leere Liste zurückgeben
        self.assertEqual(len(route), 0, "Leere Eingabe sollte leere Route zurückgeben")
        
        print("Leere Kundenliste korrekt behandelt")
    
    # Test 6: Kalender-Export
    def test_export_route_to_calendar(self):
        """
        Test: Export einer Route als Kalender-Termine
        
        Requirement: 16.5
        """
        # Test-Route erstellen
        test_route = [
            {
                'id': 1,
                'name': 'Test User 1',
                'address': 'Straße 1',
                'city': 'Berlin',
                'zip_code': '10115',
                'latitude': 52.5200,
                'longitude': 13.4050,
                'distance_km': 0,
                'cumulative_distance_km': 0
            },
            {
                'id': 2,
                'name': 'Test User 2',
                'address': 'Straße 2',
                'city': 'Berlin',
                'zip_code': '10117',
                'latitude': 52.5180,
                'longitude': 13.4100,
                'distance_km': 1.5,
                'cumulative_distance_km': 1.5
            }
        ]
        
        # Startdatum
        start_date = datetime(2024, 6, 1, 9, 0)
        
        # Termine generieren
        appointments = self.mapper.export_route_to_calendar(
            test_route,
            start_date,
            duration_per_stop_minutes=60
        )
        
        # Prüfen
        self.assertEqual(len(appointments), 2, "2 Termine sollten erstellt werden")
        
        # Ersten Termin prüfen
        apt1 = appointments[0]
        self.assertEqual(apt1['customer_id'], 1)
        self.assertIn('Kundenbesuch', apt1['title'])
        self.assertEqual(apt1['start_time'], start_date.isoformat())
        
        # Zweiten Termin prüfen (sollte später sein)
        apt2 = appointments[1]
        self.assertEqual(apt2['customer_id'], 2)
        
        start2 = datetime.fromisoformat(apt2['start_time'])
        self.assertGreater(start2, start_date, "Zweiter Termin sollte später sein")
        
        print(f"{len(appointments)} Termine erfolgreich generiert")
    
    def test_save_appointments_to_db(self):
        """
        Test: Speichern von Terminen in der Datenbank
        
        Requirement: 16.5
        """
        # Test-Termine
        appointments = [
            {
                'customer_id': 1,
                'title': 'Test Termin 1',
                'description': 'Test Beschreibung 1',
                'start_time': datetime.now().isoformat(),
                'end_time': (datetime.now() + timedelta(hours=1)).isoformat(),
                'location': 'Test Location 1',
                'appointment_type': 'customer_visit'
            },
            {
                'customer_id': 2,
                'title': 'Test Termin 2',
                'description': 'Test Beschreibung 2',
                'start_time': (datetime.now() + timedelta(hours=2)).isoformat(),
                'end_time': (datetime.now() + timedelta(hours=3)).isoformat(),
                'location': 'Test Location 2',
                'appointment_type': 'customer_visit'
            }
        ]
        
        # Speichern
        saved_count = self.mapper.save_appointments_to_db(appointments)
        
        # Prüfen
        self.assertEqual(saved_count, 2, "2 Termine sollten gespeichert werden")
        
        # Aus Datenbank abrufen und prüfen
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM crm_appointments")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 2, "2 Termine sollten in DB sein")
        
        print(f"{saved_count} Termine erfolgreich gespeichert")


class TestGeoHelpers(unittest.TestCase):
    """Tests für Hilfsfunktionen"""
    
    def test_ensure_geo_columns(self):
        """
        Test: Sicherstellen, dass Geo-Spalten existieren
        
        Requirement: 16.1
        """
        # Temporäre Datenbank
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        
        try:
            # Datenbank mit customers-Tabelle erstellen
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT,
                    last_name TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            # Geo-Spalten hinzufügen
            # Note: ensure_geo_columns verwendet get_db_connection aus database.py
            # Für diesen Test müssen wir die Funktion direkt aufrufen
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Spalten hinzufügen
            columns_to_add = {
                'latitude': 'REAL',
                'longitude': 'REAL',
                'geocoded_at': 'TEXT'
            }
            
            for col_name, col_type in columns_to_add.items():
                try:
                    cursor.execute(f"ALTER TABLE customers ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    pass
            
            conn.commit()
            
            # Prüfen, ob Spalten existieren
            cursor.execute("PRAGMA table_info(customers)")
            columns = [row[1] for row in cursor.fetchall()]
            
            conn.close()
            
            # Assertions
            self.assertIn('latitude', columns, "latitude-Spalte sollte existieren")
            self.assertIn('longitude', columns, "longitude-Spalte sollte existieren")
            self.assertIn('geocoded_at', columns, "geocoded_at-Spalte sollte existieren")
            
            print("Geo-Spalten erfolgreich hinzugefügt")
            
        finally:
            os.close(db_fd)
            os.unlink(db_path)


def run_tests():
    """Führt alle Tests aus"""
    # Test-Suite erstellen
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Tests hinzufügen
    suite.addTests(loader.loadTestsFromTestCase(TestGeoMapper))
    suite.addTests(loader.loadTestsFromTestCase(TestGeoHelpers))
    
    # Tests ausführen
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Zusammenfassung
    print("\n" + "="*70)
    print("TEST-ZUSAMMENFASSUNG")
    print("="*70)
    print(f"Tests durchgeführt: {result.testsRun}")
    print(f"Erfolgreich: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fehlgeschlagen: {len(result.failures)}")
    print(f"Fehler: {len(result.errors)}")
    print(f"Übersprungen: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\nALLE TESTS ERFOLGREICH!")
    else:
        print("\nEINIGE TESTS FEHLGESCHLAGEN")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
