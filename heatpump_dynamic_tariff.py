"""
Dynamische Stromtarif & Stromcloud Berechnungen für Wärmepumpen
Teil des Wärmepumpen-Moduls - Energiemanagement & Tarif-Optimierung

Author: GitHub Copilot
Version: 1.0
Date: 2025-11-03
"""

from typing import Any
import math
import random
from datetime import datetime, timedelta


# ============================================================================
# DYNAMISCHE STROMTARIF-BERECHNUNGEN
# ============================================================================

def get_tariff_zones() -> dict[str, dict[str, Any]]:
    """
    Definiert Tarifzonen für stündliche Preisberechnung
    
    Returns:
        Dict mit Zeitbereichen und Preisfaktoren
    """
    return {
        "night": {
            "hours": list(range(0, 6)),  # 0-6 Uhr
            "price_factor": 0.70,  # 30% günstiger
            "description": "Nachtstrom (sehr günstig)"
        },
        "morning_peak": {
            "hours": [6, 7, 8],  # 6-9 Uhr
            "price_factor": 1.25,  # 25% teurer
            "description": "Morgen-Spitze (teuer)"
        },
        "midday": {
            "hours": list(range(9, 12)),  # 9-12 Uhr
            "price_factor": 0.95,  # 5% günstiger
            "description": "Vormittag (moderat)"
        },
        "solar_peak": {
            "hours": list(range(12, 16)),  # 12-16 Uhr
            "price_factor": 0.60,  # 40% günstiger (viel Solar)
            "description": "Solar-Peak (sehr günstig)"
        },
        "afternoon": {
            "hours": list(range(16, 18)),  # 16-18 Uhr
            "price_factor": 1.05,  # 5% teurer
            "description": "Nachmittag (moderat)"
        },
        "evening_peak": {
            "hours": list(range(18, 22)),  # 18-22 Uhr
            "price_factor": 1.35,  # 35% teurer
            "description": "Abend-Spitze (sehr teuer)"
        },
        "late_night": {
            "hours": list(range(22, 24)),  # 22-24 Uhr
            "price_factor": 0.85,  # 15% günstiger
            "description": "Spätnacht (günstig)"
        }
    }


def calculate_hourly_electricity_costs(
    base_price_eur_kwh: float,
    annual_consumption_kwh: float,
    use_dynamic_tariff: bool = False
) -> dict[str, Any]:
    """
    Berechnet stündliche Stromkosten für statischen vs. dynamischen Tarif
    
    Args:
        base_price_eur_kwh: Basis-Arbeitspreis (statischer Tarif)
        annual_consumption_kwh: Jahresverbrauch in kWh
        use_dynamic_tariff: True für dynamische Preisberechnung
    
    Returns:
        Dict mit stündlichen Kosten und Zusammenfassung
    """
    
    tariff_zones = get_tariff_zones()
    
    # Gleichmäßige Verteilung des Verbrauchs über 24h
    hourly_consumption = annual_consumption_kwh / 8760
    
    hourly_data = []
    total_cost_static = 0
    total_cost_dynamic = 0
    
    for hour in range(24):
        # Statischer Tarif
        cost_static = hourly_consumption * base_price_eur_kwh
        total_cost_static += cost_static
        
        # Dynamischer Tarif
        if use_dynamic_tariff:
            # Finde passende Tarifzone
            price_factor = 1.0
            zone_name = "standard"
            
            for zone_key, zone_data in tariff_zones.items():
                if hour in zone_data["hours"]:
                    price_factor = zone_data["price_factor"]
                    zone_name = zone_data["description"]
                    break
            
            # Dynamischer Preis mit Zufallsschwankung (±5%)
            random_factor = random.uniform(0.95, 1.05)
            dynamic_price = base_price_eur_kwh * price_factor * random_factor
            cost_dynamic = hourly_consumption * dynamic_price
            total_cost_dynamic += cost_dynamic
        else:
            dynamic_price = base_price_eur_kwh
            cost_dynamic = cost_static
            zone_name = "statisch"
        
        hourly_data.append({
            "hour": hour,
            "consumption_kwh": round(hourly_consumption, 3),
            "price_static_eur_kwh": round(base_price_eur_kwh, 4),
            "price_dynamic_eur_kwh": round(dynamic_price, 4) if use_dynamic_tariff else round(base_price_eur_kwh, 4),
            "cost_static_eur": round(cost_static, 4),
            "cost_dynamic_eur": round(cost_dynamic, 4),
            "zone": zone_name,
            "savings_eur": round(cost_static - cost_dynamic, 4)
        })
    
    # Jahreshochrechnung
    annual_cost_static = total_cost_static * 365
    annual_cost_dynamic = total_cost_dynamic * 365
    annual_savings = annual_cost_static - annual_cost_dynamic
    
    return {
        "hourly_data": hourly_data,
        "daily_summary": {
            "cost_static_eur": round(total_cost_static, 2),
            "cost_dynamic_eur": round(total_cost_dynamic, 2),
            "savings_eur": round(total_cost_static - total_cost_dynamic, 2),
            "savings_percent": round(((total_cost_static - total_cost_dynamic) / total_cost_static) * 100, 1) if total_cost_static > 0 else 0
        },
        "annual_summary": {
            "cost_static_eur": round(annual_cost_static, 2),
            "cost_dynamic_eur": round(annual_cost_dynamic, 2),
            "savings_eur": round(annual_savings, 2),
            "savings_percent": round((annual_savings / annual_cost_static) * 100, 1) if annual_cost_static > 0 else 0
        },
        "tariff_zones": tariff_zones
    }


