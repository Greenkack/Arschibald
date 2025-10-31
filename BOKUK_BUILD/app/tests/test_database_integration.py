#!/usr/bin/env python3
"""
Test script for the new database_bridge.py integration
Tests all database APIs to ensure they work correctly with SolarCalculator
"""

import json
import os
import subprocess
import sys

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_database_command(command, *args):
    """Run a database command and return the result"""
    try:
        cmd = ['python', 'database_bridge.py', command] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__))
        if result.returncode == 0:
            return json.loads(result.stdout)
        print(f"Error running {command}: {result.stderr}")
        return None
    except Exception as e:
        print(f"Exception running {command}: {e}")
        return None


def test_database_apis():
    """Test all database APIs that SolarCalculator needs"""
    print("=== Testing Database Bridge APIs ===\n")

    # Test 1: List all categories
    print("1. Testing list_categories...")
    categories = run_database_command('list_categories')
    if categories and categories.get('success'):
        print(
            f"   ✓ Found {len(categories['data'])} categories: {categories['data']}")
    else:
        print("   ✗ Failed to list categories")

    # Test 2: List manufacturers
    print("\n2. Testing list_manufacturers...")
    manufacturers = run_database_command('list_manufacturers')
    if manufacturers and manufacturers.get('success'):
        print(
            f"   ✓ Found {len(manufacturers['data'])} manufacturers: {manufacturers['data'][:5]}...")
    else:
        print("   ✗ Failed to list manufacturers")

    # Test 3: List Modul products
    print("\n3. Testing list_products for 'Modul' category...")
    modules = run_database_command('list_products', '--category=Modul')
    if modules and modules.get('success'):
        print(f"   ✓ Found {len(modules['data'])} modules")
        # Show first few modules
        for i, module in enumerate(modules['data'][:3]):
            print(
                f"     - {
                    module.get(
                        'brand',
                        'Unknown')} {
                    module.get(
                        'model_name',
                        'Unknown')} ({
                    module.get(
                        'capacity_w',
                        0)}W)")
        if len(modules['data']) > 3:
            print(f"     ... and {len(modules['data']) - 3} more")
    else:
        print("   ✗ Failed to list Modul products")

    # Test 4: List Wechselrichter products
    print("\n4. Testing list_products for 'Wechselrichter' category...")
    inverters = run_database_command(
        'list_products', '--category=Wechselrichter')
    if inverters and inverters.get('success'):
        print(f"   ✓ Found {len(inverters['data'])} inverters")
        for i, inverter in enumerate(inverters['data'][:2]):
            print(
                f"     - {
                    inverter.get(
                        'brand',
                        'Unknown')} {
                    inverter.get(
                        'model_name',
                        'Unknown')} ({
                    inverter.get(
                        'power_kw',
                        0)}kW)")
    else:
        print("   ✗ Failed to list Wechselrichter products")

    # Test 5: List Batteriespeicher products
    print("\n5. Testing list_products for 'Batteriespeicher' category...")
    batteries = run_database_command(
        'list_products', '--category=Batteriespeicher')
    if batteries and batteries.get('success'):
        print(f"   ✓ Found {len(batteries['data'])} battery storage systems")
        for i, battery in enumerate(batteries['data'][:2]):
            print(
                f"     - {
                    battery.get(
                        'brand',
                        'Unknown')} {
                    battery.get(
                        'model_name',
                        'Unknown')} ({
                    battery.get(
                        'storage_power_kw',
                        0)}kWh)")
    else:
        print("   ✗ Failed to list Batteriespeicher products")

    # Test 6: Get products by manufacturer
    if manufacturers and manufacturers.get(
            'success') and manufacturers['data']:
        first_manufacturer = manufacturers['data'][0]
        print(
            f"\n6. Testing get_products_by_manufacturer for '{first_manufacturer}'...")
        manufacturer_products = run_database_command(
            'get_products_by_manufacturer',
            f'--manufacturer={first_manufacturer}')
        if manufacturer_products and manufacturer_products.get('success'):
            print(
                f"   ✓ Found {len(manufacturer_products['data'])} products from {first_manufacturer}")
        else:
            print(f"   ✗ Failed to get products for {first_manufacturer}")

    # Test 7: Test database initialization
    print("\n7. Testing init_database...")
    init_result = run_database_command('init_database')
    if init_result and init_result.get('success'):
        print("   ✓ Database initialization successful")
    else:
        print("   ✗ Database initialization failed")

    # Test 8: Get specific product by ID
    if modules and modules.get('success') and modules['data']:
        first_module = modules['data'][0]
        module_id = first_module.get('id')
        print(f"\n8. Testing get_product_by_id for ID {module_id}...")
        product = run_database_command(
            'get_product_by_id', f'--id={module_id}')
        if product and product.get('success') and product.get('data'):
            print(
                f"   ✓ Retrieved product: {
                    product['data'].get('brand')} {
                    product['data'].get('model_name')}")
        else:
            print(f"   ✗ Failed to get product by ID {module_id}")

    print("\n=== Database Bridge Test Complete ===")
    print("Database APIs are ready for SolarCalculator integration!")


if __name__ == "__main__":
    test_database_apis()
