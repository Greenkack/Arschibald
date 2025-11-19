"""
Dynamic Key System - Quick Demo

This demonstrates the key features of the Dynamic Key System.
"""

import sys
from pathlib import Path
import importlib.util

# Load the module directly
spec = importlib.util.spec_from_file_location(
    "dynamic_keys",
    Path(__file__).parent / "core" / "dynamic_keys.py"
)
dynamic_keys = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dynamic_keys)

# Import classes
DynamicKeyMixin = dynamic_keys.DynamicKeyMixin
DynamicKeyIndex = dynamic_keys.DynamicKeyIndex
DynamicKeyValidator = dynamic_keys.DynamicKeyValidator
KeyPrefix = dynamic_keys.KeyPrefix
generate_hash_key = dynamic_keys.generate_hash_key


def demo_basic_usage():
    """Demonstrate basic key generation"""
    print("=" * 60)
    print("DEMO 1: Basic Key Generation")
    print("=" * 60)
    
    # Create a simple object with key generation
    mixin = DynamicKeyMixin()
    
    # Generate different types of keys
    solar_key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
    print(f"Solar calculation key: {solar_key}")
    
    project_key = mixin.generate_dynamic_key(
        KeyPrefix.PROJECT,
        custom_suffix="house_berlin"
    )
    print(f"Project key: {project_key}")
    
    # Generate hash-based key
    email = "user@example.com"
    user_key = generate_hash_key(email, KeyPrefix.USER)
    print(f"User key (hash-based): {user_key}")
    
    print()


def demo_index_usage():
    """Demonstrate index operations"""
    print("=" * 60)
    print("DEMO 2: Index Operations")
    print("=" * 60)
    
    index = DynamicKeyIndex()
    
    # Add solar calculations
    calc1_key = "SOL_20231116_001"
    calc1_data = {"power": 10.5, "modules": 30, "location": "Berlin"}
    index.add(calc1_key, calc1_data, metadata={"user": "john"})
    
    calc2_key = "SOL_20231116_002"
    calc2_data = {"power": 15.0, "modules": 45, "location": "Munich"}
    index.add(calc2_key, calc2_data, metadata={"user": "jane"})
    
    # Add heat pump calculation
    hp_key = "HP_20231116_001"
    hp_data = {"cop": 4.5, "power": 8.0}
    index.add(hp_key, hp_data)
    
    print(f"Added 3 objects to index")
    print(f"Total objects: {index.count()}")
    
    # Retrieve by key
    retrieved = index.get(calc1_key)
    print(f"\nRetrieved {calc1_key}:")
    print(f"  Data: {retrieved}")
    print(f"  Metadata: {index.get_metadata(calc1_key)}")
    
    # Query by prefix
    solar_calcs = index.get_by_prefix("SOL")
    print(f"\nSolar calculations: {len(solar_calcs)}")
    for calc in solar_calcs:
        print(f"  - {calc['location']}: {calc['power']} kWp")
    
    # Get statistics
    stats = index.get_statistics()
    print(f"\nIndex statistics:")
    print(f"  Total keys: {stats['total_keys']}")
    print(f"  Prefixes: {stats['total_prefixes']}")
    print(f"  Keys by prefix: {stats['keys_by_prefix']}")
    
    print()


def demo_validation():
    """Demonstrate key validation"""
    print("=" * 60)
    print("DEMO 3: Key Validation")
    print("=" * 60)
    
    validator = DynamicKeyValidator()
    
    # Test various keys
    test_keys = [
        ("SOL_20231116_143052_a1b2c3d4", "Valid solar key"),
        ("HP_test_123", "Valid heat pump key"),
        ("invalid_key", "Invalid format"),
        ("sol_lowercase", "Invalid (lowercase prefix)"),
        ("PRJ_20231116_143052_a1b2c3d4_important", "Valid project key")
    ]
    
    print("Validating keys:\n")
    for key, description in test_keys:
        is_valid, error = validator.validate(key)
        status = "✓" if is_valid else "✗"
        print(f"{status} {description}")
        print(f"  Key: {key}")
        if not is_valid:
            print(f"  Error: {error}")
        print()


