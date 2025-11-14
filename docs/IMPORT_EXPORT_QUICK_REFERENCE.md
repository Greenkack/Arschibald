# Kunden Import/Export - Quick Reference

## Übersicht

Das Import/Export-System ermöglicht den einfachen Austausch von Kundendaten zwischen der CRM-Anwendung und externen Systemen.

**Unterstützte Formate:**
- CSV (Comma-Separated Values)
- Excel (.xlsx)

**Hauptfunktionen:**
- ✅ Export aller oder ausgewählter Kunden
- ✅ Import mit automatischer Feld-Zuordnung
- ✅ Duplikatserkennung
- ✅ Datenvalidierung
- ✅ Vorschau vor Import

---

## Export

### CSV-Export

```python
from database import get_db_connection
from crm.utils.import_export_manager import export_customers_to_csv

conn = get_db_connection()

# Alle Kunden exportieren
csv_data = export_customers_to_csv(conn)

# Nur bestimmte Felder exportieren
csv_data = export_customers_to_csv(
    conn,
    include_fields=['first_name', 'last_name', 'email']
)

# Nur bestimmte Kunden exportieren
csv_data = export_customers_to_csv(
    conn,
    customer_ids=[1, 2, 3]
)
```

### Excel-Export

```python
from crm.utils.import_export_manager import export_customers_to_excel

# Export in Excel-Datei
success = export_customers_to_excel(
    conn,
    filepath='kunden_export.xlsx',
    include_fields=['first_name', 'last_name', 'email', 'phone_mobile']
)
```

### Export-Statistiken

```python
from crm.utils.import_export_manager import get_export_statistics

stats = get_export_statistics(conn)
print(f"Gesamt: {stats['total_customers']}")
print(f"Mit E-Mail: {stats['customers_with_email']}")
print(f"Vollständigkeit: {stats['completeness_rate']}%")
```

---

## Import

### CSV-Import

```python
from crm.utils.import_export_manager import (
    parse_csv_for_import,
    map_import_fields,
    import_customers_batch
)

# 1. CSV parsen
csv_content = """Vorname,Nachname,E-Mail
Max,Mustermann,max@example.com
Erika,Musterfrau,erika@example.com"""

header, rows, errors = parse_csv_for_import(csv_content)

# 2. Felder zuordnen (automatisch)
field_mapping = map_import_fields(header)

# 3. Import durchführen
stats = import_customers_batch(
    conn,
    rows,
    field_mapping,
    duplicate_action='skip'  # 'skip', 'update', oder 'create'
)

print(f"Erfolgreich: {stats['success']}")
print(f"Übersprungen: {stats['skipped']}")
print(f"Fehler: {stats['errors']}")
```

### Excel-Import

```python
from crm.utils.import_export_manager import (
    parse_excel_for_import,
    get_excel_sheet_names
)

# Sheet-Namen abrufen
sheet_names = get_excel_sheet_names('kunden.xlsx')

# Excel parsen
header, rows, errors = parse_excel_for_import(
    'kunden.xlsx',
    sheet_name='Kunden'  # Optional
)

# Weiter wie bei CSV-Import
field_mapping = map_import_fields(header)
stats = import_customers_batch(conn, rows, field_mapping, 'skip')
```

### Einzelkunden-Import

```python
from crm.utils.import_export_manager import import_customer

customer_data = {
    'first_name': 'Max',
    'last_name': 'Mustermann',
    'email': 'max@example.com',
    'phone_mobile': '0171234567',
    'zip_code': '12345',
    'city': 'Musterstadt'
}

success, customer_id, message = import_customer(
    conn,
    customer_data,
    duplicate_action='skip'
)

if success:
    print(f"Kunde importiert: ID {customer_id}")
else:
    print(f"Fehler: {message}")
```

---

## Duplikatserkennung

Duplikate werden automatisch erkannt über:

