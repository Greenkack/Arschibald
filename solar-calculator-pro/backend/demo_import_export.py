"""
Import/Export System Demo

Demonstrates the import/export functionality with various examples
"""

import asyncio
import base64
import json
from services.import_export_service import (
    ImportExportService,
    ImportConfig,
    ExportConfig,
    ImportFormat,
    ExportFormat,
    DataMapping,
    ValidationRule
)


async def demo_csv_import():
    """Demo: Import data from CSV"""
    print("\n=== CSV Import Demo ===")
    
    # Sample CSV data
    csv_data = """Name,Email,Phone,Age
John Doe,john@example.com,+1234567890,30
Jane Smith,jane@example.com,+0987654321,25
Bob Johnson,bob@example.com,+1122334455,35
Invalid User,invalid_phone,abc
"""
    
    # Configure import
    config = ImportConfig(
        format=ImportFormat.CSV,
        mappings=[
            DataMapping(source_field="Name", target_field="name", transformation="trim"),
            DataMapping(source_field="Email", target_field="email", transformation="lowercase"),
            DataMapping(source_field="Phone", target_field="phone"),
            DataMapping(source_field="Age", target_field="age", transformation="to_int")
        ],
        validation_rules=[
            ValidationRule(
                field="name",
                rule_type="required",
                parameters={},
                error_message="Name is required"
            ),
            ValidationRule(
                field="email",
                rule_type="custom",
                parameters={"validator": "email"},
                error_message="Invalid email format"
            ),
            ValidationRule(
                field="age",
                rule_type="range",
                parameters={"min": 18, "max": 100},
                error_message="Age must be between 18 and 100"
            )
        ],
        skip_errors=True,
        batch_size=10
    )
    
    # Import data
    service = ImportExportService()
    result = await service.import_data(csv_data, config)
    
    print(f"Total records: {result.total_records}")
    print(f"Imported: {result.imported_records}")
    print(f"Failed: {result.failed_records}")
    print(f"Errors: {json.dumps(result.errors, indent=2)}")


async def demo_excel_export():
    """Demo: Export data to Excel"""
    print("\n=== Excel Export Demo ===")
    
    # Sample data
    data = [
        {"id": 1, "name": "Project A", "customer": "John Doe", "size": 10.5, "status": "active"},
        {"id": 2, "name": "Project B", "customer": "Jane Smith", "size": 15.2, "status": "completed"},
        {"id": 3, "name": "Project C", "customer": "Bob Johnson", "size": 8.7, "status": "active"}
    ]
    
    # Configure export
    config = ExportConfig(
        format=ExportFormat.EXCEL,
        fields=["id", "name", "customer", "size", "status"],
        include_headers=True,
        custom_headers={
            "id": "Project ID",
            "name": "Project Name",
            "customer": "Customer Name",
            "size": "System Size (kWp)",
            "status": "Status"
        }
    )
    
    # Export data
    service = ImportExportService()
    file_data = await service.export_data(data, config)
    
    print(f"Exported {len(data)} records")
    print(f"File size: {len(file_data)} bytes")
    print("File saved as: export_demo.xlsx")
    
    # Save file
    with open("export_demo.xlsx", "wb") as f:
        f.write(file_data)


async def demo_json_import_export():
    """Demo: Import and export JSON"""
    print("\n=== JSON Import/Export Demo ===")
    
    # Sample JSON data
    json_data = json.dumps([
        {"product_name": "Solar Panel A", "price": "299.99", "stock": "50"},
        {"product_name": "Solar Panel B", "price": "349.99", "stock": "30"},
        {"product_name": "Inverter X", "price": "1299.99", "stock": "20"}
    ])
    
    # Configure import
    import_config = ImportConfig(
        format=ImportFormat.JSON,
        mappings=[
            DataMapping(source_field="product_name", target_field="name"),
            DataMapping(source_field="price", target_field="price", transformation="to_float"),
            DataMapping(source_field="stock", target_field="stock", transformation="to_int")
        ],
        validation_rules=[
            ValidationRule(
                field="name",
                rule_type="required",
                parameters={},
                error_message="Product name is required"
            ),
            ValidationRule(
                field="price",
                rule_type="custom",
                parameters={"validator": "positive"},
                error_message="Price must be positive"
            )
        ],
        skip_errors=False
    )
    
    # Import data
    service = ImportExportService()
    import_result = await service.import_data(json_data, import_config)
    
    print(f"Import - Total: {import_result.total_records}, Imported: {import_result.imported_records}")
    
    # Export back to JSON
    export_config = ExportConfig(
        format=ExportFormat.JSON,
        fields=["name", "price", "stock"],
        include_headers=True
    )
    
    # Create sample data for export
    export_data = [
        {"name": "Solar Panel A", "price": 299.99, "stock": 50},
        {"name": "Solar Panel B", "price": 349.99, "stock": 30},
        {"name": "Inverter X", "price": 1299.99, "stock": 20}
    ]
    
    file_data = await service.export_data(export_data, export_config)
    
    print(f"Export - File size: {len(file_data)} bytes")
    print(f"Exported data:\n{file_data.decode('utf-8')}")


