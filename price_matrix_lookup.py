"""price_matrix_lookup.py

Lookup-Logik für die Preismatrix-basierte Preisberechnung.

Diese Modul implementiert die INDEX-basierte Preisabfrage aus der Preismatrix:
- Modulanzahl-Suche mit Floor-Logik (nächst-kleinere Zahl)
- Speichermodell-Suche mit "Kein Speicher" Fallback
- Preis-Lookup an der Kreuzung von Zeile und Spalte
- Umfassende Fehlerbehandlung und Validierung

Struktur der Preismatrix:
- Spalte A (Index 0): Modulanzahlen (numerisch, aufsteigend sortiert)
- Zeile 1 (Index 0): Speichermodell-Namen (Text)
- Zellen: Schlüsselfertige Preise (numerisch)

Beispiel:
    Spalte A: 10, 15, 20, 25, 30
    Zeile 1: "10kWh", "15kWh", "20kWh", "Kein Speicher"
    Zelle (20, "15kWh"): 18500.00
"""

from typing import Any, Optional, Tuple
import price_matrix_store


def find_module_count_row(matrix_data: dict, module_count: int) -> Tuple[Optional[str], Optional[int]]:
    """
    Findet die Zeile für eine gegebene Modulanzahl in Spalte A.
    
    Logik:
    1. Exakte Übereinstimmung wird bevorzugt
    2. Falls nicht gefunden: Nächst-kleinere Zahl verwenden (Floor-Logik)
    3. Fehler wenn keine passende Zeile gefunden
    
    Args:
        matrix_data: Vollständige Matrix-Daten von get_matrix_full()
        module_count: Gesuchte Modulanzahl
        
    Returns:
        Tupel (row_label, row_id) oder (None, None) bei Fehler
        
    Beispiel:
        >>> find_module_count_row(matrix, 18)
        ('15', 3)  # Nächst-kleinere Zahl ist 15
    """
    if not matrix_data or 'rows' not in matrix_data:
        return (None, None)
    
    rows = matrix_data['rows']
    if not rows:
        return (None, None)
    
    # Sammle alle numerischen Zeilen-Labels mit ihren IDs
    numeric_rows = []
    for row in rows:
        label = row.get('label', '')
        try:
            # Versuche Label als Zahl zu interpretieren
            numeric_value = float(str(label).replace(',', '.'))
            numeric_rows.append({
                'value': numeric_value,
                'label': label,
                'id': row.get('id'),
                'position': row.get('position')
            })
        except (ValueError, TypeError):
            # Nicht-numerische Labels überspringen
            continue
    
    if not numeric_rows:
        return (None, None)
    
    # Sortiere nach numerischem Wert
    numeric_rows.sort(key=lambda x: x['value'])
    
    # 1. Exakte Übereinstimmung suchen
    for row in numeric_rows:
        if row['value'] == module_count:
            return (str(row['label']), row['id'])
    
    # 2. Floor-Logik: Nächst-kleinere Zahl finden
    candidates = [row for row in numeric_rows if row['value'] <= module_count]
    
    if candidates:
        # Größte Zahl die kleiner oder gleich module_count ist
        best_match = candidates[-1]
        return (str(best_match['label']), best_match['id'])
    
    # Keine passende Zeile gefunden
    return (None, None)


