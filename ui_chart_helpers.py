"""
ui_chart_helpers.py
Utility-Funktionen für moderne Chart-Darstellung mit Plotly
"""


import plotly.express as px
import plotly.graph_objects as go

# Moderne Farbpalette (Türkis/Cyan Akzente)
CHART_COLORS = [
    "#00E5FF",
    "#00BCD4",
    "#38E1B0",
    "#8A7FFF",
    "#50C4FF",
    "#7EE0FF"]
ACCENT_COLOR = "#00E5FF"
ACCENT_COLOR_2 = "#00BCD4"


def get_modern_plotly_layout(
    title: str | None = None,
    show_legend: bool = True,
    height: int | None = None
) -> dict:
    """
    Gibt ein modernes Plotly-Layout zurück, das zum Dark Theme passt

    Args:
        title: Chart-Titel (optional)
        show_legend: Legende anzeigen
        height: Chart-Höhe in Pixeln

    Returns:
        Dict mit Layout-Optionen
    """
    layout = {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": "Nunito, sans-serif",
            "color": "#E6F7FF",
            "size": 12
        },
        "title": {
            "text": title or "",
            "font": {"size": 18, "color": "#E6F7FF", "family": "Nunito"},
            "x": 0.5,
            "xanchor": "center"
        },
        "showlegend": show_legend,
        "legend": {
            "bgcolor": "rgba(16,22,30,.6)",
            "bordercolor": "rgba(255,255,255,.08)",
            "borderwidth": 1,
            "font": {"color": "#E6F7FF"}
        },
        "margin": {"l": 40, "r": 40, "t": 50, "b": 40},
        "xaxis": {
            "gridcolor": "rgba(255,255,255,.08)",
            "zerolinecolor": "rgba(255,255,255,.12)",
            "color": "#E6F7FF"
        },
        "yaxis": {
            "gridcolor": "rgba(255,255,255,.08)",
            "zerolinecolor": "rgba(255,255,255,.12)",
            "color": "#E6F7FF"
        }
    }

    if height:
        layout["height"] = height

    return layout


def apply_modern_theme_to_figure(fig, title: str | None = None) -> go.Figure:
    """
    Wendet das moderne Dark Theme auf ein Plotly Figure an

    Args:
        fig: Plotly Figure Objekt
        title: Optionaler Titel

    Returns:
        Modifiziertes Figure Objekt
    """
    layout = get_modern_plotly_layout(title=title)
    fig.update_layout(**layout)

    # Grid-Linien sanfter machen
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,.08)"
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,.08)"
    )

    return fig


def create_modern_line_chart(
    data,
    x: str,
    y: str,
    title: str | None = None,
    color: str | None = None,
    markers: bool = True
) -> go.Figure:
    """
    Erstellt ein modernes Liniendiagramm

    Args:
        data: DataFrame oder dict
        x: Spaltenname für X-Achse
        y: Spaltenname für Y-Achse
        title: Chart-Titel
        color: Spaltenname für Farbgruppierung (optional)
        markers: Marker anzeigen

    Returns:
        Plotly Figure
    """
    fig = px.line(
        data,
        x=x,
        y=y,
        color=color,
        markers=markers,
        color_discrete_sequence=CHART_COLORS
    )

    # Linie dicker und mit Glow-Effekt
    fig.update_traces(
        line=dict(width=3),
        hovertemplate=f"{x}: %{{x}}<br>{y}: %{{y}}<extra></extra>"
    )

    return apply_modern_theme_to_figure(fig, title)


def create_modern_bar_chart(
    data,
    x: str,
    y: str,
    title: str | None = None,
    color: str | None = None,
    orientation: str = "v"
) -> go.Figure:
    """
    Erstellt ein modernes Balkendiagramm

    Args:
        data: DataFrame oder dict
        x: Spaltenname für X-Achse
        y: Spaltenname für Y-Achse
        title: Chart-Titel
        color: Spaltenname für Farbgruppierung (optional)
        orientation: "v" für vertikal, "h" für horizontal

    Returns:
        Plotly Figure
    """
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        orientation=orientation,
        color_discrete_sequence=CHART_COLORS
    )

    # Abgerundete Ecken simulieren durch Marker
    fig.update_traces(
        marker=dict(
            line=dict(width=0),
            opacity=0.9
        )
    )

    return apply_modern_theme_to_figure(fig, title)


