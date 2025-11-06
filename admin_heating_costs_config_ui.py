"""
Admin-UI für Heizkosten-Konfiguration
Verwaltung von CO₂-Emissionsfaktoren, Brennstoffpreisen und Betriebskosten
"""

import streamlit as st
import json
import os
from pathlib import Path


# Standardwerte für Heizkosten-Konfiguration
DEFAULT_HEATING_CONFIG = {
    "co2_factors": {
        "oil_kg_per_liter": 2.66,
        "gas_g_per_kwh": 428,
        "electricity_g_per_kwh": 420,
        "pellets_kg_per_ton": 26,
        "co2_price_euro_per_ton": 55.0
    },
    "fuel_prices": {
        "oil_cent_per_kwh": 10.0,
        "gas_cent_per_kwh": 12.0,
        "electricity_cent_per_kwh": 32.0,
        "pellets_euro_per_ton": 350.0,
        "wood_euro_per_ster": 80.0
    },
    "operating_costs": {
        "chimney_sweep_gas_oil_annual": 80.0,
        "chimney_sweep_pellets_annual": 120.0,
        "chimney_sweep_heatpump_annual": 0.0,
        "maintenance_gas_annual": 200.0,
        "maintenance_oil_annual": 250.0,
        "maintenance_pellets_annual": 300.0,
        "maintenance_heatpump_annual": 300.0,
        "repair_gas_annual_avg": 150.0,
        "repair_oil_annual_avg": 200.0,
        "repair_pellets_annual_avg": 250.0,
        "repair_heatpump_annual_avg": 150.0,
        "pump_power_gas_kwh_annual": 500.0,
        "pump_power_oil_kwh_annual": 450.0,
        "pump_power_pellets_kwh_annual": 600.0
    },
    "conversion_factors": {
        "oil_liter_to_kwh": 10.0,
        "oil_ton_to_liter": 1190.0,
        "wood_ster_to_kwh": 2000.0,
        "pellets_kg_to_kwh": 4.9
    }
}


CONFIG_FILE_PATH = Path(__file__).parent / "config" / "heating_costs_config.json"


def load_heating_config() -> dict:
    """Lade Heizkosten-Konfiguration aus Datei oder verwende Standardwerte"""
    if CONFIG_FILE_PATH.exists():
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Fehler beim Laden der Konfiguration: {e}")
            return DEFAULT_HEATING_CONFIG
    else:
        return DEFAULT_HEATING_CONFIG


def save_heating_config(config: dict) -> bool:
    """Speichere Heizkosten-Konfiguration in Datei"""
    try:
        # Erstelle config-Verzeichnis falls nicht vorhanden
        CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern der Konfiguration: {e}")
        return False


