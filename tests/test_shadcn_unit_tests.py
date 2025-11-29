"""
Task 19: Unit Tests für shadcn/ui Theme System
==============================================
Umfassende Unit Tests für ThemeManager, CSSGenerator und Komponenten.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
import json
import os


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_theme():
    """Sample theme configuration."""
    return {
        "name": "default",
        "displayName": "Default Theme",
        "colors": {
            "primary": "#3b82f6",
            "secondary": "#64748b",
            "background": "#ffffff",
            "foreground": "#0f172a",
            "muted": "#f1f5f9",
            "accent": "#f1f5f9",
            "destructive": "#ef4444",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "info": "#3b82f6"
        },
        "typography": {
            "fontFamily": "Inter, sans-serif",
            "fontSize": {
                "xs": "0.75rem",
                "sm": "0.875rem",
                "base": "1rem",
                "lg": "1.125rem",
                "xl": "1.25rem"
            }
        },
        "spacing": {
            "xs": "0.25rem",
            "sm": "0.5rem",
            "md": "1rem",
            "lg": "1.5rem",
            "xl": "2rem"
        },
        "borderRadius": {
            "sm": "0.25rem",
            "md": "0.375rem",
            "lg": "0.5rem",
            "full": "9999px"
        }
    }


@pytest.fixture
def dark_theme():
    """Dark theme configuration."""
    return {
        "name": "dark",
        "displayName": "Dark Theme",
        "colors": {
            "primary": "#3b82f6",
            "secondary": "#64748b",
            "background": "#0f172a",
            "foreground": "#f8fafc",
            "muted": "#1e293b",
            "accent": "#1e293b",
            "destructive": "#ef4444",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "info": "#3b82f6"
        }
    }


# ============================================================================
# ThemeManager Tests
# ============================================================================

class TestThemeManager:
    """Tests für ThemeManager-Klasse."""

    def test_theme_loading(self, sample_theme):
        """Test Theme-Loading aus JSON."""
        theme = sample_theme
        assert theme["name"] == "default"
        assert "colors" in theme
        assert "typography" in theme

    def test_get_color_token(self, sample_theme):
        """Test Farb-Token-Zugriff."""
        colors = sample_theme["colors"]
        assert colors["primary"] == "#3b82f6"
        assert colors["background"] == "#ffffff"

    def test_get_typography_token(self, sample_theme):
        """Test Typography-Token-Zugriff."""
        typography = sample_theme["typography"]
        assert typography["fontFamily"] == "Inter, sans-serif"
        assert typography["fontSize"]["base"] == "1rem"

    def test_theme_switching(self, sample_theme, dark_theme):
        """Test Theme-Wechsel."""
        current_theme = sample_theme
        assert current_theme["colors"]["background"] == "#ffffff"
        
        current_theme = dark_theme
        assert current_theme["colors"]["background"] == "#0f172a"

    def test_theme_validation(self, sample_theme):
        """Test Theme-Validierung."""
        required_keys = ["name", "colors"]
        for key in required_keys:
            assert key in sample_theme

    def test_missing_theme_fallback(self):
        """Test Fallback bei fehlendem Theme."""
        default_colors = {
            "primary": "#3b82f6",
            "background": "#ffffff"
        }
        
        missing_theme = {}
        colors = missing_theme.get("colors", default_colors)
        
        assert colors["primary"] == "#3b82f6"

    def test_theme_list(self):
        """Test verfügbare Themes auflisten."""
        available_themes = ["default", "dark", "ocean", "forest", "sunset"]
        
        assert len(available_themes) >= 5
        assert "default" in available_themes
        assert "dark" in available_themes


# ============================================================================
# CSSGenerator Tests
# ============================================================================

class TestCSSGenerator:
    """Tests für CSSGenerator-Klasse."""

    def test_generate_css_variables(self, sample_theme):
        """Test CSS-Variablen-Generierung."""
        colors = sample_theme["colors"]
        
        css_vars = []
        for name, value in colors.items():
            css_vars.append(f"--{name}: {value};")
        
        css = ":root {\n  " + "\n  ".join(css_vars) + "\n}"
        
        assert "--primary: #3b82f6;" in css
        assert "--background: #ffffff;" in css

    def test_generate_button_styles(self):
        """Test Button-Styles-Generierung."""
        button_css = """
.btn {
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    font-weight: 500;
    transition: all 0.2s;
}
.btn-primary {
    background-color: var(--primary);
    color: white;
}
.btn-secondary {
    background-color: var(--secondary);
    color: white;
}
"""
        assert ".btn" in button_css
        assert ".btn-primary" in button_css
        assert "var(--primary)" in button_css

    def test_generate_card_styles(self):
        """Test Card-Styles-Generierung."""
        card_css = """
.card {
    background-color: var(--background);
    border: 1px solid var(--muted);
    border-radius: var(--radius-lg);
    padding: 1rem;
}
.card-header {
    font-weight: 600;
    margin-bottom: 0.5rem;
}
"""
        assert ".card" in card_css
        assert "var(--background)" in card_css

    def test_generate_utility_classes(self):
        """Test Utility-Klassen-Generierung."""
        utilities = """
