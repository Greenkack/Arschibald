"""
Unit Tests für Data Input Bridge

Testet die vollständige Datenextraktion, Duplikatserkennung und Fehlerbehandlung.

Führe aus mit: python -m pytest crm/integration/test_data_input_bridge.py -v
"""

import sqlite3
from datetime import datetime
import sys
from unittest.mock import MagicMock

# Mock streamlit für Tests
class MockSessionState(dict):
    """Mock für st.session_state"""
    pass

# Simuliere streamlit import
sys.modules['streamlit'] = MagicMock()
import streamlit as st
st.session_state = MockSessionState()

from crm.integration.data_input_bridge import (
    extract_customer_data_from_session,
    extract_project_data_from_session,
    check_duplicate_customer,
    validate_required_fields,
    get_data_preview_summary,
)


def test_extract_customer_data_complete():
    """Test: Vollständige Kundenextraktion aus Session State"""
    # Setup - Vollständige Kundendaten
    st.session_state['project_data'] = {
        'customer_data': {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'salutation': 'Herr',
            'title': 'Dr.',
            'company_name': 'Musterfirma GmbH',
            'num_persons': 4,
            'address': 'Musterstraße',
            'house_number': '123',
            'zip_code': '10115',
            'city': 'Berlin',
            'state': 'Berlin',
            'region': 'Nord',
            'full_address': 'Musterstraße 123, 10115 Berlin',
            'email': 'max@example.com',
            'phone_landline': '030-12345678',
            'phone_mobile': '0170-1234567',
            'income_tax_rate_percent': 30.0,
            'type': 'Gewerbe',
        }
    }
    
    # Execute
    customer_data = extract_customer_data_from_session()
    
    # Assert - Alle Felder korrekt extrahiert
    assert customer_data['first_name'] == 'Max'
    assert customer_data['last_name'] == 'Mustermann'
    assert customer_data['salutation'] == 'Herr'
    assert customer_data['title'] == 'Dr.'
    assert customer_data['company_name'] == 'Musterfirma GmbH'
    assert customer_data['num_persons'] == 4
    assert customer_data['address'] == 'Musterstraße'
    assert customer_data['house_number'] == '123'
    assert customer_data['zip_code'] == '10115'
    assert customer_data['city'] == 'Berlin'
    assert customer_data['state'] == 'Berlin'
    assert customer_data['region'] == 'Nord'
    assert customer_data['full_address'] == 'Musterstraße 123, 10115 Berlin'
    assert customer_data['email'] == 'max@example.com'
    assert customer_data['phone_landline'] == '030-12345678'
    assert customer_data['phone_mobile'] == '0170-1234567'
    assert customer_data['income_tax_rate_percent'] == 30.0
    assert customer_data['type'] == 'Gewerbe'
    assert 'creation_date' in customer_data
    assert 'last_updated' in customer_data
    print("Test extract_customer_data_complete bestanden")


def test_extract_customer_data_minimal():
    """Test: Kundenextraktion mit minimalen Daten"""
    # Setup - Nur Pflichtfelder
    st.session_state['project_data'] = {
        'customer_data': {
            'first_name': 'Anna',
            'last_name': 'Schmidt',
        }
    }
    
    # Execute
    customer_data = extract_customer_data_from_session()
    
    # Assert
    assert customer_data['first_name'] == 'Anna'
    assert customer_data['last_name'] == 'Schmidt'
    assert customer_data['email'] == ''
    assert customer_data['num_persons'] == 1  # Default
    assert customer_data['type'] == 'Privat'  # Default
    print("Test extract_customer_data_minimal bestanden")


