"""price_matrix_error_handling.py

Zentrale Fehlerbehandlung und Validierung für das Preismatrix-System.

Dieses Modul konsolidiert alle Fehlerbehandlungs- und Validierungsfunktionen
und bietet eine einheitliche Schnittstelle für:

1. Fehler-Typen Definition (Task 8.1)
   - Matrix nicht gefunden
   - Modulanzahl nicht in Matrix
   - Speichermodell nicht in Matrix
   - Zelle leer oder ungültig
   - Zelle enthält Text statt Zahl

2. Benutzerfreundliche Fehlermeldungen (Task 8.2)
   - Klare Fehlertexte
   - Lösungsvorschläge
   - Hinweise auf Matrix-Konfiguration

3. Fallback-Mechanismen (Task 8.3)
   - Warnung anzeigen bei Fehler
   - Optional: Fallback auf Standardberechnung
   - Admin-Benachrichtigung bei kritischen Fehlern

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.5
"""

from typing import Any, Dict, Optional, List, Callable
from datetime import datetime
import logging
from enum import Enum

# Import bestehende Error-Handler
from price_matrix_error_handler import (
    PriceMatrixError,
    MatrixNotFoundError,
    ModuleCountNotFoundError,
    StorageModelNotFoundError,
    PriceCellEmptyError,
    InvalidPriceError,
    create_user_friendly_error_message,
    get_fallback_price,
    validate_input_parameters,
    handle_edge_cases,
    create_detailed_error_report,
    logger
)

from price_matrix_validation import (
    validate_matrix_for_pricing,
    get_validation_summary
)


# ============================================================================
# Task 8.1: Fehler-Typen Definition
# ============================================================================

class ErrorSeverity(Enum):
    """Schweregrad von Fehlern"""
    INFO = "info"           # Informativ, kein Fehler
    WARNING = "warning"     # Warnung, Betrieb möglich
    ERROR = "error"         # Fehler, Betrieb eingeschränkt
    CRITICAL = "critical"   # Kritischer Fehler, Betrieb nicht möglich


class ErrorCategory(Enum):
    """Kategorien von Fehlern"""
    MATRIX_NOT_FOUND = "matrix_not_found"           # Matrix nicht gefunden
    MODULE_COUNT_MISSING = "module_count_missing"   # Modulanzahl nicht in Matrix
    STORAGE_MODEL_MISSING = "storage_model_missing" # Speichermodell nicht in Matrix
    CELL_EMPTY = "cell_empty"                       # Zelle leer
    CELL_INVALID = "cell_invalid"                   # Zelle enthält ungültigen Wert
    VALIDATION_FAILED = "validation_failed"         # Validierung fehlgeschlagen
    INPUT_INVALID = "input_invalid"                 # Ungültige Eingabeparameter
    SYSTEM_ERROR = "system_error"                   # Systemfehler


class PriceMatrixErrorInfo:
    """
    Strukturierte Fehlerinformation
    
    Requirement 7.1, 7.2, 7.3, 7.4, 7.5
    """
    
    def __init__(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        message: str,
        user_message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        fallback_available: bool = False
    ):
        self.category = category
        self.severity = severity
        self.message = message
        self.user_message = user_message
        self.details = details or {}
        self.suggestions = suggestions or []
        self.fallback_available = fallback_available
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'category': self.category.value,
            'severity': self.severity.value,
            'message': self.message,
            'user_message': self.user_message,
            'details': self.details,
            'suggestions': self.suggestions,
            'fallback_available': self.fallback_available,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.category.value}: {self.message}"


