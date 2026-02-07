# unified_design_system.py
# Zentrales Design-System für die gesamte ARSCHIBALD-App
# Basierend auf dem Orange-Akzent Design aus data_input.py

"""
DESIGN-SYSTEM SPEZIFIKATION:
============================
Farben:
- Primär-Akzent: #ff8c00 (Orange)
- Hintergrund: #e8ecf1 (Hellgrau)
- Text: #1a202c (Dunkelgrau-Schwarz)
- Weiß-Gradient: #ffffff → #f7f9fc
- Orange-Hover: #fff5e6 → #ffe6cc

Schatten:
- Basis: 0 2px 4px rgba(255, 140, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.04)
- Hover: 0 3px 6px rgba(255, 140, 0, 0.12), 0 6px 12px rgba(0, 0, 0, 0.05)
- Focus: 0 4px 8px rgba(255, 140, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.06)
- Stark: 0 4px 8px rgba(255, 140, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.08)

Border:
- Basis: 1px solid rgba(255, 200, 140, 0.3)
- Akzent: 4-6px solid #ff8c00 (links)
- Hover: border-color #ff8c00

Border-Radius:
- Klein: 8px
- Standard: 12px
- Groß: 16px

Transitions:
- Standard: all 0.3s ease
"""

def get_unified_css() -> str:
    """
    Gibt das einheitliche CSS für die gesamte App zurück.
    Dieses CSS sollte in JEDEM Modul/Seite eingefügt werden.
    """
    return """
    <style>
    /* ==================== GLOBALE BASIS-STYLES ==================== */
    
    /* Haupthintergrund */
    .stApp, .main, .block-container {
        background-color: #e8ecf1 !important;
    }
    
    /* Alle Texte schwarz und fett */
    .main label,
    .main .stSelectbox label,
    .main .stTextInput label, 
    .main .stTextInput > label,
    .main .stNumberInput label,
    .main .stNumberInput > label,
    .main .stCheckbox label,
    .main .stCheckbox > label,
    .main .stRadio label,
    .main .stRadio > label,
    .main .stSlider label,
    .main .stTextArea label,
    .main .stDateInput label,
    .main .stTimeInput label,
    .main .stFileUploader label,
    .main [data-testid="stWidgetLabel"],
    .main div[data-testid="stWidgetLabel"],
    .main .stMarkdown p,
    .main .stMarkdown li,
    .main .stMarkdown span,
    .main .element-container label,
    .main .row-widget label,
    .main .stExpander label,
    .main p,
    .main span:not(.st-emotion-cache-10trblm) {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* Überschriften */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* ==================== BUTTONS ==================== */
    
    .stButton > button {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        color: #1a202c !important;
        font-weight: 700 !important;
        border: 2px solid rgba(255, 200, 140, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.04) !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        border-color: #ff8c00 !important;
        box-shadow: 0 6px 12px rgba(255, 140, 0, 0.2), 0 12px 24px rgba(255, 140, 0, 0.15) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        background: linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%) !important;
        transform: translateY(0) !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.15) !important;
    }
    
    /* ==================== EINGABEFELDER ==================== */
    
    .main input[type="text"],
    .main input[type="number"],
    .main input[type="email"],
    .main input[type="tel"],
    .main input[type="password"],
    .main input[type="date"],
    .main input[type="time"],
    .main textarea,
    .main .stTextInput > div > div > input,
    .main .stNumberInput > div > div > input {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.04) !important;
        border: 1px solid rgba(255, 200, 140, 0.2) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    .main input:focus,
    .main textarea:focus {
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.06) !important;
        border-color: #ff8c00 !important;
        background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%) !important;
        outline: none !important;
    }
    
    .main input:hover,
    .main textarea:hover {
        box-shadow: 0 3px 6px rgba(255, 140, 0, 0.12), 0 6px 12px rgba(0, 0, 0, 0.05) !important;
        border-color: rgba(255, 140, 0, 0.4) !important;
    }
    
    /* Number Input Container */
    .main .stNumberInput > div {
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.04) !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        transition: all 0.3s ease !important;
    }
    
    .main .stNumberInput > div:hover {
        box-shadow: 0 3px 6px rgba(255, 140, 0, 0.12), 0 6px 12px rgba(0, 0, 0, 0.05) !important;
    }
    
    .main .stNumberInput > div:focus-within {
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.06) !important;
        background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%) !important;
    }
    
    /* +/- Buttons */
    .main .stNumberInput button {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        border: 1px solid rgba(255, 200, 140, 0.3) !important;
        box-shadow: 0 1px 2px rgba(255, 140, 0, 0.08) !important;
        transition: all 0.3s ease !important;
        border-radius: 6px !important;
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    .main .stNumberInput button:hover {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        border-color: #ff8c00 !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.15), 0 4px 8px rgba(0, 0, 0, 0.06) !important;
        transform: translateY(-1px) !important;
    }
    
    .main .stNumberInput button:active {
        transform: translateY(0) !important;
        box-shadow: 0 1px 2px rgba(255, 140, 0, 0.12) !important;
    }
    
    /* ==================== SELECTBOX / DROPDOWN ==================== */
    
    .main .stSelectbox > div > div,
    .main .stSelectbox [data-baseweb="select"] {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.04) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        border: 1px solid rgba(255, 200, 140, 0.2) !important;
    }
    
    .main .stSelectbox > div > div {
        display: flex !important;
        align-items: center !important;
    }
    
    .main .stSelectbox [data-baseweb="select"] > div {
        display: flex !important;
        align-items: center !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    .main .stSelectbox [data-baseweb="select"]:hover {
        box-shadow: 0 3px 6px rgba(255, 140, 0, 0.12), 0 6px 12px rgba(0, 0, 0, 0.05) !important;
        border-color: rgba(255, 140, 0, 0.4) !important;
    }
    
    /* ==================== CHECKBOX & RADIO ==================== */
    
    .main .stCheckbox > label,
    .main .stRadio > label {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        border: 2px solid rgba(255, 200, 140, 0.3) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.3s ease !important;
        margin-bottom: 0.5rem !important;
    }
    
    .main .stCheckbox > label:hover,
    .main .stRadio > label:hover {
        border-color: #ff8c00 !important;
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        box-shadow: 0 3px 6px rgba(255, 140, 0, 0.12), 0 6px 12px rgba(0, 0, 0, 0.05) !important;
    }
    
    input[type="checkbox"]:checked,
    input[type="radio"]:checked {
        accent-color: #ff8c00 !important;
    }
    
    /* ==================== EXPANDER ==================== */
    
    .main .streamlit-expanderHeader {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        border-left: 4px solid #ff8c00 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.1), 0 4px 8px rgba(0, 0, 0, 0.05) !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
        margin-bottom: 0.5rem !important;
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    .main .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.2), 0 8px 16px rgba(0, 0, 0, 0.08) !important;
        border-left-color: #ff8c00 !important;
        transform: translateX(2px) !important;
    }
    
    .main .streamlit-expanderContent {
        background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%) !important;
        border-radius: 0 0 12px 12px !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05), 0 2px 4px rgba(0, 0, 0, 0.03) !important;
        padding: 1.5rem !important;
        border-left: 2px solid rgba(255, 140, 0, 0.2) !important;
        margin-bottom: 1rem !important;
    }
    
    /* ==================== INFO/WARNING/SUCCESS BOXES ==================== */
    
    .main .stAlert {
        border-left: 4px solid #ff8c00 !important;
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.06) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
    }
    
    .main .stAlert:hover {
        box-shadow: 0 6px 12px rgba(255, 140, 0, 0.18), 0 4px 8px rgba(0, 0, 0, 0.08) !important;
        transform: translateY(-1px) !important;
    }
    
    /* ==================== DIVIDER / TRENNLINIEN ==================== */
    
    .main hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, rgba(255, 140, 0, 0.3), transparent) !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.1) !important;
        margin: 2rem 0 !important;
    }
    
    /* ==================== TABS ==================== */
    
    .main .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.04) !important;
    }
    
    .main .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        color: #1a202c !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        padding: 0.75rem 1.5rem !important;
    }
    
    .main .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        color: #ff8c00 !important;
    }
    
    .main .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        border-bottom: 3px solid #ff8c00 !important;
        color: #ff8c00 !important;
    }
    
    /* ==================== COLUMNS / CARDS ==================== */
    
    .main .element-container {
        transition: all 0.3s ease !important;
    }
    
    /* ==================== SIDEBAR ==================== */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 140, 0, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, rgba(255, 140, 0, 0.2) 0%, rgba(255, 140, 0, 0.1) 100%) !important;
        border-color: #ff8c00 !important;
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.3) !important;
    }
    
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* ==================== DATAFRAME / TABLES ==================== */
    
    .main .stDataFrame,
    .main [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.06) !important;
    }
    
    .main .stDataFrame thead tr th {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        color: #1a202c !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #ff8c00 !important;
    }
    
    .main .stDataFrame tbody tr:hover {
        background: rgba(255, 140, 0, 0.05) !important;
    }
    
    /* ==================== SLIDER ==================== */
    
    .main .stSlider > div > div > div {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.04) !important;
    }
    
    .main .stSlider [role="slider"] {
        background: #ff8c00 !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.3) !important;
    }
    
    /* ==================== FILE UPLOADER ==================== */
    
    .main .stFileUploader > div {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        border: 2px dashed rgba(255, 140, 0, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.3s ease !important;
    }
    
    .main .stFileUploader > div:hover {
        border-color: #ff8c00 !important;
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.06) !important;
    }
    
    /* ==================== METRIC / KPI CARDS ==================== */
    
    .main [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        border-left: 4px solid #ff8c00 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.3s ease !important;
    }
    
    .main [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.06) !important;
        transform: translateY(-2px) !important;
    }
    
    .main [data-testid="stMetricLabel"] {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    .main [data-testid="stMetricValue"] {
        color: #ff8c00 !important;
        font-weight: 700 !important;
    }
    
    /* ==================== PROGRESS BAR ==================== */
    
    .main .stProgress > div > div {
        background: linear-gradient(90deg, #ff8c00 0%, #ffa500 100%) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.3) !important;
    }
    
    /* ==================== SPINNER / LOADING ==================== */
    
    .main .stSpinner > div {
        border-top-color: #ff8c00 !important;
    }
    
    /* ==================== TOAST / NOTIFICATIONS ==================== */
    
    .main .stToast {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        border-left: 4px solid #ff8c00 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* ==================== CODE BLOCKS ==================== */
    
    .main .stCodeBlock {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%) !important;
        border-left: 4px solid #ff8c00 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.06) !important;
    }
    
    /* ==================== CUSTOM CARD STYLE ==================== */
    
    .custom-card {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.08);
        border-left: 6px solid #ff8c00;
        border: 1px solid rgba(255, 200, 140, 0.3);
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        box-shadow: 0 6px 12px rgba(255, 140, 0, 0.2), 0 12px 24px rgba(0, 0, 0, 0.10);
        transform: translateY(-2px);
    }
    
    .custom-card h2,
    .custom-card h3 {
        color: #1a202c;
        margin: 0 0 1rem 0;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    </style>
    """