def test_extract_customer_data_whitespace_trimming():
    """Test: Whitespace wird korrekt entfernt"""
    # Setup - Daten mit Whitespace
    st.session_state['project_data'] = {
        'customer_data': {
            'first_name': '  Max  ',
            'last_name': '  Mustermann  ',
            'email': '  max@example.com  ',
            'city': '  Berlin  ',
        }
    }
    
    # Execute
    customer_data = extract_customer_data_from_session()
    
    # Assert - Whitespace entfernt
    assert customer_data['first_name'] == 'Max'
    assert customer_data['last_name'] == 'Mustermann'
    assert customer_data['email'] == 'max@example.com'
    assert customer_data['city'] == 'Berlin'
    print("Test extract_customer_data_whitespace_trimming bestanden")


def test_extract_customer_data_missing_names_fallback():
    """Test: Fallback für fehlende Namen"""
    # Setup - Fehlende Namen, aber Firmenname vorhanden
    st.session_state['project_data'] = {
        'customer_data': {
            'company_name': 'Musterfirma GmbH',
        }
    }
    
    # Execute
    customer_data = extract_customer_data_from_session()
    
    # Assert - Firmenname als Fallback
    assert customer_data['first_name'] == 'Musterfirma GmbH'
    assert customer_data['last_name'] == 'Musterfirma GmbH'
    print("Test extract_customer_data_missing_names_fallback bestanden")


def test_extract_customer_data_empty_session():
    """Test: Leerer Session State"""
    # Setup - Leerer Session State
    st.session_state.clear()
    
    # Execute
    customer_data = extract_customer_data_from_session()
    
    # Assert - Defaults werden verwendet
    assert customer_data['first_name'] == 'Interessent'
    assert customer_data['last_name'] == 'Unbekannt'
    assert customer_data['num_persons'] == 1
    print("Test extract_customer_data_empty_session bestanden")


def test_extract_project_data_complete():
    """Test: Vollständige Projektextraktion aus Session State"""
    # Setup - Vollständige Projektdaten
    st.session_state['project_data'] = {
        'project_details': {
            'project_name': 'Test PV-Anlage',
            'project_status': 'Angebot',
            'anlage_type': 'Neuanlage',
            'feed_in_type': 'Volleinspeisung',
            'roof_type': 'Satteldach',
            'roof_covering_type': 'Ziegel',
            'free_roof_area_sqm': 50.0,
            'roof_orientation': 'Süd',
            'roof_inclination_deg': 35,
            'building_height_gt_7m': True,
            'annual_consumption_kwh': 4500.0,
            'costs_household_euro_mo': 120.0,
            'annual_heating_kwh': 8000.0,
            'costs_heating_euro_mo': 200.0,
            'module_quantity': 20,
            'selected_module_id': 'MOD-001',
            'selected_inverter_id': 'INV-001',
            'include_storage': True,
            'selected_storage_id': 'BAT-001',
            'selected_storage_storage_power_kw': 10.0,
            'include_additional_components': True,
            'selected_wallbox_id': 'WB-001',
            'selected_ems_id': 'EMS-001',
            'selected_optimizer_id': 'OPT-001',
            'selected_carport_id': 'CAR-001',
            'selected_notstrom_id': 'NOT-001',
            'selected_tierabwehr_id': 'TIER-001',
            'visualize_roof_in_pdf': True,
            'latitude': 52.5200,
            'longitude': 13.4050,
        }
    }
    
    # Execute
    project_data = extract_project_data_from_session()
    
    # Assert - Alle Felder korrekt extrahiert
    assert project_data['project_name'] == 'Test PV-Anlage'
    assert project_data['project_status'] == 'Angebot'
    assert project_data['anlage_type'] == 'Neuanlage'
    assert project_data['feed_in_type'] == 'Volleinspeisung'
    assert project_data['roof_type'] == 'Satteldach'
    assert project_data['roof_covering_type'] == 'Ziegel'
    assert project_data['free_roof_area_sqm'] == 50.0
    assert project_data['roof_orientation'] == 'Süd'
    assert project_data['roof_inclination_deg'] == 35
    assert project_data['building_height_gt_7m'] == 1
    assert project_data['annual_consumption_kwh'] == 4500.0
    assert project_data['costs_household_euro_mo'] == 120.0
    assert project_data['annual_heating_kwh'] == 8000.0
    assert project_data['costs_heating_euro_mo'] == 200.0
    assert project_data['module_quantity'] == 20
    assert project_data['selected_module_id'] == 'MOD-001'
    assert project_data['selected_inverter_id'] == 'INV-001'
    assert project_data['include_storage'] == 1
    assert project_data['selected_storage_id'] == 'BAT-001'
    assert project_data['selected_storage_storage_power_kw'] == 10.0
    assert project_data['include_additional_components'] == 1
    assert project_data['selected_wallbox_id'] == 'WB-001'
    assert project_data['visualize_roof_in_pdf'] == 1
    assert project_data['latitude'] == 52.5200
    assert project_data['longitude'] == 13.4050
    assert 'creation_date' in project_data
    assert 'last_updated' in project_data
    print("Test extract_project_data_complete bestanden")


