# Inventory Management System - Complete Guide

## Overview

The Inventory Management System provides comprehensive functionality for tracking stock levels, managing suppliers, creating purchase orders, and generating inventory reports. This system is designed to help businesses maintain optimal stock levels, reduce costs, and improve supply chain efficiency.

## Features

### 1. Stock Tracking
- Real-time inventory levels
- Reserved vs. available quantities
- Warehouse and bin location tracking
- Stock status monitoring (in stock, low stock, out of stock)
- Historical transaction tracking

### 2. Low Stock Alerts
- Automatic alert generation
- Configurable alert thresholds
- Multiple severity levels (info, warning, critical)
- Alert acknowledgment and resolution tracking
- Email notifications (optional)

### 3. Reorder Point Calculations
- Automatic reorder point monitoring
- Recommended order quantity calculations
- Lead time consideration
- Cost estimation
- Preferred supplier identification

### 4. Supplier Management
- Comprehensive supplier database
- Contact information and payment terms
- Supplier rating system
- Performance metrics tracking
- Multiple suppliers per product

### 5. Purchase Orders
- Complete purchase order lifecycle
- Multi-item orders
- Status tracking (draft, pending, approved, ordered, received)
- Automatic order number generation
- Receiving and inventory updates
- Cost tracking and reporting

### 6. Inventory Reports
- Comprehensive inventory overview
- Stock value calculations
- Product status summaries
- Supplier performance reports
- Custom date range reports

## Architecture

### Database Models

#### Supplier
- Basic information (name, code, contact details)
- Business details (tax ID, payment terms, currency)
- Rating and notes
- Timestamps

#### ProductSupplier
- Links products to suppliers
- Supplier-specific SKU
- Cost price and MOQ (Minimum Order Quantity)
- Lead time
- Preferred supplier flag

#### InventoryStock
- Product stock levels
- Reorder settings
- Location information
- Stock status
- Last counted/restocked dates

#### InventoryTransaction
- Transaction history
- Type (purchase, sale, adjustment, return, transfer, damage)
- Quantity changes
- Cost tracking
- Reference to source (PO, sale, etc.)

#### PurchaseOrder
- Order header information
- Supplier reference
- Status and dates
- Financial totals
- Approval tracking

#### PurchaseOrderItem
- Line items for purchase orders
- Product and quantity
- Pricing
- Received quantity tracking

#### StockAlert
- Alert information
- Severity level
- Acknowledgment tracking
- Resolution status

## API Endpoints

### Supplier Management

#### Create Supplier
```http
POST /api/v1/inventory/suppliers
Content-Type: application/json

{
  "name": "Solar Tech GmbH",
  "code": "ST-001",
  "contact_person": "Hans Mueller",
  "email": "hans@solartech.de",
  "phone": "+49 30 12345678",
  "address": "Hauptstrasse 123",
  "city": "Berlin",
  "country": "Germany",
  "postal_code": "10115",
  "payment_terms": "Net 30",
  "currency": "EUR",
  "rating": 4.5
}
```

#### Get Suppliers
```http
GET /api/v1/inventory/suppliers?skip=0&limit=100&is_active=true
```

#### Update Supplier
```http
PUT /api/v1/inventory/suppliers/{supplier_id}
Content-Type: application/json

{
  "rating": 4.8,
  "notes": "Excellent service and on-time delivery"
}
```

### Stock Management

#### Create Stock
```http
POST /api/v1/inventory/stock
Content-Type: application/json

{
  "product_id": 1,
  "quantity_on_hand": 100,
  "quantity_reserved": 10,
  "reorder_point": 20,
  "reorder_quantity": 50,
  "minimum_stock_level": 10,
  "maximum_stock_level": 500,
  "warehouse_location": "Warehouse A",
  "bin_location": "A-12-03"
}
```

#### Get Stock
```http
GET /api/v1/inventory/stock/{product_id}
```

#### Adjust Stock
```http
POST /api/v1/inventory/stock/adjust
Content-Type: application/json

{
  "product_id": 1,
  "quantity_change": -25,
  "reason": "Sale to customer",
  "notes": "Order #12345",
  "performed_by": "admin"
}
```

### Stock Alerts

#### Get Alerts
```http
GET /api/v1/inventory/alerts?is_resolved=false&severity=warning
```

#### Acknowledge Alert
```http
POST /api/v1/inventory/alerts/{alert_id}/acknowledge?acknowledged_by=admin
```

#### Resolve Alert
```http
POST /api/v1/inventory/alerts/{alert_id}/resolve
```

### Reorder Management

#### Calculate Reorder Needs
```http
GET /api/v1/inventory/reorder/calculate
```

Response:
```json
[
  {
    "product_id": 1,
    "current_stock": 15,
    "reorder_point": 20,
    "reorder_quantity": 50,
    "recommended_order_quantity": 50,
    "estimated_cost": 12500.00,
    "preferred_supplier_id": 1,
    "lead_time_days": 14
  }
]
```

### Purchase Orders

#### Create Purchase Order
```http
POST /api/v1/inventory/purchase-orders?created_by=admin
Content-Type: application/json

{
  "supplier_id": 1,
  "expected_delivery_date": "2024-02-15T00:00:00Z",
  "shipping_cost": 50.00,
  "notes": "Restock order",
  "shipping_address": "Warehouse A, Berlin",
  "items": [
    {
      "product_id": 1,
      "quantity_ordered": 50,
      "unit_cost": 250.00,
      "notes": "Standard reorder"
    }
  ]
}
```

