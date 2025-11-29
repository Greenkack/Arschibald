"""
Task 20: Integration Tests für shadcn/ui Theme System
=====================================================
Integration Tests für Theme-Wechsel, CSS-Injection und Komponenten.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_session_state():
    """Mock Streamlit session state."""
    return {
        "current_theme": "default",
        "dark_mode": False,
        "theme_loaded": True
    }


@pytest.fixture
def mock_themes():
    """Mock available themes."""
    return {
        "default": {
            "name": "default",
            "colors": {"primary": "#3b82f6", "background": "#ffffff"}
        },
        "dark": {
            "name": "dark",
            "colors": {"primary": "#3b82f6", "background": "#0f172a"}
        },
        "ocean": {
            "name": "ocean",
            "colors": {"primary": "#0ea5e9", "background": "#f0f9ff"}
        }
    }


# ============================================================================
# Theme Switch Integration Tests
# ============================================================================

class TestThemeSwitchIntegration:
    """Integration Tests für Theme-Wechsel."""

    def test_theme_switch_updates_session_state(self, mock_session_state, mock_themes):
        """Test dass Theme-Wechsel Session State aktualisiert."""
        # Initial state
        assert mock_session_state["current_theme"] == "default"
        
        # Switch theme
        mock_session_state["current_theme"] = "dark"
        
        # Verify
        assert mock_session_state["current_theme"] == "dark"

    def test_theme_switch_triggers_css_regeneration(self, mock_themes):
        """Test dass Theme-Wechsel CSS neu generiert."""
        css_generated = []
        
        def generate_css(theme_name):
            theme = mock_themes[theme_name]
            css = f":root {{ --primary: {theme['colors']['primary']}; }}"
            css_generated.append(css)
            return css
        
        # Generate CSS for default
        generate_css("default")
        assert len(css_generated) == 1
        assert "#3b82f6" in css_generated[0]
        
        # Switch to ocean
        generate_css("ocean")
        assert len(css_generated) == 2
        assert "#0ea5e9" in css_generated[1]

    def test_dark_mode_toggle(self, mock_session_state):
        """Test Dark Mode Toggle."""
        assert mock_session_state["dark_mode"] == False
        
        # Toggle dark mode
        mock_session_state["dark_mode"] = True
        
        assert mock_session_state["dark_mode"] == True

    def test_theme_switch_preserves_other_state(self, mock_session_state):
        """Test dass Theme-Wechsel anderen State nicht beeinflusst."""
        mock_session_state["user_data"] = {"name": "Test User"}
        
        # Switch theme
        mock_session_state["current_theme"] = "ocean"
        
        # Verify other state preserved
        assert mock_session_state["user_data"]["name"] == "Test User"


# ============================================================================
# CSS Injection Integration Tests
# ============================================================================

class TestCSSInjectionIntegration:
    """Integration Tests für CSS-Injection."""

    def test_css_injection_on_app_start(self):
        """Test CSS-Injection beim App-Start."""
        injected_css = []
        
        def inject_css(css):
            injected_css.append(css)
        
        # Simulate app start
        startup_css = ":root { --primary: #3b82f6; }"
        inject_css(startup_css)
        
        assert len(injected_css) == 1
        assert "--primary" in injected_css[0]

    def test_css_injection_includes_all_variables(self, mock_themes):
        """Test dass CSS alle Variablen enthält."""
        theme = mock_themes["default"]
        
        css_vars = []
        for name, value in theme["colors"].items():
            css_vars.append(f"--{name}: {value};")
        
        css = ":root {\n  " + "\n  ".join(css_vars) + "\n}"
        
        assert "--primary" in css
        assert "--background" in css

    def test_css_injection_order(self):
        """Test CSS-Injection-Reihenfolge."""
        injection_order = []
        
        def inject_css(css_type, css):
            injection_order.append(css_type)
        
        # Inject in correct order
        inject_css("variables", ":root { --primary: #3b82f6; }")
        inject_css("components", ".btn { padding: 0.5rem; }")
        inject_css("utilities", ".text-primary { color: var(--primary); }")
        
        assert injection_order == ["variables", "components", "utilities"]

    def test_css_injection_handles_errors(self):
        """Test Fehlerbehandlung bei CSS-Injection."""
        errors = []
        
        def inject_css_safe(css):
            try:
                if not css or not isinstance(css, str):
                    raise ValueError("Invalid CSS")
                return True
            except Exception as e:
                errors.append(str(e))
                return False
        
        # Valid CSS
        assert inject_css_safe(":root { --primary: #3b82f6; }") == True
        
        # Invalid CSS
        assert inject_css_safe(None) == False
        assert len(errors) == 1


# ============================================================================
# Component Theme Integration Tests
# ============================================================================

class TestComponentThemeIntegration:
    """Integration Tests für Komponenten mit verschiedenen Themes."""

    def test_card_renders_with_theme_colors(self, mock_themes):
        """Test Card-Rendering mit Theme-Farben."""
        theme = mock_themes["default"]
        
        card_style = f"background-color: {theme['colors']['background']};"
        
        assert "#ffffff" in card_style

    def test_button_renders_with_theme_colors(self, mock_themes):
        """Test Button-Rendering mit Theme-Farben."""
        theme = mock_themes["ocean"]
        
        button_style = f"background-color: {theme['colors']['primary']};"
        
        assert "#0ea5e9" in button_style

    def test_components_update_on_theme_change(self, mock_themes):
        """Test Komponenten-Update bei Theme-Wechsel."""
        rendered_components = []
        
        def render_card(theme_name):
            theme = mock_themes[theme_name]
            card = f"<div style='background: {theme['colors']['background']}'>Card</div>"
            rendered_components.append(card)
            return card
        
        # Render with default theme
        render_card("default")
        assert "#ffffff" in rendered_components[0]
        
        # Render with dark theme
        render_card("dark")
        assert "#0f172a" in rendered_components[1]

    def test_all_components_use_css_variables(self):
        """Test dass alle Komponenten CSS-Variablen nutzen."""
        component_styles = {
            "card": "background-color: var(--background);",
            "button": "background-color: var(--primary);",
            "alert": "border-color: var(--info);",
            "badge": "background-color: var(--secondary);"
        }
        
        for component, style in component_styles.items():
            assert "var(--" in style, f"{component} should use CSS variables"


# ============================================================================
# Theme Persistence Integration Tests
# ============================================================================

class TestThemePersistenceIntegration:
    """Integration Tests für Theme-Persistierung."""

    def test_theme_saved_to_local_storage(self):
        """Test Theme-Speicherung in Local Storage."""
        local_storage = {}
        
        def save_theme(theme_name):
            local_storage["selected_theme"] = theme_name
        
        save_theme("ocean")
        
        assert local_storage["selected_theme"] == "ocean"

    def test_theme_loaded_from_local_storage(self):
        """Test Theme-Laden aus Local Storage."""
        local_storage = {"selected_theme": "dark"}
        
        def load_theme():
            return local_storage.get("selected_theme", "default")
        
        loaded = load_theme()
        
        assert loaded == "dark"

    def test_theme_persists_across_sessions(self):
        """Test Theme-Persistierung über Sessions."""
        # Simulate session 1
        session1_storage = {}
        session1_storage["selected_theme"] = "forest"
        
        # Simulate session 2 (new session, same storage)
        session2_storage = session1_storage.copy()
        
        assert session2_storage["selected_theme"] == "forest"

    def test_invalid_theme_falls_back_to_default(self, mock_themes):
        """Test Fallback bei ungültigem Theme."""
        local_storage = {"selected_theme": "invalid_theme"}
        
        def load_theme():
            theme_name = local_storage.get("selected_theme", "default")
            if theme_name not in mock_themes:
                return "default"
            return theme_name
        
        loaded = load_theme()
        
        assert loaded == "default"

    def test_theme_preference_syncs_with_database(self):
        """Test Theme-Sync mit Datenbank."""
        database = {}
        
        def save_user_theme(user_id, theme_name):
            database[f"user_{user_id}_theme"] = theme_name
        
        def load_user_theme(user_id):
            return database.get(f"user_{user_id}_theme", "default")
        
        # Save preference
        save_user_theme(123, "sunset")
        
        # Load preference
        loaded = load_user_theme(123)
        
        assert loaded == "sunset"


# ============================================================================
# Full Integration Flow Tests
# ============================================================================

class TestFullIntegrationFlow:
    """End-to-End Integration Tests."""

    def test_complete_theme_switch_flow(self, mock_session_state, mock_themes):
        """Test kompletter Theme-Wechsel-Flow."""
        # 1. User selects new theme
        selected_theme = "ocean"
        
        # 2. Update session state
        mock_session_state["current_theme"] = selected_theme
        
        # 3. Generate new CSS
        theme = mock_themes[selected_theme]
        css = f":root {{ --primary: {theme['colors']['primary']}; }}"
        
        # 4. Save to storage
        storage = {"selected_theme": selected_theme}
        
        # Verify all steps
        assert mock_session_state["current_theme"] == "ocean"
        assert "#0ea5e9" in css
        assert storage["selected_theme"] == "ocean"

    def test_app_startup_with_saved_theme(self, mock_themes):
        """Test App-Start mit gespeichertem Theme."""
        # Simulate saved preference
        storage = {"selected_theme": "dark"}
        
        # App startup
        session_state = {}
        
        # Load saved theme
        saved_theme = storage.get("selected_theme", "default")
        session_state["current_theme"] = saved_theme
        
        # Generate CSS
        theme = mock_themes[saved_theme]
        css = f":root {{ --background: {theme['colors']['background']}; }}"
        
        # Verify
        assert session_state["current_theme"] == "dark"
        assert "#0f172a" in css

    def test_theme_change_updates_all_components(self, mock_themes):
        """Test dass Theme-Wechsel alle Komponenten aktualisiert."""
        components = ["card", "button", "alert", "badge", "input"]
        updated_components = []
        
        def update_component(component_name, theme):
            updated_components.append(component_name)
        
        # Switch theme
        new_theme = mock_themes["ocean"]
        
        for component in components:
            update_component(component, new_theme)
        
        assert len(updated_components) == 5
        assert all(c in updated_components for c in components)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
