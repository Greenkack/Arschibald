# Admin Panel Matrix Upload - Benutzerhandbuch

## Übersicht

Das Admin Panel bietet eine erweiterte Upload-Funktionalität für Preismatrizen mit umfassender Validierung und Vorschau.

**Task 5: Verbessere Admin Panel Matrix-Upload Validierung**  
**Requirements: 2.1, 2.2, 2.4**

## Features

### ✓ Struktur-Validierung
- Automatische Prüfung der Matrix-Struktur vor dem Import
- Validierung von Spalten und Zeilen
- Erkennung von Datentyp-Problemen

### ✓ Aussagekräftige Fehlermeldungen
- Detaillierte Fehlerberichte mit Zellreferenzen
- Warnungen für potenzielle Probleme
- Hilfreiche Hinweise zur Fehlerbehebung

### ✓ Vorschau-Validierung
- Live-Vorschau der hochgeladenen Datei
- Anzeige von Datei-Informationen
- Validierung vor dem Speichern

### ✓ Multi-Format-Support
- CSV-Dateien (verschiedene Delimiters und Encodings)
- Excel-Dateien (XLSX, XLS)
- Automatische Format-Erkennung

## Verwendung

### 1. Matrix hochladen

```python
import streamlit as st
from admin_price_matrix_upload import render_matrix_upload_ui

# Im Admin Panel
render_matrix_upload_ui()
```

### 2. Validierung durchführen

Die Validierung erfolgt automatisch beim Upload:

1. **Datei auswählen**: CSV oder Excel-Datei hochladen
2. **Automatische Validierung**: System prüft Struktur und Daten
3. **Ergebnis anzeigen**: Fehler, Warnungen und Informationen werden angezeigt
4. **Vorschau prüfen**: Erste 10 Zeilen der Matrix werden angezeigt
5. **Import bestätigen**: Bei gültiger Matrix kann Import durchgeführt werden

### 3. Matrix-Liste anzeigen

```python
from admin_price_matrix_upload import render_matrix_list_ui

# Zeige alle Matrizen mit Validierungsstatus
render_matrix_list_ui()
```

## Validierungsregeln

### Erforderliche Struktur

```
         A              B              C              D
    (Modulanzahl)  (10kWh)        (15kWh)        (Kein Speicher)
1   Modulanzahl    10kWh          15kWh          Kein Speicher
2   10             15000.00       17500.00       12000.00
3   15             18000.00       20500.00       15000.00
4   20             21000.00       23500.00       18000.00
```

### Regel 1: Numerischer Index (Requirement 2.2)

**Erste Spalte muss numerische Werte enthalten (Modulanzahl)**

✓ **Gültig:**
```
10
15
20
25
```

✗ **Ungültig:**
```
ABC
DEF
Zehn
```

**Fehlermeldung:**
```
Index (erste Spalte) muss numerische Werte (Modulanzahl) enthalten.
Folgende Werte sind nicht numerisch: ABC, DEF
```

### Regel 2: Spaltenüberschriften (Requirement 2.2)

**Alle Spalten müssen Überschriften haben**

✓ **Gültig:**
```
10kWh | 15kWh | Ohne Speicher
```

✗ **Ungültig:**
```
10kWh |       | Ohne Speicher
```

**Fehlermeldung:**
```
Folgende Spalten haben keine Überschrift: Spalte 2
```

### Regel 3: "Ohne Speicher" Spalte (Requirement 2.2)

**Mindestens eine Spalte muss "Ohne Speicher" heißen**

✓ **Gültige Varianten:**
- "Ohne Speicher"
- "Kein Speicher"
- "ohne speicher"
- "KEIN SPEICHER"
- "No Storage"
- "none"

✗ **Ungültig:**
```
10kWh | 15kWh | 20kWh
(keine "Ohne Speicher" Spalte)
```

**Fehlermeldung:**
```
Keine "Ohne Speicher" Spalte gefunden.
Mindestens eine Spalte muss "Kein Speicher", "Ohne Speicher" oder ähnlich heißen.
```

### Regel 4: Numerische Preise (Requirement 2.2)

**Preis-Zellen müssen numerische Werte enthalten**

✓ **Gültig:**
```
15000.00
15000,00
15000
```

✗ **Ungültig:**
```
ABC
15000 Euro
N/A
```

**Fehlermeldung:**
```
Preis-Zellen müssen numerische Werte enthalten.
Folgende Zellen sind ungültig: 10kWh / 10 ('ABC')
```