def calculate_dynamic_tariff_comparison(
    building_data: dict[str, Any],
    current_price_eur_kwh: float = 0.32,
    heatpump_share_percent: float = 30,
    smart_meter_cost_eur: float = 100
) -> dict[str, Any]:
    """
    Umfassender Vergleich: Statischer vs. Dynamischer Stromtarif
    
    Args:
        building_data: Gebäudedaten mit Heizlast und WP-COP
        current_price_eur_kwh: Aktueller statischer Arbeitspreis
        heatpump_share_percent: Anteil WP am Gesamtverbrauch (%)
        smart_meter_cost_eur: Einmalige Kosten für Smart-Meter
    
    Returns:
        Detaillierter Vergleich mit Einsparungen und Amortisation
    """
    
    # Jahresverbrauch berechnen
    heat_load_kw = building_data.get("heat_load_kw", 10)
    cop = building_data.get("cop", 3.5)
    annual_heat_kwh = heat_load_kw * 1800
    wp_electricity_kwh = annual_heat_kwh / cop
    
    # Gesamt-Haushaltsverbrauch (WP + Rest)
    if heatpump_share_percent > 0:
        total_consumption_kwh = wp_electricity_kwh / (heatpump_share_percent / 100)
    else:
        total_consumption_kwh = wp_electricity_kwh
    
    household_consumption_kwh = total_consumption_kwh - wp_electricity_kwh
    
    # Statischer Tarif
    static_cost_total = total_consumption_kwh * current_price_eur_kwh
    static_cost_wp = wp_electricity_kwh * current_price_eur_kwh
    static_cost_household = household_consumption_kwh * current_price_eur_kwh
    
    # Dynamischer Tarif - Durchschnittlich 15% günstiger
    dynamic_discount_factor = 0.85  # 15% Ersparnis
    
    # Für WP: Mehr Ersparnis durch gezielte Steuerung in günstige Zeiten
    dynamic_discount_wp = 0.75  # 25% Ersparnis durch Load-Shifting
    
    dynamic_cost_wp = wp_electricity_kwh * current_price_eur_kwh * dynamic_discount_wp
    dynamic_cost_household = household_consumption_kwh * current_price_eur_kwh * dynamic_discount_factor
    dynamic_cost_total = dynamic_cost_wp + dynamic_cost_household
    
    # Monatliche Grundgebühr Dynamischer Tarif (oft etwas höher)
    dynamic_base_fee_monthly = 12  # EUR/Monat
    dynamic_base_fee_annual = dynamic_base_fee_monthly * 12
    
    dynamic_cost_total_with_fee = dynamic_cost_total + dynamic_base_fee_annual
    
    # Einsparungen
    annual_savings = static_cost_total - dynamic_cost_total_with_fee
    annual_savings_percent = (annual_savings / static_cost_total) * 100 if static_cost_total > 0 else 0
    
    # Amortisation Smart-Meter
    payback_months = (smart_meter_cost_eur / (annual_savings / 12)) if annual_savings > 0 else 999
    
    # 10-Jahres-Bilanz
    savings_10_years = (annual_savings * 10) - smart_meter_cost_eur
    
    return {
        "consumption": {
            "total_kwh": round(total_consumption_kwh, 0),
            "heatpump_kwh": round(wp_electricity_kwh, 0),
            "household_kwh": round(household_consumption_kwh, 0),
            "heatpump_share_percent": round(heatpump_share_percent, 1)
        },
        "static_tariff": {
            "price_eur_kwh": current_price_eur_kwh,
            "annual_cost_total_eur": round(static_cost_total, 2),
            "annual_cost_wp_eur": round(static_cost_wp, 2),
            "annual_cost_household_eur": round(static_cost_household, 2),
            "monthly_cost_eur": round(static_cost_total / 12, 2)
        },
        "dynamic_tariff": {
            "avg_discount_percent": 15,
            "wp_discount_percent": 25,
            "annual_cost_energy_eur": round(dynamic_cost_total, 2),
            "annual_base_fee_eur": dynamic_base_fee_annual,
            "annual_cost_total_eur": round(dynamic_cost_total_with_fee, 2),
            "monthly_cost_eur": round(dynamic_cost_total_with_fee / 12, 2)
        },
        "savings": {
            "annual_eur": round(annual_savings, 2),
            "annual_percent": round(annual_savings_percent, 1),
            "monthly_eur": round(annual_savings / 12, 2),
            "10_years_eur": round(savings_10_years, 2)
        },
        "investment": {
            "smart_meter_cost_eur": smart_meter_cost_eur,
            "payback_months": round(payback_months, 1),
            "payback_years": round(payback_months / 12, 2)
        },
        "recommendation": {
            "worth_it": annual_savings > 200,  # Lohnt sich ab 200 EUR/Jahr
            "reason": "Lohnt sich!" if annual_savings > 200 else "Einsparung zu gering",
            "confidence": "Hoch" if heatpump_share_percent > 20 else "Mittel"
        }
    }


# ============================================================================
# STROMCLOUD-BERECHNUNGEN
# ============================================================================

