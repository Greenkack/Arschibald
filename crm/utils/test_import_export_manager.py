# crm/utils/test_import_export_manager.py
"""
Unit Tests für Import/Export Manager

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import os
import sqlite3
import tempfile
import pytest
from typing import Generator

# Import der zu testenden Funktionen
from crm.utils.import_export_manager import (
    export_customers_to_csv,
    export_customers_to_excel,
    get_export_statistics,
    parse_csv_for_import,
    parse_excel_for_import,
    get_excel_sheet_names,
    map_import_fields,
    check_duplicate_customer,
    validate_customer_data,
    import_customer,
    import_customers_batch,
    preview_import_data,
    CUSTOMER_FIELDS,
    REQUIRED_FIELDS
)


@pytest.fixture
def test_db() -> Generator[sqlite3.Connection, None, None]:
    """Erstellt eine temporäre Test-Datenbank."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    
    # Customers Tabelle erstellen
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            salutation TEXT,
            title TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            company_name TEXT,
            address TEXT,
            house_number TEXT,
            zip_code TEXT,
            city TEXT,
            state TEXT,
            region TEXT,
            email TEXT,
            phone_landline TEXT,
            phone_mobile TEXT,
            income_tax_rate_percent REAL DEFAULT 0.0,
            creation_date TEXT,
            last_updated TEXT
        )
    """)
    
    # Test-Kunden erstellen
    test_customers = [
        ("Herr", "Dr.", "Max", "Mustermann", "Musterfirma GmbH", "Musterstraße", "1", "12345", "Musterstadt", "Bayern", "Süd", "max@example.com", "089123456", "0171234567", 30.0),
        ("Frau", None, "Erika", "Musterfrau", None, "Testweg", "2", "54321", "Teststadt", "NRW", "West", "erika@example.com", "0221987654", "0162987654", 25.0),
        ("Herr", None, "Hans", "Schmidt", "Schmidt Solar", "Hauptstraße", "10", "67890", "Neustadt", "Hessen", "Mitte", "hans@example.com", None, "0173456789", 35.0),
    ]
    
    for customer in test_customers:
        cursor.execute("""
            INSERT INTO customers (
                salutation, title, first_name, last_name, company_name,
                address, house_number, zip_code, city, state, region,
                email, phone_landline, phone_mobile, income_tax_rate_percent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, customer)
    
    conn.commit()
    
    yield conn
    
    conn.close()
    try:
        os.unlink(db_path)
    except Exception:
        pass


# ============================================================================
# EXPORT TESTS
# ============================================================================

def test_export_customers_to_csv(test_db):
    """Test: CSV-Export aller Kunden"""
    csv_data = export_customers_to_csv(test_db)
    
    assert csv_data is not None
    assert len(csv_data) > 0
    
    # Prüfe Header
    lines = csv_data.strip().split('\n')
    assert len(lines) == 4  # Header + 3 Kunden
    
    # Prüfe, dass Daten enthalten sind
    assert "Max" in csv_data
    assert "Mustermann" in csv_data
    assert "max@example.com" in csv_data


def test_export_customers_to_csv_with_fields(test_db):
    """Test: CSV-Export mit ausgewählten Feldern"""
    fields = ['first_name', 'last_name', 'email']
    csv_data = export_customers_to_csv(test_db, include_fields=fields)
    
    assert csv_data is not None
    lines = csv_data.strip().split('\n')
    
    # Header sollte nur 3 Felder haben
    header = lines[0].split(',')
    assert len(header) == 3


def test_export_customers_to_csv_with_ids(test_db):
    """Test: CSV-Export bestimmter Kunden"""
    customer_ids = [1, 2]
    csv_data = export_customers_to_csv(test_db, customer_ids=customer_ids)
    
    assert csv_data is not None
    lines = csv_data.strip().split('\n')
    assert len(lines) == 3  # Header + 2 Kunden


def test_export_customers_to_excel(test_db):
    """Test: Excel-Export"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        success = export_customers_to_excel(test_db, tmp_path)
        assert success is True
        assert os.path.exists(tmp_path)
        
        # Prüfe, dass Datei nicht leer ist
        assert os.path.getsize(tmp_path) > 0
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


def test_get_export_statistics(test_db):
    """Test: Export-Statistiken"""
    stats = get_export_statistics(test_db)
    
    assert stats is not None
    assert stats['total_customers'] == 3
    assert stats['customers_with_email'] == 3
    assert stats['customers_with_phone'] == 3
    assert stats['completeness_rate'] == 100.0


# ============================================================================
# IMPORT PARSING TESTS
# ============================================================================

def test_parse_csv_for_import():
    """Test: CSV-Parsing"""
    csv_content = """Vorname,Nachname,E-Mail
