"""Quick test of PV mounting database"""
from pv_mounting_database import read_components

# Test 1: All components
all_comps = read_components()
print(f"Total components: {len(all_comps)}")

if all_comps:
    print(f"   First component: {all_comps[0].get('product_name', 'UNNAMED')}")
    print(f"   Manufacturer: {all_comps[0].get('manufacturer', 'UNKNOWN')}")
    print(f"   Keys available: {list(all_comps[0].keys())[:10]}")  # First 10 keys

# Test 2: Filtered by manufacturer
k2_comps = read_components(filters={'manufacturer': 'K2 Systems'})
print(f"\nK2 Systems components: {len(k2_comps)}")

# Test 3: Filtered by category
hooks = read_components(filters={'category': 'Dachhaken'})
print(f"\nDachhaken components: {len(hooks)}")

if hooks:
    for hook in hooks[:3]:
        print(f"   - {hook.get('product_name', 'UNNAMED')} ({hook.get('manufacturer', 'UNKNOWN')}) - {hook.get('price_netto', 0):.2f} EUR")