def calculate_stromcloud_economics(
    pv_data: dict[str, Any],
    consumption_data: dict[str, Any],
    cloud_provider: str = "E.ON",
    cloud_plan: str = "3000"
) -> dict[str, Any]:
    """
    Berechnet Wirtschaftlichkeit einer Stromcloud
    
    Args:
        pv_data: PV-Anlagendaten (Jahresertrag, Eigenverbrauch)
        consumption_data: Verbrauchsdaten
        cloud_provider: Anbieter (E.ON, SENEC, sonnen, etc.)
        cloud_plan: Paket-Größe (z.B. "3000" für 3000 kWh Freimenge)
    
    Returns:
        Kosten-Nutzen-Analyse Stromcloud vs. Einspeisung
    """
    
    # Cloud-Tarife definieren (realistische Werte 2024)
    cloud_tariffs = {
        "E.ON": {
            "3000": {"base_fee_monthly": 19.90, "free_kwh": 3000, "overage_eur_kwh": 0.25},
            "4000": {"base_fee_monthly": 24.90, "free_kwh": 4000, "overage_eur_kwh": 0.25},
            "5000": {"base_fee_monthly": 29.90, "free_kwh": 5000, "overage_eur_kwh": 0.25}
        },
        "SENEC": {
            "2500": {"base_fee_monthly": 17.90, "free_kwh": 2500, "overage_eur_kwh": 0.23},
            "5000": {"base_fee_monthly": 27.90, "free_kwh": 5000, "overage_eur_kwh": 0.23}
        },
        "sonnen": {
            "3000": {"base_fee_monthly": 19.90, "free_kwh": 3000, "overage_eur_kwh": 0.23},
            "5500": {"base_fee_monthly": 29.90, "free_kwh": 5500, "overage_eur_kwh": 0.23}
        }
    }
    
    # PV-Daten
    annual_pv_production_kwh = pv_data.get("annual_production_kwh", 10000)
    direct_consumption_kwh = pv_data.get("direct_consumption_kwh", 3000)
    surplus_kwh = annual_pv_production_kwh - direct_consumption_kwh
    
    # Verbrauchsdaten
    annual_consumption_kwh = consumption_data.get("annual_consumption_kwh", 4500)
    grid_consumption_kwh = annual_consumption_kwh - direct_consumption_kwh
    
    # Cloud-Tarif
    if cloud_provider not in cloud_tariffs or cloud_plan not in cloud_tariffs[cloud_provider]:
        cloud_provider = "E.ON"
        cloud_plan = "3000"
    
    tariff = cloud_tariffs[cloud_provider][cloud_plan]
    
    # Stromcloud-Kosten
    base_fee_annual = tariff["base_fee_monthly"] * 12
    free_kwh = tariff["free_kwh"]
    
    # Wie viel wird aus Cloud bezogen?
    cloud_consumption_kwh = min(grid_consumption_kwh, free_kwh)
    overage_kwh = max(0, grid_consumption_kwh - free_kwh)
    overage_cost = overage_kwh * tariff["overage_eur_kwh"]
    
    total_cloud_cost = base_fee_annual + overage_cost
    
    # Vergleich: Ohne Cloud (normale Einspeisung)
    feed_in_tariff_eur_kwh = 0.082  # 8,2 Cent/kWh Einspeisevergütung 2024
    grid_price_eur_kwh = 0.32  # 32 Cent/kWh Bezugspreis
    
    # Ohne Cloud
    without_cloud_feed_in_revenue = surplus_kwh * feed_in_tariff_eur_kwh
    without_cloud_grid_cost = grid_consumption_kwh * grid_price_eur_kwh
    without_cloud_net_cost = without_cloud_grid_cost - without_cloud_feed_in_revenue
    
    # Mit Cloud
    with_cloud_feed_in_revenue = (surplus_kwh - cloud_consumption_kwh) * feed_in_tariff_eur_kwh if surplus_kwh > cloud_consumption_kwh else 0
    with_cloud_net_cost = total_cloud_cost - with_cloud_feed_in_revenue
    
    # Einsparung
    annual_savings = without_cloud_net_cost - with_cloud_net_cost
    
    # Autarkie-Grad
    autarkie_without_cloud = (direct_consumption_kwh / annual_consumption_kwh) * 100
    autarkie_with_cloud = ((direct_consumption_kwh + cloud_consumption_kwh) / annual_consumption_kwh) * 100
    
    return {
        "pv_system": {
            "annual_production_kwh": round(annual_pv_production_kwh, 0),
            "direct_consumption_kwh": round(direct_consumption_kwh, 0),
            "surplus_kwh": round(surplus_kwh, 0),
            "autarkie_without_cloud_percent": round(autarkie_without_cloud, 1),
            "autarkie_with_cloud_percent": round(autarkie_with_cloud, 1)
        },
        "cloud_tariff": {
            "provider": cloud_provider,
            "plan": f"{cloud_plan} kWh Freimenge",
            "base_fee_monthly_eur": tariff["base_fee_monthly"],
            "base_fee_annual_eur": round(base_fee_annual, 2),
            "free_kwh": free_kwh,
            "overage_price_eur_kwh": tariff["overage_eur_kwh"]
        },
        "without_cloud": {
            "grid_consumption_kwh": round(grid_consumption_kwh, 0),
            "grid_cost_eur": round(without_cloud_grid_cost, 2),
            "feed_in_kwh": round(surplus_kwh, 0),
            "feed_in_revenue_eur": round(without_cloud_feed_in_revenue, 2),
            "net_cost_eur": round(without_cloud_net_cost, 2)
        },
        "with_cloud": {
            "cloud_consumption_kwh": round(cloud_consumption_kwh, 0),
            "overage_kwh": round(overage_kwh, 0),
            "overage_cost_eur": round(overage_cost, 2),
            "total_cloud_cost_eur": round(total_cloud_cost, 2),
            "remaining_feed_in_kwh": round(max(0, surplus_kwh - cloud_consumption_kwh), 0),
            "feed_in_revenue_eur": round(with_cloud_feed_in_revenue, 2),
            "net_cost_eur": round(with_cloud_net_cost, 2)
        },
        "comparison": {
            "annual_savings_eur": round(annual_savings, 2),
            "monthly_savings_eur": round(annual_savings / 12, 2),
            "savings_percent": round((annual_savings / without_cloud_net_cost) * 100, 1) if without_cloud_net_cost > 0 else 0,
            "worth_it": annual_savings > 100,
            "autarkie_improvement_percent": round(autarkie_with_cloud - autarkie_without_cloud, 1)
        },
        "available_plans": cloud_tariffs
    }


# ============================================================================
# ENERGIEMANAGEMENT-SYSTEM (EMS) SIMULATOR
# ============================================================================

