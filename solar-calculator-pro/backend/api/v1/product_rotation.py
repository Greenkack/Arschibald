"""
Product Rotation API Endpoints

API endpoints for product rotation functionality in multi-PDF generation.
"""

import sys
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.product_rotation_service import (
    get_product_rotation_service,
    RotationStrategy
)

router = APIRouter(prefix="/product-rotation", tags=["product-rotation"])


# ==================== Request/Response Models ====================

class RotationStateResponse(BaseModel):
    """Rotation state response"""
    used_brands: Dict[str, List[str]]
    used_products: Dict[str, List[int]]
    total_used_brands: int
    total_used_products: int


class SelectProductRequest(BaseModel):
    """Request to select a rotated product"""
    category: str = Field(..., description="Product category")
    strategy: str = Field(
        default=RotationStrategy.AVOID_BOTH.value,
        description="Rotation strategy"
    )
    reference_product_id: Optional[int] = Field(
        None,
        description="Reference product ID for price comparison"
    )
    price_tolerance: float = Field(
        default=0.2,
        description="Price tolerance (0.2 = ±20%)"
    )
    required_specs: Optional[Dict[str, Any]] = Field(
        None,
        description="Required specifications"
    )


class SelectProductSetRequest(BaseModel):
    """Request to select a product set"""
    categories: List[str] = Field(..., description="Product categories")
    strategy: str = Field(
        default=RotationStrategy.AVOID_BOTH.value,
        description="Rotation strategy"
    )
    reference_products: Optional[Dict[str, int]] = Field(
        None,
        description="Reference products per category"
    )
    price_tolerance: float = Field(
        default=0.2,
        description="Price tolerance"
    )
    required_specs: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Required specifications per category"
    )


class CompatibilityCheckRequest(BaseModel):
    """Request to check product compatibility"""
    product_set: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Product set to check"
    )


class CompatibilityCheckResponse(BaseModel):
    """Compatibility check response"""
    is_compatible: bool
    has_warnings: bool
    issues: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    checked_at: str


# ==================== API Endpoints ====================

@router.get("/state", response_model=RotationStateResponse)
async def get_rotation_state():
    """
    Get current rotation state.
    
    Returns the current state of used brands and products.
    """
    try:
        service = get_product_rotation_service()
        state = service.get_rotation_state()
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_rotation_state():
    """
    Reset rotation state.
    
    Clears all tracked brands and products.
    """
    try:
        service = get_product_rotation_service()
        service.reset_rotation_state()
        return {"message": "Rotation state reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select-product")
async def select_rotated_product(request: SelectProductRequest):
    """
    Select a rotated product.
    
    Selects a product with rotation logic applied to avoid
    previously used brands/products.
    """
    try:
        service = get_product_rotation_service()
        
        product = service.select_rotated_product(
            category=request.category,
            strategy=request.strategy,
            reference_product_id=request.reference_product_id,
            price_tolerance=request.price_tolerance,
            required_specs=request.required_specs
        )
        
        if product is None:
            raise HTTPException(
                status_code=404,
                detail=f"No suitable product found in category '{request.category}'"
            )
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select-product-set")
async def select_product_set(request: SelectProductSetRequest):
    """
    Select a complete product set.
    
    Selects products across multiple categories with rotation logic.
    """
    try:
        service = get_product_rotation_service()
        
        product_set = service.select_product_set(
            categories=request.categories,
            strategy=request.strategy,
            reference_products=request.reference_products,
            price_tolerance=request.price_tolerance,
            required_specs=request.required_specs
        )
        
        return product_set
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-compatibility", response_model=CompatibilityCheckResponse)
async def check_product_compatibility(request: CompatibilityCheckRequest):
    """
    Check product compatibility.
    
    Checks if products in a set are compatible with each other.
    """
    try:
        service = get_product_rotation_service()
        
        report = service.check_product_compatibility(request.product_set)
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def get_rotation_strategies():
    """
    Get available rotation strategies.
    
    Returns list of available rotation strategies with descriptions.
    """
    strategies = [
        {
            "value": RotationStrategy.AVOID_BRANDS.value,
            "label": "Avoid Brands",
            "description": "Avoid previously used brands"
        },
        {
            "value": RotationStrategy.AVOID_PRODUCTS.value,
            "label": "Avoid Products",
            "description": "Avoid previously used products"
        },
        {
            "value": RotationStrategy.AVOID_BOTH.value,
            "label": "Avoid Both",
            "description": "Avoid both brands and products"
        },
        {
            "value": RotationStrategy.PRICE_SIMILAR.value,
            "label": "Price Similar",
            "description": "Select products with similar price"
        },
        {
            "value": RotationStrategy.PRICE_HIGHER.value,
            "label": "Price Higher",
            "description": "Select products with higher price"
        },
        {
            "value": RotationStrategy.PRICE_LOWER.value,
            "label": "Price Lower",
            "description": "Select products with lower price"
        }
    ]
    
    return {"strategies": strategies}


@router.get("/categories")
async def get_product_categories():
    """
    Get available product categories.
    
    Returns list of product categories for rotation.
    """
    from backend.services.product_rotation_service import ProductCategory
    
    categories = [
        {
            "value": ProductCategory.PV_MODULE.value,
            "label": "PV Module",
            "description": "Solar PV modules"
        },
        {
            "value": ProductCategory.INVERTER.value,
            "label": "Inverter",
            "description": "Solar inverters"
        },
        {
            "value": ProductCategory.BATTERY.value,
            "label": "Battery",
            "description": "Battery storage systems"
        },
        {
            "value": ProductCategory.MOUNTING.value,
            "label": "Mounting",
            "description": "Mounting systems"
        },
        {
            "value": ProductCategory.CABLE.value,
            "label": "Cable",
            "description": "Cables and wiring"
        },
        {
            "value": ProductCategory.ACCESSORY.value,
            "label": "Accessory",
            "description": "Accessories"
        }
    ]
    
    return {"categories": categories}
