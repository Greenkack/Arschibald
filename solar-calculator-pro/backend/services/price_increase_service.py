"""
Price Increase Service for Multi-PDF Generation

This service implements the critical price increase logic for multi-PDF generation.
When generating multiple offers for different companies, each subsequent offer should
be MORE EXPENSIVE than the previous one through automatic price increases.

Key Concept:
- Main Offer: Base price from Solar Calculator (e.g., 16.999,00 €)
- Second Offer: Base price + configured increase (e.g., +7%) = 18.188,93 €
- Third Offer: Previous price + configured increase (e.g., +7%) = 19.462,16 €
- Logic: ALWAYS apply increase rule, even if rotated products are cheaper/more expensive

Key Features:
- Configurable increase percentage (default: 7%)
- Cumulative or fixed increase strategies
- Price tracking across all offers
- German number formatting (16.999,00 €)
- Integration with product rotation system
- Price history and comparison
"""

import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.base_service import BaseService, HealthCheckResult, ServiceStatus
from backend.core.error_wrapper import handle_service_errors
from backend.core.logging_decorator import log_service_call
from backend.core.german_formatter import GermanNumberFormatter


class IncreaseStrategy(Enum):
    """Price increase strategies"""
    CUMULATIVE = "cumulative"  # Each offer increases from previous: base * (1 + rate)^n
    FIXED = "fixed"  # Each offer increases by fixed percentage from base: base * (1 + rate * n)
    STEPPED = "stepped"  # Stepped increases: 5%, 10%, 15%, etc.
    CUSTOM = "custom"  # Custom increase per offer


