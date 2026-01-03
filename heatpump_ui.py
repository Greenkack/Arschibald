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
from pathlib import Path
import json
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

__all__ = [
    'render_heatpump',
    'render_heatpump_analysis',
    'MONITORING_AVAILABLE',
]

# Monitoring Infrastructure
try:
    from app_tracing import app_tracer
    from app_evaluation import track_success, track_error, evaluate_performance
    MONITORING_AVAILABLE = True
    
    def trace_heatpump(func):
        """Decorator for heatpump operations tracing."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation_name = f"heatpump.{func.__name__}"
            try:
                with app_tracer.create_span(operation_name, {"function": func.__name__}):
                    result = func(*args, **kwargs)
                    track_success(operation_name)
                    evaluate_performance(operation_name, time.time() - start_time)
                    return result
            except Exception as e:
                track_error(operation_name, e)
                raise
        return wrapper
except ImportError:
    MONITORING_AVAILABLE = False
    def trace_heatpump(func):
        return func


# Deutsche Zahlenformatierung
def format_german_number(number, decimals=2):
    """
    Formatiert Zahlen nach deutscher Notation:
    - Tausender-Trennzeichen: Punkt (.)
    - Dezimal-Trennzeichen: Komma ()
    - Immer 2 Dezimalstellen für Geldbeträge
    
    Beispiel: 12345.67 -> "12.345,67"
    """
    if number is None:
        return "0,00" if decimals == 2 else "0"
    
    # Format mit englischer Notation
    if decimals == 0:
        formatted = f"{number:,.0f}"
    else:
        formatted = f"{number:,.{decimals}f}"
    
    # Tausche Trennzeichen: , -> TEMP, . -> , TEMP -> .
    formatted = formatted.replace(',', 'TEMP')
    formatted = formatted.replace('.', ',')
    formatted = formatted.replace('TEMP', '.')
    
    return formatted


# ============================================================================
# CHART THEME - VOLLSTÄNDIGES SHADCN UI DESIGN-SYSTEM
# ============================================================================

def get_chart_theme():
    """
    Gibt Chart-Theme basierend auf aktuellem Streamlit Theme zurück.
    Vollständiges Shadcn UI Design mit modernen Effekten.
    """
    import streamlit as st
    
    # Erkenne aktuelles Theme
    try:
        theme = st.get_option("theme.base")
    except:
        theme = "dark"  # Default zu dark
    
    # Shadcn UI Farben (echte Shadcn-Palette)
    if theme == "light":
        # Light Mode - Helles Shadcn UI
        bg_color = "#ffffff"
        paper_color = "#f8fafc"
        text_color = "#020817"
        text_muted = "#64748b"
        grid_color = "#e2e8f0"
        border_color = "#e2e8f0"
        primary_color = "#0ea5e9"
        primary_light = "#7dd3fc"
        secondary_color = "#8b5cf6"
        success_color = "#10b981"
        warning_color = "#f59e0b"
        danger_color = "#ef4444"
        accent_color = "#f43f5e"
    else:
        # Dark Mode - Dunkles Shadcn UI (Standard)
        bg_color = "#020817"
        paper_color = "#0f172a"
        text_color = "#f8fafc"
        text_muted = "#94a3b8"
        grid_color = "#1e293b"
        border_color = "#334155"
        primary_color = "#38bdf8"
        primary_light = "#7dd3fc"
        secondary_color = "#a78bfa"
        success_color = "#34d399"
        warning_color = "#fbbf24"
        danger_color = "#f87171"
        accent_color = "#fb7185"
    
    return {
        "layout": {
            # Hintergründe
            "plot_bgcolor": paper_color,
            "paper_bgcolor": bg_color,
            
            # Typografie
            "font": {
                "family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
                "size": 13,
                "color": text_color
            },
            "title": {
                "font": {
                    "size": 20,
                    "weight": 600,
                    "color": text_color,
                    "family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                },
                "x": 0.5,
                "xanchor": "center",
                "pad": {"t": 20, "b": 20}
            },
            
            # X-Achse (Shadcn UI Stil)
            "xaxis": {
                "gridcolor": grid_color,
                "gridwidth": 1,
                "linecolor": border_color,
                "linewidth": 2,
                "tickcolor": border_color,
                "tickwidth": 1,
                "tickfont": {"color": text_muted, "size": 11},
                "title": {"font": {"color": text_color, "size": 13, "weight": 500}},
                "showgrid": True,
                "zeroline": False
            },
            
            # Y-Achse (Shadcn UI Stil)
            "yaxis": {
                "gridcolor": grid_color,
                "gridwidth": 1,
                "linecolor": border_color,
                "linewidth": 2,
                "tickcolor": border_color,
                "tickwidth": 1,
                "tickfont": {"color": text_muted, "size": 11},
                "title": {"font": {"color": text_color, "size": 13, "weight": 500}},
                "showgrid": True,
                "zeroline": True,
                "zerolinecolor": grid_color,
                "zerolinewidth": 2
            },
            
            # Legende (Shadcn Card-Style)
            "legend": {
                "bgcolor": paper_color,
                "bordercolor": border_color,
                "borderwidth": 1,
                "font": {"color": text_color, "size": 12},
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.2,
                "xanchor": "center",
                "x": 0.5,
                "itemsizing": "constant"
            },
            
            # Hover-Labels (Shadcn Popover-Style)
            "hoverlabel": {
                "bgcolor": paper_color,
                "bordercolor": border_color,
                "font": {
                    "family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
                    "size": 12,
                    "color": text_color
                },
                "align": "left"
            },
            
            # Abstände (großzügiger für moderne UI)
            "margin": {"l": 70, "r": 40, "t": 80, "b": 70},
            
            # Interaktivität
            "hovermode": "x unified",
            "dragmode": "zoom",
            
            # Moderne Effekte
            "showlegend": True,
            "modebar": {
                "bgcolor": bg_color,
                "color": text_muted,
                "activecolor": primary_color
            }
        },
        "colors": {
            "primary": primary_color,
            "primary_light": primary_light,
            "secondary": secondary_color,
            "success": success_color,
            "warning": warning_color,
            "danger": danger_color,
            "accent": accent_color,
            "text": text_color,
            "text_muted": text_muted,
            "grid": grid_color,
            "border": border_color,
            "bg": bg_color,
            "paper": paper_color
        }
    }


def apply_chart_theme(fig):
    """
    Wendet vollständiges Shadcn UI Design auf Plotly Figure an.
    
    Features:
    - Moderne Shadcn UI Farbpalette
    - Gradient-Fills bei Scatter-Charts
    - Abgerundete Bar-Ecken
    - Optimierte Hover-Effekte
    - Responsive Layout
    """
    theme = get_chart_theme()
    colors = theme["colors"]
    
    # Basis-Layout anwenden
    fig.update_layout(**theme["layout"])
    
    # Shadcn UI Styling für verschiedene Chart-Typen
    for trace in fig.data:
        trace_type = type(trace).__name__
        
        # SCATTER/LINE CHARTS - Gradient & moderne Linien
        if trace_type == "Scatter":
            if trace.mode and "lines" in trace.mode:
                # Moderne Linienbreite
                if trace.line and trace.line.width:
                    trace.update(line=dict(width=3, shape="spline"))
                else:
                    trace.update(line=dict(width=3, shape="spline"))
                
                # Gradient-Fill für gefüllte Bereiche
                if trace.fill:
                    if not trace.fillcolor or "rgba" not in str(trace.fillcolor):
                        # Automatische Gradient-Farbe basierend auf Linienfarbe
                        line_color = trace.line.color if trace.line and trace.line.color else colors["primary"]
                        trace.update(fillcolor=f"rgba({_hex_to_rgb(line_color)}, 0.15)")
        
        # BAR CHARTS - Abgerundete Ecken & Shadcn-Farben
        elif trace_type == "Bar":
            # Moderne Bar-Breite
            trace.update(
                marker=dict(
                    line=dict(width=0),
                    opacity=0.9
                ),
                width=0.7
            )
            
            # Farben anpassen wenn nicht gesetzt
            if not trace.marker or not trace.marker.color:
                trace.update(marker_color=colors["primary"])
        
        # HISTOGRAM - Shadcn-Farben
        elif trace_type == "Histogram":
            trace.update(
                marker=dict(
                    color=colors["primary"],
                    line=dict(width=0),
                    opacity=0.85
                )
            )
    
    # Alle Achsen für Multi-Plot Charts
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=colors["grid"],
        zeroline=False
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=colors["grid"],
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor=colors["grid"]
    )
    
    return fig


def _hex_to_rgb(hex_color: str) -> str:
    """Konvertiert Hex-Farbe zu RGB-String für rgba()"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    return "59, 130, 246"  # Fallback Blue


# Heizkosten-Konfiguration laden
def load_heating_costs_config():
    """Lädt die Heizkosten-Konfiguration aus der Admin-Einstellung"""
    config_file = Path(__file__).parent / "config" / "heating_costs_config.json"
    
    # Standardwerte falls Datei nicht existiert
    default_config = {
        "co2_factors": {
            "oil_kg_per_liter": 2.66,
            "gas_g_per_kwh": 428,
            "electricity_g_per_kwh": 420,
            "pellets_kg_per_ton": 26,
            "co2_price_euro_per_ton": 55
        },
        "fuel_prices": {
            "gas_cent_per_kwh": 12.0,
            "oil_cent_per_liter": 90.0,
            "wood_euro_per_ster": 80.0,
            "pellets_euro_per_ton": 350.0,
            "electricity_cent_per_kwh": 32.0
        },
        "operating_costs": {
            "gas": {"chimney_sweep": 120, "maintenance": 150, "repair": 200, "pump_power_kwh": 300},
            "oil": {"chimney_sweep": 120, "maintenance": 200, "repair": 250, "pump_power_kwh": 400},
            "pellets": {"chimney_sweep": 120, "maintenance": 300, "repair": 300, "pump_power_kwh": 500},
            "heatpump": {"chimney_sweep": 0, "maintenance": 150, "repair": 100, "pump_power_kwh": 0}
        }
    }
    
    try:
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    
    return default_config


