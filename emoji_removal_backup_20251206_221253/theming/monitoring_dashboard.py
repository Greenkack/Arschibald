"""
Monitoring Dashboard - Visualisierung von Theme-System-Metriken

Dieses Modul stellt ein interaktives Dashboard zur Überwachung des Theme-Systems bereit.
Es zeigt Logs, Statistiken, Performance-Metriken und Fehler in Echtzeit an.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter

try:
    from theming.theme_logger import get_theme_logger, ThemeLogger, LogEntry
except ImportError:
    from theme_logger import get_theme_logger, ThemeLogger, LogEntry


def render_monitoring_dashboard(
    logger: Optional[ThemeLogger] = None,
    show_in_sidebar: bool = False
) -> None:
    """
    Rendert das Monitoring-Dashboard
    
    Args:
        logger: ThemeLogger-Instanz (optional, wird automatisch geholt)
        show_in_sidebar: Ob Dashboard in Sidebar angezeigt werden soll
    """
    if logger is None:
        logger = get_theme_logger()
    
    container = st.sidebar if show_in_sidebar else st
    
    with container:
        st.subheader("🔍 Theme System Monitoring")
        
        # Tabs für verschiedene Ansichten
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Übersicht",
            "📝 Logs",
            "⚡ Performance",
            "⚙️ Einstellungen"
        ])
        
        with tab1:
            _render_overview_tab(logger)
        
        with tab2:
            _render_logs_tab(logger)
        
        with tab3:
            _render_performance_tab(logger)
        
        with tab4:
            _render_settings_tab(logger)


def _render_overview_tab(logger: ThemeLogger) -> None:
    """Rendert Übersichts-Tab"""
    st.markdown("### 📈 Statistiken")
    
    stats = logger.get_stats()
    
    # Metriken in Spalten
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Theme-Wechsel",
            stats['theme_switches'],
            help="Anzahl der Theme-Wechsel"
        )
    
    with col2:
        st.metric(
            "CSS-Injections",
            stats['css_injections'],
            help="Anzahl der CSS-Injection-Ereignisse"
        )
    
    with col3:
        st.metric(
            "Komponenten",
            stats['component_renders'],
            help="Anzahl der gerenderten Komponenten"
        )
    
    with col4:
        st.metric(
            "Fehler",
            stats['errors'],
            delta=-stats['errors'] if stats['errors'] > 0 else None,
            delta_color="inverse",
            help="Anzahl der aufgetretenen Fehler"
        )
    
    # Cache-Statistiken
    st.markdown("### 💾 Cache-Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Cache Hits",
            stats['cache_hits'],
            help="Anzahl erfolgreicher Cache-Zugriffe"
        )
    
    with col2:
        st.metric(
            "Cache Misses",
            stats['cache_misses'],
            help="Anzahl fehlgeschlagener Cache-Zugriffe"
        )
    
    with col3:
        st.metric(
            "Hit Rate",
            stats['cache_hit_rate'],
            help="Prozentsatz erfolgreicher Cache-Zugriffe"
        )
    
    # Aktivitäts-Timeline
    st.markdown("### 📅 Aktivitäts-Timeline")
    
    recent_entries = logger.get_recent_entries(count=100)
    
    if recent_entries:
        # Gruppiere nach Stunde
        activity_by_hour = Counter()
        for entry in recent_entries:
            hour = entry.timestamp.replace(minute=0, second=0, microsecond=0)
            activity_by_hour[hour] += 1
        
        # Erstelle Chart
        hours = sorted(activity_by_hour.keys())
        counts = [activity_by_hour[h] for h in hours]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hours,
            y=counts,
            mode='lines+markers',
            name='Aktivität',
            line=dict(color='#3b82f6', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Aktivität pro Stunde",
            xaxis_title="Zeit",
            yaxis_title="Anzahl Events",
            height=300,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Noch keine Aktivitätsdaten vorhanden")
    
    # Kategorie-Verteilung
    st.markdown("### 📊 Event-Kategorien")
    
    if recent_entries:
        category_counts = Counter(entry.category for entry in recent_entries)
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(category_counts.keys()),
                values=list(category_counts.values()),
                hole=0.4
            )
        ])
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Noch keine Event-Daten vorhanden")


def _render_logs_tab(logger: ThemeLogger) -> None:
    """Rendert Logs-Tab"""
    st.markdown("### 📝 Log-Einträge")
    
    # Filter-Optionen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.selectbox(
            "Kategorie",
            ["Alle"] + [
                logger.CATEGORY_THEME_SWITCH,
                logger.CATEGORY_CSS_INJECTION,
                logger.CATEGORY_COMPONENT_RENDER,
                logger.CATEGORY_PERFORMANCE,
                logger.CATEGORY_ERROR,
                logger.CATEGORY_CACHE
            ]
        )
    
    with col2:
        level_filter = st.selectbox(
            "Level",
            ["Alle", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
    
    with col3:
        count = st.number_input(
            "Anzahl",
            min_value=10,
            max_value=500,
            value=50,
            step=10
        )
    
    # Hole gefilterte Logs
    category = None if category_filter == "Alle" else category_filter
    level = None if level_filter == "Alle" else level_filter
    
    entries = logger.get_recent_entries(
        count=int(count),
        category=category,
        level=level
    )
    
    # Zeige Logs
    if entries:
        st.markdown(f"**{len(entries)} Einträge gefunden**")
        
        for entry in reversed(entries):  # Neueste zuerst
            # Farbe basierend auf Level
            if entry.level == "ERROR" or entry.level == "CRITICAL":
                color = "#ef4444"
                icon = "🔴"
            elif entry.level == "WARNING":
                color = "#f59e0b"
                icon = "🟡"
            elif entry.level == "INFO":
                color = "#3b82f6"
                icon = "🔵"
            else:
                color = "#6b7280"
                icon = "⚪"
            
            # Expandable Log-Eintrag
            with st.expander(
                f"{icon} {entry.timestamp.strftime('%H:%M:%S')} - {entry.message}",
                expanded=False
            ):
                st.markdown(f"**Level:** {entry.level}")
                st.markdown(f"**Kategorie:** {entry.category}")
                st.markdown(f"**Zeit:** {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if entry.user_id:
                    st.markdown(f"**User ID:** {entry.user_id}")
                
                if entry.metadata:
                    st.markdown("**Metadaten:**")
                    st.json(entry.metadata)
    else:
        st.info("Keine Log-Einträge gefunden")
    
    # Export-Button
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Als JSON exportieren", use_container_width=True):
            filepath = logger.export_logs(format="json")
            st.success(f"Logs exportiert nach: {filepath}")
    
    with col2:
        if st.button("📥 Als CSV exportieren", use_container_width=True):
            filepath = logger.export_logs(format="csv")
            st.success(f"Logs exportiert nach: {filepath}")


def _render_performance_tab(logger: ThemeLogger) -> None:
    """Rendert Performance-Tab"""
    st.markdown("### ⚡ Performance-Metriken")
    
    # Hole Performance-Einträge
    perf_entries = logger.get_recent_entries(
        count=200,
        category=logger.CATEGORY_PERFORMANCE
    )
    
    if not perf_entries:
        st.info("Noch keine Performance-Daten vorhanden")
        return
    
    # CSS-Generierungs-Performance
    st.markdown("#### CSS-Generierung")
    
    css_gen_entries = [
        e for e in perf_entries
        if 'CSS generated' in e.message
    ]
    
    if css_gen_entries:
        durations = [
            e.metadata.get('duration_ms', 0)
            for e in css_gen_entries
        ]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Durchschnitt", f"{sum(durations) / len(durations):.2f}ms")
        
        with col2:
            st.metric("Minimum", f"{min(durations):.2f}ms")
        
        with col3:
            st.metric("Maximum", f"{max(durations):.2f}ms")
        
        # Zeitverlauf
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=durations,
            mode='lines+markers',
            name='CSS-Generierung',
            line=dict(color='#3b82f6', width=2)
        ))
        
        fig.add_hline(
            y=100,
            line_dash="dash",
            line_color="red",
            annotation_text="Ziel: 100ms"
        )
        
        fig.update_layout(
            title="CSS-Generierungs-Performance",
            xaxis_title="Messung",
            yaxis_title="Dauer (ms)",
            height=300,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Komponenten-Rendering-Performance
    st.markdown("#### Komponenten-Rendering")
    
    component_entries = logger.get_recent_entries(
        count=200,
        category=logger.CATEGORY_COMPONENT_RENDER
    )
    
    if component_entries:
        # Gruppiere nach Komponente
        component_durations: Dict[str, List[float]] = {}
        
        for entry in component_entries:
            comp_name = entry.metadata.get('component_name', 'Unknown')
            duration = entry.metadata.get('duration_ms', 0)
            
            if comp_name not in component_durations:
                component_durations[comp_name] = []
            component_durations[comp_name].append(duration)
        
        # Berechne Durchschnitte
        avg_durations = {
            comp: sum(durs) / len(durs)
            for comp, durs in component_durations.items()
        }
        
        # Sortiere nach Dauer
        sorted_components = sorted(
            avg_durations.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Zeige Top 10
        if sorted_components:
            components = [c[0] for c in sorted_components[:10]]
            durations = [c[1] for c in sorted_components[:10]]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=durations,
                    y=components,
                    orientation='h',
                    marker=dict(color='#34d399')
                )
            ])
            
            fig.update_layout(
                title="Durchschnittliche Rendering-Zeit pro Komponente",
                xaxis_title="Dauer (ms)",
                yaxis_title="Komponente",
                height=400,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)


def _render_settings_tab(logger: ThemeLogger) -> None:
    """Rendert Einstellungen-Tab"""
    st.markdown("### ⚙️ Logger-Einstellungen")
    
    # Log-Level
    current_level = logger.log_level
    
    new_level = st.selectbox(
        "Log-Level",
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        index=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"].index(current_level)
    )
    
    if new_level != current_level:
        if st.button("Log-Level ändern"):
            logger.set_log_level(new_level)
            st.success(f"Log-Level auf {new_level} gesetzt")
            st.rerun()
    
    st.markdown("---")
    
    # Aktionen
    st.markdown("### 🔧 Aktionen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Logs löschen", use_container_width=True):
            logger.clear_logs()
            st.success("Logs gelöscht")
            st.rerun()
    
    with col2:
        if st.button("🔄 Dashboard aktualisieren", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # System-Info
    st.markdown("### ℹ️ System-Info")
    
    stats = logger.get_stats()
    
    st.markdown(f"""
    - **Log-Verzeichnis:** `{logger.log_dir}`
    - **Gesamt-Einträge:** {stats['total_entries']}
    - **Log-Level:** {logger.log_level}
    - **Handler:** File + Console
    """)


def render_compact_monitoring(
    logger: Optional[ThemeLogger] = None
) -> None:
    """
    Rendert kompakte Monitoring-Ansicht für Sidebar
    
    Args:
        logger: ThemeLogger-Instanz (optional)
    """
    if logger is None:
        logger = get_theme_logger()
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 System Status")
        
        stats = logger.get_stats()
        
        # Kompakte Metriken
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Themes", stats['theme_switches'], label_visibility="visible")
            st.metric("Fehler", stats['errors'], label_visibility="visible")
        
        with col2:
            st.metric("CSS", stats['css_injections'], label_visibility="visible")
            st.metric("Cache", stats['cache_hit_rate'], label_visibility="visible")
        
        # Link zum vollständigen Dashboard
        if st.button("🔍 Vollständiges Dashboard", use_container_width=True):
            st.session_state['show_monitoring_dashboard'] = True


# Beispiel-Verwendung
if __name__ == "__main__":
    st.set_page_config(page_title="Theme Monitoring", layout="wide")
    
    # Initialisiere Logger
    logger = get_theme_logger(log_level="DEBUG")
    
    # Füge Test-Daten hinzu
    logger.log_theme_switch("shadcn-default", "shadcn-dark", "user123", 45.2)
    logger.log_css_generation("shadcn-dark", 78.5, 45000)
    logger.log_css_injection("shadcn-dark", True, 12.3)
    logger.log_component_render("Card", 23.4, True, user_id="user123")
    logger.log_performance_metric("css_size", 45.2, "KB", "shadcn-dark")
    logger.log_cache_event("theme_cache", "shadcn-dark", True)
    
    # Rendere Dashboard
    render_monitoring_dashboard(logger)
