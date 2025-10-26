"""Enhanced Product Management UI

Erweiterte Produktverwaltung mit vollständiger Unterstützung für alle Produktfelder,
dynamische Keys für PDF-Integration und Produktdatenbank-Reset-Funktionalität.
"""

import json

import pandas as pd
import streamlit as st

# Import product database functions
try:
    from product_db import (
        add_product,
        clear_all_products,
        delete_product,
        generate_product_dynamic_keys,
        get_product_by_id,
        get_product_with_dynamic_keys,
        get_products_with_dynamic_keys,
        list_product_categories,
        list_products,
        update_product,
    )
    PRODUCT_DB_AVAILABLE = True
except ImportError as e:
    st.error(f"Produktdatenbank nicht verfügbar: {e}")
    PRODUCT_DB_AVAILABLE = False


def show_enhanced_product_management():
    """Hauptfunktion für die erweiterte Produktverwaltung"""

    if not PRODUCT_DB_AVAILABLE:
        st.error(
            "Produktdatenbank-Modul nicht verfügbar. Bitte überprüfen Sie die Installation.")
        return

    st.title("🔧 Erweiterte Produktverwaltung")
    st.markdown("---")

    # Sidebar für Navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox("Seite auswählen:",
                            ["Produktliste",
                             "Produkt hinzufügen",
                             "Produkt bearbeiten",
                             "Dynamische Keys",
                             "Datenbank-Verwaltung"])

    if page == "Produktliste":
        show_product_list()
    elif page == "Produkt hinzufügen":
        show_add_product()
    elif page == "Produkt bearbeiten":
        show_edit_product()
    elif page == "Dynamische Keys":
        show_dynamic_keys()
    elif page == "Datenbank-Verwaltung":
        show_database_management()


def show_product_list():
    """Zeigt die Produktliste mit Filteroptionen"""
    st.header("📋 Produktliste")

    # Filter-Optionen
    col1, col2, col3 = st.columns(3)

    with col1:
        categories = list_product_categories()
        selected_category = st.selectbox(
            "Kategorie filtern:",
            ["Alle"] + categories
        )

    with col2:
        show_dynamic_keys_option = st.checkbox(
            "Dynamische Keys anzeigen", value=False)

    with col3:
        if st.button("🔄 Aktualisieren"):
            st.rerun()

    # Produkte laden
    try:
        if selected_category == "Alle":
            if show_dynamic_keys_option:
                products = get_products_with_dynamic_keys()
            else:
                products = list_products()
        else:
            if show_dynamic_keys_option:
                products = get_products_with_dynamic_keys(
                    category=selected_category)
            else:
                products = list_products(category=selected_category)

        if not products:
            st.info("Keine Produkte gefunden.")
            return

        st.success(f"{len(products)} Produkte gefunden")

        # Produkttabelle erstellen
        df_data = []
        for product in products:
            row = {
                "ID": product.get('id', ''),
                "Kategorie": product.get('category', ''),
                "Modellname": product.get('model_name', ''),
                "Marke": product.get('brand', ''),
                "Preis (€)": product.get('price_euro', 0.0),
                "Technologie": product.get('technology', ''),
                "Feature": product.get('feature', ''),
                "Design": product.get('design', ''),
                "Upgrade": product.get('upgrade', ''),
            }

            # Kategorie-spezifische Felder
            category = product.get('category', '').lower()
            if 'pv' in category or 'modul' in category:
                row["Leistung (W)"] = product.get('capacity_w', 0.0)
                row["Effizienz (%)"] = product.get('efficiency_percent', 0.0)
                row["Schatten-Fading"] = "Ja" if product.get(
                    'shadow_fading') else "Nein"
            elif 'wechselrichter' in category or 'inverter' in category:
                row["Leistung (kW)"] = product.get('power_kw', 0.0)
                row["Outdoor"] = "Ja" if product.get('outdoor_opt') else "Nein"
                row["Smart Home"] = "Ja" if product.get(
                    'smart_home') else "Nein"
            elif 'speicher' in category or 'battery' in category:
                row["Speicherleistung (kW)"] = product.get(
                    'storage_power_kw', 0.0)
                row["Max. Kapazität (kWh)"] = product.get(
                    'max_kwh_capacity', 0.0)
                row["Max. Zyklen"] = product.get('max_cycles', 0)

            df_data.append(row)

        df = pd.DataFrame(df_data)

        # Interaktive Tabelle
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # Aktionen für ausgewählte Produkte
        st.subheader("Aktionen")
        col1, col2 = st.columns(2)

        with col1:
            selected_id = st.number_input(
                "Produkt-ID für Aktion:", min_value=1, step=1)

        with col2:
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("🔍 Details anzeigen"):
                    show_product_details(selected_id)
            with action_col2:
                if st.button("🗑️ Löschen", type="secondary"):
                    if st.session_state.get('confirm_delete') != selected_id:
                        st.session_state.confirm_delete = selected_id
                        st.warning(
                            f"Klicken Sie erneut, um Produkt {selected_id} zu löschen!")
                    else:
                        if delete_product(selected_id):
                            st.success(
                                f"Produkt {selected_id} erfolgreich gelöscht!")
                            st.session_state.confirm_delete = None
                            st.rerun()
                        else:
                            st.error("Fehler beim Löschen des Produkts!")

    except Exception as e:
        st.error(f"Fehler beim Laden der Produkte: {e}")
        st.exception(e)


