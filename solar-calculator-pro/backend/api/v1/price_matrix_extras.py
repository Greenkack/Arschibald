"""
Price Matrix Extras and Services API Endpoints

API endpoints for calculating extras, services, bundles, and applying pricing rules.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Any, Optional
from decimal import Decimal

from ...services.price_matrix_extras_service import PriceMatrixExtrasService
from ...core.database import get_db

router = APIRouter(prefix="/price-matrix-extras", tags=["price-matrix-extras"])


# Request/Response Models

class ProductItem(BaseModel):
    """Product item for calculation"""
    id: Optional[int] = None
    model_name: Optional[str] = None
    name: str
    category: str
    price: float
    quantity: float = 1.0
    calculate_per: Optional[str] = "Stück"


class ServiceSelection(BaseModel):
    """Service selection request"""
    service_ids: list[int] = Field(default_factory=list)
    include_standard: bool = True


class BundleRule(BaseModel):
    """Bundle pricing rule"""
    name: str
    type: str  # 'percentage' or 'fixed'
    value: float
    required_items: list[int] = Field(default_factory=list)
    required_categories: list[str] = Field(default_factory=list)
    min_items: int = 0
    min_total: float = 0.0


class ConditionalRule(BaseModel):
    """Conditional pricing rule"""
    name: str
    condition: dict[str, Any]
    adjustment_type: str  # 'percentage', 'fixed', 'multiplier'
    adjustment_value: float


class CustomRule(BaseModel):
    """Custom pricing rule"""
    name: str
    type: str  # 'discount', 'surcharge'
    value: float
    value_type: str = 'fixed'  # 'fixed' or 'percentage'
    enabled: bool = True


class SpecialProductsRequest(BaseModel):
    """Request for special products calculation"""
    project_details: dict[str, Any]
    selected_products: list[ProductItem]


class ServicesRequest(BaseModel):
    """Request for services calculation"""
    project_details: dict[str, Any]
    selected_service_ids: list[int] = Field(default_factory=list)
    include_standard: bool = True


class BundlePricingRequest(BaseModel):
    """Request for bundle pricing calculation"""
    items: list[dict[str, Any]]
    bundle_rules: list[BundleRule]


class ConditionalPricingRequest(BaseModel):
    """Request for conditional pricing"""
    base_price: float
    conditions: dict[str, Any]
    pricing_rules: list[ConditionalRule]


class CustomRulesRequest(BaseModel):
    """Request for custom pricing rules"""
    pricing_data: dict[str, Any]
    custom_rules: list[CustomRule]


# API Endpoints

@router.post("/special-products")
async def calculate_special_products(
    request: SpecialProductsRequest,
    db=Depends(get_db)
):
    """
    Calculate costs for special products (extras)
    
    Special products are marked with is_special_product = 1 and are
    calculated in addition to the base price matrix price.
    """
    try:
        service = PriceMatrixExtrasService(db)
        
        # Convert ProductItem models to dicts
        products_dict = [p.dict() for p in request.selected_products]
        
        result = service.calculate_special_products(
            request.project_details,
            products_dict
        )
        
        # Convert Decimal to float for JSON serialization
        return {
            'total': float(result['total']),
            'items': [
                {
                    **item,
                    'unit_price': float(item['unit_price']),
                    'total_price': float(item['total_price'])
                }
                for item in result['items']
            ],
            'count': result['count'],
            'formatted_total': result['formatted_total']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services")
async def calculate_services(
    request: ServicesRequest,
    db=Depends(get_db)
):
    """
    Calculate service pricing
    
    Calculates costs for standard services (always included) and
    selected optional services.
    """
    try:
        service = PriceMatrixExtrasService(db)
        
        result = service.calculate_services(
            request.project_details,
            request.selected_service_ids,
            request.include_standard
        )
        
        # Convert Decimal to float for JSON serialization
        return {
            'standard_services': [
                {
                    **s,
                    'unit_price': float(s['unit_price']),
                    'total_price': float(s['total_price'])
                }
                for s in result['standard_services']
            ],
            'optional_services': [
                {
                    **s,
                    'unit_price': float(s['unit_price']),
                    'total_price': float(s['total_price'])
                }
                for s in result['optional_services']
            ],
            'total_standard': float(result['total_standard']),
            'total_optional': float(result['total_optional']),
            'total_services': float(result['total_services']),
            'formatted_total_standard': result['formatted_total_standard'],
            'formatted_total_optional': result['formatted_total_optional'],
            'formatted_total_services': result['formatted_total_services']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bundle-pricing")
async def calculate_bundle_pricing(
    request: BundlePricingRequest,
    db=Depends(get_db)
):
    """
    Calculate bundle pricing with discounts
    
    Applies bundle discount rules to a set of items.
    """
    try:
        service = PriceMatrixExtrasService(db)
        
        # Convert BundleRule models to dicts
        rules_dict = [r.dict() for r in request.bundle_rules]
        
        result = service.calculate_bundle_pricing(
            request.items,
            rules_dict
        )
        
        # Convert Decimal to float for JSON serialization
        return {
            'original_total': float(result['original_total']),
            'discount_amount': float(result['discount_amount']),
            'discount_percentage': float(result['discount_percentage']),
            'final_total': float(result['final_total']),
            'applied_rules': result['applied_rules'],
            'formatted_original': result['formatted_original'],
            'formatted_discount': result['formatted_discount'],
            'formatted_final': result['formatted_final']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conditional-pricing")
async def apply_conditional_pricing(
    request: ConditionalPricingRequest,
    db=Depends(get_db)
):
    """
    Apply conditional pricing rules
    
    Applies pricing adjustments based on conditions like system size,
    customer type, season, etc.
    """
    try:
        service = PriceMatrixExtrasService(db)
        
        # Convert ConditionalRule models to dicts
        rules_dict = [r.dict() for r in request.pricing_rules]
        
        result = service.apply_conditional_pricing(
            Decimal(str(request.base_price)),
            request.conditions,
            rules_dict
        )
        
        # Convert Decimal to float for JSON serialization
        return {
            'base_price': float(result['base_price']),
            'adjustments': [
                {
                    **adj,
                    'amount': float(adj['amount'])
                }
                for adj in result['adjustments']
            ],
            'total_adjustment': float(result['total_adjustment']),
            'final_price': float(result['final_price']),
            'formatted_base': result['formatted_base'],
            'formatted_adjustment': result['formatted_adjustment'],
            'formatted_final': result['formatted_final']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/custom-rules")
async def apply_custom_rules(
    request: CustomRulesRequest,
    db=Depends(get_db)
):
    """
    Apply custom pricing rules
    
    Applies user-defined custom pricing rules like discounts, surcharges, etc.
    """
    try:
        service = PriceMatrixExtrasService(db)
        
        # Convert CustomRule models to dicts
        rules_dict = [r.dict() for r in request.custom_rules]
        
        result = service.apply_custom_pricing_rules(
            request.pricing_data,
            rules_dict
        )
        
        # Convert Decimal values to float for JSON serialization
        if 'total' in result and isinstance(result['total'], Decimal):
            result['total'] = float(result['total'])
        if 'discount_applied' in result and isinstance(result['discount_applied'], Decimal):
            result['discount_applied'] = float(result['discount_applied'])
        if 'surcharge_applied' in result and isinstance(result['surcharge_applied'], Decimal):
            result['surcharge_applied'] = float(result['surcharge_applied'])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/all")
async def get_all_services(db=Depends(get_db)):
    """
    Get all available services
    
    Returns all services from the database, both standard and optional.
    """
    try:
        service = PriceMatrixExtrasService(db)
        services = service._get_services_from_db()
        
        return {
            'services': services,
            'count': len(services)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/standard")
async def get_standard_services(db=Depends(get_db)):
    """
    Get standard services (always included)
    """
    try:
        service = PriceMatrixExtrasService(db)
        all_services = service._get_services_from_db()
        standard = [s for s in all_services if s.get('is_standard', False)]
        
        return {
            'services': standard,
            'count': len(standard)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/optional")
async def get_optional_services(db=Depends(get_db)):
    """
    Get optional services (user-selectable)
    """
    try:
        service = PriceMatrixExtrasService(db)
        all_services = service._get_services_from_db()
        optional = [s for s in all_services if not s.get('is_standard', False)]
        
        return {
            'services': optional,
            'count': len(optional)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