def test_extract_project_data_consumption_fallback():
    """Test: Verbrauchsdaten aus verschiedenen Quellen"""
    # Setup - Verbrauchsdaten in consumption_data statt project_details
    st.session_state['project_data'] = {
        'project_details': {
            'project_name': 'Test Projekt',
        },
        'consumption_data': {
            'annual_consumption': 5000.0,
            'consumption_household_kwh_yr': 4800.0,
            'costs_household_euro_mo': 150.0,
            'consumption_heating_kwh_yr': 9000.0,
            'costs_heating_euro_mo': 250.0,
        }
    }
    
    # Execute
    project_data = extract_project_data_from_session()
    
    # Assert - Fallback funktioniert
    assert project_data['annual_consumption_kwh'] == 5000.0
    assert project_data['costs_household_euro_mo'] == 150.0
    assert project_data['annual_heating_kwh'] == 9000.0
    assert project_data['costs_heating_euro_mo'] == 250.0
    print("Test extract_project_data_consumption_fallback bestanden")


def test_extract_project_data_auto_name_generation():
    """Test: Automatische Projektname-Generierung"""
    # Setup - Kein Projektname
    st.session_state['project_data'] = {
        'project_details': {}
    }
    
    # Execute
    project_data = extract_project_data_from_session()
    
    # Assert - Name wurde generiert
    assert 'Projekt' in project_data['project_name']
    assert len(project_data['project_name']) > 10  # Enthält Datum/Zeit
    print("Test extract_project_data_auto_name_generation bestanden")


def test_extract_project_data_empty_session():
    """Test: Leerer Session State für Projekt"""
    # Setup - Leerer Session State
    st.session_state.clear()
    
    # Execute
    project_data = extract_project_data_from_session()
    
    # Assert - Defaults werden verwendet
    assert 'Projekt' in project_data['project_name']
    assert project_data['project_status'] == 'Angebot'
    assert project_data['anlage_type'] == 'Neuanlage'
    assert project_data['feed_in_type'] == 'Teileinspeisung'
    print("Test extract_project_data_empty_session bestanden")


def test_validate_required_fields_valid():
    """Test: Validierung mit allen Pflichtfeldern"""
    customer_data = {
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'email': 'max@example.com',
    }
    
    is_valid, missing = validate_required_fields(customer_data)
    
    assert is_valid is True
    assert len(missing) == 0
    print("Test validate_required_fields_valid bestanden")


def test_validate_required_fields_missing_first_name():
    """Test: Fehlender Vorname"""
    customer_data = {
        'first_name': '',
        'last_name': 'Mustermann',
    }
    
    is_valid, missing = validate_required_fields(customer_data)
    
    assert is_valid is False
    assert len(missing) == 1
    assert 'Vorname' in missing
    print("Test validate_required_fields_missing_first_name bestanden")


def test_validate_required_fields_missing_last_name():
    """Test: Fehlender Nachname"""
    customer_data = {
        'first_name': 'Max',
        'last_name': '',
    }
    
    is_valid, missing = validate_required_fields(customer_data)
    
    assert is_valid is False
    assert len(missing) == 1
    assert 'Nachname' in missing
    print("Test validate_required_fields_missing_last_name bestanden")


