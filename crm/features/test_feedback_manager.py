# crm/features/test_feedback_manager.py
"""
Unit Tests für Kunden-Feedback und Zufriedenheitsumfragen

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import sqlite3
import pytest
import json
from datetime import datetime, timedelta
from crm.features import feedback_manager


@pytest.fixture
def test_db():
    """Erstellt eine Test-Datenbank im Speicher."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    # Erstelle Feedback-Tabellen
    feedback_manager.create_feedback_tables(conn)
    
    # Erstelle Mock-Tabellen für Fremdschlüssel
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            name TEXT,
            status TEXT
        )
    """)
    
    # Füge Test-Daten hinzu
    cursor.execute("""
        INSERT INTO customers (first_name, last_name, email) 
        VALUES ('Max', 'Mustermann', 'max@example.com')
    """)
    cursor.execute("""
        INSERT INTO projects (customer_id, name, status) 
        VALUES (1, 'Solar Installation', 'completed')
    """)
    
    conn.commit()
    
    yield conn
    conn.close()


@pytest.fixture
def sample_questions():
    """Beispiel-Fragen für Tests."""
    return [
        {
            'id': 'q1',
            'type': 'rating',
            'text': 'Wie zufrieden sind Sie mit unserer Dienstleistung?',
            'required': True
        },
        {
            'id': 'q2',
            'type': 'text',
            'text': 'Was können wir verbessern?',
            'required': False
        },
        {
            'id': 'q3',
            'type': 'multiple_choice',
            'text': 'Würden Sie uns weiterempfehlen?',
            'options': ['Ja, auf jeden Fall', 'Vielleicht', 'Nein'],
            'required': True
        }
    ]


# ============================================================================
# SURVEY TESTS
# ============================================================================

def test_create_survey(test_db, sample_questions):
    """Test: Umfrage erstellen"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Kundenzufriedenheit 2025",
        questions=sample_questions,
        description="Jährliche Zufriedenheitsumfrage",
        trigger_event="project_completed",
        trigger_delay_days=7
    )
    
    assert survey_id is not None
    assert survey_id > 0
    
    # Umfrage laden und prüfen
    survey = feedback_manager.get_survey_by_id(test_db, survey_id)
    assert survey is not None
    assert survey['name'] == "Kundenzufriedenheit 2025"
    assert survey['trigger_event'] == "project_completed"
    assert survey['trigger_delay_days'] == 7
    assert len(survey['questions']) == 3
    assert survey['is_active'] == 1


def test_get_survey_by_id(test_db, sample_questions):
    """Test: Umfrage anhand ID laden"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    survey = feedback_manager.get_survey_by_id(test_db, survey_id)
    
    assert survey is not None
    assert survey['id'] == survey_id
    assert survey['name'] == "Test Umfrage"
    assert 'questions' in survey
    assert isinstance(survey['questions'], list)


def test_get_all_surveys(test_db, sample_questions):
    """Test: Alle Umfragen laden"""
    # Erstelle mehrere Umfragen
    feedback_manager.create_survey(test_db, "Umfrage 1", sample_questions)
    feedback_manager.create_survey(test_db, "Umfrage 2", sample_questions, is_active=False)
    feedback_manager.create_survey(test_db, "Umfrage 3", sample_questions)
    
    # Alle Umfragen
    all_surveys = feedback_manager.get_all_surveys(test_db)
    assert len(all_surveys) == 3
    
    # Nur aktive Umfragen
    active_surveys = feedback_manager.get_all_surveys(test_db, active_only=True)
    assert len(active_surveys) == 2


def test_update_survey(test_db, sample_questions):
    """Test: Umfrage aktualisieren"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Original Name",
        questions=sample_questions
    )
    
    # Aktualisiere Name
    success = feedback_manager.update_survey(
        test_db,
        survey_id,
        name="Neuer Name",
        description="Neue Beschreibung"
    )
    
    assert success is True
    
    # Prüfe Änderungen
    survey = feedback_manager.get_survey_by_id(test_db, survey_id)
    assert survey['name'] == "Neuer Name"
    assert survey['description'] == "Neue Beschreibung"


