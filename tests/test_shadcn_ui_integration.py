"""
Unit tests for streamlit-shadcn-ui integration module

Tests all wrapper functions and fallback behavior.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components import shadcn_ui_integration as sui


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_is_available(self):
        """Test library availability check"""
        result = sui.is_available()
        assert isinstance(result, bool)
    
    def test_get_version(self):
        """Test version retrieval"""
        version = sui.get_version()
        if sui.is_available():
            assert version is not None
            assert isinstance(version, str)
        else:
            assert version is None
    
    def test_get_available_components(self):
        """Test component list retrieval"""
        components = sui.get_available_components()
        assert isinstance(components, list)
        assert len(components) > 0
        
        # Check expected components
        expected = [
            "button", "badge", "card", "alert", "tabs",
            "switch", "slider", "input", "textarea", "select",
            "checkbox", "radio_group", "date_picker", "link",
            "metric", "table", "element"
        ]
        
        for component in expected:
            assert component in components
    
    def test_get_component(self):
        """Test component retrieval by name"""
        # Valid component
        button_func = sui.get_component("button")
        assert button_func is not None
        assert callable(button_func)
        
        # Invalid component
        invalid = sui.get_component("nonexistent")
        assert invalid is None


class TestComponentRegistry:
    """Test component registry"""
    
    def test_registry_exists(self):
        """Test that component registry exists"""
        assert hasattr(sui, 'COMPONENT_REGISTRY')
        assert isinstance(sui.COMPONENT_REGISTRY, dict)
    
    def test_all_components_registered(self):
        """Test that all components are in registry"""
        components = sui.get_available_components()
        
        for component_name in components:
            assert component_name in sui.COMPONENT_REGISTRY
            assert callable(sui.COMPONENT_REGISTRY[component_name])


class TestComponentSignatures:
    """Test that component functions have correct signatures"""
    
    def test_button_signature(self):
        """Test button function signature"""
        import inspect
        sig = inspect.signature(sui.button)
        params = sig.parameters
        
        assert 'text' in params
        assert 'key' in params
        assert 'variant' in params
        assert 'size' in params
        assert 'disabled' in params
    
    def test_input_signature(self):
        """Test input function signature"""
        import inspect
        sig = inspect.signature(sui.input)
        params = sig.parameters
        
        assert 'label' in params
        assert 'default_value' in params
        assert 'placeholder' in params
        assert 'type' in params
        assert 'key' in params
        assert 'disabled' in params
    
    def test_card_signature(self):
        """Test card function signature"""
        import inspect
        sig = inspect.signature(sui.card)
        params = sig.parameters
        
        assert 'title' in params
        assert 'description' in params
        assert 'content' in params
        assert 'key' in params


class TestFallbackBehavior:
    """Test fallback behavior when library is not available"""
    
    def test_fallback_imports(self):
        """Test that fallback imports work"""
        # The module should import successfully regardless of library availability
        assert sui is not None
        assert hasattr(sui, 'button')
        assert hasattr(sui, 'badge')
        assert hasattr(sui, 'card')
    
    def test_shadcn_ui_available_flag(self):
        """Test SHADCN_UI_AVAILABLE flag"""
        assert hasattr(sui, 'SHADCN_UI_AVAILABLE')
        assert isinstance(sui.SHADCN_UI_AVAILABLE, bool)


class TestComponentDefaults:
    """Test component default values"""
    
    def test_button_defaults(self):
        """Test button default parameters"""
        import inspect
        sig = inspect.signature(sui.button)
        
        assert sig.parameters['variant'].default == "default"
        assert sig.parameters['size'].default == "default"
        assert sig.parameters['disabled'].default == False
    
    def test_badge_defaults(self):
        """Test badge default parameters"""
        import inspect
        sig = inspect.signature(sui.badge)
        
        assert sig.parameters['variant'].default == "default"
    
    def test_alert_defaults(self):
        """Test alert default parameters"""
        import inspect
        sig = inspect.signature(sui.alert)
        
        assert sig.parameters['variant'].default == "default"
    
    def test_switch_defaults(self):
        """Test switch default parameters"""
        import inspect
        sig = inspect.signature(sui.switch)
        
        assert sig.parameters['default'].default == False
        assert sig.parameters['disabled'].default == False


class TestTypeHints:
    """Test that functions have proper type hints"""
    
    def test_button_return_type(self):
        """Test button return type hint"""
        import inspect
        sig = inspect.signature(sui.button)
        assert sig.return_annotation == bool
    
    def test_input_return_type(self):
        """Test input return type hint"""
        import inspect
        sig = inspect.signature(sui.input)
        assert sig.return_annotation == str
    
    def test_checkbox_return_type(self):
        """Test checkbox return type hint"""
        import inspect
        sig = inspect.signature(sui.checkbox)
        assert sig.return_annotation == bool


class TestDocstrings:
    """Test that all components have docstrings"""
    
    def test_all_components_have_docstrings(self):
        """Test that all components have docstrings"""
        components = sui.get_available_components()
        
        for component_name in components:
            func = sui.get_component(component_name)
            assert func.__doc__ is not None
            assert len(func.__doc__.strip()) > 0
    
    def test_utility_functions_have_docstrings(self):
        """Test that utility functions have docstrings"""
        assert sui.is_available.__doc__ is not None
        assert sui.get_version.__doc__ is not None
        assert sui.get_available_components.__doc__ is not None
        assert sui.get_component.__doc__ is not None


class TestModuleStructure:
    """Test module structure and organization"""
    
    def test_module_has_logger(self):
        """Test that module has logger"""
        assert hasattr(sui, 'logger')
    
    def test_module_has_constants(self):
        """Test that module has required constants"""
        assert hasattr(sui, 'SHADCN_UI_AVAILABLE')
        assert hasattr(sui, 'COMPONENT_REGISTRY')
    
    def test_module_docstring(self):
        """Test that module has docstring"""
        assert sui.__doc__ is not None
        assert len(sui.__doc__.strip()) > 0


class TestErrorHandling:
    """Test error handling in components"""
    
    def test_components_handle_missing_library(self):
        """Test that components handle missing library gracefully"""
        # All components should work even if library is not available
        # They should fall back to native Streamlit components
        
        # This test verifies that the module loads without errors
        # regardless of library availability
        assert sui is not None
        
        # Verify all components are callable
        for component_name in sui.get_available_components():
            func = sui.get_component(component_name)
            assert callable(func)


class TestComponentCategories:
    """Test component categorization"""
    
    def test_button_components(self):
        """Test button-related components"""
        assert 'button' in sui.get_available_components()
    
    def test_form_components(self):
        """Test form-related components"""
        form_components = ['input', 'textarea', 'select', 'checkbox', 'radio_group', 'switch', 'slider']
        available = sui.get_available_components()
        
        for component in form_components:
            assert component in available
    
    def test_display_components(self):
        """Test display-related components"""
        display_components = ['card', 'alert', 'badge', 'metric', 'table']
        available = sui.get_available_components()
        
        for component in display_components:
            assert component in available
    
    def test_navigation_components(self):
        """Test navigation-related components"""
        nav_components = ['tabs', 'link']
        available = sui.get_available_components()
        
        for component in nav_components:
            assert component in available


class TestComponentCount:
    """Test component count"""
    
    def test_minimum_component_count(self):
        """Test that we have minimum expected components"""
        components = sui.get_available_components()
        # We should have at least 15 components
        assert len(components) >= 15
    
    def test_component_registry_matches_list(self):
        """Test that registry matches component list"""
        components = sui.get_available_components()
        registry_keys = list(sui.COMPONENT_REGISTRY.keys())
        
        assert len(components) == len(registry_keys)
        assert set(components) == set(registry_keys)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
