"""
PV-Berechnungsalgorithmen - Kernmodul
===================================

Umfassende Sammlung von PV-Berechnungsfunktionen für:
- Grundberechnungen (Ertrag, Eigenverbrauch, Autarkie)
- Wirtschaftlichkeit (ROI, NPV, Amortisation)
- Technische Analysen (Degradation, Verschattung, Temperatur)
- Speicherberechnungen und Optimierungen
- Umwelt/Nachhaltigkeit
- Finanzierung/Steuern/Förderungen

Portiert aus kalkulationen.py mit Sicherheits- und Performance-Optimierungen.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import numpy_financial as npf

# Konstanten
LIFESPAN_YEARS = 25
DISCOUNT_RATE = 0.04
CO2_EMISSIONS_GRID_KWH = 0.474  # kg CO2 pro kWh
CO2_EMBODIED_PV_KWP = 1000 * 0.05  # kg CO2 pro kWp (50g/Wp)


def safe_float(value: Any, default: float = 0.0) -> float:
    """Sichere Konvertierung zu float mit Fallback."""
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (ValueError, TypeError):
        return default


def safe_divide(
        numerator: float,
        denominator: float,
        default: float = 0.0) -> float:
    """Sichere Division mit Fallback bei Division durch Null."""
    if denominator == 0:
        return float('inf') if numerator != 0 else default
    return numerator / denominator


# =============================================================================
# GRUNDBERECHNUNGEN
# =============================================================================

def calculate_annual_energy_yield(pv_peak_power_kwp: float,
                                  specific_yield_kwh_per_kwp: float) -> float:
    """
    Jahresenergieertrag in kWh pro Jahr.

    Args:
        pv_peak_power_kwp: Installierte PV-Leistung in kWp
        specific_yield_kwh_per_kwp: Spezifischer Ertrag in kWh/kWp

    Returns:
        Jährlicher Energieertrag in kWh
    """
    pv_power = safe_float(pv_peak_power_kwp)
    specific = safe_float(
        specific_yield_kwh_per_kwp,
        950.0)  # Default: 950 kWh/kWp
    return pv_power * specific


def calculate_self_consumption_quote(self_consumed_kwh: float,
                                     total_generation_kwh: float) -> float:
    """
    Eigenverbrauchsquote in %.

    Args:
        self_consumed_kwh: Selbst verbrauchter PV-Strom
        total_generation_kwh: Gesamte PV-Erzeugung

    Returns:
        Eigenverbrauchsquote in Prozent
    """
    self_consumed = safe_float(self_consumed_kwh)
    total_gen = safe_float(total_generation_kwh)

    if total_gen == 0:
        return 0.0
    return (self_consumed / total_gen) * 100


def calculate_autarky_degree(self_consumed_kwh: float,
                             total_consumption_kwh: float) -> float:
    """
    Autarkiegrad in %.

    Args:
        self_consumed_kwh: Selbst verbrauchter PV-Strom
        total_consumption_kwh: Gesamter Stromverbrauch

    Returns:
        Autarkiegrad in Prozent
    """
    self_consumed = safe_float(self_consumed_kwh)
    total_cons = safe_float(total_consumption_kwh)

    if total_cons == 0:
        return 0.0
    return min(100.0, (self_consumed / total_cons) * 100)


def calculate_specific_yield(annual_yield_kwh: float,
                             pv_peak_power_kwp: float) -> float:
    """
    Spezifischer Ertrag in kWh/kWp.

    Args:
        annual_yield_kwh: Jahresertrag in kWh
        pv_peak_power_kwp: Installierte Leistung in kWp

    Returns:
        Spezifischer Ertrag in kWh/kWp
    """
    annual_yield = safe_float(annual_yield_kwh)
    pv_power = safe_float(pv_peak_power_kwp)

    return safe_divide(annual_yield, pv_power, 0.0)


def calculate_performance_ratio(actual_yield_kwh: float,
                                global_radiation_kwh_per_m2: float,
                                pv_area_m2: float) -> float:
    """
    Performance Ratio der PV-Anlage.

    Args:
        actual_yield_kwh: Tatsächlicher Ertrag
        global_radiation_kwh_per_m2: Globalstrahlung
        pv_area_m2: PV-Modulfläche

    Returns:
        Performance Ratio (0-1)
    """
    actual_yield = safe_float(actual_yield_kwh)
    radiation = safe_float(global_radiation_kwh_per_m2, 1000.0)
    area = safe_float(pv_area_m2, 1.0)

    theoretical_yield = radiation * area
    return safe_divide(actual_yield, theoretical_yield, 0.0)


# =============================================================================
# WIRTSCHAFTLICHKEITSBERECHNUNGEN
# =============================================================================

def calculate_payback_period(investment_costs: float,
                             annual_savings: float) -> float:
    """
    Amortisationszeit in Jahren.

    Args:
        investment_costs: Investitionskosten
        annual_savings: Jährliche Einsparungen

    Returns:
        Amortisationszeit in Jahren
    """
    investment = safe_float(investment_costs)
    savings = safe_float(annual_savings)

    return safe_divide(investment, savings, float('inf'))


def calculate_annual_cost_savings(self_consumed_kwh: float,
                                  electricity_price: float) -> float:
    """
    Jährliche Stromkostenersparnis in €.

    Args:
        self_consumed_kwh: Selbst verbrauchter PV-Strom
        electricity_price: Strompreis in €/kWh

    Returns:
        Jährliche Ersparnis in €
    """
    self_consumed = safe_float(self_consumed_kwh)
    price = safe_float(electricity_price, 0.30)  # Default: 30 ct/kWh

    return self_consumed * price


def calculate_feed_in_tariff_revenue(feed_in_kwh: float,
                                     feed_in_rate_eur: float) -> float:
    """
    Jährliche Einspeisevergütung in €.

    Args:
        feed_in_kwh: Eingespeiste Energiemenge
        feed_in_rate_eur: Vergütungssatz in €/kWh

    Returns:
        Jährliche Einspeisevergütung in €
    """
    feed_in = safe_float(feed_in_kwh)
    rate = safe_float(feed_in_rate_eur, 0.08)  # Default: 8 ct/kWh

    return feed_in * rate


def calculate_net_present_value(investment: float,
                                annual_savings: float,
                                years: int = LIFESPAN_YEARS,
                                discount_rate: float = DISCOUNT_RATE) -> float:
    """
    Kapitalwert (NPV) der PV-Investition.

    Args:
        investment: Anfangsinvestition
        annual_savings: Jährliche Einsparungen
        years: Betrachtungszeitraum
        discount_rate: Kalkulationszinssatz

    Returns:
        Nettobarwert (NPV)
    """
    investment_val = safe_float(investment)
    savings = safe_float(annual_savings)
    period = max(1, int(years))
    rate = safe_float(discount_rate, DISCOUNT_RATE)

    cash_flows = [savings] * period
    return npf.npv(rate, cash_flows) - investment_val


def calculate_irr(investment: float,
                  annual_savings: float,
                  years: int = LIFESPAN_YEARS) -> float:
    """
    Interner Zinsfuß (IRR) in %.

    Args:
        investment: Anfangsinvestition
        annual_savings: Jährliche Einsparungen
        years: Betrachtungszeitraum

    Returns:
        IRR in Prozent
    """
    investment_val = safe_float(investment)
    savings = safe_float(annual_savings)
    period = max(1, int(years))

    if investment_val <= 0 or savings <= 0:
        return 0.0

    cash_flows = [-investment_val] + [savings] * period

    try:
        irr_result = npf.irr(cash_flows)
        return safe_float(irr_result * 100, 0.0)
    except BaseException:
        return 0.0


def calculate_total_roi(investment: float,
                        annual_savings: float,
                        years: int = LIFESPAN_YEARS) -> float:
    """
    Gesamtrendite über Lebensdauer in %.

    Args:
        investment: Anfangsinvestition
        annual_savings: Jährliche Einsparungen
        years: Betrachtungszeitraum

    Returns:
        ROI in Prozent
    """
    investment_val = safe_float(investment)
    savings = safe_float(annual_savings)
    period = max(1, int(years))

    if investment_val <= 0:
        return 0.0

    total_profit = (savings * period) - investment_val
    return (total_profit / investment_val) * 100


# =============================================================================
# SPEICHERBERECHNUNGEN
# =============================================================================

def calculate_storage_coverage_degree(
        stored_self_consumption_kwh: float,
        total_self_consumption_kwh: float) -> float:
    """
    Speicherdeckungsgrad in %.

    Args:
        stored_self_consumption_kwh: Aus Speicher genutzter Eigenverbrauch
        total_self_consumption_kwh: Gesamter Eigenverbrauch

    Returns:
        Speicherdeckungsgrad in Prozent
    """
    stored = safe_float(stored_self_consumption_kwh)
    total = safe_float(total_self_consumption_kwh)

    return safe_divide(stored * 100, total, 0.0)


def calculate_optimal_storage_size(daily_consumption_kwh: float,
                                   losses_percent: float = 10.0) -> float:
    """
    Optimale Batteriespeichergröße in kWh.

    Args:
        daily_consumption_kwh: Täglicher Verbrauch
        losses_percent: Verluste in Prozent

    Returns:
        Empfohlene Speicherkapazität in kWh
    """
    daily_cons = safe_float(daily_consumption_kwh)
    losses = safe_float(losses_percent, 10.0)
    losses = max(0.0, min(50.0, losses))  # Begrenze auf 0-50%

    return daily_cons * (1 - losses / 100)


def calculate_emergency_power_capacity(
        storage_kwh: float,
        usable_capacity_percent: float = 80.0) -> float:
    """
    Notstromkapazität in kWh/Tag.

    Args:
        storage_kwh: Speicherkapazität
        usable_capacity_percent: Nutzbare Kapazität in Prozent

    Returns:
        Notstromkapazität in kWh/Tag
    """
    storage = safe_float(storage_kwh)
    usable = safe_float(usable_capacity_percent, 80.0)
    usable = max(0.0, min(100.0, usable))  # Begrenze auf 0-100%

    return storage * (usable / 100)


# =============================================================================
# UMWELT- UND NACHHALTIGKEITSBERECHNUNGEN
# =============================================================================

def calculate_co2_savings(
        annual_yield_kwh: float,
        co2_factor_kg_per_kwh: float = CO2_EMISSIONS_GRID_KWH) -> float:
    """
    Jährliche CO2-Einsparung in kg.

    Args:
        annual_yield_kwh: Jährlicher PV-Ertrag
        co2_factor_kg_per_kwh: CO2-Faktor Strommix

    Returns:
        CO2-Einsparung in kg/Jahr
    """
    annual_yield = safe_float(annual_yield_kwh)
    co2_factor = safe_float(co2_factor_kg_per_kwh, CO2_EMISSIONS_GRID_KWH)

    return annual_yield * co2_factor


def calculate_co2_payback_time(pv_size_kwp: float,
                               annual_production_kwh: float) -> float:
    """
    CO2-Amortisationszeit in Jahren.

    Args:
        pv_size_kwp: PV-Anlagengröße in kWp
        annual_production_kwh: Jährliche Produktion

    Returns:
        CO2-Amortisationszeit in Jahren
    """
    pv_size = safe_float(pv_size_kwp)
    annual_prod = safe_float(annual_production_kwh)

    total_embodied_co2 = pv_size * CO2_EMBODIED_PV_KWP
    annual_co2_savings = annual_prod * CO2_EMISSIONS_GRID_KWH

    return safe_divide(total_embodied_co2, annual_co2_savings, float('inf'))


# =============================================================================
# TECHNISCHE ANALYSEN
# =============================================================================

def calculate_pv_module_efficiency(module_power_wp: float,
                                   module_area_m2: float) -> float:
    """
    PV-Modulwirkungsgrad in %.

    Args:
        module_power_wp: Modulleistung in Wp
        module_area_m2: Modulfläche in m²

    Returns:
        Modulwirkungsgrad in Prozent
    """
    power = safe_float(module_power_wp)
    area = safe_float(module_area_m2, 1.0)

    if area == 0:
        return 0.0

    # 1000 W/m² Einstrahlung unter STC
    efficiency = (power / (area * 1000)) * 100
    return max(0.0, min(100.0, efficiency))  # Begrenze auf 0-100%


def calculate_dc_ac_oversizing_factor(pv_power_kwp: float,
                                      inverter_power_kw: float) -> float:
    """
    DC/AC-Überdimensionierungsfaktor.

    Args:
        pv_power_kwp: PV-Leistung in kWp
        inverter_power_kw: Wechselrichterleistung in kW

    Returns:
        Überdimensionierungsfaktor
    """
    pv_power = safe_float(pv_power_kwp)
    inv_power = safe_float(inverter_power_kw)

    return safe_divide(pv_power, inv_power, float('inf'))


# =============================================================================
# FINANZIERUNGSBERECHNUNGEN
# =============================================================================

def calculate_annuity(principal: float,
                      annual_interest_rate: float,
                      duration_years: int) -> dict[str, Any]:
    """
    Annuitätendarlehen-Berechnung.

    Args:
        principal: Darlehensbetrag
        annual_interest_rate: Jahreszins in Prozent
        duration_years: Laufzeit in Jahren

    Returns:
        Dict mit Kreditdetails
    """
    principal_val = safe_float(principal)
    interest_rate = safe_float(annual_interest_rate)
    duration = max(1, int(duration_years))

    if principal_val <= 0:
        return {"error": "Ungültiger Darlehensbetrag"}

    monthly_rate = interest_rate / 100 / 12
    num_payments = duration * 12

    if monthly_rate == 0:  # Zinsfrei
        monthly_payment = principal_val / num_payments
        total_interest = 0
    else:
        # Annuitätenformel
        q = 1 + monthly_rate
        monthly_payment = principal_val * \
            (monthly_rate * q**num_payments) / (q**num_payments - 1)
        total_interest = (monthly_payment * num_payments) - principal_val

    return {
        "monatliche_rate": round(monthly_payment, 2),
        "gesamtzinsen": round(total_interest, 2),
        "gesamtkosten": round(principal_val + total_interest, 2),
        "effective_rate": round(interest_rate, 2),
        "laufzeit_monate": int(num_payments)
    }


def calculate_leasing_costs(total_investment: float,
                            leasing_factor: float,
                            duration_months: int,
                            residual_value_percent: float = 1.0) -> dict[str, Any]:
    """
    Leasingkostenberechnung.

    Args:
        total_investment: Gesamtinvestition
        leasing_factor: Leasingfaktor in % pro Monat
        duration_months: Laufzeit in Monaten
        residual_value_percent: Restwert in %

    Returns:
        Dict mit Leasingdetails
    """
    investment = safe_float(total_investment)
    factor = safe_float(leasing_factor)
    duration = max(1, int(duration_months))
    residual = safe_float(residual_value_percent, 1.0)

    if investment <= 0 or factor <= 0:
        return {"error": "Ungültige Parameter"}

    monthly_rate = investment * (factor / 100)
    total_costs = monthly_rate * duration
    residual_value = investment * (residual / 100)
    effective_costs = total_costs - residual_value

    return {
        "monatliche_rate": round(monthly_rate, 2),
        "gesamtkosten": round(total_costs, 2),
        "restwert": round(residual_value, 2),
        "effektive_kosten": round(effective_costs, 2),
        "kostenvorteil_vs_kauf": round(investment - effective_costs, 2)
    }


# =============================================================================
# ERWEITERTE BERECHNUNGSFUNKTIONEN
# =============================================================================

class PVCalculationsAdvanced:
    """
    Erweiterte PV-Berechnungsklasse mit komplexen Analysen.
    """

    def __init__(self):
        self.years = LIFESPAN_YEARS
        self.discount_rate = DISCOUNT_RATE

    def calculate_detailed_co2_analysis(
            self, calc_results: dict[str, Any]) -> dict[str, Any]:
        """
        Detaillierte CO2-Bilanz über die Lebensdauer.

        Args:
            calc_results: Berechnungsergebnisse

        Returns:
            Dict mit detaillierter CO2-Bilanz
        """
        annual_production = safe_float(
            calc_results.get(
                "annual_pv_production_kwh", 10000))
        system_kwp = safe_float(calc_results.get("anlage_kwp", 10))

        # Jährliche CO2-Einsparung
        annual_co2_savings = calculate_co2_savings(annual_production)
        annual_co2_savings_tons = annual_co2_savings / 1000  # Tonnen

        # Kumulierte Einsparung über Jahre
        years_list = list(range(1, self.years + 1))
        cumulative_savings = [
            annual_co2_savings_tons *
            year for year in years_list]

        # Produktionsemissionen
        production_emissions = system_kwp * CO2_EMBODIED_PV_KWP / 1000  # Tonnen

        # CO2-Amortisationszeit
        carbon_payback_time = calculate_co2_payback_time(
            system_kwp, annual_production)

        # Gesamte Netto-CO2-Einsparung
        total_co2_savings = annual_co2_savings_tons * self.years - production_emissions

        # Äquivalente berechnen
        tree_equivalent = total_co2_savings * 47  # ~22 kg CO2/Jahr pro Baum
        car_km_equivalent = total_co2_savings * 1000 / 0.12  # 120g/km

        # Weitere Umweltaspekte
        primary_energy_saved = annual_production * self.years * 2.8  # kWh Primärenergie
        water_saved = annual_production * self.years * 1.2  # Liter Wasser

        return {
            "annual_co2_savings_tons": round(annual_co2_savings_tons, 2),
            "cumulative_savings": [round(x, 2) for x in cumulative_savings],
            "production_emissions": round(production_emissions, 2),
            "carbon_payback_time": round(carbon_payback_time, 1),
            "total_co2_savings": round(total_co2_savings, 2),
            "tree_equivalent": round(tree_equivalent, 0),
            "car_km_equivalent": round(car_km_equivalent, 0),
            "primary_energy_saved": round(primary_energy_saved, 0),
            "water_saved": round(water_saved, 0),
            "years": years_list
        }

    def run_monte_carlo_simulation(self,
                                   calc_results: dict[str,
                                                      Any],
                                   n_simulations: int = 1000,
                                   confidence_level: int = 95) -> dict[str,
                                                                       Any]:
        """
        Monte-Carlo-Simulation für Risikobewertung.

        Args:
            calc_results: Berechnungsergebnisse
            n_simulations: Anzahl Simulationen
            confidence_level: Konfidenzlevel in %

        Returns:
            Dict mit Simulationsergebnissen
        """
        base_investment = safe_float(
            calc_results.get(
                "total_investment_netto", 20000))
        base_annual_benefit = safe_float(
            calc_results.get(
                "annual_financial_benefit_year1", 1500))

        # Validierung
        if base_investment <= 0 or base_annual_benefit <= 0:
            return {"error": "Ungültige Basisdaten für Simulation"}

        np.random.seed(42)  # Für reproduzierbare Ergebnisse
        npv_distribution = []

        for _ in range(n_simulations):
            # Parameter variieren (normalverteilt)
            investment = max(
                0,
                np.random.normal(
                    base_investment,
                    base_investment *
                    0.1))
            annual_benefit = max(
                0,
                np.random.normal(
                    base_annual_benefit,
                    base_annual_benefit *
                    0.15))
            discount_rate = max(0, np.random.normal(0.04, 0.01))

            # NPV berechnen
            npv = -investment
            for year in range(1, self.years + 1):
                npv += annual_benefit / (1 + discount_rate) ** year

            npv_distribution.append(npv)

        npv_array = np.array(npv_distribution)

        # Statistiken berechnen
        npv_mean = np.mean(npv_array)
        npv_std = np.std(npv_array)

        # Konfidenzintervall
        alpha = (100 - confidence_level) / 2
        npv_lower = np.percentile(npv_array, alpha)
        npv_upper = np.percentile(npv_array, 100 - alpha)

        # Value at Risk (5% Quantil)
        var_5 = np.percentile(npv_array, 5)

        # Erfolgswahrscheinlichkeit (NPV > 0)
        success_prob = (npv_array > 0).sum() / n_simulations * 100

        return {
            "npv_mean": round(npv_mean, 2),
            "npv_std": round(npv_std, 2),
            "npv_lower_bound": round(npv_lower, 2),
            "npv_upper_bound": round(npv_upper, 2),
            "var_5": round(var_5, 2),
            "success_probability": round(success_prob, 1),
            "simulations_count": n_simulations,
            "confidence_level": confidence_level
        }

    def generate_optimization_suggestions(self,
                                          calc_results: dict[str,
                                                             Any],
                                          project_data: dict[str,
                                                             Any] = None) -> dict[str,
                                                                                  Any]:
        """
        Optimierungsvorschläge für die PV-Anlage.

        Args:
            calc_results: Berechnungsergebnisse
            project_data: Projektdaten (optional)

        Returns:
            Dict mit Optimierungsvorschlägen
        """
        if project_data is None:
            project_data = {}

        # Vorschläge mit Berechnungen
        optimization_potentials = [{"title": "Batteriespeicher erweitern",
                                    "description": "Vergrößerung des Batteriespeichers für höheren Eigenverbrauch",
                                    "category": "Speicher",
                                    "implementation_effort": 30,
                                    "benefit_potential": 400,
                                    "roi_improvement": 1.2,
                                    "cost_estimate": 3000,
                                    },
                                   {"title": "Leistungsoptimierer installieren",
                                    "description": "Leistungsoptimierer für verschattete Module",
                                    "category": "Technik",
                                    "implementation_effort": 50,
                                    "benefit_potential": 600,
                                    "roi_improvement": 2.1,
                                    "cost_estimate": 2000,
                                    },
                                   {"title": "Warmwasser-Integration",
                                    "description": "Elektrische Warmwasserbereitung für PV-Überschuss",
                                    "category": "Integration",
                                    "implementation_effort": 40,
                                    "benefit_potential": 300,
                                    "roi_improvement": 0.8,
                                    "cost_estimate": 1500,
                                    },
                                   {"title": "Smart Home System",
                                    "description": "Intelligente Laststeuerung für optimalen Verbrauch",
                                    "category": "Automatisierung",
                                    "implementation_effort": 60,
                                    "benefit_potential": 250,
                                    "roi_improvement": 0.6,
                                    "cost_estimate": 2500,
                                    },
                                   ]

        # Nach ROI-Verbesserung sortieren
        top_recommendations = sorted(optimization_potentials,
                                     key=lambda x: x["roi_improvement"],
                                     reverse=True)

        # Zusätzliche Details ergänzen
        for rec in top_recommendations:
            rec["annual_benefit"] = rec["benefit_potential"]
            rec["investment"] = rec["cost_estimate"]
            rec["payback"] = safe_divide(
                rec["investment"], rec["annual_benefit"], 99)
            rec["difficulty"] = (
                "Einfach" if rec["implementation_effort"] < 40 else
                "Mittel" if rec["implementation_effort"] < 60 else "Komplex"
            )

        # Systemoptimierung
        system_optimization = {
            "optimal_tilt": 30,  # Optimaler Neigungswinkel
            "optimal_azimuth": 0,  # Süd
            "optimal_battery_size": 8.0,  # kWh
            "optimal_dc_ac_ratio": 1.15,
        }

        return {
            "optimization_potentials": optimization_potentials,
            "top_recommendations": top_recommendations[:3],  # Top 3
            "system_optimization": system_optimization,
        }


# =============================================================================
# FACTORY FUNCTION FÜR VOLLSTÄNDIGE BERECHNUNG
# =============================================================================

def calculate_comprehensive_pv_analysis(
        project_data: dict[str, Any]) -> dict[str, Any]:
    """
    Umfassende PV-Analyse mit allen verfügbaren Berechnungen.

    Args:
        project_data: Vollständige Projektdaten

    Returns:
        Dict mit allen Berechnungsergebnissen
    """

    # Basis-Parameter extrahieren
    pv_power = safe_float(project_data.get("anlage_kwp", 10))
    annual_production = safe_float(
        project_data.get(
            "annual_pv_production_kwh",
            pv_power *
            950))  # Default: 950 kWh/kWp
    annual_consumption = safe_float(
        project_data.get(
            "annual_consumption_kwh", 4000))
    self_consumption = safe_float(
        project_data.get(
            "self_consumption_kwh", min(
                annual_production * 0.3, annual_consumption)))
    investment_costs = safe_float(
        project_data.get(
            "total_investment_netto",
            20000))
    electricity_price = safe_float(
        project_data.get(
            "electricity_price_eur_kwh", 0.30))
    feed_in_tariff = safe_float(
        project_data.get(
            "feed_in_tariff_eur_kwh", 0.08))

    # Grundberechnungen
    results = {
        "pv_power_kwp": pv_power,
        "annual_production_kwh": annual_production,
        "annual_consumption_kwh": annual_consumption,
        "self_consumption_kwh": self_consumption,
        "investment_costs_eur": investment_costs,
    }

    # Eigenverbrauch und Autarkie
    results["self_consumption_rate"] = calculate_self_consumption_quote(
        self_consumption, annual_production)
    results["autarky_degree"] = calculate_autarky_degree(
        self_consumption, annual_consumption)

    # Spezifischer Ertrag und Performance Ratio
    results["specific_yield"] = calculate_specific_yield(
        annual_production, pv_power)

    # Wirtschaftlichkeit
    feed_in_kwh = max(0, annual_production - self_consumption)
    annual_savings = (
        calculate_annual_cost_savings(
            self_consumption,
            electricity_price) +
        calculate_feed_in_tariff_revenue(
            feed_in_kwh,
            feed_in_tariff))

    results["annual_savings_eur"] = annual_savings
    results["feed_in_kwh"] = feed_in_kwh
    results["payback_period_years"] = calculate_payback_period(
        investment_costs, annual_savings)
    results["npv_eur"] = calculate_net_present_value(
        investment_costs, annual_savings)
    results["irr_percent"] = calculate_irr(investment_costs, annual_savings)
    results["total_roi_percent"] = calculate_total_roi(
        investment_costs, annual_savings)

    # Umwelt
    results["annual_co2_savings_kg"] = calculate_co2_savings(annual_production)
    results["co2_payback_years"] = calculate_co2_payback_time(
        pv_power, annual_production)

    # Erweiterte Analysen (wenn Advanced-Klasse verwendet wird)
    advanced = PVCalculationsAdvanced()
    results["detailed_co2_analysis"] = advanced.calculate_detailed_co2_analysis({
        "annual_pv_production_kwh": annual_production,
        "anlage_kwp": pv_power
    })

    # Monte Carlo nur bei ausreichenden Daten
    if annual_savings > 0 and investment_costs > 0:
        results["monte_carlo_analysis"] = advanced.run_monte_carlo_simulation({
            "total_investment_netto": investment_costs,
            "annual_financial_benefit_year1": annual_savings
        })

    # Optimierungsvorschläge
    results["optimization_suggestions"] = advanced.generate_optimization_suggestions({
        "anlage_kwp": pv_power,
        "annual_production_kwh": annual_production
    }, project_data)

    # Berechnungsstatus
    results["calculation_timestamp"] = str(np.datetime64('now'))
    results["calculation_status"] = "success"

    return results


# =============================================================================
# EXPORT/IMPORT COMPATIBILITY
# =============================================================================

# Alle Hauptfunktionen für einfachen Import
__all__ = [
    'calculate_annual_energy_yield',
    'calculate_self_consumption_quote',
    'calculate_autarky_degree',
    'calculate_specific_yield',
    'calculate_performance_ratio',
    'calculate_payback_period',
    'calculate_annual_cost_savings',
    'calculate_feed_in_tariff_revenue',
    'calculate_net_present_value',
    'calculate_irr',
    'calculate_total_roi',
    'calculate_storage_coverage_degree',
    'calculate_optimal_storage_size',
    'calculate_emergency_power_capacity',
    'calculate_co2_savings',
    'calculate_co2_payback_time',
    'calculate_pv_module_efficiency',
    'calculate_dc_ac_oversizing_factor',
    'calculate_annuity',
    'calculate_leasing_costs',
    'PVCalculationsAdvanced',
    'calculate_comprehensive_pv_analysis'
]