def find_storage_column(matrix_data: dict, storage_model: Optional[str]) -> Tuple[Optional[str], Optional[int]]:
    """
    Findet die Spalte für ein gegebenes Speichermodell in Zeile 1.
    
    Logik:
    1. Exakte Übereinstimmung mit Modellname (case-insensitive)
    2. Falls storage_model is None: Suche "Kein Speicher" Spalte
    3. Fehler wenn Modell nicht gefunden
    
    Args:
        matrix_data: Vollständige Matrix-Daten von get_matrix_full()
        storage_model: Speichermodell-Name oder None für "Kein Speicher"
        
    Returns:
        Tupel (column_label, column_id) oder (None, None) bei Fehler
        
    Beispiel:
        >>> find_storage_column(matrix, "15kWh")
        ('15kWh', 5)
        >>> find_storage_column(matrix, None)
        ('Kein Speicher', 8)
    """
    if not matrix_data or 'columns' not in matrix_data:
        return (None, None)
    
    columns = matrix_data['columns']
    if not columns:
        return (None, None)
    
    # Wenn kein Speichermodell angegeben: Suche "Kein Speicher" Spalte
    if storage_model is None:
        # Mögliche Varianten für "Kein Speicher"
        no_storage_variants = [
            'kein speicher',
            'ohne speicher',
            'keine batterie',
            'ohne batterie',
            'no storage',
            'none',
            'kein'
        ]
        
        for col in columns:
            label = str(col.get('label', '')).strip().lower()
            if label in no_storage_variants:
                return (str(col.get('label')), col.get('id'))
        
        # Keine "Kein Speicher" Spalte gefunden
        return (None, None)
    
    # Exakte Suche (case-insensitive)
    storage_model_lower = storage_model.strip().lower()
    
    for col in columns:
        label = str(col.get('label', '')).strip()
        if label.lower() == storage_model_lower:
            return (label, col.get('id'))
    
    # Keine Übereinstimmung gefunden
    return (None, None)


def lookup_price_by_intersection(
    matrix_data: dict,
    row_id: int,
    column_id: int
) -> Optional[float]:
    """
    Holt den Preis an der Kreuzung von Zeile und Spalte.
    
    Validierung:
    - Zelle muss existieren
    - Wert muss eine Zahl sein
    - Fehler bei leerer oder ungültiger Zelle
    
    Args:
        matrix_data: Vollständige Matrix-Daten von get_matrix_full()
        row_id: ID der Zeile
        column_id: ID der Spalte
        
    Returns:
        Preis als float oder None bei Fehler
        
    Beispiel:
        >>> lookup_price_by_intersection(matrix, 3, 5)
        18500.0
    """
    if not matrix_data or 'cells' not in matrix_data:
        return None
    
    cells = matrix_data['cells']
    
    # Suche Zelle an der Kreuzung
    cell_key = (row_id, column_id)
    
    if cell_key not in cells:
        # Zelle existiert nicht (leer)
        return None
    
    cell_data = cells[cell_key]
    
    # Prüfe ob Zelle einen Wert hat
    if isinstance(cell_data, dict):
        value = cell_data.get('value')
        data_type = cell_data.get('data_type', 'text')
        
        # Wenn data_type 'number' ist, sollte value eine Zahl sein
        if data_type == 'number' and value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        # Fallback: Versuche value als Zahl zu interpretieren
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
    
    # Legacy-Format: Zelle ist direkt ein numerischer Wert
    try:
        return float(cell_data)
    except (ValueError, TypeError):
        return None


