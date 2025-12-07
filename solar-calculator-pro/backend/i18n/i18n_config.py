"""
Backend i18n Configuration
"""

SUPPORTED_LANGUAGES = {
    "de": {
        "name": "German",
        "nativeName": "Deutsch",
        "flag": "",
        "rtl": False,
        "locale": "de-DE",
    },
    "en": {
        "name": "English",
        "nativeName": "English",
        "flag": "",
        "rtl": False,
        "locale": "en-US",
    },
    "fr": {
        "name": "French",
        "nativeName": "Français",
        "flag": "",
        "rtl": False,
        "locale": "fr-FR",
    },
    "es": {
        "name": "Spanish",
        "nativeName": "Español",
        "flag": "",
        "rtl": False,
        "locale": "es-ES",
    },
    "it": {
        "name": "Italian",
        "nativeName": "Italiano",
        "flag": "",
        "rtl": False,
        "locale": "it-IT",
    },
    "pl": {
        "name": "Polish",
        "nativeName": "Polski",
        "flag": "",
        "rtl": False,
        "locale": "pl-PL",
    },
    "nl": {
        "name": "Dutch",
        "nativeName": "Nederlands",
        "flag": "",
        "rtl": False,
        "locale": "nl-NL",
    },
    "ar": {
        "name": "Arabic",
        "nativeName": "العربية",
        "flag": "",
        "rtl": True,
        "locale": "ar-SA",
    },
    "he": {
        "name": "Hebrew",
        "nativeName": "עברית",
        "flag": "",
        "rtl": True,
        "locale": "he-IL",
    },
}

DEFAULT_LANGUAGE = "de"

NAMESPACES = [
    "common",
    "navigation",
    "solar",
    "heatpump",
    "pricing",
    "pdf",
    "crm",
    "products",
    "admin",
    "errors",
    "validation",
    "units",
    "dates",
    "messages",
]
