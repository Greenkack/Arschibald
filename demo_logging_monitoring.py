"""
Demo: Theme Logging & Monitoring System

Dieses Demo zeigt die Verwendung des Logging- und Monitoring-Systems.
"""

import streamlit as st
import time
from datetime import datetime

try:
    from theming.theme_logger import get_theme_logger
    from theming.monitoring_dashboard import render_monitoring_dashboard, render_compact_monitoring
except ImportError:
    st.error("Theme-System nicht gefunden. Bitte installieren Sie die erforderlichen Module.")
    st.stop()


def main():
    st.set_page_config(
        page_title="Logging & Monitoring Demo",
        page_icon="",
        layout="wide"
    )
    
    st.title(" Theme Logging & Monitoring System Demo")
    
    # Initialisiere Logger
    if 'logger' not in st.session_state:
        st.session_state.logger = get_theme_logger(log_level="DEBUG")
    
    logger = st.session_state.logger
    
    # Sidebar mit kompaktem Monitoring
    with st.sidebar:
        st.header(" Steuerung")
        
        # Log-Level
        log_level = st.selectbox(
            "Log-Level",
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            index=1
        )
        
        if st.button("Log-Level ändern"):
            logger.set_log_level(log_level)
            st.success(f"Log-Level auf {log_level} gesetzt")
        
        st.markdown("---")
        
        # Kompaktes Monitoring
        render_compact_monitoring(logger)
    
    # Hauptbereich mit Tabs
    tab1, tab2, tab3 = st.tabs([
        " Demo-Aktionen",
        " Monitoring Dashboard",
        " Dokumentation"
    ])
    
    with tab1:
        render_demo_actions(logger)
    
    with tab2:
        render_monitoring_dashboard(logger)
    
    with tab3:
        render_documentation()


