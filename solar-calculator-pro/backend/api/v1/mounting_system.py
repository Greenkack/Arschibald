"""
API endpoints for 3D Mounting System Visualization

Provides endpoints for:
- Generating mounting rail visualization
- Creating mounting clamp placement
- Visualizing roof penetrations
- Cable routing visualization
- BOM generation
- Cost calculation

Requirements: 1.3, 6.1
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from ...services.mounting_system_service import (
    MountingSystemService,
    MountingType,
    RailOrientation,
    ClampType,
    PenetrationType
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mounting-system", tags=["Mounting System"])

# Initialize service
mounting_service = MountingSystemService()


# Request/Response Models

class Position3D(BaseModel):
    """3D position coordinates"""
    x: float
    y: float
    z: float


class ModulePosition(BaseModel):
    """Module position data"""
    id: str
    position: Position3D
    width: float = 1.6  # meters
    height: float = 1.0  # meters
    orientation: str = "landscape"


class MountingRailRequest(BaseModel):
    """Request for generating mounting rails"""
    module_positions: List[ModulePosition]
    mounting_type: str = Field(..., description="Type: flat_roof, pitched_roof, ground_mount, facade")
    rail_orientation: str = Field(..., description="Orientation: horizontal, vertical")


class MountingRailResponse(BaseModel):
    """Mounting rail data"""
    id: str
    start_point: Position3D
    end_point: Position3D
    length: float
    orientation: str
    material: str
    profile: str


class MountingClampResponse(BaseModel):
    """Mounting clamp data"""
    id: str
    position: Position3D
    clamp_type: str
    rail_id: str
    module_id: Optional[str]
    torque_spec: float


class RoofPenetrationRequest(BaseModel):
    """Request for generating roof penetrations"""
    rails: List[Dict[str, Any]]
    mounting_type: str
    roof_angle: float = Field(..., ge=0, le=90, description="Roof angle in degrees")


class RoofPenetrationResponse(BaseModel):
    """Roof penetration data"""
    id: str
    position: Position3D
    penetration_type: str
    rail_id: str
    waterproofing: bool
    load_capacity: float


class CableRoutingRequest(BaseModel):
    """Request for generating cable routing"""
    module_positions: List[ModulePosition]
    inverter_position: Position3D
    mounting_type: str


class CableRouteResponse(BaseModel):
    """Cable route data"""
    id: str
    waypoints: List[Position3D]
    cable_type: str
    diameter: float
    length: float


class BOMItemResponse(BaseModel):
    """Bill of Materials item"""
    item_id: str
    description: str
    quantity: int
    unit: str
    unit_price: float
    total_price: float
    category: str
    manufacturer: Optional[str]
    part_number: Optional[str]


class CompleteMountingSystemRequest(BaseModel):
    """Request for complete mounting system visualization"""
    module_positions: List[ModulePosition]
    mounting_type: str = Field(..., description="Type: flat_roof, pitched_roof, ground_mount, facade")
    rail_orientation: str = Field(..., description="Orientation: horizontal, vertical")
    roof_angle: float = Field(..., ge=0, le=90, description="Roof angle in degrees")
    inverter_position: Position3D


class CompleteMountingSystemResponse(BaseModel):
    """Complete mounting system visualization"""
    rails: List[MountingRailResponse]
    clamps: List[MountingClampResponse]
    penetrations: List[RoofPenetrationResponse]
    cable_routes: List[CableRouteResponse]
    bom: List[BOMItemResponse]
    total_cost: float
    mounting_type: str
    summary: Dict[str, Any]


# API Endpoints

@router.post("/rails", response_model=List[MountingRailResponse])
async def generate_mounting_rails(request: MountingRailRequest):
    """
    Generate mounting rails based on module positions
    
    This endpoint creates the mounting rail structure that will support
    the solar modules. Rails are positioned based on module layout and
    mounting system type.
    """
    try:
        logger.info(f"Generating mounting rails for {len(request.module_positions)} modules")
        
        # Convert string enums to enum types
        mounting_type = MountingType(request.mounting_type)
        rail_orientation = RailOrientation(request.rail_orientation)
        
        # Convert module positions to dict format
        module_positions = [
            {
                'id': m.id,
                'position': {'x': m.position.x, 'y': m.position.y, 'z': m.position.z},
                'width': m.width,
                'height': m.height,
                'orientation': m.orientation
            }
            for m in request.module_positions
        ]
        
        # Generate rails
        rails = mounting_service.generate_mounting_rails(
            module_positions,
            mounting_type,
            rail_orientation
        )
        
        # Convert to response format
        response = [
            MountingRailResponse(
                id=rail.id,
                start_point=Position3D(x=rail.start_point[0], y=rail.start_point[1], z=rail.start_point[2]),
                end_point=Position3D(x=rail.end_point[0], y=rail.end_point[1], z=rail.end_point[2]),
                length=rail.length,
                orientation=rail.orientation.value,
                material=rail.material,
                profile=rail.profile
            )
            for rail in rails
        ]
        
        logger.info(f"Successfully generated {len(response)} mounting rails")
        return response
        
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating mounting rails: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating mounting rails: {str(e)}"
        )


@router.post("/clamps", response_model=List[MountingClampResponse])
async def generate_mounting_clamps(
    rails: List[Dict[str, Any]],
    module_positions: List[ModulePosition]
):
    """
    Generate mounting clamps for rails and modules
    
    This endpoint creates the clamp placement that secures modules to rails.
    Clamps are positioned at module edges and categorized by type (end, mid, corner).
    """
    try:
        logger.info(f"Generating mounting clamps for {len(rails)} rails and {len(module_positions)} modules")
        
        # Convert rails to service format
        from ...services.mounting_system_service import MountingRail, RailOrientation
        
        rail_objects = []
        for rail_data in rails:
            rail = MountingRail(
                id=rail_data['id'],
                start_point=tuple(rail_data['start_point'].values()),
                end_point=tuple(rail_data['end_point'].values()),
                length=rail_data['length'],
                orientation=RailOrientation(rail_data['orientation']),
                material=rail_data.get('material', 'aluminum'),
                profile=rail_data.get('profile', 'standard')
            )
            rail_objects.append(rail)
        
        # Convert module positions
        module_positions_dict = [
            {
                'id': m.id,
                'position': {'x': m.position.x, 'y': m.position.y, 'z': m.position.z},
                'width': m.width,
                'height': m.height
            }
            for m in module_positions
        ]
        
        # Generate clamps
        clamps = mounting_service.generate_mounting_clamps(rail_objects, module_positions_dict)
        
        # Convert to response format
        response = [
            MountingClampResponse(
                id=clamp.id,
                position=Position3D(x=clamp.position[0], y=clamp.position[1], z=clamp.position[2]),
                clamp_type=clamp.clamp_type.value,
                rail_id=clamp.rail_id,
                module_id=clamp.module_id,
                torque_spec=clamp.torque_spec
            )
            for clamp in clamps
        ]
        
        logger.info(f"Successfully generated {len(response)} mounting clamps")
        return response
        
    except Exception as e:
        logger.error(f"Error generating mounting clamps: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating mounting clamps: {str(e)}"
        )


@router.post("/penetrations", response_model=List[RoofPenetrationResponse])
async def generate_roof_penetrations(request: RoofPenetrationRequest):
    """
    Generate roof penetration points
    
    This endpoint creates the roof attachment points where the mounting
    system connects to the roof structure. Includes waterproofing details.
    """
    try:
        logger.info(f"Generating roof penetrations for {len(request.rails)} rails")
        
        # Convert rails to service format
        from ...services.mounting_system_service import MountingRail, RailOrientation
        
        rail_objects = []
        for rail_data in request.rails:
            rail = MountingRail(
                id=rail_data['id'],
                start_point=tuple(rail_data['start_point'].values()),
                end_point=tuple(rail_data['end_point'].values()),
                length=rail_data['length'],
                orientation=RailOrientation(rail_data['orientation']),
                material=rail_data.get('material', 'aluminum'),
                profile=rail_data.get('profile', 'standard')
            )
            rail_objects.append(rail)
        
        # Convert mounting type
        mounting_type = MountingType(request.mounting_type)
        
        # Generate penetrations
        penetrations = mounting_service.generate_roof_penetrations(
            rail_objects,
            mounting_type,
            request.roof_angle
        )
        
        # Convert to response format
        response = [
            RoofPenetrationResponse(
                id=pen.id,
                position=Position3D(x=pen.position[0], y=pen.position[1], z=pen.position[2]),
                penetration_type=pen.penetration_type.value,
                rail_id=pen.rail_id,
                waterproofing=pen.waterproofing,
                load_capacity=pen.load_capacity
            )
            for pen in penetrations
        ]
        
        logger.info(f"Successfully generated {len(response)} roof penetrations")
        return response
        
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating roof penetrations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating roof penetrations: {str(e)}"
        )


@router.post("/cable-routing", response_model=List[CableRouteResponse])
async def generate_cable_routing(request: CableRoutingRequest):
    """
    Generate cable routing paths
    
    This endpoint creates the cable routing from modules to inverter,
    including DC strings and AC connection. Calculates cable lengths.
    """
    try:
        logger.info(f"Generating cable routing for {len(request.module_positions)} modules")
        
        # Convert module positions
        module_positions = [
            {
                'id': m.id,
                'position': {'x': m.position.x, 'y': m.position.y, 'z': m.position.z},
                'width': m.width,
                'height': m.height
            }
            for m in request.module_positions
        ]
        
        # Convert inverter position
        inverter_position = (
            request.inverter_position.x,
            request.inverter_position.y,
            request.inverter_position.z
        )
        
        # Convert mounting type
        mounting_type = MountingType(request.mounting_type)
        
        # Generate cable routes
        cable_routes = mounting_service.generate_cable_routing(
            module_positions,
            inverter_position,
            mounting_type
        )
        
        # Convert to response format
        response = [
            CableRouteResponse(
                id=route.id,
                waypoints=[Position3D(x=wp[0], y=wp[1], z=wp[2]) for wp in route.waypoints],
                cable_type=route.cable_type,
                diameter=route.diameter,
                length=route.length
            )
            for route in cable_routes
        ]
        
        logger.info(f"Successfully generated {len(response)} cable routes")
        return response
        
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating cable routing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating cable routing: {str(e)}"
        )


@router.post("/complete", response_model=CompleteMountingSystemResponse)
async def create_complete_mounting_system(request: CompleteMountingSystemRequest):
    """
    Create complete mounting system visualization
    
    This endpoint generates the entire mounting system including:
    - Mounting rails
    - Mounting clamps
    - Roof penetrations
    - Cable routing
    - Bill of Materials (BOM)
    - Total cost calculation
    
    This is the primary endpoint for comprehensive mounting system design.
    """
    try:
        logger.info(f"Creating complete mounting system for {len(request.module_positions)} modules")
        
        # Convert module positions
        module_positions = [
            {
                'id': m.id,
                'position': {'x': m.position.x, 'y': m.position.y, 'z': m.position.z},
                'width': m.width,
                'height': m.height,
                'orientation': m.orientation
            }
            for m in request.module_positions
        ]
        
        # Convert enums
        mounting_type = MountingType(request.mounting_type)
        rail_orientation = RailOrientation(request.rail_orientation)
        
        # Convert inverter position
        inverter_position = (
            request.inverter_position.x,
            request.inverter_position.y,
            request.inverter_position.z
        )
        
        # Create complete visualization
        visualization = mounting_service.create_complete_visualization(
            module_positions,
            mounting_type,
            rail_orientation,
            request.roof_angle,
            inverter_position
        )
        
        # Convert to response format
        response = CompleteMountingSystemResponse(
            rails=[
                MountingRailResponse(
                    id=rail.id,
                    start_point=Position3D(x=rail.start_point[0], y=rail.start_point[1], z=rail.start_point[2]),
                    end_point=Position3D(x=rail.end_point[0], y=rail.end_point[1], z=rail.end_point[2]),
                    length=rail.length,
                    orientation=rail.orientation.value,
                    material=rail.material,
                    profile=rail.profile
                )
                for rail in visualization.rails
            ],
            clamps=[
                MountingClampResponse(
                    id=clamp.id,
                    position=Position3D(x=clamp.position[0], y=clamp.position[1], z=clamp.position[2]),
                    clamp_type=clamp.clamp_type.value,
                    rail_id=clamp.rail_id,
                    module_id=clamp.module_id,
                    torque_spec=clamp.torque_spec
                )
                for clamp in visualization.clamps
            ],
            penetrations=[
                RoofPenetrationResponse(
                    id=pen.id,
                    position=Position3D(x=pen.position[0], y=pen.position[1], z=pen.position[2]),
                    penetration_type=pen.penetration_type.value,
                    rail_id=pen.rail_id,
                    waterproofing=pen.waterproofing,
                    load_capacity=pen.load_capacity
                )
                for pen in visualization.penetrations
            ],
            cable_routes=[
                CableRouteResponse(
                    id=route.id,
                    waypoints=[Position3D(x=wp[0], y=wp[1], z=wp[2]) for wp in route.waypoints],
                    cable_type=route.cable_type,
                    diameter=route.diameter,
                    length=route.length
                )
                for route in visualization.cable_routes
            ],
            bom=[
                BOMItemResponse(
                    item_id=item.item_id,
                    description=item.description,
                    quantity=item.quantity,
                    unit=item.unit,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    category=item.category,
                    manufacturer=item.manufacturer,
                    part_number=item.part_number
                )
                for item in visualization.bom
            ],
            total_cost=visualization.total_cost,
            mounting_type=visualization.mounting_type.value,
            summary={
                'total_rails': len(visualization.rails),
                'total_clamps': len(visualization.clamps),
                'total_penetrations': len(visualization.penetrations),
                'total_cable_routes': len(visualization.cable_routes),
                'total_bom_items': len(visualization.bom),
                'total_rail_length': sum(rail.length for rail in visualization.rails),
                'total_dc_cable_length': sum(
                    route.length for route in visualization.cable_routes 
                    if route.cable_type == "DC"
                ),
                'total_ac_cable_length': sum(
                    route.length for route in visualization.cable_routes 
                    if route.cable_type == "AC"
                )
            }
        )
        
        logger.info(f"Successfully created complete mounting system (Cost: €{visualization.total_cost:,.2f})")
        return response
        
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating complete mounting system: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating complete mounting system: {str(e)}"
        )


@router.get("/component-prices", response_model=Dict[str, float])
async def get_component_prices():
    """
    Get current component prices
    
    Returns the price list for all mounting system components.
    Prices are in EUR.
    """
    try:
        return mounting_service.component_prices
    except Exception as e:
        logger.error(f"Error retrieving component prices: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving component prices: {str(e)}"
        )


@router.get("/mounting-types", response_model=List[str])
async def get_mounting_types():
    """Get available mounting system types"""
    return [mt.value for mt in MountingType]


@router.get("/rail-orientations", response_model=List[str])
async def get_rail_orientations():
    """Get available rail orientation options"""
    return [ro.value for ro in RailOrientation]


@router.get("/clamp-types", response_model=List[str])
async def get_clamp_types():
    """Get available clamp types"""
    return [ct.value for ct in ClampType]


@router.get("/penetration-types", response_model=List[str])
async def get_penetration_types():
    """Get available penetration types"""
    return [pt.value for pt in PenetrationType]
