"""
Live Preview Helper Functions - Hilfsfunktionen für die Live-Vorschau
====================================================================

Alle notwendigen Funktionen für die Live-Vorschau der Berechnungen
"""

import math
from typing import Any

import streamlit as st

from emoji_toggle import should_show_emojis
from financial_calculations import (
    aggregate_subtotal,
    calculate_discount_amount,
    calculate_payback_years,
    calculate_surcharge_amount,
)


def _get_pricing_modifications_from_session() -> dict[str, Any]:
    """
    Holt Preismodifikationen aus der Session (Legacy-Funktion für Kompatibilität).
    Verwendet die neue einheitliche Implementierung.
    """
    return _get_pricing_modifications_from_session_unified()


def _calculate_final_price_with_modifications(
        base_price: float, modifications: dict[str, Any]) -> tuple:
    """
    Berechnet finalen Preis mit Modifikationen (Legacy-Funktion für Kompatibilität).

    WICHTIG: Diese Funktion wird für die Live-Vorschau verwendet.
    Die korrekte Formel ist: Matrixpreis + Zubehör - Rabatte
    """

    # Verwende die korrekte Formel: base_price sollte bereits Matrixpreis +
    # Zubehör sein
    final_price = base_price

    # Prozentuale Rabatte/Aufschläge
    discount_percent = modifications.get('discount_percent', 0.0)
    surcharge_percent = modifications.get('surcharge_percent', 0.0)

    percent_discount_amount = calculate_discount_amount(
        final_price, discount_percent)
    final_price = aggregate_subtotal(
        base=final_price,
        discounts=[percent_discount_amount] if percent_discount_amount else None,
    )

    percent_surcharge_amount = calculate_surcharge_amount(
        final_price, surcharge_percent)
    final_price = aggregate_subtotal(
        base=final_price,
        surcharges=[percent_surcharge_amount] if percent_surcharge_amount else None,
    )

    # Absolute Beträge
    special_discount = modifications.get('special_discount', 0.0)
    additional_costs = modifications.get('additional_costs', 0.0)

    final_price = aggregate_subtotal(
        base=final_price,
        discounts=[special_discount] if special_discount else None,
        additions=[additional_costs] if additional_costs else None,
    )

    # Gesamte Rabatte und Aufpreise berechnen (für Anzeige)
    total_rebates = percent_discount_amount + special_discount
    total_surcharges = percent_surcharge_amount + additional_costs

    return max(0, final_price), total_rebates, total_surcharges


def _get_pricing_modifications_from_session_unified() -> dict[str, float]:
    """
    Sammelt alle Preismodifikationen aus Session State (einheitliche Implementierung).

    Returns:
        Dictionary mit standardisierten Preismodifikationen
    """
    try:
        def _to_float(val, default=0.0):
            try:
                return float(val or 0.0)
            except Exception:
                return default

        # Sammle aus verschiedenen Session State Quellen
        modifications = {}

        # Aus pricing_modifications Dictionary (falls vorhanden)
        pricing_mods = st.session_state.get("pricing_modifications", {})
        modifications["discount_percent"] = _to_float(
            pricing_mods.get("discount_percent", 0.0))
        modifications["surcharge_percent"] = _to_float(
            pricing_mods.get("surcharge_percent", 0.0))
        modifications["special_discount"] = _to_float(
            pricing_mods.get("special_discount", 0.0))
        modifications["additional_costs"] = _to_float(
            pricing_mods.get("additional_costs", 0.0))

        # Aus individuellen Session State Keys (Slider-Werte haben Priorität)
        slider_discount = _to_float(st.session_state.get(
            "pricing_modifications_discount_slider", 0.0))
        slider_rebates = _to_float(st.session_state.get(
            "pricing_modifications_rebates_slider", 0.0))
        slider_surcharge = _to_float(st.session_state.get(
            "pricing_modifications_surcharge_slider", 0.0))
        slider_special_costs = _to_float(st.session_state.get(
            "pricing_modifications_special_costs_slider", 0.0))
        slider_miscellaneous = _to_float(st.session_state.get(
            "pricing_modifications_miscellaneous_slider", 0.0))

        # Verwende Slider-Werte falls sie höher sind (Slider haben Priorität)
        modifications["discount_percent"] = max(
            modifications["discount_percent"], slider_discount)
        modifications["surcharge_percent"] = max(
            modifications["surcharge_percent"], slider_surcharge)
        modifications["special_discount"] = max(
            modifications["special_discount"], slider_rebates)
        modifications["additional_costs"] = max(
            modifications["additional_costs"],
            slider_special_costs + slider_miscellaneous)

        return modifications

    except Exception as e:
        print(f"Warning: Could not collect pricing modifications: {e}")
        return {
            'discount_percent': 0.0,
            'surcharge_percent': 0.0,
            'special_discount': 0.0,
            'additional_costs': 0.0
        }


