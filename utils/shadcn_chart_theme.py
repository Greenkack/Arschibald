"""
shadcn/ui Chart Theme

Styling-System für Plotly-Charts im shadcn/ui-Design.
Wendet konsistente Farben, Schriftarten und Layouts auf Charts an.
"""

from typing import Optional, List, Dict, Any
import plotly.graph_objects as go
from theming.theme_manager import ThemeManager


def apply_chart_theme(
    fig: go.Figure,
    theme_manager: Optional[ThemeManager] = None,
    enable_spline: bool = True,
    enable_gradients: bool = True,
    dark_mode: Optional[bool] = None
) -> go.Figure:
    """
    Wendet shadcn/ui-Theme auf Plotly-Chart an
    
    Args:
        fig: Plotly Figure Objekt
        theme_manager: ThemeManager-Instanz (optional, verwendet Session State wenn None)
        enable_spline: Aktiviert glatte Spline-Kurven für Linien-Charts
        enable_gradients: Aktiviert Gradient-Fills für Area-Charts
        dark_mode: Erzwingt Dark Mode (None = automatisch aus Theme)
    
    Returns:
        Modifiziertes Figure Objekt mit shadcn/ui-Styling
    
    Example:
        >>> from theming import ThemeManager
        >>> import plotly.graph_objects as go
        >>> 
        >>> theme_manager = ThemeManager()
        >>> theme_manager.set_theme('shadcn-default')
        >>> 
        >>> fig = go.Figure(data=[go.Scatter(x=[1,2,3], y=[4,5,6])])
        >>> fig = apply_chart_theme(fig, theme_manager)
        >>> fig.show()
    """
    # Hole ThemeManager aus Session State wenn nicht übergeben
    if theme_manager is None:
        import streamlit as st
        theme_manager = st.session_state.get('theme_manager')
        if theme_manager is None:
            # Fallback: Erstelle temporären ThemeManager
            theme_manager = ThemeManager()
            theme_manager.set_theme('shadcn-default')
    
    if not theme_manager.current_theme:
        raise ValueError("Kein Theme aktiv im ThemeManager")
    
    theme = theme_manager.current_theme
    
    # Erkenne Dark Mode automatisch wenn nicht explizit gesetzt
    if dark_mode is None:
        dark_mode = _is_dark_mode(theme)
    
    # Hole Theme-Farben
    colors = _get_chart_colors(theme)
    
    # Wende Layout-Styling an
    fig.update_layout(
        # Schriftarten
        font=dict(
            family=theme.typography.font_family,
            size=14,
            color=theme.colors.foreground
        ),
        
        # Hintergrund
        plot_bgcolor=theme.colors.background,
        paper_bgcolor=theme.colors.background,
        
        # Responsive Margins
        margin=dict(l=70, r=40, t=60, b=60),
        
        # Hover-Styling
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=theme.colors.muted,
            font_size=13,
            font_family=theme.typography.font_family,
            font_color=theme.colors.muted_foreground
        ),
        
        # Grid-Styling
        xaxis=dict(
            gridcolor=theme.colors.border,
            linecolor=theme.colors.border,
            zerolinecolor=theme.colors.border,
            tickfont=dict(color=theme.colors.muted_foreground)
        ),
        yaxis=dict(
            gridcolor=theme.colors.border,
            linecolor=theme.colors.border,
            zerolinecolor=theme.colors.border,
            tickfont=dict(color=theme.colors.muted_foreground)
        ),
        
        # Legend-Styling
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor=theme.colors.border,
            borderwidth=1,
            font=dict(color=theme.colors.foreground)
        ),
        
        # Title-Styling
        title=dict(
            font=dict(
                size=18,
                color=theme.colors.foreground,
                family=theme.typography.font_family
            )
        )
    )
    
    # Wende Trace-Styling an
    for i, trace in enumerate(fig.data):
        color = colors[i % len(colors)]
        
        # Scatter/Line Charts
        if trace.type == 'scatter':
            updates = {
                'line': dict(
                    color=color,
                    width=3,
                    shape='spline' if enable_spline else 'linear'
                ),
                'marker': dict(
                    color=color,
                    size=8,
                    line=dict(width=2, color=theme.colors.background)
                )
            }
            
            # Gradient-Fill für Area-Charts
            if trace.fill and enable_gradients:
                updates['fillcolor'] = _create_gradient_color(color, opacity=0.2)
            elif trace.fill:
                updates['fillcolor'] = _hex_to_rgba(color, 0.2)
            
            trace.update(updates)
        
        # Bar Charts
        elif trace.type == 'bar':
            trace.update(
                marker=dict(
                    color=color,
                    line=dict(width=0)
                )
            )
        
        # Pie Charts
        elif trace.type == 'pie':
            trace.update(
                marker=dict(
                    colors=colors,
                    line=dict(color=theme.colors.background, width=2)
                ),
                textfont=dict(color=theme.colors.background)
            )
        
        # Heatmaps
        elif trace.type == 'heatmap':
            trace.update(
                colorscale=_create_colorscale(colors[:3])
            )
    
    return fig


