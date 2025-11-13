"""price_matrix_lookup.py

Lookup-Logik für die Preismatrix-basierte Preisberechnung.

Diese Modul implementiert die INDEX-basierte Preisabfrage aus der Preismatrix:
- Modulanzahl-Suche mit Floor-Logik (nächst-kleinere Zahl)
- Speichermodell-Suche mit "Kein Speicher" Fallback
- Preis-Lookup an der Kreuzung von Zeile und Spalte
- Umfassende Fehlerbehandlung und Validierung
- Performance-Monitoring und Optimierung

Struktur der Preismatrix:
- Spalte A (Index 0): Modulanzahlen (numerisch, aufsteigend sortiert)
- Zeile 1 (Index 0): Speichermodell-Namen (Text)
- Zellen: Schlüsselfertige Preise (numerisch)

Beispiel:
    Spalte A: 10, 15, 20, 25, 30
    Zeile 1: "10kWh", "15kWh", "20kWh", "Kein Speicher"
    Zelle (20, "15kWh"): 18500.00
"""

from typing import Any, Optional, Tuple, List
import time
import price_matrix_store
from price_matrix_error_handler import (
    log_matrix_lookup_attempt,
    log_matrix_lookup_success,
    log_matrix_lookup_error,
    create_user_friendly_error_message,
    get_fallback_price,
    validate_input_parameters,
    handle_edge_cases,
    create_detailed_error_report,
    MatrixNotFoundError,
    ModuleCountNotFoundError,
    StorageModelNotFoundError,
    PriceCellEmptyError,
    InvalidPriceError,
    logger
)

# Import comprehensive error handling (Task 8)
from price_matrix_error_handling import (
    handle_error_with_fallback,
    classify_error,
    ErrorCategory,
    ErrorSeverity
)

