# shadcn/ui Streamlit Integration Guide

## Übersicht

Dieses Dokument beschreibt die vollständige Integration des shadcn/ui Design-Systems in die Streamlit-Anwendung. Das System bietet moderne, konsistente UI-Komponenten mit Theme-Unterstützung.

## Inhaltsverzeichnis

1. [Installation](#installation)
2. [Theme-System](#theme-system)
3. [Komponenten](#komponenten)
4. [Best Practices](#best-practices)
5. [Beispiele](#beispiele)

---

## Installation

### Voraussetzungen

```bash
pip install streamlit-shadcn-ui
pip install watchdog  # Für Hot Reload
```

### Aktivierung

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from utils.shadcn_css_generator import CSSGenerator

# Theme-System initialisieren
theme_manager = ThemeManager()
css_generator = CSSGenerator(theme_manager)

# CSS injizieren
st.markdown(f"<style>{css_generator.generate_full_css()}</style>", unsafe_allow_html=True)
```

---

## Theme-System

### Verfügbare Themes

| Theme | Beschreibung |
|-------|-------------|
| `default` | Standard-Theme mit neutralen Farben |
| `dark` | Dunkles Theme für reduzierte Augenbelastung |
| `ocean` | Blaue Farbpalette |
| `forest` | Grüne Farbpalette |
| `sunset` | Warme Orange/Rot-Töne |

### Theme wechseln

```python
from theming.theme_manager import ThemeManager

theme_manager = ThemeManager()
theme_manager.set_theme("dark")
```

### Theme-Selector UI

```python
from utils.shadcn_theme_selector import render_theme_selector

# In der Sidebar
with st.sidebar:
    render_theme_selector()
```

### Custom Theme erstellen

```python
from tools.theme_generator import ThemeGenerator

generator = ThemeGenerator()
custom_theme = generator.generate_from_base_color("#3B82F6")
generator.export_theme(custom_theme, "my_custom_theme.json")
```

---

## Komponenten

### Card

```python
from components.shadcn_card import Card

# Einfache Card
Card(
    title="Projekttitel",
    content="Beschreibung des Projekts",
    variant="default"  # default, outlined, elevated
)

# Card mit Footer
Card(
    title="Statistik",
    content="Aktuelle Werte",
    footer="Letzte Aktualisierung: Heute",
    variant="elevated"
)
```

### Alert

```python
from components.shadcn_alert import Alert

# Info Alert
Alert(
    message="Information für den Benutzer",
    type="info"  # info, success, warning, error
)

# Success Alert mit Icon
Alert(
    message="Aktion erfolgreich!",
    type="success",
    show_icon=True
)
```

### Badge

```python
from components.shadcn_badge import Badge

# Standard Badge
Badge(text="Neu", variant="default")

# Farbige Badges
Badge(text="Aktiv", variant="success")
Badge(text="Ausstehend", variant="warning")
Badge(text="Fehler", variant="destructive")
```

### MetricCard

```python
from components.shadcn_metric_card import MetricCard

MetricCard(
    title="Umsatz",
    value="€ 12.345,67",
    trend="+15%",
    trend_direction="up",  # up, down, neutral
    icon="💰",
    size="medium"  # small, medium, large
)
```

### Table

```python
from components.shadcn_table import Table
import pandas as pd

df = pd.DataFrame({
    "Name": ["Projekt A", "Projekt B"],
    "Status": ["Aktiv", "Abgeschlossen"],
    "Wert": [10000, 25000]
})

Table(
    data=df,
    sortable=True,
    striped=True,
    hover=True
)
```

### Accordion

```python
from components.shadcn_accordion import Accordion

items = [
    {"title": "Abschnitt 1", "content": "Inhalt 1"},
    {"title": "Abschnitt 2", "content": "Inhalt 2"},
]

Accordion(items=items, allow_multiple=False)
```

### Progress

```python
from components.shadcn_progress import Progress

Progress(value=75, max=100, show_label=True)
```

### Skeleton Loader

```python
from components.shadcn_skeleton import Skeleton

# Während Daten laden
if loading:
    Skeleton(variant="card")
else:
    # Echte Komponente anzeigen
    Card(...)
```


### Input mit Floating Label

```python
from components.shadcn_input import Input

Input(
    label="E-Mail",
    placeholder="name@example.com",
    type="email",
    floating_label=True,
    prefix_icon="📧"
)
```

### DatePicker

```python
from components.shadcn_datepicker import DatePicker

selected_date = DatePicker(
    label="Datum auswählen",
    min_date="2024-01-01",
    max_date="2025-12-31"
)
```

### Dropdown Menu

```python
from components.shadcn_dropdown import DropdownMenu

DropdownMenu(
    trigger="Aktionen",
    items=[
        {"label": "Bearbeiten", "icon": "✏️", "action": "edit"},
        {"label": "Löschen", "icon": "🗑️", "action": "delete"},
        {"separator": True},
        {"label": "Exportieren", "icon": "📤", "action": "export"},
    ]
)
```

### Breadcrumb

```python
from components.shadcn_breadcrumb import Breadcrumb

Breadcrumb(
    items=[
        {"label": "Home", "href": "/"},
        {"label": "Projekte", "href": "/projects"},
        {"label": "Projekt A", "active": True},
    ]
)
```

### Pagination

```python
from components.shadcn_pagination import Pagination

current_page = Pagination(
    total_items=100,
    items_per_page=10,
    current_page=1
)
```

---

## Chart-Styling

### Plotly Charts mit shadcn/ui Theme

```python
from utils.shadcn_chart_theme import apply_chart_theme
import plotly.express as px

fig = px.line(df, x="date", y="value")
fig = apply_chart_theme(fig)
st.plotly_chart(fig)
```

### Verfügbare Chart-Optionen

```python
fig = apply_chart_theme(
    fig,
    dark_mode=False,
    gradient_fill=True,
    smooth_lines=True,
    modern_fonts=True
)
```

---

## Sidebar-Styling

```python
from utils.shadcn_sidebar import apply_sidebar_styling

# Am Anfang der App
apply_sidebar_styling()

# Sidebar mit Gruppen
with st.sidebar:
    st.markdown("### Navigation")
    st.page_link("pages/dashboard.py", label="Dashboard", icon="📊")
    st.page_link("pages/projects.py", label="Projekte", icon="📁")
    
    st.markdown("### Einstellungen")
    st.page_link("pages/settings.py", label="Einstellungen", icon="⚙️")
```

---

## Animationen

### Fade-In Animation

```python
from utils.shadcn_animations import fade_in

with fade_in():
    st.write("Dieser Inhalt erscheint mit Fade-In")
```

### Slide Animation

```python
from utils.shadcn_animations import slide_in

with slide_in(direction="left"):
    st.write("Dieser Inhalt gleitet von links herein")
```

---

## Responsive Design

### Breakpoints

| Breakpoint | Breite | Beschreibung |
|------------|--------|--------------|
| `mobile` | < 640px | Smartphones |
| `tablet` | 640px - 1024px | Tablets |
| `desktop` | > 1024px | Desktop |

### Responsive Layouts

```python
from utils.shadcn_responsive import responsive_columns

# Automatisch angepasste Spalten
cols = responsive_columns(
    desktop=3,
    tablet=2,
    mobile=1
)

for col in cols:
    with col:
        Card(...)
```

---

## Best Practices

### 1. Theme-Konsistenz

- Verwende immer die Theme-Farben über CSS-Variablen
- Vermeide hardcodierte Farbwerte

```python
# ❌ Schlecht
st.markdown('<div style="color: #3B82F6">Text</div>', unsafe_allow_html=True)

# ✅ Gut
st.markdown('<div style="color: var(--primary)">Text</div>', unsafe_allow_html=True)
```

### 2. Komponenten-Hierarchie

- Verwende Cards als Container für zusammengehörige Inhalte
- Nutze Accordions für optionale Details
- Setze Badges für Status-Anzeigen ein

### 3. Performance

- Nutze `@st.cache_data` für Theme-Daten
- Aktiviere CSS-Caching in Produktion
- Verwende Skeleton-Loader während Ladevorgängen

### 4. Accessibility

- Stelle ausreichenden Farbkontrast sicher (WCAG 2.1 AA)
- Füge ARIA-Labels zu interaktiven Elementen hinzu
- Teste Keyboard-Navigation

---

## Fehlerbehebung

### Theme wird nicht angewendet

1. Prüfe, ob CSS korrekt injiziert wird
2. Prüfe Browser-Konsole auf Fehler
3. Lösche Browser-Cache

### Komponenten werden nicht angezeigt

1. Prüfe Import-Pfade
2. Stelle sicher, dass `streamlit-shadcn-ui` installiert ist
3. Prüfe Streamlit-Version (>= 1.28.0)

### Performance-Probleme

1. Aktiviere CSS-Caching
2. Reduziere Theme-Wechsel
3. Nutze Lazy Loading für große Komponenten

---

## API-Referenz

### ThemeManager

```python
class ThemeManager:
    def __init__(self, themes_dir: str = "theming/themes")
    def get_theme(self, name: str) -> Theme
    def set_theme(self, name: str) -> None
    def get_current_theme(self) -> Theme
    def list_themes(self) -> List[str]
    def reload_themes(self) -> None
```

### CSSGenerator

```python
class CSSGenerator:
    def __init__(self, theme_manager: ThemeManager)
    def generate_variables(self) -> str
    def generate_component_styles(self) -> str
    def generate_utility_classes(self) -> str
    def generate_full_css(self) -> str
```

### ThemeValidator

```python
class ThemeValidator:
    def validate(self, theme_data: dict) -> ValidationResult
    def validate_colors(self, colors: dict) -> List[str]
    def validate_typography(self, typography: dict) -> List[str]
```

---

## Changelog

### Version 1.0.0

- Initiale Implementierung des Theme-Systems
- 17 Basis-Komponenten
- 5 vordefinierte Themes
- Chart-Styling-Integration
- Responsive Design Support
- Accessibility Features

---

## Support

Bei Fragen oder Problemen:

1. Prüfe diese Dokumentation
2. Schaue in den Troubleshooting-Abschnitt
3. Erstelle ein Issue im Repository
