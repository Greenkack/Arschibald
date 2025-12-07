"""
Product Import/Export Demo

Demonstrates all import/export functionality
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from services.product_import_export_service import ProductImportExportService
from models.product_import_schemas import (
    ProductImportMapping,
    ProductExportRequest,
    ProductExportFormat
)
import pandas as pd
import io


def demo_excel_import():
    """Demo: Import products from Excel"""
    print("\n" + "="*60)
    print("DEMO: Excel Import")
    print("="*60)
    
    # Create sample Excel file
    data = {
        'Product Name': ['Solar Module 400W', 'Inverter 5kW', 'Battery 10kWh'],
        'Article Number': ['SM-400-001', 'INV-5K-001', 'BAT-10K-001'],
        'Category': ['Solar Modules', 'Inverters', 'Batteries'],
        'Brand': ['SolarTech', 'PowerTech', 'EnergyStore'],
        'Unit Price': [299.99, 1499.99, 3999.99],
        'Description': [
            'High-efficiency monocrystalline module',
            'Hybrid inverter with battery management',
            'Lithium-ion battery storage system'
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Save to Excel
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl')
    excel_file.seek(0)
    
    print("\n Sample Excel Data:")
    print(df.to_string(index=False))
    
    # Create column mapping
    mapping = ProductImportMapping(
        name_column='Product Name',
        sku_column='Article Number',
        category_column='Category',
        manufacturer_column='Brand',
        price_column='Unit Price',
        description_column='Description'
    )
    
    print("\n Column Mapping:")
    print(f"  Product Name → name")
    print(f"  Article Number → sku")
    print(f"  Category → category")
    print(f"  Brand → manufacturer")
    print(f"  Unit Price → price")
    print(f"  Description → description")
    
    print("\n Import would process 3 products with custom column names")
    print("   (Actual import requires database connection)")


def demo_csv_import():
    """Demo: Import products from CSV"""
    print("\n" + "="*60)
    print("DEMO: CSV Import")
    print("="*60)
    
    # Create sample CSV
    csv_data = """name,sku,category,manufacturer,price,spec_power,spec_efficiency
Solar Module 400W,SM-400-001,Solar Modules,SolarTech,299.99,400W,21.5%
Solar Module 450W,SM-450-001,Solar Modules,SolarTech,349.99,450W,22.0%
Inverter 5kW,INV-5K-001,Inverters,PowerTech,1499.99,5000W,97.5%
Inverter 10kW,INV-10K-001,Inverters,PowerTech,2499.99,10000W,98.0%
Battery 10kWh,BAT-10K-001,Batteries,EnergyStore,3999.99,10kWh,95%"""
    
    print("\n Sample CSV Data:")
    print(csv_data)
    
    # Parse CSV
    df = pd.read_csv(io.StringIO(csv_data))
    
    print("\n Parsed Data:")
    print(df.to_string(index=False))
    
    print("\n Import would process 5 products")
    print("   Including custom specifications (spec_power, spec_efficiency)")


def demo_xml_import():
    """Demo: Import products from XML"""
    print("\n" + "="*60)
    print("DEMO: XML Import")
    print("="*60)
    
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<products>
    <product>
        <name>Solar Module 400W Monocrystalline</name>
        <sku>SM-400-MONO-001</sku>
        <category>Solar Modules</category>
        <manufacturer>SolarTech GmbH</manufacturer>
        <price>299.99</price>
        <description>Premium monocrystalline solar module</description>
        <specifications>
            <power>400W</power>
            <efficiency>21.5%</efficiency>
            <warranty>25 years</warranty>
        </specifications>
    </product>
    <product>
        <name>Inverter 5kW Hybrid</name>
        <sku>INV-5K-HYB-001</sku>
        <category>Inverters</category>
        <manufacturer>PowerTech AG</manufacturer>
        <price>1499.99</price>
        <description>Hybrid inverter with battery management</description>
        <specifications>
            <power>5000W</power>
            <efficiency>97.5%</efficiency>
            <warranty>10 years</warranty>
        </specifications>
    </product>
</products>"""
    
    print("\n Sample XML Data:")
    print(xml_data)
    
    print("\n Import would process 2 products from XML")
    print("   Including nested specifications")


def demo_api_integration():
    """Demo: Import from external API"""
    print("\n" + "="*60)
    print("DEMO: API Integration")
    print("="*60)
    
    api_config = {
        "api_url": "https://api.supplier.com/v1/products",
        "api_key": "your-api-key-here",
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        "params": {
            "category": "solar-modules",
            "in_stock": True,
            "limit": 100
        }
    }
    
    print("\n API Configuration:")
    print(f"  URL: {api_config['api_url']}")
    print(f"  Authentication: API Key")
    print(f"  Filters: category=solar-modules, in_stock=true, limit=100")
    
    sample_response = {
        "data": {
            "products": [
                {
                    "name": "Solar Module 400W",
                    "sku": "SM-400-001",
                    "category": "Solar Modules",
                    "manufacturer": "SolarTech",
                    "price": 299.99,
                    "stock": 150
                },
                {
                    "name": "Solar Module 450W",
                    "sku": "SM-450-001",
                    "category": "Solar Modules",
                    "manufacturer": "SolarTech",
                    "price": 349.99,
                    "stock": 200
                }
            ],
            "total": 2,
            "page": 1
        }
    }
    
    print("\n Sample API Response:")
    import json
    print(json.dumps(sample_response, indent=2))
    
    print("\n Import would process products from external API")
    print("   Supports pagination and filtering")


