"""
Interactive UI Components API

Provides REST API for interactive UI components:
- Dropdown menus with search
- Sliders for continuous values
- Date picker components
- Checkbox groups
- Info tooltips with explanations
- Form validation helpers

Requirements: funktionen.txt - "interaktive Steuerelemente"
Task: 281. Interactive UI Components
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, date
from enum import Enum

router = APIRouter(prefix="/ui-components", tags=["UI Components"])


# ==================== Enums ====================

class ComponentType(str, Enum):
    DROPDOWN = "dropdown"
    SLIDER = "slider"
    DATE_PICKER = "date_picker"
    CHECKBOX_GROUP = "checkbox_group"
    RADIO_GROUP = "radio_group"
    NUMBER_INPUT = "number_input"
    TEXT_INPUT = "text_input"
    TOGGLE = "toggle"


class ValidationRule(str, Enum):
    REQUIRED = "required"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    EMAIL = "email"
    PHONE = "phone"


# ==================== Pydantic Models ====================

class DropdownOption(BaseModel):
    """Dropdown option"""
    value: str
    label: str
    description: Optional[str] = None
    icon: Optional[str] = None
    disabled: bool = False
    group: Optional[str] = None


class DropdownConfig(BaseModel):
    """Dropdown configuration"""
    id: str
    label: str
    options: List[DropdownOption]
    placeholder: str = "Bitte wählen..."
    searchable: bool = True
    clearable: bool = True
    multi_select: bool = False
    default_value: Optional[Union[str, List[str]]] = None
    tooltip: Optional[str] = None
    required: bool = False


class SliderConfig(BaseModel):
    """Slider configuration"""
    id: str
    label: str
    min_value: float
    max_value: float
    step: float = 1.0
    default_value: float
    unit: Optional[str] = None
    show_value: bool = True
    show_range: bool = True
    marks: Optional[Dict[float, str]] = None
    tooltip: Optional[str] = None
    required: bool = False


class DatePickerConfig(BaseModel):
    """Date picker configuration"""
    id: str
    label: str
    min_date: Optional[date] = None
    max_date: Optional[date] = None
    default_value: Optional[date] = None
    date_format: str = "DD.MM.YYYY"
    show_time: bool = False
    range_mode: bool = False
    tooltip: Optional[str] = None
    required: bool = False


class CheckboxOption(BaseModel):
    """Checkbox option"""
    value: str
    label: str
    description: Optional[str] = None
    default_checked: bool = False
    disabled: bool = False


class CheckboxGroupConfig(BaseModel):
    """Checkbox group configuration"""
    id: str
    label: str
    options: List[CheckboxOption]
    min_selected: int = 0
    max_selected: Optional[int] = None
    layout: str = "vertical"  # vertical, horizontal, grid
    tooltip: Optional[str] = None


class NumberInputConfig(BaseModel):
    """Number input configuration"""
    id: str
    label: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: float = 1.0
    default_value: Optional[float] = None
    unit: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    decimal_places: int = 2
    thousand_separator: str = "."
    decimal_separator: str = ","
    tooltip: Optional[str] = None
    required: bool = False


class TooltipConfig(BaseModel):
    """Tooltip configuration"""
    id: str
    content: str
    title: Optional[str] = None
    position: str = "top"  # top, bottom, left, right
    trigger: str = "hover"  # hover, click
    max_width: int = 300
    has_link: bool = False
    link_url: Optional[str] = None
    link_text: Optional[str] = None


class FormFieldValidation(BaseModel):
    """Form field validation"""
    field_id: str
    rules: List[Dict[str, Any]]
    error_messages: Dict[str, str]


# ==================== Component Configurations ====================

# Solar Calculator Dropdowns
SOLAR_DROPDOWNS = {
    "roof_type": DropdownConfig(
        id="roof_type",
        label="Dachtyp",
        options=[
            DropdownOption(value="satteldach", label="Satteldach", description="Klassisches Giebeldach"),
            DropdownOption(value="pultdach", label="Pultdach", description="Einseitig geneigtes Dach"),
            DropdownOption(value="flachdach", label="Flachdach", description="Horizontales Dach"),
            DropdownOption(value="walmdach", label="Walmdach", description="Allseitig geneigtes Dach"),
            DropdownOption(value="krueppelwalmdach", label="Krüppelwalmdach", description="Walmdach mit verkürzten Giebeln"),
            DropdownOption(value="zeltdach", label="Zeltdach", description="Pyramidenförmiges Dach"),
        ],
        placeholder="Dachtyp auswählen...",
        tooltip="Der Dachtyp beeinflusst die Modulplatzierung und den Ertrag",
        required=True
    ),
    "orientation": DropdownConfig(
        id="orientation",
        label="Ausrichtung",
        options=[
            DropdownOption(value="north", label="Nord", description="0°"),
            DropdownOption(value="northeast", label="Nordost", description="45°"),
            DropdownOption(value="east", label="Ost", description="90°"),
            DropdownOption(value="southeast", label="Südost", description="135°"),
            DropdownOption(value="south", label="Süd", description="180° - Optimal"),
            DropdownOption(value="southwest", label="Südwest", description="225°"),
            DropdownOption(value="west", label="West", description="270°"),
            DropdownOption(value="northwest", label="Nordwest", description="315°"),
        ],
        default_value="south",
        tooltip="Südausrichtung liefert den höchsten Ertrag",
        required=True
    ),
    "module_type": DropdownConfig(
        id="module_type",
        label="Modultyp",
        options=[
            DropdownOption(value="mono_standard", label="Monokristallin Standard", description="380-400 Wp"),
            DropdownOption(value="mono_premium", label="Monokristallin Premium", description="400-430 Wp"),
            DropdownOption(value="mono_bifacial", label="Bifazial", description="Beidseitige Stromerzeugung"),
            DropdownOption(value="poly", label="Polykristallin", description="Günstigere Alternative"),
        ],
        searchable=True,
        tooltip="Monokristalline Module haben den höchsten Wirkungsgrad",
        required=True
    ),
    "inverter_type": DropdownConfig(
        id="inverter_type",
        label="Wechselrichter",
        options=[
            DropdownOption(value="string", label="String-Wechselrichter", description="Standard für Hausdächer"),
            DropdownOption(value="hybrid", label="Hybrid-Wechselrichter", description="Mit Speicheranschluss"),
            DropdownOption(value="micro", label="Mikro-Wechselrichter", description="Pro Modul"),
        ],
        tooltip="Hybrid-Wechselrichter ermöglichen späteren Speicheranschluss",
        required=True
    ),
    "battery_model": DropdownConfig(
        id="battery_model",
        label="Batteriespeicher",
        options=[
            DropdownOption(value="none", label="Kein Speicher", description="Ohne Batteriespeicher"),
            DropdownOption(value="5kwh", label="5 kWh", description="Für kleine Haushalte"),
            DropdownOption(value="10kwh", label="10 kWh", description="Standard für Einfamilienhäuser"),
            DropdownOption(value="15kwh", label="15 kWh", description="Für höheren Eigenverbrauch"),
            DropdownOption(value="20kwh", label="20 kWh", description="Für große Haushalte"),
        ],
        clearable=True,
        tooltip="Ein Speicher erhöht den Eigenverbrauch auf 60-80%"
    ),
}

# Solar Calculator Sliders
SOLAR_SLIDERS = {
    "roof_area": SliderConfig(
        id="roof_area",
        label="Dachfläche",
        min_value=20,
        max_value=200,
        step=5,
        default_value=80,
        unit="m²",
        marks={20: "20", 50: "50", 100: "100", 150: "150", 200: "200"},
        tooltip="Verfügbare Dachfläche für PV-Module"
    ),
    "roof_tilt": SliderConfig(
        id="roof_tilt",
        label="Dachneigung",
        min_value=0,
        max_value=60,
        step=5,
        default_value=30,
        unit="°",
        marks={0: "0° (Flach)", 30: "30° (Optimal)", 45: "45°", 60: "60° (Steil)"},
        tooltip="Optimale Neigung in Deutschland: 30-35°"
    ),
    "annual_consumption": SliderConfig(
        id="annual_consumption",
        label="Jahresverbrauch",
        min_value=1000,
        max_value=15000,
        step=500,
        default_value=4000,
        unit="kWh",
        marks={1000: "1.000", 4000: "4.000", 8000: "8.000", 15000: "15.000"},
        tooltip="Durchschnittlicher Stromverbrauch pro Jahr"
    ),
    "electricity_price": SliderConfig(
        id="electricity_price",
        label="Strompreis",
        min_value=0.20,
        max_value=0.50,
        step=0.01,
        default_value=0.30,
        unit="€/kWh",
        tooltip="Aktueller Strompreis vom Versorger"
    ),
}

# Heat Pump Dropdowns
HEATPUMP_DROPDOWNS = {
    "building_type": DropdownConfig(
        id="building_type",
        label="Gebäudetyp",
        options=[
            DropdownOption(value="single_family", label="Einfamilienhaus"),
            DropdownOption(value="multi_family", label="Mehrfamilienhaus"),
            DropdownOption(value="apartment", label="Wohnung"),
            DropdownOption(value="commercial", label="Gewerbe"),
        ],
        required=True
    ),
    "heating_system": DropdownConfig(
        id="heating_system",
        label="Heizsystem",
        options=[
            DropdownOption(value="floor", label="Fußbodenheizung", description="Optimal für Wärmepumpen"),
            DropdownOption(value="radiator", label="Heizkörper", description="Höhere Vorlauftemperatur"),
            DropdownOption(value="mixed", label="Gemischt", description="Kombination"),
        ],
        tooltip="Fußbodenheizung ermöglicht niedrigere Vorlauftemperaturen und höhere Effizienz"
    ),
    "heatpump_type": DropdownConfig(
        id="heatpump_type",
        label="Wärmepumpentyp",
        options=[
            DropdownOption(value="air_water", label="Luft-Wasser", description="Einfache Installation"),
            DropdownOption(value="ground_water", label="Sole-Wasser", description="Höhere Effizienz"),
            DropdownOption(value="water_water", label="Wasser-Wasser", description="Beste Effizienz"),
        ],
        tooltip="Luft-Wasser ist am weitesten verbreitet und einfach zu installieren"
    ),
    "current_heating": DropdownConfig(
        id="current_heating",
        label="Aktuelle Heizung",
        options=[
            DropdownOption(value="gas", label="Gas"),
            DropdownOption(value="oil", label="Öl"),
            DropdownOption(value="electric", label="Elektro"),
            DropdownOption(value="district", label="Fernwärme"),
            DropdownOption(value="pellet", label="Pellet"),
        ],
        tooltip="Für Vergleichsberechnung der Heizkosten"
    ),
}

# Heat Pump Sliders
HEATPUMP_SLIDERS = {
    "living_area": SliderConfig(
        id="living_area",
        label="Wohnfläche",
        min_value=50,
        max_value=400,
        step=10,
        default_value=150,
        unit="m²",
        tooltip="Beheizte Wohnfläche"
    ),
    "building_year": SliderConfig(
        id="building_year",
        label="Baujahr",
        min_value=1950,
        max_value=2024,
        step=1,
        default_value=1990,
        marks={1950: "1950", 1980: "1980", 2000: "2000", 2024: "2024"},
        tooltip="Baujahr beeinflusst den Dämmstandard"
    ),
    "current_consumption": SliderConfig(
        id="current_consumption",
        label="Aktueller Verbrauch",
        min_value=5000,
        max_value=50000,
        step=1000,
        default_value=20000,
        unit="kWh",
        tooltip="Aktueller Heizenergieverbrauch pro Jahr"
    ),
}

# Info Tooltips
INFO_TOOLTIPS = {
    "eigenverbrauch": TooltipConfig(
        id="eigenverbrauch",
        title="Eigenverbrauch",
        content="Der Eigenverbrauch gibt an, wie viel des selbst erzeugten Stroms direkt im Haushalt verbraucht wird. Ein höherer Eigenverbrauch bedeutet mehr Einsparungen.",
        position="right"
    ),
    "autarkie": TooltipConfig(
        id="autarkie",
        title="Autarkiegrad",
        content="Der Autarkiegrad zeigt, wie unabhängig Sie vom Stromnetz sind. 100% bedeutet vollständige Unabhängigkeit.",
        position="right"
    ),
    "amortisation": TooltipConfig(
        id="amortisation",
        title="Amortisationszeit",
        content="Die Zeit, bis sich die Investition durch Einsparungen bezahlt gemacht hat. Typisch sind 8-12 Jahre.",
        position="right"
    ),
    "cop": TooltipConfig(
        id="cop",
        title="COP (Coefficient of Performance)",
        content="Der COP gibt an, wie viel Wärme aus einer Einheit Strom erzeugt wird. Ein COP von 4 bedeutet: 1 kWh Strom → 4 kWh Wärme.",
        position="right"
    ),
    "jaz": TooltipConfig(
        id="jaz",
        title="JAZ (Jahresarbeitszahl)",
        content="Die JAZ ist der durchschnittliche COP über ein ganzes Jahr. Sie berücksichtigt alle Betriebszustände und Temperaturen.",
        position="right"
    ),
    "kwp": TooltipConfig(
        id="kwp",
        title="kWp (Kilowatt Peak)",
        content="Die Nennleistung einer PV-Anlage unter Standardtestbedingungen. 1 kWp erzeugt in Deutschland ca. 900-1100 kWh pro Jahr.",
        position="right"
    ),
}


# ==================== API Endpoints ====================

@router.get("/dropdowns")
async def get_dropdown_configs(category: Optional[str] = None):
    """Get dropdown configurations."""
    if category == "solar":
        return {"dropdowns": SOLAR_DROPDOWNS}
    elif category == "heatpump":
        return {"dropdowns": HEATPUMP_DROPDOWNS}
    else:
        return {
            "dropdowns": {
                "solar": SOLAR_DROPDOWNS,
                "heatpump": HEATPUMP_DROPDOWNS
            }
        }


@router.get("/dropdowns/{dropdown_id}")
async def get_dropdown_config(dropdown_id: str):
    """Get specific dropdown configuration."""
    if dropdown_id in SOLAR_DROPDOWNS:
        return {"dropdown": SOLAR_DROPDOWNS[dropdown_id]}
    elif dropdown_id in HEATPUMP_DROPDOWNS:
        return {"dropdown": HEATPUMP_DROPDOWNS[dropdown_id]}
    else:
        raise HTTPException(status_code=404, detail="Dropdown nicht gefunden")


@router.get("/sliders")
async def get_slider_configs(category: Optional[str] = None):
    """Get slider configurations."""
    if category == "solar":
        return {"sliders": SOLAR_SLIDERS}
    elif category == "heatpump":
        return {"sliders": HEATPUMP_SLIDERS}
    else:
        return {
            "sliders": {
                "solar": SOLAR_SLIDERS,
                "heatpump": HEATPUMP_SLIDERS
            }
        }


@router.get("/sliders/{slider_id}")
async def get_slider_config(slider_id: str):
    """Get specific slider configuration."""
    if slider_id in SOLAR_SLIDERS:
        return {"slider": SOLAR_SLIDERS[slider_id]}
    elif slider_id in HEATPUMP_SLIDERS:
        return {"slider": HEATPUMP_SLIDERS[slider_id]}
    else:
        raise HTTPException(status_code=404, detail="Slider nicht gefunden")


@router.get("/tooltips")
async def get_tooltip_configs():
    """Get all tooltip configurations."""
    return {"tooltips": INFO_TOOLTIPS}


@router.get("/tooltips/{tooltip_id}")
async def get_tooltip_config(tooltip_id: str):
    """Get specific tooltip configuration."""
    if tooltip_id not in INFO_TOOLTIPS:
        raise HTTPException(status_code=404, detail="Tooltip nicht gefunden")
    return {"tooltip": INFO_TOOLTIPS[tooltip_id]}


@router.post("/validate")
async def validate_form_field(field_id: str, value: Any, rules: List[Dict[str, Any]]):
    """Validate form field value."""
    errors = []
    
    for rule in rules:
        rule_type = rule.get("type")
        
        if rule_type == "required" and (value is None or value == ""):
            errors.append(rule.get("message", "Dieses Feld ist erforderlich"))
        
        elif rule_type == "min_value" and value is not None:
            if float(value) < rule.get("value", 0):
                errors.append(rule.get("message", f"Mindestwert: {rule.get('value')}"))
        
        elif rule_type == "max_value" and value is not None:
            if float(value) > rule.get("value", 0):
                errors.append(rule.get("message", f"Maximalwert: {rule.get('value')}"))
        
        elif rule_type == "min_length" and value is not None:
            if len(str(value)) < rule.get("value", 0):
                errors.append(rule.get("message", f"Mindestlänge: {rule.get('value')} Zeichen"))
        
        elif rule_type == "max_length" and value is not None:
            if len(str(value)) > rule.get("value", 0):
                errors.append(rule.get("message", f"Maximallänge: {rule.get('value')} Zeichen"))
    
    return {
        "field_id": field_id,
        "value": value,
        "valid": len(errors) == 0,
        "errors": errors
    }


@router.get("/form-config/{form_type}")
async def get_form_config(form_type: str):
    """Get complete form configuration."""
    if form_type == "solar_basic":
        return {
            "form_type": form_type,
            "title": "PV-Anlage Grunddaten",
            "sections": [
                {
                    "id": "roof",
                    "title": "Dachdaten",
                    "fields": [
                        {"type": "dropdown", "config": SOLAR_DROPDOWNS["roof_type"]},
                        {"type": "slider", "config": SOLAR_SLIDERS["roof_area"]},
                        {"type": "slider", "config": SOLAR_SLIDERS["roof_tilt"]},
                        {"type": "dropdown", "config": SOLAR_DROPDOWNS["orientation"]},
                    ]
                },
                {
                    "id": "system",
                    "title": "Systemkonfiguration",
                    "fields": [
                        {"type": "dropdown", "config": SOLAR_DROPDOWNS["module_type"]},
                        {"type": "dropdown", "config": SOLAR_DROPDOWNS["inverter_type"]},
                        {"type": "dropdown", "config": SOLAR_DROPDOWNS["battery_model"]},
                    ]
                },
                {
                    "id": "consumption",
                    "title": "Verbrauchsdaten",
                    "fields": [
                        {"type": "slider", "config": SOLAR_SLIDERS["annual_consumption"]},
                        {"type": "slider", "config": SOLAR_SLIDERS["electricity_price"]},
                    ]
                }
            ]
        }
    
    elif form_type == "heatpump_basic":
        return {
            "form_type": form_type,
            "title": "Wärmepumpe Grunddaten",
            "sections": [
                {
                    "id": "building",
                    "title": "Gebäudedaten",
                    "fields": [
                        {"type": "dropdown", "config": HEATPUMP_DROPDOWNS["building_type"]},
                        {"type": "slider", "config": HEATPUMP_SLIDERS["living_area"]},
                        {"type": "slider", "config": HEATPUMP_SLIDERS["building_year"]},
                    ]
                },
                {
                    "id": "heating",
                    "title": "Heizsystem",
                    "fields": [
                        {"type": "dropdown", "config": HEATPUMP_DROPDOWNS["heating_system"]},
                        {"type": "dropdown", "config": HEATPUMP_DROPDOWNS["current_heating"]},
                        {"type": "slider", "config": HEATPUMP_SLIDERS["current_consumption"]},
                    ]
                },
                {
                    "id": "heatpump",
                    "title": "Wärmepumpe",
                    "fields": [
                        {"type": "dropdown", "config": HEATPUMP_DROPDOWNS["heatpump_type"]},
                    ]
                }
            ]
        }
    
    else:
        raise HTTPException(status_code=404, detail="Formular nicht gefunden")


@router.get("/health/check")
async def health_check():
    """Health check for UI components service."""
    return {
        "status": "healthy",
        "service": "ui-components-interactive",
        "dropdowns": len(SOLAR_DROPDOWNS) + len(HEATPUMP_DROPDOWNS),
        "sliders": len(SOLAR_SLIDERS) + len(HEATPUMP_SLIDERS),
        "tooltips": len(INFO_TOOLTIPS),
        "timestamp": datetime.now().isoformat()
    }
