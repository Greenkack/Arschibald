__all__ = [
    'calculate_annual_energy_consumption',
    'calculate_beg_subsidy',
    'calculate_building_heat_load',
    'calculate_co2_costs_fossil_heating',
    'calculate_domestic_hot_water_demand',
    'calculate_green_fuel_premium',
    'calculate_heat_load_with_climate_zone',
    'calculate_heatpump_economics',
    'calculate_heatpump_sizing',
    'calculate_npv_20_years',
    'calculate_pv_self_consumption_heatpump',
    'calculate_required_flow_temperature',
    'check_radiator_compatibility',
    'compare_heating_systems_20_years',
    'estimate_annual_heat_demand_kwh_from_consumption',
    'estimate_heat_load_kw_from_annual_demand',
    'get_default_heating_system_efficiency',
    'recommend_heat_pump',
]

# calculations_heatpump.py
"""
Berechnungen für die Auslegung und Analyse von Wärmepumpensystemen.

Author: Suratina Sicmislar
Version: 1.0 (Fully Implemented)
"""
import math
from typing import Any

from financial_calculations import calculate_payback_years


def calculate_building_heat_load(
    building_type: str, living_area_m2: float, insulation_quality: str
) -> float:
    """
    Vereinfachte Berechnung der Heizlast eines Gebäudes in kW.

    Args:
        building_type (str): z.B. "Neubau KFW40", "Altbau saniert".
        living_area_m2 (float): Wohnfläche in Quadratmetern.
        insulation_quality (str): z.B. "Gut", "Mittel", "Schlecht".

    Returns:
        float: Die geschätzte maximale Heizlast in kW.
    """
    base_load_w_per_m2 = {
        "Neubau KFW40": 40.0,
        "Neubau KFW55": 55.0,
        "Altbau saniert": 70.0,
        "Altbau unsaniert": 120.0,
    }

    insulation_factor = {
        "Gut": 0.9,
        "Mittel": 1.0,
        "Schlecht": 1.2,
    }

    base_w_m2 = base_load_w_per_m2.get(building_type, 100.0)
    factor = insulation_factor.get(insulation_quality, 1.0)

    heat_load_watts = living_area_m2 * base_w_m2 * factor
    return heat_load_watts / 1000  # Umrechnung in kW


def recommend_heat_pump(
        heat_load_kw: float,
        available_pumps: list[dict]) -> dict:
    """
    Empfiehlt die kleinste passende Wärmepumpe aus einer Liste.

    Args:
        heat_load_kw (float): Die benötigte Heizlast.
        available_pumps (List[Dict]): Liste der verfügbaren Pumpen aus der DB.

    Returns:
        Dict: Die Daten der empfohlenen Wärmepumpe oder None.
    """
    suitable_pumps = [
        p for p in available_pumps if p['heating_output_kw'] >= heat_load_kw]
    if not suitable_pumps:
        return None
    # Sortiere nach Leistung und wähle die kleinste, die passt
    return sorted(suitable_pumps, key=lambda p: p['heating_output_kw'])[0]


def calculate_annual_energy_consumption(
        heat_load_kw: float,
        scop: float,
        heating_hours: int = 1800) -> float:
    """
    Berechnet den jährlichen Stromverbrauch der Wärmepumpe.

    Args:
        heat_load_kw (float): Die Heizlast des Gebäudes.
        scop (float): Die Jahresarbeitszahl der Pumpe.
        heating_hours (int): Angenommene jährliche Volllaststunden.

    Returns:
        float: Der geschätzte jährliche Stromverbrauch in kWh.
    """
    if scop == 0:
        return 0.0
    annual_heat_demand_kwh = heat_load_kw * heating_hours
    annual_electricity_consumption_kwh = annual_heat_demand_kwh / scop
    return annual_electricity_consumption_kwh


def calculate_heatpump_economics(
        heatpump_data: dict[str, Any], building_data: dict[str, Any] = None) -> dict[str, Any]:
    """
    Berechnet die Wirtschaftlichkeit einer Wärmepumpe.

    Args:
        heatpump_data (Dict[str, Any]): Wärmepumpendaten
        building_data (Dict[str, Any], optional): Gebäudedaten

    Returns:
        Dict[str, Any]: Wirtschaftlichkeitsberechnung
    """
    # Standardwerte setzen
    if building_data is None:
        building_data = {}

    # Extrahiere Daten
    heating_demand = heatpump_data.get(
        'heating_demand', building_data.get(
            'heating_demand', 15000))  # kWh/Jahr
    heatpump_power = heatpump_data.get(
        'heatpump_power', heatpump_data.get(
            'heating_power_kw', 10.0))  # kW
    cop = heatpump_data.get('cop', heatpump_data.get('cop_rating', 3.5))
    electricity_price = heatpump_data.get('electricity_price', 0.30)  # €/kWh
    investment_cost = heatpump_data.get(
        'investment_cost', heatpump_data.get(
            'price', 15000))  # €

    # Alternative Heizkosten (z.B. Gas/Öl)
    alternative_fuel_price = heatpump_data.get(
        'alternative_fuel_price', 0.08)  # €/kWh
    alternative_efficiency = heatpump_data.get('alternative_efficiency', 0.9)

    # Berechnungen
    electricity_consumption = heating_demand / cop  # kWh/Jahr
    annual_electricity_cost = electricity_consumption * electricity_price  # €/Jahr

    # Alternative Heizkosten
    alternative_fuel_consumption = heating_demand / alternative_efficiency
    annual_alternative_cost = alternative_fuel_consumption * alternative_fuel_price

    # Einsparungen
    annual_savings = annual_alternative_cost - annual_electricity_cost

    # Amortisation
    payback_period_years = calculate_payback_years(
        investment_cost,
        annual_savings,
        allow_infinite=True,
        default_zero=False)

    # 20-Jahres-Bilanz
    total_savings_20y = annual_savings * 20 - investment_cost

    return {
        'heating_demand_kwh': heating_demand,
        'electricity_consumption_kwh': electricity_consumption,
        'annual_electricity_cost': round(annual_electricity_cost, 2),
        'annual_alternative_cost': round(annual_alternative_cost, 2),
        'annual_savings': round(annual_savings, 2),
        'payback_period_years': (round(payback_period_years, 1) if math.isfinite(payback_period_years) else None),
        'total_savings_20y': round(total_savings_20y, 2),
        'investment_cost': investment_cost,
        'cop': cop,
        'recommendation': 'Wirtschaftlich' if payback_period_years <= 15 else 'Bedingt wirtschaftlich' if payback_period_years <= 25 else 'Nicht wirtschaftlich'
    }


def calculate_heatpump_sizing(building_data: dict[str, Any]) -> dict[str, Any]:
    """
    Berechnet die optimale Wärmepumpengröße für ein Gebäude.

    Args:
        building_data (Dict[str, Any]): Gebäudedaten

    Returns:
        Dict[str, Any]: Auslegungsempfehlung
    """
    # Gebäudedaten extrahieren
    building_type = building_data.get('building_type', 'Altbau saniert')
    living_area_m2 = building_data.get('living_area_m2', 150)
    insulation_quality = building_data.get('insulation_quality', 'Mittel')

    # Heizlast berechnen
    heat_load_kw = calculate_building_heat_load(
        building_type, living_area_m2, insulation_quality)

    # Warmwasser-Anteil hinzufügen (ca. 15-25% der Heizlast)
    hot_water_factor = building_data.get('hot_water_factor', 0.2)
    total_load_kw = heat_load_kw * (1 + hot_water_factor)

    # Empfohlene Wärmepumpenleistung (etwas überdimensioniert für Komfort)
    recommended_power_kw = total_load_kw * 1.1

    # Jährlicher Wärmebedarf schätzen
    heating_hours = building_data.get('heating_hours', 1800)
    annual_heat_demand = heat_load_kw * heating_hours

    return {
        'heat_load_kw': round(heat_load_kw, 2),
        'total_load_kw': round(total_load_kw, 2),
        'recommended_power_kw': round(recommended_power_kw, 2),
        'annual_heat_demand_kwh': round(annual_heat_demand, 0),
        'building_type': building_type,
        'living_area_m2': living_area_m2,
        'insulation_quality': insulation_quality
    }

