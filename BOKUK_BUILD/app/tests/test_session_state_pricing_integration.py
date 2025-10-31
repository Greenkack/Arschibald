"""Tests for enhanced pricing system integration with Streamlit session state"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

# Mock streamlit before importing our modules
mock_st = Mock()
mock_st.session_state = {}

with patch.dict('sys.modules', {'streamlit': mock_st}):
    from calculations import (
        EnhancedPricingSessionManager,
        _update_enhanced_pricing_in_calculation_results,
        calculate_enhanced_pricing,
        get_enhanced_pricing_from_session,
        get_pricing_cache_info,
        invalidate_pricing_cache,
        update_pricing_on_component_change,
    )


class TestEnhancedPricingSessionManager:
    """Test the EnhancedPricingSessionManager class"""

    def setup_method(self):
        """Setup for each test method"""
        self.manager = EnhancedPricingSessionManager()
        mock_st.session_state.clear()

    def test_initialization(self):
        """Test manager initialization"""
        assert self.manager.cache_timeout_seconds == 30
        assert self.manager._pricing_engines == {}

    @patch('calculations.PricingEngine')
    def test_get_pricing_engine_creation(self, mock_pricing_engine_class):
        """Test pricing engine creation and caching"""
        mock_engine = Mock()
        mock_pricing_engine_class.return_value = mock_engine

        # First call should create engine
        with patch.dict('sys.modules', {'pricing.enhanced_pricing_engine': Mock()}):
            engine = self.manager.get_pricing_engine("pv")

        assert engine == mock_engine
        assert "pv" in self.manager._pricing_engines

        # Second call should return cached engine
        engine2 = self.manager.get_pricing_engine("pv")
        assert engine2 == mock_engine
        assert mock_pricing_engine_class.call_count == 1

    def test_get_pricing_engine_import_error(self):
        """Test handling of import errors"""
        with patch('calculations.PricingEngine', side_effect=ImportError("Module not found")):
            engine = self.manager.get_pricing_engine("pv")

        assert engine is None

    def test_generate_cache_key(self):
        """Test cache key generation"""
        calculation_data = {
            'components': [
                {'product_id': 1, 'quantity': 2},
                {'model_name': 'test_module', 'quantity': 1}
            ],
            'modifications': {'discount_percent': 5.0},
            'vat_rate': 19.0
        }

        cache_key = self.manager._generate_cache_key(calculation_data)

        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5 hash length

        # Same data should produce same key
        cache_key2 = self.manager._generate_cache_key(calculation_data)
        assert cache_key == cache_key2

        # Different data should produce different key
        calculation_data['modifications']['discount_percent'] = 10.0
        cache_key3 = self.manager._generate_cache_key(calculation_data)
        assert cache_key != cache_key3

    def test_update_pricing_in_session_state_success(self):
        """Test successful pricing update in session state"""
        # Mock pricing engine and result
        mock_engine = Mock()
        mock_final_result = Mock()
        mock_final_result.base_price = 1000.0
        mock_final_result.final_price_net = 950.0
        mock_final_result.final_price_gross = 1130.5
        mock_final_result.total_discounts = 50.0
        mock_final_result.total_surcharges = 0.0
        mock_final_result.vat_amount = 180.5
        mock_final_result.components = []
        mock_final_result.dynamic_keys = {"PV_BASE_PRICE": 1000.0}
        mock_final_result.metadata = {"system_type": "pv"}
        mock_final_result.calculation_timestamp = datetime.now()

        mock_engine.validate_pricing_data.return_value = True
        mock_engine.generate_final_price.return_value = mock_final_result

        self.manager._pricing_engines["pv"] = mock_engine

        calculation_data = {
            'components': [{'product_id': 1, 'quantity': 1}],
            'modifications': {},
            'vat_rate': 19.0
        }

        # Test update
        result = self.manager.update_pricing_in_session_state(
            calculation_data, "pv")

        assert result is True
        assert 'enhanced_pricing' in mock_st.session_state
        assert 'pv' in mock_st.session_state['enhanced_pricing']

        pricing_data = mock_st.session_state['enhanced_pricing']['pv']
        assert pricing_data['base_price'] == 1000.0
        assert pricing_data['final_price_net'] == 950.0
        assert pricing_data['final_price_gross'] == 1130.5
        assert 'dynamic_keys' in pricing_data
        assert 'cache_key' in pricing_data

    def test_update_pricing_invalid_data(self):
        """Test handling of invalid pricing data"""
        mock_engine = Mock()
        mock_engine.validate_pricing_data.return_value = False

        self.manager._pricing_engines["pv"] = mock_engine

        calculation_data = {'invalid': 'data'}

        result = self.manager.update_pricing_in_session_state(
            calculation_data, "pv")

        assert result is False
        mock_engine.validate_pricing_data.assert_called_once_with(
            calculation_data)

    def test_get_cached_pricing_valid_cache(self):
        """Test getting valid cached pricing data"""
        # Setup cached data
        cache_key = "test_cache_key"
        cached_data = {
            'base_price': 1000.0,
            'cache_key': cache_key,
            'calculation_timestamp': datetime.now().isoformat()
        }

        mock_st.session_state['enhanced_pricing'] = {'pv': cached_data}

        calculation_data = {'components': []}

        with patch.object(self.manager, '_generate_cache_key', return_value=cache_key):
            result = self.manager.get_cached_pricing(calculation_data, "pv")

        assert result == cached_data

    def test_get_cached_pricing_invalid_cache_key(self):
        """Test cache miss due to different cache key"""
        cached_data = {
            'base_price': 1000.0,
            'cache_key': 'old_key',
            'calculation_timestamp': datetime.now().isoformat()
        }

        mock_st.session_state['enhanced_pricing'] = {'pv': cached_data}

        calculation_data = {'components': []}

        with patch.object(self.manager, '_generate_cache_key', return_value='new_key'):
            result = self.manager.get_cached_pricing(calculation_data, "pv")

        assert result is None

    def test_get_cached_pricing_expired_cache(self):
        """Test cache miss due to expired timestamp"""
        # Create expired timestamp
        expired_time = datetime.now() - timedelta(seconds=60)
        cached_data = {
            'base_price': 1000.0,
            'cache_key': 'test_key',
            'calculation_timestamp': expired_time.isoformat()
        }

        mock_st.session_state['enhanced_pricing'] = {'pv': cached_data}

        calculation_data = {'components': []}

        with patch.object(self.manager, '_generate_cache_key', return_value='test_key'):
            result = self.manager.get_cached_pricing(calculation_data, "pv")

        assert result is None

    def test_invalidate_pricing_cache_specific_system(self):
        """Test invalidating cache for specific system type"""
        mock_st.session_state['enhanced_pricing'] = {
            'pv': {'data': 'pv_data'},
            'heatpump': {'data': 'hp_data'}
        }

        self.manager.invalidate_pricing_cache("pv")

        assert 'pv' not in mock_st.session_state['enhanced_pricing']
        assert 'heatpump' in mock_st.session_state['enhanced_pricing']

    def test_invalidate_pricing_cache_all_systems(self):
        """Test invalidating cache for all systems"""
        mock_st.session_state['enhanced_pricing'] = {
            'pv': {'data': 'pv_data'},
            'heatpump': {'data': 'hp_data'}
        }

        self.manager.invalidate_pricing_cache(None)

        assert mock_st.session_state['enhanced_pricing'] == {}

    def test_get_pricing_modifications_from_session(self):
        """Test getting pricing modifications from session state"""
        # Setup session state with pricing modifications
        mock_st.session_state['pricing_modifications'] = {
            'discount_percent': 5.0,
            'surcharge_percent': 2.0,
            'special_discount': 100.0,
            'additional_costs': 50.0
        }

        mock_st.session_state['pricing_modifications_discount_slider'] = 10.0
        mock_st.session_state['pricing_modifications_rebates_slider'] = 200.0

        modifications = self.manager.get_pricing_modifications_from_session()

        # Should use higher slider values
        assert modifications['discount_percent'] == 10.0  # max(5.0, 10.0)
        assert modifications['discount_fixed'] == 200.0   # max(100.0, 200.0)
        assert modifications['surcharge_percent'] == 2.0
        assert modifications['surcharge_fixed'] == 0.0
        assert modifications['accessories_cost'] == 50.0

    def test_update_legacy_pricing_fields(self):
        """Test updating legacy pricing fields for backward compatibility"""
        mock_final_result = Mock()
        mock_final_result.base_price = 1000.0
        mock_final_result.final_price_net = 950.0
        mock_final_result.final_price_gross = 1130.5
        mock_final_result.total_discounts = 50.0
        mock_final_result.total_surcharges = 0.0
        mock_final_result.vat_amount = 180.5

        self.manager._update_legacy_pricing_fields(mock_final_result, "pv")

        assert mock_st.session_state["base_matrix_price_netto"] == 1000.0
        assert mock_st.session_state["final_price_netto"] == 950.0
        assert mock_st.session_state["final_price_brutto"] == 1130.5

        live_calc = mock_st.session_state["live_pricing_calculations"]
        assert live_calc["base_cost"] == 1000.0
        assert live_calc["final_price"] == 950.0
        assert live_calc["enhanced_pricing"] is True


class TestIntegrationFunctions:
    """Test the integration functions"""

    def setup_method(self):
        """Setup for each test method"""
        mock_st.session_state.clear()

    @patch('calculations._pricing_session_manager')
    def test_calculate_enhanced_pricing_with_cache(self, mock_manager):
        """Test calculate_enhanced_pricing with cache hit"""
        cached_result = {'base_price': 1000.0, 'cached': True}
        mock_manager.get_cached_pricing.return_value = cached_result
        mock_manager.get_pricing_modifications_from_session.return_value = {}

        components = [{'product_id': 1, 'quantity': 1}]
        result = calculate_enhanced_pricing(components, "pv", use_cache=True)

        assert result == cached_result
        mock_manager.get_cached_pricing.assert_called_once()
        mock_manager.update_pricing_in_session_state.assert_not_called()

    @patch('calculations._pricing_session_manager')
    def test_calculate_enhanced_pricing_cache_miss(self, mock_manager):
        """Test calculate_enhanced_pricing with cache miss"""
        mock_manager.get_cached_pricing.return_value = None
        mock_manager.update_pricing_in_session_state.return_value = True
        mock_manager.get_pricing_modifications_from_session.return_value = {}

        # Setup session state with result
        pricing_data = {'base_price': 1000.0, 'calculated': True}
        mock_st.session_state['enhanced_pricing'] = {'pv': pricing_data}

        components = [{'product_id': 1, 'quantity': 1}]
        result = calculate_enhanced_pricing(components, "pv", use_cache=True)

        assert result == pricing_data
        mock_manager.update_pricing_in_session_state.assert_called_once()

    @patch('calculations._pricing_session_manager')
    def test_invalidate_pricing_cache_function(self, mock_manager):
        """Test invalidate_pricing_cache function"""
        invalidate_pricing_cache("pv")
        mock_manager.invalidate_pricing_cache.assert_called_once_with("pv")

        invalidate_pricing_cache(None)
        mock_manager.invalidate_pricing_cache.assert_called_with(None)

    def test_get_enhanced_pricing_from_session(self):
        """Test getting enhanced pricing from session state"""
        pricing_data = {'base_price': 1000.0}
        mock_st.session_state['enhanced_pricing'] = {'pv': pricing_data}

        result = get_enhanced_pricing_from_session("pv")
        assert result == pricing_data

        result = get_enhanced_pricing_from_session("heatpump")
        assert result is None

    @patch('calculations.calculate_enhanced_pricing')
    @patch('calculations.invalidate_pricing_cache')
    def test_update_pricing_on_component_change(
            self, mock_invalidate, mock_calculate):
        """Test updating pricing when components change"""
        mock_calculate.return_value = {'updated': True}

        components = [{'product_id': 1, 'quantity': 2}]
        result = update_pricing_on_component_change(components, "pv")

        assert result is True
        mock_invalidate.assert_called_once_with("pv")
        mock_calculate.assert_called_once_with(
            components, "pv", use_cache=False)

    def test_get_pricing_cache_info(self):
        """Test getting pricing cache information"""
        # Setup cache data
        pricing_data = {
            'calculation_timestamp': '2023-01-01T12:00:00',
            'components': [{'id': 1}, {'id': 2}],
            'final_price_net': 1000.0,
            'dynamic_keys': {'key1': 'value1', 'key2': 'value2'},
            'cache_key': 'abcdef123456789'
        }

        mock_st.session_state['enhanced_pricing'] = {
            'pv': pricing_data,
            'heatpump': pricing_data
        }

        cache_info = get_pricing_cache_info()

        assert cache_info['cache_available'] is True
        assert set(cache_info['cached_systems']) == {'pv', 'heatpump'}

        pv_details = cache_info['cache_details']['pv']
        assert pv_details['calculation_timestamp'] == '2023-01-01T12:00:00'
        assert pv_details['component_count'] == 2
        assert pv_details['final_price_net'] == 1000.0
        assert pv_details['dynamic_keys_count'] == 2
        assert pv_details['cache_key'] == 'abcdef12...'

    def test_update_enhanced_pricing_in_calculation_results(self):
        """Test updating calculation results with enhanced pricing"""
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

        # Mock enhanced pricing calculation
        enhanced_pricing = {
            'base_price': 1000.0,
            'final_price_net': 950.0,
            'final_price_gross': 1130.5,
            'total_discounts': 50.0,
            'total_surcharges': 0.0,
            'vat_amount': 180.5,
            'components': [{'id': 1}, {'id': 2}],
            'dynamic_keys': {'key1': 'value1'},
            'calculation_timestamp': '2023-01-01T12:00:00'
        }

        with patch('calculations.calculate_enhanced_pricing', return_value=enhanced_pricing):
            _update_enhanced_pricing_in_calculation_results(results)

        # Check that enhanced pricing was added to results
        assert 'enhanced_pricing' in results
        ep = results['enhanced_pricing']
        assert ep['base_price'] == 1000.0
        assert ep['final_price_net'] == 950.0
        assert ep['component_count'] == 2
        assert ep['dynamic_keys_count'] == 1

        # Check legacy fields were updated
        assert results['final_price_netto'] == 950.0
        assert results['final_price_brutto'] == 1130.5


class TestErrorHandling:
    """Test error handling in session state integration"""

    def setup_method(self):
        """Setup for each test method"""
        mock_st.session_state.clear()

    def test_calculate_enhanced_pricing_exception(self):
        """Test handling of exceptions in calculate_enhanced_pricing"""
        with patch('calculations._pricing_session_manager') as mock_manager:
            mock_manager.get_pricing_modifications_from_session.side_effect = Exception(
                "Test error")

            result = calculate_enhanced_pricing([])
            assert result is None

    def test_get_enhanced_pricing_from_session_no_streamlit(self):
        """Test handling when streamlit is not available"""
        with patch('calculations.st', Mock(spec=[])):  # Mock without session_state
            result = get_enhanced_pricing_from_session("pv")
            assert result is None

    def test_get_pricing_cache_info_error(self):
        """Test error handling in get_pricing_cache_info"""
        with patch('calculations.st', Mock(spec=[])):  # Mock without session_state
            cache_info = get_pricing_cache_info()
            assert cache_info['cache_available'] is False
            assert 'No session state' in cache_info['reason']


if __name__ == "__main__":
    pytest.main([__file__])