def simulate_energy_management_system(
    building_data: dict[str, Any],
    pv_data: dict[str, Any],
    battery_size_kwh: float = 10,
    ems_type: str = "SolarEdge"
) -> dict[str, Any]:
    """
    Simuliert intelligentes Energiemanagement-System
    
    Args:
        building_data: Gebäudedaten mit WP-Leistung
        pv_data: PV-Daten (Jahresertrag)
        battery_size_kwh: Batteriespeicher-Größe in kWh
        ems_type: EMS-Typ (SolarEdge, SMA, Fronius, SENEC, etc.)
    
    Returns:
        Load-Shifting-Potenzial, Autarkie-Verbesserung, Kosten-Einsparung
    """
    
    # EMS-Systeme mit Eigenschaften
    ems_systems = {
        "SolarEdge": {
            "efficiency": 0.95,  # 95% Wirkungsgrad
            "price_eur": 1500,
            "features": ["AI-Optimierung", "Wetterprognose", "API-Integration"],
            "max_battery_kwh": 20
        },
        "SMA": {
            "efficiency": 0.94,
            "price_eur": 1200,
            "features": ["ems-Light", "Lastmanagement", "Fernsteuerung"],
            "max_battery_kwh": 15
        },
        "Fronius": {
            "efficiency": 0.93,
            "price_eur": 1000,
            "features": ["Smart Grid Ready", "Notstrom", "Dynamische Tarife"],
            "max_battery_kwh": 12
        },
        "SENEC": {
            "efficiency": 0.96,
            "price_eur": 2000,
            "features": ["Senec.Cloud", "KI-Steuerung", "Wetter-API", "Auto-Heizen"],
            "max_battery_kwh": 30
        }
    }
    
    if ems_type not in ems_systems:
        ems_type = "SolarEdge"
    
    ems = ems_systems[ems_type]
    
    # Gebäude & PV-Daten
    heat_load_kw = building_data.get("heat_load_kw", 10)
    cop = building_data.get("cop", 3.5)
    annual_wp_kwh = (heat_load_kw * 1800) / cop
    
    annual_pv_kwh = pv_data.get("annual_production_kwh", 10000)
    direct_consumption_kwh = pv_data.get("direct_consumption_kwh", 3000)
    
    # Haushaltsverbrauch (angenommen 4500 kWh/Jahr)
    annual_household_kwh = 4500
    total_consumption_kwh = annual_wp_kwh + annual_household_kwh
    
    # OHNE EMS: Normale Steuerung
    without_ems_pv_usage = direct_consumption_kwh
    without_ems_autarkie = (without_ems_pv_usage / total_consumption_kwh) * 100
    without_ems_grid_consumption = total_consumption_kwh - without_ems_pv_usage
    
    # MIT EMS: Intelligente Steuerung
    # 1. Batterie-Pufferung
    battery_cycles_per_year = 250  # Realistische Zyklenzahl
    battery_usable_kwh = battery_size_kwh * 0.9  # 90% nutzbar (DoD)
    annual_battery_throughput = battery_usable_kwh * battery_cycles_per_year * ems["efficiency"]
    
    # 2. Load-Shifting: WP läuft während PV-Produktion
    shiftable_wp_percent = 0.40  # 40% der WP-Last verschiebbar (Puffer-Effekt Haus)
    shiftable_wp_kwh = annual_wp_kwh * shiftable_wp_percent
    
    # 3. Gesamter PV-Eigenverbrauch mit EMS
    with_ems_direct = direct_consumption_kwh
    with_ems_shifted = shiftable_wp_kwh * 0.70  # 70% davon wirklich in PV-Zeiten
    with_ems_battery = min(annual_battery_throughput, annual_pv_kwh * 0.30)  # Max 30% via Batterie
    
    with_ems_pv_usage = min(
        with_ems_direct + with_ems_shifted + with_ems_battery,
        annual_pv_kwh
    )
    
    with_ems_autarkie = (with_ems_pv_usage / total_consumption_kwh) * 100
    with_ems_grid_consumption = total_consumption_kwh - with_ems_pv_usage
    
    # Kosten-Einsparung
    grid_price_eur_kwh = 0.32
    savings_kwh = without_ems_grid_consumption - with_ems_grid_consumption
    annual_savings_eur = savings_kwh * grid_price_eur_kwh
    
    # ROI
    total_investment = ems["price_eur"] + (battery_size_kwh * 1000)  # 1000 EUR/kWh Batterie
    payback_years = total_investment / annual_savings_eur if annual_savings_eur > 0 else 999
    
    return {
        "ems_system": {
            "type": ems_type,
            "efficiency": ems["efficiency"],
            "price_eur": ems["price_eur"],
            "features": ems["features"],
            "battery_size_kwh": battery_size_kwh
        },
        "consumption": {
            "annual_wp_kwh": round(annual_wp_kwh, 0),
            "annual_household_kwh": annual_household_kwh,
            "total_kwh": round(total_consumption_kwh, 0)
        },
        "without_ems": {
            "pv_usage_kwh": round(without_ems_pv_usage, 0),
            "grid_consumption_kwh": round(without_ems_grid_consumption, 0),
            "autarkie_percent": round(without_ems_autarkie, 1),
            "annual_cost_eur": round(without_ems_grid_consumption * grid_price_eur_kwh, 2)
        },
        "with_ems": {
            "pv_usage_kwh": round(with_ems_pv_usage, 0),
            "load_shifted_kwh": round(with_ems_shifted, 0),
            "battery_usage_kwh": round(with_ems_battery, 0),
            "grid_consumption_kwh": round(with_ems_grid_consumption, 0),
            "autarkie_percent": round(with_ems_autarkie, 1),
            "annual_cost_eur": round(with_ems_grid_consumption * grid_price_eur_kwh, 2)
        },
        "improvement": {
            "additional_pv_usage_kwh": round(savings_kwh, 0),
            "autarkie_increase_percent": round(with_ems_autarkie - without_ems_autarkie, 1),
            "annual_savings_eur": round(annual_savings_eur, 2),
            "10_year_savings_eur": round(annual_savings_eur * 10, 2)
        },
        "investment": {
            "ems_cost_eur": ems["price_eur"],
            "battery_cost_eur": round(battery_size_kwh * 1000, 0),
            "total_investment_eur": round(total_investment, 0),
            "payback_years": round(payback_years, 2),
            "worth_it": payback_years < 10
        }
    }


# ============================================================================
# SMART-HOME-INTEGRATION
# ============================================================================

