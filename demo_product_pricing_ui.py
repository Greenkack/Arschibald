"""
Demo: Excel Product Pricing UI

Demonstriert die Verwendung der Produktpreis-Konfigurations-UI.
"""

import streamlit as st
from excel.excel_product_pricing_ui import (
    render_product_price_config_ui,
    render_product_price_config_inline
)
from price_matrix_store import (
    create_matrix,
    add_row,
    add_column,
    set_cell_value,
    set_active_matrix,
    delete_matrix,
    list_matrices
)


def setup_demo_matrix():
    """Erstellt eine Demo-Matrix falls keine vorhanden"""
    matrices = list_matrices()
    
    if not matrices:
        st.info("Erstelle Demo-Matrix...")
        
        # Erstelle Matrix
        matrix_id = create_matrix(
            "Demo PV-System Preise",
            "Beispiel-Preismatrix für PV-Systeme",
            pricing_mode='pauschal'
        )
        
        # Füge Zeilen hinzu (Modulanzahl)
        rows = {}
        for modules in [10, 15, 20, 25, 30]:
            rows[modules] = add_row(matrix_id, str(modules))
        
        # Füge Spalten hinzu (Speicher-Größen)
        cols = {}
        for storage in [5, 10, 15, 20]:
            cols[storage] = add_column(matrix_id, f"{storage}kWh")
        
        # Setze Preise (Basis: 500€ pro Modul + 1000€ pro kWh Speicher)
        for modules, row_id in rows.items():
            for storage, col_id in cols.items():
                price = modules * 500 + storage * 1000
                set_cell_value(matrix_id, row_id, col_id, float(price))
        
        # Setze als aktiv
        set_active_matrix(matrix_id)
        
        st.success("Demo-Matrix erstellt!")
        return matrix_id
    
    return matrices[0]['id']


def demo_standalone_ui():
    """Demo: Standalone UI-Komponente"""
    st.header("Demo 1: Standalone UI-Komponente")
    st.markdown("---")
    
    # Stelle sicher dass Demo-Matrix existiert
    setup_demo_matrix()
    
    # Beispiel-Produkt-Daten
    product_id = 123
    current_price = 15000.0
    current_pricing_mode = 'einzelpreis'
    
    st.write("**Beispiel-Produkt:**")
    st.write(f"• Produkt-ID: {product_id}")
    st.write(f"• Aktueller Preis: {current_price:,.2f} €")
    st.write(f"• Aktueller Modus: {current_pricing_mode}")
    
    st.markdown("---")
    
    # Callback-Funktion
    def on_save(config):
        st.session_state.saved_config = config
    
    # Rendere UI
    config = render_product_price_config_ui(
        product_id=product_id,
        current_price=current_price,
        current_pricing_mode=current_pricing_mode,
        on_save_callback=on_save
    )
    
    # Zeige Konfiguration
    if 'saved_config' in st.session_state:
        st.markdown("---")
        st.subheader(" Gespeicherte Konfiguration")
        st.json(st.session_state.saved_config)


def demo_inline_ui():
    """Demo: Inline UI für Formulare"""
    st.header("Demo 2: Inline UI für Formulare")
    st.markdown("---")
    
    # Stelle sicher dass Demo-Matrix existiert
    setup_demo_matrix()
    
    st.write("Diese Variante ist für die Integration in Produkt-Formulare gedacht.")
    
    # Beispiel-Produkt-Daten
    product_data = {
        'id': 456,
        'kategorie': 'PV System',
        'produkt_modell': 'Beispiel PV-System',
        'hersteller': 'Demo Hersteller',
        'preis_stück': 18000.0,
        'pricing_mode': 'einzelpreis',
        'price_matrix_id': None,
        'price_row_label': None,
        'price_column_label': None
    }
    
    st.write("**Beispiel-Produkt:**")
    st.json(product_data)
    
    st.markdown("---")
    
    # Formular
    with st.form("product_form"):
        st.subheader("Produkt bearbeiten")
        
        # Basis-Felder
        col1, col2 = st.columns(2)
        
        with col1:
            product_data['kategorie'] = st.text_input(
                "Kategorie",
                value=product_data['kategorie']
            )
            product_data['produkt_modell'] = st.text_input(
                "Produktmodell",
                value=product_data['produkt_modell']
            )
        
        with col2:
            product_data['hersteller'] = st.text_input(
                "Hersteller",
                value=product_data['hersteller']
            )
        
        st.markdown("---")
        
        # Preis-Konfiguration (Inline)
        product_data = render_product_price_config_inline(
            product_data,
            key_suffix="demo_form"
        )
        
        # Submit
        submitted = st.form_submit_button("Speichern", type="primary")
        
        if submitted:
            st.success("Produkt gespeichert!")
            st.json(product_data)