def show_product_details(product_id: int):
    """Zeigt detaillierte Produktinformationen"""
    try:
        product = get_product_with_dynamic_keys(product_id)
        if not product:
            st.error(f"Produkt mit ID {product_id} nicht gefunden!")
            return

        st.subheader(f"📄 Produktdetails: {product.get('model_name', 'N/A')}")

        # Grundinformationen
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Grunddaten:**")
            st.write(f"- ID: {product.get('id', 'N/A')}")
            st.write(f"- Kategorie: {product.get('category', 'N/A')}")
            st.write(f"- Modellname: {product.get('model_name', 'N/A')}")
            st.write(f"- Marke: {product.get('brand', 'N/A')}")
            st.write(f"- Preis: {product.get('price_euro', 0.0):.2f} €")
            st.write(
                f"- Berechnungsart: {product.get('calculate_per', 'N/A')}")

        with col2:
            st.write("**Erweiterte Eigenschaften:**")
            st.write(f"- Technologie: {product.get('technology', 'N/A')}")
            st.write(f"- Feature: {product.get('feature', 'N/A')}")
            st.write(f"- Design: {product.get('design', 'N/A')}")
            st.write(f"- Upgrade: {product.get('upgrade', 'N/A')}")
            st.write(f"- Garantie: {product.get('warranty_years', 0)} Jahre")
            st.write(
                f"- Herkunftsland: {product.get('origin_country', 'N/A')}")

        # Kategorie-spezifische Details
        category = product.get('category', '').lower()

        if 'pv' in category or 'modul' in category:
            st.write("**PV-Modul spezifisch:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"- Leistung: {product.get('capacity_w', 0.0)} W")
                st.write(
                    f"- Effizienz: {product.get('efficiency_percent', 0.0)} %")
                st.write(f"- Länge: {product.get('length_m', 0.0)} m")
                st.write(f"- Breite: {product.get('width_m', 0.0)} m")
            with col2:
                st.write(f"- Gewicht: {product.get('weight_kg', 0.0)} kg")
                st.write(
                    f"- Schatten-Fading: {'Ja' if product.get('shadow_fading') else 'Nein'}")

        elif 'wechselrichter' in category or 'inverter' in category:
            st.write("**Wechselrichter spezifisch:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"- Leistung: {product.get('power_kw', 0.0)} kW")
                st.write(
                    f"- Effizienz: {product.get('efficiency_percent', 0.0)} %")
                st.write(f"- Gewicht: {product.get('weight_kg', 0.0)} kg")
            with col2:
                st.write(
                    f"- Outdoor-Option: {'Ja' if product.get('outdoor_opt') else 'Nein'}")
                st.write(
                    f"- Eigenverbrauch: {'Ja' if product.get('self_supply_feature') else 'Nein'}")
                st.write(
                    f"- Schatten-Fading: {'Ja' if product.get('shadow_fading') else 'Nein'}")
                st.write(
                    f"- Smart Home: {'Ja' if product.get('smart_home') else 'Nein'}")

        elif 'speicher' in category or 'battery' in category:
            st.write("**Batteriespeicher spezifisch:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(
                    f"- Speicherleistung: {product.get('storage_power_kw', 0.0)} kW")
                st.write(
                    f"- Max. Kapazität: {product.get('max_kwh_capacity', 0.0)} kWh")
            with col2:
                st.write(f"- Max. Zyklen: {product.get('max_cycles', 0)}")
                st.write(f"- Gewicht: {product.get('weight_kg', 0.0)} kg")

        # Beschreibung
        if product.get('description'):
            st.write("**Beschreibung:**")
            st.write(product.get('description'))

        # Dynamische Keys anzeigen
        if 'dynamic_keys' in product and product['dynamic_keys']:
            with st.expander("🔑 Dynamische Keys für PDF"):
                st.json(product['dynamic_keys'])

    except Exception as e:
        st.error(f"Fehler beim Laden der Produktdetails: {e}")


def show_add_product():
    """Formular zum Hinzufügen neuer Produkte"""
    st.header("➕ Neues Produkt hinzufügen")

    with st.form("add_product_form"):
        # Grunddaten
        st.subheader("Grunddaten")
        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox("Kategorie *",
                                    ["PV Module",
                                     "Wechselrichter",
                                     "Batteriespeicher",
                                     "Montagesystem",
                                     "Kabel",
                                     "Zubehör",
                                     "Dienstleistung"],
                                    help="Produktkategorie auswählen")
            model_name = st.text_input(
                "Modellname *", help="Eindeutiger Modellname")
            brand = st.text_input("Marke", help="Herstellermarke")
            price_euro = st.number_input(
                "Preis (€)",
                min_value=0.0,
                step=0.01,
                help="Verkaufspreis in Euro")

        with col2:
            calculate_per = st.selectbox(
                "Berechnungsart",
                ["Stück", "Meter", "pauschal", "kWp"],
                help="Art der Preisberechnung"
            )
            warranty_years = st.number_input(
                "Garantie (Jahre)", min_value=0, step=1)
            weight_kg = st.number_input(
                "Gewicht (kg)", min_value=0.0, step=0.1)
            origin_country = st.text_input("Herkunftsland")

        # Erweiterte Eigenschaften
        st.subheader("Erweiterte Eigenschaften")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            technology = st.text_input(
                "Technologie", help="z.B. Monokristallin, MPPT")
        with col2:
            feature = st.text_input("Feature", help="Besondere Eigenschaften")
        with col3:
            design = st.text_input("Design", help="Design-Eigenschaften")
        with col4:
            upgrade = st.text_input("Upgrade", help="Upgrade-Optionen")

        # Kategorie-spezifische Felder
        category_lower = category.lower()

        if 'pv' in category_lower or 'modul' in category_lower:
            st.subheader("PV-Modul spezifische Eigenschaften")
            col1, col2, col3 = st.columns(3)

            with col1:
                capacity_w = st.number_input(
                    "Leistung (W)", min_value=0.0, step=1.0)
                efficiency_percent = st.number_input(
                    "Effizienz (%)", min_value=0.0, max_value=100.0, step=0.1)
            with col2:
                length_m = st.number_input(
                    "Länge (m)", min_value=0.0, step=0.01)
                width_m = st.number_input(
                    "Breite (m)", min_value=0.0, step=0.01)
            with col3:
                shadow_fading = st.checkbox(
                    "Schatten-Fading", help="Unterstützt Schatten-Fading")

            # Nicht relevante Felder auf None setzen
            power_kw = None
            storage_power_kw = None
            max_cycles = None
            max_kwh_capacity = None
            outdoor_opt = None
            self_supply_feature = None
            smart_home = None

        elif 'wechselrichter' in category_lower or 'inverter' in category_lower:
            st.subheader("Wechselrichter spezifische Eigenschaften")
            col1, col2, col3 = st.columns(3)

            with col1:
                power_kw = st.number_input(
                    "Leistung (kW)", min_value=0.0, step=0.1)
                efficiency_percent = st.number_input(
                    "Effizienz (%)", min_value=0.0, max_value=100.0, step=0.1)
            with col2:
                outdoor_opt = st.checkbox(
                    "Outdoor-Option", help="Für Außeninstallation geeignet")
                self_supply_feature = st.checkbox(
                    "Eigenverbrauch-Feature", help="Eigenverbrauchsoptimierung")
            with col3:
                shadow_fading = st.checkbox(
                    "Schatten-Fading", help="Unterstützt Schatten-Fading")
                smart_home = st.checkbox(
                    "Smart Home", help="Smart Home Integration")

            # Nicht relevante Felder auf None setzen
            capacity_w = None
            storage_power_kw = None
            max_cycles = None
            max_kwh_capacity = None
            length_m = None
            width_m = None

        elif 'speicher' in category_lower or 'battery' in category_lower:
            st.subheader("Batteriespeicher spezifische Eigenschaften")
            col1, col2, col3 = st.columns(3)

            with col1:
                storage_power_kw = st.number_input(
                    "Speicherleistung (kW)", min_value=0.0, step=0.1)
                max_kwh_capacity = st.number_input(
                    "Max. Kapazität (kWh)", min_value=0.0, step=0.1)
            with col2:
                max_cycles = st.number_input(
                    "Max. Zyklen", min_value=0, step=100)

            # Nicht relevante Felder auf None setzen
            capacity_w = None
            power_kw = None
            efficiency_percent = None
            length_m = None
            width_m = None
            outdoor_opt = None
            self_supply_feature = None
            shadow_fading = None
            smart_home = None

        else:
            # Für andere Kategorien alle spezifischen Felder auf None
            capacity_w = None
            power_kw = None
            storage_power_kw = None
            max_cycles = None
            max_kwh_capacity = None
            efficiency_percent = None
            length_m = None
            width_m = None
            outdoor_opt = None
            self_supply_feature = None
            shadow_fading = None
            smart_home = None

        # Beschreibung
        st.subheader("Beschreibung")
        description = st.text_area("Produktbeschreibung", height=100)

        # Submit Button
        submitted = st.form_submit_button("Produkt hinzufügen", type="primary")

        if submitted:
            if not model_name or not category:
                st.error("Modellname und Kategorie sind Pflichtfelder!")
                return

            # Produktdaten zusammenstellen
            product_data = {
                'category': category,
                'model_name': model_name,
                'brand': brand,
                'price_euro': price_euro,
                'calculate_per': calculate_per,
                'warranty_years': warranty_years,
                'weight_kg': weight_kg,
                'origin_country': origin_country,
                'technology': technology,
                'feature': feature,
                'design': design,
                'upgrade': upgrade,
                'description': description
            }

            # Kategorie-spezifische Felder hinzufügen (nur wenn nicht None)
            if capacity_w is not None:
                product_data['capacity_w'] = capacity_w
            if power_kw is not None:
                product_data['power_kw'] = power_kw
            if storage_power_kw is not None:
                product_data['storage_power_kw'] = storage_power_kw
            if max_cycles is not None:
                product_data['max_cycles'] = max_cycles
            if max_kwh_capacity is not None:
                product_data['max_kwh_capacity'] = max_kwh_capacity
            if efficiency_percent is not None:
                product_data['efficiency_percent'] = efficiency_percent
            if length_m is not None:
                product_data['length_m'] = length_m
            if width_m is not None:
                product_data['width_m'] = width_m
            if outdoor_opt is not None:
                product_data['outdoor_opt'] = 1 if outdoor_opt else 0
            if self_supply_feature is not None:
                product_data['self_supply_feature'] = 1 if self_supply_feature else 0
            if shadow_fading is not None:
                product_data['shadow_fading'] = 1 if shadow_fading else 0
            if smart_home is not None:
                product_data['smart_home'] = 1 if smart_home else 0

            try:
                product_id = add_product(product_data)
                if product_id:
                    st.success(
                        f"Produkt '{model_name}' erfolgreich mit ID {product_id} hinzugefügt!")

                    # Dynamische Keys anzeigen
                    product_with_keys = get_product_with_dynamic_keys(
                        product_id)
                    if product_with_keys and 'dynamic_keys' in product_with_keys:
                        with st.expander("🔑 Generierte dynamische Keys"):
                            st.json(product_with_keys['dynamic_keys'])
                else:
                    st.error("Fehler beim Hinzufügen des Produkts!")
            except Exception as e:
                st.error(f"Fehler beim Hinzufügen des Produkts: {e}")


def show_edit_product():
    """Formular zum Bearbeiten bestehender Produkte"""
    st.header("✏️ Produkt bearbeiten")

    # Produkt auswählen
    products = list_products()
    if not products:
        st.info("Keine Produkte zum Bearbeiten verfügbar.")
        return

    product_options = {f"{p['id']} - {p['model_name']}": p['id']
                       for p in products}
    selected_product_key = st.selectbox(
        "Produkt auswählen:", list(
            product_options.keys()))

    if not selected_product_key:
        return

    selected_product_id = product_options[selected_product_key]
    product = get_product_by_id(selected_product_id)

    if not product:
        st.error("Produkt nicht gefunden!")
        return

    st.info(f"Bearbeite: {product['model_name']}")

    # Ähnliches Formular wie beim Hinzufügen, aber mit vorausgefüllten Werten
    with st.form("edit_product_form"):
        # Grunddaten
        st.subheader("Grunddaten")
        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "Kategorie *",
                [
                    "PV Module",
                    "Wechselrichter",
                    "Batteriespeicher",
                    "Montagesystem",
                    "Kabel",
                    "Zubehör",
                    "Dienstleistung"],
                index=[
                    "PV Module",
                    "Wechselrichter",
                    "Batteriespeicher",
                    "Montagesystem",
                    "Kabel",
                    "Zubehör",
                    "Dienstleistung"].index(
                    product.get(
                        'category',
                        'PV Module')) if product.get('category') in [
                        "PV Module",
                        "Wechselrichter",
                        "Batteriespeicher",
                        "Montagesystem",
                        "Kabel",
                        "Zubehör",
                    "Dienstleistung"] else 0)
            model_name = st.text_input(
                "Modellname *",
                value=product.get(
                    'model_name',
                    ''))
            brand = st.text_input("Marke", value=product.get('brand', ''))
            price_euro = st.number_input(
                "Preis (€)",
                min_value=0.0,
                step=0.01,
                value=float(
                    product.get(
                        'price_euro',
                        0.0)))

        with col2:
            calculate_per = st.selectbox(
                "Berechnungsart", [
                    "Stück", "Meter", "pauschal", "kWp"], index=[
                    "Stück", "Meter", "pauschal", "kWp"].index(
                    product.get(
                        'calculate_per', 'Stück')) if product.get('calculate_per') in [
                        "Stück", "Meter", "pauschal", "kWp"] else 0)
            warranty_years = st.number_input(
                "Garantie (Jahre)",
                min_value=0,
                step=1,
                value=int(
                    product.get(
                        'warranty_years',
                        0)))
            weight_kg = st.number_input(
                "Gewicht (kg)",
                min_value=0.0,
                step=0.1,
                value=float(
                    product.get(
                        'weight_kg',
                        0.0)))
            origin_country = st.text_input(
                "Herkunftsland", value=product.get(
                    'origin_country', ''))

        # Erweiterte Eigenschaften
        st.subheader("Erweiterte Eigenschaften")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            technology = st.text_input(
                "Technologie", value=product.get(
                    'technology', ''))
        with col2:
            feature = st.text_input(
                "Feature", value=product.get(
                    'feature', ''))
        with col3:
            design = st.text_input("Design", value=product.get('design', ''))
        with col4:
            upgrade = st.text_input(
                "Upgrade", value=product.get(
                    'upgrade', ''))

        # Kategorie-spezifische Felder (ähnlich wie beim Hinzufügen, aber mit
        # Werten)
        category_lower = category.lower()

        if 'pv' in category_lower or 'modul' in category_lower:
            st.subheader("PV-Modul spezifische Eigenschaften")
            col1, col2, col3 = st.columns(3)

            with col1:
                capacity_w = st.number_input(
                    "Leistung (W)",
                    min_value=0.0,
                    step=1.0,
                    value=float(
                        product.get(
                            'capacity_w',
                            0.0)))
                efficiency_percent = st.number_input(
                    "Effizienz (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    value=float(
                        product.get(
                            'efficiency_percent',
                            0.0)))
            with col2:
                length_m = st.number_input(
                    "Länge (m)",
                    min_value=0.0,
                    step=0.01,
                    value=float(
                        product.get(
                            'length_m',
                            0.0)))
                width_m = st.number_input(
                    "Breite (m)",
                    min_value=0.0,
                    step=0.01,
                    value=float(
                        product.get(
                            'width_m',
                            0.0)))
            with col3:
                shadow_fading = st.checkbox(
                    "Schatten-Fading",
                    value=bool(
                        product.get(
                            'shadow_fading',
                            0)))

        # Beschreibung
        st.subheader("Beschreibung")
        description = st.text_area(
            "Produktbeschreibung",
            height=100,
            value=product.get(
                'description',
                ''))

        # Submit Button
        submitted = st.form_submit_button(
            "Änderungen speichern", type="primary")

        if submitted:
            if not model_name or not category:
                st.error("Modellname und Kategorie sind Pflichtfelder!")
                return

            # Update-Daten zusammenstellen
            update_data = {
                'category': category,
                'model_name': model_name,
                'brand': brand,
                'price_euro': price_euro,
                'calculate_per': calculate_per,
                'warranty_years': warranty_years,
                'weight_kg': weight_kg,
                'origin_country': origin_country,
                'technology': technology,
                'feature': feature,
                'design': design,
                'upgrade': upgrade,
                'description': description
            }

            # Kategorie-spezifische Felder
            if 'pv' in category_lower or 'modul' in category_lower:
                update_data.update({
                    'capacity_w': capacity_w,
                    'efficiency_percent': efficiency_percent,
                    'length_m': length_m,
                    'width_m': width_m,
                    'shadow_fading': 1 if shadow_fading else 0
                })

            try:
                if update_product(selected_product_id, update_data):
                    st.success(
                        f"Produkt '{model_name}' erfolgreich aktualisiert!")

                    # Aktualisierte dynamische Keys anzeigen
                    product_with_keys = get_product_with_dynamic_keys(
                        selected_product_id)
                    if product_with_keys and 'dynamic_keys' in product_with_keys:
                        with st.expander("🔑 Aktualisierte dynamische Keys"):
                            st.json(product_with_keys['dynamic_keys'])
                else:
                    st.error("Fehler beim Aktualisieren des Produkts!")
            except Exception as e:
                st.error(f"Fehler beim Aktualisieren des Produkts: {e}")


