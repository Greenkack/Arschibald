"""
shadcn/ui Responsive Design System

Dieses Modul implementiert ein vollständiges Responsive Design System für Streamlit-Apps
mit shadcn/ui-Styling. Es bietet:

- Media Queries für verschiedene Breakpoints (mobile, tablet, desktop)
- Kollabierbare Sidebar für Mobile
- Gestapelte Layouts für Mobile
- Touch-freundliche Button-Größen (min. 44px)
- Verhindert horizontales Scrollen

Author: shadcn/ui Theme System
Version: 1.0.0
"""

from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
import streamlit as st


@dataclass
class Breakpoint:
    """Repräsentiert einen Responsive Breakpoint"""
    name: str
    min_width: int
    max_width: Optional[int] = None
    
    def to_media_query(self) -> str:
        """Konvertiert Breakpoint zu CSS Media Query"""
        if self.max_width:
            return f"@media (min-width: {self.min_width}px) and (max-width: {self.max_width}px)"
        return f"@media (min-width: {self.min_width}px)"


class ResponsiveDesignSystem:
    """
    Verwaltet Responsive Design für shadcn/ui Streamlit Apps
    
    Features:
    - Breakpoint-Management
    - Mobile-First CSS
    - Touch-optimierte Komponenten
    - Kollabierbare Sidebar
    - Responsive Layouts
    """
    
    # Standard Breakpoints (Mobile-First)
    BREAKPOINTS = {
        'mobile': Breakpoint('mobile', 0, 767),
        'tablet': Breakpoint('tablet', 768, 1023),
        'desktop': Breakpoint('desktop', 1024, None)
    }
    
    # Touch-freundliche Mindestgrößen
    MIN_TOUCH_SIZE = 44  # px (Apple HIG & Material Design Standard)
    
    def __init__(self):
        """Initialisiert das Responsive Design System"""
        self.breakpoints = self.BREAKPOINTS.copy()
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialisiert Session State für Responsive Features"""
        if 'sidebar_collapsed' not in st.session_state:
            st.session_state.sidebar_collapsed = False
        if 'current_breakpoint' not in st.session_state:
            st.session_state.current_breakpoint = 'desktop'
    
    def generate_responsive_css(self) -> str:
        """
        Generiert vollständiges Responsive CSS
        
        Returns:
            str: CSS-String mit allen Responsive Styles
        """
        css_parts = [
            self._generate_base_responsive_css(),
            self._generate_mobile_css(),
            self._generate_tablet_css(),
            self._generate_desktop_css(),
            self._generate_touch_optimized_css(),
            self._generate_sidebar_responsive_css(),
            self._generate_layout_responsive_css(),
            self._generate_utility_classes()
        ]
        
        return "\n\n".join(css_parts)
    
    def _generate_base_responsive_css(self) -> str:
        """Generiert Basis Responsive CSS"""
        return """
/* ===== BASE RESPONSIVE STYLES ===== */

/* Verhindere horizontales Scrollen */
html, body, [data-testid="stAppViewContainer"] {
    overflow-x: hidden !important;
    max-width: 100vw !important;
}

/* Box-Sizing für alle Elemente */
*, *::before, *::after {
    box-sizing: border-box;
}

/* Responsive Container */
.responsive-container {
    width: 100%;
    max-width: 100%;
    padding-left: 1rem;
    padding-right: 1rem;
    margin-left: auto;
    margin-right: auto;
}

/* Responsive Images */
img {
    max-width: 100%;
    height: auto;
}

/* Responsive Tables */
table {
    width: 100%;
    overflow-x: auto;
    display: block;
}

