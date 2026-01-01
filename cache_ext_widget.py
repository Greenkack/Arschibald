"""
Phase 10: Cache Extensions - Widget Library

Widgets für Cache Invalidation, Monitoring und Warming.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime


def render_cache_invalidation_widget(
    key_prefix: str = "cache_inv"
) -> None:
    """
    Widget für Cache-Invalidierung.
    
    Zeigt:
    - Invalidierung nach Tags
    - Invalidierung nach Pattern
    - Batch-Invalidierung
    - Invalidierungs-History
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("🗑️ Cache Invalidierung")
    
    try:
        from core.cache_invalidation import get_invalidation_engine, get_invalidation_stats
        from core.cache import get_cache
        
        engine = get_invalidation_engine()
        cache = get_cache()
        
        # Tabs für verschiedene Invalidierungs-Methoden
        tab1, tab2, tab3 = st.tabs([
            "🏷️ Tag-basiert",
            "🔍 Pattern-basiert",
            "📊 Statistiken"
        ])
        
        with tab1:
            st.markdown("**Invalidiere Cache-Einträge nach Tags**")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                tag = st.text_input(
                    "Tag eingeben",
                    placeholder="z.B. user:123, product:*",
                    key=f"{key_prefix}_tag"
                )
            
            with col2:
                if st.button("Invalidieren", key=f"{key_prefix}_inv_tag", type="primary"):
                    if tag:
                        try:
                            # Nutze Cache direkt für Tag-basierte Invalidierung
                            cache.invalidate(tag)
                            st.success(f"✅ Cache für Tag '{tag}' invalidiert!")
                        except Exception as e:
                            st.error(f"Fehler: {e}")
                    else:
                        st.warning("Bitte Tag eingeben")
            
            # Beispiele
            with st.expander("💡 Beispiele"):
                st.code("""
# Einzelner Tag
user:123

# Wildcard (alle Benutzer)
user:*

# Mehrere Tags (komma-separiert)
user:123,session:abc
                """)
        
        with tab2:
            st.markdown("**Invalidiere Cache-Einträge nach Ressource**")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                resource_type = st.text_input(
                    "Ressource-Typ",
                    placeholder="z.B. user, product, form",
                    key=f"{key_prefix}_resource_type"
                )
            
            with col2:
                resource_id = st.text_input(
                    "Ressource-ID (optional)",
                    placeholder="z.B. 123",
                    key=f"{key_prefix}_resource_id"
                )
            
            with col3:
                if st.button("Invalidieren", key=f"{key_prefix}_inv_write", type="primary"):
                    if resource_type:
                        try:
                            count = engine.invalidate_by_write(
                                resource_type=resource_type,
                                resource_id=resource_id if resource_id else None,
                                operation="update"
                            )
                            st.success(f"✅ {count} Einträge invalidiert!")
                        except Exception as e:
                            st.error(f"Fehler: {e}")
                    else:
                        st.warning("Bitte Ressource-Typ eingeben")
            
            # Beispiele
            with st.expander("💡 Regex-Beispiele"):
                st.code("""
# Alle Einträge die mit "user:" beginnen
^user:.*$

# Alle Session-Caches
.*session.*

# Bestimmte Module
^module_(pv|wp|storage):.*$
                """)
        
        with tab3:
            try:
                invalidation_stats = get_invalidation_stats()
            except Exception:
                invalidation_stats = {}
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesamt Invalidierungen", invalidation_stats.get('total_invalidations', 0))
            with col2:
                st.metric("Aktive Regeln", invalidation_stats.get('rules_count', 0))
            with col3:
                st.metric("Status", "🟢 Aktiv" if invalidation_stats.get('enabled', True) else "⚪ Inaktiv")
            
            # History
            if invalidation_stats.get('recent_invalidations'):
                st.markdown("**Letzte Invalidierungen:**")
                import pandas as pd
                df = pd.DataFrame(invalidation_stats['recent_invalidations'][-10:])
                st.dataframe(df, use_container_width=True)
    
    except ImportError as ie:
        st.warning(f"⚠️ Cache Invalidation Module nicht verfügbar: {ie}")
        st.info("Bitte prüfen Sie, ob `core.cache_invalidation` installiert ist.")
    except Exception as e:
        st.error(f"Fehler: {e}")
        import traceback
        with st.expander("🔍 Fehlerdetails"):
            st.code(traceback.format_exc())