Max,Mustermann,max@test.com
Erika,Musterfrau,erika@test.com"""
    
    header, rows, errors = parse_csv_for_import(csv_content)
    
    assert len(errors) == 0
    assert header == ['Vorname', 'Nachname', 'E-Mail']
    assert len(rows) == 2
    assert rows[0] == ['Max', 'Mustermann', 'max@test.com']


def test_parse_csv_empty():
    """Test: Leere CSV"""
    csv_content = ""
    
    header, rows, errors = parse_csv_for_import(csv_content)
    
    assert len(errors) > 0
    assert "keinen Header" in errors[0]


def test_parse_excel_for_import():
    """Test: Excel-Parsing"""
    # Erstelle temporäre Excel-Datei
    import pandas as pd
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # Erstelle Test-Excel
        df = pd.DataFrame({
            'Vorname': ['Max', 'Erika'],
            'Nachname': ['Mustermann', 'Musterfrau'],
            'E-Mail': ['max@test.com', 'erika@test.com']
        })
        df.to_excel(tmp_path, index=False, engine='openpyxl')
        
        # Parse
        header, rows, errors = parse_excel_for_import(tmp_path)
        
        assert len(errors) == 0
        assert header == ['Vorname', 'Nachname', 'E-Mail']
        assert len(rows) == 2
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


def test_get_excel_sheet_names():
    """Test: Excel Sheet-Namen abrufen"""
    import pandas as pd
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # Erstelle Excel mit mehreren Sheets
        with pd.ExcelWriter(tmp_path, engine='openpyxl') as writer:
            pd.DataFrame({'A': [1]}).to_excel(writer, sheet_name='Sheet1', index=False)
            pd.DataFrame({'B': [2]}).to_excel(writer, sheet_name='Sheet2', index=False)
        
        sheet_names = get_excel_sheet_names(tmp_path)
        
        assert len(sheet_names) == 2
        assert 'Sheet1' in sheet_names
        assert 'Sheet2' in sheet_names
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


# ============================================================================
# FIELD MAPPING TESTS
# ============================================================================

def test_map_import_fields_automatic():
    """Test: Automatisches Feld-Mapping"""
    import_header = ['Vorname', 'Nachname', 'E-Mail', 'PLZ', 'Stadt']
    
    mapping = map_import_fields(import_header)
    
    assert mapping['Vorname'] == 'first_name'
    assert mapping['Nachname'] == 'last_name'
    assert mapping['E-Mail'] == 'email'
    assert mapping['PLZ'] == 'zip_code'
    assert mapping['Stadt'] == 'city'


def test_map_import_fields_english():
    """Test: Mapping mit englischen Feldnamen"""
    import_header = ['first_name', 'last_name', 'email', 'phone']
    
    mapping = map_import_fields(import_header)
    
    assert mapping['first_name'] == 'first_name'
    assert mapping['last_name'] == 'last_name'
    assert mapping['email'] == 'email'
    assert 'phone' in mapping  # Sollte phone_landline oder phone_mobile sein


def test_map_import_fields_manual():
    """Test: Manuelles Feld-Mapping"""
    import_header = ['Name', 'Surname', 'Mail']
    manual_mapping = {
        'Name': 'first_name',
        'Surname': 'last_name',
        'Mail': 'email'
    }
    
    mapping = map_import_fields(import_header, manual_mapping)
    
    assert mapping == manual_mapping


# ============================================================================
# DUPLICATE CHECK TESTS
# ============================================================================

def test_check_duplicate_customer_by_email(test_db):
    """Test: Duplikatserkennung über E-Mail"""
    customer_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'max@example.com'  # Existiert bereits
    }
    
    duplicate = check_duplicate_customer(test_db, customer_data)
    
    assert duplicate is not None
    assert duplicate['email'] == 'max@example.com'
    assert duplicate['first_name'] == 'Max'


def test_check_duplicate_customer_by_phone(test_db):
    """Test: Duplikatserkennung über Telefon"""
    customer_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'phone_mobile': '0171234567'  # Existiert bereits
    }
    
    duplicate = check_duplicate_customer(test_db, customer_data)
    
    assert duplicate is not None
    assert duplicate['phone_mobile'] == '0171234567'


def test_check_duplicate_customer_by_name_zip(test_db):
    """Test: Duplikatserkennung über Name + PLZ"""
    customer_data = {
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'zip_code': '12345'
    }
    
    duplicate = check_duplicate_customer(test_db, customer_data)
    
    assert duplicate is not None
    assert duplicate['first_name'] == 'Max'
    assert duplicate['last_name'] == 'Mustermann'


def test_check_duplicate_customer_no_duplicate(test_db):
    """Test: Kein Duplikat gefunden"""
    customer_data = {
        'first_name': 'Neu',
        'last_name': 'Kunde',
        'email': 'neu@example.com'
    }
    
    duplicate = check_duplicate_customer(test_db, customer_data)
    
    assert duplicate is None


# ============================================================================
# VALIDATION TESTS
# ============================================================================

def test_validate_customer_data_valid():
    """Test: Validierung gültiger Daten"""
    customer_data = {
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'email': 'max@example.com',
        'zip_code': '12345',
        'income_tax_rate_percent': 30.0
    }
    
    errors = validate_customer_data(customer_data)
    
    assert len(errors) == 0


def test_validate_customer_data_missing_required():
    """Test: Validierung mit fehlenden Pflichtfeldern"""
    customer_data = {
        'first_name': 'Max'
        # last_name fehlt
    }
    
    errors = validate_customer_data(customer_data)
    
    assert len(errors) > 0
    assert any('Nachname' in error for error in errors)


def test_validate_customer_data_invalid_email():
    """Test: Validierung ungültiger E-Mail"""
    customer_data = {
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'email': 'invalid-email'
    }
    
    errors = validate_customer_data(customer_data)
    
    assert len(errors) > 0
    assert any('E-Mail' in error for error in errors)


def test_validate_customer_data_invalid_zip():
    """Test: Validierung ungültiger PLZ"""
    customer_data = {
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'zip_code': '123'  # Zu kurz
    }
    
    errors = validate_customer_data(customer_data)
    
    assert len(errors) > 0
    assert any('PLZ' in error for error in errors)


def test_validate_customer_data_invalid_tax_rate():
    """Test: Validierung ungültiger Steuersatz"""
    customer_data = {
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'income_tax_rate_percent': 150  # Zu hoch
    }
    
    errors = validate_customer_data(customer_data)
    
    assert len(errors) > 0
    assert any('Steuersatz' in error for error in errors)



# ============================================================================
# IMPORT TESTS
# ============================================================================

def test_import_customer_success(test_db):
    """Test: Erfolgreicher Kunden-Import"""
    customer_data = {
        'first_name': 'Neu',
        'last_name': 'Kunde',
        'email': 'neu@example.com',
        'phone_mobile': '0170123456',
        'zip_code': '99999',
        'city': 'Neustadt'
    }
    
    success, customer_id, message = import_customer(test_db, customer_data, 'skip')
    
    assert success is True
    assert customer_id is not None
    assert customer_id > 0
    assert 'erfolgreich' in message


def test_import_customer_duplicate_skip(test_db):
    """Test: Import mit Duplikat (skip)"""
    customer_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'max@example.com'  # Existiert bereits
    }
    
    success, customer_id, message = import_customer(test_db, customer_data, 'skip')
    
    assert success is False
    assert 'existiert bereits' in message


def test_import_customer_duplicate_update(test_db):
    """Test: Import mit Duplikat (update)"""
    customer_data = {
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'email': 'max@example.com',
        'city': 'Neue Stadt'  # Neue Daten
    }
    
    success, customer_id, message = import_customer(test_db, customer_data, 'update')
    
    assert success is True
    assert 'aktualisiert' in message
    
    # Prüfe, dass Daten aktualisiert wurden
    cursor = test_db.cursor()
    cursor.execute("SELECT city FROM customers WHERE id = ?", (customer_id,))
    result = cursor.fetchone()
    assert result[0] == 'Neue Stadt'


def test_import_customer_duplicate_create(test_db):
    """Test: Import mit Duplikat (create)"""
    customer_data = {
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'email': 'max@example.com'  # Existiert bereits
    }
    
    # Zähle Kunden vor Import
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers")
    count_before = cursor.fetchone()[0]
    
    success, customer_id, message = import_customer(test_db, customer_data, 'create')
    
    assert success is True
    
    # Zähle Kunden nach Import
    cursor.execute("SELECT COUNT(*) FROM customers")
    count_after = cursor.fetchone()[0]
    
    assert count_after == count_before + 1


def test_import_customer_validation_error(test_db):
    """Test: Import mit Validierungsfehler"""
    customer_data = {
        'first_name': 'Test'
        # last_name fehlt (Pflichtfeld)
    }
    
    success, customer_id, message = import_customer(test_db, customer_data, 'skip')
    
    assert success is False
    assert customer_id is None
    assert 'Pflichtfeld' in message


def test_import_customers_batch(test_db):
    """Test: Batch-Import mehrerer Kunden"""
    rows = [
        ['Kunde1', 'Test1', 'kunde1@test.com', '11111', 'Stadt1'],
        ['Kunde2', 'Test2', 'kunde2@test.com', '22222', 'Stadt2'],
        ['Kunde3', 'Test3', 'kunde3@test.com', '33333', 'Stadt3'],
    ]
    
    field_mapping = {
        'Vorname': 'first_name',
        'Nachname': 'last_name',
        'E-Mail': 'email',
        'PLZ': 'zip_code',
        'Stadt': 'city'
    }
    
    # Mapping muss mit tatsächlichen Spalten übereinstimmen
    # Simuliere Header
    import_header = ['Vorname', 'Nachname', 'E-Mail', 'PLZ', 'Stadt']
    
    stats = import_customers_batch(test_db, rows, field_mapping, 'skip')
    
    assert stats['total'] == 3
    assert stats['success'] == 3
    assert stats['errors'] == 0


def test_import_customers_batch_with_duplicates(test_db):
    """Test: Batch-Import mit Duplikaten"""
    rows = [
        ['Max', 'Mustermann', 'max@example.com', '12345', 'Musterstadt'],  # Duplikat
        ['Neu', 'Kunde', 'neu@test.com', '99999', 'Neustadt'],  # Neu
    ]
    
    field_mapping = {
        'Vorname': 'first_name',
        'Nachname': 'last_name',
        'E-Mail': 'email',
        'PLZ': 'zip_code',
        'Stadt': 'city'
    }
    
    stats = import_customers_batch(test_db, rows, field_mapping, 'skip')
    
    assert stats['total'] == 2
    assert stats['success'] == 1
    assert stats['skipped'] == 1


def test_import_customers_batch_with_errors(test_db):
    """Test: Batch-Import mit Fehlern"""
    rows = [
        ['Kunde1', 'Test1', 'kunde1@test.com', '11111', 'Stadt1'],  # OK
        ['', 'Test2', 'kunde2@test.com', '22222', 'Stadt2'],  # Fehler: Vorname fehlt
        ['Kunde3', 'Test3', 'invalid-email', '33333', 'Stadt3'],  # Fehler: Ungültige E-Mail
    ]
    
    field_mapping = {
        'Vorname': 'first_name',
        'Nachname': 'last_name',
        'E-Mail': 'email',
        'PLZ': 'zip_code',
        'Stadt': 'city'
    }
    
    stats = import_customers_batch(test_db, rows, field_mapping, 'skip')
    
    assert stats['total'] == 3
    assert stats['success'] == 1
    assert stats['errors'] == 2
    assert len(stats['error_details']) == 2


# ============================================================================
# PREVIEW TESTS
# ============================================================================

def test_preview_import_data():
    """Test: Import-Vorschau"""
    rows = [
        ['Max', 'Mustermann', 'max@test.com'],
        ['Erika', 'Musterfrau', 'erika@test.com'],
        ['Hans', 'Schmidt', 'hans@test.com'],
    ]
    
    field_mapping = {
        'Vorname': 'first_name',
        'Nachname': 'last_name',
        'E-Mail': 'email'
    }
    
    preview = preview_import_data(rows, field_mapping, max_rows=2)
    
    assert len(preview) == 2
    assert preview[0]['Vorname'] == 'Max'
    assert preview[0]['Nachname'] == 'Mustermann'
    assert preview[0]['E-Mail'] == 'max@test.com'


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_complete_import_workflow(test_db):
    """Test: Kompletter Import-Workflow"""
    # 1. CSV erstellen
    csv_content = """Vorname,Nachname,E-Mail,PLZ,Stadt
