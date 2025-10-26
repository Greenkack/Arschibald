# calculations.py
"""
Hauptmodul für die Berechnung von Photovoltaikanlagen und Wirtschaftlichkeitsanalysen.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from typing import Any

import numpy as np
import requests  # Für HTTP-Anfragen an PVGIS

# Import der erweiterten PV-Berechnungsalgorithmen
try:
    from pv_calculations_core import (
        PVCalculationsAdvanced,
        calculate_annual_energy_yield,
        calculate_annuity,
        calculate_autarky_degree,
        calculate_co2_payback_time,
        calculate_co2_savings,
        calculate_comprehensive_pv_analysis,
        calculate_irr,
        calculate_leasing_costs,
        calculate_net_present_value,
        calculate_payback_period,
        calculate_self_consumption_quote,
        calculate_total_roi,
    )
    PV_CALCULATIONS_CORE_AVAILABLE = True
except ImportError as e:
    PV_CALCULATIONS_CORE_AVAILABLE = False
    print(f"Warnung: pv_calculations_core nicht verfügbar: {e}")
    # Fallback-Implementierungen werden bei Bedarf verwendet

# Streamlit Import für UI-Funktionen
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Dummy st für Kompatibilität

    class DummySt:
        @staticmethod
        def info(msg): print(f"INFO: {msg}")
        @staticmethod
        def warning(msg): print(f"WARNING: {msg}")
        @staticmethod
        def error(msg): print(f"ERROR: {msg}")

        class sidebar:
            @staticmethod
            def info(msg): print(f"SIDEBAR INFO: {msg}")
    st = DummySt()

_global_import_errors_calc: list[str] = []


# --- DUMMY FUNKTIONEN UND FALLBACKS ---
def Dummy_load_admin_setting_calc(key, default=None):
    if key == "price_matrix_csv_data":
        return ""
    if key == "price_matrix_excel_bytes":
        return None
    if key == "feed_in_tariffs":
        return {
            "parts": [
                {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 7.92},
                {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 6.88},
                {"kwp_min": 40.01, "kwp_max": 100.0, "ct_per_kwh": 5.62},
            ],
            "full": [
                {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 12.60},
                {"kwp_min": 10.01, "kwp_max": 100.0, "ct_per_kwh": 10.56},
            ],
        }
    if key == "global_constants":
        return {
            "vat_rate_percent": 0.0,
            "electricity_price_increase_annual_percent": 3.0,
            "simulation_period_years": 20,
            "inflation_rate_percent": 2.0,
            "loan_interest_rate_percent": 4.0,
            "capital_gains_tax_kest_percent": 26.375,
            "alternative_investment_interest_rate_percent": 5.0,
            "co2_emission_factor_kg_per_kwh": 0.474,
            "maintenance_costs_base_percent": 1.5,
            "einspeiseverguetung_period_years": 20,
            "marktwert_strom_eur_per_kwh_after_eeg": 0.03,
            "storage_cycles_per_year": 250,
            "storage_efficiency": 0.9,
            "eauto_annual_km": 10000,
            "eauto_consumption_kwh_per_100km": 18.0,
            "eauto_pv_share_percent": 30.0,
            "heatpump_cop_factor": 3.5,
            "heatpump_pv_share_percent": 40.0,
            "afa_period_years": 20,
            "pvgis_system_loss_default_percent": 14.0,
            "annual_module_degradation_percent": 0.5,
            "maintenance_fixed_eur_pa": 50.0,
            "maintenance_variable_eur_per_kwp_pa": 5.0,
            "maintenance_increase_percent_pa": 2.0,
            "one_time_bonus_eur": 0.0,
            "global_yield_adjustment_percent": 0.0,
            "default_specific_yield_kwh_kwp": 950.0,
            "reference_specific_yield_pr": 1100.0,
            "pvgis_enabled": True,  # Neue Option für PVGIS aktivieren/deaktivieren
            "specific_yields_by_orientation_tilt": {
                "Süd_0": 950.0,
                "Süd_15": 980.0,
                "Süd_30": 1000.0,
                "Süd_45": 980.0,
                "Süd_60": 950.0,
                "Südost_0": 900.0,
                "Südost_15": 930.0,
                "Südost_30": 950.0,
                "Südost_45": 930.0,
                "Südost_60": 900.0,
                "Südwest_0": 900.0,
                "Südwest_15": 930.0,
                "Südwest_30": 950.0,
                "Südwest_45": 930.0,
                "Südwest_60": 900.0,
                "Ost_0": 850.0,
                "Ost_15": 880.0,
                "Ost_30": 900.0,
                "Ost_45": 880.0,
                "Ost_60": 850.0,
                "West_0": 850.0,
                "West_15": 880.0,
                "West_30": 900.0,
                "West_45": 880.0,
                "West_60": 850.0,
                "Nord_0": 700.0,
                "Nord_15": 720.0,
                "Nord_30": 750.0,
                "Nord_45": 720.0,
                "Nord_60": 700.0,
                "Nordost_0": 750.0,
                "Nordost_15": 770.0,
                "Nordost_30": 800.0,
                "Nordost_45": 770.0,
                "Nordost_60": 750.0,
                "Nordwest_0": 750.0,
                "Nordwest_15": 770.0,
                "Nordwest_30": 800.0,
                "Nordwest_45": 770.0,
                "Nordwest_60": 750.0,
                "Flachdach_0": 900.0,
                "Flachdach_15": 920.0,
                "Sonstige_0": 800.0,
                "Sonstige_15": 820.0,
                "Sonstige_30": 850.0,
                "Sonstige_45": 820.0,
                "Sonstige_60": 800.0,
            },
            "monthly_production_distribution": [
                0.03,
                0.05,
                0.08,
                0.11,
                0.13,
                0.14,
                0.13,
                0.12,
                0.09,
                0.06,
                0.04,
                0.02,
            ],
            "monthly_consumption_distribution": [
                0.0833,
                0.0833,
                0.0833,
                0.0833,
                0.0833,
                0.0833,
                0.0833,
                0.0833,
                0.0833,
                0.0833,
                0.0833,
                0.0837,
            ],  # Summe ca. 1
            "direct_self_consumption_factor_of_production": 0.25,
            "co2_per_tree_kg_pa": 12.5,
            "co2_per_car_km_kg": 0.12,
            "co2_per_flight_muc_pmi_kg": 180.0,
            "economic_settings": {
                "reference_specific_yield_for_pr_kwh_per_kwp": 1100.0
            },
            "default_performance_ratio_percent": 78.0,
            "peak_shaving_effect_kw_estimate": 0.0,
            "optimal_storage_factor": 1.0,
            "app_debug_mode_enabled": False,
        }
    return default


def Dummy_list_products_calc(category=None):
    return []


def Dummy_get_product_by_id_calc(product_id):
    return None


def Dummy_get_product_by_model_name_calc(model_name):
    return None


_DATABASE_AVAILABLE = False
try:
    from database import load_admin_setting as real_load_admin_setting

    if not callable(real_load_admin_setting):
        raise ImportError("real_load_admin_setting nicht aufrufbar.")
    _DATABASE_AVAILABLE = True
except ImportError:
    real_load_admin_setting = Dummy_load_admin_setting_calc
except Exception:
    real_load_admin_setting = Dummy_load_admin_setting_calc

_PRODUCT_DB_AVAILABLE = True
try:
    from product_db import (
        get_product_by_id as real_get_product_by_id,
    )
    from product_db import (
        get_product_by_model_name as real_get_product_by_model_name,
    )
    from product_db import (
        list_products as real_list_products,
    )

    if (
        not callable(real_list_products)
        or not callable(real_get_product_by_id)
        or not callable(real_get_product_by_model_name)
    ):
        raise ImportError(
            "Eine oder mehrere Produkt-DB Funktionen sind nicht aufrufbar."
        )
    _PRODUCT_DB_AVAILABLE = True
except ImportError:
    real_list_products, real_get_product_by_id, real_get_product_by_model_name = (
        Dummy_list_products_calc,
        Dummy_get_product_by_id_calc,
        Dummy_get_product_by_model_name_calc,
    )
except Exception:
    real_list_products, real_get_product_by_id, real_get_product_by_model_name = (
        Dummy_list_products_calc,
        Dummy_get_product_by_id_calc,
        Dummy_get_product_by_model_name_calc,
    )


# Old cache implementation removed - now using MatrixLoader class


def _collect_pricing_modifications_from_session() -> dict[str, float]:
    """
    Sammelt alle Preismodifikationen aus verschiedenen Session State Quellen.

    Returns:
        Dictionary mit standardisierten Preismodifikationen
    """
    try:
        import streamlit as st
        if not hasattr(st, "session_state"):
            return {}

        def _to_float(val, default=0.0):
            try:
                return float(val or 0.0)
            except Exception:
                return default

        # Sammle aus verschiedenen Session State Quellen
        modifications = {}

        # Aus pricing_modifications Dictionary (falls vorhanden)
        pricing_mods = st.session_state.get("pricing_modifications", {})
        modifications["discount_percent"] = _to_float(
            pricing_mods.get("discount_percent", 0.0))
        modifications["surcharge_percent"] = _to_float(
            pricing_mods.get("surcharge_percent", 0.0))
        modifications["special_discount"] = _to_float(
            pricing_mods.get("special_discount", 0.0))
        modifications["additional_costs"] = _to_float(
            pricing_mods.get("additional_costs", 0.0))

        # Aus individuellen Session State Keys (Slider-Werte)
        slider_discount = _to_float(st.session_state.get(
            "pricing_modifications_discount_slider", 0.0))
        slider_rebates = _to_float(st.session_state.get(
            "pricing_modifications_rebates_slider", 0.0))
        slider_surcharge = _to_float(st.session_state.get(
            "pricing_modifications_surcharge_slider", 0.0))
        slider_special_costs = _to_float(st.session_state.get(
            "pricing_modifications_special_costs_slider", 0.0))
        slider_miscellaneous = _to_float(st.session_state.get(
            "pricing_modifications_miscellaneous_slider", 0.0))

        # Verwende Slider-Werte falls sie höher sind (Slider haben Priorität)
        modifications["discount_percent"] = max(
            modifications["discount_percent"], slider_discount)
        modifications["surcharge_percent"] = max(
            modifications["surcharge_percent"], slider_surcharge)
        modifications["special_discount"] = max(
            modifications["special_discount"], slider_rebates)
        modifications["additional_costs"] = max(
            modifications["additional_costs"],
            slider_special_costs + slider_miscellaneous)

        return modifications

    except Exception as e:
        print(f"Warning: Could not collect pricing modifications: {e}")
        return {}


class EnhancedPricingSessionManager:
    """Manages enhanced pricing system integration with Streamlit session state"""

    def __init__(self):
        self.cache_timeout_seconds = 30  # Cache timeout for pricing calculations
        self._pricing_engines = {}  # Cache for pricing engines

        # Initialize intelligent caching system
        try:
            from pricing.pricing_cache import get_cache_manager
            self.intelligent_cache_manager = get_cache_manager()
            self.intelligent_caching_enabled = True
        except ImportError:
            self.intelligent_cache_manager = None
            self.intelligent_caching_enabled = False

    def get_pricing_engine(self, system_type: str = "pv"):
        """Get or create pricing engine for system type"""
        if system_type not in self._pricing_engines:
            try:
                from pricing.enhanced_pricing_engine import PricingEngine
                self._pricing_engines[system_type] = PricingEngine(system_type)
            except ImportError:
                print(
                    f"Warning: Enhanced pricing engine not available for {system_type}")
                return None
        return self._pricing_engines[system_type]

    def update_pricing_in_session_state(self, calculation_data: dict[str, Any],
                                        system_type: str = "pv") -> bool:
        """Update session state with enhanced pricing calculations

        Args:
            calculation_data: Complete calculation data including components and modifications
            system_type: Type of system ("pv", "heatpump", "combined")

        Returns:
            True if update was successful, False otherwise
        """
        try:
            import streamlit as st
            if not hasattr(st, "session_state"):
                return False

            # Ensure session_state is accessible
            if not hasattr(st.session_state, '__setitem__'):
                return False

            # Get pricing engine
            pricing_engine = self.get_pricing_engine(system_type)
            if not pricing_engine:
                return False

            # Validate input data
            if not pricing_engine.validate_pricing_data(calculation_data):
                print(f"Warning: Invalid pricing data for {system_type}")
                return False

            # Calculate final pricing
            final_result = pricing_engine.generate_final_price(
                calculation_data)

            # Initialize session state pricing structure if needed
            if hasattr(st.session_state, '__setitem__'):
                if 'enhanced_pricing' not in st.session_state:
                    st.session_state['enhanced_pricing'] = {}

                # Store pricing data by system type
                pricing_data = {
                    'base_price': final_result.base_price,
                    'final_price_net': final_result.final_price_net,
                    'final_price_gross': final_result.final_price_gross,
                    'total_discounts': final_result.total_discounts,
                    'total_surcharges': final_result.total_surcharges,
                    'vat_amount': final_result.vat_amount,
                    'components': [
                        {
                            'product_id': comp.product_id,
                            'model_name': comp.model_name,
                            'category': comp.category,
                            'quantity': comp.quantity,
                            'unit_price': comp.unit_price,
                            'total_price': comp.total_price,
                            'calculate_per': comp.calculate_per
                        }
                        for comp in final_result.components
                    ],
                    'dynamic_keys': final_result.dynamic_keys,
                    'metadata': final_result.metadata,
                    'calculation_timestamp': final_result.calculation_timestamp.isoformat(),
                    'cache_key': self._generate_cache_key(calculation_data)
                }

                enhanced_pricing = st.session_state.get('enhanced_pricing', {})
                enhanced_pricing[system_type] = pricing_data
                st.session_state['enhanced_pricing'] = enhanced_pricing
            else:
                # Fallback for mock objects or limited session state
                if not hasattr(st.session_state, 'enhanced_pricing'):
                    st.session_state.enhanced_pricing = {}

                pricing_data = {
                    'base_price': final_result.base_price,
                    'final_price_net': final_result.final_price_net,
                    'final_price_gross': final_result.final_price_gross,
                    'total_discounts': final_result.total_discounts,
                    'total_surcharges': final_result.total_surcharges,
                    'vat_amount': final_result.vat_amount,
                    'components': [
                        {
                            'product_id': comp.product_id,
                            'model_name': comp.model_name,
                            'category': comp.category,
                            'quantity': comp.quantity,
                            'unit_price': comp.unit_price,
                            'total_price': comp.total_price,
                            'calculate_per': comp.calculate_per
                        }
                        for comp in final_result.components
                    ],
                    'dynamic_keys': final_result.dynamic_keys,
                    'metadata': final_result.metadata,
                    'calculation_timestamp': final_result.calculation_timestamp.isoformat(),
                    'cache_key': self._generate_cache_key(calculation_data)
                }

                st.session_state.enhanced_pricing[system_type] = pricing_data

            # Update global dynamic keys for PDF integration
            if 'dynamic_keys' not in st.session_state:
                st.session_state.dynamic_keys = {}

            st.session_state.dynamic_keys.update(final_result.dynamic_keys)

            # Update legacy pricing fields for backward compatibility
            self._update_legacy_pricing_fields(final_result, system_type)

            # Invalidate dependent caches
            self._invalidate_dependent_caches(system_type)

            return True

        except Exception as e:
            print(f"Error updating enhanced pricing in session state: {e}")
            return False

    def get_cached_pricing(self, calculation_data: dict[str, Any],
                           system_type: str = "pv") -> dict[str, Any] | None:
        """Get cached pricing data if available and valid

        Args:
            calculation_data: Current calculation data to check against cache
            system_type: Type of system ("pv", "heatpump", "combined")

        Returns:
            Cached pricing data if valid, None otherwise
        """
        try:
            import streamlit as st
            if not hasattr(
                    st, "session_state") or not hasattr(
                    st.session_state, 'get'):
                return None

            enhanced_pricing = st.session_state.get('enhanced_pricing', {})
            cached_data = enhanced_pricing.get(system_type)

            if not cached_data:
                return None

            # Check cache validity
            cache_key = self._generate_cache_key(calculation_data)
            if cached_data.get('cache_key') != cache_key:
                return None

            # Check cache timeout
            from datetime import datetime, timedelta
            cache_time = datetime.fromisoformat(
                cached_data['calculation_timestamp'])
            if datetime.now() - cache_time > timedelta(seconds=self.cache_timeout_seconds):
                return None

            return cached_data

        except Exception as e:
            print(f"Error getting cached pricing: {e}")
            return None

    def invalidate_pricing_cache(self, system_type: str | None = None) -> None:
        """Invalidate pricing cache for specific system type or all systems

        Args:
            system_type: System type to invalidate, or None for all systems
        """
        try:
            import streamlit as st
            if not hasattr(st, "session_state"):
                return

            # Ensure session_state supports item access
            if not hasattr(st.session_state, 'get'):
                return

            if system_type:
                # Invalidate specific system type
                enhanced_pricing = st.session_state.get('enhanced_pricing', {})
                if system_type in enhanced_pricing:
                    del enhanced_pricing[system_type]
                    # Update session state if possible
                    if hasattr(st.session_state, '__setitem__'):
                        st.session_state['enhanced_pricing'] = enhanced_pricing
            else:
                # Invalidate all pricing caches
                if hasattr(st.session_state, '__setitem__'):
                    st.session_state['enhanced_pricing'] = {}

            # Also invalidate intelligent cache if enabled
            if self.intelligent_caching_enabled and self.intelligent_cache_manager:
                if system_type:
                    invalidated = self.intelligent_cache_manager.invalidate_system_cache(
                        system_type)
                    print(
                        f"Invalidated {invalidated} intelligent cache entries for {system_type}")
                else:
                    cleared = self.intelligent_cache_manager.cache.clear()
                    print(f"Cleared {cleared} intelligent cache entries")

            # Also invalidate dependent caches
            self._invalidate_dependent_caches(system_type)

        except Exception as e:
            print(f"Error invalidating pricing cache: {e}")

    def get_pricing_modifications_from_session(self) -> dict[str, Any]:
        """Get pricing modifications from session state in enhanced format

        Returns:
            Dictionary with pricing modifications compatible with enhanced pricing engine
        """
        legacy_mods = _collect_pricing_modifications_from_session()

        # Convert to enhanced pricing format
        return {
            'discount_percent': legacy_mods.get('discount_percent', 0.0),
            'discount_fixed': legacy_mods.get('special_discount', 0.0),
            'surcharge_percent': legacy_mods.get('surcharge_percent', 0.0),
            'surcharge_fixed': 0.0,  # Not used in legacy system
            'accessories_cost': legacy_mods.get('additional_costs', 0.0)
        }

    def _generate_cache_key(self, calculation_data: dict[str, Any]) -> str:
        """Generate cache key for calculation data"""
        import hashlib
        import json

        # Create a normalized representation for hashing
        cache_data = {
            'components': sorted([
                {
                    'id': comp.get('product_id', comp.get('model_name', '')),
                    'qty': comp.get('quantity', 1)
                }
                for comp in calculation_data.get('components', [])
            ], key=lambda x: str(x['id'])),
            'modifications': calculation_data.get('modifications', {}),
            'vat_rate': calculation_data.get('vat_rate', 19.0)
        }

        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _update_legacy_pricing_fields(
            self, final_result, system_type: str) -> None:
        """Update legacy pricing fields in session state for backward compatibility"""
        try:
            import streamlit as st

            # Update main pricing fields used by existing code
            if system_type == "pv":
                if hasattr(st.session_state, '__setitem__'):
                    st.session_state["base_matrix_price_netto"] = final_result.base_price
                    st.session_state["final_price_netto"] = final_result.final_price_net
                    st.session_state["final_price_brutto"] = final_result.final_price_gross

                    # Update live pricing calculations for PDF integration
                    st.session_state["live_pricing_calculations"] = {
                        "base_cost": final_result.base_price,
                        "final_price": final_result.final_price_net,
                        "final_price_brutto": final_result.final_price_gross,
                        "total_discounts": final_result.total_discounts,
                        "total_surcharges": final_result.total_surcharges,
                        "vat_amount": final_result.vat_amount,
                        "enhanced_pricing": True  # Flag to indicate enhanced pricing is active
                    }
                else:
                    # Fallback for mock objects
                    st.session_state.base_matrix_price_netto = final_result.base_price
                    st.session_state.final_price_netto = final_result.final_price_net
                    st.session_state.final_price_brutto = final_result.final_price_gross
                    st.session_state.live_pricing_calculations = {
                        "base_cost": final_result.base_price,
                        "final_price": final_result.final_price_net,
                        "final_price_brutto": final_result.final_price_gross,
                        "total_discounts": final_result.total_discounts,
                        "total_surcharges": final_result.total_surcharges,
                        "vat_amount": final_result.vat_amount,
                        "enhanced_pricing": True
                    }

        except Exception as e:
            print(f"Error updating legacy pricing fields: {e}")

    def _invalidate_dependent_caches(self, system_type: str | None) -> None:
        """Invalidate caches that depend on pricing calculations"""
        try:
            import streamlit as st
            if not hasattr(st, "session_state"):
                return

            # List of session state keys that should be invalidated when
            # pricing changes
            dependent_keys = [
                'calculation_results',
                'calculation_results_backup',
                'pdf_generation_cache',
                'economic_analysis_cache'
            ]

            for key in dependent_keys:
                if key in st.session_state:
                    del st.session_state[key]

        except Exception as e:
            print(f"Error invalidating dependent caches: {e}")


# Global instance for session management
_pricing_session_manager = EnhancedPricingSessionManager()


def _update_enhanced_pricing_in_calculation_results(
        results: dict[str, Any]) -> None:
    """Update calculation results with enhanced pricing data if available"""
    try:
        # Extract component information from results if available
        components = []

        # Try to extract PV components
        if "pv_modules_selected" in results and results["pv_modules_selected"]:
            for module_info in results["pv_modules_selected"]:
                if isinstance(module_info,
                              dict) and "model_name" in module_info:
                    components.append({
                        "model_name": module_info["model_name"],
                        "quantity": module_info.get("quantity", 1),
                        "category": "PV Module"
                    })

        # Try to extract inverter information
        if "inverter_selected" in results and results["inverter_selected"]:
            inverter_info = results["inverter_selected"]
            if isinstance(
                    inverter_info,
                    dict) and "model_name" in inverter_info:
                components.append({
                    "model_name": inverter_info["model_name"],
                    "quantity": 1,
                    "category": "Inverter"
                })

        # Try to extract battery information
        if "battery_selected" in results and results["battery_selected"]:
            battery_info = results["battery_selected"]
            if isinstance(battery_info, dict) and "model_name" in battery_info:
                components.append({
                    "model_name": battery_info["model_name"],
                    "quantity": battery_info.get("quantity", 1),
                    "category": "Battery"
                })

        # If we have components, calculate enhanced pricing
        if components:
            enhanced_pricing = calculate_enhanced_pricing(
                components, "pv", use_cache=True)

            if enhanced_pricing:
                # Add enhanced pricing data to results
                results["enhanced_pricing"] = {
                    "base_price": enhanced_pricing["base_price"],
                    "final_price_net": enhanced_pricing["final_price_net"],
                    "final_price_gross": enhanced_pricing["final_price_gross"],
                    "total_discounts": enhanced_pricing["total_discounts"],
                    "total_surcharges": enhanced_pricing["total_surcharges"],
                    "vat_amount": enhanced_pricing["vat_amount"],
                    "component_count": len(
                        enhanced_pricing["components"]),
                    "dynamic_keys_count": len(
                        enhanced_pricing["dynamic_keys"]),
                    "calculation_timestamp": enhanced_pricing["calculation_timestamp"]}

                # Update legacy pricing fields for compatibility
                if enhanced_pricing["final_price_net"] > 0:
                    results["final_price_netto"] = enhanced_pricing["final_price_net"]
                    results["final_price_brutto"] = enhanced_pricing["final_price_gross"]

    except Exception as e:
        print(
            f"Warning: Could not update enhanced pricing in calculation results: {e}")


def get_pricing_cache_info() -> dict[str, Any]:
    """Get information about current pricing cache status - for debugging and monitoring

    Returns:
        Dictionary with cache status information
    """
    try:
        import streamlit as st
        if not hasattr(
                st,
                "session_state") or not hasattr(
                st.session_state,
                'get'):
            return {"cache_available": False, "reason": "No session state"}

        enhanced_pricing = st.session_state.get('enhanced_pricing', {})

        cache_info = {
            "cache_available": True,
            "cached_systems": list(enhanced_pricing.keys()),
            "cache_details": {}
        }

        for system_type, pricing_data in enhanced_pricing.items():
            cache_info["cache_details"][system_type] = {
                "calculation_timestamp": pricing_data.get("calculation_timestamp"),
                "component_count": len(pricing_data.get("components", [])),
                "final_price_net": pricing_data.get("final_price_net", 0.0),
                "dynamic_keys_count": len(pricing_data.get("dynamic_keys", {})),
                # First 8 chars
                "cache_key": pricing_data.get("cache_key", "")[:8] + "..."
            }

        return cache_info

    except Exception as e:
        return {"cache_available": False, "reason": f"Error: {e}"}


def calculate_enhanced_pricing(
    components: list[dict[str, Any]],
    system_type: str = "pv",
    vat_rate: float = 19.0,
    use_cache: bool = True
) -> dict[str, Any] | None:
    """Calculate pricing using the enhanced pricing system

    Args:
        components: List of component dictionaries with product info and quantities
        system_type: Type of system ("pv", "heatpump", "combined")
        vat_rate: VAT rate in percent
        use_cache: Whether to use cached results if available

    Returns:
        Enhanced pricing calculation result or None if calculation fails
    """
    try:
        # Prepare calculation data
        modifications = _pricing_session_manager.get_pricing_modifications_from_session()

        calculation_data = {
            'components': components,
            'modifications': modifications,
            'vat_rate': vat_rate
        }

        # Check cache first if enabled
        if use_cache:
            cached_result = _pricing_session_manager.get_cached_pricing(
                calculation_data, system_type)
            if cached_result:
                return cached_result

        # Update session state with new calculation
        success = _pricing_session_manager.update_pricing_in_session_state(
            calculation_data, system_type)

        if success:
            # Return the updated pricing data
            import streamlit as st
            if hasattr(st, "session_state"):
                enhanced_pricing = st.session_state.get('enhanced_pricing', {})
                return enhanced_pricing.get(system_type)

        return None

    except Exception as e:
        print(f"Error in enhanced pricing calculation: {e}")
        return None


def invalidate_pricing_cache(system_type: str | None = None) -> None:
    """Invalidate pricing cache - call when component selection or pricing parameters change

    Args:
        system_type: System type to invalidate, or None for all systems
    """
    _pricing_session_manager.invalidate_pricing_cache(system_type)


def get_enhanced_pricing_from_session(
        system_type: str = "pv") -> dict[str, Any] | None:
    """Get enhanced pricing data from session state

    Args:
        system_type: Type of system ("pv", "heatpump", "combined")

    Returns:
        Enhanced pricing data or None if not available
    """
    try:
        import streamlit as st
        if not hasattr(
                st,
                "session_state") or not hasattr(
                st.session_state,
                'get'):
            return None

        enhanced_pricing = st.session_state.get('enhanced_pricing', {})
        return enhanced_pricing.get(system_type)

    except Exception as e:
        print(f"Error getting enhanced pricing from session: {e}")
        return None


def update_pricing_on_component_change(components: list[dict[str, Any]],
                                       system_type: str = "pv") -> bool:
    """Update pricing when component selection changes - for real-time updates

    Args:
        components: Updated component list
        system_type: Type of system ("pv", "heatpump", "combined")

    Returns:
        True if update was successful, False otherwise
    """
    try:
        # Invalidate cache first to force recalculation
        invalidate_pricing_cache(system_type)

        # Calculate new pricing
        result = calculate_enhanced_pricing(
            components, system_type, use_cache=False)

        return result is not None

    except Exception as e:
        print(f"Error updating pricing on component change: {e}")
        return False


def _calculate_final_price_with_correct_formula(
    base_matrix_price: float,
    additional_costs: float,
    pricing_modifications: dict[str, float],
    vat_rate_percent: float,
    one_time_bonus: float = 0.0,
    debug_mode: bool = False
) -> dict[str, float]:
    """
    Berechnet den finalen Preis mit der korrekten Formel: Matrixpreis + Zubehör - Rabatte.

    Args:
        base_matrix_price: Basis-Matrixpreis (netto)
        additional_costs: Zusätzliche Kosten (Zubehör, etc.)
        pricing_modifications: Dictionary mit Preismodifikationen
        vat_rate_percent: MwSt-Satz in Prozent
        one_time_bonus: Einmaliger Bonus (wird abgezogen)
        debug_mode: Ob Debug-Ausgaben aktiviert sind

    Returns:
        Dictionary mit finalen Preisberechnungen
    """

    # Schritt 1: Basis-Nettobetrag = Matrixpreis + Zusatzkosten
    subtotal_netto = base_matrix_price + additional_costs

    # Schritt 2: Einmaliger Bonus abziehen
    subtotal_after_bonus = subtotal_netto - one_time_bonus

    # Schritt 3: Preismodifikationen anwenden
    final_price_netto = subtotal_after_bonus

    # Prozentuale Rabatte und Aufschläge
    discount_percent = pricing_modifications.get("discount_percent", 0.0)
    surcharge_percent = pricing_modifications.get("surcharge_percent", 0.0)

    if discount_percent > 0:
        final_price_netto *= (1 - discount_percent / 100.0)

    if surcharge_percent > 0:
        final_price_netto *= (1 + surcharge_percent / 100.0)

    # Absolute Rabatte und Zusatzkosten
    special_discount = pricing_modifications.get("special_discount", 0.0)
    additional_costs_mod = pricing_modifications.get("additional_costs", 0.0)

    final_price_netto = final_price_netto - special_discount + additional_costs_mod

    # Preis kann nicht negativ sein
    final_price_netto = max(0.0, final_price_netto)

    # Brutto-Preis berechnen
    final_price_brutto = final_price_netto * (1 + vat_rate_percent / 100.0)

    # Debug-Ausgaben
    if debug_mode:
        print("\n🔍 FINAL PRICE CALCULATION (CORRECTED FORMULA):")
        print(f"   Base matrix price: {base_matrix_price:.2f} €")
        print(f"   Additional costs (accessories): {additional_costs:.2f} €")
        print(f"   Subtotal before modifications: {subtotal_netto:.2f} €")
        print(f"   One-time bonus: -{one_time_bonus:.2f} €")
        print(f"   Subtotal after bonus: {subtotal_after_bonus:.2f} €")
        print("   Pricing modifications:")
        print(f"     - Discount percent: {discount_percent}%")
        print(f"     - Surcharge percent: {surcharge_percent}%")
        print(f"     - Special discount: {special_discount} €")
        print(f"     - Additional costs: {additional_costs_mod} €")
        print(f"   FINAL PRICE (netto): {final_price_netto:.2f} €")
        print(f"   FINAL PRICE (brutto): {final_price_brutto:.2f} €")

    # Berechne Gesamtrabatte und Aufschläge für Anzeige
    total_discount_amount = (subtotal_after_bonus *
                             discount_percent / 100.0) + special_discount
    total_surcharge_amount = (
        subtotal_after_bonus * surcharge_percent / 100.0) + additional_costs_mod

    return {
        "subtotal_netto": subtotal_netto,
        "subtotal_after_bonus": subtotal_after_bonus,
        "final_price_netto": final_price_netto,
        "final_price_brutto": final_price_brutto,
        "total_discount_amount": total_discount_amount,
        "total_surcharge_amount": total_surcharge_amount,
        "pricing_modifications_applied": pricing_modifications,
        "one_time_bonus_applied": one_time_bonus
    }

# Alte Parser-Funktionen für Preis-Matrix wurden entfernt.
# Placeholder: Neue Matrix-Engine wird separat implementiert.


class AdvancedCalculationsIntegrator:
    """Integriert erweiterte Berechnungen in Dashboard und PDF"""

    def __init__(self):
        # Liste der erweiterten Berechnungen aus calculations.py
        self.advanced_calculations = {
            "degradation_analysis": {
                "name": "Degradationsanalyse",
                "description": "Berechnet die Leistungsabnahme über 25 Jahre",
                "category": "technical",
            },
            "shading_analysis": {
                "name": "Verschattungsanalyse",
                "description": "Detaillierte Verschattungsberechnung",
                "category": "technical",
            },
            "grid_interaction": {
                "name": "Netzinteraktion",
                "description": "Analyse der Netzeinspeisung und -bezug",
                "category": "economic",
            },
            "battery_cycles": {
                "name": "Batteriezyklen",
                "description": "Berechnung der Ladezyklen und Lebensdauer",
                "category": "storage",
            },
            "weather_impact": {
                "name": "Wettereinfluss",
                "description": "Einfluss von Wetterbedingungen auf Ertrag",
                "category": "environmental",
            },
            "maintenance_schedule": {
                "name": "Wartungsplan",
                "description": "Optimaler Wartungsplan und Kosten",
                "category": "operational",
            },
            "carbon_footprint": {
                "name": "CO2-Bilanz",
                "description": "Detaillierte CO2-Einsparungsberechnung",
                "category": "environmental",
            },
            "peak_shaving": {
                "name": "Lastspitzenkappung",
                "description": "Potenzial zur Reduzierung von Lastspitzen",
                "category": "optimization",
            },
            "dynamic_pricing": {
                "name": "Dynamische Preise",
                "description": "Optimierung bei variablen Strompreisen",
                "category": "economic",
            },
            "energy_independence": {
                "name": "Energieunabhängigkeit",
                "description": "Analyse der Autarkie über Zeit",
                "category": "strategic",
            },
            "recycling_potential": {
                "name": "Recycling-Potenzial",
                "description": "Analyse des Recyclingpotenzials der Anlagenteile",
                "category": "environmental",
            },
        }

        # Berechnungsfunktionen mapping
        self.calculation_functions = {
            "degradation_analysis": self._calculate_degradation,
            "shading_analysis": self._calculate_shading,
            "grid_interaction": self._calculate_grid_interaction,
            "battery_cycles": self._calculate_battery_cycles,
            "weather_impact": self._calculate_weather_impact,
            "maintenance_schedule": self._calculate_maintenance,
            "carbon_footprint": self._calculate_carbon_footprint,
            "peak_shaving": self._calculate_peak_shaving,
            "dynamic_pricing": self._calculate_dynamic_pricing,
            "energy_independence": self._calculate_energy_independence,
            "recycling_potential": self.calculate_recycling_potential,
        }

    def _calculate_degradation(
            self, base_data: dict[str, Any]) -> dict[str, Any]:
        """Berechnet die Degradation über 25 Jahre"""
        years = 25
        initial_power = base_data.get("anlage_kwp", 10) * 1000  # in Watt
        degradation_rate = 0.005  # 0.5% pro Jahr

        power_over_time = []
        energy_loss = []

        for year in range(years + 1):
            current_power = initial_power * (1 - degradation_rate) ** year
            power_over_time.append(current_power)

            if year > 0:
                annual_loss = (initial_power - current_power) * 1700  # kWh
                energy_loss.append(annual_loss)

        return {
            "years": list(range(years + 1)),
            "power_kw": [p / 1000 for p in power_over_time],
            "total_energy_loss_kwh": sum(energy_loss),
            "final_performance_percent": (power_over_time[-1] / initial_power) * 100,
            "average_degradation_rate": degradation_rate * 100,
        }

    def _calculate_shading(self, base_data: dict[str, Any]) -> dict[str, Any]:
        """Berechnet detaillierte Verschattungsverluste"""
        # Beispielhafte Verschattungsanalyse
        hours_of_day = list(range(6, 20))  # 6:00 bis 19:00
        months = [
            "Jan",
            "Feb",
            "Mär",
            "Apr",
            "Mai",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Okt",
            "Nov",
            "Dez",
        ]

        shading_matrix = []
        for month_idx in range(12):
            month_shading = []
            for hour in hours_of_day:
                # Simulierte Verschattung basierend auf Sonnenstand
                base_shading = 0.1  # 10% Basis-Verschattung

                # Morgens und abends mehr Verschattung
                if hour < 9 or hour > 17:
                    base_shading += 0.2

                # Winter mehr Verschattung
                if month_idx in [0, 1, 10, 11]:
                    base_shading += 0.15

                month_shading.append(min(base_shading, 0.9))

            shading_matrix.append(month_shading)

        # Jährlicher Verschattungsverlust
        avg_shading = np.mean(shading_matrix)
        annual_loss_kwh = base_data.get(
            "annual_pv_production_kwh", 10000) * avg_shading

        return {
            "hours": hours_of_day,
            "months": months,
            "shading_matrix": shading_matrix,
            "average_shading_percent": avg_shading * 100,
            "annual_shading_loss_kwh": annual_loss_kwh,
            "optimal_hours": [h for h in hours_of_day if 10 <= h <= 15],
        }

    def _calculate_grid_interaction(
            self, base_data: dict[str, Any]) -> dict[str, Any]:
        """Analysiert die Netzinteraktion"""
        monthly_production = base_data.get("monthly_production", [500] * 12)
        monthly_consumption = base_data.get("monthly_consumption", [400] * 12)

        grid_feed_in = []
        grid_purchase = []
        self_consumption = []

        for prod, cons in zip(
                monthly_production, monthly_consumption, strict=False):
            if prod > cons:
                grid_feed_in.append(prod - cons)
                grid_purchase.append(0)
                self_consumption.append(cons)
            else:
                grid_feed_in.append(0)
                grid_purchase.append(cons - prod)
                self_consumption.append(prod)

        return {
            "months": [
                "Jan",
                "Feb",
                "Mär",
                "Apr",
                "Mai",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Okt",
                "Nov",
                "Dez",
            ],
            "grid_feed_in_kwh": grid_feed_in,
            "grid_purchase_kwh": grid_purchase,
            "self_consumption_kwh": self_consumption,
            "total_feed_in_kwh": sum(grid_feed_in),
            "total_purchase_kwh": sum(grid_purchase),
            "self_consumption_rate": sum(self_consumption)
            / sum(monthly_consumption)
            * 100,
            "grid_independence_rate": (
                1 - sum(grid_purchase) / sum(monthly_consumption)
            )
            * 100,
        }

    def _calculate_battery_cycles(
            self, base_data: dict[str, Any]) -> dict[str, Any]:
        """Berechnet Batteriezyklen und Lebensdauer"""
        battery_capacity = base_data.get("battery_capacity_kwh", 10)
        daily_cycles = 1.2  # Durchschnittliche Zyklen pro Tag

        annual_cycles = daily_cycles * 365
        cycle_life = 6000  # Typische Zyklenlebensdauer

        expected_lifetime_years = cycle_life / annual_cycles

        # Degradation über Zeit
        years = list(range(int(expected_lifetime_years) + 1))
        capacity_over_time = []

        for year in years:
            # 80% Kapazität nach Zyklenlebensdauer
            remaining_capacity = 100 - (20 * year / expected_lifetime_years)
            capacity_over_time.append(max(80, remaining_capacity))

        return {
            "battery_capacity_kwh": battery_capacity,
            "daily_cycles": daily_cycles,
            "annual_cycles": annual_cycles,
            "expected_lifetime_years": expected_lifetime_years,
            "years": years,
            "capacity_percent": capacity_over_time,
            "replacement_year": int(expected_lifetime_years),
            "total_energy_throughput_mwh": battery_capacity *
            cycle_life /
            1000,
        }

    def _calculate_weather_impact(
            self, base_data: dict[str, Any]) -> dict[str, Any]:
        """Berechnet den Einfluss von Wetterbedingungen"""
        # Wetter-Faktoren für verschiedene Bedingungen
        weather_factors = {
            "sunny": 1.0,
            "partly_cloudy": 0.75,
            "cloudy": 0.4,
            "rainy": 0.25,
            "snowy": 0.1,
        }

        # Typische Wetterverteilung (Tage pro Jahr)
        weather_distribution = {
            "sunny": 90,
            "partly_cloudy": 120,
            "cloudy": 80,
            "rainy": 60,
            "snowy": 15,
        }

        # Berechnung des gewichteten Durchschnitts
        total_days = sum(weather_distribution.values())
        weighted_factor = (
            sum(
                days * weather_factors[weather]
                for weather, days in weather_distribution.items()
            )
            / total_days
        )

        # Einfluss auf Jahresertrag
        ideal_production = base_data.get("annual_pv_production_kwh", 10000)
        actual_production = ideal_production * weighted_factor

        return {
            "weather_types": list(weather_factors.keys()),
            "production_factors": list(weather_factors.values()),
            "days_per_year": list(weather_distribution.values()),
            "weighted_average_factor": weighted_factor,
            "ideal_production_kwh": ideal_production,
            "weather_adjusted_production_kwh": actual_production,
            "production_loss_kwh": ideal_production - actual_production,
            "efficiency_percent": weighted_factor * 100,
        }

    def _calculate_maintenance(
            self, base_data: dict[str, Any]) -> dict[str, Any]:
        """Erstellt einen Wartungsplan mit Kosten"""
        system_size_kwp = base_data.get("anlage_kwp", 10)

        # Wartungsaktivitäten
        maintenance_tasks = {
            "visual_inspection": {
                "interval_months": 6,
                "cost_per_kwp": 5,
                "duration_hours": 1,
            },
            "cleaning": {
                "interval_months": 12,
                "cost_per_kwp": 10,
                "duration_hours": 2,
            },
            "electrical_check": {
                "interval_months": 12,
                "cost_per_kwp": 15,
                "duration_hours": 3,
            },
            "inverter_service": {
                "interval_months": 24,
                "cost_per_kwp": 20,
                "duration_hours": 4,
            },
            "full_system_check": {
                "interval_months": 60,
                "cost_per_kwp": 50,
                "duration_hours": 8,
            },
        }

        # 10-Jahres-Plan erstellen
        maintenance_schedule = []
        total_cost = 0

        for month in range(1, 121):  # 10 Jahre
            for task, details in maintenance_tasks.items():
                if month % details["interval_months"] == 0:
                    cost = details["cost_per_kwp"] * system_size_kwp
                    maintenance_schedule.append(
                        {
                            "month": month,
                            "year": (month - 1) // 12 + 1,
                            "task": task,
                            "cost": cost,
                            "duration_hours": details["duration_hours"],
                        }
                    )
                    total_cost += cost

        # Jahreskosten
        annual_costs = {}
        for item in maintenance_schedule:
            year = item["year"]
            if year not in annual_costs:
                annual_costs[year] = 0
            annual_costs[year] += item["cost"]

        return {
            "schedule": maintenance_schedule,
            "total_cost_10_years": total_cost,
            "average_annual_cost": total_cost / 10,
            "annual_costs": annual_costs,
            "cost_per_kwp_per_year": (total_cost / 10) / system_size_kwp,
        }

    def _calculate_carbon_footprint(
            self, base_data: dict[str, Any]) -> dict[str, Any]:
        """Berechnet detaillierte CO2-Bilanz"""
        annual_production = base_data.get("annual_pv_production_kwh", 10000)

        # CO2-Faktoren
        grid_co2_per_kwh = 0.4  # kg CO2/kWh für Strommix
        pv_production_co2 = 40  # g CO2/kWh für PV-Produktion

        # Herstellung
        system_size_kwp = base_data.get("anlage_kwp", 10)
        manufacturing_co2 = system_size_kwp * 1500  # kg CO2 pro kWp

        # Jährliche Einsparung
        annual_co2_saved = annual_production * grid_co2_per_kwh
        annual_co2_pv = annual_production * pv_production_co2 / 1000
        net_annual_saving = annual_co2_saved - annual_co2_pv

        # Amortisation der Herstellungs-CO2
        co2_payback_years = manufacturing_co2 / net_annual_saving

        # 25-Jahres-Bilanz
        lifetime_co2_saved = net_annual_saving * 25 - manufacturing_co2

        return {
            "manufacturing_co2_kg": manufacturing_co2,
            "annual_grid_co2_saved_kg": annual_co2_saved,
            "annual_pv_co2_kg": annual_co2_pv,
            "net_annual_co2_saved_kg": net_annual_saving,
            "co2_payback_years": co2_payback_years,
            "lifetime_co2_saved_tons": lifetime_co2_saved / 1000,
            "equivalent_trees_planted": int(
                lifetime_co2_saved / 20
            ),  # 20kg CO2/Baum/Jahr
            # 120g CO2/km
            "equivalent_car_km_saved": int(lifetime_co2_saved / 0.12),
        }

    def _calculate_peak_shaving(
            self, base_data: dict[str, Any]) -> dict[str, Any]:
        """Berechnet Lastspitzenkappung"""
        # Beispielhafte Lastprofile
        hours = list(range(24))
        base_load = [
            0.3,
            0.25,
            0.2,
            0.2,
            0.25,
            0.4,
            0.7,
            0.9,
            1.0,
            0.9,
            0.8,
            0.7,
            0.8,
            0.7,
            0.6,
            0.7,
            0.9,
            1.2,
            1.0,
            0.8,
            0.6,
            0.5,
            0.4,
            0.35,
        ]

        peak_power_kw = base_data.get("peak_power_kw", 5)
        battery_power_kw = base_data.get("battery_power_kw", 3)

        # Lastspitzen identifizieren
        peak_threshold = 0.8  # 80% der Maximallast
        peaks = [load for load in base_load if load > peak_threshold]

        # Potenzielle Einsparung
        shaved_load = []
        for load in base_load:
            if load > peak_threshold:
                shaved = min(
                    load - peak_threshold,
                    battery_power_kw / peak_power_kw)
                shaved_load.append(load - shaved)
            else:
                shaved_load.append(load)

        # Kostenersparnis (Leistungspreis)
        power_price_per_kw = 100  # EUR/kW/Jahr
        peak_reduction_kw = peak_power_kw * (max(base_load) - max(shaved_load))
        annual_savings = peak_reduction_kw * power_price_per_kw

        return {
            "hours": hours,
            "original_load_profile": base_load,
            "shaved_load_profile": shaved_load,
            "peak_reduction_kw": peak_reduction_kw,
            "peak_reduction_percent": (
                1 - max(shaved_load) / max(base_load)) * 100,
            "annual_cost_savings_eur": annual_savings,
            "battery_utilization_hours": len(peaks),
        }

    def _calculate_dynamic_pricing(
            self, base_data: dict[str, Any]) -> dict[str, Any]:
        """Optimierung bei dynamischen Strompreisen"""
        # Beispielhafte Strompreise über 24h
        hours = list(range(24))
        base_price = 0.30  # EUR/kWh

        # Preiskurve (niedrig nachts, hoch tagsüber)
        price_factors = []
        for hour in hours:
            if 0 <= hour < 6:
                factor = 0.6
            elif 6 <= hour < 9:
                factor = 1.2
            elif 9 <= hour < 17:
                factor = 0.9
            elif 17 <= hour < 21:
                factor = 1.4
            else:
                factor = 0.8
            price_factors.append(factor)

        hourly_prices = [base_price * factor for factor in price_factors]

        # Optimierungspotenzial mit Batterie
        battery_capacity = base_data.get("battery_capacity_kwh", 10)

        # Lade in günstigen Zeiten, entlade in teuren Zeiten
        charge_hours = [h for h, p in enumerate(
            hourly_prices) if p < base_price * 0.8]
        discharge_hours = [
            h for h, p in enumerate(hourly_prices) if p > base_price * 1.2
        ]

        # Potenzielle Ersparnis
        avg_charge_price = np.mean([hourly_prices[h] for h in charge_hours])
        avg_discharge_price = np.mean(
            [hourly_prices[h] for h in discharge_hours])

        daily_arbitrage = (
            battery_capacity * 0.8 * (avg_discharge_price - avg_charge_price)
        )
        annual_arbitrage = daily_arbitrage * 365

        return {
            "hours": hours,
            "hourly_prices_eur": hourly_prices,
            "average_price_eur": base_price,
            "charge_hours": charge_hours,
            "discharge_hours": discharge_hours,
            "daily_arbitrage_eur": daily_arbitrage,
            "annual_arbitrage_eur": annual_arbitrage,
            "price_spread_percent": (
                (avg_discharge_price - avg_charge_price) / base_price
            )
            * 100,
        }

    def _calculate_energy_independence(
        self, base_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Analysiert Energieunabhängigkeit über Zeit"""
        years = list(range(1, 26))  # 25 Jahre

        # Basis-Parameter
        initial_self_consumption = base_data.get(
            "self_supply_rate_percent", 30)
        battery_capacity = base_data.get("battery_capacity_kwh", 0)

        # Entwicklung über Zeit
        self_consumption_rates = []
        grid_dependency = []

        for year in years:
            # Mit Batterie steigt Eigenverbrauch
            if battery_capacity > 0:
                # Annahme: 2% Steigerung pro Jahr bis max 85%
                rate = min(85, initial_self_consumption + year * 2)
            else:
                # Ohne Batterie langsamer Anstieg
                rate = min(50, initial_self_consumption + year * 0.5)

            self_consumption_rates.append(rate)
            grid_dependency.append(100 - rate)

        # Wirtschaftliche Unabhängigkeit
        electricity_price_increase = 0.03  # 3% pro Jahr
        cost_without_pv = []
        cost_with_pv = []

        annual_consumption = base_data.get("annual_consumption_kwh", 5000)
        base_price = 0.30  # EUR/kWh

        for year in years:
            price = base_price * (1 + electricity_price_increase) ** year
            cost_without = annual_consumption * price
            cost_with = (
                annual_consumption
                * (1 - self_consumption_rates[year - 1] / 100)
                * price
            )

            cost_without_pv.append(cost_without)
            cost_with_pv.append(cost_with)

        return {
            "years": years,
            "self_consumption_rates": self_consumption_rates,
            "grid_dependency_rates": grid_dependency,
            "annual_costs_without_pv": cost_without_pv,
            "annual_costs_with_pv": cost_with_pv,
            "cumulative_savings": np.cumsum(
                np.array(cost_without_pv) - np.array(cost_with_pv)
            ).tolist(),
            "average_independence_rate": np.mean(self_consumption_rates),
            "final_independence_rate": self_consumption_rates[-1],
        }

    def calculate_shading_analysis(
        self, project_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Stub für Verschattungsanalyse - noch nicht implementiert"""
        # Simulierte Werte für Testing
        annual_production = project_data.get(
            "expected_annual_production", 10000)
        shading_loss_percent = 5.2
        energy_loss_kwh = annual_production * (shading_loss_percent / 100)

        return {
            "shading_matrix": [
                [10, 15, 20] * 4 for _ in range(12)
            ],  # Dummy 12x12 Matrix
            "annual_shading_loss": shading_loss_percent,
            "energy_loss_kwh": energy_loss_kwh,  # Fehlender Key hinzugefügt
            "seasonal_variations": {"winter": 8.1, "summer": 3.4},
            "worst_case_month": "Dezember",
            "worst_month": "Dezember",  # Alias für worst_case_month
            "worst_month_loss": 8.1,  # Verlust im schlechtesten Monat
            "optimization_potential": energy_loss_kwh
            * 0.3,  # 30% des Verlustes könnte optimiert werden
        }

    def calculate_subsidy_scenarios(
        self, calc_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Stub für Förderszenarien - noch nicht implementiert"""
        return {
            "scenarios": {
                "Jahr": list(range(1, 21)),
                "Ohne Förderung": [i * 1000 for i in range(1, 21)],
                "Mit KfW-Förderung": [i * 1200 for i in range(1, 21)],
                "Mit regionaler Förderung": [i * 1100 for i in range(1, 21)],
            },
            "comparison": [
                {
                    "Szenario": "Ohne Förderung",
                    "NPV": 25000.0,
                    "IRR": 6.2,
                    "Amortisation": 12.5,
                    "Förderung": 0.0,
                },
                {
                    "Szenario": "Mit KfW-Förderung",
                    "NPV": 35000.0,
                    "IRR": 8.1,
                    "Amortisation": 10.2,
                    "Förderung": 5000.0,
                },
                {
                    "Szenario": "Mit regionaler Förderung",
                    "NPV": 30000.0,
                    "IRR": 7.3,
                    "Amortisation": 11.1,
                    "Förderung": 2500.0,
                },
            ],
        }

    def generate_optimization_suggestions(
        self, calc_results: dict[str, Any], project_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Stub für Optimierungsvorschläge - noch nicht implementiert"""
        return {
            "optimization_potentials": [
                {
                    "category": "Technisch",
                    "description": "Optimale Modulausrichtung",
                    "implementation_effort": 30,
                    "benefit_potential": 800,
                    "roi_improvement": 1.2,
                    "cost_estimate": 500,
                },
                {
                    "category": "Wirtschaftlich",
                    "description": "Batteriespeicher optimieren",
                    "implementation_effort": 70,
                    "benefit_potential": 1200,
                    "roi_improvement": 2.1,
                    "cost_estimate": 3000,
                },
            ],
            "top_recommendations": [
                {
                    "priority": 1,
                    "title": "Modulausrichtung optimieren",
                    "description": "Anpassung der Neigung für höhere Erträge",
                    "annual_benefit": 800,  # Key korrigiert von 'potential_benefit'
                    "investment": 500,  # Key korrigiert von 'implementation_cost'
                    # Key korrigiert von 'payback_time' (Jahre statt Monate)
                    "payback": 0.6,
                    "roi_improvement": 12.5,  # Prozent ROI-Verbesserung
                    "difficulty": "Einfach",  # Neuer Key für Schwierigkeitsgrad
                },
                {
                    "priority": 2,
                    "title": "Batteriespeicher erweitern",
                    "description": "Erhöhung der Speicherkapazität für bessere Eigennutzung",
                    "annual_benefit": 1200,
                    "investment": 3000,
                    "payback": 2.5,
                    "roi_improvement": 8.3,
                    "difficulty": "Mittel",  # Neuer Key für Schwierigkeitsgrad
                },
                {
                    "priority": 3,
                    "title": "Optimiertes Energiemanagement",
                    "description": "Intelligente Steuerung für Verbrauchsoptimierung",
                    "annual_benefit": 600,
                    "investment": 1500,
                    "payback": 2.5,
                    "roi_improvement": 5.2,
                    "difficulty": "Komplex",  # Neuer Key für Schwierigkeitsgrad
                },
            ],
            "system_optimization": {
                "optimal_tilt": 35,
                "optimal_azimuth": 0,
                "optimal_battery_size": 8.5,
                "optimal_dc_ac_ratio": 1.25,
            },
        }

    def calculate_detailed_co2_analysis(
        self, calc_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Stub für detaillierte CO2-Analyse - noch nicht implementiert"""
        annual_production = calc_results.get("annual_pv_production_kwh", 8000)
        years = list(range(1, 26))

        return {
            "years": years,
            "cumulative_savings": [
                i * annual_production * 0.474 / 1000 for i in years
            ],  # t CO2
            "production_emissions": 2.5,  # t CO2 für Herstellung
            "carbon_payback_time": 2.3,
            "total_co2_savings": annual_production * 25 * 0.474 / 1000,
            "tree_equivalent": int(
                annual_production * 25 * 0.474 / 22
            ),  # 22kg CO2 pro Baum/Jahr
            "car_km_equivalent": int(
                annual_production * 25 * 0.474 / 0.12
            ),  # 120g CO2/km
            "primary_energy_saved": annual_production * 25 * 2.5,  # kWh
            "water_saved": annual_production * 25 * 1.2,  # Liter
            "so2_avoided": annual_production * 25 * 0.474 * 0.001,  # kg
            "nox_avoided": annual_production * 25 * 0.474 * 0.0008,  # kg
            "particulates_avoided": annual_production * 25 * 0.474 * 0.00005,  # kg
        }

    def calculate_recycling_potential(
        self, calc_results: dict[str, Any], project_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Stub für Recycling-Potenzial - noch nicht implementiert"""
        system_kwp = calc_results.get("anlage_kwp", 10.0)

        # Beispiel-Materialzusammensetzung basierend auf Anlagengröße
        silicon_weight = system_kwp * 15  # kg Silizium pro kWp
        aluminum_weight = system_kwp * 25  # kg Aluminium pro kWp
        glass_weight = system_kwp * 50  # kg Glas pro kWp
        plastic_weight = system_kwp * 8  # kg Kunststoff pro kWp

        return {
            "material_composition": [
                {
                    "material": "Silizium",
                    "weight_kg": silicon_weight,
                    "recyclable": True,
                    "value_per_kg": 15.0,
                },
                {
                    "material": "Aluminium",
                    "weight_kg": aluminum_weight,
                    "recyclable": True,
                    "value_per_kg": 2.5,
                },
                {
                    "material": "Glas",
                    "weight_kg": glass_weight,
                    "recyclable": True,
                    "value_per_kg": 0.1,
                },
                {
                    "material": "Kunststoff",
                    "weight_kg": plastic_weight,
                    "recyclable": False,
                    "value_per_kg": 0.0,
                },
            ],
            "recycling_rate": 85.0,  # Prozent recycelbar
            "material_value": (
                silicon_weight * 15.0 + aluminum_weight * 2.5 + glass_weight * 0.1
            ),
            "co2_savings_recycling": system_kwp
            * 0.5,  # Tonnen CO2-Einsparung durch Recycling
            "end_of_life_cost": system_kwp * 50,  # Kosten für Entsorgung
            "recycling_revenue": system_kwp * 75,  # Erlös aus Recycling
        }

    def calculate_lcoe_advanced(
            self, lcoe_params: dict[str, Any]) -> dict[str, Any]:
        """LCOE-Berechnung (Levelized Cost of Energy)"""
        investment = lcoe_params.get("investment", 20000)
        annual_production = lcoe_params.get("annual_production", 10000)
        lifetime = lcoe_params.get("lifetime", 25)
        discount_rate = lcoe_params.get("discount_rate", 0.04)
        opex_rate = lcoe_params.get("opex_rate", 0.01)
        degradation_rate = lcoe_params.get("degradation_rate", 0.005)

        # Einfache LCOE
        lcoe_simple = investment / (annual_production * lifetime)

        # Diskontierte LCOE mit Degradation
        total_discounted_energy = 0
        total_discounted_costs = investment
        yearly_lcoe = []

        for year in range(1, lifetime + 1):
            # Energieproduktion mit Degradation
            yearly_production = annual_production * \
                (1 - degradation_rate) ** (year - 1)
            discounted_production = yearly_production / \
                (1 + discount_rate) ** year
            total_discounted_energy += discounted_production

            # Jährliche Betriebskosten
            yearly_opex = investment * opex_rate
            discounted_opex = yearly_opex / (1 + discount_rate) ** year
            total_discounted_costs += discounted_opex

            # LCOE für dieses Jahr
            year_lcoe = (
                total_discounted_costs / total_discounted_energy
                if total_discounted_energy > 0
                else 0
            )
            yearly_lcoe.append(year_lcoe)

        lcoe_discounted = (
            total_discounted_costs / total_discounted_energy
            if total_discounted_energy > 0
            else 0
        )

        # Vergleich mit Netzstrom
        grid_price = 0.32  # EUR/kWh
        grid_comparison = lcoe_discounted / grid_price if grid_price > 0 else 0
        savings_potential = grid_price - lcoe_discounted

        return {
            "lcoe_simple": lcoe_simple,
            "lcoe_discounted": lcoe_discounted,
            "yearly_lcoe": yearly_lcoe,
            "grid_comparison": grid_comparison,
            "savings_potential": max(0, savings_potential),
        }

    def calculate_npv_sensitivity(
        self, calc_results: dict[str, Any], discount_rate: float
    ) -> float:
        """NPV-Sensitivitätsanalyse"""
        investment = calc_results.get("total_investment_netto", 20000)
        annual_benefit = calc_results.get(
            "annual_financial_benefit_year1", 1500)
        lifetime = 25

        # NPV berechnen
        npv = -investment
        for year in range(1, lifetime + 1):
            discounted_benefit = annual_benefit / (1 + discount_rate) ** year
            npv += discounted_benefit

        return npv

    def calculate_irr_advanced(
            self, calc_results: dict[str, Any]) -> dict[str, Any]:
        """Erweiterte IRR-Berechnung"""
        investment = calc_results.get("total_investment_netto", 20000)
        annual_benefit = calc_results.get(
            "annual_financial_benefit_year1", 1500)
        lifetime = 25

        # Cash Flow generieren
        cash_flows = [-investment] + [annual_benefit] * lifetime

        # IRR iterativ berechnen
        irr = 0.0
        try:
            # Vereinfachte IRR-Berechnung
            for rate in np.arange(0.01, 0.20, 0.001):
                npv = sum(cf / (1 + rate) ** i for i,
                          cf in enumerate(cash_flows))
                if abs(npv) < 100:  # Nahe null
                    irr = rate
                    break
        except BaseException:
            irr = 0.05  # Fallback

        # MIRR (vereinfacht)
        finance_rate = 0.04
        reinvest_rate = 0.03
        mirr = ((annual_benefit * lifetime / investment) ** (1 / lifetime)) - 1

        # Profitability Index
        pi = (sum(annual_benefit / (1 + 0.04) **
                  year for year in range(1, lifetime + 1)) / investment)

        return {
            "irr": irr * 100,
            "mirr": mirr * 100,
            "profitability_index": pi}

    def calculate_detailed_energy_flows(
        self, calc_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Detaillierte Energieflüsse für Sankey-Diagramm"""
        pv_production = calc_results.get("annual_pv_production_kwh", 10000)
        total_consumption = calc_results.get("total_consumption_kwh_yr", 4000)
        direct_consumption = calc_results.get(
            "annual_direct_self_consumption_kwh", 3000
        )
        battery_charge = calc_results.get("annual_battery_charge_kwh", 1500)
        battery_discharge = calc_results.get(
            "annual_battery_discharge_kwh", 1200)
        grid_feed_in = calc_results.get("annual_feed_in_kwh", 5500)
        grid_purchase = calc_results.get("annual_grid_purchase_kwh", 1000)

        # Sankey-Daten
        # PV -> Direkt, Batterie, Netz; Batterie -> Verbrauch; Netz ->
        # Verbrauch
        sources = [0, 0, 0, 4, 5, 6, ]
        targets = [
            1,
            2,
            3,
            6,
            6,
            6,
        ]  # -> Direktverbrauch, Batterieladung, Netzeinspeisung, Hausverbrauch
        values = [
            direct_consumption,
            battery_charge,
            grid_feed_in,
            battery_discharge,
            grid_purchase,
            direct_consumption,
        ]

        flow_names = [
            "PV-Erzeugung",
            "Direktverbrauch",
            "Batterieladung",
            "Netzeinspeisung",
            "Batterieentladung",
            "Netzbezug",
            "Hausverbrauch",
        ]

        flow_values = [
            pv_production,
            direct_consumption,
            battery_charge,
            grid_feed_in,
            battery_discharge,
            grid_purchase,
            total_consumption,
        ]
        flow_percentages = [
            v /
            pv_production *
            100 if pv_production > 0 else 0 for v in flow_values]

        return {
            "sources": sources,
            "targets": targets,
            "values": values,
            "colors": ["rgba(255,165,0,0.4)"] * len(values),
            "flow_names": flow_names,
            "flow_values": flow_values,
            "flow_percentages": flow_percentages,
        }

    def calculate_load_profile_analysis(
        self, calc_results: dict[str, Any], project_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Lastprofilanalyse"""
        # Typisches Tageslastprofil
        consumption_profile = [
            0.3,
            0.25,
            0.2,
            0.2,
            0.25,
            0.4,
            0.7,
            0.9,
            1.0,
            0.9,
            0.8,
            0.7,
            0.8,
            0.7,
            0.6,
            0.7,
            0.9,
            1.2,
            1.0,
            0.8,
            0.6,
            0.5,
            0.4,
            0.35,
        ]

        # PV-Erzeugungsprofil
        pv_generation_profile = [
            0,
            0,
            0,
            0,
            0,
            0,
            0.1,
            0.3,
            0.6,
            0.8,
            0.9,
            1.0,
            1.0,
            0.9,
            0.8,
            0.6,
            0.4,
            0.2,
            0.1,
            0,
            0,
            0,
            0,
            0,
        ]

        # Batterieprofil (Ladung positiv, Entladung negativ)
        battery_profile = []
        for i in range(24):
            if pv_generation_profile[i] > consumption_profile[i]:
                battery_profile.append(
                    min(0.5, pv_generation_profile[i] - consumption_profile[i])
                )
            else:
                battery_profile.append(-min(0.3,
                                            consumption_profile[i] - pv_generation_profile[i]))

        peak_load = max(consumption_profile)
        simultaneity_factor = peak_load / \
            (calc_results.get("anlage_kwp", 10) / 10)
        load_coverage = (
            sum(
                min(pv_generation_profile[i], consumption_profile[i]) for i in range(24)
            )
            / sum(consumption_profile)
            * 100
        )
        grid_relief = sum(pv_generation_profile) / \
            sum(consumption_profile) * 100

        return {
            "consumption_profile": consumption_profile,
            "pv_generation_profile": pv_generation_profile,
            "battery_profile": battery_profile,
            "peak_load": peak_load,
            "simultaneity_factor": simultaneity_factor,
            "load_coverage": min(100, load_coverage),
            "grid_relief": min(100, grid_relief),
        }

    def calculate_shading_analysis(
        self, project_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Verschattungsanalyse"""
        # Beispiel-Verschattungsmatrix (12 Monate x 13 Stunden)
        shading_matrix = []
        for month in range(12):
            month_data = []
            for hour in range(6, 19):  # 6:00 bis 18:00
                # Grundverschattung
                base_shading = 5  # 5% Grundverschattung

                # Morgens und abends mehr Verschattung
                if hour < 9 or hour > 16:
                    base_shading += 10

                # Winter mehr Verschattung
                if month in [0, 1, 10, 11]:
                    base_shading += 15

                month_data.append(min(base_shading, 50))
            shading_matrix.append(month_data)

        annual_loss = np.mean(shading_matrix)
        energy_loss_kwh = (
            project_data.get("annual_production", 10000) * annual_loss / 100
        )

        worst_month_idx = np.argmax([np.mean(month)
                                    for month in shading_matrix])
        worst_month = [
            "Jan",
            "Feb",
            "Mär",
            "Apr",
            "Mai",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Okt",
            "Nov",
            "Dez",
        ][worst_month_idx]
        worst_month_loss = np.mean(shading_matrix[worst_month_idx])

        optimization_potential = energy_loss_kwh * 0.3  # 30% durch Optimierung möglich

        return {
            "shading_matrix": shading_matrix,
            "annual_shading_loss": annual_loss,
            "energy_loss_kwh": energy_loss_kwh,
            "worst_month": worst_month,
            "worst_month_loss": worst_month_loss,
            "optimization_potential": optimization_potential,
        }

    def calculate_temperature_effects(
        self, calc_results: dict[str, Any], project_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Temperatureffekte auf die PV-Anlage"""
        # Typische Umgebungstemperaturen (monatlich)
        ambient_temps = [2, 4, 8, 13, 18, 21, 23, 22, 18, 13, 7, 3]

        # Modultemperaturen (ca. 25°C höher bei Sonnenschein)
        module_temps = [temp + 25 for temp in ambient_temps]

        # Temperaturkoeffizient für Silizium: -0.4%/°C
        temp_coefficient = -0.004
        reference_temp = 25  # °C

        power_loss_percent = []
        for temp in module_temps:
            loss = abs(temp_coefficient * (temp - reference_temp)) * 100
            power_loss_percent.append(loss)

        avg_temp_loss = np.mean(power_loss_percent)
        max_module_temp = max(module_temps)
        max_temp_delta = max_module_temp - max(ambient_temps)
        annual_energy_loss = (
            calc_results.get(
                "annual_pv_production_kwh",
                10000) * avg_temp_loss / 100)

        return {
            "ambient_temperatures": ambient_temps,
            "module_temperatures": module_temps,
            "power_loss_percent": power_loss_percent,
            "avg_temp_loss": avg_temp_loss,
            "max_module_temp": max_module_temp,
            "max_temp_delta": max_temp_delta,
            "annual_energy_loss": annual_energy_loss,
        }

    def calculate_inverter_efficiency(
        self, calc_results: dict[str, Any], project_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Wechselrichter-Effizienzanalyse"""
        # Typische Wirkungsgradkurve
        load_percentages = list(range(0, 101, 5))
        efficiency_curve = []

        for load in load_percentages:
            if load < 5:
                eff = 0
            elif load < 10:
                eff = 85 + load * 1.5
            elif load < 20:
                eff = 95 + (load - 10) * 0.3
            elif load < 100:
                eff = 98 - (load - 20) * 0.025
            else:
                eff = 96
            efficiency_curve.append(eff)

        # Häufige Betriebspunkte
        operating_points = [20, 30, 50, 70, 100]
        operating_efficiencies = [
            efficiency_curve[int(p / 5)] for p in operating_points
        ]

        # Gewichtete Wirkungsgrade (korrigierte Indizes und Gewichte)
        # Euro-Efficiency: 5%, 10%, 20%, 30%, 50%, 100%
        euro_points = [
            efficiency_curve[1],
            efficiency_curve[2],
            efficiency_curve[4],
            efficiency_curve[6],
            efficiency_curve[10],
            efficiency_curve[20],
        ]
        euro_efficiency = np.average(
            euro_points, weights=[0.03, 0.06, 0.13, 0.1, 0.48, 0.2]
        )

        # CEC-Efficiency: 10%, 20%, 30%, 50%, 75%, 100%
        cec_points = [
            efficiency_curve[2],
            efficiency_curve[4],
            efficiency_curve[6],
            efficiency_curve[10],
            efficiency_curve[15],
            efficiency_curve[20],
        ]
        cec_efficiency = np.average(
            cec_points, weights=[0.04, 0.05, 0.12, 0.21, 0.53, 0.05]
        )

        # Verluste
        annual_production = calc_results.get("annual_pv_production_kwh", 10000)
        avg_efficiency = np.mean(efficiency_curve[4:21])  # 20-100% Auslastung
        annual_losses = annual_production * (100 - avg_efficiency) / 100
        loss_percentage = 100 - avg_efficiency

        # Dimensionierung
        dc_power = calc_results.get("anlage_kwp", 10)
        ac_power = project_data.get("inverter_power_kw", dc_power * 0.9)
        sizing_factor = (dc_power / ac_power * 100) if ac_power > 0 else 110

        return {
            "efficiency_curve": efficiency_curve,
            "operating_points": operating_points,
            "operating_efficiencies": operating_efficiencies,
            "euro_efficiency": euro_efficiency,
            "cec_efficiency": cec_efficiency,
            "annual_losses": annual_losses,
            "loss_percentage": loss_percentage,
            "sizing_factor": sizing_factor,
        }

    def run_monte_carlo_simulation(
        self, calc_results: dict[str, Any], n_simulations: int, confidence_level: int
    ) -> dict[str, Any]:
        """Monte-Carlo-Simulation für Risikobewertung"""
        np.random.seed(42)  # Für reproduzierbare Ergebnisse

        base_investment = calc_results.get("total_investment_netto", 20000)
        base_annual_benefit = calc_results.get(
            "annual_financial_benefit_year1", 1500)
        lifetime = 25

        npv_distribution = []

        for _ in range(n_simulations):
            # Variationen der Parameter (normalverteilt)
            investment = np.random.normal(
                base_investment, base_investment * 0.1)
            annual_benefit = np.random.normal(
                base_annual_benefit, base_annual_benefit * 0.15
            )
            discount_rate = np.random.normal(0.04, 0.01)

            # NPV berechnen
            npv = -investment
            for year in range(1, lifetime + 1):
                npv += annual_benefit / (1 + discount_rate) ** year

            npv_distribution.append(npv)

        npv_distribution = np.array(npv_distribution)

        # Statistiken
        npv_mean = np.mean(npv_distribution)
        npv_std = np.std(npv_distribution)

        # Konfidenzintervall
        alpha = (100 - confidence_level) / 2
        npv_lower_bound = np.percentile(npv_distribution, alpha)
        npv_upper_bound = np.percentile(npv_distribution, 100 - alpha)

        # Value at Risk
        var_5 = np.percentile(npv_distribution, 5)

        # Erfolgswahrscheinlichkeit
        success_probability = (
            npv_distribution > 0).sum() / n_simulations * 100

        # Sensitivitätsanalyse (vereinfacht)
        sensitivity_analysis = [
            {"parameter": "Investitionskosten", "impact": -0.8},
            {"parameter": "Jährlicher Nutzen", "impact": 0.9},
            {"parameter": "Diskontierungsrate", "impact": -0.4},
            {"parameter": "Strompreissteigerung", "impact": 0.6},
            {"parameter": "Anlagenlebensdauer", "impact": 0.3},
        ]

        return {
            "npv_distribution": npv_distribution.tolist(),
            "npv_mean": npv_mean,
            "npv_std": npv_std,
            "npv_lower_bound": npv_lower_bound,
            "npv_upper_bound": npv_upper_bound,
            "var_5": var_5,
            "success_probability": success_probability,
            "sensitivity_analysis": sensitivity_analysis,
        }

    def calculate_subsidy_scenarios(
        self, calc_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Förderszenarien berechnen"""
        base_investment = calc_results.get("total_investment_netto", 20000)
        annual_benefit = calc_results.get(
            "annual_financial_benefit_year1", 1500)
        years = 25

        # Verschiedene Förderszenarien
        scenarios = {
            "Jahr": list(range(1, years + 1)),
            "Ohne Förderung": [],
            "KfW-Kredit (1%)": [],
            "Zuschuss 10%": [],
            "Kombination": [],
        }

        # Cashflow für jedes Szenario berechnen
        for year in range(1, years + 1):
            # Ohne Förderung
            if year == 1:
                cf_none = -base_investment + annual_benefit
            else:
                cf_none = scenarios["Ohne Förderung"][-1] + annual_benefit
            scenarios["Ohne Förderung"].append(cf_none)

            # KfW-Kredit (vereinfacht)
            if year == 1:
                cf_kfw = (
                    -base_investment * 0.2
                    + annual_benefit
                    - base_investment * 0.8 * 0.01
                )  # 80% Kredit, 1% Zinsen
            else:
                cf_kfw = (
                    scenarios["KfW-Kredit (1%)"][-1]
                    + annual_benefit
                    - base_investment * 0.8 * 0.01
                )
            scenarios["KfW-Kredit (1%)"].append(cf_kfw)

            # 10% Zuschuss
            if year == 1:
                cf_grant = -base_investment * 0.9 + annual_benefit
            else:
                cf_grant = scenarios["Zuschuss 10%"][-1] + annual_benefit
            scenarios["Zuschuss 10%"].append(cf_grant)

            # Kombination
            if year == 1:
                cf_combo = (
                    -base_investment * 0.8
                    + annual_benefit
                    - base_investment * 0.7 * 0.005
                )  # 20% Zuschuss + günstiger Kredit
            else:
                cf_combo = (
                    scenarios["Kombination"][-1]
                    + annual_benefit
                    - base_investment * 0.7 * 0.005
                )
            scenarios["Kombination"].append(cf_combo)

        # Vergleichstabelle
        comparison = [
            {
                "Szenario": "Ohne Förderung",
                "NPV": float(scenarios["Ohne Förderung"][-1]),
                "IRR": 5.2,
                "Amortisation": 13.3,
                "Förderung": 0.0,
            },
            {
                "Szenario": "KfW-Kredit",
                "NPV": float(scenarios["KfW-Kredit (1%)"][-1]),
                "IRR": 7.1,
                "Amortisation": 11.8,
                # Zinsvorteil
                "Förderung": float(base_investment * 0.8 * 0.03),
            },
            {
                "Szenario": "Zuschuss 10%",
                "NPV": float(scenarios["Zuschuss 10%"][-1]),
                "IRR": 8.4,
                "Amortisation": 10.2,
                "Förderung": float(base_investment * 0.1),
            },
            {
                "Szenario": "Kombination",
                "NPV": float(scenarios["Kombination"][-1]),
                "IRR": 9.8,
                "Amortisation": 8.9,
                "Förderung": float(
                    base_investment * 0.2 + base_investment * 0.7 * 0.025
                ),  # Zuschuss + Zinsvorteil
            },
        ]

        return {"scenarios": scenarios, "comparison": comparison}

    def calculate_detailed_co2_analysis(
        self, calc_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Detaillierte CO2-Bilanz"""
        annual_production = calc_results.get("annual_pv_production_kwh", 10000)
        system_kwp = calc_results.get("anlage_kwp", 10)
        years = 25

        # CO2-Emissionsfaktor Deutschland
        co2_factor_kg_kwh = 0.474  # kg CO2/kWh

        # Jährliche CO2-Einsparung
        annual_co2_savings = annual_production * co2_factor_kg_kwh / 1000  # Tonnen

        # Kumulative Einsparung
        years_list = list(range(1, years + 1))
        cumulative_savings = [annual_co2_savings * year for year in years_list]

        # CO2 aus Herstellung (ca. 50g CO2/Wp)
        production_emissions = system_kwp * 1000 * 0.05  # Tonnen

        # CO2-Amortisation
        carbon_payback_time = (
            production_emissions /
            annual_co2_savings if annual_co2_savings > 0 else 99)

        # Gesamte CO2-Einsparung
        total_co2_savings = annual_co2_savings * years - production_emissions

        # Äquivalente
        tree_equivalent = total_co2_savings * 47  # Ein Baum bindet ca. 22kg CO2/Jahr
        car_km_equivalent = total_co2_savings * 1000 / 0.12  # 120g CO2/km für PKW

        # Weitere Umweltaspekte
        primary_energy_saved = (
            annual_production * years * 2.8
        )  # kWh Primärenergie pro kWh Strom
        water_saved = annual_production * years * 1.2  # Liter Wasser pro kWh
        so2_avoided = total_co2_savings * 0.474 * 0.001  # kg
        nox_avoided = total_co2_savings * 0.474 * 0.0008  # kg
        particulates_avoided = total_co2_savings * 0.474 * 0.00005  # kg

        return {
            "years": years_list,
            "cumulative_savings": cumulative_savings,
            "production_emissions": production_emissions,
            "carbon_payback_time": carbon_payback_time,
            "total_co2_savings": total_co2_savings,
            "tree_equivalent": tree_equivalent,
            "car_km_equivalent": car_km_equivalent,
            "primary_energy_saved": primary_energy_saved,
            "water_saved": water_saved,
            "so2_avoided": so2_avoided,
            "nox_avoided": nox_avoided,
            "particulates_avoided": particulates_avoided,
        }

    def generate_optimization_suggestions(
        self, calc_results: dict[str, Any], project_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Optimierungsvorschläge generieren"""

        # Identifizierte Potenziale
        optimization_potentials = [{"title": "Batteriespeicher erweitern",
                                    "description": "Vergrößerung des Batteriespeichers für höheren Eigenverbrauch",
                                    "category": "Speicher",
                                    "implementation_effort": 30,
                                    "benefit_potential": 400,
                                    "roi_improvement": 1.2,
                                    "cost_estimate": 3000,
                                    },
                                   {"title": "Optimierer installieren",
                                    "description": "Leistungsoptimierer für verschattete Module",
                                    "category": "Technik",
                                    "implementation_effort": 50,
                                    "benefit_potential": 600,
                                    "roi_improvement": 2.1,
                                    "cost_estimate": 2000,
                                    },
                                   {"title": "Warmwasser-Integration",
                                    "description": "Elektrische Warmwasserbereitung für PV-Überschuss",
                                    "category": "Integration",
                                    "implementation_effort": 40,
                                    "benefit_potential": 300,
                                    "roi_improvement": 0.8,
                                    "cost_estimate": 1500,
                                    },
                                   {"title": "Smart Home System",
                                    "description": "Intelligente Laststeuerung für optimalen Verbrauch",
                                    "category": "Automatisierung",
                                    "implementation_effort": 60,
                                    "benefit_potential": 250,
                                    "roi_improvement": 0.6,
                                    "cost_estimate": 2500,
                                    },
                                   {"title": "Ladestation E-Auto",
                                    "description": "Elektroauto-Ladestation für PV-Strom",
                                    "category": "Mobilität",
                                    "implementation_effort": 35,
                                    "benefit_potential": 800,
                                    "roi_improvement": 3.2,
                                    "cost_estimate": 1200,
                                    },
                                   ]

        # Top-Empfehlungen (sortiert nach ROI-Verbesserung)
        top_recommendations = sorted(
            optimization_potentials,
            key=lambda x: x["roi_improvement"],
            reverse=True)

        # Zusätzliche Details für Top-Empfehlungen
        for rec in top_recommendations:
            rec["annual_benefit"] = rec["benefit_potential"]
            rec["investment"] = rec["cost_estimate"]
            rec["payback"] = (
                rec["investment"] / rec["annual_benefit"]
                if rec["annual_benefit"] > 0
                else 99
            )
            rec["difficulty"] = (
                "Einfach"
                if rec["implementation_effort"] < 40
                else "Mittel" if rec["implementation_effort"] < 60 else "Komplex"
            )

        # Systemoptimierung
        system_optimization = {
            "optimal_tilt": 30,  # Optimal für Deutschland
            "optimal_azimuth": 0,  # Süd
            "optimal_battery_size": 8.0,  # kWh
            "optimal_dc_ac_ratio": 1.15,
        }

        return {
            "optimization_potentials": optimization_potentials,
            "top_recommendations": top_recommendations,
            "system_optimization": system_optimization,
        }
    # (Entfernt: fehlerhafter top-level Block mit Speicherlogik-Duplikat)


def format_kpi_value(
    value: Any,
    unit: str = "",
    na_text_key: str = "data_not_available_short",
    precision: int = 2,
    texts_dict: dict[str, str] | None = None,
) -> str:
    current_texts = texts_dict if texts_dict is not None else {}
    na_text = current_texts.get(na_text_key, "N/A")

    if value is None:
        return na_text
    if isinstance(value, (float, int)) and math.isnan(value):
        return na_text  # Expliziter NaN-Check

    if isinstance(value, str):
        try:
            # Bereinigung für Zahlen im String-Format (z.B. "1.234,56" oder
            # "1,234.56")
            cleaned_value_str = value
            if "." in value and "," in value:  # Enthält sowohl Punkt als auch Komma
                # Annahme: Punkt ist Tausendertrenner, Komma ist Dezimaltrennzeichen (deutsche Notation)
                # oder Komma ist Tausendertrenner, Punkt ist
                # Dezimaltrennzeichen (englische Notation)
                if value.rfind(".") > value.rfind(
                    ","
                ):  # Punkt ist weiter rechts -> Punkt ist Dezimaltrennzeichen (englisch)
                    cleaned_value_str = value.replace(
                        ",", ""
                    )  # Entferne Kommas (Tausendertrenner)
                elif value.rfind(",") > value.rfind(
                    "."
                ):  # Komma ist weiter rechts -> Komma ist Dezimaltrennzeichen (deutsch)
                    cleaned_value_str = value.replace(
                        ".", ""
                    )  # Entferne Punkte (Tausendertrenner)
            # Ersetze verbleibendes Komma (falls deutsch) durch Punkt für
            # float()
            cleaned_value_str = cleaned_value_str.replace(",", ".")
            value_float = float(cleaned_value_str)
            value = value_float  # Konvertiere zu float für die weitere Formatierung
        except ValueError:
            return value  # Wenn Konvertierung fehlschlägt, Originalstring zurückgeben

    if isinstance(value, (int, float)):
        if math.isinf(value):
            return current_texts.get("value_infinite", "Nicht berechenbar")
        if unit == "Jahre":
            return (
                current_texts.get("years_format_string", "{val:.2f} Jahre")
                or "{val:.2f} Jahre"
            ).format(val=value)

        # Formatierung für deutsche Zahlen (Punkt als Tausendertrenner, Komma
        # als Dezimal)
        # Standard englische Formatierung
        formatted_num_en = f"{value:,.{precision}f}"
        # Konvertiere zu deutscher Notation
        formatted_num_de = (
            formatted_num_en.replace(",", "#TEMP#")
            .replace(".", ",")
            .replace("#TEMP#", ",")
        )
        return f"{formatted_num_de} {unit}".strip()
    return str(value)


def convert_orientation_to_pvgis_azimuth(orientation_text: str | None) -> int:
    """Konvertiert Text-Ausrichtung (z.B. 'Süd', 'Ost-West') in PVGIS Azimut-Werte."""
    if orientation_text is None or not str(orientation_text).strip():
        return 0  # Standardmäßig Süd

    ot_lower = str(orientation_text).lower().strip()

    # Exakte und gängige Abkürzungen zuerst
    mapping = {
        "süd": 0,
        "s": 0,
        "nord": 180,
        "n": 180,
        "ost": -90,
        "o": -90,
        "west": 90,
        "w": 90,
        "südost": -45,
        "süd-ost": -45,
        "so": -45,
        "südwest": 45,
        "süd-west": 45,
        "sw": 45,
        "nordost": -135,
        "nord-ost": -135,
        "no": -135,
        "nordwest": 135,
        "nord-west": 135,
        "nw": 135,
        # Spezifisch für O-W Ausrichtung auf Flachdach
        "flachdach (ost-west)": -90,
        "flachdach (o-w)": -90,
        "flachdach": 0,  # Standard Flachdach oft leicht nach Süden ausgerichtet oder optimal
    }
    for key, val in mapping.items():
        if key in ot_lower:
            return val
    return 0  # Fallback auf Süd


def get_pvgis_data(
    latitude: float,
    longitude: float,
    peak_power_kwp: float,
    tilt: int,
    azimuth: int,
    system_loss_percent: float = 14.0,
    texts: dict[str, str] | None = None,
    errors_list: list[str] | None = None,
    debug_mode_enabled: bool = False,
) -> dict[str, Any] | None:
    """Holt PV-Produktionsdaten von der PVGIS API."""
    local_errors: list[str] = []  # Für interne Fehler dieser Funktion
    # Sicherstellen, dass texts ein Dict ist
    texts = texts if texts is not None else {}
    effective_errors_list = errors_list if errors_list is not None else local_errors

    # Validierung der Eingabeparameter
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        actual_error_msg = (
            texts.get(
                "pvgis_invalid_lat_lon", "PVGIS: Ungültige Breiten- oder Längengrade."
            )
            or ""
        ) + f" (Lat: {latitude}, Lon: {longitude})"
        effective_errors_list.append(actual_error_msg)
        # if debug_mode_enabled: print(f"PVGIS Error: {actual_error_msg}") #
        # Bereinigt
        return None
    if peak_power_kwp <= 0:
        actual_error_msg = (
            texts.get(
                "pvgis_invalid_peak_power",
                "PVGIS: Installierte Leistung muss positiv sein.",
            )
            or ""
        )
        effective_errors_list.append(actual_error_msg)
        # if debug_mode_enabled: print(f"PVGIS Error: {actual_error_msg}") #
        # Bereinigt
        return None

    base_url = "https://re.jrc.ec.europa.eu/api/seriescalc"
    params = {
        "lat": latitude,
        "lon": longitude,
        "peakpower": peak_power_kwp,
        "loss": system_loss_percent,
        "pvtechchoice": "crystSi",
        "mountingplace": "building",
        "angle": tilt,
        "aspect": azimuth,
        "outputformat": "json",
        "browser": 0,  # Wichtig, um HTML-Antworten zu vermeiden
    }

    # if debug_mode_enabled: # Bereinigt
    #     try:
    #         prepared_request = requests.Request('GET', base_url, params=params).prepare()
    #         print(f"PVGIS Anfrage URL: {prepared_request.url}")
    #     except Exception as e_prep:
    #         print(f"PVGIS: Fehler Vorbereitung Request-URL: {e_prep}")

    error_msg_pvgis = ""  # Initialisiere Fehlermeldung

    try:
        response = requests.get(
            base_url, params=params, timeout=25
        )  # Timeout von 25 Sekunden

        # if debug_mode_enabled: print(f"PVGIS Response Status Code:
        # {response.status_code}") # Bereinigt

        response.raise_for_status()  # Löst HTTPError für 4xx/5xx Status Codes
        data = response.json()

        # if debug_mode_enabled: # Bereinigt
        #     try:
        #         print(f"PVGIS JSON Antwort (Auszug): {json.dumps(data.get('outputs', {}).get('totals', {}), indent=2, ensure_ascii=False)}")
        #     except Exception as e_json_debug:
        #         print(f"PVGIS: Fehler Ausgabe JSON-Antwort: {e_json_debug}")

        monthly_production_kwh = [
            m.get(
                "E_m",
                0.0) for m in data.get(
                "outputs",
                {}).get(
                "monthly",
                [])]
        annual_production_kwh = (
            data.get(
                "outputs",
                {}).get(
                "totals",
                {}).get(
                "fixed",
                {}).get(
                    "E_y",
                0.0))
        specific_yield_kwh_kwp_pa = (
            data.get("outputs", {})
            .get("totals", {})
            .get("fixed", {})
            .get("Yield_y", 0.0)
        )  # Korrigierter Key 'Yield_y'

        if (
            not monthly_production_kwh
            or len(monthly_production_kwh) != 12
            or (annual_production_kwh == 0.0 and peak_power_kwp > 0)
        ):
            error_msg_pvgis = (
                texts.get(
                    "pvgis_incomplete_data",
                    "PVGIS: Antwort erhalten, aber Daten scheinen unvollständig oder null.",
                ) or "")
            # if debug_mode_enabled: print(f"PVGIS: Unvollständige Daten:
            # monthly_empty={not monthly_production_kwh},
            # len_monthly={len(monthly_production_kwh)},
            # annual_zero={annual_production_kwh == 0 and peak_power_kwp > 0}")
            # # Bereinigt
            effective_errors_list.append(error_msg_pvgis)
            return None

        return {
            "monthly_production_kwh": monthly_production_kwh,
            "annual_production_kwh": annual_production_kwh,
            "specific_yield_kwh_kwp_pa": specific_yield_kwh_kwp_pa,
            "pvgis_source": data.get("meta", {}).get(
                "source", "PVGIS-TMY"
            ),  # Quelle der Daten (z.B. TMY, ERA5)
        }

    except requests.exceptions.HTTPError as e_http:
        status_code_val = (
            e_http.response.status_code if e_http.response is not None else "N/A")
        error_msg_pvgis = (
            texts.get("pvgis_http_error", "PVGIS API HTTP-Fehler") or ""
        ) + f": Status {status_code_val}"
        response_text_detail = ""
        if e_http.response is not None:  # Response-Objekt könnte None sein
            try:
                response_text_detail = e_http.response.json().get(
                    "message", e_http.response.text
                )
            except json.JSONDecodeError:
                response_text_detail = e_http.response.text
            except Exception:
                response_text_detail = "Konnte Fehlerdetails nicht extrahieren."
        # Begrenze Länge
        error_msg_pvgis += f" - Details: {response_text_detail[:200]}"
    except requests.exceptions.Timeout:
        error_msg_pvgis = (
            texts.get(
                "pvgis_timeout_error",
                "PVGIS API Zeitüberschreitung (Timeout nach 25s). Bitte Netzwerkverbindung prüfen.",
            ) or "")
    except requests.exceptions.ConnectionError as e_conn:
        error_msg_pvgis = (
            texts.get(
                "pvgis_connection_error",
                "PVGIS API Verbindungsfehler. Ist das Internet verfügbar und die API erreichbar?",
            ) or "") + f" Details: {e_conn}"
    except (
        requests.exceptions.RequestException
    ) as e_req:  # Allgemeinerer Request-Fehler
        error_msg_pvgis = (
            texts.get(
                "pvgis_request_error",
                "PVGIS API Allgemeiner Anfragefehler.") or "") + f" Details: {e_req}"
    except json.JSONDecodeError:
        error_msg_pvgis = (
            texts.get(
                "pvgis_json_decode_error",
                "PVGIS API: Fehler beim Lesen der JSON-Antwort. Möglicherweise temporäres API-Problem.",
            ) or "")
    except Exception as e_pvgis_unknown:
        error_msg_pvgis = (
            texts.get("pvgis_unknown_error", "PVGIS API: Unbekannter Fehler.") or ""
        ) + f" Details: {e_pvgis_unknown}"
        # if debug_mode_enabled: traceback.print_exc() # Bereinigt

    if error_msg_pvgis:  # Nur wenn ein Fehler aufgetreten ist
        effective_errors_list.append(error_msg_pvgis)
        # if debug_mode_enabled: print(f"PVGIS Fehler: {error_msg_pvgis}") #
        # Bereinigt
    return None


def perform_calculations(
    project_data: dict[str, Any],
    texts: dict[str, str],
    errors_list: list[str],
    simulation_duration_user: int | None = None,
    electricity_price_increase_user: float | None = None,
) -> dict[str, Any]:
    results: dict[str, Any] = {"calculation_errors": errors_list}
    customer_data = project_data.get("customer_data", {})
    project_details = project_data.get("project_details", {})
    economic_data = project_data.get("economic_data", {})

    # KORREKTUR: Definition von module_quantity an den Anfang verschieben
    # Anlagengröße (Modulanzahl wird früh benötigt)
    module_quantity = int(project_details.get("module_quantity", 0) or 0)
    # selected_module_id wird später für die Kapazität benötigt, aber die
    # Anzahl ist jetzt schon da.

    global_constants = real_load_admin_setting("global_constants")
    if not isinstance(global_constants, dict) or not global_constants:
        global_constants = Dummy_load_admin_setting_calc("global_constants")
        errors_list.append(
            texts.get(
                "warn_global_constants_fallback",
                "Warnung: Fallback für globale Konstanten verwendet.",
            )
        )

    app_debug_mode_is_enabled = global_constants.get(
        "app_debug_mode_enabled", False)
    if not isinstance(app_debug_mode_is_enabled, bool):
        app_debug_mode_is_enabled = False
    # --- Preis-Matrix vollständig entfernt ---
    # Ergebnisse kennzeichnen, damit aufrufende Komponenten wissen, dass das
    # alte Feature nicht mehr existiert.
    results["price_matrix_source_type"] = "removed"
    results["price_matrix_loaded_successfully"] = False

    # Einspeisevergütungen laden
    feed_in_tariffs_block = real_load_admin_setting(
        "feed_in_tariffs", Dummy_load_admin_setting_calc("feed_in_tariffs")
    )
    einspeiseverguetung_parts_data = (
        feed_in_tariffs_block.get("parts", [])
        if isinstance(feed_in_tariffs_block, dict)
        else []
    )
    einspeiseverguetung_full_data = (
        feed_in_tariffs_block.get("full", [])
        if isinstance(feed_in_tariffs_block, dict)
        else []
    )

    # Globale Konstanten extrahieren mit robusten Fallbacks
    DEFAULT_YIELD_KWH_PER_KWP_ANNUAL = float(
        global_constants.get("default_specific_yield_kwh_kwp", 950.0) or 950.0
    )
    simulation_period_years_default = int(
        global_constants.get("simulation_period_years", 20) or 20
    )
    results["simulation_period_years_effective"] = (
        simulation_duration_user
        if simulation_duration_user is not None
        else int(
            economic_data.get(
                "simulation_period_years", simulation_period_years_default
            )
            or simulation_period_years_default
        )
    )
    electricity_price_increase_default_percent = float(global_constants.get(
        "electricity_price_increase_annual_percent", 3.0) or 3.0)
    results["electricity_price_increase_rate_effective_percent"] = (
        electricity_price_increase_user
        if electricity_price_increase_user is not None
        else float(
            economic_data.get(
                "electricity_price_increase_annual_percent",
                electricity_price_increase_default_percent,
            )
            or electricity_price_increase_default_percent
        )
    )
    vat_rate_percent = float(
        global_constants.get(
            "vat_rate_percent",
            0.0) or 0.0)
    inflation_rate_percent = float(
        global_constants.get("inflation_rate_percent", 2.0) or 2.0
    )
    loan_interest_rate_percent = float(
        global_constants.get("loan_interest_rate_percent", 4.0) or 4.0
    )
    annual_module_degradation_percent = float(
        global_constants.get("annual_module_degradation_percent", 0.5) or 0.5
    )
    annual_degredation_factor = 1.0 - \
        (annual_module_degradation_percent / 100.0)
    specific_yields_by_orientation_tilt = global_constants.get(
        "specific_yields_by_orientation_tilt", {}
    )
    if not isinstance(
        specific_yields_by_orientation_tilt, dict
    ):  # Fallback, falls Typ nicht stimmt
        specific_yields_by_orientation_tilt = Dummy_load_admin_setting_calc(
            "global_constants"
        )["specific_yields_by_orientation_tilt"]
    global_yield_adjustment_percent = float(
        global_constants.get("global_yield_adjustment_percent", 0.0) or 0.0
    )

    # Projektdaten für Verbrauch und Strompreis
    jahresverbrauch_haushalt = float(
        project_details.get("annual_consumption_kwh_yr", 0.0) or 0.0
    )
    jahresverbrauch_heizung = float(
        project_details.get("consumption_heating_kwh_yr", 0.0) or 0.0
    )
    annual_consumption_kwh_yr = jahresverbrauch_haushalt + jahresverbrauch_heizung
    electricity_price_kwh = float(
        project_details.get("electricity_price_kwh", 0.30) or 0.30
    )
    results["total_consumption_kwh_yr"] = (
        annual_consumption_kwh_yr  # Für Diagramme oft benötigt
    )
    (
        results["jahresstromverbrauch_fuer_hochrechnung_kwh"],
        results["aktueller_strompreis_fuer_hochrechnung_euro_kwh"],
    ) = (annual_consumption_kwh_yr, electricity_price_kwh)

    # Anlagengröße
    selected_module_id = project_details.get("selected_module_id")
    module_details = (real_get_product_by_id(
        selected_module_id) if selected_module_id else None)
    module_capacity_w = (
        float(
            module_details.get(
                "capacity_w",
                0.0) or 0.0) if module_details else 0.0)
    results["anlage_kwp"] = (module_quantity * module_capacity_w) / 1000.0

    # Anlagengröße für erweiterte Berechnungen definieren
    anlage_kwp = results["anlage_kwp"]

    # Fallback: Neuberechnung, falls 'anlage_kwp' aus project_details fehlt oder 0 ist.
    # Dies ist die ursprüngliche Logik, die nun als Fallback dient.

    # Hinzufügen von Fehlermeldungen/Warnungen, wenn der Fallback verwendet
    # wird oder null ergibt

    # PVGIS-Datenabruf oder manuelle Ertragsberechnung
    pvgis_results_data = None

    # KORREKTUR: PV GIS Einstellung aus Datenbank laden statt aus
    # global_constants
    try:
        from database import load_admin_setting
        pvgis_setting_raw = load_admin_setting(
            "pvgis_enabled", "false")  # Default auf false
        # Boolean-Konvertierung - berücksichtigt String-Werte aus Datenbank
        if isinstance(pvgis_setting_raw, str):
            pvgis_enabled = pvgis_setting_raw.lower() in [
                'true', '1', 'yes', 'on']
        else:
            pvgis_enabled = bool(pvgis_setting_raw)

        # Debug-Info für PV GIS Status
        if app_debug_mode_is_enabled:
            debug_msg = f"DEBUG: PV GIS Status - Raw: '{pvgis_setting_raw}', Enabled: {pvgis_enabled}"
            print(debug_msg)
            if STREAMLIT_AVAILABLE:
                st.sidebar.info(debug_msg)

    except ImportError:
        # Fallback auf global_constants wenn Datenbank nicht verfügbar
        pvgis_enabled = bool(
            global_constants.get(
                "pvgis_enabled",
                False))  # Default auf false
        if app_debug_mode_is_enabled:
            debug_msg = f"DEBUG: PV GIS Fallback - Enabled: {pvgis_enabled} (Database not available)"
            print(debug_msg)
            if STREAMLIT_AVAILABLE:
                st.sidebar.info(debug_msg)

    if (
        pvgis_enabled
        and project_details.get("latitude") is not None
        and project_details.get("longitude") is not None
        and results["anlage_kwp"] > 0
    ):
        # Debug: Zeige PV GIS Status
        if hasattr(st, 'sidebar'):  # Nur wenn Streamlit verfügbar
            st.info(
                f" DEBUG: PV GIS ist AKTIVIERT (pvgis_enabled={pvgis_enabled})")

        try:
            lat = float(project_details["latitude"])
            lon = float(project_details["longitude"])
            # Nur Koordinaten prüfen wenn PV GIS aktiviert ist
            if (
                abs(lat) < 1e-5 and abs(lon) < 1e-5
            ):  # Standardkoordinaten (0,0) sind meist ungültig für PVGIS
                errors_list.append(
                    texts.get(
                        "warn_pvgis_zero_coords",
                        "PVGIS: Ungültige Standardkoordinaten (0,0) erhalten. Nutze manuelle Ertragsberechnung.",
                    ))
            elif not (
                -90 <= lat <= 90 and -180 <= lon <= 180
            ):  # Gültigkeitsbereich prüfen
                errors_list.append(
                    texts.get(
                        "pvgis_invalid_lat_lon_range",
                        "PVGIS: Breiten- oder Längengrade außerhalb des gültigen Bereichs.",
                    ))
            else:
                tilt_val = int(
                    project_details.get(
                        "roof_inclination_deg",
                        30) or 30)
                orientation_text_val = project_details.get(
                    "roof_orientation", "Süd")
                azimuth_val = convert_orientation_to_pvgis_azimuth(
                    orientation_text_val)
                SYSTEM_LOSS_PVGIS = float(
                    global_constants.get(
                        "pvgis_system_loss_default_percent",
                        14.0) or 14.0)
                pvgis_results_data = get_pvgis_data(
                    lat,
                    lon,
                    results["anlage_kwp"],
                    tilt_val,
                    azimuth_val,
                    SYSTEM_LOSS_PVGIS,
                    texts,
                    errors_list,
                    debug_mode_enabled=app_debug_mode_is_enabled,
                )
        except (ValueError, TypeError) as e_coords:
            errors_list.append(
                (
                    texts.get(
                        "error_geocoding_conversion_calc",
                        "Fehler Konvertierung Geodaten für PVGIS.",
                    )
                    or ""
                )
                + f" Details: {e_coords}"
            )
            pvgis_results_data = None  # Sicherstellen, dass es None ist bei Fehler
    elif not pvgis_enabled:
        # PVGIS ist deaktiviert - verwende manuelle Berechnung ohne Meldung
        pvgis_results_data = None

    annual_pv_production_kwh_base, monthly_pv_production_kwh_base = 0.0, [
        0.0] * 12
    results["pvgis_data_used"] = False  # Standardmäßig auf False setzen

    if pvgis_results_data and isinstance(pvgis_results_data, dict):
        annual_prod_pvgis = pvgis_results_data.get("annual_production_kwh")
        monthly_prod_pvgis = pvgis_results_data.get("monthly_production_kwh")
        if (
            isinstance(annual_prod_pvgis, (int, float))
            and isinstance(monthly_prod_pvgis, list)
            and len(monthly_prod_pvgis) == 12
        ):
            if (
                annual_prod_pvgis == 0.0 and results["anlage_kwp"] > 0
            ):  # Wenn PVGIS 0 liefert trotz Anlage
                # if app_debug_mode_is_enabled and not any("PVGIS" in err for err in errors_list): # Bereinigt
                # errors_list.append(texts.get("warn_pvgis_returned_zero_yield_fallback", "PVGIS lieferte 0 kWh Ertrag. Nutze manuelle Ertragsberechnung."))
                pass  # Fehler wurde bereits in get_pvgis_data behandelt oder es wird der manuelle Fallback genutzt
            else:
                annual_pv_production_kwh_base = annual_prod_pvgis
                monthly_pv_production_kwh_base = monthly_prod_pvgis
                results["specific_annual_yield_kwh_per_kwp"] = pvgis_results_data.get(
                    "specific_yield_kwh_kwp_pa", 0.0)
                results["pvgis_source"] = pvgis_results_data.get(
                    "pvgis_source", "PVGIS"
                )
                results["pvgis_data_used"] = True
        # else: # Bereinigt
        # if app_debug_mode_is_enabled:
        # errors_list.append(texts.get("warn_pvgis_incomplete_data_fallback", "PVGIS-Antwort unvollständig/fehlerhaft. Nutze manuelle Ertragsberechnung."))

    if (
        not results["pvgis_data_used"] and results["anlage_kwp"] > 0
    ):  # Fallback zur manuellen Berechnung
        # Informative Meldung wenn PV GIS bewusst deaktiviert wurde
        if not pvgis_enabled and STREAMLIT_AVAILABLE:
            try:
                import streamlit as st_local
                st_local.info(
                    "ℹ PV GIS ist in den Einstellungen DEAKTIVIERT. Verwende manuelle Ertragsberechnung.")
            except BaseException:
                pass  # Streamlit nicht verfügbar, ignoriere Meldung

        orientation_key = project_details.get(
            "roof_orientation", "Sonstige"
        )  # Default auf 'Sonstige'
        tilt_val_manual = project_details.get(
            "roof_inclination_deg", 30
        )  # Default auf 30 Grad
        tilt_key_manual = int(
            tilt_val_manual or 30
        )  # Sicherstellen, dass es ein Int ist
        lookup_key = f"{orientation_key}_{tilt_key_manual}"
        specific_yields_map = global_constants.get(
            "specific_yields_by_orientation_tilt", {}
        )
        if not isinstance(
            specific_yields_map, dict
        ):  # Fallback, falls Typ nicht stimmt
            specific_yields_map = Dummy_load_admin_setting_calc(
                "global_constants")["specific_yields_by_orientation_tilt"]
        specific_annual_yield_kwh_per_kwp_manual = float(
            specific_yields_map.get(lookup_key, DEFAULT_YIELD_KWH_PER_KWP_ANNUAL)
            or DEFAULT_YIELD_KWH_PER_KWP_ANNUAL
        )
        annual_pv_production_kwh_base = (
            results["anlage_kwp"] * specific_annual_yield_kwh_per_kwp_manual
        )
        results["specific_annual_yield_kwh_per_kwp"] = (
            specific_annual_yield_kwh_per_kwp_manual
        )
        monthly_distribution_factors = global_constants.get(
            "monthly_production_distribution", [1 / 12] * 12
        )
        if (
            not isinstance(monthly_distribution_factors, list)
            or len(monthly_distribution_factors) != 12
            or not all(
                isinstance(x, (int, float)) for x in monthly_distribution_factors
            )
        ):
            monthly_distribution_factors = [1 / 12] * 12  # Robuster Fallback
            errors_list.append(
                texts.get(
                    "warn_invalid_monthly_distribution",
                    "Ungültige monatliche Produktionsverteilung in Konstanten, nutze gleichmäßige Verteilung.",
                ))
        sum_factors = sum(
            monthly_distribution_factors
        )  # Normierung, falls Summe nicht 1
        normalized_monthly_distribution = (
            [f / sum_factors for f in monthly_distribution_factors]
            if sum_factors > 0
            else [1 / 12] * 12
        )
        monthly_pv_production_kwh_base = [
            annual_pv_production_kwh_base * factor
            for factor in normalized_monthly_distribution
        ]
        results["pvgis_source"] = "Manuelle Berechnung"  # Quelle klarstellen
        # if app_debug_mode_is_enabled: # Bereinigt
        # print(f"CALC: Manuelle Ertragsberechnung: lookup_key='{lookup_key}', specific_yield={specific_annual_yield_kwh_per_kwp_manual} kWh/kWp/a")
    elif results["anlage_kwp"] == 0:  # Keine Anlage, keine Produktion
        annual_pv_production_kwh_base = 0.0
        monthly_pv_production_kwh_base = [0.0] * 12
        results["specific_annual_yield_kwh_per_kwp"] = 0.0
        results["pvgis_source"] = "Keine Anlage"
        # if app_debug_mode_is_enabled: print("CALC: Keine Anlagenleistung (0
        # kWp), daher keine Ertragsberechnung.") # Bereinigt

    # Globale Ertragsanpassung anwenden
    annual_pv_production_kwh = annual_pv_production_kwh_base * (
        1 + global_yield_adjustment_percent / 100.0
    )
    monthly_pv_production_kwh = [
        m_prod * (1 + global_yield_adjustment_percent / 100.0)
        for m_prod in monthly_pv_production_kwh_base
    ]

    # if global_yield_adjustment_percent != 0.0 and app_debug_mode_is_enabled: # Bereinigt
    # errors_list.append((texts.get("info_global_yield_adjustment_applied", "Globale Ertragsanpassung von {percent}% wurde angewendet.") or "").format(percent=global_yield_adjustment_percent))

    results["annual_pv_production_kwh"] = annual_pv_production_kwh
    results["monthly_productions_sim"] = (
        monthly_pv_production_kwh  # Dies sind die Produktionsdaten für Jahr 1
    )

    # if app_debug_mode_is_enabled: print(f"CALC: Jährliche PV Produktion
    # (nach Anpassung, Jahr 1): {annual_pv_production_kwh:.2f} kWh") #
    # Bereinigt

    # Monatlicher Verbrauch
    monthly_distribution_factors_consumption = global_constants.get(
        "monthly_consumption_distribution", [1 / 12] * 12
    )
    if (
        not isinstance(monthly_distribution_factors_consumption, list)
        or len(monthly_distribution_factors_consumption) != 12
        or not all(
            isinstance(x, (int, float))
            for x in monthly_distribution_factors_consumption
        )
    ):
        monthly_distribution_factors_consumption = [1 / 12] * 12  # Fallback
        errors_list.append(
            texts.get(
                "warn_invalid_monthly_consumption_distribution",
                "Ungültige monatliche Verbrauchsverteilung, nutze gleichmäßige Verteilung.",
            ))
    sum_factors_cons = sum(monthly_distribution_factors_consumption)
    normalized_monthly_consumption_distribution = (
        [f / sum_factors_cons for f in monthly_distribution_factors_consumption]
        if sum_factors_cons > 0
        else [1 / 12] * 12
    )
    monthly_total_consumption_kwh = [
        annual_consumption_kwh_yr * factor
        for factor in normalized_monthly_consumption_distribution
    ]
    results["monthly_consumption_sim"] = (
        monthly_total_consumption_kwh  # Monatlicher Verbrauch für Jahr 1
    )

    # Eigenverbrauchsberechnung (vereinfacht, kann detaillierter werden)
    direct_sc_from_production_factor = float(global_constants.get(
        "direct_self_consumption_factor_of_production", 0.25) or 0.25)
    include_storage = project_details.get("include_storage", False)
    selected_storage_id = (
        project_details.get("selected_storage_id") if include_storage else None
    )
    # Sicherstellen, dass die Storage-ID wirklich ein int ist (wichtig für
    # get_product_by_id)
    if selected_storage_id is not None and not isinstance(
            selected_storage_id, int):
        try:
            selected_storage_id = int(str(selected_storage_id).strip())
        except Exception:
            # Falls Konvertierung fehlschlägt, belassen wir den Wert (Lookup
            # schlägt dann ggf. fehl)
            pass
    # Nutze die explizit im Projekt ausgewählte Kapazität, nicht die aus den
    # Produktdetails für diese Logik
    selected_storage_capacity_kwh = (
        float(
            project_details.get(
                "selected_storage_storage_power_kw",
                0.0) or 0.0) if include_storage else 0.0)
    storage_efficiency = float(
        global_constants.get("storage_efficiency", 0.9) or 0.9
    )  # Speicherwirkungsgrad

    monthly_direct_self_consumption_kwh = [0.0] * 12
    monthly_storage_charge_kwh = [
        0.0
    ] * 12  # Wie viel in den Speicher geladen wird (Netto nach Ladeverlust)
    monthly_storage_discharge_for_sc_kwh = [
        0.0
    ] * 12  # Wie viel aus dem Speicher für Eigenverbrauch entladen wird
    monthly_feed_in_kwh = [0.0] * 12
    monthly_grid_bezug_kwh = [0.0] * 12

    for i in range(12):
        prod_month = monthly_pv_production_kwh[i]
        cons_month = monthly_total_consumption_kwh[i]

        # 1. Direkter Eigenverbrauch – Grundlogik (Begrenzung durch
        # gleichzeitige Verfügbarkeit)
        direct_sc_base = min(prod_month, cons_month)
        # Dynamischer Faktor (Standard 35 %, konfigurierbar über
        # global_constants)
        direct_fraction = float(
            global_constants.get(
                "direct_sc_fraction_cap",
                0.35) or 0.35)
        if direct_fraction < 0.05:
            direct_fraction = 0.05
        if direct_fraction > 0.85:
            direct_fraction = 0.85
        direct_sc = min(direct_sc_base, prod_month * direct_fraction)
        monthly_direct_self_consumption_kwh[i] = direct_sc

        # 2. Überschuss & Restverbrauch nach Direktverbrauch
        pv_ueberschuss = max(0.0, prod_month - direct_sc)
        rest_verbrauch = max(0.0, cons_month - direct_sc)

        # 3. Speicher-Ladung nur aus PV-Überschuss
        speicher_ladung_brutto = (
            min(pv_ueberschuss, selected_storage_capacity_kwh)
            if include_storage and selected_storage_capacity_kwh > 0
            else 0.0
        )
        speicher_ladung_netto = speicher_ladung_brutto * storage_efficiency
        monthly_storage_charge_kwh[i] = speicher_ladung_netto

        # 4. Speicher-Nutzung: realistisch wird ein Teil der geladenen Energie zeitversetzt verbraucht
        # Falls rest_verbrauch == 0 (z.B. sehr niedriger Verbrauch oder hohe direkte Deckung), erlauben wir
        # trotzdem eine Nutzung eines Anteils (abendliche Verlagerung). Annahme: bis zu 50 % des Verbrauchs
        # darf über zeitversetzte Speicherung laufen, begrenzt durch Ladung.
        evening_fraction = float(
            global_constants.get(
                "evening_shift_fraction",
                0.5) or 0.5)
        if evening_fraction < 0.1:
            evening_fraction = 0.1
        if evening_fraction > 0.9:
            evening_fraction = 0.9

        # Basispotenzial für Speicherentladung = Restverbrauch
        discharge_potential = rest_verbrauch
        if discharge_potential <= 0 and speicher_ladung_netto > 0 and cons_month > 0:
            # Künstliche Abendverschiebung falls kompletter Verbrauch schon als
            # direkt gezählt wurde
            shifted_portion = cons_month * evening_fraction
            # Verhindere Doppelzählung: reduziere den direkten Eigenverbrauch
            # entsprechend (nur intern für Entladung)
            effective_direct_for_storage_view = max(
                0.0, direct_sc - shifted_portion)
            # Neue nutzbare Speicher-Entladungsmenge durch Verschiebung
            discharge_potential = min(shifted_portion, speicher_ladung_netto)
        # Tatsächliche Speicherentladung begrenzt durch Ladung
        speicher_nutzung = min(speicher_ladung_netto, discharge_potential)

        # 4b. Mindest-Nutzungsanteil falls bislang 0 (Vermeidung
        # unrealistischer 0-Entladung bei vorhandener Ladung)
        if speicher_nutzung <= 0 and speicher_ladung_netto > 0 and cons_month > 0:
            min_usage_share = float(
                global_constants.get(
                    "storage_min_usage_share_of_charge",
                    0.25) or 0.25)
            if min_usage_share < 0.05:
                min_usage_share = 0.05
            if min_usage_share > 0.9:
                min_usage_share = 0.9
            min_usage_candidate = speicher_ladung_netto * min_usage_share
            # Zusätzlich durch Gesamtverbrauch begrenzen
            min_usage = min(
                min_usage_candidate,
                speicher_ladung_netto,
                cons_month)
            if min_usage > speicher_nutzung:
                speicher_nutzung = min_usage

        monthly_storage_discharge_for_sc_kwh[i] = speicher_nutzung

        # 5. Netzeinspeisung nach Speicherladung (brutto-Ladung abziehen)
        netzeinspeisung = max(0.0, pv_ueberschuss - speicher_ladung_brutto)
        monthly_feed_in_kwh[i] = netzeinspeisung

        # 6. Netzbezug: Restverbrauch minus Speicher-Nutzung
        grid_bezug = max(0.0, rest_verbrauch - speicher_nutzung)
        monthly_grid_bezug_kwh[i] = grid_bezug

        if app_debug_mode_is_enabled:
            try:
                print(
                    f"MONAT {
                        i +
                        1:02d} | Prod={
                        prod_month:.2f} kWh | Verbrauch={
                        cons_month:.2f} kWh | Direkt={
                        direct_sc:.2f} | PV-Überschuss={
                        pv_ueberschuss:.2f} | RestVerbrauch={
                            rest_verbrauch:.2f} | Ladung={
                                speicher_ladung_netto:.2f} | Nutzung={
                                    speicher_nutzung:.2f} | Einspeisung={
                                        netzeinspeisung:.2f} | Netzbezug={
                                            grid_bezug:.2f}")
            except Exception:
                pass

    # --- Spezialfall Volleinspeisung ----------------------------------------
    feed_in_type_str_tmp = str(
        project_details.get(
            "feed_in_type",
            "Teileinspeisung") or "Teileinspeisung")
    if feed_in_type_str_tmp.lower().startswith("voll"):
        # Bei Volleinspeisung wird die gesamte Produktion eingespeist, kein
        # Eigenverbrauch
        monthly_direct_self_consumption_kwh = [0.0] * 12
        monthly_storage_charge_kwh = [0.0] * 12
        monthly_storage_discharge_for_sc_kwh = [0.0] * 12
        # alles geht ins Netz
        monthly_feed_in_kwh = monthly_pv_production_kwh[:]
        # gesamter Verbrauch aus dem Netz
        monthly_grid_bezug_kwh = monthly_total_consumption_kwh[:]
        # Hinweis: Speicher wird bei reiner Volleinspeisung wirtschaftlich
        # nicht genutzt -> 0 gesetzt
        if app_debug_mode_is_enabled:
            errors_list.append(
                texts.get(
                    "info_full_feed_in_override",
                    "Info: Volleinspeisung aktiviert – Eigenverbrauch & Speicher auf 0 gesetzt.",
                ))

    eigenverbrauch_pro_jahr_kwh = sum(monthly_direct_self_consumption_kwh) + sum(
        monthly_storage_discharge_for_sc_kwh)  # bei Volleinspeisung bereits 0
    netzeinspeisung_kwh = sum(monthly_feed_in_kwh)
    grid_bezug_kwh = sum(monthly_grid_bezug_kwh)  # Netzbezug (kWh)
    # Jährliche Speicher-Summen für PDF-Platzhalter
    annual_storage_charge_kwh = sum(
        monthly_storage_charge_kwh)  # Speicherladung pro Jahr
    annual_storage_discharge_kwh = sum(
        monthly_storage_discharge_for_sc_kwh)  # Speichernutzung pro Jahr

    results.update(
        {
            "monthly_direct_self_consumption_kwh": monthly_direct_self_consumption_kwh,
            "monthly_storage_charge_kwh": monthly_storage_charge_kwh,
            "monthly_storage_discharge_for_sc_kwh": monthly_storage_discharge_for_sc_kwh,
            "monthly_feed_in_kwh": monthly_feed_in_kwh,
            "monthly_grid_bezug_kwh": monthly_grid_bezug_kwh,
            "eigenverbrauch_pro_jahr_kwh": eigenverbrauch_pro_jahr_kwh,
            # Netzeinspeisung (kWh)
            "netzeinspeisung_kwh": netzeinspeisung_kwh,
            "grid_bezug_kwh": grid_bezug_kwh,
            "annual_storage_charge_kwh": annual_storage_charge_kwh,  # Speicherladung pro Jahr
            # Speichernutzung pro Jahr
            "annual_storage_discharge_kwh": annual_storage_discharge_kwh,
        }
    )

    selected_inverter_id = project_details.get("selected_inverter_id")
    inverter_details = (real_get_product_by_id(
        selected_inverter_id) if selected_inverter_id else None)
    free_roof_area_sqm = float(
        project_details.get(
            "free_roof_area_sqm",
            0.0) or 0.0)

    # Speicher-Produktdetails früh auflösen (für Matrix & Aufpreise)
    storage_details_from_db = None
    if include_storage and selected_storage_id:
        try:
            storage_details_from_db = real_get_product_by_id(
                selected_storage_id)
        except Exception:
            storage_details_from_db = None

    # --- NEUE Dynamische Preis-Matrix Integration ---
    # Falls eine aktive Matrix existiert, wird versucht anhand:
    #   row_label  = Anzahl Module (floor match für numerische Labels)
    #   column_label = Speicher-Konfiguration (oder "Ohne Speicher")
    # einen Basispreis zu ermitteln. Fallback: 0.0
    from price_matrix_store import get_active_matrix_id, get_matrix_full, lookup_price
    matrix_price_is_pauschal = False
    # Speichert tatsächliche Spalte die gefunden wurde
    matrix_column_used_for_price = None
    active_matrix_id = get_active_matrix_id()
    storage_column_label = None
    if include_storage:
        # Speicherlabel aus project_details oder DB ableiten
        # Versuche zuerst exaktes Modell, ansonsten generisches Label
        if storage_details_from_db:
            storage_column_label = storage_details_from_db.get(
                "model_name") or None
        if not storage_column_label:
            storage_column_label = texts.get(
                "storage_generic_label", "Speicher")
    else:
        storage_column_label = texts.get(
            "no_storage_option_for_matrix", "Ohne Speicher")

    base_matrix_price_netto = 0.0
    # Meta aus Matrix (Standardwerte bis echte Meta geladen wurde)
    matrix_pricing_mode = 'pauschal'
    # True bedeutet: Zubehör im Pauschalpreis enthalten -> nicht extra addieren
    matrix_include_accessories = True
    # True bedeutet: Sonstige Kosten im Pauschalpreis enthalten
    matrix_include_misc = True
    suppress_accessories = False
    suppress_misc = False
    if active_matrix_id:
        try:
            # Zeilenlabel = Modulanzahl (als Zahl interpretierbar)
            row_label = str(
                int(module_quantity)) if module_quantity is not None else None
            col_label = storage_column_label
            looked_up = None
            if row_label and col_label:
                looked_up = lookup_price(
                    active_matrix_id, row_label, col_label)
                if looked_up is None and include_storage:
                    # Versuch Fallback auf generischen Speicherlabel
                    generic_fallback = texts.get(
                        "storage_generic_label", "Speicher")
                    if generic_fallback != col_label:
                        looked_up = lookup_price(
                            active_matrix_id, row_label, generic_fallback)
                if looked_up is None and not include_storage:
                    # Versuch alternativen Ohne-Speicher Text
                    alt_no_storage = texts.get(
                        "no_storage_alt_label", "Ohne Speicher")
                    if alt_no_storage != col_label:
                        looked_up = lookup_price(
                            active_matrix_id, row_label, alt_no_storage)
            if looked_up is None and row_label:
                # Letzter Fallback: kolumnen-unabhängige Basis (falls Spalte
                # nicht gefunden) -> Versuche "Ohne Speicher"
                generic_no_storage = texts.get(
                    "no_storage_option_for_matrix", "Ohne Speicher")
                looked_up = lookup_price(
                    active_matrix_id, row_label, generic_no_storage)
            if looked_up is not None:
                base_matrix_price_netto = float(looked_up)
                # Annahme: Matrixpreis beinhaltet Standardkosten außer
                # expliziten Aufpreisen
                matrix_price_is_pauschal = True
                results["matrix_matched_module_count"] = module_quantity
                results["matrix_matched_storage_column"] = storage_column_label
                matrix_column_used_for_price = storage_column_label
                # Versuche Meta-Daten einzulesen (pricing_mode / include_*
                # flags)
                try:
                    _full = get_matrix_full(active_matrix_id)
                    if _full and isinstance(_full, dict):
                        _meta = _full.get('meta') or {}
                        matrix_pricing_mode = (
                            _meta.get('pricing_mode') or 'pauschal') or 'pauschal'
                        matrix_include_accessories = bool(
                            _meta.get('include_accessories', True))
                        matrix_include_misc = bool(
                            _meta.get('include_misc', True))
                except Exception:
                    pass
            else:
                results["matrix_matched_module_count"] = None
                results["matrix_matched_storage_column"] = None
        except Exception as _e:
            results["matrix_lookup_error"] = str(_e)
            results["matrix_matched_module_count"] = None
            results["matrix_matched_storage_column"] = None
    else:
        results["matrix_matched_module_count"] = None
        results["matrix_matched_storage_column"] = None

    # Suppression Flags bestimmen (nur sinnvoll bei Pauschalmodus und
    # gefundenem Preis)
    if matrix_price_is_pauschal and base_matrix_price_netto > 0 and matrix_pricing_mode == 'pauschal':
        suppress_accessories = matrix_include_accessories
        suppress_misc = matrix_include_misc

    results["base_matrix_price_netto"] = base_matrix_price_netto
    results["matrix_pricing_mode"] = matrix_pricing_mode
    results["matrix_include_accessories"] = matrix_include_accessories
    results["matrix_include_misc"] = matrix_include_misc
    results["matrix_accessories_suppressed"] = suppress_accessories
    results["matrix_misc_suppressed"] = suppress_misc

    cost_modules_aufpreis_netto = 0.0
    cost_inverter_aufpreis_netto = 0.0
    cost_accessories_aufpreis_netto = 0.0
    cost_misc_netto = 0.0  # Sonstige Kosten

    # Modul- & WR-Aufpreise nur addieren wenn kein Pauschalpreis ODER
    # additiver Modus
    if (not matrix_price_is_pauschal) or matrix_pricing_mode == 'additiv':
        cost_modules_aufpreis_netto = (
            float(
                module_details.get(
                    "additional_cost_netto",
                    0.0) or 0.0) *
            module_quantity if module_details and module_quantity else 0.0)
        cost_inverter_aufpreis_netto = (
            float(inverter_details.get("additional_cost_netto", 0.0) or 0.0)
            if inverter_details else 0.0
        )
    # Zubehör / Sonstige nur addieren wenn nicht unterdrückt
    if not suppress_accessories:
        cost_accessories_aufpreis_netto = float(global_constants.get(
            "additional_components_flat_rate_netto", 500.0) or 500.0)
    if not suppress_misc:
        cost_misc_netto = float(
            global_constants.get("misc_costs_flat_rate_netto", 200.0) or 200.0
        )
    # elif app_debug_mode_is_enabled: # Bereinigt
    # errors_list.append("CALC: Gültiger Matrix-Pauschalpreis. Zusatzkosten Module, WR, Zubehör, Sonstige auf 0 (da im Pauschalpreis enthalten).")

    # Speicher-Zusatzkosten: Nur wenn Matrix "Ohne Speicher" verwendet wurde
    # oder kein Matrixpreis UND Speicher gewünscht
    cost_storage_aufpreis_product_db_netto = 0.0
    if include_storage and storage_details_from_db:
        # Speicherkosten nur addieren wenn:
        # - kein Matrixpreis gefunden wurde ODER
        # - Matrix-Spalte einem "Ohne Speicher" Label entspricht
        no_storage_variants = [
            texts.get(
                "no_storage_option_for_matrix",
                "Ohne Speicher").strip().lower(),
            texts.get(
                "no_storage_alt_label",
                "Ohne Speicher").strip().lower(),
        ]
        matrix_col_lower = (matrix_column_used_for_price or "").strip().lower()
        should_add_storage_db_cost_cond = (
            results["base_matrix_price_netto"] == 0.0
        ) or (
            matrix_col_lower in no_storage_variants
        )
        if should_add_storage_db_cost_cond:
            cost_storage_aufpreis_product_db_netto = float(
                storage_details_from_db.get("additional_cost_netto", 0.0) or 0.0
            )
            # if app_debug_mode_is_enabled and cost_storage_aufpreis_product_db_netto > 0: # Bereinigt
            # errors_list.append(f"CALC: Zusatzkosten Speicher '{storage_details_from_db.get('model_name')}' aus DB ({cost_storage_aufpreis_product_db_netto:.2f}€) addiert (Matrix='Ohne Speicher' oder kein Matrixpreis).")
        # elif app_debug_mode_is_enabled and matrix_column_used_for_price and include_storage : # Bereinigt
        # errors_list.append(f"CALC: Matrixpreis für spezifischen Speicher '{matrix_column_used_for_price}' verwendet. KEINE separaten Speicherkosten aus DB addiert.")
    results["cost_storage_aufpreis_product_db_netto"] = (
        cost_storage_aufpreis_product_db_netto
    )
    # if app_debug_mode_is_enabled: print(f"CALC:
    # cost_storage_aufpreis_product_db_netto={cost_storage_aufpreis_product_db_netto:.2f}")
    # # Bereinigt

    # Weitere Kosten
    cost_scaffolding_netto = (
        free_roof_area_sqm *
        float(
            global_constants.get(
                "scaffolding_cost_per_sqm_gt_7m_netto",
                20.0) or 20.0) if project_details.get(
            "building_height_gt_7m",
            False) else 0.0)
    cost_custom_netto = float(
        economic_data.get("custom_costs_netto", 0.0) or 0.0
    )  # Manuelle Zusatzkosten

    # Optionale Komponenten
    total_optional_components_cost_netto = 0.0
    optional_component_keys_map_calc = {
        "selected_wallbox_id": "cost_wallbox_aufpreis_netto",
        "selected_ems_id": "cost_ems_aufpreis_netto",
        # Annahme: pauschal oder pro Modul * Menge? Hier pauschal.
        "selected_optimizer_id": "cost_optimizer_aufpreis_netto",
        "selected_carport_id": "cost_carport_aufpreis_netto",
        "selected_notstrom_id": "cost_notstrom_aufpreis_netto",
        "selected_tierabwehr_id": "cost_tierabwehr_aufpreis_netto",
    }
    if project_details.get("include_additional_components", False):
        for pd_key, res_key in optional_component_keys_map_calc.items():
            component_id = project_details.get(pd_key)
            cost_val = 0.0
            if component_id:
                component_details_db = real_get_product_by_id(component_id)
                cost_val = (
                    float(
                        component_details_db.get(
                            "additional_cost_netto",
                            0.0) or 0.0) if component_details_db else 0.0)
                # Spezifische Logik für Optimierer (Menge?) könnte hierhin
                # if pd_key == 'selected_optimizer_id' and module_quantity > 0:
                # cost_val *= module_quantity # Beispiel
                total_optional_components_cost_netto += cost_val
            # Speichere individuelle Kosten im Ergebnis
            results[res_key] = cost_val
    # if app_debug_mode_is_enabled: print(f"CALC:
    # total_optional_components_cost_netto={total_optional_components_cost_netto:.2f}")
    # # Bereinigt

    # Summe aller Zusatzkosten (die nicht im Matrix-Pauschalpreis sind)
    total_additional_costs_netto = sum(
        filter(
            None,
            [
                cost_modules_aufpreis_netto,
                cost_inverter_aufpreis_netto,
                cost_storage_aufpreis_product_db_netto,
                # Diese werden nur addiert, wenn sie nicht im Matrixpreis sind
                cost_accessories_aufpreis_netto,
                cost_misc_netto,
                cost_scaffolding_netto,
                cost_custom_netto,
                total_optional_components_cost_netto,
            ],
        )
    )
    results.update(
        {
            "cost_modules_aufpreis_netto": cost_modules_aufpreis_netto,
            "cost_inverter_aufpreis_netto": cost_inverter_aufpreis_netto,
            "cost_accessories_aufpreis_netto": cost_accessories_aufpreis_netto,
            "cost_misc_netto": cost_misc_netto,
            "cost_scaffolding_netto": cost_scaffolding_netto,
            "cost_custom_netto": cost_custom_netto,
            "total_optional_components_cost_netto": total_optional_components_cost_netto,
            "total_additional_costs_netto": total_additional_costs_netto,
        })
    # if app_debug_mode_is_enabled: print(f"CALC:
    # total_additional_costs_netto={total_additional_costs_netto:.2f}") #
    # Bereinigt

    subtotal_netto = results["base_matrix_price_netto"] + \
        total_additional_costs_netto
    results["subtotal_netto"] = subtotal_netto
    # if app_debug_mode_is_enabled: print(f"CALC: subtotal_netto (base_matrix
    # + total_additional): {subtotal_netto:.2f}") # Bereinigt

    one_time_bonus_eur = float(
        global_constants.get(
            "one_time_bonus_eur",
            0.0) or 0.0)
    total_investment_netto = subtotal_netto - one_time_bonus_eur
    # if one_time_bonus_eur > 0 and app_debug_mode_is_enabled: # Bereinigt
    # errors_list.append((texts.get("info_one_time_bonus_applied", "Einmaliger Bonus von {bonus:.2f} € wurde von Nettoinvestition abgezogen.") or "").format(bonus=one_time_bonus_eur))

    results["total_investment_netto"] = total_investment_netto
    results["vat_rate_percent"] = vat_rate_percent  # MwSt.-Satz
    results["total_investment_brutto"] = total_investment_netto * (
        1 + vat_rate_percent / 100.0
    )
    # if app_debug_mode_is_enabled: print(f"CALC: Endgültige Kosten:
    # base_matrix={results['base_matrix_price_netto']:.2f},
    # total_additional={total_additional_costs_netto:.2f},
    # subtotal_netto={subtotal_netto:.2f},
    # total_investment_netto={total_investment_netto:.2f},
    # c={results['total_investment_brutto']:.2f}") # Bereinigt

    # Bruttoinvestition für erweiterte Berechnungen definieren
    total_investment_brutto = results["total_investment_brutto"]

    # -------------------------------------------------------------
    # Finale Preisberechnung (final_price / final_price_netto / final_price_brutto)
    # KORREKTE FORMEL: Matrixpreis + Zubehör - Rabatte
    # Quelle der Modifikationen: st.session_state (falls vorhanden)
    # Diese Werte werden häufig in GUI und PDFs benötigt -> zentral hier ableiten.
    # -------------------------------------------------------------

    # Sammle alle Preismodifikationen aus verschiedenen Session State Quellen
    pricing_modifications = _collect_pricing_modifications_from_session()

    # Berechne finalen Preis mit korrekter Formel
    final_price_calculation_result = _calculate_final_price_with_correct_formula(
        base_matrix_price=results["base_matrix_price_netto"],
        additional_costs=total_additional_costs_netto,
        pricing_modifications=pricing_modifications,
        vat_rate_percent=vat_rate_percent,
        one_time_bonus=one_time_bonus_eur,
        debug_mode=app_debug_mode_is_enabled)

    # Aktualisiere Ergebnisse mit finalen Preisen
    results.update(final_price_calculation_result)

    # Für Konsistenz: "final_price" als Netto-Endpreis (existiert schon in
    # anderen Stellen)
    results["final_price"] = results["final_price_netto"]

    # --- Wirtschaftlichkeitsberechnung (Jahr 1) ---
    # Bei Volleinspeisung keine Einsparung durch Eigenverbrauch
    if str(project_details.get("feed_in_type", "Teileinspeisung")
           or "Teileinspeisung").lower().startswith("voll"):
        annual_electricity_cost_savings_self_consumption_year1 = 0.0
    else:
        annual_electricity_cost_savings_self_consumption_year1 = (
            eigenverbrauch_pro_jahr_kwh * electricity_price_kwh
        )
    results["annual_electricity_cost_savings_self_consumption_year1"] = (
        annual_electricity_cost_savings_self_consumption_year1
    )

    # Einspeisevergütung bestimmen
    einspeiseverguetung_ct_per_kwh = 0.0
    feed_in_type_str = project_details.get(
        "feed_in_type", "Teileinspeisung"
    )  # Default auf Teileinspeisung
    einspeiseverguetung_data_to_use = (
        einspeiseverguetung_parts_data
        if feed_in_type_str == "Teileinspeisung"
        else einspeiseverguetung_full_data
    )
    if (
        results["anlage_kwp"] > 0
        and einspeiseverguetung_data_to_use
        and isinstance(einspeiseverguetung_data_to_use, list)
    ):
        for entry in sorted(
            einspeiseverguetung_data_to_use,
            key=lambda x: float(x.get("kwp_max", 0.0) or 0.0),
        ):  # Sicherstellen, dass kwp_max ein Float ist
            if results["anlage_kwp"] <= float(
                entry.get("kwp_max", float("inf")) or float("inf")
            ):  # Sicherstellen, dass kwp_max ein Float ist
                einspeiseverguetung_ct_per_kwh = float(
                    entry.get("ct_per_kwh", 0.0) or 0.0
                )  # Sicherstellen, dass ct_per_kwh ein Float ist
                break
        if (
            einspeiseverguetung_ct_per_kwh == 0.0 and einspeiseverguetung_data_to_use
        ):  # Wenn kein passender Tarif gefunden wurde, nimm den letzten
            einspeiseverguetung_ct_per_kwh = float(
                einspeiseverguetung_data_to_use[-1].get("ct_per_kwh", 0.0) or 0.0
            )
    # elif not einspeiseverguetung_data_to_use and results['anlage_kwp'] > 0 and app_debug_mode_is_enabled: # Bereinigt
    # errors_list.append((texts.get("warn_no_feed_in_tariffs_defined", "Keine Einspeisevergütungen für Typ '{feed_in_type}' definiert.") or "").format(feed_in_type=feed_in_type_str))

    results["einspeiseverguetung_ct_per_kwh"] = einspeiseverguetung_ct_per_kwh
    results["einspeiseverguetung_eur_per_kwh"] = einspeiseverguetung_ct_per_kwh / 100.0
    annual_feed_in_revenue_year1 = (
        netzeinspeisung_kwh * results["einspeiseverguetung_eur_per_kwh"]
    )
    results["annual_feed_in_revenue_year1"] = annual_feed_in_revenue_year1

    # Kennzahlen-Quoten
    if annual_pv_production_kwh > 0:
        self_consumption_ratio = eigenverbrauch_pro_jahr_kwh / annual_pv_production_kwh
        feed_in_ratio = netzeinspeisung_kwh / annual_pv_production_kwh
    else:
        self_consumption_ratio = 0.0
        feed_in_ratio = 0.0
    if (eigenverbrauch_pro_jahr_kwh + grid_bezug_kwh) > 0:
        autarkiegrad = eigenverbrauch_pro_jahr_kwh / \
            (eigenverbrauch_pro_jahr_kwh + grid_bezug_kwh)
    else:
        autarkiegrad = 0.0
    results.update({
        # Anteil der PV-Erzeugung, der selbst verbraucht wird
        "self_consumption_ratio": self_consumption_ratio,
        "feed_in_ratio": feed_in_ratio,  # Anteil der PV-Erzeugung, der eingespeist wird
        # Anteil des Gesamtverbrauchs, der durch PV gedeckt wird
        "autarkiegrad": autarkiegrad,
    })

    # Einspeisevergütung für erweiterte Berechnungen definieren
    feed_in_tariff_effective = results["einspeiseverguetung_eur_per_kwh"]

    # Steuerlicher Vorteil (optional, falls gewerblich)
    tax_benefit_feed_in_year1 = 0.0
    income_tax_rate_percent = float(
        customer_data.get("income_tax_rate_percent", 0.0) or 0.0
    )
    if (
        customer_data.get("type", "Privat").lower() == "gewerblich"
        and income_tax_rate_percent > 0
    ):
        tax_benefit_feed_in_year1 = annual_feed_in_revenue_year1 * (
            income_tax_rate_percent / 100.0
        )  # Vereinfachte Annahme
    results["tax_benefit_feed_in_year1"] = tax_benefit_feed_in_year1

    annual_financial_benefit_year1 = (
        annual_electricity_cost_savings_self_consumption_year1
        + annual_feed_in_revenue_year1
        + tax_benefit_feed_in_year1
    )
    results["annual_financial_benefit_year1"] = annual_financial_benefit_year1
    # Verwende finalen Angebotspreis aus Solar Calculator falls verfügbar
    final_investment_amount = total_investment_netto

    # Prüfe ob finale Preise aus project_details verfügbar sind (direkt aus
    # Parameter)
    try:
        # project_details ist bereits als Parameter verfügbar
        if project_details:
            # Priorität: Preisänderungen > Provision > Basis
            if project_details.get('final_modified_price_net'):
                final_investment_amount = float(
                    project_details['final_modified_price_net'])
                print(
                    f"DEBUG: Amortisation verwendet final_modified_price_net: {final_investment_amount}")
            elif project_details.get('final_price_with_provision'):
                final_investment_amount = float(
                    project_details['final_price_with_provision'])
                print(
                    f"DEBUG: Amortisation verwendet final_price_with_provision: {final_investment_amount}")
            elif project_details.get('final_offer_price_net'):
                final_investment_amount = float(
                    project_details['final_offer_price_net'])
                print(
                    f"DEBUG: Amortisation verwendet final_offer_price_net: {final_investment_amount}")
            else:
                print(
                    f"DEBUG: Amortisation verwendet Fallback total_investment_netto: {final_investment_amount}")
        else:
            print(
                f"DEBUG: Amortisation - keine project_details gefunden, verwende Fallback: {final_investment_amount}")

    except Exception as e:
        # Fallback auf ursprüngliche Berechnung
        print(f"DEBUG: Amortisation Exception: {e}")

    amortization_time_calc = (
        final_investment_amount / annual_financial_benefit_year1
        if annual_financial_benefit_year1 > 0
        else float("inf")
    )
    # Basis-Amortisationszeit speichern
    results["amortization_time_years"] = amortization_time_calc
    # Admin-Cheat anwenden (falls aktiviert)
    try:
        cheat_settings = real_load_admin_setting(
            "amortization_cheat_settings", None)
        if isinstance(cheat_settings, dict) and cheat_settings.get("enabled"):
            mode = cheat_settings.get("mode", "fixed")
            cheated_value_years = cheat_settings.get("value_years")
            cheated_percent = cheat_settings.get("percent")
            original = results.get(
                "amortization_time_years",
                amortization_time_calc)
            cheated = None
            if mode == "fixed":
                try:
                    val = float(cheated_value_years)
                    if val > 0:
                        cheated = val
                except (TypeError, ValueError):
                    cheated = None
            elif mode == "absolute_reduction":
                try:
                    red = float(cheated_value_years)
                    if red > 0 and original != float("inf"):
                        cheated = max(0.1, original - red)
                except (TypeError, ValueError):
                    cheated = None
            elif mode == "percentage_reduction":
                try:
                    pct = float(cheated_percent)
                    if original != float("inf"):
                        pct = min(95.0, max(0.0, pct))
                        cheated = max(0.1, original * (1 - pct / 100.0))
                except (TypeError, ValueError):
                    cheated = None
            if cheated is not None:
                results["amortization_time_years_original"] = original
                results["amortization_time_years"] = cheated
    except Exception:
        # Cheat-Einstellungen ignorieren, falls Fehler
        pass

    # --- Simulation über die Jahre ---
    cash_flows_initial_investment = [
        -total_investment_netto
    ]  # Jahr 0 ist die Investition
    (
        annual_productions_sim_list,
        annual_benefits_sim_list,
        annual_maintenance_costs_sim_list,
    ) = ([], [], [])
    (
        annual_cash_flows_yearly_list,
        annual_elec_prices_sim_list,
        annual_feed_in_tariffs_sim_list,
    ) = ([], [], [])
    annual_revenue_from_feed_in_sim_list = []  # Für detailliertere Analyse

    # Wartungskosten
    maintenance_fixed_pa = float(
        global_constants.get("maintenance_fixed_eur_pa", 0.0) or 0.0
    )
    maintenance_variable_pa_kwp = float(
        global_constants.get("maintenance_variable_eur_per_kwp_pa", 0.0) or 0.0
    )
    maintenance_increase_pa_rate = (
        float(
            global_constants.get(
                "maintenance_increase_percent_pa", inflation_rate_percent
            )
            or inflation_rate_percent
        )
        / 100.0
    )  # Kopplung an Inflation als Default
    maintenance_base_percent_of_invest = (
        float(
            global_constants.get(
                "maintenance_costs_base_percent",
                1.5) or 1.5) / 100.0)

    annual_maintenance_costs_eur_year1_calc = 0.0
    if (
        maintenance_fixed_pa > 0 or maintenance_variable_pa_kwp > 0
    ):  # Wenn spezifische Werte da sind
        annual_maintenance_costs_eur_year1_calc = maintenance_fixed_pa + (
            maintenance_variable_pa_kwp * results["anlage_kwp"]
        )
    else:  # Fallback auf Prozentsatz der Investition
        annual_maintenance_costs_eur_year1_calc = (
            base_matrix_price_netto * maintenance_base_percent_of_invest
        )
        # if app_debug_mode_is_enabled: # Bereinigt
        # if (maintenance_increase_pa_rate * 100) == inflation_rate_percent: errors_list.append(texts.get("info_maintenance_increase_uses_inflation", "Info: Steigerung Wartungskosten an Inflationsrate gekoppelt."))
        # if maintenance_base_percent_of_invest * 100 > 0 : errors_list.append(texts.get("info_maintenance_fallback_used", "Info: Detaillierte Wartungskosten nicht gesetzt, Fallback auf % der Investition."))
    results["annual_maintenance_costs_eur_year1"] = (
        annual_maintenance_costs_eur_year1_calc
    )

    # Wartungskosten für erweiterte Berechnungen definieren
    maintenance_cost_fixed_pa = annual_maintenance_costs_eur_year1_calc

    for year_idx in range(1, results["simulation_period_years_effective"] + 1):
        current_year_production = annual_pv_production_kwh * (
            annual_degredation_factor ** (year_idx - 1)
        )
        annual_productions_sim_list.append(current_year_production)

        # Annahme: Anteile von EV und Einspeisung bleiben über die Jahre
        # relativ konstant zur Produktion
        ev_anteil_an_prod_j1 = (
            eigenverbrauch_pro_jahr_kwh / annual_pv_production_kwh
            if annual_pv_production_kwh > 0
            else 0
        )
        einspeisung_anteil_an_prod_j1 = (
            netzeinspeisung_kwh / annual_pv_production_kwh
            if annual_pv_production_kwh > 0
            else 0
        )

        current_year_ev = current_year_production * ev_anteil_an_prod_j1
        current_year_einspeisung = (
            current_year_production * einspeisung_anteil_an_prod_j1
        )

        elec_price_sim = electricity_price_kwh * (
            (1 + results["electricity_price_increase_rate_effective_percent"] / 100.0)
            ** (year_idx - 1)
        )
        annual_elec_prices_sim_list.append(elec_price_sim)

        feed_in_tariff_sim = results[
            "einspeiseverguetung_eur_per_kwh"
        ]  # Annahme: fester Tarif für EEG-Zeitraum
        if year_idx > int(
            global_constants.get("einspeiseverguetung_period_years", 20) or 20
        ):  # Nach EEG-Vergütungszeitraum
            feed_in_tariff_sim = float(
                global_constants.get(
                    "marktwert_strom_eur_per_kwh_after_eeg",
                    0.03) or 0.03)  # Marktwert
        annual_feed_in_tariffs_sim_list.append(feed_in_tariff_sim)

        cost_savings_sim = current_year_ev * elec_price_sim
        feed_in_rev_sim = current_year_einspeisung * feed_in_tariff_sim
        annual_revenue_from_feed_in_sim_list.append(
            feed_in_rev_sim
        )  # Speichern für Details

        tax_benefit_sim = (
            feed_in_rev_sim * (income_tax_rate_percent / 100.0)
            if customer_data.get("type", "Privat").lower() == "gewerblich"
            else 0.0
        )
        maint_costs_sim = annual_maintenance_costs_eur_year1_calc * (
            (1 + maintenance_increase_pa_rate) ** (year_idx - 1)
        )
        annual_maintenance_costs_sim_list.append(maint_costs_sim)

        annual_benefit_this_year = cost_savings_sim + feed_in_rev_sim + tax_benefit_sim
        annual_benefits_sim_list.append(annual_benefit_this_year)

        cash_flow_this_year = annual_benefit_this_year - maint_costs_sim
        cash_flows_initial_investment.append(
            cash_flow_this_year)  # Für IRR und NPV
        annual_cash_flows_yearly_list.append(
            cash_flow_this_year
        )  # Nur die jährlichen CFs

    results.update(
        {
            "annual_productions_sim": annual_productions_sim_list,
            "annual_benefits_sim": annual_benefits_sim_list,
            "annual_maintenance_costs_sim": annual_maintenance_costs_sim_list,
            # Jährliche CFs (ohne Jahr 0)
            "annual_cash_flows_sim": annual_cash_flows_yearly_list,
            "cumulative_cash_flows_sim": np.cumsum(
                cash_flows_initial_investment
            ).tolist(),  # Kumulierte CFs (inkl. Jahr 0)
            "annual_elec_prices_sim": annual_elec_prices_sim_list,  # Strompreise pro Jahr
            # Einspeisevergütung pro Jahr
            "annual_feed_in_tariffs_sim": annual_feed_in_tariffs_sim_list,
            # Jährliche Einnahmen aus Einspeisung
            "annual_revenue_from_feed_in_sim": annual_revenue_from_feed_in_sim_list,
        }
    )

    # --- Weitere Kennzahlen ---
    # Nettobarwert (NPV)
    npv_value = -cash_flows_initial_investment[0]  # Investition in Jahr 0
    discount_rate_npv = loan_interest_rate_percent / \
        100.0  # Kalkulatorischer Zinssatz
    for i_npv, cf_val in enumerate(
            cash_flows_initial_investment[1:], 1):  # Ab Jahr 1
        npv_value += cf_val / ((1 + discount_rate_npv) ** i_npv)
    results["npv_value"] = npv_value
    results["npv_per_kwp"] = (
        npv_value /
        results["anlage_kwp"] if results["anlage_kwp"] > 0 else float("nan"))

    # Interner Zinsfuß (IRR)
    try:
        import numpy_financial as npf

        irr_val = npf.irr(
            cash_flows_initial_investment
        )  # Benötigt Cashflows inkl. initialer Investition
        results["irr_percent"] = (
            irr_val *
            100 if irr_val is not None and not (
                math.isnan(irr_val) or math.isinf(irr_val)) else float("nan"))
    except ImportError:
        results["irr_percent"] = float("nan")
        errors_list.append(
            texts.get(
                "warn_numpy_financial_missing_for_irr",
                "Hinweis: numpy_financial nicht installiert, IRR kann nicht berechnet werden.",
            ))
    except (
        Exception
    ) as e_irr_calc:  # Fängt auch ValueError von npf.irr ab, wenn keine Lösung gefunden
        results["irr_percent"] = float("nan")
        errors_list.append(
            (
                texts.get(
                    "error_irr_calculation",
                    "Fehler bei IRR-Berechnung: {error_details}",
                )
                or ""
            ).format(error_details=str(e_irr_calc))
        )

    # Stromgestehungskosten (LCOE)
    total_discounted_costs_lcoe = total_investment_netto  # Kosten in Jahr 0
    total_discounted_production_lcoe = 0.0
    discount_rate_lcoe = (
        loan_interest_rate_percent / 100.0
    )  # Gleicher Diskontsatz wie NPV
    if annual_productions_sim_list and annual_maintenance_costs_sim_list:
        for y_idx in range(
            min(
                len(annual_productions_sim_list),
                len(annual_maintenance_costs_sim_list),
                results["simulation_period_years_effective"],
            )
        ):
            total_discounted_production_lcoe += annual_productions_sim_list[y_idx] / (
                (1 + discount_rate_lcoe) ** (y_idx + 1))
            total_discounted_costs_lcoe += annual_maintenance_costs_sim_list[y_idx] / (
                (1 + discount_rate_lcoe) ** (y_idx + 1)
            )  # Diskontierte Wartungskosten addieren
    results["lcoe_euro_per_kwh"] = (
        total_discounted_costs_lcoe / total_discounted_production_lcoe
        if total_discounted_production_lcoe > 0
        else float("inf")
    )
    results["effektiver_pv_strompreis_ct_kwh"] = (
        results["lcoe_euro_per_kwh"] * 100
        if results["lcoe_euro_per_kwh"] != float("inf")
        else float("inf")
    )

    # Einfache Rentabilität (ROI) für Jahr 1
    results["simple_roi_percent"] = (
        (annual_financial_benefit_year1 / total_investment_netto * 100)
        if total_investment_netto > 0
        else float("inf")
    )

    # Performance Ratio (PR) - Annahme: Referenzwert aus global_constants
    ref_specific_yield_for_pr = float(
        global_constants.get("reference_specific_yield_pr", 1100.0) or 1100.0
    )
    current_specific_yield = (
        results.get("specific_annual_yield_kwh_per_kwp", 0.0) or 0.0
    )
    if current_specific_yield > 0 and ref_specific_yield_for_pr > 0:
        pr_calculated = (current_specific_yield /
                         ref_specific_yield_for_pr) * 100
        results["performance_ratio_percent"] = min(
            max(pr_calculated, 50.0), 95.0
        )  # Begrenzung auf plausiblen Bereich
    else:
        results["performance_ratio_percent"] = float(
            global_constants.get(
                "default_performance_ratio_percent",
                78.0) or 78.0)  # Fallback auf Default PR

    # AfA und Restwert
    afa_period_years = int(global_constants.get("afa_period_years", 20) or 20)
    results["afa_linear_pa_eur"] = (
        total_investment_netto /
        afa_period_years if afa_period_years > 0 else 0.0)
    results["restwert_anlage_eur_nach_laufzeit"] = max(0.0, total_investment_netto - (
        results["afa_linear_pa_eur"] * results["simulation_period_years_effective"]), )

    # Eigenkapitalrendite (ROE) - hier vereinfacht als IRR, da keine
    # Fremdfinanzierung modelliert
    results["eigenkapitalrendite_roe_pct"] = results["irr_percent"]

    # Alternativanlage
    alternative_investment_interest_rate_percent = float(global_constants.get(
        "alternative_investment_interest_rate_percent", 5.0) or 5.0)
    results["alternativanlage_kapitalwert_eur"] = total_investment_netto * (
        (1 + alternative_investment_interest_rate_percent / 100.0)
        ** results["simulation_period_years_effective"]
    )

    # CO2-Einsparungen
    co2_emission_factor_kg_per_kwh = float(
        global_constants.get("co2_emission_factor_kg_per_kwh", 0.474) or 0.474
    )
    annual_co2_savings_kg = (
        annual_pv_production_kwh * co2_emission_factor_kg_per_kwh
    )  # Für Jahr 1
    results["annual_co2_savings_kg"] = annual_co2_savings_kg
    co2_per_tree = float(
        global_constants.get(
            "co2_per_tree_kg_pa",
            12.5) or 12.5)
    results["co2_equivalent_trees_per_year"] = (
        annual_co2_savings_kg / co2_per_tree if co2_per_tree > 0 else 0.0
    )
    co2_per_car = float(
        global_constants.get(
            "co2_per_car_km_kg",
            0.12) or 0.12)
    results["co2_equivalent_car_km_per_year"] = (
        annual_co2_savings_kg / co2_per_car if co2_per_car > 0 else 0.0
    )
    co2_per_flight = float(
        global_constants.get("co2_per_flight_muc_pmi_kg", 180.0) or 180.0
    )
    results["co2_equivalent_flights_muc_pmi_per_year"] = (
        annual_co2_savings_kg / co2_per_flight if co2_per_flight > 0 else 0.0
    )
    total_co2_savings_over_lifetime_kg = (
        sum(annual_productions_sim_list) if annual_productions_sim_list else 0
    ) * co2_emission_factor_kg_per_kwh
    results["co2_avoidance_cost_euro_per_tonne"] = (
        (total_investment_netto / (total_co2_savings_over_lifetime_kg / 1000.0))
        if total_co2_savings_over_lifetime_kg > 0
        else float("inf")
    )

    # E-Auto und Wärmepumpe (vereinfachte Betrachtung)
    if project_details.get("future_ev", False):  # Wenn E-Auto geplant ist
        eauto_annual_km_calc = float(
            global_constants.get("eauto_annual_km", 10000) or 10000
        )
        eauto_consumption_kwh_per_100km_calc = float(
            global_constants.get("eauto_consumption_kwh_per_100km", 18) or 18
        )
        future_ev_consump_kwh_calc = (
            eauto_annual_km_calc / 100.0
        ) * eauto_consumption_kwh_per_100km_calc
        eauto_pv_share_percent_calc = float(
            global_constants.get("eauto_pv_share_percent", 30) or 30
        )
        # Max. was PV für EV liefern kann, ist der geringere Wert aus PV-Anteil
        # am EV-Verbrauch und der gesamten PV-Produktion (die nicht schon für
        # Haushalt weg ist)
        results["eauto_ladung_durch_pv_kwh"] = min(
            future_ev_consump_kwh_calc * (eauto_pv_share_percent_calc / 100.0),
            annual_pv_production_kwh,
        )  # Vereinfacht: nimmt von Gesamtproduktion
    else:
        results["eauto_ladung_durch_pv_kwh"] = 0.0

    if project_details.get("future_hp", False):  # Wenn Wärmepumpe geplant ist
        waermebedarf_heizung_kwh_calc = float(
            project_details.get("consumption_heating_kwh_yr", 0) or 0
        )  # Wärmebedarf = Verbrauch Heizung
        hp_cop_calc = float(
            global_constants.get(
                "heatpump_cop_factor",
                3.5) or 3.5)
        future_hp_consump_kwh_calc = (
            waermebedarf_heizung_kwh_calc /
            hp_cop_calc if hp_cop_calc > 0 else 0)  # Stromverbrauch der WP
        hp_pv_share_percent_calc = float(
            global_constants.get("heatpump_pv_share_percent", 40) or 40
        )
        potential_hp_coverage_by_pv_kwh_calc = future_hp_consump_kwh_calc * (
            hp_pv_share_percent_calc / 100.0
        )
        # PV-Deckungsgrad für WP: Wie viel vom WP-Strombedarf kann die PV
        # decken?
        results["pv_deckungsgrad_wp_pct"] = (
            (min(
                potential_hp_coverage_by_pv_kwh_calc,
                annual_pv_production_kwh) /
                future_hp_consump_kwh_calc *
                100) if future_hp_consump_kwh_calc > 0 else 0.0)
    else:
        results["pv_deckungsgrad_wp_pct"] = 0.0

    # Kostenhochrechnung ohne PV
    annual_costs_hochrechnung_values_calc = []
    total_projected_costs_with_increase_calc = 0.0
    total_projected_costs_without_increase_calc = 0.0
    base_consumption_for_projection_calc = (
        project_details.get("annual_consumption_kwh_yr", 0.0) or 0.0
    ) + (project_details.get("consumption_heating_kwh_yr", 0.0) or 0.0)
    base_price_for_projection_calc = float(
        project_details.get("electricity_price_kwh", 0.30) or 0.30
    )
    # if base_consumption_for_projection_calc==0 and results['anlage_kwp']>0 and app_debug_mode_is_enabled: errors_list.append(texts.get("warn_zero_consumption_for_projection","Warnung: Gesamtjahresverbrauch für Kostenhochrechnung ist 0 kWh.")) # Bereinigt
    # if base_price_for_projection_calc==0 and results['anlage_kwp']>0 and
    # base_consumption_for_projection_calc > 0 and app_debug_mode_is_enabled:
    # errors_list.append(texts.get("warn_zero_price_for_projection","Warnung:
    # Strompreis für Kostenhochrechnung ist 0 €/kWh.")) # Bereinigt
    for year_proj_calc in range(results["simulation_period_years_effective"]):
        cost_this_year_proj_calc = (
            base_consumption_for_projection_calc *
            base_price_for_projection_calc *
            (
                (1 +
                 results["electricity_price_increase_rate_effective_percent"] /
                 100.0) ** year_proj_calc))
        annual_costs_hochrechnung_values_calc.append(cost_this_year_proj_calc)
        total_projected_costs_with_increase_calc += cost_this_year_proj_calc
        total_projected_costs_without_increase_calc += (
            base_consumption_for_projection_calc *
            base_price_for_projection_calc)
    results["annual_costs_hochrechnung_values"] = annual_costs_hochrechnung_values_calc
    results["annual_costs_hochrechnung_jahre_effektiv"] = results[
        "simulation_period_years_effective"
    ]
    results["annual_costs_hochrechnung_steigerung_effektiv_prozent"] = results[
        "electricity_price_increase_rate_effective_percent"
    ]
    results["total_projected_costs_with_increase"] = (
        total_projected_costs_with_increase_calc
    )
    results["total_projected_costs_without_increase"] = (
        total_projected_costs_without_increase_calc
    )

    # Break-Even Analyse
    try:
        break_even_analyzer = BreakEvenAnalysis(
            investment=total_investment_brutto,
            annual_savings=annual_financial_benefit_year1,
            inflation_rate=inflation_rate_percent,
            electricity_price_increase=results[
                "electricity_price_increase_rate_effective_percent"
            ],
        )
        results["break_even_scenarios"] = break_even_analyzer.calculate_scenarios()
    except Exception as e:
        if errors_list is not None:
            errors_list.append(f"Fehler bei Break-Even Analyse: {str(e)}")

    # Energiepreisvergleich
    try:
        energy_price_comparator = EnergyPriceComparison(
            current_consumption=annual_consumption_kwh_yr,
            current_price=electricity_price_kwh,
            pv_production=annual_pv_production_kwh,
            self_consumption=eigenverbrauch_pro_jahr_kwh,
            feed_in_rate=feed_in_tariff_effective,
        )
        sample_tariffs = [
            {"name": "Aktueller Tarif", "price_per_kwh": electricity_price_kwh},
            {"name": "Ökostromtarif", "price_per_kwh": electricity_price_kwh * 1.1},
            {"name": "Grundversorgung", "price_per_kwh": electricity_price_kwh * 0.95},
        ]
        results["energy_price_comparison"] = energy_price_comparator.compare_tariffs(
            sample_tariffs)
    except Exception as e:
        if errors_list is not None:
            errors_list.append(f"Fehler bei Energiepreisvergleich: {str(e)}")

    # Technische Degradation
    try:
        degradation_analyzer = TechnicalDegradation(
            initial_power=anlage_kwp * 1000,  # Umrechnung in Watt
            annual_degradation=annual_module_degradation_percent,
            warranty_years=25,  # Standard 25 Jahre
            warranty_power=80,  # Standard 80% nach Garantiezeit
        )
        results["degradation_analysis"] = degradation_analyzer.calculate_degradation(
            years=results["simulation_period_years_effective"])
    except Exception as e:
        if errors_list is not None:
            errors_list.append(f"Fehler bei Degradationsanalyse: {str(e)}")

    # Wartungsplan
    try:
        components = [
            {
                "name": "Wechselrichter",
                "maintenance_interval_months": 12,
                "maintenance_cost": maintenance_cost_fixed_pa
                / 2,  # Hälfte der jährlichen Wartungskosten
                "last_maintenance_date": datetime.now().strftime("%Y-%m-%d"),
            },
            {
                "name": "PV-Module",
                "maintenance_interval_months": 6,
                "maintenance_cost": maintenance_cost_fixed_pa
                / 2,  # Andere Hälfte der jährlichen Wartungskosten
                "last_maintenance_date": datetime.now().strftime("%Y-%m-%d"),
            },
        ]

        # Speicherkomponente nur hinzufügen, wenn ein Speicher vorhanden ist
        if include_storage and selected_storage_capacity_kwh > 0:
            components.append(
                {
                    "name": "Speichersystem",
                    "maintenance_interval_months": 12,
                    "maintenance_cost": maintenance_cost_fixed_pa
                    * 0.2,  # 20% der jährlichen Wartungskosten
                    "last_maintenance_date": datetime.now().strftime("%Y-%m-%d"),
                }
            )

        maintenance_monitor = MaintenanceMonitoring(
            components=components,
            installation_date=datetime.now().strftime("%Y-%m-%d"))
        results["maintenance_schedule"] = (
            maintenance_monitor.generate_maintenance_schedule()
        )
    except Exception as e:
        if errors_list is not None:
            errors_list.append(f"Fehler bei Wartungsplanerstellung: {str(e)}")

    # Standardwerte für Diagrammdaten-Keys setzen, falls sie nicht explizit berechnet wurden
    # Dies ist wichtig, damit analysis.py nicht auf nicht existierende Keys
    # zugreift.
    chart_data_keys_to_ensure = [
        "monthly_prod_cons_chart_bytes",
        "cumulative_cashflow_chart_bytes",
        "pv_usage_chart_bytes",
        "consumption_coverage_chart_bytes",
        "cost_overview_chart_bytes",
        "cost_projection_chart_bytes",
        "break_even_scenarios_chart_bytes",
        "technical_degradation_chart_bytes",
        "maintenance_schedule_chart_bytes",
        "energy_price_comparison_chart_bytes",
    ]
    for chart_key_init_final in chart_data_keys_to_ensure:
        results.setdefault(chart_key_init_final, None)

    # Finale Kennzahlen für die Darstellung
    results["self_supply_rate_percent"] = (
        (eigenverbrauch_pro_jahr_kwh / annual_consumption_kwh_yr * 100)
        if annual_consumption_kwh_yr > 0
        else 0.0
    )
    results["grid_consumption_rate_percent"] = (
        100.0 - results["self_supply_rate_percent"]
    )  # Anteil Netzbezug am Gesamtverbrauch
    results["direktverbrauch_anteil_pv_produktion_pct"] = (
        (sum(monthly_direct_self_consumption_kwh) /
         annual_pv_production_kwh *
         100) if annual_pv_production_kwh > 0 else 0.0)
    results["speichernutzung_anteil_pv_produktion_pct"] = (
        (sum(monthly_storage_discharge_for_sc_kwh) / annual_pv_production_kwh * 100)
        if annual_pv_production_kwh > 0
        else 0.0
    )  # Anteil Speichernutzung an PV-Produktion

    # Speicherbezogene Kennzahlen
    if include_storage and selected_storage_capacity_kwh > 0:
        # Speichergrad / Deckungsgrad durch Speicher (Anteil des
        # Gesamtverbrauchs, der aus dem Speicher gedeckt wird)
        results["speichergrad_deckungsgrad_speicher_pct"] = (
            (
                sum(monthly_storage_discharge_for_sc_kwh)
                / annual_consumption_kwh_yr
                * 100
            )
            if annual_consumption_kwh_yr > 0
            else 0.0
        )
        # Optimale Speichergröße (Heuristik)
        optimal_storage_factor_calc = float(
            global_constants.get("optimal_storage_factor", 1.0) or 1.0
        )  # z.B. 1 kWh Speicher pro 1000 kWh Jahresverbrauch
        results["optimale_speichergröße_kwh_geschaetzt"] = (
            (annual_consumption_kwh_yr / 1000.0) * optimal_storage_factor_calc
            if annual_consumption_kwh_yr > 0
            else 0.0
        )
        # Notstromkapazität (vereinfacht als Speicherkapazität)
        results["notstromkapazitaet_kwh_pro_tag"] = (
            selected_storage_capacity_kwh  # Annahme: gesamter Speicher für Notstrom nutzbar
        )
        # Batterielebensdauer
        storage_max_cycles_calc = 0.0
        if storage_details_from_db:
            storage_max_cycles_raw_val = storage_details_from_db.get(
                "max_cycles"
            )  # Aus Produktdatenbank
            # Fallback, falls 'max_cycles' nicht in DB ist oder 0
            default_cycles_from_product_db_val = 6000  # Ein typischer Wert
            cycles_per_year_for_default_from_constants_val = float(
                global_constants.get("storage_cycles_per_year", 250) or 250
            )
            calculated_default_max_cycles_val = default_cycles_from_product_db_val
            if (
                cycles_per_year_for_default_from_constants_val > 0
                and results["simulation_period_years_effective"] > 0
            ):  # Sicherstellen, dass Divisor > 0
                calculated_default_max_cycles_val = (
                    cycles_per_year_for_default_from_constants_val
                    * results["simulation_period_years_effective"]
                )  # Alternative: Zyklen über Lebensdauer

            if storage_max_cycles_raw_val is None:  # Kein Wert in DB
                storage_max_cycles_calc = calculated_default_max_cycles_val
            else:
                try:
                    storage_max_cycles_val_conv = float(
                        storage_max_cycles_raw_val)
                    storage_max_cycles_calc = (
                        storage_max_cycles_val_conv
                        if storage_max_cycles_val_conv > 0
                        else calculated_default_max_cycles_val
                    )
                except (ValueError, TypeError):  # Wenn Konvertierung fehlschlägt
                    storage_max_cycles_calc = calculated_default_max_cycles_val

        storage_cycles_per_year_val_calc = float(
            global_constants.get("storage_cycles_per_year", 250) or 250
        )  # Zyklen pro Jahr
        if storage_max_cycles_calc > 0 and storage_cycles_per_year_val_calc > 0:
            results["batterie_lebensdauer_geschaetzt_jahre"] = (
                storage_max_cycles_calc / storage_cycles_per_year_val_calc
            )
        else:
            results["batterie_lebensdauer_geschaetzt_jahre"] = float(
                "inf"
            )  # Wenn keine Zyklenangabe oder keine Nutzung
    else:  # Keine Speicherlogik
        (
            results["speichergrad_deckungsgrad_speicher_pct"],
            results["optimale_speichergröße_kwh_geschaetzt"],
            results["notstromkapazitaet_kwh_pro_tag"],
            results["batterie_lebensdauer_geschaetzt_jahre"],
        ) = (0.0, 0.0, 0.0, 0.0)

    # Verschattungsverlust (aus Eingabe übernehmen)
    results["verschattungsverlust_pct"] = float(
        project_details.get("verschattungsverlust_pct", 0.0) or 0.0
    )

    # *** ERWEITERTE PV-BERECHNUNGEN INTEGRIEREN ***
    if PV_CALCULATIONS_CORE_AVAILABLE:
        try:
            # Daten für erweiterte Berechnung vorbereiten
            extended_calc_data = {
                "anlage_kwp": results.get("anlage_kwp", 0),
                "annual_pv_production_kwh": results.get("annual_pv_production_kwh", 0),
                "annual_consumption_kwh": results.get("gesamtverbrauch_kwh", 4000),
                "self_consumption_kwh": results.get("eigenverbrauch_kwh", 0),
                "total_investment_netto": results.get("total_investment_netto", 20000),
                "electricity_price_eur_kwh": results.get("stromtarif_eur_kwh", 0.30),
                "feed_in_tariff_eur_kwh": results.get("einspeiseverguetung_eur_kwh", 0.08),
                "storage_capacity_kwh": results.get("speicherkapazitaet_kwh", 0),
                "customer_type": customer_data.get("customer_type", "private"),
            }

            # Umfassende PV-Analyse durchführen
            extended_results = calculate_comprehensive_pv_analysis(
                extended_calc_data)

            # Erweiterte Ergebnisse zu den Hauptergebnissen hinzufügen
            results.update(
                {
                    "pv_calculations_core_results": extended_results, "extended_npv_eur": extended_results.get(
                        "npv_eur", 0), "extended_irr_percent": extended_results.get(
                        "irr_percent", 0), "extended_payback_years": extended_results.get(
                        "payback_period_years", float('inf')), "extended_annual_co2_savings_kg": extended_results.get(
                        "annual_co2_savings_kg", 0), "extended_co2_payback_years": extended_results.get(
                            "co2_payback_years", 0), "monte_carlo_success_probability": extended_results.get(
                                "monte_carlo_analysis", {}).get(
                                    "success_probability", 0), "optimization_suggestions_available": bool(
                                        extended_results.get(
                                            "optimization_suggestions", {}).get(
                                                "top_recommendations", [])), })

            # Detaillierte CO2-Analyse verfügbar machen
            if "detailed_co2_analysis" in extended_results:
                co2_analysis = extended_results["detailed_co2_analysis"]
                results.update({
                    "co2_total_savings_lifetime_tons": co2_analysis.get("total_co2_savings", 0),
                    "co2_tree_equivalent": co2_analysis.get("tree_equivalent", 0),
                    "co2_car_km_equivalent": co2_analysis.get("car_km_equivalent", 0),
                })

            if app_debug_mode_is_enabled:
                print("CALC: Erweiterte PV-Berechnungen erfolgreich integriert")

        except Exception as e:
            error_msg = f"Fehler bei erweiterten PV-Berechnungen: {str(e)}"
            errors_list.append(error_msg)
            if app_debug_mode_is_enabled:
                print(f"CALC: {error_msg}")
    else:
        if app_debug_mode_is_enabled:
            print(
                "CALC: Erweiterte PV-Berechnungen nicht verfügbar (pv_calculations_core nicht geladen)")

    # if app_debug_mode_is_enabled: print(f"--- CALCULATIONS.PY: Berechnungen abgeschlossen. Ergebnisse (Auszug): {json.dumps({k: v for k,v in results.items() if not isinstance(v, list) or len(v) < 5}, indent=2, ensure_ascii=False)}") # Bereinigt
    # if app_debug_mode_is_enabled and errors_list: print(f"CALC: Gesammelte
    # Fehler/Hinweise: {errors_list}") # Bereinigt

    # *** BACKUP-SYSTEM: Speichere Ergebnisse in Session State mit Zeitstempel ***
    try:
        import streamlit as st

        if hasattr(st, "session_state"):
            # Zeitstempel für dieses Berechnungsergebnis
            timestamp = datetime.now().isoformat()

            # Speichere Hauptergebnisse
            st.session_state.calculation_results = results.copy()

            # Update enhanced pricing if components are available
            _update_enhanced_pricing_in_calculation_results(results)

            # Erstelle Backup-Kopie mit Zeitstempel
            backup_data = {
                "results": results.copy(),
                "timestamp": timestamp,
                "project_data_summary": {
                    "anlage_kwp": results.get("anlage_kwp", 0),
                    "total_investment_brutto": results.get(
                        "total_investment_brutto", 0
                    ),
                    "annual_pv_production_kwh": results.get(
                        "annual_pv_production_kwh", 0
                    ),
                },
            }
            st.session_state.calculation_results_backup = backup_data

            # Speichere zusätzlich einen Timestamp für Debugging
            st.session_state.calculation_timestamp = timestamp

            if app_debug_mode_is_enabled:
                print(
                    f"CALC: Berechnungsergebnisse in Session State gespeichert (Zeitstempel: {timestamp})")
    except ImportError:
        # Streamlit nicht verfügbar (z.B. bei direkter Ausführung)
        pass
    except Exception as e:
        if app_debug_mode_is_enabled:
            print(f"CALC: Fehler beim Speichern in Session State: {e}")

    return results


class BreakEvenAnalysis:
    """Break-Even Analyseklasse für Wirtschaftlichkeitsberechnungen"""

    def __init__(
            self,
            investment: float,
            annual_savings: float,
            inflation_rate: float,
            electricity_price_increase: float):
        self.investment = investment
        self.annual_savings = annual_savings
        self.inflation_rate = inflation_rate / \
            100.0 if inflation_rate > 1 else inflation_rate  # Normalisieren auf Dezimalwert
        self.electricity_price_increase = electricity_price_increase / \
            100.0 if electricity_price_increase > 1 else electricity_price_increase

    def calculate_scenarios(self) -> dict[str, Any]:
        """Berechnet verschiedene Break-Even Szenarien"""
        scenarios = {}

        try:
            # Einfacher Break-Even (ohne Inflation/Preissteigerung)
            if self.annual_savings > 0:
                simple_break_even = self.investment / self.annual_savings
                scenarios["simple_break_even_years"] = round(
                    simple_break_even, 2)
            else:
                scenarios["simple_break_even_years"] = float('inf')

            # Break-Even mit Preissteigerung
            break_even_with_increase = self.calculate_break_even_with_price_increase()
            scenarios["break_even_with_price_increase_years"] = break_even_with_increase

            # Break-Even mit Inflation
            break_even_with_inflation = self.calculate_break_even_with_inflation()
            scenarios["break_even_with_inflation_years"] = break_even_with_inflation

            # Optimistisches Szenario (Preissteigerung + niedrigere Inflation)
            optimistic_break_even = self.calculate_optimistic_scenario()
            scenarios["optimistic_break_even_years"] = optimistic_break_even

            # Konservatives Szenario (höhere Inflation, niedrigere
            # Preissteigerung)
            conservative_break_even = self.calculate_conservative_scenario()
            scenarios["conservative_break_even_years"] = conservative_break_even

        except Exception as e:
            scenarios["error"] = f"Fehler bei Break-Even Berechnung: {str(e)}"

        return scenarios

    def calculate_break_even_with_price_increase(self) -> float:
        """Break-Even Berechnung mit Strompreissteigerung"""
        if self.annual_savings <= 0:
            return float('inf')

        cumulative_savings = 0
        year = 0
        max_years = 50  # Sicherheitslimit

        while cumulative_savings < self.investment and year < max_years:
            year += 1
            annual_savings_this_year = self.annual_savings * \
                ((1 + self.electricity_price_increase) ** (year - 1))
            cumulative_savings += annual_savings_this_year

        return round(year, 2) if year < max_years else float('inf')

    def calculate_break_even_with_inflation(self) -> float:
        """Break-Even Berechnung mit Inflation (Real-Betrachtung)"""
        if self.annual_savings <= 0:
            return float('inf')

        # Reale Einsparungen (inflationsbereinigt)
        real_annual_savings = self.annual_savings
        real_investment = self.investment

        cumulative_real_savings = 0
        year = 0
        max_years = 50

        while cumulative_real_savings < real_investment and year < max_years:
            year += 1
            # Nominale Einsparungen steigen mit Strompreissteigerung
            nominal_savings = self.annual_savings * \
                ((1 + self.electricity_price_increase) ** (year - 1))
            # Reale Einsparungen (inflationsbereinigt)
            real_savings_this_year = nominal_savings / \
                ((1 + self.inflation_rate) ** (year - 1))
            cumulative_real_savings += real_savings_this_year

        return round(year, 2) if year < max_years else float('inf')

    def calculate_optimistic_scenario(self) -> float:
        """Optimistisches Szenario mit erhöhter Strompreissteigerung"""
        optimistic_price_increase = self.electricity_price_increase * \
            1.2  # 20% höhere Preissteigerung

        if self.annual_savings <= 0:
            return float('inf')

        cumulative_savings = 0
        year = 0
        max_years = 50

        while cumulative_savings < self.investment and year < max_years:
            year += 1
            annual_savings_this_year = self.annual_savings * \
                ((1 + optimistic_price_increase) ** (year - 1))
            cumulative_savings += annual_savings_this_year

        return round(year, 2) if year < max_years else float('inf')

    def calculate_conservative_scenario(self) -> float:
        """Konservatives Szenario mit reduzierter Strompreissteigerung"""
        conservative_price_increase = self.electricity_price_increase * \
            0.7  # 30% niedrigere Preissteigerung
        higher_inflation = self.inflation_rate * 1.3  # 30% höhere Inflation

        if self.annual_savings <= 0:
            return float('inf')

        cumulative_real_savings = 0
        year = 0
        max_years = 50

        while cumulative_real_savings < self.investment and year < max_years:
            year += 1
            # Nominale Einsparungen mit konservativer Preissteigerung
            nominal_savings = self.annual_savings * \
                ((1 + conservative_price_increase) ** (year - 1))
            # Reale Einsparungen mit höherer Inflation
            real_savings_this_year = nominal_savings / \
                ((1 + higher_inflation) ** (year - 1))
            cumulative_real_savings += real_savings_this_year

        return round(year, 2) if year < max_years else float('inf')


class EnergyPriceComparison:
    """Energiepreisvergleichstool"""

    def __init__(
        self,
        current_consumption: float,
        current_price: float,
        pv_production: float,
        self_consumption: float,
        feed_in_rate: float,
    ):
        self.current_consumption = current_consumption
        self.current_price = current_price
        self.pv_production = pv_production
        self.self_consumption = self_consumption
        self.feed_in_rate = feed_in_rate

    def compare_tariffs(
        self, tariffs: list[dict[str, Any]]
    ) -> dict[str, list[dict[str, float]]]:
        base_cost = self.current_consumption * self.current_price
        pv_savings = self.self_consumption * self.current_price
        feed_in_revenue = (
            self.pv_production - self.self_consumption
        ) * self.feed_in_rate

        comparisons = []
        for tariff in tariffs:
            new_cost = (self.current_consumption -
                        self.self_consumption) * tariff["price_per_kwh"]
            total_cost = new_cost - feed_in_revenue
            savings = base_cost - total_cost
            savings_percent = (savings / base_cost) * \
                100 if base_cost > 0 else 0

            comparisons.append(
                {
                    "tariff_name": tariff["name"],
                    "total_cost_yearly": total_cost,
                    "savings_yearly": savings,
                    "savings_percent": savings_percent,
                }
            )

        return {"comparisons": comparisons}


class TechnicalDegradation:
    """Detaillierte Degradationsanalyse"""

    def __init__(
        self,
        initial_power: float,
        annual_degradation: float,
        warranty_years: int,
        warranty_power: float,
    ):
        self.initial_power = initial_power
        self.annual_degradation = annual_degradation
        self.warranty_years = warranty_years
        self.warranty_power = warranty_power

    def calculate_degradation(self, years: int = 25) -> dict[str, Any]:
        efficiency_by_year = []
        degradation_rate_by_year = []
        current_power = self.initial_power

        for year in range(years):
            # Guard gegen Division durch 0
            if self.initial_power and self.initial_power > 0:
                efficiency = (current_power / self.initial_power) * 100
            else:
                efficiency = 0.0
            efficiency_by_year.append(efficiency)

            if year < years - 1:
                next_power = current_power * \
                    (1 - self.annual_degradation / 100)
                # Wenn current_power 0 ist, setze Rate direkt auf
                # annual_degradation
                if current_power and current_power > 0:
                    degradation_rate = (
                        (current_power - next_power) / current_power) * 100
                else:
                    degradation_rate = self.annual_degradation
                degradation_rate_by_year.append(degradation_rate)
                current_power = next_power
            else:
                degradation_rate_by_year.append(self.annual_degradation)

        if self.initial_power and self.initial_power > 0:
            total_degradation = (
                (self.initial_power - current_power) / self.initial_power
            ) * 100
        else:
            total_degradation = 0.0
        warranty_compliance = current_power >= (
            self.warranty_power * self.initial_power / 100
        )

        return {
            "efficiency_by_year": efficiency_by_year,
            "degradation_rate_by_year": degradation_rate_by_year,
            "total_degradation_percent": total_degradation,
            "warranty_compliance": warranty_compliance,
        }


class MaintenanceMonitoring:
    """Wartungs- und Überwachungsmodul"""

    def __init__(
            self, components: list[dict[str, Any]], installation_date: str):
        self.components = components
        self.installation_date = datetime.strptime(
            installation_date, "%Y-%m-%d")

    def generate_maintenance_schedule(self) -> dict[str, Any]:
        maintenance_schedule = []
        total_annual_cost = 0

        for component in self.components:
            interval_months = component.get("maintenance_interval_months", 12)
            last_maintenance = component.get("last_maintenance_date")
            if last_maintenance:
                last_maintenance = datetime.strptime(
                    last_maintenance, "%Y-%m-%d")
            else:
                last_maintenance = self.installation_date

            next_maintenance = last_maintenance
            while next_maintenance < datetime.now():
                next_maintenance = datetime.fromtimestamp(
                    next_maintenance.timestamp() + (interval_months * 30 * 24 * 3600)
                )

            estimated_cost = component.get("maintenance_cost", 0)
            total_annual_cost += estimated_cost * (12 / interval_months)

            maintenance_schedule.append(
                {
                    "component": component["name"],
                    "last_maintenance": last_maintenance,
                    "next_maintenance": next_maintenance,
                    "interval_months": interval_months,
                    "priority": (
                        "Hoch"
                        if interval_months <= 6
                        else "Mittel" if interval_months <= 12 else "Niedrig"
                    ),
                    "estimated_cost": estimated_cost,
                }
            )

        return {
            "maintenance_schedule": sorted(
                maintenance_schedule, key=lambda x: x["next_maintenance"]
            ),
            "total_annual_cost": total_annual_cost,
        }


def calculate_offer_details(
    customer_id: int | None = None, project_data: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Berechnet detaillierte Angebotsdaten für einen Kunden.

    Args:
        customer_id: Optional - ID des Kunden
        project_data: Optional - Projektdaten für die Berechnung

    Returns:
        Dict mit Angebotsdaten
    """
    try:
        # Fallback-Projektdaten wenn nicht übergeben
        if not project_data:
            project_data = {
                "anlage_kwp": 10.0,
                "electricity_price_eur_per_kwh": 0.30,
                "annual_consumption_kwh": 4000,
                "storage_kwh": 10.0,
                "location": {"latitude": 50.0, "longitude": 10.0},
            }

        # Basis-Berechnungen durchführen
        calculation_errors = []
        results = perform_calculations(
            project_data, {}, calculation_errors)  # texts

        # Zusätzliche Angebotsdaten erstellen
        offer_details = {
            "customer_id": customer_id,
            "calculation_results": results,
            "project_data": project_data,
            "calculation_errors": calculation_errors,
            "generated_at": datetime.now().isoformat(),
            # Wichtige Kennzahlen für Angebot
            "total_investment": results.get("total_investment_brutto", 0),
            "annual_savings": results.get("annual_financial_benefit_year1", 0),
            "payback_time": results.get("amortization_time_years", 0),
            "annual_production": results.get("annual_pv_production_kwh", 0),
            "self_consumption_rate": results.get("self_supply_rate_percent", 0),
            "co2_savings_annual": results.get("co2_emission_avoided_kg_per_year", 0),
            # Finanzielle Details
            "financing_options": {
                "cash_payment": results.get("total_investment_brutto", 0),
                "financing_available": False,
                "monthly_rate_estimate": (
                    results.get("total_investment_brutto", 0) / 240
                    if results.get("total_investment_brutto", 0) > 0
                    else 0
                ),
            },
            # Komponenten
            "system_components": {
                "modules": f"{results.get('anlage_kwp', 0)} kWp PV-Module",
                "inverter": "Wechselrichter",
                "storage": (
                    f"{project_data.get('storage_kwh',
                                        0)} kWh Batteriespeicher"
                    if project_data.get("storage_kwh", 0) > 0
                    else None
                ),
                "installation": "Montage und Installation",
            },
        }

        return offer_details

    except Exception as e:
        return {
            "error": f"Fehler bei Angebotserstellung: {str(e)}",
            "customer_id": customer_id,
            "generated_at": datetime.now().isoformat(),
        }

# === SPEICHER-RELATIONEN BERECHNUNGEN ===


def calculate_storage_to_consumption_ratio(
        storage_capacity_kwh, daily_consumption_kwh):
    """
    Berechnet das Verhältnis der Speicherkapazität zum durchschnittlichen Tagesverbrauch

    Args:
        storage_capacity_kwh (float): Speicherkapazität in kWh
        daily_consumption_kwh (float): Durchschnittlicher Tagesverbrauch in kWh

    Returns:
        float: Prozentsatz der Speicherkapazität im Verhältnis zum Tagesverbrauch
    """
    if daily_consumption_kwh == 0:
        return 0
    return (storage_capacity_kwh / daily_consumption_kwh) * 100


def calculate_storage_to_production_ratio(
        storage_capacity_kwh,
        daily_pv_production_kwh):
    """
    Berechnet das Verhältnis der Speicherkapazität zur durchschnittlichen PV-Tagesproduktion

    Args:
        storage_capacity_kwh (float): Speicherkapazität in kWh
        daily_pv_production_kwh (float): Durchschnittliche PV-Tagesproduktion in kWh

    Returns:
        float: Prozentsatz der Speicherkapazität im Verhältnis zur PV-Tagesproduktion
    """
    if daily_pv_production_kwh == 0:
        return 0
    return (storage_capacity_kwh / daily_pv_production_kwh) * 100
