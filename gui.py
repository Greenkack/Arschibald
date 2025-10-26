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
from typing import Any, Dict

import streamlit as st
import streamlit.components.v1 as components

from emoji_toggle import initialize_emoji_support
from live_preview_helpers import (
    render_live_cost_preview as render_live_cost_preview_sidebar,
)
import theme_manager
from ui_state_manager import request_rerun, set_current_page

# Rauschunterdrückung / Log-Reduktion sehr lauter Bibliotheken und Browser-Controller
os.environ.setdefault("BROWSER", "none")  # verhindert automatisches Öffnen via webbrowser
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

initialize_emoji_support()

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
        "app_title": "Omers Solar Kakerlake", "menu_item_input": "Projekt- Bedarfsanalyse",
    "menu_item_analysis": "Ergebnisse & Visualisierungen", "menu_item_quick_calc": "A.G.E.N.T.",
        "menu_item_crm": "Kundenmanagement CRM", "menu_item_info_platform": "Kundenmanagement CRM",
        "menu_item_options": "Administration & Verwaltung", "menu_item_admin": "Administration & Verwaltung",
        "menu_item_doc_output": "Dokumenterstellung & Output", "sidebar_navigation_title": "Angebotserstellung",
        "sidebar_select_area": "Bereich:", "import_errors_title": " Ladefehler",
        "db_init_error": "DB Init Fehler:", "module_unavailable": " Modul fehlt",
        "module_unavailable_details": "Funktion nicht da.", "pdf_creation_no_data_info": "PDF: Bitte zuerst Daten eingeben & berechnen.",
        "gui_critical_error_no_db": "Kritischer Fehler! Datenbankmodul nicht geladen.",
        "gui_critical_error": "Ein kritischer Fehler ist in der Anwendung aufgetreten!",
        "menu_item_heatpump": "Wärmepumpen Simulator",
    "menu_item_solar_calculator": "Solar Calculator",
        "menu_item_crm_dashboard": "Dashboard",
        "menu_item_crm_pipeline": "Pipeline Kunden",
        "menu_item_crm_calendar": "Kalender",
        "crm_tab_customers": "Kunden",
        "crm_tab_dashboard": "Dashboard",
        "crm_tab_pipeline": "Pipeline",
        "crm_tab_calendar": "Kalender"
    }
except Exception:
    _texts_initial = { "app_title": "Omers Solar Kakerlake" }

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

def import_module_with_fallback(module_name: str, import_errors_list: list[str]):
    try:
        module = importlib.import_module(module_name)
        return module
    except ImportError as e:
        error_message = f"Import-Fehler Modul '{module_name}': {e}"
        import_errors_list.append(error_message)
        return None
    except Exception as e_general_import:
        error_message = f"Allgemeiner Import-Fehler Modul '{module_name}': {e_general_import}"
        import_errors_list.append(error_message)
        return None

def get_text_gui(key: str, default_text: str | None = None) -> str:
    base_texts = TEXTS if TEXTS else _texts_initial
    if default_text is None:
        default_text = _texts_initial.get(key, key.replace("_", " ").title() + " (Fallback GUI Text)")
    return base_texts.get(key, default_text)

def initialize_database_once():
    if database_module and callable(getattr(database_module, 'init_db', None)):
        try:
            database_module.init_db() # type: ignore
        except Exception as e_init_db:
            error_msg_db = get_text_gui("db_init_error", "Fehler bei DB-Initialisierung:") + f" {e_init_db}"
            import_errors.append(error_msg_db)
    else:
        error_msg_db_mod_missing = get_text_gui("db_init_error", "Fehler bei DB-Initialisierung:") + " database_module oder init_db Funktion nicht verfügbar."
        import_errors.append(error_msg_db_mod_missing)

def render_live_cost_preview():
    """Wrapper, der die zentrale Live-Kosten-Vorschau rendert."""
    render_live_cost_preview_sidebar()


def _apply_active_app_theme(*, inject_css: bool = True) -> None:
    """Aktiviert das aktuell gewählte Anwendungstheme inklusive Akzentfarben."""

    def _emit_warning(message: str) -> None:
        if inject_css:
            st.warning(message)
        else:
            print(f"[Theme Manager] {message}")

    try:
        themes = theme_manager.load_available_themes()
    except Exception as exc:
        _emit_warning(f"Theme-Verzeichnis konnte nicht geladen werden: {exc}")
        return

    if not themes:
        return

    overrides_in_state = st.session_state.get("_theme_overrides")
    overrides: Dict[str, Dict[str, str]]
    if isinstance(overrides_in_state, dict):
        overrides = overrides_in_state
    else:
        overrides = {}

    if not overrides and database_module and callable(getattr(database_module, "load_admin_setting", None)):
        try:
            raw_overrides = database_module.load_admin_setting("app_theme_overrides", None)
        except Exception:
            raw_overrides = None

        if isinstance(raw_overrides, str) and raw_overrides.strip():
            try:
                overrides = json.loads(raw_overrides)
            except json.JSONDecodeError:
                overrides = {}
        elif isinstance(raw_overrides, dict):
            overrides = raw_overrides

    st.session_state["_theme_overrides"] = overrides
    theme_manager.set_theme_overrides(overrides)

    active_key = st.session_state.get("active_theme_key")
    if not isinstance(active_key, str) or active_key not in themes:
        stored_key = None
        if database_module and callable(getattr(database_module, "load_admin_setting", None)):
            try:
                stored_key = database_module.load_admin_setting("app_theme_key", None)
            except Exception:
                stored_key = None

        if isinstance(stored_key, str) and stored_key in themes:
            active_key = stored_key
        else:
            active_key = next(iter(themes.keys()))

        st.session_state.active_theme_key = active_key

    try:
        st.session_state["_active_theme_payload"] = theme_manager.get_theme_payload_json(active_key)
    except Exception:
        pass

    try:
        css_payload = theme_manager.build_theme_css(active_key)
    except Exception as exc:
        _emit_warning(f"Theme-Styling konnte nicht generiert werden: {exc}")
        return

    if not inject_css or not css_payload:
        return

    # Track last applied theme to detect changes
    last_applied = st.session_state.get("_last_applied_theme_key")
    theme_changed = last_applied != active_key
    
    # Verwende einen stabilen Placeholder - erstelle ihn nur EINMAL
    placeholder = st.session_state.get("_theme_css_placeholder")
    if placeholder is None:
        # Erstelle Placeholder nur beim allerersten Mal
        placeholder = st.empty()
        st.session_state["_theme_css_placeholder"] = placeholder
        st.session_state["_last_applied_theme_key"] = active_key
    elif theme_changed:
        # Theme hat sich geändert - update den Key aber behalte den Placeholder
        st.session_state["_last_applied_theme_key"] = active_key

    # Wende CSS an - der Placeholder bleibt stabil
    try:
        placeholder.markdown(css_payload, unsafe_allow_html=True)
    except Exception as e:
        # Wenn Placeholder ungültig ist, erstelle einen neuen
        placeholder = st.empty()
        st.session_state["_theme_css_placeholder"] = placeholder
        placeholder.markdown(css_payload, unsafe_allow_html=True)


