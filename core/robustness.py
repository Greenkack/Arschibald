"""
core/robustness.py
Zentrale Robustheit- und Stabilitäts-Utilities für maximale Zuverlässigkeit

Features:
- Error Handling mit Retry-Logic
- Session State Guards
- File I/O mit Atomic Writes
- Input Validation & Sanitization
- Memory Management
- Type Safety
"""
from __future__ import annotations

import functools
import logging
import os
import pickle
import sqlite3
import tempfile
import time
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Union

import streamlit as st

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Robustness')

T = TypeVar('T')

# ============================================================================
# ERROR HANDLING & RETRY LOGIC
# ============================================================================

def retry_on_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    fallback: Any = None,
):
    """
    Decorator für automatische Wiederholungsversuche bei Fehlern
    
    Args:
        max_attempts: Maximale Anzahl Versuche
        delay: Initiale Wartezeit in Sekunden
        backoff: Multiplikator für exponential backoff
        exceptions: Tuple von zu behandelnden Exceptions
        fallback: Rückgabewert bei finalem Fehler
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            wait_time = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"{func.__name__} Versuch {attempt+1}/{max_attempts} fehlgeschlagen: {e}"
                    )
                    
                    if attempt < max_attempts - 1:
                        logger.info(f"Warte {wait_time:.1f}s vor erneutem Versuch...")
                        time.sleep(wait_time)
                        wait_time *= backoff
                    else:
                        logger.error(f"{func.__name__} final fehlgeschlagen nach {max_attempts} Versuchen")
            
            if fallback is not None:
                logger.info(f"{func.__name__} verwendet Fallback: {fallback}")
                return fallback
            
            raise last_exception
        
        return wrapper
    return decorator


def safe_execute(func: Callable[..., T], fallback: T, *args, **kwargs) -> T:
    """
    Führe Funktion sicher aus mit Fallback bei Fehler
    
    Args:
        func: Auszuführende Funktion
        fallback: Rückgabewert bei Fehler
        *args, **kwargs: Argumente für func
    
    Returns:
        Funktionsergebnis oder Fallback
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"safe_execute Fehler in {func.__name__}: {e}")
        logger.debug(traceback.format_exc())
        return fallback


# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def init_session_state(key: str, default: Any) -> None:
    """Initialisiere Session State Key falls nicht vorhanden"""
    if key not in st.session_state:
        st.session_state[key] = default


def get_session_state(key: str, default: Any = None) -> Any:
    """Hole Session State Wert mit Fallback"""
    return st.session_state.get(key, default)


def set_session_state_safe(key: str, value: Any) -> bool:
    """
    Setze Session State Wert mit Pickle-Validierung
    
    Args:
        key: Session State Key
        value: Zu speichernder Wert
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        # Teste Pickle-Serialisierbarkeit
        pickle.dumps(value)
        st.session_state[key] = value
        return True
    except (pickle.PickleError, TypeError) as e:
        logger.error(f"Session State Fehler für '{key}': {e} (Typ: {type(value).__name__})")
        return False


class SessionStateGuard:
    """
    Context Manager für sichere Session State Operationen
    
    Usage:
        with SessionStateGuard('my_key', default=[]) as value:
            value.append('new_item')
    """
    def __init__(self, key: str, default: Any = None):
        self.key = key
        self.default = default
    
    def __enter__(self):
        init_session_state(self.key, self.default)
        return st.session_state[self.key]
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"SessionStateGuard Fehler für '{self.key}': {exc_val}")
        return False  # Propagiere Exception


# ============================================================================
# FILE I/O ROBUSTNESS
# ============================================================================

@contextmanager
def atomic_write(filepath: Union[str, Path], encoding: str = 'utf-8'):
    """
    Atomic File Write: Schreibe erst in Temp-Datei, dann rename
    
    Usage:
        with atomic_write('config.json') as f:
            json.dump(data, f)
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Erstelle Temp-Datei im gleichen Verzeichnis
    fd, temp_path = tempfile.mkstemp(
        dir=filepath.parent,
        prefix=f".{filepath.name}.",
        suffix='.tmp'
    )
    
    try:
        with os.fdopen(fd, 'w', encoding=encoding) as f:
            yield f
        
        # Atomic rename (ersetzt alte Datei)
        temp_path_obj = Path(temp_path)
        temp_path_obj.replace(filepath)
        logger.debug(f"Atomic write erfolgreich: {filepath}")
        
    except Exception as e:
        # Cleanup bei Fehler
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        logger.error(f"Atomic write fehlgeschlagen für {filepath}: {e}")
        raise


def safe_read_file(filepath: Union[str, Path], fallback: str = "", encoding: str = 'utf-8') -> str:
    """Lese Datei sicher mit Fallback"""
    try:
        return Path(filepath).read_text(encoding=encoding)
    except Exception as e:
        logger.error(f"Datei-Lesefehler {filepath}: {e}")
        return fallback


def safe_write_file(filepath: Union[str, Path], content: str, atomic: bool = True, encoding: str = 'utf-8') -> bool:
    """
    Schreibe Datei sicher
    
    Args:
        filepath: Dateipfad
        content: Zu schreibender Inhalt
        atomic: Verwende atomic write
        encoding: Text-Encoding
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        if atomic:
            with atomic_write(filepath, encoding=encoding) as f:
                f.write(content)
        else:
            Path(filepath).write_text(content, encoding=encoding)
        return True
    except Exception as e:
        logger.error(f"Datei-Schreibfehler {filepath}: {e}")
        return False


def ensure_directory(path: Union[str, Path]) -> bool:
    """Stelle sicher dass Verzeichnis existiert"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Verzeichnis-Erstellung fehlgeschlagen {path}: {e}")
        return False


