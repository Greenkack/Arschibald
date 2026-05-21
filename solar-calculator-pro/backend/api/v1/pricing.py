"""
Product Pricing API Endpoints
RESTful API for managing product pricing
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db
from backend.services.pricing_service import PricingService
from backend.models.pricing_schemas import (
    PriceListCreate, PriceListUpdate, PriceListResponse,
    ProductPriceCreate, ProductPriceUpdate, ProductPriceResponse,
    PriceHistoryResponse, VolumeDiscountCreate, VolumeDiscountUpdate,
    VolumeDiscountResponse, PromotionalPricingCreate, PromotionalPricingUpdate,
    PromotionalPricingResponse, CustomerSpecificPriceCreate,
    CustomerSpecificPriceUpdate, CustomerSpecificPriceResponse,
    PriceCalculationRequest, PriceCalculationResponse
)

router = APIRouter(prefix="/pricing", tags=["pricing"])


# Price List Endpoints
@router.post("/price-lists", response_model=PriceListResponse, status_code=status.HTTP_201_CREATED)
async def create_price_list(
    price_list: PriceListCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new price list
    
    - **name**: Unique name for the price list
    - **currency**: Currency code (default: EUR)
    - **is_default**: Set as default price list
    - **valid_from**: Start date for price list validity
    - **valid_until**: Optional end date
    """
    service = PricingService(db)
    return service.create_price_list(price_list)


@router.get("/price-lists", response_model=List[PriceListResponse])
async def get_price_lists(
    active_only: bool = Query(False, description="Filter active price lists only"),
    db: Session = Depends(get_db)
):
    """Get all price lists"""
    service = PricingService(db)
    return service.get_price_lists(active_only=active_only)


@router.get("/price-lists/{price_list_id}", response_model=PriceListResponse)
async def get_price_list(
    price_list_id: int,
    db: Session = Depends(get_db)
):
    """Get price list by ID"""
    service = PricingService(db)
    price_list = service.get_price_list(price_list_id)
    if not price_list:
        raise HTTPException(status_code=404, detail="Price list not found")
    return price_list


@router.put("/price-lists/{price_list_id}", response_model=PriceListResponse)
async def update_price_list(
    price_list_id: int,
    update_data: PriceListUpdate,
    db: Session = Depends(get_db)
):
    """Update price list"""
    service = PricingService(db)
    return service.update_price_list(price_list_id, update_data)


@router.delete("/price-lists/{price_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_price_list(
    price_list_id: int,
    db: Session = Depends(get_db)
):
    """Delete price list"""
    service = PricingService(db)
    service.delete_price_list(price_list_id)


# Product Price Endpoints
@router.post("/product-prices", response_model=ProductPriceResponse, status_code=status.HTTP_201_CREATED)
async def create_product_price(
    product_price: ProductPriceCreate,
    changed_by: Optional[str] = Query(None, description="User making the change"),
    db: Session = Depends(get_db)
):
    """
    Create product price in a price list
    
    - **product_id**: Product identifier
    - **base_price**: Base price for the product
    - **pricing_type**: Type of pricing (standard, tiered, etc.)
    - **tier_config**: Configuration for tiered pricing
    """
    service = PricingService(db)
    return service.create_product_price(product_price, changed_by)


@router.put("/product-prices/{product_price_id}", response_model=ProductPriceResponse)
async def update_product_price(
    product_price_id: int,
    update_data: ProductPriceUpdate,
    changed_by: Optional[str] = Query(None, description="User making the change"),
    db: Session = Depends(get_db)
):
    """Update product price"""
    service = PricingService(db)
    return service.update_product_price(product_price_id, update_data, changed_by)


@router.get("/product-prices/{product_price_id}/history", response_model=List[PriceHistoryResponse])
async def get_product_price_history(
    product_price_id: int,
    db: Session = Depends(get_db)
):
    """Get price change history for a product"""
    service = PricingService(db)
    return service.get_product_price_history(product_price_id)


