"""
solar_calculator.py

Enhanced Solar Calculator with integrated pricing system.
Separater Menüpunkt für die Auswahl der Technik (Module, WR, Speicher, Zusatzkomponenten).
Verwendet die gleichen Keys in st.session_state.project_data['project_details'] wie data_input,
damit Analyse und PDF weiterhin funktionieren.

Enhanced with real-time pricing calculations and calculate_per support.
"""

from __future__ import annotations

import contextlib
from typing import Any

import streamlit as st
try:
    # Für Session-Liveness-Prüfung (None außerhalb von streamlit run)
    from streamlit.runtime.scriptrunner import get_script_run_ctx  # type: ignore
except Exception:  # pragma: no cover
    def get_script_run_ctx():  # type: ignore
        return None

def _is_session_alive() -> bool:
    """Prüft, ob eine aktive Streamlit-Session vorhanden ist.

    Verhindert UI-Schreiboperationen (st.write, st.markdown, ...),
    wenn der WebSocket/Session bereits beendet wurde.
    """
    try:
        return get_script_run_ctx() is not None
    except Exception:
        return False

# Globale, zentrale Absicherung für Streamlit-UI-Funktionen in diesem Modul.
# Wir patchen häufig genutzte st.* Aufrufe, um WebSocketClosedError & Co.
# zentral abzufangen und sinnvolle Fallbacks zu liefern, wenn die Session
# nicht mehr aktiv ist.
_ST_PATCHED = False
_ST_ORIG: dict[str, any] = {}


class _NoOpContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    # No-Op UI Methoden
    def write(self, *args, **kwargs):
        return None

    def markdown(self, *args, **kwargs):
        return None

    def text(self, *args, **kwargs):
        return None

    def caption(self, *args, **kwargs):
        return None

    def subheader(self, *args, **kwargs):
        return None

    def header(self, *args, **kwargs):
        return None

    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None

    def success(self, *args, **kwargs):
        return None


def _patch_streamlit_ui_safeguards():
    global _ST_PATCHED
    if _ST_PATCHED:
        return
    try:
        # Speichere Originale nur einmal
        for name in (
            'write', 'markdown', 'text', 'caption', 'subheader', 'header',
            'info', 'warning', 'error', 'success',
            'columns', 'expander', 'number_input', 'slider', 'selectbox',
            'toggle', 'text_area', 'button'
        ):
            if name in _ST_ORIG:
                continue
            _ST_ORIG[name] = getattr(st, name, None)

        def safe_call(name, *args, **kwargs):
            fn = _ST_ORIG.get(name)
            if not callable(fn):
                return None
            try:
                if not _is_session_alive():
                    # Session ist nicht aktiv → Fallback
                    return _fallback_for(name, *args, **kwargs)
                return fn(*args, **kwargs)
            except Exception as e:  # z.B. WebSocketClosedError
                try:
                    debug_log("solar_calculator.ui", f"safe_{name} unterdrückt Fehler", error=str(e))
                except Exception:
                    pass
                return _fallback_for(name, *args, **kwargs)

        # Wrapper je Funktion setzen
        for name in ('write', 'markdown', 'text', 'caption', 'subheader', 'header', 'info', 'warning', 'error', 'success'):
            if _ST_ORIG.get(name):
                setattr(st, name, lambda *a, __n=name, **k: safe_call(__n, *a, **k))

        # columns: muss Liste von Context-Managern liefern
        def safe_columns(*args, **kwargs):
            # Ermittele Zahl der Spalten
            count = 1
            if args:
                spec = args[0]
                if isinstance(spec, int):
                    count = spec
                elif isinstance(spec, (list, tuple)):
                    count = len(spec)
            if _is_session_alive() and callable(_ST_ORIG.get('columns')):
                try:
                    return _ST_ORIG['columns'](*args, **kwargs)
                except Exception:
                    pass
            # Fallback: No-Op Columns
            return [_NoOpContext() for _ in range(max(1, int(count)))]

        if _ST_ORIG.get('columns'):
            st.columns = safe_columns  # type: ignore

        # expander: muss Context-Manager liefern
        def safe_expander(*args, **kwargs):
            if _is_session_alive() and callable(_ST_ORIG.get('expander')):
                try:
                    return _ST_ORIG['expander'](*args, **kwargs)
                except Exception:
                    pass
            return _NoOpContext()

        if _ST_ORIG.get('expander'):
            st.expander = safe_expander  # type: ignore

        # Interaktive Widgets mit sinnvollen Defaults
        def safe_number_input(*args, **kwargs):
            if _is_session_alive() and callable(_ST_ORIG.get('number_input')):
                try:
                    return _ST_ORIG['number_input'](*args, **kwargs)
                except Exception:
                    pass
            # Fallback: gebe den übergebenen Default-Wert zurück
            if 'value' in kwargs:
                return kwargs['value']
            # versuche positional default (selten genutzt, aber der Vollständigkeit halber)
            return 0

        if _ST_ORIG.get('number_input'):
            st.number_input = safe_number_input  # type: ignore

        def safe_slider(*args, **kwargs):
            if _is_session_alive() and callable(_ST_ORIG.get('slider')):
                try:
                    return _ST_ORIG['slider'](*args, **kwargs)
                except Exception:
                    pass
            return kwargs.get('value', 0)

        if _ST_ORIG.get('slider'):
            st.slider = safe_slider  # type: ignore

        def safe_selectbox(*args, **kwargs):
            if _is_session_alive() and callable(_ST_ORIG.get('selectbox')):
                try:
                    return _ST_ORIG['selectbox'](*args, **kwargs)
                except Exception:
                    pass
            options = []
            if 'options' in kwargs:
                options = kwargs['options']
            elif args:
                # signatur: label, options, index=0, ...
                try:
                    options = args[1]
                except Exception:
                    options = []
            if isinstance(options, (list, tuple)) and options:
                idx = kwargs.get('index', 0)
                try:
                    return options[idx]
                except Exception:
                    return options[0]
            return None

        if _ST_ORIG.get('selectbox'):
            st.selectbox = safe_selectbox  # type: ignore

        def safe_toggle(*args, **kwargs):
            if _is_session_alive() and callable(_ST_ORIG.get('toggle')):
                try:
                    return _ST_ORIG['toggle'](*args, **kwargs)
                except Exception:
                    pass
            return kwargs.get('value', False)

        if _ST_ORIG.get('toggle'):
            st.toggle = safe_toggle  # type: ignore

        def safe_text_area(*args, **kwargs):
            if _is_session_alive() and callable(_ST_ORIG.get('text_area')):
                try:
                    return _ST_ORIG['text_area'](*args, **kwargs)
                except Exception:
                    pass
            return kwargs.get('value', "")

        if _ST_ORIG.get('text_area'):
            st.text_area = safe_text_area  # type: ignore

        def safe_button(*args, **kwargs):
            if _is_session_alive() and callable(_ST_ORIG.get('button')):
                try:
                    return _ST_ORIG['button'](*args, **kwargs)
                except Exception:
                    pass
            return False

        if _ST_ORIG.get('button'):
            st.button = safe_button  # type: ignore

        _ST_PATCHED = True
    except Exception as e:
        # Falls Patching fehlschlägt, läuft der Code weiter mit Originalen
        try:
            debug_log("solar_calculator.ui", "Patching st.* fehlgeschlagen", error=str(e))
        except Exception:
            pass


