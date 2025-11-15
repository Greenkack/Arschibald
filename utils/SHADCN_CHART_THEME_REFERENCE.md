# shadcn/ui Chart Theme - Referenz

Vollständige Referenz für das Chart-Styling-System.

## Übersicht

Das Chart-Theme-System wendet konsistentes shadcn/ui-Styling auf Plotly-Charts an. Es unterstützt:

- ✅ Automatisches Theme-Styling
- ✅ Glatte Spline-Kurven
- ✅ Gradient-Fills für Area-Charts
- ✅ Dark Mode Support
- ✅ Responsive Layouts
- ✅ 5 harmonische Chart-Farben pro Theme
- ✅ Moderne Schriftarten

## Hauptfunktionen

### apply_chart_theme()

Wendet shadcn/ui-Theme auf bestehende Plotly-Figure an.

```python
from utils.shadcn_chart_theme import apply_chart_theme
import plotly.graph_objects as go

fig = go.Figure(data=[go.Scatter(x=[1,2,3], y=[4,5,6])])
fig = apply_chart_theme(fig, theme_manager)
```

**Parameter:**
- `fig` (go.Figure): Plotly Figure Objekt
- `theme_manager` (ThemeManager, optional): ThemeManager-Instanz
- `enable_spline` (bool): Aktiviert glatte Spline-Kurven (default: True)
- `enable_gradients` (bool): Aktiviert Gradient-Fills (default: True)
- `dark_mode` (bool, optional): Erzwingt Dark Mode (None = automatisch)

**Returns:** Modifizierte Figure mit shadcn/ui-Styling

### create_line_chart()

Erstellt Linien-Chart mit shadcn/ui-Styling.

```python
from utils.shadcn_chart_theme import create_line_chart

fig = create_line_chart(
    x=[1, 2, 3, 4, 5],
    y=[10, 20, 15, 25, 30],
    name="Umsatz",
    theme_manager=theme_manager
)
```

**Parameter:**
- `x` (List): X-Achsen-Daten
- `y` (List): Y-Achsen-Daten
- `name` (str, optional): Name der Linie
- `theme_manager` (ThemeManager, optional): ThemeManager-Instanz
- `**kwargs`: Zusätzliche Scatter-Parameter

**Features:**
- Glatte Spline-Kurven
- Marker an Datenpunkten
- Automatische Theme-Farben

### create_area_chart()

Erstellt Area-Chart mit Gradient-Fill.

```python
from utils.shadcn_chart_theme import create_area_chart

fig = create_area_chart(
    x=[1, 2, 3, 4, 5],
    y=[10, 20, 15, 25, 30],
    name="Energieproduktion",
    theme_manager=theme_manager
)
```

**Parameter:**
- `x` (List): X-Achsen-Daten
- `y` (List): Y-Achsen-Daten
- `name` (str, optional): Name der Fläche
- `theme_manager` (ThemeManager, optional): ThemeManager-Instanz
- `**kwargs`: Zusätzliche Scatter-Parameter

**Features:**
- Gradient-Fill unter der Kurve
- Glatte Spline-Kurven
- Transparente Füllung

### create_bar_chart()

Erstellt Bar-Chart mit shadcn/ui-Styling.

```python
from utils.shadcn_chart_theme import create_bar_chart

fig = create_bar_chart(
    x=['Jan', 'Feb', 'Mär', 'Apr'],
    y=[30, 45, 35, 50],
    name="Verkäufe",
    theme_manager=theme_manager
)
```

**Parameter:**
- `x` (List): X-Achsen-Daten (Kategorien)
- `y` (List): Y-Achsen-Daten (Werte)
- `name` (str, optional): Name der Balken
- `theme_manager` (ThemeManager, optional): ThemeManager-Instanz
- `**kwargs`: Zusätzliche Bar-Parameter

**Features:**
- Theme-Farben
- Keine Border-Linien
- Optimierte Balkenbreite

### create_pie_chart()

Erstellt Pie-Chart mit shadcn/ui-Farben.

```python
from utils.shadcn_chart_theme import create_pie_chart

fig = create_pie_chart(
    labels=['Solar', 'Wind', 'Wasser'],
    values=[35, 25, 20],
    theme_manager=theme_manager,
    hole=0.3  # Donut-Chart
)
```

**Parameter:**
- `labels` (List[str]): Beschriftungen
- `values` (List[float]): Werte
- `theme_manager` (ThemeManager, optional): ThemeManager-Instanz
- `**kwargs`: Zusätzliche Pie-Parameter (z.B. `hole` für Donut)

**Features:**
- 5 harmonische Farben
- Weiße Trennlinien
- Donut-Modus unterstützt

### create_themed_figure()

Erstellt leere Figure mit voreingestelltem Theme.

```python
from utils.shadcn_chart_theme import create_themed_figure

fig = create_themed_figure(
    theme_manager=theme_manager,
    title="Mein Chart"
)

# Traces hinzufügen
fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6]))
```

