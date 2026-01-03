# Database Integration with Universal Data

Complete guide for Task 222: Database Integration

## Overview

This document describes the database integration that adds universal data capabilities to all database tables, including dynamic key generation, PDF byte storage, and bulk operations.

## Features

### 1. Universal Database Columns

All database tables now include:

- **`dynamic_key`**: Unique string identifier for flexible data access
- **`pdf_bytes`**: Binary storage for PDF documents
- **`created_at`**: Timestamp of record creation
- **`updated_at`**: Timestamp of last update

### 2. Dynamic Key System

Every record can have a unique dynamic key generated with:
- Configurable prefix (e.g., `USR_`, `CUS_`, `PRJ_`)
- Timestamp component
- UUID component
- Custom suffixes

Example key: `SOL_20241116_143052_a1b2c3d4`

### 3. PDF Byte Generation

Records can generate and store PDF representations:
- Automatic PDF generation from record data
- German number formatting
- Custom metadata support
- Bulk generation capabilities

### 4. Bulk Operations

Efficient batch processing for:
- Generating keys for multiple records
- Generating PDFs for multiple records
- Combined key and PDF generation
- Progress tracking

## Database Models

### UniversalDatabaseModel

Base class for all database models:

```python
from backend.models.database_models import UniversalDatabaseModel
from backend.core.dynamic_keys import KeyPrefix

class MyModel(UniversalDatabaseModel):
    __tablename__ = "my_table"
    
    name = Column(String(255))
    value = Column(Float)
    
    def _get_default_title(self) -> str:
        return f"My Model: {self.name}"
    
    def _render_to_pdf(self, story, doc):
        # Custom PDF rendering
        pass
```

### Available Models

- **User**: User accounts with authentication
- **Customer**: Customer information
- **Project**: Project management
- **SolarCalculation**: Solar system calculations
- **Product**: Product catalog
- **Offer**: Sales offers
- **Task**: Task management

## Usage Examples

### 1. Creating Records with Keys

```python
from backend.models.database_models import Customer
from backend.core.dynamic_keys import KeyPrefix
from backend.services.universal_data_service import UniversalDataService

# Create customer
customer = Customer(
    name="Solar GmbH",
    email="info@solar.de",
    city="Berlin"
)

db.add(customer)
db.commit()
db.refresh(customer)

# Generate dynamic key
service = UniversalDataService(db)
key = service.generate_key_for_record(customer, KeyPrefix.CUSTOMER)

print(f"Generated key: {key}")
# Output: CUS_20241116_143052_a1b2c3d4_1
```

### 2. Generating PDFs

```python
from backend.core.pdf_bytes import PDFMetadata

# Generate PDF for customer
metadata = PDFMetadata(
    title="Customer Report",
    author="Solar Calculator Pro"
)

pdf_bytes = service.generate_pdf_for_record(customer, metadata)

# Save to file
with open('customer_report.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### 3. Combined Key and PDF Generation

```python
# Generate both key and PDF
key, pdf_bytes = service.generate_key_and_pdf(
    customer,
    KeyPrefix.CUSTOMER,
    metadata
)

print(f"Key: {key}")
print(f"PDF size: {len(pdf_bytes)} bytes")
```

### 4. Bulk Operations

```python
# Create multiple customers
customers = [
    Customer(name=f"Customer {i}")
    for i in range(100)
]

for customer in customers:
    db.add(customer)
db.commit()

# Bulk generate keys
keys = service.bulk_generate_keys(customers, KeyPrefix.CUSTOMER)

# Bulk generate PDFs
pdf_list = service.bulk_generate_pdfs(customers)

print(f"Generated {len(keys)} keys and {len(pdf_list)} PDFs")
```

### 5. Key-Based Lookups

```python
# Find by dynamic key
customer = service.get_by_dynamic_key(Customer, "CUS_20241116_143052_a1b2c3d4")

# Find all by prefix
all_customers = service.get_by_prefix(Customer, "CUS")

# Find records with PDFs
with_pdfs = service.get_records_with_pdf(Customer)
```

### 6. Formatted Data Retrieval

```python
# Get data with German formatting
formatted = service.get_formatted_data(customer, locale='de-DE')

print(formatted['total_cost'])  # "15.000,00"

# Export to JSON
json_str = service.export_to_json(customer)
```

### 7. Batch PDF Generation with Progress

```python
from backend.services.universal_data_service import BulkPDFGenerator

generator = BulkPDFGenerator(db)

def progress_callback(current, total):
    percent = (current / total) * 100
    print(f"Progress: {percent:.1f}% ({current}/{total})")

results = generator.generate_pdfs_batch(
    customers,
    batch_size=50,
    progress_callback=progress_callback
)

print(f"Success rate: {results['success_rate']}%")
```

## Database Migration

### Running the Migration

Add universal columns to existing database:

```bash
# Dry run (no changes)
python backend/migrations/add_universal_columns.py --dry-run

# Apply migration
python backend/migrations/add_universal_columns.py
```

### Migration Features

- Adds `dynamic_key` column to all tables
- Adds `pdf_bytes` column to all tables
- Creates indexes on `dynamic_key` columns
- Handles existing columns gracefully
- Provides detailed progress reporting

### Migration Output

```
============================================================
Universal Data Columns Migration
============================================================
Database: data/app_data.db
Timestamp: 2024-11-16T14:30:52
Commit changes: True
============================================================

