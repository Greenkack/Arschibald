"""
Robustness & Stability Core Module
===================================

Zentrale Robustheitsmuster für Wärmepumpen- und Unterkonstruktions-Module.
Implementiert Best Practices aus core/-Modulen.

Author: Bokuk2 System
Date: 2025-11-06
Version: 1.0.0
"""

import logging
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
import sys

# Structlog Setup
try:
    import structlog
    logger = structlog.get_logger(__name__)
    STRUCTLOG_AVAILABLE = True
except ImportError:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    STRUCTLOG_AVAILABLE = False


# ============================================================================
# 1. PICKLE-SERIALISIERUNG für Streamlit Session State
# ============================================================================

class PickleSerializable:
    """
    Mixin für Pickle-Serialisierung (Session State Kompatibilität).
    
    Usage:
        class MyDataClass(PickleSerializable):
            def __init__(self, data):
                self.data = data
    """
    
    def __getstate__(self):
        """Ermöglicht Pickle-Serialisierung für Session State"""
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        """Ermöglicht Pickle-Deserialisierung für Session State"""
        self.__dict__.update(state)


# ============================================================================
# 2. ERROR HANDLING & LOGGING
# ============================================================================

T = TypeVar('T')


def safe_execute(
    func: Callable[..., T],
    *args,
    fallback_value: Optional[T] = None,
    error_message: str = "Error executing function",
    log_error: bool = True,
    **kwargs
) -> T:
    """
    Sichere Ausführung einer Funktion mit Error Handling.
    
    Args:
        func: Funktion zum Ausführen
        *args: Positionsargumente
        fallback_value: Rückgabewert bei Fehler
        error_message: Custom Error Message
        log_error: Ob Fehler geloggt werden sollen
        **kwargs: Keyword-Argumente
        
    Returns:
        Funktionsergebnis oder fallback_value
        
    Example:
        result = safe_execute(
            risky_function,
            arg1, arg2,
            fallback_value=0.0,
            error_message="Calculation failed"
        )
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(
                error_message,
                function=func.__name__,
                error=str(e),
                traceback=traceback.format_exc()
            )
        return fallback_value


def safe_function(
    fallback_value: Any = None,
    error_message: str = "Function execution failed"
):
    """
    Decorator für sichere Funktionsausführung.
    
    Args:
        fallback_value: Rückgabewert bei Fehler
        error_message: Custom Error Message
        
    Example:
        @safe_function(fallback_value=0.0, error_message="Calc failed")
        def calculate_cop(temp_in, temp_out):
            return temp_in / (temp_out - temp_in)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    error_message,
                    function=func.__name__,
                    error=str(e),
                    args=args,
                    kwargs=kwargs
                )
                return fallback_value
        return wrapper
    return decorator


@contextmanager
def error_context(
    operation: str,
    raise_on_error: bool = False,
    log_level: str = "error"
):
    """
    Context Manager für Error Handling mit Logging.
    
    Args:
        operation: Beschreibung der Operation
        raise_on_error: Ob Exception erneut geworfen werden soll
        log_level: Log-Level (error, warning, info)
        
    Example:
        with error_context("Database query", raise_on_error=False):
            result = db.query(...)
    """
    try:
        yield
    except Exception as e:
        log_func = getattr(logger, log_level, logger.error)
        log_func(
            f"Error in {operation}",
            operation=operation,
            error=str(e),
            traceback=traceback.format_exc()
        )
        if raise_on_error:
            raise


# ============================================================================
# 3. VALIDATION & TYPE CHECKING
# ============================================================================

def validate_numeric(
    value: Any,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_none: bool = False,
    default: Optional[float] = None
) -> Optional[float]:
    """
    Validiert numerische Werte.
    
    Args:
        value: Zu validierender Wert
        min_value: Minimalwert (inklusiv)
        max_value: Maximalwert (inklusiv)
        allow_none: Ob None erlaubt ist
        default: Default-Wert bei ungültigem Input
        
    Returns:
        Validierter float-Wert oder default
        
    Example:
        temperature = validate_numeric(user_input, min_value=-20, max_value=50, default=20.0)
    """
    if value is None:
        return None if allow_none else default
    
    try:
        num_value = float(value)
        
        if min_value is not None and num_value < min_value:
            logger.warning(f"Value {num_value} below minimum {min_value}, using default")
            return default
        
        if max_value is not None and num_value > max_value:
            logger.warning(f"Value {num_value} above maximum {max_value}, using default")
            return default
        
        return num_value
    
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid numeric value: {value}, using default: {e}")
        return default