def calculate_price_from_matrix(
    module_count: int,
    storage_model: Optional[str],
    matrix_id: Optional[int] = None
) -> dict[str, Any]:
    """
    Berechnet den Preis aus der Preismatrix basierend auf Modulanzahl und Speichermodell.
    
    Diese Funktion kombiniert alle Lookup-Schritte:
    1. Lade Matrix-Daten (aktive Matrix oder spezifische Matrix-ID)
    2. Finde Zeile für Modulanzahl (mit Floor-Logik)
    3. Finde Spalte für Speichermodell
    4. Hole Preis an der Kreuzung
    5. Umfassende Fehlerbehandlung
    
    Args:
        module_count: Anzahl der Module
        storage_model: Speichermodell-Name oder None für "Kein Speicher"
        matrix_id: Optional Matrix-ID (None = aktive Matrix)
    
    Returns:
        Dictionary mit folgenden Feldern:
        {
            'success': bool,              # True wenn Preis gefunden
            'base_price': float | None,   # Gefundener Preis
            'row_used': str | None,       # Verwendetes Zeilen-Label
            'row_id': int | None,         # Verwendete Zeilen-ID
            'column_used': str | None,    # Verwendetes Spalten-Label
            'column_id': int | None,      # Verwendete Spalten-ID
            'matrix_id': int | None,      # Verwendete Matrix-ID
            'matrix_name': str | None,    # Name der Matrix
            'error': str | None,          # Fehlermeldung bei Fehler
            'error_type': str | None      # Fehlertyp für spezifische Behandlung
        }
        
    Fehlertypen:
        - 'no_matrix': Keine aktive Matrix gefunden
        - 'no_row': Modulanzahl nicht in Matrix gefunden
        - 'no_column': Speichermodell nicht in Matrix gefunden
        - 'no_price': Keine Preis-Zelle an Kreuzung
        - 'invalid_price': Zelle enthält ungültigen Wert
        
    Beispiel:
        >>> result = calculate_price_from_matrix(20, "15kWh")
        >>> if result['success']:
        ...     print(f"Preis: {result['base_price']} EUR")
        ...     print(f"Zeile: {result['row_used']}, Spalte: {result['column_used']}")
    """
    result = {
        'success': False,
        'base_price': None,
        'row_used': None,
        'row_id': None,
        'column_used': None,
        'column_id': None,
        'matrix_id': None,
        'matrix_name': None,
        'error': None,
        'error_type': None
    }
    
    # 1. Lade Matrix-Daten
    if matrix_id is None:
        matrix_id = price_matrix_store.get_active_matrix_id()
        if matrix_id is None:
            result['error'] = "Keine aktive Preismatrix gefunden. Bitte aktivieren Sie eine Matrix in den Admin-Einstellungen."
            result['error_type'] = 'no_matrix'
            return result
    
    matrix_data = price_matrix_store.get_matrix_full(matrix_id)
    if not matrix_data:
        result['error'] = f"Preismatrix mit ID {matrix_id} konnte nicht geladen werden."
        result['error_type'] = 'no_matrix'
        return result
    
    result['matrix_id'] = matrix_id
    result['matrix_name'] = matrix_data.get('meta', {}).get('name', 'Unbekannt')
    
    # 2. Finde Zeile für Modulanzahl
    row_label, row_id = find_module_count_row(matrix_data, module_count)
    if row_label is None or row_id is None:
        result['error'] = f"Modulanzahl {module_count} nicht in Preismatrix gefunden. Bitte ergänzen Sie die Matrix oder wählen Sie eine andere Modulanzahl."
        result['error_type'] = 'no_row'
        return result
    
    result['row_used'] = row_label
    result['row_id'] = row_id
    
    # 3. Finde Spalte für Speichermodell
    column_label, column_id = find_storage_column(matrix_data, storage_model)
    if column_label is None or column_id is None:
        if storage_model is None:
            result['error'] = "Spalte 'Kein Speicher' nicht in Preismatrix gefunden. Bitte ergänzen Sie die Matrix."
        else:
            result['error'] = f"Speichermodell '{storage_model}' nicht in Preismatrix gefunden. Bitte ergänzen Sie die Matrix oder wählen Sie ein anderes Modell."
        result['error_type'] = 'no_column'
        return result
    
    result['column_used'] = column_label
    result['column_id'] = column_id
    
    # 4. Hole Preis an der Kreuzung
    price = lookup_price_by_intersection(matrix_data, row_id, column_id)
    
    if price is None:
        result['error'] = f"Kein Preis für Kombination {row_label} Module + {column_label} definiert. Bitte ergänzen Sie die Matrix."
        result['error_type'] = 'no_price'
        return result
    
    if not isinstance(price, (int, float)) or price < 0:
        result['error'] = f"Ungültiger Preiswert in Zelle ({row_label}, {column_label}): {price}"
        result['error_type'] = 'invalid_price'
        return result
    
    # Erfolg!
    result['success'] = True
    result['base_price'] = float(price)
    
    return result


__all__ = [
    'find_module_count_row',
    'find_storage_column',
    'lookup_price_by_intersection',
    'calculate_price_from_matrix'
]
