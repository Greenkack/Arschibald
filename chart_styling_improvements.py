"""
chart_styling_improvements.py

Modul für verbesserte Diagramm-Darstellung gemäß Task 4.1-4.3
Bietet konsistente Styling-Funktionen für alle Chart-Module.

Autor: Kiro AI
Datum: 2025-10-10
Version: 1.0
"""

import io
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# ============================================================================
# STYLING CONSTANTS
# ============================================================================

# Schriftgrößen (Task 4.1)
FONT_SIZE_TITLE = 14
FONT_SIZE_AXIS_LABEL = 12
FONT_SIZE_LEGEND = 10
FONT_SIZE_TICK_LABEL = 10
FONT_SIZE_DATA_LABEL = 9
FONT_SIZE_PIE_PERCENT = 10

# Linien und Balken (Task 4.1)
BAR_WIDTH = 0.6
LINE_WIDTH = 2.5
MARKER_SIZE = 100
DONUT_WIDTH = 0.4
EDGE_LINE_WIDTH = 2

# Auflösung und Dimensionen (Task 4.3)
DPI = 300
FIGURE_WIDTH_CM = 14
FIGURE_HEIGHT_CM = 10
CM_TO_INCH = 0.393701

# Farben (Task 4.2)
GRID_ALPHA = 0.3
PROFESSIONAL_COLORS = [
    '#1f77b4',  # Blau
    '#ff7f0e',  # Orange
    '#2ca02c',  # Grün
    '#d62728',  # Rot
    '#9467bd',  # Lila
    '#8c564b',  # Braun
    '#e377c2',  # Pink
    '#7f7f7f',  # Grau
    '#bcbd22',  # Gelb-Grün
    '#17becf'   # Cyan
]

# ============================================================================
# MATPLOTLIB STYLING FUNCTIONS
# ============================================================================


def apply_improved_matplotlib_style(
    fig: matplotlib.figure.Figure,
    ax: matplotlib.axes.Axes,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    show_grid: bool = True,
    show_legend: bool = True
) -> None:
    """
    Wendet verbesserte Styling-Einstellungen auf Matplotlib-Diagramme an.

    Args:
        fig: Matplotlib Figure-Objekt
        ax: Matplotlib Axes-Objekt
        title: Diagramm-Titel
        xlabel: X-Achsen-Beschriftung
        ylabel: Y-Achsen-Beschriftung
        show_grid: Gitternetz anzeigen
        show_legend: Legende anzeigen
    """
    # Transparente Hintergründe (Task 1)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    # Titel (Task 4.1)
    if title:
        ax.set_title(
            title,
            fontsize=FONT_SIZE_TITLE,
            fontweight='bold',
            pad=20)

    # Achsenbeschriftungen (Task 4.1)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=FONT_SIZE_AXIS_LABEL, fontweight='bold')
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=FONT_SIZE_AXIS_LABEL, fontweight='bold')

    # Tick-Labels (Task 4.1)
    ax.tick_params(axis='both', which='major', labelsize=FONT_SIZE_TICK_LABEL)

    # Gitternetz (Task 4.2)
    if show_grid:
        ax.grid(True, alpha=GRID_ALPHA, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)

    # Legende (Task 4.1)
    if show_legend and ax.get_legend_handles_labels()[0]:
        legend = ax.legend(fontsize=FONT_SIZE_LEGEND, framealpha=0, loc='best')
        if legend:
            legend.get_frame().set_facecolor('none')
            legend.get_frame().set_edgecolor('none')


