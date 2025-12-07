"""
Product Advanced Service Demo

Demonstrates all features of the Product Advanced Service.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.product_advanced_service import get_product_advanced_service


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_lifecycle_management():
    """Demo lifecycle management"""
    print_section("Product Lifecycle Management")
    
    service = get_product_advanced_service()
    product_id = 1
    
    try:
        # Get lifecycle
        print(f"Getting lifecycle for product {product_id}...")
        lifecycle = service.get_product_lifecycle(product_id)
        print(f" Current status: {lifecycle['status']}")
        print(f"  Version: {lifecycle['version']}")
        print(f"  Is active: {lifecycle['is_active']}")
        
        # Update lifecycle
        print(f"\nUpdating lifecycle to 'discontinued'...")
        updated = service.update_product_lifecycle(
            product_id,
            "discontinued",
            "End of life - replaced by newer model"
        )
        print(f" Lifecycle updated successfully")
        
    except Exception as e:
        print(f" Error: {e}")


def demo_versioning():
    """Demo product versioning"""
    print_section("Product Versioning")
    
    service = get_product_advanced_service()
    product_id = 1
    
    try:
        # Create version
        print(f"Creating new version for product {product_id}...")
        version = service.create_product_version(
            product_id,
            changes={
                "price_euro": 260.0,
                "efficiency": 21.0
            },
            version_notes="Price increase and efficiency improvement"
        )
        print(f" Version {version['version']} created")
        print(f"  Previous version: {version['previous_version']}")
        
        # Get version history
        print(f"\nGetting version history...")
        history = service.get_product_version_history(product_id, limit=10)
        print(f" Found {len(history)} versions")
        for v in history:
            print(f"  - Version {v['version']}: {v.get('version_notes', 'N/A')}")
        
    except Exception as e:
        print(f" Error: {e}")


def demo_comparison():
    """Demo product comparison"""
    print_section("Product Comparison")
    
    service = get_product_advanced_service()
    
    try:
        # Compare products
        print("Comparing products 1, 2, and 3...")
        comparison = service.compare_products(
            product_ids=[1, 2, 3],
            comparison_attributes=["power_wp", "efficiency", "price_euro"]
        )
        
        print(f" Compared {comparison['summary']['total_products']} products")
        print(f"  Attributes compared: {comparison['summary']['total_attributes']}")
        
        print("\nProducts:")
        for product in comparison['products']:
            print(f"  - {product['model_name']} ({product['brand']})")
        
        print("\nAttribute Differences:")
        for attr, data in comparison['attributes'].items():
            if data['has_differences']:
                print(f"  - {attr}: DIFFERENT")
                for val in data['values']:
                    print(f"    Product {val['product_id']}: {val['formatted_value']}")
        
    except Exception as e:
        print(f" Error: {e}")


def demo_recommendations():
    """Demo product recommendations"""
    print_section("Product Recommendations")
    
    service = get_product_advanced_service()
    
    try:
        # Get recommendations
        print("Getting product recommendations...")
        context = {
            "required_power": 420,
            "budget": 270.0,
            "preferred_brands": ["TestBrand"]
        }
        
        recommendations = service.get_product_recommendations(
            calculation_context=context,
            category="Solar Modules",
            limit=5
        )
        
        print(f" Found {len(recommendations)} recommendations")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['model_name']} (Score: {rec['recommendation_score']:.1f})")
            print(f"   Brand: {rec.get('brand', 'N/A')}")
            print(f"   Power: {rec.get('power_wp', 'N/A')}W")
            print(f"   Price: €{rec.get('price_euro', 0):.2f}")
            print(f"   Reasons:")
            for reason in rec['recommendation_reasons']:
                print(f"     - {reason}")
        
    except Exception as e:
        print(f" Error: {e}")


def demo_availability():
    """Demo availability tracking"""
    print_section("Product Availability Tracking")
    
    service = get_product_advanced_service()
    product_id = 1
    
    try:
        # Get availability
        print(f"Getting availability for product {product_id}...")
        availability = service.get_product_availability(product_id)
        
        print(f" Status: {availability['status']}")
        print(f"  Stock quantity: {availability['stock_quantity']}")
        print(f"  Reorder point: {availability['reorder_point']}")
        print(f"  Available: {availability['is_available']}")
        
        # Update availability
        print(f"\nUpdating availability...")
        updated = service.update_product_availability(
            product_id,
            stock_quantity=50,
            reorder_point=15
        )
        print(f" Availability updated")
        print(f"  New stock: {updated['stock_quantity']}")
        
    except Exception as e:
        print(f" Error: {e}")


def demo_suppliers():
    """Demo supplier management"""
    print_section("Supplier Management")
    
    service = get_product_advanced_service()
    product_id = 1
    
    try:
        # Get suppliers
        print(f"Getting suppliers for product {product_id}...")
        suppliers = service.get_product_suppliers(product_id)
        
        print(f" Found {len(suppliers)} suppliers")
        for supplier in suppliers:
            print(f"\n  {supplier['supplier_name']}")
            print(f"    SKU: {supplier.get('supplier_sku', 'N/A')}")
            print(f"    Price: €{supplier.get('unit_price', 0):.2f}")
            print(f"    MOQ: {supplier.get('minimum_order_quantity', 'N/A')}")
            print(f"    Lead time: {supplier.get('lead_time_days', 'N/A')} days")
        
        # Add supplier
        print(f"\nAdding new supplier...")
        new_supplier = service.add_product_supplier(
            product_id,
            supplier_data={
                "supplier_name": "Demo Supplier",
                "unit_price": 200.0,
                "minimum_order_quantity": 10,
                "lead_time_days": 14
            }
        )
        print(f" Supplier added: {new_supplier['supplier_name']}")
        
    except Exception as e:
        print(f" Error: {e}")


def demo_pricing_history():
    """Demo pricing history"""
    print_section("Pricing History & Trends")
    
    service = get_product_advanced_service()
    product_id = 1
    
    try:
        # Get pricing history
        print(f"Getting pricing history for product {product_id}...")
        history = service.get_pricing_history(product_id, limit=10)
        
        print(f" Found {len(history)} price changes")
        for record in history[:5]:
            print(f"  {record.get('changed_at', 'N/A')}: €{record.get('price_euro', 0):.2f}")
        
        # Analyze trends
        print(f"\nAnalyzing pricing trends (90 days)...")
        trends = service.analyze_pricing_trends(product_id, period_days=90)
        
        if trends.get('has_data'):
            print(f" Trend analysis:")
            print(f"  Current price: €{trends['current_price']:.2f}")
            print(f"  Min price: €{trends['min_price']:.2f}")
            print(f"  Max price: €{trends['max_price']:.2f}")
            print(f"  Average price: €{trends['avg_price']:.2f}")
            print(f"  Price change: €{trends['price_change']:.2f} ({trends['price_change_percent']:.1f}%)")
            print(f"  Trend: {trends['trend']}")
            print(f"  Volatility: €{trends['volatility']:.2f}")
        else:
            print(f" No pricing data available")
        
    except Exception as e:
        print(f" Error: {e}")


def demo_performance():
    """Demo performance analytics"""
    print_section("Performance Analytics")
    
    service = get_product_advanced_service()
    product_id = 1
    
    try:
        # Get product performance
        print(f"Getting performance for product {product_id} (30 days)...")
        performance = service.get_product_performance(product_id, period_days=30)
        
        print(f" Performance metrics:")
        metrics = performance['metrics']
        print(f"  Total sales: {metrics['total_sales']}")
        print(f"  Total revenue: €{metrics['total_revenue']:,.2f}")
        print(f"  Average order value: €{metrics['average_order_value']:.2f}")
        print(f"  Units sold: {metrics['units_sold']}")
        print(f"  Return rate: {metrics['return_rate']*100:.1f}%")
        print(f"  Customer satisfaction: {metrics['customer_satisfaction']}/5")
        
        print(f"\n  Trends:")
        trends = performance['trends']
        print(f"    Sales: {trends['sales_trend']}")
        print(f"    Revenue: {trends['revenue_trend']}")
        print(f"    Satisfaction: {trends['satisfaction_trend']}")
        
        # Get category performance
        print(f"\nGetting category performance...")
        category_perf = service.get_category_performance(
            "Solar Modules",
            period_days=30,
            limit=5
        )
        
        if category_perf.get('has_data'):
            print(f" Category: {category_perf['category']}")
            print(f"  Total products: {category_perf['total_products']}")
            print(f"  Total revenue: €{category_perf['totals']['total_revenue']:,.2f}")
            print(f"  Total units: {category_perf['totals']['total_units_sold']}")
        
    except Exception as e:
        print(f" Error: {e}")


def demo_price_matrix():
    """Demo price matrix integration"""
    print_section("Price Matrix Integration")
    
    service = get_product_advanced_service()
    
    try:
        # Get single product pricing
        print("Getting pricing from matrix for product 1...")
        pricing = service.get_product_pricing_from_matrix(
            product_id=1,
            quantity=10,
            context={"discount_code": "DEMO10"}
        )
        
        print(f" Pricing calculated:")
        print(f"  Base price: €{pricing.get('base_price', 0):.2f}")
        print(f"  Total price: €{pricing.get('total_price', 0):.2f}")
        
        # Get bulk pricing
        print(f"\nGetting bulk pricing for 5 products...")
        bulk_pricing = service.get_bulk_pricing(
            product_ids=[1, 2, 3, 4, 5],
            quantities=[10, 5, 8, 12, 6],
            context={"customer_type": "wholesale"}
        )
        
        print(f" Bulk pricing:")
        print(f"  Product count: {bulk_pricing['product_count']}")
        print(f"  Total quantity: {bulk_pricing['total_quantity']}")
        print(f"  Subtotal: €{bulk_pricing['subtotal']:,.2f}")
        print(f"  Bulk discount: {bulk_pricing['bulk_discount_percent']}% (€{bulk_pricing['bulk_discount']:,.2f})")
        print(f"  Total price: €{bulk_pricing['total_price']:,.2f}")
        
    except Exception as e:
        print(f" Error: {e}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("  PRODUCT ADVANCED SERVICE DEMO")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\nInitializing service...")
        service = get_product_advanced_service()
        health = service.health_check()
        print(f" Service status: {health.status}")
        
        # Run demos
        demo_lifecycle_management()
        demo_versioning()
        demo_comparison()
        demo_recommendations()
        demo_availability()
        demo_suppliers()
        demo_pricing_history()
        demo_performance()
        demo_price_matrix()
        
        print("\n" + "=" * 60)
        print("  DEMO COMPLETE")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
