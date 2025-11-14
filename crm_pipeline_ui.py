"""
CRM Pipeline UI Module
Autor: Gemini Ultra
Datum: 2025-06-21
"""

from datetime import datetime, timedelta
from typing import Any

import streamlit as st

try:
    from database import get_all_active_customers, get_db_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Lead Scoring Integration
try:
    from crm.features.lead_scoring import (
        create_lead_scoring_tables,
        initialize_default_scoring_rules,
        update_lead_score,
        get_high_score_leads,
        check_high_score_notifications
    )
    from crm.features.lead_scoring_ui import render_lead_score_badge
    LEAD_SCORING_AVAILABLE = True
except ImportError:
    LEAD_SCORING_AVAILABLE = False


class CRMPipeline:
    """CRM Pipeline Management für Sales-Prozess"""
    def __getstate__(self):
        """Ermöglicht Pickle-Serialisierung für Session State"""
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        """Ermöglicht Pickle-Deserialisierung für Session State"""
        self.__dict__.update(state)
    

    def __init__(self):
        self.pipeline_stages = {
            'lead': {
                'name': 'Lead',
                'description': 'Neuer Interessent',
                'color': '#94A3B8',
                'icon': '',
                'order': 1
            },
            'qualified': {
                'name': 'Qualifiziert',
                'description': 'Lead wurde qualifiziert',
                'color': '#3B82F6',
                'icon': '',
                'order': 2
            },
            'proposal': {
                'name': 'Angebot',
                'description': 'Angebot wurde erstellt',
                'color': '#F59E0B',
                'icon': '',
                'order': 3
            },
            'negotiation': {
                'name': 'Verhandlung',
                'description': 'In Verhandlung',
                'color': '#8B5CF6',
                'icon': '🤝',
                'order': 4
            },
            'won': {
                'name': 'Gewonnen',
                'description': 'Auftrag gewonnen',
                'color': '#10B981',
                'icon': '',
                'order': 5
            },
            'lost': {
                'name': 'Verloren',
                'description': 'Auftrag verloren',
                'color': '#EF4444',
                'icon': '',
                'order': 6
            }
        }

        self.lead_sources = [
            'Website', 'Empfehlung', 'Social Media', 'Kaltakquise',
            'Messe', 'Online-Werbung', 'Printmedien', 'Sonstiges'
        ]

    def render_pipeline_interface(self, texts: dict[str, str]):
        """Rendert die Pipeline-Hauptoberfläche"""
        st.header(" CRM Sales Pipeline")

        if not DATABASE_AVAILABLE:
            st.error("Datenbankverbindung nicht verfügbar")
            return

        # Tabs für verschiedene Ansichten
        tab1, tab2, tab3, tab4 = st.tabs(
            [" Pipeline-Übersicht", " Neuer Lead", " Lead-Liste", " Analytics"])

        with tab1:
            self._render_pipeline_overview()

        with tab2:
            self._render_new_lead_form()

        with tab3:
            self._render_lead_list()

        with tab4:
            self._render_pipeline_analytics()

    def _render_pipeline_overview(self):
        """Rendert die Pipeline-Übersicht im Kanban-Stil"""
        st.subheader("[TARGET] Pipeline-Übersicht")

        # Pipeline-Statistiken mit modernen Cards
        stats = self._get_pipeline_statistics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
                <div style="
                    background: linear-gradient(145deg, #808080 0%, #6a6a6a 100%);
                    padding: 15px;
                    border-radius: 12px;
                    color: white;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                ">
                    <p style="margin: 0; font-size: 0.9em; opacity: 0.9;">Gesamte Leads</p>
                    <h2 style="margin: 5px 0; font-size: 2em;">{}</h2>
                    <p style="margin: 0; font-size: 0.8em;">+{} diesen Monat ↗️</p>
                </div>
            """.format(stats['total_leads'], stats['new_leads_this_month']), unsafe_allow_html=True)

        with col2:
            st.markdown("""
                <div style="
                    background: linear-gradient(145deg, #808080 0%, #6a6a6a 100%);
                    padding: 15px;
                    border-radius: 12px;
                    color: white;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                ">
                    <p style="margin: 0; font-size: 0.9em; opacity: 0.9;">Pipeline-Wert</p>
                    <h2 style="margin: 5px 0; font-size: 2em;">{:,.0f}€</h2>
                    <p style="margin: 0; font-size: 0.8em;">Ø {:,.0f}€</p>
                </div>
            """.format(stats['total_pipeline_value'], stats['avg_deal_value']), unsafe_allow_html=True)

        with col3:
            st.markdown("""
                <div style="
                    background: linear-gradient(145deg, #808080 0%, #6a6a6a 100%);
                    padding: 15px;
                    border-radius: 12px;
                    color: white;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                ">
                    <p style="margin: 0; font-size: 0.9em; opacity: 0.9;">Conversion Rate</p>
                    <h2 style="margin: 5px 0; font-size: 2em;">{:.1f}%</h2>
                    <p style="margin: 0; font-size: 0.8em;">{:+.1f}% Trend</p>
                </div>
            """.format(stats['conversion_rate'], stats['monthly_conversion_change']), unsafe_allow_html=True)

        with col4:
            st.markdown("""
                <div style="
                    background: linear-gradient(145deg, #808080 0%, #6a6a6a 100%);
                    padding: 15px;
                    border-radius: 12px;
                    color: white;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                ">
                    <p style="margin: 0; font-size: 0.9em; opacity: 0.9;">Ø Verkaufszyklus</p>
                    <h2 style="margin: 5px 0; font-size: 2em;">{} Tage</h2>
                    <p style="margin: 0; font-size: 0.8em;">{:+.0f} Tage Trend</p>
                </div>
            """.format(stats['avg_sales_cycle'], stats['cycle_trend']), unsafe_allow_html=True)

        st.markdown("---")

        # Kanban-Board mit verbessertem Design
        stages = sorted(
            self.pipeline_stages.items(),
            key=lambda x: x[1]['order'])
        active_stages = [(k, v) for k, v in stages if k not in ['won', 'lost']]

        # Aktive Pipeline-Stufen
        cols = st.columns(len(active_stages))

        for idx, (stage_key, stage_info) in enumerate(active_stages):
            with cols[idx]:
                leads_in_stage = self._get_leads_by_stage(stage_key)
                stage_value = sum(lead.get('estimated_value', 0)
                                  for lead in leads_in_stage)

                st.markdown(f"""
                    <div style="
                        background: linear-gradient(145deg, #808080 0%, #6a6a6a 100%);
                        padding: 15px;
                        border-radius: 12px;
                        margin-bottom: 15px;
                        border-left: 4px solid #555;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                        color: white;
                    ">
                        <h4 style="margin: 0; font-size: 1.1em;">
                            {stage_info['icon']} {stage_info['name']}
                        </h4>
                        <p style="margin: 8px 0 0 0; font-size: 0.85em; opacity: 0.9;">
                            <strong>{len(leads_in_stage)}</strong> Leads • <strong>{stage_value:,.0f} €</strong>
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                # Leads in dieser Stufe anzeigen
                for lead in leads_in_stage[:5]:  # Max 5 Leads pro Spalte
                    self._render_pipeline_lead_card(lead, stage_key)

                if len(leads_in_stage) > 5:
                    st.caption(f"+ {len(leads_in_stage) - 5} weitere Leads")

        # Geschlossene Deals (separate Sektion)
        st.markdown("---")
        st.subheader("[WINNER] Geschlossene Deals (letzte 30 Tage)")

        col1, col2 = st.columns(2)

        with col1:
            won_leads = self._get_recent_closed_leads('won')
            st.markdown("### [OK] Gewonnene Aufträge")
            if won_leads:
                for lead in won_leads[:3]:
                    st.markdown(f"""
                        <div style="
                            background-color: #d4edda;
                            border-left: 4px solid #28a745;
                            padding: 10px;
                            border-radius: 5px;
                            margin-bottom: 8px;
                        ">
                            <strong>{lead['company_name']}</strong><br>
                            <span style="color: #28a745; font-size: 1.1em;">{lead['estimated_value']:,.0f} €</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Keine gewonnenen Aufträge in den letzten 30 Tagen")

        with col2:
            lost_leads = self._get_recent_closed_leads('lost')
            st.markdown("### [ERROR] Verlorene Aufträge")
            if lost_leads:
                for lead in lost_leads[:3]:
                    st.markdown(f"""
                        <div style="
                            background-color: #f8d7da;
                            border-left: 4px solid #dc3545;
                            padding: 10px;
                            border-radius: 5px;
                            margin-bottom: 8px;
                        ">
                            <strong>{lead['company_name']}</strong><br>
                            <span style="color: #dc3545; font-size: 1.1em;">{lead['estimated_value']:,.0f} €</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Keine verlorenen Aufträge in den letzten 30 Tagen")

    def _render_pipeline_lead_card(self, lead: dict[str, Any], stage_key: str):
        """Rendert eine Lead-Karte in der Pipeline"""
        days_in_stage = (
            datetime.now() -
            datetime.fromisoformat(
                lead['stage_changed_at'])).days

        # Score Badge Farbe bestimmen
        score = lead.get('score', 0)
        if score >= 80:
            score_color = "#10B981"
            score_label = "🔥"
        elif score >= 60:
            score_color = "#F59E0B"
            score_label = "[POWER]"
        elif score >= 40:
            score_color = "#3B82F6"
            score_label = "[CHART]"
        else:
            score_color = "#6B7280"
            score_label = "❄️"

        with st.container():
            # Moderne Lead-Karte mit Score
            st.markdown(f"""
                <div style="
                    background: linear-gradient(145deg, #808080 0%, #6a6a6a 100%);
                    border: 1px solid #666;
                    border-left: 3px solid #555;
                    padding: 12px;
                    border-radius: 8px;
                    margin: 8px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                    color: white;
                    position: relative;
                ">
                    <div style="position: absolute; top: 8px; right: 8px;">
                        <span style="
                            background: {score_color};
                            color: white;
                            padding: 4px 8px;
                            border-radius: 12px;
                            font-weight: bold;
                            font-size: 0.75em;
                        ">{score_label} {score}</span>
                    </div>
                    <h5 style="margin: 0 0 8px 0; font-size: 0.95em; padding-right: 50px;">
                        🏢 {lead['company_name']}
                    </h5>
                    <div style="margin: 5px 0; font-size: 0.8em;">
                        <span style="
                            background: rgba(255,255,255,0.2);
                            color: white;
                            padding: 3px 8px;
                            border-radius: 12px;
                            font-weight: bold;
                        ">[MONEY] {lead['estimated_value']:,.0f} €</span>
                    </div>
                    <p style="margin: 8px 0 0 0; font-size: 0.75em; opacity: 0.8;">
                        ⏱️ {days_in_stage} Tage in Stufe
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Aktions-Buttons (klein und modern)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                        "👁️",
                        key=f"view_{
                            lead['id']}",
                        help="Details anzeigen"):
                    st.session_state.selected_lead_id = lead['id']
                    st.rerun()

            with col2:
                if st.button(
                        "↔️",
                        key=f"move_{
                            lead['id']}",
                        help="Stufe ändern"):
                    st.session_state.move_lead_id = lead['id']
                    st.rerun()

    def _render_new_lead_form(self):
        """Rendert das Formular für neue Leads"""
        st.subheader(" Neuen Lead erstellen")

        with st.form("new_lead_form"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Kontaktdaten")
                company_name = st.text_input(
                    "Firmenname *", placeholder="z.B. Mustermann GmbH")
                contact_person = st.text_input(
                    "Ansprechpartner *", placeholder="Max Mustermann")
                email = st.text_input(
                    "E-Mail", placeholder="max@mustermann.de")
                phone = st.text_input("Telefon", placeholder="+49 123 456789")
                address = st.text_area(
                    "Adresse", placeholder="Straße, PLZ Ort")

            with col2:
                st.markdown("#### Lead-Details")
                lead_source = st.selectbox(
                    "Lead-Quelle *", options=self.lead_sources)

                estimated_value = st.number_input(
                    "Geschätzter Auftragswert (€) *",
                    min_value=1000,
                    max_value=1000000,
                    value=25000,
                    step=1000
                )

                probability = st.slider(
                    "Abschlusswahrscheinlichkeit (%)",
                    min_value=0,
                    max_value=100,
                    value=50,
                    step=5
                )

                expected_close_date = st.date_input(
                    "Erwartetes Abschlussdatum",
                    value=datetime.now().date() + timedelta(days=30)
                )

                initial_stage = st.selectbox(
                    "Startstufe", options=[
                        'lead', 'qualified'], format_func=lambda x: f"{
                        self.pipeline_stages[x]['icon']} {
                        self.pipeline_stages[x]['name']}")

            notes = st.text_area(
                "Notizen", placeholder="Zusätzliche Informationen zum Lead")

            submitted = st.form_submit_button(
                " Lead erstellen", type="primary")

            if submitted:
                if company_name and contact_person and estimated_value:
                    lead_data = {
                        'company_name': company_name,
                        'contact_person': contact_person,
                        'email': email,
                        'phone': phone,
                        'address': address,
                        'lead_source': lead_source,
                        'estimated_value': estimated_value,
                        'probability': probability,
                        'expected_close_date': expected_close_date,
                        'stage': initial_stage,
                        'notes': notes
                    }

                    if self._create_lead(lead_data):
                        st.success(" Lead wurde erfolgreich erstellt!")
                        st.rerun()
                    else:
                        st.error(" Fehler beim Erstellen des Leads")
                else:
                    st.error("Bitte füllen Sie alle Pflichtfelder aus")

    def _render_lead_list(self):
        """Rendert die Lead-Liste mit Filter- und Sortieroptionen"""
        st.subheader(" Lead-Verwaltung")

        # Filter
        col1, col2, col3 = st.columns(3)

        with col1:
            stage_filter = st.selectbox(
                "Stufe filtern",
                options=['all'] +
                list(
                    self.pipeline_stages.keys()),
                format_func=lambda x: "Alle Stufen" if x == 'all' else f"{
                    self.pipeline_stages[x]['icon']} {
                    self.pipeline_stages[x]['name']}")

        with col2:
            source_filter = st.selectbox(
                "Quelle filtern",
                options=['all'] + self.lead_sources,
                format_func=lambda x: "Alle Quellen" if x == 'all' else x
            )

        with col3:
            sort_options = [
                'created_at',
                'estimated_value',
                'probability',
                'expected_close_date'
            ]
            
            # Füge Score-Sortierung hinzu wenn verfügbar
            if LEAD_SCORING_AVAILABLE:
                sort_options.insert(0, 'score')
            
            sort_by = st.selectbox(
                "Sortieren nach",
                options=sort_options,
                format_func=lambda x: {
                    'score': '[TARGET] Lead Score',
                    'created_at': 'Erstellungsdatum',
                    'estimated_value': 'Auftragswert',
                    'probability': 'Wahrscheinlichkeit',
                    'expected_close_date': 'Erwartetes Datum'}.get(x, x))

        # Leads laden und anzeigen
        leads = self._get_filtered_leads(stage_filter, source_filter, sort_by)

        if leads:
            for lead in leads:
                self._render_lead_detail_card(lead)
        else:
            st.info("Keine Leads gefunden")

    def _render_lead_detail_card(self, lead: dict[str, Any]):
        """Rendert eine detaillierte Lead-Karte"""
        stage_info = self.pipeline_stages[lead['stage']]
        days_in_stage = (
            datetime.now() -
            datetime.fromisoformat(
                lead['stage_changed_at'])).days

        with st.expander(f"{stage_info['icon']} {lead['company_name']} - {lead['estimated_value']:,.0f} €", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Kontaktdaten:**")
                st.text(f" {lead['contact_person']}")
                if lead['email']:
                    st.text(f" {lead['email']}")
                if lead['phone']:
                    st.text(f" {lead['phone']}")
                if lead['address']:
                    st.text(f" {lead['address']}")

            with col2:
                st.markdown("**Lead-Details:**")
                st.text(f" Quelle: {lead['lead_source']}")
                st.text(f" Wert: {lead['estimated_value']:,.0f} €")
                st.text(f" Wahrscheinlichkeit: {lead['probability']}%")
                st.text(
                    f" Erwarteter Abschluss: {
                        lead['expected_close_date']}")

            with col3:
                st.markdown("**Status:**")
                st.text(f" Aktuelle Stufe: {stage_info['name']}")
                st.text(f"⏱ {days_in_stage} Tage in dieser Stufe")
                st.text(f" Erstellt: {lead['created_at'][:10]}")

                # Gewichteter Wert
                weighted_value = lead['estimated_value'] * \
                    lead['probability'] / 100
                st.text(f" Gewichteter Wert: {weighted_value:,.0f} €")

            # Notizen
            if lead['notes']:
                st.markdown("**Notizen:**")
                st.text(lead['notes'])

            # Aktionen
            st.markdown("---")
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)

            with action_col1:
                if st.button(" Bearbeiten", key=f"edit_lead_{lead['id']}"):
                    st.session_state.edit_lead_id = lead['id']
                    st.rerun()

            with action_col2:
                next_stage = self._get_next_stage(lead['stage'])
                if next_stage:
                    next_stage_info = self.pipeline_stages[next_stage]
                    if st.button(
                            f" {next_stage_info['name']}", key=f"next_stage_{lead['id']}"):
                        self._update_lead_stage(lead['id'], next_stage)
                        st.success(
                            f"Lead zu '{
                                next_stage_info['name']}' verschoben")
                        st.rerun()

            with action_col3:
                if st.button(" Verloren", key=f"lost_{lead['id']}"):
                    self._update_lead_stage(lead['id'], 'lost')
                    st.error("Lead als 'Verloren' markiert")
                    st.rerun()

            with action_col4:
                if st.button(" Löschen", key=f"delete_lead_{lead['id']}"):
                    if self._delete_lead(lead['id']):
                        st.success("Lead gelöscht")
                        st.rerun()

    def _render_pipeline_analytics(self):
        """Rendert Pipeline-Analytics und Berichte"""
        st.subheader(" Pipeline Analytics")

        # Zeitraum-Auswahl
        period = st.selectbox(
            "Analysezeitraum",
            options=['last_30_days', 'last_90_days', 'this_year', 'all_time'],
            format_func=lambda x: {
                'last_30_days': 'Letzte 30 Tage',
                'last_90_days': 'Letzte 90 Tage',
                'this_year': 'Dieses Jahr',
                'all_time': 'Gesamtzeitraum'
            }[x]
        )

        analytics_data = self._get_analytics_data(period)

        # KPI-Dashboard
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Neue Leads",
                analytics_data['new_leads'],
                delta=f"{analytics_data['leads_growth']:+.1f}%"
            )

        with col2:
            st.metric(
                "Gewonnene Deals",
                analytics_data['won_deals'],
                delta=f"{analytics_data['won_value']:,.0f} €"
            )

        with col3:
            st.metric(
                "Conversion Rate",
                f"{analytics_data['conversion_rate']:.1f}%",
                delta=f"{analytics_data['conversion_change']:+.1f}%"
            )

        with col4:
            st.metric(
                "Ø Deal-Größe",
                f"{analytics_data['avg_deal_size']:,.0f} €",
                delta=f"{analytics_data['deal_size_change']:+.1f}%"
            )

        # Charts
        tab1, tab2, tab3 = st.tabs(
            [" Pipeline-Trichter", " Trend-Analyse", " Quellen-Performance"])

        with tab1:
            self._render_pipeline_funnel(analytics_data)

        with tab2:
            self._render_trend_analysis(analytics_data)

        with tab3:
            self._render_source_performance(analytics_data)

    def _render_pipeline_funnel(self, analytics_data: dict[str, Any]):
        """Rendert den Pipeline-Trichter"""
        st.markdown("####  Pipeline-Trichter")

        funnel_data = analytics_data.get('funnel_data', {})

        # Einfache Text-Darstellung des Trichters
        stages = ['lead', 'qualified', 'proposal', 'negotiation', 'won']

        for i, stage in enumerate(stages):
            stage_info = self.pipeline_stages[stage]
            count = funnel_data.get(stage, 0)

            if i == 0:
                conversion = 100.0
            else:
                prev_count = funnel_data.get(stages[i - 1], 1)
                conversion = (
                    count /
                    prev_count *
                    100) if prev_count > 0 else 0

            # Balken-Darstellung
            bar_width = max(10, int(conversion))
            bar = "" * (bar_width // 5)

            st.markdown(f"""
                **{stage_info['icon']} {stage_info['name']}**
                {bar} {count} Leads ({conversion:.1f}%)
            """)

    def _render_trend_analysis(self, analytics_data: dict[str, Any]):
        """Rendert Trend-Analysen"""
        st.markdown("####  Lead-Trends")

        trend_data = analytics_data.get('trend_data', {})

        # Vereinfachte Trend-Darstellung
        st.markdown("**Monatliche Lead-Entwicklung:**")
        for month, data in trend_data.items():
            st.text(
                f"{month}: {
                    data['new_leads']} neue Leads, {
                    data['won_deals']} gewonnen")

    def _render_source_performance(self, analytics_data: dict[str, Any]):
        """Rendert Quellen-Performance"""
        st.markdown("####  Lead-Quellen Performance")

        source_data = analytics_data.get('source_performance', {})

        for source, data in source_data.items():
            col1, col2, col3 = st.columns(3)

            with col1:
                st.text(f" {source}")
            with col2:
                st.text(f"Leads: {data['count']}")
            with col3:
                st.text(f"Conversion: {data['conversion_rate']:.1f}%")

    # Helper methods
    def _get_pipeline_statistics(self) -> dict[str, Any]:
        """Lädt Pipeline-Statistiken"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Basis-Statistiken
            cursor.execute(
                'SELECT COUNT(*) FROM crm_leads WHERE stage NOT IN ("won", "lost")')
            active_leads = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM crm_leads')
            total_leads = cursor.fetchone()[0]

            cursor.execute(
                'SELECT SUM(estimated_value) FROM crm_leads WHERE stage NOT IN ("won", "lost")')
            pipeline_value = cursor.fetchone()[0] or 0

            cursor.execute('SELECT AVG(estimated_value) FROM crm_leads')
            avg_deal_value = cursor.fetchone()[0] or 0

            conn.close()

            return {
                'total_leads': total_leads,
                'active_leads': active_leads,
                'total_pipeline_value': pipeline_value,
                'avg_deal_value': avg_deal_value,
                'conversion_rate': 25.5,  # Mock data
                'new_leads_this_month': 12,  # Mock data
                'monthly_conversion_change': 2.3,  # Mock data
                'avg_sales_cycle': 45,  # Mock data
                'cycle_trend': -3  # Mock data
            }

        except Exception as e:
            print(f"Fehler beim Laden der Pipeline-Statistiken: {e}")
            return {
                'total_leads': 0,
                'active_leads': 0,
                'total_pipeline_value': 0,
                'avg_deal_value': 0,
                'conversion_rate': 0,
                'new_leads_this_month': 0,
                'monthly_conversion_change': 0,
                'avg_sales_cycle': 0,
                'cycle_trend': 0}

    def _get_leads_by_stage(self, stage: str) -> list[dict[str, Any]]:
        """Lädt Leads nach Pipeline-Stufe"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Tabelle erstellen falls sie nicht existiert
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crm_leads (
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
            ''')

            cursor.execute('''
                SELECT * FROM crm_leads
                WHERE stage = ?
                ORDER BY stage_changed_at DESC
            ''', (stage,))

            leads = []
            for row in cursor.fetchall():
                lead = {
                    'id': row[0],
                    'company_name': row[1],
                    'contact_person': row[2],
                    'email': row[3],
                    'phone': row[4],
                    'address': row[5],
                    'lead_source': row[6],
                    'estimated_value': row[7],
                    'probability': row[8],
                    'expected_close_date': row[9],
                    'stage': row[10],
                    'stage_changed_at': row[11],
                    'notes': row[12],
                    'created_at': row[13],
                    'updated_at': row[14]
                }
                leads.append(lead)

            conn.close()
            return leads

        except Exception as e:
            print(f"Fehler beim Laden der Leads für Stufe {stage}: {e}")
            return []

    def _get_recent_closed_leads(self, status: str) -> list[dict[str, Any]]:
        """Lädt kürzlich geschlossene Leads (won/lost)"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            thirty_days_ago = datetime.now() - timedelta(days=30)

            cursor.execute('''
                SELECT * FROM crm_leads
                WHERE stage = ? AND stage_changed_at >= ?
                ORDER BY stage_changed_at DESC
            ''', (status, thirty_days_ago.isoformat()))

            leads = []
            for row in cursor.fetchall():
                lead = {
                    'id': row[0],
                    'company_name': row[1],
                    'contact_person': row[2],
                    'estimated_value': row[7],
                    'stage_changed_at': row[11]
                }
                leads.append(lead)

            conn.close()
            return leads

        except Exception as e:
            print(f"Fehler beim Laden der geschlossenen Leads: {e}")
            return []

    def _get_filtered_leads(self,
                            stage_filter: str,
                            source_filter: str,
                            sort_by: str) -> list[dict[str,
                                                       Any]]:
        """Lädt gefilterte Leads"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            query = 'SELECT * FROM crm_leads WHERE 1=1'
            params = []

            if stage_filter != 'all':
                query += ' AND stage = ?'
                params.append(stage_filter)

            if source_filter != 'all':
                query += ' AND lead_source = ?'
                params.append(source_filter)

            # Sortierung
            if sort_by == 'estimated_value':
                query += ' ORDER BY estimated_value DESC'
            elif sort_by == 'probability':
                query += ' ORDER BY probability DESC'
            elif sort_by == 'expected_close_date':
                query += ' ORDER BY expected_close_date ASC'
            else:
                query += ' ORDER BY created_at DESC'

            cursor.execute(query, params)

            leads = []
            for row in cursor.fetchall():
                lead = {
                    'id': row[0],
                    'company_name': row[1],
                    'contact_person': row[2],
                    'email': row[3],
                    'phone': row[4],
                    'address': row[5],
                    'lead_source': row[6],
                    'estimated_value': row[7],
                    'probability': row[8],
                    'expected_close_date': row[9],
                    'stage': row[10],
                    'stage_changed_at': row[11],
                    'notes': row[12],
                    'created_at': row[13],
                    'updated_at': row[14]
                }
                leads.append(lead)

            conn.close()
            return leads

        except Exception as e:
            print(f"Fehler beim Laden der gefilterten Leads: {e}")
            return []

    def _create_lead(self, lead_data: dict[str, Any]) -> bool:
        """Erstellt einen neuen Lead"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Initialisiere Lead Scoring Tabellen falls nötig
            if LEAD_SCORING_AVAILABLE:
                try:
                    create_lead_scoring_tables(conn)
                    initialize_default_scoring_rules(conn)
                except Exception as e:
                    print(f"Lead Scoring Initialisierung: {e}")

            cursor.execute('''
                INSERT INTO crm_leads
                (company_name, contact_person, email, phone, address, lead_source,
                 estimated_value, probability, expected_close_date, stage, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead_data['company_name'],
                lead_data['contact_person'],
                lead_data['email'],
                lead_data['phone'],
                lead_data['address'],
                lead_data['lead_source'],
                lead_data['estimated_value'],
                lead_data['probability'],
                lead_data['expected_close_date'].isoformat(),
                lead_data['stage'],
                lead_data['notes']
            ))

            lead_id = cursor.lastrowid
            conn.commit()
            
            # Berechne initialen Score
            if LEAD_SCORING_AVAILABLE and lead_id:
                try:
                    update_lead_score(conn, lead_id, "Lead created")
                except Exception as e:
                    print(f"Fehler beim Berechnen des Lead-Scores: {e}")
            
            conn.close()
            return True

        except Exception as e:
            print(f"Fehler beim Erstellen des Leads: {e}")
            return False

    def _update_lead_stage(self, lead_id: int, new_stage: str) -> bool:
        """Aktualisiert die Pipeline-Stufe eines Leads"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE crm_leads
                SET stage = ?, stage_changed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_stage, lead_id))

            conn.commit()
            
            # Aktualisiere Score nach Stage-Änderung
            if LEAD_SCORING_AVAILABLE:
                try:
                    update_lead_score(conn, lead_id, f"Stage changed to {new_stage}")
                except Exception as e:
                    print(f"Fehler beim Aktualisieren des Lead-Scores: {e}")
            
            conn.close()
            return True

        except Exception as e:
            print(f"Fehler beim Aktualisieren der Lead-Stufe: {e}")
            return False

    def _delete_lead(self, lead_id: int) -> bool:
        """Löscht einen Lead"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM crm_leads WHERE id = ?', (lead_id,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Fehler beim Löschen des Leads: {e}")
            return False

    def _get_next_stage(self, current_stage: str) -> str | None:
        """Ermittelt die nächste Pipeline-Stufe"""
        stage_order = ['lead', 'qualified', 'proposal', 'negotiation', 'won']

        try:
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
        except ValueError:
            pass

        return None

    def _get_analytics_data(self, period: str) -> dict[str, Any]:
        """Lädt Analytics-Daten für den gewählten Zeitraum"""
        # Mock data für Demo-Zwecke
        return {
            'new_leads': 45,
            'leads_growth': 12.5,
            'won_deals': 8,
            'won_value': 185000,
            'conversion_rate': 18.2,
            'conversion_change': 3.1,
            'avg_deal_size': 23125,
            'deal_size_change': 8.7,
            'funnel_data': {
                'lead': 45,
                'qualified': 28,
                'proposal': 15,
                'negotiation': 12,
                'won': 8
            },
            'trend_data': {
                'Januar': {'new_leads': 12, 'won_deals': 2},
                'Februar': {'new_leads': 18, 'won_deals': 4},
                'März': {'new_leads': 15, 'won_deals': 2}
            },
            'source_performance': {
                'Website': {'count': 18, 'conversion_rate': 22.2},
                'Empfehlung': {'count': 12, 'conversion_rate': 33.3},
                'Social Media': {'count': 8, 'conversion_rate': 12.5},
                'Kaltakquise': {'count': 7, 'conversion_rate': 14.3}
            }
        }


def render_crm_pipeline(texts: dict[str, str], module_name: str | None = None):
    """Haupt-Render-Funktion für CRM-Pipeline"""
    if module_name:
        st.title(module_name)
    pipeline_manager = CRMPipeline()
    pipeline_manager.render_pipeline_interface(texts)

# Änderungshistorie
# 2025-06-21, Gemini Ultra: CRM Pipeline UI implementiert
#                           - Kanban-Style Pipeline-Übersicht
#                           - Lead-Management mit vollständigem Lifecycle
#                           - Analytics und Reporting
#                           - Pipeline-Statistiken und KPIs
