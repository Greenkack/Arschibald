"""
Erweiterte Berechnungen für Wärmepumpen - Teil 2
Features 5-8: Optimierung und Analyse

Author: GitHub Copilot
Version: 2.0
Date: 2025-11-03
"""

from typing import Any
import math
import random


# ============================================================================
# FEATURE 5: VERBRAUCHSOPTIMIERER TURBO
# ============================================================================

def optimize_heating_schedule(
    building_data: dict[str, Any],
    occupancy_profile: dict[str, list[float]],
    electricity_tariff: dict[str, float] = None
) -> dict[str, Any]:
    """
    Optimiert Heizplan basierend auf Anwesenheit und Stromtarifen
    
    Args:
        building_data: Gebäudedaten mit Heizlast
        occupancy_profile: {"monday": [0,0,0,0,0,1,1,1,...], ...} (24h-Profile)
        electricity_tariff: {"day": 0.32, "night": 0.22} (EUR/kWh)
    
    Returns:
        Optimaler Heizplan mit Kosten-Einsparung
    """
    
    if electricity_tariff is None:
        electricity_tariff = {"day": 0.32, "night": 0.22, "peak": 0.42}
    
    # Tageszeiten definieren
    time_periods = {
        "night": list(range(0, 6)),      # 0-6 Uhr
        "morning": list(range(6, 9)),     # 6-9 Uhr
        "day": list(range(9, 18)),        # 9-18 Uhr
        "evening": list(range(18, 22)),   # 18-22 Uhr
        "late": list(range(22, 24))       # 22-24 Uhr
    }
    
    # Tarife nach Tageszeit
    tariff_by_hour = []
    for hour in range(24):
        if hour in time_periods["night"] or hour in time_periods["late"]:
            tariff_by_hour.append(electricity_tariff["night"])
        elif hour in time_periods["morning"] or hour in time_periods["evening"]:
            tariff_by_hour.append(electricity_tariff["peak"])
        else:
            tariff_by_hour.append(electricity_tariff["day"])
    
    heat_load_kw = building_data.get("heat_load_kw", 10)
    cop = building_data.get("cop", 3.5)
    
    # Gebäude-Trägheit (Stunden bis 1°C Temperaturabfall)
    thermal_mass_hours = building_data.get("thermal_mass_hours", 4)
    
    # Wochen-Durchschnitt der Anwesenheit
    weekly_schedule = []
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        weekly_schedule.extend(occupancy_profile.get(day, [1] * 24))
    
    # Strategie 1: Konstante Heizung (Baseline)
    baseline_cost = 0
    for hour_profile in weekly_schedule:
        power_kw = heat_load_kw * 0.8  # 80% Durchschnittslast
        electricity_kw = power_kw / cop
        hour_index = len([x for x in weekly_schedule[:weekly_schedule.index(hour_profile)]]) % 24
        cost = electricity_kw * tariff_by_hour[hour_index]
        baseline_cost += cost
    
    # Strategie 2: Optimierte Heizung (Vorheizen in Niedrigtarif-Zeiten)
    optimized_cost = 0
    optimized_schedule = []
    
    for i, occupancy in enumerate(weekly_schedule):
        hour = i % 24
        
        # Ist Vorheizen sinnvoll?
        next_hours_occupied = sum(weekly_schedule[i:i+thermal_mass_hours]) if i+thermal_mass_hours < len(weekly_schedule) else 0
        current_tariff = tariff_by_hour[hour]
        
        if occupancy > 0.5:
            # Anwesend: Normal heizen
            power_kw = heat_load_kw * 0.8
            mode = "normal"
        elif next_hours_occupied > 0 and current_tariff == electricity_tariff["night"]:
            # Vorheizen im Niedrigtarif
            power_kw = heat_load_kw * 1.2  # 20% mehr zum Vorheizen
            mode = "preheat"
        else:
            # Absenken
            power_kw = heat_load_kw * 0.3  # 30% Grundlast
            mode = "reduced"
        
        electricity_kw = power_kw / cop
        cost = electricity_kw * current_tariff
        optimized_cost += cost
        
        optimized_schedule.append({
            "hour": hour,
            "day": i // 24,
            "occupancy": occupancy,
            "mode": mode,
            "power_kw": round(power_kw, 2),
            "electricity_kw": round(electricity_kw, 2),
            "cost_eur": round(cost, 3),
            "tariff_eur_kwh": current_tariff
        })
    
    # Wochen-Zusammenfassung
    weekly_savings = baseline_cost - optimized_cost
    annual_savings = weekly_savings * 52
    
    return {
        "baseline": {
            "weekly_cost_eur": round(baseline_cost, 2),
            "annual_cost_eur": round(baseline_cost * 52, 2),
            "strategy": "Konstante Temperatur"
        },
        "optimized": {
            "weekly_cost_eur": round(optimized_cost, 2),
            "annual_cost_eur": round(optimized_cost * 52, 2),
            "strategy": "Vorheizen + Nachtabsenkung"
        },
        "savings": {
            "weekly_eur": round(weekly_savings, 2),
            "annual_eur": round(annual_savings, 2),
            "percent": round((weekly_savings / baseline_cost) * 100, 1)
        },
        "schedule": optimized_schedule,
        "tariff_structure": electricity_tariff
    }


