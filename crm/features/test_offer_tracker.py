# crm/features/test_offer_tracker.py
"""
Tests für Angebotsverfolgung (Offer Tracking)
"""

import os
import sqlite3
import sys
from datetime import datetime, timedelta

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from crm.features.offer_tracker import (
    create_offer_tracking_tables,
    get_all_offers,
    get_offer_statistics,
    get_offer_status,
    get_pending_follow_ups,
    mark_follow_up_completed,
    update_lead_status_from_offer,
    update_offer_status,
)


def create_test_db():
    """Erstellt eine Test-Datenbank im Speicher."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    # Erstelle customers Tabelle
    conn.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            company_name TEXT,
            email TEXT,
            phone_mobile TEXT
        )
    """)
    
    # Erstelle projects Tabelle
    conn.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            project_name TEXT,
            project_status TEXT,
            creation_date TEXT,
            last_updated TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    # Erstelle crm_leads Tabelle (für Lead-Status-Update-Tests)
    conn.execute("""
        CREATE TABLE crm_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            contact_person TEXT,
            stage TEXT,
            stage_changed_at TEXT,
            updated_at TEXT
        )
    """)
    
    conn.commit()
    return conn


def test_create_offer_tracking_tables():
    """Test: Tabellen-Erstellung für Angebotsverfolgung"""
    print("\n=== Test: Tabellen-Erstellung ===")
    
    conn = create_test_db()
    
    # Erstelle Angebotsverfolgung-Felder
    create_offer_tracking_tables(conn)
    
    # Prüfe ob Spalten hinzugefügt wurden
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in cursor.fetchall()]
    
    required_columns = [
        'offer_status', 'offer_sent_date', 'offer_accepted_date',
        'offer_rejected_date', 'offer_version', 'offer_value',
        'rejection_reason', 'rejection_notes', 'follow_up_date',
        'follow_up_completed'
    ]
    
    for col in required_columns:
        assert col in columns, f"Spalte '{col}' fehlt in projects Tabelle"
    
    print("Alle erforderlichen Spalten wurden hinzugefügt")
    conn.close()


def test_update_offer_status():
    """Test: Status-Workflow für Angebote"""
    print("\n=== Test: Status-Workflow ===")
    
    conn = create_test_db()
    create_offer_tracking_tables(conn)
    
    # Erstelle Test-Kunde und Projekt
    conn.execute("INSERT INTO customers (first_name, last_name, email) VALUES (?, ?, ?)",
                 ("Max", "Mustermann", "max@test.de"))
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    conn.execute("INSERT INTO projects (customer_id, project_name) VALUES (?, ?)",
                 (customer_id, "Test Projekt"))
    project_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    
    # Test 1: Status auf "sent" setzen
    print("\n1. Status auf 'sent' setzen...")
    result = update_offer_status(conn, project_id, 'sent', offer_value=25000.0)
    assert result, "Status-Update fehlgeschlagen"
    
    offer = get_offer_status(conn, project_id)
    assert offer['offer_status'] == 'sent', f"Status sollte 'sent' sein, ist aber '{offer['offer_status']}'"
    assert offer['offer_sent_date'] is not None, "offer_sent_date sollte gesetzt sein"
    assert offer['follow_up_date'] is not None, "follow_up_date sollte automatisch gesetzt sein"
    assert offer['offer_value'] == 25000.0, f"offer_value sollte 25000.0 sein, ist aber {offer['offer_value']}"
    print("Status 'sent' erfolgreich gesetzt mit automatischem Follow-up")
    
    # Test 2: Status auf "accepted" setzen
    print("\n2. Status auf 'accepted' setzen...")
    result = update_offer_status(conn, project_id, 'accepted')
    assert result, "Status-Update fehlgeschlagen"
    
    offer = get_offer_status(conn, project_id)
    assert offer['offer_status'] == 'accepted', f"Status sollte 'accepted' sein"
    assert offer['offer_accepted_date'] is not None, "offer_accepted_date sollte gesetzt sein"
    print("Status 'accepted' erfolgreich gesetzt")
    
    # Test 3: Neues Projekt mit "rejected" Status
    conn.execute("INSERT INTO projects (customer_id, project_name) VALUES (?, ?)",
                 (customer_id, "Test Projekt 2"))
    project_id_2 = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    
    print("\n3. Status auf 'rejected' setzen mit Ablehnungsgrund...")
    result = update_offer_status(
        conn, project_id_2, 'rejected',
        rejection_reason='Preis zu hoch',
        rejection_notes='Kunde hat günstigeres Angebot gefunden'
    )
    assert result, "Status-Update fehlgeschlagen"
    
    offer = get_offer_status(conn, project_id_2)
    assert offer['offer_status'] == 'rejected', "Status sollte 'rejected' sein"
    assert offer['rejection_reason'] == 'Preis zu hoch', "Ablehnungsgrund sollte gesetzt sein"
    assert offer['rejection_notes'] is not None, "Ablehnungsnotizen sollten gesetzt sein"
    print("Status 'rejected' erfolgreich gesetzt mit Ablehnungsgrund")
    
    conn.close()


