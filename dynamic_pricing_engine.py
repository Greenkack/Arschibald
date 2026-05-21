"""
dynamic_pricing_engine.py

Dynamische Preisberechnung für alle Komponenten:
- PV Module, Wechselrichter, Batteriespeicher
- Dienstleistungen und Services
- Rabatte und Aufpreise
- Zubehör und Sonstiges
"""

import json
from datetime import datetime
from typing import Any

import streamlit as st


def _safe_float_conversion(price_string: str) -> float:
    """
    Safely convert German formatted price strings to float
    Handles formats like: '2.900,00 €', '1.234.567,89 €', '123,45 €'
    """
    if not price_string:
        return 0.0

    try:
        # Remove currency symbol and spaces
        clean_string = price_string.replace('€', '').replace(' ', '').strip()

        # Handle German number format (dots as thousand separators, comma as
        # decimal)
        if ',' in clean_string:
            # Split at comma to separate decimal part
            parts = clean_string.split(',')
            if len(parts) == 2:
                # Remove dots from integer part (thousand separators)
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1]
                # Reconstruct as English format
                clean_string = f"{integer_part}.{decimal_part}"
            else:
                # No decimal part, just remove dots
                clean_string = clean_string.replace('.', '')
        else:
            # No comma, check if dots are thousand separators or decimal
            dot_count = clean_string.count('.')
            if dot_count > 1:
                # Multiple dots = thousand separators, remove all
                clean_string = clean_string.replace('.', '')
            elif dot_count == 1:
                # Single dot could be decimal or thousand separator
                parts = clean_string.split('.')
                if len(parts) == 2:
                    # In German format, if there's no comma and a single dot:
                    # - If exactly 3 digits after dot OR more than 3 digits after dot: thousand separator
                    # - If 1-2 digits after dot: could be decimal, but in German context likely thousand separator
                    # Since we're dealing with prices in Euro context, assume
                    # thousand separator unless clearly decimal
                    if len(parts[1]) == 3 or len(parts[1]) > 3:
                        # Definitely thousand separator
                        clean_string = clean_string.replace('.', '')
                    elif len(parts[1]) <= 2 and int(parts[0]) >= 100:
                        # Likely thousand separator for larger amounts (e.g.,
                        # 1.500 = 1500, not 1.5)
                        clean_string = clean_string.replace('.', '')
                    # For small amounts with 1-2 decimal places, keep as
                    # decimal (e.g., 1.5 = 1.5)

        return float(clean_string)

    except (ValueError, AttributeError) as e:
        print(
            f"Warning: Could not convert price string '{price_string}' to float: {e}")
        return 0.0


def calculate_dynamic_total_price(
        project_details: dict[str, Any]) -> dict[str, Any]:
    """
    Berechnet den dynamischen Gesamtpreis aus allen Komponenten

    Returns:
        Dict mit allen Preiskomponenten und Gesamtsumme
    """

    pricing_result = {
        'components': {},
        'categories': {},
        'totals': {},
        'breakdown': {},
        'metadata': {
            'calculation_timestamp': datetime.now().isoformat(),
            'project_details_hash': str(hash(str(project_details))),
            'version': '1.0'
        }
    }

    try:
        # 1. Hardware-Komponenten (PV, Wechselrichter, Batterien)
        hardware_pricing = calculate_hardware_pricing(project_details)
        pricing_result['components']['hardware'] = hardware_pricing

        # 2. Services und Dienstleistungen
        services_pricing = calculate_services_pricing_dynamic(project_details)
        pricing_result['components']['services'] = services_pricing

        # 3. Zubehör und Zusatzkomponenten
        accessories_pricing = calculate_accessories_pricing(project_details)
        pricing_result['components']['accessories'] = accessories_pricing

        # 4. Rabatte und Aufpreise
        adjustments_pricing = calculate_price_adjustments(project_details)
        pricing_result['components']['adjustments'] = adjustments_pricing

        # 5. Kategorien zusammenfassen
        pricing_result['categories'] = {
            'Hardware': hardware_pricing,
            'Services': services_pricing,
            'Zubehör': accessories_pricing,
            'Anpassungen': adjustments_pricing
        }

        # 6. Gesamtsummen berechnen
        subtotal = (
            hardware_pricing.get('total', 0) +
            services_pricing.get('total', 0) +
            accessories_pricing.get('total', 0)
        )

        adjustments_total = adjustments_pricing.get('total', 0)
        total_price = subtotal + adjustments_total

        # MwSt berechnen
        vat_rate = project_details.get('vat_rate', 0.19)
        vat_amount = total_price * vat_rate
        total_with_vat = total_price + vat_amount

        pricing_result['totals'] = {
            'subtotal': subtotal,
            'adjustments': adjustments_total,
            'net_total': total_price,
            'vat_rate': vat_rate,
            'vat_amount': vat_amount,
            'gross_total': total_with_vat,
            'formatted': {
                'subtotal': f"{subtotal:.2f} €",
                'adjustments': f"{adjustments_total:.2f} €",
                'net_total': f"{total_price:.2f} €",
                'vat_amount': f"{vat_amount:.2f} €",
                'gross_total': f"{total_with_vat:.2f} €"
            }
        }

        # 7. Detaillierte Aufschlüsselung
        pricing_result['breakdown'] = create_detailed_breakdown(pricing_result)

        # 8. In Session State speichern für PDF-Generierung
        store_pricing_for_pdf(pricing_result, project_details)

        return pricing_result

    except Exception as e:
        st.error(f"Fehler bei dynamischer Preisberechnung: {str(e)}")
        return create_empty_pricing_result()


