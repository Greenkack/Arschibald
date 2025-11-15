

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
    ZUERST: Suche in product_db.py (echte Produktdatenbank)
    FALLBACK: Suche in statischer Konfiguration
    
    Args:
        manufacturer: Hersteller (z.B. "Viessmann")
        hp_type: Typ (z.B. "Luft-Wasser-Wärmepumpe")
        model: Modellname (z.B. "Vitocal 250-A")
        power_kw: Heizleistung in kW
    
    Returns:
        Dict mit base_price_eur, installation_price_eur, total_price_eur
    """
    
    # SCHRITT 1: SUCHE IN ECHTER PRODUKTDATENBANK (product_db.py)
    try:
        from product_db import get_product_by_model_name
        
        db_product = get_product_by_model_name(model)
        if db_product and db_product.get('price_euro', 0) > 0:
            # Produkt gefunden mit gültigem Preis!
            base_price = float(db_product.get('price_euro', 0))
            installation_price = base_price * 0.4  # 40% für Installation
            total_price = base_price + installation_price
            
            return {
                "base_price_eur": round(base_price, 2),
                "installation_price_eur": round(installation_price, 2),
                "total_price_eur": round(total_price, 2)
            }
    except Exception:
        pass  # Fallback zu statischer Konfiguration
    
    # SCHRITT 2: FALLBACK AUF STATISCHE KONFIGURATION
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
        st.warning(f"Preis nicht in Konfiguration gefunden: {manufacturer} {model} {power_kw}kW. Nutze Standardberechnung.")
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
        "Wärmepumpen-Preise",
        "Heizkosten-Konfiguration",
        "� Bulk-Upload",  # NEU: Bulk-Upload Tab
        "�Übersicht & Export",
        "🔗 Integration & Tests"
    ])
    
    # Tab 1: Wärmepumpen-Preise
    with tabs[0]:
        render_heatpump_prices_tab()
    
    # Tab 2: Heizkosten-Konfiguration
    with tabs[1]:
        render_heating_costs_tab()
    
    # Tab 3: Bulk-Upload (NEU!)
    with tabs[2]:
        render_bulk_upload_tab()
    
    # Tab 4: Übersicht & Export
    with tabs[3]:
        render_overview_tab()
    
    # Tab 5: Integration & Tests
    with tabs[4]:
        render_integration_tab()


# ============================================================================
# TAB 1: WÄRMEPUMPEN-PREISE
# ============================================================================

def render_heatpump_prices_tab():
    """Tab für Wärmepumpen-Preise"""
    
    st.subheader("Wärmepumpen-Preise verwalten")
    st.caption("Preise für alle Hersteller, Typen, Modelle und Leistungsstufen")
    
    # Lade aktuelle Preise
    prices = load_heatpump_prices()
    
    # Hersteller-Auswahl
    if not HEATPUMP_PRODUCTS:
        st.error("Produktdatenbank konnte nicht geladen werden!")
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
                
                with st.expander(f"{model_name} (SCOP: {scop})"):
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
                            st.caption(f"{format_german_number(base_price, 2)}")
                        
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
                            st.caption(f"{format_german_number(installation_price, 2)}")
                        
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
                st.success("Preise erfolgreich gespeichert!")
            else:
                st.error("Fehler beim Speichern!")
    
    with col2:
        if st.button("🔄 Standardpreise wiederherstellen", use_container_width=True):
            prices = DEFAULT_HEATPUMP_PRICES.copy()
            if save_heatpump_prices(prices):
                st.success("Standardpreise wiederhergestellt!")
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
    
    st.subheader("Konfigurationsübersicht")
    
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
            label="Wärmepumpen-Preise exportieren",
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
            label="Heizkosten-Konfiguration exportieren",
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
            
            st.success("Preisabfrage erfolgreich!")
            
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
        {"Module": "heatpump_ui.py", "Funktion": "render_heatpump_analysis()", "Status": "Aktiv"},
        {"Module": "calculations_heatpump.py", "Funktion": "calculate_heatpump_economics()", "Status": "Aktiv"},
        {"Module": "pdf_generation", "Funktion": "generate_heatpump_pdf()", "Status": "Aktiv"},
        {"Module": "heatpump_products_database.py", "Funktion": "get_heatpump_models()", "Status": "Aktiv"},
    ]
    
    df = pd.DataFrame(integration_points)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.info("Die Preise werden automatisch in allen Wärmepumpen-Berechnungen und PDF-Generierungen verwendet.")


# ============================================================================
# TAB 3: BULK-UPLOAD
# ============================================================================

def clean_heatpump_data(df: pd.DataFrame) -> pd.DataFrame:
    """Bereinigt und korrigiert Wärmepumpen-Daten"""
    
    import pandas as pd
    import numpy as np
    
    # Brand-Korrektur: FISMAN → Viessmann, PODEROS → Buderus, PHYLAND → Vaillant
    brand_mapping = {
        'FISMAN': 'Viessmann',
        'PODEROS': 'Buderus',
        'PHYLAND': 'Vaillant',
        'fisman': 'Viessmann',
        'poderos': 'Buderus',
        'phyland': 'Vaillant'
    }
    
    # Arbeite mit manufacturer (nach Mapping)
    if 'manufacturer' in df.columns:
        df['manufacturer'] = df['manufacturer'].replace(brand_mapping)
    
    # SKU-basierte Brand-Erkennung und Model-Korrektur
    if 'sku' in df.columns:
        for idx, row in df.iterrows():
            sku = str(row.get('sku', ''))
            sku_lower = sku.lower()
            
            # Hersteller aus SKU extrahieren (case-insensitive)
            if sku_lower.startswith('buderus-') or sku_lower.startswith('buderus_'):
                df.at[idx, 'manufacturer'] = 'Buderus'
                # SKU als Model Name verwenden (ohne Prefix)
                if 'model' in df.columns:
                    model_from_sku = sku.split('-', 1)[1] if '-' in sku else sku.split('_', 1)[1] if '_' in sku else sku
                    parts = model_from_sku.rsplit('-', 1)
                    if len(parts) > 1 and parts[-1].isdigit() and len(parts[-1]) > 8:
                        model_from_sku = parts[0]
                    df.at[idx, 'model'] = model_from_sku
                    
            elif sku_lower.startswith('viessmann-') or sku_lower.startswith('viessmann_'):
                df.at[idx, 'manufacturer'] = 'Viessmann'
                if 'model' in df.columns:
                    model_from_sku = sku.split('-', 1)[1] if '-' in sku else sku.split('_', 1)[1] if '_' in sku else sku
                    parts = model_from_sku.rsplit('-', 1)
                    if len(parts) > 1 and parts[-1].isdigit() and len(parts[-1]) > 8:
                        model_from_sku = parts[0]
                    df.at[idx, 'model'] = model_from_sku
                    
            elif sku_lower.startswith('vaillant-') or sku_lower.startswith('vaillant_'):
                df.at[idx, 'manufacturer'] = 'Vaillant'
                if 'model' in df.columns:
                    model_from_sku = sku.split('-', 1)[1] if '-' in sku else sku.split('_', 1)[1] if '_' in sku else sku
                    parts = model_from_sku.rsplit('-', 1)
                    if len(parts) > 1 and parts[-1].isdigit() and len(parts[-1]) > 8:
                        model_from_sku = parts[0]
                    df.at[idx, 'model'] = model_from_sku
    
    # Model bereinigen: "HeizungsDiscount24 GmbH" und ähnliche entfernen
    unwanted_names = [
        'HeizungsDiscount24 GmbH',
        'HeizungsDiscount24',
        'Heizungsdiscount',
        'GmbH',
        'Amazon',
        'eBay'
    ]
    
    if 'model' in df.columns:
        for unwanted in unwanted_names:
            df['model'] = df['model'].str.replace(unwanted, '', case=False, regex=False)
        
        # Trimme Whitespace
        df['model'] = df['model'].str.strip()
        
        # Entferne reine Zahlen als Modellnamen
        # Behalte nur Models mit mindestens einem Buchstaben
        df = df[df['model'].str.contains(r'[A-Za-z]', na=False)]
        
        # Entferne zu kurze Models (< 3 Zeichen)
        df = df[df['model'].str.len() >= 3]
        
        # Formatiere Modellnamen: Großbuchstaben am Anfang, Rest klein (außer bei Codes)
        for idx, row in df.iterrows():
            model = str(row.get('model', ''))
            
            # Wenn Model nur aus Großbuchstaben und Zahlen besteht (z.B. "VWL-250"), behalte es
            if not model.isupper() and not any(char.isdigit() for char in model):
                # Sonst: Title Case
                df.at[idx, 'model'] = model.title()
        
        # Entferne leere Models
        df = df[df['model'].str.len() > 0]
    
    # Type-Korrektur: MONOBLOC → Luft-Wasser-Wärmepumpe
    type_mapping = {
        'MONOBLOC': 'Luft-Wasser-Wärmepumpe',
        'SPLIT': 'Luft-Wasser-Wärmepumpe',
        'SOLE': 'Sole-Wasser-Wärmepumpe',
        'ERDWÄRME': 'Sole-Wasser-Wärmepumpe',
        'GRUNDWASSER': 'Wasser-Wasser-Wärmepumpe',
        'WASSER': 'Wasser-Wasser-Wärmepumpe',
        'LUFT-WASSER': 'Luft-Wasser-Wärmepumpe',
        'SOLE-WASSER': 'Sole-Wasser-Wärmepumpe',
        'WASSER-WASSER': 'Wasser-Wasser-Wärmepumpe'
    }
    
    if 'heatpump_type' in df.columns:
        df['heatpump_type'] = df['heatpump_type'].str.upper()
        df['heatpump_type'] = df['heatpump_type'].replace(type_mapping)
    
    # SCOP-Werte bereinigen
    if 'scop' in df.columns:
        # NaN durch 4.0 ersetzen
        df['scop'] = df['scop'].fillna(4.0)
        # Ungültige Werte (< 2.0 oder > 6.0) auf 4.0 setzen
        df.loc[(df['scop'] < 2.0) | (df['scop'] > 6.0), 'scop'] = 4.0
    
    # Max Flow Temp bereinigen
    if 'max_flow_temp' in df.columns:
        # NaN durch 65 ersetzen
        df['max_flow_temp'] = df['max_flow_temp'].fillna(65)
        # Ungültige Werte (< 45 oder > 80) auf 65 setzen
        df.loc[(df['max_flow_temp'] < 45) | (df['max_flow_temp'] > 80), 'max_flow_temp'] = 65
    
    # Price Range bereinigen
    if 'price_range' in df.columns:
        # Entferne ungültige Preisklassen
        valid_ranges = ['€', '€€', '€€€', '€€€€']
        # Wenn price_range keine gültige Preisklasse ist und numerisch aussieht, berechne aus Preis
        for idx, val in df['price_range'].items():
            if pd.notna(val) and str(val) not in valid_ranges:
                # Versuche als Zahl zu interpretieren
                try:
                    price = float(str(val).replace('€', '').strip())
                    if price < 8000:
                        df.at[idx, 'price_range'] = '€'
                    elif price < 12000:
                        df.at[idx, 'price_range'] = '€€'
                    elif price < 18000:
                        df.at[idx, 'price_range'] = '€€€'
                    else:
                        df.at[idx, 'price_range'] = '€€€€'
                except:
                    # Fallback: €€
                    df.at[idx, 'price_range'] = '€€'
        
        # NaN-Werte auffüllen
        df['price_range'] = df['price_range'].fillna('€€')
    
    # Duplikate entfernen (behalte erste)
    if 'manufacturer' in df.columns and 'heatpump_type' in df.columns and 'model' in df.columns:
        df = df.drop_duplicates(subset=['manufacturer', 'heatpump_type', 'model'], keep='first')
    
    return df


def render_bulk_upload_tab():
    """Tab für Bulk-Upload von Wärmepumpen-Daten"""
    
    st.subheader("📤 Bulk-Upload Wärmepumpen-Daten")
    st.caption("Importieren Sie mehrere Wärmepumpen gleichzeitig via CSV, Excel oder JSON")
    
    # Info-Box mit Formatbeschreibung
    with st.expander("Format-Informationen & Beispiele", expanded=False):
        st.markdown("""
        ### 📋 Erforderliche Spalten/Felder:
        
        | Feld | Beschreibung | Beispiel |
        |------|--------------|----------|
        | `manufacturer` | Hersteller | Viessmann, Buderus, Vaillant |
        | `heatpump_type` | Typ | Luft-Wasser-Wärmepumpe, Sole-Wasser-Wärmepumpe, Wasser-Wasser-Wärmepumpe |
        | `model` | Modellname | Vitocal 250-A, aroTHERM plus, Logatherm WLW196i AR |
        | `heating_power_kw` | Leistungen in kW (kommasepariert) | 6.0,8.0,10.0,12.0 oder 8.5 |
        | `scop` | Jahresarbeitszahl | 4.6, 4.5, 5.1 |
        | `max_flow_temp` | Max. Vorlauftemperatur °C | 65, 70, 75 |
        | `price_range` | Preisklasse | €, €€, €€€, €€€€ |
        | `features` | Features (optional, pipe-separiert) | Smart Grid Ready&#124;Active Cooling |
        | `refrigerant` | Kältemittel (optional) | R290 (Propan), R32 |
        | `rating` | Bewertung (optional) | 4.5, 4.8, 5.0 |
        | `awards` | Auszeichnungen (optional, pipe-separiert) | Testsieger 2024&#124;Öko-Test SEHR GUT |
        
        ### CSV-Format Beispiel:
        ```csv
        manufacturer,heatpump_type,model,heating_power_kw,scop,max_flow_temp,price_range,features,refrigerant,rating,awards
        Viessmann,Luft-Wasser-Wärmepumpe,Vitocal 250-A,"6.0,8.0,10.0,12.0",4.6,70,€€€,Smart Grid Ready|Active Cooling,R290 (Propan),4.8,Testsieger 2024
        Vaillant,Luft-Wasser-Wärmepumpe,aroTHERM plus,8.5,4.5,65,€€,Smart Grid Ready,R32,4.5,
        Buderus,Sole-Wasser-Wärmepumpe,Logatherm WSW196i,"8.0,11.0,15.0",5.1,70,€€€,Erdwärmesonden|Smart Grid,R290 (Propan),4.7,
        ```
        
        ### Excel-Format:
        - Erste Zeile: Spaltenüberschriften (wie oben)
        - Ab Zeile 2: Daten
        - Bei mehreren Leistungswerten: Kommasepariert in einer Zelle
        
        ### JSON-Format Beispiel:
        ```json
        [
            {
                "manufacturer": "Viessmann",
                "heatpump_type": "Luft-Wasser-Wärmepumpe",
                "model": "Vitocal 250-A",
                "heating_power_kw": [6.0, 8.0, 10.0, 12.0],
                "scop": 4.6,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": ["Smart Grid Ready", "Active Cooling"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.8,
                "awards": ["Testsieger 2024"]
            }
        ]
        ```
        """)
    
    # Upload-Bereich
    st.markdown("### Datei hochladen")
    
    upload_format = st.radio(
        "Format wählen:",
        ["CSV", "Excel (XLSX)", "JSON"],
        horizontal=True,
        help="Wählen Sie das Format Ihrer Upload-Datei"
    )
    
    uploaded_file = None
    
    if upload_format == "CSV":
        uploaded_file = st.file_uploader(
            "CSV-Datei hochladen",
            type=['csv'],
            help="CSV-Datei mit Komma- oder Semikolon-Trennung"
        )
    elif upload_format == "Excel (XLSX)":
        uploaded_file = st.file_uploader(
            "Excel-Datei hochladen",
            type=['xlsx', 'xls'],
            help="Excel-Datei (.xlsx oder .xls)"
        )
    else:  # JSON
        uploaded_file = st.file_uploader(
            "JSON-Datei hochladen",
            type=['json'],
            help="JSON-Datei mit Array von Wärmepumpen-Objekten"
        )
    
    if uploaded_file is not None:
        try:
            # Datei verarbeiten
            import pandas as pd
            import json
            import io
            
            df = None
            
            if upload_format == "CSV":
                # CSV einlesen (Auto-detect Delimiter)
                df = pd.read_csv(uploaded_file, sep=None, engine='python')
                st.success(f"CSV-Datei eingelesen: {len(df)} Zeilen")
                
            elif upload_format == "Excel (XLSX)":
                # Excel einlesen
                df = pd.read_excel(uploaded_file)
                st.success(f"Excel-Datei eingelesen: {len(df)} Zeilen")
                
            else:  # JSON
                # JSON einlesen
                content = uploaded_file.read().decode('utf-8')
                data = json.loads(content)
                
                # Prüfen ob es verschachtelte HEATPUMP_PRODUCTS-Struktur ist
                if isinstance(data, dict) and any(isinstance(v, dict) for v in data.values()):
                    # Verschachtelte Struktur: {Hersteller: {Typ: [Modelle]}}
                    st.info("Verschachtelte Datenbank-Struktur erkannt, wird in Tabelle konvertiert...")
                    flat_data = []
                    for manufacturer, types in data.items():
                        if isinstance(types, dict):
                            for heatpump_type, models in types.items():
                                if isinstance(models, list):
                                    for model in models:
                                        model_copy = model.copy()
                                        model_copy['manufacturer'] = manufacturer
                                        model_copy['heatpump_type'] = heatpump_type
                                        flat_data.append(model_copy)
                    data = flat_data
                
                df = pd.DataFrame(data)
                st.success(f"JSON-Datei eingelesen: {len(df)} Zeilen")
            
            # Datenvalidierung
            required_columns = ['manufacturer', 'heatpump_type', 'model', 'heating_power_kw', 'scop', 'max_flow_temp', 'price_range']
            
            # Debug: Zeige vorhandene Spalten
            st.info(f"Gefundene Spalten: {', '.join(df.columns.tolist())}")
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                # Versuche Spalten-Mapping
                st.warning("Versuche automatisches Spalten-Mapping...")
                
                column_mapping = {}
                # Mögliche alternative Spaltennamen
                alternatives = {
                    'model': ['Model', 'Modell', 'name', 'Name', 'product_name'],
                    'heating_power_kw': ['heating_power', 'power_kw', 'power', 'Leistung', 'kW', 'sizes_kw'],
                    'max_flow_temp': ['max_temp', 'flow_temp', 'vorlauftemperatur', 'temp', 'max_flow_temp_c'],
                    'price_range': ['price', 'preis', 'preisklasse', 'price_eur', 'price_range_calc'],
                    'scop': ['SCOP', 'cop', 'COP', 'efficiency'],
                    'manufacturer': ['Manufacturer', 'Hersteller', 'brand', 'Brand'],
                    'heatpump_type': ['type', 'Type', 'Typ', 'category']
                }
                
                for required, alts in alternatives.items():
                    if required not in df.columns:
                        for alt in alts:
                            if alt in df.columns:
                                column_mapping[alt] = required
                                st.success(f"'{alt}' → '{required}'")
                                break
                
                if column_mapping:
                    df = df.rename(columns=column_mapping)
                    missing_columns = [col for col in required_columns if col not in df.columns]
                
                # Wenn price_range fehlt aber price_eur vorhanden ist, berechne Preisklasse
                if 'price_range' not in df.columns and 'price_eur' in df.columns:
                    st.info("Berechne Preisklassen aus Preisen...")
                    def calculate_price_range(price):
                        if pd.isna(price):
                            return '€€'
                        price = float(price)
                        if price < 8000:
                            return '€'
                        elif price < 12000:
                            return '€€'
                        elif price < 18000:
                            return '€€€'
                        else:
                            return '€€€€'
                    
                    df['price_range'] = df['price_eur'].apply(calculate_price_range)
                    st.success("Preisklassen berechnet")
                    missing_columns = [col for col in required_columns if col not in df.columns]
                
                # Nochmal prüfen nach allen Mappings
                if missing_columns:
                    st.error(f"Immer noch fehlende Felder: {', '.join(missing_columns)}")
                    
                    # Zeige erste Zeile als Beispiel
                    st.markdown("### Erste Zeile der Daten:")
                    st.json(df.head(1).to_dict(orient='records')[0] if len(df) > 0 else {})
                    
                    st.info("Bitte stellen Sie sicher, dass Ihre JSON-Datei die korrekten Feldnamen hat.")
                    return
                else:
                    st.success("Alle Pflichtfelder gefunden oder erfolgreich gemappt!")
            
            # JETZT Datenbereinigung durchführen (NACH dem Mapping!)
            st.info("🧹 Bereinige Daten...")
            df = clean_heatpump_data(df)
            st.success(f"Datenbereinigung abgeschlossen - {len(df)} Zeilen übrig")
            
            # Datenvorschau
            st.markdown("### 👀 Datenvorschau")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Statistiken
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesamt Wärmepumpen", len(df))
            with col2:
                st.metric("Hersteller", df['manufacturer'].nunique())
            with col3:
                st.metric("Typen", df['heatpump_type'].nunique())
            
            # Import-Optionen
            st.markdown("### ⚙️ Import-Optionen")
            
            col_opt1, col_opt2 = st.columns(2)
            
            with col_opt1:
                overwrite_existing = st.checkbox(
                    "Bestehende Einträge überschreiben",
                    value=False,
                    help="Wenn aktiviert, werden bestehende Wärmepumpen mit gleichen Daten überschrieben"
                )
            
            with col_opt2:
                validate_data = st.checkbox(
                    "Daten validieren",
                    value=True,
                    help="Prüft SCOP-Werte, Temperaturen und Preisklassen"
                )
            
            # Import-Button
            st.markdown("---")
            
            col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
            
            with col_btn1:
                if st.button("Import starten", type="primary", use_container_width=True):
                    import_heatpump_bulk_data(df, overwrite_existing, validate_data)
            
            with col_btn2:
                if st.button("📋 Validierung", use_container_width=True):
                    validate_bulk_data(df, validate_data)
            
            with col_btn3:
                if st.button("Abbrechen", use_container_width=True):
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Fehler beim Einlesen der Datei: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    # Template-Download
    st.markdown("---")
    st.markdown("### 📥 Vorlagen herunterladen")
    st.caption("Laden Sie eine Vorlage herunter um die richtige Struktur zu sehen")
    
    col_tpl1, col_tpl2, col_tpl3 = st.columns(3)
    
    with col_tpl1:
        # CSV-Template
        csv_template = """manufacturer,heatpump_type,model,heating_power_kw,scop,max_flow_temp,price_range,features,refrigerant,rating,awards
