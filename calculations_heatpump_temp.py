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
        default_zero=False,
    )

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
    custom_efficiency: float | None = None,
) -> float:
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


"""
def calculate_domestic_hot_water_demand_DUPLICATE(
    living_area_m2: float,
    persons: int,
    daily_usage_liters_per_person: float = 50.0
) -> float:
    """
    Berechnet Warmwasserbedarf in kWh/Jahr

    Formel: persons * daily_usage * 365 * 0.04 kWh/Liter
    (0.04 kWh/L = Energie um 1L Wasser von 10°C auf 55°C zu erhitzen)

    Args:
        living_area_m2: Wohnfläche in m²
        persons: Anzahl Personen im Haushalt
        daily_usage_liters_per_person: Täglicher Warmwasserverbrauch pro Person

    Returns:
        Jährlicher Warmwasserbedarf in kWh

    Quelle: Excel 1-3.xlsx, PDF Seite 8
    """
    # Fallback: Schätze Personen aus Wohnfläche falls nicht angegeben
    if persons <= 0:
        persons = max(1, int(living_area_m2 / 40))  # ~40m² pro Person

    # Berechnung: Personen * Liter/Tag * Tage/Jahr * kWh/Liter
    annual_kwh = persons * daily_usage_liters_per_person * 365 * 0.04

    return round(annual_kwh, 1)


def calculate_heat_load_with_climate_zone(
    building_type: str,
    living_area_m2: float,
    climate_zone: str,  # "Kalt", "Gemäßigt", "Mild"
    insulation_quality: str,
    persons: int = 0
) -> dict:
    """
    Erweiterte Heizlastberechnung mit Klimazone und Warmwasser

    Args:
        building_type: Gebäudetyp (siehe calculate_building_heat_load)
        living_area_m2: Wohnfläche in m²
        climate_zone: "Kalt" (Alpen), "Gemäßigt" (Mitteleuropa), "Mild" (Süd)
        insulation_quality: "Gut", "Mittel", "Schlecht"
        persons: Anzahl Personen (für Warmwasser)

    Returns:
        dict mit heating_load_kw, dhw_load_kw, total_load_kw, annual_heating_demand_kwh, annual_dhw_demand_kwh

    Quelle: Excel 4.xlsx, PDF Seite 11
    """
    # Basis-Heizlast
    base_heating_load_kw = calculate_building_heat_load(
        building_type, living_area_m2, insulation_quality
    )

    # Klimafaktor anwenden
    climate_factors = {
        "Kalt": 1.2,      # Z.B. Alpenregion, harte Winter
        "Gemäßigt": 1.0,  # Mitteleuropa Standard
        "Mild": 0.8       # Südliche Regionen, milde Winter
    }
    climate_factor = climate_factors.get(climate_zone, 1.0)
    heating_load_kw = base_heating_load_kw * climate_factor

    # Warmwasser-Bedarf (typisch 12-15% vom Gesamtwärmebedarf)
    annual_dhw_kwh = calculate_domestic_hot_water_demand(
        living_area_m2, persons
    )

    # Warmwasser-Leistung (Spitzenlast für WW-Bereitung)
    dhw_load_kw = annual_dhw_kwh / 1800  # Vereinfachung: 1800 Volllaststunden

    # Gesamtlast
    total_load_kw = heating_load_kw + dhw_load_kw

    # Jahreswärmebedarf (Heizung)
    # Formel aus PDF: annual_demand = heat_load_kw * 1800 Volllaststunden
    annual_heating_kwh = heating_load_kw * 1800

    return {
        "heating_load_kw": round(heating_load_kw, 2),
        "dhw_load_kw": round(dhw_load_kw, 2),
        "total_load_kw": round(total_load_kw, 2),
        "annual_heating_demand_kwh": round(annual_heating_kwh, 0),
        "annual_dhw_demand_kwh": round(annual_dhw_kwh, 0),
        "total_annual_demand_kwh": round(annual_heating_kwh + annual_dhw_kwh, 0)
    }


def calculate_required_flow_temperature(
    heat_load_kw: float,
    radiator_area_m2: float,
    room_temperature_c: float = 20.0,
    radiator_exponent: float = 1.3  # n in Q ~ ΔT^n
) -> float:
    """
    Berechnet erforderliche Vorlauftemperatur für bestehende Radiatoren

    Formel: Q = k * A * ΔT^n → ΔT = (Q / (k * A))^(1/n)
    Dann: Vorlauf = Raum + ΔT

    Args:
        heat_load_kw: Heizlast in kW
        radiator_area_m2: Gesamte Radiatorenfläche in m²
        room_temperature_c: Raumtemperatur in °C
        radiator_exponent: Exponent n (typisch 1.3 für Radiatoren)

    Returns:
        Erforderliche Vorlauftemperatur in °C

    Quelle: PDF Seite 11 (Radiator Check)
    """
    # Wärmeübertragungskoeffizient k (typisch 10 W/(m²·K^n))
    k = 10.0

    # Umrechnung kW in W
    heat_load_w = heat_load_kw * 1000

    # ΔT berechnen: ΔT = (Q / (k * A))^(1/n)
    if radiator_area_m2 <= 0:
        # Fallback: Schätze Fläche aus Heizlast
        radiator_area_m2 = heat_load_kw * 0.15  # Faustformel: ~0.15 m²/kW

    delta_t = (heat_load_w / (k * radiator_area_m2)) ** (1 / radiator_exponent)

    # Vorlauftemperatur = Raumtemperatur + Übertemperatur
    flow_temp = room_temperature_c + delta_t

    return round(flow_temp, 1)


def check_radiator_compatibility(
    required_flow_temp: float,
    heatpump_max_temp: float = 70.0
) -> dict:
    """
    Prüft ob Radiatoren für Wärmepumpe geeignet sind

    Args:
        required_flow_temp: Erforderliche Vorlauftemperatur in °C
        heatpump_max_temp: Maximale Vorlauftemperatur der WP (Standard: 70°C)

    Returns:
        dict mit compatible, recommendation, efficiency_impact, upgrade_cost_estimate

    Quelle: PDF Seite 11
    """
    compatible = required_flow_temp <= heatpump_max_temp

    # Effizienz-Bewertung
    if required_flow_temp <= 55:
        recommendation = "Optimal"
        efficiency_impact = 0.0  # Kein COP-Verlust
        upgrade_cost = 0.0
    elif required_flow_temp <= 65:
        recommendation = "Grenzwertig"
        efficiency_impact = 15.0  # ~15% COP-Reduktion
        upgrade_cost = 3000.0  # Empfehlung: Einzelne Radiatoren vergrößern
    else:
        recommendation = "Upgrade nötig"
        efficiency_impact = 30.0  # ~30% COP-Reduktion
        upgrade_cost = 8000.0  # Komplett neue Radiatoren oder Fußbodenheizung

    return {
        "compatible": compatible,
        "recommendation": recommendation,
        "required_flow_temp": required_flow_temp,
        "efficiency_impact_percent": efficiency_impact,
        "upgrade_cost_estimate_eur": upgrade_cost
    }


def calculate_co2_costs_fossil_heating(
    fuel_type: str,  # "Heizöl", "Erdgas"
    annual_consumption_kwh: float,
    co2_price_per_ton: float = 85.0,  # Durchschnitt nächste 20 Jahre
    green_fuel_share: float = 0.0  # GEG: 2029: 15%, 2035: 30%, 2040: 60%
) -> dict:
    """
    Berechnet CO2-Kosten für fossile Heizung mit GEG-Regelung

    Args:
        fuel_type: "Heizöl" oder "Erdgas"
        annual_consumption_kwh: Jährlicher Verbrauch in kWh
        co2_price_per_ton: CO2-Preis in €/Tonne (2025: 55€ → 2045: 85€)
        green_fuel_share: Anteil grüner Brennstoffe (GEG-Pflicht)

    Returns:
        dict mit annual_co2_cost_eur, co2_emissions_tons, green_fuel_cost_premium, total_annual_cost

    Quelle: Excel 5.xlsx (CO2-Preis Tab)
    """
    # CO2-Emissionsfaktoren in kg/kWh
    co2_factors = {
        "Heizöl": 0.266,  # kg CO2 / kWh
        "Erdgas": 0.201   # kg CO2 / kWh
    }

    co2_factor = co2_factors.get(fuel_type, 0.25)

    # Fossiler Anteil (1 - grüner Anteil)
    fossil_share = 1.0 - green_fuel_share

    # CO2-Emissionen nur für fossilen Anteil
    co2_emissions_tons = (annual_consumption_kwh * co2_factor * fossil_share) / 1000

    # CO2-Kosten
    annual_co2_cost = co2_emissions_tons * co2_price_per_ton

    # Grüne Brennstoff-Mehrkosten (aus Excel 5: +42.5% Öl, +28.3% Gas)
    green_fuel_premium_percent = {
        "Heizöl": 42.5,
        "Erdgas": 28.3
    }
    premium_percent = green_fuel_premium_percent.get(fuel_type, 35.0)

    # Basis-Brennstoffkosten (ohne CO2)
    fuel_base_prices = {
        "Heizöl": 0.10,  # €/kWh
        "Erdgas": 0.08   # €/kWh
    }
    base_price = fuel_base_prices.get(fuel_type, 0.09)
    base_fuel_cost = annual_consumption_kwh * base_price

    # Mehrkosten für grünen Anteil
    green_fuel_cost_premium = base_fuel_cost * green_fuel_share * (premium_percent / 100)

    # Gesamtkosten
    total_annual_cost = base_fuel_cost + annual_co2_cost + green_fuel_cost_premium

    return {
        "annual_co2_cost_eur": round(annual_co2_cost, 2),
        "co2_emissions_tons": round(co2_emissions_tons, 2),
        "green_fuel_cost_premium_eur": round(green_fuel_cost_premium, 2),
        "total_annual_cost_eur": round(total_annual_cost, 2),
        "fossil_share": fossil_share,
        "green_share": green_fuel_share
    }


def calculate_green_fuel_premium(
    fuel_type: str,
    kwh_consumed: float,
    green_share: float
) -> float:
    """
    Berechnet Mehrkosten für grüne Brennstoffe (GEG-Pflicht ab 2029)

    Basis Excel 5.xlsx: Industriestrom 0.17€/kWh, Wirkungsgradverluste 40-60%

    Args:
        fuel_type: "Heizöl" oder "Erdgas"
        kwh_consumed: Verbrauchte kWh
        green_share: Anteil grüne Brennstoffe (0.0 bis 1.0)

    Returns:
        Mehrkosten in €

    Quelle: Excel 5.xlsx (Grüne Brennstoffe)
    """
    # Mehrkosten-Faktoren aus Excel
    premium_factors = {
        "Heizöl": 0.425,  # +42.5%
        "Erdgas": 0.283   # +28.3%
    }

    # Basis-Preis
    base_prices = {
        "Heizöl": 0.10,
        "Erdgas": 0.08
    }

    factor = premium_factors.get(fuel_type, 0.35)
    base_price = base_prices.get(fuel_type, 0.09)

    # Mehrkosten = Verbrauch * Basispreis * Grünanteil * Mehrkosten-Faktor
    premium = kwh_consumed * base_price * green_share * factor

    return round(premium, 2)


def calculate_beg_subsidy(
    investment_cost_eur: float,
    replaces_gas_oil: bool = True,
    household_income_below_threshold: bool = False
) -> dict:
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

    fossil_annual_cost = co2_costs["total_annual_cost_eur"]

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
    co2_savings_tons_per_year = co2_costs["co2_emissions_tons"]
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
            "co2_emissions_tons_per_year": co2_costs["co2_emissions_tons"]
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
"""


# Test-Funktion auskommentiert für Produktionscode
"""
if __name__ == "__main__":
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