def show_dynamic_keys():
    """Zeigt dynamische Keys für alle Produkte"""
    st.header("🔑 Dynamische Keys für PDF-Integration")

    st.info("""
    Diese Seite zeigt die automatisch generierten dynamischen Keys für alle Produkte.
    Diese Keys können in PDF-Vorlagen verwendet werden, um Produktdaten automatisch einzufügen.
    """)

    # Produkt auswählen
    products = list_products()
    if not products:
        st.info("Keine Produkte verfügbar.")
        return

    product_options = {
        f"{p['id']} - {p['model_name']} ({p['category']})": p['id'] for p in products}
    selected_product_key = st.selectbox(
        "Produkt auswählen:",
        ["Alle Produkte"] +
        list(
            product_options.keys()))

    if selected_product_key == "Alle Produkte":
        # Alle Produkte mit Keys anzeigen
        st.subheader("Alle Produkte mit dynamischen Keys")

        products_with_keys = get_products_with_dynamic_keys()

        for product in products_with_keys:
            with st.expander(f"🔑 {product['model_name']} ({product['category']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Produktinfo:**")
                    st.write(f"- ID: {product.get('id')}")
                    st.write(f"- Kategorie: {product.get('category')}")
                    st.write(f"- Marke: {product.get('brand', 'N/A')}")
                    st.write(
                        f"- Preis: {product.get('price_euro', 0.0):.2f} €")

                with col2:
                    st.write("**Dynamische Keys:**")
                    if 'dynamic_keys' in product:
                        st.json(product['dynamic_keys'])
                    else:
                        st.write("Keine Keys generiert")

    else:
        # Einzelnes Produkt
        selected_product_id = product_options[selected_product_key]
        product_with_keys = get_product_with_dynamic_keys(selected_product_id)

        if not product_with_keys:
            st.error("Produkt nicht gefunden!")
            return

        st.subheader(f"Dynamische Keys für: {product_with_keys['model_name']}")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Produktinformationen:**")
            st.write(f"- **ID:** {product_with_keys.get('id')}")
            st.write(f"- **Kategorie:** {product_with_keys.get('category')}")
            st.write(
                f"- **Modellname:** {product_with_keys.get('model_name')}")
            st.write(f"- **Marke:** {product_with_keys.get('brand', 'N/A')}")
            st.write(
                f"- **Preis:** {product_with_keys.get('price_euro', 0.0):.2f} €")
            st.write(
                f"- **Technologie:** {product_with_keys.get('technology', 'N/A')}")
            st.write(
                f"- **Feature:** {product_with_keys.get('feature', 'N/A')}")

        with col2:
            st.write("**Generierte dynamische Keys:**")
            if 'dynamic_keys' in product_with_keys and product_with_keys['dynamic_keys']:
                # Keys als formatierte Tabelle anzeigen
                keys_data = []
                for key, value in product_with_keys['dynamic_keys'].items():
                    keys_data.append({"Key": key, "Wert": str(value)})

                keys_df = pd.DataFrame(keys_data)
                st.dataframe(
                    keys_df,
                    use_container_width=True,
                    hide_index=True)

                # JSON-Export Option
                if st.button("📋 Keys als JSON kopieren"):
                    st.code(
                        json.dumps(
                            product_with_keys['dynamic_keys'],
                            indent=2,
                            ensure_ascii=False))
            else:
                st.write("Keine dynamischen Keys verfügbar")

        # Beispiel für PDF-Verwendung
        st.subheader("💡 Verwendung in PDF-Vorlagen")
        st.info("""
        **Beispiel für die Verwendung in PDF-Vorlagen:**

        Die generierten Keys können in PDF-Vorlagen wie folgt verwendet werden:
        - `{{PRODUKTNAME_ID}}` - Produkt-ID
        - `{{PRODUKTNAME_MODEL_NAME}}` - Modellname
        - `{{PRODUKTNAME_PRICE_EURO}}` - Preis in Euro
        - `{{PRODUKTNAME_CAPACITY_W}}` - Leistung in Watt (für PV-Module)
        - `{{PRODUKTNAME_POWER_KW}}` - Leistung in kW (für Wechselrichter)

        Ersetzen Sie `PRODUKTNAME` durch den tatsächlichen Key-Präfix des Produkts.
        """)