# Performance-Monitoring importieren
try:
    from price_matrix_performance import get_global_monitor
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False
    def get_global_monitor():
        return None


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
    matrix_id: Optional[int] = None,
    enable_fallback: bool = False
) -> dict[str, Any]:
    """
    Berechnet den Preis aus der Preismatrix basierend auf Modulanzahl und Speichermodell.
    
    Diese Funktion kombiniert alle Lookup-Schritte:
    1. Validiere Eingabeparameter
    2. Lade Matrix-Daten (aktive Matrix oder spezifische Matrix-ID)
    3. Behandle Edge Cases
    4. Finde Zeile für Modulanzahl (mit Floor-Logik)
    5. Finde Spalte für Speichermodell
    6. Hole Preis an der Kreuzung
    7. Umfassende Fehlerbehandlung mit Logging
    8. Optional: Fallback-Strategien
    
    Args:
        module_count: Anzahl der Module
        storage_model: Speichermodell-Name oder None für "Kein Speicher"
        matrix_id: Optional Matrix-ID (None = aktive Matrix)
        enable_fallback: Aktiviert Fallback-Strategien bei Fehlern
    
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
            'error_type': str | None,     # Fehlertyp für spezifische Behandlung
            'user_message': str | None,   # Benutzerfreundliche Fehlermeldung
            'fallback_used': bool,        # True wenn Fallback verwendet wurde
            'fallback_info': dict | None, # Details zum Fallback
            'debug_info': dict | None     # Debug-Informationen
        }
        
    Fehlertypen:
        - 'invalid_input': Ungültige Eingabeparameter
        - 'no_matrix': Keine aktive Matrix gefunden
        - 'empty_matrix': Matrix ist leer
        - 'no_row': Modulanzahl nicht in Matrix gefunden
        - 'no_column': Speichermodell nicht in Matrix gefunden
        - 'no_price': Keine Preis-Zelle an Kreuzung
        - 'invalid_price': Zelle enthält ungültigen Wert
        
    Beispiel:
        >>> result = calculate_price_from_matrix(20, "15kWh")
        >>> if result['success']:
        ...     print(f"Preis: {result['base_price']} EUR")
        ...     print(f"Zeile: {result['row_used']}, Spalte: {result['column_used']}")
        >>> else:
        ...     print(result['user_message'])
    """
    start_time = time.time()
    
    # Performance-Monitoring
    monitor = get_global_monitor() if PERFORMANCE_MONITORING_AVAILABLE else None
    
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
        'error_type': None,
        'user_message': None,
        'fallback_used': False,
        'fallback_info': None,
        'debug_info': None
    }
    
    try:
        # Log lookup attempt
        log_matrix_lookup_attempt(module_count, storage_model, matrix_id)
        
        # 1. Validiere Eingabeparameter
        is_valid, validation_error = validate_input_parameters(module_count, storage_model)
        if not is_valid:
            result['error'] = validation_error
            result['error_type'] = 'invalid_input'
            result['user_message'] = f"❌ Ungültige Eingabe: {validation_error}"
            logger.warning(f"Invalid input parameters: {validation_error}")
            return result
        
        # 2. Lade Matrix-Daten
        if matrix_id is None:
            matrix_id = price_matrix_store.get_active_matrix_id()
            if matrix_id is None:
                error = MatrixNotFoundError()
                result['error'] = str(error)
                result['error_type'] = error.error_type
                result['user_message'] = create_user_friendly_error_message(error)
                log_matrix_lookup_error(error, module_count, storage_model, matrix_id)
                return result
        
        matrix_data = price_matrix_store.get_matrix_full(matrix_id)
        if not matrix_data:
            error = MatrixNotFoundError(matrix_id)
            result['error'] = str(error)
            result['error_type'] = error.error_type
            result['user_message'] = create_user_friendly_error_message(error)
            log_matrix_lookup_error(error, module_count, storage_model, matrix_id)
            return result
        
        result['matrix_id'] = matrix_id
        result['matrix_name'] = matrix_data.get('meta', {}).get('name', 'Unbekannt')
        
        # 3. Behandle Edge Cases
        edge_case_result = handle_edge_cases(module_count, storage_model, matrix_data)
        if edge_case_result:
            result.update(edge_case_result)
            result['user_message'] = f"❌ {edge_case_result['error']}"
            logger.error(f"Edge case detected: {edge_case_result['error']}")
            return result
        
        # 4. Finde Zeile für Modulanzahl
        row_label, row_id = find_module_count_row(matrix_data, module_count)
        if row_label is None or row_id is None:
            # Sammle verfügbare Modulanzahlen für bessere Fehlermeldung
            available_counts = _extract_available_module_counts(matrix_data)
            error = ModuleCountNotFoundError(module_count, available_counts)
            
            # Versuche Fallback wenn aktiviert
            if enable_fallback:
                fallback_info = get_fallback_price(module_count, storage_model, error, matrix_data)
                if fallback_info and fallback_info.get('fallback_type') == 'module_count_floor':
                    # Rekursiver Aufruf mit Fallback-Modulanzahl
                    fallback_count = fallback_info['fallback_module_count']
                    fallback_result = calculate_price_from_matrix(
                        fallback_count, storage_model, matrix_id, enable_fallback=False
                    )
                    if fallback_result['success']:
                        fallback_result['fallback_used'] = True
                        fallback_result['fallback_info'] = fallback_info
                        fallback_result['user_message'] = fallback_info['message']
                        logger.info(f"Fallback successful: {fallback_info['message']}")
                        return fallback_result
            
            result['error'] = str(error)
            result['error_type'] = error.error_type
            result['user_message'] = create_user_friendly_error_message(error)
            log_matrix_lookup_error(error, module_count, storage_model, matrix_id)
            return result
        
        result['row_used'] = row_label
        result['row_id'] = row_id
        
        # 5. Finde Spalte für Speichermodell
        column_label, column_id = find_storage_column(matrix_data, storage_model)
        if column_label is None or column_id is None:
            # Sammle verfügbare Speichermodelle für bessere Fehlermeldung
            available_models = _extract_available_storage_models(matrix_data)
            error = StorageModelNotFoundError(storage_model or "Kein Speicher", available_models)
            
            # Versuche Fallback wenn aktiviert
            if enable_fallback and storage_model is not None:
                fallback_info = get_fallback_price(module_count, storage_model, error, matrix_data)
                if fallback_info and fallback_info.get('fallback_type') == 'no_storage':
                    # Rekursiver Aufruf mit "Kein Speicher"
                    fallback_result = calculate_price_from_matrix(
                        module_count, None, matrix_id, enable_fallback=False
                    )
                    if fallback_result['success']:
                        fallback_result['fallback_used'] = True
                        fallback_result['fallback_info'] = fallback_info
                        fallback_result['user_message'] = fallback_info['message']
                        logger.info(f"Fallback successful: {fallback_info['message']}")
                        return fallback_result
            
            result['error'] = str(error)
            result['error_type'] = error.error_type
            result['user_message'] = create_user_friendly_error_message(error)
            log_matrix_lookup_error(error, module_count, storage_model, matrix_id)
            return result
        
        result['column_used'] = column_label
        result['column_id'] = column_id
        
        # 6. Hole Preis an der Kreuzung
        price = lookup_price_by_intersection(matrix_data, row_id, column_id)
        
        if price is None:
            error = PriceCellEmptyError(row_label, column_label)
            result['error'] = str(error)
            result['error_type'] = error.error_type
            result['user_message'] = create_user_friendly_error_message(error)
            log_matrix_lookup_error(error, module_count, storage_model, matrix_id)
            return result
        
        if not isinstance(price, (int, float)) or price < 0:
            error = InvalidPriceError(row_label, column_label, price)
            result['error'] = str(error)
            result['error_type'] = error.error_type
            result['user_message'] = create_user_friendly_error_message(error)
            log_matrix_lookup_error(error, module_count, storage_model, matrix_id)
            return result
        
        # Erfolg!
        result['success'] = True
        result['base_price'] = float(price)
        
        # Log success
        execution_time_ms = (time.time() - start_time) * 1000
        log_matrix_lookup_success(result, execution_time_ms)
        
        return result
        
    except Exception as e:
        # Unerwarteter Fehler - erstelle detaillierten Bericht
        logger.exception(f"Unexpected error in calculate_price_from_matrix: {e}")
        
        result['error'] = f"Unerwarteter Fehler: {str(e)}"
        result['error_type'] = 'unexpected_error'
        result['user_message'] = (
            "❌ Ein unerwarteter Fehler ist aufgetreten.\n\n"
            "Bitte kontaktieren Sie den Administrator und geben Sie folgende Informationen an:\n"
            f"• Modulanzahl: {module_count}\n"
            f"• Speichermodell: {storage_model}\n"
            f"• Fehler: {str(e)}"
        )
        result['debug_info'] = create_detailed_error_report(
            e, module_count, storage_model, matrix_id, matrix_data
        )
        
        return result


