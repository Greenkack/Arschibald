"""
solar_calculator.py

Enhanced Solar Calculator with integrated pricing system.
Separater Menüpunkt für die Auswahl der Technik (Module, WR, Speicher, Zusatzkomponenten).
Verwendet die gleichen Keys in st.session_state.project_data['project_details'] wie data_input,
damit Analyse und PDF weiterhin funktionieren.

Enhanced with real-time pricing calculations and calculate_per support.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st


# Fallback-freundliche Imports aus product_db
def _dummy_list_products(*args, **kwargs):
    return []


def _dummy_get_product_by_model_name(*args, **kwargs):
    return None


try:
    from product_db import get_product_by_model_name as get_product_by_model_name_safe
    from product_db import list_products as list_products_safe
except Exception:
    list_products_safe = _dummy_list_products  # type: ignore
    get_product_by_model_name_safe = _dummy_get_product_by_model_name  # type: ignore

# Import pricing integration
try:
    from dynamic_pricing_engine import _safe_float_conversion
    from services_integration import _format_german_currency
    from solar_calculator_pricing_integration import (
        get_pricing_display_for_ui,
        solar_pricing_integration,
        update_pricing_in_session_state,
    )
    PRICING_INTEGRATION_AVAILABLE = True
except ImportError as e:
    PRICING_INTEGRATION_AVAILABLE = False
    print(f"Warning: Pricing integration not available: {e}")

    # Fallback currency formatting function
    def _format_german_currency(amount: float) -> str:
        """Fallback German currency formatting"""
        formatted = f"{amount:.2f}"
        if '.' in formatted:
            integer_part, decimal_part = formatted.split('.')
        else:
            integer_part, decimal_part = formatted, "00"
        if len(integer_part) > 3:
            reversed_int = integer_part[::-1]
            grouped = '.'.join(reversed_int[i:i + 3]
                               for i in range(0, len(reversed_int), 3))
            integer_part = grouped[::-1]
        return f"{integer_part},{decimal_part} €"

    def _safe_float_conversion(price_string: str) -> float:
        """Fallback function if import fails"""
        try:
            clean_string = price_string.replace(
                '€', '').replace(' ', '').strip()
            if ',' in clean_string:
                parts = clean_string.split(',')
                if len(parts) == 2:
                    integer_part = parts[0].replace('.', '')
                    decimal_part = parts[1]
                    clean_string = f"{integer_part}.{decimal_part}"
            return float(clean_string)
        except BaseException:
            return 0.0


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


def _get_text(texts: dict[str, str], key: str,
              fallback: str | None = None) -> str:
    if fallback is None:
        fallback = key.replace("_", " ").title()
    try:
        return str(texts.get(key, fallback))
    except Exception:
        return fallback


def _display_pricing_information(
        details: dict[str, Any], texts: dict[str, str]) -> None:
    """Display enhanced real-time pricing information for selected components with categorization"""
    if not PRICING_INTEGRATION_AVAILABLE:
        return

    try:
        # Get pricing display data
        pricing_display = get_pricing_display_for_ui(details)

        if pricing_display.get("error"):
            st.warning(
                f"Preisberechnung nicht verfügbar: {
                    pricing_display['error']}")
            return

        # Display pricing summary
        if pricing_display.get("display_components"):
            # Header with switch for additional optional services
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### 💰 Preisübersicht")
            with col2:
                # Switch for optional services only (standard services are
                # always included)
                optional_services_enabled = st.toggle(
                    "Zusätzliche Services",
                    value=st.session_state.get(
                        "pricing_optional_services_enabled",
                        False),
                    key="pricing_optional_services_toggle",
                    help="Zusätzliche optionale Services in Preisberechnung einbeziehen")
                # Store state
                st.session_state["pricing_optional_services_enabled"] = optional_services_enabled

            # Always include standard services in pricing
            services_enabled = True  # Standard services always enabled

            # Always include standard services, show optional services
            # selection if enabled
            try:
                from services_integration import (
                    render_services_selection,
                    update_pricing_with_services,
                )

                # Always update pricing with standard services
                pricing_display = update_pricing_with_services(
                    pricing_display,
                    details,
                    services_enabled,
                    optional_services_enabled
                )

                # Show optional services selection if enabled
                if optional_services_enabled:
                    with st.expander("🛠️ Zusätzliche Services auswählen", expanded=True):
                        # Render optional services selection only
                        selected_services = render_services_selection(
                            show_standard=False)

                        # Update pricing with newly selected optional services
                        pricing_display = update_pricing_with_services(
                            pricing_display,
                            details,
                            services_enabled,
                            optional_services_enabled
                        )

                # Trigger dynamic pricing calculation
                try:
                    from dynamic_pricing_engine import calculate_dynamic_total_price
                    dynamic_pricing = calculate_dynamic_total_price(details)

                    # Update pricing display with dynamic results
                    if dynamic_pricing and dynamic_pricing.get('totals'):
                        pricing_display['dynamic_total'] = dynamic_pricing['totals']['gross_total']
                        pricing_display['dynamic_total_formatted'] = dynamic_pricing['totals']['formatted']['gross_total']
                        pricing_display['dynamic_breakdown'] = dynamic_pricing['breakdown']

                except ImportError:
                    pass

            except ImportError:
                st.warning(
                    "Services-Integration nicht verfügbar. Bitte überprüfen Sie die services_integration.py Datei.")

            # Verify and fix pricing totals
            if pricing_display.get("display_components_by_category"):
                # Recalculate totals to ensure they're correct
                hardware_total = 0
                services_total = 0

                for category, category_data in pricing_display["display_components_by_category"].items(
                ):
                    category_sum = 0
                    for comp in category_data["components"]:
                        # Get the actual numeric total price directly
                        if comp.get("is_service", False):
                            # For services, use the raw total_price value to
                            # avoid conversion errors
                            price_value = float(comp.get("total_price", 0))
                        else:
                            # For hardware, parse the formatted price
                            price_str = comp.get(
                                "formatted_total_price", "0,00 €")
                            price_value = _safe_float_conversion(price_str)
                        category_sum += price_value

                    # Update category total in German format
                    category_data["category_total"] = category_sum
                    category_data["formatted_category_total"] = _format_german_currency(
                        category_sum)

                    if category == "Dienstleistungen":
                        services_total = category_sum
                    else:
                        hardware_total += category_sum

                # Calculate final totals
                net_total = hardware_total + services_total
                vat_rate = 0.19  # 19% MwSt
                vat_amount = net_total * vat_rate
                gross_total = net_total + vat_amount

                # Update pricing display with correct totals in German format
                pricing_display["hardware_total"] = hardware_total
                pricing_display["services_total"] = services_total
                pricing_display["net_total"] = net_total
                pricing_display["vat_amount"] = vat_amount
                pricing_display["gross_total"] = gross_total
                pricing_display["formatted_hardware_total"] = _format_german_currency(
                    hardware_total)
                pricing_display["formatted_services_total"] = _format_german_currency(
                    services_total)
                pricing_display["formatted_net_total"] = _format_german_currency(
                    net_total)
                pricing_display["formatted_vat_amount"] = _format_german_currency(
                    vat_amount)
                pricing_display["formatted_gross_total"] = _format_german_currency(
                    gross_total)

                # Generate dynamic keys for PDF integration
                try:
                    from pricing.dynamic_key_manager import KeyCategory
                    from solar_calculator_pricing_integration import (
                        SolarCalculatorPricingIntegration,
                    )

                    pricing_integration = SolarCalculatorPricingIntegration()
                    if pricing_integration.key_manager:
                        # Generate comprehensive pricing keys for PDF
                        pricing_keys = pricing_integration.key_manager.generate_keys({
                            # Hardware totals
                            "HARDWARE_TOTAL": hardware_total,
                            "HARDWARE_TOTAL_FORMATTED": pricing_display["formatted_hardware_total"],

                            # Services totals
                            "SERVICES_TOTAL": services_total,
                            "SERVICES_TOTAL_FORMATTED": pricing_display["formatted_services_total"],

                            # Final calculations
                            "NET_TOTAL": net_total,
                            "NET_TOTAL_FORMATTED": pricing_display["formatted_net_total"],
                            "VAT_AMOUNT": vat_amount,
                            "VAT_AMOUNT_FORMATTED": pricing_display["formatted_vat_amount"],
                            "GROSS_TOTAL": gross_total,
                            "GROSS_TOTAL_FORMATTED": pricing_display["formatted_gross_total"],
                            "VAT_RATE": 19.0,

                            # Component counts
                            "HARDWARE_COMPONENT_COUNT": sum(len(cat_data["components"]) for cat_name, cat_data in pricing_display.get("display_components_by_category", {}).items() if cat_name != "Dienstleistungen"),
                            "SERVICES_COMPONENT_COUNT": len(pricing_display.get("display_components_by_category", {}).get("Dienstleistungen", {}).get("components", [])),

                        }, prefix="PRICING_", category=KeyCategory.PRICING)

                        # Add individual component keys
                        component_counter = 1
                        for category, category_data in pricing_display.get(
                                "display_components_by_category", {}).items():
                            for comp in category_data["components"]:
                                comp_keys = pricing_integration.key_manager.generate_keys({
                                    f"COMPONENT_{component_counter}_NAME": comp["name"],
                                    f"COMPONENT_{component_counter}_TYPE": comp["type"],
                                    f"COMPONENT_{component_counter}_QUANTITY": comp["quantity"],
                                    f"COMPONENT_{component_counter}_UNIT_PRICE": comp["formatted_unit_price"],
                                    f"COMPONENT_{component_counter}_TOTAL_PRICE": comp["formatted_total_price"],
                                    f"COMPONENT_{component_counter}_CATEGORY": category,
                                    f"COMPONENT_{component_counter}_BRAND": comp.get("brand", ""),
                                    f"COMPONENT_{component_counter}_IS_SERVICE": comp.get("is_service", False),
                                    f"COMPONENT_{component_counter}_IS_STANDARD": comp.get("is_standard", False),
                                }, prefix="", category=KeyCategory.COMPONENTS)

                                pricing_keys.update(comp_keys)
                                component_counter += 1

                        # Store keys in pricing display for PDF access
                        pricing_display["dynamic_keys"] = pricing_keys

                        # Store in session state for global PDF access
                        if hasattr(st, 'session_state'):
                            st.session_state["solar_calculator_pricing_keys"] = pricing_keys
                            st.session_state["solar_calculator_pricing_data"] = {
                                "hardware_total": hardware_total,
                                "services_total": services_total,
                                "net_total": net_total,
                                "vat_amount": vat_amount,
                                "gross_total": gross_total,
                                "components": pricing_display.get(
                                    "display_components_by_category",
                                    {}),
                                "formatted_totals": {
                                    "hardware": pricing_display["formatted_hardware_total"],
                                    "services": pricing_display["formatted_services_total"],
                                    "net": pricing_display["formatted_net_total"],
                                    "vat": pricing_display["formatted_vat_amount"],
                                    "gross": pricing_display["formatted_gross_total"]}}

                except ImportError:
                    pass

            # Show corrected pricing summary
            if pricing_display.get("hardware_total") is not None and pricing_display.get(
                    "services_total") is not None:
                st.markdown("---")
                st.markdown("#### 📊 Preiszusammenfassung")

                # Hardware and Services totals
                col1, col2 = st.columns([3, 1])
                with col1:
                    hardware_count = sum(len(cat_data["components"]) for cat_name, cat_data in pricing_display.get(
                        "display_components_by_category", {}).items() if cat_name != "Dienstleistungen")
                    st.write(f"**Hardware ({hardware_count} Positionen)**")
                with col2:
                    st.write(
                        f"**{pricing_display['formatted_hardware_total']}**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    services_count = len(
                        pricing_display.get(
                            "display_components_by_category",
                            {}).get(
                            "Dienstleistungen",
                            {}).get(
                            "components",
                            []))
                    st.write(f"**Services ({services_count} Positionen)**")
                with col2:
                    st.write(
                        f"**{pricing_display['formatted_services_total']}**")

                st.markdown("---")

                # Show gross total first (as "Gesamtpreis Brutto")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("### **Gesamtpreis Brutto:**")
                with col2:
                    st.markdown(
                        f"### **{pricing_display['formatted_gross_total']}**")

                # Show VAT as deduction (savings)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**abzüglich Mehrwertsteuer:**")
                with col2:
                    st.write(
                        f"**- {pricing_display['formatted_vat_amount']}**")

                st.markdown("---")

                # Final net price (as "finaler Angebotspreis")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("### **finaler Angebotspreis:**")
                with col2:
                    st.markdown(
                        f"### **{pricing_display['formatted_net_total']}**")

                st.markdown("---")

                # Manual provision field
                st.markdown("#### **Manuelle Provision**")
                col1, col2 = st.columns(2)
                with col1:
                    provision_percent = st.number_input(
                        "Provision (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=0.0,
                        step=0.1,
                        format="%.1f",
                        help="Manuelle Provision in Prozent auf den finalen Angebotspreis"
                    )
                with col2:
                    provision_euro = st.number_input(
                        "Provision (€)",
                        min_value=0.0,
                        max_value=100000.0,
                        value=0.0,
                        step=10.0,
                        format="%.2f",
                        help="Manuelle Provision als fester Euro-Betrag"
                    )

                # Calculate final price with provision if provision > 0 or
                # provision_euro > 0
                if provision_percent > 0 or provision_euro > 0:
                    # Get the net total as base for provision calculation
                    net_total_amount = pricing_display.get('net_total', 0.0)

                    # Calculate total provision (% + €)
                    provision_percent_amount = net_total_amount * \
                        (provision_percent / 100.0)
                    total_provision_amount = provision_percent_amount + provision_euro
                    final_price_with_provision = net_total_amount + total_provision_amount

                    # Format provision amount and final price using imported
                    # function

                    formatted_total_provision = _format_german_currency(
                        total_provision_amount)
                    formatted_final_with_provision = _format_german_currency(
                        final_price_with_provision)

                    # Show calculation breakdown
                    st.markdown("**Provisionsberechnung:**")

                    # Show base price
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Basis (finaler Angebotspreis):")
                    with col2:
                        st.write(f"{pricing_display['formatted_net_total']}")

                    # Show provision breakdown
                    if provision_percent > 0:
                        formatted_percent_provision = _format_german_currency(
                            provision_percent_amount)
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"+ Provision ({provision_percent}%)")
                        with col2:
                            st.write(f"+ {formatted_percent_provision}")

                    if provision_euro > 0:
                        formatted_euro_provision = _format_german_currency(
                            provision_euro)
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write("+ Provision (Festbetrag)")
                        with col2:
                            st.write(f"+ {formatted_euro_provision}")

                    st.markdown("---")

                    # Show final price with provision (recalculate to ensure
                    # correctness)
                    final_endpreis = net_total_amount + total_provision_amount
                    formatted_final_endpreis = _format_german_currency(
                        final_endpreis)

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("### **🎯 Endpreis mit Provision:**")
                    with col2:
                        st.markdown(f"### **{formatted_final_endpreis}**")

                    # Store provision data in session state for PDF access
                    if 'project_data' not in st.session_state:
                        st.session_state.project_data = {}
                    if 'project_details' not in st.session_state.project_data:
                        st.session_state.project_data['project_details'] = {}

                    st.session_state.project_data['project_details']['provision_percent'] = provision_percent
                    st.session_state.project_data['project_details']['provision_euro'] = provision_euro
                    st.session_state.project_data['project_details']['provision_percent_amount'] = provision_percent_amount
                    st.session_state.project_data['project_details']['total_provision_amount'] = total_provision_amount
                    st.session_state.project_data['project_details']['final_price_with_provision'] = final_endpreis
                    st.session_state.project_data['project_details']['formatted_total_provision'] = formatted_total_provision
                    st.session_state.project_data['project_details'][
                        'formatted_final_with_provision'] = formatted_final_endpreis
                else:
                    # Clear provision data if no provision is set
                    if 'project_data' in st.session_state and 'project_details' in st.session_state.project_data:
                        provision_keys = [
                            'provision_percent',
                            'provision_euro',
                            'provision_percent_amount',
                            'total_provision_amount',
                            'final_price_with_provision',
                            'formatted_total_provision',
                            'formatted_final_with_provision']
                        for key in provision_keys:
                            st.session_state.project_data['project_details'].pop(
                                key, None)

                st.markdown("---")

                # Preisänderungen Section (vollständig aus analysis.py
                # übernommen)
                st.markdown(
                    "#### **Preisänderungen (Rabatte, Zuschläge, Sondervereinbarungen)**")

                # Vier Spalten für vollständige Übersicht
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown("**Rabatte**")
                    discount_percent = st.slider(
                        "Rabatt (%)",
                        min_value=0.0, max_value=100.0, value=0.0, step=0.1,
                        key="pricing_modifications_discount_slider",
                        help="Prozentualer Rabatt auf den Bruttobetrag"
                    )
                    st.text_area(
                        "Beschreibung für Rabatt",
                        key="pricing_modifications_descriptions_discount_text",
                        help="Beschreibung oder Details zum Rabatt.",
                        height=80
                    )

                with col2:
                    st.markdown("**Nachlässe**")
                    rebates_eur = st.slider(
                        "Nachlässe (€)",
                        min_value=0.0, max_value=10000.0, value=0.0, step=10.0,
                        key="pricing_modifications_rebates_slider",
                        help="Feste Nachlässe in Euro"
                    )
                    st.text_area(
                        "Beschreibung für Nachlässe",
                        key="pricing_modifications_descriptions_rebates_text",
                        help="Beschreibung oder Details zu den Nachlässen.",
                        height=80
                    )

                with col3:
                    st.markdown("**Zuschläge**")
                    surcharge_percent = st.slider(
                        "Zuschlag (%)",
                        min_value=0.0, max_value=100.0, value=0.0, step=0.1,
                        key="pricing_modifications_surcharge_slider",
                        help="Prozentualer Zuschlag auf den Bruttobetrag"
                    )
                    st.text_area(
                        "Beschreibung für Zuschlag",
                        key="pricing_modifications_descriptions_surcharge_text",
                        help="Beschreibung oder Details zum Zuschlag.",
                        height=80)

                with col4:
                    st.markdown("**Sonderkosten**")
                    special_costs_eur = st.slider(
                        "Sonderkosten (€)",
                        min_value=0.0, max_value=10000.0, value=0.0, step=10.0,
                        key="pricing_modifications_special_costs_slider",
                        help="Zusätzliche Sonderkosten in Euro"
                    )
                    st.text_area(
                        "Beschreibung für Sonderkosten",
                        key="pricing_modifications_descriptions_special_costs_text",
                        help="Beschreibung oder Details zu den Sonderkosten.",
                        height=80)

                # Sonstiges und Sondervereinbarungen (volle Breite)
                col_misc1, col_misc2 = st.columns(2)
                with col_misc1:
                    miscellaneous_eur = st.slider(
                        "Sonstiges (€)",
                        min_value=0.0, max_value=10000.0, value=0.0, step=10.0,
                        key="pricing_modifications_miscellaneous_slider",
                        help="Sonstige Kosten oder Abzüge in Euro"
                    )
                    st.text_area(
                        "Beschreibung für Sonstiges",
                        key="pricing_modifications_descriptions_miscellaneous_text",
                        help="Beschreibung oder Details zu Sonstigem.",
                        height=80)

                with col_misc2:
                    st.text_area(
                        "Sondervereinbarungen",
                        key="pricing_modifications_special_agreements_text",
                        help="Zusätzliche Informationen oder Vereinbarungen, die im Angebot berücksichtigt werden sollen.",
                        height=120)

                # Calculate final price with discounts and surcharges if any
                # modifications are applied
                if (discount_percent > 0 or rebates_eur > 0 or surcharge_percent >
                        0 or special_costs_eur > 0 or miscellaneous_eur > 0):

                    # Determine base price for discount/surcharge calculations
                    # Start with the correct net total
                    net_base = pricing_display.get('net_total', 0.0)
                    vat_rate = 0.19  # 19% MwSt

                    # If provision was applied, include it in the base
                    if provision_percent > 0 or provision_euro > 0:
                        # Add provision to net base (same logic as provision
                        # calculation)
                        provision_percent_amount = net_base * \
                            (provision_percent / 100.0)
                        net_with_provision = net_base + provision_percent_amount + provision_euro
                        # Use net price with provision as base for
                        # modifications
                        base_price_net = net_with_provision
                    else:
                        # Use net total as base
                        base_price_net = net_base

                    # Show base price for transparency
                    st.markdown("**Preisänderungen-Berechnung:**")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if provision_percent > 0 or provision_euro > 0:
                            st.write("Basis (Angebotspreis + Provision):")
                        else:
                            st.write("Basis (finaler Angebotspreis):")
                    with col2:
                        st.write(f"{_format_german_currency(base_price_net)}")

                    # Calculate discounts (on net price)
                    discount_percent_amount = base_price_net * \
                        (discount_percent / 100.0)
                    total_discounts = discount_percent_amount + rebates_eur
                    price_after_discounts = base_price_net - total_discounts

                    # Calculate surcharges (on net price after discounts)
                    surcharge_percent_amount = price_after_discounts * \
                        (surcharge_percent / 100.0)
                    total_surcharges = surcharge_percent_amount + \
                        special_costs_eur + miscellaneous_eur

                    # Final net price after all modifications
                    final_net_price_modified = price_after_discounts + total_surcharges

                    # Calculate VAT on final net price
                    final_vat_amount = final_net_price_modified * vat_rate
                    final_gross_price_modified = final_net_price_modified + final_vat_amount

                    # Show discount calculations
                    if total_discounts > 0:
                        st.markdown("**Rabatte & Nachlässe:**")
                        if discount_percent > 0:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"- Rabatt ({discount_percent}%)")
                            with col2:
                                st.write(
                                    f"- {_format_german_currency(discount_percent_amount)}")

                        if rebates_eur > 0:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write("- Pauschale Rabatte")
                            with col2:
                                st.write(
                                    f"- {_format_german_currency(rebates_eur)}")

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write("**Summe Rabatte:**")
                        with col2:
                            st.write(
                                f"**- {_format_german_currency(total_discounts)}**")

                    # Show surcharge calculations
                    if total_surcharges > 0:
                        st.markdown("**Aufpreise & Zusatzkosten:**")
                        if surcharge_percent > 0:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"+ Aufpreis ({surcharge_percent}%)")
                            with col2:
                                st.write(
                                    f"+ {_format_german_currency(surcharge_percent_amount)}")

                        if special_costs_eur > 0:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write("+ Sonderkosten")
                            with col2:
                                st.write(
                                    f"+ {_format_german_currency(special_costs_eur)}")

                        if miscellaneous_eur > 0:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write("+ Sonstiges")
                            with col2:
                                st.write(
                                    f"+ {_format_german_currency(miscellaneous_eur)}")

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write("**Summe Aufpreise:**")
                        with col2:
                            st.write(
                                f"**+ {_format_german_currency(total_surcharges)}**")

                    st.markdown("---")

                    # Show final modified price (NETTO!)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("### **🎯 Finaler Angebotspreis (netto):**")
                    with col2:
                        st.markdown(
                            f"### **{_format_german_currency(final_net_price_modified)}**")

                    # Show VAT breakdown for modified price
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("zzgl. Mehrwertsteuer (19%):")
                    with col2:
                        st.write(
                            f"+ {_format_german_currency(final_vat_amount)}")

                    st.markdown("---")

                    # Show final gross price
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("### **💰 Endpreis (brutto):**")
                    with col2:
                        st.markdown(
                            f"### **{_format_german_currency(final_gross_price_modified)}**")

                    # Store modified pricing data in session state
                    if 'project_data' not in st.session_state:
                        st.session_state.project_data = {}
                    if 'project_details' not in st.session_state.project_data:
                        st.session_state.project_data['project_details'] = {}

                    st.session_state.project_data['project_details']['discount_percent'] = discount_percent
                    st.session_state.project_data['project_details']['rebates_eur'] = rebates_eur
                    st.session_state.project_data['project_details']['surcharge_percent'] = surcharge_percent
                    st.session_state.project_data['project_details']['special_costs_eur'] = special_costs_eur
                    st.session_state.project_data['project_details']['miscellaneous_eur'] = miscellaneous_eur
                    st.session_state.project_data['project_details']['total_discounts'] = total_discounts
                    st.session_state.project_data['project_details']['total_surcharges'] = total_surcharges
                    st.session_state.project_data['project_details']['final_modified_price_net'] = final_net_price_modified
                    st.session_state.project_data['project_details']['final_modified_price_gross'] = final_gross_price_modified
                    st.session_state.project_data['project_details']['final_modified_vat_amount'] = final_vat_amount
                    st.session_state.project_data['project_details']['formatted_final_modified_price_net'] = _format_german_currency(
                        final_net_price_modified)
                    st.session_state.project_data['project_details']['formatted_final_modified_price_gross'] = _format_german_currency(
                        final_gross_price_modified)
                    st.session_state.project_data['project_details']['formatted_final_modified_vat_amount'] = _format_german_currency(
                        final_vat_amount)
                else:
                    # Clear modification data if no modifications are applied
                    if 'project_data' in st.session_state and 'project_details' in st.session_state.project_data:
                        modification_keys = [
                            'discount_percent',
                            'rebates_eur',
                            'surcharge_percent',
                            'special_costs_eur',
                            'miscellaneous_eur',
                            'total_discounts',
                            'total_surcharges',
                            'final_modified_price',
                            'modified_net_price',
                            'modified_vat_amount',
                            'formatted_final_modified_price',
                            'formatted_modified_net_price']
                        for key in modification_keys:
                            st.session_state.project_data['project_details'].pop(
                                key, None)

                # Amortisationszeit-Berechnungen wurden in Ergebnisse &
                # Dashboard verschoben
                st.info(
                    "💡 **Hinweis:** Amortisationszeit-Berechnungen sind jetzt im Bereich 'Ergebnisse & Dashboard' verfügbar.")

            # Generate comprehensive PDF bytes for all pricing data
            if pricing_display.get("dynamic_keys"):
                try:
                    # Create PDF-ready data structure
                    pdf_pricing_data = {
                        "timestamp": datetime.now().isoformat(),
                        "totals": {
                            "hardware": {
                                "amount": hardware_total,
                                "formatted": pricing_display["formatted_hardware_total"],
                                "count": sum(
                                    len(
                                        cat_data["components"]) for cat_name,
                                    cat_data in pricing_display.get(
                                        "display_components_by_category",
                                        {}).items() if cat_name != "Dienstleistungen")},
                            "services": {
                                "amount": services_total,
                                "formatted": pricing_display["formatted_services_total"],
                                "count": len(
                                    pricing_display.get(
                                        "display_components_by_category",
                                        {}).get(
                                        "Dienstleistungen",
                                        {}).get(
                                            "components",
                                            []))},
                            "net": {
                                "amount": net_total,
                                "formatted": pricing_display["formatted_net_total"]},
                            "vat": {
                                "amount": vat_amount,
                                "formatted": pricing_display["formatted_vat_amount"],
                                "rate": 19.0},
                            "gross": {
                                "amount": gross_total,
                                "formatted": pricing_display["formatted_gross_total"]}},
                        "components": [],
                        "dynamic_keys": pricing_display["dynamic_keys"]}

                    # Add all components with their details (active ones)
                    for category, category_data in pricing_display.get(
                            "display_components_by_category", {}).items():
                        for comp in category_data["components"]:
                            pdf_pricing_data["components"].append({
                                "name": comp["name"],
                                "type": comp["type"],
                                "category": category,
                                "quantity": comp["quantity"],
                                "unit_price": comp["formatted_unit_price"],
                                "total_price": comp["formatted_total_price"],
                                "brand": comp.get("brand", ""),
                                "is_service": comp.get("is_service", False),
                                "is_standard": comp.get("is_standard", False),
                                "is_active": True,  # These are the active components
                                "calculate_per": comp.get("calculate_per", "Stück")
                            })

                    # Add ALL available services (including inactive optional
                    # ones) for PDF flexibility
                    try:
                        from services_integration import (
                            get_service_quantity,
                            get_services_for_calculation,
                        )

                        all_available_services = get_services_for_calculation()
                        all_services_list = all_available_services['standard'] + \
                            all_available_services['optional']

                        pdf_pricing_data["all_available_services"] = []

                        for service in all_services_list:
                            quantity = get_service_quantity(service, details)
                            total_price = service['price'] * quantity

                            # Determine if service is currently active
                            # Standard services are always active
                            is_active = service['is_standard']
                            if not is_active:
                                # Check if optional service is selected (would
                                # need to check session state)
                                is_active = False  # For now, mark optional as inactive by default

                            pdf_pricing_data["all_available_services"].append({
                                "id": service['id'],
                                "name": service['name'],
                                "description": service.get('description', ''),
                                "category": service.get('category', ''),
                                "price": service['price'],
                                "quantity": quantity,
                                "calculate_per": service['calculate_per'],
                                "total_price": total_price,
                                "formatted_price": _format_german_currency(service['price']),
                                "formatted_total": _format_german_currency(total_price),
                                "is_standard": service['is_standard'],
                                "is_active": is_active,
                                "pdf_order": service.get('pdf_order', 0)
                            })

                    except ImportError:
                        pass

                    # Convert to JSON bytes for PDF integration
                    import json
                    pdf_bytes = json.dumps(
                        pdf_pricing_data,
                        ensure_ascii=False,
                        indent=2).encode('utf-8')

                    # Store PDF bytes in session state
                    if hasattr(st, 'session_state'):
                        st.session_state["solar_calculator_pdf_bytes"] = pdf_bytes
                        st.session_state["solar_calculator_pdf_data"] = pdf_pricing_data

                    # Add to pricing display
                    pricing_display["pdf_bytes"] = pdf_bytes
                    pricing_display["pdf_data"] = pdf_pricing_data

                except Exception as e:
                    print(f"Warning: Could not generate PDF bytes: {e}")

            # FINALE PREISLOGIK FÜR PDF - Bestimme den finalen Angebotspreis
            # Priorität: Preisänderungen > Provision > Basis-Angebotspreis
            final_offer_price_net = None
            final_offer_price_gross = None
            final_offer_price_source = "basis"

            # 1. Basis: Net Total aus Pricing Display
            if pricing_display.get('net_total'):
                final_offer_price_net = pricing_display['net_total']
                final_offer_price_gross = pricing_display.get(
                    'gross_total', final_offer_price_net * 1.19)
                final_offer_price_source = "basis"

            # 2. Mit Provision (falls vorhanden)
            if provision_percent > 0 or provision_euro > 0:
                if final_offer_price_net:
                    provision_percent_amount = final_offer_price_net * \
                        (provision_percent / 100.0)
                    total_provision_amount = provision_percent_amount + provision_euro
                    final_offer_price_net = final_offer_price_net + total_provision_amount
                    final_offer_price_gross = final_offer_price_net * 1.19
                    final_offer_price_source = "provision"

            # 3. Mit Preisänderungen (falls vorhanden) - höchste Priorität
            if (discount_percent > 0 or rebates_eur > 0 or surcharge_percent >
                    0 or special_costs_eur > 0 or miscellaneous_eur > 0):
                # Verwende die bereits berechneten Werte aus der
                # Preisänderungen-Sektion
                if 'final_net_price_modified' in locals():
                    final_offer_price_net = final_net_price_modified
                    final_offer_price_gross = final_gross_price_modified
                    final_offer_price_source = "modifications"

            # Speichere den finalen Angebotspreis in Session State für PDF
            if final_offer_price_net is not None:
                if 'project_data' not in st.session_state:
                    st.session_state.project_data = {}
                if 'project_details' not in st.session_state.project_data:
                    st.session_state.project_data['project_details'] = {}

                # Finale Preise für PDF
                st.session_state.project_data['project_details']['final_offer_price_net'] = final_offer_price_net
                st.session_state.project_data['project_details']['final_offer_price_gross'] = final_offer_price_gross
                st.session_state.project_data['project_details']['final_offer_price_source'] = final_offer_price_source
                st.session_state.project_data['project_details']['formatted_final_offer_price_net'] = _format_german_currency(
                    final_offer_price_net)
                st.session_state.project_data['project_details']['formatted_final_offer_price_gross'] = _format_german_currency(
                    final_offer_price_gross)

                # Debug-Info (kann später entfernt werden)
                st.info(
                    f"📄 **PDF-Preis bestimmt:** {
                        _format_german_currency(final_offer_price_net)} (netto) / {
                        _format_german_currency(final_offer_price_gross)} (brutto) - Quelle: {final_offer_price_source}")

            # Remove the duplicate dynamic pricing summary - we already show
            # the correct one above

            # Display by category if available - only show active components
            if pricing_display.get("display_components_by_category"):
                for category, category_data in pricing_display["display_components_by_category"].items(
                ):
                    # Filter components: Show all hardware, all standard
                    # services, only active optional services
                    active_components = []
                    for comp in category_data["components"]:
                        if comp.get("is_service", False):
                            # For services: show all standard services (even
                            # 0€), only active optional services
                            if comp.get("is_standard", False):
                                # Standard services are always shown (even if
                                # 0€)
                                active_components.append(comp)
                            elif comp.get("total_price", 0) > 0:
                                # Optional services only if they have a price >
                                # 0
                                active_components.append(comp)
                        else:
                            # For hardware, always show
                            active_components.append(comp)

                    if active_components:
                        st.markdown(f"#### {category}")

                        # Create category pricing table with only active
                        # components
                        category_pricing_data = []
                        for comp in active_components:
                            row = {
                                "Komponente": comp["name"],
                                "Typ": comp["type"],
                                "Anzahl": comp["quantity"],
                                "Berechnungsart": comp["calculate_per"],
                                "Einzelpreis": comp["formatted_unit_price"],
                                "Gesamtpreis": comp["formatted_total_price"]
                            }

                            # Add additional info for optional components
                            if comp.get("is_optional", False):
                                row["Status"] = "Optional"
                            if comp.get("brand"):
                                row["Hersteller"] = comp["brand"]

                            category_pricing_data.append(row)

                        if category_pricing_data:
                            st.table(category_pricing_data)
                            st.markdown(
                                f"**{category} Summe: {category_data['formatted_category_total']}**")
                            st.markdown("---")
            else:
                # Fallback to simple table if categorization not available
                pricing_data = []
                for comp in pricing_display["display_components"]:
                    pricing_data.append({
                        "Komponente": comp["name"],
                        "Typ": comp["type"],
                        "Anzahl": comp["quantity"],
                        "Berechnungsart": comp["calculate_per"],
                        "Einzelpreis": comp["formatted_unit_price"],
                        "Gesamtpreis": comp["formatted_total_price"]
                    })

                if pricing_data:
                    st.table(pricing_data)

            # Update session state with pricing data
            update_pricing_in_session_state(details)

            # Show enhanced calculation method info and accessory rules
            with st.expander("ℹ️ Preisberechnung & Zusatzkomponenten"):
                st.markdown("**Berechnungsmethoden:**")
                st.markdown("""
                - **Stück**: Preis pro Einzelteil (z.B. Module, Wechselrichter)
                - **Meter**: Preis pro Meter (z.B. Kabel, Montagesysteme)
                - **pauschal**: Pauschaler Preis unabhängig von der Menge (z.B. Dienstleistungen)
                - **kWp**: Preis pro Kilowattpeak Anlagenleistung
                """)

                st.markdown("**Zusatzkomponenten:**")
                st.markdown("""
                - **Wallboxen**: Unterstützen Mengenauswahl (bis zu 20 Stück)
                - **Leistungsoptimierer**: Mengenauswahl basierend auf Modulanzahl
                - **Energiemanagementsysteme**: Typischerweise 1 Stück pro Anlage
                - **Carports**: Individuelle Konfiguration mit Baugenehmigung
                - **Notstromversorgung**: Systemabhängige Installation
                - **Tierabwehrschutz**: Modulabhängige Berechnung
                - **Sonstige Komponenten**: Freie Preiseingabe für individuelle Anforderungen
                """)

                # Show component count summary
                total_components = pricing_display.get("component_count", 0)
                optional_components = pricing_display.get(
                    "optional_component_count", 0)
                main_components = total_components - optional_components

                st.markdown(
                    f"**Komponentenübersicht:** {main_components} Hauptkomponenten, {optional_components} Zusatzkomponenten")

    except Exception as e:
        st.error(f"Fehler bei der Preisberechnung: {e}")


def _trigger_pricing_update(details: dict[str, Any]) -> None:
    """Trigger pricing update when component selection changes"""
    if not PRICING_INTEGRATION_AVAILABLE:
        return

    try:
        # Update pricing in session state
        update_pricing_in_session_state(details)

        # Clear any cached pricing data when selections change
        solar_pricing_integration.clear_pricing_cache()

    except Exception as e:
        print(f"Error triggering pricing update: {e}")


def _ensure_project_data_dicts():
    if 'project_data' not in st.session_state:
        st.session_state.project_data = {}
    pd = st.session_state.project_data
    if 'project_details' not in pd:
        pd['project_details'] = {}
    if 'customer_data' not in pd:
        pd['customer_data'] = {}
    if 'economic_data' not in pd:
        pd['economic_data'] = {}
    return pd


def _product_names_by_category(
        category: str, texts: dict[str, str]) -> list[str]:
    try:
        products = list_products_safe(category=category)
        names = [
            p.get(
                'model_name',
                f"ID:{
                    p.get(
                        'id',
                        'N/A')}") for p in products]
        if not names:
            return [
                _get_text(texts, {
                    'Modul': 'no_modules_in_db',
                    'Wechselrichter': 'no_inverters_in_db',
                    'Batteriespeicher': 'no_storages_in_db',
                    'Wallbox': 'no_wallboxes_in_db',
                    'Energiemanagementsystem': 'no_ems_in_db',
                    'Leistungsoptimierer': 'no_optimizers_in_db',
                    'Carport': 'no_carports_in_db',
                    'Notstromversorgung': 'no_notstrom_in_db',
                    'Tierabwehrschutz': 'no_tierabwehr_in_db',
                }.get(category, 'no_products_in_db'), 'Keine Produkte in DB')
            ]
        return names
    except Exception:
        return []


def render_solar_calculator(
        texts: dict[str, str], module_name: str | None = None) -> None:
    """Erweiterter Solar Calculator mit 2-Schritt Wizard.

    Schritt 1: Kerntechnik (Module, Wechselrichter, Speicher)
    Schritt 2: Zusatzkomponenten
    Abschluss: 'Berechnungen Starten' -> Navigation zurück (Standard: 'analysis')

    Wichtige Anforderungen (User Story):
    - Anzahl PV Module: freie Eingabe + separate + / - Buttons
    - Hersteller-/Modell-Filter für Module, Wechselrichter, Speicher
    - Automatische kWp Berechnung: qty * module_capacity_w / 1000
    - Automatische Anzeige WR-Leistung (W) und Speicher-Kapazität (kWh)
    - Optionaler Speicherbereich per Checkbox
    - Zusatzkomponenten als eigener Schritt mit optionaler Aktivierung
    - Freies Feld 'sonstiges'
    """
    pd = _ensure_project_data_dicts()
    details: dict[str, Any] = pd['project_details']

    please_select_text = _get_text(
        texts,
        'please_select_option',
        '--- Bitte wählen ---')

    # Wizard Step State
    if 'solar_calc_step' not in st.session_state:
        st.session_state['solar_calc_step'] = 1
    step = st.session_state['solar_calc_step']

    # Hilfsfunktionen
    def _products_by_category(category: str) -> list[dict[str, Any]]:
        try:
            return list_products_safe(category=category)  # type: ignore
        except Exception:
            return []

    def _brands_from_products(products: list[dict[str, Any]]) -> list[str]:
        brands = sorted({(p.get('brand') or '').strip()
                        for p in products if p.get('brand')})
        return brands

    def _filter_models_by_brand(
            products: list[dict[str, Any]], brand: str | None) -> list[dict[str, Any]]:
        if not brand:
            return products
        return [
            p for p in products if (
                p.get('brand') or '').strip().lower() == brand.strip().lower()]

    # Sichtbare Version / Build Tag zur Kontrolle, dass neue Datei wirklich
    # geladen wurde
    VERSION_TAG = "SolarCalcWizard-2025-09-05-v1"
    st.caption(f"Solar Calculator – Schritt {step} / 2 | Build: {VERSION_TAG}")

    # Optionaler Debug-Block zur Fehlersuche falls Nutzer nur Minimal-UI sieht
    with st.expander("Debug (nur vorübergehend) ", expanded=False):
        st.write(
            {
                'step': step,
                'module_qty_state': st.session_state.get('module_quantity_sc_v1'),
                'details_keys': sorted(
                    list(
                        details.keys())),
                'have_products_modul': len(
                    list_products_safe(
                        category='Modul')) if callable(list_products_safe) else 'n/a',
                'have_products_wr': len(
                    list_products_safe(
                        category='Wechselrichter')) if callable(list_products_safe) else 'n/a',
                'have_products_storage': len(
                    list_products_safe(
                        category='Batteriespeicher')) if callable(list_products_safe) else 'n/a',
            })
        st.info("Falls hier 0 Produkte angezeigt werden, fehlen Einträge in der Produktdatenbank (Kategorie: 'Modul', 'Wechselrichter', 'Batteriespeicher').")

    if step == 1:
        st.subheader(
            _get_text(
                texts,
                'technology_selection_header',
                'Auswahl der Technik'))

        # --- MODULE ---
        module_products = _products_by_category('Modul')
        module_brands = _brands_from_products(module_products)

        cols_mod_top = st.columns([1, 1, 2])
        with cols_mod_top[0]:
            # Anzahl Module mit + / - Buttons
            # Sichere Initialisierung: Falls Key noch nicht gesetzt wurde
            if 'module_quantity_sc_v1' not in st.session_state:
                st.session_state['module_quantity_sc_v1'] = int(
                    details.get('module_quantity', 20) or 20)

            # Wir arbeiten mit einer lokalen Variable und schreiben am Ende
            # zurück
            local_qty = int(
                st.session_state.get(
                    'module_quantity_sc_v1',
                    0) or 0)

            # Anzeige des aktuellen Werts (read-only) + Zahleneingabe via
            # separate number_input ohne gleichen Key Konflikt
            new_qty = st.number_input(
                _get_text(texts, 'module_quantity_label', 'Anzahl PV Module'),
                min_value=0,
                value=local_qty,
                key='module_quantity_sc_v1_input'
            )

            # Buttons unterhalb für inkrement/dekrement
            col_btn_minus, col_btn_plus = st.columns(2)
            with col_btn_minus:
                if st.button('−', key='btn_module_qty_minus'):
                    local_qty = max(0, local_qty - 1)
            with col_btn_plus:
                if st.button('+', key='btn_module_qty_plus'):
                    local_qty = local_qty + 1

            # Priorität: Button-Anpassungen > direkte Eingabe
            if new_qty != st.session_state.get('module_quantity_sc_v1'):
                # Nutzer hat direkt im number_input geändert
                local_qty = int(new_qty)

            # Nur einmal schreiben (nach Widgets), um Streamlit Mutation nach
            # Instanziierung zu vermeiden
            st.session_state['module_quantity_sc_v1'] = int(local_qty)
            details['module_quantity'] = int(local_qty)
        with cols_mod_top[1]:
            # Hersteller Auswahl
            current_brand = details.get(
                'selected_module_brand') or please_select_text
            brand_options = [please_select_text] + module_brands
            try:
                idx_brand = brand_options.index(current_brand)
            except ValueError:
                idx_brand = 0
            selected_brand = st.selectbox(
                _get_text(texts, 'module_brand_label', 'PV Modul Hersteller'),
                options=brand_options,
                index=idx_brand,
                key='selected_module_brand_sc_v1'
            )
            details['selected_module_brand'] = selected_brand if selected_brand != please_select_text else None
        with cols_mod_top[2]:
            # Modelle je Hersteller
            filtered_mods = _filter_models_by_brand(
                module_products, details.get('selected_module_brand'))
            model_names = [p.get('model_name')
                           for p in filtered_mods if p.get('model_name')]
            current_module = details.get(
                'selected_module_name', please_select_text)
            module_options = [please_select_text] + model_names
            try:
                idx_mod = module_options.index(current_module)
            except ValueError:
                idx_mod = 0
            selected_module = st.selectbox(
                _get_text(texts, 'module_model_label', 'PV Modul Modell'),
                options=module_options,
                index=idx_mod,
                key='selected_module_name_sc_v1'
            )
            details['selected_module_name'] = selected_module if selected_module != please_select_text else None
            if details.get('selected_module_name'):
                md = get_product_by_model_name_safe(
                    details['selected_module_name'])
                if md:
                    details['selected_module_id'] = md.get('id')
                    details['selected_module_capacity_w'] = float(
                        md.get('capacity_w', 0.0) or 0.0)
                else:
                    details['selected_module_id'] = None
                    details['selected_module_capacity_w'] = 0.0
            else:
                details['selected_module_id'] = None
                details['selected_module_capacity_w'] = 0.0

        if details.get('selected_module_capacity_w', 0.0) > 0:
            st.info(
                f"{
                    _get_text(
                        texts,
                        'module_capacity_label',
                        'Leistung pro Modul (Wp)')}: {
                    details['selected_module_capacity_w']:.0f} Wp")

        # Anlagengröße (kWp)
        anlage_kwp = ((details.get('module_quantity', 0) or 0) *
                      (details.get('selected_module_capacity_w', 0.0) or 0.0)) / 1000.0
        details['anlage_kwp'] = anlage_kwp
        st.info(f"{_get_text(texts,
                             'anlage_size_label',
                             'Anlagengröße (kWp)')}: {anlage_kwp:.2f} kWp")

        # Trigger pricing update for modules
        _trigger_pricing_update(details)

        # --- WECHSELRICHTER ---
        inverter_products = _products_by_category('Wechselrichter')
        inverter_brands = _brands_from_products(inverter_products)
        st.markdown('---')
        st.markdown('### Wechselrichter')
        cols_inv_top = st.columns([1, 2, 1])
        with cols_inv_top[0]:
            current_inv_brand = details.get(
                'selected_inverter_brand') or please_select_text
            inv_brand_options = [please_select_text] + inverter_brands
            try:
                idx_inv_brand = inv_brand_options.index(current_inv_brand)
            except ValueError:
                idx_inv_brand = 0
            selected_inv_brand = st.selectbox(
                _get_text(
                    texts,
                    'inverter_brand_label',
                    'Wechselrichter Hersteller'),
                options=inv_brand_options,
                index=idx_inv_brand,
                key='selected_inverter_brand_sc_v1')
            details['selected_inverter_brand'] = selected_inv_brand if selected_inv_brand != please_select_text else None
        with cols_inv_top[1]:
            filtered_inv = _filter_models_by_brand(
                inverter_products, details.get('selected_inverter_brand'))
            inv_model_names = [p.get('model_name')
                               for p in filtered_inv if p.get('model_name')]
            current_inv_model = details.get(
                'selected_inverter_name', please_select_text)
            inv_model_options = [please_select_text] + inv_model_names
            try:
                idx_inv_model = inv_model_options.index(current_inv_model)
            except ValueError:
                idx_inv_model = 0
            selected_inv_model = st.selectbox(
                _get_text(
                    texts,
                    'inverter_model_label',
                    'Wechselrichter Modell'),
                options=inv_model_options,
                index=idx_inv_model,
                key='selected_inverter_name_sc_v1')
            details['selected_inverter_name'] = selected_inv_model if selected_inv_model != please_select_text else None
        with cols_inv_top[2]:
            details['selected_inverter_quantity'] = int(st.number_input(
                _get_text(texts, 'inverter_quantity_label', 'Anzahl WR'),
                min_value=1,
                value=int(details.get('selected_inverter_quantity', 1) or 1),
                step=1,
                key='selected_inverter_quantity_sc_v1'
            ))

        base_inverter_power_kw = 0.0
        if details.get('selected_inverter_name'):
            invd = get_product_by_model_name_safe(
                details['selected_inverter_name'])
            if invd:
                details['selected_inverter_id'] = invd.get('id')
                base_inverter_power_kw = float(
                    invd.get('power_kw', 0.0) or 0.0)
            else:
                details['selected_inverter_id'] = None
        else:
            details['selected_inverter_id'] = None

        details['selected_inverter_power_kw_single'] = base_inverter_power_kw
        inv_qty = max(
            1, int(
                details.get(
                    'selected_inverter_quantity', 1) or 1))
        total_inverter_power_kw = base_inverter_power_kw * inv_qty
        details['selected_inverter_power_kw'] = total_inverter_power_kw
        details['selected_inverter_power_w_total'] = total_inverter_power_kw * 1000
        details['selected_inverter_power_w_single'] = base_inverter_power_kw * 1000

        try:
            st.session_state.project_data['inverter_power_kw'] = total_inverter_power_kw
        except Exception:
            pass

        if total_inverter_power_kw > 0:
            st.info(
                f"{
                    _get_text(
                        texts,
                        'inverter_power_label',
                        'Leistung WR gesamt')}: {
                    details['selected_inverter_power_w_total']:.0f} W")
            if inv_qty > 1 and base_inverter_power_kw > 0:
                st.caption(
                    f"{inv_qty} × {
                        base_inverter_power_kw *
                        1000:.0f} W je WR")

        # Trigger pricing update for inverters
        _trigger_pricing_update(details)

        # --- SPEICHER (optional) ---
        st.markdown('---')
        details['include_storage'] = st.checkbox(
            _get_text(
                texts,
                'include_storage_label',
                'Batteriespeicher einplanen'),
            value=bool(
                details.get(
                    'include_storage',
                    False)),
            key='include_storage_sc_v1')

        if details['include_storage']:
            storage_products = _products_by_category('Batteriespeicher')
            storage_brands = _brands_from_products(storage_products)
            cols_storage = st.columns([1, 2, 1])
            with cols_storage[0]:
                current_storage_brand = details.get(
                    'selected_storage_brand') or please_select_text
                storage_brand_options = [please_select_text] + storage_brands
                try:
                    idx_st_brand = storage_brand_options.index(
                        current_storage_brand)
                except ValueError:
                    idx_st_brand = 0
                selected_st_brand = st.selectbox(
                    _get_text(
                        texts,
                        'storage_brand_label',
                        'Speicher Hersteller'),
                    options=storage_brand_options,
                    index=idx_st_brand,
                    key='selected_storage_brand_sc_v1')
                details['selected_storage_brand'] = selected_st_brand if selected_st_brand != please_select_text else None
            with cols_storage[1]:
                filtered_storage = _filter_models_by_brand(
                    storage_products, details.get('selected_storage_brand'))
                storage_model_names = [
                    p.get('model_name') for p in filtered_storage if p.get('model_name')]
                current_storage_model = details.get(
                    'selected_storage_name', please_select_text)
                storage_model_options = [
                    please_select_text] + storage_model_names
                try:
                    idx_st_model = storage_model_options.index(
                        current_storage_model)
                except ValueError:
                    idx_st_model = 0
                selected_storage = st.selectbox(
                    _get_text(texts, 'storage_model_label', 'Speicher Modell'),
                    options=storage_model_options,
                    index=idx_st_model,
                    key='selected_storage_name_sc_v1'
                )
                details['selected_storage_name'] = selected_storage if selected_storage != please_select_text else None
            with cols_storage[2]:
                # Wunschkapazität
                default_cap = float(
                    details.get(
                        'selected_storage_storage_power_kw',
                        0.0) or 0.0)
                if details.get('selected_storage_name') and not default_cap:
                    std = get_product_by_model_name_safe(
                        details['selected_storage_name'])
                    if std:
                        default_cap = float(
                            std.get('storage_power_kw', 0.0) or 0.0)
                if default_cap == 0.0:
                    default_cap = 5.0
                details['selected_storage_storage_power_kw'] = st.number_input(
                    _get_text(
                        texts,
                        'storage_capacity_manual_label',
                        'Gewünschte Gesamtkapazität (kWh)'),
                    min_value=0.0,
                    value=default_cap,
                    step=0.1,
                    key='selected_storage_storage_power_kw_sc_v1')
            # Anzeige Modell Kapazität
            if details.get('selected_storage_name'):
                std = get_product_by_model_name_safe(
                    details['selected_storage_name'])
                if std:
                    cap_model = float(std.get('storage_power_kw', 0.0) or 0.0)
                    st.info(f"{_get_text(texts,
                                         'storage_capacity_model_label',
                                         'Kapazität Modell (kWh)')}: {cap_model:.2f} kWh")

            # Trigger pricing update for storage
            _trigger_pricing_update(details)
        else:
            details['selected_storage_name'] = None
            details['selected_storage_id'] = None
            details['selected_storage_storage_power_kw'] = 0.0

        # Display pricing information for step 1 components
        st.markdown('---')
        _display_pricing_information(details, texts)

        # Navigation -> Schritt 2
        st.markdown('---')
        col_nav1, col_nav2 = st.columns([3, 1])
        with col_nav2:
            if st.button(
                    _get_text(
                        texts,
                        'next_page_label',
                        'Nächste Seite'),
                    key='btn_to_step2_sc_v1'):
                st.session_state['solar_calc_step'] = 2
                st.rerun()

    elif step == 2:
        st.subheader(
            _get_text(
                texts,
                'additional_components_header',
                'Zusätzliche Komponenten'))
        # Zusatzkomponenten Produkte
        WALLBOXES = _product_names_by_category('Wallbox', texts)
        EMS = _product_names_by_category('Energiemanagementsystem', texts)
        OPTI = _product_names_by_category('Leistungsoptimierer', texts)
        CARPORT = _product_names_by_category('Carport', texts)
        NOTSTROM = _product_names_by_category('Notstromversorgung', texts)
        TIERABWEHR = _product_names_by_category('Tierabwehrschutz', texts)

        details['include_additional_components'] = st.checkbox(
            _get_text(
                texts,
                'include_additional_components_label',
                'Zusätzliche Komponenten einplanen'),
            value=bool(
                details.get(
                    'include_additional_components',
                    False)),
            key='include_additional_components_sc_v1')

        def _component_selector_with_pricing(
                label_key: str,
                options: list[str],
                name_key: str,
                id_key: str,
                widget_key: str,
                quantity_key: str = None):
            """Enhanced component selector with pricing display and quantity selection"""
            fallback_labels = {
                'wallbox_model_label': 'Wallbox | E-Ladestationen',
                'ems_model_label': 'Energiemanagementsysteme',
                'optimizer_model_label': 'Leistungsoptimierer',
                'carport_model_label': 'Solar CarPorts',
                'notstrom_model_label': 'Notstromversorgungen',
                'tierabwehr_model_label': 'Tierabwehrschutz',
            }

            # Create columns for component selection and quantity
            if quantity_key:
                col1, col2, col3 = st.columns([3, 1, 2])
            else:
                col1, col2 = st.columns([4, 2])
                col3 = None

            with col1:
                current_val = details.get(name_key, please_select_text)
                opts = [please_select_text] + options
                try:
                    idx = opts.index(current_val)
                except ValueError:
                    idx = 0
                label_text = _get_text(
                    texts, label_key, fallback_labels.get(
                        label_key, label_key))
                sel = st.selectbox(
                    label_text,
                    options=opts,
                    index=idx,
                    key=widget_key)
                details[name_key] = sel if sel != please_select_text else None

                if details.get(name_key):
                    comp = get_product_by_model_name_safe(details[name_key])
                    details[id_key] = comp.get('id') if comp else None
                else:
                    details[id_key] = None

            # Quantity selection for accessories that support it
            if col3 and quantity_key and details.get(name_key):
                with col2:
                    current_qty = int(details.get(quantity_key, 1))
                    new_qty = st.number_input(
                        "Anzahl",
                        min_value=1,
                        max_value=20,
                        value=current_qty,
                        step=1,
                        key=f"{widget_key}_qty"
                    )
                    details[quantity_key] = new_qty

            # Display pricing information for selected component
            if details.get(name_key) and col3:
                with col3:
                    comp = get_product_by_model_name_safe(details[name_key])
                    if comp:
                        try:
                            # Get pricing information
                            from product_db import calculate_selling_price
                            margin_info = calculate_selling_price(comp["id"])

                            if margin_info and margin_info.get(
                                    "selling_price_net", 0) > 0:
                                unit_price = margin_info["selling_price_net"]
                            else:
                                unit_price = float(comp.get("price_euro", 0.0))

                            calculate_per = comp.get("calculate_per", "Stück")
                            quantity = details.get(
                                quantity_key, 1) if quantity_key else 1

                            # Calculate total price based on calculate_per
                            # method
                            from product_db import calculate_price_by_method
                            total_price = calculate_price_by_method(
                                base_price=unit_price,
                                quantity=quantity,
                                calculate_per=calculate_per,
                                product_specs=comp
                            )

                            # Display pricing info
                            st.caption(
                                f"💰 {
                                    unit_price:.2f} € ({calculate_per})")
                            if quantity > 1:
                                st.caption(f"Gesamt: {total_price:.2f} €")

                        except Exception:
                            st.caption("⚠️ Preis nicht verfügbar")
            elif details.get(name_key) and not col3:
                # Simple pricing display without quantity
                comp = get_product_by_model_name_safe(details[name_key])
                if comp:
                    try:
                        from product_db import calculate_selling_price
                        margin_info = calculate_selling_price(comp["id"])

                        if margin_info and margin_info.get(
                                "selling_price_net", 0) > 0:
                            unit_price = margin_info["selling_price_net"]
                        else:
                            unit_price = float(comp.get("price_euro", 0.0))

                        calculate_per = comp.get("calculate_per", "Stück")
                        st.caption(f"💰 {unit_price:.2f} € ({calculate_per})")

                    except Exception:
                        st.caption("⚠️ Preis nicht verfügbar")

        if details['include_additional_components']:
            st.markdown("#### 🔌 Ladeinfrastruktur")
            _component_selector_with_pricing(
                'wallbox_model_label',
                WALLBOXES,
                'selected_wallbox_name',
                'selected_wallbox_id',
                'sel_wallbox_sc_v1',
                'selected_wallbox_quantity')

            st.markdown("#### ⚡ Energiemanagement")
            _component_selector_with_pricing(
                'ems_model_label',
                EMS,
                'selected_ems_name',
                'selected_ems_id',
                'sel_ems_sc_v1')
            _component_selector_with_pricing(
                'optimizer_model_label',
                OPTI,
                'selected_optimizer_name',
                'selected_optimizer_id',
                'sel_opti_sc_v1',
                'selected_optimizer_quantity')

            st.markdown("#### 🏠 Bauliche Erweiterungen")
            _component_selector_with_pricing(
                'carport_model_label',
                CARPORT,
                'selected_carport_name',
                'selected_carport_id',
                'sel_cp_sc_v1')

            st.markdown("#### 🔋 Zusätzliche Systeme")
            _component_selector_with_pricing(
                'notstrom_model_label',
                NOTSTROM,
                'selected_notstrom_name',
                'selected_notstrom_id',
                'sel_not_sc_v1')

            st.markdown("#### 🛡️ Schutz & Sicherheit")
            _component_selector_with_pricing(
                'tierabwehr_model_label',
                TIERABWEHR,
                'selected_tierabwehr_name',
                'selected_tierabwehr_id',
                'sel_ta_sc_v1')

            # Initialize quantity fields if not present
            if 'selected_wallbox_quantity' not in details:
                details['selected_wallbox_quantity'] = 1
            if 'selected_optimizer_quantity' not in details:
                details['selected_optimizer_quantity'] = 1

            # Freies Feld Sonstiges mit Preiseingabe
            st.markdown("#### ✏️ Sonstige Komponenten")
            col_other1, col_other2 = st.columns([3, 1])
            with col_other1:
                details['additional_other_custom'] = st.text_input(
                    _get_text(
                        texts,
                        'additional_other_label',
                        'Sonstiges (Beschreibung)'),
                    value=details.get(
                        'additional_other_custom',
                        ''),
                    max_chars=120,
                    key='additional_other_custom_sc_v1')
            with col_other2:
                if details.get('additional_other_custom'):
                    details['additional_other_price'] = st.number_input(
                        "Preis (€)",
                        min_value=0.0,
                        value=float(
                            details.get(
                                'additional_other_price',
                                0.0)),
                        step=10.0,
                        key='additional_other_price_sc_v1')
                else:
                    details['additional_other_price'] = 0.0

            # Trigger pricing update for additional components
            _trigger_pricing_update(details)

        # Display complete pricing information including additional components
        if details.get('include_additional_components', False):
            st.markdown('---')
            _display_pricing_information(details, texts)

        st.markdown('---')
        col_back, col_spacer, col_finish = st.columns([1, 3, 1])
        with col_back:
            if st.button(
                    _get_text(
                        texts,
                        'back_label',
                        'Zurück'),
                    key='btn_back_step1_sc_v1'):
                st.session_state['solar_calc_step'] = 1
                st.rerun()
        with col_finish:
            if st.button(
                    _get_text(
                        texts,
                        'start_calculations_label',
                        'Berechnungen Starten'),
                    key='btn_finish_sc_v1'):
                # Navigation zurück in Analysebereich (Annahme: 'analysis')
                # Falls anderes Ziel erwünscht, Key hier ändern.
                st.success(
                    _get_text(
                        texts,
                        'tech_selection_saved_info',
                        'Technik-Auswahl übernommen.'))
                try:
                    st.session_state['selected_page_key'] = 'analysis'
                except Exception:
                    pass
                # Reset für nächsten Aufruf
                st.session_state['solar_calc_step'] = 1
                st.rerun()

    # Abschluss Hinweis (nur Schritt 1 zeigt fortlaufend Info, Schritt 2 via
    # Button)
    if step == 1:
        st.caption(
            _get_text(
                texts,
                'tech_selection_saved_info',
                'Änderungen werden automatisch gespeichert.'))
