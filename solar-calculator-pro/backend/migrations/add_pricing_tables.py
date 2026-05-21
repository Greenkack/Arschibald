"""
Database Migration: Add Product Pricing Tables
Creates tables for tiered pricing, volume discounts, promotional pricing, and customer-specific pricing
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Enum
from datetime import datetime
import enum


class PricingType(enum.Enum):
    """Types of pricing strategies"""
    STANDARD = "standard"
    TIERED = "tiered"
    CUSTOMER_SPECIFIC = "customer_specific"
    VOLUME_DISCOUNT = "volume_discount"
    PROMOTIONAL = "promotional"
    BUNDLE = "bundle"


class DiscountType(enum.Enum):
    """Types of discounts"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED_PERCENTAGE = "tiered_percentage"


def upgrade(engine):
    """Create pricing tables"""
    metadata = MetaData()

    # Price Lists Table
    price_lists = Table(
        'price_lists', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(255), nullable=False, unique=True),
        Column('description', String(500)),
        Column('currency', String(3), default='EUR'),
        Column('is_active', Boolean, default=True),
        Column('is_default', Boolean, default=False),
        Column('valid_from', DateTime, nullable=False),
        Column('valid_until', DateTime),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    # Product Prices Table
    product_prices = Table(
        'product_prices', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('price_list_id', Integer, ForeignKey('price_lists.id'), nullable=False),
        Column('product_id', Integer, nullable=False),
        Column('base_price', Float, nullable=False),
        Column('pricing_type', Enum(PricingType), default=PricingType.STANDARD),
        Column('tier_config', JSON),
        Column('cost_price', Float),
        Column('margin_percentage', Float),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    # Price History Table
    price_history = Table(
        'price_history', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('product_price_id', Integer, ForeignKey('product_prices.id'), nullable=False),
        Column('old_price', Float, nullable=False),
        Column('new_price', Float, nullable=False),
        Column('change_percentage', Float),
        Column('change_reason', String(500)),
        Column('changed_by', String(255)),
        Column('changed_at', DateTime, default=datetime.utcnow)
    )

    # Customer Price Lists Table
    customer_price_lists = Table(
        'customer_price_lists', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('customer_id', Integer, nullable=False),
        Column('price_list_id', Integer, ForeignKey('price_lists.id'), nullable=False),
        Column('priority', Integer, default=0),
        Column('valid_from', DateTime, nullable=False),
        Column('valid_until', DateTime),
        Column('created_at', DateTime, default=datetime.utcnow)
    )

    # Volume Discounts Table
    volume_discounts = Table(
        'volume_discounts', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(255), nullable=False),
        Column('description', String(500)),
        Column('product_id', Integer),
        Column('category_id', Integer),
        Column('discount_type', Enum(DiscountType), nullable=False),
        Column('min_quantity', Integer, nullable=False),
        Column('max_quantity', Integer),
        Column('discount_value', Float, nullable=False),
        Column('tier_config', JSON),
        Column('is_active', Boolean, default=True),
        Column('valid_from', DateTime, nullable=False),
        Column('valid_until', DateTime),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    # Promotional Pricing Table
    promotional_pricing = Table(
        'promotional_pricing', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(255), nullable=False),
        Column('description', String(500)),
        Column('promo_code', String(50), unique=True),
        Column('discount_type', Enum(DiscountType), nullable=False),
        Column('discount_value', Float, nullable=False),
        Column('max_discount_amount', Float),
        Column('product_ids', JSON),
        Column('category_ids', JSON),
        Column('customer_ids', JSON),
        Column('max_uses_total', Integer),
        Column('max_uses_per_customer', Integer),
        Column('current_uses', Integer, default=0),
        Column('is_active', Boolean, default=True),
        Column('valid_from', DateTime, nullable=False),
        Column('valid_until', DateTime, nullable=False),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    # Promotional Usage Table
    promotional_usage = Table(
        'promotional_usage', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('promotion_id', Integer, ForeignKey('promotional_pricing.id'), nullable=False),
        Column('customer_id', Integer, nullable=False),
        Column('order_id', Integer),
        Column('discount_amount', Float, nullable=False),
        Column('used_at', DateTime, default=datetime.utcnow)
    )

    # Customer Specific Prices Table
    customer_specific_prices = Table(
        'customer_specific_prices', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('customer_id', Integer, nullable=False),
        Column('product_id', Integer, nullable=False),
        Column('special_price', Float, nullable=False),
        Column('discount_percentage', Float),
        Column('reason', String(500)),
        Column('is_active', Boolean, default=True),
        Column('valid_from', DateTime, nullable=False),
        Column('valid_until', DateTime),
        Column('approved_by', String(255)),
        Column('approved_at', DateTime),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    # Create all tables
    metadata.create_all(engine)
    print("✅ Pricing tables created successfully")


def downgrade(engine):
    """Drop pricing tables"""
    metadata = MetaData()
    
    # Define tables in reverse order (to handle foreign keys)
    tables_to_drop = [
        'promotional_usage',
        'customer_specific_prices',
        'promotional_pricing',
        'volume_discounts',
        'customer_price_lists',
        'price_history',
        'product_prices',
        'price_lists'
    ]
    
    for table_name in tables_to_drop:
        table = Table(table_name, metadata)
        table.drop(engine, checkfirst=True)
    
    print("✅ Pricing tables dropped successfully")


if __name__ == "__main__":
    # Example usage
    from backend.core.database import engine
    
    print("Running pricing tables migration...")
    upgrade(engine)
    print("Migration completed!")
