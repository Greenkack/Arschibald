"""
Heat Pump Product API Endpoints

This module provides REST API endpoints for heat pump product management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from solar-calculator-pro.backend.models.heatpump_product_schemas import (
    HeatPumpSpecification,
    HeatPumpFilterRequest,
    HeatPumpFilterResponse,
    HeatPumpComparisonRequest,
    HeatPumpComparisonResponse,
    HeatPumpRecommendationRequest,
    HeatPumpRecommendationResponse,
    HeatPumpAvailability,
    HeatPumpAvailabilityUpdate,
    HeatPumpBulkAvailabilityRequest,
    HeatPumpBulkAvailabilityResponse,
    HeatPumpType)
from solar-calculator-pro.backend.services.heatpump_product_service import heatpump_product_service


router = APIRouter(prefix="/heatpump-products", tags=["Heat Pump Products"])


@router.get("/", response_model=List[HeatPumpSpecification])
async def get_all_products():
    """Get all heat pump products"""
    return heatpump_product_service.get_all_products()


@router.get("/{product_id}", response_model=HeatPumpSpecification)
async def get_product(product_id: str):
    """Get a specific heat pump product by ID"""
    product = heatpump_product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


@router.get("/manufacturer/{manufacturer}", response_model=List[HeatPumpSpecification])
async def get_products_by_manufacturer(manufacturer: str):
    """Get all products from a specific manufacturer"""
    return heatpump_product_service.get_products_by_manufacturer(manufacturer)


@router.get("/type/{heatpump_type}", response_model=List[HeatPumpSpecification])
async def get_products_by_type(heatpump_type: HeatPumpType):
    """Get all products of a specific type"""
    return heatpump_product_service.get_products_by_type(heatpump_type)


@router.post("/filter", response_model=HeatPumpFilterResponse)
async def filter_products(filter_request: HeatPumpFilterRequest):
    """
    Filter heat pump products based on various criteria
    
    Supports filtering by:
    - Manufacturers
    - Heat pump types
    - Power range
    - Efficiency (COP, SCOP)
    - Temperature requirements
    - Features (smart grid, internet, inverter)
    - Price range
    - Availability
    
    Results can be sorted and paginated.
    """
    return heatpump_product_service.filter_products(filter_request)


@router.post("/compare", response_model=HeatPumpComparisonResponse)
async def compare_products(comparison_request: HeatPumpComparisonRequest):
    """
    Compare multiple heat pump products
    
    Compares products across multiple criteria:
    - Efficiency (COP, SCOP, EER, SEER)
    - Power capabilities
    - Cost (base price, installation, total)
    - Features (smart grid, connectivity, etc.)
    - Temperature range
    
    Returns comparison matrix and identifies best in each category.
    """
    try:
        return heatpump_product_service.compare_products(comparison_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recommend", response_model=HeatPumpRecommendationResponse)
async def recommend_products(recommendation_request: HeatPumpRecommendationRequest):
    """
    Get intelligent heat pump recommendations
    
    Analyzes building characteristics and requirements to recommend
    the most suitable heat pump products.
    
    Considers:
    - Building size and insulation
    - Climate and temperature requirements
    - Heating and cooling needs
    - Budget constraints
    - Feature preferences
    - Energy efficiency goals
    
    Returns ranked recommendations with suitability scores,
    economic analysis, and environmental impact.
    """
    return heatpump_product_service.recommend_products(recommendation_request)


@router.get("/availability/{product_id}", response_model=HeatPumpAvailability)
async def get_availability(product_id: str):
    """Get availability information for a specific product"""
    availability = heatpump_product_service.get_availability(product_id)
    if not availability:
        raise HTTPException(
            status_code=404,
            detail=f"Availability information for product {product_id} not found"
        )
    return availability


@router.put("/availability", response_model=HeatPumpAvailability)
async def update_availability(availability_update: HeatPumpAvailabilityUpdate):
    """Update product availability information"""
    try:
        return heatpump_product_service.update_availability(availability_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/availability/bulk", response_model=HeatPumpBulkAvailabilityResponse)
async def check_bulk_availability(bulk_request: HeatPumpBulkAvailabilityRequest):
    """Check availability for multiple products at once"""
    return heatpump_product_service.check_bulk_availability(bulk_request)


@router.get("/alternatives/{product_id}", response_model=List[str])
async def get_alternatives(
    product_id: str,
    max_alternatives: int = Query(3, ge=1, le=10, description="Maximum number of alternatives")
):
    """
    Get alternative product suggestions
    
    When a product is unavailable, this endpoint suggests similar
    alternatives based on:
    - Same heat pump type
    - Similar power output
    - Similar efficiency
    - Similar price range
    """
    alternatives = heatpump_product_service.suggest_alternatives(product_id, max_alternatives)
    if not alternatives:
        raise HTTPException(
            status_code=404,
            detail=f"No alternatives found for product {product_id}"
        )
    return alternatives


@router.get("/manufacturers", response_model=List[str])
async def get_manufacturers():
    """Get list of all manufacturers"""
    products = heatpump_product_service.get_all_products()
    manufacturers = sorted(set(p.manufacturer for p in products))
    return manufacturers


@router.get("/types", response_model=List[str])
async def get_types():
    """Get list of all heat pump types"""
    return [t.value for t in HeatPumpType]


@router.get("/statistics", response_model=dict)
async def get_statistics():
    """Get statistics about the heat pump product database"""
    products = heatpump_product_service.get_all_products()
    
    available_products = [p for p in products if p.available]
    products_with_price = [p for p in products if p.base_price is not None]
    products_with_scop = [p for p in products if p.scop is not None]
    
    return {
        "total_products": len(products),
        "available_products": len(available_products),
        "manufacturers_count": len(set(p.manufacturer for p in products)),
        "types_count": len(set(p.heatpump_type for p in products)),
        "price_range": {
            "min": min((p.base_price for p in products_with_price), default=None),
            "max": max((p.base_price for p in products_with_price), default=None),
            "average": sum(p.base_price for p in products_with_price) / len(products_with_price) if products_with_price else None,
        },
        "power_range": {
            "min": min(min(p.heating_power_kw) for p in products),
            "max": max(max(p.heating_power_kw) for p in products),
        },
        "efficiency": {
            "scop_min": min((p.scop for p in products_with_scop), default=None),
            "scop_max": max((p.scop for p in products_with_scop), default=None),
            "scop_average": sum(p.scop for p in products_with_scop) / len(products_with_scop) if products_with_scop else None,
        },
        "features": {
            "smart_grid_ready": sum(1 for p in products if p.smart_grid_ready),
            "internet_connectivity": sum(1 for p in products if p.internet_connectivity),
            "inverter_technology": sum(1 for p in products if p.inverter_technology),
            "modulating": sum(1 for p in products if p.modulating),
        },
    }
