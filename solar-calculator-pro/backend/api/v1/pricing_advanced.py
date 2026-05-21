"""
Advanced Pricing API Endpoints

FastAPI endpoints for advanced pricing features.

Requirements: 1.3, 4.5, 6.1
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.services.pricing_advanced_service import (
    get_pricing_advanced_service,
    PricingAdvancedService
)

router = APIRouter(prefix="/pricing/advanced", tags=["pricing-advanced"])


# ========================================================================
# Request/Response Models
# ========================================================================

class PricingRuleCreate(BaseModel):
    """Request model for creating pricing rule"""
    name: str
    rule_type: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int = 0
    active: bool = True
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class VolumeDiscountRequest(BaseModel):
    """Request model for volume discount calculation"""
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    discount_tiers: List[Dict[str, Any]]


class TimeBasedPriceRequest(BaseModel):
    """Request model for time-based pricing"""
    base_price: float = Field(..., gt=0)
    pricing_schedule: Dict[str, Any]
    target_date: Optional[datetime] = None


class CustomerPriceRequest(BaseModel):
    """Request model for customer-specific pricing"""
    customer_id: str
    product_id: str
    base_price: float = Field(..., gt=0)
    quantity: int = Field(default=1, gt=0)


class BundlePriceRequest(BaseModel):
    """Request model for bundle pricing"""
    items: List[Dict[str, Any]]
    bundle_rules: Optional[Dict[str, Any]] = None


class PromotionCreate(BaseModel):
    """Request model for creating promotion"""
    name: str
    promotion_type: str
    discount_value: float
    valid_from: datetime
    valid_until: datetime
    conditions: Optional[Dict[str, Any]] = None
    max_uses: Optional[int] = None
    max_uses_per_customer: Optional[int] = None


class PromotionCodeRequest(BaseModel):
    """Request model for applying promotion code"""
    promo_code: str
    base_price: float = Field(..., gt=0)
    customer_id: Optional[str] = None


class ExchangeRateSet(BaseModel):
    """Request model for setting exchange rate"""
    from_currency: str
    to_currency: str
    rate: float = Field(..., gt=0)


class CurrencyConvertRequest(BaseModel):
    """Request model for currency conversion"""
    amount: float = Field(..., gt=0)
    from_currency: str
    to_currency: str


class MultiCurrencyPriceRequest(BaseModel):
    """Request model for multi-currency pricing"""
    base_price: float = Field(..., gt=0)
    base_currency: str
    target_currencies: List[str]


class PriceChangeRecord(BaseModel):
    """Request model for recording price change"""
    product_id: str
    old_price: float = Field(..., ge=0)
    new_price: float = Field(..., ge=0)
    reason: str
    changed_by: Optional[str] = None


# ========================================================================
# Endpoints
# ========================================================================

@router.get("/health")
async def health_check(
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Health check endpoint"""
    return service.health_check()


# Dynamic Pricing Rules
@router.post("/rules")
async def create_pricing_rule(
    request: PricingRuleCreate,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Create a dynamic pricing rule"""
    result = service.create_pricing_rule(
        name=request.name,
        rule_type=request.rule_type,
        conditions=request.conditions,
        actions=request.actions,
        priority=request.priority,
        active=request.active,
        valid_from=request.valid_from,
        valid_until=request.valid_until
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@router.post("/rules/apply")
async def apply_pricing_rules(
    base_price: float,
    context: Dict[str, Any],
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Apply pricing rules to a base price"""
    result = service.apply_pricing_rules(base_price, context)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


# Volume Discounts
@router.post("/volume-discount")
async def calculate_volume_discount(
    request: VolumeDiscountRequest,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Calculate volume-based discount"""
    result = service.calculate_volume_discount(
        quantity=request.quantity,
        unit_price=request.unit_price,
        discount_tiers=request.discount_tiers
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


# Time-Based Pricing
@router.post("/time-based")
async def calculate_time_based_price(
    request: TimeBasedPriceRequest,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Calculate time-based pricing"""
    result = service.calculate_time_based_price(
        base_price=request.base_price,
        pricing_schedule=request.pricing_schedule,
        target_date=request.target_date
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


# Customer-Specific Pricing
@router.post("/customer-price")
async def get_customer_price(
    request: CustomerPriceRequest,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Get customer-specific pricing"""
    result = service.get_customer_price(
        customer_id=request.customer_id,
        product_id=request.product_id,
        base_price=request.base_price,
        quantity=request.quantity
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


# Bundle Pricing
@router.post("/bundle")
async def calculate_bundle_price(
    request: BundlePriceRequest,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Calculate bundle pricing"""
    result = service.calculate_bundle_price(
        items=request.items,
        bundle_rules=request.bundle_rules
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


# Promotional Pricing
@router.post("/promotions")
async def create_promotion(
    request: PromotionCreate,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Create a promotional campaign"""
    result = service.create_promotion(
        name=request.name,
        promotion_type=request.promotion_type,
        discount_value=request.discount_value,
        valid_from=request.valid_from,
        valid_until=request.valid_until,
        conditions=request.conditions,
        max_uses=request.max_uses,
        max_uses_per_customer=request.max_uses_per_customer
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@router.post("/promotions/apply")
async def apply_promotion_code(
    request: PromotionCodeRequest,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Apply promotion code to price"""
    result = service.apply_promotion_code(
        promo_code=request.promo_code,
        base_price=request.base_price,
        customer_id=request.customer_id
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


# Currency Conversion
@router.post("/currency/exchange-rate")
async def set_exchange_rate(
    request: ExchangeRateSet,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Set exchange rate between currencies"""
    result = service.set_exchange_rate(
        from_currency=request.from_currency,
        to_currency=request.to_currency,
        rate=request.rate
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@router.post("/currency/convert")
async def convert_currency(
    request: CurrencyConvertRequest,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Convert amount from one currency to another"""
    result = service.convert_currency(
        amount=request.amount,
        from_currency=request.from_currency,
        to_currency=request.to_currency
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@router.post("/currency/multi-currency")
async def get_multi_currency_price(
    request: MultiCurrencyPriceRequest,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Get price in multiple currencies"""
    result = service.get_multi_currency_price(
        base_price=request.base_price,
        base_currency=request.base_currency,
        target_currencies=request.target_currencies
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


# Price History
@router.post("/history/record")
async def record_price_change(
    request: PriceChangeRecord,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Record a price change in history"""
    result = service.record_price_change(
        product_id=request.product_id,
        old_price=request.old_price,
        new_price=request.new_price,
        reason=request.reason,
        changed_by=request.changed_by
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@router.get("/history")
async def get_price_history(
    product_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Get price change history"""
    result = service.get_price_history(
        product_id=product_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@router.get("/history/trend/{product_id}")
async def get_price_trend(
    product_id: str,
    days: int = 30,
    service: PricingAdvancedService = Depends(get_pricing_advanced_service)
):
    """Get price trend analysis"""
    result = service.get_price_trend(
        product_id=product_id,
        days=days
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result
