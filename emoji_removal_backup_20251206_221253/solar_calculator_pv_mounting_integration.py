"""
PV-Unterkonstruktions-Integration für Solar Calculator
=======================================================

Automatische Mengenberechnung basierend auf Modulanzahl und
Integration mit pv_mounting_calculations.py.

Autor: Bokuk2 System
Version: 1.0.0
Datum: 2025-11-06
"""

from typing import Dict, List, Optional, Any
import streamlit as st

from pv_mounting_calculations import (
    ModuleConfiguration,
    RoofConfiguration,
    calculate_mounting_system,
    MountingCalculationResult
)
from pv_mounting_db_bridge import (
    get_pv_mounting_component_by_name,
    get_pv_mounting_component_price,
    get_pv_mounting_component_unit
)


def calculate_mounting_requirements_from_details(
    project_details: Dict[str, Any]
) -> Optional[MountingCalculationResult]:
    """
    Berechnet Unterkonstruktions-Anforderungen aus project_details.
    
    Args:
        project_details: Solar Calculator project_details Dictionary
        
    Returns:
        MountingCalculationResult oder None bei Fehler
    """
    try:
        # FIX: Modul-Konfiguration aus project_details
        # Prüfe mehrere mögliche Keys für Modulanzahl (Kompatibilität mit verschiedenen Modulen)
        module_count = (
            project_details.get('module_count', 0) or 
            project_details.get('module_quantity', 0) or 
            0
        )
        
        if module_count <= 0:
            return None
            
        # Module-Spezifikationen (mit Defaults)
        module_width_mm = project_details.get('module_width_mm', 1134)
        module_height_mm = project_details.get('module_height_mm', 1722)
        module_weight_kg = project_details.get('module_weight_kg', 21.5)
        
        # Orientation (Portrait/Landscape)
        orientation = project_details.get('module_orientation', 'Portrait')
        
        # Rows (optional, wird berechnet falls nicht vorhanden)
        rows = project_details.get('module_rows', 1)
        
        module_config = ModuleConfiguration(
            count=module_count,
            width_mm=module_width_mm,
            height_mm=module_height_mm,
            weight_kg=module_weight_kg,
            orientation=orientation,
            rows=rows
        )
        
        # Dach-Konfiguration
        # FIX: Prüfe beide mögliche Keys für Dachtyp
        roof_type = (
            project_details.get('pv_mounting_roof_type') or  # Spezifisches Feld
            project_details.get('roof_type') or              # Aus Bedarfsanalyse
            'Ziegeldach'                                      # Fallback
        )
        roof_pitch_deg = project_details.get('roof_pitch_degrees', 35.0)
        roof_orientation = project_details.get('roof_orientation', 'Süd')
        rafter_spacing = project_details.get('rafter_spacing_mm', 800.0)
        snow_zone = project_details.get('snow_load_zone', 2)
        wind_zone = project_details.get('wind_load_zone', 2)
        
        roof_config = RoofConfiguration(
            roof_type=roof_type,
            pitch_degrees=roof_pitch_deg,
            orientation=roof_orientation,
            rafter_spacing_mm=rafter_spacing,
            snow_load_zone=snow_zone,
            wind_load_zone=wind_zone
        )
        
        # Optional: Hersteller aus manueller Auswahl
        manufacturer = project_details.get('mounting_manufacturer', 'K2 Systems')
        distance_to_inverter = project_details.get('distance_to_inverter_m', 10.0)
        
        # Berechnung durchführen
        result = calculate_mounting_system(
            module_config=module_config,
            roof_config=roof_config,
            manufacturer=manufacturer,
            distance_to_inverter_m=distance_to_inverter
        )
        
        return result
        
    except Exception as e:
        st.error(f"Fehler bei Unterkonstruktions-Berechnung: {e}")
        return None


def update_mounting_quantities_in_details(
    project_details: Dict[str, Any],
    calculation_result: MountingCalculationResult
) -> None:
    """
    Aktualisiert project_details mit berechneten Mengen.
    
    Diese Funktion überschreibt manuelle Auswahlen NICHT,
    fügt aber berechnete Mengen hinzu.
    
    Args:
        project_details: Solar Calculator project_details (wird modifiziert)
        calculation_result: Berechnungsergebnis
    """
    # Speichere Berechnungsergebnis
    project_details['mounting_calculation_result'] = {
        'total_components_count': calculation_result.total_components_count,
        'total_price_netto': calculation_result.total_price_netto,
        'total_weight_kg': calculation_result.total_weight_kg,
        'calculation_notes': calculation_result.calculation_notes,
        'warnings': calculation_result.warnings
    }
    
    # Komponenten mit Mengen
    project_details['mounting_components_calculated'] = []
    
    for comp in calculation_result.components:
        component_data = {
            'component_id': comp.component_id,
            'product_name': comp.product_name,
            'category': comp.category,
            'manufacturer': comp.manufacturer,
            'quantity': comp.quantity,
            'unit': comp.unit,
            'price_per_unit': comp.price_per_unit,
            'total_price': comp.total_price,
            'notes': comp.notes
        }
        project_details['mounting_components_calculated'].append(component_data)
    
    # Flags setzen
    project_details['mounting_quantities_calculated'] = True
    project_details['mounting_last_calculation_module_count'] = calculation_result.module_config.count