def get_card_header_html(title: str, icon: str = "") -> str:
    """
    Gibt HTML für einen standardisierten Card-Header zurück.
    
    Args:
        title: Der Titel der Card
        icon: Optionales Icon (ohne Emojis zu verwenden)
        
    Returns:
        HTML-String für den Card-Header
    """
    icon_html = f'<span style="margin-right: 0.5rem;">{icon}</span>' if icon else ""
    
    return f"""
    <div style="
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 8px rgba(255, 140, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.08);
        border-left: 6px solid #ff8c00;
        border: 1px solid rgba(255, 200, 140, 0.3);
        transition: all 0.3s ease;
    ">
        <h2 style="color: #1a202c; margin: 0; font-size: 1.6rem; font-weight: 700; letter-spacing: -0.02em;">
            {icon_html}{title}
        </h2>
    </div>
    """


def get_section_divider() -> str:
    """
    Gibt HTML für einen standardisierten Abschnittsteiler zurück.
    """
    return '<hr style="border: none; height: 2px; background: linear-gradient(90deg, transparent, rgba(255, 140, 0, 0.3), transparent); box-shadow: 0 2px 4px rgba(255, 140, 0, 0.1); margin: 2rem 0;">'


def apply_unified_design():
    """
    Wendet das einheitliche Design auf die aktuelle Seite an.
    Diese Funktion sollte am Anfang jeder Seite/Komponente aufgerufen werden.
    
    Usage:
        from unified_design_system import apply_unified_design
        
        def my_page():
            apply_unified_design()
            # Rest der Seite...
    """
    import streamlit as st
    st.markdown(get_unified_css(), unsafe_allow_html=True)


# Exportiere die Hauptfunktionen
__all__ = [
    'get_unified_css',
    'get_card_header_html',
    'get_section_divider',
    'apply_unified_design',
]
