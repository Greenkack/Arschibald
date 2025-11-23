"""
Price Increase API Endpoints

Provides REST API endpoints for the Price Increase Service.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.services.price_increase_service import get_price_increase_service, IncreaseStrategy


router = APIRouter(prefix="/price-increase", tags=["price-increase"])


# ==================== Request/Response Models ====================

class SetBasePriceRequest(BaseModel):
    """Request to set base price"""
    price: float = Field(..., gt=0, description="Base price in euros")


class SetIncreaseRateRequest(BaseModel):
    """Request to set increase rate"""
    rate: float = Field(..., ge=0.01, le=0.50, description="Increase rate (0.07 = 7%)")


class SetStrategyRequest(BaseModel):
    """Request to set increase strategy"""
    strategy: str = Field(..., description="Strategy: cumulative, fixed, stepped, custom")


class SetCustomRatesRequest(BaseModel):
    """Request to set custom rates"""
    rates: List[float] = Field(..., description="List of increase rates for each offer")


class CalculateNextPriceRequest(BaseModel):
    """Request to calculate next price"""
    product_price: Optional[float] = Field(None, description="Calculated price from rotated products")
    custom_increase_rate: Optional[float] = Field(None, description="Custom increase rate for this offer")


class CalculatePriceForOfferRequest(BaseModel):
    """Request to calculate price for specific offer"""
    offer_index: int = Field(..., ge=1, description="Offer index (1, 2, 3, ...)")
    product_price: Optional[float] = Field(None, description="Calculated price from rotated products")


class CalculateAllPricesRequest(BaseModel):
    """Request to calculate all prices"""
    num_offers: int = Field(..., ge=1, le=100, description="Number of offers to generate")
    product_prices: Optional[List[float]] = Field(None, description="List of product prices")


class PriceResponse(BaseModel):
    """Price calculation response"""
    offer_index: int
    price: float
    price_formatted: str
    increase_rate: float
    increase_rate_percentage: str
    increase_amount: float
    increase_amount_formatted: str
    base_price: float
    base_price_formatted: str
    strategy: str
    previous_price: Optional[float] = None
    previous_price_formatted: Optional[str] = None


class ConfigurationResponse(BaseModel):
    """Configuration response"""
    default_increase_rate: float
    default_increase_percentage: str
    strategy: str
    min_increase_rate: float
    max_increase_rate: float
    custom_rates: List[float]


class PriceHistoryResponse(BaseModel):
    """Price history response"""
    total_offers: int
    prices: List[Dict[str, Any]]


class PriceComparisonResponse(BaseModel):
    """Price comparison response"""
    total_offers: int
    base_price: Optional[float]
    base_price_formatted: Optional[str]
    current_price: Optional[float]
    current_price_formatted: Optional[str]
    total_increase: Optional[float]
    total_increase_formatted: Optional[str]
    total_increase_percentage: Optional[str]
    average_increase_rate: Optional[float]
    average_increase_percentage: Optional[str]
    strategy: str
    prices: List[Dict[str, Any]]


# ==================== Configuration Endpoints ====================

@router.get("/configuration", response_model=ConfigurationResponse)
async def get_configuration():
    """
    Get current price increase configuration.
    
    Returns:
        Current configuration including increase rate and strategy
    """
    try:
        service = get_price_increase_service()
        config = service.get_configuration()
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration: {str(e)}"
        )


@router.post("/configuration/increase-rate")
async def set_increase_rate(request: SetIncreaseRateRequest):
    """
    Set the default increase rate.
    
    Args:
        request: Increase rate (0.07 = 7%)
        
    Returns:
        Success message
    """
    try:
        service = get_price_increase_service()
        service.set_increase_rate(request.rate)
        return {
            "message": f"Increase rate set to {request.rate * 100}%",
            "rate": request.rate
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set increase rate: {str(e)}"
        )


@router.post("/configuration/strategy")
async def set_strategy(request: SetStrategyRequest):
    """
    Set the price increase strategy.
    
    Args:
        request: Strategy name (cumulative, fixed, stepped, custom)
        
    Returns:
        Success message
    """
    try:
        service = get_price_increase_service()
        service.set_strategy(request.strategy)
        return {
            "message": f"Strategy set to {request.strategy}",
            "strategy": request.strategy
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set strategy: {str(e)}"
        )


@router.post("/configuration/custom-rates")
async def set_custom_rates(request: SetCustomRatesRequest):
    """
    Set custom increase rates for each offer.
    
    Args:
        request: List of increase rates
        
    Returns:
        Success message
    """
    try:
        service = get_price_increase_service()
        service.set_custom_rates(request.rates)
        return {
            "message": f"Custom rates set for {len(request.rates)} offers",
            "rates": request.rates
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set custom rates: {str(e)}"
        )


# ==================== Price State Endpoints ====================

@router.post("/reset")
async def reset_price_state():
    """
    Reset price state (clear base price and history).
    
    Returns:
        Success message
    """
    try:
        service = get_price_increase_service()
        service.reset_price_state()
        return {"message": "Price state reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset price state: {str(e)}"
        )


@router.post("/base-price")
async def set_base_price(request: SetBasePriceRequest):
    """
    Set the base price from Solar Calculator.
    
    Args:
        request: Base price in euros
        
    Returns:
        Success message with formatted price
    """
    try:
        service = get_price_increase_service()
        service.set_base_price(request.price)
        
        from backend.core.german_formatter import GermanNumberFormatter
        formatter = GermanNumberFormatter()
        
        return {
            "message": "Base price set successfully",
            "price": request.price,
            "price_formatted": formatter.format_currency(request.price)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set base price: {str(e)}"
        )


@router.get("/history", response_model=PriceHistoryResponse)
async def get_price_history():
    """
    Get price history for all offers.
    
    Returns:
        List of price records
    """
    try:
        service = get_price_increase_service()
        history = service.get_price_history()
        return {
            "total_offers": len(history) - 1 if history else 0,  # Exclude base
            "prices": history
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get price history: {str(e)}"
        )


@router.get("/current-price")
async def get_current_price():
    """
    Get the current (most recent) price.
    
    Returns:
        Current price or null if no price set
    """
    try:
        service = get_price_increase_service()
        price = service.get_current_price()
        
        if price is None:
            return {"price": None, "price_formatted": None}
        
        from backend.core.german_formatter import GermanNumberFormatter
        formatter = GermanNumberFormatter()
        
        return {
            "price": price,
            "price_formatted": formatter.format_currency(price)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current price: {str(e)}"
        )


# ==================== Price Calculation Endpoints ====================

@router.post("/calculate-next", response_model=PriceResponse)
async def calculate_next_price(request: CalculateNextPriceRequest):
    """
    Calculate the next offer price with automatic increase.
    
    Args:
        request: Optional product price and custom increase rate
        
    Returns:
        Price details for next offer
    """
    try:
        service = get_price_increase_service()
        result = service.calculate_next_price(
            product_price=request.product_price,
            custom_increase_rate=request.custom_increase_rate
        )
        return result
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate next price: {str(e)}"
        )


@router.post("/calculate-for-offer", response_model=PriceResponse)
async def calculate_price_for_offer(request: CalculatePriceForOfferRequest):
    """
    Calculate price for a specific offer index.
    
    Args:
        request: Offer index and optional product price
        
    Returns:
        Price details for specified offer
    """
    try:
        service = get_price_increase_service()
        result = service.calculate_price_for_offer(
            offer_index=request.offer_index,
            product_price=request.product_price
        )
        return result
    except (RuntimeError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate price for offer: {str(e)}"
        )


@router.post("/calculate-all")
async def calculate_all_prices(request: CalculateAllPricesRequest):
    """
    Calculate prices for all offers at once.
    
    Args:
        request: Number of offers and optional product prices
        
    Returns:
        List of price details for each offer
    """
    try:
        service = get_price_increase_service()
        result = service.calculate_all_prices(
            num_offers=request.num_offers,
            product_prices=request.product_prices
        )
        return {
            "total_offers": len(result) - 1,  # Exclude base
            "prices": result
        }
    except (RuntimeError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate all prices: {str(e)}"
        )


# ==================== Comparison Endpoints ====================

@router.get("/comparison", response_model=PriceComparisonResponse)
async def generate_price_comparison():
    """
    Generate a comparison of all prices in history.
    
    Returns:
        Comparison report with statistics
    """
    try:
        service = get_price_increase_service()
        result = service.generate_price_comparison()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate price comparison: {str(e)}"
        )


# ==================== Health Check ====================

@router.get("/health")
async def health_check():
    """
    Check service health.
    
    Returns:
        Health status
    """
    try:
        service = get_price_increase_service()
        health = service.health_check()
        return {
            "status": health.status.value,
            "message": health.message,
            "details": health.details
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )
