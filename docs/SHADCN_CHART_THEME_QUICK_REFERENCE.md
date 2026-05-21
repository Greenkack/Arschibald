# shadcn/ui Chart Theme - Quick Reference

Schnellreferenz für das Chart-Styling-System.

## Installation

```python
from theming.theme_manager import ThemeManager
from utils.shadcn_chart_theme import apply_chart_theme
```

## Basis-Verwendung

### 1. Theme Manager initialisieren

```python
import streamlit as st
from theming.theme_manager import ThemeManager

if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

theme_manager = st.session_state.theme_manager
```

### 2. Chart erstellen und stylen

```python
import plotly.graph_objects as go
from utils.shadcn_chart_theme import apply_chart_theme

# Chart erstellen
fig = go.Figure(data=[go.Scatter(x=[1,2,3], y=[4,5,6])])

# Theme anwenden
fig = apply_chart_theme(fig, theme_manager)

# Anzeigen
st.plotly_chart(fig)
```

## Schnelle Chart-Erstellung

### Linien-Chart

```python
from utils.shadcn_chart_theme import create_line_chart

fig = create_line_chart(
    x=[1, 2, 3, 4, 5],
    y=[10, 20, 15, 25, 30],
    name="Umsatz",
    theme_manager=theme_manager
)
st.plotly_chart(fig)
```

### Area-Chart

```python
from utils.shadcn_chart_theme import create_area_chart

fig = create_area_chart(
    x=[1, 2, 3, 4, 5],
    y=[10, 20, 15, 25, 30],
    name="Energie",
    theme_manager=theme_manager
)
st.plotly_chart(fig)
```

### Bar-Chart

```python
from utils.shadcn_chart_theme import create_bar_chart

fig = create_bar_chart(
    x=['Jan', 'Feb', 'Mär'],
    y=[30, 45, 35],
    name="Verkäufe",
    theme_manager=theme_manager
)
st.plotly_chart(fig)
```

### Pie-Chart

```python
from utils.shadcn_chart_theme import create_pie_chart

fig = create_pie_chart(
    labels=['A', 'B', 'C'],
    values=[35, 25, 20],
    theme_manager=theme_manager
)
st.plotly_chart(fig)
```

## Optionen

### Spline-Kurven deaktivieren

```python
fig = apply_chart_theme(fig, theme_manager, enable_spline=False)
```

### Gradients deaktivieren

```python
fig = apply_chart_theme(fig, theme_manager, enable_gradients=False)
```

### Dark Mode erzwingen

```python
fig = apply_chart_theme(fig, theme_manager, dark_mode=True)
```

### Mobile Layout

```python
from utils.shadcn_chart_theme import apply_responsive_layout

fig = apply_responsive_layout(fig, mobile=True)
```

## Erweiterte Features

### Titel setzen

```python
from utils.shadcn_chart_theme import set_chart_title

fig = set_chart_title(
    fig,
    "Haupttitel",
    "Untertitel",
    theme_manager
)
```

### Annotationen hinzufügen

```python
from utils.shadcn_chart_theme import add_chart_annotations

annotations = [
    dict(x=5, y=30, text="Peak", showarrow=True)
]
fig = add_chart_annotations(fig, annotations, theme_manager)
```

### Chart-Farben abrufen

```python
from utils.shadcn_chart_theme import get_chart_colors

colors = get_chart_colors(theme_manager)
# ['#38bdf8', '#34d399', '#f87171', '#fbbf24', '#a78bfa']
```

## Verfügbare Themes

- `shadcn-default` - Standard Light Theme
- `shadcn-dark` - Dark Theme
- `shadcn-ocean` - Blau-Töne
- `shadcn-forest` - Grün-Töne
- `shadcn-sunset` - Warm-Töne

## Häufige Patterns

### Multi-Linien-Chart

```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6], name="A"))
fig.add_trace(go.Scatter(x=[1,2,3], y=[7,8,9], name="B"))
fig = apply_chart_theme(fig, theme_manager)
```

### Gestapelter Area-Chart

```python
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[1,2,3], y=[1,2,3],
    fill='tozeroy', stackgroup='one'
))
fig.add_trace(go.Scatter(
    x=[1,2,3], y=[2,3,4],
    fill='tonexty', stackgroup='one'
))
fig = apply_chart_theme(fig, theme_manager)
```

### Gruppierter Bar-Chart

```python
fig = go.Figure()
fig.add_trace(go.Bar(x=['Q1','Q2'], y=[20,30], name='2023'))
fig.add_trace(go.Bar(x=['Q1','Q2'], y=[25,35], name='2024'))
fig = apply_chart_theme(fig, theme_manager)
```

## Performance-Tipps

### Caching

```python
@st.cache_data
def create_chart(data, _theme_manager):
    fig = create_line_chart(
        x=data['x'],
        y=data['y'],
        theme_manager=_theme_manager
    )
    return fig
```

### Lazy Loading

Erstelle Charts nur wenn sichtbar:

```python
with st.expander("Chart anzeigen"):
    fig = create_line_chart(...)
    st.plotly_chart(fig)
```

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| "Kein Theme aktiv" | `theme_manager.set_theme('shadcn-default')` |
| Farben falsch | ThemeManager korrekt übergeben |
| Keine Splines | `enable_spline=True` setzen |
| Keine Gradients | `enable_gradients=True` + `fill='tozeroy'` |

## Siehe auch

- [Vollständige Referenz](../utils/SHADCN_CHART_THEME_REFERENCE.md)
- [Theme Manager](../theming/THEME_MANAGER_REFERENCE.md)
- [Demo](../demo_shadcn_chart_theme.py)
