"""
ARSCHIBALD UI Design System
Zentrale Definition von Farben, Typografie, Spacing, Component Variants und Icons
Version: 1.0.0
Erstellt: 2025-12-09
"""

from typing import Dict, List, Literal
import streamlit as st

# ==================== FARB-PALETTE ====================

class ColorPalette:
    """Zentrale Farbdefinitionen für die gesamte Anwendung"""
    
    # Primärfarben (Blau-basiert für professionelle Tech-Optik)
    PRIMARY = "#0066CC"
    PRIMARY_LIGHT = "#3399FF"
    PRIMARY_DARK = "#004C99"
    PRIMARY_HOVER = "#0052A3"
    
    # Sekundärfarben (Grau-Skala für neutrale Elemente)
    SECONDARY = "#6B7280"
    SECONDARY_LIGHT = "#9CA3AF"
    SECONDARY_DARK = "#4B5563"
    
    # Akzentfarben
    ACCENT = "#7C3AED"  # Lila für Highlights
    ACCENT_LIGHT = "#A78BFA"
    ACCENT_DARK = "#5B21B6"
    
    # Statusfarben
    SUCCESS = "#10B981"  # Grün
    SUCCESS_LIGHT = "#34D399"
    SUCCESS_DARK = "#059669"
    
    WARNING = "#F59E0B"  # Orange/Gelb
    WARNING_LIGHT = "#FBBF24"
    WARNING_DARK = "#D97706"
    
    ERROR = "#EF4444"  # Rot
    ERROR_LIGHT = "#F87171"
    ERROR_DARK = "#DC2626"
    
    INFO = "#3B82F6"  # Hellblau
    INFO_LIGHT = "#60A5FA"
    INFO_DARK = "#2563EB"
    
    # Neutrale Farben (für Backgrounds, Borders, Text)
    BACKGROUND_LIGHT = "#FFFFFF"
    BACKGROUND_DARK = "#F9FAFB"
    BACKGROUND_DARKER = "#F3F4F6"
    
    SURFACE = "#FFFFFF"
    SURFACE_HOVER = "#F9FAFB"
    
    BORDER = "#E5E7EB"
    BORDER_LIGHT = "#F3F4F6"
    BORDER_DARK = "#D1D5DB"
    
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6B7280"
    TEXT_TERTIARY = "#9CA3AF"
    TEXT_INVERSE = "#FFFFFF"
    
    # Dark Mode Farben (für zukünftige Implementation)
    DARK_BACKGROUND = "#1F2937"
    DARK_BACKGROUND_LIGHT = "#374151"
    DARK_SURFACE = "#111827"
    DARK_TEXT_PRIMARY = "#F9FAFB"
    DARK_TEXT_SECONDARY = "#D1D5DB"
    DARK_BORDER = "#374151"
    
    # Spezifische Farben für ARSCHIBALD Features
    SOLAR_YELLOW = "#FCD34D"  # PV-Anlagen
    HEAT_PUMP_ORANGE = "#FB923C"  # Wärmepumpen
    CRM_BLUE = "#60A5FA"  # CRM
    CONTROLLING_PURPLE = "#A78BFA"  # Controlling
    
    @classmethod
    def get_color_map(cls) -> Dict[str, str]:
        """Gibt alle Farben als Dictionary zurück"""
        return {
            "primary": cls.PRIMARY,
            "primary_light": cls.PRIMARY_LIGHT,
            "primary_dark": cls.PRIMARY_DARK,
            "secondary": cls.SECONDARY,
            "success": cls.SUCCESS,
            "warning": cls.WARNING,
            "error": cls.ERROR,
            "info": cls.INFO,
            "text_primary": cls.TEXT_PRIMARY,
            "text_secondary": cls.TEXT_SECONDARY,
            "background": cls.BACKGROUND_LIGHT,
            "border": cls.BORDER
        }
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """Gibt Farbe basierend auf Status zurück"""
        status_map = {
            "success": cls.SUCCESS,
            "warning": cls.WARNING,
            "error": cls.ERROR,
            "info": cls.INFO,
            "active": cls.SUCCESS,
            "pending": cls.WARNING,
            "inactive": cls.SECONDARY,
            "cancelled": cls.ERROR
        }
        return status_map.get(status.lower(), cls.SECONDARY)


# ==================== TYPOGRAFIE ====================