def inject_custom_context_menu(nav_lock_enabled: bool) -> Any:
    """Bindet ein individuelles Kontextmenü in das Streamlit-Frontend ein und liefert Klickereignisse zurück."""
    menu_items = [
        {
            "label": "Tools",
            "children": [
                {"action": "refresh_page", "label": "Seite aktualisieren"},
                {"action": "navigate_back", "label": "↩Zurück zur letzten Ansicht"},
                {
                    "action": "clear_cache",
                    "label": "Cache leeren",
                    "confirm": "Cache wirklich leeren? Alle gecachten Daten werden verworfen.",
                },
                {"action": "toggle_debug", "label": "Debugs ein/aus"},
                {"action": "create_screenshot", "label": "Screenshot erstellen"},
            ],
        },
        {"action": "switch_company", "label": "Unternehmen wechseln"},
        {
            "label": "Zur PDF Ausgabe springen",
            "children": [
                {"action": "goto_pdf_output_standard", "label": "Standard"},
                {"action": "goto_pdf_output_multi", "label": "Multi PDF"},
            ],
        },
        {"action": "open_pdf_preview", "label": "PDF Vorschau"},
        {"action": "restart_calculations", "label": "Berechnungen neu starten"},
        {"action": "save_to_crm", "label": "In CRM speichern"},
        {"action": "add_note", "label": "Notiz hinzufügen"},
    ]

    menu_items_json = json.dumps(menu_items)

    html_template = """
    <script>
    (function() {{
        const parentDoc = window.parent?.document;
        if (!parentDoc) {{
            return;
        }}

        const menuItems = __MENU_ITEMS__;
        const styleId = 'custom-context-menu-style';
        const menuId = 'custom-context-menu';

        if (!parentDoc.getElementById(styleId)) {{
            const styleTag = parentDoc.createElement('style');
            styleTag.id = styleId;
            styleTag.innerHTML = `
                .custom-context-menu {{
                    position: absolute;
                    z-index: 99999;
                    min-width: 228px;
                    background: rgba(17, 24, 39, 0.95);
                    backdrop-filter: blur(6px);
                    border-radius: 12px;
                    box-shadow: 0 20px 48px rgba(0, 0, 0, 0.35);
                    padding: 8px 0;
                    color: #f9fafb;
                    font-family: 'Inter', sans-serif;
                    display: none;
                }}
                .custom-context-menu.visible {{
                    display: block;
                    animation: contextMenuFade 120ms ease-out;
                }}
                .custom-context-menu__entry {{
                    position: relative;
                }}
                .custom-context-menu__button {{
                    width: 100%;
                    border: none;
                    background: none;
                    padding: 10px 18px;
                    font-size: 14px;
                    display: flex;
                    gap: 10px;
                    align-items: center;
                    color: inherit;
                    cursor: pointer;
                    transition: background 120ms ease;
                    text-align: left;
                }}
                .custom-context-menu__entry.has-children > .custom-context-menu__button {{
                    padding-right: 32px;
                }}
                .custom-context-menu__entry.has-children > .custom-context-menu__button::after {{
                    content: '›';
                    margin-left: auto;
                    font-size: 12px;
                    opacity: 0.55;
                }}
                .custom-context-menu__button:hover {{
                    background: rgba(59, 130, 246, 0.18);
                }}
                .custom-context-menu__button:active {{
                    background: rgba(59, 130, 246, 0.28);
                }}
                .custom-context-submenu {{
                    position: absolute;
                    top: -8px;
                    left: calc(100% - 6px);
                    min-width: 210px;
                    background: rgba(17, 24, 39, 0.96);
                    border-radius: 12px;
                    box-shadow: 0 18px 48px rgba(0, 0, 0, 0.35);
                    padding: 8px 0;
                    display: none;
                }}
                .custom-context-menu__entry.has-children:hover > .custom-context-submenu,
                .custom-context-menu__entry.has-children:focus-within > .custom-context-submenu {{
                    display: block;
                }}
                .custom-context-submenu .custom-context-menu__entry.has-children > .custom-context-submenu {{
                    left: calc(100% - 4px);
                }}
                @keyframes contextMenuFade {{
                    from {{
                        opacity: 0;
                        transform: translateY(4px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
            `;
            parentDoc.head.appendChild(styleTag);
        }}

        let menu = parentDoc.getElementById(menuId);
        if (!menu) {{
            menu = parentDoc.createElement('div');
            menu.id = menuId;
            menu.className = 'custom-context-menu';
            parentDoc.body.appendChild(menu);
        }}

        const buildMenu = (container, items) => {{
            container.innerHTML = '';
            if (!Array.isArray(items)) {{
                return;
            }}
            items.forEach((item) => {{
                const entry = parentDoc.createElement('div');
                entry.className = 'custom-context-menu__entry';

                const button = parentDoc.createElement('button');
                button.className = 'custom-context-menu__button';
                button.type = 'button';
                button.textContent = item?.label ?? '';

                const actionName = item?.action ?? '';
                if (actionName) {{
                    button.dataset.action = actionName;
                }}

                if (typeof item?.confirm === 'string' && item.confirm.trim().length > 0) {{
                    button.dataset.confirm = item.confirm.trim();
                }}

                const hasChildren = Array.isArray(item?.children) && item.children.length > 0;
                if (hasChildren) {{
                    entry.classList.add('has-children');
                }}

                entry.appendChild(button);

                if (hasChildren) {{
                    const subMenu = parentDoc.createElement('div');
                    subMenu.className = 'custom-context-submenu';
                    buildMenu(subMenu, item.children);
                    entry.appendChild(subMenu);
                }}

                container.appendChild(entry);
            }});
        }};

        buildMenu(menu, menuItems);

        const hideMenu = () => {{
            menu.classList.remove('visible');
        }};

        const clampPosition = (value, max, size) => {{
            return Math.max(8, Math.min(value, max - size - 8));
        }};

        const showMenu = (x, y) => {{
            const docEl = parentDoc.documentElement;
            const win = parentDoc.defaultView || window;
            const scrollX = (win?.scrollX ?? docEl.scrollLeft ?? parentDoc.body.scrollLeft ?? 0);
            const scrollY = (win?.scrollY ?? docEl.scrollTop ?? parentDoc.body.scrollTop ?? 0);
            const maxX = scrollX + docEl.clientWidth;
            const maxY = scrollY + docEl.clientHeight;

            const rect = menu.getBoundingClientRect();
            const width = rect.width || menu.offsetWidth;
            const height = rect.height || menu.offsetHeight;

            const posX = clampPosition(x, maxX, width || 0);
            const posY = clampPosition(y, maxY, height || 0);

            menu.style.left = `${posX}px`;
            menu.style.top = `${posY}px`;
            menu.classList.add('visible');
        }};

        const applyPendingTabNavigation = () => {{
            try {{
                const win = parentDoc.defaultView || window;
                const target = win.sessionStorage?.getItem('contextMenuNavigateTab');
                if (!target) {{
                    return;
                }}

                const labelMap = {{
                    standard: ['PDF-Ausgabe', 'PDF Ausgabe', 'Standard'],
                    preview: ['PDF-Vorschau', 'PDF Vorschau', 'Vorschau'],
                    multi: ['Multi-Firmen-Angebote', 'Multi Firmen Angebote', 'Multi PDF'],
                }};

                const attemptsLimit = 40;
                let attempts = 0;

                const tryActivate = () => {{
                    attempts += 1;
                    const buttons = parentDoc.querySelectorAll('[data-baseweb="tab"]');
                    for (const btn of buttons) {{
                        const text = btn.textContent?.trim() ?? '';
                        if (!text) continue;
                        const candidates = labelMap[target] ?? [];
                        const matches = candidates.some((label) => text.includes(label));
                        if (matches) {{
                            btn.click();
                            win.sessionStorage?.removeItem('contextMenuNavigateTab');
                            return true;
                        }}
                    }}
                    if (attempts >= attemptsLimit) {{
                        win.sessionStorage?.removeItem('contextMenuNavigateTab');
                        return true;
                    }}
                    return false;
                }};

                if (!tryActivate()) {{
                    const timer = setInterval(() => {{
                        if (tryActivate()) {{
                            clearInterval(timer);
                        }}
                    }}, 150);
                }}
            }} catch (err) {{
                console.warn('Context menu tab navigation failed', err);
            }}
        }};

        if (!window.customContextMenuEventsBound) {{
            window.customContextMenuEventsBound = true;

            parentDoc.addEventListener('contextmenu', (event) => {{
                if (event.target?.closest('input, textarea, select, [contenteditable="true"], .custom-context-menu-ignore')) {{
                    return;
                }}
                if (event.ctrlKey || event.metaKey || event.altKey) {{
                    return;
                }}
                event.preventDefault();
                showMenu(event.pageX, event.pageY);
            }}, true);

            parentDoc.addEventListener('click', (event) => {{
                if (!event.target?.closest('#' + menuId)) {{
                    hideMenu();
                }}
            }});

            parentDoc.addEventListener('keydown', (event) => {{
                if (event.key === 'Escape') {{
                    hideMenu();
                }}
            }});

            parentDoc.addEventListener('scroll', hideMenu, true);
            parentDoc.addEventListener('resize', hideMenu, true);

            menu.addEventListener('contextmenu', (event) => event.preventDefault());

            menu.addEventListener('click', (event) => {{
                const button = event.target?.closest('.custom-context-menu__button');
                if (!button) {{
                    return;
                }}
                const action = button.dataset.action ?? '';
                if (!action) {{
                    return;
                }}

                const confirmMessage = button.dataset.confirm;
                if (confirmMessage) {{
                    const win = parentDoc.defaultView || window;
                    if (!win.confirm(confirmMessage)) {{
                        return;
                    }}
                }}

                hideMenu();

                if (action === 'create_screenshot') {{
                    try {{
                        const win = parentDoc.defaultView || window;
                        win.focus();
                        win.print();
                    }} catch (error) {{
                        console.warn('Screenshot trigger failed', error);
                    }}
                }}

                if (['goto_pdf_output_standard', 'goto_pdf_output_multi', 'open_pdf_preview'].includes(action)) {{
                    try {{
                        const win = parentDoc.defaultView || window;
                        const target = action === 'goto_pdf_output_multi' ? 'multi' : (action === 'open_pdf_preview' ? 'preview' : 'standard');
                        win.sessionStorage?.setItem('contextMenuNavigateTab', target);
                    }} catch (error) {{
                        console.warn('Unable to persist tab preference', error);
                    }}
                }}

                const payload = {{ action, nonce: Date.now() }};
                window.parent.postMessage({{
                    isStreamlitMessage: true,
                    type: 'streamlit:setComponentValue',
                    value: payload,
                }}, '*');
            }});
        }}

        applyPendingTabNavigation();
    }})();
    </script>
    """

    html_payload = (
        html_template
        .replace("__MENU_ITEMS__", menu_items_json)
        .replace("{{", "{")
        .replace("}}", "}")
    )

    try:
        return components.html(html_payload, height=0, width=0, key="custom_context_menu")
    except TypeError:
        return components.html(html_payload, height=0, width=0)


def _clear_streamlit_cache() -> bool:
    cleared = False
    try:
        st.cache_data.clear()
        cleared = True
    except Exception:
        pass
    cache_resource = getattr(st, "cache_resource", None)
    if cache_resource is not None and hasattr(cache_resource, "clear"):
        try:
            cache_resource.clear()
            cleared = True
        except Exception:
            pass
    return cleared


def _set_doc_output_target(target: str, message: str) -> None:
    st.session_state.context_menu_doc_output_preferred_tab = target
    st.toast(message)
    already_on_doc = st.session_state.get("selected_page_key_sui") == "doc_output"
    set_current_page("doc_output")
    if already_on_doc:
        request_rerun()


def _reset_calculations() -> None:
    for key in ("calculation_results", "analysis_results", "calculation_results_backup"):
        if key in st.session_state:
            st.session_state[key] = {}
    st.session_state.calculation_results_timestamp = None
    st.toast("Berechnungsdaten zurückgesetzt. Bitte Analyse erneut ausführen.")
    already_on_analysis = st.session_state.get("selected_page_key_sui") == "analysis"
    set_current_page("analysis")
    if already_on_analysis:
        request_rerun()