# Volume Discount Endpoints
@router.post("/volume-discounts", response_model=VolumeDiscountResponse, status_code=status.HTTP_201_CREATED)
async def create_volume_discount(
    discount: VolumeDiscountCreate,
    db: Session = Depends(get_db)
):
    """
    Create volume discount rule
    
    - **name**: Discount name
    - **discount_type**: Type of discount (percentage, fixed_amount, tiered_percentage)
    - **min_quantity**: Minimum quantity for discount
    - **discount_value**: Discount value
    - **tier_config**: Optional tiered discount configuration
    """
    service = PricingService(db)
    return service.create_volume_discount(discount)


@router.get("/volume-discounts", response_model=List[VolumeDiscountResponse])
async def get_volume_discounts(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    active_only: bool = Query(True, description="Filter active discounts only"),
    db: Session = Depends(get_db)
):
    """Get volume discounts"""
    service = PricingService(db)
    return service.get_volume_discounts(product_id=product_id, active_only=active_only)


@router.put("/volume-discounts/{discount_id}", response_model=VolumeDiscountResponse)
async def update_volume_discount(
    discount_id: int,
    update_data: VolumeDiscountUpdate,
    db: Session = Depends(get_db)
):
    """Update volume discount"""
    service = PricingService(db)
    return service.update_volume_discount(discount_id, update_data)


# Promotional Pricing Endpoints
@router.post("/promotions", response_model=PromotionalPricingResponse, status_code=status.HTTP_201_CREATED)
async def create_promotional_pricing(
    promo: PromotionalPricingCreate,
    db: Session = Depends(get_db)
):
    """
    Create promotional pricing campaign
    
    - **name**: Campaign name
    - **promo_code**: Optional promo code
    - **discount_type**: Type of discount
    - **discount_value**: Discount value
    - **valid_from**: Campaign start date
    - **valid_until**: Campaign end date
    - **max_uses_total**: Optional total usage limit
    - **max_uses_per_customer**: Optional per-customer usage limit
    """
    service = PricingService(db)
    return service.create_promotional_pricing(promo)


@router.get("/promotions/{promo_code}", response_model=PromotionalPricingResponse)
async def get_promotional_pricing(
    promo_code: str,
    db: Session = Depends(get_db)
):
    """Get promotional pricing by code"""
    service = PricingService(db)
    promo = service.get_promotional_pricing(promo_code)
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found or expired")
    return promo


@router.post("/promotions/validate")
async def validate_promo_code(
    promo_code: str = Query(..., description="Promo code to validate"),
    customer_id: int = Query(..., description="Customer ID"),
    product_id: int = Query(..., description="Product ID"),
    db: Session = Depends(get_db)
):
    """Validate if promo code can be used"""
    service = PricingService(db)
    is_valid, error_msg = service.validate_promo_code(promo_code, customer_id, product_id)
    
    if not is_valid:
        return {"valid": False, "message": error_msg}
    
    return {"valid": True, "message": "Promo code is valid"}


# Customer-Specific Pricing Endpoints
@router.post("/customer-prices", response_model=CustomerSpecificPriceResponse, status_code=status.HTTP_201_CREATED)
async def create_customer_specific_price(
    price: CustomerSpecificPriceCreate,
    db: Session = Depends(get_db)
):
    """
    Create customer-specific price
    
    - **customer_id**: Customer identifier
    - **product_id**: Product identifier
    - **special_price**: Special price for customer
    - **reason**: Reason for special pricing
    """
    service = PricingService(db)
    return service.create_customer_specific_price(price)


@router.get("/customer-prices/{customer_id}/{product_id}", response_model=CustomerSpecificPriceResponse)
async def get_customer_specific_price(
    customer_id: int,
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get customer-specific price"""
    service = PricingService(db)
    price = service.get_customer_specific_price(customer_id, product_id)
    if not price:
        raise HTTPException(status_code=404, detail="Customer-specific price not found")
    return price


# Price Calculation Endpoint
@router.post("/calculate", response_model=PriceCalculationResponse)
async def calculate_price(
    request: PriceCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate final price with all applicable discounts
    
    - **product_id**: Product identifier
    - **quantity**: Quantity to purchase
    - **customer_id**: Optional customer identifier for customer-specific pricing
    - **promo_code**: Optional promotional code
    - **price_list_id**: Optional price list identifier
    
    Returns detailed price breakdown with all applied discounts
    """
    service = PricingService(db)
    return service.calculate_price(request)
