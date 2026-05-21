"""
Tests for Currency Service

This module contains comprehensive tests for the currency service including:
- Currency management
- Exchange rate management
- Currency conversion
- Multi-currency display
- Currency-specific rounding
- Exchange rate history
- Automatic updates
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.models.currency_models import Base, Currency, ExchangeRate, ExchangeRateHistory, CurrencyRoundingRule
from backend.services.currency_service import CurrencyService
from backend.models.currency_schemas import (
    CurrencyCreate, CurrencyUpdate,
    ExchangeRateCreate, ExchangeRateUpdate,
    CurrencyConversionRequest,
    MultiCurrencyDisplayRequest,
    CurrencyRoundingRuleCreate,
    CurrencyUpdateRequest
)


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def currency_service(db_session):
    """Create a currency service instance"""
    return CurrencyService(db_session)


@pytest.fixture
def sample_currencies(currency_service):
    """Create sample currencies for testing"""
    currencies = [
        CurrencyCreate(code="EUR", name="Euro", symbol="€", decimal_places=2, is_default=True),
        CurrencyCreate(code="USD", name="US Dollar", symbol="$", decimal_places=2),
        CurrencyCreate(code="GBP", name="British Pound", symbol="£", decimal_places=2),
        CurrencyCreate(code="JPY", name="Japanese Yen", symbol="¥", decimal_places=0)
    ]
    
    created = []
    for currency_data in currencies:
        created.append(currency_service.create_currency(currency_data))
    
    return created


@pytest.fixture
def sample_exchange_rates(currency_service, sample_currencies):
    """Create sample exchange rates for testing"""
    rates = [
        ExchangeRateCreate(
            from_currency_code="EUR",
            to_currency_code="USD",
            rate=1.08,
            source="Test",
            valid_from=datetime.utcnow(),
            is_active=True
        ),
        ExchangeRateCreate(
            from_currency_code="EUR",
            to_currency_code="GBP",
            rate=0.86,
            source="Test",
            valid_from=datetime.utcnow(),
            is_active=True
        ),
        ExchangeRateCreate(
            from_currency_code="EUR",
            to_currency_code="JPY",
            rate=161.50,
            source="Test",
            valid_from=datetime.utcnow(),
            is_active=True
        )
    ]
    
    created = []
    for rate_data in rates:
        created.append(currency_service.create_exchange_rate(rate_data))
    
    return created


# ==================== Currency Management Tests ====================

def test_create_currency(currency_service):
    """Test creating a new currency"""
    currency_data = CurrencyCreate(
        code="EUR",
        name="Euro",
        symbol="€",
        decimal_places=2,
        is_default=True
    )
    
    result = currency_service.create_currency(currency_data)
    
    assert result.code == "EUR"
    assert result.name == "Euro"
    assert result.symbol == "€"
    assert result.decimal_places == 2
    assert result.is_default == True
    assert result.is_active == True


def test_create_duplicate_currency(currency_service, sample_currencies):
    """Test that creating a duplicate currency raises an error"""
    currency_data = CurrencyCreate(
        code="EUR",
        name="Euro",
        symbol="€",
        decimal_places=2
    )
    
    with pytest.raises(ValueError, match="already exists"):
        currency_service.create_currency(currency_data)


def test_get_currency_by_code(currency_service, sample_currencies):
    """Test getting a currency by code"""
    result = currency_service.get_currency_by_code("EUR")
    
    assert result is not None
    assert result.code == "EUR"
    assert result.name == "Euro"


def test_list_currencies(currency_service, sample_currencies):
    """Test listing all currencies"""
    result = currency_service.list_currencies()
    
    assert len(result) == 4
    assert all(c.code in ["EUR", "USD", "GBP", "JPY"] for c in result)


def test_list_active_currencies(currency_service, sample_currencies):
    """Test listing only active currencies"""
    # Deactivate one currency
    eur = currency_service.get_currency_by_code("EUR")
    currency_service.update_currency(eur.id, CurrencyUpdate(is_active=False))
    
    result = currency_service.list_currencies(active_only=True)
    
    assert len(result) == 3
    assert all(c.code != "EUR" for c in result)


def test_update_currency(currency_service, sample_currencies):
    """Test updating a currency"""
    eur = currency_service.get_currency_by_code("EUR")
    
    update_data = CurrencyUpdate(name="European Euro", symbol="EUR")
    result = currency_service.update_currency(eur.id, update_data)
    
    assert result.name == "European Euro"
    assert result.symbol == "EUR"
    assert result.code == "EUR"  # Code should not change


def test_delete_currency(currency_service, sample_currencies):
    """Test deleting a currency"""
    jpy = currency_service.get_currency_by_code("JPY")
    
    success = currency_service.delete_currency(jpy.id)
    
    assert success == True
    assert currency_service.get_currency_by_code("JPY") is None


def test_get_default_currency(currency_service, sample_currencies):
    """Test getting the default currency"""
    result = currency_service.get_default_currency()
    
    assert result is not None
    assert result.code == "EUR"
    assert result.is_default == True


# ==================== Exchange Rate Tests ====================

def test_create_exchange_rate(currency_service, sample_currencies):
    """Test creating an exchange rate"""
    rate_data = ExchangeRateCreate(
        from_currency_code="EUR",
        to_currency_code="USD",
        rate=1.08,
        source="Test",
        valid_from=datetime.utcnow(),
        is_active=True
    )
    
    result = currency_service.create_exchange_rate(rate_data)
    
    assert result.from_currency_code == "EUR"
    assert result.to_currency_code == "USD"
    assert result.rate == 1.08
    assert result.is_active == True


def test_get_exchange_rate(currency_service, sample_currencies, sample_exchange_rates):
    """Test getting an exchange rate"""
    result = currency_service.get_exchange_rate("EUR", "USD")
    
    assert result is not None
    assert result.from_currency_code == "EUR"
    assert result.to_currency_code == "USD"
    assert result.rate == 1.08


def test_get_reverse_exchange_rate(currency_service, sample_currencies, sample_exchange_rates):
    """Test getting a reverse exchange rate"""
    # We only have EUR->USD, but should be able to get USD->EUR
    result = currency_service.get_exchange_rate("USD", "EUR")
    
    # This should return None since we don't have the reverse rate
    # The conversion function will handle this
    assert result is None


def test_list_exchange_rates(currency_service, sample_currencies, sample_exchange_rates):
    """Test listing exchange rates"""
    result = currency_service.list_exchange_rates()
    
    assert len(result) == 3


def test_list_exchange_rates_for_currency(currency_service, sample_currencies, sample_exchange_rates):
    """Test listing exchange rates for a specific currency"""
    result = currency_service.list_exchange_rates(currency_code="EUR")
    
    assert len(result) == 3
    assert all(r.from_currency_code == "EUR" for r in result)


# ==================== Currency Conversion Tests ====================

def test_convert_same_currency(currency_service, sample_currencies):
    """Test converting between same currency"""
    request = CurrencyConversionRequest(
        amount=100.0,
        from_currency="EUR",
        to_currency="EUR"
    )
    
    result = currency_service.convert_currency(request)
    
    assert result.original_amount == 100.0
    assert result.converted_amount == 100.0
    assert result.exchange_rate == 1.0


def test_convert_currency(currency_service, sample_currencies, sample_exchange_rates):
    """Test converting between different currencies"""
    request = CurrencyConversionRequest(
        amount=100.0,
        from_currency="EUR",
        to_currency="USD"
    )
    
    result = currency_service.convert_currency(request)
    
    assert result.original_amount == 100.0
    assert result.converted_amount == 108.0  # 100 * 1.08
    assert result.exchange_rate == 1.08


def test_convert_with_reverse_rate(currency_service, sample_currencies, sample_exchange_rates):
    """Test converting using reverse exchange rate"""
    request = CurrencyConversionRequest(
        amount=108.0,
        from_currency="USD",
        to_currency="EUR"
    )
    
    result = currency_service.convert_currency(request)
    
    # Should use reverse of EUR->USD rate (1/1.08)
    assert result.original_amount == 108.0
    assert abs(result.converted_amount - 100.0) < 0.01  # Allow small rounding error


def test_multi_currency_display(currency_service, sample_currencies, sample_exchange_rates):
    """Test displaying amount in multiple currencies"""
    request = MultiCurrencyDisplayRequest(
        base_amount=100.0,
        base_currency="EUR",
        target_currencies=["USD", "GBP", "JPY"]
    )
    
    result = currency_service.multi_currency_display(request)
    
    assert result.base_amount == 100.0
    assert result.base_currency == "EUR"
    assert len(result.conversions) == 3
    
    # Check USD conversion
    usd_conversion = next(c for c in result.conversions if c.to_currency == "USD")
    assert usd_conversion.converted_amount == 108.0


# ==================== Currency Rounding Tests ====================

def test_create_rounding_rule(currency_service, sample_currencies):
    """Test creating a rounding rule"""
    rule_data = CurrencyRoundingRuleCreate(
        currency_code="EUR",
        rounding_mode="ROUND_HALF_UP",
        rounding_precision=2,
        description="Standard Euro rounding"
    )
    
    result = currency_service.create_rounding_rule(rule_data)
    
    assert result.currency_code == "EUR"
    assert result.rounding_mode == "ROUND_HALF_UP"
    assert result.rounding_precision == 2


def test_apply_default_rounding(currency_service, sample_currencies):
    """Test applying default rounding (no rule)"""
    result = currency_service.apply_rounding(123.456, "EUR")
    
    assert result == 123.46  # Default 2 decimal places, ROUND_HALF_UP


def test_apply_custom_rounding(currency_service, sample_currencies):
    """Test applying custom rounding rule"""
    # Create rounding rule for 5-cent rounding
    rule_data = CurrencyRoundingRuleCreate(
        currency_code="EUR",
        rounding_mode="ROUND_HALF_UP",
        rounding_precision=2,
        min_unit=0.05,
        description="5-cent rounding"
    )
    currency_service.create_rounding_rule(rule_data)
    
    # Test various amounts
    assert currency_service.apply_rounding(1.22, "EUR") == 1.20
    assert currency_service.apply_rounding(1.23, "EUR") == 1.25
    assert currency_service.apply_rounding(1.27, "EUR") == 1.25
    assert currency_service.apply_rounding(1.28, "EUR") == 1.30


def test_apply_zero_decimal_rounding(currency_service, sample_currencies):
    """Test applying zero decimal rounding (e.g., JPY)"""
    # Create rounding rule for JPY (no decimals)
    rule_data = CurrencyRoundingRuleCreate(
        currency_code="JPY",
        rounding_mode="ROUND_HALF_UP",
        rounding_precision=0,
        description="No decimal places"
    )
    currency_service.create_rounding_rule(rule_data)
    
    result = currency_service.apply_rounding(123.456, "JPY")
    
    assert result == 123.0


# ==================== Exchange Rate History Tests ====================

def test_exchange_rate_history(currency_service, sample_currencies, sample_exchange_rates):
    """Test retrieving exchange rate history"""
    history = currency_service.get_exchange_rate_history("EUR", "USD")
    
    assert len(history) > 0
    assert history[0]["from_currency"] == "EUR"
    assert history[0]["to_currency"] == "USD"
    assert history[0]["rate"] == 1.08


def test_exchange_rate_history_with_date_range(currency_service, sample_currencies, sample_exchange_rates):
    """Test retrieving exchange rate history with date range"""
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow() + timedelta(days=1)
    
    history = currency_service.get_exchange_rate_history(
        "EUR", "USD",
        start_date=start_date,
        end_date=end_date
    )
    
    assert len(history) > 0


# ==================== Statistics Tests ====================

def test_get_statistics(currency_service, sample_currencies, sample_exchange_rates):
    """Test getting currency statistics"""
    stats = currency_service.get_statistics()
    
    assert stats.total_currencies == 4
    assert stats.active_currencies == 4
    assert stats.total_exchange_rates == 3
    assert stats.active_exchange_rates == 3
    assert stats.default_currency == "EUR"


# ==================== Error Handling Tests ====================

def test_convert_with_missing_rate(currency_service, sample_currencies):
    """Test conversion with missing exchange rate"""
    request = CurrencyConversionRequest(
        amount=100.0,
        from_currency="EUR",
        to_currency="USD"
    )
    
    with pytest.raises(ValueError, match="No exchange rate found"):
        currency_service.convert_currency(request)


def test_create_rounding_rule_for_nonexistent_currency(currency_service):
    """Test creating rounding rule for non-existent currency"""
    rule_data = CurrencyRoundingRuleCreate(
        currency_code="XXX",
        rounding_mode="ROUND_HALF_UP",
        rounding_precision=2
    )
    
    with pytest.raises(ValueError, match="not found"):
        currency_service.create_rounding_rule(rule_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
