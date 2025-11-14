# crm/features/feedback_integration_example.py
"""
Beispiel für die Integration des Feedback-Systems in die CRM-Anwendung

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import sqlite3
from datetime import datetime, timedelta
from crm.features import feedback_manager


def example_create_standard_surveys(conn: sqlite3.Connection):
    """Erstellt Standard-Umfragen für verschiedene Szenarien."""
    
    print("=== Erstelle Standard-Umfragen ===\n")
    
    # 1. Projekt-Abschluss Umfrage
    project_survey_id = feedback_manager.create_survey(
        conn,
        name="Projekt-Abschluss Feedback",
        description="Zufriedenheitsumfrage nach Projektabschluss",
        questions=[
            {
                'id': 'q1',
                'type': 'rating',
                'text': 'Wie zufrieden sind Sie mit der Gesamtleistung?',
                'required': True
            },
            {
                'id': 'q2',
                'type': 'rating',
                'text': 'Wie bewerten Sie die Kommunikation während des Projekts?',
                'required': True
            },
            {
                'id': 'q3',
                'type': 'rating',
                'text': 'Wie zufrieden sind Sie mit der Qualität der Arbeit?',
                'required': True
            },
            {
                'id': 'q4',
                'type': 'multiple_choice',
                'text': 'Würden Sie uns weiterempfehlen?',
                'options': ['Ja, auf jeden Fall', 'Wahrscheinlich ja', 'Vielleicht', 'Eher nicht', 'Nein'],
                'required': True
            },
            {
                'id': 'q5',
                'type': 'text',
                'text': 'Was können wir in Zukunft besser machen?',
                'required': False
            }
        ],
        trigger_event="project_completed",
        trigger_delay_days=7,
        email_subject="Ihre Meinung zu Ihrem Projekt ist uns wichtig!",
        email_body="""Hallo {{first_name}} {{last_name}},

vielen Dank für Ihr Vertrauen in unser Projekt "{{project_name}}".

Wir würden uns sehr freuen, wenn Sie sich 2-3 Minuten Zeit nehmen könnten, 
um uns Feedback zu geben. Ihre Meinung hilft uns, unseren Service kontinuierlich zu verbessern.

Mit freundlichen Grüßen
Ihr Team"""
    )
    
    print(f"✅ Projekt-Abschluss Umfrage erstellt (ID: {project_survey_id})")
    
    # 2. Installation Feedback (schnelles Follow-up)
    installation_survey_id = feedback_manager.create_survey(
        conn,
        name="Installation Feedback",
        description="Kurzes Feedback direkt nach Installation",
        questions=[
            {
                'id': 'q1',
                'type': 'rating',
                'text': 'Wie zufrieden sind Sie mit der Installation?',
                'required': True
            },
            {
                'id': 'q2',
                'type': 'yes_no',
                'text': 'War die Installation pünktlich?',
                'required': True
            },
            {
                'id': 'q3',
                'type': 'yes_no',
                'text': 'Wurde alles sauber hinterlassen?',
                'required': True
            },
            {
                'id': 'q4',
                'type': 'text',
                'text': 'Gibt es etwas, das wir sofort verbessern sollten?',
                'required': False
            }
        ],
        trigger_event="installation_done",
        trigger_delay_days=1,
        email_subject="Wie war Ihre Installation?",
        email_body="""Hallo {{first_name}},

Ihre Installation wurde gestern abgeschlossen. Wir hoffen, alles lief reibungslos!

Bitte nehmen Sie sich kurz Zeit für 4 schnelle Fragen.

Vielen Dank!"""
    )
    
    print(f"✅ Installation Feedback erstellt (ID: {installation_survey_id})")
    
    # 3. Langzeit-Zufriedenheit (nach 90 Tagen)
    longterm_survey_id = feedback_manager.create_survey(
        conn,
        name="Langzeit-Zufriedenheit",
        description="Feedback nach 90 Tagen Nutzung",
        questions=[
            {
                'id': 'q1',
                'type': 'rating',
                'text': 'Wie zufrieden sind Sie nach 3 Monaten Nutzung?',
                'required': True
            },
            {
                'id': 'q2',
                'type': 'rating',
                'text': 'Entspricht die Leistung Ihren Erwartungen?',
                'required': True
            },
            {
                'id': 'q3',
                'type': 'yes_no',
                'text': 'Gab es technische Probleme?',
                'required': True
            },
            {
                'id': 'q4',
                'type': 'text',
                'text': 'Welche Erfahrungen haben Sie gemacht?',
                'required': False
            }
        ],
        trigger_event="after_90_days",
        trigger_delay_days=90,
        email_subject="Wie läuft es nach 3 Monaten?",
        email_body="""Hallo {{first_name}},

