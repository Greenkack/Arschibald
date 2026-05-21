# MetricCard Component Reference

## Overview

Die `MetricCard`-Komponente ist eine moderne, shadcn/ui-styled Komponente zur Anzeige von KPIs (Key Performance Indicators) und wichtigen Metriken. Sie bietet Trend-Indikatoren, verschiedene Größen, Icons und animierte Wert-Änderungen.

## Features

- ✅ **Trend-Indikatoren**: Zeigt Aufwärts-/Abwärtstrends mit Pfeilen und Farben
- ✅ **Verschiedene Größen**: Small, Medium, Large
- ✅ **Icons**: Optionale Icons für visuelle Identifikation
- ✅ **Animationen**: Fade-In und Count-Up Animationen
- ✅ **Responsive**: Automatisches Grid-Layout für Gruppen
- ✅ **Varianten**: Default, Outlined, Elevated
- ✅ **Beschreibungen**: Zusätzliche Kontext-Informationen

## Installation

```python
from components import MetricCard, MetricCardGroup
# oder
from components.metric_card import metric_card, metric_card_group
```

## Basic Usage

### Einfache MetricCard

```python
from components.metric_card import metric_card

metric_card(
    label="Umsatz",
    value="€45,231",
    icon="💰"
)
```

### MetricCard mit Trend

```python
metric_card(
    label="Neue Kunden",
    value="1,234",
    trend=12.5,  # Positiver Trend (grün, Pfeil nach oben)
    trend_label="+12.5% vs. letzter Monat",
    icon="👥"
)
```

### MetricCard mit negativem Trend

```python
metric_card(
    label="Absprungrate",
    value="23.4%",
    trend=-5.2,  # Negativer Trend (rot, Pfeil nach unten)
    trend_label="-5.2% vs. letzter Monat",
    icon="📉"
)
```

## API Reference

### MetricCard Class

```python
class MetricCard(ShadcnComponent):
    def render(
        self,
        label: str,
        value: str,
        description: Optional[str] = None,
        trend: Optional[float] = None,
        trend_label: Optional[str] = None,
        icon: Optional[str] = None,
        size: Literal["small", "medium", "large"] = "medium",
        variant: Literal["default", "outlined", "elevated"] = "default",
        show_trend_arrow: bool = True,
        animate: bool = True,
        custom_css: Optional[str] = None,
        key: Optional[str] = None
    ) -> None
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str` | **Required** | Label/Bezeichnung der Metrik |
| `value` | `str` | **Required** | Wert der Metrik (als String formatiert) |
| `description` | `Optional[str]` | `None` | Optionale Beschreibung unter dem Wert |
| `trend` | `Optional[float]` | `None` | Trend-Wert in Prozent (positiv = ↑, negativ = ↓) |
| `trend_label` | `Optional[str]` | `None` | Optionaler Text für den Trend |
| `icon` | `Optional[str]` | `None` | Optionales Icon (Emoji oder Unicode) |
| `size` | `Literal` | `"medium"` | Größe: `"small"`, `"medium"`, `"large"` |
| `variant` | `Literal` | `"default"` | Variante: `"default"`, `"outlined"`, `"elevated"` |
| `show_trend_arrow` | `bool` | `True` | Ob Trend-Pfeil angezeigt werden soll |
| `animate` | `bool` | `True` | Ob Wert-Änderungen animiert werden sollen |
| `custom_css` | `Optional[str]` | `None` | Zusätzliches Custom-CSS |
| `key` | `Optional[str]` | `None` | Eindeutiger Key für die Komponente |

### MetricCardGroup Class

```python
class MetricCardGroup(ShadcnComponent):
    def render(
        self,
        metrics: list[dict],
        columns: int = 3,
        gap: Literal["sm", "md", "lg"] = "md",
        size: Literal["small", "medium", "large"] = "medium",
        variant: Literal["default", "outlined", "elevated"] = "default",
        key: Optional[str] = None
    ) -> None
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `metrics` | `list[dict]` | **Required** | Liste von Metric-Konfigurationen |
| `columns` | `int` | `3` | Anzahl der Spalten im Grid |
| `gap` | `Literal` | `"md"` | Abstand zwischen Cards: `"sm"`, `"md"`, `"lg"` |
| `size` | `Literal` | `"medium"` | Standard-Größe für alle Cards |
| `variant` | `Literal` | `"default"` | Standard-Variante für alle Cards |
| `key` | `Optional[str]` | `None` | Eindeutiger Key |

## Examples

### Verschiedene Größen

```python
# Small
metric_card(
    label="Besucher",
    value="12,345",
    trend=8.2,
    icon="👁️",
    size="small"
)

