"""
Auto-Contrast CSS Generator

Generiert CSS-Regeln für automatische Kontrastanpassung
"""

from utils.contrast_utils import get_accessible_text_color, is_light_color


def generate_auto_contrast_css(theme_colors: dict) -> str:
    """
    Generiert CSS für automatische Kontrastanpassung
    
    Args:
        theme_colors: Dictionary mit Theme-Farben
                     Keys: background, foreground, primary, secondary, etc.
    
    Returns:
        CSS-String mit Auto-Contrast-Regeln
    """
    
    # Hole Farben aus Theme
    bg = theme_colors.get('background', '#FFFFFF')
    fg = theme_colors.get('foreground', '#0A0A0A')
    primary = theme_colors.get('primary', '#3B82F6')
    secondary = theme_colors.get('secondary', '#64748B')
    muted = theme_colors.get('muted', '#F1F5F9')
    accent = theme_colors.get('accent', '#F59E0B')
    
    # Berechne optimale Textfarben
    text_on_bg = get_accessible_text_color(bg)
    text_on_primary = get_accessible_text_color(primary)
    text_on_secondary = get_accessible_text_color(secondary)
    text_on_muted = get_accessible_text_color(muted)
    text_on_accent = get_accessible_text_color(accent)
    
    css = f"""
/* ==========================================
   AUTO-CONTRAST CSS - ENHANCED VERSION
   Automatische Textfarben-Anpassung
   Überschreibt ALLE anderen Styles
   ========================================== */

/* Basis-Kontrast Variablen */
:root {{
    --text-on-background: {text_on_bg} !important;
    --text-on-primary: {text_on_primary} !important;
    --text-on-secondary: {text_on_secondary} !important;
    --text-on-muted: {text_on_muted} !important;
    --text-on-accent: {text_on_accent} !important;
}}

/* ==========================================
   KRITISCHE FIXES: Dunkle Schrift auf Dunkel
   ========================================== */

/* ALLE Text-Elemente - höchste Priorität */
body,
body *,
div,
div *,
span,
p,
h1, h2, h3, h4, h5, h6,
label,
button,
a,
input,
textarea,
select {{
    color: {text_on_bg} !important;
}}

/* Streamlit-Container */
.main,
.main *,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] *,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlock"] *,
[data-testid="stHorizontalBlock"],
[data-testid="stHorizontalBlock"] * {{
    color: {text_on_bg} !important;
}}

/* Sidebar - KRITISCH */
.stSidebar,
.stSidebar *,
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] *,
[data-testid="stSidebar"],
[data-testid="stSidebar"] * {{
    background-color: {bg} !important;
    color: {text_on_bg} !important;
}}

/* Sidebar-Überschriften */
.stSidebar h1,
.stSidebar h2,
.stSidebar h3,
.stSidebar h4,
.stSidebar h5,
.stSidebar h6,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] h5,
section[data-testid="stSidebar"] h6 {{
    color: {text_on_bg} !important;
}}

/* Sidebar Markdown */
.stSidebar .stMarkdown,
.stSidebar .stMarkdown *,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown * {{
    color: {text_on_bg} !important;
}}

/* Sidebar Buttons */
.stSidebar .stButton > button,
.stSidebar button,
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] button {{
    color: {text_on_bg} !important;
    background-color: transparent !important;
    border: 1px solid {text_on_bg} !important;
}}

.stSidebar .stButton > button:hover,
.stSidebar button:hover,
section[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] button:hover {{
    background-color: {muted} !important;
    color: {text_on_muted} !important;
    border-color: {text_on_muted} !important;
}}

/* Selectbox, Radio, Checkbox - KRITISCH */
.stSelectbox,
.stSelectbox *,
.stSelectbox label,
.stSelectbox > div,
.stSelectbox > div > div,
.stRadio,
.stRadio *,
.stRadio label,
.stRadio > div,
.stCheckbox,
.stCheckbox *,
.stCheckbox label,
.stCheckbox > div {{
    color: {text_on_bg} !important;
}}

/* Selectbox Dropdown */
[data-baseweb="select"],
[data-baseweb="select"] *,
.stSelectbox [role="listbox"],
.stSelectbox [role="option"] {{
    color: {text_on_bg} !important;
    background-color: {bg} !important;
}}

/* Text Inputs */
.stTextInput,
.stTextInput *,
.stTextInput label,
.stTextInput input,
.stNumberInput,
.stNumberInput *,
.stNumberInput label,
.stNumberInput input,
.stTextArea,
.stTextArea *,
.stTextArea label,
.stTextArea textarea {{
    color: {text_on_bg} !important;
}}

/* Input Fields */
input,
input *,
textarea,
textarea *,
select,
select * {{
    color: {text_on_bg} !important;
}}

/* Tabs - KRITISCH */
.stTabs,
.stTabs *,
[data-baseweb="tab-list"],
[data-baseweb="tab-list"] *,
[data-baseweb="tab"],
[data-baseweb="tab"] *,
[data-baseweb="tab-panel"],
[data-baseweb="tab-panel"] * {{
    color: {text_on_bg} !important;
    background-color: {bg} !important;
}}

.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] * {{
    background-color: {primary} !important;
    color: {text_on_primary} !important;
}}

/* Expander - KRITISCH */
.streamlit-expanderHeader,
.streamlit-expanderHeader *,
[data-testid="stExpander"],
[data-testid="stExpander"] *,
details,
details *,
summary,
summary * {{
    color: {text_on_bg} !important;
    background-color: {muted} !important;
}}

/* Metriken */
.stMetric,
.stMetric *,
.stMetric label,
.stMetric [data-testid="stMetricValue"],
.stMetric [data-testid="stMetricDelta"] {{
    color: {text_on_bg} !important;
}}

/* Dataframe / Tabellen */
.stDataFrame,
.stDataFrame *,
.stTable,
.stTable *,
table,
table *,
thead,
thead *,
tbody,
tbody *,
th,
td {{
    color: {text_on_bg} !important;
}}

.stDataFrame th,
.stTable th,
table th,
thead th {{
    background-color: {muted} !important;
    color: {text_on_muted} !important;
}}

/* Forms */
form,
form *,
.stForm,
.stForm * {{
    color: {text_on_bg} !important;
}}

/* Markdown - ALLE Varianten */
.stMarkdown,
.stMarkdown *,
.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4,
.stMarkdown h5,
.stMarkdown h6,
.stMarkdown p,
.stMarkdown span,
.stMarkdown div,
.stMarkdown li,
.stMarkdown ul,
.stMarkdown ol {{
    color: {text_on_bg} !important;
}}

.stMarkdown a {{
    color: {primary} !important;
}}

.stMarkdown a:hover {{
    color: {accent} !important;
}}

/* Buttons - ALLE Typen */
.stButton,
.stButton *,
.stButton > button,
.stDownloadButton,
.stDownloadButton *,
.stDownloadButton > button,
button,
button * {{
    color: {text_on_primary} !important;
}}

.stButton > button {{
    background-color: {primary} !important;
    color: {text_on_primary} !important;
    border: none !important;
}}

.stButton > button:hover {{
    background-color: {accent} !important;
    color: {text_on_accent} !important;
}}

/* Download Button */
.stDownloadButton > button {{
    background-color: {secondary} !important;
    color: {text_on_secondary} !important;
}}

.stDownloadButton > button:hover {{
    background-color: {primary} !important;
    color: {text_on_primary} !important;
}}

/* File Uploader */
.stFileUploader,
.stFileUploader *,
.stFileUploader label {{
    color: {text_on_bg} !important;
}}

/* Slider */
.stSlider,
.stSlider *,
.stSlider label {{
    color: {text_on_bg} !important;
}}

/* MultiSelect */
.stMultiSelect,
.stMultiSelect *,
.stMultiSelect label,
.stMultiSelect > div,
.stMultiSelect > div > div {{
    color: {text_on_bg} !important;
    background-color: {muted} !important;
}}

/* Caption */
.stCaption,
.stCaption * {{
    color: {secondary} !important;
}}

/* JSON */
.stJson,
.stJson * {{
    background-color: {muted} !important;
    color: {text_on_muted} !important;
}}

/* Columns */
[data-testid="column"],
[data-testid="column"] * {{
    color: {text_on_bg} !important;
}}

/* Container */
[data-testid="stContainer"],
[data-testid="stContainer"] * {{
    color: {text_on_bg} !important;
}}

/* ==========================================
   SHADCN KOMPONENTEN
   ========================================== */

/* Cards */
.shadcn-card,
.shadcn-card * {{
    background-color: {bg} !important;
    color: {text_on_bg} !important;
    border: 1px solid {muted} !important;
}}

.shadcn-card-header,
.shadcn-card-header * {{
    background-color: {muted} !important;
    color: {text_on_muted} !important;
}}

.shadcn-card-title,
.shadcn-card-description,
.shadcn-card-content {{
    color: {text_on_bg} !important;
}}

/* Custom Buttons */
.shadcn-button,
.shadcn-button * {{
    background-color: {primary} !important;
    color: {text_on_primary} !important;
}}

.shadcn-button:hover,
.shadcn-button:hover * {{
    background-color: {accent} !important;
    color: {text_on_accent} !important;
}}

.shadcn-button-secondary,
.shadcn-button-secondary * {{
    background-color: {secondary} !important;
    color: {text_on_secondary} !important;
}}

.shadcn-button-outline,
.shadcn-button-outline * {{
    background-color: transparent !important;
    color: {text_on_bg} !important;
    border: 1px solid {text_on_bg} !important;
}}

/* Badges */
.shadcn-badge,
.shadcn-badge * {{
    background-color: {primary} !important;
    color: {text_on_primary} !important;
}}

.shadcn-badge-secondary,
.shadcn-badge-secondary * {{
    background-color: {secondary} !important;
    color: {text_on_secondary} !important;
}}

/* Alerts */
.shadcn-alert,
.shadcn-alert *,
.shadcn-alert-title {{
    background-color: {muted} !important;
    color: {text_on_muted} !important;
}}

/* Info/Warning/Error/Success Boxes */
.stAlert,
.stAlert *,
[data-testid="stAlert"],
[data-testid="stAlert"] *,
.stSuccess,
.stSuccess *,
.stWarning,
.stWarning *,
.stError,
.stError *,
.stInfo,
.stInfo * {{
    color: {text_on_bg} !important;
}}

/* Code Blocks */
.stCodeBlock,
.stCodeBlock *,
.stCodeBlock code,
code,
pre,
pre * {{
    background-color: {muted} !important;
    color: {text_on_muted} !important;
}}

/* ==========================================
   ACCESSIBILITY & FALLBACKS
   ========================================== */

/* Focus States */
*:focus,
*:focus-visible {{
    outline: 2px solid {primary} !important;
    outline-offset: 2px !important;
}}

/* Platzhalter-Text */
::placeholder {{
    color: {secondary} !important;
    opacity: 0.7 !important;
}}

/* Selection */
::selection {{
    background-color: {primary} !important;
    color: {text_on_primary} !important;
}}

/* Disabled States */
:disabled,
[disabled],
.disabled {{
    opacity: 0.5 !important;
    color: {secondary} !important;
}}

/* Print Styles */
@media print {{
    body,
    body * {{
        background-color: white !important;
        color: black !important;
    }}
}}

/* ==========================================
   ZUSÄTZLICHE ROBUSTHEIT
   ========================================== */

/* Alle restlichen Elemente */
article, aside, footer, header, nav, section,
main, figure, figcaption, time, mark, abbr,
address, blockquote, cite, q, small, strong,
em, i, b, u, s, sub, sup, code, kbd, samp,
var, del, ins, dfn, ruby, rt, rp {{
    color: {text_on_bg} !important;
}}
"""
    
    return css


def inject_auto_contrast_css(theme_colors: dict) -> None:
    """
    Injiziert Auto-Contrast CSS in Streamlit
    
    Args:
        theme_colors: Dictionary mit Theme-Farben
    """
    import streamlit as st
    
    css = generate_auto_contrast_css(theme_colors)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
