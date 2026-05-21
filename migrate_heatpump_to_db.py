"""
Wärmepumpen-Datenbank Migration Script
Migriert die riesige heatpump_products_database.py (25.661 Zeilen!) in SQLite
Ermöglicht Lazy Loading und verhindert Memory-Probleme
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


class HeatpumpDatabaseMigrator:
    """Migriert Wärmepumpen-Daten von Python-Dict zu SQLite"""
    
    def __init__(self, db_path: str = "data/app_data.db"):
        self.db_path = db_path
    
    def create_heatpump_tables(self):
        """Erstellt optimierte Tabellen für Wärmepumpen mit Indizes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Haupt-Tabelle für Wärmepumpen
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS heatpump_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer TEXT NOT NULL,
                heatpump_type TEXT NOT NULL,
                model TEXT NOT NULL,
                scop REAL DEFAULT 0.0,
                max_flow_temp INTEGER DEFAULT 0,
                price_range TEXT DEFAULT '',
                refrigerant TEXT DEFAULT '',
                rating REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabelle für Heizleistungen (mehrere Werte pro Modell möglich)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS heatpump_heating_powers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                heatpump_id INTEGER NOT NULL,
                heating_power_kw REAL NOT NULL,
                FOREIGN KEY (heatpump_id) REFERENCES heatpump_products(id) ON DELETE CASCADE
            )
        """)
        
        # Tabelle für Features (mehrere Features pro Modell)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS heatpump_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                heatpump_id INTEGER NOT NULL,
                feature TEXT NOT NULL,
                FOREIGN KEY (heatpump_id) REFERENCES heatpump_products(id) ON DELETE CASCADE
            )
        """)
        
        # Tabelle für Awards (mehrere Awards pro Modell)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS heatpump_awards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                heatpump_id INTEGER NOT NULL,
                award TEXT NOT NULL,
                FOREIGN KEY (heatpump_id) REFERENCES heatpump_products(id) ON DELETE CASCADE
            )
        """)
        
        # Performance-Indizes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hp_manufacturer ON heatpump_products(manufacturer)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hp_type ON heatpump_products(heatpump_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hp_model ON heatpump_products(model)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hp_manufacturer_type ON heatpump_products(manufacturer, heatpump_type)")
        
        conn.commit()
        conn.close()
        print(" Wärmepumpen-Tabellen erstellt mit Performance-Indizes")
    
    def migrate_from_python_dict(self, heatpump_data: dict, clear_existing: bool = False):
        """
        Migriert Daten aus Python-Dictionary zu SQLite
        
        Args:
            heatpump_data: Dictionary im Format {"Hersteller": {"Typ": [Modelle]}}
            clear_existing: Wenn True, werden existierende Daten gelöscht
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if clear_existing:
            cursor.execute("DELETE FROM heatpump_products")
            cursor.execute("DELETE FROM heatpump_heating_powers")
            cursor.execute("DELETE FROM heatpump_features")
            cursor.execute("DELETE FROM heatpump_awards")
            print(" Existierende Wärmepumpen-Daten gelöscht")
        
        total_models = 0
        
        try:
            for manufacturer, types in heatpump_data.items():
                for heatpump_type, models in types.items():
                    for model_data in models:
                        # Haupt-Eintrag einfügen
                        cursor.execute("""
                            INSERT INTO heatpump_products (
                                manufacturer, heatpump_type, model, scop, 
                                max_flow_temp, price_range, refrigerant, rating
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            manufacturer,
                            heatpump_type,
                            model_data.get('model', ''),
                            model_data.get('scop', 0.0),
                            model_data.get('max_flow_temp', 0),
                            model_data.get('price_range', ''),
                            model_data.get('refrigerant', ''),
                            model_data.get('rating', 0.0)
                        ))
                        
                        heatpump_id = cursor.lastrowid
                        
                        # Heizleistungen einfügen
                        heating_powers = model_data.get('heating_power_kw', [])
                        if isinstance(heating_powers, (int, float)):
                            heating_powers = [heating_powers]
                        
                        for power in heating_powers:
                            cursor.execute("""
                                INSERT INTO heatpump_heating_powers (heatpump_id, heating_power_kw)
                                VALUES (?, ?)
                            """, (heatpump_id, power))
                        
                        # Features einfügen
                        features = model_data.get('features', [])
                        for feature in features:
                            cursor.execute("""
                                INSERT INTO heatpump_features (heatpump_id, feature)
                                VALUES (?, ?)
                            """, (heatpump_id, feature))
                        
                        # Awards einfügen
                        awards = model_data.get('awards', [])
                        for award in awards:
                            cursor.execute("""
                                INSERT INTO heatpump_awards (heatpump_id, award)
                                VALUES (?, ?)
                            """, (heatpump_id, award))
                        
                        total_models += 1
                        
                        # Commit alle 100 Modelle
                        if total_models % 100 == 0:
                            conn.commit()
                            print(f" {total_models} Modelle migriert...")
            
            conn.commit()
            print(f" Migration abgeschlossen: {total_models} Wärmepumpen-Modelle importiert")
            
        except Exception as e:
            conn.rollback()
            print(f" Fehler bei Migration: {e}")
            raise
        finally:
            conn.close()
    
    def get_manufacturers(self) -> list[str]:
        """Alle Hersteller abrufen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT manufacturer FROM heatpump_products ORDER BY manufacturer")
        manufacturers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return manufacturers
    
    def get_types_by_manufacturer(self, manufacturer: str) -> list[str]:
        """Typen nach Hersteller"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT heatpump_type FROM heatpump_products WHERE manufacturer = ? ORDER BY heatpump_type",
            [manufacturer]
        )
        types = [row[0] for row in cursor.fetchall()]
        conn.close()
        return types
    
    def get_models_paginated(
        self,
        page: int = 1,
        items_per_page: int = 50,
        manufacturer: str = None,
        heatpump_type: str = None
    ) -> list[dict]:
        """
        Modelle mit Pagination abrufen (MEMORY-SAFE)
        
        Returns:
            Liste von Dictionaries mit allen Details
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        offset = (page - 1) * items_per_page
        
        # Query bauen
        query = "SELECT * FROM heatpump_products WHERE 1=1"
        params = []
        
        if manufacturer:
            query += " AND manufacturer = ?"
            params.append(manufacturer)
        
        if heatpump_type:
            query += " AND heatpump_type = ?"
            params.append(heatpump_type)
        
        query += f" ORDER BY manufacturer, heatpump_type, model LIMIT {items_per_page} OFFSET {offset}"
        
        cursor.execute(query, params)
        models = []
        
        for row in cursor.fetchall():
            heatpump_id = row['id']
            
            # Heizleistungen laden
            cursor.execute(
                "SELECT heating_power_kw FROM heatpump_heating_powers WHERE heatpump_id = ?",
                [heatpump_id]
            )
            heating_powers = [r[0] for r in cursor.fetchall()]
            
            # Features laden
            cursor.execute(
                "SELECT feature FROM heatpump_features WHERE heatpump_id = ?",
                [heatpump_id]
            )
            features = [r[0] for r in cursor.fetchall()]
            
            # Awards laden
            cursor.execute(
                "SELECT award FROM heatpump_awards WHERE heatpump_id = ?",
                [heatpump_id]
            )
            awards = [r[0] for r in cursor.fetchall()]
            
            models.append({
                'id': row['id'],
                'manufacturer': row['manufacturer'],
                'heatpump_type': row['heatpump_type'],
                'model': row['model'],
                'heating_power_kw': heating_powers,
                'scop': row['scop'],
                'max_flow_temp': row['max_flow_temp'],
                'price_range': row['price_range'],
                'refrigerant': row['refrigerant'],
                'rating': row['rating'],
                'features': features,
                'awards': awards
            })
        
        conn.close()
        return models
    
    def get_model_count(self, manufacturer: str = None, heatpump_type: str = None) -> int:
        """Anzahl der Modelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM heatpump_products WHERE 1=1"
        params = []
        
        if manufacturer:
            query += " AND manufacturer = ?"
            params.append(manufacturer)
        
        if heatpump_type:
            query += " AND heatpump_type = ?"
            params.append(heatpump_type)
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def find_suitable_model(
        self,
        heating_requirement_kw: float,
        heatpump_type: str = None,
        manufacturer: str = None,
        min_scop: float = 0.0
    ) -> list[dict]:
        """
        Findet passende Modelle basierend auf Anforderungen
        
        Args:
            heating_requirement_kw: Benötigte Heizleistung
            heatpump_type: Optional: Typ der Wärmepumpe
            manufacturer: Optional: Hersteller
            min_scop: Minimaler SCOP-Wert
        
        Returns:
            Liste passender Modelle, sortiert nach Rating
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Modelle mit passender Heizleistung finden
        query = """
            SELECT DISTINCT hp.* 
            FROM heatpump_products hp
            JOIN heatpump_heating_powers pow ON hp.id = pow.heatpump_id
            WHERE pow.heating_power_kw >= ?
            AND hp.scop >= ?
        """
        params = [heating_requirement_kw, min_scop]
        
        if heatpump_type:
            query += " AND hp.heatpump_type = ?"
            params.append(heatpump_type)
        
        if manufacturer:
            query += " AND hp.manufacturer = ?"
            params.append(manufacturer)
        
        query += " ORDER BY hp.rating DESC, hp.scop DESC LIMIT 20"
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            heatpump_id = row['id']
            
            # Heizleistungen
            cursor.execute(
                "SELECT heating_power_kw FROM heatpump_heating_powers WHERE heatpump_id = ?",
                [heatpump_id]
            )
            heating_powers = [r[0] for r in cursor.fetchall()]
            
            # Features
            cursor.execute(
                "SELECT feature FROM heatpump_features WHERE heatpump_id = ?",
                [heatpump_id]
            )
            features = [r[0] for r in cursor.fetchall()]
            
            # Awards
            cursor.execute(
                "SELECT award FROM heatpump_awards WHERE heatpump_id = ?",
                [heatpump_id]
            )
            awards = [r[0] for r in cursor.fetchall()]
            
            results.append({
                'id': row['id'],
                'manufacturer': row['manufacturer'],
                'heatpump_type': row['heatpump_type'],
                'model': row['model'],
                'heating_power_kw': heating_powers,
                'scop': row['scop'],
                'max_flow_temp': row['max_flow_temp'],
                'price_range': row['price_range'],
                'refrigerant': row['refrigerant'],
                'rating': row['rating'],
                'features': features,
                'awards': awards
            })
        
        conn.close()
        return results
    
    def export_statistics(self) -> dict:
        """Exportiert Statistiken über die Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Gesamt
        cursor.execute("SELECT COUNT(*) FROM heatpump_products")
        stats['total_models'] = cursor.fetchone()[0]
        
        # Nach Hersteller
        cursor.execute("""
            SELECT manufacturer, COUNT(*) as count
            FROM heatpump_products
            GROUP BY manufacturer
            ORDER BY count DESC
        """)
        stats['by_manufacturer'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Nach Typ
        cursor.execute("""
            SELECT heatpump_type, COUNT(*) as count
            FROM heatpump_products
            GROUP BY heatpump_type
            ORDER BY count DESC
        """)
        stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Durchschnittlicher SCOP
        cursor.execute("SELECT AVG(scop) FROM heatpump_products WHERE scop > 0")
        stats['avg_scop'] = round(cursor.fetchone()[0], 2)
        
        # Durchschnittliches Rating
        cursor.execute("SELECT AVG(rating) FROM heatpump_products WHERE rating > 0")
        stats['avg_rating'] = round(cursor.fetchone()[0], 2)
        
        conn.close()
        return stats


def migrate_heatpump_products_to_db():
    """
    Haupt-Migrations-Funktion
    Lädt heatpump_products_database.py und migriert in SQLite
    """
    print(" Starte Wärmepumpen-Migration...")
    
    try:
        # Import der riesigen Python-Datei (nur einmal!)
        from heatpump_products_database import HEATPUMP_PRODUCTS
        
        migrator = HeatpumpDatabaseMigrator()
        
        # Tabellen erstellen
        migrator.create_heatpump_tables()
        
        # Migration durchführen
        migrator.migrate_from_python_dict(HEATPUMP_PRODUCTS, clear_existing=True)
        
        # Statistiken anzeigen
        stats = migrator.export_statistics()
        print("\n Migrations-Statistiken:")
        print(f"   Gesamt Modelle: {stats['total_models']}")
        print(f"   Durchschn. SCOP: {stats['avg_scop']}")
        print(f"   Durchschn. Rating: {stats['avg_rating']}")
        print("\n   Nach Hersteller:")
        for manufacturer, count in stats['by_manufacturer'].items():
            print(f"      {manufacturer}: {count} Modelle")
        
        print("\n Migration erfolgreich abgeschlossen!")
        print(" Die Datei 'heatpump_products_database.py' kann nun archiviert werden.")
        
        return True
        
    except ImportError:
        print(" Fehler: heatpump_products_database.py nicht gefunden!")
        print("   Stelle sicher, dass die Datei im gleichen Verzeichnis liegt.")
        return False
    except Exception as e:
        print(f" Fehler bei Migration: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    migrate_heatpump_products_to_db()
