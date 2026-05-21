"""
Inventory Management Database Models

This module defines the database models for the inventory management system,
including stock tracking, suppliers, purchase orders, and inventory transactions.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from backend.core.database import Base


class StockStatus(enum.Enum):
    """Stock status enumeration"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class PurchaseOrderStatus(enum.Enum):
    """Purchase order status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class TransactionType(enum.Enum):
    """Inventory transaction type enumeration"""
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    TRANSFER = "transfer"
    DAMAGE = "damage"


class Supplier(Base):
    """Supplier model for managing product suppliers"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Business details
    tax_id = Column(String(50))
    payment_terms = Column(String(100))  # e.g., "Net 30", "Net 60"
    currency = Column(String(3), default="EUR")
    
    # Status
    is_active = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)  # 0-5 rating
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    products = relationship("ProductSupplier", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


class ProductSupplier(Base):
    """Product-Supplier relationship with pricing"""
    __tablename__ = "product_suppliers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    # Pricing
    supplier_sku = Column(String(100))
    cost_price = Column(Float, nullable=False)
    minimum_order_quantity = Column(Integer, default=1)
    lead_time_days = Column(Integer, default=14)
    
    # Status
    is_preferred = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")


class InventoryStock(Base):
    """Inventory stock tracking for products"""
    __tablename__ = "inventory_stock"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True)
    
    # Stock levels
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)  # Reserved for orders
    quantity_available = Column(Integer, default=0)  # on_hand - reserved
    
    # Reorder settings
    reorder_point = Column(Integer, default=10)
    reorder_quantity = Column(Integer, default=50)
    minimum_stock_level = Column(Integer, default=5)
    maximum_stock_level = Column(Integer, default=1000)
    
    # Location
    warehouse_location = Column(String(100))
    bin_location = Column(String(50))
    
    # Status
    stock_status = Column(SQLEnum(StockStatus), default=StockStatus.IN_STOCK)
    last_counted_at = Column(DateTime(timezone=True))
    last_restock_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transactions = relationship("InventoryTransaction", back_populates="stock")


class InventoryTransaction(Base):
    """Inventory transaction history"""
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("inventory_stock.id"), nullable=False)
    
    # Transaction details
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    
    # Reference
    reference_type = Column(String(50))  # e.g., "purchase_order", "sale", "adjustment"
    reference_id = Column(Integer)
    
    # Details
    unit_cost = Column(Float)
    total_cost = Column(Float)
    notes = Column(Text)
    performed_by = Column(String(255))
    
    # Timestamp
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    stock = relationship("InventoryStock", back_populates="transactions")


class PurchaseOrder(Base):
    """Purchase order for ordering products from suppliers"""
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    # Order details
    status = Column(SQLEnum(PurchaseOrderStatus), default=PurchaseOrderStatus.DRAFT)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    expected_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    
    # Financial
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    currency = Column(String(3), default="EUR")
    
    # Additional info
    notes = Column(Text)
    shipping_address = Column(Text)
    created_by = Column(String(255))
    approved_by = Column(String(255))
    approved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    """Purchase order line items"""
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Order details
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, default=0)
    unit_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    
    # Additional info
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")


class StockAlert(Base):
    """Stock alert notifications"""
    __tablename__ = "stock_alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("inventory_stock.id"), nullable=False)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # "low_stock", "out_of_stock", "reorder_point"
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="warning")  # "info", "warning", "critical"
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(255))
    acknowledged_at = Column(DateTime(timezone=True))
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