# Medium (Standard)
metric_card(
    label="Besucher",
    value="12,345",
    trend=8.2,
    icon="👁️",
    size="medium"
)

# Large
metric_card(
    label="Besucher",
    value="12,345",
    trend=8.2,
    icon="👁️",
    size="large"
)
```

### Verschiedene Varianten

```python
# Default
metric_card(
    label="Conversion Rate",
    value="3.24%",
    trend=1.2,
    icon="🎯",
    variant="default"
)

# Outlined
metric_card(
    label="Conversion Rate",
    value="3.24%",
    trend=1.2,
    icon="🎯",
    variant="outlined"
)

# Elevated
metric_card(
    label="Conversion Rate",
    value="3.24%",
    trend=1.2,
    icon="🎯",
    variant="elevated"
)
```

### Mit Beschreibung

```python
metric_card(
    label="Durchschnittlicher Bestellwert",
    value="€127.50",
    description="Basierend auf 1,234 Bestellungen in diesem Monat",
    trend=5.3,
    icon="🛒",
    size="large"
)
```

### Ohne Trend-Pfeil

```python
metric_card(
    label="Wachstum",
    value="+15.2%",
    trend=15.2,
    show_trend_arrow=False,  # Kein Pfeil
    icon="📈"
)
```

### MetricCard-Gruppe

```python
from components.metric_card import metric_card_group

metric_card_group(
    metrics=[
        {
            "label": "Gesamtumsatz",
            "value": "€245,231",
            "trend": 12.5,
            "trend_label": "+12.5% vs. letzter Monat",
            "icon": "💰"
        },
        {
            "label": "Neue Kunden",
            "value": "1,234",
            "trend": 8.2,
            "trend_label": "+8.2% vs. letzter Monat",
            "icon": "👥"
        },
        {
            "label": "Bestellungen",
            "value": "3,456",
            "trend": -3.1,
            "trend_label": "-3.1% vs. letzter Monat",
            "icon": "📦"
        },
        {
            "label": "Conversion Rate",
            "value": "3.24%",
            "trend": 1.2,
            "trend_label": "+1.2% vs. letzter Monat",
            "icon": "🎯"
        }
    ],
    columns=4,
    gap="md",
    variant="elevated"
)
```

### Solar-spezifische Metriken

```python
metric_card_group(
    metrics=[
        {
            "label": "Aktuelle Leistung",
            "value": "8.5 kW",
            "description": "Von 10 kW Nennleistung",
            "trend": 15.2,
            "trend_label": "+15.2% vs. gestern",
            "icon": "☀️",
            "size": "large"
        },
        {
            "label": "Heutige Erzeugung",
            "value": "42.3 kWh",
            "description": "Seit Sonnenaufgang",
            "trend": 8.5,
            "trend_label": "+8.5% vs. gestern",
            "icon": "⚡",
            "size": "large"
        },
        {
            "label": "CO₂ Einsparung",
            "value": "18.2 kg",
            "description": "Heute eingespart",
            "trend": 8.5,
            "icon": "🌱",
            "size": "large"
        },
        {
            "label": "Eigenverbrauch",
            "value": "68%",
            "description": "Selbst verbraucht",
            "trend": 3.2,
            "trend_label": "+3.2% vs. letzter Monat",
            "icon": "🏠",
            "size": "large"
        }
    ],
    columns=2,
    gap="lg",
    variant="elevated"
)
```

## Styling

### Theme-Tokens

Die MetricCard verwendet folgende Theme-Tokens:

- `colors.background` - Hintergrundfarbe
- `colors.foreground` - Textfarbe
- `colors.border` - Border-Farbe
- `colors.muted_foreground` - Gedämpfte Textfarbe (Label)
- `colors.success` - Farbe für positive Trends
- `colors.error` - Farbe für negative Trends
- `borders.border_radius_lg` - Border-Radius
- `shadows.shadow_sm/md/lg` - Schatten
- `animations.transition_base` - Transition-Timing

### Custom CSS

```python
metric_card(
    label="Custom Styled",
    value="€12,345",
    custom_css="""
    .shadcn-metric-custom {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    """
)
```

## Trend-Logik

Die Trend-Anzeige funktioniert wie folgt:

| Trend-Wert | Farbe | Pfeil | Bedeutung |
|------------|-------|-------|-----------|
| `> 0` | Grün (`colors.success`) | ↑ | Positiver Trend |
| `< 0` | Rot (`colors.error`) | ↓ | Negativer Trend |
| `= 0` | Grau (`colors.muted_foreground`) | → | Kein Trend |
| `None` | - | - | Kein Trend angezeigt |

## Animationen

Die MetricCard unterstützt zwei Animationen:

1. **Fade-In Animation**: Die gesamte Card faded ein beim Laden
2. **Count-Up Animation**: Der Wert skaliert leicht beim Erscheinen

Animationen können mit `animate=False` deaktiviert werden.

## Responsive Verhalten

### MetricCardGroup

Die `MetricCardGroup` verwendet ein responsives Grid-Layout:

- **Mobile** (< 768px): 1 Spalte (auto-fit)
- **Desktop** (≥ 768px): Konfigurierte Anzahl Spalten

```python
# Wird auf Mobile zu 1 Spalte, auf Desktop zu 4 Spalten
metric_card_group(
    metrics=[...],
    columns=4  # Nur auf Desktop
)
```

## Best Practices

### 1. Wert-Formatierung

```python
# ✅ Gut: Formatierte Werte
metric_card(label="Umsatz", value="€45,231.50")
metric_card(label="Kunden", value="1,234")
metric_card(label="Rate", value="3.24%")