def create_improved_bar_chart(
    ax: matplotlib.axes.Axes,
    x_data: list,
    y_data: list,
    labels: list[str] | None = None,
    colors: list[str] | None = None,
    show_values: bool = True
) -> None:
    """
    Erstellt ein verbessertes Balkendiagramm.

    Args:
        ax: Matplotlib Axes-Objekt
        x_data: X-Achsen-Daten
        y_data: Y-Achsen-Daten
        labels: Beschriftungen für Balken
        colors: Farben für Balken
        show_values: Werte über Balken anzeigen
    """
    if colors is None:
        colors = PROFESSIONAL_COLORS[:len(y_data)]

    # Balken mit verbesserter Breite (Task 4.1)
    bars = ax.bar(
        x_data,
        y_data,
        width=BAR_WIDTH,
        color=colors,
        alpha=0.9,
        edgecolor='white',
        linewidth=1.5,
        label=labels
    )

    # Werte über Balken (Task 4.2)
    if show_values:
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f'{height:,.0f}',
                ha='center',
                va='bottom',
                fontsize=FONT_SIZE_DATA_LABEL,
                fontweight='bold'
            )


def create_improved_line_chart(
    ax: matplotlib.axes.Axes,
    x_data: list,
    y_data: list,
    label: str | None = None,
    color: str | None = None,
    show_markers: bool = True
) -> None:
    """
    Erstellt ein verbessertes Liniendiagramm.

    Args:
        ax: Matplotlib Axes-Objekt
        x_data: X-Achsen-Daten
        y_data: Y-Achsen-Daten
        label: Beschriftung für Linie
        color: Farbe für Linie
        show_markers: Marker anzeigen
    """
    if color is None:
        color = PROFESSIONAL_COLORS[0]

    # Linie mit verbesserter Breite (Task 4.1)
    if show_markers:
        ax.plot(
            x_data,
            y_data,
            linewidth=LINE_WIDTH,
            color=color,
            marker='o',
            markersize=8,
            label=label,
            alpha=0.9
        )
    else:
        ax.plot(
            x_data,
            y_data,
            linewidth=LINE_WIDTH,
            color=color,
            label=label,
            alpha=0.9
        )


def create_improved_donut_chart(
    ax: matplotlib.axes.Axes,
    values: list,
    labels: list[str],
    colors: list[str] | None = None,
    explode: list[float] | None = None
) -> None:
    """
    Erstellt ein verbessertes Donut-Diagramm.

    Args:
        ax: Matplotlib Axes-Objekt
        values: Werte für Segmente
        labels: Beschriftungen für Segmente
        colors: Farben für Segmente
        explode: Explosion für Segmente
    """
    if colors is None:
        colors = PROFESSIONAL_COLORS[:len(values)]

    # Donut mit verbesserter Breite (Task 4.1)
    wedgeprops = {
        'width': DONUT_WIDTH,
        'edgecolor': 'white',
        'linewidth': EDGE_LINE_WIDTH
    }

    # Pie Chart mit Prozentsätzen (Task 4.2)
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        explode=explode,
        wedgeprops=wedgeprops,
        textprops={'fontsize': FONT_SIZE_LEGEND}
    )

    # Prozentsätze formatieren (Task 4.2)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(FONT_SIZE_PIE_PERCENT)
        autotext.set_fontweight('bold')


def create_improved_scatter_plot(
    ax: matplotlib.axes.Axes,
    x_data: list,
    y_data: list,
    label: str | None = None,
    color: str | None = None,
    size_data: list | None = None
) -> None:
    """
    Erstellt ein verbessertes Streudiagramm.

    Args:
        ax: Matplotlib Axes-Objekt
        x_data: X-Achsen-Daten
        y_data: Y-Achsen-Daten
        label: Beschriftung
        color: Farbe
        size_data: Größen für Marker
    """
    if color is None:
        color = PROFESSIONAL_COLORS[0]

    if size_data is None:
        size_data = [MARKER_SIZE] * len(x_data)

    # Scatter mit verbesserter Marker-Größe (Task 4.1)
    ax.scatter(
        x_data,
        y_data,
        s=size_data,
        c=color,
        alpha=0.7,
        edgecolors='white',
        linewidth=1.5,
        label=label
    )


