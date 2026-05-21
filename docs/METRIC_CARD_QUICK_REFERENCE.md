# MetricCard Quick Reference

## 📊 Übersicht

Die MetricCard-Komponente zeigt KPIs und wichtige Metriken im modernen shadcn/ui-Stil an.

## 🚀 Quick Start

```python
from components.metric_card import metric_card

metric_card(
    label="Umsatz",
    value="€45,231",
    trend=12.5,
    icon="💰"
)
```

## 📋 Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `label` | `str` | **Required** | Label der Metrik |
| `value` | `str` | **Required** | Wert (formatiert) |
| `trend` | `float` | `None` | Trend in % (+ = ↑, - = ↓) |
| `icon` | `str` | `None` | Icon (Emoji) |
| `size` | `str` | `"medium"` | `"small"`, `"medium"`, `"large"` |
| `variant` | `str` | `"default"` | `"default"`, `"outlined"`, `"elevated"` |

## 🎨 Größen

```python
# Small - Kompakt
metric_card(label="Besucher", value="12K", size="small")

# Medium - Standard
metric_card(label="Besucher", value="12K", size="medium")

# Large - Prominent
metric_card(label="Besucher", value="12K", size="large")
```

## 📈 Trends

```python
# Positiv (grün ↑)
metric_card(label="Umsatz", value="€45K", trend=12.5)

# Negativ (rot ↓)
metric_card(label="Kosten", value="€23K", trend=-5.2)

# Neutral (grau →)
metric_card(label="Stabil", value="100", trend=0)
```

## 🎯 Varianten

```python
# Default
metric_card(label="Metrik", value="123", variant="default")

# Outlined
metric_card(label="Metrik", value="123", variant="outlined")

# Elevated
metric_card(label="Metrik", value="123", variant="elevated")
```

## 📦 Gruppen

```python
from components.metric_card import metric_card_group

metric_card_group(
    metrics=[
        {"label": "Umsatz", "value": "€45K", "trend": 12.5, "icon": "💰"},
        {"label": "Kunden", "value": "1.2K", "trend": 8.2, "icon": "👥"},
        {"label": "Orders", "value": "3.4K", "trend": -3.1, "icon": "📦"}
    ],
    columns=3
)
```

## 🌞 Solar-Beispiele

```python
# Aktuelle Leistung
metric_card(
    label="Aktuelle Leistung",
    value="8.5 kW",
    description="Von 10 kW Nennleistung",
    trend=15.2,
    icon="☀️",
    size="large"
)

# Tagesertrag
metric_card(
    label="Heutige Erzeugung",
    value="42.3 kWh",
    trend=8.5,
    icon="⚡"
)

# CO₂-Einsparung
metric_card(
    label="CO₂ Einsparung",
    value="18.2 kg",
    trend=8.5,
    icon="🌱"
)

# Eigenverbrauch
metric_card(
    label="Eigenverbrauch",
    value="68%",
    trend=3.2,
    icon="🏠"
)
```

## 💡 Häufige Icons

| Icon | Verwendung |
|------|------------|
| 💰 | Umsatz, Geld |
| 👥 | Kunden, Benutzer |
| 📦 | Bestellungen, Produkte |
| 🎯 | Conversion, Ziele |
| 📈 | Wachstum, Trends |
| ⚡ | Leistung, Energie |
| ☀️ | Solar, Sonne |
| 🏠 | Eigenverbrauch, Haus |
| 🌱 | CO₂, Umwelt |
| ⭐ | Bewertung, Qualität |

## ✅ Best Practices

**Do:**
- ✅ Formatiere Werte (€45,231 statt 45231)
- ✅ Verwende aussagekräftige Trend-Labels
- ✅ Wähle passende Icons
- ✅ Nutze 2-4 Spalten für Gruppen

**Don't:**
- ❌ Unformatierte Werte
- ❌ Zu viele Spalten (> 4)
- ❌ Zu lange Labels

## 🎬 Demo

```bash
streamlit run demo_metric_card.py
```

## 📚 Weitere Dokumentation

- [Vollständige API-Referenz](../components/METRIC_CARD_REFERENCE.md)
- [Component Library](../components/README.md)
- [Theme System](../theming/THEME_SELECTOR_REFERENCE.md)
