"""price_matrix_error_handler.py

Robuste Fehlerbehandlung für das Preismatrix-System.

Dieses Modul implementiert:
- Spezifische Fehlermeldungen für Matrix-Lookup Probleme
- Fallback-Strategien bei fehlenden Werten
- Verbessertes Error-Logging für Debugging
- Edge Case Handling (leere Matrix, ungültige Eingaben)

Requirements: 4.4, 1.5, 3.4
"""

import logging
from typing import Any, Dict, Optional, Tuple, List
from datetime import datetime
import traceback

# Configure logging
logger = logging.getLogger('price_matrix')
logger.setLevel(logging.DEBUG)

# Create console handler if not already configured
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


class PriceMatrixError(Exception):
    """Basis-Exception für Preismatrix-Fehler"""
    
    def __init__(self, message: str, error_type: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}
        self.timestamp = datetime.now()


class MatrixNotFoundError(PriceMatrixError):
    """Matrix wurde nicht gefunden"""
    
    def __init__(self, matrix_id: Optional[int] = None):
        message = "Keine aktive Preismatrix gefunden" if matrix_id is None else f"Matrix mit ID {matrix_id} nicht gefunden"
        super().__init__(message, 'no_matrix', {'matrix_id': matrix_id})


class ModuleCountNotFoundError(PriceMatrixError):
    """Modulanzahl nicht in Matrix gefunden"""
    
    def __init__(self, module_count: int, available_counts: Optional[List[int]] = None):
        message = f"Modulanzahl {module_count} nicht in Preismatrix gefunden"
        details = {
            'module_count': module_count,
            'available_counts': available_counts or []
        }
        super().__init__(message, 'no_row', details)


class StorageModelNotFoundError(PriceMatrixError):
    """Speichermodell nicht in Matrix gefunden"""
    
    def __init__(self, storage_model: str, available_models: Optional[List[str]] = None):
        message = f"Speichermodell '{storage_model}' nicht in Preismatrix gefunden"
        details = {
            'storage_model': storage_model,
            'available_models': available_models or []
        }
        super().__init__(message, 'no_column', details)


class PriceCellEmptyError(PriceMatrixError):
    """Preis-Zelle ist leer"""
    
    def __init__(self, row_label: str, column_label: str):
        message = f"Kein Preis für Kombination {row_label} Module + {column_label} definiert"
        details = {
            'row_label': row_label,
            'column_label': column_label
        }
        super().__init__(message, 'no_price', details)


class InvalidPriceError(PriceMatrixError):
    """Ungültiger Preiswert"""
    
    def __init__(self, row_label: str, column_label: str, invalid_value: Any):
        message = f"Ungültiger Preiswert in Zelle ({row_label}, {column_label}): {invalid_value}"
        details = {
            'row_label': row_label,
            'column_label': column_label,
            'invalid_value': invalid_value
        }
        super().__init__(message, 'invalid_price', details)


def log_matrix_lookup_attempt(
    module_count: int,
    storage_model: Optional[str],
    matrix_id: Optional[int] = None
) -> None:
    """
    Loggt einen Matrix-Lookup-Versuch für Debugging
    
    Args:
        module_count: Gesuchte Modulanzahl
        storage_model: Gesuchtes Speichermodell
        matrix_id: Matrix-ID (None = aktive Matrix)
    """
    logger.debug(
        f"Matrix-Lookup: module_count={module_count}, "
        f"storage_model={storage_model}, matrix_id={matrix_id}"
    )


def log_matrix_lookup_success(
    result: Dict[str, Any],
    execution_time_ms: float
) -> None:
    """
    Loggt einen erfolgreichen Matrix-Lookup
    
    Args:
        result: Lookup-Ergebnis
        execution_time_ms: Ausführungszeit in Millisekunden
    """
    logger.info(
        f"Matrix-Lookup erfolgreich: "
        f"base_price={result.get('base_price')}, "
        f"row={result.get('row_used')}, "
        f"column={result.get('column_used')}, "
        f"matrix={result.get('matrix_name')}, "
        f"time={execution_time_ms:.2f}ms"
    )


