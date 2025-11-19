"""
Product Management Service Demo

Demonstrates the usage of the ProductService for managing products.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.product_service import get_product_service


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_service_initialization():
    """Demonstrate service initialization and health check"""
    print_section("Service Initialization")
    
    # Get service instance
    service = get_product_service()
    print(f"✓ Service created: {service.service_name}")
    print(f"✓ Service initialized: {service.is_initialized}")
    
    # Check health
    health = service.health_check()
    print(f"\nHealth Check:")
    print(f"  Status: {health.status.value}")
    print(f"  Message: {health.message}")
    if health.details:
        print(f"  Details:")
        for key, value in health.details.items():
            print(f"    - {key}: {value}")
    
    return service


def demo_create_products(service):
    """Demonstrate creating products"""
    print_section("Creating Products")
    
    # Sample products to create
    products_to_create = [
        {
            'category': 'Modul',
            'model_name': 'SolarMax Pro 450W',
            'brand': 'SolarMax',
            'price_euro': 220.0,
            'capacity_w': 450.0,
            'warranty_years': 25,
            'efficiency_percent': 21.5,
            'technology': 'Monokristallin',
            'feature': 'Bifazial',
            'design': 'All-Black'
        },
        {
            'category': 'Modul',
            'model_name': 'EcoSolar 400W',
            'brand': 'EcoSolar',
            'price_euro': 180.0,
            'capacity_w': 400.0,
            'warranty_years': 20,
            'efficiency_percent': 20.0,
            'technology': 'Polykristallin'
        },
        {
            'category': 'Wechselrichter',
            'model_name': 'PowerInvert 5000',
            'brand': 'PowerTech',
            'price_euro': 850.0,
            'power_kw': 5.0,
            'warranty_years': 10,
            'efficiency_percent': 97.5,
            'smart_home': 1
        },
        {
            'category': 'Batteriespeicher',
            'model_name': 'EnergyStore 10kWh',
            'brand': 'EnergyTech',
            'price_euro': 4500.0,
            'storage_power_kw': 10.0,
            'max_cycles': 6000,
            'warranty_years': 10
        }
    ]
    
    created_ids = []
    
    for product_data in products_to_create:
        try:
            product = service.create_product(product_data)
            created_ids.append(product['id'])
            print(f"✓ Created: {product['model_name']} (ID: {product['id']})")
        except Exception as e:
            print(f"✗ Failed to create {product_data['model_name']}: {e}")
    
    return created_ids


def demo_read_products(service, product_ids):
    """Demonstrate reading products"""
    print_section("Reading Products")
    
    if not product_ids:
        print("No products to read")
        return
    
    # Get product by ID
    product_id = product_ids[0]
    product = service.get_product(product_id)
    if product:
        print(f"✓ Retrieved product by ID {product_id}:")
        print(f"  Model: {product['model_name']}")
        print(f"  Brand: {product['brand']}")
        print(f"  Price: €{product['price_euro']}")
    
    # Get product by model name
    model_name = product['model_name']
    product = service.get_product_by_model_name(model_name)
    if product:
        print(f"\n✓ Retrieved product by model name '{model_name}':")
        print(f"  ID: {product['id']}")
        print(f"  Category: {product['category']}")


def demo_list_and_search(service):
    """Demonstrate listing and searching products"""
    print_section("Listing and Searching Products")
    
    # List all products
    all_products = service.list_products()
    print(f"✓ Total products: {len(all_products)}")
    
    # List by category
    modules = service.list_products(category='Modul')
    print(f"✓ PV Modules: {len(modules)}")
    for module in modules:
        print(f"  - {module['model_name']}: €{module['price_euro']}")
    
    # Search products
    search_results = service.list_products(search_term='Solar')
    print(f"\n✓ Search results for 'Solar': {len(search_results)}")
    for product in search_results:
        print(f"  - {product['model_name']}")
    
    # Advanced search with filters
    filters = {
        'category': 'Modul',
        'price_min': 150.0,
        'price_max': 250.0
    }
    advanced_results = service.search_products(
        query='',
        filters=filters,
        limit=10
    )
    print(f"\n✓ Advanced search (Modules €150-250): {len(advanced_results)}")
    for product in advanced_results:
        print(f"  - {product['model_name']}: €{product['price_euro']}")
    
    # Get categories
    categories = service.get_categories()
    print(f"\n✓ Product categories: {', '.join(categories)}")


def demo_update_products(service, product_ids):
    """Demonstrate updating products"""
    print_section("Updating Products")
    
    if not product_ids:
        print("No products to update")
        return
    
    product_id = product_ids[0]
    
    # Get current product
    product = service.get_product(product_id)
    print(f"Current product:")
    print(f"  Model: {product['model_name']}")
    print(f"  Price: €{product['price_euro']}")
    print(f"  Warranty: {product['warranty_years']} years")
    
    # Update product
    update_data = {
        'price_euro': 210.0,
        'warranty_years': 30,
        'description': 'High-efficiency solar module with extended warranty'
    }
    
    try:
        updated_product = service.update_product(product_id, update_data)
        print(f"\n✓ Product updated:")
        print(f"  New price: €{updated_product['price_euro']}")
        print(f"  New warranty: {updated_product['warranty_years']} years")
        print(f"  Description: {updated_product['description']}")
    except Exception as e:
        print(f"✗ Failed to update product: {e}")


def demo_pagination(service):
    """Demonstrate pagination"""
    print_section("Pagination")
    
    # Get first page
    page_1 = service.list_products(limit=2, offset=0)
    print(f"✓ Page 1 (limit=2, offset=0): {len(page_1)} products")
    for product in page_1:
        print(f"  - {product['model_name']}")
    
    # Get second page
    page_2 = service.list_products(limit=2, offset=2)
    print(f"\n✓ Page 2 (limit=2, offset=2): {len(page_2)} products")
    for product in page_2:
        print(f"  - {product['model_name']}")


def demo_export_import(service):
    """Demonstrate export and import"""
    print_section("Export and Import")
    
    # Export products to JSON
    export_data = service.export_products(
        category='Modul',
        format='json'
    )
    print(f"✓ Exported {export_data['product_count']} products to JSON")
    print(f"  Export date: {export_data['export_date']}")
    print(f"  Format: {export_data['format']}")
    
    # Export to CSV
    csv_export = service.export_products(format='csv')
    print(f"\n✓ Exported {csv_export['product_count']} products to CSV")
    print(f"  CSV preview (first 200 chars):")
    print(f"  {csv_export['csv_data'][:200]}...")
    
    # Import products
    import_data = {
        'products': [
            {
                'category': 'Modul',
                'model_name': 'TestModule Import 1',
                'brand': 'TestBrand',
                'price_euro': 150.0,
                'capacity_w': 350.0
            },
            {
                'category': 'Modul',
                'model_name': 'TestModule Import 2',
                'brand': 'TestBrand',
                'price_euro': 160.0,
                'capacity_w': 360.0
            }
        ]
    }
    
    try:
        results = service.import_products(
            import_data=import_data,
            format='json',
            update_existing=False
        )
        print(f"\n✓ Import results:")
        print(f"  Total: {results['total']}")
        print(f"  Created: {results['created']}")
        print(f"  Updated: {results['updated']}")
        print(f"  Failed: {results['failed']}")
        if results['errors']:
            print(f"  Errors:")
            for error in results['errors']:
                print(f"    - {error}")
    except Exception as e:
        print(f"✗ Import failed: {e}")


def demo_delete_products(service, product_ids):
    """Demonstrate deleting products"""
    print_section("Deleting Products")
    
    if not product_ids:
        print("No products to delete")
        return
    
    # Delete the first product
    product_id = product_ids[0]
    product = service.get_product(product_id)
    
    if product:
        print(f"Deleting product:")
        print(f"  ID: {product['id']}")
        print(f"  Model: {product['model_name']}")
        
        try:
            success = service.delete_product(product_id)
            if success:
                print(f"✓ Product deleted successfully")
                
                # Verify deletion
                deleted_product = service.get_product(product_id)
                if deleted_product is None:
                    print(f"✓ Verified: Product no longer exists")
        except Exception as e:
            print(f"✗ Failed to delete product: {e}")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  PRODUCT MANAGEMENT SERVICE DEMO")
    print("="*60)
    
    try:
        # Initialize service
        service = demo_service_initialization()
        
        # Create products
        product_ids = demo_create_products(service)
        
        # Read products
        demo_read_products(service, product_ids)
        
        # List and search
        demo_list_and_search(service)
        
        # Update products
        demo_update_products(service, product_ids)
        
        # Pagination
        demo_pagination(service)
        
        # Export and import
        demo_export_import(service)
        
        # Delete products
        demo_delete_products(service, product_ids)
        
        print_section("Demo Complete")
        print("✓ All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