def calculate_hardware_pricing(
        project_details: dict[str, Any]) -> dict[str, Any]:
    """Berechnet Hardware-Preise (PV, WR, Batterien)"""

    hardware_total = 0
    hardware_components = []

    try:
        # PV Module
        pv_pricing = get_pv_module_pricing(project_details)
        if pv_pricing:
            hardware_components.extend(pv_pricing['components'])
            hardware_total += pv_pricing['total']

        # Wechselrichter
        inverter_pricing = get_inverter_pricing(project_details)
        if inverter_pricing:
            hardware_components.extend(inverter_pricing['components'])
            hardware_total += inverter_pricing['total']

        # Batteriespeicher
        battery_pricing = get_battery_pricing(project_details)
        if battery_pricing:
            hardware_components.extend(battery_pricing['components'])
            hardware_total += battery_pricing['total']

        return {
            'components': hardware_components,
            'total': hardware_total,
            'formatted_total': f"{hardware_total:.2f} €",
            'count': len(hardware_components)
        }

    except Exception as e:
        st.error(f"Fehler bei Hardware-Preisberechnung: {str(e)}")
        return {
            'components': [],
            'total': 0,
            'formatted_total': "0.00 €",
            'count': 0}


def calculate_services_pricing_dynamic(
        project_details: dict[str, Any]) -> dict[str, Any]:
    """Berechnet Services-Preise dynamisch"""

    try:
        from services_integration import calculate_services_pricing

        # Hole ausgewählte Services aus Session State
        selected_services = []

        # Durchsuche Session State nach ausgewählten Services
        for key, value in st.session_state.items():
            if key.startswith("service_select_") and value:
                service_id = int(key.replace("service_select_", ""))
                selected_services.append(service_id)

        services_result = calculate_services_pricing(
            selected_services, project_details)

        # Formatiere für einheitliche Struktur und sortiere nach
        # PDF-Reihenfolge
        all_services = services_result['standard_services'] + \
            services_result['optional_services']
        all_services.sort(key=lambda x: (x.get('pdf_order', 0), x['name']))

        return {
            'components': all_services,
            'total': services_result['total_services'],
            'formatted_total': services_result['formatted_total_services'],
            'count': len(all_services),
            'standard_total': services_result['total_standard'],
            'optional_total': services_result['total_optional']
        }

    except ImportError:
        return {
            'components': [],
            'total': 0,
            'formatted_total': "0.00 €",
            'count': 0}
    except Exception as e:
        st.error(f"Fehler bei Services-Preisberechnung: {str(e)}")
        return {
            'components': [],
            'total': 0,
            'formatted_total': "0.00 €",
            'count': 0}


