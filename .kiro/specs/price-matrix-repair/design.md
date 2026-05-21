# Design Document

## Overview

Die aktuelle Preismatrix-Implementierung hat mehrere kritische Probleme:

1. **Index-Verschiebung**: Der Code addiert +5 zu der gewählten Modulanzahl (corrected_module_quantity = module_quantity + 5), was zu falschen Zeilen-Lookups führt
2. **Spalten-Matching**: Das System erkennt Batteriespeicher-Modelle nicht korrekt und fällt immer auf "Ohne Speicher" zurück
3. **Mehrfache Implementierungen**: Es gibt verschiedene Preismatrix-Logiken im Code, die sich widersprechen können
4. **Datenformat-Inkonsistenzen**: Die Matrix wird sowohl als CSV als auch Excel gespeichert, aber nicht einheitlich verarbeitet

Die Lösung implementiert eine zentrale, robuste INDEX/MATCH Logik wie in Excel.

## Architecture

### Komponenten-Übersicht

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Admin Panel   │───▶│  Matrix Storage  │───▶│ Price Calculator│
│   (Upload UI)   │    │   (CSV/Excel)    │    │   (INDEX/MATCH) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Matrix Loader   │
                       │   & Validator    │
                       └──────────────────┘
```

### Datenfluss

1. **Upload**: Admin lädt price_matrix.xlsx oder price_matrix.csv hoch
2. **Validation**: System validiert Struktur (erste Spalte = "Anzahl Module", letzte Spalte = "Ohne Speicher")
3. **Storage**: Matrix wird in Admin-Settings gespeichert
4. **Loading**: Calculator lädt Matrix mit Caching
5. **Lookup**: INDEX/MATCH Logik findet korrekten Preis

## Components and Interfaces

### 1. Matrix Data Structure

```python
# Erwartete Matrix-Struktur:
# Spalte 0: "Anzahl Module" (Index)
# Spalte 1-N: Batteriespeicher-Modellnamen
# Spalte N+1: "Ohne Speicher" (letzte Spalte)

class PriceMatrix:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.module_counts = list(dataframe.index)
        self.storage_models = list(dataframe.columns)
        
    def get_price(self, module_count: int, storage_model: str) -> float:
        """Excel INDEX/MATCH Logik"""
        pass
```

### 2. Matrix Loader & Cache

```python
class MatrixLoader:
    def __init__(self):
        self._cache = {}
        self._cache_keys = {}
    
    def load_matrix(self, excel_bytes=None, csv_data=None) -> Optional[PriceMatrix]:
        """Lädt Matrix mit Caching basierend auf Daten-Hash"""
        pass
    
    def _parse_excel(self, excel_bytes: bytes) -> pd.DataFrame:
        """Parst Excel-Datei zu DataFrame"""
        pass
    
    def _parse_csv(self, csv_data: str) -> pd.DataFrame:
        """Parst CSV-Daten zu DataFrame"""
        pass
    
    def _validate_structure(self, df: pd.DataFrame) -> List[str]:
        """Validiert Matrix-Struktur"""
        pass
```

### 3. Price Calculator Interface

```python
class PriceCalculator:
    def __init__(self, matrix_loader: MatrixLoader):
        self.matrix_loader = matrix_loader
    
    def calculate_base_price(self, 
                           module_count: int, 
                           storage_model: Optional[str],
                           include_storage: bool) -> Tuple[float, List[str]]:
        """
        Berechnet Basis-Matrixpreis
        Returns: (preis, fehler_liste)
        """
        pass
```

### 4. Storage Model Resolution

```python
class StorageModelResolver:
    def resolve_storage_name(self, 
                           storage_id: Optional[str], 
                           include_storage: bool,
                           get_product_func: Callable) -> str:
        """
        Löst Speicher-ID zu Modellname auf
        Returns: Modellname oder "Ohne Speicher"
        """
        pass
