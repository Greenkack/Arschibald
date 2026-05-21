"""
Unit Tests für Calculation Bridge

Testet das Speichern von Berechnungen, Versionierung und Vergleichs-Funktion.

Führe aus mit: python crm/integration/test_calculation_bridge.py
"""

import sqlite3
import json
from unittest.mock import patch


class NonClosingConnection:
    """Wrapper für Datenbankverbindung die close() ignoriert"""
    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, name):
        if name == 'close':
            # Ignoriere close() Aufrufe
            return lambda: None
        return getattr(self._conn, name)


def setup_test_db():
    """Erstellt eine In-Memory-Testdatenbank mit allen benötigten Tabellen"""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Erstelle customers Tabelle
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )
    """)

    # Erstelle projects Tabelle
    cursor.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            project_name TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    """)

    # Erstelle project_calculations Tabelle
    cursor.execute("""
        CREATE TABLE project_calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            calculation_data TEXT NOT NULL,
            calculation_type TEXT,
            is_main_offer INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            notes TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    """)

    # Füge Testdaten hinzu
    cursor.execute("""
        INSERT INTO customers (first_name, last_name, email)
        VALUES ('Max', 'Mustermann', 'max@example.com')
    """)

    cursor.execute("""
        INSERT INTO projects (customer_id, project_name)
        VALUES (1, 'Test PV-Anlage')
    """)

    conn.commit()
    # Wrap connection to prevent closing
    return NonClosingConnection(conn)


def test_save_calculation_basic():
    """Test: Grundlegendes Speichern einer Berechnung"""
    conn = setup_test_db()

    # Import here to use mocked functions
    from crm.integration import calculation_bridge

    # Setup - Berechnungsdaten
    calculation_data = {
        'annual_pv_production_kwh': 8500.0,
        'total_investment_netto': 15000.0,
        'total_investment_brutto': 17850.0,
        'annual_total_savings_euro': 1200.0,
        'payback_period_years': 12.5,
    }

    # Mock database functions
    with patch.object(
        calculation_bridge, 'get_db_connection', return_value=conn
    ):
        with patch.object(
            calculation_bridge, 'ensure_project_calculations_table'
        ):
            # Execute
            calc_id = calculation_bridge.save_calculation_to_project(
                project_id=1,
                customer_id=1,
                calculation_data=calculation_data,
                calculation_type='pv',
                created_by='Test User',
                notes='Erste Berechnung'
            )

    # Assert
    assert calc_id is not None
    assert calc_id > 0

    # Überprüfe in Datenbank
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM project_calculations WHERE id = ?",
        (calc_id)
    )
    row = cursor.fetchone()

    assert row is not None
    assert row['project_id'] == 1
    assert row['customer_id'] == 1
    assert row['version'] == 1
    assert row['calculation_type'] == 'pv'
    assert row['created_by'] == 'Test User'
    assert row['notes'] == 'Erste Berechnung'
    assert row['is_main_offer'] == 0

    # Überprüfe JSON-Daten
    stored_data = json.loads(row['calculation_data'])
    assert stored_data['annual_pv_production_kwh'] == 8500.0
    assert stored_data['total_investment_netto'] == 15000.0

    conn.close()
    print("Test save_calculation_basic bestanden")


def test_save_calculation_versioning():
    """Test: Automatische Versionierung bei mehreren Berechnungen"""
    conn = setup_test_db()
    from crm.integration import calculation_bridge

    # Setup - Drei Berechnungen
    calc_data_v1 = {'annual_pv_production_kwh': 8000.0}
    calc_data_v2 = {'annual_pv_production_kwh': 9000.0}
    calc_data_v3 = {'annual_pv_production_kwh': 10000.0}

    with patch.object(calculation_bridge, 'get_db_connection', return_value=conn):
        with patch.object(calculation_bridge, 'ensure_project_calculations_table'):
            calc_id_v1 = calculation_bridge.save_calculation_to_project(
                project_id=1, customer_id=1,
                calculation_data=calc_data_v1, calculation_type='pv'
            )
            calc_id_v2 = calculation_bridge.save_calculation_to_project(
                project_id=1, customer_id=1,
                calculation_data=calc_data_v2, calculation_type='pv'
            )
            calc_id_v3 = calculation_bridge.save_calculation_to_project(
                project_id=1, customer_id=1,
                calculation_data=calc_data_v3, calculation_type='pv'
            )

    # Assert - Alle IDs sind unterschiedlich
    assert calc_id_v1 != calc_id_v2
    assert calc_id_v2 != calc_id_v3

    # Überprüfe Versionsnummern
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM project_calculations WHERE id = ?",
                   (calc_id_v1))
    assert cursor.fetchone()['version'] == 1

    cursor.execute("SELECT version FROM project_calculations WHERE id = ?",
                   (calc_id_v2))
    assert cursor.fetchone()['version'] == 2

    cursor.execute("SELECT version FROM project_calculations WHERE id = ?",
                   (calc_id_v3))
    assert cursor.fetchone()['version'] == 3

    conn.close()
    print("Test save_calculation_versioning bestanden")


