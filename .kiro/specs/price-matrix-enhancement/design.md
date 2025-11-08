# Design Document - Preismatrix-Erweiterung

## Überblick

Dieses Design beschreibt die Erweiterung der bestehenden Preismatrix-Funktionalität um:
1. Text- und Zahleneingabe in Zellen
2. Strukturierte Matrix mit Kopfzeile (Speichermodelle) und Kopfspalte (Modulanzahl)
3. Preisberechnungsmodus-Auswahl im Admin-Panel
4. INDEX-basierte Preisabfrage im Solarcalculator
5. Vollständige Trennung zwischen Standardberechnung und Preismatrix-Modus

## Architektur

### Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                      Admin Panel                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Erweiterte Einstellungen                            │   │
│  │  - Preisberechnungsmodus-Auswahl                     │   │
│  │    ○ Standardberechnung (Einzelprodukte)             │   │
│  │    ○ Preismatrix (Schlüsselfertige Preise)          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database (admin_settings)                   │
│  - pricing_calculation_mode: "standard" | "matrix"          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Solarcalculator                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  IF pricing_calculation_mode == "matrix":            │   │
│  │    1. Hole Modulanzahl aus Benutzerauswahl           │   │
│  │    2. Hole Speichermodell aus Benutzerauswahl        │   │
│  │    3. Lookup in Preismatrix (INDEX-Funktion)         │   │
│  │    4. Verwende Preis als Basispreis                  │   │
│  │    5. Addiere nur Sonderprodukte/Extras              │   │
│  │  ELSE:                                                │   │
│  │    - Normale Einzelprodukt-Kalkulation               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Excel Grid UI (Preismatrix)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Spalte A: Modulanzahl (10, 15, 20, 25, ...)        │   │
│  │  Zeile 1: Speichermodelle (10kWh, 15kWh, Kein, ...) │   │
│  │  Zellen: Schlüsselfertige Preise                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Komponenten und Schnittstellen

### 1. Excel Grid UI - Text/Zahlen-Eingabe

**Datei:** `excel_grid_ui.py`

**Änderungen:**
- Zellen-Validierung erweitern um Text-Unterstützung
- Keine automatische Konvertierung zu Zahlen erzwingen
- Speicherung von Text und Zahlen in `Cell.raw_input`

**Neue Funktionen:**
```python
def _validate_cell_input_mixed(value: str) -> dict:
    """
    Validiert Zell-Eingabe für Text oder Zahlen
    
    Returns:
        {
            'valid': bool,
            'type': 'text' | 'number' | 'formula',
            'value': Any,
            'error': str | None
        }
    """
```

### 2. Database Schema - Preisberechnungsmodus

**Datei:** `database.py`

**Neue Admin-Setting:**
```python
# In INITIAL_ADMIN_SETTINGS hinzufügen:
"pricing_calculation_mode": "standard"  # "standard" | "matrix"
```

**Funktionen:**
```python
def get_pricing_calculation_mode() -> str:
    """Gibt aktuellen Preisberechnungsmodus zurück"""
    return load_admin_setting('pricing_calculation_mode', 'standard')

def set_pricing_calculation_mode(mode: str) -> bool:
    """Setzt Preisberechnungsmodus"""
    if mode not in ['standard', 'matrix']:
        return False
    return save_admin_setting('pricing_calculation_mode', mode)
```

### 3. Admin Panel - Modus-Auswahl

**Datei:** `admin_panel.py`

**Neue Funktion:**
```python
def render_pricing_mode_settings():
    """
    Rendert Preisberechnungsmodus-Einstellungen in 'Erweiterte Einstellungen'
    """
```


### 4. Solarcalculator - Preismatrix-Integration

**Datei:** `solar_calculator.py`