/* Flexible Layouts */
.flex-container {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

.flex-item {
    flex: 1 1 auto;
    min-width: 0;
}
"""
    
    def _generate_mobile_css(self) -> str:
        """Generiert Mobile-spezifisches CSS"""
        return f"""
/* ===== MOBILE STYLES (0-767px) ===== */
{self.breakpoints['mobile'].to_media_query()} {{
    
    /* Container Padding reduzieren */
    .responsive-container {{
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }}
    
    /* Streamlit Columns zu Stack */
    [data-testid="column"] {{
        width: 100% !important;
        flex: 0 0 100% !important;
        max-width: 100% !important;
        margin-bottom: 1rem;
    }}
    
    /* Tabs vertikal stapeln */
    [data-testid="stTabs"] {{
        flex-direction: column;
    }}
    
    [data-testid="stTab"] {{
        width: 100%;
        margin-bottom: 0.5rem;
    }}
    
    /* Cards volle Breite */
    .shadcn-card {{
        width: 100% !important;
        margin-bottom: 1rem;
    }}
    
    /* Metric Cards stapeln */
    .metric-card {{
        width: 100% !important;
        margin-bottom: 0.75rem;
    }}
    
    /* Buttons volle Breite */
    .stButton > button {{
        width: 100% !important;
        margin-bottom: 0.5rem;
    }}
    
    /* Form Inputs volle Breite */
    .stTextInput, .stNumberInput, .stSelectbox, .stMultiSelect {{
        width: 100% !important;
    }}
    
    /* Tabellen horizontal scrollbar */
    .dataframe-container {{
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }}
    
    /* Charts responsive */
    .js-plotly-plot {{
        width: 100% !important;
        height: auto !important;
    }}
    
    /* Font-Größen anpassen */
    h1 {{ font-size: 1.75rem !important; }}
    h2 {{ font-size: 1.5rem !important; }}
    h3 {{ font-size: 1.25rem !important; }}
    
    /* Padding reduzieren */
    .element-container {{
        padding: 0.5rem 0;
    }}
    
    /* Sidebar volle Breite wenn ausgeklappt */
    [data-testid="stSidebar"] {{
        width: 100% !important;
        max-width: 100% !important;
    }}
    
    /* Sidebar Toggle Button */
    .sidebar-toggle-mobile {{
        display: block !important;
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 1000;
        background: var(--background);
        border: 1px solid var(--border);
        border-radius: 0.5rem;
        padding: 0.75rem;
        min-width: {self.MIN_TOUCH_SIZE}px;
        min-height: {self.MIN_TOUCH_SIZE}px;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
}}
"""
    
    def _generate_tablet_css(self) -> str:
        """Generiert Tablet-spezifisches CSS"""
        return f"""
/* ===== TABLET STYLES (768px-1023px) ===== */
{self.breakpoints['tablet'].to_media_query()} {{
    
    /* Container mit moderatem Padding */
    .responsive-container {{
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 768px;
    }}
    
    /* 2-Spalten Layout für Columns */
    [data-testid="column"] {{
        flex: 0 0 48% !important;
        max-width: 48% !important;
    }}
    
    /* Metric Cards 2-spaltig */
    .metric-card {{
        width: 48% !important;
        display: inline-block;
        margin-right: 2%;
    }}
    
    /* Cards 2-spaltig */
    .shadcn-card {{
        width: 48% !important;
        display: inline-block;
        margin-right: 2%;
        margin-bottom: 1rem;
    }}
    
    /* Sidebar reduzierte Breite */
    [data-testid="stSidebar"] {{
        width: 250px !important;
        max-width: 250px !important;
    }}
    
    /* Font-Größen */
    h1 {{ font-size: 2rem !important; }}
    h2 {{ font-size: 1.75rem !important; }}
    h3 {{ font-size: 1.5rem !important; }}
    
    /* Sidebar Toggle verstecken */
    .sidebar-toggle-mobile {{
        display: none !important;
    }}
}}
"""
    
    def _generate_desktop_css(self) -> str:
        """Generiert Desktop-spezifisches CSS"""
        return f"""
/* ===== DESKTOP STYLES (1024px+) ===== */
{self.breakpoints['desktop'].to_media_query()} {{
    
    /* Container mit voller Breite */
    .responsive-container {{
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1400px;
    }}
    
    /* Columns normale Breite */
    [data-testid="column"] {{
        flex: 1 !important;
    }}
    
    /* Sidebar normale Breite */
    [data-testid="stSidebar"] {{
        width: 300px !important;
        max-width: 300px !important;
    }}
    
    /* Sidebar Toggle verstecken */
    .sidebar-toggle-mobile {{
        display: none !important;
    }}
    
    /* Hover-Effekte aktivieren */
    .stButton > button:hover,
    .shadcn-card:hover,
    .metric-card:hover {{
        transform: translateY(-2px);
        transition: transform 0.2s ease;
    }}
}}
"""
    
    def _generate_touch_optimized_css(self) -> str:
        """Generiert Touch-optimiertes CSS"""
        return f"""
/* ===== TOUCH-OPTIMIZED STYLES ===== */

/* Mindestgröße für Touch-Targets */
.stButton > button,
.stCheckbox,
.stRadio,
[role="button"],
a {{
    min-width: {self.MIN_TOUCH_SIZE}px !important;
    min-height: {self.MIN_TOUCH_SIZE}px !important;
    padding: 0.75rem 1rem !important;
}}

/* Größere Touch-Bereiche für Inputs */
input[type="text"],
input[type="number"],
input[type="email"],
input[type="password"],
textarea,
select {{
    min-height: {self.MIN_TOUCH_SIZE}px !important;
    padding: 0.75rem !important;
    font-size: 16px !important; /* Verhindert Zoom auf iOS */
}}

/* Slider Touch-freundlich */
input[type="range"] {{
    height: {self.MIN_TOUCH_SIZE}px !important;
    cursor: pointer;
}}

/* Checkbox/Radio größer */
input[type="checkbox"],
input[type="radio"] {{
    width: 24px !important;
    height: 24px !important;
    cursor: pointer;
}}

/* Links größere Touch-Bereiche */
a {{
    padding: 0.5rem !important;
    display: inline-block;
}}

/* Tab-Buttons Touch-freundlich */
[data-testid="stTab"] {{
    min-height: {self.MIN_TOUCH_SIZE}px !important;
    padding: 0.75rem 1.5rem !important;
}}

/* Dropdown-Items */
[role="option"],
[role="menuitem"] {{
    min-height: {self.MIN_TOUCH_SIZE}px !important;
    padding: 0.75rem 1rem !important;
}}

/* Touch-Feedback */
@media (hover: none) and (pointer: coarse) {{
    .stButton > button:active,
    [role="button"]:active {{
        transform: scale(0.98);
        opacity: 0.8;
    }}
}}
"""
    
    def _generate_sidebar_responsive_css(self) -> str:
        """Generiert Responsive Sidebar CSS"""
        return """
/* ===== RESPONSIVE SIDEBAR ===== */

/* Sidebar Basis */
[data-testid="stSidebar"] {
    transition: transform 0.3s ease, width 0.3s ease;
}

/* Sidebar kollabiert (Mobile) */
[data-testid="stSidebar"].collapsed {
    transform: translateX(-100%);
}

/* Sidebar Overlay für Mobile */
.sidebar-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
}

.sidebar-overlay.active {
    display: block;
}

/* Sidebar Toggle Button */
.sidebar-toggle {
    display: none;
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 1001;
    background: var(--background);
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    padding: 0.75rem;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Mobile Sidebar */
@media (max-width: 767px) {
    .sidebar-toggle {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    [data-testid="stSidebar"] {
        position: fixed;
        top: 0;
        left: 0;
        height: 100vh;
        z-index: 1000;
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
    }
}
"""
    
    def _generate_layout_responsive_css(self) -> str:
        """Generiert Responsive Layout CSS"""
        return """
/* ===== RESPONSIVE LAYOUTS ===== */

/* Grid System */
.responsive-grid {
    display: grid;
    gap: 1rem;
    width: 100%;
}

/* Mobile: 1 Spalte */
@media (max-width: 767px) {
    .responsive-grid {
        grid-template-columns: 1fr;
    }
    
    .responsive-grid-2,
    .responsive-grid-3,
    .responsive-grid-4 {
        grid-template-columns: 1fr;
    }
}

/* Tablet: 2 Spalten */
@media (min-width: 768px) and (max-width: 1023px) {
    .responsive-grid-2,
    .responsive-grid-3,
    .responsive-grid-4 {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Desktop: Volle Spalten */
@media (min-width: 1024px) {
    .responsive-grid-2 {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .responsive-grid-3 {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .responsive-grid-4 {
        grid-template-columns: repeat(4, 1fr);
    }
}

/* Flexbox Layouts */
.responsive-flex {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

.responsive-flex > * {
    flex: 1 1 auto;
    min-width: 0;
}

/* Mobile: Stack */
@media (max-width: 767px) {
    .responsive-flex {
        flex-direction: column;
    }
    
    .responsive-flex > * {
        width: 100%;
    }
}

/* Spacing Utilities */
.spacing-mobile-sm { padding: 0.5rem; }
.spacing-mobile-md { padding: 1rem; }
.spacing-mobile-lg { padding: 1.5rem; }

@media (min-width: 768px) {
    .spacing-mobile-sm { padding: 0.75rem; }
    .spacing-mobile-md { padding: 1.5rem; }
    .spacing-mobile-lg { padding: 2rem; }
}

@media (min-width: 1024px) {
    .spacing-mobile-sm { padding: 1rem; }
    .spacing-mobile-md { padding: 2rem; }
    .spacing-mobile-lg { padding: 3rem; }
}
"""
    
    def _generate_utility_classes(self) -> str:
        """Generiert Responsive Utility Classes"""
        return """
/* ===== RESPONSIVE UTILITIES ===== */

/* Visibility Utilities */
.hide-mobile { display: block; }
.hide-tablet { display: block; }
.hide-desktop { display: block; }

.show-mobile { display: none; }
.show-tablet { display: none; }
.show-desktop { display: none; }

@media (max-width: 767px) {
    .hide-mobile { display: none !important; }
    .show-mobile { display: block !important; }
}

@media (min-width: 768px) and (max-width: 1023px) {
    .hide-tablet { display: none !important; }
    .show-tablet { display: block !important; }
}

@media (min-width: 1024px) {
    .hide-desktop { display: none !important; }
    .show-desktop { display: block !important; }
}

/* Text Alignment */
.text-center-mobile { text-align: left; }

@media (max-width: 767px) {
    .text-center-mobile { text-align: center; }
}

/* Width Utilities */
.w-full { width: 100%; }
.w-auto { width: auto; }

.max-w-mobile { max-width: 100%; }
.max-w-tablet { max-width: 768px; }
.max-w-desktop { max-width: 1400px; }

/* Margin Utilities */
.mx-auto { margin-left: auto; margin-right: auto; }
.my-auto { margin-top: auto; margin-bottom: auto; }

/* Overflow Control */
.overflow-hidden { overflow: hidden; }
.overflow-x-hidden { overflow-x: hidden; }
.overflow-y-auto { overflow-y: auto; }
.overflow-x-auto { overflow-x: auto; }

/* Scroll Behavior */
.scroll-smooth { scroll-behavior: smooth; }
.scroll-snap { scroll-snap-type: x mandatory; }
.scroll-snap-item { scroll-snap-align: start; }
"""
    
    def inject_responsive_css(self):
        """Injiziert Responsive CSS in die Streamlit App"""
        css = self.generate_responsive_css()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    def render_sidebar_toggle(self):
        """Rendert Sidebar Toggle Button für Mobile"""
        toggle_html = """
        <div class="sidebar-toggle-mobile" onclick="toggleSidebar()">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
        </div>
        
        <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>
        
        <script>
        function toggleSidebar() {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            const overlay = document.getElementById('sidebarOverlay');
            
            if (sidebar && overlay) {
                sidebar.classList.toggle('collapsed');
                overlay.classList.toggle('active');
            }
        }
        </script>
        """
        
        st.markdown(toggle_html, unsafe_allow_html=True)
    
    def get_current_breakpoint(self) -> str:
        """
        Ermittelt den aktuellen Breakpoint basierend auf Viewport-Breite
        
        Returns:
            str: 'mobile', 'tablet', oder 'desktop'
        """
        # JavaScript zum Ermitteln der Viewport-Breite
        js_code = """
        <script>
        const width = window.innerWidth;
        let breakpoint = 'desktop';
        
        if (width < 768) {
            breakpoint = 'mobile';
        } else if (width < 1024) {
            breakpoint = 'tablet';
        }
        
        // Speichere in Session Storage
        sessionStorage.setItem('current_breakpoint', breakpoint);
        </script>
        """
        
        st.markdown(js_code, unsafe_allow_html=True)
        return st.session_state.get('current_breakpoint', 'desktop')
    
    def is_mobile(self) -> bool:
        """Prüft ob aktueller Viewport Mobile ist"""
        return self.get_current_breakpoint() == 'mobile'
    
    def is_tablet(self) -> bool:
        """Prüft ob aktueller Viewport Tablet ist"""
        return self.get_current_breakpoint() == 'tablet'
    
    def is_desktop(self) -> bool:
        """Prüft ob aktueller Viewport Desktop ist"""
        return self.get_current_breakpoint() == 'desktop'


# Convenience Functions

def inject_responsive_design():
    """
    Injiziert Responsive Design CSS in die App
    
    Usage:
        from utils.shadcn_responsive import inject_responsive_design
        inject_responsive_design()
    """
    system = ResponsiveDesignSystem()
    system.inject_responsive_css()


def render_mobile_sidebar_toggle():
    """
    Rendert Sidebar Toggle Button für Mobile
    
    Usage:
        from utils.shadcn_responsive import render_mobile_sidebar_toggle
        render_mobile_sidebar_toggle()
    """
    system = ResponsiveDesignSystem()
    system.render_sidebar_toggle()


def responsive_columns(num_columns: int, mobile_stack: bool = True) -> List:
    """
    Erstellt responsive Columns die auf Mobile stacken
    
    Args:
        num_columns: Anzahl der Spalten auf Desktop
        mobile_stack: Ob Spalten auf Mobile gestackt werden sollen
    
    Returns:
        List: Streamlit Column-Objekte
    
    Usage:
        cols = responsive_columns(3)
        with cols[0]:
            st.write("Column 1")
    """
    if mobile_stack:
        # Füge CSS-Klasse hinzu für Mobile-Stacking
        st.markdown("""
        <style>
        @media (max-width: 767px) {
            [data-testid="column"] {
                width: 100% !important;
                flex: 0 0 100% !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    return st.columns(num_columns)


def responsive_container(max_width: Literal['mobile', 'tablet', 'desktop'] = 'desktop'):
    """
    Erstellt einen responsive Container mit max-width
    
    Args:
        max_width: Maximale Breite ('mobile', 'tablet', 'desktop')
    
    Returns:
        Streamlit Container
    
    Usage:
        with responsive_container('tablet'):
            st.write("Content")
    """
    max_widths = {
        'mobile': '100%',
        'tablet': '768px',
        'desktop': '1400px'
    }
    
    st.markdown(f"""
    <style>
    .responsive-container-{max_width} {{
        max-width: {max_widths[max_width]};
        margin: 0 auto;
        padding: 0 1rem;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    return st.container()


# Export
__all__ = [
    'ResponsiveDesignSystem',
    'Breakpoint',
    'inject_responsive_design',
    'render_mobile_sidebar_toggle',
    'responsive_columns',
    'responsive_container'
]