def test_get_all_offers():
    """Test: Alle Angebote laden mit Filter"""
    print("\n=== Test: Angebote laden ===")
    
    conn = create_test_db()
    create_offer_tracking_tables(conn)
    
    # Erstelle Test-Daten
    conn.execute("INSERT INTO customers (first_name, last_name, company_name) VALUES (?, ?, ?)",
                 ("Max", "Mustermann", "Test GmbH"))
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Erstelle mehrere Projekte mit verschiedenen Status
    projects = [
        ("Projekt Draft", "draft"),
        ("Projekt Sent", "sent"),
        ("Projekt Accepted", "accepted"),
        ("Projekt Rejected", "rejected")
    ]
    
    for name, status in projects:
        conn.execute("INSERT INTO projects (customer_id, project_name, offer_status) VALUES (?, ?, ?)",
                     (customer_id, name, status))
    conn.commit()
    
    # Test 1: Alle Angebote laden
    print("\n1. Alle Angebote laden...")
    all_offers = get_all_offers(conn)
    assert len(all_offers) == 4, f"Sollte 4 Angebote haben, hat aber {len(all_offers)}"
    print(f"{len(all_offers)} Angebote geladen")
    
    # Test 2: Filter nach Status "sent"
    print("\n2. Filter nach Status 'sent'...")
    sent_offers = get_all_offers(conn, status_filter='sent')
    assert len(sent_offers) == 1, f"Sollte 1 'sent' Angebot haben, hat aber {len(sent_offers)}"
    assert sent_offers[0]['offer_status'] == 'sent', "Gefiltertes Angebot sollte Status 'sent' haben"
    print("Filter funktioniert korrekt")
    
    # Test 3: Mit Kundeninformationen
    print("\n3. Mit Kundeninformationen laden...")
    offers_with_customer = get_all_offers(conn, include_customer_info=True)
    assert 'customer_first_name' in offers_with_customer[0], "Kundeninformationen fehlen"
    assert offers_with_customer[0]['customer_company_name'] == 'Test GmbH', "Firmenname sollte geladen sein"
    print("Kundeninformationen werden korrekt geladen")
    
    conn.close()