# ============================================================================
# DATABASE ROBUSTNESS
# ============================================================================

@retry_on_error(max_attempts=3, delay=0.5, exceptions=(sqlite3.OperationalError,))
def safe_db_execute(conn: sqlite3.Connection, query: str, params: tuple = ()) -> Optional[sqlite3.Cursor]:
    """
    Führe DB-Query sicher aus mit Retry-Logic
    
    Args:
        conn: DB-Connection
        query: SQL-Query
        params: Query-Parameter
    
    Returns:
        Cursor oder None bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor
    except Exception as e:
        logger.error(f"DB-Query fehlgeschlagen: {e}\nQuery: {query[:100]}")
        raise


@contextmanager
def safe_db_transaction(conn: sqlite3.Connection):
    """
    Context Manager für sichere DB-Transaktionen mit Rollback
    
    Usage:
        with safe_db_transaction(conn):
            conn.execute("INSERT ...")
            conn.execute("UPDATE ...")
    """
    try:
        yield conn
        conn.commit()
        logger.debug("DB-Transaktion erfolgreich committed")
    except Exception as e:
        conn.rollback()
        logger.error(f"DB-Transaktion rollback: {e}")
        raise


# ============================================================================
# INPUT VALIDATION & SANITIZATION
# ============================================================================

def sanitize_string(text: str, max_length: int = 1000, allow_html: bool = False) -> str:
    """
    Sanitize String-Input
    
    Args:
        text: Input-Text
        max_length: Maximale Länge
        allow_html: HTML-Tags erlauben
    
    Returns:
        Sanitized String
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Länge begrenzen
    text = text[:max_length]
    
    # HTML-Tags entfernen falls nicht erlaubt
    if not allow_html:
        import html
        text = html.escape(text)
    
    return text.strip()


def validate_path(path: Union[str, Path], must_exist: bool = False, allowed_extensions: Optional[list] = None) -> bool:
    """
    Validiere Dateipfad
    
    Args:
        path: Zu prüfender Pfad
        must_exist: Datei muss existieren
        allowed_extensions: Liste erlaubter Dateiendungen (z.B. ['.pdf', '.json'])
    
    Returns:
        True wenn valide, False sonst
    """
    try:
        path = Path(path).resolve()
        
        # Path Traversal Prevention
        if '..' in str(path):
            logger.warning(f"Path Traversal Versuch erkannt: {path}")
            return False
        
        # Existenz-Check
        if must_exist and not path.exists():
            return False
        
        # Extension-Check
        if allowed_extensions and path.suffix.lower() not in allowed_extensions:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Path-Validierung fehlgeschlagen: {e}")
        return False


def validate_type(value: Any, expected_type: type, fallback: Any = None) -> Any:
    """
    Validiere Typ mit Fallback
    
    Args:
        value: Zu prüfender Wert
        expected_type: Erwarteter Typ
        fallback: Rückgabewert bei falschem Typ
    
    Returns:
        value wenn Typ korrekt, sonst fallback
    """
    if isinstance(value, expected_type):
        return value
    
    logger.warning(f"Typ-Validierung fehlgeschlagen: Erwartet {expected_type.__name__}, erhalten {type(value).__name__}")
    return fallback


# ============================================================================
# MEMORY MANAGEMENT
# ============================================================================

def clear_session_state_cache(prefix: str = "img_cache_") -> int:
    """
    Lösche gecachte Werte aus Session State
    
    Args:
        prefix: Präfix der zu löschenden Keys
    
    Returns:
        Anzahl gelöschter Einträge
    """
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith(prefix)]
    for key in keys_to_delete:
        del st.session_state[key]
    
    if keys_to_delete:
        logger.info(f"Session State Cache gelöscht: {len(keys_to_delete)} Einträge")
    
    return len(keys_to_delete)


def limit_session_state_size(max_items: int = 100, pattern: str = "*") -> None:
    """
    Begrenze Session State Größe (LRU-ähnlich)
    
    Args:
        max_items: Maximale Anzahl Items
        pattern: Wildcard-Pattern für zu betrachtende Keys
    """
    import fnmatch
    
    matching_keys = [k for k in st.session_state.keys() if fnmatch.fnmatch(k, pattern)]
    
    if len(matching_keys) > max_items:
        # Lösche älteste Einträge (naive Implementation)
        to_delete = matching_keys[:-max_items]
        for key in to_delete:
            del st.session_state[key]
        
        logger.info(f"Session State limitiert: {len(to_delete)} alte Einträge gelöscht")


# ============================================================================
# LOGGING & MONITORING
# ============================================================================

def log_function_call(func: Callable) -> Callable:
    """Decorator für Function-Call Logging"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"CALL: {func.__name__}({args}, {kwargs})")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"RETURN: {func.__name__} -> {type(result).__name__}")
            return result
        except Exception as e:
            logger.error(f"ERROR: {func.__name__} -> {e}")
            raise
    
    return wrapper


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Error Handling
    'retry_on_error',
    'safe_execute',
    # Session State
    'init_session_state',
    'get_session_state',
    'set_session_state_safe',
    'SessionStateGuard',
    # File I/O
    'atomic_write',
    'safe_read_file',
    'safe_write_file',
    'ensure_directory',
    # Database
    'safe_db_execute',
    'safe_db_transaction',
    # Validation
    'sanitize_string',
    'validate_path',
    'validate_type',
    # Memory
    'clear_session_state_cache',
    'limit_session_state_size',
    # Logging
    'log_function_call',
]
