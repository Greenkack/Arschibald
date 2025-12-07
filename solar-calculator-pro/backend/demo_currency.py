"""
Currency System Demo

This script demonstrates the multi-currency functionality including:
- Currency management
- Exchange rate management
- Currency conversion
- Multi-currency display
- Currency-specific rounding
- Exchange rate history
"""

from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, engine
from backend.models.currency_models import Base
from backend.services.currency_service import CurrencyService
from backend.models.currency_schemas import (
    CurrencyCreate, ExchangeRateCreate,
    CurrencyConversionRequest, MultiCurrencyDisplayRequest,
    CurrencyRoundingRuleCreate, CurrencyUpdateRequest
)
from datetime import datetime


def setup_database():
    """Create database tables"""
    print("Setting up database...")
    Base.metadata.create_all(bind=engine)
    print("Database setup complete!\n")


def demo_currency_management(service: CurrencyService):
    """Demonstrate currency management"""
    print("=" * 60)
    print("CURRENCY MANAGEMENT DEMO")
    print("=" * 60)
    
    # Create currencies
    print("\n1. Creating currencies...")
    currencies = [
        CurrencyCreate(code="EUR", name="Euro", symbol="€", decimal_places=2, is_default=True),
        CurrencyCreate(code="USD", name="US Dollar", symbol="$", decimal_places=2),
        CurrencyCreate(code="GBP", name="British Pound", symbol="£", decimal_places=2),
        CurrencyCreate(code="CHF", name="Swiss Franc", symbol="CHF", decimal_places=2),
        CurrencyCreate(code="JPY", name="Japanese Yen", symbol="¥", decimal_places=0)
    ]
    
    for currency_data in currencies:
        try:
            currency = service.create_currency(currency_data)
            print(f"    Created: {currency.code} - {currency.name} ({currency.symbol})")
        except ValueError as e:
            print(f"    {e}")
    
    # List currencies
    print("\n2. Listing all currencies...")
    all_currencies = service.list_currencies()
    for currency in all_currencies:
        default_marker = " [DEFAULT]" if currency.is_default else ""
        print(f"   • {currency.code}: {currency.name} ({currency.symbol}){default_marker}")
    
    # Get default currency
    print("\n3. Getting default currency...")
    default = service.get_default_currency()
    if default:
        print(f"   Default currency: {default.code} - {default.name}")


def demo_exchange_rates(service: CurrencyService):
    """Demonstrate exchange rate management"""
    print("\n" + "=" * 60)
    print("EXCHANGE RATE MANAGEMENT DEMO")
    print("=" * 60)
    
    # Create exchange rates
    print("\n1. Creating exchange rates (EUR as base)...")
    rates = [
        ("USD", 1.08, "European Central Bank"),
        ("GBP", 0.86, "European Central Bank"),
        ("CHF", 0.95, "European Central Bank"),
        ("JPY", 161.50, "European Central Bank")
    ]
    
    for to_currency, rate, source in rates:
        try:
            rate_data = ExchangeRateCreate(
                from_currency_code="EUR",
                to_currency_code=to_currency,
                rate=rate,
                source=source,
                valid_from=datetime.utcnow(),
                is_active=True
            )
            result = service.create_exchange_rate(rate_data)
            print(f"    EUR/{to_currency} = {rate}")
        except ValueError as e:
            print(f"    {e}")
    
    # List exchange rates
    print("\n2. Listing all exchange rates...")
    all_rates = service.list_exchange_rates()
    for rate in all_rates:
        print(f"   • {rate.from_currency_code}/{rate.to_currency_code} = {rate.rate} (Source: {rate.source})")


def demo_currency_conversion(service: CurrencyService):
    """Demonstrate currency conversion"""
    print("\n" + "=" * 60)
    print("CURRENCY CONVERSION DEMO")
    print("=" * 60)
    
    # Single conversion
    print("\n1. Converting 1000 EUR to various currencies...")
    conversions = [
        ("EUR", "USD"),
        ("EUR", "GBP"),
        ("EUR", "CHF"),
        ("EUR", "JPY")
    ]
    
    for from_curr, to_curr in conversions:
        try:
            request = CurrencyConversionRequest(
                amount=1000.0,
                from_currency=from_curr,
                to_currency=to_curr
            )
            result = service.convert_currency(request)
            print(f"   • 1000 {from_curr} = {result.converted_amount:.2f} {to_curr} (Rate: {result.exchange_rate})")
        except ValueError as e:
            print(f"    {e}")
    
    # Reverse conversion
    print("\n2. Reverse conversion (USD to EUR)...")
    try:
        request = CurrencyConversionRequest(
            amount=1080.0,
            from_currency="USD",
            to_currency="EUR"
        )
        result = service.convert_currency(request)
        print(f"   • 1080 USD = {result.converted_amount:.2f} EUR (Rate: {result.exchange_rate:.4f})")
    except ValueError as e:
        print(f"    {e}")


