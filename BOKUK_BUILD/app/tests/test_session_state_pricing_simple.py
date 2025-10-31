"""Simple tests for enhanced pricing system session state integration"""

from unittest.mock import Mock, patch

import pytest


def test_enhanced_pricing_session_manager_basic():
    """Test basic functionality of EnhancedPricingSessionManager"""
    # Import after mocking streamlit
    with patch.dict('sys.modules', {'streamlit': Mock()}):
        from calculations import EnhancedPricingSessionManager

        manager = EnhancedPricingSessionManager()

        # Test initialization
        assert manager.cache_timeout_seconds == 30
        assert manager._pricing_engines == {}

        # Test cache key generation
        calculation_data = {
            'components': [{'product_id': 1, 'quantity': 2}],
            'modifications': {'discount_percent': 5.0},
            'vat_rate': 19.0
        }

        cache_key = manager._generate_cache_key(calculation_data)
        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5 hash length

        # Same data should produce same key
        cache_key2 = manager._generate_cache_key(calculation_data)
        assert cache_key == cache_key2


def test_pricing_modifications_collection():
    """Test collection of pricing modifications from session state"""
    mock_st = Mock()
    mock_st.session_state = {
        'pricing_modifications': {
            'discount_percent': 5.0,
            'surcharge_percent': 2.0,
            'special_discount': 100.0,
            'additional_costs': 50.0
        },
        'pricing_modifications_discount_slider': 10.0,
        'pricing_modifications_rebates_slider': 200.0,
        'pricing_modifications_surcharge_slider': 3.0,
        'pricing_modifications_special_costs_slider': 25.0,
        'pricing_modifications_miscellaneous_slider': 15.0
    }

    with patch.dict('sys.modules', {'streamlit': mock_st}):
        from calculations import _collect_pricing_modifications_from_session

        modifications = _collect_pricing_modifications_from_session()

        # Should use higher slider values where applicable
        assert modifications['discount_percent'] == 10.0  # max(5.0, 10.0)
        assert modifications['surcharge_percent'] == 3.0   # max(2.0, 3.0)
        assert modifications['special_discount'] == 200.0  # max(100.0, 200.0)
        # max(50.0, 25.0 + 15.0) = max(50.0, 40.0) = 50.0
        assert modifications['additional_costs'] == 50.0


def test_enhanced_pricing_session_manager_modifications():
    """Test getting pricing modifications in enhanced format"""
    mock_st = Mock()
    mock_st.session_state = {
        'pricing_modifications_discount_slider': 5.0,
        'pricing_modifications_rebates_slider': 100.0,
        'pricing_modifications_surcharge_slider': 2.0,
        'pricing_modifications_special_costs_slider': 50.0
    }

    with patch.dict('sys.modules', {'streamlit': mock_st}):
        from calculations import EnhancedPricingSessionManager

        manager = EnhancedPricingSessionManager()
        modifications = manager.get_pricing_modifications_from_session()

        assert modifications['discount_percent'] == 5.0
        assert modifications['discount_fixed'] == 100.0
        assert modifications['surcharge_percent'] == 2.0
        assert modifications['surcharge_fixed'] == 0.0
        assert modifications['accessories_cost'] == 50.0


def test_calculate_enhanced_pricing_no_components():
    """Test enhanced pricing calculation with no components"""

    class MockSessionState:
        def __init__(self):
            self._data = {}

        def get(self, key, default=None):
            return self._data.get(key, default)

        def __setitem__(self, key, value):
            self._data[key] = value

        def __getitem__(self, key):
            return self._data[key]

        def __contains__(self, key):
            return key in self._data

        def __setattr__(self, name, value):
            if name.startswith('_'):
                super().__setattr__(name, value)
            else:
                self._data[name] = value

        def __getattr__(self, name):
            if name in self._data:
                return self._data[name]
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'")

    mock_st = Mock()
    mock_st.session_state = MockSessionState()

    with patch.dict('sys.modules', {'streamlit': mock_st}):
        from calculations import calculate_enhanced_pricing

        # Should handle empty components gracefully
        result = calculate_enhanced_pricing([], "pv", use_cache=False)

        # Should return some result even with no components
        assert result is not None
        assert isinstance(result, dict)


