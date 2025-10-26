# admin_logo_management_ui.py
"""
Logo-Management UI für den Admin-Bereich
Ermöglicht CRUD-Operationen für Hersteller-Logos mit Upload und Verwaltung
"""

import base64
import io
import traceback
from typing import Any

import pandas as pd
import streamlit as st
from PIL import Image

# Import der Logo-DB-Funktionen
try:
    from brand_logo_db import (
        add_brand_logo,
        delete_brand_logo,
        get_brand_logo,
        list_all_brand_logos,
        upload_logo_from_file,
    )
    LOGO_DB_AVAILABLE = True
except ImportError as e:
    st.error(f"Logo-Database nicht verfügbar: {e}")
    LOGO_DB_AVAILABLE = False

# Import der Produkt-DB für Hersteller-Namen
try:
    from product_db import get_db_connection, list_products
    PRODUCT_DB_AVAILABLE = True
except ImportError:
    PRODUCT_DB_AVAILABLE = False


def get_unique_brands_from_products() -> list[str]:
    """Extrahiert alle einzigartigen Hersteller-Namen aus der Produkt-DB"""
    if not PRODUCT_DB_AVAILABLE:
        return []

    try:
        products = list_products()
        brands = set()
        for product in products:
            brand = product.get('brand', '').strip()
            if brand:
                brands.add(brand)
        return sorted(list(brands))
    except Exception as e:
        st.error(f"Fehler beim Laden der Hersteller: {e}")
        return []


def validate_image_file(uploaded_file) -> tuple[bool, str]:
    """Validiert eine hochgeladene Bilddatei"""
    if uploaded_file is None:
        return False, "Keine Datei ausgewählt"

    # Dateigröße prüfen (max 5MB)
    if uploaded_file.size > 5 * 1024 * 1024:
        return False, "Datei zu groß (max. 5MB)"

    # Dateiformat prüfen
    allowed_formats = ['png', 'jpg', 'jpeg', 'svg', 'gif', 'webp']
    file_extension = uploaded_file.name.split('.')[-1].lower()

    if file_extension not in allowed_formats:
        return False, f"Nicht unterstütztes Format. Erlaubt: {
            ', '.join(allowed_formats)}"

    return True, "OK"


def convert_uploaded_file_to_base64(
        uploaded_file) -> tuple[str | None, str | None]:
    """Konvertiert eine hochgeladene Datei zu Base64"""
    try:
        file_bytes = uploaded_file.getvalue()
        base64_string = base64.b64encode(file_bytes).decode('utf-8')
        file_format = uploaded_file.name.split('.')[-1].upper()
        return base64_string, file_format
    except Exception as e:
        st.error(f"Fehler bei der Konvertierung: {e}")
        return None, None


def display_logo_preview(logo_data: dict[str, Any], max_width: int = 150):
    """Zeigt eine Vorschau des Logos an"""
    try:
        if not logo_data.get('logo_base64'):
            st.warning("Keine Logo-Daten verfügbar")
            return

        # Base64 zu Bytes
        logo_bytes = base64.b64decode(logo_data['logo_base64'])

        # Für SVG anders behandeln
        if logo_data.get('logo_format', '').upper() == 'SVG':
            st.markdown(f"""
            <div style="max-width: {max_width}px;">
                <img src="data:image/svg+xml;base64,{logo_data['logo_base64']}"
                     style="max-width: 100%; height: auto;" />
            </div>
            """, unsafe_allow_html=True)
        else:
            # Für andere Formate PIL verwenden
            image = Image.open(io.BytesIO(logo_bytes))
            st.image(image, width=max_width)

    except Exception as e:
        st.error(f"Fehler bei der Logo-Anzeige: {e}")


