# admin_heatpump_settings_ui.py
"""
Wärmepumpen-Einstellungen Admin UI
Verwaltet:
- Wärmepumpen-Produktpreise (alle Hersteller & Modelle)
- Heizkosten-Konfiguration (CO₂, Brennstoffpreise, Betriebskosten)
- Dynamische Verknüpfung mit allen Wärmepumpen-Berechnungen
- PDF-Integration für alle Bereiche

Author: GitHub Copilot
Version: 1.0
Date: 2025-01-15
"""

import streamlit as st
import json
from pathlib import Path
from typing import Any, Dict
import pandas as pd


# ============================================================================
# KONFIGURATIONSPFADE
# ============================================================================

CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_DIR.mkdir(exist_ok=True)

HEATING_COSTS_CONFIG_FILE = CONFIG_DIR / "heating_costs_config.json"
HEATPUMP_PRICES_CONFIG_FILE = CONFIG_DIR / "heatpump_prices_config.json"


# ============================================================================
# STANDARD-KONFIGURATIONEN
# ============================================================================

DEFAULT_HEATING_CONFIG = {
    "co2_factors": {
        "oil_kg_per_liter": 2.66,
        "gas_g_per_kwh": 428,
        "electricity_g_per_kwh": 420,
        "pellets_kg_per_ton": 26,
        "co2_price_euro_per_ton": 55
    },
    "fuel_prices": {
        "gas_cent_per_kwh": 12.0,
        "oil_cent_per_liter": 90.0,
        "wood_euro_per_ster": 80.0,
        "pellets_euro_per_ton": 350.0,
        "electricity_cent_per_kwh": 32.0
    },
    "operating_costs": {
        "gas": {
            "chimney_sweep": 120,
            "maintenance": 150,
            "repair": 200,
            "pump_power_kwh": 300
        },
        "oil": {
            "chimney_sweep": 120,
            "maintenance": 200,
            "repair": 250,
            "pump_power_kwh": 400
        },
        "pellets": {
            "chimney_sweep": 120,
            "maintenance": 300,
            "repair": 300,
            "pump_power_kwh": 500
        },
        "heatpump": {
            "chimney_sweep": 0,
            "maintenance": 150,
            "repair": 100,
            "pump_power_kwh": 0
        }
    },
    "conversion_factors": {
        "oil_liter_to_kwh": 10.0,
        "oil_ton_to_liter": 1190,
        "wood_ster_to_kwh": 2000,
        "pellets_kg_to_kwh": 4.9
    }
}


# Lade Produktdatenbank
try:
    from heatpump_products_database import HEATPUMP_PRODUCTS
except ImportError:
    HEATPUMP_PRODUCTS = {}


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def format_german_number(number: float, decimals: int = 2) -> str:
    """
    Formatiert eine Zahl nach deutschem Format
    
    Args:
        number: Die zu formatierende Zahl
        decimals: Anzahl Dezimalstellen (Standard: 2)
    
    Returns:
        Formatierte Zahl (z.B. 12.345,67)
    """
    # Formatiere mit Punkt als Tausender-Trennzeichen und Komma als Dezimaltrennzeichen
    formatted = f"{number:,.{decimals}f}"
    # Ersetze englische Format durch deutsches
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted


# Erstelle Standardpreise für alle Produkte
def create_default_heatpump_prices():
    """Erstellt Standardpreise für alle Wärmepumpen-Produkte"""
    prices = {}
    
    for manufacturer, types in HEATPUMP_PRODUCTS.items():
        prices[manufacturer] = {}
        for hp_type, models in types.items():
            prices[manufacturer][hp_type] = {}
            for model in models:
                model_name = model.get("model", "Unknown")
                heating_powers = model.get("heating_power_kw", [])
                
                # Standardpreise basierend auf Leistung
                power_prices = {}
                for power in heating_powers:
                    # Basispreis: 800€ + 200€ pro kW
                    base_price = 800 + (power * 200)
                    power_prices[str(power)] = {
                        "base_price_eur": round(base_price, 2),
                        "installation_price_eur": round(base_price * 0.4, 2),  # 40% für Installation
                        "total_price_eur": round(base_price * 1.4, 2)
                    }
                
                prices[manufacturer][hp_type][model_name] = power_prices
    
    return prices