def save_matplotlib_chart_to_bytes(
    fig: matplotlib.figure.Figure
) -> bytes:
    """
    Speichert Matplotlib-Diagramm als PNG-Bytes mit hoher Auflösung.

    Args:
        fig: Matplotlib Figure-Objekt

    Returns:
        PNG-Bytes
    """
    buf = io.BytesIO()
    plt.savefig(
        buf,
        format='png',
        dpi=DPI,  # Task 4.3
        bbox_inches='tight',
        facecolor='none',
        edgecolor='none',
        transparent=True
    )
    buf.seek(0)
    chart_bytes = buf.getvalue()
    plt.close(fig)
    return chart_bytes


# ============================================================================
# PLOTLY STYLING FUNCTIONS
# ============================================================================

def apply_improved_plotly_style(
    fig: go.Figure,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    show_grid: bool = True,
    show_legend: bool = True
) -> None:
    """
    Wendet verbesserte Styling-Einstellungen auf Plotly-Diagramme an.

    Args:
        fig: Plotly Figure-Objekt
        title: Diagramm-Titel
        xlabel: X-Achsen-Beschriftung
        ylabel: Y-Achsen-Beschriftung
        show_grid: Gitternetz anzeigen
        show_legend: Legende anzeigen
    """
    # Layout mit transparenten Hintergründen (Task 1)
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=FONT_SIZE_TITLE, family='Arial', color='black'),
            x=0.5,
            xanchor='center'
        ) if title else None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=FONT_SIZE_TICK_LABEL, family='Arial', color='black'),
        xaxis=dict(
            title=dict(text=xlabel, font=dict(size=FONT_SIZE_AXIS_LABEL)) if xlabel else None,
            gridcolor=f'rgba(128,128,128,{GRID_ALPHA})' if show_grid else 'rgba(0,0,0,0)',
            showgrid=show_grid,
            tickfont=dict(size=FONT_SIZE_TICK_LABEL)
        ),
        yaxis=dict(
            title=dict(text=ylabel, font=dict(size=FONT_SIZE_AXIS_LABEL)) if ylabel else None,
            gridcolor=f'rgba(128,128,128,{GRID_ALPHA})' if show_grid else 'rgba(0,0,0,0)',
            showgrid=show_grid,
            tickfont=dict(size=FONT_SIZE_TICK_LABEL)
        ),
        showlegend=show_legend,
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)',
            font=dict(size=FONT_SIZE_LEGEND)
        ),
        margin=dict(l=70, r=30, t=80, b=60),
        height=500
    )


def create_improved_plotly_bar_chart(
    fig: go.Figure,
    x_data: list,
    y_data: list,
    name: str | None = None,
    color: str | None = None,
    show_values: bool = True
) -> None:
    """
    Fügt verbesserte Balken zu Plotly-Diagramm hinzu.

    Args:
        fig: Plotly Figure-Objekt
        x_data: X-Achsen-Daten
        y_data: Y-Achsen-Daten
        name: Name für Trace
        color: Farbe für Balken
        show_values: Werte über Balken anzeigen
    """
    if color is None:
        color = PROFESSIONAL_COLORS[0]

    fig.add_trace(go.Bar(
        x=x_data,
        y=y_data,
        name=name,
        marker=dict(
            color=color,
            line=dict(color='white', width=1.5)
        ),
        text=[f'{val:,.0f}' for val in y_data] if show_values else None,
        textposition='outside' if show_values else None,
        textfont=dict(size=FONT_SIZE_DATA_LABEL, color='black') if show_values else None,
        hovertemplate='<b>%{x}</b><br>Wert: %{y:,.0f}<extra></extra>'
    ))


