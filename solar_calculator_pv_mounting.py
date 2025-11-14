"""
solar_calculator_pv_mounting.py

PV Mounting Component Selection for Solar Calculator.
Renders dropdown-based selection interface for mounting system components.

Integrated into solar_calculator.py Step 1 (Component Selection).

VERSION 2.0: Automatic quantity calculation integration
"""

import streamlit as st
from typing import Dict, Any, List, Optional

# Import mounting database bridge
try:
    from pv_mounting_db_bridge import (
        get_pv_mounting_manufacturers_by_category,
        get_pv_mounting_component_names_by_manufacturer,
        get_pv_mounting_component_by_name,
        get_pv_mounting_roof_types,
        PV_MOUNTING_DB_AVAILABLE,
    )
    from solar_calculator_pv_mounting_integration import (
        calculate_mounting_requirements_from_details,
        update_mounting_quantities_in_details,
        render_mounting_calculation_summary,
        get_mounting_total_price
    )
    PV_MOUNTING_INTEGRATION_FULL = True
except ImportError:
    PV_MOUNTING_DB_AVAILABLE = False
    PV_MOUNTING_INTEGRATION_FULL = False


def _get_text(texts: Dict[str, str], key: str, default: str) -> str:
    """Get localized text with fallback."""
    if isinstance(texts, dict):
        return texts.get(key, default)
    return default


def render_pv_mounting_selection(
    details: Dict[str, Any],
    texts: Dict[str, str],
    please_select_text: str = "-- Bitte wählen --"
) -> None:
    """
    Render PV mounting component selection interface.
    
    Args:
        details: Session state project_details dictionary
        texts: Localization texts
        please_select_text: Placeholder text for dropdowns
    """
    
    if not PV_MOUNTING_DB_AVAILABLE:
        st.warning("[WARNING] PV-Unterkonstruktions-Datenbank nicht verfügbar. Bitte Admin kontaktieren.")
        return
    
    st.markdown("---")
    st.markdown("### [TOOL] PV-Unterkonstruktion")
    
    # Checkbox to include mounting components
    details['include_pv_mounting'] = st.checkbox(
        "PV-Unterkonstruktion konfigurieren",
        value=bool(details.get('include_pv_mounting', True)),  # Default: True
        key='include_pv_mounting_sc',
        help="Dachhaken, Montageschienen, Modulklemmen, etc."
    )
    
    if not details['include_pv_mounting']:
        # Clear selections if disabled
        _clear_mounting_selections(details)
        return
    
    # Get roof types from database
    roof_types = get_pv_mounting_roof_types()
    if not roof_types:
        st.info("[PACKAGE] Keine Dachtypen in Datenbank gefunden. Bitte zuerst Komponenten im Admin-Bereich hinzufügen.")
        return
    
    # === ROOF TYPE SELECTION ===
    st.markdown("#### Dachtyp")
    
    # [OK] FIX: Auto-fill from Bedarfsanalyse (data_input.py)
    # Prüfe ob Dachtyp bereits in Bedarfsanalyse gewählt wurde
    from_bedarfsanalyse = details.get('roof_type')  # Aus data_input.py
    
    # Wenn Dachtyp aus Bedarfsanalyse vorhanden, übernehme ihn
    if from_bedarfsanalyse and from_bedarfsanalyse != please_select_text:
        # Nur übernehmen wenn noch nicht gesetzt
        if not details.get('pv_mounting_roof_type'):
            details['pv_mounting_roof_type'] = from_bedarfsanalyse
            st.success(f"[OK] Dachtyp aus Bedarfsanalyse übernommen: **{from_bedarfsanalyse}**")
    
    current_roof_type = details.get('pv_mounting_roof_type', please_select_text)
    roof_type_options = [please_select_text] + roof_types
    
    try:
        idx_roof = roof_type_options.index(current_roof_type)
    except ValueError:
        idx_roof = 0
    
    selected_roof_type = st.selectbox(
        "Dachtyp auswählen *" + (" (aus Bedarfsanalyse)" if from_bedarfsanalyse and from_bedarfsanalyse != please_select_text else ""),
        options=roof_type_options,
        index=idx_roof,
        key='pv_mounting_roof_type_select',
        help="Bestimmt verfügbare Komponenten. Wird automatisch aus Bedarfsanalyse übernommen, falls vorhanden."
    )
    
    details['pv_mounting_roof_type'] = selected_roof_type if selected_roof_type != please_select_text else None
    
    if not details.get('pv_mounting_roof_type'):
        st.info("👆 Bitte Dachtyp auswählen, um Komponenten zu konfigurieren.")
        return
    
    # === AUTOMATIC QUANTITY CALCULATION ===
    if PV_MOUNTING_INTEGRATION_FULL:
        st.markdown("---")
        col_calc1, col_calc2 = st.columns([3, 1])
        
        with col_calc1:
            st.markdown("#### 🔢 Automatische Mengenberechnung")
            
        with col_calc2:
            if st.button("🔄 Berechnen", key='calc_mounting_quantities'):
                # [OK] FIX: Prüfe beide mögliche Keys für Modulanzahl
                module_count = (
                    details.get('module_count', 0) or 
                    details.get('module_quantity', 0) or 
                    st.session_state.get('module_quantity_sc_v1', 0) or 
                    0
                )
                
                if module_count > 0:
                    with st.spinner("Berechne Unterkonstruktion..."):
                        calc_result = calculate_mounting_requirements_from_details(details)
                        if calc_result:
                            update_mounting_quantities_in_details(details, calc_result)
                            st.success(f"[OK] Berechnung für {module_count} Module abgeschlossen!")
                            st.rerun()
                        else:
                            st.error("[ERROR] Berechnung fehlgeschlagen. Bitte Eingaben prüfen.")
                else:
                    st.warning("[WARNING] Bitte zuerst Modulanzahl in Step 1 angeben.")
        
        # Show calculation summary if available
        if details.get('mounting_quantities_calculated'):
            render_mounting_calculation_summary(details)
            st.markdown("---")
    
    # === COMPONENT SELECTION ===
    # Define component categories to configure
    component_categories = [
        {
            'key': 'roof_hook',
            'category': 'Dachhaken',
            'label': 'Dachhaken',
            'icon': '[BUILD]',
            'required': True
        },
        {
            'key': 'mounting_rail',
            'category': 'Montageschiene',
            'label': 'Montageschiene',
            'icon': '📏',
            'required': True
        },
        {
            'key': 'end_clamp',
            'category': 'Modulklemme (End)',
            'label': 'Endklemme',
            'icon': '🔗',
            'required': True
        },
        {
            'key': 'mid_clamp',
            'category': 'Modulklemme (Mittel)',
            'label': 'Mittelklemme',
            'icon': '🔗',
            'required': True
        },
        {
            'key': 'screw',
            'category': 'Schrauben',
            'label': 'Schrauben',
            'icon': '🔩',
            'required': False
        },
        {
            'key': 'cable',
            'category': 'Kabel',
            'label': 'Solar-Kabel',
            'icon': '[POWER]',
            'required': False
        },
    ]
    
    st.markdown("#### Komponenten auswählen")
    
    for comp_config in component_categories:
        _render_component_selector(
            comp_config=comp_config,
            details=details,
            roof_type=details['pv_mounting_roof_type'],
            please_select_text=please_select_text
        )


