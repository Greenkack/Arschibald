"""
Excel Integration - Product Pricing UI

UI-Komponente für die Konfiguration von Produktpreisen aus Preismatrizen.
Ermöglicht die Auswahl zwischen Einzelpreis und Matrix-Preis mit Vorschau.
"""

import streamlit as st
from typing import Optional, Dict, Any, List

from excel.excel_product_pricing import (
    calculate_product_price_from_matrix,
    get_price_preview,
    validate_matrix_for_product_pricing,
    ProductPriceResult
)
from price_matrix_store import (
    list_matrices,
    get_active_matrix_id,
    set_active_matrix,
    get_matrix_full
)


def render_product_price_config_ui(
    product_id: Optional[int] = None,
    current_price: Optional[float] = None,
    current_pricing_mode: str = 'einzelpreis',
    current_matrix_id: Optional[int] = None,
    on_save_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Rendert die UI für Produktpreis-Konfiguration
    
    Args:
        product_id: Optionale Produkt-ID für Kontext
        current_price: Aktueller Einzelpreis
        current_pricing_mode: 'einzelpreis' oder 'matrix'
        current_matrix_id: Aktuelle Matrix-ID (falls Matrix-Modus)
        on_save_callback: Callback-Funktion beim Speichern
    
    Returns:
        Dictionary mit Konfiguration:
        {
            'pricing_mode': str,
            'price': Optional[float],
            'matrix_id': Optional[int],
            'row_label': Optional[str],
            'column_label': Optional[str]
        }
    """
    
    st.subheader("💰 Preisberechnung")
    
    # Initialisiere Session State
    if 'product_pricing_mode' not in st.session_state:
        st.session_state.product_pricing_mode = current_pricing_mode
    if 'product_price' not in st.session_state:
        st.session_state.product_price = current_price
    if 'product_matrix_id' not in st.session_state:
        st.session_state.product_matrix_id = current_matrix_id
    
    # Preismodus-Auswahl
    pricing_mode = st.radio(
        "Preismodus",
        options=["einzelpreis", "matrix"],
        format_func=lambda x: "📝 Einzelpreis" if x == "einzelpreis" else "📊 Matrix-Preis",
        horizontal=True,
        help="Einzelpreis: Manuell eingeben. Matrix-Preis: Aus Preismatrix berechnen",
        key="pricing_mode_radio"
    )
    
    st.session_state.product_pricing_mode = pricing_mode
    
    result = {
        'pricing_mode': pricing_mode,
        'price': None,
        'matrix_id': None,
        'row_label': None,
        'column_label': None
    }
    
    if pricing_mode == "einzelpreis":
        # Einzelpreis-Modus
        st.markdown("---")
        price = st.number_input(
            "Preis (€)",
            min_value=0.0,
            value=float(current_price or 0.0),
            step=10.0,
            format="%.2f",
            help="Geben Sie den Preis manuell ein",
            key="single_price_input"
        )
        
        st.session_state.product_price = price
        result['price'] = price
        
        if price > 0:
            st.success(f"✓ Preis: {price:,.2f} €")
    
    else:
        # Matrix-Preis-Modus
        st.markdown("---")
        
        # Matrix-Auswahl
        matrices = list_matrices()
        
        if not matrices:
            st.warning("⚠️ Keine Preismatrizen verfügbar. Bitte erstellen Sie zuerst eine Matrix im 'Preis Matrix' Tab.")
            return result
        
        # Matrix-Dropdown
        matrix_options = {m['id']: f"{m['name']} ({m['pricing_mode']})" for m in matrices}
        active_matrix_id = get_active_matrix_id()
        
        # Vorauswahl: current_matrix_id oder aktive Matrix
        default_matrix_id = current_matrix_id or active_matrix_id or matrices[0]['id']
        
        selected_matrix_id = st.selectbox(
            "Preismatrix auswählen",
            options=list(matrix_options.keys()),
            format_func=lambda x: matrix_options[x],
            index=list(matrix_options.keys()).index(default_matrix_id) if default_matrix_id in matrix_options else 0,
            help="Wählen Sie die Matrix für die Preisberechnung",
            key="matrix_selection"
        )
        
        st.session_state.product_matrix_id = selected_matrix_id
        result['matrix_id'] = selected_matrix_id
        
        # Matrix-Info anzeigen
        matrix_data = get_matrix_full(selected_matrix_id)
        if matrix_data:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Zeilen", len(matrix_data['rows']))
            with col2:
                st.metric("Spalten", len(matrix_data['columns']))
            with col3:
                st.metric("Modus", matrix_data['meta']['pricing_mode'].title())
            
            # Validierung
            validation = validate_matrix_for_product_pricing(selected_matrix_id)
            if not validation['valid']:
                st.error("❌ Matrix ist nicht gültig für Produktpreise:")
                for error in validation['errors']:
                    st.error(f"  • {error}")
                return result
            
            if validation['warnings']:
                with st.expander("⚠️ Warnungen", expanded=False):
                    for warning in validation['warnings']:
                        st.warning(f"  • {warning}")
            
            st.markdown("---")
            
            # Zeilen- und Spalten-Auswahl für Beispiel-Berechnung
            st.subheader("🔍 Preis-Vorschau")
            
            row_labels = [r['label'] for r in matrix_data['rows']]
            col_labels = [c['label'] for c in matrix_data['columns']]
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_row = st.selectbox(
                    "Zeile (z.B. Modulanzahl)",
                    options=row_labels,
                    help="Wählen Sie eine Zeile für die Vorschau",
                    key="preview_row_selection"
                )
                result['row_label'] = selected_row
            
            with col2:
                selected_col = st.selectbox(
                    "Spalte (z.B. Speicher-Variante)",
                    options=col_labels,
                    help="Wählen Sie eine Spalte für die Vorschau",
                    key="preview_col_selection"
                )
                result['column_label'] = selected_col
            
            # Beispiel-Berechnung
            if selected_row and selected_col:
                st.markdown("---")
                
                # Berechne Preis
                calc_result = calculate_product_price_from_matrix(
                    row_label=selected_row,
                    column_label=selected_col,
                    matrix_id=selected_matrix_id
                )
                
                if calc_result.is_valid():
                    # Erfolgreiche Berechnung
                    st.success(f"✓ Berechneter Preis: **{calc_result.total_price:,.2f} €**")
                    
                    # Details anzeigen
                    with st.expander("📋 Berechnungs-Details", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Basis-Informationen:**")
                            st.write(f"• Matrix: {calc_result.matrix_name}")
                            st.write(f"• Modus: {calc_result.pricing_mode}")
                            st.write(f"• Zeile verwendet: {calc_result.row_used}")
                            st.write(f"• Spalte verwendet: {calc_result.column_used}")
                            
                            if calc_result.row_floor_source:
                                st.info(f"ℹ️ Floor-Matching: Zeile '{selected_row}' → '{calc_result.row_floor_source}'")
                        
                        with col2:
                            st.write("**Preis-Aufschlüsselung:**")
                            st.write(f"• Basis-Preis: {calc_result.base_price:,.2f} €")
                            
                            if calc_result.pricing_mode == 'additiv':
                                if calc_result.accessories_price > 0:
                                    st.write(f"• Zubehör: {calc_result.accessories_price:,.2f} €")
                                if calc_result.misc_price > 0:
                                    st.write(f"• Sonstiges: {calc_result.misc_price:,.2f} €")
                            
                            st.write(f"**• Gesamt: {calc_result.total_price:,.2f} €**")
                    
                    result['price'] = calc_result.total_price
                
                else:
                    # Fehler bei Berechnung
                    st.error(f"❌ Fehler bei Preisberechnung: {calc_result.error}")
            
            # Preis-Tabelle anzeigen
            st.markdown("---")
            st.subheader("📊 Preis-Tabelle (Vorschau)")
            
            preview = get_price_preview(
                matrix_id=selected_matrix_id,
                max_rows=10,
                max_cols=10
            )
            
            if 'error' in preview:
                st.error(f"Fehler beim Laden der Vorschau: {preview['error']}")
            elif preview['prices']:
                # Erstelle DataFrame für Anzeige
                import pandas as pd
                
                rows = preview['rows']
                cols = preview['columns']
                prices = preview['prices']
                
                # Erstelle Daten-Matrix
                data = []
                for row in rows:
                    row_data = []
                    for col in cols:
                        price = prices.get((row, col))
                        if price is not None:
                            row_data.append(f"{price:,.2f} €")
                        else:
                            row_data.append("-")
                    data.append(row_data)
                
                df = pd.DataFrame(data, columns=cols, index=rows)
                df.index.name = "Zeile \\ Spalte"
                
                st.dataframe(df, use_container_width=True)
                
                if preview['truncated']:
                    st.info("ℹ️ Tabelle wurde gekürzt. Vollständige Matrix im 'Preis Matrix' Tab anzeigen.")
            else:
                st.info("Keine Preise in der Matrix vorhanden.")
    
    # Speichern-Button (optional)
    if on_save_callback:
        st.markdown("---")
        if st.button("💾 Konfiguration speichern", type="primary", use_container_width=True):
            on_save_callback(result)
            st.success("✓ Konfiguration gespeichert!")
    
    return result


def render_product_price_config_inline(
    product_data: Dict[str, Any],
    key_suffix: str = ""
) -> Dict[str, Any]:
    """
    Inline-Version der Produktpreis-Konfiguration für Formulare
    
    Args:
        product_data: Produkt-Daten Dictionary
        key_suffix: Suffix für eindeutige Widget-Keys
    
    Returns:
        Aktualisierte Produkt-Daten mit Preis-Konfiguration
    """
    
    # Extrahiere aktuelle Werte
    current_pricing_mode = product_data.get('pricing_mode', 'einzelpreis')
    current_price = product_data.get('preis_stück', 0.0)
    current_matrix_id = product_data.get('price_matrix_id')
    current_row_label = product_data.get('price_row_label')
    current_col_label = product_data.get('price_column_label')
    
    # Preismodus
    pricing_mode = st.radio(
        "Preismodus",
        options=["einzelpreis", "matrix"],
        format_func=lambda x: "📝 Einzelpreis" if x == "einzelpreis" else "📊 Matrix-Preis",
        horizontal=True,
        index=0 if current_pricing_mode == "einzelpreis" else 1,
        key=f"pricing_mode_{key_suffix}"
    )
    
    product_data['pricing_mode'] = pricing_mode
    
    if pricing_mode == "einzelpreis":
        # Einzelpreis
        price = st.number_input(
            "Preis (€)",
            min_value=0.0,
            value=float(current_price or 0.0),
            step=10.0,
            format="%.2f",
            key=f"price_{key_suffix}"
        )
        product_data['preis_stück'] = price
        product_data['price_matrix_id'] = None
        product_data['price_row_label'] = None
        product_data['price_column_label'] = None
    
    else:
        # Matrix-Preis
        matrices = list_matrices()
        
        if not matrices:
            st.warning("⚠️ Keine Preismatrizen verfügbar.")
            product_data['pricing_mode'] = 'einzelpreis'
            return product_data
        
        matrix_options = {m['id']: m['name'] for m in matrices}
        
        selected_matrix_id = st.selectbox(
            "Preismatrix",
            options=list(matrix_options.keys()),
            format_func=lambda x: matrix_options[x],
            index=list(matrix_options.keys()).index(current_matrix_id) if current_matrix_id in matrix_options else 0,
            key=f"matrix_{key_suffix}"
        )
        
        product_data['price_matrix_id'] = selected_matrix_id
        
        # Zeilen- und Spalten-Labels
        matrix_data = get_matrix_full(selected_matrix_id)
        if matrix_data:
            row_labels = [r['label'] for r in matrix_data['rows']]
            col_labels = [c['label'] for c in matrix_data['columns']]
            
            col1, col2 = st.columns(2)
            
            with col1:
                row_label = st.selectbox(
                    "Zeile",
                    options=row_labels,
                    index=row_labels.index(current_row_label) if current_row_label in row_labels else 0,
                    key=f"row_{key_suffix}"
                )
                product_data['price_row_label'] = row_label
            
            with col2:
                col_label = st.selectbox(
                    "Spalte",
                    options=col_labels,
                    index=col_labels.index(current_col_label) if current_col_label in col_labels else 0,
                    key=f"col_{key_suffix}"
                )
                product_data['price_column_label'] = col_label
            
            # Berechne und zeige Preis
            if row_label and col_label:
                calc_result = calculate_product_price_from_matrix(
                    row_label=row_label,
                    column_label=col_label,
                    matrix_id=selected_matrix_id
                )
                
                if calc_result.is_valid():
                    st.success(f"✓ Berechneter Preis: **{calc_result.total_price:,.2f} €**")
                    product_data['preis_stück'] = calc_result.total_price
                else:
                    st.error(f"❌ {calc_result.error}")
                    product_data['preis_stück'] = 0.0
    
    return product_data


__all__ = [
    'render_product_price_config_ui',
    'render_product_price_config_inline'
]
