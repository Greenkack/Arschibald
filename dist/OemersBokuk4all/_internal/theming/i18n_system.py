"""
Task 31: Internationalisierung (i18n) System
============================================
i18n-System für Theme-Namen und Komponenten-Labels.
"""

from typing import Dict, Optional
from dataclasses import dataclass
import json


@dataclass
class Translation:
    """Translation entry."""
    key: str
    de: str
    en: str


class I18nManager:
    """Internationalization manager for themes and components."""
    
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        # Theme names
        "theme.default": {"de": "Standard", "en": "Default"},
        "theme.dark": {"de": "Dunkel", "en": "Dark"},
        "theme.ocean": {"de": "Ozean", "en": "Ocean"},
        "theme.forest": {"de": "Wald", "en": "Forest"},
        "theme.sunset": {"de": "Sonnenuntergang", "en": "Sunset"},
        "theme.solar": {"de": "Solar", "en": "Solar"},
        "theme.finance": {"de": "Finanzen", "en": "Finance"},
        "theme.healthcare": {"de": "Gesundheit", "en": "Healthcare"},
        
        # Component labels
        "component.card": {"de": "Karte", "en": "Card"},
        "component.button": {"de": "Schaltfläche", "en": "Button"},
        "component.input": {"de": "Eingabefeld", "en": "Input"},
        "component.alert": {"de": "Hinweis", "en": "Alert"},
        "component.badge": {"de": "Abzeichen", "en": "Badge"},
        "component.table": {"de": "Tabelle", "en": "Table"},
        
        # UI labels
        "ui.theme_selector": {"de": "Theme auswählen", "en": "Select Theme"},
        "ui.dark_mode": {"de": "Dunkelmodus", "en": "Dark Mode"},
        "ui.light_mode": {"de": "Hellmodus", "en": "Light Mode"},
        "ui.save": {"de": "Speichern", "en": "Save"},
        "ui.cancel": {"de": "Abbrechen", "en": "Cancel"},
        "ui.apply": {"de": "Anwenden", "en": "Apply"},
        "ui.reset": {"de": "Zurücksetzen", "en": "Reset"},
        
        # Messages
        "msg.theme_changed": {"de": "Theme wurde geändert", "en": "Theme changed"},
        "msg.settings_saved": {"de": "Einstellungen gespeichert", "en": "Settings saved"},
        "msg.error": {"de": "Fehler aufgetreten", "en": "Error occurred"},
    }
    
    def __init__(self, default_locale: str = "de"):
        self.current_locale = default_locale
        self.supported_locales = ["de", "en"]
    
    def t(self, key: str, locale: Optional[str] = None) -> str:
        """Translate a key to the specified or current locale."""
        loc = locale or self.current_locale
        if key in self.TRANSLATIONS:
            return self.TRANSLATIONS[key].get(loc, key)
        return key
    
    def set_locale(self, locale: str) -> bool:
        """Set the current locale."""
        if locale in self.supported_locales:
            self.current_locale = locale
            return True
        return False
    
    def get_locale(self) -> str:
        """Get the current locale."""
        return self.current_locale
    
    def format_number(self, value: float, locale: Optional[str] = None) -> str:
        """Format number according to locale."""
        loc = locale or self.current_locale
        if loc == "de":
            return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{value:,.2f}"
    
    def format_date(self, date_str: str, locale: Optional[str] = None) -> str:
        """Format date according to locale."""
        loc = locale or self.current_locale
        # Simple format conversion
        if loc == "de":
            # Convert YYYY-MM-DD to DD.MM.YYYY
            parts = date_str.split("-")
            if len(parts) == 3:
                return f"{parts[2]}.{parts[1]}.{parts[0]}"
        return date_str
    
    def get_rtl_direction(self) -> str:
        """Get text direction for RTL support."""
        rtl_locales = ["ar", "he", "fa"]
        if self.current_locale in rtl_locales:
            return "rtl"
        return "ltr"


# Global instance
i18n = I18nManager()


def t(key: str, locale: Optional[str] = None) -> str:
    """Shortcut for translation."""
    return i18n.t(key, locale)


def format_number_de(value: float) -> str:
    """Format number in German format."""
    return i18n.format_number(value, "de")


def format_date_de(date_str: str) -> str:
    """Format date in German format."""
    return i18n.format_date(date_str, "de")
