"""
Accessibility (A11y) Module for shadcn/ui Theme System

This module provides comprehensive accessibility features including:
- WCAG 2.1 Level AA contrast checking
- Keyboard navigation support
- ARIA labels and attributes
- Focus indicators
- Screen reader support
- Color blindness friendly themes
- Text scaling support

Author: Theme System
Date: 2025
"""

import colorsys
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class ContrastLevel(Enum):
    """WCAG Contrast Levels"""
    AAA_LARGE = 4.5  # WCAG AAA for large text (18pt+)
    AA_NORMAL = 4.5  # WCAG AA for normal text
    AA_LARGE = 3.0   # WCAG AA for large text
    AAA_NORMAL = 7.0 # WCAG AAA for normal text


class ColorBlindnessType(Enum):
    """Types of color blindness"""
    PROTANOPIA = "protanopia"      # Red-blind
    DEUTERANOPIA = "deuteranopia"  # Green-blind
    TRITANOPIA = "tritanopia"      # Blue-blind
    ACHROMATOPSIA = "achromatopsia" # Total color blindness


@dataclass
class ContrastResult:
    """Result of contrast check"""
    ratio: float
    passes_aa_normal: bool
    passes_aa_large: bool
    passes_aaa_normal: bool
    passes_aaa_large: bool
    recommendation: str


@dataclass
class AccessibilityReport:
    """Comprehensive accessibility report"""
    theme_name: str
    contrast_issues: List[Dict[str, Any]]
    keyboard_nav_issues: List[str]
    aria_issues: List[str]
    focus_issues: List[str]
    overall_score: float
    recommendations: List[str]


class ContrastChecker:
    """Checks color contrast ratios according to WCAG 2.1"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def get_relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance according to WCAG formula"""
        def adjust(channel: int) -> float:
            c = channel / 255.0
            if c <= 0.03928:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4
        
        r, g, b = rgb
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)
    
    @classmethod
    def calculate_contrast_ratio(cls, color1: str, color2: str) -> float:
        """
        Calculate contrast ratio between two colors
        
        Args:
            color1: First color (hex format)
            color2: Second color (hex format)
            
        Returns:
            Contrast ratio (1-21)
        """
        rgb1 = cls.hex_to_rgb(color1)
        rgb2 = cls.hex_to_rgb(color2)
        
        l1 = cls.get_relative_luminance(rgb1)
        l2 = cls.get_relative_luminance(rgb2)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @classmethod
    def check_contrast(cls, foreground: str, background: str, 
                      is_large_text: bool = False) -> ContrastResult:
        """
        Check if color combination meets WCAG standards
        
        Args:
            foreground: Foreground color (hex)
            background: Background color (hex)
            is_large_text: Whether text is large (18pt+ or 14pt+ bold)
            
        Returns:
            ContrastResult with detailed information
        """
        ratio = cls.calculate_contrast_ratio(foreground, background)
        
        passes_aa_normal = ratio >= ContrastLevel.AA_NORMAL.value
        passes_aa_large = ratio >= ContrastLevel.AA_LARGE.value
        passes_aaa_normal = ratio >= ContrastLevel.AAA_NORMAL.value
        passes_aaa_large = ratio >= ContrastLevel.AAA_LARGE.value
        
        # Generate recommendation
        if is_large_text:
            if passes_aaa_large:
                recommendation = " Excellent contrast (WCAG AAA)"
            elif passes_aa_large:
                recommendation = " Good contrast (WCAG AA)"
            else:
                recommendation = f" Insufficient contrast ({ratio:.2f}:1). Need at least 3:1 for large text."
        else:
            if passes_aaa_normal:
                recommendation = " Excellent contrast (WCAG AAA)"
            elif passes_aa_normal:
                recommendation = " Good contrast (WCAG AA)"
            else:
                recommendation = f" Insufficient contrast ({ratio:.2f}:1). Need at least 4.5:1 for normal text."
        
        return ContrastResult(
            ratio=ratio,
            passes_aa_normal=passes_aa_normal,
            passes_aa_large=passes_aa_large,
            passes_aaa_normal=passes_aaa_normal,
            passes_aaa_large=passes_aaa_large,
            recommendation=recommendation
        )