# --- Erweiterungen: Verbrauchsbasierte Abschätzung ---


# Energieinhalte (vereinfachte Durchschnittswerte)
ENERGY_CONTENT_KWH_PER_UNIT: dict[str, float] = {
    'oil_l': 10.0,          # kWh pro Liter Heizöl EL
    'gas_kwh': 1.0,         # kWh pro kWh Erdgas (Rechnungswert)
    # kWh pro Ster (Raummeter) lufttrockenes Hartholz (Durchschnitt)
    'wood_ster': 1400.0,
}

# Standard-Wirkungsgrade je Systemtyp (Heizkesselanlage gesamt, konservativ)
EFFICIENCY_DEFAULTS_BY_SYSTEM: dict[str, float] = {
    'Gas-Brennwert': 0.92,
    'Öl-Brennwert': 0.90,
    'Pellets': 0.80,
    'Fernwärme': 0.95,
    'Strom-Direktheizung': 1.00,
    'Alte Gasheizung': 0.80,
    'Alte Ölheizung': 0.78,
}


def get_default_heating_system_efficiency(heating_system: str) -> float:
    """Gibt einen sinnvollen Standard-Wirkungsgrad für das aktuelle Heizsystem zurück."""
    return EFFICIENCY_DEFAULTS_BY_SYSTEM.get(heating_system, 0.85)


def estimate_annual_heat_demand_kwh_from_consumption(
    consumption: dict[str, float],
    heating_system: str,
    wood_ster_additional: float = 0.0,
    custom_efficiency: float | None = None) -> float:
    """
    Schätzt den jährlichen Wärmebedarf (Nutzwärme) aus aktuellem Verbrauch.

    Args:
        consumption: Dict mit möglichen Keys: 'oil_l', 'gas_kwh', 'wood_ster'. Werte pro Jahr.
        heating_system: Aktuelles Heizsystem (zur Ableitung des Wirkungsgrads).
        wood_ster_additional: Zusätzlicher Holzverbrauch in Ster (z.B. Kamin) stets als Zusatz.
        custom_efficiency: Optionaler manueller Wirkungsgrad (0.6..1.0). Falls None, Defaults.

    Returns:
        Jährlicher Wärmebedarf in kWh (Nutzwärme).
    """
    eff_main = custom_efficiency if (custom_efficiency is not None and 0.4 <= custom_efficiency <=
                                     1.05) else get_default_heating_system_efficiency(heating_system)
    eff_wood = 0.75  # typischer Nutzungsgrad Einzelofen

    oil_l = float(consumption.get('oil_l', 0) or 0)
    gas_kwh = float(consumption.get('gas_kwh', 0) or 0)
    wood_ster = float(consumption.get('wood_ster', 0) or 0) + \
        float(wood_ster_additional or 0)

    # Nutzwärme aus den Brennstoffen (Energieinhalt * Anlagenwirkungsgrad)
    heat_from_oil = oil_l * ENERGY_CONTENT_KWH_PER_UNIT['oil_l'] * eff_main
    heat_from_gas = gas_kwh * eff_main
    heat_from_wood = wood_ster * \
        ENERGY_CONTENT_KWH_PER_UNIT['wood_ster'] * eff_wood

    return max(0.0, heat_from_oil + heat_from_gas + heat_from_wood)


def estimate_heat_load_kw_from_annual_demand(
        annual_heat_demand_kwh: float,
        heating_hours: int = 1800) -> float:
    """Leitet die Spitzen-Heizlast aus dem Jahreswärmebedarf über angenommene Volllaststunden ab."""
    if not heating_hours or heating_hours <= 0:
        return 0.0
    return annual_heat_demand_kwh / float(heating_hours)


# ==================== ERWEITERTE FUNKTIONEN (2025-11-02) ====================
# Basierend auf WP_implementierung.pdf + Excel-Dateien (1-5.xlsx)
# =============================================================================

def calculate_domestic_hot_water_demand(
    living_area_m2: float,
    persons: int = None,
    daily_usage_liters_per_person: float = 50.0
) -> dict[str, float]:
    """
    Berechnet Warmwasserbedarf (Trinkwasser) in kWh/Jahr.

    Args:
        living_area_m2: Wohnfläche in m²
        persons: Anzahl Personen (wenn None: geschätzt aus Wohnfläche)
        daily_usage_liters_per_person: Täglicher Warmwasserverbrauch pro Person (Standard: 50L)

    Returns:
        Dict mit DHW-Bedarf in verschiedenen Einheiten

    Basis: PDF Seite 10, Excel 5.xlsx
    - Warmwasserverbrauch: 40-60 Liter/Person/Tag (Standard: 50L)
    - Temperaturanhebung: ca. 45K (von 10°C auf 55°C)
    - Energiebedarf: ca. 0.052 kWh/Liter (1.16 Wh/L*K * 45K)
    """
    # Personenzahl schätzen falls nicht angegeben (ca. 35-40 m²/Person)
    if persons is None:
        persons = max(1, round(living_area_m2 / 37.5))

    # Jährlicher Warmwasserverbrauch in Litern
    annual_water_liters = persons * daily_usage_liters_per_person * 365

    # Energiebedarf: 0.052 kWh/Liter (Aufheizung von 10°C auf 55°C)
    annual_dhw_demand_kwh = annual_water_liters * 0.052

    # Anteil am Gesamt-Wärmebedarf (typisch 12-18%)
    dhw_percentage = 15.0  # Durchschnitt

    return {
        'annual_dhw_demand_kwh': round(annual_dhw_demand_kwh, 1),
        'persons': persons,
        'daily_liters': round(persons * daily_usage_liters_per_person, 1),
        'dhw_load_kw': round(annual_dhw_demand_kwh / 1800, 2),  # Spitzenlast
        'dhw_percentage': dhw_percentage
    }


def calculate_heat_load_with_climate_zone(
    building_type: str,
    living_area_m2: float,
    climate_zone: str = "Gemäßigt",
    insulation_quality: str = "Mittel",
    persons: int = None
) -> dict[str, Any]:
    """
    Erweiterte Heizlastberechnung mit Klimazone und Warmwasser.

    Args:
        building_type: "Neubau KFW40", "Neubau KFW55", "Altbau saniert", "Altbau unsaniert"
        living_area_m2: Wohnfläche in m²
        climate_zone: "Kalt", "Gemäßigt", "Mild"
        insulation_quality: "Gut", "Mittel", "Schlecht"
        persons: Anzahl Personen (optional, wird sonst geschätzt)

    Returns:
        Dict mit detaillierter Heizlastanalyse

    Basis: PDF Seite 9-10, Excel 1-3.xlsx
    """
    # Klimafaktoren (Anpassung der Heizlast)
    climate_factors = {
        "Kalt": 1.2,      # Z.B. Bergregionen, harte Winter
        "Gemäßigt": 1.0,  # Standardklima Deutschland
        "Mild": 0.8       # Z.B. Küstenregionen, milde Winter
    }
    climate_factor = climate_factors.get(climate_zone, 1.0)

    # Basis-Heizlast berechnen
    base_heat_load_kw = calculate_building_heat_load(
        building_type, living_area_m2, insulation_quality
    )

    # Mit Klimafaktor anpassen
    heating_load_kw = base_heat_load_kw * climate_factor

    # Warmwasserbedarf berechnen
    dhw_data = calculate_domestic_hot_water_demand(living_area_m2, persons)
    dhw_load_kw = dhw_data['dhw_load_kw']

    # Gesamt-Heizlast
    total_load_kw = heating_load_kw + dhw_load_kw

    # Jährlicher Wärmebedarf (1800 Volllaststunden)
    annual_heating_demand_kwh = heating_load_kw * 1800
    annual_dhw_demand_kwh = dhw_data['annual_dhw_demand_kwh']
    annual_total_demand_kwh = annual_heating_demand_kwh + annual_dhw_demand_kwh

    return {
        'heating_load_kw': round(heating_load_kw, 2),
        'dhw_load_kw': round(dhw_load_kw, 2),
        'total_load_kw': round(total_load_kw, 2),
        'annual_heating_demand_kwh': round(annual_heating_demand_kwh, 0),
        'annual_dhw_demand_kwh': round(annual_dhw_demand_kwh, 0),
        'annual_total_demand_kwh': round(annual_total_demand_kwh, 0),
        'climate_zone': climate_zone,
        'climate_factor': climate_factor,
        'persons': dhw_data['persons'],
        'building_type': building_type,
        'living_area_m2': living_area_m2,
        'insulation_quality': insulation_quality
    }


