# crm/features/test_tag_manager.py
"""
Unit Tests für Tag Management System

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
from crm.features.tag_manager import (
    create_tag_tables,
    create_tag,
    get_tag_by_id,
    get_tag_by_name,
    get_all_tags,
    update_tag,
    delete_tag,
    assign_tag_to_customer,
    remove_tag_from_customer,
    get_customer_tags,
    get_customers_by_tag,
    get_customers_by_tags,
    assign_tags_to_customers,
    remove_tags_from_customers,
    get_tag_statistics,
    get_tag_categories,
)


@pytest.fixture
def test_db() -> Generator[sqlite3.Connection, None, None]:
    """Erstellt eine temporäre Test-Datenbank."""
    # Erstelle temporäre Datei
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Verbindung erstellen
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Erstelle notwendige Tabellen
    cursor = conn.cursor()
    
    # Customers Tabelle (vereinfacht für Tests)
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )
    """)
    
    # Tag-Tabellen erstellen
    create_tag_tables(conn)
    
    # Test-Kunden erstellen
    test_customers = [
        ("Max", "Mustermann", "max@example.com"),
        ("Erika", "Musterfrau", "erika@example.com"),
        ("Hans", "Schmidt", "hans@example.com"),
    ]
    
    for first_name, last_name, email in test_customers:
        cursor.execute(
            "INSERT INTO customers (first_name, last_name, email) VALUES (?, ?, ?)",
            (first_name, last_name, email)
        )
    
    conn.commit()
    
    yield conn
    
    # Cleanup
    conn.close()
    try:
        os.unlink(db_path)
    except Exception:
        pass


# ============================================================================
# TAG CRUD TESTS
# ============================================================================

def test_create_tag(test_db):
    """Test: Tag erstellen"""
    tag_id = create_tag(
        test_db,
        name="VIP-Kunde",
        color="#FF0000",
        category="Kundentyp",
        description="Wichtige Kunden mit hohem Umsatz"
    )
    
    assert tag_id is not None
    assert tag_id > 0
    
    # Tag laden und prüfen
    tag = get_tag_by_id(test_db, tag_id)
    assert tag is not None
    assert tag['name'] == "VIP-Kunde"
    assert tag['color'] == "#FF0000"
    assert tag['category'] == "Kundentyp"
    assert tag['is_active'] == 1


def test_create_duplicate_tag(test_db):
    """Test: Duplikat-Tag erstellen (sollte fehlschlagen)"""
    create_tag(test_db, name="Test-Tag")
    
    # Zweiter Versuch mit gleichem Namen
    tag_id = create_tag(test_db, name="Test-Tag")
    assert tag_id is None


def test_get_tag_by_name(test_db):
    """Test: Tag nach Name laden"""
    create_tag(test_db, name="Interessent", color="#00FF00")
    
    tag = get_tag_by_name(test_db, "Interessent")
    assert tag is not None
    assert tag['name'] == "Interessent"
    assert tag['color'] == "#00FF00"


def test_get_all_tags(test_db):
    """Test: Alle Tags laden"""
    # Erstelle mehrere Tags
    create_tag(test_db, name="Tag1", category="Kategorie A")
    create_tag(test_db, name="Tag2", category="Kategorie B")
    create_tag(test_db, name="Tag3", category="Kategorie A")
    
    # Alle Tags laden
    all_tags = get_all_tags(test_db)
    assert len(all_tags) == 3
    
    # Nach Kategorie filtern
    category_a_tags = get_all_tags(test_db, category="Kategorie A")
    assert len(category_a_tags) == 2


def test_update_tag(test_db):
    """Test: Tag aktualisieren"""
    tag_id = create_tag(test_db, name="Alter Name", color="#000000")
    
    # Tag aktualisieren
    success = update_tag(
        test_db,
        tag_id,
        name="Neuer Name",
        color="#FFFFFF",
        description="Neue Beschreibung"
    )
    
    assert success is True
    
    # Prüfen
    tag = get_tag_by_id(test_db, tag_id)
    assert tag['name'] == "Neuer Name"
    assert tag['color'] == "#FFFFFF"
    assert tag['description'] == "Neue Beschreibung"