def calculate_smart_home_benefits(
    building_data: dict[str, Any],
    devices: dict[str, bool],
    automation_level: str = "medium"
) -> dict[str, Any]:
    """
    Berechnet Vorteile durch Smart-Home-Integration
    
    Args:
        building_data: Gebäudedaten
        devices: Dict mit steuerbaren Geräten {"heatpump": True, "battery": True, ...}
        automation_level: "low", "medium", "high"
    
    Returns:
        Einspar-Potenzial, Comfort-Score, Setup-Kosten
    """
    
    # Steuerbare Geräte und ihre Eigenschaften
    device_properties = {
        "heatpump": {
            "shiftable_percent": 40,  # 40% Last verschiebbar
            "savings_potential_eur_year": 250,
            "setup_cost_eur": 300,  # Smart-Thermostat + Integration
            "comfort_impact": 0.9  # 0-1 (1 = kein Komfortverlust)
        },
        "battery": {
            "shiftable_percent": 80,
            "savings_potential_eur_year": 400,
            "setup_cost_eur": 0,  # Meist im EMS enthalten
            "comfort_impact": 1.0
        },
        "wallbox": {
            "shiftable_percent": 90,  # E-Auto lädt meist nachts
            "savings_potential_eur_year": 300,
            "setup_cost_eur": 500,  # Smart-Wallbox
            "comfort_impact": 0.95
        },
        "washing_machine": {
            "shiftable_percent": 70,
            "savings_potential_eur_year": 50,
            "setup_cost_eur": 80,  # Smart-Plug
            "comfort_impact": 0.85
        },
        "dishwasher": {
            "shiftable_percent": 70,
            "savings_potential_eur_year": 40,
            "setup_cost_eur": 80,
            "comfort_impact": 0.85
        },
        "dryer": {
            "shiftable_percent": 60,
            "savings_potential_eur_year": 45,
            "setup_cost_eur": 80,
            "comfort_impact": 0.80
        }
    }
    
    # Automations-Level Faktoren
    automation_factors = {
        "low": {
            "efficiency": 0.60,  # 60% des theoretischen Potenzials
            "description": "Manuelle Steuerung über App",
            "setup_complexity": "Einfach"
        },
        "medium": {
            "efficiency": 0.80,  # 80%
            "description": "Zeit-basierte Automatisierung",
            "setup_complexity": "Mittel"
        },
        "high": {
            "efficiency": 0.95,  # 95%
            "description": "KI-gesteuert mit Wetterprognose",
            "setup_complexity": "Komplex"
        }
    }
    
    if automation_level not in automation_factors:
        automation_level = "medium"
    
    automation = automation_factors[automation_level]
    
    # Berechne Einsparungen pro Gerät
    device_results = {}
    total_savings = 0
    total_setup_cost = 0
    comfort_scores = []
    
    for device_name, is_enabled in devices.items():
        if not is_enabled or device_name not in device_properties:
            continue
        
        props = device_properties[device_name]
        
        # Reale Einsparung = Potenzial × Automations-Effizienz
        device_savings = props["savings_potential_eur_year"] * automation["efficiency"]
        device_setup = props["setup_cost_eur"]
        
        device_results[device_name] = {
            "enabled": True,
            "shiftable_percent": props["shiftable_percent"],
            "annual_savings_eur": round(device_savings, 2),
            "setup_cost_eur": device_setup,
            "comfort_impact": props["comfort_impact"],
            "payback_years": round(device_setup / device_savings, 2) if device_savings > 0 else 999
        }
        
        total_savings += device_savings
        total_setup_cost += device_setup
        comfort_scores.append(props["comfort_impact"])
    
    # Comfort-Score (Durchschnitt aller aktiven Geräte)
    avg_comfort = sum(comfort_scores) / len(comfort_scores) if comfort_scores else 1.0
    comfort_score_10 = avg_comfort * 10  # 0-10 Skala
    
    # ROI
    payback_years = total_setup_cost / total_savings if total_savings > 0 else 999
    
    # Zusätzliche Vorteile
    convenience_benefits = [
        "Automatische Optimierung ohne manuelle Eingriffe",
        "Fernsteuerung über App (auch im Urlaub)",
        "Benachrichtigungen bei Preisschwankungen",
        "Wetterbasierte Vorheizung (WP)",
        "E-Auto lädt immer im günstigsten Zeitfenster"
    ]
    
    return {
        "automation": {
            "level": automation_level,
            "efficiency_percent": round(automation["efficiency"] * 100, 0),
            "description": automation["description"],
            "setup_complexity": automation["setup_complexity"]
        },
        "devices": device_results,
        "summary": {
            "active_devices": len(device_results),
            "total_annual_savings_eur": round(total_savings, 2),
            "total_setup_cost_eur": round(total_setup_cost, 2),
            "payback_years": round(payback_years, 2),
            "10_year_savings_eur": round(total_savings * 10 - total_setup_cost, 2)
        },
        "comfort": {
            "score_0_10": round(comfort_score_10, 1),
            "description": "Hoch" if comfort_score_10 >= 8 else "Mittel" if comfort_score_10 >= 6 else "Niedrig",
            "recommendation": "Sehr gut - kaum Einschränkungen" if comfort_score_10 >= 8.5 else "Akzeptabel mit kleinen Anpassungen"
        },
        "convenience_benefits": convenience_benefits,
        "all_devices": device_properties
    }


# ============================================================================
# PROS & CONS ANALYSE
# ============================================================================

