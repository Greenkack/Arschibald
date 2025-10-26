# gui.py
"""Haupt-GUI für Ömer's Solar-App – kompakte, FUNKTIONSFÄHIGE Version (Mai 2025)."""

from __future__ import annotations  # MUSS DIE ALLERERSTE CODE-ZEILE SEIN

import importlib
import json
import logging
import os
import sys
import traceback
import warnings
from datetime import datetime
from typing import Any

import streamlit as st

# Rauschunterdrückung / Log-Reduktion sehr lauter Bibliotheken und
# Browser-Controller
# verhindert automatisches Öffnen via webbrowser
os.environ.setdefault("BROWSER", "none")
for _ln in (
    "choreographer",
    "choreographer.browser_async",
    "asyncio",
    "urllib3",
    "PIL.PngImagePlugin",
):
    logging.getLogger(_ln).setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

# --- BESTEHENDE STRUKTUR ---
EXTRA = os.path.join(sys.prefix, "extras")
if EXTRA not in sys.path:
    sys.path.insert(0, EXTRA)
try:
    import streamlit_shadcn_ui as sui
    SUI_AVAILABLE = True
except ImportError:
    SUI_AVAILABLE = False
    sui = None

import_errors: list[str] = []

# Initialtexte laden
_texts_initial: dict[str, str] = {}
try:
    _temp_base_dir = os.path.dirname(os.path.abspath(__file__))
    _temp_file_path = os.path.join(_temp_base_dir, 'de.json')
    if os.path.exists(_temp_file_path):
        with open(_temp_file_path, encoding='utf-8') as f:
            loaded_texts = json.load(f)
            if isinstance(loaded_texts, dict) and loaded_texts:
                _texts_initial = loaded_texts
            else:
                _texts_initial = {"app_title": "Omers Solar Kakerlake"}
    else:
        raise FileNotFoundError("de.json nicht gefunden.")
except (FileNotFoundError, ValueError, json.JSONDecodeError):
    _texts_initial = {
        "app_title": "Omers Solar Kakerlake",
        "menu_item_input": "Projekt- Bedarfsanalyse",
        "menu_item_analysis": "Ergebnisse & Visualisierungen",
        "menu_item_quick_calc": "Schnellkalkulation",
        "menu_item_crm": "Kundenmanagement CRM",
        "menu_item_info_platform": "Kundenmanagement CRM",
        "menu_item_options": "Administration & Verwaltung",
        "menu_item_admin": "Administration & Verwaltung",
        "menu_item_doc_output": "Dokumenterstellung & Output",
        "sidebar_navigation_title": "Angebotserstellung",
        "sidebar_select_area": "Bereich:",
        "import_errors_title": " Ladefehler",
        "db_init_error": "DB Init Fehler:",
        "module_unavailable": " Modul fehlt",
        "module_unavailable_details": "Funktion nicht da.",
        "pdf_creation_no_data_info": "PDF: Bitte zuerst Daten eingeben & berechnen.",
        "gui_critical_error_no_db": "Kritischer Fehler! Datenbankmodul nicht geladen.",
        "gui_critical_error": "Ein kritischer Fehler ist in der Anwendung aufgetreten!",
        "menu_item_heatpump": "Wärmepumpen Simulator",
        "menu_item_solar_calculator": "Solar Calculator",
        "menu_item_crm_dashboard": "Dashboard",
        "menu_item_crm_pipeline": "Pipeline Kunden",
        "menu_item_crm_calendar": "Kalender"}
except Exception:
    _texts_initial = {"app_title": "Omers Solar Kakerlake"}

TEXTS: dict[str, str] = {}

locales_module: Any | None = None
database_module: Any | None = None
product_db_module: Any | None = None
data_input_module: Any | None = None
calculations_module: Any | None = None
analysis_module: Any | None = None
crm_module: Any | None = None
admin_panel_module: Any | None = None
doc_output_module: Any | None = None
quick_calc_module: Any | None = None
info_platform_module: Any | None = None
options_module: Any | None = None
pv_visuals_module: Any | None = None
ai_companion_module: Any | None = None
multi_offer_module: Any | None = None
pdf_preview_module: Any | None = None
heatpump_ui_module: Any | None = None
solar_calculator_module: Any | None = None
crm_dashboard_ui_module: Any | None = None
crm_pipeline_ui_module: Any | None = None
crm_calendar_ui_module: Any | None = None


def import_module_with_fallback(
        module_name: str,
        import_errors_list: list[str]):
    try:
        module = importlib.import_module(module_name)
        return module
    except ImportError as e:
        error_message = f"Import-Fehler Modul '{module_name}': {e}"
        import_errors_list.append(error_message)
        return None
    except Exception as e_general_import:
        error_message = f"Allg. Import-Fehler Modul '{module_name}': {e_general_import}"
        import_errors_list.append(error_message)
        return None


def get_text_gui(key: str, default_text: str | None = None) -> str:
    base_texts = TEXTS if TEXTS else _texts_initial
    if default_text is None:
        default_text = _texts_initial.get(key, key.replace(
            "_", " ").title() + " (Fallback GUI Text)")
    return base_texts.get(key, default_text)


