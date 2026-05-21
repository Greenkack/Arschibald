"""
Theme System API

Provides REST API for theme management:
- Light/dark theme toggle
- Custom color themes (blue, green, purple)
- Corporate design customization
- Theme persistence
- Chart and PDF theme application

Requirements: funktionen.txt - "Theme-System"
Task: 282. Theme System Implementation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/themes", tags=["Theme System"])


# ==================== Enums ====================

class ThemeMode(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class ThemeColor(str, Enum):
    BLUE = "blue"
    GREEN = "green"
    PURPLE = "purple"
    ORANGE = "orange"
    RED = "red"
    TEAL = "teal"
    CUSTOM = "custom"


# ==================== Pydantic Models ====================

class ColorPalette(BaseModel):
    """Color palette definition"""
    primary: str = "#3B82F6"
    primary_hover: str = "#2563EB"
    primary_light: str = "#DBEAFE"
    secondary: str = "#6B7280"
    secondary_hover: str = "#4B5563"
    success: str = "#10B981"
    warning: str = "#F59E0B"
    error: str = "#EF4444"
    info: str = "#3B82F6"
    background: str = "#FFFFFF"
    surface: str = "#F9FAFB"
    text_primary: str = "#111827"
    text_secondary: str = "#6B7280"
    border: str = "#E5E7EB"


class ChartColors(BaseModel):
    """Chart color scheme"""
    series: List[str] = [
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Yellow
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#EC4899",  # Pink
        "#06B6D4",  # Cyan
        "#F97316",  # Orange
    ]
    grid: str = "#E5E7EB"
    axis: str = "#6B7280"
    tooltip_bg: str = "#1F2937"
    tooltip_text: str = "#FFFFFF"


class Typography(BaseModel):
    """Typography settings"""
    font_family: str = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    font_size_base: str = "14px"
    font_size_sm: str = "12px"
    font_size_lg: str = "16px"
    font_size_xl: str = "20px"
    font_size_2xl: str = "24px"
    font_weight_normal: int = 400
    font_weight_medium: int = 500
    font_weight_bold: int = 700
    line_height: float = 1.5


class Spacing(BaseModel):
    """Spacing settings"""
    xs: str = "4px"
    sm: str = "8px"
    md: str = "16px"
    lg: str = "24px"
    xl: str = "32px"
    xxl: str = "48px"


class BorderRadius(BaseModel):
    """Border radius settings"""
    none: str = "0"
    sm: str = "4px"
    md: str = "8px"
    lg: str = "12px"
    xl: str = "16px"
    full: str = "9999px"


class Shadow(BaseModel):
    """Shadow settings"""
    sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
    xl: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1)"


class ThemeConfig(BaseModel):
    """Complete theme configuration"""
    id: str
    name: str
    mode: ThemeMode = ThemeMode.LIGHT
    color_scheme: ThemeColor = ThemeColor.BLUE
    colors: ColorPalette = ColorPalette()
    chart_colors: ChartColors = ChartColors()
    typography: Typography = Typography()
    spacing: Spacing = Spacing()
    border_radius: BorderRadius = BorderRadius()
    shadows: Shadow = Shadow()
    is_default: bool = False
    is_custom: bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class UserThemePreference(BaseModel):
    """User theme preference"""
    user_id: str
    theme_id: str
    mode: ThemeMode = ThemeMode.LIGHT
    custom_overrides: Optional[Dict[str, Any]] = None


# ==================== Predefined Themes ====================

LIGHT_BLUE_THEME = ThemeConfig(
    id="light_blue",
    name="Hell Blau",
    mode=ThemeMode.LIGHT,
    color_scheme=ThemeColor.BLUE,
    colors=ColorPalette(
        primary="#3B82F6",
        primary_hover="#2563EB",
        primary_light="#DBEAFE",
        background="#FFFFFF",
        surface="#F9FAFB",
        text_primary="#111827",
        text_secondary="#6B7280",
        border="#E5E7EB"
    ),
    is_default=True
)

DARK_BLUE_THEME = ThemeConfig(
    id="dark_blue",
    name="Dunkel Blau",
    mode=ThemeMode.DARK,
    color_scheme=ThemeColor.BLUE,
    colors=ColorPalette(
        primary="#60A5FA",
        primary_hover="#3B82F6",
        primary_light="#1E3A5F",
        background="#111827",
        surface="#1F2937",
        text_primary="#F9FAFB",
        text_secondary="#9CA3AF",
        border="#374151"
    )
)

LIGHT_GREEN_THEME = ThemeConfig(
    id="light_green",
    name="Hell Grün",
    mode=ThemeMode.LIGHT,
    color_scheme=ThemeColor.GREEN,
    colors=ColorPalette(
        primary="#10B981",
        primary_hover="#059669",
        primary_light="#D1FAE5",
        background="#FFFFFF",
        surface="#F9FAFB",
        text_primary="#111827",
        text_secondary="#6B7280",
        border="#E5E7EB"
    ),
    chart_colors=ChartColors(
        series=["#10B981", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4", "#F97316"]
    )
)

DARK_GREEN_THEME = ThemeConfig(
    id="dark_green",
    name="Dunkel Grün",
    mode=ThemeMode.DARK,
    color_scheme=ThemeColor.GREEN,
    colors=ColorPalette(
        primary="#34D399",
        primary_hover="#10B981",
        primary_light="#064E3B",
        background="#111827",
        surface="#1F2937",
        text_primary="#F9FAFB",
        text_secondary="#9CA3AF",
        border="#374151"
    )
)

LIGHT_PURPLE_THEME = ThemeConfig(
    id="light_purple",
    name="Hell Lila",
    mode=ThemeMode.LIGHT,
    color_scheme=ThemeColor.PURPLE,
    colors=ColorPalette(
        primary="#8B5CF6",
        primary_hover="#7C3AED",
        primary_light="#EDE9FE",
        background="#FFFFFF",
        surface="#F9FAFB",
        text_primary="#111827",
        text_secondary="#6B7280",
        border="#E5E7EB"
    ),
    chart_colors=ChartColors(
        series=["#8B5CF6", "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#EC4899", "#06B6D4", "#F97316"]
    )
)

DARK_PURPLE_THEME = ThemeConfig(
    id="dark_purple",
    name="Dunkel Lila",
    mode=ThemeMode.DARK,
    color_scheme=ThemeColor.PURPLE,
    colors=ColorPalette(
        primary="#A78BFA",
        primary_hover="#8B5CF6",
        primary_light="#4C1D95",
        background="#111827",
        surface="#1F2937",
        text_primary="#F9FAFB",
        text_secondary="#9CA3AF",
        border="#374151"
    )
)

# Store all themes
_themes: Dict[str, ThemeConfig] = {
    "light_blue": LIGHT_BLUE_THEME,
    "dark_blue": DARK_BLUE_THEME,
    "light_green": LIGHT_GREEN_THEME,
    "dark_green": DARK_GREEN_THEME,
    "light_purple": LIGHT_PURPLE_THEME,
    "dark_purple": DARK_PURPLE_THEME,
}

# User preferences storage
_user_preferences: Dict[str, UserThemePreference] = {}


# ==================== Helper Functions ====================

def get_theme_css_variables(theme: ThemeConfig) -> Dict[str, str]:
    """Generate CSS variables from theme config."""
    return {
        "--color-primary": theme.colors.primary,
        "--color-primary-hover": theme.colors.primary_hover,
        "--color-primary-light": theme.colors.primary_light,
        "--color-secondary": theme.colors.secondary,
        "--color-success": theme.colors.success,
        "--color-warning": theme.colors.warning,
        "--color-error": theme.colors.error,
        "--color-info": theme.colors.info,
        "--color-background": theme.colors.background,
        "--color-surface": theme.colors.surface,
        "--color-text-primary": theme.colors.text_primary,
        "--color-text-secondary": theme.colors.text_secondary,
        "--color-border": theme.colors.border,
        "--font-family": theme.typography.font_family,
        "--font-size-base": theme.typography.font_size_base,
        "--font-size-sm": theme.typography.font_size_sm,
        "--font-size-lg": theme.typography.font_size_lg,
        "--spacing-xs": theme.spacing.xs,
        "--spacing-sm": theme.spacing.sm,
        "--spacing-md": theme.spacing.md,
        "--spacing-lg": theme.spacing.lg,
        "--spacing-xl": theme.spacing.xl,
        "--border-radius-sm": theme.border_radius.sm,
        "--border-radius-md": theme.border_radius.md,
        "--border-radius-lg": theme.border_radius.lg,
        "--shadow-sm": theme.shadows.sm,
        "--shadow-md": theme.shadows.md,
        "--shadow-lg": theme.shadows.lg,
    }


def get_chart_theme(theme: ThemeConfig) -> Dict[str, Any]:
    """Generate chart theme configuration."""
    return {
        "colors": theme.chart_colors.series,
        "grid": {
            "color": theme.chart_colors.grid,
            "strokeDasharray": "3 3"
        },
        "axis": {
            "color": theme.chart_colors.axis,
            "fontSize": 12
        },
        "tooltip": {
            "backgroundColor": theme.chart_colors.tooltip_bg,
            "textColor": theme.chart_colors.tooltip_text,
            "borderRadius": theme.border_radius.md
        },
        "legend": {
            "textColor": theme.colors.text_primary
        }
    }


def get_pdf_theme(theme: ThemeConfig) -> Dict[str, Any]:
    """Generate PDF theme configuration."""
    return {
        "primary_color": theme.colors.primary,
        "secondary_color": theme.colors.secondary,
        "text_color": theme.colors.text_primary,
        "background_color": theme.colors.background,
        "accent_color": theme.colors.primary_light,
        "chart_colors": theme.chart_colors.series,
        "font_family": "Helvetica",  # PDF-safe font
        "heading_size": 14,
        "body_size": 10,
        "caption_size": 8
    }


# ==================== API Endpoints ====================

@router.get("/")
async def get_all_themes():
    """Get all available themes."""
    return {
        "themes": list(_themes.values()),
        "total": len(_themes)
    }


@router.get("/{theme_id}")
async def get_theme(theme_id: str):
    """Get specific theme configuration."""
    if theme_id not in _themes:
        raise HTTPException(status_code=404, detail="Theme nicht gefunden")
    return {"theme": _themes[theme_id]}


@router.get("/{theme_id}/css-variables")
async def get_theme_css(theme_id: str):
    """Get CSS variables for theme."""
    if theme_id not in _themes:
        raise HTTPException(status_code=404, detail="Theme nicht gefunden")
    
    theme = _themes[theme_id]
    css_vars = get_theme_css_variables(theme)
    
    # Generate CSS string
    css_string = ":root {\n"
    for var, value in css_vars.items():
        css_string += f"  {var}: {value};\n"
    css_string += "}"
    
    return {
        "theme_id": theme_id,
        "variables": css_vars,
        "css": css_string
    }


@router.get("/{theme_id}/chart-config")
async def get_theme_chart_config(theme_id: str):
    """Get chart configuration for theme."""
    if theme_id not in _themes:
        raise HTTPException(status_code=404, detail="Theme nicht gefunden")
    
    theme = _themes[theme_id]
    return {
        "theme_id": theme_id,
        "chart_config": get_chart_theme(theme)
    }


@router.get("/{theme_id}/pdf-config")
async def get_theme_pdf_config(theme_id: str):
    """Get PDF configuration for theme."""
    if theme_id not in _themes:
        raise HTTPException(status_code=404, detail="Theme nicht gefunden")
    
    theme = _themes[theme_id]
    return {
        "theme_id": theme_id,
        "pdf_config": get_pdf_theme(theme)
    }


@router.post("/custom")
async def create_custom_theme(theme: ThemeConfig):
    """Create custom theme."""
    theme.id = f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    theme.is_custom = True
    theme.created_at = datetime.now()
    theme.updated_at = datetime.now()
    
    _themes[theme.id] = theme
    
    return {"theme": theme, "created": True}


@router.put("/custom/{theme_id}")
async def update_custom_theme(theme_id: str, theme: ThemeConfig):
    """Update custom theme."""
    if theme_id not in _themes:
        raise HTTPException(status_code=404, detail="Theme nicht gefunden")
    
    existing = _themes[theme_id]
    if not existing.is_custom:
        raise HTTPException(status_code=400, detail="Standard-Themes können nicht bearbeitet werden")
    
    theme.id = theme_id
    theme.updated_at = datetime.now()
    _themes[theme_id] = theme
    
    return {"theme": theme, "updated": True}


@router.delete("/custom/{theme_id}")
async def delete_custom_theme(theme_id: str):
    """Delete custom theme."""
    if theme_id not in _themes:
        raise HTTPException(status_code=404, detail="Theme nicht gefunden")
    
    if not _themes[theme_id].is_custom:
        raise HTTPException(status_code=400, detail="Standard-Themes können nicht gelöscht werden")
    
    del _themes[theme_id]
    return {"deleted": True, "theme_id": theme_id}


@router.get("/user/{user_id}/preference")
async def get_user_theme_preference(user_id: str):
    """Get user's theme preference."""
    if user_id in _user_preferences:
        pref = _user_preferences[user_id]
        theme = _themes.get(pref.theme_id, LIGHT_BLUE_THEME)
        return {
            "preference": pref,
            "theme": theme
        }
    
    # Return default
    return {
        "preference": UserThemePreference(user_id=user_id, theme_id="light_blue"),
        "theme": LIGHT_BLUE_THEME
    }