#### Get Purchase Orders
```http
GET /api/v1/inventory/purchase-orders?status=approved&supplier_id=1
```

#### Update PO Status
```http
PUT /api/v1/inventory/purchase-orders/{po_id}/status?status=approved&approved_by=manager
```

#### Receive Purchase Order
```http
POST /api/v1/inventory/purchase-orders/{po_id}/receive
Content-Type: application/json

{
  "1": 50,
  "2": 30
}
```

### Reports

#### Inventory Report
```http
GET /api/v1/inventory/reports/inventory
```

Response:
```json
{
  "total_products": 150,
  "total_stock_value": 125000.00,
  "products_in_stock": 120,
  "products_low_stock": 20,
  "products_out_of_stock": 10,
  "products_needing_reorder": 25,
  "average_stock_level": 45.5,
  "report_date": "2024-01-15T10:30:00Z"
}
```

#### Supplier Performance
```http
GET /api/v1/inventory/reports/supplier/{supplier_id}/performance
```

Response:
```json
{
  "supplier_id": 1,
  "supplier_name": "Solar Tech GmbH",
  "total_orders": 25,
  "on_time_deliveries": 22,
  "late_deliveries": 3,
  "average_lead_time_days": 15.5,
  "total_spend": 125000.00,
  "rating": 4.5
}
```

## Usage Examples

### Python Service Usage

```python
from backend.services.inventory_service import InventoryService
from backend.models.inventory_schemas import (
    SupplierCreate, InventoryStockCreate, PurchaseOrderCreate
)

# Initialize service
service = InventoryService(db)

# Create supplier
supplier = service.create_supplier(SupplierCreate(
    name="Solar Tech GmbH",
    code="ST-001",
    email="contact@solartech.de",
    payment_terms="Net 30"
))

# Create stock
stock = service.create_stock(InventoryStockCreate(
    product_id=1,
    quantity_on_hand=100,
    reorder_point=20,
    reorder_quantity=50
))

# Check reorder needs
reorder_list = service.calculate_reorder_needs()
for item in reorder_list:
    print(f"Product {item.product_id} needs {item.recommended_order_quantity} units")

# Create purchase order
po = service.create_purchase_order(
    PurchaseOrderCreate(
        supplier_id=supplier.id,
        items=[...]
    ),
    created_by="admin"
)
```

## Best Practices

### 1. Stock Management
- Perform regular stock counts
- Update reorder points based on demand patterns
- Use warehouse and bin locations for efficient picking
- Track reserved quantities for pending orders

### 2. Supplier Management
- Maintain multiple suppliers for critical products
- Update supplier ratings regularly
- Review supplier performance quarterly
- Negotiate better terms with high-performing suppliers

### 3. Purchase Orders
- Approve orders before sending to suppliers
- Track expected vs. actual delivery dates
- Receive items promptly to update inventory
- Review and resolve discrepancies immediately

### 4. Alerts and Monitoring
- Acknowledge alerts promptly
- Investigate root causes of stock issues
- Adjust reorder points based on alert frequency
- Set up email notifications for critical alerts

### 5. Reporting
- Generate inventory reports weekly
- Review supplier performance monthly
- Analyze stock turnover rates
- Identify slow-moving inventory

## Configuration

### Reorder Point Calculation

The reorder point should be set based on:
- Average daily usage
- Lead time from supplier
- Safety stock buffer

Formula:
```
Reorder Point = (Average Daily Usage × Lead Time) + Safety Stock
```

Example:
- Average daily usage: 5 units
- Lead time: 14 days
- Safety stock: 20 units
- Reorder point: (5 × 14) + 20 = 90 units

### Stock Status Thresholds

- **In Stock**: quantity_available > reorder_point
- **Low Stock**: 0 < quantity_available ≤ reorder_point
- **Out of Stock**: quantity_available ≤ 0

## Troubleshooting

### Common Issues

#### Stock Not Updating After PO Receipt
- Verify PO status is "received"
- Check that product IDs match
- Ensure stock record exists for product
- Review transaction log for errors

#### Alerts Not Generating
- Verify stock status is being calculated
- Check alert thresholds are set correctly
- Ensure stock updates trigger alert checks
- Review alert resolution status

#### Supplier Performance Incorrect
- Verify PO dates are set correctly
- Check that POs are marked as received
- Ensure delivery dates are recorded
- Review calculation logic for edge cases

## Security Considerations

- Implement role-based access control
- Audit all stock adjustments
- Require approval for large purchase orders
- Log all inventory transactions
- Encrypt sensitive supplier information

## Performance Optimization

- Index frequently queried fields
- Cache reorder calculations
- Batch process stock updates
- Archive old transactions
- Optimize report queries

## Future Enhancements

- Barcode scanning integration
- Automated reordering
- Demand forecasting
- Multi-warehouse support
- Integration with accounting systems
- Mobile app for stock counting
- Real-time dashboard
- Advanced analytics and insights

## Support

For issues or questions:
- Check the API documentation
- Review the demo script
- Contact the development team
- Submit bug reports via issue tracker
