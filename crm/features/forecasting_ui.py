"""
CRM Forecasting UI
Benutzeroberfläche für Verkaufsziele und Forecasting

Autor: Kiro AI
Datum: 2025-01-14
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional
import plotly.graph_objects as go
import plotly.express as px

try:
    from crm.features.forecasting_engine import (
        ensure_forecasting_tables,
        create_sales_target,
        get_sales_targets,
        update_target_progress,
        update_target_status,
        calculate_pipeline_forecast,
        create_forecast,
        get_forecasts,
        get_target_achievement_status,
        check_at_risk_targets,
        auto_update_target_progress_from_pipeline
    )
    FORECASTING_AVAILABLE = True
except ImportError:
    FORECASTING_AVAILABLE = False


def render_forecasting_dashboard(texts: Optional[dict] = None):
    """
    Rendert das Haupt-Dashboard für Verkaufsziele und Forecasting.
    
    Args:
        texts: Optionales Übersetzungs-Dictionary
    """
    if not FORECASTING_AVAILABLE:
        st.error("[ERROR] Forecasting-Modul nicht verfügbar")
        return
    
    # Stelle sicher, dass Tabellen existieren
    ensure_forecasting_tables()
    
    st.header("[CHART] Verkaufsziele & Forecasting")
    
    # Tab-Navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "[STATS] Übersicht",
        "[TARGET] Ziele verwalten",
        "🔮 Forecasts",
        "[WARNING] Warnungen"
    ])
    
    with tab1:
        render_overview_tab()
    
    with tab2:
        render_targets_management_tab()
    
    with tab3:
        render_forecasts_tab()
    
    with tab4:
        render_warnings_tab()


def render_overview_tab():
    """Rendert die Übersichts-Seite mit KPIs und Visualisierungen."""
    st.subheader("[CHART] Aktuelle Übersicht")
    
    # Lade aktive Ziele
    active_targets = get_sales_targets(status='active')
    
    if not active_targets:
        st.info("[INFO] Keine aktiven Verkaufsziele vorhanden. Erstellen Sie ein neues Ziel im Tab 'Ziele verwalten'.")
        return
    
    # KPI-Metriken
    col1, col2, col3, col4 = st.columns(4)
    
    total_targets = len(active_targets)
    achieved_targets = sum(1 for t in active_targets if t['current_value'] >= t['target_value'])
    total_target_value = sum(t['target_value'] for t in active_targets)
    total_current_value = sum(t['current_value'] for t in active_targets)
    
    with col1:
        st.metric("Aktive Ziele", total_targets)
    
    with col2:
        st.metric("Erreichte Ziele", achieved_targets)
    
    with col3:
        achievement_pct = (total_current_value / total_target_value * 100) if total_target_value > 0 else 0
        st.metric("Gesamt-Zielerreichung", f"{achievement_pct:.1f}%")
    
    with col4:
        st.metric("Gesamt-Zielwert", f"{total_target_value:,.0f} €")
    
    st.divider()
    
    # Visualisierung: Ziel vs. Ist
    st.subheader("[TARGET] Ziele im Überblick")
    
    for target in active_targets[:5]:  # Zeige Top 5
        status = get_target_achievement_status(target['id'])
        
        if status:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{target['target_name']}**")
                
                # Progress Bar mit Farbe basierend auf Health
                health_colors = {
                    'excellent': 'green',
                    'good': 'blue',
                    'warning': 'orange',
                    'critical': 'red'
                }
                
                progress = min(status['achievement_percentage'] / 100, 1.0)
                
                # Custom Progress Bar mit Plotly
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=status['current_value'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"Fortschritt: {status['achievement_percentage']:.1f}%"},
                    delta={'reference': status['target_value']},
                    gauge={
                        'axis': {'range': [None, status['target_value']]},
                        'bar': {'color': health_colors.get(status['health'], 'gray')},
                        'steps': [
                            {'range': [0, status['target_value'] * 0.5], 'color': "lightgray"},
                            {'range': [status['target_value'] * 0.5, status['target_value'] * 0.8], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': status['target_value']
                        }
                    }
                ))
                fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Zielwert", f"{target['target_value']:,.0f} €")
                st.metric("Aktuell", f"{status['current_value']:,.0f} €")
                st.metric("Verbleibend", f"{status['remaining_value']:,.0f} €")
                
                # Health Badge
                health_emoji = {
                    'excellent': '🟢',
                    'good': '🔵',
                    'warning': '🟠',
                    'critical': '🔴'
                }
                st.write(f"{health_emoji.get(status['health'], '⚪')} {status['health'].upper()}")
        
        st.divider()


def render_targets_management_tab():
    """Rendert die Ziel-Verwaltungs-Seite."""
    st.subheader("[TARGET] Verkaufsziele verwalten")
    
    # Neues Ziel erstellen
    with st.expander("➕ Neues Ziel erstellen", expanded=False):
        with st.form("new_target_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                target_name = st.text_input("Ziel-Name*", placeholder="z.B. Q1 2025 Umsatzziel")
                target_type = st.selectbox("Ziel-Typ*", ['company', 'team', 'individual'])
                period_type = st.selectbox("Zeitraum*", ['monthly', 'quarterly', 'yearly'])
            
            with col2:
                target_value = st.number_input("Zielwert (€)*", min_value=0.0, step=1000.0)
                target_unit = st.selectbox("Einheit", ['EUR', 'deals', 'leads'])
                
                if target_type == 'individual':
                    assigned_to = st.text_input("Zugewiesen an", placeholder="Mitarbeiter-Name")
                else:
                    assigned_to = None
            
            # Zeitraum
            col3, col4 = st.columns(2)
            with col3:
                period_start = st.date_input("Start-Datum*")
            with col4:
                period_end = st.date_input("End-Datum*")
            
            description = st.text_area("Beschreibung", placeholder="Optional: Zusätzliche Informationen")
            
            submitted = st.form_submit_button("[OK] Ziel erstellen")
            
            if submitted:
                if not target_name or not target_value or not period_start or not period_end:
                    st.error("[ERROR] Bitte füllen Sie alle Pflichtfelder aus")
                elif period_end <= period_start:
                    st.error("[ERROR] End-Datum muss nach Start-Datum liegen")
                else:
                    target_id = create_sales_target(
                        target_name=target_name,
                        target_type=target_type,
                        period_type=period_type,
                        period_start=period_start.strftime('%Y-%m-%d'),
                        period_end=period_end.strftime('%Y-%m-%d'),
                        target_value=target_value,
                        assigned_to=assigned_to,
                        target_unit=target_unit,
                        description=description,
                        created_by=st.session_state.get('current_user', 'System')
                    )
                    
                    if target_id:
                        st.success(f"[OK] Ziel '{target_name}' erfolgreich erstellt!")
                        st.rerun()
                    else:
                        st.error("[ERROR] Fehler beim Erstellen des Ziels")
    
    st.divider()
    
    # Bestehende Ziele anzeigen
    st.subheader("📋 Bestehende Ziele")
    
    # Filter
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.selectbox("Typ filtern", ['Alle', 'company', 'team', 'individual'])
    with col2:
        filter_status = st.selectbox("Status filtern", ['Alle', 'active', 'completed', 'failed', 'cancelled'])
    with col3:
        filter_period = st.selectbox("Zeitraum", ['Alle', 'Aktuell', 'Vergangen', 'Zukünftig'])
    
    # Lade Ziele mit Filtern
    targets = get_sales_targets(
        target_type=None if filter_type == 'Alle' else filter_type,
        status=None if filter_status == 'Alle' else filter_status
    )
    
    # Zeitraum-Filter anwenden
    if filter_period != 'Alle':
        now = datetime.now().strftime('%Y-%m-%d')
        if filter_period == 'Aktuell':
            targets = [t for t in targets if t['period_start'] <= now <= t['period_end']]
        elif filter_period == 'Vergangen':
            targets = [t for t in targets if t['period_end'] < now]
        elif filter_period == 'Zukünftig':
            targets = [t for t in targets if t['period_start'] > now]
    
    if not targets:
        st.info("[INFO] Keine Ziele gefunden")
    else:
        for target in targets:
            with st.expander(f"[TARGET] {target['target_name']} ({target['status']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Typ:** {target['target_type']}")
                    st.write(f"**Zeitraum:** {target['period_type']}")
                    st.write(f"**Von:** {target['period_start']}")
                    st.write(f"**Bis:** {target['period_end']}")
                
                with col2:
                    st.write(f"**Zielwert:** {target['target_value']:,.0f} {target['target_unit']}")
                    st.write(f"**Aktuell:** {target['current_value']:,.0f} {target['target_unit']}")
                    achievement = (target['current_value'] / target['target_value'] * 100) if target['target_value'] > 0 else 0
                    st.write(f"**Erreichung:** {achievement:.1f}%")
                
                with col3:
                    if target['assigned_to']:
                        st.write(f"**Zugewiesen:** {target['assigned_to']}")
                    st.write(f"**Status:** {target['status']}")
                    st.write(f"**Erstellt:** {target['created_at'][:10]}")
                
                if target['description']:
                    st.write(f"**Beschreibung:** {target['description']}")
                
                # Aktionen
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"🔄 Fortschritt aktualisieren", key=f"update_{target['id']}"):
                        if auto_update_target_progress_from_pipeline(target['id']):
                            st.success("[OK] Fortschritt aktualisiert")
                            st.rerun()
                        else:
                            st.error("[ERROR] Fehler beim Aktualisieren")
                
                with col2:
                    new_status = st.selectbox(
                        "Status ändern",
                        ['active', 'completed', 'failed', 'cancelled'],
                        index=['active', 'completed', 'failed', 'cancelled'].index(target['status']),
                        key=f"status_{target['id']}"
                    )
                    if new_status != target['status']:
                        if st.button(f"💾 Status speichern", key=f"save_status_{target['id']}"):
                            if update_target_status(target['id'], new_status):
                                st.success("[OK] Status aktualisiert")
                                st.rerun()


def render_forecasts_tab():
    """Rendert die Forecast-Seite."""
    st.subheader("🔮 Sales Forecasts")
    
    # Neuen Forecast erstellen
    with st.expander("➕ Neuen Forecast erstellen", expanded=False):
        st.write("**Automatischer Pipeline-basierter Forecast**")
        
        col1, col2 = st.columns(2)
        with col1:
            forecast_period = st.selectbox("Zeitraum", ['monthly', 'quarterly', 'yearly'])
            period_start = st.date_input("Start-Datum", key="forecast_start")
        with col2:
            period_end = st.date_input("End-Datum", key="forecast_end")
        
        # Verknüpfung mit Ziel (optional)
        targets = get_sales_targets(status='active')
        target_options = ['Kein Ziel'] + [f"{t['target_name']} (ID: {t['id']})" for t in targets]
        selected_target = st.selectbox("Mit Ziel verknüpfen (optional)", target_options)
        
        if st.button("🔮 Forecast berechnen"):
            # Berechne Forecast
            forecast_data = calculate_pipeline_forecast(
                period_start.strftime('%Y-%m-%d'),
                period_end.strftime('%Y-%m-%d')
            )
            
            if forecast_data:
                st.success("[OK] Forecast erfolgreich berechnet!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prognostizierter Wert", f"{forecast_data['forecast_value']:,.0f} €")
                with col2:
                    confidence_pct = forecast_data['confidence_level'] * 100
                    st.metric("Konfidenz", f"{confidence_pct:.0f}%")
                with col3:
                    st.metric("Leads in Pipeline", forecast_data['details']['total_leads'])
                
                # Stage Breakdown
                st.write("**Pipeline-Verteilung:**")
                stage_data = forecast_data['details']['stage_breakdown']
                
                if stage_data:
                    stages = list(stage_data.keys())
                    counts = [stage_data[s]['count'] for s in stages]
                    values = [stage_data[s]['weighted_value'] for s in stages]
                    
                    fig = go.Figure(data=[
                        go.Bar(name='Anzahl Leads', x=stages, y=counts, yaxis='y', offsetgroup=1),
                        go.Bar(name='Gewichteter Wert (€)', x=stages, y=values, yaxis='y2', offsetgroup=2)
                    ])
                    fig.update_layout(
                        xaxis=dict(title='Pipeline Stage'),
                        yaxis=dict(title='Anzahl Leads', side='left'),
                        yaxis2=dict(title='Gewichteter Wert (€)', overlaying='y', side='right'),
                        barmode='group',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Forecast speichern
                if st.button("💾 Forecast speichern"):
                    target_id = None
                    if selected_target != 'Kein Ziel':
                        # Extrahiere ID aus String
                        target_id = int(selected_target.split('ID: ')[1].rstrip(')'))
                    
                    forecast_id = create_forecast(
                        forecast_period=forecast_period,
                        period_start=period_start.strftime('%Y-%m-%d'),
                        period_end=period_end.strftime('%Y-%m-%d'),
                        forecast_value=forecast_data['forecast_value'],
                        confidence_level=forecast_data['confidence_level'],
                        forecast_method='pipeline_based',
                        target_id=target_id,
                        pipeline_data=forecast_data['details'],
                        calculation_details=forecast_data['details'],
                        created_by=st.session_state.get('current_user', 'System')
                    )
                    
                    if forecast_id:
                        st.success("[OK] Forecast gespeichert!")
                        st.rerun()
    
    st.divider()
    
    # Gespeicherte Forecasts anzeigen
    st.subheader("[CHART] Gespeicherte Forecasts")
    
    forecasts = get_forecasts()
    
    if not forecasts:
        st.info("[INFO] Keine Forecasts vorhanden")
    else:
        for forecast in forecasts:
            with st.expander(f"🔮 Forecast {forecast['period_start']} - {forecast['period_end']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Prognostizierter Wert", f"{forecast['forecast_value']:,.0f} €")
                with col2:
                    confidence_pct = forecast['confidence_level'] * 100
                    st.metric("Konfidenz", f"{confidence_pct:.0f}%")
                with col3:
                    st.write(f"**Methode:** {forecast['forecast_method']}")
                    st.write(f"**Erstellt:** {forecast['created_at'][:10]}")
                
                if forecast['calculation_details']:
                    details = forecast['calculation_details']
                    st.write(f"**Leads in Pipeline:** {details.get('total_leads', 'N/A')}")


def render_warnings_tab():
    """Rendert die Warnungen-Seite für gefährdete Ziele."""
    st.subheader("[WARNING] Gefährdete Ziele")
    
    at_risk = check_at_risk_targets()
    
    if not at_risk:
        st.success("[OK] Alle Ziele sind auf Kurs! Keine Warnungen.")
        return
    
    st.warning(f"[WARNING] {len(at_risk)} Ziel(e) benötigen Aufmerksamkeit")
    
    for status in at_risk:
        # Lade Ziel-Details
        targets = get_sales_targets()
        target = next((t for t in targets if t['id'] == status['target_id']), None)
        
        if not target:
            continue
        
        health_colors = {
            'warning': '🟠',
            'critical': '🔴'
        }
        
        with st.expander(f"{health_colors.get(status['health'], '⚪')} {target['target_name']} - {status['health'].upper()}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Zielwert", f"{status['target_value']:,.0f} €")
                st.metric("Aktueller Wert", f"{status['current_value']:,.0f} €")
                st.metric("Zielerreichung", f"{status['achievement_percentage']:.1f}%")
            
            with col2:
                st.metric("Verbleibend", f"{status['remaining_value']:,.0f} €")
                st.metric("Zeitfortschritt", f"{status['time_percentage']:.1f}%")
                
                # Empfehlung
                if status['health'] == 'critical':
                    st.error("🔴 **KRITISCH:** Sofortige Maßnahmen erforderlich!")
                    st.write("Empfohlene Aktionen:")
                    st.write("- Pipeline-Review durchführen")
                    st.write("- Zusätzliche Ressourcen einsetzen")
                    st.write("- Ziel ggf. anpassen")
                else:
                    st.warning("🟠 **WARNUNG:** Ziel gefährdet")
                    st.write("Empfohlene Aktionen:")
                    st.write("- Leads nachfassen")
                    st.write("- Conversion-Rate verbessern")
            
            # Visualisierung
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=['Ziel', 'Aktuell'],
                y=[status['target_value'], status['current_value']],
                marker_color=['lightblue', 'red' if status['health'] == 'critical' else 'orange']
            ))
            
            fig.update_layout(
                title="Ziel vs. Ist",
                yaxis_title="Wert (€)",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_period_dates(period_type: str) -> tuple[str, str]:
    """
    Berechnet Start- und End-Datum für einen Zeitraum-Typ.
    
    Args:
        period_type: 'monthly', 'quarterly', 'yearly'
        
    Returns:
        tuple: (start_date, end_date) als Strings
    """
    now = datetime.now()
    
    if period_type == 'monthly':
        start = now.replace(day=1)
        if now.month == 12:
            end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
    
    elif period_type == 'quarterly':
        quarter = (now.month - 1) // 3 + 1
        start = now.replace(month=(quarter - 1) * 3 + 1, day=1)
        end_month = quarter * 3
        if end_month == 12:
            end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = now.replace(month=end_month + 1, day=1) - timedelta(days=1)
    
    else:  # yearly
        start = now.replace(month=1, day=1)
        end = now.replace(month=12, day=31)
    
    return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
