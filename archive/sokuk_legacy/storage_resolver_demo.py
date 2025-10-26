"""
Demonstration of StorageModelResolver with real product database integration.

This script shows how the StorageModelResolver works with the actual
product database and price matrix system.
"""

import sys
from typing import Any

# Import the resolver
from storage_model_resolver import StorageModelResolver

# Try to import the real product database
try:
    from product_db import get_product_by_id as real_get_product_by_id
    from product_db import list_products as real_list_products
    PRODUCT_DB_AVAILABLE = True
    print("✅ Real product database available")
except ImportError:
    print("⚠️  Product database not available, using mock data")
    PRODUCT_DB_AVAILABLE = False

    # Mock product database for demonstration
    mock_products = {1: {"id": 1,
                         "model_name": "Tesla Powerwall 2",
                         "category": "Batteriespeicher",
                         "storage_power_kw": 13.5},
                     2: {"id": 2,
                         "model_name": "BYD Battery-Box Premium HVS",
                         "category": "Batteriespeicher",
                         "storage_power_kw": 10.24},
                     3: {"id": 3,
                         "model_name": "Sonnen eco 10",
                         "category": "Batteriespeicher",
                         "storage_power_kw": 10.0},
                     4: {"id": 4,
                         "model_name": "Fronius Solar Battery 12.0",
                         "category": "Batteriespeicher",
                         "storage_power_kw": 12.0},
                     }

    def real_get_product_by_id(product_id: int) -> dict[str, Any] | None:
        return mock_products.get(product_id)

    def real_list_products(category: str | None = None) -> list:
        if category == "Batteriespeicher":
            return list(mock_products.values())
        return []


def demonstrate_storage_resolution():
    """Demonstrate the StorageModelResolver functionality."""
    print("\n" + "=" * 60)
    print("StorageModelResolver Demonstration")
    print("=" * 60)

    # Initialize resolver
    resolver = StorageModelResolver()

    # Get available storage products
    storage_products = real_list_products(category="Batteriespeicher")
    print("\n📦 Available storage products in database:")
    for product in storage_products:
        print(
            f"   ID {
                product['id']}: {
                product['model_name']} ({
                product.get(
                    'storage_power_kw',
                    'N/A')} kWh)")

    print("\n🔍 Testing storage resolution scenarios:")
    print("-" * 40)

    # Test scenarios with real IDs from the database
    test_scenarios = [
        # (storage_id, include_storage, description)
        ("81", True, "Valid storage ID with storage included (LUNA2000-10-SO)"),
        ("187", True, "Another valid storage ID (ECS4100 -H2)"),
        ("999", True, "Non-existent storage ID"),
        ("81", False, "Valid storage ID but storage not included"),
        (None, True, "No storage ID provided"),
        ("", True, "Empty storage ID"),
        ("abc", True, "Invalid storage ID format"),
    ]

    for storage_id, include_storage, description in test_scenarios:
        print(f"\n📋 Scenario: {description}")
        print(
            f"   Input: storage_id='{storage_id}', include_storage={include_storage}")

        try:
            result = resolver.resolve_storage_name(
                storage_id,
                include_storage,
                real_get_product_by_id
            )
            print(f"   ✅ Result: '{result}'")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Test normalization
    print("\n🔧 Testing storage name normalization:")
    print("-" * 40)

    normalization_tests = [
        "Tesla Powerwall 2",
        "  Tesla Powerwall 2  ",  # With whitespace
        "ohne speicher",
        "OHNE SPEICHER",
        "kein speicher",
        "no storage",
        "",
        None
    ]

    for test_name in normalization_tests:
        normalized = resolver.normalize_storage_name(test_name)
        print(f"   '{test_name}' → '{normalized}'")

    # Test matrix validation
    print("\n🎯 Testing matrix validation:")
    print("-" * 40)

    # Simulate available storage models in price matrix
    matrix_storage_models = [
        "Tesla Powerwall 2",
        "BYD Battery-Box Premium HVS",
        "Sonnen eco 10",
        "Fronius Solar Battery 12.0"
    ]

    validation_tests = [
        "Tesla Powerwall 2",  # Exact match
        "tesla powerwall 2",  # Case insensitive
        "Tesla",              # Partial match
        "Unknown Battery",    # No match
        "",                   # Empty
    ]

    for test_name in validation_tests:
        result, is_exact = resolver.validate_storage_name_in_matrix(
            test_name, matrix_storage_models
        )
        match_type = "exact" if is_exact else "partial/fallback"
        print(f"   '{test_name}' → '{result}' ({match_type})")

    # Test caching
    print("\n💾 Testing caching functionality:")
    print("-" * 40)

    # Clear cache and show stats
    resolver.clear_cache()
    stats = resolver.get_cache_stats()
    print(f"   Initial cache: {stats}")

    # Make some calls to populate cache
    resolver.resolve_storage_name("1", True, real_get_product_by_id)
    resolver.resolve_storage_name("2", True, real_get_product_by_id)

    stats = resolver.get_cache_stats()
    print(f"   After 2 calls: {stats}")

    # Make same calls again (should use cache)
    resolver.resolve_storage_name("1", True, real_get_product_by_id)
    resolver.resolve_storage_name("2", True, real_get_product_by_id)

    stats = resolver.get_cache_stats()
    print(f"   After repeat calls: {stats}")


def demonstrate_integration_with_price_matrix():
    """Show how StorageModelResolver integrates with price matrix lookups."""
    print("\n🔗 Integration with Price Matrix:")
    print("-" * 40)

    # Simulate a price matrix lookup workflow
    resolver = StorageModelResolver()

    # Simulate user selections from UI
    user_selections = [
        {"module_count": 15, "storage_id": "1", "include_storage": True},
        {"module_count": 20, "storage_id": "2", "include_storage": True},
        {"module_count": 10, "storage_id": None, "include_storage": False},
        {"module_count": 25, "storage_id": "999",
            "include_storage": True},  # Invalid ID
    ]

    for i, selection in enumerate(user_selections, 1):
        print(f"\n   Scenario {i}:")
        print(f"   User selected: {selection['module_count']} modules, "
              f"storage_id={selection['storage_id']}, "
              f"include_storage={selection['include_storage']}")

        # Resolve storage name for matrix lookup
        storage_name = resolver.resolve_storage_name(
            selection['storage_id'],
            selection['include_storage'],
            real_get_product_by_id
        )

        print(f"   → Storage name for matrix lookup: '{storage_name}'")
        print(
            f"   → Matrix lookup would be: modules={
                selection['module_count']}, " f"storage='{storage_name}'")


if __name__ == "__main__":
    print("StorageModelResolver Demo")
    print("This demonstrates the storage ID to model name resolution functionality.")

    try:
        demonstrate_storage_resolution()
        demonstrate_integration_with_price_matrix()

        print("\n✅ Demo completed successfully!")
        print("\nKey features demonstrated:")
        print("  • Storage ID to model name resolution")
        print("  • Fallback to 'Ohne Speicher' for invalid/missing data")
        print("  • Storage name normalization")
        print("  • Matrix validation with partial matching")
        print("  • Caching for performance")
        print("  • Integration with price matrix workflow")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
