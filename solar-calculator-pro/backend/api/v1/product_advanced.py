"""
Product Advanced API Endpoints

API endpoints for advanced product management features.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from backend.services.product_advanced_service import get_product_advanced_service


router = APIRouter(prefix="/product-advanced", tags=["product-advanced"])


# ==================== Request/Response Models ====================

class ProductLifecycleUpdate(BaseModel):
    """Product lifecycle update request"""
    status: str = Field(..., description="New lifecycle status")
    notes: Optional[str] = Field(None, description="Notes about status change")


class ProductVersionCreate(BaseModel):
    """Product version creation request"""
    changes: Dict[str, Any] = Field(..., description="Changes to apply")
    version_notes: Optional[str] = Field(None, description="Version notes")


class ProductComparisonRequest(BaseModel):
    """Product comparison request"""
    product_ids: List[int] = Field(..., min_items=2, description="Product IDs to compare")
    comparison_attributes: Optional[List[str]] = Field(None, description="Attributes to compare")


class ProductRecommendationRequest(BaseModel):
    """Product recommendation request"""
    calculation_context: Dict[str, Any] = Field(..., description="Calculation context")
    category: Optional[str] = Field(None, description="Product category filter")
    limit: int = Field(5, ge=1, le=20, description="Maximum recommendations")


class ProductAvailabilityUpdate(BaseModel):
    """Product availability update request"""
    stock_quantity: Optional[int] = Field(None, ge=0, description="Stock quantity")
    reorder_point: Optional[int] = Field(None, ge=0, description="Reorder point")
    estimated_restock_date: Optional[str] = Field(None, description="Estimated restock date")


class ProductSupplierCreate(BaseModel):
    """Product supplier creation request"""
    supplier_name: str = Field(..., description="Supplier name")
    supplier_sku: Optional[str] = Field(None, description="Supplier SKU")
    unit_price: Optional[float] = Field(None, ge=0, description="Unit price")
    minimum_order_quantity: Optional[int] = Field(None, ge=1, description="Minimum order quantity")
    lead_time_days: Optional[int] = Field(None, ge=0, description="Lead time in days")
    is_preferred: bool = Field(False, description="Is preferred supplier")


class BulkPricingRequest(BaseModel):
    """Bulk pricing request"""
    product_ids: List[int] = Field(..., min_items=1, description="Product IDs")
    quantities: Optional[List[int]] = Field(None, description="Quantities per product")
    context: Optional[Dict[str, Any]] = Field(None, description="Pricing context")


# ==================== Lifecycle Management Endpoints ====================

@router.get("/{product_id}/lifecycle")
async def get_product_lifecycle(product_id: int):
    """Get product lifecycle information"""
    try:
        service = get_product_advanced_service()
        lifecycle = service.get_product_lifecycle(product_id)
        return {"success": True, "data": lifecycle}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lifecycle: {str(e)}")


@router.put("/{product_id}/lifecycle")
async def update_product_lifecycle(
    product_id: int,
    update: ProductLifecycleUpdate
):
    """Update product lifecycle status"""
    try:
        service = get_product_advanced_service()
        lifecycle = service.update_product_lifecycle(
            product_id,
            update.status,
            update.notes
        )
        return {"success": True, "data": lifecycle}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update lifecycle: {str(e)}")


# ==================== Versioning Endpoints ====================

@router.post("/{product_id}/versions")
async def create_product_version(
    product_id: int,
    version: ProductVersionCreate
):
    """Create a new product version"""
    try:
        service = get_product_advanced_service()
        new_version = service.create_product_version(
            product_id,
            version.changes,
            version.version_notes
        )
        return {"success": True, "data": new_version}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create version: {str(e)}")


@router.get("/{product_id}/versions")
async def get_product_version_history(
    product_id: int,
    limit: int = Query(50, ge=1, le=100, description="Maximum versions to return")
):
    """Get product version history"""
    try:
        service = get_product_advanced_service()
        versions = service.get_product_version_history(product_id, limit)
        return {"success": True, "data": versions}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get versions: {str(e)}")


# ==================== Comparison Endpoints ====================

@router.post("/compare")
async def compare_products(request: ProductComparisonRequest):
    """Compare multiple products"""
    try:
        service = get_product_advanced_service()
        comparison = service.compare_products(
            request.product_ids,
            request.comparison_attributes
        )
        return {"success": True, "data": comparison}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare products: {str(e)}")


# ==================== Recommendation Endpoints ====================

@router.post("/recommendations")
async def get_product_recommendations(request: ProductRecommendationRequest):
    """Get product recommendations based on calculation context"""
    try:
        service = get_product_advanced_service()
        recommendations = service.get_product_recommendations(
            request.calculation_context,
            request.category,
            request.limit
        )
        return {"success": True, "data": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


# ==================== Availability Endpoints ====================

@router.get("/{product_id}/availability")
async def get_product_availability(product_id: int):
    """Get product availability information"""
    try:
        service = get_product_advanced_service()
        availability = service.get_product_availability(product_id)
        return {"success": True, "data": availability}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get availability: {str(e)}")


@router.put("/{product_id}/availability")
async def update_product_availability(
    product_id: int,
    update: ProductAvailabilityUpdate
):
    """Update product availability"""
    try:
        service = get_product_advanced_service()
        availability = service.update_product_availability(
            product_id,
            update.stock_quantity,
            update.reorder_point,
            update.estimated_restock_date
        )
        return {"success": True, "data": availability}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update availability: {str(e)}")


# ==================== Supplier Endpoints ====================

@router.get("/{product_id}/suppliers")
async def get_product_suppliers(product_id: int):
    """Get suppliers for a product"""
    try:
        service = get_product_advanced_service()
        suppliers = service.get_product_suppliers(product_id)
        return {"success": True, "data": suppliers}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suppliers: {str(e)}")


@router.post("/{product_id}/suppliers")
async def add_product_supplier(
    product_id: int,
    supplier: ProductSupplierCreate
):
    """Add a supplier for a product"""
    try:
        service = get_product_advanced_service()
        new_supplier = service.add_product_supplier(
            product_id,
            supplier.dict()
        )
        return {"success": True, "data": new_supplier}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add supplier: {str(e)}")


# ==================== Pricing History Endpoints ====================

@router.get("/{product_id}/pricing-history")
async def get_pricing_history(
    product_id: int,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records")
):
    """Get pricing history for a product"""
    try:
        service = get_product_advanced_service()
        history = service.get_pricing_history(
            product_id,
            start_date,
            end_date,
            limit
        )
        return {"success": True, "data": history}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pricing history: {str(e)}")


@router.get("/{product_id}/pricing-trends")
async def analyze_pricing_trends(
    product_id: int,
    period_days: int = Query(90, ge=1, le=365, description="Analysis period in days")
):
    """Analyze pricing trends for a product"""
    try:
        service = get_product_advanced_service()
        trends = service.analyze_pricing_trends(product_id, period_days)
        return {"success": True, "data": trends}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze trends: {str(e)}")


# ==================== Performance Analytics Endpoints ====================

@router.get("/{product_id}/performance")
async def get_product_performance(
    product_id: int,
    period_days: int = Query(30, ge=1, le=365, description="Analysis period in days")
):
    """Get product performance analytics"""
    try:
        service = get_product_advanced_service()
        performance = service.get_product_performance(product_id, period_days)
        return {"success": True, "data": performance}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance: {str(e)}")


@router.get("/category/{category}/performance")
async def get_category_performance(
    category: str,
    period_days: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    limit: int = Query(10, ge=1, le=50, description="Top products to return")
):
    """Get performance analytics for a product category"""
    try:
        service = get_product_advanced_service()
        performance = service.get_category_performance(category, period_days, limit)
        return {"success": True, "data": performance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category performance: {str(e)}")


# ==================== Price Matrix Integration Endpoints ====================

@router.get("/{product_id}/matrix-pricing")
async def get_product_pricing_from_matrix(
    product_id: int,
    quantity: int = Query(1, ge=1, description="Quantity"),
    context: Optional[str] = Query(None, description="Context JSON string")
):
    """Get product pricing from price matrix"""
    try:
        import json
        context_dict = json.loads(context) if context else None
        
        service = get_product_advanced_service()
        pricing = service.get_product_pricing_from_matrix(
            product_id,
            quantity,
            context_dict
        )
        return {"success": True, "data": pricing}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pricing: {str(e)}")


@router.post("/bulk-pricing")
async def get_bulk_pricing(request: BulkPricingRequest):
    """Get bulk pricing for multiple products"""
    try:
        service = get_product_advanced_service()
        pricing = service.get_bulk_pricing(
            request.product_ids,
            request.quantities,
            request.context
        )
        return {"success": True, "data": pricing}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bulk pricing: {str(e)}")
