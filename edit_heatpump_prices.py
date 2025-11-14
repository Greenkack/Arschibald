#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Admin-Tool: Wärmepumpen-Preise in product_db.py bearbeiten
"""

import streamlit as st
from product_db import get_db_connection, get_product_by_model_name
from heatpump_products_database import HEATPUMP_PRODUCTS

def render_price_editor():
    st.title("[MONEY] Wärmepumpen-Preise bearbeiten")
    st.caption("Bearbeite Preise direkt in der Produktdatenbank (product_db.py)")
    st.markdown("---")
    
    # Wähle Hersteller
    manufacturers = list(HEATPUMP_PRODUCTS.keys())
    selected_manufacturer = st.selectbox("Hersteller", manufacturers)
    
    # Wähle Typ
    types = list(HEATPUMP_PRODUCTS[selected_manufacturer].keys())
    selected_type = st.selectbox("Typ", types)
    
    # Wähle Modell
    models = HEATPUMP_PRODUCTS[selected_manufacturer][selected_type]
    model_names = [m['model'] for m in models]
    selected_model_name = st.selectbox("Modell", model_names)
    
    # Lade Produkt aus Datenbank
    db_product = get_product_by_model_name(selected_model_name)
    
    if db_product is None:
        st.error(f"[ERROR] Produkt '{selected_model_name}' nicht in Datenbank gefunden!")
        st.warning("[WARNING] Führe zuerst 'python import_heatpumps_to_db.py' aus!")
        return
    
    st.success(f"[OK] Produkt gefunden: {selected_model_name}")
    
    # Zeige aktuelle Daten
    st.markdown("### [CHART] Aktuelle Daten")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Aktueller Preis", f"{db_product.get('price_euro', 0):.2f} €")
        st.caption(f"Kategorie: {db_product.get('category', 'N/A')}")
        st.caption(f"Rating: {db_product.get('rating', 0):.1f}/5.0")
    
    with col2:
        st.caption(f"ID: {db_product.get('id', 'N/A')}")
        st.caption(f"Hersteller: {db_product.get('manufacturer', 'N/A')}")
        st.caption(f"Beschreibung: {db_product.get('description', 'N/A')[:50]}...")
    
    # Bearbeite Preis
    st.markdown("### ✏️ Preis bearbeiten")
    
    new_price = st.number_input(
        "Neuer Preis (€)",
        min_value=0.0,
        value=float(db_product.get('price_euro', 0)),
        step=100.0,
        help="Gerätepreis netto (ohne Installation)"
    )
    
    installation_factor = st.slider(
        "Installationsfaktor",
        min_value=0.0,
        max_value=1.0,
        value=0.4,
        step=0.05,
        help="Faktor für Installationskosten (0.4 = 40% vom Gerätepreis)"
    )
    
    # Berechne Gesamtpreis
    installation_price = new_price * installation_factor
    total_price = new_price + installation_price
    
    st.info(f"""
    **Preisberechnung:**
    - Gerät: {new_price:,.2f} €
    - Installation ({installation_factor*100:.0f}%): {installation_price:,.2f} €
    - **Gesamt: {total_price:,.2f} €**
    """)
    
    # Speichern-Button
    if st.button("💾 Preis speichern", type="primary", use_container_width=True):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE products
                SET price_euro = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE model_name = ?
            """, (new_price, selected_model_name))
            
            conn.commit()
            conn.close()
            
            st.success(f"[OK] Preis für '{selected_model_name}' erfolgreich aktualisiert!")
            st.balloons()
            st.rerun()
            
        except Exception as e:
            st.error(f"[ERROR] Fehler beim Speichern: {e}")

if __name__ == "__main__":
    render_price_editor()