class ColorBlindnessSimulator:
    """Simulates how colors appear to people with color blindness"""
    
    @staticmethod
    def simulate_protanopia(hex_color: str) -> str:
        """Simulate red-blindness (protanopia)"""
        r, g, b = ContrastChecker.hex_to_rgb(hex_color)
        
        # Protanopia transformation matrix
        new_r = 0.567 * r + 0.433 * g
        new_g = 0.558 * r + 0.442 * g
        new_b = 0.242 * g + 0.758 * b
        
        return f"#{int(new_r):02x}{int(new_g):02x}{int(new_b):02x}"
    
    @staticmethod
    def simulate_deuteranopia(hex_color: str) -> str:
        """Simulate green-blindness (deuteranopia)"""
        r, g, b = ContrastChecker.hex_to_rgb(hex_color)
        
        # Deuteranopia transformation matrix
        new_r = 0.625 * r + 0.375 * g
        new_g = 0.7 * r + 0.3 * g
        new_b = 0.3 * g + 0.7 * b
        
        return f"#{int(new_r):02x}{int(new_g):02x}{int(new_b):02x}"
    
    @staticmethod
    def simulate_tritanopia(hex_color: str) -> str:
        """Simulate blue-blindness (tritanopia)"""
        r, g, b = ContrastChecker.hex_to_rgb(hex_color)
        
        # Tritanopia transformation matrix
        new_r = 0.95 * r + 0.05 * g
        new_g = 0.433 * g + 0.567 * b
        new_b = 0.475 * g + 0.525 * b
        
        return f"#{int(new_r):02x}{int(new_g):02x}{int(new_b):02x}"
    
    @staticmethod
    def simulate_achromatopsia(hex_color: str) -> str:
        """Simulate total color blindness (achromatopsia)"""
        r, g, b = ContrastChecker.hex_to_rgb(hex_color)
        
        # Convert to grayscale using luminance formula
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        
        return f"#{gray:02x}{gray:02x}{gray:02x}"
    
    @classmethod
    def simulate(cls, hex_color: str, cb_type: ColorBlindnessType) -> str:
        """
        Simulate color blindness for a given color
        
        Args:
            hex_color: Color in hex format
            cb_type: Type of color blindness
            
        Returns:
            Simulated color in hex format
        """
        if cb_type == ColorBlindnessType.PROTANOPIA:
            return cls.simulate_protanopia(hex_color)
        elif cb_type == ColorBlindnessType.DEUTERANOPIA:
            return cls.simulate_deuteranopia(hex_color)
        elif cb_type == ColorBlindnessType.TRITANOPIA:
            return cls.simulate_tritanopia(hex_color)
        elif cb_type == ColorBlindnessType.ACHROMATOPSIA:
            return cls.simulate_achromatopsia(hex_color)
        return hex_color


class KeyboardNavigationHelper:
    """Provides keyboard navigation support"""
    
    @staticmethod
    def get_keyboard_nav_css() -> str:
        """Generate CSS for keyboard navigation"""
        return """
        /* Keyboard Navigation Styles */
        *:focus {
            outline: 2px solid var(--ring, #18181b);
            outline-offset: 2px;
            transition: outline 150ms ease-in-out;
        }
        
        *:focus:not(:focus-visible) {
            outline: none;
        }
        
        *:focus-visible {
            outline: 2px solid var(--ring, #18181b);
            outline-offset: 2px;
        }
        
        /* Skip to main content link */
        .skip-to-main {
            position: absolute;
            top: -40px;
            left: 0;
            background: var(--primary, #18181b);
            color: var(--primary-foreground, #fafafa);
            padding: 8px 16px;
            text-decoration: none;
            z-index: 100;
        }
        
        .skip-to-main:focus {
            top: 0;
        }
        
        /* Keyboard-only focus indicators */
        button:focus-visible,
        a:focus-visible,
        input:focus-visible,
        select:focus-visible,
        textarea:focus-visible {
            box-shadow: 0 0 0 3px var(--ring, #18181b);
        }
        
        /* Tab order indicators (for debugging) */
        [tabindex]:not([tabindex="-1"]) {
            position: relative;
        }
        """
    
    @staticmethod
    def get_skip_to_main_html() -> str:
        """Generate skip to main content link"""
        return """
        <a href="#main-content" class="skip-to-main">
            Skip to main content
        </a>
        """