def _calculate_electricity_costs_projection(
        results: dict[str, Any], years: int, price_increase: float) -> float:
    """Berechnet Stromkosten-Projektion ohne PV"""

    annual_consumption = results.get('annual_consumption_kwh', 3000.0)
    current_price_per_kwh = results.get(
        'electricity_price_ct_per_kwh', 30.0) / 100.0

    total_costs = 0
    for year in range(years):
        yearly_price = current_price_per_kwh * \
            ((1 + price_increase / 100) ** year)
        total_costs += annual_consumption * yearly_price

    return total_costs


def _calculate_electricity_costs_with_pv_projection(
        results: dict[str, Any], years: int, price_increase: float) -> float:
    """Berechnet Stromkosten-Projektion mit PV"""

    grid_consumption = results.get('grid_bezug_kwh', 0.0)
    current_price_per_kwh = results.get(
        'electricity_price_ct_per_kwh', 30.0) / 100.0
    annual_feed_in_revenue = results.get('annual_feedin_revenue_euro', 0.0)

    total_costs = 0
    for year in range(years):
        yearly_price = current_price_per_kwh * \
            ((1 + price_increase / 100) ** year)
        yearly_costs = grid_consumption * yearly_price - annual_feed_in_revenue
        total_costs += max(0, yearly_costs)  # Nie negativ

    return total_costs


def _calculate_amortization_time(
        investment: float,
        annual_savings: float) -> float:
    """Berechnet Amortisationszeit"""

    return calculate_payback_years(
        investment,
        annual_savings,
        allow_infinite=False,
        default_zero=True,
    )


def _format_german_number(
        value: float,
        unit: str = "",
        decimal_places: int = 2) -> str:
    """Formatiert Zahlen im deutschen Format: 1.234,56 €"""
    if value == 0:
        return f"0,00 {unit}".strip()

    if decimal_places == 0:
        formatted = f"{value:,.0f}".replace(',', '.')
    else:
        formatted = f"{value:,.{decimal_places}f}"
        formatted = formatted.replace(
            ',',
            'TEMP').replace(
            '.',
            ',').replace(
            'TEMP',
            '.')

    return f"{formatted} {unit}".strip()


def format_kpi_value(value: Any,
                     unit: str = "",
                     precision: int = 2,
                     texts_dict: dict[str,
                                      str] | None = None) -> str:
    """Formatiert KPI-Werte"""
    if value is None:
        return "k.A."
    if isinstance(value, (float, int)) and (
            math.isnan(value) or math.isinf(value)):
        return "k.A."
    if isinstance(value, str):
        try:
            value = float(value.replace(",", "."))
        except (ValueError, AttributeError):
            return value

    if isinstance(value, (int, float)):
        if unit == "Jahre":
            return f"{value:.1f} Jahre"
        return _format_german_number(value, unit, precision)

    return str(value)


def _get_emoji(emoji: str) -> str:
    """Gibt Emoji zurück oder leeren String je nach Einstellung"""
    return emoji if should_show_emojis() else ""


