"""
Theme Data Models

Defines all data structures for theme tokens including colors,
typography, spacing, shadows, borders, and animations.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ColorTokens:
    """Farb-Tokens für Theme"""
    # Base colors
    background: str
    foreground: str
    
    # Component colors
    primary: str
    primary_foreground: str
    secondary: str
    secondary_foreground: str
    accent: str
    accent_foreground: str
    
    # Semantic colors
    success: str
    warning: str
    error: str
    info: str
    
    # UI colors
    muted: str
    muted_foreground: str
    border: str
    input: str
    ring: str
    
    # Chart colors
    chart_1: str
    chart_2: str
    chart_3: str
    chart_4: str
    chart_5: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ColorTokens':
        """Erstellt ColorTokens aus Dictionary"""
        return cls(**data)

    def to_dict(self) -> Dict[str, str]:
        """Konvertiert zu Dictionary"""
        return {
            'background': self.background,
            'foreground': self.foreground,
            'primary': self.primary,
            'primary_foreground': self.primary_foreground,
            'secondary': self.secondary,
            'secondary_foreground': self.secondary_foreground,
            'accent': self.accent,
            'accent_foreground': self.accent_foreground,
            'success': self.success,
            'warning': self.warning,
            'error': self.error,
            'info': self.info,
            'muted': self.muted,
            'muted_foreground': self.muted_foreground,
            'border': self.border,
            'input': self.input,
            'ring': self.ring,
            'chart_1': self.chart_1,
            'chart_2': self.chart_2,
            'chart_3': self.chart_3,
            'chart_4': self.chart_4,
            'chart_5': self.chart_5
        }


@dataclass
class TypographyTokens:
    """Typografie-Tokens für Theme"""
    font_family: str
    font_family_mono: str
    
    # Font sizes
    font_size_xs: str
    font_size_sm: str
    font_size_base: str
    font_size_lg: str
    font_size_xl: str
    font_size_2xl: str
    
    # Font weights
    font_weight_normal: int
    font_weight_medium: int
    font_weight_semibold: int
    font_weight_bold: int
    
    # Line heights
    line_height_tight: float
    line_height_normal: float
    line_height_relaxed: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TypographyTokens':
        """Erstellt TypographyTokens aus Dictionary"""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'font_family': self.font_family,
            'font_family_mono': self.font_family_mono,
            'font_size_xs': self.font_size_xs,
            'font_size_sm': self.font_size_sm,
            'font_size_base': self.font_size_base,
            'font_size_lg': self.font_size_lg,
            'font_size_xl': self.font_size_xl,
            'font_size_2xl': self.font_size_2xl,
            'font_weight_normal': self.font_weight_normal,
            'font_weight_medium': self.font_weight_medium,
            'font_weight_semibold': self.font_weight_semibold,
            'font_weight_bold': self.font_weight_bold,
            'line_height_tight': self.line_height_tight,
            'line_height_normal': self.line_height_normal,
            'line_height_relaxed': self.line_height_relaxed
        }


@dataclass
class SpacingTokens:
    """Abstands-Tokens für Theme"""
    spacing_0: str
    spacing_1: str  # 0.25rem
    spacing_2: str  # 0.5rem
    spacing_3: str  # 0.75rem
    spacing_4: str  # 1rem
    spacing_6: str  # 1.5rem
    spacing_8: str  # 2rem
    spacing_12: str  # 3rem
    spacing_16: str  # 4rem

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'SpacingTokens':
        """Erstellt SpacingTokens aus Dictionary"""
        return cls(**data)

    def to_dict(self) -> Dict[str, str]:
        """Konvertiert zu Dictionary"""
        return {
            'spacing_0': self.spacing_0,
            'spacing_1': self.spacing_1,
            'spacing_2': self.spacing_2,
            'spacing_3': self.spacing_3,
            'spacing_4': self.spacing_4,
            'spacing_6': self.spacing_6,
            'spacing_8': self.spacing_8,
            'spacing_12': self.spacing_12,
            'spacing_16': self.spacing_16
        }


@dataclass
class ShadowTokens:
    """Schatten-Tokens für Theme"""
    shadow_sm: str
    shadow_md: str
    shadow_lg: str
    shadow_xl: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ShadowTokens':
        """Erstellt ShadowTokens aus Dictionary"""
        return cls(**data)

    def to_dict(self) -> Dict[str, str]:
        """Konvertiert zu Dictionary"""
        return {
            'shadow_sm': self.shadow_sm,
            'shadow_md': self.shadow_md,
            'shadow_lg': self.shadow_lg,
            'shadow_xl': self.shadow_xl
        }


@dataclass
class BorderTokens:
    """Border-Tokens für Theme"""
    border_width: str
    border_radius_sm: str
    border_radius_md: str
    border_radius_lg: str
    border_radius_full: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'BorderTokens':
        """Erstellt BorderTokens aus Dictionary"""
        return cls(**data)

    def to_dict(self) -> Dict[str, str]:
        """Konvertiert zu Dictionary"""
        return {
            'border_width': self.border_width,
            'border_radius_sm': self.border_radius_sm,
            'border_radius_md': self.border_radius_md,
            'border_radius_lg': self.border_radius_lg,
            'border_radius_full': self.border_radius_full
        }


@dataclass
class AnimationTokens:
    """Animations-Tokens für Theme"""
    transition_fast: str    # 150ms
    transition_base: str    # 200ms
    transition_slow: str    # 300ms
    easing_default: str     # cubic-bezier(0.4, 0, 0.2, 1)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'AnimationTokens':
        """Erstellt AnimationTokens aus Dictionary"""
        return cls(**data)

    def to_dict(self) -> Dict[str, str]:
        """Konvertiert zu Dictionary"""
        return {
            'transition_fast': self.transition_fast,
            'transition_base': self.transition_base,
            'transition_slow': self.transition_slow,
            'easing_default': self.easing_default
        }


@dataclass
class Theme:
    """Repräsentiert ein vollständiges Theme"""
    name: str
    display_name: str
    colors: ColorTokens
    typography: TypographyTokens
    spacing: SpacingTokens
    shadows: ShadowTokens
    borders: BorderTokens
    animations: AnimationTokens

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """Erstellt Theme aus Dictionary"""
        return cls(
            name=data['name'],
            display_name=data['display_name'],
            colors=ColorTokens.from_dict(data['colors']),
            typography=TypographyTokens.from_dict(data['typography']),
            spacing=SpacingTokens.from_dict(data['spacing']),
            shadows=ShadowTokens.from_dict(data['shadows']),
            borders=BorderTokens.from_dict(data['borders']),
            animations=AnimationTokens.from_dict(data['animations'])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Theme zu Dictionary"""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'colors': self.colors.to_dict(),
            'typography': self.typography.to_dict(),
            'spacing': self.spacing.to_dict(),
            'shadows': self.shadows.to_dict(),
            'borders': self.borders.to_dict(),
            'animations': self.animations.to_dict()
        }
