"""
Inventory Management Pydantic Schemas

This module defines the Pydantic schemas for request/response validation
in the inventory management system.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class StockStatusEnum(str, Enum):
    """Stock status enumeration"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class PurchaseOrderStatusEnum(str, Enum):
    """Purchase order status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class TransactionTypeEnum(str, Enum):
    """Transaction type enumeration"""
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    TRANSFER = "transfer"
    DAMAGE = "damage"


# Supplier Schemas
class SupplierBase(BaseModel):
    """Base supplier schema"""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    currency: str = "EUR"
    is_active: bool = True
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    """Schema for creating a supplier"""
    pass


class SupplierUpdate(BaseModel):
    """Schema for updating a supplier"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    notes: Optional[str] = None


class SupplierResponse(SupplierBase):
    """Schema for supplier response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Product Supplier Schemas
class ProductSupplierBase(BaseModel):
    """Base product-supplier schema"""
    product_id: int
    supplier_id: int
    supplier_sku: Optional[str] = None
    cost_price: float = Field(..., gt=0)
    minimum_order_quantity: int = Field(default=1, ge=1)
    lead_time_days: int = Field(default=14, ge=0)
    is_preferred: bool = False
    is_active: bool = True


class ProductSupplierCreate(ProductSupplierBase):
    """Schema for creating a product-supplier relationship"""
    pass


class ProductSupplierUpdate(BaseModel):
    """Schema for updating a product-supplier relationship"""
    supplier_sku: Optional[str] = None
    cost_price: Optional[float] = Field(None, gt=0)
    minimum_order_quantity: Optional[int] = Field(None, ge=1)
    lead_time_days: Optional[int] = Field(None, ge=0)
    is_preferred: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductSupplierResponse(ProductSupplierBase):
    """Schema for product-supplier response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Inventory Stock Schemas
class InventoryStockBase(BaseModel):
    """Base inventory stock schema"""
    product_id: int
    quantity_on_hand: int = Field(default=0, ge=0)
    quantity_reserved: int = Field(default=0, ge=0)
    reorder_point: int = Field(default=10, ge=0)
    reorder_quantity: int = Field(default=50, ge=1)
    minimum_stock_level: int = Field(default=5, ge=0)
    maximum_stock_level: int = Field(default=1000, ge=0)
    warehouse_location: Optional[str] = None
    bin_location: Optional[str] = None


class InventoryStockCreate(InventoryStockBase):
    """Schema for creating inventory stock"""
    pass


class InventoryStockUpdate(BaseModel):
    """Schema for updating inventory stock"""
    quantity_on_hand: Optional[int] = Field(None, ge=0)
    quantity_reserved: Optional[int] = Field(None, ge=0)
    reorder_point: Optional[int] = Field(None, ge=0)
    reorder_quantity: Optional[int] = Field(None, ge=1)
    minimum_stock_level: Optional[int] = Field(None, ge=0)
    maximum_stock_level: Optional[int] = Field(None, ge=0)
    warehouse_location: Optional[str] = None
    bin_location: Optional[str] = None


class InventoryStockResponse(InventoryStockBase):
    """Schema for inventory stock response"""
    id: int
    quantity_available: int
    stock_status: StockStatusEnum
    last_counted_at: Optional[datetime] = None
    last_restock_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Inventory Transaction Schemas
class InventoryTransactionBase(BaseModel):
    """Base inventory transaction schema"""
    stock_id: int
    transaction_type: TransactionTypeEnum
    quantity: int
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    unit_cost: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    performed_by: Optional[str] = None


class InventoryTransactionCreate(InventoryTransactionBase):
    """Schema for creating an inventory transaction"""
    pass


class InventoryTransactionResponse(InventoryTransactionBase):
    """Schema for inventory transaction response"""
    id: int
    quantity_before: int
    quantity_after: int
    total_cost: Optional[float] = None
    transaction_date: datetime

    class Config:
        from_attributes = True


# Purchase Order Schemas
class PurchaseOrderItemBase(BaseModel):
    """Base purchase order item schema"""
    product_id: int
    quantity_ordered: int = Field(..., gt=0)
    unit_cost: float = Field(..., gt=0)
    notes: Optional[str] = None


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    """Schema for creating a purchase order item"""
    pass


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    """Schema for purchase order item response"""
    id: int
    purchase_order_id: int
    quantity_received: int
    total_cost: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    """Base purchase order schema"""
    supplier_id: int
    expected_delivery_date: Optional[datetime] = None
    shipping_cost: float = Field(default=0.0, ge=0)
    notes: Optional[str] = None
    shipping_address: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema for creating a purchase order"""
    items: List[PurchaseOrderItemCreate]


class PurchaseOrderUpdate(BaseModel):
    """Schema for updating a purchase order"""
    status: Optional[PurchaseOrderStatusEnum] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    shipping_cost: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    shipping_address: Optional[str] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    """Schema for purchase order response"""
    id: int
    order_number: str
    status: PurchaseOrderStatusEnum
    order_date: datetime
    actual_delivery_date: Optional[datetime] = None
    subtotal: float
    tax_amount: float
    total_amount: float
    currency: str
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[PurchaseOrderItemResponse] = []

    class Config:
        from_attributes = True


# Stock Alert Schemas
class StockAlertBase(BaseModel):
    """Base stock alert schema"""
    product_id: int
    stock_id: int
    alert_type: str
    message: str
    severity: str = "warning"


class StockAlertCreate(StockAlertBase):
    """Schema for creating a stock alert"""
    pass


class StockAlertResponse(StockAlertBase):
    """Schema for stock alert response"""
    id: int
    is_acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Additional Schemas
class StockAdjustment(BaseModel):
    """Schema for stock adjustment"""
    product_id: int
    quantity_change: int
    reason: str
    notes: Optional[str] = None
    performed_by: Optional[str] = None


class ReorderCalculation(BaseModel):
    """Schema for reorder calculation result"""
    product_id: int
    current_stock: int
    reorder_point: int
    reorder_quantity: int
    recommended_order_quantity: int
    estimated_cost: float
    preferred_supplier_id: Optional[int] = None
    lead_time_days: int


class InventoryReport(BaseModel):
    """Schema for inventory report"""
    total_products: int
    total_stock_value: float
    products_in_stock: int
    products_low_stock: int
    products_out_of_stock: int
    products_needing_reorder: int
    average_stock_level: float
    report_date: datetime


class SupplierPerformance(BaseModel):
    """Schema for supplier performance metrics"""
    supplier_id: int
    supplier_name: str
    total_orders: int
    on_time_deliveries: int
    late_deliveries: int
    average_lead_time_days: float
    total_spend: float
    rating: float