def render_live_cost_preview(results_for_display: dict[str, Any] = None):
    """Rendert die Live-Kostenvorschau in der Seitenleiste"""

    if results_for_display is None:
        results_for_display = st.session_state.get('calculation_results', {})

    project_details = st.session_state.get(
        'project_data', {}).get(
        'project_details', {})

    st.sidebar.markdown("---")
    st.sidebar.subheader("Live-Fakten-Vorschau")

    if results_for_display:
        pricing_modifications_preview = _get_pricing_modifications_from_session()

        analysis_results = st.session_state.get('analysis_results', {})
        simple_pricing = st.session_state.get('simple_pricing_data', {})
        complete_pricing = st.session_state.get('complete_pricing_data', {})
        final_pricing = st.session_state.get('final_pricing_data', {})
        final_keys_values = st.session_state.get(
            'solar_calculator_final_pricing_values', {})

        data_sources: list[dict[str,
                                Any]] = [project_details,
                                         results_for_display,
                                         analysis_results,
                                         simple_pricing,
                                         simple_pricing.get('formatted',
                                                            {}) if isinstance(simple_pricing.get('formatted'),
                                                                              dict) else {},
                                         complete_pricing,
                                         complete_pricing.get('formatted',
                                                              {}) if isinstance(complete_pricing.get('formatted'),
                                                                                dict) else {},
                                         final_pricing,
                                         final_pricing.get('formatted',
                                                           {}) if isinstance(final_pricing.get('formatted'),
                                                                             dict) else {},
                                         final_keys_values if isinstance(final_keys_values,
                                                                         dict) else {},
                                         ]

        def _to_float(value: Any) -> float | None:
            if value is None:
                return None
            if isinstance(value, (int, float)):
                candidate = float(value)
                if math.isnan(candidate) or math.isinf(candidate):
                    return None
                return candidate
            if isinstance(value, str):
                cleaned = value.strip()
                if not cleaned or cleaned.lower(
                ) in {"n/a", "k.a.", "na", "--"}:
                    return None
                replacements = ["€", "kwh", "kwp", "jahre",
                                "jahr", "%", "p.a.", "brutto", "netto"]
                for token in replacements:
                    cleaned = cleaned.replace(token, "")
                    cleaned = cleaned.replace(token.upper(), "")
                cleaned = cleaned.replace("\xa0", "")
                cleaned = cleaned.replace(" ", "")
                cleaned = cleaned.replace("−", "-")
                cleaned = cleaned.replace("~", "")
                # Ersetze deutsche Dezimaltrennzeichen korrekt
                if "," in cleaned and "." in cleaned:
                    if cleaned.rfind(",") > cleaned.rfind('.'):
                        cleaned = cleaned.replace('.', '').replace(',', '.')
                    else:
                        cleaned = cleaned.replace(',', '')
                elif cleaned.count(',') == 1:
                    cleaned = cleaned.replace(',', '.')
                # Entferne verbleibende Tausenderpunkte
                if cleaned.count('.') > 1:
                    parts = cleaned.split('.')
                    cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
                try:
                    return float(cleaned)
                except ValueError:
                    return None
            return None

        def _resolve_numeric(
                keys: list[str],
                default: float | None = None) -> float | None:
            for source in data_sources:
                if not isinstance(source, dict):
                    continue
                for key in keys:
                    if key in source:
                        parsed = _to_float(source.get(key))
                        if parsed is not None:
                            return parsed
            return default

        netto_betrag = _resolve_numeric(
            [
                'final_offer_price_net',
                'final_end_preis',
                'base_price_for_modifications',
                'finale_summe_netto',
                'total_investment_netto',
                'netto_mit_provision',
                'final_offer_price_netto',
            ],
            default=0.0,
        ) or 0.0

        total_rebates = _resolve_numeric([
            'total_discounts',
            'total_discount',
            'discount_total',
        ])
        if total_rebates is None:
            total_rebates = (
                pricing_modifications_preview.get(
                    'special_discount',
                    0.0) +
                calculate_discount_amount(
                    netto_betrag,
                    pricing_modifications_preview.get(
                        'discount_percent',
                        0.0)))
        total_rebates = max(total_rebates or 0.0, 0.0)

        total_surcharges = _resolve_numeric([
            'total_surcharges',
            'total_surcharge',
            'surcharge_total',
        ])
        if total_surcharges is None:
            total_surcharges = (
                pricing_modifications_preview.get(
                    'additional_costs',
                    0.0) +
                calculate_surcharge_amount(
                    max(
                        netto_betrag -
                        total_rebates,
                        0.0),
                    pricing_modifications_preview.get(
                        'surcharge_percent',
                        0.0),
                ))
        total_surcharges = max(total_surcharges or 0.0, 0.0)

        vat_amount = _resolve_numeric([
            'minus_mehrwertsteuer',
            'base_mwst',
            'mwst_betrag',
            'vat_amount',
        ], default=0.0) or 0.0

        brutto_endbetrag = _resolve_numeric([
            'preis_mit_mwst',
            'final_offer_price_gross',
            'zwischensumme_brutto',
            'endergebnis_brutto',
            'zwischensumme_final',
        ])

        if brutto_endbetrag is None or brutto_endbetrag <= 0:
            brutto_endbetrag = max(
                netto_betrag -
                total_rebates +
                total_surcharges +
                vat_amount,
                0.0)
            if brutto_endbetrag <= 0:
                brutto_endbetrag = max(
                    netto_betrag - total_rebates + total_surcharges, 0.0)

        if netto_betrag <= 0 and brutto_endbetrag > 0 and vat_amount > 0:
            netto_betrag = max(brutto_endbetrag - vat_amount, 0.0)

        if netto_betrag <= 0:
            final_price_preview, _, _ = _calculate_final_price_with_modifications(
                max(results_for_display.get('total_investment_netto', 0.0), 0.0),
                pricing_modifications_preview,
            )
            netto_betrag = max(final_price_preview - vat_amount, 0.0)

        final_offer_price = _resolve_numeric([
            'final_end_preis',
            'final_offer_price_net',
            'final_offer_price_gross',
            'preis_mit_mwst',
            'zwischensumme_brutto',
            'endergebnis_brutto',
            'zwischensumme_final',
        ])

        if final_offer_price is None or final_offer_price <= 0:
            final_offer_price = brutto_endbetrag

        final_offer_price_display: str | None = None
        preferred_display_keys = [
            'final_end_preis_formatted',
            'FINAL_END_PREIS_FORMATTED',
            'formatted_final_end_preis',
            'PDF__FINAL_END_PREIS_FORMATTED',
            'final_end_preis',
        ]
        for source in data_sources:
            if not isinstance(source, dict):
                continue
            for key in preferred_display_keys:
                if key in source:
                    candidate = source.get(key)
                    if isinstance(candidate, str) and candidate.strip():
                        final_offer_price_display = candidate.strip()
                        break
            if final_offer_price_display:
                break

        if not final_offer_price_display and final_offer_price is not None and final_offer_price > 0:
            final_offer_price_display = _format_german_number(
                final_offer_price, '€')

        if not final_offer_price_display:
            final_offer_price_display = "k.A."

        if '€' not in final_offer_price_display and final_offer_price is not None and final_offer_price > 0:
            final_offer_price_display = f"{final_offer_price_display} €"

        st.sidebar.write(
            f" **Netto (nach Provision):** {_format_german_number(netto_betrag, '€')}")
        if total_rebates > 0:
            st.sidebar.write(
                f" **Rabatte gesamt:** -{_format_german_number(total_rebates, '€')}")
        if total_surcharges > 0:
            st.sidebar.write(
                f" **Aufpreise gesamt:** +{_format_german_number(total_surcharges, '€')}")
        st.sidebar.write(
            f" **Finaler Angebotspreis:** {final_offer_price_display}")

        # Zusätzliche Kennzahlen – nur anzeigen, wenn valide Werte vorhanden
        annual_savings = _resolve_numeric([
            'annual_savings_total_euro',
            'annual_financial_benefit_year1',
            'total_annual_savings_eur',
            'annual_total_benefits_eur',
        ])

        if (annual_savings is None or annual_savings <= 0) and results_for_display:
            baseline_costs = _calculate_electricity_costs_projection(
                results_for_display, 1, 0.0)
            with_pv_costs = _calculate_electricity_costs_with_pv_projection(
                results_for_display, 1, 0.0)
            feed_in_revenue = _resolve_numeric([
                'annual_feedin_revenue_euro',
                'annual_feed_in_revenue_eur',
                'annual_feed_in_revenue_year1',
                'annual_feed_in_revenue',
            ], default=0.0) or 0.0
            annual_savings = max(
                baseline_costs -
                with_pv_costs +
                feed_in_revenue,
                0.0)

        if annual_savings and annual_savings > 0 and netto_betrag > 0:
            amortization_years = _calculate_amortization_time(
                netto_betrag, annual_savings)
            if amortization_years > 0 and amortization_years < 100:
                st.sidebar.write(
                    f"{_get_emoji('⏱')} **Amortisationszeit:** {_format_german_number(amortization_years, 'Jahre')}")

        annual_feed_in = _resolve_numeric([
            'annual_feedin_revenue_euro',
            'annual_feed_in_revenue_eur',
            'annual_feed_in_revenue_year1',
            'annual_feed_in_revenue',
        ])
        if annual_feed_in is not None:
            st.sidebar.write(
                f"{_get_emoji('')} **Jährliche Einspeisevergütung:** {format_kpi_value(annual_feed_in, '€')}")

        battery_capacity = _resolve_numeric([
            'selected_storage_capacity_kwh',
            'storage_capacity_kwh',
            'battery_capacity_kwh',
            'selected_storage_storage_power_kw',
        ])
        if battery_capacity and battery_capacity > 0:
            st.sidebar.write(
                f"{_get_emoji('')} **Batteriegröße:** {format_kpi_value(battery_capacity, 'kWh')}")

    else:
        st.sidebar.info("Keine Berechnungsergebnisse verfügbar")

    st.sidebar.markdown("---")