def demo_matrix_comparison():
    """Demo: Vergleich verschiedener Matrizen"""
    st.header("Demo 3: Matrix-Vergleich")
    st.markdown("---")
    
    # Erstelle mehrere Demo-Matrizen
    matrices = list_matrices()
    
    if len(matrices) < 2:
        st.info("Erstelle zusätzliche Demo-Matrizen für Vergleich...")
        
        # Matrix 1: Pauschal
        matrix1_id = create_matrix(
            "Pauschal-Preise Standard",
            "Standard Pauschalpreise",
            pricing_mode='pauschal'
        )
        
        for modules in [10, 20, 30]:
            row_id = add_row(matrix1_id, str(modules))
            for storage in [5, 10, 15]:
                col_id = add_column(matrix1_id, f"{storage}kWh")
                price = modules * 500 + storage * 1000
                set_cell_value(matrix1_id, row_id, col_id, float(price))
        
        # Matrix 2: Additiv
        matrix2_id = create_matrix(
            "Basis-Preise Additiv",
            "Basis-Preise ohne Zubehör",
            pricing_mode='additiv'
        )
        
        for modules in [10, 20, 30]:
            row_id = add_row(matrix2_id, str(modules))
            for storage in [5, 10, 15]:
                col_id = add_column(matrix2_id, f"{storage}kWh")
                price = modules * 400 + storage * 800  # Niedrigere Basis-Preise
                set_cell_value(matrix2_id, row_id, col_id, float(price))
        
        st.success("Demo-Matrizen erstellt!")
        st.rerun()
    
    # Zeige Vergleich
    matrices = list_matrices()
    
    st.write(f"**{len(matrices)} Matrizen verfügbar:**")
    
    for matrix in matrices:
        with st.expander(f"{matrix['name']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**ID:** {matrix['id']}")
                st.write(f"**Modus:** {matrix['pricing_mode']}")
            
            with col2:
                st.write(f"**Aktiv:** {'' if matrix['is_active'] else ''}")
                st.write(f"**Zubehör:** {'' if matrix['include_accessories'] else ''}")
            
            with col3:
                st.write(f"**Sonstiges:** {'' if matrix['include_misc'] else ''}")
            
            # Beispiel-Berechnung
            from excel.excel_product_pricing import calculate_product_price_from_matrix
            
            result = calculate_product_price_from_matrix(
                "20", "10kWh",
                matrix_id=matrix['id']
            )
            
            if result.is_valid():
                st.success(f"Beispiel (20 Module, 10kWh): **{result.total_price:,.2f} €**")
            else:
                st.error(f"Fehler: {result.error}")


def demo_cleanup():
    """Demo: Cleanup-Funktion"""
    st.header(" Cleanup")
    st.markdown("---")
    
    matrices = list_matrices()
    
    if matrices:
        st.write(f"**{len(matrices)} Demo-Matrizen gefunden:**")
        
        for matrix in matrices:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"• {matrix['name']} (ID: {matrix['id']})")
            
            with col2:
                if st.button("Löschen", key=f"delete_{matrix['id']}"):
                    if delete_matrix(matrix['id']):
                        st.success(f"Matrix {matrix['id']} gelöscht")
                        st.rerun()
    else:
        st.info("Keine Demo-Matrizen vorhanden.")


def main():
    """Hauptfunktion"""
    st.set_page_config(
        page_title="Product Pricing UI Demo",
        page_
        layout="wide"
    )
    
    st.title("Product Pricing UI - Demo")
    st.markdown("Demonstriert die Verwendung der Produktpreis-Konfigurations-UI")
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    demo_mode = st.sidebar.radio(
        "Demo auswählen",
        [
            "Standalone UI",
            "Inline UI (Formular)",
            "Matrix-Vergleich",
            "Cleanup"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Diese Demo zeigt verschiedene Verwendungsmöglichkeiten "
        "der Produktpreis-Konfigurations-UI."
    )
    
    # Zeige ausgewählte Demo
    if demo_mode == "Standalone UI":
        demo_standalone_ui()
    elif demo_mode == "Inline UI (Formular)":
        demo_inline_ui()
    elif demo_mode == "Matrix-Vergleich":
        demo_matrix_comparison()
    elif demo_mode == "Cleanup":
        demo_cleanup()


if __name__ == "__main__":
    main()