def test_pricing_cache_invalidation():
    """Test pricing cache invalidation functionality"""
    mock_st = Mock()
    mock_st.session_state = {
        'enhanced_pricing': {
            'pv': {'base_price': 1000.0},
            'heatpump': {'base_price': 2000.0}
        }
    }

    with patch.dict('sys.modules', {'streamlit': mock_st}):
        from calculations import invalidate_pricing_cache

        # Test invalidating specific system
        invalidate_pricing_cache("pv")

        # Should still have heatpump data
        assert 'heatpump' in mock_st.session_state.get('enhanced_pricing', {})


def test_get_enhanced_pricing_from_session():
    """Test getting enhanced pricing from session state"""
    mock_st = Mock()
    pricing_data = {'base_price': 1000.0, 'final_price_net': 950.0}
    mock_st.session_state = {
        'enhanced_pricing': {
            'pv': pricing_data
        }
    }

    with patch.dict('sys.modules', {'streamlit': mock_st}):
        from calculations import get_enhanced_pricing_from_session

        result = get_enhanced_pricing_from_session("pv")
        assert result == pricing_data

        result = get_enhanced_pricing_from_session("heatpump")
        assert result is None


def test_update_pricing_on_component_change():
    """Test updating pricing when components change"""
    mock_st = Mock()
    mock_st.session_state = {}

    with patch.dict('sys.modules', {'streamlit': mock_st}):
        from calculations import update_pricing_on_component_change

        components = [{'product_id': 1, 'quantity': 2}]

        # Should handle the update gracefully even if pricing engine not
        # available
        result = update_pricing_on_component_change(components, "pv")

        # Should return boolean result
        assert isinstance(result, bool)


def test_get_pricing_cache_info():
    """Test getting pricing cache information"""
    mock_st = Mock()
    pricing_data = {
        'calculation_timestamp': '2023-01-01T12:00:00',
        'components': [{'id': 1}, {'id': 2}],
        'final_price_net': 1000.0,
        'dynamic_keys': {'key1': 'value1', 'key2': 'value2'},
        'cache_key': 'abcdef123456789'
    }

    mock_st.session_state = {
        'enhanced_pricing': {
            'pv': pricing_data
        }
    }

    with patch.dict('sys.modules', {'streamlit': mock_st}):
        from calculations import get_pricing_cache_info

        cache_info = get_pricing_cache_info()

        assert cache_info['cache_available'] is True
        assert 'pv' in cache_info['cached_systems']

        pv_details = cache_info['cache_details']['pv']
        assert pv_details['calculation_timestamp'] == '2023-01-01T12:00:00'
        assert pv_details['component_count'] == 2
        assert pv_details['final_price_net'] == 1000.0
        assert pv_details['dynamic_keys_count'] == 2
        assert pv_details['cache_key'] == 'abcdef12...'


def test_update_enhanced_pricing_in_calculation_results():
    """Test updating calculation results with enhanced pricing"""
    mock_st = Mock()
    mock_st.session_state = {}

    with patch.dict('sys.modules', {'streamlit': mock_st}):
        from calculations import _update_enhanced_pricing_in_calculation_results

        # Setup calculation results with component data
        results = {
            'pv_modules_selected': [
                {'model_name': 'Test Module', 'quantity': 10}
            ],
            'inverter_selected': {
                'model_name': 'Test Inverter'
            },
            'battery_selected': {
                'model_name': 'Test Battery', 'quantity': 1
            }
        }

        # Should handle the update gracefully even if enhanced pricing fails
        _update_enhanced_pricing_in_calculation_results(results)

        # Results should still be a dictionary
        assert isinstance(results, dict)


if __name__ == "__main__":
    pytest.main([__file__])