Migrating table: customers
  Added 'dynamic_key' column to customers
  Added 'pdf_bytes' column to customers
  Created index idx_customers_dynamic_key

Migrating table: projects
  Added 'dynamic_key' column to projects
  Added 'pdf_bytes' column to projects
  Created index idx_projects_dynamic_key

✓ Changes committed to database

============================================================
Migration Summary
============================================================
Total tables: 15
Migrated tables: 15
Skipped tables: 0
Dynamic key columns added: 15
PDF bytes columns added: 15
Indexes created: 15

✓ No errors
============================================================
```

## Service API Reference

### UniversalDataService

#### Key Generation

- `generate_key_for_record(record, prefix, commit=True)` - Generate key for single record
- `bulk_generate_keys(records, prefix, commit=True)` - Generate keys for multiple records

#### PDF Generation

- `generate_pdf_for_record(record, metadata=None, commit=True)` - Generate PDF for single record
- `bulk_generate_pdfs(records, metadata=None, commit=True)` - Generate PDFs for multiple records

#### Combined Operations

- `generate_key_and_pdf(record, prefix, metadata=None, commit=True)` - Generate both
- `bulk_generate_keys_and_pdfs(records, prefix, metadata=None, commit=True)` - Bulk combined

#### Lookups

- `get_by_dynamic_key(model_class, key)` - Find by key
- `get_by_prefix(model_class, prefix)` - Find by prefix
- `get_records_with_pdf(model_class)` - Find records with PDFs
- `get_records_without_pdf(model_class)` - Find records without PDFs

#### Management

- `regenerate_pdf(record, metadata=None, commit=True)` - Regenerate PDF
- `delete_pdf(record, commit=True)` - Delete PDF bytes
- `get_formatted_data(record, locale='de-DE', include_keys=True)` - Get formatted data
- `export_to_json(record, include_pdf=False)` - Export to JSON
- `get_statistics(model_class)` - Get usage statistics

### BulkPDFGenerator

- `generate_pdfs_batch(records, batch_size=100, metadata=None, progress_callback=None)` - Batch generation
- `regenerate_all_pdfs(model_class, batch_size=100, metadata=None, progress_callback=None)` - Regenerate all

## Statistics and Monitoring

### Get Statistics

```python
stats = service.get_statistics(Customer)

print(f"Total records: {stats['total_records']}")
print(f"With keys: {stats['records_with_keys']}")
print(f"With PDFs: {stats['records_with_pdfs']}")
print(f"Key coverage: {stats['key_coverage_percent']:.1f}%")
print(f"PDF coverage: {stats['pdf_coverage_percent']:.1f}%")
```

### Rebuild Key Index

```python
# Rebuild in-memory index from database
count = service.rebuild_key_index(Customer)
print(f"Indexed {count} keys")
```

## Performance Considerations

### Batch Size

- Default batch size: 100 records
- Adjust based on record complexity and available memory
- Larger batches = faster but more memory
- Smaller batches = slower but less memory

### PDF Generation

- PDF generation is CPU-intensive
- Use batch operations for multiple records
- Consider background jobs for large datasets
- Store PDFs only when needed (can regenerate)

### Indexing

- Dynamic key columns are automatically indexed
- Indexes improve lookup performance
- Rebuild index after bulk operations

## Best Practices

### 1. Always Use Prefixes

```python
# Good
service.generate_key_for_record(customer, KeyPrefix.CUSTOMER)

# Bad
service.generate_key_for_record(customer, KeyPrefix.DATA)
```

### 2. Batch Operations for Multiple Records

```python
# Good
service.bulk_generate_keys(customers, KeyPrefix.CUSTOMER)

# Bad
for customer in customers:
    service.generate_key_for_record(customer, KeyPrefix.CUSTOMER)
```

### 3. Use Progress Callbacks for Long Operations

```python
def progress(current, total):
    print(f"{current}/{total}")

generator.generate_pdfs_batch(
    records,
    progress_callback=progress
)
```

### 4. Handle Errors Gracefully

```python
try:
    pdf_bytes = service.generate_pdf_for_record(record)
except Exception as e:
    print(f"PDF generation failed: {e}")
    # Continue with other operations
```

### 5. Clean Up PDFs When Not Needed

```python
# Delete PDFs for archived records
archived = db.query(Project).filter(Project.status == 'archived').all()
for project in archived:
    service.delete_pdf(project)
```

## Testing

Run the test suite:

```bash
pytest backend/tests/test_database_integration.py -v
```

Test coverage includes:
- Model creation
- Key generation
- PDF generation
- Bulk operations
- Lookups
- Statistics
- Error handling

## Requirements

- SQLAlchemy >= 1.4
- reportlab >= 3.6 (for PDF generation)
- Python >= 3.10

## Related Documentation

- [Dynamic Key System](DYNAMIC_KEY_SYSTEM.md)
- [PDF Byte Generation](PDF_BYTE_GENERATION.md)
- [Universal Data Model](UNIVERSAL_DATA_MODEL.md)

## Support

For issues or questions:
1. Check the test suite for examples
2. Review the API reference
3. Consult related documentation