# ============================================================================
# FEATURE 6: KLIMAWANDEL-SZENARIEN 2025-2050
# ============================================================================

def simulate_climate_scenarios(
    building_data: dict[str, Any],
    location: str = "Germany"
) -> dict[str, Any]:
    """
    Simuliert Heizkosten-Entwicklung unter verschiedenen Klimaszenarien
    
    Args:
        building_data: Gebäudedaten
        location: Standort für regionale Anpassung
    
    Returns:
        30-Jahres-Prognose mit 3 Szenarien (best/middle/worst case)
    """
    
    # Baseline: Heizgradtage 2024
    base_heating_degree_days = 3500
    
    # Klimaszenarien (Temperaturanstieg)
    scenarios = {
        "optimistic": {  # 1.5°C Erderwärmung bis 2050
            "name": "Paris-Ziel erreicht (1.5°C)",
            "temp_increase_per_year": 0.06,  # °C/Jahr
            "energy_price_increase": 0.02    # 2% jährlich
        },
        "realistic": {   # 2.5°C Erderwärmung bis 2050
            "name": "Mittleres Szenario (2.5°C)",
            "temp_increase_per_year": 0.10,
            "energy_price_increase": 0.03    # 3% jährlich
        },
        "pessimistic": { # 4.0°C Erderwärmung bis 2050
            "name": "Weiter wie bisher (4.0°C)",
            "temp_increase_per_year": 0.16,
            "energy_price_increase": 0.05    # 5% jährlich (Ressourcenknappheit)
        }
    }
    
    # Aktuelle Werte
    heat_load_kw = building_data.get("heat_load_kw", 10)
    cop = building_data.get("cop", 3.5)
    electricity_price_2024 = 0.32  # EUR/kWh
    
    results = {}
    
    for scenario_key, scenario in scenarios.items():
        yearly_data = []
        cumulative_cost = 0
        
        for year_offset in range(0, 27):  # 2024 bis 2050
            year = 2024 + year_offset
            
            # Temperaturanstieg
            temp_increase = scenario["temp_increase_per_year"] * year_offset
            
            # Heizgradtage sinken (ca. 3% pro °C Erwärmung)
            hdd_reduction_factor = 1 - (temp_increase * 0.03)
            heating_degree_days = base_heating_degree_days * hdd_reduction_factor
            
            # Jährlicher Wärmebedarf
            annual_heat_kwh = heat_load_kw * heating_degree_days * 0.024
            
            # COP verbessert sich (Technik-Fortschritt + wärmere Außentemperaturen)
            cop_improvement = 1 + (year_offset * 0.02)  # 2% pro Jahr
            temp_improvement = 1 + (temp_increase * 0.05)  # 5% pro °C
            current_cop = cop * cop_improvement * temp_improvement
            
            # Strombedarf
            electricity_kwh = annual_heat_kwh / current_cop
            
            # Strompreis
            price_factor = (1 + scenario["energy_price_increase"]) ** year_offset
            electricity_price = electricity_price_2024 * price_factor
            
            # Kosten
            annual_cost = electricity_kwh * electricity_price
            cumulative_cost += annual_cost
            
            yearly_data.append({
                "year": year,
                "temp_increase_c": round(temp_increase, 2),
                "heating_degree_days": round(heating_degree_days, 0),
                "annual_heat_kwh": round(annual_heat_kwh, 0),
                "cop": round(current_cop, 2),
                "electricity_kwh": round(electricity_kwh, 0),
                "electricity_price_eur_kwh": round(electricity_price, 3),
                "annual_cost_eur": round(annual_cost, 2),
                "cumulative_cost_eur": round(cumulative_cost, 2)
            })
        
        results[scenario_key] = {
            "name": scenario["name"],
            "yearly_data": yearly_data,
            "summary_2050": {
                "temp_increase_c": round(scenario["temp_increase_per_year"] * 26, 1),
                "heating_reduction_percent": round((1 - hdd_reduction_factor) * 100, 1),
                "final_cop": round(yearly_data[-1]["cop"], 2),
                "electricity_price_2050": round(yearly_data[-1]["electricity_price_eur_kwh"], 3),
                "cumulative_cost_2024_2050_eur": round(cumulative_cost, 2),
                "annual_cost_2050_eur": round(yearly_data[-1]["annual_cost_eur"], 2)
            }
        }
    
    return {
        "scenarios": results,
        "comparison": {
            "best_case_total": round(results["optimistic"]["summary_2050"]["cumulative_cost_2024_2050_eur"], 2),
            "worst_case_total": round(results["pessimistic"]["summary_2050"]["cumulative_cost_2024_2050_eur"], 2),
            "difference_eur": round(
                results["pessimistic"]["summary_2050"]["cumulative_cost_2024_2050_eur"] -
                results["optimistic"]["summary_2050"]["cumulative_cost_2024_2050_eur"],
                2
            )
        },
        "location": location,
        "base_year": 2024
    }


