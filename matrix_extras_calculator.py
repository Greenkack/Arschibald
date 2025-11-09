"""matrix_extras_calculator.py

Berechnung von Zusatzkosten für Sonderprodukte, Extras und Dienstleistungen
im Preismatrix-Modus.

Im Preismatrix-Modus enthält der Basispreis bereits:
- PV-Module
- Wechselrichter
- Batteriespeicher
- Standard-Montage
- Standard-Installation

Zusätzlich berechnet werden:
- Sonderprodukte (markiert mit is_special_product = 1)
- Zusätzliche Dienstleistungen
- Extras und Sonderwünsche
- Rabatte und Aufpreise
"""

from typing import Any, Optional
import special_products


def calculate_special_products_cost(details: dict[str, Any]) -> dict[str, Any]:
    """
    Berechnet die Kosten für Sonderprodukte.
    
    Sonderprodukte sind Produkte, die mit is_special_product = 1 markiert sind
    und zusätzlich zum Preismatrix-Basispreis berechnet werden.
    
    Args:
        details: Project details mit ausgewählten Produkten
        
    Returns:
        Dictionary mit:
        {
            'total': float,
            'items': list[dict],
            'count': int
        }
    """
    result = {
        'total': 0.0,
        'items': [],
        'count': 0
    }
    
    # Sammle alle ausgewählten Produkte aus details
    selected_products = []
    
    # PV-Module (normalerweise Standardprodukt, aber könnte Sondermodule geben)
    if 'selected_module_name' in details and details.get('selected_module_name'):
        module_name = details['selected_module_name']
        if special_products.is_special_product_by_name(module_name):
            module_price = details.get('module_price', 0.0)
            module_quantity = details.get('module_quantity', 0)
            total_price = module_price * module_quantity
            
            result['items'].append({
                'name': f"Sondermodul: {module_name}",
                'category': 'PV-Module',
                'unit_price': module_price,
                'quantity': module_quantity,
                'price': total_price
            })
            result['total'] += total_price
            result['count'] += 1
    
    # Wechselrichter (normalerweise Standardprodukt)
    if 'selected_inverter_name' in details and details.get('selected_inverter_name'):
        inverter_name = details['selected_inverter_name']
        if special_products.is_special_product_by_name(inverter_name):
            inverter_price = details.get('inverter_price', 0.0)
            
            result['items'].append({
                'name': f"Sonderwechselrichter: {inverter_name}",
                'category': 'Wechselrichter',
                'unit_price': inverter_price,
                'quantity': 1,
                'price': inverter_price
            })
            result['total'] += inverter_price
            result['count'] += 1
    
    # Batteriespeicher (normalerweise Standardprodukt)
    if 'selected_storage_name' in details and details.get('selected_storage_name'):
        storage_name = details['selected_storage_name']
        # Prüfe ob es ein Platzhalter-Text ist
        if storage_name and not ('bitte' in storage_name.lower() or 'select' in storage_name.lower()):
            if special_products.is_special_product_by_name(storage_name):
                storage_price = details.get('storage_price', 0.0)
                
                result['items'].append({
                    'name': f"Sonderspeicher: {storage_name}",
                    'category': 'Batteriespeicher',
                    'unit_price': storage_price,
                    'quantity': 1,
                    'price': storage_price
                })
                result['total'] += storage_price
                result['count'] += 1
    
    # Zusätzliche Komponenten (z.B. Optimierer, Monitoring, etc.)
    if 'additional_components' in details and isinstance(details['additional_components'], list):
        for component in details['additional_components']:
            if isinstance(component, dict):
                component_name = component.get('name', '')
                component_id = component.get('id')
                
                # Prüfe ob Sonderprodukt
                is_special = False
                if component_id:
                    is_special = special_products.is_special_product(component_id)
                elif component_name:
                    is_special = special_products.is_special_product_by_name(component_name)
                
                if is_special:
                    component_price = component.get('price', 0.0)
                    component_quantity = component.get('quantity', 1)
                    total_price = component_price * component_quantity
                    
                    result['items'].append({
                        'name': component_name,
                        'category': component.get('category', 'Zusatzkomponente'),
                        'unit_price': component_price,
                        'quantity': component_quantity,
                        'price': total_price
                    })
                    result['total'] += total_price
                    result['count'] += 1
    
    return result