# ❌ Schlecht: Unformatierte Werte
metric_card(label="Umsatz", value="45231.5")
```

### 2. Trend-Labels

```python
# ✅ Gut: Aussagekräftige Trend-Labels
metric_card(
    label="Umsatz",
    value="€45K",
    trend=12.5,
    trend_label="+12.5% vs. letzter Monat"
)

# ✅ Auch gut: Nur Trend-Wert (wird automatisch formatiert)
metric_card(
    label="Umsatz",
    value="€45K",
    trend=12.5  # Zeigt "12.5%"
)
```

### 3. Icons

```python
# ✅ Gut: Passende Icons
metric_card(label="Umsatz", value="€45K", icon="💰")
metric_card(label="Kunden", value="1.2K", icon="👥")
metric_card(label="Bestellungen", value="3.4K", icon="📦")

# ✅ Auch gut: Ohne Icon
metric_card(label="Umsatz", value="€45K")
```

### 4. Größen

```python
# ✅ Gut: Größe passend zum Kontext
# Dashboard-Übersicht: medium
# Detailansicht: large
# Sidebar: small

# Dashboard
metric_card_group(metrics=[...], size="medium")

# Detailansicht
metric_card(label="Hauptmetrik", value="€45K", size="large")
```

### 5. Gruppen-Layout

```python
# ✅ Gut: 2-4 Spalten für Desktop
metric_card_group(metrics=[...], columns=3)  # Optimal
metric_card_group(metrics=[...], columns=4)  # Gut für viele Metriken

# ❌ Vermeiden: Zu viele Spalten
metric_card_group(metrics=[...], columns=6)  # Zu eng
```

## Integration mit Streamlit

### Mit Streamlit Columns

```python
col1, col2, col3 = st.columns(3)

with col1:
    metric_card(label="Metrik 1", value="€45K", trend=12.5)

with col2:
    metric_card(label="Metrik 2", value="1.2K", trend=-3.2)

with col3:
    metric_card(label="Metrik 3", value="3.4K", trend=5.7)
```

### Mit Streamlit Tabs

```python
tab1, tab2 = st.tabs(["Übersicht", "Details"])

with tab1:
    metric_card_group(
        metrics=[...],
        columns=4
    )

with tab2:
    metric_card(
        label="Detaillierte Metrik",
        value="€45,231.50",
        description="Vollständige Beschreibung",
        size="large"
    )
```

## Troubleshooting

### Problem: Metriken werden nicht angezeigt

**Lösung**: Stelle sicher, dass der ThemeManager initialisiert ist:

```python
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()
    st.session_state.theme_manager.set_theme('shadcn-default')

# CSS injizieren
css = st.session_state.theme_manager.generate_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

### Problem: Animationen funktionieren nicht

**Lösung**: Animationen werden nur beim ersten Laden ausgeführt. Verwende `st.rerun()` um sie erneut zu triggern:

```python
if st.button("Neu laden"):
    st.rerun()
```

### Problem: Trend-Farben sind falsch

**Lösung**: Überprüfe das Theme. Die Farben kommen aus `colors.success` und `colors.error`:

```python
# Im Theme JSON
{
  "colors": {
    "success": "#22c55e",  # Grün für positive Trends
    "error": "#ef4444"     # Rot für negative Trends
  }
}
```

## Related Components

- **Card**: Basis-Card-Komponente für allgemeine Inhalte
- **Badge**: Für Status-Anzeigen und Labels
- **Alert**: Für Benachrichtigungen und Warnungen

## See Also

- [Card Component Reference](CARD_REFERENCE.md)
- [Badge Component Reference](ALERT_BADGE_REFERENCE.md)
- [Theme System Reference](../theming/THEME_SELECTOR_REFERENCE.md)