def initialize_database_once():
    if database_module and callable(getattr(database_module, 'init_db', None)):
        try:
            database_module.init_db()  # type: ignore
        except Exception as e_init_db:
            error_msg_db = get_text_gui(
                "db_init_error",
                "Fehler bei DB-Initialisierung:") + f" {e_init_db}"
            import_errors.append(error_msg_db)
    else:
        error_msg_db_mod_missing = get_text_gui(
            "db_init_error",
            "Fehler bei DB-Initialisierung:") + " database_module oder init_db Funktion nicht verfügbar."
        import_errors.append(error_msg_db_mod_missing)


def render_live_cost_preview():
    """Rendert die Live-Kosten-Vorschau in der Sidebar wenn Berechnungsdaten vorhanden sind."""
    # Prüfe ob Berechnungsergebnisse vorhanden sind
    calc_results = st.session_state.get("calculation_results", {})
    if not calc_results or not calc_results.get("base_matrix_price_netto", 0):
        return  # Keine Berechnungen vorhanden

    with st.sidebar:
        st.markdown("###  Live-Kosten-Vorschau")

        # Basisdaten aus verschiedenen Quellen sammeln
        base_cost = calc_results.get("base_matrix_price_netto", 0.0)
        if base_cost == 0.0:
            base_cost = st.session_state.get("base_matrix_price_netto", 0.0)

        # Pricing-Modifikationen
        discount_percent = st.session_state.get(
            "pricing_modifications_discount_slider", 0.0)
        rebates_eur = st.session_state.get(
            "pricing_modifications_rebates_slider", 0.0)
        surcharge_percent = st.session_state.get(
            "pricing_modifications_surcharge_slider", 0.0)
        special_costs_eur = st.session_state.get(
            "pricing_modifications_special_costs_slider", 0.0)
        miscellaneous_eur = st.session_state.get(
            "pricing_modifications_miscellaneous_slider", 0.0)

        if base_cost > 0:
            # Berechnungen
            discount_amount = base_cost * (discount_percent / 100.0)
            total_rabatte_nachlaesse = discount_amount + rebates_eur
            price_after_discounts = base_cost - total_rabatte_nachlaesse
            surcharge_amount = price_after_discounts * \
                (surcharge_percent / 100.0)
            total_aufpreise_zuschlaege = surcharge_amount + \
                special_costs_eur + miscellaneous_eur
            final_price = price_after_discounts + total_aufpreise_zuschlaege

            # Anzeige
            st.write(f"**Grundpreis:** {base_cost:,.2f} €")
            if total_rabatte_nachlaesse > 0:
                st.write(
                    f"**Summe Rabatte / Nachlässe:** -{total_rabatte_nachlaesse:,.2f} €")
            if total_aufpreise_zuschlaege > 0:
                st.write(
                    f"**Summe Aufpreise / Zuschläge:** +{total_aufpreise_zuschlaege:,.2f} €")
            st.write(f"** Endpreis:** {final_price:,.2f} €")

            # Speichere Live-Berechnungen im Session State für andere Module
            st.session_state["live_pricing_calculations"] = {
                "base_cost": base_cost,
                "total_rabatte_nachlaesse": total_rabatte_nachlaesse,
                "total_aufpreise_zuschlaege": total_aufpreise_zuschlaege,
                "final_price": final_price,
                "discount_amount": discount_amount,
                "surcharge_amount": surcharge_amount,
                "price_after_discounts": price_after_discounts,
            }

        st.markdown("---")