def _handle_context_menu_save_to_crm() -> None:
    if crm_module is None:
        st.toast("CRM-Modul nicht verfügbar.")
        return

    project_data = st.session_state.get("project_data") or {}
    if not project_data:
        st.toast("Keine Projektdaten vorhanden.")
        return

    customer = project_data.get("customer_data") or {}
    if not customer:
        st.toast("Kundendaten fehlen.")
        return

    get_conn = getattr(crm_module, "get_db_connection_safe_crm", None)
    if not callable(get_conn) and database_module is not None:
        get_conn = getattr(database_module, "get_db_connection", None)
    if not callable(get_conn):
        st.toast("CRM-Datenbank nicht erreichbar.")
        return

    try:
        conn = get_conn()
    except Exception as err:
        st.toast(f"CRM-Verbindung fehlgeschlagen: {err}")
        return

    if not conn:
        st.toast("CRM-Verbindung nicht möglich.")
        return

    project_id = None
    try:
        if hasattr(crm_module, "create_tables_crm"):
            crm_module.create_tables_crm(conn)

        save_customer = getattr(crm_module, "save_customer", None)
        save_project = getattr(crm_module, "save_project", None)
        if not callable(save_customer) or not callable(save_project):
            st.toast("CRM-Speicherfunktionen fehlen.")
            return

        def _clean(value: Any) -> Any:
            return value.strip() if isinstance(value, str) else value

        first_name = (customer.get("first_name") or "").strip()
        last_name = (customer.get("last_name") or "").strip()
        if not first_name:
            first_name = customer.get("company_name") or "Interessent"
        if not last_name:
            last_name = customer.get("company_name") or "Unbekannt"

        customer_payload = {
            'first_name': first_name,
            'last_name': last_name,
            'company_name': _clean(customer.get('company_name')),
            'address': _clean(customer.get('address')),
            'house_number': _clean(customer.get('house_number')),
            'zip_code': _clean(customer.get('zip_code')),
            'city': _clean(customer.get('city')),
            'state': _clean(customer.get('state')),
            'region': _clean(customer.get('region')),
            'email': _clean(customer.get('email')),
            'phone_landline': _clean(customer.get('phone_landline') or customer.get('phone')),
            'phone_mobile': _clean(customer.get('phone_mobile')),
            'income_tax_rate_percent': float(customer.get('income_tax_rate_percent') or 0.0),
            'creation_date': datetime.now().isoformat(),
        }

        customer_id = save_customer(conn, customer_payload)
        if not customer_id:
            st.toast("Kunde konnte nicht gespeichert werden.")
            return

        project_details = project_data.get("project_details") or {}
        consumption_data = project_data.get("consumption_data") or {}

        project_payload = {
            'customer_id': customer_id,
            'project_name': project_details.get('project_name') or f"Projekt {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'project_status': project_details.get('project_status') or 'Angebot',
            'roof_type': project_details.get('roof_type'),
            'roof_covering_type': project_details.get('roof_covering_type'),
            'free_roof_area_sqm': project_details.get('free_roof_area_sqm'),
            'roof_orientation': project_details.get('roof_orientation'),
            'roof_inclination_deg': project_details.get('roof_inclination_deg'),
            'building_height_gt_7m': int(bool(project_details.get('building_height_gt_7m'))),
            'annual_consumption_kwh': project_details.get('annual_consumption_kwh') or consumption_data.get('annual_consumption'),
            'costs_household_euro_mo': project_details.get('costs_household_euro_mo'),
            'annual_heating_kwh': project_details.get('annual_heating_kwh') or consumption_data.get('consumption_heating_kwh_yr'),
            'costs_heating_euro_mo': project_details.get('costs_heating_euro_mo'),
            'anlage_type': project_details.get('anlage_type'),
            'feed_in_type': project_details.get('feed_in_type'),
            'module_quantity': project_details.get('module_quantity'),
            'selected_module_id': project_details.get('selected_module_id'),
            'selected_inverter_id': project_details.get('selected_inverter_id'),
            'include_storage': int(bool(project_details.get('include_storage'))),
            'selected_storage_id': project_details.get('selected_storage_id'),
            'selected_storage_storage_power_kw': project_details.get('selected_storage_storage_power_kw'),
            'include_additional_components': int(bool(project_details.get('include_additional_components'))),
            'visualize_roof_in_pdf': int(bool(project_details.get('visualize_roof_in_pdf'))),
            'latitude': project_details.get('latitude'),
            'longitude': project_details.get('longitude'),
            'creation_date': datetime.now().isoformat(),
        }

        project_id = save_project(conn, project_payload)
    except Exception as err:
        st.toast(f"CRM-Fehler: {err}")
        return
    finally:
        try:
            conn.close()
        except Exception:
            pass

    st.session_state["_last_saved_crm_customer_id"] = customer_id
    if project_id:
        st.session_state["_last_saved_crm_project_id"] = project_id
    st.toast("Projekt im CRM gespeichert.")


def handle_context_menu_action(action: str) -> None:
    if action == "refresh_page":
        st.toast("Aktualisiere Seite …")
        request_rerun()
        return

    if action == "navigate_back":
        history = st.session_state.get("nav_history", [])
        if isinstance(history, list) and len(history) >= 2:
            history.pop()
            target = history[-1]
            st.session_state.nav_history = history
            st.session_state.nav_history_skip_append = True
            st.toast("Zur letzten Ansicht gewechselt.")
            set_current_page(target)
        else:
            st.toast("Keine vorherige Ansicht gespeichert.")
        return

    if action == "clear_cache":
        cleared = _clear_streamlit_cache()
        st.toast("Cache geleert." if cleared else "Keine Cache-Daten zum Löschen gefunden.")
        request_rerun()
        return

    if action == "toggle_debug":
        new_value = not st.session_state.get("context_menu_debug_enabled", False)
        st.session_state.context_menu_debug_enabled = new_value
        st.toast("Debug-Modus aktiviert." if new_value else "Debug-Modus deaktiviert.")
        return

    if action == "create_screenshot":
        st.toast("Öffne Druckdialog für Screenshot …")
        return

    if action == "switch_company":
        active_id = st.session_state.get("active_company_id")
        if active_id is None and database_module is not None and callable(getattr(database_module, "load_admin_setting", None)):
            try:
                loaded = database_module.load_admin_setting("active_company_id", None)
                if loaded not in (None, ""):
                    active_id = int(loaded)
            except Exception:
                active_id = None
        st.session_state.context_menu_company_selection = active_id
        st.session_state.context_menu_company_switch_open = True
        request_rerun()
        return

    if action == "goto_pdf_output_standard":
        _set_doc_output_target("standard", "Zur PDF-Ausgabe (Standard) gewechselt.")
        return

    if action == "goto_pdf_output_multi":
        _set_doc_output_target("multi", "Zur PDF-Ausgabe (Multi) gewechselt.")
        return

    if action == "open_pdf_preview":
        _set_doc_output_target("preview", "Zur PDF-Vorschau gewechselt.")
        return

    if action == "restart_calculations":
        _reset_calculations()
        return

    if action == "save_to_crm":
        _handle_context_menu_save_to_crm()
        return

    if action == "add_note":
        st.session_state.context_menu_note_modal_open = True
        request_rerun()
        return

    st.toast(f"Unbekannte Aktion: {action}")

