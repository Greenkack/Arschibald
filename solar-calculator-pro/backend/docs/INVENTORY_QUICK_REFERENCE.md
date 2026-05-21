# Inventory Management - Quick Reference

## Quick Start

```python
from backend.services.inventory_service import InventoryService

service = InventoryService(db)
```

## Common Operations

### Create Supplier
```python
supplier = service.create_supplier(SupplierCreate(
    name="Supplier Name",
    code="SUP-001",
    email="contact@supplier.com"
))
```

### Create Stock
```python
stock = service.create_stock(InventoryStockCreate(
    product_id=1,
    quantity_on_hand=100,
    reorder_point=20,
    reorder_quantity=50
))
```

### Adjust Stock
```python
result = service.adjust_stock(StockAdjustment(
    product_id=1,
    quantity_change=-10,
    reason="Sale",
    performed_by="admin"
))
```

### Check Reorder Needs
```python
reorder_list = service.calculate_reorder_needs()
```

### Create Purchase Order
```python
po = service.create_purchase_order(
    PurchaseOrderCreate(
        supplier_id=1,
        items=[
            PurchaseOrderItemCreate(
                product_id=1,
                quantity_ordered=50,
                unit_cost=250.00
            )
        ]
    ),
    created_by="admin"
)
```

### Receive Purchase Order
```python
result = service.receive_purchase_order(
    po_id=1,
    received_items={1: 50, 2: 30}
)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/inventory/suppliers` | POST | Create supplier |
| `/inventory/suppliers` | GET | List suppliers |
| `/inventory/suppliers/{id}` | GET | Get supplier |
| `/inventory/suppliers/{id}` | PUT | Update supplier |
| `/inventory/stock` | POST | Create stock |
| `/inventory/stock/{product_id}` | GET | Get stock |
| `/inventory/stock/adjust` | POST | Adjust stock |
| `/inventory/alerts` | GET | Get alerts |
| `/inventory/reorder/calculate` | GET | Calculate reorder needs |
| `/inventory/purchase-orders` | POST | Create PO |
| `/inventory/purchase-orders` | GET | List POs |
| `/inventory/purchase-orders/{id}/receive` | POST | Receive PO |
| `/inventory/reports/inventory` | GET | Inventory report |
| `/inventory/reports/supplier/{id}/performance` | GET | Supplier performance |

## Stock Status

- **IN_STOCK**: Available > Reorder Point
- **LOW_STOCK**: 0 < Available ≤ Reorder Point
- **OUT_OF_STOCK**: Available ≤ 0
- **DISCONTINUED**: Product no longer available

## Purchase Order Status

- **DRAFT**: Initial creation
- **PENDING**: Awaiting approval
- **APPROVED**: Approved, ready to order
- **ORDERED**: Sent to supplier
- **RECEIVED**: Items received
- **CANCELLED**: Order cancelled

## Alert Severity

- **INFO**: Informational (reorder point reached)
- **WARNING**: Low stock
- **CRITICAL**: Out of stock

## Formulas

### Reorder Point
```
Reorder Point = (Average Daily Usage × Lead Time) + Safety Stock
```

### Available Quantity
```
Available = On Hand - Reserved
```

### Order Total
```
Total = Subtotal + Tax + Shipping
Tax = Subtotal × 0.19 (19% VAT)
```

## German Number Formatting

All prices and quantities use German formatting:
- Decimal separator: comma (,)
- Thousands separator: dot (.)
- Example: 16.999,00 €

## Common Queries

### Products Needing Reorder
```sql
SELECT * FROM inventory_stock 
WHERE quantity_available <= reorder_point
```

### Active Alerts
```sql
SELECT * FROM stock_alerts 
WHERE is_resolved = FALSE
ORDER BY severity DESC, created_at DESC
```

### Pending Purchase Orders
```sql
SELECT * FROM purchase_orders 
WHERE status IN ('pending', 'approved', 'ordered')
ORDER BY expected_delivery_date ASC
```

## Tips

1. **Set realistic reorder points** based on actual usage patterns
2. **Maintain multiple suppliers** for critical products
3. **Acknowledge alerts promptly** to track response times
4. **Review supplier performance** regularly
5. **Perform stock counts** periodically to verify accuracy
6. **Use warehouse locations** for efficient picking
7. **Track lead times** to improve forecasting
8. **Monitor stock turnover** to identify slow-moving items

## Error Handling

```python
try:
    result = service.adjust_stock(adjustment)
except ValueError as e:
    # Stock not found
    print(f"Error: {e}")
except Exception as e:
    # Other errors
    print(f"Unexpected error: {e}")
```

## Demo Script

Run the demo to see all features:
```bash
python backend/demo_inventory.py
```

## Database Migration

Apply the inventory tables migration:
```bash
alembic upgrade head
```

Or run the migration script directly:
```python
from backend.migrations.add_inventory_tables import upgrade
upgrade()
```