def show_database_management():
    """Datenbank-Verwaltung mit Reset-Funktionalität"""
    st.header("🗄️ Datenbank-Verwaltung")

    st.warning(
        "⚠️ **Achtung:** Die Aktionen in diesem Bereich können nicht rückgängig gemacht werden!")

    # Statistiken anzeigen
    st.subheader("📊 Datenbankstatistiken")

    try:
        products = list_products()
        categories = list_product_categories()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Gesamtanzahl Produkte", len(products))

        with col2:
            st.metric("Anzahl Kategorien", len(categories))

        with col3:
            total_value = sum(p.get('price_euro', 0.0) for p in products)
            st.metric("Gesamtwert (€)", f"{total_value:.2f}")

        # Kategorieverteilung
        if categories:
            st.subheader("📈 Kategorieverteilung")
            category_counts = {}
            for product in products:
                cat = product.get('category', 'Unbekannt')
                category_counts[cat] = category_counts.get(cat, 0) + 1

            category_df = pd.DataFrame(
                list(
                    category_counts.items()),
                columns=[
                    'Kategorie',
                    'Anzahl'])
            st.bar_chart(category_df.set_index('Kategorie'))

    except Exception as e:
        st.error(f"Fehler beim Laden der Statistiken: {e}")

    st.markdown("---")

    # Produktdatenbank löschen
    st.subheader("🗑️ Produktdatenbank zurücksetzen")

    st.error("""
    **WARNUNG: Produktdatenbank komplett löschen**

    Diese Aktion wird ALLE Produkte aus der Datenbank entfernen!
    - Alle Produktdaten gehen verloren
    - Alle Preishistorien werden gelöscht
    - Die Aktion kann NICHT rückgängig gemacht werden

    Stellen Sie sicher, dass Sie ein Backup haben, bevor Sie fortfahren!
    """)

    # Doppelte Bestätigung
    col1, col2 = st.columns(2)

    with col1:
        confirm_text = st.text_input(
            "Geben Sie 'ALLE PRODUKTE LÖSCHEN' ein, um zu bestätigen:",
            help="Exakte Eingabe erforderlich"
        )

    with col2:
        final_confirm = st.checkbox(
            "Ich verstehe, dass diese Aktion nicht rückgängig gemacht werden kann",
            help="Finale Bestätigung erforderlich")

    # Reset-Button
    if st.button(
            "🗑️ PRODUKTDATENBANK KOMPLETT LÖSCHEN",
            type="secondary",
            disabled=not (
                confirm_text == "ALLE PRODUKTE LÖSCHEN" and final_confirm),
            help="Nur verfügbar nach Bestätigung"):
        if confirm_text == "ALLE PRODUKTE LÖSCHEN" and final_confirm:
            try:
                # Anzahl Produkte vor Löschung
                products_before = list_products()
                count_before = len(products_before)

                # Produktdatenbank löschen
                if clear_all_products():
                    st.success(
                        f"✅ Produktdatenbank erfolgreich zurückgesetzt! {count_before} Produkte wurden gelöscht.")

                    # Session State zurücksetzen
                    if 'confirm_delete' in st.session_state:
                        del st.session_state.confirm_delete

                    # Seite neu laden
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Zurücksetzen der Produktdatenbank!")

            except Exception as e:
                st.error(f"❌ Fehler beim Zurücksetzen der Datenbank: {e}")
                st.exception(e)
        else:
            st.error("Bestätigung nicht korrekt eingegeben!")

    # Export/Import Optionen (für zukünftige Erweiterung)
    st.markdown("---")
    st.subheader("📤 Export/Import (Zukünftige Funktion)")
    st.info("""
    **Geplante Funktionen:**
    - Export der Produktdatenbank als Excel/CSV
    - Import von Produkten aus Excel-Dateien
    - Backup und Wiederherstellung

    Diese Funktionen werden in einer zukünftigen Version implementiert.
    """)


if __name__ == "__main__":
    show_enhanced_product_management()
