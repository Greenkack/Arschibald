"""wp_implements/wp_bridge.py - Bridge zwischen Wärmepumpen-Berechnungen und Hauptanwendung"""
import streamlit as st
from typing import Dict, Any, Optional
from wp_implements.heat_pump_calculator import (
    calculate_heat_pump_capacity,
    calculate_cop_and_jaz,
    calculate_heat_pump_cost
)

class HeatPumpBridge:
    """Bridge-Klasse für Wärmepumpen-Integration"""
    
    def __init__(self):
        self.session_key = "wp_calculation_data"
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialisiere Session State"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {
                'capacity': None,
                'efficiency': None,
                'cost': None,
                'building_data': {},
                'selected_type': 'air_water'
            }
    
    def calculate_full_system(self, building_area: float, heat_demand: float, 
                             climate_zone: str = "temperate", target_temp: float = 21.0,
                             outdoor_min: float = -10.0, outdoor_avg: float = 8.0,
                             hp_type: str = "air_water", include_installation: bool = True) -> Dict[str, Any]:
        """Führe vollständige Wärmepumpen-Berechnung durch"""
        
        # 1. Dimensionierung
        capacity_result = calculate_heat_pump_capacity(
            building_area, heat_demand, target_temp, climate_zone
        )
        
        # 2. Effizienz
        efficiency_result = calculate_cop_and_jaz(
            outdoor_min, outdoor_avg, target_temp, hp_type
        )
        
        # 3. Kosten
        recommended_capacity = capacity_result['recommended_capacity_kw']
        cost_result = calculate_heat_pump_cost(
            recommended_capacity, hp_type, include_installation
        )
        
        # 4. Gesamtergebnis zusammenstellen
        full_result = {
            'capacity': capacity_result,
            'efficiency': efficiency_result,
            'cost': cost_result,
            'annual_electricity_consumption': capacity_result['annual_heat_demand_kwh'] / efficiency_result['jaz'],
            'annual_electricity_cost': (capacity_result['annual_heat_demand_kwh'] / efficiency_result['jaz']) * 0.30,  # 30 Cent/kWh
            'building_data': {
                'area': building_area,
                'heat_demand': heat_demand,
                'climate_zone': climate_zone,
                'target_temp': target_temp
            },
            'selected_type': hp_type
        }
        
        # In Session State speichern
        st.session_state[self.session_key] = full_result
        
        return full_result
    
    def get_calculation_data(self) -> Optional[Dict[str, Any]]:
        """Hole aktuelle Berechnungsdaten"""
        return st.session_state.get(self.session_key)
    
    def clear_calculation_data(self):
        """Lösche Berechnungsdaten"""
        if self.session_key in st.session_state:
            del st.session_state[self.session_key]
    
    def export_to_pdf_data(self) -> Dict[str, Any]:
        """Exportiere Daten für PDF-Generierung"""
        data = self.get_calculation_data()
        if not data:
            return {}
        
        return {
            'wp_type': data['selected_type'],
            'wp_capacity': data['capacity']['recommended_capacity_kw'],
            'wp_cop': data['efficiency']['cop'],
            'wp_jaz': data['efficiency']['jaz'],
            'wp_annual_demand': data['capacity']['annual_heat_demand_kwh'],
            'wp_annual_electricity': data['annual_electricity_consumption'],
            'wp_total_cost': data['cost']['total_cost'],
            'wp_building_area': data['building_data']['area'],
            'wp_heat_demand': data['building_data']['heat_demand']
        }
    
    def integrate_with_project(self, project_id: int) -> bool:
        """Integriere Wärmepumpen-Daten in Projekt"""
        from database import get_db_connection
        
        data = self.get_calculation_data()
        if not data:
            return False
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Prüfe ob Projekt existiert
            cursor.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
            if not cursor.fetchone():
                return False
            
            # Speichere Wärmepumpen-Daten als JSON in Projekt
            import json
            wp_data_json = json.dumps(data)
            
            cursor.execute("""
                UPDATE projects 
                SET heat_pump_data = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (wp_data_json, project_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Fehler bei Projekt-Integration: {e}")
            return False
    
    def compare_heat_sources(self, annual_heat_demand_kwh: float, jaz: float) -> Dict[str, Any]:
        """Vergleiche verschiedene Wärmequellen"""
        
        # Preise pro kWh
        prices = {
            'gas': 0.08,
            'oil': 0.10,
            'electricity': 0.30
        }
        
        # Wirkungsgrade
        efficiency = {
            'gas': 0.90,
            'oil': 0.85,
            'heat_pump': jaz
        }
        
        comparison = {}
        
        # Gas
        gas_consumption = annual_heat_demand_kwh / efficiency['gas']
        comparison['gas'] = {
            'consumption_kwh': gas_consumption,
            'cost': gas_consumption * prices['gas'],
            'co2_kg': gas_consumption * 0.247
        }
        
        # Öl
        oil_consumption = annual_heat_demand_kwh / efficiency['oil']
        comparison['oil'] = {
            'consumption_kwh': oil_consumption,
            'cost': oil_consumption * prices['oil'],
            'co2_kg': oil_consumption * 0.318
        }
        
        # Wärmepumpe
        wp_consumption = annual_heat_demand_kwh / efficiency['heat_pump']
        comparison['heat_pump'] = {
            'consumption_kwh': wp_consumption,
            'cost': wp_consumption * prices['electricity'],
            'co2_kg': wp_consumption * 0.150
        }
        
        # Einsparungen berechnen
        comparison['savings_vs_gas'] = {
            'cost': comparison['gas']['cost'] - comparison['heat_pump']['cost'],
            'co2_kg': comparison['gas']['co2_kg'] - comparison['heat_pump']['co2_kg']
        }
        
        comparison['savings_vs_oil'] = {
            'cost': comparison['oil']['cost'] - comparison['heat_pump']['cost'],
            'co2_kg': comparison['oil']['co2_kg'] - comparison['heat_pump']['co2_kg']
        }
        
        return comparison

# Singleton-Instanz
_bridge_instance = None

def get_heat_pump_bridge() -> HeatPumpBridge:
    """Hole Singleton-Instanz"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = HeatPumpBridge()
    return _bridge_instance
