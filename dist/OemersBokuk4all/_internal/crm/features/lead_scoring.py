"""
Lead Scoring Engine
Automatische Bewertung von Leads basierend auf konfigurierbaren Regeln
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Any


def create_lead_scoring_tables(conn: sqlite3.Connection) -> None:
    """Erstellt die Tabellen für Lead Scoring"""
    cursor = conn.cursor()
    
    # Erweitere crm_leads Tabelle um score Feld
    try:
        cursor.execute("""
            ALTER TABLE crm_leads ADD COLUMN score INTEGER DEFAULT 0
        """)
        conn.commit()
        print("Lead Scoring: 'score' Spalte zur crm_leads Tabelle hinzugefügt")
    except sqlite3.OperationalError as e:
        if "duplicate column" not in str(e).lower():
            print(f"Lead Scoring: Warnung beim Hinzufügen der score Spalte: {e}")
    
    # Tabelle für Scoring-Regeln
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_scoring_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT NOT NULL,
            rule_type TEXT NOT NULL,
            condition_field TEXT NOT NULL,
            condition_operator TEXT NOT NULL,
            condition_value TEXT NOT NULL,
            points INTEGER NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabelle für Scoring-Historie
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_scoring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            old_score INTEGER,
            new_score INTEGER,
            score_change INTEGER,
            reason TEXT,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(lead_id) REFERENCES crm_leads(id)
        )
    """)
    
    # Index für schnellere Abfragen
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_lead_scoring_history_lead_id 
        ON lead_scoring_history(lead_id)
    """)
    
    conn.commit()
    print("Lead Scoring: Tabellen erfolgreich erstellt/überprüft")


def initialize_default_scoring_rules(conn: sqlite3.Connection) -> None:
    """Initialisiert Standard-Scoring-Regeln"""
    cursor = conn.cursor()
    
    # Prüfe ob bereits Regeln existieren
    cursor.execute("SELECT COUNT(*) FROM lead_scoring_rules")
    if cursor.fetchone()[0] > 0:
        return  # Regeln bereits vorhanden
    
    default_rules = [
        # Projektgröße-Regeln
        {
            'rule_name': 'Großes Projekt (>50k)',
            'rule_type': 'project_size',
            'condition_field': 'estimated_value',
            'condition_operator': '>',
            'condition_value': '50000',
            'points': 30
        },
        {
            'rule_name': 'Mittleres Projekt (25k-50k)',
            'rule_type': 'project_size',
            'condition_field': 'estimated_value',
            'condition_operator': 'between',
            'condition_value': '25000,50000',
            'points': 20
        },
        {
            'rule_name': 'Kleines Projekt (10k-25k)',
            'rule_type': 'project_size',
            'condition_field': 'estimated_value',
            'condition_operator': 'between',
            'condition_value': '10000,25000',
            'points': 10
        },
        
        # Lead-Quellen-Regeln
        {
            'rule_name': 'Empfehlung',
            'rule_type': 'lead_source',
            'condition_field': 'lead_source',
            'condition_operator': '==',
            'condition_value': 'Empfehlung',
            'points': 25
        },
        {
            'rule_name': 'Website',
            'rule_type': 'lead_source',
            'condition_field': 'lead_source',
            'condition_operator': '==',
            'condition_value': 'Website',
            'points': 15
        },
        {
            'rule_name': 'Social Media',
            'rule_type': 'lead_source',
            'condition_field': 'lead_source',
            'condition_operator': '==',
            'condition_value': 'Social Media',
            'points': 10
        },
        
        # Reaktionszeit-Regeln
        {
            'rule_name': 'Schnelle Reaktion (<24h)',
            'rule_type': 'response_time',
            'condition_field': 'created_at',
            'condition_operator': 'age_hours',
            'condition_value': '24',
            'points': 15
        },
        
        # Engagement-Regeln
        {
            'rule_name': 'Hohe Wahrscheinlichkeit (>70%)',
            'rule_type': 'engagement',
            'condition_field': 'probability',
            'condition_operator': '>',
            'condition_value': '70',
            'points': 20
        },
        {
            'rule_name': 'Mittlere Wahrscheinlichkeit (40-70%)',
            'rule_type': 'engagement',
            'condition_field': 'probability',
            'condition_operator': 'between',
            'condition_value': '40,70',
            'points': 10
        },
        
        # Stage-Regeln
        {
            'rule_name': 'Qualifizierter Lead',
            'rule_type': 'stage',
            'condition_field': 'stage',
            'condition_operator': '==',
            'condition_value': 'qualified',
            'points': 15
        },
        {
            'rule_name': 'Angebot erstellt',
            'rule_type': 'stage',
            'condition_field': 'stage',
            'condition_operator': '==',
            'condition_value': 'proposal',
            'points': 25
        },
        {
            'rule_name': 'In Verhandlung',
            'rule_type': 'stage',
            'condition_field': 'stage',
            'condition_operator': '==',
            'condition_value': 'negotiation',
            'points': 35
        }
    ]
    
    for rule in default_rules:
        cursor.execute("""
            INSERT INTO lead_scoring_rules 
            (rule_name, rule_type, condition_field, condition_operator, condition_value, points)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            rule['rule_name'],
            rule['rule_type'],
            rule['condition_field'],
            rule['condition_operator'],
            rule['condition_value'],
            rule['points']
        ))
    
    conn.commit()
    print(f"Lead Scoring: {len(default_rules)} Standard-Regeln initialisiert")


def calculate_lead_score(conn: sqlite3.Connection, lead_id: int) -> int:
    """Berechnet den Score für einen Lead basierend auf aktiven Regeln"""
    cursor = conn.cursor()
    
    # Lade Lead-Daten
    cursor.execute("SELECT * FROM crm_leads WHERE id = ?", (lead_id))
    lead_row = cursor.fetchone()
    
    if not lead_row:
        return 0
    
    # Konvertiere Row zu Dict
    lead = dict(zip([col[0] for col in cursor.description], lead_row))
    
    # Lade aktive Scoring-Regeln
    cursor.execute("""
        SELECT * FROM lead_scoring_rules 
        WHERE is_active = 1
        ORDER BY rule_type, points DESC
    """)
    
    rules = []
    for row in cursor.fetchall():
        rules.append(dict(zip([col[0] for col in cursor.description], row)))
    
    total_score = 0
    applied_rules = []
    
    for rule in rules:
        points = _evaluate_rule(lead, rule)
        if points > 0:
            total_score += points
            applied_rules.append({
                'rule_name': rule['rule_name'],
                'points': points
            })
    
    # Begrenze Score auf 0-100
    total_score = max(0, min(100, total_score))
    
    return total_score


def _evaluate_rule(lead: dict[str, Any], rule: dict[str, Any]) -> int:
    """Evaluiert eine einzelne Regel gegen Lead-Daten"""
    field = rule['condition_field']
    operator = rule['condition_operator']
    value = rule['condition_value']
    points = rule['points']
    
    # Hole Feldwert aus Lead
    lead_value = lead.get(field)
    
    if lead_value is None:
        return 0
    
    try:
        # Numerische Vergleiche
        if operator == '>':
            if float(lead_value) > float(value):
                return points
        
        elif operator == '<':
            if float(lead_value) < float(value):
                return points
        
        elif operator == '>=':
            if float(lead_value) >= float(value):
                return points
        
        elif operator == '<=':
            if float(lead_value) <= float(value):
                return points
        
        elif operator == '==':
            if str(lead_value).lower() == str(value).lower():
                return points
        
        elif operator == 'between':
            min_val, max_val = value.split(',')
            if float(min_val) <= float(lead_value) <= float(max_val):
                return points
        
        # Spezielle Operatoren
        elif operator == 'age_hours':
            # Prüfe ob Lead jünger als X Stunden ist
            created_at = datetime.fromisoformat(lead_value)
            age_hours = (datetime.now() - created_at).total_seconds() / 3600
            if age_hours < float(value):
                return points
        
        elif operator == 'age_days':
            # Prüfe ob Lead jünger als X Tage ist
            created_at = datetime.fromisoformat(lead_value)
            age_days = (datetime.now() - created_at).days
            if age_days < float(value):
                return points
    
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Lead Scoring: Fehler beim Evaluieren der Regel '{rule['rule_name']}': {e}")
        return 0
    
    return 0


def update_lead_score(conn: sqlite3.Connection, lead_id: int, reason: str = "Manual update") -> bool:
    """Aktualisiert den Score eines Leads und speichert Historie"""
    cursor = conn.cursor()
    
    # Hole aktuellen Score
    cursor.execute("SELECT score FROM crm_leads WHERE id = ?", (lead_id))
    row = cursor.fetchone()
    
    if not row:
        return False
    
    old_score = row[0] or 0
    
    # Berechne neuen Score
    new_score = calculate_lead_score(conn, lead_id)
    
    # Update Lead
    cursor.execute("""
        UPDATE crm_leads 
        SET score = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_score, lead_id))
    
    # Speichere Historie
    cursor.execute("""
        INSERT INTO lead_scoring_history 
        (lead_id, old_score, new_score, score_change, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (lead_id, old_score, new_score, new_score - old_score, reason))
    
    conn.commit()
    
    return True


def update_all_lead_scores(conn: sqlite3.Connection) -> int:
    """Aktualisiert Scores für alle aktiven Leads"""
    cursor = conn.cursor()
    
    # Hole alle aktiven Leads (nicht won/lost)
    cursor.execute("""
        SELECT id FROM crm_leads 
        WHERE stage NOT IN ('won', 'lost')
    """)
    
    lead_ids = [row[0] for row in cursor.fetchall()]
    
    updated_count = 0
    for lead_id in lead_ids:
        if update_lead_score(conn, lead_id, "Batch update"):
            updated_count += 1
    
    return updated_count


def get_high_score_leads(conn: sqlite3.Connection, min_score: int = 70) -> list[dict[str, Any]]:
    """Gibt Leads mit hohem Score zurück"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM crm_leads 
        WHERE score >= ? AND stage NOT IN ('won', 'lost')
        ORDER BY score DESC, estimated_value DESC
    """, (min_score))
    
    leads = []
    for row in cursor.fetchall():
        lead = dict(zip([col[0] for col in cursor.description], row))
        leads.append(lead)
    
    return leads