Workflow,Test1,workflow1@test.com,11111,Stadt1
Workflow,Test2,workflow2@test.com,22222,Stadt2"""
    
    # 2. CSV parsen
    header, rows, errors = parse_csv_for_import(csv_content)
    assert len(errors) == 0
    
    # 3. Feld-Mapping
    mapping = map_import_fields(header)
    assert 'Vorname' in mapping
    
    # 4. Vorschau
    preview = preview_import_data(rows, mapping, max_rows=5)
    assert len(preview) == 2
    
    # 5. Import
    stats = import_customers_batch(test_db, rows, mapping, 'skip')
    assert stats['success'] == 2
    assert stats['errors'] == 0
    
    # 6. Prüfe, dass Kunden in DB sind
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers WHERE first_name = 'Workflow'")
    count = cursor.fetchone()[0]
    assert count == 2


def test_complete_export_workflow(test_db):
    """Test: Kompletter Export-Workflow"""
    # 1. Statistiken abrufen
    stats = get_export_statistics(test_db)
    assert stats['total_customers'] == 3
    
    # 2. CSV-Export
    csv_data = export_customers_to_csv(test_db)
    assert len(csv_data) > 0
    
    # 3. Excel-Export
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        success = export_customers_to_excel(test_db, tmp_path)
        assert success is True
        
        # 4. Excel wieder einlesen und prüfen
        header, rows, errors = parse_excel_for_import(tmp_path)
        assert len(errors) == 0
        assert len(rows) == 3
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


if __name__ == "__main__":
    # Tests ausführen
    pytest.main([__file__, "-v"])