def test_get_calculations_for_project():
    """Test: Alle Berechnungen für ein Projekt abrufen"""
    conn = setup_test_db()
    from crm.integration import calculation_bridge

    # Setup - Speichere drei Berechnungen
    with patch.object(calculation_bridge, 'get_db_connection', return_value=conn):
        with patch.object(calculation_bridge, 'ensure_project_calculations_table'):
            for i in range(3):
                calculation_bridge.save_calculation_to_project(
                    project_id=1, customer_id=1,
                    calculation_data={'version': i + 1},
                    calculation_type='pv'
                )

            # Execute
            calculations = calculation_bridge.get_calculations_for_project(
                project_id=1
            )

    # Assert
    assert len(calculations) == 3
    assert calculations[0]['version'] == 3  # Neueste zuerst
    assert calculations[1]['version'] == 2
    assert calculations[2]['version'] == 1

    conn.close()
    print("Test get_calculations_for_project bestanden")


def test_set_main_offer():
    """Test: Berechnung als Hauptangebot markieren"""
    conn = setup_test_db()
    from crm.integration import calculation_bridge

    # Setup - Speichere drei Berechnungen
    with patch.object(calculation_bridge, 'get_db_connection', return_value=conn):
        with patch.object(calculation_bridge, 'ensure_project_calculations_table'):
            calc_id_1 = calculation_bridge.save_calculation_to_project(
                project_id=1, customer_id=1,
                calculation_data={'v': 1}, calculation_type='pv'
            )
            calc_id_2 = calculation_bridge.save_calculation_to_project(
                project_id=1, customer_id=1,
                calculation_data={'v': 2}, calculation_type='pv'
            )
            calc_id_3 = calculation_bridge.save_calculation_to_project(
                project_id=1, customer_id=1,
                calculation_data={'v': 3}, calculation_type='pv'
            )

            # Execute - Markiere zweite als Hauptangebot
            success = calculation_bridge.set_main_offer(calc_id_2, project_id=1)

    # Assert
    assert success is True

    # Überprüfe in Datenbank
    cursor = conn.cursor()
    cursor.execute(
        "SELECT is_main_offer FROM project_calculations WHERE id = ?",
        (calc_id_1)
    )
    assert cursor.fetchone()['is_main_offer'] == 0

    cursor.execute(
        "SELECT is_main_offer FROM project_calculations WHERE id = ?",
        (calc_id_2)
    )
    assert cursor.fetchone()['is_main_offer'] == 1

    cursor.execute(
        "SELECT is_main_offer FROM project_calculations WHERE id = ?",
        (calc_id_3)
    )
    assert cursor.fetchone()['is_main_offer'] == 0

    conn.close()
    print("Test set_main_offer bestanden")


def test_compare_calculations():
    """Test: Zwei Berechnungen vergleichen"""
    conn = setup_test_db()
    from crm.integration import calculation_bridge

    # Setup - Zwei Berechnungen mit unterschiedlichen Werten
    calc_data_1 = {
        'annual_pv_production_kwh': 8000.0,
        'total_investment_netto': 15000.0,
        'annual_total_savings_euro': 1000.0,
        'payback_period_years': 15.0,
    }

    calc_data_2 = {
        'annual_pv_production_kwh': 9000.0,
        'total_investment_netto': 16000.0,
        'annual_total_savings_euro': 1200.0,
        'payback_period_years': 13.0,
    }

    with patch.object(calculation_bridge, 'get_db_connection', return_value=conn):
        with patch.object(calculation_bridge, 'ensure_project_calculations_table'):
            calc_id_1 = calculation_bridge.save_calculation_to_project(
                project_id=1, customer_id=1,
                calculation_data=calc_data_1, calculation_type='pv'
            )
            calc_id_2 = calculation_bridge.save_calculation_to_project(
                project_id=1, customer_id=1,
                calculation_data=calc_data_2, calculation_type='pv'
            )

            # Execute
            comparison = calculation_bridge.compare_calculations(
                calc_id_1, calc_id_2
            )

    # Assert - Struktur
    assert 'calc1' in comparison
    assert 'calc2' in comparison
    assert 'differences' in comparison

    # Assert - Unterschiede
    assert 'annual_pv_production_kwh' in comparison['differences']
    diff_production = comparison['differences']['annual_pv_production_kwh']
    assert diff_production['absolute'] == 1000.0
    assert diff_production['percent'] == 12.5

    assert 'annual_total_savings_euro' in comparison['differences']
    diff_savings = comparison['differences']['annual_total_savings_euro']
    assert diff_savings['absolute'] == 200.0
    assert diff_savings['percent'] == 20.0

    conn.close()
    print("Test compare_calculations bestanden")


