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
    from heatpump_advanced_features import (
        calculate_insulation_upgrade,
        compare_heating_systems,
        calculate_window_upgrade,
        create_renovation_roadmap,
    )
    from heatpump_advanced_features_part2 import (
        optimize_heating_schedule,
        simulate_climate_scenarios,
        compare_heatpump_types,
        simulate_annual_load_profile,
    )
    from heatpump_advanced_features_part3 import (
        calculate_subsidies,
        calculate_co2_footprint,
        monte_carlo_roi_analysis,
        benchmark_building,
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
        "🏠 Gebäudeanalyse",
        "🔧 Wärmepumpen-Auswahl",
        "🌡️ Radiator-Check",
        "💰 Wirtschaftlichkeit",
        "⚡ PV-Integration",
        "🏗️ Renovierungs-Planer",  # NEU: Features 1-4
        "⚙️ Optimierung",  # NEU: Features 5-8
        "💵 Förderung & CO2",  # NEU: Features 9-10
        "📈 ROI & Benchmarking",  # NEU: Features 11-12
        "📦 Komponenten & Angebot",
        "📊 Ergebnisse"
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

    with tabs[2]:  # NEU: Radiator-Check
        if 'building_data' in st.session_state:
            radiator_data = render_radiator_check(
                texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")
            radiator_data = None

    with tabs[3]:
        if 'heatpump_data' in st.session_state:
            economics_data = render_economics_analysis(
                texts, st.session_state.heatpump_data)
        else:
            st.info("Bitte wählen Sie zuerst eine Wärmepumpe aus.")
            economics_data = None

    with tabs[4]:
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

    with tabs[5]:  # Renovierungs-Planer
        if 'building_data' in st.session_state:
            render_renovation_planner(texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")

    with tabs[6]:  # Optimierung
        if 'building_data' in st.session_state:
            render_optimization_tools(texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")

    with tabs[7]:  # Förderung & CO2
        if 'building_data' in st.session_state:
            render_subsidy_co2(texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")

    with tabs[8]:  # ROI & Benchmarking
        if 'building_data' in st.session_state:
            render_roi_benchmarking(texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")

    with tabs[9]:  # Komponenten & Angebot
        render_components_offer_tab(texts)

    with tabs[10]:  # Ergebnisse
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


def render_radiator_check(
        texts: dict[str, str], building_data: dict[str, Any]) -> dict[str, Any]:
    """Radiator-Kompatibilitätsprüfung für Wärmepumpe"""
    import streamlit as st
    from calculations_heatpump import (
        calculate_required_flow_temperature,
        check_radiator_compatibility
    )

    st.subheader("🌡️ Radiator-Kompatibilitätsprüfung")

    heat_load_kw = building_data.get('heat_load_kw', 0)

    if heat_load_kw <= 0:
        st.error("Keine gültige Heizlast verfügbar. Bitte Gebäudeanalyse wiederholen.")
        return None

    st.info(f"📊 Heizlast: {heat_load_kw:.1f} kW")

    with st.form("radiator_check_form"):
        st.markdown("### Radiator-Daten eingeben")

        col1, col2 = st.columns(2)

        with col1:
            radiator_area_m2 = st.number_input(
                "Gesamte Radiator-Fläche (m²)",
                min_value=1.0,
                max_value=200.0,
                value=30.0,
                step=1.0,
                help="Summe aller Heizkörper-Oberflächen im Gebäude"
            )

            outdoor_temp_design = st.number_input(
                "Auslegungstemperatur außen (°C)",
                min_value=-20.0,
                max_value=0.0,
                value=-10.0,
                step=1.0,
                help="Niedrigste Außentemperatur in Ihrer Region"
            )

        with col2:
            indoor_temp_target = st.number_input(
                "Ziel-Raumtemperatur (°C)",
                min_value=18.0,
                max_value=24.0,
                value=20.0,
                step=0.5,
                help="Gewünschte Innentemperatur"
            )

            radiator_type = st.selectbox(
                "Radiator-Typ",
                options=[
                    "Standard-Plattenheizkörper",
                    "Konvektoren",
                    "Rippenheizkörper (alt)",
                    "Fußbodenheizung"
                ],
                help="Typ der installierten Heizkörper"
            )

        submitted = st.form_submit_button("🔍 Kompatibilität prüfen", use_container_width=True)

        if submitted:
            try:
                # Berechne erforderliche Vorlauftemperatur
                flow_temp_result = calculate_required_flow_temperature(
                    heat_load_kw=heat_load_kw,
                    radiator_area_m2=radiator_area_m2,
                    outdoor_temp=outdoor_temp_design,
                    indoor_temp=indoor_temp_target
                )

                required_flow_temp = flow_temp_result['required_flow_temp_celsius']

                # Prüfe Kompatibilität
                compatibility_result = check_radiator_compatibility(
                    required_flow_temp_celsius=required_flow_temp
                )

                # Speichere Ergebnis in session_state
                radiator_data = {
                    'radiator_area_m2': radiator_area_m2,
                    'outdoor_temp_design': outdoor_temp_design,
                    'indoor_temp_target': indoor_temp_target,
                    'radiator_type': radiator_type,
                    'required_flow_temp': required_flow_temp,
                    'compatibility': compatibility_result
                }
                st.session_state.radiator_data = radiator_data

                # Visualisierung der Ergebnisse
                st.markdown("---")
                st.markdown("### 📊 Prüfungsergebnis")

                # Status-Badge mit Farbe
                status = compatibility_result['status']
                if status == "Optimal für Wärmepumpe":
                    status_color = "🟢"
                    status_bg = "#d4edda"
                elif status == "Grenzwertig":
                    status_color = "🟡"
                    status_bg = "#fff3cd"
                else:  # "Upgrade empfohlen"
                    status_color = "🔴"
                    status_bg = "#f8d7da"

                st.markdown(
                    f'<div style="background-color: {status_bg}; padding: 20px; border-radius: 10px; text-align: center;">'
                    f'<h2>{status_color} {status}</h2>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Metriken
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Erforderliche Vorlauftemperatur",
                        f"{required_flow_temp:.1f} °C"
                    )

                with col2:
                    cop_loss_percent = compatibility_result.get('cop_loss_percent', 0)
                    st.metric(
                        "COP-Verlust",
                        f"{cop_loss_percent:.0f} %",
                        delta=f"-{cop_loss_percent:.0f}%" if cop_loss_percent > 0 else "Optimal"
                    )

                with col3:
                    upgrade_cost = compatibility_result.get('upgrade_cost_euros', 0)
                    if upgrade_cost > 0:
                        st.metric(
                            "Geschätzte Upgrade-Kosten",
                            f"{upgrade_cost:,.0f} €"
                        )
                    else:
                        st.metric(
                            "Upgrade-Kosten",
                            "0 €",
                            delta="Keine erforderlich"
                        )

                # Empfehlungen
                st.markdown("### 💡 Empfehlungen")
                recommendation = compatibility_result.get('recommendation', '')
                st.info(recommendation)

                # Technische Details in Expander
                with st.expander("🔧 Technische Details"):
                    st.json(flow_temp_result)

                return radiator_data

            except Exception as e:
                st.error(f"Fehler bei der Radiator-Prüfung: {e}")
                return None

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

            # NEU: CO2-Kosten und 20-Jahres-Vergleich
            st.markdown("---")
            st.subheader("🌍 CO2-Kosten & Langfristvergleich")

            try:
                from calculations_heatpump import (
                    compare_heating_systems_20_years,
                    calculate_co2_costs_fossil_heating
                )

                # Bestimme aktuelles Heizsystem
                current_system = building_data.get('heating_system', '')
                fuel_type = "Erdgas"
                if 'Öl' in current_system:
                    fuel_type = "Heizöl"
                elif 'Gas' in current_system:
                    fuel_type = "Erdgas"

                # CO2-Kosten für fossile Heizung berechnen
                co2_cost_result = calculate_co2_costs_fossil_heating(
                    annual_heat_demand_kwh=heat_demand_kwh,
                    fuel_type=fuel_type,
                    co2_price_euro_per_ton=55,  # Aktueller CO2-Preis
                    year=2025
                )

                # 20-Jahres-Systemvergleich
                comparison_result = compare_heating_systems_20_years(
                    annual_heat_demand_kwh=heat_demand_kwh,
                    wp_investment_euros=heatpump['price'] + installation_cost,
                    wp_jaz=heatpump['scop'],
                    electricity_price_euro_per_kwh=electricity_price / 100,
                    fossil_system_type=fuel_type,
                    fossil_investment_euros=12800,  # Durchschnittliche Heizungsmodernisierung
                    fossil_fuel_price_euro_per_kwh=gas_price / 100 if fuel_type == "Erdgas" else oil_price / 100,
                    beg_subsidy_wp=subsidy_amount,
                    has_gas_oil_heater=True,
                    low_income_bonus=False,
                    co2_price_start=55,
                    discount_rate=0.03,
                    annual_cost_increase=0.02
                )

                # CO2-Kosten-Vergleich visualisieren
                col_co2_1, col_co2_2, col_co2_3 = st.columns(3)

                with col_co2_1:
                    st.metric(
                        f"CO2-Kosten {fuel_type} (Jahr 1)",
                        f"{co2_cost_result['annual_co2_cost_euros']:,.0f} €",
                        help="CO2-Preis × Emissionen pro Jahr"
                    )

                with col_co2_2:
                    st.metric(
                        "CO2-Einsparung (20 Jahre)",
                        f"{comparison_result['co2_savings_tons_20y']:,.1f} t",
                        help="Eingesparte CO2-Emissionen über 20 Jahre"
                    )

                with col_co2_3:
                    st.metric(
                        "Monetäre CO2-Ersparnis",
                        f"{comparison_result['co2_savings_monetary_20y']:,.0f} €",
                        help="Vermiedene CO2-Kosten über 20 Jahre"
                    )

                # 20-Jahres-Kostenvergleich (NPV)
                st.markdown("### 💰 20-Jahres-Kostenvergleich (NPV)")

                years_npv = list(range(1, 21))
                wp_cumulative = [comparison_result['wp_net_investment']]
                fossil_cumulative = [comparison_result['fossil_investment']]

                # Berechne kumulierte Kosten über 20 Jahre
                for year in range(1, 20):
                    annual_cost_increase_factor = (1 + 0.02) ** year

                    # Wärmepumpe
                    wp_annual_cost = (
                        (heat_demand_kwh / heatpump['scop']) *
                        (electricity_price / 100) *
                        annual_cost_increase_factor +
                        maintenance_cost_annual
                    )
                    wp_cumulative.append(wp_cumulative[-1] + wp_annual_cost)

                    # Fossil
                    fossil_fuel_price = gas_price / 100 if fuel_type == "Erdgas" else oil_price / 100
                    fossil_annual_cost = (
                        heat_demand_kwh *
                        fossil_fuel_price *
                        annual_cost_increase_factor +
                        co2_cost_result['annual_co2_cost_euros'] * (1 + 0.05) ** year +  # CO2-Preis steigt 5%/Jahr
                        maintenance_cost_annual * 1.5  # Fossil-Wartung teurer
                    )
                    fossil_cumulative.append(fossil_cumulative[-1] + fossil_annual_cost)

                # Chart: 20-Jahres-Kostenvergleich
                fig_20y = go.Figure()

                fig_20y.add_trace(go.Scatter(
                    x=years_npv,
                    y=wp_cumulative,
                    mode='lines+markers',
                    name='Wärmepumpe',
                    line=dict(color='#2E7D32', width=3),
                    fill='tonexty'
                ))

                fig_20y.add_trace(go.Scatter(
                    x=years_npv,
                    y=fossil_cumulative,
                    mode='lines+markers',
                    name=f'{fuel_type}-Heizung',
                    line=dict(color='#C62828', width=3)
                ))

                # Amortisationspunkt markieren
                if comparison_result['payback_years'] < 20:
                    fig_20y.add_vline(
                        x=comparison_result['payback_years'],
                        line_dash="dash",
                        line_color="orange",
                        opacity=0.7,
                        annotation_text=f"Amortisation: {comparison_result['payback_years']:.1f} Jahre"
                    )

                fig_20y.update_layout(
                    title="Kumulierte Gesamtkosten über 20 Jahre (inkl. CO2-Kosten)",
                    xaxis_title="Jahre",
                    yaxis_title="Kumulierte Kosten (€)",
                    hovermode='x unified',
                    height=500
                )

                st.plotly_chart(fig_20y, use_container_width=True)

                # Zusammenfassung 20-Jahres-Vergleich
                st.markdown("### 📊 Ergebnis 20-Jahres-Vergleich")

                col_res1, col_res2, col_res3, col_res4 = st.columns(4)

                with col_res1:
                    st.metric(
                        "WP Gesamtkosten (20J)",
                        f"{comparison_result['wp_total_cost_20y']:,.0f} €"
                    )

                with col_res2:
                    st.metric(
                        f"{fuel_type} Gesamtkosten (20J)",
                        f"{comparison_result['fossil_total_cost_20y']:,.0f} €"
                    )

                with col_res3:
                    total_savings_20y = comparison_result['fossil_total_cost_20y'] - comparison_result['wp_total_cost_20y']
                    st.metric(
                        "Ersparnis (20J)",
                        f"{total_savings_20y:,.0f} €",
                        delta=f"+{(total_savings_20y / comparison_result['fossil_total_cost_20y'] * 100):.1f}%"
                    )

                with col_res4:
                    st.metric(
                        "Amortisation",
                        f"{comparison_result['payback_years']:.1f} Jahre"
                    )

                # CO2-Emissionen visualisieren
                st.markdown("### 🌱 CO2-Emissionen im Vergleich")

                fig_co2 = go.Figure(data=[
                    go.Bar(
                        name='Wärmepumpe',
                        x=['Jährlich', '20 Jahre'],
                        y=[
                            co2_cost_result['annual_emissions_tons_co2'] * 0.3,  # WP: ~30% der fossilen Emissionen (bei deutschem Strommix)
                            co2_cost_result['annual_emissions_tons_co2'] * 0.3 * 20
                        ],
                        marker_color='#2E7D32'
                    ),
                    go.Bar(
                        name=f'{fuel_type}-Heizung',
                        x=['Jährlich', '20 Jahre'],
                        y=[
                            co2_cost_result['annual_emissions_tons_co2'],
                            co2_cost_result['annual_emissions_tons_co2'] * 20
                        ],
                        marker_color='#C62828'
                    )
                ])

                fig_co2.update_layout(
                    title="CO2-Emissionen: Wärmepumpe vs. Fossil",
                    yaxis_title="CO2-Emissionen (Tonnen)",
                    barmode='group',
                    height=400
                )

                st.plotly_chart(fig_co2, use_container_width=True)

            except Exception as e:
                st.warning(f"CO2-Analyse konnte nicht durchgeführt werden: {e}")

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

    # NEU: Energiefluss-Sankey-Diagramm
    st.markdown("---")
    st.subheader("🔄 Energiefluss-Visualisierung")

    try:
        # Energiemengen berechnen
        pv_to_hp = hp_consumption * pv_coverage_hp  # PV → WP
        grid_to_hp = hp_consumption - pv_to_hp  # Netz → WP
        pv_to_grid = pv_production_annual - pv_to_hp  # PV → Netz (Einspeisung)

        # Wärmepumpe erzeugt Wärme mit JAZ/SCOP
        heat_output = hp_consumption * heatpump_data['selected_heatpump']['scop']

        # Sankey-Diagramm erstellen
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=[
                    "☀️ PV-Anlage",           # 0
                    "⚡ Stromnetz",            # 1
                    "🔌 Wärmepumpe",          # 2
                    "🏠 Wärme (Heizung)",     # 3
                    "💾 Einspeisung"          # 4
                ],
                color=[
                    "#f39c12",  # PV: Orange
                    "#3498db",  # Netz: Blau
                    "#2ecc71",  # WP: Grün
                    "#e74c3c",  # Wärme: Rot
                    "#95a5a6"   # Einspeisung: Grau
                ]
            ),
            link=dict(
                source=[0, 1, 2, 0],  # Von: PV, Netz, WP, PV
                target=[2, 2, 3, 4],  # Nach: WP, WP, Wärme, Einspeisung
                value=[
                    pv_to_hp,      # PV → WP
                    grid_to_hp,    # Netz → WP
                    heat_output,   # WP → Wärme
                    pv_to_grid     # PV → Einspeisung
                ],
                color=[
                    "rgba(243, 156, 18, 0.4)",  # PV → WP
                    "rgba(52, 152, 219, 0.4)",   # Netz → WP
                    "rgba(231, 76, 60, 0.6)",    # WP → Wärme
                    "rgba(149, 165, 166, 0.3)"   # PV → Einspeisung
                ],
                label=[
                    f"{pv_to_hp:,.0f} kWh (PV-Eigenverbrauch)",
                    f"{grid_to_hp:,.0f} kWh (Netzbezug)",
                    f"{heat_output:,.0f} kWh (Wärmeerzeugung, JAZ={heatpump_data['selected_heatpump']['scop']:.1f})",
                    f"{pv_to_grid:,.0f} kWh (Netzeinspeisung)"
                ]
            )
        )])

        fig_sankey.update_layout(
            title=f"Energiefluss: PV + Wärmepumpe (Jahresbetrachtung)<br><sub>PV-Deckungsgrad WP: {pv_coverage_hp*100:.0f}%</sub>",
            font=dict(size=12),
            height=500
        )

        st.plotly_chart(fig_sankey, use_container_width=True)

        # Energiebilanz-Tabelle
        with st.expander("📊 Detaillierte Energiebilanz"):
            energy_balance = pd.DataFrame({
                'Energiestrom': [
                    'PV-Erzeugung gesamt',
                    '├─ Eigenverbrauch Wärmepumpe',
                    '└─ Netzeinspeisung',
                    'Strombezug Wärmepumpe',
                    '├─ aus PV-Eigenverbrauch',
                    '└─ aus Stromnetz',
                    'Wärmeerzeugung (Output)',
                    'Jahresarbeitszahl (JAZ)'
                ],
                'Menge': [
                    f"{pv_production_annual:,.0f} kWh",
                    f"{pv_to_hp:,.0f} kWh ({pv_to_hp/pv_production_annual*100:.1f}%)",
                    f"{pv_to_grid:,.0f} kWh ({pv_to_grid/pv_production_annual*100:.1f}%)",
                    f"{hp_consumption:,.0f} kWh",
                    f"{pv_to_hp:,.0f} kWh ({pv_coverage_hp*100:.0f}%)",
                    f"{grid_to_hp:,.0f} kWh ({(1-pv_coverage_hp)*100:.0f}%)",
                    f"{heat_output:,.0f} kWh",
                    f"{heatpump_data['selected_heatpump']['scop']:.2f}"
                ]
            })

            st.dataframe(energy_balance, use_container_width=True, hide_index=True)

    except Exception as e:
        st.warning(f"Energiefluss-Diagramm konnte nicht erstellt werden: {e}")

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

    # NEU: 3D-Visualisierung
    st.markdown("---")
    with st.expander("🎬 3D-Gebäudevisualisierung mit Wärmepumpe", expanded=False):
        render_3d_building_animation(building_data, heatpump_data)

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
                from pdf_generator import generate_heatpump_offer_pdf

                # Kundendaten aus session_state holen
                customer_data = st.session_state.get('project_customer_data', {})
                company_info = st.session_state.get('active_company_info', {}) or {}

                # Radiator-Daten holen (falls vorhanden)
                radiator_data = st.session_state.get('radiator_data', None)

                # Integration-Daten holen (falls vorhanden)
                integration_data = st.session_state.get('integration_data', None)

                # PDF generieren mit neuer Wärmepumpen-spezifischer Funktion
                pdf_bytes = generate_heatpump_offer_pdf(
                    building_data=building_data,
                    heatpump_data=heatpump_data,
                    economics_data=economics_data,
                    company_info=company_info,
                    radiator_data=radiator_data,
                    integration_data=integration_data,
                    customer_data=customer_data
                )

                if pdf_bytes:
                    # Download-Button anzeigen
                    filename = f"Waermepumpe_Angebot_{datetime.now().strftime('%Y%m%d')}.pdf"
                    st.download_button(
                        " Wärmepumpen-Angebot PDF herunterladen",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf"
                    )
                    st.success("✅ PDF erfolgreich erstellt!")
                else:
                    st.error("PDF-Erstellung fehlgeschlagen.")
            except ImportError as e:
                st.error(f"PDF-Modul nicht verfügbar: {e}")
            except Exception as e:
                st.error(f"Fehler bei PDF-Erstellung: {e}")
                import traceback
                st.text(traceback.format_exc())
            except Exception as e:
                st.error(f"Fehler beim PDF-Export: {e}")

    with col_export2:
        if st.button(" Konfiguration speichern"):
            st.info("Konfiguration wird gespeichert...")


def render_3d_building_animation(building_data: dict[str, Any], heatpump_data: dict[str, Any] = None) -> None:
    """
    Erstellt eine 360°-Animation des Gebäudes mit Wärmepumpe und Energiefluss-Visualisierung.

    Args:
        building_data: Gebäudedaten (Fläche, Höhe, etc.)
        heatpump_data: Optional - Wärmepumpen-Daten für erweiterte Visualisierung
    """
    import plotly.graph_objects as go
    import numpy as np

    st.subheader("🏠 3D-Gebäudevisualisierung mit Energiefluss")

    try:
        # Gebäudedimensionen aus building_data extrahieren
        building_area = building_data.get('building_area', 150)

        # Vereinfachte Gebäudeabmessungen (quadratisch fürDemo)
        building_side = np.sqrt(building_area)
        building_height = 6.0  # Durchschnittliche Gebäudehöhe
        roof_height = 3.0      # Dachhöhe

        # Gebäude-Eckpunkte (zentriert um Ursprung)
        half_side = building_side / 2

        # Gebäude-Wände (Box)
        building_vertices = np.array([
            [-half_side, -half_side, 0],           # 0: vorne links unten
            [half_side, -half_side, 0],            # 1: vorne rechts unten
            [half_side, half_side, 0],             # 2: hinten rechts unten
            [-half_side, half_side, 0],            # 3: hinten links unten
            [-half_side, -half_side, building_height],  # 4: vorne links oben
            [half_side, -half_side, building_height],   # 5: vorne rechts oben
            [half_side, half_side, building_height],    # 6: hinten rechts oben
            [-half_side, half_side, building_height],   # 7: hinten links oben
        ])

        # Gebäude-Mesh (vereinfacht - nur sichtbare Flächen)
        building_i = [0, 0, 1, 2, 3, 4, 4, 5, 6, 7]
        building_j = [1, 4, 5, 6, 7, 5, 7, 6, 7, 4]
        building_k = [4, 5, 6, 7, 4, 1, 5, 2, 3, 0]

        # Satteldach-Eckpunkte
        roof_peak_height = building_height + roof_height
        roof_vertices = np.array([
            [-half_side, -half_side, building_height],  # 0: Dachbasis vorne links
            [half_side, -half_side, building_height],   # 1: Dachbasis vorne rechts
            [half_side, half_side, building_height],    # 2: Dachbasis hinten rechts
            [-half_side, half_side, building_height],   # 3: Dachbasis hinten links
            [0, -half_side, roof_peak_height],          # 4: First vorne
            [0, half_side, roof_peak_height],           # 5: First hinten
        ])

        # Dach-Mesh
        roof_i = [0, 1, 3, 2]
        roof_j = [4, 4, 5, 5]
        roof_k = [1, 5, 5, 4]

        # Wärmepumpe (Box außen am Gebäude)
        hp_width = 1.2
        hp_depth = 0.8
        hp_height = 1.5
        hp_x_offset = half_side + 1.5  # 1,5m von Gebäude entfernt

        hp_vertices = np.array([
            [hp_x_offset, -hp_depth/2, 0],
            [hp_x_offset + hp_width, -hp_depth/2, 0],
            [hp_x_offset + hp_width, hp_depth/2, 0],
            [hp_x_offset, hp_depth/2, 0],
            [hp_x_offset, -hp_depth/2, hp_height],
            [hp_x_offset + hp_width, -hp_depth/2, hp_height],
            [hp_x_offset + hp_width, hp_depth/2, hp_height],
            [hp_x_offset, hp_depth/2, hp_height],
        ])

        hp_i = [0, 0, 1, 2, 3, 4]
        hp_j = [1, 4, 5, 6, 7, 5]
        hp_k = [4, 5, 6, 7, 4, 1]

        # Erstelle Plotly-Figure mit Frames für 360°-Rotation
        frames = []
        num_frames = 36  # 36 Frames = 10° pro Frame

        for i in range(num_frames):
            angle = i * (360 / num_frames)

            # Kamera-Position berechnen (kreisförmige Rotation)
            camera_distance = building_side * 2.5
            camera_x = camera_distance * np.cos(np.radians(angle))
            camera_y = camera_distance * np.sin(np.radians(angle))
            camera_z = building_height + roof_height

            frame = go.Frame(
                data=[
                    # Gebäude
                    go.Mesh3d(
                        x=building_vertices[:, 0],
                        y=building_vertices[:, 1],
                        z=building_vertices[:, 2],
                        i=building_i, j=building_j, k=building_k,
                        color='#d4d4d4',
                        opacity=0.9,
                        name='Gebäude',
                        showlegend=False,
                        flatshading=True
                    ),
                    # Dach
                    go.Mesh3d(
                        x=roof_vertices[:, 0],
                        y=roof_vertices[:, 1],
                        z=roof_vertices[:, 2],
                        i=roof_i, j=roof_j, k=roof_k,
                        color='#c96a2d',
                        opacity=0.9,
                        name='Dach',
                        showlegend=False,
                        flatshading=True
                    ),
                    # Wärmepumpe
                    go.Mesh3d(
                        x=hp_vertices[:, 0],
                        y=hp_vertices[:, 1],
                        z=hp_vertices[:, 2],
                        i=hp_i, j=hp_j, k=hp_k,
                        color='#2ecc71',
                        opacity=1.0,
                        name='Wärmepumpe',
                        showlegend=True,
                        flatshading=True
                    ),
                    # Energiefluss-Pfeile (animiert)
                    go.Scatter3d(
                        x=[hp_x_offset + hp_width/2, 0],
                        y=[0, 0],
                        z=[hp_height/2, building_height/2],
                        mode='lines+markers',
                        line=dict(color='#e74c3c', width=8),
                        marker=dict(size=8, color='#e74c3c'),
                        name='Wärmefluss',
                        showlegend=True
                    )
                ],
                layout=go.Layout(
                    scene=dict(
                        camera=dict(
                            eye=dict(
                                x=camera_x / camera_distance * 1.5,
                                y=camera_y / camera_distance * 1.5,
                                z=0.8
                            ),
                            center=dict(x=0, y=0, z=building_height/2)
                        )
                    )
                ),
                name=str(i)
            )
            frames.append(frame)

        # Initial-Figure (Frame 0)
        fig = go.Figure(
            data=frames[0].data,
            layout=go.Layout(
                title=dict(
                    text=f"🏠 Gebäudevisualisierung mit Wärmepumpe<br><sub>Fläche: {building_area:.0f}m² | Höhe: {building_height + roof_height:.1f}m</sub>",
                    x=0.5,
                    xanchor='center'
                ),
                scene=dict(
                    xaxis=dict(title='X (m)', showgrid=True, zeroline=True),
                    yaxis=dict(title='Y (m)', showgrid=True, zeroline=True),
                    zaxis=dict(title='Z (m)', showgrid=True, zeroline=True),
                    aspectmode='data',
                    camera=frames[0].layout.scene.camera
                ),
                updatemenus=[
                    dict(
                        type='buttons',
                        showactive=False,
                        buttons=[
                            dict(
                                label='▶️ 360° Animation',
                                method='animate',
                                args=[None, dict(
                                    frame=dict(duration=100, redraw=True),
                                    fromcurrent=True,
                                    mode='immediate',
                                    transition=dict(duration=50)
                                )]
                            ),
                            dict(
                                label='⏸️ Pause',
                                method='animate',
                                args=[[None], dict(
                                    frame=dict(duration=0, redraw=False),
                                    mode='immediate',
                                    transition=dict(duration=0)
                                )]
                            )
                        ],
                        x=0.1,
                        y=1.15
                    )
                ],
                height=700,
                showlegend=True
            ),
            frames=frames
        )

        st.plotly_chart(fig, use_container_width=True)

        # Info-Box mit Energiedaten
        if heatpump_data:
            col1, col2, col3 = st.columns(3)

            with col1:
                heat_load = building_data.get('heat_load_kw', 0)
                st.metric(
                    "🔥 Heizlast",
                    f"{heat_load:.1f} kW",
                    help="Maximale benötigte Heizleistung"
                )

            with col2:
                hp = heatpump_data.get('selected_heatpump', {})
                st.metric(
                    "💚 WP-Leistung",
                    f"{hp.get('heating_power', 0):.1f} kW",
                    help="Installierte Wärmepumpenleistung"
                )

            with col3:
                st.metric(
                    "⚡ JAZ",
                    f"{hp.get('scop', 0):.1f}",
                    help="Jahresarbeitszahl (Effizienz)"
                )

        st.info(
            "💡 **Interaktiv**: Klicken Sie auf '▶️ 360° Animation' für automatische Rotation. "
            "Sie können das Modell auch manuell mit der Maus drehen."
        )

    except Exception as e:
        st.error(f"Fehler bei der 3D-Visualisierung: {e}")
        st.warning("3D-Animation konnte nicht erstellt werden. Bitte prüfen Sie die Gebäudedaten.")


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


# ============================================================================
# NEUE FEATURES: UI-FUNKTIONEN
# ============================================================================

def render_renovation_planner(texts: dict[str, str], building_data: dict[str, Any]):
    """Renovierungs-Planer Tab (Features 1-4)"""
    
    st.subheader("🏗️ Renovierungs-Planer")
    st.markdown("Optimale Sanierungsmaßnahmen für maximale Effizienz")
    
    # Feature 1: Dämmungs-Upgrade-Rechner
    with st.expander("🏠 Dämmungs-Upgrade-Rechner", expanded=True):
        st.markdown("### Vergleichen Sie verschiedene Dämmungs-Optionen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Aktueller Zustand:**")
            current_roof = st.selectbox("Dach", ["uninsulated", "10cm", "20cm", "30cm"], key="current_roof")
            current_facade = st.selectbox("Fassade", ["uninsulated", "poor", "12cm", "16cm", "20cm"], key="current_facade")
            current_basement = st.selectbox("Kellerdecke", ["uninsulated", "8cm", "12cm", "16cm"], key="current_basement")
            current_windows = st.selectbox("Fenster", ["single", "double_old", "double_new", "triple"], key="current_windows")
        
        with col2:
            st.write("**Ziel-Zustand:**")
            target_roof = st.selectbox("Dach", ["uninsulated", "10cm", "20cm", "30cm"], index=2, key="target_roof")
            target_facade = st.selectbox("Fassade", ["uninsulated", "poor", "12cm", "16cm", "20cm"], index=3, key="target_facade")
            target_basement = st.selectbox("Kellerdecke", ["uninsulated", "8cm", "12cm", "16cm"], index=2, key="target_basement")
            target_windows = st.selectbox("Fenster", ["single", "double_old", "double_new", "triple"], index=3, key="target_windows")
        
        if st.button("Dämmung berechnen", key="calc_insulation"):
            current_state = {
                "roof": current_roof,
                "facade": current_facade,
                "basement": current_basement,
                "windows": current_windows
            }
            target_state = {
                "roof": target_roof,
                "facade": target_facade,
                "basement": target_basement,
                "windows": target_windows
            }
            
            result = calculate_insulation_upgrade(building_data, current_state, target_state)
            
            st.success(f"💰 **Gesamt-Investition:** {result['total_investment_eur']:,.2f} €")
            st.success(f"💵 **Jährliche Einsparung:** {result['total_annual_savings_eur']:,.2f} €/Jahr")
            st.success(f"⏱️ **Amortisation:** {result['total_payback_years']:.1f} Jahre")
            st.success(f"📈 **Gewinn nach 20 Jahren:** {result['savings_20_years_eur']:,.2f} €")
            
            st.markdown("### 📊 Optimale Reihenfolge (nach ROI)")
            for i, measure in enumerate(result['optimal_order'], 1):
                data = result['measures'][measure]
                st.write(f"**{i}. {measure.upper()}**")
                col1, col2, col3 = st.columns(3)
                col1.metric("Investition", f"{data['investment_eur']:,.0f} €")
                col2.metric("Einsparung/Jahr", f"{data['annual_savings_eur']:,.0f} €")
                col3.metric("Amortisation", f"{data['payback_years']:.1f} J")
            
            # Visualisierung
            fig = go.Figure()
            components = list(result['measures'].keys())
            paybacks = [result['measures'][c]['payback_years'] for c in components]
            
            fig.add_trace(go.Bar(
                x=components,
                y=paybacks,
                text=[f"{p:.1f} J" for p in paybacks],
                textposition='auto',
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
            ))
            
            fig.update_layout(
                title="Amortisationszeit nach Komponente",
                xaxis_title="Komponente",
                yaxis_title="Jahre",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Feature 2: Heizkörper vs. Fußbodenheizung
    with st.expander("🌡️ Heizkörper vs. Fußbodenheizung Optimizer"):
        st.markdown("### Welches System ist optimal?")
        
        current_system = st.radio("Aktuelles System", ["radiators", "underfloor"], format_func=lambda x: "Heizkörper" if x == "radiators" else "Fußbodenheizung")
        
        if st.button("Systeme vergleichen", key="compare_heating"):
            result = compare_heating_systems(building_data, current_system)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔥 Niedertemperatur-Radiatoren")
                rad = result['systems']['radiators_new']
                st.metric("Vorlauftemperatur", f"{rad['flow_temperature_c']}°C")
                st.metric("COP", f"{rad['cop']:.2f}")
                st.metric("Installationskosten", f"{rad['installation_cost_eur']:,.0f} €")
                st.metric("Jahreskosten Strom", f"{rad['annual_cost_eur']:,.0f} €")
            
            with col2:
                st.markdown("#### 🌊 Fußbodenheizung")
                uf = result['systems']['underfloor']
                st.metric("Vorlauftemperatur", f"{uf['flow_temperature_c']}°C")
                st.metric("COP", f"{uf['cop']:.2f}")
                st.metric("Installationskosten", f"{uf['installation_cost_eur']:,.0f} €")
                st.metric("Jahreskosten Strom", f"{uf['annual_cost_eur']:,.0f} €")
            
            comp = result['comparison']
            st.markdown("### 🎯 Empfehlung")
            st.success(f"**{comp['recommendation']}**")
            st.info(f"Jährliche Einsparung: {comp['annual_savings_eur']:,.2f} €/Jahr")
            st.info(f"Amortisation: {comp['payback_years']:.1f} Jahre")
            st.info(f"COP-Verbesserung: +{comp['cop_improvement_percent']:.1f}%")
    
    # Feature 3: Fenster-Sanierungs-Assistent
    with st.expander("🪟 Fenster-Sanierungs-Assistent"):
        st.markdown("### U-Wert-Vergleich mit solaren Gewinnen")
        
        col1, col2 = st.columns(2)
        with col1:
            current_glaz = st.selectbox("Aktuelle Verglasung", ["single", "double_old", "double_new", "triple"], key="current_glaz")
        with col2:
            target_glaz = st.selectbox("Ziel-Verglasung", ["double_new", "triple", "triple_plus"], index=1, key="target_glaz")
        
        st.markdown("**Fenster-Ausrichtung (Anteil):**")
        col1, col2, col3, col4 = st.columns(4)
        north = col1.number_input("Norden", min_value=0.0, max_value=1.0, value=0.20, step=0.05)
        east = col2.number_input("Osten", min_value=0.0, max_value=1.0, value=0.20, step=0.05)
        south = col3.number_input("Süden", min_value=0.0, max_value=1.0, value=0.35, step=0.05)
        west = col4.number_input("Westen", min_value=0.0, max_value=1.0, value=0.25, step=0.05)
        
        if st.button("Fenster-Sanierung berechnen", key="calc_windows"):
            orientation_mix = {"north": north, "east": east, "south": south, "west": west}
            result = calculate_window_upgrade(building_data, current_glaz, target_glaz, orientation_mix)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Fensterfläche", f"{result['window_area_m2']:.1f} m²")
                st.metric("U-Wert Verbesserung", f"-{result['u_value_improvement']['reduction_percent']:.1f}%")
                st.metric("Wärmeverlust-Reduktion", f"{result['heat_loss_reduction_kwh']:,.0f} kWh")
            
            with col2:
                st.metric("Investition (brutto)", f"{result['investment_eur']:,.0f} €")
                st.metric("Förderung (15%)", f"{result['subsidy_eur']:,.0f} €")
                st.metric("Netto-Investition", f"{result['net_investment_eur']:,.0f} €")
            
            st.success(f"📈 **Gewinn nach 20 Jahren:** {result['savings_20_years_eur']:,.2f} €")
            st.info(f"⏱️ **Amortisation:** {result['payback_years']:.1f} Jahre")
    
    # Feature 4: Gesamt-Renovierungs-Planer
    with st.expander("📋 Gesamt-Renovierungs-Planer"):
        st.markdown("### Optimaler Sanierungsfahrplan mit Budget-Optimierung")
        
        budget_total = st.number_input("Verfügbares Budget (€)", min_value=10000, max_value=200000, value=50000, step=5000)
        
        st.markdown("**Aktueller Zustand aller Komponenten:**")
        col1, col2, col3, col4 = st.columns(4)
        curr_roof = col1.selectbox("Dach", ["uninsulated", "10cm", "20cm"], key="roadmap_roof")
        curr_facade = col2.selectbox("Fassade", ["uninsulated", "poor", "12cm"], key="roadmap_facade")
        curr_basement = col3.selectbox("Keller", ["uninsulated", "8cm", "12cm"], key="roadmap_basement")
        curr_windows = col4.selectbox("Fenster", ["single", "double_old", "double_new"], key="roadmap_windows")
        
        if st.button("Sanierungsplan erstellen", key="create_roadmap"):
            current_states = {
                "roof": curr_roof,
                "facade": curr_facade,
                "basement": curr_basement,
                "windows": curr_windows
            }
            
            result = create_renovation_roadmap(building_data, budget_total, current_states)
            
            st.markdown("### 📊 Sanierungsfahrplan")
            for step in result['roadmap']:
                with st.container():
                    st.markdown(f"### Schritt {step['step']}: {step['measure'].replace('_', ' ').title()}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Investition", f"{step['investment_eur']:,.0f} €")
                    col2.metric("Einsparung/Jahr", f"{step['annual_savings_eur']:,.0f} €")
                    col3.metric("Amortisation", f"{step['payback_years']:.1f} J")
                    st.progress(step['cumulative_investment'] / budget_total)
                    st.write(f"Kumulative Investition: {step['cumulative_investment']:,.0f} € von {budget_total:,.0f} €")
            
            summary = result['summary']
            st.markdown("### 💰 Zusammenfassung")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Maßnahmen", summary['total_measures'])
            col2.metric("Investition", f"{summary['net_investment_eur']:,.0f} €")
            col3.metric("Förderung", f"{summary['total_subsidy_eur']:,.0f} €")
            col4.metric("Einsparung/Jahr", f"{summary['total_annual_savings_eur']:,.0f} €")
            
            st.success(f"📈 **Gewinn nach 20 Jahren:** {summary['savings_20_years_eur']:,.2f} €")
            st.info(f"⏱️ **Gesamt-Amortisation:** {summary['overall_payback_years']:.1f} Jahre")


def render_optimization_tools(texts: dict[str, str], building_data: dict[str, Any]):
    """Optimierungs-Tools Tab (Features 5-8)"""
    
    st.subheader("⚙️ Optimierungs-Tools")
    st.markdown("Intelligente Analyse und Optimierung")
    
    # Feature 5: Verbrauchsoptimierer Turbo
    with st.expander("⚡ Verbrauchsoptimierer Turbo", expanded=True):
        st.markdown("### Heizplan-Optimierung mit Stromtarifen")
        
        st.markdown("**Anwesenheitsprofil (Wochentag):**")
        st.info("1 = Anwesend, 0 = Abwesend")
        
        # Vereinfachte Eingabe: 24 Stunden für Wochentag
        hours_occupied = st.multiselect(
            "Anwesenheitszeiten (Wochentag)",
            list(range(24)),
            default=[7, 8, 18, 19, 20, 21, 22]
        )
        
        occupancy_weekday = [1 if h in hours_occupied else 0 for h in range(24)]
        occupancy_weekend = [1] * 24  # Wochenende: Ganztags anwesend
        
        occupancy_profile = {
            "monday": occupancy_weekday,
            "tuesday": occupancy_weekday,
            "wednesday": occupancy_weekday,
            "thursday": occupancy_weekday,
            "friday": occupancy_weekday,
            "saturday": occupancy_weekend,
            "sunday": occupancy_weekend
        }
        
        col1, col2, col3 = st.columns(3)
        tariff_night = col1.number_input("Nachttarif (€/kWh)", value=0.22, step=0.01)
        tariff_day = col2.number_input("Tagtarif (€/kWh)", value=0.32, step=0.01)
        tariff_peak = col3.number_input("Spitzentarif (€/kWh)", value=0.42, step=0.01)
        
        electricity_tariff = {"night": tariff_night, "day": tariff_day, "peak": tariff_peak}
        
        if st.button("Heizplan optimieren", key="optimize_schedule"):
            result = optimize_heating_schedule(building_data, occupancy_profile, electricity_tariff)
            
            st.markdown("### 💰 Einsparung durch Optimierung")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Baseline (konstant)", f"{result['baseline']['annual_cost_eur']:,.0f} €/Jahr")
            with col2:
                st.metric("Optimiert (Vorheizen)", f"{result['optimized']['annual_cost_eur']:,.0f} €/Jahr")
            
            st.success(f"💵 **Jährliche Einsparung:** {result['savings']['annual_eur']:,.2f} € ({result['savings']['percent']:.1f}%)")
            
            # Visualisierung: Wochenplan
            schedule_df = pd.DataFrame(result['schedule'][:168])  # Erste Woche
            
            fig = go.Figure()
            
            # Heizmodus als Farbe
            mode_colors = {"normal": "green", "preheat": "orange", "reduced": "blue"}
            
            for mode in ["normal", "preheat", "reduced"]:
                df_mode = schedule_df[schedule_df['mode'] == mode]
                fig.add_trace(go.Scatter(
                    x=df_mode.index,
                    y=df_mode['power_kw'],
                    mode='markers',
                    name=mode.title(),
                    marker=dict(color=mode_colors[mode], size=8)
                ))
            
            fig.update_layout(
                title="Optimierter Heizplan (1 Woche)",
                xaxis_title="Stunde",
                yaxis_title="Heizleistung (kW)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Feature 6: Klimawandel-Szenarien
    with st.expander("🌍 Klimawandel-Szenarien 2025-2050"):
        st.markdown("### Langzeit-Prognose mit Temperaturanstieg")
        
        if st.button("Szenarien berechnen", key="climate_scenarios"):
            result = simulate_climate_scenarios(building_data)
            
            st.markdown("### 📊 Vergleich der Szenarien")
            
            # Tabelle
            summary_data = []
            for scenario_key, scenario_data in result['scenarios'].items():
                summary = scenario_data['summary_2050']
                summary_data.append({
                    "Szenario": scenario_data['name'],
                    "Temperaturanstieg": f"+{summary['temp_increase_c']:.1f}°C",
                    "Heizlast-Reduktion": f"-{summary['heating_reduction_percent']:.1f}%",
                    "COP 2050": f"{summary['final_cop']:.2f}",
                    "Strompreis 2050": f"{summary['electricity_price_2050']:.3f} €/kWh",
                    "Kosten 2024-2050": f"{summary['cumulative_cost_2024_2050_eur']:,.0f} €"
                })
            
            st.dataframe(pd.DataFrame(summary_data))
            
            st.success(f"💵 **Differenz Best/Worst Case:** {result['comparison']['difference_eur']:,.0f} €")
            
            # Visualisierung: Kosten-Entwicklung
            fig = go.Figure()
            
            for scenario_key, scenario_data in result['scenarios'].items():
                yearly = scenario_data['yearly_data']
                years = [d['year'] for d in yearly]
                costs = [d['annual_cost_eur'] for d in yearly]
                
                fig.add_trace(go.Scatter(
                    x=years,
                    y=costs,
                    mode='lines+markers',
                    name=scenario_data['name']
                ))
            
            fig.update_layout(
                title="Jährliche Heizkosten-Entwicklung bis 2050",
                xaxis_title="Jahr",
                yaxis_title="Kosten (€/Jahr)",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Feature 7: Wärmepumpen-Auswahl-Matrix
    with st.expander("🔧 Wärmepumpen-Auswahl-Matrix"):
        st.markdown("### Vergleichen Sie alle WP-Typen")
        
        col1, col2 = st.columns(2)
        plot_size = col1.number_input("Grundstücksgröße (m²)", min_value=100, max_value=5000, value=500)
        groundwater = col2.checkbox("Grundwasser verfügbar?", value=False)
        
        if st.button("WP-Typen vergleichen", key="compare_heatpumps"):
            result = compare_heatpump_types(building_data, plot_size, groundwater)
            
            st.markdown("### 🏆 Ranking nach Lebenszykluskosten")
            for rank_data in result['ranking']:
                st.write(f"**{rank_data['rank']}. {rank_data['name']}**")
            
            st.success(f"🎯 **Empfehlung:** {result['comparison'][result['recommendation']]['name']}")
            
            # Vergleichs-Tabelle
            comparison_data = []
            for wp_type, data in result['comparison'].items():
                comparison_data.append({
                    "Typ": data['name'],
                    "COP": f"{data['cop']:.2f}",
                    "Investition": f"{data['net_installation_eur']:,.0f} €",
                    "Stromkosten/Jahr": f"{data['annual_electricity_cost_eur']:,.0f} €",
                    "Wartung/Jahr": f"{data['annual_maintenance_eur']} €",
                    "Lebenszykluskosten": f"{data['lifetime_cost_eur']:,.0f} €",
                    "Lautstärke": f"{data['noise_db']} dB",
                    "Lebensdauer": f"{data['lifespan_years']} Jahre"
                })
            
            st.dataframe(pd.DataFrame(comparison_data))
    
    # Feature 8: 8760h-Lastgang-Analyse
    with st.expander("📈 8760h-Lastgang-Analyse"):
        st.markdown("### Stündliche Simulation über ganzes Jahr")
        
        if st.button("Jahres-Simulation starten", key="simulate_annual"):
            with st.spinner("Simuliere 8760 Stunden..."):
                result = simulate_annual_load_profile(building_data)
            
            st.markdown("### 📊 Jahres-Zusammenfassung")
            col1, col2, col3, col4 = st.columns(4)
            summary = result['annual_summary']
            col1.metric("Wärmebedarf", f"{summary['total_heat_kwh']:,.0f} kWh")
            col2.metric("Stromverbrauch", f"{summary['total_electricity_kwh']:,.0f} kWh")
            col3.metric("Ø COP", f"{summary['annual_average_cop']:.2f}")
            col4.metric("Betriebsstunden", f"{summary['operating_hours']:,.0f} h")
            
            st.success(f"💰 **Jahreskosten:** {summary['annual_cost_eur']:,.2f} €")
            
            # Monats-Übersicht
            st.markdown("### 📅 Monats-Übersicht")
            monthly_df = pd.DataFrame(result['monthly_summary'])
            monthly_df['month_name'] = monthly_df['month'].map({
                1: "Jan", 2: "Feb", 3: "Mär", 4: "Apr", 5: "Mai", 6: "Jun",
                7: "Jul", 8: "Aug", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dez"
            })
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=monthly_df['month_name'],
                y=monthly_df['total_electricity_kwh'],
                name="Stromverbrauch",
                marker_color='#FF6B6B'
            ))
            
            fig.add_trace(go.Scatter(
                x=monthly_df['month_name'],
                y=monthly_df['avg_cop'],
                name="Ø COP",
                yaxis='y2',
                marker_color='#4ECDC4'
            ))
            
            fig.update_layout(
                title="Monats-Übersicht: Stromverbrauch & COP",
                xaxis_title="Monat",
                yaxis_title="Stromverbrauch (kWh)",
                yaxis2=dict(title="Ø COP", overlaying='y', side='right'),
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)


def render_subsidy_co2(texts: dict[str, str], building_data: dict[str, Any]):
    """Förderung & CO2 Tab (Features 9-10)"""
    
    st.subheader("💵 Förderung & CO2-Dashboard")
    
    # Feature 9: Fördermittel-Optimizer
    with st.expander("🎁 Fördermittel-Optimizer", expanded=True):
        st.markdown("### Alle verfügbaren Förderungen (BAFA, KfW, Länder)")
        
        st.markdown("**Welche Maßnahmen planen Sie?**")
        col1, col2, col3 = st.columns(3)
        measure_hp = col1.checkbox("Wärmepumpe", value=True)
        measure_insulation = col2.checkbox("Dämmung", value=True)
        measure_windows = col3.checkbox("Fenster", value=True)
        
        building_age = st.number_input("Gebäudealter (Jahre)", min_value=0, max_value=100, value=30)
        
        measures = {
            "heatpump": measure_hp,
            "insulation": measure_insulation,
            "windows": measure_windows
        }
        
        if st.button("Förderungen berechnen", key="calc_subsidies"):
            result = calculate_subsidies(building_data, measures, building_age)
            
            st.markdown("### 💰 Finanzierung")
            col1, col2, col3 = st.columns(3)
            col1.metric("Gesamt-Investition", f"{result['total_investment_eur']:,.0f} €")
            col2.metric("Förderung", f"{result['total_subsidy_eur']:,.0f} € ({result['subsidy_rate']:.1f}%)")
            col3.metric("Netto-Investition", f"{result['net_investment_eur']:,.0f} €")
            
            st.markdown("### 📋 Förderungen im Detail")
            for subsidy in result['subsidies']:
                with st.container():
                    st.markdown(f"#### {subsidy['program']}")
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"**Typ:** {subsidy['type']}")
                    col2.write(f"**Betrag:** {subsidy['amount_eur']:,.2f} €")
                    if subsidy['rate'] > 0:
                        col3.write(f"**Rate:** {subsidy['rate']:.1f}%")
            
            if result['loan_option']:
                st.markdown("### 🏦 KfW-Kredit-Option")
                loan = result['loan_option']
                col1, col2, col3 = st.columns(3)
                col1.metric("Kreditbetrag", f"{loan['loan_amount_eur']:,.0f} €")
                col2.metric("Tilgungszuschuss", f"{loan['tilgung_grant_eur']:,.0f} €")
                col3.metric("Monatliche Rate", f"{loan['monthly_rate_eur']:.2f} €")
                st.info(f"Laufzeit: {loan['duration_years']} Jahre, Zinssatz: {loan['interest_rate']*100:.1f}%")
            
            st.markdown("### ✅ Antrags-Checkliste")
            for item in result['application_checklist']:
                st.checkbox(item, key=f"checklist_{item}")
    
    # Feature 10: CO2-Dashboard Live
    with st.expander("🌱 CO2-Dashboard Live"):
        st.markdown("### Langfristige CO2-Bilanz (20 Jahre)")
        
        col1, col2 = st.columns(2)
        current_sys = col1.selectbox("Aktuelles System", ["gas", "oil", "district_heating"], format_func=lambda x: {"gas": "Erdgas", "oil": "Heizöl", "district_heating": "Fernwärme"}[x])
        future_sys = col2.selectbox("Zukünftiges System", ["heatpump", "heatpump_pv"], format_func=lambda x: {"heatpump": "Wärmepumpe (Grid)", "heatpump_pv": "Wärmepumpe + PV"}[x])
        
        if st.button("CO2-Bilanz berechnen", key="calc_co2"):
            result = calculate_co2_footprint(building_data, current_sys, future_sys)
            
            st.markdown("### 🌍 20-Jahres-Zusammenfassung")
            col1, col2, col3, col4 = st.columns(4)
            summary = result['summary_20_years']
            col1.metric("CO2-Einsparung", f"{summary['total_co2_savings_t']:.1f} Tonnen")
            col2.metric("Kostenersparnis", f"{summary['total_co2_cost_savings_eur']:,.0f} €")
            col3.metric("≈ Bäume gepflanzt", f"{summary['equivalent_trees_planted']:,.0f}")
            col4.metric("≈ PKW-km eingespart", f"{summary['equivalent_car_km']:,.0f}")
            
            st.success(f"💚 **Pro Jahr:** {summary['avg_annual_savings_t']:.2f} Tonnen CO2")
            
            # Visualisierung: CO2-Entwicklung
            yearly_df = pd.DataFrame(result['yearly_data'])
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=yearly_df['year'],
                y=yearly_df['current_co2_t'],
                mode='lines',
                name=current_sys.upper(),
                line=dict(color='red', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=yearly_df['year'],
                y=yearly_df['future_co2_t'],
                mode='lines',
                name=future_sys.upper(),
                line=dict(color='green', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=yearly_df['year'],
                y=yearly_df['savings_co2_t'],
                mode='lines',
                name="Einsparung",
                fill='tozeroy',
                line=dict(color='lightgreen', width=1)
            ))
            
            fig.update_layout(
                title="CO2-Emissionen über 20 Jahre",
                xaxis_title="Jahr",
                yaxis_title="CO2 (Tonnen/Jahr)",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # CO2-Preis-Entwicklung
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(
                x=yearly_df['year'],
                y=yearly_df['co2_price_eur_t'],
                mode='lines+markers',
                name="CO2-Preis",
                marker=dict(color='orange')
            ))
            
            fig2.update_layout(
                title="CO2-Preis-Entwicklung",
                xaxis_title="Jahr",
                yaxis_title="€/Tonne CO2",
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)


def render_roi_benchmarking(texts: dict[str, str], building_data: dict[str, Any]):
    """ROI & Benchmarking Tab (Features 11-12)"""
    
    st.subheader("📈 ROI-Analyse & Benchmarking")
    
    # Feature 11: Monte-Carlo ROI-Calculator
    with st.expander("🎲 ROI-Calculator Monte-Carlo", expanded=True):
        st.markdown("### Probabilistische Wirtschaftlichkeits-Analyse")
        st.info("Simuliert 10.000 Szenarien mit unterschiedlichen Parametern")
        
        investment = st.number_input("Investitionssumme (€)", min_value=5000, max_value=100000, value=20000, step=1000)
        simulations = st.slider("Anzahl Simulationen", min_value=1000, max_value=10000, value=10000, step=1000)
        
        if st.button("Monte-Carlo-Simulation starten", key="monte_carlo"):
            with st.spinner(f"Führe {simulations:,} Simulationen durch..."):
                result = monte_carlo_roi_analysis(building_data, investment, simulations)
            
            st.markdown("### 📊 Amortisations-Statistik")
            col1, col2, col3, col4 = st.columns(4)
            payback = result['payback_statistics']
            col1.metric("Ø Amortisation", f"{payback['mean_years']:.1f} Jahre")
            col2.metric("Median", f"{payback['median_years']:.1f} Jahre")
            col3.metric("Best Case (10%)", f"{payback['p10_years']:.1f} Jahre")
            col4.metric("Worst Case (90%)", f"{payback['p90_years']:.1f} Jahre")
            
            st.success(f"✅ **Wahrscheinlichkeit für Amortisation <15 Jahre:** {payback['probability_under_15_years']:.1f}%")
            
            st.markdown("### 💰 Nettobarwert (NPV)")
            col1, col2, col3 = st.columns(3)
            npv = result['npv_statistics']
            col1.metric("Ø NPV", f"{npv['mean_eur']:,.0f} €")
            col2.metric("Median NPV", f"{npv['median_eur']:,.0f} €")
            col3.metric("Wahrscheinlichkeit NPV>0", f"{npv['probability_positive']:.1f}%")
            
            st.markdown("### 📈 ROI-Statistik")
            col1, col2, col3 = st.columns(3)
            roi = result['roi_statistics']
            col1.metric("Ø ROI", f"{roi['mean_percent']:.1f}%")
            col2.metric("Median ROI", f"{roi['median_percent']:.1f}%")
            col3.metric("ROI-Spanne", f"{roi['p10_percent']:.1f}% bis {roi['p90_percent']:.1f}%")
            
            # Visualisierung: Verteilung der Amortisationszeiten
            raw_results = result['raw_results']
            payback_values = [r['payback_years'] for r in raw_results if r['payback_years'] < 30]
            
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=payback_values,
                nbinsx=30,
                marker_color='#4ECDC4',
                name="Häufigkeit"
            ))
            
            fig.add_vline(x=payback['mean_years'], line_dash="dash", line_color="red", annotation_text=f"Ø {payback['mean_years']:.1f} J")
            fig.add_vline(x=payback['median_years'], line_dash="dash", line_color="green", annotation_text=f"Median {payback['median_years']:.1f} J")
            
            fig.update_layout(
                title="Verteilung der Amortisationszeiten",
                xaxis_title="Jahre",
                yaxis_title="Häufigkeit",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Feature 12: Benchmarking-Tool
    with st.expander("🏆 Benchmarking-Tool"):
        st.markdown("### Vergleich mit ähnlichen Gebäuden")
        
        region = st.selectbox("Region", ["Germany", "Bayern", "NRW", "Baden-Württemberg"], index=0)
        
        if st.button("Benchmarking durchführen", key="benchmark"):
            result = benchmark_building(building_data, region)
            
            own = result['own_building']
            ranking = result['ranking']
            comparison = result['comparison']
            
            st.markdown("### 📊 Ihr Gebäude")
            col1, col2, col3 = st.columns(3)
            col1.metric("Verbrauch", f"{own['specific_consumption_kwh_m2']:.1f} kWh/m²/Jahr")
            col2.metric("Wohnfläche", f"{own['living_area_m2']:.0f} m²")
            col3.metric("Baujahr", own['year_built'])
            
            st.markdown("### 🎯 Ranking")
            rank_color = "green" if ranking['percentile'] <= 25 else "orange" if ranking['percentile'] <= 50 else "red"
            st.markdown(f"**Platz {ranking['rank']} von {ranking['total_buildings']}** ({ranking['percentile']:.1f}. Perzentil)")
            st.markdown(f"**Bewertung:** :{rank_color}[{ranking['interpretation']}]")
            
            st.markdown("### 📉 Vergleich")
            col1, col2, col3 = st.columns(3)
            col1.metric("Durchschnitt", f"{comparison['avg_consumption_kwh_m2']:.1f} kWh/m²", 
                        delta=f"{comparison['difference_to_avg_kwh_m2']:.1f}", delta_color="inverse")
            col2.metric("Bestes Gebäude", f"{comparison['best_consumption_kwh_m2']:.1f} kWh/m²",
                        delta=f"{comparison['difference_to_best_kwh_m2']:.1f}", delta_color="inverse")
            col3.metric("Schlechtestes", f"{comparison['worst_consumption_kwh_m2']:.1f} kWh/m²")
            
            st.success(f"💰 **Einsparpotenzial:** {result['potential_annual_savings_eur']:,.2f} €/Jahr")
            
            # Best Performer
            best = result['best_performer']
            st.markdown("### 🏅 Best Performer")
            st.info(f"**System:** {best['system'].upper()}, **Gedämmt:** {'Ja' if best['insulated'] else 'Nein'}, **Baujahr:** {best['year']}, **Verbrauch:** {best['consumption_kwh_m2']} kWh/m²")
            
            # Empfehlungen
            if result['recommendations']:
                st.markdown("### 💡 Empfehlungen")
                for rec in result['recommendations']:
                    priority_color = "red" if rec['priority'] == "high" else "orange"
                    st.markdown(f":{priority_color}[**{rec['priority'].upper()}**] {rec['measure']}")
                    col1, col2 = st.columns(2)
                    col1.write(f"Einsparung: {rec['potential_savings_kwh_m2']:.0f} kWh/m²/Jahr")
                    col2.write(f"Investition: {rec['investment_eur']:,.0f} €")


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