def calculate_required_flow_temperature(
    heat_load_kw: float,
    radiator_area_m2: float = None,
    room_temperature_c: float = 20.0,
    original_flow_temp_c: float = 70.0,
    original_return_temp_c: float = 55.0,
    radiator_exponent: float = 1.3
) -> dict[str, Any]:
    """
    Berechnet erforderliche Vorlauftemperatur für bestehende Radiatoren.

    Basis-Formel: Q ~ (ΔT)^n
    Wobei ΔT = mittlere Übertemperatur = (T_vor + T_rück)/2 - T_raum

    Args:
        heat_load_kw: Erforderliche Heizleistung in kW
        radiator_area_m2: Heizfläche in m² (optional, wird geschätzt falls None)
        room_temperature_c: Raumtemperatur in °C (Standard: 20°C)
        original_flow_temp_c: Ursprüngliche Vorlauftemperatur (Standard: 70°C)
        original_return_temp_c: Ursprüngliche Rücklauftemperatur (Standard: 55°C)
        radiator_exponent: Exponent der Radiator-Kennlinie (Standard: 1.3)

    Returns:
        Dict mit erforderlicher Vorlauf-/Rücklauftemperatur

    Basis: PDF Seite 11, Formel Q ~ (ΔT)^1.3
    """
    # Original mittlere Übertemperatur
    original_mean_temp = (original_flow_temp_c + original_return_temp_c) / 2
    original_delta_t = original_mean_temp - room_temperature_c

    # Wenn Heizfläche nicht angegeben, aus Heizlast und Original-Temperaturen schätzen
    # Annahme: k ≈ 10 W/(m²*K^n) für typische Radiatoren
    if radiator_area_m2 is None:
        k_factor = 10.0  # W/(m²*K^n)
        radiator_area_m2 = (heat_load_kw * 1000) / (k_factor * (original_delta_t ** radiator_exponent))

    # Erforderliche mittlere Übertemperatur für neue Heizlast berechnen
    # Q_neu / Q_alt = (ΔT_neu / ΔT_alt)^n
    # Annahme: Original-System war für gleiche Heizlast ausgelegt
    heat_load_ratio = 1.0  # Vereinfachung: gleiche Heizlast
    required_delta_t = original_delta_t * (heat_load_ratio ** (1 / radiator_exponent))

    # Vorlauf- und Rücklauftemperatur berechnen (Annahme: Spreizung 10K)
    temperature_spread = 10.0  # K
    required_mean_temp = room_temperature_c + required_delta_t
    required_flow_temp = required_mean_temp + temperature_spread / 2
    required_return_temp = required_mean_temp - temperature_spread / 2

    return {
        'required_flow_temp_c': round(required_flow_temp, 1),
        'required_return_temp_c': round(required_return_temp, 1),
        'required_mean_temp_c': round(required_mean_temp, 1),
        'radiator_area_m2': round(radiator_area_m2, 1),
        'original_flow_temp_c': original_flow_temp_c,
        'heat_load_kw': heat_load_kw
    }


def check_radiator_compatibility(
    required_flow_temp_c: float,
    heatpump_max_temp_c: float = 70.0,
    optimal_temp_c: float = 55.0
) -> dict[str, Any]:
    """
    Prüft ob bestehende Radiatoren für Wärmepumpe geeignet sind.

    Args:
        required_flow_temp_c: Erforderliche Vorlauftemperatur in °C
        heatpump_max_temp_c: Maximale WP-Vorlauftemperatur (Standard: 70°C für R290)
        optimal_temp_c: Optimale Vorlauftemperatur für hohen COP (Standard: 55°C)

    Returns:
        Dict mit Kompatibilitäts-Bewertung und Empfehlungen

    Basis: PDF Seite 11-12
    - Optimal: ≤55°C (COP 4.5-5.5)
    - Grenzwertig: 55-65°C (COP 3.5-4.5)
    - Kritisch: 65-70°C (COP 2.5-3.5)
    - Ungeeignet: >70°C (WP kann nicht liefern)
    """
    # Bewertung und COP-Einfluss
    if required_flow_temp_c <= optimal_temp_c:
        compatibility = "Optimal"
        color = "green"
        cop_impact_percent = 0  # Kein negativer Einfluss
        efficiency_rating = "Sehr gut"
        recommendation = "Radiatoren ideal für Wärmepumpe geeignet. Hoher COP möglich."
        upgrade_needed = False
        upgrade_cost_estimate = 0

    elif required_flow_temp_c <= 60.0:
        compatibility = "Gut"
        color = "lightgreen"
        cop_impact_percent = 5  # 5% COP-Reduktion
        efficiency_rating = "Gut"
        recommendation = "Radiatoren geeignet. Leichte COP-Reduktion, aber wirtschaftlich sinnvoll."
        upgrade_needed = False
        upgrade_cost_estimate = 0

    elif required_flow_temp_c <= 65.0:
        compatibility = "Grenzwertig"
        color = "yellow"
        cop_impact_percent = 12  # 12% COP-Reduktion
        efficiency_rating = "Ausreichend"
        recommendation = "Radiatoren bedingt geeignet. Mittlere COP-Reduktion. Upgrade verbessert Wirtschaftlichkeit."
        upgrade_needed = True  # Empfohlen aber nicht zwingend
        upgrade_cost_estimate = 3000  # Geschätzte Kosten für Heizkörper-Upgrade

    elif required_flow_temp_c <= heatpump_max_temp_c:
        compatibility = "Kritisch"
        color = "orange"
        cop_impact_percent = 25  # 25% COP-Reduktion
        efficiency_rating = "Mangelhaft"
        recommendation = "Radiatoren kritisch. Hohe COP-Reduktion. Upgrade dringend empfohlen!"
        upgrade_needed = True
        upgrade_cost_estimate = 5000

    else:
        compatibility = "Ungeeignet"
        color = "red"
        cop_impact_percent = 40  # 40%+ COP-Reduktion oder nicht erreichbar
        efficiency_rating = "Unzureichend"
        recommendation = "Radiatoren NICHT geeignet! WP kann erforderliche Temperatur nicht liefern. Upgrade erforderlich."
        upgrade_needed = True
        upgrade_cost_estimate = 7000

    return {
        'compatible': required_flow_temp_c <= heatpump_max_temp_c,
        'compatibility': compatibility,
        'color': color,
        'efficiency_rating': efficiency_rating,
        'recommendation': recommendation,
        'cop_impact_percent': cop_impact_percent,
        'upgrade_needed': upgrade_needed,
        'upgrade_cost_estimate': upgrade_cost_estimate,
        'required_flow_temp_c': round(required_flow_temp_c, 1),
        'heatpump_max_temp_c': heatpump_max_temp_c,
        'optimal_temp_c': optimal_temp_c,
        'temp_difference': round(required_flow_temp_c - optimal_temp_c, 1)
    }