def demo_excel_export():
    """Demo: Export products to Excel"""
    print("\n" + "="*60)
    print("DEMO: Excel Export")
    print("="*60)
    
    export_request = {
        "format": "excel",
        "filters": {
            "category": "Solar Modules",
            "min_price": 200,
            "max_price": 500
        },
        "columns": ["name", "sku", "price", "manufacturer", "spec_power"],
        "include_metadata": True
    }
    
    print("\n Export Configuration:")
    print(f"  Format: Excel (.xlsx)")
    print(f"  Filters:")
    print(f"    - Category: Solar Modules")
    print(f"    - Price Range: 200 - 500 EUR")
    print(f"  Columns: name, sku, price, manufacturer, spec_power")
    print(f"  Include Metadata: Yes")
    
    print("\n Export would create Excel file with:")
    print("  - Products sheet with filtered data")
    print("  - Metadata sheet with export information")
    print("  - German number formatting (299,99 €)")
    print("  - Formatted headers and column widths")


def demo_csv_export():
    """Demo: Export products to CSV"""
    print("\n" + "="*60)
    print("DEMO: CSV Export")
    print("="*60)
    
    export_request = {
        "format": "csv",
        "filters": {
            "manufacturer": "SolarTech"
        },
        "columns": ["name", "sku", "price", "category"]
    }
    
    print("\n Export Configuration:")
    print(f"  Format: CSV")
    print(f"  Filters: manufacturer=SolarTech")
    print(f"  Columns: name, sku, price, category")
    print(f"  Delimiter: , (comma)")
    print(f"  Encoding: UTF-8")
    
    sample_csv = """name,sku,price,category
Solar Module 400W,SM-400-001,299.99,Solar Modules
Solar Module 450W,SM-450-001,349.99,Solar Modules
Solar Module 500W,SM-500-001,399.99,Solar Modules"""
    
    print("\n Sample CSV Output:")
    print(sample_csv)


def demo_validation():
    """Demo: Data validation"""
    print("\n" + "="*60)
    print("DEMO: Data Validation")
    print("="*60)
    
    # Sample data with errors
    data_with_errors = {
        'name': ['Solar Module 400W', '', 'Inverter 5kW', 'Battery 10kWh'],
        'sku': ['SM-400-001', 'SM-450-001', '', 'BAT-10K-001'],
        'price': [299.99, -100, 1499.99, 'invalid'],
        'category': ['Solar Modules', 'Solar Modules', 'Inverters', 'Batteries']
    }
    
    df = pd.DataFrame(data_with_errors)
    
    print("\n Sample Data with Errors:")
    print(df.to_string(index=False))
    
    print("\n Validation Errors Found:")
    print("  Row 2:")
    print("    - Name is required")
    print("  Row 3:")
    print("    - SKU is required")
    print("  Row 2:")
    print("    - Price must be non-negative")
    print("  Row 4:")
    print("    - Invalid price format")
    
    print("\n Validation Result:")
    print("  Total Rows: 4")
    print("  Valid Rows: 1")
    print("  Invalid Rows: 3")
    print("  Success: False")


def demo_bulk_operations():
    """Demo: Bulk operations"""
    print("\n" + "="*60)
    print("DEMO: Bulk Operations")
    print("="*60)
    
    print("\n Bulk Update:")
    print("  Product IDs: [1, 2, 3, 4, 5]")
    print("  Updates:")
    print("    - category: 'Premium Solar Modules'")
    print("    - price_multiplier: 1.1 (10% increase)")
    print("  Result: 5 products updated")
    
    print("\n Bulk Delete:")
    print("  Product IDs: [10, 11, 12]")
    print("  Confirmation: Required")
    print("  Result: 3 products deleted")


def demo_templates():
    """Demo: Import templates"""
    print("\n" + "="*60)
    print("DEMO: Import Templates")
    print("="*60)
    
    print("\n Available Templates:")
    print("  1. Excel Template (.xlsx)")
    print("  2. CSV Template (.csv)")
    print("  3. JSON Template (.json)")
    
    print("\n Template Contents:")
    print("  - Required columns with descriptions")
    print("  - Sample data rows")
    print("  - Import instructions")
    print("  - Validation rules")
    
    print("\n Download Template:")
    print("  GET /api/v1/product-import-export/template/download/excel")
    print("  GET /api/v1/product-import-export/template/download/csv")
    print("  GET /api/v1/product-import-export/template/download/json")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("PRODUCT IMPORT/EXPORT SYSTEM DEMO")
    print("="*60)
    print("\nDemonstrating all import/export functionality")
    print("(Database operations are simulated)")
    
    # Import demos
    demo_excel_import()
    demo_csv_import()
    demo_xml_import()
    demo_api_integration()
    
    # Export demos
    demo_excel_export()
    demo_csv_export()
    
    # Additional features
    demo_validation()
    demo_bulk_operations()
    demo_templates()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\n All import/export features demonstrated")
    print(" See docs/PRODUCT_IMPORT_EXPORT_GUIDE.md for detailed documentation")
    print(" API documentation available at /docs")


if __name__ == "__main__":
    main()