def _fallback_for(name: str, *args, **kwargs):
    # zentrale Fallbacks für häufige UI-Funktionen
    if name == 'columns':
        # handled in safe_columns
        return [_NoOpContext()]
    if name == 'expander':
        return _NoOpContext()
    if name == 'number_input':
        return kwargs.get('value', 0)
    if name == 'slider':
        return kwargs.get('value', 0)
    if name == 'selectbox':
        options = kwargs.get('options', [])
        if isinstance(options, (list, tuple)) and options:
            try:
                return options[kwargs.get('index', 0)]
            except Exception:
                return options[0]
        return None
    if name == 'toggle':
        return kwargs.get('value', False)
    if name == 'text_area':
        return kwargs.get('value', "")
    if name == 'button':
        return False
    # write/markdown/etc. → No-Op
    return None


# Patching sofort aktivieren (idempotent)
_patch_streamlit_ui_safeguards()

from debug_tools import (
    debug_log,
    init_debug_mode,
    render_debug_toolbar,
)
from emoji_toggle import initialize_emoji_support
from financial_calculations import (
    calculate_gross_from_net,
    calculate_vat_amount,
)

initialize_emoji_support()

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
        except Exception:
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

    # Session-Liveness-Guard: Keine UI-Updates nach Session-Ende
    if not _is_session_alive():
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
                        render_services_selection(show_standard=False)

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
                vat_amount = calculate_vat_amount(net_total, vat_rate)
                gross_total = calculate_gross_from_net(net_total, vat_rate)

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
                                "components": pricing_display.get("display_components_by_category", {}),
                                "formatted_totals": {
                                    "hardware": pricing_display["formatted_hardware_total"],
                                    "services": pricing_display["formatted_services_total"],
                                    "net": pricing_display["formatted_net_total"],
                                    "vat": pricing_display["formatted_vat_amount"],
                                    "gross": pricing_display["formatted_gross_total"],
                                },
                            }

                except ImportError:
                    pass

                vat_rate = 0.19

                component_net_total = float(
                    pricing_display.get(
                        "main_components_total", net_total))
                formatted_component_net = pricing_display.get(
                    "formatted_main_total",
                    _format_german_currency(component_net_total),
                )

                zubehor_total = float(
                    pricing_display.get(
                        "optional_components_total", 0.0))
                formatted_zubehor_total = pricing_display.get(
                    "formatted_optional_total",
                    _format_german_currency(zubehor_total),
                )

                optional_services_total = 0.0
                display_components = pricing_display.get(
                    "display_components") or []
                if isinstance(display_components, list):
                    optional_services_total = sum(
                        float(comp.get("total_price", 0.0))
                        for comp in display_components
                        if comp.get("category") == "Dienstleistungen" and comp.get("is_optional")
                    )

                extras_total = float(optional_services_total)
                formatted_extras_total = _format_german_currency(extras_total)
                formatted_services_total = pricing_display.get(
                    "formatted_services_total",
                    _format_german_currency(services_total),
                )

                provision_percent = float(
                    details.get("provision_percent", 0.0))
                provision_euro = float(details.get("provision_euro", 0.0))
                provision_percent_amount = 0.0
                total_provision_amount = 0.0
                formatted_provision_percent = _format_german_currency(0.0)
                formatted_provision_total = _format_german_currency(0.0)

                final_end_preis = float(net_total)
                formatted_final_endpreis = pricing_display.get(
                    "formatted_net_total",
                    _format_german_currency(final_end_preis),
                )
                minus_mwst_value = float(vat_amount)
                formatted_minus_mwst = pricing_display.get(
                    "formatted_vat_amount",
                    _format_german_currency(minus_mwst_value),
                )
                preis_mit_mwst = float(gross_total)
                formatted_preis_mit_mwst = pricing_display.get(
                    "formatted_gross_total",
                    _format_german_currency(preis_mit_mwst),
                )
                zwischensumme_brutto = preis_mit_mwst
                formatted_zwischensumme = formatted_preis_mit_mwst

                st.markdown("---")
                # Guard vor UI-Block: Session kann während schneller Eingaben enden
                if not _is_session_alive():
                    return
                st.markdown("#### **Manuelle Provision**")
                col_prov_percent, col_prov_euro = st.columns(2)
                with col_prov_percent:
                    provision_percent = st.number_input(
                        "Provision (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=provision_percent,
                        step=0.1,
                        format="%.1f",
                        key="pricing_manual_provision_percent_input",
                        help="Manuelle Provision in Prozent auf den finalen Angebotspreis",
                    )
                with col_prov_euro:
                    provision_euro = st.number_input(
                        "Provision (€)",
                        min_value=0.0,
                        max_value=100000.0,
                        value=provision_euro,
                        step=10.0,
                        format="%.2f",
                        key="pricing_manual_provision_euro_input",
                        help="Manuelle Provision als fester Euro-Betrag",
                    )

                # Debounce: bei sehr schnellen Änderungen keine Flut an UI-Updates
                do_heavy_ui = True
                try:
                    import time
                    now = time.monotonic()
                    last = st.session_state.get('_provision_update_last_ts', 0.0)
                    if (now - float(last)) < 0.2:
                        do_heavy_ui = False
                    else:
                        st.session_state['_provision_update_last_ts'] = now
                except Exception:
                    pass

                if do_heavy_ui and (provision_percent > 0 or provision_euro > 0):
                    net_total_amount = float(net_total)
                    provision_percent_amount = net_total_amount * \
                        (provision_percent / 100.0)
                    total_provision_amount = provision_percent_amount + provision_euro
                    formatted_provision_percent = _format_german_currency(
                        provision_percent_amount)
                    formatted_provision_total = _format_german_currency(
                        total_provision_amount)

                    try:
                        st.markdown("**Provisionsberechnung:**")
                        col_base_label, col_base_value = st.columns([3, 1])
                        with col_base_label:
                            st.write("Basis (finaler Angebotspreis):")
                        with col_base_value:
                            st.write(
                                pricing_display.get(
                                    "formatted_net_total",
                                    _format_german_currency(net_total_amount)))

                        if provision_percent > 0:
                            col_break_label, col_break_value = st.columns([3, 1])
                            with col_break_label:
                                st.write(f"+ Provision ({provision_percent}%)")
                            with col_break_value:
                                st.write(f"+ {formatted_provision_percent}")

                        if provision_euro > 0:
                            col_break_label, col_break_value = st.columns([3, 1])
                            with col_break_label:
                                st.write("+ Provision (Festbetrag)")
                            with col_break_value:
                                st.write(
                                    f"+ {_format_german_currency(provision_euro)}")

                        st.markdown("---")

                        final_end_preis = net_total_amount + total_provision_amount
                        formatted_final_endpreis = _format_german_currency(
                            final_end_preis)
                        minus_mwst_value = calculate_vat_amount(
                            final_end_preis, vat_rate)
                        formatted_minus_mwst = _format_german_currency(
                            minus_mwst_value)
                        preis_mit_mwst = calculate_gross_from_net(
                            final_end_preis, vat_rate)
                        formatted_preis_mit_mwst = _format_german_currency(
                            preis_mit_mwst)
                        zwischensumme_brutto = preis_mit_mwst
                        formatted_zwischensumme = formatted_preis_mit_mwst

                        col_final_label, col_final_value = st.columns([3, 1])
                        with col_final_label:
                            st.markdown("### **🎯 Endpreis mit Provision:**")
                        with col_final_value:
                            st.markdown(f"### **{formatted_final_endpreis}**")
                    except Exception as _ui_err:
                        # UI-Schreibfehler (z.B. WebSocketClosedError) ignorieren
                        debug_log("solar_calculator.ui", "UI-Update unterdrückt", error=str(_ui_err))

                st.markdown("---")
                st.markdown(
                    "#### **Preisänderungen (Rabatte, Zuschläge, Sondervereinbarungen)**")

                col_discount, col_rebates, col_surcharge, col_special = st.columns(
                    4)
                with col_discount:
                    discount_percent = st.slider(
                        "Rabatt (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(details.get("discount_percent", 0.0)),
                        step=0.1,
                        key="pricing_modifications_discount_slider",
                        help="Prozentualer Rabatt auf den Bruttobetrag",
                    )
                    st.text_area(
                        "Beschreibung für Rabatt",
                        key="pricing_modifications_descriptions_discount_text",
                        help="Beschreibung oder Details zum Rabatt.",
                        height=80,
                    )

                with col_rebates:
                    rebates_eur = st.slider(
                        "Nachlässe (€)",
                        min_value=0.0,
                        max_value=10000.0,
                        value=float(details.get("rebates_eur", 0.0)),
                        step=10.0,
                        key="pricing_modifications_rebates_slider",
                        help="Feste Nachlässe in Euro",
                    )
                    st.text_area(
                        "Beschreibung für Nachlässe",
                        key="pricing_modifications_descriptions_rebates_text",
                        help="Beschreibung oder Details zu den Nachlässen.",
                        height=80,
                    )

                with col_surcharge:
                    surcharge_percent = st.slider(
                        "Zuschlag (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(details.get("surcharge_percent", 0.0)),
                        step=0.1,
                        key="pricing_modifications_surcharge_slider",
                        help="Prozentualer Zuschlag auf den Bruttobetrag",
                    )
                    st.text_area(
                        "Beschreibung für Zuschlag",
                        key="pricing_modifications_descriptions_surcharge_text",
                        help="Beschreibung oder Details zum Zuschlag.",
                        height=80,
                    )

                with col_special:
                    special_costs_eur = st.slider(
                        "Sonderkosten (€)",
                        min_value=0.0,
                        max_value=10000.0,
                        value=float(details.get("special_costs_eur", 0.0)),
                        step=10.0,
                        key="pricing_modifications_special_costs_slider",
                        help="Zusätzliche Sonderkosten in Euro",
                    )
                    st.text_area(
                        "Beschreibung für Sonderkosten",
                        key="pricing_modifications_descriptions_special_costs_text",
                        help="Beschreibung oder Details zu den Sonderkosten.",
                        height=80,
                    )

                col_misc1, col_misc2 = st.columns(2)
                with col_misc1:
                    miscellaneous_eur = st.slider(
                        "Sonstiges (€)",
                        min_value=0.0,
                        max_value=10000.0,
                        value=float(details.get("miscellaneous_eur", 0.0)),
                        step=10.0,
                        key="pricing_modifications_miscellaneous_slider",
                        help="Sonstige Kosten oder Abzüge in Euro",
                    )
                    st.text_area(
                        "Beschreibung für Sonstiges",
                        key="pricing_modifications_descriptions_miscellaneous_text",
                        help="Beschreibung oder Details zu Sonstigem.",
                        height=80,
                    )

                with col_misc2:
                    st.text_area(
                        "Sondervereinbarungen",
                        key="pricing_modifications_special_agreements_text",
                        help="Zusätzliche Informationen oder Vereinbarungen, die im Angebot berücksichtigt werden sollen.",
                        height=120,
                    )

                discount_percent_amount = 0.0
                total_discounts = 0.0
                formatted_total_discounts = _format_german_currency(0.0)
                surcharge_percent_amount = 0.0
                total_surcharges = 0.0
                formatted_total_surcharges = _format_german_currency(0.0)

                base_price_for_modifications = final_end_preis
                base_gross_for_modifications = preis_mit_mwst
                base_vat_for_modifications = minus_mwst_value
                formatted_base_gross = formatted_preis_mit_mwst
                formatted_base_vat = formatted_minus_mwst

                if (
                    discount_percent > 0
                    or rebates_eur > 0
                    or surcharge_percent > 0
                    or special_costs_eur > 0
                    or miscellaneous_eur > 0
                    or extras_total > 0
                ):
                    discount_percent_amount = base_price_for_modifications * \
                        (discount_percent / 100.0)
                    total_discounts = discount_percent_amount + rebates_eur
                    net_after_discounts = base_price_for_modifications - total_discounts

                    surcharge_percent_amount = net_after_discounts * \
                        (surcharge_percent / 100.0)
                    total_surcharges = surcharge_percent_amount + \
                        special_costs_eur + miscellaneous_eur

                    net_after_modifications = net_after_discounts + total_surcharges + extras_total

                    final_end_preis = net_after_modifications
                    formatted_final_endpreis = _format_german_currency(
                        final_end_preis)

                    minus_mwst_value = base_vat_for_modifications
                    formatted_minus_mwst = formatted_base_vat

                    preis_mit_mwst = final_end_preis + base_vat_for_modifications
                    formatted_preis_mit_mwst = _format_german_currency(
                        preis_mit_mwst)
                    zwischensumme_brutto = preis_mit_mwst
                    formatted_zwischensumme = formatted_preis_mit_mwst

                    formatted_total_discounts = _format_german_currency(
                        total_discounts)
                    formatted_total_surcharges = _format_german_currency(
                        total_surcharges)

                    st.markdown("**Preisänderungen-Berechnung:**")
                    col_mod_label, col_mod_value = st.columns([3, 1])
                    with col_mod_label:
                        st.write(
                            "Basis (finaler Angebotspreis nach Provision, netto):")
                    with col_mod_value:
                        st.write(_format_german_currency(
                            base_price_for_modifications))

                    col_mod_label, col_mod_value = st.columns([3, 1])
                    with col_mod_label:
                        st.write(
                            "Basis (finaler Angebotspreis nach Provision inkl. MwSt):")
                    with col_mod_value:
                        st.write(formatted_base_gross)

                    if discount_percent > 0:
                        col_mod_label, col_mod_value = st.columns([3, 1])
                        with col_mod_label:
                            st.write(f"- Rabatt ({discount_percent}%)")
                        with col_mod_value:
                            st.write(
                                f"- {_format_german_currency(discount_percent_amount)}")

                    if rebates_eur > 0:
                        col_mod_label, col_mod_value = st.columns([3, 1])
                        with col_mod_label:
                            st.write("- Pauschale Rabatte")
                        with col_mod_value:
                            st.write(
                                f"- {_format_german_currency(rebates_eur)}")

                    if total_discounts > 0:
                        col_mod_label, col_mod_value = st.columns([3, 1])
                        with col_mod_label:
                            st.write("**Summe Rabatte:**")
                        with col_mod_value:
                            st.write(f"**- {formatted_total_discounts}**")

                    if surcharge_percent > 0:
                        col_mod_label, col_mod_value = st.columns([3, 1])
                        with col_mod_label:
                            st.write(f"+ Aufpreis ({surcharge_percent}%)")
                        with col_mod_value:
                            st.write(
                                f"+ {_format_german_currency(surcharge_percent_amount)}")

                    if special_costs_eur > 0:
                        col_mod_label, col_mod_value = st.columns([3, 1])
                        with col_mod_label:
                            st.write("+ Sonderkosten")
                        with col_mod_value:
                            st.write(
                                f"+ {_format_german_currency(special_costs_eur)}")

                    if miscellaneous_eur > 0:
                        col_mod_label, col_mod_value = st.columns([3, 1])
                        with col_mod_label:
                            st.write("+ Sonstiges")
                        with col_mod_value:
                            st.write(
                                f"+ {_format_german_currency(miscellaneous_eur)}")

                    if total_surcharges > 0:
                        col_mod_label, col_mod_value = st.columns([3, 1])
                        with col_mod_label:
                            st.write("**Summe Aufpreise:**")
                        with col_mod_value:
                            st.write(f"**+ {formatted_total_surcharges}**")

                    st.markdown("---")
                    col_final_label, col_final_value = st.columns([3, 1])
                    with col_final_label:
                        st.markdown("### **💰 Endpreis (brutto):**")
                    with col_final_value:
                        st.markdown(f"### **{formatted_preis_mit_mwst}**")

                    col_final_label, col_final_value = st.columns([3, 1])
                    with col_final_label:
                        st.write("Endpreis (netto nach Rabatten/Aufpreisen):")
                    with col_final_value:
                        st.write(formatted_final_endpreis)

                details['provision_percent'] = provision_percent
                details['provision_euro'] = provision_euro
                details['provision_percent_amount'] = provision_percent_amount
                details['total_provision_amount'] = total_provision_amount
                details['component_base_price_net'] = component_net_total
                details['zubehor_total'] = zubehor_total
                details['extras_total'] = extras_total
                details['services_total'] = services_total
                details['discount_percent'] = discount_percent
                details['rebates_eur'] = rebates_eur
                details['surcharge_percent'] = surcharge_percent
                details['special_costs_eur'] = special_costs_eur
                details['miscellaneous_eur'] = miscellaneous_eur
                details['total_discounts'] = total_discounts
                details['total_surcharges'] = total_surcharges
                details['preis_mit_mwst'] = preis_mit_mwst
                details['zwischensumme_brutto'] = zwischensumme_brutto
                details['minus_mehrwertsteuer'] = minus_mwst_value
                details['final_offer_price_net'] = final_end_preis
                details['final_offer_price_gross'] = zwischensumme_brutto
                details['final_price_with_provision'] = component_net_total + \
                    total_provision_amount
                details['base_price_for_modifications'] = base_price_for_modifications
                details['formatted_base_price_for_modifications'] = _format_german_currency(
                    base_price_for_modifications)
                details['base_preis_mit_mwst'] = base_gross_for_modifications
                details['formatted_base_preis_mit_mwst'] = formatted_base_gross

                formatted_values = {
                    'component_base_price_net': formatted_component_net,
                    'provision_percent_amount': formatted_provision_percent,
                    'provision_total': formatted_provision_total,
                    'preis_mit_mwst': formatted_preis_mit_mwst,
                    'zubehor_total': formatted_zubehor_total,
                    'extras_total': formatted_extras_total,
                    'services_total': formatted_services_total,
                    'total_discounts': formatted_total_discounts,
                    'total_surcharges': formatted_total_surcharges,
                    'zwischensumme_brutto': formatted_zwischensumme,
                    'minus_mehrwertsteuer': formatted_minus_mwst,
                    'final_offer_price_net': formatted_final_endpreis,
                    'final_offer_price_gross': formatted_zwischensumme,
                    'final_price_with_provision': _format_german_currency(
                        component_net_total + total_provision_amount),
                    'base_price_for_modifications': _format_german_currency(base_price_for_modifications),
                    'base_preis_mit_mwst': formatted_base_gross,
                    'base_mwst': formatted_base_vat}
                details['formatted_final_pricing'] = formatted_values

                st.session_state.project_data['project_details'].update(
                    details)

                debug_log(
                    "solar_calculator.pricing",
                    "Finale Preisberechnung aktualisiert",
                    preis_mit_mwst=preis_mit_mwst,
                    zubehor_total=zubehor_total,
                    extras_total=extras_total,
                    zwischensumme_brutto=zwischensumme_brutto,
                    final_offer_price_net=final_end_preis
                )

                try:
                    from pricing.dynamic_key_manager import KeyCategory

                    final_pricing_values = {
                        "SIMPLE_ENDERGEBNIS_BRUTTO": base_gross_for_modifications,
                        "SOLAR_CALC_ZUBEHOR_PREIS": zubehor_total,
                        "SOLAR_CALC_EXTRA_DIENSTLEISTUNGEN": extras_total,
                        "CALC_TOTAL_DISCOUNTS": total_discounts,
                        "CALC_TOTAL_SURCHARGES": total_surcharges,
                        "CALC_ZWISCHENSUMME": zwischensumme_brutto,
                        "SIMPLE_MWST_BETRAG": base_vat_for_modifications,
                        "FINAL_END_PREIS": final_end_preis,
                        "PROVISION_TOTAL": total_provision_amount,
                        "PROVISION_PERCENT_AMOUNT": provision_percent_amount,
                        "BASE_COMPONENT_PRICE_NET": component_net_total}

                    final_pricing_formatted = {
                        "SIMPLE_ENDERGEBNIS_BRUTTO_FORMATTED": formatted_base_gross,
                        "SOLAR_CALC_ZUBEHOR_PREIS_FORMATTED": formatted_zubehor_total,
                        "SOLAR_CALC_EXTRA_DIENSTLEISTUNGEN_FORMATTED": formatted_extras_total,
                        "CALC_TOTAL_DISCOUNTS_FORMATTED": formatted_total_discounts,
                        "CALC_TOTAL_SURCHARGES_FORMATTED": formatted_total_surcharges,
                        "CALC_ZWISCHENSUMME_FORMATTED": formatted_zwischensumme,
                        "SIMPLE_MWST_FORMATTED": formatted_base_vat,
                        "FINAL_END_PREIS_FORMATTED": formatted_final_endpreis,
                        "PROVISION_TOTAL_FORMATTED": formatted_provision_total,
                        "BASE_COMPONENT_PRICE_NET_FORMATTED": formatted_component_net}

                    if solar_pricing_integration.key_manager:
                        final_pricing_keys = solar_pricing_integration.key_manager.generate_keys(
                            {**final_pricing_values, **final_pricing_formatted},
                            prefix="PDF__",
                            category=KeyCategory.PRICING
                        )
                        st.session_state["solar_calculator_final_pricing_keys"] = final_pricing_keys
                        st.session_state["solar_calculator_final_pricing_values"] = {
                            **final_pricing_values, **final_pricing_formatted}
                except ImportError:
                    pass

                simple_pricing_data = {
                    "komponenten_summe": float(component_net_total),
                    "provision_euro": float(total_provision_amount),
                    "netto_mit_provision": float(base_price_for_modifications),
                    "mwst_betrag": float(base_vat_for_modifications),
                    "endergebnis_brutto": float(base_gross_for_modifications),
                    "zubehor_preis": float(zubehor_total),
                    "extras_preis": float(extras_total),
                    "formatted": {
                        "komponenten": formatted_component_net,
                        "provision": formatted_provision_total,
                        "netto": _format_german_currency(base_price_for_modifications),
                        "mwst": formatted_base_vat,
                        "endergebnis": formatted_base_gross,
                        "zubehor": formatted_zubehor_total,
                        "extras": formatted_extras_total,
                    },
                }

                complete_pricing_data = {
                    "komponenten_summe": float(component_net_total),
                    "provision_euro": float(total_provision_amount),
                    "endergebnis_brutto": float(base_gross_for_modifications),
                    "discount_percent": float(discount_percent),
                    "discount_euro": float(rebates_eur),
                    "discount_percent_amount": float(discount_percent_amount),
                    "total_discount": float(total_discounts),
                    "surcharge_percent": float(surcharge_percent),
                    "surcharge_euro": float(
                        special_costs_eur + miscellaneous_eur),
                    "surcharge_percent_amount": float(surcharge_percent_amount),
                    "total_surcharge": float(total_surcharges),
                    "zwischensumme": float(zwischensumme_brutto),
                    "finale_summe_netto": float(final_end_preis),
                    "formatted": {
                        "endergebnis_brutto": formatted_base_gross,
                        "total_discounts": formatted_total_discounts,
                        "total_surcharges": formatted_total_surcharges,
                        "zwischensumme": formatted_zwischensumme,
                        "mwst_betrag": formatted_base_vat,
                        "final_end_preis": formatted_final_endpreis,
                        "zubehor_preis": formatted_zubehor_total,
                        "extras_preis": formatted_extras_total,
                    },
                }

                final_pricing_data = {
                    "final_end_preis": float(final_end_preis),
                    "ersparte_mehrwertsteuer": float(minus_mwst_value),
                    "vat_savings": float(minus_mwst_value),
                    "zubehor_betrag": float(zubehor_total),
                    "extra_services_betrag": float(extras_total),
                    "zwischensumme_final": float(zwischensumme_brutto),
                    "mwst_in_zwischensumme": float(minus_mwst_value),
                    "kern_komponenten_total": float(component_net_total),
                    "formatted": {
                        "final_end_preis": formatted_final_endpreis,
                        "ersparte_mwst": formatted_minus_mwst,
                        "zubehor": formatted_zubehor_total,
                        "extra_services": formatted_extras_total,
                        "zwischensumme_final": formatted_zwischensumme,
                        "mwst_zwischensumme": formatted_minus_mwst,
                        "kern_komponenten_total": formatted_component_net,
                    },
                }

                st.session_state["simple_pricing_data"] = simple_pricing_data
                st.session_state["complete_pricing_data"] = complete_pricing_data
                st.session_state["final_pricing_data"] = final_pricing_data

                st.session_state.project_data["simple_pricing_data"] = simple_pricing_data
                st.session_state.project_data["complete_pricing_data"] = complete_pricing_data
                st.session_state.project_data["final_pricing_data"] = final_pricing_data

                st.info(
                    "💡 **Hinweis:** Amortisationszeit-Berechnungen sind jetzt im Bereich 'Ergebnisse & Dashboard' verfügbar.")
                # Ende der einfachen Berechnung

                # Display by category if available - only show active
                # components
                if pricing_display.get("display_components_by_category"):
                    for category, category_data in pricing_display["display_components_by_category"].items(
                    ):
                        # Only show categories with components
                        if category_data["components"]:
                            st.markdown(
                                f"**{category}** ({len(category_data['components'])} Positionen)")
                            for comp in category_data["components"]:
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    st.write(f"• {comp['name']}")
                                with col2:
                                    st.write(
                                        f"{comp['quantity']} {comp.get('calculate_per', 'Stück')}")
                                with col3:
                                    st.write(comp['formatted_total_price'])
                            st.markdown("---")

    except Exception as e:
        st.error(f"Fehler bei der Preisberechnung: {e}")


