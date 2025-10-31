"""
Performance Settings Handler
Verwaltet Performance und Caching-Einstellungen
"""

import streamlit as st
from typing import Any
from functools import lru_cache


# Globaler Cache für Settings
_settings_cache = {}


def load_performance_settings() -> dict:
    """
    Lädt alle Performance-Einstellungen aus der Database
    
    Returns:
        Dictionary mit Performance-Settings
    """
    try:
        from database import load_admin_setting
        
        settings = {
            'auto_cache_enabled': _convert_to_bool(
                load_admin_setting('performance_auto_cache_enabled', True)
            ),
            'cache_size_mb': int(
                load_admin_setting('performance_cache_size_mb', 100)
            ),
            'background_processing': _convert_to_bool(
                load_admin_setting('performance_background_processing', True)
            ),
            'preload_data': _convert_to_bool(
                load_admin_setting('performance_preload_data', False)
            ),
            'calc_precision_level': load_admin_setting('calc_precision_level', 'standard'),
            'monte_carlo_enabled': _convert_to_bool(
                load_admin_setting('calc_monte_carlo_enabled', False)
            ),
            'weather_integration': _convert_to_bool(
                load_admin_setting('calc_weather_integration', True)
            ),
            'degradation_analysis': _convert_to_bool(
                load_admin_setting('calc_degradation_analysis', True)
            ),
        }
        
        # In Session State cachen
        st.session_state['performance_settings'] = settings
        
        return settings
        
    except Exception as e:
        st.warning(f"Performance-Einstellungen konnten nicht geladen werden: {e}")
        return {
            'auto_cache_enabled': True,
            'cache_size_mb': 100,
            'background_processing': True,
            'preload_data': False,
            'calc_precision_level': 'standard',
            'monte_carlo_enabled': False,
            'weather_integration': True,
            'degradation_analysis': True,
        }


def _convert_to_bool(value: Any) -> bool:
    """Konvertiert verschiedene Typen zu Boolean"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return bool(value)


def get_cache_size_bytes() -> int:
    """
    Gibt die konfigurierte Cache-Größe in Bytes zurück
    
    Returns:
        Cache-Größe in Bytes
    """
    settings = st.session_state.get('performance_settings')
    if not settings:
        settings = load_performance_settings()
    
    cache_size_mb = settings.get('cache_size_mb', 100)
    return cache_size_mb * 1024 * 1024  # MB to Bytes


def is_caching_enabled() -> bool:
    """
    Prüft ob Caching aktiviert ist
    
    Returns:
        True wenn Caching aktiviert
    """
    settings = st.session_state.get('performance_settings')
    if not settings:
        settings = load_performance_settings()
    
    return settings.get('auto_cache_enabled', True)


def get_calculation_precision() -> str:
    """
    Gibt das konfigurierte Präzisionslevel zurück
    
    Returns:
        'basic', 'standard', 'high', oder 'ultra'
    """
    settings = st.session_state.get('performance_settings')
    if not settings:
        settings = load_performance_settings()
    
    return settings.get('calc_precision_level', 'standard')


def get_precision_config() -> dict:
    """
    Gibt Präzisions-Konfiguration basierend auf gewähltem Level zurück
    
    Returns:
        Dictionary mit Präzisions-Parametern
    """
    precision_level = get_calculation_precision()
    
    configs = {
        'basic': {
            'decimal_places': 1,
            'simulation_steps': 12,  # Monatlich
            'monte_carlo_runs': 0,
            'weather_data_detail': 'minimal'
        },
        'standard': {
            'decimal_places': 2,
            'simulation_steps': 12,  # Monatlich
            'monte_carlo_runs': 100,
            'weather_data_detail': 'standard'
        },
        'high': {
            'decimal_places': 3,
            'simulation_steps': 365,  # Täglich
            'monte_carlo_runs': 1000,
            'weather_data_detail': 'detailed'
        },
        'ultra': {
            'decimal_places': 4,
            'simulation_steps': 8760,  # Stündlich
            'monte_carlo_runs': 10000,
            'weather_data_detail': 'ultra_detailed'
        }
    }
    
    return configs.get(precision_level, configs['standard'])


def is_monte_carlo_enabled() -> bool:
    """Prüft ob Monte Carlo Simulation aktiviert ist"""
    settings = st.session_state.get('performance_settings')
    if not settings:
        settings = load_performance_settings()
    
    # Nur wenn explizit aktiviert UND Precision nicht basic
    monte_enabled = settings.get('monte_carlo_enabled', False)
    precision = get_calculation_precision()
    
    return monte_carlo_enabled and precision != 'basic'


def is_weather_integration_enabled() -> bool:
    """Prüft ob erweiterte Wetterdaten-Integration aktiviert ist"""
    settings = st.session_state.get('performance_settings')
    if not settings:
        settings = load_performance_settings()
    
    return settings.get('weather_integration', True)


def is_degradation_analysis_enabled() -> bool:
    """Prüft ob Degradations-Analyse aktiviert ist"""
    settings = st.session_state.get('performance_settings')
    if not settings:
        settings = load_performance_settings()
    
    return settings.get('degradation_analysis', True)


def should_preload_data() -> bool:
    """Prüft ob Daten vorgeladen werden sollen"""
    settings = st.session_state.get('performance_settings')
    if not settings:
        settings = load_performance_settings()
    
    return settings.get('preload_data', False)


def clear_cache():
    """Löscht den Performance-Cache"""
    _settings_cache.clear()
    lru_cache.cache_clear()
    
    if 'performance_settings' in st.session_state:
        del st.session_state['performance_settings']
    
    st.success("✅ Cache erfolgreich geleert!")


def get_cache_stats() -> dict:
    """
    Gibt Cache-Statistiken zurück
    
    Returns:
        Dictionary mit Cache-Stats
    """
    return {
        'cache_size_mb': get_cache_size_bytes() / (1024 * 1024),
        'caching_enabled': is_caching_enabled(),
        'items_cached': len(_settings_cache),
        'precision_level': get_calculation_precision(),
        'monte_carlo_enabled': is_monte_carlo_enabled(),
    }


# Initial load beim Import
if __name__ != "__main__":
    try:
        load_performance_settings()
    except Exception:
        pass  # Fehler beim Init ignorieren
