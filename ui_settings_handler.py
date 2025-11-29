"""
UI Settings Handler
Verwaltet UI/UX Einstellungen und wendet sie auf die App an
"""

import streamlit as st
from typing import Any, Dict


def apply_ui_settings():
    """
    Lädt und wendet UI-Einstellungen aus der Datenbank an.
    Wird beim App-Start aufgerufen.
    """
    try:
        from database import load_admin_setting
        
        # Dark Mode
        dark_mode = load_admin_setting('ui_dark_mode_enabled', True)  # Default: Dark
        if isinstance(dark_mode, str):
            dark_mode = dark_mode.lower() in ('true', '1', 'yes')
        
        st.session_state['theme_mode'] = 'dark' if dark_mode else 'light'
        st.session_state['ui_dark_mode_enabled'] = dark_mode
        
        # Wende SOFORT CSS an - wirkt ohne Neustart!
        if dark_mode:
            apply_dark_mode_styles()
        else:
            apply_light_mode_styles()
        
        # Animationen
        animations_enabled = load_admin_setting('ui_animations_enabled', True)
        if isinstance(animations_enabled, str):
            animations_enabled = animations_enabled.lower() in ('true', '1', 'yes')
        
        st.session_state['animations_enabled'] = animations_enabled
        if not animations_enabled:
            disable_animations()
        
        # Compact View
        compact_view = load_admin_setting('ui_compact_view_enabled', False)
        if isinstance(compact_view, str):
            compact_view = compact_view.lower() in ('true', '1', 'yes')
        
        st.session_state['compact_view'] = compact_view
        if compact_view:
            apply_compact_view_styles()
        
        # Color Scheme
        color_scheme = load_admin_setting('ui_color_scheme', 'Standard')
        apply_color_scheme(color_scheme)
        
        return True
        
    except Exception as e:
        st.warning(f"UI-Einstellungen konnten nicht geladen werden: {e}")
        return False