**Parameter:**
- `theme_manager` (ThemeManager, optional): ThemeManager-Instanz
- `title` (str, optional): Chart-Titel
- `**kwargs`: Zusätzliche Layout-Parameter

## Utility-Funktionen

### get_chart_colors()

Gibt Liste der Chart-Farben aus dem aktuellen Theme zurück.

```python
from utils.shadcn_chart_theme import get_chart_colors

colors = get_chart_colors(theme_manager)
# ['#38bdf8', '#34d399', '#f87171', '#fbbf24', '#a78bfa']
```

### apply_responsive_layout()

Passt Chart-Layout für verschiedene Bildschirmgrößen an.

```python
from utils.shadcn_chart_theme import apply_responsive_layout

# Desktop
fig = apply_responsive_layout(fig, mobile=False)

# Mobile
fig = apply_responsive_layout(fig, mobile=True)
```

**Mobile-Optimierungen:**
- Kleinere Margins
- Kleinere Schriftgröße
- Horizontale Legend unten

### set_chart_title()

Setzt Chart-Titel mit Theme-Styling.

```python
from utils.shadcn_chart_theme import set_chart_title

fig = set_chart_title(
    fig,
    title="Haupttitel",
    subtitle="Untertitel",
    theme_manager=theme_manager
)
```

### add_chart_annotations()

Fügt Annotationen mit Theme-Styling hinzu.

```python
from utils.shadcn_chart_theme import add_chart_annotations

annotations = [
    dict(
        x=5,
        y=30,
        text="Peak",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40
    )
]

fig = add_chart_annotations(fig, annotations, theme_manager)
```

## Erweiterte Beispiele

### Multi-Linien-Chart

```python
import plotly.graph_objects as go
from utils.shadcn_chart_theme import apply_chart_theme

fig = go.Figure()

# Mehrere Linien
fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6], name="Produkt A"))
fig.add_trace(go.Scatter(x=[1,2,3], y=[7,8,9], name="Produkt B"))
fig.add_trace(go.Scatter(x=[1,2,3], y=[10,11,12], name="Produkt C"))

# Theme anwenden (verwendet automatisch verschiedene Farben)
fig = apply_chart_theme(fig, theme_manager)

st.plotly_chart(fig)
```

### Gestapelter Area-Chart

```python
import plotly.graph_objects as go
from utils.shadcn_chart_theme import apply_chart_theme

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1,2,3,4,5],
    y=[1,2,3,4,5],
    name="Serie 1",
    mode='lines',
    fill='tozeroy',
    stackgroup='one'
))

fig.add_trace(go.Scatter(
    x=[1,2,3,4,5],
    y=[2,3,4,5,6],
    name="Serie 2",
    mode='lines',
    fill='tonexty',
    stackgroup='one'
))

fig = apply_chart_theme(fig, theme_manager, enable_gradients=True)

st.plotly_chart(fig)
```

### Gruppierter Bar-Chart

```python
import plotly.graph_objects as go
from utils.shadcn_chart_theme import apply_chart_theme

fig = go.Figure()

categories = ['Q1', 'Q2', 'Q3', 'Q4']

fig.add_trace(go.Bar(x=categories, y=[20, 30, 25, 35], name='2023'))
fig.add_trace(go.Bar(x=categories, y=[25, 35, 30, 40], name='2024'))

fig = apply_chart_theme(fig, theme_manager)

st.plotly_chart(fig)
```

### Kombinierter Chart (Bar + Line)

```python
import plotly.graph_objects as go
from utils.shadcn_chart_theme import apply_chart_theme

fig = go.Figure()

x = [1, 2, 3, 4, 5]

# Bar-Trace
fig.add_trace(go.Bar(
    x=x,
    y=[20, 25, 30, 28, 35],
    name="Ist-Wert"
))

# Line-Trace auf zweiter Y-Achse
fig.add_trace(go.Scatter(
    x=x,
    y=[15, 20, 25, 30, 28],
    name="Soll-Wert",
    mode='lines+markers',
    yaxis='y2'
))

# Zweite Y-Achse konfigurieren
fig.update_layout(
    yaxis2=dict(
        overlaying='y',
        side='right'
    )
)

fig = apply_chart_theme(fig, theme_manager)

st.plotly_chart(fig)
```

### Chart mit Annotationen

```python
from utils.shadcn_chart_theme import (
    create_line_chart,
    add_chart_annotations,
    set_chart_title
)

# Chart erstellen
fig = create_line_chart(
    x=[1, 2, 3, 4, 5, 6],
    y=[20, 25, 30, 28, 35, 40],
    name="Umsatz",
    theme_manager=theme_manager
)

# Titel setzen
fig = set_chart_title(
    fig,
    "Monatlicher Umsatz",
    "Januar - Juni 2024",
    theme_manager
)

# Annotationen hinzufügen
annotations = [
    dict(
        x=3,
        y=30,
        text="Höchster Wert",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40
    ),
    dict(
        x=6,
        y=40,
        text="Ziel erreicht!",
        showarrow=True,
        arrowhead=2,
        ax=-40,
        ay=-40
    )
]

fig = add_chart_annotations(fig, annotations, theme_manager)

st.plotly_chart(fig)
```

