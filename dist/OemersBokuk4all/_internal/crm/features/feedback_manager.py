# crm/features/feedback_manager.py
"""
Kunden-Feedback und Zufriedenheitsumfragen für CRM
Ermöglicht Erstellung und Verwaltung von Umfragen mit automatischem Versand

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Any


def create_feedback_tables(conn: sqlite3.Connection) -> None:
    """Erstellt die Tabellen für Feedback und Umfragen.
    
    Args:
        conn: SQLite Datenbankverbindung
    """
    cursor = conn.cursor()
    
    try:
        # 1. Tabelle: feedback_surveys (Umfragen)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                questions_json TEXT NOT NULL,
                trigger_event TEXT,
                trigger_delay_days INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                email_subject TEXT,
                email_body TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT
            )
        """)
        print("DB: Tabelle 'feedback_surveys' erstellt/überprüft.")
        
        # 2. Tabelle: feedback_responses (Antworten)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                project_id INTEGER,
                responses_json TEXT NOT NULL,
                overall_rating INTEGER,
                sentiment TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (survey_id) REFERENCES feedback_surveys(id) ON DELETE CASCADE,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            )
        """)
        print("DB: Tabelle 'feedback_responses' erstellt/überprüft.")
        
        # 3. Tabelle: feedback_triggers (Automatische Trigger)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                project_id INTEGER,
                trigger_event TEXT NOT NULL,
                scheduled_date DATE NOT NULL,
                status TEXT DEFAULT 'pending',
                sent_at TIMESTAMP,
                response_id INTEGER,
                reminder_sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (survey_id) REFERENCES feedback_surveys(id) ON DELETE CASCADE,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (response_id) REFERENCES feedback_responses(id) ON DELETE SET NULL
            )
        """)
        print("DB: Tabelle 'feedback_triggers' erstellt/überprüft.")
        
        # 4. Indizes für Performance
        indices = [
            ("idx_feedback_surveys_active", "feedback_surveys", "is_active"),
            ("idx_feedback_responses_survey", "feedback_responses", "survey_id"),
            ("idx_feedback_responses_customer", "feedback_responses", "customer_id"),
            ("idx_feedback_responses_rating", "feedback_responses", "overall_rating"),
            ("idx_feedback_responses_sentiment", "feedback_responses", "sentiment"),
            ("idx_feedback_triggers_status", "feedback_triggers", "status"),
            ("idx_feedback_triggers_scheduled", "feedback_triggers", "scheduled_date"),
        ]
        
        for index_name, table_name, column_name in indices:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})")
            except sqlite3.OperationalError:
                pass  # Index existiert bereits
        
        conn.commit()
        print("DB: Feedback-Tabellen erfolgreich erstellt/aktualisiert.")
        
    except Exception as e:
        print(f"DB FEHLER beim Erstellen der Feedback-Tabellen: {e}")
        conn.rollback()
        raise


# ============================================================================
# SURVEY CRUD OPERATIONS
# ============================================================================