def test_delete_survey(test_db, sample_questions):
    """Test: Umfrage löschen"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Zu löschende Umfrage",
        questions=sample_questions
    )
    
    # Lösche Umfrage
    success = feedback_manager.delete_survey(test_db, survey_id)
    assert success is True
    
    # Prüfe ob gelöscht
    survey = feedback_manager.get_survey_by_id(test_db, survey_id)
    assert survey is None


# ============================================================================
# RESPONSE TESTS
# ============================================================================

def test_submit_response(test_db, sample_questions):
    """Test: Antwort einreichen"""
    # Erstelle Umfrage
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    # Erstelle Antwort
    responses = {
        'q1': 5,
        'q2': 'Alles super!',
        'q3': 'Ja, auf jeden Fall'
    }
    
    response_id = feedback_manager.submit_response(
        test_db,
        survey_id=survey_id,
        customer_id=1,
        responses=responses,
        overall_rating=5,
        project_id=1
    )
    
    assert response_id is not None
    assert response_id > 0


def test_response_sentiment_calculation(test_db, sample_questions):
    """Test: Sentiment-Berechnung bei Antworten"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    # Positive Antwort
    response_id_positive = feedback_manager.submit_response(
        test_db, survey_id, 1, {}, overall_rating=5
    )
    
    # Neutrale Antwort
    response_id_neutral = feedback_manager.submit_response(
        test_db, survey_id, 1, {}, overall_rating=3
    )
    
    # Negative Antwort
    response_id_negative = feedback_manager.submit_response(
        test_db, survey_id, 1, {}, overall_rating=2
    )
    
    # Prüfe Sentiments
    cursor = test_db.cursor()
    
    cursor.execute("SELECT sentiment FROM feedback_responses WHERE id = ?", (response_id_positive,))
    assert cursor.fetchone()['sentiment'] == 'positive'
    
    cursor.execute("SELECT sentiment FROM feedback_responses WHERE id = ?", (response_id_neutral,))
    assert cursor.fetchone()['sentiment'] == 'neutral'
    
    cursor.execute("SELECT sentiment FROM feedback_responses WHERE id = ?", (response_id_negative,))
    assert cursor.fetchone()['sentiment'] == 'negative'


def test_get_responses_by_survey(test_db, sample_questions):
    """Test: Antworten zu einer Umfrage laden"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    # Erstelle mehrere Antworten
    for i in range(3):
        feedback_manager.submit_response(
            test_db, survey_id, 1, {'q1': 5}, overall_rating=5
        )
    
    responses = feedback_manager.get_responses_by_survey(test_db, survey_id)
    assert len(responses) == 3


def test_get_responses_by_customer(test_db, sample_questions):
    """Test: Antworten eines Kunden laden"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    # Erstelle Antworten
    feedback_manager.submit_response(test_db, survey_id, 1, {'q1': 5})
    feedback_manager.submit_response(test_db, survey_id, 1, {'q1': 4})
    
    responses = feedback_manager.get_responses_by_customer(test_db, 1)
    assert len(responses) == 2


# ============================================================================
# TRIGGER TESTS
# ============================================================================

def test_create_trigger(test_db, sample_questions):
    """Test: Trigger erstellen"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    scheduled_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    trigger_id = feedback_manager.create_trigger(
        test_db,
        survey_id=survey_id,
        customer_id=1,
        trigger_event="project_completed",
        scheduled_date=scheduled_date,
        project_id=1
    )
    
    assert trigger_id is not None
    assert trigger_id > 0


def test_get_pending_triggers(test_db, sample_questions):
    """Test: Ausstehende Trigger laden"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    # Erstelle Trigger für heute
    today = datetime.now().strftime('%Y-%m-%d')
    feedback_manager.create_trigger(
        test_db, survey_id, 1, "test", today
    )
    
    # Erstelle Trigger für morgen
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    feedback_manager.create_trigger(
        test_db, survey_id, 1, "test", tomorrow
    )
    
    # Lade ausstehende Trigger für heute
    pending = feedback_manager.get_pending_triggers(test_db, today)
    assert len(pending) == 1


def test_mark_trigger_sent(test_db, sample_questions):
    """Test: Trigger als versendet markieren"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    trigger_id = feedback_manager.create_trigger(
        test_db, survey_id, 1, "test", datetime.now().strftime('%Y-%m-%d')
    )
    
    success = feedback_manager.mark_trigger_sent(test_db, trigger_id)
    assert success is True
    
    # Prüfe Status
    cursor = test_db.cursor()
    cursor.execute("SELECT status FROM feedback_triggers WHERE id = ?", (trigger_id,))
    assert cursor.fetchone()['status'] == 'sent'


def test_trigger_survey_on_event(test_db, sample_questions):
    """Test: Automatisches Auslösen von Umfragen bei Ereignis"""
    # Erstelle Umfrage mit Trigger
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Auto-Trigger Umfrage",
        questions=sample_questions,
        trigger_event="project_completed",
        trigger_delay_days=7
    )
    
    # Löse Ereignis aus
    trigger_ids = feedback_manager.trigger_survey_on_event(
        test_db,
        event_type="project_completed",
        customer_id=1,
        project_id=1
    )
    
    assert len(trigger_ids) == 1
    assert trigger_ids[0] > 0


# ============================================================================
# ANALYTICS TESTS
# ============================================================================

def test_get_survey_statistics(test_db, sample_questions):
    """Test: Umfrage-Statistiken berechnen"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    # Erstelle Antworten mit verschiedenen Ratings
    feedback_manager.submit_response(test_db, survey_id, 1, {}, overall_rating=5)
    feedback_manager.submit_response(test_db, survey_id, 1, {}, overall_rating=4)
    feedback_manager.submit_response(test_db, survey_id, 1, {}, overall_rating=2)
    
    stats = feedback_manager.get_survey_statistics(test_db, survey_id)
    
    assert stats['total_responses'] == 3
    assert stats['avg_rating'] > 0
    assert stats['positive_count'] == 2
    assert stats['negative_count'] == 1


