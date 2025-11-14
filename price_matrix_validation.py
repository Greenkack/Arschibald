"""
Preismatrix-Validierung

Dieses Modul stellt Validierungsfunktionen für die Preismatrix bereit.
Es prüft die Struktur und Datenintegrität der Matrix gemäß den Anforderungen.
"""

from typing import Dict, List, Any, Optional
from price_matrix_store import get_matrix_full


def validate_matrix_for_pricing(matrix_id: int) -> Dict[str, Any]:
    """
    Validiert ob Matrix für Preisberechnung geeignet ist
    
    Prüfungen:
    - Spalte A (Position 0) enthält numerische Werte (Modulanzahl)
    - Zeile 1 (Position 0) enthält Text-Werte (Speichermodelle)
    - Mindestens eine "Kein Speicher" Spalte vorhanden
    - Alle Preis-Zellen enthalten Zahlen oder sind leer
    
    Args:
        matrix_id: ID der zu validierenden Matrix
        
    Returns:
        Dictionary mit:
        {
            'valid': bool,
            'errors': List[str],
            'warnings': List[str],
            'info': Dict[str, Any]
        }
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 7.1
    """
    errors: List[str] = []
    warnings: List[str] = []
    info: Dict[str, Any] = {}
    
    # Lade Matrix-Daten
    matrix_data = get_matrix_full(matrix_id)
    
    if not matrix_data:
        return {
            'valid': False,
            'errors': [f'Matrix mit ID {matrix_id} nicht gefunden'],
            'warnings': [],
            'info': {}
        }
    
    rows = matrix_data.get('rows', [])
    columns = matrix_data.get('columns', [])
    cells = matrix_data.get('cells', {})
    
    # Prüfe ob Matrix leer ist
    if not rows or not columns:
        errors.append('Matrix ist leer - keine Zeilen oder Spalten vorhanden')
        return {
            'valid': False,
            'errors': errors,
            'warnings': warnings,
            'info': info
        }
    
    # Requirement 2.1: Spalte A (Position 0) muss numerische Werte enthalten (Modulanzahl)
    column_a_errors = _validate_column_a_numeric(rows, columns, cells)
    errors.extend(column_a_errors)
    
    # Requirement 2.2: Zeile 1 (Position 0) muss Text-Werte enthalten (Speichermodelle)
    row_1_errors = _validate_row_1_text(rows, columns, cells)
    errors.extend(row_1_errors)
    
    # Requirement 2.3: Mindestens eine "Kein Speicher" Spalte erforderlich
    no_storage_result = _validate_no_storage_column(columns)
    if not no_storage_result['found']:
        errors.append(
            'Keine "Kein Speicher" Spalte gefunden. '
            'Mindestens eine Spalte muss "Kein Speicher", "Ohne Speicher" oder ähnlich heißen.'
        )
    else:
        info['no_storage_column'] = no_storage_result['column_label']
        info['no_storage_column_id'] = no_storage_result['column_id']
    
    # Requirement 2.4: Preis-Zellen müssen Zahlen oder leer sein
    price_cell_errors = _validate_price_cells(rows, columns, cells)
    errors.extend(price_cell_errors)
    
    # Zusätzliche Informationen sammeln
    info['total_rows'] = len(rows)
    info['total_columns'] = len(columns)
    info['total_cells'] = len(cells)
    info['module_counts'] = _extract_module_counts(rows, columns, cells)
    info['storage_models'] = _extract_storage_models(rows, columns, cells)
    
    # Warnungen für potenzielle Probleme
    if len(rows) < 2:
        warnings.append('Matrix hat nur eine Zeile. Mindestens 2 Zeilen empfohlen (Header + Daten).')
    
    if len(columns) < 2:
        warnings.append('Matrix hat nur eine Spalte. Mindestens 2 Spalten empfohlen (Modulanzahl + Speicher).')
    
    # Prüfe auf leere Preis-Zellen
    empty_price_cells = _count_empty_price_cells(rows, columns, cells)
    if empty_price_cells > 0:
        warnings.append(
            f'{empty_price_cells} Preis-Zellen sind leer. '
            'Dies kann zu Fehlern bei der Preisberechnung führen.'
        )
        info['empty_price_cells'] = empty_price_cells
    
    # Gesamtvalidierung
    valid = len(errors) == 0
    
    return {
        'valid': valid,
        'errors': errors,
        'warnings': warnings,
        'info': info
    }


