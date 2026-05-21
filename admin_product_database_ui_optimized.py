"""
Admin Product Database Management System - OPTIMIZED VERSION
CRUD Operations mit Pagination, Lazy Loading und Performance-Optimierung
Fixed: Memory-Probleme bei großen Datenmengen
"""
import base64
import io
import os
import sqlite3
from datetime import datetime
from typing import Optional, Tuple

import pandas as pd
import streamlit as st


class ProductDatabaseAdminOptimized:
    """Optimierte Produktdatenbank-Verwaltung mit Pagination und Caching"""
    
    def __getstate__(self):
        """Ermöglicht Pickle-Serialisierung für Session State"""
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        """Ermöglicht Pickle-Deserialisierung für Session State"""
        self.__dict__.update(state)
    
    def __init__(self, db_path: str = "data/app_data.db"):
        self.db_path = db_path
        self.categories = [
            "PV Modul", "Wechselrichter", "Batteriespeicher",
            "Wallbox", "Energiemanagementsystem", "Leistungsoptimierer",
            "Notstromversorgung", "Carport", "Extrakosten", "Tierabwehrschutz",
            "Wärmepumpe Luft-Wasser", "Wärmepumpe Sole-Wasser", "Wärmepumpe Wasser-Wasser"
        ]
        self.items_per_page = 50  # Pagination: 50 Produkte pro Seite
        
    def get_connection(self):
        """SQLite Verbindung erstellen"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Row Factory für besseren Zugriff
        return conn
    
    def create_products_table(self):
        """Erstellt die vollständige Produkttabelle mit Index für Performance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabelle erstellen
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
        
        # Performance-Indizes erstellen
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON products_complete(kategorie)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_manufacturer 
            ON products_complete(hersteller)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category_manufacturer 
            ON products_complete(kategorie, hersteller)
        """)
        
        conn.commit()
        conn.close()
    
    def get_product_count(self, category: Optional[str] = None, manufacturer: Optional[str] = None) -> int:
        """Anzahl der Produkte ermitteln (für Pagination)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if category and manufacturer:
                cursor.execute(
                    "SELECT COUNT(*) FROM products_complete WHERE kategorie = ? AND hersteller = ?",
                    [category, manufacturer]
                )
            elif category:
                cursor.execute(
                    "SELECT COUNT(*) FROM products_complete WHERE kategorie = ?",
                    [category]
                )
            elif manufacturer:
                cursor.execute(
                    "SELECT COUNT(*) FROM products_complete WHERE hersteller = ?",
                    [manufacturer]
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM products_complete")
            
            return cursor.fetchone()[0]
        except Exception as e:
            st.error(f"Fehler beim Zählen: {e}")
            return 0
        finally:
            conn.close()
    
    def get_products_paginated(
        self,
        page: int = 1,
        category: Optional[str] = None,
        manufacturer: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> pd.DataFrame:
        """Produkte mit Pagination laden (MEMORY-SAFE)"""
        conn = self.get_connection()
        
        # Page zu int konvertieren (falls Streamlit es als String speichert)
        page = int(page) if not isinstance(page, int) else page
        offset = (page - 1) * self.items_per_page
        
        try:
            # Query dynamisch aufbauen
            query = "SELECT * FROM products_complete WHERE 1=1"
            params = []
            
            if category:
                query += " AND kategorie = ?"
                params.append(category)
            
            if manufacturer:
                query += " AND hersteller = ?"
                params.append(manufacturer)
            
            if search_term:
                query += " AND (produkt_modell LIKE ? OR hersteller LIKE ? OR beschreibung_info LIKE ?)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            query += f" ORDER BY kategorie, hersteller, produkt_modell LIMIT {self.items_per_page} OFFSET {offset}"
            
            df = pd.read_sql_query(query, conn, params=params)
            return df
        except Exception as e:
            st.error(f"Fehler beim Laden: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def get_manufacturers_by_category(self, category: str) -> list[str]:
        """Hersteller nach Kategorie (CACHED)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT hersteller FROM products_complete WHERE kategorie = ? ORDER BY hersteller",
                [category]
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            st.error(f"Fehler beim Laden der Hersteller: {e}")
            return []
        finally:
            conn.close()
    
    def get_category_statistics(self) -> dict:
        """Statistiken pro Kategorie (für Übersicht)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    kategorie, 
                    COUNT(*) as count,
                    COUNT(DISTINCT hersteller) as manufacturers
                FROM products_complete
                GROUP BY kategorie
                ORDER BY kategorie
            """)
            
            stats = {}
            for row in cursor.fetchall():
                stats[row[0]] = {
                    'count': row[1],
                    'manufacturers': row[2]
                }
            return stats
        except Exception as e:
            st.error(f"Fehler bei Statistiken: {e}")
            return {}
        finally:
            conn.close()
    
    def add_product(self, product_data: dict) -> bool:
        """Neues Produkt hinzufügen"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products_complete (
                    kategorie, produkt_modell, hersteller, preis_stück,
                    pv_modul_leistung, kapazitaet_speicher_kwh, wr_leistung_kw,
                    ladezyklen_speicher, garantie_zeit, mass_laenge, mass_breite,
                    mass_gewicht_kg, wirkungsgrad_prozent, hersteller_land,
                    beschreibung_info, eigenschaft_info, spezial_merkmal,
                    rating_null_zehn, image_base64, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data['kategorie'],
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
                datetime.now().isoformat()
            ))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Fehler beim Hinzufügen: {e}")
            return False
        finally:
            conn.close()
    
    def update_product(self, product_id: int, product_data: dict) -> bool:
        """Produkt aktualisieren"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products_complete SET
                    kategorie = ?, produkt_modell = ?, hersteller = ?, preis_stück = ?,
                    pv_modul_leistung = ?, kapazitaet_speicher_kwh = ?, wr_leistung_kw = ?,
                    ladezyklen_speicher = ?, garantie_zeit = ?, mass_laenge = ?, mass_breite = ?,
                    mass_gewicht_kg = ?, wirkungsgrad_prozent = ?, hersteller_land = ?,
                    beschreibung_info = ?, eigenschaft_info = ?, spezial_merkmal = ?,
                    rating_null_zehn = ?, updated_at = ?
                WHERE id = ?
            """, (
                product_data['kategorie'],
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
                datetime.now().isoformat(),
                product_id
            ))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Fehler beim Aktualisieren: {e}")
            return False
        finally:
            conn.close()
    
    def delete_product(self, product_id: int) -> bool:
        """Produkt löschen"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products_complete WHERE id = ?", [product_id])
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Fehler beim Löschen: {e}")
            return False
        finally:
            conn.close()
    
    def import_from_excel(self, file_path: str, progress_callback=None) -> Tuple[bool, str]:
        """Importiert Produkte aus Excel mit Progress-Tracking.
        
        Unterstuetzt sowohl deutsche ALS AUCH englische Spaltenbezeichnungen:
          Deutsch: kategorie, produkt_modell, hersteller, preis_stück ...
          Englisch: category, model_name, brand, price_euro ...
        """
        try:
            df = pd.read_excel(file_path)
            # Spaltennamen normalisieren (Groß-/Kleinschreibung und Leerzeichen egal)
            df.columns = df.columns.str.lower().str.strip()
            conn = self.get_connection()
            cursor = conn.cursor()

            total_rows = len(df)
            imported_count = 0

            def safe_float(value, default=0.0):
                if pd.isna(value) or value is None or value == '':
                    return default
                try:
                    if isinstance(value, str):
                        value = value.replace(',', '.')
                    return float(value)
                except Exception:
                    return default

            def safe_int(value, default=0):
                if pd.isna(value) or value is None or value == '':
                    return default
                try:
                    return int(float(str(value).replace(',', '.')))
                except Exception:
                    return default

            def safe_str(value, default=''):
                if pd.isna(value) or value is None:
                    return default
                return str(value).strip()

            # Alias-Map: (deutsche DB-Spalte) → [mögliche Excel-Spaltenköpfe]
            # Sowohl deutsche als auch englische Namen werden akzeptiert
            ALIASES = {
                'kategorie':              ['kategorie', 'category', 'cat'],
                'produkt_modell':         ['produkt_modell', 'model_name', 'modell', 'model', 'name'],
                'hersteller':             ['hersteller', 'brand', 'manufacturer', 'marke'],
                'preis_stück':            ['preis_stück', 'preis_stuck', 'price_euro', 'preis', 'price'],
                'pv_modul_leistung':      ['pv_modul_leistung', 'capacity_w', 'leistung_w', 'power_w'],
                'kapazitaet_speicher_kwh':['kapazitaet_speicher_kwh', 'max_kwh_capacity', 'storage_kwh', 'kapazitaet_kwh'],
                'wr_leistung_kw':         ['wr_leistung_kw', 'power_kw', 'storage_power_kw', 'leistung_kw'],
                'ladezyklen_speicher':    ['ladezyklen_speicher', 'max_cycles', 'ladezyklen', 'cycles'],
                'garantie_zeit':          ['garantie_zeit', 'warranty_years', 'garantie', 'warranty'],
                'mass_laenge':            ['mass_laenge', 'length_m', 'laenge_m', 'length'],
                'mass_breite':            ['mass_breite', 'width_m', 'breite_m', 'width'],
                'mass_gewicht_kg':        ['mass_gewicht_kg', 'weight_kg', 'gewicht_kg', 'weight'],
                'wirkungsgrad_prozent':   ['wirkungsgrad_prozent', 'efficiency_percent', 'wirkungsgrad', 'efficiency'],
                'hersteller_land':        ['hersteller_land', 'origin_country', 'land', 'country'],
                'beschreibung_info':      ['beschreibung_info', 'description', 'beschreibung'],
                'eigenschaft_info':       ['eigenschaft_info', 'pros', 'eigenschaften', 'features'],
                'spezial_merkmal':        ['spezial_merkmal', 'cons', 'spezial', 'special'],
                'rating_null_zehn':       ['rating_null_zehn', 'rating', 'bewertung'],
                'image_base64':           ['image_base64', 'bild_base64', 'image'],
            }

            def get_val(row, db_col):
                """Liest Wert via Alias-Liste — erster Treffer gewinnt."""
                for alias in ALIASES.get(db_col, [db_col]):
                    if alias in row.index and not (pd.isna(row[alias]) if hasattr(row[alias], '__class__') else False):
                        val = row[alias]
                        if not (isinstance(val, float) and pd.isna(val)):
                            return val
                return None

            # Batch-Insert für Performance
            for idx, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO products_complete (
                            kategorie, produkt_modell, hersteller, preis_stück,
                            pv_modul_leistung, kapazitaet_speicher_kwh, wr_leistung_kw,
                            ladezyklen_speicher, garantie_zeit, mass_laenge, mass_breite,
                            mass_gewicht_kg, wirkungsgrad_prozent, hersteller_land,
                            beschreibung_info, eigenschaft_info, spezial_merkmal,
                            rating_null_zehn, image_base64
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        safe_str(get_val(row, 'kategorie')),
                        safe_str(get_val(row, 'produkt_modell')),
                        safe_str(get_val(row, 'hersteller')),
                        safe_float(get_val(row, 'preis_stück')),
                        safe_float(get_val(row, 'pv_modul_leistung')),
                        safe_float(get_val(row, 'kapazitaet_speicher_kwh')),
                        safe_float(get_val(row, 'wr_leistung_kw')),
                        safe_int(get_val(row, 'ladezyklen_speicher')),
                        safe_int(get_val(row, 'garantie_zeit')),
                        safe_float(get_val(row, 'mass_laenge')),
                        safe_float(get_val(row, 'mass_breite')),
                        safe_float(get_val(row, 'mass_gewicht_kg')),
                        safe_float(get_val(row, 'wirkungsgrad_prozent')),
                        safe_str(get_val(row, 'hersteller_land')),
                        safe_str(get_val(row, 'beschreibung_info')),
                        safe_str(get_val(row, 'eigenschaft_info')),
                        safe_str(get_val(row, 'spezial_merkmal')),
                        safe_int(get_val(row, 'rating_null_zehn')),
                        safe_str(get_val(row, 'image_base64'))
                    ))

                    imported_count += 1

                    # Commit alle 100 Zeilen für Performance
                    if imported_count % 100 == 0:
                        conn.commit()
                        if progress_callback:
                            progress_callback(imported_count, total_rows)

                except Exception as e:
                    st.warning(f"Fehler bei Zeile {idx + 1}: {e}")
                    continue

            conn.commit()
            conn.close()
            # Sync zur Haupt-Produkt-Tabelle für App-weite Verfügbarkeit
            synced, skipped_sync = self.sync_to_products_table()
            sync_msg = f" {synced} Produkte in Haupt-Tabelle synchronisiert." if synced > 0 else ""
            return True, f"Erfolgreich {imported_count} von {total_rows} Produkten importiert.{sync_msg}"
        except Exception as e:
            return False, f"Import-Fehler: {str(e)}"
    
    def sync_to_products_table(self) -> Tuple[int, int]:
        """Synchronisiert products_complete → products Tabelle (für App-weite Verwendung).
        
        Diese Methode liest alle Datensätze aus products_complete und schreibt sie
        in die Haupt-products-Tabelle, die von der gesamten App genutzt wird.
        Gibt (synced_count, skipped_count) zurück.
        """
        conn = self.get_connection()
        synced = 0
        skipped = 0
        try:
            cursor = conn.cursor()

            # Stelle sicher, dass die products-Tabelle existiert (Basis-Schema)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    model_name TEXT NOT NULL UNIQUE,
                    brand TEXT DEFAULT '',
                    price_euro REAL DEFAULT 0.0,
                    capacity_w REAL DEFAULT 0.0,
                    storage_power_kw REAL DEFAULT 0.0,
                    power_kw REAL DEFAULT 0.0,
                    max_cycles INTEGER DEFAULT 0,
                    warranty_years INTEGER DEFAULT 0,
                    length_m REAL DEFAULT 0.0,
                    width_m REAL DEFAULT 0.0,
                    weight_kg REAL DEFAULT 0.0,
                    efficiency_percent REAL DEFAULT 0.0,
                    origin_country TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    pros TEXT DEFAULT '',
                    cons TEXT DEFAULT '',
                    rating REAL DEFAULT 0.0,
                    image_base64 TEXT DEFAULT '',
                    max_kwh_capacity REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("SELECT * FROM products_complete")
            rows = cursor.fetchall()

            for row in rows:
                row_dict = dict(row)
                kategorie = (row_dict.get('kategorie') or '').strip()
                modell = (row_dict.get('produkt_modell') or '').strip()

                if not kategorie or not modell:
                    skipped += 1
                    continue

                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO products (
                            category, model_name, brand, price_euro,
                            capacity_w, max_kwh_capacity, power_kw,
                            max_cycles, warranty_years, length_m, width_m,
                            weight_kg, efficiency_percent, origin_country,
                            description, pros, cons, rating, image_base64,
                            updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        kategorie,
                        modell,
                        (row_dict.get('hersteller') or '').strip(),
                        float(row_dict.get('preis_stück') or 0),
                        float(row_dict.get('pv_modul_leistung') or 0),
                        float(row_dict.get('kapazitaet_speicher_kwh') or 0),
                        float(row_dict.get('wr_leistung_kw') or 0),
                        int(float(row_dict.get('ladezyklen_speicher') or 0)),
                        int(float(row_dict.get('garantie_zeit') or 0)),
                        float(row_dict.get('mass_laenge') or 0),
                        float(row_dict.get('mass_breite') or 0),
                        float(row_dict.get('mass_gewicht_kg') or 0),
                        float(row_dict.get('wirkungsgrad_prozent') or 0),
                        (row_dict.get('hersteller_land') or '').strip(),
                        (row_dict.get('beschreibung_info') or '').strip(),
                        (row_dict.get('eigenschaft_info') or '').strip(),
                        (row_dict.get('spezial_merkmal') or '').strip(),
                        float(row_dict.get('rating_null_zehn') or 0),
                        (row_dict.get('image_base64') or '').strip(),
                        datetime.now().isoformat()
                    ))
                    synced += 1
                except Exception:
                    skipped += 1

            conn.commit()
            return synced, skipped
        except Exception:
            return 0, 0
        finally:
            conn.close()

    def get_categories_from_db(self) -> list:
        """Gibt Kategorien aus der DB + hardcoded zurück (dedupliziert, sortiert)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT kategorie FROM products_complete 
                WHERE kategorie IS NOT NULL AND kategorie != '' 
                ORDER BY kategorie
            """)
            db_cats = [row[0] for row in cursor.fetchall()]
            # Merge: hardcoded zuerst, dann DB-Kategorien die noch nicht drin sind
            seen = set(self.categories)
            merged = list(self.categories)
            for cat in db_cats:
                if cat not in seen:
                    merged.append(cat)
                    seen.add(cat)
            return merged
        except Exception:
            return list(self.categories)
        finally:
            conn.close()

    def export_to_excel(self, category: Optional[str] = None) -> pd.DataFrame:
        """Exportiert Produkte zu Excel (mit optionalem Kategorie-Filter)"""
        conn = self.get_connection()
        try:
            if category:
                query = "SELECT * FROM products_complete WHERE kategorie = ? ORDER BY hersteller, produkt_modell"
                df = pd.read_sql_query(query, conn, params=[category])
            else:
                query = "SELECT * FROM products_complete ORDER BY kategorie, hersteller, produkt_modell"
                df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            st.error(f"Export-Fehler: {e}")
            return pd.DataFrame()
        finally:
            conn.close()


def render_product_admin_ui_optimized():
    """Optimierte Streamlit UI für Produktdatenbank mit Pagination"""
    st.title(" Produktdatenbank Administration (Optimiert)")
    
    # Session State initialisieren (EIGENER KEY um Konflikt mit Navigation zu vermeiden!)
    if 'product_db_current_page' not in st.session_state:
        st.session_state.product_db_current_page = 1
    else:
        # Sicherstellen dass es ein Integer ist
        try:
            st.session_state.product_db_current_page = int(st.session_state.product_db_current_page)
        except (ValueError, TypeError):
            st.session_state.product_db_current_page = 1
        
    if 'selected_category_filter' not in st.session_state:
        st.session_state.selected_category_filter = None
    if 'selected_manufacturer_filter' not in st.session_state:
        st.session_state.selected_manufacturer_filter = None
    
    admin = ProductDatabaseAdminOptimized()
    admin.create_products_table()  # Tabelle sicherstellen
    
    # Tabs für verschiedene Aktionen
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [" Dashboard", " Produkte durchsuchen", " Hinzufügen", " Import/Export", " Tools"]
    )
    
    # ============ TAB 1: DASHBOARD ============
    with tab1:
        st.subheader("Datenbank-Übersicht")
        
        stats = admin.get_category_statistics()
        
        if stats:
            # Gesamt-Metriken
            total_products = sum(s['count'] for s in stats.values())
            total_manufacturers = sum(s['manufacturers'] for s in stats.values())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(" Gesamt Produkte", f"{total_products:,}")
            with col2:
                st.metric(" Kategorien", len(stats))
            with col3:
                st.metric(" Hersteller", total_manufacturers)
            
            st.divider()
            
            # Kategorie-Übersicht
            st.subheader("Produkte pro Kategorie")
            
            # Tabelle mit Kategorie-Statistiken
            category_data = []
            for category, data in sorted(stats.items()):
                category_data.append({
                    'Kategorie': category,
                    'Anzahl Produkte': data['count'],
                    'Anzahl Hersteller': data['manufacturers']
                })
            
            df_stats = pd.DataFrame(category_data)
            st.dataframe(df_stats, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ Noch keine Produkte in der Datenbank. Importieren Sie Daten oder fügen Sie manuell Produkte hinzu.")
    
    # ============ TAB 2: PRODUKTE DURCHSUCHEN ============
    with tab2:
        st.subheader("Produkte durchsuchen & bearbeiten")
        
        # Filter-Bereich
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            category_filter = st.selectbox(
                " Kategorie filtern",
                ["Alle Kategorien"] + admin.get_categories_from_db(),
                key="category_filter_select"
            )
            if category_filter != "Alle Kategorien":
                st.session_state.selected_category_filter = category_filter
            else:
                st.session_state.selected_category_filter = None
        
        with col2:
            if st.session_state.selected_category_filter:
                manufacturers = admin.get_manufacturers_by_category(st.session_state.selected_category_filter)
                manufacturer_filter = st.selectbox(
                    " Hersteller filtern",
                    ["Alle Hersteller"] + manufacturers,
                    key="manufacturer_filter_select"
                )
                if manufacturer_filter != "Alle Hersteller":
                    st.session_state.selected_manufacturer_filter = manufacturer_filter
                else:
                    st.session_state.selected_manufacturer_filter = None
            else:
                st.info("Wählen Sie zuerst eine Kategorie")
                st.session_state.selected_manufacturer_filter = None
        
        with col3:
            search_term = st.text_input(" Suche (Modell, Hersteller, Beschreibung)", key="search_input")
        
        # Anzahl berechnen
        total_count = admin.get_product_count(
            category=st.session_state.selected_category_filter,
            manufacturer=st.session_state.selected_manufacturer_filter
        )
        
        # Pagination
        if total_count > 0:
            total_pages = (total_count + admin.items_per_page - 1) // admin.items_per_page
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.write(f" **{total_count} Produkte gefunden** (Seite {st.session_state.product_db_current_page} von {total_pages})")
            
            # Produkte laden
            df = admin.get_products_paginated(
                page=st.session_state.product_db_current_page,
                category=st.session_state.selected_category_filter,
                manufacturer=st.session_state.selected_manufacturer_filter,
                search_term=search_term if search_term else None
            )
            
            if not df.empty:
                # Kompakte Anzeige
                display_columns = [
                    'id', 'kategorie', 'hersteller', 'produkt_modell',
                    'pv_modul_leistung', 'wr_leistung_kw', 'kapazitaet_speicher_kwh',
                    'preis_stück', 'rating_null_zehn'
                ]
                available_columns = [col for col in display_columns if col in df.columns]
                
                st.dataframe(
                    df[available_columns],
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
                # Pagination-Buttons
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                
                with col1:
                    if st.button("⏮ Erste", disabled=(st.session_state.product_db_current_page == 1)):
                        st.session_state.product_db_current_page = 1
                        st.rerun()
                
                with col2:
                    if st.button(" Zurück", disabled=(st.session_state.product_db_current_page == 1)):
                        st.session_state.product_db_current_page -= 1
                        st.rerun()
                
                with col3:
                    # Seitensprung
                    jump_page = st.number_input(
                        "Gehe zu Seite:",
                        min_value=1,
                        max_value=total_pages,
                        value=int(st.session_state.product_db_current_page),
                        step=1,
                        key="page_jump"
                    )
                    if int(jump_page) != int(st.session_state.product_db_current_page):
                        st.session_state.product_db_current_page = int(jump_page)
                        st.rerun()
                
                with col4:
                    if st.button(" Weiter", disabled=(st.session_state.product_db_current_page >= total_pages)):
                        st.session_state.product_db_current_page += 1
                        st.rerun()
                
                with col5:
                    if st.button("⏭ Letzte", disabled=(st.session_state.product_db_current_page >= total_pages)):
                        st.session_state.product_db_current_page = total_pages
                        st.rerun()
            else:
                st.warning("Keine Produkte auf dieser Seite.")
        else:
            st.info("ℹ Keine Produkte gefunden. Passen Sie die Filter an.")
    
    # ============ TAB 3: HINZUFÜGEN ============
    with tab3:
        st.subheader("Neues Produkt hinzufügen")
        
        with st.form("add_product_form_optimized"):
            col1, col2 = st.columns(2)
            
            with col1:
                kategorie = st.selectbox("Kategorie*", admin.categories)
                hersteller = st.text_input("Hersteller*")
                produkt_modell = st.text_input("Produktmodell*")
                preis_stück = st.number_input("Preis pro Stück (€)", min_value=0.0, step=0.01)
                
                if kategorie in ["PV Modul"]:
                    pv_modul_leistung = st.number_input("PV Modul Leistung (W)", min_value=0.0, step=1.0)
                else:
                    pv_modul_leistung = 0.0
                
                if kategorie in ["Wechselrichter"]:
                    wr_leistung_kw = st.number_input("WR Leistung (kW)", min_value=0.0, step=0.1)
                else:
                    wr_leistung_kw = 0.0
                
                if kategorie in ["Batteriespeicher"]:
                    kapazitaet_speicher_kwh = st.number_input("Speicher Kapazität (kWh)", min_value=0.0, step=0.1)
                    ladezyklen_speicher = st.number_input("Ladezyklen", min_value=0, step=100)
                else:
                    kapazitaet_speicher_kwh = 0.0
                    ladezyklen_speicher = 0
            
            with col2:
                garantie_zeit = st.number_input("Garantie (Jahre)", min_value=0, step=1)
                mass_laenge = st.number_input("Länge (m)", min_value=0.0, step=0.01)
                mass_breite = st.number_input("Breite (m)", min_value=0.0, step=0.01)
                mass_gewicht_kg = st.number_input("Gewicht (kg)", min_value=0.0, step=0.1)
                wirkungsgrad_prozent = st.number_input("Wirkungsgrad (%)", min_value=0.0, max_value=100.0, step=0.1)
                hersteller_land = st.text_input("Herstellerland")
                rating_null_zehn = st.slider("Rating (0-10)", 0, 10, 5)
            
            beschreibung_info = st.text_area("Beschreibung")
            eigenschaft_info = st.text_area("Eigenschaften")
            spezial_merkmal = st.text_area("Spezielle Merkmale")
            
            uploaded_image = st.file_uploader("Produktbild", type=['png', 'jpg', 'jpeg'])
            image_base64 = ""
            if uploaded_image:
                image_base64 = base64.b64encode(uploaded_image.read()).decode()
            
            submitted = st.form_submit_button(" Produkt hinzufügen", use_container_width=True)
            
            if submitted:
                if not all([kategorie, hersteller, produkt_modell]):
                    st.error(" Kategorie, Hersteller und Produktmodell sind Pflichtfelder!")
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
                        st.success(" Produkt erfolgreich hinzugefügt!")
                        st.rerun()
    
    # ============ TAB 4: IMPORT/EXPORT ============
    with tab4:
        st.subheader("Import/Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("** Excel Import**")
            st.info("Importieren Sie Produkte aus einer Excel-Datei. Große Dateien werden automatisch in Batches verarbeitet.")
            
            uploaded_file = st.file_uploader("Excel Datei (.xlsx)", type=['xlsx'], key="import_file")
            
            if uploaded_file and st.button(" Importieren starten"):
                temp_path = f"temp_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                
                # Progress-Bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"Importiere... {current}/{total} Produkte")
                
                success, message = admin.import_from_excel(temp_path, progress_callback=update_progress)
                
                if success:
                    st.success(f" {message}")
                else:
                    st.error(f" {message}")
                
                # Cleanup
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        with col2:
            st.write("** Excel Export**")
            st.info("Exportieren Sie Produkte nach Excel. Sie können nach Kategorie filtern.")
            
            export_category = st.selectbox(
                "Kategorie für Export",
                ["Alle Kategorien"] + admin.categories,
                key="export_category"
            )
            
            if st.button(" Export starten"):
                category_filter = None if export_category == "Alle Kategorien" else export_category
                df = admin.export_to_excel(category=category_filter)
                
                if not df.empty:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Produkte')
                    buffer.seek(0)
                    
                    filename = f"products_export_{export_category.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    
                    st.download_button(
                        label=" Download Excel",
                        data=buffer,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    st.success(f" {len(df)} Produkte exportiert!")
                else:
                    st.warning(" Keine Produkte zum Exportieren gefunden.")
    
    # ============ TAB 5: TOOLS ============
    with tab5:
        st.subheader("Datenbank Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("** Datenbank-Wartung**")
            
            if st.button(" Tabelle & Indizes initialisieren"):
                admin.create_products_table()
                st.success(" Tabelle und Performance-Indizes erstellt/aktualisiert!")

            st.write("---")
            st.write("** Synchronisation zur Haupt-Tabelle**")
            st.info(
                "Die App (Angebote, Kalkulation, CRM usw.) nutzt die interne `products`-Tabelle. "
                "Dieser Button überträgt alle Produkte aus der Admin-Tabelle dorthin."
            )
            if st.button(" Jetzt zu Haupt-Tabelle synchronisieren", type="primary"):
                with st.spinner("Synchronisiere Produkte..."):
                    synced, skipped = admin.sync_to_products_table()
                if synced > 0:
                    st.success(f" {synced} Produkte erfolgreich in die Haupt-Tabelle synchronisiert!")
                    if skipped > 0:
                        st.warning(f"⚠ {skipped} Produkte übersprungen (fehlende Kategorie oder Modellname).")
                else:
                    st.warning(
                        "⚠ Keine Produkte synchronisiert. "
                        "Prüfen Sie, ob Kategorie und Produktmodell in der Admin-Tabelle vorhanden sind."
                    )
            
            st.write("---")
            if st.button(" Session State zurücksetzen"):
                st.session_state.product_db_current_page = 1
                st.session_state.selected_category_filter = None
                st.session_state.selected_manufacturer_filter = None
                st.success(" Session zurückgesetzt!")
                st.rerun()
        
        with col2:
            st.write("** Performance-Statistiken**")
            
            total_products = admin.get_product_count()
            st.metric("Gesamt Produkte in DB", f"{total_products:,}")
            st.metric("Produkte pro Seite", admin.items_per_page)
            
            if total_products > 0:
                estimated_pages = (total_products + admin.items_per_page - 1) // admin.items_per_page
                st.metric("Geschätzte Seiten", estimated_pages)


if __name__ == "__main__":
    render_product_admin_ui_optimized()
