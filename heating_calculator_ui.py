"""heating_calculator_ui.py - Heizkosten-Rechner UI"""
import streamlit as st
from heating_cost_calculator import calculate_heating_costs, calculate_heatpump_savings

def render_heating_calculator():
    """Rendere Heizkosten-Rechner UI"""
    st.title("🔥 Heizkostenrechner")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Gebäudedaten")
        building_area = st.number_input("Wohnfläche (m²)", min_value=50.0, max_value=500.0, value=150.0)
        heat_demand = st.number_input("Wärmebedarf (kWh/m²/Jahr)", min_value=50.0, max_value=300.0, value=100.0)
    
    with col2:
        st.subheader("Aktuelle Heizung")
        energy_source = st.selectbox(
            "Energiequelle",
            ["gas", "oil", "electric", "heatpump"],
            format_func=lambda x: {"gas": "Erdgas", "oil": "Heizöl", "electric": "Strom", "heatpump": "Wärmepumpe"}[x]
        )
        energy_price = st.number_input("Energiepreis (€/kWh)", min_value=0.05, max_value=0.50, value=0.12, step=0.01)
        efficiency = st.slider("Wirkungsgrad", min_value=0.7, max_value=1.0, value=0.95, step=0.01)
    
    if st.button("Berechnen", type="primary"):
        results = calculate_heating_costs(building_area, heat_demand, energy_source, energy_price, efficiency)
        
        st.success("✓ Berechnung erfolgreich")
        
        # Ergebnisse anzeigen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Jährliche Kosten", f"{results['annual_cost_eur']:,.2f} €")
        with col2:
            st.metric("Monatliche Kosten", f"{results['monthly_cost_eur']:,.2f} €")
        with col3:
            st.metric("CO₂-Emissionen", f"{results['annual_co2_kg']:,.0f} kg/Jahr")
        
        # Wärmepumpen-Vergleich
        if energy_source != 'heatpump':
            st.divider()
            st.subheader("🌟 Potenzial mit Wärmepumpe")
            
            heatpump_jaz = st.slider("JAZ (Jahresarbeitszahl)", min_value=2.5, max_value=5.0, value=3.5, step=0.1)
            electricity_price = st.number_input("Strompreis (€/kWh)", min_value=0.20, max_value=0.50, value=0.30, step=0.01, key="elec_price")
            
            savings = calculate_heatpump_savings(results, heatpump_jaz, electricity_price)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Neue Jahreskosten", f"{savings['heatpump_annual_cost_eur']:,.2f} €")
            with col2:
                st.metric("Jährliche Ersparnis", f"{savings['annual_savings_eur']:,.2f} €", delta=f"{savings['savings_percent']}%")
            with col3:
                st.metric("CO₂-Einsparung", f"{savings['co2_savings_kg']:,.0f} kg/Jahr")

if __name__ == "__main__":
    render_heating_calculator()