**Neue Funktionen:**
```python
def calculate_price_from_matrix(
    module_count: int,
    storage_model: str | None,
    matrix_id: int | None = None
) -> dict:
    """
    Berechnet Preis aus Preismatrix basierend auf Modulanzahl und Speichermodell
    
    Args:
        module_count: Anzahl der Module
        storage_model: Speichermodell-Name oder None für "Kein Speicher"
        matrix_id: Optional Matrix-ID (None = aktive Matrix)
    
    Returns:
        {
            'success': bool,
            'base_price': float | None,
            'row_used': str,
            'column_used': str,
            'error': str | None
        }
    """

def get_total_price_with_matrix_mode(details: dict) -> dict:
    """
    Berechnet Gesamtpreis im Preismatrix-Modus
    
    Logik:
    1. Hole Basispreis aus Matrix
    2. Addiere NUR Sonderprodukte/Extras/Dienstleistungen
    3. KEINE Standard-Aufschläge (Montage, Installation, etc.)
    
    Returns:
        {
            'base_price': float,
            'extras_price': float,
            'total_price': float,
            'breakdown': dict
        }
    """
```

**Integration in bestehende Preisberechnung:**
```python
def _display_pricing_information(details: dict, texts: dict) -> None:
    """
    Erweitert um Preismatrix-Modus
    """
    # Prüfe Preisberechnungsmodus
    pricing_mode = get_pricing_calculation_mode()
    
    if pricing_mode == "matrix":
        # Preismatrix-Berechnung
        matrix_result = calculate_price_from_matrix(
            module_count=details.get('module_count'),
            storage_model=details.get('storage_model')
        )
        
        if matrix_result['success']:
            # Zeige Matrix-Preis
            display_matrix_pricing(matrix_result, details)
        else:
            # Fehler anzeigen
            st.error(f"Preismatrix-Fehler: {matrix_result['error']}")
    else:
        # Standard-Berechnung (bestehender Code)
        display_standard_pricing(details)
```

### 5. Preismatrix-Lookup-Logik

**Datei:** `price_matrix_lookup.py` (NEU)

**Funktionen:**
```python
def find_module_count_row(matrix_data: dict, module_count: int) -> tuple[str, int]:
    """
    Findet Zeile für Modulanzahl in Spalte A
    
    Logik:
    - Exakte Übereinstimmung bevorzugt
    - Falls nicht gefunden: Nächst-kleinere Zahl (Floor)
    - Gibt (row_label, row_index) zurück
    """

def find_storage_column(matrix_data: dict, storage_model: str | None) -> tuple[str, int]:
    """
    Findet Spalte für Speichermodell in Zeile 1
    
    Logik:
    - Exakte Übereinstimmung mit Modellname
    - Falls storage_model is None: Suche "Kein Speicher" Spalte
    - Gibt (column_label, column_index) zurück
    """

def lookup_price_by_intersection(
    matrix_data: dict,
    row_index: int,
    column_index: int
) -> float | None:
    """
    Holt Preis an Kreuzung von Zeile und Spalte
    
    Returns:
        Preis als float oder None wenn Zelle leer/ungültig
    """
```

## Datenmodelle

### Preismatrix-Struktur

```python
{
    'meta': {
        'id': int,
        'name': str,
        'pricing_mode': 'pauschal',  # Immer pauschal für diese Anwendung
        'created_at': datetime,
        'updated_at': datetime
    },
    'rows': [
        {'index': 0, 'label': 'Modulanzahl'},  # Header-Zeile
        {'index': 1, 'label': '10'},
        {'index': 2, 'label': '15'},
        {'index': 3, 'label': '20'},
        ...
    ],
    'columns': [
        {'index': 0, 'label': 'Modulanzahl'},  # Header-Spalte
        {'index': 1, 'label': '10kWh'},
        {'index': 2, 'label': '15kWh'},
        {'index': 3, 'label': 'Kein Speicher'},
        ...
    ],
    'cells': {
        (1, 1): {'value': 15000.0, 'type': 'number'},  # 10 Module, 10kWh
        (1, 2): {'value': 17500.0, 'type': 'number'},  # 10 Module, 15kWh
        (1, 3): {'value': 12000.0, 'type': 'number'},  # 10 Module, Kein Speicher
        (2, 1): {'value': 18000.0, 'type': 'number'},  # 15 Module, 10kWh
        ...
    }
}
```

### Solarcalculator Details-Erweiterung

```python
details = {
    # Bestehende Felder
    'module_count': int,
    'storage_model': str | None,
    
    # Neue Felder für Preismatrix
    'pricing_mode': 'standard' | 'matrix',
    'matrix_price_info': {
        'base_price': float,
        'row_used': str,
        'column_used': str,
        'matrix_id': int,
        'matrix_name': str
    } | None
}
```

