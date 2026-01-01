"""
Demo: Phase 5 Navigation Modernization

Zeigt die neue Tab-basierte Navigation mit:
- Horizontal Tabs statt Sidebar Buttons
- Breadcrumbs
- User Info
- Settings Popover
"""

import streamlit as st
from typing import Dict, List

# Page config
st.set_page_config(
    page_title="Phase 5: Navigation Demo",
    page_
    layout="wide"
)

def get_page_labels() -> Dict[str, str]:
    """Page key to label mapping"""
    return {
        'input': 'Eingabe',
        'solar_calculator': 'Solar Calculator',
        '3d_view': '3D Visualisierung',
        'heatpump': 'Warmepumpe',
        'analysis': 'Analyse',
        'crm': 'CRM',
        'doc_output': 'PDF-Ausgabe',
        'admin': 'Admin',
        'quick_calc': 'Quick Calculator',
        'options': 'Optionen',
        'info_platform': 'Info Platform',
    }

def render_header_navigation():
    """Render modern header with breadcrumbs, user info, and settings"""
    
    # Initialize session state
    if 'active_page' not in st.session_state:
        st.session_state.active_page = 'input'
    if 'username' not in st.session_state:
        st.session_state.username = 'Demo User'
    if 'show_settings_popover' not in st.session_state:
        st.session_state.show_settings_popover = False
    if 'theme_preference' not in st.session_state:
        st.session_state.theme_preference = 'Hell'
    
    # Header with 3 columns
    header_col1, header_col2, header_col3 = st.columns([3, 1, 0.3])
    
    with header_col1:
        # Breadcrumbs
        page_labels = get_page_labels()
        current_page_label = page_labels.get(st.session_state.active_page, 'Startseite')
        st.markdown(
            f'<div style="padding: 8px 0; color: #64748b; font-size: 14px;">'
            f'Startseite / {current_page_label}'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with header_col2:
        # User info
        user_name = st.session_state.username
        st.markdown(
            f'<div style="text-align: right; padding: 8px 0; color: #475569; font-size: 14px;">'
            f'Angemeldet: {user_name}'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with header_col3:
        # Settings button
        if st.button('\u2699', key='header_settings_btn', help='Einstellungen'):
            st.session_state.show_settings_popover = not st.session_state.show_settings_popover
    
    st.markdown('---')
    
    # Settings Popover (if opened)
    if st.session_state.show_settings_popover:
        with st.expander('Einstellungen', expanded=True):
            st.write('Theme:')
            theme_options = ['Hell', 'Dunkel', 'Auto']
            current_theme = st.session_state.theme_preference
            
            new_theme = st.selectbox(
                'Theme auswahlen',
                theme_options,
                index=theme_options.index(current_theme),
                key='theme_select'
            )
            
            if new_theme != current_theme:
                st.session_state.theme_preference = new_theme
                st.success(f'Theme gewechselt zu: {new_theme}')
            
            if st.button('Schliessen', key='close_settings_popover'):
                st.session_state.show_settings_popover = False
                st.rerun()

def render_tabs_navigation():
    """Render tabs-based navigation"""
    
    # Tab configuration
    tab_items = [
        'Eingabe',
        'Solar Calculator',
        '3D Visualisierung',
        'Warmepumpe',
        'Analyse',
        'CRM',
        'PDF-Ausgabe',
        'Admin',
        'Quick Calculator',
        'Optionen',
        'Info Platform',
    ]
    
    tab_keys = [
        'input', 'solar_calculator', '3d_view', 'heatpump', 'analysis',
        'crm', 'doc_output', 'admin', 'quick_calc', 'options', 'info_platform'
    ]
    
    # Get current tab index
    try:
        current_idx = tab_keys.index(st.session_state.active_page)
    except ValueError:
        current_idx = 0
    
    # Try shadcn tabs, fallback to native
    try:
        from components.shadcn_ui_integration import tabs as shadcn_tabs
        
        selected_tab_label = shadcn_tabs(
            options=tab_items,
            default=tab_items[current_idx],
            key='main_nav_tabs'
        )
        
        # Map selected label back to key
        if selected_tab_label:
            try:
                new_idx = tab_items.index(selected_tab_label)
                new_key = tab_keys[new_idx]
                if new_key != st.session_state.active_page:
                    st.session_state.active_page = new_key
                    st.rerun()
            except ValueError:
                pass
    except ImportError:
        # Fallback: Native Streamlit tabs
        st.info('shadcn/ui nicht verfugbar - Fallback auf native Streamlit Tabs')
        
        # Create tabs
        tabs = st.tabs(tab_items)
        
        # Render content in selected tab
        with tabs[current_idx]:
            st.write(f'Aktive Seite: **{tab_items[current_idx]}**')
    
    st.markdown('---')

def render_page_content():
    """Render content for current page"""
    
    page_key = st.session_state.active_page
    page_labels = get_page_labels()
    page_name = page_labels.get(page_key, 'Unbekannt')
    
    st.header(page_name)
    
    # Page-specific content
    page_descriptions = {
        'input': 'Hier konnen Sie die Eingabedaten fur die PV-Anlage erfassen.',
        'solar_calculator': 'Berechnen Sie die optimale PV-Anlagen-Konfiguration.',
        '3d_view': 'Visualisieren Sie Ihre PV-Anlage in 3D.',
        'heatpump': 'Konfigurieren Sie Warmepumpen-Systeme.',
        'analysis': 'Analysieren Sie die Ergebnisse Ihrer Berechnungen.',
        'crm': 'Verwalten Sie Kunden und Projekte.',
        'doc_output': 'Erstellen Sie PDF-Angebote.',
        'admin': 'Administrieren Sie die Anwendung.',
        'quick_calc': 'Schnelle Kalkulationen fur unterwegs.',
        'options': 'Konfigurieren Sie Anwendungseinstellungen.',
        'info_platform': 'Informationen uber die Plattform.',
    }
    
    description = page_descriptions.get(page_key, 'Keine Beschreibung verfugbar.')
    st.info(description)
    
    # Demo content
    st.subheader('Demo-Inhalt')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label='Aktive Seite',
            value=page_name,
            delta=None
        )
    
    with col2:
        st.metric(
            label='Session Theme',
            value=st.session_state.theme_preference,
            delta=None
        )
    
    with col3:
        st.metric(
            label='User',
            value=st.session_state.username,
            delta=None
        )
    
    # Example data table
    st.subheader('Beispiel-Daten')
    import pandas as pd
    
    df = pd.DataFrame({
        'Parameter': ['Module', 'Wechselrichter', 'Speicher', 'Leistung'],
        'Wert': [20, 1, 1, '10 kWp'],
        'Status': ['OK', 'OK', 'Optional', 'Berechnet']
    })
    
    st.dataframe(df, use_container_width=True)
    
    # Action buttons
    st.subheader('Aktionen')
    
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    
    with btn_col1:
        if st.button('Speichern', key=f'save_{page_key}'):
            st.success('Daten gespeichert!')
    
    with btn_col2:
        if st.button('Zurucksetzen', key=f'reset_{page_key}'):
            st.warning('Daten zuruckgesetzt!')
    
    with btn_col3:
        if st.button('Exportieren', key=f'export_{page_key}'):
            st.info('Export gestartet...')
    
    with btn_col4:
        if st.button('Hilfe', key=f'help_{page_key}'):
            st.info('Hilfe fur diese Seite wird angezeigt.')

def render_sidebar():
    """Render compact sidebar"""
    
    with st.sidebar:
        st.markdown('### Navigation Demo')
        st.caption('Phase 5: Tab-basierte Navigation')
        
        st.markdown('---')
        
        st.caption('Schnellzugriff')
        
        if st.button('Startseite', key='quick_home', use_container_width=True):
            st.session_state.active_page = 'input'
            st.rerun()
        
        if st.button('Letzte Berechnung', key='quick_last_calc', use_container_width=True):
            st.session_state.active_page = 'analysis'
            st.rerun()
        
        st.markdown('---')
        
        st.caption('Statistik')
        st.metric('Seitenaufrufe', len(st.session_state.get('page_views', [])))
        st.metric('Aktuelle Sitzung', '12 min')

def track_page_view():
    """Track page views for demo"""
    if 'page_views' not in st.session_state:
        st.session_state.page_views = []
    
    current_page = st.session_state.active_page
    st.session_state.page_views.append({
        'page': current_page,
        'timestamp': pd.Timestamp.now()
    })

def main():
    """Main demo application"""
    
    # Title
    st.title('Phase 5: Navigation Modernization Demo')
    
    # Track page view
    track_page_view()
    
    # Render components
    render_header_navigation()
    render_tabs_navigation()
    render_page_content()
    render_sidebar()
    
    # Footer with stats
    st.markdown('---')
    
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.caption(f'Aktive Seite: {st.session_state.active_page}')
    
    with footer_col2:
        st.caption(f'Theme: {st.session_state.theme_preference}')
    
    with footer_col3:
        st.caption(f'User: {st.session_state.username}')

if __name__ == '__main__':
    import pandas as pd
    main()
