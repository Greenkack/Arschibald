"""
pv_mounting_db_bridge.py

Bridge module for Solar Calculator integration.
Provides simplified interface to query PV mounting components from database.

This module mirrors the pattern used in product_db.py for PV modules/inverters,
but specialized for mounting components with category-based filtering.

Used by solar_calculator.py for dropdown population and product selection.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

# Import database functions
try:
    from pv_mounting_database import (
        initialize_database,
        read_components,
        search_components,
    )
    PV_MOUNTING_DB_AVAILABLE = True
except ImportError:
    PV_MOUNTING_DB_AVAILABLE = False


def get_pv_mounting_component_by_id(component_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single mounting component by ID.
    
    Args:
        component_id: Component ID
        
    Returns:
        Component dict or None if not found
    """
    if not PV_MOUNTING_DB_AVAILABLE:
        return None
    
    try:
        components = read_components(filters={'id': component_id}, limit=1)
        return components[0] if components else None
    except Exception:
        return None


def get_pv_mounting_component_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a single mounting component by exact name match.
    
    Args:
        name: Component name (searches in 'product_name' field)
        
    Returns:
        Component dict or None if not found
    """
    if not PV_MOUNTING_DB_AVAILABLE:
        return None
    
    try:
        components = read_components(filters={'product_name': name}, limit=1)
        return components[0] if components else None
    except Exception:
        return None


def get_pv_mounting_components_by_category(
    category: str,
    manufacturer: Optional[str] = None,
    roof_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all mounting components for a specific category with optional filters.
    
    Args:
        category: Component category (e.g., "Dachhaken", "Montageschiene")
        manufacturer: Optional manufacturer filter
        roof_type: Optional roof type filter
        
    Returns:
        List of component dicts matching criteria
    """
    if not PV_MOUNTING_DB_AVAILABLE:
        return []
    
    try:
        initialize_database()  # Ensure DB exists
        
        filters = {'category': category}
        if manufacturer:
            filters['manufacturer'] = manufacturer
        if roof_type:
            filters['roof_type'] = roof_type
        
        return read_components(filters=filters)
    except Exception:
        return []


def get_pv_mounting_manufacturers_by_category(category: str) -> List[str]:
    """
    Get list of unique manufacturers offering products in a specific category.
    
    Args:
        category: Component category
        
    Returns:
        Sorted list of manufacturer names
    """
    if not PV_MOUNTING_DB_AVAILABLE:
        return []
    
    try:
        components = get_pv_mounting_components_by_category(category)
        manufacturers = sorted(set(c['manufacturer'] for c in components if c.get('manufacturer')))
        return manufacturers
    except Exception:
        return []


def get_pv_mounting_component_names_by_manufacturer(
    category: str,
    manufacturer: str,
    roof_type: Optional[str] = None
) -> List[str]:
    """
    Get list of component names for a specific manufacturer and category.
    
    Args:
        category: Component category
        manufacturer: Manufacturer name
        roof_type: Optional roof type filter
        
    Returns:
        Sorted list of component names (from 'product_name' field)
    """
    if not PV_MOUNTING_DB_AVAILABLE:
        return []
    
    try:
        components = get_pv_mounting_components_by_category(
            category,
            manufacturer=manufacturer,
            roof_type=roof_type
        )
        names = sorted(c['product_name'] for c in components if c.get('product_name'))
        return names
    except Exception:
        return []


def get_pv_mounting_roof_types() -> List[str]:
    """
    Get list of all available roof types in database.
    
    Returns:
        Sorted list of roof type names
    """
    if not PV_MOUNTING_DB_AVAILABLE:
        return []
    
    try:
        initialize_database()
        components = read_components()
        roof_types = sorted(set(c['roof_type'] for c in components if c.get('roof_type')))
        return roof_types
    except Exception:
        return []


def get_pv_mounting_categories() -> List[str]:
    """
    Get list of all available component categories in database.
    
    Returns:
        Sorted list of category names
    """
    if not PV_MOUNTING_DB_AVAILABLE:
        return []
    
    try:
        initialize_database()
        components = read_components()
        categories = sorted(set(c['category'] for c in components if c.get('category')))
        return categories
    except Exception:
        return []