def create_survey(
    conn: sqlite3.Connection,
    name: str,
    questions: list[dict],
    trigger_event: str | None = None,
    trigger_delay_days: int = 0,
    description: str | None = None,
    email_subject: str | None = None,
    email_body: str | None = None,
    is_active: bool = True,
    created_by: str | None = None
) -> int | None:
    """Erstellt eine neue Umfrage.
    
    Args:
        conn: Datenbankverbindung
        name: Name der Umfrage
        questions: Liste von Fragen (dict mit type, text, options, required)
        trigger_event: Auslösendes Ereignis (z.B. 'project_completed')
        trigger_delay_days: Verzögerung in Tagen nach Ereignis
        description: Beschreibung der Umfrage
        email_subject: E-Mail Betreff
        email_body: E-Mail Text
        is_active: Ob Umfrage aktiv ist
        created_by: Ersteller
        
    Returns:
        ID der erstellten Umfrage oder None bei Fehler
    """
    cursor = conn.cursor()
    
    try:
        questions_json = json.dumps(questions, ensure_ascii=False)
        
        cursor.execute("""
            INSERT INTO feedback_surveys (
                name, description, questions_json, trigger_event, trigger_delay_days,
                is_active, email_subject, email_body, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, description, questions_json, trigger_event, trigger_delay_days,
            1 if is_active else 0, email_subject, email_body, created_by
        ))
        
        conn.commit()
        survey_id = cursor.lastrowid
        print(f"Umfrage '{name}' erstellt (ID: {survey_id})")
        return survey_id
        
    except Exception as e:
        print(f"FEHLER beim Erstellen der Umfrage: {e}")
        conn.rollback()
        return None


def get_survey_by_id(conn: sqlite3.Connection, survey_id: int) -> dict | None:
    """Lädt eine Umfrage anhand der ID.
    
    Args:
        conn: Datenbankverbindung
        survey_id: ID der Umfrage
        
    Returns:
        Umfrage als Dictionary oder None
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM feedback_surveys WHERE id = ?
        """, (survey_id))
        
        row = cursor.fetchone()
        if row:
            survey = dict(row)
            # Parse JSON
            survey['questions'] = json.loads(survey['questions_json'])
            return survey
        return None
        
    except Exception as e:
        print(f"FEHLER beim Laden der Umfrage: {e}")
        return None


def get_all_surveys(conn: sqlite3.Connection, active_only: bool = False) -> list[dict]:
    """Lädt alle Umfragen.
    
    Args:
        conn: Datenbankverbindung
        active_only: Nur aktive Umfragen laden
        
    Returns:
        Liste von Umfragen
    """
    cursor = conn.cursor()
    
    try:
        query = "SELECT * FROM feedback_surveys"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query)
        surveys = []
        
        for row in cursor.fetchall():
            survey = dict(row)
            survey['questions'] = json.loads(survey['questions_json'])
            surveys.append(survey)
        
        return surveys
        
    except Exception as e:
        print(f"FEHLER beim Laden der Umfragen: {e}")
        return []


def update_survey(
    conn: sqlite3.Connection,
    survey_id: int,
    **kwargs
) -> bool:
    """Aktualisiert eine Umfrage.
    
    Args:
        conn: Datenbankverbindung
        survey_id: ID der Umfrage
        **kwargs: Zu aktualisierende Felder
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    cursor = conn.cursor()
    
    try:
        # Konvertiere questions zu JSON falls vorhanden
        if 'questions' in kwargs:
            kwargs['questions_json'] = json.dumps(kwargs.pop('questions'), ensure_ascii=False)
        
        # Baue UPDATE Query
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['name', 'description', 'questions_json', 'trigger_event', 
                      'trigger_delay_days', 'is_active', 'email_subject', 'email_body', 'updated_by']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(survey_id)
        
        query = f"UPDATE feedback_surveys SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"FEHLER beim Aktualisieren der Umfrage: {e}")
        conn.rollback()
        return False


def delete_survey(conn: sqlite3.Connection, survey_id: int) -> bool:
    """Löscht eine Umfrage.
    
    Args:
        conn: Datenbankverbindung
        survey_id: ID der Umfrage
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM feedback_surveys WHERE id = ?", (survey_id))
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"FEHLER beim Löschen der Umfrage: {e}")
        conn.rollback()
        return False


# ============================================================================
# RESPONSE CRUD OPERATIONS
# ============================================================================

def submit_response(
    conn: sqlite3.Connection,
    survey_id: int,
    customer_id: int,
    responses: dict,
    overall_rating: int | None = None,
    project_id: int | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None
) -> int | None:
    """Speichert eine Umfrage-Antwort.
    
    Args:
        conn: Datenbankverbindung
        survey_id: ID der Umfrage
        customer_id: ID des Kunden
        responses: Antworten als Dictionary
        overall_rating: Gesamtbewertung (1-5)
        project_id: Zugehöriges Projekt
        ip_address: IP-Adresse des Absenders
        user_agent: User Agent
        
    Returns:
        ID der Antwort oder None bei Fehler
    """
    cursor = conn.cursor()
    
    try:
        responses_json = json.dumps(responses, ensure_ascii=False)
        
        # Berechne Sentiment basierend auf Rating
        sentiment = None
        if overall_rating:
            if overall_rating >= 4:
                sentiment = 'positive'
            elif overall_rating == 3:
                sentiment = 'neutral'
            else:
                sentiment = 'negative'
        
        cursor.execute("""
            INSERT INTO feedback_responses (
                survey_id, customer_id, project_id, responses_json,
                overall_rating, sentiment, ip_address, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            survey_id, customer_id, project_id, responses_json,
            overall_rating, sentiment, ip_address, user_agent
        ))
        
        conn.commit()
        response_id = cursor.lastrowid
        
        # Update trigger status falls vorhanden
        cursor.execute("""
            UPDATE feedback_triggers 
            SET status = 'completed', response_id = ?
            WHERE survey_id = ? AND customer_id = ? AND status = 'sent'
        """, (response_id, survey_id, customer_id))
        conn.commit()
        
        print(f"Feedback-Antwort gespeichert (ID: {response_id})")
        return response_id
        
    except Exception as e:
        print(f"FEHLER beim Speichern der Antwort: {e}")
        conn.rollback()
        return None


