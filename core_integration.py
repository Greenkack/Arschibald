"""
Core Integration Module
=======================

Sichere Integration der core/ Module in die Hauptapp.
Alle Features sind optional und haben Fallbacks.
"""

import os
import sys
from pathlib import Path

# Feature Flags
FEATURES = {
    'config': os.getenv('FEATURE_CONFIG', 'true').lower() == 'true',
    'logging': os.getenv('FEATURE_LOGGING', 'true').lower() == 'true',
    'cache': os.getenv('FEATURE_CACHE', 'false').lower() == 'true',
    'session': os.getenv('FEATURE_SESSION_PERSISTENCE', 'false').lower() == 'true',
    'database': os.getenv('FEATURE_DATABASE_POOLING', 'false').lower() == 'true',
}

# Global instances
_config = None
_logger = None
_cache = None


def init_core_integration(enable_logging=True):
    """
    Initialisiere core-Module basierend auf Feature Flags.
    
    Diese Funktion ist SAFE - wenn ein Modul fehlschlägt,
    wird es einfach deaktiviert ohne die App zu crashen.
    
    Args:
        enable_logging: Ob Logging aktiviert werden soll
    
    Returns:
        dict: Status der initialisierten Module
    """
    global _config, _logger, _cache
    
    status = {
        'config': False,
        'logging': False,
        'cache': False,
        'errors': []
    }
    
    # 1. CONFIG - Immer versuchen zu laden (Fundament)
    if FEATURES['config']:
        try:
            from core.config import get_config
            _config = get_config(reload_if_needed=False)
            status['config'] = True
            print("✅ Core Config initialized")
        except Exception as e:
            status['errors'].append(f"Config init failed: {e}")
            print(f"⚠️ Core Config disabled: {e}")
    
    # 2. LOGGING - Nur wenn Config erfolgreich
    if FEATURES['logging'] and enable_logging:
        try:
            from core.logging_config import init_logging_from_config
            
            if _config:
                init_logging_from_config(_config)
            else:
                # Fallback ohne config
                from core.logging_system import setup_structured_logging
                setup_structured_logging(
                    env='dev',
                    log_level='INFO',
                    log_dir=Path('./logs')
                )
            
            from core.logging_system import get_logger
            _logger = get_logger('bokuk2')
            _logger.info("core_integration_initialized", features=FEATURES)
            status['logging'] = True
            print("✅ Core Logging initialized")
        except Exception as e:
            status['errors'].append(f"Logging init failed: {e}")
            print(f"⚠️ Core Logging disabled: {e}")
    
    # 3. CACHE - Optional, nur wenn explizit aktiviert
    if FEATURES['cache']:
        try:
            from core.cache import get_cache
            _cache = get_cache()
            status['cache'] = True
            print("✅ Core Cache initialized")
            if _logger:
                _logger.info("cache_initialized")
        except Exception as e:
            status['errors'].append(f"Cache init failed: {e}")
            print(f"⚠️ Core Cache disabled: {e}")
    
    return status


def get_app_config():
    """
    Hole App-Konfiguration.
    
    Returns:
        AppConfig oder None wenn nicht verfügbar
    """
    return _config


def get_app_logger(name=None):
    """
    Hole Logger-Instanz.
    
    Args:
        name: Logger-Name (optional)
    
    Returns:
        Logger oder None wenn nicht verfügbar
    """
    if _logger and name:
        from core.logging_system import get_logger
        return get_logger(name)
    return _logger


def get_app_cache():
    """
    Hole Cache-Instanz.
    
    Returns:
        Cache oder None wenn nicht verfügbar
    """
    return _cache


def log_info(message, **kwargs):
    """
    Sicheres Logging - fällt zurück auf print wenn Logger nicht verfügbar.
    
    Args:
        message: Log-Nachricht
        **kwargs: Zusätzliche Context-Felder
    """
    if _logger:
        _logger.info(message, **kwargs)
    else:
        print(f"INFO: {message}", kwargs if kwargs else "")


def log_error(message, error=None, **kwargs):
    """
    Sicheres Error-Logging.
    
    Args:
        message: Fehler-Nachricht
        error: Exception (optional)
        **kwargs: Zusätzliche Context-Felder
    """
    if _logger:
        if error:
            _logger.error(message, error=str(error), **kwargs)
        else:
            _logger.error(message, **kwargs)
    else:
        print(f"ERROR: {message}", f"Error: {error}" if error else "", kwargs if kwargs else "")


def log_warning(message, **kwargs):
    """
    Sicheres Warning-Logging.
    
    Args:
        message: Warning-Nachricht
        **kwargs: Zusätzliche Context-Felder
    """
    if _logger:
        _logger.warning(message, **kwargs)
    else:
        print(f"WARNING: {message}", kwargs if kwargs else "")


def cache_get(key):
    """
    Sicherer Cache-Zugriff.
    
    Args:
        key: Cache-Key
    
    Returns:
        Cached value oder None
    """
    if _cache:
        try:
            return _cache.get(key)
        except Exception as e:
            log_error("cache_get_failed", error=e, key=key)
    return None


def cache_set(key, value, ttl=None, tags=None):
    """
    Sicheres Cache-Schreiben.
    
    Args:
        key: Cache-Key
        value: Wert zum Cachen
        ttl: Time-to-live in Sekunden
        tags: Tags für Invalidation
    
    Returns:
        bool: True wenn erfolgreich
    """
    if _cache:
        try:
            _cache.set(key, value, ttl=ttl, tags=tags or set())
            return True
        except Exception as e:
            log_error("cache_set_failed", error=e, key=key)
    return False


def is_feature_enabled(feature_name):
    """
    Prüfe ob Feature aktiviert ist.
    
    Args:
        feature_name: Name des Features
    
    Returns:
        bool: True wenn aktiviert
    """
    return FEATURES.get(feature_name, False)


# Convenience exports
__all__ = [
    'init_core_integration',
    'get_app_config',
    'get_app_logger',
    'get_app_cache',
    'log_info',
    'log_error',
    'log_warning',
    'cache_get',
    'cache_set',
    'is_feature_enabled',
    'FEATURES',
]