def _extract_available_module_counts(matrix_data: dict) -> List[int]:
    """Extrahiert alle verfügbaren Modulanzahlen aus der Matrix"""
    counts = []
    rows = matrix_data.get('rows', [])
    
    for row in rows:
        if row.get('position', 0) == 0:
            continue  # Skip header
        
        label = row.get('label', '')
        try:
            count = int(float(str(label).replace(',', '.')))
            counts.append(count)
        except (ValueError, TypeError):
            pass
    
    return sorted(counts)


def _extract_available_storage_models(matrix_data: dict) -> List[str]:
    """Extrahiert alle verfügbaren Speichermodelle aus der Matrix"""
    models = []
    columns = matrix_data.get('columns', [])
    
    for column in columns:
        if column.get('position', 0) == 0:
            continue  # Skip module count column
        
        label = column.get('label', '')
        if label:
            models.append(label)
    
    return models


def calculate_price_from_matrix_safe(
    module_count: int,
    storage_model: Optional[str],
    matrix_id: Optional[int] = None,
    enable_fallback: bool = True,
    notify_admin: bool = True
) -> dict[str, Any]:
    """
    Sichere Preisberechnung mit umfassender Fehlerbehandlung
    
    Diese Funktion ist ein Wrapper um calculate_price_from_matrix() mit:
    - Automatischer Fehlerklassifizierung
    - Fallback-Mechanismen
    - Admin-Benachrichtigungen
    - Benutzerfreundliche Fehlermeldungen
    
    Args:
        module_count: Anzahl der Module
        storage_model: Speichermodell-Name oder None für "Kein Speicher"
        matrix_id: Optional Matrix-ID (None = aktive Matrix)
        enable_fallback: Aktiviert Fallback-Strategien bei Fehlern
        notify_admin: Admin bei kritischen Fehlern benachrichtigen
    
    Returns:
        Dictionary mit erweiterten Feldern:
        {
            'success': bool,
            'base_price': float | None,
            'row_used': str | None,
            'column_used': str | None,
            'matrix_id': int | None,
            'matrix_name': str | None,
            'error': str | None,
            'error_type': str | None,
            'user_message': str | None,
            'fallback_used': bool,
            'fallback_info': dict | None,
            'admin_notified': bool,
            'error_info': dict | None,  # Strukturierte Fehlerinfo
            'error_severity': str | None,
            'error_category': str | None,
            'suggestions': list | None
        }
        
    Requirement 8.5
    
    Beispiel:
        >>> result = calculate_price_from_matrix_safe(20, "15kWh", enable_fallback=True)
        >>> if result['success']:
        ...     print(f"Preis: {result['base_price']} EUR")
        ...     if result['fallback_used']:
        ...         print(f"Hinweis: {result['fallback_info']['message']}")
        >>> else:
        ...     print(result['user_message'])
        ...     for suggestion in result.get('suggestions', []):
        ...         print(f"  - {suggestion}")
    """
    try:
        # Versuche normale Berechnung
        result = calculate_price_from_matrix(
            module_count,
            storage_model,
            matrix_id,
            enable_fallback=enable_fallback
        )
        
        # Wenn erfolgreich, erweitere Ergebnis
        if result['success']:
            result['error_severity'] = None
            result['error_category'] = None
            result['suggestions'] = []
            result['admin_notified'] = False
            return result
        
        # Bei Fehler: Verwende umfassende Fehlerbehandlung
        # Erstelle Exception aus Fehlertyp
        error_type = result.get('error_type')
        error_msg = result.get('error', 'Unbekannter Fehler')
        
        if error_type == 'no_matrix':
            error = MatrixNotFoundError(matrix_id)
        elif error_type == 'no_row':
            available = _extract_available_module_counts(
                price_matrix_store.get_matrix_full(matrix_id) if matrix_id else {}
            )
            error = ModuleCountNotFoundError(module_count, available)
        elif error_type == 'no_column':
            error = StorageModelNotFoundError(storage_model or "Kein Speicher")
        elif error_type == 'no_price':
            error = PriceCellEmptyError(
                result.get('row_used', '?'),
                result.get('column_used', '?')
            )
        elif error_type == 'invalid_price':
            error = InvalidPriceError(
                result.get('row_used', '?'),
                result.get('column_used', '?'),
                '?'
            )
        else:
            error = Exception(error_msg)
        
        # Lade Matrix-Daten für Fallback
        matrix_data = None
        if matrix_id:
            matrix_data = price_matrix_store.get_matrix_full(matrix_id)
        elif enable_fallback:
            active_id = price_matrix_store.get_active_matrix_id()
            if active_id:
                matrix_data = price_matrix_store.get_matrix_full(active_id)
        
        # Verwende umfassende Fehlerbehandlung
        error_result = handle_error_with_fallback(
            error,
            module_count,
            storage_model,
            matrix_data,
            enable_fallback=enable_fallback,
            notify_admin=notify_admin
        )
        
        # Wenn Fallback erfolgreich war, versuche erneut
        if error_result.get('fallback_used'):
            fallback_data = error_result.get('fallback_result', {}).get('data', {})
            
            if fallback_data.get('fallback_type') == 'module_count_floor':
                # Rekursiver Aufruf mit Fallback-Modulanzahl
                fallback_count = fallback_data.get('fallback_module_count')
                if fallback_count:
                    fallback_result = calculate_price_from_matrix(
                        fallback_count,
                        storage_model,
                        matrix_id,
                        enable_fallback=False
                    )
                    if fallback_result['success']:
                        fallback_result['fallback_used'] = True
                        fallback_result['fallback_info'] = fallback_data
                        fallback_result['user_message'] = error_result.get('user_message')
                        fallback_result['admin_notified'] = error_result.get('admin_notified', False)
                        return fallback_result
            
            elif fallback_data.get('fallback_type') == 'no_storage':
                # Rekursiver Aufruf mit "Kein Speicher"
                fallback_result = calculate_price_from_matrix(
                    module_count,
                    None,
                    matrix_id,
                    enable_fallback=False
                )
                if fallback_result['success']:
                    fallback_result['fallback_used'] = True
                    fallback_result['fallback_info'] = fallback_data
                    fallback_result['user_message'] = error_result.get('user_message')
                    fallback_result['admin_notified'] = error_result.get('admin_notified', False)
                    return fallback_result
            
            elif fallback_data.get('fallback_to_standard'):
                # Fallback auf Standardberechnung
                result['fallback_used'] = True
                result['fallback_info'] = {
                    'fallback_type': 'standard_calculation',
                    'message': 'Verwende Standardberechnung da keine Matrix verfügbar'
                }
                result['user_message'] = error_result.get('user_message')
                result['admin_notified'] = error_result.get('admin_notified', False)
                return result
        
        # Kein erfolgreicher Fallback - erweitere Fehlerinfo
        error_info_dict = error_result.get('error_info', {})
        result['error_info'] = error_info_dict
        result['error_severity'] = error_info_dict.get('severity')
        result['error_category'] = error_info_dict.get('category')
        result['suggestions'] = error_info_dict.get('suggestions', [])
        result['user_message'] = error_result.get('user_message')
        result['admin_notified'] = error_result.get('admin_notified', False)
        
        return result
        
    except Exception as e:
        # Unerwarteter Fehler
        logger.exception(f"Unexpected error in calculate_price_from_matrix_safe: {e}")
        
        error_result = handle_error_with_fallback(
            e,
            module_count,
            storage_model,
            None,
            enable_fallback=False,
            notify_admin=notify_admin
        )
        
        return {
            'success': False,
            'base_price': None,
            'row_used': None,
            'column_used': None,
            'matrix_id': matrix_id,
            'matrix_name': None,
            'error': str(e),
            'error_type': 'unexpected_error',
            'user_message': error_result.get('user_message'),
            'fallback_used': False,
            'fallback_info': None,
            'admin_notified': error_result.get('admin_notified', False),
            'error_info': error_result.get('error_info'),
            'error_severity': error_result.get('error_info', {}).get('severity'),
            'error_category': error_result.get('error_info', {}).get('category'),
            'suggestions': error_result.get('error_info', {}).get('suggestions', [])
        }


__all__ = [
    'find_module_count_row',
    'find_storage_column',
    'lookup_price_by_intersection',
    'calculate_price_from_matrix',
    'calculate_price_from_matrix_safe',
    '_extract_available_module_counts',
    '_extract_available_storage_models'
]
