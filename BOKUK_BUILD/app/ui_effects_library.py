# ui_effects_library.py
"""
Datei: ui_effects_library.py
Zweck: Bibliothek mit 10 verschiedenen UI-Effekt-Stilen für Buttons, Slider, Dropdowns, Expander
Autor: GitHub Copilot
Datum: 2025-10-23
"""

# Universeller Support für ALLE UI-Elemente (NUR BASIS-STYLES,
# Hover-Effekte kommen von den einzelnen Effekten!)
UNIVERSAL_SIDEBAR_CSS = """
/* ========== UNIVERSELLE BEREICHE (SIDEBAR + MAIN CONTENT) - NUR BASIS ========== */

/* ========== EXPANDER - ALLE BEREICHE (NUR BASIS) ========== */
/* Main Content Expander - Basis */
details[data-testid="stExpander"] summary,
.streamlit-expanderHeader,
details summary,
div[data-testid="stExpander"] > details > summary,
.st-emotion-cache-1inwz65,
div[class*="st-emotion-cache"] details summary {
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

/* Sidebar Expander - Basis */
section[data-testid="stSidebar"] details[data-testid="stExpander"] summary,
section[data-testid="stSidebar"] .streamlit-expanderHeader,
section[data-testid="stSidebar"] details summary,
[data-testid="stSidebar"] div[data-testid="stExpander"] > details > summary {
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

/* ========== DROPDOWNS / SELECTBOX - ALLE BEREICHE (NUR BASIS) ========== */
/* Main Content Dropdowns - Basis */
div[data-baseweb="select"],
.stSelectbox > div > div,
div[data-testid="stSelectbox"] > div,
div[data-testid="stSelectbox"] > div > div,
div[class*="css-"][class*="e1nzilvr"] > div,
div[role="button"][aria-haspopup="listbox"],
.stSelectbox div[data-baseweb="select"] > div {
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

/* Sidebar Dropdowns - Basis */
section[data-testid="stSidebar"] div[data-baseweb="select"],
section[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div,
[data-testid="stSidebar"] div[role="button"][aria-haspopup="listbox"],
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

/* ========== NUMMER INPUT (+/- BUTTONS) - ALLE BEREICHE (NUR BASIS) ========== */
/* Main Content Number Input - Basis */
button[data-testid="stNumberInputStepUp"],
button[data-testid="stNumberInputStepDown"],
div[data-testid="stNumberInput"] button {
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Sidebar Number Input - Basis */
section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"],
section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"],
[data-testid="stSidebar"] div[data-testid="stNumberInput"] button {
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ========== SLIDER - ALLE BEREICHE ========== */
/* Main Content Slider */
input[type="range"],
div[data-testid="stSlider"] input,
.stSlider input[type="range"] {
    transition: all 0.3s ease !important;
}

/* Sidebar Slider */
section[data-testid="stSidebar"] input[type="range"],
[data-testid="stSidebar"] div[data-testid="stSlider"] input {
    transition: all 0.3s ease !important;
}

/* ========== CHECKBOX - ALLE BEREICHE (NUR BASIS) ========== */
/* Main Content Checkbox - Basis */
div[data-baseweb="checkbox"],
input[type="checkbox"] + div,
div[data-testid="stCheckbox"] > label > div,
div[data-testid="stCheckbox"] label {
    transition: all 0.2s ease;
    cursor: pointer;
}

/* Sidebar Checkbox - Basis */
section[data-testid="stSidebar"] div[data-baseweb="checkbox"],
[data-testid="stSidebar"] input[type="checkbox"] + div,
[data-testid="stSidebar"] div[data-testid="stCheckbox"] > label > div,
[data-testid="stSidebar"] div[data-testid="stCheckbox"] label {
    transition: all 0.2s ease;
    cursor: pointer;
}

/* ========== SIDEBAR BUTTONS - ALLE TYPEN (NUR BASIS) ========== */
section[data-testid="stSidebar"] .stButton button,
section[data-testid="stSidebar"] button[data-testid="baseButton-primary"],
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"],
section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] button[kind="secondary"],
[data-testid="stSidebar"] div[data-baseweb="button"],
[data-testid="stSidebar"] button {
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ========== TABS (NUR BASIS) ========== */
.stTabs button[role="tab"],
button[data-baseweb="tab"],
div[role="tablist"] button,
button[data-testid="stTab"] {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

/* ========== FILE UPLOADER (NUR BASIS) ========== */
section[data-testid="stFileUploadDropzone"] button,
.uploadedFile button,
div[data-testid="stFileUploader"] button {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

/* ========== DOWNLOAD BUTTON (NUR BASIS) ========== */
.stDownloadButton button,
button[data-testid="stDownloadButton"],
div[data-testid="stDownloadButton"] button {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

/* ========== FORM BUTTONS (NUR BASIS) ========== */
section[data-testid="stSidebar"] .stForm button[type="submit"],
[data-testid="stSidebar"] form button,
.stForm button[type="submit"],
form button[type="submit"] {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

/* ========== METRIC CONTAINERS (NUR BASIS) ========== */
div[data-testid="stMetric"],
div[data-testid="metric-container"],
div[class*="stMetric"] {
    transition: all 0.2s ease;
}

/* ========== DATAFRAME BUTTONS (NUR BASIS) ========== */
div[data-testid="stDataFrame"] button,
.dataframe-container button,
div[data-testid="stDataFrameResizable"] button {
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

/* ========== RADIO BUTTONS (NUR BASIS) ========== */
div[data-testid="stRadio"] label,
div[role="radiogroup"] label,
[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    transition: all 0.2s ease;
    cursor: pointer;
}

/* ========== MULTISELECT (NUR BASIS) ========== */
div[data-baseweb="tag"],
.stMultiSelect div[data-baseweb="tag"],
[data-testid="stSidebar"] div[data-baseweb="tag"] {
    transition: all 0.2s ease;
}

/* ========== SIDEBAR NAVIGATION & MENU (NUR BASIS) ========== */
/* Sidebar Container */
section[data-testid="stSidebar"],
.css-1d391kg,
div[data-testid="stSidebarNav"],
[data-testid="stSidebarContent"],
.st-emotion-cache-16idsys,
div[class*="st-emotion-cache"][class*="sidebar"] {
    transition: all 0.3s ease;
}

/* Sidebar Navigation Links - ALLE modernen Streamlit-Selektoren */
section[data-testid="stSidebar"] a,
[data-testid="stSidebar"] a[href],
section[data-testid="stSidebar"] nav a,
.sidebar-content a,
section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a,
[data-testid="stSidebar"] .stMarkdown a,
section[data-testid="stSidebar"] p a,
[data-testid="stSidebar"] span a {
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    display: block;
}

/* Sidebar Menu Items / List Items */
section[data-testid="stSidebar"] li,
[data-testid="stSidebar"] ul li,
section[data-testid="stSidebar"] ol li,
.sidebar-nav-link,
section[data-testid="stSidebar"] div[role="listitem"],
[data-testid="stSidebar"] .stMarkdown li {
    position: relative;
    transition: all 0.3s ease;
    cursor: pointer;
}

/* Sidebar Headers/Titles */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] h5,
section[data-testid="stSidebar"] h6,
[data-testid="stSidebar"] .sidebar-header,
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    transition: all 0.3s ease;
    cursor: default;
}

/* Sidebar Text Elements - clickbare Bereiche */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] div[class*="st-emotion-cache"] p {
    transition: all 0.2s ease;
}

/* Sidebar Dividers */
section[data-testid="stSidebar"] hr,
[data-testid="stSidebar"] .stDivider,
section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
    transition: all 0.3s ease;
}

/* Sidebar Images */
section[data-testid="stSidebar"] img,
[data-testid="stSidebar"] .stImage,
section[data-testid="stSidebar"] div[data-testid="stImage"] img {
    transition: all 0.3s ease;
}

/* Sidebar Icons */
section[data-testid="stSidebar"] svg,
[data-testid="stSidebar"] .stIcon {
    transition: all 0.2s ease;
}

/* Sidebar GESAMTER Content-Bereich */
section[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
    transition: all 0.2s ease;
}

/* ========== CAROUSEL KOMPONENTEN (NUR BASIS) ========== */
.admin-carousel-container,
.admin-carousel-wrapper,
.admin-carousel-cards,
.admin-carousel-card,
.admin-carousel-card.active,
.admin-carousel-icon,
.admin-carousel-title,
.admin-carousel-nav,
.admin-carousel-dot,
.admin-carousel-dot.active,
.admin-carousel-progress,
.admin-carousel-progress-bar,
.admin-carousel-legend,
.admin-carousel-actions,
.admin-carousel-actions button {
    position: relative;
    transition: all 0.3s ease;
}

.admin-carousel-card,
.admin-carousel-card.active {
    overflow: hidden;
}

.admin-carousel-nav button,
.admin-carousel-actions button {
    cursor: pointer;
}

.admin-carousel-dot {
    cursor: pointer;
}
"""

