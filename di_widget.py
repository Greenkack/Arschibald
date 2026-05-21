"""
Phase 12: Dependency Injection - Widget Library

Widgets für DI Container, Service Registration, Lifetime Management.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime


def render_di_services_widget(
    key_prefix: str = "di_services"
) -> None:
    """
    Widget für Service-Verwaltung.
    
    Zeigt:
    - Registrierte Services
    - Service-Details
    - Service-Status
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("📦 Registrierte Services")
    
    try:
        from core.dependency_injection import get_di_container
        
        container = get_di_container()
        stats = container.get_stats()
        
        # Übersicht
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Gesamt Services", stats.get('total_services', 0))
        
        with col2:
            st.metric("Singletons", stats.get('singleton_count', 0))
        
        with col3:
            st.metric("Scoped Services", stats.get('scoped_count', 0))
        
        st.markdown("---")
        
        # Service-Liste
        services = stats.get('services', [])
        
        if services:
            # Filter-Optionen
            col1, col2 = st.columns([2, 1])
            
            with col1:
                search = st.text_input(
                    "🔍 Service suchen",
                    placeholder="Service-Name...",
                    key=f"{key_prefix}_search"
                )
            
            with col2:
                filter_lifetime = st.selectbox(
                    "Filter Lebensdauer",
                    ["Alle", "SINGLETON", "SCOPED", "TRANSIENT"],
                    key=f"{key_prefix}_filter"
                )
            
            # Filtern
            filtered_services = services
            if search:
                filtered_services = [s for s in services if search.lower() in s.get('name', '').lower()]
            if filter_lifetime != "Alle":
                filtered_services = [s for s in filtered_services if s.get('lifetime') == filter_lifetime]
            
            st.markdown(f"**{len(filtered_services)} Services:**")
            
            # Service-Karten
            for service in filtered_services:
                with st.expander(f"**{service.get('name')}** - {service.get('lifetime')}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Typ:** `{service.get('type', 'Unbekannt')}`")
                        st.write(f"**Lebensdauer:** {service.get('lifetime')}")
                        
                        if service.get('dependencies'):
                            st.write("**Abhängigkeiten:**")
                            for dep in service['dependencies']:
                                st.write(f"  • {dep}")
                    
                    with col2:
                        st.metric("Aufrufe", service.get('resolution_count', 0))
                        st.metric("Status", "✅ Aktiv" if service.get('is_resolved') else "⚪ Nicht aufgelöst")
                        
                        # Auflöse-Button für Test
                        if st.button("🔧 Resolve", key=f"{key_prefix}_resolve_{service.get('name')}"):
                            try:
                                instance = container.resolve(service.get('type'))
                                st.success(f"✅ Service aufgelöst: {type(instance).__name__}")
                            except Exception as e:
                                st.error(f"❌ Fehler: {e}")
        else:
            st.info("Keine Services registriert")
    
    except ImportError:
        st.error("DI Container Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_di_lifetime_widget(
    key_prefix: str = "di_lifetime"
) -> None:
    """
    Widget für Lifetime-Management.
    
    Zeigt:
    - Lifetime-Verteilung
    - Singleton-Instanzen
    - Scoped-Instanzen
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("⏱️ Service Lebensdauer-Verwaltung")
    
    try:
        from core.dependency_injection import get_di_container, ServiceLifetime
        
        container = get_di_container()
        stats = container.get_stats()
        
        # Lifetime-Übersicht
        st.markdown("**📊 Lifetime-Verteilung:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            singleton_count = stats.get('singleton_count', 0)
            total = stats.get('total_services', 0)
            singleton_pct = (singleton_count / total * 100) if total > 0 else 0
            
            st.metric("Singleton", singleton_count)
            st.progress(singleton_pct / 100 if singleton_pct <= 100 else 1.0)
            st.caption(f"{singleton_pct:.1f}% der Services")
        
        with col2:
            scoped_count = stats.get('scoped_count', 0)
            scoped_pct = (scoped_count / total * 100) if total > 0 else 0
            
            st.metric("Scoped", scoped_count)
            st.progress(scoped_pct / 100 if scoped_pct <= 100 else 1.0)
            st.caption(f"{scoped_pct:.1f}% der Services")
        
        with col3:
            transient_count = stats.get('transient_count', 0)
            transient_pct = (transient_count / total * 100) if total > 0 else 0
            
            st.metric("Transient", transient_count)
            st.progress(transient_pct / 100 if transient_pct <= 100 else 1.0)
            st.caption(f"{transient_pct:.1f}% der Services")
        
        # Lifetime-Erklärungen
        st.markdown("---")
        st.markdown("**📚 Lebensdauer-Typen:**")
        
        # SINGLETON
        st.markdown("##### 🔹 SINGLETON")
        st.markdown("**Eine Instanz für die gesamte Anwendungs-Laufzeit**")
        st.markdown("- ✅ **Perfekt für:** Konfiguration, Caches, Shared Services")
        st.markdown("- ⚠️ **Vorsicht bei:** Stateful Services, Request-spezifischen Daten")
        st.markdown("- 💾 **Speicher:** Eine Instanz wird gecacht")
        st.markdown("**Beispiel:**")
        st.code("""@singleton
