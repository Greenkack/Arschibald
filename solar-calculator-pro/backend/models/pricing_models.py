"""
Product Pricing Database Models
Implements tiered pricing, customer-specific pricing, volume discounts, and promotional pricing
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.core.database import Base


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


class PriceList(Base):
    """Price lists for different customer segments or regions"""
    __tablename__ = "price_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(500))
    currency = Column(String(3), default="EUR")
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product_prices = relationship("ProductPrice", back_populates="price_list", cascade="all, delete-orphan")
    customer_assignments = relationship("CustomerPriceList", back_populates="price_list")


class ProductPrice(Base):
    """Product prices within a price list"""
    __tablename__ = "product_prices"

    id = Column(Integer, primary_key=True, index=True)
    price_list_id = Column(Integer, ForeignKey("price_lists.id"), nullable=False)
    product_id = Column(Integer, nullable=False)  # Reference to product
    base_price = Column(Float, nullable=False)
    pricing_type = Column(SQLEnum(PricingType), default=PricingType.STANDARD)
    
    # Tiered pricing configuration
    tier_config = Column(JSON)  # {min_quantity, max_quantity, price}[]
    
    # Cost information
    cost_price = Column(Float)
    margin_percentage = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_list = relationship("PriceList", back_populates="product_prices")
    price_history = relationship("PriceHistory", back_populates="product_price", cascade="all, delete-orphan")


class PriceHistory(Base):
    """Track price changes over time"""
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_price_id = Column(Integer, ForeignKey("product_prices.id"), nullable=False)
    old_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    change_percentage = Column(Float)
    change_reason = Column(String(500))
    changed_by = Column(String(255))
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product_price = relationship("ProductPrice", back_populates="price_history")


class CustomerPriceList(Base):
    """Assign specific price lists to customers"""
    __tablename__ = "customer_price_lists"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)  # Reference to customer
    price_list_id = Column(Integer, ForeignKey("price_lists.id"), nullable=False)
    priority = Column(Integer, default=0)  # Higher priority wins
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    price_list = relationship("PriceList", back_populates="customer_assignments")


class VolumeDiscount(Base):
    """Volume-based discount rules"""
    __tablename__ = "volume_discounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    product_id = Column(Integer)  # Null = applies to all products
    category_id = Column(Integer)  # Null = applies to all categories
    
    # Discount configuration
    discount_type = Column(SQLEnum(DiscountType), nullable=False)
    min_quantity = Column(Integer, nullable=False)
    max_quantity = Column(Integer)
    discount_value = Column(Float, nullable=False)
    
    # Tiered discount configuration
    tier_config = Column(JSON)  # [{min_qty, max_qty, discount}]
    
    # Validity
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PromotionalPricing(Base):
    """Promotional pricing campaigns"""
    __tablename__ = "promotional_pricing"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    promo_code = Column(String(50), unique=True)
    
    # Discount configuration
    discount_type = Column(SQLEnum(DiscountType), nullable=False)
    discount_value = Column(Float, nullable=False)
    max_discount_amount = Column(Float)  # Cap on discount
    
    # Applicability
    product_ids = Column(JSON)  # List of product IDs
    category_ids = Column(JSON)  # List of category IDs
    customer_ids = Column(JSON)  # List of customer IDs (null = all)
    
    # Usage limits
    max_uses_total = Column(Integer)
    max_uses_per_customer = Column(Integer)
    current_uses = Column(Integer, default=0)
    
    # Validity
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    usage_history = relationship("PromotionalUsage", back_populates="promotion", cascade="all, delete-orphan")


class PromotionalUsage(Base):
    """Track promotional code usage"""
    __tablename__ = "promotional_usage"

    id = Column(Integer, primary_key=True, index=True)
    promotion_id = Column(Integer, ForeignKey("promotional_pricing.id"), nullable=False)
    customer_id = Column(Integer, nullable=False)
    order_id = Column(Integer)
    discount_amount = Column(Float, nullable=False)
    used_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    promotion = relationship("PromotionalPricing", back_populates="usage_history")


class CustomerSpecificPrice(Base):
    """Customer-specific pricing overrides"""
    __tablename__ = "customer_specific_prices"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    special_price = Column(Float, nullable=False)
    discount_percentage = Column(Float)
    reason = Column(String(500))
    
    # Validity
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime)
    
    # Approval workflow
    approved_by = Column(String(255))
    approved_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