def _validate_column_a_numeric(
    rows: List[Dict[str, Any]],
    columns: List[Dict[str, Any]],
    cells: Dict[tuple, Dict[str, Any]]
) -> List[str]:
    """
    Validiert dass Spalte A (Position 0) numerische Werte enthält
    
    Requirement 2.1
    """
    errors = []
    
    if not columns:
        return errors
    
    # Finde Spalte A (Position 0)
    column_a = next((col for col in columns if col['position'] == 0), None)
    
    if not column_a:
        errors.append('Spalte A (Position 0) nicht gefunden')
        return errors
    
    column_a_id = column_a['id']
    
    # Prüfe alle Zeilen außer der ersten (Header)
    non_numeric_rows = []
    
    for row in rows:
        if row['position'] == 0:
            # Überspringe Header-Zeile
            continue
        
        row_id = row['id']
        cell_key = (row_id, column_a_id)
        
        if cell_key in cells:
            cell_data = cells[cell_key]
            raw_input = cell_data.get('raw_input')
            value = cell_data.get('value')
            
            # Prüfe ob Wert numerisch ist
            if value is None and raw_input:
                # Versuche raw_input zu parsen
                try:
                    float(str(raw_input).replace(',', '.'))
                except (ValueError, TypeError):
                    non_numeric_rows.append(f"Zeile {row['position'] + 1} ('{row['label']}')")
            elif value is None:
                # Leere Zelle in Spalte A
                non_numeric_rows.append(f"Zeile {row['position'] + 1} ('{row['label']}') - leer")
    
    if non_numeric_rows:
        errors.append(
            f"Spalte A muss numerische Werte (Modulanzahl) enthalten. "
            f"Folgende Zeilen sind nicht numerisch: {', '.join(non_numeric_rows)}"
        )
    
    return errors


def _validate_row_1_text(
    rows: List[Dict[str, Any]],
    columns: List[Dict[str, Any]],
    cells: Dict[tuple, Dict[str, Any]]
) -> List[str]:
    """
    Validiert dass Zeile 1 (Position 0) Text-Werte enthält
    
    Requirement 2.2
    """
    errors = []
    
    if not rows:
        return errors
    
    # Finde Zeile 1 (Position 0)
    row_1 = next((row for row in rows if row['position'] == 0), None)
    
    if not row_1:
        errors.append('Zeile 1 (Position 0) nicht gefunden')
        return errors
    
    row_1_id = row_1['id']
    
    # Prüfe alle Spalten außer der ersten (Modulanzahl-Spalte)
    empty_columns = []
    
    for column in columns:
        if column['position'] == 0:
            # Überspringe Modulanzahl-Spalte
            continue
        
        column_id = column['id']
        cell_key = (row_1_id, column_id)
        
        if cell_key not in cells:
            empty_columns.append(f"Spalte {_get_column_letter(column['position'])} (Position {column['position']})")
        else:
            cell_data = cells[cell_key]
            raw_input = cell_data.get('raw_input')
            value = cell_data.get('value')
            
            # Zeile 1 sollte Text enthalten (Speichermodell-Namen)
            if not raw_input and value is None:
                empty_columns.append(f"Spalte {_get_column_letter(column['position'])} (Position {column['position']})")
    
    if empty_columns:
        errors.append(
            f"Zeile 1 muss Text-Werte (Speichermodell-Namen) enthalten. "
            f"Folgende Spalten sind leer: {', '.join(empty_columns)}"
        )
    
    return errors


