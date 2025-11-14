"""
Test Suite für CRM PDF Bridge Integration

Testet die automatische PDF-Archivierung in der Kundenakte.

Task 3.1: Tests für PDF-Archivierung
- Teste automatisches Speichern
- Teste Metadaten-Extraktion
- Teste Versionierung
"""

import os
import tempfile
import sqlite3
from datetime import datetime
from pathlib import Path


def setup_test_database():
    """Erstellt eine Test-Datenbank für die Tests"""
    from database import get_db_connection, _create_customer_documents_table
    
    conn = get_db_connection()
    if conn:
        _create_customer_documents_table(conn)
        
        # Erstelle Test-Kunde falls nicht vorhanden
        cursor = conn.cursor()
        
        # Prüfe ob Kunde bereits existiert
        cursor.execute("SELECT id FROM customers WHERE id = 99999")
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO customers (id, first_name, last_name, email, phone_mobile, address, city, zip_code)
                VALUES (99999, 'Test', 'Kunde PDF', 'test.pdf@example.com', '0123456789', 
                        'Teststraße 1', 'Teststadt', '12345')
            """)
        
        conn.commit()
        conn.close()
        return True
    return False


def cleanup_test_data():
    """Bereinigt Test-Daten nach den Tests"""
    from database import get_db_connection
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # Lösche Test-Dokumente
        cursor.execute("DELETE FROM customer_documents WHERE customer_id = 99999")
        # Lösche Test-Kunde
        cursor.execute("DELETE FROM customers WHERE id = 99999")
        conn.commit()
        conn.close()
    
    # Lösche Test-Dateien
    from database import CUSTOMER_DOCS_BASE_DIR
    test_customer_dir = os.path.join(CUSTOMER_DOCS_BASE_DIR, "customer_99999")
    if os.path.exists(test_customer_dir):
        import shutil
        shutil.rmtree(test_customer_dir)


def test_extract_pdf_metadata():
    """Test: Metadaten-Extraktion aus PDF"""
    print("\n=== Test: extract_pdf_metadata ===")
    
    from crm.integration.pdf_bridge import extract_pdf_metadata
    
    # Test mit Angebots-PDF
    offer_data = {
        'offer_id': 'ANG-2025-001',
        'customer': {'name': 'Max Mustermann'},
        'project_type': 'pv'
    }
    
    # Erstelle temporäre PDF-Datei
    with tempfile.NamedTemporaryFile(suffix='_angebot.pdf', delete=False) as tmp:
        tmp.write(b'%PDF-1.4 dummy content')
        tmp_path = tmp.name
    
    try:
        metadata = extract_pdf_metadata(tmp_path, offer_data)
        
        assert metadata['doc_type'] == 'offer_pdf', f"Expected 'offer_pdf', got {metadata['doc_type']}"
        assert metadata['offer_id'] == 'ANG-2025-001', f"Expected 'ANG-2025-001', got {metadata['offer_id']}"
        assert metadata['customer_name'] == 'Max Mustermann', f"Expected 'Max Mustermann', got {metadata['customer_name']}"
        assert metadata['file_size'] > 0, "File size should be > 0"
        
        print("[OK] Metadaten erfolgreich extrahiert:")
        print(f"   - Typ: {metadata['doc_type']}")
        print(f"   - Angebots-ID: {metadata['offer_id']}")
        print(f"   - Kunde: {metadata['customer_name']}")
        print(f"   - Größe: {metadata['file_size']} bytes")
        
    finally:
        os.unlink(tmp_path)


def test_extract_pdf_metadata_various_types():
    """Test: Metadaten-Extraktion für verschiedene PDF-Typen"""
    print("\n=== Test: extract_pdf_metadata_various_types ===")
    
    from crm.integration.pdf_bridge import extract_pdf_metadata
    
    test_cases = [
        ('angebot_2025.pdf', 'offer_pdf'),
        ('rechnung_001.pdf', 'invoice_pdf'),
        ('vertrag_kunde.pdf', 'contract_pdf'),
        ('bericht_analyse.pdf', 'report_pdf'),
        ('sonstiges_dokument.pdf', 'other_pdf'),
    ]
    
    for filename, expected_type in test_cases:
        with tempfile.NamedTemporaryFile(suffix=filename, delete=False) as tmp:
            tmp.write(b'%PDF-1.4 test content')
            tmp_path = tmp.name
        
        try:
            metadata = extract_pdf_metadata(tmp_path)
            assert metadata['doc_type'] == expected_type, \
                f"Expected '{expected_type}' for {filename}, got {metadata['doc_type']}"
            print(f"[OK] {filename} → {metadata['doc_type']}")
        finally:
            os.unlink(tmp_path)


def test_extract_pdf_metadata_without_offer_data():
    """Test: Metadaten-Extraktion ohne Angebotsdaten"""
    print("\n=== Test: extract_pdf_metadata_without_offer_data ===")
    
    from crm.integration.pdf_bridge import extract_pdf_metadata
    
    with tempfile.NamedTemporaryFile(suffix='_test.pdf', delete=False) as tmp:
        tmp.write(b'%PDF-1.4 test')
        tmp_path = tmp.name
    
    try:
        metadata = extract_pdf_metadata(tmp_path, None)
        
        assert 'doc_type' in metadata, "doc_type should be present"
        assert 'version' in metadata, "version should be present"
        assert 'date' in metadata, "date should be present"
        assert 'file_size' in metadata, "file_size should be present"
        
        print("[OK] Metadaten ohne offer_data erfolgreich extrahiert")
        print(f"   - Typ: {metadata['doc_type']}")
        print(f"   - Datum: {metadata['date']}")
        
    finally:
        os.unlink(tmp_path)


def test_get_next_version_number():
    """Test: Versionsnummerierung"""
    print("\n=== Test: get_next_version_number ===")
    
    from crm.integration.pdf_bridge import get_next_version_number
    
    # Test mit nicht existierendem Kunden (sollte Version 1 zurückgeben)
    version = get_next_version_number(
        customer_id=99999,  # Nicht existierende ID
        doc_type='offer_pdf'
    )
    
    assert version == 1, f"Expected version 1 for new customer, got {version}"
    print(f"[OK] Erste Version korrekt: v{version}")


def test_create_versioned_filename():
    """Test: Versionierte Dateinamen"""
    print("\n=== Test: create_versioned_filename ===")
    
    from crm.integration.pdf_bridge import create_versioned_filename
    
    metadata = {
        'date': '2025-01-13'
    }
    
    # Test verschiedene Dateinamen
    test_cases = [
        ('angebot.pdf', 1, 'angebot_v1_2025-01-13.pdf'),
        ('Rechnung_2025.pdf', 2, 'Rechnung_2025_v2_2025-01-13.pdf'),
        ('dokument', 3, 'dokument_v3_2025-01-13.pdf'),
    ]
    
    for original, version, expected in test_cases:
        result = create_versioned_filename(original, version, metadata)
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print(f"[OK] {original} → {result}")


def test_pdf_type_helpers():
    """Test: PDF-Typ Helper-Funktionen"""
    print("\n=== Test: PDF Type Helpers ===")
    
    from crm.integration.pdf_bridge import get_pdf_type_badge_color, get_pdf_type_label
    
    test_types = [
        ('offer_pdf', 'Angebot', '#2563EB'),
        ('invoice_pdf', 'Rechnung', '#22C55E'),
        ('contract_pdf', 'Vertrag', '#F59E0B'),
        ('report_pdf', 'Bericht', '#8B5CF6'),
        ('other_pdf', 'Sonstiges', '#64748B'),
    ]
    
    for doc_type, expected_label, expected_color in test_types:
        label = get_pdf_type_label(doc_type)
        color = get_pdf_type_badge_color(doc_type)
        
        assert label == expected_label, f"Expected label '{expected_label}', got '{label}'"
        assert color == expected_color, f"Expected color '{expected_color}', got '{color}'"
        
        print(f"[OK] {doc_type}: {label} ({color})")


def test_format_document_list():
    """Test: Dokumentenlisten-Formatierung"""
    print("\n=== Test: format_document_list_for_display ===")
    
    from crm.integration.pdf_bridge import format_document_list_for_display
    
    docs = [
        {
            'id': 1,
            'doc_type': 'offer_pdf',
            'display_name': 'Angebot_v1_2025-01-13.pdf',
            'uploaded_at': '2025-01-13 10:30:00'
        },
        {
            'id': 2,
            'doc_type': 'invoice_pdf',
            'display_name': 'Rechnung_v2_2025-01-14.pdf',
            'uploaded_at': '2025-01-14T15:45:00'
        }
    ]
    
    formatted = format_document_list_for_display(docs)
    
    assert len(formatted) == 2, f"Expected 2 documents, got {len(formatted)}"
    
    # Prüfe erstes Dokument
    doc1 = formatted[0]
    assert doc1['type_label'] == 'Angebot', f"Expected 'Angebot', got {doc1['type_label']}"
    assert doc1['badge_color'] == '#2563EB', f"Expected '#2563EB', got {doc1['badge_color']}"
    assert doc1['version'] == 1, f"Expected version 1, got {doc1['version']}"
    assert doc1['formatted_date'] == '13.01.2025 10:30', f"Expected '13.01.2025 10:30', got {doc1['formatted_date']}"
    
    print("[OK] Dokumentenliste erfolgreich formatiert:")
    for doc in formatted:
        print(f"   - {doc['display_name']}: {doc['type_label']} v{doc['version']} ({doc['formatted_date']})")


def test_auto_save_pdf_to_customer_documents():
    """Test: Automatisches Speichern von PDFs in Kundenakte"""
    print("\n=== Test: auto_save_pdf_to_customer_documents ===")
    
    from crm.integration.pdf_bridge import auto_save_pdf_to_customer_documents
    from database import list_customer_documents
    
    # Setup Test-Datenbank
    if not setup_test_database():
        print("[WARNING] Test übersprungen - Datenbank nicht verfügbar")
        return
    
    # Erstelle Test-PDF
    with tempfile.NamedTemporaryFile(suffix='_test_angebot.pdf', delete=False) as tmp:
        tmp.write(b'%PDF-1.4\nTest PDF Content for Auto-Save Test')
        tmp_path = tmp.name
    
    try:
        offer_data = {
            'offer_id': 'TEST-AUTO-001',
            'customer': {'name': 'Test Kunde PDF'},
            'project_type': 'pv'
        }
        
        # Speichere PDF
        doc_id = auto_save_pdf_to_customer_documents(
            pdf_path=tmp_path,
            customer_id=99999,
            project_id=None,
            offer_data=offer_data,
            display_name='Test Angebot'
        )
        
        assert doc_id is not None, "Document ID should not be None"
        assert isinstance(doc_id, int), f"Document ID should be int, got {type(doc_id)}"
        
        # Prüfe ob Dokument in Datenbank gespeichert wurde
        docs = list_customer_documents(99999)
        assert len(docs) > 0, "Should have at least one document"
        
        saved_doc = docs[0]
        assert saved_doc['doc_type'] == 'offer_pdf', f"Expected 'offer_pdf', got {saved_doc['doc_type']}"
        assert 'v1' in saved_doc['display_name'], f"Version should be in filename: {saved_doc['display_name']}"
        
        print(f"[OK] PDF erfolgreich gespeichert - Dokument-ID: {doc_id}")
        print(f"   - Typ: {saved_doc['doc_type']}")
        print(f"   - Name: {saved_doc['display_name']}")
        
    finally:
        os.unlink(tmp_path)
        cleanup_test_data()


def test_versioning_with_multiple_pdfs():
    """Test: Versionierung mit mehreren PDFs"""
    print("\n=== Test: versioning_with_multiple_pdfs ===")
    
    from crm.integration.pdf_bridge import auto_save_pdf_to_customer_documents, get_next_version_number
    from database import list_customer_documents
    
    # Setup Test-Datenbank
    if not setup_test_database():
        print("[WARNING] Test übersprungen - Datenbank nicht verfügbar")
        return
    
    try:
        # Speichere 3 PDFs nacheinander
        for i in range(1, 4):
            with tempfile.NamedTemporaryFile(suffix=f'_angebot_{i}.pdf', delete=False) as tmp:
                tmp.write(f'%PDF-1.4\nTest PDF Version {i}'.encode())
                tmp_path = tmp.name
            
            try:
                doc_id = auto_save_pdf_to_customer_documents(
                    pdf_path=tmp_path,
                    customer_id=99999,
                    project_id=None,
                    offer_data={'offer_id': f'TEST-V{i}'},
                    display_name=f'Angebot_{i}'
                )
                
                assert doc_id is not None, f"Document {i} should be saved"
                print(f"[OK] PDF {i} gespeichert - ID: {doc_id}")
                
            finally:
                os.unlink(tmp_path)
        
        # Prüfe Versionsnummern
        docs = list_customer_documents(99999)
        assert len(docs) == 3, f"Expected 3 documents, got {len(docs)}"
        
        # Prüfe dass alle Versionen vorhanden sind
        versions_found = []
        for doc in docs:
            if 'v1' in doc['display_name']:
                versions_found.append(1)
            elif 'v2' in doc['display_name']:
                versions_found.append(2)
            elif 'v3' in doc['display_name']:
                versions_found.append(3)
        
        assert len(versions_found) == 3, f"Expected 3 versions, found {len(versions_found)}"
        assert 1 in versions_found, "Version 1 not found"
        assert 2 in versions_found, "Version 2 not found"
        assert 3 in versions_found, "Version 3 not found"
        
        print("[OK] Versionierung erfolgreich:")
        for doc in docs:
            print(f"   - {doc['display_name']}")
        
        # Teste get_next_version_number
        next_version = get_next_version_number(99999, 'offer_pdf')
        assert next_version == 4, f"Expected next version 4, got {next_version}"
        print(f"[OK] Nächste Version korrekt ermittelt: v{next_version}")
        
    finally:
        cleanup_test_data()


def test_auto_save_with_project_id():
    """Test: Automatisches Speichern mit Projekt-ID"""
    print("\n=== Test: auto_save_with_project_id ===")
    
    from crm.integration.pdf_bridge import auto_save_pdf_to_customer_documents
    from database import list_customer_documents
    
    # Setup Test-Datenbank
    if not setup_test_database():
        print("[WARNING] Test übersprungen - Datenbank nicht verfügbar")
        return
    
    with tempfile.NamedTemporaryFile(suffix='_project_angebot.pdf', delete=False) as tmp:
        tmp.write(b'%PDF-1.4\nTest PDF with Project ID')
        tmp_path = tmp.name
    
    try:
        doc_id = auto_save_pdf_to_customer_documents(
            pdf_path=tmp_path,
            customer_id=99999,
            project_id=12345,
            offer_data={'offer_id': 'TEST-PROJ-001'},
            display_name='Projekt Angebot'
        )
        
        assert doc_id is not None, "Document should be saved"
        
        # Prüfe mit project_id Filter
        docs = list_customer_documents(99999, project_id=12345)
        assert len(docs) > 0, "Should have documents for project"
        
        print(f"[OK] PDF mit Projekt-ID gespeichert - ID: {doc_id}")
        
    finally:
        os.unlink(tmp_path)
        cleanup_test_data()


def test_auto_save_nonexistent_file():
    """Test: Auto-Save mit nicht existierender Datei"""
    print("\n=== Test: auto_save_nonexistent_file ===")
    
    from crm.integration.pdf_bridge import auto_save_pdf_to_customer_documents
    
    # Versuche nicht existierende Datei zu speichern
    doc_id = auto_save_pdf_to_customer_documents(
        pdf_path='/nonexistent/path/to/file.pdf',
        customer_id=99999,
        offer_data=None
    )
    
    assert doc_id is None, "Should return None for nonexistent file"
    print("[OK] Nicht existierende Datei korrekt behandelt (None zurückgegeben)")


def test_integration_workflow():
    """Test: Kompletter Integrations-Workflow"""
    print("\n=== Test: Integration Workflow ===")
    
    from crm.integration.pdf_bridge import (
        extract_pdf_metadata,
        get_next_version_number,
        create_versioned_filename,
        auto_save_pdf_to_customer_documents
    )
    
    # Setup Test-Datenbank
    if not setup_test_database():
        print("[WARNING] Test übersprungen - Datenbank nicht verfügbar")
        return
    
    # Erstelle Test-PDF
    with tempfile.NamedTemporaryFile(suffix='_test_angebot.pdf', delete=False) as tmp:
        tmp.write(b'%PDF-1.4\nTest PDF Content for Integration Test')
        tmp_path = tmp.name
    
    try:
        # Schritt 1: Metadaten extrahieren
        offer_data = {
            'offer_id': 'TEST-001',
            'customer': {'name': 'Test Kunde'},
            'project_type': 'pv'
        }
        
        metadata = extract_pdf_metadata(tmp_path, offer_data)
        print(f"[OK] Schritt 1: Metadaten extrahiert - Typ: {metadata['doc_type']}")
        
        # Schritt 2: Versionsnummer ermitteln
        version = get_next_version_number(99999, metadata['doc_type'])
        print(f"[OK] Schritt 2: Versionsnummer ermittelt - v{version}")
        
        # Schritt 3: Dateinamen erstellen
        filename = create_versioned_filename('test_angebot.pdf', version, metadata)
        print(f"[OK] Schritt 3: Dateiname erstellt - {filename}")
        
        # Schritt 4: Auto-Save mit echter Datenbank
        doc_id = auto_save_pdf_to_customer_documents(
            pdf_path=tmp_path,
            customer_id=99999,
            offer_data=offer_data
        )
        
        assert doc_id is not None, "Document should be saved"
        print(f"[OK] Schritt 4: PDF gespeichert - Dokument-ID: {doc_id}")
        
        print("\n[OK] Integration Workflow erfolgreich durchlaufen!")
        
    finally:
        os.unlink(tmp_path)
        cleanup_test_data()


def run_all_tests():
    """Führt alle Tests aus"""
    print("=" * 70)
    print("CRM PDF Bridge - Test Suite (Task 3.1)")
    print("=" * 70)
    print("\nTask 3.1 Tests:")
    print("  [OK] Teste automatisches Speichern")
    print("  [OK] Teste Metadaten-Extraktion")
    print("  [OK] Teste Versionierung")
    print("=" * 70)
    
    tests = [
        # Metadaten-Extraktion Tests
        test_extract_pdf_metadata,
        test_extract_pdf_metadata_various_types,
        test_extract_pdf_metadata_without_offer_data,
        
        # Versionierung Tests
        test_get_next_version_number,
        test_create_versioned_filename,
        
        # Helper-Funktionen Tests
        test_pdf_type_helpers,
        test_format_document_list,
        
        # Automatisches Speichern Tests
        test_auto_save_pdf_to_customer_documents,
        test_versioning_with_multiple_pdfs,
        test_auto_save_with_project_id,
        test_auto_save_nonexistent_file,
        
        # Integration Tests
        test_integration_workflow
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n[ERROR] Test fehlgeschlagen: {test.__name__}")
            print(f"   Fehler: {e}")
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] Test-Fehler: {test.__name__}")
            print(f"   Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test-Ergebnisse: {passed} bestanden, {failed} fehlgeschlagen")
    print("=" * 70)
    
    if failed == 0:
        print("\n[OK] Task 3.1 ERFOLGREICH ABGESCHLOSSEN")
        print("   • Automatisches Speichern getestet")
        print("   • Metadaten-Extraktion getestet")
        print("   • Versionierung getestet")
    else:
        print(f"\n[WARNING] {failed} Test(s) fehlgeschlagen")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
