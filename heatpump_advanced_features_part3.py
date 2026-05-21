"""
Erweiterte Berechnungen für Wärmepumpen - Teil 3
Features 9-12: Finanzanalyse und Benchmarking

Author: GitHub Copilot
Version: 2.0
Date: 2025-11-03
"""

from typing import Any
import math
import random


# ============================================================================
# FEATURE 9: FÖRDERMITTEL-OPTIMIZER
# ============================================================================

def calculate_subsidies(
    building_data: dict[str, Any],
    measures: dict[str, bool],
    building_age: int = 30
) -> dict[str, Any]:
    """
    Berechnet alle verfügbaren Förderungen (BAFA, KfW, Länder)
    
    Args:
        building_data: Gebäudedaten
        measures: {"heatpump": True, "insulation": True, "windows": True, ...}
        building_age: Alter des Gebäudes (Jahre)
    
    Returns:
        Alle Förderungen mit Kombinationsmöglichkeiten
    """
    
    # BAFA-Förderung für Wärmepumpen (2024)
    bafa_heatpump = {
        "name": "BAFA Bundesförderung effiziente Gebäude (BEG)",
        "eligible": measures.get("heatpump", False),
        "base_rate": 0.25,  # 25% Grundförderung
        "bonus_renewable_ready": 0.05,  # +5% wenn renewable-ready
        "bonus_natural_refrigerant": 0.05,  # +5% für natürliches Kältemittel
        "max_rate": 0.40,  # Max 40%
        "max_amount_eur": 60000,
        "eligible_costs_max": 60000
    }
    
    # KfW-Kredit 261/262 (Wohngebäude-Kredit)
    kfw_loan = {
        "name": "KfW 261 Wohngebäude-Kredit",
        "eligible": building_age > 5,
        "loan_amount_max": 150000,
        "interest_rate": 0.01,  # 1% Zinssatz
        "tilgung_grant": 0.05,  # 5% Tilgungszuschuss bei EH55
        "duration_years": 30
    }
    
    # KfW 430 Zuschuss (auslaufend, aber noch gültig für Altanträge)
    kfw_grant = {
        "name": "KfW 430 Investitionszuschuss (Altanträge)",
        "eligible": False,  # Nur noch für Altanträge
        "rate": 0.20,
        "max_amount_eur": 30000
    }
    
    # Landesförderungen (Beispiel Baden-Württemberg)
    state_subsidy = {
        "name": "Landesförderung BW (Beispiel)",
        "eligible": measures.get("insulation", False),
        "rate": 0.10,
        "max_amount_eur": 10000,
        "combinable_with_bafa": True
    }
    
    # Kommunale Förderungen (Beispiel)
    local_subsidy = {
        "name": "Kommunale Förderung (Beispiel Stadt)",
        "eligible": True,
        "fixed_amount_eur": 2000,
        "combinable": True
    }
    
    # Investitionskosten abschätzen
    costs = {}
    
    if measures.get("heatpump", False):
        heat_load_kw = building_data.get("heat_load_kw", 10)
        costs["heatpump"] = heat_load_kw * 1400  # 1400 EUR/kW
    
    if measures.get("insulation", False):
        living_area = building_data.get("living_area_m2", 150)
        costs["insulation"] = living_area * 200  # Pauschal 200 EUR/m²
    
    if measures.get("windows", False):
        living_area = building_data.get("living_area_m2", 150)
        window_area = living_area * 0.15
        costs["windows"] = window_area * 550  # Dreifachverglasung
    
    total_investment = sum(costs.values())
    
    # BAFA berechnen
    subsidies_breakdown = []
    total_subsidy = 0
    
    if bafa_heatpump["eligible"]:
        hp_cost = costs.get("heatpump", 0)
        eligible_cost = min(hp_cost, bafa_heatpump["eligible_costs_max"])
        
        rate = bafa_heatpump["base_rate"]
        rate += bafa_heatpump["bonus_renewable_ready"]  # Annahme: immer renewable-ready
        rate = min(rate, bafa_heatpump["max_rate"])
        
        bafa_amount = eligible_cost * rate
        bafa_amount = min(bafa_amount, bafa_heatpump["max_amount_eur"])
        
        subsidies_breakdown.append({
            "program": bafa_heatpump["name"],
            "type": "grant",
            "amount_eur": round(bafa_amount, 2),
            "rate": round(rate * 100, 1),
            "eligible_cost_eur": round(eligible_cost, 2)
        })
        total_subsidy += bafa_amount
    
    # Landesförderung
    if state_subsidy["eligible"] and state_subsidy["combinable_with_bafa"]:
        insulation_cost = costs.get("insulation", 0)
        state_amount = insulation_cost * state_subsidy["rate"]
        state_amount = min(state_amount, state_subsidy["max_amount_eur"])
        
        subsidies_breakdown.append({
            "program": state_subsidy["name"],
            "type": "grant",
            "amount_eur": round(state_amount, 2),
            "rate": round(state_subsidy["rate"] * 100, 1),
            "eligible_cost_eur": round(insulation_cost, 2)
        })
        total_subsidy += state_amount
    
    # Kommunale Förderung
    if local_subsidy["eligible"]:
        subsidies_breakdown.append({
            "program": local_subsidy["name"],
            "type": "fixed_grant",
            "amount_eur": local_subsidy["fixed_amount_eur"],
            "rate": 0,
            "eligible_cost_eur": 0
        })
        total_subsidy += local_subsidy["fixed_amount_eur"]
    
    # KfW-Kredit
    loan_details = None
    if kfw_loan["eligible"]:
        loan_amount = min(total_investment - total_subsidy, kfw_loan["loan_amount_max"])
        tilgung_grant_amount = loan_amount * kfw_loan["tilgung_grant"]
        
        loan_details = {
            "program": kfw_loan["name"],
            "loan_amount_eur": round(loan_amount, 2),
            "interest_rate": kfw_loan["interest_rate"],
            "tilgung_grant_eur": round(tilgung_grant_amount, 2),
            "duration_years": kfw_loan["duration_years"],
            "monthly_rate_eur": round(loan_amount / (kfw_loan["duration_years"] * 12), 2)
        }
        total_subsidy += tilgung_grant_amount
    
    net_investment = total_investment - total_subsidy
    
    return {
        "total_investment_eur": round(total_investment, 2),
        "subsidies": subsidies_breakdown,
        "total_subsidy_eur": round(total_subsidy, 2),
        "subsidy_rate": round((total_subsidy / total_investment) * 100, 1) if total_investment > 0 else 0,
        "net_investment_eur": round(net_investment, 2),
        "loan_option": loan_details,
        "measures": measures,
        "application_checklist": [
            "Energieberater-Bescheinigung einholen",
            "BAFA-Antrag VOR Maßnahmenbeginn stellen",
            "Fachunternehmen beauftragen (Qualifikationsnachweis)",
            "KfW-Antrag über Hausbank stellen",
            "Landesförderung separat beantragen",
            "Rechnungen und Nachweise sammeln",
            "Verwendungsnachweis einreichen"
        ]
    }