def create_improved_plotly_line_chart(
    fig: go.Figure,
    x_data: list,
    y_data: list,
    name: str | None = None,
    color: str | None = None,
    show_markers: bool = True
) -> None:
    """
    Fügt verbesserte Linie zu Plotly-Diagramm hinzu.

    Args:
        fig: Plotly Figure-Objekt
        x_data: X-Achsen-Daten
        y_data: Y-Achsen-Daten
        name: Name für Trace
        color: Farbe für Linie
        show_markers: Marker anzeigen
    """
    if color is None:
        color = PROFESSIONAL_COLORS[0]

    mode = 'lines+markers' if show_markers else 'lines'

    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode=mode,
        name=name,
        # Plotly verwendet dünnere Linien
        line=dict(color=color, width=LINE_WIDTH / 1.5),
        marker=dict(size=8, color=color) if show_markers else None,
        hovertemplate='<b>%{x}</b><br>Wert: %{y:,.0f}<extra></extra>'
    ))


def save_plotly_chart_to_bytes(
    fig: go.Figure
) -> bytes:
    """
    Speichert Plotly-Diagramm als PNG-Bytes mit hoher Auflösung.

    Args:
        fig: Plotly Figure-Objekt

    Returns:
        PNG-Bytes
    """
    import plotly.io as pio

    # Hohe Auflösung (Task 4.3)
    # Berechne Pixel-Größe: cm -> inch -> pixel
    width_px = int(FIGURE_WIDTH_CM * CM_TO_INCH * DPI)
    height_px = int(FIGURE_HEIGHT_CM * CM_TO_INCH * DPI)

    chart_bytes = pio.to_image(
        fig,
        format='png',
        width=width_px,
        height=height_px,
        scale=1  # Scale ist bereits in width/height eingerechnet
    )

    return chart_bytes


# ============================================================================
# CHART DESCRIPTION GENERATION (Task 4.4)
# ============================================================================

def generate_chart_description(
    chart_type: str,
    data: dict[str, Any],
    purpose: str = "",
    key_insights: list[str] | None = None
) -> str:
    """
    Generiert eine strukturierte Beschreibung für ein Diagramm.

    Args:
        chart_type: Typ des Diagramms (z.B. "Balkendiagramm", "Liniendiagramm")
        data: Daten des Diagramms mit numerischen Werten
        purpose: Zweck des Diagramms
        key_insights: Liste der Haupterkenntnisse

    Returns:
        Formatierte Beschreibung als String
    """
    description_parts = []

    # Diagrammtyp
    description_parts.append(f"Diagrammtyp: {chart_type}")

    # Zweck
    if purpose:
        description_parts.append(f"\nZweck: {purpose}")

    # Haupterkenntnisse
    if key_insights:
        description_parts.append("\n\nHaupterkenntnisse:")
        for i, insight in enumerate(key_insights, 1):
            description_parts.append(f"\n{i}. {insight}")

    # Numerische Werte (strukturiert)
    if 'values' in data and isinstance(data['values'], (list, tuple)):
        description_parts.append("\n\nWerte:")
        labels = data.get('labels',
                          [f"Wert {i + 1}" for i in range(len(data['values']))])
        for label, value in zip(labels, data['values']):
            if isinstance(value, (int, float)):
                description_parts.append(f"\n• {label}: {value:,.2f}")

    return "".join(description_parts)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_optimal_figure_size() -> tuple[float, float]:
    """
    Gibt die optimale Diagrammgröße in Zoll zurück (Task 4.3).

    Returns:
        Tuple (Breite, Höhe) in Zoll
    """
    width_inch = FIGURE_WIDTH_CM * CM_TO_INCH
    height_inch = FIGURE_HEIGHT_CM * CM_TO_INCH
    return (width_inch, height_inch)


def get_professional_color_palette(n_colors: int = 10) -> list[str]:
    """
    Gibt eine professionelle Farbpalette zurück.

    Args:
        n_colors: Anzahl der benötigten Farben

    Returns:
        Liste von Farbcodes
    """
    if n_colors <= len(PROFESSIONAL_COLORS):
        return PROFESSIONAL_COLORS[:n_colors]
    # Wiederhole Farben wenn mehr benötigt werden
    return (PROFESSIONAL_COLORS *
            ((n_colors // len(PROFESSIONAL_COLORS)) + 1))[:n_colors]