# ============================================================================
# FEATURE 7: WÄRMEPUMPEN-AUSWAHL-MATRIX
# ============================================================================

def compare_heatpump_types(
    building_data: dict[str, Any],
    plot_size_m2: float = 500,
    groundwater_available: bool = False
) -> dict[str, Any]:
    """
    Vergleicht alle Wärmepumpen-Typen mit COP, Kosten, Lautstärke, etc.
    
    Args:
        building_data: Gebäudedaten
        plot_size_m2: Grundstücksgröße für Erdwärme-Option
        groundwater_available: Grundwasser-Nutzung möglich?
    
    Returns:
        Matrix mit allen WP-Typen und Bewertungen
    """
    
    heat_load_kw = building_data.get("heat_load_kw", 10)
    
    # WP-Typen definieren
    heatpump_types = {
        "air_water": {
            "name": "Luft-Wasser-Wärmepumpe",
            "cop_avg": 3.5,
            "installation_cost_per_kw": 1200,
            "noise_db": 45,
            "plot_requirement_m2": 2,
            "permit_required": False,
            "maintenance_cost_annual": 200,
            "lifespan_years": 20,
            "pros": ["Günstig", "Einfache Installation", "Keine Genehmigung"],
            "cons": ["Lautstärke", "COP sinkt bei Kälte"]
        },
        "air_water_split": {
            "name": "Split-Luft-Wasser-Wärmepumpe",
            "cop_avg": 3.8,
            "installation_cost_per_kw": 1400,
            "noise_db": 35,
            "plot_requirement_m2": 1,
            "permit_required": False,
            "maintenance_cost_annual": 250,
            "lifespan_years": 20,
            "pros": ["Leiser", "Kompakt", "Guter COP"],
            "cons": ["Teurer als Monoblock"]
        },
        "brine_water": {
            "name": "Sole-Wasser-Wärmepumpe (Erdwärme)",
            "cop_avg": 4.5,
            "installation_cost_per_kw": 2000,
            "noise_db": 25,
            "plot_requirement_m2": 150,
            "permit_required": True,
            "maintenance_cost_annual": 150,
            "lifespan_years": 25,
            "pros": ["Sehr effizient", "Leise", "Konstanter COP"],
            "cons": ["Hohe Investition", "Genehmigungspflichtig", "Große Fläche"]
        },
        "water_water": {
            "name": "Wasser-Wasser-Wärmepumpe (Grundwasser)",
            "cop_avg": 5.0,
            "installation_cost_per_kw": 2500,
            "noise_db": 25,
            "plot_requirement_m2": 50,
            "permit_required": True,
            "maintenance_cost_annual": 300,
            "lifespan_years": 25,
            "pros": ["Höchste Effizienz", "Sehr leise", "Stabile Quelle"],
            "cons": ["Sehr teuer", "Grundwasser erforderlich", "Genehmigung kompliziert"]
        }
    }
    
    # Filtere nicht-verfügbare Optionen
    available_types = {}
    
    for wp_type, data in heatpump_types.items():
        # Sole-WP: Braucht genug Grundstücksfläche
        if wp_type == "brine_water" and plot_size_m2 < data["plot_requirement_m2"]:
            continue
        
        # Wasser-WP: Braucht Grundwasser
        if wp_type == "water_water" and not groundwater_available:
            continue
        
        available_types[wp_type] = data
    
    # Berechne Wirtschaftlichkeit für jeden Typ
    comparison = {}
    
    for wp_type, data in available_types.items():
        installation_cost = data["installation_cost_per_kw"] * heat_load_kw
        cop = data["cop_avg"]
        
        # Jährliche Betriebskosten
        annual_heat_kwh = heat_load_kw * 1800
        electricity_kwh = annual_heat_kwh / cop
        electricity_cost = electricity_kwh * 0.32
        maintenance_cost = data["maintenance_cost_annual"]
        total_annual_cost = electricity_cost + maintenance_cost
        
        # Lebenszeitkosten
        lifetime_cost = installation_cost + (total_annual_cost * data["lifespan_years"])
        
        # Förderung (35% für effiziente WP)
        subsidy_rate = 0.35 if cop >= 4.0 else 0.30
        subsidy = installation_cost * subsidy_rate
        net_installation = installation_cost - subsidy
        
        # Vergleich zu Luft-Wasser als Basis
        if "air_water" in available_types and wp_type != "air_water":
            base_annual_cost = available_types["air_water"]["installation_cost_per_kw"] * heat_load_kw * 0.30 / available_types["air_water"]["cop_avg"] * 0.32
            savings_vs_base = base_annual_cost - electricity_cost
            payback_years = (net_installation - (available_types["air_water"]["installation_cost_per_kw"] * heat_load_kw * 0.65)) / savings_vs_base if savings_vs_base > 0 else 999
        else:
            payback_years = 0
        
        comparison[wp_type] = {
            "name": data["name"],
            "cop": cop,
            "installation_cost_eur": round(installation_cost, 2),
            "subsidy_eur": round(subsidy, 2),
            "net_installation_eur": round(net_installation, 2),
            "annual_electricity_kwh": round(electricity_kwh, 0),
            "annual_electricity_cost_eur": round(electricity_cost, 2),
            "annual_maintenance_eur": maintenance_cost,
            "total_annual_cost_eur": round(total_annual_cost, 2),
            "lifetime_cost_eur": round(lifetime_cost, 2),
            "payback_vs_air_years": round(payback_years, 1),
            "noise_db": data["noise_db"],
            "plot_requirement_m2": data["plot_requirement_m2"],
            "permit_required": data["permit_required"],
            "lifespan_years": data["lifespan_years"],
            "pros": data["pros"],
            "cons": data["cons"]
        }
    
    # Ranking nach Lebenszykluskosten
    ranked = sorted(
        comparison.items(),
        key=lambda x: x[1]["lifetime_cost_eur"]
    )
    
    return {
        "comparison": comparison,
        "ranking": [{"rank": i+1, "type": k, "name": v["name"]} for i, (k, v) in enumerate(ranked)],
        "recommendation": ranked[0][0],
        "building_constraints": {
            "plot_size_m2": plot_size_m2,
            "groundwater_available": groundwater_available,
            "heat_load_kw": heat_load_kw
        }
    }