# Category-specific convenience functions for Solar Calculator
def get_roof_hooks(manufacturer: Optional[str] = None, roof_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all roof hooks (Dachhaken) with optional filters."""
    return get_pv_mounting_components_by_category("Dachhaken", manufacturer, roof_type)


def get_mounting_rails(manufacturer: Optional[str] = None, roof_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all mounting rails (Montageschiene) with optional filters."""
    return get_pv_mounting_components_by_category("Montageschiene", manufacturer, roof_type)


def get_end_clamps(manufacturer: Optional[str] = None, roof_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all end clamps (Modulklemme End) with optional filters."""
    return get_pv_mounting_components_by_category("Modulklemme (End)", manufacturer, roof_type)


def get_mid_clamps(manufacturer: Optional[str] = None, roof_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all mid clamps (Modulklemme Mittel) with optional filters."""
    return get_pv_mounting_components_by_category("Modulklemme (Mittel)", manufacturer, roof_type)


def get_screws(manufacturer: Optional[str] = None, roof_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all screws (Schrauben) with optional filters."""
    return get_pv_mounting_components_by_category("Schrauben", manufacturer, roof_type)


def get_cables(manufacturer: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all cables (Kabel) with optional filters."""
    return get_pv_mounting_components_by_category("Kabel", manufacturer)


def get_pv_mounting_component_price(component_name: str) -> float:
    """
    Get price of a component by name.
    
    Args:
        component_name: Name of component
        
    Returns:
        Price in EUR (netto) or 0.0 if not found
    """
    component = get_pv_mounting_component_by_name(component_name)
    if component and component.get('price_netto'):
        return float(component['price_netto'])
    return 0.0


def get_pv_mounting_component_unit(component_name: str) -> str:
    """
    Get unit of a component by name.
    
    Args:
        component_name: Name of component
        
    Returns:
        Unit string (e.g., "Stk", "m") or "Stk" as default
    """
    component = get_pv_mounting_component_by_name(component_name)
    if component and component.get('unit'):
        return component['unit']
    return "Stk"


def get_pv_mounting_component_pdf(component_name: str) -> Optional[bytes]:
    """
    Get PDF datasheet bytes of a component by name.
    
    Args:
        component_name: Name of component
        
    Returns:
        PDF bytes or None if not available
    """
    component = get_pv_mounting_component_by_name(component_name)
    if component and component.get('pdf_bytes'):
        return component['pdf_bytes']
    return None


# === Testing ===
if __name__ == "__main__":
    print("=== PV Mounting DB Bridge Test ===")
    print()
    
    if not PV_MOUNTING_DB_AVAILABLE:
        print("[ERROR] Database not available!")
    else:
        print("[OK] Database available")
        print()
        
        # Test categories
        print("[PACKAGE] Available Categories:")
        categories = get_pv_mounting_categories()
        for cat in categories:
            print(f"  - {cat}")
        print()
        
        # Test manufacturers
        print("🏭 Manufacturers for 'Dachhaken':")
        manufacturers = get_pv_mounting_manufacturers_by_category("Dachhaken")
        for manuf in manufacturers:
            print(f"  - {manuf}")
        print()
        
        # Test roof hooks
        print("[BUILD] Roof Hooks by K2 Systems:")
        hooks = get_roof_hooks(manufacturer="K2 Systems")
        for hook in hooks:
            # Handle both dict and Row objects
            name = hook.get('name') if hasattr(hook, 'get') else hook['name'] if 'name' in dir(hook) else str(hook)
            price = hook.get('price_netto', 0.0) if hasattr(hook, 'get') else getattr(hook, 'price_netto', 0.0)
            print(f"  - {name}: {price:.2f} EUR")
        print()
        
        # Test component lookup
        if hooks:
            test_name = hooks[0]['name']
            print(f"[SEARCH] Component lookup: '{test_name}'")
            component = get_pv_mounting_component_by_name(test_name)
            if component:
                print(f"  [OK] Found:")
                print(f"     Price: {component['price_netto']:.2f} EUR")
                print(f"     Unit: {component.get('unit', 'N/A')}")
                print(f"     Roof Type: {component.get('roof_type', 'N/A')}")
                print(f"     PDF available: {'Yes' if component.get('pdf_bytes') else 'No'}")
        
        print()
        print("=== Test Complete ===")