def test_follow_up_reminders():
    """Test: Follow-up-Erinnerungen"""
    print("\n=== Test: Follow-up-Erinnerungen ===")
    
    conn = create_test_db()
    create_offer_tracking_tables(conn)
    
    # Erstelle Test-Daten
    conn.execute("INSERT INTO customers (first_name, last_name, email) VALUES (?, ?, ?)",
                 ("Max", "Mustermann", "max@test.de"))
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Projekt 1: Follow-up fällig (vor 2 Tagen)
    past_date = (datetime.now() - timedelta(days=2)).isoformat()
    conn.execute("""
        INSERT INTO projects (customer_id, project_name, offer_status, follow_up_date, follow_up_completed)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, "Projekt mit fälligem Follow-up", "sent", past_date, 0))
    project_id_1 = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Projekt 2: Follow-up in Zukunft
    future_date = (datetime.now() + timedelta(days=5)).isoformat()
    conn.execute("""
        INSERT INTO projects (customer_id, project_name, offer_status, follow_up_date, follow_up_completed)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, "Projekt mit zukünftigem Follow-up", "sent", future_date, 0))
    
    # Projekt 3: Follow-up bereits erledigt
    conn.execute("""
        INSERT INTO projects (customer_id, project_name, offer_status, follow_up_date, follow_up_completed)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, "Projekt mit erledigtem Follow-up", "sent", past_date, 1))
    
    conn.commit()
    
    # Test 1: Ausstehende Follow-ups laden
    print("\n1. Ausstehende Follow-ups laden...")
    pending = get_pending_follow_ups(conn)
    assert len(pending) == 1, f"Sollte 1 ausstehendes Follow-up haben, hat aber {len(pending)}"
    assert pending[0]['project_name'] == "Projekt mit fälligem Follow-up", "Falsches Projekt geladen"
    print(f"{len(pending)} ausstehendes Follow-up gefunden")
    
    # Test 2: Follow-up als erledigt markieren
    print("\n2. Follow-up als erledigt markieren...")
    result = mark_follow_up_completed(conn, project_id_1)
    assert result, "Follow-up konnte nicht als erledigt markiert werden"
    
    pending_after = get_pending_follow_ups(conn)
    assert len(pending_after) == 0, f"Sollte 0 ausstehende Follow-ups haben, hat aber {len(pending_after)}"
    print("Follow-up erfolgreich als erledigt markiert")
    
    conn.close()


def test_lead_status_update():
    """Test: Lead-Status-Aktualisierung basierend auf Angebotsstatus"""
    print("\n=== Test: Lead-Status-Aktualisierung ===")
    
    conn = create_test_db()
    create_offer_tracking_tables(conn)
    
    # Erstelle Test-Daten
    conn.execute("INSERT INTO customers (first_name, last_name, company_name) VALUES (?, ?, ?)",
                 ("Max", "Mustermann", "Test GmbH"))
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    conn.execute("INSERT INTO projects (customer_id, project_name) VALUES (?, ?)",
                 (customer_id, "Test Projekt"))
    project_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Erstelle zugehörigen Lead
    conn.execute("""
        INSERT INTO crm_leads (company_name, contact_person, stage, stage_changed_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, ("Test GmbH", "Max Mustermann", "proposal", datetime.now().isoformat(), datetime.now().isoformat()))
    lead_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    
    # Test 1: Angebot angenommen -> Lead auf "won"
    print("\n1. Angebot angenommen -> Lead auf 'won'...")
    update_offer_status(conn, project_id, 'accepted')
    result = update_lead_status_from_offer(conn, project_id, 'accepted')
    assert result, "Lead-Status-Update fehlgeschlagen"
    
    cursor = conn.cursor()
    cursor.execute("SELECT stage FROM crm_leads WHERE id = ?", (lead_id,))
    lead_stage = cursor.fetchone()[0]
    assert lead_stage == 'won', f"Lead-Status sollte 'won' sein, ist aber '{lead_stage}'"
    print("Lead-Status erfolgreich auf 'won' aktualisiert")
    
    # Test 2: Neues Projekt/Lead für "rejected" Test
    conn.execute("INSERT INTO projects (customer_id, project_name) VALUES (?, ?)",
                 (customer_id, "Test Projekt 2"))
    project_id_2 = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    conn.execute("""
        INSERT INTO crm_leads (company_name, contact_person, stage, stage_changed_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, ("Test GmbH", "Max Mustermann", "proposal", datetime.now().isoformat(), datetime.now().isoformat()))
    lead_id_2 = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    
    print("\n2. Angebot abgelehnt -> Lead auf 'lost'...")
    update_offer_status(conn, project_id_2, 'rejected')
    result = update_lead_status_from_offer(conn, project_id_2, 'rejected')
    assert result, "Lead-Status-Update fehlgeschlagen"
    
    cursor.execute("SELECT stage FROM crm_leads WHERE id = ?", (lead_id_2,))
    lead_stage = cursor.fetchone()[0]
    assert lead_stage == 'lost', f"Lead-Status sollte 'lost' sein, ist aber '{lead_stage}'"
    print("Lead-Status erfolgreich auf 'lost' aktualisiert")
    
    conn.close()


def test_offer_statistics():
    """Test: Angebots-Statistiken"""
    print("\n=== Test: Angebots-Statistiken ===")
    
    conn = create_test_db()
    create_offer_tracking_tables(conn)
    
    # Erstelle Test-Daten
    conn.execute("INSERT INTO customers (first_name, last_name) VALUES (?, ?)",
                 ("Max", "Mustermann"))
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Erstelle Projekte mit verschiedenen Status und Werten
    test_data = [
        ("Projekt 1", "draft", 10000),
        ("Projekt 2", "sent", 20000),
        ("Projekt 3", "sent", 30000),
        ("Projekt 4", "accepted", 40000),
        ("Projekt 5", "accepted", 50000),
        ("Projekt 6", "rejected", 15000),
    ]
    
    for name, status, value in test_data:
        conn.execute("""
            INSERT INTO projects (customer_id, project_name, offer_status, offer_value)
            VALUES (?, ?, ?, ?)
        """, (customer_id, name, status, value))
    
    # Füge ein Follow-up hinzu
    past_date = (datetime.now() - timedelta(days=1)).isoformat()
    conn.execute("""
        INSERT INTO projects (customer_id, project_name, offer_status, follow_up_date, follow_up_completed)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, "Projekt mit Follow-up", "sent", past_date, 0))
    
    conn.commit()
    
    # Lade Statistiken
    print("\n1. Statistiken berechnen...")
    stats = get_offer_statistics(conn)
    
    assert stats['total_offers'] == 7, f"Sollte 7 Angebote haben, hat aber {stats['total_offers']}"
    assert stats['draft'] == 1, f"Sollte 1 Draft haben, hat aber {stats['draft']}"
    assert stats['sent'] == 3, f"Sollte 3 Sent haben, hat aber {stats['sent']}"  # 2 + 1 mit Follow-up
    assert stats['accepted'] == 2, f"Sollte 2 Accepted haben, hat aber {stats['accepted']}"
    assert stats['rejected'] == 1, f"Sollte 1 Rejected haben, hat aber {stats['rejected']}"
    
    # Conversion Rate: 2 accepted / (2 accepted + 1 rejected) = 66.67%
    expected_conversion = 2 / 3 * 100
    assert abs(stats['conversion_rate'] - expected_conversion) < 0.1, \
        f"Conversion Rate sollte ~{expected_conversion:.1f}% sein, ist aber {stats['conversion_rate']:.1f}%"
    
    # Durchschnittlicher Wert: (10000 + 20000 + 30000 + 40000 + 50000 + 15000) / 6 = 27500
    expected_avg = 165000 / 6
    assert abs(stats['avg_offer_value'] - expected_avg) < 1, \
        f"Durchschnittswert sollte ~{expected_avg:.2f} sein, ist aber {stats['avg_offer_value']:.2f}"
    
    assert stats['pending_follow_ups'] == 1, \
        f"Sollte 1 ausstehendes Follow-up haben, hat aber {stats['pending_follow_ups']}"
    
    print("Alle Statistiken korrekt berechnet:")
    print(f"   - Total: {stats['total_offers']}")
    print(f"   - Draft: {stats['draft']}, Sent: {stats['sent']}, Accepted: {stats['accepted']}, Rejected: {stats['rejected']}")
    print(f"   - Conversion Rate: {stats['conversion_rate']:.1f}%")
    print(f"   - Durchschnittswert: {stats['avg_offer_value']:,.2f} €")
    print(f"   - Ausstehende Follow-ups: {stats['pending_follow_ups']}")
    
    conn.close()


def run_all_tests():
    """Führt alle Tests aus"""
    print("=" * 60)
    print("ANGEBOTSVERFOLGUNG (OFFER TRACKING) - TEST SUITE")
    print("=" * 60)
    
    try:
        test_create_offer_tracking_tables()
        test_update_offer_status()
        test_get_all_offers()
        test_follow_up_reminders()
        test_lead_status_update()
        test_offer_statistics()
        
        print("\n" + "=" * 60)
        print("ALLE TESTS ERFOLGREICH BESTANDEN!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\nTEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\nUNERWARTETER FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
