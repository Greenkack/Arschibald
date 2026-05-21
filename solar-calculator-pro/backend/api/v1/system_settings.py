"""
System Settings and Options API

Provides REST API for system settings:
- PVGIS toggle (on/off)
- Default yield profile selection
- Localization text management
- Debug options (PDF overlay, logging)
- Simulation settings (battery cycles, degradation)
- UI effect settings

Requirements: funktionen.txt - "Weitere Einstellungen"
Task: 279. System Settings and Options
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/admin/settings", tags=["System Settings"])


# ==================== Enums ====================

class YieldProfile(str, Enum):
    PVGIS = "pvgis"
    STANDARD_GERMANY = "standard_germany"
    OPTIMISTIC = "optimistic"
    CONSERVATIVE = "conservative"
    CUSTOM = "custom"


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class UITheme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


# ==================== Pydantic Models ====================

class PVGISSettings(BaseModel):
    """PVGIS integration settings"""
    enabled: bool = True
    api_url: str = "https://re.jrc.ec.europa.eu/api/v5_2/"
    default_database: str = "PVGIS-SARAH2"
    cache_results: bool = True
    cache_duration_days: int = 30
    fallback_to_standard: bool = True


class YieldSettings(BaseModel):
    """Yield calculation settings"""
    default_profile: YieldProfile = YieldProfile.PVGIS
    specific_yield_kwh_kwp: float = Field(default=950, ge=700, le=1200)
    degradation_percent_year: float = Field(default=0.5, ge=0, le=2)
    system_losses_percent: float = Field(default=14, ge=5, le=25)
    inverter_efficiency_percent: float = Field(default=97, ge=90, le=99)


class BatterySettings(BaseModel):
    """Battery simulation settings"""
    default_cycles_per_year: int = Field(default=250, ge=100, le=500)
    max_dod_percent: float = Field(default=90, ge=50, le=100)
    round_trip_efficiency_percent: float = Field(default=95, ge=85, le=99)
    degradation_percent_year: float = Field(default=2, ge=0, le=5)
    warranty_years: int = Field(default=10, ge=5, le=20)


class DebugSettings(BaseModel):
    """Debug and development settings"""
    pdf_overlay_grid: bool = False
    pdf_show_coordinates: bool = False
    log_level: LogLevel = LogLevel.INFO
    log_api_requests: bool = False
    log_calculations: bool = False
    show_performance_metrics: bool = False
    enable_test_mode: bool = False


class UISettings(BaseModel):
    """UI and display settings"""
    theme: UITheme = UITheme.LIGHT
    primary_color: str = "#3B82F6"
    secondary_color: str = "#10B981"
    enable_animations: bool = True
    animation_speed: str = "normal"
    show_tooltips: bool = True
    compact_mode: bool = False
    sidebar_collapsed: bool = False
    date_format: str = "DD.MM.YYYY"
    number_format: str = "de-DE"
    currency: str = "EUR"


class LocalizationSettings(BaseModel):
    """Localization settings"""
    default_language: str = "de"
    available_languages: List[str] = ["de", "en"]
    date_format: str = "DD.MM.YYYY"
    time_format: str = "HH:mm"
    decimal_separator: str = ","
    thousands_separator: str = "."
    currency_symbol: str = "€"
    currency_position: str = "after"


class EmailSettings(BaseModel):
    """Email settings"""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    use_tls: bool = True
    from_email: str = ""
    from_name: str = "Solar Calculator Pro"
    reply_to: str = ""


class CalculationDefaults(BaseModel):
    """Default calculation parameters"""
    electricity_price_eur_kwh: float = 0.30
    electricity_price_increase_percent: float = 3.0
    feed_in_tariff_eur_kwh: float = 0.082
    self_consumption_percent: float = 30
    co2_factor_kg_kwh: float = 0.4
    calculation_period_years: int = 20
    discount_rate_percent: float = 2.0


class SystemSettings(BaseModel):
    """Complete system settings"""
    pvgis: PVGISSettings = PVGISSettings()
    yield_settings: YieldSettings = YieldSettings()
    battery: BatterySettings = BatterySettings()
    debug: DebugSettings = DebugSettings()
    ui: UISettings = UISettings()
    localization: LocalizationSettings = LocalizationSettings()
    email: EmailSettings = EmailSettings()
    calculation_defaults: CalculationDefaults = CalculationDefaults()
    last_updated: datetime = datetime.now()
    updated_by: str = "system"


class LocalizationText(BaseModel):
    """Localization text entry"""
    key: str
    de: str
    en: Optional[str] = None


# ==================== Settings Store ====================

_settings = SystemSettings()
_localization_texts: Dict[str, LocalizationText] = {}


def init_localization_texts():
    """Initialize default localization texts"""
    texts = [
        LocalizationText(key="app.title", de="Solar Calculator Pro", en="Solar Calculator Pro"),
        LocalizationText(key="nav.dashboard", de="Dashboard", en="Dashboard"),
        LocalizationText(key="nav.projects", de="Projekte", en="Projects"),
        LocalizationText(key="nav.calculator", de="Kalkulator", en="Calculator"),
        LocalizationText(key="nav.crm", de="Kundenverwaltung", en="Customer Management"),
        LocalizationText(key="nav.admin", de="Administration", en="Administration"),
        LocalizationText(key="calc.modules", de="Anzahl Module", en="Number of Modules"),
        LocalizationText(key="calc.power", de="Anlagenleistung", en="System Power"),
        LocalizationText(key="calc.yield", de="Jahresertrag", en="Annual Yield"),
        LocalizationText(key="calc.savings", de="Jährliche Einsparung", en="Annual Savings"),
        LocalizationText(key="calc.payback", de="Amortisationszeit", en="Payback Period"),
        LocalizationText(key="calc.autarky", de="Autarkiegrad", en="Self-Sufficiency"),
        LocalizationText(key="btn.save", de="Speichern", en="Save"),
        LocalizationText(key="btn.cancel", de="Abbrechen", en="Cancel"),
        LocalizationText(key="btn.generate_pdf", de="PDF erstellen", en="Generate PDF"),
    ]
    for text in texts:
        _localization_texts[text.key] = text


init_localization_texts()


# ==================== API Endpoints ====================

@router.get("/")
async def get_all_settings():
    """Get all system settings."""
    return {"settings": _settings}


@router.put("/")
async def update_all_settings(settings: SystemSettings):
    """Update all system settings."""
    global _settings
    settings.last_updated = datetime.now()
    _settings = settings
    return {"settings": _settings, "updated": True}


@router.get("/pvgis")
async def get_pvgis_settings():
    """Get PVGIS settings."""
    return {"settings": _settings.pvgis}


@router.put("/pvgis")
async def update_pvgis_settings(settings: PVGISSettings):
    """Update PVGIS settings."""
    _settings.pvgis = settings
    _settings.last_updated = datetime.now()
    return {"settings": _settings.pvgis, "updated": True}


@router.get("/yield")
async def get_yield_settings():
    """Get yield calculation settings."""
    return {"settings": _settings.yield_settings}


@router.put("/yield")
async def update_yield_settings(settings: YieldSettings):
    """Update yield calculation settings."""
    _settings.yield_settings = settings
    _settings.last_updated = datetime.now()
    return {"settings": _settings.yield_settings, "updated": True}


@router.get("/battery")
async def get_battery_settings():
    """Get battery simulation settings."""
    return {"settings": _settings.battery}


@router.put("/battery")
async def update_battery_settings(settings: BatterySettings):
    """Update battery simulation settings."""
    _settings.battery = settings
    _settings.last_updated = datetime.now()
    return {"settings": _settings.battery, "updated": True}


@router.get("/debug")
async def get_debug_settings():
    """Get debug settings."""
    return {"settings": _settings.debug}


@router.put("/debug")
async def update_debug_settings(settings: DebugSettings):
    """Update debug settings."""
    _settings.debug = settings
    _settings.last_updated = datetime.now()
    return {"settings": _settings.debug, "updated": True}


@router.get("/ui")
async def get_ui_settings():
    """Get UI settings."""
    return {"settings": _settings.ui}


@router.put("/ui")
async def update_ui_settings(settings: UISettings):
    """Update UI settings."""
    _settings.ui = settings
    _settings.last_updated = datetime.now()
    return {"settings": _settings.ui, "updated": True}


@router.get("/localization")
async def get_localization_settings():
    """Get localization settings."""
    return {"settings": _settings.localization}


@router.put("/localization")
async def update_localization_settings(settings: LocalizationSettings):
    """Update localization settings."""
    _settings.localization = settings
    _settings.last_updated = datetime.now()
    return {"settings": _settings.localization, "updated": True}


@router.get("/calculation-defaults")
async def get_calculation_defaults():
    """Get calculation default values."""
    return {"defaults": _settings.calculation_defaults}


@router.put("/calculation-defaults")
async def update_calculation_defaults(defaults: CalculationDefaults):
    """Update calculation default values."""
    _settings.calculation_defaults = defaults
    _settings.last_updated = datetime.now()
    return {"defaults": _settings.calculation_defaults, "updated": True}


@router.get("/texts")
async def get_localization_texts(language: str = "de"):
    """Get localization texts."""
    texts = {}
    for key, text in _localization_texts.items():
        texts[key] = getattr(text, language, text.de)
    return {"texts": texts, "language": language}


@router.put("/texts/{key}")
async def update_localization_text(key: str, text: LocalizationText):
    """Update localization text."""
    _localization_texts[key] = text
    return {"text": text, "updated": True}


@router.get("/yield-profiles")
async def get_yield_profiles():
    """Get available yield profiles."""
    return {
        "profiles": [
            {"id": "pvgis", "name": "PVGIS (Online)", "description": "Echte Wetterdaten von PVGIS"},
            {"id": "standard_germany", "name": "Standard Deutschland", "description": "950 kWh/kWp"},
            {"id": "optimistic", "name": "Optimistisch", "description": "1050 kWh/kWp"},
            {"id": "conservative", "name": "Konservativ", "description": "850 kWh/kWp"},
            {"id": "custom", "name": "Benutzerdefiniert", "description": "Eigene Werte"}
        ]
    }


@router.get("/themes")
async def get_available_themes():
    """Get available UI themes."""
    return {
        "themes": [
            {"id": "light", "name": "Hell", "preview_colors": {"bg": "#ffffff", "text": "#1f2937"}},
            {"id": "dark", "name": "Dunkel", "preview_colors": {"bg": "#1f2937", "text": "#f9fafb"}},
            {"id": "auto", "name": "Automatisch", "description": "Folgt Systemeinstellung"}
        ]
    }


@router.post("/reset")
async def reset_to_defaults(section: Optional[str] = None):
    """Reset settings to defaults."""
    global _settings
    
    if section == "pvgis":
        _settings.pvgis = PVGISSettings()
    elif section == "yield":
        _settings.yield_settings = YieldSettings()
    elif section == "battery":
        _settings.battery = BatterySettings()
    elif section == "debug":
        _settings.debug = DebugSettings()
    elif section == "ui":
        _settings.ui = UISettings()
    elif section is None:
        _settings = SystemSettings()
    else:
        raise HTTPException(status_code=400, detail="Unbekannte Sektion")
    
    _settings.last_updated = datetime.now()
    
    return {"reset": True, "section": section or "all", "settings": _settings}


@router.get("/export")
async def export_settings():
    """Export all settings as JSON."""
    return {
        "settings": _settings.dict(),
        "localization_texts": {k: v.dict() for k, v in _localization_texts.items()},
        "exported_at": datetime.now().isoformat()
    }


@router.get("/health/check")
async def health_check():
    """Health check for system settings service."""
    return {
        "status": "healthy",
        "service": "system-settings",
        "pvgis_enabled": _settings.pvgis.enabled,
        "debug_mode": _settings.debug.enable_test_mode,
        "timestamp": datetime.now().isoformat()
    }