def main():
    global TEXTS # Erlaube Modifikation der globalen TEXTS Variable

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

    if locales_module and callable(getattr(locales_module, 'load_translations', None)):
        try:
            loaded_translations = locales_module.load_translations('de')
        except Exception as e_load_loc:
            if 'import_errors' in globals() and isinstance(globals()['import_errors'], list):
                globals()['import_errors'].append(f"Fehler beim Laden der Übersetzungen: {e_load_loc}")
            loaded_translations = None

    if isinstance(loaded_translations, dict) and loaded_translations:
        TEXTS = loaded_translations
    else:
        if loaded_translations is not None:
            if 'import_errors' in globals() and isinstance(globals()['import_errors'], list):
                globals()['import_errors'].append(f"WARNUNG: Übersetzungsdaten sind kein gültiges Dictionary {type(loaded_translations)}). Verwende Fallback-Texte.")

        if isinstance(_texts_initial, dict):
            TEXTS = _texts_initial.copy()
        else:
            TEXTS = {"app_title": "Solar App (Kritischer Text-Fallback)"}
            if 'import_errors' in globals() and isinstance(globals()['import_errors'], list):
                globals()['import_errors'].append("KRITISCH: ist kein Dictionary! Minimale Fallback-Texte verwendet.")

    _apply_active_app_theme(inject_css=False)
    theme_payload = getattr(theme_manager, "streamlit_theme", None)
    try:
        if isinstance(theme_payload, dict) and theme_payload:
            st.set_page_config(page_title=get_text_gui("app_title"), layout="wide", theme=theme_payload)
        else:
            st.set_page_config(page_title=get_text_gui("app_title"), layout="wide")
    except TypeError:
        try:
            streamlit_theme_config = st.get_option("theme") or {}
        except RuntimeError:
            # Older Streamlit builds do not expose the "theme" config option
            streamlit_theme_config = {}
        except Exception:
            streamlit_theme_config = {}

        updated_theme: Dict[str, Any] = {}
        if isinstance(streamlit_theme_config, dict):
            updated_theme.update(streamlit_theme_config)

        if isinstance(theme_payload, dict) and theme_payload:
            updated_theme.update(theme_payload)
            if updated_theme:
                try:
                    st._config.set_option("theme", updated_theme)
                except Exception:
                    pass

        st.set_page_config(page_title=get_text_gui("app_title"), layout="wide")
    _apply_active_app_theme()

    # ============================================================================
    # DYNAMISCHE GLOBALE UI-EFFEKTE (10 verschiedene Stile zur Auswahl)
    # ============================================================================
    # Lade UI-Effekt-Einstellungen
    try:
        from admin_ui_effects_settings import load_ui_effects_settings
        from ui_effects_library import get_effect_css
        
        ui_effects_settings = load_ui_effects_settings()
        effects_enabled = ui_effects_settings.get("enabled", True)
        active_effect = ui_effects_settings.get("active_effect", "shimmer_pulse")
        
        if effects_enabled:
            effect_css = get_effect_css(active_effect)
            st.markdown(f"""
            <style>
            /* ========== DYNAMISCHE UI-EFFEKTE: {active_effect.upper()} ========== */
            {effect_css}
            </style>
            """, unsafe_allow_html=True)
        else:
            # Effekte deaktiviert - kein CSS laden
            pass
    except Exception as e:
        # Fallback auf Standard-Effekt bei Fehler
        from ui_effects_library import get_effect_css
        fallback_css = get_effect_css("shimmer_pulse")
        st.markdown(f"""
        <style>
        /* ========== GLOBALE BUTTON-EFFEKTE (FALLBACK) ========== */
        {fallback_css}
        </style>
        """, unsafe_allow_html=True)

    # ============================================================================
    # ZUSÄTZLICHE GLOBALE EFFEKTE: SLIDER & CHECKBOXEN
    # ========================================================================
    st.markdown("""
    <style>
    /* ========== GLOBALE SLIDER-EFFEKTE (+ / - BUTTONS) ========== */
    /* Shimmer- und Pulse-Animationen für Slider-Increment/Decrement-Buttons */
    
    /* Slider Plus/Minus Buttons */
    button[data-testid="stNumberInputStepUp"],
    button[data-testid="stNumberInputStepDown"],
    div[data-testid="stNumberInput"] button,
    .step-up,
    .step-down {
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }
    
    /* Shimmer-Effekt für Slider-Buttons */
    button[data-testid="stNumberInputStepUp"]::before,
    button[data-testid="stNumberInputStepDown"]::before,
    div[data-testid="stNumberInput"] button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.25), transparent) !important;
        transition: left 0.4s ease !important;
        pointer-events: none !important;
        z-index: 1 !important;
    }
    
    /* Shimmer aktivieren beim Hover */
    button[data-testid="stNumberInputStepUp"]:hover::before,
    button[data-testid="stNumberInputStepDown"]:hover::before,
    div[data-testid="stNumberInput"] button:hover::before {
        left: 100% !important;
    }
    
    /* Hover-Effekte für Slider-Buttons */
    button[data-testid="stNumberInputStepUp"]:hover,
    button[data-testid="stNumberInputStepDown"]:hover,
    div[data-testid="stNumberInput"] button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(102, 126, 234, 0.08) 100%) !important;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.2) !important;
        transform: scale(1.05) !important;
        animation: sliderButtonPulse 1.5s ease-in-out infinite !important;
    }
    
    @keyframes sliderButtonPulse {
        0%, 100% {
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.2);
            transform: scale(1.05);
        }
        50% {
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            transform: scale(1.08);
        }
    }
    
    /* Active State (beim Klicken) */
    button[data-testid="stNumberInputStepUp"]:active,
    button[data-testid="stNumberInputStepDown"]:active,
    div[data-testid="stNumberInput"] button:active {
        transform: scale(0.95) !important;
        box-shadow: 0 1px 5px rgba(102, 126, 234, 0.3) inset !important;
    }
    
    /* Slider Track Hover */
    div[data-testid="stSlider"] div[role="slider"]:hover {
        box-shadow: 0 0 0 8px rgba(102, 126, 234, 0.15) !important;
        transform: scale(1.1) !important;
        transition: all 0.3s ease !important;
    }
    
    /* ========== ENDE GLOBALE SLIDER-EFFEKTE ========== */
    
    /* ========== GLOBALE CHECKBOX-EFFEKTE ========== */
    /* Shimmer- und Pulse-Animationen für Checkboxen */
    
    /* Checkbox Container */
    div[data-testid="stCheckbox"],
    .stCheckbox,
    label[data-testid="stCheckbox"] {
        position: relative !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* Checkbox Label Hover-Effekt */
    div[data-testid="stCheckbox"]:hover,
    .stCheckbox:hover,
    label[data-testid="stCheckbox"]:hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%) !important;
        padding-left: 8px !important;
        border-radius: 6px !important;
        transform: translateX(3px) !important;
    }
    
    /* Checkbox Input Box */
    div[data-testid="stCheckbox"] input[type="checkbox"],
    .stCheckbox input[type="checkbox"],
    input[type="checkbox"] {
        position: relative !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* Checkbox Hover-Effekt - Shimmer */
    div[data-testid="stCheckbox"]:hover input[type="checkbox"],
    .stCheckbox:hover input[type="checkbox"] {
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15) !important;
        border-color: rgba(102, 126, 234, 0.6) !important;
        animation: checkboxPulse 1.5s ease-in-out infinite !important;
    }
    
    @keyframes checkboxPulse {
        0%, 100% {
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
            transform: scale(1);
        }
        50% {
            box-shadow: 0 0 0 6px rgba(102, 126, 234, 0.25);
            transform: scale(1.05);
        }
    }
    
    /* Checked Checkbox - Pulse-Effekt */
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked,
    .stCheckbox input[type="checkbox"]:checked,
    input[type="checkbox"]:checked {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(102, 126, 234, 0.7) 100%) !important;
        border-color: rgba(102, 126, 234, 1) !important;
        animation: checkboxCheckedPulse 2s ease-in-out infinite !important;
    }
    
    @keyframes checkboxCheckedPulse {
        0%, 100% {
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }
        50% {
            box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.3);
        }
    }
    
    /* Checkbox Checkmark - Shimmer-Effekt */
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked::after,
    .stCheckbox input[type="checkbox"]:checked::after {
        animation: checkmarkShimmer 2s ease-in-out infinite !important;
    }
    
    @keyframes checkmarkShimmer {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
            filter: brightness(1.2);
        }
    }
    
    /* Radio Buttons - Ähnliche Effekte */
    div[data-testid="stRadio"] label:hover,
    .stRadio label:hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%) !important;
        padding-left: 8px !important;
        border-radius: 6px !important;
        transform: translateX(3px) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stRadio"] input[type="radio"]:hover,
    .stRadio input[type="radio"]:hover {
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15) !important;
        animation: checkboxPulse 1.5s ease-in-out infinite !important;
    }
    
    /* ========== ENDE GLOBALE CHECKBOX-EFFEKTE ========== */
    
    </style>
    """, unsafe_allow_html=True)

    # INTRO-BILDSCHIRM (VOR DER HAUPTANWENDUNG)
    # ============================================================================
    # Prüfe ob Intro-Bildschirm angezeigt werden soll
    if 'intro_completed' not in st.session_state:
        try:
            from intro_screen import render_intro_screen
            render_intro_screen()
            # Wenn render_intro_screen() False zurückgibt, stoppe hier
            # Die Funktion selbst managed den st.rerun() nach Button-Klick
            st.stop()
        except ImportError:
            # Wenn intro_screen.py nicht verfügbar, überspringe Intro
            st.session_state['intro_completed'] = True
            st.session_state['user_mode'] = 'quick_start'
            st.session_state['username'] = 'Benutzer'
        except Exception as e:
            st.warning(f"Intro-Bildschirm konnte nicht geladen werden: {e}")
            st.session_state['intro_completed'] = True
            st.session_state['user_mode'] = 'quick_start'
            st.session_state['username'] = 'Benutzer'

    # ============================================================================
    # ROBUSTE SESSION STATE INITIALISIERUNG
    # ============================================================================
    # Verwende eine Guard-Variable um sicherzustellen, dass kritische Initialisierungen
    # nur EINMAL pro Session passieren und nicht bei jedem Rerun überschrieben werden
    
    if '_session_initialized' not in st.session_state:
        st.session_state._session_initialized = True
        
        # Projekt-Daten initialisieren
        if 'project_data' not in st.session_state:
            st.session_state.project_data = {
                'customer_data': {}, 
                'project_details': {}, 
                'economic_data': {}
            }
        
        # Berechnungs-Ergebnisse initialisieren
        if 'calculation_results' not in st.session_state:
            st.session_state.calculation_results = {}
        
        if 'calculation_results_timestamp' not in st.session_state:
            st.session_state.calculation_results_timestamp = None
        
        if 'calculation_results_backup' not in st.session_state:
            st.session_state.calculation_results_backup = {}
        
        # Navigation-Stabilität: Lock aktiviert standardmäßig
        if 'nav_lock_enabled' not in st.session_state:
            st.session_state.nav_lock_enabled = True
        
        if 'nav_event' not in st.session_state:
            st.session_state.nav_event = False
        
        # Context Menu States
        if 'context_menu_company_switch_open' not in st.session_state:
            st.session_state.context_menu_company_switch_open = False
        
        if 'context_menu_company_selection' not in st.session_state:
            st.session_state.context_menu_company_selection = None
        
        if 'context_menu_note_modal_open' not in st.session_state:
            st.session_state.context_menu_note_modal_open = False
        
        if 'context_menu_note_input' not in st.session_state:
            st.session_state.context_menu_note_input = ""
        
        if 'context_notes' not in st.session_state:
            st.session_state.context_notes = []
        
        if 'context_menu_debug_enabled' not in st.session_state:
            st.session_state.context_menu_debug_enabled = False
        
        # Navigation History
        if 'nav_history' not in st.session_state:
            st.session_state.nav_history = []
        
        if 'nav_history_skip_append' not in st.session_state:
            st.session_state.nav_history_skip_append = False
    
    # Prüfe ob kritische States noch existieren (können durch Cleanup gelöscht werden)
    if 'project_data' not in st.session_state:
        st.session_state.project_data = {'customer_data': {}, 'project_details': {}, 'economic_data': {}}
    if 'calculation_results' not in st.session_state:
        st.session_state.calculation_results = {}
    
    # Stelle sicher dass Lists auch wirklich Lists sind (nicht None oder andere Typen)
    if not isinstance(st.session_state.get('context_notes'), list):
        st.session_state.context_notes = []
    if not isinstance(st.session_state.get('nav_history'), list):
        st.session_state.nav_history = []

    # Context Menu (Rechtsklick)
    menu_event = inject_custom_context_menu(st.session_state.get('nav_lock_enabled', True))
    if isinstance(menu_event, dict):
        nonce = menu_event.get('nonce')
        action = menu_event.get('action')
        last_nonce = st.session_state.get('_context_menu_last_nonce')
        if nonce is not None and nonce != last_nonce:
            st.session_state._context_menu_last_nonce = nonce
            if isinstance(action, str) and action:
                handle_context_menu_action(action)
    
    # Ausfahrbarer Drawer - unten rechts
    drawer_action = components.html("""
    <script>
    (function() {
        const parentDoc = window.parent?.document;
        if (!parentDoc) return;
        
        // Entferne alte Elemente
        const oldBtn = parentDoc.getElementById('drawer-btn');
        const oldDrawer = parentDoc.getElementById('drawer-panel');
        if (oldBtn) oldBtn.remove();
        if (oldDrawer) oldDrawer.remove();
        
        // Style hinzufügen
        if (!parentDoc.getElementById('drawer-style')) {
            const style = parentDoc.createElement('style');
            style.id = 'drawer-style';
            style.innerHTML = `
                .drawer-button {
                    position: fixed !important;
                    bottom: 25px !important;
                    right: 25px !important;
                    z-index: 999998 !important;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 50% !important;
                    width: 65px !important;
                    height: 65px !important;
                    font-size: 28px !important;
                    cursor: pointer !important;
                    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
                    transition: all 0.3s ease !important;
                }
                .drawer-button:hover {
                    transform: scale(1.1) !important;
                    box-shadow: 0 8px 35px rgba(102, 126, 234, 0.7) !important;
                }
                .drawer-panel {
                    position: fixed !important;
                    bottom: 0 !important;
                    right: -350px !important;
                    width: 350px !important;
                    height: 500px !important;
                    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
                    box-shadow: -5px 0 30px rgba(0,0,0,0.5) !important;
                    z-index: 999999 !important;
                    transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    border-radius: 20px 0 0 20px !important;
                    padding: 25px !important;
                    overflow-y: auto !important;
                }
                .drawer-panel.open {
                    right: 0 !important;
                }
                .drawer-close {
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    background: rgba(255,255,255,0.1);
                    border: none;
                    color: white;
                    font-size: 24px;
                    width: 35px;
                    height: 35px;
                    border-radius: 50%;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                .drawer-close:hover {
                    background: rgba(255,255,255,0.2);
                    transform: rotate(90deg);
                }
                .drawer-title {
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    padding-top: 10px;
                }
                .drawer-btn {
                    width: 100%;
                    padding: 15px;
                    margin: 10px 0;
                    background: rgba(102, 126, 234, 0.2);
                    border: 1px solid rgba(102, 126, 234, 0.4);
                    border-radius: 10px;
                    color: white;
                    font-size: 16px;
                    cursor: pointer;
                    transition: all 0.3s;
                    text-align: left;
                }
                .drawer-btn:hover {
                    background: rgba(102, 126, 234, 0.4);
                    transform: translateX(-5px);
                }
            `;
            parentDoc.head.appendChild(style);
        }
        
        // Drawer Panel erstellen
        const drawer = parentDoc.createElement('div');
        drawer.id = 'drawer-panel';
        drawer.className = 'drawer-panel';
        drawer.innerHTML = `
            <button class="drawer-close">×</button>
            <div class="drawer-title">Quick Actions</div>
            <button class="drawer-btn" data-action="action1">📊 Button 1</button>
            <button class="drawer-btn" data-action="action2">🔧 Button 2</button>
            <button class="drawer-btn" data-action="action3">⚙️ Button 3</button>
            <button class="drawer-btn" data-action="action4">📈 Button 4</button>
            <button class="drawer-btn" data-action="action5">🎯 Button 5</button>
            <button class="drawer-btn" data-action="logout" style="background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.4);">🚪 Abmelden</button>
        `;
        parentDoc.body.appendChild(drawer);
        
        // Event Listeners für Drawer Buttons
        drawer.querySelectorAll('.drawer-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                const action = this.getAttribute('data-action');
                console.log('Drawer action:', action);
                
                if (action === 'logout') {
                    // Trigger Streamlit Logout via setComponentValue
                    console.log('Triggering logout...');
                    
                    // Sende Logout-Signal zurück an Streamlit
                    if (window.Streamlit) {
                        window.Streamlit.setComponentValue('logout');
                    }
                    
                    // Schließe Drawer
                    drawer.classList.remove('open');
                }
            });
        });
        
        // Toggle Button erstellen
        const btn = parentDoc.createElement('button');
        btn.id = 'drawer-btn';
        btn.className = 'drawer-button';
        btn.innerHTML = '☰';
        btn.title = 'Quick Actions';
        
        btn.onclick = function() {
            drawer.classList.toggle('open');
        };
        
        // Close button
        drawer.querySelector('.drawer-close').onclick = function() {
            drawer.classList.remove('open');
        };
        
        parentDoc.body.appendChild(btn);
    })();
    </script>
    """, height=0, width=0)
    
    # Logout-Handler: Wenn Drawer "logout" zurückgibt
    if drawer_action == 'logout':
        from user_menu import logout_user
        logout_user()
        st.rerun()



    # Sidebar-Styling - Moderne Navigation im Behance-Stil
    st.markdown("""
    <style>
    /* Sidebar mit dunklem Gradient */
    section[data-testid="stSidebar"] {
        min-width: 300px !important;
        background: linear-gradient(180deg, #1a1f35 0%, #0f1419 100%) !important;
    }
    
    /* Moderne Button-Styles im Behance-Stil mit Shimmer-Effekt */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left !important;
        padding: 14px 16px !important;
        margin: 4px 0 !important;
        background: rgba(102, 126, 234, 0.08) !important;
        border: none !important;
        border-left: 3px solid transparent !important;
        border-radius: 0 10px 10px 0 !important;
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: none !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    /* Shimmer-Effekt (Lichtstrahl) */
    section[data-testid="stSidebar"] .stButton > button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent) !important;
        transition: left 0.5s !important;
    }
    
    /* Hover-Effekt mit Shimmer */
    section[data-testid="stSidebar"] .stButton > button:hover::before {
        left: 100% !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(102, 126, 234, 0.15) !important;
        border-left-color: #667eea !important;
        color: white !important;
        transform: translateX(5px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Aktiver Button (Primary) mit Pulse-Animation */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"],
    section[data-testid="stSidebar"] .stButton > button[data-baseweb="button"][class*="primary"] {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.25) 0%, rgba(102, 126, 234, 0.1) 100%) !important;
        border-left-color: #667eea !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Pulse-Animation für aktiven Button */
    @keyframes sidebarButtonPulse {
        0%, 100% { transform: translateX(0) scale(1); }
        50% { transform: translateX(2px) scale(1.02); }
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
    section[data-testid="stSidebar"] .stButton > button[data-baseweb="button"][class*="primary"]:hover {
        animation: sidebarButtonPulse 2s ease-in-out infinite !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Section Titles */
    section[data-testid="stSidebar"] div[style*="text-transform: uppercase"] {
        margin-top: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Benutzermenü GANZ OBEN - ÜBER dem ersten Strich
        try:
            from user_menu import render_user_menu
            render_user_menu()
        except Exception as e:
            # Fallback auf altes System
            try:
                from intro_screen import show_user_info
                show_user_info()
            except:
                pass
        
        st.markdown("---")
        
        # === MODERNE SIDEBAR NAVIGATION (BEHANCE-STIL) ===
        
        # Initialisierung
        if 'active_page' not in st.session_state:
            st.session_state.active_page = 'input'
        
        # Hauptmenü Sektion
        st.markdown('<div style="color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; padding: 20px 0 8px 0; margin-top: 10px;">HAUPTMENÜ</div>', unsafe_allow_html=True)
        
        main_menu = [
            {"icon": "📊", "label": get_text_gui("menu_item_input"), "key": "input"},
            {"icon": "☀️", "label": TEXTS.get("menu_item_solar_calculator", "Solar Calculator"), "key": "solar_calculator"},
            {"icon": "🔥", "label": get_text_gui("menu_item_heatpump"), "key": "heatpump"},
            {"icon": "💰", "label": get_text_gui("menu_item_analysis"), "key": "analysis"},
        ]
        
        for item in main_menu:
            is_active = st.session_state.active_page == item['key']
            button_type = "primary" if is_active else "secondary"
            
            # Button direkt - kein HTML
            if st.button(f"{item['icon']}  {item['label']}", key=f"nav_btn_{item['key']}", use_container_width=True, type=button_type):
                st.session_state.active_page = item['key']
                st.session_state.selected_page_key_sui = item['key']
                st.session_state.nav_event = True
                st.rerun()
        
        st.markdown("---")
        
        # Business Sektion
        st.markdown('<div style="color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; padding: 20px 0 8px 0;">BUSINESS</div>', unsafe_allow_html=True)
        
        business_menu = [
            {"icon": "👥", "label": get_text_gui("menu_item_crm"), "key": "crm"},
            {"icon": "📄", "label": get_text_gui("menu_item_doc_output"), "key": "doc_output"},
            {"icon": "⚙️", "label": get_text_gui("menu_item_admin"), "key": "admin"},
        ]
        
        for item in business_menu:
            is_active = st.session_state.active_page == item['key']
            button_type = "primary" if is_active else "secondary"
            
            if st.button(f"{item['icon']}  {item['label']}", key=f"nav_btn_{item['key']}", use_container_width=True, type=button_type):
                st.session_state.active_page = item['key']
                st.session_state.selected_page_key_sui = item['key']
                st.session_state.nav_event = True
                st.rerun()
        
        st.markdown("---")
        
        # Tools Sektion
        st.markdown('<div style="color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; padding: 20px 0 8px 0;">TOOLS</div>', unsafe_allow_html=True)
        
        tools_menu = [
            {"icon": "⚡", "label": get_text_gui("menu_item_quick_calc"), "key": "quick_calc"},
            {"icon": "🔧", "label": get_text_gui("menu_item_options"), "key": "options"},
            {"icon": "ℹ️", "label": get_text_gui("menu_item_info_platform"), "key": "info_platform"},
        ]
        
        for item in tools_menu:
            is_active = st.session_state.active_page == item['key']
            button_type = "primary" if is_active else "secondary"
            
            if st.button(f"{item['icon']}  {item['label']}", key=f"nav_btn_{item['key']}", use_container_width=True, type=button_type):
                st.session_state.active_page = item['key']
                st.session_state.selected_page_key_sui = item['key']
                st.session_state.nav_event = True
                st.rerun()
        
        # Setze selected_page_key für Kompatibilität
        selected_page_key = st.session_state.active_page
        
        # === ENDE MODERNE NAVIGATION ===
        if st.session_state.get('nav_lock_enabled', True):
            # Halte einen Verlauf der zuletzt gerenderten Seite (kann für Debug/weitere Heuristiken genutzt werden)
            if 'last_rendered_page_key' not in st.session_state:
                st.session_state.last_rendered_page_key = selected_page_key

            prev_key = st.session_state.get('selected_page_key_prev', selected_page_key)

            if st.session_state.get('nav_event', False):
                # Echte Nutzer-Navigation: übernehmen und als stabil markieren
                st.session_state.nav_event = False
                st.session_state.selected_page_key_prev = selected_page_key
            else:
                # Kein explizites Navigationsevent: aktuelle Auswahl akzeptieren und als stabil betrachten,
                # um unerwünschtes "Zurückspringen" zu vermeiden (z.B. nach Button-Klicks innerhalb einer Seite).
                if selected_page_key != prev_key:
                    st.session_state.selected_page_key_prev = selected_page_key

            # Merke die zuletzt gerenderte Seite
            st.session_state.last_rendered_page_key = selected_page_key

        if st.session_state.get('context_menu_company_switch_open'):
            st.markdown("---")
            st.subheader("Unternehmen wechseln")
            companies: list[dict[str, Any]] = []
            if database_module and callable(getattr(database_module, 'list_companies', None)):
                try:
                    companies = database_module.list_companies()
                except Exception as err:
                    st.warning(f"Fehler beim Laden der Unternehmen: {err}")
            ids: list[int | None] = [None]
            labels: list[str] = ["Bitte wählen"]
            name_lookup: dict[int | None, str] = {None: "Bitte wählen"}
            for comp in companies:
                comp_id = comp.get('id')
                if comp_id is None:
                    continue
                try:
                    comp_id_int = int(comp_id)
                except Exception:
                    continue
                title = (comp.get('name') or '').strip() or f"Firma #{comp_id_int}"
                ids.append(comp_id_int)
                labels.append(f"{title} (ID {comp_id_int})")
                name_lookup[comp_id_int] = title

            active_company_id_val = st.session_state.get('active_company_id')
            if active_company_id_val is not None and active_company_id_val not in name_lookup and database_module and callable(getattr(database_module, 'get_company', None)):
                try:
                    active_company = database_module.get_company(active_company_id_val)
                    if active_company and active_company.get('name'):
                        name_lookup[active_company_id_val] = active_company['name']
                except Exception:
                    pass

            current_selection = st.session_state.get('context_menu_company_selection')
            if current_selection not in ids:
                current_selection = None
                st.session_state.context_menu_company_selection = None

            can_select_company = len(ids) > 1
            if can_select_company:
                try:
                    current_index = ids.index(current_selection)
                except ValueError:
                    current_index = 0
                selected_index = st.selectbox(
                    "Firma auswählen",
                    options=list(range(len(labels))),
                    index=current_index if 0 <= current_index < len(labels) else 0,
                    format_func=lambda idx: labels[idx] if 0 <= idx < len(labels) else labels[0],
                    key="context_menu_company_select_index",
                )
                st.session_state.context_menu_company_selection = ids[selected_index]
            else:
                st.info("Keine Unternehmen gefunden. Bitte im Admin-Bereich anlegen.")

            if active_company_id_val is not None:
                st.caption(f"Aktuell aktiv: {name_lookup.get(active_company_id_val, f'ID {active_company_id_val}')}")

            apply_col, cancel_col = st.columns(2)
            if apply_col.button("Übernehmen", key="context_menu_company_apply", disabled=not can_select_company):
                selected_id = st.session_state.get('context_menu_company_selection')
                if selected_id is None:
                    st.warning("Bitte zuerst eine Firma auswählen.")
                else:
                    try:
                        if database_module and callable(getattr(database_module, "save_admin_setting", None)):
                            database_module.save_admin_setting('active_company_id', selected_id)
                        st.session_state.active_company_id = selected_id
                        st.session_state.context_menu_company_switch_open = False
                        st.toast(f"Aktives Unternehmen: {name_lookup.get(selected_id, f'ID {selected_id}')}")
                        request_rerun()
                    except Exception as err:
                        st.error(f"Unternehmen konnte nicht gesetzt werden: {err}")
            if cancel_col.button("Abbrechen", key="context_menu_company_cancel"):
                st.session_state.context_menu_company_switch_open = False
                request_rerun()

        if st.session_state.get('context_menu_note_modal_open'):
            st.markdown("---")
            st.subheader("Notiz hinzufügen")
            note_text = st.text_area("Notiz", key="context_menu_note_input", height=140)
            save_col, cancel_col = st.columns(2)
            if save_col.button("Speichern", key="context_menu_note_save", disabled=not bool(note_text.strip())):
                cleaned = note_text.strip()
                if cleaned:
                    notes = st.session_state.get('context_notes', [])
                    notes.append({
                        "text": cleaned,
                        "created_at": datetime.now().isoformat(),
                    })
                    if len(notes) > 100:
                        notes = notes[-100:]
                    st.session_state.context_notes = notes
                    st.session_state.context_menu_note_modal_open = False
                    st.session_state.context_menu_note_input = ""
                    st.toast("Notiz gespeichert.")
                    request_rerun()
            if cancel_col.button("Abbrechen", key="context_menu_note_cancel"):
                st.session_state.context_menu_note_modal_open = False
                st.session_state.context_menu_note_input = ""
                request_rerun()

        if st.session_state.get('context_notes'):
            with st.expander("Gespeicherte Notizen", expanded=False):
                for idx, note in enumerate(reversed(st.session_state.context_notes[-5:])):
                    if idx:
                        st.divider()
                    timestamp = (note.get('created_at') or '').replace('T', ' ')[:19]
                    if timestamp:
                        st.caption(timestamp)
                    st.write(note.get('text', ''))

        if st.session_state.get('context_menu_debug_enabled'):
            st.markdown("---")
            st.caption("Debug-Informationen")
            debug_payload = {
                "current_page": st.session_state.get("selected_page_key_sui"),
                "nav_history": st.session_state.get("nav_history", [])[-10:],
                "active_company_id": st.session_state.get("active_company_id"),
                "preferred_doc_tab": st.session_state.get("context_menu_doc_output_preferred_tab"),
            }
            st.json(debug_payload)

    drawer_position = st.session_state.get("app_drawer_position")
    query_params: Dict[str, Any] = {}
    if drawer_position is None:
        if hasattr(st, "query_params"):
            query_params = dict(getattr(st, "query_params"))  # type: ignore[assignment]
        else:
            try:
                query_params = dict(st.experimental_get_query_params())  # type: ignore[attr-defined]
            except Exception:
                query_params = {}
        candidate = query_params.get("drawer") or query_params.get("drawer_pos")
        if isinstance(candidate, list):
            candidate = candidate[0] if candidate else None
        drawer_position = str(candidate).lower() if candidate else "left"
    if not isinstance(drawer_position, str):
        drawer_position = "left"
    drawer_position = drawer_position.lower()
    if drawer_position not in {"right", "left"}:
        drawer_position = "left"
    st.session_state["app_drawer_position"] = drawer_position

    drawer_classes = f"app-drawer app-drawer--collapsed app-drawer--align-{drawer_position}"
    initial_icon = "&rsaquo;" if drawer_position == "left" else "&lsaquo;"

    st.markdown(
        """
        <style>
        #app-main-drawer {
            position: fixed;
            bottom: 1.5rem;
            left: 0;
            display: flex;
            gap: 0;
            align-items: stretch;
            z-index: 9999;
        }
        #app-main-drawer.app-drawer--align-left {
            flex-direction: row;
        }
        #app-main-drawer.app-drawer--align-right {
            flex-direction: row-reverse;
            left: auto;
            right: 0;
        }
        #app-main-drawer.app-drawer--anchored {
            position: fixed;
        }
        #app-main-drawer .app-drawer__handle {
            pointer-events: auto;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.45rem;
            padding: 0.85rem 0.9rem;
            border-radius: 0 18px 18px 0;
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-right: none;
            background: rgba(15, 23, 42, 0.82);
            backdrop-filter: blur(16px);
            color: #f8fafc;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.68rem;
            font-weight: 600;
            box-shadow: 0 18px 32px rgba(15, 23, 42, 0.28);
        }
        #app-main-drawer.app-drawer--align-right .app-drawer__handle {
            border-left: none;
            border-right: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 18px 0 0 18px;
        }
        #app-main-drawer .app-drawer__panel {
            width: min(420px, 86vw);
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(28px);
            border-radius: 0 24px 24px 0;
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-left: none;
            box-shadow: 0 18px 32px rgba(15, 23, 42, 0.28);
            transform: translateX(100%);
            opacity: 0;
            pointer-events: none;
            transition: transform 0.32s ease, opacity 0.26s ease;
            overflow: hidden;
        }
        #app-main-drawer.app-drawer--align-right .app-drawer__panel {
            border-right: none;
            border-left: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 24px 0 0 24px;
            transform: translateX(-100%);
        }
        #app-main-drawer.app-drawer--expanded .app-drawer__panel {
            transform: translateX(0);
            opacity: 1;
            pointer-events: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="{drawer_classes}" id="app-main-drawer" data-position="{drawer_position}">
            <button type="button" class="app-drawer__handle" id="app-main-drawer-handle" aria-expanded="false" aria-controls="app-main-drawer-panel" title="Drawer öffnen">
                <span class="app-drawer__handle-icon" aria-hidden="true">{initial_icon}</span>
                <span class="app-drawer__handle-text">Drawer</span>
            </button>
            <aside class="app-drawer__panel" id="app-main-drawer-panel" aria-hidden="true">
                <header class="app-drawer__panel-header">
                    <span class="app-drawer__panel-title">Drawer</span>
                    <button type="button" class="app-drawer__close" id="app-main-drawer-close" aria-label="Drawer schließen">&times;</button>
                </header>
                <div class="app-drawer__panel-content">
                    <div class="app-drawer__placeholder">Noch keine Inhalte</div>
                </div>
            </aside>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <script>
        (function() {
            const doc = document;
            const drawer = doc.getElementById('app-main-drawer');
            const handle = doc.getElementById('app-main-drawer-handle');
            const closeButton = doc.getElementById('app-main-drawer-close');
            const panel = doc.getElementById('app-main-drawer-panel');
            if (!drawer || !handle || !panel) { return; }
            if (drawer.dataset.bound === 'true') { return; }

            const position = drawer.dataset.position || 'right';

            const alignToSidebar = () => {
                const sidebarSection = doc.querySelector('section[data-testid="stSidebar"]') || doc.querySelector('div[data-testid="stSidebar"]');
                if (!sidebarSection) {
                    if (position === 'left') {
                        drawer.style.left = '0';
                        drawer.style.right = '';
                    } else {
                        drawer.style.right = '0';
                        drawer.style.left = '';
                    }
                    drawer.style.bottom = '1.5rem';
                    return;
                }
                const rect = sidebarSection.getBoundingClientRect();
                if (position === 'left') {
                    drawer.style.left = `${Math.round(rect.right)}px`;
                    drawer.style.right = '';
                } else {
                    const rightOffset = Math.round(window.innerWidth - rect.left);
                    drawer.style.right = `${rightOffset}px`;
                    drawer.style.left = '';
                }
                drawer.style.bottom = '1.5rem';
            };

            if (window.__appDrawerResizeHandler) {
                window.removeEventListener('resize', window.__appDrawerResizeHandler);
            }
            window.__appDrawerResizeHandler = alignToSidebar;
            window.addEventListener('resize', alignToSidebar);

            if (window.__appDrawerMutationObserver) {
                window.__appDrawerMutationObserver.disconnect();
            }
            window.__appDrawerMutationObserver = new MutationObserver((mutations) => {
                for (const mutation of mutations) {
                    if (mutation.type === 'childList') {
                        alignToSidebar();
                        break;
                    }
                }
            });
            window.__appDrawerMutationObserver.observe(doc.body, { childList: true, subtree: true });

            requestAnimationFrame(alignToSidebar);

            let expanded = false;

            const updateState = (nextState) => {
                expanded = nextState;
                drawer.classList.toggle('app-drawer--expanded', expanded);
                drawer.classList.toggle('app-drawer--collapsed', !expanded);
                panel.setAttribute('aria-hidden', expanded ? 'false' : 'true');
                handle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
                const icon = handle.querySelector('.app-drawer__handle-icon');
                if (icon) {
                    if (position === 'left') {
                        icon.textContent = expanded ? '\\u2039' : '\\u203A';
                    } else {
                        icon.textContent = expanded ? '\\u203A' : '\\u2039';
                    }
                }
            };

            const toggleDrawer = () => updateState(!expanded);
            const closeDrawer = () => updateState(false);

            handle.addEventListener('click', toggleDrawer);
            handle.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    toggleDrawer();
                }
            });

            if (closeButton) {
                closeButton.addEventListener('click', closeDrawer);
            }

            doc.addEventListener('keydown', (event) => {
                if (event.key === 'Escape') {
                    closeDrawer();
                }
            });

            drawer.dataset.bound = 'true';
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )

    if import_errors:
        with st.sidebar:
            st.markdown("---")
            st.subheader(get_text_gui("import_errors_title"))
            for error_msg in import_errors:
                st.error(error_msg)
            st.markdown("---")

    #  LIVE-KOSTEN-VORSCHAU - IMMER SICHTBAR WENN BERECHNUNGEN VORHANDEN
    render_live_cost_preview()

    # Profil-Editor anzeigen (falls aktiviert)
    if st.session_state.get('show_profile_editor'):
        from user_menu import render_profile_editor
        render_profile_editor()
        return  # Stoppt weitere Rendering

    # Seiten-Rendering basierend auf Auswahl
    if selected_page_key == "input":
        st.header(get_text_gui("menu_item_input"))
        if data_input_module and callable(getattr(data_input_module, 'render_data_input', None)):
            data_input_module.render_data_input(TEXTS)
        else:
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_input", "Eingabemodul nicht verfügbar.")))

    elif selected_page_key == "analysis":
        st.header(get_text_gui("menu_item_analysis"))
        if analysis_module and callable(getattr(analysis_module, 'render_analysis', None)):
            try:
                analysis_module.render_analysis(TEXTS, st.session_state.get("calculation_results"))
                
                # === [FIX] MASTER-FIX: Alle Charts verfügbar machen ===
                try:
                    from MASTER_FIX import apply_master_fix
                    apply_master_fix()
                except Exception as e_master_fix:
                    # Silent fail - nicht kritisch
                    import logging
                    logging.warning(f"MASTER-FIX konnte nicht angewendet werden: {e_master_fix}")
                
            except Exception as e_render_analysis:
                st.error(f"Fehler beim Rendern des Analyse-Tabs: {e_render_analysis}")
                st.text_area("Traceback Analysis:", traceback.format_exc(), height=200)
        else:
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_analysis", "Analysemodul nicht verfügbar.")))

    elif selected_page_key == "admin":
        required_modules_for_admin_render = [admin_panel_module, database_module, product_db_module, calculations_module]
        if all(m is not None for m in required_modules_for_admin_render) and callable(getattr(admin_panel_module, 'render_admin_panel', None)):
            admin_kwargs_pass = {
                "texts": TEXTS,
                "get_db_connection_func": getattr(database_module, 'get_db_connection', None),
                "save_admin_setting_func": getattr(database_module, 'save_admin_setting', None),
                "load_admin_setting_func": getattr(database_module, 'load_admin_setting', None),
                "parse_price_matrix_csv_func": lambda *args: None,  # Deprecated - using MatrixLoader now
                "parse_price_matrix_excel_func": lambda *args: None,  # Deprecated - using MatrixLoader now
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
                     if func_name_key in ["parse_price_matrix_csv_func", "parse_price_matrix_excel_func", "get_db_connection_func", "save_admin_setting_func", "load_admin_setting_func"]:
                         if not is_callable_admin:
                             all_critical_funcs_valid = False
            if not all_critical_funcs_valid:
                 st.error("Einige Kernfunktionen für das Admin-Panel (DB-Zugriff oder Parser) konnten nicht geladen werden. Bitte Terminal prüfen.")
            else:
                try:
                    admin_panel_module.render_admin_panel(**admin_kwargs_pass) # type: ignore
                except Exception as e_render_admin:
                    st.error(f"Fehler im Admin-Panel: {e_render_admin}")
                    st.text_area("Traceback Admin:", traceback.format_exc(), height=200)
        else:
            missing_modules_admin_list = [name for name, mod in [("Admin-Panel", admin_panel_module), ("Datenbank", database_module), ("Produkt-DB", product_db_module), ("Berechnungen", calculations_module)] if not mod]
            st.warning(get_text_gui("module_unavailable_details", f"Admin-Panel oder dessen Abhängigkeiten ({', '.join(missing_modules_admin_list)}) nicht verfügbar."))

    elif selected_page_key == "doc_output":
        st.header(get_text_gui("menu_item_doc_output"))

        # Tabs für PDF-Ausgabe erstellen - VEREINFACHT (Professional PDF Features sind jetzt in Standard PDF integriert)
        # Multi-Angebote Tab wieder eingefügt
        tab_single_pdf, tab_pdf_preview, tab_multi_offers = st.tabs([
            " PDF-Ausgabe",
            " PDF-Vorschau",
            " Multi-Firmen-Angebote"
        ])

        with tab_single_pdf:
            if doc_output_module and database_module and product_db_module and callable(getattr(doc_output_module, 'render_pdf_ui', None)):
                project_data_doc = st.session_state.get('project_data', {})
                calc_results_doc = st.session_state.get("calculation_results", {})

                # Erweiterte Validierung der Daten
                project_valid = (project_data_doc and
                               project_data_doc.get('project_details',{}).get('module_quantity'))
                calc_results_valid = (calc_results_doc and
                                    isinstance(calc_results_doc, dict) and
                                    len(calc_results_doc) > 0)

                if not project_valid or not calc_results_valid:
                    st.info(" **PDF-Generierung benötigt vollständige Projekt- und Berechnungsdaten**")
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
                    # Zusätzliche Validierung: Stelle sicher, dass calc_results_doc nicht leer ist
                    if not calc_results_doc or len(calc_results_doc) == 0:
                        # Versuche, die Daten aus der Session State zu laden
                        calc_results_doc = st.session_state.get("calculation_results", {})
                        if not calc_results_doc:
                            st.error(" **Berechnungsdaten nicht verfügbar**")
                            st.info("Bitte führen Sie zuerst eine Berechnung in der Analysestufe durch.")
                            return

                    pdf_ui_kwargs_pass = {
                        "texts": TEXTS, "project_data": project_data_doc, "analysis_results": calc_results_doc,
                        "load_admin_setting_func": getattr(database_module, 'load_admin_setting', None),
                        "save_admin_setting_func": getattr(database_module, 'save_admin_setting', None),
                        "list_products_func": getattr(product_db_module, 'list_products', None),
                        "get_product_by_id_func": getattr(product_db_module, 'get_product_by_id', None),
                        "get_active_company_details_func": getattr(database_module, 'get_active_company', None),
                        "db_list_company_documents_func": getattr(database_module, 'list_company_documents', None)
                    }
                    critical_funcs_for_pdf_check = [ val for key, val in pdf_ui_kwargs_pass.items() if key.endswith("_func") ]
                    if not all(f is not None and callable(f) for f in critical_funcs_for_pdf_check):
                         st.error("Einige Kernfunktionen für die PDF-Ausgabe konnten nicht geladen werden oder sind nicht aufrufbar.")
                    else:
                        try:
                            doc_output_module.render_pdf_ui(**pdf_ui_kwargs_pass) # type: ignore
                        except Exception as e_render_pdf:
                            st.error(f"Fehler beim Rendern der PDF UI: {e_render_pdf}")
                            st.text_area("Traceback PDF UI:", traceback.format_exc(), height=200)
            else:
                st.warning(get_text_gui("module_unavailable_details", "PDF-Ausgabemodul oder dessen Abhängigkeiten sind nicht verfügbar."))



        # === PDF-VORSCHAU TAB ===
        with tab_pdf_preview:
            st.subheader("👁️ Live PDF-Vorschau & Bearbeitung")

            # PDF-Vorschau Modul importieren und verwenden
            try:
                from pdf_preview import (
                    PDF_PREVIEW_AVAILABLE,
                    render_pdf_preview_interface,
                )

                if not PDF_PREVIEW_AVAILABLE:
                    # Shim-Modul zeigt hilfreiche Meldung mit Schritt-für-Schritt-Anleitung
                    render_pdf_preview_interface()
                else:
                    # HAUPT-PDF-VORSCHAU-FUNKTIONALITÄT
                    project_data_preview = st.session_state.get('project_data', {})
                    calc_results_preview = st.session_state.get("calculation_results", {})

                    if not project_data_preview or not calc_results_preview:
                        st.info("ℹ Bitte führen Sie zuerst eine Projektanalyse durch, um die PDF-Vorschau zu nutzen.")
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
                            st.info(" Hier würde Ihre PDF-Vorschau erscheinen...")

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
                            if database_module and callable(getattr(database_module, 'get_active_company', None)):
                                active_company = database_module.get_active_company()

                            if not active_company:
                                st.warning(" Keine aktive Firma gefunden. Bitte wählen Sie eine Firma im Admin-Panel.")
                                active_company = {"id": 1, "name": "Standard-Firma"}

                            # PDF-Vorschau Interface aufrufen
                            render_pdf_preview_interface(
                                project_data=project_data_preview,
                                analysis_results=calc_results_preview,
                                company_info=active_company,
                                texts=TEXTS,
                                load_admin_setting_func=getattr(database_module, 'load_admin_setting', None),
                                save_admin_setting_func=getattr(database_module, 'save_admin_setting', None),
                                list_products_func=getattr(product_db_module, 'list_products', None),
                                get_product_by_id_func=getattr(product_db_module, 'get_product_by_id', None),
                                db_list_company_documents_func=getattr(database_module, 'list_company_documents', None),
                                active_company_id=active_company.get('id')
                            )

                        except Exception as e_preview:
                            st.error(f" Fehler bei der PDF-Vorschau: {e_preview}")
                            st.markdown("###  Fehlerbehebung:")
                            st.markdown("""
                            1. **Überprüfen Sie die Module:** Stellen Sie sicher, dass alle PDF-Module geladen sind
                            2. **Projektdaten:** Führen Sie eine vollständige Projektanalyse durch
                            3. **Firmeneinstellungen:** Wählen Sie eine aktive Firma im Admin-Panel
                            4. **Abhängigkeiten:** Installieren Sie `pip install pymupdf pillow`
                            """)

                            if st.checkbox(" Detaillierte Fehlermeldung anzeigen", key="preview_debug"):
                                st.code(traceback.format_exc())

            except ImportError as e_import:
                st.error(f" PDF-Vorschau-Modul konnte nicht importiert werden: {e_import}")
                st.info(" Überprüfen Sie, ob `pdf_preview.py` vorhanden ist und alle Abhängigkeiten installiert sind.")

                # Installations-Hilfe
                st.markdown("###  Installation der Abhängigkeiten:")
                st.code("""
                pip install pymupdf
                pip install pillow
                pip install reportlab
                """)

            except Exception as e_general:
                st.error(f" Unerwarteter Fehler im PDF-Vorschau-Tab: {e_general}")
                if st.checkbox(" Debug-Informationen anzeigen", key="preview_general_debug"):
                    st.code(traceback.format_exc())

        # Multi-Angebote Tab wieder aktiviert
        with tab_multi_offers:
            st.subheader(" Multi-Firmen-Angebotsgenerator")
            if multi_offer_module and callable(getattr(multi_offer_module, 'render_multi_offer_generator', None)):
                project_data_doc = st.session_state.get('project_data', {})
                calc_results_doc = st.session_state.get("calculation_results", {})
                multi_offer_module.render_multi_offer_generator(TEXTS, project_data_doc, calc_results_doc)

                # Aufruf der neuen Produktauswahl-Logik
                if hasattr(multi_offer_module, 'render_product_selection'):
                    multi_offer_module.render_product_selection()
            else:
                st.warning(" Multi-Angebots-Modul nicht verfügbar.")

    elif selected_page_key == "quick_calc":
        # A.G.E.N.T. - Autonomous AI Expert System
        # Use agent_ui module if available, fallback to quick_calc for backward compatibility
        if agent_ui_module and callable(getattr(agent_ui_module, 'render_agent_menu', None)):
            agent_ui_module.render_agent_menu() # type: ignore
        elif quick_calc_module and callable(getattr(quick_calc_module, 'render_quick_calc', None)):
            st.header(get_text_gui("menu_item_quick_calc"))
            quick_calc_module.render_quick_calc(TEXTS, module_name=get_text_gui("menu_item_quick_calc")) # type: ignore
        else:
            st.header(get_text_gui("menu_item_quick_calc"))
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_quick_calc","A.G.E.N.T. nicht verfügbar.")))

    elif selected_page_key == "crm":
        st.header(get_text_gui("menu_item_crm"))

        tab_labels = [
            get_text_gui("crm_tab_customers", get_text_gui("menu_item_crm")),
            get_text_gui("crm_tab_dashboard", get_text_gui("menu_item_crm_dashboard")),
            get_text_gui("crm_tab_pipeline", get_text_gui("menu_item_crm_pipeline")),
            get_text_gui("crm_tab_calendar", get_text_gui("menu_item_crm_calendar")),
        ]

        tab_customers, tab_dashboard, tab_pipeline, tab_calendar = st.tabs(tab_labels)

        with tab_customers:
            if crm_module and database_module and callable(getattr(crm_module, 'render_crm', None)):
                crm_module.render_crm( # type: ignore
                    TEXTS,
                    getattr(database_module, 'get_db_connection', None),
                    show_header=False,
                )
            else:
                st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_crm", "CRM nicht verfügbar.")))

        with tab_dashboard:
            if crm_dashboard_ui_module and callable(getattr(crm_dashboard_ui_module, 'render_crm_dashboard', None)):
                crm_dashboard_ui_module.render_crm_dashboard( # type: ignore
                    TEXTS,
                    module_name=get_text_gui("crm_tab_dashboard", get_text_gui("menu_item_crm_dashboard")),
                )
            else:
                st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_crm_dashboard", "CRM Dashboard nicht verfügbar.")))

        with tab_pipeline:
            if crm_pipeline_ui_module and callable(getattr(crm_pipeline_ui_module, 'render_crm_pipeline', None)):
                crm_pipeline_ui_module.render_crm_pipeline( # type: ignore
                    TEXTS,
                    module_name=get_text_gui("crm_tab_pipeline", get_text_gui("menu_item_crm_pipeline")),
                )
            else:
                st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_crm_pipeline", "CRM Pipeline nicht verfügbar.")))

        with tab_calendar:
            if crm_calendar_ui_module and callable(getattr(crm_calendar_ui_module, 'render_crm_calendar', None)):
                crm_calendar_ui_module.render_crm_calendar( # type: ignore
                    TEXTS,
                    module_name=get_text_gui("crm_tab_calendar", get_text_gui("menu_item_crm_calendar")),
                )
            else:
                st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_crm_calendar", "CRM Kalender nicht verfügbar.")))

    elif selected_page_key == "info_platform":
        st.header(get_text_gui("menu_item_info_platform"))
        if info_platform_module and callable(getattr(info_platform_module, 'render_info_platform', None)):
            info_platform_module.render_info_platform(TEXTS, module_name=get_text_gui("menu_item_info_platform")) # type: ignore
        else:
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_info","Info-Plattform nicht verfügbar.")))

    elif selected_page_key == "options":
        st.header(get_text_gui("menu_item_options"))

        # Tabs für die Optionen erstellen
        tab_general, tab_ai = st.tabs([" Allgemeine Einstellungen", "A.G.E.N.T. Begleiter"])

        with tab_general:
            if options_module and callable(getattr(options_module, 'render_options', None)):
                options_module.render_options(TEXTS, module_name=get_text_gui("menu_item_options")) # type: ignore
            else:
                st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_options","Optionen nicht verfügbar.")))

        with tab_ai:
            st.subheader("A.G.E.N.T. Begleiter")
            if ai_companion_module and callable(getattr(ai_companion_module, 'render_ai_companion', None)):
                ai_companion_module.render_ai_companion()
            else:
                st.warning(" AA.G.E.N.T. Begleiter Modul nicht verfügbar.")

    elif selected_page_key == "heatpump":
        st.header(get_text_gui("menu_item_heatpump"))
        if heatpump_ui_module and callable(getattr(heatpump_ui_module, 'render_heatpump', None)):
            heatpump_ui_module.render_heatpump(TEXTS, module_name=get_text_gui("menu_item_heatpump")) # type: ignore
        else:
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_heatpump","Wärmepumpen-Modul nicht verfügbar.")))

    elif selected_page_key == "solar_calculator":
        st.header(TEXTS.get("menu_item_solar_calculator", "Solar Calculator"))
        if solar_calculator_module and callable(getattr(solar_calculator_module, 'render_solar_calculator', None)):
            solar_calculator_module.render_solar_calculator(TEXTS, module_name=TEXTS.get("menu_item_solar_calculator", "Solar Calculator")) # type: ignore
        else:
            st.warning(get_text_gui("module_unavailable_details", "Solar Calculator Modul nicht verfügbar."))

if __name__ == "__main__":
    try:
        locales_module = import_module_with_fallback("locales", import_errors)
        database_module = import_module_with_fallback("database", import_errors)
        product_db_module = import_module_with_fallback("product_db", import_errors)
        data_input_module = import_module_with_fallback("data_input", import_errors)
        calculations_module = import_module_with_fallback("calculations", import_errors)
        analysis_module = import_module_with_fallback("analysis", import_errors)
        crm_module = import_module_with_fallback("crm", import_errors)
        admin_panel_module = import_module_with_fallback("admin_panel", import_errors)
        doc_output_module = import_module_with_fallback("doc_output", import_errors)
        quick_calc_module = import_module_with_fallback("quick_calc", import_errors)
        # Import Agent UI module from Agent directory
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Agent"))
        agent_ui_module = import_module_with_fallback("agent_ui", import_errors)
        info_platform_module = import_module_with_fallback("info_platform", import_errors)
        options_module = import_module_with_fallback("options", import_errors)
        pv_visuals_module = import_module_with_fallback("pv_visuals", import_errors)
        ai_companion_module = import_module_with_fallback("ai_companion", import_errors)
        multi_offer_module = import_module_with_fallback("multi_offer_generator", import_errors)
        pdf_preview_module = import_module_with_fallback("pdf_preview", import_errors)
        crm_calendar_ui_module = import_module_with_fallback("crm_calendar_ui", import_errors)
        crm_pipeline_ui_module = import_module_with_fallback("crm_pipeline_ui", import_errors)
        crm_dashboard_ui_module = import_module_with_fallback("crm_dashboard_ui", import_errors)
        heatpump_ui_module = import_module_with_fallback("heatpump_ui", import_errors)
        solar_calculator_module = import_module_with_fallback("solar_calculator", import_errors)

        if 'db_initialized' not in st.session_state:
            if database_module:
                initialize_database_once()
            st.session_state['db_initialized'] = True

        if database_module:
            main()
        else:
            st.set_page_config(page_title=_texts_initial.get("app_title", "Fehler"), layout="wide")
            st.error(get_text_gui("gui_critical_error_no_db", "Datenbankmodul nicht geladen. Anwendung kann nicht starten."))
            if import_errors:
                with st.sidebar:
                    st.subheader("Ladefehler")
                    for err_msg_display in import_errors:
                        st.error(err_msg_display)

    except Exception as e_global_gui_main_block:
        critical_error_text_for_display_main_block = get_text_gui("gui_critical_error", "Ein kritischer Fehler ist in der Anwendung aufgetreten!")
        try:
            st.set_page_config(page_title="Kritischer Fehler", layout="wide")
            st.error(f"{critical_error_text_for_display_main_block}\nDetails: {e_global_gui_main_block}")
            st.text_area("Traceback Global:", traceback.format_exc(), height=300)
        except Exception:
            pass

# Änderungshistorie
# 2025-07-12, GitHub Copilot: Komplette Neuerstellung der gui.py Datei zur Behebung aller Syntax- und Import-Fehler
#                             - Alle Variablennamen korrekt (*_ui_module statt *_module)
#                             - Alle Einrückungen und Zeilenumbrüche korrigiert
#                             - render_crm_calendar Signatur mit module_name Parameter korrigiert
#                             - Vollständig saubere Struktur ohne Syntaxfehler
