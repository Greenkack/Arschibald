"""
Product Pricing Management Demo
Demonstrates all pricing features with practical examples
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal, engine
from backend.models.pricing_models import Base
from backend.services.pricing_service import PricingService
from backend.models.pricing_schemas import (
    PriceListCreate, ProductPriceCreate, VolumeDiscountCreate,
    PromotionalPricingCreate, CustomerSpecificPriceCreate,
    PriceCalculationRequest
)


def create_demo_data(db: Session):
    """Create demo pricing data"""
    service = PricingService(db)
    
    print("\n" + "="*80)
    print("PRODUCT PRICING MANAGEMENT DEMO")
    print("="*80)
    
    # 1. Create Price Lists
    print("\n1. Creating Price Lists...")
    print("-" * 80)
    
    standard_list = service.create_price_list(PriceListCreate(
        name="Standard Retail Prices 2024",
        description="Standard pricing for retail customers",
        currency="EUR",
        is_active=True,
        is_default=True,
        valid_from=datetime(2024, 1, 1),
        valid_until=datetime(2024, 12, 31)
    ))
    print(f" Created price list: {standard_list.name} (ID: {standard_list.id})")
    
    wholesale_list = service.create_price_list(PriceListCreate(
        name="Wholesale Prices 2024",
        description="Discounted pricing for wholesale customers",
        currency="EUR",
        is_active=True,
        is_default=False,
        valid_from=datetime(2024, 1, 1),
        valid_until=datetime(2024, 12, 31)
    ))
    print(f" Created price list: {wholesale_list.name} (ID: {wholesale_list.id})")
    
    # 2. Create Product Prices
    print("\n2. Creating Product Prices...")
    print("-" * 80)
    
    # Standard pricing
    product_price_1 = service.create_product_price(ProductPriceCreate(
        price_list_id=standard_list.id,
        product_id=100,
        base_price=100.00,
        pricing_type="standard",
        cost_price=70.00,
        margin_percentage=30.0
    ))
    print(f" Product 100: €{product_price_1.base_price:.2f} (Standard)")
    
    # Tiered pricing
    product_price_2 = service.create_product_price(ProductPriceCreate(
        price_list_id=standard_list.id,
        product_id=101,
        base_price=200.00,
        pricing_type="tiered",
        tier_config=[
            {"min_quantity": 1, "max_quantity": 10, "price": 200.00},
            {"min_quantity": 11, "max_quantity": 50, "price": 190.00},
            {"min_quantity": 51, "max_quantity": None, "price": 180.00}
        ],
        cost_price=140.00,
        margin_percentage=30.0
    ))
    print(f" Product 101: €{product_price_2.base_price:.2f} (Tiered)")
    print(f"   - 1-10 units: €200.00")
    print(f"   - 11-50 units: €190.00")
    print(f"   - 51+ units: €180.00")
    
    # Wholesale pricing
    wholesale_price = service.create_product_price(ProductPriceCreate(
        price_list_id=wholesale_list.id,
        product_id=100,
        base_price=85.00,
        pricing_type="standard",
        cost_price=70.00,
        margin_percentage=21.4
    ))
    print(f" Product 100 (Wholesale): €{wholesale_price.base_price:.2f}")
    
    # 3. Create Volume Discounts
    print("\n3. Creating Volume Discounts...")
    print("-" * 80)
    
    volume_discount_1 = service.create_volume_discount(VolumeDiscountCreate(
        name="Bulk Purchase Discount",
        description="10% off for orders of 100+ units",
        product_id=100,
        discount_type="percentage",
        min_quantity=100,
        max_quantity=None,
        discount_value=10.0,
        is_active=True,
        valid_from=datetime(2024, 1, 1),
        valid_until=datetime(2024, 12, 31)
    ))
    print(f" {volume_discount_1.name}: {volume_discount_1.discount_value}% off for {volume_discount_1.min_quantity}+ units")
    
    volume_discount_2 = service.create_volume_discount(VolumeDiscountCreate(
        name="Tiered Volume Discount",
        description="Increasing discounts for larger orders",
        product_id=None,  # Applies to all products
        discount_type="tiered_percentage",
        min_quantity=50,
        max_quantity=None,
        discount_value=0,  # Not used for tiered
        tier_config=[
            {"min_qty": 50, "max_qty": 99, "discount": 5.0},
            {"min_qty": 100, "max_qty": 499, "discount": 10.0},
            {"min_qty": 500, "max_qty": None, "discount": 15.0}
        ],
        is_active=True,
        valid_from=datetime(2024, 1, 1),
        valid_until=datetime(2024, 12, 31)
    ))
    print(f" {volume_discount_2.name}:")
    print(f"   - 50-99 units: 5% off")
    print(f"   - 100-499 units: 10% off")
    print(f"   - 500+ units: 15% off")
    
    # 4. Create Promotional Pricing
    print("\n4. Creating Promotional Campaigns...")
    print("-" * 80)
    
    promo_1 = service.create_promotional_pricing(PromotionalPricingCreate(
        name="Summer Sale 2024",
        description="20% off all products",
        promo_code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        max_discount_amount=500.00,
        product_ids=None,  # All products
        customer_ids=None,  # All customers
        max_uses_total=1000,
        max_uses_per_customer=1,
        is_active=True,
        valid_from=datetime(2024, 6, 1),
        valid_until=datetime(2024, 8, 31)
    ))
    print(f" {promo_1.name}")
    print(f"   Code: {promo_1.promo_code}")
    print(f"   Discount: {promo_1.discount_value}% (max €{promo_1.max_discount_amount})")
    print(f"   Valid: {promo_1.valid_from.date()} to {promo_1.valid_until.date()}")
    
    promo_2 = service.create_promotional_pricing(PromotionalPricingCreate(
        name="New Customer Welcome",
        description="€50 off first order",
        promo_code="WELCOME50",
        discount_type="fixed_amount",
        discount_value=50.00,
        max_discount_amount=None,
        product_ids=None,
        customer_ids=None,
        max_uses_total=None,
        max_uses_per_customer=1,
        is_active=True,
        valid_from=datetime(2024, 1, 1),
        valid_until=datetime(2024, 12, 31)
    ))
    print(f" {promo_2.name}")
    print(f"   Code: {promo_2.promo_code}")
    print(f"   Discount: €{promo_2.discount_value} off")
    
    # 5. Create Customer-Specific Pricing
    print("\n5. Creating Customer-Specific Pricing...")
    print("-" * 80)
    
    customer_price = service.create_customer_specific_price(CustomerSpecificPriceCreate(
        customer_id=1,
        product_id=100,
        special_price=85.00,
        discount_percentage=15.0,
        reason="VIP customer - annual contract",
        is_active=True,
        valid_from=datetime(2024, 1, 1),
        valid_until=datetime(2024, 12, 31)
    ))
    print(f" Customer 1 - Product 100: €{customer_price.special_price:.2f}")
    print(f"   Reason: {customer_price.reason}")
    print(f"   Discount: {customer_price.discount_percentage}%")
    
    return service


def demo_price_calculations(service: PricingService):
    """Demonstrate price calculations"""
    
    print("\n" + "="*80)
    print("PRICE CALCULATION EXAMPLES")
    print("="*80)
    
    # Example 1: Standard pricing
    print("\n Example 1: Standard Pricing")
    print("-" * 80)
    result = service.calculate_price(PriceCalculationRequest(
        product_id=100,
        quantity=10,
        customer_id=None,
        promo_code=None
    ))
    print(f"Product: 100")
    print(f"Quantity: 10")
    print(f"Base Price: €{result.breakdown.base_price:.2f}")
    print(f"Subtotal: €{result.breakdown.subtotal:.2f}")
    print(f"Final Price: {result.formatted_price}")
    
    # Example 2: Volume discount
    print("\n Example 2: Volume Discount")
    print("-" * 80)
    result = service.calculate_price(PriceCalculationRequest(
        product_id=100,
        quantity=150,
        customer_id=None,
        promo_code=None
    ))
    print(f"Product: 100")
    print(f"Quantity: 150")
    print(f"Base Price: €{result.breakdown.base_price:.2f}")
    print(f"Subtotal: €{result.breakdown.subtotal:.2f}")
    print(f"Volume Discount: -€{result.breakdown.volume_discount:.2f}")
    print(f"Final Price: {result.formatted_price}")
    print(f"Savings: €{result.savings:.2f} ({result.savings_percentage:.1f}%)")
    
    # Example 3: Promotional pricing
    print("\n Example 3: Promotional Pricing")
    print("-" * 80)
    result = service.calculate_price(PriceCalculationRequest(
        product_id=100,
        quantity=10,
        customer_id=None,
        promo_code="WELCOME50"
    ))
    print(f"Product: 100")
    print(f"Quantity: 10")
    print(f"Promo Code: WELCOME50")
    print(f"Base Price: €{result.breakdown.base_price:.2f}")
    print(f"Subtotal: €{result.breakdown.subtotal:.2f}")
    print(f"Promotional Discount: -€{result.breakdown.promotional_discount:.2f}")
    print(f"Final Price: {result.formatted_price}")
    print(f"Savings: €{result.savings:.2f} ({result.savings_percentage:.1f}%)")
    
    # Example 4: Customer-specific pricing
    print("\n Example 4: Customer-Specific Pricing")
    print("-" * 80)
    result = service.calculate_price(PriceCalculationRequest(
        product_id=100,
        quantity=10,
        customer_id=1,
        promo_code=None
    ))
    print(f"Product: 100")
    print(f"Quantity: 10")
    print(f"Customer: 1 (VIP)")
    print(f"Base Price: €{result.breakdown.base_price:.2f}")
    print(f"Special Price: €{result.breakdown.unit_price:.2f}")
    print(f"Subtotal: €{result.breakdown.subtotal:.2f}")
    print(f"Customer Discount: -€{result.breakdown.customer_discount:.2f}")
    print(f"Final Price: {result.formatted_price}")
    print(f"Savings: €{result.savings:.2f} ({result.savings_percentage:.1f}%)")
    
    # Example 5: Combined discounts
    print("\n Example 5: Combined Discounts (Customer + Volume + Promo)")
    print("-" * 80)
    result = service.calculate_price(PriceCalculationRequest(
        product_id=100,
        quantity=150,
        customer_id=1,
        promo_code="SUMMER2024"
    ))
    print(f"Product: 100")
    print(f"Quantity: 150")
    print(f"Customer: 1 (VIP)")
    print(f"Promo Code: SUMMER2024")
    print(f"\nPrice Breakdown:")
    print(f"  Base Price: €{result.breakdown.base_price:.2f}")
    print(f"  Special Price: €{result.breakdown.unit_price:.2f}")
    print(f"  Subtotal: €{result.breakdown.subtotal:.2f}")
    print(f"  Customer Discount: -€{result.breakdown.customer_discount:.2f}")
    print(f"  Volume Discount: -€{result.breakdown.volume_discount:.2f}")
    print(f"  Promotional Discount: -€{result.breakdown.promotional_discount:.2f}")
    print(f"  Total Discount: -€{result.breakdown.total_discount:.2f}")
    print(f"\n  Final Price: {result.formatted_price}")
    print(f"  Total Savings: €{result.savings:.2f} ({result.savings_percentage:.1f}%)")
    
    print(f"\nApplied Discounts:")
    for discount in result.breakdown.applied_discounts:
        print(f"  • {discount['type']}: -€{discount['amount']:.2f} ({discount['description']})")


def main():
    """Run the demo"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create demo data
        service = create_demo_data(db)
        
        # Demonstrate calculations
        demo_price_calculations(service)
        
        print("\n" + "="*80)
        print(" DEMO COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nAll pricing features demonstrated:")
        print("   Price Lists")
        print("   Tiered Pricing")
        print("   Volume Discounts")
        print("   Promotional Pricing")
        print("   Customer-Specific Pricing")
        print("   Combined Discounts")
        print("   German Number Formatting")
        print("\nAPI Documentation: http://localhost:8000/docs")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