def test_validate_required_fields_missing_both():
    """Test: Beide Pflichtfelder fehlen"""
    customer_data = {
        'first_name': '',
        'last_name': '',
    }
    
    is_valid, missing = validate_required_fields(customer_data)
    
    assert is_valid is False
    assert len(missing) == 2
    assert 'Vorname' in missing
    assert 'Nachname' in missing
    print("Test validate_required_fields_missing_both bestanden")


def test_validate_required_fields_whitespace_only():
    """Test: Nur Whitespace in Pflichtfeldern"""
    customer_data = {
        'first_name': '   ',
        'last_name': '   ',
    }
    
    is_valid, missing = validate_required_fields(customer_data)
    
    assert is_valid is False
    assert len(missing) == 2
    print("Test validate_required_fields_whitespace_only bestanden")


def test_validate_required_fields_none_values():
    """Test: None-Werte in Pflichtfeldern"""
    customer_data = {
        'first_name': None,
        'last_name': None,
    }
    
    is_valid, missing = validate_required_fields(customer_data)
    
    assert is_valid is False
    assert len(missing) == 2
    print("Test validate_required_fields_none_values bestanden")


def test_check_duplicate_customer_exists():
    """Test: Duplikatsprüfung - Kunde existiert"""
    # Setup: In-Memory-Datenbank
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Erstelle Testtabelle
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )
    """)
    
    # Füge Testkunden hinzu
    cursor.execute("""
        INSERT INTO customers (first_name, last_name, email)
        VALUES ('Max', 'Mustermann', 'max@example.com')
    """)
    conn.commit()
    
    # Test: Existierender Kunde
    existing = check_duplicate_customer(conn, 'max@example.com')
    assert existing is not None
    assert existing['email'] == 'max@example.com'
    assert existing['first_name'] == 'Max'
    assert existing['last_name'] == 'Mustermann'
    
    conn.close()
    print("Test check_duplicate_customer_exists bestanden")


def test_check_duplicate_customer_not_exists():
    """Test: Duplikatsprüfung - Kunde existiert nicht"""
    # Setup: In-Memory-Datenbank
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )
    """)
    conn.commit()
    
    # Test: Nicht existierender Kunde
    not_existing = check_duplicate_customer(conn, 'other@example.com')
    assert not_existing is None
    
    conn.close()
    print("Test check_duplicate_customer_not_exists bestanden")


def test_check_duplicate_customer_case_insensitive():
    """Test: Duplikatsprüfung ist case-insensitive"""
    # Setup: In-Memory-Datenbank
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )
    """)
    
    cursor.execute("""
        INSERT INTO customers (first_name, last_name, email)
        VALUES ('Max', 'Mustermann', 'max@example.com')
    """)
    conn.commit()
    
    # Test: Case-insensitive Suche
    existing_upper = check_duplicate_customer(conn, 'MAX@EXAMPLE.COM')
    assert existing_upper is not None
    
    existing_mixed = check_duplicate_customer(conn, 'Max@Example.Com')
    assert existing_mixed is not None
    
    conn.close()
    print("Test check_duplicate_customer_case_insensitive bestanden")


def test_check_duplicate_customer_empty_email():
    """Test: Duplikatsprüfung mit leerer E-Mail"""
    # Setup: In-Memory-Datenbank
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )
    """)
    conn.commit()
    
    # Test: Leere E-Mail
    result = check_duplicate_customer(conn, '')
    assert result is None
    
    # Test: None E-Mail
    result = check_duplicate_customer(conn, None)
    assert result is None
    
    # Test: Whitespace E-Mail
    result = check_duplicate_customer(conn, '   ')
    assert result is None
    
    conn.close()
    print("Test check_duplicate_customer_empty_email bestanden")


