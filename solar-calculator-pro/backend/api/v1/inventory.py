"""
Inventory Management API Endpoints

This module provides REST API endpoints for inventory management operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.database import get_db
from backend.services.inventory_service import InventoryService
from backend.models.inventory_schemas import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    ProductSupplierCreate, ProductSupplierUpdate,
    InventoryStockCreate, InventoryStockUpdate, InventoryStockResponse,
    InventoryTransactionResponse,
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    PurchaseOrderStatusEnum,
    StockAlertResponse,
    StockAdjustment, ReorderCalculation, InventoryReport, SupplierPerformance
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    """Dependency to get inventory service"""
    return InventoryService(db)


# ==================== Supplier Endpoints ====================

@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(
    supplier: SupplierCreate,
    service: InventoryService = Depends(get_inventory_service)
):
    """Create a new supplier"""
    try:
        return service.create_supplier(supplier)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get supplier by ID"""
    supplier = service.get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.get("/suppliers", response_model=List[SupplierResponse])
def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get list of suppliers"""
    return service.get_suppliers(skip=skip, limit=limit, is_active=is_active)


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier: SupplierUpdate,
    service: InventoryService = Depends(get_inventory_service)
):
    """Update supplier"""
    updated = service.update_supplier(supplier_id, supplier)
    if not updated:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return updated


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """Delete supplier (soft delete)"""
    success = service.delete_supplier(supplier_id)
    if not success:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"success": True, "message": "Supplier deleted successfully"}


# ==================== Product-Supplier Endpoints ====================

@router.post("/products/{product_id}/suppliers")
def add_product_supplier(
    product_id: int,
    product_supplier: ProductSupplierCreate,
    service: InventoryService = Depends(get_inventory_service)
):
    """Add supplier for a product"""
    if product_supplier.product_id != product_id:
        raise HTTPException(status_code=400, detail="Product ID mismatch")
    
    try:
        return service.add_product_supplier(product_supplier)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/products/{product_id}/suppliers")
def get_product_suppliers(
    product_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get all suppliers for a product"""
    return service.get_product_suppliers(product_id)


@router.get("/products/{product_id}/suppliers/preferred")
def get_preferred_supplier(
    product_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get preferred supplier for a product"""
    supplier = service.get_preferred_supplier(product_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="No preferred supplier found")
    return supplier


# ==================== Stock Endpoints ====================

@router.post("/stock", response_model=InventoryStockResponse)
def create_stock(
    stock: InventoryStockCreate,
    service: InventoryService = Depends(get_inventory_service)
):
    """Create inventory stock for a product"""
    try:
        return service.create_stock(stock)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stock/{product_id}", response_model=InventoryStockResponse)
def get_stock(
    product_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get stock for a product"""
    stock = service.get_stock(product_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.put("/stock/{product_id}", response_model=InventoryStockResponse)
def update_stock(
    product_id: int,
    stock: InventoryStockUpdate,
    service: InventoryService = Depends(get_inventory_service)
):
    """Update stock"""
    updated = service.update_stock(product_id, stock)
    if not updated:
        raise HTTPException(status_code=404, detail="Stock not found")
    return updated


@router.post("/stock/adjust")
def adjust_stock(
    adjustment: StockAdjustment,
    service: InventoryService = Depends(get_inventory_service)
):
    """Adjust stock quantity"""
    try:
        return service.adjust_stock(adjustment)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Stock Alert Endpoints ====================

@router.get("/alerts", response_model=List[StockAlertResponse])
def get_stock_alerts(
    is_resolved: Optional[bool] = Query(False),
    severity: Optional[str] = None,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get stock alerts"""
    return service.get_stock_alerts(is_resolved=is_resolved, severity=severity)


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    acknowledged_by: str,
    service: InventoryService = Depends(get_inventory_service)
):
    """Acknowledge a stock alert"""
    success = service.acknowledge_alert(alert_id, acknowledged_by)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True, "message": "Alert acknowledged"}


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """Resolve a stock alert"""
    success = service.resolve_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True, "message": "Alert resolved"}


# ==================== Reorder Endpoints ====================

@router.get("/reorder/calculate", response_model=List[ReorderCalculation])
def calculate_reorder_needs(
    service: InventoryService = Depends(get_inventory_service)
):
    """Calculate products that need reordering"""
    return service.calculate_reorder_needs()


# ==================== Purchase Order Endpoints ====================

@router.post("/purchase-orders", response_model=PurchaseOrderResponse)
def create_purchase_order(
    po: PurchaseOrderCreate,
    created_by: str = Query(..., description="User creating the order"),
    service: InventoryService = Depends(get_inventory_service)
):
    """Create a new purchase order"""
    try:
        return service.create_purchase_order(po, created_by)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(
    po_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get purchase order by ID"""
    po = service.get_purchase_order(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
def get_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[PurchaseOrderStatusEnum] = None,
    supplier_id: Optional[int] = None,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get list of purchase orders"""
    return service.get_purchase_orders(
        skip=skip,
        limit=limit,
        status=status,
        supplier_id=supplier_id
    )


@router.put("/purchase-orders/{po_id}/status", response_model=PurchaseOrderResponse)
def update_purchase_order_status(
    po_id: int,
    status: PurchaseOrderStatusEnum,
    approved_by: Optional[str] = None,
    service: InventoryService = Depends(get_inventory_service)
):
    """Update purchase order status"""
    updated = service.update_purchase_order_status(po_id, status, approved_by)
    if not updated:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return updated


@router.post("/purchase-orders/{po_id}/receive")
def receive_purchase_order(
    po_id: int,
    received_items: dict,  # {product_id: quantity_received}
    service: InventoryService = Depends(get_inventory_service)
):
    """Receive items from a purchase order"""
    try:
        return service.receive_purchase_order(po_id, received_items)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Report Endpoints ====================

@router.get("/reports/inventory", response_model=InventoryReport)
def get_inventory_report(
    service: InventoryService = Depends(get_inventory_service)
):
    """Generate comprehensive inventory report"""
    return service.get_inventory_report()


@router.get("/reports/supplier/{supplier_id}/performance", response_model=SupplierPerformance)
def get_supplier_performance(
    supplier_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get supplier performance metrics"""
    performance = service.get_supplier_performance(supplier_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return performance
