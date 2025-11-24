"""
Database Migration: Add Currency Tables

This migration adds all tables required for multi-currency support:
- currencies
- exchange_rates
- exchange_rate_history
- currency_rounding_rules
- currency_update_logs
"""

from sqlalchemy import create_engine, MetaData
from backend.models.currency_models import Base, Currency, ExchangeRate, ExchangeRateHistory, CurrencyRoundingRule, CurrencyUpdateLog
from backend.core.database import engine
from datetime import datetime


def upgrade():
    """Create currency tables"""
    print("Creating currency tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine, tables=[
        Currency.__table__,
        ExchangeRate.__table__,
        ExchangeRateHistory.__table__,
        CurrencyRoundingRule.__table__,
        CurrencyUpdateLog.__table__
    ])
    
    print("Currency tables created successfully!")
    
    # Seed initial data
    seed_initial_data()


def seed_initial_data():
    """Seed initial currency data"""
    from sqlalchemy.orm import Session
    
    print("Seeding initial currency data...")
    
    db = Session(bind=engine)
    
    try:
        # Check if currencies already exist
        existing_count = db.query(Currency).count()
        if existing_count > 0:
            print(f"Currencies already exist ({existing_count} found). Skipping seed.")
            return
        
        # Add common currencies
        currencies = [
            Currency(
                code="EUR",
                name="Euro",
                symbol="€",
                decimal_places=2,
                is_active=True,
                is_default=True
            ),
            Currency(
                code="USD",
                name="US Dollar",
                symbol="$",
                decimal_places=2,
                is_active=True,
                is_default=False
            ),
            Currency(
                code="GBP",
                name="British Pound",
                symbol="£",
                decimal_places=2,
                is_active=True,
                is_default=False
            ),
            Currency(
                code="CHF",
                name="Swiss Franc",
                symbol="CHF",
                decimal_places=2,
                is_active=True,
                is_default=False
            ),
            Currency(
                code="JPY",
                name="Japanese Yen",
                symbol="¥",
                decimal_places=0,
                is_active=True,
                is_default=False
            ),
            Currency(
                code="CNY",
                name="Chinese Yuan",
                symbol="¥",
                decimal_places=2,
                is_active=True,
                is_default=False
            ),
            Currency(
                code="AUD",
                name="Australian Dollar",
                symbol="A$",
                decimal_places=2,
                is_active=True,
                is_default=False
            ),
            Currency(
                code="CAD",
                name="Canadian Dollar",
                symbol="C$",
                decimal_places=2,
                is_active=True,
                is_default=False
            )
        ]
        
        db.add_all(currencies)
        db.commit()
        
        print(f"Added {len(currencies)} currencies")
        
        # Add initial exchange rates (EUR as base)
        eur = db.query(Currency).filter(Currency.code == "EUR").first()
        
        initial_rates = [
            ("USD", 1.08),
            ("GBP", 0.86),
            ("CHF", 0.95),
            ("JPY", 161.50),
            ("CNY", 7.85),
            ("AUD", 1.65),
            ("CAD", 1.47)
        ]
        
        for to_code, rate in initial_rates:
            to_currency = db.query(Currency).filter(Currency.code == to_code).first()
            if to_currency:
                exchange_rate = ExchangeRate(
                    from_currency_id=eur.id,
                    to_currency_id=to_currency.id,
                    rate=rate,
                    source="Initial Seed",
                    valid_from=datetime.utcnow(),
                    is_active=True
                )
                db.add(exchange_rate)
        
        db.commit()
        print(f"Added {len(initial_rates)} exchange rates")
        
        # Add default rounding rules
        rounding_rules = [
            CurrencyRoundingRule(
                currency_id=eur.id,
                rounding_mode="ROUND_HALF_UP",
                rounding_precision=2,
                description="Standard Euro rounding"
            )
        ]
        
        # Special rounding for JPY (no decimals)
        jpy = db.query(Currency).filter(Currency.code == "JPY").first()
        if jpy:
            rounding_rules.append(
                CurrencyRoundingRule(
                    currency_id=jpy.id,
                    rounding_mode="ROUND_HALF_UP",
                    rounding_precision=0,
                    description="Japanese Yen has no decimal places"
                )
            )
        
        db.add_all(rounding_rules)
        db.commit()
        
        print(f"Added {len(rounding_rules)} rounding rules")
        print("Initial currency data seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()


def downgrade():
    """Drop currency tables"""
    print("Dropping currency tables...")
    
    # Drop all tables in reverse order
    Base.metadata.drop_all(bind=engine, tables=[
        CurrencyUpdateLog.__table__,
        CurrencyRoundingRule.__table__,
        ExchangeRateHistory.__table__,
        ExchangeRate.__table__,
        Currency.__table__
    ])
    
    print("Currency tables dropped successfully!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