1. **E-Mail-Adresse** (höchste Priorität)
2. **Mobiltelefon**
3. **Festnetz-Telefon**
4. **Name + PLZ** (schwächere Erkennung)

### Duplikat-Aktionen

```python
# Überspringen (Standard)
duplicate_action='skip'  # Duplikate werden nicht importiert

# Aktualisieren
duplicate_action='update'  # Existierende Kunden werden aktualisiert

# Neu erstellen
duplicate_action='create'  # Duplikate werden trotzdem erstellt
```

### Manuelle Duplikatsprüfung

```python
from crm.utils.import_export_manager import check_duplicate_customer

customer_data = {
    'first_name': 'Max',
    'last_name': 'Mustermann',
    'email': 'max@example.com'
}

duplicate = check_duplicate_customer(conn, customer_data)

if duplicate:
    print(f"Duplikat gefunden: ID {duplicate['id']}")
else:
    print("Kein Duplikat gefunden")
```

---

## Datenvalidierung

### Automatische Validierung

```python
from crm.utils.import_export_manager import validate_customer_data

customer_data = {
    'first_name': 'Max',
    'last_name': 'Mustermann',
    'email': 'invalid-email',  # Ungültig
    'zip_code': '123'  # Zu kurz
}

errors = validate_customer_data(customer_data)

if errors:
    for error in errors:
        print(f"Fehler: {error}")
```

### Validierungsregeln

**Pflichtfelder:**
- `first_name` (Vorname)
- `last_name` (Nachname)

**Format-Validierung:**
- E-Mail: Muss @ und . enthalten
- PLZ: Muss 5-stellig und numerisch sein
- Steuersatz: Muss zwischen 0 und 100 liegen

---

## Feld-Mapping

### Automatisches Mapping

Das System erkennt automatisch deutsche und englische Feldnamen:

```python
from crm.utils.import_export_manager import map_import_fields

# Deutsche Feldnamen
header = ['Vorname', 'Nachname', 'E-Mail', 'PLZ', 'Stadt']
mapping = map_import_fields(header)
# → {'Vorname': 'first_name', 'Nachname': 'last_name', ...}

# Englische Feldnamen
header = ['first_name', 'last_name', 'email', 'zip_code', 'city']
mapping = map_import_fields(header)
# → {'first_name': 'first_name', 'last_name': 'last_name', ...}
```

### Manuelles Mapping

```python
# Eigene Zuordnung definieren
manual_mapping = {
    'Name': 'first_name',
    'Surname': 'last_name',
    'Mail': 'email',
    'Postcode': 'zip_code'
}

mapping = map_import_fields(header, manual_mapping)
```

### Verfügbare Felder

```python
from crm.utils.import_export_manager import get_available_db_fields

fields = get_available_db_fields()
# → {'first_name': 'Vorname', 'last_name': 'Nachname', ...}
```

---

## Import-Vorschau

```python
from crm.utils.import_export_manager import preview_import_data

# Vorschau der ersten 10 Zeilen
preview = preview_import_data(
    rows,
    field_mapping,
    max_rows=10
)

for customer in preview:
    print(customer)
```

---

## UI-Integration

### In Admin-Panel einbinden

```python
# In admin_panel.py
from crm.utils.import_export_ui import render_import_export_ui

# Im Admin-Panel-Menü
if menu_selection == "Import/Export":
    render_import_export_ui()
```

### Standalone-Nutzung

```python
# Direkt ausführen
from crm.utils.import_export_ui import render_import_export_ui

render_import_export_ui()
```

---

## Fehlerbehandlung

### Import-Fehler

```python
stats = import_customers_batch(conn, rows, field_mapping, 'skip')

if stats['errors'] > 0:
    print(f"{stats['errors']} Fehler aufgetreten:")
    for error in stats['error_details']:
        print(f"  - {error}")
```

### Export-Fehler