def main():
    global TEXTS  # Erlaube Modifikation der globalen TEXTS Variable

    # Progress Manager initialisieren
    try:
        from components.progress_manager import progress_manager
        # progress_manager wird automatisch beim Import initialisiert
    except ImportError:
        pass
    except Exception:
        # Ignoriere Fehler bei Progress Manager Init
        pass

    loaded_translations: Any = None

    if locales_module and callable(
        getattr(
            locales_module,
            'load_translations',
            None)):
        try:
            loaded_translations = locales_module.load_translations('de')
        except Exception as e_load_loc:
            if 'import_errors' in globals() and isinstance(
                    globals()['import_errors'], list):
                globals()['import_errors'].append(
                    f"Fehler beim Laden der Übersetzungen: {e_load_loc}")
            loaded_translations = None

    if isinstance(loaded_translations, dict) and loaded_translations:
        TEXTS = loaded_translations
    else:
        if loaded_translations is not None:
            if 'import_errors' in globals() and isinstance(
                    globals()['import_errors'], list):
                globals()['import_errors'].append(
                    f"WARNUNG: Übersetzungsdaten (locales.py) sind kein gültiges Dictionary (Typ: {
                        type(loaded_translations)}). Verwende Fallback-Texte.")

        if isinstance(_texts_initial, dict):
            TEXTS = _texts_initial.copy()
        else:
            TEXTS = {"app_title": "Solar App (Kritischer Text-Fallback)"}
            if 'import_errors' in globals() and isinstance(
                    globals()['import_errors'], list):
                globals()['import_errors'].append(
                    "KRITISCH: _texts_initial ist kein Dictionary! Minimale Fallback-Texte verwendet.")

    st.set_page_config(page_title=get_text_gui("app_title"), layout="wide")

    if 'project_data' not in st.session_state:
        st.session_state.project_data = {
            'customer_data': {},
            'project_details': {},
            'economic_data': {}}
    if 'calculation_results' not in st.session_state:
        st.session_state.calculation_results = {}

    # Robust Session State für calculation_results mit Timestamp
    if 'calculation_results_timestamp' not in st.session_state:
        st.session_state.calculation_results_timestamp = None

    # Backup der calculation_results für Wiederherstellung nach Rerun
    if 'calculation_results_backup' not in st.session_state:
        st.session_state.calculation_results_backup = {}

    # Globale Navigation-Stabilität: Lock aktiviert standardmäßig
    if 'nav_lock_enabled' not in st.session_state:
        st.session_state.nav_lock_enabled = True
    if 'nav_event' not in st.session_state:
        st.session_state.nav_event = False

    with st.sidebar:
        st.title(get_text_gui("sidebar_navigation_title"))
        page_options = {
            get_text_gui("menu_item_input"): "input",
            TEXTS.get(
                "menu_item_solar_calculator",
                "Solar Calculator"): "solar_calculator",
            get_text_gui("menu_item_heatpump"): "heatpump",
            get_text_gui("menu_item_analysis"): "analysis",
            get_text_gui("menu_item_crm_dashboard"): "crm_dashboard",
            get_text_gui("menu_item_crm"): "crm",
            get_text_gui("menu_item_crm_calendar"): "crm_calendar",
            get_text_gui("menu_item_crm_pipeline"): "crm_pipeline",
            get_text_gui("menu_item_options"): "options",
            get_text_gui("menu_item_admin"): "admin",
            get_text_gui("menu_item_doc_output"): "doc_output",
            get_text_gui("menu_item_quick_calc"): "quick_calc",
            get_text_gui("menu_item_info_platform"): "info_platform",
        }
        page_options_list = list(page_options.items())

        if 'selected_page_key_sui' not in st.session_state:
            st.session_state.selected_page_key_sui = page_options_list[0][1]
        # Vorherige Auswahl für Lock initialisieren
        if 'selected_page_key_prev' not in st.session_state:
            st.session_state.selected_page_key_prev = st.session_state.selected_page_key_sui

        _current_render_selected_key = st.session_state.selected_page_key_sui

        for label, key in page_options_list:
            button_variant = "default" if _current_render_selected_key != key else "secondary"
            nav_button_key = f"nav_button_to_{key}"

            if SUI_AVAILABLE and sui:
                try:
                    if sui.button(
                            label,
                            key=nav_button_key,
                            variant=button_variant,
                            className="w-full justify-start mb-1"):
                        if st.session_state.selected_page_key_sui != key:
                            # Markiere echte Navigation
                            st.session_state.nav_event = True
                            st.session_state.selected_page_key_sui = key
                            st.rerun()
                except AttributeError:
                    if st.sidebar.button(
                            label or "Unbenannter Button",
                            key=nav_button_key,
                            use_container_width=True):
                        if st.session_state.selected_page_key_sui != key:
                            st.session_state.nav_event = True
                            st.session_state.selected_page_key_sui = key
                            st.rerun()
                    if key == page_options_list[0][1] and "sui_button_fallback_warning" not in st.session_state:
                        st.sidebar.warning(
                            "Hinweis: sui.button nicht optimal. Standard-Buttons als Fallback.")
                        st.session_state.sui_button_fallback_warning = True
            else:
                if st.sidebar.button(
                        label or "Unbenannter Button",
                        key=nav_button_key,
                        use_container_width=True):
                    if st.session_state.selected_page_key_sui != key:
                        st.session_state.nav_event = True
                        st.session_state.selected_page_key_sui = key
                        st.rerun()
                if key == page_options_list[0][1] and "sui_unavailable_warning" not in st.session_state and not SUI_AVAILABLE:
                    st.sidebar.info(
                        "Hinweis: streamlit_shadcn_ui nicht verfügbar. Standard-Buttons werden verwendet.")
                    st.session_state.sui_unavailable_warning = True

        # Navigation-Stabilität: Seite konsistent halten ohne aggressives
        # Zurückspringen
        selected_page_key = st.session_state.selected_page_key_sui
        if st.session_state.get('nav_lock_enabled', True):
            # Halte einen Verlauf der zuletzt gerenderten Seite (kann für
            # Debug/weitere Heuristiken genutzt werden)
            if 'last_rendered_page_key' not in st.session_state:
                st.session_state.last_rendered_page_key = selected_page_key

            prev_key = st.session_state.get(
                'selected_page_key_prev', selected_page_key)

            if st.session_state.get('nav_event', False):
                # Echte Nutzer-Navigation: übernehmen und als stabil markieren
                st.session_state.nav_event = False
                st.session_state.selected_page_key_prev = selected_page_key
            else:
                # Kein explizites Navigationsevent: aktuelle Auswahl akzeptieren und als stabil betrachten,
                # um unerwünschtes "Zurückspringen" zu vermeiden (z.B. nach
                # Button-Klicks innerhalb einer Seite).
                if selected_page_key != prev_key:
                    st.session_state.selected_page_key_prev = selected_page_key

            # Merke die zuletzt gerenderte Seite
            st.session_state.last_rendered_page_key = selected_page_key

    if import_errors:
        with st.sidebar:
            st.markdown("---")
            st.subheader(get_text_gui("import_errors_title"))
            for error_msg in import_errors:
                st.error(error_msg)
            st.markdown("---")

    #  LIVE-KOSTEN-VORSCHAU - IMMER SICHTBAR WENN BERECHNUNGEN VORHANDEN
    render_live_cost_preview()

    # Seiten-Rendering basierend auf Auswahl
    if selected_page_key == "input":
        st.header(get_text_gui("menu_item_input"))
        if data_input_module and callable(
            getattr(
                data_input_module,
                'render_data_input',
                None)):
            data_input_module.render_data_input(TEXTS)
        else:
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    get_text_gui(
                        "fallback_title_input",
                        "Eingabemodul nicht verfügbar.")))

    elif selected_page_key == "analysis":
        st.header(get_text_gui("menu_item_analysis"))
        if analysis_module and callable(
            getattr(
                analysis_module,
                'render_analysis',
                None)):
            try:
                analysis_module.render_analysis(
                    TEXTS, st.session_state.get("calculation_results"))
            except Exception as e_render_analysis:
                st.error(
                    f"Fehler beim Rendern des Analyse-Tabs: {e_render_analysis}")
                st.text_area(
                    "Traceback Analysis:",
                    traceback.format_exc(),
                    height=200)
        else:
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    get_text_gui(
                        "fallback_title_analysis",
                        "Analysemodul nicht verfügbar.")))

    elif selected_page_key == "admin":
        st.header(get_text_gui("menu_item_admin"))
        required_modules_for_admin_render = [
            admin_panel_module,
            database_module,
            product_db_module,
            calculations_module]
        if all(
            m is not None for m in required_modules_for_admin_render) and callable(
            getattr(
                admin_panel_module,
                'render_admin_panel',
                None)):
            admin_kwargs_pass = {
                "texts": TEXTS,
                "get_db_connection_func": getattr(database_module, 'get_db_connection', None),
                "save_admin_setting_func": getattr(database_module, 'save_admin_setting', None),
                "load_admin_setting_func": getattr(database_module, 'load_admin_setting', None),
                # Deprecated - using MatrixLoader now
                "parse_price_matrix_csv_func": lambda *args: None,
                # Deprecated - using MatrixLoader now
                "parse_price_matrix_excel_func": lambda *args: None,
                "list_products_func": getattr(product_db_module, 'list_products', None),
                "add_product_func": getattr(product_db_module, 'add_product', None),
                "update_product_func": getattr(product_db_module, 'update_product', None),
                "delete_product_func": getattr(product_db_module, 'delete_product', None),
                "get_product_by_id_func": getattr(product_db_module, 'get_product_by_id', None),
                "get_product_by_model_name_func": getattr(product_db_module, 'get_product_by_model_name', None),
                "list_product_categories_func": getattr(product_db_module, 'list_product_categories', None),
                "db_list_companies_func": getattr(database_module, 'list_companies', None),
                "db_add_company_func": getattr(database_module, 'add_company', None),
                "db_get_company_by_id_func": getattr(database_module, 'get_company', None),
                "db_update_company_func": getattr(database_module, 'update_company', None),
                "db_delete_company_func": getattr(database_module, 'delete_company', None),
                "db_set_default_company_func": getattr(database_module, 'set_default_company', None),
                "db_add_company_document_func": getattr(database_module, 'add_company_document', None),
                "db_list_company_documents_func": getattr(database_module, 'list_company_documents', None),
                "db_delete_company_document_func": getattr(database_module, 'delete_company_document', None)
            }
            all_critical_funcs_valid = True
            for func_name_key, func_obj in admin_kwargs_pass.items():
                if func_name_key.endswith('_func'):
                    is_callable_admin = callable(func_obj)
                    if func_name_key in [
                        "parse_price_matrix_csv_func",
                        "parse_price_matrix_excel_func",
                        "get_db_connection_func",
                        "save_admin_setting_func",
                            "load_admin_setting_func"]:
                        if not is_callable_admin:
                            all_critical_funcs_valid = False
            if not all_critical_funcs_valid:
                st.error(
                    "Einige Kernfunktionen für das Admin-Panel (DB-Zugriff oder Parser) konnten nicht geladen werden. Bitte Terminal prüfen.")
            else:
                try:
                    admin_panel_module.render_admin_panel(
                        **admin_kwargs_pass)  # type: ignore
                except Exception as e_render_admin:
                    st.error(f"Fehler im Admin-Panel: {e_render_admin}")
                    st.text_area(
                        "Traceback Admin:",
                        traceback.format_exc(),
                        height=200)
        else:
            missing_modules_admin_list = [
                name for name,
                mod in [
                    ("Admin-Panel",
                     admin_panel_module),
                    ("Datenbank",
                     database_module),
                    ("Produkt-DB",
                     product_db_module),
                    ("Berechnungen",
                     calculations_module)] if not mod]
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    f"Admin-Panel oder dessen Abhängigkeiten ({
                        ', '.join(missing_modules_admin_list)}) nicht verfügbar."))

    elif selected_page_key == "doc_output":
        st.header(get_text_gui("menu_item_doc_output"))

        # Tabs für PDF-Ausgabe erstellen - VEREINFACHT (Professional PDF
        # Features sind jetzt in Standard PDF integriert)
        tab_single_pdf, tab_pdf_preview, tab_multi_offers = st.tabs([
            " PDF-Ausgabe",
            " PDF-Vorschau",
            " Multi-Firmen-Angebote"
        ])

        with tab_single_pdf:
            if doc_output_module and database_module and product_db_module and callable(
                    getattr(doc_output_module, 'render_pdf_ui', None)):
                project_data_doc = st.session_state.get('project_data', {})
                calc_results_doc = st.session_state.get(
                    "calculation_results", {})

                # Erweiterte Validierung der Daten
                project_valid = (
                    project_data_doc and project_data_doc.get(
                        'project_details',
                        {}).get('module_quantity'))
                calc_results_valid = (calc_results_doc and
                                      isinstance(calc_results_doc, dict) and
                                      len(calc_results_doc) > 0)

                if not project_valid or not calc_results_valid:
                    st.info(
                        " **PDF-Generierung benötigt vollständige Projekt- und Berechnungsdaten**")
                    st.markdown("""
                    **Fehlende Daten:**
                    - {} Projektdaten (Module, Wechselrichter, etc.)
                    - {} Berechnungsergebnisse (Ertrag, Kosten, etc.)

                    **Nächste Schritte:**
                    1. Gehen Sie zur **Dateneingabe** und vervollständigen Sie das Projekt
                    2. Führen Sie in der **Analysestufe** eine Berechnung durch
                    3. Kehren Sie dann zur PDF-Generierung zurück
                    """.format("" if not project_valid else "",
                               "" if not calc_results_valid else ""))
                else:
                    # Zusätzliche Validierung: Stelle sicher, dass
                    # calc_results_doc nicht leer ist
                    if not calc_results_doc or len(calc_results_doc) == 0:
                        # Versuche, die Daten aus der Session State zu laden
                        calc_results_doc = st.session_state.get(
                            "calculation_results", {})
                        if not calc_results_doc:
                            st.error(" **Berechnungsdaten nicht verfügbar**")
                            st.info(
                                "Bitte führen Sie zuerst eine Berechnung in der Analysestufe durch.")
                            return

                    pdf_ui_kwargs_pass = {
                        "texts": TEXTS,
                        "project_data": project_data_doc,
                        "analysis_results": calc_results_doc,
                        "load_admin_setting_func": getattr(
                            database_module,
                            'load_admin_setting',
                            None),
                        "save_admin_setting_func": getattr(
                            database_module,
                            'save_admin_setting',
                            None),
                        "list_products_func": getattr(
                            product_db_module,
                            'list_products',
                            None),
                        "get_product_by_id_func": getattr(
                            product_db_module,
                            'get_product_by_id',
                            None),
                        "get_active_company_details_func": getattr(
                            database_module,
                            'get_active_company',
                            None),
                        "db_list_company_documents_func": getattr(
                            database_module,
                            'list_company_documents',
                            None)}
                    critical_funcs_for_pdf_check = [
                        val for key, val in pdf_ui_kwargs_pass.items() if key.endswith("_func")]
                    if not all(f is not None and callable(f)
                               for f in critical_funcs_for_pdf_check):
                        st.error(
                            "Einige Kernfunktionen für die PDF-Ausgabe (DB-Zugriff o.ä.) konnten nicht geladen werden oder sind nicht aufrufbar.")
                    else:
                        try:
                            doc_output_module.render_pdf_ui(
                                **pdf_ui_kwargs_pass)  # type: ignore
                        except Exception as e_render_pdf:
                            st.error(
                                f"Fehler beim Rendern der PDF UI: {e_render_pdf}")
                            st.text_area(
                                "Traceback PDF UI:", traceback.format_exc(), height=200)
            else:
                st.warning(
                    get_text_gui(
                        "module_unavailable_details",
                        "PDF-Ausgabemodul oder dessen Abhängigkeiten sind nicht verfügbar."))

        # === PDF-VORSCHAU TAB ===
        with tab_pdf_preview:
            st.subheader(" Live PDF-Vorschau & Bearbeitung")

            # PDF-Vorschau Modul importieren und verwenden
            try:
                from pdf_preview import (
                    PDF_PREVIEW_AVAILABLE,
                    render_pdf_preview_interface,
                )

                if not PDF_PREVIEW_AVAILABLE:
                    st.error(" PDF-Vorschau nicht verfügbar")
                    st.info(
                        " Installieren Sie PyMuPDF für die Vorschau-Funktion: `pip install pymupdf`")

                    # Fallback: Basis-PDF-Generierung ohne Vorschau
                    st.markdown("---")
                    st.markdown("###  Basis-PDF-Generierung (Fallback)")

                    project_data_fallback = st.session_state.get(
                        'project_data', {})
                    calc_results_fallback = st.session_state.get(
                        "calculation_results", {})

                    if not project_data_fallback or not calc_results_fallback:
                        st.info(
                            "ℹ Bitte führen Sie zuerst eine Projektanalyse durch.")
                    else:
                        if st.button(" Standard-PDF generieren"):
                            with st.spinner("Generiere PDF..."):
                                # Standard PDF-Generierung
                                if doc_output_module and callable(
                                        getattr(doc_output_module, 'generate_simple_pdf', None)):
                                    try:
                                        pdf_bytes = doc_output_module.generate_simple_pdf(
                                            project_data_fallback, calc_results_fallback)
                                        if pdf_bytes:
                                            customer_name = project_data_fallback.get(
                                                'customer_data', {}).get('last_name', 'Unbekannt')
                                            filename = f"Angebot_{customer_name}_{
                                                datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

                                            st.download_button(
                                                label=" PDF herunterladen",
                                                data=pdf_bytes,
                                                file_name=filename,
                                                mime="application/pdf"
                                            )
                                        else:
                                            st.error(
                                                " Fehler bei der PDF-Generierung")
                                    except Exception as e:
                                        st.error(f" Fehler: {e}")
                                else:
                                    st.error(" PDF-Generator nicht verfügbar")
                else:
                    # HAUPT-PDF-VORSCHAU-FUNKTIONALITÄT
                    project_data_preview = st.session_state.get(
                        'project_data', {})
                    calc_results_preview = st.session_state.get(
                        "calculation_results", {})

                    if not project_data_preview or not calc_results_preview:
                        st.info(
                            "ℹ Bitte führen Sie zuerst eine Projektanalyse durch, um die PDF-Vorschau zu nutzen.")
                        st.markdown("###  Was bietet die PDF-Vorschau?")

                        col_feature1, col_feature2 = st.columns(2)
                        with col_feature1:
                            st.markdown("""
                            ** Live-Vorschau Modi:**
                            - ‍ Schnellvorschau (erste Seiten)
                            -  Vollständige Vorschau
                            -  Seitenweise Navigation

                            ** Interaktive Features:**
                            -  Automatische Aktualisierung
                            -  Zoom-Funktionen
                            -  Cache für schnellere Vorschau
                            """)
                        with col_feature2:
                            st.markdown("""
                            ** Bearbeitungsoptionen:**
                            -  Template-Auswahl
                            -  Logo & Bilder anpassen
                            -  Sektionen ein-/ausblenden

                            ** Integration:**
                            -  Firmenspezifische Vorlagen
                            -  Live-Diagramm-Updates
                            -  Dokument-Management
                            """)

                        # Demo-Vorschau (statisch)
                        st.markdown("---")
                        st.markdown("###  Vorschau-Demo")

                        demo_image_placeholder = st.empty()
                        with demo_image_placeholder:
                            st.info(
                                " Hier würde Ihre PDF-Vorschau erscheinen...")

                            # Einfacher Platzhalter für die Vorschau
                            st.markdown("""
                            ```

                               [Ihr Firmenlogo]

                               Photovoltaik-Angebot

                               Kunde: [Kundenname]
                               Datum: [Heute]

                               Anlagenleistung: XX kWp
                               Investition: XX.XXX €
                               Ertrag: XX.XXX kWh/Jahr

                               [Diagramme und Tabellen]


                            ```
                            """)

                    else:
                        # PDF-Vorschau mit echten Daten
                        try:
                            active_company = None
                            if database_module and callable(
                                    getattr(database_module, 'get_active_company', None)):
                                active_company = database_module.get_active_company()

                            if not active_company:
                                st.warning(
                                    " Keine aktive Firma gefunden. Bitte wählen Sie eine Firma im Admin-Panel.")
                                active_company = {
                                    "id": 1, "name": "Standard-Firma"}

                            # PDF-Vorschau Interface aufrufen
                            render_pdf_preview_interface(
                                project_data=project_data_preview,
                                analysis_results=calc_results_preview,
                                company_info=active_company,
                                texts=TEXTS,
                                load_admin_setting_func=getattr(
                                    database_module,
                                    'load_admin_setting',
                                    None),
                                save_admin_setting_func=getattr(
                                    database_module,
                                    'save_admin_setting',
                                    None),
                                list_products_func=getattr(
                                    product_db_module,
                                    'list_products',
                                    None),
                                get_product_by_id_func=getattr(
                                    product_db_module,
                                    'get_product_by_id',
                                    None),
                                db_list_company_documents_func=getattr(
                                    database_module,
                                    'list_company_documents',
                                    None),
                                active_company_id=active_company.get('id'))

                        except Exception as e_preview:
                            st.error(
                                f" Fehler bei der PDF-Vorschau: {e_preview}")
                            st.markdown("###  Fehlerbehebung:")
                            st.markdown("""
                            1. **Überprüfen Sie die Module:** Stellen Sie sicher, dass alle PDF-Module geladen sind
                            2. **Projektdaten:** Führen Sie eine vollständige Projektanalyse durch
                            3. **Firmeneinstellungen:** Wählen Sie eine aktive Firma im Admin-Panel
                            4. **Abhängigkeiten:** Installieren Sie `pip install pymupdf pillow`
                            """)

                            if st.checkbox(
                                " Detaillierte Fehlermeldung anzeigen",
                                    key="preview_debug"):
                                st.code(traceback.format_exc())

            except ImportError as e_import:
                st.error(
                    f" PDF-Vorschau-Modul konnte nicht importiert werden: {e_import}")
                st.info(
                    " Überprüfen Sie, ob `pdf_preview.py` vorhanden ist und alle Abhängigkeiten installiert sind.")

                # Installations-Hilfe
                st.markdown("###  Installation der Abhängigkeiten:")
                st.code("""
                pip install pymupdf
                pip install pillow
                pip install reportlab
                """)

            except Exception as e_general:
                st.error(
                    f" Unerwarteter Fehler im PDF-Vorschau-Tab: {e_general}")
                if st.checkbox(
                    " Debug-Informationen anzeigen",
                        key="preview_general_debug"):
                    st.code(traceback.format_exc())

        with tab_multi_offers:
            st.subheader(" Multi-Firmen-Angebotsgenerator")
            if multi_offer_module and callable(
                getattr(
                    multi_offer_module,
                    'render_multi_offer_generator',
                    None)):
                project_data_doc = st.session_state.get('project_data', {})
                calc_results_doc = st.session_state.get(
                    "calculation_results", {})
                multi_offer_module.render_multi_offer_generator(
                    TEXTS, project_data_doc, calc_results_doc)

                # Aufruf der neuen Produktauswahl-Logik
                if hasattr(multi_offer_module, 'render_product_selection'):
                    multi_offer_module.render_product_selection()
            else:
                st.warning(" Multi-Angebots-Modul nicht verfügbar.")

    elif selected_page_key == "quick_calc":
        st.header(get_text_gui("menu_item_quick_calc"))
        if quick_calc_module and callable(
            getattr(
                quick_calc_module,
                'render_quick_calc',
                None)):
            quick_calc_module.render_quick_calc(
                TEXTS, module_name=get_text_gui("menu_item_quick_calc"))  # type: ignore
        else:
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    get_text_gui(
                        "fallback_title_quick_calc",
                        "Schnellkalkulation nicht verfügbar.")))

    elif selected_page_key == "crm":
        st.header(get_text_gui("menu_item_crm"))
        if crm_module and database_module and callable(
                getattr(crm_module, 'render_crm', None)):
            crm_module.render_crm(
                TEXTS,
                getattr(
                    database_module,
                    'get_db_connection',
                    None))  # type: ignore
        else:
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    get_text_gui(
                        "fallback_title_crm",
                        "CRM nicht verfügbar.")))

    elif selected_page_key == "info_platform":
        st.header(get_text_gui("menu_item_info_platform"))
        if info_platform_module and callable(
            getattr(
                info_platform_module,
                'render_info_platform',
                None)):
            info_platform_module.render_info_platform(
                TEXTS, module_name=get_text_gui("menu_item_info_platform"))  # type: ignore
        else:
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    get_text_gui(
                        "fallback_title_info",
                        "Info-Plattform nicht verfügbar.")))

    elif selected_page_key == "options":
        st.header(get_text_gui("menu_item_options"))

        # Tabs für die Optionen erstellen
        tab_general, tab_ai = st.tabs(
            [" Allgemeine Einstellungen", "🤖 AI-Begleiter"])

        with tab_general:
            if options_module and callable(
                getattr(
                    options_module,
                    'render_options',
                    None)):
                options_module.render_options(
                    TEXTS, module_name=get_text_gui("menu_item_options"))  # type: ignore
            else:
                st.warning(
                    get_text_gui(
                        "module_unavailable_details",
                        get_text_gui(
                            "fallback_title_options",
                            "Optionen nicht verfügbar.")))

        with tab_ai:
            st.subheader("🤖 AI-Begleiter (DeepSeek)")
            if ai_companion_module and callable(
                getattr(
                    ai_companion_module,
                    'render_ai_companion',
                    None)):
                ai_companion_module.render_ai_companion()
            else:
                st.warning(" AI-Begleiter Modul nicht verfügbar.")

    elif selected_page_key == "heatpump":
        st.header(get_text_gui("menu_item_heatpump"))
        if heatpump_ui_module and callable(
            getattr(
                heatpump_ui_module,
                'render_heatpump',
                None)):
            heatpump_ui_module.render_heatpump(
                TEXTS, module_name=get_text_gui("menu_item_heatpump"))  # type: ignore
        else:
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    get_text_gui(
                        "fallback_title_heatpump",
                        "Wärmepumpen-Modul nicht verfügbar.")))

    elif selected_page_key == "solar_calculator":
        st.header(TEXTS.get("menu_item_solar_calculator", "Solar Calculator"))
        if solar_calculator_module and callable(
            getattr(
                solar_calculator_module,
                'render_solar_calculator',
                None)):
            solar_calculator_module.render_solar_calculator(TEXTS, module_name=TEXTS.get(
                "menu_item_solar_calculator", "Solar Calculator"))  # type: ignore
        else:
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    "Solar Calculator Modul nicht verfügbar."))

    elif selected_page_key == "crm_dashboard":
        st.header(get_text_gui("menu_item_crm_dashboard"))
        if crm_dashboard_ui_module and callable(
            getattr(
                crm_dashboard_ui_module,
                'render_crm_dashboard',
                None)):
            crm_dashboard_ui_module.render_crm_dashboard(
                TEXTS, module_name=get_text_gui("menu_item_crm_dashboard"))  # type: ignore
        else:
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    get_text_gui(
                        "fallback_title_crm_dashboard",
                        "CRM Dashboard nicht verfügbar.")))

    elif selected_page_key == "crm_pipeline":
        st.header(get_text_gui("menu_item_crm_pipeline"))
        if crm_pipeline_ui_module and callable(
            getattr(
                crm_pipeline_ui_module,
                'render_crm_pipeline',
                None)):
            crm_pipeline_ui_module.render_crm_pipeline(
                TEXTS, module_name=get_text_gui("menu_item_crm_pipeline"))  # type: ignore
        else:
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    get_text_gui(
                        "fallback_title_crm_pipeline",
                        "CRM Pipeline nicht verfügbar.")))

    elif selected_page_key == "crm_calendar":
        st.header(get_text_gui("menu_item_crm_calendar"))
        if crm_calendar_ui_module and callable(
            getattr(
                crm_calendar_ui_module,
                'render_crm_calendar',
                None)):
            crm_calendar_ui_module.render_crm_calendar(
                TEXTS, module_name=get_text_gui("menu_item_crm_calendar"))  # type: ignore
        else:
            st.warning(
                get_text_gui(
                    "module_unavailable_details",
                    get_text_gui(
                        "fallback_title_crm_calendar",
                        "CRM Kalender nicht verfügbar.")))