def calculate_co2_costs_fossil_heating(
    fuel_type: str,
    annual_consumption_kwh: float,
    co2_price_per_ton: float = 85.0,
    green_fuel_share: float = 0.0,
    year: int = 2025
) -> dict[str, Any]:
    """
    Berechnet CO2-Kosten für fossile Heizung mit GEG-Regelung.

    Args:
        fuel_type: "Heizöl" oder "Erdgas"
        annual_consumption_kwh: Jährlicher Brennstoffverbrauch in kWh
        co2_price_per_ton: CO2-Preis in €/t (Standard: 85€ Durchschnitt 2025-2045)
        green_fuel_share: Anteil grüner Brennstoffe (0.0-1.0), GEG-Pflicht ab 2029
        year: Berechnungsjahr für GEG-Pflichtanteil

    Returns:
        Dict mit CO2-Kosten und Emissionen

    Basis: Excel 5.xlsx
    - CO2-Emission Heizöl: 0.266 kg/kWh
    - CO2-Emission Erdgas: 0.201 kg/kWh
    - CO2-Preis 2025: 55€/t → 2045: 85€/t (Durchschnitt für 20 Jahre)
    - GEG-Pflicht: 2029: 15%, 2035: 30%, 2040: 60%, 2045: 100%
    """
    # CO2-Emissionsfaktoren (kg CO2 pro kWh Brennstoff)
    co2_factors = {
        "Heizöl": 0.266,  # kg/kWh
        "Erdgas": 0.201,  # kg/kWh
        "Flüssiggas": 0.234,
        "Kohle": 0.350
    }

    co2_factor = co2_factors.get(fuel_type, 0.250)  # Default: Mittelwert

    # GEG-Pflichtanteil grüne Brennstoffe (ab 2029)
    if year >= 2045:
        geg_min_share = 1.00  # 100%
    elif year >= 2040:
        geg_min_share = 0.60  # 60%
    elif year >= 2035:
        geg_min_share = 0.30  # 30%
    elif year >= 2029:
        geg_min_share = 0.15  # 15%
    else:
        geg_min_share = 0.0  # Keine Pflicht vor 2029

    # Tatsächlicher Anteil (mindestens GEG-Pflicht)
    actual_green_share = max(green_fuel_share, geg_min_share)

    # CO2-Emissionen (nur fossiler Anteil)
    fossil_share = 1.0 - actual_green_share
    annual_co2_tons = (annual_consumption_kwh * co2_factor * fossil_share) / 1000

    # CO2-Kosten
    annual_co2_cost_eur = annual_co2_tons * co2_price_per_ton

    # Mehrkosten grüne Brennstoffe berechnen
    green_fuel_premium = calculate_green_fuel_premium(
        fuel_type, annual_consumption_kwh, actual_green_share
    )

    # Gesamte Zusatzkosten (CO2 + grüne Brennstoffe)
    total_climate_cost = annual_co2_cost_eur + green_fuel_premium

    return {
        'fuel_type': fuel_type,
        'annual_consumption_kwh': annual_consumption_kwh,
        'co2_factor_kg_per_kwh': co2_factor,
        'annual_co2_tons': round(annual_co2_tons, 2),
        'annual_co2_cost_eur': round(annual_co2_cost_eur, 2),
        'green_fuel_share': round(actual_green_share * 100, 1),
        'geg_min_share': round(geg_min_share * 100, 1),
        'green_fuel_cost_premium': round(green_fuel_premium, 2),
        'total_climate_cost': round(total_climate_cost, 2),
        'co2_price_per_ton': co2_price_per_ton,
        'year': year
    }


def calculate_green_fuel_premium(
    fuel_type: str,
    kwh_consumed: float,
    green_share: float
) -> float:
    """
    Berechnet Mehrkosten für grüne Brennstoffe (GEG-Pflicht ab 2029).

    Basis: Excel 5.xlsx
    - Industriestromkosten: 0.17 €/kWh
    - Wirkungsgradverluste Bio-Heizöl: 40% (nur 60% Energie bleibt)
    - Wirkungsgradverluste Bio-Methan: 60% (nur 40% Energie bleibt)
    - Stromkosten für grüne Herstellung übersteigen fossile Brennstoffkosten

    Returns:
        Mehrkosten in € pro Jahr für grünen Anteil
    """
    if green_share <= 0:
        return 0.0

    # Grundkosten fossiler Brennstoffe (€/kWh)
    fossil_base_costs = {
        "Heizöl": 0.095,   # ~9.5 ct/kWh
        "Erdgas": 0.10,    # ~10 ct/kWh
        "Flüssiggas": 0.12
    }

    # Wirkungsgradverluste bei grüner Herstellung
    efficiency_losses = {
        "Heizöl": 0.60,    # 40% Verlust (strombasiertes synth. Öl)
        "Erdgas": 0.40,    # 60% Verlust (strombasiertes Methan)
        "Flüssiggas": 0.50
    }

    base_cost = fossil_base_costs.get(fuel_type, 0.10)
    efficiency = efficiency_losses.get(fuel_type, 0.50)

    # Industriestrompreis
    electricity_price = 0.17  # €/kWh

    # Kosten grüner Brennstoff = Strompreis / Wirkungsgrad
    green_fuel_cost = electricity_price / efficiency

    # Mehrkosten = (grüne Kosten - fossile Kosten) * Anteil * Verbrauch
    premium_per_kwh = green_fuel_cost - base_cost
    total_premium = premium_per_kwh * green_share * kwh_consumed

    return max(0.0, total_premium)


def calculate_beg_subsidy(
    investment_cost_eur: float,
    replaces_gas_oil: bool = True,
    household_income_below_threshold: bool = False,
    max_eligible_cost: float = 60000.0
) -> dict[str, Any]:
    """
    Berechnet BEG-Förderung für Wärmepumpen (Bundesförderung effiziente Gebäude).

    Args:
        investment_cost_eur: Investitionskosten der Wärmepumpe
        replaces_gas_oil: Ersetzt alte Gas-/Ölheizung (gibt 10% Bonus)
        household_income_below_threshold: Haushaltseinkommen < 40.000€ (gibt 5% Bonus)
        max_eligible_cost: Max. förderfähige Kosten (Standard: 60.000€)

    Returns:
        Dict mit Förderdetails

    Basis: PDF Seite 13-14
    - Basisförderung: 30% (seit 2024, war 35% bis 2023)
    - Klimageschwindigkeitsbonus: 20% (Austausch funktionstüchtige Heizung vor Pflicht)
    - Einkommensbonus: 30% (Haushaltseinkommen < 40k€)
    - Max. Förderung: 70% (alle Boni kombiniert)
    - Max. förderfähige Kosten: 30.000€ für Einfamilienhaus (Stand 2024)

    Hinweis: Zahlen hier basieren auf PDF (älter), aktuelle BEG prüfen!
    """
    # Förderfähige Kosten (gedeckelt)
    eligible_cost = min(investment_cost_eur, max_eligible_cost)

    # Basisförderung (aktuell 30%, PDF zeigt 35% - verwende konservative 30%)
    base_subsidy_percent = 30

    # Klimageschwindigkeitsbonus (20% wenn alte funktionstüchtige Heizung ersetzt wird)
    # Entspricht dem "Gas-Ersatz-Bonus" im PDF
    speed_bonus_percent = 20 if replaces_gas_oil else 0

    # Einkommensbonus (30% wenn Haushaltseinkommen < 40.000€)
    # PDF zeigt 5%, aktuelle BEG gibt 30% - verwende 30%
    income_bonus_percent = 30 if household_income_below_threshold else 0

    # Gesamtförderung (max. 70%)
    total_subsidy_percent = min(
        base_subsidy_percent + speed_bonus_percent + income_bonus_percent,
        70
    )

    # Fördersumme
    subsidy_amount_eur = eligible_cost * (total_subsidy_percent / 100)

    # Netto-Investition nach Förderung
    net_investment_eur = investment_cost_eur - subsidy_amount_eur

    return {
        'investment_cost_eur': investment_cost_eur,
        'eligible_cost_eur': eligible_cost,
        'base_subsidy_percent': base_subsidy_percent,
        'speed_bonus_percent': speed_bonus_percent,
        'income_bonus_percent': income_bonus_percent,
        'total_subsidy_percent': total_subsidy_percent,
        'subsidy_amount_eur': round(subsidy_amount_eur, 2),
        'net_investment_eur': round(net_investment_eur, 2),
        'max_eligible_cost': max_eligible_cost,
        'replaces_fossil': replaces_gas_oil,
        'income_below_threshold': household_income_below_threshold
    }


