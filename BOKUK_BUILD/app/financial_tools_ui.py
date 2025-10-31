# financial_tools_ui.py
"""
UI-Modul für ALLE Financial Tools Berechnungen
Zeigt ALLE Finanz-Berechnungen in der PDF-UI an
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_financial_tools_section(
    project_data: dict[str, Any],
    analysis_results: dict[str, Any],
    session_key_prefix: str = "fin_tools"
) -> dict[str, Any]:
    """
    Zeigt ALLE Financial Tools Berechnungen in der UI

    Args:
        project_data: Projektdaten
        analysis_results: Analyse-Ergebnisse
        session_key_prefix: Prefix für Session State Keys

    Returns:
        Dict mit allen Financial Tools Ergebnissen + Auswahl
    """
    st.markdown("---")
    st.markdown("### 💰 Financial Tools - Alle Berechnungen")
    st.markdown("Wählen Sie die Finanz-Berechnungen für die PDF-Ausgabe:")

    # Ergebnisse sammeln
    financial_results = {}

    try:
        from financial_tools import (
            calculate_annuity,
            calculate_capital_gains_tax,
            calculate_contracting_costs,
            calculate_depreciation,
            calculate_financing_comparison,
            calculate_leasing_costs,
        )

        total_investment = analysis_results.get('total_investment', 0)
        annual_savings = analysis_results.get('annual_savings_after_pv', 0)
        annual_feed_in = analysis_results.get('annual_feed_in_revenue', 0)
        annual_consumption = project_data.get('annual_consumption', 0)

        # === 1. ANNUITÄT (KREDIT) ===
        with st.expander("💳 Annuität - Kredit-Berechnung", expanded=False):
            st.markdown(f"**Investitionssumme:** {total_investment:,.2f} €")

            col1, col2 = st.columns(2)
            with col1:
                interest_15y = st.number_input(
                    "Zinssatz 15 Jahre (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=3.5,
                    step=0.1,
                    key=f"{session_key_prefix}_annuity_15y_rate"
                )
            with col2:
                include_annuity_15y = st.checkbox(
                    "In PDF aufnehmen (15J)",
                    value=True,
                    key=f"{session_key_prefix}_inc_annuity_15y"
                )

            if total_investment > 0:
                try:
                    annuity_15y = calculate_annuity(
                        principal=total_investment,
                        annual_interest_rate=interest_15y,
                        duration_years=15
                    )

                    st.success(
                        f"**Annuität (15 Jahre):** {annuity_15y:,.2f} € pro Jahr")
                    st.info(f"Monatlich: {annuity_15y / 12:,.2f} €")

                    if include_annuity_15y:
                        financial_results['annuity_15y'] = {
                            'value': annuity_15y,
                            'monthly': annuity_15y / 12,
                            'interest_rate': interest_15y,
                            'duration': 15,
                            'principal': total_investment
                        }
                except Exception as e:
                    st.error(f"Fehler: {e}")

            # 20 Jahre
            col3, col4 = st.columns(2)
            with col3:
                interest_20y = st.number_input(
                    "Zinssatz 20 Jahre (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=4.0,
                    step=0.1,
                    key=f"{session_key_prefix}_annuity_20y_rate"
                )
            with col4:
                include_annuity_20y = st.checkbox(
                    "In PDF aufnehmen (20J)",
                    value=False,
                    key=f"{session_key_prefix}_inc_annuity_20y"
                )

            if total_investment > 0:
                try:
                    annuity_20y = calculate_annuity(
                        principal=total_investment,
                        annual_interest_rate=interest_20y,
                        duration_years=20
                    )

                    st.success(
                        f"**Annuität (20 Jahre):** {annuity_20y:,.2f} € pro Jahr")
                    st.info(f"Monatlich: {annuity_20y / 12:,.2f} €")

                    if include_annuity_20y:
                        financial_results['annuity_20y'] = {
                            'value': annuity_20y,
                            'monthly': annuity_20y / 12,
                            'interest_rate': interest_20y,
                            'duration': 20,
                            'principal': total_investment
                        }
                except Exception as e:
                    st.error(f"Fehler: {e}")

        # === 2. LEASING ===
        with st.expander("🚗 Leasing-Kosten", expanded=False):
            st.markdown(f"**Investitionssumme:** {total_investment:,.2f} €")

            col1, col2 = st.columns(2)
            with col1:
                leasing_factor = st.number_input(
                    "Leasing-Faktor (%)",
                    min_value=0.5,
                    max_value=3.0,
                    value=1.2,
                    step=0.1,
                    key=f"{session_key_prefix}_leasing_factor"
                )
            with col2:
                leasing_months = st.number_input(
                    "Laufzeit (Monate)",
                    min_value=12,
                    max_value=300,
                    value=180,
                    step=12,
                    key=f"{session_key_prefix}_leasing_months"
                )

            include_leasing = st.checkbox(
                "In PDF aufnehmen",
                value=True,
                key=f"{session_key_prefix}_inc_leasing"
            )

            if total_investment > 0:
                try:
                    leasing = calculate_leasing_costs(
                        total_investment=total_investment,
                        leasing_factor=leasing_factor,
                        duration_months=leasing_months
                    )

                    st.success(
                        f"**Leasing-Rate:** {leasing['monthly_rate']:,.2f} € pro Monat")
                    st.info(f"Gesamt: {leasing['total_cost']:,.2f} €")
                    st.warning(
                        f"Mehr-Kosten vs. Kauf: {leasing['total_cost'] - total_investment:,.2f} €")

                    if include_leasing:
                        financial_results['leasing'] = leasing
                except Exception as e:
                    st.error(f"Fehler: {e}")

        # === 3. ABSCHREIBUNG (AfA) ===
        with st.expander("📉 Abschreibung (AfA)", expanded=False):
            st.markdown(f"**Investitionssumme:** {total_investment:,.2f} €")

            col1, col2 = st.columns(2)
            with col1:
                useful_life = st.number_input(
                    "Nutzungsdauer (Jahre)",
                    min_value=5,
                    max_value=40,
                    value=20,
                    step=1,
                    key=f"{session_key_prefix}_useful_life"
                )
            with col2:
                depreciation_method = st.selectbox(
                    "Methode",
                    options=['linear', 'degressive'],
                    key=f"{session_key_prefix}_depreciation_method"
                )

            include_depreciation = st.checkbox(
                "In PDF aufnehmen",
                value=True,
                key=f"{session_key_prefix}_inc_depreciation"
            )

            if total_investment > 0:
                try:
                    depreciation = calculate_depreciation(
                        initial_value=total_investment,
                        useful_life_years=useful_life,
                        method=depreciation_method
                    )

                    st.success(
                        f"**Jährliche Abschreibung:** {depreciation['annual_depreciation']:,.2f} €")
                    st.info(
                        f"Restwert nach {useful_life} Jahren: {
                            depreciation['residual_value']:,.2f} €")

                    if include_depreciation:
                        financial_results['depreciation'] = depreciation
                except Exception as e:
                    st.error(f"Fehler: {e}")

        # === 4. FINANZIERUNGS-VERGLEICH ===
        with st.expander("⚖️ Finanzierungs-Vergleich (Kredit vs Leasing)", expanded=False):
            st.markdown(f"**Investitionssumme:** {total_investment:,.2f} €")

            col1, col2, col3 = st.columns(3)
            with col1:
                comp_interest = st.number_input(
                    "Kredit-Zinssatz (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=3.5,
                    step=0.1,
                    key=f"{session_key_prefix}_comp_interest"
                )
            with col2:
                comp_duration = st.number_input(
                    "Kredit-Laufzeit (Jahre)",
                    min_value=5,
                    max_value=30,
                    value=15,
                    step=1,
                    key=f"{session_key_prefix}_comp_duration"
                )
            with col3:
                comp_leasing_factor = st.number_input(
                    "Leasing-Faktor (%)",
                    min_value=0.5,
                    max_value=3.0,
                    value=1.2,
                    step=0.1,
                    key=f"{session_key_prefix}_comp_leasing_factor"
                )

            include_comparison = st.checkbox(
                "In PDF aufnehmen",
                value=True,
                key=f"{session_key_prefix}_inc_comparison"
            )

            if total_investment > 0:
                try:
                    comparison = calculate_financing_comparison(
                        investment=total_investment,
                        annual_interest_rate=comp_interest,
                        loan_duration_years=comp_duration,
                        leasing_factor_percent=comp_leasing_factor
                    )

                    st.success("**Vergleich:**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Kredit - Gesamt",
                                  f"{comparison['loan']['total_cost']:,.2f} €")
                        st.metric("Kredit - Monatlich",
                                  f"{comparison['loan']['monthly_payment']:,.2f} €")
                    with col_b:
                        st.metric("Leasing - Gesamt",
                                  f"{comparison['leasing']['total_cost']:,.2f} €")
                        st.metric("Leasing - Monatlich",
                                  f"{comparison['leasing']['monthly_rate']:,.2f} €")

                    diff = comparison['leasing']['total_cost'] - \
                        comparison['loan']['total_cost']
                    if diff > 0:
                        st.info(
                            f"💡 **Kredit ist günstiger:** {diff:,.2f} € Ersparnis")
                    else:
                        st.info(
                            f"💡 **Leasing ist günstiger:** {abs(diff):,.2f} € Ersparnis")

                    if include_comparison:
                        financial_results['financing_comparison'] = comparison
                except Exception as e:
                    st.error(f"Fehler: {e}")

        # === 5. KAPITALERTRAGSSTEUER ===
        with st.expander("📊 Kapitalertragssteuer (auf Einspeisevergütung)", expanded=False):
            st.markdown(
                f"**Jährliche Einspeisevergütung:** {annual_feed_in:,.2f} €")

            col1, col2 = st.columns(2)
            with col1:
                tax_rate = st.number_input(
                    "Steuersatz (%)",
                    min_value=0.0,
                    max_value=50.0,
                    value=26.375,  # KESt in Deutschland
                    step=0.1,
                    key=f"{session_key_prefix}_tax_rate"
                )
            with col2:
                include_capital_gains = st.checkbox(
                    "In PDF aufnehmen",
                    value=False,
                    key=f"{session_key_prefix}_inc_capital_gains"
                )

            if annual_feed_in > 0:
                try:
                    capital_gains = calculate_capital_gains_tax(
                        profit=annual_feed_in,
                        tax_rate=tax_rate
                    )

                    st.success(
                        f"**Steuer pro Jahr:** {capital_gains['tax_amount']:,.2f} €")
                    st.info(
                        f"Netto nach Steuern: {
                            capital_gains['net_profit']:,.2f} €")

                    if include_capital_gains:
                        financial_results['capital_gains_tax'] = capital_gains
                except Exception as e:
                    st.error(f"Fehler: {e}")

        # === 6. CONTRACTING-KOSTEN ===
        with st.expander("🔌 Contracting-Kosten (Alternative)", expanded=False):
            st.markdown(
                f"**Jährlicher Verbrauch:** {annual_consumption:,.2f} kWh")

            col1, col2, col3 = st.columns(3)
            with col1:
                base_fee = st.number_input(
                    "Grundgebühr (€/Jahr)",
                    min_value=0.0,
                    max_value=5000.0,
                    value=1200.0,
                    step=100.0,
                    key=f"{session_key_prefix}_base_fee"
                )
            with col2:
                consumption_price = st.number_input(
                    "Arbeitspreis (€/kWh)",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.15,
                    step=0.01,
                    key=f"{session_key_prefix}_consumption_price"
                )
            with col3:
                ppa_duration = st.number_input(
                    "Vertragslaufzeit (Jahre)",
                    min_value=5,
                    max_value=30,
                    value=20,
                    step=1,
                    key=f"{session_key_prefix}_ppa_duration"
                )

            include_contracting = st.checkbox(
                "In PDF aufnehmen",
                value=False,
                key=f"{session_key_prefix}_inc_contracting"
            )

            if annual_consumption > 0:
                try:
                    contracting = calculate_contracting_costs(
                        base_fee=base_fee,
                        consumption_price=consumption_price,
                        annual_consumption_kwh=annual_consumption,
                        ppa_duration_years=ppa_duration
                    )

                    st.success(
                        f"**Jährliche Kosten:** {contracting['annual_cost']:,.2f} €")
                    st.info(
                        f"Gesamt über {ppa_duration} Jahre: {
                            contracting['total_cost']:,.2f} €")

                    if include_contracting:
                        financial_results['contracting'] = contracting
                except Exception as e:
                    st.error(f"Fehler: {e}")

        # ZUSAMMENFASSUNG
        if financial_results:
            st.markdown("---")
            st.success(
                f"✅ **{len(financial_results)} Financial Tools** für PDF ausgewählt")

        return financial_results

    except ImportError as e:
        st.error(f"❌ financial_tools.py konnte nicht geladen werden: {e}")
        return {}
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Financial Tools: {e}")
        return {}