def validate_dict_keys(
    data: Dict[str, Any],
    required_keys: List[str],
    optional_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validiert Dictionary-Keys.
    
    Args:
        data: Zu validierendes Dictionary
        required_keys: Erforderliche Keys
        optional_keys: Optionale Keys
        
    Returns:
        Validiertes Dictionary mit Defaults für fehlende Keys
        
    Example:
        config = validate_dict_keys(
            user_config,
            required_keys=['temp_in', 'temp_out'],
            optional_keys=['cop', 'efficiency']
        )
    """
    validated = data.copy() if isinstance(data, dict) else {}
    
    # Check required keys
    missing_keys = [key for key in required_keys if key not in validated]
    if missing_keys:
        logger.error(f"Missing required keys: {missing_keys}")
        # Set to None or raise exception
        for key in missing_keys:
            validated[key] = None
    
    # Remove unknown keys
    if optional_keys is not None:
        allowed_keys = set(required_keys + optional_keys)
        unknown_keys = [key for key in validated.keys() if key not in allowed_keys]
        if unknown_keys:
            logger.warning(f"Removing unknown keys: {unknown_keys}")
            for key in unknown_keys:
                del validated[key]
    
    return validated


# ============================================================================
# 4. CONFIGURATION & CONSTANTS
# ============================================================================

@dataclass
class RobustConfig(PickleSerializable):
    """
    Konfiguration mit Pickle-Support.
    
    Example:
        config = RobustConfig(
            max_retries=3,
            timeout_seconds=30.0
        )
    """
    max_retries: int = 3
    timeout_seconds: float = 30.0
    enable_logging: bool = True
    fallback_enabled: bool = True
    validation_enabled: bool = True


# ============================================================================
# 5. RETRY MECHANISM
# ============================================================================

def retry_on_failure(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator für Retry-Mechanismus.
    
    Args:
        max_attempts: Maximale Versuche
        delay_seconds: Initiale Verzögerung
        backoff_factor: Exponentieller Backoff-Faktor
        exceptions: Tuple von Exception-Typen
        
    Example:
        @retry_on_failure(max_attempts=5, delay_seconds=2.0)
        def fetch_external_data():
            return requests.get(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            attempt = 0
            current_delay = delay_seconds
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(
                            f"Max retries reached for {func.__name__}",
                            attempts=attempt,
                            error=str(e)
                        )
                        raise
                    
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__}",
                        error=str(e),
                        delay=current_delay
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            return None
        return wrapper
    return decorator


# ============================================================================
# 6. PERFORMANCE MONITORING
# ============================================================================

@contextmanager
def performance_timer(operation: str, log_threshold_ms: float = 100.0):
    """
    Context Manager für Performance-Messung.
    
    Args:
        operation: Name der Operation
        log_threshold_ms: Log-Schwelle in Millisekunden
        
    Example:
        with performance_timer("Database query", log_threshold_ms=50.0):
            result = expensive_operation()
    """
    import time
    start_time = time.time()
    
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        
        if duration_ms > log_threshold_ms:
            logger.warning(
                f"Slow operation: {operation}",
                duration_ms=round(duration_ms, 2),
                threshold_ms=log_threshold_ms
            )
        else:
            logger.debug(
                f"Operation completed: {operation}",
                duration_ms=round(duration_ms, 2)
            )


# ============================================================================
# 7. DATA PROTECTION
# ============================================================================

def sanitize_input(
    text: str,
    max_length: int = 1000,
    allowed_chars: Optional[str] = None,
    remove_sql_keywords: bool = True
) -> str:
    """
    Sanitiert User-Input.
    
    Args:
        text: Zu sanitisierender Text
        max_length: Maximale Länge
        allowed_chars: Erlaubte Zeichen (Regex)
        remove_sql_keywords: SQL-Keywords entfernen
        
    Returns:
        Sanitisierter Text
        
    Example:
        safe_name = sanitize_input(user_input, max_length=50)
    """
    import re
    
    if not isinstance(text, str):
        return ""
    
    # Truncate
    text = text[:max_length]
    
    # Remove SQL keywords
    if remove_sql_keywords:
        sql_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', 'UNION', 'EXEC', 'SCRIPT']
        for keyword in sql_keywords:
            text = re.sub(rf'\b{keyword}\b', '', text, flags=re.IGNORECASE)
    
    # Filter allowed chars
    if allowed_chars:
        text = re.sub(f'[^{allowed_chars}]', '', text)
    
    return text.strip()


# ============================================================================
# 8. UTILITY FUNCTIONS
# ============================================================================

def get_module_info() -> Dict[str, Any]:
    """
    Gibt Modul-Informationen zurück.
    
    Returns:
        Dictionary mit Modul-Infos
    """
    return {
        'structlog_available': STRUCTLOG_AVAILABLE,
        'python_version': sys.version,
        'timestamp': datetime.now().isoformat()
    }


def log_function_call(func: Callable) -> Callable:
    """
    Decorator zum Loggen von Funktionsaufrufen.
    
    Example:
        @log_function_call
        def calculate_something(x, y):
            return x + y
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(
            f"Calling function: {func.__name__}",
            args=args,
            kwargs=kwargs
        )
        
        try:
            result = func(*args, **kwargs)
            logger.info(
                f"Function {func.__name__} completed successfully",
                result_type=type(result).__name__
            )
            return result
        except Exception as e:
            logger.error(
                f"Function {func.__name__} failed",
                error=str(e)
            )
            raise
    
    return wrapper


# ============================================================================
# 9. EXPORT
# ============================================================================

__all__ = [
    'PickleSerializable',
    'safe_execute',
    'safe_function',
    'error_context',
    'validate_numeric',
    'validate_dict_keys',
    'RobustConfig',
    'retry_on_failure',
    'performance_timer',
    'sanitize_input',
    'get_module_info',
    'log_function_call',
    'logger'
]