class Typography:
    """Zentrale Typografie-Definitionen"""
    
    # Font Families
    FONT_FAMILY_PRIMARY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    FONT_FAMILY_MONOSPACE = "'Fira Code', 'Courier New', monospace"
    
    # Font Sizes (rem-basiert, 1rem = 16px)
    FONT_SIZE_H1 = "2.5rem"      # 40px
    FONT_SIZE_H2 = "2rem"        # 32px
    FONT_SIZE_H3 = "1.75rem"     # 28px
    FONT_SIZE_H4 = "1.5rem"      # 24px
    FONT_SIZE_H5 = "1.25rem"     # 20px
    FONT_SIZE_H6 = "1rem"        # 16px
    FONT_SIZE_BODY = "1rem"      # 16px
    FONT_SIZE_BODY_SM = "0.875rem"  # 14px
    FONT_SIZE_CAPTION = "0.75rem"   # 12px
    FONT_SIZE_TINY = "0.625rem"     # 10px
    
    # Font Weights
    WEIGHT_LIGHT = 300
    WEIGHT_REGULAR = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700
    WEIGHT_EXTRABOLD = 800
    
    # Line Heights
    LINE_HEIGHT_TIGHT = "1.25"
    LINE_HEIGHT_NORMAL = "1.5"
    LINE_HEIGHT_RELAXED = "1.75"
    LINE_HEIGHT_LOOSE = "2"
    
    # Letter Spacing
    LETTER_SPACING_TIGHT = "-0.025em"
    LETTER_SPACING_NORMAL = "0"
    LETTER_SPACING_WIDE = "0.025em"
    
    @classmethod
    def get_heading_style(cls, level: int) -> Dict[str, str]:
        """Gibt CSS-Style für Heading zurück"""
        sizes = {
            1: cls.FONT_SIZE_H1,
            2: cls.FONT_SIZE_H2,
            3: cls.FONT_SIZE_H3,
            4: cls.FONT_SIZE_H4,
            5: cls.FONT_SIZE_H5,
            6: cls.FONT_SIZE_H6
        }
        return {
            "font-size": sizes.get(level, cls.FONT_SIZE_BODY),
            "font-weight": str(cls.WEIGHT_BOLD),
            "line-height": cls.LINE_HEIGHT_TIGHT,
            "color": ColorPalette.TEXT_PRIMARY
        }


# ==================== SPACING SYSTEM ====================

class Spacing:
    """Zentrale Spacing/Padding/Margin Definitionen"""
    
    # Spacing Scale (Pixel-Werte)
    XS = "4px"      # 0.25rem
    SM = "8px"      # 0.5rem
    MD = "16px"     # 1rem
    LG = "24px"     # 1.5rem
    XL = "32px"     # 2rem
    XXL = "48px"    # 3rem
    XXXL = "64px"   # 4rem
    
    # Component-spezifisches Spacing
    CARD_PADDING = "16px"
    BUTTON_PADDING_X = "16px"
    BUTTON_PADDING_Y = "8px"
    INPUT_PADDING = "12px"
    CONTAINER_PADDING = "24px"
    SECTION_GAP = "32px"
    
    @classmethod
    def get_spacing(cls, size: Literal["xs", "sm", "md", "lg", "xl", "xxl", "xxxl"]) -> str:
        """Gibt Spacing-Wert zurück"""
        mapping = {
            "xs": cls.XS,
            "sm": cls.SM,
            "md": cls.MD,
            "lg": cls.LG,
            "xl": cls.XL,
            "xxl": cls.XXL,
            "xxxl": cls.XXXL
        }
        return mapping.get(size, cls.MD)


# ==================== BORDER & RADIUS ====================

class BorderStyles:
    """Border und Border-Radius Definitionen"""
    
    # Border Widths
    BORDER_THIN = "1px"
    BORDER_MEDIUM = "2px"
    BORDER_THICK = "4px"
    
    # Border Radius
    RADIUS_NONE = "0"
    RADIUS_SM = "4px"
    RADIUS_MD = "8px"
    RADIUS_LG = "12px"
    RADIUS_XL = "16px"
    RADIUS_FULL = "9999px"  # Pill-Shape
    
    # Standard Border Styles
    BORDER_DEFAULT = f"{BORDER_THIN} solid {ColorPalette.BORDER}"
    BORDER_FOCUS = f"{BORDER_MEDIUM} solid {ColorPalette.PRIMARY}"
    BORDER_ERROR = f"{BORDER_MEDIUM} solid {ColorPalette.ERROR}"
    
    @classmethod
    def get_border_style(cls, variant: Literal["default", "focus", "error"] = "default") -> str:
        """Gibt Border-Style zurück"""
        mapping = {
            "default": cls.BORDER_DEFAULT,
            "focus": cls.BORDER_FOCUS,
            "error": cls.BORDER_ERROR
        }
        return mapping.get(variant, cls.BORDER_DEFAULT)