@router.put("/user/{user_id}/preference")
async def set_user_theme_preference(user_id: str, preference: UserThemePreference):
    """Set user's theme preference."""
    if preference.theme_id not in _themes:
        raise HTTPException(status_code=404, detail="Theme nicht gefunden")
    
    preference.user_id = user_id
    _user_preferences[user_id] = preference
    
    return {
        "preference": preference,
        "theme": _themes[preference.theme_id]
    }


@router.post("/user/{user_id}/toggle-mode")
async def toggle_theme_mode(user_id: str):
    """Toggle between light and dark mode."""
    if user_id not in _user_preferences:
        _user_preferences[user_id] = UserThemePreference(user_id=user_id, theme_id="light_blue")
    
    pref = _user_preferences[user_id]
    current_theme = _themes.get(pref.theme_id, LIGHT_BLUE_THEME)
    
    # Find matching theme in opposite mode
    if current_theme.mode == ThemeMode.LIGHT:
        new_mode = ThemeMode.DARK
        new_theme_id = f"dark_{current_theme.color_scheme.value}"
    else:
        new_mode = ThemeMode.LIGHT
        new_theme_id = f"light_{current_theme.color_scheme.value}"
    
    if new_theme_id in _themes:
        pref.theme_id = new_theme_id
        pref.mode = new_mode
    
    return {
        "preference": pref,
        "theme": _themes.get(pref.theme_id, LIGHT_BLUE_THEME)
    }