def create_modern_pie_chart(
    data,
    names: str,
    values: str,
    title: str | None = None,
    hole: float = 0.0
) -> go.Figure:
    """
    Erstellt ein modernes Kreisdiagramm (oder Donut wenn hole > 0)

    Args:
        data: DataFrame oder dict
        names: Spaltenname für Labels
        values: Spaltenname für Werte
        title: Chart-Titel
        hole: Größe des Lochs in der Mitte (0 = Pie, >0 = Donut)

    Returns:
        Plotly Figure
    """
    fig = px.pie(
        data,
        names=names,
        values=values,
        hole=hole,
        color_discrete_sequence=CHART_COLORS
    )

    # Sanftere Hover-Effekte
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="%{label}<br>%{value}<br>%{percent}<extra></extra>"
    )

    return apply_modern_theme_to_figure(fig, title)


def create_modern_scatter_chart(
    data,
    x: str,
    y: str,
    title: str | None = None,
    size: str | None = None,
    color: str | None = None
) -> go.Figure:
    """
    Erstellt ein modernes Streudiagramm

    Args:
        data: DataFrame oder dict
        x: Spaltenname für X-Achse
        y: Spaltenname für Y-Achse
        title: Chart-Titel
        size: Spaltenname für Punkt-Größe (optional)
        color: Spaltenname für Farbgruppierung (optional)

    Returns:
        Plotly Figure
    """
    fig = px.scatter(
        data,
        x=x,
        y=y,
        size=size,
        color=color,
        color_discrete_sequence=CHART_COLORS
    )

    # Glow-Effekt für Punkte
    fig.update_traces(
        marker=dict(
            line=dict(width=0),
            opacity=0.8
        )
    )

    return apply_modern_theme_to_figure(fig, title)


def create_modern_area_chart(
    data,
    x: str,
    y: str,
    title: str | None = None,
    color: str | None = None
) -> go.Figure:
    """
    Erstellt ein modernes Flächendiagramm

    Args:
        data: DataFrame oder dict
        x: Spaltenname für X-Achse
        y: Spaltenname für Y-Achse
        title: Chart-Titel
        color: Spaltenname für Farbgruppierung (optional)

    Returns:
        Plotly Figure
    """
    fig = px.area(
        data,
        x=x,
        y=y,
        color=color,
        color_discrete_sequence=CHART_COLORS
    )

    # Transparentere Füllung
    fig.update_traces(
        fillcolor="rgba(0,229,255,0.15)",
        line=dict(color=ACCENT_COLOR, width=2)
    )

    return apply_modern_theme_to_figure(fig, title)


def create_waterfall_chart(
    data,
    x: str,
    y: str,
    title: str | None = None,
    text: str | None = None
) -> go.Figure:
    """
    Erstellt ein modernes Wasserfalldiagramm

    Args:
        data: DataFrame oder dict
        x: Spaltenname für X-Achse (Kategorien)
        y: Spaltenname für Y-Achse (Werte)
        title: Chart-Titel
        text: Spaltenname für Beschriftungen (optional)

    Returns:
        Plotly Figure
    """
    fig = go.Figure(go.Waterfall(
        x=data[x],
        y=data[y],
        text=data[text] if text else None,
        textposition="outside",
        increasing={"marker": {"color": CHART_COLORS[2]}},
        decreasing={"marker": {"color": CHART_COLORS[3]}},
        totals={"marker": {"color": ACCENT_COLOR}}
    ))

    return apply_modern_theme_to_figure(fig, title)


def add_gradient_background(fig) -> go.Figure:
    """
    Fügt einem Chart einen Gradienten-Hintergrund hinzu

    Args:
        fig: Plotly Figure Objekt

    Returns:
        Modifiziertes Figure Objekt
    """
    fig.add_layout_image(
        dict(
            source="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxyYWRpYWxHcmFkaWVudCBpZD0iZyI+PHN0b3Agb2Zmc2V0PSIwJSIgc3R5bGU9InN0b3AtY29sb3I6cmdiYSgwLDIyOSwyNTUsMC4wNSkiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0eWxlPSJzdG9wLWNvbG9yOnJnYmEoMCwwLDAsMCkiLz48L3JhZGlhbEdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2cpIi8+PC9zdmc+",
            xref="paper",
            yref="paper",
            x=0,
            y=1,
            sizex=1,
            sizey=1,
            sizing="stretch",
            opacity=0.3,
            layer="below"
        )
    )
    return fig