def log_matrix_lookup_error(
    error: PriceMatrixError,
    module_count: int,
    storage_model: Optional[str],
    matrix_id: Optional[int] = None
) -> None:
    """
    Loggt einen fehlgeschlagenen Matrix-Lookup
    
    Args:
        error: Aufgetretener Fehler
        module_count: Gesuchte Modulanzahl
        storage_model: Gesuchtes Speichermodell
        matrix_id: Matrix-ID
    """
    logger.error(
        f"Matrix-Lookup fehlgeschlagen: "
        f"error_type={error.error_type}, "
        f"message={str(error)}, "
        f"module_count={module_count}, "
        f"storage_model={storage_model}, "
        f"matrix_id={matrix_id}, "
        f"details={error.details}"
    )


def create_user_friendly_error_message(error: PriceMatrixError) -> str:
    """
    Erstellt eine benutzerfreundliche Fehlermeldung
    
    Args:
        error: Aufgetretener Fehler
        
    Returns:
        Benutzerfreundliche Fehlermeldung mit Lösungsvorschlägen
    """
    if error.error_type == 'no_matrix':
        return (
            "Keine Preismatrix gefunden.\n\n"
            "Lösungsvorschläge:\n"
            "• Aktivieren Sie eine Preismatrix im Admin-Bereich\n"
            "• Laden Sie eine neue Preismatrix hoch\n"
            "• Kontaktieren Sie Ihren Administrator"
        )
    
    elif error.error_type == 'no_row':
        details = error.details
        module_count = details.get('module_count')
        available = details.get('available_counts', [])
        
        msg = f"Modulanzahl {module_count} nicht in Preismatrix gefunden.\n\n"
        
        if available:
            # Finde nächste verfügbare Modulanzahl
            lower = [c for c in available if c < module_count]
            higher = [c for c in available if c > module_count]
            
            msg += "Verfügbare Modulanzahlen:\n"
            if lower:
                msg += f"• Nächst-kleinere: {max(lower)}\n"
            if higher:
                msg += f"• Nächst-größere: {min(higher)}\n"
            
            msg += f"\nAlle verfügbaren: {', '.join(map(str, sorted(available)))}\n\n"
        
        msg += (
            "Lösungsvorschläge:\n"
            "• Wählen Sie eine verfügbare Modulanzahl\n"
            "• Ergänzen Sie die Preismatrix im Admin-Bereich\n"
            "• Kontaktieren Sie Ihren Administrator"
        )
        
        return msg
    
    elif error.error_type == 'no_column':
        details = error.details
        storage_model = details.get('storage_model')
        available = details.get('available_models', [])
        
        msg = f"Speichermodell '{storage_model}' nicht in Preismatrix gefunden.\n\n"
        
        if available:
            msg += "Verfügbare Speichermodelle:\n"
            for model in available[:10]:  # Zeige max. 10
                msg += f"• {model}\n"
            if len(available) > 10:
                msg += f"• ... und {len(available) - 10} weitere\n"
            msg += "\n"
        
        msg += (
            "Lösungsvorschläge:\n"
            "• Wählen Sie ein verfügbares Speichermodell\n"
            "• Wählen Sie 'Kein Speicher' wenn kein Speicher gewünscht\n"
            "• Ergänzen Sie die Preismatrix im Admin-Bereich\n"
            "• Kontaktieren Sie Ihren Administrator"
        )
        
        return msg
    
    elif error.error_type == 'no_price':
        details = error.details
        row = details.get('row_label')
        col = details.get('column_label')
        
        return (
            f"Kein Preis für Kombination {row} Module + {col} definiert.\n\n"
            "Lösungsvorschläge:\n"
            "• Ergänzen Sie den fehlenden Preis in der Matrix\n"
            "• Wählen Sie eine andere Kombination\n"
            "• Kontaktieren Sie Ihren Administrator"
        )
    
    elif error.error_type == 'invalid_price':
        details = error.details
        row = details.get('row_label')
        col = details.get('column_label')
        value = details.get('invalid_value')
        
        return (
            f"Ungültiger Preiswert in Zelle ({row}, {col}): {value}\n\n"
            "Lösungsvorschläge:\n"
            "• Korrigieren Sie den Preiswert in der Matrix\n"
            "• Preiswerte müssen numerisch und positiv sein\n"
            "• Kontaktieren Sie Ihren Administrator"
        )
    
    else:
        return f"Fehler bei der Preisberechnung: {str(error)}"