@router.get("/colors/schemes")
async def get_color_schemes():
    """Get available color schemes."""
    schemes = {}
    for color in ThemeColor:
        if color != ThemeColor.CUSTOM:
            light_id = f"light_{color.value}"
            dark_id = f"dark_{color.value}"
            schemes[color.value] = {
                "name": color.value.capitalize(),
                "light": _themes.get(light_id),
                "dark": _themes.get(dark_id)
            }
    
    return {"schemes": schemes}


@router.get("/preview/{theme_id}")
async def get_theme_preview(theme_id: str):
    """Get theme preview data for UI."""
    if theme_id not in _themes:
        raise HTTPException(status_code=404, detail="Theme nicht gefunden")
    
    theme = _themes[theme_id]
    
    return {
        "theme_id": theme_id,
        "name": theme.name,
        "mode": theme.mode,
        "preview": {
            "primary": theme.colors.primary,
            "background": theme.colors.background,
            "surface": theme.colors.surface,
            "text": theme.colors.text_primary,
            "chart_colors": theme.chart_colors.series[:4]
        }
    }


@router.get("/health/check")
async def health_check():
    """Health check for theme service."""
    return {
        "status": "healthy",
        "service": "theme-system",
        "themes": len(_themes),
        "custom_themes": len([t for t in _themes.values() if t.is_custom]),
        "user_preferences": len(_user_preferences),
        "timestamp": datetime.now().isoformat()
    }