# Import der notwendigen Funktionen
try:
    from calculations_heatpump import (
        calculate_annual_energy_consumption,
        calculate_building_heat_load,
        calculate_heatpump_economics,
        estimate_annual_heat_demand_kwh_from_consumption,
        estimate_heat_load_kw_from_annual_demand,
        get_default_heating_system_efficiency,
        recommend_heat_pump)
    from heatpump_advanced_features import (
        calculate_insulation_upgrade,
        compare_heating_systems,
        calculate_window_upgrade,
        create_renovation_roadmap)
    from heatpump_advanced_features_part2 import (
        optimize_heating_schedule,
        simulate_climate_scenarios,
        compare_heatpump_types,
        simulate_annual_load_profile)
    from heatpump_advanced_features_part3 import (
        calculate_subsidies,
        calculate_co2_footprint,
        monte_carlo_roi_analysis,
        benchmark_building)
    from heatpump_dynamic_tariff import (
        calculate_dynamic_tariff_comparison,
        calculate_stromcloud_economics,
        simulate_energy_management_system,
        calculate_smart_home_benefits,
        get_dynamic_tariff_pros_cons,
        compare_tariff_providers,
        simulate_annual_price_profile)
    from heatpump_dynamic_tariff_charts import (
        create_hourly_price_chart,
        create_annual_cost_chart,
        create_stromcloud_waterfall,
        create_load_shifting_heatmap)
    # Neue erweiterte Features (Phase 1-4)
    from heatpump_advanced_calculations import (
        calculate_jaz_prognosis,
        calculate_buffer_tank_size,
        calculate_price_scenarios,
        calculate_tax_benefits,
        calculate_noise_analysis,
        generate_annual_load_profile,
        calculate_smart_grid_benefits,
        calculate_grid_service_bonus,
        compare_hybrid_heating,
        calculate_lifecycle_co2,
        compare_refrigerants,
        calculate_maintenance_schedule,
        simulate_extreme_weather,
        compare_multiple_heatpumps,
        generate_extended_heatpump_report_data)
    from heatpump_advanced_charts import (
        create_system_3d_visualization,
        create_kpi_dashboard,
        create_jaz_comparison_chart,
        create_annual_profile_chart,
        create_noise_map,
        create_lifecycle_chart,
        create_price_scenario_chart,
        create_maintenance_timeline,
        create_comparison_radar_chart,
        create_comparison_bar_chart,
        create_comparison_heatmap,
        create_comparison_cost_chart)
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

    # CSS für Tabs - Mit Schattierungseffekten
    st.markdown("""
    <style>
    /* Tab-Liste: Transparenter Hintergrund mit Schatten */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 2px solid rgba(0, 0, 0, 0.1) !important;
        gap: 10px !important;
        padding: 0 0 5px 0 !important;
    }
    
    /* Tab-Buttons: Heller Hintergrund mit Schattierung */
    [data-testid="stTabs"] [data-baseweb="tab"] {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        border: none !important;
        color: #333333 !important;
        font-weight: 500 !important;
        padding: 12px 24px !important;
        border-radius: 8px 8px 0 0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 10px rgba(0, 0, 0, 0.15), inset 0 10px 10px rgba(0, 0, 0, 0.05) !important;
        margin-right: 4px !important;
    }
    
    [data-testid="stTabs"] [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        color: #ff8c00 !important;
        box-shadow: 0 10px 12px rgba(255, 140, 0, 0.3), inset 0 10px 10px rgba(0, 0, 0, 0.05) !important;
        transform: translateY(-2px) !important;
    }
    
    [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%) !important;
        color: #ff8c00 !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #ff8c00 !important;
        box-shadow: 0 10px 18px rgba(0, 0, 0, 0.2), 0 10px 10px rgba(255, 140, 0, 0.3), inset 0 10px 10px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Tab-Content: Transparenter Hintergrund */
    [data-testid="stTabs"] [data-baseweb="tab-panel"] {
        background-color: transparent !important;
        padding: 20px 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Tabs für verschiedene Analyse-Bereiche
    tabs = st.tabs([
        " Gebäudeanalyse",
        "Wärmepumpen-Auswahl",
        "Radiator-Check",
        "Wirtschaftlichkeit",
        "PV-Integration",
        " Erweiterte Analyse",  # NEU: Features 1.1-8.2
        " Renovierungs-Planer",
        " Optimierung",
        " Förderung & CO2",
        "ROI & Benchmarking",
        "Dynamischer Stromtarif",
        "Ergebnisse"
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
            st.info(" **Nur Wärmepumpe-Modus:** PV-Integration nicht erforderlich")
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
                        "**PV + Wärmepumpe-Modus:** Bitte führen Sie zuerst die PV-Analyse durch.")
                else:
                    st.info(
                        "PV-Daten optional. Für PV+WP-Integration bitte zuerst PV-Analyse durchführen.")
                pv_integration_data = None

    with tabs[5]:  # ERWEITERTE ANALYSE (NEU)
        if 'building_data' in st.session_state and 'heatpump_data' in st.session_state:
            render_advanced_analysis(texts, st.session_state.building_data, st.session_state.heatpump_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäude- und Wärmepumpen-Analyse durch.")

    with tabs[6]:  # Renovierungs-Planer
        if 'building_data' in st.session_state:
            render_renovation_planner(texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")

    with tabs[7]:  # Optimierung
        if 'building_data' in st.session_state:
            render_optimization_tools(texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")

    with tabs[8]:  # Förderung & CO2
        if 'building_data' in st.session_state:
            render_subsidy_co2(texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")

    with tabs[9]:  # ROI & Benchmarking
        if 'building_data' in st.session_state:
            render_roi_benchmarking(texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")

    with tabs[10]:  # Dynamischer Stromtarif
        if 'building_data' in st.session_state:
            render_dynamic_tariff_tab(texts, st.session_state.building_data)
        else:
            st.info("Bitte führen Sie zuerst die Gebäudeanalyse durch.")

    with tabs[11]:  # Ergebnisse
        render_results_summary(texts)


def render_building_analysis(texts: dict[str, str]) -> dict[str, Any]:
    """Gebäudeanalyse und Heizlastberechnung"""

    st.subheader(" Gebäudeanalyse")

    # CSS für Heizlast berechnen Button - Echter 3D-Button mit Rändern und Schattierungen
    st.markdown("""
    <style>
    /* Heizlast berechnen Button - 3D-Effekt mit prominenten Rändern */
    div[data-testid="stForm"] button[kind="primary"] {
        background: linear-gradient(135deg, #6c6c6c 0%, #4a4a4a 100%) !important;
        color: #ffffff !important;
        border: 3px solid #ff8c00 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px 24px !important;
        box-shadow: 
            0 10px 16px rgba(0, 0, 0, 0.5), 
            0 10px 10px rgba(0, 0, 0, 0.3),
            0 0 0 10px rgba(255, 140, 0, 0.2),
            inset 0 10px 10px rgba(255, 255, 255, 0.1),
            inset 0 -2px 10px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
    }
    
    div[data-testid="stForm"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7a7a7a 0%, #5a5a5a 100%) !important;
        border-color: #ff9900 !important;
        border-width: 3px !important;
        box-shadow: 
            0 12px 24px rgba(0, 0, 0, 0.6), 
            0 10px 12px rgba(0, 0, 0, 0.4),
            0 0 0 10px rgba(255, 140, 0, 0.4),
            0 0 20px rgba(255, 140, 0, 0.3),
            inset 0 10px 10px rgba(255, 255, 255, 0.15),
            inset 0 -2px 4px rgba(0, 0, 0, 0.25) !important;
        transform: translateY(-3px) !important;
    }
    
    div[data-testid="stForm"] button[kind="primary"]:active {
        background: linear-gradient(135deg, #5a5a5a 0%, #3a3a3a 100%) !important;
        border-color: #ff7700 !important;
        box-shadow: 
            0 10px 10px rgba(0, 0, 0, 0.4),
            0 0 0 10px rgba(255, 140, 0, 0.3),
            inset 0 10px 10px rgba(0, 0, 0, 0.4),
            inset 0 -1px 10px rgba(255, 255, 255, 0.05) !important;
        transform: translateY(1px) !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

        # Heizkosten-Konfiguration laden
        heating_config = load_heating_costs_config()
        fuel_prices = heating_config.get("fuel_prices", {})

        # Heizkosten-Eingabefelder
        st.markdown("**Jährliche Heizkosten**")
        st.caption("Geben Sie die Kosten für Ihre aktuelle(n) Heizart(en) ein")

        cost_col1, cost_col2, cost_col3 = st.columns(3)
        
        with cost_col1:
            st.markdown("**Gasheizung**")
            gas_monthly_cost = st.number_input(
                "Monatliche Gaskosten (€)",
                min_value=0.0,
                value=0.0,
                step=10.0,
                help="Monatlicher Abschlag für Erdgas"
            )
            gas_annual_cost = gas_monthly_cost * 12
            if gas_monthly_cost > 0:
                st.info(f"Jährlich: {format_german_number(gas_annual_cost, 2)} €")
        
        with cost_col2:
            st.markdown("**Ölheizung**")
            oil_price_raw = fuel_prices.get("oil_cent_per_liter", 90.0)
            if oil_price_raw != 0:
                default_oil_price = oil_price_raw / 100.0 * 1190.0  # Cent/L → €/Tonne
            else:
                default_oil_price = 0.0
            oil_price_per_ton = st.number_input(
                "Preis pro Tonne Heizöl (€)",
                min_value=0.0,
                value=float(default_oil_price),
                step=50.0,
                help="Aktueller Preis für 1.000 Liter Heizöl (Standard aus Admin-Konfiguration)"
            )
            # Berechnung: Liter → Tonnen (1 Tonne ≈ 1.190 Liter bei Dichte 0.84 kg/l)
            oil_tons = oil_l / 1190.0 if oil_l > 0 else 0
            oil_annual_cost = oil_tons * oil_price_per_ton
            if oil_price_per_ton > 0 and oil_l > 0:
                st.info(f"Jährlich: {format_german_number(oil_annual_cost, 2)} €")
        
        with cost_col3:
            st.markdown("**Holzheizung**")
            default_wood_price = fuel_prices.get("wood_euro_per_ster", 80.0)
            wood_price_per_ster = st.number_input(
                "Preis pro Ster Holz (€)",
                min_value=0.0,
                value=float(default_wood_price),
                step=10.0,
                help="Preis für 1 Ster (Raummeter) Brennholz (Standard aus Admin-Konfiguration)"
            )
            wood_annual_cost = wood_ster * wood_price_per_ster
            if wood_price_per_ster > 0 and wood_ster > 0:
                st.info(f"Jährlich: {format_german_number(wood_annual_cost, 2)} €")
        
        # Gesamtkosten berechnen und anzeigen
        total_annual_heating_cost = gas_annual_cost + oil_annual_cost + wood_annual_cost
        
        if total_annual_heating_cost > 0:
            st.markdown("---")
            st.markdown("###  **Gesamte jährliche Heizkosten**")
            st.metric(
                label="Summe aller Heizkosten",
                value=f"{format_german_number(total_annual_heating_cost, 2)} €",
                delta=None
            )
            
            # Breakdown anzeigen
            if gas_annual_cost > 0 or oil_annual_cost > 0 or wood_annual_cost > 0:
                breakdown_text = []
                if gas_annual_cost > 0:
                    breakdown_text.append(f"Gas: {format_german_number(gas_annual_cost, 2)} €")
                if oil_annual_cost > 0:
                    breakdown_text.append(f"Öl: {format_german_number(oil_annual_cost, 2)} €")
                if wood_annual_cost > 0:
                    breakdown_text.append(f"Holz: {format_german_number(wood_annual_cost, 2)} €")
                st.caption(" + ".join(breakdown_text))

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
                    100.0 if custom_eff else None)
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
                'heating_costs': {
                    'gas_monthly': gas_monthly_cost,
                    'gas_annual': gas_annual_cost,
                    'oil_price_per_ton': oil_price_per_ton,
                    'oil_annual': oil_annual_cost,
                    'wood_price_per_ster': wood_price_per_ster,
                    'wood_annual': wood_annual_cost,
                    'total_annual': total_annual_heating_cost
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
                if building_area != 0:
                    specific_load = heat_load * 1000 / building_area  # W/m²
                else:
                    specific_load = 0.0
                st.metric(
                    "Spezifische Heizlast",
                    f"{format_german_number(specific_load, 0)} W/m²",
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
    
    # CSS für Wärmepumpen-Auswahl-Buttons mit hellem Hintergrund und orangem Akzent
    st.markdown("""
    <style>
    /* Wählen-Button - Hell mit orangem Akzent und 3D-Schattierungen */
    div[data-testid="stVerticalBlock"] > div[data-testid="column"]:last-child button {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;
        color: #ff8c00 !important;
        border: 2px solid #ff8c00 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 10px 20px !important;
        box-shadow: 
            0 10px 12px rgba(255, 140, 0, 0.25),
            0 10px 10px rgba(0, 0, 0, 0.15),
            inset 0 1px 3px rgba(255, 255, 255, 0.8),
            inset 0 -1px 3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
    }
    
    div[data-testid="stVerticalBlock"] > div[data-testid="column"]:last-child button:hover {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        color: #ff6600 !important;
        border-color: #ff6600 !important;
        border-width: 2px !important;
        box-shadow: 
            0 10px 16px rgba(255, 140, 0, 0.4),
            0 10px 10px rgba(0, 0, 0, 0.2),
            0 0 20px rgba(255, 140, 0, 0.3),
            inset 0 1px 3px rgba(255, 255, 255, 0.9),
            inset 0 -1px 3px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-2px) scale(1.02) !important;
    }
    
    div[data-testid="stVerticalBlock"] > div[data-testid="column"]:last-child button:active {
        background: linear-gradient(135deg, #ffe6cc 0%, #ffd9b3 100%) !important;
        color: #ff5500 !important;
        border-color: #ff5500 !important;
        box-shadow: 
            0 10px 10px rgba(255, 140, 0, 0.3),
            0 10px 10px rgba(0, 0, 0, 0.2),
            inset 0 2px 4px rgba(0, 0, 0, 0.2),
            inset 0 -1px 2px rgba(255, 255, 255, 0.5) !important;
        transform: translateY(0px) scale(1) !important;
    }
    
    /* Primary Button (Testsieger) - Intensiverer oranger Akzent */
    div[data-testid="stVerticalBlock"] > div[data-testid="column"]:last-child button[kind="primary"] {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%) !important;
        color: #ff6600 !important;
        border: 3px solid #ff8c00 !important;
        box-shadow: 
            0 10px 16px rgba(255, 140, 0, 0.35),
            0 10px 10px rgba(0, 0, 0, 0.2),
            0 0 15px rgba(255, 140, 0, 0.2),
            inset 0 1px 3px rgba(255, 255, 255, 0.9),
            inset 0 -1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    
    div[data-testid="stVerticalBlock"] > div[data-testid="column"]:last-child button[kind="primary"]:hover {
        background: linear-gradient(135deg, #ffd9b3 0%, #ffcc99 100%) !important;
        color: #ff5500 !important;
        border-color: #ff6600 !important;
        box-shadow: 
            0 10px 20px rgba(255, 140, 0, 0.5),
            0 10px 10px rgba(0, 0, 0, 0.25),
            0 0 25px rgba(255, 140, 0, 0.4),
            inset 0 1px 3px rgba(255, 255, 255, 1),
            inset 0 -1px 3px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-3px) scale(1.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
        # Wahl zwischen automatischer Auswahl oder manuelle Produktauswahl
        selection_mode = st.selectbox(
            "Auswahl-Modus",
            options=[" Automatische Empfehlung", " Manuelle Produktauswahl"],
            index=0
        )
        
        # Initialisiere Variablen
        manufacturer_preference = None
        budget_category = None
        selected_manufacturer = None
        selected_product = None
        selected_power = None
        
        if selection_mode == " Manuelle Produktauswahl":
            from heatpump_products_database import (
                get_all_manufacturers,
                get_available_types_for_manufacturer,
                get_heatpump_models
            )
            
            # Hersteller-Dropdown
            manufacturers = ["Viessmann", "Buderus", "Vaillant"]
            selected_manufacturer = st.selectbox(
                " Hersteller",
                options=manufacturers,
                index=0
            )
            
            # Wärmepumpentyp basierend auf Hersteller
            available_types = get_available_types_for_manufacturer(selected_manufacturer)
            if available_types:
                selected_type = st.selectbox(
                    "Wärmepumpentyp",
                    options=available_types,
                    index=0
                )
                
                # Modelle für ausgewählten Hersteller und Typ
                models = get_heatpump_models(selected_manufacturer, selected_type)
                if models:
                    model_names = [m["model"] for m in models]
                    selected_model_name = st.selectbox(
                        "Produktmodell",
                        options=model_names,
                        index=0
                    )
                    
                    # Finde ausgewähltes Modell
                    selected_product = next(
                        (m for m in models if m["model"] == selected_model_name),
                        None
                    )
                    
                    if selected_product:
                        # Leistungsvariante auswählen
                        power_variants = selected_product["heating_power_kw"]
                        selected_power = st.selectbox(
                            "Heizleistung (kW)",
                            options=power_variants,
                            index=0
                        )
                        
                        # Lade konfigurierten Preis aus Admin-Einstellungen
                        price_info = None
                        price_text = selected_product['price_range']
                        try:
                            from admin_heatpump_settings_ui import get_heatpump_price
                            price_info = get_heatpump_price(
                                selected_manufacturer,
                                selected_type,
                                selected_model_name,
                                selected_power
                            )
                            if price_info and price_info.get('total_price_eur', 0) > 0:
                                total_price = price_info.get('total_price_eur', 0)
                                base_price = price_info.get('base_price_eur', 0)
                                install_price = price_info.get('installation_price_eur', 0)
                                price_text = f"**{format_german_number(total_price, 0)} €** (Gerät: {format_german_number(base_price, 0)} € + Installation: {format_german_number(install_price, 0)} €)"
                        except Exception:
                            pass
                        
                        # Rating und Awards anzeigen (falls vorhanden)
                        rating = selected_product.get('rating', 0)
                        awards = selected_product.get('awards', [])
                        
                        rating_text = ""
                        if rating > 0:
                            rating_stars = "" * int(rating)
                            rating_text = f"\n        - **Bewertung: {rating_stars} ({rating:.1f}/5.0)**"
                        
                        awards_text = ""
                        if awards:
                            awards_text = "\n        - **Auszeichnungen:** " + ", ".join([f"{a}" for a in awards])
                        
                        # Produktdetails anzeigen
                        st.info(f"""
                        **{selected_product['model']}**{rating_text}{awards_text}
                        - SCOP: {selected_product['scop']}
                        - Max. Vorlauftemperatur: {selected_product['max_flow_temp']}°C
                        - Kältemittel: {selected_product['refrigerant']}
                        - Features: {', '.join(selected_product['features'])}
                        - Preis: {price_text}
                        """)
        else:
            # Bisherige automatische Auswahl - NUR HERSTELLER AUS DATENBANK
            from heatpump_products_database import get_all_manufacturers
            
            available_manufacturers = ["Keine Präferenz"] + get_all_manufacturers()
            
            manufacturer_preference = st.selectbox(
                "Hersteller-Präferenz",
                options=available_manufacturers
            )

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

    # Button-Text abhängig vom Modus
    if selection_mode == " Manuelle Produktauswahl":
        button_text = "Ausgewählte Wärmepumpe übernehmen"
        button_help = "Übernimmt die manuell ausgewählte Wärmepumpe direkt"
    else:
        button_text = "Empfehlungen anzeigen"
        button_help = "Zeigt Top 5 Empfehlungen basierend auf Ihren Anforderungen"

    if st.button(button_text, use_container_width=True, type="primary", help=button_help):
        try:
            required_kw = heat_load * sizing_factor
            
            # ============================================================
            # MANUELLE PRODUKTAUSWAHL - DIREKTE ÜBERNAHME
            # ============================================================
            if selection_mode == " Manuelle Produktauswahl":
                if not selected_product or not selected_power:
                    st.error("Bitte wählen Sie zuerst einen Hersteller, Typ, Modell und Leistung aus!")
                    st.stop()
                
                # LADE PRODUKT AUS ECHTER DATENBANK
                from product_db import get_product_by_model_name
                
                db_product = get_product_by_model_name(selected_model_name)
                if db_product is None:
                    st.error(f"FEHLER: Produkt '{selected_model_name}' nicht in Datenbank gefunden!")
                    st.warning("Dieses Produkt kann dem Kunden nicht angeboten werden!")
                    st.stop()
                
                # Lade Preisinformationen (get_heatpump_price sucht jetzt ZUERST in product_db.py)
                price_info = None
                try:
                    from admin_heatpump_settings_ui import get_heatpump_price
                    price_info = get_heatpump_price(
                        selected_manufacturer,
                        selected_type,
                        selected_model_name,
                        selected_power
                    )
                except Exception as e:
                    st.warning(f"Konnte Preis nicht laden: {e}")
                    # Verwende Preis aus product_db als Fallback
                    if db_product.get('price_euro', 0) > 0:
                        base_price = float(db_product['price_euro'])
                        price_info = {
                            'base_price_eur': base_price,
                            'installation_price_eur': base_price * 0.4,
                            'total_price_eur': base_price * 1.4
                        }
                
                # Erstelle Wärmepumpen-Daten aus manueller Auswahl
                heatpump_data = {
                    'manufacturer': selected_manufacturer,
                    'type': selected_type,
                    'model': selected_model_name,
                    'heating_power': selected_power,
                    'scop': selected_product['scop'],
                    'cop': selected_product['scop'],
                    'max_flow_temp': selected_product['max_flow_temp'],
                    'features': selected_product['features'],
                    'refrigerant': selected_product['refrigerant'],
                    'price_range': selected_product['price_range'],
                    'rating': selected_product.get('rating', 0),
                    'awards': selected_product.get('awards', []),
                    'price': price_info.get('total_price_eur', 0) if price_info else 0,
                    'base_price': price_info.get('base_price_eur', 0) if price_info else 0,
                    'installation_price': price_info.get('installation_price_eur', 0) if price_info else 0,
                    'noise_level': 45,
                    'dimensions': "Standard",
                    'weight': 150,
                    'sizing_factor': sizing_factor,
                    'hot_water_storage': hot_water_storage,
                    'backup_heating': backup_heating,
                    'smart_control': smart_control,
                    'building_data': building_data,
                    'selected_heatpump': {
                        'manufacturer': selected_manufacturer,
                        'type': selected_type,
                        'model': selected_model_name,
                        'power_kw': selected_power,
                        'heating_power': selected_power,  # Für Konsistenz beide Keys
                        'scop': selected_product['scop'],
                        'max_flow_temp': selected_product['max_flow_temp'],
                        'features': selected_product['features'],
                        'refrigerant': selected_product['refrigerant'],
                        'price_range': selected_product['price_range'],
                        'rating': selected_product.get('rating', 0),
                        'awards': selected_product.get('awards', [])
                    }
                }
                
                st.session_state.heatpump_data = heatpump_data
                st.success(f"{selected_manufacturer} {selected_model_name} ({selected_power} kW) erfolgreich übernommen!")
                st.balloons()
                st.rerun()
            
            # ============================================================
            # AUTOMATISCHE EMPFEHLUNG - ZEIGE TOP 5
            # ============================================================
            else:
                # VALIDIERE GEGEN ECHTE PRODUKTDATENBANK
                from product_db import get_product_by_model_name
                from heatpump_products_database import HEATPUMP_PRODUCTS
                
                # Finde passende Modelle aus der Datenbank
                recommendations = []
                
                for manufacturer, types in HEATPUMP_PRODUCTS.items():
                    # Filter nach Hersteller-Präferenz (wenn vorhanden)
                    if manufacturer_preference and manufacturer_preference != "Keine Präferenz":
                        if manufacturer != manufacturer_preference:
                            continue
                
                    for hp_type, models in types.items():
                        for model in models:
                            model_name = model.get("model", "Unknown")
                            
                            # KRITISCH: PRÜFE OB PRODUKT IN ECHTER DATENBANK EXISTIERT
                            db_product = get_product_by_model_name(model_name)
                            if db_product is None:
                                # Produkt nicht in Datenbank -> ÜBERSPRINGEN
                                continue
                            
                            heating_powers = model.get("heating_power_kw", [])
                            scop = model.get("scop", 0)
                            max_flow_temp = model.get("max_flow_temp", 0)
                            features = model.get("features", [])
                            refrigerant = model.get("refrigerant", "")
                            price_range = model.get("price_range", "")
                            rating = model.get("rating", 0)
                            awards = model.get("awards", [])
                            
                            # Prüfe jede Leistungsvariante
                            for power in heating_powers:
                                if power >= required_kw * 0.9:  # Min. 90% der benötigten Leistung
                                    # Berechne Qualitäts-Score (Rating ist Hauptkriterium!)
                                    rating_score = rating * 20  # Rating 5.0 = 100 Punkte
                                    
                                    # Bonus für SCOP
                                    scop_score = scop * 8
                                    
                                    # Bonus für Auszeichnungen
                                    awards_score = len(awards) * 5
                                    
                                    # Malus für große Leistungsabweichung
                                    power_diff = abs(power - required_kw)
                                    if required_kw != 0:
                                        power_penalty = (power_diff / required_kw) * 10
                                    else:
                                        power_penalty = 0.0
                                    
                                    total_score = rating_score + scop_score + awards_score - power_penalty
                                    
                                    recommendations.append({
                                        "manufacturer": manufacturer,
                                        "type": hp_type,
                                        "model": model_name,
                                        "power_kw": power,
                                        "scop": scop,
                                        "max_flow_temp": max_flow_temp,
                                        "features": features,
                                        "refrigerant": refrigerant,
                                        "price_range": price_range,
                                        "rating": rating,
                                        "awards": awards,
                                        "score": total_score,
                                        "power_diff": power_diff
                                    })
                
                # Sortiere nach Qualitäts-Score (Rating dominiert)
                recommendations = sorted(recommendations, key=lambda x: x["score"], reverse=True)
                
                # LIMIT AUF TOP 5 (beste Bewertungen)
                recommendations = recommendations[:5]
            
            if recommendations:
                st.success(f"Top 5 Testsieger & beste Wärmepumpen aus der Datenbank!")
                
                # Speichere Empfehlungen im Session State
                st.session_state.heatpump_recommendations = recommendations
                st.session_state.required_power_kw = required_kw
                
                st.markdown("---")
                st.subheader(" Top 5 - Beste Wärmepumpen für Ihr Gebäude")
                st.caption(f"Benötigte Heizleistung: {required_kw:.1f} kW | Sortiert nach Bewertung & Qualität")
                
                # Zeige Top 5 mit Auswahl-Buttons
                for idx, rec in enumerate(recommendations, 1):  # NUR Top 5
                    with st.container():
                        # Header mit Ranking und Rating
                        if idx == 1:
                            medal = ""
                            title = f"{medal} **Testsieger: {rec['manufacturer']} {rec['model']}**"
                        elif idx == 2:
                            medal = ""
                            title = f"{medal} **Top-Alternative: {rec['manufacturer']} {rec['model']}**"
                        elif idx == 3:
                            medal = ""
                            title = f"{medal} **Empfohlen: {rec['manufacturer']} {rec['model']}**"
                        else:
                            medal = f"#{idx}"
                            title = f"{medal} **{rec['manufacturer']} {rec['model']}**"
                        
                        st.markdown(f"### {title}")
                        
                        # Rating-Anzeige
                        rating_stars = "" * int(rec['rating'])
                        st.markdown(f"**Bewertung: {rating_stars} ({rec['rating']:.1f}/5.0)**")
                        
                        # Auszeichnungen
                        if rec['awards']:
                            awards_text = " | ".join([f"{award}" for award in rec['awards']])
                            st.markdown(f"_{awards_text}_")
                        
                        # Lade konfigurierten Preis aus Admin-Einstellungen
                        price_info = None
                        try:
                            from admin_heatpump_settings_ui import get_heatpump_price
                            price_info = get_heatpump_price(
                                rec['manufacturer'],
                                rec['type'],
                                rec['model'],
                                rec['power_kw']
                            )
                        except Exception:
                            pass
                        
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                        
                        with col1:
                            st.metric("Heizleistung", f"{rec['power_kw']} kW")
                            st.caption(f"Typ: {rec['type']}")
                        
                        with col2:
                            st.metric("SCOP", f"{format_german_number(rec['scop'], 2)}")
                            st.caption(f"Max. Vorlauf: {rec['max_flow_temp']}°C")
                        
                        with col3:
                            # Zeige echten Preis oder Kategorie
                            if price_info and price_info.get('total_price_eur', 0) > 0:
                                total_price = price_info.get('total_price_eur', 0)
                                st.metric("Preis", f"{format_german_number(total_price, 0)} €")
                                st.caption(f"inkl. Installation")
                            else:
                                st.metric("Kältemittel", rec['refrigerant'])
                                st.caption(f"Preis: {rec['price_range']}")
                        
                        with col4:
                            # AUSWAHL-BUTTON FÜR JEDE EMPFEHLUNG
                            button_type = "primary" if idx == 1 else "secondary"
                            if st.button(
                                f"Wählen" if idx == 1 else "Auswählen",
                                key=f"select_hp_{idx}_{rec['manufacturer']}_{rec['model']}_{rec['power_kw']}",
                                type=button_type,
                                use_container_width=True
                            ):
                                # DEBUG: Zeige was WIRKLICH in rec steht
                                st.info(f"DEBUG: Button geklickt für {rec['manufacturer']} {rec['model']}")
                                
                                # Speichere ausgewählte Wärmepumpe
                                # Füge heating_power zu rec hinzu für Konsistenz
                                rec_with_heating_power = rec.copy()
                                rec_with_heating_power['heating_power'] = rec['power_kw']
                                
                                heatpump_data = {
                                    'manufacturer': rec['manufacturer'],
                                    'type': rec['type'],
                                    'model': rec['model'],
                                    'heating_power': rec['power_kw'],
                                    'scop': rec['scop'],
                                    'cop': rec['scop'],  # Vereinfacht
                                    'max_flow_temp': rec['max_flow_temp'],
                                    'features': rec['features'],
                                    'refrigerant': rec['refrigerant'],
                                    'price_range': rec['price_range'],
                                    'rating': rec['rating'],
                                    'awards': rec['awards'],
                                    'price': price_info.get('total_price_eur', 0) if price_info else 0,
                                    'base_price': price_info.get('base_price_eur', 0) if price_info else 0,
                                    'installation_price': price_info.get('installation_price_eur', 0) if price_info else 0,
                                    'noise_level': 45,  # Standardwert
                                    'dimensions': "Standard",
                                    'weight': 150,  # Standardwert
                                    'sizing_factor': sizing_factor,
                                    'hot_water_storage': hot_water_storage,
                                    'backup_heating': backup_heating,
                                    'smart_control': smart_control,
                                    'building_data': building_data,
                                    'selected_heatpump': rec_with_heating_power
                                }
                                
                                st.session_state.heatpump_data = heatpump_data
                                st.success(f"{rec['manufacturer']} {rec['model']} ({rec['power_kw']} kW) ausgewählt!")
                                st.balloons()
                                st.rerun()
                        
                        # Features und Preis-Details anzeigen
                        if rec['features']:
                            st.caption(f"Features: {', '.join(rec['features'][:4])}")
                        
                        # Preis-Breakdown anzeigen
                        if price_info and price_info.get('total_price_eur', 0) > 0:
                            st.caption(f"Gerätepreis: {format_german_number(price_info.get('base_price_eur', 0), 0)} € | Installation: {format_german_number(price_info.get('installation_price_eur', 0), 0)} € | **Gesamt: {format_german_number(price_info.get('total_price_eur', 0), 0)} €**")
                        
                        st.markdown("---")
                    
                    return st.session_state.get('heatpump_data')
                
                else:
                    st.warning("Keine passenden Wärmepumpen in der Datenbank gefunden. Bitte Parameter anpassen.")

        except Exception as e:
            st.error(f"Fehler bei der Wärmepumpen-Auswahl: {e}")
            import traceback
            st.code(traceback.format_exc())

    # Zeige aktuelle Auswahl, falls vorhanden
    if 'heatpump_data' in st.session_state and st.session_state.heatpump_data:
        selected = st.session_state.heatpump_data.get('selected_heatpump', {})
        
        # VALIDIERUNG: Nur erlaubte Hersteller
        allowed_manufacturers = ['Viessmann', 'Buderus', 'Vaillant']
        manufacturer = selected.get('manufacturer', '')
        
        if manufacturer not in allowed_manufacturers:
            # UNGÜLTIGER HERSTELLER -> SESSION LÖSCHEN
            st.warning(f"Ungültiger Hersteller '{manufacturer}' erkannt! Session wird zurückgesetzt...")
            del st.session_state.heatpump_data
            st.rerun()
        
        st.success("Wärmepumpe ausgewählt!")
        if selected:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**{manufacturer} {selected.get('model')}**")
            with col2:
                st.info(f"{selected.get('power_kw')} kW")
            with col3:
                st.info(f"SCOP: {selected.get('scop')}")
        
        return st.session_state.heatpump_data

    return None


def render_radiator_check(
        texts: dict[str, str], building_data: dict[str, Any]) -> dict[str, Any]:
    """Radiator-Kompatibilitätsprüfung für Wärmepumpe"""
    import streamlit as st
    from calculations_heatpump import (
        calculate_required_flow_temperature,
        check_radiator_compatibility
    )

    st.subheader("Radiator-Kompatibilitätsprüfung")

    heat_load_kw = building_data.get('heat_load_kw', 0)

    if heat_load_kw <= 0:
        st.error("Keine gültige Heizlast verfügbar. Bitte Gebäudeanalyse wiederholen.")
        return None

    st.info(f"Heizlast: {heat_load_kw:.1f} kW")

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

        submitted = st.form_submit_button("Kompatibilität prüfen", use_container_width=True)

        if submitted:
            try:
                # Berechne erforderliche Vorlauftemperatur
                flow_temp_result = calculate_required_flow_temperature(
                    heat_load_kw=heat_load_kw,
                    radiator_area_m2=radiator_area_m2,
                    room_temperature_c=indoor_temp_target
                )

                required_flow_temp = flow_temp_result['required_flow_temp_c']

                # Prüfe Kompatibilität
                compatibility_result = check_radiator_compatibility(
                    required_flow_temp_c=required_flow_temp
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
                st.markdown("### Prüfungsergebnis")

                # Status-Badge mit Farbe
                compatibility = compatibility_result['compatibility']
                if compatibility in ["Optimal", "Gut"]:
                    status_color = "🟢"
                    status_bg = "#d4edda"
                elif compatibility == "Grenzwertig":
                    status_color = "🟡"
                    status_bg = "#fff3cd"
                else:  # "Kritisch" oder "Ungeeignet"
                    status_color = ""
                    status_bg = "#f8d7da"

                st.markdown(
                    f'<div style="background-color: {status_bg}; padding: 20px; border-radius: 10px; text-align: center;">'
                    f'<h2>{status_color} {compatibility}</h2>'
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
                        f"{format_german_number(cop_loss_percent, 0)} %",
                        delta=f"-{format_german_number(cop_loss_percent, 0)}%" if cop_loss_percent > 0 else "Optimal"
                    )

                with col3:
                    upgrade_cost = compatibility_result.get('upgrade_cost_euros', 0)
                    if upgrade_cost > 0:
                        st.metric(
                            "Geschätzte Upgrade-Kosten",
                            f"{format_german_number(upgrade_cost, 0)} €"
                        )
                    else:
                        st.metric(
                            "Upgrade-Kosten",
                            "0,00 €",
                            delta="Keine erforderlich"
                        )

                # Empfehlungen
                st.markdown("### Empfehlungen")
                recommendation = compatibility_result.get('recommendation', '')
                st.info(recommendation)

                # Technische Details in Expander
                with st.expander("📊 Technische Details"):
                    col_tech1, col_tech2 = st.columns(2)
                    
                    with col_tech1:
                        st.metric("Erforderliche Vorlauftemperatur", f"{flow_temp_result.get('required_flow_temp_c', 0):.1f} °C")
                        st.metric("Erforderliche Rücklauftemperatur", f"{flow_temp_result.get('required_return_temp_c', 0):.1f} °C")
                        st.metric("Mittlere Temperatur", f"{flow_temp_result.get('required_mean_temp_c', 0):.1f} °C")
                    
                    with col_tech2:
                        st.metric("Radiator-Fläche", f"{flow_temp_result.get('radiator_area_m2', 0):.1f} m²")
                        st.metric("Ursprüngliche Vorlauftemperatur", f"{flow_temp_result.get('original_flow_temp_c', 0):.1f} °C")
                        st.metric("Heizlast", f"{flow_temp_result.get('heat_load_kw', 0):.1f} kW")

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
            "Ölpreis (ct/Liter)",
            min_value=50.0,
            max_value=150.0,
            value=90.0,
            step=1.0,
            help="Preis pro Liter Heizöl in Cent"
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

    # Zusätzliche Betriebskosten
    st.markdown("** Zusätzliche jährliche Betriebskosten**")
    cost_col1, cost_col2, cost_col3 = st.columns(3)
    
    with cost_col1:
        chimney_sweep_cost = st.number_input(
            "Schornsteinfeger (€/Jahr)",
            min_value=0.0,
            max_value=500.0,
            value=0.0,
            step=10.0,
            help="Kosten für Schornsteinfeger (entfällt meist bei WP)"
        )
        
        heating_system_power_kwh = st.number_input(
            "Stromverbrauch Heizungsanlage (kWh/Jahr)",
            min_value=0.0,
            max_value=2000.0,
            value=0.0,
            step=50.0,
            help="Zusätzlicher Stromverbrauch für Pumpen, Regelung etc."
        )
    
    with cost_col2:
        repair_cost_annual = st.number_input(
            "Reparaturkosten (€/Jahr)",
            min_value=0.0,
            max_value=2000.0,
            value=150.0,
            step=50.0,
            help="Durchschnittliche jährliche Reparaturkosten"
        )
    
    with cost_col3:
        st.markdown("**CO₂-Steuer-Faktoren**")
        st.caption("(Admin-Einstellungen verwenden)")
        
        # Hole CO2-Faktoren aus Admin-Settings (später implementiert)
        # Vorläufig: Hardcoded mit Option zur Anpassung
        co2_price_per_ton = st.number_input(
            "CO₂-Preis (€/Tonne)",
            min_value=0.0,
            max_value=200.0,
            value=55.0,
            step=5.0,
            help="Aktueller CO₂-Preis pro Tonne"
        )

    # Berechnung durchführen
    if st.button(" Wirtschaftlichkeit berechnen", use_container_width=True):
        try:
            # Jahresenergiebedarf berechnen (an calculations_heatpump angepasst)
            # Näherung: 1.800 Volllaststunden
            heating_hours = 1800
            heat_demand_kwh = building_data['heat_load_kw'] * heating_hours

            # Wärmepumpen-Stromverbrauch
            if heatpump != 0:
                hp_electricity_consumption = heat_demand_kwh / heatpump['scop']
            else:
                hp_electricity_consumption = 0.0

            # CO₂-Emissionen und Kosten berechnen
            # Alte Heizung CO₂-Kosten
            current_system = building_data['heating_system']
            co2_emission_old_kg = 0
            co2_cost_old = 0
            
            if 'Gas' in current_system:
                # Gas: 428g CO₂ pro kWh (Erdgas)
                co2_emission_old_kg = heat_demand_kwh * 0.428  # kg CO₂
                co2_cost_old = (co2_emission_old_kg / 1000) * co2_price_per_ton  # Tonnen → Euro
                fuel_cost_old = heat_demand_kwh * gas_price / 100
            elif 'Öl' in current_system:
                # Heizöl: 1 Liter = 2.66 kg CO₂
                # 1 Liter Heizöl ≈ 10 kWh
                oil_liters = heat_demand_kwh / 10
                co2_emission_old_kg = oil_liters * 2.66  # kg CO₂
                co2_cost_old = (co2_emission_old_kg / 1000) * co2_price_per_ton
                fuel_cost_old = heat_demand_kwh * oil_price / 100
            else:
                fuel_cost_old = heat_demand_kwh * electricity_price / 100
            
            # Wärmepumpe CO₂-Kosten (Strommix Deutschland: ~420g/kWh)
            co2_emission_wp_kg = hp_electricity_consumption * 0.420  # kg CO₂
            co2_cost_wp = (co2_emission_wp_kg / 1000) * co2_price_per_ton
            
            # Stromkosten für Heizungsanlage (Pumpen, Regelung)
            heating_system_power_cost = heating_system_power_kwh * electricity_price / 100
            
            # Gesamte jährliche Betriebskosten
            annual_hp_cost = (
                hp_electricity_consumption * electricity_price / 100  # WP-Strom
                + heating_system_power_cost  # Zusätzlicher Strom
                + maintenance_cost_annual  # Wartung
                + repair_cost_annual  # Reparatur
                + chimney_sweep_cost  # Schornsteinfeger
                + co2_cost_wp  # CO₂-Steuer
            )
            
            annual_old_cost = (
                fuel_cost_old  # Brennstoffkosten
                + heating_system_power_cost  # Strom (falls alte Heizung)
                + maintenance_cost_annual * 1.2  # Alte Heizung hat höhere Wartungskosten
                + repair_cost_annual * 1.5  # Höhere Reparaturkosten
                + chimney_sweep_cost  # Schornsteinfeger (bei Öl/Gas)
                + co2_cost_old  # CO₂-Steuer
            )
            
            # Kosten berechnen
            # Hole Preis aus heatpump_data (dynamisch konfiguriert)
            heatpump_price = heatpump_data.get('price', 0)
            
            # Fallback: Wenn kein Preis gesetzt, aus Admin-Konfiguration laden
            if heatpump_price == 0:
                try:
                    from admin_heatpump_settings_ui import get_heatpump_price
                    price_info = get_heatpump_price(
                        heatpump.get('manufacturer', ''),
                        heatpump.get('type', ''),
                        heatpump.get('model', ''),
                        heatpump.get('power_kw') or heatpump.get('heating_power', 0)
                    )
                    heatpump_price = price_info.get('total_price_eur', 0)
                except Exception:
                    # Letzter Fallback: Schätzung basierend auf Leistung
                    power = heatpump.get('power_kw') or heatpump.get('heating_power', 10)
                    heatpump_price = 800 + (power * 200)
            
            total_investment = heatpump_price + installation_cost - subsidy_amount

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
                    f"{format_german_number(total_investment, 0)} €",
                    help="Anschaffung + Installation - Förderung"
                )

            with col_kpi2:
                st.metric(
                    "Jährliche Ersparnis",
                    f"{format_german_number(annual_savings, 0)} €",
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
                    f"{format_german_number((annual_savings * 20 - total_investment), 0)} €",
                    help="Gesamtersparnis über 20 Jahre"
                )

            # Detaillierte Kostenaufstellung
            st.subheader(" Kostenaufstellung")

            cost_breakdown = pd.DataFrame({
                'Position': [
                    'Wärmepumpe',
                    'Installation',
                    'Förderung BEG',
                    ' Netto-Investition',
                    '',
                    'Jährlicher Stromverbrauch WP',
                    'Jährliche Stromkosten WP',
                    ' Jährliche Wartungskosten',
                    ' Jährliche Reparaturkosten',
                    ' Stromverbrauch Heizung',
                    ' Schornsteinfeger',
                    ' CO₂-Steuer WP',
                    ' Gesamte jährliche Kosten WP',
                    '',
                    ' Brennstoffkosten alte Heizung',
                    ' Wartung alte Heizung',
                    ' Reparatur alte Heizung',
                    ' Strom alte Heizung',
                    ' Schornsteinfeger',
                    ' CO₂-Steuer alte Heizung',
                    ' Gesamte jährliche Kosten alt',
                    '',
                    'Jährliche Ersparnis',
                    'CO₂-Einsparung (kg/Jahr)'
                ],
                'Betrag': [
                    f"{format_german_number(heatpump_price, 0)} €",
                    f"{format_german_number(installation_cost, 0)} €",
                    f"-{format_german_number(subsidy_amount, 0)} €",
                    f"{format_german_number(total_investment, 0)} €",
                    '',
                    f"{format_german_number(hp_electricity_consumption, 0)} kWh",
                    f"{format_german_number(hp_electricity_consumption * electricity_price / 100, 0)} €",
                    f"{format_german_number(maintenance_cost_annual, 0)} €",
                    f"{format_german_number(repair_cost_annual, 0)} €",
                    f"{format_german_number(heating_system_power_cost, 2)} €",
                    f"{format_german_number(chimney_sweep_cost, 0)} €",
                    f"{format_german_number(co2_cost_wp, 2)} €",
                    f"{format_german_number(annual_hp_cost, 2)} €",
                    '',
                    f"{format_german_number(fuel_cost_old, 2)} €" if 'fuel_cost_old' in locals() else "0,00 €",
                    f"{format_german_number(maintenance_cost_annual * 1.2, 0)} €",
                    f"{format_german_number(repair_cost_annual * 1.5, 0)} €",
                    f"{format_german_number(heating_system_power_cost, 2)} €",
                    f"{format_german_number(chimney_sweep_cost, 0)} €",
                    f"{format_german_number(co2_cost_old, 2)} €",
                    f"{format_german_number(annual_old_cost, 2)} €",
                    '',
                    f"{format_german_number(annual_savings, 2)} €",
                    f"{format_german_number((co2_emission_old_kg - co2_emission_wp_kg), 0)} kg"
                ]
            })

            st.dataframe(
                cost_breakdown,
                use_container_width=True,
                hide_index=True)
            
            # Zusätzliche Metriken für CO₂
            st.markdown("### Umweltbilanz")
            co2_col1, co2_col2, co2_col3 = st.columns(3)
            
            with co2_col1:
                st.metric(
                    "CO₂-Emission alt",
                    f"{format_german_number(co2_emission_old_kg, 0)} kg/Jahr",
                    help="Jährliche CO₂-Emissionen alte Heizung"
                )
            
            with co2_col2:
                st.metric(
                    "CO₂-Emission Wärmepumpe",
                    f"{format_german_number(co2_emission_wp_kg, 0)} kg/Jahr",
                    delta=f"-{((1 - co2_emission_wp_kg/co2_emission_old_kg) * 100) if co2_emission_old_kg > 0 else 0:.1f}%" if co2_emission_old_kg != 0 else "0.0%",
                    delta_color="inverse",
                    help="Jährliche CO₂-Emissionen mit Wärmepumpe"
                )
            
            with co2_col3:
                st.metric(
                    "CO₂-Einsparung 20 Jahre",
                    f"{(co2_emission_old_kg - co2_emission_wp_kg) * 20 / 1000:,.1f} Tonnen",
                    help="Gesamte CO₂-Einsparung über 20 Jahre"
                )

            # Cashflow-Diagramm
            st.subheader(" Cashflow-Entwicklung")

            years = list(range(21))
            cumulative_cashflow = [-total_investment]

            for year in range(1, 21):
                cumulative_cashflow.append(
                    cumulative_cashflow[-1] + annual_savings)

            fig_cashflow = go.Figure()

            # Formatiere Werte für Hover-Text
            cashflow_formatted = [format_german_number(val, 2) for val in cumulative_cashflow]
            
            fig_cashflow.add_trace(go.Scatter(
                x=years,
                y=cumulative_cashflow,
                mode='lines+markers',
                name='Kumulierter Cashflow',
                line=dict(color='#1f77b4', width=3),
                hovertemplate='Jahr: %{x}<br>Cashflow: %{text} €<extra></extra>',
                text=cashflow_formatted
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
                hovermode='x unified',
                separators=',.')  # Deutsche Trennzeichen für Achsen
            
            # SHADCN UI THEME ANWENDEN
            apply_chart_theme(fig_cashflow)

            st.plotly_chart(fig_cashflow, use_container_width=True)

            # NEU: CO2-Kosten und 20-Jahres-Vergleich
            st.markdown("---")
            st.subheader(" CO2-Kosten & Langfristvergleich")

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
                    annual_consumption_kwh=heat_demand_kwh,
                    fuel_type=fuel_type,
                    co2_price_per_ton=55,  # Aktueller CO2-Preis
                    year=2025
                )

                # 20-Jahres-Systemvergleich
                building_data_dict = {
                    "annual_heat_demand_kwh": heat_demand_kwh
                }
                heatpump_data_dict = {
                    "investment_cost_eur": heatpump_price + installation_cost,
                    "jaz": heatpump['scop'],
                    "electricity_price_kwh": electricity_price / 100
                }
                comparison_result = compare_heating_systems_20_years(
                    building_data=building_data_dict,
                    heatpump_data=heatpump_data_dict,
                    fossil_heating_type=fuel_type
                )

                # CO2-Kosten-Vergleich visualisieren
                col_co2_1, col_co2_2, col_co2_3 = st.columns(3)

                with col_co2_1:
                    st.metric(
                        f"CO2-Kosten {fuel_type} (Jahr 1)",
                        f"{format_german_number(co2_cost_result.get('annual_co2_cost_euros', co2_cost_result.get('annual_co2_cost_eur', 0)), 0)} €",  # FIX: Beide Keys prüfen
                        help="CO2-Preis × Emissionen pro Jahr"
                    )

                with col_co2_2:
                    st.metric(
                        "CO2-Einsparung (20 Jahre)",
                        f"{comparison_result['comparison'].get('co2_savings_tons_20years', comparison_result.get('co2_savings_tons_20y', 0)):,.1f} t",  # FIX: Beide Keys prüfen
                        help="Eingesparte CO2-Emissionen über 20 Jahre"
                    )

                with col_co2_3:
                    # FIX: Berechne monetäre CO2-Ersparnis wenn nicht vorhanden
                    co2_savings_tons = comparison_result['comparison'].get('co2_savings_tons_20years', 0)
                    co2_price = 55  # €/Tonne
                    monetary_savings = comparison_result.get('co2_savings_monetary_20y', co2_savings_tons * co2_price)
                    
                    st.metric(
                        "Monetäre CO2-Ersparnis",
                        f"{format_german_number(monetary_savings, 0)} €",
                        help="Vermiedene CO2-Kosten über 20 Jahre"
                    )

                # 20-Jahres-Kostenvergleich (NPV)
                st.markdown("### 20-Jahres-Kostenvergleich (NPV)")

                years_npv = list(range(1, 21))
                # FIX: Hole Werte aus korrekter Struktur
                wp_net_inv = comparison_result.get('wp_net_investment', comparison_result.get('heatpump', {}).get('investment_net_eur', 20000))
                fossil_inv = comparison_result.get('fossil_investment', comparison_result.get('fossil_heating', {}).get('investment', 12800))
                
                wp_cumulative = [wp_net_inv]
                fossil_cumulative = [fossil_inv]

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
                    # FIX: Beide Keys prüfen
                    co2_cost_year1 = co2_cost_result.get('annual_co2_cost_euros', co2_cost_result.get('annual_co2_cost_eur', 0))
                    fossil_annual_cost = (
                        heat_demand_kwh *
                        fossil_fuel_price *
                        annual_cost_increase_factor +
                        co2_cost_year1 * (1 + 0.05) ** year +  # CO2-Preis steigt 5%/Jahr
                        maintenance_cost_annual * 1.5  # Fossil-Wartung teurer
                    )
                    fossil_cumulative.append(fossil_cumulative[-1] + fossil_annual_cost)

                # Chart: 20-Jahres-Kostenvergleich
                fig_20y = go.Figure()

                # Formatiere Werte für Hover-Text
                wp_cumulative_formatted = [format_german_number(val, 2) for val in wp_cumulative]
                fossil_cumulative_formatted = [format_german_number(val, 2) for val in fossil_cumulative]

                fig_20y.add_trace(go.Scatter(
                    x=years_npv,
                    y=wp_cumulative,
                    mode='lines+markers',
                    name='Wärmepumpe',
                    line=dict(color='#2E7D32', width=3),
                    fill='tonexty',
                    hovertemplate='Jahr: %{x}<br>Kosten: %{text} €<extra></extra>',
                    text=wp_cumulative_formatted
                ))

                fig_20y.add_trace(go.Scatter(
                    x=years_npv,
                    y=fossil_cumulative,
                    mode='lines+markers',
                    name=f'{fuel_type}-Heizung',
                    line=dict(color='#C62828', width=3),
                    hovertemplate='Jahr: %{x}<br>Kosten: %{text} €<extra></extra>',
                    text=fossil_cumulative_formatted
                ))

                # Amortisationspunkt markieren
                payback_years = comparison_result.get('payback_years', comparison_result.get('comparison', {}).get('payback_years', 15.0))
                if payback_years < 20:
                    fig_20y.add_vline(
                        x=payback_years,
                        line_dash="dash",
                        line_color="orange",
                        opacity=0.7,
                        annotation_text=f"Amortisation: {payback_years:.1f} Jahre"
                    )

                fig_20y.update_layout(
                    title="Kumulierte Gesamtkosten über 20 Jahre (inkl. CO2-Kosten)",
                    xaxis_title="Jahre",
                    yaxis_title="Kumulierte Kosten (€)",
                    hovermode='x unified',
                    height=500,
                    separators=',.'  # Deutsche Trennzeichen
                    )
                
                # SHADCN UI THEME ANWENDEN
                apply_chart_theme(fig_20y)

                st.plotly_chart(fig_20y, use_container_width=True)

                # Zusammenfassung 20-Jahres-Vergleich
                st.markdown("### Ergebnis 20-Jahres-Vergleich")

                col_res1, col_res2, col_res3, col_res4 = st.columns(4)

                # Keys mit Fallbacks aus nested structure
                wp_total_20y = comparison_result.get('wp_total_cost_20y', 
                    comparison_result.get('heatpump', {}).get('total_cost_20years_eur', 0))
                fossil_total_20y = comparison_result.get('fossil_total_cost_20y', 
                    comparison_result.get('fossil_heating', {}).get('total_cost_20years_eur', 0))

                with col_res1:
                    st.metric(
                        "WP Gesamtkosten (20J)",
                        f"{format_german_number(wp_total_20y, 0)} €"
                    )

                with col_res2:
                    st.metric(
                        f"{fuel_type} Gesamtkosten (20J)",
                        f"{format_german_number(fossil_total_20y, 0)} €"
                    )

                with col_res3:
                    total_savings_20y = fossil_total_20y - wp_total_20y
                    st.metric(
                        "Ersparnis (20J)",
                        f"{format_german_number(total_savings_20y, 0)} €",
                        delta=f"+{(total_savings_20y / fossil_total_20y * 100):.1f}%" if fossil_total_20y > 0 else "0%"
                    )

                with col_res4:
                    st.metric(
                        "Amortisation",
                        f"{payback_years:.1f} Jahre"
                    )

                # CO2-Emissionen visualisieren
                st.markdown("### CO2-Emissionen im Vergleich")

                # FIX: Korrekter Key ist 'annual_co2_tons'
                annual_co2_tons = co2_cost_result.get('annual_co2_tons', co2_cost_result.get('annual_emissions_tons_co2', 5.0))

                fig_co2 = go.Figure(data=[
                    go.Bar(
                        name='Wärmepumpe',
                        x=['Jährlich', '20 Jahre'],
                        y=[
                            annual_co2_tons * 0.3,  # WP: ~30% der fossilen Emissionen (bei deutschem Strommix)
                            annual_co2_tons * 0.3 * 20
                        ],
                        marker_color='#2E7D32'
                    ),
                    go.Bar(
                        name=f'{fuel_type}-Heizung',
                        x=['Jährlich', '20 Jahre'],
                        y=[
                            annual_co2_tons,
                            annual_co2_tons * 20
                        ],
                        marker_color='#C62828'
                    )
                ])

                fig_co2.update_layout(
                    title="CO2-Emissionen: Wärmepumpe vs. Fossil",
                    yaxis_title="CO2-Emissionen (Tonnen)",
                    barmode='group',
                    height=400,
                    separators=',.'  # Deutsche Trennzeichen
                )
                
                # SHADCN UI THEME ANWENDEN
                apply_chart_theme(fig_co2)

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
                'subsidy_amount': subsidy_amount,
                # Neue erweiterte Kostenfelder
                'chimney_sweep_cost': chimney_sweep_cost,
                'heating_system_power_kwh': heating_system_power_kwh,
                'heating_system_power_cost': heating_system_power_cost,
                'repair_cost_annual': repair_cost_annual,
                'maintenance_cost_annual': maintenance_cost_annual,
                'co2_price_per_ton': co2_price_per_ton,
                'co2_emission_old_kg': co2_emission_old_kg,
                'co2_emission_wp_kg': co2_emission_wp_kg,
                'co2_cost_old': co2_cost_old,
                'co2_cost_wp': co2_cost_wp,
                'co2_savings_kg_annual': co2_emission_old_kg - co2_emission_wp_kg,
                'co2_savings_tons_20y': (co2_emission_old_kg - co2_emission_wp_kg) * 20 / 1000,
                'fuel_cost_old': fuel_cost_old if 'fuel_cost_old' in locals() else 0
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
            pv_size_kwp:.1f} kWp, Jahresproduktion: {format_german_number(
            pv_production_annual, 0)} kWh")

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
            f"{format_german_number(pv_coverage_hp * 100, 0)}%",
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
            f"{format_german_number(annual_pv_savings_hp, 0)} €/Jahr",
            help="Ersparnis durch PV-Eigenverbrauch der WP"
        )

        # Gesamtoptimierung
        total_annual_savings = economics_data['annual_savings'] + \
            annual_pv_savings_hp

        st.metric(
            "Gesamte jährliche Ersparnis",
            f"{format_german_number(total_annual_savings, 0)} €/Jahr",
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
        hovermode='x unified',
        separators=',.'  # Deutsche Trennzeichen
    )
    
    # SHADCN UI THEME ANWENDEN
    apply_chart_theme(fig_profile)

    st.plotly_chart(fig_profile, use_container_width=True)

    # NEU: Energiefluss-Sankey-Diagramm
    st.markdown("---")
    st.subheader(" Energiefluss-Visualisierung")

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
                    " PV-Anlage",           # 0
                    "Stromnetz",            # 1
                    " Wärmepumpe",          # 2
                    " Wärme (Heizung)",     # 3
                    " Einspeisung"          # 4
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
                    f"{format_german_number(pv_to_hp, 0)} kWh (PV-Eigenverbrauch)",
                    f"{format_german_number(grid_to_hp, 0)} kWh (Netzbezug)",
                    f"{format_german_number(heat_output, 0)} kWh (Wärmeerzeugung, JAZ={heatpump_data['selected_heatpump']['scop']:.1f})",
                    f"{format_german_number(pv_to_grid, 0)} kWh (Netzeinspeisung)"
                ]
            )
        )])

        fig_sankey.update_layout(
            title=f"Energiefluss: PV + Wärmepumpe (Jahresbetrachtung)<br><sub>PV-Deckungsgrad WP: {format_german_number(pv_coverage_hp*100, 0)}%</sub>",
            font=dict(size=12),
            height=500,
            separators=',.'  # Deutsche Trennzeichen
        )
        
        # SHADCN UI THEME ANWENDEN
        apply_chart_theme(fig_sankey)

        st.plotly_chart(fig_sankey, use_container_width=True)

        # Energiebilanz-Tabelle
        with st.expander("Detaillierte Energiebilanz"):
            energy_balance = pd.DataFrame({
                'Energiestrom': [
                    'PV-Erzeugung gesamt',
                    ' Eigenverbrauch Wärmepumpe',
                    ' Netzeinspeisung',
                    'Strombezug Wärmepumpe',
                    ' aus PV-Eigenverbrauch',
                    ' aus Stromnetz',
                    'Wärmeerzeugung (Output)',
                    'Jahresarbeitszahl (JAZ)'
                ],
                'Menge': [
                    f"{format_german_number(pv_production_annual, 0)} kWh",
                    f"{format_german_number(pv_to_hp, 0)} kWh ({pv_to_hp/pv_production_annual*100:.1f}%)",
                    f"{format_german_number(pv_to_grid, 0)} kWh ({pv_to_grid/pv_production_annual*100:.1f}%)",
                    f"{format_german_number(hp_consumption, 0)} kWh",
                    f"{format_german_number(pv_to_hp, 0)} kWh ({format_german_number(pv_coverage_hp*100, 0)}%)",
                    f"{format_german_number(grid_to_hp, 0)} kWh ({format_german_number((1-pv_coverage_hp)*100, 0)}%)",
                    f"{format_german_number(heat_output, 0)} kWh",
                    f"{format_german_number(heatpump_data['selected_heatpump']['scop'], 2)}"
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
                    # VALIDIERUNG: Nur erlaubte Hersteller
                    allowed_manufacturers = ['Viessmann', 'Buderus', 'Vaillant']
                    if top.get('manufacturer') not in allowed_manufacturers:
                        # Ungültiger Hersteller -> ÜBERSPRINGEN
                        st.warning(f"Auto-Fallback: Ungültiger Hersteller '{top.get('manufacturer')}' übersprungen!")
                    else:
                        # OK: Speichere nur valide Produkte
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

            # Hole Preis aus heatpump_data (dynamisch konfiguriert)
            heatpump_price = heatpump_data.get('price', 0)
            
            # Fallback: Wenn kein Preis gesetzt, aus Admin-Konfiguration laden
            if heatpump_price == 0:
                try:
                    from admin_heatpump_settings_ui import get_heatpump_price
                    price_info = get_heatpump_price(
                        heatpump.get('manufacturer', ''),
                        heatpump.get('type', ''),
                        heatpump.get('model', ''),
                        heatpump.get('power_kw') or heatpump.get('heating_power', 0)
                    )
                    heatpump_price = price_info.get('total_price_eur', 0)
                except Exception:
                    # Letzter Fallback: Schätzung basierend auf Leistung
                    power = heatpump.get('power_kw') or heatpump.get('heating_power', 10)
                    heatpump_price = 800 + (power * 200)

            total_investment = heatpump_price + installation_cost - subsidy_amount
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
        # Unterstütze beide Key-Formate
        heating_power = heatpump.get('heating_power') or heatpump.get('power_kw', 0)
        manufacturer = heatpump.get('manufacturer', 'N/A')
        model = heatpump.get('model', 'N/A')
        scop = heatpump.get('scop', 0)
        
        st.metric(
            "Wärmepumpe",
            f"{heating_power} kW",
            help=f"{manufacturer} {model}"
        )

        st.metric(
            "SCOP",
            f"{scop:.1f}",
            help="Saisonale Leistungszahl"
        )

    with col_summary3:
        st.metric(
            "Investition",
            f"{format_german_number(economics_data['total_investment'], 0)} €",
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
            f"{format_german_number(annual_savings, 0)} €",
            help="Gegenüber altem System"
        )

        savings_20_years = annual_savings * 20 - \
            economics_data['total_investment']
        st.metric(
            "20-Jahre-Ersparnis",
            f"{format_german_number(savings_20_years, 0)} €",
            help="Gesamte Ersparnis über 20 Jahre"
        )

    # NEU: 3D-Visualisierung
    st.markdown("---")
    with st.expander(" 3D-Gebäudevisualisierung mit Wärmepumpe", expanded=False):
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
            " **Smart Control aktivieren** - Optimiert Eigenverbrauch und reduziert Kosten")

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
                    st.success("PDF erfolgreich erstellt!")
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

    st.subheader(" 3D-Gebäudevisualisierung mit Energiefluss")

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
            if num_frames != 0:
                angle = i * (360 / num_frames)
            else:
                angle = 0.0

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
                                x=camera_x / camera_distance * 1.5 if camera_distance != 0 else 0.0,
                                y=camera_y / camera_distance * 1.5 if camera_distance != 0 else 0.0,
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
                    text=f" Gebäudevisualisierung mit Wärmepumpe<br><sub>Fläche: {format_german_number(building_area, 0)}m² | Höhe: {building_height + roof_height:.1f}m</sub>",
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
                                label=' 360° Animation',
                                method='animate',
                                args=[None, dict(
                                    frame=dict(duration=100, redraw=True),
                                    fromcurrent=True,
                                    mode='immediate',
                                    transition=dict(duration=50)
                                )]
                            ),
                            dict(
                                label='⏸ Pause',
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
        
        # SHADCN UI THEME ANWENDEN
        apply_chart_theme(fig)

        st.plotly_chart(fig, use_container_width=True)

        # Info-Box mit Energiedaten
        if heatpump_data:
            col1, col2, col3 = st.columns(3)

            with col1:
                heat_load = building_data.get('heat_load_kw', 0)
                st.metric(
                    " Heizlast",
                    f"{heat_load:.1f} kW",
                    help="Maximale benötigte Heizleistung"
                )

            with col2:
                hp = heatpump_data.get('selected_heatpump', {})
                st.metric(
                    " WP-Leistung",
                    f"{hp.get('heating_power', 0):.1f} kW",
                    help="Installierte Wärmepumpenleistung"
                )

            with col3:
                st.metric(
                    "JAZ",
                    f"{hp.get('scop', 0):.1f}",
                    help="Jahresarbeitszahl (Effizienz)"
                )

        st.info(
            "**Interaktiv**: Klicken Sie auf ' 360° Animation' für automatische Rotation. "
            "Sie können das Modell auch manuell mit der Maus drehen."
        )

    except Exception as e:
        st.error(f"Fehler bei der 3D-Visualisierung: {e}")
        st.warning("3D-Animation konnte nicht erstellt werden. Bitte prüfen Sie die Gebäudedaten.")


def get_heatpump_database() -> list[dict[str, Any]]:
    """
    ECHTE Wärmepumpen aus Produktdatenbank
    NUR: Viessmann, Buderus, Vaillant
    """
    from product_db import get_db_connection
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # NUR Viessmann, Buderus, Vaillant
        cursor.execute("""
            SELECT manufacturer, model_name, category, description, price_euro
            FROM products 
            WHERE category LIKE '%Wärmepumpe%'
            AND manufacturer IN ('Viessmann', 'Buderus', 'Vaillant')
            ORDER BY manufacturer, model_name
        """)
        
        products = cursor.fetchall()
        conn.close()
        
        # Konvertiere zu altem Format für Kompatibilität
        result = []
        for mfr, model, category, desc, price in products:
            # Typ aus Kategorie extrahieren
            hp_type = "Luft-Wasser-Wärmepumpe"  # Default
            if "Sole" in category:
                hp_type = "Sole-Wasser-Wärmepumpe"
            elif "Wasser-Wasser" in category:
                hp_type = "Wasser-Wasser-Wärmepumpe"
            
            # Leistung aus Modellname extrahieren (z.B. "Vitocal 250-A 10kW" -> 10.0)
            import re
            power_match = re.search(r'(\d+(?:\.\d+)?)\s*kW', model)
            heating_power = float(power_match.group(1)) if power_match else 10.0
            
            result.append({
                'manufacturer': mfr,
                'model': model,
                'type': hp_type,
                'heating_power': heating_power,
                'cop': 4.0,  # Standardwerte
                'scop': 4.3,
                'price': float(price or 0),
                'noise_level': 35,
                'dimensions': '1.2 x 0.6 x 1.4 m',
                'weight': 120,
                'efficiency_class': 'A+++'
            })
        
        return result if result else []
        
    except Exception as e:
        st.warning(f"Produktdatenbank konnte nicht geladen werden: {e}")
        return []


# ============================================================================
# NEUE FEATURES: UI-FUNKTIONEN
# ============================================================================

def render_renovation_planner(texts: dict[str, str], building_data: dict[str, Any]):
    """Renovierungs-Planer Tab (Features 1-4)"""
    
    st.subheader(" Renovierungs-Planer")
    st.markdown("Optimale Sanierungsmaßnahmen für maximale Effizienz")
    
    # Feature 1: Dämmungs-Upgrade-Rechner
    with st.expander(" Dämmungs-Upgrade-Rechner", expanded=True):
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
            
            st.success(f"**Gesamt-Investition:** {format_german_number(result['total_investment_eur'], 2)} €")
            st.success(f" **Jährliche Einsparung:** {format_german_number(result['total_annual_savings_eur'], 2)} €/Jahr")
            st.success(f"⏱ **Amortisation:** {result['total_payback_years']:.1f} Jahre")
            st.success(f"**Gewinn nach 20 Jahren:** {format_german_number(result['savings_20_years_eur'], 2)} €")
            
            st.markdown("### Optimale Reihenfolge (nach ROI)")
            for i, measure in enumerate(result['optimal_order'], 1):
                data = result['measures'][measure]
                st.write(f"**{i}. {measure.upper()}**")
                col1, col2, col3 = st.columns(3)
                col1.metric("Investition", f"{format_german_number(data['investment_eur'], 0)} €")
                col2.metric("Einsparung/Jahr", f"{format_german_number(data['annual_savings_eur'], 0)} €")
                col3.metric("Amortisation", f"{data['payback_years']:.1f} J")
            
            # Visualisierung
            theme = get_chart_theme()
            fig = go.Figure()
            components = list(result['measures'].keys())
            paybacks = [result['measures'][c]['payback_years'] for c in components]
            
            fig.add_trace(go.Bar(
                x=components,
                y=paybacks,
                text=[f"{p:.1f} J" for p in paybacks],
                textposition='auto',
                marker_color=[theme['colors']['danger'], theme['colors']['primary'], 
                             theme['colors']['success'], theme['colors']['warning']]
            ))
            
            fig.update_layout(
                title="Amortisationszeit nach Komponente",
                xaxis_title="Komponente",
                yaxis_title="Jahre",
                height=400,
                separators=',.'  # Deutsche Trennzeichen
            )
            
            # SHADCN UI THEME ANWENDEN
            apply_chart_theme(fig)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Feature 2: Heizkörper vs. Fußbodenheizung
    with st.expander("Heizkörper vs. Fußbodenheizung Optimizer"):
        st.markdown("### Welches System ist optimal?")
        
        current_system = st.selectbox(
            "Aktuelles System",
            options=["radiators", "underfloor"],
            format_func=lambda x: "Heizkörper" if x == "radiators" else "Fußbodenheizung",
            index=0
        )
        
        if st.button("Systeme vergleichen", key="compare_heating"):
            result = compare_heating_systems(building_data, current_system)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("####  Niedertemperatur-Radiatoren")
                rad = result['systems']['radiators_new']
                st.metric("Vorlauftemperatur", f"{rad['flow_temperature_c']}°C")
                st.metric("COP", f"{format_german_number(rad['cop'], 2)}")
                st.metric("Installationskosten", f"{format_german_number(rad['installation_cost_eur'], 0)} €")
                st.metric("Jahreskosten Strom", f"{format_german_number(rad['annual_cost_eur'], 0)} €")
            
            with col2:
                st.markdown("####  Fußbodenheizung")
                uf = result['systems']['underfloor']
                st.metric("Vorlauftemperatur", f"{uf['flow_temperature_c']}°C")
                st.metric("COP", f"{format_german_number(uf['cop'], 2)}")
                st.metric("Installationskosten", f"{format_german_number(uf['installation_cost_eur'], 0)} €")
                st.metric("Jahreskosten Strom", f"{format_german_number(uf['annual_cost_eur'], 0)} €")
            
            comp = result['comparison']
            st.markdown("### Empfehlung")
            st.success(f"**{comp['recommendation']}**")
            st.info(f"Jährliche Einsparung: {format_german_number(comp['annual_savings_eur'], 2)} €/Jahr")
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
                st.metric("Wärmeverlust-Reduktion", f"{format_german_number(result['heat_loss_reduction_kwh'], 0)} kWh")
            
            with col2:
                st.metric("Investition (brutto)", f"{format_german_number(result['investment_eur'], 0)} €")
                st.metric("Förderung (15%)", f"{format_german_number(result['subsidy_eur'], 0)} €")
                st.metric("Netto-Investition", f"{format_german_number(result['net_investment_eur'], 0)} €")
            
            st.success(f"**Gewinn nach 20 Jahren:** {format_german_number(result['savings_20_years_eur'], 2)} €")
            st.info(f"⏱ **Amortisation:** {result['payback_years']:.1f} Jahre")
    
    # Feature 4: Gesamt-Renovierungs-Planer
    with st.expander(" Gesamt-Renovierungs-Planer"):
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
            
            st.markdown("### Sanierungsfahrplan")
            for step in result['roadmap']:
                with st.container():
                    st.markdown(f"### Schritt {step['step']}: {step['measure'].replace('_', ' ').title()}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Investition", f"{format_german_number(step['investment_eur'], 0)} €")
                    col2.metric("Einsparung/Jahr", f"{format_german_number(step['annual_savings_eur'], 0)} €")
                    col3.metric("Amortisation", f"{step['payback_years']:.1f} J")
                    st.progress(step['cumulative_investment'] / budget_total)
                    st.write(f"Kumulative Investition: {format_german_number(step['cumulative_investment'], 0)} € von {format_german_number(budget_total, 0)} €")
            
            summary = result['summary']
            st.markdown("### Zusammenfassung")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Maßnahmen", summary['total_measures'])
            col2.metric("Investition", f"{format_german_number(summary['net_investment_eur'], 0)} €")
            col3.metric("Förderung", f"{format_german_number(summary['total_subsidy_eur'], 0)} €")
            col4.metric("Einsparung/Jahr", f"{format_german_number(summary['total_annual_savings_eur'], 0)} €")
            
            st.success(f"**Gewinn nach 20 Jahren:** {format_german_number(summary['savings_20_years_eur'], 2)} €")
            st.info(f"⏱ **Gesamt-Amortisation:** {summary['overall_payback_years']:.1f} Jahre")


def render_optimization_tools(texts: dict[str, str], building_data: dict[str, Any]):
    """Optimierungs-Tools Tab (Features 5-8)"""
    
    st.subheader(" Optimierungs-Tools")
    st.markdown("Intelligente Analyse und Optimierung")
    
    # Feature 5: Verbrauchsoptimierer Turbo
    with st.expander("Verbrauchsoptimierer Turbo", expanded=True):
        st.markdown("### Heizplan-Optimierung mit Stromtarifen")
        
        st.markdown("**Anwesenheitsprofil (Wochentag):**")
        st.info("1 = Anwesend, 0 = Abwesend")
        
        # CSS: Blauen Hintergrund bei Multiselect entfernen
        st.markdown("""
        <style>
        div[data-baseweb="select"] > div {
            background-color: transparent !important;
        }
        div[data-baseweb="popover"] {
            background-color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
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
            
            st.markdown("### Einsparung durch Optimierung")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Baseline (konstant)", f"{format_german_number(result['baseline']['annual_cost_eur'], 0)} €/Jahr")
            with col2:
                st.metric("Optimiert (Vorheizen)", f"{format_german_number(result['optimized']['annual_cost_eur'], 0)} €/Jahr")
            
            st.success(f" **Jährliche Einsparung:** {format_german_number(result['savings']['annual_eur'], 2)} € ({result['savings']['percent']:.1f}%)")
            
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
                height=400,
                separators=',.'  # Deutsche Trennzeichen
            )
            
            # SHADCN UI THEME ANWENDEN
            apply_chart_theme(fig)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Feature 6: Klimawandel-Szenarien
    with st.expander(" Klimawandel-Szenarien 2025-2050"):
        st.markdown("### Langzeit-Prognose mit Temperaturanstieg")
        
        if st.button("Szenarien berechnen", key="climate_scenarios"):
            result = simulate_climate_scenarios(building_data)
            
            st.markdown("### Vergleich der Szenarien")
            
            # Tabelle
            summary_data = []
            for scenario_key, scenario_data in result['scenarios'].items():
                summary = scenario_data['summary_2050']
                summary_data.append({
                    "Szenario": scenario_data['name'],
                    "Temperaturanstieg": f"+{summary['temp_increase_c']:.1f}°C",
                    "Heizlast-Reduktion": f"-{summary['heating_reduction_percent']:.1f}%",
                    "COP 2050": f"{format_german_number(summary['final_cop'], 2)}",
                    "Strompreis 2050": f"{summary['electricity_price_2050']:.3f} €/kWh",
                    "Kosten 2024-2050": f"{format_german_number(summary['cumulative_cost_2024_2050_eur'], 0)} €"
                })
            
            st.dataframe(pd.DataFrame(summary_data))
            
            st.success(f" **Differenz Best/Worst Case:** {format_german_number(result['comparison']['difference_eur'], 0)} €")
            
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
                height=500,
                separators=',.'  # Deutsche Trennzeichen
            )
            
            # SHADCN UI THEME ANWENDEN
            apply_chart_theme(fig)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Feature 7: Wärmepumpen-Auswahl-Matrix
    with st.expander("Wärmepumpen-Auswahl-Matrix"):
        st.markdown("### Vergleichen Sie alle WP-Typen")
        
        col1, col2 = st.columns(2)
        plot_size = col1.number_input("Grundstücksgröße (m²)", min_value=100, max_value=5000, value=500)
        groundwater = col2.checkbox("Grundwasser verfügbar?", value=False)
        
        if st.button("WP-Typen vergleichen", key="compare_heatpumps"):
            result = compare_heatpump_types(building_data, plot_size, groundwater)
            
            st.markdown("### Ranking nach Lebenszykluskosten")
            for rank_data in result['ranking']:
                st.write(f"**{rank_data['rank']}. {rank_data['name']}**")
            
            st.success(f"**Empfehlung:** {result['comparison'][result['recommendation']]['name']}")
            
            # Vergleichs-Tabelle
            comparison_data = []
            for wp_type, data in result['comparison'].items():
                comparison_data.append({
                    "Typ": data['name'],
                    "COP": f"{format_german_number(data['cop'], 2)}",
                    "Investition": f"{format_german_number(data['net_installation_eur'], 0)} €",
                    "Stromkosten/Jahr": f"{format_german_number(data['annual_electricity_cost_eur'], 0)} €",
                    "Wartung/Jahr": f"{data['annual_maintenance_eur']} €",
                    "Lebenszykluskosten": f"{format_german_number(data['lifetime_cost_eur'], 0)} €",
                    "Lautstärke": f"{data['noise_db']} dB",
                    "Lebensdauer": f"{data['lifespan_years']} Jahre"
                })
            
            st.dataframe(pd.DataFrame(comparison_data))
    
    # Feature 8: 8760h-Lastgang-Analyse
    with st.expander("8760h-Lastgang-Analyse"):
        st.markdown("### Stündliche Simulation über ganzes Jahr")
        
        if st.button("Jahres-Simulation starten", key="simulate_annual"):
            with st.spinner("Simuliere 8760 Stunden..."):
                result = simulate_annual_load_profile(building_data)
            
            st.markdown("### Jahres-Zusammenfassung")
            col1, col2, col3, col4 = st.columns(4)
            summary = result['annual_summary']
            col1.metric("Wärmebedarf", f"{format_german_number(summary['total_heat_kwh'], 0)} kWh")
            col2.metric("Stromverbrauch", f"{format_german_number(summary['total_electricity_kwh'], 0)} kWh")
            col3.metric("Ø COP", f"{format_german_number(summary['annual_average_cop'], 2)}")
            col4.metric("Betriebsstunden", f"{format_german_number(summary['operating_hours'], 0)} h")
            
            st.success(f"**Jahreskosten:** {format_german_number(summary['annual_cost_eur'], 2)} €")
            
            # Monats-Übersicht
            st.markdown("###  Monats-Übersicht")
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
                height=500,
                separators=',.'  # Deutsche Trennzeichen
            )
            
            # SHADCN UI THEME ANWENDEN
            apply_chart_theme(fig)
            
            st.plotly_chart(fig, use_container_width=True)


def render_subsidy_co2(texts: dict[str, str], building_data: dict[str, Any]):
    """Förderung & CO2 Tab (Features 9-10)"""
    
    st.subheader(" Förderung & CO2-Dashboard")
    
    # Feature 9: Fördermittel-Optimizer
    with st.expander(" Fördermittel-Optimizer", expanded=True):
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
            
            st.markdown("### Finanzierung")
            col1, col2, col3 = st.columns(3)
            col1.metric("Gesamt-Investition", f"{format_german_number(result['total_investment_eur'], 0)} €")
            col2.metric("Förderung", f"{format_german_number(result['total_subsidy_eur'], 0)} € ({result['subsidy_rate']:.1f}%)")
            col3.metric("Netto-Investition", f"{format_german_number(result['net_investment_eur'], 0)} €")
            
            st.markdown("###  Förderungen im Detail")
            for subsidy in result['subsidies']:
                with st.container():
                    st.markdown(f"#### {subsidy['program']}")
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"**Typ:** {subsidy['type']}")
                    col2.write(f"**Betrag:** {format_german_number(subsidy['amount_eur'], 2)} €")
                    if subsidy['rate'] > 0:
                        col3.write(f"**Rate:** {subsidy['rate']:.1f}%")
            
            if result['loan_option']:
                st.markdown("###  KfW-Kredit-Option")
                loan = result['loan_option']
                col1, col2, col3 = st.columns(3)
                col1.metric("Kreditbetrag", f"{format_german_number(loan['loan_amount_eur'], 0)} €")
                col2.metric("Tilgungszuschuss", f"{format_german_number(loan['tilgung_grant_eur'], 0)} €")
                col3.metric("Monatliche Rate", f"{format_german_number(loan['monthly_rate_eur'], 2)} €")
                st.info(f"Laufzeit: {loan['duration_years']} Jahre, Zinssatz: {loan['interest_rate']*100:.1f}%")
            
            st.markdown("### Antrags-Checkliste")
            for item in result['application_checklist']:
                st.checkbox(item, key=f"checklist_{item}")
    
    # Feature 10: CO2-Dashboard Live
    with st.expander("CO2-Dashboard Live"):
        st.markdown("### Langfristige CO2-Bilanz (20 Jahre)")
        
        col1, col2 = st.columns(2)
        current_sys = col1.selectbox("Aktuelles System", ["gas", "oil", "district_heating"], format_func=lambda x: {"gas": "Erdgas", "oil": "Heizöl", "district_heating": "Fernwärme"}[x])
        future_sys = col2.selectbox("Zukünftiges System", ["heatpump", "heatpump_pv"], format_func=lambda x: {"heatpump": "Wärmepumpe (Grid)", "heatpump_pv": "Wärmepumpe + PV"}[x])
        
        if st.button("CO2-Bilanz berechnen", key="calc_co2"):
            result = calculate_co2_footprint(building_data, current_sys, future_sys)
            
            st.markdown("###  20-Jahres-Zusammenfassung")
            col1, col2, col3, col4 = st.columns(4)
            summary = result['summary_20_years']
            col1.metric("CO2-Einsparung", f"{summary['total_co2_savings_t']:.1f} Tonnen")
            col2.metric("Kostenersparnis", f"{format_german_number(summary['total_co2_cost_savings_eur'], 0)} €")
            col3.metric("≈ Bäume gepflanzt", f"{format_german_number(summary['equivalent_trees_planted'], 0)}")
            col4.metric("≈ PKW-km eingespart", f"{format_german_number(summary['equivalent_car_km'], 0)}")
            
            st.success(f" **Pro Jahr:** {format_german_number(summary['avg_annual_savings_t'], 2)} Tonnen CO2")
            
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
                height=500,
                separators=',.'  # Deutsche Trennzeichen
            )
            
            # SHADCN UI THEME ANWENDEN
            apply_chart_theme(fig)
            
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
                height=400,
                separators=',.'  # Deutsche Trennzeichen
            )
            
            # SHADCN UI THEME ANWENDEN
            apply_chart_theme(fig2)
            
            st.plotly_chart(fig2, use_container_width=True)


def render_roi_benchmarking(texts: dict[str, str], building_data: dict[str, Any]):
    """ROI & Benchmarking Tab (Features 11-12)"""
    
    st.subheader("ROI-Analyse & Benchmarking")
    
    # Feature 11: Monte-Carlo ROI-Calculator
    with st.expander(" ROI-Calculator Monte-Carlo", expanded=True):
        st.markdown("### Probabilistische Wirtschaftlichkeits-Analyse")
        st.info("Simuliert 10.000 Szenarien mit unterschiedlichen Parametern")
        
        investment = st.number_input("Investitionssumme (€)", min_value=5000, max_value=100000, value=20000, step=1000)
        simulations = st.slider("Anzahl Simulationen", min_value=1000, max_value=10000, value=10000, step=1000)
        
        if st.button("Monte-Carlo-Simulation starten", key="monte_carlo"):
            with st.spinner(f"Führe {simulations:,} Simulationen durch..."):
                result = monte_carlo_roi_analysis(building_data, investment, simulations)
            
            st.markdown("### Amortisations-Statistik")
            col1, col2, col3, col4 = st.columns(4)
            payback = result['payback_statistics']
            col1.metric("Ø Amortisation", f"{payback['mean_years']:.1f} Jahre")
            col2.metric("Median", f"{payback['median_years']:.1f} Jahre")
            col3.metric("Best Case (10%)", f"{payback['p10_years']:.1f} Jahre")
            col4.metric("Worst Case (90%)", f"{payback['p90_years']:.1f} Jahre")
            
            st.success(f"**Wahrscheinlichkeit für Amortisation <15 Jahre:** {payback['probability_under_15_years']:.1f}%")
            
            st.markdown("### Nettobarwert (NPV)")
            col1, col2, col3 = st.columns(3)
            npv = result['npv_statistics']
            col1.metric("Ø NPV", f"{format_german_number(npv['mean_eur'], 0)} €")
            col2.metric("Median NPV", f"{format_german_number(npv['median_eur'], 0)} €")
            col3.metric("Wahrscheinlichkeit NPV>0", f"{npv['probability_positive']:.1f}%")
            
            st.markdown("### ROI-Statistik")
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
                height=400,
                separators=',.'  # Deutsche Trennzeichen
            )
            
            # SHADCN UI THEME ANWENDEN
            apply_chart_theme(fig)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Feature 12: Benchmarking-Tool
    with st.expander("Benchmarking-Tool"):
        st.markdown("### Vergleich mit ähnlichen Gebäuden")
        
        region = st.selectbox("Region", ["Germany", "Bayern", "NRW", "Baden-Württemberg"], index=0)
        
        if st.button("Benchmarking durchführen", key="benchmark"):
            result = benchmark_building(building_data, region)
            
            own = result['own_building']
            ranking = result['ranking']
            comparison = result['comparison']
            
            st.markdown("### Ihr Gebäude")
            col1, col2, col3 = st.columns(3)
            col1.metric("Verbrauch", f"{own['specific_consumption_kwh_m2']:.1f} kWh/m²/Jahr")
            col2.metric("Wohnfläche", f"{format_german_number(own['living_area_m2'], 0)} m²")
            col3.metric("Baujahr", own['year_built'])
            
            st.markdown("### Ranking")
            rank_color = "green" if ranking['percentile'] <= 25 else "orange" if ranking['percentile'] <= 50 else "red"
            st.markdown(f"**Platz {ranking['rank']} von {ranking['total_buildings']}** ({ranking['percentile']:.1f}. Perzentil)")
            st.markdown(f"**Bewertung:** :{rank_color}[{ranking['interpretation']}]")
            
            st.markdown("### [DOWN] Vergleich")
            col1, col2, col3 = st.columns(3)
            col1.metric("Durchschnitt", f"{comparison['avg_consumption_kwh_m2']:.1f} kWh/m²", 
                        delta=f"{comparison['difference_to_avg_kwh_m2']:.1f}", delta_color="inverse")
            col2.metric("Bestes Gebäude", f"{comparison['best_consumption_kwh_m2']:.1f} kWh/m²",
                        delta=f"{comparison['difference_to_best_kwh_m2']:.1f}", delta_color="inverse")
            col3.metric("Schlechtestes", f"{comparison['worst_consumption_kwh_m2']:.1f} kWh/m²")
            
            st.success(f"**Einsparpotenzial:** {format_german_number(result['potential_annual_savings_eur'], 2)} €/Jahr")
            
            # Best Performer
            best = result['best_performer']
            st.markdown("###  Best Performer")
            st.info(f"**System:** {best['system'].upper()}, **Gedämmt:** {'Ja' if best['insulated'] else 'Nein'}, **Baujahr:** {best['year']}, **Verbrauch:** {best['consumption_kwh_m2']} kWh/m²")
            
            # Empfehlungen
            if result['recommendations']:
                st.markdown("### Empfehlungen")
                for rec in result['recommendations']:
                    priority_color = "red" if rec['priority'] == "high" else "orange"
                    st.markdown(f":{priority_color}[**{rec['priority'].upper()}**] {rec['measure']}")
                    col1, col2 = st.columns(2)
                    col1.write(f"Einsparung: {format_german_number(rec['potential_savings_kwh_m2'], 0)} kWh/m²/Jahr")
                    col2.write(f"Investition: {format_german_number(rec['investment_eur'], 0)} €")