def get_fallback_price(
    module_count: int,
    storage_model: Optional[str],
    error: PriceMatrixError,
    matrix_data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Versucht einen Fallback-Preis zu finden
    
    Fallback-Strategien:
    1. Bei fehlender Modulanzahl: Nächst-kleinere Modulanzahl verwenden
    2. Bei fehlendem Speichermodell: "Kein Speicher" verwenden
    3. Bei leerer Preis-Zelle: Interpolation versuchen
    
    Args:
        module_count: Gesuchte Modulanzahl
        storage_model: Gesuchtes Speichermodell
        error: Aufgetretener Fehler
        matrix_data: Matrix-Daten (optional)
        
    Returns:
        Fallback-Ergebnis oder None wenn kein Fallback möglich
    """
    if error.error_type == 'no_row' and matrix_data:
        # Strategie 1: Nächst-kleinere Modulanzahl
        available_counts = error.details.get('available_counts', [])
        lower_counts = [c for c in available_counts if c < module_count]
        
        if lower_counts:
            fallback_count = max(lower_counts)
            logger.warning(
                f"Fallback: Verwende Modulanzahl {fallback_count} "
                f"statt {module_count}"
            )
            
            return {
                'fallback_used': True,
                'fallback_type': 'module_count_floor',
                'original_module_count': module_count,
                'fallback_module_count': fallback_count,
                'message': (
                    f"Hinweis: Modulanzahl {module_count} nicht verfügbar. "
                    f"Preis für {fallback_count} Module wird verwendet."
                )
            }
    
    elif error.error_type == 'no_column':
        # Strategie 2: "Kein Speicher" als Fallback
        logger.warning(
            f"Fallback: Verwende 'Kein Speicher' "
            f"statt '{storage_model}'"
        )
        
        return {
            'fallback_used': True,
            'fallback_type': 'no_storage',
            'original_storage_model': storage_model,
            'fallback_storage_model': None,
            'message': (
                f"Hinweis: Speichermodell '{storage_model}' nicht verfügbar. "
                f"Preis ohne Speicher wird verwendet."
            )
        }
    
    return None


def validate_input_parameters(
    module_count: Any,
    storage_model: Any
) -> Tuple[bool, Optional[str]]:
    """
    Validiert Eingabeparameter vor dem Matrix-Lookup
    
    Args:
        module_count: Modulanzahl (sollte int sein)
        storage_model: Speichermodell (sollte str oder None sein)
        
    Returns:
        Tuple (is_valid, error_message)
    """
    # Validiere module_count
    if module_count is None:
        return False, "Modulanzahl darf nicht None sein"
    
    try:
        module_count_int = int(module_count)
    except (ValueError, TypeError):
        return False, f"Modulanzahl muss eine Zahl sein, erhalten: {type(module_count).__name__}"
    
    if module_count_int <= 0:
        return False, f"Modulanzahl muss größer als 0 sein, erhalten: {module_count_int}"
    
    if module_count_int > 10000:
        return False, f"Modulanzahl ist unrealistisch hoch: {module_count_int}"
    
    # Validiere storage_model
    if storage_model is not None and not isinstance(storage_model, str):
        return False, f"Speichermodell muss ein String oder None sein, erhalten: {type(storage_model).__name__}"
    
    if storage_model is not None and len(storage_model.strip()) == 0:
        return False, "Speichermodell darf nicht leer sein (verwenden Sie None für 'Kein Speicher')"
    
    return True, None


def handle_edge_cases(
    module_count: int,
    storage_model: Optional[str],
    matrix_data: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Behandelt Edge Cases vor dem Matrix-Lookup
    
    Edge Cases:
    - Leere Matrix
    - Matrix ohne Zeilen/Spalten
    - Ungültige Matrix-Struktur
    
    Args:
        module_count: Modulanzahl
        storage_model: Speichermodell
        matrix_data: Matrix-Daten
        
    Returns:
        Error-Dict wenn Edge Case erkannt, sonst None
    """
    if not matrix_data:
        return {
            'success': False,
            'error': 'Matrix-Daten konnten nicht geladen werden',
            'error_type': 'no_matrix',
            'base_price': None
        }
    
    rows = matrix_data.get('rows', [])
    columns = matrix_data.get('columns', [])
    
    if not rows or not columns:
        return {
            'success': False,
            'error': 'Matrix ist leer (keine Zeilen oder Spalten)',
            'error_type': 'empty_matrix',
            'base_price': None
        }
    
    # Prüfe ob Matrix nur Header hat (keine Datenzeilen)
    data_rows = [r for r in rows if r.get('position', 0) > 0]
    if not data_rows:
        return {
            'success': False,
            'error': 'Matrix enthält keine Datenzeilen (nur Header)',
            'error_type': 'no_data_rows',
            'base_price': None
        }
    
    # Prüfe ob Matrix nur Modulanzahl-Spalte hat (keine Speicher-Spalten)
    data_columns = [c for c in columns if c.get('position', 0) > 0]
    if not data_columns:
        return {
            'success': False,
            'error': 'Matrix enthält keine Speicher-Spalten',
            'error_type': 'no_storage_columns',
            'base_price': None
        }
    
    return None


def create_detailed_error_report(
    error: Exception,
    module_count: int,
    storage_model: Optional[str],
    matrix_id: Optional[int],
    matrix_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Erstellt einen detaillierten Fehlerbericht für Debugging
    
    Args:
        error: Aufgetretener Fehler
        module_count: Gesuchte Modulanzahl
        storage_model: Gesuchtes Speichermodell
        matrix_id: Matrix-ID
        matrix_data: Matrix-Daten (optional)
        
    Returns:
        Detaillierter Fehlerbericht
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'error_type': getattr(error, 'error_type', 'unknown'),
        'error_message': str(error),
        'error_class': type(error).__name__,
        'input_parameters': {
            'module_count': module_count,
            'storage_model': storage_model,
            'matrix_id': matrix_id
        },
        'traceback': traceback.format_exc()
    }
    
    if isinstance(error, PriceMatrixError):
        report['error_details'] = error.details
    
    if matrix_data:
        report['matrix_info'] = {
            'matrix_id': matrix_data.get('meta', {}).get('id'),
            'matrix_name': matrix_data.get('meta', {}).get('name'),
            'total_rows': len(matrix_data.get('rows', [])),
            'total_columns': len(matrix_data.get('columns', [])),
            'total_cells': len(matrix_data.get('cells', {}))
        }
    
    return report


__all__ = [
    'PriceMatrixError',
    'MatrixNotFoundError',
    'ModuleCountNotFoundError',
    'StorageModelNotFoundError',
    'PriceCellEmptyError',
    'InvalidPriceError',
    'log_matrix_lookup_attempt',
    'log_matrix_lookup_success',
    'log_matrix_lookup_error',
    'create_user_friendly_error_message',
    'get_fallback_price',
    'validate_input_parameters',
    'handle_edge_cases',
    'create_detailed_error_report',
    'logger'
]