def get_responses_by_survey(
    conn: sqlite3.Connection,
    survey_id: int,
    sentiment_filter: str | None = None
) -> list[dict]:
    """Lädt alle Antworten zu einer Umfrage.
    
    Args:
        conn: Datenbankverbindung
        survey_id: ID der Umfrage
        sentiment_filter: Filter nach Sentiment ('positive', 'neutral', 'negative')
        
    Returns:
        Liste von Antworten
    """
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT fr.*, c.first_name, c.last_name, c.email, p.name as project_name
            FROM feedback_responses fr
            LEFT JOIN customers c ON fr.customer_id = c.id
            LEFT JOIN projects p ON fr.project_id = p.id
            WHERE fr.survey_id = ?
        """
        params = [survey_id]
        
        if sentiment_filter:
            query += " AND fr.sentiment = ?"
            params.append(sentiment_filter)
        
        query += " ORDER BY fr.submitted_at DESC"
        
        cursor.execute(query, params)
        responses = []
        
        for row in cursor.fetchall():
            response = dict(row)
            response['responses'] = json.loads(response['responses_json'])
            responses.append(response)
        
        return responses
        
    except Exception as e:
        print(f"FEHLER beim Laden der Antworten: {e}")
        return []


def get_responses_by_customer(conn: sqlite3.Connection, customer_id: int) -> list[dict]:
    """Lädt alle Antworten eines Kunden.
    
    Args:
        conn: Datenbankverbindung
        customer_id: ID des Kunden
        
    Returns:
        Liste von Antworten
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT fr.*, fs.name as survey_name
            FROM feedback_responses fr
            LEFT JOIN feedback_surveys fs ON fr.survey_id = fs.id
            WHERE fr.customer_id = ?
            ORDER BY fr.submitted_at DESC
        """, (customer_id))
        
        responses = []
        for row in cursor.fetchall():
            response = dict(row)
            response['responses'] = json.loads(response['responses_json'])
            responses.append(response)
        
        return responses
        
    except Exception as e:
        print(f"FEHLER beim Laden der Kunden-Antworten: {e}")
        return []


# ============================================================================
# TRIGGER OPERATIONS
# ============================================================================

def create_trigger(
    conn: sqlite3.Connection,
    survey_id: int,
    customer_id: int,
    trigger_event: str,
    scheduled_date: str,
    project_id: int | None = None
) -> int | None:
    """Erstellt einen automatischen Trigger für eine Umfrage.
    
    Args:
        conn: Datenbankverbindung
        survey_id: ID der Umfrage
        customer_id: ID des Kunden
        trigger_event: Auslösendes Ereignis
        scheduled_date: Geplantes Versanddatum (YYYY-MM-DD)
        project_id: Zugehöriges Projekt
        
    Returns:
        ID des Triggers oder None bei Fehler
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO feedback_triggers (
                survey_id, customer_id, project_id, trigger_event, scheduled_date
            ) VALUES (?, ?, ?, ?, ?)
        """, (survey_id, customer_id, project_id, trigger_event, scheduled_date))
        
        conn.commit()
        trigger_id = cursor.lastrowid
        print(f"Feedback-Trigger erstellt (ID: {trigger_id})")
        return trigger_id
        
    except Exception as e:
        print(f"FEHLER beim Erstellen des Triggers: {e}")
        conn.rollback()
        return None


def get_pending_triggers(conn: sqlite3.Connection, date: str | None = None) -> list[dict]:
    """Lädt alle ausstehenden Trigger.
    
    Args:
        conn: Datenbankverbindung
        date: Datum bis zu dem Trigger geladen werden (Standard: heute)
        
    Returns:
        Liste von Triggern
    """
    cursor = conn.cursor()
    
    try:
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT ft.*, fs.name as survey_name, fs.email_subject, fs.email_body,
                   c.first_name, c.last_name, c.email
            FROM feedback_triggers ft
            LEFT JOIN feedback_surveys fs ON ft.survey_id = fs.id
            LEFT JOIN customers c ON ft.customer_id = c.id
            WHERE ft.status = 'pending' AND ft.scheduled_date <= ?
            ORDER BY ft.scheduled_date ASC
        """, (date))
        
        triggers = [dict(row) for row in cursor.fetchall()]
        return triggers
        
    except Exception as e:
        print(f"FEHLER beim Laden der Trigger: {e}")
        return []


