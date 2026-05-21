"""
Demo: Price Matrix Extras and Services

Demonstrates all features of the Price Matrix Extras and Services system.
"""

from decimal import Decimal
from services.price_matrix_extras_service import PriceMatrixExtrasService


def demo_special_products():
    """Demo: Calculate special products"""
    print("\n" + "="*60)
    print("DEMO: Special Products Calculation")
    print("="*60)
    
    service = PriceMatrixExtrasService()
    
    project_details = {
        'anlage_kwp': 10.0,
        'roof_area_m2': 70.0,
        'module_quantity': 25,
        'module_power_w': 400
    }
    
    # Simulate special products (in real scenario, these would be marked in DB)
    selected_products = [
        {
            'id': 1,
            'name': 'Premium Solar Optimizer',
            'category': 'Optimizer',
            'price': 150.0,
            'quantity': 25
        },
        {
            'id': 2,
            'name': 'Advanced Monitoring System',
            'category': 'Monitoring',
            'price': 500.0,
            'quantity': 1
        }
    ]
    
    result = service.calculate_special_products(project_details, selected_products)
    
    print(f"\nProject: {project_details['anlage_kwp']} kWp system")
    print(f"Special Products Count: {result['count']}")
    print(f"\nItems:")
    for item in result['items']:
        print(f"  - {item['name']}")
        print(f"    Category: {item['category']}")
        print(f"    Unit Price: {item['formatted_unit_price']}")
        print(f"    Quantity: {item['quantity']}")
        print(f"    Total: {item['formatted_total']}")
    
    print(f"\nTotal Special Products: {result['formatted_total']}")


def demo_services():
    """Demo: Calculate services"""
    print("\n" + "="*60)
    print("DEMO: Services Calculation")
    print("="*60)
    
    service = PriceMatrixExtrasService()
    
    project_details = {
        'anlage_kwp': 10.0,
        'roof_area_m2': 70.0
    }
    
    # Simulate services (in real scenario, these would come from DB)
    # Mock the database method
    def mock_get_services():
        return [
            {
                'id': 1,
                'name': 'Installation',
                'description': 'Professional installation service',
                'category': 'Installation',
                'price': 100.0,
                'calculate_per': 'kWp',
                'is_standard': True,
                'pdf_order': 1
            },
            {
                'id': 2,
                'name': 'Commissioning',
                'description': 'System commissioning and testing',
                'category': 'Service',
                'price': 200.0,
                'calculate_per': 'Pauschal',
                'is_standard': True,
                'pdf_order': 2
            },
            {
                'id': 3,
                'name': 'Extended Warranty',
                'description': '10-year extended warranty',
                'category': 'Warranty',
                'price': 500.0,
                'calculate_per': 'Pauschal',
                'is_standard': False,
                'pdf_order': 3
            },
            {
                'id': 4,
                'name': 'Annual Maintenance',
                'description': 'Annual system maintenance',
                'category': 'Maintenance',
                'price': 150.0,
                'calculate_per': 'Pauschal',
                'is_standard': False,
                'pdf_order': 4
            }
        ]
    
    service._get_services_from_db = mock_get_services
    
    # Calculate with optional services selected
    result = service.calculate_services(
        project_details,
        [3, 4],  # Select extended warranty and maintenance
        include_standard=True
    )
    
    print(f"\nProject: {project_details['anlage_kwp']} kWp system")
    
    print(f"\nStandard Services (always included):")
    for svc in result['standard_services']:
        print(f"  - {svc['name']}")
        print(f"    {svc['formatted_unit_price']} × {svc['quantity']} {svc['calculate_per']}")
        print(f"    Total: {svc['formatted_total']}")
    
    print(f"\nOptional Services (selected):")
    for svc in result['optional_services']:
        print(f"  - {svc['name']}")
        print(f"    {svc['formatted_unit_price']} × {svc['quantity']} {svc['calculate_per']}")
        print(f"    Total: {svc['formatted_total']}")
    
    print(f"\nStandard Services Total: {result['formatted_total_standard']}")
    print(f"Optional Services Total: {result['formatted_total_optional']}")
    print(f"All Services Total: {result['formatted_total_services']}")