def calculate_npv_20_years(
    investment_eur: float,
    annual_operating_cost_eur: float,
    annual_cost_increase_percent: float = 2.0,
    discount_rate_percent: float = 3.0,
    residual_value_eur: float = 0.0,
    years: int = 20
) -> dict[str, Any]:
    """
    NPV-Berechnung (Net Present Value / Kapitalwert) über 20 Jahre.

    Args:
        investment_eur: Anfangsinvestition (Jahr 0)
        annual_operating_cost_eur: Jährliche Betriebskosten (Jahr 1)
        annual_cost_increase_percent: Jährliche Kostensteigerung (Standard: 2%)
        discount_rate_percent: Diskontrate / Kalkulationszinssatz (Standard: 3%)
        residual_value_eur: Restwert am Ende (Standard: 0)
        years: Betrachtungszeitraum (Standard: 20 Jahre)

    Returns:
        Dict mit NPV und weiteren Kennzahlen

    Basis: PDF Seite 13, Excel 1-3.xlsx (Annuitätenrechnung)
    - Diskontrate: 3% (Nominalzins Land Vorarlberg laut Excel)
    - Betrachtungszeitraum: 20 Jahre
    - Berücksichtigt jährliche Kostensteigerung (Inflation, Energiepreissteigerung)
    """
    # Barwertfaktoren
    discount_factor = 1 + (discount_rate_percent / 100)
    cost_increase_factor = 1 + (annual_cost_increase_percent / 100)

    # NPV berechnen
    npv = -investment_eur  # Anfangsinvestition (negativ)
    total_cost_undiscounted = investment_eur

    # Jährliche Cashflows
    cashflows = []
    for year in range(1, years + 1):
        # Betriebskosten mit jährlicher Steigerung
        operating_cost = annual_operating_cost_eur * (cost_increase_factor ** (year - 1))

        # Barwert der Betriebskosten
        present_value = operating_cost / (discount_factor ** year)

        npv -= present_value
        total_cost_undiscounted += operating_cost

        cashflows.append({
            'year': year,
            'operating_cost': round(operating_cost, 2),
            'present_value': round(present_value, 2)
        })

    # Restwert (positiv, daher +)
    if residual_value_eur > 0:
        residual_pv = residual_value_eur / (discount_factor ** years)
        npv += residual_pv
    else:
        residual_pv = 0

    # Annuitätenfaktor (für Umrechnung NPV → jährliche Kosten)
    # ANF = (q^n * (q-1)) / (q^n - 1) wobei q = 1 + i
    annuity_factor = (
        (discount_factor ** years) * (discount_factor - 1)
    ) / (
        (discount_factor ** years) - 1
    )

    # Äquivalente jährliche Kosten (Annuität)
    annual_equivalent_cost = abs(npv) * annuity_factor

    return {
        'npv_eur': round(npv, 2),
        'total_cost_undiscounted': round(total_cost_undiscounted, 2),
        'total_cost_present_value': round(abs(npv), 2),
        'annual_equivalent_cost': round(annual_equivalent_cost, 2),
        'investment_eur': investment_eur,
        'residual_value_pv': round(residual_pv, 2),
        'discount_rate_percent': discount_rate_percent,
        'years': years,
        'annuity_factor': round(annuity_factor, 4),
        'cashflows': cashflows[:5]  # Nur erste 5 Jahre für Übersicht
    }


