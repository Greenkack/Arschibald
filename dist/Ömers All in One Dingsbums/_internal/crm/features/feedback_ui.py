# crm/features/feedback_ui.py
"""
Streamlit UI für Kunden-Feedback und Zufriedenheitsumfragen

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from crm.features import feedback_manager


def render_feedback_management(conn: sqlite3.Connection):
    """Hauptansicht für Feedback-Management.
    
    Args:
        conn: Datenbankverbindung
    """
    st.header("Kunden-Feedback & Zufriedenheitsumfragen")
    
    # Tabs für verschiedene Bereiche
    tab1, tab2, tab3, tab4 = st.tabs([
        "Umfragen", "Auswertungen", " Alerts", " Trigger"
    ])
    
    with tab1:
        render_surveys_tab(conn)
    
    with tab2:
        render_analytics_tab(conn)
    
    with tab3:
        render_alerts_tab(conn)
    
    with tab4:
        render_triggers_tab(conn)


def render_surveys_tab(conn: sqlite3.Connection):
    """Tab für Umfragen-Verwaltung."""
    st.subheader("Umfragen verwalten")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button(" Neue Umfrage", use_container_width=True):
            st.session_state['show_survey_builder'] = True
    
    # Umfrage-Builder anzeigen
    if st.session_state.get('show_survey_builder', False):
        render_survey_builder(conn)
        st.divider()
    
    # Liste aller Umfragen
    surveys = feedback_manager.get_all_surveys(conn)
    
    if not surveys:
        st.info("Noch keine Umfragen erstellt. Erstellen Sie Ihre erste Umfrage!")
        return
    
    for survey in surveys:
        with st.expander(f" {survey['name']}" + (" " if survey['is_active'] else " ⏸")):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**Beschreibung:** {survey.get('description', 'Keine Beschreibung')}")
                st.write(f"**Fragen:** {len(survey['questions'])}")
                st.write(f"**Trigger:** {survey.get('trigger_event', 'Manuell')}")
            
            with col2:
                st.write(f"**Erstellt:** {survey['created_at'][:10]}")
                st.write(f"**Status:** {'Aktiv' if survey['is_active'] else 'Inaktiv'}")
                
                # Statistiken
                stats = feedback_manager.get_survey_statistics(conn, survey['id'])
                st.metric("Antworten", stats.get('total_responses', 0))
            
            with col3:
                if st.button("Auswerten", key=f"analyze_{survey['id']}"):
                    st.session_state['analyze_survey_id'] = survey['id']
                    st.rerun()
                
                if st.button(" Bearbeiten", key=f"edit_{survey['id']}"):
                    st.session_state['edit_survey_id'] = survey['id']
                    st.rerun()
                
                if st.button("Löschen", key=f"delete_{survey['id']}"):
                    if feedback_manager.delete_survey(conn, survey['id']):
                        st.success("Umfrage gelöscht!")
                        st.rerun()


def render_survey_builder(conn: sqlite3.Connection):
    """Umfrage-Builder UI."""
    st.subheader("Umfrage erstellen")
    
    with st.form("survey_builder"):
        # Basis-Informationen
        name = st.text_input("Name der Umfrage*", placeholder="z.B. Kundenzufriedenheit nach Installation")
        description = st.text_area("Beschreibung", placeholder="Kurze Beschreibung der Umfrage")
        
        col1, col2 = st.columns(2)
        with col1:
            trigger_event = st.selectbox(
                "Auslösendes Ereignis",
                ["Manuell", "project_completed", "installation_done", "after_30_days", "after_90_days"],
                help="Wann soll die Umfrage automatisch versendet werden?"
            )
        
        with col2:
            trigger_delay = st.number_input(
                "Verzögerung (Tage)",
                min_value=0,
                max_value=365,
                value=0,
                help="Wie viele Tage nach dem Ereignis soll die Umfrage versendet werden?"
            )
        
        # E-Mail-Vorlage
        st.subheader(" E-Mail-Vorlage")
        email_subject = st.text_input(
            "E-Mail Betreff",
            value="Ihre Meinung ist uns wichtig!",
            placeholder="Betreff der E-Mail"
        )
        email_body = st.text_area(
            "E-Mail Text",
            value="Hallo {{customer_name}},\n\nwir würden uns freuen, wenn Sie sich kurz Zeit nehmen könnten, um uns Feedback zu geben.",
            placeholder="Text der E-Mail (Platzhalter: {{customer_name}}, {{project_name}})",
            height=150
        )
        
        # Fragen-Builder
        st.subheader(" Fragen")
        
        if 'survey_questions' not in st.session_state:
            st.session_state['survey_questions'] = []
        
        # Neue Frage hinzufügen
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            question_type = st.selectbox(
                "Fragetyp",
                ["rating", "text", "multiple_choice", "yes_no"],
                key="new_question_type"
            )
        
        with col2:
            question_text = st.text_input("Fragetext", key="new_question_text")
        
        with col3:
            if st.form_submit_button(" Frage hinzufügen"):
                if question_text:
                    question = {
                        'id': f"q{len(st.session_state['survey_questions']) + 1}",
                        'type': question_type,
                        'text': question_text,
                        'required': True
                    }
                    
                    if question_type == 'multiple_choice':
                        question['options'] = ["Option 1", "Option 2", "Option 3"]
                    
                    st.session_state['survey_questions'].append(question)
        
        # Zeige hinzugefügte Fragen
        if st.session_state['survey_questions']:
            st.write("**Hinzugefügte Fragen:**")
            for i, q in enumerate(st.session_state['survey_questions']):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i+1}. [{q['type']}] {q['text']}")
                with col2:
                    if st.form_submit_button(f"", key=f"remove_q_{i}"):
                        st.session_state['survey_questions'].pop(i)
                        st.rerun()
        
        # Speichern
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button(" Umfrage speichern", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Abbrechen", use_container_width=True)
        
        if submit:
            if not name:
                st.error("Bitte geben Sie einen Namen ein!")
            elif not st.session_state['survey_questions']:
                st.error("Bitte fügen Sie mindestens eine Frage hinzu!")
            else:
                # Erstelle Umfrage
                survey_id = feedback_manager.create_survey(
                    conn,
                    name=name,
                    description=description,
                    questions=st.session_state['survey_questions'],
                    trigger_event=trigger_event if trigger_event != "Manuell" else None,
                    trigger_delay_days=trigger_delay,
                    email_subject=email_subject,
                    email_body=email_body
                )
                
                if survey_id:
                    st.success(f"Umfrage '{name}' erfolgreich erstellt!")
                    st.session_state['survey_questions'] = []
                    st.session_state['show_survey_builder'] = False
                    st.rerun()
                else:
                    st.error("Fehler beim Erstellen der Umfrage!")
        
        if cancel:
            st.session_state['survey_questions'] = []
            st.session_state['show_survey_builder'] = False
            st.rerun()


def render_analytics_tab(conn: sqlite3.Connection):
    """Tab für Auswertungen."""
    st.subheader("Auswertungen")
    
    # Umfrage auswählen
    surveys = feedback_manager.get_all_surveys(conn)
    
    if not surveys:
        st.info("Keine Umfragen vorhanden.")
        return
    
    survey_options = {s['name']: s['id'] for s in surveys}
    selected_survey_name = st.selectbox("Umfrage auswählen", list(survey_options.keys()))
    survey_id = survey_options[selected_survey_name]
    
    # Statistiken laden
    stats = feedback_manager.get_survey_statistics(conn, survey_id)
    
    # KPIs anzeigen
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Antworten", stats.get('total_responses', 0))
    
    with col2:
        avg_rating = stats.get('avg_rating', 0)
        st.metric("Ø Bewertung", f"{avg_rating:.1f}" if avg_rating else "N/A")
    
    with col3:
        response_rate = stats.get('response_rate', 0)
        st.metric("Response Rate", f"{response_rate:.1f}%")
    
    with col4:
        positive_pct = 0
        if stats.get('total_responses', 0) > 0:
            positive_pct = (stats.get('positive_count', 0) / stats['total_responses']) * 100
        st.metric("Positiv", f"{positive_pct:.0f}%")
    
    # Sentiment-Verteilung
    st.subheader("Sentiment-Verteilung")
    
    sentiment_data = {
        'Positiv': stats.get('positive_count', 0),
        'Neutral': stats.get('neutral_count', 0),
        'Negativ': stats.get('negative_count', 0)
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=list(sentiment_data.keys()),
        values=list(sentiment_data.values()),
        marker=dict(colors=['#28a745', '#ffc107', '#dc3545'])
    )])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Trend-Analyse
    st.subheader("Trend-Analyse (letzte 30 Tage)")
    
    trends = feedback_manager.get_trend_analysis(conn, survey_id, days=30)
    
    if trends:
        dates = [t['date'] for t in trends]
        ratings = [t['avg_rating'] for t in trends]
        responses = [t['responses'] for t in trends]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=ratings,
            mode='lines+markers',
            name='Ø Bewertung',
            yaxis='y'
        ))
        fig.add_trace(go.Bar(
            x=dates, y=responses,
            name='Antworten',
            yaxis='y2',
            opacity=0.3
        ))
        
        fig.update_layout(
            yaxis=dict(title='Bewertung', side='left'),
            yaxis2=dict(title='Anzahl Antworten', side='right', overlaying='y'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Noch keine Trend-Daten vorhanden.")
    
    # Einzelne Antworten
    st.subheader("Einzelne Antworten")
    
    sentiment_filter = st.selectbox(
        "Filter nach Sentiment",
        ["Alle", "Positiv", "Neutral", "Negativ"]
    )
    
    filter_map = {
        "Alle": None,
        "Positiv": "positive",
        "Neutral": "neutral",
        "Negativ": "negative"
    }
    
    responses = feedback_manager.get_responses_by_survey(
        conn, survey_id, sentiment_filter=filter_map[sentiment_filter]
    )
    
    if responses:
        for response in responses:
            sentiment_emoji = {
                'positive': '',
                'neutral': '',
                'negative': ''
            }.get(response.get('sentiment', ''), '')
            
            with st.expander(
                f"{sentiment_emoji} {response.get('first_name', '')} {response.get('last_name', '')} - "
                f"{response['submitted_at'][:10]}"
            ):
                st.write(f"**Bewertung:** {'' * (response.get('overall_rating', 0) or 0)}")
                st.write(f"**Projekt:** {response.get('project_name', 'N/A')}")
                
                st.write("**Antworten:**")
                for q_id, answer in response['responses'].items():
                    st.write(f"- {q_id}: {answer}")
    else:
        st.info("Keine Antworten vorhanden.")


def render_alerts_tab(conn: sqlite3.Connection):
    """Tab für Negativ-Feedback Alerts."""
    st.subheader(" Negativ-Feedback Alerts")
    
    days = st.slider("Zeitraum (Tage)", 1, 30, 7)
    
    alerts = feedback_manager.get_negative_feedback_alerts(conn, days=days)
    
    if not alerts:
        st.success("Kein negatives Feedback in diesem Zeitraum!")
        return
    
    st.warning(f"{len(alerts)} negative(s) Feedback gefunden!")
    
    for alert in alerts:
        with st.expander(
            f"{alert.get('first_name', '')} {alert.get('last_name', '')} - "
            f"{alert['submitted_at'][:10]} - {alert.get('overall_rating', 0)}"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Kunde:** {alert.get('first_name', '')} {alert.get('last_name', '')}")
                st.write(f"**E-Mail:** {alert.get('email', 'N/A')}")
                st.write(f"**Projekt:** {alert.get('project_name', 'N/A')}")
            
            with col2:
                st.write(f"**Umfrage:** {alert.get('survey_name', 'N/A')}")
                st.write(f"**Datum:** {alert['submitted_at'][:10]}")
                st.write(f"**Bewertung:** {'' * (alert.get('overall_rating', 0) or 0)}")
            
            st.write("**Antworten:**")
            for q_id, answer in alert['responses'].items():
                st.write(f"- {q_id}: {answer}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(" Kunde kontaktieren", key=f"contact_{alert['id']}"):
                    st.info("E-Mail-Funktion wird geöffnet...")
            
            with col2:
                if st.button("Als bearbeitet markieren", key=f"mark_{alert['id']}"):
                    st.success("Als bearbeitet markiert!")


def render_triggers_tab(conn: sqlite3.Connection):
    """Tab für Trigger-Verwaltung."""
    st.subheader(" Automatische Trigger")
    
    # Ausstehende Trigger
    st.write("**Ausstehende Trigger:**")
    
    pending_triggers = feedback_manager.get_pending_triggers(conn)
    
    if not pending_triggers:
        st.info("Keine ausstehenden Trigger.")
    else:
        for trigger in pending_triggers:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f" {trigger.get('survey_name', 'N/A')}")
                st.write(f" {trigger.get('first_name', '')} {trigger.get('last_name', '')}")
            
            with col2:
                st.write(f" {trigger['scheduled_date']}")
                st.write(f" {trigger.get('email', 'N/A')}")
            
            with col3:
                if st.button(" Jetzt senden", key=f"send_{trigger['id']}"):
                    if feedback_manager.mark_trigger_sent(conn, trigger['id']):
                        st.success("Trigger als versendet markiert!")
                        st.rerun()
    
    # Manuellen Trigger erstellen
    st.divider()
    st.subheader("Manuellen Trigger erstellen")
    
    with st.form("manual_trigger"):
        surveys = feedback_manager.get_all_surveys(conn, active_only=True)
        
        if not surveys:
            st.warning("Keine aktiven Umfragen vorhanden.")
            st.form_submit_button("Erstellen", disabled=True)
        else:
            survey_options = {s['name']: s['id'] for s in surveys}
            selected_survey = st.selectbox("Umfrage", list(survey_options.keys()))
            
            # Hier müsste eine Kunden-Auswahl implementiert werden
            customer_id = st.number_input("Kunden-ID", min_value=1, value=1)
            scheduled_date = st.date_input("Versanddatum", value=datetime.now())
            
            if st.form_submit_button("Trigger erstellen"):
                trigger_id = feedback_manager.create_trigger(
                    conn,
                    survey_id=survey_options[selected_survey],
                    customer_id=customer_id,
                    trigger_event="manual",
                    scheduled_date=scheduled_date.strftime('%Y-%m-%d')
                )
                
                if trigger_id:
                    st.success("Trigger erstellt!")
                    st.rerun()
                else:
                    st.error("Fehler beim Erstellen des Triggers!")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def render_survey_preview(survey: dict):
    """Zeigt eine Vorschau der Umfrage."""
    st.write("**Vorschau:**")
    
    for i, question in enumerate(survey['questions'], 1):
        st.write(f"{i}. {question['text']}")
        
        if question['type'] == 'rating':
            st.write("")
        elif question['type'] == 'text':
            st.text_input("", key=f"preview_text_{i}", disabled=True)
        elif question['type'] == 'multiple_choice':
            options = question.get('options', [])
            st.radio("", options, key=f"preview_mc_{i}", disabled=True)
        elif question['type'] == 'yes_no':
            st.radio("", ["Ja", "Nein"], key=f"preview_yn_{i}", disabled=True)
