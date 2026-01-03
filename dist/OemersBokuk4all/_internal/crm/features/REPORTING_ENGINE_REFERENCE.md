# CRM Reporting Engine - Referenz

## Übersicht

Das CRM Reporting Engine Modul bietet umfassende Reporting-Funktionen für das CRM-System.

## Features

### ✅ Vordefinierte Reports
- **Verkaufsübersicht**: Angebote nach Zeitraum mit Status-Tracking
- **Conversion Funnel**: Lead-Pipeline-Analyse mit Conversion-Raten
- **Lead-Quellen Analyse**: Performance nach Lead-Quelle

### ✅ Report Builder
- Flexible Tabellen-Auswahl
- Spalten-Auswahl
- Filter-Bedingungen
- Gruppierung und Aggregation
- Zeitraum-Filter
- Sortierung und Limits

### ✅ Visualisierungen
- Interaktive Plotly-Diagramme
- Bar Charts, Pie Charts, Funnel Charts
- Responsive und exportierbar

### ✅ Export-Funktionen
- Excel (.xlsx) mit Formatierung
- CSV für Datenanalyse
- HTML für Diagramme

### ✅ Report-Vorlagen
- Vorlagen speichern und wiederverwenden
- Vorlagen-Verwaltung
- Zuletzt verwendet Tracking

## Verwendung

### Basis-Verwendung

```python
from database import get_db_connection
from crm.features.reporting_engine import ReportingEngine

conn = get_db_connection()
engine = ReportingEngine(conn)

# Verkaufsübersicht
result = engine.get_sales_overview(
    start_date="2024-01-01",
    end_date="2024-12-31",
    period="monthly"
)
```


### Vordefinierte Reports

#### Verkaufsübersicht

```python
result = engine.get_sales_overview(
    start_date="2024-01-01",
    end_date="2024-12-31",
    period="monthly"  # 'daily', 'weekly', 'monthly'
)

if result["success"]:
    print(f"Gesamt Angebote: {result['summary']['total_offers']}")
    print(f"Conversion Rate: {result['summary']['conversion_rate']}%")
    
    # DataFrame mit Daten
    df = result["data"]
    
    # Plotly Chart
    chart = result["chart"]
```

#### Conversion Funnel

```python
result = engine.get_conversion_funnel(
    start_date="2024-01-01",
    end_date="2024-12-31"
)

if result["success"]:
    funnel = result["funnel_stages"]
    rates = result["conversion_rates"]
    
    print(f"Leads: {funnel['lead']}")
    print(f"Gewonnen: {funnel['won']}")
    print(f"Gesamt Conversion: {rates['overall_conversion']}%")
```

#### Lead-Quellen Analyse

```python
result = engine.get_lead_sources_report(
    start_date="2024-01-01",
    end_date="2024-12-31"
)

if result["success"]:
    df = result["data"]
    # Spalten: source, count, won_count, avg_value, conversion_rate
```

### Custom Report Builder

```python
result = engine.build_custom_report(
    table="customers",
    columns=["first_name", "last_name", "email", "creation_date"],
    filters={"city": "Berlin"},
    group_by=["city"],
    aggregations={"id": "COUNT"},
    start_date="2024-01-01",
    end_date="2024-12-31",
    order_by="creation_date DESC",
    limit=100
)

if result["success"]:
    df = result["data"]
    print(f"Zeilen: {result['row_count']}")
    print(f"Query: {result['query']}")
```

### Export-Funktionen

#### Excel Export

```python
df = result["data"]
excel_bytes = engine.export_to_excel(df, "report.xlsx")

# Speichern
with open("report.xlsx", "wb") as f:
    f.write(excel_bytes)

# Oder in Streamlit
st.download_button(
    label="Excel herunterladen",
    data=excel_bytes,
    file_name="report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
```

#### CSV Export

```python
csv_string = engine.export_to_csv(df)

# Speichern
with open("report.csv", "w") as f:
    f.write(csv_string)
```

#### Chart HTML Export

```python
chart = result["chart"]
html_string = engine.export_chart_to_html(chart)

with open("chart.html", "w") as f:
    f.write(html_string)
```

### Report-Vorlagen

#### Vorlage speichern

```python
config = {
    "table": "customers",
    "columns": ["first_name", "last_name", "email"],
    "filters": {"city": "Berlin"},
    "order_by": "last_name"
}

result = engine.save_report_template(
    name="Berlin Kunden",
    report_type="custom",
    config=config,
    description="Alle Kunden aus Berlin",
    created_by="Max Mustermann"
)

if result["success"]:
    template_id = result["template_id"]
```

#### Vorlage laden

```python
result = engine.load_report_template(template_id)

if result["success"]:
    template = result["template"]
    config = template["config"]
    
    # Report mit Vorlage ausführen
    report_result = engine.build_custom_report(**config)
```

#### Vorlagen auflisten

```python
templates = engine.list_report_templates()

for template in templates:
    print(f"{template['name']} ({template['report_type']})")
    print(f"  Erstellt: {template['created_at']}")
    print(f"  Zuletzt verwendet: {template['last_used']}")
```

#### Vorlage löschen

```python
result = engine.delete_report_template(template_id)

if result["success"]:
    print("Vorlage gelöscht")
```

## Hilfsfunktionen

### Verfügbare Tabellen

```python
from crm.features.reporting_engine import get_available_tables

tables = get_available_tables(conn)
print(tables)  # ['customers', 'projects', 'crm_leads', ...]
```

### Tabellen-Spalten