# ============================================================================
# FEATURE 8: 8760H-LASTGANG-ANALYSE
# ============================================================================

def simulate_annual_load_profile(
    building_data: dict[str, Any],
    location: str = "Germany"
) -> dict[str, Any]:
    """
    Simuliert stündliche Heizlast über ganzes Jahr (8760 Stunden)
    
    Args:
        building_data: Gebäudedaten
        location: Standort für Wetterdaten
    
    Returns:
        8760 Datenpunkte mit Lastprofil
    """
    
    heat_load_kw = building_data.get("heat_load_kw", 10)
    cop_nominal = building_data.get("cop", 3.5)
    
    # Vereinfachtes Temperaturmodell (sinusförmig)
    def outdoor_temp(day: int, hour: int) -> float:
        """Außentemperatur für Tag und Stunde"""
        # Jahresverlauf (sinusförmig, kältester Punkt Mitte Januar)
        year_factor = math.sin((day - 15) * 2 * math.pi / 365)
        avg_temp = 10 + year_factor * 12  # -2°C im Januar, +22°C im Juli
        
        # Tagesverlauf (sinusförmig, kälteste Zeit 6 Uhr morgens)
        day_factor = math.sin((hour - 6) * 2 * math.pi / 24)
        daily_variation = day_factor * 4  # ±4°C Schwankung
        
        return avg_temp + daily_variation
    
    # COP-Abhängigkeit von Außentemperatur
    def calculate_cop(t_outside: float, t_flow: float = 35) -> float:
        """COP basierend auf Carnot-Wirkungsgrad"""
        t_outside_k = t_outside + 273.15
        t_flow_k = t_flow + 273.15
        carnot_cop = t_flow_k / (t_flow_k - t_outside_k)
        # Real-COP ist ca. 50% von Carnot
        return carnot_cop * 0.50
    
    # 8760 Stunden simulieren
    hourly_data = []
    
    for day in range(365):
        for hour in range(24):
            t_outside = outdoor_temp(day, hour)
            
            # Heizgrenztemperatur: 15°C
            if t_outside >= 15:
                heat_demand_kw = 0
            else:
                # Heizlast steigt linear mit sinkender Temperatur
                heat_demand_kw = heat_load_kw * (1 - (t_outside + 12) / 27)  # Normierung auf -12°C
                heat_demand_kw = max(0, min(heat_demand_kw, heat_load_kw))
            
            # COP berechnen
            cop = calculate_cop(t_outside)
            
            # Stromverbrauch
            if heat_demand_kw > 0:
                electricity_kw = heat_demand_kw / cop
            else:
                electricity_kw = 0
            
            hourly_data.append({
                "day": day + 1,
                "hour": hour,
                "datetime": f"2024-{(day//30)+1:02d}-{(day%30)+1:02d} {hour:02d}:00",
                "t_outside_c": round(t_outside, 1),
                "heat_demand_kw": round(heat_demand_kw, 2),
                "cop": round(cop, 2),
                "electricity_kw": round(electricity_kw, 2)
            })
    
    # Zusammenfassung
    total_heat_kwh = sum(h["heat_demand_kw"] for h in hourly_data)
    total_electricity_kwh = sum(h["electricity_kw"] for h in hourly_data)
    avg_cop = total_heat_kwh / total_electricity_kwh if total_electricity_kwh > 0 else 0
    
    # Monats-Zusammenfassung
    monthly_summary = []
    for month in range(1, 13):
        month_data = [h for h in hourly_data if int(h["datetime"].split("-")[1]) == month]
        if month_data:
            monthly_summary.append({
                "month": month,
                "total_heat_kwh": round(sum(h["heat_demand_kw"] for h in month_data), 0),
                "total_electricity_kwh": round(sum(h["electricity_kw"] for h in month_data), 0),
                "avg_cop": round(sum(h["cop"] for h in month_data) / len(month_data), 2),
                "hours_operation": len([h for h in month_data if h["heat_demand_kw"] > 0])
            })
    
    return {
        "hourly_data": hourly_data,  # 8760 Datenpunkte
        "monthly_summary": monthly_summary,
        "annual_summary": {
            "total_heat_kwh": round(total_heat_kwh, 0),
            "total_electricity_kwh": round(total_electricity_kwh, 0),
            "annual_average_cop": round(avg_cop, 2),
            "operating_hours": len([h for h in hourly_data if h["heat_demand_kw"] > 0]),
            "annual_cost_eur": round(total_electricity_kwh * 0.32, 2)
        },
        "location": location
    }