async def demo_xml_import():
    """Demo: Import data from XML"""
    print("\n=== XML Import Demo ===")
    
    # Sample XML data
    xml_data = """<?xml version="1.0"?>
<data>
    <record>
        <customer_name>John Doe</customer_name>
        <email>john@example.com</email>
        <project_type>residential</project_type>
        <system_size>10.5</system_size>
    </record>
    <record>
        <customer_name>Jane Smith</customer_name>
        <email>jane@example.com</email>
        <project_type>commercial</project_type>
        <system_size>25.0</system_size>
    </record>
</data>
"""
    
    # Configure import
    config = ImportConfig(
        format=ImportFormat.XML,
        mappings=[
            DataMapping(source_field="customer_name", target_field="customer"),
            DataMapping(source_field="email", target_field="email", transformation="lowercase"),
            DataMapping(source_field="project_type", target_field="type"),
            DataMapping(source_field="system_size", target_field="size", transformation="to_float")
        ],
        validation_rules=[
            ValidationRule(
                field="customer",
                rule_type="required",
                parameters={},
                error_message="Customer name is required"
            )
        ],
        skip_errors=False
    )
    
    # Import data
    service = ImportExportService()
    result = await service.import_data(xml_data, config)
    
    print(f"Total records: {result.total_records}")
    print(f"Imported: {result.imported_records}")
    print(f"Success: {result.success}")


async def demo_template_creation():
    """Demo: Create import template"""
    print("\n=== Template Creation Demo ===")
    
    service = ImportExportService()
    
    # Create CSV template
    fields = ["customer_name", "email", "phone", "address", "system_size"]
    csv_template = service.create_import_template(fields, ExportFormat.CSV)
    
    print("CSV Template:")
    print(csv_template.decode('utf-8'))
    
    # Create Excel template
    excel_template = service.create_import_template(fields, ExportFormat.EXCEL)
    print(f"\nExcel template size: {len(excel_template)} bytes")
    
    # Save templates
    with open("import_template.csv", "wb") as f:
        f.write(csv_template)
    with open("import_template.xlsx", "wb") as f:
        f.write(excel_template)
    
    print("Templates saved: import_template.csv, import_template.xlsx")


async def demo_file_validation():
    """Demo: Validate import file"""
    print("\n=== File Validation Demo ===")
    
    # Sample CSV data with issues
    csv_data = """Name,Email,Age
John Doe,john@example.com,30
Jane Smith,invalid_email,25
,bob@example.com,35
"""
    
    # Configure validation
    config = ImportConfig(
        format=ImportFormat.CSV,
        mappings=[
            DataMapping(source_field="Name", target_field="name"),
            DataMapping(source_field="Email", target_field="email"),
            DataMapping(source_field="Age", target_field="age", transformation="to_int")
        ],
        validation_rules=[
            ValidationRule(
                field="name",
                rule_type="required",
                parameters={},
                error_message="Name is required"
            ),
            ValidationRule(
                field="email",
                rule_type="custom",
                parameters={"validator": "email"},
                error_message="Invalid email"
            )
        ],
        skip_errors=False
    )
    
    # Validate file
    service = ImportExportService()
    result = service.validate_import_file(csv_data, config)
    
    print(f"Valid: {result['valid']}")
    print(f"Record count: {result.get('record_count')}")
    print(f"Fields: {result.get('fields')}")
    print(f"Error: {result.get('error')}")


async def demo_custom_transformation():
    """Demo: Custom transformation function"""
    print("\n=== Custom Transformation Demo ===")
    
    # Register custom transformation
    service = ImportExportService()
    service.register_transformation(
        'format_phone',
        lambda x: x.replace('-', '').replace(' ', '') if x else None
    )
    
    # Sample data
    csv_data = """Name,Phone
John Doe,123-456-7890
Jane Smith,098 765 4321
"""
    
    # Configure import with custom transformation
    config = ImportConfig(
        format=ImportFormat.CSV,
        mappings=[
            DataMapping(source_field="Name", target_field="name"),
            DataMapping(source_field="Phone", target_field="phone", transformation="format_phone")
        ],
        validation_rules=[],
        skip_errors=False
    )
    
    # Import data
    result = await service.import_data(csv_data, config)
    
    print(f"Imported {result.imported_records} records with custom transformation")


async def demo_batch_processing():
    """Demo: Batch processing with progress"""
    print("\n=== Batch Processing Demo ===")
    
    # Generate large dataset
    records = []
    for i in range(250):
        records.append(f"User {i},user{i}@example.com,{20 + i % 50}")
    
    csv_data = "Name,Email,Age\n" + "\n".join(records)
    
    # Progress callback
    async def progress_callback(current, total):
        percentage = (current / total) * 100
        print(f"Progress: {current}/{total} ({percentage:.1f}%)")
    
    # Configure import
    config = ImportConfig(
        format=ImportFormat.CSV,
        mappings=[
            DataMapping(source_field="Name", target_field="name"),
            DataMapping(source_field="Email", target_field="email"),
            DataMapping(source_field="Age", target_field="age", transformation="to_int")
        ],
        validation_rules=[],
        skip_errors=False,
        batch_size=50  # Process 50 records at a time
    )
    
    # Import with progress tracking
    service = ImportExportService()
    result = await service.import_data(csv_data, config, progress_callback)
    
    print(f"\nCompleted: {result.imported_records} records imported")


async def main():
    """Run all demos"""
    print("=" * 60)
    print("Import/Export System Demo")
    print("=" * 60)
    
    await demo_csv_import()
    await demo_excel_export()
    await demo_json_import_export()
    await demo_xml_import()
    await demo_template_creation()
    await demo_file_validation()
    await demo_custom_transformation()
    await demo_batch_processing()
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
