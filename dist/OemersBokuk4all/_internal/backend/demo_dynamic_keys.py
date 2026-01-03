"""
Dynamic Keys System Demo

This script demonstrates all features of the dynamic keys system including:
- Key generation
- Key-value storage with typing
- Namespacing
- Search and filtering
- Usage tracking
- Bulk operations
- Export/import

Requirements: 4.1, 6.1
"""

from backend.services.dynamic_key_service import get_dynamic_key_service
from backend.core.dynamic_keys import KeyPrefix, KeyType
import json


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_key_generation():
    """Demonstrate key generation"""
    print_section("1. Key Generation")
    
    service = get_dynamic_key_service()
    
    # Generate different types of keys
    solar_key = service.generate_key(KeyPrefix.SOLAR_CALCULATION)
    print(f"Solar Calculation Key: {solar_key}")
    
    project_key = service.generate_key(KeyPrefix.PROJECT, custom_suffix="residential")
    print(f"Project Key: {project_key}")
    
    hash_key = service.generate_hash_key_from_data("unique_data_123", KeyPrefix.DATA)
    print(f"Hash Key: {hash_key}")
    
    # Generate same hash key again to show consistency
    hash_key2 = service.generate_hash_key_from_data("unique_data_123", KeyPrefix.DATA)
    print(f"Same Hash Key: {hash_key2}")
    print(f"Keys match: {hash_key == hash_key2}")


def demo_key_value_storage():
    """Demonstrate key-value storage with typing"""
    print_section("2. Key-Value Storage with Typing")
    
    service = get_dynamic_key_service()
    
    # Store different types of values
    service.set_value("system_size", 10.5, key_type=KeyType.FLOAT)
    print("Stored: system_size = 10.5 (FLOAT)")
    
    service.set_value("module_count", 30, key_type=KeyType.INTEGER)
    print("Stored: module_count = 30 (INTEGER)")
    
    service.set_value("system_price", 16999.00, key_type=KeyType.CURRENCY)
    print("Stored: system_price = 16999.00 (CURRENCY)")
    
    service.set_value("efficiency", 85.5, key_type=KeyType.PERCENTAGE)
    print("Stored: efficiency = 85.5 (PERCENTAGE)")
    
    service.set_value("customer_email", "customer@example.com", key_type=KeyType.EMAIL)
    print("Stored: customer_email = customer@example.com (EMAIL)")
    
    # Retrieve values
    print("\nRetrieving values:")
    print(f"system_size: {service.get_value('system_size')}")
    print(f"module_count: {service.get_value('module_count')}")
    print(f"system_price: {service.get_value('system_price')}")
    
    # Try to store invalid type (will raise error)
    try:
        service.set_value("invalid_int", "not_a_number", key_type=KeyType.INTEGER)
    except ValueError as e:
        print(f"\nType validation error (expected): {e}")


def demo_namespaces():
    """Demonstrate namespace organization"""
    print_section("3. Namespace Organization")
    
    service = get_dynamic_key_service()
    
    # Create namespace hierarchy
    service.create_namespace("root.solar.calculations.residential")
    service.create_namespace("root.solar.calculations.commercial")
    service.create_namespace("root.heatpump.calculations")
    
    # Add keys to namespaces
    service.set_value(
        "res_system_1",
        {"size": 10.5, "modules": 30},
        key_type=KeyType.JSON,
        namespace="root.solar.calculations.residential"
    )
    
    service.set_value(
        "res_system_2",
        {"size": 15.0, "modules": 45},
        key_type=KeyType.JSON,
        namespace="root.solar.calculations.residential"
    )
    
    service.set_value(
        "com_system_1",
        {"size": 50.0, "modules": 150},
        key_type=KeyType.JSON,
        namespace="root.solar.calculations.commercial"
    )
    
    # List namespaces
    print("All namespaces:")
    for ns in service.list_namespaces():
        print(f"  - {ns}")
    
    # Get keys from specific namespace
    print("\nKeys in root.solar.calculations.residential:")
    keys = service.get_namespace_keys("root.solar.calculations.residential")
    for key in keys:
        print(f"  - {key}")
    
    # Get keys recursively
    print("\nAll keys in root.solar (recursive):")
    keys = service.get_namespace_keys("root.solar", recursive=True)
    for key in keys:
        print(f"  - {key}")


def demo_search_and_filter():
    """Demonstrate search and filtering"""
    print_section("4. Search and Filtering")
    
    service = get_dynamic_key_service()
    
    # Add some test data
    service.set_value("solar_calc_1", 10.5, key_type=KeyType.FLOAT)
    service.set_value("solar_calc_2", 15.0, key_type=KeyType.FLOAT)
    service.set_value("solar_price_1", 16999.00, key_type=KeyType.CURRENCY)
    service.set_value("heatpump_calc_1", 8.5, key_type=KeyType.FLOAT)
    
    # Search by pattern
    print("Search by pattern 'solar_.*':")
    keys = service.search_keys(pattern="solar_.*")
    for key in keys:
        print(f"  - {key}")
    
    # Filter by type
    print("\nFilter by type FLOAT:")
    keys = service.filter_by_type(KeyType.FLOAT)
    for key in keys:
        print(f"  - {key}: {service.get_value(key)}")
    
    # Filter by type CURRENCY
    print("\nFilter by type CURRENCY:")
    keys = service.filter_by_type(KeyType.CURRENCY)
    for key in keys:
        print(f"  - {key}: {service.get_value(key)}")
    
    # Combined search
    print("\nCombined search (pattern + type):")
    keys = service.search_keys(
        pattern="solar_calc_.*",
        key_type=KeyType.FLOAT
    )
    for key in keys:
        print(f"  - {key}: {service.get_value(key)}")