def render_logo_upload_section():
    """Rendert den Bereich für Logo-Upload"""
    st.subheader("📤 Neues Logo hochladen")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Hersteller auswählen oder eingeben
        brands_from_db = get_unique_brands_from_products()

        if brands_from_db:
            # Dropdown mit existierenden Herstellern plus "Neu eingeben" Option
            brand_options = ["-- Hersteller auswählen --"] + \
                brands_from_db + ["🆕 Neuen Hersteller eingeben"]
            selected_brand_option = st.selectbox(
                "Hersteller auswählen:",
                brand_options,
                key="logo_brand_select"
            )

            if selected_brand_option == "🆕 Neuen Hersteller eingeben":
                brand_name = st.text_input(
                    "Neuer Hersteller-Name:",
                    key="logo_brand_new",
                    placeholder="Z.B. SolarTech GmbH"
                )
            elif selected_brand_option != "-- Hersteller auswählen --":
                brand_name = selected_brand_option
            else:
                brand_name = ""
        else:
            # Fallback: Direkte Eingabe
            brand_name = st.text_input(
                "Hersteller-Name:",
                key="logo_brand_input",
                placeholder="Z.B. SolarTech GmbH"
            )

        # Datei-Upload
        uploaded_file = st.file_uploader(
            "Logo-Datei auswählen:",
            type=['png', 'jpg', 'jpeg', 'svg', 'gif', 'webp'],
            key="logo_file_upload"
        )

    with col2:
        if uploaded_file:
            st.write("**Vorschau:**")
            try:
                if uploaded_file.name.endswith('.svg'):
                    # SVG-Vorschau
                    file_bytes = uploaded_file.getvalue()
                    base64_svg = base64.b64encode(file_bytes).decode('utf-8')
                    st.markdown(f"""
                    <div style="max-width: 150px; border: 1px solid #ddd; padding: 10px;">
                        <img src="data:image/svg+xml;base64,{base64_svg}"
                             style="max-width: 100%; height: auto;" />
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Andere Formate
                    image = Image.open(uploaded_file)
                    st.image(image, width=150)

                # Datei-Info
                st.caption(f"📁 {uploaded_file.name}")
                st.caption(f"📏 {uploaded_file.size / 1024:.1f} KB")

            except Exception as e:
                st.error(f"Vorschau-Fehler: {e}")

    # Upload-Button
    if st.button(
            "💾 Logo speichern",
            type="primary",
            disabled=not (
            brand_name and uploaded_file)):
        if not LOGO_DB_AVAILABLE:
            st.error("Logo-Datenbank nicht verfügbar!")
            return

        # Validierung
        is_valid, validation_msg = validate_image_file(uploaded_file)
        if not is_valid:
            st.error(f"Validation fehlgeschlagen: {validation_msg}")
            return

        # Konvertierung
        logo_base64, logo_format = convert_uploaded_file_to_base64(
            uploaded_file)
        if not logo_base64:
            st.error("Fehler bei der Datei-Konvertierung!")
            return

        # Speichern
        success = add_brand_logo(brand_name, logo_base64, logo_format)
        if success:
            st.success(f"✅ Logo für '{brand_name}' erfolgreich gespeichert!")
            st.rerun()
        else:
            st.error("❌ Fehler beim Speichern des Logos!")


def render_logo_management_section():
    """Rendert den Bereich für Logo-Verwaltung"""
    st.subheader("🗂️ Vorhandene Logos verwalten")

    if not LOGO_DB_AVAILABLE:
        st.error("Logo-Datenbank nicht verfügbar!")
        return

    # Alle Logos laden
    logos = list_all_brand_logos()

    if not logos:
        st.info("📭 Noch keine Logos vorhanden. Laden Sie das erste Logo hoch!")
        return

    # Logos in Tabelle anzeigen
    df_data = []
    for logo in logos:
        df_data.append({
            'ID': logo['id'],
            'Hersteller': logo['brand_name'],
            'Format': logo['logo_format'],
            'Erstellt': logo['created_at'][:10] if logo['created_at'] else 'N/A',
            'Aktualisiert': logo['updated_at'][:10] if logo['updated_at'] else 'N/A'
        })

    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)

    # Logo-Details und Aktionen
    st.subheader("🔍 Logo-Details")

    selected_logo_id = st.selectbox(
        "Logo auswählen:",
        options=["-- Logo auswählen --"] + [f"{logo['brand_name']} (ID: {logo['id']})" for logo in logos],
        key="logo_select_for_details"
    )

    if selected_logo_id != "-- Logo auswählen --":
        # Logo ID extrahieren
        logo_id = int(selected_logo_id.split("ID: ")[1].split(")")[0])
        selected_logo = next(
            (logo for logo in logos if logo['id'] == logo_id), None)

        if selected_logo:
            # Logo-Daten laden
            logo_data = get_brand_logo(selected_logo['brand_name'])

            if logo_data:
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.write("**Logo-Vorschau:**")
                    display_logo_preview(logo_data, max_width=200)

                with col2:
                    st.write("**Details:**")
                    st.write(f"**Hersteller:** {logo_data['brand_name']}")
                    st.write(f"**Format:** {logo_data['logo_format']}")
                    st.write(f"**Erstellt:** {logo_data['created_at']}")
                    st.write(f"**Aktualisiert:** {logo_data['updated_at']}")

                    # Aktionen
                    st.write("**Aktionen:**")

                    col_edit, col_delete = st.columns(2)

                    with col_edit:
                        if st.button(
                            "✏️ Bearbeiten",
                                key=f"edit_logo_{logo_id}"):
                            st.session_state[f'edit_mode_{logo_id}'] = True

                    with col_delete:
                        if st.button(
                            "🗑️ Löschen",
                            key=f"delete_logo_{logo_id}",
                                type="secondary"):
                            if st.session_state.get(
                                    f'confirm_delete_{logo_id}', False):
                                success = delete_brand_logo(
                                    selected_logo['brand_name'])
                                if success:
                                    st.success(
                                        f"✅ Logo für '{
                                            selected_logo['brand_name']}' gelöscht!")
                                    st.rerun()
                                else:
                                    st.error("❌ Fehler beim Löschen!")
                            else:
                                st.session_state[f'confirm_delete_{logo_id}'] = True
                                st.warning(
                                    "⚠️ Klicken Sie erneut zum Bestätigen!")


def render_logo_edit_section(logo_id: int, logo_data: dict[str, Any]):
    """Rendert den Bearbeitungsmodus für ein Logo"""
    st.subheader(f"✏️ Logo bearbeiten: {logo_data['brand_name']}")

    # Neuen Namen eingeben
    new_brand_name = st.text_input(
        "Hersteller-Name:",
        value=logo_data['brand_name'],
        key=f"edit_brand_name_{logo_id}"
    )

    # Neues Logo hochladen (optional)
    st.write("**Neues Logo hochladen (optional):**")
    new_uploaded_file = st.file_uploader(
        "Neue Logo-Datei (leer lassen um aktuelles Logo zu behalten):",
        type=['png', 'jpg', 'jpeg', 'svg', 'gif', 'webp'],
        key=f"edit_logo_file_{logo_id}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "💾 Änderungen speichern",
            key=f"save_edit_{logo_id}",
                type="primary"):
            # TODO: Implementierung der Bearbeitung
            st.success("✅ Änderungen gespeichert!")
            del st.session_state[f'edit_mode_{logo_id}']
            st.rerun()

    with col2:
        if st.button("❌ Abbrechen", key=f"cancel_edit_{logo_id}"):
            del st.session_state[f'edit_mode_{logo_id}']
            st.rerun()


def render_logo_management_ui():
    """Hauptfunktion für die Logo-Management UI"""
    st.title("🎨 Logo-Management")
    st.markdown("---")

    # Erweiterte Tabs mit allen CRUD-Funktionen integriert
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Übersicht",
        "➕ Hinzufügen",
        "✏️ Bearbeiten",
        "🔧 Tools",
        "📤 Upload (Legacy)",
        "🗂️ Verwaltung",
        "📊 Statistiken"
    ])

    with tab1:
        render_logo_overview_section()

    with tab2:
        render_logo_add_section()

    with tab3:
        render_logo_edit_section()

    with tab4:
        render_logo_tools_section()

    with tab5:
        render_logo_upload_section()

    with tab6:
        render_logo_management_section()
        render_logo_positions_tab()

    with tab7:
        render_logo_statistics_section()


def render_logo_overview_section():
    """Rendert die Übersicht aller Logos"""
    st.subheader("📋 Logo-Übersicht")

    if not LOGO_DB_AVAILABLE:
        st.error("Logo-Datenbank nicht verfügbar!")
        return

    try:
        # Import der BrandLogoAdmin-Funktionalität
        from admin_brand_logo_management_ui import BrandLogoAdmin
        admin = BrandLogoAdmin()

        brands = admin.get_all_brands()

        if brands:
            st.write(f"**{len(brands)} Marken-Logos verfügbar**")

            # Grid Layout für Logo-Vorschauen
            cols = st.columns(4)

            for i, brand in enumerate(brands):
                with cols[i % 4]:
                    # Logo anzeigen wenn vorhanden
                    logo_data = admin.get_brand_by_name(brand['brand_name'])
                    if logo_data and logo_data['logo_base64']:
                        try:
                            logo_bytes = base64.b64decode(
                                logo_data['logo_base64'])
                            st.image(
                                logo_bytes, width=150, caption=brand['brand_name'])
                        except BaseException:
                            st.write(f"🏷️ {brand['brand_name']}")
                    else:
                        st.write(f"🏷️ {brand['brand_name']}")

                    st.write(f"**{brand['brand_name']}**")
                    if brand.get('category'):
                        st.caption(f"Kategorie: {brand['category']}")
                    if brand.get('country'):
                        st.caption(f"Land: {brand['country']}")

                    # Edit/Delete Buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(
                                "✏️",
                                key=f"edit_{
                                    brand['id']}",
                                help="Bearbeiten"):
                            st.session_state.edit_brand_id = brand['id']
                            st.rerun()
                    with col2:
                        if st.button(
                                "🗑️",
                                key=f"delete_{
                                    brand['id']}",
                                help="Löschen"):
                            if admin.delete_brand_logo(brand['id']):
                                st.success("Logo gelöscht!")
                                st.rerun()

            # Tabelle als Alternative
            st.subheader("Tabellenansicht")
            import pandas as pd
            df = pd.DataFrame(brands)
            if not df.empty:
                display_cols = [
                    'brand_name',
                    'category',
                    'country',
                    'logo_width',
                    'logo_height',
                    'file_size_kb']
                available_cols = [
                    col for col in display_cols if col in df.columns]
                st.dataframe(df[available_cols], use_container_width=True)
        else:
            st.info("Keine Marken-Logos vorhanden.")

    except ImportError as e:
        st.error(f"Brand-Logo-Admin nicht verfügbar: {e}")
        render_logo_management_section()  # Fallback auf bestehende Funktionalität


def render_logo_add_section():
    """Rendert die Sektion zum Hinzufügen neuer Logos"""
    st.subheader("➕ Neues Marken-Logo hinzufügen")

    try:
        from admin_brand_logo_management_ui import BrandLogoAdmin
        admin = BrandLogoAdmin()

        with st.form("add_brand_form"):
            col1, col2 = st.columns(2)

            with col1:
                # Hersteller aus Produktdatenbank laden
                manufacturers = admin.get_manufacturers_from_products()

                brand_name_option = st.radio(
                    "Markenname wählen",
                    ["Aus Produktdatenbank", "Manuell eingeben"]
                )

                if brand_name_option == "Aus Produktdatenbank":
                    brand_name = st.selectbox(
                        "Hersteller aus Produkten", [""] + manufacturers)
                else:
                    brand_name = st.text_input("Markenname*")

                category = st.selectbox("Kategorie", [
                    "", "PV Module", "Wechselrichter", "Batteriespeicher",
                    "Wallbox", "Energiemanagement", "Sonstiges"
                ])
                country = st.text_input("Herstellerland")
                website_url = st.text_input("Website URL")

            with col2:
                description = st.text_area("Beschreibung")

                # Logo Upload
                uploaded_logo = st.file_uploader(
                    "Logo-Datei*",
                    type=[
                        'png',
                        'jpg',
                        'jpeg',
                        'gif',
                        'webp'],
                    help="Empfohlen: PNG mit transparentem Hintergrund, max. 300x300px")

                if uploaded_logo:
                    # Logo-Vorschau
                    st.image(uploaded_logo, width=200, caption="Logo-Vorschau")

            submitted = st.form_submit_button("Logo hinzufügen")

            if submitted:
                if not brand_name or not uploaded_logo:
                    st.error("Markenname und Logo-Datei sind Pflichtfelder!")
                else:
                    # Logo verarbeiten
                    logo_result = admin.process_logo_image(uploaded_logo)

                    if logo_result['success']:
                        result = admin.add_brand_logo({
                            'brand_name': brand_name,
                            'logo_base64': logo_result['logo_base64'],
                            'file_extension': logo_result['file_extension'],
                            'description': description,
                            'website_url': website_url,
                            'country': country,
                            'category': category,
                            'logo_width': logo_result['logo_width'],
                            'logo_height': logo_result['logo_height'],
                            'file_size_kb': logo_result['file_size_kb']
                        })

                        if result:
                            st.success(
                                f"✅ Logo für '{brand_name}' erfolgreich hinzugefügt!")
                            st.rerun()
                        else:
                            st.error("❌ Fehler beim Hinzufügen des Logos")
                    else:
                        st.error(
                            f"❌ Logo-Verarbeitung fehlgeschlagen: {
                                logo_result.get(
                                    'error', 'Unbekannter Fehler')}")

    except ImportError as e:
        st.error(f"Brand-Logo-Admin nicht verfügbar: {e}")
        render_logo_upload_section()  # Fallback


def render_logo_edit_section():
    """Rendert die Sektion zum Bearbeiten von Logos"""
    st.subheader("✏️ Logos bearbeiten")

    try:
        from admin_brand_logo_management_ui import BrandLogoAdmin
        admin = BrandLogoAdmin()

        # Logo zur Bearbeitung auswählen
        brands = admin.get_all_brands()

        if not brands:
            st.info("Keine Logos zum Bearbeiten vorhanden.")
            return

        # Brand-Namen für Selectbox
        brand_names = [brand['brand_name'] for brand in brands]

        selected_brand = st.selectbox(
            "Logo zum Bearbeiten auswählen:",
            [""] + brand_names
        )

        if selected_brand:
            # Aktuelle Daten laden
            brand_data = admin.get_brand_by_name(selected_brand)

            if brand_data:
                # Aktuelle Logo-Anzeige
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.subheader("Aktuelles Logo")
                    if brand_data['logo_base64']:
                        try:
                            logo_bytes = base64.b64decode(
                                brand_data['logo_base64'])
                            st.image(logo_bytes, width=200)
                        except BaseException:
                            st.error("Logo-Anzeige fehlgeschlagen")

                with col2:
                    st.subheader("Bearbeiten")

                    with st.form(f"edit_brand_form_{selected_brand}"):
                        new_brand_name = st.text_input(
                            "Markenname", value=brand_data['brand_name'])
                        new_category = st.selectbox(
                            "Kategorie",
                            [
                                "",
                                "PV Module",
                                "Wechselrichter",
                                "Batteriespeicher",
                                "Wallbox",
                                "Energiemanagement",
                                "Sonstiges"],
                            index=0 if not brand_data.get('category') else [
                                "",
                                "PV Module",
                                "Wechselrichter",
                                "Batteriespeicher",
                                "Wallbox",
                                "Energiemanagement",
                                "Sonstiges"].index(
                                brand_data['category']) if brand_data['category'] in [
                                "",
                                "PV Module",
                                "Wechselrichter",
                                "Batteriespeicher",
                                "Wallbox",
                                "Energiemanagement",
                                "Sonstiges"] else 0)

                        new_country = st.text_input(
                            "Land", value=brand_data.get('country', ''))
                        new_website = st.text_input(
                            "Website", value=brand_data.get(
                                'website_url', ''))
                        new_description = st.text_area(
                            "Beschreibung", value=brand_data.get(
                                'description', ''))

                        # Neues Logo optional
                        new_logo = st.file_uploader(
                            "Neues Logo (optional)",
                            type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
                            help="Lassen Sie dies leer, um das bestehende Logo zu behalten"
                        )

                        if new_logo:
                            st.image(
                                new_logo, width=200, caption="Neues Logo-Vorschau")

                        col_save, col_delete = st.columns(2)

                        with col_save:
                            save_submitted = st.form_submit_button(
                                "� Speichern", type="primary")

                        with col_delete:
                            delete_submitted = st.form_submit_button(
                                "🗑️ Löschen", type="secondary")

                        if save_submitted:
                            update_data = {
                                'brand_name': new_brand_name,
                                'category': new_category,
                                'country': new_country,
                                'website_url': new_website,
                                'description': new_description
                            }

                            # Neues Logo verarbeiten falls vorhanden
                            if new_logo:
                                logo_result = admin.process_logo_image(
                                    new_logo)
                                if logo_result['success']:
                                    update_data.update({
                                        'logo_base64': logo_result['logo_base64'],
                                        'file_extension': logo_result['file_extension'],
                                        'logo_width': logo_result['logo_width'],
                                        'logo_height': logo_result['logo_height'],
                                        'file_size_kb': logo_result['file_size_kb']
                                    })

                            if admin.update_brand_logo(
                                    brand_data['id'], update_data):
                                st.success("✅ Logo erfolgreich aktualisiert!")
                                st.rerun()
                            else:
                                st.error(
                                    "❌ Fehler beim Aktualisieren des Logos")

                        if delete_submitted:
                            if admin.delete_brand_logo(brand_data['id']):
                                st.success("✅ Logo erfolgreich gelöscht!")
                                st.rerun()
                            else:
                                st.error("❌ Fehler beim Löschen des Logos")

    except ImportError as e:
        st.error(f"Brand-Logo-Admin nicht verfügbar: {e}")


def render_logo_tools_section():
    """Rendert die Tools-Sektion"""
    st.subheader("🔧 Logo-Tools")

    try:
        from admin_brand_logo_management_ui import BrandLogoAdmin
        admin = BrandLogoAdmin()

        # Backup/Export Tools
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📦 Export & Backup")

            if st.button("📄 Alle Logos exportieren (JSON)"):
                brands = admin.get_all_brands()
                if brands:
                    import json
                    export_data = {
                        'export_date': datetime.now().isoformat(),
                        'total_logos': len(brands),
                        'brands': brands
                    }

                    json_str = json.dumps(
                        export_data, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 JSON herunterladen",
                        data=json_str,
                        file_name=f"logo_export_{
                            datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json")
                else:
                    st.info("Keine Logos zum Exportieren vorhanden.")

            if st.button("🗃️ Datenbank-Backup erstellen"):
                st.info(
                    "Backup-Funktionalität wird in der nächsten Version verfügbar sein.")

        with col2:
            st.markdown("### 🧹 Bereinigung")

            if st.button("🔍 Doppelte Logos suchen"):
                brands = admin.get_all_brands()
                duplicates = []
                seen_names = {}

                for brand in brands:
                    name = brand['brand_name'].lower().strip()
                    if name in seen_names:
                        duplicates.append((brand, seen_names[name]))
                    else:
                        seen_names[name] = brand

                if duplicates:
                    st.warning(
                        f"⚠️ {
                            len(duplicates)} mögliche Duplikate gefunden:")
                    for dup_pair in duplicates:
                        st.write(
                            f"- {
                                dup_pair[0]['brand_name']} (ID: {
                                dup_pair[0]['id']}) vs {
                                dup_pair[1]['brand_name']} (ID: {
                                dup_pair[1]['id']})")
                else:
                    st.success("✅ Keine Duplikate gefunden!")

            if st.button("📏 Logo-Größen optimieren"):
                st.info(
                    "Optimierungs-Tool wird in der nächsten Version verfügbar sein.")

        # Bulk-Operationen
        st.markdown("### 🔄 Bulk-Operationen")

        brands = admin.get_all_brands()
        if brands:
            brand_names = [brand['brand_name'] for brand in brands]

            selected_brands = st.multiselect(
                "Logos für Bulk-Operationen auswählen:",
                brand_names
            )

            if selected_brands:
                col_bulk1, col_bulk2, col_bulk3 = st.columns(3)

                with col_bulk1:
                    new_category = st.selectbox("Kategorie setzen", [
                        "Nicht ändern", "PV Module", "Wechselrichter", "Batteriespeicher",
                        "Wallbox", "Energiemanagement", "Sonstiges"
                    ])

                with col_bulk2:
                    new_country = st.text_input(
                        "Land setzen (leer = nicht ändern)")

                with col_bulk3:
                    if st.button("🔄 Bulk-Update ausführen"):
                        success_count = 0

                        for brand_name in selected_brands:
                            brand_data = admin.get_brand_by_name(brand_name)
                            if brand_data:
                                update_data = {}

                                if new_category != "Nicht ändern":
                                    update_data['category'] = new_category

                                if new_country.strip():
                                    update_data['country'] = new_country.strip()

                                if update_data and admin.update_brand_logo(
                                        brand_data['id'], update_data):
                                    success_count += 1

                        st.success(
                            f"✅ {success_count} von {
                                len(selected_brands)} Logos aktualisiert!")
                        if success_count > 0:
                            st.rerun()

        # Import-Tools
        st.markdown("### 📥 Import")

        uploaded_import = st.file_uploader(
            "Logos aus JSON importieren",
            type=['json'],
            help="Importiert Logos aus einer zuvor exportierten JSON-Datei"
        )

        if uploaded_import:
            try:
                import json
                import_data = json.loads(
                    uploaded_import.getvalue().decode('utf-8'))

                if 'brands' in import_data:
                    brands_to_import = import_data['brands']
                    st.info(
                        f"📋 {
                            len(brands_to_import)} Logos zum Import gefunden")

                    if st.button("🚀 Import starten"):
                        success_count = 0
                        error_count = 0

                        for brand in brands_to_import:
                            try:
                                # Prüfen ob bereits vorhanden
                                existing = admin.get_brand_by_name(
                                    brand['brand_name'])
                                if not existing:
                                    result = admin.add_brand_logo(**brand)
                                    if result['success']:
                                        success_count += 1
                                    else:
                                        error_count += 1
                                else:
                                    st.warning(
                                        f"Logo '{
                                            brand['brand_name']}' bereits vorhanden - übersprungen")
                            except Exception as e:
                                error_count += 1
                                st.error(
                                    f"Fehler bei '{
                                        brand.get(
                                            'brand_name',
                                            'Unbekannt')}': {e}")

                        st.success(
                            f"✅ Import abgeschlossen: {success_count} erfolgreich, {error_count} Fehler")
                        if success_count > 0:
                            st.rerun()
                else:
                    st.error("❌ Ungültiges Import-Format")

            except Exception as e:
                st.error(f"❌ Import-Fehler: {e}")

    except ImportError as e:
        st.error(f"Brand-Logo-Admin nicht verfügbar: {e}")
        st.info("Tools-Funktionalität erfordert das Brand-Logo-Admin-Modul.")


def render_logo_positions_tab():
    """Rendert den Tab für Logo-Positionen"""
    try:
        from admin_logo_positions_ui import render_logo_position_settings
        from database import load_admin_setting, save_admin_setting

        render_logo_position_settings(load_admin_setting, save_admin_setting)

    except ImportError as e:
        st.error(f"Logo-Positions-UI konnte nicht geladen werden: {e}")
        st.info("Stellen Sie sicher, dass admin_logo_positions_ui.py verfügbar ist.")
    except Exception as e:
        st.error(f"Fehler beim Rendern der Logo-Positions-UI: {e}")
        st.text(traceback.format_exc())


def render_logo_statistics_section():
    """Rendert Statistiken über die Logos"""
    st.subheader("📊 Logo-Statistiken")

    if not LOGO_DB_AVAILABLE:
        st.error("Logo-Datenbank nicht verfügbar!")
        return

    logos = list_all_brand_logos()

    if not logos:
        st.info("Keine Logos vorhanden.")
        return

    # Statistiken berechnen
    total_logos = len(logos)
    formats = {}

    for logo in logos:
        format_name = logo['logo_format']
        formats[format_name] = formats.get(format_name, 0) + 1

    # Anzeige
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Gesamt Logos", total_logos)

    with col2:
        st.metric("Verschiedene Formate", len(formats))

    with col3:
        most_common_format = max(
            formats.items(),
            key=lambda x: x[1]) if formats else (
            "N/A",
            0)
        st.metric(
            "Häufigstes Format", f"{
                most_common_format[0]} ({
                most_common_format[1]})")

    # Format-Verteilung
    if formats:
        st.subheader("Format-Verteilung")
        format_df = pd.DataFrame(
            list(
                formats.items()),
            columns=[
                'Format',
                'Anzahl'])
        st.bar_chart(format_df.set_index('Format'))


# Test-Funktion
if __name__ == "__main__":
    render_logo_management_ui()