# ============================================================================
# FEATURE 10: CO2-DASHBOARD LIVE
# ============================================================================

def calculate_co2_footprint(
    building_data: dict[str, Any],
    current_system: str = "gas",
    future_system: str = "heatpump"
) -> dict[str, Any]:
    """
    Berechnet CO2-Bilanz über 20 Jahre mit Stromgrid-Entwicklung
    
    Args:
        building_data: Gebäudedaten
        current_system: "gas", "oil", "district_heating"
        future_system: "heatpump", "heatpump_pv"
    
    Returns:
        CO2-Vergleich mit Preisentwicklung
    """
    
    # CO2-Emissionsfaktoren (kg CO2/kWh)
    emission_factors_2024 = {
        "gas": 0.201,
        "oil": 0.266,
        "district_heating": 0.150,
        "electricity_grid": 0.420,  # Deutschland 2024
        "electricity_pv": 0.040      # Eigene PV-Anlage (Herstellung)
    }
    
    # Grid-Entwicklung (Stromgrid wird grüner)
    # Ziel: 80% Erneuerbare bis 2030, nahezu CO2-neutral bis 2045
    def grid_emission_factor(year: int) -> float:
        """CO2-Faktor des Stromgrid für Jahr"""
        years_passed = year - 2024
        # Linear von 0.420 (2024) auf 0.050 (2045)
        return max(0.050, 0.420 - (years_passed * 0.0176))
    
    heat_load_kw = building_data.get("heat_load_kw", 10)
    annual_heat_kwh = heat_load_kw * 1800
    
    # CO2-Preis (EUR/Tonne CO2)
    co2_price_2024 = 45  # EUR/t CO2
    co2_price_increase = 0.10  # 10% jährlich
    
    results_by_year = []
    
    for year_offset in range(21):  # 2024 bis 2044
        year = 2024 + year_offset
        
        # Aktuelles System (Gas/Öl)
        current_emissions_kwh = emission_factors_2024.get(current_system, 0.201)
        current_co2_kg = annual_heat_kwh * current_emissions_kwh
        current_co2_t = current_co2_kg / 1000
        
        # Zukünftiges System (Wärmepumpe)
        if future_system == "heatpump":
            cop = building_data.get("cop", 3.5)
            if cop != 0:
                electricity_kwh = annual_heat_kwh / cop
            else:
                electricity_kwh = 0.0
            grid_factor = grid_emission_factor(year)
            future_co2_kg = electricity_kwh * grid_factor
        elif future_system == "heatpump_pv":
            cop = building_data.get("cop", 3.5)
            if cop != 0:
                electricity_kwh = annual_heat_kwh / cop
            else:
                electricity_kwh = 0.0
            pv_coverage = 0.60  # 60% durch PV gedeckt
            grid_kwh = electricity_kwh * (1 - pv_coverage)
            pv_kwh = electricity_kwh * pv_coverage
            grid_factor = grid_emission_factor(year)
            future_co2_kg = (grid_kwh * grid_factor) + (pv_kwh * emission_factors_2024["electricity_pv"])
        else:
            future_co2_kg = 0
        
        future_co2_t = future_co2_kg / 1000
        
        # CO2-Einsparung
        co2_savings_t = current_co2_t - future_co2_t
        
        # CO2-Preis-Entwicklung
        co2_price = co2_price_2024 * ((1 + co2_price_increase) ** year_offset)
        co2_cost_current = current_co2_t * co2_price
        co2_cost_future = future_co2_t * co2_price
        co2_cost_savings = co2_cost_current - co2_cost_future
        
        results_by_year.append({
            "year": year,
            "current_co2_t": round(current_co2_t, 2),
            "future_co2_t": round(future_co2_t, 2),
            "savings_co2_t": round(co2_savings_t, 2),
            "grid_emission_factor": round(grid_emission_factor(year), 3) if "heatpump" in future_system else 0,
            "co2_price_eur_t": round(co2_price, 2),
            "co2_cost_current_eur": round(co2_cost_current, 2),
            "co2_cost_future_eur": round(co2_cost_future, 2),
            "co2_cost_savings_eur": round(co2_cost_savings, 2)
        })
    
    # Gesamt-Zusammenfassung
    total_co2_savings_t = sum(r["savings_co2_t"] for r in results_by_year)
    total_co2_cost_savings = sum(r["co2_cost_savings_eur"] for r in results_by_year)
    
    return {
        "yearly_data": results_by_year,
        "summary_20_years": {
            "total_co2_savings_t": round(total_co2_savings_t, 1),
            "total_co2_cost_savings_eur": round(total_co2_cost_savings, 2),
            "avg_annual_savings_t": round(total_co2_savings_t / 20, 2),
            "equivalent_trees_planted": round(total_co2_savings_t * 50, 0),  # 1 Tonne CO2 = ~50 Bäume
            "equivalent_car_km": round(total_co2_savings_t * 5000, 0)  # 1 Tonne CO2 = ~5000 km PKW
        },
        "current_system": current_system,
        "future_system": future_system,
        "base_year": 2024
    }