def test_integration_full_workflow():
    """Test: Vollständiger Workflow"""
    conn = setup_test_db()
    from crm.integration import calculation_bridge

    with patch.object(calculation_bridge, 'get_db_connection', return_value=conn):
        with patch.object(calculation_bridge, 'ensure_project_calculations_table'):
            # Schritt 1: Erste Berechnung speichern
            calc_data_v1 = {
                'annual_pv_production_kwh': 8000.0,
                'total_investment_netto': 15000.0,
            }
            calc_id_v1 = calculation_bridge.save_calculation_to_project(
                project_id=1, customer_id=1,
                calculation_data=calc_data_v1, calculation_type='pv',
                created_by='Berater A', notes='Erste Variante'
            )
            assert calc_id_v1 is not None

            # Schritt 2: Zweite Berechnung speichern
            calc_data_v2 = {
                'annual_pv_production_kwh': 9000.0,
                'total_investment_netto': 16000.0,
            }
            calc_id_v2 = calculation_bridge.save_calculation_to_project(
                project_id=1, customer_id=1,
                calculation_data=calc_data_v2, calculation_type='pv',
                created_by='Berater A', notes='Optimierte Variante'
            )
            assert calc_id_v2 is not None

            # Schritt 3: Alle Berechnungen abrufen
            all_calcs = calculation_bridge.get_calculations_for_project(
                project_id=1
            )
            assert len(all_calcs) == 2
            assert all_calcs[0]['version'] == 2  # Neueste zuerst

            # Schritt 4: Zweite als Hauptangebot markieren
            success = calculation_bridge.set_main_offer(calc_id_v2, project_id=1)
            assert success is True

            # Schritt 5: Hauptangebot abrufen
            main_offer = calculation_bridge.get_main_offer(project_id=1)
            assert main_offer is not None
            assert main_offer['id'] == calc_id_v2

            # Schritt 6: Berechnungen vergleichen
            comparison = calculation_bridge.compare_calculations(
                calc_id_v1, calc_id_v2
            )
            assert 'differences' in comparison
            assert len(comparison['differences']) > 0

            # Schritt 7: Erste Berechnung löschen
            delete_success = calculation_bridge.delete_calculation(calc_id_v1)
            assert delete_success is True

            # Schritt 8: Nur noch eine Berechnung existiert
            remaining_calcs = calculation_bridge.get_calculations_for_project(
                project_id=1
            )
            assert len(remaining_calcs) == 1

    conn.close()
    print("Test integration_full_workflow bestanden")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  Unit Tests für Calculation Bridge (Task 2.1)")
    print("="*70 + "\n")

    test_count = 0
    passed_count = 0

    tests = [
        ("Grundlegendes Speichern", test_save_calculation_basic),
        ("Automatische Versionierung", test_save_calculation_versioning),
        ("Alle Berechnungen abrufen", test_get_calculations_for_project),
        ("Hauptangebot setzen", test_set_main_offer),
        ("Berechnungen vergleichen", test_compare_calculations),
        ("Vollständiger Workflow", test_integration_full_workflow),
    ]

    for test_name, test_func in tests:
        test_count += 1
        try:
            print(f"Test {test_count}/{len(tests)}: {test_name}...", end=" ")
            test_func()
            passed_count += 1
        except AssertionError as e:
            print(f"\nFEHLGESCHLAGEN: {e}\n")
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"\nFEHLER: {e}\n")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print(f"  Ergebnis: {passed_count}/{test_count} Tests bestanden")
    if passed_count == test_count:
        print("  ALLE TESTS ERFOLGREICH!")
    else:
        print(f"  {test_count - passed_count} Test(s) fehlgeschlagen")
    print("="*70 + "\n")