```

## Data Models

### Matrix File Structure

**CSV Format:**

```csv
Anzahl Module;Speicher Model 1;Speicher Model 2;...;Ohne Speicher
7;13711.80;14311.80;...;10711.80
8;13911.80;14511.80;...;10911.80
...
```

**Excel Format:**

- Erste Spalte: "Anzahl Module" (wird als Index verwendet)
- Weitere Spalten: Batteriespeicher-Modellnamen (exakte Namen aus Produktdatenbank)
- Letzte Spalte: "Ohne Speicher"
- Datentyp: Numerische Preise (Float)

### Database Schema

```sql
-- Admin Settings Tabelle (bereits vorhanden)
-- Speichert Matrix-Daten als:
-- 'price_matrix_excel_bytes': BLOB (Excel-Datei)
-- 'price_matrix_csv_data': TEXT (CSV-Inhalt)
```

### Cache Structure

```python
cache_structure = {
    "excel_hash": {
        "dataframe": pd.DataFrame,
        "timestamp": datetime,
        "errors": List[str]
    },
    "csv_hash": {
        "dataframe": pd.DataFrame, 
        "timestamp": datetime,
        "errors": List[str]
    }
}
```

## Error Handling

### Validation Errors

1. **Struktur-Fehler**:
   - Erste Spalte ist nicht "Anzahl Module"
   - Letzte Spalte ist nicht "Ohne Speicher"
   - Leere oder ungültige Daten

2. **Daten-Fehler**:
   - Nicht-numerische Preise
   - Doppelte Modulanzahlen
   - Fehlende Werte

3. **Lookup-Fehler**:
   - Modulanzahl nicht in Matrix gefunden
   - Speichermodell nicht in Matrix gefunden
   - Matrix nicht geladen

### Error Recovery

```python
def safe_matrix_lookup(matrix, module_count, storage_model):
    """
    Sichere Matrix-Suche mit Fallback-Strategien:
    1. Exakte Suche
    2. Nächste verfügbare Modulanzahl (falls konfiguriert)
    3. "Ohne Speicher" Spalte als Fallback
    4. Preis = 0 als letzter Fallback
    """
    pass
```

## Testing Strategy

### Unit Tests

1. **Matrix Loading Tests**:
   - CSV Parsing mit verschiedenen Formaten
   - Excel Parsing mit verschiedenen Strukturen
   - Cache-Funktionalität
   - Fehlerbehandlung bei ungültigen Daten

2. **Price Calculation Tests**:
   - INDEX/MATCH Logik mit bekannten Werten
   - Speichermodell-Auflösung
   - Fallback-Szenarien
   - Edge Cases (leere Matrix, ungültige Eingaben)

3. **Integration Tests**:
   - End-to-End Upload und Calculation
   - Admin Panel Integration
   - Solar Calculator Integration

### Test Data

```python
# Test Matrix (vereinfacht)
test_matrix_csv = """
Anzahl Module;Speicher A;Speicher B;Ohne Speicher
10;15000.00;16000.00;12000.00
15;18000.00;19000.00;14000.00
20;21000.00;22000.00;16000.00
"""

# Test Cases
test_cases = [
    (10, "Speicher A", True, 15000.00),
    (15, "Speicher B", True, 19000.00),
    (20, None, False, 16000.00),  # Ohne Speicher
    (25, "Speicher A", True, 0.00),  # Nicht gefunden
]
```

### Performance Tests

- Matrix Loading Performance (große Dateien)
- Cache Hit/Miss Ratios
- Memory Usage bei großen Matrizen

## Implementation Plan

### Phase 1: Core Matrix Logic

1. Neue `PriceMatrix` Klasse implementieren
2. Robuste INDEX/MATCH Logik
3. Einheitliche CSV/Excel Parser

### Phase 2: Integration

1. Bestehende Calculation-Logik ersetzen
2. Admin Panel Upload-Validierung
3. Fehlerbehandlung verbessern

### Phase 3: Cleanup

1. Alte/doppelte Matrix-Implementierungen entfernen
2. Code-Konsolidierung
3. Performance-Optimierung

### Phase 4: Testing & Validation

1. Umfassende Tests implementieren
2. Real-World Daten testen
3. Performance-Benchmarks

## Key Design Decisions

### 1. Zentrale Matrix-Klasse

**Entscheidung**: Eine einzige `PriceMatrix` Klasse für alle Matrix-Operationen
**Begründung**: Eliminiert Code-Duplikation und Inkonsistenzen

### 2. Exakte INDEX/MATCH Semantik

**Entscheidung**: Keine automatische Näherung oder Index-Korrektur
**Begründung**: Vorhersagbares Verhalten, entspricht Excel-Logik

### 3. Robuste Speichermodell-Auflösung

**Entscheidung**: Exakte String-Matches mit Normalisierung (Trim, Case-Insensitive)
**Begründung**: Toleriert kleine Formatierungsunterschiede

### 4. Fallback auf "Ohne Speicher"

**Entscheidung**: Bei unbekanntem Speichermodell automatisch "Ohne Speicher" verwenden
**Begründung**: Graceful Degradation statt Fehler

### 5. Cache-basiertes Loading

**Entscheidung**: Hash-basiertes Caching der geparsten Matrix
**Begründung**: Performance-Optimierung bei wiederholten Berechnungen
