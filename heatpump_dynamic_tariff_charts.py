# heatpump_dynamic_tariff_charts.py
"""
Visualisierungen für Dynamischer Stromtarif & Stromcloud
Plotly Charts mit Shadcn UI Design für heatpump_ui.py

Author: GitHub Copilot  
Version: 2.0 - Shadcn UI Design
Date: 2025-01-13
"""

from typing import Any
import plotly.graph_objects as go
import plotly.express as px
from heatpump_dynamic_tariff import get_tariff_zones


# ============================================================================
# SHADCN UI FARB-PALETTE FÜR CHARTS
# ============================================================================

SHADCN_COLORS = {
    # Primäre Farben (Shadcn UI)
    "primary": "#38bdf8",        # Sky Blue
    "success": "#34d399",        # Emerald Green
    "warning": "#fbbf24",        # Amber
    "danger": "#f87171",         # Red
    "info": "#a78bfa",           # Purple
    
    # Erweiterte Palette
    "emerald": "#10b981",
    "teal": "#14b8a6",
    "cyan": "#06b6d4",
    "sky": "#0ea5e9",
    "violet": "#8b5cf6",
    "fuchsia": "#d946ef",
    "pink": "#ec4899",
    "rose": "#f43f5e",
    
    # Tarif-Zonen (Shadcn-optimiert)
    "zone_night": "#34d399",      # Grün (günstig)
    "zone_morning": "#38bdf8",    # Blau (mittel)
    "zone_solar": "#10b981",      # Smaragd (sehr günstig)
    "zone_noon": "#fbbf24",       # Amber (teuer)
    "zone_afternoon": "#fb923c",  # Orange (teurer)
    "zone_peak": "#f87171",       # Rot (am teuersten)
    "zone_evening": "#a78bfa"     # Lila (mittel-teuer)
}


# ============================================================================
# VISUALISIERUNG 1: Stündliche Preiskurve (24h) - SHADCN UI
# ============================================================================