def demo_bundle_pricing():
    """Demo: Calculate bundle pricing"""
    print("\n" + "="*60)
    print("DEMO: Bundle Pricing")
    print("="*60)
    
    service = PriceMatrixExtrasService()
    
    items = [
        {
            'id': 1,
            'name': 'PV Modules',
            'category': 'Module',
            'total_price': 5000.0
        },
        {
            'id': 2,
            'name': 'Inverter',
            'category': 'Inverter',
            'total_price': 2000.0
        },
        {
            'id': 3,
            'name': 'Battery Storage',
            'category': 'Storage',
            'total_price': 3000.0
        }
    ]
    
    bundle_rules = [
        {
            'name': 'Complete System Bundle - 10% Discount',
            'type': 'percentage',
            'value': 10.0,
            'min_items': 3,
            'min_total': 0,
            'required_items': [],
            'required_categories': ['Module', 'Inverter', 'Storage']
        }
    ]
    
    result = service.calculate_bundle_pricing(items, bundle_rules)
    
    print(f"\nItems in Bundle:")
    for item in items:
        print(f"  - {item['name']}: {service._format_currency(Decimal(str(item['total_price'])))}")
    
    print(f"\nApplied Bundle Rules:")
    for rule in result['applied_rules']:
        print(f"  - {rule['name']}")
        print(f"    Type: {rule['type']}")
        print(f"    Value: {rule['value']}")
    
    print(f"\nOriginal Total: {result['formatted_original']}")
    print(f"Bundle Discount: {result['formatted_discount']} ({result['discount_percentage']:.1f}%)")
    print(f"Final Total: {result['formatted_final']}")
    print(f"Savings: {result['formatted_discount']}")


def demo_conditional_pricing():
    """Demo: Apply conditional pricing"""
    print("\n" + "="*60)
    print("DEMO: Conditional Pricing")
    print("="*60)
    
    service = PriceMatrixExtrasService()
    
    base_price = Decimal('10000.00')
    
    conditions = {
        'system_size': 15.0,
        'customer_type': 'commercial',
        'season': 'summer',
        'location': 'urban'
    }
    
    pricing_rules = [
        {
            'name': 'Large System Discount',
            'condition': {
                'type': 'size_based',
                'field': 'system_size',
                'operator': 'greater_than',
                'value': 10.0
            },
            'adjustment_type': 'percentage',
            'adjustment_value': -5.0
        },
        {
            'name': 'Commercial Customer Discount',
            'condition': {
                'type': 'customer_type',
                'field': 'customer_type',
                'operator': 'equals',
                'value': 'commercial'
            },
            'adjustment_type': 'fixed',
            'adjustment_value': -200.0
        },
        {
            'name': 'Summer Installation Bonus',
            'condition': {
                'type': 'seasonal',
                'field': 'season',
                'operator': 'equals',
                'value': 'summer'
            },
            'adjustment_type': 'percentage',
            'adjustment_value': -2.0
        }
    ]
    
    result = service.apply_conditional_pricing(base_price, conditions, pricing_rules)
    
    print(f"\nBase Price: {result['formatted_base']}")
    
    print(f"\nConditions:")
    for key, value in conditions.items():
        print(f"  - {key}: {value}")
    
    print(f"\nApplied Adjustments:")
    for adj in result['adjustments']:
        print(f"  - {adj['rule_name']}")
        print(f"    Type: {adj['rule_type']}")
        print(f"    Amount: {adj['formatted_amount']}")
    
    print(f"\nTotal Adjustment: {result['formatted_adjustment']}")
    print(f"Final Price: {result['formatted_final']}")
    
    savings = base_price - result['final_price']
    savings_pct = (savings / base_price * Decimal('100'))
    print(f"Total Savings: {service._format_currency(savings)} ({savings_pct:.1f}%)")


