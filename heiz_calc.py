# -*- coding: utf-8 -*-
"""
heiz_calc.py
------------------
Berechnungen für:
1) Heizlast
2) Heizkörper-/Vorlauftemperatur
3) Heizkosten/Wirtschaftlichkeit
"""
from typing import Dict, Any, Tuple

# 1) Heizlastrechner (vereinfachte DIN-Logik mit Klimafaktoren)
BUILDING_WM2 = {
    "Neubau KfW40": 35,
    "Neubau KfW55": 45,
    "Sanierter Altbau (gut)": 60,
    "Teilsaniert (mittel)": 85,
    "Altbau unsaniert": 120
}
INSULATION_FACTORS = {"gut": 0.90, "mittel": 1.00, "schlecht": 1.20}
CLIMATE_FACTORS    = {"mild (Küste, -10°C)": 0.90, "gemäßigt (Mitte, -12°C)": 1.00, "kalt (Süd/Hohe Lagen, -16°C)": 1.15}
VENTILATION_FACTORS= {"niedrig (WRG vorhanden)": 0.92, "mittel": 1.00, "hoch": 1.08}

def calculate_heat_load_kw(area_m2: float, building_type: str, insulation: str,
                           climate: str, ventilation: str, occupants: int = 3, include_dhw: bool = True) -> Dict[str, float]:
    base = BUILDING_WM2.get(building_type, 90)
    heat_kw = (base * INSULATION_FACTORS.get(insulation,1.0) *
               CLIMATE_FACTORS.get(climate,1.0) *
               VENTILATION_FACTORS.get(ventilation,1.0) *
               area_m2) / 1000.0
    dhw_kw = 0.2 * max(1, occupants) if include_dhw else 0.0
    return {"heat_load_kw": round(heat_kw,2), "dhw_kw": round(dhw_kw,2), "total_kw": round(heat_kw+dhw_kw,2)}

# 2) Heizkörper/Vorlauftemperatur – ΔT^n mit Übersizing-Faktor
def radiator_required_flow_temp(required_heat_kw: float, room_temp_c: float = 20.0,
                                design_flow_c: float = 70.0, design_return_c: float = 55.0,
                                oversizing_factor: float = 1.15, exponent_n: float = 1.30) -> Dict[str, float]:
    t_mean_old = (design_flow_c + design_return_c)/2.0
    delta_old = max(1.0, t_mean_old - room_temp_c)
    delta_new = delta_old * (1.0/oversizing_factor)**(1.0/exponent_n)
    t_mean_new = room_temp_c + delta_new
    return {"required_flow_c": round(t_mean_new+5,1), "required_return_c": round(t_mean_new-5,1), "delta_new": round(delta_new,1)}

def radiator_compatibility(flow_c: float) -> Tuple[str, str]:
    if flow_c <= 55: return "Optimal", "Sehr gute Effizienz (hoher COP), keine Maßnahmen nötig."
    if flow_c <= 60: return "Gut", "Leichter Effizienzverlust, i.d.R. unkritisch."
    if flow_c <= 65: return "Grenzwertig", "Effizienzverlust; größere Heizkörper empfehlen sich."
    if flow_c <= 70: return "Kritisch", "Deutlicher Effizienzverlust; Heizkörper/Flächenheizung nachrüsten."
    return "Ungeeignet", "Mit Monobloc kaum realisierbar; Systemanpassung erforderlich."

# 3) Heizkosten/Amortisation
FUEL_CO2 = {"Gas": 0.201, "Öl": 0.266, "Strom": 0.366}  # kg/kWh (Strom: grober Mix)

def economics_heatpump(annual_heat_kwh: float, scop: float, electricity_price_eur_per_kwh: float,
                       alt_fuel: str, alt_fuel_price_eur_per_kwh: float, alt_system_efficiency: float,
                       investment_cost_eur: float, subsidy_rate: float = 0.0,
                       carbon_price_eur_per_ton: float = 0.0) -> Dict[str, Any]:
    scop = max(1.0, scop)
    wp_strom_kwh = annual_heat_kwh / scop
    wp_kosten = wp_strom_kwh * electricity_price_eur_per_kwh

    eff = min(1.0, max(0.5, alt_system_efficiency))
    alt_end_kwh = annual_heat_kwh / eff
    alt_kosten = alt_end_kwh * alt_fuel_price_eur_per_kwh

    einsparung = alt_kosten - wp_kosten
    subsidy_rate = min(0.8, max(0.0, subsidy_rate))
    netto_invest = investment_cost_eur * (1.0 - subsidy_rate)
    payback = round(netto_invest / einsparung, 1) if einsparung > 0 else None

    co2_alt_t = (alt_end_kwh * FUEL_CO2.get(alt_fuel,0.0))/1000.0
    co2_wp_t  = (wp_strom_kwh * FUEL_CO2["Strom"])/1000.0
    co2_diff  = co2_alt_t - co2_wp_t
    co2_cost  = round(co2_diff * carbon_price_eur_per_ton, 2) if carbon_price_eur_per_ton>0 else None

    return {
        "wp_strom_kwh": round(wp_strom_kwh,0), "wp_kosten_eur": round(wp_kosten,2),
        "alt_kosten_eur": round(alt_kosten,2), "einsparung_eur_pro_jahr": round(einsparung,2),
        "netto_invest_eur": round(netto_invest,2), "payback_jahre": payback,
        "co2_alt_t": round(co2_alt_t,2), "co2_wp_t": round(co2_wp_t,2), "co2_einsparung_t": round(co2_diff,2),
        "co2_kostenersparnis_eur": co2_cost
    }