def render_demo_actions(logger):
    """Rendert Demo-Aktionen"""
    st.header(" Demo-Aktionen")
    
    st.markdown("""
    Führe verschiedene Aktionen aus, um das Logging-System zu testen.
    Die Logs werden in Echtzeit im Monitoring-Dashboard angezeigt.
    """)
    
    # Theme-Wechsel simulieren
    st.subheader("1. Theme-Wechsel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        from_theme = st.selectbox(
            "Von Theme",
            ["shadcn-default", "shadcn-dark", "shadcn-ocean", "shadcn-forest", "shadcn-sunset"]
        )
    
    with col2:
        to_theme = st.selectbox(
            "Zu Theme",
            ["shadcn-dark", "shadcn-default", "shadcn-ocean", "shadcn-forest", "shadcn-sunset"]
        )
    
    if st.button(" Theme wechseln", use_container_width=True):
        start = time.perf_counter()
        time.sleep(0.045)  # Simuliere Theme-Wechsel
        duration_ms = (time.perf_counter() - start) * 1000
        
        logger.log_theme_switch(
            from_theme=from_theme,
            to_theme=to_theme,
            user_id=st.session_state.get('user_id', 'demo_user'),
            duration_ms=duration_ms
        )
        
        st.success(f"Theme gewechselt: {from_theme} → {to_theme} ({duration_ms:.2f}ms)")
    
    st.markdown("---")
    
    # CSS-Generierung simulieren
    st.subheader("2. CSS-Generierung")
    
    theme_name = st.selectbox(
        "Theme",
        ["shadcn-default", "shadcn-dark", "shadcn-ocean"],
        key="css_theme"
    )
    
    if st.button(" CSS generieren", use_container_width=True):
        start = time.perf_counter()
        time.sleep(0.078)  # Simuliere CSS-Generierung
        duration_ms = (time.perf_counter() - start) * 1000
        
        css_size = 45000  # Simulierte CSS-Größe
        
        logger.log_css_generation(
            theme_name=theme_name,
            duration_ms=duration_ms,
            css_size_bytes=css_size
        )
        
        logger.log_css_injection(
            theme_name=theme_name,
            success=True,
            duration_ms=12.3
        )
        
        st.success(f"CSS generiert: {duration_ms:.2f}ms ({css_size / 1024:.2f}KB)")
    
    st.markdown("---")
    
    # Komponenten-Rendering simulieren
    st.subheader("3. Komponenten-Rendering")
    
    component_name = st.selectbox(
        "Komponente",
        ["Card", "Alert", "Badge", "Table", "MetricCard", "Accordion"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Erfolgreich rendern", use_container_width=True):
            start = time.perf_counter()
            time.sleep(0.023)  # Simuliere Rendering
            duration_ms = (time.perf_counter() - start) * 1000
            
            logger.log_component_render(
                component_name=component_name,
                duration_ms=duration_ms,
                success=True,
                user_id=st.session_state.get('user_id', 'demo_user')
            )
            
            st.success(f"{component_name} gerendert: {duration_ms:.2f}ms")
    
    with col2:
        if st.button(" Fehler simulieren", use_container_width=True):
            start = time.perf_counter()
            time.sleep(0.015)
            duration_ms = (time.perf_counter() - start) * 1000
            
            logger.log_component_render(
                component_name=component_name,
                duration_ms=duration_ms,
                success=False,
                error="Simulated rendering error"
            )
            
            st.error(f"{component_name} Fehler: {duration_ms:.2f}ms")
    
    st.markdown("---")
    
    # Performance-Metriken
    st.subheader("4. Performance-Metriken")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_name = st.text_input("Metrik-Name", "custom_metric")
    
    with col2:
        metric_value = st.number_input("Wert", value=100.0)
    
    with col3:
        metric_unit = st.selectbox("Einheit", ["ms", "KB", "MB", "count"])
    
    if st.button(" Metrik loggen", use_container_width=True):
        logger.log_performance_metric(
            metric_name=metric_name,
            value=metric_value,
            unit=metric_unit,
            theme_name="shadcn-default"
        )
        
        st.success(f"Metrik geloggt: {metric_name} = {metric_value}{metric_unit}")
    
    st.markdown("---")
    
    # Cache-Ereignisse
    st.subheader("5. Cache-Ereignisse")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Cache Hit", use_container_width=True):
            logger.log_cache_event(
                event_type="theme_cache",
                cache_key="shadcn-dark",
                hit=True
            )
            st.success("Cache Hit geloggt")
    
    with col2:
        if st.button(" Cache Miss", use_container_width=True):
            logger.log_cache_event(
                event_type="theme_cache",
                cache_key="shadcn-custom",
                hit=False
            )
            st.warning("Cache Miss geloggt")
    
    st.markdown("---")
    
    # Fehler
    st.subheader("6. Fehler loggen")
    
    error_message = st.text_input(
        "Fehlermeldung",
        "Beispiel-Fehler: Theme konnte nicht geladen werden"
    )
    
    if st.button(" Fehler loggen", use_container_width=True):
        logger.log_error(
            error_message=error_message,
            category=logger.CATEGORY_ERROR,
            metadata={"timestamp": datetime.now().isoformat()}
        )
        st.error(f"Fehler geloggt: {error_message}")
    
    st.markdown("---")
    
    # Bulk-Aktionen
    st.subheader("7. Bulk-Aktionen")
    
    if st.button(" Viele Events generieren", use_container_width=True):
        with st.spinner("Generiere Events..."):
            # Theme-Wechsel
            for i in range(5):
                logger.log_theme_switch(
                    from_theme="shadcn-default",
                    to_theme=f"shadcn-theme-{i}",
                    duration_ms=45.0 + i * 5
                )
            
            # Komponenten
            components = ["Card", "Alert", "Badge", "Table", "MetricCard"]
            for comp in components:
                logger.log_component_render(
                    component_name=comp,
                    duration_ms=20.0 + len(comp),
                    success=True
                )
            
            # Cache-Events
            for i in range(10):
                logger.log_cache_event(
                    event_type="theme_cache",
                    cache_key=f"theme-{i}",
                    hit=i % 3 != 0  # 2/3 Hits, 1/3 Misses
                )
        
        st.success("20 Events generiert!")
    
    st.markdown("---")
    
    # Export
    st.subheader("8. Logs exportieren")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Als JSON exportieren", use_container_width=True):
            filepath = logger.export_logs(format="json")
            st.success(f"Exportiert nach: {filepath}")
    
    with col2:
        if st.button(" Als CSV exportieren", use_container_width=True):
            filepath = logger.export_logs(format="csv")
            st.success(f"Exportiert nach: {filepath}")
    
    # Logs löschen
    st.markdown("---")
    
    if st.button(" Alle Logs löschen", type="secondary", use_container_width=True):
        logger.clear_logs()
        st.warning("Alle Logs gelöscht!")
        st.rerun()


def render_documentation():
    """Rendert Dokumentation"""
    st.header(" Dokumentation")
    
    st.markdown("""
    ## Übersicht
    
    Das Theme Logging & Monitoring System bietet umfassendes Logging und Monitoring
    für das shadcn/ui Theme-System.
    
    ## Features
    
    -  **Theme-Wechsel-Logging** mit Timestamp und User-ID
    -  **CSS-Injection-Logging** mit Performance-Metriken
    -  **Komponenten-Rendering-Logging** mit Fehlerbehandlung
    -  **Performance-Metriken** für alle Operationen
    -  **Cache-Ereignisse** (Hits und Misses)
    -  **Fehler-Logging** mit Stack-Traces
    -  **Interaktives Monitoring-Dashboard**
    -  **Export** als JSON oder CSV
    -  **Konfigurierbares Log-Level**
    
    ## Schnellstart
    
    ```python
    from theming.theme_logger import get_theme_logger
    
    # Logger initialisieren
    logger = get_theme_logger()
    
    # Theme-Wechsel loggen
    logger.log_theme_switch("default", "dark", user_id="user123")
    
    # Statistiken abrufen
    stats = logger.get_stats()
    print(stats)
    ```
    
    ## Log-Kategorien
    
    - `CATEGORY_THEME_SWITCH`: Theme-Wechsel
    - `CATEGORY_CSS_INJECTION`: CSS-Injection
    - `CATEGORY_COMPONENT_RENDER`: Komponenten-Rendering
    - `CATEGORY_PERFORMANCE`: Performance-Metriken
    - `CATEGORY_ERROR`: Fehler
    - `CATEGORY_CACHE`: Cache-Ereignisse
    
    ## Log-Level
    
    - `DEBUG`: Detaillierte Informationen
    - `INFO`: Normale Operationen
    - `WARNING`: Warnungen
    - `ERROR`: Fehler
    - `CRITICAL`: Kritische Fehler
    
    ## Monitoring Dashboard
    
    Das Dashboard zeigt:
    
    -  **Übersicht**: Statistiken und Metriken
    -  **Logs**: Gefilterte Log-Einträge
    -  **Performance**: Performance-Analysen
    -  **Einstellungen**: Logger-Konfiguration
    
    ## Weitere Ressourcen
    
    - [Vollständige Referenz](theming/LOGGING_SYSTEM_REFERENCE.md)
    - [Quick Reference](docs/LOGGING_MONITORING_QUICK_REFERENCE.md)
    - [Error Handling Guide](docs/ERROR_HANDLING_QUICK_REFERENCE.md)
    """)


if __name__ == "__main__":
    main()
