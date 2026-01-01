"""
Lead Scoring UI Module
Benutzeroberfläche für Lead Scoring Verwaltung
"""

import streamlit as st
from datetime import datetime
from typing import Any

try:
    from database import get_db_connection
    from crm.features.lead_scoring import (
        create_lead_scoring_tables,
        initialize_default_scoring_rules,
        get_scoring_rules,
        add_scoring_rule,
        update_scoring_rule,
        delete_scoring_rule,
        update_all_lead_scores,
        get_high_score_leads,
        get_score_distribution,
        check_high_score_notifications,
        get_lead_score_history
    )
    SCORING_AVAILABLE = True
except ImportError as e:
    SCORING_AVAILABLE = False
    print(f"Lead Scoring UI: Import-Fehler: {e}")


def render_lead_scoring_admin(texts: dict[str, str]) -> None:
    """Rendert die Admin-Oberfläche für Lead Scoring Konfiguration"""
    if not SCORING_AVAILABLE:
        st.error("Lead Scoring Modul nicht verfügbar")
        return
    
    st.subheader("Lead Scoring Konfiguration")
    
    conn = get_db_connection()
    if not conn:
        st.error("Datenbankverbindung nicht verfügbar")
        return
    
    try:
        # Initialisiere Tabellen
        create_lead_scoring_tables(conn)
        initialize_default_scoring_rules(conn)
        
        # Tabs für verschiedene Bereiche
        tab1, tab2, tab3 = st.tabs([
            "Übersicht",
            " Regeln verwalten",
            " Scores aktualisieren"
        ])
        
        with tab1:
            _render_scoring_overview(conn)
        
        with tab2:
            _render_rules_management(conn)
        
        with tab3:
            _render_score_update(conn)
    
    finally:
        conn.close()