def classify_error(error: Exception) -> PriceMatrixErrorInfo:
    """
    Klassifiziert einen Fehler und erstellt strukturierte Fehlerinformation
    
    Args:
        error: Aufgetretener Fehler
        
    Returns:
        Strukturierte Fehlerinformation
        
    Requirement 7.1, 7.2, 7.3, 7.4, 7.5
    """
    if isinstance(error, MatrixNotFoundError):
        return PriceMatrixErrorInfo(
            category=ErrorCategory.MATRIX_NOT_FOUND,
            severity=ErrorSeverity.CRITICAL,
            message=str(error),
            user_message=create_user_friendly_error_message(error),
            details=error.details,
            suggestions=[
                "Aktivieren Sie eine Preismatrix im Admin-Bereich",
                "Laden Sie eine neue Preismatrix hoch",
                "Kontaktieren Sie Ihren Administrator"
            ],
            fallback_available=True
        )
    
    elif isinstance(error, ModuleCountNotFoundError):
        return PriceMatrixErrorInfo(
            category=ErrorCategory.MODULE_COUNT_MISSING,
            severity=ErrorSeverity.ERROR,
            message=str(error),
            user_message=create_user_friendly_error_message(error),
            details=error.details,
            suggestions=[
                "Wählen Sie eine verfügbare Modulanzahl",
                "Ergänzen Sie die Preismatrix im Admin-Bereich",
                "System kann automatisch nächst-kleinere Modulanzahl verwenden"
            ],
            fallback_available=True
        )
    
    elif isinstance(error, StorageModelNotFoundError):
        return PriceMatrixErrorInfo(
            category=ErrorCategory.STORAGE_MODEL_MISSING,
            severity=ErrorSeverity.ERROR,
            message=str(error),
            user_message=create_user_friendly_error_message(error),
            details=error.details,
            suggestions=[
                "Wählen Sie ein verfügbares Speichermodell",
                "Wählen Sie 'Kein Speicher' wenn kein Speicher gewünscht",
                "Ergänzen Sie die Preismatrix im Admin-Bereich"
            ],
            fallback_available=True
        )
    
    elif isinstance(error, PriceCellEmptyError):
        return PriceMatrixErrorInfo(
            category=ErrorCategory.CELL_EMPTY,
            severity=ErrorSeverity.ERROR,
            message=str(error),
            user_message=create_user_friendly_error_message(error),
            details=error.details,
            suggestions=[
                "Ergänzen Sie den fehlenden Preis in der Matrix",
                "Wählen Sie eine andere Kombination",
                "Kontaktieren Sie Ihren Administrator"
            ],
            fallback_available=False
        )
    
    elif isinstance(error, InvalidPriceError):
        return PriceMatrixErrorInfo(
            category=ErrorCategory.CELL_INVALID,
            severity=ErrorSeverity.ERROR,
            message=str(error),
            user_message=create_user_friendly_error_message(error),
            details=error.details,
            suggestions=[
                "Korrigieren Sie den Preiswert in der Matrix",
                "Preiswerte müssen numerisch und positiv sein",
                "Kontaktieren Sie Ihren Administrator"
            ],
            fallback_available=False
        )
    
    else:
        return PriceMatrixErrorInfo(
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.CRITICAL,
            message=str(error),
            user_message=f"Ein unerwarteter Fehler ist aufgetreten: {str(error)}",
            details={'error_type': type(error).__name__},
            suggestions=[
                "Kontaktieren Sie den Administrator",
                "Prüfen Sie die System-Logs für Details"
            ],
            fallback_available=True
        )


# ============================================================================
# Task 8.2: Benutzerfreundliche Fehlermeldungen
# ============================================================================