def _trigger_pricing_update(details: dict[str, Any]) -> None:
    """Trigger pricing update when component selection changes"""
    if not PRICING_INTEGRATION_AVAILABLE:
        return
    # Verbindungs-/Session-Check: vermeidet Sends nach Session-Ende
    try:
        if get_script_run_ctx() is None:
            return

        # Debounce: vermeidet Flut an Updates bei schneller Auswahl
        import time
        now = time.monotonic()
        last = st.session_state.get('_pricing_update_last_ts', 0.0)
        if (now - float(last)) < 0.2:  # 200 ms Mindestabstand
            return
        st.session_state['_pricing_update_last_ts'] = now

        debug_log(
            "solar_calculator.pricing",
            "Pricing-Update ausgelöst",
            selected_components={
                k: details.get(k) for k in [
                    'selected_module_name',
                    'selected_inverter_name',
                    'selected_storage_name']},
            step=st.session_state.get('solar_calc_step'))
        update_pricing_in_session_state(details)
        debug_log(
            "solar_calculator.pricing",
            "Pricing-Update abgeschlossen",
            pricing_data=st.session_state.get(
                'pricing_data',
                {}).get(
                'pv_system_pricing',
                {}))
    except Exception as e:
        debug_log(
            "solar_calculator.pricing",
            "Fehler beim Pricing-Update",
            error=str(e))
        print(f"Error updating pricing: {e}")


