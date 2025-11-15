"""
CRM Forecasting Integration Example
Zeigt die Integration des Forecasting-Systems in die Hauptanwendung

Autor: Kiro AI
Datum: 2025-01-14
"""

import streamlit as st
from datetime import datetime, timedelta

try:
    from crm.features.forecasting_engine import (
        ensure_forecasting_tables,
        create_sales_target,
        get_sales_targets,
        calculate_pipeline_forecast,
        create_forecast,
        get_target_achievement_status,
        check_at_risk_targets,
        auto_update_target_progress_from_pipeline
    )
    from crm.features.forecasting_ui import render_forecasting_dashboard
    FORECASTING_AVAILABLE = True
except ImportError:
    FORECASTING_AVAILABLE = False


def integrate_forecasting_into_crm():
    """
    Beispiel: Integration des Forecasting-Systems in das CRM-Dashboard
    
    Diese Funktion zeigt, wie das Forecasting-System in die bestehende
    CRM-Anwendung integriert werden kann.
    """
    
    if not FORECASTING_AVAILABLE:
        st.error("Forecasting-System nicht verfügbar")
        return
    
    # 1. Stelle sicher, dass Tabellen existieren
    ensure_forecasting_tables()
    
    # 2. Zeige Forecasting-Dashboard
    st.header("Verkaufsziele & Forecasting")
    
    # Quick Stats in Sidebar
    with st.sidebar:
        st.subheader("Ziel-Übersicht")
        
        # Lade aktive Ziele
        active_targets = get_sales_targets(status='active')
        
        if active_targets:
            st.metric("Aktive Ziele", len(active_targets))
            
            # Prüfe gefährdete Ziele
            at_risk = check_at_risk_targets()
            if at_risk:
                st.warning(f"{len(at_risk)} Ziel(e) gefährdet")
            else:
                st.success("Alle Ziele auf Kurs")
        else:
            st.info("Keine aktiven Ziele")
    
    # 3. Haupt-Dashboard
    render_forecasting_dashboard()


def auto_create_quarterly_targets():
    """
    Beispiel: Automatische Erstellung von Quartalszielen
    
    Diese Funktion kann zu Beginn eines Quartals aufgerufen werden,
    um automatisch Ziele zu erstellen.
    """
    
    if not FORECASTING_AVAILABLE:
        print("Forecasting nicht verfügbar")
        return
    
    # Berechne aktuelles Quartal
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    
    # Start- und End-Datum des Quartals
    start_month = (quarter - 1) * 3 + 1
    start_date = now.replace(month=start_month, day=1)
    
    end_month = quarter * 3
    if end_month == 12:
        end_date = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = now.replace(month=end_month + 1, day=1) - timedelta(days=1)
    
    # Erstelle Company-Ziel
    target_id = create_sales_target(
        target_name=f"Q{quarter} {now.year} Unternehmensziel",
        target_type="company",
        period_type="quarterly",
        period_start=start_date.strftime('%Y-%m-%d'),
        period_end=end_date.strftime('%Y-%m-%d'),
        target_value=250000.0,  # Beispielwert
        description=f"Automatisch erstelltes Quartalsziel für Q{quarter} {now.year}",
        created_by="System"
    )
    
    if target_id:
        print(f"Quartalsziel erstellt: ID {target_id}")
        
        # Erstelle initialen Forecast
        forecast_data = calculate_pipeline_forecast(
            period_start=start_date.strftime('%Y-%m-%d'),
            period_end=end_date.strftime('%Y-%m-%d')
        )
        
        if forecast_data:
            forecast_id = create_forecast(
                forecast_period="quarterly",
                period_start=start_date.strftime('%Y-%m-%d'),
                period_end=end_date.strftime('%Y-%m-%d'),
                forecast_value=forecast_data['forecast_value'],
                confidence_level=forecast_data['confidence_level'],
                forecast_method="pipeline_based",
                target_id=target_id,
                pipeline_data=forecast_data['details'],
                notes="Initialer Forecast zu Quartalsbeginn",
                created_by="System"
            )
            
            if forecast_id:
                print(f"Initialer Forecast erstellt: {forecast_data['forecast_value']:,.2f} €")
    else:
        print("Fehler beim Erstellen des Quartalsziels")


def daily_target_monitoring():
    """
    Beispiel: Tägliche Überwachung der Verkaufsziele
    
    Diese Funktion kann als täglicher Cron-Job ausgeführt werden,
    um Ziele zu aktualisieren und Warnungen zu versenden.
    """
    
    if not FORECASTING_AVAILABLE:
        print("Forecasting nicht verfügbar")
        return
    
    print("=== Tägliche Ziel-Überwachung ===")
    print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Aktualisiere alle aktiven Ziele
    active_targets = get_sales_targets(status='active')
    
    print(f"\n{len(active_targets)} aktive Ziele gefunden")
    
    for target in active_targets:
        print(f"\n{target['target_name']}")
        
        # Aktualisiere Fortschritt aus Pipeline
        success = auto_update_target_progress_from_pipeline(target['id'])
        
        if success:
            # Hole aktuellen Status
            status = get_target_achievement_status(target['id'])
            
            if status:
                print(f"   Zielerreichung: {status['achievement_percentage']:.1f}%")
                print(f"   Health: {status['health']}")
                
                # Warnungen
                if status['health'] == 'critical':
                    print(f"   🔴 KRITISCH: Sofortige Maßnahmen erforderlich!")
                elif status['health'] == 'warning':
                    print(f"   🟠 WARNUNG: Ziel gefährdet")
                elif status['health'] == 'excellent':
                    print(f"   🟢 EXZELLENT: Ziel erreicht!")
                else:
                    print(f"   🔵 GUT: Auf Kurs")
    
    # 2. Prüfe gefährdete Ziele
    at_risk = check_at_risk_targets()
    
    if at_risk:
        print(f"\n{len(at_risk)} gefährdete Ziele:")
        
        for target_status in at_risk:
            targets = get_sales_targets()
            target = next((t for t in targets if t['id'] == target_status['target_id']), None)
            
            if target:
                print(f"   - {target['target_name']}: {target_status['achievement_percentage']:.1f}%")
                
                # Hier könnte eine Benachrichtigung versendet werden
                # send_notification(target, target_status)
    else:
        print("\nAlle Ziele auf Kurs!")
    
    print("\n=== Überwachung abgeschlossen ===")