## Theme-Farben

Jedes Theme definiert 5 harmonische Chart-Farben:

### shadcn-default
- Chart 1: `#38bdf8` (Sky Blue)
- Chart 2: `#34d399` (Emerald)
- Chart 3: `#f87171` (Red)
- Chart 4: `#fbbf24` (Amber)
- Chart 5: `#a78bfa` (Purple)

### shadcn-dark
- Chart 1: `#38bdf8` (Sky Blue)
- Chart 2: `#34d399` (Emerald)
- Chart 3: `#f87171` (Red)
- Chart 4: `#fbbf24` (Amber)
- Chart 5: `#a78bfa` (Purple)

### shadcn-ocean
- Chart 1: `#06b6d4` (Cyan)
- Chart 2: `#0ea5e9` (Blue)
- Chart 3: `#3b82f6` (Indigo)
- Chart 4: `#6366f1` (Violet)
- Chart 5: `#8b5cf6` (Purple)

### shadcn-forest
- Chart 1: `#10b981` (Emerald)
- Chart 2: `#22c55e` (Green)
- Chart 3: `#84cc16` (Lime)
- Chart 4: `#eab308` (Yellow)
- Chart 5: `#f59e0b` (Amber)

### shadcn-sunset
- Chart 1: `#f97316` (Orange)
- Chart 2: `#ef4444` (Red)
- Chart 3: `#ec4899` (Pink)
- Chart 4: `#d946ef` (Fuchsia)
- Chart 5: `#a855f7` (Purple)

## Best Practices

### 1. Theme Manager in Session State

```python
import streamlit as st
from theming.theme_manager import ThemeManager

# Initialisiere einmal beim App-Start
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

# Verwende in Charts
theme_manager = st.session_state.theme_manager
```

### 2. Konsistente Farben

Verwende `get_chart_colors()` für konsistente Farben über mehrere Charts:

```python
colors = get_chart_colors(theme_manager)

# Verwende in allen Charts
fig1.update_traces(marker_color=colors[0])
fig2.update_traces(marker_color=colors[1])
```

### 3. Responsive Design

Passe Charts an Bildschirmgröße an:

```python
# Erkenne Mobile
is_mobile = st.session_state.get('is_mobile', False)

# Wende entsprechendes Layout an
fig = apply_responsive_layout(fig, mobile=is_mobile)
```

### 4. Performance

Cache Chart-Erstellung für bessere Performance:

```python
@st.cache_data
def create_sales_chart(data, _theme_manager):
    fig = create_line_chart(
        x=data['x'],
        y=data['y'],
        theme_manager=_theme_manager
    )
    return fig

# Verwende gecachte Funktion
fig = create_sales_chart(data, theme_manager)
```

### 5. Dark Mode

Lasse Dark Mode automatisch erkennen:

```python
# Automatische Erkennung
fig = apply_chart_theme(fig, theme_manager)  # dark_mode=None

# Oder explizit setzen
fig = apply_chart_theme(fig, theme_manager, dark_mode=True)
```

## Fehlerbehebung

### Problem: "Kein Theme aktiv"

**Lösung:** Stelle sicher, dass ein Theme gesetzt ist:

```python
theme_manager = ThemeManager()
theme_manager.set_theme('shadcn-default')  # Theme setzen!
```

### Problem: Farben werden nicht angewendet

**Lösung:** Prüfe ob ThemeManager korrekt übergeben wird:

```python
# Falsch
fig = apply_chart_theme(fig)  # theme_manager fehlt

# Richtig
fig = apply_chart_theme(fig, theme_manager)
```

### Problem: Spline-Kurven werden nicht angezeigt

**Lösung:** Aktiviere Spline explizit:

```python
fig = apply_chart_theme(fig, theme_manager, enable_spline=True)
```

### Problem: Gradient-Fills fehlen

**Lösung:** 
1. Stelle sicher, dass Trace `fill` gesetzt hat
2. Aktiviere Gradients explizit

```python
fig.add_trace(go.Scatter(
    x=[1,2,3],
    y=[4,5,6],
    fill='tozeroy'  # Wichtig!
))

fig = apply_chart_theme(fig, theme_manager, enable_gradients=True)
```

## API-Referenz

Siehe vollständige Docstrings in `utils/shadcn_chart_theme.py`.

## Siehe auch

- [Theme Manager Referenz](../theming/THEME_MANAGER_REFERENCE.md)
- [CSS Generator Referenz](../theming/CSS_GENERATOR_REFERENCE.md)
- [shadcn/ui Dokumentation](https://ui.shadcn.com/)