Viessmann,Luft-Wasser-Wärmepumpe,Vitocal 250-A,"6.0,8.0,10.0,12.0",4.6,70,€€€,Smart Grid Ready|Active Cooling,R290 (Propan),4.8,Testsieger 2024
Vaillant,Luft-Wasser-Wärmepumpe,aroTHERM plus,8.5,4.5,65,€€,Smart Grid Ready,R32,4.5,
Buderus,Sole-Wasser-Wärmepumpe,Logatherm WSW196i,"8.0,11.0,15.0",5.1,70,€€€,Erdwärmesonden|Smart Grid,R290 (Propan),4.7,"""
        
        st.download_button(
            label="CSV-Vorlage",
            data=csv_template,
            file_name="wärmepumpen_vorlage.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_tpl2:
        # Excel-Template
        import pandas as pd
        import io
        
        template_data = {
            'manufacturer': ['Viessmann', 'Vaillant', 'Buderus'],
            'heatpump_type': ['Luft-Wasser-Wärmepumpe', 'Luft-Wasser-Wärmepumpe', 'Sole-Wasser-Wärmepumpe'],
            'model': ['Vitocal 250-A', 'aroTHERM plus', 'Logatherm WSW196i'],
            'heating_power_kw': ['6.0,8.0,10.0,12.0', '8.5', '8.0,11.0,15.0'],
            'scop': [4.6, 4.5, 5.1],
            'max_flow_temp': [70, 65, 70],
            'price_range': ['€€€', '€€', '€€€'],
            'features': ['Smart Grid Ready|Active Cooling', 'Smart Grid Ready', 'Erdwärmesonden|Smart Grid'],
            'refrigerant': ['R290 (Propan)', 'R32', 'R290 (Propan)'],
            'rating': [4.8, 4.5, 4.7],
            'awards': ['Testsieger 2024', '', '']
        }
        
        template_df = pd.DataFrame(template_data)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Wärmepumpen')
        excel_buffer.seek(0)
        
        st.download_button(
            label="Excel-Vorlage",
            data=excel_buffer,
            file_name="wärmepumpen_vorlage.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col_tpl3:
        # JSON-Template
        import json
        
        json_template = [
            {
                "manufacturer": "Viessmann",
                "heatpump_type": "Luft-Wasser-Wärmepumpe",
                "model": "Vitocal 250-A",
                "heating_power_kw": [6.0, 8.0, 10.0, 12.0],
                "scop": 4.6,
                "max_flow_temp": 70,
                "price_range": "€€€",
                "features": ["Smart Grid Ready", "Active Cooling"],
                "refrigerant": "R290 (Propan)",
                "rating": 4.8,
                "awards": ["Testsieger 2024"]
            },
            {
                "manufacturer": "Vaillant",
                "heatpump_type": "Luft-Wasser-Wärmepumpe",
                "model": "aroTHERM plus",
                "heating_power_kw": [8.5],
                "scop": 4.5,
                "max_flow_temp": 65,
                "price_range": "€€",
                "features": ["Smart Grid Ready"],
                "refrigerant": "R32",
                "rating": 4.5,
                "awards": []
            }
        ]
        
        st.download_button(
            label="JSON-Vorlage",
            data=json.dumps(json_template, indent=2, ensure_ascii=False),
            file_name="wärmepumpen_vorlage.json",
            mime="application/json",
            use_container_width=True
        )


def validate_bulk_data(df: pd.DataFrame, validate_data: bool = True):
    """Validiert die Bulk-Daten vor dem Import"""
    
    st.markdown("### Validierungs-Ergebnisse")
    
    errors = []
    warnings = []
    
    # Pflichtfelder prüfen
    required_fields = ['manufacturer', 'heatpump_type', 'model', 'heating_power_kw', 'scop', 'max_flow_temp', 'price_range']
    for field in required_fields:
        null_count = df[field].isnull().sum()
        if null_count > 0:
            errors.append(f"{field}: {null_count} leere Werte gefunden")
    
    # Daten validieren
    if validate_data:
        # SCOP-Werte
        invalid_scop = df[(df['scop'] < 2.0) | (df['scop'] > 6.0)]
        if len(invalid_scop) > 0:
            warnings.append(f"{len(invalid_scop)} SCOP-Werte außerhalb 2.0-6.0")
        
        # Vorlauftemperatur
        invalid_temp = df[(df['max_flow_temp'] < 45) | (df['max_flow_temp'] > 80)]
        if len(invalid_temp) > 0:
            warnings.append(f"{len(invalid_temp)} Vorlauftemperaturen außerhalb 45-80 °C")
        
        # Preisklassen
        valid_price_ranges = ['€', '€€', '€€€', '€€€€']
        invalid_price_range = df[~df['price_range'].isin(valid_price_ranges)]
        if len(invalid_price_range) > 0:
            warnings.append(f"{len(invalid_price_range)} ungültige Preisklassen (erlaubt: {', '.join(valid_price_ranges)})")
    
    # Duplikate prüfen
    duplicates = df.duplicated(subset=['manufacturer', 'heatpump_type', 'model'], keep=False)
    if duplicates.sum() > 0:
        warnings.append(f"{duplicates.sum()} Duplikate gefunden (gleiche Hersteller/Typ/Modell)")
    
    # Hersteller prüfen
    known_manufacturers = ['Viessmann', 'Buderus', 'Vaillant']
    unknown_manufacturers = df[~df['manufacturer'].isin(known_manufacturers)]['manufacturer'].unique()
    if len(unknown_manufacturers) > 0:
        warnings.append(f"Unbekannte Hersteller: {', '.join(unknown_manufacturers)}")
    
    # Ergebnisse anzeigen
    if errors:
        for error in errors:
            st.error(error)
    
    if warnings:
        for warning in warnings:
            st.warning(warning)
    
    if not errors and not warnings:
        st.success("Alle Validierungen bestanden! Daten können importiert werden.")
    elif not errors:
        st.info("Validierung erfolgreich mit Warnungen. Import möglich.")
    else:
        st.error("Validierung fehlgeschlagen. Bitte Fehler korrigieren.")


def import_heatpump_bulk_data(df: pd.DataFrame, overwrite: bool = False, validate: bool = True):
    """Importiert Wärmepumpen-Daten aus DataFrame in die Datenbank"""
    
    # Validierung durchführen
    if validate:
        validate_bulk_data(df, validate)
    
    try:
        from heatpump_products_database import HEATPUMP_PRODUCTS
        import json
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        total = len(df)
        current = 0
        
        for idx, row in df.iterrows():
            try:
                current += 1
                # Fortschritt aktualisieren
                progress = min(current / total, 1.0)  # Limitiere auf max 1.0
                progress_bar.progress(progress)
                status_text.text(f"Importiere {current}/{total}: {row['manufacturer']} {row['model']}")
                
                manufacturer = str(row['manufacturer'])
                heatpump_type = str(row['heatpump_type'])
                
                # Hersteller-Struktur erstellen falls nicht vorhanden
                if manufacturer not in HEATPUMP_PRODUCTS:
                    HEATPUMP_PRODUCTS[manufacturer] = {}
                
                # Typ-Struktur erstellen falls nicht vorhanden
                if heatpump_type not in HEATPUMP_PRODUCTS[manufacturer]:
                    HEATPUMP_PRODUCTS[manufacturer][heatpump_type] = []
                
                # Prüfen ob Modell bereits existiert
                existing_models = HEATPUMP_PRODUCTS[manufacturer][heatpump_type]
                model_exists = any(m['model'] == str(row['model']) for m in existing_models)
                
                if model_exists and not overwrite:
                    skipped_count += 1
                    continue
                
                # Heating Power verarbeiten (kann String mit Kommas oder Array sein)
                heating_power = row['heating_power_kw']
                if isinstance(heating_power, str):
                    # String wie "6.0,8.0,10.0" in Liste umwandeln
                    heating_power_kw = [float(x.strip()) for x in heating_power.split(',')]
                elif isinstance(heating_power, (list, tuple)):
                    heating_power_kw = [float(x) for x in heating_power]
                else:
                    # Einzelwert
                    heating_power_kw = [float(heating_power)]
                
                # Features verarbeiten (kann String mit | oder Array sein)
                features = []
                if 'features' in row and pd.notna(row['features']):
                    if isinstance(row['features'], str):
                        features = [f.strip() for f in row['features'].split('|') if f.strip()]
                    elif isinstance(row['features'], list):
                        features = row['features']
                
                # Awards verarbeiten
                awards = []
                if 'awards' in row and pd.notna(row['awards']):
                    if isinstance(row['awards'], str):
                        awards = [a.strip() for a in row['awards'].split('|') if a.strip()]
                    elif isinstance(row['awards'], list):
                        awards = row['awards']
                
                # Neues Modell-Dict erstellen
                new_model = {
                    'model': str(row['model']),
                    'heating_power_kw': heating_power_kw,
                    'scop': float(row['scop']) if pd.notna(row['scop']) else 4.0,
                    'max_flow_temp': int(row['max_flow_temp']) if pd.notna(row['max_flow_temp']) else 65,
                    'price_range': str(row['price_range']),
                    'features': features,
                    'refrigerant': str(row.get('refrigerant', '')) if pd.notna(row.get('refrigerant')) else '',
                    'rating': float(row.get('rating', 0.0)) if pd.notna(row.get('rating')) else 0.0,
                    'awards': awards
                }
                
                # Modell hinzufügen oder überschreiben
                if model_exists and overwrite:
                    # Bestehendes Modell ersetzen
                    for i, m in enumerate(existing_models):
                        if m['model'] == str(row['model']):
                            HEATPUMP_PRODUCTS[manufacturer][heatpump_type][i] = new_model
                            break
                else:
                    # Neues Modell hinzufügen
                    HEATPUMP_PRODUCTS[manufacturer][heatpump_type].append(new_model)
                
                # Preise auch in heatpump_prices.json speichern (falls vorhanden)
                if 'price_eur' in row and pd.notna(row['price_eur']):
                    try:
                        prices = load_heatpump_prices()
                        
                        # Struktur erstellen
                        if manufacturer not in prices:
                            prices[manufacturer] = {}
                        if heatpump_type not in prices[manufacturer]:
                            prices[manufacturer][heatpump_type] = {}
                        if str(row['model']) not in prices[manufacturer][heatpump_type]:
                            prices[manufacturer][heatpump_type][str(row['model'])] = {}
                        
                        # Für jede Leistungsvariante Preis setzen
                        for power in heating_power_kw:
                            power_str = str(power)
                            base_price = float(row['price_eur'])
                            installation = base_price * 0.3  # 30% Installationskosten
                            
                            prices[manufacturer][heatpump_type][str(row['model'])][power_str] = {
                                "base_price_eur": round(base_price, 2),
                                "installation_price_eur": round(installation, 2),
                                "total_price_eur": round(base_price + installation, 2)
                            }
                        
                        # Speichere Preise
                        save_heatpump_prices(prices)
                    except Exception as price_error:
                        # Ignoriere Preisfehler, importiere trotzdem das Modell
                        pass
                
                success_count += 1
                        
            except Exception as e:
                error_count += 1
                st.warning(f"Zeile {idx + 1}: {e}")
        
        # Datenbank-Datei aktualisieren
        try:
            st.info("💾 Speichere Daten in heatpump_products_database.py...")
            
            # heatpump_products_database.py neu schreiben
            db_file_path = "heatpump_products_database.py"
            
            # Lese Original-Datei
            with open(db_file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Finde Anfang und Ende des HEATPUMP_PRODUCTS Dictionary
            start_marker = 'HEATPUMP_PRODUCTS = {'
            start_pos = original_content.find(start_marker)
            
            if start_pos == -1:
                raise ValueError("HEATPUMP_PRODUCTS nicht gefunden in Datei")
            
            # Finde das Ende - suche nach der letzten Funktion
            func_marker = '\n\ndef get_heatpump_models'
            func_pos = original_content.find(func_marker)
            
            if func_pos == -1:
                raise ValueError("Funktionen nicht gefunden in Datei")
            
            # Teile: Header (bis HEATPUMP_PRODUCTS) + neue Daten + Funktionen
            header = original_content[:start_pos]
            functions = original_content[func_pos:]
            
            # Erstelle JSON-String mit korrektem Python-Format
            import json
            json_str = json.dumps(HEATPUMP_PRODUCTS, indent=4, ensure_ascii=False)
            
            # Ersetze JSON-null mit Python-4.0 für fehlende SCOP-Werte
            json_str = json_str.replace(': null', ': 4.0')
            
            # Schreibe neue Datei
            new_content = f"{header}HEATPUMP_PRODUCTS = {json_str}\n{functions}"
            
            with open(db_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            st.success(f"{success_count} Wärmepumpen in heatpump_products_database.py gespeichert!")
            
        except Exception as e:
            st.error(f"Fehler beim Speichern: {e}")
            import traceback
            st.code(traceback.format_exc())
        
        # Abschluss
        progress_bar.progress(1.0)
        status_text.empty()
        progress_bar.empty()
        
        # Ergebnis anzeigen
        st.markdown("---")
        st.markdown("### Import-Ergebnis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Erfolgreich", success_count)
        with col2:
            st.metric("Übersprungen", skipped_count)
        with col3:
            st.metric("Fehler", error_count)
        
        if success_count > 0:
            st.success(f"{success_count} Wärmepumpen erfolgreich importiert!")
        
        if skipped_count > 0:
            st.info(f"{skipped_count} Einträge übersprungen (bereits vorhanden). Aktivieren Sie 'Bestehende Einträge überschreiben' um diese zu aktualisieren.")
        
        if error_count > 0:
            st.error(f"{error_count} Fehler beim Import aufgetreten.")
            
    except Exception as e:
        st.error(f"Kritischer Fehler beim Import: {e}")
        import traceback

__all__ = [
    'CONFIG_DIR',
    'DEFAULT_HEATING_CONFIG',
    'DEFAULT_HEATPUMP_PRICES',
    'HEATING_COSTS_CONFIG_FILE',
    'HEATPUMP_PRICES_CONFIG_FILE',
    'HEATPUMP_PRODUCTS',
    'calculate_price_range',
    'clean_heatpump_data',
    'create_default_heatpump_prices',
    'format_german_number',
    'get_configured_heatpump_price',
    'get_heatpump_price',
    'import_heatpump_bulk_data',
    'load_heating_config',
    'load_heatpump_prices',
    'render_admin_heatpump_settings_ui',
    'render_bulk_upload_tab',
    'render_heating_costs_tab',
    'render_heatpump_prices_tab',
    'render_integration_tab',
    'render_overview_tab',
    'save_heating_config',
    'save_heatpump_prices',
    'validate_bulk_data',
]

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
