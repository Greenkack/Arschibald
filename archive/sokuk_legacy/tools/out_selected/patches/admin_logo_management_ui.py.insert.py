# === AUTO-GENERATED INSERT PATCH ===
# target_module: admin_logo_management_ui.py

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import base64
import io
import traceback
from typing import Any

import pandas as pd
import streamlit as st
from PIL import Image


# --- DEF BLOCK START: func get_unique_brands_from_products ---
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
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func validate_image_file ---
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
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func convert_uploaded_file_to_base64 ---
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
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func display_logo_preview ---
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
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func render_logo_upload_section ---
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
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func render_logo_management_section ---
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
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func render_logo_edit_section ---
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
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func render_logo_management_ui ---
def render_logo_management_ui():
    """Hauptfunktion für die Logo-Management UI"""
    st.title("🎨 Logo-Management")
    st.markdown("---")

    # Tabs für verschiedene Bereiche
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📤 Upload", "🗂️ Verwaltung", "� Positionen", "�📊 Statistiken"])

    with tab1:
        render_logo_upload_section()

    with tab2:
        render_logo_management_section()

    with tab3:
        render_logo_positions_tab()

    with tab4:
        render_logo_statistics_section()
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func render_logo_positions_tab ---
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
# --- DEF BLOCK END ---


# --- DEF BLOCK START: func render_logo_statistics_section ---
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
# --- DEF BLOCK END ---