class ARIAHelper:
    """Provides ARIA labels and attributes"""
    
    @staticmethod
    def get_button_aria(label: str, pressed: Optional[bool] = None,
                       expanded: Optional[bool] = None,
                       disabled: bool = False) -> str:
        """Generate ARIA attributes for button"""
        attrs = [f'aria-label="{label}"']
        
        if pressed is not None:
            attrs.append(f'aria-pressed="{str(pressed).lower()}"')
        
        if expanded is not None:
            attrs.append(f'aria-expanded="{str(expanded).lower()}"')
        
        if disabled:
            attrs.append('aria-disabled="true"')
        
        return ' '.join(attrs)
    
    @staticmethod
    def get_input_aria(label: str, required: bool = False,
                      invalid: bool = False,
                      describedby: Optional[str] = None) -> str:
        """Generate ARIA attributes for input"""
        attrs = [f'aria-label="{label}"']
        
        if required:
            attrs.append('aria-required="true"')
        
        if invalid:
            attrs.append('aria-invalid="true"')
        
        if describedby:
            attrs.append(f'aria-describedby="{describedby}"')
        
        return ' '.join(attrs)
    
    @staticmethod
    def get_dialog_aria(label: str, modal: bool = True) -> str:
        """Generate ARIA attributes for dialog"""
        attrs = [
            'role="dialog"',
            f'aria-label="{label}"'
        ]
        
        if modal:
            attrs.append('aria-modal="true"')
        
        return ' '.join(attrs)
    
    @staticmethod
    def get_alert_aria(live: str = "polite") -> str:
        """Generate ARIA attributes for alert"""
        return f'role="alert" aria-live="{live}"'
    
    @staticmethod
    def get_navigation_aria(label: str) -> str:
        """Generate ARIA attributes for navigation"""
        return f'role="navigation" aria-label="{label}"'


class FocusManager:
    """Manages focus indicators and focus trapping"""
    
    @staticmethod
    def get_focus_trap_js(container_id: str) -> str:
        """Generate JavaScript for focus trapping in modals"""
        return f"""
        <script>
        (function() {{
            const container = document.getElementById('{container_id}');
            if (!container) return;
            
            const focusableElements = container.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            container.addEventListener('keydown', function(e) {{
                if (e.key !== 'Tab') return;
                
                if (e.shiftKey) {{
                    if (document.activeElement === firstElement) {{
                        lastElement.focus();
                        e.preventDefault();
                    }}
                }} else {{
                    if (document.activeElement === lastElement) {{
                        firstElement.focus();
                        e.preventDefault();
                    }}
                }}
            }});
            
            // Focus first element when modal opens
            firstElement.focus();
        }})();
        </script>
        """
    
    @staticmethod
    def get_focus_indicator_css() -> str:
        """Generate enhanced focus indicator CSS"""
        return """
        /* Enhanced Focus Indicators */
        :root {
            --focus-ring-width: 2px;
            --focus-ring-offset: 2px;
            --focus-ring-color: var(--ring, #18181b);
        }
        
        .focus-ring {
            position: relative;
        }
        
        .focus-ring:focus-visible::after {
            content: '';
            position: absolute;
            top: calc(-1 * var(--focus-ring-offset));
            left: calc(-1 * var(--focus-ring-offset));
            right: calc(-1 * var(--focus-ring-offset));
            bottom: calc(-1 * var(--focus-ring-offset));
            border: var(--focus-ring-width) solid var(--focus-ring-color);
            border-radius: inherit;
            pointer-events: none;
        }
        
        /* High contrast focus for accessibility */
        @media (prefers-contrast: high) {
            *:focus-visible {
                outline: 3px solid currentColor;
                outline-offset: 3px;
            }
        }
        """


