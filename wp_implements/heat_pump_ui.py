"""wp_implements/heat_pump_ui.py - Wärmepumpen UI"""
import streamlit as st
from wp_implements.heat_pump_calculator import (
    calculate_heat_pump_capacity,
    calculate_cop_and_jaz,
    calculate_heat_pump_cost
)

def render_heat_pump_ui():
    """Rendere Wärmepumpen-Konfigurator"""
    st.title("🔥 Wärmepumpen-Konfigurator")
    
    tab1, tab2, tab3 = st.tabs(["Dimensionierung", "Effizienz", "Kosten"])
    
    with tab1:
        st.subheader("Dimensionierung")
        
        col1, col2 = st.columns(2)
        with col1:
            building_area = st.number_input("Wohnfläche (m²)", min_value=50, max_value=500, value=150)
            heat_demand = st.number_input("Wärmebedarf (kWh/m²/Jahr)", min_value=30, max_value=200, value=80)
        
        with col2:
            climate_zone = st.selectbox("Klimazone", ["cold", "temperate", "warm"], 
                                       format_func=lambda x: {"cold": "Kalt", "temperate": "Gemäßigt", "warm": "Warm"}[x])
            target_temp = st.slider("Zieltemperatur (°C)", min_value=18, max_value=24, value=21)
        
        if st.button("Berechnen", key="dim_calc"):
            result = calculate_heat_pump_capacity(building_area, heat_demand, target_temp, climate_zone)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jahreswärmebedarf", f"{result['annual_heat_demand_kwh']:,.0f} kWh")
            with col2:
                st.metric("Heizlast", f"{result['heating_load_kw']:.1f} kW")
            with col3:
                st.metric("Empfohlene Leistung", f"{result['recommended_capacity_kw']:.1f} kW")
    
    with tab2:
        st.subheader("Effizienz-Berechnung")
        
        col1, col2 = st.columns(2)
        with col1:
            hp_type = st.selectbox("Wärmepumpentyp", 
                                  ["air_water", "brine_water", "water_water"],
                                  format_func=lambda x: {
                                      "air_water": "Luft-Wasser",
                                      "brine_water": "Sole-Wasser",
                                      "water_water": "Wasser-Wasser"
                                  }[x])
            indoor_temp = st.number_input("Innentemperatur (°C)", value=21.0)
        
        with col2:
            outdoor_min = st.number_input("Min. Außentemperatur (°C)", value=-10.0)
            outdoor_avg = st.number_input("Ø Außentemperatur (°C)", value=8.0)
        
        if st.button("COP/JAZ berechnen", key="eff_calc"):
            result = calculate_cop_and_jaz(outdoor_min, outdoor_avg, indoor_temp, hp_type)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("COP", result['cop'])
            with col2:
                st.metric("JAZ", result['jaz'])
            with col3:
                st.metric("Bewertung", result['efficiency_rating'])
    
    with tab3:
        st.subheader("Kostenberechnung")
        
        col1, col2 = st.columns(2)
        with col1:
            capacity = st.number_input("Leistung (kW)", min_value=5.0, max_value=30.0, value=12.0)
            hp_type_cost = st.selectbox("Typ", 
                                       ["air_water", "brine_water", "water_water"],
                                       format_func=lambda x: {
                                           "air_water": "Luft-Wasser",
                                           "brine_water": "Sole-Wasser",
                                           "water_water": "Wasser-Wasser"
                                       }[x],
                                       key="hp_type_cost")
        
        with col2:
            include_install = st.checkbox("Installation einbeziehen", value=True)
        
        if st.button("Kosten berechnen", key="cost_calc"):
            result = calculate_heat_pump_cost(capacity, hp_type_cost, include_install)
            
            st.info(f"**Gesamtkosten: {result['total_cost']:,.2f} €**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Wärmepumpe", f"{result['heat_pump_cost']:,.2f} €")
                st.metric("Pufferspeicher", f"{result['buffer_tank']:,.2f} €")
            
            with col2:
                st.metric("Installation", f"{result['installation_cost']:,.2f} €")
                st.metric("Steuerung", f"{result['controls']:,.2f} €")

if __name__ == "__main__":
    render_heat_pump_ui()
