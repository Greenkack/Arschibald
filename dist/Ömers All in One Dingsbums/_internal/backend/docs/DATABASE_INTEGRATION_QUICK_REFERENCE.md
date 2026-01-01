# Database Integration - Quick Reference

Quick reference for Task 222: Database Integration

## Quick Start

```python
from backend.models.database_models import Customer
from backend.core.dynamic_keys import KeyPrefix
from backend.services.universal_data_service import UniversalDataService

# Initialize service
service = UniversalDataService(db)

# Create record
customer = Customer(name="Test Customer")
db.add(customer)
db.commit()
db.refresh(customer)

# Generate key and PDF
key, pdf = service.generate_key_and_pdf(customer, KeyPrefix.CUSTOMER)
```

## Common Operations

### Generate Dynamic Key

```python
key = service.generate_key_for_record(record, KeyPrefix.CUSTOMER)
```

### Generate PDF

```python
pdf_bytes = service.generate_pdf_for_record(record)
```

### Bulk Generate Keys

```python
keys = service.bulk_generate_keys(records, KeyPrefix.CUSTOMER)
```

### Bulk Generate PDFs

```python
pdfs = service.bulk_generate_pdfs(records)
```

### Find by Key

```python
record = service.get_by_dynamic_key(Customer, "CUS_20241116_...")
```

### Find by Prefix

```python
records = service.get_by_prefix(Customer, "CUS")
```

### Get Formatted Data

```python
data = service.get_formatted_data(record, locale='de-DE')
```

### Get Statistics

```python
stats = service.get_statistics(Customer)
```

## Key Prefixes

| Prefix | Type | Example |
|--------|------|---------|
| `USR` | User | `USR_20241116_143052_a1b2c3d4` |
| `CUS` | Customer | `CUS_20241116_143052_a1b2c3d4` |
| `PRJ` | Project | `PRJ_20241116_143052_a1b2c3d4` |
| `SOL` | Solar Calculation | `SOL_20241116_143052_a1b2c3d4` |
| `PRD` | Product | `PRD_20241116_143052_a1b2c3d4` |
| `OFF` | Offer | `OFF_20241116_143052_a1b2c3d4` |
| `TSK` | Task | `TSK_20241116_143052_a1b2c3d4` |

## Database Models

All models inherit from `UniversalDatabaseModel`:

- `User` - User accounts
- `Customer` - Customer information
- `Project` - Projects
- `SolarCalculation` - Solar calculations
- `Product` - Products
- `Offer` - Sales offers
- `Task` - Tasks

## Migration

```bash
# Dry run
python backend/migrations/add_universal_columns.py --dry-run

# Apply
python backend/migrations/add_universal_columns.py
```

## Batch Operations

```python
from backend.services.universal_data_service import BulkPDFGenerator

generator = BulkPDFGenerator(db)

results = generator.generate_pdfs_batch(
    records,
    batch_size=100,
    progress_callback=lambda c, t: print(f"{c}/{t}")
)
```

## Error Handling

```python
try:
    key = service.generate_key_for_record(record, KeyPrefix.CUSTOMER)
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

1. Use bulk operations for multiple records
2. Adjust batch size based on record complexity
3. Use progress callbacks for long operations
4. Delete PDFs when not needed
5. Rebuild index after bulk operations

## Testing

```bash
pytest backend/tests/test_database_integration.py -v
```

## Requirements

- SQLAlchemy >= 1.4
- reportlab >= 3.6
- Python >= 3.10
