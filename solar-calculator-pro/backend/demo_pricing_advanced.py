"""
Demo script for Advanced Pricing Service

This script demonstrates all features of the advanced pricing service.

Requirements: 1.3, 4.5, 6.1
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from backend.services.pricing_advanced_service import get_pricing_advanced_service


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_volume_discounts():
    """Demonstrate volume discount calculations"""
    print_section("Volume Discount Calculations")
    
    service = get_pricing_advanced_service()
    
    discount_tiers = [
        {'min_quantity': 10, 'discount_percentage': 5},
        {'min_quantity': 50, 'discount_percentage': 10},
        {'min_quantity': 100, 'discount_percentage': 15}
    ]
    
    quantities = [5, 15, 75, 150]
    
    for qty in quantities:
        result = service.calculate_volume_discount(
            quantity=qty,
            unit_price=100.0,
            discount_tiers=discount_tiers
        )
        
        print(f"\nQuantity: {qty}")
        print(f"  Base Total: €{result['base_total']:,.2f}")
        print(f"  Discount: {result['discount_percentage']}%")
        print(f"  Final Total: €{result['final_total']:,.2f}")
        print(f"  Savings: €{result['savings']:,.2f}")


def demo_time_based_pricing():
    """Demonstrate time-based pricing"""
    print_section("Time-Based Pricing")
    
    service = get_pricing_advanced_service()
    
    pricing_schedule = {
        'weekday_multiplier': 1.0,
        'weekend_multiplier': 1.1,
        'peak_hours': {'start': 9, 'end': 17, 'multiplier': 1.2},
        'seasonal': {
            'summer': {'months': [6, 7, 8], 'multiplier': 1.15},
            'winter': {'months': [12, 1, 2], 'multiplier': 0.95}
        }
    }
    
    test_dates = [
        datetime(2024, 7, 15, 12, 0),  # Summer weekday, peak hours
        datetime(2024, 7, 20, 20, 0),  # Summer weekend, off-peak
        datetime(2024, 1, 10, 12, 0),  # Winter weekday, peak hours
    ]
    
    for date in test_dates:
        result = service.calculate_time_based_price(
            base_price=1000.0,
            pricing_schedule=pricing_schedule,
            target_date=date
        )
        
        print(f"\nDate: {date.strftime('%Y-%m-%d %H:%M')} ({date.strftime('%A')})")
        print(f"  Base Price: €{result['base_price']:,.2f}")
        print(f"  Adjustments: {result['adjustments']}")
        print(f"  Final Price: €{result['final_price']:,.2f}")
        print(f"  Total Multiplier: {result['total_multiplier']:.2f}x")


def demo_customer_specific_pricing():
    """Demonstrate customer-specific pricing"""
    print_section("Customer-Specific Pricing")
    
    service = get_pricing_advanced_service()
    
    # Create VIP customer rule
    service.create_pricing_rule(
        name="VIP Customer Discount",
        rule_type="customer_specific",
        conditions={'customer_id': 'VIP001'},
        actions={'discount_percentage': 20},
        priority=100
    )
    
    customers = ['VIP001', 'REGULAR001']
    
    for customer_id in customers:
        result = service.get_customer_price(
            customer_id=customer_id,
            product_id='SOLAR_SYSTEM',
            base_price=10000.0,
            quantity=1
        )
        
        print(f"\nCustomer: {customer_id}")
        print(f"  Base Price: €{result['base_price']:,.2f}")
        print(f"  Has Custom Pricing: {result['has_custom_pricing']}")
        print(f"  Final Price: €{result['final_price']:,.2f}")
        if result['has_custom_pricing']:
            print(f"  Applied Rules: {result['applied_rules']}")


def demo_bundle_pricing():
    """Demonstrate bundle pricing"""
    print_section("Bundle Pricing")
    
    service = get_pricing_advanced_service()
    
    items = [
        {'product_id': 'solar_panel', 'quantity': 20, 'unit_price': 250},
        {'product_id': 'inverter', 'quantity': 1, 'unit_price': 1500},
        {'product_id': 'battery', 'quantity': 1, 'unit_price': 5000},
        {'product_id': 'mounting', 'quantity': 1, 'unit_price': 800}
    ]
    
    bundle_rules = {
        'discount_percentage': 12,
        'free_items': ['installation', 'warranty_basic'],
        'bonus_items': [
            {'product_id': 'monitoring_system', 'quantity': 1}
        ]
    }
    
    result = service.calculate_bundle_price(items, bundle_rules)
    
    print("\nBundle Items:")
    for item in result['items']:
        print(f"  {item['product_id']}: {item['quantity']} × €{item['unit_price']} = €{item['total']:,.2f}")
    
    print(f"\nIndividual Total: €{result['individual_total']:,.2f}")
    print(f"Bundle Discount: {result['bundle_discount_percentage']}%")
    print(f"Bundle Total: €{result['bundle_total']:,.2f}")
    print(f"Savings: €{result['savings']:,.2f}")
    print(f"Free Items: {result['free_items']}")
    print(f"Bonus Items: {result['bonus_items']}")


def demo_promotional_pricing():
    """Demonstrate promotional pricing"""
    print_section("Promotional Pricing")
    
    service = get_pricing_advanced_service()
    
    # Create promotion
    promo_result = service.create_promotion(
        name="Summer Sale 2024",
        promotion_type="percentage",
        discount_value=25.0,
        valid_from=datetime.now(),
        valid_until=datetime.now() + timedelta(days=90),
        conditions={'promo_code': 'SUMMER2024'},
        max_uses=1000
    )
    
    print(f"\nPromotion Created: {promo_result['promotion_id']}")
    
    # Apply promotion
    apply_result = service.apply_promotion_code(
        promo_code='SUMMER2024',
        base_price=8000.0,
        customer_id='CUST001'
    )
    
    if apply_result['success']:
        print(f"\nPromotion Applied: {apply_result['promotion_name']}")
        print(f"  Base Price: €{apply_result['base_price']:,.2f}")
        print(f"  Discount: €{apply_result['discount_amount']:,.2f}")
        print(f"  Final Price: €{apply_result['final_price']:,.2f}")
        print(f"  Savings: €{apply_result['savings']:,.2f}")


def demo_currency_conversion():
    """Demonstrate currency conversion"""
    print_section("Currency Conversion")
    
    service = get_pricing_advanced_service()
    
    # Set exchange rates
    rates = [
        ('EUR', 'USD', 1.10),
        ('EUR', 'GBP', 0.85),
        ('EUR', 'CHF', 0.95),
        ('EUR', 'JPY', 160.0)
    ]
    
    print("\nExchange Rates Set:")
    for from_curr, to_curr, rate in rates:
        service.set_exchange_rate(from_curr, to_curr, rate)
        print(f"  1 {from_curr} = {rate} {to_curr}")
    
    # Multi-currency pricing
    result = service.get_multi_currency_price(
        base_price=10000.0,
        base_currency='EUR',
        target_currencies=['USD', 'GBP', 'CHF', 'JPY']
    )
    
    print("\nMulti-Currency Pricing:")
    for currency, price in result['prices'].items():
        if currency == 'JPY':
            print(f"  {currency}: ¥{price:,.0f}")
        else:
            print(f"  {currency}: {price:,.2f}")


def demo_price_history():
    """Demonstrate price history tracking"""
    print_section("Price History Tracking")
    
    service = get_pricing_advanced_service()
    
    # Record price changes
    changes = [
        ('SOLAR_PANEL_001', 250.0, 260.0, 'Raw material cost increase'),
        ('SOLAR_PANEL_001', 260.0, 255.0, 'Supplier discount'),
        ('SOLAR_PANEL_001', 255.0, 270.0, 'Market adjustment'),
    ]
    
    print("\nRecording Price Changes:")
    for product_id, old_price, new_price, reason in changes:
        result = service.record_price_change(
            product_id=product_id,
            old_price=old_price,
            new_price=new_price,
            reason=reason,
            changed_by='admin'
        )
        change_pct = ((new_price - old_price) / old_price * 100)
        print(f"  €{old_price} → €{new_price} ({change_pct:+.1f}%): {reason}")
    
    # Get price history
    history_result = service.get_price_history(product_id='SOLAR_PANEL_001')
    
    print(f"\nPrice History (Total: {history_result['count']} changes)")
    
    # Get price trend
    trend_result = service.get_price_trend(product_id='SOLAR_PANEL_001', days=30)
    
    print(f"\nPrice Trend Analysis:")
    print(f"  Trend: {trend_result['trend'].upper()}")
    print(f"  Changes: {trend_result['changes_count']}")
    print(f"  Total Change: €{trend_result['total_change']:+.2f}")
    print(f"  Average Change: €{trend_result['average_change']:+.2f}")


def demo_complete_pricing_flow():
    """Demonstrate complete pricing flow with all features"""
    print_section("Complete Pricing Flow")
    
    service = get_pricing_advanced_service()
    
    print("\nScenario: Large solar installation for VIP customer")
    print("=" * 70)
    
    # Step 1: Base price
    base_price = 50000.0
    print(f"\n1. Base Price: €{base_price:,.2f}")
    
    # Step 2: Volume discount
    volume_result = service.calculate_volume_discount(
        quantity=100,
        unit_price=base_price / 100,
        discount_tiers=[
            {'min_quantity': 50, 'discount_percentage': 10},
            {'min_quantity': 100, 'discount_percentage': 15}
        ]
    )
    price = volume_result['final_total']
    print(f"2. After Volume Discount (15%): €{price:,.2f} (saved €{volume_result['savings']:,.2f})")
    
    # Step 3: Customer-specific discount
    service.create_pricing_rule(
        name="VIP Discount",
        rule_type="customer_specific",
        conditions={'customer_id': 'VIP_CUSTOMER'},
        actions={'discount_percentage': 5},
        priority=50
    )
    
    customer_result = service.get_customer_price(
        customer_id='VIP_CUSTOMER',
        product_id='SOLAR_SYSTEM',
        base_price=price,
        quantity=1
    )
    price = customer_result['final_price']
    vip_savings = volume_result['final_total'] - price
    print(f"3. After VIP Discount (5%): €{price:,.2f} (saved €{vip_savings:,.2f})")
    
    # Step 4: Promotional code
    service.create_promotion(
        name="Spring Promo",
        promotion_type="percentage",
        discount_value=3.0,
        valid_from=datetime.now(),
        valid_until=datetime.now() + timedelta(days=30),
        conditions={'promo_code': 'SPRING2024'}
    )
    
    promo_result = service.apply_promotion_code(
        promo_code='SPRING2024',
        base_price=price,
        customer_id='VIP_CUSTOMER'
    )
    
    if promo_result['success']:
        price = promo_result['final_price']
        print(f"4. After Promo Code (3%): €{price:,.2f} (saved €{promo_result['savings']:,.2f})")
    
    # Step 5: Multi-currency
    service.set_exchange_rate('EUR', 'USD', 1.10)
    service.set_exchange_rate('EUR', 'GBP', 0.85)
    
    multi_result = service.get_multi_currency_price(
        base_price=price,
        base_currency='EUR',
        target_currencies=['USD', 'GBP']
    )
    
    print(f"\n5. Multi-Currency Pricing:")
    for currency, amount in multi_result['prices'].items():
        print(f"   {currency}: {amount:,.2f}")
    
    # Summary
    total_savings = base_price - price
    savings_pct = (total_savings / base_price * 100)
    
    print(f"\n{'=' * 70}")
    print(f"SUMMARY:")
    print(f"  Original Price: €{base_price:,.2f}")
    print(f"  Final Price: €{price:,.2f}")
    print(f"  Total Savings: €{total_savings:,.2f} ({savings_pct:.1f}%)")
    print(f"{'=' * 70}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  ADVANCED PRICING SERVICE DEMONSTRATION")
    print("=" * 70)
    
    try:
        demo_volume_discounts()
        demo_time_based_pricing()
        demo_customer_specific_pricing()
        demo_bundle_pricing()
        demo_promotional_pricing()
        demo_currency_conversion()
        demo_price_history()
        demo_complete_pricing_flow()
        
        print("\n" + "=" * 70)
        print("  ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
