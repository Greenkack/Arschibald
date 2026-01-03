"""
Task 34: Theme-Presets für Branchen
===================================
Branchenspezifische Theme-Presets.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ThemePreset:
    """Theme preset configuration."""
    name: str
    display_name: str
    category: str
    colors: Dict[str, str]
    description: str


THEME_PRESETS: Dict[str, ThemePreset] = {
    # Solar/Energy
    "solar_bright": ThemePreset(
        name="solar_bright",
        display_name="Solar Bright",
        category="Solar",
        colors={
            "primary": "#f59e0b",
            "secondary": "#fbbf24",
            "background": "#fffbeb",
            "foreground": "#78350f",
            "accent": "#fef3c7",
            "success": "#22c55e",
            "warning": "#f97316",
            "destructive": "#ef4444"
        },
        description="Helles, sonniges Theme für Solar-Anwendungen"
    ),
    "solar_professional": ThemePreset(
        name="solar_professional",
        display_name="Solar Professional",
        category="Solar",
        colors={
            "primary": "#0369a1",
            "secondary": "#0284c7",
            "background": "#f0f9ff",
            "foreground": "#0c4a6e",
            "accent": "#e0f2fe",
            "success": "#16a34a",
            "warning": "#ea580c",
            "destructive": "#dc2626"
        },
        description="Professionelles Theme für Solar-Unternehmen"
    ),
    
    # Finance
    "finance_classic": ThemePreset(
        name="finance_classic",
        display_name="Finance Classic",
        category="Finance",
        colors={
            "primary": "#1e40af",
            "secondary": "#3b82f6",
            "background": "#f8fafc",
            "foreground": "#1e293b",
            "accent": "#dbeafe",
            "success": "#15803d",
            "warning": "#b45309",
            "destructive": "#b91c1c"
        },
        description="Klassisches Finanz-Theme mit Vertrauensfarben"
    ),
    "finance_modern": ThemePreset(
        name="finance_modern",
        display_name="Finance Modern",
        category="Finance",
        colors={
            "primary": "#7c3aed",
            "secondary": "#8b5cf6",
            "background": "#faf5ff",
            "foreground": "#4c1d95",
            "accent": "#ede9fe",
            "success": "#059669",
            "warning": "#d97706",
            "destructive": "#dc2626"
        },
        description="Modernes Fintech-Theme"
    ),
    
    # Healthcare
    "healthcare_clean": ThemePreset(
        name="healthcare_clean",
        display_name="Healthcare Clean",
        category="Healthcare",
        colors={
            "primary": "#0891b2",
            "secondary": "#06b6d4",
            "background": "#ecfeff",
            "foreground": "#164e63",
            "accent": "#cffafe",
            "success": "#10b981",
            "warning": "#f59e0b",
            "destructive": "#ef4444"
        },
        description="Sauberes, beruhigendes Healthcare-Theme"
    ),
    "healthcare_professional": ThemePreset(
        name="healthcare_professional",
        display_name="Healthcare Professional",
        category="Healthcare",
        colors={
            "primary": "#0d9488",
            "secondary": "#14b8a6",
            "background": "#f0fdfa",
            "foreground": "#134e4a",
            "accent": "#ccfbf1",
            "success": "#22c55e",
            "warning": "#eab308",
            "destructive": "#f43f5e"
        },
        description="Professionelles medizinisches Theme"
    ),
    
    # Technology
    "tech_dark": ThemePreset(
        name="tech_dark",
        display_name="Tech Dark",
        category="Technology",
        colors={
            "primary": "#6366f1",
            "secondary": "#818cf8",
            "background": "#0f172a",
            "foreground": "#e2e8f0",
            "accent": "#1e293b",
            "success": "#4ade80",
            "warning": "#fbbf24",
            "destructive": "#f87171"
        },
        description="Dunkles Tech-Theme für Entwickler"
    ),
    "tech_neon": ThemePreset(
        name="tech_neon",
        display_name="Tech Neon",
        category="Technology",
        colors={
            "primary": "#22d3ee",
            "secondary": "#67e8f9",
            "background": "#18181b",
            "foreground": "#fafafa",
            "accent": "#27272a",
            "success": "#a3e635",
            "warning": "#facc15",
            "destructive": "#fb7185"
        },
        description="Neon-Theme für moderne Tech-Apps"
    ),
    
    # Nature/Eco
    "eco_green": ThemePreset(
        name="eco_green",
        display_name="Eco Green",
        category="Nature",
        colors={
            "primary": "#16a34a",
            "secondary": "#22c55e",
            "background": "#f0fdf4",
            "foreground": "#14532d",
            "accent": "#dcfce7",
            "success": "#15803d",
            "warning": "#ca8a04",
            "destructive": "#dc2626"
        },
        description="Umweltfreundliches grünes Theme"
    ),
    "nature_earth": ThemePreset(
        name="nature_earth",
        display_name="Nature Earth",
        category="Nature",
        colors={
            "primary": "#854d0e",
            "secondary": "#a16207",
            "background": "#fefce8",
            "foreground": "#422006",
            "accent": "#fef9c3",
            "success": "#65a30d",
            "warning": "#d97706",
            "destructive": "#b91c1c"
        },
        description="Erdiges Natur-Theme"
    ),
    
    # Corporate
    "corporate_blue": ThemePreset(
        name="corporate_blue",
        display_name="Corporate Blue",
        category="Corporate",
        colors={
            "primary": "#1d4ed8",
            "secondary": "#2563eb",
            "background": "#ffffff",
            "foreground": "#1e3a8a",
            "accent": "#eff6ff",
            "success": "#059669",
            "warning": "#d97706",
            "destructive": "#dc2626"
        },
        description="Klassisches Corporate-Theme"
    ),
    "corporate_gray": ThemePreset(
        name="corporate_gray",
        display_name="Corporate Gray",
        category="Corporate",
        colors={
            "primary": "#475569",
            "secondary": "#64748b",
            "background": "#f8fafc",
            "foreground": "#1e293b",
            "accent": "#f1f5f9",
            "success": "#16a34a",
            "warning": "#ea580c",
            "destructive": "#dc2626"
        },
        description="Neutrales Corporate-Theme"
    ),
}


def get_preset(name: str) -> ThemePreset:
    """Get a theme preset by name."""
    return THEME_PRESETS.get(name)


def get_presets_by_category(category: str) -> List[ThemePreset]:
    """Get all presets in a category."""
    return [p for p in THEME_PRESETS.values() if p.category == category]


def get_all_categories() -> List[str]:
    """Get all available categories."""
    return list(set(p.category for p in THEME_PRESETS.values()))


def get_all_presets() -> List[ThemePreset]:
    """Get all available presets."""
    return list(THEME_PRESETS.values())
