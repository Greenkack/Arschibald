"""
🎨 VISUALISIERUNGS-MODUL FÜR ERWEITERTE WÄRMEPUMPEN-FEATURES

Dieses Modul erstellt professionelle Visualisierungen für die erweiterten
Features aus heatpump_advanced_calculations.py.

Features:
- 9.1: 3D-Systemvisualisierung (erweitert)
- 9.2: KPI-Dashboard
- Zusätzliche Charts für alle Berechnungen

Autor: AI-Assistent
Datum: 2024
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import streamlit as st


# ============================================================================
# FEATURE 9.1: 3D-SYSTEMVISUALISIERUNG (ERWEITERT)
# ============================================================================

def create_system_3d_visualization(
    building_data: Dict[str, Any],
    heatpump_data: Dict[str, Any],
    buffer_data: Dict[str, Any] = None,
    pv_data: Dict[str, Any] = None
) -> go.Figure:
    """
    Erstellt erweiterte 3D-Visualisierung des kompletten Heizsystems
    
    Zeigt:
    - Wärmepumpe (Außeneinheit)
    - Pufferspeicher
    - Heizkreise
    - PV-Anlage (falls vorhanden)
    - Komponenten-Verbindungen
    
    Returns:
    - Plotly 3D Figure
    """
    
    fig = go.Figure()
    
    # Gebäude-Basis (vereinfacht als Box)
    area = building_data.get('area', 150)
    building_width = np.sqrt(area)
    building_height = 6  # m
    
    # Gebäude
    fig.add_trace(go.Mesh3d(
        x=[0, building_width, building_width, 0, 0, building_width, building_width, 0],
        y=[0, 0, building_width, building_width, 0, 0, building_width, building_width],
        z=[0, 0, 0, 0, building_height, building_height, building_height, building_height],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        opacity=0.3,
        color='lightblue',
        name='Gebäude',
        hovertext=f"Gebäude: {area:.0f} m²"
    ))
    
    # Wärmepumpe Außeneinheit (vor dem Gebäude)
    wp_x = -3
    wp_y = building_width / 2
    wp_z = 0
    wp_width = 1.2
    wp_depth = 0.8
    wp_height = 1.5
    
    fig.add_trace(go.Mesh3d(
        x=[wp_x, wp_x + wp_width, wp_x + wp_width, wp_x, wp_x, wp_x + wp_width, wp_x + wp_width, wp_x],
        y=[wp_y - wp_depth/2, wp_y - wp_depth/2, wp_y + wp_depth/2, wp_y + wp_depth/2, 
           wp_y - wp_depth/2, wp_y - wp_depth/2, wp_y + wp_depth/2, wp_y + wp_depth/2],
        z=[wp_z, wp_z, wp_z, wp_z, wp_z + wp_height, wp_z + wp_height, wp_z + wp_height, wp_z + wp_height],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        opacity=0.8,
        color='darkgreen',
        name='Wärmepumpe',
        hovertext=f"WP: {heatpump_data.get('manufacturer', 'N/A')} {heatpump_data.get('model', 'N/A')}<br>"
                  f"Leistung: {heatpump_data.get('heating_power', 0):.1f} kW<br>"
                  f"SCOP: {heatpump_data.get('scop', 0):.1f}"
    ))
    
    # Pufferspeicher (im Gebäude)
    if buffer_data:
        buffer_size = buffer_data.get('recommended_size_liters', 500)
        # Größe abhängig von Speichervolumen
        buffer_radius = 0.3 + (buffer_size / 2000) * 0.2  # 0.3-0.5m
        buffer_height = 1.2 + (buffer_size / 1000) * 0.5  # 1.2-1.8m
        
        buffer_x = building_width / 4
        buffer_y = building_width / 4
        buffer_z = 0
        
        # Zylinder für Pufferspeicher (vereinfacht als Mesh)
        theta = np.linspace(0, 2*np.pi, 20)
        z_buffer = np.linspace(buffer_z, buffer_z + buffer_height, 10)
        
        x_buffer = buffer_x + buffer_radius * np.outer(np.cos(theta), np.ones(len(z_buffer)))
        y_buffer = buffer_y + buffer_radius * np.outer(np.sin(theta), np.ones(len(z_buffer)))
        z_buffer_mesh = np.outer(np.ones(len(theta)), z_buffer)
        
        fig.add_trace(go.Surface(
            x=x_buffer,
            y=y_buffer,
            z=z_buffer_mesh,
            opacity=0.7,
            colorscale=[[0, 'orange'], [1, 'red']],
            showscale=False,
            name='Pufferspeicher',
            hovertext=f"Pufferspeicher: {buffer_size:.0f} L"
        ))
    
    # PV-Anlage auf Dach (falls vorhanden)
    if pv_data and pv_data.get('installed', False):
        pv_power = pv_data.get('capacity_kwp', 10)
        # PV-Panels als Fläche auf Dach
        pv_panels = int(pv_power / 0.4)  # Ca. 2.5 Panels pro kWp
        
        panel_width = 1.0
        panel_length = 1.7
        panels_per_row = int(np.sqrt(pv_panels))
        
        for i in range(panels_per_row):
            for j in range(min(panels_per_row, pv_panels - i * panels_per_row)):
                x_start = 1 + i * panel_width * 1.1
                y_start = 1 + j * panel_length * 1.1
                
                if x_start + panel_width < building_width - 1 and y_start + panel_length < building_width - 1:
                    fig.add_trace(go.Mesh3d(
                        x=[x_start, x_start + panel_width, x_start + panel_width, x_start],
                        y=[y_start, y_start, y_start + panel_length, y_start + panel_length],
                        z=[building_height, building_height, building_height, building_height],
                        i=[0, 0],
                        j=[1, 2],
                        k=[2, 3],
                        opacity=0.8,
                        color='darkblue',
                        name='PV-Panel' if i == 0 and j == 0 else None,
                        showlegend=True if i == 0 and j == 0 else False,
                        hovertext=f"PV-Anlage: {pv_power:.1f} kWp"
                    ))
    
    # Verbindungsleitungen (WP → Pufferspeicher)
    if buffer_data:
        fig.add_trace(go.Scatter3d(
            x=[wp_x + wp_width, buffer_x],
            y=[wp_y, buffer_y],
            z=[wp_z + wp_height/2, buffer_z + buffer_height/2],
            mode='lines',
            line=dict(color='red', width=8, dash='dash'),
            name='Heizleitung',
            hovertext='Vorlauf (warm)'
        ))
        
        fig.add_trace(go.Scatter3d(
            x=[wp_x + wp_width, buffer_x],
            y=[wp_y, buffer_y],
            z=[wp_z + wp_height/3, buffer_z + buffer_height/3],
            mode='lines',
            line=dict(color='blue', width=8, dash='dash'),
            name='Rücklauf',
            hovertext='Rücklauf (kalt)'
        ))
    
    # Layout
    fig.update_layout(
        title=dict(
            text=f"<b>3D-Systemübersicht: Wärmepumpen-Anlage</b><br>"
                 f"<sub>{heatpump_data.get('manufacturer', 'N/A')} {heatpump_data.get('model', 'N/A')} | "
                 f"{area:.0f}m² Wohnfläche</sub>",
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis=dict(title='X [m]', backgroundcolor="rgb(230, 230,230)", gridcolor="white"),
            yaxis=dict(title='Y [m]', backgroundcolor="rgb(230, 230,230)", gridcolor="white"),
            zaxis=dict(title='Höhe [m]', backgroundcolor="rgb(230, 230,230)", gridcolor="white"),
            aspectmode='data'
        ),
        showlegend=True,
        height=700,
        paper_bgcolor='white',
        plot_bgcolor='rgba(240,240,240,0.9)'
    )
    
    return fig


# ============================================================================
# FEATURE 9.2: KPI-DASHBOARD
# ============================================================================

def create_kpi_dashboard(
    building_data: Dict[str, Any],
    heatpump_data: Dict[str, Any],
    economics_data: Dict[str, Any],
    jaz_data: Dict[str, Any],
    co2_data: Dict[str, Any],
    noise_data: Dict[str, Any] = None
) -> go.Figure:
    """
    Erstellt interaktives KPI-Dashboard mit wichtigsten Kennzahlen
    
    KPIs:
    - JAZ (Jahresarbeitszahl)
    - Jährliche Kosten
    - CO2-Einsparung
    - Amortisationszeit
    - Effizienz-Rating
    - Lautstärke
    
    Returns:
    - Plotly Subplot Figure mit Gauges und Indikatoren
    """
    
    # Subplot erstellen (2x3 Grid)
    fig = make_subplots(
        rows=2, cols=3,
        specs=[
            [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
            [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]
        ],
        subplot_titles=(
            'Jahresarbeitszahl (JAZ)', 
            'Jährliche Heizkosten', 
            'CO2-Einsparung/Jahr',
            'Amortisationszeit', 
            'Effizienz-Rating', 
            'Lautstärke'
        )
    )
    
    # KPI 1: JAZ (Gauge)
    jaz_value = jaz_data.get('jaz_realistic', 4.0)
    jaz_rating = 'Hervorragend' if jaz_value > 4.5 else 'Sehr gut' if jaz_value > 4.0 else 'Gut' if jaz_value > 3.5 else 'Mittel'
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=jaz_value,
        title={'text': f"JAZ: {jaz_rating}"},
        delta={'reference': heatpump_data.get('scop', 4.5), 'suffix': ' (vs. SCOP)'},
        gauge={
            'axis': {'range': [2, 6], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkgreen"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [2, 3.5], 'color': 'lightcoral'},
                {'range': [3.5, 4.0], 'color': 'lightyellow'},
                {'range': [4.0, 4.5], 'color': 'lightgreen'},
                {'range': [4.5, 6], 'color': 'darkgreen'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 5.0
            }
        }
    ), row=1, col=1)
    
    # KPI 2: Jährliche Kosten (Number + Delta)
    annual_cost = economics_data.get('annual_hp_cost', 1500)
    old_system_cost = building_data.get('heating_costs', {}).get('annual_heating_cost', 2500)
    savings = old_system_cost - annual_cost
    
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=annual_cost,
        title={'text': "Jährliche Heizkosten"},
        delta={
            'reference': old_system_cost,
            'relative': False,
            'valueformat': '.0f',
            'suffix': '€ Einsparung'
        },
        number={'suffix': '€', 'valueformat': ',.0f'},
        domain={'x': [0, 1], 'y': [0, 1]}
    ), row=1, col=2)
    
    # KPI 3: CO2-Einsparung (Number)
    co2_savings_annual = co2_data.get('einsparung', {}).get('annual_kg_co2', 3000)
    
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=co2_savings_annual,
        title={'text': "CO2-Einsparung/Jahr"},
        number={'suffix': ' kg', 'valueformat': ',.0f'},
        delta={
            'reference': 0,
            'increasing': {'color': 'green'},
            'suffix': ' eingespart'
        }
    ), row=1, col=3)
    
    # KPI 4: Amortisationszeit (Gauge)
    investment = economics_data.get('installation_cost', 20000)
    payback_years = investment / savings if savings > 0 else 99
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=payback_years,
        title={'text': "Amortisation"},
        number={'suffix': ' Jahre'},
        gauge={
            'axis': {'range': [0, 25], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 10], 'color': 'lightgreen'},
                {'range': [10, 15], 'color': 'lightyellow'},
                {'range': [15, 20], 'color': 'lightcoral'},
                {'range': [20, 25], 'color': 'darkred'}
            ],
            'threshold': {
                'line': {'color': "green", 'width': 4},
                'thickness': 0.75,
                'value': 10
            }
        }
    ), row=2, col=1)
    
    # KPI 5: Effizienz-Rating (Sterne)
    # Rating basiert auf JAZ, CO2, Kosten
    rating_score = 0
    if jaz_value > 4.5:
        rating_score += 2
    elif jaz_value > 4.0:
        rating_score += 1.5
    elif jaz_value > 3.5:
        rating_score += 1
    
    if savings > 500:
        rating_score += 2
    elif savings > 300:
        rating_score += 1.5
    elif savings > 0:
        rating_score += 1
    
    if co2_savings_annual > 3000:
        rating_score += 1
    elif co2_savings_annual > 2000:
        rating_score += 0.5
    
    rating_stars = min(5, rating_score)
    rating_text = '⭐' * int(rating_stars) + ('½' if rating_stars % 1 >= 0.5 else '')
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=rating_stars,
        title={'text': f"Effizienz-Rating<br>{rating_text}"},
        number={'suffix': '/5', 'valueformat': '.1f'}
    ), row=2, col=2)
    
    # KPI 6: Lautstärke (falls vorhanden)
    if noise_data:
        noise_level = noise_data.get('noise_at_neighbor_dba', 40)
        compliant = noise_data.get('compliance', {}).get('night_compliant', True)
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=noise_level,
            title={'text': "Lautstärke (Nachbar)"},
            number={'suffix': ' dB(A)'},
            gauge={
                'axis': {'range': [25, 60], 'tickwidth': 1},
                'bar': {'color': "green" if compliant else "red"},
                'steps': [
                    {'range': [25, 35], 'color': 'lightgreen'},
                    {'range': [35, 40], 'color': 'lightyellow'},
                    {'range': [40, 50], 'color': 'lightcoral'},
                    {'range': [50, 60], 'color': 'darkred'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 40  # Typischer Nachtwert Wohngebiet
                }
            }
        ), row=2, col=3)
    else:
        # Fallback: Hersteller-Wert
        noise_wp = heatpump_data.get('noise_level', 45)
        fig.add_trace(go.Indicator(
            mode="number",
            value=noise_wp,
            title={'text': "Lautstärke (WP)"},
            number={'suffix': ' dB(A)'}
        ), row=2, col=3)
    
    # Layout
    fig.update_layout(
        title=dict(
            text=f"<b>📊 KPI-Dashboard: {heatpump_data.get('manufacturer', 'N/A')} {heatpump_data.get('model', 'N/A')}</b>",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        height=700,
        showlegend=False,
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig


# ============================================================================
# ZUSATZ-CHARTS FÜR BERECHNUNGEN
# ============================================================================

def create_jaz_comparison_chart(jaz_data: Dict[str, Any]) -> go.Figure:
    """
    Vergleicht JAZ mit SCOP und zeigt Einflussfaktoren
    """
    
    factors = jaz_data.get('factors', {})
    
    # Balkendiagramm für Faktoren
    factor_names = list(factors.keys())
    factor_impacts = [factors[f].get('impact_percent', 0) for f in factor_names]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=factor_names,
        y=factor_impacts,
        marker_color=['green' if v > 0 else 'red' for v in factor_impacts],
        text=[f"{v:+.1f}%" for v in factor_impacts],
        textposition='outside',
        hovertemplate='%{x}<br>Einfluss: %{y:+.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="<b>JAZ-Einflussfaktoren</b><br><sub>Abweichungen vom Hersteller-SCOP</sub>",
        xaxis_title="Faktor",
        yaxis_title="Einfluss (%)",
        height=500,
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='rgba(240,240,240,0.9)',
        separators=',.'
    )
    
    return fig


def create_annual_profile_chart(load_profile: Dict[str, Any]) -> go.Figure:
    """
    Jahresganglinie: Monatlicher Energiebedarf
    """
    
    monthly_data = load_profile.get('monthly_profile', [])
    
    months = [m['month'] for m in monthly_data]
    heat_demand = [m['heat_demand_kwh'] for m in monthly_data]
    electricity = [m['total_electricity_kwh'] for m in monthly_data]
    temps = [m['avg_temp_c'] for m in monthly_data]
    
    # Subplot: Balken + Linie
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(
            x=months,
            y=heat_demand,
            name='Wärmebedarf',
            marker_color='orange',
            hovertemplate='%{x}<br>Wärmebedarf: %{y:,.0f} kWh<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            x=months,
            y=electricity,
            name='Stromverbrauch WP',
            marker_color='blue',
            hovertemplate='%{x}<br>Stromverbrauch: %{y:,.0f} kWh<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=months,
            y=temps,
            name='Außentemperatur',
            mode='lines+markers',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            hovertemplate='%{x}<br>Temperatur: %{y:.0f}°C<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Monat")
    fig.update_yaxes(title_text="Energie [kWh]", secondary_y=False, separators=',.')
    fig.update_yaxes(title_text="Temperatur [°C]", secondary_y=True)
    
    fig.update_layout(
        title="<b>Jahresganglinie: Monatlicher Energiebedarf</b>",
        barmode='group',
        height=550,
        paper_bgcolor='white',
        plot_bgcolor='rgba(240,240,240,0.9)',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_noise_map(noise_data: Dict[str, Any], building_data: Dict[str, Any]) -> go.Figure:
    """
    Schallausbreitungs-Karte (2D Heatmap)
    """
    
    wp_noise = noise_data.get('wp_noise_level_dba', 45)
    distance = noise_data.get('neighbor_distance_m', 5)
    
    # Grid erstellen (20x20m Bereich)
    x = np.linspace(-10, 10, 50)
    y = np.linspace(-10, 10, 50)
    X, Y = np.meshgrid(x, y)
    
    # WP-Position: (0, 0)
    # Schallpegel = wp_noise - 20*log10(distance)
    distances = np.sqrt(X**2 + Y**2)
    distances[distances < 1] = 1  # Mindestabstand
    
    noise_levels = wp_noise - 20 * np.log10(distances)
    noise_levels = np.clip(noise_levels, 25, 65)
    
    fig = go.Figure(data=go.Heatmap(
        x=x,
        y=y,
        z=noise_levels,
        colorscale='RdYlGn_r',
        colorbar=dict(title='Lautstärke<br>dB(A)'),
        hovertemplate='Position: (%{x:.1f}m, %{y:.1f}m)<br>Lautstärke: %{z:.1f} dB(A)<extra></extra>',
        zmin=25,
        zmax=65
    ))
    
    # WP-Position markieren
    fig.add_trace(go.Scatter(
        x=[0],
        y=[0],
        mode='markers+text',
        marker=dict(size=20, color='black', symbol='square'),
        text=['WP'],
        textposition='top center',
        name='Wärmepumpe',
        hovertext=f'WP: {wp_noise} dB(A)'
    ))
    
    # Nachbargrenze markieren (vereinfacht)
    fig.add_shape(
        type='line',
        x0=distance, y0=-10,
        x1=distance, y1=10,
        line=dict(color='red', width=3, dash='dash')
    )
    
    fig.add_annotation(
        x=distance,
        y=8,
        text=f'Nachbargrenze<br>({distance}m)',
        showarrow=False,
        bgcolor='white',
        bordercolor='red'
    )
    
    fig.update_layout(
        title="<b>Schallausbreitungs-Karte</b><br><sub>Lautstärke in Abhängigkeit vom Abstand</sub>",
        xaxis_title="X-Position [m]",
        yaxis_title="Y-Position [m]",
        height=600,
        paper_bgcolor='white',
        yaxis=dict(scaleanchor='x', scaleratio=1)
    )
    
    return fig


def create_lifecycle_chart(co2_data: Dict[str, Any]) -> go.Figure:
    """
    Lebenszyklus-CO2-Bilanz (Sankey oder gestapelte Balken)
    """
    
    wp_data = co2_data.get('wärmepumpe', {})
    old_data = co2_data.get('alte_heizung', {})
    
    categories = ['Herstellung', 'Betrieb (20J)', 'Entsorgung']
    
    wp_values = [
        wp_data.get('herstellung_kg_co2', 0),
        wp_data.get('betrieb_20y_kg_co2', 0),
        wp_data.get('entsorgung_kg_co2', 0)
    ]
    
    old_values = [
        old_data.get('herstellung_kg_co2', 0),
        old_data.get('betrieb_20y_kg_co2', 0),
        old_data.get('entsorgung_kg_co2', 0)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Wärmepumpe',
        x=categories,
        y=wp_values,
        marker_color='green',
        text=[f"{v/1000:.1f} t" for v in wp_values],
        textposition='inside',
        hovertemplate='%{x}<br>WP: %{y:,.0f} kg CO2<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        name=old_data.get('system', 'Alte Heizung'),
        x=categories,
        y=old_values,
        marker_color='red',
        text=[f"{v/1000:.1f} t" for v in old_values],
        textposition='inside',
        hovertemplate='%{x}<br>Alt: %{y:,.0f} kg CO2<extra></extra>'
    ))
    
    fig.update_layout(
        title="<b>Lebenszyklus-CO2-Bilanz (20 Jahre)</b>",
        xaxis_title="Phase",
        yaxis_title="CO2-Emissionen [kg]",
        barmode='group',
        height=550,
        paper_bgcolor='white',
        plot_bgcolor='rgba(240,240,240,0.9)',
        yaxis=dict(separators=',.'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_price_scenario_chart(price_scenarios: Dict[str, Any]) -> go.Figure:
    """
    Preisentwicklungs-Szenarien über 20 Jahre
    """
    
    scenarios = price_scenarios.get('scenarios', {})
    
    fig = go.Figure()
    
    colors = {
        'konservativ': 'green',
        'realistisch': 'orange',
        'pessimistisch': 'red'
    }
    
    for scenario_name, scenario_data in scenarios.items():
        yearly_data = scenario_data.get('yearly_data', [])
        
        if yearly_data:
            years = [d['year'] for d in yearly_data]
            costs_wp = [d['cost_wp'] for d in yearly_data]
            costs_old = [d['cost_old'] for d in yearly_data]
            
            # WP-Kosten
            fig.add_trace(go.Scatter(
                x=years,
                y=costs_wp,
                name=f'WP ({scenario_name.capitalize()})',
                mode='lines',
                line=dict(color=colors.get(scenario_name, 'blue'), width=2),
                hovertemplate='Jahr %{x}<br>Kosten WP: %{y:,.0f}€<extra></extra>'
            ))
            
            # Alte Heizung (gestrichelt)
            fig.add_trace(go.Scatter(
                x=years,
                y=costs_old,
                name=f'Alt ({scenario_name.capitalize()})',
                mode='lines',
                line=dict(color=colors.get(scenario_name, 'blue'), width=2, dash='dash'),
                hovertemplate='Jahr %{x}<br>Kosten Alt: %{y:,.0f}€<extra></extra>'
            ))
    
    fig.update_layout(
        title="<b>Preisentwicklungs-Szenarien (20 Jahre)</b><br><sub>Vergleich: Wärmepumpe vs. Alte Heizung</sub>",
        xaxis_title="Jahr",
        yaxis_title="Jährliche Kosten [€]",
        height=600,
        paper_bgcolor='white',
        plot_bgcolor='rgba(240,240,240,0.9)',
        hovermode='x unified',
        yaxis=dict(separators=',.'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_maintenance_timeline(maintenance_schedule: Dict[str, Any]) -> go.Figure:
    """
    Wartungsplan-Timeline (Gantt-ähnlich)
    """
    
    schedule = maintenance_schedule.get('schedule_20_years', [])
    
    # Daten für Timeline
    timeline_data = []
    
    for year_data in schedule:
        year = year_data['year']
        items = year_data.get('items', [])
        
        for item in items:
            timeline_data.append({
                'Year': year,
                'Item': item['item'],
                'Cost': item['cost_eur'],
                'Description': item['description']
            })
    
    if not timeline_data:
        # Fallback: Leeres Chart
        fig = go.Figure()
        fig.add_annotation(
            text="Keine Wartungsdaten verfügbar",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    df = pd.DataFrame(timeline_data)
    
    # Scatter Plot mit Größe = Kosten
    fig = px.scatter(
        df,
        x='Year',
        y='Item',
        size='Cost',
        color='Cost',
        hover_data=['Description', 'Cost'],
        color_continuous_scale='Reds',
        title='<b>Wartungsplan (20 Jahre)</b><br><sub>Größe = Kosten</sub>'
    )
    
    fig.update_layout(
        height=600,
        paper_bgcolor='white',
        plot_bgcolor='rgba(240,240,240,0.9)',
        xaxis=dict(title='Jahr', tickmode='linear', tick0=1, dtick=1),
        yaxis=dict(title='Wartungsposten'),
        coloraxis_colorbar=dict(title='Kosten [€]')
    )
    
    return fig


# ============================================================================
# FEATURE 7.1: VERGLEICHSRECHNER VISUALISIERUNG
# ============================================================================

def create_comparison_radar_chart(comparison_data: Dict[str, Any]) -> go.Figure:
    """
    Radar Chart für Multi-Kriterien-Vergleich mehrerer Wärmepumpen
    """
    
    results = comparison_data.get('comparison_table', [])
    
    if len(results) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Mindestens 2 Wärmepumpen zum Vergleich erforderlich",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Kriterien für Radar
    criteria = [
        'JAZ',
        'Preis',
        'Betriebskosten',
        'Amortisation',
        'Gesamtkosten',
        'Lautstärke',
        'CO2',
        'Wartung',
        'Kältemittel',
        'Leistung'
    ]
    
    # Mapping zu score-keys
    score_keys = [
        'jaz', 'price', 'annual_cost', 'payback', 'total_cost',
        'noise', 'co2', 'maintenance', 'refrigerant', 'power_reserve'
    ]
    
    fig = go.Figure()
    
    # Farben für bis zu 6 WPs
    colors = [
        'rgb(31, 119, 180)',   # Blau
        'rgb(255, 127, 14)',   # Orange
        'rgb(44, 160, 44)',    # Grün
        'rgb(214, 39, 40)',    # Rot
        'rgb(148, 103, 189)',  # Lila
        'rgb(140, 86, 75)'     # Braun
    ]
    
    for idx, result in enumerate(results[:6]):  # Max. 6
        scores = result.get('scores', {})
        values = [scores.get(key, 0) for key in score_keys]
        
        # Schließe Polygon
        values_closed = values + [values[0]]
        criteria_closed = criteria + [criteria[0]]
        
        medal = result.get('medal', '')
        name = f"{medal} {result['name']}" if medal else result['name']
        
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=criteria_closed,
            fill='toself',
            name=name,
            line=dict(color=colors[idx % len(colors)], width=2),
            opacity=0.6
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20
            )
        ),
        title=dict(
            text='<b>Multi-Kriterien-Vergleich</b><br><sub>0-100 Punkte pro Kriterium</sub>',
            x=0.5,
            xanchor='center'
        ),
        height=600,
        showlegend=True,
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='left',
            x=1.05
        )
    )
    
    return fig


def create_comparison_bar_chart(comparison_data: Dict[str, Any]) -> go.Figure:
    """
    Horizontales Balkendiagramm mit Gesamtpunktzahl
    """
    
    ranking = comparison_data.get('ranking', [])
    
    if not ranking:
        fig = go.Figure()
        fig.add_annotation(
            text="Keine Vergleichsdaten verfügbar",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Daten extrahieren
    names = [f"{r['medal']} {r['name']}" if r['medal'] else r['name'] for r in ranking]
    scores = [r['total_score'] for r in ranking]
    ratings = [r['rating'] for r in ranking]
    
    # Farben nach Rating
    color_map = {
        'TESTSIEGER': 'rgb(255, 215, 0)',     # Gold
        'SEHR GUT': 'rgb(192, 192, 192)',     # Silber
        'GUT': 'rgb(205, 127, 50)',           # Bronze
        'SOLIDE': 'rgb(100, 149, 237)'        # Blau
    }
    
    colors_list = [color_map.get(r, 'rgb(100, 149, 237)') for r in ratings]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=names,
        x=scores,
        orientation='h',
        marker=dict(
            color=colors_list,
            line=dict(color='rgba(0,0,0,0.3)', width=1)
        ),
        text=[f"{s:.1f}" for s in scores],
        textposition='outside',
        textfont=dict(size=14, color='black'),
        hovertemplate='<b>%{y}</b><br>Gesamtpunktzahl: %{x:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>Ranking: Gesamtpunktzahl</b><br><sub>Gewichtete Bewertung aller Kriterien</sub>',
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Gesamtpunktzahl (0-100)',
            range=[0, 105]
        ),
        yaxis=dict(
            title='',
            autorange='reversed'  # Platz 1 oben
        ),
        height=max(400, len(ranking) * 80),
        paper_bgcolor='white',
        plot_bgcolor='rgba(240,240,240,0.9)',
        showlegend=False
    )
    
    return fig


def create_comparison_heatmap(comparison_data: Dict[str, Any]) -> go.Figure:
    """
    Heatmap mit detailliertem Score-Breakdown
    """
    
    results = comparison_data.get('comparison_table', [])
    
    if not results:
        fig = go.Figure()
        fig.add_annotation(
            text="Keine Vergleichsdaten verfügbar",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Kriterien
    criteria_labels = [
        'JAZ<br>(15%)',
        'Preis<br>(10%)',
        'Betriebs-<br>kosten<br>(15%)',
        'Amortisa-<br>tion<br>(10%)',
        'Gesamt-<br>kosten<br>(12%)',
        'Laut-<br>stärke<br>(8%)',
        'CO2<br>(10%)',
        'Wartung<br>(8%)',
        'Kälte-<br>mittel<br>(7%)',
        'Leistung<br>(5%)'
    ]
    
    score_keys = [
        'jaz', 'price', 'annual_cost', 'payback', 'total_cost',
        'noise', 'co2', 'maintenance', 'refrigerant', 'power_reserve'
    ]
    
    # Namen
    names = [f"{r['medal']} {r['name']}" if r['medal'] else r['name'] for r in results]
    
    # Score-Matrix
    score_matrix = []
    for result in results:
        scores = result.get('scores', {})
        row = [scores.get(key, 0) for key in score_keys]
        score_matrix.append(row)
    
    # Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=score_matrix,
        x=criteria_labels,
        y=names,
        colorscale='RdYlGn',  # Rot-Gelb-Grün
        zmin=0,
        zmax=100,
        text=[[f"{val:.0f}" for val in row] for row in score_matrix],
        texttemplate='%{text}',
        textfont=dict(size=12, color='black'),
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f} Punkte<extra></extra>',
        colorbar=dict(
            title='Punkte',
            tickmode='linear',
            tick0=0,
            dtick=20
        )
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>Detaillierter Kriterien-Vergleich</b><br><sub>Gewichtung in % angegeben</sub>',
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title='Kriterium (Gewichtung)', side='top'),
        yaxis=dict(title='', autorange='reversed'),
        height=max(400, len(results) * 60 + 100),
        paper_bgcolor='white'
    )
    
    return fig


def create_comparison_cost_chart(comparison_data: Dict[str, Any]) -> go.Figure:
    """
    Kostenvergleich: Anschaffung vs. 20-Jahres-Gesamtkosten
    """
    
    results = comparison_data.get('comparison_table', [])
    
    if not results:
        fig = go.Figure()
        fig.add_annotation(
            text="Keine Vergleichsdaten verfügbar",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    names = [f"{r['medal']} {r['name']}" if r['medal'] else r['name'] for r in results]
    prices = [r['price'] for r in results]
    total_costs = [r['total_cost_20y_eur'] for r in results]
    
    fig = go.Figure()
    
    # Anschaffungspreis
    fig.add_trace(go.Bar(
        name='Anschaffungspreis',
        x=names,
        y=prices,
        marker=dict(color='rgb(55, 83, 109)'),
        text=[f"{p:,.0f}".replace(",", ".") + ' €' for p in prices],
        textposition='outside',
        textfont=dict(size=11)
    ))
    
    # Gesamtkosten 20 Jahre
    fig.add_trace(go.Bar(
        name='Gesamtkosten 20 Jahre',
        x=names,
        y=total_costs,
        marker=dict(color='rgb(26, 118, 255)'),
        text=[f"{c:,.0f}".replace(",", ".") + ' €' for c in total_costs],
        textposition='outside',
        textfont=dict(size=11)
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>Kostenvergleich</b><br><sub>Anschaffung vs. Gesamtkosten (20 Jahre)</sub>',
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title=''),
        yaxis=dict(title='Kosten [€]', separators=',.'),
        barmode='group',
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='rgba(240,240,240,0.9)',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )
    
    return fig

