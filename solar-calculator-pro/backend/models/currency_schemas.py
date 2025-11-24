"""
Currency Pydantic Schemas

This module defines the Pydantic schemas for currency-related API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CurrencyBase(BaseModel):
    """Base currency schema"""
    code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)
    decimal_places: int = Field(default=2, ge=0, le=4)
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    
    @validator('code')
    def code_must_be_uppercase(cls, v):
        return v.upper()


class CurrencyCreate(CurrencyBase):
    """Schema for creating a new currency"""
    pass


class CurrencyUpdate(BaseModel):
    """Schema for updating a currency"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    decimal_places: Optional[int] = Field(None, ge=0, le=4)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class CurrencyResponse(CurrencyBase):
    """Schema for currency response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExchangeRateBase(BaseModel):
    """Base exchange rate schema"""
    from_currency_code: str = Field(..., min_length=3, max_length=3)
    to_currency_code: str = Field(..., min_length=3, max_length=3)
    rate: float = Field(..., gt=0)
    source: Optional[str] = Field(None, max_length=100)
    valid_from: datetime
    valid_to: Optional[datetime] = None
    is_active: bool = Field(default=True)


class ExchangeRateCreate(ExchangeRateBase):
    """Schema for creating a new exchange rate"""
    pass


class ExchangeRateUpdate(BaseModel):
    """Schema for updating an exchange rate"""
    rate: Optional[float] = Field(None, gt=0)
    source: Optional[str] = Field(None, max_length=100)
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class ExchangeRateResponse(BaseModel):
    """Schema for exchange rate response"""
    id: int
    from_currency_code: str
    to_currency_code: str
    rate: float
    source: Optional[str]
    valid_from: datetime
    valid_to: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CurrencyConversionRequest(BaseModel):
    """Schema for currency conversion request"""
    amount: float = Field(..., description="Amount to convert")
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    date: Optional[datetime] = Field(None, description="Date for historical rate (optional)")
    
    @validator('from_currency', 'to_currency')
    def currency_must_be_uppercase(cls, v):
        return v.upper()


class CurrencyConversionResponse(BaseModel):
    """Schema for currency conversion response"""
    original_amount: float
    converted_amount: float
    from_currency: str
    to_currency: str
    exchange_rate: float
    conversion_date: datetime
    source: Optional[str]


class MultiCurrencyDisplayRequest(BaseModel):
    """Schema for multi-currency display request"""
    base_amount: float
    base_currency: str = Field(..., min_length=3, max_length=3)
    target_currencies: List[str] = Field(..., min_items=1)
    
    @validator('base_currency')
    def base_currency_must_be_uppercase(cls, v):
        return v.upper()
    
    @validator('target_currencies')
    def target_currencies_must_be_uppercase(cls, v):
        return [c.upper() for c in v]


class MultiCurrencyDisplayResponse(BaseModel):
    """Schema for multi-currency display response"""
    base_amount: float
    base_currency: str
    conversions: List[CurrencyConversionResponse]


class CurrencyRoundingRuleBase(BaseModel):
    """Base currency rounding rule schema"""
    currency_code: str = Field(..., min_length=3, max_length=3)
    rounding_mode: str = Field(default="ROUND_HALF_UP")
    rounding_precision: int = Field(default=2, ge=0, le=4)
    min_unit: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    
    @validator('currency_code')
    def currency_code_must_be_uppercase(cls, v):
        return v.upper()
    
    @validator('rounding_mode')
    def validate_rounding_mode(cls, v):
        valid_modes = ["ROUND_UP", "ROUND_DOWN", "ROUND_HALF_UP", "ROUND_HALF_DOWN", "ROUND_CEILING", "ROUND_FLOOR"]
        if v not in valid_modes:
            raise ValueError(f"Rounding mode must be one of: {', '.join(valid_modes)}")
        return v


class CurrencyRoundingRuleCreate(CurrencyRoundingRuleBase):
    """Schema for creating a currency rounding rule"""
    pass


class CurrencyRoundingRuleUpdate(BaseModel):
    """Schema for updating a currency rounding rule"""
    rounding_mode: Optional[str] = None
    rounding_precision: Optional[int] = Field(None, ge=0, le=4)
    min_unit: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None


class CurrencyRoundingRuleResponse(CurrencyRoundingRuleBase):
    """Schema for currency rounding rule response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExchangeRateHistoryResponse(BaseModel):
    """Schema for exchange rate history response"""
    id: int
    from_currency_code: str
    to_currency_code: str
    rate: float
    source: Optional[str]
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class CurrencyUpdateRequest(BaseModel):
    """Schema for currency update request"""
    source: Optional[str] = Field(None, description="API source for rates")
    currencies: Optional[List[str]] = Field(None, description="Specific currencies to update")
    force: bool = Field(default=False, description="Force update even if recent data exists")


class CurrencyUpdateResponse(BaseModel):
    """Schema for currency update response"""
    update_type: str
    source: Optional[str]
    currencies_updated: int
    rates_updated: int
    status: str
    error_message: Optional[str]
    started_at: datetime
    completed_at: datetime


class CurrencyStatistics(BaseModel):
    """Schema for currency statistics"""
    total_currencies: int
    active_currencies: int
    total_exchange_rates: int
    active_exchange_rates: int
    last_update: Optional[datetime]
    default_currency: Optional[str]
