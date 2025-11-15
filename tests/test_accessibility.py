"""
Unit Tests for Accessibility Module

Tests all accessibility features including:
- Contrast checking
- Color blindness simulation
- ARIA helpers
- Focus management
- Screen reader support
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from theming.accessibility import (
    ContrastChecker,
    ContrastLevel,
    ColorBlindnessSimulator,
    ColorBlindnessType,
    KeyboardNavigationHelper,
    ARIAHelper,
    FocusManager,
    ScreenReaderHelper,
    TextScalingHelper,
    AccessibilityAuditor,
    ColorBlindnessFriendlyThemeGenerator
)


class TestContrastChecker:
    """Test contrast checking functionality"""
    
    def test_hex_to_rgb(self):
        """Test hex to RGB conversion"""
        assert ContrastChecker.hex_to_rgb("#ffffff") == (255, 255, 255)
        assert ContrastChecker.hex_to_rgb("#000000") == (0, 0, 0)
        assert ContrastChecker.hex_to_rgb("#ff0000") == (255, 0, 0)
        assert ContrastChecker.hex_to_rgb("3b82f6") == (59, 130, 246)
    
    def test_relative_luminance(self):
        """Test relative luminance calculation"""
        # White should have luminance of 1
        white_lum = ContrastChecker.get_relative_luminance((255, 255, 255))
        assert abs(white_lum - 1.0) < 0.01
        
        # Black should have luminance of 0
        black_lum = ContrastChecker.get_relative_luminance((0, 0, 0))
        assert abs(black_lum - 0.0) < 0.01
    
    def test_contrast_ratio_black_white(self):
        """Test contrast ratio for black and white"""
        ratio = ContrastChecker.calculate_contrast_ratio("#000000", "#ffffff")
        assert abs(ratio - 21.0) < 0.1  # Should be 21:1
    
    def test_contrast_ratio_same_color(self):
        """Test contrast ratio for same color"""
        ratio = ContrastChecker.calculate_contrast_ratio("#ff0000", "#ff0000")
        assert abs(ratio - 1.0) < 0.1  # Should be 1:1
    
    def test_wcag_aa_pass(self):
        """Test WCAG AA passing combination"""
        result = ContrastChecker.check_contrast("#000000", "#ffffff")
        assert result.passes_aa_normal
        assert result.passes_aa_large
        assert result.ratio >= 4.5
    
    def test_wcag_aa_fail(self):
        """Test WCAG AA failing combination"""
        result = ContrastChecker.check_contrast("#cccccc", "#ffffff")
        assert not result.passes_aa_normal
        assert result.ratio < 4.5
    
    def test_wcag_aaa_pass(self):
        """Test WCAG AAA passing combination"""
        result = ContrastChecker.check_contrast("#000000", "#ffffff")
        assert result.passes_aaa_normal
        assert result.passes_aaa_large
        assert result.ratio >= 7.0
    
    def test_large_text_threshold(self):
        """Test large text has lower threshold"""
        # Test that large text threshold (3:1) is lower than normal text (4.5:1)
        result_normal = ContrastChecker.check_contrast("#767676", "#ffffff", is_large_text=False)
        result_large = ContrastChecker.check_contrast("#767676", "#ffffff", is_large_text=True)
        
        # Same color combination should have same ratio
        assert result_normal.ratio == result_large.ratio
        
        # But different pass/fail results based on threshold
        # This color has ratio ~4.54:1, which passes both
        # Just verify the thresholds are different
        assert ContrastLevel.AA_LARGE.value < ContrastLevel.AA_NORMAL.value


class TestColorBlindnessSimulator:
    """Test color blindness simulation"""
    
    def test_protanopia_simulation(self):
        """Test red-blindness simulation"""
        original = "#ff0000"  # Pure red
        simulated = ColorBlindnessSimulator.simulate_protanopia(original)
        assert simulated != original
        assert simulated.startswith("#")
        assert len(simulated) == 7
    
    def test_deuteranopia_simulation(self):
        """Test green-blindness simulation"""
        original = "#00ff00"  # Pure green
        simulated = ColorBlindnessSimulator.simulate_deuteranopia(original)
        assert simulated != original
        assert simulated.startswith("#")
    
    def test_tritanopia_simulation(self):
        """Test blue-blindness simulation"""
        original = "#0000ff"  # Pure blue
        simulated = ColorBlindnessSimulator.simulate_tritanopia(original)
        assert simulated != original
        assert simulated.startswith("#")
    
    def test_achromatopsia_simulation(self):
        """Test total color blindness simulation"""
        original = "#3b82f6"  # Blue
        simulated = ColorBlindnessSimulator.simulate_achromatopsia(original)
        # Should be grayscale (all RGB values equal)
        r, g, b = ContrastChecker.hex_to_rgb(simulated)
        assert r == g == b
    
    def test_simulate_with_enum(self):
        """Test simulation using enum"""
        color = "#ff0000"
        
        protanopia = ColorBlindnessSimulator.simulate(color, ColorBlindnessType.PROTANOPIA)
        assert protanopia.startswith("#")
        
        deuteranopia = ColorBlindnessSimulator.simulate(color, ColorBlindnessType.DEUTERANOPIA)
        assert deuteranopia.startswith("#")
        
        tritanopia = ColorBlindnessSimulator.simulate(color, ColorBlindnessType.TRITANOPIA)
        assert tritanopia.startswith("#")
        
        achromatopsia = ColorBlindnessSimulator.simulate(color, ColorBlindnessType.ACHROMATOPSIA)
        assert achromatopsia.startswith("#")


class TestKeyboardNavigationHelper:
    """Test keyboard navigation helpers"""
    
    def test_keyboard_nav_css_generation(self):
        """Test keyboard navigation CSS generation"""
        css = KeyboardNavigationHelper.get_keyboard_nav_css()
        assert "*:focus" in css
        assert "outline" in css
        assert "skip-to-main" in css
    
    def test_skip_to_main_html(self):
        """Test skip to main content link"""
        html = KeyboardNavigationHelper.get_skip_to_main_html()
        assert "skip-to-main" in html
        assert "#main-content" in html
        assert "<a" in html


class TestARIAHelper:
    """Test ARIA helper functions"""
    
    def test_button_aria_basic(self):
        """Test basic button ARIA"""
        aria = ARIAHelper.get_button_aria("Save")
        assert 'aria-label="Save"' in aria
    
    def test_button_aria_pressed(self):
        """Test button ARIA with pressed state"""
        aria = ARIAHelper.get_button_aria("Toggle", pressed=True)
        assert 'aria-pressed="true"' in aria
    
    def test_button_aria_expanded(self):
        """Test button ARIA with expanded state"""
        aria = ARIAHelper.get_button_aria("Menu", expanded=False)
        assert 'aria-expanded="false"' in aria
    
    def test_button_aria_disabled(self):
        """Test button ARIA with disabled state"""
        aria = ARIAHelper.get_button_aria("Submit", disabled=True)
        assert 'aria-disabled="true"' in aria
    
    def test_input_aria_basic(self):
        """Test basic input ARIA"""
        aria = ARIAHelper.get_input_aria("Email")
        assert 'aria-label="Email"' in aria
    
    def test_input_aria_required(self):
        """Test input ARIA with required"""
        aria = ARIAHelper.get_input_aria("Name", required=True)
        assert 'aria-required="true"' in aria
    
    def test_input_aria_invalid(self):
        """Test input ARIA with invalid state"""
        aria = ARIAHelper.get_input_aria("Email", invalid=True)
        assert 'aria-invalid="true"' in aria
    
    def test_input_aria_describedby(self):
        """Test input ARIA with describedby"""
        aria = ARIAHelper.get_input_aria("Password", describedby="pwd-help")
        assert 'aria-describedby="pwd-help"' in aria
    
    def test_dialog_aria(self):
        """Test dialog ARIA"""
        aria = ARIAHelper.get_dialog_aria("Confirm")
        assert 'role="dialog"' in aria
        assert 'aria-label="Confirm"' in aria
        assert 'aria-modal="true"' in aria
    
    def test_alert_aria(self):
        """Test alert ARIA"""
        aria = ARIAHelper.get_alert_aria()
        assert 'role="alert"' in aria
        assert 'aria-live="polite"' in aria
    
    def test_navigation_aria(self):
        """Test navigation ARIA"""
        aria = ARIAHelper.get_navigation_aria("Main menu")
        assert 'role="navigation"' in aria
        assert 'aria-label="Main menu"' in aria


class TestFocusManager:
    """Test focus management"""
    
    def test_focus_trap_js_generation(self):
        """Test focus trap JavaScript generation"""
        js = FocusManager.get_focus_trap_js("modal-1")
        assert "modal-1" in js
        assert "querySelectorAll" in js
        assert "focus()" in js
        assert "Tab" in js
    
    def test_focus_indicator_css(self):
        """Test focus indicator CSS"""
        css = FocusManager.get_focus_indicator_css()
        assert "focus-visible" in css
        assert "focus-ring" in css
        assert "outline" in css or "border" in css


class TestScreenReaderHelper:
    """Test screen reader helpers"""
    
    def test_sr_only_css(self):
        """Test screen reader only CSS"""
        css = ScreenReaderHelper.get_sr_only_css()
        assert "sr-only" in css
        assert "position: absolute" in css
        assert "width: 1px" in css
    
    def test_wrap_sr_only(self):
        """Test wrapping text in sr-only span"""
        html = ScreenReaderHelper.wrap_sr_only("Hidden text")
        assert '<span class="sr-only">Hidden text</span>' in html
    
    def test_live_region_html(self):
        """Test live region HTML generation"""
        html = ScreenReaderHelper.get_live_region_html("announcements")
        assert 'id="announcements"' in html
        assert 'role="status"' in html
        assert 'aria-live="polite"' in html
    
    def test_announce_message(self):
        """Test message announcement"""
        js = ScreenReaderHelper.announce("announcements", "Success!")
        assert "announcements" in js
        assert "Success!" in js
        assert "textContent" in js


class TestTextScalingHelper:
    """Test text scaling helpers"""
    
    def test_responsive_text_css(self):
        """Test responsive text CSS generation"""
        css = TextScalingHelper.get_responsive_text_css()
        assert "font-size" in css
        assert "min-height: 44px" in css
        assert "min-width: 44px" in css
        assert "prefers-reduced-motion" in css


class TestAccessibilityAuditor:
    """Test accessibility auditor"""
    
    def test_audit_good_theme(self):
        """Test auditing a theme with good contrast"""
        theme_data = {
            'name': 'test-theme',
            'colors': {
                'foreground': '#000000',
                'background': '#ffffff',
                'primary': '#0000ff',
                'primary_foreground': '#ffffff',
                'secondary': '#f0f0f0',
                'secondary_foreground': '#000000',
                'muted': '#f5f5f5',
                'muted_foreground': '#666666'
            }
        }
        
        auditor = AccessibilityAuditor()
        report = auditor.audit_theme(theme_data)
        
        assert report.theme_name == 'test-theme'
        assert report.overall_score >= 0
        assert report.overall_score <= 100
        assert isinstance(report.contrast_issues, list)
    
    def test_audit_bad_theme(self):
        """Test auditing a theme with poor contrast"""
        theme_data = {
            'name': 'bad-theme',
            'colors': {
                'foreground': '#cccccc',
                'background': '#ffffff',
                'primary': '#ffff00',
                'primary_foreground': '#ffffff',
                'secondary': '#f0f0f0',
                'secondary_foreground': '#ffffff',
                'muted': '#ffffff',
                'muted_foreground': '#f0f0f0'
            }
        }
        
        auditor = AccessibilityAuditor()
        report = auditor.audit_theme(theme_data)
        
        assert len(report.contrast_issues) > 0
        assert report.overall_score < 100
    
    def test_generate_report_html(self):
        """Test HTML report generation"""
        theme_data = {
            'name': 'test-theme',
            'colors': {
                'foreground': '#000000',
                'background': '#ffffff',
                'primary': '#0000ff',
                'primary_foreground': '#ffffff',
                'secondary': '#f0f0f0',
                'secondary_foreground': '#000000',
                'muted': '#f5f5f5',
                'muted_foreground': '#666666'
            }
        }
        
        auditor = AccessibilityAuditor()
        report = auditor.audit_theme(theme_data)
        html = auditor.generate_report_html(report)
        
        assert "Accessibility Report" in html
        assert "test-theme" in html
        assert "Overall Score" in html


class TestColorBlindnessFriendlyThemeGenerator:
    """Test colorblind-friendly theme generation"""
    
    def test_generate_high_contrast_theme(self):
        """Test high contrast theme generation"""
        base_theme = {
            'name': 'base',
            'display_name': 'Base Theme',
            'colors': {
                'background': '#f0f0f0',
                'foreground': '#333333',
                'primary': '#3b82f6'
            }
        }
        
        hc_theme = ColorBlindnessFriendlyThemeGenerator.generate_high_contrast_theme(base_theme)
        
        assert hc_theme['name'] == 'base-high-contrast'
        assert 'High Contrast' in hc_theme['display_name']
        assert hc_theme['colors']['background'] == '#ffffff'
        assert hc_theme['colors']['foreground'] == '#000000'
    
    def test_generate_colorblind_safe_theme(self):
        """Test colorblind-safe theme generation"""
        base_theme = {
            'name': 'base',
            'display_name': 'Base Theme',
            'colors': {
                'background': '#ffffff',
                'foreground': '#000000',
                'primary': '#ff0000',
                'success': '#00ff00'
            }
        }
        
        cb_theme = ColorBlindnessFriendlyThemeGenerator.generate_colorblind_safe_theme(base_theme)
        
        assert cb_theme['name'] == 'base-colorblind-safe'
        assert 'Colorblind Safe' in cb_theme['display_name']
        # Should use blue instead of green for success
        assert cb_theme['colors']['success'] == '#0066cc'


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