def calculate_accessories_pricing(
        project_details: dict[str, Any]) -> dict[str, Any]:
    """Berechnet Zubehör-Preise"""

    accessories_total = 0
    accessories_components = []

    try:
        # Montagesystem
        mounting_price = project_details.get('mounting_system_price', 0)
        if mounting_price > 0:
            accessories_components.append({
                'name': 'Montagesystem',
                'type': 'Zubehör',
                'price': mounting_price,
                'quantity': 1,
                'total_price': mounting_price,
                'formatted_total': f"{mounting_price:.2f} €"
            })
            accessories_total += mounting_price

        # Kabel und Verkabelung
        cable_price = project_details.get('cable_price', 0)
        if cable_price > 0:
            accessories_components.append({
                'name': 'Verkabelung',
                'type': 'Zubehör',
                'price': cable_price,
                'quantity': 1,
                'total_price': cable_price,
                'formatted_total': f"{cable_price:.2f} €"
            })
            accessories_total += cable_price

        # Monitoring System
        monitoring_price = project_details.get('monitoring_price', 0)
        if monitoring_price > 0:
            accessories_components.append({
                'name': 'Monitoring System',
                'type': 'Zubehör',
                'price': monitoring_price,
                'quantity': 1,
                'total_price': monitoring_price,
                'formatted_total': f"{monitoring_price:.2f} €"
            })
            accessories_total += monitoring_price

        return {
            'components': accessories_components,
            'total': accessories_total,
            'formatted_total': f"{accessories_total:.2f} €",
            'count': len(accessories_components)
        }

    except Exception as e:
        st.error(f"Fehler bei Zubehör-Preisberechnung: {str(e)}")
        return {
            'components': [],
            'total': 0,
            'formatted_total': "0.00 €",
            'count': 0}


def calculate_price_adjustments(
        project_details: dict[str, Any]) -> dict[str, Any]:
    """Berechnet Rabatte und Aufpreise"""

    adjustments_total = 0
    adjustments_components = []

    try:
        # Rabatte
        discount_percent = project_details.get('discount_percent', 0)
        if discount_percent > 0:
            # Basis für Rabatt berechnen (Hardware + Services + Zubehör)
            base_amount = (
                project_details.get('hardware_total', 0) +
                project_details.get('services_total', 0) +
                project_details.get('accessories_total', 0)
            )
            discount_amount = base_amount * (discount_percent / 100)

            adjustments_components.append({
                'name': f'Rabatt ({discount_percent}%)',
                'type': 'Rabatt',
                'price': -discount_amount,
                'quantity': 1,
                'total_price': -discount_amount,
                'formatted_total': f"-{discount_amount:.2f} €"
            })
            adjustments_total -= discount_amount

        # Aufpreise
        surcharge_amount = project_details.get('surcharge_amount', 0)
        if surcharge_amount > 0:
            adjustments_components.append({
                'name': 'Aufpreis',
                'type': 'Aufpreis',
                'price': surcharge_amount,
                'quantity': 1,
                'total_price': surcharge_amount,
                'formatted_total': f"{surcharge_amount:.2f} €"
            })
            adjustments_total += surcharge_amount

        return {
            'components': adjustments_components,
            'total': adjustments_total,
            'formatted_total': f"{adjustments_total:.2f} €",
            'count': len(adjustments_components)
        }

    except Exception as e:
        st.error(f"Fehler bei Anpassungs-Preisberechnung: {str(e)}")
        return {
            'components': [],
            'total': 0,
            'formatted_total': "0.00 €",
            'count': 0}


def get_pv_module_pricing(
        project_details: dict[str, Any]) -> dict[str, Any] | None:
    """Hole PV-Modul Preise aus bestehender Preisberechnung"""
    try:
        # Integration mit bestehendem Pricing-System
        from solar_calculator_pricing_integration import get_pricing_display_for_ui

        pricing_display = get_pricing_display_for_ui(project_details)

        if pricing_display.get('display_components'):
            pv_components = [
                comp for comp in pricing_display['display_components'] if 'pv' in comp.get(
                    'type', '').lower() or 'modul' in comp.get(
                    'name', '').lower()]

            if pv_components:
                total = sum(
                    _safe_float_conversion(
                        comp.get(
                            'formatted_total_price',
                            '0')) for comp in pv_components)
                return {
                    'components': pv_components,
                    'total': total
                }

        return None

    except ImportError:
        return None


def get_inverter_pricing(
        project_details: dict[str, Any]) -> dict[str, Any] | None:
    """Hole Wechselrichter Preise"""
    try:
        from solar_calculator_pricing_integration import get_pricing_display_for_ui

        pricing_display = get_pricing_display_for_ui(project_details)

        if pricing_display.get('display_components'):
            inverter_components = [
                comp for comp in pricing_display['display_components'] if 'wechselrichter' in comp.get(
                    'name', '').lower() or 'inverter' in comp.get(
                    'type', '').lower()]

            if inverter_components:
                total = sum(
                    _safe_float_conversion(
                        comp.get(
                            'formatted_total_price',
                            '0')) for comp in inverter_components)
                return {
                    'components': inverter_components,
                    'total': total
                }

        return None

    except ImportError:
        return None


