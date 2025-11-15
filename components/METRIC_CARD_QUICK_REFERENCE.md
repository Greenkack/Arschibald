# MetricCard Quick Reference

## Import

```python
from components.metric_card import metric_card, metric_card_group
```

## Basic Usage

```python
# Einfache Metrik
metric_card(
    label="Umsatz",
    value="€45,231",
    icon="💰"
)

# Mit Trend
metric_card(
    label="Neue Kunden",
    value="1,234",
    trend=12.5,
    trend_label="+12.5% vs. letzter Monat",
    icon="👥"
)

# Gruppe
metric_card_group(
    metrics=[
        {"label": "Umsatz", "value": "€45K", "trend": 12.5, "icon": "💰"},
        {"label": "Kunden", "value": "1.2K", "trend": -3.2, "icon": "👥"}
    ],
    columns=2
)
```

## Parameters

### metric_card()

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str` | Required | Label der Metrik |
| `value` | `str` | Required | Wert (formatiert) |
| `trend` | `float` | `None` | Trend in % (+ = grün ↑, - = rot ↓) |
| `icon` | `str` | `None` | Icon (Emoji) |
| `size` | `str` | `"medium"` | `"small"`, `"medium"`, `"large"` |
| `variant` | `str` | `"default"` | `"default"`, `"outlined"`, `"elevated"` |

### metric_card_group()

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `metrics` | `list[dict]` | Required | Liste von Metric-Configs |
| `columns` | `int` | `3` | Anzahl Spalten |
| `gap` | `str` | `"md"` | `"sm"`, `"md"`, `"lg"` |

## Examples

### Größen

```python
metric_card(label="Small", value="€45K", size="small")
metric_card(label="Medium", value="€45K", size="medium")
metric_card(label="Large", value="€45K", size="large")
```

### Varianten

```python
metric_card(label="Default", value="€45K", variant="default")
metric_card(label="Outlined", value="€45K", variant="outlined")
metric_card(label="Elevated", value="€45K", variant="elevated")
```

### Mit Beschreibung

```python
metric_card(
    label="Durchschnittlicher Bestellwert",
    value="€127.50",
    description="Basierend auf 1,234 Bestellungen",
    trend=5.3,
    icon="🛒"
)
```

### Dashboard

```python
metric_card_group(
    metrics=[
        {
            "label": "Umsatz",
            "value": "€245K",
            "trend": 12.5,
            "icon": "💰"
        },
        {
            "label": "Kunden",
            "value": "1.2K",
            "trend": 8.2,
            "icon": "👥"
        },
        {
            "label": "Bestellungen",
            "value": "3.4K",
            "trend": -3.1,
            "icon": "📦"
        }
    ],
    columns=3,
    variant="elevated"
)
```

## Trend-Logik

| Wert | Farbe | Pfeil |
|------|-------|-------|
| `> 0` | Grün | ↑ |
| `< 0` | Rot | ↓ |
| `= 0` | Grau | → |

## Common Icons

- 💰 Umsatz/Geld
- 👥 Kunden/Benutzer
- 📦 Bestellungen/Produkte
- 🎯 Conversion/Ziele
- 📈 Wachstum/Trends
- ⚡ Leistung/Energie
- ☀️ Solar/Sonne
- 🏠 Eigenverbrauch/Haus
- 🌱 CO₂/Umwelt

## Tips

✅ **Do:**
- Formatiere Werte (€45,231 statt 45231)
- Verwende aussagekräftige Trend-Labels
- Wähle passende Icons
- Nutze 2-4 Spalten für Gruppen

❌ **Don't:**
- Unformatierte Werte
- Zu viele Spalten (> 4)
- Zu lange Labels

## Demo

```bash
streamlit run demo_metric_card.py
```