# ==================== SHADOWS ====================

class Shadows:
    """Box Shadow Definitionen für Depth/Elevation"""
    
    SHADOW_NONE = "none"
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    SHADOW_2XL = "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
    
    # Spezielle Shadows
    SHADOW_INNER = "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"
    SHADOW_OUTLINE = f"0 0 0 3px rgba(0, 102, 204, 0.1)"  # Focus Outline
    
    @classmethod
    def get_shadow(cls, size: Literal["sm", "md", "lg", "xl", "2xl"] = "md") -> str:
        """Gibt Shadow basierend auf Größe zurück"""
        mapping = {
            "sm": cls.SHADOW_SM,
            "md": cls.SHADOW_MD,
            "lg": cls.SHADOW_LG,
            "xl": cls.SHADOW_XL,
            "2xl": cls.SHADOW_2XL
        }
        return mapping.get(size, cls.SHADOW_MD)


# ==================== COMPONENT VARIANTS ====================

class ComponentVariants:
    """Standard-Variants für wiederverwendbare Komponenten"""
    
    # Button Sizes
    BUTTON_SIZES = {
        "sm": {
            "padding": f"{Spacing.XS} {Spacing.SM}",
            "font-size": Typography.FONT_SIZE_BODY_SM,
            "height": "32px"
        },
        "md": {
            "padding": f"{Spacing.SM} {Spacing.MD}",
            "font-size": Typography.FONT_SIZE_BODY,
            "height": "40px"
        },
        "lg": {
            "padding": f"{Spacing.MD} {Spacing.LG}",
            "font-size": Typography.FONT_SIZE_H6,
            "height": "48px"
        }
    }
    
    # Button Variants
    BUTTON_VARIANTS = {
        "primary": {
            "background": ColorPalette.PRIMARY,
            "color": ColorPalette.TEXT_INVERSE,
            "border": "none",
            "hover_background": ColorPalette.PRIMARY_HOVER
        },
        "secondary": {
            "background": ColorPalette.SECONDARY,
            "color": ColorPalette.TEXT_INVERSE,
            "border": "none",
            "hover_background": ColorPalette.SECONDARY_DARK
        },
        "outline": {
            "background": "transparent",
            "color": ColorPalette.PRIMARY,
            "border": BorderStyles.BORDER_DEFAULT,
            "hover_background": ColorPalette.BACKGROUND_DARK
        },
        "ghost": {
            "background": "transparent",
            "color": ColorPalette.TEXT_PRIMARY,
            "border": "none",
            "hover_background": ColorPalette.BACKGROUND_DARK
        },
        "destructive": {
            "background": ColorPalette.ERROR,
            "color": ColorPalette.TEXT_INVERSE,
            "border": "none",
            "hover_background": ColorPalette.ERROR_DARK
        }
    }
    
    # Card Variants
    CARD_VARIANTS = {
        "elevated": {
            "background": ColorPalette.SURFACE,
            "border": "none",
            "box-shadow": Shadows.SHADOW_MD,
            "hover-shadow": Shadows.SHADOW_LG
        },
        "outlined": {
            "background": ColorPalette.SURFACE,
            "border": BorderStyles.BORDER_DEFAULT,
            "box-shadow": Shadows.SHADOW_NONE,
            "hover-shadow": Shadows.SHADOW_SM
        },
        "flat": {
            "background": ColorPalette.BACKGROUND_DARK,
            "border": "none",
            "box-shadow": Shadows.SHADOW_NONE,
            "hover-shadow": Shadows.SHADOW_NONE
        }
    }
    
    # Badge Variants
    BADGE_VARIANTS = {
        "default": {
            "background": ColorPalette.PRIMARY,
            "color": ColorPalette.TEXT_INVERSE
        },
        "secondary": {
            "background": ColorPalette.SECONDARY,
            "color": ColorPalette.TEXT_INVERSE
        },
        "success": {
            "background": ColorPalette.SUCCESS,
            "color": ColorPalette.TEXT_INVERSE
        },
        "warning": {
            "background": ColorPalette.WARNING,
            "color": ColorPalette.TEXT_PRIMARY
        },
        "error": {
            "background": ColorPalette.ERROR,
            "color": ColorPalette.TEXT_INVERSE
        },
        "outline": {
            "background": "transparent",
            "color": ColorPalette.TEXT_PRIMARY,
            "border": BorderStyles.BORDER_DEFAULT
        }
    }


# ==================== RESPONSIVE BREAKPOINTS ====================