def demo_custom_rules():
    """Demo: Apply custom pricing rules"""
    print("\n" + "="*60)
    print("DEMO: Custom Pricing Rules")
    print("="*60)
    
    service = PriceMatrixExtrasService()
    
    pricing_data = {
        'total': 10000.0,
        'items': []
    }
    
    custom_rules = [
        {
            'name': 'Early Bird Discount',
            'type': 'discount',
            'value': 5.0,
            'value_type': 'percentage',
            'enabled': True
        },
        {
            'name': 'Express Delivery Surcharge',
            'type': 'surcharge',
            'value': 100.0,
            'value_type': 'fixed',
            'enabled': True
        },
        {
            'name': 'Loyalty Discount',
            'type': 'discount',
            'value': 200.0,
            'value_type': 'fixed',
            'enabled': True
        }
    ]
    
    result = service.apply_custom_pricing_rules(pricing_data, custom_rules)
    
    print(f"\nOriginal Total: {service._format_currency(Decimal(str(pricing_data['total'])))}")
    
    print(f"\nApplied Custom Rules:")
    for rule_result in result['applied_custom_rules']:
        if rule_result['applied']:
            print(f"   {rule_result['rule_name']}")
    
    if 'discount_applied' in result:
        print(f"\nTotal Discounts: {service._format_currency(result['discount_applied'])}")
    
    if 'surcharge_applied' in result:
        print(f"Total Surcharges: {service._format_currency(result['surcharge_applied'])}")
    
    print(f"\nFinal Total: {service._format_currency(result['total'])}")


def demo_complete_calculation():
    """Demo: Complete pricing calculation workflow"""
    print("\n" + "="*60)
    print("DEMO: Complete Pricing Calculation")
    print("="*60)
    
    service = PriceMatrixExtrasService()
    
    # Step 1: Base price from matrix
    base_price = Decimal('8000.00')
    print(f"\n1. Base Price (from matrix): {service._format_currency(base_price)}")
    
    # Step 2: Add special products
    special_products = [
        {'id': 1, 'name': 'Optimizer', 'price': 150.0, 'quantity': 25}
    ]
    extras_result = service.calculate_special_products(
        {'anlage_kwp': 10.0},
        special_products
    )
    total = base_price + extras_result['total']
    print(f"2. + Special Products: {extras_result['formatted_total']}")
    print(f"   Subtotal: {service._format_currency(total)}")
    
    # Step 3: Add services (simulated)
    services_total = Decimal('1200.00')
    total += services_total
    print(f"3. + Services: {service._format_currency(services_total)}")
    print(f"   Subtotal: {service._format_currency(total)}")
    
    # Step 4: Apply bundle discount
    bundle_discount = total * Decimal('0.10')  # 10% discount
    total -= bundle_discount
    print(f"4. - Bundle Discount (10%): {service._format_currency(bundle_discount)}")
    print(f"   Subtotal: {service._format_currency(total)}")
    
    # Step 5: Apply conditional pricing
    conditional_discount = Decimal('200.00')
    total -= conditional_discount
    print(f"5. - Conditional Discount: {service._format_currency(conditional_discount)}")
    print(f"   Subtotal: {service._format_currency(total)}")
    
    # Step 6: Apply custom rules
    custom_discount = total * Decimal('0.05')  # 5% early bird
    total -= custom_discount
    print(f"6. - Custom Discount (5%): {service._format_currency(custom_discount)}")
    
    print(f"\n{'='*60}")
    print(f"FINAL PRICE: {service._format_currency(total)}")
    print(f"{'='*60}")
    
    original = base_price + extras_result['total'] + services_total
    savings = original - total
    savings_pct = (savings / original * Decimal('100'))
    print(f"\nOriginal Price: {service._format_currency(original)}")
    print(f"Total Savings: {service._format_currency(savings)} ({savings_pct:.1f}%)")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("PRICE MATRIX EXTRAS AND SERVICES - DEMO")
    print("="*60)
    
    demo_special_products()
    demo_services()
    demo_bundle_pricing()
    demo_conditional_pricing()
    demo_custom_rules()
    demo_complete_calculation()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nFor more information, see:")
    print("  - docs/PRICE_MATRIX_EXTRAS_GUIDE.md")
    print("  - docs/PRICE_MATRIX_EXTRAS_QUICK_REFERENCE.md")
    print("  - tests/test_price_matrix_extras_service.py")
    print()


if __name__ == '__main__':
    main()