def demo_usage_tracking():
    """Demonstrate usage tracking"""
    print_section("5. Usage Tracking")
    
    service = get_dynamic_key_service()
    
    # Access some keys multiple times
    for _ in range(10):
        service.get_value("system_size", track_usage=True)
    
    for _ in range(5):
        service.get_value("module_count", track_usage=True)
    
    for _ in range(3):
        service.get_value("system_price", track_usage=True)
    
    # Get usage statistics
    print("Usage statistics for 'system_size':")
    stats = service.get_usage_statistics("system_size")
    print(f"  Access count: {stats.get('access_count', 0)}")
    print(f"  First access: {stats.get('first_access', 'N/A')}")
    print(f"  Last access: {stats.get('last_access', 'N/A')}")
    
    # Get most accessed keys
    print("\nMost accessed keys:")
    most_accessed = service.get_most_accessed_keys(limit=5)
    for key, count in most_accessed:
        print(f"  - {key}: {count} accesses")
    
    # Get recently accessed keys
    print("\nRecently accessed keys:")
    recent = service.get_recently_accessed_keys(limit=5)
    for key, timestamp in recent:
        print(f"  - {key}: {timestamp}")


def demo_bulk_operations():
    """Demonstrate bulk operations"""
    print_section("6. Bulk Operations")
    
    service = get_dynamic_key_service()
    
    # Bulk set
    print("Bulk setting values:")
    items = {
        "bulk_key_1": "value1",
        "bulk_key_2": "value2",
        "bulk_key_3": "value3",
        "bulk_key_4": "value4",
        "bulk_key_5": "value5"
    }
    service.bulk_set(items)
    print(f"Set {len(items)} keys")
    
    # Bulk get
    print("\nBulk getting values:")
    keys_to_get = ["bulk_key_1", "bulk_key_2", "bulk_key_3"]
    values = service.bulk_get(keys_to_get)
    for key, value in values.items():
        print(f"  - {key}: {value}")
    
    # Bulk delete
    print("\nBulk deleting keys:")
    keys_to_delete = ["bulk_key_4", "bulk_key_5"]
    deleted_count = service.bulk_delete(keys_to_delete)
    print(f"Deleted {deleted_count} keys")


def demo_metadata():
    """Demonstrate metadata usage"""
    print_section("7. Metadata Usage")
    
    service = get_dynamic_key_service()
    
    # Store value with metadata
    service.set_value(
        "solar_system_premium",
        {"size": 20.0, "modules": 60},
        key_type=KeyType.JSON,
        metadata={
            "customer": "John Doe",
            "date": "2023-11-16",
            "location": "Berlin",
            "system_type": "premium",
            "warranty_years": 25
        }
    )
    
    print("Stored value with metadata")
    
    # Retrieve metadata
    metadata = service.get_key_metadata("solar_system_premium")
    print("\nMetadata:")
    for key, value in metadata.items():
        print(f"  - {key}: {value}")
    
    # Search by metadata
    print("\nSearch by metadata (system_type=premium):")
    keys = service.search_keys(
        metadata_filter={"system_type": "premium"}
    )
    for key in keys:
        print(f"  - {key}")


def demo_export_import():
    """Demonstrate export and import"""
    print_section("8. Export and Import")
    
    service = get_dynamic_key_service()
    
    # Create a namespace with some data
    service.create_namespace("root.export_demo")
    service.set_value("demo_key_1", "value1", namespace="root.export_demo")
    service.set_value("demo_key_2", 42, key_type=KeyType.INTEGER, namespace="root.export_demo")
    service.set_value("demo_key_3", 99.99, key_type=KeyType.CURRENCY, namespace="root.export_demo")
    
    # Export configuration
    print("Exporting configuration from root.export_demo:")
    data = service.export_configuration(namespace="root.export_demo")
    print(json.dumps(data, indent=2))
    
    # Clear namespace
    print("\nClearing namespace...")
    service.clear_all(namespace="root.export_demo")
    
    # Verify it's empty
    keys = service.get_namespace_keys("root.export_demo")
    print(f"Keys after clear: {len(keys)}")
    
    # Import configuration
    print("\nImporting configuration back...")
    service.import_configuration(data, namespace="root.export_demo")
    
    # Verify data is restored
    keys = service.get_namespace_keys("root.export_demo")
    print(f"Keys after import: {len(keys)}")
    for key in keys:
        value = service.get_value(key)
        print(f"  - {key}: {value}")


def demo_statistics():
    """Demonstrate comprehensive statistics"""
    print_section("9. Comprehensive Statistics")
    
    service = get_dynamic_key_service()
    
    # Get overall statistics
    stats = service.get_statistics()
    
    print("Store Statistics:")
    print(f"  Total keys: {stats['store']['total_keys']}")
    print(f"  Namespaces: {stats['store']['namespaces']}")
    
    print("\nUsage Statistics:")
    usage = stats['usage']
    print(f"  Total keys accessed: {usage.get('total_keys_accessed', 0)}")
    print(f"  Total accesses: {usage.get('total_accesses', 0)}")
    
    print("\nMost Accessed Keys:")
    for key, count in stats.get('most_accessed', []):
        print(f"  - {key}: {count} accesses")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("  DYNAMIC KEYS SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    try:
        demo_key_generation()
        demo_key_value_storage()
        demo_namespaces()
        demo_search_and_filter()
        demo_usage_tracking()
        demo_bulk_operations()
        demo_metadata()
        demo_export_import()
        demo_statistics()
        
        print("\n" + "=" * 60)
        print("  DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("\nAll features demonstrated successfully!")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