def render_admin_heating_costs_ui():
    """Rendert die Admin-UI für Heizkosten-Konfiguration"""
    
    st.title("⚙️ Heizkosten-Konfiguration")
    st.markdown("---")
    
    # Lade aktuelle Konfiguration
    config = load_heating_config()
    
    # Tabs für verschiedene Kategorien
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌍 CO₂-Faktoren",
        "⛽ Brennstoffpreise",
        "🛠️ Betriebskosten",
        "🔄 Umrechnungsfaktoren",
        "💾 Aktionen"
    ])
    
    # Tab 1: CO₂-Faktoren
    with tab1:
        st.subheader("CO₂-Emissionsfaktoren")
        st.caption("Geben Sie die CO₂-Emissionen für verschiedene Energieträger an")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config["co2_factors"]["oil_kg_per_liter"] = st.number_input(
                "Heizöl (kg CO₂ pro Liter)",
                min_value=0.0,
                max_value=10.0,
                value=config["co2_factors"]["oil_kg_per_liter"],
                step=0.01,
                help="Standard: 2.66 kg CO₂ pro Liter Heizöl"
            )
            
            config["co2_factors"]["gas_g_per_kwh"] = st.number_input(
                "Erdgas (g CO₂ pro kWh)",
                min_value=0.0,
                max_value=1000.0,
                value=config["co2_factors"]["gas_g_per_kwh"],
                step=1.0,
                help="Standard: 428 g CO₂ pro kWh Erdgas"
            )
            
            config["co2_factors"]["electricity_g_per_kwh"] = st.number_input(
                "Strom (g CO₂ pro kWh)",
                min_value=0.0,
                max_value=1000.0,
                value=config["co2_factors"]["electricity_g_per_kwh"],
                step=1.0,
                help="Standard: 420 g CO₂ pro kWh (Strommix Deutschland 2025)"
            )
        
        with col2:
            config["co2_factors"]["pellets_kg_per_ton"] = st.number_input(
                "Pellets (kg CO₂ pro Tonne)",
                min_value=0.0,
                max_value=500.0,
                value=config["co2_factors"]["pellets_kg_per_ton"],
                step=1.0,
                help="Standard: 26 kg CO₂ pro Tonne Pellets"
            )
            
            config["co2_factors"]["co2_price_euro_per_ton"] = st.number_input(
                "CO₂-Preis (€ pro Tonne)",
                min_value=0.0,
                max_value=500.0,
                value=config["co2_factors"]["co2_price_euro_per_ton"],
                step=1.0,
                help="Aktueller CO₂-Preis in Deutschland (Stand 2025: 55 €/t)"
            )
        
        # Berechnungsbeispiel
        st.markdown("---")
        st.markdown("### 📊 Berechnungsbeispiel")
        example_kwh = st.number_input("Jahreswärmebedarf (kWh)", value=15000, step=1000)
        
        example_col1, example_col2, example_col3 = st.columns(3)
        
        with example_col1:
            oil_liters = example_kwh / config["conversion_factors"]["oil_liter_to_kwh"]
            oil_co2_kg = oil_liters * config["co2_factors"]["oil_kg_per_liter"]
            oil_co2_cost = (oil_co2_kg / 1000) * config["co2_factors"]["co2_price_euro_per_ton"]
            
            st.info(f"""
            **Heizöl**
            - Verbrauch: {oil_liters:,.0f} Liter
            - CO₂: {oil_co2_kg:,.0f} kg/Jahr
            - CO₂-Steuer: {oil_co2_cost:,.2f} €/Jahr
            """)
        
        with example_col2:
            gas_co2_kg = example_kwh * (config["co2_factors"]["gas_g_per_kwh"] / 1000)
            gas_co2_cost = (gas_co2_kg / 1000) * config["co2_factors"]["co2_price_euro_per_ton"]
            
            st.info(f"""
            **Erdgas**
            - Verbrauch: {example_kwh:,.0f} kWh
            - CO₂: {gas_co2_kg:,.0f} kg/Jahr
            - CO₂-Steuer: {gas_co2_cost:,.2f} €/Jahr
            """)
        
        with example_col3:
            # Annahme: SCOP 4.0 für Wärmepumpe
            wp_electricity_kwh = example_kwh / 4.0
            wp_co2_kg = wp_electricity_kwh * (config["co2_factors"]["electricity_g_per_kwh"] / 1000)
            wp_co2_cost = (wp_co2_kg / 1000) * config["co2_factors"]["co2_price_euro_per_ton"]
            
            st.success(f"""
            **Wärmepumpe (SCOP 4.0)**
            - Strom: {wp_electricity_kwh:,.0f} kWh
            - CO₂: {wp_co2_kg:,.0f} kg/Jahr
            - CO₂-Steuer: {wp_co2_cost:,.2f} €/Jahr
            - ✅ Einsparung: {gas_co2_kg - wp_co2_kg:,.0f} kg/Jahr
            """)
    
    # Tab 2: Brennstoffpreise
    with tab2:
        st.subheader("Brennstoffpreise (Standard-Werte)")
        st.caption("Diese Werte werden als Voreinstellung in der Anwendung verwendet")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config["fuel_prices"]["oil_cent_per_kwh"] = st.number_input(
                "Heizöl (Cent/kWh)",
                min_value=0.0,
                max_value=50.0,
                value=config["fuel_prices"]["oil_cent_per_kwh"],
                step=0.1,
                help="Standard-Preis für Heizöl"
            )
            
            config["fuel_prices"]["gas_cent_per_kwh"] = st.number_input(
                "Erdgas (Cent/kWh)",
                min_value=0.0,
                max_value=50.0,
                value=config["fuel_prices"]["gas_cent_per_kwh"],
                step=0.1,
                help="Standard-Preis für Erdgas"
            )
            
            config["fuel_prices"]["electricity_cent_per_kwh"] = st.number_input(
                "Strom (Cent/kWh)",
                min_value=0.0,
                max_value=100.0,
                value=config["fuel_prices"]["electricity_cent_per_kwh"],
                step=0.1,
                help="Standard-Strompreis"
            )
        
        with col2:
            config["fuel_prices"]["pellets_euro_per_ton"] = st.number_input(
                "Pellets (€/Tonne)",
                min_value=0.0,
                max_value=1000.0,
                value=config["fuel_prices"]["pellets_euro_per_ton"],
                step=10.0,
                help="Standard-Preis für Pellets"
            )
            
            config["fuel_prices"]["wood_euro_per_ster"] = st.number_input(
                "Brennholz (€/Ster)",
                min_value=0.0,
                max_value=200.0,
                value=config["fuel_prices"]["wood_euro_per_ster"],
                step=5.0,
                help="Standard-Preis für Brennholz (Raummeter)"
            )
    
    # Tab 3: Betriebskosten
    with tab3:
        st.subheader("Jährliche Betriebskosten")
        
        st.markdown("#### 🧹 Schornsteinfeger-Kosten")
        cost_col1, cost_col2, cost_col3 = st.columns(3)
        
        with cost_col1:
            config["operating_costs"]["chimney_sweep_gas_oil_annual"] = st.number_input(
                "Gas/Öl (€/Jahr)",
                min_value=0.0,
                max_value=500.0,
                value=config["operating_costs"]["chimney_sweep_gas_oil_annual"],
                step=10.0
            )
        
        with cost_col2:
            config["operating_costs"]["chimney_sweep_pellets_annual"] = st.number_input(
                "Pellets (€/Jahr)",
                min_value=0.0,
                max_value=500.0,
                value=config["operating_costs"]["chimney_sweep_pellets_annual"],
                step=10.0
            )
        
        with cost_col3:
            config["operating_costs"]["chimney_sweep_heatpump_annual"] = st.number_input(
                "Wärmepumpe (€/Jahr)",
                min_value=0.0,
                max_value=500.0,
                value=config["operating_costs"]["chimney_sweep_heatpump_annual"],
                step=10.0,
                help="Normalerweise 0€ bei Wärmepumpe"
            )
        
        st.markdown("---")
        st.markdown("#### 🛠️ Wartungskosten")
        maint_col1, maint_col2, maint_col3, maint_col4 = st.columns(4)
        
        with maint_col1:
            config["operating_costs"]["maintenance_gas_annual"] = st.number_input(
                "Gas (€/Jahr)",
                min_value=0.0,
                max_value=2000.0,
                value=config["operating_costs"]["maintenance_gas_annual"],
                step=10.0
            )
        
        with maint_col2:
            config["operating_costs"]["maintenance_oil_annual"] = st.number_input(
                "Öl (€/Jahr)",
                min_value=0.0,
                max_value=2000.0,
                value=config["operating_costs"]["maintenance_oil_annual"],
                step=10.0
            )
        
        with maint_col3:
            config["operating_costs"]["maintenance_pellets_annual"] = st.number_input(
                "Pellets (€/Jahr)",
                min_value=0.0,
                max_value=2000.0,
                value=config["operating_costs"]["maintenance_pellets_annual"],
                step=10.0
            )
        
        with maint_col4:
            config["operating_costs"]["maintenance_heatpump_annual"] = st.number_input(
                "Wärmepumpe (€/Jahr)",
                min_value=0.0,
                max_value=2000.0,
                value=config["operating_costs"]["maintenance_heatpump_annual"],
                step=10.0
            )
        
        st.markdown("---")
        st.markdown("#### 🔩 Durchschnittliche Reparaturkosten")
        repair_col1, repair_col2, repair_col3, repair_col4 = st.columns(4)
        
        with repair_col1:
            config["operating_costs"]["repair_gas_annual_avg"] = st.number_input(
                "Gas (€/Jahr)",
                min_value=0.0,
                max_value=5000.0,
                value=config["operating_costs"]["repair_gas_annual_avg"],
                step=50.0,
                key="repair_gas"
            )
        
        with repair_col2:
            config["operating_costs"]["repair_oil_annual_avg"] = st.number_input(
                "Öl (€/Jahr)",
                min_value=0.0,
                max_value=5000.0,
                value=config["operating_costs"]["repair_oil_annual_avg"],
                step=50.0,
                key="repair_oil"
            )
        
        with repair_col3:
            config["operating_costs"]["repair_pellets_annual_avg"] = st.number_input(
                "Pellets (€/Jahr)",
                min_value=0.0,
                max_value=5000.0,
                value=config["operating_costs"]["repair_pellets_annual_avg"],
                step=50.0,
                key="repair_pellets"
            )
        
        with repair_col4:
            config["operating_costs"]["repair_heatpump_annual_avg"] = st.number_input(
                "Wärmepumpe (€/Jahr)",
                min_value=0.0,
                max_value=5000.0,
                value=config["operating_costs"]["repair_heatpump_annual_avg"],
                step=50.0,
                key="repair_hp"
            )
        
        st.markdown("---")
        st.markdown("#### ⚡ Stromverbrauch Heizungsanlage (Pumpen, Regelung)")
        pump_col1, pump_col2, pump_col3 = st.columns(3)
        
        with pump_col1:
            config["operating_costs"]["pump_power_gas_kwh_annual"] = st.number_input(
                "Gas (kWh/Jahr)",
                min_value=0.0,
                max_value=2000.0,
                value=config["operating_costs"]["pump_power_gas_kwh_annual"],
                step=50.0
            )
        
        with pump_col2:
            config["operating_costs"]["pump_power_oil_kwh_annual"] = st.number_input(
                "Öl (kWh/Jahr)",
                min_value=0.0,
                max_value=2000.0,
                value=config["operating_costs"]["pump_power_oil_kwh_annual"],
                step=50.0
            )
        
        with pump_col3:
            config["operating_costs"]["pump_power_pellets_kwh_annual"] = st.number_input(
                "Pellets (kWh/Jahr)",
                min_value=0.0,
                max_value=2000.0,
                value=config["operating_costs"]["pump_power_pellets_kwh_annual"],
                step=50.0
            )
    
    # Tab 4: Umrechnungsfaktoren
    with tab4:
        st.subheader("Umrechnungsfaktoren")
        st.caption("Faktoren zur Umrechnung zwischen verschiedenen Einheiten")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config["conversion_factors"]["oil_liter_to_kwh"] = st.number_input(
                "Heizöl: Liter → kWh",
                min_value=0.0,
                max_value=20.0,
                value=config["conversion_factors"]["oil_liter_to_kwh"],
                step=0.1,
                help="Standard: 1 Liter Heizöl ≈ 10 kWh"
            )
            
            config["conversion_factors"]["oil_ton_to_liter"] = st.number_input(
                "Heizöl: Tonne → Liter",
                min_value=0.0,
                max_value=2000.0,
                value=config["conversion_factors"]["oil_ton_to_liter"],
                step=10.0,
                help="Standard: 1 Tonne ≈ 1.190 Liter (bei Dichte 0.84 kg/l)"
            )
        
        with col2:
            config["conversion_factors"]["wood_ster_to_kwh"] = st.number_input(
                "Holz: Ster → kWh",
                min_value=0.0,
                max_value=5000.0,
                value=config["conversion_factors"]["wood_ster_to_kwh"],
                step=100.0,
                help="Standard: 1 Ster (Raummeter) ≈ 2.000 kWh"
            )
            
            config["conversion_factors"]["pellets_kg_to_kwh"] = st.number_input(
                "Pellets: kg → kWh",
                min_value=0.0,
                max_value=10.0,
                value=config["conversion_factors"]["pellets_kg_to_kwh"],
                step=0.1,
                help="Standard: 1 kg Pellets ≈ 4.9 kWh"
            )
    
    # Tab 5: Aktionen
    with tab5:
        st.subheader("Konfiguration verwalten")
        
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("💾 Konfiguration speichern", use_container_width=True, type="primary"):
                if save_heating_config(config):
                    st.success("✅ Konfiguration erfolgreich gespeichert!")
                else:
                    st.error("❌ Fehler beim Speichern der Konfiguration")
        
        with col_action2:
            if st.button("🔄 Standardwerte wiederherstellen", use_container_width=True):
                config = DEFAULT_HEATING_CONFIG.copy()
                if save_heating_config(config):
                    st.success("✅ Standardwerte wiederhergestellt!")
                    st.rerun()
        
        with col_action3:
            if st.button("📥 Konfiguration exportieren", use_container_width=True):
                config_json = json.dumps(config, indent=2, ensure_ascii=False)
                st.download_button(
                    label="JSON herunterladen",
                    data=config_json,
                    file_name="heating_costs_config.json",
                    mime="application/json"
                )
        
        st.markdown("---")
        st.markdown("### 📋 Aktuelle Konfiguration (JSON)")
        st.json(config, expanded=False)
        
        st.markdown("---")
        st.info(f"""
        **Konfigurationsdatei:**
        `{CONFIG_FILE_PATH}`
        
        Diese Einstellungen werden automatisch in allen Berechnungen verwendet.
        """)


if __name__ == "__main__":
    render_admin_heating_costs_ui()