def calculate_services_cost(details: dict[str, Any]) -> dict[str, Any]:
    """
    Berechnet die Kosten für zusätzliche Dienstleistungen.
    
    Im Preismatrix-Modus werden nur explizit ausgewählte zusätzliche
    Dienstleistungen berechnet. Standard-Dienstleistungen sind im
    Basispreis enthalten.
    
    Args:
        details: Project details mit ausgewählten Services
        
    Returns:
        Dictionary mit:
        {
            'total': float,
            'items': list[dict],
            'count': int
        }
    """
    result = {
        'total': 0.0,
        'items': [],
        'count': 0
    }
    
    try:
        from services_integration import get_selected_services_total, calculate_services_pricing
        
        # Hole ausgewählte Services aus Session State
        import streamlit as st
        if hasattr(st, 'session_state'):
            selected_services = st.session_state.get('selected_optional_services', [])
            
            if selected_services:
                # Berechne Service-Preise
                services_result = calculate_services_pricing(selected_services, details)
                
                # Nur optionale Services (Standard-Services sind im Basispreis)
                if 'optional_details' in services_result:
                    for service in services_result['optional_details']:
                        result['items'].append({
                            'name': service.get('name', 'Unbekannter Service'),
                            'category': 'Dienstleistung',
                            'unit_price': service.get('price', 0.0),
                            'quantity': service.get('quantity', 1),
                            'price': service.get('total_price', 0.0),
                            'description': service.get('description', '')
                        })
                        result['total'] += service.get('total_price', 0.0)
                        result['count'] += 1
                
                # Fallback: Verwende Gesamt-Optional-Preis
                elif 'total_optional' in services_result:
                    total_optional = services_result['total_optional']
                    if total_optional > 0:
                        result['items'].append({
                            'name': 'Zusätzliche Dienstleistungen',
                            'category': 'Dienstleistung',
                            'unit_price': total_optional,
                            'quantity': 1,
                            'price': total_optional
                        })
                        result['total'] = total_optional
                        result['count'] = 1
    
    except ImportError:
        # Services-Integration nicht verfügbar
        pass
    except Exception as e:
        print(f"Fehler bei calculate_services_cost: {e}")
    
    return result


def calculate_extras_cost(details: dict[str, Any]) -> dict[str, Any]:
    """
    Berechnet die Kosten für Extras und Sonderwünsche.
    
    Extras sind zusätzliche Positionen, die nicht in der Produktdatenbank
    sind, aber vom Benutzer hinzugefügt wurden.
    
    Args:
        details: Project details mit Extras
        
    Returns:
        Dictionary mit:
        {
            'total': float,
            'items': list[dict],
            'count': int
        }
    """
    result = {
        'total': 0.0,
        'items': [],
        'count': 0
    }
    
    # Extras aus details
    if 'additional_extras' in details and isinstance(details['additional_extras'], list):
        for extra in details['additional_extras']:
            if isinstance(extra, dict) and 'price' in extra:
                extra_price = float(extra.get('price', 0))
                extra_quantity = extra.get('quantity', 1)
                total_price = extra_price * extra_quantity
                
                result['items'].append({
                    'name': extra.get('name', 'Zusätzliches Extra'),
                    'category': 'Extra',
                    'unit_price': extra_price,
                    'quantity': extra_quantity,
                    'price': total_price,
                    'description': extra.get('description', '')
                })
                result['total'] += total_price
                result['count'] += 1
    
    # Custom items aus Session State
    try:
        import streamlit as st
        if hasattr(st, 'session_state'):
            custom_items = st.session_state.get('custom_price_items', [])
            for item in custom_items:
                if isinstance(item, dict) and 'price' in item:
                    item_price = float(item.get('price', 0))
                    item_quantity = item.get('quantity', 1)
                    total_price = item_price * item_quantity
                    
                    result['items'].append({
                        'name': item.get('name', 'Benutzerdefinierte Position'),
                        'category': 'Sonderwunsch',
                        'unit_price': item_price,
                        'quantity': item_quantity,
                        'price': total_price,
                        'description': item.get('description', '')
                    })
                    result['total'] += total_price
                    result['count'] += 1
    except Exception as e:
        print(f"Fehler bei Extras aus Session State: {e}")
    
    return result