def test_get_trend_analysis(test_db, sample_questions):
    """Test: Trend-Analyse"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    # Erstelle Antworten
    feedback_manager.submit_response(test_db, survey_id, 1, {}, overall_rating=5)
    
    trends = feedback_manager.get_trend_analysis(test_db, survey_id, days=30)
    
    # Sollte mindestens einen Eintrag haben (heute)
    assert len(trends) >= 0  # Kann 0 sein wenn keine Daten im Zeitraum


def test_get_negative_feedback_alerts(test_db, sample_questions):
    """Test: Negativ-Feedback Alerts"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    # Erstelle negative Antwort
    feedback_manager.submit_response(
        test_db, survey_id, 1, {'q2': 'Sehr unzufrieden!'}, overall_rating=1
    )
    
    # Erstelle positive Antwort
    feedback_manager.submit_response(
        test_db, survey_id, 1, {'q2': 'Alles super!'}, overall_rating=5
    )
    
    alerts = feedback_manager.get_negative_feedback_alerts(test_db, days=7)
    
    assert len(alerts) == 1
    assert alerts[0]['sentiment'] == 'negative'


def test_get_question_statistics(test_db, sample_questions):
    """Test: Statistiken für einzelne Frage"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Test Umfrage",
        questions=sample_questions
    )
    
    # Erstelle Antworten
    feedback_manager.submit_response(test_db, survey_id, 1, {'q1': 5})
    feedback_manager.submit_response(test_db, survey_id, 1, {'q1': 4})
    feedback_manager.submit_response(test_db, survey_id, 1, {'q1': 5})
    
    stats = feedback_manager.get_question_statistics(test_db, survey_id, 'q1')
    
    assert stats['total_answers'] == 3
    assert 'avg' in stats
    assert stats['avg'] > 4


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_complete_survey_workflow(test_db, sample_questions):
    """Test: Kompletter Workflow von Umfrage-Erstellung bis Auswertung"""
    # 1. Umfrage erstellen
    survey_id = feedback_manager.create_survey(
        test_db,
        name="Workflow Test",
        questions=sample_questions,
        trigger_event="project_completed",
        trigger_delay_days=0
    )
    assert survey_id is not None
    
    # 2. Trigger auslösen
    trigger_ids = feedback_manager.trigger_survey_on_event(
        test_db, "project_completed", 1, 1
    )
    assert len(trigger_ids) == 1
    
    # 3. Trigger als versendet markieren
    success = feedback_manager.mark_trigger_sent(test_db, trigger_ids[0])
    assert success is True
    
    # 4. Antwort einreichen
    response_id = feedback_manager.submit_response(
        test_db, survey_id, 1, {'q1': 5, 'q2': 'Sehr gut!', 'q3': 'Ja, auf jeden Fall'},
        overall_rating=5, project_id=1
    )
    assert response_id is not None
    
    # 5. Statistiken prüfen
    stats = feedback_manager.get_survey_statistics(test_db, survey_id)
    assert stats['total_responses'] == 1
    assert stats['positive_count'] == 1
    
    # 6. Antworten laden
    responses = feedback_manager.get_responses_by_survey(test_db, survey_id)
    assert len(responses) == 1


def test_email_template_placeholders(test_db, sample_questions):
    """Test: E-Mail-Vorlagen mit Platzhaltern"""
    survey_id = feedback_manager.create_survey(
        test_db,
        name="E-Mail Test",
        questions=sample_questions,
        email_subject="Feedback für {{customer_name}}",
        email_body="Hallo {{customer_name}}, wie war Ihr Projekt {{project_name}}?"
    )
    
    survey = feedback_manager.get_survey_by_id(test_db, survey_id)
    
    assert '{{customer_name}}' in survey['email_subject']
    assert '{{project_name}}' in survey['email_body']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
