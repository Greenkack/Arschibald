# === AUTO-GENERATED INSERT PATCH ===
# target_module: analysis.py

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import traceback
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import math
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple
import os
import time  # Für Timestamp-Funktionalität
from reportlab.lib import colors  # Für HexColor Zugriff
import colorsys  # Für HLS/RGB Konvertierungen
from datetime import datetime, timedelta
from calculations import AdvancedCalculationsIntegrator
from financial_tools import (
from typing import Dict, Any, Optional

# --- DEF BLOCK START: func create_four_type_chart ---
def create_four_type_chart(
    data: Dict[str, Any],
    title: str,
    chart_key: str,
    x_label: str="",
    y_label: str="",
):
    """Spezielle Helper-Funktion nur mit vier erlaubten Typen: Balken, Säulen, Kreis, Donut.
    Unterstützt entweder (x,y) oder (labels,values).
    """
    col1, col2=st.columns([2, 1])
    with col1:
        st.markdown(f"### {title}")
    with col2:
        chart_type=st.selectbox(
            "Diagrammtyp:",
            ["Säulen", "Balken", "Kreis", "Donut"],
            key=f"{chart_key}_four_type",
        )
    try:
        if "x" in data and "y" in data:
            df=pd.DataFrame({"x": data["x"], "y": data["y"]})
            if chart_type == "Säulen":
                fig=px.bar(
    df, x="x", y="y", title=title, labels={
        "x": x_label, "y": y_label})
            elif chart_type == "Balken":
                fig=px.bar(
    df,
    x="y",
    y="x",
    orientation="h",
    title=title,
    labels={
        "y": x_label,
         "x": y_label})
            elif chart_type in ("Kreis", "Donut"):
                hole=0.4 if chart_type == "Donut" else 0
                fig=px.pie(df, names="x", values="y", title=title, hole=hole)
        elif "labels" in data and "values" in data:
            df=pd.DataFrame(
                {"labels": data["labels"], "values": data["values"]})
            if chart_type == "Säulen":
                fig=px.bar(
    df,
    x="labels",
    y="values",
    title=title,
    labels={
        "labels": x_label,
         "values": y_label})
            elif chart_type == "Balken":
                fig=px.bar(
    df,
    x="values",
    y="labels",
    orientation="h",
    title=title,
    labels={
        "values": y_label,
         "labels": x_label})
            else:  # Kreis / Donut
                hole=0.4 if chart_type == "Donut" else 0
                fig=px.pie(
    df,
    names="labels",
    values="values",
    title=title,
     hole=hole)
        else:
            import plotly.graph_objects as go
            fig=go.Figure()
            fig.add_annotation(
                text="Unbekanntes Datenformat für vier-Typ-Chart",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="red"),
            )
            fig.update_layout(title=title)
        _apply_shadcn_like_theme(fig)
        return fig
    except Exception as e:
        import plotly.graph_objects as go
        fig=go.Figure()
        fig.add_annotation(
            text=f"Fehler: {e}", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title=title)
        st.error(f"Chart Fehler: {e}")
        return fig
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func _get_baseline_annual_costs_without_pv ---
def _get_baseline_annual_costs_without_pv(
    project_data: Dict[str, Any] | None,
    project_details: Dict[str, Any] | None,
    analysis_results: Dict[str, Any] | None,
) -> float:
    """Ermittelt die jährlichen Stromkosten (ohne Photovoltaik) mit robusten Fallbacks.

    Reihenfolge der Quellen (analog placeholders._get_monthly_cost_eur):
    - project_data: monatlich Haushalt/Heizung, sonst jährlich -> Monat -> *12
    - project_details: wie oben
    - analysis_results: jahresverbrauch * aktueller_strompreis
    """
    project_data=project_data or {}
    project_details=project_details or {}
    analysis_results=analysis_results or {}

    def _parse_float(val: Any) -> float | None:
        try:
            if val is None:
                return None
            if isinstance(val, (int, float)):
                return float(val)
            s=str(val).strip()
            s=re.sub(r"[^0-9,\.\-]", "", s).replace(",", ".")
            return float(s) if s not in {"", "-", "."} else None
        except Exception:
            return None

    # 1) project_data monatlich
    hh=_parse_float(project_data.get("stromkosten_haushalt_euro_monat")) or 0.0
    hz=_parse_float(project_data.get("stromkosten_heizung_euro_monat")) or 0.0
    if (hh + hz) > 0:
        return float((hh + hz) * 12.0)
    # jährlich -> Monat
    ah=_parse_float(project_data.get("stromkosten_haushalt_euro_jahr")) or 0.0
    az=_parse_float(project_data.get("stromkosten_heizung_euro_jahr")) or 0.0
    total_a=ah + az
    if total_a > 0:
        return float(total_a)
    # gesamtsumme jährlich
    total_a2=_parse_float(project_data.get("stromkosten_gesamt_euro_jahr"))
    if total_a2 is None:
        total_a2=_parse_float(project_data.get("stromkosten_gesamt_jahr_eur"))
    if (total_a2 or 0.0) > 0:
        return float(total_a2 or 0.0)

    # 2) project_details
    hh=_parse_float(project_details.get(
        "stromkosten_haushalt_euro_monat")) or 0.0
    hz=_parse_float(project_details.get(
        "stromkosten_heizung_euro_monat")) or 0.0
    if (hh + hz) > 0:
        return float((hh + hz) * 12.0)
    ah=_parse_float(project_details.get(
        "stromkosten_haushalt_euro_jahr")) or 0.0
    az=_parse_float(project_details.get(
        "stromkosten_heizung_euro_jahr")) or 0.0
    total_a=ah + az
    if total_a > 0:
        return float(total_a)
    total_a2=_parse_float(project_details.get("stromkosten_gesamt_euro_jahr"))
    if total_a2 is None:
        total_a2=_parse_float(
    project_details.get("stromkosten_gesamt_jahr_eur"))
    if (total_a2 or 0.0) > 0:
        return float(total_a2 or 0.0)

    # 3) analysis_results (verbrauch * preis)
    cons_kwh=_parse_float(analysis_results.get(
        "jahresstromverbrauch_fuer_hochrechnung_kwh")) or 0.0
    price_eur_kwh=_parse_float(analysis_results.get(
        "aktueller_strompreis_fuer_hochrechnung_euro_kwh")) or 0.0
    if cons_kwh > 0 and price_eur_kwh > 0:
        return float(cons_kwh * price_eur_kwh)

    return 0.0
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func _compute_annual_cost_series ---
def _compute_annual_cost_series(
    base_annual_cost: float,
    years: int,
     inc_percent: float) -> List[float]:
    """Erzeugt eine Jahreskosten-Serie über 'years' Jahre.

    - base_annual_cost: Startwert in Jahr 1 (€/Jahr)
    - inc_percent: jährliche Preissteigerung in % (z. B. 5.0)
    Rückgabe: Liste der jährlichen Kosten je Jahr (nicht kumuliert).
    """
    try:
        years=int(max(1, years))
        base=float(max(0.0, base_annual_cost))
        r=max(0.0, float(inc_percent)) / 100.0
    except Exception:
        years, base, r=20, 0.0, 0.0
    series: List[float]=[]
    for i in range(years):
        series.append(base * ((1.0 + r) ** i))
    return series
# --- DEF BLOCK END ---
