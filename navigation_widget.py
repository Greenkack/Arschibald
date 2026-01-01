"""
Navigation History Widget for Streamlit Apps

Beispiel-Widget zur Integration von Phase 7 Navigation History
"""

import streamlit as st
from typing import Optional, Callable
from core_integration import get_navigation_history, is_feature_enabled
from core.navigation_history import render_breadcrumbs
from core.router import get_router


def render_navigation_widget(show_breadcrumbs: bool = True, show_back_forward: bool = True):
    """
    Rendere komplettes Navigation-Widget mit Breadcrumbs und Back/Forward
    
    Args:
        show_breadcrumbs: Zeige Breadcrumbs
        show_back_forward: Zeige Back/Forward Buttons
    """
    if not is_feature_enabled('navigation'):
        return
    
    nav_hist = get_navigation_history()
    if not nav_hist:
        return
    
    router = get_router()
    
    # Breadcrumbs
    if show_breadcrumbs:
        breadcrumbs = nav_hist.get_breadcrumbs(max_items=5, include_home=True)
        if breadcrumbs:
            def on_breadcrumb_click(page, params):
                router.navigate(page, params)
                st.rerun()
            
            render_breadcrumbs(breadcrumbs, on_click=on_breadcrumb_click)
            st.markdown("---")
    
    # Back/Forward Buttons
    if show_back_forward:
        col1, col2, col3 = st.columns([1, 1, 8])
        
        with col1:
            if nav_hist.can_go_back():
                if st.button("◄ Zurück", key="nav_widget_back", help="Zur vorherigen Seite"):
                    prev_entry = nav_hist.back()
                    if prev_entry:
                        router.navigate(prev_entry.page, prev_entry.params)
                        st.rerun()
            else:
                st.button("◄ Zurück", key="nav_widget_back_disabled", disabled=True)
        
        with col2:
            if nav_hist.can_go_forward():
                if st.button("Vorwärts ►", key="nav_widget_forward", help="Zur nächsten Seite"):
                    next_entry = nav_hist.forward()
                    if next_entry:
                        router.navigate(next_entry.page, next_entry.params)
                        st.rerun()
            else:
                st.button("Vorwärts ►", key="nav_widget_forward_disabled", disabled=True)


def render_navigation_sidebar(page_config: dict[str, dict]):
    """
    Rendere Navigation-Sidebar mit History-Support
    
    Args:
        page_config: Dictionary mit Page-Konfiguration
            {
                'home': {'title': 'Startseite', 'icon': '🏠'},
                'crm': {'title': 'CRM', 'icon': '👥'},
                ...
            }
    """
    if not is_feature_enabled('navigation'):
        return
    
    nav_hist = get_navigation_history()
    router = get_router()
    
    if nav_hist:
        # Seiten-Titel und Icons registrieren
        for page, config in page_config.items():
            nav_hist.register_page_title(page, config.get('title', page))
            if 'icon' in config:
                nav_hist.register_page_icon(page, config['icon'])
        
        # Back/Forward Buttons
        st.sidebar.markdown("### Navigation")
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if nav_hist.can_go_back():
                if st.button("◄", key="sidebar_back", help="Zurück"):
                    prev_entry = nav_hist.back()
                    if prev_entry:
                        router.navigate(prev_entry.page, prev_entry.params)
                        st.rerun()
        
        with col2:
            if nav_hist.can_go_forward():
                if st.button("►", key="sidebar_forward", help="Vorwärts"):
                    next_entry = nav_hist.forward()
                    if next_entry:
                        router.navigate(next_entry.page, next_entry.params)
                        st.rerun()
        
        # Besuchsstatistik (Expander)
        with st.sidebar.expander("📊 Seiten-Statistik"):
            page_visits = nav_hist.get_page_visits()
            if page_visits:
                sorted_visits = sorted(page_visits.items(), key=lambda x: x[1], reverse=True)
                for page, count in sorted_visits[:5]:  # Top 5
                    title = page_config.get(page, {}).get('title', page)
                    icon = page_config.get(page, {}).get('icon', '')
                    st.text(f"{icon} {title}: {count}")


