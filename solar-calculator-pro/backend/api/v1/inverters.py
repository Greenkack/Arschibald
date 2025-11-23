"""
Inverter Management API Endpoints

Provides REST API endpoints for solar inverter management including:
- Inverter selection
- Sizing calculations
- Compatibility checks
- Multi-inverter configurations
- Monitoring integration

Requirements: 1.3, 6.1
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import logging

# Import the inverter service
try:
    from services.inverter_service import InverterService, InverterSpecs
except ImportError:
    from backend.services.inverter_service import InverterService, InverterSpecs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inverters", tags=["inverters"])


# Request/Response Models
class InverterSelectionRequest(BaseModel):
    """Request model for inverter selection"""
    pv_power_kwp: float = Field(..., gt=0, description="PV system power in kWp")
    system_voltage: float = Field(default=400.0, description="System voltage in V")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="User preferences")


class InverterSizingRequest(BaseModel):
    """Request model for inverter sizing calculations"""
    pv_power_kwp: float = Field(..., gt=0, description="PV system power in kWp")
    module_voltage: float = Field(..., gt=0, description="Module voltage (Vmp) in V")
    module_current: float = Field(..., gt=0, description="Module current (Imp) in A")
    string_configuration: Dict[str, Any] = Field(..., description="String layout configuration")


class CompatibilityCheckRequest(BaseModel):
    """Request model for compatibility check"""
    inverter_id: int = Field(..., description="Inverter product ID")
    pv_system: Dict[str, Any] = Field(..., description="PV system specifications")


class MultiInverterRequest(BaseModel):
    """Request model for multi-inverter configuration"""
    pv_power_kwp: float = Field(..., gt=0, description="Total PV power in kWp")
    system_layout: Dict[str, Any] = Field(..., description="System layout with roof sections")


class MonitoringIntegrationRequest(BaseModel):
    """Request model for monitoring integration"""
    inverter_id: int = Field(..., description="Inverter product ID")
    monitoring_config: Dict[str, Any] = Field(..., description="Monitoring configuration")


class InverterResponse(BaseModel):
    """Response model for inverter data"""
    id: Optional[int]
    model_name: str
    manufacturer: str
    power_kw: float
    efficiency_percent: float
    max_dc_voltage: float
    mppt_count: int
    max_dc_current: float
    price_netto: float
    additional_cost_netto: float
    warranty_years: int
    weight_kg: float
    description: str
    technology: str
    features: List[str]


class InverterSelectionResponse(BaseModel):
    """Response model for inverter selection"""
    selected_inverter: InverterResponse
    selection_score: float
    sizing_ratio: float
    alternatives: List[Dict[str, Any]]
    selection_reasoning: str


class InverterSizingResponse(BaseModel):
    """Response model for inverter sizing"""
    required_power_kw: float
    recommended_power_range: Dict[str, float]
    dc_specifications: Dict[str, float]
    mppt_configuration: Dict[str, Any]
    sizing_ratio: Dict[str, Any]
    safety_margins: Dict[str, int]


class CompatibilityCheckResponse(BaseModel):
    """Response model for compatibility check"""
    is_compatible: bool
    compatibility_score: float
    checks: List[Dict[str, str]]
    warnings: List[str]
    recommendation: str


class MultiInverterResponse(BaseModel):
    """Response model for multi-inverter configuration"""
    configuration_type: str
    inverter_count: int
    inverters: List[InverterResponse]
    total_power_kw: float
    power_distribution: Optional[List[Dict[str, Any]]] = None
    sizing_ratio: Optional[float] = None
    reasoning: str


class MonitoringIntegrationResponse(BaseModel):
    """Response model for monitoring integration"""
    monitoring_supported: bool
    inverter_id: Optional[int] = None
    inverter_model: Optional[str] = None
    manufacturer: Optional[str] = None
    communication_protocol: Optional[str] = None
    data_points: Optional[List[str]] = None
    update_interval_seconds: Optional[int] = None
    data_retention_days: Optional[int] = None
    alerts: Optional[List[Dict[str, Any]]] = None
    api_endpoints: Optional[Dict[str, str]] = None
    message: Optional[str] = None
    alternative: Optional[str] = None


# Dependency to get inverter service
def get_inverter_service() -> InverterService:
    """Get inverter service instance"""
    # In production, this would get the database connection
    return InverterService()


@router.get("/", response_model=List[InverterResponse])
async def list_inverters(
    manufacturer: Optional[str] = Query(None, description="Filter by manufacturer"),
    min_power_kw: Optional[float] = Query(None, description="Minimum power in kW"),
    max_power_kw: Optional[float] = Query(None, description="Maximum power in kW"),
    service: InverterService = Depends(get_inverter_service)
):
    """
    List available inverters with optional filtering
    
    - **manufacturer**: Filter by manufacturer name
    - **min_power_kw**: Minimum inverter power
    - **max_power_kw**: Maximum inverter power
    """
    try:
        inverters = service._get_available_inverters()
        
        # Apply filters
        if manufacturer:
            inverters = [
                inv for inv in inverters
                if inv.get('manufacturer', '').lower() == manufacturer.lower()
            ]
        
        if min_power_kw is not None:
            inverters = [
                inv for inv in inverters
                if inv.get('power_kw', 0) >= min_power_kw
            ]
        
        if max_power_kw is not None:
            inverters = [
                inv for inv in inverters
                if inv.get('power_kw', 0) <= max_power_kw
            ]
        
        # Extract and return inverter data
        result = [service.extract_inverter_data(inv) for inv in inverters]
        
        logger.info(f"Listed {len(result)} inverters")
        return result
        
    except Exception as e:
        logger.error(f"Error listing inverters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{inverter_id}", response_model=InverterResponse)
async def get_inverter(
    inverter_id: int,
    service: InverterService = Depends(get_inverter_service)
):
    """
    Get detailed information about a specific inverter
    
    - **inverter_id**: Inverter product ID
    """
    try:
        inverters = service._get_available_inverters()
        inverter = next((inv for inv in inverters if inv.get('id') == inverter_id), None)
        
        if not inverter:
            raise HTTPException(status_code=404, detail=f"Inverter {inverter_id} not found")
        
        result = service.extract_inverter_data(inverter)
        logger.info(f"Retrieved inverter {inverter_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inverter {inverter_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select", response_model=InverterSelectionResponse)
async def select_inverter(
    request: InverterSelectionRequest,
    service: InverterService = Depends(get_inverter_service)
):
    """
    Select optimal inverter for a PV system
    
    Analyzes system requirements and selects the best matching inverter
    based on power, efficiency, and user preferences.
    """
    try:
        result = service.select_inverter(
            pv_power_kwp=request.pv_power_kwp,
            system_voltage=request.system_voltage,
            preferences=request.preferences
        )
        
        logger.info(f"Selected inverter for {request.pv_power_kwp}kWp system")
        return result
        
    except Exception as e:
        logger.error(f"Error selecting inverter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sizing", response_model=InverterSizingResponse)
async def calculate_sizing(
    request: InverterSizingRequest,
    service: InverterService = Depends(get_inverter_service)
):
    """
    Calculate detailed inverter sizing requirements
    
    Provides comprehensive sizing calculations including voltage, current,
    MPPT configuration, and safety margins.
    """
    try:
        result = service.calculate_inverter_sizing(
            pv_power_kwp=request.pv_power_kwp,
            module_voltage=request.module_voltage,
            module_current=request.module_current,
            string_configuration=request.string_configuration
        )
        
        logger.info(f"Calculated sizing for {request.pv_power_kwp}kWp system")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating sizing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compatibility", response_model=CompatibilityCheckResponse)
async def check_compatibility(
    request: CompatibilityCheckRequest,
    service: InverterService = Depends(get_inverter_service)
):
    """
    Check inverter compatibility with PV system
    
    Performs comprehensive compatibility checks including power, voltage,
    current, and MPPT configuration.
    """
    try:
        # Get inverter data
        inverters = service._get_available_inverters()
        inverter = next(
            (inv for inv in inverters if inv.get('id') == request.inverter_id),
            None
        )
        
        if not inverter:
            raise HTTPException(
                status_code=404,
                detail=f"Inverter {request.inverter_id} not found"
            )
        
        result = service.check_inverter_compatibility(
            inverter=inverter,
            pv_system=request.pv_system
        )
        
        logger.info(f"Checked compatibility for inverter {request.inverter_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking compatibility: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multi-inverter", response_model=MultiInverterResponse)
async def create_multi_inverter_config(
    request: MultiInverterRequest,
    service: InverterService = Depends(get_inverter_service)
):
    """
    Create multi-inverter configuration for large systems
    
    Designs optimal multi-inverter setup for systems with multiple roof
    sections or large power requirements.
    """
    try:
        result = service.create_multi_inverter_configuration(
            pv_power_kwp=request.pv_power_kwp,
            system_layout=request.system_layout
        )
        
        logger.info(
            f"Created multi-inverter config for {request.pv_power_kwp}kWp system"
        )
        return result
        
    except Exception as e:
        logger.error(f"Error creating multi-inverter config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring", response_model=MonitoringIntegrationResponse)
async def integrate_monitoring(
    request: MonitoringIntegrationRequest,
    service: InverterService = Depends(get_inverter_service)
):
    """
    Configure monitoring integration for inverter
    
    Sets up monitoring system integration including data points,
    update intervals, and alert configuration.
    """
    try:
        # Get inverter data
        inverters = service._get_available_inverters()
        inverter = next(
            (inv for inv in inverters if inv.get('id') == request.inverter_id),
            None
        )
        
        if not inverter:
            raise HTTPException(
                status_code=404,
                detail=f"Inverter {request.inverter_id} not found"
            )
        
        result = service.integrate_monitoring(
            inverter=inverter,
            monitoring_config=request.monitoring_config
        )
        
        logger.info(f"Configured monitoring for inverter {request.inverter_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error integrating monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/manufacturers", response_model=List[str])
async def list_manufacturers(
    service: InverterService = Depends(get_inverter_service)
):
    """
    List all available inverter manufacturers
    """
    try:
        inverters = service._get_available_inverters()
        manufacturers = list(set(
            inv.get('manufacturer', inv.get('brand', ''))
            for inv in inverters
            if inv.get('manufacturer') or inv.get('brand')
        ))
        manufacturers.sort()
        
        logger.info(f"Listed {len(manufacturers)} manufacturers")
        return manufacturers
        
    except Exception as e:
        logger.error(f"Error listing manufacturers: {e}")
        raise HTTPException(status_code=500, detail=str(e))