def create_hourly_price_chart(hourly_data: list[dict[str, Any]]) -> go.Figure:
    """
    Plotly Line Chart - 24h Strompreise mit Shadcn UI Design
    
    Args:
        hourly_data: Liste mit hourly_data aus calculate_dynamic_tariff_comparison()
    
    Returns:
        Plotly Figure mit Shadcn UI Styling
    """
    
    # Shadcn UI Zonen-Farben
    zone_colors = {
        "night": SHADCN_COLORS["zone_night"],
        "morning": SHADCN_COLORS["zone_morning"],
        "solar_peak": SHADCN_COLORS["zone_solar"],
        "noon": SHADCN_COLORS["zone_noon"],
        "afternoon": SHADCN_COLORS["zone_afternoon"],
        "evening_peak": SHADCN_COLORS["zone_peak"],
        "evening": SHADCN_COLORS["zone_evening"]
    }
    
    # Daten vorbereiten
    hours = [h["hour"] for h in hourly_data]
    prices = [h["price_dynamic_eur_kwh"] for h in hourly_data]
    zones = [h["zone"] for h in hourly_data]
    static_prices = [h["price_static_eur_kwh"] for h in hourly_data]
    
    # Durchschnittspreis
    avg_dynamic = sum(prices) / len(prices)
    avg_static = static_prices[0] if static_prices else 0.32
    
    fig = go.Figure()
    
    # Dynamischer Preis - Shadcn UI Gradient-Linie
    fig.add_trace(go.Scatter(
        x=hours,
        y=prices,
        mode='lines',
        name='Dynamischer Tarif',
        line=dict(
            color=SHADCN_COLORS["primary"],
            width=3,
            shape='spline'  # Glatte moderne Kurve
        ),
        fill='tozeroy',
        fillcolor=f'rgba(56, 189, 248, 0.15)',  # Shadcn Primary mit Transparenz
        hovertemplate='<b>%{x}:00 Uhr</b><br>Preis: %{y:.3f} €/kWh<extra></extra>'
    ))
    
    # Statischer Preis - Shadcn Danger-Farbe
    fig.add_trace(go.Scatter(
        x=hours,
        y=static_prices,
        mode='lines',
        name='Statischer Tarif',
        line=dict(
            color=SHADCN_COLORS["danger"],
            width=3,
            dash='dash',
            shape='spline'
        ),
        hovertemplate='<b>%{x}:00 Uhr</b><br>Preis: %{y:.3f} €/kWh<extra></extra>'
    ))
    
    # Durchschnittslinien - Shadcn Success-Farbe
    fig.add_hline(
        y=avg_dynamic,
        line_dash="dot",
        line_color=SHADCN_COLORS["success"],
        line_width=2,
        annotation_text=f"Ø Dynamisch: {avg_dynamic:.3f} €",
        annotation_position="right",
        annotation_font_size=11
    )
    
    # Zonen als farbige Hintergründe (Shapes)
    zones_map = get_tariff_zones()
    for zone_key, zone_info in zones_map.items():
        hours = zone_info["hours"]
        if not hours:
            continue
        
        start_hour = min(hours)
        end_hour = max(hours) + 1  # +1 weil vrect end_hour exklusiv ist
        
        fig.add_vrect(
            x0=start_hour,
            x1=end_hour,
            fillcolor=zone_colors.get(zone_key, "#95A5A6"),
            opacity=0.1,
            layer="below",
            line_width=0,
            annotation_text=zone_info["description"],
            annotation_position="top left",
            annotation_font_size=9
        )
    
    # Layout
    fig.update_layout(
        title={
            'text': "Stündliche Strompreise - Dynamisch vs. Statisch",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2C3E50'}
        },
        xaxis_title="Uhrzeit",
        yaxis_title="Strompreis (EUR/kWh)",
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=2,
            ticksuffix=":00",
            gridcolor='#ECF0F1'
        ),
        yaxis=dict(
            tickformat='.3f',
            gridcolor='#ECF0F1'
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


# ============================================================================
# VISUALISIERUNG 2: Jährliche Kostenentwicklung (Kumulative Area)
# ============================================================================

def create_annual_cost_chart(monthly_summaries: dict[int, Any], static_price: float = 0.32) -> go.Figure:
    """
    Plotly Area Chart - Kumulative Kosten über 12 Monate
    
    Args:
        monthly_summaries: Dict aus simulate_annual_price_profile()
        static_price: Statischer Strompreis zum Vergleich
    
    Returns:
        Plotly Figure
    """
    
    months = list(range(1, 13))
    month_names = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", 
                   "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    
    # Kumulative Kosten
    cumulative_dynamic = []
    cumulative_static = []
    total_dynamic = 0
    total_static = 0
    
    for month in months:
        monthly_data = monthly_summaries[month]
        
        # Dynamisch
        total_dynamic += monthly_data["cost_eur"]
        cumulative_dynamic.append(total_dynamic)
        
        # Statisch (zum Vergleich)
        consumption = monthly_data["consumption_kwh"]
        static_cost = consumption * static_price
        total_static += static_cost
        cumulative_static.append(total_static)
    
    fig = go.Figure()
    
    # Statischer Tarif (unten)
    fig.add_trace(go.Scatter(
        x=month_names,
        y=cumulative_static,
        mode='lines',
        name='Statischer Tarif',
        line=dict(color='#E74C3C', width=0),
        fill='tozeroy',
        fillcolor='rgba(231, 76, 60, 0.3)',
        hovertemplate='<b>%{x}</b><br>Kumulativ: %{y:,.0f} €<extra></extra>'
    ))
    
    # Dynamischer Tarif (oben)
    fig.add_trace(go.Scatter(
        x=month_names,
        y=cumulative_dynamic,
        mode='lines',
        name='Dynamischer Tarif',
        line=dict(color='#3498DB', width=0),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.5)',
        hovertemplate='<b>%{x}</b><br>Kumulativ: %{y:,.0f} €<extra></extra>'
    ))
    
    # Einsparung als Differenz (grüne Fläche)
    savings = [cumulative_static[i] - cumulative_dynamic[i] for i in range(12)]
    
    fig.add_trace(go.Scatter(
        x=month_names,
        y=savings,
        mode='lines',
        name='Einsparung',
        line=dict(color='#2ECC71', width=2),
        fill='tozeroy',
        fillcolor='rgba(46, 204, 113, 0.2)',
        hovertemplate='<b>%{x}</b><br>Ersparnis: %{y:,.0f} €<extra></extra>'
    ))
    
    # Layout
    fig.update_layout(
        title={
            'text': "Jährliche Kostenentwicklung - Kumulativ",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2C3E50'}
        },
        xaxis_title="Monat",
        yaxis_title="Kumulative Kosten (EUR)",
        xaxis=dict(gridcolor='#ECF0F1'),
        yaxis=dict(
            tickformat=',',
            gridcolor='#ECF0F1'
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        annotations=[
            dict(
                x=11,
                y=max(cumulative_static),
                text=f"Ersparnis: {savings[-1]:,.0f} €/Jahr",
                showarrow=True,
                arrowhead=2,
                ax=-40,
                ay=-40,
                font=dict(color='#2ECC71', size=14, family='Arial Black')
            )
        ]
    )
    
    return fig


# ============================================================================
# VISUALISIERUNG 3: Stromcloud-Bilanz (Waterfall)
# ============================================================================

def create_stromcloud_waterfall(cloud_result: dict[str, Any]) -> go.Figure:
    """
    Plotly Waterfall Chart - Stromcloud Kosten-Komponenten
    
    Args:
        cloud_result: Output von calculate_stromcloud_economics()
    
    Returns:
        Plotly Figure
    """
    
    without = cloud_result["without_cloud"]
    with_cloud = cloud_result["with_cloud"]
    comparison = cloud_result["comparison"]
    pv_system = cloud_result["pv_system"]
    
    # Wasserfall-Komponenten
    labels = [
        "Ohne Cloud<br>(Netto-Kosten)",
        "Eigenverbrauch<br>verbessert",
        "Cloud-Nutzung<br>(Einsparung)",
        "Cloud-Gebühr<br>(-)",
        "Mit Cloud<br>(Netto-Kosten)"
    ]
    
    # Werte berechnen (vereinfacht für Visualisierung)
    start_value = without["net_cost_eur"]
    
    # Eigenverbrauch-Verbesserung durch Cloud
    direct_consumption = pv_system["direct_consumption_kwh"]
    cloud_consumption = with_cloud["cloud_consumption_kwh"]
    eigenverbrauch_saving = -(cloud_consumption * 0.32)  # Cloud-Strom statt Netzstrom
    
    # Cloud-Gebühr
    cloud_tariff = cloud_result["cloud_tariff"]
    cloud_fee = cloud_tariff["base_fee_annual_eur"] + with_cloud["overage_cost_eur"]
    
    # Einspeise-Unterschied
    feed_in_diff = with_cloud["feed_in_revenue_eur"] - without["feed_in_revenue_eur"]
    
    end_value = with_cloud["net_cost_eur"]
    
    values = [
        start_value,
        eigenverbrauch_saving,
        feed_in_diff,
        cloud_fee,
        end_value
    ]
    
    # Measure types (absolute, relative, total)
    measures = ["absolute", "relative", "relative", "relative", "total"]
    
    # Farben
    colors = [
        "#E74C3C",  # Rot (Start - ohne Cloud)
        "#2ECC71",  # Grün (Einsparung Eigenverbrauch)
        "#1ABC9C",  # Türkis (Cloud-Freimenge)
        "#E67E22",  # Orange (Gebühr)
        "#3498DB"   # Blau (Ende - mit Cloud)
    ]
    
    fig = go.Figure(go.Waterfall(
        name="Stromcloud",
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        text=[f"{v:,.0f} €" for v in values],
        textposition="outside",
        connector={"line": {"color": "#7F8C8D"}},
        decreasing={"marker": {"color": "#2ECC71"}},  # Grün für Einsparungen
        increasing={"marker": {"color": "#E74C3C"}},  # Rot für Kosten
        totals={"marker": {"color": "#3498DB"}}       # Blau für Totals
    ))
    
    # Layout
    fig.update_layout(
        title={
            'text': "☁️ Stromcloud Kosten-Bilanz (Waterfall)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2C3E50'}
        },
        yaxis_title="Kosten (EUR/Jahr)",
        yaxis=dict(
            tickformat=',',
            gridcolor='#ECF0F1'
        ),
        xaxis=dict(gridcolor='#ECF0F1'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        showlegend=False
    )
    
    # Annotations für Erklärungen
    fig.add_annotation(
        x=4,
        y=end_value,
        text=f"<b>Ersparnis: {start_value - end_value:,.0f} €/Jahr</b>",
        showarrow=True,
        arrowhead=2,
        ax=-50,
        ay=-50,
        font=dict(color='#2ECC71', size=14, family='Arial Black'),
        bgcolor='#E8F8F5',
        bordercolor='#2ECC71',
        borderwidth=2
    )
    
    return fig


# ============================================================================
# VISUALISIERUNG 4: Load-Shifting Heatmap (7x24)
# ============================================================================

def create_load_shifting_heatmap(hourly_data: list[dict[str, Any]]) -> go.Figure:
    """
    Plotly Heatmap - 7 Tage × 24 Stunden Load-Shifting Potenzial
    
    Args:
        hourly_data: Liste mit Stundendaten (aus simulate_annual_price_profile)
    
    Returns:
        Plotly Figure
    """
    
    # Erste Woche extrahieren (168 Stunden)
    week_data = hourly_data[:168]
    
    # 2D Matrix: 7 Tage × 24 Stunden
    days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    hours = list(range(24))
    
    # Matrix mit Preisen
    price_matrix = []
    for day in range(7):
        day_prices = []
        for hour in range(24):
            idx = day * 24 + hour
            if idx < len(week_data):
                price = week_data[idx]["price_dynamic_eur_kwh"]
            else:
                price = 0.12  # Fallback
            day_prices.append(price)
        price_matrix.append(day_prices)
    
    # Beste Load-Shifting Zeiten markieren (grün = günstig)
    # Wir nehmen die günstigsten 6 Stunden pro Tag
    best_hours_per_day = []
    for day_prices in price_matrix:
        sorted_hours = sorted(enumerate(day_prices), key=lambda x: x[1])
        best_6 = [h for h, _ in sorted_hours[:6]]
        best_hours_per_day.append(best_6)
    
    fig = go.Figure(data=go.Heatmap(
        z=price_matrix,
        x=[f"{h:02d}:00" for h in hours],
        y=days,
        colorscale=[
            [0.0, "#2ECC71"],   # Grün (sehr günstig)
            [0.3, "#1ABC9C"],   # Türkis (günstig)
            [0.5, "#F39C12"],   # Orange (mittel)
            [0.7, "#E67E22"],   # Dunkelorange (teuer)
            [1.0, "#E74C3C"]    # Rot (sehr teuer)
        ],
        colorbar=dict(
            title="EUR/kWh",
            tickformat=".3f"
        ),
        hovertemplate='<b>%{y}</b><br>%{x} Uhr<br>Preis: %{z:.3f} €/kWh<extra></extra>'
    ))
    
    # Layout
    fig.update_layout(
        title={
            'text': "🔥 Load-Shifting Heatmap (Woche)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2C3E50'}
        },
        xaxis_title="Uhrzeit",
        yaxis_title="Wochentag",
        xaxis=dict(
            side='bottom',
            tickangle=0
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500
    )
    
    # Annotations für beste Zeiten (optional - wird zu voll bei 7×6=42 Punkten)
    # Daher nur Zusammenfassung als Text
    fig.add_annotation(
        text="<b>Grün = Günstigste Zeiten</b><br>Optimal für WP, E-Auto, Waschmaschine",
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.15,
        showarrow=False,
        font=dict(size=12, color='#2C3E50'),
        bgcolor='#E8F8F5',
        bordercolor='#2ECC71',
        borderwidth=1
    )
    
    return fig