## Beispiel-Workflows

### Workflow 1: CSV-Upload

```python
# 1. CSV-Datei vorbereiten
csv_content = """Anzahl Module;10kWh;15kWh;Ohne Speicher
10;15000.00;17500.00;12000.00
15;18000.00;20500.00;15000.00
20;21000.00;23500.00;18000.00"""

# 2. Im Admin Panel hochladen
# - Datei auswählen
# - Automatische Validierung
# - Vorschau prüfen
# - Import bestätigen

# 3. Matrix wird validiert und importiert
# - Matrix-ID wird zurückgegeben
# - Matrix kann als aktiv gesetzt werden
# - Validierungsbericht wird angezeigt
```

### Workflow 2: Excel-Upload

```python
import pandas as pd

# 1. Excel-Datei erstellen
df = pd.DataFrame(
    [[15000.00, 17500.00, 12000.00],
     [18000.00, 20500.00, 15000.00],
     [21000.00, 23500.00, 18000.00]],
    index=[10, 15, 20],
    columns=['10kWh', '15kWh', 'Ohne Speicher']
)
df.index.name = 'Anzahl Module'
df.to_excel('price_matrix.xlsx')

# 2. Im Admin Panel hochladen
# - Excel-Datei auswählen
# - Automatische Validierung
# - Vorschau prüfen
# - Import bestätigen
```

### Workflow 3: Fehlerbehandlung

```python
# Ungültige Matrix hochladen
csv_content = """Anzahl Module;10kWh;15kWh
ABC;15000.00;17500.00
DEF;18000.00;20500.00"""

# Validierung schlägt fehl:
# ✗ Fehler:
#   • Index (erste Spalte) muss numerische Werte enthalten
#   • Keine "Ohne Speicher" Spalte gefunden

# Matrix kann nicht importiert werden
# Benutzer muss Fehler beheben und erneut hochladen
```

## API-Referenz

### `validate_uploaded_file(file_content, file_type)`

Validiert eine hochgeladene Matrix-Datei.

**Parameter:**
- `file_content` (bytes): Dateiinhalt
- `file_type` (str): 'csv' oder 'excel'

**Returns:**
```python
{
    'valid': bool,              # True wenn gültig
    'errors': List[str],        # Liste von Fehlern
    'warnings': List[str],      # Liste von Warnungen
    'preview_df': pd.DataFrame, # Vorschau-DataFrame
    'info': {                   # Zusätzliche Informationen
        'rows': int,
        'columns': int,
        'delimiter': str,       # Nur bei CSV
        'encoding': str,        # Nur bei CSV
        'no_storage_column': str,
        'module_counts': List[float],
        'storage_models': List[str],
        'total_cells': int,
        'empty_cells': int
    }
}
```

**Beispiel:**
```python
from admin_price_matrix_upload import validate_uploaded_file

# CSV validieren
with open('price_matrix.csv', 'rb') as f:
    file_content = f.read()

result = validate_uploaded_file(file_content, 'csv')

if result['valid']:
    print("✓ Matrix ist gültig")
    print(f"Zeilen: {result['info']['rows']}")
    print(f"Spalten: {result['info']['columns']}")
else:
    print("✗ Matrix ist ungültig")
    for error in result['errors']:
        print(f"  • {error}")
```

### `render_matrix_upload_ui()`

Rendert die Upload-UI im Admin Panel.

**Features:**
- Datei-Upload Widget
- Automatische Validierung
- Vorschau-Anzeige
- Import-Formular
- Fehler- und Warnungsanzeige

**Beispiel:**
```python
import streamlit as st
from admin_price_matrix_upload import render_matrix_upload_ui

st.title("Preismatrix-Verwaltung")
render_matrix_upload_ui()
```

### `render_matrix_list_ui()`

Rendert eine Liste aller Matrizen mit Validierungsstatus.

**Features:**
- Liste aller Matrizen
- Validierungsstatus
- Aktivieren/Deaktivieren
- Validierung durchführen

**Beispiel:**
```python
import streamlit as st
from admin_price_matrix_upload import render_matrix_list_ui

st.title("Vorhandene Matrizen")
render_matrix_list_ui()
```

## Fehlerbehebung

### Problem: CSV wird nicht erkannt

**Symptom:**
```
CSV-Datei konnte nicht gelesen werden.
Bitte prüfen Sie das Format (Delimiter, Encoding).
```

