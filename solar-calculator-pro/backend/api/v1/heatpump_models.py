"""
Heat Pump Model Selection API

Provides REST API for heat pump model selection and sizing:
- Heat pump selection from product database
- Display specifications (kW, COP, JAZ, price)
- Calculate sizing based on heating load
- Heat pump type selection (air/water, brine/water)
- Buffer storage recommendation

Requirements: funktionen.txt - "Wärmepumpen-Auslegung"
Task: 255. Heat Pump Model Selection
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

router = APIRouter(prefix="/heatpump/models", tags=["Heat Pump Models"])


# ==================== Enums ====================

class HeatPumpType(str, Enum):
    """Heat pump type classification"""
    AIR_WATER = "air_water"          # Luft/Wasser-Wärmepumpe
    BRINE_WATER = "brine_water"      # Sole/Wasser-Wärmepumpe (Erdwärme)
    WATER_WATER = "water_water"      # Wasser/Wasser-Wärmepumpe
    AIR_AIR = "air_air"              # Luft/Luft-Wärmepumpe


class HeatPumpCategory(str, Enum):
    """Heat pump category"""
    MONOBLOCK = "monoblock"          # Monoblock (Außenaufstellung)
    SPLIT = "split"                  # Split-System
    INDOOR = "indoor"                # Innenaufstellung
    HYBRID = "hybrid"                # Hybrid (mit Gas-Backup)


class EfficiencyClass(str, Enum):
    """Energy efficiency class"""
    A_PLUS_PLUS_PLUS = "A+++"
    A_PLUS_PLUS = "A++"
    A_PLUS = "A+"
    A = "A"
    B = "B"


# ==================== Pydantic Models ====================

class HeatPumpModel(BaseModel):
    """Heat pump model data"""
    id: str
    manufacturer: str
    model_name: str
    heat_pump_type: HeatPumpType
    category: HeatPumpCategory
    heating_power_kw: float = Field(..., description="Heizleistung in kW")
    cop_a7w35: float = Field(..., description="COP bei A7/W35")
    cop_a2w35: float = Field(..., description="COP bei A2/W35")
    cop_a_7w35: Optional[float] = Field(None, description="COP bei A-7/W35")
    jaz_estimate: float = Field(..., description="Geschätzte Jahresarbeitszahl")
    max_flow_temp_c: float = Field(..., description="Max. Vorlauftemperatur")
    noise_level_db: Optional[float] = Field(None, description="Schallleistungspegel")
    refrigerant: str = Field(default="R290", description="Kältemittel")
    efficiency_class: EfficiencyClass = Field(default=EfficiencyClass.A_PLUS_PLUS)
    price_net_eur: float = Field(..., description="Nettopreis in EUR")
    price_gross_eur: float = Field(..., description="Bruttopreis in EUR")
    warranty_years: int = Field(default=5)
    dimensions: Optional[Dict[str, float]] = None
    weight_kg: Optional[float] = None
    features: List[str] = Field(default_factory=list)
    datasheet_url: Optional[str] = None
    image_url: Optional[str] = None


class HeatPumpSizingRequest(BaseModel):
    """Request for heat pump sizing"""
    heating_load_kw: float = Field(..., gt=0, description="Heizlast in kW")
    hot_water_included: bool = Field(default=True)
    preferred_type: Optional[HeatPumpType] = None
    max_price_eur: Optional[float] = None
    min_cop: Optional[float] = Field(None, ge=2.0, le=6.0)
    max_noise_db: Optional[float] = None
    flow_temperature_c: float = Field(default=35, ge=25, le=65)


class HeatPumpSizingResult(BaseModel):
    """Result of heat pump sizing"""
    heating_load_kw: float
    recommended_power_kw: float
    sizing_factor: float
    recommended_models: List[HeatPumpModel]
    buffer_storage_recommendation: Dict[str, Any]
    notes: List[str]


class BufferStorageRecommendation(BaseModel):
    """Buffer storage recommendation"""
    recommended: bool
    min_volume_liters: int
    optimal_volume_liters: int
    reason: str
    hot_water_storage_liters: Optional[int] = None


# ==================== Sample Data ====================

SAMPLE_HEAT_PUMPS: List[Dict[str, Any]] = [
    {
        "id": "vaillant-arotherm-plus-7",
        "manufacturer": "Vaillant",
        "model_name": "aroTHERM plus VWL 75/6 A",
        "heat_pump_type": HeatPumpType.AIR_WATER,
        "category": HeatPumpCategory.MONOBLOCK,
        "heating_power_kw": 7.0,
        "cop_a7w35": 5.1,
        "cop_a2w35": 4.2,
        "cop_a_7w35": 3.1,
        "jaz_estimate": 4.0,
        "max_flow_temp_c": 75,
        "noise_level_db": 54,
        "refrigerant": "R290",
        "efficiency_class": EfficiencyClass.A_PLUS_PLUS_PLUS,
        "price_net_eur": 12500,
        "price_gross_eur": 14875,
        "warranty_years": 5,
        "features": ["Inverter", "Smart Grid Ready", "Kühlfunktion", "Natürliches Kältemittel"]
    },
    {
        "id": "vaillant-arotherm-plus-10",
        "manufacturer": "Vaillant",
        "model_name": "aroTHERM plus VWL 105/6 A",
        "heat_pump_type": HeatPumpType.AIR_WATER,
        "category": HeatPumpCategory.MONOBLOCK,
        "heating_power_kw": 10.0,
        "cop_a7w35": 4.9,
        "cop_a2w35": 4.0,
        "cop_a_7w35": 3.0,
        "jaz_estimate": 3.9,
        "max_flow_temp_c": 75,
        "noise_level_db": 56,
        "refrigerant": "R290",
        "efficiency_class": EfficiencyClass.A_PLUS_PLUS_PLUS,
        "price_net_eur": 14500,
        "price_gross_eur": 17255,
        "warranty_years": 5,
        "features": ["Inverter", "Smart Grid Ready", "Kühlfunktion"]
    },
    {
        "id": "viessmann-vitocal-250-a-8",
        "manufacturer": "Viessmann",
        "model_name": "Vitocal 250-A AWO-E-AC 251.A08",
        "heat_pump_type": HeatPumpType.AIR_WATER,
        "category": HeatPumpCategory.MONOBLOCK,
        "heating_power_kw": 8.0,
        "cop_a7w35": 5.0,
        "cop_a2w35": 4.1,
        "cop_a_7w35": 3.0,
        "jaz_estimate": 4.0,
        "max_flow_temp_c": 70,
        "noise_level_db": 55,
        "refrigerant": "R290",
        "efficiency_class": EfficiencyClass.A_PLUS_PLUS_PLUS,
        "price_net_eur": 13200,
        "price_gross_eur": 15708,
        "warranty_years": 5,
        "features": ["Inverter", "Vitoconnect", "Kühlfunktion"]
    },
    {
        "id": "viessmann-vitocal-250-a-13",
        "manufacturer": "Viessmann",
        "model_name": "Vitocal 250-A AWO-E-AC 251.A13",
        "heat_pump_type": HeatPumpType.AIR_WATER,
        "category": HeatPumpCategory.MONOBLOCK,
        "heating_power_kw": 13.0,
        "cop_a7w35": 4.7,
        "cop_a2w35": 3.9,
        "cop_a_7w35": 2.9,
        "jaz_estimate": 3.8,
        "max_flow_temp_c": 70,
        "noise_level_db": 58,
        "refrigerant": "R290",
        "efficiency_class": EfficiencyClass.A_PLUS_PLUS,
        "price_net_eur": 16500,
        "price_gross_eur": 19635,
        "warranty_years": 5,
        "features": ["Inverter", "Vitoconnect", "Kühlfunktion"]
    },
    {
        "id": "bosch-compress-7400i-aw-9",
        "manufacturer": "Bosch",
        "model_name": "Compress 7400i AW 9 OR-S",
        "heat_pump_type": HeatPumpType.AIR_WATER,
        "category": HeatPumpCategory.MONOBLOCK,
        "heating_power_kw": 9.0,
        "cop_a7w35": 4.8,
        "cop_a2w35": 4.0,
        "cop_a_7w35": 2.9,
        "jaz_estimate": 3.9,
        "max_flow_temp_c": 65,
        "noise_level_db": 56,
        "refrigerant": "R290",
        "efficiency_class": EfficiencyClass.A_PLUS_PLUS,
        "price_net_eur": 11800,
        "price_gross_eur": 14042,
        "warranty_years": 5,
        "features": ["Inverter", "HomeCom", "Kühlfunktion"]
    },
    {
        "id": "stiebel-eltron-wpl-17",
        "manufacturer": "Stiebel Eltron",
        "model_name": "WPL 17 ACS classic",
        "heat_pump_type": HeatPumpType.AIR_WATER,
        "category": HeatPumpCategory.MONOBLOCK,
        "heating_power_kw": 17.0,
        "cop_a7w35": 4.5,
        "cop_a2w35": 3.7,
        "cop_a_7w35": 2.8,
        "jaz_estimate": 3.7,
        "max_flow_temp_c": 65,
        "noise_level_db": 60,
        "refrigerant": "R410A",
        "efficiency_class": EfficiencyClass.A_PLUS_PLUS,
        "price_net_eur": 18500,
        "price_gross_eur": 22015,
        "warranty_years": 5,
        "features": ["Inverter", "ISG Web", "Kühlfunktion"]
    },
    {
        "id": "daikin-altherma-3-h-11",
        "manufacturer": "Daikin",
        "model_name": "Altherma 3 H HT ETBH16E6V",
        "heat_pump_type": HeatPumpType.AIR_WATER,
        "category": HeatPumpCategory.SPLIT,
        "heating_power_kw": 11.0,
        "cop_a7w35": 4.6,
        "cop_a2w35": 3.8,
        "cop_a_7w35": 2.9,
        "jaz_estimate": 3.8,
        "max_flow_temp_c": 70,
        "noise_level_db": 57,
        "refrigerant": "R32",
        "efficiency_class": EfficiencyClass.A_PLUS_PLUS,
        "price_net_eur": 14200,
        "price_gross_eur": 16898,
        "warranty_years": 5,
        "features": ["Inverter", "Onecta App", "Kühlfunktion", "Hochtemperatur"]
    },
    {
        "id": "wolf-cha-10",
        "manufacturer": "Wolf",
        "model_name": "CHA-10/400V Monoblock",
        "heat_pump_type": HeatPumpType.AIR_WATER,
        "category": HeatPumpCategory.MONOBLOCK,
        "heating_power_kw": 10.0,
        "cop_a7w35": 4.7,
        "cop_a2w35": 3.9,
        "cop_a_7w35": 2.9,
        "jaz_estimate": 3.8,
        "max_flow_temp_c": 65,
        "noise_level_db": 55,
        "refrigerant": "R290",
        "efficiency_class": EfficiencyClass.A_PLUS_PLUS,
        "price_net_eur": 12800,
        "price_gross_eur": 15232,
        "warranty_years": 5,
        "features": ["Inverter", "Smartset", "Kühlfunktion"]
    }
]


# ==================== Helper Functions ====================

def calculate_sizing_factor(heating_load_kw: float, hot_water: bool) -> float:
    """Calculate sizing factor for heat pump selection"""
    base_factor = 1.0
    if hot_water:
        base_factor += 0.15  # 15% extra for hot water
    return base_factor


def calculate_recommended_power(heating_load_kw: float, hot_water: bool) -> float:
    """Calculate recommended heat pump power"""
    factor = calculate_sizing_factor(heating_load_kw, hot_water)
    return round(heating_load_kw * factor, 1)


def calculate_buffer_storage(heating_power_kw: float, hot_water: bool) -> Dict[str, Any]:
    """Calculate buffer storage recommendation"""
    # Rule of thumb: 20-30 liters per kW heating power
    min_volume = int(heating_power_kw * 20)
    optimal_volume = int(heating_power_kw * 25)
    
    # Hot water storage: 50 liters per person (assume 4 persons)
    hot_water_storage = 200 if hot_water else None
    
    return {
        "recommended": True,
        "min_volume_liters": min_volume,
        "optimal_volume_liters": optimal_volume,
        "reason": "Pufferspeicher reduziert Taktung und erhöht Effizienz",
        "hot_water_storage_liters": hot_water_storage
    }


def filter_heat_pumps(
    models: List[Dict],
    min_power: float,
    max_power: float,
    preferred_type: Optional[HeatPumpType] = None,
    max_price: Optional[float] = None,
    min_cop: Optional[float] = None,
    max_noise: Optional[float] = None
) -> List[Dict]:
    """Filter heat pumps by criteria"""
    filtered = []
    
    for model in models:
        # Power range filter
        if model["heating_power_kw"] < min_power or model["heating_power_kw"] > max_power:
            continue
        
        # Type filter
        if preferred_type and model["heat_pump_type"] != preferred_type:
            continue
        
        # Price filter
        if max_price and model["price_gross_eur"] > max_price:
            continue
        
        # COP filter
        if min_cop and model["cop_a7w35"] < min_cop:
            continue
        
        # Noise filter
        if max_noise and model.get("noise_level_db") and model["noise_level_db"] > max_noise:
            continue
        
        filtered.append(model)
    
    return filtered


def sort_heat_pumps(models: List[Dict], sort_by: str = "cop") -> List[Dict]:
    """Sort heat pumps by criteria"""
    if sort_by == "cop":
        return sorted(models, key=lambda x: x["cop_a7w35"], reverse=True)
    elif sort_by == "price":
        return sorted(models, key=lambda x: x["price_gross_eur"])
    elif sort_by == "power":
        return sorted(models, key=lambda x: x["heating_power_kw"])
    elif sort_by == "noise":
        return sorted(models, key=lambda x: x.get("noise_level_db", 100))
    return models


def generate_sizing_notes(
    heating_load_kw: float,
    recommended_power: float,
    flow_temp: float,
    models_found: int
) -> List[str]:
    """Generate sizing notes and recommendations"""
    notes = []
    
    if heating_load_kw > 15:
        notes.append("Bei hoher Heizlast kann eine Kaskadenlösung sinnvoll sein.")
    
    if flow_temp > 50:
        notes.append("Hohe Vorlauftemperatur reduziert die Effizienz. Prüfen Sie Niedertemperatur-Optionen.")
    
    if models_found == 0:
        notes.append("Keine passenden Modelle gefunden. Erweitern Sie die Suchkriterien.")
    
    notes.append(f"Empfohlene Leistung: {recommended_power} kW (inkl. Sicherheitszuschlag)")
    notes.append("Pufferspeicher wird empfohlen für optimalen Betrieb.")
    
    return notes


# ==================== API Endpoints ====================

@router.get("/", response_model=List[HeatPumpModel])
async def get_all_heat_pumps(
    heat_pump_type: Optional[HeatPumpType] = None,
    category: Optional[HeatPumpCategory] = None,
    min_power_kw: Optional[float] = Query(None, ge=0),
    max_power_kw: Optional[float] = Query(None, le=50),
    manufacturer: Optional[str] = None,
    sort_by: str = Query("cop", regex="^(cop|price|power|noise)$")
):
    """
    Get all available heat pump models with optional filtering.
    """
    models = SAMPLE_HEAT_PUMPS.copy()
    
    # Apply filters
    if heat_pump_type:
        models = [m for m in models if m["heat_pump_type"] == heat_pump_type]
    
    if category:
        models = [m for m in models if m["category"] == category]
    
    if min_power_kw:
        models = [m for m in models if m["heating_power_kw"] >= min_power_kw]
    
    if max_power_kw:
        models = [m for m in models if m["heating_power_kw"] <= max_power_kw]
    
    if manufacturer:
        models = [m for m in models if manufacturer.lower() in m["manufacturer"].lower()]
    
    # Sort
    models = sort_heat_pumps(models, sort_by)
    
    return [HeatPumpModel(**m) for m in models]


@router.get("/{model_id}", response_model=HeatPumpModel)
async def get_heat_pump_by_id(model_id: str):
    """
    Get a specific heat pump model by ID.
    """
    for model in SAMPLE_HEAT_PUMPS:
        if model["id"] == model_id:
            return HeatPumpModel(**model)
    
    raise HTTPException(status_code=404, detail=f"Heat pump model {model_id} not found")


@router.post("/sizing", response_model=HeatPumpSizingResult)
async def calculate_heat_pump_sizing(request: HeatPumpSizingRequest):
    """
    Calculate heat pump sizing and recommend suitable models.
    """
    # Calculate recommended power
    sizing_factor = calculate_sizing_factor(request.heating_load_kw, request.hot_water_included)
    recommended_power = calculate_recommended_power(request.heating_load_kw, request.hot_water_included)
    
    # Define power range for filtering (±30%)
    min_power = request.heating_load_kw * 0.8
    max_power = recommended_power * 1.3
    
    # Filter models
    filtered = filter_heat_pumps(
        SAMPLE_HEAT_PUMPS,
        min_power=min_power,
        max_power=max_power,
        preferred_type=request.preferred_type,
        max_price=request.max_price_eur,
        min_cop=request.min_cop,
        max_noise=request.max_noise_db
    )
    
    # Sort by COP (best efficiency first)
    sorted_models = sort_heat_pumps(filtered, "cop")
    
    # Limit to top 5
    top_models = sorted_models[:5]
    
    # Calculate buffer storage
    buffer_storage = calculate_buffer_storage(recommended_power, request.hot_water_included)
    
    # Generate notes
    notes = generate_sizing_notes(
        request.heating_load_kw,
        recommended_power,
        request.flow_temperature_c,
        len(top_models)
    )
    
    return HeatPumpSizingResult(
        heating_load_kw=request.heating_load_kw,
        recommended_power_kw=recommended_power,
        sizing_factor=sizing_factor,
        recommended_models=[HeatPumpModel(**m) for m in top_models],
        buffer_storage_recommendation=buffer_storage,
        notes=notes
    )


@router.get("/types/list")
async def get_heat_pump_types():
    """
    Get all available heat pump types with descriptions.
    """
    return {
        "types": [
            {
                "type": HeatPumpType.AIR_WATER.value,
                "label_de": "Luft/Wasser-Wärmepumpe",
                "description_de": "Nutzt Außenluft als Wärmequelle. Einfache Installation.",
                "pros": ["Geringe Installationskosten", "Keine Erdarbeiten", "Flexibel einsetzbar"],
                "cons": ["Geringere Effizienz bei Kälte", "Geräuschentwicklung"],
                "typical_cop": "3.5-5.0",
                "suitable_for": ["Neubau", "Sanierung", "Alle Gebäudetypen"]
            },
            {
                "type": HeatPumpType.BRINE_WATER.value,
                "label_de": "Sole/Wasser-Wärmepumpe",
                "description_de": "Nutzt Erdwärme über Sonden oder Kollektoren.",
                "pros": ["Hohe Effizienz", "Konstante Wärmequelle", "Leiser Betrieb"],
                "cons": ["Hohe Installationskosten", "Erdarbeiten erforderlich", "Genehmigung nötig"],
                "typical_cop": "4.0-5.5",
                "suitable_for": ["Neubau", "Große Grundstücke"]
            },
            {
                "type": HeatPumpType.WATER_WATER.value,
                "label_de": "Wasser/Wasser-Wärmepumpe",
                "description_de": "Nutzt Grundwasser als Wärmequelle.",
                "pros": ["Höchste Effizienz", "Konstante Temperatur"],
                "cons": ["Wasserrechtliche Genehmigung", "Grundwasser erforderlich", "Hohe Kosten"],
                "typical_cop": "4.5-6.0",
                "suitable_for": ["Gebiete mit Grundwasser"]
            },
            {
                "type": HeatPumpType.AIR_AIR.value,
                "label_de": "Luft/Luft-Wärmepumpe",
                "description_de": "Direkte Lufterwärmung ohne Wasserkreislauf.",
                "pros": ["Günstig", "Einfache Installation", "Auch zum Kühlen"],
                "cons": ["Keine Warmwasserbereitung", "Nur für gut gedämmte Gebäude"],
                "typical_cop": "3.0-4.5",
                "suitable_for": ["Passivhäuser", "Zusatzheizung"]
            }
        ]
    }


@router.get("/categories/list")
async def get_heat_pump_categories():
    """
    Get all available heat pump categories.
    """
    return {
        "categories": [
            {
                "category": HeatPumpCategory.MONOBLOCK.value,
                "label_de": "Monoblock",
                "description_de": "Kompaktgerät für Außenaufstellung"
            },
            {
                "category": HeatPumpCategory.SPLIT.value,
                "label_de": "Split-System",
                "description_de": "Außen- und Inneneinheit getrennt"
            },
            {
                "category": HeatPumpCategory.INDOOR.value,
                "label_de": "Innenaufstellung",
                "description_de": "Komplett im Gebäude installiert"
            },
            {
                "category": HeatPumpCategory.HYBRID.value,
                "label_de": "Hybrid",
                "description_de": "Kombination mit Gas-Brennwertgerät"
            }
        ]
    }


@router.get("/manufacturers")
async def get_manufacturers():
    """
    Get all available manufacturers.
    """
    manufacturers = list(set(m["manufacturer"] for m in SAMPLE_HEAT_PUMPS))
    return {"manufacturers": sorted(manufacturers)}


@router.get("/buffer-storage/calculate")
async def calculate_buffer_storage_recommendation(
    heating_power_kw: float = Query(..., gt=0, le=50),
    hot_water_included: bool = Query(True),
    number_of_residents: int = Query(4, ge=1, le=20)
):
    """
    Calculate buffer storage recommendation.
    """
    # Heating buffer: 20-30 liters per kW
    min_heating_buffer = int(heating_power_kw * 20)
    optimal_heating_buffer = int(heating_power_kw * 25)
    
    # Hot water storage: 50 liters per person
    hot_water_storage = number_of_residents * 50 if hot_water_included else 0
    
    return {
        "heating_buffer": {
            "min_volume_liters": min_heating_buffer,
            "optimal_volume_liters": optimal_heating_buffer,
            "reason": "Reduziert Taktung und erhöht Effizienz"
        },
        "hot_water_storage": {
            "recommended_liters": hot_water_storage,
            "per_person_liters": 50,
            "reason": "Ausreichend Warmwasser für alle Bewohner"
        },
        "combined_recommendation": {
            "total_volume_liters": optimal_heating_buffer + hot_water_storage,
            "note": "Kombispeicher oder separate Speicher möglich"
        }
    }


@router.get("/compare")
async def compare_heat_pumps(
    model_ids: str = Query(..., description="Comma-separated model IDs")
):
    """
    Compare multiple heat pump models.
    """
    ids = [id.strip() for id in model_ids.split(",")]
    models = []
    
    for model_id in ids:
        for model in SAMPLE_HEAT_PUMPS:
            if model["id"] == model_id:
                models.append(model)
                break
    
    if not models:
        raise HTTPException(status_code=404, detail="No models found")
    
    # Calculate comparison metrics
    comparison = {
        "models": [HeatPumpModel(**m) for m in models],
        "comparison": {
            "best_cop": max(m["cop_a7w35"] for m in models),
            "lowest_price": min(m["price_gross_eur"] for m in models),
            "quietest": min(m.get("noise_level_db", 100) for m in models),
            "highest_power": max(m["heating_power_kw"] for m in models)
        }
    }
    
    return comparison


@router.get("/health/check")
async def health_check():
    """
    Health check for heat pump models service.
    """
    return {
        "status": "healthy",
        "service": "heatpump-models",
        "total_models": len(SAMPLE_HEAT_PUMPS),
        "manufacturers": len(set(m["manufacturer"] for m in SAMPLE_HEAT_PUMPS)),
        "timestamp": datetime.now().isoformat()
    }
