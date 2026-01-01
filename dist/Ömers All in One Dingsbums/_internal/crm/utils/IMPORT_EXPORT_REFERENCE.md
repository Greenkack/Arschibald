# Import/Export Manager - Technical Reference

## Module Overview

**File:** `crm/utils/import_export_manager.py`  
**Purpose:** Kunden Import/Export mit CSV und Excel  
**Version:** 1.0  
**Author:** Kiro AI Assistant

---

## Constants

### CUSTOMER_FIELDS
Dictionary mit allen Kundenfeldern und deutschen Beschreibungen.

```python
CUSTOMER_FIELDS = {
    'id': 'ID',
    'salutation': 'Anrede',
    'title': 'Titel',
    'first_name': 'Vorname',
    'last_name': 'Nachname',
    'company_name': 'Firmenname',
    'address': 'Straße',
    'house_number': 'Hausnummer',
    'zip_code': 'PLZ',
    'city': 'Stadt',
    'state': 'Bundesland',
    'region': 'Region',
    'email': 'E-Mail',
    'phone_landline': 'Telefon (Festnetz)',
    'phone_mobile': 'Telefon (Mobil)',
    'income_tax_rate_percent': 'Einkommensteuersatz (%)',
    'creation_date': 'Erstellungsdatum',
    'last_updated': 'Letzte Aktualisierung'
}
```

### REQUIRED_FIELDS
Liste der Pflichtfelder für Import.

```python
REQUIRED_FIELDS = ['first_name', 'last_name']
```

### DUPLICATE_CHECK_FIELDS
Felder für Duplikatserkennung.

```python
DUPLICATE_CHECK_FIELDS = ['email', 'phone_mobile', 'phone_landline']
```

---

## Export Functions

### export_customers_to_csv()

Exportiert Kundendaten als CSV-String.

**Signatur:**
```python
def export_customers_to_csv(
    conn: sqlite3.Connection,
    include_fields: Optional[List[str]] = None,
    customer_ids: Optional[List[int]] = None
) -> str
```

**Parameter:**
- `conn`: Datenbankverbindung
- `include_fields`: Liste der zu exportierenden Felder (None = alle)
- `customer_ids`: Liste der zu exportierenden Kunden-IDs (None = alle)

**Returns:**
- CSV-String mit Kundendaten

**Beispiel:**
```python
conn = get_db_connection()
csv_data = export_customers_to_csv(
    conn,
    include_fields=['first_name', 'last_name', 'email'],
    customer_ids=[1, 2, 3]
)
```

---

### export_customers_to_excel()

Exportiert Kundendaten als Excel-Datei.

**Signatur:**
```python
def export_customers_to_excel(
    conn: sqlite3.Connection,
    filepath: str,
    include_fields: Optional[List[str]] = None,
    customer_ids: Optional[List[int]] = None
) -> bool
```

**Parameter:**
- `conn`: Datenbankverbindung
- `filepath`: Pfad zur Excel-Datei
- `include_fields`: Liste der zu exportierenden Felder (None = alle)
- `customer_ids`: Liste der zu exportierenden Kunden-IDs (None = alle)

**Returns:**
- True bei Erfolg, False bei Fehler

**Beispiel:**
```python
success = export_customers_to_excel(
    conn,
    'kunden_export.xlsx',
    include_fields=['first_name', 'last_name', 'email']
)
```

---

### get_export_statistics()

Gibt Statistiken über exportierbare Daten zurück.

**Signatur:**
```python
def get_export_statistics(conn: sqlite3.Connection) -> Dict[str, Any]
```

**Returns:**
```python
{
    'total_customers': int,
    'customers_with_email': int,
    'customers_with_phone': int,
    'customers_with_company': int,
    'completeness_rate': float
}
```

**Beispiel:**
```python
stats = get_export_statistics(conn)
print(f"Gesamt: {stats['total_customers']}")
print(f"Vollständigkeit: {stats['completeness_rate']}%")
```

---

## Import Parsing Functions

### parse_csv_for_import()