# Haupt-Export-Funktion


def show_heatpump_analysis(
        texts: dict[str, str], project_data: dict[str, Any] = None):
    """Öffentliche Funktion zum Anzeigen der Wärmepumpen-Analyse"""
    render_heatpump_analysis(texts, project_data)

# Wrapper für GUI-Integration

@trace_heatpump
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


# ============================================================================
# DYNAMISCHER STROMTARIF TAB (NEU - Feature 13)
# ============================================================================

def render_dynamic_tariff_tab(texts: dict[str, str], building_data: dict[str, Any]) -> None:
    """
    Dynamischer Stromtarif & Stromcloud Analyse
    
    Todos 8-14: Komplette UI mit 6 Expandern
    """
    
    st.subheader("Dynamischer Stromtarif & Stromcloud")
    st.markdown("""
    Sparen Sie **15-25%** Stromkosten durch dynamische Tarife mit stundengenauer Abrechnung.
    Optimal für Wärmepumpen, E-Autos und Smart-Home-Systeme.
    """)
    
    # ========================================================================
    # EXPANDER 1: Dynamischer vs Statischer Tarif (Todo 9)
    # ========================================================================
    
    with st.expander("Dynamischer vs Statischer Tarif", expanded=True):
        st.markdown("""
        Vergleichen Sie statischen Festpreis-Tarif mit dynamischem Börsenpreis-Tarif.
        **Dynamische Tarife** passen sich stündlich an Stromangebot an.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            annual_consumption = st.number_input(
                "Jahresverbrauch Haushalt (kWh/Jahr)",
                min_value=2000,
                max_value=15000,
                value=4500,
                step=500,
                help="Normaler Haushaltsstrom ohne WP"
            )
            
            static_price = st.number_input(
                "Aktueller Strompreis (EUR/kWh)",
                min_value=0.20,
                max_value=0.50,
                value=0.32,
                step=0.01,
                format="%.3f"
            )
        
        with col2:
            wp_power_kw = building_data.get("heat_load_kw", 10)
            wp_annual_hours = st.number_input(
                "WP Betriebsstunden/Jahr",
                min_value=1000,
                max_value=2500,
                value=1800,
                step=100
            )
            
            cop = building_data.get("cop", 3.5)
            st.metric("JAZ (Jahresarbeitszahl)", f"{cop:.1f}")
            
            # WP-Anteil am Gesamtverbrauch berechnen
            heat_load_kw = building_data.get("heat_load_kw", 10)
            annual_heat_kwh = heat_load_kw * wp_annual_hours
            wp_electricity_kwh = annual_heat_kwh / cop if cop > 0 else 0
            total_consumption_kwh = annual_consumption + wp_electricity_kwh
            heatpump_share = (wp_electricity_kwh / total_consumption_kwh * 100) if total_consumption_kwh > 0 else 30
        
        if st.button("Tarife vergleichen", type="primary"):
            with st.spinner("Berechne Einsparpotenzial..."):
                # Berechnung mit korrekten Parametern
                comparison = calculate_dynamic_tariff_comparison(
                    building_data,
                    current_price_eur_kwh=static_price,
                    heatpump_share_percent=heatpump_share,
                    smart_meter_cost_eur=100
                )
                
                # Ergebnisse
                st.markdown("---")
                st.markdown("### Ergebnisse")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Statischer Tarif (Gesamt)",
                        f"{format_german_number(comparison['static_tariff']['annual_cost_total_eur'], 0)} €/Jahr",
                        help="Festpreis für kompletten Verbrauch"
                    )
                    st.caption(f"WP: {format_german_number(comparison['static_tariff']['annual_cost_wp_eur'], 0)} €")
                    st.caption(f"Haushalt: {format_german_number(comparison['static_tariff']['annual_cost_household_eur'], 0)} €")
                
                with col2:
                    st.metric(
                        "Dynamischer Tarif (Gesamt)",
                        f"{format_german_number(comparison['dynamic_tariff']['annual_cost_total_eur'], 0)} €/Jahr",
                        delta=f"-{format_german_number(comparison['savings']['annual_eur'], 0)} €",
                        delta_color="normal",
                        help="Börsenpreis mit intelligentem Load-Shifting"
                    )
                    st.caption(f"WP: {format_german_number(comparison['dynamic_tariff']['annual_cost_energy_eur'] * 0.25, 0)} €")
                    st.caption(f"Haushalt: {format_german_number(comparison['dynamic_tariff']['annual_cost_energy_eur'] * 0.75, 0)} €")
                
                with col3:
                    st.metric(
                        "Einsparung",
                        f"{comparison['savings']['annual_percent']:.1f}%",
                        help=f"{format_german_number(comparison['savings']['annual_eur'], 0)} € pro Jahr"
                    )
                    st.caption(f"Monatlich: {format_german_number(comparison['savings']['monthly_eur'], 0)} €")
                
                # Smart Meter ROI
                st.markdown("---")
                st.markdown("###  Smart Meter Investment")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Einmalkosten", f"{format_german_number(comparison['investment']['smart_meter_cost_eur'], 0)} €")
                
                with col2:
                    st.metric("Amortisation", f"{comparison['investment']['payback_years']:.1f} Jahre")
                
                with col3:
                    st.metric("10-Jahres-Bilanz", f"{format_german_number(comparison['savings']['10_years_eur'], 0)} €")
                
                
                # VISUALISIERUNG 1: Stündliche Preiskurve (Todo 15)
                st.markdown("---")
                st.markdown("### Visualisierung: 24h-Preisverlauf")
                
                # Generiere stündliche Daten für Chart
                from heatpump_dynamic_tariff import calculate_hourly_electricity_costs
                hourly_result = calculate_hourly_electricity_costs(
                    annual_consumption_kwh=comparison['consumption']['total_kwh'],  # Jahresverbrauch
                    base_price_eur_kwh=comparison['static_tariff']['price_eur_kwh']
                )
                
                # Extrahiere hourly_data Liste aus dem Ergebnis-Dictionary
                hourly_chart = create_hourly_price_chart(hourly_result['hourly_data'])
                
                # SHADCN UI THEME ANWENDEN
                apply_chart_theme(hourly_chart)
                
                st.plotly_chart(hourly_chart, use_container_width=True)
    
    
    # ========================================================================
    # EXPANDER 2: Stromcloud-Analyse (Todo 10)
    # ========================================================================
    
    with st.expander(" Stromcloud-Analyse"):
        st.markdown("""
        **Stromcloud** = Virtueller Stromspeicher beim Anbieter statt physischer Batterie.
        Überschuss-Strom wird "eingelagert" und später kostenfrei entnommen.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            pv_size_kwp = st.number_input(
                "PV-Anlagengröße (kWp)",
                min_value=3.0,
                max_value=30.0,
                value=10.0,
                step=1.0
            )
            
            annual_pv_kwh = pv_size_kwp * 1000  # Vereinfacht: 1000 kWh/kWp
            
            feed_in_tariff = st.number_input(
                "Einspeisevergütung (EUR/kWh)",
                min_value=0.05,
                max_value=0.15,
                value=0.08,
                step=0.01,
                format="%.3f"
            )
        
        with col2:
            if cop != 0:
                total_consumption = annual_consumption + (wp_power_kw * wp_annual_hours / cop)
            else:
                total_consumption = 0.0
            
            st.metric("Jahresverbrauch Gesamt", f"{format_german_number(total_consumption, 0)} kWh")
            st.metric("PV-Ertrag (geschätzt)", f"{format_german_number(annual_pv_kwh, 0)} kWh")
            
            cloud_provider = st.selectbox(
                "Stromcloud-Anbieter",
                options=["E.ON SolarCloud", "SENEC.Cloud", "sonnenFlat"]
            )
        
        if st.button(" Stromcloud berechnen", type="primary"):
            with st.spinner("Berechne Cloud-Ökonomie..."):
                pv_data = {
                    "annual_production_kwh": annual_pv_kwh,
                    "direct_consumption_kwh": annual_pv_kwh * 0.30  # 30% Eigenverbrauch ohne Cloud
                }
                
                cloud_result = calculate_stromcloud_economics(
                    building_data,
                    pv_data,
                    feed_in_tariff
                )
                
                st.markdown("---")
                st.markdown("### Stromcloud Vergleich")
                
                # Vor Cloud
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Ohne Stromcloud")
                    st.metric("Netzstrom-Bezug", f"{format_german_number(cloud_result['without_cloud']['grid_consumption_kwh'], 0)} kWh")
                    st.metric("Stromkosten", f"{format_german_number(cloud_result['without_cloud']['grid_cost_eur'], 0)} €/Jahr")
                    st.metric("Einspeisung", f"{format_german_number(cloud_result['without_cloud']['feed_in_kwh'], 0)} kWh")
                    st.metric("Einnahmen", f"{format_german_number(cloud_result['without_cloud']['feed_in_revenue_eur'], 0)} €/Jahr")
                    st.metric("**Netto-Kosten**", f"**{format_german_number(cloud_result['without_cloud']['net_cost_eur'], 0)} €/Jahr**")
                
                with col2:
                    st.markdown("#### Mit Stromcloud")
                    cloud_grid_kwh = cloud_result['with_cloud'].get('overage_kwh', 0)
                    st.metric("Cloud-Bezug", f"{format_german_number(cloud_result['with_cloud']['cloud_consumption_kwh'], 0)} kWh")
                    st.metric("Cloud-Kosten", f"{format_german_number(cloud_result['with_cloud']['total_cloud_cost_eur'], 0)} €/Jahr")
                    st.metric("Überschuss", f"{format_german_number(cloud_result['with_cloud']['overage_kwh'], 0)} kWh")
                    st.metric("Autarkie", f"{cloud_result['pv_system']['autarkie_with_cloud_percent']:.1f}%")
                    st.metric("**Netto-Kosten**", f"**{format_german_number(cloud_result['with_cloud']['net_cost_eur'], 0)} €/Jahr**")
                
                # Verbesserung
                st.markdown("---")
                comparison = cloud_result['comparison']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Einsparung/Jahr",
                        f"{format_german_number(comparison['annual_savings_eur'], 0)} €",
                        delta=f"{comparison['savings_percent']:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Autarkie-Steigerung",
                        f"{comparison['autarkie_improvement_percent']:.1f} %",
                        delta="mehr Eigenverbrauch"
                    )
                
                with col3:
                    st.metric(
                        "10-Jahres-Ersparnis",
                        f"{format_german_number(comparison['annual_savings_eur'] * 10, 0)} €"
                    )
                
                # Anbieter-Pläne
                st.markdown("---")
                st.markdown("###  Verfügbare Cloud-Pläne")
                
                # Erstelle Tabelle aus verfügbaren Plänen
                plans_data = []
                for provider, plans in cloud_result['available_plans'].items():
                    for plan_size, plan_details in plans.items():
                        plans_data.append({
                            "Anbieter": provider,
                            "Tarif": f"{plan_size} kWh",
                            "Freimenge (kWh/Jahr)": plan_details['free_kwh'],
                            "Grundgebühr (€/Monat)": plan_details['base_fee_monthly']
                        })
                
                plans_df = pd.DataFrame(plans_data)
                st.dataframe(plans_df, use_container_width=True, hide_index=True)
                
                # VISUALISIERUNG 3: Stromcloud Waterfall (Todo 17)
                st.markdown("---")
                st.markdown("### Visualisierung: Kosten-Wasserfall")
                
                waterfall_chart = create_stromcloud_waterfall(cloud_result)
                
                # SHADCN UI THEME ANWENDEN
                apply_chart_theme(waterfall_chart)
                
                st.plotly_chart(waterfall_chart, use_container_width=True)
    
    
    # ========================================================================
    # EXPANDER 3: Energiemanagement-System (Todo 11)
    # ========================================================================
    
    with st.expander(" Energiemanagement-System (EMS)"):
        st.markdown("""
        **EMS** koordiniert Wärmepumpe, Batterie und PV intelligent für maximale Autarkie.
        Nutzt Wetterprognosen und dynamische Tarife für optimales Load-Shifting.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            ems_type = st.selectbox(
                "EMS-System",
                options=["SolarEdge", "SMA", "Fronius", "SENEC"],
                help="Jedes System hat unterschiedliche Funktionen und Preise"
            )
            
            battery_size = st.slider(
                "Batteriegröße (kWh)",
                min_value=5,
                max_value=30,
                value=10,
                step=5
            )
        
        with col2:
            st.info(f"""
            **{ems_type}**
            - AI-Optimierung
            - Wetterprognose
            - Smart-Grid Ready
            """)
        
        if st.button(" EMS simulieren", type="primary"):
            with st.spinner(f"Simuliere {ems_type} EMS..."):
                pv_data = {
                    "annual_production_kwh": pv_size_kwp * 1000,
                    "direct_consumption_kwh": pv_size_kwp * 300
                }
                
                ems_result = simulate_energy_management_system(
                    building_data,
                    pv_data,
                    battery_size,
                    ems_type
                )
                
                st.markdown("---")
                st.markdown(f"### {ems_type} Simulation")
                
                # System-Info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("System", ems_result['ems_system']['type'])
                    st.caption(f"Wirkungsgrad: {format_german_number(ems_result['ems_system']['efficiency']*100, 0)}%")
                
                with col2:
                    st.metric("Batterie", f"{format_german_number(ems_result['ems_system']['battery_size_kwh'], 0)} kWh")
                
                with col3:
                    st.metric("System-Preis", f"{format_german_number(ems_result['ems_system']['price_eur'], 0)} €")
                
                # Vorher/Nachher
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Ohne EMS")
                    st.metric("PV-Eigenverbrauch", f"{format_german_number(ems_result['without_ems']['pv_usage_kwh'], 0)} kWh")
                    st.metric("Autarkie", f"{ems_result['without_ems']['autarkie_percent']:.1f}%")
                    st.metric("Stromkosten", f"{format_german_number(ems_result['without_ems']['annual_cost_eur'], 0)} €/Jahr")
                
                with col2:
                    st.markdown("#### Mit EMS")
                    st.metric("PV-Eigenverbrauch", f"{format_german_number(ems_result['with_ems']['pv_usage_kwh'], 0)} kWh")
                    st.metric("Autarkie", f"{ems_result['with_ems']['autarkie_percent']:.1f}%")
                    st.metric("Stromkosten", f"{format_german_number(ems_result['with_ems']['annual_cost_eur'], 0)} €/Jahr")
                    st.caption(f"Load-Shifting: {format_german_number(ems_result['with_ems']['load_shifted_kwh'], 0)} kWh")
                
                # Verbesserung
                st.markdown("---")
                imp = ems_result['improvement']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Zusätzlicher PV-Nutzen",
                        f"{format_german_number(imp['additional_pv_usage_kwh'], 0)} kWh/Jahr"
                    )
                
                with col2:
                    st.metric(
                        "Autarkie-Steigerung",
                        f"+{imp['autarkie_increase_percent']:.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "Einsparung",
                        f"{format_german_number(imp['annual_savings_eur'], 0)} €/Jahr"
                    )
                
                # Investment
                st.markdown("---")
                st.markdown("### Investment & ROI")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("EMS-Kosten", f"{format_german_number(ems_result['investment']['ems_cost_eur'], 0)} €")
                
                with col2:
                    st.metric("Batterie-Kosten", f"{format_german_number(ems_result['investment']['battery_cost_eur'], 0)} €")
                
                with col3:
                    st.metric("Gesamt-Investment", f"{format_german_number(ems_result['investment']['total_investment_eur'], 0)} €")
                
                with col4:
                    st.metric("Amortisation", f"{ems_result['investment']['payback_years']:.1f} Jahre")
                
                if ems_result['investment']['worth_it']:
                    st.success("Investment lohnt sich - Amortisation unter 10 Jahren!")
                else:
                    st.warning("Amortisation über 10 Jahre - gut abwägen!")
    
    
    # ========================================================================
    # EXPANDER 4: Smart-Home-Vorteile (Todo 12)
    # ========================================================================
    
    with st.expander(" Smart-Home-Integration"):
        st.markdown("""
        Vernetzen Sie alle Großverbraucher für automatisches Last-Management.
        **Ziel:** Geräte laufen automatisch wenn Strom günstig ist.
        """)
        
        st.markdown("### Steuerbare Geräte")
        
        col1, col2, col3 = st.columns(3)
        
        devices = {}
        
        with col1:
            devices['heatpump'] = st.checkbox("Wärmepumpe", value=True, key="dynamic_tariff_heatpump_checkbox")
            devices['battery'] = st.checkbox(" Batteriespeicher", value=False, key="dynamic_tariff_battery_checkbox")
            devices['wallbox'] = st.checkbox(" E-Auto Wallbox", value=False, key="dynamic_tariff_wallbox_checkbox")
        
        with col2:
            devices['washing_machine'] = st.checkbox(" Waschmaschine", value=False, key="dynamic_tariff_washing_checkbox")
            devices['dishwasher'] = st.checkbox(" Geschirrspüler", value=False, key="dynamic_tariff_dishwasher_checkbox")
            devices['dryer'] = st.checkbox(" Wäschetrockner", value=False, key="dynamic_tariff_dryer_checkbox")
        
        with col3:
            automation_level = st.select_slider(
                "Automatisierungs-Level",
                options=["low", "medium", "high"],
                value="medium",
                help="low=Manuell | medium=Zeit-basiert | high=KI-gesteuert",
                key="dynamic_tariff_automation_slider"
            )
        
        if st.button(" Smart-Home analysieren", type="primary"):
            with st.spinner("Berechne Smart-Home-Potenzial..."):
                sh_result = calculate_smart_home_benefits(
                    building_data,
                    devices,
                    automation_level
                )
                
                st.markdown("---")
                st.markdown(f"###  {sh_result['automation']['description']}")
                
                # Automatisierungs-Info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Automatisierungs-Level", sh_result['automation']['level'].upper())
                
                with col2:
                    st.metric("Effizienz", f"{format_german_number(sh_result['automation']['efficiency_percent'], 0)}%")
                
                with col3:
                    st.metric("Komplexität", sh_result['automation']['setup_complexity'])
                
                # Geräte-Details
                st.markdown("---")
                st.markdown("###  Geräte-Übersicht")
                
                if sh_result['devices']:
                    devices_data = []
                    for device_name, device_info in sh_result['devices'].items():
                        devices_data.append({
                            "Gerät": device_name.replace("_", " ").title(),
                            "Last verschiebbar": f"{device_info['shiftable_percent']}%",
                            "Einsparung/Jahr": f"{format_german_number(device_info['annual_savings_eur'], 0)} €",
                            "Setup-Kosten": f"{format_german_number(device_info['setup_cost_eur'], 0)} €",
                            "Amortisation": f"{device_info['payback_years']:.1f} Jahre",
                            "Komfort": f"{device_info['comfort_impact']*10:.1f}/10"
                        })
                    
                    devices_df = pd.DataFrame(devices_data)
                    st.dataframe(devices_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Keine Geräte ausgewählt")
                
                # Zusammenfassung
                st.markdown("---")
                st.markdown("### Gesamt-Bilanz")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Aktive Geräte", sh_result['summary']['active_devices'])
                
                with col2:
                    st.metric("Einsparung/Jahr", f"{format_german_number(sh_result['summary']['total_annual_savings_eur'], 0)} €")
                
                with col3:
                    st.metric("Setup-Kosten", f"{format_german_number(sh_result['summary']['total_setup_cost_eur'], 0)} €")
                
                with col4:
                    st.metric("Amortisation", f"{sh_result['summary']['payback_years']:.1f} Jahre")
                
                # Comfort-Score
                st.markdown("---")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    comfort = sh_result['comfort']['score_0_10']
                    st.metric("Komfort-Score", f"{comfort:.1f}/10")
                
                with col2:
                    st.info(f"""
                    **{sh_result['comfort']['description']}**
                    
                    {sh_result['comfort']['recommendation']}
                    """)
                
                # Vorteile
                st.markdown("---")
                st.markdown("###  Zusätzliche Vorteile")
                for benefit in sh_result['convenience_benefits']:
                    st.success(benefit)
    
    
    # ========================================================================
    # EXPANDER 5: Vor- & Nachteile (Todo 13)
    # ========================================================================
    
    with st.expander(" Vor- & Nachteile Dynamischer Tarife"):
        st.markdown("""
        Ist ein dynamischer Tarif das Richtige für Sie? 
        Hier finden Sie alle Pros & Cons mit Gewichtung.
        """)
        
        building_type_map = {
            "Neubau KfW40": "residential",
            "Neubau KfW55": "residential",
            "Neubau Standard": "residential",
            "Altbau saniert": "residential",
            "Altbau teilsaniert": "residential",
            "Altbau unsaniert": "residential"
        }
        
        building_type_raw = building_data.get("building_type", "Neubau Standard")
        building_type_clean = building_type_map.get(building_type_raw, "residential")
        
        pros_cons = get_dynamic_tariff_pros_cons(building_type_clean)
        
        # Empfehlung
        st.markdown(f"### {pros_cons['scoring']['recommendation']}")
        st.info(pros_cons['scoring']['recommendation_detail'])
        
        # Scores
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Pro-Score", pros_cons['scoring']['pro_score'], help="Summe aller Vorteile-Gewichte")
        
        with col2:
            st.metric("Contra-Score", pros_cons['scoring']['con_score'], help="Summe aller Nachteile-Gewichte")
        
        with col3:
            total = pros_cons['scoring']['total_score']
            st.metric(
                "Gesamt-Score",
                total,
                delta="Positiv" if total > 0 else "Negativ",
                help="Pro-Score minus Contra-Score"
            )
        
        # Pros & Cons nebeneinander
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Vorteile")
            for pro in pros_cons['pros']:
                weight_stars = "" * pro['weight']
                st.success(f"""
                **{pro['title']}**
                
                {pro['description']}
                
                Gewichtung: {weight_stars} ({pro['weight']}/10)
                """)
        
        with col2:
            st.markdown("### Nachteile")
            for con in pros_cons['cons']:
                weight_stars = "" * min(con['weight'], 5)  # Max 5 Warnungen
                st.warning(f"""
                **{con['title']}**
                
                {con['description']}
                
                Gewichtung: {weight_stars} ({con['weight']}/10)
                """)
        
        # Idealer Nutzer
        st.markdown("---")
        st.markdown("### Ideal für:")
        for profile in pros_cons['ideal_user']:
            st.info(profile)
    
    
    # ========================================================================
    # EXPANDER 6: Anbieter-Vergleich (Todo 14)
    # ========================================================================
    
    with st.expander("Anbieter im Vergleich"):
        st.markdown("""
        Alle dynamischen Tarif-Anbieter in Deutschland im direkten Vergleich.
        Finden Sie den besten Tarif für Ihr Profil.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            comp_consumption = st.number_input(
                "Jahresverbrauch Gesamt (kWh)",
                min_value=3000,
                max_value=20000,
                value=8000,
                step=500,
                help="Haushalt + Wärmepumpe"
            )
        
        with col2:
            has_ev_comp = st.checkbox("E-Auto vorhanden", value=False)
            has_wp_comp = st.checkbox("Wärmepumpe vorhanden", value=True)
        
        if st.button("Anbieter vergleichen", type="primary"):
            with st.spinner("Vergleiche alle Anbieter..."):
                provider_result = compare_tariff_providers(
                    comp_consumption,
                    has_ev_comp,
                    has_wp_comp
                )
                
                # Empfehlung
                st.markdown("---")
                st.markdown("###  Unsere Empfehlung")
                
                recommended = provider_result['summary']['recommended_provider']
                reason = provider_result['summary']['recommendation_reason']
                
                st.success(f"""
                ## {recommended}
                
                **Grund:** {reason}
                
                Website: {provider_result['providers'][recommended]['website']}
                """)
                
                # Ranking
                st.markdown("---")
                st.markdown("### Kosten-Ranking")
                
                ranking_data = []
                for rank_entry in provider_result['ranking']:
                    provider_name = rank_entry['provider']
                    provider_info = provider_result['providers'][provider_name]
                    
                    ranking_data.append({
                        "Rang": f"#{rank_entry['rank']}",
                        "Anbieter": provider_name,
                        "Grundgebühr": f"{format_german_number(provider_info['costs']['base_fee_eur_month'], 2)} €/Monat",
                        "Aufschlag": f"{provider_info['costs']['markup_eur_kwh']*100:.1f} ct/kWh",
                        "Jahreskosten": f"{format_german_number(rank_entry['annual_cost_eur'], 0)} €",
                        "Rating": f"{'' * int(provider_info['rating'])} ({provider_info['rating']:.1f})",
                        "Land": provider_info['country']
                    })
                
                ranking_df = pd.DataFrame(ranking_data)
                st.dataframe(ranking_df, use_container_width=True, hide_index=True)
                
                # Max Einsparung
                st.info(f"""
                **Maximale Einsparung:** {format_german_number(provider_result['summary']['max_savings_eur_year'], 0)} € pro Jahr 
                zwischen günstigstem ({provider_result['summary']['cheapest_provider']}) 
                und teuerstem ({provider_result['summary']['most_expensive_provider']}) Anbieter.
                """)
                
                # Detaillierter Vergleich
                st.markdown("---")
                st.markdown("### Detaillierter Vergleich")
                
                for provider_name, provider_info in provider_result['providers'].items():
                    with st.expander(f"{provider_name} - {provider_info['rating']:.1f}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### Kosten")
                            st.metric("Grundgebühr", f"{format_german_number(provider_info['costs']['base_fee_eur_month'], 2)} €/Monat")
                            st.metric("kWh-Aufschlag", f"{provider_info['costs']['markup_eur_kwh']*100:.1f} ct/kWh")
                            st.metric("Effektiv-Preis", f"{provider_info['costs']['effective_price_eur_kwh']:.3f} €/kWh")
                            st.metric("**Jahreskosten**", f"**{format_german_number(provider_info['costs']['total_annual_cost_eur'], 0)} €**")
                        
                        with col2:
                            st.markdown("####  Features")
                            for feature in provider_info['features']:
                                st.success(feature)
                        
                        # Pros & Cons
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Vorteile:**")
                            for pro in provider_info['pros']:
                                st.write(f"{pro}")
                        
                        with col2:
                            st.markdown("**Nachteile:**")
                            for con in provider_info['cons']:
                                st.write(f"{con}")
                        
                        # Boni
                        if has_ev_comp or has_wp_comp:
                            st.markdown("---")
                            st.markdown("** Ihre Rabatte:**")
                            if provider_info['bonuses']['ev_discount_eur_kwh'] != 0:
                                st.write(f"E-Auto: {provider_info['bonuses']['ev_discount_eur_kwh']*100:.1f} ct/kWh")
                            if provider_info['bonuses']['wp_discount_eur_kwh'] != 0:
                                st.write(f"Wärmepumpe: {provider_info['bonuses']['wp_discount_eur_kwh']*100:.1f} ct/kWh")
    
    
    # ========================================================================
    # BONUS-VISUALISIERUNGEN: Jahres-Analyse & Load-Shifting (Todos 16 & 18)
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## Erweiterte Analysen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        simulate_annual = st.checkbox("Jahres-Simulation anzeigen", value=False)
    
    with col2:
        simulate_heatmap = st.checkbox(" Load-Shifting Heatmap anzeigen", value=False)
    
    # VISUALISIERUNG 2: Jährliche Kostenentwicklung (Todo 16)
    if simulate_annual:
        with st.spinner("Simuliere 8760 Stunden..."):
            st.markdown("---")
            st.markdown("### Jahres-Simulation (8760h)")
            
            annual_simulation = simulate_annual_price_profile(
                building_data,
                include_seasonal_variations=True
            )
            
            # Zusammenfassung
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Jahresverbrauch",
                    f"{format_german_number(annual_simulation['annual_summary']['total_consumption_kwh'], 0)} kWh"
                )
            
            with col2:
                st.metric(
                    "Durchschnittspreis",
                    f"{annual_simulation['annual_summary']['avg_price_eur_kwh']:.3f} €/kWh"
                )
            
            with col3:
                st.metric(
                    "Jahreskosten",
                    f"{format_german_number(annual_simulation['annual_summary']['total_cost_eur'], 0)} €"
                )
            
            with col4:
                st.metric(
                    "WP-Anteil",
                    f"{format_german_number(annual_simulation['annual_summary']['wp_consumption_kwh'], 0)} kWh"
                )
            
            # Chart
            st.markdown("### Kumulative Kostenentwicklung")
            annual_chart = create_annual_cost_chart(
                annual_simulation['monthly_summaries'],
                static_price=0.32
            )
            
            # SHADCN UI THEME ANWENDEN
            apply_chart_theme(annual_chart)
            
            st.plotly_chart(annual_chart, use_container_width=True)
            
            # Peak-Hours
            st.markdown("---")
            st.markdown("### ⏰ Extremwerte")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Teuerste Stunde:**")
                peak = annual_simulation['peak_hours']['most_expensive_hour']
                st.info(f"""
                Stunde {peak['hour']}: {peak['price_eur_kwh']:.3f} €/kWh
                Verbrauch: {format_german_number(peak['total_load_kw'], 2)} kW
                """)
            
            with col2:
                st.markdown("**Günstigste Stunde:**")
                cheapest = annual_simulation['peak_hours']['cheapest_hour']
                st.success(f"""
                Stunde {cheapest['hour']}: {cheapest['price_eur_kwh']:.3f} €/kWh
                Verbrauch: {format_german_number(cheapest['total_load_kw'], 2)} kW
                """)
            
            with col3:
                st.markdown("**Höchster Verbrauch:**")
                highest = annual_simulation['peak_hours']['highest_consumption_hour']
                st.warning(f"""
                Stunde {highest['hour']}: {format_german_number(highest['total_load_kw'], 2)} kW
                Preis: {highest['price_eur_kwh']:.3f} €/kWh
                """)
    
    # VISUALISIERUNG 4: Load-Shifting Heatmap (Todo 18)
    if simulate_heatmap:
        with st.spinner("Erstelle Load-Shifting Heatmap..."):
            st.markdown("---")
            st.markdown("###  Load-Shifting Heatmap (Woche)")
            st.info("""
            **Grün** = Günstige Zeiten (ideal für WP, E-Auto, Waschmaschine)  
            **Rot** = Teure Zeiten (Vermeiden!)
            """)
            
            # Nutze Jahres-Simulation falls vorhanden, sonst neue erstellen
            if 'annual_simulation' not in locals():
                annual_simulation = simulate_annual_price_profile(
                    building_data,
                    include_seasonal_variations=True
                )
            
            heatmap = create_load_shifting_heatmap(annual_simulation['hourly_data'])
            
            # SHADCN UI THEME ANWENDEN
            apply_chart_theme(heatmap)
            
            st.plotly_chart(heatmap, use_container_width=True)
            
            # Empfehlungen
            st.markdown("---")
            st.markdown("### Load-Shifting Empfehlungen")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success("""
                **Beste Zeiten (Grün):**
                - Nachts 22:00 - 06:00 Uhr
                - Mittags 11:00 - 15:00 Uhr (Solar-Peak)
                - Sonntags ganztägig günstiger
                """)
            
            with col2:
                st.error("""
                **Meiden (Rot):**
                - Morgens 06:00 - 09:00 Uhr
                - Abends 17:00 - 21:00 Uhr
                - Montag/Dienstag (höchste Nachfrage)
                """)