def _render_component_selector(
    comp_config: Dict[str, Any],
    details: Dict[str, Any],
    roof_type: str,
    please_select_text: str
) -> None:
    """Render dropdown selection for a single component category."""
    
    key = comp_config['key']
    category = comp_config['category']
    label = comp_config['label']
    icon = comp_config['icon']
    required = comp_config['required']
    
    with st.expander(f"{icon} {label}" + (" *" if required else ""), expanded=required):
        # Manufacturer selection
        manufacturers = get_pv_mounting_manufacturers_by_category(category)
        
        if not manufacturers:
            st.info(f"📭 Keine Hersteller für '{label}' verfügbar.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Manufacturer dropdown
            current_manuf = details.get(f'pv_mounting_{key}_manufacturer', please_select_text)
            manuf_options = [please_select_text] + manufacturers
            
            try:
                idx_manuf = manuf_options.index(current_manuf)
            except ValueError:
                idx_manuf = 0
            
            selected_manuf = st.selectbox(
                "Hersteller",
                options=manuf_options,
                index=idx_manuf,
                key=f'pv_mounting_{key}_manuf_select'
            )
            
            details[f'pv_mounting_{key}_manufacturer'] = selected_manuf if selected_manuf != please_select_text else None
        
        with col2:
            # Product/Model selection
            if details.get(f'pv_mounting_{key}_manufacturer'):
                product_names = get_pv_mounting_component_names_by_manufacturer(
                    category=category,
                    manufacturer=details[f'pv_mounting_{key}_manufacturer'],
                    roof_type=roof_type
                )
                
                if not product_names:
                    st.warning(f"[WARNING] Keine Produkte für '{details[f'pv_mounting_{key}_manufacturer']}' verfügbar.")
                    details[f'pv_mounting_{key}_name'] = None
                else:
                    current_prod = details.get(f'pv_mounting_{key}_name', please_select_text)
                    prod_options = [please_select_text] + product_names
                    
                    try:
                        idx_prod = prod_options.index(current_prod)
                    except ValueError:
                        idx_prod = 0
                    
                    selected_prod = st.selectbox(
                        "Produkt",
                        options=prod_options,
                        index=idx_prod,
                        key=f'pv_mounting_{key}_prod_select'
                    )
                    
                    details[f'pv_mounting_{key}_name'] = selected_prod if selected_prod != please_select_text else None
                    
                    # Load component details and display info
                    if details.get(f'pv_mounting_{key}_name'):
                        component = get_pv_mounting_component_by_name(details[f'pv_mounting_{key}_name'])
                        if component:
                            details[f'pv_mounting_{key}_id'] = component['id']
                            details[f'pv_mounting_{key}_price'] = component.get('price_netto', 0.0)
                            details[f'pv_mounting_{key}_unit'] = component.get('unit', 'Stk')
                            details[f'pv_mounting_{key}_pdf_available'] = bool(component.get('pdf_bytes'))
                            
                            # Display component info
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.caption(f"[MONEY] Preis: {component['price_netto']:.2f} € / {component.get('unit', 'Stk')}")
                            with col_info2:
                                if component.get('pdf_bytes'):
                                    st.caption("[FILE] Datenblatt verfügbar")
                            
                            if component.get('article_number'):
                                st.caption(f"[PACKAGE] Art.-Nr: {component['article_number']}")
            else:
                st.info("👈 Bitte zuerst Hersteller wählen")
                details[f'pv_mounting_{key}_name'] = None


def _clear_mounting_selections(details: Dict[str, Any]) -> None:
    """Clear all mounting component selections from session state."""
    
    keys_to_clear = [
        'pv_mounting_roof_type',
        'pv_mounting_roof_hook_manufacturer',
        'pv_mounting_roof_hook_name',
        'pv_mounting_roof_hook_id',
        'pv_mounting_roof_hook_price',
        'pv_mounting_roof_hook_unit',
        'pv_mounting_mounting_rail_manufacturer',
        'pv_mounting_mounting_rail_name',
        'pv_mounting_mounting_rail_id',
        'pv_mounting_mounting_rail_price',
        'pv_mounting_mounting_rail_unit',
        'pv_mounting_end_clamp_manufacturer',
        'pv_mounting_end_clamp_name',
        'pv_mounting_end_clamp_id',
        'pv_mounting_end_clamp_price',
        'pv_mounting_end_clamp_unit',
        'pv_mounting_mid_clamp_manufacturer',
        'pv_mounting_mid_clamp_name',
        'pv_mounting_mid_clamp_id',
        'pv_mounting_mid_clamp_price',
        'pv_mounting_mid_clamp_unit',
        'pv_mounting_screw_manufacturer',
        'pv_mounting_screw_name',
        'pv_mounting_screw_id',
        'pv_mounting_screw_price',
        'pv_mounting_screw_unit',
        'pv_mounting_cable_manufacturer',
        'pv_mounting_cable_name',
        'pv_mounting_cable_id',
        'pv_mounting_cable_price',
        'pv_mounting_cable_unit',
    ]
    
    for key in keys_to_clear:
        if key in details:
            details[key] = None


def get_selected_mounting_components_summary(details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get summary of selected mounting components for display/export.
    
    Returns dict with component names, prices, and availability flags.
    """
    
    if not details.get('include_pv_mounting'):
        return {}
    
    summary = {
        'roof_type': details.get('pv_mounting_roof_type'),
        'components': []
    }
    
    component_keys = ['roof_hook', 'mounting_rail', 'end_clamp', 'mid_clamp', 'screw', 'cable']
    component_labels = {
        'roof_hook': 'Dachhaken',
        'mounting_rail': 'Montageschiene',
        'end_clamp': 'Endklemme',
        'mid_clamp': 'Mittelklemme',
        'screw': 'Schrauben',
        'cable': 'Solar-Kabel'
    }
    
    for key in component_keys:
        name = details.get(f'pv_mounting_{key}_name')
        if name:
            summary['components'].append({
                'category': component_labels[key],
                'name': name,
                'manufacturer': details.get(f'pv_mounting_{key}_manufacturer'),
                'price': details.get(f'pv_mounting_{key}_price', 0.0),
                'unit': details.get(f'pv_mounting_{key}_unit', 'Stk'),
                'pdf_available': details.get(f'pv_mounting_{key}_pdf_available', False)
            })
    
    return summary


# === Testing ===
if __name__ == "__main__":
    st.set_page_config(page_title="PV Mounting Test", layout="wide")
    
    # Mock session state
    if 'project_details' not in st.session_state:
        st.session_state.project_details = {}
    
    details = st.session_state.project_details
    texts = {}
    
    render_pv_mounting_selection(details, texts)
    
    # Debug output
    if details.get('include_pv_mounting'):
        st.markdown("---")
        st.markdown("### Debug: Selected Components")
        st.json(get_selected_mounting_components_summary(details))