Parst CSV-Inhalt und gibt Header, Daten und Fehler zurück.

**Signatur:**
```python
def parse_csv_for_import(
    csv_content: str,
    delimiter: str = ',',
    encoding: str = 'utf-8'
) -> Tuple[List[str], List[List[str]], List[str]]
```

**Parameter:**
- `csv_content`: CSV-Inhalt als String
- `delimiter`: CSV-Trennzeichen (Standard: ',')
- `encoding`: Zeichenkodierung (Standard: 'utf-8')

**Returns:**
- Tuple: (header, rows, errors)

**Beispiel:**
```python
csv_content = """Vorname,Nachname,E-Mail
Max,Mustermann,max@example.com"""

header, rows, errors = parse_csv_for_import(csv_content)
```

---

### parse_excel_for_import()

Parst Excel-Datei und gibt Header, Daten und Fehler zurück.

**Signatur:**
```python
def parse_excel_for_import(
    filepath: str,
    sheet_name: Optional[str] = None
) -> Tuple[List[str], List[List[Any]], List[str]]
```

**Parameter:**
- `filepath`: Pfad zur Excel-Datei
- `sheet_name`: Name des Sheets (None = erstes Sheet)

**Returns:**
- Tuple: (header, rows, errors)

**Beispiel:**
```python
header, rows, errors = parse_excel_for_import(
    'kunden.xlsx',
    sheet_name='Kunden'
)
```

---

### get_excel_sheet_names()

Gibt alle Sheet-Namen einer Excel-Datei zurück.

**Signatur:**
```python
def get_excel_sheet_names(filepath: str) -> List[str]
```

**Beispiel:**
```python
sheet_names = get_excel_sheet_names('kunden.xlsx')
# → ['Sheet1', 'Kunden', 'Archiv']
```

---

## Field Mapping Functions

### map_import_fields()

Erstellt Mapping zwischen Import-Spalten und Datenbankfeldern.

**Signatur:**
```python
def map_import_fields(
    import_header: List[str],
    field_mapping: Optional[Dict[str, str]] = None
) -> Dict[str, str]
```

**Parameter:**
- `import_header`: Header aus Import-Datei
- `field_mapping`: Optionales manuelles Mapping

**Returns:**
- Dictionary: {import_column: db_field}

**Beispiel:**
```python
# Automatisches Mapping
header = ['Vorname', 'Nachname', 'E-Mail']
mapping = map_import_fields(header)
# → {'Vorname': 'first_name', 'Nachname': 'last_name', 'E-Mail': 'email'}

# Manuelles Mapping
manual = {'Name': 'first_name', 'Surname': 'last_name'}
mapping = map_import_fields(header, manual)
```

**Mapping-Logik:**
1. Direkte Übereinstimmung mit deutschen Beschreibungen
2. Direkte Übereinstimmung mit englischen Feldnamen
3. Teilübereinstimmungen (Keywords)
4. Manuelles Mapping überschreibt automatisches

---

## Duplicate Detection Functions

### check_duplicate_customer()

Prüft, ob ein Kunde bereits existiert.

**Signatur:**
```python
def check_duplicate_customer(
    conn: sqlite3.Connection,
    customer_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]
```

**Parameter:**
- `conn`: Datenbankverbindung
- `customer_data`: Kundendaten zum Prüfen

**Returns:**
- Existierender Kunde als Dictionary oder None

**Beispiel:**
```python
customer_data = {
    'first_name': 'Max',
    'last_name': 'Mustermann',
    'email': 'max@example.com'
}

duplicate = check_duplicate_customer(conn, customer_data)
if duplicate:
    print(f"Duplikat gefunden: ID {duplicate['id']}")
```

**Erkennungs-Reihenfolge:**
1. E-Mail-Adresse (höchste Priorität)
2. Mobiltelefon
3. Festnetz-Telefon
4. Name + PLZ (Fallback)

---

## Validation Functions

### validate_customer_data()

Validiert Kundendaten vor dem Import.