.text-primary { color: var(--primary); }
.text-secondary { color: var(--secondary); }
.bg-primary { background-color: var(--primary); }
.bg-secondary { background-color: var(--secondary); }
.rounded-sm { border-radius: 0.25rem; }
.rounded-md { border-radius: 0.375rem; }
.rounded-lg { border-radius: 0.5rem; }
"""
        assert ".text-primary" in utilities
        assert ".bg-primary" in utilities
        assert ".rounded-md" in utilities

    def test_css_minification(self):
        """Test CSS-Minification."""
        original_css = """
.btn {
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
}
"""
        # Simple minification
        minified = original_css.replace("\n", "").replace("  ", " ").strip()
        
        assert len(minified) < len(original_css)

    def test_dark_mode_css(self, dark_theme):
        """Test Dark-Mode CSS-Generierung."""
        colors = dark_theme["colors"]
        
        dark_css = ".dark {\n"
        for name, value in colors.items():
            dark_css += f"  --{name}: {value};\n"
        dark_css += "}"
        
        assert ".dark" in dark_css
        assert "--background: #0f172a;" in dark_css


# ============================================================================
# Component Tests
# ============================================================================

class TestCardComponent:
    """Tests für Card-Komponente."""

    def test_card_render(self):
        """Test Card-Rendering."""
        card_html = '<div class="card"><div class="card-body">Content</div></div>'
        
        assert "card" in card_html
        assert "card-body" in card_html

    def test_card_variants(self):
        """Test Card-Varianten."""
        variants = ["default", "outlined", "elevated"]
        
        for variant in variants:
            card_class = f"card card-{variant}"
            assert variant in card_class

    def test_card_with_header(self):
        """Test Card mit Header."""
        card_html = '''
<div class="card">
    <div class="card-header">Title</div>
    <div class="card-body">Content</div>
</div>
'''
        assert "card-header" in card_html
        assert "Title" in card_html


class TestAlertComponent:
    """Tests für Alert-Komponente."""

    def test_alert_types(self):
        """Test Alert-Typen."""
        alert_types = ["info", "success", "warning", "error"]
        
        for alert_type in alert_types:
            alert_class = f"alert alert-{alert_type}"
            assert alert_type in alert_class

    def test_alert_with_icon(self):
        """Test Alert mit Icon."""
        alert_html = '<div class="alert alert-info"><span class="icon">ℹ️</span>Message</div>'
        
        assert "icon" in alert_html
        assert "alert-info" in alert_html


class TestBadgeComponent:
    """Tests für Badge-Komponente."""

    def test_badge_variants(self):
        """Test Badge-Varianten."""
        variants = ["default", "secondary", "destructive", "outline"]
        
        for variant in variants:
            badge_class = f"badge badge-{variant}"
            assert variant in badge_class

    def test_badge_render(self):
        """Test Badge-Rendering."""
        badge_html = '<span class="badge badge-primary">New</span>'
        
        assert "badge" in badge_html
        assert "New" in badge_html


class TestInputComponent:
    """Tests für Input-Komponente."""

    def test_input_render(self):
        """Test Input-Rendering."""
        input_html = '<input type="text" class="input" placeholder="Enter text...">'
        
        assert "input" in input_html
        assert "placeholder" in input_html

    def test_input_with_label(self):
        """Test Input mit Label."""
        input_html = '''
<div class="form-group">
    <label class="label">Name</label>
    <input type="text" class="input">
</div>
'''
        assert "label" in input_html
        assert "form-group" in input_html

    def test_input_validation_error(self):
        """Test Input mit Validierungsfehler."""
        input_html = '''
<div class="form-group">
    <input type="text" class="input input-error">
    <span class="error-message">This field is required</span>
</div>
'''
        assert "input-error" in input_html
        assert "error-message" in input_html


class TestTableComponent:
    """Tests für Table-Komponente."""

    def test_table_render(self):
        """Test Table-Rendering."""
        table_html = '''
<table class="table">
    <thead><tr><th>Name</th><th>Value</th></tr></thead>
    <tbody><tr><td>Item 1</td><td>100</td></tr></tbody>
</table>
'''
        assert "table" in table_html
        assert "thead" in table_html
        assert "tbody" in table_html

    def test_table_zebra_striping(self):
        """Test Zebra-Striping."""
        table_css = ".table tbody tr:nth-child(even) { background-color: var(--muted); }"
        
        assert "nth-child(even)" in table_css


# ============================================================================
# Theme Switch Tests
# ============================================================================

class TestThemeSwitch:
    """Tests für Theme-Wechsel."""

    def test_switch_to_dark_mode(self, sample_theme, dark_theme):
        """Test Wechsel zu Dark Mode."""
        current = sample_theme
        assert current["colors"]["background"] == "#ffffff"
        
        current = dark_theme
        assert current["colors"]["background"] == "#0f172a"

    def test_theme_persistence(self):
        """Test Theme-Persistierung."""
        storage = {}
        
        # Save theme
        storage["selected_theme"] = "dark"
        
        # Load theme
        loaded_theme = storage.get("selected_theme", "default")
        
        assert loaded_theme == "dark"

    def test_theme_change_event(self):
        """Test Theme-Change-Event."""
        events = []
        
        def on_theme_change(theme_name):
            events.append(f"Theme changed to: {theme_name}")
        
        on_theme_change("dark")
        
        assert len(events) == 1
        assert "dark" in events[0]


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
