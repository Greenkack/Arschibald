# Admin Matrix Upload - Quick Reference

## Schnellstart

### Upload-UI im Admin Panel

```python
from admin_price_matrix_upload import render_matrix_upload_ui

render_matrix_upload_ui()
```

### Matrix-Liste anzeigen

```python
from admin_price_matrix_upload import render_matrix_list_ui

render_matrix_list_ui()
```

### Datei programmatisch validieren

```python
from admin_price_matrix_upload import validate_uploaded_file

with open('matrix.csv', 'rb') as f:
    result = validate_uploaded_file(f.read(), 'csv')

if result['valid']:
    print("✓ Gültig")
else:
    for error in result['errors']:
        print(f"✗ {error}")
```

## Validierungsregeln

| Regel | Beschreibung | Beispiel |
|-------|--------------|----------|
| **Index numerisch** | Erste Spalte = Modulanzahl | `10, 15, 20` |
| **Spaltenüberschriften** | Alle Spalten benannt | `10kWh, 15kWh` |
| **"Ohne Speicher"** | Mind. 1 Spalte | `Ohne Speicher` |
| **Preise numerisch** | Alle Preise = Zahlen | `15000.00` |

## Gültige Matrix-Struktur

```csv
Anzahl Module;10kWh;15kWh;Ohne Speicher
10;15000.00;17500.00;12000.00
15;18000.00;20500.00;15000.00
20;21000.00;23500.00;18000.00
```

## Häufige Fehler

### ✗ Nicht-numerischer Index
```csv
ABC;15000.00;12000.00  ← Fehler: "ABC" ist keine Zahl
```

**Lösung:** Verwende Zahlen: `10;15000.00;12000.00`

### ✗ Fehlende "Ohne Speicher" Spalte
```csv
Anzahl Module;10kWh;15kWh  ← Fehler: Keine "Ohne Speicher" Spalte
```

**Lösung:** Füge Spalte hinzu: `Anzahl Module;10kWh;15kWh;Ohne Speicher`

### ✗ Nicht-numerische Preise
```csv
10;ABC;12000.00  ← Fehler: "ABC" ist keine Zahl
```

**Lösung:** Verwende Zahlen: `10;15000.00;12000.00`

## API-Funktionen

### `validate_uploaded_file(file_content, file_type)`

**Parameter:**
- `file_content`: bytes
- `file_type`: 'csv' oder 'excel'

**Returns:**
```python
{
    'valid': bool,
    'errors': List[str],
    'warnings': List[str],
    'preview_df': pd.DataFrame,
    'info': dict
}
```

### `render_matrix_upload_ui()`

Rendert Upload-UI mit:
- Datei-Upload Widget
- Automatische Validierung
- Vorschau (erste 10 Zeilen)
- Import-Formular

### `render_matrix_list_ui()`

Rendert Matrix-Liste mit:
- Alle Matrizen
- Validierungsstatus
- Aktivieren/Deaktivieren
- Validierung durchführen

## Unterstützte Formate

### CSV
- **Delimiters:** `;`, `,`, `\t`, `|`
- **Encodings:** UTF-8, Latin-1, Windows-1252
- **Automatische Erkennung:** Ja

### Excel
- **Formate:** XLSX, XLS
- **Engine:** openpyxl
- **Automatische Erkennung:** Ja

## Validierungsergebnis

```python
{
    'valid': True,
    'errors': [],
    'warnings': ['2 Zellen sind leer'],
    'info': {
        'rows': 4,
        'columns': 3,
        'no_storage_column': 'Ohne Speicher',
        'module_counts': [10, 15, 20, 25],
        'storage_models': ['10kWh', '15kWh', 'Ohne Speicher']
    }
}
```

## Integration

### In Admin Panel

```python
# admin_panel.py
from admin_price_matrix_upload import render_matrix_upload_ui

def render_price_matrix_tab():
    st.title("Preismatrix-Verwaltung")
    render_matrix_upload_ui()
```

### In Excel Grid UI

```python
# excel_grid_ui.py
def render_price_matrix_tab():
    from admin_price_matrix_upload import render_matrix_upload_ui
    render_matrix_upload_ui()
```

## Checkliste für Upload

- [ ] Matrix-Datei vorbereitet (CSV oder Excel)
- [ ] Erste Spalte enthält Modulanzahlen (numerisch)
- [ ] Spaltenüberschriften vorhanden
- [ ] "Ohne Speicher" Spalte vorhanden
- [ ] Alle Preise sind numerisch
- [ ] Datei im Admin Panel hochgeladen
- [ ] Validierung erfolgreich
- [ ] Vorschau geprüft
- [ ] Import bestätigt
- [ ] Matrix als aktiv gesetzt (optional)

## Weitere Informationen

- **Vollständige Dokumentation:** `docs/ADMIN_MATRIX_UPLOAD_GUIDE.md`
- **Tests:** `test_admin_matrix_upload.py`
- **Quellcode:** `admin_price_matrix_upload.py`