def get_dynamic_tariff_pros_cons(building_type: str = "residential") -> dict[str, Any]:
    """
    Detaillierte Pros & Cons Matrix für dynamische Stromtarife
    
    Args:
        building_type: "residential", "commercial", "multi_family"
    
    Returns:
        Umfangreiche Pro/Contra-Liste mit Gewichtungen
    """
    
    # Allgemeine Pros & Cons
    base_pros = [
        {
            "title": "💰 Deutliche Kosteneinsparung möglich",
            "description": "15-25% günstigere Stromkosten bei intelligentem Load-Shifting",
            "weight": 10,  # 1-10
            "applies_to": ["residential", "commercial", "multi_family"]
        },
        {
            "title": "♻️ Umweltfreundlich",
            "description": "Automatischer Verbrauch wenn viel Solar-/Windstrom verfügbar",
            "weight": 8,
            "applies_to": ["residential", "commercial", "multi_family"]
        },
        {
            "title": "🤖 Perfekt für Smart-Home",
            "description": "WP, E-Auto, Batterie automatisch zur besten Zeit steuern",
            "weight": 9,
            "applies_to": ["residential", "commercial"]
        },
        {
            "title": "📊 Transparente Preise",
            "description": "Stündliche Börsenstrompreise 1:1 sichtbar (kein Anbieter-Aufschlag)",
            "weight": 7,
            "applies_to": ["residential", "commercial", "multi_family"]
        },
        {
            "title": "🎯 Netzstabilität unterstützen",
            "description": "Lastverschiebung entlastet Stromnetz in Spitzenzeiten",
            "weight": 6,
            "applies_to": ["commercial", "multi_family"]
        },
        {
            "title": "🔮 Zukunftssicher",
            "description": "EU plant dynamische Tarife als Standard ab 2025",
            "weight": 8,
            "applies_to": ["residential", "commercial", "multi_family"]
        }
    ]
    
    base_cons = [
        {
            "title": "⚠️ Preisschwankungen",
            "description": "Strompreis kann stark schwanken (Faktor 3-5 zwischen günstig/teuer)",
            "weight": 8,
            "applies_to": ["residential", "commercial", "multi_family"]
        },
        {
            "title": "🔌 Smart Meter Pflicht",
            "description": "Intelligenter Stromzähler nötig (300-500 EUR Einbau, 40-100 EUR/Jahr)",
            "weight": 7,
            "applies_to": ["residential", "commercial", "multi_family"]
        },
        {
            "title": "🤔 Komplexität",
            "description": "Mehr Aufwand als normaler Stromtarif, Technik-Affinität hilfreich",
            "weight": 6,
            "applies_to": ["residential"]
        },
        {
            "title": "📱 Automatisierung empfohlen",
            "description": "Ohne Smart-Home/EMS kaum Einspar-Potenzial (manuelle Steuerung zu aufwändig)",
            "weight": 9,
            "applies_to": ["residential", "commercial", "multi_family"]
        },
        {
            "title": "⚡ Weniger Anbieter",
            "description": "Nur 3-4 Anbieter in Deutschland (Tibber, aWATTar, Ostrom, Rabot.Charge)",
            "weight": 5,
            "applies_to": ["residential", "commercial"]
        },
        {
            "title": "📈 Risiko bei fossilen Krisen",
            "description": "Bei Gas-Mangel können Börsenpreise explodieren (wie 2022)",
            "weight": 7,
            "applies_to": ["residential", "commercial", "multi_family"]
        },
        {
            "title": "🏠 Komfort-Einschränkungen möglich",
            "description": "WP heizt nachts statt tagsüber, E-Auto lädt zu festgelegten Zeiten",
            "weight": 5,
            "applies_to": ["residential"]
        }
    ]
    
    # Filter nach Gebäudetyp
    pros = [p for p in base_pros if building_type in p["applies_to"]]
    cons = [c for c in base_cons if building_type in c["applies_to"]]
    
    # Gewichtete Scores berechnen
    pro_score = sum(p["weight"] for p in pros)
    con_score = sum(c["weight"] for c in cons)
    total_score = pro_score - con_score
    
    # Empfehlung generieren
    if total_score >= 15:
        recommendation = "✅ Sehr empfehlenswert"
        recommendation_detail = "Dynamischer Tarif passt hervorragend zu Ihrem Profil"
    elif total_score >= 5:
        recommendation = "👍 Empfehlenswert"
        recommendation_detail = "Vorteile überwiegen die Nachteile deutlich"
    elif total_score >= -5:
        recommendation = "⚖️ Neutral"
        recommendation_detail = "Vorteile und Nachteile halten sich die Waage"
    elif total_score >= -15:
        recommendation = "⚠️ Mit Vorsicht"
        recommendation_detail = "Nachteile überwiegen leicht, gut abwägen"
    else:
        recommendation = "❌ Nicht empfohlen"
        recommendation_detail = "Zu viele Nachteile für Ihr Profil"
    
    # Idealer Nutzer
    ideal_user_profiles = {
        "residential": [
            "✅ Wärmepumpen-Besitzer mit großem Pufferspeicher",
            "✅ E-Auto-Fahrer mit Wallbox (flexibles Laden)",
            "✅ PV-Anlage mit Batteriespeicher",
            "✅ Smart-Home affin (Home Assistant, ioBroker, etc.)",
            "✅ Hoher Stromverbrauch (>5.000 kWh/Jahr)",
            "✅ Flexibler Tagesablauf"
        ],
        "commercial": [
            "✅ Flexible Produktionszeiten",
            "✅ Eigene PV-Anlage",
            "✅ Energiemanagement-System vorhanden",
            "✅ Hoher Grundverbrauch (>50.000 kWh/Jahr)",
            "✅ Kühl- oder Wärmespeicher verfügbar"
        ],
        "multi_family": [
            "✅ Zentrale Wärmepumpe mit großem Pufferspeicher",
            "✅ PV-Anlage für Mieterstrommodell",
            "✅ Energiemanagement für Gebäude",
            "✅ >20 Wohneinheiten (Skaleneffekt)"
        ]
    }
    
    return {
        "building_type": building_type,
        "pros": pros,
        "cons": cons,
        "scoring": {
            "pro_score": pro_score,
            "con_score": con_score,
            "total_score": total_score,
            "recommendation": recommendation,
            "recommendation_detail": recommendation_detail
        },
        "ideal_user": ideal_user_profiles.get(building_type, []),
        "summary": {
            "total_pros": len(pros),
            "total_cons": len(cons),
            "critical_cons": len([c for c in cons if c["weight"] >= 8])
        }
    }


# ============================================================================
# TARIF-PROVIDER VERGLEICH
# ============================================================================

