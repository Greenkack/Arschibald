"""
Admin Product Database Management System
CRUD Operations für Produktdatenbank mit Excel Import/Export
"""
import base64
import io
import os
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st


class ProductDatabaseAdmin:
    def __init__(self, db_path: str = "data/app_data.db"):
        self.db_path = db_path
        self.categories = [
            "PV Modul", "Wechselrichter", "Batteriespeicher",
            "Wallbox", "Energiemanagementsystem", "Leistungsoptimierer",
            "Notstromversorgung", "Carport", "Extrakosten", "Tierabwehrschutz"
        ]

    def get_connection(self):
        """SQLite Verbindung erstellen"""
        return sqlite3.connect(self.db_path)

    def create_products_table(self):
        """Erstellt die vollständige Produkttabelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products_complete (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kategorie TEXT NOT NULL,
                produkt_modell TEXT NOT NULL,
                hersteller TEXT NOT NULL,
                preis_stück REAL DEFAULT 0.0,
                pv_modul_leistung REAL DEFAULT 0.0,
                kapazitaet_speicher_kwh REAL DEFAULT 0.0,
                wr_leistung_kw REAL DEFAULT 0.0,
                ladezyklen_speicher INTEGER DEFAULT 0,
                garantie_zeit INTEGER DEFAULT 0,
                mass_laenge REAL DEFAULT 0.0,
                mass_breite REAL DEFAULT 0.0,
                mass_gewicht_kg REAL DEFAULT 0.0,
                wirkungsgrad_prozent REAL DEFAULT 0.0,
                hersteller_land TEXT DEFAULT '',
                beschreibung_info TEXT DEFAULT '',
                eigenschaft_info TEXT DEFAULT '',
                spezial_merkmal TEXT DEFAULT '',
                rating_null_zehn INTEGER DEFAULT 0,
                image_base64 TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def import_from_excel(self, file_path: str):
        """Importiert Produkte aus Excel"""
        try:
            df = pd.read_excel(file_path)
            conn = self.get_connection()

            # Tabelle leeren für Neuimport
            conn.execute("DELETE FROM products_complete")

            def safe_float(value, default=0.0):
                """Sichere Konvertierung zu Float mit deutschen Zahlen"""
                if pd.isna(value) or value is None or value == '':
                    return default
                try:
                    # Deutsche Zahlenformate (Komma als Dezimaltrennzeichen)
                    if isinstance(value, str):
                        value = value.replace(',', '.')
                    return float(value)
                except BaseException:
                    return default

            def safe_int(value, default=0):
                """Sichere Konvertierung zu Int"""
                if pd.isna(value) or value is None or value == '':
                    return default
                try:
                    return int(float(str(value).replace(',', '.')))
                except BaseException:
                    return default

            def safe_str(value, default=''):
                """Sichere Konvertierung zu String"""
                if pd.isna(value) or value is None:
                    return default
                return str(value)

            for _, row in df.iterrows():
                conn.execute("""
                    INSERT INTO products_complete (
                        kategorie, produkt_modell, hersteller, preis_stück,
                        pv_modul_leistung, kapazitaet_speicher_kwh, wr_leistung_kw,
                        ladezyklen_speicher, garantie_zeit, mass_laenge, mass_breite,
                        mass_gewicht_kg, wirkungsgrad_prozent, hersteller_land,
                        beschreibung_info, eigenschaft_info, spezial_merkmal,
                        rating_null_zehn, image_base64
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    safe_str(row.get('kategorie')),
                    safe_str(row.get('produkt_modell')),
                    safe_str(row.get('hersteller')),
                    safe_float(row.get('preis_stück')),
                    safe_float(row.get('pv_modul_leistung')),
                    safe_float(row.get('kapazitaet_speicher_kwh')),
                    safe_float(row.get('wr_leistung_kw')),
                    safe_int(row.get('ladezyklen_speicher')),
                    safe_int(row.get('garantie_zeit')),
                    safe_float(row.get('mass_laenge')),
                    safe_float(row.get('mass_breite')),
                    safe_float(row.get('mass_gewicht_kg')),
                    safe_float(row.get('wirkungsgrad_prozent')),
                    safe_str(row.get('hersteller_land')),
                    safe_str(row.get('beschreibung_info')),
                    safe_str(row.get('eigenschaft_info')),
                    safe_str(row.get('spezial_merkmal')),
                    safe_int(row.get('rating_null_zehn')),
                    safe_str(row.get('image_base64'))
                ))

            conn.commit()
            conn.close()
            return True, f"Successfully imported {len(df)} products"
        except Exception as e:
            return False, f"Import error: {str(e)}"

    def get_all_products(self) -> pd.DataFrame:
        """Alle Produkte laden"""
        conn = self.get_connection()
        try:
            df = pd.read_sql_query(
                "SELECT * FROM products_complete ORDER BY kategorie, hersteller, produkt_modell",
                conn)
            return df
        except BaseException:
            return pd.DataFrame()
        finally:
            conn.close()

    def get_products_by_category(self, category: str) -> pd.DataFrame:
        """Produkte nach Kategorie filtern"""
        conn = self.get_connection()
        try:
            df = pd.read_sql_query(
                "SELECT * FROM products_complete WHERE kategorie = ? ORDER BY hersteller, produkt_modell",
                conn,
                params=[category])
            return df
        except BaseException:
            return pd.DataFrame()
        finally:
            conn.close()

    def get_manufacturers_by_category(self, category: str) -> list[str]:
        """Hersteller nach Kategorie"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT hersteller FROM products_complete WHERE kategorie = ? ORDER BY hersteller",
                [category])
            return [row[0] for row in cursor.fetchall()]
        except BaseException:
            return []
        finally:
            conn.close()

    def get_models_by_manufacturer(
            self,
            category: str,
            manufacturer: str) -> list[dict]:
        """Modelle nach Hersteller (mit allen Eigenschaften)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, produkt_modell, pv_modul_leistung, wr_leistung_kw,
                       kapazitaet_speicher_kwh, preis_stück, wirkungsgrad_prozent
                FROM products_complete
                WHERE kategorie = ? AND hersteller = ?
                ORDER BY produkt_modell
            """, [category, manufacturer])

            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row, strict=False))
                    for row in cursor.fetchall()]
        except BaseException:
            return []
        finally:
            conn.close()

    def add_product(self, product_data: dict) -> bool:
        """Neues Produkt hinzufügen"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO products_complete (
                    kategorie, produkt_modell, hersteller, preis_stück,
                    pv_modul_leistung, kapazitaet_speicher_kwh, wr_leistung_kw,
                    ladezyklen_speicher, garantie_zeit, mass_laenge, mass_breite,
                    mass_gewicht_kg, wirkungsgrad_prozent, hersteller_land,
                    beschreibung_info, eigenschaft_info, spezial_merkmal,
                    rating_null_zehn, image_base64, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (product_data['kategorie'],
                 product_data['produkt_modell'],
                 product_data['hersteller'],
                 product_data['preis_stück'],
                 product_data['pv_modul_leistung'],
                 product_data['kapazitaet_speicher_kwh'],
                 product_data['wr_leistung_kw'],
                 product_data['ladezyklen_speicher'],
                 product_data['garantie_zeit'],
                 product_data['mass_laenge'],
                 product_data['mass_breite'],
                 product_data['mass_gewicht_kg'],
                 product_data['wirkungsgrad_prozent'],
                 product_data['hersteller_land'],
                 product_data['beschreibung_info'],
                 product_data['eigenschaft_info'],
                 product_data['spezial_merkmal'],
                 product_data['rating_null_zehn'],
                 product_data['image_base64'],
                 datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Fehler beim Hinzufügen: {e}")
            return False
        finally:
            conn.close()


def render_product_admin_ui():
    """Streamlit UI für Produktdatenbank Administration"""
    st.title("🗄️ Produktdatenbank Administration")

    admin = ProductDatabaseAdmin()

    # Tabs für verschiedene Aktionen
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Übersicht", "➕ Hinzufügen", "📤 Import/Export", "🔧 Tools"])

    with tab1:
        st.subheader("Produktübersicht")

        # Kategorie Filter
        col1, col2 = st.columns(2)
        with col1:
            selected_category = st.selectbox(
                "Kategorie", ["Alle"] + admin.categories)

        if selected_category == "Alle":
            df = admin.get_all_products()
        else:
            df = admin.get_products_by_category(selected_category)

        if not df.empty:
            st.write(f"**{len(df)} Produkte gefunden**")

            # Wichtige Spalten anzeigen
            display_columns = [
                'id',
                'kategorie',
                'hersteller',
                'produkt_modell',
                'pv_modul_leistung',
                'wr_leistung_kw',
                'kapazitaet_speicher_kwh',
                'preis_stück']

            available_columns = [
                col for col in display_columns if col in df.columns]
            st.dataframe(df[available_columns], use_container_width=True)
        else:
            st.info("Keine Produkte gefunden.")

    with tab2:
        st.subheader("Neues Produkt hinzufügen")

        with st.form("add_product_form"):
            col1, col2 = st.columns(2)

            with col1:
                kategorie = st.selectbox("Kategorie*", admin.categories)
                hersteller = st.text_input("Hersteller*")
                produkt_modell = st.text_input("Produktmodell*")
                preis_stück = st.number_input(
                    "Preis pro Stück (€)", min_value=0.0, step=0.01)

                if kategorie == "PV Modul":
                    pv_modul_leistung = st.number_input(
                        "PV Modul Leistung (W)", min_value=0.0, step=1.0)
                else:
                    pv_modul_leistung = 0.0

                if kategorie == "Wechselrichter":
                    wr_leistung_kw = st.number_input(
                        "WR Leistung (kW)", min_value=0.0, step=0.1)
                else:
                    wr_leistung_kw = 0.0

                if kategorie == "Batteriespeicher":
                    kapazitaet_speicher_kwh = st.number_input(
                        "Speicher Kapazität (kWh)", min_value=0.0, step=0.1)
                    ladezyklen_speicher = st.number_input(
                        "Ladezyklen", min_value=0, step=100)
                else:
                    kapazitaet_speicher_kwh = 0.0
                    ladezyklen_speicher = 0

            with col2:
                garantie_zeit = st.number_input(
                    "Garantie (Jahre)", min_value=0, step=1)
                mass_laenge = st.number_input(
                    "Länge (m)", min_value=0.0, step=0.01)
                mass_breite = st.number_input(
                    "Breite (m)", min_value=0.0, step=0.01)
                mass_gewicht_kg = st.number_input(
                    "Gewicht (kg)", min_value=0.0, step=0.1)
                wirkungsgrad_prozent = st.number_input(
                    "Wirkungsgrad (%)", min_value=0.0, max_value=100.0, step=0.1)
                hersteller_land = st.text_input("Herstellerland")
                rating_null_zehn = st.slider("Rating (0-10)", 0, 10, 5)

            beschreibung_info = st.text_area("Beschreibung")
            eigenschaft_info = st.text_area("Eigenschaften")
            spezial_merkmal = st.text_area("Spezielle Merkmale")

            # Bild Upload
            uploaded_image = st.file_uploader(
                "Produktbild", type=['png', 'jpg', 'jpeg'])
            image_base64 = ""
            if uploaded_image:
                image_base64 = base64.b64encode(uploaded_image.read()).decode()

            submitted = st.form_submit_button("Produkt hinzufügen")

            if submitted:
                if not all([kategorie, hersteller, produkt_modell]):
                    st.error(
                        "Kategorie, Hersteller und Produktmodell sind Pflichtfelder!")
                else:
                    product_data = {
                        'kategorie': kategorie,
                        'produkt_modell': produkt_modell,
                        'hersteller': hersteller,
                        'preis_stück': preis_stück,
                        'pv_modul_leistung': pv_modul_leistung,
                        'kapazitaet_speicher_kwh': kapazitaet_speicher_kwh,
                        'wr_leistung_kw': wr_leistung_kw,
                        'ladezyklen_speicher': ladezyklen_speicher,
                        'garantie_zeit': garantie_zeit,
                        'mass_laenge': mass_laenge,
                        'mass_breite': mass_breite,
                        'mass_gewicht_kg': mass_gewicht_kg,
                        'wirkungsgrad_prozent': wirkungsgrad_prozent,
                        'hersteller_land': hersteller_land,
                        'beschreibung_info': beschreibung_info,
                        'eigenschaft_info': eigenschaft_info,
                        'spezial_merkmal': spezial_merkmal,
                        'rating_null_zehn': rating_null_zehn,
                        'image_base64': image_base64
                    }

                    if admin.add_product(product_data):
                        st.success("Produkt erfolgreich hinzugefügt!")
                        st.rerun()

    with tab3:
        st.subheader("Import/Export")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Excel Import**")
            uploaded_file = st.file_uploader(
                "Excel Datei (.xlsx)", type=['xlsx'])

            if uploaded_file and st.button("Importieren"):
                # Temporäre Datei erstellen
                temp_path = f"temp_import_{
                    datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())

                success, message = admin.import_from_excel(temp_path)
                if success:
                    st.success(message)
                else:
                    st.error(message)

                # Temporäre Datei löschen
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        with col2:
            st.write("**Excel Export**")
            if st.button("Alle Produkte exportieren"):
                df = admin.get_all_products()
                if not df.empty:
                    # Excel Buffer erstellen
                    buffer = io.BytesIO()
                    df.to_excel(buffer, index=False)
                    buffer.seek(0)

                    st.download_button(
                        label="Download Excel",
                        data=buffer,
                        file_name=f"products_export_{
                            datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with tab4:
        st.subheader("Datenbank Tools")

        if st.button("Produkttabelle initialisieren"):
            admin.create_products_table()
            st.success("Tabelle erstellt/überprüft!")

        # Statistiken
        df = admin.get_all_products()
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesamt Produkte", len(df))
            with col2:
                st.metric(
                    "Kategorien",
                    df['kategorie'].nunique() if 'kategorie' in df.columns else 0)
            with col3:
                st.metric(
                    "Hersteller",
                    df['hersteller'].nunique() if 'hersteller' in df.columns else 0)


if __name__ == "__main__":
    render_product_admin_ui()