def _ensure_project_data_dicts():
    if 'project_data' not in st.session_state:
        st.session_state.project_data = {}
    if 'project_details' not in st.session_state.project_data:
        st.session_state.project_data['project_details'] = {}
    if 'analysis_results' not in st.session_state.project_data:
        st.session_state.project_data['analysis_results'] = {}
    if 'company_info' not in st.session_state.project_data:
        st.session_state.project_data['company_info'] = {}

    # RETURN the project_data dictionary!
    return st.session_state.project_data


def _product_names_by_category(
        category: str, texts: dict[str, str]) -> list[str]:
    try:
        products = list_products_safe(category=category)
        return [
            p.get(
                'model_name',
                f"ID:{
                    p.get(
                        'id',
                        'N/A')}") for p in products]
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
    init_debug_mode()
    render_debug_toolbar("sidebar")

    debug_log(
        "solar_calculator",
        "Render Solar Calculator gestartet",
        module=module_name,
        session_step=st.session_state.get('solar_calc_step')
    )

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
    debug_log("solar_calculator", "Aktive Wizard-Stufe", step=step)

    # Hilfsfunktionen
    def _products_by_category(category: str) -> list[dict[str, Any]]:
        try:
            return list_products_safe(category=category)  # type: ignore
        except Exception:
            return []

    def _brands_from_products(products: list[dict[str, Any]]) -> list[str]:
        return sorted({(p.get('brand') or '').strip()
                      for p in products if p.get('brand')})

    def _filter_models_by_brand(
            products: list[dict[str, Any]], brand: str | None) -> list[dict[str, Any]]:
        if not brand:
            return products
        return [
            p for p in products if (
                p.get('brand') or '').strip().lower() == brand.strip().lower()]

    # Sichtbare Version / Build Tag zur Kontrolle, dass neue Datei wirklich
    # geladen wurde
    version_tag = "SolarCalcWizard-2025-09-05-v1"
    st.caption(f"Solar Calculator – Schritt {step} / 2 | Build: {version_tag}")

    # Optionaler Debug-Block zur Fehlersuche falls Nutzer nur Minimal-UI sieht
    with st.expander("Debug (nur vorübergehend) ", expanded=False):
        st.write(
            {
                'step': step,
                'module_qty_state': st.session_state.get('module_quantity_sc_v1'),
                'details_keys': sorted(
                    details.keys()),
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

        # Session-Guard vor Modul-Block
        if not _is_session_alive():
            return

        # --- MODULE ---
        try:
            module_products = _products_by_category('Modul')
            module_brands = _brands_from_products(module_products)
        except Exception as e:
            debug_log("solar_calculator.module", "Fehler beim Laden der Module", error=str(e))
            module_products = []
            module_brands = []

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

            # Guard vor number_input
            if not _is_session_alive():
                return

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
            
            # Guard vor selectbox
            if not _is_session_alive():
                return
                
            selected_brand = st.selectbox(
                _get_text(texts, 'module_brand_label', 'PV Modul Hersteller'),
                options=brand_options,
                index=idx_brand,
                key='selected_module_brand_sc_v1'
            )
            details['selected_module_brand'] = selected_brand if selected_brand != please_select_text else None
        with cols_mod_top[2]:
            # Modelle je Hersteller
            try:
                filtered_mods = _filter_models_by_brand(
                    module_products, details.get('selected_module_brand'))
                model_names = [p.get('model_name')
                               for p in filtered_mods if p.get('model_name')]
            except Exception as e:
                debug_log("solar_calculator.module", "Fehler beim Filtern der Modelle", error=str(e))
                model_names = []
                
            current_module = details.get(
                'selected_module_name', please_select_text)
            module_options = [please_select_text] + model_names
            try:
                idx_mod = module_options.index(current_module)
            except ValueError:
                idx_mod = 0
            
            # Guard vor selectbox
            if not _is_session_alive():
                return
                
            selected_module = st.selectbox(
                _get_text(texts, 'module_model_label', 'PV Modul Modell'),
                options=module_options,
                index=idx_mod,
                key='selected_module_name_sc_v1'
            )
            details['selected_module_name'] = selected_module if selected_module != please_select_text else None
            if details.get('selected_module_name'):
                try:
                    md = get_product_by_model_name_safe(
                        details['selected_module_name'])
                    if md:
                        details['selected_module_id'] = md.get('id')
                        details['selected_module_capacity_w'] = float(
                            md.get('capacity_w', 0.0) or 0.0)
                    else:
                        details['selected_module_id'] = None
                        details['selected_module_capacity_w'] = 0.0
                except Exception as e:
                    debug_log("solar_calculator.module", "Fehler beim Laden der Modulkapazität", error=str(e))
                    details['selected_module_id'] = None
                    details['selected_module_capacity_w'] = 0.0
            else:
                details['selected_module_id'] = None
                details['selected_module_capacity_w'] = 0.0

        if _is_session_alive() and details.get('selected_module_capacity_w', 0.0) > 0:
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
        
        if _is_session_alive():
            st.info(f"{_get_text(texts,
                                 'anlage_size_label',
                                 'Anlagengröße (kWp)')}: {anlage_kwp:.2f} kWp")

        # Trigger pricing update for modules
        _trigger_pricing_update(details)

        # Session-Guard vor Wechselrichter-Block
        if not _is_session_alive():
            return

        # --- WECHSELRICHTER ---
        try:
            inverter_products = _products_by_category('Wechselrichter')
            inverter_brands = _brands_from_products(inverter_products)
        except Exception as e:
            debug_log("solar_calculator.inverter", "Fehler beim Laden der Wechselrichter", error=str(e))
            inverter_products = []
            inverter_brands = []
            
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
            
            # Guard vor selectbox
            if not _is_session_alive():
                return
                
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
            try:
                filtered_inv = _filter_models_by_brand(
                    inverter_products, details.get('selected_inverter_brand'))
                inv_model_names = [p.get('model_name')
                                   for p in filtered_inv if p.get('model_name')]
            except Exception as e:
                debug_log("solar_calculator.inverter", "Fehler beim Filtern der Wechselrichter", error=str(e))
                inv_model_names = []
                
            current_inv_model = details.get(
                'selected_inverter_name', please_select_text)
            inv_model_options = [please_select_text] + inv_model_names
            try:
                idx_inv_model = inv_model_options.index(current_inv_model)
            except ValueError:
                idx_inv_model = 0
            
            # Guard vor selectbox
            if not _is_session_alive():
                return
                
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
            # Guard vor number_input
            if not _is_session_alive():
                return
                
            details['selected_inverter_quantity'] = int(st.number_input(
                _get_text(texts, 'inverter_quantity_label', 'Anzahl WR'),
                min_value=1,
                value=int(details.get('selected_inverter_quantity', 1) or 1),
                step=1,
                key='selected_inverter_quantity_sc_v1'
            ))

        base_inverter_power_kw = 0.0
        if details.get('selected_inverter_name'):
            try:
                invd = get_product_by_model_name_safe(
                    details['selected_inverter_name'])
                if invd:
                    details['selected_inverter_id'] = invd.get('id')
                    base_inverter_power_kw = float(
                        invd.get('power_kw', 0.0) or 0.0)
                else:
                    details['selected_inverter_id'] = None
            except Exception as e:
                debug_log("solar_calculator.inverter", "Fehler beim Laden der Wechselrichter-Leistung", error=str(e))
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

        with contextlib.suppress(Exception):
            st.session_state.project_data['inverter_power_kw'] = total_inverter_power_kw

        if _is_session_alive() and total_inverter_power_kw > 0:
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
        
        # Session-Guard vor Speicher-Block
        if not _is_session_alive():
            return
        
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
            # Debounce: bei schnellen Änderungen keine UI-Flut
            import time
            now = time.monotonic()
            last_storage = st.session_state.get('_storage_update_last_ts', 0.0)
            debounce_storage = (now - float(last_storage)) < 0.25  # 250ms für Speicher (etwas länger)
            
            try:
                storage_products = _products_by_category('Batteriespeicher')
                storage_brands = _brands_from_products(storage_products)
            except Exception as e:
                debug_log("solar_calculator.storage", "Fehler beim Laden der Speicherprodukte", error=str(e))
                storage_products = []
                storage_brands = []
            
            # Guard vor Columns
            if not _is_session_alive():
                return
            
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
                
                # Guard vor Selectbox
                if not _is_session_alive():
                    return
                    
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
                try:
                    filtered_storage = _filter_models_by_brand(
                        storage_products, details.get('selected_storage_brand'))
                    storage_model_names = [
                        p.get('model_name') for p in filtered_storage if p.get('model_name')]
                except Exception as e:
                    debug_log("solar_calculator.storage", "Fehler beim Filtern der Modelle", error=str(e))
                    storage_model_names = []
                    
                current_storage_model = details.get(
                    'selected_storage_name', please_select_text)
                storage_model_options = [
                    please_select_text] + storage_model_names
                try:
                    idx_st_model = storage_model_options.index(
                        current_storage_model)
                except ValueError:
                    idx_st_model = 0
                
                # Guard vor Selectbox
                if not _is_session_alive():
                    return
                    
                selected_storage = st.selectbox(
                    _get_text(texts, 'storage_model_label', 'Speicher Modell'),
                    options=storage_model_options,
                    index=idx_st_model,
                    key='selected_storage_name_sc_v1'
                )
                details['selected_storage_name'] = selected_storage if selected_storage != please_select_text else None
                
            with cols_storage[2]:
                default_cap = float(
                    details.get(
                        'selected_storage_storage_power_kw',
                        0.0) or 0.0)
                if details.get('selected_storage_name') and not default_cap:
                    try:
                        std = get_product_by_model_name_safe(
                            details['selected_storage_name'])
                        if std:
                            default_cap = float(
                                std.get('storage_power_kw', 0.0) or 0.0)
                    except Exception as e:
                        debug_log("solar_calculator.storage", "Fehler beim Laden der Speicherkapazität", error=str(e))
                        
                if default_cap == 0.0:
                    default_cap = 5.0
                
                # Guard vor number_input
                if not _is_session_alive():
                    return
                    
                details['selected_storage_storage_power_kw'] = st.number_input(
                    _get_text(
                        texts,
                        'storage_capacity_manual_label',
                        'Gewünschte Gesamtkapazität (kWh)'),
                    min_value=0.0,
                    value=default_cap,
                    step=0.1,
                    key='selected_storage_storage_power_kw_sc_v1')
            
            # Info-Block nur wenn Session aktiv und nicht gedrosselt
            if not debounce_storage and _is_session_alive() and details.get('selected_storage_name'):
                try:
                    std = get_product_by_model_name_safe(
                        details['selected_storage_name'])
                    if std:
                        cap_model = float(std.get('storage_power_kw', 0.0) or 0.0)
                        st.info(f"{_get_text(texts,
                                             'storage_capacity_model_label',
                                             'Kapazität Modell (kWh)')}: {cap_model:.2f} kWh")
                except Exception as e:
                    debug_log("solar_calculator.storage", "Fehler beim Anzeigen der Speicherkapazität", error=str(e))

            # Aktualisiere Debounce-Timestamp
            st.session_state['_storage_update_last_ts'] = now
            
            # Pricing-Update nur wenn nicht gedrosselt
            if not debounce_storage:
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
                debug_log(
                    "solar_calculator",
                    "Wechsel zu Schritt 2",
                    previous_step=step)
                st.session_state['solar_calc_step'] = 2
                st.rerun()

    elif step == 2:
        st.subheader(
            _get_text(
                texts,
                'additional_components_header',
                'Zusätzliche Komponenten'))

        wallboxes = _product_names_by_category('Wallbox', texts)
        ems = _product_names_by_category('Energiemanagementsystem', texts)
        optimizers = _product_names_by_category('Leistungsoptimierer', texts)
        carports = _product_names_by_category('Carport', texts)
        backup_systems = _product_names_by_category(
            'Notstromversorgung', texts)
        animal_protection = _product_names_by_category(
            'Tierabwehrschutz', texts)

        details['include_additional_components'] = st.checkbox(
            _get_text(
                texts,
                'include_additional_components_label',
                'Zusätzliche Komponenten einplanen'),
            value=bool(
                details.get(
                    'include_additional_components',
                    False)),
            key='include_additional_components_sc_v1',
        )

        def _component_selector_with_pricing(
            label_key: str,
            options: list[str],
            name_key: str,
            id_key: str,
            widget_key: str,
            quantity_key: str | None = None,
        ) -> None:
            """Component selector that displays pricing details and optional quantity."""

            fallback_labels = {
                'wallbox_model_label': 'Wallbox | E-Ladestationen',
                'ems_model_label': 'Energiemanagementsysteme',
                'optimizer_model_label': 'Leistungsoptimierer',
                'carport_model_label': 'Solar CarPorts',
                'notstrom_model_label': 'Notstromversorgungen',
                'tierabwehr_model_label': 'Tierabwehrschutz',
            }

            if quantity_key:
                col1, col2, col3 = st.columns([3, 1, 2])
            else:
                col1, col2 = st.columns([4, 2])
                col3 = None

            with col1:
                current_val = details.get(name_key, please_select_text)
                options_with_placeholder = [please_select_text] + options
                try:
                    selected_index = options_with_placeholder.index(
                        current_val)
                except ValueError:
                    selected_index = 0

                label_text = _get_text(
                    texts, label_key, fallback_labels.get(
                        label_key, label_key))
                selected_value = st.selectbox(
                    label_text,
                    options=options_with_placeholder,
                    index=selected_index,
                    key=widget_key,
                )

                details[name_key] = selected_value if selected_value != please_select_text else None

                if details.get(name_key):
                    product = get_product_by_model_name_safe(details[name_key])
                    details[id_key] = product.get('id') if product else None
                else:
                    details[id_key] = None

            if col3 and quantity_key and details.get(name_key):
                with col2:
                    current_quantity = int(details.get(quantity_key, 1))
                    new_quantity = st.number_input(
                        "Anzahl",
                        min_value=1,
                        max_value=20,
                        value=current_quantity,
                        step=1,
                        key=f"{widget_key}_qty",
                    )
                    details[quantity_key] = new_quantity

            if details.get(name_key) and col3:
                with col3:
                    product = get_product_by_model_name_safe(details[name_key])
                    if product:
                        try:
                            from product_db import (
                                calculate_price_by_method,
                                calculate_selling_price,
                            )

                            margin_info = calculate_selling_price(
                                product["id"])
                            if margin_info and margin_info.get(
                                    "selling_price_net", 0) > 0:
                                unit_price = margin_info["selling_price_net"]
                            else:
                                unit_price = float(
                                    product.get("price_euro", 0.0))

                            calculate_per = product.get(
                                "calculate_per", "Stück")
                            quantity = details.get(
                                quantity_key, 1) if quantity_key else 1

                            total_price = calculate_price_by_method(
                                base_price=unit_price,
                                quantity=quantity,
                                calculate_per=calculate_per,
                                product_specs=product,
                            )

                            st.caption(
                                f"💰 {
                                    unit_price:.2f} € ({calculate_per})")
                            if quantity > 1:
                                st.caption(f"Gesamt: {total_price:.2f} €")
                        except Exception:
                            st.caption("⚠️ Preis nicht verfügbar")
            elif details.get(name_key) and not col3:
                product = get_product_by_model_name_safe(details[name_key])
                if product:
                    try:
                        from product_db import calculate_selling_price

                        margin_info = calculate_selling_price(product["id"])
                        if margin_info and margin_info.get(
                                "selling_price_net", 0) > 0:
                            unit_price = margin_info["selling_price_net"]
                        else:
                            unit_price = float(product.get("price_euro", 0.0))

                        calculate_per = product.get("calculate_per", "Stück")
                        st.caption(f"💰 {unit_price:.2f} € ({calculate_per})")
                    except Exception:
                        st.caption("⚠️ Preis nicht verfügbar")

        if details['include_additional_components']:
            st.markdown("#### 🔌 Ladeinfrastruktur")
            _component_selector_with_pricing(
                'wallbox_model_label',
                wallboxes,
                'selected_wallbox_name',
                'selected_wallbox_id',
                'sel_wallbox_sc_v1',
                'selected_wallbox_quantity',
            )

            st.markdown("#### ⚡ Energiemanagement")
            _component_selector_with_pricing(
                'ems_model_label',
                ems,
                'selected_ems_name',
                'selected_ems_id',
                'sel_ems_sc_v1')
            _component_selector_with_pricing(
                'optimizer_model_label',
                optimizers,
                'selected_optimizer_name',
                'selected_optimizer_id',
                'sel_opti_sc_v1',
                'selected_optimizer_quantity',
            )

            st.markdown("#### 🏠 Bauliche Erweiterungen")
            _component_selector_with_pricing(
                'carport_model_label',
                carports,
                'selected_carport_name',
                'selected_carport_id',
                'sel_cp_sc_v1')

            st.markdown("#### 🔋 Zusätzliche Systeme")
            _component_selector_with_pricing(
                'notstrom_model_label',
                backup_systems,
                'selected_notstrom_name',
                'selected_notstrom_id',
                'sel_not_sc_v1')

            st.markdown("#### 🛡️ Schutz & Sicherheit")
            _component_selector_with_pricing(
                'tierabwehr_model_label',
                animal_protection,
                'selected_tierabwehr_name',
                'selected_tierabwehr_id',
                'sel_ta_sc_v1')

            if 'selected_wallbox_quantity' not in details:
                details['selected_wallbox_quantity'] = 1
            if 'selected_optimizer_quantity' not in details:
                details['selected_optimizer_quantity'] = 1

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
                    key='additional_other_custom_sc_v1',
                )

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
                        key='additional_other_price_sc_v1',
                    )
                else:
                    details['additional_other_price'] = 0.0

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
                debug_log(
                    "solar_calculator",
                    "Zurück zu Schritt 1",
                    previous_step=step)
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
                with contextlib.suppress(Exception):
                    st.session_state['selected_page_key'] = 'analysis'
                # Reset für nächsten Aufruf
                st.session_state['solar_calc_step'] = 1
                debug_log(
                    "solar_calculator",
                    "Wizard abgeschlossen",
                    target_page=st.session_state.get('selected_page_key'))
                st.rerun()

    # Abschluss Hinweis (nur Schritt 1 zeigt fortlaufend Info, Schritt 2 via
    # Button)
    if step == 1:
        st.caption(
            _get_text(
                texts,
                'tech_selection_saved_info',
                'Änderungen werden automatisch gespeichert.'))
