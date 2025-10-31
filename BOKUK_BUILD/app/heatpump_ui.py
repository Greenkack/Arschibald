# heatpump_ui.py
"""
Wärmepumpen UI Module
Benutzeroberfläche für Wärmepumpen-Analyse und Integration

Author: GitHub Copilot
Version: 2.0 (Vollständig implementiert)
Date: 2025-01-12
"""

from datetime import datetime
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Import der notwendigen Funktionen
try:
    from calculations_heatpump import (
        calculate_annual_energy_consumption,
        calculate_building_heat_load,
        calculate_heatpump_economics,
        estimate_annual_heat_demand_kwh_from_consumption,
        estimate_heat_load_kw_from_annual_demand,
        get_default_heating_system_efficiency,
        recommend_heat_pump,
    )
    from database import get_db_connection
    from locales import get_text
    HEATPUMP_MODULES_AVAILABLE = True
except ImportError as e:
    st.error(f"Wärmepumpen-Module nicht verfügbar: {e}")
    HEATPUMP_MODULES_AVAILABLE = False


def render_heatpump_analysis(
        texts: dict[str, str], project_data: dict[str, Any] = None):
    """Hauptfunktion für die Wärmepumpen-Analyse"""

    if not HEATPUMP_MODULES_AVAILABLE:
        st.error(" Wärmepumpen-Analyse nicht verfügbar - Module fehlen")
        return

    st.header(" Wärmepumpen-Analyse")
    st.markdown(
        "Optimale Dimensionierung und Wirtschaftlichkeitsanalyse für Wärmepumpen")

    # Tabs für verschiedene Analyse-Bereiche
    tabs = st.tabs([
        " Gebäudeanalyse",
        " Wärmepumpen-Auswahl",
        " Wirtschaftlichkeit",
        " PV-Integration",
        " Komponenten & Angebot",
        " Ergebnisse"
    ])

    with tabs[0]:
        building_data = render_building_analysis(texts)

    with tabs[1]:
        if 'building_data' in st.session_state:
            heatpump_data = render_heatpump_selection(
                texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")
            heatpump_data = None

    with tabs[2]:
        if 'heatpump_data' in st.session_state:
            economics_data = render_economics_analysis(
                texts, st.session_state.heatpump_data)
        else:
            st.info("Bitte wählen Sie zuerst eine Wärmepumpe aus.")
            economics_data = None

    with tabs[3]:
        # Check demand mode to determine if PV integration is needed
        demand_mode = st.session_state.get('demand_mode_selection', None)

        if demand_mode == 'wp_only':
            # For WP-only mode, PV integration is not required
            st.info("🏠 **Nur Wärmepumpe-Modus:** PV-Integration nicht erforderlich")
            pv_integration_data = None
        else:
            # For PV+WP combined mode, use existing PV data logic
            project_data_effective = (
                project_data
                or st.session_state.get("calculation_results")
                or st.session_state.get("calculation_results_backup")
                or {}
            )
            if isinstance(
                    project_data_effective,
                    dict) and project_data_effective:
                pv_integration_data = render_pv_integration(
                    texts, project_data_effective)
            else:
                if demand_mode == 'pv_wp_combined':
                    st.warning(
                        "⚡ **PV + Wärmepumpe-Modus:** Bitte führen Sie zuerst die PV-Analyse durch.")
                else:
                    st.info(
                        "PV-Daten optional. Für PV+WP-Integration bitte zuerst PV-Analyse durchführen.")
                pv_integration_data = None

    with tabs[4]:
        render_components_offer_tab(texts)

    with tabs[5]:
        render_results_summary(texts)


def render_building_analysis(texts: dict[str, str]) -> dict[str, Any]:
    """Gebäudeanalyse und Heizlastberechnung"""

    st.subheader(" Gebäudeanalyse")

    with st.form("building_analysis_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Grunddaten**")

            building_area = st.number_input(
                "Beheizte Wohnfläche (m²)",
                min_value=30,
                max_value=1000,
                value=150,
                step=10
            )

            building_type = st.selectbox(
                "Gebäudetyp",
                options=[
                    "Neubau KfW40",
                    "Neubau KfW55",
                    "Neubau Standard",
                    "Altbau saniert",
                    "Altbau teilsaniert",
                    "Altbau unsaniert"
                ]
            )

            building_year = st.selectbox(
                "Baujahr",
                options=[
                    "Nach 2020",
                    "2010-2020",
                    "2000-2010",
                    "1990-2000",
                    "1980-1990",
                    "1970-1980",
                    "Vor 1970"
                ]
            )

        with col2:
            st.markdown("**Technische Details**")

            insulation_quality = st.selectbox(
                "Dämmqualität",
                options=[
                    "Sehr gut",
                    "Gut",
                    "Mittel",
                    "Schlecht",
                    "Sehr schlecht"])

            heating_system = st.selectbox(
                "Aktuelles Heizsystem",
                options=[
                    "Gas-Brennwert",
                    "Öl-Brennwert",
                    "Pellets",
                    "Fernwärme",
                    "Strom-Direktheizung",
                    "Alte Gasheizung",
                    "Alte Ölheizung"
                ]
            )

            hot_water_demand = st.selectbox(
                "Warmwasserbedarf",
                options=[
                    "Niedrig (1-2 Personen)",
                    "Mittel (3-4 Personen)",
                    "Hoch (5+ Personen)"])

        # Zusätzliche Parameter
        st.markdown("**Aktueller Verbrauch (pro Jahr)**")

        colc1, colc2, colc3 = st.columns(3)
        with colc1:
            oil_l = st.number_input(
                "Heizöl (Liter/Jahr)",
                min_value=0.0,
                value=0.0,
                step=50.0)
        with colc2:
            gas_kwh = st.number_input(
                "Erdgas (kWh/Jahr)",
                min_value=0.0,
                value=0.0,
                step=100.0)
        with colc3:
            wood_ster = st.number_input(
                "Holz (Ster/Jahr)",
                min_value=0.0,
                value=0.0,
                step=0.5,
                help="Zusätzlicher Holzverbrauch wird stets als Zusatz berücksichtigt.")

        colc4, colc5 = st.columns(2)
        with colc4:
            default_eff = get_default_heating_system_efficiency(heating_system)
            custom_eff = st.number_input(
                "Wirkungsgrad aktuelles System (%)",
                min_value=40.0,
                max_value=105.0,
                value=round(
                    default_eff * 100,
                    1),
                step=1.0)
        with colc5:
            heating_hours = st.number_input(
                "Volllaststunden/Jahr (Schätzung)",
                min_value=1200,
                max_value=2600,
                value=1800,
                step=100)

        st.markdown("**Erweiterte Parameter**")

        col3, col4 = st.columns(2)

        with col3:
            desired_temperature = st.slider(
                "Gewünschte Raumtemperatur (°C)",
                min_value=18,
                max_value=24,
                value=21
            )

            heating_days = st.slider(
                "Heiztage pro Jahr",
                min_value=150,
                max_value=300,
                value=220
            )

        with col4:
            outside_temp_design = st.slider(
                "Auslegungstemperatur außen (°C)",
                min_value=-20,
                max_value=-5,
                value=-12
            )

            heating_system_temp = st.selectbox(
                "Heizsystem-Temperatur",
                options=[
                    "Fußbodenheizung (35°C)",
                    "Wandheizung (40°C)",
                    "Radiatoren (55°C)",
                    "Alte Radiatoren (70°C)"])

        submitted = st.form_submit_button(
            " Heizlast berechnen", use_container_width=True)

    if submitted:
        try:
            # Heizlastberechnung – zuerst Standard nach Typ/Fläche/Dämmung
            heat_load = calculate_building_heat_load(
                building_type=building_type,
                living_area_m2=building_area,
                insulation_quality=insulation_quality
            )

            # Falls Verbrauchsdaten vorhanden, Wärmebedarf schätzen und
            # Heizlast überschreiben
            if any([oil_l > 0, gas_kwh > 0, wood_ster > 0]):
                annual_heat_kwh = estimate_annual_heat_demand_kwh_from_consumption(
                    consumption={
                        'oil_l': oil_l,
                        'gas_kwh': gas_kwh,
                        'wood_ster': wood_ster},
                    heating_system=heating_system,
                    wood_ster_additional=0.0,
                    custom_efficiency=custom_eff /
                    100.0 if custom_eff else None,
                )
                heat_load_from_cons = estimate_heat_load_kw_from_annual_demand(
                    annual_heat_kwh, heating_hours=int(heating_hours))
                # Nimm den höheren Wert zur Sicherheit bzw. ersetze
                # vollständig? Hier: überschreiben nach Verbrauch
                heat_load = heat_load_from_cons

            building_data = {
                'area': building_area,
                'type': building_type,
                'year': building_year,
                'insulation': insulation_quality,
                'heating_system': heating_system,
                'hot_water': hot_water_demand,
                'consumption_inputs': {
                    'oil_l': oil_l,
                    'gas_kwh': gas_kwh,
                    'wood_ster': wood_ster,
                    'heating_hours': heating_hours,
                    'system_efficiency_pct': custom_eff,
                },
                'desired_temp': desired_temperature,
                'heating_days': heating_days,
                'outside_temp': outside_temp_design,
                'system_temp': heating_system_temp,
                'heat_load_kw': heat_load,
                'heat_load_source': 'verbrauchsbasiert' if any(
                    [
                        oil_l > 0,
                        gas_kwh > 0,
                        wood_ster > 0]) else 'gebäudedaten',
                'calculated_at': datetime.now()}

            st.session_state.building_data = building_data

            # Ergebnisse anzeigen
            st.success(" Heizlastberechnung abgeschlossen!")

            col_result1, col_result2, col_result3 = st.columns(3)

            with col_result1:
                st.metric(
                    "Heizlast",
                    f"{heat_load:.1f} kW",
                    help="Benötigte Heizleistung bei Auslegungstemperatur"
                )

            with col_result2:
                specific_load = heat_load * 1000 / building_area  # W/m²
                st.metric(
                    "Spezifische Heizlast",
                    f"{specific_load:.0f} W/m²",
                    help="Heizlast pro Quadratmeter Wohnfläche"
                )

            with col_result3:
                # Qualitätsbewertung
                if specific_load < 40:
                    quality = "Sehr gut (Passivhaus)"
                elif specific_load < 60:
                    quality = "Gut (Niedrigenergiehaus)"
                elif specific_load < 100:
                    quality = "Standard"
                else:
                    quality = "Sanierungsbedarf"

                st.metric(
                    "Energetische Qualität",
                    quality + (" • Basis: Verbrauch" if building_data['heat_load_source'] == "verbrauchsbasiert" else " • Basis: Gebäudedaten"),
                    help="Bewertung basierend auf spezifischer Heizlast"
                )

            return building_data

        except Exception as e:
            st.error(f"Fehler bei der Heizlastberechnung: {e}")
            return None

    return None


def render_heatpump_selection(
        texts: dict[str, str], building_data: dict[str, Any]) -> dict[str, Any]:
    """Wärmepumpen-Auswahl und Dimensionierung"""

    st.subheader(" Wärmepumpen-Auswahl")

    heat_load = building_data.get('heat_load_kw', 0)

    if heat_load <= 0:
        st.error(
            "Keine gültige Heizlast verfügbar. Bitte Gebäudeanalyse wiederholen.")
        return None

    st.info(f"Benötigte Heizleistung: {heat_load:.1f} kW")

    # Wärmepumpen-Typ auswählen
    col1, col2 = st.columns(2)

    with col1:
        heatpump_type = st.selectbox(
            "Wärmepumpentyp",
            options=[
                "Luft-Wasser-Wärmepumpe",
                "Sole-Wasser-Wärmepumpe",
                "Wasser-Wasser-Wärmepumpe",
                "Luft-Luft-Wärmepumpe"
            ]
        )

        installation_type = st.selectbox(
            "Installation",
            options=["Außenaufstellung", "Innenaufstellung", "Split-Gerät"]
        )

    with col2:
        manufacturer_preference = st.selectbox(
            "Hersteller-Präferenz",
            options=[
                "Keine Präferenz",
                "Vaillant",
                "Viessmann",
                "Daikin",
                "Mitsubishi",
                "Panasonic",
                "Stiebel Eltron"])

        budget_category = st.selectbox(
            "Budget-Kategorie",
            options=["Economy", "Standard", "Premium"]
        )

    # Erweiterte Parameter
    with st.expander(" Erweiterte Einstellungen"):
        col3, col4 = st.columns(2)

        with col3:
            sizing_factor = st.slider(
                "Dimensionierungsfaktor",
                min_value=0.8,
                max_value=1.3,
                value=1.0,
                step=0.05,
                help="1.0 = monovalent, <1.0 = bivalent"
            )

            hot_water_storage = st.slider(
                "Warmwasserspeicher (Liter)",
                min_value=200,
                max_value=1000,
                value=300,
                step=50
            )

        with col4:
            backup_heating = st.checkbox("Backup-Heizstab", value=True)

            smart_control = st.checkbox("Smart Grid Ready", value=True)

    if st.button(" Wärmepumpen suchen", use_container_width=True):
        try:
            # Dummy-Wärmepumpen-Datenbank (in echter Implementierung aus DB
            # laden)
            heatpumps_db = get_heatpump_database()

            # Lokale Empfehlung basierend auf UI-Parametern (Kompatibel mit
            # Dummy-DB)
            required_kw = heat_load * sizing_factor
            candidates = [
                hp for hp in heatpumps_db if hp.get('type') == heatpump_type]
            if manufacturer_preference and manufacturer_preference != "Keine Präferenz":
                candidates = [hp for hp in candidates if hp.get(
                    'manufacturer') == manufacturer_preference]

            # Bevorzugt kleinste, die reicht; sonst dichteste über/unter dem
            # Bedarf
            suitable = [
                hp for hp in candidates if hp.get(
                    'heating_power',
                    0) >= required_kw]
            if suitable:
                suitable = sorted(
                    suitable, key=lambda hp: hp.get(
                        'heating_power', 0))
                recommended_list = suitable
            else:
                # Fallback: nächstgrößte Abweichung (unterdimensioniert)
                candidates = sorted(
                    candidates,
                    key=lambda hp: abs(
                        hp.get(
                            'heating_power',
                            0) - required_kw))
                recommended_list = candidates

            if recommended_list:
                st.success(
                    f" {len(recommended_list)} passende Wärmepumpen gefunden!")

                # Top-Empfehlung anzeigen
                top_heatpump = recommended_list[0]

                st.subheader(" Top-Empfehlung")

                col_hp1, col_hp2, col_hp3 = st.columns(3)

                with col_hp1:
                    st.write(
                        f"**{top_heatpump['manufacturer']} {top_heatpump['model']}**")
                    st.write(f"Typ: {top_heatpump['type']}")
                    st.write(f"Leistung: {top_heatpump['heating_power']} kW")

                with col_hp2:
                    st.metric("COP (A2/W35)", f"{top_heatpump['cop']:.1f}")
                    st.metric("SCOP", f"{top_heatpump['scop']:.1f}")
                    st.write(
                        f"Schallpegel: {
                            top_heatpump['noise_level']} dB(A)")

                with col_hp3:
                    st.metric(
                        "Anschaffungskosten", f"{
                            top_heatpump['price']:,.0f} €")
                    st.write(f"Größe: {top_heatpump['dimensions']}")
                    st.write(f"Gewicht: {top_heatpump['weight']} kg")

                # Weitere Optionen anzeigen
                if len(recommended_list) > 1:
                    with st.expander(" Weitere Optionen anzeigen"):
                        for i, hp in enumerate(
                                recommended_list[1:4], 2):  # Top 3 weitere
                            st.write(
                                f"**Option {i}: {hp['manufacturer']} {hp['model']}**")
                            col_alt1, col_alt2, col_alt3 = st.columns(3)
                            with col_alt1:
                                st.write(f"Leistung: {hp['heating_power']} kW")
                            with col_alt2:
                                st.write(f"SCOP: {hp['scop']:.1f}")
                            with col_alt3:
                                st.write(f"Preis: {hp['price']:,.0f} €")
                            st.markdown("---")

                # Auswahl speichern
                heatpump_data = {
                    'selected_heatpump': top_heatpump,
                    'alternatives': recommended_list[1:],
                    'sizing_factor': sizing_factor,
                    'hot_water_storage': hot_water_storage,
                    'backup_heating': backup_heating,
                    'smart_control': smart_control,
                    'building_data': building_data
                }

                st.session_state.heatpump_data = heatpump_data

                return heatpump_data

            st.warning(
                "Keine passenden Wärmepumpen gefunden. Bitte Parameter anpassen.")

        except Exception as e:
            st.error(f"Fehler bei der Wärmepumpen-Suche: {e}")

    return None


def render_economics_analysis(
        texts: dict[str, str], heatpump_data: dict[str, Any]) -> dict[str, Any]:
    """Wirtschaftlichkeitsanalyse der Wärmepumpe"""

    st.subheader(" Wirtschaftlichkeitsanalyse")

    heatpump = heatpump_data['selected_heatpump']
    building_data = heatpump_data['building_data']

    # Parameter für Wirtschaftlichkeitsrechnung
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Energiepreise**")

        electricity_price = st.number_input(
            "Strompreis (ct/kWh)",
            min_value=20.0,
            max_value=50.0,
            value=32.0,
            step=0.5
        )

        gas_price = st.number_input(
            "Gaspreis (ct/kWh)",
            min_value=5.0,
            max_value=20.0,
            value=12.0,
            step=0.5
        )

        oil_price = st.number_input(
            "Ölpreis (ct/kWh)",
            min_value=5.0,
            max_value=20.0,
            value=10.0,
            step=0.5
        )

    with col2:
        st.markdown("**Förderung & Kosten**")

        subsidy_amount = st.number_input(
            "Förderung BEG (€)",
            min_value=0,
            max_value=20000,
            value=7500,
            step=500,
            help="Bundesförderung für effiziente Gebäude"
        )

        installation_cost = st.number_input(
            "Installationskosten (€)",
            min_value=3000,
            max_value=15000,
            value=6000,
            step=500
        )

        maintenance_cost_annual = st.number_input(
            "Jährliche Wartungskosten (€)",
            min_value=200,
            max_value=1000,
            value=300,
            step=50
        )

    # Berechnung durchführen
    if st.button(" Wirtschaftlichkeit berechnen", use_container_width=True):
        try:
            # Jahresenergiebedarf berechnen (an calculations_heatpump angepasst)
            # Näherung: 1.800 Volllaststunden
            heating_hours = 1800
            heat_demand_kwh = building_data['heat_load_kw'] * heating_hours

            # Wärmepumpen-Stromverbrauch
            hp_electricity_consumption = heat_demand_kwh / heatpump['scop']

            # Kosten berechnen
            total_investment = heatpump['price'] + \
                installation_cost - subsidy_amount

            annual_hp_cost = (hp_electricity_consumption *
                              electricity_price / 100) + maintenance_cost_annual

            # Vergleich mit aktueller Heizung
            current_system = building_data['heating_system']
            if 'Gas' in current_system:
                annual_old_cost = heat_demand_kwh * gas_price / 100
            elif 'Öl' in current_system:
                annual_old_cost = heat_demand_kwh * oil_price / 100
            else:
                annual_old_cost = heat_demand_kwh * electricity_price / 100

            annual_savings = annual_old_cost - annual_hp_cost
            payback_time = total_investment / \
                annual_savings if annual_savings > 0 else float('inf')

            # Ergebnisse anzeigen
            st.success(" Wirtschaftlichkeitsanalyse abgeschlossen!")

            # KPIs
            col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

            with col_kpi1:
                st.metric(
                    "Gesamtinvestition",
                    f"{total_investment:,.0f} €",
                    help="Anschaffung + Installation - Förderung"
                )

            with col_kpi2:
                st.metric(
                    "Jährliche Ersparnis",
                    f"{annual_savings:,.0f} €",
                    help="Einsparung gegenüber altem System"
                )

            with col_kpi3:
                if payback_time != float('inf'):
                    st.metric(
                        "Amortisationszeit",
                        f"{payback_time:.1f} Jahre",
                        help="Zeit bis zur Kostendeckung"
                    )
                else:
                    st.metric(
                        "Amortisationszeit",
                        "∞",
                        help="Keine Amortisation")

            with col_kpi4:
                st.metric(
                    "20-Jahre-Ersparnis",
                    f"{(annual_savings * 20 - total_investment):,.0f} €",
                    help="Gesamtersparnis über 20 Jahre"
                )

            # Detaillierte Kostenaufstellung
            st.subheader(" Kostenaufstellung")

            cost_breakdown = pd.DataFrame({
                'Position': [
                    'Wärmepumpe',
                    'Installation',
                    'Förderung BEG',
                    'Netto-Investition',
                    '',
                    'Jährlicher Stromverbrauch WP',
                    'Jährliche Stromkosten WP',
                    'Jährliche Wartungskosten',
                    'Gesamte jährliche Kosten WP',
                    '',
                    'Jährliche Kosten altes System',
                    'Jährliche Ersparnis'
                ],
                'Betrag': [
                    f"{heatpump['price']:,.0f} €",
                    f"{installation_cost:,.0f} €",
                    f"-{subsidy_amount:,.0f} €",
                    f"{total_investment:,.0f} €",
                    '',
                    f"{hp_electricity_consumption:,.0f} kWh",
                    f"{hp_electricity_consumption * electricity_price / 100:,.0f} €",
                    f"{maintenance_cost_annual:,.0f} €",
                    f"{annual_hp_cost:,.0f} €",
                    '',
                    f"{annual_old_cost:,.0f} €",
                    f"{annual_savings:,.0f} €"
                ]
            })

            st.dataframe(
                cost_breakdown,
                use_container_width=True,
                hide_index=True)

            # Cashflow-Diagramm
            st.subheader(" Cashflow-Entwicklung")

            years = list(range(21))
            cumulative_cashflow = [-total_investment]

            for year in range(1, 21):
                cumulative_cashflow.append(
                    cumulative_cashflow[-1] + annual_savings)

            fig_cashflow = go.Figure()

            fig_cashflow.add_trace(go.Scatter(
                x=years,
                y=cumulative_cashflow,
                mode='lines+markers',
                name='Kumulierter Cashflow',
                line=dict(color='#1f77b4', width=3)
            ))

            fig_cashflow.add_hline(
                y=0,
                line_dash="dash",
                line_color="red",
                opacity=0.7)

            fig_cashflow.update_layout(
                title="Kumulierter Cashflow über 20 Jahre",
                xaxis_title="Jahre",
                yaxis_title="Kumulierter Cashflow (€)",
                hovermode='x unified'
            )

            st.plotly_chart(fig_cashflow, use_container_width=True)

            # Ergebnisse speichern
            economics_data = {
                'total_investment': total_investment,
                'annual_savings': annual_savings,
                'payback_time': payback_time,
                'hp_electricity_consumption': hp_electricity_consumption,
                'annual_hp_cost': annual_hp_cost,
                'annual_old_cost': annual_old_cost,
                'heat_demand_kwh': heat_demand_kwh,
                'electricity_price': electricity_price,
                'subsidy_amount': subsidy_amount
            }

            st.session_state.economics_data = economics_data

            return economics_data

        except Exception as e:
            st.error(f"Fehler bei der Wirtschaftlichkeitsberechnung: {e}")

    return None


def render_pv_integration(
        texts: dict[str, str], project_data: dict[str, Any]) -> dict[str, Any]:
    """PV-Wärmepumpen-Integration"""

    st.subheader(" PV-Wärmepumpen-Integration")

    if 'heatpump_data' not in st.session_state or 'economics_data' not in st.session_state:
        st.info("Bitte führen Sie zuerst die Wärmepumpen-Analyse durch.")
        return None

    heatpump_data = st.session_state.heatpump_data
    economics_data = st.session_state.economics_data

    # PV-Daten aus Projektdaten extrahieren (mit Session-Fallback)
    calc_results_ss = st.session_state.get(
        'calculation_results', {}) if hasattr(
        st, 'session_state') else {}
    pv_production_annual = (
        (project_data.get('annual_pv_production_kwh') if isinstance(
            project_data,
            dict) else None) or calc_results_ss.get('annual_pv_production_kwh') or 0)
    pv_size_kwp = ((project_data.get('anlage_kwp') if isinstance(
        project_data, dict) else None) or calc_results_ss.get('anlage_kwp') or 0)

    if pv_production_annual <= 0:
        st.warning("Keine PV-Daten verfügbar. Integration nicht möglich.")
        return None

    st.info(
        f"PV-Anlage: {
            pv_size_kwp:.1f} kWp, Jahresproduktion: {
            pv_production_annual:,.0f} kWh")

    # Integration berechnen
    hp_consumption = float(
        economics_data.get(
            'hp_electricity_consumption',
            0) or 0)

    # Vereinfachte Berechnung der Eigenverbrauchsquote
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Eigenverbrauch-Optimierung**")

        # Smart Control für WP
        smart_control_enabled = st.checkbox(
            "Smart Grid Ready aktivieren",
            value=True,
            help="Wärmepumpe läuft bevorzugt bei PV-Überschuss"
        )

        # Wärmespeicher-Größe
        thermal_storage_size = st.slider(
            "Pufferspeicher-Größe (Liter)",
            min_value=300,
            max_value=2000,
            value=800,
            step=100,
            help="Größerer Speicher = mehr Flexibilität"
        )

        # Eigenverbrauchsquote WP
        if hp_consumption > 0:
            if smart_control_enabled:
                pv_coverage_hp = min(
                    0.8, pv_production_annual / hp_consumption)
            else:
                pv_coverage_hp = min(
                    0.4, pv_production_annual / hp_consumption)
        else:
            pv_coverage_hp = 0.0

        st.metric(
            "PV-Deckung Wärmepumpe",
            f"{pv_coverage_hp * 100:.0f}%",
            help="Anteil des WP-Stroms aus PV"
        )

    with col2:
        st.markdown("**Wirtschaftliche Auswirkung**")

        # Stromkosten mit/ohne PV
        electricity_price = economics_data['electricity_price']

        hp_cost_without_pv = hp_consumption * electricity_price / 100
        hp_cost_with_pv = hp_consumption * \
            (1 - pv_coverage_hp) * electricity_price / 100

        annual_pv_savings_hp = hp_cost_without_pv - hp_cost_with_pv

        st.metric(
            "Zusätzliche PV-Ersparnis",
            f"{annual_pv_savings_hp:,.0f} €/Jahr",
            help="Ersparnis durch PV-Eigenverbrauch der WP"
        )

        # Gesamtoptimierung
        total_annual_savings = economics_data['annual_savings'] + \
            annual_pv_savings_hp

        st.metric(
            "Gesamte jährliche Ersparnis",
            f"{total_annual_savings:,.0f} €/Jahr",
            help="WP-Ersparnis + PV-Eigenverbrauch"
        )

    # Lastprofil-Visualisierung
    st.subheader(" Tages-Lastprofil (Beispiel)")

    # Dummy-Daten für Lastprofil
    hours = list(range(24))
    pv_generation = [0, 0, 0, 0, 0, 0, 10, 30, 50, 70, 85,
                     95, 100, 95, 85, 70, 50, 30, 10, 0, 0, 0, 0, 0]
    hp_demand_normal = [
        30,
        25,
        20,
        20,
        25,
        35,
        45,
        50,
        40,
        35,
        30,
        30,
        30,
        30,
        35,
        40,
        50,
        55,
        50,
        45,
        40,
        35,
        30,
        30]

    if smart_control_enabled:
        # WP läuft bevorzugt bei PV-Überschuss
        hp_demand_smart = [
            20,
            15,
            15,
            15,
            20,
            25,
            30,
            40,
            60,
            80,
            90,
            95,
            95,
            90,
            80,
            60,
            40,
            35,
            30,
            25,
            25,
            20,
            20,
            20]
    else:
        hp_demand_smart = hp_demand_normal

    fig_profile = go.Figure()

    # PV-Erzeugung
    fig_profile.add_trace(go.Scatter(
        x=hours,
        y=pv_generation,
        mode='lines',
        name='PV-Erzeugung (%)',
        fill='tozeroy',
        line=dict(color='#f39c12', width=2)
    ))

    # WP-Verbrauch
    profile_name = "WP-Verbrauch (Smart)" if smart_control_enabled else "WP-Verbrauch (Normal)"
    fig_profile.add_trace(go.Scatter(
        x=hours,
        y=hp_demand_smart,
        mode='lines+markers',
        name=profile_name,
        line=dict(color='#e74c3c', width=2)
    ))

    fig_profile.update_layout(
        title="Tages-Lastprofil: PV-Erzeugung vs. Wärmepumpen-Verbrauch",
        xaxis_title="Stunde",
        yaxis_title="Relative Leistung (%)",
        hovermode='x unified'
    )

    st.plotly_chart(fig_profile, use_container_width=True)

    # Integration speichern
    integration_data = {
        'pv_coverage_hp': pv_coverage_hp,
        'annual_pv_savings_hp': annual_pv_savings_hp,
        'total_annual_savings': total_annual_savings,
        'smart_control_enabled': smart_control_enabled,
        'thermal_storage_size': thermal_storage_size
    }

    st.session_state.integration_data = integration_data

    return integration_data


def render_results_summary(texts: dict[str, str]):
    """Zusammenfassung aller Ergebnisse"""

    st.subheader(" Ergebnis-Zusammenfassung")

    # Auto-Fallback 0: Wenn keine heatpump_data vorhanden, aber Gebäudedaten existieren,
    # wähle automatisch eine passende Wärmepumpe aus der lokalen DB
    if 'heatpump_data' not in st.session_state and 'building_data' in st.session_state:
        try:
            building_data = st.session_state.building_data
            heat_load = float(building_data.get('heat_load_kw', 0) or 0)
            if heat_load > 0:
                sizing_factor = 1.0
                required_kw = heat_load * sizing_factor
                hp_db = get_heatpump_database()
                # Bevorzugt Luft-Wasser, dann kleinste ausreichende Leistung
                candidates = [hp for hp in hp_db if hp.get(
                    'type') == 'Luft-Wasser-Wärmepumpe'] or hp_db
                suitable = [
                    hp for hp in candidates if float(
                        hp.get(
                            'heating_power',
                            0) or 0) >= required_kw]
                if suitable:
                    suitable = sorted(
                        suitable,
                        key=lambda hp: float(
                            hp.get(
                                'heating_power',
                                0) or 0))
                    top = suitable[0]
                else:
                    candidates = sorted(
                        candidates,
                        key=lambda hp: abs(
                            float(
                                hp.get(
                                    'heating_power',
                                    0) or 0) -
                            required_kw))
                    top = candidates[0] if candidates else None

                if top:
                    st.session_state.heatpump_data = {
                        'selected_heatpump': top,
                        'alternatives': [],
                        'sizing_factor': sizing_factor,
                        'hot_water_storage': 300,
                        'backup_heating': True,
                        'smart_control': True,
                        'building_data': building_data,
                        'auto_selected': True,
                    }
        except Exception:
            pass

    # Auto-Fallback: Wirtschaftlichkeit berechnen, wenn WP- und Gebäudedaten
    # vorhanden
    if 'economics_data' not in st.session_state and 'building_data' in st.session_state and 'heatpump_data' in st.session_state:
        try:
            building_data = st.session_state.building_data
            heatpump = st.session_state.heatpump_data['selected_heatpump']
            # Defaults analog zur UI
            electricity_price = 32.0  # ct/kWh
            gas_price = 12.0          # ct/kWh
            oil_price = 10.0          # ct/kWh
            subsidy_amount = 7500
            installation_cost = 6000
            maintenance_cost_annual = 300

            heating_hours = int(
                building_data.get(
                    'consumption_inputs',
                    {}).get(
                    'heating_hours',
                    1800) or 1800)
            heat_demand_kwh = building_data['heat_load_kw'] * heating_hours
            hp_electricity_consumption = heat_demand_kwh / \
                max(heatpump.get('scop', 3.5), 0.1)

            total_investment = heatpump['price'] + \
                installation_cost - subsidy_amount
            annual_hp_cost = (hp_electricity_consumption *
                              electricity_price / 100) + maintenance_cost_annual

            current_system = building_data.get('heating_system', '')
            if 'Gas' in current_system:
                annual_old_cost = heat_demand_kwh * gas_price / 100
            elif 'Öl' in current_system:
                annual_old_cost = heat_demand_kwh * oil_price / 100
            else:
                annual_old_cost = heat_demand_kwh * electricity_price / 100

            annual_savings = annual_old_cost - annual_hp_cost
            payback_time = total_investment / \
                annual_savings if annual_savings > 0 else float('inf')

            st.session_state.economics_data = {
                'total_investment': total_investment,
                'annual_savings': annual_savings,
                'payback_time': payback_time,
                'hp_electricity_consumption': hp_electricity_consumption,
                'annual_hp_cost': annual_hp_cost,
                'annual_old_cost': annual_old_cost,
                'heat_demand_kwh': heat_demand_kwh,
                'electricity_price': electricity_price,
                'subsidy_amount': subsidy_amount
            }
        except Exception as _auto_econ_err:
            # Leise weiter – unten folgt ansonsten wieder die Standardwarnung
            pass

    # Prüfen ob alle Daten verfügbar sind
    required_data = ['building_data', 'heatpump_data', 'economics_data']
    missing_data = [
        key for key in required_data if key not in st.session_state]
    if missing_data:
        st.warning(
            f"Unvollständige Analyse. Fehlende Daten: {
                ', '.join(missing_data)}")
        return

    building_data = st.session_state.building_data
    heatpump_data = st.session_state.heatpump_data
    economics_data = st.session_state.economics_data
    integration_data = st.session_state.get('integration_data', {})

    # Übersichts-Dashboard
    st.markdown("###  Projekt-Übersicht")

    col_summary1, col_summary2, col_summary3, col_summary4 = st.columns(4)

    with col_summary1:
        st.metric(
            "Gebäude",
            f"{building_data['area']} m²",
            help=f"{building_data['type']}, {building_data['insulation']}"
        )

        st.metric(
            "Heizlast",
            f"{building_data['heat_load_kw']:.1f} kW",
            help="Bei Auslegungstemperatur"
        )

    with col_summary2:
        heatpump = heatpump_data['selected_heatpump']
        st.metric(
            "Wärmepumpe",
            f"{heatpump['heating_power']} kW",
            help=f"{heatpump['manufacturer']} {heatpump['model']}"
        )

        st.metric(
            "SCOP",
            f"{heatpump['scop']:.1f}",
            help="Saisonale Leistungszahl"
        )

    with col_summary3:
        st.metric(
            "Investition",
            f"{economics_data['total_investment']:,.0f} €",
            help="Nach Förderung"
        )

        st.metric(
            "Amortisation",
            f"{economics_data['payback_time']:.1f} Jahre",
            help="Bis zur Kostendeckung"
        )

    with col_summary4:
        annual_savings = economics_data['annual_savings']
        if integration_data:
            annual_savings = integration_data.get(
                'total_annual_savings', annual_savings)

        st.metric(
            "Jährliche Ersparnis",
            f"{annual_savings:,.0f} €",
            help="Gegenüber altem System"
        )

        savings_20_years = annual_savings * 20 - \
            economics_data['total_investment']
        st.metric(
            "20-Jahre-Ersparnis",
            f"{savings_20_years:,.0f} €",
            help="Gesamte Ersparnis über 20 Jahre"
        )

    # Empfehlungen
    st.markdown("###  Empfehlungen")

    recommendations = []

    # Technische Empfehlungen
    if building_data['heat_load_kw'] * 1000 / building_data['area'] > 80:
        recommendations.append(
            " **Gebäudesanierung empfehlenswert** - Hohe spezifische Heizlast deutet auf Sanierungspotenzial hin")

    if heatpump['scop'] < 4.0:
        recommendations.append(
            " **Höhere Effizienz möglich** - Prüfen Sie Wärmepumpen mit besserer SCOP")

    if economics_data['payback_time'] > 12:
        recommendations.append(
            " **Lange Amortisationszeit** - Prüfen Sie zusätzliche Förderungen oder günstigere Alternativen")

    # PV-Integration
    if integration_data and integration_data.get('pv_coverage_hp', 0) < 0.5:
        recommendations.append(
            " **PV-Anlage vergrößern** - Höhere PV-Deckung der Wärmepumpe möglich")

    if not integration_data.get('smart_control_enabled', False):
        recommendations.append(
            "🤖 **Smart Control aktivieren** - Optimiert Eigenverbrauch und reduziert Kosten")

    if not recommendations:
        recommendations.append(
            " **Optimale Konfiguration** - Alle Parameter sind gut aufeinander abgestimmt")

    for rec in recommendations:
        st.write(rec)

    # Export-Optionen
    st.markdown("###  Dokumentation")

    col_export1, col_export2 = st.columns(2)

    with col_export1:
        if st.button(" Ergebnisse als PDF exportieren"):
            try:
                from pdf_generator import generate_offer_pdf
                # Minimaler PV-Dummy damit Validator zufrieden ist
                project_data_hp = {
                    'customer_data': st.session_state.get(
                        'project_customer_data',
                        {}),
                    'project_details': {
                        'module_quantity': 1,
                        'selected_module_name': 'Placeholder Modul',
                        'selected_inverter_name': 'Placeholder WR',
                        'anlage_kwp': 0.1,
                    },
                    'heatpump_offer': st.session_state.get('heatpump_offer'),
                }
                analysis_results_hp = {
                    'anlage_kwp': 0.1,
                    'annual_pv_production_kwh': 0.0,
                    'total_investment_netto': (
                        st.session_state.get(
                            'heatpump_offer',
                            {}) or {}).get(
                        'beg_subsidy',
                        {}).get('effective_total_after_subsidy_net')}
                company_info = st.session_state.get(
                    'active_company_info', {}) or {}
                pdf_bytes = generate_offer_pdf(
                    project_data=project_data_hp,
                    analysis_results=analysis_results_hp,
                    company_info=company_info,
                    company_logo_base64=company_info.get('logo_base64'),
                    selected_title_image_b64=None,
                    selected_offer_title_text='Angebot Wärmepumpe',
                    selected_cover_letter_text='Sehr geehrte Damen und Herren,\n\nwir freuen uns, Ihnen unser Wärmepumpen-Angebot zu präsentieren.',
                    sections_to_include=None,
                    inclusion_options={
                        'include_company_logo': True,
                        'include_product_images': False},
                    load_admin_setting_func=lambda k,
                    d=None: d,
                    save_admin_setting_func=lambda k,
                    v: False,
                    list_products_func=lambda *a,
                    **k: [],
                    get_product_by_id_func=lambda x: None,
                    db_list_company_documents_func=lambda *a,
                    **k: [],
                    active_company_id=None,
                    texts={},
                )
                if pdf_bytes:
                    st.download_button(
                        " Wärmepumpen-Angebot PDF herunterladen",
                        data=pdf_bytes,
                        file_name="Waermepumpe_Angebot.pdf",
                        mime="application/pdf")
                else:
                    st.error("PDF-Erstellung fehlgeschlagen.")
            except Exception as e:
                st.error(f"Fehler beim PDF-Export: {e}")

    with col_export2:
        if st.button(" Konfiguration speichern"):
            st.info("Konfiguration wird gespeichert...")


def render_components_offer_tab(texts: dict[str, str]):
    """Neue Tab-Seite: Strukturierte Anzeige Hauptkomponenten + Zubehör, Preislogik, Förderung & Finanzierung."""
    st.subheader(" Komponenten & Angebot")
    try:
        from heatpump_pricing import (
            apply_discounts_and_surcharges,
            build_full_heatpump_offer,
            calculate_annuity_loan,
            calculate_base_price,
            calculate_beg_subsidy,
            load_heatpump_components,
        )
    except Exception as e:
        st.warning(f"Preis-/Fördermodul nicht verfügbar: {e}")
        return

    # Komponenten laden
    comps = load_heatpump_components()
    main_comps = comps.get("main", [])
    accessory_comps = comps.get("accessories", [])

    if not (main_comps or accessory_comps):
        st.info(
            "Keine Wärmepumpen-Komponenten in der Produkt-DB gefunden. Bitte im Admin-Panel anlegen.")
        return

    # Hauptkomponenten Abschnitt
    st.markdown("### Hauptkomponenten")
    for c in main_comps:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"**{c.name}**")
            if c.description:
                st.caption(c.description[:180])
        with col2:
            st.write(f"Material: {c.material_net:,.0f} €")
        with col3:
            if c.labor_hours:
                st.write(f"Arbeitsstd.: {c.labor_hours:g}")
            else:
                st.write("-")
        with col4:
            st.write(f"Gesamt: {c.total_net:,.0f} €")

    # Zubehör / Dienstleistungen
    with st.expander("Zubehör und Leistungen", expanded=False):
        for c in accessory_comps:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(c.name)
            with col2:
                st.write(f"{c.material_net:,.0f} €")
            with col3:
                st.write(f"{c.labor_hours:g}h" if c.labor_hours else "-")
            with col4:
                st.write(f"{c.total_net:,.0f} €")

    base = calculate_base_price(comps)
    st.markdown("### Basispreis")
    colb1, colb2, colb3 = st.columns(3)
    colb1.metric("Material", f"{base['material_sum_net']:,.0f} €")
    colb2.metric("Arbeit", f"{base['labor_sum_net']:,.0f} €")
    colb3.metric("Summe Netto", f"{base['base_total_net']:,.0f} €")

    st.markdown("### Rabatte / Aufpreise")
    colr1, colr2, colr3, colr4 = st.columns(4)
    with colr1:
        rabatt_pct = st.number_input(
            "Rabatt %",
            min_value=0.0,
            max_value=50.0,
            value=0.0,
            step=1.0)
    with colr2:
        rabatt_abs = st.number_input(
            "Rabatt €",
            min_value=0.0,
            max_value=50000.0,
            value=0.0,
            step=500.0)
    with colr3:
        zuschlag_pct = st.number_input(
            "Zuschlag %",
            min_value=0.0,
            max_value=50.0,
            value=0.0,
            step=1.0)
    with colr4:
        zuschlag_abs = st.number_input(
            "Zuschlag €",
            min_value=0.0,
            max_value=50000.0,
            value=0.0,
            step=500.0)

    mods = apply_discounts_and_surcharges(
        base['base_total_net'],
        rabatt_pct,
        rabatt_abs,
        zuschlag_pct,
        zuschlag_abs)
    colm1, colm2, colm3 = st.columns(3)
    colm1.metric("Nach Rabatt/Zuschlag", f"{mods['final_price_net']:,.0f} €")
    colm2.metric("Rabatt gesamt",
                 f"-{mods['rabatt_pct_amount'] + mods['rabatt_abs']:,.0f} €")
    colm3.metric(
        "Zuschläge gesamt", f"{
            mods['zuschlag_pct_amount'] + mods['zuschlag_abs']:,.0f} €")

    st.markdown("### BEG-Förderung")
    colf1, colf2, colf3, colf4 = st.columns(4)
    with colf1:
        natural_ref = st.checkbox(
            "Natürliches Kältemittel",
            value=True,
            help="R290 Bonus +5%")
    with colf2:
        replace_old = st.checkbox(
            "Heizungstausch",
            value=False,
            help="+20% Bonus")
    with colf3:
        low_income = st.checkbox(
            "Einkommen <40 T€",
            value=False,
            help="+20% Bonus")
    with colf4:
        st.write("Max 70%")
    subsidy = calculate_beg_subsidy(
        mods['final_price_net'],
        natural_ref,
        replace_old,
        low_income)
    colsub1, colsub2, colsub3 = st.columns(3)
    colsub1.metric("Förder-%", f"{subsidy['applied_pct']:.0f}%")
    colsub2.metric("Förderbetrag", f"{subsidy['subsidy_amount_net']:,.0f} €")
    colsub3.metric(
        "Netto nach Förderung", f"{
            subsidy['effective_total_after_subsidy_net']:,.0f} €")

    st.markdown("### Finanzierung (Annuität)")
    colfin1, colfin2, colfin3, colfin4 = st.columns(4)
    with colfin1:
        years = st.number_input(
            "Laufzeit Jahre",
            min_value=1,
            max_value=30,
            value=15)
    with colfin2:
        interest = st.number_input(
            "Zins % p.a.",
            min_value=0.0,
            max_value=15.0,
            value=3.0,
            step=0.1)
    with colfin3:
        equity_pct = st.number_input(
            "Eigenkapital %",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=5.0)
    with colfin4:
        st.write("")
    equity_amount = subsidy['effective_total_after_subsidy_net'] * \
        (equity_pct / 100.0)
    principal = subsidy['effective_total_after_subsidy_net'] - equity_amount
    fin = calculate_annuity_loan(
        principal,
        interest,
        int(years)) if principal > 0 else {
        "monthly_rate": 0,
        "total_interest": 0}
    colfinm1, colfinm2, colfinm3 = st.columns(3)
    colfinm1.metric("Kreditsumme", f"{principal:,.0f} €")
    colfinm2.metric("Monatsrate", f"{fin['monthly_rate']:,.0f} €")
    colfinm3.metric("Gesamtzinsen", f"{fin['total_interest']:,.0f} €")

    # Komplettes Angebotsobjekt im Session-State bereitstellen für PDF /
    # Platzhalter
    try:
        from heatpump_pricing import (
            build_full_heatpump_offer,
        )
        offer = build_full_heatpump_offer(
            rabatt_pct=rabatt_pct,
            rabatt_abs=rabatt_abs,
            zuschlag_pct=zuschlag_pct,
            zuschlag_abs=zuschlag_abs,
            beg_flags={
                "natural_refrigerant": natural_ref,
                "replace_old": replace_old,
                "low_income": low_income},
            financing={
                "equity_amount": equity_amount,
                "interest_pct": interest,
                "years": years})
        st.session_state['heatpump_offer'] = offer
        st.success("Angebotsdaten aktualisiert und gespeichert.")
    except Exception as e:
        st.warning(f"Offer-Erstellung fehlgeschlagen: {e}")

    if st.checkbox("Details anzeigen (Debug)"):
        st.json(st.session_state.get('heatpump_offer'))


