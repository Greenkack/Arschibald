#!/usr/bin/env python3
"""
calculation_bridge.py
Python bridge script for React-Electron calculations
Connects TypeScript PythonCalculationService with Python calculations.py

Usage:
    python calculation_bridge.py <json_payload_file>
"""

import json
import sys
import traceback
from pathlib import Path

from financial_calculations import calculate_payback_years

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Import our calculation modules
    import pandas as pd

    from calculations import perform_calculations

    # Try to import additional modules if they exist
    try:
        from product_db import get_battery_by_id, get_inverter_by_id, get_module_by_id
    except ImportError:
        print(
            "Warning: product_db module not available, using mock data",
            file=sys.stderr)

        def get_module_by_id(module_id): return None
        def get_inverter_by_id(inverter_id): return None
        def get_battery_by_id(battery_id): return None

except ImportError as e:
    print(f"Error importing Python modules: {e}", file=sys.stderr)
    sys.exit(1)


def convert_configuration_to_python_format(config):
    """
    Convert TypeScript SolarConfiguration to Python format
    Expected by calculations.py:perform_calculations
    """
    try:
        # Build modules data
        modules_data = []
        total_module_power_wp = 0

        for module in config.get('selectedModules', []):
            count = module.get('count', 1)
            power_wp = module.get('power_wp', 0)

            modules_data.append({
                'id': module.get('id'),
                'name': module.get('name', 'Unknown Module'),
                'manufacturer': module.get('manufacturer', 'Unknown'),
                'power_wp': power_wp,
                'price_netto': module.get('price_netto', 0),
                'count': count
            })

            total_module_power_wp += power_wp * count

        # Build inverters data
        inverters_data = []

        for inverter in config.get('selectedInverters', []):
            count = inverter.get('count', 1)

            inverters_data.append({
                'id': inverter.get('id'),
                'name': inverter.get('name', 'Unknown Inverter'),
                'manufacturer': inverter.get('manufacturer', 'Unknown'),
                'power_kw': inverter.get('power_kw', 0),
                'price_netto': inverter.get('price_netto', 0),
                'count': count
            })

        # Build batteries data
        batteries_data = []

        for battery in config.get('selectedBatteries', []):
            count = battery.get('count', 1)

            batteries_data.append({
                'id': battery.get('id'),
                'name': battery.get('name', 'Unknown Battery'),
                'manufacturer': battery.get('manufacturer', 'Unknown'),
                'capacity_kwh': battery.get('capacity_kwh', 0),
                'price_netto': battery.get('price_netto', 0),
                'count': count
            })

        # Build additional components
        additional_components = []

        for component in config.get('additionalComponents', []):
            additional_components.append({
                'id': component.get('id'),
                'name': component.get('name', 'Unknown Component'),
                'category': component.get('category', 'other'),
                'price_netto': component.get('price_netto', 0),
                'count': component.get('count', 1)
            })

        # Extract consumption data
        consumption_data = config.get('consumptionData', {})
        annual_consumption = consumption_data.get(
            'annual_consumption_kwh', 4000)  # Default 4000 kWh

        # Extract location data
        location_data = config.get('locationData', {})

        # Extract technical parameters
        tech_params = config.get('technicalParams', {})

        # Build Python calculation input format
        calculation_input = {
            # System configuration
            'modules': modules_data,
            'inverters': inverters_data,
            'batteries': batteries_data,
            'additional_components': additional_components,

            # System totals
            'anlage_kwp': total_module_power_wp / 1000.0,  # Convert Wp to kWp
            'module_count_total': sum(m['count'] for m in modules_data),

            # Consumption
            'annual_consumption_kwh': annual_consumption,
            'peak_consumption_kw': consumption_data.get('peak_consumption_kw'),
            'consumption_profile': consumption_data.get('consumption_profile', 'residential'),

            # Location for PVGIS
            'location': {
                'street': location_data.get('street'),
                'city': location_data.get('city'),
                'zipCode': location_data.get('zipCode'),
                'coordinates': location_data.get('coordinates')
            },

            # Technical parameters
            # South = 180°
            'roof_azimuth': tech_params.get('roof_azimuth', 180),
            # 30° default
            'roof_inclination': tech_params.get('roof_inclination', 30),
            # No shading = 1.0
            'shading_factor': tech_params.get('shading_factor', 1.0),
            'installation_type': tech_params.get('installation_type', 'roof'),

            # Options
            'include_pvgis': True,
            'include_financial_analysis': True,
            'include_environmental_analysis': True,
            'mwst_satz': 19.0  # German VAT
        }

        return calculation_input

    except Exception as e:
        raise Exception(f"Configuration conversion error: {str(e)}")


