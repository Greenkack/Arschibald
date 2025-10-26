"""
services_integration.py

Integration von Dienstleistungen und Services in die Preisberechnung
"""

from typing import Any

import streamlit as st


def _format_german_currency(amount: float) -> str:
    """Format currency in German format: 1.234,56 €"""
    # Format with 2 decimal places
    formatted = f"{amount:.2f}"

    # Split into integer and decimal parts
    if '.' in formatted:
        integer_part, decimal_part = formatted.split('.')
    else:
        integer_part, decimal_part = formatted, "00"

    # Add thousand separators (dots) to integer part
    if len(integer_part) > 3:
        # Reverse, add dots every 3 digits, then reverse back
        reversed_int = integer_part[::-1]
        grouped = '.'.join(reversed_int[i:i + 3]
                           for i in range(0, len(reversed_int), 3))
        integer_part = grouped[::-1]

    return f"{integer_part},{decimal_part} €"


def get_services_for_calculation() -> dict[str, list[dict[str, Any]]]:
    """Get services categorized for calculation"""
    try:
        from admin_services_ui import get_optional_services, get_standard_services

        standard_services = get_standard_services()
        optional_services = get_optional_services()

        return {
            'standard': standard_services,
            'optional': optional_services
        }
    except ImportError:
        return {'standard': [], 'optional': []}


def calculate_services_pricing(
    selected_services: list[int],
    project_details: dict[str, Any]
) -> dict[str, Any]:
    """Calculate pricing for selected services"""
    try:
        from admin_services_ui import load_services

        all_services = load_services()
        services_by_id = {s['id']: s for s in all_services}

        # Get standard services (always included)
        standard_services = [s for s in all_services if s['is_standard']]

        # Get selected optional services
        optional_services = [
            services_by_id[service_id]
            for service_id in selected_services
            if service_id in services_by_id and not services_by_id[service_id]['is_standard']
        ]

        # Calculate pricing
        total_standard = 0
        total_optional = 0

        standard_details = []
        optional_details = []

        # Calculate standard services
        for service in standard_services:
            quantity = get_service_quantity(service, project_details)
            total_price = service['price'] * quantity
            total_standard += total_price

            standard_details.append({
                'id': service['id'],
                'name': service['name'],
                'description': service['description'],
                'category': service['category'],
                'price': service['price'],
                'quantity': quantity,
                'calculate_per': service['calculate_per'],
                'total_price': total_price,
                'formatted_price': _format_german_currency(service['price']),
                'formatted_total': _format_german_currency(total_price),
                'is_standard': True,
                'pdf_order': service.get('pdf_order', 0)
            })

        # Calculate optional services
        for service in optional_services:
            quantity = get_service_quantity(service, project_details)
            total_price = service['price'] * quantity
            total_optional += total_price

            optional_details.append({
                'id': service['id'],
                'name': service['name'],
                'description': service['description'],
                'category': service['category'],
                'price': service['price'],
                'quantity': quantity,
                'calculate_per': service['calculate_per'],
                'total_price': total_price,
                'formatted_price': _format_german_currency(service['price']),
                'formatted_total': _format_german_currency(total_price),
                'is_standard': False,
                'pdf_order': service.get('pdf_order', 0)
            })

        return {
            'standard_services': standard_details,
            'optional_services': optional_details,
            'total_standard': total_standard,
            'total_optional': total_optional,
            'total_services': total_standard + total_optional,
            'formatted_total_standard': _format_german_currency(total_standard),
            'formatted_total_optional': _format_german_currency(total_optional),
            'formatted_total_services': _format_german_currency(
                total_standard + total_optional)}

    except Exception as e:
        st.error(f"Fehler bei Services-Berechnung: {str(e)}")
        return {
            'standard_services': [],
            'optional_services': [],
            'total_standard': 0,
            'total_optional': 0,
            'total_services': 0,
            'formatted_total_standard': "0,00 €",
            'formatted_total_optional': "0,00 €",
            'formatted_total_services': "0,00 €"
        }