def merge_manual_and_calculated_components(
    project_details: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Merged manuell ausgewählte Komponenten mit automatisch berechneten Mengen.
    
    Logik:
    - Wenn Komponente manuell ausgewählt: Verwende automatische Menge
    - Wenn nur manuell: Behalte manuelle Auswahl (Menge 1)
    - Wenn nur berechnet: Verwende Berechnung
    
    Args:
        project_details: Solar Calculator project_details
        
    Returns:
        List[Dict]: Merged Komponenten-Liste für PDF/Pricing
    """
    manual_components = {}
    calculated_components = {}
    
    # Sammle manuelle Auswahlen
    for category in ['roof_hook', 'mounting_rail', 'end_clamp', 'mid_clamp', 'screw', 'cable']:
        selected_name = project_details.get(f'mounting_{category}_selected_name')
        if selected_name:
            comp_data = get_pv_mounting_component_by_name(selected_name)
            if comp_data:
                manual_components[category] = {
                    'product_name': comp_data['product_name'],
                    'manufacturer': comp_data['manufacturer'],
                    'category': comp_data['category'],
                    'price_netto': comp_data['price_netto'],
                    'unit': comp_data['unit'],
                    'quantity': 1,  # Default, wird überschrieben
                    'manual': True
                }
    
    # Sammle berechnete Komponenten
    if project_details.get('mounting_quantities_calculated'):
        for comp in project_details.get('mounting_components_calculated', []):
            cat_key = _category_to_key(comp['category'])
            # Normalize field names for consistency
            calculated_components[cat_key] = {
                'product_name': comp['product_name'],
                'manufacturer': comp['manufacturer'],
                'category': comp['category'],
                'price_netto': comp.get('price_per_unit', 0.0),  # Normalize
                'unit': comp['unit'],
                'quantity': comp['quantity'],
                'total_price': comp['total_price'],
                'notes': comp.get('notes', '')
            }
    
    # Merge
    merged = []
    
    for cat_key in ['roof_hook', 'mounting_rail', 'end_clamp', 'mid_clamp', 'screw', 'cable']:
        if cat_key in manual_components:
            # Manuell ausgewählt
            comp = manual_components[cat_key].copy()
            
            # Verwende berechnete Menge falls vorhanden
            if cat_key in calculated_components:
                comp['quantity'] = calculated_components[cat_key]['quantity']
                comp['total_price'] = comp['price_netto'] * comp['quantity']
                comp['auto_calculated'] = True
            else:
                comp['total_price'] = comp['price_netto']
                comp['auto_calculated'] = False
                
            merged.append(comp)
            
        elif cat_key in calculated_components:
            # Nur berechnet, nicht manuell ausgewählt
            merged.append(calculated_components[cat_key])
    
    return merged


def _category_to_key(category: str) -> str:
    """Konvertiert Kategorie-Name zu key."""
    mapping = {
        'Dachhaken': 'roof_hook',
        'Montageschiene': 'mounting_rail',
        'Endklemme': 'end_clamp',
        'Mittelklemme': 'mid_clamp',
        'Schraube': 'screw',
        'PV-Kabel': 'cable'
    }
    return mapping.get(category, category.lower().replace(' ', '_'))


def get_mounting_total_price(project_details: Dict[str, Any]) -> float:
    """
    Berechnet Gesamtpreis der Unterkonstruktion.
    
    Args:
        project_details: Solar Calculator project_details
        
    Returns:
        float: Gesamtpreis netto in EUR
    """
    merged = merge_manual_and_calculated_components(project_details)
    return sum(comp.get('total_price', 0.0) for comp in merged)


def get_mounting_components_for_pdf(
    project_details: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Bereitet Mounting-Komponenten für PDF auf.
    
    Args:
        project_details: Solar Calculator project_details
        
    Returns:
        List[Dict]: Komponenten mit allen PDF-relevanten Infos
    """
    merged = merge_manual_and_calculated_components(project_details)
    
    # Sortiere nach Kategorie
    category_order = ['Dachhaken', 'Montageschiene', 'Endklemme', 'Mittelklemme', 'Schraube', 'PV-Kabel']
    
    def sort_key(comp):
        cat = comp.get('category', '')
        try:
            return category_order.index(cat)
        except ValueError:
            return 999
    
    return sorted(merged, key=sort_key)


def render_mounting_calculation_summary(project_details: Dict[str, Any]) -> None:
    """
    Rendert Zusammenfassung der Unterkonstruktions-Berechnung in Streamlit.
    
    Args:
        project_details: Solar Calculator project_details
    """
    if not project_details.get('mounting_quantities_calculated'):
        st.info("Noch keine automatische Berechnung durchgeführt.")
        return
    
    calc_result = project_details.get('mounting_calculation_result', {})
    
    st.markdown("### Berechnete Unterkonstruktion")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Komponenten",
            f"{calc_result.get('total_components_count', 0)}"
        )
    
    with col2:
        total_price = calc_result.get('total_price_netto', 0.0)
        st.metric(
            "Gesamtpreis",
            f"{total_price:,.2f} €".replace(',', '.')
        )
    
    with col3:
        total_weight = calc_result.get('total_weight_kg', 0.0)
        st.metric(
            "Gewicht",
            f"{total_weight:.1f} kg"
        )
    
    # Warnings
    warnings = calc_result.get('warnings', [])
    if warnings:
        st.warning("**Hinweise:**\n\n" + "\n".join(f"- {w}" for w in warnings))
    
    # Komponenten-Tabelle
    with st.expander("📋 Komponenten-Details"):
        components = project_details.get('mounting_components_calculated', [])
        
        if components:
            for comp in components:
                st.markdown(f"""
**{comp['product_name']}** ({comp['manufacturer']})
- Kategorie: {comp['category']}
- Menge: {comp['quantity']} {comp['unit']}
- Einzelpreis: {comp['price_per_unit']:.2f} €
- Gesamt: {comp['total_price']:.2f} €
{f"- {comp['notes']}" if comp.get('notes') else ""}
---
                """)