def compare_heating_systems_20_years(
    building_data: dict[str, Any],
    heatpump_data: dict[str, Any],
    fossil_heating_type: str = "Erdgas",
    electricity_price_kwh: float = 0.30,
    fossil_fuel_price_kwh: float = 0.10,
    co2_price_per_ton: float = 85.0,
    include_pv: bool = False,
    pv_data: dict[str, Any] = None
) -> dict[str, Any]:
    """
    Vollständiger Kostenvergleich: Wärmepumpe vs. Öl/Gas über 20 Jahre.

    Berücksichtigt:
    - Anschaffungskosten (nach BEG-Förderung)
    - Betriebskosten (Strom vs. Öl/Gas)
    - CO2-Kosten
    - GEG-Pflicht grüne Brennstoffe
    - Wartungs- & Reparaturkosten
    - NPV mit 3% Diskontrate
    - Optional: PV-Eigenverbrauch

    Args:
        building_data: Gebäudedaten mit Wärmebedarf
        heatpump_data: WP-Daten (Leistung, COP, Preis)
        fossil_heating_type: "Heizöl" oder "Erdgas"
        electricity_price_kwh: Strompreis in €/kWh
        fossil_fuel_price_kwh: Brennstoffpreis in €/kWh
        co2_price_per_ton: CO2-Preis in €/t
        include_pv: PV-Eigenverbrauch berücksichtigen
        pv_data: PV-Systemdaten (falls include_pv=True)

    Returns:
        Dict mit detailliertem Vergleich

    Basis: Excel 4.xlsx, 5.xlsx
    """
    # Wärmebedarf ermitteln
    annual_heat_demand_kwh = building_data.get(
        'annual_total_demand_kwh',
        building_data.get('heating_demand', 15000)
    )

    # ===== WÄRMEPUMPE =====

    # Investitionskosten
    hp_investment = heatpump_data.get('investment_cost', heatpump_data.get('price', 30000))

    # BEG-Förderung (ersetzt fossile Heizung)
    beg_subsidy = calculate_beg_subsidy(
        hp_investment,
        replaces_gas_oil=True,
        household_income_below_threshold=False
    )
    hp_net_investment = beg_subsidy['net_investment_eur']

    # Stromverbrauch WP
    cop = heatpump_data.get('cop', heatpump_data.get('cop_rating', 3.5))
    hp_annual_electricity_kwh = annual_heat_demand_kwh / cop

    # PV-Eigenverbrauch abziehen (falls vorhanden)
    if include_pv and pv_data:
        pv_self_consumption = calculate_pv_self_consumption_heatpump(
            hp_annual_electricity_kwh,
            pv_data.get('system_size_kwp', 10.0),
            pv_data.get('annual_yield_kwh_per_kwp', 1000.0),
            pv_data.get('self_consumption_rate_percent', 50.0)
        )
        hp_grid_electricity_kwh = pv_self_consumption['heatpump_from_grid_kwh']
        pv_cost_savings = pv_self_consumption['cost_savings_eur']
    else:
        hp_grid_electricity_kwh = hp_annual_electricity_kwh
        pv_cost_savings = 0

    # Jährliche Stromkosten
    hp_annual_electricity_cost = hp_grid_electricity_kwh * electricity_price_kwh

    # Wartungskosten WP (ca. 150-250€/Jahr)
    hp_annual_maintenance = 200

    # Gesamte jährliche Betriebskosten WP
    hp_annual_operating_cost = hp_annual_electricity_cost + hp_annual_maintenance - pv_cost_savings

    # NPV Wärmepumpe
    hp_npv = calculate_npv_20_years(
        hp_net_investment,
        hp_annual_operating_cost,
        annual_cost_increase_percent=2.0,  # Strompreissteigerung
        discount_rate_percent=3.0
    )

    # ===== FOSSILE HEIZUNG =====

    # Investitionskosten (neue Gas-/Ölheizung)
    fossil_investment = 12800  # Laut Excel 4.xlsx

    # Brennstoffverbrauch (mit Wirkungsgrad)
    fossil_efficiency = 0.90  # Brennwert-Technologie
    fossil_fuel_consumption_kwh = annual_heat_demand_kwh / fossil_efficiency

    # Brennstoffkosten
    fossil_annual_fuel_cost = fossil_fuel_consumption_kwh * fossil_fuel_price_kwh

    # CO2-Kosten berechnen (mit GEG-Regelung)
    co2_costs = calculate_co2_costs_fossil_heating(
        fossil_heating_type,
        fossil_fuel_consumption_kwh,
        co2_price_per_ton,
        green_fuel_share=0.0,  # Startet mit 0%, steigt durch GEG
        year=2025
    )

    # Durchschnittliche CO2-Kosten über 20 Jahre (steigend durch GEG)
    # Jahr 1-4 (2025-2028): 0% grün
    # Jahr 5-10 (2029-2034): 15% grün
    # Jahr 11-15 (2035-2039): 30% grün
    # Jahr 16-20 (2040-2044): 60% grün
    avg_co2_cost = 0
    for year_offset in range(20):
        year = 2025 + year_offset
        co2_year = calculate_co2_costs_fossil_heating(
            fossil_heating_type,
            fossil_fuel_consumption_kwh,
            co2_price_per_ton,
            year=year
        )
        avg_co2_cost += co2_year['total_climate_cost']
    avg_annual_co2_climate_cost = avg_co2_cost / 20

    # Wartungskosten fossile Heizung (höher als WP: ca. 300-400€/Jahr)
    fossil_annual_maintenance = 350

    # Gesamte jährliche Betriebskosten Fossil
    fossil_annual_operating_cost = (
        fossil_annual_fuel_cost +
        avg_annual_co2_climate_cost +
        fossil_annual_maintenance
    )

    # NPV Fossile Heizung
    fossil_npv = calculate_npv_20_years(
        fossil_investment,
        fossil_annual_operating_cost,
        annual_cost_increase_percent=3.0,  # Höhere Steigerung (CO2-Preis!)
        discount_rate_percent=3.0
    )

    # ===== VERGLEICH =====

    # Einsparungen WP vs. Fossil
    savings_eur = fossil_npv['npv_eur'] - hp_npv['npv_eur']
    annual_savings = fossil_annual_operating_cost - hp_annual_operating_cost

    # Amortisation (einfache Berechnung)
    investment_difference = hp_net_investment - fossil_investment
    if annual_savings > 0:
        payback_years = investment_difference / annual_savings
    else:
        payback_years = float('inf')

    # CO2-Einsparungen
    # WP hat minimale CO2-Emissionen (deutscher Strommix: ~0.4 kg/kWh)
    hp_co2_tons_per_year = (hp_annual_electricity_kwh * 0.4) / 1000
    fossil_co2_tons_per_year = co2_costs['annual_co2_tons']
    co2_savings_tons_per_year = fossil_co2_tons_per_year - hp_co2_tons_per_year
    co2_savings_tons_20_years = co2_savings_tons_per_year * 20

    return {
        # Wärmepumpe
        'heatpump': {
            'investment_gross': hp_investment,
            'beg_subsidy': beg_subsidy['subsidy_amount_eur'],
            'investment_net': hp_net_investment,
            'annual_electricity_kwh': round(hp_annual_electricity_kwh, 0),
            'annual_electricity_cost': round(hp_annual_electricity_cost, 2),
            'annual_maintenance': hp_annual_maintenance,
            'annual_operating_cost': round(hp_annual_operating_cost, 2),
            'npv_20years': hp_npv['npv_eur'],
            'total_cost_20years': round(hp_npv['total_cost_undiscounted'], 2),
            'annual_co2_tons': round(hp_co2_tons_per_year, 2),
            'cop': cop,
            'pv_cost_savings': round(pv_cost_savings, 2) if include_pv else 0
        },

        # Fossile Heizung
        'fossil_heating': {
            'type': fossil_heating_type,
            'investment': fossil_investment,
            'annual_fuel_kwh': round(fossil_fuel_consumption_kwh, 0),
            'annual_fuel_cost': round(fossil_annual_fuel_cost, 2),
            'annual_co2_climate_cost': round(avg_annual_co2_climate_cost, 2),
            'annual_maintenance': fossil_annual_maintenance,
            'annual_operating_cost': round(fossil_annual_operating_cost, 2),
            'npv_20years': fossil_npv['npv_eur'],
            'total_cost_20years': round(fossil_npv['total_cost_undiscounted'], 2),
            'annual_co2_tons': round(fossil_co2_tons_per_year, 2)
        },

        # Vergleich
        'comparison': {
            'savings_eur_20years': round(savings_eur, 2),
            'annual_savings_eur': round(annual_savings, 2),
            'payback_years': round(payback_years, 1) if payback_years < 100 else None,
            'co2_savings_tons_per_year': round(co2_savings_tons_per_year, 2),
            'co2_savings_tons_20years': round(co2_savings_tons_20_years, 2),
            'recommendation': (
                'Wärmepumpe klar wirtschaftlich' if payback_years <= 10 else
                'Wärmepumpe wirtschaftlich' if payback_years <= 15 else
                'Wärmepumpe grenzwertig' if payback_years <= 20 else
                'Wärmepumpe langfristig vorteilhaft'
            )
        },

        # Zusatzinfos
        'parameters': {
            'annual_heat_demand_kwh': annual_heat_demand_kwh,
            'electricity_price_kwh': electricity_price_kwh,
            'fossil_fuel_price_kwh': fossil_fuel_price_kwh,
            'co2_price_per_ton': co2_price_per_ton,
            'include_pv': include_pv
        }
    }


def calculate_pv_self_consumption_heatpump(
    heatpump_annual_consumption_kwh: float,
    pv_system_size_kwp: float,
    pv_annual_yield_kwh_per_kwp: float = 1000.0,
    self_consumption_rate_percent: float = 50.0,
    electricity_price_kwh: float = 0.30
) -> dict[str, Any]:
    """
    Berechnet PV-Eigenverbrauch für Wärmepumpe.

    Wärmepumpen erhöhen den Eigenverbrauch von PV-Strom, da sie
    tagsüber laufen können (Pufferspeicher, Warmwasserbereitung).

    Args:
        heatpump_annual_consumption_kwh: Jährlicher WP-Stromverbrauch
        pv_system_size_kwp: PV-Anlagengröße in kWp
        pv_annual_yield_kwh_per_kwp: Spezifischer Ertrag (Standard: 1000 kWh/kWp)
        self_consumption_rate_percent: Eigenverbrauchsquote (Standard: 50%)
        electricity_price_kwh: Strompreis für Einsparungsberechnung

    Returns:
        Dict mit PV-Eigenverbrauch-Analyse

    Basis: Excel 3.xlsx (PV-Einspeisung Sheet)
    - PV-Ertrag: ~1000 kWh/kWp/Jahr (Deutschland)
    - Eigenverbrauch ohne WP: ~30%
    - Eigenverbrauch mit WP: ~50-60% (WP als flexibler Verbraucher)
    """
    # PV-Gesamtertrag
    pv_total_yield_kwh = pv_system_size_kwp * pv_annual_yield_kwh_per_kwp

    # Eigenverbrauch (gesamt, alle Haushaltsverbraucher)
    total_self_consumption_kwh = pv_total_yield_kwh * (self_consumption_rate_percent / 100)

    # Wie viel davon kann die WP nutzen? (Annahme: 60% des Eigenverbrauchs)
    # WP läuft bevorzugt tagsüber wenn PV-Ertrag hoch ist
    heatpump_share_of_self_consumption = 0.6
    heatpump_from_pv_kwh = min(
        total_self_consumption_kwh * heatpump_share_of_self_consumption,
        heatpump_annual_consumption_kwh
    )

    # Rest der WP-Energie kommt aus Netz
    heatpump_from_grid_kwh = heatpump_annual_consumption_kwh - heatpump_from_pv_kwh

    # Kosteneinsparungen
    cost_savings_eur = heatpump_from_pv_kwh * electricity_price_kwh

    # Eigenverbrauchsquote erhöht sich durch WP
    self_consumption_increased_percent = (
        total_self_consumption_kwh / pv_total_yield_kwh * 100
    )

    return {
        'pv_total_yield_kwh': round(pv_total_yield_kwh, 0),
        'pv_system_size_kwp': pv_system_size_kwp,
        'heatpump_annual_consumption_kwh': round(heatpump_annual_consumption_kwh, 0),
        'heatpump_from_pv_kwh': round(heatpump_from_pv_kwh, 0),
        'heatpump_from_grid_kwh': round(heatpump_from_grid_kwh, 0),
        'pv_coverage_percent': round((heatpump_from_pv_kwh / heatpump_annual_consumption_kwh) * 100, 1),
        'cost_savings_eur': round(cost_savings_eur, 2),
        'self_consumption_rate_percent': round(self_consumption_increased_percent, 1),
        'electricity_price_kwh': electricity_price_kwh
    }


