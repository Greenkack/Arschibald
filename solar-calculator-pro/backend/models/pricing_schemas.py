"""
Product Pricing Pydantic Schemas
Request/Response models for pricing API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PricingTypeEnum(str, Enum):
    """Pricing strategy types"""
    STANDARD = "standard"
    TIERED = "tiered"
    CUSTOMER_SPECIFIC = "customer_specific"
    VOLUME_DISCOUNT = "volume_discount"
    PROMOTIONAL = "promotional"
    BUNDLE = "bundle"


class DiscountTypeEnum(str, Enum):
    """Discount types"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED_PERCENTAGE = "tiered_percentage"


# Price List Schemas
class PriceListBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    is_active: bool = True
    is_default: bool = False
    valid_from: datetime
    valid_until: Optional[datetime] = None


class PriceListCreate(PriceListBase):
    pass


class PriceListUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    valid_until: Optional[datetime] = None


class PriceListResponse(PriceListBase):
    id: int
    created_at: datetime
    updated_at: datetime
    product_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Product Price Schemas
class TierConfig(BaseModel):
    """Configuration for tiered pricing"""
    min_quantity: int = Field(..., ge=1)
    max_quantity: Optional[int] = Field(None, ge=1)
    price: float = Field(..., gt=0)

    @validator('max_quantity')
    def validate_max_quantity(cls, v, values):
        if v is not None and 'min_quantity' in values and v <= values['min_quantity']:
            raise ValueError('max_quantity must be greater than min_quantity')
        return v


class ProductPriceBase(BaseModel):
    product_id: int = Field(..., gt=0)
    base_price: float = Field(..., gt=0)
    pricing_type: PricingTypeEnum = PricingTypeEnum.STANDARD
    tier_config: Optional[List[TierConfig]] = None
    cost_price: Optional[float] = Field(None, ge=0)
    margin_percentage: Optional[float] = Field(None, ge=0, le=100)


class ProductPriceCreate(ProductPriceBase):
    price_list_id: int = Field(..., gt=0)


class ProductPriceUpdate(BaseModel):
    base_price: Optional[float] = Field(None, gt=0)
    pricing_type: Optional[PricingTypeEnum] = None
    tier_config: Optional[List[TierConfig]] = None
    cost_price: Optional[float] = Field(None, ge=0)
    margin_percentage: Optional[float] = Field(None, ge=0, le=100)


class ProductPriceResponse(ProductPriceBase):
    id: int
    price_list_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Price History Schemas
class PriceHistoryResponse(BaseModel):
    id: int
    product_price_id: int
    old_price: float
    new_price: float
    change_percentage: Optional[float]
    change_reason: Optional[str]
    changed_by: Optional[str]
    changed_at: datetime

    class Config:
        from_attributes = True


# Volume Discount Schemas
class VolumeTierConfig(BaseModel):
    """Configuration for tiered volume discounts"""
    min_qty: int = Field(..., ge=1)
    max_qty: Optional[int] = Field(None, ge=1)
    discount: float = Field(..., gt=0)


class VolumeDiscountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    product_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    discount_type: DiscountTypeEnum
    min_quantity: int = Field(..., ge=1)
    max_quantity: Optional[int] = Field(None, ge=1)
    discount_value: float = Field(..., gt=0)
    tier_config: Optional[List[VolumeTierConfig]] = None
    is_active: bool = True
    valid_from: datetime
    valid_until: Optional[datetime] = None


class VolumeDiscountCreate(VolumeDiscountBase):
    pass


class VolumeDiscountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    discount_value: Optional[float] = Field(None, gt=0)
    tier_config: Optional[List[VolumeTierConfig]] = None
    is_active: Optional[bool] = None
    valid_until: Optional[datetime] = None


class VolumeDiscountResponse(VolumeDiscountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Promotional Pricing Schemas
class PromotionalPricingBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    promo_code: Optional[str] = Field(None, min_length=1, max_length=50)
    discount_type: DiscountTypeEnum
    discount_value: float = Field(..., gt=0)
    max_discount_amount: Optional[float] = Field(None, gt=0)
    product_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    customer_ids: Optional[List[int]] = None
    max_uses_total: Optional[int] = Field(None, ge=1)
    max_uses_per_customer: Optional[int] = Field(None, ge=1)
    is_active: bool = True
    valid_from: datetime
    valid_until: datetime

    @validator('valid_until')
    def validate_dates(cls, v, values):
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('valid_until must be after valid_from')
        return v


class PromotionalPricingCreate(PromotionalPricingBase):
    pass


class PromotionalPricingUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    discount_value: Optional[float] = Field(None, gt=0)
    max_discount_amount: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None
    valid_until: Optional[datetime] = None


class PromotionalPricingResponse(PromotionalPricingBase):
    id: int
    current_uses: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Customer-Specific Price Schemas
class CustomerSpecificPriceBase(BaseModel):
    customer_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    special_price: float = Field(..., gt=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    reason: Optional[str] = Field(None, max_length=500)
    is_active: bool = True
    valid_from: datetime
    valid_until: Optional[datetime] = None


class CustomerSpecificPriceCreate(CustomerSpecificPriceBase):
    pass


class CustomerSpecificPriceUpdate(BaseModel):
    special_price: Optional[float] = Field(None, gt=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    reason: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    valid_until: Optional[datetime] = None


class CustomerSpecificPriceResponse(CustomerSpecificPriceBase):
    id: int
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Price Calculation Schemas
class PriceCalculationRequest(BaseModel):
    """Request for price calculation"""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)
    customer_id: Optional[int] = Field(None, gt=0)
    promo_code: Optional[str] = None
    price_list_id: Optional[int] = Field(None, gt=0)


class PriceBreakdown(BaseModel):
    """Detailed price breakdown"""
    base_price: float
    unit_price: float
    subtotal: float
    volume_discount: float = 0.0
    promotional_discount: float = 0.0
    customer_discount: float = 0.0
    total_discount: float = 0.0
    final_price: float
    currency: str = "EUR"
    pricing_type: str
    applied_discounts: List[Dict[str, Any]] = []


class PriceCalculationResponse(BaseModel):
    """Response with calculated price"""
    product_id: int
    quantity: int
    breakdown: PriceBreakdown
    formatted_price: str  # German format: "16.999,00 €"
    savings: Optional[float] = None
    savings_percentage: Optional[float] = None