```python
csv_data = export_customers_to_csv(conn)

if not csv_data:
    print("Export fehlgeschlagen")
else:
    print(f"Export erfolgreich: {len(csv_data)} Bytes")
```

---

## Best Practices

### Export

1. **Feldauswahl**: Exportieren Sie nur benötigte Felder
2. **Datenschutz**: Achten Sie auf sensible Daten
3. **Regelmäßige Backups**: Nutzen Sie Export für Datensicherung

### Import

1. **Vorschau prüfen**: Immer Vorschau vor Import ansehen
2. **Duplikat-Strategie**: Wählen Sie passende Duplikat-Aktion
3. **Kleine Batches**: Bei großen Datenmengen in Teilen importieren
4. **Validierung**: Prüfen Sie Daten vor Import

### Feld-Mapping

1. **Automatik nutzen**: Verwenden Sie Standard-Feldnamen
2. **Dokumentation**: Dokumentieren Sie eigene Mappings
3. **Konsistenz**: Verwenden Sie einheitliche Feldnamen

---

## Beispiel-Workflows

### Workflow 1: Kunden aus Excel importieren

```python
# 1. Excel-Datei hochladen (in Streamlit)
uploaded_file = st.file_uploader("Excel-Datei", type=['xlsx'])

# 2. Parsen
header, rows, errors = parse_excel_for_import(uploaded_file.name)

# 3. Mapping
mapping = map_import_fields(header)

# 4. Vorschau
preview = preview_import_data(rows, mapping, max_rows=5)
st.dataframe(preview)

# 5. Import
if st.button("Import starten"):
    stats = import_customers_batch(conn, rows, mapping, 'skip')
    st.success(f"Import abgeschlossen: {stats['success']} Kunden importiert")
```

### Workflow 2: Kunden nach CSV exportieren

```python
# 1. Felder auswählen
fields = ['first_name', 'last_name', 'email', 'phone_mobile', 'city']

# 2. Export
csv_data = export_customers_to_csv(conn, include_fields=fields)

# 3. Download anbieten (in Streamlit)
st.download_button(
    label="CSV herunterladen",
    data=csv_data,
    file_name="kunden_export.csv",
    mime="text/csv"
)
```

### Workflow 3: Duplikate aktualisieren

```python
# Import mit Update-Strategie
stats = import_customers_batch(
    conn,
    rows,
    field_mapping,
    duplicate_action='update'
)

print(f"Aktualisiert: {stats['updated']}")
print(f"Neu erstellt: {stats['success']}")
```

---

## Troubleshooting

### Problem: Import schlägt fehl

**Lösung:**
1. Prüfen Sie Pflichtfelder (Vorname, Nachname)
2. Validieren Sie E-Mail-Format
3. Prüfen Sie PLZ-Format (5-stellig)

### Problem: Duplikate werden nicht erkannt

**Lösung:**
1. Prüfen Sie E-Mail-Adresse
2. Prüfen Sie Telefonnummern
3. Verwenden Sie Name + PLZ als Fallback

### Problem: Feld-Mapping funktioniert nicht

**Lösung:**
1. Verwenden Sie Standard-Feldnamen
2. Definieren Sie manuelles Mapping
3. Prüfen Sie Groß-/Kleinschreibung

---

## Performance-Tipps

1. **Batch-Import**: Nutzen Sie `import_customers_batch()` statt Einzelimport
2. **Feldauswahl**: Exportieren Sie nur benötigte Felder
3. **Indizes**: Datenbank-Indizes auf E-Mail und Telefon verbessern Duplikatserkennung
4. **Große Dateien**: Teilen Sie große Imports in kleinere Batches

---

## Weitere Informationen

- **Modul**: `crm/utils/import_export_manager.py`
- **UI**: `crm/utils/import_export_ui.py`
- **Tests**: `crm/utils/test_import_export_manager.py`
- **Requirements**: Requirement 12 (Requirements-Dokument)