class PriceIncreaseService(BaseService):
    """
    Price Increase Service
    
    Manages automatic price increases for multi-PDF generation.
    Ensures each offer is more expensive than the previous one.
    """
    
    def __init__(self):
        super().__init__("price_increase")
        self._formatter = GermanNumberFormatter()
        self._base_price: Optional[Decimal] = None
        self._price_history: List[Dict[str, Any]] = []
        self._current_offer_index: int = 0
        
        # Default configuration
        self._config = {
            "default_increase_rate": Decimal("0.07"),  # 7%
            "strategy": IncreaseStrategy.CUMULATIVE.value,
            "min_increase_rate": Decimal("0.01"),  # 1%
            "max_increase_rate": Decimal("0.50"),  # 50%
            "custom_rates": []  # For custom strategy
        }
        
    def initialize(self) -> None:
        """Initialize the service"""
        try:
            self._set_initialized(True)
            self.logger.info("Price Increase Service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Price Increase Service: {e}")
            raise
    
    def health_check(self) -> HealthCheckResult:
        """Perform health check"""
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Service not initialized"
            )
        
        return HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="Service is healthy",
            details={
                "base_price": str(self._base_price) if self._base_price else None,
                "offers_generated": len(self._price_history),
                "current_strategy": self._config["strategy"]
            }
        )
    
    # ==================== Configuration Management ====================
    
    def set_increase_rate(self, rate: float) -> None:
        """
        Set the default increase rate.
        
        Args:
            rate: Increase rate as decimal (0.07 = 7%)
        """
        rate_decimal = Decimal(str(rate))
        
        if rate_decimal < self._config["min_increase_rate"]:
            raise ValueError(f"Increase rate must be at least {self._config['min_increase_rate']}")
        
        if rate_decimal > self._config["max_increase_rate"]:
            raise ValueError(f"Increase rate must not exceed {self._config['max_increase_rate']}")
        
        self._config["default_increase_rate"] = rate_decimal
        self.logger.info(f"Set increase rate to {rate_decimal * 100}%")
    
    def set_strategy(self, strategy: str) -> None:
        """
        Set the price increase strategy.
        
        Args:
            strategy: Strategy name (cumulative, fixed, stepped, custom)
        """
        try:
            strategy_enum = IncreaseStrategy(strategy)
            self._config["strategy"] = strategy_enum.value
            self.logger.info(f"Set increase strategy to {strategy}")
        except ValueError:
            raise ValueError(f"Invalid strategy: {strategy}")
    
    def set_custom_rates(self, rates: List[float]) -> None:
        """
        Set custom increase rates for each offer.
        
        Args:
            rates: List of increase rates (e.g., [0.05, 0.10, 0.15] for 5%, 10%, 15%)
        """
        self._config["custom_rates"] = [Decimal(str(rate)) for rate in rates]
        self.logger.info(f"Set custom rates: {rates}")
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration.
        
        Returns:
            Configuration dictionary
        """
        return {
            "default_increase_rate": float(self._config["default_increase_rate"]),
            "default_increase_percentage": f"{self._config['default_increase_rate'] * 100}%",
            "strategy": self._config["strategy"],
            "min_increase_rate": float(self._config["min_increase_rate"]),
            "max_increase_rate": float(self._config["max_increase_rate"]),
            "custom_rates": [float(rate) for rate in self._config["custom_rates"]]
        }
    
    # ==================== Price State Management ====================
    
    def reset_price_state(self) -> None:
        """Reset price state (clear base price and history)"""
        self._base_price = None
        self._price_history.clear()
        self._current_offer_index = 0
        self.logger.info("Reset price increase state")
    
    def set_base_price(self, price: float) -> None:
        """
        Set the base price from Solar Calculator.
        
        Args:
            price: Base price in euros
        """
        self._base_price = Decimal(str(price))
        self._current_offer_index = 0
        self._price_history.clear()
        
        # Record base price in history
        self._price_history.append({
            "offer_index": 0,
            "price": self._base_price,
            "price_formatted": self._formatter.format_currency(float(self._base_price)),
            "increase_rate": Decimal("0"),
            "increase_amount": Decimal("0"),
            "is_base": True,
            "timestamp": datetime.now().isoformat()
        })
        
        self.logger.info(f"Set base price to {self._formatter.format_currency(float(self._base_price))}")
    
    def get_price_history(self) -> List[Dict[str, Any]]:
        """
        Get price history for all offers.
        
        Returns:
            List of price records
        """
        return [
            {
                **record,
                "price": float(record["price"]),
                "increase_rate": float(record["increase_rate"]),
                "increase_amount": float(record["increase_amount"])
            }
            for record in self._price_history
        ]
    
    def get_current_price(self) -> Optional[float]:
        """
        Get the current (most recent) price.
        
        Returns:
            Current price or None if no price set
        """
        if not self._price_history:
            return None
        return float(self._price_history[-1]["price"])
    
    # ==================== Price Calculation ====================
    
    @log_service_call(service_name="price_increase", log_timing=True)
    @handle_service_errors(service_name="price_increase", error_message="Failed to calculate next price")
    def calculate_next_price(
        self,
        product_price: Optional[float] = None,
        custom_increase_rate: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate the next offer price with automatic increase.
        
        Args:
            product_price: Calculated price from rotated products (optional)
            custom_increase_rate: Custom increase rate for this offer (optional)
            
        Returns:
            Dictionary with price details
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        if self._base_price is None:
            raise RuntimeError("Base price not set. Call set_base_price() first.")
        
        # Increment offer index
        self._current_offer_index += 1
        
        # Determine increase rate
        if custom_increase_rate is not None:
            increase_rate = Decimal(str(custom_increase_rate))
        else:
            increase_rate = self._get_increase_rate_for_offer(self._current_offer_index)
        
        # Calculate new price based on strategy
        strategy = IncreaseStrategy(self._config["strategy"])
        
        if strategy == IncreaseStrategy.CUMULATIVE:
            # Each offer increases from previous: price * (1 + rate)
            previous_price = self._price_history[-1]["price"]
            new_price = previous_price * (Decimal("1") + increase_rate)
        
        elif strategy == IncreaseStrategy.FIXED:
            # Each offer increases by fixed percentage from base: base * (1 + rate * n)
            new_price = self._base_price * (Decimal("1") + increase_rate * self._current_offer_index)
        
        elif strategy == IncreaseStrategy.STEPPED:
            # Stepped increases: 5%, 10%, 15%, etc.
            step_rate = increase_rate * self._current_offer_index
            new_price = self._base_price * (Decimal("1") + step_rate)
        
        elif strategy == IncreaseStrategy.CUSTOM:
            # Use custom rate for this offer
            new_price = self._base_price * (Decimal("1") + increase_rate)
        
        else:
            # Default to cumulative
            previous_price = self._price_history[-1]["price"]
            new_price = previous_price * (Decimal("1") + increase_rate)
        
        # Round to 2 decimal places
        new_price = new_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Calculate increase amount
        previous_price = self._price_history[-1]["price"]
        increase_amount = new_price - previous_price
        
        # Record in history
        price_record = {
            "offer_index": self._current_offer_index,
            "price": new_price,
            "price_formatted": self._formatter.format_currency(float(new_price)),
            "increase_rate": increase_rate,
            "increase_rate_percentage": f"{increase_rate * 100}%",
            "increase_amount": increase_amount,
            "increase_amount_formatted": self._formatter.format_currency(float(increase_amount)),
            "previous_price": previous_price,
            "previous_price_formatted": self._formatter.format_currency(float(previous_price)),
            "base_price": self._base_price,
            "base_price_formatted": self._formatter.format_currency(float(self._base_price)),
            "product_price": Decimal(str(product_price)) if product_price else None,
            "strategy": strategy.value,
            "is_base": False,
            "timestamp": datetime.now().isoformat()
        }
        
        self._price_history.append(price_record)
        
        self.logger.info(
            f"Calculated price for offer {self._current_offer_index}: "
            f"{self._formatter.format_currency(float(new_price))} "
            f"(+{increase_rate * 100}% from previous)"
        )
        
        # Return formatted result
        return {
            "offer_index": self._current_offer_index,
            "price": float(new_price),
            "price_formatted": self._formatter.format_currency(float(new_price)),
            "increase_rate": float(increase_rate),
            "increase_rate_percentage": f"{increase_rate * 100}%",
            "increase_amount": float(increase_amount),
            "increase_amount_formatted": self._formatter.format_currency(float(increase_amount)),
            "previous_price": float(previous_price),
            "previous_price_formatted": self._formatter.format_currency(float(previous_price)),
            "base_price": float(self._base_price),
            "base_price_formatted": self._formatter.format_currency(float(self._base_price)),
            "strategy": strategy.value
        }
    
    @log_service_call(service_name="price_increase", log_timing=True)
    @handle_service_errors(service_name="price_increase", error_message="Failed to calculate price for offer")
    def calculate_price_for_offer(
        self,
        offer_index: int,
        product_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate price for a specific offer index.
        
        Args:
            offer_index: Offer index (1, 2, 3, ...)
            product_price: Calculated price from rotated products (optional)
            
        Returns:
            Dictionary with price details
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        if self._base_price is None:
            raise RuntimeError("Base price not set. Call set_base_price() first.")
        
        if offer_index < 1:
            raise ValueError("Offer index must be >= 1")
        
        # Calculate increase rate for this offer
        increase_rate = self._get_increase_rate_for_offer(offer_index)
        
        # Calculate price based on strategy
        strategy = IncreaseStrategy(self._config["strategy"])
        
        if strategy == IncreaseStrategy.CUMULATIVE:
            # Cumulative: base * (1 + rate)^n
            new_price = self._base_price * ((Decimal("1") + increase_rate) ** offer_index)
        
        elif strategy == IncreaseStrategy.FIXED:
            # Fixed: base * (1 + rate * n)
            new_price = self._base_price * (Decimal("1") + increase_rate * offer_index)
        
        elif strategy == IncreaseStrategy.STEPPED:
            # Stepped: base * (1 + rate * n)
            step_rate = increase_rate * offer_index
            new_price = self._base_price * (Decimal("1") + step_rate)
        
        elif strategy == IncreaseStrategy.CUSTOM:
            # Custom: use specific rate for this offer
            if offer_index <= len(self._config["custom_rates"]):
                custom_rate = self._config["custom_rates"][offer_index - 1]
                new_price = self._base_price * (Decimal("1") + custom_rate)
            else:
                # Fallback to default rate
                new_price = self._base_price * (Decimal("1") + increase_rate * offer_index)
        
        else:
            # Default to cumulative
            new_price = self._base_price * ((Decimal("1") + increase_rate) ** offer_index)
        
        # Round to 2 decimal places
        new_price = new_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Calculate increase from base
        increase_amount = new_price - self._base_price
        
        return {
            "offer_index": offer_index,
            "price": float(new_price),
            "price_formatted": self._formatter.format_currency(float(new_price)),
            "increase_rate": float(increase_rate),
            "increase_rate_percentage": f"{increase_rate * 100}%",
            "increase_amount": float(increase_amount),
            "increase_amount_formatted": self._formatter.format_currency(float(increase_amount)),
            "base_price": float(self._base_price),
            "base_price_formatted": self._formatter.format_currency(float(self._base_price)),
            "strategy": strategy.value
        }
    
    @log_service_call(service_name="price_increase", log_timing=True)
    @handle_service_errors(service_name="price_increase", error_message="Failed to calculate all prices")
    def calculate_all_prices(
        self,
        num_offers: int,
        product_prices: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculate prices for all offers at once.
        
        Args:
            num_offers: Number of offers to generate
            product_prices: List of calculated prices from rotated products (optional)
            
        Returns:
            List of price details for each offer
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        if self._base_price is None:
            raise RuntimeError("Base price not set. Call set_base_price() first.")
        
        if num_offers < 1:
            raise ValueError("Number of offers must be >= 1")
        
        prices = []
        
        # Include base price (offer 0)
        prices.append({
            "offer_index": 0,
            "price": float(self._base_price),
            "price_formatted": self._formatter.format_currency(float(self._base_price)),
            "increase_rate": 0.0,
            "increase_rate_percentage": "0%",
            "increase_amount": 0.0,
            "increase_amount_formatted": self._formatter.format_currency(0.0),
            "base_price": float(self._base_price),
            "base_price_formatted": self._formatter.format_currency(float(self._base_price)),
            "is_base": True,
            "strategy": self._config["strategy"]
        })
        
        # Calculate prices for each offer
        for i in range(1, num_offers + 1):
            product_price = product_prices[i - 1] if product_prices and i - 1 < len(product_prices) else None
            price_info = self.calculate_price_for_offer(i, product_price)
            prices.append(price_info)
        
        self.logger.info(f"Calculated prices for {num_offers} offers")
        
        return prices
    
    # ==================== Price Comparison ====================
    
    @log_service_call(service_name="price_increase", log_timing=True)
    @handle_service_errors(service_name="price_increase", error_message="Failed to generate comparison")
    def generate_price_comparison(self) -> Dict[str, Any]:
        """
        Generate a comparison of all prices in history.
        
        Returns:
            Comparison report with statistics
        """
        if not self._price_history:
            return {
                "total_offers": 0,
                "base_price": None,
                "current_price": None,
                "total_increase": None,
                "average_increase_rate": None,
                "prices": []
            }
        
        base_price = self._price_history[0]["price"]
        current_price = self._price_history[-1]["price"]
        total_increase = current_price - base_price
        
        # Calculate average increase rate
        if len(self._price_history) > 1:
            total_rate = sum(
                record["increase_rate"] 
                for record in self._price_history[1:]
            )
            avg_rate = total_rate / (len(self._price_history) - 1)
        else:
            avg_rate = Decimal("0")
        
        return {
            "total_offers": len(self._price_history) - 1,  # Exclude base
            "base_price": float(base_price),
            "base_price_formatted": self._formatter.format_currency(float(base_price)),
            "current_price": float(current_price),
            "current_price_formatted": self._formatter.format_currency(float(current_price)),
            "total_increase": float(total_increase),
            "total_increase_formatted": self._formatter.format_currency(float(total_increase)),
            "total_increase_percentage": f"{(total_increase / base_price * 100):.2f}%",
            "average_increase_rate": float(avg_rate),
            "average_increase_percentage": f"{avg_rate * 100:.2f}%",
            "strategy": self._config["strategy"],
            "prices": self.get_price_history()
        }
    
    # ==================== Helper Methods ====================
    
    def _get_increase_rate_for_offer(self, offer_index: int) -> Decimal:
        """Get the increase rate for a specific offer index"""
        strategy = IncreaseStrategy(self._config["strategy"])
        
        if strategy == IncreaseStrategy.CUSTOM:
            # Use custom rate if available
            if offer_index <= len(self._config["custom_rates"]):
                return self._config["custom_rates"][offer_index - 1]
        
        # Use default rate
        return self._config["default_increase_rate"]


# Singleton instance
_price_increase_service = None


def get_price_increase_service() -> PriceIncreaseService:
    """Get singleton instance of Price Increase Service"""
    global _price_increase_service
    if _price_increase_service is None:
        _price_increase_service = PriceIncreaseService()
        _price_increase_service.initialize()
    return _price_increase_service