def mark_trigger_sent(conn: sqlite3.Connection, trigger_id: int) -> bool:
    """Markiert einen Trigger als versendet.
    
    Args:
        conn: Datenbankverbindung
        trigger_id: ID des Triggers
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE feedback_triggers 
            SET status = 'sent', sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (trigger_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"FEHLER beim Aktualisieren des Triggers: {e}")
        conn.rollback()
        return False


def send_reminder(conn: sqlite3.Connection, trigger_id: int) -> bool:
    """Sendet eine Erinnerung für einen Trigger.
    
    Args:
        conn: Datenbankverbindung
        trigger_id: ID des Triggers
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE feedback_triggers 
            SET reminder_sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (trigger_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"FEHLER beim Senden der Erinnerung: {e}")
        conn.rollback()
        return False


# ============================================================================
# ANALYTICS & REPORTING
# ============================================================================

def get_survey_statistics(conn: sqlite3.Connection, survey_id: int) -> dict:
    """Berechnet Statistiken für eine Umfrage.
    
    Args:
        conn: Datenbankverbindung
        survey_id: ID der Umfrage
        
    Returns:
        Dictionary mit Statistiken
    """
    cursor = conn.cursor()
    
    try:
        # Gesamtzahl Antworten
        cursor.execute("""
            SELECT COUNT(*) as total_responses,
                   AVG(overall_rating) as avg_rating,
                   COUNT(CASE WHEN sentiment = 'positive' THEN 1 END) as positive_count,
                   COUNT(CASE WHEN sentiment = 'neutral' THEN 1 END) as neutral_count,
                   COUNT(CASE WHEN sentiment = 'negative' THEN 1 END) as negative_count
            FROM feedback_responses
            WHERE survey_id = ?
        """, (survey_id))
        
        stats = dict(cursor.fetchone())
        
        # Response Rate berechnen
        cursor.execute("""
            SELECT COUNT(*) as total_sent
            FROM feedback_triggers
            WHERE survey_id = ? AND status IN ('sent', 'completed')
        """, (survey_id))
        
        sent_row = cursor.fetchone()
        total_sent = sent_row['total_sent'] if sent_row else 0
        
        if total_sent > 0:
            stats['response_rate'] = (stats['total_responses'] / total_sent) * 100
        else:
            stats['response_rate'] = 0
        
        stats['total_sent'] = total_sent
        
        return stats
        
    except Exception as e:
        print(f"FEHLER beim Berechnen der Statistiken: {e}")
        return {}