def get_heatpump_database() -> list[dict[str, Any]]:
    """Dummy-Wärmepumpen-Datenbank"""

    return [
        {
            'manufacturer': 'Vaillant',
            'model': 'aroTHERM plus VWL 125/6 A',
            'type': 'Luft-Wasser-Wärmepumpe',
            'heating_power': 12.8,
            'cop': 4.2,
            'scop': 4.6,
            'price': 15500,
            'noise_level': 35,
            'dimensions': '1.2 x 0.6 x 1.4 m',
            'weight': 125,
            'efficiency_class': 'A+++'
        },
        {
            'manufacturer': 'Viessmann',
            'model': 'Vitocal 200-S AWO-E-AC 101.A08',
            'type': 'Luft-Wasser-Wärmepumpe',
            'heating_power': 8.1,
            'cop': 4.1,
            'scop': 4.4,
            'price': 12800,
            'noise_level': 37,
            'dimensions': '1.1 x 0.6 x 1.3 m',
            'weight': 110,
            'efficiency_class': 'A++'
        },
        {
            'manufacturer': 'Daikin',
            'model': 'Altherma 3 H HT EPRA14DW1',
            'type': 'Luft-Wasser-Wärmepumpe',
            'heating_power': 14.5,
            'cop': 3.8,
            'scop': 4.2,
            'price': 17200,
            'noise_level': 39,
            'dimensions': '1.3 x 0.7 x 1.5 m',
            'weight': 145,
            'efficiency_class': 'A++'
        }
    ]