def get_service_quantity(
        service: dict[str, Any], project_details: dict[str, Any]) -> float:
    """Calculate quantity for a service based on project details"""
    calculate_per = service.get('calculate_per', 'Stück')

    if calculate_per == 'kWp':
        # Use PV system size - try multiple possible keys, starting with
        # anlage_kwp
        pv_kwp = project_details.get('anlage_kwp')
        if pv_kwp is None:
            pv_kwp = project_details.get('pv_kwp')
        if pv_kwp is None:
            pv_kwp = project_details.get('system_size_kwp')
        if pv_kwp is None:
            pv_kwp = project_details.get('kwp')
        if pv_kwp is None:
            # Calculate from module data
            module_quantity = project_details.get('module_quantity', 0)
            selected_module_name = project_details.get(
                'selected_module_name', '')

            if module_quantity > 0 and selected_module_name:
                # Extract wattage from model name (e.g., "TSM-440" -> 440W)
                import re
                watt_match = re.search(r'(\d+)W?', selected_module_name)
                if watt_match:
                    watts = int(watt_match.group(1))
                    kwp_per_module = watts / 1000.0
                    pv_kwp = kwp_per_module * module_quantity
                    print(
                        f"Calculated kWp: {module_quantity} modules × {watts}W = {
                            pv_kwp:.2f} kWp")

        if pv_kwp is None:
            pv_kwp = 1.0  # Fallback

        print(
            f"Service '{
                service.get('name')}': Using {pv_kwp} kWp for calculation")
        return float(pv_kwp)
    if calculate_per == 'm²':
        # Use roof area or estimate from kWp
        roof_area = project_details.get('roof_area_m2')
        if roof_area:
            return roof_area
        # Estimate: ~6-8 m² per kWp, prioritize anlage_kwp
        kwp_value = project_details.get(
            'anlage_kwp') or project_details.get('pv_kwp', 1.0)
        return kwp_value * 7
    if calculate_per == 'Stunde':
        # Default hours for installation/service, prioritize anlage_kwp
        pv_kwp = project_details.get(
            'anlage_kwp') or project_details.get('pv_kwp', 1.0)
        # Estimate installation time based on system size
        return max(8, pv_kwp * 2)  # Minimum 8 hours, 2 hours per kWp
    # Stück or Pauschal
    return 1.0


def render_services_selection(show_standard: bool = True):
    """Render services selection UI"""
    services_data = get_services_for_calculation()

    if not services_data['standard'] and not services_data['optional']:
        st.info(
            "Keine Services konfiguriert. Bitte konfigurieren Sie Services im Admin-Bereich.")
        return []

    selected_optional_services = []

    # Show standard services (always included) - only if requested
    if show_standard and services_data['standard']:
        st.markdown("#### ✅ Standard-Services (automatisch enthalten)")
        for service in services_data['standard']:
            st.write(
                f"• **{service['name']}** - {service['price']:.2f} € pro {service['calculate_per']}")
            if service['description']:
                st.caption(f"  {service['description']}")

    # Show optional services for selection
    if services_data['optional']:
        if show_standard:
            st.markdown("#### 🔧 Zusätzliche Services (optional)")
        else:
            st.markdown("#### 🔧 Optionale Services auswählen")

        for service in services_data['optional']:
            col1, col2 = st.columns([3, 1])

            with col1:
                selected = st.checkbox(
                    f"**{service['name']}** - {service['price']:.2f} € pro {service['calculate_per']}",
                    key=f"service_select_{service['id']}"
                )
                if service['description']:
                    st.caption(f"  {service['description']}")

            with col2:
                if service['category']:
                    st.caption(f"📂 {service['category']}")

            if selected:
                selected_optional_services.append(service['id'])

    return selected_optional_services