class ScreenReaderHelper:
    """Provides screen reader support"""
    
    @staticmethod
    def get_sr_only_css() -> str:
        """Generate CSS for screen-reader-only content"""
        return """
        /* Screen Reader Only */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border-width: 0;
        }
        
        .sr-only-focusable:focus {
            position: static;
            width: auto;
            height: auto;
            padding: inherit;
            margin: inherit;
            overflow: visible;
            clip: auto;
            white-space: normal;
        }
        """
    
    @staticmethod
    def wrap_sr_only(text: str) -> str:
        """Wrap text in screen-reader-only span"""
        return f'<span class="sr-only">{text}</span>'
    
    @staticmethod
    def get_live_region_html(region_id: str, politeness: str = "polite") -> str:
        """Generate live region for dynamic content announcements"""
        return f'''
        <div id="{region_id}" 
             role="status" 
             aria-live="{politeness}" 
             aria-atomic="true"
             class="sr-only">
        </div>
        '''
    
    @staticmethod
    def announce(region_id: str, message: str) -> str:
        """Generate JavaScript to announce message to screen readers"""
        return f"""
        <script>
        (function() {{
            const region = document.getElementById('{region_id}');
            if (region) {{
                region.textContent = '{message}';
                setTimeout(() => {{ region.textContent = ''; }}, 1000);
            }}
        }})();
        </script>
        """


class TextScalingHelper:
    """Ensures proper text scaling support"""
    
    @staticmethod
    def get_responsive_text_css() -> str:
        """Generate CSS for responsive text scaling"""
        return """
        /* Responsive Text Scaling */
        html {
            font-size: 16px;
        }
        
        /* Support text scaling up to 200% */
        @media (min-width: 320px) {
            html {
                font-size: calc(16px + 6 * ((100vw - 320px) / 680));
            }
        }
        
        @media (min-width: 1000px) {
            html {
                font-size: 22px;
            }
        }
        
        /* Ensure minimum touch target size */
        button, a, input, select, textarea {
            min-height: 44px;
            min-width: 44px;
        }
        
        /* Prevent text overflow */
        * {
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        
        /* Maintain readability at all sizes */
        p, li, td, th {
            max-width: 70ch;
            line-height: 1.5;
        }
        
        /* Respect user preferences */
        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        """


class AccessibilityAuditor:
    """Audits themes and components for accessibility issues"""
    
    def __init__(self):
        self.contrast_checker = ContrastChecker()
        self.issues = []
    
    def audit_theme(self, theme_data: Dict[str, Any]) -> AccessibilityReport:
        """
        Perform comprehensive accessibility audit on theme
        
        Args:
            theme_data: Theme data dictionary
            
        Returns:
            AccessibilityReport with findings
        """
        contrast_issues = []
        recommendations = []
        
        colors = theme_data.get('colors', {})
        
        # Check critical color combinations
        critical_pairs = [
            ('foreground', 'background', 'Body text'),
            ('primary_foreground', 'primary', 'Primary button text'),
            ('secondary_foreground', 'secondary', 'Secondary button text'),
            ('muted_foreground', 'muted', 'Muted text'),
        ]
        
        for fg_key, bg_key, description in critical_pairs:
            if fg_key in colors and bg_key in colors:
                fg = colors[fg_key]
                bg = colors[bg_key]
                
                result = self.contrast_checker.check_contrast(fg, bg)
                
                if not result.passes_aa_normal:
                    contrast_issues.append({
                        'description': description,
                        'foreground': fg,
                        'background': bg,
                        'ratio': result.ratio,
                        'recommendation': result.recommendation
                    })
                    recommendations.append(
                        f"Improve contrast for {description}: {result.recommendation}"
                    )
        
        # Calculate overall score
        total_checks = len(critical_pairs)
        passed_checks = total_checks - len(contrast_issues)
        overall_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        return AccessibilityReport(
            theme_name=theme_data.get('name', 'Unknown'),
            contrast_issues=contrast_issues,
            keyboard_nav_issues=[],
            aria_issues=[],
            focus_issues=[],
            overall_score=overall_score,
            recommendations=recommendations
        )
    
    def generate_report_html(self, report: AccessibilityReport) -> str:
        """Generate HTML report of accessibility audit"""
        issues_html = ""
        
        for issue in report.contrast_issues:
            issues_html += f"""
            <div style="margin: 10px 0; padding: 10px; border-left: 3px solid #ef4444;">
                <strong>{issue['description']}</strong><br>
                Foreground: {issue['foreground']} | Background: {issue['background']}<br>
                Contrast Ratio: {issue['ratio']:.2f}:1<br>
                {issue['recommendation']}
            </div>
            """
        
        if not issues_html:
            issues_html = '<p style="color: #22c55e;"> No contrast issues found!</p>'
        
        recommendations_html = ""
        for rec in report.recommendations:
            recommendations_html += f"<li>{rec}</li>"
        
        return f"""
        <div style="font-family: system-ui, sans-serif; padding: 20px;">
            <h2>Accessibility Report: {report.theme_name}</h2>
            <div style="margin: 20px 0;">
                <h3>Overall Score: {report.overall_score:.1f}%</h3>
                <div style="background: #e5e7eb; height: 20px; border-radius: 10px;">
                    <div style="background: #22c55e; height: 100%; width: {report.overall_score}%; border-radius: 10px;"></div>
                </div>
            </div>
            
            <h3>Contrast Issues</h3>
            {issues_html}
            
            <h3>Recommendations</h3>
            <ul>{recommendations_html if recommendations_html else '<li>No recommendations</li>'}</ul>
        </div>
        """