class Breakpoints:
    """Responsive Breakpoints für verschiedene Bildschirmgrößen"""
    
    # Breakpoint-Werte (Pixel)
    MOBILE_MAX = 767
    TABLET_MIN = 768
    TABLET_MAX = 1023
    DESKTOP_MIN = 1024
    DESKTOP_MAX = 1439
    WIDE_MIN = 1440
    
    # Media Queries (für CSS)
    MOBILE = f"(max-width: {MOBILE_MAX}px)"
    TABLET = f"(min-width: {TABLET_MIN}px) and (max-width: {TABLET_MAX}px)"
    DESKTOP = f"(min-width: {DESKTOP_MIN}px)"
    WIDE = f"(min-width: {WIDE_MIN}px)"
    
    # Grid Columns pro Breakpoint
    GRID_COLUMNS = {
        "mobile": 1,
        "tablet": 2,
        "desktop": 3,
        "wide": 4
    }
    
    @classmethod
    def get_columns_for_viewport(cls, viewport_width: int) -> int:
        """Gibt Anzahl Grid-Columns basierend auf Viewport-Breite zurück"""
        if viewport_width <= cls.MOBILE_MAX:
            return cls.GRID_COLUMNS["mobile"]
        elif viewport_width <= cls.TABLET_MAX:
            return cls.GRID_COLUMNS["tablet"]
        elif viewport_width <= cls.DESKTOP_MAX:
            return cls.GRID_COLUMNS["desktop"]
        else:
            return cls.GRID_COLUMNS["wide"]


# ==================== ICON MAPPING ====================

class IconMapping:
    """
    Icon-Mapping für Lucide Icons
    https://lucide.dev/icons/
    """
    
    # Feature Icons
    SOLAR = "sun"
    HEAT_PUMP = "flame"
    CRM = "users"
    CONTROLLING = "bar-chart-2"
    ADMIN = "settings"
    PDF = "file-text"
    ANALYSIS = "trending-up"
    CALCULATOR = "calculator"
    
    # UI Icons
    HOME = "home"
    MENU = "menu"
    CLOSE = "x"
    SEARCH = "search"
    FILTER = "filter"
    SETTINGS = "settings"
    USER = "user"
    LOGOUT = "log-out"
    LOGIN = "log-in"
    
    # Action Icons
    SAVE = "save"
    EDIT = "edit-2"
    DELETE = "trash-2"
    ADD = "plus"
    REMOVE = "minus"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    REFRESH = "refresh-cw"
    
    # Status Icons
    SUCCESS = "check-circle"
    WARNING = "alert-triangle"
    ERROR = "x-circle"
    INFO = "info"
    HELP = "help-circle"
    
    # Navigation Icons
    ARROW_LEFT = "arrow-left"
    ARROW_RIGHT = "arrow-right"
    ARROW_UP = "arrow-up"
    ARROW_DOWN = "arrow-down"
    CHEVRON_LEFT = "chevron-left"
    CHEVRON_RIGHT = "chevron-right"
    CHEVRON_UP = "chevron-up"
    CHEVRON_DOWN = "chevron-down"
    
    # Data Icons
    CHART = "bar-chart"
    PIE_CHART = "pie-chart"
    TABLE = "table"
    LIST = "list"
    GRID = "grid"
    
    # Document Icons
    FILE = "file"
    FOLDER = "folder"
    IMAGE = "image"
    VIDEO = "video"
    
    # Communication Icons
    MAIL = "mail"
    PHONE = "phone"
    MESSAGE = "message-square"
    
    @classmethod
    def get_icon(cls, feature: str) -> str:
        """Gibt Icon-Name für Feature zurück"""
        mapping = {
            "pv": cls.SOLAR,
            "photovoltaik": cls.SOLAR,
            "waermepumpe": cls.HEAT_PUMP,
            "heatpump": cls.HEAT_PUMP,
            "crm": cls.CRM,
            "controlling": cls.CONTROLLING,
            "admin": cls.ADMIN,
            "pdf": cls.PDF,
            "analysis": cls.ANALYSIS,
            "calculator": cls.CALCULATOR
        }
        return mapping.get(feature.lower(), cls.FILE)


# ==================== ANIMATION SETTINGS ====================