def test_check_duplicate_customer_whitespace_trimming():
    """Test: Duplikatsprüfung trimmt Whitespace"""
    # Setup: In-Memory-Datenbank
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )
    """)
    
    cursor.execute("""
        INSERT INTO customers (first_name, last_name, email)
        VALUES ('Max', 'Mustermann', 'max@example.com')
    """)
    conn.commit()
    
    # Test: E-Mail mit Whitespace
    existing = check_duplicate_customer(conn, '  max@example.com  ')
    assert existing is not None
    assert existing['email'] == 'max@example.com'
    
    conn.close()
    print("Test check_duplicate_customer_whitespace_trimming bestanden")


def test_check_duplicate_customer_error_handling():
    """Test: Fehlerbehandlung bei ungültiger Datenbank"""
    # Setup: Geschlossene Verbindung
    conn = sqlite3.connect(':memory:')
    conn.close()
    
    # Test: Sollte None zurückgeben statt Exception
    result = check_duplicate_customer(conn, 'test@example.com')
    assert result is None
    
    print("Test check_duplicate_customer_error_handling bestanden")


def test_get_data_preview_summary():
    """Test: Vorschau-Zusammenfassung erstellen"""
    # Setup
    customer_data = {
        'salutation': 'Herr',
        'title': 'Dr.',
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'company_name': 'Musterfirma GmbH',
        'address': 'Musterstraße',
        'house_number': '123',
        'zip_code': '10115',
        'city': 'Berlin',
        'email': 'max@example.com',
        'phone_landline': '030-12345678',
        'type': 'Gewerbe',
    }
    
    project_data = {
        'project_name': 'Test PV-Anlage',
        'project_status': 'Angebot',
        'anlage_type': 'Neuanlage',
        'feed_in_type': 'Volleinspeisung',
        'roof_type': 'Satteldach',
        'module_quantity': 20,
        'annual_consumption_kwh': 4500.0,
        'include_storage': 1,
    }
    
    # Execute
    summary = get_data_preview_summary(customer_data, project_data)
    
    # Assert
    assert 'customer' in summary
    assert 'project' in summary
    assert 'counts' in summary
    
    # Customer summary
    assert 'Dr. Max Mustermann' in summary['customer']['name']
    assert summary['customer']['company'] == 'Musterfirma GmbH'
    assert 'Musterstraße 123' in summary['customer']['address']
    assert summary['customer']['email'] == 'max@example.com'
    assert summary['customer']['phone'] == '030-12345678'
    assert summary['customer']['type'] == 'Gewerbe'
    
    # Project summary
    assert summary['project']['name'] == 'Test PV-Anlage'
    assert summary['project']['status'] == 'Angebot'
    assert summary['project']['anlage_type'] == 'Neuanlage'
    assert summary['project']['roof_type'] == 'Satteldach'
    assert summary['project']['module_quantity'] == 20
    assert summary['project']['has_storage'] is True
    
    # Counts
    assert summary['counts']['customer_fields'] > 0
    assert summary['counts']['project_fields'] > 0
    
    print("Test get_data_preview_summary bestanden")


def test_get_data_preview_summary_minimal():
    """Test: Vorschau mit minimalen Daten"""
    # Setup
    customer_data = {
        'first_name': 'Anna',
        'last_name': 'Schmidt',
    }
    
    project_data = {
        'project_name': 'Minimal Projekt',
    }
    
    # Execute
    summary = get_data_preview_summary(customer_data, project_data)
    
    # Assert
    assert 'Anna Schmidt' in summary['customer']['name']
    assert summary['project']['name'] == 'Minimal Projekt'
    assert summary['counts']['customer_fields'] >= 2
    assert summary['counts']['project_fields'] >= 1
    
    print("Test get_data_preview_summary_minimal bestanden")


def test_integration_full_workflow():
    """Test: Vollständiger Workflow - Extraktion, Validierung, Duplikatsprüfung"""
    # Setup: Session State mit vollständigen Daten
    st.session_state['project_data'] = {
        'customer_data': {
            'first_name': 'Integration',
            'last_name': 'Test',
            'email': 'integration@test.com',
            'phone_landline': '030-111111',
            'city': 'Berlin',
            'zip_code': '10115',
        },
        'project_details': {
            'project_name': 'Integration Test Projekt',
            'roof_type': 'Flachdach',
            'module_quantity': 15,
        }
    }
    
    # Setup: Datenbank
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )
    """)
    conn.commit()
    
    # Schritt 1: Daten extrahieren
    customer_data = extract_customer_data_from_session()
    project_data = extract_project_data_from_session()
    
    assert customer_data['first_name'] == 'Integration'
    assert project_data['project_name'] == 'Integration Test Projekt'
    
    # Schritt 2: Pflichtfelder validieren
    is_valid, missing = validate_required_fields(customer_data)
    assert is_valid is True
    assert len(missing) == 0
    
    # Schritt 3: Duplikat prüfen
    duplicate = check_duplicate_customer(conn, customer_data['email'])
    assert duplicate is None  # Kein Duplikat
    
    # Schritt 4: Vorschau erstellen
    summary = get_data_preview_summary(customer_data, project_data)
    assert 'Integration Test' in summary['customer']['name']
    assert summary['project']['name'] == 'Integration Test Projekt'
    
    conn.close()
    print("Test integration_full_workflow bestanden")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  Unit Tests für Data Input Bridge (Task 1.1)")
    print("="*70 + "\n")
    
    test_count = 0
    passed_count = 0
    
    tests = [
        # Kundenextraktion Tests
        ("Vollständige Kundenextraktion", test_extract_customer_data_complete),
        ("Minimale Kundenextraktion", test_extract_customer_data_minimal),
        ("Whitespace Trimming", test_extract_customer_data_whitespace_trimming),
        ("Fallback für fehlende Namen", test_extract_customer_data_missing_names_fallback),
        ("Leerer Session State", test_extract_customer_data_empty_session),
        
        # Projektextraktion Tests
        ("Vollständige Projektextraktion", test_extract_project_data_complete),
        ("Verbrauchsdaten Fallback", test_extract_project_data_consumption_fallback),
        ("Auto-Projektname", test_extract_project_data_auto_name_generation),
        ("Leerer Session State (Projekt)", test_extract_project_data_empty_session),
        
        # Validierung Tests
        ("Validierung - Gültig", test_validate_required_fields_valid),
        ("Validierung - Fehlender Vorname", test_validate_required_fields_missing_first_name),
        ("Validierung - Fehlender Nachname", test_validate_required_fields_missing_last_name),
        ("Validierung - Beide fehlen", test_validate_required_fields_missing_both),
        ("Validierung - Nur Whitespace", test_validate_required_fields_whitespace_only),
        ("Validierung - None-Werte", test_validate_required_fields_none_values),
        
        # Duplikatsprüfung Tests
        ("Duplikat existiert", test_check_duplicate_customer_exists),
        ("Duplikat existiert nicht", test_check_duplicate_customer_not_exists),
        ("Case-insensitive Suche", test_check_duplicate_customer_case_insensitive),
        ("Leere E-Mail", test_check_duplicate_customer_empty_email),
        ("Whitespace Trimming (Duplikat)", test_check_duplicate_customer_whitespace_trimming),
        ("Fehlerbehandlung", test_check_duplicate_customer_error_handling),
        
        # Vorschau Tests
        ("Vorschau-Zusammenfassung", test_get_data_preview_summary),
        ("Vorschau minimal", test_get_data_preview_summary_minimal),
        
        # Integration Test
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
        except Exception as e:
            print(f"\nFEHLER: {e}\n")
    
    print("\n" + "="*70)
    print(f"  Ergebnis: {passed_count}/{test_count} Tests bestanden")
    if passed_count == test_count:
        print("  ALLE TESTS ERFOLGREICH!")
    else:
        print(f"  {test_count - passed_count} Test(s) fehlgeschlagen")
    print("="*70 + "\n")
