"""
Currency API Endpoints

This module provides REST API endpoints for currency management and conversion.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.core.dependencies import get_db
from backend.services.currency_service import CurrencyService
from backend.models.currency_schemas import (
    CurrencyCreate, CurrencyUpdate, CurrencyResponse,
    ExchangeRateCreate, ExchangeRateUpdate, ExchangeRateResponse,
    CurrencyConversionRequest, CurrencyConversionResponse,
    MultiCurrencyDisplayRequest, MultiCurrencyDisplayResponse,
    CurrencyRoundingRuleCreate, CurrencyRoundingRuleUpdate, CurrencyRoundingRuleResponse,
    CurrencyUpdateRequest, CurrencyUpdateResponse,
    CurrencyStatistics
)

router = APIRouter(prefix="/currency", tags=["currency"])


def get_currency_service(db: Session = Depends(get_db)) -> CurrencyService:
    """Dependency to get currency service"""
    return CurrencyService(db)


# ==================== Currency Management ====================

@router.post("/currencies", response_model=CurrencyResponse, status_code=201)
def create_currency(
    currency_data: CurrencyCreate,
    service: CurrencyService = Depends(get_currency_service)
):
    """
    Create a new currency
    
    - **code**: ISO 4217 currency code (e.g., EUR, USD, GBP)
    - **name**: Full currency name
    - **symbol**: Currency symbol (e.g., €, $, £)
    - **decimal_places**: Number of decimal places (default: 2)
    - **is_active**: Whether the currency is active
    - **is_default**: Whether this is the default currency
    """
    try:
        return service.create_currency(currency_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/currencies", response_model=List[CurrencyResponse])
def list_currencies(
    active_only: bool = Query(False, description="Return only active currencies"),
    service: CurrencyService = Depends(get_currency_service)
):
    """List all currencies"""
    return service.list_currencies(active_only=active_only)


@router.get("/currencies/{currency_id}", response_model=CurrencyResponse)
def get_currency(
    currency_id: int,
    service: CurrencyService = Depends(get_currency_service)
):
    """Get currency by ID"""
    currency = service.get_currency(currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    return currency


@router.get("/currencies/code/{code}", response_model=CurrencyResponse)
def get_currency_by_code(
    code: str,
    service: CurrencyService = Depends(get_currency_service)
):
    """Get currency by code"""
    currency = service.get_currency_by_code(code)
    if not currency:
        raise HTTPException(status_code=404, detail=f"Currency {code} not found")
    return currency


@router.put("/currencies/{currency_id}", response_model=CurrencyResponse)
def update_currency(
    currency_id: int,
    currency_data: CurrencyUpdate,
    service: CurrencyService = Depends(get_currency_service)
):
    """Update a currency"""
    try:
        return service.update_currency(currency_id, currency_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/currencies/{currency_id}", status_code=204)
def delete_currency(
    currency_id: int,
    service: CurrencyService = Depends(get_currency_service)
):
    """Delete a currency"""
    try:
        if not service.delete_currency(currency_id):
            raise HTTPException(status_code=404, detail="Currency not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/currencies/default/get", response_model=CurrencyResponse)
def get_default_currency(
    service: CurrencyService = Depends(get_currency_service)
):
    """Get the default currency"""
    currency = service.get_default_currency()
    if not currency:
        raise HTTPException(status_code=404, detail="No default currency set")
    return currency


# ==================== Exchange Rate Management ====================

@router.post("/exchange-rates", response_model=ExchangeRateResponse, status_code=201)
def create_exchange_rate(
    rate_data: ExchangeRateCreate,
    service: CurrencyService = Depends(get_currency_service)
):
    """
    Create a new exchange rate
    
    - **from_currency_code**: Source currency code
    - **to_currency_code**: Target currency code
    - **rate**: Exchange rate value
    - **source**: Source of the rate (e.g., "ECB", "Manual")
    - **valid_from**: Date from which the rate is valid
    - **valid_to**: Date until which the rate is valid (optional)
    - **is_active**: Whether the rate is active
    """
    try:
        return service.create_exchange_rate(rate_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/exchange-rates", response_model=List[ExchangeRateResponse])
def list_exchange_rates(
    currency_code: Optional[str] = Query(None, description="Filter by currency code"),
    active_only: bool = Query(True, description="Return only active rates"),
    service: CurrencyService = Depends(get_currency_service)
):
    """List exchange rates"""
    return service.list_exchange_rates(currency_code=currency_code, active_only=active_only)


@router.get("/exchange-rates/{from_currency}/{to_currency}", response_model=ExchangeRateResponse)
def get_exchange_rate(
    from_currency: str,
    to_currency: str,
    date: Optional[datetime] = Query(None, description="Date for historical rate"),
    service: CurrencyService = Depends(get_currency_service)
):
    """Get exchange rate between two currencies"""
    rate = service.get_exchange_rate(from_currency, to_currency, date)
    if not rate:
        raise HTTPException(
            status_code=404,
            detail=f"No exchange rate found for {from_currency}/{to_currency}"
        )
    return rate


@router.put("/exchange-rates/{rate_id}", response_model=ExchangeRateResponse)
def update_exchange_rate(
    rate_id: int,
    rate_data: ExchangeRateUpdate,
    service: CurrencyService = Depends(get_currency_service)
):
    """Update an exchange rate"""
    try:
        return service.update_exchange_rate(rate_id, rate_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Currency Conversion ====================

@router.post("/convert", response_model=CurrencyConversionResponse)
def convert_currency(
    request: CurrencyConversionRequest,
    service: CurrencyService = Depends(get_currency_service)
):
    """
    Convert amount from one currency to another
    
    - **amount**: Amount to convert
    - **from_currency**: Source currency code
    - **to_currency**: Target currency code
    - **date**: Date for historical rate (optional)
    """
    try:
        return service.convert_currency(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/multi-display", response_model=MultiCurrencyDisplayResponse)
def multi_currency_display(
    request: MultiCurrencyDisplayRequest,
    service: CurrencyService = Depends(get_currency_service)
):
    """
    Display amount in multiple currencies
    
    - **base_amount**: Base amount
    - **base_currency**: Base currency code
    - **target_currencies**: List of target currency codes
    """
    return service.multi_currency_display(request)


# ==================== Currency Rounding ====================

@router.post("/rounding-rules", response_model=CurrencyRoundingRuleResponse, status_code=201)
def create_rounding_rule(
    rule_data: CurrencyRoundingRuleCreate,
    service: CurrencyService = Depends(get_currency_service)
):
    """
    Create a currency rounding rule
    
    - **currency_code**: Currency code
    - **rounding_mode**: Rounding mode (ROUND_UP, ROUND_DOWN, ROUND_HALF_UP, etc.)
    - **rounding_precision**: Number of decimal places
    - **min_unit**: Minimum unit for rounding (e.g., 0.05 for 5-cent rounding)
    - **description**: Description of the rule
    """
    try:
        return service.create_rounding_rule(rule_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rounding-rules/{currency_code}", response_model=CurrencyRoundingRuleResponse)
def get_rounding_rule(
    currency_code: str,
    service: CurrencyService = Depends(get_currency_service)
):
    """Get rounding rule for a currency"""
    rule = service.get_rounding_rule(currency_code)
    if not rule:
        raise HTTPException(status_code=404, detail=f"No rounding rule found for {currency_code}")
    return rule


@router.post("/apply-rounding")
def apply_rounding(
    amount: float = Query(..., description="Amount to round"),
    currency_code: str = Query(..., description="Currency code"),
    service: CurrencyService = Depends(get_currency_service)
):
    """Apply currency-specific rounding to an amount"""
    rounded_amount = service.apply_rounding(amount, currency_code)
    return {
        "original_amount": amount,
        "rounded_amount": rounded_amount,
        "currency_code": currency_code
    }


# ==================== Exchange Rate History ====================

@router.get("/history/{from_currency}/{to_currency}")
def get_exchange_rate_history(
    from_currency: str,
    to_currency: str,
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    service: CurrencyService = Depends(get_currency_service)
):
    """Get historical exchange rates"""
    return service.get_exchange_rate_history(
        from_currency, to_currency, start_date, end_date, limit
    )


# ==================== Automatic Updates ====================

@router.post("/update-rates", response_model=CurrencyUpdateResponse)
def update_exchange_rates(
    request: CurrencyUpdateRequest,
    service: CurrencyService = Depends(get_currency_service)
):
    """
    Update exchange rates from external API
    
    - **source**: API source (optional)
    - **currencies**: Specific currencies to update (optional)
    - **force**: Force update even if recent data exists
    """
    return service.update_exchange_rates_from_api(request)


# ==================== Statistics ====================

@router.get("/statistics", response_model=CurrencyStatistics)
def get_statistics(
    service: CurrencyService = Depends(get_currency_service)
):
    """Get currency system statistics"""
    return service.get_statistics()