def compare_tariff_providers(
    annual_consumption_kwh: float = 8000,
    has_ev: bool = False,
    has_heatpump: bool = True
) -> dict[str, Any]:
    """
    Vergleicht alle großen dynamischen Tarif-Anbieter in Deutschland
    
    Args:
        annual_consumption_kwh: Jahresverbrauch
        has_ev: E-Auto vorhanden
        has_heatpump: Wärmepumpe vorhanden
    
    Returns:
        Detaillierter Provider-Vergleich mit Kosten, Features, Empfehlung
    """
    
    # Durchschnittlicher Börsenpreis 2024 (angenommen)
    avg_spot_price_eur_kwh = 0.12
    
    providers = {
        "Tibber": {
            "base_fee_eur_month": 3.99,
            "markup_eur_kwh": 0.06,  # 6 ct/kWh Aufschlag
            "features": [
                "🤖 Beste App & Smart-Home Integration",
                "📊 Stündliche Prognose für nächsten Tag",
                "🔌 Pulse-Hardware für Echtzeit-Tracking (optional)",
                "🚗 Spezial-Tarif für E-Autos",
                "♻️ 100% Ökostrom"
            ],
            "pros": ["Top Smart-Home", "Sehr gute App", "Große Community"],
            "cons": ["Höchster Aufschlag", "Pulse kostet 99 EUR extra"],
            "rating": 4.7,
            "ev_bonus": 0.01 if has_ev else 0,  # 1 ct/kWh günstiger
            "wp_bonus": 0.005 if has_heatpump else 0,  # 0.5 ct/kWh günstiger
            "country": "Norwegen/Schweden",
            "website": "tibber.com/de"
        },
        "aWATTar": {
            "base_fee_eur_month": 0,  # Keine Grundgebühr!
            "markup_eur_kwh": 0.05,
            "features": [
                "💰 Keine Grundgebühr",
                "📈 Transparent: Börsenpreis + 5 ct/kWh",
                "🤝 Viele Partnerschaften (Sonnen, E3DC, etc.)",
                "🔌 HOURLY und YEARLY Tarif verfügbar",
                "♻️ 100% Ökostrom"
            ],
            "pros": ["Keine Grundgebühr", "Sehr transparent", "Günstig"],
            "cons": ["App weniger komfortabel", "Keine Echtzeit-Daten"],
            "rating": 4.5,
            "ev_bonus": 0,
            "wp_bonus": 0.01 if has_heatpump else 0,  # HOURLY Tarif für WP
            "country": "Österreich/Deutschland",
            "website": "awattar.de"
        },
        "Ostrom": {
            "base_fee_eur_month": 9.99,
            "markup_eur_kwh": 0.04,  # Niedrigster Aufschlag!
            "features": [
                "💚 Niedrigster Aufschlag (4 ct/kWh)",
                "📱 Moderne App mit Widget",
                "🔔 Push-Benachrichtigungen bei Negativ-Preisen",
                "🌍 100% Ökostrom aus Deutschland",
                "🤝 Chargepool Integration (E-Auto)"
            ],
            "pros": ["Niedrigster kWh-Preis", "Deutsche Firma", "Gute App"],
            "cons": ["Höhere Grundgebühr", "Weniger Smart-Home Integrationen"],
            "rating": 4.4,
            "ev_bonus": 0.015 if has_ev else 0,
            "wp_bonus": 0.01 if has_heatpump else 0,
            "country": "Deutschland",
            "website": "ostrom.de"
        },
        "Rabot.Charge": {
            "base_fee_eur_month": 5.99,
            "markup_eur_kwh": 0.055,
            "features": [
                "🚗 Spezialisiert auf E-Autos",
                "🤖 KI-gesteuerte Lade-Optimierung",
                "🔌 Eigene Wallbox-Hardware",
                "📊 THG-Quote direkt abrechenbar",
                "♻️ 100% Ökostrom"
            ],
            "pros": ["Beste E-Auto Integration", "THG-Bonus", "KI-Optimierung"],
            "cons": ["Nur für E-Auto-Besitzer sinnvoll", "Mittlerer Preis"],
            "rating": 4.6,
            "ev_bonus": 0.025 if has_ev else -0.02,  # 2.5 ct günstiger mit E-Auto, 2 ct teurer ohne
            "wp_bonus": 0,
            "country": "Deutschland",
            "website": "rabot.charge"
        }
    }
    
    # Kosten berechnen für jeden Provider
    comparison = {}
    for provider_name, provider in providers.items():
        # Effektiver Preis pro kWh
        effective_price = (
            avg_spot_price_eur_kwh +
            provider["markup_eur_kwh"] -
            provider["ev_bonus"] -
            provider["wp_bonus"]
        )
        
        # Jahreskosten
        annual_energy_cost = annual_consumption_kwh * effective_price
        annual_base_fee = provider["base_fee_eur_month"] * 12
        total_annual_cost = annual_energy_cost + annual_base_fee
        
        comparison[provider_name] = {
            "costs": {
                "base_fee_eur_month": provider["base_fee_eur_month"],
                "markup_eur_kwh": provider["markup_eur_kwh"],
                "effective_price_eur_kwh": round(effective_price, 4),
                "annual_energy_cost_eur": round(annual_energy_cost, 2),
                "annual_base_fee_eur": round(annual_base_fee, 2),
                "total_annual_cost_eur": round(total_annual_cost, 2)
            },
            "features": provider["features"],
            "pros": provider["pros"],
            "cons": provider["cons"],
            "rating": provider["rating"],
            "country": provider["country"],
            "website": provider["website"],
            "bonuses": {
                "ev_discount_eur_kwh": provider["ev_bonus"],
                "wp_discount_eur_kwh": provider["wp_bonus"]
            }
        }
    
    # Ranking erstellen (nach Gesamtkosten)
    ranked = sorted(
        comparison.items(),
        key=lambda x: x[1]["costs"]["total_annual_cost_eur"]
    )
    
    cheapest = ranked[0][0]
    most_expensive = ranked[-1][0]
    savings_vs_most_expensive = (
        comparison[most_expensive]["costs"]["total_annual_cost_eur"] -
        comparison[cheapest]["costs"]["total_annual_cost_eur"]
    )
    
    # Empfehlung generieren
    if has_ev and has_heatpump:
        recommended = "Rabot.Charge" if has_ev else "Ostrom"
        reason = "Beste Kombination für E-Auto + Wärmepumpe"
    elif has_ev:
        recommended = "Rabot.Charge"
        reason = "Spezialist für E-Auto-Laden"
    elif has_heatpump:
        recommended = "aWATTar" if annual_consumption_kwh > 5000 else "Ostrom"
        reason = "Bester Tarif für Wärmepumpen ohne E-Auto"
    else:
        recommended = "aWATTar"
        reason = "Keine Grundgebühr, sehr transparent"
    
    return {
        "providers": comparison,
        "ranking": [
            {
                "rank": i + 1,
                "provider": name,
                "annual_cost_eur": comparison[name]["costs"]["total_annual_cost_eur"]
            }
            for i, (name, _) in enumerate(ranked)
        ],
        "summary": {
            "cheapest_provider": cheapest,
            "most_expensive_provider": most_expensive,
            "max_savings_eur_year": round(savings_vs_most_expensive, 2),
            "recommended_provider": recommended,
            "recommendation_reason": reason
        },
        "assumptions": {
            "annual_consumption_kwh": annual_consumption_kwh,
            "avg_spot_price_eur_kwh": avg_spot_price_eur_kwh,
            "has_ev": has_ev,
            "has_heatpump": has_heatpump
        }
    }


