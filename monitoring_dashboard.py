"""
Application Monitoring Dashboard.

Displays real-time tracing and evaluation metrics in Streamlit UI.
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from app_evaluation import evaluation_system


def render_monitoring_dashboard():
    """Render the complete monitoring dashboard."""
    
    st.title("Anwendungsüberwachung & Auswertung")
    
    # CSS für Tabs mit Schattierungen und orangenen Akzenten
    st.markdown("""
    <style>
    /* Tab-Container transparent (kein schwarzer Hintergrund) */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 8px !important;
        padding: 10px 0 !important;
    }
    
    /* Tab-Buttons mit weißem Hintergrund, Schatten und orangen Akzenten */
    .stTabs [data-baseweb="tab-list"] button {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        border: 2px solid transparent !important;
        border-radius: 12px 12px 0 0 !important;
        padding: 14px 24px !important;
        font-weight: 700 !important;
        color: #2d3748 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06) !important;
        margin-right: 4px !important;
    }
    
    /* Hover-Effekt mit orangenem Akzent */
    .stTabs [data-baseweb="tab-list"] button:hover {
        border-color: rgba(255, 140, 0, 0.4) !important;
        box-shadow: 0 6px 8px rgba(255, 140, 0, 0.2), 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px) !important;
        color: #ff8c00 !important;
    }
    
    /* Aktiver Tab mit orangenen Akzenten und stärkerem Schatten */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #ffffff 0%, #fff8f0 100%) !important;
        border-color: #ff8c00 !important;
        border-bottom: 4px solid #ff8c00 !important;
        color: #ff8c00 !important;
        box-shadow: 0 8px 12px rgba(255, 140, 0, 0.25), 0 6px 8px rgba(0, 0, 0, 0.1), inset 0 1px 3px rgba(255, 140, 0, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Tab-Content ohne schwarzen Hintergrund */
    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        padding: 20px 0 !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tabs = st.tabs([
        "Systemstatus",
        "Leistung",
        "Genauigkeit",
        "Fehler",
        "Berichte"
    ])
    
    # Tab 1: Health Status
    with tabs[0]:
        render_health_status()
    
    # Tab 2: Performance
    with tabs[1]:
        render_performance_metrics()
    
    # Tab 3: Accuracy
    with tabs[2]:
        render_accuracy_metrics()
    
    # Tab 4: Errors
    with tabs[3]:
        render_error_tracking()
    
    # Tab 5: Reports
    with tabs[4]:
        render_reports()


def render_health_status():
    """Render overall health status."""
    
    st.header("Anwendungsstatus")
    
    # Testdaten-Generator Button
    col_test1, col_test2 = st.columns([3, 1])
    with col_test2:
        if st.button("🧪 Testdaten generieren", use_container_width=True, help="Generiert Beispieldaten für die Anzeige"):
            _generate_test_data()
            st.success("Testdaten wurden generiert!")
            st.rerun()
    
    health = evaluation_system.get_health_status()
    
    # Status badge
    status_colors = {
        "HEALTHY": "🟢",
        "DEGRADED": "🟡",
        "UNHEALTHY": ""
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Status",
            f"{status_colors.get(health['status'], '')} {health['status']}"
        )
    
    with col2:
        st.metric(
            "Fehlerrate",
            f"{health['error_rate']*100:.2f}%"
        )
    
    with col3:
        st.metric(
            "Gesamtoperationen",
            health['total_operations']
        )
    
    # Detailed metrics
    st.subheader("Systemmetriken")
    
    report = evaluation_system.generate_report()
    summary = report.get("summary", {})
    
    if "performance" in summary:
        perf = summary["performance"]
        st.write("**Leistung:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Ø Zeit", f"{perf['average_execution_time']:.3f}s")
        with col2:
            st.metric("Akzeptanzrate", f"{perf['acceptable_performance_rate']*100:.1f}%")
        with col3:
            st.metric("Ø Bewertung", f"{perf['average_score']:.2f}/5")
    
    if "accuracy" in summary:
        acc = summary["accuracy"]
        st.write("**Genauigkeit:**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Gültige Ergebnisse", f"{acc['valid_results_rate']*100:.1f}%")
        with col2:
            st.metric("Genauigkeitsrate", f"{acc['accuracy_rate']*100:.1f}%")
    
    if "errors" in summary:
        err = summary["errors"]
        st.write("**Fehler:**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Erfolgsrate", f"{err['success_rate']*100:.1f}%")
        with col2:
            st.metric("Fehleranzahl", err['error_count'])
    
    # Zeige letzte Scan-Ergebnisse
    st.markdown("---")
    st.subheader("Letzte Code-Analyse")
    
    scan_report = _load_scan_report()
    if scan_report:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Gefundene Issues", scan_report.get('total_issues', 0))
        with col2:
            critical = scan_report.get('severity_breakdown', {}).get('CRITICAL', 0)
            st.metric("Kritisch", critical, delta="-" if critical > 0 else "OK", delta_color="inverse")
        with col3:
            high = scan_report.get('severity_breakdown', {}).get('HIGH', 0)
            st.metric("Hoch", high)
        with col4:
            files = len(scan_report.get('top_problematic_files', []))
            st.metric("Betroffene Dateien", files)
        
        # Top Issues anzeigen
        if scan_report.get('issues'):
            with st.expander("🔍 Top Issues anzeigen", expanded=False):
                import pandas as pd
                issues_df = pd.DataFrame(scan_report['issues'][:10])
                st.dataframe(issues_df, use_container_width=True)
    else:
        st.info("Keine Scan-Ergebnisse verfügbar. Klicken Sie auf 'Rescan Application' um einen Scan durchzuführen.")


def render_performance_metrics():
    """Render performance metrics and charts."""
    
    st.header("Leistungsmetriken")
    
    metrics = evaluation_system.performance_evaluator.metrics
    
    if not metrics:
        st.warning("Noch keine Leistungsdaten verfügbar. Nutzen Sie die Anwendung, um Metriken zu sammeln.")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🧪 Testdaten generieren", key="test_perf", use_container_width=True):
                _generate_test_data()
                st.success("Testdaten generiert!")
                st.rerun()
        return
    
    # Recent metrics
    st.subheader("Letzte Operationen")
    
    recent = metrics[-20:]
    
    # Performance chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=[m['operation'] for m in recent],
        y=[m['execution_time_seconds'] for m in recent],
        marker_color=[
            'green' if m['is_acceptable'] else 'red'
            for m in recent
        ],
        text=[f"{m['performance_score']}/5" for m in recent],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Ausführungszeiten (Letzte 20 Operationen)",
        xaxis_title="Operation",
        yaxis_title="Zeit (Sekunden)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance distribution
    st.subheader("Leistungsverteilung")
    
    scores = [m['performance_score'] for m in metrics]
    score_dist = {i: scores.count(i) for i in range(1, 6)}
    
    fig2 = go.Figure(data=[
        go.Bar(
            x=list(score_dist.keys()),
            y=list(score_dist.values()),
            marker_color=['red', 'orange', 'yellow', 'lightgreen', 'green']
        )
    ])
    
    fig2.update_layout(
        title="Verteilung der Leistungsbewertung",
        xaxis_title="Bewertung (1-5)",
        yaxis_title="Anzahl",
        height=300
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Statistics table
    st.subheader("Statistiken")
    
    import pandas as pd
    
    df = pd.DataFrame(metrics)
    
    stats = df.groupby('operation').agg({
        'execution_time_seconds': ['mean', 'min', 'max', 'count'],
        'is_acceptable': 'mean',
        'performance_score': 'mean'
    }).round(3)
    
    st.dataframe(stats, use_container_width=True)


def render_accuracy_metrics():
    """Render accuracy metrics."""
    
    st.header("Berechnungsgenauigkeit")
    
    metrics = evaluation_system.accuracy_evaluator.metrics
    
    if not metrics:
        st.warning("Noch keine Genauigkeitsdaten verfügbar.")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🧪 Testdaten generieren", key="test_acc", use_container_width=True):
                _generate_test_data()
                st.success("Testdaten generiert!")
                st.rerun()
        return
    
    # Validity chart
    valid_count = sum(1 for m in metrics if m['is_valid'])
    invalid_count = len(metrics) - valid_count
    
    fig = go.Figure(data=[
        go.Pie(
            labels=['Gültig', 'Ungültig'],
            values=[valid_count, invalid_count],
            marker_colors=['green', 'red']
        )
    ])
    
    fig.update_layout(
        title="Ergebnisgültigkeit",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent calculations
    st.subheader("Letzte Berechnungen")
    
    import pandas as pd
    
    recent = metrics[-10:]
    
    data = []
    for m in recent:
        row = {
            "Typ": m['calculation_type'],
            "Ergebnis": f"{m['result']:.2f}" if isinstance(m['result'], (int, float)) else str(m['result']),
            "Gültig": "OK" if m['is_valid'] else "FEHLER",
            "Zeit": m['timestamp'][-8:]  # Last 8 chars (time only)
        }
        
        if 'expected' in m:
            row["Erwartet"] = f"{m['expected']:.2f}"
            row["Fehler %"] = f"{m['error_percentage']:.2f}%"
            row["Genau"] = "OK" if m['is_accurate'] else "FEHLER"
        
        data.append(row)
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)


def render_error_tracking():
    """Render error tracking information."""
    
    st.header("Fehlerverfolgung")
    
    metrics = evaluation_system.error_rate_evaluator.metrics
    
    if not metrics:
        st.warning("Noch keine Fehlerdaten verfügbar.")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🧪 Testdaten generieren", key="test_err", use_container_width=True):
                _generate_test_data()
                st.success("Testdaten generiert!")
                st.rerun()
        return
    
    # Error rate over time
    st.subheader("Fehlerrate im Zeitverlauf")
    
    fig = go.Figure()
    
    error_rates = [m['error_rate'] for m in metrics]
    
    fig.add_trace(go.Scatter(
        y=error_rates,
        mode='lines+markers',
        name='Fehlerrate',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title="Fehlerrate im Zeitverlauf",
        xaxis_title="Operationsnummer",
        yaxis_title="Fehlerrate",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Error details
    st.subheader("Letzte Fehler")
    
    errors = [m for m in metrics if not m['success']]
    
    if errors:
        import pandas as pd
        
        recent_errors = errors[-10:]
        
        df = pd.DataFrame([{
            "Operation": e['operation'],
            "Fehlertyp": e.get('error_type', 'Unbekannt'),
            "Nachricht": e.get('error_message', 'Keine Nachricht')[:50] + "...",
            "Zeit": e['timestamp'][-8:]
        } for e in recent_errors])
        
        st.dataframe(df, use_container_width=True)
    else:
        st.success("Keine Fehler aufgezeichnet!")


def render_reports():
    """Render evaluation reports."""
    
    st.header("Auswertungsberichte")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Aktueller Sitzungsbericht")
    
    with col2:
        if st.button(" Bericht herunterladen", type="primary"):
            report = evaluation_system.generate_report()
            filepath = evaluation_system.save_report(report)
            st.success(f"Bericht gespeichert: {filepath.name}")
    
    # Generate and display report
    report = evaluation_system.generate_report()
    
    st.json(report, expanded=False)
    
    # Previous reports
    st.subheader("Frühere Berichte")
    
    report_dir = Path("evaluation_results")
    
    if report_dir.exists():
        reports = sorted(report_dir.glob("evaluation_report_*.json"), reverse=True)
        
        if reports:
            for report_file in reports[:5]:  # Last 5 reports
                with st.expander(f" {report_file.name}"):
                    try:
                        with open(report_file, 'r') as f:
                            old_report = json.load(f)
                        st.json(old_report, expanded=False)
                    except Exception as e:
                        st.error(f"Fehler beim Laden des Berichts: {e}")
        else:
            st.info("Keine früheren Berichte gefunden.")


def _load_scan_report() -> dict:
    """Lade letzten Scan-Report."""
    try:
        import json
        scan_file = Path("code_analysis_report.json")
        if scan_file.exists():
            with open(scan_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden des Scan-Reports: {e}")
    return None


def _generate_test_data():
    """Generiere Testdaten für das Monitoring."""
    try:
        from app_evaluation import track_success, track_error, evaluate_performance
        import time
        import random
        
        # Generiere Performance-Daten
        operations = ['calculation', 'pdf_generation', 'data_input', 'analysis', 'database_query']
        for _ in range(10):
            op = random.choice(operations)
            exec_time = random.uniform(0.05, 2.5)
            evaluate_performance(op, exec_time)
            if random.random() > 0.15:  # 85% Erfolgsrate
                track_success(op)
            else:
                track_error(op, "Beispielfehler für Testzwecke")
        
        # Generiere Accuracy-Daten
        from app_evaluation import evaluation_system
        for _ in range(5):
            calc_type = random.choice(['pv_yield', 'amortization', 'savings'])
            result = random.uniform(1000, 50000)
            expected = result * random.uniform(0.95, 1.05)
            evaluation_system.accuracy_evaluator.evaluate_calculation(
                calculation_type=calc_type,
                result=result,
                expected=expected
            )
        
    except Exception as e:
        print(f"Fehler beim Generieren von Testdaten: {e}")


if __name__ == "__main__":
    # Test dashboard
    render_monitoring_dashboard()
