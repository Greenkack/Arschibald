"""
Admin Brand Logo Management System
Vollständiges CRUD System für Hersteller/Marken-Logos
"""
import base64
import io
import sqlite3
from datetime import datetime

import streamlit as st
from PIL import Image


class BrandLogoAdmin:
    """Admin System für Herstellerlogos/Markenlogos"""

    def __init__(self, db_path: str = "data/app_data.db"):
        self.db_path = db_path
        self.ensure_brand_logos_table()

    def get_connection(self):
        """SQLite Verbindung"""
        return sqlite3.connect(self.db_path)

    def ensure_brand_logos_table(self):
        """Stellt sicher, dass die brand_logos Tabelle existiert"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brand_logos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand_name TEXT UNIQUE NOT NULL,
                    logo_base64 TEXT NOT NULL,
                    file_extension TEXT DEFAULT 'png',
                    description TEXT DEFAULT '',
                    website_url TEXT DEFAULT '',
                    country TEXT DEFAULT '',
                    category TEXT DEFAULT '',
                    logo_width INTEGER DEFAULT 0,
                    logo_height INTEGER DEFAULT 0,
                    file_size_kb INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            st.error(f"Fehler beim Erstellen der Tabelle: {e}")
        finally:
            conn.close()

    def get_all_brands(self) -> list[dict]:
        """Alle Marken/Hersteller laden"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, brand_name, description, website_url, country,
                       category, logo_width, logo_height, file_size_bytes,
                       created_at, updated_at
                FROM brand_logos
                ORDER BY brand_name
            """)

            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row, strict=False))
                    for row in cursor.fetchall()]
        except Exception as e:
            st.error(f"Fehler beim Laden der Marken: {e}")
            return []
        finally:
            conn.close()

    def get_brand_by_name(self, brand_name: str) -> dict | None:
        """Einzelne Marke laden"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM brand_logos WHERE brand_name = ?
            """, [brand_name])

            result = cursor.fetchone()
            if result:
                columns = [description[0]
                           for description in cursor.description]
                return dict(zip(columns, result, strict=False))
            return None
        except Exception as e:
            st.error(f"Fehler beim Laden der Marke: {e}")
            return None
        finally:
            conn.close()

    def add_brand_logo(self, brand_data: dict) -> bool:
        """Neue Marke/Logo hinzufügen"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO brand_logos (
                    brand_name, logo_base64, logo_format, description,
                    website_url, country, category, logo_width, logo_height,
                    file_size_bytes, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                brand_data['brand_name'],
                brand_data['logo_base64'],
                # Map file_extension to logo_format
                brand_data.get('file_extension', 'png'),
                brand_data.get('description', ''),
                brand_data.get('website_url', ''),
                brand_data.get('country', ''),
                brand_data.get('category', ''),
                brand_data.get('logo_width', 0),
                brand_data.get('logo_height', 0),
                brand_data.get('file_size_kb', 0) *
                1024,  # Convert KB to bytes
                datetime.now().isoformat()
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            st.error(f"Marke '{brand_data['brand_name']}' existiert bereits!")
            return False
        except Exception as e:
            st.error(f"Fehler beim Hinzufügen: {e}")
            return False
        finally:
            conn.close()

    def update_brand_logo(self, brand_id: int, brand_data: dict) -> bool:
        """Marke/Logo aktualisieren"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE brand_logos SET
                    brand_name = ?, logo_base64 = ?, logo_format = ?,
                    description = ?, website_url = ?, country = ?, category = ?,
                    logo_width = ?, logo_height = ?, file_size_bytes = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                brand_data['brand_name'],
                brand_data['logo_base64'],
                # Map file_extension to logo_format
                brand_data.get('file_extension', 'png'),
                brand_data.get('description', ''),
                brand_data.get('website_url', ''),
                brand_data.get('country', ''),
                brand_data.get('category', ''),
                brand_data.get('logo_width', 0),
                brand_data.get('logo_height', 0),
                brand_data.get('file_size_kb', 0) *
                1024,  # Convert KB to bytes
                datetime.now().isoformat(),
                brand_id
            ))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Fehler beim Aktualisieren: {e}")
            return False
        finally:
            conn.close()

    def delete_brand_logo(self, brand_id: int) -> bool:
        """Marke/Logo löschen"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM brand_logos WHERE id = ?", [brand_id])
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Fehler beim Löschen: {e}")
            return False
        finally:
            conn.close()

    def get_manufacturers_from_products(self) -> list[str]:
        """Alle Hersteller aus der Produktdatenbank laden"""
        conn = self.get_connection()
        manufacturers = set()

        try:
            cursor = conn.cursor()

            # Aus products_complete
            try:
                cursor.execute(
                    "SELECT DISTINCT hersteller FROM products_complete WHERE hersteller != ''")
                manufacturers.update([row[0] for row in cursor.fetchall()])
            except BaseException:
                pass

            # Aus products (Fallback)
            try:
                cursor.execute(
                    "SELECT DISTINCT manufacturer FROM products WHERE manufacturer != ''")
                manufacturers.update([row[0] for row in cursor.fetchall()])
            except BaseException:
                pass

            return sorted(list(manufacturers))
        except Exception as e:
            st.error(f"Fehler beim Laden der Hersteller: {e}")
            return []
        finally:
            conn.close()

    def process_logo_image(self, uploaded_file) -> dict:
        """Logo Bild verarbeiten und analysieren"""
        try:
            image = Image.open(uploaded_file)

            # Bildgröße optimieren (max 300x300 für Logos)
            max_size = (300, 300)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Zu Base64 konvertieren
            buffer = io.BytesIO()
            format_map = {
                'JPEG': 'JPEG',
                'PNG': 'PNG',
                'GIF': 'PNG',
                'WEBP': 'PNG'}
            save_format = format_map.get(image.format, 'PNG')
            image.save(buffer, format=save_format, optimize=True, quality=85)

            logo_base64 = base64.b64encode(buffer.getvalue()).decode()
            file_extension = save_format.lower()

            return {
                'logo_base64': logo_base64,
                'file_extension': file_extension,
                'logo_width': image.width,
                'logo_height': image.height,
                'file_size_kb': len(buffer.getvalue()) // 1024,
                'success': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def render_brand_logo_admin_ui():
    """Streamlit UI für Brand Logo Administration"""
    st.title("🏷️ Marken-Logo Administration")

    admin = BrandLogoAdmin()

    # Tabs für verschiedene Aktionen
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Übersicht", "➕ Hinzufügen", "✏️ Bearbeiten", "🔧 Tools"])

    with tab1:
        st.subheader("Logo-Übersicht")

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
                    if brand['category']:
                        st.caption(f"Kategorie: {brand['category']}")
                    if brand['country']:
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

    with tab2:
        st.subheader("Neues Marken-Logo hinzufügen")

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
                        brand_data = {
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
                        }

                        if admin.add_brand_logo(brand_data):
                            st.success(
                                f"Logo für '{brand_name}' erfolgreich hinzugefügt!")
                            st.rerun()
                    else:
                        st.error(
                            f"Fehler beim Verarbeiten des Logos: {
                                logo_result['error']}")

    with tab3:
        st.subheader("Logo bearbeiten")

        if hasattr(st.session_state, 'edit_brand_id'):
            brand_id = st.session_state.edit_brand_id

            # Bestehende Daten laden
            brands = admin.get_all_brands()
            current_brand = next(
                (b for b in brands if b['id'] == brand_id), None)

            if current_brand:
                full_brand_data = admin.get_brand_by_name(
                    current_brand['brand_name'])

                with st.form("edit_brand_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        brand_name = st.text_input(
                            "Markenname*", value=current_brand['brand_name'])
                        category = st.text_input(
                            "Kategorie", value=current_brand['category'] or "")
                        country = st.text_input(
                            "Herstellerland", value=current_brand['country'] or "")
                        website_url = st.text_input(
                            "Website URL", value=current_brand['website_url'] or "")

                    with col2:
                        description = st.text_area(
                            "Beschreibung", value=current_brand['description'] or "")

                        # Aktuelles Logo anzeigen
                        if full_brand_data and full_brand_data['logo_base64']:
                            try:
                                logo_bytes = base64.b64decode(
                                    full_brand_data['logo_base64'])
                                st.image(
                                    logo_bytes, width=200, caption="Aktuelles Logo")
                            except BaseException:
                                st.write("Logo-Anzeige nicht möglich")

                        # Neues Logo Upload (optional)
                        new_logo = st.file_uploader(
                            "Neues Logo (optional)",
                            type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
                            help="Leer lassen um aktuelles Logo zu behalten"
                        )

                    col_submit, col_cancel = st.columns(2)

                    with col_submit:
                        submitted = st.form_submit_button(
                            "Änderungen speichern")
                    with col_cancel:
                        cancelled = st.form_submit_button("Abbrechen")

                    if cancelled:
                        del st.session_state.edit_brand_id
                        st.rerun()

                    if submitted:
                        if not brand_name:
                            st.error("Markenname ist Pflichtfeld!")
                        else:
                            # Logo-Daten vorbereiten
                            if new_logo:
                                logo_result = admin.process_logo_image(
                                    new_logo)
                                if not logo_result['success']:
                                    st.error(
                                        f"Fehler beim Logo: {
                                            logo_result['error']}")
                                    return

                                logo_data = {
                                    'logo_base64': logo_result['logo_base64'],
                                    'file_extension': logo_result['file_extension'],
                                    'logo_width': logo_result['logo_width'],
                                    'logo_height': logo_result['logo_height'],
                                    'file_size_kb': logo_result['file_size_kb']}
                            else:
                                # Bestehendes Logo beibehalten
                                logo_data = {
                                    'logo_base64': full_brand_data['logo_base64'],
                                    'file_extension': full_brand_data['file_extension'],
                                    'logo_width': full_brand_data['logo_width'],
                                    'logo_height': full_brand_data['logo_height'],
                                    'file_size_kb': full_brand_data['file_size_kb']}

                            brand_data = {
                                'brand_name': brand_name,
                                'description': description,
                                'website_url': website_url,
                                'country': country,
                                'category': category,
                                **logo_data
                            }

                            if admin.update_brand_logo(brand_id, brand_data):
                                st.success("Logo erfolgreich aktualisiert!")
                                del st.session_state.edit_brand_id
                                st.rerun()
            else:
                st.error("Logo nicht gefunden")
                if st.button("Zurück zur Übersicht"):
                    del st.session_state.edit_brand_id
                    st.rerun()
        else:
            st.info("Wählen Sie ein Logo aus der Übersicht zum Bearbeiten")

    with tab4:
        st.subheader("Tools & Statistiken")

        brands = admin.get_all_brands()
        manufacturers = admin.get_manufacturers_from_products()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Gesamt Logos", len(brands))
        with col2:
            st.metric("Hersteller in Produkten", len(manufacturers))
        with col3:
            brands_with_logos = len([b for b in brands if b['brand_name']])
            missing_logos = len([m for m in manufacturers if not any(
                b['brand_name'] == m for b in brands)])
            st.metric("Fehlende Logos", missing_logos)

        if missing_logos > 0:
            st.subheader("Hersteller ohne Logos")
            missing_list = [
                m for m in manufacturers if not any(
                    b['brand_name'] == m for b in brands)]
            for manufacturer in missing_list:
                st.write(f"• {manufacturer}")

        st.subheader("Datenbank-Tools")

        if st.button("Tabelle neu initialisieren"):
            admin.ensure_brand_logos_table()
            st.success("Tabelle überprüft/erstellt!")


if __name__ == "__main__":
    render_brand_logo_admin_ui()
