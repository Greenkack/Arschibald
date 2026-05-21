"""
Product Rotation Service Demonstration

This script demonstrates the product rotation functionality for multi-PDF generation.
Shows how products are automatically rotated to provide variety across multiple offers.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.product_rotation_service import (
    get_product_rotation_service,
    RotationStrategy
)


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_product(product: dict, label: str = "Product"):
    """Print product information"""
    if product:
        print(f"{label}:")
        print(f"  ID: {product.get('id')}")
        print(f"  Brand: {product.get('brand')}")
        print(f"  Model: {product.get('model_name')}")
        print(f"  Category: {product.get('category')}")
        if 'power_wp' in product:
            print(f"  Power: {product.get('power_wp')}W")
        if 'efficiency' in product:
            print(f"  Efficiency: {product.get('efficiency')}%")
        if 'price_euro' in product:
            print(f"  Price: €{product.get('price_euro'):,.2f}")
    else:
        print(f"{label}: None")
    print()


def demo_basic_rotation():
    """Demonstrate basic product rotation"""
    print_section("1. Basic Product Rotation - Avoid Brands")
    
    service = get_product_rotation_service()
    service.reset_rotation_state()
    
    print("Selecting 3 PV modules in sequence, avoiding previously used brands:\n")
    
    for i in range(1, 4):
        product = service.select_rotated_product(
            category="pv_module",
            strategy=RotationStrategy.AVOID_BRANDS.value
        )
        print_product(product, f"Offer {i} - PV Module")
    
    # Show rotation state
    state = service.get_rotation_state()
    print(f"Used brands in pv_module: {state['used_brands'].get('pv_module', [])}")


def demo_avoid_both():
    """Demonstrate avoiding both brands and products"""
    print_section("2. Advanced Rotation - Avoid Both Brands and Products")
    
    service = get_product_rotation_service()
    service.reset_rotation_state()
    
    print("Selecting 3 PV modules, avoiding both brands AND products:\n")
    
    for i in range(1, 4):
        product = service.select_rotated_product(
            category="pv_module",
            strategy=RotationStrategy.AVOID_BOTH.value
        )
        print_product(product, f"Offer {i} - PV Module")
    
    # Show rotation state
    state = service.get_rotation_state()
    print(f"Used brands: {state['used_brands'].get('pv_module', [])}")
    print(f"Used products: {state['used_products'].get('pv_module', [])}")


def demo_product_set():
    """Demonstrate selecting complete product sets"""
    print_section("3. Complete Product Set Selection")
    
    service = get_product_rotation_service()
    service.reset_rotation_state()
    
    print("Generating 3 complete offers with PV Module + Inverter + Battery:\n")
    
    categories = ["pv_module", "inverter", "battery"]
    
    for i in range(1, 4):
        print(f"--- Offer {i} ---")
        
        product_set = service.select_product_set(
            categories=categories,
            strategy=RotationStrategy.AVOID_BOTH.value
        )
        
        for category, product in product_set.items():
            if product:
                print(f"\n{category.upper()}:")
                print(f"  Brand: {product.get('brand')}")
                print(f"  Model: {product.get('model_name')}")
                print(f"  Price: €{product.get('price_euro', 0):,.2f}")
        
        print()


def demo_price_based_rotation():
    """Demonstrate price-based rotation"""
    print_section("4. Price-Based Rotation")
    
    service = get_product_rotation_service()
    service.reset_rotation_state()
    
    print("Main Offer (Reference):")
    main_product = service.select_rotated_product(
        category="pv_module",
        strategy=RotationStrategy.AVOID_BOTH.value
    )
    print_product(main_product, "Main PV Module")
    
    print("\nOffer 2 - Similar Price (±20%):")
    similar_product = service.select_rotated_product(
        category="pv_module",
        strategy=RotationStrategy.PRICE_SIMILAR.value,
        reference_product_id=main_product['id'],
        price_tolerance=0.2
    )
    print_product(similar_product, "Similar Price PV Module")
    
    print("\nOffer 3 - Higher Price:")
    higher_product = service.select_rotated_product(
        category="pv_module",
        strategy=RotationStrategy.PRICE_HIGHER.value,
        reference_product_id=main_product['id'],
        price_tolerance=0.3
    )
    print_product(higher_product, "Higher Price PV Module")


def demo_spec_requirements():
    """Demonstrate selection with specification requirements"""
    print_section("5. Selection with Specification Requirements")
    
    service = get_product_rotation_service()
    service.reset_rotation_state()
    
    print("Selecting PV modules with minimum 410W power:\n")
    
    required_specs = {
        "power_wp": {"min": 410}
    }
    
    for i in range(1, 3):
        product = service.select_rotated_product(
            category="pv_module",
            strategy=RotationStrategy.AVOID_BOTH.value,
            required_specs=required_specs
        )
        print_product(product, f"High-Power Module {i}")


def demo_compatibility_check():
    """Demonstrate compatibility checking"""
    print_section("6. Product Compatibility Checking")
    
    service = get_product_rotation_service()
    service.reset_rotation_state()
    
    print("Selecting a complete system and checking compatibility:\n")
    
    product_set = service.select_product_set(
        categories=["pv_module", "inverter", "battery"],
        strategy=RotationStrategy.AVOID_BOTH.value
    )
    
    print("Selected Products:")
    for category, product in product_set.items():
        if product:
            print(f"\n{category.upper()}:")
            print(f"  Brand: {product.get('brand')}")
            print(f"  Model: {product.get('model_name')}")
    
    print("\n\nCompatibility Check:")
    report = service.check_product_compatibility(product_set)
    
    print(f"  Compatible: {report['is_compatible']}")
    print(f"  Has Warnings: {report['has_warnings']}")
    
    if report['issues']:
        print("\n  Issues:")
        for issue in report['issues']:
            print(f"    - [{issue['severity']}] {issue['message']}")
    
    if report['warnings']:
        print("\n  Warnings:")
        for warning in report['warnings']:
            print(f"    - [{warning['severity']}] {warning['message']}")
    
    if not report['issues'] and not report['warnings']:
        print("\n   All products are compatible!")


def demo_multi_offer_scenario():
    """Demonstrate complete multi-offer scenario"""
    print_section("7. Complete Multi-Offer Scenario (3 Companies)")
    
    service = get_product_rotation_service()
    service.reset_rotation_state()
    
    companies = ["Company A", "Company B", "Company C"]
    categories = ["pv_module", "inverter", "battery"]
    
    print("Generating 3 complete offers for different companies:\n")
    print("Each offer will have DIFFERENT products/brands than previous offers.\n")
    
    all_offers = []
    
    for i, company in enumerate(companies, 1):
        print(f"\n{'=' * 60}")
        print(f"  OFFER {i} - {company}")
        print('=' * 60)
        
        product_set = service.select_product_set(
            categories=categories,
            strategy=RotationStrategy.AVOID_BOTH.value
        )
        
        total_price = 0
        
        for category, product in product_set.items():
            if product:
                price = product.get('price_euro', 0)
                total_price += price
                
                print(f"\n{category.replace('_', ' ').upper()}:")
                print(f"  Brand: {product.get('brand')}")
                print(f"  Model: {product.get('model_name')}")
                print(f"  Price: €{price:,.2f}")
        
        print(f"\n  TOTAL PRICE: €{total_price:,.2f}")
        
        all_offers.append({
            "company": company,
            "products": product_set,
            "total_price": total_price
        })
    
    # Summary
    print("\n\n" + "=" * 60)
    print("  SUMMARY - All Offers")
    print("=" * 60 + "\n")
    
    for offer in all_offers:
        print(f"{offer['company']}: €{offer['total_price']:,.2f}")
        pv_brand = offer['products'].get('pv_module', {}).get('brand', 'N/A')
        inv_brand = offer['products'].get('inverter', {}).get('brand', 'N/A')
        bat_brand = offer['products'].get('battery', {}).get('brand', 'N/A')
        print(f"  PV: {pv_brand} | Inverter: {inv_brand} | Battery: {bat_brand}")
        print()
    
    # Show rotation state
    state = service.get_rotation_state()
    print("\nRotation State:")
    print(f"  Total brands used: {state['total_used_brands']}")
    print(f"  Total products used: {state['total_used_products']}")


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 80)
    print("  PRODUCT ROTATION SERVICE DEMONSTRATION")
    print("  Multi-PDF Generation with Automatic Product Variety")
    print("=" * 80)
    
    try:
        demo_basic_rotation()
        demo_avoid_both()
        demo_product_set()
        demo_price_based_rotation()
        demo_spec_requirements()
        demo_compatibility_check()
        demo_multi_offer_scenario()
        
        print("\n" + "=" * 80)
        print("  DEMONSTRATION COMPLETE")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
