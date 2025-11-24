"""
Currency Database Models

This module defines the database models for multi-currency support in the price matrix system.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class Currency(Base):
    """Currency model for supported currencies"""
    __tablename__ = "currencies"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, nullable=False, index=True)  # ISO 4217 code (EUR, USD, GBP, etc.)
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=False)  # €, $, £, etc.
    decimal_places = Column(Integer, default=2)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exchange_rates_from = relationship("ExchangeRate", foreign_keys="ExchangeRate.from_currency_id", back_populates="from_currency")
    exchange_rates_to = relationship("ExchangeRate", foreign_keys="ExchangeRate.to_currency_id", back_populates="to_currency")
    
    def __repr__(self):
        return f"<Currency {self.code} - {self.name}>"


class ExchangeRate(Base):
    """Exchange rate model for currency conversions"""
    __tablename__ = "exchange_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    from_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    to_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    rate = Column(Float, nullable=False)  # Conversion rate
    source = Column(String(100))  # API source (e.g., "ECB", "OpenExchangeRates")
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    from_currency = relationship("Currency", foreign_keys=[from_currency_id], back_populates="exchange_rates_from")
    to_currency = relationship("Currency", foreign_keys=[to_currency_id], back_populates="exchange_rates_to")
    
    def __repr__(self):
        return f"<ExchangeRate {self.from_currency.code}/{self.to_currency.code} = {self.rate}>"


class ExchangeRateHistory(Base):
    """Historical exchange rates for tracking and analysis"""
    __tablename__ = "exchange_rate_history"
    
    id = Column(Integer, primary_key=True, index=True)
    from_currency_code = Column(String(3), nullable=False, index=True)
    to_currency_code = Column(String(3), nullable=False, index=True)
    rate = Column(Float, nullable=False)
    source = Column(String(100))
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExchangeRateHistory {self.from_currency_code}/{self.to_currency_code} = {self.rate} @ {self.timestamp}>"


class CurrencyRoundingRule(Base):
    """Currency-specific rounding rules"""
    __tablename__ = "currency_rounding_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False, unique=True)
    rounding_mode = Column(String(20), default="ROUND_HALF_UP")  # ROUND_UP, ROUND_DOWN, ROUND_HALF_UP, etc.
    rounding_precision = Column(Integer, default=2)
    min_unit = Column(Float)  # Minimum unit (e.g., 0.01 for cents, 0.05 for 5-cent rounding)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    currency = relationship("Currency")
    
    def __repr__(self):
        return f"<CurrencyRoundingRule {self.currency.code} - {self.rounding_mode}>"


class CurrencyUpdateLog(Base):
    """Log of currency update operations"""
    __tablename__ = "currency_update_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    update_type = Column(String(50), nullable=False)  # "manual", "automatic", "api"
    source = Column(String(100))
    currencies_updated = Column(Integer, default=0)
    rates_updated = Column(Integer, default=0)
    status = Column(String(20), nullable=False)  # "success", "partial", "failed"
    error_message = Column(Text)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CurrencyUpdateLog {self.update_type} - {self.status} @ {self.started_at}>"
