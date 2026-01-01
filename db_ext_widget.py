"""
Phase 11: Database Extensions - Widget Library

Widgets für DB Performance Monitoring, Slow Queries, Connection Pool.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime


def render_db_performance_widget(
    key_prefix: str = "db_perf"
) -> None:
    """
    Widget für DB Performance Monitoring.
    
    Zeigt:
    - Query Performance Metriken
    - Ausführungszeiten
    - Erfolgsraten
    - Performance-Trends
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("⚡ Datenbank Performance")
    
    try:
        from core.db_performance import get_db_performance_monitor
        
        monitor = get_db_performance_monitor()
        try:
            stats = monitor.get_stats()
        except Exception:
            stats = {}
        
        # KPI-Metriken
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt Abfragen", f"{stats.get('total_queries', 0):,}")
        
        with col2:
            avg_duration = stats.get('avg_duration_ms', 0)
            st.metric("Ø Dauer", f"{avg_duration:.2f} ms")
        
        with col3:
            slow_queries = stats.get('slow_queries', 0)
            st.metric(
                "Langsame Abfragen",
                slow_queries,
                delta="Problem" if slow_queries > 0 else "OK",
                delta_color="inverse" if slow_queries > 0 else "off"
            )
        
        with col4:
            success_rate = stats.get('success_rate', 0) * 100
            st.metric("Erfolgsrate", f"{success_rate:.1f}%")
        
        st.markdown("---")
        
        # Performance-Chart
        if stats.get('recent_queries'):
            st.markdown("**📊 Performance-Trend (Letzte 20 Abfragen):**")
            
            import plotly.graph_objects as go
            
            recent = stats['recent_queries'][-20:]
            
            fig = go.Figure()
            
            # Query Dauer
            fig.add_trace(go.Scatter(
                y=[q['duration_ms'] for q in recent],
                mode='lines+markers',
                name='Dauer (ms)',
                line=dict(color='#ff8c00', width=2),
                marker=dict(size=8)
            ))
            
            # Schwellenwert
            threshold = monitor.slow_query_threshold_ms
            fig.add_hline(
                y=threshold,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Schwellenwert Langsame Abfragen ({threshold}ms)"
            )
            
            fig.update_layout(
                title="Abfrage-Ausführungszeiten",
                xaxis_title="Abfrage #",
                yaxis_title="Dauer (ms)",
                height=350,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Verbindungspool Metriken
        st.markdown("---")
        st.markdown("**🔌 Verbindungspool:**")
        
        pool_stats = stats.get('connection_pool', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Aktive Verbindungen", pool_stats.get('active_connections', 0))
        
        with col2:
            st.metric("Inaktive Verbindungen", pool_stats.get('idle_connections', 0))
        
        with col3:
            st.metric("Max. Verbindungen", pool_stats.get('max_connections', 0))
        
        with col4:
            wait_time = pool_stats.get('avg_wait_time_ms', 0)
            st.metric("Ø Wartezeit", f"{wait_time:.2f} ms")
        
        # Aktionen
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Metriken aktualisieren", key=f"{key_prefix}_refresh"):
                st.rerun()
        
        with col2:
            if st.button("🗑️ Metriken zurücksetzen", key=f"{key_prefix}_clear"):
                monitor.clear_metrics()
                st.success("✅ Metriken zurückgesetzt!")
                st.rerun()
        
        with col3:
            # Sampling Rate anpassen
            with st.popover("⚙️ Einstellungen"):
                sampling_rate = st.slider(
                    "Abtastrate (%)",
                    1, 100, 100,
                    key=f"{key_prefix}_sampling",
                    help="Prozentsatz der Abfragen die getrackt werden"
                )
                
                slow_threshold = st.number_input(
                    "Schwellenwert Langsame Abfragen (ms)",
                    min_value=100,
                    max_value=10000,
                    value=1000,
                    step=100,
                    key=f"{key_prefix}_threshold"
                )
                
                if st.button("💾 Speichern", key=f"{key_prefix}_save"):
                    monitor.set_sampling_rate(sampling_rate / 100)
                    monitor.set_slow_query_threshold(slow_threshold)
                    st.success("✅ Einstellungen gespeichert!")
    
    except ImportError:
        st.error("DB Performance Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_slow_queries_widget(
    key_prefix: str = "slow_queries"
) -> None:
    """
    Widget für Slow Query Detection und Analyse.
    
    Zeigt:
    - Liste langsamer Queries
    - Query-Details
    - Optimierungs-Hinweise
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("🐌 Langsame Abfragen")
    
    try:
        from core.db_performance import get_db_performance_monitor
        
        monitor = get_db_performance_monitor()
        
        # Limit-Auswahl
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Langsame Queries analysieren und optimieren**")
        with col2:
            limit = st.selectbox(
                "Anzahl",
                [5, 10, 20, 50],
                index=1,
                key=f"{key_prefix}_limit"
            )
        
        slow_queries = monitor.get_slow_queries(limit=limit)
        
        if slow_queries:
            st.metric("Gefundene langsame Abfragen", len(slow_queries))
            
            st.markdown("---")
            
            # Query-Liste
            for idx, query in enumerate(slow_queries, 1):
                with st.expander(
                    f"**#{idx}** - {query.duration_ms:.2f} ms - {query.timestamp.split('T')[1][:8]}",
                    expanded=(idx == 1)
                ):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**SQL:**")
                        st.code(query.sql, language="sql")
                        
                        if query.error:
                            st.error(f"❌ **Fehler:** {query.error}")
                    
                    with col2:
                        st.metric("Dauer", f"{query.duration_ms:.2f} ms")
                        st.metric("Rows", query.rows_affected or "N/A")
                        st.metric("Status", "✅ Erfolg" if query.success else "❌ Fehler")
                        
                        # Optimierungs-Hinweise
                        st.markdown("**💡 Hinweise:**")
                        
                        hints = []
                        if query.duration_ms > 2000:
                            hints.append("⚠️ Sehr langsam (>2s)")
                        if "SELECT *" in query.sql.upper():
                            hints.append("💡 Vermeide SELECT *")
                        if "JOIN" in query.sql.upper() and "WHERE" not in query.sql.upper():
                            hints.append("💡 Füge WHERE hinzu")
                        if query.rows_affected and query.rows_affected > 10000:
                            hints.append("💡 Limitiere Ergebnisse")
                        
                        if hints:
                            for hint in hints:
                                st.caption(hint)
                        else:
                            st.caption("✅ Keine Hinweise")
        else:
            st.success("✅ Keine langsamen Abfragen gefunden!")
            st.info("Alle Abfragen laufen unter dem Schwellenwert.")
        
        # Threshold-Konfiguration
        st.markdown("---")
        with st.expander("⚙️ Threshold konfigurieren"):
            threshold = st.number_input(
                "Schwellenwert Langsame Abfragen (ms)",
                min_value=100,
                max_value=10000,
                value=monitor.slow_query_threshold_ms,
                step=100,
                key=f"{key_prefix}_threshold",
                help="Abfragen über diesem Wert gelten als langsam"
            )
            
            if st.button("💾 Schwellenwert speichern", key=f"{key_prefix}_save_threshold"):
                monitor.set_slow_query_threshold(threshold)
                st.success(f"✅ Schwellenwert auf {threshold}ms gesetzt!")
                st.rerun()
    
    except ImportError:
        st.error("DB Performance Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_query_optimizer_widget(
    key_prefix: str = "query_opt"
) -> None:
    """
    Widget für Query-Optimierung.
    
    Zeigt:
    - Query-Analyse
    - Index-Empfehlungen
    - Optimierungs-Vorschläge
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("🎯 Abfrage-Optimierer")
    
    st.info("🚧 Abfrage-Optimierer ist in Entwicklung")
    
    # Abfrage-Eingabe für Analyse
    st.markdown("**SQL-Abfrage analysieren:**")
    
    query_input = st.text_area(
        "SQL-Abfrage",
        placeholder="SELECT * FROM users WHERE ...",
        height=100,
        key=f"{key_prefix}_query"
    )
    
    if st.button("🔍 Abfrage analysieren", key=f"{key_prefix}_analyze"):
        if query_input:
            with st.spinner("Analysiere Abfrage..."):
                # Placeholder für zukünftige Implementierung
                st.markdown("**📊 Analyse-Ergebnis:**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🔍 Erkannte Muster:**")
                    patterns = []
                    
                    if "SELECT *" in query_input.upper():
                        patterns.append("⚠️ SELECT * - Spezifiziere Spalten")
                    if "JOIN" in query_input.upper():
                        patterns.append("✅ JOIN gefunden")
                    if "WHERE" in query_input.upper():
                        patterns.append("✅ WHERE-Klausel vorhanden")
                    if "LIMIT" in query_input.upper():
                        patterns.append("✅ LIMIT verwendet")
                    
                    for p in patterns:
                        st.write(p)
                
                with col2:
                    st.markdown("**💡 Empfehlungen:**")
                    
                    recommendations = [
                        "Füge Index auf häufig verwendete WHERE-Spalten hinzu",
                        "Verwende EXPLAIN zur Analyse des Query-Plans",
                        "Erwäge materialized views für komplexe Queries"
                    ]
                    
                    for rec in recommendations:
                        st.write(f"• {rec}")
        else:
            st.warning("Bitte Abfrage eingeben")
    
    # Automatische Optimierungs-Vorschläge
    st.markdown("---")
    st.markdown("**🤖 Automatische Vorschläge:**")
    
    with st.expander("Index-Empfehlungen"):
        st.markdown("""
        Basierend auf Ihren Slow Queries werden folgende Indizes empfohlen:
        
        - `CREATE INDEX idx_users_email ON users(email);`
        - `CREATE INDEX idx_projects_customer_id ON projects(customer_id);`
        - `CREATE INDEX idx_calculations_timestamp ON calculations(timestamp);`
        """)
    
    with st.expander("Abfrage-Umschreibungen"):
        st.markdown("""
        Folgende Abfragen können optimiert werden:
        
        **Vorher:**
        ```sql
        SELECT * FROM users WHERE status = 'active';
        ```
        
        **Nachher:**
        ```sql
        SELECT id, name, email FROM users WHERE status = 'active' LIMIT 1000;
        ```
        """)


def render_connection_pool_widget(
    key_prefix: str = "conn_pool"
) -> None:
    """
    Widget für Connection Pool Monitoring.
    
    Zeigt:
    - Pool-Status
    - Connection-Metriken
    - Wartezeiten
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("🔌 Verbindungspool")
    
    try:
        from core.db_performance import get_db_performance_monitor
        
        monitor = get_db_performance_monitor()
        try:
            stats = monitor.get_stats()
        except Exception:
            stats = {}
        pool_stats = stats.get('connection_pool', {})
        
        # Pool-Status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            active = pool_stats.get('active_connections', 0)
            max_conn = pool_stats.get('max_connections', 0)
            st.metric(
                "Aktive Verbindungen",
                active,
                delta=f"{active}/{max_conn}",
                delta_color="off"
            )
        
        with col2:
            idle = pool_stats.get('idle_connections', 0)
            st.metric("Inaktive Verbindungen", idle)
        
        with col3:
            wait_time = pool_stats.get('avg_wait_time_ms', 0)
            st.metric("Ø Wartezeit", f"{wait_time:.2f} ms")
        
        with col4:
            max_wait = pool_stats.get('max_wait_time_ms', 0)
            st.metric("Max. Wartezeit", f"{max_wait:.2f} ms")
        
        # Pool-Auslastung Visualisierung
        st.markdown("---")
        st.markdown("**📊 Pool-Auslastung:**")
        
        if max_conn > 0:
            usage_percent = (active / max_conn * 100) if max_conn > 0 else 0
            
            # Progress Bar
            st.progress(usage_percent / 100 if usage_percent <= 100 else 1.0)
            st.caption(f"{usage_percent:.1f}% ausgelastet ({active} von {max_conn})")
            
            # Warnung bei hoher Auslastung
            if usage_percent > 80:
                st.warning("⚠️ Hohe Pool-Auslastung! Erwäge Pool-Vergrößerung.")
            elif usage_percent > 95:
                st.error("🔴 Kritische Pool-Auslastung! Pool ist nahezu voll.")
        
        # Verbindungs-Statistiken
        st.markdown("---")
        st.markdown("**📈 Verbindungs-Statistiken:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Gesamt erstellt", pool_stats.get('total_connections_created', 0))
            st.metric("Gesamt geschlossen", pool_stats.get('total_connections_closed', 0))
        
        with col2:
            st.metric("Zeitüberschreitungen", pool_stats.get('connection_timeouts', 0))
            st.metric("Fehler", pool_stats.get('connection_errors', 0))
        
        # Pool-Konfiguration
        st.markdown("---")
        with st.expander("⚙️ Pool-Konfiguration"):
            st.markdown("""
            **Empfohlene Einstellungen:**
            
            - **Min. Pool-Größe:** 5-10 Verbindungen
            - **Max. Pool-Größe:** 20-50 Verbindungen (abhängig von Last)
            - **Verbindungs-Timeout:** 30 Sekunden
            - **Inaktivitäts-Timeout:** 300 Sekunden (5 Minuten)
            
            ⚠️ Änderungen erfordern App-Neustart.
            """)
    
    except ImportError:
        st.error("DB Performance Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_db_analytics_widget(
    key_prefix: str = "db_analytics"
) -> None:
    """
    Widget für DB Analytics.
    
    Zeigt:
    - Query-Pattern-Analyse
    - Performance-Trends
    - Nutzungs-Statistiken
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("📊 Datenbank-Analysen")
    
    try:
        from core.db_performance import get_db_performance_monitor
        
        monitor = get_db_performance_monitor()
        try:
            stats = monitor.get_stats()
        except Exception:
            stats = {}
        
        # Performance-Übersicht
        st.markdown("**⚡ Performance-Übersicht:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_queries = stats.get('total_queries', 0)
            st.metric("Gesamt Abfragen", f"{total_queries:,}")
        
        with col2:
            avg_duration = stats.get('avg_duration_ms', 0)
            st.metric("Ø Abfrage-Dauer", f"{avg_duration:.2f} ms")
        
        with col3:
            success_rate = stats.get('success_rate', 0) * 100
            st.metric("Erfolgsrate", f"{success_rate:.1f}%")
        
        # Abfrage-Verteilung
        st.markdown("---")
        st.markdown("**📊 Abfrage-Typ-Verteilung:**")
        
        query_types = stats.get('query_type_distribution', {})
        
        if query_types:
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(query_types.keys()),
                    values=list(query_types.values()),
                    marker_colors=['#ff8c00', '#ffa500', '#ffb347', '#ffc26b']
                )
            ])
            
            fig.update_layout(
                title="Abfrage-Typ-Verteilung",
                height=300,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance-Trend
        st.markdown("---")
        st.markdown("**📈 Performance-Trend:**")
        
        if stats.get('recent_queries'):
            import plotly.graph_objects as go
            
            recent = stats['recent_queries'][-50:]
            
            # Berechne gleitenden Durchschnitt
            window_size = 10
            moving_avg = []
            for i in range(len(recent)):
                start = max(0, i - window_size + 1)
                window = recent[start:i+1]
                avg = sum(q['duration_ms'] for q in window) / len(window) if len(window) > 0 else 0
                moving_avg.append(avg)
            
            fig = go.Figure()
            
            # Einzelne Abfrage-Zeiten
            fig.add_trace(go.Scatter(
                y=[q['duration_ms'] for q in recent],
                mode='markers',
                name='Abfrage-Dauer',
                marker=dict(color='lightgray', size=6)
            ))
            
            # Gleitender Durchschnitt
            fig.add_trace(go.Scatter(
                y=moving_avg,
                mode='lines',
                name=f'Gleitender Ø ({window_size})',
                line=dict(color='#ff8c00', width=3)
            ))
            
            fig.update_layout(
                title=f"Performance-Trend (Letzte {len(recent)} Abfragen)",
                xaxis_title="Abfrage #",
                yaxis_title="Dauer (ms)",
                height=350,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Top Slow Tables
        st.markdown("---")
        st.markdown("**🐌 Langsamste Tabellen:**")
        
        slow_tables = stats.get('slow_tables', [])
        
        if slow_tables:
            import pandas as pd
            df = pd.DataFrame(slow_tables)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Keine Daten verfügbar")
    
    except ImportError:
        st.error("DB Analytics Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_db_ext_admin(
    show_header: bool = True,
    key_prefix: str = "db_ext_admin"
) -> None:
    """
    Vollständiges Admin-Panel für Database Extensions.
    
    Kombiniert alle DB-Extension-Widgets in einem Dashboard.
    
    Args:
        show_header: Zeige Header
        key_prefix: Prefix für Widget-Keys
    """
    if show_header:
        st.title("🗄️ Datenbank-Erweiterungen Administration")
        st.markdown("**Verwalten Sie DB-Performance, Langsame Abfragen und Verbindungspool**")
        st.markdown("---")
    
    # CSS für Tab-Styling (Weiße Tabs mit Schattierungen)
    st.markdown("""
    <style>
    /* Tab-Container mit weißem Hintergrund */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background-color: #ffffff !important;
        gap: 8px;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Tabs mit weißem Hintergrund und Schatten */
    [data-testid="stTabs"] [data-baseweb="tab"] {
        background: #ffffff !important;
        border-radius: 8px 8px 0 0 !important;
        border: 1px solid #e0e0e0 !important;
        border-bottom: none !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06) !important;
    }
    
    /* Tab Hover-Effekt */
    [data-testid="stTabs"] [data-baseweb="tab"]:hover {
        background: #ffffff !important;
        border-color: #ff8c00 !important;
        box-shadow: 0 4px 12px rgba(255, 140, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Aktiver Tab mit oranger Akzent */
    [data-testid="stTabs"] [aria-selected="true"] {
        background: #ffffff !important;
        border-color: #ff8c00 !important;
        border-bottom: 3px solid #ff8c00 !important;
        color: #ff8c00 !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 16px rgba(255, 140, 0, 0.2), 0 3px 6px rgba(0, 0, 0, 0.12) !important;
    }
    
    /* Tab-Content mit weißem Hintergrund */
    [data-testid="stTabs"] [data-baseweb="tab-panel"] {
        background: #ffffff !important;
        padding: 20px !important;
        border-radius: 0 0 10px 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        margin-top: -1px;
    }
    
    /* Code-Blöcke mit hellgrauem Hintergrund */
    code {
        background-color: #f5f5f5 !important;
        color: #333333 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    pre {
        background-color: #f5f5f5 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 6px !important;
        padding: 16px !important;
    }
    
    pre code {
        background-color: transparent !important;
        color: #333333 !important;
        border: none !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Tabs für verschiedene Bereiche
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚡ Performance",
        "🐌 Langsame Abfragen",
        "🎯 Abfrage-Optimierer",
        "🔌 Verbindungspool",
        "📊 Analysen"
    ])
    
    with tab1:
        render_db_performance_widget(key_prefix=f"{key_prefix}_perf")
    
    with tab2:
        render_slow_queries_widget(key_prefix=f"{key_prefix}_slow")
    
    with tab3:
        render_query_optimizer_widget(key_prefix=f"{key_prefix}_opt")
    
    with tab4:
        render_connection_pool_widget(key_prefix=f"{key_prefix}_pool")
    
    with tab5:
        render_db_analytics_widget(key_prefix=f"{key_prefix}_analytics")


if __name__ == "__main__":
    # Test-Modus
    st.set_page_config(page_title="DB-Erweiterungen Widgets", layout="wide")
    render_db_ext_admin()