# ============================================================================
# FEATURE 11: ROI-CALCULATOR MONTE-CARLO
# ============================================================================

def monte_carlo_roi_analysis(
    building_data: dict[str, Any],
    investment_eur: float,
    simulations: int = 10000
) -> dict[str, Any]:
    """
    Probabilistische ROI-Analyse mit Monte-Carlo-Simulation
    
    Args:
        building_data: Gebäudedaten
        investment_eur: Investitionssumme
        simulations: Anzahl Simulationen
    
    Returns:
        Wahrscheinlichkeits-Verteilung der ROI-Werte
    """
    
    heat_load_kw = building_data.get("heat_load_kw", 10)
    cop_nominal = building_data.get("cop", 3.5)
    annual_heat_kwh_nominal = heat_load_kw * 1800
    
    # Unsicherheits-Parameter (Standardabweichungen)
    uncertainties = {
        "electricity_price": {"mean": 0.32, "std": 0.08},      # EUR/kWh
        "gas_price": {"mean": 0.10, "std": 0.03},              # EUR/kWh
        "cop_variation": {"mean": cop_nominal, "std": 0.5},    # COP-Schwankung
        "heat_demand_variation": {"mean": 1.0, "std": 0.15},   # Heizlast-Unsicherheit
        "maintenance_cost": {"mean": 250, "std": 100},         # EUR/Jahr
        "lifespan": {"mean": 20, "std": 3}                     # Jahre
    }
    
    simulation_results = []
    
    for _ in range(simulations):
        # Zufällige Werte aus Normalverteilungen
        electricity_price = max(0.15, random.gauss(
            uncertainties["electricity_price"]["mean"],
            uncertainties["electricity_price"]["std"]
        ))
        
        gas_price = max(0.05, random.gauss(
            uncertainties["gas_price"]["mean"],
            uncertainties["gas_price"]["std"]
        ))
        
        cop_real = max(2.0, random.gauss(
            uncertainties["cop_variation"]["mean"],
            uncertainties["cop_variation"]["std"]
        ))
        
        heat_demand_factor = max(0.5, random.gauss(
            uncertainties["heat_demand_variation"]["mean"],
            uncertainties["heat_demand_variation"]["std"]
        ))
        
        maintenance = max(0, random.gauss(
            uncertainties["maintenance_cost"]["mean"],
            uncertainties["maintenance_cost"]["std"]
        ))
        
        lifespan = max(10, int(random.gauss(
            uncertainties["lifespan"]["mean"],
            uncertainties["lifespan"]["std"]
        )))
        
        # Jährliche Kosten berechnen
        annual_heat_kwh = annual_heat_kwh_nominal * heat_demand_factor
        
        # Mit Gas (Baseline)
        gas_cost_annual = annual_heat_kwh * gas_price
        
        # Mit Wärmepumpe
        if cop_real != 0:
            electricity_kwh = annual_heat_kwh / cop_real
        else:
            electricity_kwh = 0.0
        wp_cost_annual = electricity_kwh * electricity_price + maintenance
        
        # Jährliche Einsparung
        annual_savings = gas_cost_annual - wp_cost_annual
        
        # Amortisationszeit
        if annual_savings > 0:
            if annual_savings != 0:
                payback_years = investment_eur / annual_savings
            else:
                payback_years = 0.0
        else:
            payback_years = 999
        
        # Nettobarwert (NPV) über Lebensdauer
        discount_rate = 0.03  # 3% Diskontierung
        npv = -investment_eur
        for year in range(1, lifespan + 1):
            npv += annual_savings / ((1 + discount_rate) ** year)
        
        # ROI über Lebensdauer
        total_savings = annual_savings * lifespan
        roi_percent = ((total_savings - investment_eur) / investment_eur) * 100
        
        simulation_results.append({
            "payback_years": payback_years,
            "npv": npv,
            "roi_percent": roi_percent,
            "annual_savings": annual_savings,
            "cop": cop_real,
            "electricity_price": electricity_price,
            "lifespan": lifespan
        })
    
    # Statistik-Auswertung
    payback_values = [r["payback_years"] for r in simulation_results if r["payback_years"] < 50]
    npv_values = [r["npv"] for r in simulation_results]
    roi_values = [r["roi_percent"] for r in simulation_results]
    
    def percentile(data: list[float], p: float) -> float:
        """Berechnet p-Perzentil"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    return {
        "simulations": simulations,
        "payback_statistics": {
            "mean_years": round(sum(payback_values) / len(payback_values), 1),
            "median_years": round(percentile(payback_values, 0.5), 1),
            "p10_years": round(percentile(payback_values, 0.1), 1),  # Best case (10%)
            "p90_years": round(percentile(payback_values, 0.9), 1),  # Worst case (90%)
            "probability_under_15_years": round(len([p for p in payback_values if p < 15]) / len(payback_values) * 100, 1)
        },
        "npv_statistics": {
            "mean_eur": round(sum(npv_values) / len(npv_values), 0),
            "median_eur": round(percentile(npv_values, 0.5), 0),
            "p10_eur": round(percentile(npv_values, 0.1), 0),
            "p90_eur": round(percentile(npv_values, 0.9), 0),
            "probability_positive": round(len([n for n in npv_values if n > 0]) / len(npv_values) * 100, 1)
        },
        "roi_statistics": {
            "mean_percent": round(sum(roi_values) / len(roi_values), 1),
            "median_percent": round(percentile(roi_values, 0.5), 1),
            "p10_percent": round(percentile(roi_values, 0.1), 1),
            "p90_percent": round(percentile(roi_values, 0.9), 1)
        },
        "raw_results": simulation_results[:100],  # Erste 100 für Visualisierung
        "uncertainties": uncertainties
    }


# ============================================================================
# FEATURE 12: BENCHMARKING-TOOL
# ============================================================================

def benchmark_building(
    building_data: dict[str, Any],
    region: str = "Germany"
) -> dict[str, Any]:
    """
    Vergleicht Gebäude mit ähnlichen Referenzgebäuden
    
    Args:
        building_data: Eigenes Gebäude
        region: Region für Vergleich
    
    Returns:
        Ranking und Best-Practice-Empfehlungen
    """
    
    # Eigenes Gebäude
    own_building = {
        "living_area_m2": building_data.get("living_area_m2", 150),
        "year_built": building_data.get("year_built", 1980),
        "heat_load_kw": building_data.get("heat_load_kw", 10),
        "heating_system": building_data.get("heating_system", "gas")
    }
    
    # Spezifischer Verbrauch (kWh/m²/Jahr)
    own_specific_consumption = (own_building["heat_load_kw"] * 1800) / own_building["living_area_m2"]
    
    # Referenzgebäude (synthetische Daten für Vergleich)
    reference_buildings = [
        {"id": 1, "area": 145, "year": 1975, "consumption_kwh_m2": 180, "system": "gas", "insulated": False},
        {"id": 2, "area": 160, "year": 1985, "consumption_kwh_m2": 140, "system": "gas", "insulated": True},
        {"id": 3, "area": 150, "year": 1990, "consumption_kwh_m2": 120, "system": "oil", "insulated": True},
        {"id": 4, "area": 155, "year": 1980, "consumption_kwh_m2": 95, "system": "heatpump", "insulated": True},
        {"id": 5, "area": 140, "year": 1978, "consumption_kwh_m2": 70, "system": "heatpump", "insulated": True},
        {"id": 6, "area": 165, "year": 2000, "consumption_kwh_m2": 85, "system": "district_heating", "insulated": True},
        {"id": 7, "area": 148, "year": 1982, "consumption_kwh_m2": 160, "system": "gas", "insulated": False},
        {"id": 8, "area": 152, "year": 1988, "consumption_kwh_m2": 75, "system": "heatpump", "insulated": True},
        {"id": 9, "area": 158, "year": 1979, "consumption_kwh_m2": 110, "system": "gas", "insulated": True},
        {"id": 10, "area": 143, "year": 1984, "consumption_kwh_m2": 130, "system": "oil", "insulated": False}
    ]
    
    # Filtere ähnliche Gebäude (±15 Jahre, ±30 m²)
    similar_buildings = [
        b for b in reference_buildings
        if abs(b["year"] - own_building["year_built"]) <= 15
        and abs(b["area"] - own_building["living_area_m2"]) <= 30
    ]
    
    # Ranking erstellen
    all_consumptions = [b["consumption_kwh_m2"] for b in similar_buildings] + [own_specific_consumption]
    sorted_consumptions = sorted(all_consumptions)
    own_rank = sorted_consumptions.index(own_specific_consumption) + 1
    total_buildings = len(sorted_consumptions)
    if total_buildings != 0:
        percentile_rank = (own_rank / total_buildings) * 100
    else:
        percentile_rank = 0.0
    
    # Best Performer identifizieren
    best_performer = min(similar_buildings, key=lambda x: x["consumption_kwh_m2"])
    potential_savings = own_specific_consumption - best_performer["consumption_kwh_m2"]
    
    # Empfehlungen ableiten
    recommendations = []
    
    if potential_savings > 50:
        recommendations.append({
            "priority": "high",
            "measure": "Umfassende energetische Sanierung",
            "potential_savings_kwh_m2": round(potential_savings * 0.6, 0),
            "investment_eur": own_building["living_area_m2"] * 300
        })
    
    if own_building["heating_system"] != "heatpump" and best_performer["system"] == "heatpump":
        recommendations.append({
            "priority": "high",
            "measure": "Wechsel zu Wärmepumpe",
            "potential_savings_kwh_m2": round(potential_savings * 0.4, 0),
            "investment_eur": own_building["heat_load_kw"] * 1400
        })
    
    if potential_savings > 30:
        recommendations.append({
            "priority": "medium",
            "measure": "Dämmung optimieren",
            "potential_savings_kwh_m2": round(potential_savings * 0.5, 0),
            "investment_eur": own_building["living_area_m2"] * 200
        })
    
    # Durchschnittswerte berechnen
    avg_consumption = sum(b["consumption_kwh_m2"] for b in similar_buildings) / len(similar_buildings)
    
    return {
        "own_building": {
            "specific_consumption_kwh_m2": round(own_specific_consumption, 1),
            "total_consumption_kwh": round(own_specific_consumption * own_building["living_area_m2"], 0),
            "living_area_m2": own_building["living_area_m2"],
            "year_built": own_building["year_built"]
        },
        "ranking": {
            "rank": own_rank,
            "total_buildings": total_buildings,
            "percentile": round(percentile_rank, 1),
            "interpretation": "Top 25%" if percentile_rank <= 25 else "Überdurchschnittlich" if percentile_rank <= 50 else "Unterdurchschnittlich" if percentile_rank <= 75 else "Bottom 25%"
        },
        "comparison": {
            "similar_buildings_count": len(similar_buildings),
            "avg_consumption_kwh_m2": round(avg_consumption, 1),
            "best_consumption_kwh_m2": best_performer["consumption_kwh_m2"],
            "worst_consumption_kwh_m2": max(b["consumption_kwh_m2"] for b in similar_buildings),
            "difference_to_avg_kwh_m2": round(own_specific_consumption - avg_consumption, 1),
            "difference_to_best_kwh_m2": round(potential_savings, 1)
        },
        "best_performer": {
            "id": best_performer["id"],
            "consumption_kwh_m2": best_performer["consumption_kwh_m2"],
            "system": best_performer["system"],
            "insulated": best_performer["insulated"],
            "year": best_performer["year"]
        },
        "recommendations": recommendations,
        "potential_annual_savings_eur": round(potential_savings * own_building["living_area_m2"] * 0.10, 2),
        "region": region
    }
