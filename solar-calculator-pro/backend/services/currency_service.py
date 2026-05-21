"""
Currency Service

This service handles all currency-related operations including:
- Currency management
- Exchange rate management
- Currency conversion
- Multi-currency display
- Currency-specific rounding
- Exchange rate history
- Automatic currency updates
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP, ROUND_DOWN, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_DOWN
import requests
from backend.models.currency_models import (
    Currency, ExchangeRate, ExchangeRateHistory, 
    CurrencyRoundingRule, CurrencyUpdateLog
)
from backend.models.currency_schemas import (
    CurrencyCreate, CurrencyUpdate, CurrencyResponse,
    ExchangeRateCreate, ExchangeRateUpdate, ExchangeRateResponse,
    CurrencyConversionRequest, CurrencyConversionResponse,
    MultiCurrencyDisplayRequest, MultiCurrencyDisplayResponse,
    CurrencyRoundingRuleCreate, CurrencyRoundingRuleUpdate,
    CurrencyUpdateRequest, CurrencyUpdateResponse,
    CurrencyStatistics
)


class CurrencyService:
    """Service for currency operations"""
    
    # Rounding mode mapping
    ROUNDING_MODES = {
        "ROUND_UP": ROUND_UP,
        "ROUND_DOWN": ROUND_DOWN,
        "ROUND_HALF_UP": ROUND_HALF_UP,
        "ROUND_HALF_DOWN": ROUND_HALF_DOWN,
        "ROUND_CEILING": ROUND_CEILING,
        "ROUND_FLOOR": ROUND_FLOOR
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== Currency Management ====================
    
    def create_currency(self, currency_data: CurrencyCreate) -> CurrencyResponse:
        """Create a new currency"""
        # Check if currency already exists
        existing = self.db.query(Currency).filter(Currency.code == currency_data.code).first()
        if existing:
            raise ValueError(f"Currency {currency_data.code} already exists")
        
        # If this is set as default, unset other defaults
        if currency_data.is_default:
            self.db.query(Currency).filter(Currency.is_default == True).update({"is_default": False})
        
        currency = Currency(**currency_data.dict())
        self.db.add(currency)
        self.db.commit()
        self.db.refresh(currency)
        
        return CurrencyResponse.from_orm(currency)
    
    def get_currency(self, currency_id: int) -> Optional[CurrencyResponse]:
        """Get currency by ID"""
        currency = self.db.query(Currency).filter(Currency.id == currency_id).first()
        return CurrencyResponse.from_orm(currency) if currency else None
    
    def get_currency_by_code(self, code: str) -> Optional[CurrencyResponse]:
        """Get currency by code"""
        currency = self.db.query(Currency).filter(Currency.code == code.upper()).first()
        return CurrencyResponse.from_orm(currency) if currency else None
    
    def list_currencies(self, active_only: bool = False) -> List[CurrencyResponse]:
        """List all currencies"""
        query = self.db.query(Currency)
        if active_only:
            query = query.filter(Currency.is_active == True)
        currencies = query.all()
        return [CurrencyResponse.from_orm(c) for c in currencies]
    
    def update_currency(self, currency_id: int, currency_data: CurrencyUpdate) -> CurrencyResponse:
        """Update a currency"""
        currency = self.db.query(Currency).filter(Currency.id == currency_id).first()
        if not currency:
            raise ValueError(f"Currency with ID {currency_id} not found")
        
        # If setting as default, unset other defaults
        if currency_data.is_default:
            self.db.query(Currency).filter(Currency.is_default == True).update({"is_default": False})
        
        for key, value in currency_data.dict(exclude_unset=True).items():
            setattr(currency, key, value)
        
        currency.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(currency)
        
        return CurrencyResponse.from_orm(currency)
    
    def delete_currency(self, currency_id: int) -> bool:
        """Delete a currency"""
        currency = self.db.query(Currency).filter(Currency.id == currency_id).first()
        if not currency:
            return False
        
        # Check if currency is used in exchange rates
        rates_count = self.db.query(ExchangeRate).filter(
            or_(
                ExchangeRate.from_currency_id == currency_id,
                ExchangeRate.to_currency_id == currency_id
            )
        ).count()
        
        if rates_count > 0:
            raise ValueError(f"Cannot delete currency {currency.code} - it is used in {rates_count} exchange rates")
        
        self.db.delete(currency)
        self.db.commit()
        return True
    
    def get_default_currency(self) -> Optional[CurrencyResponse]:
        """Get the default currency"""
        currency = self.db.query(Currency).filter(Currency.is_default == True).first()
        return CurrencyResponse.from_orm(currency) if currency else None
    
    # ==================== Exchange Rate Management ====================
    
    def create_exchange_rate(self, rate_data: ExchangeRateCreate) -> ExchangeRateResponse:
        """Create a new exchange rate"""
        # Get currency IDs
        from_currency = self.db.query(Currency).filter(Currency.code == rate_data.from_currency_code).first()
        to_currency = self.db.query(Currency).filter(Currency.code == rate_data.to_currency_code).first()
        
        if not from_currency or not to_currency:
            raise ValueError("One or both currencies not found")
        
        # Deactivate existing active rates for this pair
        self.db.query(ExchangeRate).filter(
            and_(
                ExchangeRate.from_currency_id == from_currency.id,
                ExchangeRate.to_currency_id == to_currency.id,
                ExchangeRate.is_active == True
            )
        ).update({"is_active": False})
        
        rate = ExchangeRate(
            from_currency_id=from_currency.id,
            to_currency_id=to_currency.id,
            rate=rate_data.rate,
            source=rate_data.source,
            valid_from=rate_data.valid_from,
            valid_to=rate_data.valid_to,
            is_active=rate_data.is_active
        )
        
        self.db.add(rate)
        self.db.commit()
        self.db.refresh(rate)
        
        # Add to history
        self._add_to_history(rate_data.from_currency_code, rate_data.to_currency_code, rate_data.rate, rate_data.source)
        
        return self._exchange_rate_to_response(rate)
    
    def get_exchange_rate(self, from_currency: str, to_currency: str, date: Optional[datetime] = None) -> Optional[ExchangeRateResponse]:
        """Get exchange rate between two currencies"""
        from_curr = self.db.query(Currency).filter(Currency.code == from_currency.upper()).first()
        to_curr = self.db.query(Currency).filter(Currency.code == to_currency.upper()).first()
        
        if not from_curr or not to_curr:
            return None
        
        query = self.db.query(ExchangeRate).filter(
            and_(
                ExchangeRate.from_currency_id == from_curr.id,
                ExchangeRate.to_currency_id == to_curr.id,
                ExchangeRate.is_active == True
            )
        )
        
        if date:
            query = query.filter(
                and_(
                    ExchangeRate.valid_from <= date,
                    or_(ExchangeRate.valid_to.is_(None), ExchangeRate.valid_to >= date)
                )
            )
        
        rate = query.first()
        return self._exchange_rate_to_response(rate) if rate else None
    
    def list_exchange_rates(self, currency_code: Optional[str] = None, active_only: bool = True) -> List[ExchangeRateResponse]:
        """List exchange rates"""
        query = self.db.query(ExchangeRate)
        
        if currency_code:
            currency = self.db.query(Currency).filter(Currency.code == currency_code.upper()).first()
            if currency:
                query = query.filter(
                    or_(
                        ExchangeRate.from_currency_id == currency.id,
                        ExchangeRate.to_currency_id == currency.id
                    )
                )
        
        if active_only:
            query = query.filter(ExchangeRate.is_active == True)
        
        rates = query.all()
        return [self._exchange_rate_to_response(r) for r in rates]
    
    def update_exchange_rate(self, rate_id: int, rate_data: ExchangeRateUpdate) -> ExchangeRateResponse:
        """Update an exchange rate"""
        rate = self.db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()
        if not rate:
            raise ValueError(f"Exchange rate with ID {rate_id} not found")
        
        for key, value in rate_data.dict(exclude_unset=True).items():
            setattr(rate, key, value)
        
        rate.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(rate)
        
        # Add to history if rate changed
        if rate_data.rate is not None:
            self._add_to_history(
                rate.from_currency.code,
                rate.to_currency.code,
                rate.rate,
                rate.source
            )
        
        return self._exchange_rate_to_response(rate)
    
    # ==================== Currency Conversion ====================
    
    def convert_currency(self, request: CurrencyConversionRequest) -> CurrencyConversionResponse:
        """Convert amount from one currency to another"""
        # Handle same currency
        if request.from_currency == request.to_currency:
            return CurrencyConversionResponse(
                original_amount=request.amount,
                converted_amount=request.amount,
                from_currency=request.from_currency,
                to_currency=request.to_currency,
                exchange_rate=1.0,
                conversion_date=request.date or datetime.utcnow(),
                source="same_currency"
            )
        
        # Get exchange rate
        rate_response = self.get_exchange_rate(request.from_currency, request.to_currency, request.date)
        
        if not rate_response:
            # Try reverse rate
            reverse_rate = self.get_exchange_rate(request.to_currency, request.from_currency, request.date)
            if reverse_rate:
                rate = 1.0 / reverse_rate.rate
                source = reverse_rate.source
            else:
                raise ValueError(f"No exchange rate found for {request.from_currency}/{request.to_currency}")
        else:
            rate = rate_response.rate
            source = rate_response.source
        
        # Convert
        converted_amount = request.amount * rate
        
        # Apply rounding
        to_currency = self.get_currency_by_code(request.to_currency)
        if to_currency:
            converted_amount = self.apply_rounding(converted_amount, request.to_currency)
        
        return CurrencyConversionResponse(
            original_amount=request.amount,
            converted_amount=converted_amount,
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            exchange_rate=rate,
            conversion_date=request.date or datetime.utcnow(),
            source=source
        )
    
    def multi_currency_display(self, request: MultiCurrencyDisplayRequest) -> MultiCurrencyDisplayResponse:
        """Display amount in multiple currencies"""
        conversions = []
        
        for target_currency in request.target_currencies:
            try:
                conversion = self.convert_currency(
                    CurrencyConversionRequest(
                        amount=request.base_amount,
                        from_currency=request.base_currency,
                        to_currency=target_currency
                    )
                )
                conversions.append(conversion)
            except Exception as e:
                # Skip currencies that fail conversion
                continue
        
        return MultiCurrencyDisplayResponse(
            base_amount=request.base_amount,
            base_currency=request.base_currency,
            conversions=conversions
        )
    
    # ==================== Currency Rounding ====================
    
    def create_rounding_rule(self, rule_data: CurrencyRoundingRuleCreate) -> CurrencyRoundingRuleResponse:
        """Create a currency rounding rule"""
        currency = self.db.query(Currency).filter(Currency.code == rule_data.currency_code).first()
        if not currency:
            raise ValueError(f"Currency {rule_data.currency_code} not found")
        
        # Check if rule already exists
        existing = self.db.query(CurrencyRoundingRule).filter(
            CurrencyRoundingRule.currency_id == currency.id
        ).first()
        
        if existing:
            raise ValueError(f"Rounding rule for {rule_data.currency_code} already exists")
        
        rule = CurrencyRoundingRule(
            currency_id=currency.id,
            rounding_mode=rule_data.rounding_mode,
            rounding_precision=rule_data.rounding_precision,
            min_unit=rule_data.min_unit,
            description=rule_data.description
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        return self._rounding_rule_to_response(rule)
    
    def get_rounding_rule(self, currency_code: str) -> Optional[CurrencyRoundingRuleResponse]:
        """Get rounding rule for a currency"""
        currency = self.db.query(Currency).filter(Currency.code == currency_code.upper()).first()
        if not currency:
            return None
        
        rule = self.db.query(CurrencyRoundingRule).filter(
            CurrencyRoundingRule.currency_id == currency.id
        ).first()
        
        return self._rounding_rule_to_response(rule) if rule else None
    
    def apply_rounding(self, amount: float, currency_code: str) -> float:
        """Apply currency-specific rounding to an amount"""
        rule = self.get_rounding_rule(currency_code)
        
        if not rule:
            # Use default rounding (2 decimal places, ROUND_HALF_UP)
            return round(amount, 2)
        
        decimal_amount = Decimal(str(amount))
        rounding_mode = self.ROUNDING_MODES.get(rule.rounding_mode, ROUND_HALF_UP)
        
        # Apply minimum unit rounding if specified
        if rule.min_unit:
            min_unit_decimal = Decimal(str(rule.min_unit))
            rounded = (decimal_amount / min_unit_decimal).quantize(Decimal('1'), rounding=rounding_mode) * min_unit_decimal
        else:
            # Apply precision rounding
            quantize_str = '0.' + '0' * rule.rounding_precision if rule.rounding_precision > 0 else '1'
            rounded = decimal_amount.quantize(Decimal(quantize_str), rounding=rounding_mode)
        
        return float(rounded)
    
    # ==================== Exchange Rate History ====================
    
    def get_exchange_rate_history(
        self, 
        from_currency: str, 
        to_currency: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get historical exchange rates"""
        query = self.db.query(ExchangeRateHistory).filter(
            and_(
                ExchangeRateHistory.from_currency_code == from_currency.upper(),
                ExchangeRateHistory.to_currency_code == to_currency.upper()
            )
        )
        
        if start_date:
            query = query.filter(ExchangeRateHistory.timestamp >= start_date)
        if end_date:
            query = query.filter(ExchangeRateHistory.timestamp <= end_date)
        
        history = query.order_by(desc(ExchangeRateHistory.timestamp)).limit(limit).all()
        
        return [
            {
                "from_currency": h.from_currency_code,
                "to_currency": h.to_currency_code,
                "rate": h.rate,
                "source": h.source,
                "timestamp": h.timestamp
            }
            for h in history
        ]
    
    def _add_to_history(self, from_currency: str, to_currency: str, rate: float, source: Optional[str]):
        """Add exchange rate to history"""
        history = ExchangeRateHistory(
            from_currency_code=from_currency.upper(),
            to_currency_code=to_currency.upper(),
            rate=rate,
            source=source,
            timestamp=datetime.utcnow()
        )
        self.db.add(history)
        self.db.commit()
    
    # ==================== Automatic Updates ====================
    
    def update_exchange_rates_from_api(self, request: CurrencyUpdateRequest) -> CurrencyUpdateResponse:
        """Update exchange rates from external API"""
        started_at = datetime.utcnow()
        currencies_updated = 0
        rates_updated = 0
        error_message = None
        
        try:
            # This is a placeholder - implement actual API integration
            # Example: European Central Bank API, OpenExchangeRates, etc.
            
            # For demonstration, we'll use a mock update
            base_currency = "EUR"
            rates = self._fetch_rates_from_api(request.source or "ECB")
            
            for currency_code, rate in rates.items():
                try:
                    # Create or update exchange rate
                    self.create_exchange_rate(
                        ExchangeRateCreate(
                            from_currency_code=base_currency,
                            to_currency_code=currency_code,
                            rate=rate,
                            source=request.source or "ECB",
                            valid_from=datetime.utcnow(),
                            is_active=True
                        )
                    )
                    rates_updated += 1
                except Exception as e:
                    continue
            
            status = "success"
            currencies_updated = len(rates)
            
        except Exception as e:
            status = "failed"
            error_message = str(e)
        
        completed_at = datetime.utcnow()
        
        # Log the update
        log = CurrencyUpdateLog(
            update_type="automatic" if not request.source else "api",
            source=request.source,
            currencies_updated=currencies_updated,
            rates_updated=rates_updated,
            status=status,
            error_message=error_message,
            started_at=started_at,
            completed_at=completed_at
        )
        self.db.add(log)
        self.db.commit()
        
        return CurrencyUpdateResponse(
            update_type=log.update_type,
            source=log.source,
            currencies_updated=currencies_updated,
            rates_updated=rates_updated,
            status=status,
            error_message=error_message,
            started_at=started_at,
            completed_at=completed_at
        )
    
    def _fetch_rates_from_api(self, source: str) -> Dict[str, float]:
        """Fetch exchange rates from external API"""
        # This is a placeholder - implement actual API integration
        # For now, return mock data
        return {
            "USD": 1.08,
            "GBP": 0.86,
            "CHF": 0.95,
            "JPY": 161.50,
            "CNY": 7.85
        }
    
    # ==================== Statistics ====================
    
    def get_statistics(self) -> CurrencyStatistics:
        """Get currency system statistics"""
        total_currencies = self.db.query(Currency).count()
        active_currencies = self.db.query(Currency).filter(Currency.is_active == True).count()
        total_rates = self.db.query(ExchangeRate).count()
        active_rates = self.db.query(ExchangeRate).filter(ExchangeRate.is_active == True).count()
        
        last_update_log = self.db.query(CurrencyUpdateLog).order_by(
            desc(CurrencyUpdateLog.completed_at)
        ).first()
        
        default_currency = self.db.query(Currency).filter(Currency.is_default == True).first()
        
        return CurrencyStatistics(
            total_currencies=total_currencies,
            active_currencies=active_currencies,
            total_exchange_rates=total_rates,
            active_exchange_rates=active_rates,
            last_update=last_update_log.completed_at if last_update_log else None,
            default_currency=default_currency.code if default_currency else None
        )
    
    # ==================== Helper Methods ====================
    
    def _exchange_rate_to_response(self, rate: ExchangeRate) -> ExchangeRateResponse:
        """Convert ExchangeRate model to response schema"""
        return ExchangeRateResponse(
            id=rate.id,
            from_currency_code=rate.from_currency.code,
            to_currency_code=rate.to_currency.code,
            rate=rate.rate,
            source=rate.source,
            valid_from=rate.valid_from,
            valid_to=rate.valid_to,
            is_active=rate.is_active,
            created_at=rate.created_at,
            updated_at=rate.updated_at
        )
    
    def _rounding_rule_to_response(self, rule: CurrencyRoundingRule) -> CurrencyRoundingRuleResponse:
        """Convert CurrencyRoundingRule model to response schema"""
        return CurrencyRoundingRuleResponse(
            id=rule.id,
            currency_code=rule.currency.code,
            rounding_mode=rule.rounding_mode,
            rounding_precision=rule.rounding_precision,
            min_unit=rule.min_unit,
            description=rule.description,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
