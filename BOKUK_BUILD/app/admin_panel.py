# admin_panel.py
"""
Datei: admin_panel.py
Zweck: Modul für den Admin Panel Tab (F) - UI-Anpassungen für Wirtschaftlichkeit, Produkte und PDF-Vorlagen.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-04 (Überarbeitet für Syntaxkonsistenz)
"""
import base64
import json
import traceback
from collections.abc import Callable
from datetime import datetime
from typing import Any

import streamlit as st

from admin_intro_settings_ui import render_intro_settings_tab
from admin_payment_terms_ui import (
    render_comprehensive_admin_payment_terms_ui_with_variants,
)
from admin_product_database_ui import render_product_admin_ui
from admin_services_ui import render_services_admin_ui
from admin_user_management_ui import render_user_management_tab
from ui_state_manager import (
    commit_widget_value,
    ensure_session_defaults,
    keep_session_state_alive,
    mirror_widget_value,
    set_current_page,
)

# === WIDGET KEY SUFFIX (global, damit alle Funktionen es nutzen können) ===
WIDGET_KEY_SUFFIX = "_v16_admin_definitiv"

# === DEFAULT FALLBACKS ===
_DEFAULT_GLOBAL_CONSTANTS_FALLBACK: dict[str, Any] = {
    'direct_self_consumption_factor_of_production': 0.25,
    'co2_per_tree_kg_pa': 12.5, 'co2_per_car_km_kg': 0.12, 'co2_per_flight_muc_pmi_kg': 180.0,
    'economic_settings': {'reference_specific_yield_for_pr_kwh_per_kwp': 1100.0},
    'default_performance_ratio_percent': 78.0, 'peak_shaving_effect_kw_estimate': 0.0,
    'optimal_storage_factor': 1.0, 'app_debug_mode_enabled': False, 'active_company_id': None,
    "specific_yields_by_orientation_tilt": {
        "Süd_0": 950.0, "Süd_15": 980.0, "Süd_30": 1000.0, "Süd_45": 980.0, "Süd_60": 950.0,
        "Südost_0": 900.0, "Südost_15": 930.0, "Südost_30": 950.0, "Südost_45": 930.0, "Südost_60": 900.0,
        "Südwest_0": 900.0, "Südwest_15": 930.0, "Südwest_30": 950.0, "Südwest_45": 930.0, "Südwest_60": 900.0,
        "Ost_0": 850.0, "Ost_15": 880.0, "Ost_30": 900.0, "Ost_45": 880.0, "Ost_60": 850.0,
        "West_0": 850.0, "West_15": 880.0, "West_30": 900.0, "West_45": 880.0, "West_60": 850.0,
        "Nord_0": 700.0, "Nord_15": 720.0, "Nord_30": 730.0, "Nord_45": 720.0, "Nord_60": 700.0,
    },
    "visualization_settings": {
        "default_color_palette": "Plotly", "primary_chart_color": "#1f77b4",
        "secondary_chart_color": "#ff7f0e", "chart_font_family": "Arial, sans-serif",
        "chart_font_size_title": 16, "chart_font_size_axis_label": 12,
        "chart_font_size_tick_label": 10,
        "cost_overview_chart": {"chart_type": "bar", "color_palette": "Plotly Standard", "primary_color_bar": "#1f77b4", "show_values_on_chart": True},
        "consumption_coverage_chart": {"chart_type": "pie", "color_palette": "Pastel", "show_percentage": True, "show_labels": True},
        "pv_usage_chart": {"chart_type": "pie", "color_palette": "Grün-Variationen", "show_percentage": True},
        "monthly_prod_cons_chart": {"chart_type": "line", "line_color_production": "#2ca02c", "line_color_consumption": "#d62728", "show_markers": True},
        "cumulative_cashflow_chart": {"chart_type": "line", "line_color": "#17becf", "show_zero_line": True}
    }
}
_DEFAULT_FEED_IN_TARIFFS_FALLBACK: dict[str, list[dict[str, Any]]] = {
    "parts": [{"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 7.86},
              {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 6.80},
              {"kwp_min": 40.01, "kwp_max": 100.0, "ct_per_kwh": 5.56}],
    "full": [{"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 12.47},
             {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 10.45},
             {"kwp_min": 40.01, "kwp_max": 100.0, "ct_per_kwh": 10.45}]
}


def _dummy_load_admin_setting(key, default=None):
    if key == 'pdf_title_image_templates' or key == 'pdf_offer_title_templates' or key == 'pdf_cover_letter_templates':
        return []
    if key == 'pdf_design_settings':
        return {'primary_color': '#4F81BD', 'secondary_color': '#C0C0C0'}
    if key == 'global_constants':
        return _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.copy()
    if key == 'feed_in_tariffs':
        return _DEFAULT_FEED_IN_TARIFFS_FALLBACK.copy()
    if key == 'visualization_settings':
        return _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.get(
            'visualization_settings', {}).copy()
    if key in ["Maps_api_key", "bing_maps_api_key", "osm_nominatim_email"]:
        return ""
    return default


def _dummy_save_admin_setting(key, value): return False
def _dummy_list_products(
    category: str | None = None) -> list[dict[str, Any]]: return []


def _dummy_add_product(product_data: dict[str, Any]) -> int | None: return None
def _dummy_update_product(product_id: int | float,
                          product_data: dict[str, Any]) -> bool: return False


def _dummy_delete_product(product_id: int | float) -> bool: return False


def _dummy_get_product_by_id(
    product_id: int | float) -> dict[str, Any] | None: return None
def _dummy_get_product_by_model_name(
    model_name: str) -> dict[str, Any] | None: return None
def _dummy_list_product_categories(
) -> list[str]: return ["Modul", "Wechselrichter", "Batteriespeicher"]
def _dummy_list_companies() -> list[dict[str, Any]]: return []
def _dummy_add_company(company_data: dict[str, Any]) -> int | None: return None


def _dummy_get_company_by_id(
    company_id: int) -> dict[str, Any] | None: return None
def _dummy_update_company(
    company_id: int, company_data: dict[str, Any]) -> bool: return False


def _dummy_delete_company(company_id: int) -> bool: return False
def _dummy_set_default_company(company_id: int) -> bool: return False


def _dummy_add_company_document(
    company_id: int,
    display_name: str,
    document_type: str,
    original_filename: str,
    file_content_bytes: bytes) -> int | None: return None


def _dummy_list_company_documents(
    company_id: int, doc_type: str | None = None) -> list[dict[str, Any]]: return []


def _dummy_delete_company_document(document_id: int) -> bool: return False
# Old dummy CSV parsing function removed - now using MatrixLoader class


_load_admin_setting_safe: Callable = _dummy_load_admin_setting
_save_admin_setting_safe: Callable = _dummy_save_admin_setting
_list_products_safe: Callable = _dummy_list_products
_add_product_safe: Callable = _dummy_add_product
_update_product_safe: Callable = _dummy_update_product
_delete_product_safe: Callable = _dummy_delete_product
_get_product_by_id_safe: Callable = _dummy_get_product_by_id
_get_product_by_model_name_safe: Callable = _dummy_get_product_by_model_name
_list_product_categories_safe: Callable = _dummy_list_product_categories
_list_companies_safe: Callable = _dummy_list_companies
_add_company_safe: Callable = _dummy_add_company
_get_company_by_id_safe: Callable = _dummy_get_company_by_id
_update_company_safe: Callable = _dummy_update_company
_delete_company_safe: Callable = _dummy_delete_company
_set_default_company_safe: Callable = _dummy_set_default_company
_add_company_document_safe: Callable = _dummy_add_company_document
_list_company_documents_safe: Callable = _dummy_list_company_documents
_delete_company_document_safe: Callable = _dummy_delete_company_document

ADMIN_TAB_KEYS_DEFINITION_GLOBAL = [
    "admin_tab_company_management_new",
    "admin_tab_user_management",
    "admin_tab_product_management",
    "admin_tab_logo_management",
    "admin_tab_product_database_crud",
    "admin_tab_services_management",
    "admin_tab_general_settings",
    "admin_tab_intro_settings",
    "admin_tab_tariff_management",
    "admin_tab_pdf_design",
    "admin_tab_payment_terms",
    "admin_tab_visualization_settings",
    "admin_tab_advanced"]

# Icon-Mapping für Admin-Menü-Kategorien (Deutsche Emojis)
ADMIN_TAB_ICONS = {
    "admin_tab_company_management_new": "🏢",
    "admin_tab_user_management": "👥",
    "admin_tab_product_management": "📦",
    "admin_tab_logo_management": "🖼️",
    "admin_tab_product_database_crud": "🗄️",
    "admin_tab_services_management": "🛠️",
    "admin_tab_general_settings": "⚙️",
    "admin_tab_intro_settings": "🎬",
    "admin_tab_tariff_management": "💡",
    "admin_tab_pdf_design": "📝",
    "admin_tab_payment_terms": "💳",
    "admin_tab_visualization_settings": "📊",
    "admin_tab_ui_effects": "✨",
    "admin_tab_advanced": "🧠"
}

ADMIN_TAB_DESCRIPTIONS = {
    "admin_tab_company_management_new": "Stammdaten, Dokumente & Standardwerte",
    "admin_tab_user_management": "Benutzerrollen, Teams und Rechte",
    "admin_tab_product_management": "Produkte, Varianten und Preise verwalten",
    "admin_tab_logo_management": "Logos, Brand-Assets und Platzierungen",
    "admin_tab_product_database_crud": "Produktdatenbank synchronisieren und pflegen",
    "admin_tab_services_management": "Dienstleistungen strukturieren und bündeln",
    "admin_tab_general_settings": "Globale Parameter, Einheiten und Defaults",
    "admin_tab_intro_settings": "Intro-Inhalte und Onboarding-Story anpassen",
    "admin_tab_tariff_management": "Einspeisevergütungen & Tarife konfigurieren",
    "admin_tab_pdf_design": "PDF-Looks, Cover und Layouts definieren",
    "admin_tab_payment_terms": "Zahlungsbedingungen & Varianten steuern",
    "admin_tab_visualization_settings": "Themes, UI-Effekte, Charts & Farben",
    "admin_tab_advanced": "Erweiterte Tools, Debugging & Integrationen"}

# Deutsche Beschriftungen für Admin-Tabs
ADMIN_TAB_LABELS_DE = {
    "admin_tab_company_management_new": "Firmenverwaltung",
    "admin_tab_user_management": "Benutzerverwaltung",
    "admin_tab_product_management": "Produktverwaltung",
    "admin_tab_logo_management": "Logo-Verwaltung",
    "admin_tab_product_database_crud": "Produktdatenbank",
    "admin_tab_services_management": "Dienstleistungen Management",
    "admin_tab_general_settings": "Allgemeine Einstellungen",
    "admin_tab_intro_settings": "Intro-Einstellungen",
    "admin_tab_tariff_management": "Einspeisung Tarifverwaltung",
    "admin_tab_pdf_design": "PDF-Design Einstellungen",
    "admin_tab_payment_terms": "Zahlungsbedingungen Einstellungen",
    "admin_tab_visualization_settings": "Anzeigeeinstellungen",
    "admin_tab_ui_effects": "UI-Effekte",
    "admin_tab_advanced": "Erweiterte Einstellungen"
}


def _render_horizontal_menu_selector(
    state_key: str,
    options: list[tuple[str, str]],
    icons: dict[str, str] | None = None,
    *,
    label: str | None = None,
    help_text: str | None = None,
) -> str:
    """Render a modern vertical sidebar menu with glassmorphism design."""

    if not options:
        raise ValueError(
            "_render_horizontal_menu_selector requires at least one option")

    option_keys = [opt_key for opt_key, _ in options]
    option_labels = {opt_key: opt_label for opt_key, opt_label in options}
    default_key = option_keys[0]

    ensure_session_defaults({state_key: default_key})
    if st.session_state.get(state_key) not in option_keys:
        st.session_state[state_key] = default_key
    keep_session_state_alive([state_key])

    current_selection = st.session_state.get(state_key, default_key)

    if label:
        st.markdown(f"### {label}")
    if help_text:
        st.caption(help_text)

    icons = icons or {}

    # Modern glassmorphism sidebar navigation
    st.markdown(
        """
        <style>
        .admin-nav-container {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
            border-radius: 16px;
            padding: 8px;
            margin: 16px 0;
            border: 1px solid rgba(148, 163, 184, 0.15);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
        }

        .admin-nav-item {
            position: relative;
            margin: 4px 0;
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .admin-nav-item button {
            width: 100%;
            text-align: left;
            padding: 14px 16px !important;
            border: 1px solid transparent !important;
            background: rgba(51, 65, 85, 0.4) !important;
            border-radius: 12px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            color: rgba(226, 232, 240, 0.85) !important;
            transition: all 0.25s ease !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .admin-nav-item button:hover {
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.25) 0%, rgba(37, 99, 235, 0.2) 100%) !important;
            border-color: rgba(96, 165, 250, 0.3) !important;
            color: #e0e7ff !important;
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }

        .admin-nav-item.active button {
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.9) 0%, rgba(37, 99, 235, 0.85) 100%) !important;
            border-color: rgba(147, 197, 253, 0.6) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .admin-nav-icon {
            display: inline-block;
            width: 24px;
            margin-right: 10px;
            font-size: 16px;
            text-align: center;
        }

        .admin-nav-label {
            display: inline-block;
            vertical-align: middle;
        }

        .admin-nav-badge {
            float: right;
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 10px;
            background: rgba(34, 197, 94, 0.2);
            color: #86efac;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .admin-nav-item.active .admin-nav-badge {
            background: rgba(255, 255, 255, 0.25);
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="admin-nav-container">', unsafe_allow_html=True)

    for option_key in option_keys:
        icon = icons.get(option_key, "📋")
        display_label = option_labels[option_key]
        description = ADMIN_TAB_DESCRIPTIONS.get(option_key, "")
        is_active = option_key == current_selection

        # VEREINFACHTER FIX: Buttons OHNE HTML-Wrapper
        # Das HTML interferiert mit Streamlit's Button-Event-Handling
        if st.button(
            f"{icon} {display_label}",
            key=f"{state_key}_{option_key}",
            help=description,
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state[state_key] = option_key
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.session_state[f"{state_key}_last_change"] = datetime.utcnow(
    ).isoformat()
    return st.session_state.get(state_key, current_selection)


def _render_stateful_selector(
    state_key: str,
    options: list[tuple[str, str]],
    *,
    label: str | None = None,
    help_text: str | None = None,
    widget_suffix: str = "",
) -> str:
    """Render a radio/select control whose selection persists across reruns.

    Args:
        state_key: Session-State key that stores the selected option key.
        options: List of ``(option_key, display_label)`` tuples.
        label: Optional label for the control (falls back to generic text).
        help_text: Optional tooltip text.
        widget_suffix: Extra suffix to keep widget keys unique per context.

    Returns:
        The selected option key.
    """

    if not options:
        raise ValueError(
            "_render_stateful_selector requires at least one option")

    option_keys = [opt[0] for opt in options]
    option_labels = {opt_key: opt_label for opt_key, opt_label in options}
    default_key = option_keys[0]

    ensure_session_defaults({state_key: default_key})
    if st.session_state.get(state_key) not in option_keys:
        st.session_state[state_key] = default_key
    keep_session_state_alive([state_key])

    widget_key = mirror_widget_value(
        state_key,
        default_key,
        widget_key=f"{state_key}_widget{widget_suffix}")
    label_text = label or "Bereich auswählen"
    label_visibility = "visible" if label else "collapsed"

    radio_kwargs: dict[str, Any] = {
        "label": label_text,
        "options": option_keys,
        "format_func": lambda opt_key: option_labels.get(opt_key, opt_key),
        "key": widget_key,
        "label_visibility": label_visibility,
    }
    if help_text:
        radio_kwargs["help"] = help_text

    try:
        radio_kwargs["horizontal"] = True
        selected_value = st.radio(**radio_kwargs)
    except TypeError:
        radio_kwargs.pop("horizontal", None)
        selected_value = st.selectbox(**radio_kwargs)

    commit_widget_value(state_key, widget_key=widget_key)

    current_value = st.session_state.get(state_key, selected_value)
    if current_value != selected_value:
        st.session_state[state_key] = selected_value
        current_value = selected_value

    st.session_state[f"{state_key}_last_change"] = datetime.utcnow(
    ).isoformat()
    return current_value


def get_text_local(key: str, fallback_text: str) -> str:
    admin_texts_dict = st.session_state.get('_admin_panel_texts', {})
    if not isinstance(admin_texts_dict, dict):
        admin_texts_dict = {}
    return admin_texts_dict.get(key, fallback_text)


def render_company_crud_tab(
    db_list_companies_func: Callable[[], list[dict[str, Any]]],
    db_add_company_func: Callable[[dict[str, Any]], int | None],
    db_get_company_by_id_func: Callable[[int], dict[str, Any] | None],
    db_update_company_func: Callable[[int, dict[str, Any]], bool],
    db_delete_company_func: Callable[[int], bool],
    db_set_default_company_func: Callable[[int], bool],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    db_add_company_document_func: Callable[[int, str, str, str, bytes], int | None],
    db_list_company_documents_func: Callable[[int, str | None], list[dict[str, Any]]],
    db_delete_company_document_func: Callable[[int], bool]
):
    st.subheader(
        get_text_local(
            "admin_tab_company_management_new",
            "Firmenverwaltung (Mandanten)"))

    if 'editing_company_id' not in st.session_state:
        st.session_state.editing_company_id = None

    active_company_id_str = load_admin_setting_func('active_company_id', None)
    active_company_id = None
    if active_company_id_str is not None:
        try:
            active_company_id = int(active_company_id_str)
        except (ValueError, TypeError):
            st.warning(
                f"Ungültige active_company_id '{active_company_id_str}' in Admin-Settings.")

    active_company_details_display = db_get_company_by_id_func(
        active_company_id) if active_company_id is not None else None

    if active_company_details_display:
        st.info(
            f"Aktuell aktive Firma für Angebote: **{
                active_company_details_display.get(
                    'name',
                    'N/A')}** (ID: {active_company_id})")
    else:
        st.warning("Es ist keine Firma als 'aktiv' für die Angebotserstellung ausgewählt. Bitte eine Firma als Standard festlegen oder eine anlegen.")
    st.markdown("---")

    # PDF-Batch-Import in Company Management entfernt (auf Wunsch)

    form_title = get_text_local(
        "admin_add_new_company_header",
        "Neue Firma anlegen")
    submit_button_label = get_text_local(
        "admin_add_company_button", "Firma anlegen")
    company_data_for_form = {}
    if st.session_state.editing_company_id:
        company_to_edit = db_get_company_by_id_func(
            st.session_state.editing_company_id)
        if company_to_edit:
            company_data_for_form = company_to_edit
            form_title = get_text_local(
                "admin_edit_company_header",
                "Firma bearbeiten:") + f" {
                company_data_for_form.get(
                    'name',
                    '')}"
            submit_button_label = get_text_local(
                "admin_save_company_button", "Änderungen speichern")
        else:
            st.error(
                f"Firma mit ID {
                    st.session_state.editing_company_id} nicht gefunden. Bearbeitungsmodus zurückgesetzt.")
            st.session_state.editing_company_id = None

    expander_title = form_title
    _all_companies_temp_list = db_list_companies_func()
    expander_expanded_default = (
        st.session_state.editing_company_id is not None or not _all_companies_temp_list)

    with st.expander(expander_title, expanded=expander_expanded_default):
        form_key_company_ui_crud = f"company_form_ui_crud_{
            st.session_state.editing_company_id or 'new_company_v16_admin_definitiv'}"
        with st.form(key=form_key_company_ui_crud, clear_on_submit=False):
            c_name = st.text_input(
                get_text_local(
                    "admin_company_name_label",
                    "Firmenname"),
                value=company_data_for_form.get(
                    "name",
                    ""),
                key=f"{form_key_company_ui_crud}_name")
            uploaded_logo_file_ui_crud = st.file_uploader(
                get_text_local(
                    "admin_company_logo_upload_label",
                    "Firmenlogo (PNG, JPG, max. 2MB)"),
                type=[
                    "png",
                    "jpg",
                    "jpeg"],
                key=f"{form_key_company_ui_crud}_logo_upload")
            current_logo_b64_form_crud = company_data_for_form.get(
                "logo_base64")
            if current_logo_b64_form_crud and not uploaded_logo_file_ui_crud and st.session_state.editing_company_id:
                try:
                    st.image(
                        base64.b64decode(current_logo_b64_form_crud),
                        caption=get_text_local(
                            "admin_current_logo_caption",
                            "Aktuelles Logo"),
                        width=100)
                except Exception:
                    pass

            c_street = st.text_input(
                get_text_local(
                    "admin_company_street_label",
                    "Straße & Nr."),
                value=company_data_for_form.get(
                    "street",
                    ""),
                key=f"{form_key_company_ui_crud}_street")
            c_zip = st.text_input(
                get_text_local(
                    "admin_company_zip_label", "PLZ"), value=company_data_for_form.get(
                    "zip_code", ""), key=f"{form_key_company_ui_crud}_zip")
            c_city = st.text_input(
                get_text_local(
                    "admin_company_city_label", "Ort"), value=company_data_for_form.get(
                    "city", ""), key=f"{form_key_company_ui_crud}_city")
            c_phone = st.text_input(
                get_text_local(
                    "admin_company_phone_label",
                    "Telefon"),
                value=company_data_for_form.get(
                    "phone",
                    ""),
                key=f"{form_key_company_ui_crud}_phone")
            c_email = st.text_input(
                get_text_local(
                    "admin_company_email_label",
                    "E-Mail"),
                value=company_data_for_form.get(
                    "email",
                    ""),
                key=f"{form_key_company_ui_crud}_email")
            c_web = st.text_input(
                get_text_local(
                    "admin_company_website_label",
                    "Webseite"),
                value=company_data_for_form.get(
                    "website",
                    ""),
                key=f"{form_key_company_ui_crud}_web")
            c_tax = st.text_input(
                get_text_local(
                    "admin_company_tax_id_label",
                    "Steuernr./USt-ID"),
                value=company_data_for_form.get(
                    "tax_id",
                    ""),
                key=f"{form_key_company_ui_crud}_tax")
            c_reg = st.text_input(
                get_text_local(
                    "admin_company_commercial_register_label",
                    "Handelsregister"),
                value=company_data_for_form.get(
                    "commercial_register",
                    ""),
                key=f"{form_key_company_ui_crud}_reg")
            c_bank = st.text_area(
                get_text_local(
                    "admin_company_bank_details_label",
                    "Bankverbindung"),
                value=company_data_for_form.get(
                    "bank_details",
                    ""),
                height=80,
                key=f"{form_key_company_ui_crud}_bank")
            c_footer = st.text_area(
                get_text_local(
                    "admin_company_footer_text_label",
                    "PDF Fußzeilentext"),
                value=company_data_for_form.get(
                    "pdf_footer_text",
                    ""),
                height=80,
                key=f"{form_key_company_ui_crud}_footer")
            submitted_company_form_btn_crud = st.form_submit_button(
                submit_button_label)

        if submitted_company_form_btn_crud:
            company_name_stripped_crud = c_name.strip() if isinstance(c_name, str) else ""
            if not company_name_stripped_crud:
                st.error(
                    get_text_local(
                        "admin_company_name_required_error",
                        "Firmenname ist ein Pflichtfeld."))
            else:
                data_for_db_crud = {
                    "name": company_name_stripped_crud,
                    "street": c_street.strip() if isinstance(c_street, str) else None,
                    "zip_code": c_zip.strip() if isinstance(c_zip, str) else None,
                    "city": c_city.strip() if isinstance(c_city, str) else None,
                    "phone": c_phone.strip() if isinstance(c_phone, str) else None,
                    "email": c_email.strip() if isinstance(c_email, str) else None,
                    "website": c_web.strip() if isinstance(c_web, str) else None,
                    "tax_id": c_tax.strip() if isinstance(c_tax, str) else None,
                    "commercial_register": c_reg.strip() if isinstance(c_reg, str) else None,
                    "bank_details": c_bank.strip() if isinstance(c_bank, str) else None,
                    "pdf_footer_text": c_footer.strip() if isinstance(c_footer, str) else None
                }
                if uploaded_logo_file_ui_crud is not None:
                    if uploaded_logo_file_ui_crud.size > 2 * 1024 * 1024:
                        st.error(
                            get_text_local(
                                "admin_error_logo_too_large",
                                "Logo-Datei ist zu groß (max. 2MB). Altes Logo wird beibehalten, falls vorhanden."))
                        data_for_db_crud["logo_base64"] = current_logo_b64_form_crud
                    else:
                        data_for_db_crud["logo_base64"] = base64.b64encode(
                            uploaded_logo_file_ui_crud.getvalue()).decode('utf-8')
                elif st.session_state.editing_company_id:
                    data_for_db_crud["logo_base64"] = current_logo_b64_form_crud
                else:
                    data_for_db_crud["logo_base64"] = None

                if st.session_state.editing_company_id:
                    if db_update_company_func(
                            st.session_state.editing_company_id,
                            data_for_db_crud):
                        st.success(
                            get_text_local(
                                "admin_company_updated_success",
                                "Firma erfolgreich aktualisiert."))
                        st.session_state.editing_company_id = None
                        set_current_page("admin")
                    else:
                        st.error(
                            get_text_local(
                                "admin_company_update_error",
                                "Fehler beim Aktualisieren der Firma."))
                else:
                    new_company_id_crud = db_add_company_func(data_for_db_crud)
                    if new_company_id_crud:
                        st.success(
                            get_text_local(
                                "admin_company_added_success_param",
                                "Firma '{company_name}' erfolgreich angelegt.").format(
                                company_name=company_name_stripped_crud))
                        if len(db_list_companies_func()) == 1:
                            if db_set_default_company_func(
                                    new_company_id_crud):
                                st.info(
                                    get_text_local(
                                        "admin_info_company_set_default_param",
                                        "Firma '{company_name}' wurde als Standard und aktive Firma gesetzt.").format(
                                        company_name=company_name_stripped_crud))
                            else:
                                st.warning(
                                    get_text_local(
                                        "admin_warning_company_set_default_failed",
                                        "Konnte Firma nicht automatisch als Standard/Aktiv setzen."))
                        st.session_state.editing_company_id = None
                        set_current_page("admin")
                    else:
                        st.error(
                            get_text_local(
                                "admin_company_add_error",
                                "Fehler beim Anlegen der Firma. Existiert der Name bereits?"))

        if st.session_state.editing_company_id:
            if st.button(
                get_text_local(
                    "admin_finish_edit_company_button",
                    "Bearbeitung abschließen / Neue Firma anlegen"),
                key=f"finish_edit_company_btn_ui_crud_{
                    st.session_state.editing_company_id}_v16_admin_definitiv"):
                st.session_state.editing_company_id = None
                set_current_page("admin")

            current_company_id_for_docs_crud = st.session_state.editing_company_id
            st.markdown("---")

            # =================================================================
            # NEUE TABS FÜR FIRMENSPEZIFISCHE ANGEBOTSVORLAGEN
            # =================================================================

            selector_state_key = f"admin_company_detail_tab_{current_company_id_for_docs_crud}{WIDGET_KEY_SUFFIX}"
            selected_company_tab = _render_stateful_selector(
                selector_state_key,
                [
                    ("documents", " Dokumente"),
                    ("text_templates", " Textvorlagen"),
                    ("image_templates", " Bildvorlagen"),
                ],
                label=get_text_local("admin_company_detail_selector", "Bereich auswählen"),
                widget_suffix=f"_{current_company_id_for_docs_crud}",
            )
            st.markdown("---")

            if selected_company_tab == "documents":
                st.subheader(
                    get_text_local(
                        "admin_company_documents_header",
                        "Dokumente für diese Firma verwalten"))

                DOCUMENT_TYPES_AVAILABLE_CRUD = [
                    "AGB",
                    "Datenschutz",
                    "Vollmacht",
                    "SEPA-Mandat",
                    "Freistellungsbescheinigung",
                    "Sonstiges"]

                form_key_doc_upload_crud = f"company_document_upload_form_crud_{current_company_id_for_docs_crud}_v16_admin_definitiv"
                with st.form(key=form_key_doc_upload_crud, clear_on_submit=True):
                    st.markdown(
                        "**" +
                        get_text_local(
                            "admin_upload_new_document_header",
                            "Neues Dokument hochladen:") +
                        "**")
                    doc_display_name_upload_crud = st.text_input(
                        get_text_local(
                            "admin_doc_display_name_label",
                            "Anzeigename des Dokuments (z.B. AGB Stand 01/2024)"),
                        key=f"doc_disp_name_upload_crud_{current_company_id_for_docs_crud}_v16_admin_definitiv")
                    doc_type_upload_crud = st.selectbox(
                        get_text_local("admin_doc_type_label", "Dokumententyp"),
                        options=DOCUMENT_TYPES_AVAILABLE_CRUD,
                        key=f"doc_type_upload_crud_{current_company_id_for_docs_crud}_v16_admin_definitiv"
                    )
                    uploaded_pdf_file_doc_crud = st.file_uploader(
                        get_text_local(
                            "admin_doc_pdf_upload_label",
                            "PDF-Dokument auswählen (max. 5MB)"),
                        type=["pdf"],
                        key=f"doc_pdf_upload_crud_{current_company_id_for_docs_crud}_v16_admin_definitiv")
                    submitted_doc_upload_btn_crud = st.form_submit_button(get_text_local(
                        "admin_doc_upload_button", "Dokument hochladen & speichern"))

                    if submitted_doc_upload_btn_crud:
                        doc_display_name_val_crud = str(doc_display_name_upload_crud).strip(
                        ) if doc_display_name_upload_crud else ""
                        if not doc_display_name_val_crud:
                            st.error(
                                get_text_local(
                                    "admin_error_doc_display_name_required",
                                    "Bitte einen Anzeigenamen für das Dokument eingeben."))
                        elif not uploaded_pdf_file_doc_crud:
                            st.error(
                                get_text_local(
                                    "admin_error_doc_file_required",
                                    "Bitte eine PDF-Datei für das Dokument auswählen."))
                        elif uploaded_pdf_file_doc_crud.size > 5 * 1024 * 1024:
                            st.error(
                                get_text_local(
                                    "admin_error_doc_file_too_large",
                                    "Dokument-Datei ist zu groß (max. 5MB)."))
                        else:
                            file_bytes_doc_crud = uploaded_pdf_file_doc_crud.getvalue()
                            original_filename_doc_crud = uploaded_pdf_file_doc_crud.name
                            doc_id_db_crud = db_add_company_document_func(
                                current_company_id_for_docs_crud,
                                doc_display_name_val_crud,
                                doc_type_upload_crud,
                                original_filename_doc_crud,
                                file_bytes_doc_crud
                            )
                            if doc_id_db_crud:
                                st.success(
                                    get_text_local(
                                        "admin_success_doc_uploaded_param",
                                        "Dokument '{doc_name}' erfolgreich hochgeladen.").format(
                                        doc_name=doc_display_name_val_crud))
                                set_current_page("admin")
                            else:
                                st.error(
                                    get_text_local(
                                        "admin_error_doc_saving_to_db",
                                        "Fehler beim Speichern des Dokuments in der Datenbank."))

                company_documents_list_crud = db_list_company_documents_func(
                    current_company_id_for_docs_crud, None)
                if company_documents_list_crud:
                    st.markdown(
                        "**" +
                        get_text_local(
                            "admin_existing_documents_header",
                            "Vorhandene Dokumente:") +
                        "**")
                    for doc_item_crud in company_documents_list_crud:
                        doc_id_list_crud = doc_item_crud['id']
                        cols_doc_display_crud = st.columns([3, 2, 3, 1])
                        cols_doc_display_crud[0].markdown(
                            f"**{doc_item_crud.get('display_name')}**")
                        cols_doc_display_crud[1].caption(
                            f"Typ: {doc_item_crud.get('document_type')}")
                        cols_doc_display_crud[2].caption(
                            f"Datei: {doc_item_crud.get('file_name')}")

                        delete_doc_btn_key_list_crud = f"delete_company_doc_btn_crud_{doc_id_list_crud}_v16_admin_definitiv"
                        confirm_delete_doc_session_key_crud = f"confirm_delete_company_doc_sess_crud_{doc_id_list_crud}_v16_admin_definitiv"

                        if cols_doc_display_crud[3].button(
                                "", key=delete_doc_btn_key_list_crud, help="Dokument löschen"):
                            if st.session_state.get(
                                    confirm_delete_doc_session_key_crud, False):
                                if db_delete_company_document_func(
                                        doc_id_list_crud):
                                    st.success(
                                        get_text_local(
                                            "admin_success_doc_deleted_param",
                                            "Dokument '{doc_name}' gelöscht.").format(
                                            doc_name=doc_item_crud.get('display_name')))
                                    # if confirm_delete_doc_session_key_crud in st.session_state:
                                    # del
                                    # st.session_state[confirm_delete_doc_session_key_crud]
                                    # # Auskommentiert für Robustheit
                                    set_current_page("admin")
                                else:
                                    st.error(
                                        get_text_local(
                                            "admin_error_deleting_doc_param",
                                            "Fehler beim Löschen des Dokuments '{doc_name}'.").format(
                                            doc_name=doc_item_crud.get('display_name')))
                            else:
                                st.session_state[confirm_delete_doc_session_key_crud] = True
                                st.warning(
                                    get_text_local(
                                        "admin_warning_confirm_delete_doc_param",
                                        "Sicher, dass Dokument '{doc_name}' gelöscht werden soll? Erneut 'Löschen' klicken.").format(
                                        doc_name=doc_item_crud.get('display_name')))
                                set_current_page("admin")

            elif selected_company_tab == "text_templates":
                render_company_text_templates_tab(
                    current_company_id_for_docs_crud)

            elif selected_company_tab == "image_templates":
                render_company_image_templates_tab(
                    current_company_id_for_docs_crud)

            st.markdown("---")

    st.markdown("---")
    st.subheader(
        get_text_local(
            "admin_existing_companies_header",
            "Vorhandene Firmen"))

    active_company_id_for_list_display_str_crud = load_admin_setting_func(
        'active_company_id', None)
    active_company_id_for_list_display_crud = None
    if active_company_id_for_list_display_str_crud is not None:
        try:
            active_company_id_for_list_display_crud = int(
                active_company_id_for_list_display_str_crud)
        except (ValueError, TypeError):
            active_company_id_for_list_display_crud = None

    all_companies_list_crud = db_list_companies_func()
    if not all_companies_list_crud:
        st.info(
            get_text_local(
                "admin_no_companies_info",
                "Es wurden noch keine Firmen angelegt."))
    else:
        header_cols_crud = st.columns([0.5, 2, 1, 1, 1, 0.5, 0.5, 1.5])
        column_headers_crud = [
            "ID",
            "Firmenname",
            "Logo",
            "Standard",
            "Aktiv",
            "",
            "",
            "Als Standard/Aktiv"]
        for col_idx_crud, header_title_crud in enumerate(column_headers_crud):
            header_cols_crud[col_idx_crud].markdown(f"**{header_title_crud}**")

        for company_list_item_crud in all_companies_list_crud:
            company_id_item_int_crud = company_list_item_crud.get('id')
            row_cols_crud = st.columns([0.5, 2, 1, 1, 1, 0.5, 0.5, 1.5])
            row_cols_crud[0].write(
                str(company_id_item_int_crud) if company_id_item_int_crud is not None else "FEHLER")
            row_cols_crud[1].write(company_list_item_crud.get('name', 'N/A'))
            company_logo_b64_list_view_crud = company_list_item_crud.get(
                'logo_base64')
            if company_logo_b64_list_view_crud:
                try:
                    row_cols_crud[2].image(
                        base64.b64decode(company_logo_b64_list_view_crud), width=40)
                except Exception:
                    row_cols_crud[2].caption("err")
            else:
                row_cols_crud[2].caption("-")
            is_db_default_list_crud = company_list_item_crud.get(
                'is_default') == 1
            row_cols_crud[3].write("" if is_db_default_list_crud else "")
            is_currently_active_item_crud = (active_company_id_for_list_display_crud is not None and
                                             company_id_item_int_crud is not None and
                                             active_company_id_for_list_display_crud == company_id_item_int_crud)
            row_cols_crud[4].write("" if is_currently_active_item_crud else "")
            if company_id_item_int_crud is not None:
                if row_cols_crud[5].button(
                    "",
                    key=f"edit_company_list_btn_crud_{company_id_item_int_crud}_v16_admin_definitiv",
                        help="Bearbeiten"):
                    st.session_state.editing_company_id = company_id_item_int_crud
                    set_current_page("admin")
                confirm_del_key_list_item_crud = f"confirm_delete_company_list_item_crud_{company_id_item_int_crud}_v16_admin_definitiv"
                if row_cols_crud[6].button(
                    "",
                    key=f"delete_company_list_btn_crud_{company_id_item_int_crud}_v16_admin_definitiv",
                        help="Löschen"):
                    if st.session_state.get(
                            confirm_del_key_list_item_crud, False):
                        if db_delete_company_func(company_id_item_int_crud):
                            st.success(
                                get_text_local(
                                    "admin_success_company_deleted_param",
                                    "Firma '{company_name}' gelöscht.").format(
                                    company_name=company_list_item_crud.get('name')))
                            # if confirm_del_key_list_item_crud in
                            # st.session_state: del
                            # st.session_state[confirm_del_key_list_item_crud]
                            # # Auskommentiert
                            if st.session_state.editing_company_id == company_id_item_int_crud:
                                st.session_state.editing_company_id = None
                            set_current_page("admin")
                        else:
                            st.error(
                                get_text_local(
                                    "admin_error_deleting_company_param",
                                    "Fehler Löschen Firma '{company_name}'.").format(
                                    company_name=company_list_item_crud.get('name')))
                    else:
                        st.session_state[confirm_del_key_list_item_crud] = True
                        st.warning(
                            get_text_local(
                                "admin_warning_confirm_delete_company_param",
                                "Sicher Firma '{company_name}' löschen? Erneut klicken.").format(
                                company_name=company_list_item_crud.get('name')))
                        set_current_page("admin")
                if not is_currently_active_item_crud or not is_db_default_list_crud:
                    if row_cols_crud[7].button(
                            get_text_local(
                                "admin_set_company_default_button",
                                "Als Standard/Aktiv"),
                            key=f"set_default_list_btn_crud_{company_id_item_int_crud}_v16_admin_definitiv"):
                        if db_set_default_company_func(
                                company_id_item_int_crud):
                            st.success(
                                get_text_local(
                                    "admin_success_company_set_default_param",
                                    "Firma '{company_name}' als Standard/Aktiv gesetzt.").format(
                                    company_name=company_list_item_crud.get('name')))
                            set_current_page("admin")
                        else:
                            st.error(
                                get_text_local(
                                    "admin_error_setting_default_company",
                                    "Fehler Setzen Standardfirma."))
                else:
                    row_cols_crud[7].markdown("*(Std/Aktiv)*")
            else:
                row_cols_crud[5].caption("-")
                row_cols_crud[6].caption("-")
                row_cols_crud[7].caption("-")
            st.markdown("---")


def render_services_management_tab():
    """Render services management tab"""
    try:
        render_services_admin_ui()
    except Exception as e:
        st.error(f"Fehler beim Laden der Services-Verwaltung: {str(e)}")
        st.info("Bitte überprüfen Sie die admin_services_ui.py Datei")


def render_product_management(
        list_products_func,
        add_product_func,
        update_product_func,
        delete_product_func,
        get_product_by_id_func,
        list_product_categories_func,
        get_product_by_model_name_func):

    if 'product_to_edit_id_manual' not in st.session_state:
        st.session_state.product_to_edit_id_manual = None

    product_categories_manual_list = list_product_categories_func()

    if not product_categories_manual_list:  # KORRIGIERTE Zeile 679
        product_categories_manual_list = [
            "Modul",
            "Wechselrichter",
            "Batteriespeicher",
            "Wallbox",
            "Zubehör",
            "Sonstiges"]

    product_data_for_manual_form = {}
    form_manual_title = get_text_local(
        "admin_add_new_product_header_manual",
        "Neues Produkt manuell anlegen / Bearbeiten")

    if st.session_state.product_to_edit_id_manual:
        product_to_edit_manual_data = get_product_by_id_func(
            st.session_state.product_to_edit_id_manual)
        if product_to_edit_manual_data:
            product_data_for_manual_form = product_to_edit_manual_data
            form_manual_title = f"Produkt bearbeiten: {
                product_data_for_manual_form.get(
                    'model_name', '')} (ID: {
                st.session_state.product_to_edit_id_manual})"
        else:
            st.error(
                f"Produkt mit ID {
                    st.session_state.product_to_edit_id_manual} nicht gefunden.")
            st.session_state.product_to_edit_id_manual = None

    with st.expander(form_manual_title, expanded=(st.session_state.product_to_edit_id_manual is not None or not list_products_func(None))):
        form_key_manual_prod_ui = f"product_form_manual_ui_man_{
            st.session_state.product_to_edit_id_manual or 'new_prod_man'}{WIDGET_KEY_SUFFIX}"
        with st.form(key=form_key_manual_prod_ui, clear_on_submit=False):
            # Helper für sichere Numerik-Konvertierung (None -> 0 / 0.0)
            def _safe_float(v, default=0.0):
                try:
                    if v is None or (isinstance(v, str) and v.strip() == ""):
                        return float(default)
                    return float(v)
                except Exception:
                    return float(default)

            def _safe_int(v, default=0):
                try:
                    if v is None or (isinstance(v, str) and v.strip() == ""):
                        return int(default)
                    return int(float(v))
                except Exception:
                    return int(default)
            st.text_input(
                "Produkt ID",
                value=str(
                    st.session_state.product_to_edit_id_manual) if st.session_state.product_to_edit_id_manual else "Automatisch",
                disabled=True,
                key=f"{form_key_manual_prod_ui}_id_man")
            p_model_name_form = st.text_input(
                label=get_text_local(
                    "product_model_name_label",
                    "Modellname*"),
                value=product_data_for_manual_form.get(
                    'model_name',
                    ''),
                key=f"{form_key_manual_prod_ui}_model_name_man")
            available_cats_form = [cat for cat in product_categories_manual_list if cat and str(
                cat).lower() != "ohne speicher"]
            default_cat_idx = 0
            current_cat_val = product_data_for_manual_form.get('category')
            if current_cat_val and current_cat_val in available_cats_form:
                default_cat_idx = available_cats_form.index(current_cat_val)
            p_category_form = st.selectbox(
                label=get_text_local(
                    "product_category_label",
                    "Kategorie*"),
                options=available_cats_form,
                index=default_cat_idx,
                key=f"{form_key_manual_prod_ui}_category_man",
                disabled=not available_cats_form)
            p_brand_form = st.text_input(
                label=get_text_local(
                    "product_brand_label", "Hersteller"), value=product_data_for_manual_form.get(
                    'brand', ''), key=f"{form_key_manual_prod_ui}_brand_man")
            p_price_form = st.number_input(
                label=get_text_local(
                    "product_price_euro_label",
                    "Preis (€)"),
                min_value=0.0,
                value=_safe_float(
                    product_data_for_manual_form.get(
                        'price_euro',
                        0.0)),
                step=0.01,
                format="%.2f",
                key=f"{form_key_manual_prod_ui}_price_man")
            p_add_cost_form = st.number_input(
                label=get_text_local(
                    "product_additional_cost_netto_label",
                    "Zusatzkosten Netto (€)"),
                min_value=0.0,
                value=_safe_float(
                    product_data_for_manual_form.get(
                        'additional_cost_netto',
                        0.0)),
                step=0.01,
                format="%.2f",
                key=f"{form_key_manual_prod_ui}_add_cost_man")
            p_warranty_form = st.number_input(
                label=get_text_local(
                    "product_warranty_years_label",
                    "Garantie (Jahre)"),
                min_value=0,
                value=_safe_int(
                    product_data_for_manual_form.get(
                        'warranty_years',
                        0)),
                step=1,
                key=f"{form_key_manual_prod_ui}_warranty_man")

            st.markdown(
                "**" +
                get_text_local(
                    "product_image_header",
                    "Produktbild") +
                "**")
            uploaded_product_image_manual_file_form = st.file_uploader(
                get_text_local(
                    "product_image_upload_label",
                    "Produktbild (PNG, JPG, max. 2MB)"),
                type=[
                    "png",
                    "jpg",
                    "jpeg"],
                key=f"{form_key_manual_prod_ui}_image_upload_man")
            current_product_image_b64_form = product_data_for_manual_form.get(
                "image_base64")

            # Zeige aktuelles Bild an
            if current_product_image_b64_form and not uploaded_product_image_manual_file_form and st.session_state.product_to_edit_id_manual:
                try:
                    st.image(
                        base64.b64decode(current_product_image_b64_form),
                        caption=get_text_local(
                            "product_current_image_caption",
                            "Aktuelles Produktbild"),
                        width=100)
                    st.caption(
                        f"Aktuelle Bildgröße: {
                            len(current_product_image_b64_form)} Zeichen (Base64)")
                except Exception:
                    st.warning("Aktuelles Bild konnte nicht angezeigt werden.")
            elif not current_product_image_b64_form and st.session_state.product_to_edit_id_manual:
                st.info(
                    "ℹ️ Kein Produktbild vorhanden. Laden Sie ein neues Bild hoch.")

            # Zeige Upload-Vorschau
            if uploaded_product_image_manual_file_form:
                st.image(
                    uploaded_product_image_manual_file_form,
                    caption=f"🆕 Neues Bild: {
                        uploaded_product_image_manual_file_form.name} ({
                        uploaded_product_image_manual_file_form.size} Bytes)",
                    width=100)

            st.markdown(
                "**" +
                get_text_local(
                    "product_datasheet_header",
                    "Produktdatenblatt (PDF)") +
                "**")
            uploaded_datasheet_pdf_file_form = st.file_uploader(
                get_text_local(
                    "product_datasheet_upload_label",
                    "Datenblatt-PDF hochladen (max. 5MB)"),
                type="pdf",
                key=f"{form_key_manual_prod_ui}_datasheet_upload_man")
            current_datasheet_link = product_data_for_manual_form.get(
                "datasheet_link_db_path")

            # Zeige aktuelles Datenblatt an
            if current_datasheet_link:
                st.caption(
                    f"{
                        get_text_local(
                            'product_current_datasheet_caption',
                            'Aktuelles Datenblatt')}: `{current_datasheet_link}`")
            elif st.session_state.product_to_edit_id_manual:
                st.info(
                    "ℹ️ Kein Datenblatt vorhanden. Laden Sie ein PDF-Datenblatt hoch.")

            # Zeige Upload-Vorschau
            if uploaded_datasheet_pdf_file_form:
                st.caption(
                    f"🆕 Neues Datenblatt: {
                        uploaded_datasheet_pdf_file_form.name} ({
                        uploaded_datasheet_pdf_file_form.size} Bytes)")

            st.markdown(
                f"**{
                    get_text_local(
                        'product_category_specific_fields_header',
                        'Spezifische Felder für Kategorie')}: {
                    p_category_form or get_text_local(
                        'product_no_category_selected',
                        'Keine Kategorie gewählt')}**")
            p_capacity_w_val, p_power_kw_val, p_storage_power_kw_val, p_efficiency_percent_val, p_length_m_val, p_width_m_val, p_weight_kg_val, p_max_cycles_val = None, None, None, None, None, None, None, None
            if p_category_form == 'Modul':
                p_capacity_w_val = st.number_input(
                    label=get_text_local(
                        "module_capacity_w_label", "Leistung (Wp)"), min_value=0.0, value=_safe_float(
                        product_data_for_manual_form.get(
                            'capacity_w', 0.0)), step=1.0, key=f"{form_key_manual_prod_ui}_cap_w_man")
                p_efficiency_percent_val = st.number_input(
                    label=get_text_local(
                        "module_efficiency_percent_label",
                        "Wirkungsgrad (%)"),
                    min_value=0.0,
                    max_value=100.0,
                    value=_safe_float(
                        product_data_for_manual_form.get(
                            'efficiency_percent',
                            0.0)),
                    step=0.01,
                    format="%.2f",
                    key=f"{form_key_manual_prod_ui}_eff_mod_man")
                m_c1, m_c2 = st.columns(2)
                p_length_m_val = m_c1.number_input(
                    label=get_text_local(
                        "module_length_m_label",
                        "Länge (m)"),
                    min_value=0.0,
                    value=_safe_float(
                        product_data_for_manual_form.get(
                            'length_m',
                            0.0)),
                    step=0.001,
                    format="%.3f",
                    key=f"{form_key_manual_prod_ui}_len_man")
                p_width_m_val = m_c2.number_input(
                    label=get_text_local(
                        "module_width_m_label",
                        "Breite (m)"),
                    min_value=0.0,
                    value=_safe_float(
                        product_data_for_manual_form.get(
                            'width_m',
                            0.0)),
                    step=0.001,
                    format="%.3f",
                    key=f"{form_key_manual_prod_ui}_width_man")
                p_weight_kg_val = st.number_input(
                    label=get_text_local(
                        "module_weight_kg_label", "Gewicht (kg)"), min_value=0.0, value=_safe_float(
                        product_data_for_manual_form.get(
                            'weight_kg', 0.0)), step=0.1, key=f"{form_key_manual_prod_ui}_weight_man")
            elif p_category_form == 'Wechselrichter':
                p_power_kw_val = st.number_input(
                    label=get_text_local(
                        "inverter_power_kw_label",
                        "Nennleistung AC (kW)"),
                    min_value=0.0,
                    value=_safe_float(
                        product_data_for_manual_form.get(
                            'power_kw',
                            0.0)),
                    step=0.1,
                    key=f"{form_key_manual_prod_ui}_power_kw_inv_man")
                p_efficiency_percent_val = st.number_input(
                    label=get_text_local(
                        "inverter_max_efficiency_percent_label",
                        "Max. Wirkungsgrad (%)"),
                    min_value=0.0,
                    max_value=100.0,
                    value=_safe_float(
                        product_data_for_manual_form.get(
                            'efficiency_percent',
                            0.0)),
                    step=0.01,
                    format="%.2f",
                    key=f"{form_key_manual_prod_ui}_eff_inv_man")
            elif p_category_form == 'Batteriespeicher':
                p_storage_power_kw_val = st.number_input(
                    label=get_text_local(
                        "storage_usable_storage_power_kw_label",
                        "Nutzbare Kapazität (kWh)"),
                    min_value=0.0,
                    value=_safe_float(
                        product_data_for_manual_form.get(
                            'storage_power_kw',
                            0.0)),
                    step=0.1,
                    key=f"{form_key_manual_prod_ui}_storage_cap_man")
                p_power_kw_val = st.number_input(
                    label=get_text_local(
                        "storage_max_charge_discharge_storage_power_kw_label",
                        "Max. Lade-/Entladeleistung (kW)"),
                    min_value=0.0,
                    value=_safe_float(
                        product_data_for_manual_form.get(
                            'power_kw',
                            0.0)),
                    step=0.1,
                    key=f"{form_key_manual_prod_ui}_storage_power_man")
                p_max_cycles_val = st.number_input(
                    label=get_text_local(
                        "storage_max_cycles_manufacturer_label",
                        "Zyklen (Herstellerangabe)"),
                    min_value=0,
                    value=_safe_int(
                        product_data_for_manual_form.get(
                            'max_cycles',
                            0)),
                    step=100,
                    key=f"{form_key_manual_prod_ui}_max_cycles_man")

            p_description_form_val = st.text_area(
                get_text_local(
                    "product_description_label",
                    "Beschreibung"),
                value=product_data_for_manual_form.get(
                    'description',
                    ''),
                height=100,
                key=f"{form_key_manual_prod_ui}_desc_man")
            form_manual_submit_label_dyn = get_text_local(
                "admin_save_product_button_manual",
                "Änderungen speichern") if st.session_state.product_to_edit_id_manual else get_text_local(
                "admin_add_product_button_manual",
                "Produkt anlegen")
            submitted_manual_product_form_btn = st.form_submit_button(
                form_manual_submit_label_dyn)

        if submitted_manual_product_form_btn:
            if not (p_model_name_form or "").strip() or not p_category_form:
                st.error(
                    get_text_local(
                        "product_error_model_category_required",
                        "Modellname und Kategorie sind Pflichtfelder."))
            else:
                product_data_to_save_db = {
                    "model_name": (p_model_name_form or "").strip(), "category": p_category_form,
                    "brand": (p_brand_form or "").strip(), "price_euro": p_price_form,
                    "additional_cost_netto": p_add_cost_form, "warranty_years": p_warranty_form,
                    "description": (p_description_form_val or "").strip(),
                    # Start with current, update if new one uploaded
                    "image_base64": current_product_image_b64_form or "",
                    "datasheet_link_db_path": current_datasheet_link  # Start with current
                }
                if p_category_form == 'Modul':
                    product_data_to_save_db.update(
                        {
                            "capacity_w": p_capacity_w_val,
                            "efficiency_percent": p_efficiency_percent_val,
                            "length_m": p_length_m_val,
                            "width_m": p_width_m_val,
                            "weight_kg": p_weight_kg_val})
                elif p_category_form == 'Wechselrichter':
                    product_data_to_save_db.update(
                        {"power_kw": p_power_kw_val, "efficiency_percent": p_efficiency_percent_val})
                elif p_category_form == 'Batteriespeicher':
                    product_data_to_save_db.update(
                        {
                            "storage_power_kw": p_storage_power_kw_val,
                            "power_kw": p_power_kw_val,
                            "max_cycles": p_max_cycles_val})

                if uploaded_product_image_manual_file_form:
                    if uploaded_product_image_manual_file_form.size <= 2 * 1024 * 1024:
                        new_image_b64 = base64.b64encode(
                            uploaded_product_image_manual_file_form.getvalue()).decode('utf-8')
                        product_data_to_save_db["image_base64"] = new_image_b64
                        st.success(
                            f"Bild erfolgreich verarbeitet ({
                                uploaded_product_image_manual_file_form.size} Bytes)")
                    else:
                        st.error(
                            get_text_local(
                                "product_error_image_too_large",
                                "Produktbild zu groß (max. 2MB). Nicht gespeichert."))

                datasheet_content_bytes_to_write, original_datasheet_filename_to_write = None, None
                if uploaded_datasheet_pdf_file_form:
                    if uploaded_datasheet_pdf_file_form.size <= 5 * 1024 * 1024:
                        datasheet_content_bytes_to_write = uploaded_datasheet_pdf_file_form.getvalue()
                        original_datasheet_filename_to_write = uploaded_datasheet_pdf_file_form.name
                        st.success(
                            f"Datenblatt erfolgreich verarbeitet: {
                                uploaded_datasheet_pdf_file_form.name} ({
                                uploaded_datasheet_pdf_file_form.size} Bytes)")
                    else:
                        st.error(
                            get_text_local(
                                "product_error_datasheet_too_large",
                                "Datenblatt-PDF zu groß (max. 5MB). Nicht hochgeladen."))

                if st.session_state.product_to_edit_id_manual:
                    product_id_for_files = st.session_state.product_to_edit_id_manual

                    if datasheet_content_bytes_to_write and original_datasheet_filename_to_write:
                        old_ds_path = product_data_for_manual_form.get(
                            "datasheet_link_db_path")
                        if old_ds_path:
                            full_old_ds_path = os.path.join(
                                PRODUCT_DATASHEETS_BASE_DIR_ADMIN, old_ds_path)
                            if os.path.exists(full_old_ds_path):
                                try:
                                    os.remove(full_old_ds_path)
                                    parent_dir_old_ds = os.path.dirname(
                                        full_old_ds_path)
                                    if os.path.exists(parent_dir_old_ds) and not os.listdir(
                                            parent_dir_old_ds):
                                        os.rmdir(parent_dir_old_ds)
                                except OSError as e_del_old:
                                    st.warning(
                                        f"Altes Datenblatt konnte nicht gelöscht werden: {e_del_old}")
                        prod_specific_dir = os.path.join(
                            PRODUCT_DATASHEETS_BASE_DIR_ADMIN, str(product_id_for_files))
                        os.makedirs(prod_specific_dir, exist_ok=True)
                        safe_filename = "".join(
                            c if c.isalnum() or c in (
                                '.', '-', '_') else '_' for c in original_datasheet_filename_to_write)
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        final_safe_filename_ds = f"{
                            os.path.splitext(safe_filename)[0]}_{timestamp}{
                            os.path.splitext(safe_filename)[1]}"
                        disk_path = os.path.join(
                            prod_specific_dir, final_safe_filename_ds)
                        with open(disk_path, "wb") as f:
                            f.write(datasheet_content_bytes_to_write)
                        product_data_to_save_db["datasheet_link_db_path"] = os.path.join(
                            str(product_id_for_files), final_safe_filename_ds)

                    if update_product_func(
                            product_id_for_files,
                            product_data_to_save_db):
                        st.success(
                            get_text_local(
                                "product_success_updated",
                                "Produkt erfolgreich aktualisiert."))

                        # Zusätzliche Bestätigung für Uploads
                        if uploaded_product_image_manual_file_form:
                            st.info("Produktbild wurde erfolgreich gespeichert.")
                        if datasheet_content_bytes_to_write:
                            st.info("Datenblatt wurde erfolgreich gespeichert.")

                        set_current_page("admin")
                    else:
                        st.error(
                            get_text_local(
                                "product_error_updating",
                                "Fehler beim Aktualisieren des Produkts."))
                else:
                    product_data_for_add = product_data_to_save_db.copy()
                    if "datasheet_link_db_path" in product_data_for_add:
                        del product_data_for_add["datasheet_link_db_path"]

                    new_product_id = add_product_func(product_data_for_add)
                    if new_product_id:
                        st.success(
                            get_text_local(
                                "product_success_added_param",
                                "Produkt '{model_name}' mit ID {id} angelegt.").format(
                                model_name=p_model_name_form.strip(),
                                id=new_product_id))

                        # Zusätzliche Bestätigung für Uploads
                        if uploaded_product_image_manual_file_form:
                            st.info(
                                "🖼️ Produktbild wurde erfolgreich gespeichert.")

                        if datasheet_content_bytes_to_write and original_datasheet_filename_to_write:
                            prod_specific_dir = os.path.join(
                                PRODUCT_DATASHEETS_BASE_DIR_ADMIN, str(new_product_id))
                            os.makedirs(prod_specific_dir, exist_ok=True)
                            safe_filename = "".join(
                                c if c.isalnum() or c in (
                                    '.', '-', '_') else '_' for c in original_datasheet_filename_to_write)
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            final_safe_filename_ds = f"{
                                os.path.splitext(safe_filename)[0]}_{timestamp}{
                                os.path.splitext(safe_filename)[1]}"
                            disk_path = os.path.join(
                                prod_specific_dir, final_safe_filename_ds)
                            with open(disk_path, "wb") as f:
                                f.write(datasheet_content_bytes_to_write)
                            relative_ds_path = os.path.join(
                                str(new_product_id), final_safe_filename_ds)
                            if update_product_func(
                                new_product_id, {
                                    "datasheet_link_db_path": relative_ds_path}):
                                st.info(
                                    get_text_local(
                                        "product_info_datasheet_saved",
                                        "Produktdatenblatt gespeichert..."))
                            else:
                                st.error(
                                    get_text_local(
                                        "product_error_datasheet_path",
                                        "Produkt angelegt, aber Fehler beim Speichern des Datenblatt-Pfads."))
                        st.session_state.product_to_edit_id_manual = new_product_id
                        set_current_page("admin")
                    else:
                        st.error(
                            get_text_local(
                                "product_error_adding",
                                "Fehler beim Anlegen des Produkts. Modellname bereits vorhanden?"))

        # Aufklappbarer Zusatz: Erweiterte Eigenschaften / Attribute für das aktuell ausgewählte Produkt
        # Nur anzeigen, wenn ein bestehendes Produkt bearbeitet wird (ID
        # vorhanden)
        if st.session_state.product_to_edit_id_manual:
            st.markdown("---")
            with st.expander(get_text_local("product_attributes_expander_title", "Erweiterte Eigenschaften / Attribute"), expanded=False):
                if not pa_list_attributes or not pa_upsert_attribute or not pa_delete_attribute:
                    st.warning(
                        get_text_local(
                            "product_attributes_module_missing",
                            "Attribut-Module nicht verfügbar."))
                else:
                    current_pid_attr = int(
                        st.session_state.product_to_edit_id_manual)
                    current_category_attr = product_data_for_manual_form.get(
                        'category') or ''

                    # Liste vorhandener Attribute
                    attrs_list = pa_list_attributes(current_pid_attr) or []
                    if not attrs_list:
                        st.info(
                            get_text_local(
                                "product_attributes_none_info",
                                "Keine Attribute vorhanden. Du kannst unten welche hinzufügen."))
                    else:
                        st.markdown(
                            "**" +
                            get_text_local(
                                "product_attributes_existing_header",
                                "Vorhandene Attribute") +
                            ":**")
                        for a in attrs_list:
                            cols_a = st.columns([2.2, 3.2, 1.2, 0.8, 0.6])
                            cols_a[0].caption(a.get('attribute_key') or "")
                            cols_a[1].text(a.get('attribute_value') or "")
                            cols_a[2].caption(a.get('unit') or "")
                            cols_a[3].caption(str(a.get('display_order') or 0))
                            del_key = f"del_attr_{current_pid_attr}_{
                                a.get('id')}{WIDGET_KEY_SUFFIX}"
                            if cols_a[4].button(
                                "", key=del_key, help=get_text_local(
                                    "product_attributes_delete_help", "Attribut löschen")):
                                try:
                                    if pa_delete_attribute(int(a['id'])):
                                        st.success(
                                            get_text_local(
                                                "product_attributes_deleted_success",
                                                "Attribut gelöscht."))
                                        set_current_page("admin")
                                    else:
                                        st.error(
                                            get_text_local(
                                                "product_attributes_deleted_fail",
                                                "Fehler beim Löschen."))
                                except Exception as e_del:
                                    st.error(
                                        get_text_local(
                                            "product_attributes_deleted_exception",
                                            f"Fehler: {e_del}"))

                    st.markdown("---")
                    st.markdown(
                        "**" +
                        get_text_local(
                            "product_attributes_add_update_header",
                            "Attribut hinzufügen/aktualisieren") +
                        ":**")
                    # Formular für Upsert (gleicher Key => Update)
                    form_key_attr = f"attr_form_{current_pid_attr}{WIDGET_KEY_SUFFIX}"
                    with st.form(key=form_key_attr, clear_on_submit=True):
                        a_key = st.text_input(
                            get_text_local(
                                "product_attributes_key_label",
                                "Key (z. B. cell_technology)"),
                            key=f"{form_key_attr}_key")
                        a_val = st.text_input(
                            get_text_local(
                                "product_attributes_value_label",
                                "Wert"),
                            key=f"{form_key_attr}_value")
                        cols_uo = st.columns([1, 1])
                        a_unit = cols_uo[0].text_input(
                            get_text_local(
                                "product_attributes_unit_label",
                                "Einheit (optional)"),
                            key=f"{form_key_attr}_unit")
                        try:
                            a_order_default = 0
                        except Exception:
                            a_order_default = 0
                        a_order = cols_uo[1].number_input(
                            get_text_local(
                                "product_attributes_order_label",
                                "Reihenfolge"),
                            min_value=0,
                            value=a_order_default,
                            step=1,
                            key=f"{form_key_attr}_order")
                        submit_attr = st.form_submit_button(get_text_local(
                            "product_attributes_upsert_button", "Speichern"))

                    if submit_attr:
                        if not a_key or not a_key.strip():
                            st.error(
                                get_text_local(
                                    "product_attributes_key_required",
                                    "Key ist erforderlich."))
                        else:
                            try:
                                saved_id = pa_upsert_attribute(
                                    current_pid_attr, current_category_attr, a_key.strip(), a_val.strip() if isinstance(
                                        a_val, str) else a_val, a_unit.strip() if isinstance(
                                        a_unit, str) else a_unit, int(a_order))
                                if saved_id:
                                    st.success(
                                        get_text_local(
                                            "product_attributes_upsert_success",
                                            "Attribut gespeichert."))
                                    set_current_page("admin")
                                else:
                                    st.error(
                                        get_text_local(
                                            "product_attributes_upsert_fail",
                                            "Fehler beim Speichern des Attributs."))
                            except Exception as e_up:
                                st.error(
                                    get_text_local(
                                        "product_attributes_upsert_exception",
                                        f"Fehler: {e_up}"))

        if st.session_state.product_to_edit_id_manual and product_data_for_manual_form.get(
                "datasheet_link_db_path"):
            st.markdown(
                "**" +
                get_text_local(
                    "product_existing_datasheet_actions_header",
                    "Vorhandenes Datenblatt Aktionen:") +
                "**")
            if st.button(
                get_text_local(
                    "product_button_delete_current_datasheet",
                    "Aktuelles Datenblatt löschen"),
                key=f"delete_datasheet_prod_btn_man_{
                    st.session_state.product_to_edit_id_manual}{WIDGET_KEY_SUFFIX}_key"):
                datasheet_to_delete_path_val = product_data_for_manual_form.get(
                    "datasheet_link_db_path")
                full_path_to_delete_val = os.path.join(
                    PRODUCT_DATASHEETS_BASE_DIR_ADMIN, datasheet_to_delete_path_val)
                file_deleted_fs_val = False
                if os.path.exists(full_path_to_delete_val):
                    try:
                        os.remove(full_path_to_delete_val)
                        parent_dir_ds_val = os.path.dirname(
                            full_path_to_delete_val)
                        if os.path.exists(parent_dir_ds_val) and not os.listdir(
                                parent_dir_ds_val):
                            os.rmdir(parent_dir_ds_val)
                        file_deleted_fs_val = True
                    except OSError as e_del_ds_f:
                        st.error(
                            f"Fehler beim Löschen der Datenblatt-Datei: {e_del_ds_f}")
                else:
                    st.warning(
                        get_text_local(
                            "product_warning_datasheet_not_found",
                            "Datenblatt-Datei nicht auf dem Server gefunden..."))
                    file_deleted_fs_val = True

                if file_deleted_fs_val:
                    if update_product_func(
                        st.session_state.product_to_edit_id_manual, {
                            "datasheet_link_db_path": None}):
                        st.success(
                            get_text_local(
                                "product_success_datasheet_link_removed",
                                "Datenblatt-Verknüpfung entfernt."))
                        set_current_page("admin")
                    else:
                        st.error(
                            get_text_local(
                                "product_error_removing_datasheet_path",
                                "Fehler beim Entfernen des Datenblatt-Pfads aus der DB."))

        if st.session_state.product_to_edit_id_manual:
            if st.button(
                    get_text_local(
                        "admin_finish_edit_product_button",
                        "Produktbearbeitung abschließen/Neues Produkt"),
                    key=f"finish_edit_prod_btn_manual_man{WIDGET_KEY_SUFFIX}_key_end"):
                st.session_state.product_to_edit_id_manual = None
                set_current_page("admin")

    st.markdown("---")
    st.subheader(
        get_text_local(
            "admin_current_products_header_display",
            "Produkte in Datenbank (gefiltert)"))
    selected_category_filter_disp_list = st.selectbox(
        get_text_local(
            "admin_select_category_label_display",
            "Angezeigte Produktkategorie"),
        options=[
            get_text_local(
                "all_categories",
                "Alle")] +
        product_categories_manual_list,
        key=f"product_cat_select_display_list_man{WIDGET_KEY_SUFFIX}_key_filter")
    filter_cat_disp_list_val = None if selected_category_filter_disp_list == get_text_local(
        "all_categories", "Alle") else selected_category_filter_disp_list
    all_products_list_display_val = list_products_func(
        category=filter_cat_disp_list_val)

    if not all_products_list_display_val:
        st.info(
            get_text_local(
                "product_info_no_products_for_filter",
                "Keine Produkte zum Anzeigen gefunden für die aktuelle Filterauswahl."))
    else:
        list_cols_h = st.columns([0.4, 2, 0.8, 0.8, 1, 0.8, 0.4, 0.4])
        list_headers = [
            "ID",
            "Modell",
            "Bild",
            "Datenblatt?",
            "Kategorie",
            "Preis (€)",
            "",
            ""]
        for c, h in zip(list_cols_h, list_headers, strict=False):
            c.markdown(f"**{h}**")

        for i_list, prod_item_in_list in enumerate(
                all_products_list_display_val):
            prod_id_in_list = prod_item_in_list.get('id')
            key_suffix_in_list = prod_id_in_list if prod_id_in_list is not None else f"idx_prod_list_man_final_key_admin_item_{i_list}{WIDGET_KEY_SUFFIX}"
            list_cols_r = st.columns([0.4, 2, 0.8, 0.8, 1, 0.8, 0.4, 0.4])
            list_cols_r[0].text(
                str(prod_id_in_list) if prod_id_in_list is not None else "N/A")
            list_cols_r[1].text(
                f"{
                    prod_item_in_list.get(
                        'brand',
                        '') or ''} {
                    prod_item_in_list.get(
                        'model_name',
                        '') or ''}".strip())
            prod_img_b64_list_view = prod_item_in_list.get('image_base64')
            if prod_img_b64_list_view:
                try:
                    list_cols_r[2].image(
                        base64.b64decode(prod_img_b64_list_view), width=40)
                except Exception:
                    list_cols_r[2].caption("err")
            else:
                list_cols_r[2].caption("-")
            list_cols_r[3].caption("Ja" if prod_item_in_list.get(
                "datasheet_link_db_path") else "Nein")
            list_cols_r[4].caption(prod_item_in_list.get('category', ''))
            price_euro_val = prod_item_in_list.get('price_euro')
            price_display_val = 0.0
            try:
                price_display_val = float(
                    price_euro_val if price_euro_val is not None else 0.0)
            except (ValueError, TypeError):
                pass
            list_cols_r[5].caption(f"{price_display_val:.2f}")

            if list_cols_r[6].button(
                "",
                key=f"edit_prod_list_btn_man_final_key_admin_item_{key_suffix_in_list}",
                    help="Produkt bearbeiten"):
                if prod_id_in_list is not None:
                    st.session_state.product_to_edit_id_manual = prod_id_in_list
                    set_current_page("admin")

            confirm_del_key_prod_item_list_final = f"confirm_del_prod_item_list_man_final_key_admin_item_{key_suffix_in_list}"
            if list_cols_r[7].button(
                "",
                key=f"delete_prod_list_btn_man_final_key_admin_item_{key_suffix_in_list}",
                    help="Produkt löschen"):
                if prod_id_in_list is not None:
                    if st.session_state.get(
                            confirm_del_key_prod_item_list_final, False):
                        if delete_product_func(prod_id_in_list):
                            st.success(
                                get_text_local(
                                    "product_success_deleted_param",
                                    "Produkt '{model_name}' gelöscht.").format(
                                    model_name=prod_item_in_list.get('model_name')))
                            # KORREKTUR: Explizites Löschen des Session State Keys nach st.rerun() ist oft nicht nötig
                            # if confirm_del_key_prod_item_list_final in st.session_state:
                            #     del st.session_state[confirm_del_key_prod_item_list_final]
                            if st.session_state.product_to_edit_id_manual == prod_id_in_list:
                                st.session_state.product_to_edit_id_manual = None
                            set_current_page("admin")
                        else:
                            st.error(
                                get_text_local(
                                    "product_error_deleting_param",
                                    "Fehler Löschen Produkt '{model_name}'.").format(
                                    model_name=prod_item_in_list.get('model_name')))
                    else:
                        st.session_state[confirm_del_key_prod_item_list_final] = True
                        st.warning(
                            get_text_local(
                                "product_confirm_delete_param",
                                "Sicher Produkt '{model_name}' löschen? Erneut klicken.").format(
                                model_name=prod_item_in_list.get('model_name')))
                        set_current_page("admin")
            st.divider()

# Änderungshistorie
# ... (vorherige Einträge)
# 2025-06-04, Gemini Ultra (Korrektur SyntaxError): Die einzeilige if-Anweisung in `render_product_management` für `product_categories_manual_list` wurde
#                                                    in einen Standard-Block mit Doppelpunkt und Einrückung umgewandelt, um den `SyntaxError: expected ':'` zu beheben.
#                                                    Die Logik zum Löschen von Session-State-Keys für Bestätigungsdialoge (z.B. `confirm_del_key_prod_item_list_final`)
#                                                    wurde beibehalten, aber das explizite `del st.session_state[...]` nach einem `st.rerun()` wurde entfernt,
# da `st.rerun()` den Zustand oft ausreichend zurücksetzt und ein
# verbleibender Key im session_state meist unkritisch ist.

# Fortsetzung von admin_panel.py


def render_general_settings_extended(
        load_admin_setting_func: Callable,
        save_admin_setting_func: Callable):
    st.subheader(
        get_text_local(
            "admin_general_calc_params_basic",
            "Allgemeine Berechnungsparameter"))
    current_global_constants = load_admin_setting_func('global_constants', {})
    temp_merged_constants = _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.copy()
    if isinstance(current_global_constants, dict):
        temp_merged_constants.update(current_global_constants)
    current_global_constants = temp_merged_constants
    with st.form(f"global_constants_form{WIDGET_KEY_SUFFIX}"):
        col_gc1, col_gc2 = st.columns(2)
        with col_gc1:
            new_vat_rate = st.number_input(
                label=get_text_local(
                    "vat_rate_percent", "Standard MwSt. (%)"), value=float(
                    current_global_constants.get(
                        'vat_rate_percent', 0.0)), key=f"gc_vat{WIDGET_KEY_SUFFIX}")
            new_degradation = st.number_input(
                label=get_text_local(
                    "annual_module_degradation_percent",
                    "Leistungsdegradation... (% pro Jahr)"),
                value=float(
                    current_global_constants.get(
                        'annual_module_degradation_percent',
                        0.5)),
                key=f"gc_degradation{WIDGET_KEY_SUFFIX}",
                format="%.2f")
            new_maintenance_fixed = st.number_input(
                label=get_text_local(
                    "maintenance_fixed_eur_pa",
                    "Jährliche Wartungspauschale (€, netto)"),
                value=float(
                    current_global_constants.get(
                        'maintenance_fixed_eur_pa',
                        50.0)),
                key=f"gc_maint_fixed{WIDGET_KEY_SUFFIX}",
                format="%.2f")
        with col_gc2:
            new_inflation = st.number_input(
                label=get_text_local(
                    "inflation_rate_percent",
                    "Inflationsrate... (% p.a.)"),
                value=float(
                    current_global_constants.get(
                        'inflation_rate_percent',
                        2.0)),
                key=f"gc_inflation{WIDGET_KEY_SUFFIX}",
                format="%.2f")
            new_maintenance_increase = st.number_input(
                label=get_text_local(
                    "maintenance_increase_percent_pa",
                    "Jährliche Steigerung Wartungskosten (% p.a.)"),
                value=float(
                    current_global_constants.get(
                        'maintenance_increase_percent_pa',
                        2.0)),
                key=f"gc_maint_increase{WIDGET_KEY_SUFFIX}",
                format="%.2f")
            new_maint_var = st.number_input(
                label=get_text_local(
                    "maintenance_variable_eur_per_kwp_pa",
                    "Variable Wartungskosten (€ pro kWp p.a., netto)"),
                value=float(
                    current_global_constants.get(
                        'maintenance_variable_eur_per_kwp_pa',
                        5.0)),
                key=f"gc_maint_var{WIDGET_KEY_SUFFIX}",
                format="%.2f")
            new_alt_invest_interest = st.number_input(
                label=get_text_local(
                    "alternative_investment_interest_rate_percent",
                    "Vergleichszinssatz Alternativanlage (% p.a.)"),
                value=float(
                    current_global_constants.get(
                        'alternative_investment_interest_rate_percent',
                        3.0)),
                key=f"gc_alt_invest{WIDGET_KEY_SUFFIX}",
                format="%.2f")
        st.markdown("---")
        st.subheader(
            get_text_local(
                "admin_yield_settings_header",
                "Ertragseinstellungen für Photovoltaik-Anlage"))
        col_yield1, col_yield2 = st.columns(2)
        with col_yield1:
            new_global_yield_adj = st.number_input(
                label=get_text_local(
                    "global_yield_adjustment_percent",
                    "Globale Ertragsanpassung (%)"),
                value=float(
                    current_global_constants.get(
                        'global_yield_adjustment_percent',
                        0.0)),
                key=f"gc_yield_adj{WIDGET_KEY_SUFFIX}",
                format="%.2f",
                help="Ein positiver Wert erhöht...")
        with col_yield2:
            new_ref_yield_pr = st.number_input(
                label=get_text_local(
                    "reference_specific_yield_pr",
                    "Referenz-Spezialertrag für PR (kWh/kWp/a)"),
                value=float(
                    current_global_constants.get(
                        'reference_specific_yield_pr',
                        1100.0)),
                key=f"gc_ref_yield_pr{WIDGET_KEY_SUFFIX}",
                format="%.0f",
                help="Wird für die Performance Ratio Berechnung verwendet.")
        st.markdown("---")
        st.subheader(
            get_text_local(
                "admin_orientation_yields_subheader_v2",
                "Spezifische Jahreserträge (kWh/kWp/a)..."))
        st.caption(
            get_text_local(
                "admin_orientation_yields_info_v2",
                "Basis-Ertragswerte..."))
        current_specific_yields_map = current_global_constants.get(
            'specific_yields_by_orientation_tilt', {})
        default_yield_map_template = _DEFAULT_GLOBAL_CONSTANTS_FALLBACK[
            'specific_yields_by_orientation_tilt']
        updated_specific_yields_map = {}
        orientations_ordered = [
            "Süd",
            "Südost",
            "Südwest",
            "Ost",
            "West",
            "Nordost",
            "Nordwest",
            "Nord",
            "Flachdach",
            "Sonstige"]
        tilts_ordered = ["0", "15", "30", "45", "60"]
        header_cols = st.columns([2] + [1] * len(tilts_ordered))
        header_cols[0].markdown("**Ausrichtung**")
        for i, tilt_val_str in enumerate(tilts_ordered):
            header_cols[i + 1].markdown(f"**{tilt_val_str}°**")
        for ori in orientations_ordered:
            row_cols = st.columns([2] + [1] * len(tilts_ordered))
            row_cols[0].markdown(f"*{ori}*")
            updated_specific_yields_map[ori] = {}
            for i_tilt, tilt_val_str_loop in enumerate(tilts_ordered):
                current_val_for_field = 900.0
                if isinstance(
                        current_specific_yields_map.get(ori),
                        dict) and tilt_val_str_loop in current_specific_yields_map[ori]:
                    current_val_for_field = float(
                        current_specific_yields_map[ori][tilt_val_str_loop])
                elif isinstance(default_yield_map_template.get(ori), dict) and tilt_val_str_loop in default_yield_map_template[ori]:
                    current_val_for_field = float(
                        default_yield_map_template[ori][tilt_val_str_loop])
                updated_specific_yields_map[ori][tilt_val_str_loop] = row_cols[
                    i_tilt + 1].number_input(
                    label=f"{ori}-{tilt_val_str_loop}",
                    value=current_val_for_field,
                    min_value=0.0,
                    max_value=2000.0,
                    step=10.0,
                    format="%.0f",
                    key=f"gc_yield_{ori}_{tilt_val_str_loop}{WIDGET_KEY_SUFFIX}",
                    label_visibility="collapsed")
        current_global_constants['specific_yields_by_orientation_tilt'] = updated_specific_yields_map
        st.markdown("---")
        st.subheader(
            get_text_local(
                "admin_multiyear_settings_header",
                "Parameter für Mehrjahressimulation"))
        col_my1, col_my2 = st.columns(2)
        with col_my1:
            new_sim_period = col_my1.number_input(
                label=get_text_local(
                    "simulation_period_years",
                    "Simulationsdauer (Jahre)"),
                value=int(
                    current_global_constants.get(
                        'simulation_period_years',
                        20)),
                min_value=1,
                max_value=50,
                step=1,
                key=f"gc_sim_period{WIDGET_KEY_SUFFIX}")
        with col_my2:
            new_elec_price_increase = col_my2.number_input(
                label=get_text_local(
                    "electricity_price_increase_annual_percent",
                    "Strompreissteigerung (% p.a.)"),
                value=float(
                    current_global_constants.get(
                        'electricity_price_increase_annual_percent',
                        3.0)),
                min_value=0.0,
                max_value=20.0,
                step=0.1,
                format="%.2f",
                key=f"gc_elec_increase{WIDGET_KEY_SUFFIX}")
        if st.form_submit_button(
            get_text_local(
                "admin_save_economic_yield_settings_button",
                "Alle Wirtschafts- und Ertragsparameter speichern")):
            current_global_constants['vat_rate_percent'] = new_vat_rate
            current_global_constants['annual_module_degradation_percent'] = new_degradation
            current_global_constants['maintenance_fixed_eur_pa'] = new_maintenance_fixed
            current_global_constants['inflation_rate_percent'] = new_inflation
            current_global_constants['maintenance_increase_percent_pa'] = new_maintenance_increase
            current_global_constants['maintenance_variable_eur_per_kwp_pa'] = new_maint_var
            current_global_constants['alternative_investment_interest_rate_percent'] = new_alt_invest_interest
            current_global_constants['global_yield_adjustment_percent'] = new_global_yield_adj
            current_global_constants['reference_specific_yield_pr'] = new_ref_yield_pr
            current_global_constants['simulation_period_years'] = new_sim_period
            current_global_constants['electricity_price_increase_annual_percent'] = new_elec_price_increase
            for key_gc, default_val_gc in _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.items():
                if key_gc not in current_global_constants:
                    current_global_constants[key_gc] = default_val_gc
                elif isinstance(default_val_gc, dict) and isinstance(current_global_constants.get(key_gc), dict):
                    for sub_key_gc, sub_default_val_gc in default_val_gc.items():
                        if sub_key_gc not in current_global_constants[key_gc]:
                            current_global_constants[key_gc][sub_key_gc] = sub_default_val_gc
            if save_admin_setting_func(
                'global_constants',
                    current_global_constants):
                st.success(
                    get_text_local(
                        "admin_economic_yield_settings_save_success",
                        "Einstellungen erfolgreich gespeichert."))
                set_current_page("admin")
            else:
                st.error(
                    get_text_local(
                        "admin_economic_yield_settings_save_error",
                        "Fehler beim Speichern der Einstellungen."))

    # Abschnitt: Cheat-Amortisationszeit
    st.markdown("---")
    st.subheader("Cheat-Amortisationszeit")
    st.caption(
        "Optional: Überschreibe die berechnete Amortisationszeit für Präsentationszwecke.")
    cheat_current = load_admin_setting_func(
        'amortization_cheat_settings', {
            "enabled": False, "mode": "fixed", "value_years": None, "percent": None})
    if not isinstance(cheat_current, dict):
        cheat_current = {
            "enabled": False,
            "mode": "fixed",
            "value_years": None,
            "percent": None}
    with st.form(f"amort_cheat_form{WIDGET_KEY_SUFFIX}"):
        enabled = st.checkbox(
            "Cheat aktivieren",
            value=bool(
                cheat_current.get(
                    "enabled",
                    False)),
            key=f"cheat_enabled{WIDGET_KEY_SUFFIX}")
        mode = st.selectbox(
            "Modus",
            options=[
                "fixed",
                "absolute_reduction",
                "percentage_reduction"],
            index=[
                "fixed",
                "absolute_reduction",
                "percentage_reduction"].index(
                cheat_current.get(
                    "mode",
                    "fixed")),
            help="fixed: feste Jahre setzen; absolute_reduction: feste Jahre abziehen; percentage_reduction: prozentuale Reduktion")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            value_years = st.number_input(
                "Feste Jahre / Abzug (Jahre)",
                value=float(
                    cheat_current.get("value_years") or 0.0),
                min_value=0.0,
                step=0.1,
                format="%.2f")
        with col_c2:
            percent = st.number_input(
                "Prozentuale Reduktion (%)",
                value=float(
                    cheat_current.get("percent") or 0.0),
                min_value=0.0,
                max_value=95.0,
                step=1.0,
                format="%.0f")
        if st.form_submit_button("Cheat-Einstellung speichern"):
            to_save = {
                "enabled": enabled,
                "mode": mode,
                "value_years": value_years,
                "percent": percent}
            if save_admin_setting_func('amortization_cheat_settings', to_save):
                st.success("Cheat-Amortisationszeit gespeichert.")
                set_current_page("admin")
            else:
                st.error("Fehler beim Speichern der Cheat-Einstellung.")


def render_tariff_management(
        load_admin_setting_func: Callable,
        save_admin_setting_func: Callable):
    st.subheader(
        get_text_local(
            "admin_tariff_management_header",
            "Einspeisevergütungen"))
    st.info(
        get_text_local(
            "admin_tariff_management_info",
            "Verwalten Sie hier die Einspeisevergütungen..."))
    current_feed_in_tariffs_block = load_admin_setting_func(
        'feed_in_tariffs', _DEFAULT_FEED_IN_TARIFFS_FALLBACK.copy())
    if not isinstance(current_feed_in_tariffs_block, dict):
        current_feed_in_tariffs_block = _DEFAULT_FEED_IN_TARIFFS_FALLBACK.copy()
    if 'parts' not in current_feed_in_tariffs_block or not isinstance(
            current_feed_in_tariffs_block['parts'], list):
        current_feed_in_tariffs_block['parts'] = _DEFAULT_FEED_IN_TARIFFS_FALLBACK['parts'][:]
    if 'full' not in current_feed_in_tariffs_block or not isinstance(
            current_feed_in_tariffs_block['full'], list):
        current_feed_in_tariffs_block['full'] = _DEFAULT_FEED_IN_TARIFFS_FALLBACK['full'][:]
    form_key_parts = f"tariff_form_parts{WIDGET_KEY_SUFFIX}"
    st.markdown(
        f"#### {
            get_text_local(
                'admin_partial_feed_in_header',
                'Teileinspeisung')}")
    with st.form(key=form_key_parts):
        rendered_tariffs_parts_ui, final_valid_parts_form_check = manage_tariff_list_ui(
            current_feed_in_tariffs_block['parts'], f"parts_cat{WIDGET_KEY_SUFFIX}")
        submitted_parts = st.form_submit_button(
            get_text_local(
                "admin_save_tariffs_button_parts",
                "Tarife für Teileinspeisung speichern"))
        if submitted_parts:
            final_processed_tariffs_parts = rendered_tariffs_parts_ui
            final_valid_parts_form = True
            for item_tariff in final_processed_tariffs_parts:
                if item_tariff.get(
                        "kwp_min",
                        0.0) >= item_tariff.get(
                        "kwp_max",
                        0.0):
                    final_valid_parts_form = False
                    break
            if final_valid_parts_form:
                current_feed_in_tariffs_block['parts'] = final_processed_tariffs_parts
                if save_admin_setting_func(
                    'feed_in_tariffs',
                        current_feed_in_tariffs_block):
                    st.success(
                        get_text_local(
                            "admin_tariffs_saved_success_parts",
                            "Teileinspeisungstarife gespeichert."))
                    set_current_page("admin")
                else:
                    st.error(
                        get_text_local(
                            "admin_tariffs_save_error",
                            "Fehler beim Speichern der Tarife."))
            else:
                st.error("Einige Tarifstufen für Teileinspeisung sind ungültig...")
    st.markdown("---")
    form_key_full = f"tariff_form_full{WIDGET_KEY_SUFFIX}"
    st.markdown(
        f"#### {
            get_text_local(
                'admin_full_feed_in_header',
                'Volleinspeisung')}")
    with st.form(key=form_key_full):
        rendered_tariffs_full_ui, final_valid_full_form_check = manage_tariff_list_ui(
            current_feed_in_tariffs_block['full'], f"full_cat{WIDGET_KEY_SUFFIX}")
        submitted_full = st.form_submit_button(
            get_text_local(
                "admin_save_tariffs_button_full",
                "Tarife für Volleinspeisung speichern"))
        if submitted_full:
            final_processed_tariffs_full = rendered_tariffs_full_ui
            final_valid_full_form = True
            for item_tariff_f in final_processed_tariffs_full:
                if item_tariff_f.get(
                        "kwp_min",
                        0.0) >= item_tariff_f.get(
                        "kwp_max",
                        0.0):
                    final_valid_full_form = False
                    break
            if final_valid_full_form:
                current_feed_in_tariffs_block['full'] = final_processed_tariffs_full
                if save_admin_setting_func(
                    'feed_in_tariffs',
                        current_feed_in_tariffs_block):
                    st.success(
                        get_text_local(
                            "admin_tariffs_saved_success_full",
                            "Volleinspeisungstarife gespeichert."))
                    set_current_page("admin")
                else:
                    st.error(
                        get_text_local(
                            "admin_tariffs_save_error",
                            "Fehler beim Speichern der Tarife."))
            else:
                st.error("Einige Tarifstufen für Volleinspeisung sind ungültig...")
    st.markdown("---")


def render_visualization_settings(
        load_admin_setting_func: Callable,
        save_admin_setting_func: Callable):
    """
    Konsolidierte Anzeigeeinstellungen: Themes, UI-Effekte und Visualisierung
    """
    st.title(" Anzeige & Design-Einstellungen")
    st.caption(
        "Zentrale Verwaltung für Themes, UI-Effekte und Diagramm-Visualisierungen")

    # Tabs für die drei Bereiche
    tab_theme, tab_effects, tab_charts = st.tabs([
        " App-Theme & Farben",
        " UI-Effekte & Interaktionen",
        " Diagramm-Visualisierung"
    ])

    # ========== TAB 1: THEME & FARBEN ==========
    with tab_theme:
        st.subheader("App-Theme & Farbschema")
        st.info("Wählen Sie das globale Theme und passen Sie Akzentfarben an.")

        try:
            import json

            import theme_manager

            themes = theme_manager.load_available_themes()

            # Lade gespeicherte Overrides
            overrides_json = load_admin_setting_func(
                'app_theme_overrides', '{}')
            if isinstance(overrides_json, str):
                try:
                    overrides = json.loads(overrides_json)
                except BaseException:
                    overrides = {}
            else:
                overrides = overrides_json if isinstance(
                    overrides_json, dict) else {}

            if not themes:
                st.warning(
                    "⚠️ Keine Themes gefunden. Bitte Theme-Ordner prüfen.")
            else:
                # Theme-Auswahl
                theme_entries = [
                    (f"{definition.title} ({key})" if definition.title else key, key, definition)
                    for key, definition in themes.items()
                ]
                labels = [entry[0] for entry in theme_entries]

                # Aktuelles Theme
                active_key = load_admin_setting_func(
                    'app_theme_key', next(iter(themes.keys())))
                active_index = next((idx for idx, (_, key, _) in enumerate(
                    theme_entries) if key == active_key), 0, )

                selected_title = st.selectbox(
                    "Theme auswählen",
                    options=labels,
                    index=active_index,
                    help="Ändert Farben und Typografie der gesamten Anwendung",
                    key=f"admin_theme_selector{WIDGET_KEY_SUFFIX}",
                )
                selected_key = next(
                    key for label, key, _ in theme_entries if label == selected_title)

                theme_description = themes[selected_key].description
                if theme_description:
                    st.caption(theme_description)

                # Theme speichern wenn geändert
                if selected_key != active_key:
                    if save_admin_setting_func('app_theme_key', selected_key):
                        st.session_state.active_theme_key = selected_key
                        st.session_state["_active_theme_payload"] = theme_manager.get_theme_payload_json(
                            selected_key)
                        theme_manager.clear_theme_cache()
                        theme_manager.set_theme_overrides(overrides)
                        st.success(
                            f"✅ Theme '{
                                themes[selected_key].title}' aktiviert.")
                        st.rerun()

                # Akzentfarben-Anpassung
                st.markdown("---")
                st.markdown("**Akzentfarben anpassen**")
                st.caption(
                    "Passe die Hauptfarben des Themes an. Änderungen werden global übernommen.")

                theme_def = themes[selected_key]
                base_config = dict(
                    theme_def.config) if theme_def.config else {}
                sidebar_config = dict(
                    theme_def.sidebar_config) if theme_def.sidebar_config else {}
                override_for_theme = overrides.get(selected_key, {})

                def _normalize_hex(value, fallback):
                    if isinstance(value, str):
                        candidate = value.strip()
                        if candidate.startswith("#"):
                            if len(candidate) == 7:
                                return candidate
                            if len(candidate) == 4:
                                return "#" + \
                                    "".join(ch * 2 for ch in candidate[1:])
                    return fallback

                accent_fields = [
                    ("primaryColor", "Primärfarbe", "#2563eb"),
                    ("linkColor", "Linkfarbe", "#38bdf8"),
                    ("backgroundColor", "Hintergrund", "#0f172a"),
                    ("secondaryBackgroundColor", "Sekundärhintergrund", "#111827"),
                    ("textColor", "Textfarbe", "#f8fafc"),
                    ("borderColor", "Rahmenfarbe", "#1f2937"),
                ]

                cols = st.columns(2)
                updated_colors = {}
                default_colors = {}

                for idx, (field_key, label, fallback) in enumerate(
                        accent_fields):
                    base_value = base_config.get(field_key)
                    base_hex = _normalize_hex(base_value, fallback)
                    default_colors[field_key] = base_hex

                    override_value = override_for_theme.get(field_key)
                    current_value = _normalize_hex(override_value, base_hex)

                    picker = cols[idx % 2].color_picker(
                        label,
                        value=current_value,
                        key=f"admin_theme_color_{field_key}{WIDGET_KEY_SUFFIX}",
                    )
                    updated_colors[field_key] = picker

                action_cols = st.columns([1, 1, 1])
                with action_cols[0]:
                    if st.button(
                        "💾 Akzente speichern",
                        key=f"save_theme_accents{WIDGET_KEY_SUFFIX}",
                            type="primary"):
                        filtered_overrides = {
                            key: value
                            for key, value in updated_colors.items()
                            if value and value != default_colors.get(key)
                        }
                        if filtered_overrides:
                            overrides[selected_key] = filtered_overrides
                        elif selected_key in overrides:
                            overrides.pop(selected_key)

                        if save_admin_setting_func(
                                'app_theme_overrides', json.dumps(overrides)):
                            theme_manager.set_theme_overrides(overrides)
                            theme_manager.clear_theme_cache()
                            st.success("✅ Theme-Akzente gespeichert.")
                            st.rerun()

                with action_cols[1]:
                    if st.button(
                        "🔄 Akzente zurücksetzen",
                            key=f"reset_theme_accents{WIDGET_KEY_SUFFIX}"):
                        if selected_key in overrides:
                            overrides.pop(selected_key)
                            if save_admin_setting_func(
                                    'app_theme_overrides', json.dumps(overrides)):
                                theme_manager.set_theme_overrides(overrides)
                                theme_manager.clear_theme_cache()
                                st.success(
                                    "✅ Akzente auf Standard zurückgesetzt.")
                                st.rerun()

        except ImportError as e:
            st.error(f"Theme-Manager konnte nicht geladen werden: {e}")

    # ========== TAB 2: UI-EFFEKTE ==========
    with tab_effects:
        st.subheader(" Globale UI-Effekte")
        st.info(
            "Wählen Sie einen Effekt-Stil für Buttons, Slider, Dropdowns und Expander.")

        try:
            from pathlib import Path

            from ui_effects_library import (
                get_default_effect,
                get_effect_info,
                get_effect_names,
            )

            # Lade UI-Effekte-Einstellungen
            settings_file = Path("data/ui_effects_settings.json")
            default_settings = {
                "active_effect": get_default_effect(),
                "enabled": True}

            if settings_file.exists():
                try:
                    with open(settings_file, encoding='utf-8') as f:
                        current_settings = json.load(f)
                        if current_settings.get(
                                "active_effect") not in get_effect_names():
                            current_settings["active_effect"] = get_default_effect(
                            )
                except BaseException:
                    current_settings = default_settings
            else:
                current_settings = default_settings

            current_effect = current_settings.get(
                "active_effect", get_default_effect())
            is_enabled = current_settings.get("enabled", True)

            # Effekte aktivieren/deaktivieren
            enabled = st.checkbox(
                "UI-Effekte aktivieren",
                value=is_enabled,
                help="Aktiviert oder deaktiviert alle UI-Effekte global",
                key=f"ui_effects_enabled{WIDGET_KEY_SUFFIX}"
            )

            if not enabled:
                st.warning("⚠️ UI-Effekte sind derzeit deaktiviert.")

            st.markdown("---")

            # Effekt-Auswahl
            effect_options = []
            for effect_key in get_effect_names():
                effect_info = get_effect_info(effect_key)
                effect_name = effect_info.get("name", effect_key)
                effect_options.append((effect_key, effect_name))

            current_index = next((idx for idx, (key, _) in enumerate(
                effect_options) if key == current_effect), 0)

            selected_effect_tuple = st.selectbox(
                "Wählen Sie einen Effekt-Stil",
                options=effect_options,
                index=current_index,
                format_func=lambda x: x[1],
                help="Der ausgewählte Effekt wird auf alle UI-Elemente angewendet",
                key=f"ui_effects_selector{WIDGET_KEY_SUFFIX}")

            selected_effect_key = selected_effect_tuple[0]

            # Effekt-Vorschau
            effect_info = get_effect_info(selected_effect_key)
            st.markdown(f"**{effect_info.get('name', selected_effect_key)}**")
            st.caption(
                effect_info.get(
                    'description',
                    'Keine Beschreibung verfügbar'))

            # Speichern-Button
            if st.button("💾 UI-Effekte speichern", type="primary",
                         key=f"save_ui_effects{WIDGET_KEY_SUFFIX}"):
                new_settings = {
                    "active_effect": selected_effect_key,
                    "enabled": enabled
                }
                settings_file.parent.mkdir(exist_ok=True, parents=True)
                try:
                    with open(settings_file, 'w', encoding='utf-8') as f:
                        json.dump(
                            new_settings, f, indent=2, ensure_ascii=False)
                    st.success(
                        f"✅ UI-Effekt '{effect_info.get('name')}' gespeichert!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")

        except ImportError as e:
            st.error(f"UI-Effekte-Bibliothek konnte nicht geladen werden: {e}")

    # ========== TAB 3: DIAGRAMM-VISUALISIERUNG ==========
    with tab_charts:
        st.subheader(" Diagramm-Visualisierungs-Einstellungen")
        st.info("Passen Sie Standardfarben und Schriftarten für alle Diagramme an.")

        current_global_constants = load_admin_setting_func(
            'global_constants', _DEFAULT_GLOBAL_CONSTANTS_FALLBACK)
        if not isinstance(current_global_constants.get(
                'visualization_settings'), dict):
            current_global_constants['visualization_settings'] = _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.get(
                'visualization_settings', {}).copy()

        viz_settings = current_global_constants['visualization_settings']
        default_viz_settings_fallback = _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.get(
            'visualization_settings', {})
        plotly_palettes = [
            "Plotly",
            "D3",
            "G10",
            "T10",
            "Alphabet",
            "Dark24",
            "Light24",
            "Set1",
            "Set2",
            "Set3",
            "Pastel",
            "Pastel1",
            "Pastel2",
            "Antique",
            "Bold",
            "Safe",
            "Vivid"]

        with st.form(f"visualization_settings_form{WIDGET_KEY_SUFFIX}"):
            st.markdown("**Allgemeine Diagrammfarben**")
            selected_palette_val = viz_settings.get(
                "default_color_palette",
                default_viz_settings_fallback.get("default_color_palette"))
            selected_palette = st.selectbox(
                "Standard-Farbpalette",
                options=plotly_palettes,
                index=plotly_palettes.index(selected_palette_val) if selected_palette_val in plotly_palettes else 0,
                key=f"viz_default_palette_select{WIDGET_KEY_SUFFIX}")

            col1, col2 = st.columns(2)
            with col1:
                primary_color = st.color_picker(
                    "Primäre Diagrammfarbe",
                    value=viz_settings.get(
                        "primary_chart_color",
                        default_viz_settings_fallback.get("primary_chart_color")),
                    key=f"viz_primary_color_picker{WIDGET_KEY_SUFFIX}")
            with col2:
                secondary_color = st.color_picker(
                    "Sekundäre Diagrammfarbe",
                    value=viz_settings.get(
                        "secondary_chart_color",
                        default_viz_settings_fallback.get("secondary_chart_color")),
                    key=f"viz_secondary_color_picker{WIDGET_KEY_SUFFIX}")

            st.markdown("---")
            st.markdown("**Schriftart-Einstellungen**")
            font_family = st.text_input(
                "Schriftfamilie",
                value=viz_settings.get(
                    "chart_font_family",
                    default_viz_settings_fallback.get("chart_font_family")),
                key=f"viz_font_family_input{WIDGET_KEY_SUFFIX}")

            c1f, c2f, c3f = st.columns(3)
            font_size_title = c1f.number_input(
                "Schriftgröße Titel",
                min_value=8,
                max_value=30,
                value=int(
                    viz_settings.get(
                        "chart_font_size_title",
                        default_viz_settings_fallback.get("chart_font_size_title"))),
                key=f"viz_font_size_title_num{WIDGET_KEY_SUFFIX}")
            font_size_axis = c2f.number_input(
                "Schriftgröße Achsenbeschriftung",
                min_value=6,
                max_value=24,
                value=int(
                    viz_settings.get(
                        "chart_font_size_axis_label",
                        default_viz_settings_fallback.get("chart_font_size_axis_label"))),
                key=f"viz_font_size_axis_num{WIDGET_KEY_SUFFIX}")
            font_size_tick = c3f.number_input(
                "Schriftgröße Achsenticks",
                min_value=5,
                max_value=20,
                value=int(
                    viz_settings.get(
                        "chart_font_size_tick_label",
                        default_viz_settings_fallback.get("chart_font_size_tick_label"))),
                key=f"viz_font_size_tick_num{WIDGET_KEY_SUFFIX}")

            submitted_viz_settings = st.form_submit_button(
                "💾 Visualisierungs-Einstellungen speichern")

        if submitted_viz_settings:
            new_viz_settings = {
                "default_color_palette": selected_palette,
                "primary_chart_color": primary_color,
                "secondary_chart_color": secondary_color,
                "chart_font_family": font_family,
                "chart_font_size_title": font_size_title,
                "chart_font_size_axis_label": font_size_axis,
                "chart_font_size_tick_label": font_size_tick,
                **{k: v for k, v in viz_settings.items() if isinstance(v, dict)}
            }
            current_global_constants['visualization_settings'] = new_viz_settings
            if save_admin_setting_func(
                'global_constants',
                    current_global_constants):
                st.success("✅ Visualisierungs-Einstellungen gespeichert.")
                st.rerun()
            else:
                st.error(
                    "Fehler beim Speichern der Visualisierungs-Einstellungen.")


def render_advanced_settings(
        load_admin_setting_func: Callable,
        save_admin_setting_func: Callable):
    st.subheader(
        get_text_local(
            "admin_advanced_header",
            "Erweiterte Einstellungen"))
    render_api_key_settings(load_admin_setting_func, save_admin_setting_func)
    st.markdown("---")
    st.subheader(
        get_text_local(
            "admin_localization_settings_header",
            "Lokalisierung"))
    st.info(
        get_text_local(
            "admin_localization_info",
            "Bearbeiten Sie hier die Texte der Anwendung (JSON-Format)..."))
    current_locale_data = load_admin_setting_func('de_locale_data', {})
    locale_json_string = "{}"
    if not isinstance(current_locale_data, dict):
        current_locale_data = {}
    try:
        locale_json_string = json.dumps(
            current_locale_data, indent=2, ensure_ascii=False)
    except Exception as e_json_dump:
        st.error(f"Fehler Konvertierung JSON: {e_json_dump}")
    edited_locale_json_string = st.text_area(
        get_text_local(
            "admin_locale_json_editor_label",
            "Texte (JSON-Editor)"),
        value=locale_json_string,
        height=300,
        key=f"locale_json_editor_final{WIDGET_KEY_SUFFIX}")
    if st.button(
            get_text_local(
                "admin_save_locale_button",
                "Lokalisierungstexte speichern"),
            key=f"save_locale_btn_final{WIDGET_KEY_SUFFIX}"):
        try:
            parsed_locale_data = json.loads(edited_locale_json_string)
            if not isinstance(parsed_locale_data, dict):
                st.error(
                    "Eingegebene Lokalisierungsdaten kein gültiges JSON-Objekt.")
            elif save_admin_setting_func('de_locale_data', parsed_locale_data):
                st.success(
                    "Lokalisierungstexte gespeichert. Bitte App neu starten.")
            else:
                st.error("Fehler beim Speichern der Lokalisierungstexte.")
        except json.JSONDecodeError as e_json_decode:
            st.error(f"Ungültiges JSON: {e_json_decode}")
        except Exception as e_locale_general:
            st.error(f"Fehler Speichern Locale: {e_locale_general}")
    st.markdown("---")
    st.subheader(
        get_text_local(
            "admin_debugging_settings_header",
            "Debugging-Einstellungen"))
    current_debug_mode_for_display = load_admin_setting_func(
        'app_debug_mode_enabled', False)
    if not isinstance(current_debug_mode_for_display, bool):
        current_debug_mode_for_display = False
    with st.form(f"debug_settings_form_final{WIDGET_KEY_SUFFIX}"):
        app_debug_mode_new_val = st.checkbox(
            get_text_local(
                "admin_enable_debug_mode_label",
                "App-weiten Debug-Modus aktivieren..."),
            value=current_debug_mode_for_display,
            key=f"app_debug_mode_checkbox_final_key{WIDGET_KEY_SUFFIX}",
            help=get_text_local(
                "admin_enable_debug_mode_help",
                "..."))
        submitted_debug_form_button = st.form_submit_button(get_text_local(
            "admin_save_debug_settings_button", "Debugging-Einstellungen speichern"))
    if submitted_debug_form_button:
        if save_admin_setting_func(
            'app_debug_mode_enabled',
                app_debug_mode_new_val):
            st.success(
                get_text_local(
                    "admin_debug_settings_saved_success",
                    "Debugging-Einstellungen gespeichert."))
            set_current_page("admin")
        else:
            st.error(
                get_text_local(
                    "admin_debug_settings_save_error",
                    "Fehler beim Speichern der Debugging-Einstellungen."))
    st.markdown("---")
    st.subheader(
        get_text_local(
            "admin_reset_data_header",
            "Daten zurücksetzen"))
    if st.checkbox(
            get_text_local(
                "admin_show_reset_options_label",
                "Optionen zum Zurücksetzen anzeigen..."),
            key=f"show_reset_options_final{WIDGET_KEY_SUFFIX}"):
        st.warning(
            get_text_local(
                "admin_reset_warning_text",
                "ACHTUNG: Das Zurücksetzen...nicht rückgängig..."))
        confirm_text_reset = "ALLES ENDGÜLTIG LÖSCHEN"
        user_confirm_text = st.text_input(
            f"Geben Sie exakt '{confirm_text_reset}' ein...",
            key=f"confirm_delete_text_input_final{WIDGET_KEY_SUFFIX}")
        if st.button(
                get_text_local(
                    "admin_reset_app_data_button",
                    " App-Daten jetzt endgültig zurücksetzen"),
                key=f"reset_all_app_data_btn_final{WIDGET_KEY_SUFFIX}",
                type="primary"):
            if user_confirm_text == confirm_text_reset:
                try:
                    _base_dir_for_reset = os.path.dirname(
                        os.path.abspath(__file__))
                    _data_dir_for_reset = os.path.join(
                        _base_dir_for_reset, 'data')
                    _db_path_for_reset = os.path.join(
                        _data_dir_for_reset, 'app_data.db')
                    if os.path.exists(_db_path_for_reset):
                        os.remove(_db_path_for_reset)
                        st.success(
                            f"Alle Anwendungsdaten ({_db_path_for_reset}) wurden gelöscht.")
                        st.info(
                            "Bitte starten Sie die Streamlit-Anwendung vollständig neu...")
                        for k_to_del in list(st.session_state.keys()):
                            if k_to_del not in [
                                    '_admin_panel_texts', 'selected_page_key_sui']:
                                del st.session_state[k_to_del]
                        set_current_page("admin")
                    else:
                        st.warning(
                            f"Keine Datenbankdatei unter '{_db_path_for_reset}' zum Löschen gefunden.")
                except Exception as e_reset_final_exc:
                    st.error(
                        f"Fehler beim Zurücksetzen der Daten: {e_reset_final_exc}")
            else:
                st.error("Falscher Bestätigungstext...")


def render_pdf_design_settings(
        load_admin_setting_func: Callable,
        save_admin_setting_func: Callable):
    """Erweiterte PDF Design Einstellungen mit integrierten Template-Management"""
    st.subheader(
        get_text_local(
            "admin_pdf_design_main_header",
            "PDF Design & Vorlagen"))

    selected_pdf_tab = _render_stateful_selector(
        "admin_pdf_design_subtab",
        [
            ("design", "Design & Branding"),
            ("title_images", "Titelbilder"),
            ("offer_titles", "Angebotstitels"),
            ("cover_letters", "Anschreiben"),
        ],
        label=get_text_local("admin_pdf_design_selector", "Bereich auswählen"),
        widget_suffix=WIDGET_KEY_SUFFIX,
    )
    st.markdown("---")

    if selected_pdf_tab == "design":
        st.subheader(
            get_text_local(
                "admin_pdf_company_branding_expander",
                "Firmen-Branding für PDF-Dokumente"))
        active_company_id = load_admin_setting_func('active_company_id', None)
        company_info_for_pdf = {"name": "Ihre Firma (Platzhalter)", "id": 0}
        company_logo_b64_for_pdf = None
        if _get_company_by_id_safe and callable(
                _get_company_by_id_safe) and active_company_id:
            active_company_data = _get_company_by_id_safe(
                int(active_company_id))
            if active_company_data:
                company_info_for_pdf = active_company_data
                company_logo_b64_for_pdf = active_company_data.get(
                    'logo_base64')
        col_pdf_logo, col_pdf_info = st.columns([1, 2])
        with col_pdf_logo:
            st.markdown(
                "<h6>" +
                get_text_local(
                    "admin_pdf_logo_header_short",
                    "Logo für PDF") +
                "</h6>",
                unsafe_allow_html=True)
            if company_logo_b64_for_pdf:
                try:
                    st.image(
                        base64.b64decode(company_logo_b64_for_pdf),
                        width=150,
                        caption=get_text_local(
                            "admin_pdf_current_logo_caption",
                            "Aktives Logo"))
                except Exception:
                    st.warning(
                        get_text_local(
                            "admin_pdf_logo_display_error",
                            "Fehler Anzeige Logo"))
            else:
                st.caption(
                    get_text_local(
                        "admin_pdf_no_active_logo",
                        "Kein Logo für aktive Firma gesetzt."))
            st.caption(
                get_text_local(
                    "admin_pdf_logo_manage_in_companies",
                    "Logo wird in der 'Firmenverwaltung'... verwendet."))
        with col_pdf_info:
            st.markdown(
                "<h6>" +
                get_text_local(
                    "admin_pdf_company_info_header_short",
                    "Firmeninfo für PDF") +
                "</h6>",
                unsafe_allow_html=True)
            for field_key, label_key_suffix in [("name", "name"), ("street", "address1"), ("zip_code", "address2_zip"), ("city", "address2_city"), (
                    "phone", "phone"), ("email", "email"), ("website", "website"), ("tax_id", "tax_id"), ("commercial_register", "commercial_register")]:
                val_disp = company_info_for_pdf.get(field_key, '')
                if field_key == "zip_code":
                    val_disp = f"{
                        company_info_for_pdf.get(
                            'zip_code', '')} {
                        company_info_for_pdf.get(
                            'city', '')}".strip()
                if field_key == "city" and "zip_code" in [
                    f[0] for f in [
                        ("name",
                         "name"),
                        ("street",
                         "address1"),
                        ("zip_code",
                         "address2_zip"),
                        ("city",
                         "address2_city"),
                        ("phone",
                         "phone"),
                        ("email",
                         "email"),
                        ("website",
                         "website"),
                        ("tax_id",
                         "tax_id"),
                        ("commercial_register",
                         "commercial_register")]]:
                    continue
                st.text_input(
                    get_text_local(
                        f"admin_pdf_company_{label_key_suffix}",
                        field_key.replace(
                            "_",
                            " ").title()),
                    value=val_disp,
                    disabled=True,
                    key=f"pdf_disp_ci_{field_key}{WIDGET_KEY_SUFFIX}")
            st.caption(
                get_text_local(
                    "admin_pdf_company_info_manage_in_companies",
                    "Firmeninformationen werden in 'Firmenverwaltung' gepflegt..."))
        st.markdown("---")
        st.subheader("Seite 7 Darstellung: Dienstleistungen & Produkte")
        try:
            from service_display_config_ui import render_service_display_config
            if 'pdf_design_config' not in st.session_state:
                st.session_state['pdf_design_config'] = {}
            render_service_display_config(
                st.session_state['pdf_design_config'], inline=True)
        except Exception as e_srv_cfg:
            st.warning(f"Service Darstellungs-UI nicht geladen: {e_srv_cfg}")
        st.markdown("---")
        st.subheader(
            get_text_local(
                "admin_pdf_design_colors_header",
                "PDF Design Farben"))
        PDF_DESIGN_SETTINGS_DEFAULT = {
            'primary_color': '#4F81BD',
            'secondary_color': '#C0C0C0'}
        current_design_settings = load_admin_setting_func(
            'pdf_design_settings', PDF_DESIGN_SETTINGS_DEFAULT.copy())
        if not isinstance(current_design_settings, dict):
            current_design_settings = PDF_DESIGN_SETTINGS_DEFAULT.copy()
        with st.form(f"pdf_design_form{WIDGET_KEY_SUFFIX}"):
            primary_color = st.color_picker(
                get_text_local(
                    "admin_pdf_primary_color_label",
                    "PDF Haupt-/Akzentfarbe"),
                value=current_design_settings.get(
                    'primary_color',
                    PDF_DESIGN_SETTINGS_DEFAULT['primary_color']),
                key=f"pdf_primary_color{WIDGET_KEY_SUFFIX}",
            )
            secondary_color = st.color_picker(
                get_text_local(
                    "admin_pdf_secondary_color_label",
                    "PDF Sekundärfarbe"),
                value=current_design_settings.get(
                    'secondary_color',
                    PDF_DESIGN_SETTINGS_DEFAULT['secondary_color']),
                key=f"pdf_secondary_color{WIDGET_KEY_SUFFIX}",
            )
            submitted_pdf_design = st.form_submit_button(
                get_text_local(
                    "admin_save_pdf_design_button",
                    "Design Einstellungen Speichern"))
        if submitted_pdf_design:
            updated_design_settings = {
                'primary_color': primary_color,
                'secondary_color': secondary_color}
            if save_admin_setting_func(
                'pdf_design_settings',
                    updated_design_settings):
                st.success(
                    get_text_local(
                        "admin_pdf_design_settings_saved_success",
                        "PDF Design gespeichert."))
                set_current_page("admin")
            else:
                st.error(
                    get_text_local(
                        "admin_pdf_design_settings_save_error",
                        "Fehler Speichern PDF Design."))

    elif selected_pdf_tab == "title_images":
        manage_templates_local(
            "pdf_title_image",
            "pdf_title_image_templates",
            "admin_template_name_label_image",
            is_image_template=True)

    elif selected_pdf_tab == "offer_titles":
        manage_templates_local(
            "pdf_offer_title",
            "pdf_offer_title_templates",
            "admin_template_name_label_text",
            item_content_label_key="admin_template_content_label_title")

    elif selected_pdf_tab == "cover_letters":
        manage_templates_local(
            "pdf_cover_letter",
            "pdf_cover_letter_templates",
            "admin_template_name_label_text",
            item_content_label_key="admin_template_content_label_cover_letter")


def manage_templates_local(
        template_type_key: str,
        template_list_setting_key: str,
        item_name_label_key: str,
        item_content_label_key: str | None = None,
        is_image_template: bool = False):
    st.subheader(
        get_text_local(
            f"admin_{template_type_key}_header", f"{
                template_type_key.replace(
                    '_', ' ').title()} Vorlagen"))
    templates: list[dict[str, Any]] = _load_admin_setting_safe(
        template_list_setting_key, [])
    if not isinstance(templates, list):
        st.error(
            f"Fehler: Vorlagendaten für '{template_list_setting_key}' nicht im Listenformat.")
        templates = []
    form_key_mt = f"{template_type_key}_form_mt_local_tpl{WIDGET_KEY_SUFFIX}"
    edit_mode_session_key = f"edit_mode_template_{template_type_key}{WIDGET_KEY_SUFFIX}"
    edit_index_session_key = f"edit_index_template_{template_type_key}{WIDGET_KEY_SUFFIX}"
    if edit_mode_session_key not in st.session_state:
        st.session_state[edit_mode_session_key] = False
    if edit_index_session_key not in st.session_state:
        st.session_state[edit_index_session_key] = -1
    options_for_select = [
        get_text_local(
            "admin_template_add_new_option",
            "--- Neue Vorlage erstellen ---")] + [
        f"{
            t.get(
                'name',
                f'Vorlage {
                    i + 1}')} (ID: {i})" for i,
        t in enumerate(templates)]
    current_selection_index = 0
    if st.session_state[edit_mode_session_key] and st.session_state[edit_index_session_key] != -1:
        if 0 <= st.session_state[edit_index_session_key] < len(templates):
            current_selection_index = st.session_state[edit_index_session_key] + 1
        else:
            st.session_state[edit_mode_session_key] = False
            st.session_state[edit_index_session_key] = -1
    selected_template_display_name = st.selectbox(
        get_text_local(
            "admin_select_template_to_edit_or_add_new",
            "Vorlage bearbeiten..."),
        options=options_for_select,
        key=f"select_or_add_template_{template_type_key}{WIDGET_KEY_SUFFIX}_select",
        index=current_selection_index)
    if selected_template_display_name == get_text_local(
        "admin_template_add_new_option",
            "--- Neue Vorlage erstellen ---"):
        if st.session_state[edit_mode_session_key] or st.session_state[edit_index_session_key] != -1:
            st.session_state[edit_mode_session_key] = False
            st.session_state[edit_index_session_key] = -1
            set_current_page("admin")
    else:
        try:
            selected_idx = int(selected_template_display_name.split(
                "(ID: ")[1].replace(")", ""))
            if not st.session_state[edit_mode_session_key] or st.session_state[edit_index_session_key] != selected_idx:
                st.session_state[edit_mode_session_key] = True
                st.session_state[edit_index_session_key] = selected_idx
                set_current_page("admin")
        except (IndexError, ValueError):
            st.error(
                get_text_local(
                    "admin_template_selection_error",
                    "Fehler bei der Auswahl der Vorlage..."))
            if st.session_state[edit_mode_session_key] or st.session_state[edit_index_session_key] != -1:
                st.session_state[edit_mode_session_key] = False
                st.session_state[edit_index_session_key] = -1
                set_current_page("admin")
    current_name_val = ""
    current_content_val = ""
    current_image_data_b64 = None
    if st.session_state[edit_mode_session_key] and st.session_state[edit_index_session_key] != -1:
        if 0 <= st.session_state[edit_index_session_key] < len(templates):
            template_to_edit = templates[st.session_state[edit_index_session_key]]
            current_name_val = template_to_edit.get('name', '')
            if is_image_template:
                current_image_data_b64 = template_to_edit.get('data')
            else:
                current_content_val = template_to_edit.get('content', '')
        else:
            st.warning(
                get_text_local(
                    "admin_template_edit_invalid_index_warning",
                    "Die ausgewählte Vorlage...existiert nicht mehr..."))
            st.session_state[edit_mode_session_key] = False
            st.session_state[edit_index_session_key] = -1
            set_current_page("admin")
    # clear_on_submit hier auf False, um Werte bei Validierungsfehlern zu
    # behalten
    with st.form(form_key_mt, clear_on_submit=False):
        st.markdown(f"**{get_text_local('admin_template_edit_add_header',
                                        'Vorlage erstellen / bearbeiten')}**")
        new_template_name = st.text_input(
            get_text_local(
                item_name_label_key,
                "Vorlagenname"),
            value=current_name_val,
            key=f"{template_type_key}_name_input_mt{WIDGET_KEY_SUFFIX}_form")
        new_template_data_b64_for_save = None
        new_template_content_input = ""
        if is_image_template:
            uploaded_image_file = st.file_uploader(
                get_text_local(
                    "admin_upload_title_image",
                    "Bild hochladen..."),
                type=[
                    "png",
                    "jpg",
                    "jpeg"],
                key=f"{template_type_key}_upload_fu_mt{WIDGET_KEY_SUFFIX}_form")
            if uploaded_image_file:
                new_template_data_b64_for_save = base64.b64encode(
                    uploaded_image_file.getvalue()).decode('utf-8')
                st.image(
                    uploaded_image_file,
                    caption=get_text_local(
                        "admin_image_preview",
                        "Vorschau"),
                    width=200)
            elif current_image_data_b64 and st.session_state[edit_mode_session_key]:
                try:
                    st.image(
                        base64.b64decode(current_image_data_b64),
                        caption=get_text_local(
                            "admin_current_image",
                            "Aktuelles Bild"),
                        width=200)
                    new_template_data_b64_for_save = current_image_data_b64
                except Exception:
                    st.error(
                        get_text_local(
                            "admin_error_displaying_current_image",
                            "Fehler beim Anzeigen..."))
        else:
            new_template_content_input = st.text_area(
                get_text_local(
                    item_content_label_key or "admin_template_content_label",
                    "Inhalt..."),
                value=current_content_val,
                height=200,
                key=f"{template_type_key}_content_ta_mt{WIDGET_KEY_SUFFIX}_form")
        submit_button_text = get_text_local(
            "admin_save_template_button", "Vorlage speichern")
        if st.session_state[edit_mode_session_key] and st.session_state[edit_index_session_key] != -1:
            submit_button_text = get_text_local(
                "admin_update_template_button", "Vorlage aktualisieren")
        submitted = st.form_submit_button(submit_button_text)
        if submitted:
            if not new_template_name.strip():
                st.error(
                    get_text_local(
                        "admin_template_name_required",
                        "Vorlagenname ist erforderlich."))
            else:
                new_template_entry = {"name": new_template_name.strip()}
                valid_to_save = True
                if is_image_template:
                    if new_template_data_b64_for_save:
                        new_template_entry["data"] = new_template_data_b64_for_save
                    elif not st.session_state[edit_mode_session_key]:
                        st.error(
                            get_text_local(
                                "admin_image_required_for_new_template",
                                "Für eine neue Bildvorlage..."))
                        valid_to_save = False
                else:
                    new_template_entry["content"] = new_template_content_input
                if valid_to_save:
                    temp_templates_list = templates[:]
                    if st.session_state[edit_mode_session_key] and st.session_state[edit_index_session_key] != -1:
                        if 0 <= st.session_state[edit_index_session_key] < len(
                                temp_templates_list):
                            temp_templates_list[st.session_state[edit_index_session_key]
                                                ] = new_template_entry
                        else:
                            st.error(
                                get_text_local(
                                    "admin_template_update_error_invalid_index",
                                    "Fehler: Die zu aktualisierende Vorlage..."))
                            valid_to_save = False
                    else:
                        temp_templates_list.append(new_template_entry)
                    if valid_to_save:
                        if _save_admin_setting_safe(
                                template_list_setting_key, temp_templates_list):
                            st.success(
                                get_text_local(
                                    "admin_template_saved_success",
                                    "Vorlage gespeichert."))
                            set_current_page("admin")
                        else:
                            st.error(
                                get_text_local(
                                    "admin_template_save_error",
                                    "Fehler beim Speichern der Vorlage."))
    if st.session_state[edit_mode_session_key] and st.session_state[edit_index_session_key] != -1:
        if 0 <= st.session_state[edit_index_session_key] < len(templates):
            delete_button_key = f"delete_template_{template_type_key}{WIDGET_KEY_SUFFIX}_outer_btn"
            confirm_delete_session_key = f"confirm_delete_tpl_{template_type_key}_{
                st.session_state[edit_index_session_key]}{WIDGET_KEY_SUFFIX}_conf"
            if st.button(
                    get_text_local(
                        "admin_delete_template_button",
                        "Ausgewählte Vorlage löschen"),
                    key=delete_button_key,
                    type="secondary"):
                if st.session_state.get(confirm_delete_session_key, False):
                    temp_templates_list_del = templates[:]
                    try:
                        del temp_templates_list_del[st.session_state[edit_index_session_key]]
                        if _save_admin_setting_safe(
                                template_list_setting_key, temp_templates_list_del):
                            st.success(
                                get_text_local(
                                    "admin_template_deleted_success",
                                    "Vorlage gelöscht."))
                            if confirm_delete_session_key in st.session_state:
                                del st.session_state[confirm_delete_session_key]
                            st.session_state[edit_mode_session_key] = False
                            st.session_state[edit_index_session_key] = -1
                            set_current_page("admin")
                        else:
                            st.error(
                                get_text_local(
                                    "admin_template_delete_error",
                                    "Fehler beim Speichern nach dem Löschen..."))
                    except IndexError:
                        st.error(
                            "Fehler: Vorlage zum Löschen nicht im Index gefunden (IndexError).")
                        if confirm_delete_session_key in st.session_state:
                            del st.session_state[confirm_delete_session_key]
                        st.session_state[edit_mode_session_key] = False
                        st.session_state[edit_index_session_key] = -1
                        set_current_page("admin")
                    except Exception as e:
                        st.error(
                            f"Ein unerwarteter Fehler ist beim Löschen aufgetreten: {e}")
                        if confirm_delete_session_key in st.session_state:
                            del st.session_state[confirm_delete_session_key]
                        st.session_state[edit_mode_session_key] = False
                        st.session_state[edit_index_session_key] = -1
                        set_current_page("admin")
                else:
                    st.warning(
                        get_text_local(
                            "admin_confirm_delete_template",
                            "Sicher? Erneut klicken zum Löschen."))
                    st.session_state[confirm_delete_session_key] = True
                    set_current_page("admin")
    st.markdown("---")


def render_api_key_settings(
        load_admin_setting_func: Callable,
        save_admin_setting_func: Callable):
    st.subheader(get_text_local("admin_api_keys_header", "API-Key Verwaltung"))
    st.info(
        get_text_local(
            "admin_api_keys_info",
            "Verwalten Sie hier Ihre API-Schlüssel für externe Dienste..."))
    api_keys_to_manage = {
        "Maps_api_key": get_text_local(
            "admin_Maps_api_key_label",
            "Google Maps API Key"),
        "bing_maps_api_key": get_text_local(
            "admin_bing_maps_api_key_label",
            "Bing Maps API Key..."),
        "osm_nominatim_email": get_text_local(
            "admin_osm_nominatim_email_label",
            "OpenStreetMap Nominatim E-Mail...")}
    current_api_keys_values_for_display = {key_name: load_admin_setting_func(
        key_name, "LEER_DEFAULT") for key_name in api_keys_to_manage}
    with st.form(f"api_keys_form{WIDGET_KEY_SUFFIX}"):
        new_api_key_inputs = {}
        for key_name, key_label_text in api_keys_to_manage.items():
            current_val_for_placeholder = current_api_keys_values_for_display.get(
                key_name, "")
            display_value_placeholder = "**********" if current_val_for_placeholder and current_val_for_placeholder not in [
                "PLATZHALTER_HIER_IHREN_KEY_EINFUEGEN", "LEER_DEFAULT"] else get_text_local(
                "api_key_not_set_placeholder", "Nicht gesetzt")
            new_api_key_inputs[key_name] = st.text_input(
                key_label_text,
                value="",
                type="password",
                help=f"{
                    get_text_local(
                        'api_key_current_value_notice',
                        'Aktuell...')}: {display_value_placeholder}. {
                    get_text_local(
                        'api_key_input_help',
                        'Geben Sie hier einen neuen Schlüssel ein...')}",
                key=f"api_key_input_{key_name}{WIDGET_KEY_SUFFIX}")
        submitted_api_keys = st.form_submit_button(get_text_local(
            "admin_save_api_keys_button", "API-Schlüssel speichern"))
        if submitted_api_keys:
            something_changed_and_saved = False
            for key_name, new_value_from_input in new_api_key_inputs.items():
                if new_value_from_input and new_value_from_input.strip():
                    value_to_save = new_value_from_input.strip()
                    if save_admin_setting_func(key_name, value_to_save):
                        reloaded_value = load_admin_setting_func(
                            key_name, "FEHLER_BEIM_NEULADEN")
                        if reloaded_value == value_to_save:
                            st.success(
                                f"'{api_keys_to_manage[key_name]}' erfolgreich gespeichert...")
                            something_changed_and_saved = True
                        else:
                            st.error(
                                f"Fehler Verifizierung von '{
                                    api_keys_to_manage[key_name]}'. Gesp.: '{value_to_save}', Gel.: '{reloaded_value}'.")
                    else:
                        st.error(
                            get_text_local(
                                "admin_api_key_save_error",
                                f"Fehler beim Speichern von {
                                    api_keys_to_manage[key_name]}."))
            if something_changed_and_saved:
                st.info("Änderungen verarbeitet...")
                set_current_page("admin")
            elif not any(new_api_key_inputs.values()):
                st.info("Keine neuen API-Schlüssel eingegeben...")
    st.markdown("---")


def manage_tariff_list_ui(tariff_list_input: list[dict[str, Any]],
                          form_element_key_suffix: str) -> tuple[list[dict[str, Any]], bool]:
    collected_tariffs_from_ui = []
    all_entries_valid = True
    actual_tariff_list_for_ui = tariff_list_input[:]
    if not actual_tariff_list_for_ui:
        actual_tariff_list_for_ui = [
            {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 0.0}]
    for i, tariff_entry_db_like in enumerate(actual_tariff_list_for_ui):
        cols_tariff_ui = st.columns([2, 2, 2, 1])
        # Suffix konsistent
        key_base = f"tariff_entry_{form_element_key_suffix}_{i}{WIDGET_KEY_SUFFIX}_ui"
        kwp_min_current_value = st.session_state.get(
            f"{key_base}_min", float(
                tariff_entry_db_like.get(
                    "kwp_min", 0.0)))
        kwp_min_ui_val = cols_tariff_ui[0].number_input(
            label=f"kWp Min #{
                i + 1}",
            min_value=0.0,
            value=kwp_min_current_value,
            step=0.01,
            key=f"{key_base}_min",
            format="%.2f")
        min_value_for_kwp_max = kwp_min_ui_val + \
            0.01 if kwp_min_ui_val is not None else 0.01
        kwp_max_current_value = st.session_state.get(f"{key_base}_max", float(
            tariff_entry_db_like.get("kwp_max", min_value_for_kwp_max + 9.99)))
        corrected_kwp_max_for_display = max(
            kwp_max_current_value, min_value_for_kwp_max)
        kwp_max_ui_val = cols_tariff_ui[1].number_input(
            label=f"kWp Max #{
                i + 1}",
            min_value=min_value_for_kwp_max,
            value=corrected_kwp_max_for_display,
            step=0.01,
            key=f"{key_base}_max",
            format="%.2f")
        ct_per_kwh_current_value = st.session_state.get(
            f"{key_base}_ct", float(
                tariff_entry_db_like.get(
                    "ct_per_kwh", 0.0)))
        ct_per_kwh_ui_val = cols_tariff_ui[2].number_input(
            label=f"ct/kWh #{
                i + 1}",
            min_value=0.0,
            value=ct_per_kwh_current_value,
            step=0.1,
            key=f"{key_base}_ct",
            format="%.2f")
        collected_tariffs_from_ui.append(
            {"kwp_min": kwp_min_ui_val, "kwp_max": kwp_max_ui_val, "ct_per_kwh": ct_per_kwh_ui_val})
        if kwp_min_ui_val is not None and kwp_max_ui_val is not None and kwp_min_ui_val >= kwp_max_ui_val:
            cols_tariff_ui[1].error("Max kWp muss größer Min kWp sein!")
            all_entries_valid = False
    return collected_tariffs_from_ui, all_entries_valid


def render_admin_panel(
    texts: dict[str, str] | tuple,
    get_db_connection_func: Callable[[], Any | None],
    save_admin_setting_func: Callable[[str, Any], bool],
    load_admin_setting_func: Callable[[str, Any], Any],
    list_products_func: Callable[[str | None], list[dict[str, Any]]],
    add_product_func: Callable[[dict[str, Any]], int | None],
    update_product_func: Callable[[int | float, dict[str, Any]], bool],
    delete_product_func: Callable[[int | float], bool],
    get_product_by_id_func: Callable[[int | float], dict[str, Any] | None],
    get_product_by_model_name_func: Callable[[str], dict[str, Any] | None],
    list_product_categories_func: Callable[[], list[str]],
    db_list_companies_func: Callable[[], list[dict[str, Any]]],
    db_add_company_func: Callable[[dict[str, Any]], int | None],
    db_get_company_by_id_func: Callable[[int], dict[str, Any] | None],
    db_update_company_func: Callable[[int, dict[str, Any]], bool],
    db_delete_company_func: Callable[[int], bool],
    db_set_default_company_func: Callable[[int], bool],
    db_add_company_document_func: Callable[[int, str, str, str, bytes], int | None],
    db_list_company_documents_func: Callable[[int, str | None], list[dict[str, Any]]],
    db_delete_company_document_func: Callable[[int], bool],
    **kwargs: Any
):
    global _load_admin_setting_safe, _save_admin_setting_safe
    global _list_products_safe, _add_product_safe, _update_product_safe, _delete_product_safe
    global _get_product_by_id_safe, _get_product_by_model_name_safe, _list_product_categories_safe
    global _list_companies_safe, _add_company_safe, _get_company_by_id_safe, _update_company_safe
    global _delete_company_safe, _set_default_company_safe, _add_company_document_safe
    global _list_company_documents_safe, _delete_company_document_safe

    _load_admin_setting_safe = load_admin_setting_func
    _save_admin_setting_safe = save_admin_setting_func
    _list_products_safe = list_products_func
    _add_product_safe = add_product_func
    _update_product_safe = update_product_func
    _delete_product_safe = delete_product_func
    _get_product_by_id_safe = get_product_by_id_func
    _get_product_by_model_name_safe = get_product_by_model_name_func
    _list_product_categories_safe = list_product_categories_func
    _list_companies_safe = db_list_companies_func
    _add_company_safe = db_add_company_func
    _get_company_by_id_safe = db_get_company_by_id_func
    _update_company_safe = db_update_company_func
    _delete_company_safe = db_delete_company_func
    _set_default_company_safe = db_set_default_company_func
    _add_company_document_safe = db_add_company_document_func
    _list_company_documents_safe = db_list_company_documents_func
    _delete_company_document_safe = db_delete_company_document_func

    actual_texts_dict_for_session: dict[str, str]
    if isinstance(texts, dict):
        actual_texts_dict_for_session = texts
    elif isinstance(texts, tuple):
        # Dieser Fall sollte durch die Korrektur in gui.py nicht mehr
        # auftreten, aber als Sicherheit:
        st.warning("ADMIN_PANEL WARNUNG: Der 'texts'-Parameter wurde als Tupel übergeben. Dies sollte in gui.py korrigiert werden. Versuche Konvertierung.")
        try:
            actual_texts_dict_for_session = dict(texts)
            if not actual_texts_dict_for_session and texts:
                st.warning(
                    "ADMIN_PANEL WARNUNG: Konnte Tupel 'texts' nicht sinnvoll in Dict umwandeln. Verwende leeres Text-Dict.")
                actual_texts_dict_for_session = {}
        except (TypeError, ValueError):
            st.error(
                "ADMIN_PANEL FEHLER: Konnte Tupel 'texts' nicht in Dict umwandeln. Verwende leeres Text-Dict.")
            actual_texts_dict_for_session = {}
    else:
        st.error(
            f"ADMIN_PANEL FEHLER: 'texts'-Parameter ist weder Dict noch Tuple (Typ: {
                type(texts)}). Verwende leeres Text-Dict.")
        actual_texts_dict_for_session = {}
    st.session_state['_admin_panel_texts'] = actual_texts_dict_for_session

    st.header(
        get_text_local(
            "menu_item_admin",
            "Administration & Konfiguration"))

    admin_tab_keys_definition = ADMIN_TAB_KEYS_DEFINITION_GLOBAL
    # Verwende deutsche Beschriftungen aus ADMIN_TAB_LABELS_DE
    admin_tab_labels_definition = [
        ADMIN_TAB_LABELS_DE.get(
            key, key.replace(
                "admin_tab_", "").replace(
                "_", " ").title()) for key in admin_tab_keys_definition]

    if not any(admin_tab_labels_definition) and admin_tab_keys_definition:
        st.warning(
            "Admin-Tab-Beschriftungen konnten nicht geladen werden. Verwende Fallback-Namen.")
        admin_tab_labels_definition = [
            key.replace(
                "admin_tab_",
                "").replace(
                "_",
                " ").title() for key in admin_tab_keys_definition]

    if not admin_tab_labels_definition:
        st.error("FEHLER: Keine Admin-Tabs zum Anzeigen vorhanden. ADMIN_TAB_KEYS_DEFINITION_GLOBAL oder Textdefinitionen prüfen.")
        return

    tab_functions_map = {
        "admin_tab_company_management_new": lambda: render_company_crud_tab(
            db_list_companies_func,
            db_add_company_func,
            db_get_company_by_id_func,
            db_update_company_func,
            db_delete_company_func,
            db_set_default_company_func,
            load_admin_setting_func,
            save_admin_setting_func,
            db_add_company_document_func,
            db_list_company_documents_func,
            db_delete_company_document_func),
        "admin_tab_user_management": lambda: render_user_management_tab(),
        "admin_tab_product_management": lambda: render_product_management(
            list_products_func,
            add_product_func,
            update_product_func,
            delete_product_func,
            get_product_by_id_func,
            list_product_categories_func,
            get_product_by_model_name_func),
        "admin_tab_logo_management": lambda: render_logo_management_tab(),
        "admin_tab_product_database_crud": lambda: render_product_admin_ui(),
        "admin_tab_general_settings": lambda: render_general_settings_extended(
            load_admin_setting_func,
            save_admin_setting_func),
        "admin_tab_intro_settings": lambda: render_intro_settings_tab(),
        "admin_tab_tariff_management": lambda: render_tariff_management(
            load_admin_setting_func,
            save_admin_setting_func),
        "admin_tab_pdf_design": lambda: render_pdf_design_settings(
            load_admin_setting_func,
            save_admin_setting_func),
        "admin_tab_payment_terms": lambda: render_comprehensive_admin_payment_terms_ui_with_variants(
            load_admin_setting_func,
            save_admin_setting_func,
            WIDGET_KEY_SUFFIX),
        "admin_tab_visualization_settings": lambda: render_visualization_settings(
            load_admin_setting_func,
            save_admin_setting_func),
        "admin_tab_advanced": lambda: render_advanced_settings(
            load_admin_setting_func,
            save_admin_setting_func),
        "admin_tab_services_management": lambda: render_services_management_tab(),
    }
    tab_labels_map = {
        key: admin_tab_labels_definition[idx]
        for idx, key in enumerate(admin_tab_keys_definition)
        if idx < len(admin_tab_labels_definition)
    }

    selector_options = [(key, tab_labels_map.get(key, key))
                        for key in admin_tab_keys_definition]

    # Modernes Karten-Menü statt Karussell-Navigation
    selected_tab_key = _render_horizontal_menu_selector(
        "admin_active_tab_key",
        selector_options,
        icons=ADMIN_TAB_ICONS,
        label=None,
        help_text=None,
    )

    selected_tab_label = tab_labels_map.get(selected_tab_key, selected_tab_key)
    st.markdown("---")

    render_func = tab_functions_map.get(selected_tab_key)
    if callable(render_func):
        try:
            render_func()
        except Exception as e_tab_render_loop:
            st.error(
                f"Fehler beim Rendern des Bereichs '{selected_tab_label}': {e_tab_render_loop}")
            st.text(traceback.format_exc())
    else:
        st.warning(
            f"Für den Bereich '{selected_tab_label}' ist keine Render-Funktion hinterlegt.")


# Änderungshistorie
# ... (vorherige Einträge) ...
# 2025-06-03, Gemini Ultra: `render_admin_panel` stellt sicher, dass `st.session_state['_admin_panel_texts']`
#                           immer ein Dictionary ist. Alle Tab-Render-Funktionen wurden angepasst, um
#                           keinen `texts`-Parameter mehr zu erwarten und stattdessen `get_text_local` zu verwenden.
#                           Lambdas in `tab_functions_map` übergeben `texts` nicht mehr.
#                           Widget-Keys auf _v15_final/_v16_admin_definitiv aktualisiert.
#
# 2025-06-04, Gemini Ultra: Variable `WIDGET_KEY_SUFFIX` global am Anfang des Moduls definiert, um NameError zu beheben.
#                           Die Render-Funktionen in `tab_functions_map` wurden so angepasst, dass sie nun den `texts`-Parameter nicht mehr explizit übergeben,
#                           da die jeweiligen Unterfunktionen `get_text_local` verwenden, welches auf `st.session_state['_admin_panel_texts']` zugreift.
#

def render_logo_management_tab():
    """Rendert den Logo-Management-Tab im Admin-Panel"""
    try:
        from admin_logo_management_ui import render_logo_management_ui
        render_logo_management_ui()
    except ImportError as e:
        st.error(f"Logo-Management UI konnte nicht geladen werden: {e}")
        st.info("Stellen Sie sicher, dass admin_logo_management_ui.py verfügbar ist.")
    except Exception as e:
        st.error(f"Fehler beim Rendern der Logo-Management UI: {e}")
        st.text(traceback.format_exc())
#
# === NEUE FUNKTIONEN FÜR FIRMENSPEZIFISCHE ANGEBOTSVORLAGEN ===


def render_company_text_templates_tab(company_id: int):
    """Rendert die Verwaltung für firmenspezifische Textvorlagen"""
    st.markdown("###  Firmenspezifische Textvorlagen")
    st.caption(
        "Erstellen Sie individuelle Textbausteine für Angebote dieser Firma.")

    # Textvorlage hinzufügen
    with st.expander(" Neue Textvorlage erstellen", expanded=False):
        with st.form(f"add_text_template_{company_id}", clear_on_submit=True):
            template_name = st.text_input(
                "Name der Vorlage",
                placeholder="z.B. Willkommenstext, Beratungstext, Abschlusstext")

            template_type = st.selectbox(
                "Vorlagentyp",
                options=[
                    "offer_text",
                    "cover_letter",
                    "title_text",
                    "footer_text",
                    "custom"],
                format_func=lambda x: {
                    "offer_text": "Angebotstext",
                    "cover_letter": "Anschreiben",
                    "title_text": "Titel/Überschrift",
                    "footer_text": "Fußzeile",
                    "custom": "Benutzerdefiniert"}.get(
                    x,
                    x))

            template_content = st.text_area(
                "Inhalt der Textvorlage",
                height=150,
                placeholder="Geben Sie hier den Text ein. Sie können Platzhalter wie {customer_name}, {company_name} verwenden."
            )

            if st.form_submit_button("Textvorlage speichern", type="primary"):
                if not template_name.strip():
                    st.error("Bitte geben Sie einen Namen für die Vorlage ein.")
                elif not template_content.strip():
                    st.error("Bitte geben Sie einen Inhalt für die Vorlage ein.")
                else:
                    try:
                        from database import add_company_text_template
                        template_id = add_company_text_template(
                            company_id=company_id,
                            name=template_name.strip(),
                            content=template_content.strip(),
                            template_type=template_type
                        )
                        if template_id:
                            st.success(
                                f" Textvorlage '{template_name}' erfolgreich erstellt!")
                            st.rerun()
                        else:
                            st.error(" Fehler beim Speichern der Textvorlage.")
                    except ImportError:
                        st.error(" Datenbankfunktionen nicht verfügbar.")

    # Vorhandene Textvorlagen auflisten
    try:
        from database import (
            delete_company_text_template,
            list_company_text_templates,
            update_company_text_template,
        )

        text_templates = list_company_text_templates(company_id)

        if text_templates:
            st.markdown("###  Vorhandene Textvorlagen")

            for template in text_templates:
                with st.expander(f" {template['name']} ({template['template_type']})", expanded=False):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Bearbeitung
                        with st.form(f"edit_text_template_{template['id']}"):
                            new_name = st.text_input(
                                "Name",
                                value=template['name'],
                                key=f"text_name_{template['id']}"
                            )
                            new_content = st.text_area(
                                "Inhalt",
                                value=template['content'] or "",
                                height=100,
                                key=f"text_content_{template['id']}"
                            )

                            col_save, col_del = st.columns(2)

                            with col_save:
                                if st.form_submit_button(" Speichern"):
                                    if update_company_text_template(
                                            template['id'], new_name, new_content):
                                        st.success("Textvorlage aktualisiert!")
                                        st.rerun()
                                    else:
                                        st.error("Fehler beim Aktualisieren.")

                            with col_del:
                                if st.form_submit_button(
                                        " Löschen", type="secondary"):
                                    if delete_company_text_template(
                                            template['id']):
                                        st.success("Textvorlage gelöscht!")
                                        st.rerun()
                                    else:
                                        st.error("Fehler beim Löschen.")

                    with col2:
                        st.markdown("**Vorschau:**")
                        preview_text = (template['content'] or "")[:200]
                        if len(template['content'] or "") > 200:
                            preview_text += "..."
                        st.caption(preview_text)
        else:
            st.info(" Noch keine Textvorlagen für diese Firma erstellt.")

    except ImportError:
        st.error(" Datenbankfunktionen für Textvorlagen nicht verfügbar.")


def render_company_image_templates_tab(company_id: int):
    """Rendert die Verwaltung für firmenspezifische Bildvorlagen"""
    st.markdown("###  Firmenspezifische Bildvorlagen")
    st.caption(
        "Laden Sie individuelle Bilder für Angebote dieser Firma hoch (Logos, Referenzbilder, etc.).")

    # Bildvorlage hinzufügen
    with st.expander(" Neue Bildvorlage hochladen", expanded=False):
        with st.form(f"add_image_template_{company_id}", clear_on_submit=True):
            template_name = st.text_input(
                "Name der Bildvorlage",
                placeholder="z.B. Firmenlogo groß, Referenzbild Projekt A, Titellogo")

            template_type = st.selectbox(
                "Bildtyp",
                options=[
                    "title_image",
                    "logo",
                    "reference",
                    "background",
                    "custom"],
                format_func=lambda x: {
                    "title_image": "Titelbild",
                    "logo": "Logo/Emblem",
                    "reference": "Referenzbild",
                    "background": "Hintergrund",
                    "custom": "Benutzerdefiniert"}.get(
                    x,
                    x))

            uploaded_image = st.file_uploader(
                "Bild auswählen",
                type=["png", "jpg", "jpeg", "svg"],
                help="Unterstützte Formate: PNG, JPG, JPEG, SVG. Empfohlene Größe: 1920x1080 für Titelbilder."
            )

            if uploaded_image:
                st.image(uploaded_image, caption="Vorschau", width=300)

            if st.form_submit_button("Bildvorlage hochladen", type="primary"):
                if not template_name.strip():
                    st.error(
                        "Bitte geben Sie einen Namen für die Bildvorlage ein.")
                elif not uploaded_image:
                    st.error("Bitte wählen Sie ein Bild aus.")
                else:
                    try:
                        from database import add_company_image_template

                        image_bytes = uploaded_image.getvalue()
                        template_id = add_company_image_template(
                            company_id=company_id,
                            name=template_name.strip(),
                            image_data=image_bytes,
                            template_type=template_type,
                            original_filename=uploaded_image.name
                        )
                        if template_id:
                            st.success(
                                f" Bildvorlage '{template_name}' erfolgreich hochgeladen!")
                            st.rerun()
                        else:
                            st.error(" Fehler beim Speichern der Bildvorlage.")
                    except ImportError:
                        st.error(" Datenbankfunktionen nicht verfügbar.")

    # Vorhandene Bildvorlagen auflisten
    try:
        import base64

        from database import (
            delete_company_image_template,
            get_company_image_template_data,
            list_company_image_templates,
            update_company_image_template,
        )

        image_templates = list_company_image_templates(company_id)

        if image_templates:
            st.markdown("###  Vorhandene Bildvorlagen")

            # Galerie-Ansicht
            cols_per_row = 3
            for i in range(0, len(image_templates), cols_per_row):
                cols = st.columns(cols_per_row)

                for j, template in enumerate(
                        image_templates[i:i + cols_per_row]):
                    with cols[j]:
                        st.markdown(f"**{template['name']}**")
                        st.caption(f"Typ: {template['template_type']}")

                        # Bild anzeigen
                        try:
                            image_data = get_company_image_template_data(
                                template['id'])
                            if image_data:
                                st.image(image_data, width=200)
                            else:
                                st.error("Bild nicht gefunden")
                        except Exception as e:
                            st.error(f"Fehler beim Laden: {str(e)}")

                        # Bearbeitung und Löschung
                        with st.expander(" Bearbeiten"):
                            with st.form(f"edit_image_template_{template['id']}"):
                                new_name = st.text_input(
                                    "Name ändern",
                                    value=template['name'],
                                    key=f"img_name_{template['id']}"
                                )

                                col_save, col_del = st.columns(2)

                                with col_save:
                                    if st.form_submit_button(
                                            "", help="Speichern"):
                                        if update_company_image_template(
                                                template['id'], new_name):
                                            st.success("Name aktualisiert!")
                                            st.rerun()
                                        else:
                                            st.error(
                                                "Fehler beim Aktualisieren.")

                                with col_del:
                                    if st.form_submit_button(
                                            "", help="Löschen", type="secondary"):
                                        if delete_company_image_template(
                                                template['id']):
                                            st.success("Bildvorlage gelöscht!")
                                            st.rerun()
                                        else:
                                            st.error("Fehler beim Löschen.")
        else:
            st.info(" Noch keine Bildvorlagen für diese Firma hochgeladen.")

    except ImportError:
        st.error(" Datenbankfunktionen für Bildvorlagen nicht verfügbar.")