def apply_responsive_layout(fig: go.Figure, mobile: bool = False) -> go.Figure:
    """
    Passt Chart-Layout für verschiedene Bildschirmgrößen an
    
    Args:
        fig: Plotly Figure Objekt
        mobile: True für mobile Optimierung
    
    Returns:
        Modifiziertes Figure mit responsivem Layout
    """
    if mobile:
        fig.update_layout(
            margin=dict(l=40, r=20, t=40, b=40),
            font=dict(size=12),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='center',
                x=0.5
            )
        )
    else:
        fig.update_layout(
            margin=dict(l=70, r=40, t=60, b=60),
            font=dict(size=14)
        )
    
    return fig


def create_themed_figure(
    theme_manager: Optional[ThemeManager] = None,
    title: Optional[str] = None,
    **kwargs
) -> go.Figure:
    """
    Erstellt eine neue Figure mit voreingestelltem shadcn/ui-Theme
    
    Args:
        theme_manager: ThemeManager-Instanz
        title: Chart-Titel
        **kwargs: Zusätzliche Layout-Parameter
    
    Returns:
        Neue Figure mit shadcn/ui-Styling
    
    Example:
        >>> fig = create_themed_figure(theme_manager, title="Mein Chart")
        >>> fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6]))
        >>> fig.show()
    """
    fig = go.Figure()
    
    if title:
        fig.update_layout(title=title)
    
    if kwargs:
        fig.update_layout(**kwargs)
    
    return apply_chart_theme(fig, theme_manager)


def get_chart_colors(theme_manager: Optional[ThemeManager] = None) -> List[str]:
    """
    Gibt Liste der Chart-Farben aus dem aktuellen Theme zurück
    
    Args:
        theme_manager: ThemeManager-Instanz
    
    Returns:
        Liste von Hex-Farbcodes
    """
    if theme_manager is None:
        import streamlit as st
        theme_manager = st.session_state.get('theme_manager')
        if theme_manager is None:
            theme_manager = ThemeManager()
            theme_manager.set_theme('shadcn-default')
    
    if not theme_manager.current_theme:
        raise ValueError("Kein Theme aktiv")
    
    return _get_chart_colors(theme_manager.current_theme)


def _get_chart_colors(theme) -> List[str]:
    """Extrahiert Chart-Farben aus Theme"""
    return [
        theme.colors.chart_1,
        theme.colors.chart_2,
        theme.colors.chart_3,
        theme.colors.chart_4,
        theme.colors.chart_5
    ]


def _is_dark_mode(theme) -> bool:
    """
    Erkennt ob Theme im Dark Mode ist
    
    Prüft Helligkeit der Hintergrundfarbe
    """
    bg = theme.colors.background
    
    # Konvertiere Hex zu RGB
    if bg.startswith('#'):
        r = int(bg[1:3], 16)
        g = int(bg[3:5], 16)
        b = int(bg[5:7], 16)
        
        # Berechne relative Luminanz
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        # Dark Mode wenn Luminanz < 0.5
        return luminance < 0.5
    
    return False


def _hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """
    Konvertiert Hex-Farbe zu RGBA-String
    
    Args:
        hex_color: Hex-Farbcode (z.B. '#38bdf8')
        alpha: Alpha-Wert (0.0 - 1.0)
    
    Returns:
        RGBA-String (z.B. 'rgba(56, 189, 248, 0.2)')
    """
    hex_color = hex_color.lstrip('#')
    
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return f'rgba({r}, {g}, {b}, {alpha})'


def _create_gradient_color(hex_color: str, opacity: float = 0.2) -> str:
    """
    Erstellt Gradient-Farbe für Area-Charts
    
    Args:
        hex_color: Basis-Hex-Farbe
        opacity: Transparenz
    
    Returns:
        RGBA-String mit Gradient-Effekt
    """
    # Für echte Gradienten würde man SVG verwenden
    # Hier verwenden wir einfach eine transparente Version
    return _hex_to_rgba(hex_color, opacity)


def _create_colorscale(colors: List[str]) -> List[List]:
    """
    Erstellt Plotly-Colorscale aus Farbliste
    
    Args:
        colors: Liste von Hex-Farbcodes
    
    Returns:
        Plotly-Colorscale-Format [[0, color1], [0.5, color2], [1, color3]]
    """
    if not colors:
        return [[0, '#000000'], [1, '#ffffff']]
    
    n = len(colors)
    return [[i / (n - 1), color] for i, color in enumerate(colors)]


# Vordefinierte Chart-Typen mit optimalen Einstellungen