```python
from crm.features.reporting_engine import get_table_columns

columns = get_table_columns(conn, "customers")
print(columns)  # ['id', 'first_name', 'last_name', ...]
```

### Formatierung

```python
from crm.features.reporting_engine import format_currency, format_percentage

print(format_currency(25000.50))  # "€ 25.000,50"
print(format_percentage(42.5))     # "42,5%"
```

## Streamlit UI

```python
from crm.features.report_ui import render_reporting_ui

# In Streamlit App
render_reporting_ui()
```

Die UI bietet:
- Tab-Navigation für verschiedene Report-Typen
- Interaktive Zeitraum-Auswahl
- Visualisierungen mit Plotly
- Export-Buttons für Excel, CSV, HTML
- Vorlagen-Verwaltung

## Datenbank-Schema

### saved_reports Tabelle

```sql
CREATE TABLE saved_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    report_type TEXT NOT NULL,
    config TEXT NOT NULL,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    last_used TIMESTAMP
)
```

## Beispiel-Workflows

### Workflow 1: Monatlicher Verkaufsbericht

```python
# 1. Report generieren
result = engine.get_sales_overview(
    start_date="2024-01-01",
    end_date="2024-01-31",
    period="daily"
)

# 2. Excel exportieren
excel_bytes = engine.export_to_excel(result["data"])

# 3. Per E-Mail versenden (mit E-Mail-Manager)
from crm.features.email_manager import EmailManager
email_mgr = EmailManager(conn)

email_mgr.send_email(
    to="chef@firma.de",
    subject="Verkaufsbericht Januar 2024",
    body="Anbei der Verkaufsbericht für Januar.",
    attachments=[("verkaufsbericht.xlsx", excel_bytes)]
)
```

### Workflow 2: Wöchentliches Lead-Tracking

```python
# 1. Conversion Funnel
funnel = engine.get_conversion_funnel(
    start_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
    end_date=datetime.now().strftime("%Y-%m-%d")
)

# 2. Lead-Quellen
sources = engine.get_lead_sources_report(
    start_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
    end_date=datetime.now().strftime("%Y-%m-%d")
)

# 3. Zusammenfassung erstellen
summary = f"""
Wöchentliches Lead-Update:

Funnel:
- Neue Leads: {funnel['funnel_stages']['lead']}
- Gewonnen: {funnel['funnel_stages']['won']}
- Conversion Rate: {funnel['conversion_rates']['overall_conversion']:.1f}%

Top Lead-Quelle: {sources['data'].iloc[0]['source']}
"""

print(summary)
```

### Workflow 3: Custom Report als Vorlage

```python
# 1. Custom Report erstellen
config = {
    "table": "projects",
    "columns": ["project_name", "offer_status", "offer_value", "offer_sent_date"],
    "filters": {"offer_status": ["sent", "accepted"]},
    "order_by": "offer_sent_date DESC",
    "limit": 50
}

result = engine.build_custom_report(**config)

# 2. Als Vorlage speichern
template_result = engine.save_report_template(
    name="Aktive Angebote",
    report_type="custom",
    config=config,
    description="Alle versendeten und angenommenen Angebote"
)

# 3. Später wiederverwenden
template = engine.load_report_template(template_result["template_id"])
report = engine.build_custom_report(**template["template"]["config"])
```

## Best Practices

### Performance

1. **Zeitraum begrenzen**: Verwenden Sie sinnvolle Zeiträume
2. **Limit setzen**: Bei großen Datenmengen Limit verwenden
3. **Indizes nutzen**: Stellen Sie sicher, dass wichtige Spalten indiziert sind

### Datenqualität

1. **Validierung**: Prüfen Sie `result["success"]` vor Verwendung
2. **Fehlerbehandlung**: Behandeln Sie leere Resultate
3. **Datentypen**: Achten Sie auf korrekte Datums-Formate

### Vorlagen

1. **Beschreibungen**: Fügen Sie aussagekräftige Beschreibungen hinzu
2. **Naming**: Verwenden Sie klare, eindeutige Namen
3. **Wartung**: Löschen Sie ungenutzte Vorlagen regelmäßig

## Troubleshooting

### Problem: Keine Daten im Report

**Lösung**: 
- Prüfen Sie den Zeitraum
- Prüfen Sie Filter-Bedingungen
- Prüfen Sie ob Daten in der Tabelle existieren

### Problem: Export schlägt fehl

**Lösung**:
- Prüfen Sie ob pandas und openpyxl installiert sind
- Prüfen Sie Schreibrechte
- Prüfen Sie Dateiname auf ungültige Zeichen

### Problem: Chart wird nicht angezeigt

**Lösung**:
- Prüfen Sie ob plotly installiert ist
- Prüfen Sie Browser-Kompatibilität
- Prüfen Sie Datenformat

## Requirements

- Python 3.8+
- pandas
- plotly
- openpyxl (für Excel-Export)
- sqlite3 (Standard-Bibliothek)

## Testing

```bash
# Alle Tests ausführen
pytest crm/features/test_reporting_engine.py -v

# Spezifische Test-Klasse
pytest crm/features/test_reporting_engine.py::TestReportingEngine -v

# Mit Coverage
pytest crm/features/test_reporting_engine.py --cov=crm.features.reporting_engine
```

## Siehe auch

- [Task Manager Reference](TASK_MANAGER_TESTS_REFERENCE.md)
- [Email Manager Reference](EMAIL_MANAGER_TESTS_REFERENCE.md)
- [Offer Tracker Reference](OFFER_TRACKER_REFERENCE.md)
