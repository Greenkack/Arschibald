#!/usr/bin/env python3
"""
Erweiterte Berechnungslogik für korrekte Live-Vorschau Werte
"""

from typing import Any

import streamlit as st

from financial_calculations import calculate_payback_years


def calculate_correct_live_values(results: dict[str, Any]) -> dict[str, Any]:
    """
    Berechnet alle Live-Vorschau Werte korrekt nach der angegebenen Logik
    """
    # Basis-Daten extrahieren
    annual_production_kwh = results.get('annual_pv_production_kwh', 0)
    annual_consumption_kwh = results.get('annual_consumption_kwh', 0)
    monthly_electricity_cost = results.get('monthly_electricity_cost', 0)
    autarkie_grad_percent = results.get('self_supply_rate_percent', 0)
    battery_capacity_kwh = results.get('battery_capacity_kwh', 0)
    feed_in_tariff_ct_kwh = results.get(
        'feed_in_tariff_ct_kwh',
        8.2)  # Admin-Bereich Wert
    price_increase_percent = results.get(
        'electricity_price_increase_rate_effective_percent', 4.0)
    simulation_years = results.get('simulation_period_years_effective', 20)

    # Investment-Werte
    investment_netto = results.get('total_investment_netto', 0)
    investment_brutto = results.get(
        'total_investment_brutto',
        investment_netto *
        1.19 if investment_netto > 0 else 0)

    # 1. STROMTARIF BERECHNEN
    # Jährliche Gesamtstromkosten / Gesamtstromverbrauch kWh = Stromtarif
    # ct/kWh
    yearly_electricity_cost = monthly_electricity_cost * 12
    stromtarif_ct_kwh = (yearly_electricity_cost * 100) / \
        annual_consumption_kwh if annual_consumption_kwh > 0 else 0

    # 2. STROMKOSTEN OHNE PV
    # Stromkosten monatlich x 12 = jährliche Kosten + Strompreissteigerung
    # über Simulationsdauer
    base_yearly_cost = yearly_electricity_cost
    total_cost_without_pv = 0
    for year in range(1, int(simulation_years) + 1):
        yearly_cost = base_yearly_cost * \
            ((1 + price_increase_percent / 100) ** (year - 1))
        total_cost_without_pv += yearly_cost

    # 3. AUTARKIEGRAD UND VERBRAUCHSAUFTEILUNG
    # Direkter Verbrauch aus PV
    direct_consumption_kwh = annual_consumption_kwh * \
        (autarkie_grad_percent / 100)

    # Batteriespeicher-Ladung (falls vorhanden)
    battery_charged_kwh = min(
        battery_capacity_kwh *
        365,
        annual_production_kwh -
        direct_consumption_kwh) if battery_capacity_kwh > 0 else 0

    # Überschuss für Einspeisung
    surplus_for_feed_in = annual_production_kwh - \
        direct_consumption_kwh - battery_charged_kwh
    surplus_for_feed_in = max(0, surplus_for_feed_in)

    # 4. JÄHRLICHE EINSPEISEVERGÜTUNG
    # Überschuss x Einspeisevergütungstarif
    annual_feed_in_revenue = surplus_for_feed_in * \
        (feed_in_tariff_ct_kwh / 100)

    # 5. STROMKOSTEN MIT PV
    # Jährliche Stromkosten minus Autarkiegrad-Anteil plus Einspeisevergütung
    remaining_consumption_kwh = annual_consumption_kwh - direct_consumption_kwh
    yearly_cost_with_pv_base = remaining_consumption_kwh * \
        (stromtarif_ct_kwh / 100)

    total_cost_with_pv = 0
    for year in range(1, int(simulation_years) + 1):
        yearly_cost = yearly_cost_with_pv_base * \
            ((1 + price_increase_percent / 100) ** (year - 1))
        total_cost_with_pv += yearly_cost

    # Einspeisung reduziert die Kosten
    total_feed_in_revenue = annual_feed_in_revenue * \
        simulation_years  # Vereinfacht, könnte auch steigen
    total_cost_with_pv -= total_feed_in_revenue
    total_cost_with_pv = max(0, total_cost_with_pv)

    # 6. GESAMTERSPARNIS
    # Autarkiegrad-Anteil für verbrauchte kWh x Stromtarif + Einspeisevergütung
    annual_savings_from_self_consumption = direct_consumption_kwh * \
        (stromtarif_ct_kwh / 100)
    annual_total_savings = annual_savings_from_self_consumption + annual_feed_in_revenue
    total_savings_over_period = total_cost_without_pv - total_cost_with_pv

    # 7. AMORTISATIONSZEIT
    amortization_years = calculate_payback_years(
        investment_brutto,
        annual_total_savings,
        allow_infinite=False,
        default_zero=True,
    )

    return {
        'stromtarif_ct_kwh': stromtarif_ct_kwh,
        'stromkosten_ohne_pv_total': total_cost_without_pv,
        'stromkosten_mit_pv_total': total_cost_with_pv,
        'gesamtersparnis_total': total_savings_over_period,
        'jaehrliche_einspeiseverguetung': annual_feed_in_revenue,
        'jaehrliche_gesamtersparnis': annual_total_savings,
        'amortisationszeit_jahre': amortization_years,
        'direct_consumption_kwh': direct_consumption_kwh,
        'surplus_for_feed_in_kwh': surplus_for_feed_in,
        'battery_charged_kwh': battery_charged_kwh,
        'remaining_consumption_kwh': remaining_consumption_kwh
    }


def get_admin_feed_in_tariff() -> float:
    """
    Holt Einspeisevergütung aus Admin-Einstellungen
    """
    try:
        # Hier würde normalerweise die Admin-Funktion aufgerufen
        # Fallback auf Standard-Wert
        return st.session_state.get('admin_feed_in_tariff_ct_kwh', 8.2)
    except BaseException:
        return 8.2  # Standard-Einspeisevergütung in ct/kWh