def weekly_forecast_update():
    """
    Beispiel: Wöchentliche Forecast-Aktualisierung
    
    Diese Funktion kann wöchentlich ausgeführt werden,
    um Forecasts zu aktualisieren und Trends zu analysieren.
    """
    
    if not FORECASTING_AVAILABLE:
        print("Forecasting nicht verfügbar")
        return
    
    print("=== Wöchentliche Forecast-Aktualisierung ===")
    print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Lade alle aktiven Ziele
    active_targets = get_sales_targets(status='active')
    
    for target in active_targets:
        print(f"\n{target['target_name']}")
        
        # Berechne neuen Forecast
        forecast_data = calculate_pipeline_forecast(
            period_start=target['period_start'],
            period_end=target['period_end']
        )
        
        if forecast_data:
            print(f"   Neuer Forecast: {forecast_data['forecast_value']:,.2f} €")
            print(f"   Konfidenz: {forecast_data['confidence_level']:.2%}")
            print(f"   Basierend auf {forecast_data['details']['total_leads']} Leads")
            
            # Speichere Forecast
            forecast_id = create_forecast(
                forecast_period=target['period_type'],
                period_start=target['period_start'],
                period_end=target['period_end'],
                forecast_value=forecast_data['forecast_value'],
                confidence_level=forecast_data['confidence_level'],
                forecast_method="pipeline_based",
                target_id=target['id'],
                pipeline_data=forecast_data['details'],
                notes=f"Wöchentliches Update vom {datetime.now().strftime('%Y-%m-%d')}",
                created_by="System"
            )
            
            if forecast_id:
                print(f"   Forecast gespeichert (ID: {forecast_id})")
            
            # Vergleiche mit Ziel
            gap = target['target_value'] - forecast_data['forecast_value']
            gap_percentage = (gap / target['target_value'] * 100) if target['target_value'] > 0 else 0
            
            if gap > 0:
                print(f"   Gap zum Ziel: {gap:,.2f} € ({gap_percentage:.1f}%)")
            else:
                print(f"   Forecast übertrifft Ziel um {abs(gap):,.2f} €")
    
    print("\n=== Forecast-Update abgeschlossen ===")


def render_forecasting_widget_for_dashboard():
    """
    Beispiel: Kompaktes Forecasting-Widget für das Haupt-Dashboard
    
    Dieses Widget kann in das bestehende CRM-Dashboard integriert werden.
    """
    
    if not FORECASTING_AVAILABLE:
        return
    
    st.subheader("Verkaufsziele")
    
    # Lade aktive Ziele
    active_targets = get_sales_targets(status='active')
    
    if not active_targets:
        st.info("Keine aktiven Ziele vorhanden")
        return
    
    # Zeige Top 3 Ziele
    for target in active_targets[:3]:
        status = get_target_achievement_status(target['id'])
        
        if status:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{target['target_name']}**")
            
            with col2:
                achievement = status['achievement_percentage']
                st.metric("Erreichung", f"{achievement:.1f}%")
            
            with col3:
                health_emoji = {
                    'excellent': '🟢',
                    'good': '🔵',
                    'warning': '🟠',
                    'critical': '🔴'
                }
                st.write(f"{health_emoji.get(status['health'], '⚪')} {status['health'].upper()}")
            
            # Progress Bar
            progress = min(achievement / 100, 1.0)
            st.progress(progress)
    
    # Link zum vollständigen Dashboard
    if st.button("Alle Ziele anzeigen"):
        st.session_state['show_forecasting'] = True


# ============================================================================
# VERWENDUNG IN HAUPTANWENDUNG
# ============================================================================

def example_integration_in_main_app():
    """
    Beispiel: Integration in die Hauptanwendung (gui.py oder crm.py)
    """
    
    # In gui.py oder crm.py:
    
    # 1. Import
    # from crm.features.forecasting_integration_example import integrate_forecasting_into_crm
    
    # 2. Navigation erweitern
    # menu_options = ["Dashboard", "Kunden", "Pipeline", "Forecasting", ...]
    
    # 3. Forecasting-Seite anzeigen
    # if selected_menu == "Forecasting":
    #     integrate_forecasting_into_crm()
    
    # 4. Widget im Dashboard
    # if selected_menu == "Dashboard":
    #     render_forecasting_widget_for_dashboard()
    
    pass


if __name__ == "__main__":
    print("=== CRM Forecasting Integration Examples ===\n")
    
    # Beispiel 1: Automatische Quartalsziele
    print("1. Automatische Quartalsziel-Erstellung:")
    auto_create_quarterly_targets()
    
    print("\n" + "="*60 + "\n")
    
    # Beispiel 2: Tägliche Überwachung
    print("2. Tägliche Ziel-Überwachung:")
    daily_target_monitoring()
    
    print("\n" + "="*60 + "\n")
    
    # Beispiel 3: Wöchentliches Forecast-Update
    print("3. Wöchentliche Forecast-Aktualisierung:")
    weekly_forecast_update()
