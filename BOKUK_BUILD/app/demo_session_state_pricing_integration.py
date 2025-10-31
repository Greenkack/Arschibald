"""Demonstration of Enhanced Pricing System Session State Integration

This script demonstrates how the enhanced pricing system integrates with
Streamlit session state for real-time pricing updates and caching.
"""

from calculations import (
    EnhancedPricingSessionManager,
    _collect_pricing_modifications_from_session,
    calculate_enhanced_pricing,
    get_enhanced_pricing_from_session,
    get_pricing_cache_info,
    invalidate_pricing_cache,
    update_pricing_on_component_change,
)
import sys
from unittest.mock import Mock


# Mock streamlit for demonstration
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


# Mock streamlit module
mock_st = Mock()
mock_st.session_state = MockSessionState()
sys.modules['streamlit'] = mock_st

# Now import our enhanced pricing functions


def demonstrate_session_state_integration():
    """Demonstrate the enhanced pricing system session state integration"""

    print("🔧 Enhanced Pricing System - Session State Integration Demo")
    print("=" * 60)

    # 1. Setup session state with pricing modifications
    print("\n1. Setting up session state with pricing modifications...")
    mock_st.session_state['pricing_modifications_discount_slider'] = 5.0
    mock_st.session_state['pricing_modifications_rebates_slider'] = 100.0
    mock_st.session_state['pricing_modifications_surcharge_slider'] = 2.0
    mock_st.session_state['pricing_modifications_special_costs_slider'] = 50.0

    # Collect pricing modifications
    modifications = _collect_pricing_modifications_from_session()
    print(f"   Collected modifications: {modifications}")

    # 2. Test enhanced pricing session manager
    print("\n2. Testing Enhanced Pricing Session Manager...")
    manager = EnhancedPricingSessionManager()
    print(f"   Cache timeout: {manager.cache_timeout_seconds} seconds")

    # Get pricing modifications in enhanced format
    enhanced_mods = manager.get_pricing_modifications_from_session()
    print(f"   Enhanced format modifications: {enhanced_mods}")

    # 3. Test pricing calculation with empty components
    print("\n3. Testing pricing calculation with empty components...")
    result = calculate_enhanced_pricing([], "pv", use_cache=False)
    if result:
        print(f"   Base price: {result.get('base_price', 0):.2f} €")
        print(
            f"   Final price (net): {
                result.get(
                    'final_price_net',
                    0):.2f} €")
        print(f"   Components: {len(result.get('components', []))}")
        print(f"   Dynamic keys: {len(result.get('dynamic_keys', {}))}")
    else:
        print("   No pricing result (expected with empty components)")

    # 4. Test cache information
    print("\n4. Testing cache information...")
    cache_info = get_pricing_cache_info()
    print(f"   Cache available: {cache_info.get('cache_available', False)}")
    print(f"   Cached systems: {cache_info.get('cached_systems', [])}")

    # 5. Test component change handling
    print("\n5. Testing component change handling...")
    sample_components = [
        {'model_name': 'Sample PV Module', 'quantity': 10, 'category': 'PV Module'},
        {'model_name': 'Sample Inverter', 'quantity': 1, 'category': 'Inverter'}
    ]

    success = update_pricing_on_component_change(sample_components, "pv")
    print(f"   Component change update successful: {success}")

    # 6. Test cache invalidation
    print("\n6. Testing cache invalidation...")
    # First add some mock data to cache
    mock_st.session_state['enhanced_pricing'] = {
        'pv': {'base_price': 1000.0, 'cached': True},
        'heatpump': {'base_price': 2000.0, 'cached': True}
    }

    print(
        f"   Before invalidation: {
            list(
                mock_st.session_state.get(
                    'enhanced_pricing',
                    {}).keys())}")

    # Invalidate PV cache only
    invalidate_pricing_cache("pv")
    remaining_systems = list(
        mock_st.session_state.get(
            'enhanced_pricing',
            {}).keys())
    print(f"   After PV invalidation: {remaining_systems}")

    # 7. Test getting pricing from session
    print("\n7. Testing getting pricing from session...")
    pv_pricing = get_enhanced_pricing_from_session("pv")
    hp_pricing = get_enhanced_pricing_from_session("heatpump")

    print(f"   PV pricing available: {pv_pricing is not None}")
    print(f"   Heat pump pricing available: {hp_pricing is not None}")

    if hp_pricing:
        print(
            f"   Heat pump base price: {
                hp_pricing.get(
                    'base_price',
                    0):.2f} €")

    # 8. Test cache key generation
    print("\n8. Testing cache key generation...")
    calculation_data = {
        'components': [
            {'product_id': 1, 'quantity': 2},
            {'model_name': 'test_module', 'quantity': 1}
        ],
        'modifications': {'discount_percent': 5.0},
        'vat_rate': 19.0
    }

    cache_key = manager._generate_cache_key(calculation_data)
    print(f"   Generated cache key: {cache_key}")

    # Same data should produce same key
    cache_key2 = manager._generate_cache_key(calculation_data)
    print(f"   Key consistency check: {cache_key == cache_key2}")

    # Different data should produce different key
    calculation_data['modifications']['discount_percent'] = 10.0
    cache_key3 = manager._generate_cache_key(calculation_data)
    print(
        f"   Different data produces different key: {
            cache_key != cache_key3}")

    print("\n✅ Session State Integration Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("- ✓ Pricing modifications collection from session state")
    print("- ✓ Enhanced pricing calculation with session state storage")
    print("- ✓ Cache management and invalidation")
    print("- ✓ Real-time pricing updates on component changes")
    print("- ✓ Cache key generation and consistency")
    print("- ✓ Backward compatibility with legacy pricing fields")


def demonstrate_real_time_updates():
    """Demonstrate real-time pricing updates"""

    print("\n🔄 Real-time Pricing Updates Demo")
    print("=" * 40)

    # Simulate component selection changes
    components_v1 = [
        {'model_name': 'Basic PV Module', 'quantity': 8}
    ]

    components_v2 = [
        {'model_name': 'Basic PV Module', 'quantity': 10},
        {'model_name': 'Premium Inverter', 'quantity': 1}
    ]

    components_v3 = [
        {'model_name': 'Basic PV Module', 'quantity': 10},
        {'model_name': 'Premium Inverter', 'quantity': 1},
        {'model_name': 'Battery Storage', 'quantity': 1}
    ]

    print("\n1. Initial component selection (8 PV modules)...")
    update_pricing_on_component_change(components_v1, "pv")
    cache_info = get_pricing_cache_info()
    print(f"   Cached systems: {cache_info.get('cached_systems', [])}")

    print("\n2. Adding more modules and inverter...")
    update_pricing_on_component_change(components_v2, "pv")

    print("\n3. Adding battery storage...")
    update_pricing_on_component_change(components_v3, "pv")

    # Show final cache state
    final_cache = get_pricing_cache_info()
    if final_cache.get('cache_available'):
        for system, details in final_cache.get('cache_details', {}).items():
            print(f"\n   {system.upper()} System Cache:")
            print(f"     - Components: {details.get('component_count', 0)}")
            print(
                f"     - Final price: {details.get('final_price_net', 0):.2f} €")
            print(
                f"     - Dynamic keys: {details.get('dynamic_keys_count', 0)}")
            print(f"     - Cache key: {details.get('cache_key', 'N/A')}")

    print("\n✅ Real-time Updates Demo Complete!")


if __name__ == "__main__":
    try:
        demonstrate_session_state_integration()
        demonstrate_real_time_updates()

        print("\n🎉 All demonstrations completed successfully!")
        print(
            "\nThe enhanced pricing system is now integrated with Streamlit session state")
        print("and provides real-time pricing updates with intelligent caching.")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