def format_error_message_for_ui(
    error_info: PriceMatrixErrorInfo,
    include_suggestions: bool = True,
    include_details: bool = False
) -> str:
    """
    Formatiert Fehlermeldung für UI-Anzeige
    
    Args:
        error_info: Strukturierte Fehlerinformation
        include_suggestions: Lösungsvorschläge einbeziehen
        include_details: Technische Details einbeziehen
        
    Returns:
        Formatierte Fehlermeldung
        
    Requirement 7.1, 7.2, 7.3, 7.4, 7.5
    """
    lines = []
    
    # Severity-Icon
    severity_icons = {
        ErrorSeverity.INFO: "",
        ErrorSeverity.WARNING: "",
        ErrorSeverity.ERROR: "",
        ErrorSeverity.CRITICAL: "🚨"
    }
    icon = severity_icons.get(error_info.severity, "")
    
    # Hauptmeldung
    lines.append(f"{icon} {error_info.user_message}")
    lines.append("")
    
    # Lösungsvorschläge
    if include_suggestions and error_info.suggestions:
        lines.append("**Lösungsvorschläge:**")
        for suggestion in error_info.suggestions:
            lines.append(f"• {suggestion}")
        lines.append("")
    
    # Fallback-Hinweis
    if error_info.fallback_available:
        lines.append("**Hinweis:** Das System kann automatisch einen alternativen Wert verwenden.")
        lines.append("")
    
    # Technische Details (optional)
    if include_details and error_info.details:
        lines.append("**Technische Details:**")
        for key, value in error_info.details.items():
            lines.append(f"• {key}: {value}")
        lines.append("")
    
    return "\n".join(lines)


