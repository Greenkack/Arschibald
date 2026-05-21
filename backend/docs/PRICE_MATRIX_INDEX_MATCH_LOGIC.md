# Preismatrix INDEX/MATCH Logik - Detaillierte Dokumentation

## Übersicht

Die Preismatrix verwendet eine Excel-ähnliche INDEX/MATCH-Logik zur Preisermittlung für schlüsselfertige PV-Anlagen. Diese Logik ist **KRITISCH** für das gesamte Preisberechnungssystem.

## Excel-Formel Beispiel

```excel
=INDEX(A2:A200; VERGLEICH(C37; A2:XX200; 0); VERGLEICH(C65; B2:XX2; 0))
```

### Formel-Komponenten

- **INDEX(A2:A200, row, col)**: Gibt den Wert an der Kreuzung von Zeile und Spalte zurück
- **VERGLEICH(C37, A2:XX200, 0)**: Findet die Zeile basierend auf Modulanzahl
- **VERGLEICH(C65, B2:XX2, 0)**: Findet die Spalte basierend auf Batteriespeicher
- **0**: Exakte Übereinstimmung erforderlich

## Matrix-Struktur

### Aufbau der Tabelle

```
     A          B           C           D         ...    XX
1  [leer]   Speicher1   Speicher2   Speicher3   ...  kein Speicher
2    10      15.000€     18.000€     20.000€     ...    12.000€
3    15      18.000€     21.000€     23.000€     ...    15.000€
4    20      21.000€     24.000€     26.000€     ...    18.000€
...
200  500     95.000€     98.000€    100.000€     ...    85.000€
```

### Spalten-Definition

- **Spalte A (A2:A200)**: Anzahl der PV-Module
  - Werte: 10, 15, 20, 25, ..., 500
  - Wird im Solar Calculator ausgewählt/eingegeben
  - Verknüpft mit Zelle C37 (Beispiel)

- **Zeile 1 (B1:XX1)**: Batteriespeichermodelle
  - Werte: "Tesla Powerwall 2", "BYD HVS 10.2", "Sonnen Batterie 10", etc.
  - Wird im Solar Calculator ausgewählt
  - Verknüpft mit Zelle C65 (Beispiel)

- **Letzte Spalte (XX2:XX200)**: "kein Speicher"
  - Spezialfall: Wenn KEIN Speicher gewählt wird
  - **Umgekehrte Logik**: Auswahl "kein Speicher" → Letzte Spalte aktiv
  - Enthält Preise nur für PV-Anlage ohne Batteriespeicher

### Zellen-Inhalt

Alle Datenzellen (B2:XX200) enthalten **schlüsselfertige Preise** die ALLES beinhalten:

#### Im Preis ENTHALTEN:
- ✅ PV-Module (alle benötigten Module)
- ✅ Wechselrichter (Inverter)
- ✅ Batteriespeicher (wenn gewählt)
- ✅ Unterkonstruktion (Mounting System)
- ✅ Alle Kabel und Materialien
- ✅ Installation und Montage
- ✅ Inbetriebnahme
- ✅ Genehmigungen und Anmeldungen
- ✅ Provisionen und Margen
- ✅ Komplette schlüsselfertige Übergabe

#### NICHT im Preis enthalten (werden separat addiert):
- ❌ Extrakosten (nur wenn gewählt)
- ❌ Aufpreise (nur wenn gewählt)
- ❌ Rabatte (werden abgezogen)
- ❌ Nachlässe (werden abgezogen)
- ❌ Zubehör (nur wenn gewählt)
- ❌ Extras (nur wenn gewählt)

## Lookup-Logik

### Schritt-für-Schritt Ablauf

1. **Eingabe im Solar Calculator**
   ```
   Benutzer wählt:
   - Anzahl Module: 25
   - Batteriespeicher: "Tesla Powerwall 2"
   ```

2. **Zeilen-Lookup (VERGLEICH für Module)**
   ```python
   row_index = MATCH(25, column_A_range, exact_match=True)
   # Findet Zeile wo Spalte A = 25
   # Beispiel: Zeile 5
   ```

3. **Spalten-Lookup (VERGLEICH für Speicher)**
   ```python
   col_index = MATCH("Tesla Powerwall 2", row_1_range, exact_match=True)
   # Findet Spalte wo Zeile 1 = "Tesla Powerwall 2"
   # Beispiel: Spalte B (Index 2)
   ```

