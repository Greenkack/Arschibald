# CRM Reporting - Quick Reference

## 🚀 Schnellstart

```python
from database import get_db_connection
from crm.features.reporting_engine import ReportingEngine

conn = get_db_connection()
engine = ReportingEngine(conn)
```

## 📊 Vordefinierte Reports

### Verkaufsübersicht

```python
result = engine.get_sales_overview(
    start_date="2024-01-01",
    end_date="2024-12-31",
    period="monthly"  # daily, weekly, monthly
)
```

**Rückgabe:**
- `summary`: Zusammenfassung (total_offers, accepted_offers, conversion_rate, etc.)
- `data`: DataFrame mit allen Angeboten
- `chart`: Plotly Visualisierung

### Conversion Funnel

```python
result = engine.get_conversion_funnel(
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

**Rückgabe:**
- `funnel_stages`: Dict mit Anzahl pro Stufe
- `conversion_rates`: Dict mit Conversion-Raten
- `chart`: Funnel-Diagramm

### Lead-Quellen

```python
result = engine.get_lead_sources_report(
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

**Rückgabe:**
- `data`: DataFrame mit Quellen-Statistiken
- `chart`: Pie + Bar Chart

## 🔧 Custom Reports

```python
result = engine.build_custom_report(
    table="customers",
    columns=["first_name", "last_name", "email"],
    filters={"city": "Berlin"},
    group_by=["city"],
    aggregations={"id": "COUNT"},
    start_date="2024-01-01",
    end_date="2024-12-31",
    order_by="last_name",
    limit=100
)
```

## 📥 Export

### Excel

```python
excel_bytes = engine.export_to_excel(df, "report.xlsx")
```

### CSV

```python
csv_string = engine.export_to_csv(df)
```

### Chart HTML

```python
html_string = engine.export_chart_to_html(chart)
```

## 💾 Vorlagen

### Speichern

```python
result = engine.save_report_template(
    name="Mein Report",
    report_type="custom",
    config={...},
    description="Beschreibung"
)
template_id = result["template_id"]
```

### Laden

```python
result = engine.load_report_template(template_id)
config = result["template"]["config"]
```

### Auflisten

```python
templates = engine.list_report_templates()
```

### Löschen

```python
result = engine.delete_report_template(template_id)
```

## 🎨 Streamlit UI

```python
from crm.features.report_ui import render_reporting_ui

render_reporting_ui()
```

## 🛠️ Hilfsfunktionen

```python
from crm.features.reporting_engine import (
    get_available_tables,
    get_table_columns,
    format_currency,
    format_percentage
)

tables = get_available_tables(conn)
columns = get_table_columns(conn, "customers")
print(format_currency(25000))      # € 25.000,00
print(format_percentage(42.5))     # 42,5%
```

## 📋 Verfügbare Tabellen

- `customers` - Kundendaten
- `projects` - Projekte mit Angeboten
- `crm_leads` - Pipeline Leads
- `crm_tasks` - Aufgaben
- `crm_activities` - Notizen & Historie
- `crm_reminders` - Erinnerungen

## 🎯 Häufige Use Cases

### Monatsbericht

```python
result = engine.get_sales_overview(
    start_date="2024-01-01",
    end_date="2024-01-31",
    period="daily"
)
excel = engine.export_to_excel(result["data"])
```

### Pipeline-Analyse

```python
funnel = engine.get_conversion_funnel(
    start_date="2024-01-01",
    end_date="2024-12-31"
)
print(f"Conversion: {funnel['conversion_rates']['overall_conversion']:.1f}%")
```

### Top Kunden

```python
result = engine.build_custom_report(
    table="projects",
    columns=["customer_id", "offer_value"],
    group_by=["customer_id"],
    aggregations={"offer_value": "SUM"},
    order_by="offer_value_sum DESC",
    limit=10
)
```

## ⚡ Performance-Tipps

1. **Zeitraum begrenzen** - Nicht mehr als 1 Jahr auf einmal
2. **Limit verwenden** - Bei großen Datenmengen
3. **Indizes prüfen** - Wichtige Spalten sollten indiziert sein
4. **Filter nutzen** - Reduziert Datenmenge

## 🐛 Troubleshooting

| Problem | Lösung |
|---------|--------|
| Keine Daten | Zeitraum/Filter prüfen |
| Export fehlschlägt | openpyxl installieren |
| Chart nicht sichtbar | plotly installieren |
| Langsam | Zeitraum/Limit reduzieren |

## 📦 Dependencies

```bash
pip install pandas plotly openpyxl
```

## 🧪 Testing

```bash
pytest crm/features/test_reporting_engine.py -v
```

## 📚 Weitere Infos

Siehe [REPORTING_ENGINE_REFERENCE.md](../crm/features/REPORTING_ENGINE_REFERENCE.md)