def test_delete_tag(test_db):
    """Test: Tag löschen"""
    tag_id = create_tag(test_db, name="Zu löschen")
    
    # Löschen
    success = delete_tag(test_db, tag_id)
    assert success is True
    
    # Prüfen, dass Tag nicht mehr existiert
    tag = get_tag_by_id(test_db, tag_id)
    assert tag is None


# ============================================================================
# TAG ASSIGNMENT TESTS
# ============================================================================

def test_assign_tag_to_customer(test_db):
    """Test: Tag einem Kunden zuweisen"""
    tag_id = create_tag(test_db, name="VIP")
    customer_id = 1  # Erster Test-Kunde
    
    success = assign_tag_to_customer(test_db, customer_id, tag_id)
    assert success is True
    
    # Prüfen
    tags = get_customer_tags(test_db, customer_id)
    assert len(tags) == 1
    assert tags[0]['name'] == "VIP"


def test_assign_duplicate_tag(test_db):
    """Test: Gleichen Tag zweimal zuweisen (sollte fehlschlagen)"""
    tag_id = create_tag(test_db, name="Test")
    customer_id = 1
    
    # Erste Zuweisung
    success1 = assign_tag_to_customer(test_db, customer_id, tag_id)
    assert success1 is True
    
    # Zweite Zuweisung (Duplikat)
    success2 = assign_tag_to_customer(test_db, customer_id, tag_id)
    assert success2 is False


def test_remove_tag_from_customer(test_db):
    """Test: Tag von Kunde entfernen"""
    tag_id = create_tag(test_db, name="Temporär")
    customer_id = 1
    
    # Zuweisen
    assign_tag_to_customer(test_db, customer_id, tag_id)
    
    # Entfernen
    success = remove_tag_from_customer(test_db, customer_id, tag_id)
    assert success is True
    
    # Prüfen
    tags = get_customer_tags(test_db, customer_id)
    assert len(tags) == 0


def test_get_customers_by_tag(test_db):
    """Test: Kunden nach Tag filtern"""
    tag_id = create_tag(test_db, name="Premium")
    
    # Tags zuweisen
    assign_tag_to_customer(test_db, 1, tag_id)
    assign_tag_to_customer(test_db, 2, tag_id)
    
    # Kunden laden
    customer_ids = get_customers_by_tag(test_db, tag_id)
    assert len(customer_ids) == 2
    assert 1 in customer_ids
    assert 2 in customer_ids


def test_get_customers_by_multiple_tags(test_db):
    """Test: Kunden nach mehreren Tags filtern"""
    tag1_id = create_tag(test_db, name="Tag1")
    tag2_id = create_tag(test_db, name="Tag2")
    tag3_id = create_tag(test_db, name="Tag3")
    
    # Kunde 1: Tag1, Tag2
    assign_tag_to_customer(test_db, 1, tag1_id)
    assign_tag_to_customer(test_db, 1, tag2_id)
    
    # Kunde 2: Tag1, Tag3
    assign_tag_to_customer(test_db, 2, tag1_id)
    assign_tag_to_customer(test_db, 2, tag3_id)
    
    # Kunde 3: Tag2, Tag3
    assign_tag_to_customer(test_db, 3, tag2_id)
    assign_tag_to_customer(test_db, 3, tag3_id)
    
    # Test: Mindestens einen Tag (OR)
    customers_or = get_customers_by_tags(test_db, [tag1_id, tag2_id], match_all=False)
    assert len(customers_or) == 3  # Alle haben mindestens einen der Tags
    
    # Test: Alle Tags (AND)
    customers_and = get_customers_by_tags(test_db, [tag1_id, tag2_id], match_all=True)
    assert len(customers_and) == 1  # Nur Kunde 1 hat beide Tags
    assert 1 in customers_and


# ============================================================================
# BULK OPERATIONS TESTS
# ============================================================================

