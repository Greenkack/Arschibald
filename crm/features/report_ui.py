"""
CRM Reporting UI

Streamlit UI für das CRM Reporting-System.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

try:
    from database import get_db_connection
    from crm.features.reporting_engine import (
        ReportingEngine,
        get_available_tables,
        get_table_columns,
        format_currency,
        format_percentage
    )
except ImportError as e:
    st.error(f"Import-Fehler: {e}")
    st.stop()


def render_reporting_ui():
    """Hauptfunktion für die Reporting-UI."""
    st.title("CRM Reports & Analysen")
    
    # Datenbankverbindung
    conn = get_db_connection()
    if not conn:
        st.error("Keine Datenbankverbindung möglich")
        return
    
    engine = ReportingEngine(conn)
    
    # Tab-Navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "Vordefinierte Reports",
        "Report Builder",
        "💾 Gespeicherte Vorlagen",
        "📥 Export"
    ])
    
    with tab1:
        render_predefined_reports(engine)
    
    with tab2:
        render_report_builder(engine, conn)
    
    with tab3:
        render_saved_templates(engine)
    
    with tab4:
        render_export_section()
    
    conn.close()


def render_predefined_reports(engine: ReportingEngine):
    """Rendert die vordefinierten Reports."""
    st.header("Vordefinierte Reports")
    
    report_type = st.selectbox(
        "Report auswählen",
        ["Verkaufsübersicht", "Conversion Funnel", "Lead-Quellen Analyse"]
    )
    
    # Zeitraum-Auswahl
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "Von",
            value=datetime.now() - timedelta(days=365)
        )
    
    with col2:
        end_date = st.date_input(
            "Bis",
            value=datetime.now()
        )
    
    with col3:
        if report_type == "Verkaufsübersicht":
            period = st.selectbox(
                "Zeitraum-Gruppierung",
                ["monthly", "weekly", "daily"],
                format_func=lambda x: {
                    "monthly": "Monatlich",
                    "weekly": "Wöchentlich",
                    "daily": "Täglich"
                }[x]
            )
        else:
            period = None
    
    # Report generieren
    if st.button("Report generieren", type="primary"):
        with st.spinner("Report wird erstellt..."):
            if report_type == "Verkaufsübersicht":
                result = engine.get_sales_overview(
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    period=period
                )
                
                if result["success"]:
                    # Zusammenfassung anzeigen
                    st.subheader("Zusammenfassung")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Gesamt Angebote", result["summary"]["total_offers"])
                    with col2:
                        st.metric("Angenommen", result["summary"]["accepted_offers"])
                    with col3:
                        st.metric("Abgelehnt", result["summary"]["rejected_offers"])
                    with col4:
                        st.metric(
                            "Conversion Rate",
                            format_percentage(result["summary"]["conversion_rate"])
                        )
                    
                    # Gesamtwert
                    if result["summary"]["total_value"] > 0:
                        st.metric(
                            "Gesamtwert aller Angebote",
                            format_currency(result["summary"]["total_value"])
                        )
                    
                    # Diagramm anzeigen
                    st.plotly_chart(result["chart"], use_container_width=True)
                    
                    # Daten-Tabelle
                    with st.expander("📋 Detaillierte Daten anzeigen"):
                        st.dataframe(result["data"], use_container_width=True)
                    
                    # In Session State speichern für Export
                    st.session_state['last_report_data'] = result["data"]
                    st.session_state['last_report_chart'] = result["chart"]
                else:
                    st.warning(result["message"])
            
            elif report_type == "Conversion Funnel":
                result = engine.get_conversion_funnel(
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d")
                )
                
                if result["success"]:
                    # Zusammenfassung
                    st.subheader("Funnel-Übersicht")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Gesamt Leads", result["total_leads"])
                    with col2:
                        st.metric(
                            "Gesamt Conversion Rate",
                            format_percentage(result["conversion_rates"]["overall_conversion"])
                        )
                    
                    # Conversion-Raten
                    st.subheader("Conversion-Raten pro Stufe")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Lead → Qualifiziert",
                            format_percentage(result["conversion_rates"]["lead_to_qualified"])
                        )
                    with col2:
                        st.metric(
                            "Qualifiziert → Angebot",
                            format_percentage(result["conversion_rates"]["qualified_to_proposal"])
                        )
                    with col3:
                        st.metric(
                            "Angebot → Gewonnen",
                            format_percentage(result["conversion_rates"]["proposal_to_won"])
                        )
                    
                    # Funnel-Diagramm
                    st.plotly_chart(result["chart"], use_container_width=True)
                    
                    # Funnel-Stufen Details
                    with st.expander("Funnel-Stufen Details"):
                        funnel_df = pd.DataFrame([
                            {"Stufe": "Leads", "Anzahl": result["funnel_stages"]["lead"]},
                            {"Stufe": "Qualifiziert", "Anzahl": result["funnel_stages"]["qualified"]},
                            {"Stufe": "Angebot", "Anzahl": result["funnel_stages"]["proposal"]},
                            {"Stufe": "Verhandlung", "Anzahl": result["funnel_stages"]["negotiation"]},
                            {"Stufe": "Gewonnen", "Anzahl": result["funnel_stages"]["won"]},
                            {"Stufe": "Verloren", "Anzahl": result["funnel_stages"]["lost"]}
                        ])
                        st.dataframe(funnel_df, use_container_width=True)
                    
                    st.session_state['last_report_chart'] = result["chart"]
                else:
                    st.warning(result.get("message", "Keine Daten verfügbar"))
            
            elif report_type == "Lead-Quellen Analyse":
                result = engine.get_lead_sources_report(
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d")
                )
                
                if result["success"]:
                    st.subheader("Lead-Quellen Übersicht")
                    
                    # Diagramm
                    st.plotly_chart(result["chart"], use_container_width=True)
                    
                    # Daten-Tabelle
                    st.subheader("Detaillierte Statistiken")
                    
                    # Formatierung für bessere Lesbarkeit
                    display_df = result["data"].copy()
                    display_df.columns = ['Quelle', 'Anzahl Leads', 'Gewonnen', 'Ø Wert', 'Conversion Rate (%)']
                    display_df['Ø Wert'] = display_df['Ø Wert'].apply(lambda x: format_currency(x) if x > 0 else "-")
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    st.session_state['last_report_data'] = result["data"]
                    st.session_state['last_report_chart'] = result["chart"]
                else:
                    st.warning(result["message"])


def render_report_builder(engine: ReportingEngine, conn):
    """Rendert den benutzerdefinierten Report Builder."""
    st.header("Benutzerdefinierter Report Builder")
    
    st.info("Erstellen Sie individuelle Reports mit flexiblen Filtern und Gruppierungen")
    
    # Tabellen-Auswahl
    available_tables = get_available_tables(conn)
    crm_tables = [t for t in available_tables if t.startswith('crm_') or t in ['customers', 'projects']]
    
    selected_table = st.selectbox(
        "Tabelle auswählen",
        crm_tables,
        help="Wählen Sie die Datenquelle für Ihren Report"
    )
    
    if selected_table:
        # Spalten der Tabelle abrufen
        columns = get_table_columns(conn, selected_table)
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_columns = st.multiselect(
                "Spalten auswählen",
                columns,
                default=columns[:5] if len(columns) >= 5 else columns,
                help="Wählen Sie die Spalten, die im Report angezeigt werden sollen"
            )
        
        with col2:
            group_by_columns = st.multiselect(
                "Gruppieren nach (optional)",
                selected_columns,
                help="Gruppieren Sie Daten nach bestimmten Spalten"
            )
        
        # Aggregationen (wenn Gruppierung aktiv)
        aggregations = {}
        if group_by_columns:
            st.subheader("Aggregationen")
            agg_col1, agg_col2 = st.columns(2)
            
            numeric_columns = [col for col in selected_columns if col not in group_by_columns]
            
            with agg_col1:
                agg_column = st.selectbox("Spalte", numeric_columns)
            
            with agg_col2:
                agg_function = st.selectbox(
                    "Funktion",
                    ["COUNT", "SUM", "AVG", "MIN", "MAX"]
                )
            
            if st.button("Aggregation hinzufügen"):
                aggregations[agg_column] = agg_function
                st.success(f"Aggregation hinzugefügt: {agg_function}({agg_column})")
        
        # Filter
        st.subheader("Filter (optional)")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            filter_column = st.selectbox("Filter-Spalte", [""] + columns)
        
        filters = {}
        if filter_column:
            with filter_col2:
                filter_operator = st.selectbox("Operator", ["=", "IN"])
            
            with filter_col3:
                if filter_operator == "IN":
                    filter_value = st.text_input("Werte (kommagetrennt)")
                    if filter_value:
                        filters[filter_column] = [v.strip() for v in filter_value.split(",")]
                else:
                    filter_value = st.text_input("Wert")
                    if filter_value:
                        filters[filter_column] = filter_value
        
        # Zeitraum
        st.subheader("Zeitraum (optional)")
        col1, col2 = st.columns(2)
        
        with col1:
            use_date_filter = st.checkbox("Zeitfilter aktivieren")
        
        start_date = None
        end_date = None
        
        if use_date_filter:
            with col1:
                start_date = st.date_input(
                    "Von",
                    value=datetime.now() - timedelta(days=90)
                ).strftime("%Y-%m-%d")
            
            with col2:
                end_date = st.date_input(
                    "Bis",
                    value=datetime.now()
                ).strftime("%Y-%m-%d")
        
        # Sortierung und Limit
        col1, col2 = st.columns(2)
        
        with col1:
            order_by = st.selectbox("Sortieren nach (optional)", [""] + selected_columns)
        
        with col2:
            limit = st.number_input("Max. Zeilen", min_value=0, value=100, step=10)
        
        # Report generieren
        if st.button("Report erstellen", type="primary"):
            if not selected_columns:
                st.error("Bitte wählen Sie mindestens eine Spalte aus")
                return
            
            with st.spinner("Report wird erstellt..."):
                result = engine.build_custom_report(
                    table=selected_table,
                    columns=selected_columns,
                    filters=filters if filters else None,
                    group_by=group_by_columns if group_by_columns else None,
                    aggregations=aggregations if aggregations else None,
                    start_date=start_date,
                    end_date=end_date,
                    order_by=order_by if order_by else None,
                    limit=limit if limit > 0 else None
                )
                
                if result["success"]:
                    st.success(f"Report erfolgreich erstellt ({result['row_count']} Zeilen)")
                    
                    # Daten anzeigen
                    st.dataframe(result["data"], use_container_width=True)
                    
                    # Query anzeigen
                    with st.expander("SQL Query anzeigen"):
                        st.code(result["query"], language="sql")
                    
                    # In Session State speichern
                    st.session_state['last_report_data'] = result["data"]
                    
                    # Vorlage speichern
                    st.subheader("Als Vorlage speichern")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        template_name = st.text_input("Vorlagen-Name")
                        template_desc = st.text_area("Beschreibung (optional)")
                    
                    with col2:
                        st.write("")
                        st.write("")
                        if st.button("💾 Speichern"):
                            if template_name:
                                config = {
                                    "table": selected_table,
                                    "columns": selected_columns,
                                    "filters": filters,
                                    "group_by": group_by_columns,
                                    "aggregations": aggregations,
                                    "order_by": order_by,
                                    "limit": limit
                                }
                                
                                save_result = engine.save_report_template(
                                    name=template_name,
                                    report_type="custom",
                                    config=config,
                                    description=template_desc
                                )
                                
                                if save_result["success"]:
                                    st.success(save_result["message"])
                                else:
                                    st.error(save_result["message"])
                            else:
                                st.error("Bitte geben Sie einen Namen ein")
                else:
                    st.error(result["message"])


def render_saved_templates(engine: ReportingEngine):
    """Rendert die gespeicherten Report-Vorlagen."""
    st.header("Gespeicherte Report-Vorlagen")
    
    templates = engine.list_report_templates()
    
    if not templates:
        st.info("Noch keine Vorlagen gespeichert. Erstellen Sie einen Report und speichern Sie ihn als Vorlage.")
        return
    
    st.write(f"**{len(templates)} Vorlage(n) verfügbar**")
    
    for template in templates:
        with st.expander(f"{template['name']}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Typ:** {template['report_type']}")
                if template['description']:
                    st.write(f"**Beschreibung:** {template['description']}")
                st.write(f"**Erstellt:** {template['created_at']}")
                if template['created_by']:
                    st.write(f"**Erstellt von:** {template['created_by']}")
                if template['last_used']:
                    st.write(f"**Zuletzt verwendet:** {template['last_used']}")
            
            with col2:
                if st.button("▶️ Ausführen", key=f"run_{template['id']}"):
                    result = engine.load_report_template(template['id'])
                    if result["success"]:
                        st.info("Vorlage geladen. Bitte wechseln Sie zum Report Builder Tab.")
                        st.session_state['loaded_template'] = result['template']
                    else:
                        st.error(result["message"])
            
            with col3:
                if st.button("Löschen", key=f"del_{template['id']}"):
                    result = engine.delete_report_template(template['id'])
                    if result["success"]:
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])


def render_export_section():
    """Rendert die Export-Sektion."""
    st.header("Report Export")
    
    if 'last_report_data' not in st.session_state:
        st.info("Erstellen Sie zuerst einen Report, um ihn zu exportieren.")
        return
    
    df = st.session_state['last_report_data']
    
    st.write(f"**Aktueller Report:** {len(df)} Zeilen")
    
    # Export-Optionen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Excel Export
        st.subheader("Excel")
        
        conn = get_db_connection()
        if conn:
            engine = ReportingEngine(conn)
            excel_data = engine.export_to_excel(df)
            conn.close()
            
            st.download_button(
                label="Excel herunterladen",
                data=excel_data,
                file_name=f"crm_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        # CSV Export
        st.subheader("CSV")
        
        conn = get_db_connection()
        if conn:
            engine = ReportingEngine(conn)
            csv_data = engine.export_to_csv(df)
            conn.close()
            
            st.download_button(
                label="CSV herunterladen",
                data=csv_data,
                file_name=f"crm_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        # Chart Export (wenn vorhanden)
        if 'last_report_chart' in st.session_state:
            st.subheader("Diagramm")
            
            conn = get_db_connection()
            if conn:
                engine = ReportingEngine(conn)
                html_data = engine.export_chart_to_html(st.session_state['last_report_chart'])
                conn.close()
                
                st.download_button(
                    label="HTML herunterladen",
                    data=html_data,
                    file_name=f"crm_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )


if __name__ == "__main__":
    render_reporting_ui()