def get_lead_score_history(conn: sqlite3.Connection, lead_id: int) -> list[dict[str, Any]]:
    """Gibt Score-Historie für einen Lead zurück"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM lead_scoring_history 
        WHERE lead_id = ?
        ORDER BY calculated_at DESC
    """, (lead_id))
    
    history = []
    for row in cursor.fetchall():
        entry = dict(zip([col[0] for col in cursor.description], row))
        history.append(entry)
    
    return history


def get_scoring_rules(conn: sqlite3.Connection, active_only: bool = True) -> list[dict[str, Any]]:
    """Gibt alle Scoring-Regeln zurück"""
    cursor = conn.cursor()
    
    if active_only:
        cursor.execute("""
            SELECT * FROM lead_scoring_rules 
            WHERE is_active = 1
            ORDER BY rule_type, points DESC
        """)
    else:
        cursor.execute("""
            SELECT * FROM lead_scoring_rules 
            ORDER BY rule_type, points DESC
        """)
    
    rules = []
    for row in cursor.fetchall():
        rule = dict(zip([col[0] for col in cursor.description], row))
        rules.append(rule)
    
    return rules


def add_scoring_rule(
    conn: sqlite3.Connection,
    rule_name: str,
    rule_type: str,
    condition_field: str,
    condition_operator: str,
    condition_value: str,
    points: int
) -> int | None:
    """Fügt eine neue Scoring-Regel hinzu"""
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO lead_scoring_rules 
        (rule_name, rule_type, condition_field, condition_operator, condition_value, points)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (rule_name, rule_type, condition_field, condition_operator, condition_value, points))
    
    conn.commit()
    
    return cursor.lastrowid


def update_scoring_rule(
    conn: sqlite3.Connection,
    rule_id: int,
    rule_name: str | None = None,
    points: int | None = None,
    is_active: bool | None = None
) -> bool:
    """Aktualisiert eine Scoring-Regel"""
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if rule_name is not None:
        updates.append("rule_name = ?")
        values.append(rule_name)
    
    if points is not None:
        updates.append("points = ?")
        values.append(points)
    
    if is_active is not None:
        updates.append("is_active = ?")
        values.append(1 if is_active else 0)
    
    if not updates:
        return False
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(rule_id)
    
    cursor.execute(f"""
        UPDATE lead_scoring_rules 
        SET {', '.join(updates)}
        WHERE id = ?
    """, values)
    
    conn.commit()
    
    return cursor.rowcount > 0


def delete_scoring_rule(conn: sqlite3.Connection, rule_id: int) -> bool:
    """Löscht eine Scoring-Regel"""
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM lead_scoring_rules WHERE id = ?", (rule_id))
    conn.commit()
    
    return cursor.rowcount > 0


def get_score_distribution(conn: sqlite3.Connection) -> dict[str, int]:
    """Gibt Verteilung der Scores zurück"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN score >= 80 THEN 'Hot (80-100)'
                WHEN score >= 60 THEN 'Warm (60-79)'
                WHEN score >= 40 THEN 'Medium (40-59)'
                WHEN score >= 20 THEN 'Cold (20-39)'
                ELSE 'Very Cold (0-19)'
            END as score_range,
            COUNT(*) as count
        FROM crm_leads
        WHERE stage NOT IN ('won', 'lost')
        GROUP BY score_range
        ORDER BY MIN(score) DESC
    """)
    
    distribution = {}
    for row in cursor.fetchall():
        distribution[row[0]] = row[1]
    
    return distribution


def check_high_score_notifications(conn: sqlite3.Connection, threshold: int = 80) -> list[dict[str, Any]]:
    """Prüft auf Leads mit hohem Score, die Benachrichtigungen benötigen"""
    cursor = conn.cursor()
    
    # Hole Leads mit hohem Score, die in den letzten 24h aktualisiert wurden
    cursor.execute("""
        SELECT l.*, h.old_score, h.new_score, h.calculated_at
        FROM crm_leads l
        JOIN lead_scoring_history h ON l.id = h.lead_id
        WHERE l.score >= ?
        AND l.stage NOT IN ('won', 'lost')
        AND h.calculated_at >= datetime('now', '-24 hours')
        AND h.new_score >= ?
        AND (h.old_score < ? OR h.old_score IS NULL)
        ORDER BY l.score DESC, h.calculated_at DESC
    """, (threshold, threshold, threshold))
    
    notifications = []
    seen_leads = set()
    
    for row in cursor.fetchall():
        lead = dict(zip([col[0] for col in cursor.description], row))
        
        # Nur erste Benachrichtigung pro Lead
        if lead['id'] not in seen_leads:
            notifications.append(lead)
            seen_leads.add(lead['id'])
    
    return notifications