class Animations:
    """CSS Animation Definitionen"""
    
    # Transition Durations
    DURATION_FAST = "150ms"
    DURATION_NORMAL = "300ms"
    DURATION_SLOW = "500ms"
    
    # Easing Functions
    EASE_IN = "cubic-bezier(0.4, 0, 1, 1)"
    EASE_OUT = "cubic-bezier(0, 0, 0.2, 1)"
    EASE_IN_OUT = "cubic-bezier(0.4, 0, 0.2, 1)"
    
    # Standard Transitions
    TRANSITION_ALL = f"all {DURATION_NORMAL} {EASE_IN_OUT}"
    TRANSITION_COLORS = f"background-color {DURATION_NORMAL} {EASE_IN_OUT}, color {DURATION_NORMAL} {EASE_IN_OUT}"
    TRANSITION_TRANSFORM = f"transform {DURATION_NORMAL} {EASE_OUT}"
    
    # Keyframe Animations
    FADE_IN = """
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    """
    
    SLIDE_IN_RIGHT = """
    @keyframes slideInRight {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    """
    
    SHIMMER = """
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    """


# ==================== UTILITY FUNCTIONS ====================

def apply_custom_css():
    """Wendet globale CSS-Styles an (für Streamlit)"""
    css = f"""
    <style>
    /* Global Styles */
    :root {{
        --color-primary: {ColorPalette.PRIMARY};
        --color-secondary: {ColorPalette.SECONDARY};
        --color-success: {ColorPalette.SUCCESS};
        --color-warning: {ColorPalette.WARNING};
        --color-error: {ColorPalette.ERROR};
        --color-info: {ColorPalette.INFO};
        
        --font-family: {Typography.FONT_FAMILY_PRIMARY};
        --font-size-base: {Typography.FONT_SIZE_BODY};
        
        --spacing-sm: {Spacing.SM};
        --spacing-md: {Spacing.MD};
        --spacing-lg: {Spacing.LG};
        
        --border-radius: {BorderStyles.RADIUS_MD};
        --shadow: {Shadows.SHADOW_MD};
    }}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: {Typography.FONT_FAMILY_PRIMARY};
        color: {ColorPalette.TEXT_PRIMARY};
        font-weight: {Typography.WEIGHT_BOLD};
    }}
    
    h1 {{ font-size: {Typography.FONT_SIZE_H1}; }}
    h2 {{ font-size: {Typography.FONT_SIZE_H2}; }}
    h3 {{ font-size: {Typography.FONT_SIZE_H3}; }}
    h4 {{ font-size: {Typography.FONT_SIZE_H4}; }}
    h5 {{ font-size: {Typography.FONT_SIZE_H5}; }}
    h6 {{ font-size: {Typography.FONT_SIZE_H6}; }}
    
    /* Smooth Transitions */
    * {{
        transition: {Animations.TRANSITION_COLORS};
    }}
    
    /* Card Hover Effects */
    .card-hover {{
        transition: {Animations.TRANSITION_ALL};
    }}
    
    .card-hover:hover {{
        box-shadow: {Shadows.SHADOW_LG};
        transform: translateY(-2px);
    }}
    
    /* Animations */
    {Animations.FADE_IN}
    {Animations.SLIDE_IN_RIGHT}
    {Animations.SHIMMER}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {ColorPalette.BACKGROUND_DARK};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {ColorPalette.SECONDARY_LIGHT};
        border-radius: {BorderStyles.RADIUS_FULL};
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {ColorPalette.SECONDARY};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def get_component_style(
    component_type: str,
    variant: str = "default",
    size: str = "md"
) -> Dict[str, str]:
    """
    Gibt Style-Dictionary für einen Component-Typ zurück
    
    Args:
        component_type: "button", "card", "badge"
        variant: Variant-Name (z.B. "primary", "elevated", "success")
        size: Größe (z.B. "sm", "md", "lg")
    
    Returns:
        Dictionary mit CSS-Properties
    """
    if component_type == "button":
        base_style = ComponentVariants.BUTTON_VARIANTS.get(variant, ComponentVariants.BUTTON_VARIANTS["primary"])
        size_style = ComponentVariants.BUTTON_SIZES.get(size, ComponentVariants.BUTTON_SIZES["md"])
        return {**base_style, **size_style}
    
    elif component_type == "card":
        return ComponentVariants.CARD_VARIANTS.get(variant, ComponentVariants.CARD_VARIANTS["elevated"])
    
    elif component_type == "badge":
        return ComponentVariants.BADGE_VARIANTS.get(variant, ComponentVariants.BADGE_VARIANTS["default"])
    
    return {}


# ==================== EXPORT ====================

__all__ = [
    "ColorPalette",
    "Typography",
    "Spacing",
    "BorderStyles",
    "Shadows",
    "ComponentVariants",
    "Breakpoints",
    "IconMapping",
    "Animations",
    "apply_custom_css",
    "get_component_style"
]