UI_EFFECTS_LIBRARY = {
    "shimmer_pulse": {
        "name": "Shimmer + Pulse",
        "description": "Glänzender Sweep-Effekt mit sanfter Puls-Animation. Elegant und modern.",
        "css": """
        /* SHIMMER + PULSE EFFEKT */
        /* Basis-Styling für alle Buttons */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* Shimmer-Effekt: Glänzender Sweep von links nach rechts */
        .stButton button::before,
        button[data-testid="baseButton-primary"]::before,
        button[data-testid="baseButton-secondary"]::before,
        button[kind="primary"]::before,
        button[kind="secondary"]::before,
        div[data-baseweb="button"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s ease;
            z-index: 1;
        }

        .stButton button:hover::before,
        button[data-testid="baseButton-primary"]:hover::before,
        button[data-testid="baseButton-secondary"]:hover::before,
        button[kind="primary"]:hover::before,
        button[kind="secondary"]:hover::before,
        div[data-baseweb="button"]:hover::before {
            left: 100%;
        }

        /* Hover-Effekte mit Transform */
        .stButton button:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-baseweb="button"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }

        /* Pulse-Animation */
        @keyframes globalButtonPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }

        button[data-testid="baseButton-primary"]:hover,
        button[kind="primary"]:hover {
            animation: globalButtonPulse 2s ease-in-out infinite;
        }

        /* ========== EXPANDER HOVER (SHIMMER + PULSE) ========== */
        details[data-testid="stExpander"] summary:hover,
        .streamlit-expanderHeader:hover,
        details summary:hover,
        section[data-testid="stSidebar"] details[data-testid="stExpander"] summary:hover,
        section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transform: translateX(2px) scale(1.01);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        /* ========== DROPDOWN HOVER (SHIMMER + PULSE) ========== */
        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.15);
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        }

        /* ========== NUMBER INPUT HOVER (SHIMMER + PULSE) ========== */
        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {
            transform: scale(1.08);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            animation: globalButtonPulse 1s ease-in-out;
        }

        /* ========== CHECKBOX HOVER (SHIMMER + PULSE) ========== */
        div[data-baseweb="checkbox"]:hover,
        div[data-testid="stCheckbox"] label:hover,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"]:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }

        /* ========== SIDEBAR NAVIGATION HOVER (SHIMMER + PULSE) ========== */
        /* Sidebar Links - ALLE Varianten */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] a[href]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a:hover,
        [data-testid="stSidebar"] .stMarkdown a:hover,
        section[data-testid="stSidebar"] p a:hover {
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transform: translateX(4px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding-left: 8px;
        }

        /* Sidebar List Items */
        section[data-testid="stSidebar"] li:hover,
        [data-testid="stSidebar"] ul li:hover,
        [data-testid="stSidebar"] .stMarkdown li:hover {
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
            transform: translateX(2px);
            padding-left: 4px;
        }

        /* Sidebar Headers Hover */
        section[data-testid="stSidebar"] h1:hover,
        section[data-testid="stSidebar"] h2:hover,
        section[data-testid="stSidebar"] h3:hover,
        [data-testid="stSidebar"] .stMarkdown h1:hover,
        [data-testid="stSidebar"] .stMarkdown h2:hover {
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
            transform: translateX(1px);
        }

        /* Sidebar Content Blocks Hover */
        section[data-testid="stSidebar"] > div:hover,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.02), transparent);
        }

        /* ========== CAROUSEL HOVER (SHIMMER + PULSE) ========== */
        .admin-carousel-card:hover,
        .admin-carousel-card.active {
            background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.02));
            box-shadow: 0 10px 25px rgba(0,0,0,0.18);
            transform: translateY(-4px) scale(1.01);
        }

        .admin-carousel-card:hover .admin-carousel-icon,
        .admin-carousel-card.active .admin-carousel-icon {
            animation: globalButtonPulse 1.8s ease-in-out infinite;
            filter: drop-shadow(0 6px 16px rgba(255,255,255,0.35));
        }

        .admin-carousel-nav button:hover {
            background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
            box-shadow: 0 6px 18px rgba(0,0,0,0.18);
            transform: translateY(-1px);
        }

        .admin-carousel-dot:hover,
        .admin-carousel-dot.active {
            background: linear-gradient(135deg, rgba(255,255,255,0.6), rgba(255,255,255,0.2));
            box-shadow: 0 0 10px rgba(255,255,255,0.6);
            transform: scale(1.25);
        }
        """
    },

    "glow_bounce": {
        "name": "Glow + Bounce",
        "description": "Leuchtender Glow-Effekt mit dynamischer Bounce-Animation. Energiegeladen und auffällig.",
        "css": """
        /* GLOW + BOUNCE EFFEKT */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            position: relative;
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            filter: drop-shadow(0 0 5px rgba(76, 175, 80, 0.3));
        }

        .stButton button:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-baseweb="button"]:hover {
            filter: drop-shadow(0 0 20px rgba(76, 175, 80, 0.8));
            animation: glowBounce 0.6s ease-in-out;
        }

        @keyframes glowBounce {
            0%, 100% { transform: translateY(0) scale(1); }
            25% { transform: translateY(-10px) scale(1.05); }
            50% { transform: translateY(-5px) scale(1.03); }
            75% { transform: translateY(-8px) scale(1.04); }
        }

        /* ========== EXPANDER HOVER (GLOW + BOUNCE) ========== */
        details[data-testid="stExpander"] summary:hover,
        .streamlit-expanderHeader:hover,
        details summary:hover,
        section[data-testid="stSidebar"] details[data-testid="stExpander"] summary:hover,
        section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.5);
            animation: glowPulse 1.5s ease-in-out infinite;
            transform: scale(1.01);
        }

        @keyframes glowPulse {
            0%, 100% { box-shadow: 0 0 10px rgba(76, 175, 80, 0.3); }
            50% { box-shadow: 0 0 20px rgba(76, 175, 80, 0.6); }
        }

        /* ========== DROPDOWN HOVER (GLOW + BOUNCE) ========== */
        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
            box-shadow: 0 0 12px rgba(76, 175, 80, 0.4);
            animation: glowBounce 0.6s ease-in-out;
        }

        /* ========== NUMBER INPUT HOVER (GLOW + BOUNCE) ========== */
        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {
            filter: drop-shadow(0 0 10px rgba(76, 175, 80, 0.7));
            animation: glowBounce 0.6s ease-in-out;
        }

        /* ========== CHECKBOX HOVER (GLOW + BOUNCE) ========== */
        div[data-baseweb="checkbox"]:hover,
        div[data-testid="stCheckbox"] label:hover,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"]:hover {
            filter: drop-shadow(0 0 8px rgba(76, 175, 80, 0.6));
        }

        /* ========== SIDEBAR NAVIGATION HOVER (GLOW + BOUNCE) ========== */
        /* Sidebar Links - ALLE Varianten */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] a[href]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a:hover,
        [data-testid="stSidebar"] .stMarkdown a:hover,
        section[data-testid="stSidebar"] p a:hover {
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.5);
            animation: glowPulse 1.5s ease-in-out infinite;
            transform: translateX(3px);
            padding-left: 8px;
        }

        /* Sidebar List Items */
        section[data-testid="stSidebar"] li:hover,
        [data-testid="stSidebar"] ul li:hover,
        [data-testid="stSidebar"] .stMarkdown li:hover {
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
            animation: glowBounce 0.6s ease-in-out;
            padding-left: 4px;
        }

        /* Sidebar Headers Hover */
        section[data-testid="stSidebar"] h1:hover,
        section[data-testid="stSidebar"] h2:hover,
        section[data-testid="stSidebar"] h3:hover,
        [data-testid="stSidebar"] .stMarkdown h1:hover,
        [data-testid="stSidebar"] .stMarkdown h2:hover {
            box-shadow: 0 0 8px rgba(76, 175, 80, 0.2);
            transform: translateX(1px);
        }

        /* Sidebar Content Blocks Hover */
        section[data-testid="stSidebar"] > div:hover,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
            box-shadow: 0 0 5px rgba(76, 175, 80, 0.1);
        }

        /* ========== CAROUSEL HOVER (GLOW + BOUNCE) ========== */
        .admin-carousel-card:hover,
        .admin-carousel-card.active {
            box-shadow: 0 0 25px rgba(76, 175, 80, 0.55);
            border: 1px solid rgba(76, 175, 80, 0.4);
            transform: translateY(-4px) scale(1.02);
            animation: glowPulse 1.6s ease-in-out infinite;
        }

        .admin-carousel-card:hover .admin-carousel-icon,
        .admin-carousel-card.active .admin-carousel-icon {
            filter: drop-shadow(0 0 18px rgba(76, 175, 80, 0.6));
            animation: glowBounce 0.6s ease-in-out;
        }

        .admin-carousel-nav button:hover {
            box-shadow: 0 0 20px rgba(76, 175, 80, 0.45);
            transform: translateY(-2px) scale(1.05);
        }

        .admin-carousel-dot:hover,
        .admin-carousel-dot.active {
            background: rgba(76, 175, 80, 0.85);
            box-shadow: 0 0 14px rgba(76, 175, 80, 0.8);
            transform: scale(1.3);
        }
        """
    },

    "neon_wave": {
        "name": "Neon + Wave",
        "description": "Intensiver Neon-Glow mit wellenförmiger Bewegung. Futuristisch und dynamisch.",
        "css": """
        /* NEON + WAVE EFFEKT */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            position: relative;
            border: 2px solid rgba(0, 255, 255, 0.5) !important;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.3),
                        inset 0 0 10px rgba(0, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .stButton button:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-baseweb="button"]:hover {
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.8),
                        inset 0 0 20px rgba(0, 255, 255, 0.3);
            animation: neonWave 1.5s ease-in-out infinite;
        }

        @keyframes neonWave {
            0%, 100% {
                transform: translateX(0) skewX(0deg);
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.8);
            }
            25% {
                transform: translateX(2px) skewX(2deg);
                box-shadow: 0 0 30px rgba(0, 255, 255, 1);
            }
            50% {
                transform: translateX(0) skewX(0deg);
                box-shadow: 0 0 25px rgba(0, 255, 255, 0.9);
            }
            75% {
                transform: translateX(-2px) skewX(-2deg);
                box-shadow: 0 0 30px rgba(0, 255, 255, 1);
            }
        }

        /* ========== EXPANDER HOVER (NEON + WAVE) ========== */
        details[data-testid="stExpander"] summary,
        .streamlit-expanderHeader,
        details summary,
        section[data-testid="stSidebar"] details[data-testid="stExpander"] summary,
        section[data-testid="stSidebar"] .streamlit-expanderHeader {
            border-left: 3px solid rgba(0, 255, 255, 0.5);
        }

        details[data-testid="stExpander"] summary:hover,
        .streamlit-expanderHeader:hover,
        details summary:hover,
        section[data-testid="stSidebar"] details[data-testid="stExpander"] summary:hover,
        section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
            border-left: 3px solid rgba(0, 255, 255, 1);
            box-shadow: -5px 0 15px rgba(0, 255, 255, 0.5);
            animation: neonPulse 1s ease-in-out infinite;
        }

        /* ========== DROPDOWN HOVER (NEON + WAVE) ========== */
        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
            border: 1px solid rgba(0, 255, 255, 1);
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.6);
        }

        /* ========== NUMBER INPUT HOVER (NEON + WAVE) ========== */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"] {
            border: 1px solid rgba(0, 255, 255, 0.5) !important;
        }

        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.8);
            animation: neonPulse 1s ease-in-out infinite;
        }

        @keyframes neonPulse {
            0%, 100% { box-shadow: 0 0 10px rgba(0, 255, 255, 0.5); }
            50% { box-shadow: 0 0 20px rgba(0, 255, 255, 1); }
        }

        /* ========== SIDEBAR NAVIGATION HOVER (NEON + WAVE) ========== */
        /* Sidebar Links - ALLE Varianten */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] a[href]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a:hover,
        [data-testid="stSidebar"] .stMarkdown a:hover,
        section[data-testid="stSidebar"] p a:hover {
            border-left: 3px solid rgba(0, 255, 255, 1);
            box-shadow: -5px 0 15px rgba(0, 255, 255, 0.6);
            animation: neonPulse 1s ease-in-out infinite;
            padding-left: 12px;
        }

        /* Sidebar List Items */
        section[data-testid="stSidebar"] li:hover,
        [data-testid="stSidebar"] ul li:hover,
        [data-testid="stSidebar"] .stMarkdown li:hover {
            border-left: 2px solid rgba(0, 255, 255, 0.8);
            box-shadow: -3px 0 10px rgba(0, 255, 255, 0.4);
            padding-left: 8px;
        }

        /* Sidebar Headers Hover */
        section[data-testid="stSidebar"] h1:hover,
        section[data-testid="stSidebar"] h2:hover,
        section[data-testid="stSidebar"] h3:hover,
        [data-testid="stSidebar"] .stMarkdown h1:hover,
        [data-testid="stSidebar"] .stMarkdown h2:hover {
            border-left: 2px solid rgba(0, 255, 255, 0.6);
            box-shadow: -2px 0 8px rgba(0, 255, 255, 0.3);
            padding-left: 6px;
        }

        /* Sidebar Content Blocks Hover */
        section[data-testid="stSidebar"] > div:hover,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
            border-left: 1px solid rgba(0, 255, 255, 0.3);
            box-shadow: -1px 0 5px rgba(0, 255, 255, 0.2);
        }

        /* ========== CAROUSEL HOVER (NEON + WAVE) ========== */
        .admin-carousel-card:hover,
        .admin-carousel-card.active {
            border: 2px solid rgba(0, 255, 255, 0.85);
            box-shadow: 0 0 28px rgba(0, 255, 255, 0.7);
            transform: translateY(-4px) scale(1.03);
            animation: neonPulse 1.2s ease-in-out infinite;
        }

        .admin-carousel-card:hover .admin-carousel-icon,
        .admin-carousel-card.active .admin-carousel-icon {
            filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.9));
        }

        .admin-carousel-nav button:hover {
            border: 1px solid rgba(0, 255, 255, 0.8);
            box-shadow: 0 0 18px rgba(0, 255, 255, 0.7);
            transform: translateY(-2px) scale(1.05);
        }

        .admin-carousel-dot:hover,
        .admin-carousel-dot.active {
            background: rgba(0, 255, 255, 0.9);
            box-shadow: 0 0 16px rgba(0, 255, 255, 0.9);
            transform: scale(1.35);
        }
        """
    },

    "gradient_slide": {
        "name": "Gradient + Slide",
        "description": "Fließender Farbverlauf mit gleitender Bewegung. Smooth und professionell.",
        "css": """
        /* GRADIENT + SLIDE EFFEKT */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            position: relative;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
            background-size: 200% 100%;
            transition: all 0.4s ease;
        }

        .stButton button:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-baseweb="button"]:hover {
            background-position: 100% 0;
            transform: translateX(5px);
            box-shadow: -5px 5px 20px rgba(102, 126, 234, 0.4);
        }

        /* Expander Gradient */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, transparent 0%, rgba(102, 126, 234, 0.1) 100%);
            background-size: 200% 100%;
            background-position: 0% 0;
            transition: all 0.4s ease;
        }

        /* ========== EXPANDER HOVER (GRADIENT + SLIDE) ========== */
        details[data-testid="stExpander"] summary:hover,
        .streamlit-expanderHeader:hover,
        details summary:hover,
        section[data-testid="stSidebar"] details[data-testid="stExpander"] summary:hover,
        section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
            background-position: 100% 0;
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        /* ========== DROPDOWN HOVER (GRADIENT + SLIDE) ========== */
        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
            background: linear-gradient(90deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
            transform: translateX(3px);
            box-shadow: 0 4px 10px rgba(102, 126, 234, 0.2);
        }

        /* ========== NUMBER INPUT HOVER (GRADIENT + SLIDE) ========== */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            transition: all 0.3s ease;
        }

        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
            transform: scale(1.1);
        }

        /* ========== CHECKBOX HOVER (GRADIENT + SLIDE) ========== */
        div[data-baseweb="checkbox"]:hover,
        div[data-testid="stCheckbox"] label:hover,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"]:hover {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
            border-radius: 4px;
            transform: scale(1.05);
        }

        /* ========== SIDEBAR NAVIGATION HOVER (GRADIENT + SLIDE) ========== */
        /* Sidebar Links - ALLE Varianten */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] a[href]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a:hover,
        [data-testid="stSidebar"] .stMarkdown a:hover,
        section[data-testid="stSidebar"] p a:hover {
            background: linear-gradient(90deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            padding-left: 10px;
        }

        /* Sidebar List Items */
        section[data-testid="stSidebar"] li:hover,
        [data-testid="stSidebar"] ul li:hover,
        [data-testid="stSidebar"] .stMarkdown li:hover {
            background: linear-gradient(90deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
            transform: translateX(3px);
            padding-left: 6px;
        }

        /* Sidebar Headers Hover */
        section[data-testid="stSidebar"] h1:hover,
        section[data-testid="stSidebar"] h2:hover,
        section[data-testid="stSidebar"] h3:hover,
        [data-testid="stSidebar"] .stMarkdown h1:hover,
        [data-testid="stSidebar"] .stMarkdown h2:hover {
            background: linear-gradient(90deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            transform: translateX(2px);
            padding-left: 4px;
        }

        /* Sidebar Content Blocks Hover */
        section[data-testid="stSidebar"] > div:hover,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
            background: linear-gradient(90deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
        }

        /* ========== CAROUSEL HOVER (GRADIENT + SLIDE) ========== */
        .admin-carousel-card:hover,
        .admin-carousel-card.active {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.25), rgba(118, 75, 162, 0.25));
            box-shadow: 0 14px 32px rgba(102, 126, 234, 0.35);
            transform: translateY(-5px) scale(1.03);
        }

        .admin-carousel-card:hover .admin-carousel-icon,
        .admin-carousel-card.active .admin-carousel-icon {
            background: linear-gradient(135deg, rgba(255,255,255,0.45), rgba(255,255,255,0.05));
            box-shadow: 0 8px 20px rgba(118, 75, 162, 0.3);
            transform: translateY(-3px);
        }

        .admin-carousel-nav button:hover {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
            box-shadow: 0 12px 26px rgba(102, 126, 234, 0.32);
            transform: translateY(-2px) scale(1.05);
        }

        .admin-carousel-dot:hover,
        .admin-carousel-dot.active {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
            box-shadow: 0 0 18px rgba(118, 75, 162, 0.6);
            transform: scale(1.35);
        }
        """
    },

    "glass_morph": {
        "name": "Glass + Morph",
        "description": "Glasmorphismus-Effekt mit organischer Morphing-Animation. Modern und elegant.",
        "css": """
        /* GLASS + MORPH EFFEKT */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .stButton button:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-baseweb="button"]:hover {
            background: rgba(255, 255, 255, 0.2) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            animation: glassMorph 0.8s ease-in-out;
        }

        @keyframes glassMorph {
            0%, 100% { border-radius: 8px; }
            25% { border-radius: 12px 8px 12px 8px; }
            50% { border-radius: 8px 12px 8px 12px; }
            75% { border-radius: 12px 8px 12px 8px; }
        }

        /* Expander Glass */
        .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .streamlit-expanderHeader:hover {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Slider Glass */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"] {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }

        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {
            background: rgba(255, 255, 255, 0.2) !important;
            backdrop-filter: blur(15px);
        }

        /* Checkbox Glass */
        div[data-baseweb="checkbox"],
        div[data-testid="stCheckbox"] label,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"],
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label {
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(6px);
            border-radius: 6px;
        }

        div[data-baseweb="checkbox"]:hover,
        div[data-testid="stCheckbox"] label:hover,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"]:hover,
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label:hover {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(12px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
        }

        /* Dropdown Glass */
        div[data-baseweb="select"],
        .stSelectbox > div > div,
        div[data-testid="stSelectbox"] > div,
        section[data-testid="stSidebar"] div[data-baseweb="select"],
        section[data-testid="stSidebar"] .stSelectbox > div > div {
            transition: all 0.4s ease;
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
            background: rgba(255, 255, 255, 0.16);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.28);
            box-shadow: 0 18px 32px rgba(0, 0, 0, 0.2);
        }

        /* Sidebar Navigation Hover (Glass + Morph) */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] a[href]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a:hover,
        [data-testid="stSidebar"] .stMarkdown a:hover,
        section[data-testid="stSidebar"] p a:hover {
            background: rgba(255, 255, 255, 0.18);
            backdrop-filter: blur(14px);
            border-radius: 8px;
            transform: translateX(4px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18);
            padding-left: 10px;
        }

        section[data-testid="stSidebar"] li:hover,
        [data-testid="stSidebar"] ul li:hover,
        [data-testid="stSidebar"] .stMarkdown li:hover {
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            border-radius: 6px;
            padding-left: 8px;
        }

        section[data-testid="stSidebar"] h1:hover,
        section[data-testid="stSidebar"] h2:hover,
        section[data-testid="stSidebar"] h3:hover,
        [data-testid="stSidebar"] .stMarkdown h1:hover,
        [data-testid="stSidebar"] .stMarkdown h2:hover {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            transform: translateX(2px);
            padding-left: 6px;
            border-radius: 4px;
        }

        section[data-testid="stSidebar"] > div:hover,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
            background: rgba(255, 255, 255, 0.06);
            backdrop-filter: blur(6px);
        }

        /* ========== CAROUSEL HOVER (GLASS + MORPH) ========== */
        .admin-carousel-card:hover,
        .admin-carousel-card.active {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(18px);
            border: 1px solid rgba(255, 255, 255, 0.28);
            box-shadow: 0 20px 36px rgba(0, 0, 0, 0.24);
            transform: translateY(-4px) scale(1.02);
        }

        .admin-carousel-card:hover .admin-carousel-icon,
        .admin-carousel-card.active .admin-carousel-icon {
            background: rgba(255, 255, 255, 0.24);
            backdrop-filter: blur(22px);
            border-radius: 18px;
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.22);
        }

        .admin-carousel-nav button:hover,
        .admin-carousel-actions button:hover {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(14px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
            transform: translateY(-2px);
        }

        .admin-carousel-dot:hover,
        .admin-carousel-dot.active {
            background: rgba(255, 255, 255, 0.85);
            box-shadow: 0 0 18px rgba(255, 255, 255, 0.7);
            transform: scale(1.28);
        }
        """
    },

    "minimal_fade": {
        "name": "Minimal + Fade",
        "description": "Minimalistischer Stil mit sanften Fade-Übergängen. Dezent und professionell.",
        "css": """
        /* MINIMAL + FADE EFFEKT */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            transition: all 0.3s ease;
            opacity: 0.9;
        }

        .stButton button:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-baseweb="button"]:hover {
            opacity: 1;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        /* Expander Minimal */
        .streamlit-expanderHeader {
            transition: all 0.3s ease;
            opacity: 0.85;
        }

        .streamlit-expanderHeader:hover {
            opacity: 1;
            background-color: rgba(255, 255, 255, 0.03);
        }

        /* Slider Minimal */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"] {
            transition: opacity 0.3s ease;
            opacity: 0.8;
        }

        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {
            opacity: 1;
        }

        /* Checkbox Minimal */
        div[data-baseweb="checkbox"],
        div[data-testid="stCheckbox"] label,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"],
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label {
            transition: opacity 0.2s ease;
            opacity: 0.9;
        }

        div[data-baseweb="checkbox"]:hover,
        div[data-testid="stCheckbox"] label:hover,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"]:hover,
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label:hover {
            opacity: 1;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        }

        /* Dropdown Minimal */
        div[data-baseweb="select"],
        .stSelectbox > div > div,
        div[data-testid="stSelectbox"] > div,
        section[data-testid="stSidebar"] div[data-baseweb="select"],
        section[data-testid="stSidebar"] .stSelectbox > div > div {
            transition: all 0.25s ease;
            background-color: rgba(255, 255, 255, 0.04);
            border-radius: 6px;
        }

        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
            background-color: rgba(255, 255, 255, 0.07);
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
        }

        /* Sidebar Navigation Hover (Minimal + Fade) */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] a[href]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a:hover,
        [data-testid="stSidebar"] .stMarkdown a:hover,
        section[data-testid="stSidebar"] p a:hover {
            background-color: rgba(255, 255, 255, 0.06);
            border-radius: 6px;
            transform: translateX(3px);
            box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
            padding-left: 8px;
        }

        section[data-testid="stSidebar"] li:hover,
        [data-testid="stSidebar"] ul li:hover,
        [data-testid="stSidebar"] .stMarkdown li:hover {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            padding-left: 6px;
        }

        section[data-testid="stSidebar"] h1:hover,
        section[data-testid="stSidebar"] h2:hover,
        section[data-testid="stSidebar"] h3:hover,
        [data-testid="stSidebar"] .stMarkdown h1:hover,
        [data-testid="stSidebar"] .stMarkdown h2:hover {
            background-color: rgba(255, 255, 255, 0.04);
            border-radius: 4px;
            transform: translateX(2px);
            padding-left: 5px;
        }

        section[data-testid="stSidebar"] > div:hover,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
            background-color: rgba(255, 255, 255, 0.03);
        }

        /* ========== CAROUSEL HOVER (MINIMAL + FADE) ========== */
        .admin-carousel-card:hover,
        .admin-carousel-card.active {
            background-color: rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
            transform: translateY(-3px) scale(1.01);
        }

        .admin-carousel-card:hover .admin-carousel-icon,
        .admin-carousel-card.active .admin-carousel-icon {
            opacity: 1;
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.12);
            transform: translateY(-2px);
        }

        .admin-carousel-nav button:hover,
        .admin-carousel-actions button:hover {
            background-color: rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }

        .admin-carousel-dot:hover,
        .admin-carousel-dot.active {
            background-color: rgba(255, 255, 255, 0.8);
            box-shadow: 0 0 12px rgba(0, 0, 0, 0.1);
            transform: scale(1.2);
        }
        """
    },

    "retro_pixel": {
        "name": "Retro + Pixel",
        "description": "Retro-Gaming-Stil mit pixeliger Animation. Nostalgisch und verspielt.",
        "css": """
        /* RETRO + PIXEL EFFEKT */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            border: 3px solid currentColor !important;
            box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.2);
            transition: all 0.1s ease;
            image-rendering: pixelated;
        }

        .stButton button:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-baseweb="button"]:hover {
            transform: translate(2px, 2px);
            box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.2);
            animation: pixelShake 0.3s ease-in-out;
        }

        @keyframes pixelShake {
            0%, 100% { transform: translate(2px, 2px); }
            25% { transform: translate(0px, 2px); }
            50% { transform: translate(2px, 0px); }
            75% { transform: translate(0px, 0px); }
        }

        /* Expander Retro */
        .streamlit-expanderHeader {
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 3px 3px 0 rgba(0, 0, 0, 0.1);
            transition: all 0.1s ease;
        }

        .streamlit-expanderHeader:hover {
            transform: translate(1px, 1px);
            box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.1);
        }

        /* Slider Retro */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"] {
            border: 2px solid currentColor !important;
            box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.2);
        }

        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {
            transform: translate(1px, 1px);
            box-shadow: 1px 1px 0 rgba(0, 0, 0, 0.2);
        }

        /* Dropdown Retro */
        div[data-baseweb="select"],
        .stSelectbox > div > div,
        div[data-testid="stSelectbox"] > div,
        section[data-testid="stSidebar"] div[data-baseweb="select"],
        section[data-testid="stSidebar"] .stSelectbox > div > div {
            border: 2px solid currentColor;
            box-shadow: 3px 3px 0 rgba(0, 0, 0, 0.25);
            transition: all 0.12s ease;
            image-rendering: pixelated;
        }

        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
            transform: translate(1px, 1px);
            box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.2);
        }

        /* Checkbox Retro */
        div[data-baseweb="checkbox"],
        div[data-testid="stCheckbox"] label,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"],
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label {
            border: 2px solid currentColor;
            box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.2);
            transition: all 0.12s ease;
        }

        div[data-baseweb="checkbox"]:hover,
        div[data-testid="stCheckbox"] label:hover,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"]:hover,
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label:hover {
            transform: translate(1px, 1px);
            box-shadow: 1px 1px 0 rgba(0, 0, 0, 0.2);
        }

        /* Sidebar Navigation Hover (Retro + Pixel) */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] a[href]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a:hover,
        [data-testid="stSidebar"] .stMarkdown a:hover,
        section[data-testid="stSidebar"] p a:hover {
            border: 2px solid currentColor;
            box-shadow: 3px 3px 0 rgba(0, 0, 0, 0.25);
            transform: translate(2px, 2px);
            padding-left: 8px;
            image-rendering: pixelated;
        }

        section[data-testid="stSidebar"] li:hover,
        [data-testid="stSidebar"] ul li:hover,
        [data-testid="stSidebar"] .stMarkdown li:hover {
            border: 2px solid currentColor;
            box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.2);
            transform: translate(1px, 1px);
            padding-left: 6px;
        }

        section[data-testid="stSidebar"] h1:hover,
        section[data-testid="stSidebar"] h2:hover,
        section[data-testid="stSidebar"] h3:hover,
        [data-testid="stSidebar"] .stMarkdown h1:hover,
        [data-testid="stSidebar"] .stMarkdown h2:hover {
            border: 2px solid currentColor;
            box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.18);
            transform: translate(1px, 1px);
            padding-left: 5px;
        }

        section[data-testid="stSidebar"] > div:hover,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
            border: 2px solid rgba(255, 255, 255, 0.2);
            box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.15);
        }

        /* ========== CAROUSEL HOVER (RETRO + PIXEL) ========== */
        .admin-carousel-card:hover,
        .admin-carousel-card.active {
            border: 3px solid currentColor;
            box-shadow: 6px 6px 0 rgba(0, 0, 0, 0.35);
            transform: translate(-3px, -3px) scale(1.02);
            image-rendering: pixelated;
        }

        .admin-carousel-card:hover .admin-carousel-icon,
        .admin-carousel-card.active .admin-carousel-icon {
            box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.28);
            transform: translate(2px, 2px);
        }

        .admin-carousel-nav button:hover,
        .admin-carousel-actions button:hover {
            border: 2px solid currentColor;
            box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.28);
            transform: translate(2px, 2px);
        }

        .admin-carousel-dot:hover,
        .admin-carousel-dot.active {
            transform: scale(1.3);
            box-shadow: 0 0 0 2px currentColor, 3px 3px 0 rgba(0, 0, 0, 0.3);
        }
        """
    },

    "rainbow_spin": {
        "name": "Rainbow + Spin",
        "description": "Regenbogen-Farbverlauf mit rotierender Bewegung. Bunt und energiegeladen.",
        "css": """
        /* RAINBOW + SPIN EFFEKT */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            position: relative;
            background: linear-gradient(90deg,
                #ff0000 0%, #ff7f00 16.67%, #ffff00 33.33%,
                #00ff00 50%, #0000ff 66.67%, #4b0082 83.33%,
                #9400d3 100%) !important;
            background-size: 200% 100%;
            animation: rainbowFlow 3s linear infinite;
            transition: all 0.3s ease;
        }

        @keyframes rainbowFlow {
            0% { background-position: 0% 50%; }
            100% { background-position: 200% 50%; }
        }

        .stButton button:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-baseweb="button"]:hover {
            animation: rainbowFlow 1s linear infinite, rainbowSpin 0.6s ease-in-out;
        }

        @keyframes rainbowSpin {
            0% { transform: rotate(0deg) scale(1); }
            50% { transform: rotate(5deg) scale(1.05); }
            100% { transform: rotate(0deg) scale(1); }
        }

        /* Expander Rainbow */
        .streamlit-expanderHeader {
            border-left: 4px solid transparent;
            border-image: linear-gradient(180deg,
                #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3) 1;
            transition: all 0.3s ease;
        }

        .streamlit-expanderHeader:hover {
            border-left-width: 6px;
            animation: rainbowBorder 2s linear infinite;
        }

        @keyframes rainbowBorder {
            0%, 100% { filter: hue-rotate(0deg); }
            50% { filter: hue-rotate(180deg); }
        }

        /* Slider Rainbow */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"] {
            background: linear-gradient(135deg,
                #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff) !important;
            background-size: 200% 200%;
            animation: rainbowFlow 2s ease infinite;
        }

        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {
            animation: rainbowFlow 1s ease infinite, rainbowSpin 0.6s ease-in-out;
            transform: translateY(-1px);
        }

        /* Dropdown Rainbow */
        div[data-baseweb="select"],
        .stSelectbox > div > div,
        div[data-testid="stSelectbox"] > div,
        section[data-testid="stSidebar"] div[data-baseweb="select"],
        section[data-testid="stSidebar"] .stSelectbox > div > div {
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease;
        }

        div[data-baseweb="select"]::before,
        .stSelectbox > div > div::before,
        div[data-testid="stSelectbox"] > div::before,
        section[data-testid="stSidebar"] div[data-baseweb="select"]::before,
        section[data-testid="stSidebar"] .stSelectbox > div > div::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(120deg,
                rgba(255,0,0,0.25), rgba(255,127,0,0.25), rgba(255,255,0,0.25),
                rgba(0,255,0,0.25), rgba(0,0,255,0.25), rgba(75,0,130,0.25), rgba(148,0,211,0.25));
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(148, 0, 211, 0.25);
        }

        div[data-baseweb="select"]:hover::before,
        .stSelectbox > div > div:hover::before,
        div[data-testid="stSelectbox"] > div:hover::before,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover::before,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover::before {
            opacity: 1;
        }

        /* Checkbox Rainbow */
        div[data-baseweb="checkbox"],
        div[data-testid="stCheckbox"] label,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"],
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label {
            transition: transform 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        div[data-baseweb="checkbox"]:hover,
        div[data-testid="stCheckbox"] label:hover,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"]:hover,
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label:hover {
            transform: translateY(-1px) scale(1.02);
            box-shadow: 0 10px 20px rgba(148, 0, 211, 0.25);
        }

        /* Sidebar Navigation Hover (Rainbow + Spin) */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] a[href]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a:hover,
        [data-testid="stSidebar"] .stMarkdown a:hover,
        section[data-testid="stSidebar"] p a:hover {
            background: linear-gradient(90deg, rgba(255,0,0,0.25), rgba(0,0,255,0.25));
            box-shadow: 0 10px 24px rgba(148, 0, 211, 0.25);
            transform: translateX(4px);
            padding-left: 10px;
        }

        section[data-testid="stSidebar"] li:hover,
        [data-testid="stSidebar"] ul li:hover,
        [data-testid="stSidebar"] .stMarkdown li:hover {
            background: linear-gradient(90deg, rgba(255,127,0,0.2), rgba(0,255,0,0.2));
            transform: translateX(3px);
            padding-left: 8px;
        }

        section[data-testid="stSidebar"] h1:hover,
        section[data-testid="stSidebar"] h2:hover,
        section[data-testid="stSidebar"] h3:hover,
        [data-testid="stSidebar"] .stMarkdown h1:hover,
        [data-testid="stSidebar"] .stMarkdown h2:hover {
            background: linear-gradient(90deg, rgba(0,0,255,0.2), rgba(148,0,211,0.2));
            transform: translateX(2px);
            padding-left: 6px;
        }

        section[data-testid="stSidebar"] > div:hover,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
            background: linear-gradient(120deg, rgba(255,0,0,0.12), rgba(148,0,211,0.12));
        }

        /* ========== CAROUSEL HOVER (RAINBOW + SPIN) ========== */
        .admin-carousel-card:hover,
        .admin-carousel-card.active {
            background: linear-gradient(135deg,
                rgba(255,0,0,0.35), rgba(255,127,0,0.35), rgba(255,255,0,0.35),
                rgba(0,255,0,0.35), rgba(0,0,255,0.35), rgba(75,0,130,0.35), rgba(148,0,211,0.35));
            box-shadow: 0 18px 36px rgba(148, 0, 211, 0.3);
            transform: translateY(-5px) scale(1.03);
            animation: rainbowSpin 0.8s ease-in-out;
        }

        .admin-carousel-card:hover .admin-carousel-icon,
        .admin-carousel-card.active .admin-carousel-icon {
            animation: rainbowSpin 0.6s ease-in-out;
            filter: drop-shadow(0 10px 24px rgba(148, 0, 211, 0.35));
        }

        .admin-carousel-nav button:hover,
        .admin-carousel-actions button:hover {
            background: linear-gradient(135deg, rgba(255,0,0,0.45), rgba(0,0,255,0.45));
            box-shadow: 0 14px 28px rgba(148, 0, 211, 0.35);
            transform: translateY(-2px) scale(1.05);
        }

        .admin-carousel-dot:hover,
        .admin-carousel-dot.active {
            background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(148,0,211,0.9));
            box-shadow: 0 0 20px rgba(148, 0, 211, 0.5);
            transform: scale(1.35);
        }
        """
    },

    "cyberpunk_glitch": {
        "name": "Cyberpunk + Glitch",
        "description": "Cyberpunk-Stil mit digitalem Glitch-Effekt. Futuristisch und kantig.",
        "css": """
        /* CYBERPUNK + GLITCH EFFEKT */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            position: relative;
            background: linear-gradient(135deg, #ff00ff 0%, #00ffff 100%) !important;
            border: 2px solid #ff00ff !important;
            box-shadow: 0 0 10px #ff00ff, inset 0 0 10px rgba(255, 0, 255, 0.2);
            transition: all 0.2s ease;
            clip-path: polygon(0 0, 100% 0, 100% 90%, 95% 100%, 0 100%);
        }

        .stButton button:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-baseweb="button"]:hover {
            animation: cyberGlitch 0.3s ease-in-out;
            box-shadow: 0 0 20px #ff00ff, 0 0 30px #00ffff, inset 0 0 20px rgba(255, 0, 255, 0.3);
        }

        @keyframes cyberGlitch {
            0%, 100% {
                transform: translate(0, 0) skew(0deg);
                filter: hue-rotate(0deg);
            }
            10% {
                transform: translate(-2px, -2px) skew(-2deg);
                filter: hue-rotate(90deg);
            }
            20% {
                transform: translate(2px, 2px) skew(2deg);
                filter: hue-rotate(-90deg);
            }
            30% {
                transform: translate(-1px, 1px) skew(1deg);
                filter: hue-rotate(45deg);
            }
            40% {
                transform: translate(1px, -1px) skew(-1deg);
                filter: hue-rotate(-45deg);
            }
        }

        /* Expander Cyberpunk */
        .streamlit-expanderHeader {
            border-left: 3px solid #ff00ff;
            box-shadow: -3px 0 10px rgba(255, 0, 255, 0.3);
            clip-path: polygon(0 0, 100% 0, 100% 85%, 98% 100%, 0 100%);
            transition: all 0.2s ease;
        }

        .streamlit-expanderHeader:hover {
            border-left: 3px solid #00ffff;
            box-shadow: -5px 0 15px rgba(0, 255, 255, 0.5);
            animation: cyberGlitch 0.3s ease-in-out;
        }

        /* Slider Cyberpunk */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"] {
            background: linear-gradient(135deg, #ff00ff, #00ffff) !important;
            border: 1px solid #ff00ff !important;
            box-shadow: 0 0 5px #ff00ff;
        }

        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {
            animation: cyberGlitch 0.2s ease-in-out;
            box-shadow: 0 0 10px #ff00ff, 0 0 15px #00ffff;
        }

        /* Dropdown Cyberpunk */
        div[data-baseweb="select"],
        .stSelectbox > div > div,
        div[data-testid="stSelectbox"] > div,
        section[data-testid="stSidebar"] div[data-baseweb="select"],
        section[data-testid="stSidebar"] .stSelectbox > div > div {
            position: relative;
            border: 2px solid #ff00ff;
            box-shadow: 0 0 10px rgba(255, 0, 255, 0.45);
            transition: transform 0.2s ease;
            clip-path: polygon(0 0, 100% 0, 100% 90%, 95% 100%, 0 100%);
        }

        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
            transform: translate(-2px, -2px);
            border-color: #00ffff;
            box-shadow: 0 0 18px #ff00ff, 0 0 25px #00ffff;
            animation: cyberGlitch 0.3s ease-in-out;
        }

        /* Checkbox Cyberpunk */
        div[data-baseweb="checkbox"],
        div[data-testid="stCheckbox"] label,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"],
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label {
            border: 2px solid #ff00ff;
            box-shadow: 0 0 8px rgba(255, 0, 255, 0.4);
            transition: all 0.2s ease;
            clip-path: polygon(0 0, 100% 0, 100% 85%, 96% 100%, 0 100%);
        }

        div[data-baseweb="checkbox"]:hover,
        div[data-testid="stCheckbox"] label:hover,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"]:hover,
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label:hover {
            border-color: #00ffff;
            box-shadow: 0 0 16px #ff00ff, 0 0 20px #00ffff;
            animation: cyberGlitch 0.3s ease-in-out;
        }

        /* Sidebar Navigation Hover (Cyberpunk + Glitch) */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] a[href]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a:hover,
        [data-testid="stSidebar"] .stMarkdown a:hover,
        section[data-testid="stSidebar"] p a:hover {
            border-left: 3px solid #ff00ff;
            box-shadow: -6px 0 20px rgba(255, 0, 255, 0.4);
            transform: translateX(4px) skewX(-2deg);
            padding-left: 10px;
            animation: cyberGlitch 0.35s ease-in-out;
        }

        section[data-testid="stSidebar"] li:hover,
        [data-testid="stSidebar"] ul li:hover,
        [data-testid="stSidebar"] .stMarkdown li:hover {
            border-left: 3px solid #00ffff;
            box-shadow: -4px 0 14px rgba(0, 255, 255, 0.35);
            transform: translateX(2px) skewX(-1deg);
            padding-left: 8px;
        }

        section[data-testid="stSidebar"] h1:hover,
        section[data-testid="stSidebar"] h2:hover,
        section[data-testid="stSidebar"] h3:hover,
        [data-testid="stSidebar"] .stMarkdown h1:hover,
        [data-testid="stSidebar"] .stMarkdown h2:hover {
            border-left: 3px solid #ff00ff;
            box-shadow: -4px 0 16px rgba(255, 0, 255, 0.35);
            transform: translateX(2px) skewX(-1deg);
            padding-left: 6px;
        }

        section[data-testid="stSidebar"] > div:hover,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
            border-left: 2px solid rgba(255, 0, 255, 0.35);
            box-shadow: -4px 0 14px rgba(255, 0, 255, 0.25);
        }

        /* ========== CAROUSEL HOVER (CYBERPUNK + GLITCH) ========== */
        .admin-carousel-card:hover,
        .admin-carousel-card.active {
            background: linear-gradient(135deg, rgba(255, 0, 255, 0.25), rgba(0, 255, 255, 0.15));
            border: 2px solid #ff00ff;
            box-shadow: 0 0 35px rgba(255, 0, 255, 0.45), 0 0 26px rgba(0, 255, 255, 0.35);
            transform: translateY(-4px) skewX(-1deg) scale(1.02);
            animation: cyberGlitch 0.35s ease-in-out;
        }

        .admin-carousel-card:hover .admin-carousel-icon,
        .admin-carousel-card.active .admin-carousel-icon {
            background: linear-gradient(135deg, rgba(255, 0, 255, 0.35), rgba(0, 255, 255, 0.2));
            box-shadow: 0 0 24px rgba(255, 0, 255, 0.4), 0 0 32px rgba(0, 255, 255, 0.35);
            animation: cyberGlitch 0.3s ease-in-out;
        }

        .admin-carousel-nav button:hover,
        .admin-carousel-actions button:hover {
            border: 2px solid #00ffff;
            box-shadow: 0 0 24px rgba(0, 255, 255, 0.4), 0 0 28px rgba(255, 0, 255, 0.35);
            transform: translateY(-2px) skewX(-2deg);
        }

        .admin-carousel-dot:hover,
        .admin-carousel-dot.active {
            background: linear-gradient(135deg, rgba(255, 0, 255, 0.85), rgba(0, 255, 255, 0.85));
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.6), 0 0 28px rgba(0, 255, 255, 0.5);
            transform: scale(1.35);
        }
        """
    },

    "elegant_luxury": {
        "name": "Elegant + Luxury",
        "description": "Eleganter Luxus-Stil mit goldenen Akzenten. Premium und hochwertig.",
        "css": """
        /* ELEGANT + LUXURY EFFEKT */
        .stButton button,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"],
        div[data-baseweb="button"] {
            position: relative;
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%) !important;
            border: 2px solid #f6d365 !important;
            box-shadow: 0 8px 16px rgba(246, 211, 101, 0.3);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
        }

        .stButton button::before,
        button[data-testid="baseButton-primary"]::before,
        button[data-testid="baseButton-secondary"]::before,
        button[kind="primary"]::before,
        button[kind="secondary"]::before,
        div[data-baseweb="button"]::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.4s ease;
        }

        .stButton button:hover,
        button[data-testid="baseButton-primary"]:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-baseweb="button"]:hover {
            border: 2px solid #ffd700 !important;
            box-shadow: 0 12px 24px rgba(255, 215, 0, 0.5), inset 0 0 20px rgba(255, 255, 255, 0.2);
            transform: translateY(-3px);
        }

        .stButton button:hover::before,
        button[data-testid="baseButton-primary"]:hover::before,
        button[data-testid="baseButton-secondary"]:hover::before,
        button[kind="primary"]:hover::before,
        button[kind="secondary"]:hover::before,
        div[data-baseweb="button"]:hover::before {
            opacity: 1;
            animation: luxuryShine 1.5s ease-in-out infinite;
        }

        @keyframes luxuryShine {
            0% { transform: translate(-50%, -50%) rotate(0deg); }
            100% { transform: translate(-50%, -50%) rotate(360deg); }
        }

        /* Expander Luxury */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, rgba(246, 211, 101, 0.1) 0%, rgba(253, 160, 133, 0.1) 100%);
            border-left: 3px solid #f6d365;
            transition: all 0.4s ease;
        }

        .streamlit-expanderHeader:hover {
            background: linear-gradient(90deg, rgba(246, 211, 101, 0.2) 0%, rgba(253, 160, 133, 0.2) 100%);
            border-left: 4px solid #ffd700;
            box-shadow: -5px 0 15px rgba(255, 215, 0, 0.3);
        }

        /* Slider Luxury */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"],
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"] {
            background: linear-gradient(135deg, #f6d365, #fda085) !important;
            border: 1px solid #f6d365 !important;
            box-shadow: 0 4px 8px rgba(246, 211, 101, 0.3);
        }

        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover,
        section[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover {
            border: 1px solid #ffd700 !important;
            box-shadow: 0 6px 12px rgba(255, 215, 0, 0.5);
            transform: scale(1.05);
        }

        /* Checkbox Luxury */
        div[data-baseweb="checkbox"],
        div[data-testid="stCheckbox"] label,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"],
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label {
            transition: all 0.35s ease;
            border-radius: 10px;
        }

        div[data-baseweb="checkbox"]:hover,
        div[data-testid="stCheckbox"] label:hover,
        section[data-testid="stSidebar"] div[data-baseweb="checkbox"]:hover,
        section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label:hover {
            box-shadow: 0 0 10px rgba(246, 211, 101, 0.5);
            transform: translateY(-1px);
        }

        /* Dropdown Luxury */
        div[data-baseweb="select"],
        .stSelectbox > div > div,
        div[data-testid="stSelectbox"] > div,
        section[data-testid="stSidebar"] div[data-baseweb="select"],
        section[data-testid="stSidebar"] .stSelectbox > div > div {
            position: relative;
            background: linear-gradient(135deg, rgba(246, 211, 101, 0.15), rgba(253, 160, 133, 0.15));
            border: 1px solid rgba(246, 211, 101, 0.4);
            box-shadow: 0 10px 20px rgba(246, 211, 101, 0.18);
            transition: all 0.35s ease;
            border-radius: 12px;
        }

        div[data-baseweb="select"]:hover,
        .stSelectbox > div > div:hover,
        div[data-testid="stSelectbox"] > div:hover,
        section[data-testid="stSidebar"] div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
            border: 1px solid rgba(255, 215, 0, 0.8);
            box-shadow: 0 16px 30px rgba(255, 215, 0, 0.28);
            transform: translateY(-3px);
        }

        /* Sidebar Navigation Hover (Elegant + Luxury) */
        section[data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] a[href]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] div[class*="st-emotion-cache"] a:hover,
        [data-testid="stSidebar"] .stMarkdown a:hover,
        section[data-testid="stSidebar"] p a:hover {
            background: linear-gradient(135deg, rgba(246, 211, 101, 0.25), rgba(253, 160, 133, 0.25));
            border-left: 4px solid rgba(255, 215, 0, 0.9);
            box-shadow: -6px 0 18px rgba(246, 211, 101, 0.25);
            transform: translateX(4px);
            padding-left: 12px;
            border-radius: 12px;
        }

        section[data-testid="stSidebar"] li:hover,
        [data-testid="stSidebar"] ul li:hover,
        [data-testid="stSidebar"] .stMarkdown li:hover {
            background: linear-gradient(135deg, rgba(253, 160, 133, 0.18), rgba(246, 211, 101, 0.18));
            border-left: 3px solid rgba(255, 215, 0, 0.8);
            transform: translateX(3px);
            padding-left: 10px;
            border-radius: 10px;
        }

        section[data-testid="stSidebar"] h1:hover,
        section[data-testid="stSidebar"] h2:hover,
        section[data-testid="stSidebar"] h3:hover,
        [data-testid="stSidebar"] .stMarkdown h1:hover,
        [data-testid="stSidebar"] .stMarkdown h2:hover {
            background: linear-gradient(135deg, rgba(246, 211, 101, 0.2), rgba(253, 160, 133, 0.2));
            border-left: 3px solid rgba(255, 215, 0, 0.8);
            transform: translateX(2px);
            padding-left: 8px;
            border-radius: 8px;
        }

        section[data-testid="stSidebar"] > div:hover,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
            background: linear-gradient(135deg, rgba(246, 211, 101, 0.12), rgba(253, 160, 133, 0.12));
            border-radius: 12px;
        }

        /* ========== CAROUSEL HOVER (ELEGANT + LUXURY) ========== */
        .admin-carousel-card:hover,
        .admin-carousel-card.active {
            background: linear-gradient(135deg, rgba(246, 211, 101, 0.3), rgba(253, 160, 133, 0.3));
            border: 1px solid rgba(255, 215, 0, 0.8);
            box-shadow: 0 18px 36px rgba(255, 215, 0, 0.35);
            transform: translateY(-4px) scale(1.02);
        }

        .admin-carousel-card:hover .admin-carousel-icon,
        .admin-carousel-card.active .admin-carousel-icon {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.45), rgba(255, 215, 0, 0.3));
            box-shadow: 0 14px 28px rgba(255, 215, 0, 0.35);
            transform: translateY(-3px);
        }

        .admin-carousel-nav button:hover,
        .admin-carousel-actions button:hover {
            background: linear-gradient(135deg, rgba(246, 211, 101, 0.3), rgba(253, 160, 133, 0.3));
            border: 1px solid rgba(255, 215, 0, 0.8);
            box-shadow: 0 12px 24px rgba(255, 215, 0, 0.3);
            transform: translateY(-2px);
        }

        .admin-carousel-dot:hover,
        .admin-carousel-dot.active {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 215, 0, 0.95));
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
            transform: scale(1.32);
        }
        """
    }
}


def get_effect_names():
    """Gibt eine Liste aller verfügbaren Effekt-Namen zurück"""
    return list(UI_EFFECTS_LIBRARY.keys())


def get_effect_info(effect_key):
    """Gibt Informationen zu einem bestimmten Effekt zurück"""
    return UI_EFFECTS_LIBRARY.get(effect_key, {})


def get_effect_css(effect_key):
    """Gibt das CSS für einen bestimmten Effekt zurück (inkl. universeller Sidebar-Support)"""
    effect = UI_EFFECTS_LIBRARY.get(effect_key, {})
    base_css = effect.get("css", "")

    # Kombiniere Basis-CSS mit universellem Sidebar-Support
    return f"""
    {UNIVERSAL_SIDEBAR_CSS}

    /* ========== EFFEKT-SPEZIFISCHES CSS ========== */
    {base_css}
    """


def get_default_effect():
    """Gibt den Standard-Effekt zurück"""
    return "shimmer_pulse"