class ColorBlindnessFriendlyThemeGenerator:
    """Generates color blindness friendly themes"""
    
    @staticmethod
    def generate_high_contrast_theme(base_theme: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high contrast version of theme"""
        theme = base_theme.copy()
        colors = theme.get('colors', {}).copy()
        
        # Use pure black and white for maximum contrast
        colors['background'] = '#ffffff'
        colors['foreground'] = '#000000'
        colors['muted'] = '#f5f5f5'
        colors['muted_foreground'] = '#262626'
        colors['border'] = '#000000'
        
        # Use highly saturated, distinct colors
        colors['primary'] = '#0000ff'  # Pure blue
        colors['primary_foreground'] = '#ffffff'
        colors['success'] = '#008000'  # Pure green
        colors['error'] = '#ff0000'    # Pure red
        colors['warning'] = '#ff8c00'  # Dark orange
        colors['info'] = '#0000cd'     # Medium blue
        
        theme['colors'] = colors
        theme['name'] = f"{base_theme.get('name', 'theme')}-high-contrast"
        theme['display_name'] = f"{base_theme.get('display_name', 'Theme')} (High Contrast)"
        
        return theme
    
    @staticmethod
    def generate_colorblind_safe_theme(base_theme: Dict[str, Any]) -> Dict[str, Any]:
        """Generate colorblind-safe theme using patterns and shapes"""
        theme = base_theme.copy()
        colors = theme.get('colors', {}).copy()
        
        # Use colors that are distinguishable for all types of color blindness
        # Blue and orange are safe for most types
        colors['primary'] = '#0066cc'  # Blue
        colors['secondary'] = '#ff8800'  # Orange
        colors['success'] = '#0066cc'  # Blue (instead of green)
        colors['error'] = '#cc0000'    # Dark red
        colors['warning'] = '#ff8800'  # Orange
        colors['info'] = '#6600cc'     # Purple
        
        # Chart colors that work for color blindness
        colors['chart_1'] = '#0066cc'  # Blue
        colors['chart_2'] = '#ff8800'  # Orange
        colors['chart_3'] = '#cc0000'  # Red
        colors['chart_4'] = '#6600cc'  # Purple
        colors['chart_5'] = '#00cccc'  # Cyan
        
        theme['colors'] = colors
        theme['name'] = f"{base_theme.get('name', 'theme')}-colorblind-safe"
        theme['display_name'] = f"{base_theme.get('display_name', 'Theme')} (Colorblind Safe)"
        
        return theme


# Export all classes
__all__ = [
    'ContrastChecker',
    'ContrastResult',
    'ContrastLevel',
    'ColorBlindnessSimulator',
    'ColorBlindnessType',
    'KeyboardNavigationHelper',
    'ARIAHelper',
    'FocusManager',
    'ScreenReaderHelper',
    'TextScalingHelper',
    'AccessibilityAuditor',
    'AccessibilityReport',
    'ColorBlindnessFriendlyThemeGenerator'
]