**Signatur:**
```python
def validate_customer_data(customer_data: Dict[str, Any]) -> List[str]
```

**Parameter:**
- `customer_data`: Zu validierende Kundendaten

**Returns:**
- Liste von Fehlermeldungen (leer = valide)

**Beispiel:**
```python
customer_data = {
    'first_name': 'Max',
    'email': 'invalid-email'
}

errors = validate_customer_data(customer_data)
# → ['Pflichtfeld fehlt: Nachname', 'Ungültiges E-Mail-Format: invalid-email']
```

**Validierungs-Regeln:**
- Pflichtfelder: first_name, last_name
- E-Mail-Format: muss @ und . enthalten
- PLZ-Format: 5-stellig, numerisch
- Steuersatz: 0-100%

---

## Import Functions

### import_customer()

Importiert einen einzelnen Kunden.

**Signatur:**
```python
def import_customer(
    conn: sqlite3.Connection,
    customer_data: Dict[str, Any],
    duplicate_action: str = 'skip'
) -> Tuple[bool, Optional[int], str]
```

**Parameter:**
- `conn`: Datenbankverbindung
- `customer_data`: Kundendaten
- `duplicate_action`: Aktion bei Duplikat ('skip', 'update', 'create')

**Returns:**
- Tuple: (success, customer_id, message)

**Beispiel:**
```python
customer_data = {
    'first_name': 'Max',
    'last_name': 'Mustermann',
    'email': 'max@example.com'
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

**Duplikat-Aktionen:**
- `'skip'`: Duplikate werden nicht importiert
- `'update'`: Existierende Kunden werden aktualisiert
- `'create'`: Duplikate werden trotzdem erstellt

---

### import_customers_batch()

Importiert mehrere Kunden auf einmal.

**Signatur:**
```python
def import_customers_batch(
    conn: sqlite3.Connection,
    rows: List[List[Any]],
    field_mapping: Dict[str, str],
    duplicate_action: str = 'skip'
) -> Dict[str, Any]
```

**Parameter:**
- `conn`: Datenbankverbindung
- `rows`: Liste von Datenzeilen
- `field_mapping`: Mapping zwischen Import-Spalten und DB-Feldern
- `duplicate_action`: Aktion bei Duplikat

**Returns:**
```python
{
    'total': int,           # Gesamtanzahl Zeilen
    'success': int,         # Erfolgreich importiert
    'skipped': int,         # Übersprungen (Duplikate)
    'updated': int,         # Aktualisiert
    'errors': int,          # Fehler
    'error_details': List[str]  # Fehlerdetails
}
```

**Beispiel:**
```python
rows = [
    ['Max', 'Mustermann', 'max@example.com'],
    ['Erika', 'Musterfrau', 'erika@example.com']
]

field_mapping = {
    'Vorname': 'first_name',
    'Nachname': 'last_name',
    'E-Mail': 'email'
}

stats = import_customers_batch(conn, rows, field_mapping, 'skip')
print(f"Erfolgreich: {stats['success']}")
print(f"Fehler: {stats['errors']}")
```

---

### update_customer_from_import()

Aktualisiert einen existierenden Kunden mit Import-Daten.

**Signatur:**
```python
def update_customer_from_import(
    conn: sqlite3.Connection,
    customer_id: int,
    customer_data: Dict[str, Any]
) -> Tuple[bool, int, str]
```

**Parameter:**
- `conn`: Datenbankverbindung
- `customer_id`: ID des zu aktualisierenden Kunden
- `customer_data`: Neue Kundendaten

**Returns:**
- Tuple: (success, customer_id, message)

---

## Preview Functions

### preview_import_data()

Erstellt eine Vorschau der zu importierenden Daten.

**Signatur:**
```python
def preview_import_data(
    rows: List[List[Any]],
    field_mapping: Dict[str, str],
    max_rows: int = 10
) -> List[Dict[str, Any]]
```

**Parameter:**
- `rows`: Datenzeilen
- `field_mapping`: Feld-Mapping
- `max_rows`: Maximale Anzahl Zeilen für Vorschau

**Returns:**
- Liste von Dictionaries mit Vorschaudaten

**Beispiel:**
```python
preview = preview_import_data(rows, field_mapping, max_rows=5)
for customer in preview:
    print(customer)