def _render_scoring_overview(conn) -> None:
    """Rendert Übersicht über Lead Scoring"""
    st.markdown("### Lead Scoring Übersicht")
    
    # Score-Verteilung
    distribution = get_score_distribution(conn)
    
    if distribution:
        st.markdown("#### Score-Verteilung")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        cols = [col1, col2, col3, col4, col5]
        ranges = ['Hot (80-100)', 'Warm (60-79)', 'Medium (40-59)', 'Cold (20-39)', 'Very Cold (0-19)']
        colors = ['#10B981', '#F59E0B', '#3B82F6', '#8B5CF6', '#6B7280']
        
        for i, (col, range_name) in enumerate(zip(cols, ranges)):
            count = distribution.get(range_name, 0)
            with col:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(145deg, {colors[i]} 0%, {colors[i]}dd 100%);
                        padding: 15px;
                        border-radius: 12px;
                        color: white;
                        text-align: center;
                        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                    ">
                        <p style="margin: 0; font-size: 0.85em; opacity: 0.9;">{range_name}</p>
                        <h2 style="margin: 5px 0; font-size: 2.5em;">{count}</h2>
                        <p style="margin: 0; font-size: 0.75em;">Leads</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Keine Leads mit Scores vorhanden")
    
    st.markdown("---")
    
    # High-Score Leads
    st.markdown("####  Top-Leads (Score ≥ 70)")
    
    high_score_leads = get_high_score_leads(conn, min_score=70)
    
    if high_score_leads:
        for lead in high_score_leads[:10]:  # Top 10
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"** {lead['company_name']}**")
                st.caption(f" {lead['contact_person']}")
            
            with col2:
                st.markdown(f"**{lead['estimated_value']:,.0f} €**")
                st.caption(f"Wahrscheinlichkeit: {lead['probability']}%")
            
            with col3:
                stage_icons = {
                    'lead': '',
                    'qualified': '',
                    'proposal': '',
                    'negotiation': ''
                }
                stage_icon = stage_icons.get(lead['stage'], '')
                st.markdown(f"**{stage_icon} {lead['stage'].title()}**")
                st.caption(f" {lead['created_at'][:10]}")
            
            with col4:
                # Score Badge
                score = lead['score']
                if score >= 80:
                    color = "#10B981"
                    label = "Hot"
                elif score >= 60:
                    color = "#F59E0B"
                    label = "Warm"
                else:
                    color = "#3B82F6"
                    label = "Medium"
                
                st.markdown(f"""
                    <div style="
                        background: {color};
                        color: white;
                        padding: 8px;
                        border-radius: 8px;
                        text-align: center;
                        font-weight: bold;
                    ">
                        {score}<br>
                        <span style="font-size: 0.7em;">{label}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
    else:
        st.info("Keine Leads mit Score ≥ 70 vorhanden")
    
    # Benachrichtigungen
    st.markdown("####  Neue High-Score Leads (letzte 24h)")
    
    notifications = check_high_score_notifications(conn, threshold=80)
    
    if notifications:
        for notif in notifications:
            st.success(f"""
                 **{notif['company_name']}** hat einen Score von **{notif['new_score']}** erreicht!
                (vorher: {notif['old_score'] or 0})
                - Kontakt: {notif['contact_person']}
                - Wert: {notif['estimated_value']:,.0f} €
            """)
    else:
        st.info("Keine neuen High-Score Leads in den letzten 24 Stunden")


def _render_rules_management(conn) -> None:
    """Rendert Regel-Verwaltung"""
    st.markdown("###  Scoring-Regeln verwalten")
    
    # Aktuelle Regeln anzeigen
    rules = get_scoring_rules(conn, active_only=False)
    
    if rules:
        st.markdown("#### Aktuelle Regeln")
        
        # Gruppiere nach Regel-Typ
        rule_types = {}
        for rule in rules:
            rule_type = rule['rule_type']
            if rule_type not in rule_types:
                rule_types[rule_type] = []
            rule_types[rule_type].append(rule)
        
        type_names = {
            'project_size': 'Projektgröße',
            'lead_source': ' Lead-Quelle',
            'response_time': '⏱ Reaktionszeit',
            'engagement': 'Engagement',
            'stage': 'Pipeline-Stufe'
        }
        
        for rule_type, type_rules in rule_types.items():
            with st.expander(f"{type_names.get(rule_type, rule_type)} ({len(type_rules)} Regeln)", expanded=True):
                for rule in type_rules:
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{rule['rule_name']}**")
                        st.caption(f"{rule['condition_field']} {rule['condition_operator']} {rule['condition_value']}")
                    
                    with col2:
                        st.markdown(f"**+{rule['points']} Punkte**")
                    
                    with col3:
                        is_active = rule['is_active'] == 1
                        if st.checkbox("Aktiv", value=is_active, key=f"active_{rule['id']}"):
                            if not is_active:
                                update_scoring_rule(conn, rule['id'], is_active=True)
                                st.rerun()
                        else:
                            if is_active:
                                update_scoring_rule(conn, rule['id'], is_active=False)
                                st.rerun()
                    
                    with col4:
                        if st.button("", key=f"delete_rule_{rule['id']}", help="Regel löschen"):
                            if delete_scoring_rule(conn, rule['id']):
                                st.success("Regel gelöscht")
                                st.rerun()
    else:
        st.info("Keine Scoring-Regeln vorhanden")
    
    st.markdown("---")
    
    # Neue Regel hinzufügen
    st.markdown("####  Neue Regel hinzufügen")
    
    with st.form("add_scoring_rule"):
        col1, col2 = st.columns(2)
        
        with col1:
            rule_name = st.text_input("Regelname *", placeholder="z.B. Sehr großes Projekt")
            
            rule_type = st.selectbox(
                "Regel-Typ *",
                options=['project_size', 'lead_source', 'response_time', 'engagement', 'stage', 'custom'],
                format_func=lambda x: {
                    'project_size': 'Projektgröße',
                    'lead_source': ' Lead-Quelle',
                    'response_time': '⏱ Reaktionszeit',
                    'engagement': 'Engagement',
                    'stage': 'Pipeline-Stufe',
                    'custom': 'Benutzerdefiniert'
                }[x]
            )
            
            condition_field = st.selectbox(
                "Feld *",
                options=['estimated_value', 'lead_source', 'probability', 'stage', 'created_at'],
                format_func=lambda x: {
                    'estimated_value': 'Auftragswert',
                    'lead_source': 'Lead-Quelle',
                    'probability': 'Wahrscheinlichkeit',
                    'stage': 'Pipeline-Stufe',
                    'created_at': 'Erstellungsdatum'
                }[x]
            )
        
        with col2:
            condition_operator = st.selectbox(
                "Operator *",
                options=['>', '<', '>=', '<=', '==', 'between', 'age_hours', 'age_days'],
                format_func=lambda x: {
                    '>': 'Größer als',
                    '<': 'Kleiner als',
                    '>=': 'Größer oder gleich',
                    '<=': 'Kleiner oder gleich',
                    '==': 'Gleich',
                    'between': 'Zwischen',
                    'age_hours': 'Alter in Stunden',
                    'age_days': 'Alter in Tagen'
                }[x]
            )
            
            condition_value = st.text_input(
                "Wert *",
                placeholder="z.B. 100000 oder 50000,100000 (für between)",
                help="Bei 'between': Werte mit Komma trennen (min,max)"
            )
            
            points = st.number_input(
                "Punkte *",
                min_value=1,
                max_value=100,
                value=10,
                step=5
            )
        
        submitted = st.form_submit_button(" Regel hinzufügen", type="primary")
        
        if submitted:
            if rule_name and condition_field and condition_operator and condition_value:
                rule_id = add_scoring_rule(
                    conn,
                    rule_name,
                    rule_type,
                    condition_field,
                    condition_operator,
                    condition_value,
                    points
                )
                
                if rule_id:
                    st.success(f"Regel '{rule_name}' erfolgreich hinzugefügt!")
                    st.rerun()
                else:
                    st.error("Fehler beim Hinzufügen der Regel")
            else:
                st.error("Bitte füllen Sie alle Pflichtfelder aus")


def _render_score_update(conn) -> None:
    """Rendert Score-Aktualisierung"""
    st.markdown("###  Scores aktualisieren")
    
    st.info("""
        **Hinweis:** Scores werden automatisch aktualisiert, wenn:
        - Ein Lead erstellt oder bearbeitet wird
        - Die Pipeline-Stufe geändert wird
        - Scoring-Regeln geändert werden
        
        Hier können Sie manuell alle Scores neu berechnen.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Alle Scores neu berechnen", type="primary", use_container_width=True):
            with st.spinner("Berechne Scores..."):
                updated_count = update_all_lead_scores(conn)
                st.success(f"{updated_count} Lead-Scores wurden aktualisiert!")
    
    with col2:
        if st.button("Score-Statistiken anzeigen", use_container_width=True):
            st.session_state['show_score_stats'] = True
    
    if st.session_state.get('show_score_stats', False):
        st.markdown("---")
        st.markdown("#### Score-Statistiken")
        
        cursor = conn.cursor()
        
        # Durchschnittlicher Score
        cursor.execute("""
            SELECT AVG(score) as avg_score, MIN(score) as min_score, MAX(score) as max_score
            FROM crm_leads
            WHERE stage NOT IN ('won', 'lost')
        """)
        
        row = cursor.fetchone()
        if row and row[0] is not None:
            avg_score, min_score, max_score = row
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Durchschnittlicher Score", f"{avg_score:.1f}")
            with col2:
                st.metric("Niedrigster Score", f"{min_score}")
            with col3:
                st.metric("Höchster Score", f"{max_score}")


def render_lead_score_badge(score: int, size: str = "medium") -> None:
    """Rendert ein Score-Badge"""
    if score >= 80:
        color = "#10B981"
        label = "Hot"
    elif score >= 60:
        color = "#F59E0B"
        label = "Warm"
    elif score >= 40:
        color = "#3B82F6"
        label = "Medium"
    elif score >= 20:
        color = "#8B5CF6"
        label = "Cold"
    else:
        color = "#6B7280"
        label = "Very Cold"
    
    if size == "small":
        font_size = "0.8em"
        padding = "4px 8px"
    elif size == "large":
        font_size = "1.2em"
        padding = "12px 16px"
    else:  # medium
        font_size = "1em"
        padding = "8px 12px"
    
    st.markdown(f"""
        <div style="
            background: {color};
            color: white;
            padding: {padding};
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            font-size: {font_size};
            display: inline-block;
        ">
            {score} - {label}
        </div>
    """, unsafe_allow_html=True)


def render_lead_score_history(conn, lead_id: int) -> None:
    """Rendert Score-Historie für einen Lead"""
    st.markdown("#### Score-Historie")
    
    history = get_lead_score_history(conn, lead_id)
    
    if history:
        for entry in history[:10]:  # Letzte 10 Einträge
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                st.caption(entry['calculated_at'][:19])
            
            with col2:
                st.text(f"{entry['old_score'] or 0} → {entry['new_score']}")
            
            with col3:
                change = entry['score_change']
                if change > 0:
                    st.markdown(f"<span style='color: #10B981;'>+{change}</span>", unsafe_allow_html=True)
                elif change < 0:
                    st.markdown(f"<span style='color: #EF4444;'>{change}</span>", unsafe_allow_html=True)
                else:
                    st.text("0")
            
            with col4:
                st.caption(entry['reason'])
    else:
        st.info("Keine Score-Historie vorhanden")