def apply_dark_mode_styles():
    """Wendet Dark Mode CSS an - SOFORT wirksam!"""
    st.markdown("""
    <style>
    /* ============================================
       DARK MODE - VOLLSTÄNDIGE UI TRANSFORMATION
       ============================================ */
    
    /* Main App Container */
    .stApp {
        background-color: #0B0F14 !important;
        color: #E6F7FF !important;
    }
    
    /* Sidebar Dark */
    section[data-testid="stSidebar"] {
        background-color: #111720 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #E6F7FF !important;
    }
    
    /* Main Content Area */
    .main .block-container {
        background-color: #0B0F14 !important;
        color: #E6F7FF !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #00E5FF !important;
    }
    
    /* Text & Paragraphs */
    p, span, div, label {
        color: #E6F7FF !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1a2332 !important;
        color: #E6F7FF !important;
        border: 1px solid #2a3342 !important;
    }
    
    .stButton > button:hover {
        background-color: #2a3342 !important;
        border-color: #00E5FF !important;
        color: #00E5FF !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #00E5FF !important;
        color: #0B0F14 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #4EA1FF !important;
        color: #0B0F14 !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1a2332 !important;
        color: #E6F7FF !important;
        border: 1px solid #2a3342 !important;
    }
    
    /* Selectbox & Dropdown */
    .stSelectbox > div > div,
    div[data-baseweb="select"] > div {
        background-color: #1a2332 !important;
        color: #E6F7FF !important;
        border: 1px solid #2a3342 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a2332 !important;
        color: #E6F7FF !important;
    }
    
    .streamlit-expanderContent {
        background-color: #111720 !important;
        border: 1px solid #2a3342 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #111720 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #E6F7FF !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a2332 !important;
        color: #00E5FF !important;
    }
    
    /* Dataframe & Tables */
    .dataframe {
        background-color: #1a2332 !important;
        color: #E6F7FF !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #00E5FF !important;
    }
    
    /* Code Blocks */
    code {
        background-color: #0B1220 !important;
        color: #00E5FF !important;
    }
    
    pre {
        background-color: #0B1220 !important;
        border: 1px solid #2a3342 !important;
    }
    
    /* Info/Warning/Error Boxes */
    .stAlert {
        background-color: #1a2332 !important;
        color: #E6F7FF !important;
        border-left: 4px solid #00E5FF !important;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_light_mode_styles():
    """Wendet Light Mode CSS an - SOFORT wirksam!"""
    st.markdown("""
    <style>
    /* ============================================
       LIGHT MODE - VOLLSTÄNDIGE UI TRANSFORMATION
       ============================================ */
    
    /* Main App Container */
    .stApp {
        background-color: #FFFFFF !important;
        color: #262730 !important;
    }
    
    /* Sidebar Light */
    section[data-testid="stSidebar"] {
        background-color: #F7F9FC !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #262730 !important;
    }
    
    /* Main Content Area */
    .main .block-container {
        background-color: #FFFFFF !important;
        color: #262730 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1a202c !important;
    }
    
    /* Text & Paragraphs */
    p, span, div, label {
        color: #262730 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #F0F2F6 !important;
        color: #262730 !important;
        border: 1px solid #D0D5DD !important;
    }
    
    .stButton > button:hover {
        background-color: #E0E4EA !important;
        border-color: #667eea !important;
        color: #1a202c !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #667eea !important;
        color: #FFFFFF !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #5568d3 !important;
        color: #FFFFFF !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #FFFFFF !important;
        color: #262730 !important;
        border: 1px solid #D0D5DD !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }
    
    /* Selectbox & Dropdown */
    .stSelectbox > div > div,
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #262730 !important;
        border: 1px solid #D0D5DD !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #F7F9FC !important;
        color: #262730 !important;
        border: 1px solid #E0E4EA !important;
    }
    
    .streamlit-expanderContent {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E4EA !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F7F9FC !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #262730 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #667eea !important;
        border-bottom: 2px solid #667eea !important;
    }
    
    /* Dataframe & Tables */
    .dataframe {
        background-color: #FFFFFF !important;
        color: #262730 !important;
        border: 1px solid #E0E4EA !important;
    }
    
    .dataframe th {
        background-color: #F7F9FC !important;
        color: #1a202c !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #667eea !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #4a5568 !important;
    }
    
    /* Code Blocks */
    code {
        background-color: #F7F9FC !important;
        color: #667eea !important;
        border: 1px solid #E0E4EA !important;
    }
    
    pre {
        background-color: #F7F9FC !important;
        border: 1px solid #E0E4EA !important;
    }
    
    /* Info/Warning/Error Boxes */
    .stAlert {
        background-color: #F7F9FC !important;
        color: #262730 !important;
    }
    
    /* Checkbox & Radio */
    .stCheckbox label,
    .stRadio label {
        color: #262730 !important;
    }
    
    /* Slider */
    .stSlider [data-testid="stTickBar"] {
        background-color: #E0E4EA !important;
    }
    </style>
    """, unsafe_allow_html=True)


def disable_animations():
    """Deaktiviert alle UI-Animationen"""
    st.markdown("""
    <style>
    /* Disable Animations */
    * {
        transition: none !important;
        animation: none !important;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_compact_view_styles():
    """Wendet kompakte Ansicht an"""
    st.markdown("""
    <style>
    /* Compact View */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .stButton > button {
        padding: 0.4rem 1rem;
        font-size: 14px;
    }
    
    .stExpander {
        margin-bottom: 0.5rem;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_color_scheme(scheme_name: str):
    """Wendet ein Farbschema an"""
    
    color_schemes = {
        'Standard': {
            'primary': '#ff4b4b',
            'secondary': '#0068c9',
            'accent': '#00c983'
        },
        'Ocean Blue': {
            'primary': '#0077b6',
            'secondary': '#0096c7',
            'accent': '#48cae4'
        },
        'Forest Green': {
            'primary': '#2d6a4f',
            'secondary': '#52b788',
            'accent': '#95d5b2'
        },
        'Sunset Orange': {
            'primary': '#f77f00',
            'secondary': '#fcbf49',
            'accent': '#d62828'
        },
        'Purple Rain': {
            'primary': '#7209b7',
            'secondary': '#b5179e',
            'accent': '#f72585'
        },
        'Monochrome': {
            'primary': '#2b2d42',
            'secondary': '#8d99ae',
            'accent': '#edf2f4'
        }
    }
    
    if scheme_name not in color_schemes:
        scheme_name = 'Standard'
    
    colors = color_schemes[scheme_name]
    
    st.markdown(f"""
    <style>
    /* Color Scheme: {scheme_name} */
    .stButton > button[kind="primary"] {{
        background-color: {colors['primary']};
        border-color: {colors['primary']};
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: {colors['secondary']};
        border-color: {colors['secondary']};
    }}
    
    .stProgress > div > div {{
        background-color: {colors['primary']};
    }}
    
    a {{
        color: {colors['secondary']};
    }}
    
    .stSuccess {{
        background-color: {colors['accent']}22;
        border-left-color: {colors['accent']};
    }}
    
    .stInfo {{
        background-color: {colors['secondary']}22;
        border-left-color: {colors['secondary']};
    }}
    </style>
    """, unsafe_allow_html=True)
    
    st.session_state['color_scheme'] = scheme_name


def get_ui_setting(key: str, default: Any = None) -> Any:
    """
    Holt eine UI-Einstellung aus Session State oder Database
    
    Args:
        key: Setting-Key
        default: Default-Wert falls nicht gefunden
        
    Returns:
        Einstellungswert
    """
    # Erst Session State prüfen
    if key in st.session_state:
        return st.session_state[key]
    
    # Dann Database
    try:
        from database import load_admin_setting
        value = load_admin_setting(key, default)
        
        # Boolean conversion
        if isinstance(value, str) and value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        
        # In Session State cachen
        st.session_state[key] = value
        return value
        
    except Exception:
        return default


def save_ui_setting(key: str, value: Any) -> bool:
    """
    Speichert eine UI-Einstellung in Database und Session State
    
    Args:
        key: Setting-Key
        value: Zu speichernder Wert
        
    Returns:
        True wenn erfolgreich
    """
    try:
        from database import save_admin_setting
        
        # In Database speichern
        success = save_admin_setting(key, value)
        
        # In Session State aktualisieren
        if success:
            st.session_state[key] = value
            st.session_state[f'{key}_updated'] = True
        
        return success
        
    except Exception as e:
        st.error(f"Fehler beim Speichern von {key}: {e}")
        return False


def refresh_ui_settings():
    """
    Lädt alle UI-Einstellungen neu und wendet sie an.
    Wird nach dem Speichern aufgerufen.
    """
    apply_ui_settings()
    
    # Force rerun um Änderungen sichtbar zu machen
    if st.session_state.get('ui_refresh_needed', False):
        st.session_state['ui_refresh_needed'] = False
        st.rerun()
