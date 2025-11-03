"""
Erweiterte Berechnungen für Gebäudesanierung und Wärmepumpen-Optimierung
Teil des Wärmepumpen-Moduls - Feature-Erweiterung

Author: GitHub Copilot
Version: 2.0 (Advanced Features)
Date: 2025-11-03
"""

from typing import Any
import math


# ============================================================================
# FEATURE 1: DÄMMUNGS-UPGRADE-RECHNER
# ============================================================================

def calculate_insulation_upgrade(
    building_data: dict[str, Any],
    current_state: dict[str, str],
    target_state: dict[str, str]
) -> dict[str, Any]:
    """
    Berechnet Kosten und Einsparungen für Dämmungs-Upgrades
    
    Args:
        building_data: Gebäudedaten (Fläche, Heizlast)
        current_state: Aktueller Zustand {"roof": "uninsulated", "facade": "poor", ...}
        target_state: Ziel-Zustand {"roof": "20cm", "facade": "16cm", ...}
    
    Returns:
        Dict mit Kosten, Einsparungen, ROI pro Maßnahme
    """
    
    # U-Werte (W/m²K) für verschiedene Dämmzustände
    u_values = {
        "roof": {
            "uninsulated": 1.5,
            "10cm": 0.35,
            "20cm": 0.20,
            "30cm": 0.14
        },
        "facade": {
            "uninsulated": 1.4,
            "poor": 1.0,
            "12cm": 0.28,
            "16cm": 0.21,
            "20cm": 0.17
        },
        "basement": {
            "uninsulated": 1.0,
            "8cm": 0.35,
            "12cm": 0.25,
            "16cm": 0.19
        },
        "windows": {
            "single": 5.0,
            "double_old": 3.0,
            "double_new": 1.3,
            "triple": 0.8
        }
    }
    
    # Kosten pro m² (EUR)
    costs_per_m2 = {
        "roof": {"10cm": 80, "20cm": 100, "30cm": 120},
        "facade": {"12cm": 140, "16cm": 160, "20cm": 180},
        "basement": {"8cm": 50, "12cm": 60, "16cm": 70},
        "windows": {"double_new": 400, "triple": 550}
    }
    
    # Gebäudeflächen schätzen
    living_area = building_data.get("living_area_m2", 150)
    floors = building_data.get("floors", 2)
    
    roof_area = living_area / floors
    facade_area = living_area * 0.8  # Vereinfacht: 80% der Wohnfläche
    basement_area = living_area / floors
    window_area = living_area * 0.15  # 15% Fensteranteil
    
    areas = {
        "roof": roof_area,
        "facade": facade_area,
        "basement": basement_area,
        "windows": window_area
    }
    
    # Heizgradtage (Deutschland Durchschnitt)
    heating_degree_days = 3500
    
    results = {}
    total_investment = 0
    total_savings = 0
    
    for component in ["roof", "facade", "basement", "windows"]:
        current = current_state.get(component, "uninsulated")
        target = target_state.get(component, current)
        
        if current == target:
            continue
        
        # U-Wert-Differenz
        u_current = u_values[component].get(current, 1.0)
        u_target = u_values[component].get(target, 1.0)
        delta_u = u_current - u_target
        
        # Jährliche Einsparung (kWh)
        area = areas[component]
        annual_savings_kwh = delta_u * area * heating_degree_days * 0.024
        
        # Kosteneinsparung (bei 0.10 EUR/kWh für Heizöl/Gas)
        annual_savings_eur = annual_savings_kwh * 0.10
        
        # Investitionskosten
        if component == "windows":
            investment = area * costs_per_m2[component].get(target, 400)
        else:
            investment = area * costs_per_m2[component].get(target, 100)
        
        # Amortisation
        payback_years = investment / annual_savings_eur if annual_savings_eur > 0 else 999
        
        results[component] = {
            "area_m2": round(area, 1),
            "u_current": u_current,
            "u_target": u_target,
            "delta_u": round(delta_u, 2),
            "annual_savings_kwh": round(annual_savings_kwh, 0),
            "annual_savings_eur": round(annual_savings_eur, 2),
            "investment_eur": round(investment, 2),
            "payback_years": round(payback_years, 1),
            "current_state": current,
            "target_state": target
        }
        
        total_investment += investment
        total_savings += annual_savings_eur
    
    # Optimale Reihenfolge (nach ROI)
    sorted_measures = sorted(
        results.items(),
        key=lambda x: x[1]["payback_years"]
    )
    
    return {
        "measures": results,
        "optimal_order": [m[0] for m in sorted_measures],
        "total_investment_eur": round(total_investment, 2),
        "total_annual_savings_eur": round(total_savings, 2),
        "total_payback_years": round(total_investment / total_savings, 1) if total_savings > 0 else 999,
        "savings_20_years_eur": round(total_savings * 20 - total_investment, 2)
    }