# ============================================================================
# JAHRES-SIMULATION (8760 Stunden)
# ============================================================================

def simulate_annual_price_profile(
    building_data: dict[str, Any],
    include_seasonal_variations: bool = True
) -> dict[str, Any]:
    """
    Simuliert komplettes Preis- & Verbrauchs-Profil für ein Jahr (8760h)
    
    Args:
        building_data: Gebäudedaten
        include_seasonal_variations: Saisonale Schwankungen einbeziehen
    
    Returns:
        8760h-Simulation mit Kosten pro Stunde
    """
    
    # Basis-Daten
    heat_load_kw = building_data.get("heat_load_kw", 10)
    cop = building_data.get("cop", 3.5)
    base_load_kw = 0.5  # Haushalt Grundlast
    
    # Tarif-Zonen - konvertiere zu Liste mit start/end
    zones_dict = get_tariff_zones()
    zones = []
    for zone_name, zone_data in zones_dict.items():
        hours = zone_data["hours"]
        if hours:
            zones.append({
                "name": zone_name,
                "start_hour": min(hours),
                "end_hour": max(hours) + 1,  # +1 für exclusive Ende
                "price_factor": zone_data["price_factor"]
            })
    
    # Sortiere nach start_hour
    zones.sort(key=lambda z: z["start_hour"])
    
    # Monatliche Faktoren (Heizlast variiert stark)
    monthly_heating_factors = {
        1: 1.3,   # Januar: kältester Monat
        2: 1.2,   # Februar
        3: 1.0,   # März
        4: 0.7,   # April: wird wärmer
        5: 0.3,   # Mai
        6: 0.1,   # Juni: kaum Heizung
        7: 0.05,  # Juli
        8: 0.05,  # August
        9: 0.2,   # September
        10: 0.6,  # Oktober
        11: 0.9,  # November
        12: 1.2   # Dezember
    }
    
    # Strom-Preis Faktoren (Börse schwankt saisonal)
    monthly_price_factors = {
        1: 1.2,   # Winter: teuer
        2: 1.15,
        3: 1.0,
        4: 0.9,
        5: 0.85,
        6: 0.8,   # Sommer: viel Solar
        7: 0.75,
        8: 0.8,
        9: 0.9,
        10: 1.0,
        11: 1.1,
        12: 1.2
    } if include_seasonal_variations else {m: 1.0 for m in range(1, 13)}
    
    # Simulation
    base_price_eur_kwh = 0.12  # Börsen-Basispreis
    hourly_data = []
    
    monthly_summaries = {}
    current_month = 1
    month_consumption_kwh = 0
    month_cost_eur = 0
    
    for hour in range(8760):
        # Aktueller Monat (vereinfacht: 730h pro Monat)
        month = min(12, (hour // 730) + 1)
        hour_of_day = hour % 24
        day_of_week = (hour // 24) % 7
        
        # Verbrauch berechnen
        heating_factor = monthly_heating_factors[month]
        wp_load_kw = heat_load_kw * heating_factor / cop if heating_factor > 0.05 else 0
        
        # Haushalt: tagsüber mehr, nachts weniger
        if 6 <= hour_of_day < 22:
            household_factor = 1.2
        else:
            household_factor = 0.8
        
        household_load_kw = base_load_kw * household_factor
        total_load_kw = wp_load_kw + household_load_kw
        
        # Strompreis berechnen
        zone = None
        for z in zones:
            # Debug: Stelle sicher, dass z ein Dictionary ist
            if not isinstance(z, dict):
                continue
            if z["start_hour"] <= hour_of_day < z["end_hour"]:
                zone = z
                break
        
        if not zone:
            # Fallback mit Standard-Zone
            zone = {
                "name": "default",
                "price_factor": 1.0
            }
        
        price_factor = zone["price_factor"] * monthly_price_factors[month]
        price_eur_kwh = base_price_eur_kwh * price_factor
        
        # Kosten
        hourly_cost_eur = total_load_kw * price_eur_kwh
        
        hourly_data.append({
            "hour": hour,
            "month": month,
            "hour_of_day": hour_of_day,
            "day_of_week": day_of_week,
            "zone": zone["name"],
            "wp_load_kw": round(wp_load_kw, 3),
            "household_load_kw": round(household_load_kw, 3),
            "total_load_kw": round(total_load_kw, 3),
            "price_eur_kwh": round(price_eur_kwh, 4),
            "cost_eur": round(hourly_cost_eur, 4)
        })
        
        # Monatliche Summen
        month_consumption_kwh += total_load_kw
        month_cost_eur += hourly_cost_eur
        
        # Monatsende?
        if month != current_month or hour == 8759:
            monthly_summaries[current_month] = {
                "month": current_month,
                "consumption_kwh": round(month_consumption_kwh, 2),
                "cost_eur": round(month_cost_eur, 2),
                "avg_price_eur_kwh": round(month_cost_eur / month_consumption_kwh, 4) if month_consumption_kwh > 0 else 0
            }
            current_month = month
            month_consumption_kwh = 0
            month_cost_eur = 0
    
    # Jahres-Summen
    total_annual_consumption = sum(h["total_load_kw"] for h in hourly_data)
    total_annual_cost = sum(h["cost_eur"] for h in hourly_data)
    avg_price = total_annual_cost / total_annual_consumption if total_annual_consumption > 0 else 0
    
    return {
        "hourly_data": hourly_data,  # Alle 8760 Stunden
        "monthly_summaries": monthly_summaries,
        "annual_summary": {
            "total_consumption_kwh": round(total_annual_consumption, 2),
            "total_cost_eur": round(total_annual_cost, 2),
            "avg_price_eur_kwh": round(avg_price, 4),
            "wp_consumption_kwh": round(sum(h["wp_load_kw"] for h in hourly_data), 2),
            "household_consumption_kwh": round(sum(h["household_load_kw"] for h in hourly_data), 2)
        },
        "peak_hours": {
            "most_expensive_hour": max(hourly_data, key=lambda h: h["price_eur_kwh"]),
            "cheapest_hour": min(hourly_data, key=lambda h: h["price_eur_kwh"]),
            "highest_consumption_hour": max(hourly_data, key=lambda h: h["total_load_kw"])
        }
    }