def create_admin_notification(
    error_info: PriceMatrixErrorInfo,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Erstellt Admin-Benachrichtigung für kritische Fehler
    
    Args:
        error_info: Strukturierte Fehlerinformation
        context: Zusätzlicher Kontext (z.B. Benutzer, Zeitpunkt)
        
    Returns:
        Benachrichtigungs-Dictionary
        
    Requirement 8.5
    """
    notification = {
        'type': 'price_matrix_error',
        'severity': error_info.severity.value,
        'category': error_info.category.value,
        'message': error_info.message,
        'timestamp': error_info.timestamp.isoformat(),
        'details': error_info.details,
        'requires_action': error_info.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]
    }
    
    if context:
        notification['context'] = context
    
    # Empfohlene Aktionen basierend auf Fehlertyp
    if error_info.category == ErrorCategory.MATRIX_NOT_FOUND:
        notification['recommended_actions'] = [
            "Preismatrix im Admin-Bereich aktivieren",
            "Neue Preismatrix hochladen"
        ]
    elif error_info.category == ErrorCategory.MODULE_COUNT_MISSING:
        notification['recommended_actions'] = [
            "Fehlende Modulanzahlen in Matrix ergänzen",
            "Matrix-Struktur überprüfen"
        ]
    elif error_info.category == ErrorCategory.STORAGE_MODEL_MISSING:
        notification['recommended_actions'] = [
            "Fehlende Speichermodelle in Matrix ergänzen",
            "Matrix-Struktur überprüfen"
        ]
    elif error_info.category == ErrorCategory.CELL_EMPTY:
        notification['recommended_actions'] = [
            "Leere Preis-Zellen in Matrix ausfüllen",
            "Matrix-Vollständigkeit prüfen"
        ]
    elif error_info.category == ErrorCategory.CELL_INVALID:
        notification['recommended_actions'] = [
            "Ungültige Preiswerte korrigieren",
            "Matrix-Validierung durchführen"
        ]
    
    return notification


def get_error_help_text(category: ErrorCategory) -> str:
    """
    Gibt Hilfetext für spezifischen Fehlertyp zurück
    
    Args:
        category: Fehlerkategorie
        
    Returns:
        Hilfetext mit Erklärung und Lösungsansätzen
        
    Requirement 7.1, 7.2, 7.3, 7.4, 7.5
    """
    help_texts = {
        ErrorCategory.MATRIX_NOT_FOUND: """
**Matrix nicht gefunden**

Dieser Fehler tritt auf, wenn keine aktive Preismatrix im System vorhanden ist.

**Ursachen:**
• Keine Preismatrix wurde hochgeladen
• Die aktive Matrix wurde gelöscht
• Matrix-Datenbank ist beschädigt

**Lösung:**
1. Öffnen Sie den Admin-Bereich
2. Navigieren Sie zu "Preismatrix-Verwaltung"
3. Laden Sie eine neue Matrix hoch oder aktivieren Sie eine bestehende
4. Stellen Sie sicher, dass die Matrix korrekt strukturiert ist
        """,
        
        ErrorCategory.MODULE_COUNT_MISSING: """
**Modulanzahl nicht in Matrix gefunden**

Die gewählte Modulanzahl existiert nicht in der Preismatrix.

**Ursachen:**
• Matrix enthält nicht alle benötigten Modulanzahlen
• Modulanzahl liegt außerhalb des definierten Bereichs

**Lösung:**
1. Wählen Sie eine verfügbare Modulanzahl aus der Liste
2. ODER: Ergänzen Sie die Matrix um die fehlende Modulanzahl
3. Das System kann automatisch die nächst-kleinere Modulanzahl verwenden (Floor-Logik)

**Hinweis:** Die Floor-Logik verwendet automatisch die größte Modulanzahl,
die kleiner oder gleich der gewünschten Anzahl ist.
        """,
        
        ErrorCategory.STORAGE_MODEL_MISSING: """
**Speichermodell nicht in Matrix gefunden**

Das gewählte Speichermodell existiert nicht in der Preismatrix.

**Ursachen:**
• Speichermodell wurde nicht in Matrix eingetragen
• Schreibweise des Modellnamens stimmt nicht überein
• Matrix enthält keine "Kein Speicher" Option

**Lösung:**
1. Wählen Sie ein verfügbares Speichermodell aus der Liste
2. Wählen Sie "Kein Speicher" wenn kein Speicher gewünscht
3. ODER: Ergänzen Sie die Matrix um das fehlende Speichermodell
4. Achten Sie auf exakte Schreibweise (Groß-/Kleinschreibung wird ignoriert)
        """,
        
        ErrorCategory.CELL_EMPTY: """
**Preis-Zelle ist leer**

Für die gewählte Kombination aus Modulanzahl und Speichermodell
ist kein Preis in der Matrix hinterlegt.

**Ursachen:**
• Matrix ist unvollständig
• Preis wurde vergessen einzutragen
• Kombination ist nicht verfügbar

**Lösung:**
1. Ergänzen Sie den fehlenden Preis in der Matrix
2. ODER: Wählen Sie eine andere Kombination
3. Prüfen Sie die Matrix auf Vollständigkeit

**Tipp:** Verwenden Sie die Matrix-Validierung im Admin-Bereich,
um alle leeren Zellen zu identifizieren.
        """,
        
        ErrorCategory.CELL_INVALID: """
**Ungültiger Preiswert**

Die Preis-Zelle enthält einen ungültigen Wert (z.B. Text statt Zahl).

**Ursachen:**
• Text wurde in Preis-Zelle eingegeben
• Formatierung ist falsch
• Zelle enthält Formel-Fehler

**Lösung:**
1. Öffnen Sie die Matrix im Admin-Bereich
2. Korrigieren Sie den ungültigen Wert
3. Stellen Sie sicher, dass nur numerische Werte eingegeben werden
4. Verwenden Sie Punkt oder Komma als Dezimaltrennzeichen

**Hinweis:** Preiswerte müssen positive Zahlen sein.
        """
    }
    
    return help_texts.get(category, "Keine Hilfe verfügbar für diesen Fehlertyp.")


# ============================================================================
# Task 8.3: Fallback-Mechanismen
# ============================================================================

class FallbackStrategy(Enum):
    """Fallback-Strategien"""
    NONE = "none"                           # Kein Fallback
    FLOOR_MODULE_COUNT = "floor_module"     # Nächst-kleinere Modulanzahl
    NO_STORAGE = "no_storage"               # "Kein Speicher" verwenden
    STANDARD_CALCULATION = "standard_calc"  # Standardberechnung verwenden
    DEFAULT_PRICE = "default_price"         # Standard-Preis verwenden


class FallbackResult:
    """Ergebnis eines Fallback-Versuchs"""
    
    def __init__(
        self,
        success: bool,
        strategy: FallbackStrategy,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.strategy = strategy
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'success': self.success,
            'strategy': self.strategy.value,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


def try_fallback(
    error_info: PriceMatrixErrorInfo,
    module_count: int,
    storage_model: Optional[str],
    matrix_data: Optional[Dict[str, Any]] = None,
    allowed_strategies: Optional[List[FallbackStrategy]] = None
) -> Optional[FallbackResult]:
    """
    Versucht Fallback-Strategie anzuwenden
    
    Args:
        error_info: Strukturierte Fehlerinformation
        module_count: Ursprüngliche Modulanzahl
        storage_model: Ursprüngliches Speichermodell
        matrix_data: Matrix-Daten (optional)
        allowed_strategies: Erlaubte Fallback-Strategien (None = alle)
        
    Returns:
        Fallback-Ergebnis oder None wenn kein Fallback möglich
        
    Requirement 8.5
    """
    if not error_info.fallback_available:
        return None
    
    # Standard-Strategien wenn nicht spezifiziert
    if allowed_strategies is None:
        allowed_strategies = [
            FallbackStrategy.FLOOR_MODULE_COUNT,
            FallbackStrategy.NO_STORAGE,
            FallbackStrategy.STANDARD_CALCULATION
        ]
    
    # Versuche passende Strategie basierend auf Fehlertyp
    if error_info.category == ErrorCategory.MODULE_COUNT_MISSING:
        if FallbackStrategy.FLOOR_MODULE_COUNT in allowed_strategies:
            # Verwende bestehende Fallback-Funktion
            fallback_info = get_fallback_price(
                module_count,
                storage_model,
                ModuleCountNotFoundError(module_count),
                matrix_data
            )
            
            if fallback_info and fallback_info.get('fallback_type') == 'module_count_floor':
                return FallbackResult(
                    success=True,
                    strategy=FallbackStrategy.FLOOR_MODULE_COUNT,
                    message=fallback_info['message'],
                    data=fallback_info
                )
    
    elif error_info.category == ErrorCategory.STORAGE_MODEL_MISSING:
        if FallbackStrategy.NO_STORAGE in allowed_strategies:
            # Verwende bestehende Fallback-Funktion
            fallback_info = get_fallback_price(
                module_count,
                storage_model,
                StorageModelNotFoundError(storage_model or "Kein Speicher"),
                matrix_data
            )
            
            if fallback_info and fallback_info.get('fallback_type') == 'no_storage':
                return FallbackResult(
                    success=True,
                    strategy=FallbackStrategy.NO_STORAGE,
                    message=fallback_info['message'],
                    data=fallback_info
                )
    
    elif error_info.category == ErrorCategory.MATRIX_NOT_FOUND:
        if FallbackStrategy.STANDARD_CALCULATION in allowed_strategies:
            return FallbackResult(
                success=True,
                strategy=FallbackStrategy.STANDARD_CALCULATION,
                message="Verwende Standardberechnung da keine Matrix verfügbar",
                data={'fallback_to_standard': True}
            )
    
    return None


def handle_error_with_fallback(
    error: Exception,
    module_count: int,
    storage_model: Optional[str],
    matrix_data: Optional[Dict[str, Any]] = None,
    enable_fallback: bool = True,
    notify_admin: bool = True
) -> Dict[str, Any]:
    """
    Behandelt Fehler mit automatischem Fallback
    
    Args:
        error: Aufgetretener Fehler
        module_count: Modulanzahl
        storage_model: Speichermodell
        matrix_data: Matrix-Daten (optional)
        enable_fallback: Fallback aktivieren
        notify_admin: Admin bei kritischen Fehlern benachrichtigen
        
    Returns:
        Ergebnis-Dictionary mit Fehlerinfo und Fallback-Status
        
    Requirement 8.5
    """
    # Klassifiziere Fehler
    error_info = classify_error(error)
    
    # Log Fehler
    logger.error(f"Price matrix error: {error_info}")
    
    result = {
        'success': False,
        'error_info': error_info.to_dict(),
        'user_message': format_error_message_for_ui(error_info),
        'fallback_used': False,
        'fallback_result': None,
        'admin_notified': False
    }
    
    # Versuche Fallback wenn aktiviert
    if enable_fallback and error_info.fallback_available:
        fallback_result = try_fallback(
            error_info,
            module_count,
            storage_model,
            matrix_data
        )
        
        if fallback_result and fallback_result.success:
            result['fallback_used'] = True
            result['fallback_result'] = fallback_result.to_dict()
            result['user_message'] = (
                f"{fallback_result.message}\n\n"
                f"{result['user_message']}"
            )
            logger.info(f"Fallback successful: {fallback_result.strategy.value}")
    
    # Admin-Benachrichtigung bei kritischen Fehlern
    if notify_admin and error_info.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
        notification = create_admin_notification(
            error_info,
            context={
                'module_count': module_count,
                'storage_model': storage_model,
                'fallback_used': result['fallback_used']
            }
        )
        
        # Hier würde die Benachrichtigung an Admin-System gesendet
        logger.warning(f"Admin notification created: {notification}")
        result['admin_notified'] = True
        result['admin_notification'] = notification
    
    return result


# ============================================================================
# Validierungs-Wrapper
# ============================================================================

def validate_matrix_with_error_handling(matrix_id: int) -> Dict[str, Any]:
    """
    Validiert Matrix mit umfassender Fehlerbehandlung
    
    Args:
        matrix_id: Matrix-ID
        
    Returns:
        Validierungsergebnis mit Fehlerbehandlung
        
    Requirement 7.1, 8.1
    """
    try:
        validation_result = validate_matrix_for_pricing(matrix_id)
        
        if not validation_result['valid']:
            # Erstelle Fehlerinfo aus Validierungsfehlern
            error_info = PriceMatrixErrorInfo(
                category=ErrorCategory.VALIDATION_FAILED,
                severity=ErrorSeverity.ERROR,
                message="Matrix-Validierung fehlgeschlagen",
                user_message=get_validation_summary(validation_result),
                details={
                    'errors': validation_result['errors'],
                    'warnings': validation_result['warnings']
                },
                suggestions=[
                    "Korrigieren Sie die Validierungsfehler",
                    "Prüfen Sie die Matrix-Struktur",
                    "Verwenden Sie das Beispiel als Vorlage"
                ],
                fallback_available=False
            )
            
            return {
                'valid': False,
                'validation_result': validation_result,
                'error_info': error_info.to_dict(),
                'user_message': format_error_message_for_ui(error_info)
            }
        
        return {
            'valid': True,
            'validation_result': validation_result,
            'user_message': "Matrix ist gültig für Preisberechnung"
        }
        
    except Exception as e:
        logger.exception(f"Error during matrix validation: {e}")
        
        error_info = classify_error(e)
        
        return {
            'valid': False,
            'error_info': error_info.to_dict(),
            'user_message': format_error_message_for_ui(error_info)
        }


__all__ = [
    # Enums
    'ErrorSeverity',
    'ErrorCategory',
    'FallbackStrategy',
    
    # Classes
    'PriceMatrixErrorInfo',
    'FallbackResult',
    
    # Task 8.1: Fehler-Typen
    'classify_error',
    
    # Task 8.2: Benutzerfreundliche Fehlermeldungen
    'format_error_message_for_ui',
    'create_admin_notification',
    'get_error_help_text',
    
    # Task 8.3: Fallback-Mechanismen
    'try_fallback',
    'handle_error_with_fallback',
    
    # Validierung
    'validate_matrix_with_error_handling',
    
    # Re-exports from existing modules
    'PriceMatrixError',
    'MatrixNotFoundError',
    'ModuleCountNotFoundError',
    'StorageModelNotFoundError',
    'PriceCellEmptyError',
    'InvalidPriceError'
]
