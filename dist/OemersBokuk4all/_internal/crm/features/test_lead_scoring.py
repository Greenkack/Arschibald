"""
Tests für Lead Scoring Engine
"""

import sqlite3
import tempfile
import os
from datetime import datetime, timedelta

import pytest

from crm.features.lead_scoring import (
    create_lead_scoring_tables,
    initialize_default_scoring_rules,
    calculate_lead_score,
    update_lead_score,
    update_all_lead_scores,
    get_high_score_leads,
    get_lead_score_history,
    get_scoring_rules,
    add_scoring_rule,
    update_scoring_rule,
    delete_scoring_rule,
    get_score_distribution,
    check_high_score_notifications
)


@pytest.fixture
def test_db():
    """Erstellt eine temporäre Test-Datenbank"""
    # Erstelle temporäre Datei
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Erstelle crm_leads Tabelle
    conn.execute("""
        CREATE TABLE crm_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            lead_source TEXT,
            estimated_value REAL DEFAULT 0,
            probability INTEGER DEFAULT 50,
            expected_close_date DATE,
            stage TEXT DEFAULT 'lead',
            stage_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Erstelle Lead Scoring Tabellen
    create_lead_scoring_tables(conn)
    initialize_default_scoring_rules(conn)
    
    yield conn
    
    # Cleanup
    conn.close()
    try:
        os.unlink(db_path)
    except:
        pass


def test_create_lead_scoring_tables(test_db):
    """Test: Tabellen werden korrekt erstellt"""
    cursor = test_db.cursor()
    
    # Prüfe ob score Spalte existiert
    cursor.execute("PRAGMA table_info(crm_leads)")
    columns = [row[1] for row in cursor.fetchall()]
    assert 'score' in columns
    
    # Prüfe ob lead_scoring_rules Tabelle existiert
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lead_scoring_rules'")
    assert cursor.fetchone() is not None
    
    # Prüfe ob lead_scoring_history Tabelle existiert
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lead_scoring_history'")
    assert cursor.fetchone() is not None


def test_initialize_default_scoring_rules(test_db):
    """Test: Standard-Regeln werden initialisiert"""
    rules = get_scoring_rules(test_db, active_only=False)
    
    assert len(rules) > 0
    
    # Prüfe ob verschiedene Regel-Typen vorhanden sind
    rule_types = set(rule['rule_type'] for rule in rules)
    assert 'project_size' in rule_types
    assert 'lead_source' in rule_types
    assert 'engagement' in rule_types
    assert 'stage' in rule_types


def test_calculate_lead_score_basic(test_db):
    """Test: Score-Berechnung für einfachen Lead"""
    cursor = test_db.cursor()
    
    # Erstelle Test-Lead
    cursor.execute("""
        INSERT INTO crm_leads 
        (company_name, contact_person, lead_source, estimated_value, probability, stage)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Test GmbH', 'Max Mustermann', 'Empfehlung', 60000, 80, 'qualified'))
    
    lead_id = cursor.lastrowid
    test_db.commit()
    
    # Berechne Score
    score = calculate_lead_score(test_db, lead_id)
    
    # Score sollte > 0 sein (Empfehlung + großes Projekt + hohe Wahrscheinlichkeit + qualified)
    assert score > 0
    assert score <= 100


def test_calculate_lead_score_high_value(test_db):
    """Test: Hoher Score für wertvollen Lead"""
    cursor = test_db.cursor()
    
    # Erstelle hochwertigen Lead
    cursor.execute("""
        INSERT INTO crm_leads 
        (company_name, contact_person, lead_source, estimated_value, probability, stage)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Premium GmbH', 'VIP Kunde', 'Empfehlung', 100000, 90, 'negotiation'))
    
    lead_id = cursor.lastrowid
    test_db.commit()
    
    score = calculate_lead_score(test_db, lead_id)
    
    # Sollte hohen Score haben (>70)
    assert score >= 70


def test_calculate_lead_score_low_value(test_db):
    """Test: Niedriger Score für weniger wertvollen Lead"""
    cursor = test_db.cursor()
    
    # Erstelle niedrigwertigen Lead
    cursor.execute("""
        INSERT INTO crm_leads 
        (company_name, contact_person, lead_source, estimated_value, probability, stage)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Klein GmbH', 'Test Kunde', 'Kaltakquise', 5000, 20, 'lead'))
    
    lead_id = cursor.lastrowid
    test_db.commit()
    
    score = calculate_lead_score(test_db, lead_id)
    
    # Sollte niedrigen Score haben (<40)
    assert score < 40


def test_update_lead_score(test_db):
    """Test: Score-Update und Historie"""
    cursor = test_db.cursor()
    
    # Erstelle Lead
    cursor.execute("""
        INSERT INTO crm_leads 
        (company_name, contact_person, lead_source, estimated_value, probability, stage, score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('Test GmbH', 'Max Mustermann', 'Website', 30000, 50, 'lead', 0))
    
    lead_id = cursor.lastrowid
    test_db.commit()
    
    # Update Score
    success = update_lead_score(test_db, lead_id, "Test update")
    
    assert success
    
    # Prüfe ob Score aktualisiert wurde
    cursor.execute("SELECT score FROM crm_leads WHERE id = ?", (lead_id))
    new_score = cursor.fetchone()[0]
    assert new_score > 0
    
    # Prüfe Historie
    history = get_lead_score_history(test_db, lead_id)
    assert len(history) == 1
    assert history[0]['old_score'] == 0
    assert history[0]['new_score'] == new_score
    assert history[0]['reason'] == "Test update"


def test_update_all_lead_scores(test_db):
    """Test: Batch-Update aller Scores"""
    cursor = test_db.cursor()
    
    # Erstelle mehrere Leads
    for i in range(5):
        cursor.execute("""
            INSERT INTO crm_leads 
            (company_name, contact_person, lead_source, estimated_value, probability, stage)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (f'Firma {i}', f'Person {i}', 'Website', 25000 + i*10000, 50, 'lead'))
    
    test_db.commit()
    
    # Update alle Scores
    updated_count = update_all_lead_scores(test_db)
    
    assert updated_count == 5
    
    # Prüfe ob alle Scores gesetzt wurden
    cursor.execute("SELECT COUNT(*) FROM crm_leads WHERE score > 0")
    assert cursor.fetchone()[0] == 5


def test_get_high_score_leads(test_db):
    """Test: Abrufen von High-Score Leads"""
    cursor = test_db.cursor()
    
    # Erstelle Leads mit verschiedenen Scores
    leads_data = [
        ('High Score GmbH', 'VIP', 'Empfehlung', 100000, 90, 'negotiation'),
        ('Medium Score GmbH', 'Normal', 'Website', 30000, 60, 'qualified'),
        ('Low Score GmbH', 'Test', 'Kaltakquise', 10000, 30, 'lead')
    ]
    
    for data in leads_data:
        cursor.execute("""
            INSERT INTO crm_leads 
            (company_name, contact_person, lead_source, estimated_value, probability, stage)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)
        lead_id = cursor.lastrowid
        update_lead_score(test_db, lead_id, "Initial score")
    
    test_db.commit()
    
    # Hole High-Score Leads (>= 70)
    high_score_leads = get_high_score_leads(test_db, min_score=70)
    
    # Mindestens der High-Score Lead sollte dabei sein
    assert len(high_score_leads) >= 1
    assert all(lead['score'] >= 70 for lead in high_score_leads)


def test_add_scoring_rule(test_db):
    """Test: Neue Regel hinzufügen"""
    initial_count = len(get_scoring_rules(test_db))
    
    rule_id = add_scoring_rule(
        test_db,
        "Test Regel",
        "custom",
        "estimated_value",
        ">",
        "75000",
        40
    )
    
    assert rule_id is not None
    
    # Prüfe ob Regel hinzugefügt wurde
    rules = get_scoring_rules(test_db)
    assert len(rules) == initial_count + 1
    
    # Finde neue Regel
    new_rule = next((r for r in rules if r['id'] == rule_id), None)
    assert new_rule is not None
    assert new_rule['rule_name'] == "Test Regel"
    assert new_rule['points'] == 40


def test_update_scoring_rule(test_db):
    """Test: Regel aktualisieren"""
    # Erstelle Regel
    rule_id = add_scoring_rule(
        test_db,
        "Original Name",
        "custom",
        "probability",
        ">",
        "80",
        20
    )
    
    # Update Regel
    success = update_scoring_rule(
        test_db,
        rule_id,
        rule_name="Updated Name",
        points=30,
        is_active=False
    )
    
    assert success
    
    # Prüfe Updates
    rules = get_scoring_rules(test_db, active_only=False)
    updated_rule = next((r for r in rules if r['id'] == rule_id), None)
    
    assert updated_rule is not None
    assert updated_rule['rule_name'] == "Updated Name"
    assert updated_rule['points'] == 30
    assert updated_rule['is_active'] == 0


def test_delete_scoring_rule(test_db):
    """Test: Regel löschen"""
    # Erstelle Regel
    rule_id = add_scoring_rule(
        test_db,
        "To Delete",
        "custom",
        "stage",
        "==",
        "won",
        50
    )
    
    initial_count = len(get_scoring_rules(test_db, active_only=False))
    
    # Lösche Regel
    success = delete_scoring_rule(test_db, rule_id)
    
    assert success
    
    # Prüfe ob gelöscht
    rules = get_scoring_rules(test_db, active_only=False)
    assert len(rules) == initial_count - 1
    assert not any(r['id'] == rule_id for r in rules)


def test_get_score_distribution(test_db):
    """Test: Score-Verteilung"""
    cursor = test_db.cursor()
    
    # Erstelle Leads mit verschiedenen Scores
    test_leads = [
        ('Hot Lead', 'Person 1', 'Empfehlung', 100000, 90, 'negotiation'),  # Hot
        ('Warm Lead', 'Person 2', 'Website', 50000, 70, 'proposal'),  # Warm
        ('Medium Lead', 'Person 3', 'Social Media', 30000, 50, 'qualified'),  # Medium
        ('Cold Lead', 'Person 4', 'Kaltakquise', 15000, 30, 'lead'),  # Cold
    ]
    
    for data in test_leads:
        cursor.execute("""
            INSERT INTO crm_leads 
            (company_name, contact_person, lead_source, estimated_value, probability, stage)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)
        lead_id = cursor.lastrowid
        update_lead_score(test_db, lead_id, "Initial")
    
    test_db.commit()
    
    # Hole Verteilung
    distribution = get_score_distribution(test_db)
    
    assert isinstance(distribution, dict)
    assert len(distribution) > 0
    
    # Summe sollte Anzahl Leads entsprechen
    total = sum(distribution.values())
    assert total == 4


def test_check_high_score_notifications(test_db):
    """Test: Benachrichtigungen für High-Score Leads"""
    cursor = test_db.cursor()
    
    # Erstelle Lead mit niedrigem initialen Score
    cursor.execute("""
        INSERT INTO crm_leads 
        (company_name, contact_person, lead_source, estimated_value, probability, stage, score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('Test GmbH', 'Max Mustermann', 'Website', 30000, 50, 'lead', 40))
    
    lead_id = cursor.lastrowid
    test_db.commit()
    
    # Update zu hohem Score
    cursor.execute("""
        UPDATE crm_leads 
        SET estimated_value = 100000, probability = 90, stage = 'negotiation', lead_source = 'Empfehlung'
        WHERE id = ?
    """, (lead_id))
    test_db.commit()
    
    # Update Score (sollte jetzt hoch sein)
    update_lead_score(test_db, lead_id, "Score increased")
    
    # Prüfe Benachrichtigungen
    notifications = check_high_score_notifications(test_db, threshold=80)
    
    # Sollte Benachrichtigung für diesen Lead geben
    assert len(notifications) >= 1
    assert any(n['id'] == lead_id for n in notifications)


def test_score_calculation_with_custom_rule(test_db):
    """Test: Score-Berechnung mit benutzerdefinierter Regel"""
    # Füge custom Regel hinzu
    add_scoring_rule(
        test_db,
        "Sehr hohe Wahrscheinlichkeit",
        "custom",
        "probability",
        ">",
        "85",
        25
    )
    
    cursor = test_db.cursor()
    
    # Erstelle Lead der die Regel erfüllt
    cursor.execute("""
        INSERT INTO crm_leads 
        (company_name, contact_person, lead_source, estimated_value, probability, stage)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Custom Rule Test', 'Test Person', 'Website', 30000, 90, 'qualified'))
    
    lead_id = cursor.lastrowid
    test_db.commit()
    
    # Berechne Score
    score = calculate_lead_score(test_db, lead_id)
    
    # Score sollte die custom Regel berücksichtigen
    assert score > 0
    
    # Erstelle Lead der die Regel NICHT erfüllt
    cursor.execute("""
        INSERT INTO crm_leads 
        (company_name, contact_person, lead_source, estimated_value, probability, stage)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('No Custom Rule', 'Test Person 2', 'Website', 30000, 50, 'qualified'))
    
    lead_id_2 = cursor.lastrowid
    test_db.commit()
    
    score_2 = calculate_lead_score(test_db, lead_id_2)
    
    # Erster Lead sollte höheren Score haben
    assert score > score_2


def test_score_history_tracking(test_db):
    """Test: Score-Historie wird korrekt verfolgt"""
    cursor = test_db.cursor()
    
    # Erstelle Lead
    cursor.execute("""
        INSERT INTO crm_leads 
        (company_name, contact_person, lead_source, estimated_value, probability, stage, score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('History Test', 'Test Person', 'Website', 20000, 40, 'lead', 0))
    
    lead_id = cursor.lastrowid
    test_db.commit()
    
    # Mehrere Score-Updates
    update_lead_score(test_db, lead_id, "First update")
    
    cursor.execute("""
        UPDATE crm_leads 
        SET estimated_value = 50000, stage = 'qualified'
        WHERE id = ?
    """, (lead_id))
    test_db.commit()
    
    update_lead_score(test_db, lead_id, "Second update")
    
    cursor.execute("""
        UPDATE crm_leads 
        SET probability = 80, stage = 'proposal'
        WHERE id = ?
    """, (lead_id))
    test_db.commit()
    
    update_lead_score(test_db, lead_id, "Third update")
    
    # Prüfe Historie
    history = get_lead_score_history(test_db, lead_id)
    
    # Sollte 3 Einträge haben
    assert len(history) == 3
    
    # Alle Einträge sollten verschiedene Reasons haben
    reasons = [h['reason'] for h in history]
    assert "First update" in reasons
    assert "Second update" in reasons
    assert "Third update" in reasons
    
    # Scores sollten generell steigen (letzter Score sollte höchster sein)
    scores = [h['new_score'] for h in history]
    assert max(scores) > min(scores)  # Es gab eine Steigerung


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