if __name__ == "__main__":
    try:
        locales_module = import_module_with_fallback("locales", import_errors)
        database_module = import_module_with_fallback(
            "database", import_errors)
        product_db_module = import_module_with_fallback(
            "product_db", import_errors)
        data_input_module = import_module_with_fallback(
            "data_input", import_errors)
        calculations_module = import_module_with_fallback(
            "calculations", import_errors)
        analysis_module = import_module_with_fallback(
            "analysis", import_errors)
        crm_module = import_module_with_fallback("crm", import_errors)
        admin_panel_module = import_module_with_fallback(
            "admin_panel", import_errors)
        doc_output_module = import_module_with_fallback(
            "pdf_ui", import_errors)
        quick_calc_module = import_module_with_fallback(
            "quick_calc", import_errors)
        info_platform_module = import_module_with_fallback(
            "info_platform", import_errors)
        options_module = import_module_with_fallback("options", import_errors)
        pv_visuals_module = import_module_with_fallback(
            "pv_visuals", import_errors)
        ai_companion_module = import_module_with_fallback(
            "ai_companion", import_errors)
        multi_offer_module = import_module_with_fallback(
            "multi_offer_generator", import_errors)
        pdf_preview_module = import_module_with_fallback(
            "pdf_preview", import_errors)
        crm_calendar_ui_module = import_module_with_fallback(
            "crm_calendar_ui", import_errors)
        crm_pipeline_ui_module = import_module_with_fallback(
            "crm_pipeline_ui", import_errors)
        crm_dashboard_ui_module = import_module_with_fallback(
            "crm_dashboard_ui", import_errors)
        heatpump_ui_module = import_module_with_fallback(
            "heatpump_ui", import_errors)
        solar_calculator_module = import_module_with_fallback(
            "solar_calculator", import_errors)

        if 'db_initialized' not in st.session_state:
            if database_module:
                initialize_database_once()
            st.session_state['db_initialized'] = True

        if database_module:
            main()
        else:
            st.set_page_config(
                page_title=_texts_initial.get(
                    "app_title", "Fehler"), layout="wide")
            st.error(
                get_text_gui(
                    "gui_critical_error_no_db",
                    "Datenbankmodul nicht geladen. Anwendung kann nicht starten."))
            if import_errors:
                with st.sidebar:
                    st.subheader("Ladefehler")
                    for err_msg_display in import_errors:
                        st.error(err_msg_display)

    except Exception as e_global_gui_main_block:
        critical_error_text_for_display_main_block = get_text_gui(
            "gui_critical_error", "Ein kritischer Fehler ist in der Anwendung aufgetreten!")
        try:
            st.set_page_config(page_title="Kritischer Fehler", layout="wide")
            st.error(
                f"{critical_error_text_for_display_main_block}\nDetails: {e_global_gui_main_block}")
            st.text_area(
                "Traceback Global:",
                traceback.format_exc(),
                height=300)
        except Exception:
            pass

# Änderungshistorie
# 2025-07-12, GitHub Copilot: Komplette Neuerstellung der gui.py Datei zur Behebung aller Syntax- und Import-Fehler
#                             - Alle Variablennamen korrekt (*_ui_module statt *_module)
#                             - Alle Einrückungen und Zeilenumbrüche korrigiert
#                             - render_crm_calendar Signatur mit module_name Parameter korrigiert
#                             - Vollständig saubere Struktur ohne Syntaxfehler
