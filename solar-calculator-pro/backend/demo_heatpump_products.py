"""
Heat Pump Product Database - Demo Script

This script demonstrates all features of the heat pump product database system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from solar-calculator-pro.backend.services.heatpump_product_service import heatpump_product_service
from solar-calculator-pro.backend.models.heatpump_product_schemas import (
    HeatPumpFilterRequest,
    HeatPumpComparisonRequest,
    HeatPumpRecommendationRequest,
    HeatPumpAvailabilityUpdate,
    HeatPumpBulkAvailabilityRequest,
    HeatPumpType)


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_get_all_products():
    """Demo: Get all products"""
    print_section("1. Get All Products")
    
    products = heatpump_product_service.get_all_products()
    print(f"Total products in database: {len(products)}")
    
    if products:
        print("\nFirst 3 products:")
        for product in products[:3]:
            print(f"  - {product.manufacturer} {product.model}")
            print(f"    Type: {product.heatpump_type}")
            print(f"    Power: {min(product.heating_power_kw)}-{max(product.heating_power_kw)} kW")
            print(f"    SCOP: {product.scop}")
            print()


def demo_filter_products():
    """Demo: Filter products"""
    print_section("2. Filter Products")
    
    # Example 1: High efficiency products
    print("Example 1: High efficiency products (SCOP >= 4.5)")
    filter_req = HeatPumpFilterRequest(
        min_scop=4.5,
        available_only=True,
        sort_by="scop",
        sort_order="desc",
        page_size=5
    )
    result = heatpump_product_service.filter_products(filter_req)
    print(f"Found {result.total_count} products")
    for product in result.products:
        print(f"  - {product.manufacturer} {product.model}: SCOP {product.scop}")
    
    # Example 2: Budget-friendly options
    print("\nExample 2: Budget-friendly options (< 12000 EUR)")
    filter_req = HeatPumpFilterRequest(
        max_price=12000.00,
        min_scop=4.0,
        available_only=True,
        sort_by="price",
        sort_order="asc",
        page_size=5
    )
    result = heatpump_product_service.filter_products(filter_req)
    print(f"Found {result.total_count} products")
    for product in result.products:
        price = product.base_price if product.base_price else "N/A"
        print(f"  - {product.manufacturer} {product.model}: {price} EUR")
    
    # Example 3: Smart grid ready products
    print("\nExample 3: Smart grid ready products")
    filter_req = HeatPumpFilterRequest(
        smart_grid_required=True,
        internet_required=True,
        available_only=True,
        page_size=5
    )
    result = heatpump_product_service.filter_products(filter_req)
    print(f"Found {result.total_count} products")
    for product in result.products:
        print(f"  - {product.manufacturer} {product.model}")
        print(f"    Smart Grid: {product.smart_grid_ready}, Internet: {product.internet_connectivity}")


def demo_compare_products():
    """Demo: Compare products"""
    print_section("3. Compare Products")
    
    # Get some products to compare
    products = heatpump_product_service.get_all_products()[:3]
    product_ids = [
        f"{p.manufacturer}_{p.model}".replace(" ", "_")
        for p in products
    ]
    
    print(f"Comparing {len(product_ids)} products:")
    for pid in product_ids:
        print(f"  - {pid}")
    
    comparison_req = HeatPumpComparisonRequest(
        product_ids=product_ids,
        comparison_criteria=["efficiency", "power", "cost", "features"]
    )
    
    try:
        result = heatpump_product_service.compare_products(comparison_req)
        
        print("\nBest in each category:")
        for category, product_name in result.best_in_category.items():
            print(f"  {category.capitalize()}: {product_name}")
        
        print("\nSummary:")
        print(f"  Manufacturers: {', '.join(result.summary['manufacturers'])}")
        print(f"  Price range: {result.summary['price_range']['min']} - {result.summary['price_range']['max']} EUR")
        print(f"  Power range: {result.summary['power_range']['min']} - {result.summary['power_range']['max']} kW")
    except ValueError as e:
        print(f"Error: {e}")


def demo_recommendations():
    """Demo: Get recommendations"""
    print_section("4. Get Intelligent Recommendations")
    
    # Example building scenario
    print("Building scenario:")
    print("  - Area: 150 sqm")
    print("  - Insulation: Good")
    print("  - Climate: Central Europe")
    print("  - Lowest outdoor temp: -15°C")
    print("  - Hot water required: Yes")
    print("  - Budget: 18,000 EUR")
    print("  - Preferences: Quiet, smart features")
    
    rec_req = HeatPumpRecommendationRequest(
        building_area_sqm=150.0,
        building_insulation="good",
        building_age=15,
        desired_indoor_temp=21.0,
        climate_zone="Central Europe",
        lowest_outdoor_temp=-15.0,
        existing_heating_system="gas",
        radiator_type="low-temp",
        hot_water_required=True,
        cooling_required=False,
        max_budget=18000.00,
        prefer_quiet=True,
        prefer_smart_features=True,
        target_scop=4.5
    )
    
    result = heatpump_product_service.recommend_products(rec_req)
    
    print(f"\nEstimated heat load: {result.estimated_heat_load_kw} kW")
    print(f"Recommended power range: {result.recommended_power_range['min']:.1f} - {result.recommended_power_range['max']:.1f} kW")
    
    print(f"\nTop {len(result.recommendations)} recommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"\n{i}. {rec.product.manufacturer} {rec.product.model}")
        print(f"   Suitability Score: {rec.suitability_score}/100")
        print(f"   Reasons:")
        for reason in rec.recommendation_reasons:
            print(f"     - {reason}")
        if rec.estimated_annual_cost:
            print(f"   Estimated annual cost: {rec.estimated_annual_cost:.2f} EUR")
        if rec.estimated_savings:
            print(f"   Estimated annual savings: {rec.estimated_savings:.2f} EUR")
        if rec.payback_period_years:
            print(f"   Payback period: {rec.payback_period_years:.1f} years")


def demo_availability():
    """Demo: Availability tracking"""
    print_section("5. Availability Tracking")
    
    # Get a product
    products = heatpump_product_service.get_all_products()
    if not products:
        print("No products available for demo")
        return
    
    product = products[0]
    product_id = f"{product.manufacturer}_{product.model}".replace(" ", "_")
    
    print(f"Checking availability for: {product.manufacturer} {product.model}")
    
    # Get availability
    availability = heatpump_product_service.get_availability(product_id)
    if availability:
        print(f"  Available: {availability.available}")
        print(f"  Stock level: {availability.stock_level}")
        print(f"  Lead time: {availability.lead_time_days} days")
    
    # Update availability
    print("\nUpdating availability...")
    update = HeatPumpAvailabilityUpdate(
        product_id=product_id,
        available=True,
        stock_level="low_stock",
        lead_time_days=21
    )
    updated = heatpump_product_service.update_availability(update)
    print(f"  New stock level: {updated.stock_level}")
    print(f"  New lead time: {updated.lead_time_days} days")
    
    # Get alternatives
    print("\nFinding alternative products...")
    alternatives = heatpump_product_service.suggest_alternatives(product_id, max_alternatives=3)
    print(f"Found {len(alternatives)} alternatives:")
    for alt_id in alternatives:
        alt_product = heatpump_product_service.get_product_by_id(alt_id)
        if alt_product:
            print(f"  - {alt_product.manufacturer} {alt_product.model}")


def demo_statistics():
    """Demo: Database statistics"""
    print_section("6. Database Statistics")
    
    products = heatpump_product_service.get_all_products()
    
    # Calculate statistics
    available_products = [p for p in products if p.available]
    products_with_price = [p for p in products if p.base_price is not None]
    products_with_scop = [p for p in products if p.scop is not None]
    
    print(f"Total products: {len(products)}")
    print(f"Available products: {len(available_products)}")
    print(f"Manufacturers: {len(set(p.manufacturer for p in products))}")
    print(f"Product types: {len(set(p.heatpump_type for p in products))}")
    
    if products_with_price:
        print(f"\nPrice range:")
        print(f"  Min: {min(p.base_price for p in products_with_price):.2f} EUR")
        print(f"  Max: {max(p.base_price for p in products_with_price):.2f} EUR")
        print(f"  Average: {sum(p.base_price for p in products_with_price) / len(products_with_price):.2f} EUR")
    
    print(f"\nPower range:")
    print(f"  Min: {min(min(p.heating_power_kw) for p in products):.1f} kW")
    print(f"  Max: {max(max(p.heating_power_kw) for p in products):.1f} kW")
    
    if products_with_scop:
        print(f"\nEfficiency (SCOP):")
        print(f"  Min: {min(p.scop for p in products_with_scop):.2f}")
        print(f"  Max: {max(p.scop for p in products_with_scop):.2f}")
        print(f"  Average: {sum(p.scop for p in products_with_scop) / len(products_with_scop):.2f}")
    
    print(f"\nFeatures:")
    print(f"  Smart grid ready: {sum(1 for p in products if p.smart_grid_ready)}")
    print(f"  Internet connectivity: {sum(1 for p in products if p.internet_connectivity)}")
    print(f"  Inverter technology: {sum(1 for p in products if p.inverter_technology)}")
    print(f"  Modulating: {sum(1 for p in products if p.modulating)}")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  HEAT PUMP PRODUCT DATABASE - DEMO")
    print("=" * 80)
    
    try:
        demo_get_all_products()
        demo_filter_products()
        demo_compare_products()
        demo_recommendations()
        demo_availability()
        demo_statistics()
        
        print("\n" + "=" * 80)
        print("  DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