def perform_full_calculations(config):
    """
    Perform full PV calculations using calculations.py
    Returns results in TypeScript-compatible format
    """
    try:
        # Convert configuration
        calc_input = convert_configuration_to_python_format(config)

        # Perform calculations
        print("Starting PV calculations...", file=sys.stderr)
        results = perform_calculations(calc_input)

        # Convert results to TypeScript format
        typescript_results = {
            # Basic System Data
            'anlage_kwp': results.get('anlage_kwp', 0),
            'annual_pv_production_kwh': results.get('annual_pv_production_kwh', 0),
            'module_count_total': results.get('module_count_total', 0),

            # Financial Core Data
            'base_matrix_price_netto': results.get('base_matrix_price_netto', 0),
            'total_additional_costs_netto': results.get('total_additional_costs_netto', 0),
            'subtotal_netto': results.get('subtotal_netto', 0),
            'total_investment_netto': results.get('total_investment_netto', 0),
            'total_investment_brutto': results.get('total_investment_brutto', 0),

            # Performance Metrics
            'self_supply_rate_percent': results.get('self_supply_rate_percent', 0),
            'autarky_rate_percent': results.get('autarky_rate_percent', 0),
            'specific_yield_kwh_per_kwp': results.get('specific_yield_kwh_per_kwp', 0),

            # Economic Analysis
            'annual_financial_benefit_year1': results.get('annual_financial_benefit_year1', 0),
            'amortization_time_years': results.get('amortization_time_years', 0),
            'simple_roi_percent': results.get('simple_roi_percent', 0),
            'npv_value': results.get('npv_value', 0),

            # Environmental Impact
            'annual_co2_savings_kg': results.get('annual_co2_savings_kg', 0),
            'co2_savings_25_years_kg': results.get('co2_savings_25_years_kg', 0),

            # Advanced Analysis
            'einspeiseverguetung_euro_per_kwh': results.get('einspeiseverguetung_euro_per_kwh', 0.082),
            'stromkostenersparnis_year1': results.get('stromkostenersparnis_year1', 0),
            'feed_in_revenue_year1': results.get('feed_in_revenue_year1', 0),

            # Storage Analysis
            'storage_capacity_kwh': results.get('storage_capacity_kwh'),
            'storage_efficiency_percent': results.get('storage_efficiency_percent'),
            'battery_cycles_per_year': results.get('battery_cycles_per_year'),

            # Chart Data (monthly data converted to arrays)
            'monthly_production_data': results.get('monthly_production_data', [0] * 12),
            'monthly_consumption_data': results.get('monthly_consumption_data', [0] * 12),
            'monthly_self_consumption_data': results.get('monthly_self_consumption_data', [0] * 12),
            'cash_flow_25_years': results.get('cash_flow_25_years', [0] * 25),

            # Cost Breakdown
            'cost_breakdown': {
                'modules_cost': results.get('modules_cost_netto', 0),
                'inverters_cost': results.get('inverters_cost_netto', 0),
                'batteries_cost': results.get('batteries_cost_netto', 0),
                'additional_components_cost': results.get('additional_components_cost_netto', 0),
                'installation_cost': results.get('installation_cost_netto', 0),
                'planning_cost': results.get('planning_cost_netto', 0),
            },

            # Warnings and Errors
            'calculation_warnings': results.get('warnings', []),
            'calculation_errors': results.get('errors', [])
        }

        print("Calculations completed successfully", file=sys.stderr)
        return {
            'success': True,
            'calculation_results': typescript_results
        }

    except Exception as e:
        error_msg = f"Calculation error: {
            str(e)}\nTraceback: {
            traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        return {
            'success': False,
            'error': error_msg
        }


def calculate_live_pricing(base_results, modifications):
    """
    Calculate live pricing modifications
    """
    try:
        # Extract base price
        base_price = base_results.get('total_investment_netto', 0)

        # Apply modifications
        discount_percent = modifications.get('discount_percent', 0)
        surcharge_percent = modifications.get('surcharge_percent', 0)
        additional_costs = modifications.get('additional_costs', 0)

        # Calculate new price
        discount_amount = base_price * (discount_percent / 100)
        surcharge_amount = base_price * (surcharge_percent / 100)

        final_price_netto = base_price - discount_amount + \
            surcharge_amount + additional_costs
        final_price_brutto = final_price_netto * 1.19  # Add German VAT

        # Recalculate affected KPIs
        annual_production = base_results.get('annual_pv_production_kwh', 0)
        annual_savings = base_results.get('annual_financial_benefit_year1', 0)

        # Recalculate amortization with new price
        new_amortization_years = calculate_payback_years(
            final_price_netto,
            annual_savings,
            allow_infinite=False,
            default_zero=True,
        )

        # Simple ROI with new price
        new_roi_percent = (
            annual_savings /
            final_price_netto *
            100) if final_price_netto > 0 else 0

        pricing_results = {
            'base_price_netto': base_price,
            'discount_amount': discount_amount,
            'surcharge_amount': surcharge_amount,
            'additional_costs': additional_costs,
            'final_price_netto': final_price_netto,
            'final_price_brutto': final_price_brutto,
            'price_change_percent': (
                (final_price_netto - base_price) / base_price * 100) if base_price > 0 else 0,
            'new_amortization_years': new_amortization_years,
            'new_roi_percent': new_roi_percent,
            'updated_at': pd.Timestamp.now().isoformat()}

        return {
            'success': True,
            'pricing_results': pricing_results
        }

    except Exception as e:
        error_msg = f"Live pricing error: {str(e)}"
        print(error_msg, file=sys.stderr)
        return {
            'success': False,
            'error': error_msg
        }


def main():
    """
    Main bridge function
    """
    try:
        if len(sys.argv) != 2:
            print(
                "Usage: python calculation_bridge.py <json_payload_file>",
                file=sys.stderr)
            sys.exit(1)

        payload_file = sys.argv[1]

        # Read payload
        with open(payload_file, encoding='utf-8') as f:
            payload = json.load(f)

        command = payload.get('command')

        if command == 'perform_calculations':
            # Full calculations
            config = payload.get('configuration')
            result = perform_full_calculations(config)

        elif command == 'calculate_live_pricing':
            # Live pricing update
            base_results = payload.get('base_results')
            modifications = payload.get('modifications')
            result = calculate_live_pricing(base_results, modifications)

        else:
            result = {
                'success': False,
                'error': f'Unknown command: {command}'
            }

        # Output result as JSON
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        error_result = {
            'success': False,
            'error': f'Bridge error: {
                str(e)}\nTraceback: {
                traceback.format_exc()}'}
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