4. **Preis-Abruf (INDEX)**
   ```python
   price = INDEX(full_matrix, row_index=5, col_index=2)
   # Gibt Wert an Kreuzung zurück
   # Beispiel: 22.500€
   ```

### Spezialfall: "kein Speicher"

```python
if battery_selection == "kein Speicher":
    # Verwende LETZTE Spalte (XX)
    col_index = last_column_index
    price = INDEX(full_matrix, row_index, col_index)
```

**Wichtig**: Die Logik ist umgekehrt!
- Wenn "kein Speicher" gewählt → Letzte Spalte wird verwendet
- Wenn ein Speicher gewählt → Entsprechende Spalte wird verwendet

## Implementierungs-Anforderungen

### 1. Matrix-Upload und -Verwaltung

```python
class PriceMatrixService:
    def upload_matrix(self, file_data, file_type):
        """
        Upload matrix from CSV, JSON, or XLSX
        
        Validations:
        - Column A must contain numeric module counts
        - Row 1 must contain battery model names
        - Last column must be labeled "kein Speicher"
        - All price cells must be numeric
        - No empty cells in price range
        """
        pass
    
    def validate_matrix_structure(self, matrix_data):
        """
        Validate matrix structure:
        - Check column A for sequential module counts
        - Check row 1 for valid battery models
        - Verify "kein Speicher" in last column
        - Validate all prices are positive numbers
        """
        pass
```

### 2. INDEX/MATCH Implementierung

```python
def index_match_lookup(matrix, module_count, battery_model):
    """
    Implement Excel INDEX/MATCH logic
    
    Args:
        matrix: 2D array of price data
        module_count: Number of PV modules (from Solar Calculator)
        battery_model: Battery storage model or "kein Speicher"
    
    Returns:
        float: Turnkey system price in EUR
    
    Raises:
        ValueError: If module_count or battery_model not found
    """
    # Step 1: Find row index
    row_index = match(module_count, matrix[:, 0], exact=True)
    
    # Step 2: Find column index
    if battery_model == "kein Speicher":
        col_index = len(matrix[0]) - 1  # Last column
    else:
        col_index = match(battery_model, matrix[0, :], exact=True)
    
    # Step 3: Return price at intersection
    return matrix[row_index, col_index]
```

### 3. Solar Calculator Integration

```python
def calculate_total_price(solar_config):
    """
    Calculate total price with matrix lookup
    
    Steps:
    1. Get base price from matrix (INDEX/MATCH)
    2. Add selected extras
    3. Apply discounts
    4. Format in German (1.234,56 €)
    5. Generate PDF bytes
    6. Assign dynamic keys
    """
    # Base price from matrix
    base_price = index_match_lookup(
        matrix=price_matrix,
        module_count=solar_config.module_count,
        battery_model=solar_config.battery_model
    )
    
    # Add extras (only if selected)
    total_price = base_price
    if solar_config.extras:
        total_price += sum(extra.price for extra in solar_config.extras)
    
    # Apply discounts
    if solar_config.discounts:
        total_price -= sum(discount.amount for discount in solar_config.discounts)
    
    return {
        'base_price': base_price,
        'total_price': total_price,
        'extras': solar_config.extras,
        'discounts': solar_config.discounts,
        'formatted_price': format_german(total_price),  # "22.500,00 €"
        'pdf_bytes': generate_pdf_bytes(total_price),
        'dynamic_key': generate_dynamic_key('price', solar_config.id)
    }
```

### 4. Dynamische Features

#### CRUD-Operationen
```python
# Create: Neue Matrix hochladen
matrix_id = service.create_matrix(file_data, metadata)

# Read: Matrix abrufen
matrix = service.get_matrix(matrix_id)

# Update: Einzelne Zellen oder ganze Matrix aktualisieren
service.update_matrix_cell(matrix_id, row=5, col=3, new_price=23000.00)

# Delete: Matrix löschen
service.delete_matrix(matrix_id)
```

#### Echtzeit-Synchronisation
```python
# Änderungen in Matrix → Sofort in Solar Calculator sichtbar
@on_matrix_update
def sync_to_calculator(matrix_id):
    # Invalidate cache
    cache.invalidate(f"matrix_{matrix_id}")
    
    # Notify Solar Calculator
    websocket.broadcast({
        'event': 'matrix_updated',
        'matrix_id': matrix_id
    })
```

