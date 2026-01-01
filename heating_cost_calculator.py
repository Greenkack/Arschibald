"""heating_cost_calculator.py - Heizkostenberechnung"""
import math
from typing import Dict, Any

def calculate_heating_costs(
    building_area: float,
    heat_demand: float,
    energy_source: str,
    energy_price: float,
    efficiency: float = 0.95
) -> Dict[str, Any]:
    """
    Berechne Heizkosten
    
    Args:
        building_area: Wohnfläche in m²
        heat_demand: Wärmebedarf in kWh/m²/Jahr
        energy_source: Energiequelle (gas, oil, electric, heatpump)
        energy_price: Energiepreis in €/kWh
        efficiency: Wirkungsgrad der Heizung
    
    Returns:
        Dict mit Berechnungsergebnissen
    """
    annual_heat_demand = building_area * heat_demand
    annual_energy_consumption = annual_heat_demand / efficiency
    annual_cost = annual_energy_consumption * energy_price
    
    monthly_cost = annual_cost / 12
    daily_cost = annual_cost / 365
    
    # CO2-Emissionen (kg CO2/kWh)
    co2_factors = {
        'gas': 0.247,
        'oil': 0.318,
        'electric': 0.401,
        'heatpump': 0.150  # Bei JAZ=3.5
    }
    
    annual_co2 = annual_energy_consumption * co2_factors.get(energy_source, 0.247)
    
    return {
        'annual_heat_demand_kwh': round(annual_heat_demand, 2),
        'annual_energy_consumption_kwh': round(annual_energy_consumption, 2),
        'annual_cost_eur': round(annual_cost, 2),
        'monthly_cost_eur': round(monthly_cost, 2),
        'daily_cost_eur': round(daily_cost, 2),
        'annual_co2_kg': round(annual_co2, 2),
        'efficiency': efficiency,
        'energy_source': energy_source
    }

def calculate_heatpump_savings(
    current_costs: Dict[str, Any],
    heatpump_jaz: float = 3.5,
    electricity_price: float = 0.30
) -> Dict[str, Any]:
    """Berechne Einsparungen durch Wärmepumpe"""
    annual_heat_demand = current_costs['annual_heat_demand_kwh']
    heatpump_energy_consumption = annual_heat_demand / heatpump_jaz
    heatpump_annual_cost = heatpump_energy_consumption * electricity_price
    
    annual_savings = current_costs['annual_cost_eur'] - heatpump_annual_cost
    co2_savings = current_costs['annual_co2_kg'] - (heatpump_energy_consumption * 0.150)
    
    return {
        'heatpump_annual_cost_eur': round(heatpump_annual_cost, 2),
        'annual_savings_eur': round(annual_savings, 2),
        'savings_percent': round((annual_savings / current_costs['annual_cost_eur']) * 100, 1),
        'co2_savings_kg': round(co2_savings, 2),
        'payback_years': 0  # Wird separat berechnet mit Investitionskosten
    }