Ihr Projekt läuft nun seit 3 Monaten. Wir würden gerne wissen, 
wie Ihre Erfahrungen sind.

Ihr Feedback ist uns wichtig!"""
    )
    
    print(f"✅ Langzeit-Zufriedenheit erstellt (ID: {longterm_survey_id})\n")
    
    return {
        'project': project_survey_id,
        'installation': installation_survey_id,
        'longterm': longterm_survey_id
    }


def example_trigger_workflow(conn: sqlite3.Connection):
    """Demonstriert den kompletten Trigger-Workflow."""
    
    print("=== Trigger-Workflow Beispiel ===\n")
    
    # Simuliere Projektabschluss
    customer_id = 1
    project_id = 1
    
    print(f"📋 Projekt {project_id} für Kunde {customer_id} abgeschlossen")
    
    # Löse automatische Umfragen aus
    trigger_ids = feedback_manager.trigger_survey_on_event(
        conn,
        event_type="project_completed",
        customer_id=customer_id,
        project_id=project_id
    )
    
    print(f"✅ {len(trigger_ids)} Umfrage(n) geplant\n")
    
    # Zeige ausstehende Trigger
    pending = feedback_manager.get_pending_triggers(conn)
    
    print(f"📅 Ausstehende Trigger: {len(pending)}")
    for trigger in pending:
        print(f"  - Umfrage: {trigger.get('survey_name', 'N/A')}")
        print(f"    Kunde: {trigger.get('first_name', '')} {trigger.get('last_name', '')}")
        print(f"    Geplant: {trigger['scheduled_date']}")
        print(f"    Status: {trigger['status']}\n")


def example_response_submission(conn: sqlite3.Connection, survey_id: int):
    """Demonstriert das Einreichen von Antworten."""
    
    print("=== Antwort-Einreichung Beispiel ===\n")
    
    # Simuliere verschiedene Kunden-Antworten
    responses_data = [
        {
            'customer_id': 1,
            'responses': {
                'q1': 5,
                'q2': 5,
                'q3': 5,
                'q4': 'Ja, auf jeden Fall',
                'q5': 'Alles war perfekt!'
            },
            'overall_rating': 5
        },
        {
            'customer_id': 2,
            'responses': {
                'q1': 4,
                'q2': 4,
                'q3': 5,
                'q4': 'Wahrscheinlich ja',
                'q5': 'Kommunikation könnte besser sein'
            },
            'overall_rating': 4
        },
        {
            'customer_id': 3,
            'responses': {
                'q1': 2,
                'q2': 2,
                'q3': 3,
                'q4': 'Eher nicht',
                'q5': 'Viele Verzögerungen, schlechte Kommunikation'
            },
            'overall_rating': 2
        }
    ]
    
    for data in responses_data:
        response_id = feedback_manager.submit_response(
            conn,
            survey_id=survey_id,
            customer_id=data['customer_id'],
            responses=data['responses'],
            overall_rating=data['overall_rating']
        )
        
        sentiment = '😊' if data['overall_rating'] >= 4 else '😐' if data['overall_rating'] == 3 else '😞'
        print(f"{sentiment} Antwort von Kunde {data['customer_id']}: {data['overall_rating']}⭐ (ID: {response_id})")
    
    print()


def example_analytics(conn: sqlite3.Connection, survey_id: int):
    """Demonstriert Analytics-Funktionen."""
    
    print("=== Analytics Beispiel ===\n")
    
    # Gesamtstatistiken
    stats = feedback_manager.get_survey_statistics(conn, survey_id)
    
    print("📊 Gesamtstatistiken:")
    print(f"  Antworten: {stats.get('total_responses', 0)}")
    print(f"  Ø Bewertung: {stats.get('avg_rating', 0):.1f}⭐")
    print(f"  Response Rate: {stats.get('response_rate', 0):.1f}%")
    print(f"  Positiv: {stats.get('positive_count', 0)} ({stats.get('positive_count', 0) / max(stats.get('total_responses', 1), 1) * 100:.0f}%)")
    print(f"  Neutral: {stats.get('neutral_count', 0)}")
    print(f"  Negativ: {stats.get('negative_count', 0)}\n")
    
    # Fragen-Statistiken
    print("📈 Fragen-Statistiken:")
    for q_id in ['q1', 'q2', 'q3']:
        q_stats = feedback_manager.get_question_statistics(conn, survey_id, q_id)
        if q_stats.get('avg'):
            print(f"  {q_id}: Ø {q_stats['avg']:.1f}⭐ (Min: {q_stats['min']}, Max: {q_stats['max']})")
    
    print()


def example_negative_feedback_handling(conn: sqlite3.Connection):
    """Demonstriert Umgang mit negativem Feedback."""
    
    print("=== Negativ-Feedback Handling ===\n")
    
    # Lade negatives Feedback der letzten 7 Tage
    alerts = feedback_manager.get_negative_feedback_alerts(conn, days=7)
    
    if not alerts:
        print("✅ Kein negatives Feedback in den letzten 7 Tagen!\n")
        return
    
    print(f"⚠️ {len(alerts)} negative(s) Feedback gefunden:\n")
    
    for alert in alerts:
        print(f"Kunde: {alert.get('first_name', '')} {alert.get('last_name', '')}")
        print(f"E-Mail: {alert.get('email', 'N/A')}")
        print(f"Projekt: {alert.get('project_name', 'N/A')}")
        print(f"Bewertung: {alert.get('overall_rating', 0)}⭐")
        print(f"Datum: {alert['submitted_at'][:10]}")
        print(f"Antworten:")
        for q_id, answer in alert['responses'].items():
            print(f"  {q_id}: {answer}")
        print()
        
        # Hier würde man:
        # 1. Automatische Aufgabe erstellen (task_manager)
        # 2. Benachrichtigung an Vertrieb senden
        # 3. Kunde kontaktieren
        print("→ Aktion: Aufgabe für Vertrieb erstellt")
        print("→ Aktion: Benachrichtigung versendet")
        print("→ Aktion: Kunde wird kontaktiert\n")


def example_trend_analysis(conn: sqlite3.Connection, survey_id: int):
    """Demonstriert Trend-Analyse."""
    
    print("=== Trend-Analyse ===\n")
    
    trends = feedback_manager.get_trend_analysis(conn, survey_id, days=30)
    
    if not trends:
        print("Noch keine Trend-Daten vorhanden.\n")
        return
    
    print("📈 Trend der letzten 30 Tage:\n")
    print("Datum       | Antworten | Ø Rating | Positiv | Negativ")
    print("-" * 60)
    
    for trend in trends:
        print(f"{trend['date']} | {trend['responses']:9} | {trend['avg_rating']:8.1f} | "
              f"{trend['positive']:7} | {trend['negative']:7}")
    
    print()


def example_complete_workflow():
    """Komplettes Beispiel-Workflow."""
    
    print("\n" + "=" * 70)
    print("FEEDBACK-SYSTEM - KOMPLETTES BEISPIEL")
    print("=" * 70 + "\n")
    
    # Verbindung zur Datenbank
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    # Erstelle Tabellen
    feedback_manager.create_feedback_tables(conn)
    
    # Mock-Tabellen für Fremdschlüssel
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
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            name TEXT
        )
    """)
    
    # Test-Daten
    for i in range(1, 4):
        cursor.execute(
            "INSERT INTO customers VALUES (?, ?, ?, ?)",
            (i, f"Max{i}", f"Mustermann{i}", f"max{i}@example.com")
        )
        cursor.execute(
            "INSERT INTO projects VALUES (?, ?, ?)",
            (i, i, f"Solar Installation {i}")
        )
    
    conn.commit()
    
    # 1. Standard-Umfragen erstellen
    survey_ids = example_create_standard_surveys(conn)
    
    # 2. Trigger-Workflow
    example_trigger_workflow(conn)
    
    # 3. Antworten einreichen
    example_response_submission(conn, survey_ids['project'])
    
    # 4. Analytics
    example_analytics(conn, survey_ids['project'])
    
    # 5. Negativ-Feedback
    example_negative_feedback_handling(conn)
    
    # 6. Trend-Analyse
    example_trend_analysis(conn, survey_ids['project'])
    
    print("=" * 70)
    print("BEISPIEL ABGESCHLOSSEN")
    print("=" * 70 + "\n")
    
    conn.close()


if __name__ == '__main__':
    example_complete_workflow()