### 5. Fehlerbehandlung

```python
class MatrixLookupError(Exception):
    """Raised when matrix lookup fails"""
    pass

def safe_index_match_lookup(matrix, module_count, battery_model):
    """
    Safe lookup with German error messages
    """
    try:
        return index_match_lookup(matrix, module_count, battery_model)
    except ValueError as e:
        if "module_count" in str(e):
            raise MatrixLookupError(
                f"Modulanzahl {module_count} nicht in Preismatrix gefunden. "
                f"Verfügbare Werte: {get_available_module_counts(matrix)}"
            )
        elif "battery_model" in str(e):
            raise MatrixLookupError(
                f"Batteriespeicher '{battery_model}' nicht in Preismatrix gefunden. "
                f"Verfügbare Modelle: {get_available_battery_models(matrix)}"
            )
        else:
            raise MatrixLookupError(f"Preisermittlung fehlgeschlagen: {e}")
```

## Performance-Optimierung

### Caching-Strategie

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_price_lookup(matrix_id, module_count, battery_model):
    """
    Cache häufig abgerufene Preise
    
    Cache-Key: (matrix_id, module_count, battery_model)
    Cache-Size: 1000 häufigste Kombinationen
    Cache-Invalidierung: Bei Matrix-Update
    """
    matrix = load_matrix(matrix_id)
    return index_match_lookup(matrix, module_count, battery_model)
```

### Index-Optimierung

```python
# Datenbank-Indizes für schnelle Abfragen
CREATE INDEX idx_matrix_module_count ON price_matrix(module_count);
CREATE INDEX idx_matrix_battery_model ON price_matrix(battery_model);
CREATE INDEX idx_matrix_lookup ON price_matrix(module_count, battery_model);
```

## Testing-Anforderungen

### Unit Tests

```python
def test_index_match_basic():
    """Test basic INDEX/MATCH lookup"""
    matrix = create_test_matrix()
    price = index_match_lookup(matrix, module_count=20, battery_model="Tesla Powerwall 2")
    assert price == 21000.00

def test_kein_speicher_logic():
    """Test 'kein Speicher' special case"""
    matrix = create_test_matrix()
    price = index_match_lookup(matrix, module_count=20, battery_model="kein Speicher")
    # Should use last column
    assert price == 18000.00

def test_module_count_not_found():
    """Test error when module count not in matrix"""
    matrix = create_test_matrix()
    with pytest.raises(MatrixLookupError):
        index_match_lookup(matrix, module_count=999, battery_model="Tesla Powerwall 2")

def test_battery_model_not_found():
    """Test error when battery model not in matrix"""
    matrix = create_test_matrix()
    with pytest.raises(MatrixLookupError):
        index_match_lookup(matrix, module_count=20, battery_model="Unknown Model")
```

### Integration Tests

```python
def test_solar_calculator_integration():
    """Test full integration with Solar Calculator"""
    # Setup
    solar_config = {
        'module_count': 25,
        'battery_model': 'BYD HVS 10.2',
        'extras': [],
        'discounts': []
    }
    
    # Execute
    result = calculate_total_price(solar_config)
    
    # Verify
    assert result['base_price'] > 0
    assert result['total_price'] == result['base_price']
    assert result['formatted_price'].endswith(' €')
    assert result['pdf_bytes'] is not None
    assert result['dynamic_key'].startswith('price_')
```

## Zusammenfassung

Die Preismatrix-Logik ist das Herzstück der Preisberechnung:

1. **Matrix-Struktur**: Spalte A = Module, Zeile 1 = Speicher, Zellen = Preise
2. **Lookup-Logik**: INDEX/MATCH wie in Excel
3. **Spezialfall**: "kein Speicher" verwendet letzte Spalte
4. **Preis-Inhalt**: Schlüsselfertig, alles inklusive
5. **Extras**: Werden separat addiert
6. **Dynamisch**: Vollständig editierbar, CRUD, Echtzeit-Sync
7. **Integration**: Direkt mit Solar Calculator verknüpft
8. **Format**: Deutsche Zahlenformatierung (1.234,56 €)
9. **PDF**: Automatische PDF-Bytes-Generierung
10. **Keys**: Dynamische Schlüssel für alle Daten

Diese Logik MUSS in allen relevanten Tasks (12, 140, 141, 142, 143, 145) implementiert werden!
