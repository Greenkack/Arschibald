#!/usr/bin/env python3
"""
Debug - Zeigt was genau in extract_brands_from_project_data passiert
"""

from pdf_logo_integration import extract_brands_from_project_data
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Test-Daten wie im simple_logo_test.py
project_data = {
    "customer_data": {
        "first_name": "Max",
        "last_name": "Mustermann"
    },
    "project_details": {},
    "selected_products": {
        "module": {
            "product_id": 1,
            "brand_name": "Huawei",
            "product_name": "SUN2000-8KTL-M1"
        },
        "inverter": {
            "product_id": 2,
            "brand_name": "GoodWe",
            "product_name": "GW8K-ET"
        },
        "storage": {
            "product_id": 3,
            "brand_name": "BYD",
            "product_name": "Battery-Box Premium HVM"
        }
    }
}

print("🔍 DEBUG: extract_brands_from_project_data")
print("=" * 50)

print("📥 Input project_data structure:")
print(f"  Keys auf oberster Ebene: {list(project_data.keys())}")
print(
    f"  selected_products Keys: {
        list(
            project_data.get(
                'selected_products',
                {}).keys())}")

# Test original function
result = extract_brands_from_project_data(project_data)
print(f"\n📤 Result from extract_brands_from_project_data: {result}")

print("\n🔧 Manual extraction für selected_products:")
selected_products = project_data.get('selected_products', {})
manual_result = {}

for prod_key, prod_data in selected_products.items():
    if isinstance(prod_data, dict):
        brand = prod_data.get('brand_name') or prod_data.get('brand')
        print(f"  {prod_key}: {brand}")

        # Map to logo category names
        category_mapping = {
            'module': 'modul',
            'inverter': 'wechselrichter',
            'storage': 'batteriespeicher'
        }

        mapped_category = category_mapping.get(prod_key, prod_key)
        if brand:
            manual_result[mapped_category] = brand

print(f"\n📋 Manual result: {manual_result}")