def _validate_no_storage_column(columns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prüft ob mindestens eine "Kein Speicher" Spalte vorhanden ist
    
    Requirement 2.3
    """
    # Mögliche Bezeichnungen für "Kein Speicher"
    no_storage_keywords = [
        'kein speicher',
        'ohne speicher',
        'no storage',
        'none',
        'kein',
        'ohne'
    ]
    
    for column in columns:
        label_lower = column['label'].lower().strip()
        
        for keyword in no_storage_keywords:
            if keyword in label_lower:
                return {
                    'found': True,
                    'column_label': column['label'],
                    'column_id': column['id'],
                    'column_position': column['position']
                }
    
    return {'found': False}


def _validate_price_cells(
    rows: List[Dict[str, Any]],
    columns: List[Dict[str, Any]],
    cells: Dict[tuple, Dict[str, Any]]
) -> List[str]:
    """
    Validiert dass Preis-Zellen Zahlen oder leer sind
    
    Requirement 2.4
    """
    errors = []
    invalid_cells = []
    
    # Prüfe alle Zellen außer Header-Zeile und Modulanzahl-Spalte
    for row in rows:
        if row['position'] == 0:
            # Überspringe Header-Zeile
            continue
        
        for column in columns:
            if column['position'] == 0:
                # Überspringe Modulanzahl-Spalte
                continue
            
            cell_key = (row['id'], column['id'])
            
            if cell_key in cells:
                cell_data = cells[cell_key]
                value = cell_data.get('value')
                raw_input = cell_data.get('raw_input')
                data_type = cell_data.get('data_type', 'text')
                
                # Preis-Zellen müssen numerisch sein oder leer
                if value is None and raw_input:
                    # Versuche zu parsen
                    try:
                        float(str(raw_input).replace(',', '.'))
                    except (ValueError, TypeError):
                        # Nicht-numerischer Wert in Preis-Zelle
                        cell_ref = f"{_get_column_letter(column['position'])}{row['position'] + 1}"
                        invalid_cells.append(f"{cell_ref} ('{raw_input}')")
    
    if invalid_cells:
        errors.append(
            f"Preis-Zellen müssen numerische Werte enthalten. "
            f"Folgende Zellen sind ungültig: {', '.join(invalid_cells)}"
        )
    
    return errors


def _extract_module_counts(
    rows: List[Dict[str, Any]],
    columns: List[Dict[str, Any]],
    cells: Dict[tuple, Dict[str, Any]]
) -> List[Any]:
    """Extrahiert alle Modulanzahlen aus Spalte A"""
    module_counts = []
    
    if not columns:
        return module_counts
    
    column_a = next((col for col in columns if col['position'] == 0), None)
    if not column_a:
        return module_counts
    
    column_a_id = column_a['id']
    
    for row in rows:
        if row['position'] == 0:
            continue
        
        cell_key = (row['id'], column_a_id)
        if cell_key in cells:
            cell_data = cells[cell_key]
            value = cell_data.get('value')
            raw_input = cell_data.get('raw_input')
            
            if value is not None:
                module_counts.append(value)
            elif raw_input:
                try:
                    module_counts.append(float(str(raw_input).replace(',', '.')))
                except (ValueError, TypeError):
                    pass
    
    return sorted(module_counts)


def _extract_storage_models(
    rows: List[Dict[str, Any]],
    columns: List[Dict[str, Any]],
    cells: Dict[tuple, Dict[str, Any]]
) -> List[str]:
    """Extrahiert alle Speichermodell-Namen aus Zeile 1"""
    storage_models = []
    
    if not rows:
        return storage_models
    
    row_1 = next((row for row in rows if row['position'] == 0), None)
    if not row_1:
        return storage_models
    
    row_1_id = row_1['id']
    
    for column in columns:
        if column['position'] == 0:
            continue
        
        cell_key = (row_1_id, column['id'])
        if cell_key in cells:
            cell_data = cells[cell_key]
            raw_input = cell_data.get('raw_input')
            
            if raw_input:
                storage_models.append(str(raw_input))
    
    return storage_models


def _count_empty_price_cells(
    rows: List[Dict[str, Any]],
    columns: List[Dict[str, Any]],
    cells: Dict[tuple, Dict[str, Any]]
) -> int:
    """Zählt leere Preis-Zellen"""
    empty_count = 0
    
    for row in rows:
        if row['position'] == 0:
            continue
        
        for column in columns:
            if column['position'] == 0:
                continue
            
            cell_key = (row['id'], column['id'])
            
            if cell_key not in cells:
                empty_count += 1
            else:
                cell_data = cells[cell_key]
                value = cell_data.get('value')
                raw_input = cell_data.get('raw_input')
                
                if value is None and not raw_input:
                    empty_count += 1
    
    return empty_count


def _get_column_letter(position: int) -> str:
    """
    Konvertiert Spaltenposition zu Excel-Buchstaben (A, B, C, ..., Z, AA, AB, ...)
    
    Args:
        position: Spaltenposition (0-basiert)
        
    Returns:
        Spaltenbuchstabe (z.B. 'A', 'B', 'AA')
    """
    label = ""
    position += 1  # Excel ist 1-basiert
    
    while position > 0:
        position -= 1
        label = chr(65 + (position % 26)) + label
        position //= 26
    
    return label


def get_validation_summary(validation_result: Dict[str, Any]) -> str:
    """
    Erstellt eine lesbare Zusammenfassung des Validierungsergebnisses
    
    Args:
        validation_result: Ergebnis von validate_matrix_for_pricing()
        
    Returns:
        Formatierte Zusammenfassung als String
    """
    lines = []
    
    if validation_result['valid']:
        lines.append("[OK] Matrix ist gültig für Preisberechnung")
    else:
        lines.append("[ERROR] Matrix ist NICHT gültig für Preisberechnung")
    
    lines.append("")
    
    # Fehler
    if validation_result['errors']:
        lines.append("FEHLER:")
        for error in validation_result['errors']:
            lines.append(f"  • {error}")
        lines.append("")
    
    # Warnungen
    if validation_result['warnings']:
        lines.append("WARNUNGEN:")
        for warning in validation_result['warnings']:
            lines.append(f"  ⚠ {warning}")
        lines.append("")
    
    # Informationen
    info = validation_result.get('info', {})
    if info:
        lines.append("INFORMATIONEN:")
        lines.append(f"  • Zeilen: {info.get('total_rows', 0)}")
        lines.append(f"  • Spalten: {info.get('total_columns', 0)}")
        lines.append(f"  • Zellen mit Werten: {info.get('total_cells', 0)}")
        
        if 'no_storage_column' in info:
            lines.append(f"  • 'Kein Speicher' Spalte: {info['no_storage_column']}")
        
        if 'module_counts' in info and info['module_counts']:
            counts_str = ', '.join(str(c) for c in info['module_counts'][:10])
            if len(info['module_counts']) > 10:
                counts_str += f", ... ({len(info['module_counts'])} gesamt)"
            lines.append(f"  • Modulanzahlen: {counts_str}")
        
        if 'storage_models' in info and info['storage_models']:
            models_str = ', '.join(info['storage_models'][:5])
            if len(info['storage_models']) > 5:
                models_str += f", ... ({len(info['storage_models'])} gesamt)"
            lines.append(f"  • Speichermodelle: {models_str}")
        
        if 'empty_price_cells' in info:
            lines.append(f"  • Leere Preis-Zellen: {info['empty_price_cells']}")
    
    return "\n".join(lines)


# Beispiel-Matrix-Struktur für Dokumentation
EXAMPLE_MATRIX_STRUCTURE = """
Beispiel-Struktur einer gültigen Preismatrix:

         A              B              C              D
    (Modulanzahl)  (10kWh)        (15kWh)        (Kein Speicher)
1   Modulanzahl    10kWh          15kWh          Kein Speicher
2   10             15000.00       17500.00       12000.00
3   15             18000.00       20500.00       15000.00
4   20             21000.00       23500.00       18000.00
5   25             24000.00       26500.00       21000.00

Regeln:
- Spalte A: Numerische Werte (Modulanzahl)
- Zeile 1: Text-Werte (Speichermodell-Namen)
- Mindestens eine "Kein Speicher" Spalte
- Preis-Zellen (B2:D5): Numerische Werte oder leer
"""


__all__ = [
    'validate_matrix_for_pricing',
    'get_validation_summary',
    'EXAMPLE_MATRIX_STRUCTURE'
]