def get_battery_pricing(
        project_details: dict[str, Any]) -> dict[str, Any] | None:
    """Hole Batteriespeicher Preise"""
    try:
        from solar_calculator_pricing_integration import get_pricing_display_for_ui

        pricing_display = get_pricing_display_for_ui(project_details)

        if pricing_display.get('display_components'):
            battery_components = [
                comp for comp in pricing_display['display_components'] if 'batterie' in comp.get(
                    'name', '').lower() or 'speicher' in comp.get(
                    'type', '').lower()]

            if battery_components:
                total = sum(
                    _safe_float_conversion(
                        comp.get(
                            'formatted_total_price',
                            '0')) for comp in battery_components)
                return {
                    'components': battery_components,
                    'total': total
                }

        return None

    except ImportError:
        return None


def create_detailed_breakdown(
        pricing_result: dict[str, Any]) -> dict[str, Any]:
    """Erstellt detaillierte Aufschlüsselung für UI und PDF"""

    breakdown = {
        'categories': [],
        'summary': {},
        'line_items': []
    }

    # Kategorien durchgehen
    for category_name, category_data in pricing_result['categories'].items():
        if category_data['count'] > 0:
            category_breakdown = {
                'name': category_name,
                'total': category_data['total'],
                'formatted_total': category_data['formatted_total'],
                'items': category_data['components']
            }
            breakdown['categories'].append(category_breakdown)

            # Line Items für PDF
            for item in category_data['components']:
                breakdown['line_items'].append({
                    'category': category_name,
                    'name': item['name'],
                    'description': item.get('description', ''),
                    'quantity': item.get('quantity', 1),
                    'unit_price': item.get('price', 0),
                    'total_price': item.get('total_price', 0),
                    'formatted_unit_price': f"{item.get('price', 0):.2f} €",
                    'formatted_total_price': item.get('formatted_total', '0.00 €')
                })

    # Summary
    breakdown['summary'] = pricing_result['totals']

    return breakdown


def store_pricing_for_pdf(
        pricing_result: dict[str, Any], project_details: dict[str, Any]):
    """Speichert Preisberechnung für PDF-Generierung"""

    # Speichere in Session State für PDF-Zugriff
    st.session_state['dynamic_pricing_result'] = pricing_result
    st.session_state['dynamic_pricing_timestamp'] = datetime.now().isoformat()

    # Erstelle PDF-kompatible Datenstruktur
    pdf_data = {
        'project_details': project_details,
        'pricing': pricing_result,
        'line_items': pricing_result['breakdown']['line_items'],
        'totals': pricing_result['totals'],
        'categories': pricing_result['breakdown']['categories'],
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'version': '1.0',
            'type': 'dynamic_pricing'
        }
    }

    # Als JSON für PDF-System
    st.session_state['pdf_pricing_data'] = json.dumps(
        pdf_data, ensure_ascii=False, indent=2)

    # Als Bytes für direkten PDF-Zugriff
    pdf_bytes_data = json.dumps(pdf_data, ensure_ascii=False).encode('utf-8')
    st.session_state['pdf_pricing_bytes'] = pdf_bytes_data


def create_empty_pricing_result() -> dict[str, Any]:
    """Erstellt leeres Preisberechnungs-Ergebnis bei Fehlern"""
    return {
        'components': {},
        'categories': {},
        'totals': {
            'subtotal': 0,
            'adjustments': 0,
            'net_total': 0,
            'vat_amount': 0,
            'gross_total': 0,
            'formatted': {
                'subtotal': "0.00 €",
                'adjustments': "0.00 €",
                'net_total': "0.00 €",
                'vat_amount': "0.00 €",
                'gross_total': "0.00 €"
            }
        },
        'breakdown': {'categories': [], 'summary': {}, 'line_items': []},
        'metadata': {
            'calculation_timestamp': datetime.now().isoformat(),
            'error': True
        }
    }


def get_dynamic_pricing_key() -> str:
    """Gibt den Session State Key für dynamische Preisberechnung zurück"""
    return 'dynamic_pricing_result'


def get_dynamic_pricing_bytes() -> bytes | None:
    """Gibt die Preisberechnung als Bytes für PDF zurück"""
    return st.session_state.get('pdf_pricing_bytes')


def get_dynamic_pricing_json() -> str | None:
    """Gibt die Preisberechnung als JSON für PDF zurück"""
    return st.session_state.get('pdf_pricing_data')