## Fehlerbehandlung

### Fehlertypen und Behandlung

1. **Matrix nicht gefunden**
   - Fehler: "Keine aktive Preismatrix gefunden"
   - Aktion: Zeige Warnung, falle zurück auf Standardberechnung

2. **Modulanzahl nicht in Matrix**
   - Fehler: "Modulanzahl {X} nicht in Preismatrix gefunden"
   - Aktion: Verwende Floor-Logik (nächst-kleinere Zahl)
   - Falls keine kleinere Zahl: Zeige Fehler

3. **Speichermodell nicht in Matrix**
   - Fehler: "Speichermodell '{Y}' nicht in Preismatrix gefunden"
   - Aktion: Zeige Fehler mit Vorschlag "Kein Speicher" zu verwenden

4. **Zelle leer oder ungültig**
   - Fehler: "Kein Preis für Kombination {X} Module + {Y} Speicher"
   - Aktion: Zeige Fehler, fordere Admin auf Matrix zu vervollständigen

5. **Zelle enthält Text statt Zahl**
   - Fehler: "Ungültiger Preiswert in Zelle {A1}: '{text}'"
   - Aktion: Zeige Fehler mit Hinweis auf Zahlen-Eingabe

### Validierungs-Funktion

```python
def validate_matrix_for_pricing(matrix_id: int) -> dict:
    """
    Validiert ob Matrix für Preisberechnung geeignet ist
    
    Prüfungen:
    - Spalte A enthält numerische Werte (Modulanzahl)
    - Zeile 1 enthält Text-Werte (Speichermodelle)
    - Mindestens eine "Kein Speicher" Spalte vorhanden
    - Alle Preis-Zellen enthalten Zahlen oder sind leer
    
    Returns:
        {
            'valid': bool,
            'errors': list[str],
            'warnings': list[str]
        }
    """
```

## Testing-Strategie

### Unit Tests

1. **Preismatrix-Lookup**
   - Test: Exakte Modulanzahl-Übereinstimmung
   - Test: Floor-Logik bei fehlender Modulanzahl
   - Test: Speichermodell-Suche (exakt)
   - Test: "Kein Speicher" Fallback
   - Test: Ungültige Eingaben

2. **Preisberechnung**
   - Test: Matrix-Modus vs. Standard-Modus
   - Test: Basispreis + Extras (keine Standard-Aufschläge)
   - Test: Fehlerbehandlung bei fehlenden Daten

3. **Admin-Panel**
   - Test: Modus-Umschaltung
   - Test: Persistierung in Datenbank
   - Test: UI-Anzeige

### Integrationstests

1. **End-to-End Preisberechnung**
   - Szenario: Admin aktiviert Matrix-Modus
   - Szenario: Benutzer wählt 20 Module + 10kWh Speicher
   - Erwartung: Korrekter Preis aus Matrix
   - Erwartung: Keine Standard-Aufschläge

2. **Fehlerszenarien**
   - Szenario: Matrix leer
   - Szenario: Modulanzahl nicht vorhanden
   - Szenario: Speichermodell nicht vorhanden
   - Erwartung: Sinnvolle Fehlermeldungen

## Implementierungs-Reihenfolge

1. **Phase 1: Datenbank & Admin-Panel**
   - Admin-Setting für Preisberechnungsmodus
   - UI in "Erweiterte Einstellungen"
   - Persistierung und Laden

2. **Phase 2: Excel Grid - Text/Zahlen**
   - Zellen-Validierung erweitern
   - Text-Eingabe ermöglichen
   - Speicherung anpassen

3. **Phase 3: Preismatrix-Lookup**
   - Lookup-Logik implementieren
   - Floor-Funktion für Modulanzahl
   - Speichermodell-Suche

4. **Phase 4: Solarcalculator-Integration**
   - Modus-Prüfung
   - Matrix-Preisberechnung
   - UI-Anpassungen

5. **Phase 5: Fehlerbehandlung & Validierung**
   - Validierungs-Funktionen
   - Fehler-UI
   - Benutzer-Feedback

6. **Phase 6: Testing & Dokumentation**
   - Unit Tests
   - Integrationstests
   - Benutzer-Dokumentation
