"""
Inventory Management Service

This service handles all inventory management operations including stock tracking,
low stock alerts, reorder point calculations, supplier management, purchase orders,
and inventory reports.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from backend.models.inventory_models import (
    Supplier, ProductSupplier, InventoryStock, InventoryTransaction,
    PurchaseOrder, PurchaseOrderItem, StockAlert,
    StockStatus, PurchaseOrderStatus, TransactionType
)
from backend.models.inventory_schemas import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    ProductSupplierCreate, ProductSupplierUpdate,
    InventoryStockCreate, InventoryStockUpdate, InventoryStockResponse,
    InventoryTransactionCreate, InventoryTransactionResponse,
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    StockAlertCreate, StockAlertResponse,
    StockAdjustment, ReorderCalculation, InventoryReport, SupplierPerformance
)

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for managing inventory operations"""

    def __init__(self, db: Session):
        """Initialize inventory service"""
        self.db = db

    # ==================== Supplier Management ====================

    def create_supplier(self, supplier_data: SupplierCreate) -> SupplierResponse:
        """Create a new supplier"""
        try:
            supplier = Supplier(**supplier_data.dict())
            self.db.add(supplier)
            self.db.commit()
            self.db.refresh(supplier)
            
            logger.info(f"Created supplier: {supplier.name} (ID: {supplier.id})")
            return SupplierResponse.from_orm(supplier)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating supplier: {str(e)}")
            raise

    def get_supplier(self, supplier_id: int) -> Optional[SupplierResponse]:
        """Get supplier by ID"""
        supplier = self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
        return SupplierResponse.from_orm(supplier) if supplier else None

    def get_suppliers(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[SupplierResponse]:
        """Get list of suppliers"""
        query = self.db.query(Supplier)
        
        if is_active is not None:
            query = query.filter(Supplier.is_active == is_active)
        
        suppliers = query.offset(skip).limit(limit).all()
        return [SupplierResponse.from_orm(s) for s in suppliers]

    def update_supplier(
        self,
        supplier_id: int,
        supplier_data: SupplierUpdate
    ) -> Optional[SupplierResponse]:
        """Update supplier"""
        supplier = self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return None

        try:
            for key, value in supplier_data.dict(exclude_unset=True).items():
                setattr(supplier, key, value)
            
            self.db.commit()
            self.db.refresh(supplier)
            
            logger.info(f"Updated supplier: {supplier.name} (ID: {supplier.id})")
            return SupplierResponse.from_orm(supplier)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating supplier: {str(e)}")
            raise

    def delete_supplier(self, supplier_id: int) -> bool:
        """Delete supplier (soft delete by setting is_active=False)"""
        supplier = self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return False

        try:
            supplier.is_active = False
            self.db.commit()
            logger.info(f"Deleted supplier: {supplier.name} (ID: {supplier.id})")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting supplier: {str(e)}")
            raise

    # ==================== Product-Supplier Management ====================

    def add_product_supplier(
        self,
        product_supplier_data: ProductSupplierCreate
    ) -> Dict[str, Any]:
        """Add supplier for a product"""
        try:
            product_supplier = ProductSupplier(**product_supplier_data.dict())
            self.db.add(product_supplier)
            self.db.commit()
            self.db.refresh(product_supplier)
            
            logger.info(f"Added supplier {product_supplier.supplier_id} for product {product_supplier.product_id}")
            return {"success": True, "data": product_supplier}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding product supplier: {str(e)}")
            raise

    def get_product_suppliers(self, product_id: int) -> List[Dict[str, Any]]:
        """Get all suppliers for a product"""
        suppliers = self.db.query(ProductSupplier).filter(
            ProductSupplier.product_id == product_id,
            ProductSupplier.is_active == True
        ).all()
        
        return [
            {
                "id": ps.id,
                "supplier_id": ps.supplier_id,
                "supplier_sku": ps.supplier_sku,
                "cost_price": ps.cost_price,
                "minimum_order_quantity": ps.minimum_order_quantity,
                "lead_time_days": ps.lead_time_days,
                "is_preferred": ps.is_preferred
            }
            for ps in suppliers
        ]

    def get_preferred_supplier(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get preferred supplier for a product"""
        supplier = self.db.query(ProductSupplier).filter(
            ProductSupplier.product_id == product_id,
            ProductSupplier.is_preferred == True,
            ProductSupplier.is_active == True
        ).first()
        
        if supplier:
            return {
                "supplier_id": supplier.supplier_id,
                "cost_price": supplier.cost_price,
                "minimum_order_quantity": supplier.minimum_order_quantity,
                "lead_time_days": supplier.lead_time_days
            }
        return None

    # ==================== Stock Management ====================

    def create_stock(self, stock_data: InventoryStockCreate) -> InventoryStockResponse:
        """Create inventory stock for a product"""
        try:
            stock = InventoryStock(**stock_data.dict())
            stock.quantity_available = stock.quantity_on_hand - stock.quantity_reserved
            stock.stock_status = self._calculate_stock_status(stock)
            
            self.db.add(stock)
            self.db.commit()
            self.db.refresh(stock)
            
            logger.info(f"Created stock for product {stock.product_id}")
            return InventoryStockResponse.from_orm(stock)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating stock: {str(e)}")
            raise

    def get_stock(self, product_id: int) -> Optional[InventoryStockResponse]:
        """Get stock for a product"""
        stock = self.db.query(InventoryStock).filter(
            InventoryStock.product_id == product_id
        ).first()
        return InventoryStockResponse.from_orm(stock) if stock else None

    def update_stock(
        self,
        product_id: int,
        stock_data: InventoryStockUpdate
    ) -> Optional[InventoryStockResponse]:
        """Update stock"""
        stock = self.db.query(InventoryStock).filter(
            InventoryStock.product_id == product_id
        ).first()
        
        if not stock:
            return None

        try:
            for key, value in stock_data.dict(exclude_unset=True).items():
                setattr(stock, key, value)
            
            stock.quantity_available = stock.quantity_on_hand - stock.quantity_reserved
            stock.stock_status = self._calculate_stock_status(stock)
            
            self.db.commit()
            self.db.refresh(stock)
            
            # Check for low stock alerts
            self._check_stock_alerts(stock)
            
            logger.info(f"Updated stock for product {product_id}")
            return InventoryStockResponse.from_orm(stock)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating stock: {str(e)}")
            raise

    def adjust_stock(self, adjustment: StockAdjustment) -> Dict[str, Any]:
        """Adjust stock quantity"""
        stock = self.db.query(InventoryStock).filter(
            InventoryStock.product_id == adjustment.product_id
        ).first()
        
        if not stock:
            raise ValueError(f"Stock not found for product {adjustment.product_id}")

        try:
            quantity_before = stock.quantity_on_hand
            stock.quantity_on_hand += adjustment.quantity_change
            stock.quantity_available = stock.quantity_on_hand - stock.quantity_reserved
            stock.stock_status = self._calculate_stock_status(stock)
            
            # Create transaction record
            transaction = InventoryTransaction(
                stock_id=stock.id,
                transaction_type=TransactionType.ADJUSTMENT,
                quantity=abs(adjustment.quantity_change),
                quantity_before=quantity_before,
                quantity_after=stock.quantity_on_hand,
                notes=adjustment.notes,
                performed_by=adjustment.performed_by
            )
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(stock)
            
            # Check for alerts
            self._check_stock_alerts(stock)
            
            logger.info(f"Adjusted stock for product {adjustment.product_id}: {adjustment.quantity_change}")
            return {
                "success": True,
                "quantity_before": quantity_before,
                "quantity_after": stock.quantity_on_hand,
                "stock_status": stock.stock_status.value
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adjusting stock: {str(e)}")
            raise

    def _calculate_stock_status(self, stock: InventoryStock) -> StockStatus:
        """Calculate stock status based on quantity"""
        if stock.quantity_available <= 0:
            return StockStatus.OUT_OF_STOCK
        elif stock.quantity_available <= stock.reorder_point:
            return StockStatus.LOW_STOCK
        else:
            return StockStatus.IN_STOCK

    # ==================== Stock Alerts ====================

    def _check_stock_alerts(self, stock: InventoryStock):
        """Check and create stock alerts if needed"""
        try:
            # Check if alert already exists and is not resolved
            existing_alert = self.db.query(StockAlert).filter(
                StockAlert.stock_id == stock.id,
                StockAlert.is_resolved == False
            ).first()
            
            if stock.stock_status == StockStatus.OUT_OF_STOCK:
                if not existing_alert or existing_alert.alert_type != "out_of_stock":
                    alert = StockAlert(
                        product_id=stock.product_id,
                        stock_id=stock.id,
                        alert_type="out_of_stock",
                        message=f"Product {stock.product_id} is out of stock",
                        severity="critical"
                    )
                    self.db.add(alert)
                    
            elif stock.stock_status == StockStatus.LOW_STOCK:
                if not existing_alert or existing_alert.alert_type != "low_stock":
                    alert = StockAlert(
                        product_id=stock.product_id,
                        stock_id=stock.id,
                        alert_type="low_stock",
                        message=f"Product {stock.product_id} is low on stock ({stock.quantity_available} units)",
                        severity="warning"
                    )
                    self.db.add(alert)
            
            elif stock.quantity_available <= stock.reorder_point:
                if not existing_alert or existing_alert.alert_type != "reorder_point":
                    alert = StockAlert(
                        product_id=stock.product_id,
                        stock_id=stock.id,
                        alert_type="reorder_point",
                        message=f"Product {stock.product_id} has reached reorder point",
                        severity="info"
                    )
                    self.db.add(alert)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error checking stock alerts: {str(e)}")

    def get_stock_alerts(
        self,
        is_resolved: Optional[bool] = False,
        severity: Optional[str] = None
    ) -> List[StockAlertResponse]:
        """Get stock alerts"""
        query = self.db.query(StockAlert)
        
        if is_resolved is not None:
            query = query.filter(StockAlert.is_resolved == is_resolved)
        
        if severity:
            query = query.filter(StockAlert.severity == severity)
        
        alerts = query.order_by(StockAlert.created_at.desc()).all()
        return [StockAlertResponse.from_orm(alert) for alert in alerts]

    def acknowledge_alert(self, alert_id: int, acknowledged_by: str) -> bool:
        """Acknowledge a stock alert"""
        alert = self.db.query(StockAlert).filter(StockAlert.id == alert_id).first()
        if not alert:
            return False

        try:
            alert.is_acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error acknowledging alert: {str(e)}")
            raise

    def resolve_alert(self, alert_id: int) -> bool:
        """Resolve a stock alert"""
        alert = self.db.query(StockAlert).filter(StockAlert.id == alert_id).first()
        if not alert:
            return False

        try:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resolving alert: {str(e)}")
            raise

    # ==================== Reorder Calculations ====================

    def calculate_reorder_needs(self) -> List[ReorderCalculation]:
        """Calculate products that need reordering"""
        stocks = self.db.query(InventoryStock).filter(
            InventoryStock.quantity_available <= InventoryStock.reorder_point
        ).all()
        
        reorder_list = []
        for stock in stocks:
            preferred_supplier = self.get_preferred_supplier(stock.product_id)
            
            if preferred_supplier:
                estimated_cost = stock.reorder_quantity * preferred_supplier["cost_price"]
                lead_time = preferred_supplier["lead_time_days"]
                supplier_id = preferred_supplier["supplier_id"]
            else:
                estimated_cost = 0.0
                lead_time = 14
                supplier_id = None
            
            reorder = ReorderCalculation(
                product_id=stock.product_id,
                current_stock=stock.quantity_available,
                reorder_point=stock.reorder_point,
                reorder_quantity=stock.reorder_quantity,
                recommended_order_quantity=stock.reorder_quantity,
                estimated_cost=estimated_cost,
                preferred_supplier_id=supplier_id,
                lead_time_days=lead_time
            )
            reorder_list.append(reorder)
        
        return reorder_list

    # ==================== Purchase Orders ====================

    def create_purchase_order(
        self,
        po_data: PurchaseOrderCreate,
        created_by: str
    ) -> PurchaseOrderResponse:
        """Create a new purchase order"""
        try:
            # Generate order number
            order_number = self._generate_order_number()
            
            # Calculate totals
            subtotal = sum(item.quantity_ordered * item.unit_cost for item in po_data.items)
            tax_amount = subtotal * 0.19  # 19% VAT (German standard)
            total_amount = subtotal + tax_amount + po_data.shipping_cost
            
            # Create purchase order
            po = PurchaseOrder(
                order_number=order_number,
                supplier_id=po_data.supplier_id,
                expected_delivery_date=po_data.expected_delivery_date,
                shipping_cost=po_data.shipping_cost,
                notes=po_data.notes,
                shipping_address=po_data.shipping_address,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                created_by=created_by
            )
            
            self.db.add(po)
            self.db.flush()
            
            # Create purchase order items
            for item_data in po_data.items:
                total_cost = item_data.quantity_ordered * item_data.unit_cost
                item = PurchaseOrderItem(
                    purchase_order_id=po.id,
                    product_id=item_data.product_id,
                    quantity_ordered=item_data.quantity_ordered,
                    unit_cost=item_data.unit_cost,
                    total_cost=total_cost,
                    notes=item_data.notes
                )
                self.db.add(item)
            
            self.db.commit()
            self.db.refresh(po)
            
            logger.info(f"Created purchase order: {order_number}")
            return PurchaseOrderResponse.from_orm(po)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating purchase order: {str(e)}")
            raise

    def _generate_order_number(self) -> str:
        """Generate unique purchase order number"""
        today = datetime.now()
        prefix = f"PO-{today.year}{today.month:02d}"
        
        # Get last order number for this month
        last_po = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.order_number.like(f"{prefix}%")
        ).order_by(PurchaseOrder.order_number.desc()).first()
        
        if last_po:
            last_num = int(last_po.order_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}-{new_num:04d}"

    def get_purchase_order(self, po_id: int) -> Optional[PurchaseOrderResponse]:
        """Get purchase order by ID"""
        po = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        return PurchaseOrderResponse.from_orm(po) if po else None

    def get_purchase_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[PurchaseOrderStatusEnum] = None,
        supplier_id: Optional[int] = None
    ) -> List[PurchaseOrderResponse]:
        """Get list of purchase orders"""
        query = self.db.query(PurchaseOrder)
        
        if status:
            query = query.filter(PurchaseOrder.status == status.value)
        
        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)
        
        orders = query.order_by(PurchaseOrder.order_date.desc()).offset(skip).limit(limit).all()
        return [PurchaseOrderResponse.from_orm(po) for po in orders]

    def update_purchase_order_status(
        self,
        po_id: int,
        status: PurchaseOrderStatusEnum,
        approved_by: Optional[str] = None
    ) -> Optional[PurchaseOrderResponse]:
        """Update purchase order status"""
        po = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            return None

        try:
            po.status = status.value
            
            if status == PurchaseOrderStatusEnum.APPROVED and approved_by:
                po.approved_by = approved_by
                po.approved_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(po)
            
            logger.info(f"Updated purchase order {po.order_number} status to {status.value}")
            return PurchaseOrderResponse.from_orm(po)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating purchase order status: {str(e)}")
            raise

    def receive_purchase_order(
        self,
        po_id: int,
        received_items: Dict[int, int]  # {product_id: quantity_received}
    ) -> Dict[str, Any]:
        """Receive items from a purchase order"""
        po = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            raise ValueError(f"Purchase order {po_id} not found")

        try:
            for item in po.items:
                if item.product_id in received_items:
                    quantity_received = received_items[item.product_id]
                    item.quantity_received += quantity_received
                    
                    # Update stock
                    stock = self.db.query(InventoryStock).filter(
                        InventoryStock.product_id == item.product_id
                    ).first()
                    
                    if stock:
                        quantity_before = stock.quantity_on_hand
                        stock.quantity_on_hand += quantity_received
                        stock.quantity_available = stock.quantity_on_hand - stock.quantity_reserved
                        stock.stock_status = self._calculate_stock_status(stock)
                        stock.last_restock_at = datetime.utcnow()
                        
                        # Create transaction
                        transaction = InventoryTransaction(
                            stock_id=stock.id,
                            transaction_type=TransactionType.PURCHASE,
                            quantity=quantity_received,
                            quantity_before=quantity_before,
                            quantity_after=stock.quantity_on_hand,
                            reference_type="purchase_order",
                            reference_id=po.id,
                            unit_cost=item.unit_cost,
                            total_cost=quantity_received * item.unit_cost
                        )
                        self.db.add(transaction)
            
            # Check if all items are fully received
            all_received = all(
                item.quantity_received >= item.quantity_ordered
                for item in po.items
            )
            
            if all_received:
                po.status = PurchaseOrderStatus.RECEIVED
                po.actual_delivery_date = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Received items for purchase order {po.order_number}")
            return {
                "success": True,
                "order_number": po.order_number,
                "status": po.status.value,
                "all_received": all_received
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error receiving purchase order: {str(e)}")
            raise

    # ==================== Inventory Reports ====================

    def get_inventory_report(self) -> InventoryReport:
        """Generate comprehensive inventory report"""
        total_products = self.db.query(func.count(InventoryStock.id)).scalar()
        
        products_in_stock = self.db.query(func.count(InventoryStock.id)).filter(
            InventoryStock.stock_status == StockStatus.IN_STOCK
        ).scalar()
        
        products_low_stock = self.db.query(func.count(InventoryStock.id)).filter(
            InventoryStock.stock_status == StockStatus.LOW_STOCK
        ).scalar()
        
        products_out_of_stock = self.db.query(func.count(InventoryStock.id)).filter(
            InventoryStock.stock_status == StockStatus.OUT_OF_STOCK
        ).scalar()
        
        products_needing_reorder = self.db.query(func.count(InventoryStock.id)).filter(
            InventoryStock.quantity_available <= InventoryStock.reorder_point
        ).scalar()
        
        avg_stock = self.db.query(func.avg(InventoryStock.quantity_available)).scalar() or 0.0
        
        # Calculate total stock value (simplified - would need product prices)
        total_stock_value = 0.0
        
        return InventoryReport(
            total_products=total_products or 0,
            total_stock_value=total_stock_value,
            products_in_stock=products_in_stock or 0,
            products_low_stock=products_low_stock or 0,
            products_out_of_stock=products_out_of_stock or 0,
            products_needing_reorder=products_needing_reorder or 0,
            average_stock_level=float(avg_stock),
            report_date=datetime.utcnow()
        )

    def get_supplier_performance(self, supplier_id: int) -> Optional[SupplierPerformance]:
        """Get supplier performance metrics"""
        supplier = self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return None

        total_orders = self.db.query(func.count(PurchaseOrder.id)).filter(
            PurchaseOrder.supplier_id == supplier_id
        ).scalar() or 0
        
        # Calculate on-time deliveries
        completed_orders = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.supplier_id == supplier_id,
            PurchaseOrder.status == PurchaseOrderStatus.RECEIVED
        ).all()
        
        on_time = sum(
            1 for po in completed_orders
            if po.actual_delivery_date and po.expected_delivery_date
            and po.actual_delivery_date <= po.expected_delivery_date
        )
        
        late = len(completed_orders) - on_time
        
        # Calculate average lead time
        lead_times = [
            (po.actual_delivery_date - po.order_date).days
            for po in completed_orders
            if po.actual_delivery_date
        ]
        avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0.0
        
        # Calculate total spend
        total_spend = self.db.query(func.sum(PurchaseOrder.total_amount)).filter(
            PurchaseOrder.supplier_id == supplier_id,
            PurchaseOrder.status.in_([
                PurchaseOrderStatus.APPROVED,
                PurchaseOrderStatus.ORDERED,
                PurchaseOrderStatus.RECEIVED
            ])
        ).scalar() or 0.0
        
        return SupplierPerformance(
            supplier_id=supplier.id,
            supplier_name=supplier.name,
            total_orders=total_orders,
            on_time_deliveries=on_time,
            late_deliveries=late,
            average_lead_time_days=avg_lead_time,
            total_spend=float(total_spend),
            rating=supplier.rating
        )