# ============================================================================
# FEATURE 2: HEIZKÖRPER VS. FUSSBODENHEIZUNG OPTIMIZER
# ============================================================================

def compare_heating_systems(
    building_data: dict[str, Any],
    current_system: str = "radiators",
    rooms: list[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Vergleicht Heizkörper vs. Fußbodenheizung für optimale Wärmepumpen-Effizienz
    
    Args:
        building_data: Gebäudedaten
        current_system: "radiators" oder "underfloor"
        rooms: Liste von Räumen mit Fläche und Nutzung
    
    Returns:
        Vergleich mit Kosten, Effizienz, Komfort
    """
    
    if rooms is None:
        # Standard-Raumaufteilung wenn nicht angegeben
        living_area = building_data.get("living_area_m2", 150)
        rooms = [
            {"name": "Wohnzimmer", "area_m2": living_area * 0.30, "usage": "living"},
            {"name": "Küche", "area_m2": living_area * 0.15, "usage": "kitchen"},
            {"name": "Schlafzimmer", "area_m2": living_area * 0.20, "usage": "bedroom"},
            {"name": "Bad", "area_m2": living_area * 0.10, "usage": "bathroom"},
            {"name": "Kinderzimmer", "area_m2": living_area * 0.15, "usage": "bedroom"},
            {"name": "Flur", "area_m2": living_area * 0.10, "usage": "hallway"}
        ]
    
    # Vorlauftemperaturen für verschiedene Systeme
    flow_temps = {
        "radiators_old": 70,      # Alte Radiatoren
        "radiators_new": 55,      # Niedertemperatur-Radiatoren
        "underfloor": 35          # Fußbodenheizung
    }
    
    # COP-Abhängigkeit von Vorlauftemperatur (Luft-Wasser WP)
    def calculate_cop_at_temp(flow_temp: float) -> float:
        # Vereinfachte Formel: COP sinkt mit steigender Vorlauftemperatur
        # Bei 35°C: COP ~4.5, bei 55°C: COP ~3.5, bei 70°C: COP ~2.8
        return 6.0 - (flow_temp - 20) * 0.04
    
    # Installationskosten pro m²
    installation_costs = {
        "radiators_new": 80,      # Neue Niedertemperatur-Radiatoren
        "underfloor": 60          # Fußbodenheizung (Neubau/Sanierung)
    }
    
    # Komfort-Faktoren (1-10)
    comfort_scores = {
        "radiators": {"comfort": 6, "dust": 4, "flexibility": 8},
        "underfloor": {"comfort": 9, "dust": 9, "flexibility": 3}
    }
    
    results = {}
    
    for system in ["radiators_new", "underfloor"]:
        flow_temp = flow_temps[system]
        cop = calculate_cop_at_temp(flow_temp)
        
        # Gesamtfläche
        total_area = sum(r["area_m2"] for r in rooms)
        
        # Installationskosten
        if current_system == "radiators" and system == "radiators_new":
            # Upgrade bestehender Radiatoren
            installation = total_area * 40  # Nur Austausch
        elif current_system == "radiators" and system == "underfloor":
            # Komplett neue Fußbodenheizung
            installation = total_area * installation_costs[system] * 1.5  # +50% für Estrich-Aufbau
        else:
            installation = total_area * installation_costs[system]
        
        # Jährliche Betriebskosten
        heat_load_kw = building_data.get("heat_load_kw", 10)
        annual_heat_kwh = heat_load_kw * 1800
        electricity_kwh = annual_heat_kwh / cop
        electricity_cost_eur = electricity_kwh * 0.32
        
        results[system] = {
            "flow_temperature_c": flow_temp,
            "cop": round(cop, 2),
            "installation_cost_eur": round(installation, 2),
            "annual_electricity_kwh": round(electricity_kwh, 0),
            "annual_cost_eur": round(electricity_cost_eur, 2),
            "comfort_score": comfort_scores["underfloor" if system == "underfloor" else "radiators"]
        }
    
    # Vergleich
    radiators = results["radiators_new"]
    underfloor = results["underfloor"]
    
    savings_per_year = radiators["annual_cost_eur"] - underfloor["annual_cost_eur"]
    additional_investment = underfloor["installation_cost_eur"] - radiators["installation_cost_eur"]
    payback_years = additional_investment / savings_per_year if savings_per_year > 0 else 999
    
    return {
        "systems": results,
        "comparison": {
            "annual_savings_eur": round(savings_per_year, 2),
            "additional_investment_eur": round(additional_investment, 2),
            "payback_years": round(payback_years, 1),
            "cop_improvement_percent": round((underfloor["cop"] - radiators["cop"]) / radiators["cop"] * 100, 1),
            "recommendation": "Fußbodenheizung" if payback_years < 15 else "Niedertemperatur-Radiatoren"
        },
        "rooms": rooms
    }


# ============================================================================
# FEATURE 3: FENSTER-SANIERUNGS-ASSISTENT
# ============================================================================

def calculate_window_upgrade(
    building_data: dict[str, Any],
    current_glazing: str = "double_old",
    target_glazing: str = "triple",
    orientation_mix: dict[str, float] = None
) -> dict[str, Any]:
    """
    Berechnet Fenster-Sanierung mit U-Wert-Vergleich und solaren Gewinnen
    
    Args:
        building_data: Gebäudedaten
        current_glazing: "single", "double_old", "double_new", "triple"
        target_glazing: Ziel-Verglasung
        orientation_mix: {"north": 0.2, "east": 0.2, "south": 0.4, "west": 0.2}
    
    Returns:
        Kosten, Einsparung, ROI mit solaren Gewinnen
    """
    
    # U-Werte (W/m²K)
    u_values = {
        "single": 5.0,
        "double_old": 3.0,
        "double_new": 1.3,
        "triple": 0.8,
        "triple_plus": 0.5
    }
    
    # g-Werte (Gesamtenergiedurchlassgrad - solare Gewinne)
    g_values = {
        "single": 0.85,
        "double_old": 0.75,
        "double_new": 0.60,
        "triple": 0.55,
        "triple_plus": 0.50
    }
    
    # Kosten pro m² Fensterfläche
    costs_per_m2 = {
        "double_new": 400,
        "triple": 550,
        "triple_plus": 700
    }
    
    if orientation_mix is None:
        orientation_mix = {
            "north": 0.20,
            "east": 0.20,
            "south": 0.35,
            "west": 0.25
        }
    
    # Solare Einstrahlung (kWh/m²/Jahr) nach Himmelsrichtung
    solar_irradiance = {
        "north": 100,
        "east": 400,
        "south": 700,
        "west": 450
    }
    
    living_area = building_data.get("living_area_m2", 150)
    window_area = living_area * 0.15  # 15% Fensteranteil
    
    # Wärmeverluste berechnen
    u_current = u_values[current_glazing]
    u_target = u_values[target_glazing]
    delta_u = u_current - u_target
    
    heating_degree_days = 3500
    heat_loss_reduction_kwh = delta_u * window_area * heating_degree_days * 0.024
    
    # Solare Gewinne berechnen
    g_current = g_values[current_glazing]
    g_target = g_values[target_glazing]
    
    solar_gain_current = 0
    solar_gain_target = 0
    
    for orientation, fraction in orientation_mix.items():
        area_orientation = window_area * fraction
        irradiance = solar_irradiance[orientation]
        
        solar_gain_current += area_orientation * irradiance * g_current * 0.7  # 70% Nutzungsgrad
        solar_gain_target += area_orientation * irradiance * g_target * 0.7
    
    # Netto-Einsparung (Wärmeverluste - solare Gewinne)
    net_savings_kwh = heat_loss_reduction_kwh - (solar_gain_current - solar_gain_target)
    net_savings_eur = net_savings_kwh * 0.10  # 0.10 EUR/kWh für Gas/Öl
    
    # Investitionskosten
    investment = window_area * costs_per_m2.get(target_glazing, 550)
    
    # Förderung (15% für Fenster-Sanierung)
    subsidy = investment * 0.15
    net_investment = investment - subsidy
    
    payback_years = net_investment / net_savings_eur if net_savings_eur > 0 else 999
    
    return {
        "window_area_m2": round(window_area, 1),
        "current_glazing": current_glazing,
        "target_glazing": target_glazing,
        "u_value_improvement": {
            "current": u_current,
            "target": u_target,
            "reduction_percent": round((delta_u / u_current) * 100, 1)
        },
        "heat_loss_reduction_kwh": round(heat_loss_reduction_kwh, 0),
        "solar_gains": {
            "current_kwh": round(solar_gain_current, 0),
            "target_kwh": round(solar_gain_target, 0),
            "loss_kwh": round(solar_gain_current - solar_gain_target, 0)
        },
        "net_savings_kwh": round(net_savings_kwh, 0),
        "net_savings_eur": round(net_savings_eur, 2),
        "investment_eur": round(investment, 2),
        "subsidy_eur": round(subsidy, 2),
        "net_investment_eur": round(net_investment, 2),
        "payback_years": round(payback_years, 1),
        "savings_20_years_eur": round(net_savings_eur * 20 - net_investment, 2),
        "orientation_mix": orientation_mix
    }


# ============================================================================
# FEATURE 4: GESAMT-RENOVIERUNGS-PLANER
# ============================================================================

def create_renovation_roadmap(
    building_data: dict[str, Any],
    budget_total: float,
    current_states: dict[str, str],
    priorities: list[str] = None
) -> dict[str, Any]:
    """
    Erstellt optimalen Sanierungsfahrplan mit Budget-Optimierung
    
    Args:
        building_data: Gebäudedaten
        budget_total: Verfügbares Gesamt-Budget (EUR)
        current_states: Aktueller Zustand aller Komponenten
        priorities: Optionale Prioritäten-Liste
    
    Returns:
        Schritt-für-Schritt Sanierungsplan mit Förderungen
    """
    
    # Alle möglichen Maßnahmen definieren
    measures = {}
    
    # 1. Dämmung
    target_insulation = {
        "roof": "20cm",
        "facade": "16cm",
        "basement": "12cm",
        "windows": "triple"
    }
    
    insulation_result = calculate_insulation_upgrade(
        building_data,
        current_states,
        target_insulation
    )
    
    for component, data in insulation_result["measures"].items():
        measures[f"insulation_{component}"] = {
            "type": "insulation",
            "component": component,
            "investment": data["investment_eur"],
            "annual_savings": data["annual_savings_eur"],
            "payback": data["payback_years"],
            "priority_score": 100 / data["payback_years"] if data["payback_years"] > 0 else 0
        }
    
    # 2. Heizungssystem
    heating_comparison = compare_heating_systems(building_data, "radiators")
    underfloor_investment = heating_comparison["systems"]["underfloor"]["installation_cost_eur"]
    underfloor_savings = heating_comparison["comparison"]["annual_savings_eur"]
    
    measures["heating_underfloor"] = {
        "type": "heating",
        "component": "underfloor",
        "investment": underfloor_investment,
        "annual_savings": underfloor_savings,
        "payback": underfloor_investment / underfloor_savings if underfloor_savings > 0 else 999,
        "priority_score": 100 / (underfloor_investment / underfloor_savings) if underfloor_savings > 0 else 0
    }
    
    # 3. Fenster (wenn noch nicht in Dämmung)
    if "insulation_windows" not in measures:
        window_result = calculate_window_upgrade(building_data, "double_old", "triple")
        measures["windows_upgrade"] = {
            "type": "windows",
            "component": "windows",
            "investment": window_result["net_investment_eur"],
            "annual_savings": window_result["net_savings_eur"],
            "payback": window_result["payback_years"],
            "priority_score": 100 / window_result["payback_years"] if window_result["payback_years"] > 0 else 0
        }
    
    # Sortiere nach Priorität (ROI)
    if priorities:
        # Manuelle Prioritäten überschreiben
        for i, measure_key in enumerate(priorities):
            if measure_key in measures:
                measures[measure_key]["priority_score"] = 1000 - i * 10
    
    sorted_measures = sorted(
        measures.items(),
        key=lambda x: x[1]["priority_score"],
        reverse=True
    )
    
    # Budget-Optimierung: Wähle Maßnahmen bis Budget erschöpft
    roadmap = []
    remaining_budget = budget_total
    cumulative_savings = 0
    
    for measure_key, measure in sorted_measures:
        if measure["investment"] <= remaining_budget:
            roadmap.append({
                "step": len(roadmap) + 1,
                "measure": measure_key,
                "type": measure["type"],
                "component": measure["component"],
                "investment_eur": measure["investment"],
                "annual_savings_eur": measure["annual_savings"],
                "payback_years": measure["payback"],
                "cumulative_investment": round(budget_total - remaining_budget + measure["investment"], 2)
            })
            remaining_budget -= measure["investment"]
            cumulative_savings += measure["annual_savings"]
    
    # Förderungen berechnen (gesamt)
    total_investment = sum(m["investment_eur"] for m in roadmap)
    total_subsidy = total_investment * 0.20  # Durchschnittlich 20% Förderung
    net_investment = total_investment - total_subsidy
    
    return {
        "roadmap": roadmap,
        "summary": {
            "total_measures": len(roadmap),
            "total_investment_eur": round(total_investment, 2),
            "total_subsidy_eur": round(total_subsidy, 2),
            "net_investment_eur": round(net_investment, 2),
            "total_annual_savings_eur": round(cumulative_savings, 2),
            "overall_payback_years": round(net_investment / cumulative_savings, 1) if cumulative_savings > 0 else 999,
            "savings_20_years_eur": round(cumulative_savings * 20 - net_investment, 2),
            "remaining_budget_eur": round(remaining_budget, 2)
        },
        "excluded_measures": [k for k, v in sorted_measures if k not in [m["measure"] for m in roadmap]]
    }