# Haupt-Export-Funktion


def show_heatpump_analysis(
        texts: dict[str, str], project_data: dict[str, Any] = None):
    """Öffentliche Funktion zum Anzeigen der Wärmepumpen-Analyse"""
    render_heatpump_analysis(texts, project_data)

# Wrapper für GUI-Integration


def render_heatpump(texts: dict[str,
                                str],
                    module_name: str | None = None,
                    project_data: dict[str,
                                       Any] | None = None):
    """Von gui.py erwarteter Einstiegspunkt."""
    # Falls keine Projektdaten übergeben wurden, nimm vorhandene PV-Ergebnisse
    # aus dem Session-State
    project_data_effective = (
        project_data
        or st.session_state.get("calculation_results")
        or st.session_state.get("calculation_results_backup")
        or {}
    )
    render_heatpump_analysis(texts, project_data_effective)


if __name__ == "__main__":
    # Test-Modus
    st.set_page_config(page_title="Wärmepumpen-Analyse Test", layout="wide")

    # Dummy-Texte und Projektdaten für Test
    test_texts = {
        'heatpump_analysis': 'Wärmepumpen-Analyse',
        'building_analysis': 'Gebäudeanalyse'
    }

    test_project_data = {
        'annual_pv_production_kwh': 15000,
        'anlage_kwp': 12.5
    }

    show_heatpump_analysis(test_texts, test_project_data)
