"""
Heat Pump Building Data Integration API

Provides REST API for heat pump building data and heating load calculations:
- Heated area input and validation
- Heating load calculation from building data
- Heating demand estimation from building age and area
- Insulation standard selection
- Heating system type selection

Requirements: funktionen.txt - "Gebäude- und Heizungsdaten"
Task: 254. Heat Pump Building Data Integration
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

router = APIRouter(prefix="/heatpump/building", tags=["Heat Pump Building Data"])


# ==================== Enums ====================

class InsulationStandard(str, Enum):
    """Insulation standard classification"""
    POOR = "poor"                    # Unsaniert (vor 1978)
    MODERATE = "moderate"            # Teilsaniert (1978-1995)
    GOOD = "good"                    # Gut gedämmt (1995-2009)
    EXCELLENT = "excellent"          # Sehr gut gedämmt (nach 2009)
    PASSIVE_HOUSE = "passive_house"  # Passivhaus-Standard


class HeatingSystemType(str, Enum):
    """Heating system type"""
    FLOOR_HEATING = "floor_heating"      # Fußbodenheizung
    RADIATORS_LOW = "radiators_low"      # Heizkörper Niedertemperatur
    RADIATORS_HIGH = "radiators_high"    # Heizkörper Hochtemperatur
    WALL_HEATING = "wall_heating"        # Wandheizung
    CEILING_HEATING = "ceiling_heating"  # Deckenheizung
    MIXED = "mixed"                      # Gemischtes System


class BuildingType(str, Enum):
    """Building type classification"""
    SINGLE_FAMILY = "single_family"      # Einfamilienhaus
    SEMI_DETACHED = "semi_detached"      # Doppelhaushälfte
    ROW_HOUSE = "row_house"              # Reihenhaus
    APARTMENT = "apartment"              # Wohnung
    MULTI_FAMILY = "multi_family"        # Mehrfamilienhaus
    COMMERCIAL = "commercial"            # Gewerbe


class OldHeatingSystem(str, Enum):
    """Old heating system type"""
    OIL = "oil"                          # Ölheizung
    GAS = "gas"                          # Gasheizung
    ELECTRIC = "electric"                # Elektroheizung
    COAL = "coal"                        # Kohleheizung
    WOOD = "wood"                        # Holzheizung
    DISTRICT = "district"                # Fernwärme
    NONE = "none"                        # Keine/Neu


# ==================== Pydantic Models ====================

class BuildingDataRequest(BaseModel):
    """Request for building data input"""
    heated_area_m2: float = Field(..., gt=0, le=10000, description="Beheizte Fläche in m²")
    building_year: Optional[int] = Field(None, ge=1800, le=2030, description="Baujahr")
    building_type: BuildingType = Field(default=BuildingType.SINGLE_FAMILY)
    insulation_standard: Optional[InsulationStandard] = Field(None)
    heating_system_type: HeatingSystemType = Field(default=HeatingSystemType.FLOOR_HEATING)
    old_heating_system: OldHeatingSystem = Field(default=OldHeatingSystem.GAS)
    number_of_floors: int = Field(default=2, ge=1, le=10)
    number_of_residents: int = Field(default=4, ge=1, le=20)
    hot_water_included: bool = Field(default=True, description="Warmwasser über Wärmepumpe")
    location_climate_zone: Optional[str] = Field(None, description="Klimazone (z.B. 'mild', 'kalt')")


class HeatingLoadResult(BaseModel):
    """Result of heating load calculation"""
    heating_load_kw: float = Field(..., description="Heizlast in kW")
    specific_heating_load_w_m2: float = Field(..., description="Spezifische Heizlast in W/m²")
    annual_heating_demand_kwh: float = Field(..., description="Jahresheizwärmebedarf in kWh")
    hot_water_demand_kwh: float = Field(..., description="Warmwasserbedarf in kWh/Jahr")
    total_heat_demand_kwh: float = Field(..., description="Gesamtwärmebedarf in kWh/Jahr")
    recommended_hp_power_kw: float = Field(..., description="Empfohlene WP-Leistung in kW")
    flow_temperature_c: float = Field(..., description="Vorlauftemperatur in °C")
    calculation_details: Dict[str, Any] = Field(default_factory=dict)


class InsulationInfo(BaseModel):
    """Information about insulation standard"""
    standard: InsulationStandard
    label_de: str
    description_de: str
    specific_heat_demand_kwh_m2: float
    u_value_range: str
    typical_building_years: str


class HeatingSystemInfo(BaseModel):
    """Information about heating system type"""
    system_type: HeatingSystemType
    label_de: str
    description_de: str
    flow_temperature_c: float
    return_temperature_c: float
    cop_factor: float
    suitable_for_hp: bool


class BuildingDataResponse(BaseModel):
    """Response with building data analysis"""
    building_data: Dict[str, Any]
    heating_load: HeatingLoadResult
    recommendations: List[str]
    warnings: List[str]


# ==================== Constants ====================

# Specific heating demand by insulation standard (kWh/m²/year)
SPECIFIC_HEAT_DEMAND = {
    InsulationStandard.POOR: 200,           # Unsaniert
    InsulationStandard.MODERATE: 130,       # Teilsaniert
    InsulationStandard.GOOD: 80,            # Gut gedämmt
    InsulationStandard.EXCELLENT: 50,       # Sehr gut gedämmt
    InsulationStandard.PASSIVE_HOUSE: 15,   # Passivhaus
}

# Specific heating load by insulation standard (W/m²)
SPECIFIC_HEATING_LOAD = {
    InsulationStandard.POOR: 120,
    InsulationStandard.MODERATE: 80,
    InsulationStandard.GOOD: 50,
    InsulationStandard.EXCELLENT: 35,
    InsulationStandard.PASSIVE_HOUSE: 15,
}

# Flow temperatures by heating system type (°C)
FLOW_TEMPERATURES = {
    HeatingSystemType.FLOOR_HEATING: 35,
    HeatingSystemType.RADIATORS_LOW: 45,
    HeatingSystemType.RADIATORS_HIGH: 55,
    HeatingSystemType.WALL_HEATING: 35,
    HeatingSystemType.CEILING_HEATING: 35,
    HeatingSystemType.MIXED: 45,
}

# COP factors by heating system (higher = better for heat pump)
COP_FACTORS = {
    HeatingSystemType.FLOOR_HEATING: 1.0,
    HeatingSystemType.RADIATORS_LOW: 0.9,
    HeatingSystemType.RADIATORS_HIGH: 0.8,
    HeatingSystemType.WALL_HEATING: 1.0,
    HeatingSystemType.CEILING_HEATING: 0.95,
    HeatingSystemType.MIXED: 0.9,
}

# Building type factors (affects heating load)
BUILDING_TYPE_FACTORS = {
    BuildingType.SINGLE_FAMILY: 1.0,
    BuildingType.SEMI_DETACHED: 0.9,
    BuildingType.ROW_HOUSE: 0.85,
    BuildingType.APARTMENT: 0.75,
    BuildingType.MULTI_FAMILY: 0.8,
    BuildingType.COMMERCIAL: 1.1,
}

# Hot water demand per person (kWh/year)
HOT_WATER_DEMAND_PER_PERSON = 500

# Full load hours for Germany (average)
FULL_LOAD_HOURS = 2000


# ==================== Helper Functions ====================

def estimate_insulation_from_year(building_year: int) -> InsulationStandard:
    """Estimate insulation standard from building year"""
    if building_year < 1978:
        return InsulationStandard.POOR
    elif building_year < 1995:
        return InsulationStandard.MODERATE
    elif building_year < 2009:
        return InsulationStandard.GOOD
    elif building_year < 2016:
        return InsulationStandard.EXCELLENT
    else:
        return InsulationStandard.EXCELLENT  # Could be passive house


def calculate_heating_load(
    heated_area_m2: float,
    insulation_standard: InsulationStandard,
    building_type: BuildingType,
    number_of_floors: int
) -> float:
    """Calculate heating load in kW"""
    # Base specific heating load
    specific_load = SPECIFIC_HEATING_LOAD[insulation_standard]
    
    # Apply building type factor
    building_factor = BUILDING_TYPE_FACTORS[building_type]
    
    # Apply floor factor (more floors = slightly higher load)
    floor_factor = 1.0 + (number_of_floors - 1) * 0.05
    
    # Calculate total heating load
    heating_load_w = heated_area_m2 * specific_load * building_factor * floor_factor
    
    return round(heating_load_w / 1000, 2)  # Convert to kW


def calculate_annual_heating_demand(
    heated_area_m2: float,
    insulation_standard: InsulationStandard,
    building_type: BuildingType
) -> float:
    """Calculate annual heating demand in kWh"""
    # Base specific heat demand
    specific_demand = SPECIFIC_HEAT_DEMAND[insulation_standard]
    
    # Apply building type factor
    building_factor = BUILDING_TYPE_FACTORS[building_type]
    
    return round(heated_area_m2 * specific_demand * building_factor, 0)


def calculate_hot_water_demand(
    number_of_residents: int,
    hot_water_included: bool
) -> float:
    """Calculate annual hot water demand in kWh"""
    if not hot_water_included:
        return 0.0
    return number_of_residents * HOT_WATER_DEMAND_PER_PERSON


def recommend_hp_power(
    heating_load_kw: float,
    hot_water_included: bool
) -> float:
    """Recommend heat pump power based on heating load"""
    # Add 10-20% buffer for hot water if included
    buffer_factor = 1.15 if hot_water_included else 1.0
    
    recommended = heating_load_kw * buffer_factor
    
    # Round to common heat pump sizes
    common_sizes = [3, 5, 7, 9, 11, 14, 17, 20, 25, 30]
    for size in common_sizes:
        if recommended <= size:
            return float(size)
    
    return round(recommended, 0)


def get_flow_temperature(heating_system: HeatingSystemType) -> float:
    """Get flow temperature for heating system"""
    return FLOW_TEMPERATURES.get(heating_system, 45)


def generate_recommendations(
    insulation_standard: InsulationStandard,
    heating_system: HeatingSystemType,
    heating_load_kw: float,
    building_year: Optional[int]
) -> List[str]:
    """Generate recommendations based on building data"""
    recommendations = []
    
    # Insulation recommendations
    if insulation_standard in [InsulationStandard.POOR, InsulationStandard.MODERATE]:
        recommendations.append(
            "Empfehlung: Vor Installation einer Wärmepumpe sollte die Gebäudedämmung verbessert werden."
        )
    
    # Heating system recommendations
    if heating_system == HeatingSystemType.RADIATORS_HIGH:
        recommendations.append(
            "Hinweis: Hochtemperatur-Heizkörper reduzieren die Effizienz der Wärmepumpe. "
            "Prüfen Sie den Austausch gegen Niedertemperatur-Heizkörper oder Fußbodenheizung."
        )
    
    # Size recommendations
    if heating_load_kw > 20:
        recommendations.append(
            "Bei hoher Heizlast kann eine Kaskadenlösung mit mehreren Wärmepumpen sinnvoll sein."
        )
    
    # Building age recommendations
    if building_year and building_year < 1978:
        recommendations.append(
            "Altbau vor 1978: Hydraulischer Abgleich und ggf. Heizkörpertausch empfohlen."
        )
    
    # General recommendations
    recommendations.append(
        "Tipp: Ein Pufferspeicher erhöht die Effizienz und reduziert Taktung der Wärmepumpe."
    )
    
    return recommendations


def generate_warnings(
    insulation_standard: InsulationStandard,
    heating_system: HeatingSystemType,
    heating_load_kw: float
) -> List[str]:
    """Generate warnings based on building data"""
    warnings = []
    
    # Poor insulation warning
    if insulation_standard == InsulationStandard.POOR:
        warnings.append(
            "⚠️ Warnung: Bei ungedämmten Gebäuden ist der Betrieb einer Wärmepumpe "
            "oft unwirtschaftlich. Sanierung dringend empfohlen."
        )
    
    # High temperature warning
    if heating_system == HeatingSystemType.RADIATORS_HIGH:
        warnings.append(
            "⚠️ Warnung: Hochtemperatur-Heizkörper (>55°C) führen zu deutlich "
            "reduzierter Effizienz (COP) der Wärmepumpe."
        )
    
    # Very high heating load
    if heating_load_kw > 30:
        warnings.append(
            "⚠️ Hinweis: Sehr hohe Heizlast. Prüfen Sie die Wirtschaftlichkeit "
            "und erwägen Sie Sanierungsmaßnahmen."
        )
    
    return warnings


# ==================== API Endpoints ====================

@router.post("/calculate", response_model=BuildingDataResponse)
async def calculate_building_data(request: BuildingDataRequest):
    """
    Calculate heating load and demand from building data.
    
    Analyzes building characteristics and calculates:
    - Heating load (kW)
    - Annual heating demand (kWh)
    - Hot water demand (kWh)
    - Recommended heat pump power
    """
    # Determine insulation standard
    insulation = request.insulation_standard
    if insulation is None and request.building_year:
        insulation = estimate_insulation_from_year(request.building_year)
    elif insulation is None:
        insulation = InsulationStandard.MODERATE  # Default
    
    # Calculate heating load
    heating_load_kw = calculate_heating_load(
        request.heated_area_m2,
        insulation,
        request.building_type,
        request.number_of_floors
    )
    
    # Calculate specific heating load
    specific_load = round(heating_load_kw * 1000 / request.heated_area_m2, 1)
    
    # Calculate annual heating demand
    annual_demand = calculate_annual_heating_demand(
        request.heated_area_m2,
        insulation,
        request.building_type
    )
    
    # Calculate hot water demand
    hot_water_demand = calculate_hot_water_demand(
        request.number_of_residents,
        request.hot_water_included
    )
    
    # Total heat demand
    total_demand = annual_demand + hot_water_demand
    
    # Recommended HP power
    recommended_power = recommend_hp_power(heating_load_kw, request.hot_water_included)
    
    # Flow temperature
    flow_temp = get_flow_temperature(request.heating_system_type)
    
    # Create heating load result
    heating_load_result = HeatingLoadResult(
        heating_load_kw=heating_load_kw,
        specific_heating_load_w_m2=specific_load,
        annual_heating_demand_kwh=annual_demand,
        hot_water_demand_kwh=hot_water_demand,
        total_heat_demand_kwh=total_demand,
        recommended_hp_power_kw=recommended_power,
        flow_temperature_c=flow_temp,
        calculation_details={
            "insulation_standard": insulation.value,
            "building_type_factor": BUILDING_TYPE_FACTORS[request.building_type],
            "cop_factor": COP_FACTORS[request.heating_system_type],
            "full_load_hours": FULL_LOAD_HOURS
        }
    )
    
    # Generate recommendations and warnings
    recommendations = generate_recommendations(
        insulation,
        request.heating_system_type,
        heating_load_kw,
        request.building_year
    )
    
    warnings = generate_warnings(
        insulation,
        request.heating_system_type,
        heating_load_kw
    )
    
    return BuildingDataResponse(
        building_data={
            "heated_area_m2": request.heated_area_m2,
            "building_year": request.building_year,
            "building_type": request.building_type.value,
            "insulation_standard": insulation.value,
            "heating_system_type": request.heating_system_type.value,
            "old_heating_system": request.old_heating_system.value,
            "number_of_floors": request.number_of_floors,
            "number_of_residents": request.number_of_residents,
            "hot_water_included": request.hot_water_included
        },
        heating_load=heating_load_result,
        recommendations=recommendations,
        warnings=warnings
    )


@router.get("/insulation-standards", response_model=List[InsulationInfo])
async def get_insulation_standards():
    """
    Get all available insulation standards with descriptions.
    """
    standards = [
        InsulationInfo(
            standard=InsulationStandard.POOR,
            label_de="Unsaniert",
            description_de="Gebäude ohne nennenswerte Dämmung, typisch vor 1978",
            specific_heat_demand_kwh_m2=200,
            u_value_range="> 1.0 W/(m²K)",
            typical_building_years="vor 1978"
        ),
        InsulationInfo(
            standard=InsulationStandard.MODERATE,
            label_de="Teilsaniert",
            description_de="Gebäude mit teilweiser Dämmung, typisch 1978-1995",
            specific_heat_demand_kwh_m2=130,
            u_value_range="0.5 - 1.0 W/(m²K)",
            typical_building_years="1978 - 1995"
        ),
        InsulationInfo(
            standard=InsulationStandard.GOOD,
            label_de="Gut gedämmt",
            description_de="Gebäude nach EnEV/WSchV, typisch 1995-2009",
            specific_heat_demand_kwh_m2=80,
            u_value_range="0.3 - 0.5 W/(m²K)",
            typical_building_years="1995 - 2009"
        ),
        InsulationInfo(
            standard=InsulationStandard.EXCELLENT,
            label_de="Sehr gut gedämmt",
            description_de="Gebäude nach EnEV 2009/2014, KfW-Effizienzhaus",
            specific_heat_demand_kwh_m2=50,
            u_value_range="0.15 - 0.3 W/(m²K)",
            typical_building_years="nach 2009"
        ),
        InsulationInfo(
            standard=InsulationStandard.PASSIVE_HOUSE,
            label_de="Passivhaus-Standard",
            description_de="Passivhaus oder vergleichbar, minimaler Heizwärmebedarf",
            specific_heat_demand_kwh_m2=15,
            u_value_range="< 0.15 W/(m²K)",
            typical_building_years="Passivhaus-Zertifizierung"
        )
    ]
    return standards


@router.get("/heating-systems", response_model=List[HeatingSystemInfo])
async def get_heating_systems():
    """
    Get all available heating system types with specifications.
    """
    systems = [
        HeatingSystemInfo(
            system_type=HeatingSystemType.FLOOR_HEATING,
            label_de="Fußbodenheizung",
            description_de="Flächenheizung im Boden, ideal für Wärmepumpen",
            flow_temperature_c=35,
            return_temperature_c=28,
            cop_factor=1.0,
            suitable_for_hp=True
        ),
        HeatingSystemInfo(
            system_type=HeatingSystemType.WALL_HEATING,
            label_de="Wandheizung",
            description_de="Flächenheizung in der Wand, sehr gut für Wärmepumpen",
            flow_temperature_c=35,
            return_temperature_c=28,
            cop_factor=1.0,
            suitable_for_hp=True
        ),
        HeatingSystemInfo(
            system_type=HeatingSystemType.CEILING_HEATING,
            label_de="Deckenheizung",
            description_de="Flächenheizung in der Decke, gut für Wärmepumpen",
            flow_temperature_c=35,
            return_temperature_c=28,
            cop_factor=0.95,
            suitable_for_hp=True
        ),
        HeatingSystemInfo(
            system_type=HeatingSystemType.RADIATORS_LOW,
            label_de="Heizkörper (Niedertemperatur)",
            description_de="Moderne Niedertemperatur-Heizkörper, geeignet für Wärmepumpen",
            flow_temperature_c=45,
            return_temperature_c=35,
            cop_factor=0.9,
            suitable_for_hp=True
        ),
        HeatingSystemInfo(
            system_type=HeatingSystemType.RADIATORS_HIGH,
            label_de="Heizkörper (Hochtemperatur)",
            description_de="Klassische Heizkörper, bedingt geeignet für Wärmepumpen",
            flow_temperature_c=55,
            return_temperature_c=45,
            cop_factor=0.8,
            suitable_for_hp=False
        ),
        HeatingSystemInfo(
            system_type=HeatingSystemType.MIXED,
            label_de="Gemischtes System",
            description_de="Kombination aus Fußbodenheizung und Heizkörpern",
            flow_temperature_c=45,
            return_temperature_c=35,
            cop_factor=0.9,
            suitable_for_hp=True
        )
    ]
    return systems


@router.get("/building-types")
async def get_building_types():
    """
    Get all available building types.
    """
    return {
        "building_types": [
            {"type": BuildingType.SINGLE_FAMILY.value, "label_de": "Einfamilienhaus", "factor": 1.0},
            {"type": BuildingType.SEMI_DETACHED.value, "label_de": "Doppelhaushälfte", "factor": 0.9},
            {"type": BuildingType.ROW_HOUSE.value, "label_de": "Reihenhaus", "factor": 0.85},
            {"type": BuildingType.APARTMENT.value, "label_de": "Wohnung", "factor": 0.75},
            {"type": BuildingType.MULTI_FAMILY.value, "label_de": "Mehrfamilienhaus", "factor": 0.8},
            {"type": BuildingType.COMMERCIAL.value, "label_de": "Gewerbe", "factor": 1.1}
        ]
    }


@router.get("/old-heating-systems")
async def get_old_heating_systems():
    """
    Get all available old heating system types for comparison.
    """
    return {
        "old_heating_systems": [
            {
                "type": OldHeatingSystem.OIL.value,
                "label_de": "Ölheizung",
                "efficiency": 0.85,
                "co2_factor_kg_kwh": 0.266
            },
            {
                "type": OldHeatingSystem.GAS.value,
                "label_de": "Gasheizung",
                "efficiency": 0.90,
                "co2_factor_kg_kwh": 0.201
            },
            {
                "type": OldHeatingSystem.ELECTRIC.value,
                "label_de": "Elektroheizung",
                "efficiency": 1.0,
                "co2_factor_kg_kwh": 0.420
            },
            {
                "type": OldHeatingSystem.COAL.value,
                "label_de": "Kohleheizung",
                "efficiency": 0.70,
                "co2_factor_kg_kwh": 0.338
            },
            {
                "type": OldHeatingSystem.WOOD.value,
                "label_de": "Holzheizung",
                "efficiency": 0.80,
                "co2_factor_kg_kwh": 0.036
            },
            {
                "type": OldHeatingSystem.DISTRICT.value,
                "label_de": "Fernwärme",
                "efficiency": 0.95,
                "co2_factor_kg_kwh": 0.180
            },
            {
                "type": OldHeatingSystem.NONE.value,
                "label_de": "Keine/Neubau",
                "efficiency": 1.0,
                "co2_factor_kg_kwh": 0.0
            }
        ]
    }


@router.get("/estimate-insulation")
async def estimate_insulation(
    building_year: int = Query(..., ge=1800, le=2030, description="Baujahr des Gebäudes")
):
    """
    Estimate insulation standard from building year.
    """
    insulation = estimate_insulation_from_year(building_year)
    
    return {
        "building_year": building_year,
        "estimated_insulation": insulation.value,
        "specific_heat_demand_kwh_m2": SPECIFIC_HEAT_DEMAND[insulation],
        "specific_heating_load_w_m2": SPECIFIC_HEATING_LOAD[insulation],
        "note": "Dies ist eine Schätzung. Der tatsächliche Dämmstandard kann abweichen."
    }


@router.get("/quick-calculation")
async def quick_calculation(
    heated_area_m2: float = Query(..., gt=0, le=10000),
    building_year: int = Query(None, ge=1800, le=2030),
    insulation: InsulationStandard = Query(None)
):
    """
    Quick heating load calculation with minimal input.
    """
    # Determine insulation
    if insulation is None:
        if building_year:
            insulation = estimate_insulation_from_year(building_year)
        else:
            insulation = InsulationStandard.MODERATE
    
    # Calculate heating load
    heating_load_kw = calculate_heating_load(
        heated_area_m2,
        insulation,
        BuildingType.SINGLE_FAMILY,
        2
    )
    
    # Calculate annual demand
    annual_demand = calculate_annual_heating_demand(
        heated_area_m2,
        insulation,
        BuildingType.SINGLE_FAMILY
    )
    
    # Recommended HP power
    recommended_power = recommend_hp_power(heating_load_kw, True)
    
    return {
        "heated_area_m2": heated_area_m2,
        "insulation_standard": insulation.value,
        "heating_load_kw": heating_load_kw,
        "annual_heating_demand_kwh": annual_demand,
        "recommended_hp_power_kw": recommended_power,
        "note": "Schnellberechnung mit Standardannahmen"
    }


@router.get("/health/check")
async def health_check():
    """
    Health check for heat pump building data service.
    """
    return {
        "status": "healthy",
        "service": "heatpump-building-data",
        "insulation_standards": len(InsulationStandard),
        "heating_systems": len(HeatingSystemType),
        "building_types": len(BuildingType),
        "timestamp": datetime.now().isoformat()
    }
