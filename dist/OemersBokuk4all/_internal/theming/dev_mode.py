"""
Development Mode Configuration

Konfiguration für Theme-Entwicklungs-Features wie Hot Reload.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class DevModeConfig:
    """Konfiguration für Development Mode"""
    
    # Hot Reload
    hot_reload_enabled: bool = False
    hot_reload_debounce: float = 1.0
    
    # Validation
    show_validation_errors: bool = True
    validate_on_reload: bool = True
    
    # Logging
    verbose_logging: bool = True
    log_theme_switches: bool = True
    log_css_generation: bool = True
    
    # Performance
    disable_css_cache: bool = False
    show_performance_metrics: bool = True
    
    # UI
    show_dev_tools: bool = True
    show_theme_inspector: bool = True


def get_dev_mode_config() -> DevModeConfig:
    """
    Lädt Development Mode Konfiguration aus Umgebungsvariablen
    
    Environment Variables:
        SHADCN_DEV_MODE: Aktiviert Development Mode (1, true, yes)
        SHADCN_HOT_RELOAD: Aktiviert Hot Reload (1, true, yes)
        SHADCN_HOT_RELOAD_DEBOUNCE: Debounce-Zeit in Sekunden (Standard: 1.0)
        SHADCN_VERBOSE: Aktiviert verbose logging (1, true, yes)
        SHADCN_DISABLE_CACHE: Deaktiviert CSS-Cache (1, true, yes)
    
    Returns:
        DevModeConfig-Instanz
    """
    def parse_bool(value: Optional[str], default: bool = False) -> bool:
        """Parse boolean aus String"""
        if value is None:
            return default
        return value.lower() in ('1', 'true', 'yes', 'on')
    
    def parse_float(value: Optional[str], default: float) -> float:
        """Parse float aus String"""
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default
    
    # Prüfe ob Dev Mode aktiviert ist
    dev_mode = parse_bool(os.getenv('SHADCN_DEV_MODE'))
    
    # Wenn Dev Mode aktiviert, setze sinnvolle Defaults
    if dev_mode:
        config = DevModeConfig(
            hot_reload_enabled=parse_bool(
                os.getenv('SHADCN_HOT_RELOAD'),
                default=True  # In Dev Mode standardmäßig an
            ),
            hot_reload_debounce=parse_float(
                os.getenv('SHADCN_HOT_RELOAD_DEBOUNCE'),
                default=1.0
            ),
            show_validation_errors=True,
            validate_on_reload=True,
            verbose_logging=parse_bool(
                os.getenv('SHADCN_VERBOSE'),
                default=True
            ),
            log_theme_switches=True,
            log_css_generation=True,
            disable_css_cache=parse_bool(
                os.getenv('SHADCN_DISABLE_CACHE'),
                default=False
            ),
            show_performance_metrics=True,
            show_dev_tools=True,
            show_theme_inspector=True
        )
    else:
        # Production Mode: Alles aus
        config = DevModeConfig(
            hot_reload_enabled=False,
            hot_reload_debounce=1.0,
            show_validation_errors=False,
            validate_on_reload=False,
            verbose_logging=False,
            log_theme_switches=False,
            log_css_generation=False,
            disable_css_cache=False,
            show_performance_metrics=False,
            show_dev_tools=False,
            show_theme_inspector=False
        )
    
    return config


def is_dev_mode() -> bool:
    """
    Prüft ob Development Mode aktiviert ist
    
    Returns:
        True wenn Dev Mode aktiv
    """
    return os.getenv('SHADCN_DEV_MODE', '').lower() in ('1', 'true', 'yes', 'on')


def enable_dev_mode() -> None:
    """Aktiviert Development Mode (setzt Umgebungsvariable)"""
    os.environ['SHADCN_DEV_MODE'] = '1'


def disable_dev_mode() -> None:
    """Deaktiviert Development Mode"""
    os.environ.pop('SHADCN_DEV_MODE', None)