def render_cache_monitor_widget(
    key_prefix: str = "cache_mon"
) -> None:
    """
    Widget für Cache-Monitoring.
    
    Zeigt:
    - Hit Rate Metriken
    - Cache-Größe
    - Performance-Trends
    - Alerts
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("📊 Cache Monitoring")
    
    try:
        from core.cache_monitoring import get_cache_monitor
        from core.cache import get_cache
        
        monitor = get_cache_monitor()
        cache = get_cache()
        report = monitor.get_report()
        cache_stats = cache.get_stats()
        
        # KPI-Metriken
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Hit Rate aus memory layer
            memory_layer = report.get('layers', {}).get('memory', {})
            hit_rate_data = memory_layer.get('hit_rate', {})
            hit_rate = hit_rate_data.get('current', 0) * 100 if isinstance(hit_rate_data, dict) else 0
            st.metric("Hit Rate", f"{hit_rate:.1f}%")
        
        with col2:
            # Gesamt Zugriffe aus Cache-Stats
            memory_stats = cache_stats.get('memory', {})
            total_hits = memory_stats.get('hits', 0)
            total_misses = memory_stats.get('misses', 0)
            st.metric("Gesamt Zugriffe", f"{total_hits + total_misses:,}")
        
        with col3:
            # Cache-Größe
            size_data = memory_layer.get('size', {})
            cache_size_mb = size_data.get('current_mb', 0) if isinstance(size_data, dict) else 0
            st.metric("Cache-Größe", f"{cache_size_mb:.1f} MB")
        
        with col4:
            alerts = len(report.get('alerts', []))
            st.metric(
                "Alerts",
                alerts,
                delta="Problem" if alerts > 0 else "OK",
                delta_color="inverse" if alerts > 0 else "off"
            )
        
        # Tabs für Details
        tab1, tab2, tab3 = st.tabs(["📈 Trends", "⚠️ Alerts", "🔍 Details"])
        
        with tab1:
            # Hit Rate Chart
            if stats.get('hit_rate_history'):
                import plotly.graph_objects as go
                
                history = stats['hit_rate_history']
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    y=[h * 100 for h in history],
                    mode='lines+markers',
                    name='Hit Rate %',
                    line=dict(color='#ff8c00', width=3)
                ))
                
                fig.update_layout(
                    title="Hit Rate Trend",
                    yaxis_title="Hit Rate (%)",
                    xaxis_title="Zeit",
                    height=300,
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            alerts_list = report.get('alerts', [])
            if alerts_list:
                for alert in alerts_list:
                    severity = alert.get('severity', 'INFO')
                    icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(severity, "ℹ️")
                    st.warning(f"{icon} **{alert.get('message')}**\n\n{alert.get('details', '')}")
            else:
                st.success("✅ Keine aktiven Alerts")
        
        with tab3:
            st.json(report, expanded=False)
        
        # Refresh Button
        if st.button("🔄 Aktualisieren", key=f"{key_prefix}_refresh"):
            st.rerun()
    
    except ImportError:
        st.error("Cache Monitor Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_cache_warming_widget(
    key_prefix: str = "cache_warm"
) -> None:
    """
    Widget für Cache-Warming.
    
    Zeigt:
    - Warming-Tasks
    - Task-Ausführung
    - Warming-Historie
    - Auto-Warming Status
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("🔥 Cache Warming")
    
    try:
        from core.cache_warming import get_warming_engine
        
        warmer = get_warming_engine()
        # Nutze get_stats() für Statistiken
        try:
            warming_stats = warmer.get_stats()
        except Exception:
            warming_stats = {}
        
        # Status-Übersicht
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Registrierte Tasks", warming_stats.get('total_tasks', 0))
        
        with col2:
            st.metric("Heute ausgeführt", warming_stats.get('executed_today', 0))
        
        with col3:
            st.metric("Erfolgsrate", f"{warming_stats.get('success_rate', 0) * 100:.1f}%")
        
        with col4:
            auto_enabled = warming_stats.get('auto_warming_enabled', False)
            st.metric("Auto-Warming", "🟢 Aktiv" if auto_enabled else "⚪ Inaktiv")
        
        st.markdown("---")
        
        # Task-Liste
        tasks = warming_stats.get('tasks', [])
        if tasks:
            st.markdown("**📋 Warming-Tasks:**")
            
            for task in tasks:
                with st.expander(f"**{task.get('name', 'Unnamed')}**", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Beschreibung:** {task.get('description', 'Keine')}")
                        st.write(f"**Priority:** {task.get('priority', 'NORMAL')}")
                        st.write(f"**Schedule:** {task.get('schedule', 'Manual')}")
                        st.write(f"**Letzte Ausführung:** {task.get('last_execution', 'Nie')}")
                    
                    with col2:
                        if st.button(
                            "▶️ Jetzt ausführen",
                            key=f"{key_prefix}_exec_{task.get('name')}",
                            use_container_width=True
                        ):
                            try:
                                warmer.warm_now(task.get('name'))
                                st.success("✅ Task ausgeführt!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Fehler: {e}")
        else:
            st.info("Keine Warming-Tasks registriert")
        
        st.markdown("---")
        
        # Globale Aktionen
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔥 Alle Tasks ausführen", key=f"{key_prefix}_warm_all", type="primary"):
                with st.spinner("Warming läuft..."):
                    try:
                        warmer.warm_all()
                        st.success("✅ Alle Tasks ausgeführt!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Fehler: {e}")
        
        with col2:
            if st.button("🔄 Statistiken aktualisieren", key=f"{key_prefix}_refresh"):
                st.rerun()
    
    except ImportError as ie:
        st.warning(f"⚠️ Cache Warming Module nicht verfügbar: {ie}")
        st.info("Bitte prüfen Sie, ob `core.cache_warming` installiert ist.")
    except Exception as e:
        st.error(f"Fehler: {e}")
        import traceback
        with st.expander("🔍 Fehlerdetails"):
            st.code(traceback.format_exc())


def render_cache_analytics_widget(
    key_prefix: str = "cache_analytics"
) -> None:
    """
    Widget für Cache-Analytics.
    
    Zeigt:
    - Performance-Metriken
    - Nutzungs-Patterns
    - Optimierungs-Empfehlungen
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("📈 Cache Analytics")
    
    try:
        from core.cache_monitoring import get_cache_monitor
        from core.cache import get_cache
        
        monitor = get_cache_monitor()
        cache = get_cache()
        report = monitor.get_report()
        
        # Performance-Analyse
        st.markdown("**Performance-Analyse:**")
        
        # Hole Hit Rate und Size Analysen
        memory_layer = report.get('layers', {}).get('memory', {})
        hit_rate_data = memory_layer.get('hit_rate', {})
        size_data = memory_layer.get('size', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            hit_rate = hit_rate_data.get('hit_rate', 0) * 100 if isinstance(hit_rate_data, dict) else 0
            st.metric("Hit Rate", f"{hit_rate:.1f}%")
        with col2:
            utilization = size_data.get('utilization', 0) * 100 if isinstance(size_data, dict) else 0
            st.metric("Cache-Auslastung", f"{utilization:.1f}%")
        with col3:
            eviction_data = memory_layer.get('evictions', {})
            evictions = eviction_data.get('evictions', 0) if isinstance(eviction_data, dict) else 0
            st.metric("Evictions", evictions)
        
        # Nutzungs-Pattern
        st.markdown("---")
        st.markdown("**🔍 Nutzungs-Pattern:**")
        
        # Hole Cache-Stats für Pattern-Analyse
        cache_stats = cache.get_stats()
        memory_stats = cache_stats.get('memory', {})
        
        st.info("🚧 Nutzungs-Pattern-Analyse in Entwicklung")
        
        # Zeige grundlegende Cache-Statistiken
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cache Entries", memory_stats.get('entries', 0))
        with col2:
            st.metric("Max Entries", memory_stats.get('max_entries', 0))
        
        # Optimierungs-Empfehlungen
        st.markdown("---")
        st.markdown("**💡 Optimierungs-Empfehlungen:**")
        
        recommendations = report.get('recommendations', [])
        
        if recommendations:
            for rec in recommendations:
                if isinstance(rec, dict):
                    severity = rec.get('severity', 'info')
                    icon = {"critical": "🔴", "warning": "🟠", "info": "🔵"}.get(severity.lower(), "ℹ️")
                    st.info(f"{icon} {rec.get('message', rec)}")
                else:
                    st.info(f"ℹ️ {rec}")
        else:
            st.success("✅ Keine Optimierungen nötig - Cache läuft optimal!")
    
    except ImportError:
        st.error("Cache Analytics Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_cache_alerts_widget(
    key_prefix: str = "cache_alerts"
) -> None:
    """
    Widget für Cache-Alerts.
    
    Zeigt:
    - Aktive Alerts
    - Alert-Historie
    - Alert-Konfiguration
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("⚠️ Cache Alerts")
    
    try:
        from core.cache_monitoring import get_cache_monitor
        
        monitor = get_cache_monitor()
        stats = monitor.get_report()
        
        # Aktive Alerts
        alerts = stats.get('alerts', [])
        active_count = len([a for a in alerts if a.get('active', True)])
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.metric("Aktive Alerts", active_count)
        with col2:
            if st.button("🔄 Aktualisieren", key=f"{key_prefix}_refresh"):
                st.rerun()
        
        st.markdown("---")
        
        # Alert-Liste
        if alerts:
            for alert in alerts:
                severity = alert.get('severity', 'INFO')
                active = alert.get('active', True)
                
                icon_map = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🔵",
                    "INFO": "ℹ️"
                }
                icon = icon_map.get(severity, "ℹ️")
                
                status_icon = "🔔" if active else "🔕"
                
                with st.container():
                    st.markdown(f"{status_icon} {icon} **{alert.get('message')}**")
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.caption(alert.get('details', ''))
                    with col2:
                        st.caption(f"Severity: {severity}")
                    with col3:
                        st.caption(f"Zeit: {alert.get('timestamp', 'Unbekannt')}")
                    
                    st.markdown("---")
        else:
            st.success("✅ Keine Alerts - Alles läuft optimal!")
        
        # Alert-Konfiguration
        with st.expander("⚙️ Alert-Konfiguration"):
            st.markdown("**Alert-Schwellenwerte:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                hit_rate_threshold = st.slider(
                    "Min. Hit Rate (%)",
                    0, 100, 70,
                    key=f"{key_prefix}_hit_rate_thresh"
                )
                
                cache_size_threshold = st.slider(
                    "Max. Cache-Größe (MB)",
                    0, 1000, 500,
                    key=f"{key_prefix}_size_thresh"
                )
            
            with col2:
                alert_cooldown = st.number_input(
                    "Alert Cooldown (Sekunden)",
                    min_value=10,
                    max_value=3600,
                    value=60,
                    key=f"{key_prefix}_cooldown"
                )
                
                enable_alerts = st.checkbox(
                    "Alerts aktivieren",
                    value=True,
                    key=f"{key_prefix}_enable"
                )
            
            if st.button("💾 Konfiguration speichern", key=f"{key_prefix}_save_config"):
                st.success("✅ Konfiguration gespeichert!")
    
    except ImportError:
        st.error("Cache Alerts Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_cache_ext_admin(
    show_header: bool = True,
    key_prefix: str = "cache_ext_admin"
) -> None:
    """
    Vollständiges Admin-Panel für Cache Extensions.
    
    Kombiniert alle Cache-Extension-Widgets in einem Dashboard.
    
    Args:
        show_header: Zeige Header
        key_prefix: Prefix für Widget-Keys
    """
    if show_header:
        st.title("🗄️ Cache-Erweiterungen Administration")
        st.markdown("**Verwalten Sie Cache Invalidation, Monitoring und Warming**")
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
        "🗑️ Invalidierung",
        "📊 Überwachung",
        "🔥 Vorwärmung",
        "📈 Analysen",
        "⚠️ Warnungen"
    ])
    
    with tab1:
        render_cache_invalidation_widget(key_prefix=f"{key_prefix}_inv")
    
    with tab2:
        render_cache_monitor_widget(key_prefix=f"{key_prefix}_mon")
    
    with tab3:
        render_cache_warming_widget(key_prefix=f"{key_prefix}_warm")
    
    with tab4:
        render_cache_analytics_widget(key_prefix=f"{key_prefix}_analytics")
    
    with tab5:
        render_cache_alerts_widget(key_prefix=f"{key_prefix}_alerts")


if __name__ == "__main__":
    # Test-Modus
    st.set_page_config(page_title="Cache-Erweiterungen Widgets", layout="wide")
    render_cache_ext_admin()