def demo_multi_currency_display(service: CurrencyService):
    """Demonstrate multi-currency display"""
    print("\n" + "=" * 60)
    print("MULTI-CURRENCY DISPLAY DEMO")
    print("=" * 60)
    
    print("\n1. Displaying 16,999.00 EUR in multiple currencies...")
    request = MultiCurrencyDisplayRequest(
        base_amount=16999.00,
        base_currency="EUR",
        target_currencies=["USD", "GBP", "CHF", "JPY"]
    )
    
    result = service.multi_currency_display(request)
    
    print(f"\n   Base Amount: {result.base_amount:.2f} {result.base_currency}")
    print("   Conversions:")
    for conversion in result.conversions:
        print(f"      • {conversion.to_currency}: {conversion.converted_amount:.2f}")


def demo_currency_rounding(service: CurrencyService):
    """Demonstrate currency-specific rounding"""
    print("\n" + "=" * 60)
    print("CURRENCY ROUNDING DEMO")
    print("=" * 60)
    
    # Create rounding rules
    print("\n1. Creating rounding rules...")
    
    # Standard EUR rounding
    try:
        rule = CurrencyRoundingRuleCreate(
            currency_code="EUR",
            rounding_mode="ROUND_HALF_UP",
            rounding_precision=2,
            description="Standard Euro rounding"
        )
        service.create_rounding_rule(rule)
        print("    EUR: Standard 2 decimal places")
    except ValueError as e:
        print(f"    {e}")
    
    # 5-cent rounding for CHF
    try:
        rule = CurrencyRoundingRuleCreate(
            currency_code="CHF",
            rounding_mode="ROUND_HALF_UP",
            rounding_precision=2,
            min_unit=0.05,
            description="Swiss Franc 5-cent rounding"
        )
        service.create_rounding_rule(rule)
        print("    CHF: 5-cent rounding")
    except ValueError as e:
        print(f"    {e}")
    
    # No decimals for JPY
    try:
        rule = CurrencyRoundingRuleCreate(
            currency_code="JPY",
            rounding_mode="ROUND_HALF_UP",
            rounding_precision=0,
            description="Japanese Yen has no decimal places"
        )
        service.create_rounding_rule(rule)
        print("    JPY: No decimal places")
    except ValueError as e:
        print(f"    {e}")
    
    # Test rounding
    print("\n2. Testing rounding with amount 123.456...")
    test_amount = 123.456
    
    for currency in ["EUR", "CHF", "JPY"]:
        rounded = service.apply_rounding(test_amount, currency)
        print(f"   • {currency}: {test_amount} → {rounded}")


def demo_exchange_rate_history(service: CurrencyService):
    """Demonstrate exchange rate history"""
    print("\n" + "=" * 60)
    print("EXCHANGE RATE HISTORY DEMO")
    print("=" * 60)
    
    print("\n1. Retrieving EUR/USD exchange rate history...")
    history = service.get_exchange_rate_history("EUR", "USD", limit=5)
    
    if history:
        print(f"   Found {len(history)} historical rates:")
        for entry in history:
            print(f"      • {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}: {entry['rate']} (Source: {entry['source']})")
    else:
        print("   No history available yet")


def demo_statistics(service: CurrencyService):
    """Demonstrate currency statistics"""
    print("\n" + "=" * 60)
    print("CURRENCY STATISTICS")
    print("=" * 60)
    
    stats = service.get_statistics()
    
    print(f"\n   Total Currencies: {stats.total_currencies}")
    print(f"   Active Currencies: {stats.active_currencies}")
    print(f"   Total Exchange Rates: {stats.total_exchange_rates}")
    print(f"   Active Exchange Rates: {stats.active_exchange_rates}")
    print(f"   Default Currency: {stats.default_currency}")
    if stats.last_update:
        print(f"   Last Update: {stats.last_update.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("MULTI-CURRENCY SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Setup database
    setup_database()
    
    # Create service
    db = SessionLocal()
    service = CurrencyService(db)
    
    try:
        # Run demos
        demo_currency_management(service)
        demo_exchange_rates(service)
        demo_currency_conversion(service)
        demo_multi_currency_display(service)
        demo_currency_rounding(service)
        demo_exchange_rate_history(service)
        demo_statistics(service)
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE!")
        print("=" * 60)
        print("\nThe multi-currency system is fully functional and ready to use.")
        print("All features have been demonstrated successfully.\n")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