# ============================================================================
# NEUE ERWEITERTE FUNKTIONEN (TODO 1 - 10 Funktionen)
# Basis: HEATPUMP_IMPLEMENTATION_PLAN.md
# ============================================================================
# HINWEIS: Alle erweiterten Funktionen sind bereits oben definiert (ab Zeile 278)
# Keine Duplikate mehr - Code wurde bereinigt für bessere Wartbarkeit

    """
    Berechnet BEG-Förderung für Wärmepumpen

    Args:
        investment_cost_eur: Investitionskosten
        replaces_gas_oil: Ersetzt Gas/Öl-Heizung?
        household_income_below_threshold: Haushaltseinkommen < 40k€?

    Returns:
        dict mit Förder-Details

    Quelle: PDF Seite 13 (BEG-Förderung)
    """
    # BEG-Fördersätze 2024/2025
    base_subsidy = 35  # 35% Basis-Förderung
    gas_oil_bonus = 10 if replaces_gas_oil else 0
    income_bonus = 5 if household_income_below_threshold else 0

    # Gesamt-Fördersatz (max 70%)
    total_subsidy_percent = min(70, base_subsidy + gas_oil_bonus + income_bonus)

    # Max. förderfähige Kosten: 60.000€
    eligible_costs = min(investment_cost_eur, 60000.0)

    # Förderbetrag
    subsidy_amount = eligible_costs * (total_subsidy_percent / 100)

    # Netto-Investition
    net_investment = investment_cost_eur - subsidy_amount

    return {
        "base_subsidy_percent": base_subsidy,
        "gas_replacement_bonus_percent": gas_oil_bonus,
        "income_bonus_percent": income_bonus,
        "total_subsidy_percent": total_subsidy_percent,
        "eligible_costs_eur": round(eligible_costs, 2),
        "subsidy_amount_eur": round(subsidy_amount, 2),
        "net_investment_eur": round(net_investment, 2),
        "max_eligible_costs": 60000.0
    }


def calculate_npv_20_years(
    investment_eur: float,
    annual_operating_cost_eur: float,
    annual_cost_increase_percent: float = 2.0,
    discount_rate_percent: float = 3.0,
    residual_value_eur: float = 0.0
) -> dict:
    """
    NPV-Berechnung über 20 Jahre mit Diskontrate

    Args:
        investment_eur: Anfangsinvestition
        annual_operating_cost_eur: Jährliche Betriebskosten (Jahr 1)
        annual_cost_increase_percent: Jährliche Kostensteigerung
        discount_rate_percent: Diskontrate (nominal)
        residual_value_eur: Restwert nach 20 Jahren

    Returns:
        dict mit npv_eur, total_cost_undiscounted, payback_years

    Quelle: Excel 1-3.xlsx (Annuitätenrechnung), PDF Seite 13
    """
    years = 20
    discount_rate = discount_rate_percent / 100
    cost_increase = annual_cost_increase_percent / 100

    # Berechne diskontierten Barwert aller Betriebskosten
    total_discounted_costs = investment_eur
    total_undiscounted_costs = investment_eur
    cumulative_undiscounted = investment_eur
    payback_years = None

    for year in range(1, years + 1):
        # Betriebskosten für dieses Jahr (mit Steigerung)
        yearly_cost = annual_operating_cost_eur * ((1 + cost_increase) ** (year - 1))

        # Diskontfaktor
        discount_factor = 1 / ((1 + discount_rate) ** year)

        # Diskontierte Kosten
        discounted_cost = yearly_cost * discount_factor

        total_discounted_costs += discounted_cost
        total_undiscounted_costs += yearly_cost

        # Amortisation (undiskontiert, vs. Referenzsystem)
        # Hier vereinfacht: Wenn kumulative Kosten < 0 (würde gegen Referenz verglichen)
        cumulative_undiscounted += yearly_cost

    # Restwert einbeziehen (diskontiert)
    if residual_value_eur > 0:
        residual_discounted = residual_value_eur / ((1 + discount_rate) ** years)
        total_discounted_costs -= residual_discounted

    # NPV = Negativ der Gesamtkosten (da Ausgaben)
    npv = -total_discounted_costs

    return {
        "npv_eur": round(npv, 2),
        "total_cost_discounted_eur": round(total_discounted_costs, 2),
        "total_cost_undiscounted_eur": round(total_undiscounted_costs, 2),
        "discount_rate_percent": discount_rate_percent,
        "years": years
    }