# ============================================================================
# NEUE FUNKTION: ERWEITERTE ANALYSE (FEATURES 1.1-8.2)
# ============================================================================

def render_advanced_analysis(texts: dict[str, str], building_data: dict[str, Any], heatpump_data: dict[str, Any]):
    """
    Neue Tab: Erweiterte Analyse
    
    Zeigt alle erweiterten Features:
    - JAZ-Prognose (1.1)
    - Pufferspeicher-Dimensionierung (1.2)
    - Preisszenario-Analyse (2.2)
    - Steuerliche Vorteile (2.3)
    - Lautstärke-Analyse (3.2)
    - Jahresganglinie (3.3)
    - Smart-Grid Integration (4.1)
    - Netzdienlichkeits-Bonus (4.2)
    - Hybrid-Heizung Vergleich (4.3)
    - Lebenszyklus-CO2 (6.1)
    - Kältemittel-Vergleich (6.2)
    - Wartungsplan (8.1)
    - Extremwetter-Simulation (8.2)
    """
    
    st.header("Erweiterte Analyse")
    st.markdown("**Professionelle Detailanalysen für optimale Planung**")
    
    # Sub-Tabs für verschiedene Analysebereiche
    sub_tabs = st.tabs([
        "Dimensionierung",
        "Finanzen",
        "Komfort & Betrieb",
        "Energie-Management",
        "Nachhaltigkeit",
        "Wartung & Szenarien",
        "Vergleichsrechner"
    ])
    
    # ========================================================================
    # TAB 1: DIMENSIONIERUNG (Features 1.1, 1.2)
    # ========================================================================
    with sub_tabs[0]:
        st.subheader("Präzise Dimensionierung")
        
        # Feature 1.1: JAZ-Prognose
        st.markdown("### Realistische JAZ-Prognose")
        st.info("Berücksichtigt 7 Einflussfaktoren für präzise Effizienz-Vorhersage")
        
        jaz_data = calculate_jaz_prognosis(building_data, heatpump_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "JAZ Realistisch",
                f"{jaz_data['jaz_realistic']:.2f}",
                delta=f"{jaz_data['deviation_percent']:+.1f}% vs. SCOP"
            )
        with col2:
            st.metric("JAZ Optimistisch", f"{jaz_data['jaz_optimistic']:.2f}")
        with col3:
            st.metric("JAZ Pessimistisch", f"{jaz_data['jaz_pessimistic']:.2f}")
        
        # JAZ-Faktoren Visualisierung
        jaz_chart = create_jaz_comparison_chart(jaz_data)
        apply_chart_theme(jaz_chart)
        st.plotly_chart(jaz_chart, use_container_width=True)
        
        # Empfehlungen
        with st.expander("Optimierungs-Empfehlungen anzeigen"):
            for rec in jaz_data['recommendations']:
                st.markdown(f"- {rec}")
        
        st.markdown("---")
        
        # Feature 1.2: Pufferspeicher
        st.markdown("###  Pufferspeicher-Dimensionierung")
        
        buffer_data = calculate_buffer_tank_size(heatpump_data, building_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Empfohlene Größe",
                f"{format_german_number(buffer_data['recommended_size_liters'], 0)} Liter"
            )
        with col2:
            st.metric(
                "Kostenrahmen",
                f"{format_german_number(buffer_data['estimated_cost_eur'], 0)} €"
            )
        with col3:
            buffer_priority = buffer_data['buffer_priority']
            priority_emoji = "" if buffer_priority == "Sehr wichtig" else "🟡" if buffer_priority == "Empfohlen" else "🟢"
            st.metric(
                "Priorität",
                f"{priority_emoji} {buffer_priority}"
            )
        
        st.info(f"**Begründung:** {buffer_data['reasoning']}")
        
        with st.expander(" Vorteile eines Pufferspeichers"):
            for benefit in buffer_data['benefits']:
                st.markdown(f"- {benefit}")
    
    # ========================================================================
    # TAB 2: FINANZEN (Features 2.2, 2.3)
    # ========================================================================
    with sub_tabs[1]:
        st.subheader("Finanzielle Analyse")
        
        # Feature 2.2: Preisszenario-Analyse
        st.markdown("### Preisentwicklungs-Szenarien (20 Jahre)")
        
        economics_data = st.session_state.get('economics_data', {})
        price_scenarios = calculate_price_scenarios(building_data, heatpump_data, economics_data)
        
        # Szenarien-Vergleich
        scenarios_df = pd.DataFrame([
            {
                'Szenario': name.capitalize(),
                'Wahrscheinlichkeit': f"{data.get('probability', 0)*100:.0f}%",
                'Amortisation (Jahre)': data.get('payback_year', 'N/A'),
                'Einsparung 20J': f"{format_german_number(data.get('total_savings_20y', 0), 0)} €",
                'ROI': f"{data.get('roi_percent', 0):.1f}%"
            }
            for name, data in price_scenarios['scenarios'].items()
        ])
        
        st.dataframe(scenarios_df, use_container_width=True, hide_index=True)
        
        # Preisentwicklungs-Chart
        price_chart = create_price_scenario_chart(price_scenarios)
        apply_chart_theme(price_chart)
        st.plotly_chart(price_chart, use_container_width=True)
        
        # Best/Worst Case
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"""
            **Best Case (Konservativ):**
            - Einsparung: {format_german_number(price_scenarios['scenarios']['konservativ']['total_savings_20y'], 0)} €
            - Amortisation: {price_scenarios['scenarios']['konservativ']['payback_year']} Jahre
            """)
        with col2:
            st.warning(f"""
            **Worst Case (Pessimistisch):**
            - Einsparung: {format_german_number(price_scenarios['scenarios']['pessimistisch']['total_savings_20y'], 0)} €
            - Amortisation: {price_scenarios['scenarios']['pessimistisch']['payback_year']} Jahre
            """)
        
        st.markdown("---")
        
        # Feature 2.3: Steuerliche Vorteile
        st.markdown("###  Steuerliche Absetzbarkeit")
        
        # FIX: Hole installation_cost aus economics_data für Prozentberechnung
        installation_cost = economics_data.get('installation_cost', 20000)
        tax_benefits = calculate_tax_benefits(heatpump_data, building_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Gesamter Steuervorteil",
                f"{format_german_number(tax_benefits['total_benefit'], 2)} €"
            )
        with col2:
            st.metric(
                "Netto-Investition",
                f"{format_german_number(tax_benefits['net_investment_after_tax'], 2)} €"
            )
        with col3:
            benefit_percent = (tax_benefits['total_benefit'] / installation_cost) * 100 if installation_cost > 0 else 0
            st.metric(
                "Ersparnis",
                f"{benefit_percent:.1f}%"
            )
        
        # Details zu beiden Steuervorteilen
        col1, col2 = st.columns(2)
        with col1:
            hw = tax_benefits['handwerkerleistungen']
            st.info(f"""
            **Handwerkerleistungen (§35a EStG)**
            - Max. pro Jahr: {format_german_number(hw['max_benefit_per_year'], 2)} €
            - Über {hw['years']} Jahre: {format_german_number(hw['total_benefit'], 2)} €
            - Anteilige Arbeitskosten: {format_german_number(hw['labor_cost_estimate'], 2)} €
            """)
        with col2:
            es = tax_benefits.get('energetische_sanierung', {})
            if es.get('eligible', False):
                st.success(f"""
                ** Energetische Sanierung (§35c EStG)**
                - Förderung: {format_german_number(es['total_benefit'], 2)} €
                - Jahr 1-2: je {format_german_number(es['year_1_2'], 2)} € (7%)
                - Jahr 3: {format_german_number(es['year_3'], 2)} € (6%)
                """)
            else:
                st.warning(f"""
                **Energetische Sanierung nicht möglich**
                Grund: {es.get('reason', 'Gebäude zu neu')}
                """)
        
        st.markdown(tax_benefits['recommendation'])
    
    # ========================================================================
    # TAB 3: KOMFORT & BETRIEB (Features 3.2, 3.3)
    # ========================================================================
    with sub_tabs[2]:
        st.subheader("Komfort & Betriebsverhalten")
        
        # Feature 3.2: Lautstärke-Analyse
        st.markdown("###  Lautstärke & Aufstellort (TA Lärm)")
        
        neighbor_distance = st.slider(
            "Abstand zur Grundstücksgrenze (m)",
            min_value=3.0,
            max_value=20.0,
            value=5.0,
            step=0.5
        )
        
        noise_data = calculate_noise_analysis(heatpump_data, building_data, neighbor_distance)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "WP-Lautstärke",
                f"{noise_data['wp_noise_level_dba']} dB(A)"
            )
        with col2:
            st.metric(
                "Beim Nachbarn",
                f"{noise_data['noise_at_neighbor_dba']} dB(A)",
                delta=f"-{noise_data['attenuation']['total']} dB"
            )
        with col3:
            compliant = noise_data['compliance']['night_compliant']
            st.metric(
                "TA Lärm Konform",
                "Ja" if compliant else "Nein"
            )
        
        # Beurteilung
        assessment_color = "success" if "UNKRITISCH" in noise_data['assessment'] else "warning" if "GRENZWERTIG" in noise_data['assessment'] else "error"
        getattr(st, assessment_color)(noise_data['assessment'])
        
        # Schallausbreitungs-Karte
        noise_chart = create_noise_map(noise_data, building_data)
        apply_chart_theme(noise_chart)
        st.plotly_chart(noise_chart, use_container_width=True)
        
        # Optimaler Aufstellort
        with st.expander(" Empfehlungen für optimalen Aufstellort"):
            optimal_location = noise_data['optimal_location']
            st.markdown(f"**Erforderlicher Mindestabstand:** {optimal_location['min_distance_required_m']} m")
            for rec in optimal_location['recommendations']:
                st.markdown(f"- {rec}")
        
        # Schallschutzmaßnahmen (falls erforderlich)
        if noise_data['measures']:
            with st.expander(" Mögliche Schallschutzmaßnahmen"):
                for measure in noise_data['measures']:
                    st.markdown(f"""
                    **{measure['measure']}**
                    - Reduktion: {measure['reduction_db']} dB
                    - Kosten: {measure['cost_eur']}
                    - {measure['description']}
                    """)
        
        st.markdown("---")
        
        # Feature 3.3: Jahresganglinie
        st.markdown("###  Jahresganglinie & Heizprofil")
        
        load_profile = generate_annual_load_profile(building_data, heatpump_data)
        
        # Jahres-Zusammenfassung
        annual = load_profile['annual_summary']
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Wärmebedarf/Jahr",
                f"{format_german_number(annual['total_heat_and_hw_kwh'], 0)} kWh"
            )
        with col2:
            st.metric(
                "Stromverbrauch/Jahr",
                f"{format_german_number(annual['total_electricity_kwh'], 0)} kWh"
            )
        with col3:
            st.metric(
                "Durchschnittliche JAZ",
                f"{annual['average_jaz']:.2f}"
            )
        with col4:
            st.metric(
                "Heiztage/Jahr",
                f"{annual['heating_days_per_year']}"
            )
        
        # Monatsprofil-Chart
        load_profile_chart = create_annual_profile_chart(load_profile)
        apply_chart_theme(load_profile_chart)
        st.plotly_chart(load_profile_chart, use_container_width=True)
        
        # Monats-Tabelle
        with st.expander("Monatliche Details anzeigen"):
            monthly_df = pd.DataFrame(load_profile['monthly_profile'])
            monthly_df['Heizenergie (kWh)'] = monthly_df['heat_demand_kwh'].apply(lambda x: format_german_number(x, 0))
            monthly_df['Strom WP (kWh)'] = monthly_df['total_electricity_kwh'].apply(lambda x: format_german_number(x, 0))
            monthly_df['Außentemp (°C)'] = monthly_df['avg_temp_c']
            monthly_df['Heiztage'] = monthly_df['heating_days']
            
            st.dataframe(
                monthly_df[['month', 'Außentemp (°C)', 'Heiztage', 'Heizenergie (kWh)', 'Strom WP (kWh)']],
                use_container_width=True,
                hide_index=True
            )
    
    # ========================================================================
    # TAB 4: ENERGIE-MANAGEMENT (Features 4.1, 4.2, 4.3)
    # ========================================================================
    with sub_tabs[3]:
        st.subheader("Energie-Management & Flexibilität")
        
        # Feature 4.1: Smart-Grid-Ready
        st.markdown("###  Smart-Grid-Ready Integration")
        
        pv_data = st.session_state.get('pv_integration_data', None)
        sg_benefits = calculate_smart_grid_benefits(building_data, heatpump_data, pv_data)
        
        # Szenarien-Vergleich
        scenarios_comparison = []
        base_cost = sg_benefits['base_annual_cost']
        
        for name, data in sg_benefits['scenarios'].items():
            scenarios_comparison.append({
                'Szenario': name.replace('_', ' ').title(),
                'Jahreskosten': f"{format_german_number(data['annual_cost'], 2)} €",
                'Einsparung': f"{format_german_number(base_cost - data['annual_cost'], 2)} €",
                'Beschreibung': data['description']
            })
        
        st.dataframe(pd.DataFrame(scenarios_comparison), use_container_width=True, hide_index=True)
        
        # Best Scenario
        best = sg_benefits['best_scenario']
        st.success(f"""
        **Bestes Szenario: {best['name'].replace('_', ' ').title()}**
        - Jährliche Einsparung: {format_german_number(best['annual_savings'], 2)} €
        - Gesamtkosten: {format_german_number(best['annual_cost'], 2)} €/Jahr
        """)
        
        # Anforderungen
        with st.expander(" Technische Anforderungen"):
            for req in sg_benefits['requirements']:
                st.markdown(f"- {req}")
        
        # Empfehlungen
        with st.expander("Empfehlungen"):
            for rec in sg_benefits['recommendations']:
                st.markdown(f"- {rec}")
        
        st.markdown("---")
        
        # Feature 4.2: §14a EnWG Bonus
        st.markdown("###  Netzdienlichkeits-Bonus (§14a EnWG)")
        
        grid_bonus = calculate_grid_service_bonus(heatpump_data, building_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Jährlicher Bonus",
                f"{format_german_number(grid_bonus['bonus_annual_eur'], 2)} €"
            )
        with col2:
            st.metric(
                "Variante",
                grid_bonus['bonus_variant']
            )
        with col3:
            st.metric(
                "20-Jahres-Vorteil",
                f"{format_german_number(grid_bonus['benefit_20_years'], 2)} €"
            )
        
        # Dimming-Details
        with st.expander(" Was bedeutet Netzdienlichkeit?"):
            dimming = grid_bonus['dimming_details']
            st.info(f"""
            **Verpflichtung:**
            - Netzbetreiber kann WP dimmen bei Netzengpässen
            - Max. Abregelung: {dimming['max_dimming_percentage']}%
            - Max. Dauer: {dimming['max_dimming_duration_hours']}h pro Eingriff
            - Max. Eingriffe: {dimming['max_interventions_per_day']}/Tag
            - Comfort-Einfluss: {dimming['comfort_impact']}
            """)
        
        # Anmeldeprozess
        with st.expander("Anmeldeprozess beim Netzbetreiber"):
            for step in grid_bonus['application_process']:
                st.markdown(f"- {step}")
        
        st.markdown("---")
        
        # Feature 4.3: Hybrid-Heizung
        st.markdown("###  Hybrid-System Vergleich (Bivalent)")
        
        backup_system = st.selectbox(
            "Backup-System auswählen",
            ['Gaskessel', 'Ölkessel', 'Elektroheizstab']
        )
        
        hybrid_comparison = compare_hybrid_heating(building_data, heatpump_data, backup_system)
        
        # Vergleichstabelle
        comparison_df = pd.DataFrame([
            {
                'System': 'Monovalent (nur WP)',
                'WP-Größe': f"{hybrid_comparison['monovalent_system']['wp_size_kw']:.1f} kW",
                'Investition': f"{format_german_number(hybrid_comparison['monovalent_system']['investment_eur'], 0)} €",
                'Jahreskosten': f"{format_german_number(hybrid_comparison['monovalent_system']['annual_operating_cost_eur'], 0)} €",
                'Kosten 20J': f"{format_german_number(hybrid_comparison['monovalent_system']['total_cost_20y_eur'], 0)} €"
            },
            {
                'System': f"Hybrid (WP + {backup_system})",
                'WP-Größe': f"{hybrid_comparison['hybrid_system']['wp_size_kw']:.1f} kW + Backup",
                'Investition': f"{format_german_number(hybrid_comparison['hybrid_system']['investment_eur'], 0)} €",
                'Jahreskosten': f"{format_german_number(hybrid_comparison['hybrid_system']['annual_operating_cost_eur'], 0)} €",
                'Kosten 20J': f"{format_german_number(hybrid_comparison['hybrid_system']['total_cost_20y_eur'], 0)} €"
            }
        ])
        
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # Empfehlung
        recommendation = hybrid_comparison['comparison']['recommendation']
        rec_color = "success" if "SINNVOLL" in recommendation else "warning" if "GRENZWERTIG" in recommendation else "error"
        getattr(st, rec_color)(recommendation)
        
        # Vor-/Nachteile
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Vorteile Hybrid:**")
            for adv in hybrid_comparison['advantages_hybrid']:
                st.markdown(f"- {adv}")
        with col2:
            st.markdown("**Nachteile Hybrid:**")
            for dis in hybrid_comparison['disadvantages_hybrid']:
                st.markdown(f"- {dis}")
    
    # ========================================================================
    # TAB 5: NACHHALTIGKEIT (Features 6.1, 6.2)
    # ========================================================================
    with sub_tabs[4]:
        st.subheader("Nachhaltigkeit & Umwelt")
        
        # Feature 6.1: Lebenszyklus-CO2
        st.markdown("###  Vollständige Ökobilanz (20 Jahre)")
        
        old_system = building_data.get('heating_system', 'Gasheizung')
        co2_data = calculate_lifecycle_co2(building_data, heatpump_data, old_system)
        
        # Hauptkennzahlen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "CO2-Einsparung (20J)",
                f"{format_german_number(co2_data['einsparung']['total_20y_tonnen_co2'], 1)} t"
            )
        with col2:
            st.metric(
                "Einsparung/Jahr",
                f"{format_german_number(co2_data['einsparung']['annual_kg_co2']/1000, 1)} t"
            )
        with col3:
            break_even = co2_data['einsparung']['break_even_year']
            st.metric(
                "Break-Even",
                f"{break_even} Jahre" if isinstance(break_even, int) else "Nie"
            )
        
        # Bewertung
        interpretation = co2_data['interpretation']
        interp_color = "success" if "HERVORRAGEND" in interpretation or "SEHR GUT" in interpretation else "warning" if "AKZEPTABEL" in interpretation else "error"
        getattr(st, interp_color)(interpretation)
        
        # Lebenszyklus-Chart
        lifecycle_chart = create_lifecycle_chart(co2_data)
        apply_chart_theme(lifecycle_chart)
        st.plotly_chart(lifecycle_chart, use_container_width=True)
        
        # Details
        with st.expander("Detaillierte CO2-Bilanz"):
            col1, col2 = st.columns(2)
            with col1:
                wp_data = co2_data['wärmepumpe']
                st.markdown(f"""
                **Wärmepumpe:**
                - Herstellung: {format_german_number(wp_data['herstellung_kg_co2']/1000, 1)} t
                - Betrieb (20J): {format_german_number(wp_data['betrieb_20y_kg_co2']/1000, 1)} t
                - Entsorgung: {format_german_number(wp_data['entsorgung_kg_co2']/1000, 1)} t
                - **Gesamt: {format_german_number(wp_data['gesamt_20y_kg_co2']/1000, 1)} t**
                """)
            with col2:
                old_data = co2_data['alte_heizung']
                st.markdown(f"""
                **{old_data['system']}:**
                - Herstellung: {format_german_number(old_data['herstellung_kg_co2']/1000, 1)} t
                - Betrieb (20J): {format_german_number(old_data['betrieb_20y_kg_co2']/1000, 1)} t
                - Entsorgung: {format_german_number(old_data['entsorgung_kg_co2']/1000, 1)} t
                - **Gesamt: {format_german_number(old_data['gesamt_20y_kg_co2']/1000, 1)} t**
                """)
        
        st.markdown("---")
        
        # Feature 6.2: Kältemittel-Vergleich
        st.markdown("###  Kältemittel & F-Gas-Compliance")
        
        refrigerant_data = compare_refrigerants(heatpump_data)
        
        current = refrigerant_data['current_refrigerant']
        
        # Aktuelles Kältemittel
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Aktuelles Kältemittel",
                current['name']
            )
        with col2:
            gwp = current['gwp']
            gwp_color = "🟢" if gwp < 150 else "🟡" if gwp < 700 else ""
            st.metric(
                "GWP (CO2-Äquivalent)",
                f"{gwp_color} {gwp}"
            )
        with col3:
            st.metric(
                "Compliant bis",
                current['f_gas_compliant_until']
            )
        
        # Bewertung
        assessment = refrigerant_data['assessment']
        assess_color = "success" if "HERVORRAGEND" in assessment or "SEHR GUT" in assessment else "warning" if "AKZEPTABEL" in assessment or "GRENZWERTIG" in assessment else "error"
        getattr(st, assess_color)(assessment)
        
        # Alternative Kältemittel
        st.markdown("####  Zukunftssichere Alternativen")
        
        alternatives_df = pd.DataFrame([
            {
                'Kältemittel': alt['refrigerant'],
                'GWP': alt['gwp'],
                'Status': alt['status'],
                'Effizienz': alt['efficiency'],
                'Sicherheit': alt['safety_class'],
                'Score': f"{alt['score']}/100"
            }
            for alt in refrigerant_data['alternatives']
        ])
        
        st.dataframe(alternatives_df, use_container_width=True, hide_index=True)
        
        # Empfehlung
        future_proofing = refrigerant_data['future_proofing']
        st.info(f"""
        **Empfehlung für nächsten Kauf:**
        {future_proofing['recommendation']} - {future_proofing['reason']}
        """)
    
    # ========================================================================
    # TAB 6: WARTUNG & SZENARIEN (Features 8.1, 8.2)
    # ========================================================================
    with sub_tabs[5]:
        st.subheader("Wartung & Extrem-Szenarien")
        
        # Feature 8.1: Wartungsplan
        st.markdown("###  20-Jahres-Wartungsplan")
        
        maintenance = calculate_maintenance_schedule(heatpump_data, building_data)
        
        # Zusammenfassung
        summary = maintenance['summary']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Wartungskosten (20J)",
                f"{format_german_number(summary['total_maintenance_cost_20y_eur'], 0)} €"
            )
        with col2:
            st.metric(
                "Durchschnitt/Jahr",
                f"{format_german_number(summary['average_annual_cost_eur'], 0)} €"
            )
        with col3:
            st.metric(
                "Größte Services",
                "Jahr 5, 10, 15"
            )
        
        # Wartungsplan-Timeline
        maintenance_chart = create_maintenance_timeline(maintenance)
        apply_chart_theme(maintenance_chart)
        st.plotly_chart(maintenance_chart, use_container_width=True)
        
        # Große Wartungen
        with st.expander("Wichtige Wartungs-Meilensteine"):
            for service in summary['major_services']:
                st.markdown(f"- {service}")
        
        # Garantie
        with st.expander(" Garantie & Versicherung"):
            warranty = maintenance['warranty_info']
            st.info(f"""
            **Standard-Garantie:** {warranty['standard_warranty_years']} Jahre
            
            **Erweiterte Garantie verfügbar:**
            - Laufzeit: {warranty['extended_warranty_years']} Jahre
            - Kosten: {format_german_number(warranty['extended_warranty_cost_eur'], 0)} €
            - Empfehlung: {warranty['recommendation']}
            """)
        
        st.markdown("---")
        
        # Feature 8.2: Extremwetter-Simulation
        st.markdown("### Extremwetter-Szenarien")
        
        scenario = st.selectbox(
            "Szenario auswählen",
            ['Kältewelle', 'Blackout', 'Hitzewelle']
        )
        
        extreme_weather = simulate_extreme_weather(building_data, heatpump_data, scenario)
        
        # Szenario-Titel
        st.markdown(f"#### {extreme_weather['scenario']}")
        
        # Bedingungen
        if 'conditions' in extreme_weather:
            st.info(f"""
            **Bedingungen:**
            {', '.join([f"{k.replace('_', ' ').title()}: {v}" for k, v in extreme_weather['conditions'].items()])}
            """)
        
        # Bewertung
        assessment = extreme_weather['assessment']
        assess_color = "success" if "UNKRITISCH" in assessment or "AUSREICHEND" in assessment or "VERFÜGBAR" in assessment else "warning" if "UNBEQUEM" in assessment or "UNTERDIMENSIONIERT" in assessment else "error"
        getattr(st, assess_color)(assessment)
        
        # Auswirkungen
        if 'impact' in extreme_weather:
            st.markdown("**Auswirkungen:**")
            impact_df = pd.DataFrame([
                {'Kennzahl': k.replace('_', ' ').title(), 'Wert': str(v)}
                for k, v in extreme_weather['impact'].items()
            ])
            st.dataframe(impact_df, use_container_width=True, hide_index=True)
        
        # Empfehlungen
        if 'recommendations' in extreme_weather:
            with st.expander("Empfehlungen & Maßnahmen"):
                for rec in extreme_weather['recommendations']:
                    st.markdown(f"- {rec}")
    
    # ========================================================================
    # TAB 7: VERGLEICHSRECHNER (Feature 7.1)
    # ========================================================================
    with sub_tabs[6]:
        st.subheader("Wärmepumpen-Vergleichsrechner")
        st.info("Vergleichen Sie bis zu 6 Wärmepumpen-Modelle nach 10 Kriterien mit gewichteter Bewertung")
        
        st.markdown("###  Wärmepumpen auswählen")
        
        # Liste für Vergleichs-WPs aufbauen
        if 'comparison_heatpumps' not in st.session_state:
            st.session_state['comparison_heatpumps'] = [heatpump_data.copy()]  # Aktuelle WP als erste
        
        # Anzahl der WPs zum Vergleich
        num_heatpumps = st.slider(
            "Anzahl Wärmepumpen im Vergleich:",
            min_value=2,
            max_value=6,
            value=min(len(st.session_state['comparison_heatpumps']), 6),
            help="Mindestens 2, maximal 6 Wärmepumpen"
        )
        
        # Passe Liste an
        current_count = len(st.session_state['comparison_heatpumps'])
        if num_heatpumps > current_count:
            # Füge neue WPs hinzu (als Kopien der ersten)
            for _ in range(num_heatpumps - current_count):
                new_hp = heatpump_data.copy()
                new_hp['model'] = f"Modell {len(st.session_state['comparison_heatpumps']) + 1}"
                st.session_state['comparison_heatpumps'].append(new_hp)
        elif num_heatpumps < current_count:
            # Entferne überschüssige WPs
            st.session_state['comparison_heatpumps'] = st.session_state['comparison_heatpumps'][:num_heatpumps]
        
        # Editierbare Parameter für jede WP
        st.markdown("---")
        st.markdown("**Wärmepumpen-Daten bearbeiten:**")
        
        hp_cols = st.columns(min(num_heatpumps, 3))  # Max. 3 Spalten
        
        for idx in range(num_heatpumps):
            col_idx = idx % 3
            with hp_cols[col_idx]:
                with st.expander(f"**WP {idx + 1}:** {st.session_state['comparison_heatpumps'][idx].get('manufacturer', 'Hersteller')} {st.session_state['comparison_heatpumps'][idx].get('model', 'Modell')}", expanded=(idx < 2)):
                    hp = st.session_state['comparison_heatpumps'][idx]
                    
                    hp['manufacturer'] = st.text_input(
                        "Hersteller:",
                        value=hp.get('manufacturer', 'Unbekannt'),
                        key=f"hp_manufacturer_{idx}"
                    )
                    
                    hp['model'] = st.text_input(
                        "Modell:",
                        value=hp.get('model', 'Modell'),
                        key=f"hp_model_{idx}"
                    )
                    
                    hp['price'] = st.number_input(
                        "Preis [€]:",
                        min_value=5000,
                        max_value=50000,
                        value=int(hp.get('price', 15000)),
                        step=500,
                        key=f"hp_price_{idx}"
                    )
                    
                    hp['heating_power'] = st.number_input(
                        "Heizleistung [kW]:",
                        min_value=3.0,
                        max_value=30.0,
                        value=float(hp.get('heating_power', 10.0)),
                        step=0.5,
                        key=f"hp_power_{idx}"
                    )
                    
                    hp['scop'] = st.number_input(
                        "SCOP:",
                        min_value=2.0,
                        max_value=6.0,
                        value=float(hp.get('scop', 4.0)),
                        step=0.1,
                        key=f"hp_scop_{idx}"
                    )
                    
                    hp['noise_level'] = st.number_input(
                        "Schallleistung [dB(A)]:",
                        min_value=30,
                        max_value=70,
                        value=int(hp.get('noise_level', 45)),
                        key=f"hp_noise_{idx}"
                    )
                    
                    hp['refrigerant'] = st.selectbox(
                        "Kältemittel:",
                        options=['R32', 'R290', 'R410A', 'R454C', 'R1234yf', 'R744'],
                        index=['R32', 'R290', 'R410A', 'R454C', 'R1234yf', 'R744'].index(hp.get('refrigerant', 'R32')),
                        key=f"hp_refrigerant_{idx}"
                    )
        
        st.markdown("---")
        
        # Button zum Vergleich starten
        if st.button("Vergleich durchführen", type="primary", use_container_width=True):
            with st.spinner("Umfassende Analyse läuft... (10 Kriterien werden bewertet)"):
                comparison_result = compare_multiple_heatpumps(
                    building_data,
                    st.session_state['comparison_heatpumps']
                )
                
                if 'error' in comparison_result:
                    st.error(comparison_result['error'])
                else:
                    st.success(f"Vergleich abgeschlossen: {comparison_result['count']} Wärmepumpen analysiert")
                    
                    # ===== RANKING =====
                    st.markdown("###  Ranking")
                    
                    # Ranking-Tabelle
                    ranking_df = pd.DataFrame(comparison_result['ranking'])
                    ranking_df = ranking_df[['rank', 'medal', 'name', 'total_score', 'rating']]
                    ranking_df.columns = ['#', '', 'Modell', 'Punkte', 'Bewertung']
                    
                    st.dataframe(
                        ranking_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Gesamtpunktzahl Balkendiagramm
                    bar_fig = create_comparison_bar_chart(comparison_result)
                    apply_chart_theme(bar_fig)
                    st.plotly_chart(bar_fig, use_container_width=True)
                    
                    # ===== EMPFEHLUNG =====
                    st.markdown("### Unsere Empfehlung")
                    
                    rec = comparison_result['recommendation']
                    winner = rec['winner']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            " Testsieger",
                            winner['name'],
                            f"{winner['total_score']:.1f} Punkte"
                        )
                    with col2:
                        st.metric(
                            "Preis",
                            format_german_number(winner['price'], 0) + " €"
                        )
                    with col3:
                        st.metric(
                            "Jährl. Einsparung vs. #2",
                            format_german_number(winner['annual_savings_vs_runner_up'], 2) + " €"
                        )
                    
                    # Stärken des Siegers
                    if winner['strengths']:
                        st.success("**Besondere Stärken:**")
                        for strength in winner['strengths']:
                            st.markdown(f"- {strength}")
                    
                    # Allgemeine Ratschläge
                    if rec['general_advice']:
                        with st.expander("Allgemeine Hinweise"):
                            for advice in rec['general_advice']:
                                st.warning(advice)
                    
                    # ===== DETAILLIERTER VERGLEICH =====
                    st.markdown("### Detaillierter Vergleich")
                    
                    # Radar Chart (Multi-Kriterien)
                    radar_fig = create_comparison_radar_chart(comparison_result)
                    apply_chart_theme(radar_fig)
                    st.plotly_chart(radar_fig, use_container_width=True)
                    
                    # Heatmap (Score-Breakdown)
                    heatmap_fig = create_comparison_heatmap(comparison_result)
                    apply_chart_theme(heatmap_fig)
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                    
                    # Kostenvergleich
                    cost_fig = create_comparison_cost_chart(comparison_result)
                    apply_chart_theme(cost_fig)
                    st.plotly_chart(cost_fig, use_container_width=True)
                    
                    # ===== KATEGORIE-GEWINNER =====
                    st.markdown("###  Kategorie-Gewinner")
                    
                    cat_winners = comparison_result['category_winners']
                    
                    cat_cols = st.columns(5)
                    
                    with cat_cols[0]:
                        st.metric(
                            "Beste Effizienz",
                            cat_winners['beste_effizienz']['name'][:20] + "..." if len(cat_winners['beste_effizienz']['name']) > 20 else cat_winners['beste_effizienz']['name'],
                            f"JAZ {cat_winners['beste_effizienz']['value']:.2f}"
                        )
                    
                    with cat_cols[1]:
                        st.metric(
                            "Günstigste",
                            cat_winners['guenstigste_anschaffung']['name'][:20] + "..." if len(cat_winners['guenstigste_anschaffung']['name']) > 20 else cat_winners['guenstigste_anschaffung']['name'],
                            format_german_number(cat_winners['guenstigste_anschaffung']['value'], 0) + " €"
                        )
                    
                    with cat_cols[2]:
                        st.metric(
                            "Niedrigste Kosten",
                            cat_winners['niedrigste_betriebskosten']['name'][:20] + "..." if len(cat_winners['niedrigste_betriebskosten']['name']) > 20 else cat_winners['niedrigste_betriebskosten']['name'],
                            format_german_number(cat_winners['niedrigste_betriebskosten']['value'], 0) + " €/Jahr"
                        )
                    
                    with cat_cols[3]:
                        st.metric(
                            "Beste Ökobilanz",
                            cat_winners['beste_oekobilanz']['name'][:20] + "..." if len(cat_winners['beste_oekobilanz']['name']) > 20 else cat_winners['beste_oekobilanz']['name'],
                            format_german_number(cat_winners['beste_oekobilanz']['value'], 0) + " kg CO2 gespart"
                        )
                    
                    with cat_cols[4]:
                        st.metric(
                            "Leiseste",
                            cat_winners['leiseste']['name'][:20] + "..." if len(cat_winners['leiseste']['name']) > 20 else cat_winners['leiseste']['name'],
                            f"{cat_winners['leiseste']['value']:.1f} dB(A)"
                        )
                    
                    # ===== SCORING-METHODIK =====
                    with st.expander("Bewertungs-Methodik (Gewichtung)"):
                        st.markdown("""
                        **Gewichtete 10-Kriterien-Bewertung:**
                        
                        Die Gesamtpunktzahl (0-100) ergibt sich aus:
                        """)
                        
                        weights = comparison_result['score_breakdown']['weights']
                        weight_df = pd.DataFrame([
                            {'Kriterium': k, 'Gewichtung': v}
                            for k, v in weights.items()
                        ])
                        st.dataframe(weight_df, use_container_width=True, hide_index=True)
                        
                        st.info("Jedes Kriterium wird auf 0-100 Punkte normalisiert und mit dem Gewicht multipliziert.")


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
