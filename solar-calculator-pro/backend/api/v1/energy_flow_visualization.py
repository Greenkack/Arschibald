"""
360° Energy Flow Visualization API

Provides REST API for energy flow visualization:
- Animated 360° energy flow visualization (GIF)
- Heat pump components (outdoor unit, indoor unit, heating circuits)
- Compare old system (oil/gas) vs. new heat pump
- Interactive energy flow diagram
- Exportable visualization for presentations

Requirements: funktionen.txt - "360°-Visualisierung der Energieflüsse"
Task: 259. 360° Energy Flow Visualization
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

router = APIRouter(prefix="/visualization/energy-flow", tags=["Energy Flow Visualization"])


# ==================== Enums ====================

class SystemType(str, Enum):
    """System type for visualization"""
    HEAT_PUMP = "heat_pump"
    OIL_HEATING = "oil_heating"
    GAS_HEATING = "gas_heating"
    COMBINED_PV_HP = "combined_pv_hp"


class AnimationStyle(str, Enum):
    """Animation style"""
    FLOW = "flow"
    PULSE = "pulse"
    GRADIENT = "gradient"


# ==================== Pydantic Models ====================

class EnergyFlowRequest(BaseModel):
    """Request for energy flow visualization"""
    system_type: SystemType = Field(default=SystemType.HEAT_PUMP)
    heating_power_kw: float = Field(default=10.0, gt=0)
    electricity_consumption_kw: float = Field(default=2.5, gt=0)
    cop: float = Field(default=4.0, ge=2.0, le=6.0)
    outdoor_temp_c: float = Field(default=7.0, ge=-20, le=40)
    flow_temp_c: float = Field(default=35.0, ge=25, le=65)
    return_temp_c: float = Field(default=28.0, ge=20, le=55)
    pv_power_kw: Optional[float] = Field(None, ge=0)
    battery_power_kw: Optional[float] = Field(None, ge=0)


class EnergyFlowNode(BaseModel):
    """Node in energy flow diagram"""
    id: str
    label: str
    type: str
    x: float
    y: float
    power_kw: Optional[float] = None
    temperature_c: Optional[float] = None
    icon: str
    color: str


class EnergyFlowEdge(BaseModel):
    """Edge in energy flow diagram"""
    id: str
    source: str
    target: str
    label: str
    power_kw: float
    flow_type: str
    color: str
    animated: bool = True


class EnergyFlowDiagram(BaseModel):
    """Complete energy flow diagram"""
    nodes: List[EnergyFlowNode]
    edges: List[EnergyFlowEdge]
    total_input_kw: float
    total_output_kw: float
    efficiency_percent: float
    cop: float
    animation_config: Dict[str, Any]


class ComparisonResult(BaseModel):
    """Comparison between old and new system"""
    old_system: Dict[str, Any]
    new_system: Dict[str, Any]
    savings: Dict[str, Any]
    environmental_impact: Dict[str, Any]


# ==================== Helper Functions ====================

def create_heat_pump_nodes(request: EnergyFlowRequest) -> List[EnergyFlowNode]:
    """Create nodes for heat pump visualization"""
    nodes = [
        EnergyFlowNode(
            id="outdoor_air",
            label="Außenluft",
            type="source",
            x=0, y=50,
            temperature_c=request.outdoor_temp_c,
            icon="",
            color="#87CEEB"
        ),
        EnergyFlowNode(
            id="outdoor_unit",
            label="Außengerät",
            type="component",
            x=25, y=50,
            power_kw=request.heating_power_kw * 0.75,
            icon="",
            color="#4A90D9"
        ),
        EnergyFlowNode(
            id="compressor",
            label="Verdichter",
            type="component",
            x=50, y=50,
            power_kw=request.electricity_consumption_kw,
            icon="",
            color="#FFD700"
        ),
        EnergyFlowNode(
            id="indoor_unit",
            label="Innengerät",
            type="component",
            x=75, y=50,
            power_kw=request.heating_power_kw,
            temperature_c=request.flow_temp_c,
            icon="",
            color="#FF6B6B"
        ),
        EnergyFlowNode(
            id="heating_circuit",
            label="Heizkreis",
            type="output",
            x=100, y=50,
            temperature_c=request.flow_temp_c,
            icon="",
            color="#FF4500"
        ),
        EnergyFlowNode(
            id="grid",
            label="Stromnetz",
            type="source",
            x=50, y=0,
            power_kw=request.electricity_consumption_kw,
            icon="",
            color="#32CD32"
        )
    ]
    
    # Add PV if present
    if request.pv_power_kw and request.pv_power_kw > 0:
        nodes.append(EnergyFlowNode(
            id="pv_system",
            label="PV-Anlage",
            type="source",
            x=25, y=0,
            power_kw=request.pv_power_kw,
            icon="",
            color="#FFD700"
        ))
    
    # Add battery if present
    if request.battery_power_kw and request.battery_power_kw > 0:
        nodes.append(EnergyFlowNode(
            id="battery",
            label="Batterie",
            type="storage",
            x=35, y=25,
            power_kw=request.battery_power_kw,
            icon="",
            color="#9370DB"
        ))
    
    return nodes


def create_heat_pump_edges(request: EnergyFlowRequest) -> List[EnergyFlowEdge]:
    """Create edges for heat pump visualization"""
    env_heat = request.heating_power_kw - request.electricity_consumption_kw
    
    edges = [
        EnergyFlowEdge(
            id="air_to_outdoor",
            source="outdoor_air",
            target="outdoor_unit",
            label=f"Umweltwärme",
            power_kw=env_heat,
            flow_type="heat",
            color="#87CEEB"
        ),
        EnergyFlowEdge(
            id="outdoor_to_compressor",
            source="outdoor_unit",
            target="compressor",
            label="Kältemittel",
            power_kw=env_heat,
            flow_type="refrigerant",
            color="#4A90D9"
        ),
        EnergyFlowEdge(
            id="grid_to_compressor",
            source="grid",
            target="compressor",
            label=f"{request.electricity_consumption_kw:.1f} kW",
            power_kw=request.electricity_consumption_kw,
            flow_type="electricity",
            color="#32CD32"
        ),
        EnergyFlowEdge(
            id="compressor_to_indoor",
            source="compressor",
            target="indoor_unit",
            label="Heißgas",
            power_kw=request.heating_power_kw,
            flow_type="refrigerant",
            color="#FF6B6B"
        ),
        EnergyFlowEdge(
            id="indoor_to_heating",
            source="indoor_unit",
            target="heating_circuit",
            label=f"{request.heating_power_kw:.1f} kW",
            power_kw=request.heating_power_kw,
            flow_type="heat",
            color="#FF4500"
        )
    ]
    
    # Add PV edge if present
    if request.pv_power_kw and request.pv_power_kw > 0:
        edges.append(EnergyFlowEdge(
            id="pv_to_compressor",
            source="pv_system",
            target="compressor",
            label=f"{min(request.pv_power_kw, request.electricity_consumption_kw):.1f} kW",
            power_kw=min(request.pv_power_kw, request.electricity_consumption_kw),
            flow_type="electricity",
            color="#FFD700"
        ))
    
    return edges


# ==================== API Endpoints ====================

@router.post("/diagram", response_model=EnergyFlowDiagram)
async def create_energy_flow_diagram(request: EnergyFlowRequest):
    """
    Create energy flow diagram for visualization.
    """
    nodes = create_heat_pump_nodes(request)
    edges = create_heat_pump_edges(request)
    
    env_heat = request.heating_power_kw - request.electricity_consumption_kw
    efficiency = (request.heating_power_kw / request.electricity_consumption_kw) * 100
    
    return EnergyFlowDiagram(
        nodes=nodes,
        edges=edges,
        total_input_kw=request.electricity_consumption_kw + env_heat,
        total_output_kw=request.heating_power_kw,
        efficiency_percent=round(efficiency, 1),
        cop=request.cop,
        animation_config={
            "style": "flow",
            "speed": 1.0,
            "particle_count": 20,
            "colors": {
                "electricity": "#32CD32",
                "heat": "#FF4500",
                "refrigerant": "#4A90D9"
            }
        }
    )


@router.get("/compare")
async def compare_systems(
    heating_demand_kwh: float = Query(..., gt=0),
    old_system: str = Query("gas", regex="^(gas|oil)$"),
    jaz: float = Query(4.0, ge=2.0, le=6.0),
    electricity_price: float = Query(0.30),
    gas_price: float = Query(0.10),
    oil_price: float = Query(0.12)
):
    """
    Compare old heating system with new heat pump.
    """
    # Old system calculations
    old_efficiency = 0.90 if old_system == "gas" else 0.85
    old_fuel_consumption = heating_demand_kwh / old_efficiency
    old_fuel_price = gas_price if old_system == "gas" else oil_price
    old_cost = old_fuel_consumption * old_fuel_price
    old_co2 = old_fuel_consumption * (0.201 if old_system == "gas" else 0.266)
    
    # New system (heat pump)
    hp_electricity = heating_demand_kwh / jaz
    new_cost = hp_electricity * electricity_price
    new_co2 = hp_electricity * 0.420  # German grid mix
    
    return ComparisonResult(
        old_system={
            "type": old_system,
            "fuel_consumption_kwh": round(old_fuel_consumption, 0),
            "annual_cost_eur": round(old_cost, 2),
            "co2_emissions_kg": round(old_co2, 0),
            "efficiency_percent": old_efficiency * 100
        },
        new_system={
            "type": "heat_pump",
            "electricity_consumption_kwh": round(hp_electricity, 0),
            "annual_cost_eur": round(new_cost, 2),
            "co2_emissions_kg": round(new_co2, 0),
            "cop": jaz
        },
        savings={
            "annual_eur": round(old_cost - new_cost, 2),
            "percent": round((old_cost - new_cost) / old_cost * 100, 1),
            "co2_kg": round(old_co2 - new_co2, 0)
        },
        environmental_impact={
            "co2_reduction_percent": round((old_co2 - new_co2) / old_co2 * 100, 1),
            "trees_equivalent": round((old_co2 - new_co2) / 20, 0),  # ~20kg CO2 per tree/year
            "car_km_equivalent": round((old_co2 - new_co2) / 0.12, 0)  # ~120g CO2/km
        }
    )


@router.get("/animation-config")
async def get_animation_config(style: AnimationStyle = Query(AnimationStyle.FLOW)):
    """
    Get animation configuration for energy flow visualization.
    """
    configs = {
        AnimationStyle.FLOW: {
            "type": "flow",
            "particle_speed": 2.0,
            "particle_size": 8,
            "particle_count": 30,
            "trail_length": 10,
            "colors": {
                "electricity": {"start": "#32CD32", "end": "#228B22"},
                "heat": {"start": "#FF4500", "end": "#FF6347"},
                "refrigerant": {"start": "#4A90D9", "end": "#1E90FF"}
            }
        },
        AnimationStyle.PULSE: {
            "type": "pulse",
            "pulse_speed": 1.5,
            "pulse_intensity": 0.3,
            "glow_radius": 20
        },
        AnimationStyle.GRADIENT: {
            "type": "gradient",
            "gradient_speed": 1.0,
            "gradient_steps": 10
        }
    }
    
    return {
        "style": style.value,
        "config": configs.get(style, configs[AnimationStyle.FLOW]),
        "supported_styles": [s.value for s in AnimationStyle]
    }


@router.get("/export-config")
async def get_export_config():
    """
    Get configuration for exporting visualization.
    """
    return {
        "formats": [
            {"format": "gif", "label": "Animiertes GIF", "recommended": True},
            {"format": "mp4", "label": "Video (MP4)", "recommended": False},
            {"format": "svg", "label": "Vektorgrafik (SVG)", "recommended": False},
            {"format": "png", "label": "Standbild (PNG)", "recommended": False}
        ],
        "resolutions": [
            {"width": 800, "height": 600, "label": "Standard"},
            {"width": 1280, "height": 720, "label": "HD"},
            {"width": 1920, "height": 1080, "label": "Full HD"}
        ],
        "animation_duration_seconds": [3, 5, 10, 15],
        "frame_rate": 30
    }


@router.get("/health/check")
async def health_check():
    """Health check for energy flow visualization service."""
    return {
        "status": "healthy",
        "service": "energy-flow-visualization",
        "timestamp": datetime.now().isoformat()
    }