**Lösung:**
1. Prüfen Sie den Delimiter (Semikolon, Komma, Tab)
2. Prüfen Sie das Encoding (UTF-8, Latin-1, Windows-1252)
3. Stellen Sie sicher, dass die erste Zeile Spaltenüberschriften enthält

### Problem: Index nicht numerisch

**Symptom:**
```
Index (erste Spalte) muss numerische Werte (Modulanzahl) enthalten.
```

**Lösung:**
1. Erste Spalte muss Zahlen enthalten (z.B. 10, 15, 20)
2. Keine Text-Werte (z.B. "Zehn", "ABC")
3. Dezimaltrennzeichen: Punkt oder Komma

### Problem: "Ohne Speicher" Spalte fehlt

**Symptom:**
```
Keine "Ohne Speicher" Spalte gefunden.
```

**Lösung:**
1. Fügen Sie eine Spalte mit Namen "Ohne Speicher" hinzu
2. Alternative Namen: "Kein Speicher", "No Storage", "none"
3. Groß-/Kleinschreibung ist egal

### Problem: Nicht-numerische Preise

**Symptom:**
```
Preis-Zellen müssen numerische Werte enthalten.
Folgende Zellen sind ungültig: 10kWh / 10 ('ABC')
```

**Lösung:**
1. Alle Preis-Zellen müssen Zahlen enthalten
2. Keine Text-Werte (z.B. "N/A", "TBD")
3. Leere Zellen sind erlaubt (werden als Warnung angezeigt)

## Best Practices

### 1. Matrix-Struktur vorbereiten

✓ **Empfohlen:**
- Erste Spalte: Numerische Modulanzahlen (aufsteigend sortiert)
- Weitere Spalten: Speichermodell-Namen (eindeutig)
- Letzte Spalte: "Ohne Speicher"
- Alle Preis-Zellen: Numerische Werte

### 2. Datei-Format wählen

✓ **CSV:**
- Einfach zu erstellen und bearbeiten
- Delimiter: Semikolon (;) empfohlen
- Encoding: UTF-8 empfohlen

✓ **Excel:**
- Bessere Formatierung
- Einfacher zu bearbeiten
- Automatische Typ-Erkennung

### 3. Validierung nutzen

✓ **Vor dem Import:**
1. Datei hochladen
2. Validierungsergebnis prüfen
3. Fehler beheben
4. Erneut hochladen
5. Import bestätigen

### 4. Matrix testen

✓ **Nach dem Import:**
1. Matrix als aktiv setzen
2. Validierung durchführen
3. Testberechnung durchführen
4. Ergebnisse prüfen

## Integration

### In Admin Panel integrieren

```python
# admin_panel.py

import streamlit as st
from admin_price_matrix_upload import (
    render_matrix_upload_ui,
    render_matrix_list_ui
)

def render_price_matrix_tab():
    """Rendert den Preismatrix-Tab im Admin Panel"""
    
    st.title("Preismatrix-Verwaltung")
    
    # Tabs für Upload und Liste
    tab1, tab2 = st.tabs(["📤 Upload", "📊 Matrizen"])
    
    with tab1:
        render_matrix_upload_ui()
    
    with tab2:
        render_matrix_list_ui()
```

### In Excel Grid UI integrieren

```python
# excel_grid_ui.py

from admin_price_matrix_upload import validate_uploaded_file

def render_price_matrix_tab():
    """Rendert den Preis Matrix Tab im Admin Panel"""
    
    # Verwende neue Upload-Validierung
    from admin_price_matrix_upload import render_matrix_upload_ui
    render_matrix_upload_ui()
```

## Zusammenfassung

Die erweiterte Upload-Validierung bietet:

✓ **Automatische Struktur-Prüfung**
- Validierung vor dem Import
- Fehler werden sofort erkannt
- Keine ungültigen Matrizen in der Datenbank

✓ **Aussagekräftige Fehlermeldungen**
- Detaillierte Fehlerberichte
- Zellreferenzen für einfache Fehlerbehebung
- Hilfreiche Hinweise

✓ **Vorschau-Validierung**
- Live-Vorschau der Daten
- Informationen über Matrix-Struktur
- Validierung vor dem Speichern

✓ **Multi-Format-Support**
- CSV und Excel
- Automatische Format-Erkennung
- Flexible Delimiter und Encodings

**Requirements erfüllt:**
- ✓ 2.1: Datei-Upload im Admin-Bereich
- ✓ 2.2: Struktur-Validierung
- ✓ 2.4: Bestätigung nach erfolgreichem Upload