```

---

## Utility Functions

### get_available_db_fields()

Gibt alle verfügbaren Datenbankfelder mit deutschen Beschreibungen zurück.

**Signatur:**
```python
def get_available_db_fields() -> Dict[str, str]
```

**Returns:**
- Dictionary: {db_field: german_description}

---

### get_required_fields()

Gibt Liste der Pflichtfelder zurück.

**Signatur:**
```python
def get_required_fields() -> List[str]
```

**Returns:**
- Liste der Pflichtfelder

---

### format_import_statistics()

Formatiert Import-Statistiken als lesbaren Text.

**Signatur:**
```python
def format_import_statistics(stats: Dict[str, Any]) -> str
```

**Parameter:**
- `stats`: Statistik-Dictionary

**Returns:**
- Formatierter Text

**Beispiel:**
```python
stats = import_customers_batch(conn, rows, field_mapping, 'skip')
formatted = format_import_statistics(stats)
print(formatted)
```

**Output:**
```
Import abgeschlossen:
  Gesamt: 100 Zeilen
  ✓ Erfolgreich importiert: 85
  ↻ Aktualisiert: 0
  ⊘ Übersprungen (Duplikate): 10
  ✗ Fehler: 5

Fehlerdetails:
  • Zeile 15: Pflichtfeld fehlt: Nachname
  • Zeile 23: Ungültige PLZ: 123
  ...
```

---

## Error Handling

Alle Funktionen verwenden Try-Except-Blöcke und geben aussagekräftige Fehlermeldungen zurück.

**Fehlertypen:**
- Validierungsfehler (Pflichtfelder, Formate)
- Duplikatsfehler (bei 'skip'-Modus)
- Datenbankfehler (SQL-Fehler)
- Parsing-Fehler (CSV/Excel)

**Best Practice:**
```python
try:
    success, customer_id, message = import_customer(conn, data, 'skip')
    if success:
        print(f"Erfolg: {message}")
    else:
        print(f"Warnung: {message}")
except Exception as e:
    print(f"Fehler: {str(e)}")
```

---

## Dependencies

**Standard Library:**
- `csv`: CSV-Verarbeitung
- `io`: String-IO
- `sqlite3`: Datenbankzugriff
- `datetime`: Zeitstempel
- `typing`: Type Hints

**External:**
- `pandas`: Excel-Verarbeitung
- `openpyxl`: Excel-Engine

**Installation:**
```bash
pip install pandas openpyxl
```

---

## Performance Considerations

**Optimierungen:**
- Batch-Import statt Einzelimport
- Effiziente SQL-Queries
- Pandas für Excel-Verarbeitung
- Indizes auf E-Mail und Telefon

**Benchmarks:**
- CSV-Export: ~2.000 Kunden/Sekunde
- Excel-Export: ~833 Kunden/Sekunde
- CSV-Import: ~400 Kunden/Sekunde
- Excel-Import: ~333 Kunden/Sekunde

---

## Testing

**Test-Datei:** `crm/utils/test_import_export_manager.py`

**Test-Kategorien:**
- Export-Tests (CSV, Excel)
- Import-Parsing-Tests
- Feld-Mapping-Tests
- Duplikatserkennung-Tests
- Validierungs-Tests
- Import-Tests
- Integration-Tests

**Ausführen:**
```bash
pytest crm/utils/test_import_export_manager.py -v
```

---

## See Also

- **UI-Modul:** `crm/utils/import_export_ui.py`
- **Quick Reference:** `docs/IMPORT_EXPORT_QUICK_REFERENCE.md`
- **Task Summary:** `TASK_13_IMPORT_EXPORT_COMPLETE.md`
- **Requirements:** `.kiro/specs/crm-system-enhancement/requirements.md` (Requirement 12)
