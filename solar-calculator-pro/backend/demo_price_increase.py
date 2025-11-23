"""
Demo: Price Increase Service for Multi-PDF Generation

This demo shows how the Price Increase Service works for generating
multiple offers with automatic price increases.

Key Concept:
- Main Offer: Base price from Solar Calculator (e.g., 16.999,00 €)
- Second Offer: Base price + 7% = 18.188,93 €
- Third Offer: Previous price + 7% = 19.462,16 €
- Logic: ALWAYS apply increase rule, even if rotated products are cheaper/more expensive
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.price_increase_service import get_price_increase_service, IncreaseStrategy


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_price_info(price_info: dict):
    """Print price information"""
    print(f"  Offer {price_info['offer_index']}:")
    print(f"    Price: {price_info['price_formatted']}")
    print(f"    Increase Rate: {price_info['increase_rate_percentage']}")
    if price_info.get('increase_amount'):
        print(f"    Increase Amount: {price_info['increase_amount_formatted']}")
    if price_info.get('previous_price'):
        print(f"    Previous Price: {price_info['previous_price_formatted']}")
    print()


def demo_basic_usage():
    """Demo: Basic usage with default settings"""
    print_section("Demo 1: Basic Usage (Default 7% Cumulative Increase)")
    
    service = get_price_increase_service()
    service.reset_price_state()
    
    # Set base price from Solar Calculator
    base_price = 16999.00
    service.set_base_price(base_price)
    print(f"Base Price: {service._formatter.format_currency(base_price)}")
    print()
    
    # Generate 3 offers
    print("Generating 3 offers with 7% cumulative increase:\n")
    
    offer1 = service.calculate_next_price()
    print_price_info(offer1)
    
    offer2 = service.calculate_next_price()
    print_price_info(offer2)
    
    offer3 = service.calculate_next_price()
    print_price_info(offer3)
    
    # Show comparison
    comparison = service.generate_price_comparison()
    print(f"Total Increase: {comparison['total_increase_formatted']} ({comparison['total_increase_percentage']})")
    print(f"Average Increase Rate: {comparison['average_increase_percentage']}")


def demo_custom_increase_rate():
    """Demo: Custom increase rate"""
    print_section("Demo 2: Custom Increase Rate (10%)")
    
    service = get_price_increase_service()
    service.reset_price_state()
    
    # Set custom increase rate
    service.set_increase_rate(0.10)  # 10%
    
    base_price = 16999.00
    service.set_base_price(base_price)
    print(f"Base Price: {service._formatter.format_currency(base_price)}")
    print(f"Increase Rate: 10%")
    print()
    
    # Generate 3 offers
    print("Generating 3 offers with 10% cumulative increase:\n")
    
    for i in range(3):
        offer = service.calculate_next_price()
        print_price_info(offer)


def demo_fixed_strategy():
    """Demo: Fixed increase strategy"""
    print_section("Demo 3: Fixed Increase Strategy")
    
    service = get_price_increase_service()
    service.reset_price_state()
    
    # Set fixed strategy
    service.set_strategy(IncreaseStrategy.FIXED.value)
    service.set_increase_rate(0.07)  # 7%
    
    base_price = 16999.00
    service.set_base_price(base_price)
    print(f"Base Price: {service._formatter.format_currency(base_price)}")
    print(f"Strategy: Fixed (each offer increases by 7% from base)")
    print()
    
    # Generate 3 offers
    print("Generating 3 offers with fixed 7% increase from base:\n")
    
    for i in range(3):
        offer = service.calculate_next_price()
        print_price_info(offer)


def demo_custom_rates():
    """Demo: Custom rates per offer"""
    print_section("Demo 4: Custom Rates Per Offer")
    
    service = get_price_increase_service()
    service.reset_price_state()
    
    # Set custom rates
    custom_rates = [0.05, 0.10, 0.15]  # 5%, 10%, 15%
    service.set_strategy(IncreaseStrategy.CUSTOM.value)
    service.set_custom_rates(custom_rates)
    
    base_price = 16999.00
    service.set_base_price(base_price)
    print(f"Base Price: {service._formatter.format_currency(base_price)}")
    print(f"Strategy: Custom")
    print(f"Custom Rates: {[f'{r*100}%' for r in custom_rates]}")
    print()
    
    # Generate 3 offers
    print("Generating 3 offers with custom rates:\n")
    
    for i in range(3):
        offer = service.calculate_next_price()
        print_price_info(offer)


def demo_multi_pdf_scenario():
    """Demo: Real-world multi-PDF scenario"""
    print_section("Demo 5: Multi-PDF Scenario (8 Companies)")
    
    service = get_price_increase_service()
    service.reset_price_state()
    
    # Setup for 8 companies
    base_price = 16999.00
    service.set_base_price(base_price)
    service.set_increase_rate(0.07)  # 7%
    
    print(f"Base Price: {service._formatter.format_currency(base_price)}")
    print(f"Number of Companies: 8")
    print(f"Increase Rate: 7% (cumulative)")
    print()
    
    # Generate all prices at once
    print("Generating prices for all 8 companies:\n")
    
    all_prices = service.calculate_all_prices(8)
    
    # Print all prices
    for price_info in all_prices:
        if price_info.get('is_base'):
            print(f"  Base Offer:")
            print(f"    Price: {price_info['price_formatted']}")
            print()
        else:
            print_price_info(price_info)
    
    # Show comparison
    comparison = service.generate_price_comparison()
    print(f"Summary:")
    print(f"  Base Price: {comparison['base_price_formatted']}")
    print(f"  Final Price: {comparison['current_price_formatted']}")
    print(f"  Total Increase: {comparison['total_increase_formatted']} ({comparison['total_increase_percentage']})")
    print(f"  Average Increase: {comparison['average_increase_percentage']}")


def demo_calculate_specific_offer():
    """Demo: Calculate price for specific offer"""
    print_section("Demo 6: Calculate Price for Specific Offer")
    
    service = get_price_increase_service()
    service.reset_price_state()
    
    base_price = 16999.00
    service.set_base_price(base_price)
    service.set_increase_rate(0.07)
    
    print(f"Base Price: {service._formatter.format_currency(base_price)}")
    print()
    
    # Calculate for specific offers
    print("Calculating prices for specific offers:\n")
    
    for offer_index in [1, 5, 10]:
        price_info = service.calculate_price_for_offer(offer_index)
        print_price_info(price_info)


def demo_price_comparison():
    """Demo: Price comparison and history"""
    print_section("Demo 7: Price Comparison and History")
    
    service = get_price_increase_service()
    service.reset_price_state()
    
    base_price = 16999.00
    service.set_base_price(base_price)
    service.set_increase_rate(0.07)
    
    # Generate 5 offers
    for i in range(5):
        service.calculate_next_price()
    
    # Get history
    history = service.get_price_history()
    print(f"Price History ({len(history)} entries):\n")
    
    for record in history:
        if record.get('is_base'):
            print(f"  Base: {record['price_formatted']}")
        else:
            print(f"  Offer {record['offer_index']}: {record['price_formatted']} (+{record['increase_rate_percentage']})")
    
    print()
    
    # Get comparison
    comparison = service.generate_price_comparison()
    print("Comparison Report:")
    print(f"  Total Offers: {comparison['total_offers']}")
    print(f"  Base Price: {comparison['base_price_formatted']}")
    print(f"  Current Price: {comparison['current_price_formatted']}")
    print(f"  Total Increase: {comparison['total_increase_formatted']}")
    print(f"  Total Increase %: {comparison['total_increase_percentage']}")
    print(f"  Average Increase: {comparison['average_increase_percentage']}")


def demo_german_formatting():
    """Demo: German number formatting"""
    print_section("Demo 8: German Number Formatting")
    
    service = get_price_increase_service()
    service.reset_price_state()
    
    base_price = 16999.00
    service.set_base_price(base_price)
    
    print("All prices are formatted in German:")
    print(f"  - Decimal separator: comma (,)")
    print(f"  - Thousand separator: dot (.)")
    print(f"  - Currency symbol: €")
    print()
    
    # Generate offers
    print("Examples:\n")
    
    for i in range(3):
        offer = service.calculate_next_price()
        print(f"  Offer {offer['offer_index']}:")
        print(f"    Raw: {offer['price']}")
        print(f"    Formatted: {offer['price_formatted']}")
        print()


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  PRICE INCREASE SERVICE DEMO")
    print("  Multi-PDF Generation with Automatic Price Increases")
    print("=" * 80)
    
    try:
        demo_basic_usage()
        demo_custom_increase_rate()
        demo_fixed_strategy()
        demo_custom_rates()
        demo_multi_pdf_scenario()
        demo_calculate_specific_offer()
        demo_price_comparison()
        demo_german_formatting()
        
        print("\n" + "=" * 80)
        print("  ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