def create_line_chart(
    x: List,
    y: List,
    name: Optional[str] = None,
    theme_manager: Optional[ThemeManager] = None,
    **kwargs
) -> go.Figure:
    """
    Erstellt einen Linien-Chart mit shadcn/ui-Styling
    
    Args:
        x: X-Achsen-Daten
        y: Y-Achsen-Daten
        name: Name der Linie
        theme_manager: ThemeManager-Instanz
        **kwargs: Zusätzliche Scatter-Parameter
    
    Returns:
        Gestylte Figure
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        name=name,
        mode='lines+markers',
        **kwargs
    ))
    
    return apply_chart_theme(fig, theme_manager, enable_spline=True)


def create_area_chart(
    x: List,
    y: List,
    name: Optional[str] = None,
    theme_manager: Optional[ThemeManager] = None,
    **kwargs
) -> go.Figure:
    """
    Erstellt einen Area-Chart mit Gradient-Fill
    
    Args:
        x: X-Achsen-Daten
        y: Y-Achsen-Daten
        name: Name der Fläche
        theme_manager: ThemeManager-Instanz
        **kwargs: Zusätzliche Scatter-Parameter
    
    Returns:
        Gestylte Figure mit Gradient
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        name=name,
        mode='lines',
        fill='tozeroy',
        **kwargs
    ))
    
    return apply_chart_theme(fig, theme_manager, enable_gradients=True)


def create_bar_chart(
    x: List,
    y: List,
    name: Optional[str] = None,
    theme_manager: Optional[ThemeManager] = None,
    **kwargs
) -> go.Figure:
    """
    Erstellt einen Bar-Chart mit shadcn/ui-Styling
    
    Args:
        x: X-Achsen-Daten (Kategorien)
        y: Y-Achsen-Daten (Werte)
        name: Name der Balken
        theme_manager: ThemeManager-Instanz
        **kwargs: Zusätzliche Bar-Parameter
    
    Returns:
        Gestylte Figure
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x,
        y=y,
        name=name,
        **kwargs
    ))
    
    return apply_chart_theme(fig, theme_manager)


def create_pie_chart(
    labels: List[str],
    values: List[float],
    theme_manager: Optional[ThemeManager] = None,
    **kwargs
) -> go.Figure:
    """
    Erstellt einen Pie-Chart mit shadcn/ui-Farben
    
    Args:
        labels: Beschriftungen
        values: Werte
        theme_manager: ThemeManager-Instanz
        **kwargs: Zusätzliche Pie-Parameter
    
    Returns:
        Gestylte Figure
    """
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        **kwargs
    ))
    
    return apply_chart_theme(fig, theme_manager)


# Utility-Funktionen für erweiterte Anpassungen

def add_chart_annotations(
    fig: go.Figure,
    annotations: List[Dict[str, Any]],
    theme_manager: Optional[ThemeManager] = None
) -> go.Figure:
    """
    Fügt Annotationen mit Theme-Styling hinzu
    
    Args:
        fig: Figure Objekt
        annotations: Liste von Annotation-Dicts
        theme_manager: ThemeManager-Instanz
    
    Returns:
        Figure mit Annotationen
    """
    if theme_manager is None:
        import streamlit as st
        theme_manager = st.session_state.get('theme_manager')
    
    if theme_manager and theme_manager.current_theme:
        theme = theme_manager.current_theme
        
        # Style Annotationen
        for ann in annotations:
            ann.setdefault('font', {})
            ann['font'].setdefault('family', theme.typography.font_family)
            ann['font'].setdefault('color', theme.colors.foreground)
            ann.setdefault('bgcolor', theme.colors.muted)
            ann.setdefault('bordercolor', theme.colors.border)
    
    fig.update_layout(annotations=annotations)
    return fig


def set_chart_title(
    fig: go.Figure,
    title: str,
    subtitle: Optional[str] = None,
    theme_manager: Optional[ThemeManager] = None
) -> go.Figure:
    """
    Setzt Chart-Titel mit Theme-Styling
    
    Args:
        fig: Figure Objekt
        title: Haupttitel
        subtitle: Untertitel (optional)
        theme_manager: ThemeManager-Instanz
    
    Returns:
        Figure mit gestyltem Titel
    """
    if theme_manager is None:
        import streamlit as st
        theme_manager = st.session_state.get('theme_manager')
    
    title_text = title
    if subtitle:
        title_text = f"{title}<br><sub>{subtitle}</sub>"
    
    if theme_manager and theme_manager.current_theme:
        theme = theme_manager.current_theme
        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(
                    size=20,
                    color=theme.colors.foreground,
                    family=theme.typography.font_family
                ),
                x=0.5,
                xanchor='center'
            )
        )
    else:
        fig.update_layout(title=title_text)
    
    return fig