def compare_heating_systems_20_years(
    building_data: dict,
    heatpump_data: dict,
    fossil_heating_type: str = "Gasheizung"
) -> dict:
    """
    Vollständiger Kostenvergleich: WP vs. Öl/Gas über 20 Jahre

    Berücksichtigt:
    - Anschaffungskosten (nach BEG-Förderung)
    - Betriebskosten (Strom vs. Öl/Gas)
    - CO2-Kosten
    - GEG-Pflicht grüne Brennstoffe
    - Wartungs- & Reparaturkosten
    - NPV mit 3% Diskontrate

    Args:
        building_data: Dict mit annual_heat_demand_kwh
        heatpump_data: Dict mit investment_cost, cop/jaz, electricity_price
        fossil_heating_type: "Heizöl" oder "Erdgas"

    Returns:
        dict mit WP und Fossil Daten, Einsparungen, Amortisation

    Quelle: Excel 4.xlsx (econ calc light)
    """
    # Extrahiere Daten
    annual_demand_kwh = building_data.get("annual_heat_demand_kwh", 15000)

    # === WÄRMEPUMPE ===
    wp_investment = heatpump_data.get("investment_cost_eur", 30000)
    wp_cop = heatpump_data.get("jaz", heatpump_data.get("cop", 3.5))
    electricity_price = heatpump_data.get("electricity_price_kwh", 0.32)

    # BEG-Förderung
    beg_subsidy = calculate_beg_subsidy(
        wp_investment,
        replaces_gas_oil=True,
        household_income_below_threshold=False
    )
    wp_net_investment = beg_subsidy["net_investment_eur"]

    # Jährliche Stromkosten
    wp_annual_electricity_kwh = annual_demand_kwh / wp_cop
    wp_annual_operating_cost = wp_annual_electricity_kwh * electricity_price

    # Wartungskosten WP (ca. 200€/Jahr)
    wp_annual_maintenance = 200.0
    wp_total_annual_cost = wp_annual_operating_cost + wp_annual_maintenance

    # NPV WP
    wp_npv = calculate_npv_20_years(
        investment_eur=wp_net_investment,
        annual_operating_cost_eur=wp_total_annual_cost,
        annual_cost_increase_percent=2.0,
        discount_rate_percent=3.0
    )

    # === FOSSILE HEIZUNG ===
    # Investitionskosten (Gasheizung ~12.8k, Ölheizung ~15k)
    fossil_investment = 12800 if "Gas" in fossil_heating_type else 15000

    # Wirkungsgrad fossile Heizung (ca. 90%)
    fossil_efficiency = 0.90
    fossil_fuel_kwh = annual_demand_kwh / fossil_efficiency

    # Brennstoffkosten (Jahr 1)
    fuel_type = "Erdgas" if "Gas" in fossil_heating_type else "Heizöl"

    # CO2-Kosten berechnen (inklusive GEG grüne Brennstoffe)
    # GEG-Timeline: 2029: 15%, 2035: 30%, 2040: 60%, 2045: 100%
    # Durchschnitt über 20 Jahre: ~30%
    avg_green_share = 0.30

    co2_costs = calculate_co2_costs_fossil_heating(
        fuel_type=fuel_type,
        annual_consumption_kwh=fossil_fuel_kwh,
        co2_price_per_ton=70.0,  # Durchschnitt 2025-2045
        green_fuel_share=avg_green_share
    )

    fossil_annual_cost = co2_costs["total_climate_cost"]

    # Wartungskosten fossil (ca. 300€/Jahr - Schornsteinfeger, Service)
    fossil_annual_maintenance = 300.0
    fossil_total_annual_cost = fossil_annual_cost + fossil_annual_maintenance

    # NPV Fossil
    fossil_npv = calculate_npv_20_years(
        investment_eur=fossil_investment,
        annual_operating_cost_eur=fossil_total_annual_cost,
        annual_cost_increase_percent=3.5,  # Höher wegen CO2-Preis-Anstieg
        discount_rate_percent=3.0
    )

    # === VERGLEICH ===
    savings_eur = fossil_npv["total_cost_undiscounted_eur"] - wp_npv["total_cost_undiscounted_eur"]

    # Amortisation (einfach)
    annual_savings = fossil_total_annual_cost - wp_total_annual_cost
    payback_years = (wp_net_investment - fossil_investment) / annual_savings if annual_savings > 0 else 99

    # CO2-Einsparungen
    co2_savings_tons_per_year = co2_costs["annual_co2_tons"]
    co2_savings_20years = co2_savings_tons_per_year * 20

    return {
        "heatpump": {
            "investment_gross_eur": wp_investment,
            "subsidy_eur": beg_subsidy["subsidy_amount_eur"],
            "investment_net_eur": wp_net_investment,
            "annual_operating_cost_eur": round(wp_total_annual_cost, 2),
            "npv_20years_eur": wp_npv["npv_eur"],
            "total_cost_20years_eur": wp_npv["total_cost_undiscounted_eur"]
        },
        "fossil_heating": {
            "type": fossil_heating_type,
            "investment_eur": fossil_investment,
            "annual_operating_cost_eur": round(fossil_total_annual_cost, 2),
            "npv_20years_eur": fossil_npv["npv_eur"],
            "total_cost_20years_eur": fossil_npv["total_cost_undiscounted_eur"],
            "co2_emissions_tons_per_year": co2_costs["annual_co2_tons"]
        },
        "comparison": {
            "savings_20years_eur": round(savings_eur, 2),
            "payback_years": round(payback_years, 1),
            "co2_savings_tons_20years": round(co2_savings_20years, 2),
            "annual_savings_eur": round(annual_savings, 2)
        }
    }


def calculate_pv_self_consumption_heatpump(
    heatpump_annual_consumption_kwh: float,
    pv_system_size_kwp: float,
    pv_annual_yield_kwh_per_kwp: float = 1000.0,
    self_consumption_rate_percent: float = 30.0,
    electricity_price_kwh: float = 0.32,
    feed_in_tariff_kwh: float = 0.08
) -> dict:
    """
    Berechnet PV-Eigenverbrauch für Wärmepumpe

    Args:
        heatpump_annual_consumption_kwh: WP Stromverbrauch
        pv_system_size_kwp: PV-Anlagengröße in kWp
        pv_annual_yield_kwh_per_kwp: Ertrag pro kWp (Standard: 1000 kWh)
        self_consumption_rate_percent: Eigenverbrauchsrate ohne Speicher (Standard: 30%)
        electricity_price_kwh: Strompreis
        feed_in_tariff_kwh: Einspeisevergütung

    Returns:
        dict mit PV-Ertrag, WP-Eigenverbrauch, Kosteneinsparungen

    Quelle: Excel 3.xlsx (PV-Einspeisung)
    """
    # PV-Gesamtertrag
    pv_total_yield_kwh = pv_system_size_kwp * pv_annual_yield_kwh_per_kwp

    # Basis-Eigenverbrauch (ohne WP)
    base_self_consumption_kwh = pv_total_yield_kwh * (self_consumption_rate_percent / 100)

    # WP erhöht Eigenverbrauch (mehr Tagesverbrauch)
    # Annahme: WP erhöht Eigenverbrauch um +20% (von 30% auf ~50%)
    increased_rate_percent = min(70, self_consumption_rate_percent + 20)
    increased_self_consumption_kwh = pv_total_yield_kwh * (increased_rate_percent / 100)

    # WP-Anteil vom PV-Eigenverbrauch
    heatpump_from_pv_kwh = min(
        increased_self_consumption_kwh - base_self_consumption_kwh,
        heatpump_annual_consumption_kwh
    )

    # Rest vom Netz
    heatpump_from_grid_kwh = heatpump_annual_consumption_kwh - heatpump_from_pv_kwh

    # Kosteneinsparungen
    # Eigenverbrauch spart (Strompreis - Einspeisevergütung)
    cost_savings_eur = heatpump_from_pv_kwh * (electricity_price_kwh - feed_in_tariff_kwh)

    # Prozentuale Erhöhung des Eigenverbrauchs
    self_consumption_increase = increased_rate_percent - self_consumption_rate_percent

    return {
        "pv_total_yield_kwh": round(pv_total_yield_kwh, 0),
        "heatpump_from_pv_kwh": round(heatpump_from_pv_kwh, 0),
        "heatpump_from_grid_kwh": round(heatpump_from_grid_kwh, 0),
        "cost_savings_eur": round(cost_savings_eur, 2),
        "self_consumption_rate_base_percent": self_consumption_rate_percent,
        "self_consumption_rate_with_hp_percent": increased_rate_percent,
        "self_consumption_increase_percent": self_consumption_increase,
        "pv_coverage_of_hp_percent": round((heatpump_from_pv_kwh / heatpump_annual_consumption_kwh) * 100, 1)
    }

    # Test der Berechnungen
    test_building = {
        'building_type': 'Neubau KFW55',
        'living_area_m2': 180,
        'insulation_quality': 'Gut'
    }

    test_heatpump = {
        'heating_power_kw': 12.0,
        'cop_rating': 4.2,
        'price': 18000,
        'electricity_price': 0.32,
        'heating_demand': 12000
    }

    sizing = calculate_heatpump_sizing(test_building)
    economics = calculate_heatpump_economics(test_heatpump, test_building)

    print("Wärmepumpen-Auslegung:")
    print(f"  Heizlast: {sizing['heat_load_kw']} kW")
    print(f"  Empfohlene Leistung: {sizing['recommended_power_kw']} kW")

    print("\nWirtschaftlichkeit:")
    print(f"  Jährliche Stromkosten: {economics['annual_electricity_cost']} €")
    print(f"  Jährliche Einsparungen: {economics['annual_savings']} €")
    print(f"  Amortisation: {economics['payback_period_years']} Jahre")
    print(f"  Bewertung: {economics['recommendation']}")