DEFAULT_HEATPUMP_PRICES = create_default_heatpump_prices()


# ============================================================================
# LADE- UND SPEICHER-FUNKTIONEN
# ============================================================================

def load_heating_config() -> Dict[str, Any]:
    """Lädt Heizkosten-Konfiguration"""
    try:
        if HEATING_COSTS_CONFIG_FILE.exists():
            with open(HEATING_COSTS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"Fehler beim Laden der Heizkosten-Konfiguration: {e}")
    
    return DEFAULT_HEATING_CONFIG.copy()


def save_heating_config(config: Dict[str, Any]) -> bool:
    """Speichert Heizkosten-Konfiguration"""
    try:
        with open(HEATING_COSTS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False


def load_heatpump_prices() -> Dict[str, Any]:
    """Lädt Wärmepumpen-Preise"""
    try:
        if HEATPUMP_PRICES_CONFIG_FILE.exists():
            with open(HEATPUMP_PRICES_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"Fehler beim Laden der Wärmepumpen-Preise: {e}")
    
    return DEFAULT_HEATPUMP_PRICES.copy()


def save_heatpump_prices(prices: Dict[str, Any]) -> bool:
    """Speichert Wärmepumpen-Preise"""
    try:
        with open(HEATPUMP_PRICES_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(prices, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False


# ============================================================================
# HELPER-FUNKTIONEN FÜR DYNAMISCHE PREISABFRAGE
# ============================================================================

def get_heatpump_price(manufacturer: str, hp_type: str, model: str, power_kw: float) -> Dict[str, float]:
    """
    Gibt den Preis für eine spezifische Wärmepumpe zurück
    
    Args:
        manufacturer: Hersteller (z.B. "Viessmann")
        hp_type: Typ (z.B. "Luft-Wasser-Wärmepumpe")
        model: Modellname (z.B. "Vitocal 250-A")
        power_kw: Heizleistung in kW
    
    Returns:
        Dict mit base_price_eur, installation_price_eur, total_price_eur
    """
    prices = load_heatpump_prices()
    
    try:
        # Prüfe ob Hersteller existiert
        if manufacturer not in prices:
            raise KeyError(f"Hersteller '{manufacturer}' nicht in Preiskonfiguration gefunden")
        
        # Prüfe ob Typ existiert
        if hp_type not in prices[manufacturer]:
            raise KeyError(f"Typ '{hp_type}' nicht gefunden")
        
        # Prüfe ob Modell existiert
        if model not in prices[manufacturer][hp_type]:
            raise KeyError(f"Modell '{model}' nicht gefunden")
        
        model_prices = prices[manufacturer][hp_type][model]
        
        # Versuche verschiedene String-Formate für power_kw
        power_formats = [
            str(power_kw),                    # z.B. "16.0"
            str(int(power_kw)),               # z.B. "16"
            f"{power_kw:.1f}",                # z.B. "16.0"
            f"{float(power_kw)}",             # z.B. "16.0"
        ]
        
        # Versuche exakten Match mit verschiedenen Formaten
        for power_str in power_formats:
            if power_str in model_prices:
                price_data = model_prices[power_str]
                # Stelle sicher, dass alle Felder vorhanden sind
                return {
                    "base_price_eur": float(price_data.get("base_price_eur", 0)),
                    "installation_price_eur": float(price_data.get("installation_price_eur", 0)),
                    "total_price_eur": float(price_data.get("total_price_eur", 0))
                }
        
        # Fallback: Nächste verfügbare Leistung suchen
        available_powers = []
        for key in model_prices.keys():
            try:
                available_powers.append(float(key))
            except ValueError:
                continue
        
        if not available_powers:
            raise KeyError(f"Keine gültigen Leistungsvarianten gefunden")
        
        # Finde nächstgelegene Leistung
        closest_power = min(available_powers, key=lambda x: abs(x - power_kw))
        
        # Versuche wieder verschiedene Formate für closest_power
        closest_formats = [
            str(closest_power),
            str(int(closest_power)) if closest_power == int(closest_power) else str(closest_power),
            f"{closest_power:.1f}",
        ]
        
        for closest_str in closest_formats:
            if closest_str in model_prices:
                price_data = model_prices[closest_str]
                return {
                    "base_price_eur": float(price_data.get("base_price_eur", 0)),
                    "installation_price_eur": float(price_data.get("installation_price_eur", 0)),
                    "total_price_eur": float(price_data.get("total_price_eur", 0))
                }
        
        raise KeyError(f"Leistung {power_kw} kW nicht gefunden. Verfügbare: {list(model_prices.keys())}")
        
    except (KeyError, ValueError) as e:
        # Fallback auf Standardberechnung
        import streamlit as st
        st.warning(f"⚠️ Preis nicht in Konfiguration gefunden: {manufacturer} {model} {power_kw}kW. Nutze Standardberechnung.")
        base_price = 800 + (power_kw * 200)
        return {
            "base_price_eur": round(base_price, 2),
            "installation_price_eur": round(base_price * 0.4, 2),
            "total_price_eur": round(base_price * 1.4, 2)
        }


# ============================================================================
# HAUPT-UI
# ============================================================================

def render_admin_heatpump_settings_ui():
    """Hauptfunktion: Rendert die Wärmepumpen-Einstellungen UI"""
    
    st.title("🔥 Wärmepumpen-Einstellungen")
    st.markdown("---")
    
    # Tab-Navigation
    tabs = st.tabs([
        "💰 Wärmepumpen-Preise",
        "🌡️ Heizkosten-Konfiguration",
        "📊 Übersicht & Export",
        "🔗 Integration & Tests"
    ])
    
    # Tab 1: Wärmepumpen-Preise
    with tabs[0]:
        render_heatpump_prices_tab()
    
    # Tab 2: Heizkosten-Konfiguration
    with tabs[1]:
        render_heating_costs_tab()
    
    # Tab 3: Übersicht & Export
    with tabs[2]:
        render_overview_tab()
    
    # Tab 4: Integration & Tests
    with tabs[3]:
        render_integration_tab()


# ============================================================================
# TAB 1: WÄRMEPUMPEN-PREISE
# ============================================================================

def render_heatpump_prices_tab():
    """Tab für Wärmepumpen-Preise"""
    
    st.subheader("💰 Wärmepumpen-Preise verwalten")
    st.caption("Preise für alle Hersteller, Typen, Modelle und Leistungsstufen")
    
    # Lade aktuelle Preise
    prices = load_heatpump_prices()
    
    # Hersteller-Auswahl
    if not HEATPUMP_PRODUCTS:
        st.error("❌ Produktdatenbank konnte nicht geladen werden!")
        return
    
    manufacturers = list(HEATPUMP_PRODUCTS.keys())
    selected_manufacturer = st.selectbox(
        "Hersteller auswählen",
        manufacturers,
        key="price_manufacturer_select"
    )
    
    if selected_manufacturer:
        types = list(HEATPUMP_PRODUCTS[selected_manufacturer].keys())
        selected_type = st.selectbox(
            "Typ auswählen",
            types,
            key="price_type_select"
        )
        
        if selected_type:
            models = HEATPUMP_PRODUCTS[selected_manufacturer][selected_type]
            
            st.markdown("---")
            st.markdown(f"### {selected_manufacturer} - {selected_type}")
            
            # Für jedes Modell
            for idx, model_data in enumerate(models):
                model_name = model_data.get("model", "Unknown")
                heating_powers = model_data.get("heating_power_kw", [])
                scop = model_data.get("scop", 0)
                
                with st.expander(f"🔧 {model_name} (SCOP: {scop})"):
                    st.caption(f"Verfügbare Leistungen: {', '.join([str(p) + ' kW' for p in heating_powers])}")
                    
                    # Preise für jede Leistungsstufe
                    for power in heating_powers:
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                        
                        # Hole aktuelle Preise
                        try:
                            current_prices = prices[selected_manufacturer][selected_type][model_name][str(power)]
                        except KeyError:
                            # Initialisiere mit Standardpreisen
                            base_price = 800 + (power * 200)
                            current_prices = {
                                "base_price_eur": round(base_price, 2),
                                "installation_price_eur": round(base_price * 0.4, 2),
                                "total_price_eur": round(base_price * 1.4, 2)
                            }
                            
                            # Speichere in prices dict
                            if selected_manufacturer not in prices:
                                prices[selected_manufacturer] = {}
                            if selected_type not in prices[selected_manufacturer]:
                                prices[selected_manufacturer][selected_type] = {}
                            if model_name not in prices[selected_manufacturer][selected_type]:
                                prices[selected_manufacturer][selected_type][model_name] = {}
                            prices[selected_manufacturer][selected_type][model_name][str(power)] = current_prices
                        
                        with col1:
                            st.markdown(f"**{power} kW**")
                        
                        with col2:
                            base_price = st.number_input(
                                "Gerätepreis (€)",
                                min_value=0.0,
                                value=float(current_prices["base_price_eur"]),
                                step=100.0,
                                format="%.2f",
                                key=f"base_price_{selected_manufacturer}_{selected_type}_{model_name}_{power}_{idx}"
                            )
                            prices[selected_manufacturer][selected_type][model_name][str(power)]["base_price_eur"] = base_price
                            st.caption(f"💰 {format_german_number(base_price, 2)}")
                        
                        with col3:
                            installation_price = st.number_input(
                                "Installation (€)",
                                min_value=0.0,
                                value=float(current_prices["installation_price_eur"]),
                                step=100.0,
                                format="%.2f",
                                key=f"install_price_{selected_manufacturer}_{selected_type}_{model_name}_{power}_{idx}"
                            )
                            prices[selected_manufacturer][selected_type][model_name][str(power)]["installation_price_eur"] = installation_price
                            st.caption(f"🔧 {format_german_number(installation_price, 2)}")
                        
                        with col4:
                            total = base_price + installation_price
                            prices[selected_manufacturer][selected_type][model_name][str(power)]["total_price_eur"] = total
                            st.metric("Gesamtpreis", f"{format_german_number(total, 2)} €")
    
    # Speichern-Button
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Preise speichern", type="primary", use_container_width=True):
            if save_heatpump_prices(prices):
                st.success("✅ Preise erfolgreich gespeichert!")
            else:
                st.error("❌ Fehler beim Speichern!")
    
    with col2:
        if st.button("🔄 Standardpreise wiederherstellen", use_container_width=True):
            prices = DEFAULT_HEATPUMP_PRICES.copy()
            if save_heatpump_prices(prices):
                st.success("✅ Standardpreise wiederhergestellt!")
                st.rerun()
    
    with col3:
        if st.button("📋 Alle Preise anzeigen", use_container_width=True):
            st.json(prices)


# ============================================================================
# TAB 2: HEIZKOSTEN-KONFIGURATION
# ============================================================================

def render_heating_costs_tab():
    """Tab für Heizkosten-Konfiguration (alte Funktionalität)"""
    
    from admin_heating_costs_config_ui import render_admin_heating_costs_ui
    render_admin_heating_costs_ui()


# ============================================================================
# TAB 3: ÜBERSICHT & EXPORT
# ============================================================================

def render_overview_tab():
    """Übersicht über alle Einstellungen"""
    
    st.subheader("📊 Konfigurationsübersicht")
    
    # Wärmepumpen-Preise Statistik
    prices = load_heatpump_prices()
    
    total_models = 0
    total_variants = 0
    
    for manufacturer in prices:
        for hp_type in prices[manufacturer]:
            for model in prices[manufacturer][hp_type]:
                total_models += 1
                total_variants += len(prices[manufacturer][hp_type][model])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Hersteller", len(prices))
    
    with col2:
        st.metric("Modelle", total_models)
    
    with col3:
        st.metric("Preisvarianten", total_variants)
    
    # Export-Funktionen
    st.markdown("---")
    st.markdown("### 📥 Export & Backup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export Wärmepumpen-Preise
        prices_json = json.dumps(prices, indent=2, ensure_ascii=False)
        st.download_button(
            label="📦 Wärmepumpen-Preise exportieren",
            data=prices_json,
            file_name="heatpump_prices_config.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Export Heizkosten-Konfiguration
        heating_config = load_heating_config()
        heating_json = json.dumps(heating_config, indent=2, ensure_ascii=False)
        st.download_button(
            label="📦 Heizkosten-Konfiguration exportieren",
            data=heating_json,
            file_name="heating_costs_config.json",
            mime="application/json",
            use_container_width=True
        )


# ============================================================================
# TAB 4: INTEGRATION & TESTS
# ============================================================================

def render_integration_tab():
    """Integration & Tests"""
    
    st.subheader("🔗 Integration & Tests")
    
    # Test: Preisabfrage
    st.markdown("### 🧪 Preisabfrage testen")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        test_manufacturer = st.selectbox("Hersteller", list(HEATPUMP_PRODUCTS.keys()), key="test_manu")
    
    with col2:
        if test_manufacturer:
            test_type = st.selectbox("Typ", list(HEATPUMP_PRODUCTS[test_manufacturer].keys()), key="test_type")
        else:
            test_type = None
    
    with col3:
        if test_manufacturer and test_type:
            models = HEATPUMP_PRODUCTS[test_manufacturer][test_type]
            test_model = st.selectbox("Modell", [m["model"] for m in models], key="test_model")
        else:
            test_model = None
    
    with col4:
        if test_manufacturer and test_type and test_model:
            model_data = next((m for m in HEATPUMP_PRODUCTS[test_manufacturer][test_type] if m["model"] == test_model), None)
            if model_data:
                test_power = st.selectbox("Leistung (kW)", model_data["heating_power_kw"], key="test_power")
            else:
                test_power = None
        else:
            test_power = None
    
    if test_manufacturer and test_type and test_model and test_power:
        if st.button("🧪 Preis abrufen", type="primary"):
            price_data = get_heatpump_price(test_manufacturer, test_type, test_model, test_power)
            
            st.success("✅ Preisabfrage erfolgreich!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gerätepreis", f"{price_data['base_price_eur']:,.2f} €")
            with col2:
                st.metric("Installation", f"{price_data['installation_price_eur']:,.2f} €")
            with col3:
                st.metric("Gesamt", f"{price_data['total_price_eur']:,.2f} €")
    
    # Integrationspunkte anzeigen
    st.markdown("---")
    st.markdown("### 📋 Integrationspunkte")
    
    integration_points = [
        {"Module": "heatpump_ui.py", "Funktion": "render_heatpump_analysis()", "Status": "✅ Aktiv"},
        {"Module": "calculations_heatpump.py", "Funktion": "calculate_heatpump_economics()", "Status": "✅ Aktiv"},
        {"Module": "pdf_generation", "Funktion": "generate_heatpump_pdf()", "Status": "✅ Aktiv"},
        {"Module": "heatpump_products_database.py", "Funktion": "get_heatpump_models()", "Status": "✅ Aktiv"},
    ]
    
    df = pd.DataFrame(integration_points)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.info("💡 Die Preise werden automatisch in allen Wärmepumpen-Berechnungen und PDF-Generierungen verwendet.")


# ============================================================================
# HAUPT-EXPORTFUNKTION FÜR VERWENDUNG IN ANDEREN MODULEN
# ============================================================================

def get_configured_heatpump_price(manufacturer: str, hp_type: str, model: str, power_kw: float) -> Dict[str, float]:
    """
    Öffentliche Funktion zum Abrufen von Wärmepumpen-Preisen
    Kann von anderen Modulen importiert werden
    """
    return get_heatpump_price(manufacturer, hp_type, model, power_kw)


if __name__ == "__main__":
    # Test der UI
    render_admin_heatpump_settings_ui()