def demo_key_parsing():
    """Demonstrate key parsing"""
    print("=" * 60)
    print("DEMO 4: Key Parsing and Analysis")
    print("=" * 60)
    
    key = "SOL_20231116_143052_a1b2c3d4_berlin"
    
    print(f"Analyzing key: {key}\n")
    
    # Extract prefix
    prefix = DynamicKeyMixin.extract_prefix(key)
    print(f"Prefix: {prefix}")
    
    # Extract all components
    components = DynamicKeyMixin.extract_components(key)
    print(f"Full key: {components['full_key']}")
    print(f"Parts: {components['parts']}")
    if 'date' in components:
        print(f"Date: {components['date']}")
    if 'uuid' in components:
        print(f"UUID: {components['uuid']}")
    
    print()


def demo_real_world_scenario():
    """Demonstrate a real-world usage scenario"""
    print("=" * 60)
    print("DEMO 5: Real-World Scenario - Solar Calculator Service")
    print("=" * 60)
    
    # Simulate a solar calculator service
    index = DynamicKeyIndex()
    
    # User creates multiple calculations
    calculations = [
        {"power": 10.5, "modules": 30, "location": "Berlin", "user": "john"},
        {"power": 15.0, "modules": 45, "location": "Munich", "user": "john"},
        {"power": 8.5, "modules": 25, "location": "Hamburg", "user": "jane"},
    ]
    
    print("Creating solar calculations...\n")
    
    for i, calc in enumerate(calculations, 1):
        # Generate key
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            KeyPrefix.SOLAR_CALCULATION,
            custom_suffix=calc['location'].lower()
        )
        
        # Add to index
        metadata = {
            "user": calc['user'],
            "created_at": "2023-11-16T14:30:00",
            "version": 1
        }
        index.add(key, calc, metadata)
        
        print(f"Calculation {i}:")
        print(f"  Key: {key}")
        print(f"  Location: {calc['location']}")
        print(f"  Power: {calc['power']} kWp")
        print(f"  User: {calc['user']}")
        print()
    
    # Query user's calculations
    print("Retrieving John's calculations:")
    all_calcs = index.get_by_prefix("SOL")
    john_calcs = [
        calc for calc in all_calcs
        if calc.get('user') == 'john'
    ]
    print(f"Found {len(john_calcs)} calculations for John")
    for calc in john_calcs:
        print(f"  - {calc['location']}: {calc['power']} kWp")
    
    print()


def demo_performance():
    """Demonstrate performance characteristics"""
    print("=" * 60)
    print("DEMO 6: Performance Characteristics")
    print("=" * 60)
    
    import time
    
    index = DynamicKeyIndex()
    
    # Add many objects
    n = 1000
    print(f"Adding {n} objects to index...")
    
    start = time.time()
    for i in range(n):
        key = f"DAT_{i:06d}"
        index.add(key, {"id": i, "data": f"value_{i}"})
    add_time = time.time() - start
    
    print(f"  Time: {add_time:.4f} seconds")
    print(f"  Rate: {n/add_time:.0f} ops/sec")
    
    # Lookup performance
    print(f"\nLookup performance (100 random keys)...")
    start = time.time()
    for i in range(0, n, 10):
        key = f"DAT_{i:06d}"
        obj = index.get(key)
    lookup_time = time.time() - start
    
    print(f"  Time: {lookup_time:.4f} seconds")
    if lookup_time > 0:
        print(f"  Rate: {100/lookup_time:.0f} ops/sec")
    else:
        print(f"  Rate: Very fast (< 0.0001 seconds)")
    
    # Prefix query performance
    print(f"\nPrefix query performance...")
    start = time.time()
    results = index.get_by_prefix("DAT")
    query_time = time.time() - start
    
    print(f"  Time: {query_time:.4f} seconds")
    print(f"  Results: {len(results)} objects")
    
    # Memory usage estimate
    stats = index.get_statistics()
    print(f"\nIndex statistics:")
    print(f"  Total keys: {stats['total_keys']}")
    print(f"  Estimated memory: ~{stats['total_keys'] * 100 / 1024:.1f} KB")
    
    print()


def run_all_demos():
    """Run all demonstrations"""
    print("\n")
    print("=" * 60)
    print(" " * 10 + "DYNAMIC KEY SYSTEM DEMONSTRATION")
    print("=" * 60)
    print()
    
    demo_basic_usage()
    demo_index_usage()
    demo_validation()
    demo_key_parsing()
    demo_real_world_scenario()
    demo_performance()
    
    print("=" * 60)
    print("All demonstrations complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_demos()