def apply_discounts_and_surcharges(
    base_amount: float,
    details: dict[str, Any]
) -> dict[str, Any]:
    """
    Wendet Rabatte und Aufpreise auf einen Betrag an.
    
    Args:
        base_amount: Basisbetrag vor Rabatten/Aufpreisen
        details: Project details mit Rabatt/Aufpreis-Informationen
        
    Returns:
        Dictionary mit:
        {
            'base_amount': float,
            'discount_amount': float,
            'discount_percent': float,
            'surcharge_amount': float,
            'surcharge_percent': float,
            'final_amount': float,
            'items': list[dict]  # Details zu Rabatten/Aufpreisen
        }
    """
    result = {
        'base_amount': base_amount,
        'discount_amount': 0.0,
        'discount_percent': 0.0,
        'surcharge_amount': 0.0,
        'surcharge_percent': 0.0,
        'final_amount': base_amount,
        'items': []
    }
    
    current_amount = base_amount
    
    # Rabatte
    if 'discount_percent' in details and details['discount_percent']:
        discount_percent = float(details['discount_percent'])
        if discount_percent > 0:
            discount_amount = current_amount * (discount_percent / 100)
            current_amount -= discount_amount
            
            result['discount_percent'] = discount_percent
            result['discount_amount'] = discount_amount
            result['items'].append({
                'type': 'discount',
                'name': f'Rabatt ({discount_percent}%)',
                'amount': -discount_amount
            })
    
    if 'discount_amount' in details and details['discount_amount']:
        discount_amount = float(details['discount_amount'])
        if discount_amount > 0:
            current_amount -= discount_amount
            
            result['discount_amount'] += discount_amount
            result['items'].append({
                'type': 'discount',
                'name': 'Rabatt (Festbetrag)',
                'amount': -discount_amount
            })
    
    # Aufpreise
    if 'surcharge_percent' in details and details['surcharge_percent']:
        surcharge_percent = float(details['surcharge_percent'])
        if surcharge_percent > 0:
            surcharge_amount = current_amount * (surcharge_percent / 100)
            current_amount += surcharge_amount
            
            result['surcharge_percent'] = surcharge_percent
            result['surcharge_amount'] = surcharge_amount
            result['items'].append({
                'type': 'surcharge',
                'name': f'Aufpreis ({surcharge_percent}%)',
                'amount': surcharge_amount
            })
    
    if 'surcharge_amount' in details and details['surcharge_amount']:
        surcharge_amount = float(details['surcharge_amount'])
        if surcharge_amount > 0:
            current_amount += surcharge_amount
            
            result['surcharge_amount'] += surcharge_amount
            result['items'].append({
                'type': 'surcharge',
                'name': 'Aufpreis (Festbetrag)',
                'amount': surcharge_amount
            })
    
    result['final_amount'] = current_amount
    
    return result


def calculate_all_extras(details: dict[str, Any]) -> dict[str, Any]:
    """
    Berechnet alle Zusatzkosten für den Preismatrix-Modus.
    
    Diese Funktion kombiniert:
    - Sonderprodukte
    - Zusätzliche Dienstleistungen
    - Extras und Sonderwünsche
    
    Args:
        details: Project details
        
    Returns:
        Dictionary mit vollständiger Aufschlüsselung:
        {
            'total': float,
            'special_products': dict,
            'services': dict,
            'extras': dict,
            'breakdown': list[dict]
        }
    """
    # Berechne einzelne Kategorien
    special_products_result = calculate_special_products_cost(details)
    services_result = calculate_services_cost(details)
    extras_result = calculate_extras_cost(details)
    
    # Gesamtsumme
    total = (
        special_products_result['total'] +
        services_result['total'] +
        extras_result['total']
    )
    
    # Erstelle Breakdown für UI-Anzeige
    breakdown = []
    
    # Sonderprodukte
    for item in special_products_result['items']:
        breakdown.append({
            'category': 'Sonderprodukt',
            'name': item['name'],
            'quantity': item['quantity'],
            'unit_price': item['unit_price'],
            'total_price': item['price']
        })
    
    # Dienstleistungen
    for item in services_result['items']:
        breakdown.append({
            'category': 'Dienstleistung',
            'name': item['name'],
            'quantity': item.get('quantity', 1),
            'unit_price': item.get('unit_price', item['price']),
            'total_price': item['price'],
            'description': item.get('description', '')
        })
    
    # Extras
    for item in extras_result['items']:
        breakdown.append({
            'category': 'Extra',
            'name': item['name'],
            'quantity': item['quantity'],
            'unit_price': item['unit_price'],
            'total_price': item['price'],
            'description': item.get('description', '')
        })
    
    return {
        'total': total,
        'special_products': special_products_result,
        'services': services_result,
        'extras': extras_result,
        'breakdown': breakdown
    }


__all__ = [
    'calculate_special_products_cost',
    'calculate_services_cost',
    'calculate_extras_cost',
    'apply_discounts_and_surcharges',
    'calculate_all_extras'
]
