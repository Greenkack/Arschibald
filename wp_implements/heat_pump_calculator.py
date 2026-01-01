"""wp_implements/heat_pump_calculator.py - Wärmepumpen-Berechnung"""
from typing import Dict, Any, Optional

def calculate_heat_pump_capacity(
    building_area: float,
    heat_demand_per_sqm: float,
    target_temp: float = 21.0,
    climate_zone: str = "temperate"
) -> Dict[str, Any]:
    """
    Berechne benötigte Wärmepumpen-Leistung
    
    Args:
        building_area: Wohnfläche in m²
        heat_demand_per_sqm: Wärmebedarf pro m² (kWh/m²/Jahr)
        target_temp: Ziel-Innentemperatur
        climate_zone: Klimazone (cold, temperate, warm)
    
    Returns:
        Dict mit Berechnungsergebnissen
    """
    # Jahreswärmebedarf
    annual_heat_demand = building_area * heat_demand_per_sqm
    
    # Klimafaktoren
    climate_factors = {
        'cold': 1.2,
        'temperate': 1.0,
        'warm': 0.8
    }
    factor = climate_factors.get(climate_zone, 1.0)
    
    # Heizlast (kW)
    heating_load = (annual_heat_demand / 2100) * factor  # Grobe Näherung
    
    # Empfohlene Nennleistung (mit Puffer)
    recommended_capacity = heating_load * 1.2
    
    return {
        'annual_heat_demand_kwh': round(annual_heat_demand, 2),
        'heating_load_kw': round(heating_load, 2),
        'recommended_capacity_kw': round(recommended_capacity, 2),
        'climate_factor': factor
    }

def calculate_cop_and_jaz(
    outdoor_temp_min: float = -10.0,
    outdoor_temp_avg: float = 8.0,
    indoor_temp: float = 21.0,
    heat_pump_type: str = "air_water"
) -> Dict[str, float]:
    """
    Berechne COP (Coefficient of Performance) und JAZ (Jahresarbeitszahl)
    
    Args:
        outdoor_temp_min: Minimale Außentemperatur
        outdoor_temp_avg: Durchschnittliche Außentemperatur
        indoor_temp: Innentemperatur
        heat_pump_type: Typ (air_water, brine_water, water_water)
    
    Returns:
        Dict mit COP und JAZ
    """
    # Basis-COP basierend auf Typ
    base_cop = {
        'air_water': 3.0,
        'brine_water': 4.0,
        'water_water': 4.5
    }
    
    cop_base = base_cop.get(heat_pump_type, 3.0)
    
    # Temperatur-Differenz-Faktor
    temp_diff = indoor_temp - outdoor_temp_avg
    temp_factor = 1 - (temp_diff / 100)
    
    cop = cop_base * temp_factor
    
    # JAZ (ca. 10-15% niedriger als COP)
    jaz = cop * 0.88
    
    return {
        'cop': round(cop, 2),
        'jaz': round(jaz, 2),
        'efficiency_rating': 'Sehr gut' if jaz > 4.0 else 'Gut' if jaz > 3.5 else 'Befriedigend'
    }

def calculate_heat_pump_cost(
    capacity_kw: float,
    heat_pump_type: str = "air_water",
    include_installation: bool = True
) -> Dict[str, float]:
    """
    Schätze Wärmepumpen-Kosten
    
    Args:
        capacity_kw: Leistung in kW
        heat_pump_type: Typ der Wärmepumpe
        include_installation: Installation einbeziehen
    
    Returns:
        Dict mit Kostenaufstellung
    """
    # Basis-Kosten pro kW
    cost_per_kw = {
        'air_water': 1200,
        'brine_water': 1800,
        'water_water': 2000
    }
    
    base_cost = cost_per_kw.get(heat_pump_type, 1200) * capacity_kw
    
    # Installationskosten
    installation_cost = base_cost * 0.3 if include_installation else 0
    
    # Zusatzkomponenten
    buffer_tank = 2000
    controls = 1500
    
    total_cost = base_cost + installation_cost + buffer_tank + controls
    
    return {
        'heat_pump_cost': round(base_cost, 2),
        'installation_cost': round(installation_cost, 2),
        'buffer_tank': buffer_tank,
        'controls': controls,
        'total_cost': round(total_cost, 2)
    }
