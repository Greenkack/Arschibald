# crm/features/test_contract_manager.py
"""
Unit Tests für Vertrags- und Garantieverwaltung

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import sqlite3
import pytest
from datetime import datetime, timedelta
from crm.features import contract_manager


@pytest.fixture
def test_db():
    """Erstellt eine Test-Datenbank im Speicher."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    # Erstelle notwendige Tabellen
    contract_manager.create_contract_tables(conn)
    
    # Erstelle Mock-Tabellen für Fremdschlüssel
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            file_name TEXT
        )
    """)
    
    # Füge Test-Daten hinzu
    cursor.execute("INSERT INTO customers (first_name, last_name) VALUES ('Max', 'Mustermann')")
    cursor.execute("INSERT INTO projects (customer_id, name) VALUES (1, 'Solar Installation')")
    cursor.execute("INSERT INTO customer_documents (customer_id, file_name) VALUES (1, 'contract.pdf')")
    
    conn.commit()
    
    yield conn
    conn.close()


# ============================================================================
# CONTRACT TESTS
# ============================================================================

def test_create_contract(test_db):
    """Test: Vertrag erstellen"""
    contract_id = contract_manager.create_contract(
        test_db,
        customer_id=1,
        contract_type="Wartungsvertrag",
        title="PV-Anlage Wartung 2025",
        start_date="2025-01-01",
        end_date="2025-12-31",
        value=1200.0,
        description="Jährliche Wartung der PV-Anlage"
    )
    
    assert contract_id is not None
    assert contract_id > 0
    
    # Vertrag laden und prüfen
    contract = contract_manager.get_contract_by_id(test_db, contract_id)
    assert contract is not None
    assert contract['title'] == "PV-Anlage Wartung 2025"
    assert contract['contract_type'] == "Wartungsvertrag"
    assert contract['customer_id'] == 1
    assert contract['value'] == 1200.0
    assert contract['status'] == 'active'


def test_create_contract_with_reminder(test_db):
    """Test: Vertrag mit automatischer Erinnerung erstellen"""
    end_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
    
    contract_id = contract_manager.create_contract(
        test_db,
        customer_id=1,
        contract_type="Kaufvertrag",
        title="Kaufvertrag PV-Module",
        start_date=datetime.now().strftime('%Y-%m-%d'),
        end_date=end_date
    )
    
    assert contract_id is not None
    
    # Prüfe ob Erinnerung erstellt wurde
    cursor = test_db.cursor()
    cursor.execute("""
        SELECT * FROM contract_reminders 
        WHERE contract_id = ? AND reminder_type = 'contract_expiry'
    """, (contract_id))
    reminder = cursor.fetchone()
    
    assert reminder is not None
    assert reminder['status'] == 'pending'



def test_get_contract_by_id(test_db):
    """Test: Vertrag anhand ID laden"""
    # Erstelle Vertrag
    contract_id = contract_manager.create_contract(
        test_db,
        customer_id=1,
        contract_type="Servicevertrag",
        title="Service-Vertrag",
        start_date="2025-01-01"
    )
    
    # Lade Vertrag
    contract = contract_manager.get_contract_by_id(test_db, contract_id)
    
    assert contract is not None
    assert contract['id'] == contract_id
    assert contract['title'] == "Service-Vertrag"


def test_get_contracts_by_customer(test_db):
    """Test: Alle Verträge eines Kunden laden"""
    # Erstelle mehrere Verträge
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Wartungsvertrag",
        title="Wartung 1", start_date="2025-01-01"
    )
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Kaufvertrag",
        title="Kauf 1", start_date="2025-02-01"
    )
    
    # Lade Verträge
    contracts = contract_manager.get_contracts_by_customer(test_db, 1)
    
    assert len(contracts) == 2
    assert all(c['customer_id'] == 1 for c in contracts)


def test_update_contract(test_db):
    """Test: Vertrag aktualisieren"""
    # Erstelle Vertrag
    contract_id = contract_manager.create_contract(
        test_db,
        customer_id=1,
        contract_type="Wartungsvertrag",
        title="Original Titel",
        start_date="2025-01-01",
        value=1000.0
    )
    
    # Aktualisiere Vertrag
    success = contract_manager.update_contract(
        test_db,
        contract_id,
        title="Neuer Titel",
        value=1500.0,
        status="expired"
    )
    
    assert success is True
    
    # Prüfe Änderungen
    contract = contract_manager.get_contract_by_id(test_db, contract_id)
    assert contract['title'] == "Neuer Titel"
    assert contract['value'] == 1500.0
    assert contract['status'] == "expired"


def test_delete_contract(test_db):
    """Test: Vertrag löschen"""
    # Erstelle Vertrag
    contract_id = contract_manager.create_contract(
        test_db,
        customer_id=1,
        contract_type="Testvertrag",
        title="Zu löschender Vertrag",
        start_date="2025-01-01"
    )
    
    # Lösche Vertrag
    success = contract_manager.delete_contract(test_db, contract_id)
    assert success is True
    
    # Prüfe ob gelöscht
    contract = contract_manager.get_contract_by_id(test_db, contract_id)
    assert contract is None


def test_get_expiring_contracts(test_db):
    """Test: Ablaufende Verträge finden"""
    # Erstelle Verträge mit verschiedenen Enddaten
    today = datetime.now()
    
    # Vertrag läuft in 15 Tagen ab
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Test",
        title="Bald ablaufend", start_date=today.strftime('%Y-%m-%d'),
        end_date=(today + timedelta(days=15)).strftime('%Y-%m-%d')
    )
    
    # Vertrag läuft in 60 Tagen ab
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Test",
        title="Später ablaufend", start_date=today.strftime('%Y-%m-%d'),
        end_date=(today + timedelta(days=60)).strftime('%Y-%m-%d')
    )
    
    # Vertrag bereits abgelaufen
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Test",
        title="Abgelaufen", start_date=(today - timedelta(days=365)).strftime('%Y-%m-%d'),
        end_date=(today - timedelta(days=1)).strftime('%Y-%m-%d')
    )
    
    # Finde ablaufende Verträge (30 Tage)
    expiring = contract_manager.get_expiring_contracts(test_db, 30)
    
    assert len(expiring) == 1
    assert expiring[0]['title'] == "Bald ablaufend"


def test_get_expired_contracts(test_db):
    """Test: Abgelaufene Verträge finden"""
    today = datetime.now()
    
    # Erstelle abgelaufenen Vertrag
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Test",
        title="Abgelaufener Vertrag",
        start_date=(today - timedelta(days=365)).strftime('%Y-%m-%d'),
        end_date=(today - timedelta(days=1)).strftime('%Y-%m-%d')
    )
    
    # Erstelle aktiven Vertrag
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Test",
        title="Aktiver Vertrag",
        start_date=today.strftime('%Y-%m-%d'),
        end_date=(today + timedelta(days=365)).strftime('%Y-%m-%d')
    )
    
    # Finde abgelaufene Verträge
    expired = contract_manager.get_expired_contracts(test_db)
    
    assert len(expired) == 1
    assert expired[0]['title'] == "Abgelaufener Vertrag"


# ============================================================================
# WARRANTY TESTS
# ============================================================================

def test_create_warranty(test_db):
    """Test: Garantie erstellen"""
    warranty_id = contract_manager.create_warranty(
        test_db,
        project_id=1,
        customer_id=1,
        warranty_type="Produktgarantie",
        title="PV-Module Garantie",
        start_date="2025-01-01",
        duration_months=120,
        description="25 Jahre Leistungsgarantie"
    )
    
    assert warranty_id is not None
    assert warranty_id > 0
    
    # Garantie laden und prüfen
    warranty = contract_manager.get_warranty_by_id(test_db, warranty_id)
    assert warranty is not None
    assert warranty['title'] == "PV-Module Garantie"
    assert warranty['warranty_type'] == "Produktgarantie"
    assert warranty['duration_months'] == 120
    assert warranty['status'] == 'active'
    assert warranty['end_date'] is not None


def test_create_warranty_with_reminder(test_db):
    """Test: Garantie mit automatischer Erinnerung erstellen"""
    warranty_id = contract_manager.create_warranty(
        test_db,
        project_id=1,
        customer_id=1,
        warranty_type="Leistungsgarantie",
        title="Leistungsgarantie",
        start_date=datetime.now().strftime('%Y-%m-%d'),
        duration_months=2  # 2 Monate für Test
    )
    
    assert warranty_id is not None
    
    # Prüfe ob Erinnerung erstellt wurde
    cursor = test_db.cursor()
    cursor.execute("""
        SELECT * FROM contract_reminders 
        WHERE warranty_id = ? AND reminder_type = 'warranty_expiry'
    """, (warranty_id))
    reminder = cursor.fetchone()
    
    assert reminder is not None
    assert reminder['status'] == 'pending'


def test_get_warranty_by_id(test_db):
    """Test: Garantie anhand ID laden"""
    warranty_id = contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Herstellergarantie", title="Test Garantie",
        start_date="2025-01-01", duration_months=24
    )
    
    warranty = contract_manager.get_warranty_by_id(test_db, warranty_id)
    
    assert warranty is not None
    assert warranty['id'] == warranty_id
    assert warranty['title'] == "Test Garantie"


def test_get_warranties_by_project(test_db):
    """Test: Alle Garantien eines Projekts laden"""
    # Erstelle mehrere Garantien
    contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Produktgarantie", title="Garantie 1",
        start_date="2025-01-01", duration_months=24
    )
    contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Leistungsgarantie", title="Garantie 2",
        start_date="2025-01-01", duration_months=120
    )
    
    warranties = contract_manager.get_warranties_by_project(test_db, 1)
    
    assert len(warranties) == 2
    assert all(w['project_id'] == 1 for w in warranties)


def test_update_warranty(test_db):
    """Test: Garantie aktualisieren"""
    warranty_id = contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Produktgarantie", title="Original",
        start_date="2025-01-01", duration_months=24
    )
    
    success = contract_manager.update_warranty(
        test_db, warranty_id,
        title="Aktualisiert",
        duration_months=36,
        status="expired"
    )
    
    assert success is True
    
    warranty = contract_manager.get_warranty_by_id(test_db, warranty_id)
    assert warranty['title'] == "Aktualisiert"
    assert warranty['duration_months'] == 36
    assert warranty['status'] == "expired"


def test_delete_warranty(test_db):
    """Test: Garantie löschen"""
    warranty_id = contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Test", title="Zu löschen",
        start_date="2025-01-01", duration_months=12
    )
    
    success = contract_manager.delete_warranty(test_db, warranty_id)
    assert success is True
    
    warranty = contract_manager.get_warranty_by_id(test_db, warranty_id)
    assert warranty is None


def test_get_expiring_warranties(test_db):
    """Test: Ablaufende Garantien finden"""
    today = datetime.now()
    
    # Garantie läuft in 1 Monat ab
    contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Test", title="Bald ablaufend",
        start_date=(today - timedelta(days=330)).strftime('%Y-%m-%d'),
        duration_months=12
    )
    
    # Garantie läuft in 6 Monaten ab
    contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Test", title="Später ablaufend",
        start_date=(today - timedelta(days=180)).strftime('%Y-%m-%d'),
        duration_months=12
    )
    
    expiring = contract_manager.get_expiring_warranties(test_db, 60)
    
    assert len(expiring) >= 1


# ============================================================================
# REMINDER TESTS
# ============================================================================

def test_create_contract_expiry_reminder(test_db):
    """Test: Vertrags-Ablauf-Erinnerung erstellen"""
    end_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
    
    contract_id = contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Test",
        title="Test", start_date=datetime.now().strftime('%Y-%m-%d'),
        end_date=end_date
    )
    
    # Erinnerung sollte automatisch erstellt worden sein
    cursor = test_db.cursor()
    cursor.execute("""
        SELECT * FROM contract_reminders 
        WHERE contract_id = ?
    """, (contract_id))
    reminder = cursor.fetchone()
    
    assert reminder is not None
    assert reminder['reminder_type'] == 'contract_expiry'
    assert reminder['status'] == 'pending'


def test_update_contract_expiry_reminder(test_db):
    """Test: Vertrags-Ablauf-Erinnerung aktualisieren"""
    end_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
    
    contract_id = contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Test",
        title="Test", start_date=datetime.now().strftime('%Y-%m-%d'),
        end_date=end_date
    )
    
    # Ändere Enddatum
    new_end_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
    contract_manager.update_contract(test_db, contract_id, end_date=new_end_date)
    
    # Prüfe ob Erinnerung aktualisiert wurde
    cursor = test_db.cursor()
    cursor.execute("""
        SELECT * FROM contract_reminders 
        WHERE contract_id = ?
    """, (contract_id))
    reminder = cursor.fetchone()
    
    assert reminder is not None
    # Erinnerungsdatum sollte 30 Tage vor neuem Enddatum sein
    expected_reminder_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
    assert reminder['reminder_date'] == expected_reminder_date


def test_get_pending_reminders(test_db):
    """Test: Fällige Erinnerungen laden"""
    today = datetime.now()
    
    # Erstelle Vertrag mit Erinnerung in 10 Tagen
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Test",
        title="Test", start_date=today.strftime('%Y-%m-%d'),
        end_date=(today + timedelta(days=40)).strftime('%Y-%m-%d')
    )
    
    # Lade fällige Erinnerungen (30 Tage voraus)
    reminders = contract_manager.get_pending_reminders(test_db, 30)
    
    assert len(reminders) >= 1


def test_mark_reminder_notified(test_db):
    """Test: Erinnerung als benachrichtigt markieren"""
    end_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
    
    contract_id = contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Test",
        title="Test", start_date=datetime.now().strftime('%Y-%m-%d'),
        end_date=end_date
    )
    
    # Finde Erinnerung
    cursor = test_db.cursor()
    cursor.execute("""
        SELECT id FROM contract_reminders 
        WHERE contract_id = ?
    """, (contract_id))
    reminder = cursor.fetchone()
    reminder_id = reminder[0]
    
    # Markiere als benachrichtigt
    success = contract_manager.mark_reminder_notified(test_db, reminder_id)
    assert success is True
    
    # Prüfe Status
    cursor.execute("SELECT status FROM contract_reminders WHERE id = ?", (reminder_id,))
    status = cursor.fetchone()[0]
    assert status == 'notified'


# ============================================================================
# STATISTICS TESTS
# ============================================================================

def test_get_contract_statistics(test_db):
    """Test: Vertrags-Statistiken laden"""
    # Erstelle verschiedene Verträge
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Wartungsvertrag",
        title="Wartung", start_date="2025-01-01", value=1000.0
    )
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Kaufvertrag",
        title="Kauf", start_date="2025-01-01", value=5000.0, status="expired"
    )
    
    stats = contract_manager.get_contract_statistics(test_db)
    
    assert stats['total'] == 2
    assert stats['by_status']['active'] == 1
    assert stats['by_status']['expired'] == 1
    assert stats['total_value'] == 1000.0  # Nur aktive Verträge


def test_get_warranty_statistics(test_db):
    """Test: Garantie-Statistiken laden"""
    # Erstelle verschiedene Garantien
    contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Produktgarantie", title="Produkt",
        start_date="2025-01-01", duration_months=24
    )
    contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Leistungsgarantie", title="Leistung",
        start_date="2025-01-01", duration_months=120, status="expired"
    )
    
    stats = contract_manager.get_warranty_statistics(test_db)
    
    assert stats['total'] == 2
    assert stats['by_status']['active'] == 1
    assert stats['by_status']['expired'] == 1


def test_get_contract_types(test_db):
    """Test: Vertragstypen laden"""
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Wartungsvertrag",
        title="Test 1", start_date="2025-01-01"
    )
    contract_manager.create_contract(
        test_db, customer_id=1, contract_type="Kaufvertrag",
        title="Test 2", start_date="2025-01-01"
    )
    
    types = contract_manager.get_contract_types(test_db)
    
    assert len(types) == 2
    assert "Wartungsvertrag" in types
    assert "Kaufvertrag" in types


def test_get_warranty_types(test_db):
    """Test: Garantietypen laden"""
    contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Produktgarantie", title="Test 1",
        start_date="2025-01-01", duration_months=24
    )
    contract_manager.create_warranty(
        test_db, project_id=1, customer_id=1,
        warranty_type="Leistungsgarantie", title="Test 2",
        start_date="2025-01-01", duration_months=120
    )
    
    types = contract_manager.get_warranty_types(test_db)
    
    assert len(types) == 2
    assert "Produktgarantie" in types
    assert "Leistungsgarantie" in types


if __name__ == "__main__":
    print("Führe Tests aus...")
    pytest.main([__file__, "-v"])