def render_navigation_history_debug():
    """
    Rendere Debug-Info für Navigation History (nur für Admin)
    """
    if not is_feature_enabled('navigation'):
        st.warning("Navigation History ist deaktiviert")
        return
    
    nav_hist = get_navigation_history()
    if not nav_hist:
        st.error("Navigation History nicht verfügbar")
        return
    
    st.markdown("### 🔍 Navigation History Debug")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("History Size", len(nav_hist.history))
    with col2:
        st.metric("Current Index", nav_hist.current_index + 1 if nav_hist.current_index >= 0 else 0)
    with col3:
        st.metric("Can Go Back", "Ja" if nav_hist.can_go_back() else "Nein")
    with col4:
        st.metric("Can Go Forward", "Ja" if nav_hist.can_go_forward() else "Nein")
    
    # Current Entry
    current = nav_hist.get_current()
    if current:
        st.markdown("**Aktuelle Seite:**")
        st.json({
            'page': current.page,
            'params': current.params,
            'timestamp': current.timestamp.isoformat(),
            'duration': str(current.duration) if current.duration else None,
            'user_id': current.user_id,
        })
    
    # Complete Journey
    with st.expander("Komplette User Journey"):
        journey = nav_hist.get_journey()
        for i, entry in enumerate(journey):
            indicator = "➤" if i == nav_hist.current_index else " "
            st.text(f"{indicator} [{i+1}] {entry.page} @ {entry.timestamp.strftime('%H:%M:%S')}")
            if entry.params:
                st.json(entry.params)
    
    # Page Visits
    with st.expander("Seiten-Besuche"):
        page_visits = nav_hist.get_page_visits()
        if page_visits:
            import pandas as pd
            df = pd.DataFrame([
                {'Seite': page, 'Besuche': count}
                for page, count in sorted(page_visits.items(), key=lambda x: x[1], reverse=True)
            ])
            st.dataframe(df, use_container_width=True)


def track_page_view(page_name: str, **kwargs):
    """
    Utility-Funktion zum einfachen Tracking von Seitenaufrufen
    
    Args:
        page_name: Name der Seite
        **kwargs: Zusätzliche Parameter (user_id, params, metadata)
    
    Example:
        track_page_view('crm', user_id='user_123', params={'customer_id': 456})
    """
    if not is_feature_enabled('navigation'):
        return
    
    from core_integration import track_navigation
    
    track_navigation(
        page=page_name,
        user_id=kwargs.get('user_id'),
        params=kwargs.get('params'),
        session_id=kwargs.get('session_id'),
        metadata=kwargs.get('metadata')
    )


# Example Usage in gui.py
if __name__ == "__main__":
    st.set_page_config(page_title="Navigation Widget Demo", layout="wide")
    
    # Page Configuration
    PAGE_CONFIG = {
        'home': {'title': 'Startseite', 'icon': '🏠'},
        'pv': {'title': 'PV-Konfiguration', 'icon': '☀️'},
        'heatpump': {'title': 'Wärmepumpe', 'icon': '🔥'},
        'crm': {'title': 'CRM', 'icon': '👥'},
        'pdf': {'title': 'PDF-Angebote', 'icon': '📄'},
        'admin': {'title': 'Administration', 'icon': '⚙️'},
    }
    
    # Sidebar Navigation
    render_navigation_sidebar(PAGE_CONFIG)
    
    # Main Content
    st.title("Navigation Widget Demo")
    
    # Navigation Widget (Breadcrumbs + Back/Forward)
    render_navigation_widget(show_breadcrumbs=True, show_back_forward=True)
    
    # Page Selection
    selected_page = st.selectbox(
        "Seite auswählen",
        list(PAGE_CONFIG.keys()),
        format_func=lambda x: f"{PAGE_CONFIG[x]['icon']} {PAGE_CONFIG[x]['title']}"
    )
    
    # Track page view
    if st.button("Seite besuchen"):
        track_page_view(selected_page, user_id='demo_user', params={'demo': True})
        router = get_router()
        router.navigate(selected_page)
        st.rerun()
    
    # Debug Info (Expander)
    with st.expander("🔍 Navigation Debug"):
        render_navigation_history_debug()
