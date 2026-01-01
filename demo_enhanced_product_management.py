"""Demo für erweiterte Produktverwaltung

Demonstriert die neuen Funktionen der erweiterten Produktdatenbank:
- Neue Spalten (technology, feature, design, upgrade, etc.)
- Dynamische Keys für PDF-Integration
- Produktdatenbank-Reset-Funktionalität
"""

import os
import sys

import streamlit as st

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Hauptfunktion der Demo-Anwendung"""

    st.set_page_config(
        page_title="Enhanced Product Management Demo",
        page_
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Enhanced Product Management Demo")
    st.markdown("---")

    st.markdown("""
    ## Neue Funktionen der erweiterten Produktverwaltung

    Diese Demo zeigt die vollständig implementierten Erweiterungen der Produktdatenbank:

    ### **1. Erweiterte Produktfelder**
    - **technology** - Technologie-Spezifikation
    - **feature** - Besondere Features
    - **design** - Design-Eigenschaften
    - **upgrade** - Upgrade-Optionen
    - **max_kwh_capacity** - Maximale kWh-Kapazität
    - **outdoor_opt** - Outdoor-Optimierung (Boolean)
    - **self_supply_feature** - Eigenverbrauch-Feature (Boolean)
    - **shadow_fading** - Schatten-Fading (Boolean)
    - **smart_home** - Smart Home Integration (Boolean)

    ###  **2. Dynamische Keys für PDF-Integration**

    **a) PV-Module Keys:**
    - id, category, model_name, brand, price_euro, calculate_per
    - capacity_w, warranty_years, technology, feature, design
    - shadow_fading, length_m, width_m, weight_kg, efficiency_percent
    - origin_country, description

    **b) Wechselrichter Keys:**
    - id, category, model_name, brand, price_euro, calculate_per
    - power_kw, warranty_years, technology, feature
    - outdoor_opt, self_supply_feature, shadow_fading, smart_home
    - weight_kg, efficiency_percent, origin_country, description

    **c) Batteriespeicher Keys:**
    - id, category, model_name, brand, price_euro, calculate_per
    - storage_power_kw, max_cycles, warranty_years, technology
    - feature, upgrade, max_kwh_capacity, weight_kg
    - origin_country, description

    ### **3. Produktdatenbank-Reset**
    - Komplette Löschung aller Produkte
    - Doppelte Sicherheitsabfrage
    - Statistiken und Backup-Hinweise
    """)

    st.markdown("---")

    # Navigation
    st.subheader("Demo starten")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            " Produktverwaltung öffnen",
            type="primary",
                use_container_width=True):
            st.info(
                "Die erweiterte Produktverwaltung wird in einem neuen Tab geöffnet...")
            st.markdown("""
            **Führen Sie folgenden Befehl aus:**
            ```bash
            streamlit run enhanced_product_management_ui.py
            ```
            """)

    with col2:
        if st.button(
            " Tests ausführen",
            type="secondary",
                use_container_width=True):
            st.info("Tests für die erweiterte Produktdatenbank...")
            st.markdown("""
            **Führen Sie folgenden Befehl aus:**
            ```bash
            python -m pytest tests/test_enhanced_product_db.py -v
            ```
            """)

    with col3:
        if st.button(" Dokumentation", use_container_width=True):
            show_documentation()


def show_documentation():
    """Zeigt die ausführliche Dokumentation"""

    st.markdown("---")
    st.header(" Ausführliche Dokumentation")

    # Implementierungsdetails
    with st.expander("Implementierungsdetails", expanded=True):
        st.markdown("""
        ### Datenbankschema-Erweiterungen

        Die Produktdatenbank wurde um folgende Spalten erweitert:

        ```sql
        ALTER TABLE products ADD COLUMN technology TEXT DEFAULT '';
        ALTER TABLE products ADD COLUMN feature TEXT DEFAULT '';
        ALTER TABLE products ADD COLUMN design TEXT DEFAULT '';
        ALTER TABLE products ADD COLUMN upgrade TEXT DEFAULT '';
        ALTER TABLE products ADD COLUMN max_kwh_capacity REAL DEFAULT 0.0;
        ALTER TABLE products ADD COLUMN outdoor_opt INTEGER DEFAULT 0;
        ALTER TABLE products ADD COLUMN self_supply_feature INTEGER DEFAULT 0;
        ALTER TABLE products ADD COLUMN shadow_fading INTEGER DEFAULT 0;
        ALTER TABLE products ADD COLUMN smart_home INTEGER DEFAULT 0;
        ```

        ### Neue Funktionen

        **1. `generate_product_dynamic_keys(product, category_specific=True)`**
        - Generiert dynamische Keys für alle Produktfelder
        - Kategorie-spezifische Key-Generierung
        - Automatische Formatierung für Boolean-Werte

        **2. `get_product_with_dynamic_keys(product_id, category_specific=True)`**
        - Lädt Produkt mit generierten dynamischen Keys
        - Direkt verwendbar für PDF-Integration

        **3. `clear_all_products()`**
        - Löscht alle Produkte aus der Datenbank
        - Setzt Auto-Increment-Zähler zurück
        - Umfassende Fehlerbehandlung
        """)

    # Verwendungsbeispiele
    with st.expander("Verwendungsbeispiele"):
        st.markdown("""
        ### Produkt mit neuen Feldern hinzufügen

        ```python
        from product_db import add_product

        pv_module_data = {
            'category': 'PV Module',
            'model_name': 'SolarMax Pro 450W',
            'brand': 'SolarTech',
            'price_euro': 220.0,
            'capacity_w': 450.0,
            'technology': 'Monokristallin N-Type',
            'feature': 'Bifacial',
            'design': 'All-Black Frame',
            'shadow_fading': 1,  # Boolean als Integer
            'efficiency_percent': 22.1,
            'warranty_years': 25
        }

        product_id = add_product(pv_module_data)
        ```

        ### Dynamische Keys generieren

        ```python
        from product_db import get_product_with_dynamic_keys

        # Produkt mit Keys laden
        product = get_product_with_dynamic_keys(product_id)

        # Keys für PDF verwenden
        pdf_data = product['dynamic_keys']
        # Beispiel: pdf_data['SOLARMAX_PRO_450W_CAPACITY_W'] = 450.0
        ```

        ### PDF-Template Integration

        ```html
        <!-- PDF Template Beispiel -->
        <h2>{{SOLARMAX_PRO_450W_MODEL_NAME}}</h2>
        <p>Leistung: {{SOLARMAX_PRO_450W_CAPACITY_W}} W</p>
        <p>Technologie: {{SOLARMAX_PRO_450W_TECHNOLOGY}}</p>
        <p>Schatten-Fading: {{SOLARMAX_PRO_450W_SHADOW_FADING_TEXT}}</p>
        <p>Preis: {{SOLARMAX_PRO_450W_PRICE_EURO}} €</p>
        ```
        """)

    # API-Referenz
    with st.expander(" API-Referenz"):
        st.markdown("""
        ### Neue Funktionen

        #### `generate_product_dynamic_keys(product, category_specific=True)`
        **Parameter:**
        - `product` (Dict): Produktdaten-Dictionary
        - `category_specific` (bool): Nur kategorie-spezifische Keys generieren

        **Rückgabe:** Dictionary mit dynamischen Keys

        #### `get_product_with_dynamic_keys(product_id, category_specific=True)`
        **Parameter:**
        - `product_id` (int): Produkt-ID
        - `category_specific` (bool): Nur kategorie-spezifische Keys generieren

        **Rückgabe:** Produkt-Dictionary mit 'dynamic_keys' Feld

        #### `get_products_with_dynamic_keys(category=None, company_id=None, category_specific=True)`
        **Parameter:**
        - `category` (str, optional): Kategorie-Filter
        - `company_id` (int, optional): Firmen-ID-Filter
        - `category_specific` (bool): Nur kategorie-spezifische Keys generieren

        **Rückgabe:** Liste von Produkten mit dynamischen Keys

        #### `clear_all_products()`
        **Parameter:** Keine

        **Rückgabe:** bool - True bei Erfolg, False bei Fehler

        **WARNUNG:** Löscht ALLE Produkte unwiderruflich!
        """)

    # Kategorie-spezifische Felder
    with st.expander(" Kategorie-spezifische Felder"):

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            ###  PV-Module
            **Spezifische Felder:**
            - `capacity_w` - Leistung in Watt
            - `efficiency_percent` - Wirkungsgrad
            - `length_m` - Länge in Metern
            - `width_m` - Breite in Metern
            - `shadow_fading` - Schatten-Fading (Boolean)

            **Dynamische Keys:**
            - `{NAME}_CAPACITY_W`
            - `{NAME}_EFFICIENCY_PERCENT`
            - `{NAME}_LENGTH_M`
            - `{NAME}_WIDTH_M`
            - `{NAME}_SHADOW_FADING_TEXT`
            """)

        with col2:
            st.markdown("""
            ### Wechselrichter
            **Spezifische Felder:**
            - `power_kw` - Leistung in kW
            - `outdoor_opt` - Outdoor-Option (Boolean)
            - `self_supply_feature` - Eigenverbrauch (Boolean)
            - `smart_home` - Smart Home (Boolean)
            - `efficiency_percent` - Wirkungsgrad

            **Dynamische Keys:**
            - `{NAME}_POWER_KW`
            - `{NAME}_OUTDOOR_OPT_TEXT`
            - `{NAME}_SELF_SUPPLY_FEATURE_TEXT`
            - `{NAME}_SMART_HOME_TEXT`
            - `{NAME}_EFFICIENCY_PERCENT`
            """)

        with col3:
            st.markdown("""
            ###  Batteriespeicher
            **Spezifische Felder:**
            - `storage_power_kw` - Speicherleistung in kW
            - `max_kwh_capacity` - Max. Kapazität in kWh
            - `max_cycles` - Maximale Zyklen
            - `upgrade` - Upgrade-Optionen

            **Dynamische Keys:**
            - `{NAME}_STORAGE_POWER_KW`
            - `{NAME}_MAX_KWH_CAPACITY`
            - `{NAME}_MAX_CYCLES`
            - `{NAME}_UPGRADE`
            """)

    # Sicherheitshinweise
    with st.expander(" Sicherheitshinweise"):
        st.markdown("""
        ### Produktdatenbank-Reset

        **WICHTIGE SICHERHEITSHINWEISE:**

        1. **Backup erstellen:** Erstellen Sie immer ein Backup vor dem Reset
        2. **Doppelte Bestätigung:** Der Reset erfordert explizite Textbestätigung
        3. **Unwiderruflich:** Gelöschte Daten können nicht wiederhergestellt werden
        4. **Produktionsumgebung:** Besondere Vorsicht in Produktionsumgebungen

        ### Empfohlenes Vorgehen:

        ```python
        # 1. Backup erstellen (manuell)
        # Exportieren Sie die Datenbank vor dem Reset

        # 2. Reset nur nach Bestätigung
        if user_confirms_reset():
            clear_all_products()

        # 3. Neue Daten importieren
        # Importieren Sie neue Produktdaten nach dem Reset
        ```
        """)


if __name__ == "__main__":
    main()