def get_trend_analysis(
    conn: sqlite3.Connection,
    survey_id: int,
    days: int = 30
) -> list[dict]:
    """Analysiert Trends über einen Zeitraum.
    
    Args:
        conn: Datenbankverbindung
        survey_id: ID der Umfrage
        days: Anzahl Tage zurück
        
    Returns:
        Liste mit Trend-Daten pro Tag
    """
    cursor = conn.cursor()
    
    try:
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT DATE(submitted_at) as date,
                   COUNT(*) as responses,
                   AVG(overall_rating) as avg_rating,
                   COUNT(CASE WHEN sentiment = 'positive' THEN 1 END) as positive,
                   COUNT(CASE WHEN sentiment = 'negative' THEN 1 END) as negative
            FROM feedback_responses
            WHERE survey_id = ? AND DATE(submitted_at) >= ?
            GROUP BY DATE(submitted_at)
            ORDER BY date ASC
        """, (survey_id, start_date))
        
        trends = [dict(row) for row in cursor.fetchall()]
        return trends
        
    except Exception as e:
        print(f"FEHLER bei der Trend-Analyse: {e}")
        return []


def get_negative_feedback_alerts(conn: sqlite3.Connection, days: int = 7) -> list[dict]:
    """Lädt negatives Feedback der letzten Tage für Alerts.
    
    Args:
        conn: Datenbankverbindung
        days: Anzahl Tage zurück
        
    Returns:
        Liste mit negativem Feedback
    """
    cursor = conn.cursor()
    
    try:
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT fr.*, fs.name as survey_name,
                   c.first_name, c.last_name, c.email,
                   p.name as project_name
            FROM feedback_responses fr
            LEFT JOIN feedback_surveys fs ON fr.survey_id = fs.id
            LEFT JOIN customers c ON fr.customer_id = c.id
            LEFT JOIN projects p ON fr.project_id = p.id
            WHERE fr.sentiment = 'negative' 
            AND DATE(fr.submitted_at) >= ?
            ORDER BY fr.submitted_at DESC
        """, (start_date))
        
        alerts = []
        for row in cursor.fetchall():
            alert = dict(row)
            alert['responses'] = json.loads(alert['responses_json'])
            alerts.append(alert)
        
        return alerts
        
    except Exception as e:
        print(f"FEHLER beim Laden der Negativ-Alerts: {e}")
        return []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def trigger_survey_on_event(
    conn: sqlite3.Connection,
    event_type: str,
    customer_id: int,
    project_id: int | None = None
) -> list[int]:
    """Löst Umfragen basierend auf einem Ereignis aus.
    
    Args:
        conn: Datenbankverbindung
        event_type: Typ des Ereignisses (z.B. 'project_completed')
        customer_id: ID des Kunden
        project_id: ID des Projekts
        
    Returns:
        Liste der erstellten Trigger-IDs
    """
    cursor = conn.cursor()
    trigger_ids = []
    
    try:
        # Finde alle aktiven Umfragen mit diesem Trigger
        cursor.execute("""
            SELECT id, trigger_delay_days
            FROM feedback_surveys
            WHERE trigger_event = ? AND is_active = 1
        """, (event_type))
        
        surveys = cursor.fetchall()
        
        for survey in surveys:
            survey_id = survey['id']
            delay_days = survey['trigger_delay_days'] or 0
            
            # Berechne Versanddatum
            scheduled_date = (datetime.now() + timedelta(days=delay_days)).strftime('%Y-%m-%d')
            
            # Erstelle Trigger
            trigger_id = create_trigger(
                conn, survey_id, customer_id, event_type, scheduled_date, project_id
            )
            
            if trigger_id:
                trigger_ids.append(trigger_id)
        
        return trigger_ids
        
    except Exception as e:
        print(f"FEHLER beim Auslösen der Umfragen: {e}")
        return []


def get_question_statistics(conn: sqlite3.Connection, survey_id: int, question_id: str) -> dict:
    """Berechnet Statistiken für eine spezifische Frage.
    
    Args:
        conn: Datenbankverbindung
        survey_id: ID der Umfrage
        question_id: ID der Frage
        
    Returns:
        Dictionary mit Statistiken
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT responses_json
            FROM feedback_responses
            WHERE survey_id = ?
        """, (survey_id))
        
        answers = []
        for row in cursor.fetchall():
            responses = json.loads(row['responses_json'])
            if question_id in responses:
                answers.append(responses[question_id])
        
        # Berechne Statistiken basierend auf Antworttyp
        stats = {
            'total_answers': len(answers),
            'answers': answers
        }
        
        # Für numerische Antworten
        numeric_answers = [a for a in answers if isinstance(a, (int, float))]
        if numeric_answers:
            stats['avg'] = sum(numeric_answers) / len(numeric_answers)
            stats['min'] = min(numeric_answers)
            stats['max'] = max(numeric_answers)
        
        # Für Multiple-Choice: Zähle Häufigkeiten
        if answers and isinstance(answers[0], str):
            from collections import Counter
            stats['frequency'] = dict(Counter(answers))
        
        return stats
        
    except Exception as e:
        print(f"FEHLER bei Fragen-Statistiken: {e}")
        return {}
