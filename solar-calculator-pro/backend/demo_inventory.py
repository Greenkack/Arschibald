"""
Inventory Management Demo

This script demonstrates the inventory management system functionality.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.core.database import SessionLocal
from backend.services.inventory_service import InventoryService
from backend.models.inventory_schemas import (
    SupplierCreate, ProductSupplierCreate,
    InventoryStockCreate, StockAdjustment,
    PurchaseOrderCreate, PurchaseOrderItemCreate,
    PurchaseOrderStatusEnum
)


def demo_inventory_management():
    """Demonstrate inventory management features"""
    db = SessionLocal()
    service = InventoryService(db)
    
    print("=" * 80)
    print("INVENTORY MANAGEMENT SYSTEM DEMO")
    print("=" * 80)
    
    try:
        # ==================== Supplier Management ====================
        print("\n1. SUPPLIER MANAGEMENT")
        print("-" * 80)
        
        # Create suppliers
        supplier1 = service.create_supplier(SupplierCreate(
            name="Solar Tech GmbH",
            code="ST-001",
            contact_person="Hans Mueller",
            email="hans@solartech.de",
            phone="+49 30 12345678",
            address="Hauptstrasse 123",
            city="Berlin",
            country="Germany",
            postal_code="10115",
            payment_terms="Net 30",
            currency="EUR",
            rating=4.5
        ))
        print(f" Created supplier: {supplier1.name} (ID: {supplier1.id})")
        
        supplier2 = service.create_supplier(SupplierCreate(
            name="Energy Components AG",
            code="EC-001",
            contact_person="Maria Schmidt",
            email="maria@energycomp.de",
            phone="+49 89 98765432",
            address="Industrieweg 45",
            city="Munich",
            country="Germany",
            postal_code="80331",
            payment_terms="Net 60",
            currency="EUR",
            rating=4.8
        ))
        print(f" Created supplier: {supplier2.name} (ID: {supplier2.id})")
        
        # ==================== Product-Supplier Relationships ====================
        print("\n2. PRODUCT-SUPPLIER RELATIONSHIPS")
        print("-" * 80)
        
        # Assuming product IDs 1, 2, 3 exist
        product_id_1 = 1
        product_id_2 = 2
        
        # Add suppliers for products
        ps1 = service.add_product_supplier(ProductSupplierCreate(
            product_id=product_id_1,
            supplier_id=supplier1.id,
            supplier_sku="ST-PV-400W",
            cost_price=250.00,
            minimum_order_quantity=10,
            lead_time_days=14,
            is_preferred=True
        ))
        print(f" Added supplier {supplier1.name} for product {product_id_1}")
        print(f"  Cost: €{250.00:.2f}, MOQ: 10, Lead time: 14 days")
        
        ps2 = service.add_product_supplier(ProductSupplierCreate(
            product_id=product_id_1,
            supplier_id=supplier2.id,
            supplier_sku="EC-PV-400W-ALT",
            cost_price=260.00,
            minimum_order_quantity=5,
            lead_time_days=21,
            is_preferred=False
        ))
        print(f" Added alternative supplier {supplier2.name} for product {product_id_1}")
        print(f"  Cost: €{260.00:.2f}, MOQ: 5, Lead time: 21 days")
        
        # ==================== Stock Management ====================
        print("\n3. STOCK MANAGEMENT")
        print("-" * 80)
        
        # Create stock for products
        stock1 = service.create_stock(InventoryStockCreate(
            product_id=product_id_1,
            quantity_on_hand=100,
            quantity_reserved=10,
            reorder_point=20,
            reorder_quantity=50,
            minimum_stock_level=10,
            maximum_stock_level=500,
            warehouse_location="Warehouse A",
            bin_location="A-12-03"
        ))
        print(f" Created stock for product {product_id_1}")
        print(f"  On hand: {stock1.quantity_on_hand}, Available: {stock1.quantity_available}")
        print(f"  Status: {stock1.stock_status.value}")
        print(f"  Location: {stock1.warehouse_location} - {stock1.bin_location}")
        
        stock2 = service.create_stock(InventoryStockCreate(
            product_id=product_id_2,
            quantity_on_hand=15,
            quantity_reserved=5,
            reorder_point=20,
            reorder_quantity=30,
            minimum_stock_level=10,
            maximum_stock_level=200,
            warehouse_location="Warehouse A",
            bin_location="A-15-07"
        ))
        print(f"\n Created stock for product {product_id_2}")
        print(f"  On hand: {stock2.quantity_on_hand}, Available: {stock2.quantity_available}")
        print(f"  Status: {stock2.stock_status.value}")
        
        # ==================== Stock Adjustments ====================
        print("\n4. STOCK ADJUSTMENTS")
        print("-" * 80)
        
        # Adjust stock
        adjustment_result = service.adjust_stock(StockAdjustment(
            product_id=product_id_1,
            quantity_change=-25,
            reason="Sale to customer",
            notes="Order #12345",
            performed_by="admin"
        ))
        print(f" Adjusted stock for product {product_id_1}")
        print(f"  Before: {adjustment_result['quantity_before']}")
        print(f"  After: {adjustment_result['quantity_after']}")
        print(f"  Status: {adjustment_result['stock_status']}")
        
        # ==================== Stock Alerts ====================
        print("\n5. STOCK ALERTS")
        print("-" * 80)
        
        alerts = service.get_stock_alerts(is_resolved=False)
        print(f" Found {len(alerts)} active alerts")
        for alert in alerts:
            print(f"  [{alert.severity.upper()}] {alert.alert_type}: {alert.message}")
            print(f"    Created: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Acknowledge an alert
        if alerts:
            service.acknowledge_alert(alerts[0].id, "admin")
            print(f"\n Acknowledged alert {alerts[0].id}")
        
        # ==================== Reorder Calculations ====================
        print("\n6. REORDER CALCULATIONS")
        print("-" * 80)
        
        reorder_needs = service.calculate_reorder_needs()
        print(f" Found {len(reorder_needs)} products needing reorder")
        for reorder in reorder_needs:
            print(f"\n  Product {reorder.product_id}:")
            print(f"    Current stock: {reorder.current_stock}")
            print(f"    Reorder point: {reorder.reorder_point}")
            print(f"    Recommended quantity: {reorder.recommended_order_quantity}")
            print(f"    Estimated cost: €{reorder.estimated_cost:.2f}")
            print(f"    Lead time: {reorder.lead_time_days} days")
        
        # ==================== Purchase Orders ====================
        print("\n7. PURCHASE ORDERS")
        print("-" * 80)
        
        # Create purchase order
        po = service.create_purchase_order(
            PurchaseOrderCreate(
                supplier_id=supplier1.id,
                expected_delivery_date=datetime.now() + timedelta(days=14),
                shipping_cost=50.00,
                notes="Restock order for low inventory items",
                shipping_address="Warehouse A, Hauptstrasse 123, 10115 Berlin",
                items=[
                    PurchaseOrderItemCreate(
                        product_id=product_id_1,
                        quantity_ordered=50,
                        unit_cost=250.00,
                        notes="Standard reorder"
                    ),
                    PurchaseOrderItemCreate(
                        product_id=product_id_2,
                        quantity_ordered=30,
                        unit_cost=180.00,
                        notes="Low stock reorder"
                    )
                ]
            ),
            created_by="admin"
        )
        print(f" Created purchase order: {po.order_number}")
        print(f"  Supplier: {supplier1.name}")
        print(f"  Status: {po.status.value}")
        print(f"  Items: {len(po.items)}")
        print(f"  Subtotal: €{po.subtotal:.2f}")
        print(f"  Tax: €{po.tax_amount:.2f}")
        print(f"  Shipping: €{po.shipping_cost:.2f}")
        print(f"  Total: €{po.total_amount:.2f}")
        
        # Update PO status
        po_updated = service.update_purchase_order_status(
            po.id,
            PurchaseOrderStatusEnum.APPROVED,
            approved_by="manager"
        )
        print(f"\n Updated purchase order status to: {po_updated.status.value}")
        print(f"  Approved by: {po_updated.approved_by}")
        
        # Receive items
        receive_result = service.receive_purchase_order(
            po.id,
            {
                product_id_1: 50,
                product_id_2: 30
            }
        )
        print(f"\n Received items for purchase order {receive_result['order_number']}")
        print(f"  Status: {receive_result['status']}")
        print(f"  All received: {receive_result['all_received']}")
        
        # ==================== Inventory Reports ====================
        print("\n8. INVENTORY REPORTS")
        print("-" * 80)
        
        report = service.get_inventory_report()
        print(f" Inventory Report (as of {report.report_date.strftime('%Y-%m-%d %H:%M:%S')})")
        print(f"  Total products: {report.total_products}")
        print(f"  Products in stock: {report.products_in_stock}")
        print(f"  Products low stock: {report.products_low_stock}")
        print(f"  Products out of stock: {report.products_out_of_stock}")
        print(f"  Products needing reorder: {report.products_needing_reorder}")
        print(f"  Average stock level: {report.average_stock_level:.2f}")
        print(f"  Total stock value: €{report.total_stock_value:.2f}")
        
        # ==================== Supplier Performance ====================
        print("\n9. SUPPLIER PERFORMANCE")
        print("-" * 80)
        
        performance = service.get_supplier_performance(supplier1.id)
        if performance:
            print(f" Performance metrics for {performance.supplier_name}")
            print(f"  Total orders: {performance.total_orders}")
            print(f"  On-time deliveries: {performance.on_time_deliveries}")
            print(f"  Late deliveries: {performance.late_deliveries}")
            print(f"  Average lead time: {performance.average_lead_time_days:.1f} days")
            print(f"  Total spend: €{performance.total_spend:.2f}")
            print(f"  Rating: {performance.rating:.1f}/5.0")
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    demo_inventory_management()