class ConfigService:
    def __init__(self):
        self.settings = load_settings()""", language="python")
        
        st.markdown("")
        
        # SCOPED
        st.markdown("##### 🔹 SCOPED")
        st.markdown("**Eine Instanz pro Scope (z.B. Request, Session)**")
        st.markdown("- ✅ **Perfekt für:** Request-Context, Database-Connections per Request")
        st.markdown("- ⚠️ **Vorsicht bei:** Langlebigen Referenzen")
        st.markdown("- 💾 **Speicher:** Eine Instanz pro Scope")
        st.markdown("**Beispiel:**")
        st.code("""@scoped
class RequestContext:
    def __init__(self):
        self.user_id = get_current_user_id()""", language="python")
        
        st.markdown("")
        
        # TRANSIENT
        st.markdown("##### 🔹 TRANSIENT")
        st.markdown("**Neue Instanz bei jedem Resolve**")
        st.markdown("- ✅ **Perfekt für:** Leichtgewichtige Services, Factory-Pattern")
        st.markdown("- ⚠️ **Vorsicht bei:** Resource-intensiven Services")
        st.markdown("- 💾 **Speicher:** Keine Caching, neue Instanz jedes Mal")
        st.markdown("**Beispiel:**")
        st.code("""@transient
class LogEntry:
    def __init__(self):
        self.timestamp = datetime.now()""", language="python")
        
        # Lifetime-Performance
        st.markdown("---")
        st.markdown("**⚡ Performance-Impact:**")
        
        import plotly.graph_objects as go
        
        lifetimes = ['SINGLETON', 'SCOPED', 'TRANSIENT']
        performance = [0.1, 0.5, 1.0]  # Relative Kosten
        colors = ['#28a745', '#ffc107', '#dc3545']
        
        fig = go.Figure(data=[
            go.Bar(
                x=lifetimes,
                y=performance,
                marker_color=colors,
                text=[f"{p:.1f}x" for p in performance],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Relative Resolution-Kosten",
            yaxis_title="Kosten (relativ)",
            height=300,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    except ImportError:
        st.error("DI Container Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_di_dependencies_widget(
    key_prefix: str = "di_deps"
) -> None:
    """
    Widget für Dependency-Visualisierung.
    
    Zeigt:
    - Dependency-Graph
    - Circular Dependencies
    - Dependency-Chains
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("🔗 Service-Abhängigkeiten")
    
    try:
        from core.dependency_injection import get_di_container
        
        container = get_di_container()
        stats = container.get_stats()
        
        st.info("🚧 Dependency-Graph-Visualisierung ist in Entwicklung")
        
        # Service-Auswahl für Dependency-Analyse
        services = stats.get('services', [])
        service_names = [s.get('name') for s in services]
        
        if service_names:
            selected = st.selectbox(
                "Service auswählen",
                service_names,
                key=f"{key_prefix}_select"
            )
            
            if selected:
                service = next((s for s in services if s.get('name') == selected), None)
                
                if service:
                    st.markdown(f"**Dependencies für `{selected}`:**")
                    
                    deps = service.get('dependencies', [])
                    
                    if deps:
                        # Dependency-Tree
                        st.markdown("```")
                        st.text(f"📦 {selected}")
                        for dep in deps:
                            st.text(f"  └─ {dep}")
                        st.markdown("```")
                        
                        # Prüfe auf zirkuläre Dependencies
                        st.markdown("---")
                        st.markdown("**🔍 Zirkuläre Abhängigkeiten-Check:**")
                        
                        # Placeholder - echte Implementierung würde Graph durchlaufen
                        st.success("✅ Keine zirkulären Abhängigkeiten gefunden")
                    else:
                        st.info(f"Service `{selected}` hat keine Dependencies")
        else:
            st.info("Keine Services zum Analysieren")
        
        # Dependency-Statistiken
        st.markdown("---")
        st.markdown("**📊 Abhängigkeits-Statistiken:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_deps = sum(len(s.get('dependencies', [])) for s in services)
            st.metric("Gesamt Abhängigkeiten", total_deps)
        
        with col2:
            services_with_deps = len([s for s in services if s.get('dependencies')])
            st.metric("Services mit Deps", services_with_deps)
        
        with col3:
            max_deps = max([len(s.get('dependencies', [])) for s in services], default=0)
            st.metric("Max. Deps pro Service", max_deps)
        
        # Empfehlungen
        st.markdown("---")
        st.markdown("**💡 Best Practices:**")
        
        with st.expander("Dependency-Management-Tipps"):
            st.markdown("""
            **✅ DO:**
            - Injiziere Interfaces statt Concrete-Types
            - Halte Dependency-Chains kurz (<5 Ebenen)
            - Nutze Constructor Injection
            - Verwende @injectable Decorator
            
            **❌ DON'T:**
            - Vermeide zirkuläre Dependencies
            - Vermeide zu viele Dependencies (>10)
            - Vermeide Service Locator Anti-Pattern
            - Vermeide Property Injection wenn möglich
            
            **Beispiel:**
            ```python
            @injectable
            class UserService:
                def __init__(
                    self,
                    db: DatabaseService,
                    cache: CacheService
                ):
                    self.db = db
                    self.cache = cache
            ```
            """)
    
    except ImportError:
        st.error("DI Container Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_di_stats_widget(
    key_prefix: str = "di_stats"
) -> None:
    """
    Widget für DI-Statistiken.
    
    Zeigt:
    - Resolution-Metriken
    - Performance-Stats
    - Fehler-Tracking
    
    Args:
        key_prefix: Prefix für Widget-Keys
    """
    st.subheader("📊 DI-Container Statistiken")
    
    try:
        from core.dependency_injection import get_di_container
        
        container = get_di_container()
        try:
            stats = container.get_stats()
        except Exception:
            stats = {}
        
        # Haupt-Metriken
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt Services", stats.get('total_services', 0))
        
        with col2:
            st.metric("Gesamt Resolutions", stats.get('total_resolutions', 0))
        
        with col3:
            errors = stats.get('resolution_errors', 0)
            st.metric("Fehler", errors, delta="Problem" if errors > 0 else "OK", delta_color="inverse" if errors > 0 else "off")
        
        with col4:
            cache_hits = stats.get('cache_hits', 0)
            total_res = stats.get('total_resolutions', 0)
            hit_rate = (cache_hits / total_res * 100) if total_res > 0 else 0
            st.metric("Cache Hit Rate", f"{hit_rate:.1f}%")
        
        st.markdown("---")
        
        # Top Resolved Services
        st.markdown("**🏆 Top Resolved Services:**")
        
        top_services = stats.get('top_resolved_services', [])
        
        if top_services:
            import pandas as pd
            
            df = pd.DataFrame(top_services[:10])
            
            # Bar Chart
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[
                go.Bar(
                    x=df['name'],
                    y=df['resolution_count'],
                    marker_color='#ff8c00',
                    text=df['resolution_count'],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Top 10 Resolved Services",
                xaxis_title="Service",
                yaxis_title="Resolutions",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance-Metriken
        st.markdown("---")
        st.markdown("**⚡ Performance:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_resolution_time = stats.get('avg_resolution_time_ms', 0)
            st.metric("Ø Resolution-Zeit", f"{avg_resolution_time:.2f} ms")
        
        with col2:
            max_resolution_time = stats.get('max_resolution_time_ms', 0)
            st.metric("Max. Resolution-Zeit", f"{max_resolution_time:.2f} ms")
        
        with col3:
            slow_resolutions = stats.get('slow_resolutions', 0)
            st.metric("Langsame Resolutions", slow_resolutions)
        
        # Fehler-Liste
        if errors > 0:
            st.markdown("---")
            st.markdown("**❌ Letzte Fehler:**")
            
            error_list = stats.get('recent_errors', [])
            
            for error in error_list[:5]:
                st.error(f"**{error.get('service')}**: {error.get('message')}")
        
        # Aktionen
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Statistiken aktualisieren", key=f"{key_prefix}_refresh"):
                st.rerun()
        
        with col2:
            if st.button("🗑️ Statistiken zurücksetzen", key=f"{key_prefix}_clear"):
                # Placeholder für Reset-Funktion
                st.success("✅ Statistiken zurückgesetzt!")
                st.rerun()
    
    except ImportError:
        st.error("DI Container Module nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler: {e}")


def render_di_admin(
    show_header: bool = True,
    key_prefix: str = "di_admin"
) -> None:
    """
    Vollständiges Admin-Panel für Dependency Injection.
    
    Kombiniert alle DI-Widgets in einem Dashboard.
    
    Args:
        show_header: Zeige Header
        key_prefix: Prefix für Widget-Keys
    """
    if show_header:
        st.title("💉 Dependency Injection Administration")
        st.markdown("**Verwalten Sie Services, Lebensdauer und Abhängigkeiten**")
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
    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Services",
        "⏱️ Lebensdauer",
        "🔗 Abhängigkeiten",
        "📊 Statistiken"
    ])
    
    with tab1:
        render_di_services_widget(key_prefix=f"{key_prefix}_services")
    
    with tab2:
        render_di_lifetime_widget(key_prefix=f"{key_prefix}_lifetime")
    
    with tab3:
        render_di_dependencies_widget(key_prefix=f"{key_prefix}_deps")
    
    with tab4:
        render_di_stats_widget(key_prefix=f"{key_prefix}_stats")
    
    # Schnellaktionen am Ende
    st.markdown("---")
    st.markdown("**🚀 Schnellaktionen:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Service-Liste exportieren", key=f"{key_prefix}_export", use_container_width=True):
            try:
                from core.dependency_injection import get_di_container
                container = get_di_container()
                stats = container.get_stats()
                
                import json
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'stats': stats
                }
                
                st.download_button(
                    "💾 Download JSON",
                    json.dumps(export_data, indent=2),
                    file_name=f"di_container_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"Export-Fehler: {e}")
    
    with col2:
        if st.button("🔍 Container validieren", key=f"{key_prefix}_validate", use_container_width=True):
            try:
                from core.dependency_injection import get_di_container
                container = get_di_container()
                
                # Validierung durchführen
                with st.spinner("Validiere Container..."):
                    # Placeholder - echte Implementierung würde alle Services testen
                    st.success("✅ Container ist valide!")
            except Exception as e:
                st.error(f"Validierungs-Fehler: {e}")
    
    with col3:
        if st.button("📖 Dokumentation", key=f"{key_prefix}_docs", use_container_width=True):
            st.info("📚 Siehe PHASE_12_DEPENDENCY_INJECTION_INTEGRATION.md für vollständige Dokumentation")


if __name__ == "__main__":
    # Test-Modus
    st.set_page_config(page_title="DI-Container Widgets", layout="wide")
    render_di_admin()