def update_pricing_with_services(
    base_pricing: dict[str, Any],
    project_details: dict[str, Any],
    standard_services_enabled: bool = True,
    optional_services_enabled: bool = False
) -> dict[str, Any]:
    """Update pricing calculation to include services"""

    # Always include standard services, optionally include selected optional
    # services

    # Get selected optional services from session state (only if optional
    # services are enabled)
    selected_optional_services = []
    services_data = get_services_for_calculation()

    if optional_services_enabled:
        for service in services_data['optional']:
            if st.session_state.get(f"service_select_{service['id']}", False):
                selected_optional_services.append(service['id'])

    # Calculate services pricing (always include standard services)
    services_pricing = calculate_services_pricing(
        selected_optional_services, project_details)

    # Update base pricing with services
    updated_pricing = base_pricing.copy()

    # Add services to components
    if 'display_components' not in updated_pricing:
        updated_pricing['display_components'] = []

    # Combine and sort services by PDF order
    all_services_for_display = services_pricing['standard_services'] + \
        services_pricing['optional_services']
    all_services_for_display.sort(
        key=lambda x: (
            x.get(
                'pdf_order',
                0),
            x['name']))

    # Add services in PDF order
    for service in all_services_for_display:
        # Format service type for better display
        service_type = "Dienstleistung"
        if service['is_standard']:
            service_type = "Standard-Service"
        else:
            service_type = "Zusatz-Service"

        # Format quantity display
        quantity_display = service['quantity']
        if service['calculate_per'] == 'kWp':
            quantity_display = f"{service['quantity']:.1f}"
        elif service['calculate_per'] == 'm²' or service['calculate_per'] in ['Stück', 'Pauschal']:
            quantity_display = f"{service['quantity']:.0f}"
        else:
            quantity_display = f"{service['quantity']:.1f}"

        updated_pricing['display_components'].append({
            'name': service['name'],
            'type': service_type,
            'quantity': quantity_display,
            'calculate_per': service['calculate_per'],
            'formatted_unit_price': service['formatted_price'],
            'formatted_total_price': service['formatted_total'],
            'total_price': service['total_price'],  # Add raw numeric value
            'category': 'Dienstleistungen',  # Group all services under one category
            'is_service': True,
            'is_standard': service['is_standard'],
            'pdf_order': service.get('pdf_order', 0),
            # Use service category as "brand" for display
            'brand': service.get('category', '')
        })

    # Update totals
    original_total = base_pricing.get('total_price', 0)
    services_total = services_pricing['total_services']
    new_total = original_total + services_total

    updated_pricing.update({
        'services_total': services_total,
        'services_formatted': services_pricing['formatted_total_services'],
        'original_total': original_total,
        'total_price': new_total,
        'formatted_total_price': _format_german_currency(new_total),
        'services_breakdown': services_pricing
    })

    # Update category breakdown if exists
    if 'display_components_by_category' in updated_pricing:
        # Add Dienstleistungen category
        if services_pricing['standard_services'] or services_pricing['optional_services']:
            services_category_components = []

            for service in all_services_for_display:
                # Format service type for better display
                service_type = "Standard-Service" if service['is_standard'] else "Zusatz-Service"

                # Format quantity display with 2 decimal places for kWp
                quantity_display = service['quantity']
                if service['calculate_per'] == 'kWp':
                    quantity_display = f"{service['quantity']:.2f}"
                elif service['calculate_per'] == 'm²' or service['calculate_per'] in ['Stück', 'Pauschal']:
                    quantity_display = f"{service['quantity']:.0f}"
                else:
                    quantity_display = f"{service['quantity']:.1f}"

                services_category_components.append({
                    'name': service['name'],
                    'type': service_type,
                    'quantity': quantity_display,
                    'calculate_per': service['calculate_per'],
                    'formatted_unit_price': service['formatted_price'],
                    'formatted_total_price': service['formatted_total'],
                    # Add raw numeric value
                    'total_price': service['total_price'],
                    'is_service': True,
                    'is_standard': service['is_standard'],
                    # Use service category as brand
                    'brand': service.get('category', '')
                })

            updated_pricing['display_components_by_category']['Dienstleistungen'] = {
                'components': services_category_components,
                'category_total': services_total,
                'formatted_category_total': _format_german_currency(services_total)}

            # Generate PDF keys for services
            try:
                from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory

                key_manager = DynamicKeyManager()
                services_keys = {}

                # Generate keys for ALL services (active, inactive, standard,
                # optional)
                all_available_services = get_services_for_calculation()
                all_services_list = all_available_services['standard'] + \
                    all_available_services['optional']

                for i, service in enumerate(all_services_list, 1):
                    # Calculate quantity and pricing for this service
                    quantity = get_service_quantity(service, project_details)
                    total_price = service['price'] * quantity

                    # Determine if this service is currently active/selected
                    is_active = False
                    if service['is_standard']:
                        is_active = True  # Standard services are always active
                    else:
                        # Check if optional service is selected
                        is_active = service['id'] in selected_optional_services

                    service_keys = key_manager.generate_keys({
                        f"SERVICE_{i}_NAME": service['name'],
                        f"SERVICE_{i}_DESCRIPTION": service.get('description', ''),
                        f"SERVICE_{i}_CATEGORY": service.get('category', ''),
                        f"SERVICE_{i}_PRICE": service['price'],
                        f"SERVICE_{i}_QUANTITY": quantity,
                        f"SERVICE_{i}_CALCULATE_PER": service['calculate_per'],
                        f"SERVICE_{i}_TOTAL_PRICE": total_price,
                        f"SERVICE_{i}_FORMATTED_PRICE": _format_german_currency(service['price']),
                        f"SERVICE_{i}_FORMATTED_TOTAL": _format_german_currency(total_price),
                        f"SERVICE_{i}_IS_STANDARD": service['is_standard'],
                        f"SERVICE_{i}_IS_ACTIVE": is_active,
                        f"SERVICE_{i}_PDF_ORDER": service.get('pdf_order', 0),
                    }, prefix="", category=KeyCategory.SERVICES)

                    services_keys.update(service_keys)

                # Add summary keys
                summary_keys = key_manager.generate_keys({
                    "SERVICES_TOTAL_STANDARD": services_pricing['total_standard'],
                    "SERVICES_TOTAL_OPTIONAL": services_pricing['total_optional'],
                    "SERVICES_TOTAL_ALL": services_pricing['total_services'],
                    "SERVICES_FORMATTED_STANDARD": services_pricing['formatted_total_standard'],
                    "SERVICES_FORMATTED_OPTIONAL": services_pricing['formatted_total_optional'],
                    "SERVICES_FORMATTED_ALL": services_pricing['formatted_total_services'],
                    "SERVICES_COUNT_STANDARD": len(services_pricing['standard_services']),
                    "SERVICES_COUNT_OPTIONAL": len(services_pricing['optional_services']),
                    "SERVICES_COUNT_TOTAL": len(services_pricing['standard_services']) + len(services_pricing['optional_services']),
                }, prefix="", category=KeyCategory.SERVICES)

                services_keys.update(summary_keys)

                # Store in updated pricing for PDF access
                updated_pricing['services_dynamic_keys'] = services_keys

                # Store in session state for global PDF access
                if 'st' in globals() and hasattr(st, 'session_state'):
                    st.session_state["services_pricing_keys"] = services_keys
                    st.session_state["services_pricing_data"] = services_pricing

            except ImportError:
                pass

    return updated_pricing
