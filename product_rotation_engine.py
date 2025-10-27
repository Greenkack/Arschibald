"""
Produkt-Rotations-Engine für Multi-PDF Angebotserstellung

Diese Engine sorgt dafür, dass jede Firma automatisch andere Marken bekommt
als das Standard-Angebot und die vorherigen Firmen.

Logik:
- Standard wählt Marke A → Firma 1 wählt Marke B → Firma 2 wählt Marke C
- Gleiche Spezifikationen beibehalten (±10% Toleranz)
- Bei Marken-Erschöpfung: Duplikate erlaubt, aber andere Modelle bevorzugt
- WR + Speicher: Gleiche Marke bevorzugt wenn beide verfügbar
"""

import streamlit as st
from typing import Dict, Set, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


def load_all_products() -> Dict[str, List[dict]]:
    """
    Lade alle Produkte aus der Datenbank oder Session State
    
    Returns:
        {
            'pv_modules': [...],
            'inverters': [...],
            'battery_storage': [...]
        }
    """
    products = {
        'pv_modules': [],
        'inverters': [],
        'battery_storage': []
    }
    
    # 1. PRIMÄR: Lade aus Produktdatenbank-Modul
    try:
        import product_db  # ← RICHTIGER Modulname!
        logger.info(f"✅ product_db Modul importiert")
        
        if hasattr(product_db, 'list_products'):
            logger.info(f"✅ list_products() Funktion gefunden")
            
            if callable(product_db.list_products):
                logger.info(f"🔍 Rufe list_products() für alle Kategorien auf...")
                
                # ⚠️ WICHTIG: Die Datenbank nutzt DEUTSCHE Kategorienamen!
                # list_products(category) gibt Liste für EINE Kategorie zurück!
                pv_modules_raw = product_db.list_products(category='Modul') or []
                inverters_raw = product_db.list_products(category='Wechselrichter') or []
                battery_raw = product_db.list_products(category='Batteriespeicher') or []
                
                # Konvertiere zu einheitlichem Format (mit brand, model, etc.)
                products['pv_modules'] = [
                    {
                        'brand': p.get('manufacturer', p.get('brand', '')),
                        'model': p.get('model_name', p.get('name', '')),
                        'model_name': p.get('model_name', p.get('name', '')),
                        'name': p.get('name', p.get('model_name', '')),
                        'manufacturer': p.get('manufacturer', p.get('brand', '')),
                        'power_w': p.get('power_wp', p.get('capacity_w', 0)),
                        'capacity_w': p.get('capacity_w', p.get('power_wp', 0)),
                        'power_wp': p.get('power_wp', p.get('capacity_w', 0)),
                        'id': p.get('id'),
                        'price': p.get('price', 0)
                    }
                    for p in pv_modules_raw
                ]
                
                products['inverters'] = [
                    {
                        'brand': p.get('manufacturer', p.get('brand', '')),
                        'model': p.get('model_name', p.get('name', '')),
                        'model_name': p.get('model_name', p.get('name', '')),
                        'name': p.get('name', p.get('model_name', '')),
                        'manufacturer': p.get('manufacturer', p.get('brand', '')),
                        'power_kw': p.get('power_kw', 0),
                        'id': p.get('id'),
                        'price': p.get('price', 0)
                    }
                    for p in inverters_raw
                ]
                
                products['battery_storage'] = [
                    {
                        'brand': p.get('manufacturer', p.get('brand', '')),
                        'model': p.get('model_name', p.get('name', '')),
                        'model_name': p.get('model_name', p.get('name', '')),
                        'name': p.get('name', p.get('model_name', '')),
                        'manufacturer': p.get('manufacturer', p.get('brand', '')),
                        'capacity_kwh': p.get('capacity_kwh', 0),
                        'id': p.get('id'),
                        'price': p.get('price', 0)
                    }
                    for p in battery_raw
                ]
                
                total = sum(len(p) for p in products.values())
                if total > 0:
                    logger.info(f"✅ Produkte aus Datenbank geladen: {total} gesamt (PV={len(products['pv_modules'])}, INV={len(products['inverters'])}, BAT={len(products['battery_storage'])})")
                    return products
                else:
                    logger.warning("⚠️ Produktdatenbank ist LEER!")
            else:
                logger.warning("⚠️ list_products ist NICHT callable")
        else:
            logger.warning("⚠️ list_products() Funktion NICHT gefunden in product_db")
    except Exception as e:
        logger.error(f"❌ Produktdatenbank konnte nicht geladen werden: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # 2. FALLBACK: Session State
    try:
        # Versuche aus Session State zu laden (wenn in Streamlit)
        import streamlit as st
        
        if hasattr(st, 'session_state'):
            # DEBUG: Zeige Session State Keys
            logger.info(f"Session State Keys verfügbar: {list(st.session_state.keys())}")
            
            # Lade aus Session State Product Lists
            products['pv_modules'] = st.session_state.get('pv_modules_list', [])
            products['inverters'] = st.session_state.get('inverters_list', [])
            products['battery_storage'] = st.session_state.get('battery_storage_list', [])
            
            logger.info(f"Geladene Produkte: PV={len(products['pv_modules'])}, INV={len(products['inverters'])}, BAT={len(products['battery_storage'])}")
            
            if any(products.values()):
                logger.info(f"Produkte aus Session State geladen: {sum(len(p) for p in products.values())} gesamt")
                return products
            else:
                logger.warning("Session State hat KEINE Produkte in pv_modules_list/inverters_list/battery_storage_list!")
                return products
    except Exception as e:
        logger.debug(f"Session State nicht verfügbar: {e}")
    
    return products


@dataclass
class ProductSpecs:
    """Produkt-Spezifikationen für Matching"""
    power_w: Optional[float] = None  # PV Module Leistung in W
    power_kw: Optional[float] = None  # Wechselrichter Leistung in kW
    capacity_kwh: Optional[float] = None  # Batteriespeicher Kapazität in kWh
    tolerance: float = 0.1  # ±10% Toleranz


def get_available_brands(category: str, exclude_brands: Set[str] = None) -> List[str]:
    """
    Hole alle verfügbaren Marken aus Produktdatenbank für eine Kategorie
    
    Args:
        category: 'pv_modules', 'inverters', 'battery_storage'
        exclude_brands: Marken, die ausgeschlossen werden sollen
    
    Returns:
        Liste von Marken-Namen
    """
    # load_all_products() ist bereits in DIESEM Modul definiert (Zeile 22)!
    # KEIN Import notwendig!
    
    exclude_brands = exclude_brands or set()
    
    # Lade alle Produkte aus Datenbank
    all_products = load_all_products()
    
    if category not in all_products:
        logger.warning(f"Kategorie {category} nicht in Produktdatenbank gefunden")
        return []
    
    # Extrahiere eindeutige Marken
    brands = set()
    for product in all_products[category]:
        brand = product.get('brand') or product.get('Marke')
        if brand and brand not in exclude_brands:
            brands.add(brand)
    
    brands_list = sorted(list(brands))
    logger.info(f"Gefundene Marken für {category}: {brands_list}")
    
    return brands_list


def get_product_by_specs(
    category: str, 
    brand: str, 
    specs: ProductSpecs,
    used_models: Set[str] = None
) -> Optional[dict]:
    """
    Finde Produkt mit passenden Specs (±10% Toleranz)
    
    Args:
        category: Produktkategorie
        brand: Marke, die verwendet werden soll
        specs: Ziel-Spezifikationen
        used_models: Bereits verwendete Produktmodelle (zur Vermeidung von Duplikaten)
    
    Returns:
        Produkt-Dict oder None
    """
    # load_all_products() ist bereits in DIESEM Modul definiert!
    
    used_models = used_models or set()
    
    all_products = load_all_products()
    
    if category not in all_products:
        return None
    
    # Filtere nach Marke
    brand_products = [p for p in all_products[category] 
                      if (p.get('brand') or p.get('Marke')) == brand]
    
    if not brand_products:
        logger.warning(f"Keine Produkte für Marke {brand} in {category}")
        return None
    
    # Finde passendes Produkt nach Specs
    for product in brand_products:
        model = product.get('model') or product.get('Modell')
        
        # Überspringe bereits verwendete Modelle
        if model in used_models:
            continue
        
        # PV Module: Leistung in W
        if category == 'pv_modules' and specs.power_w:
            product_power = product.get('power_w') or product.get('Leistung_W')
            if product_power:
                min_power = specs.power_w * (1 - specs.tolerance)
                max_power = specs.power_w * (1 + specs.tolerance)
                if min_power <= product_power <= max_power:
                    logger.info(f"Gefunden: {brand} {model} mit {product_power}W (Ziel: {specs.power_w}W)")
                    return product
        
        # Wechselrichter: Leistung in kW
        elif category == 'inverters' and specs.power_kw:
            product_power = product.get('power_kw') or product.get('Leistung_kW')
            if product_power:
                min_power = specs.power_kw * (1 - specs.tolerance)
                max_power = specs.power_kw * (1 + specs.tolerance)
                if min_power <= product_power <= max_power:
                    logger.info(f"Gefunden: {brand} {model} mit {product_power}kW (Ziel: {specs.power_kw}kW)")
                    return product
        
        # Batteriespeicher: Kapazität in kWh
        elif category == 'battery_storage' and specs.capacity_kwh:
            product_capacity = product.get('capacity_kwh') or product.get('Kapazität_kWh')
            if product_capacity:
                min_capacity = specs.capacity_kwh * (1 - specs.tolerance)
                max_capacity = specs.capacity_kwh * (1 + specs.tolerance)
                if min_capacity <= product_capacity <= max_capacity:
                    logger.info(f"Gefunden: {brand} {model} mit {product_capacity}kWh (Ziel: {specs.capacity_kwh}kWh)")
                    return product
    
    # Kein passendes Produkt gefunden - nehme erstes verfügbares
    logger.warning(f"Kein exaktes Match für {brand} in {category}, nehme erstes verfügbares")
    return brand_products[0] if brand_products else None


def find_matching_brands_for_inverter_and_battery(
    used_brands: Set[str],
    inverter_specs: ProductSpecs,
    battery_specs: ProductSpecs
) -> Tuple[Optional[str], Optional[str]]:
    """
    Versuche Marke zu finden, die sowohl Wechselrichter als auch Batteriespeicher hat
    
    Returns:
        (inverter_brand, battery_brand) oder (None, None)
    """
    inverter_brands = get_available_brands('inverters', used_brands)
    battery_brands = get_available_brands('battery_storage', used_brands)
    
    # Finde gemeinsame Marken
    common_brands = set(inverter_brands) & set(battery_brands)
    
    if not common_brands:
        return None, None
    
    # Prüfe ob Marke passende Produkte hat
    for brand in common_brands:
        inverter = get_product_by_specs('inverters', brand, inverter_specs)
        battery = get_product_by_specs('battery_storage', brand, battery_specs)
        
        if inverter and battery:
            logger.info(f"Gemeinsame Marke gefunden: {brand} (WR + Speicher)")
            return brand, brand
    
    return None, None


def rotate_products(
    standard_products: Dict[str, dict],
    used_brands: Set[str],
    firm_index: int = 0,
    used_models: Dict[str, Set[str]] = None
) -> Dict[str, dict]:
    """
    Hauptfunktion: Rotiere Produkte für eine Firma
    
    Args:
        standard_products: {category: product_dict} vom Standard-Angebot
        used_brands: Set von bereits verwendeten Marken (für alle Kategorien)
        firm_index: Index der Firma (0-basiert)
        used_models: {category: set(model_names)} - bereits verwendete Modelle
    
    Returns:
        {category: rotated_product_dict} - Rotierte Produkte für diese Firma
    """
    used_models = used_models or {}
    rotated = {}
    
    logger.info(f"=== Produkt-Rotation für Firma {firm_index + 1} ===")
    logger.info(f"Verwendete Marken bisher: {used_brands}")
    
    # Extrahiere Specs aus Standard-Produkten
    specs = {}
    
    # PV Module Specs
    if 'pv_modules' in standard_products:
        pv = standard_products['pv_modules']
        if pv is not None:  # ⬅️ ABSICHERUNG gegen None!
            power_w = pv.get('power_w') or pv.get('Leistung_W')
            specs['pv_modules'] = ProductSpecs(power_w=power_w)
            logger.info(f"PV Module Ziel-Specs: {power_w}W")
        else:
            logger.warning("PV Module ist None - wird nicht rotiert")
    
    # Wechselrichter Specs
    if 'inverters' in standard_products:
        inv = standard_products['inverters']
        if inv is not None:  # ⬅️ ABSICHERUNG gegen None!
            power_kw = inv.get('power_kw') or inv.get('Leistung_kW')
            specs['inverters'] = ProductSpecs(power_kw=power_kw)
            logger.info(f"Wechselrichter Ziel-Specs: {power_kw}kW")
        else:
            logger.warning("Wechselrichter ist None - wird nicht rotiert")
    
    # Batteriespeicher Specs
    if 'battery_storage' in standard_products:
        bat = standard_products['battery_storage']
        if bat is not None:  # ⬅️ ABSICHERUNG gegen None!
            capacity_kwh = bat.get('capacity_kwh') or bat.get('Kapazität_kWh')
            specs['battery_storage'] = ProductSpecs(capacity_kwh=capacity_kwh)
            logger.info(f"Batteriespeicher Ziel-Specs: {capacity_kwh}kWh")
        else:
            logger.warning("Batteriespeicher ist None - wird nicht rotiert")
    
    # Schritt 1: Versuche gemeinsame Marke für WR + Speicher zu finden
    inverter_brand = None
    battery_brand = None
    
    if 'inverters' in specs and 'battery_storage' in specs:
        inverter_brand, battery_brand = find_matching_brands_for_inverter_and_battery(
            used_brands, specs['inverters'], specs['battery_storage']
        )
    
    # Schritt 2: Rotiere PV Module
    if 'pv_modules' in specs:
        available_brands = get_available_brands('pv_modules', used_brands)
        
        if not available_brands:
            # Marken erschöpft - erlaube Duplikate
            logger.warning("PV Module Marken erschöpft - erlaube Duplikate")
            available_brands = get_available_brands('pv_modules')
        
        if available_brands:
            pv_brand = available_brands[0]
            pv_product = get_product_by_specs(
                'pv_modules', 
                pv_brand, 
                specs['pv_modules'],
                used_models.get('pv_modules', set())
            )
            
            if pv_product:
                rotated['pv_modules'] = pv_product
                logger.info(f"✓ PV Module: {pv_brand}")
    
    # Schritt 3: Rotiere Wechselrichter
    if 'inverters' in specs:
        if not inverter_brand:
            # Keine gemeinsame Marke - wähle separate Marke
            available_brands = get_available_brands('inverters', used_brands)
            
            if not available_brands:
                logger.warning("Wechselrichter Marken erschöpft - erlaube Duplikate")
                available_brands = get_available_brands('inverters')
            
            if available_brands:
                inverter_brand = available_brands[0]
        
        if inverter_brand:
            inv_product = get_product_by_specs(
                'inverters',
                inverter_brand,
                specs['inverters'],
                used_models.get('inverters', set())
            )
            
            if inv_product:
                rotated['inverters'] = inv_product
                logger.info(f"✓ Wechselrichter: {inverter_brand}")
    
    # Schritt 4: Rotiere Batteriespeicher
    if 'battery_storage' in specs:
        if not battery_brand:
            # Prüfe ob WR-Marke auch Speicher hat
            if inverter_brand:
                bat_product = get_product_by_specs(
                    'battery_storage',
                    inverter_brand,
                    specs['battery_storage'],
                    used_models.get('battery_storage', set())
                )
                if bat_product:
                    battery_brand = inverter_brand
                    logger.info(f"Batteriespeicher nutzt gleiche Marke wie WR: {battery_brand}")
            
            # Sonst separate Marke
            if not battery_brand:
                available_brands = get_available_brands('battery_storage', used_brands)
                
                if not available_brands:
                    logger.warning("Batteriespeicher Marken erschöpft - erlaube Duplikate")
                    available_brands = get_available_brands('battery_storage')
                
                if available_brands:
                    battery_brand = available_brands[0]
        
        if battery_brand:
            bat_product = get_product_by_specs(
                'battery_storage',
                battery_brand,
                specs['battery_storage'],
                used_models.get('battery_storage', set())
            )
            
            if bat_product:
                rotated['battery_storage'] = bat_product
                logger.info(f"✓ Batteriespeicher: {battery_brand}")
    
    logger.info(f"=== Rotation abgeschlossen: {len(rotated)} Produkte ===")
    
    return rotated


def track_used_brands(products: Dict[str, dict]) -> Set[str]:
    """
    Extrahiere verwendete Marken aus Produkt-Dict
    
    Args:
        products: {category: product_dict}
    
    Returns:
        Set von Marken-Namen
    """
    brands = set()
    
    for category, product in products.items():
        if product:
            brand = product.get('brand') or product.get('Marke')
            if brand:
                brands.add(brand)
    
    return brands


def track_used_models(products: Dict[str, dict]) -> Dict[str, Set[str]]:
    """
    Extrahiere verwendete Modelle pro Kategorie
    
    Args:
        products: {category: product_dict}
    
    Returns:
        {category: set(model_names)}
    """
    models = {}
    
    for category, product in products.items():
        if product:
            model = product.get('model') or product.get('Modell')
            if model:
                if category not in models:
                    models[category] = set()
                models[category].add(model)
    
    return models