def test_bulk_assign_tags(test_db):
    """Test: Massen-Tagging"""
    tag1_id = create_tag(test_db, name="Bulk1")
    tag2_id = create_tag(test_db, name="Bulk2")
    
    customer_ids = [1, 2, 3]
    tag_ids = [tag1_id, tag2_id]
    
    stats = assign_tags_to_customers(test_db, customer_ids, tag_ids)
    
    assert stats['success'] == 6  # 3 Kunden * 2 Tags
    assert stats['skipped'] == 0
    assert stats['errors'] == 0
    
    # Prüfen
    for customer_id in customer_ids:
        tags = get_customer_tags(test_db, customer_id)
        assert len(tags) == 2


def test_bulk_remove_tags(test_db):
    """Test: Massen-Entfernung von Tags"""
    tag1_id = create_tag(test_db, name="Remove1")
    tag2_id = create_tag(test_db, name="Remove2")
    
    customer_ids = [1, 2]
    
    # Zuweisen
    assign_tags_to_customers(test_db, customer_ids, [tag1_id, tag2_id])
    
    # Entfernen
    removed = remove_tags_from_customers(test_db, customer_ids, [tag1_id])
    assert removed == 2  # 2 Kunden * 1 Tag
    
    # Prüfen
    for customer_id in customer_ids:
        tags = get_customer_tags(test_db, customer_id)
        assert len(tags) == 1  # Nur tag2 sollte noch da sein
        assert tags[0]['name'] == "Remove2"


# ============================================================================
# STATISTICS TESTS
# ============================================================================

def test_tag_statistics(test_db):
    """Test: Tag-Statistiken"""
    tag1_id = create_tag(test_db, name="Popular", category="Test")
    tag2_id = create_tag(test_db, name="Rare", category="Test")
    
    # Tag1 zu 3 Kunden, Tag2 zu 1 Kunde
    assign_tag_to_customer(test_db, 1, tag1_id)
    assign_tag_to_customer(test_db, 2, tag1_id)
    assign_tag_to_customer(test_db, 3, tag1_id)
    assign_tag_to_customer(test_db, 1, tag2_id)
    
    stats = get_tag_statistics(test_db)
    
    assert len(stats) == 2
    # Sollte nach customer_count sortiert sein
    assert stats[0]['name'] == "Popular"
    assert stats[0]['customer_count'] == 3
    assert stats[1]['name'] == "Rare"
    assert stats[1]['customer_count'] == 1


def test_get_tag_categories(test_db):
    """Test: Tag-Kategorien laden"""
    create_tag(test_db, name="Tag1", category="Kategorie A")
    create_tag(test_db, name="Tag2", category="Kategorie B")
    create_tag(test_db, name="Tag3", category="Kategorie A")
    create_tag(test_db, name="Tag4", category=None)
    
    categories = get_tag_categories(test_db)
    
    assert len(categories) == 2
    assert "Kategorie A" in categories
    assert "Kategorie B" in categories


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_complete_workflow(test_db):
    """Test: Kompletter Workflow"""
    # 1. Tags erstellen
    vip_id = create_tag(test_db, name="VIP", color="#FFD700", category="Status")
    interessent_id = create_tag(test_db, name="Interessent", color="#87CEEB", category="Status")
    gewerbe_id = create_tag(test_db, name="Gewerbe", color="#90EE90", category="Typ")
    
    # 2. Tags zuweisen
    assign_tag_to_customer(test_db, 1, vip_id)
    assign_tag_to_customer(test_db, 1, gewerbe_id)
    assign_tag_to_customer(test_db, 2, interessent_id)
    
    # 3. Kunden nach Tags filtern
    vip_customers = get_customers_by_tag(test_db, vip_id)
    assert len(vip_customers) == 1
    
    # 4. Statistiken prüfen
    stats = get_tag_statistics(test_db)
    assert len(stats) == 3
    
    # 5. Tag aktualisieren
    update_tag(test_db, vip_id, description="Sehr wichtige Kunden")
    
    # 6. Tag entfernen
    remove_tag_from_customer(test_db, 1, gewerbe_id)
    
    # 7. Prüfen
    customer_tags = get_customer_tags(test_db, 1)
    assert len(customer_tags) == 1
    assert customer_tags[0]['name'] == "VIP"


if __name__ == "__main__":
    # Tests ausführen
    pytest.main([__file__, "-v"])
